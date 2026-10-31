#!/usr/bin/env python3
"""Related coverage for Videshi articles.

Finds up to 3 related published articles and renders a "Related
coverage" block appended to the article body at insert time. Keeps
readers on-site. This module is the ONLY producer of baked related
blocks (called from v3-insert-article.py after insert; the writer
LLM's own inline /articles/ links are separate editorial content).

RELEVANCE ENFORCEMENT (2026-10-31, root-cause program — BAPS
acceptance hole 6): the old ranking treated shared tags and same
category as sufficient (score > 0), so generic-tag collisions filled
blocks with unrelated stories — the Dallas BAPS article's block
carried a Singapore nightclub crime story and a missing-person story
next to one relevant Diwali link, via the shared tag "Indian
diaspora" + same category. Measured baseline over the last 7 days of
published articles: 63.8% of 1,106 baked related items fail the
relevance function below; 78% of blocked articles carry at least one
failing item.

Selection is now a hard FILTER, then the old ranking among the
survivors (storyline > shared tags > category > recency). A candidate
qualifies ONLY via `qualifies()`:

  (c) same event cluster — shared storyline (storyline_articles) or
      the same non-null topic_id;
  (a) shared entity — headline subjects / co-subjects from
      article_picture_pass.extract_article_entities (sources
      headline + image_entities only; body mentions are not
      subjects) or tags, mapped through entity_registry: a shared
      registry entry (QID / canonical name), or a shared strong
      extracted name (multi-token or sourceable, not a headline-
      formula phrase like "Earnings Beat Estimates"), or a shared
      subject TAG that both headlines themselves name verbatim —
      the H-1B case: a hyphenated programme name the extractor,
      the tokenizer and the registry all miss, carried by the
      writers' own tags (rarity-gated like (b); place tags are
      excluded — a shared city tag is geography, not a subject).
      A PLACE-type registry entry never qualifies alone — geography
      is not a subject — it needs a corroborating shared strong
      headline token outside the place's own name;
  (b) strong topical overlap — shared headline content tokens
      (stopword/formula-filtered) whose corpus frequency is low:
      >= 2 shared strong tokens, or exactly 1 with very low
      frequency that is not a place name. Token frequency is
      measured over the last 14 days of published headlines
      (document frequency), calibrated 2026-10-31: on random
      same-category pairs the token routes qualify ~1%.

Same category alone NEVER qualifies; a shared tag alone NEVER
qualifies either (tags count only as route (a) describes). When
fewer than `limit` candidates qualify, fewer are linked — never
backfilled.

All HTTP via curl (urllib/requests fail through this host's proxy).
"""

import html
import json
import os
import re
import subprocess
import time
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


# ------------------------------------------------------- relevance
#
# Calibrated 2026-10-31 on 1,106 baked related pairs + 2,955 random
# same-category control pairs from the Oct 17-31 corpus (see header).
# Thresholds: a headline token is STRONG when its document frequency
# over recent headlines is <= max(4, 3% of corpus); a single shared
# strong token carries a pair only when it is RARE (df <= max(2,
# 0.6% of corpus)) and not a place name.

_TOKEN_STOP = set("""
the a an and or of for in on at to from by with as is are was were be
been it its this that these those after over amid among between into
out up down off per via than then when while who whom whose what which
how why not no yes new news india indian indians diaspora america
american americas us usa uk world global today latest live update
updates report reports said says say gets get got set sets first one
two three day days week weeks month months year years time times
people man woman men women dies dead death found missing police court
case cases held top big back home play plays win wins won loss losses
could would should may might must shall will just also more most other
others another about above below under again further once here there
all any both each few many much own same so too very can now chief
minister became become becomes makes made takes took gives goes went
comes came brings leaves left keeps turns turned shows showed earnings
revenue revenues profit profits quarter quarterly estimates shares
stocks jumps jumped surge surges plunge plunges gains losses targets
record records star stars adds raised beats
""".split())

# Headline-formula words: an extracted "entity" composed ONLY of these
# is a headline phrase, not a subject ("Earnings Beat Estimates",
# "Revenue Rises") — it never counts as a shared entity.
_FORMULA_TOKENS = set("""
earnings revenue revenues profit profits rises rose rise jumps jumped
falls fell beats beat estimates estimate targets target shares stocks
quarter quarterly results growth surge surges plunges gains losses
record records announced announces launches launched unveils reveals
wins loses dies dead missing found arrested charged convicted
sentenced says said calls warns warning eyes set sets
""".split())

_DF_CACHE = {"t": 0.0, "df": None, "n": 0}
_PLACE_TOKENS = None
_REG_BY_QID = None


