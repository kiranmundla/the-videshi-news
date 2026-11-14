"""Regression tests for the trailer channel-authority gate
(embed_placement.trailer_embed_gate / channel_authority_reason,
media-sources._verify_official_trailer, roster precedence inputs).

The case (2026-10-31): enrich-articles' trailer pass embedded
y05zEL0O4As — "'Jailer 2' box office collection worldwide gross
reaches Rs 733.35 cr" from the fan/news channel Narayanatv — into the
Jailer 2 box-office article as its "trailer". It was not a trailer,
not the official channel (Sun Pictures), and its figure contradicted
the article's headline. The route's verifier
(media-sources._verify_official_trailer) ran only
youtube_embed_reject_reason on the oEmbed title/channel — and that
gate's channel rule fires solely on trailer/teaser titles, so a
non-trailer video from a fan channel passed untouched. The same weak
verifier shape sat in source-image.py, and the generic search routes
(enrich_youtube / find_best_youtube_embed) had no channel authority
and no US region gate at all.

Fixtures use the REAL titles/channels: the Narayanatv video (oEmbed),
the real Sun Pictures trailer FW_PPcr1sPE (Data API metadata fetched
live 2026-10-31: channel "Sun TV", id UCBnxEdpoZwstJqC1yZpOjRA, no
region restriction), and the real article headline/roster.

Run: python3 test_trailer_channel_gate.py  (exit 0 = all pass)
"""
import sys
from datetime import datetime, timedelta, timezone

import review_trailer as rt
from embed_placement import (channel_authority_reason,
                             trailer_embed_gate, youtube_embed_accept)
from importlib.machinery import SourceFileLoader

ms = SourceFileLoader("media_sources", "media-sources.py").load_module()

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


FRESH = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
    "%Y-%m-%dT%H:%M:%SZ")

JAILER_HEADLINE = ("Jailer 2 Dips 20 Percent on Tuesday, "
                   "India Gross Reaches Rs 462.75 Crore")
JAILER_ARTICLE = {"headline": JAILER_HEADLINE,
                  "slug": "jailer-2-tuesday-drop-india-gross-462-crore",
                  "category": "entertainment", "body": ""}

NARAYANA_TITLE = ("'Jailer 2' box office collection worldwide gross "
                  "reaches Rs 733.35 cr")
NARAYANA_META = {"title": NARAYANA_TITLE, "channel_title": "Narayanatv",
                 "channel_id": "UCnarayanatv000000000",
                 "region_restriction": None}
SUN_META = {"title": "JAILER 2 - Official Trailer | Superstar "
                     "Rajinikanth | Sun Pictures | Anirudh | Nelson",
            "channel_title": "Sun TV",
            "channel_id": "UCBnxEdpoZwstJqC1yZpOjRA",
            "region_restriction": None}

# ─── trailer_embed_gate: the Narayanatv case ─────────────────────────
reason = trailer_embed_gate(
    NARAYANA_TITLE, "Narayanatv", channel_id=NARAYANA_META["channel_id"],
    region_restriction=None, region_checked=True, film_title="Jailer 2")
check("gate: Narayanatv box-office video rejected as trailer",
      reason is not None, f"(got {reason!r})")
check("gate: Narayanatv reason is the trailer-title leg",
      reason is not None and "does not say trailer/teaser" in reason,
      f"(got {reason!r})")

# Same video with a trailer-bait title still dies on channel authority.
reason = trailer_embed_gate(
    "Jailer 2 Official Trailer | Box Office Collection", "Narayanatv",
    channel_id=NARAYANA_META["channel_id"], region_restriction=None,
    region_checked=True, film_title="Jailer 2")
check("gate: fan channel with trailer title rejected on authority",
      reason is not None and ("allowlist" in reason
                              or "non-official channel" in reason),
      f"(got {reason!r})")

# ─── trailer_embed_gate: the real Sun Pictures trailer ───────────────
reason = trailer_embed_gate(
    SUN_META["title"], "Sun TV", channel_id=SUN_META["channel_id"],
    region_restriction=None, region_checked=True, film_title="Jailer 2")
check("gate: Sun TV official trailer accepted", reason is None,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    SUN_META["title"], "Sun TV", channel_id=SUN_META["channel_id"],
    region_restriction=None, region_checked=True, film_title="Udta Teer")
check("gate: right channel, wrong film rejected",
      reason is not None and "does not name the film" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    SUN_META["title"], "Sun TV", channel_id=SUN_META["channel_id"],
    region_restriction={"allowed": ["IN"]}, region_checked=True,
    film_title="Jailer 2")
check("gate: US-region-blocked trailer rejected",
      reason is not None and "region-blocked" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    SUN_META["title"], "Sun TV", channel_id=SUN_META["channel_id"],
    region_restriction=None, region_checked=False, film_title="Jailer 2")
check("gate: unverified region rejected (fail-closed)",
      reason is not None and "fail-closed" in reason, f"(got {reason!r})")

