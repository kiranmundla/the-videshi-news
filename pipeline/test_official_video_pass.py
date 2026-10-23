#!/usr/bin/env python3
"""Gate tests for the official-video embed pass (2026-10-22).

Style mirrors test_event_categorize.py / test_happenings_earnings_gate.py:
plain check() harness, fixture data (no network, no Supabase writes).

Cases:
  1. right video accepted (SQUASHTV R2 highlights on the Anahat article)
  2. wrong-topic video rejected (same official channel, different players)
  3. non-official channel rejected (identical title, fan channel)
  4. article already carrying a <youtube> embed is skipped without searching
  5. pirate-bait title rejected by the shared gate even on the official channel
  6. embed inserted after the first body paragraph (after key-takeaways)
  7. X widening: official handle discovered when mapped, deduped when in registry
  8. no channel mapped -> no_channel, no search
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILURES = []


def check(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'} {name}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(name)


def load(mod_name, filename):
    spec = importlib.util.spec_from_file_location(
        mod_name, os.path.join(HERE, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ovp = load("official_video_pass", "official_video_pass.py")

SQUASH = {"name": "SQUASHTV", "channel_id": "UCklie6BM0fhFvzWYqQVoCTA",
          "domain": "squash", "categories": ["sports"],
          "match_terms": ["squash"], "x_handle": "PSASquashTour",
          "rights_holder": "PSA Squash Tour"}
CHANNELS = [SQUASH]

ANA_BODY = (
    '<div class="key-takeaways"><ul><li>India\'s Anahat Singh, 18, beat '
    'Nour El Sherbini 11-8, 11-8, 11-7 in the second round of the '
    'Silicon Valley Open squash tournament.</li></ul></div>\n'
    '<p>Eighteen-year-old Anahat Singh produced the biggest win of her '
    'career on Wednesday, defeating eight-time world champion Nour '
    'El Sherbini at the Silicon Valley Open.</p>\n'
    '<p>El Sherbini arrived as the clear favourite.</p>\n')

ART = {"id": "test-1", "slug": "anahat-singh-stuns-el-sherbini",
       "headline": ("Anahat Singh Stuns Eight-Time World Champion "
                    "El Sherbini at Silicon Valley Open"),
       "category": "sports", "body": ANA_BODY,
       "published_at": "2026-10-22T04:48:43Z"}

R2_VIDEO = {"videoId": "KdXtalT2c-E",
            "title": "\U0001f1ee\U0001f1f3 Singh v ElSherbini "
                     "\U0001f1ea\U0001f1ec | Silicon Valley Open 2026 | "
                     "ROUND 2 HIGHLIGHTS",
            "channelTitle": "SQUASHTV", "channelId": "UCklie6BM0fhFvzWYqQVoCTA",
            "publishedAt": "2026-10-22T15:00:00Z"}

# ── 1. right video accepted ─────────────────────────────────────────────
calls = []


def fake_search_ok(entry, query, art):
    calls.append((entry["name"], query))
    return [R2_VIDEO]


res = ovp.official_video_for_article(ART, search_fn=fake_search_ok,
                                     channels=CHANNELS)
check("1 accepted status", res["status"], "accepted")
check("1 video id", res.get("video_id"), "KdXtalT2c-E")
check("1 decision accepted logged",
      [d for d in res["decisions"] if d.get("accepted")][0]["video_id"],
      "KdXtalT2c-E")

# ── 2. wrong-topic video rejected (same official channel) ───────────────
OTHER_MATCH = {"videoId": "XxXxXxXxXx1",
               "title": "Coll v Farag | Chicago Open 2026 | FINAL HIGHLIGHTS",
               "channelTitle": "SQUASHTV",
               "channelId": "UCklie6BM0fhFvzWYqQVoCTA",
               "publishedAt": "2026-10-22T15:00:00Z"}


def fake_search_wrong(entry, query, art):
    return [OTHER_MATCH]


res2 = ovp.official_video_for_article(ART, search_fn=fake_search_wrong,
                                      channels=CHANNELS)
check("2 status rejected", res2["status"], "rejected")
# Caught by whichever layer fires first — both name the topic mismatch:
# shared gate ("no topical overlap") or strong match ("no headline name").
_reason2 = res2["decisions"][0]["reason"]
check("2 rejection names the problem",
      ("topical overlap" in _reason2) or ("headline name" in _reason2), True)

# ── 3. non-official channel rejected (identical title) ──────────────────
FAN_COPY = dict(R2_VIDEO)
FAN_COPY["channelId"] = "UCfanupload999"
FAN_COPY["channelTitle"] = "Squash Replays HD"


def fake_search_fan(entry, query, art):
    return [FAN_COPY]


res3 = ovp.official_video_for_article(ART, search_fn=fake_search_fan,
                                      channels=CHANNELS)
check("3 status rejected", res3["status"], "rejected")
check("3 rejection is channel identity",
      "not the allowlisted" in res3["decisions"][0]["reason"], True)

# ── 4. already-has-embed skipped without searching ──────────────────────
searched = []


def fake_search_never(entry, query, art):
    searched.append(True)
    return [R2_VIDEO]


art_with_embed = dict(ART)
art_with_embed["body"] = ANA_BODY + "\n<youtube>rLcBFGk_IsY</youtube>\n"
res4 = ovp.official_video_for_article(art_with_embed,
                                      search_fn=fake_search_never,
                                      channels=CHANNELS)
check("4 skipped status", res4["status"], "skipped_has_embed")
check("4 no search executed", searched, [])

# ── 5. pirate-bait rejected on the official channel ─────────────────────
PIRATE = dict(R2_VIDEO)
PIRATE["videoId"] = "P1r4t3P1r4t3"
PIRATE["title"] = "Anahat Singh v El Sherbini full movie watch online free"


def fake_search_pirate(entry, query, art):
    return [PIRATE]


res5 = ovp.official_video_for_article(ART, search_fn=fake_search_pirate,
                                      channels=CHANNELS)
check("5 status rejected", res5["status"], "rejected")
check("5 pirate-bait named",
      "pirate-bait" in res5["decisions"][0]["reason"], True)

# ── 6. insert position: after first </p> past key-takeaways ──────────────
new_body = ovp.insert_after_first_paragraph(ANA_BODY, "KdXtalT2c-E")
idx_tag = new_body.index("<youtube>KdXtalT2c-E</youtube>")
idx_first_p = new_body.index("</p>")
idx_kt_end = new_body.index("</div>")
check("6 insert after first </p>", idx_first_p < idx_tag, True)
check("6 insert past key-takeaways", idx_kt_end < idx_tag, True)
check("6 single tag", new_body.count("<youtube>"), 1)
check("6 idempotent",
      ovp.insert_after_first_paragraph(new_body, "KdXtalT2c-E"), new_body)

# ── 7. X widening ───────────────────────────────────────────────────────
xc = ovp.official_x_candidates(ART, CHANNELS, registry_handles=())
check("7 official handle discovered",
      [c["handle"] for c in xc], ["PSASquashTour"])
check("7 source labeled", xc[0]["source"], "official-allowlist")
check("7 deduped against registry",
      ovp.official_x_candidates(ART, CHANNELS,
                                registry_handles=["psasquashtour"]), [])

# ── 7b. query construction: specific first, name fallback ────────────────
_qs = ovp.build_search_queries(ART, ovp.headline_people(ART["headline"]))
check("7b primary has both surnames + event",
      all(t in _qs[0] for t in ("Singh", "Sherbini", "Silicon Valley Open")),
      True)
check("7b fallback is the lead name", _qs[-1], "Anahat Singh")

# ── 9. team-match queries (2026-10-23) ──────────────────────────────────
TEAM_HL = ("India Eye 2-0 Lead in Second T20I Against New Zealand "
           "in Christchurch")
TEAM_ART = {"id": "test-team", "slug": "india-nz-t20i",
            "headline": TEAM_HL, "category": "sports",
            "body": "<p>Series preview: the cricket in Christchurch.</p>",
            "published_at": "2026-10-23T00:00:00Z"}
_tqs = ovp.build_search_queries(TEAM_ART,
                                 ovp.headline_people(TEAM_HL))
check("9 pair highlights query", "india new zealand highlights" in _tqs,
      True)
check("9 pair v query", "india v new zealand" in _tqs, True)
check("9 second-team highlights query",
      "new zealand highlights" in _tqs, True)
check("9 person queries stay first",
      _tqs.index("india new zealand highlights")
      > _tqs.index("India Eye"), True)
check("9 query cap", len(_tqs) <= 5, True)

REAL_HL = ("India Eye 2-0 Lead as Bowlers Face Christchurch Test "
           "in Second T20I")
REAL_ART = dict(TEAM_ART)
REAL_ART["headline"] = REAL_HL
_rqs = ovp.build_search_queries(REAL_ART,
                                ovp.headline_people(REAL_HL))
check("9 single-team highlights query", "india highlights" in _rqs, True)

_ana_qs = ovp.build_search_queries(ART, ovp.headline_people(ART["headline"]))
check("9 person article gets no team queries",
      [q for q in _ana_qs if q.endswith(" highlights") or " v " in q], [])

# ── 10. channel ranking + search cap (2026-10-23) ───────────────────────
BALL = {"name": "Ball Media", "channel_id": "UCball000000001",
        "domain": "football", "categories": ["sports"],
        "match_terms": ["football"], "x_handle": None}
LEAGUE = {"name": "League Media", "channel_id": "UCleague0000001",
          "domain": "football", "categories": ["sports"],
          "match_terms": ["premier league"], "x_handle": None}
FOOT_ART = {"id": "test-foot", "slug": "pl-returns",
            "headline": "Premier League Football Returns This Weekend",
            "category": "sports",
            "body": "<p>premier league football is back.</p>",
            "published_at": "2026-10-23T00:00:00Z"}
_ranked = ovp.channels_for_article(FOOT_ART, [BALL, LEAGUE])
check("10 multi-word term beats generic",
      [e["name"] for e, _w in _ranked], ["League Media", "Ball Media"])

GENERIC_CRICKET = {"name": "Cricket World", "channel_id": "UCgen000000001",
                   "domain": "cricket", "categories": ["sports"],
                   "match_terms": ["cricket"], "x_handle": None}
NZC = {"name": "New Zealand Cricket",
       "channel_id": "UCuKowzPg2-A0FcmyPa3yWug",
       "domain": "cricket", "categories": ["sports"],
       "match_terms": ["cricket", "blackcaps"], "x_handle": None}
_ranked2 = ovp.channels_for_article(TEAM_ART, [GENERIC_CRICKET, NZC])
check("10 name entity in headline ranks first",
      [e["name"] for e, _w in _ranked2],
      ["New Zealand Cricket", "Cricket World"])

cap_calls = []


def fake_search_cap(entry, query, art):
    cap_calls.append(entry["name"])
    return []


_six = [dict(GENERIC_CRICKET, name=f"Cricket Feed {i}",
             channel_id=f"UCcap00000000{i}") for i in range(6)]
CAP_ART = {"id": "test-cap", "slug": "cap",
           "headline": "India Beat Australia in Cricket Thriller",
           "category": "sports", "body": "<p>cricket</p>",
           "published_at": "2026-10-23T00:00:00Z"}
res_cap = ovp.official_video_for_article(CAP_ART,
                                         search_fn=fake_search_cap,
                                         channels=_six)
check("10 search capped at 4 channels", len(set(cap_calls)), 4)
check("10 cap noted in decisions",
      any("searching top 4" in (d.get("reason") or "")
          for d in res_cap["decisions"]), True)

# ── 10b. team query discovers the official highlight end-to-end ──────────
NZ_VIDEO = {"videoId": "NzV1deo2026",
            "title": "New Zealand v India | HIGHLIGHTS | Christchurch "
                     "| 2nd T20I",
            "channelTitle": "New Zealand Cricket",
            "channelId": "UCuKowzPg2-A0FcmyPa3yWug",
            "publishedAt": "2026-10-22T10:00:00Z"}


def fake_search_team(entry, query, art):
    if query == "india new zealand highlights":
        return [NZ_VIDEO]
    return []


res_team = ovp.official_video_for_article(TEAM_ART,
                                          search_fn=fake_search_team,
                                          channels=[NZC])
check("10b team highlight accepted via team query",
      res_team["status"], "accepted")
check("10b team video id", res_team.get("video_id"), "NzV1deo2026")

# ── 8. no channel mapped -> no_channel, no search ──
searched8 = []


def fake_search8(entry, query, art):
    searched8.append(True)
    return [R2_VIDEO]


cricket_art = dict(ART)
cricket_art["headline"] = "Kohli Hits Century as India Beat Australia in ODI"
cricket_art["body"] = "<p>Virat Kohli scored a masterful century.</p>"
res8 = ovp.official_video_for_article(cricket_art, search_fn=fake_search8,
                                      channels=CHANNELS)
check("8 no_channel status", res8["status"], "no_channel")
check("8 no search executed", searched8, [])

print()
if FAILURES:
    print(f"FAILURES ({len(FAILURES)}): {FAILURES}")
    sys.exit(1)
print("ALL PASS")