def headline_tokens(headline):
    """Content tokens of a headline: lowercase alpha tokens of length
    >= 4 minus stopwords/formula words, plus hyphenated alphanumeric
    forms (h-1b, l-1, f-1) that the alpha pattern cannot see."""
    low = (headline or "").lower()
    out = set()
    for t in re.findall(r"[a-z][a-z'\-]*", low):
        t = t.strip("'-")
        if len(t) >= 4 and t not in _TOKEN_STOP:
            out.add(t)
    for t in re.findall(r"[a-z]+(?:-[a-z0-9]+)+", low):
        if len(t) >= 4 and t not in _TOKEN_STOP:
            out.add(t)
    return out


def _token_df(days=14):
    """(df, n) — headline-token document frequency over the last
    `days` of published articles. Cached per process for an hour.
    (None, 0) when the fetch fails: callers fall back to a
    length-only strong-token rule with no rare-token route."""
    now = time.time()
    if _DF_CACHE["df"] is not None and now - _DF_CACHE["t"] < 3600:
        return _DF_CACHE["df"], _DF_CACHE["n"]
    df = {}
    n = 0
    try:
        since = (datetime.now(timezone.utc)
                 - timedelta(days=days)).isoformat()
        rows = _get("p2_articles",
                    [("select", "headline"), ("status", "eq.published"),
                     ("published_at", f"gte.{since}"),
                     ("order", "published_at.desc"), ("limit", "1000")])
        for r in rows:
            n += 1
            for t in headline_tokens(r.get("headline")):
                df[t] = df.get(t, 0) + 1
    except Exception:
        return None, 0
    _DF_CACHE.update({"t": now, "df": df, "n": n})
    return df, n


def _strong_tokens(article, df, n):
    toks = headline_tokens(article.get("headline"))
    if df is None:
        # No frequency table: conservative fallback — longer tokens
        # only, and `qualifies` disables the single-token route.
        return {t for t in toks if len(t) >= 5}
    lim = max(4, 0.03 * n)
    return {t for t in toks if df.get(t, 0) <= lim}


def _registry_maps():
    global _PLACE_TOKENS, _REG_BY_QID
    if _REG_BY_QID is None:
        import entity_resolve as er
        reg = er.load_registry()
        _REG_BY_QID = {e["wikidata_qid"]: e for e in reg.get("entities", [])
                       if e.get("wikidata_qid")}
        place_tokens = set()
        for e in reg.get("entities", []):
            if e.get("type") == "place":
                for nm in [e.get("name")] + list(e.get("aliases") or []):
                    if nm:
                        place_tokens |= set(er._norm(nm).split())
        _PLACE_TOKENS = place_tokens
    return _REG_BY_QID, _PLACE_TOKENS


def _entity_keys(article, df=None, df_n=0):
    """(qualifying_keys, place_keys) for one article.

    Evidence pool: extracted entities with source headline or
    image_entities (subjects / co-subjects — body mentions never
    count), plus the article's tags. Registry-backed names/tags yield
    qid:/reg: keys; place-type registry entries go to place_keys.
    Strong extracted names (multi-token or sourceable) also yield
    name: keys, unless every token is a headline-formula word.
    Finally (needs the DF table): a tag the headline itself names
    verbatim yields a tag: key when the tag is not a registry place
    and at least one of its tokens is corpus-uncommon — the H-1B
    route (see module header).
    """
    import entity_resolve as er
    by_qid, _ = _registry_maps()
    qualifying, place = set(), set()

    def add_registry(name):
        for ent in er._candidates(name):
            qid = ent.get("wikidata_qid")
            if qid:
                key = f"qid:{qid}"
                target = place if by_qid.get(qid, {}).get(
                    "type") == "place" else qualifying
                target.add(key)
            else:
                qualifying.add(f"reg:{er._norm(ent.get('name'))}")

    try:
        import article_picture_pass as app
        for e in app.extract_article_entities(article):
            if e.get("source") not in ("headline", "image_entities"):
                continue
            add_registry(e["name"])
            if len(e["name"].split()) > 1 or e.get("sourceable"):
                if not set(er._norm(e["name"]).split()) <= _FORMULA_TOKENS:
                    qualifying.add(f"name:{er._norm(e['name'])}")
    except Exception:
        pass
    for tag in article.get("tags") or []:
        if tag:
            add_registry(tag)
    if df is not None:
        hl_norm = " " + er._norm(article.get("headline")) + " "
        lim = max(4, 0.03 * df_n)
        for tag in article.get("tags") or []:
            if not tag:
                continue
            nt = er._norm(tag)
            if not nt or f" {nt} " not in hl_norm:
                continue
            if any(ent.get("type") == "place"
                   for ent in er._candidates(tag)):
                continue
            toks = headline_tokens(tag)
            if toks and min(df.get(t, 0) for t in toks) <= lim:
                qualifying.add(f"tag:{nt}")
    return qualifying, place