# News-org status does NOT confer trailer authority (Sun News is a
# real news channel; its Jailer 2 segment is not the film's trailer).
reason = trailer_embed_gate(
    "Jailer 2 - Official Trailer | Rajinikanth", "Sun News",
    channel_id="UCsunnews000000000000", region_restriction=None,
    region_checked=True, film_title="Jailer 2")
check("gate: news channel cannot carry a trailer embed",
      reason is not None and ("allowlist" in reason
                              or "non-official channel" in reason),
      f"(got {reason!r})")

# Rahil Store pattern (2026-10-30, Salman article): fan channel,
# no trailer in the verified title at all.
reason = trailer_embed_gate(
    "Sanjay Dutt Ke Saath Salman Khan! Khalnayak Returns Mein Bada "
    "Twist?", "Rahil Store", channel_id="UCrahilstore000000000",
    region_restriction=None, region_checked=True)
check("gate: Rahil Store fan video rejected",
      reason is not None, f"(got {reason!r})")

# ─── Title exception: producer/studio channels (2026-11-13) ─────────
# Kiran-approved: Vels Music International (UCMsAo0XUISOL6O1ek_3QWfg),
# the producer channel for Mookuthi Amman 2, titled the film's official
# video "World Of Mahasakthi" with no trailer/teaser wording, and no
# trailer-titled official upload exists. trailer-channels.json flags
# producer/studio-owned channels with title_exception=true; for those
# channels ONLY, the title leg is waived when the title still names
# the film. Every other leg (authority, language, region) is unchanged.
VELS_TITLE = ("Mookuthi Amman 2 - World Of Mahasakthi | Nayanthara | "
              "Sundar C | Hiphop Tamizha | VELS FILM")
VELS_ID = "UCMsAo0XUISOL6O1ek_3QWfg"
AYNGARAN_ID = "UCGjn3ZbkkNcQaj00qwJ0DYQ"

reason = trailer_embed_gate(
    VELS_TITLE, "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: Vels featured film video accepted", reason is None,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    VELS_TITLE, "Vels Music International", channel_id=None,
    region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: Vels accepted by channel name alone",
      reason is None, f"(got {reason!r})")

reason = trailer_embed_gate(
    VELS_TITLE, "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True,
    film_title="Some Other Film", film_language="Tamil")
