#!/usr/bin/env python3
"""shadow_run.py — divergence runner for the image rebuild's
shadow path (design.md §3: two weeks of shadow decisions before
any wiring decision).

For every article published in the last N hours (default 4,
--hours), compute what the NEW path would have placed — hero
via verified_sourcer.decide(), inlines via inline_decide() —
and compare it against what the LIVE pipeline actually placed
(the article's image_url + the figures in its body). Append a
divergence summary to pipeline/.state/shadow-report-<date>.md:

  counts — agree / shadow-image-live-none /
           shadow-none-live-image / different-image (hero),
           plus inline-divergence and error counts;
  lines  — one per divergence: slug, live file key, shadow
           decision + route + reason (inlines: both key sets).

READ-ONLY against Supabase (GET only) and side-effect free by
construction:
  - decisions are computed with write_log=False (the shadow
    JSONL ledger belongs to the producers' own shadow calls);
  - the resolver's registry cache-back is DISABLED in this
    process — a measurement run must never mutate
    entity_registry.json (cache-back happens in the resolver's
    own callers, under the names_agree guard);
  - the only write is the .state report (skipped by --dry-run,
    which prints the summary instead).

Comparison is by canonical Commons file key
(entity_resolve.file_key — the same identity the IOB dedup fix
uses). Honest limit: a live image the pipeline re-hosted under
a generated storage name cannot be keyed back to its Commons
file; it reads as different-image, and its raw URL is shown in
the divergence line. Agreement therefore understates, never
overstates, how often the two paths coincide.

Usage: python3 -u shadow_run.py [--hours 4] [--dry-run]
Env: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (read from the
environment; source ~/workspace/.env.supabase first).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import entity_resolve as er
import verified_sourcer as vs

# A measurement run never mutates the registry (see docstring).
er._cache_back = lambda *a, **k: False  # noqa: E731

UA = ("TheVideshiShadowRun/1.0 "
      "(news image verification; contact editor@thevideshi.com)")
SELECT = ("slug,headline,subheadline,body,image_url,"
          "image_entities,image_must_show,published_at")


def state_dir():
    env = os.environ.get("SHADOW_STATE_DIR")
    if env:
        return Path(env)
    return Path(HERE) / ".state"


# ── Supabase (read-only) ─────────────────────────────────────────
def _supabase_get(path_qs):
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    out = subprocess.run(
        ["curl", "-s", "-m", "60", "-A", UA,
         "-H", f"apikey: {key}",
         "-H", f"Authorization: Bearer {key}",
         f"{base}/rest/v1/{path_qs}"],
        capture_output=True, text=True, timeout=70)
    rows = json.loads(out.stdout)
    if not isinstance(rows, list):
        raise RuntimeError(f"Supabase GET failed: {rows}")
    return rows


def fetch_recent_articles(hours, now=None):
    """Published articles from the last `hours` hours, newest
    first. Maps the table's subheadline onto the summary field
    verified_sourcer.article_context reads."""
    now = now or datetime.now(timezone.utc)
    since = (now - timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    qs = ("p2_articles?status=eq.published"
          f"&published_at=gte.{urllib.parse.quote(since)}"
          "&order=published_at.desc"
          f"&select={SELECT}")
    rows = _supabase_get(qs)
    for a in rows:
        a["summary"] = a.get("subheadline") or ""
    return rows


# ── comparison ───────────────────────────────────────────────────
_IMG_SRC = re.compile(r"""<img[^>]+src=["']([^"']+)["']""",
                      re.IGNORECASE)


def live_inline_keys(article):
    """Canonical file keys of the figures the live pipeline
    placed in the body, hero excluded, order preserved."""
    hero_key = er.file_key(article.get("image_url"))
    keys = []
    for src in _IMG_SRC.findall(article.get("body") or ""):
        k = er.file_key(src)
        if k and k != hero_key and k not in keys:
            keys.append(k)
    return keys


def classify_hero(live_has, live_key, shadow):
    """One of agree / shadow-image-live-none /
    shadow-none-live-image / different-image."""
    shadow_has = (shadow.get("decision") == "image"
                  and bool(shadow.get("file_key")))
    if shadow_has and not live_has:
        return "shadow-image-live-none"
    if shadow_has and live_has:
        if live_key and live_key == shadow.get("file_key"):
            return "agree"
        return "different-image"
    if live_has:
        return "shadow-none-live-image"
    return "agree"


def run(hours=4, dry_run=False, fetch=None, decide_fn=None,
        inline_fn=None, now=None, state=None):
    """Execute one shadow run. Returns (report_text, stats).
    fetch/decide_fn/inline_fn are injectable for tests."""
    fetch = fetch or fetch_recent_articles
    if decide_fn is None:
        decide_fn = lambda a: vs.decide(a, write_log=False)  # noqa: E731
    if inline_fn is None:
        inline_fn = (lambda a, hero: vs.inline_decide(  # noqa: E731
            a, hero=hero, write_log=False))
    now = now or datetime.now(timezone.utc)
    articles = fetch(hours)
    counts = Counter()
    lines = []
    inline_differ = 0
    errors = 0
    for a in articles:
        slug = a.get("slug") or "(no slug)"
        try:
            hero = decide_fn(a)
            inl = inline_fn(a, hero)
        except Exception as e:  # one bad article must not kill
            errors += 1             # the run — record and move on
            lines.append(f"- {slug} | ERROR deciding: {e}")
            continue
        live_has = bool(a.get("image_url"))
        live_key = er.file_key(a.get("image_url"))
        cat = classify_hero(live_has, live_key, hero)
        counts[cat] += 1
        if cat != "agree":
            lines.append(
                f"- {slug} | hero {cat} | live: "
                f"{live_key or a.get('image_url') or 'none'} | "
                f"shadow: {hero.get('decision')}/"
                f"{hero.get('route')}/{hero.get('entity')} — "
                f"{hero.get('reason')}")
        shadow_keys = [p["file_key"] for p in inl.get("inlines")
                       or []]
        live_keys = live_inline_keys(a)
        if set(shadow_keys) != set(live_keys):
            inline_differ += 1
            lines.append(
                f"- {slug} | inline differ | live: "
                f"{live_keys} | shadow: {shadow_keys}")
    stats = {"articles": len(articles), "counts": dict(counts),
             "inline_divergences": inline_differ, "errors": errors}
    text = _render(now, hours, stats, lines)
    if not dry_run:
        state = state or state_dir()
        state.mkdir(parents=True, exist_ok=True)
        path = state / f"shadow-report-{now:%Y-%m-%d}.md"
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
        stats["report_path"] = str(path)
    return text, stats


def _render(now, hours, stats, lines):
    c = stats["counts"]
    out = [
        f"## Shadow run {now:%Y-%m-%dT%H:%M:%SZ} — last "
        f"{hours}h, {stats['articles']} articles",
        "",
        "Comparison by canonical Commons file key; live images "
        "re-hosted under generated names cannot be keyed and "
        "read as different-image (agreement understates).",
        "",
        f"- agree: {c.get('agree', 0)}",
        f"- shadow-image-live-none: "
        f"{c.get('shadow-image-live-none', 0)}",
        f"- shadow-none-live-image: "
        f"{c.get('shadow-none-live-image', 0)}",
        f"- different-image: {c.get('different-image', 0)}",
        f"- inline divergences: {stats['inline_divergences']} "
        f"of {stats['articles']} articles",
        f"- errors: {stats['errors']}",
        "",
        "### Divergences",
        "",
    ]
    out.extend(lines or ["(none)"])
    out.append("")
    return "\n".join(out)


def _main(argv):
    ap = argparse.ArgumentParser(
        description="Shadow-path divergence runner (image "
                    "rebuild). Read-only; see module docstring.")
    ap.add_argument("--hours", type=float, default=4,
                    help="look-back window (default 4)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the summary; write nothing")
    args = ap.parse_args(argv)
    text, stats = run(hours=args.hours, dry_run=args.dry_run)
    print(text)
    if stats.get("report_path"):
        print(f"[appended to {stats['report_path']}]",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