def qualifies(source, candidate, df=None, df_n=0, same_storyline=False):
    """Deterministic relevance verdict for a related-coverage link.
    Returns (bool, route) with route in {"storyline", "topic",
    "entity", "entity+place", "tokens", "tokens-rare", ""}. See the
    module header for the rule. df/df_n inject the token-frequency
    table (tests, offline measurement); df=None disables the
    single-token route."""
    if same_storyline:
        return True, "storyline"
    st = source.get("topic_id")
    if st and st == candidate.get("topic_id"):
        return True, "topic"
    sq, sp = _entity_keys(source, df=df, df_n=df_n)
    cq, cp = _entity_keys(candidate, df=df, df_n=df_n)
    if sq & cq:
        return True, "entity"
    shared = (_strong_tokens(source, df, df_n)
              & _strong_tokens(candidate, df, df_n))
    if sp and cp and (sp & cp):
        _, place_tokens = _registry_maps()
        if any(t not in place_tokens for t in shared):
            return True, "entity+place"
    if len(shared) >= 2:
        return True, "tokens"
    if len(shared) == 1 and df is not None:
        t = next(iter(shared))
        _, place_tokens = _registry_maps()
        if df.get(t, 0) <= max(2, 0.006 * df_n) and t not in place_tokens:
            return True, "tokens-rare"
    return False, ""


# ------------------------------------------------------- selection

_EVAL_POOL = 12  # shortlist size relevance-checked per insert


def find_related(article_id, category, tags, limit=3, days=14,
                 article=None):
    """Return up to `limit` related articles as dicts (id, headline,
    slug, category, published_at) that PASS the relevance filter,
    ranked among themselves by storyline > shared tags > same
    category > recency. Fewer than `limit` — including zero — when
    fewer qualify; never backfilled with unqualified items.
    `article` is the source article's full row when the caller has
    it (headline/image_entities/topic_id/body feed the filter)."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    tags = [t for t in (tags or []) if t]
    tag_set = set(t.lower() for t in tags)
    _FIELDS = "id,headline,slug,category,tags,topic_id,published_at"

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
                        [("select", _FIELDS),
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
    # 3. same-category recent as candidate breadth (candidates only —
    #    category membership alone never qualifies a link any more)
    try:
        rows = _get("p2_articles",
                    [("select", _FIELDS),
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
        scored.append((score, c.get("published_at") or "", c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # 4. relevance filter over the shortlist (storyline members are
    #    always evaluated, even past the shortlist cut)
    shortlist = [c for _, _, c in scored[:_EVAL_POOL]]
    seen_ids = {c["id"] for c in shortlist}
    for _, _, c in scored[_EVAL_POOL:]:
        if c["id"] in storyline_article_ids and c["id"] not in seen_ids:
            shortlist.append(c)
            seen_ids.add(c["id"])
    if not shortlist:
        return []

    # full rows for the filter (body + image_entities feed extraction)
    full = {}
    try:
        ids = ",".join(sorted(seen_ids))
        for r in _get("p2_articles",
                      [("select", _FIELDS + ",image_entities,body"),
                       ("id", f"in.({ids})")]):
            full[r["id"]] = r
    except Exception:
        full = {}
    source = article
    if not source:
        try:
            rows = _get("p2_articles",
                        [("select", _FIELDS + ",image_entities,body"),
                         ("id", f"eq.{article_id}"), ("limit", "1")])
            source = rows[0] if rows else {}
        except Exception:
            source = {}
    df, df_n = _token_df()

    out = []
    for c in shortlist:
        cand = full.get(c["id"], c)
        ok, _route = qualifies(
            source, cand, df=df, df_n=df_n,
            same_storyline=c["id"] in storyline_article_ids)
        if ok:
            out.append(c)
        if len(out) >= limit:
            break
    return out


def render_related_block(related):
    """HTML block appended to the article body. Empty string if none."""
    if not related:
        return ""
    items = []
    for r in related:
        slug = r.get("slug") or ""
        # unescape first: headlines may carry entities (&#x27;) — escaping raw
        # would double-encode to &amp;#x27; which renders literally
        title = html.escape(html.unescape(r.get("headline") or ""))
        cat = (r.get("category") or "").replace("-", " ").title()
        pub = (r.get("published_at") or "")[:10]
        meta = " · ".join(p for p in (cat, pub) if p)
        items.append(
            f'<a class="related-item" href="/articles/{html.escape(slug)}">'
            f'<span class="related-item-title">{title}</span>'
            + (f'<span class="related-item-meta">{html.escape(meta)}</span>'
               if meta else "")
            + "</a>")
    return ('<div class="related-coverage">'
            '<div class="related-coverage-title">Related coverage</div>'
            + "".join(items) + "</div>")


def append_related_block(article_id):
    """Find related articles and append the block to the article body.
    Returns number of related articles linked (0 if none qualify /
    already present)."""
    rows = _get("p2_articles",
                [("select", "id,headline,body,category,tags,topic_id,"
                           "image_entities"),
                 ("id", f"eq.{article_id}"), ("limit", "1")])
    if not rows:
        return 0
    art = rows[0]
    body = art.get("body") or ""
    if "related-coverage" in body:
        return 0
    related = find_related(article_id, art.get("category"), art.get("tags"),
                           article=art)
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
