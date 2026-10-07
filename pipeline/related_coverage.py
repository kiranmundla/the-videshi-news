#!/usr/bin/env python3
"""Related coverage for Videshi articles.

Finds 2-3 related published articles and renders a "Related coverage" block
appended to the article body at insert time. Keeps readers on-site.

Ranking: same developing storyline > shared tags > same category, recency
tiebreak. All HTTP via curl (urllib/requests fail through this host's proxy).
"""

import html
import json
import os
import re
import subprocess
import urllib.parse
from datetime import datetime, timedelta, timezone


def _sb_env():
    env = {}
    p = os.path.expanduser("~/workspace/.env.supabase")
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"').strip("'")
    return env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_ROLE_KEY")


def _get(path, params=()):
    SB, K = _sb_env()
    flat = []
    for k, v in params:
        flat += ["--data-urlencode", f"{k}={v}"]
    cmd = (["curl", "-sS", "--fail", "-G", f"{SB}/rest/v1/{path}"] + flat
           + ["-H", f"apikey: {K}", "-H", f"Authorization: Bearer {K}"])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout)


def _patch(path, params, data):
    SB, K = _sb_env()
    qs = urllib.parse.urlencode([(k, v) for k, v in params])
    cmd = (["curl", "-sS", "--fail", "-X", "PATCH",
            f"{SB}/rest/v1/{path}?{qs}",
            "-H", f"apikey: {K}", "-H", f"Authorization: Bearer {K}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=minimal",
            "-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    return True


def find_related(article_id, category, tags, limit=3, days=14):
    """Return up to `limit` related articles as dicts (id, headline, slug,
    category, published_at), ranked by storyline > tags > category > recency."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    tags = [t for t in (tags or []) if t]
    tag_set = set(t.lower() for t in tags)

    # 1. my storylines
    my_storylines = set()
    try:
        for row in _get("storyline_articles",
                        [("select", "storyline_id"),
                         ("article_id", f"eq.{article_id}")]):
            my_storylines.add(row["storyline_id"])
    except Exception:
        pass

    storyline_article_ids = set()
    if my_storylines:
        try:
            ids = ",".join(sorted(my_storylines))
            for row in _get("storyline_articles",
                            [("select", "article_id"),
                             ("storyline_id", f"in.({ids})")]):
                if row["article_id"] != article_id:
                    storyline_article_ids.add(row["article_id"])
        except Exception:
            pass

    # 2. candidates sharing tags (tag-driven, not recency-window driven —
    #    at 50+ articles/day a bare "recent N" window misses obvious matches)
    candidates = {}
    for t in list(tag_set)[:6]:
        try:
            rows = _get("p2_articles",
                        [("select", "id,headline,slug,category,tags,published_at"),
                         ("status", "eq.published"),
                         ("tags", "cs.{%s}" % t),
                         ("published_at", f"gte.{since}"),
                         ("order", "published_at.desc"),
                         ("limit", "10")])
            for r in rows:
                if r["id"] != article_id:
                    candidates[r["id"]] = r
        except Exception:
            pass
    # 3. same-category recent as fallback breadth
    try:
        rows = _get("p2_articles",
                    [("select", "id,headline,slug,category,tags,published_at"),
                     ("status", "eq.published"),
                     ("category", f"eq.{category}"),
                     ("published_at", f"gte.{since}"),
                     ("order", "published_at.desc"),
                     ("limit", "30")])
        for r in rows:
            if r["id"] != article_id:
                candidates.setdefault(r["id"], r)
    except Exception:
        pass
    candidates = list(candidates.values())
    if not candidates:
        return []

    scored = []
    for c in candidates:
        score = 0
        if c["id"] in storyline_article_ids:
            score += 100
        ctags = set((t or "").lower() for t in (c.get("tags") or []))
        score += 10 * len(tag_set & ctags)
        if (c.get("category") or "") == category:
            score += 5
        if score > 0:
            scored.append((score, c.get("published_at") or "", c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [c for _, _, c in scored[:limit]]


def render_related_block(related):
    """HTML block appended to the article body. Empty string if none."""
    if not related:
        return ""
    items = []
    for r in related:
        slug = r.get("slug") or ""
        title = r.get("headline") or ""
        cat = (r.get("category") or "").replace("-", " ").title()
        pub = (r.get("published_at") or "")[:10]
        meta = " · ".join(p for p in (cat, pub) if p)
        items.append(
            f'<a class="related-item" href="/articles/{html.escape(slug)}">'
            f'<span class="related-item-title">{html.escape(title)}</span>'
            + (f'<span class="related-item-meta">{html.escape(meta)}</span>'
               if meta else "")
            + "</a>")
    return ('<div class="related-coverage">'
            '<div class="related-coverage-title">Related coverage</div>'
            + "".join(items) + "</div>")


def append_related_block(article_id):
    """Find related articles and append the block to the article body.
    Returns number of related articles linked (0 if none / already present)."""
    rows = _get("p2_articles",
                [("select", "id,body,category,tags"),
                 ("id", f"eq.{article_id}"), ("limit", "1")])
    if not rows:
        return 0
    art = rows[0]
    body = art.get("body") or ""
    if "related-coverage" in body:
        return 0
    related = find_related(article_id, art.get("category"), art.get("tags"))
    block = render_related_block(related)
    if not block:
        return 0
    _patch("p2_articles", [("id", f"eq.{article_id}")],
           {"body": body + "\n" + block})
    return len(related)


if __name__ == "__main__":
    import sys
    aid = sys.argv[1]
    n = append_related_block(aid)
    print(f"linked {n} related articles")