check("exception: film mismatch still rejected on the title leg",
      reason is not None and "does not say trailer/teaser" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    VELS_TITLE, "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True)
check("exception: no film_title still rejected on the title leg",
      reason is not None and "does not say trailer/teaser" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    "Mookuthi Amman 2 - World Of Mahasakthi", "Ayngaran",
    channel_id=AYNGARAN_ID, region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: non-rostered channel gets no exception",
      reason is not None, f"(got {reason!r})")

# Think Music India is rostered but is a music label — NOT flagged
# title_exception — so its non-trailer-titled video still fails leg 2.
reason = trailer_embed_gate(
    "Mookuthi Amman 2 - Official First Look", "Think Music India",
    channel_id=None, region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: rostered label without flag still title-rejected",
      reason is not None and "does not say trailer/teaser" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    "Mookuthi Amman 2 Trailer ( Tamil ) | Nayanthara | Sundar C | "
    "Hiphop Tamizha", "Ayngaran", channel_id=AYNGARAN_ID,
    region_restriction={"blocked": ["IN"]}, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: trailer-titled fan/aggregator upload still rejected",
      reason is not None, f"(got {reason!r})")

reason = trailer_embed_gate(
    VELS_TITLE, "Vels Music International", channel_id=VELS_ID,
    region_restriction={"blocked": ["US"]}, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("exception: US-region block still rejects under the exception",
      reason is not None and "region-blocked" in reason,
      f"(got {reason!r})")

# ─── Title-exception tightening: song/music screen (2026-11-13) ─────
# Kiran-approved after the exception's first live use passed a Vels
# SONG video (7H4SOzsX8m4, "Mahasakthi Trance Video") — right channel,
# title names the film, but not the featured film video. On the
# exception path only, song/music markers now deny the waiver. The
# normal trailer/teaser path is NOT screened.
reason = trailer_embed_gate(
    "Mahasakthi Trance Video | Mookuthi Amman 2 | Nayanthara | "
    "Sundar C | Hiphop Tamizha", "Vels Music International",
    channel_id=VELS_ID, region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("tightening: Vels trance song video denied the waiver",
      reason is not None and "title-exception denied" in reason
      and "trance" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    "Mookuthi Amman 2 - Lyrical Video Song | Nayanthara",
    "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("tightening: lyrical video song denied the waiver",
      reason is not None and "title-exception denied" in reason,
      f"(got {reason!r})")

reason = trailer_embed_gate(
    "Mookuthi Amman 2 - Behind The Scenes | Nayanthara",
    "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("tightening: behind-the-scenes video denied the waiver",
      reason is not None and "title-exception denied" in reason,
      f"(got {reason!r})")

# A properly trailer-titled video on the same flagged channel whose
# title ALSO mentions a song still passes via the normal path — the
# marker screen is exception-path only.
reason = trailer_embed_gate(
    "Mookuthi Amman 2 Official Trailer | Song Promo",
    "Vels Music International", channel_id=VELS_ID,
    region_restriction=None, region_checked=True,
    film_title="Mookuthi Amman 2", film_language="Tamil")
check("tightening: trailer title mentioning a song passes normally",
      reason is None, f"(got {reason!r})")

# ─── media-sources._verify_official_trailer (injected fetchers) ──────
def oe(meta):
    return lambda vid: {"title": meta["title"],
                        "author": meta["channel_title"]}


def mf(meta):
    return lambda vid: meta


url = ms._verify_official_trailer(
    "y05zEL0O4As", meta_fetcher=mf(NARAYANA_META),
    oembed_fetcher=oe(NARAYANA_META))
check("verify: Narayanatv candidate returns None", url is None,
      f"(got {url!r})")

url = ms._verify_official_trailer(
    "FW_PPcr1sPE", film_title="Jailer 2", meta_fetcher=mf(SUN_META),
    oembed_fetcher=oe(SUN_META))
check("verify: Sun Pictures trailer accepted",
      url == "https://youtube.com/watch?v=FW_PPcr1sPE", f"(got {url!r})")

url = ms._verify_official_trailer(
    "FW_PPcr1sPE", meta_fetcher=lambda vid: None,
    oembed_fetcher=oe(SUN_META))
check("verify: metadata failure fails closed", url is None,
      f"(got {url!r})")

url = ms._verify_official_trailer(
    "FW_PPcr1sPE", meta_fetcher=mf(SUN_META),
    oembed_fetcher=lambda vid: None)
check("verify: oEmbed failure fails closed", url is None,
      f"(got {url!r})")

blocked = dict(SUN_META, region_restriction={"blocked": ["US"]})
url = ms._verify_official_trailer(
    "FW_PPcr1sPE", meta_fetcher=mf(blocked), oembed_fetcher=oe(blocked))
check("verify: US-blocked trailer returns None", url is None,
      f"(got {url!r})")

# ─── Generic route: channel authority inside youtube_embed_accept ────
def result(title, channel, channel_id=""):
    return {"videoId": "dQw4w9WgXcQ", "title": title,
            "channelTitle": channel, "channelId": channel_id,
            "publishedAt": FRESH}


score, reason = youtube_embed_accept(
    result(NARAYANA_TITLE, "Narayanatv"),
    "Rajinikanth", ["india", "gross", "crore", "tuesday"],
    headline=JAILER_HEADLINE)
check("accept: Narayanatv video rejected on channel authority",
      reason is not None and "no verified authority" in reason,
      f"(got score={score}, reason={reason!r})")

score, reason = youtube_embed_accept(
    result("Wipro Q2 Results: Revenue Beats Estimates, Shares Jump",
           "NDTV Profit"),
    "Wipro", ["revenue", "beats", "estimates", "sensex"],
    headline="Wipro Q2 Revenue Beats Estimates as Sensex Rallies "
             "1,534 Points")
check("accept: recognized news channel still accepted",
      reason is None, f"(got score={score}, reason={reason!r})")

score, reason = youtube_embed_accept(
    result("ISRO Launches Gaganyaan G-1 Mission | Live From Sriharikota",
           "ISRO"),
    "ISRO", ["successfully", "launches", "gaganyaan", "mission"],
    headline="ISRO Successfully Launches Gaganyaan G-1 Mission From "
             "Sriharikota")
check("accept: entity's own channel still accepted", reason is None,
      f"(got score={score}, reason={reason!r})")

check("authority: allowlisted channel id passes",
      channel_authority_reason("Any Name", "UCGdHCtXEzkCB7-g_NXYZPcw",
                               "Someone") is None)
check("authority: fan channel rejected",
      channel_authority_reason("Filmy Star", None, "Rajinikanth")
      is not None)

# ─── Roster precedence inputs: the box-office article matches ────────
# enrich-articles' trailer pass and enrich-on-publish both consult
# review_trailer BEFORE any search route; these checks pin that the
# Jailer 2 box-office article (not a review) is claimed by the roster
# route, so the search route never gets to speak for it.
film = rt.match_roster_film(JAILER_ARTICLE, rt.load_roster())
check("roster: box-office slug/headline matches Jailer 2",
      film is not None and film.get("title") == "Jailer 2",
      f"(got {film and film.get('title')!r})")

decision = rt.review_trailer_for_article(
    JAILER_ARTICLE, meta_fetcher=mf(SUN_META))
check("roster: box-office article decision is the Sun trailer",
      decision.get("status") == "accepted"
      and decision.get("video_id") == "FW_PPcr1sPE",
      f"(got {decision!r})")

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
