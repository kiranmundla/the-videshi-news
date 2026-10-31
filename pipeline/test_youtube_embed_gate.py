"""Regression tests for the shared YouTube embed gate (embed_placement.py).

Covers the 2026-10-15 hardening after the reviewer stripped two junk
embeds in 12 hours:
  1. "AI chatbots prioritizing engagement over safety" on Pramila
     Jayapal's voter-roll article — off-topic, rode in on her own
     channel's authority via enrich-articles' weak score>=3 acceptance.
  2. "My NIGHTMARE Experience Flying Air India Economy class to Delhi"
     on the Air India Delhi–Osaka route-launch article — a first-person
     rant vlog, present in BOTH the body <youtube> tag and social_embeds.

Fixtures use the real headlines/titles and the keyword lists the
enrichers' own extractors produce for them. Legit cases (official
trailer, airline announcement, ISRO launch, NDTV Profit results video)
must still pass.

Run: python3 test_youtube_embed_gate.py  (exit 0 = all pass)
"""
import sys
from datetime import datetime, timedelta, timezone

from embed_placement import (youtube_embed_accept,
                             youtube_embed_reject_reason,
                             score_youtube_result)

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


def result(title, channel):
    return {"videoId": "dQw4w9WgXcQ", "title": title,
            "channelTitle": channel, "publishedAt": FRESH}


# ─── REAL FAILURE 1: chatbots video on Jayapal voter-roll article ────
# Keywords = enrich-on-publish extractor output for this headline/entity.
score, reason = youtube_embed_accept(
    result("AI chatbots prioritizing engagement over safety",
           "Pramila Jayapal"),
    "Pramila Jayapal",
    ["chennai", "born", "congresswoman", "backs"],
    headline="Chennai-Born Congresswoman Pramila Jayapal Backs India "
             "Protests Over Voter Roll Deletions")
check("fail1: chatbots-on-Jayapal rejected", reason is not None,
      f"(got score={score}, reason={reason})")
check("fail1: reason is topical overlap",
      reason == "no topical overlap with article headline",
      f"(got {reason!r})")
# The old enrich-articles fork accepted at raw score >= 3 with no keyword
# floor — this fixture's raw score clears that bar, proving the hole.
raw = score_youtube_result(
    result("AI chatbots prioritizing engagement over safety",
           "Pramila Jayapal"),
    "Pramila Jayapal", ["chennai", "born", "congresswoman", "backs"])
check("fail1: raw score would have passed the OLD enrich-articles bar",
      raw >= 3, f"(raw={raw})")

# ─── REAL FAILURE 2: first-person rant on Air India route launch ─────
score, reason = youtube_embed_accept(
    result("My NIGHTMARE Experience Flying Air India Economy class to Delhi",
           "Wanderlust Vlogs"),
    "Air India",
    ["launch", "non", "stop", "delhi"],
    headline="Air India to Launch Non-Stop Delhi-Osaka Flights From "
             "February 2, 2027")
check("fail2: Air India nightmare vlog rejected", reason is not None,
      f"(got score={score}, reason={reason})")
check("fail2: reason is first-person/vlog",
      reason is not None and "first-person" in reason, f"(got {reason!r})")

# ─── LEGIT 1: official teaser from allowlisted channel ───────────────
score, reason = youtube_embed_accept(
    result("JAILER 2 - Official Teaser | Superstar Rajinikanth | Sun Pictures",
           "Sun Pictures"),
    "Rajinikanth",
    ["jailer", "teaser", "returns", "muthuvel"],
    headline="Jailer 2 Teaser: Rajinikanth Returns as Muthuvel Pandian "
             "in Nelson's Sequel")
check("legit1: official Jailer 2 teaser accepted", reason is None,
      f"(got score={score}, reason={reason})")

# ─── LEGIT 2: airline's own route announcement ───────────────────────
score, reason = youtube_embed_accept(
    result("Air India Announces Non-Stop Flights Between Delhi and Osaka",
           "Air India"),
    "Air India",
    ["launch", "non", "stop", "delhi"],
    headline="Air India to Launch Non-Stop Delhi-Osaka Flights From "
             "February 2, 2027")
check("legit2: Air India route announcement accepted", reason is None,
      f"(got score={score}, reason={reason})")

# ─── LEGIT 3: ISRO launch footage (single-word entity, bar = 8) ──────
score, reason = youtube_embed_accept(
    result("ISRO Launches Gaganyaan G-1 Mission | Live From Sriharikota",
           "ISRO"),
    "ISRO",
    ["successfully", "launches", "gaganyaan", "mission"],
    headline="ISRO Successfully Launches Gaganyaan G-1 Mission From "
             "Sriharikota")
check("legit3: ISRO launch accepted", reason is None,
      f"(got score={score}, reason={reason})")

# ─── LEGIT 4: news-channel results video, no entity channel ──────────
# Also guards the word-boundary junk match: "Beats" must NOT trip the
# "beat" junk word, and the channel-relevance penalty must not sink it.
score, reason = youtube_embed_accept(
    result("Wipro Q2 Results: Revenue Beats Estimates, Shares Jump",
           "NDTV Profit"),
    "Wipro",
    ["revenue", "beats", "estimates", "sensex"],
    headline="Wipro Q2 Revenue Beats Estimates as Sensex Rallies "
             "1,534 Points")
check("legit4: Wipro results on NDTV Profit accepted", reason is None,
      f"(got score={score}, reason={reason})")

# ─── Gate unit checks (title/channel only, no headline) ──────────────
check("gate: pirate-bait rejected",
      youtube_embed_reject_reason("Some Film Full Movie Watch Online",
                                  "Random Channel") == "pirate-bait title")
check("gate: trailer from non-official channel rejected",
      "non-official channel" in
      (youtube_embed_reject_reason("New Film Official Trailer",
                                   "Random Channel") or ""))
check("gate: official-channel trailer passes",
      youtube_embed_reject_reason(
          "JAILER 2 - Official Teaser | Superstar Rajinikanth | Sun Pictures",
          "Sun Pictures") is None)
check("gate: 'I tried' vlog rejected",
      youtube_embed_reject_reason("I Tried the Cheapest Flight to Delhi",
                                  "Some Vlogger") is not None)
check("gate: 'honest review' rejected",
      youtube_embed_reject_reason("Air India A350 Honest Review",
                                  "Some Vlogger") is not None)
check("gate: plain news title passes",
      youtube_embed_reject_reason("ISRO Launches Gaganyaan Mission",
                                  "ISRO") is None)
# 2026-10-30: config aliases count as the channel — Sun Pictures uploads
# appear under the "Sun TV" display name; the gate rejected an official
# Sun TV trailer and a fan video took its place.
check("gate: alias-channel trailer passes (Sun TV = Sun Pictures)",
      youtube_embed_reject_reason(
          "JAILER 2 - Official Trailer | Superstar Rajinikanth | "
          "Nelson | Anirudh", "Sun TV") is None)
check("gate: alias does not rescue pirate-bait",
      youtube_embed_reject_reason("Jailer 2 Full Movie Watch Online",
                                  "Sun TV") == "pirate-bait title")
check("gate: near-name fan channel still rejected",
      "non-official channel" in
      (youtube_embed_reject_reason("JAILER 2 - Official Trailer",
                                   "Sun TV Official Fan") or ""))

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
