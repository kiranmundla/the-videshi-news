"""Regression tests: Instagram enrichment via the Meta connector.

Covers the 2026-10-24 swap from Apify to instagram-cli:
  - connector posts are normalized only when the returned author exactly
    matches the requested public handle and the post URL yields a shortcode;
  - a 429 from the connector is a hard stop for the rest of the run;
  - prefetch is cache-first and caps live handle refreshes per run;
  - an embed requires topical caption evidence — a person's unrelated
    latest post is never used as a fallback;
  - the cache refresh rotates through the registry instead of reading all
    handles in one run.

Run: python3 test_ig_connector_enrichment.py  (exit 0 = all pass)
"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
fails = 0
total = 0


def check(name, cond, extra=""):
    global fails, total
    total += 1
    if cond:
        print(f"ok   {name}")
    else:
        fails += 1
        print(f"FAIL {name} {extra}")


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


enr = load("enrich_on_publish_ig", "enrich-on-publish.py")
ref = load("refresh_embed_cache_ig", "refresh-embed-cache.py")

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Normalization: exact owner, public, parseable URL ─────────────────────
item = {
    "username": "ICC",
    "url": "https://www.instagram.com/reel/ABC123/",
    "post_caption": "India wins a thriller",
    "likes": 10,
    "comments": 2,
    "created_at": "2026-10-24 10:00:00",
    "media_type": "video",
    "visibility": "public",
    "post_id": "post-1",
}
norm = enr._normalize_ig_post(item, "icc")
check("normalize keeps exact-owner public reel",
      norm and norm["shortCode"] == "ABC123" and norm["ownerUsername"] == "icc"
      and norm["caption"] == "India wins a thriller" and norm["post_id"] == "post-1")
check("normalize rejects a different author",
      enr._normalize_ig_post({**item, "username": "someoneelse"}, "icc") is None)
check("normalize rejects non-public post",
      enr._normalize_ig_post({**item, "visibility": "private"}, "icc") is None)
check("normalize rejects URL without a post shortcode",
      enr._normalize_ig_post({**item, "url": "https://www.instagram.com/icc/"}, "icc") is None)

# ── Connector fetch: grouping + 429 hard stop ─────────────────────────────
class FakeResult:
    def __init__(self, stdout, returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


orig_enr_subprocess = enr.subprocess
calls = []


def fake_run_success(cmd, **_kwargs):
    calls.append(cmd)
    handle = cmd[cmd.index("--username") + 1]
    payload = {"posts": [
        {"username": handle, "url": "https://www.instagram.com/p/OK123/",
         "post_caption": "hello", "visibility": "public",
         "post_id": "18142955500011122", "likes": 4291},
        {"username": "intruder", "url": "https://www.instagram.com/p/BAD123/",
         "post_caption": "not theirs", "visibility": "public"},
    ]}
    return FakeResult(json.dumps(payload))


enr.subprocess = SimpleNamespace(run=fake_run_success)
enr.IG_RATE_LIMITED = False
got = enr.fetch_ig_posts_live(["icc", "bcci"], results_limit=5)
enr.subprocess = orig_enr_subprocess
check("connector fetch groups only exact-owner posts",
      len(got.get("icc", [])) == 1 and got["icc"][0]["shortCode"] == "OK123"
      and len(got.get("bcci", [])) == 1 and len(calls) == 2)
check("payload digits containing 429 do not trip the rate-limit stop",
      enr.IG_RATE_LIMITED is False)

calls = []


def fake_run_429(cmd, **_kwargs):
    calls.append(cmd)
    return FakeResult(json.dumps({"provider_error": {"code": 429, "message": "rate limited"}}))


enr.subprocess = SimpleNamespace(run=fake_run_429)
enr.IG_RATE_LIMITED = False
got = enr.fetch_ig_posts_live(["first", "second"], results_limit=5)
enr.subprocess = orig_enr_subprocess
check("429 is a hard stop for remaining handles",
      got == {} and len(calls) == 1 and enr.IG_RATE_LIMITED is True)
enr.IG_RATE_LIMITED = False

# ── Prefetch: cache-first + per-run live cap ──────────────────────────────
orig_match = enr.match_handles
orig_fetch = enr.fetch_ig_posts_live
orig_cap = enr.IG_MAX_LIVE_HANDLES_PER_RUN
handles_by_headline = {
    "One": [{"name": "Fresh Person", "handle": "fresh"}],
    "Two": [{"name": "Stale Person", "handle": "stale"}],
    "Three": [{"name": "Third Person", "handle": "third"}],
}
enr.match_handles = lambda headline, registry, platform: handles_by_headline[headline]
live_calls = []


def fake_prefetch_fetch(handles, results_limit=12):
    live_calls.append(list(handles))
    return {handles[0]: [{"shortCode": "NEW1", "caption": "fresh evidence",
                          "url": "https://www.instagram.com/p/NEW1/",
                          "ownerUsername": handles[0]}]}


enr.fetch_ig_posts_live = fake_prefetch_fetch
enr.IG_MAX_LIVE_HANDLES_PER_RUN = 1
cache = {"ig": {
    "fresh": {"posts": [{"shortCode": "F1"}], "fetched_at": NOW},
    "stale": {"posts": [{"shortCode": "S0"}], "fetched_at": "2020-01-01T00:00:00Z"},
    "third": {"posts": [{"shortCode": "T0"}], "fetched_at": "2020-01-01T00:00:00Z"},
}}
articles = [{"headline": h, "body": ""} for h in ("One", "Two", "Three")]
live = enr.prefetch_ig_for_articles(articles, {}, cache=cache, persist=False)
enr.match_handles = orig_match
enr.fetch_ig_posts_live = orig_fetch
enr.IG_MAX_LIVE_HANDLES_PER_RUN = orig_cap
check("prefetch refreshes only the first stale handle under the cap",
      live_calls == [["stale"]] and "stale" in live and "third" not in live)
check("prefetch updates the in-memory cache for the refreshed handle",
      cache["ig"]["stale"]["posts"][0]["shortCode"] == "NEW1")
check("prefetch leaves fresh and deferred cache entries untouched",
      cache["ig"]["fresh"]["posts"][0]["shortCode"] == "F1"
      and cache["ig"]["third"]["posts"][0]["shortCode"] == "T0")

# ── Enrichment evidence gate ──────────────────────────────────────────────
orig_match = enr.match_handles
enr.match_handles = lambda headline, registry, platform: [
    {"name": "Virat Kohli", "handle": "virat.kohli", "group": "persons"}]
article = {"headline": "Virat Kohli announces cricket academy launch", "body": ""}


def ig_cache_with(posts):
    return {"ig": {"virat.kohli": {"posts": posts, "fetched_at": NOW}}}


unrelated = [{"shortCode": "U1", "caption": "Welcome aboard this rocket ship",
              "url": "https://www.instagram.com/p/U1/", "ownerUsername": "virat.kohli"}]
url, info = enr.enrich_ig_from_cache(article, ig_cache_with(unrelated), {})
check("no embed from a person's unrelated latest post", url is None and info is None)

topical = [{"shortCode": "R1", "caption": "Official launch of a cricket academy for young players",
            "url": "https://www.instagram.com/reel/R1/", "ownerUsername": "virat.kohli",
            "timestamp": "2026-10-24 09:00:00", "post_id": "p1"}]
url, info = enr.enrich_ig_from_cache(article, ig_cache_with(topical), {})
check("topical post embeds with its exact reel URL",
      url == "https://www.instagram.com/reel/R1/")
check("evidence records score, matched terms, and post id",
      info and info["score"] == 8 and "cricket" in info["matched_keywords"]
      and "academy" in info["matched_keywords"] and info["post_id"] == "p1")

wrong_owner = [{**topical[0], "ownerUsername": "not.kohli"}]
url, info = enr.enrich_ig_from_cache(article, ig_cache_with(wrong_owner), {})
check("topical caption from the wrong owner is rejected", url is None and info is None)

substring_only = [{"shortCode": "S1", "caption": "Looking forward to the weekend",
                   "url": "https://www.instagram.com/p/S1/", "ownerUsername": "virat.kohli"}]
king_article = {"headline": "Virat Kohli king returns", "body": ""}
url, info = enr.enrich_ig_from_cache(king_article, ig_cache_with(substring_only), {})
check("substring-only caption match is rejected", url is None and info is None)
enr.match_handles = orig_match

# ── Targeted fetch by article IDs (was a silent None) ────────────────────
orig_sb_get = enr.sb_get
seen_params = []
enr.sb_get = lambda table, params: seen_params.append((table, params)) or [{"id": "a1"}]
got = enr.fetch_articles(article_ids=["a1", "b2"])
enr.sb_get = orig_sb_get
check("fetch_articles by IDs returns the queried rows",
      got == [{"id": "a1"}] and seen_params
      and seen_params[0][1]["id"] == "in.(a1,b2)")

# ── Cache refresh rotation ────────────────────────────────────────────────
orig_ref_fetch = ref.fetch_ig_posts_batch
selected_seen = []


def fake_refresh_fetch(handles, results_limit=12):
    selected_seen.append(list(handles))
    return {h: [{"shortCode": "N1", "caption": "x",
                 "url": "https://www.instagram.com/p/N1/", "ownerUsername": h}]
            for h in handles}


ref.fetch_ig_posts_batch = fake_refresh_fetch
existing = {"ig": {
    "aaa": {"posts": [{"shortCode": "OLD"}], "fetched_at": "2020-01-01T00:00:00Z"},
    "ccc": {"posts": [{"shortCode": "KEEP"}], "fetched_at": NOW},
}}
updated = ref.refresh_ig_cache(["aaa", "bbb", "ccc"], existing, max_handles=2)
ref.fetch_ig_posts_batch = orig_ref_fetch
check("refresh rotates missing/oldest handles first",
      selected_seen == [["bbb", "aaa"]])
check("refresh preserves unreached cache entries",
      updated["ccc"]["posts"][0]["shortCode"] == "KEEP"
      and updated["aaa"]["posts"][0]["shortCode"] == "N1"
      and updated["bbb"]["posts"][0]["shortCode"] == "N1")

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
