"""Tests for watchlist_pilot.py — scorer parsing, corroboration matcher,
evidence gate, watermark/dedup helpers, RSS parser.

Network-free: the module is imported directly (its network functions are
only called from the pipeline driver, never at import).

Run: python3 test_watchlist_pilot.py  (exit 0 = all pass)
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchlist_pilot as wp

fails = 0
total = 0


def check(name, cond):
    global fails, total
    total += 1
    if cond:
        print(f"  ✓ {name}")
    else:
        fails += 1
        print(f"  ✗ FAIL: {name}")


NOW = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)

# ── parse_score_results ──────────────────────────────────────────────────────
content = {"results": [
    {"id": 1, "score": 9, "type": "announcement", "summary": "ok",
     "entities": ["SpaceX", "Starlink"], "category": "tech"},
    {"id": 2, "score": "not-a-number", "type": "promo", "summary": "x",
     "entities": "oops", "category": "news"},
    "bare-string-item",
    {"id": 99, "score": 10, "type": "result", "summary": "out of range"},
    {"id": 3, "score": 27, "type": "result", "summary": "clamped",
     "entities": [], "category": "cricket"},
]}
parsed = wp.parse_score_results(content, 3)
check("scorer: valid item parsed", parsed.get(0, {}).get("score") == 9.0)
check("scorer: category normalised (tech->technology)",
      parsed.get(0, {}).get("category") == "technology")
check("scorer: bad score -> 0, bad entities -> []",
      parsed.get(1, {}).get("score") == 0.0 and parsed.get(1, {}).get("entities") == [])
check("scorer: bare string item skipped, out-of-range id skipped",
      len(parsed) == 3 and all(0 <= k < 3 for k in parsed))
check("scorer: score clamped to 10", parsed.get(2, {}).get("score") == 10.0)
check("scorer: cricket category normalised to sports",
      parsed.get(2, {}).get("category") == "sports")
check("scorer: non-dict content -> {}", wp.parse_score_results(None, 3) == {})

# ── passes_score_gate ────────────────────────────────────────────────────────
check("gate: 9/10 announcement passes",
      wp.passes_score_gate({"score": 9, "type": "announcement"}))
check("gate: 9/10 promo FAILS (type checked independently)",
      not wp.passes_score_gate({"score": 9, "type": "promo"}))
check("gate: 10/10 greeting FAILS",
      not wp.passes_score_gate({"score": 10, "type": "greeting"}))
check("gate: 6/10 statement fails threshold",
      not wp.passes_score_gate({"score": 6, "type": "statement"}))
check("gate: 7/10 result passes at threshold",
      wp.passes_score_gate({"score": 7, "type": "result"}))
check("gate: None result fails", not wp.passes_score_gate(None))

# ── match_corroboration ──────────────────────────────────────────────────────
cand_toks, cand_phrases = wp.candidate_keywords(
    "SpaceX launches 27 Starlink satellites from Vandenberg aboard Falcon 9",
    ["SpaceX", "Starlink", "Falcon 9"])
items = [
    {"title": "Random unrelated market wrap", "source_name": "Wire",
     "url": "https://example.com/a"},
    {"title": "SpaceX Falcon 9 launches Starlink satellites from Vandenberg",
     "source_name": "Reuters", "url": "https://example.com/b"},
    {"title": "SpaceX Starlink Falcon 9 Vandenberg launch (official)",
     "source_name": "spacex", "url": "https://x.com/spacex/status/1"},
]
hit = wp.match_corroboration(cand_toks, cand_phrases, items,
                             {"spacex", "SpaceX", "https://x.com/spacex/status/1"})
check("matcher: finds the Reuters corroboration", hit is not None and hit[0]["source_name"] == "Reuters")
check("matcher: shared-token count >= 3", hit is not None and hit[1] >= 3)

self_only = [{"title": "SpaceX Starlink Falcon 9 Vandenberg launch",
              "source_name": "SpaceX", "url": "https://x.com/spacex/status/1"}]
check("matcher: self-source never corroborates",
      wp.match_corroboration(cand_toks, cand_phrases, self_only,
                             {"spacex", "https://x.com/spacex/status/1"}) is None)
check("matcher: unrelated item does not match",
      wp.match_corroboration(cand_toks, cand_phrases, items[:1], set()) is None)
check("matcher: empty items -> None",
      wp.match_corroboration(cand_toks, cand_phrases, [], set()) is None)

weak_toks, weak_phrases = wp.candidate_keywords("Kohli announces retirement",
                                                ["Virat Kohli"])
phrase_items = [{"title": "Virat Kohli stuns fans with announcement",
                 "source_name": "PTI", "url": "https://example.com/c"}]
hit2 = wp.match_corroboration(weak_toks, weak_phrases, phrase_items, {"imvkohli"})
check("matcher: entity-phrase + token match counts", hit2 is not None)

# ── strict already-published dedup (min_ratio mode) ──────────────────────────
# Same person, DIFFERENT story — must NOT count as already published.
arsh_toks, arsh_phrases = wp.candidate_keywords(
    "Arshdeep Singh becomes India's highest T20I wicket-taker with 99 wickets",
    ["Arshdeep Singh"])
arsh_articles = [{"title": "Arshdeep Singh Retires Hurt With Arm Blow as West "
                           "Indies Level Series in Hyderabad",
                  "source_name": "The Videshi (published)",
                  "url": "https://www.thevideshi.com/articles/x", "extra_text": ""}]
check("dedup-strict: same person, different event -> NOT a duplicate",
      wp.match_corroboration(arsh_toks, arsh_phrases, arsh_articles, set(),
                             min_shared=4, phrase_min_shared=2,
                             min_ratio=0.30) is None)
# Same event — MUST count as already published.
karak_toks, karak_phrases = wp.candidate_keywords(
    "India condemns the Karak church attack in Jordan and expresses "
    "condolences as the death toll rises to eight",
    ["S. Jaishankar"])
karak_articles = [{"title": "India Condemns Karak Church Attack as Jordan "
                            "Raises Death Toll to Eight",
                   "source_name": "The Videshi (published)",
                   "url": "https://www.thevideshi.com/articles/y", "extra_text": ""}]
check("dedup-strict: same event -> duplicate detected",
      wp.match_corroboration(karak_toks, karak_phrases, karak_articles, set(),
                             min_shared=4, phrase_min_shared=2,
                             min_ratio=0.30) is not None)

# ── evidence gate in build_sample_article ────────────────────────────────────
post = {
    "platform": "x", "entry_name": "SpaceX", "lane": "A", "handle": "spacex",
    "id": "123", "text": "Falcon 9 launches 27 Starlink satellites",
    "url": "https://x.com/spacex/status/123",
    "created_at_dt": NOW, "photos": [], "has_video": False, "origin": "live",
}
scored = {"score": 9, "type": "launch", "summary": "s", "category": "technology",
          "entities": ["SpaceX"]}
writer = {"headline": "SpaceX Launches 27 Starlink Satellites From California",
          "subheadline": "sub", "takeaways": ["t1", "t2", "t3"],
          "paragraphs": ["In a post on X, SpaceX announced the launch.",
                         "The booster landed successfully."],
          "tags": ["spacex"], "diaspora_angle": ""}

check("evidence gate: NO corroboration -> NO draft",
      wp.build_sample_article(post, scored, None, writer) is None)
check("evidence gate: corroboration without URL -> NO draft",
      wp.build_sample_article(post, scored, {"source_name": "X", "url": ""}, writer) is None)

corr = {"source_name": "Reuters", "url": "https://example.com/spacex-launch",
        "title": "SpaceX launches Starlink satellites", "extra_text": ""}
art = wp.build_sample_article(post, scored, corr, writer)
check("evidence gate: corroborated -> draft built", art is not None)
check("draft: >=2 distinct sources",
      art is not None and len({s["url"] for s in art["sources"]}) >= 2)
check("draft: post URL is source #1",
      art is not None and art["sources"][0]["url"] == post["url"])
check("draft: post embedded in body (bare URL line)",
      art is not None and f"\n\n{post['url']}\n" in "\n\n" + art["body"] + "\n"
      or (art is not None and post["url"] in art["body"]))
check("draft: key-takeaways block present",
      art is not None and '<div class="key-takeaways">' in art["body"])
check("draft: attribution in first paragraph",
      art is not None and "In a post on X" in art["body"])
check("draft: category carried from scorer",
      art is not None and art["category"] == "technology")
check("draft: no writer output -> None",
      wp.build_sample_article(post, scored, corr, None) is None)

# photos: org post photo becomes writer-preset hero; persons get search hint
post_photo = dict(post, photos=["https://pbs.twimg.com/media/xyz.jpg"])
art2 = wp.build_sample_article(post_photo, scored, corr, writer)
check("draft: post photo preset as hero for org post",
      art2 is not None and art2.get("image_url", "").endswith("xyz.jpg"))
person_post = dict(post, entry_name="Virat Kohli", lane="B", handle="imvkohli",
                   photos=[])
art3 = wp.build_sample_article(person_post, scored, corr, writer)
check("draft: Lane B person gets verified-portrait search hint",
      art3 is not None and art3.get("image_search_persons") == ["Virat Kohli"])

# ── watermark / dedup ────────────────────────────────────────────────────────
wm = NOW - timedelta(hours=72)
fresh = {"id": "1", "platform": "x", "created_at_dt": NOW}
stale = {"id": "2", "platform": "x", "created_at_dt": NOW - timedelta(hours=100)}
check("watermark: fresh unseen post is new", wp.is_new_post(fresh, wm, set()))
check("watermark: stale post is not new", not wp.is_new_post(stale, wm, set()))
check("watermark: platform-prefixed seen key blocks reprocessing",
      not wp.is_new_post(fresh, wm, {"x:1"}))
check("watermark: same id on another platform is a different post",
      wp.is_new_post(dict(fresh, platform="ig"), wm, {"x:1"}))

xp = {"platform": "x", "entry_name": "SpaceX", "id": "1", "photos": [],
      "text": "Falcon 9 launches 27 Starlink satellites from Vandenberg today"}
igp = {"platform": "ig", "entry_name": "SpaceX", "id": "2",
       "photos": ["https://img/1.jpg"],
       "text": "Falcon 9 launches 27 Starlink satellites from Vandenberg today"}
other = {"platform": "x", "entry_name": "ISRO", "id": "3", "photos": [],
         "text": "Gaganyaan crew module test completed successfully today"}
ded = wp.dedupe_candidates([xp, igp, other])
check("dedup: cross-post merged to one", len(ded) == 2)
merged = [d for d in ded if d["entry_name"] == "SpaceX"][0]
check("dedup: richer (media) version kept", merged["platform"] == "ig")
check("dedup: merge recorded", bool(merged.get("merged_from")))

# ── timestamps + slug ────────────────────────────────────────────────────────
check("time: X format parsed",
      wp.parse_post_time("Mon Oct 05 02:00:00 +0000 2026", "x") is not None)
check("time: IG format parsed",
      wp.parse_post_time("2026-10-23 17:16:40", "ig") is not None)
check("time: garbage -> None", wp.parse_post_time("not a date", "x") is None)
check("time: Atom fractional-second Z parsed (Apple Newsroom shape)",
      wp.parse_post_time("2026-10-23T06:10:35.677Z", "rss") is not None)
check("source name: null RSS source falls back to domain",
      wp._source_display_name({"source_name": None, "source_type": "rss",
                               "original_url": "https://timesofindia.indiatimes.com/a.cms"})
      == "timesofindia.indiatimes.com")
check("source name: google_news null name -> 'Google News'",
      wp._source_display_name({"source_name": "", "source_type": "google_news",
                               "original_url": "https://news.google.com/rss/articles/x"})
      == "Google News")
check("source name: real name wins",
      wp._source_display_name({"source_name": "Reuters", "source_type": "rss",
                               "original_url": "https://reuters.com/x"}) == "Reuters")
check("slugify", wp.slugify("SpaceX Launches 27 Starlink Satellites!")
      == "spacex-launches-27-starlink-satellites")

# ── RSS parser ───────────────────────────────────────────────────────────────
RSS = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>OpenAI announces GPT-9</title><link>https://openai.com/index/gpt-9</link>
<pubDate>Fri, 24 Oct 2026 10:00:00 GMT</pubDate><guid>g1</guid>
<description>The new model is available today.</description></item>
<item><title>Second item</title><link>https://openai.com/index/two</link>
<pubDate>Fri, 24 Oct 2026 09:00:00 GMT</pubDate><description>d2</description></item>
</channel></rss>"""
items = wp.parse_feed(RSS, "OpenAI News", "https://openai.com/news/rss.xml")
check("rss: two items parsed", len(items) == 2)
check("rss: title/text/url/date carried",
      items and items[0]["url"] == "https://openai.com/index/gpt-9"
      and "GPT-9" in items[0]["text"] and items[0]["created_at_dt"] is not None)
ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Atom post</title><link rel="alternate" href="https://example.com/a"/>
<published>2026-10-24T08:00:00Z</published><summary>Summary text</summary><id>urn:1</id></entry></feed>"""
aitems = wp.parse_feed(ATOM, "Atom", "https://example.com/feed")
check("rss: atom entry parsed", len(aitems) == 1 and aitems[0]["url"] == "https://example.com/a")
check("rss: garbage -> []", wp.parse_feed("<not xml", "x", "y") == [])

print(f"\n{total - fails}/{total} checks passed")
sys.exit(1 if fails else 0)
