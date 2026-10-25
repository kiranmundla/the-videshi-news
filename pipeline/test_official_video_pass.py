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

# ── 11. team-match gate (approved 2026-10-24) ───────────────────────────
# The proven Oct 23 failures: rights-holder highlights titled
# '<Team> v <Team> | HIGHLIGHTS' died at the shared gate's
# entity-centred score / headline-overlap rules, and the India v NZ
# article's headline never literally names New Zealand (slug/body do).
SLUG_ART = dict(REAL_ART)
SLUG_ART["slug"] = ("india-eye-2-0-lead-second-t20i-new-zealand-"
                    "christchurch")
BODY_ART = dict(REAL_ART)
BODY_ART["body"] = ("<p>India face New Zealand in Christchurch as the "
                    "T20I cricket series continues.</p>")

check("11 fixture pair from headline stays the pair",
      ovp._fixture_teams(TEAM_ART)[:2], ["india", "new zealand"])
check("11 fixture pair completed from slug",
      ovp._fixture_teams(SLUG_ART)[:2], ["india", "new zealand"])
check("11 fixture pair completed from body",
      ovp._fixture_teams(BODY_ART)[:2], ["india", "new zealand"])
check("11 no second team anywhere -> single team only",
      ovp._fixture_teams(REAL_ART), ["india"])

check("11 team-match true (slug case)",
      ovp._team_match(SLUG_ART, NZ_VIDEO["title"]), True)
check("11 team-match true (body case)",
      ovp._team_match(BODY_ART, NZ_VIDEO["title"]), True)
check("11 team-match false: wrong opponent",
      ovp._team_match(SLUG_ART, "India v Australia | HIGHLIGHTS"), False)
check("11 team-match false: only one team in title",
      ovp._team_match(SLUG_ART, "New Zealand | HIGHLIGHTS | Christchurch"),
      False)
check("11 team-match false: no format word",
      ovp._team_match(SLUG_ART, "New Zealand v India | Christchurch"),
      False)
check("11 team-match false: 'india' as substring of 'indian'",
      ovp._team_match(SLUG_ART, "Indian v New Zealand | HIGHLIGHTS"),
      False)

_ok, _reason, _score = ovp.gate_candidate(
    SLUG_ART, NZC, NZ_VIDEO, ovp.headline_people(SLUG_ART["headline"]))
check("11 gate accepts slug case via team-match", _ok, True)
check("11 gate reason names team-match", "team-match" in _reason, True)
_ok2, _reason2, _ = ovp.gate_candidate(
    REAL_ART, NZC, NZ_VIDEO, ovp.headline_people(REAL_ART["headline"]))
check("11 gate still rejects when no second team exists", _ok2, False)


def fake_search_nz(entry, query, art):
    return [NZ_VIDEO]


res_slug = ovp.official_video_for_article(SLUG_ART,
                                          search_fn=fake_search_nz,
                                          channels=[NZC])
check("11 end-to-end accepted (slug case)", res_slug["status"], "accepted")
res_body = ovp.official_video_for_article(BODY_ART,
                                          search_fn=fake_search_nz,
                                          channels=[NZC])
check("11 end-to-end accepted (body case)", res_body["status"], "accepted")

WRONG_OPP = dict(NZ_VIDEO)
WRONG_OPP["videoId"] = "WrongOpp2026"
WRONG_OPP["title"] = "Australia v England | HIGHLIGHTS | 2nd T20I"


def fake_search_wrong_opp(entry, query, art):
    return [WRONG_OPP]


res_wo = ovp.official_video_for_article(SLUG_ART,
                                        search_fn=fake_search_wrong_opp,
                                        channels=[NZC])
check("11 end-to-end rejected: neither fixture team pairing",
      res_wo["status"], "rejected")

NOFMT = dict(NZ_VIDEO)
NOFMT["videoId"] = "NoFormat2026"
NOFMT["title"] = "New Zealand v India | Christchurch"


def fake_search_nofmt(entry, query, art):
    return [NOFMT]


res_nf = ovp.official_video_for_article(SLUG_ART,
                                        search_fn=fake_search_nofmt,
                                        channels=[NZC])
check("11 end-to-end rejected: teams but no format word",
      res_nf["status"], "rejected")

# Sri Lanka v England shape + pirate-bait must still die in team branch
SLC = {"name": "Sri Lanka Cricket", "channel_id": "UCslc000000001",
       "domain": "cricket", "categories": ["sports"],
       "match_terms": ["cricket"], "x_handle": None}
SL_ART = {"id": "test-sl", "slug": "sri-lanka-beat-england-t20i-thriller",
          "headline": "Sri Lanka Beat England in T20I Thriller to Level Series",
          "category": "sports",
          "body": "<p>Sri Lanka beat England in a T20I cricket thriller.</p>",
          "published_at": "2026-10-23T00:00:00Z"}
SL_VIDEO = {"videoId": "SlV1deo2026",
            "title": "Sri Lanka v England | HIGHLIGHTS | 2nd T20I",
            "channelTitle": "Sri Lanka Cricket",
            "channelId": "UCslc000000001",
            "publishedAt": "2026-10-22T10:00:00Z"}


def fake_search_sl(entry, query, art):
    return [SL_VIDEO]


res_sl = ovp.official_video_for_article(SL_ART, search_fn=fake_search_sl,
                                        channels=[SLC])
check("11 Sri Lanka v England highlight accepted",
      res_sl["status"], "accepted")

SL_PIRATE = dict(SL_VIDEO)
SL_PIRATE["videoId"] = "SlP1rate2026"
SL_PIRATE["title"] = ("Sri Lanka v England | HIGHLIGHTS | watch online "
                      "free download")


def fake_search_sl_pirate(entry, query, art):
    return [SL_PIRATE]


res_slp = ovp.official_video_for_article(SL_ART,
                                         search_fn=fake_search_sl_pirate,
                                         channels=[SLC])
check("11 pirate-bait still rejected in team branch",
      res_slp["status"], "rejected")
check("11 pirate-bait reason survives",
      "pirate-bait" in res_slp["decisions"][0]["reason"], True)

# ── 12. daily search budget ledger (2026-10-24) ─────────────────────────
import json as _json
import tempfile

_budget_file = os.path.join(tempfile.mkdtemp(), "budget.json")
_orig_budget_path = ovp.SEARCH_BUDGET_PATH
_orig_budget_cap = ovp.DAILY_SEARCH_BUDGET
_orig_search = ovp.search_channel_videos
_orig_region = ovp.fetch_region_restriction
ovp.fetch_region_restriction = lambda token, vid: {}
ovp.SEARCH_BUDGET_PATH = _budget_file
ovp.DAILY_SEARCH_BUDGET = 3
check("12 consume 1-3 within cap",
      [ovp._consume_search_budget() for _ in range(3)],
      [True, True, True])
check("12 fourth consume denied", ovp._consume_search_budget(), False)
with open(_budget_file) as f:
    _state = _json.load(f)
check("12 ledger records date + count",
      (_state["date"], _state["searches"]),
      (ovp._pacific_today(), 3))

with open(_budget_file, "w") as f:
    _json.dump({"date": "1999-01-01", "searches": 99}, f)
check("12 stale date rolls over", ovp._consume_search_budget(), True)
with open(_budget_file) as f:
    _state = _json.load(f)
check("12 rollover resets count", _state["searches"], 1)

with open(_budget_file, "w") as f:
    f.write("not json {")
check("12 corrupt ledger fails closed", ovp._consume_search_budget(), False)

# Live path: budget spent -> no API call, decision names the budget
live_calls = []


def fake_api_search(token, channel_id, query, **_kw):
    live_calls.append(query)
    return [NZ_VIDEO]


ovp.search_channel_videos = fake_api_search
with open(_budget_file, "w") as f:
    _json.dump({"date": ovp._pacific_today(), "searches": 3}, f)
res_b0 = ovp.official_video_for_article(TEAM_ART, token="fake-token",
                                        channels=[NZC])
check("12 spent budget makes no API call", live_calls, [])
check("12 spent budget decision is named",
      any("budget exhausted" in (d.get("reason") or "")
          for d in res_b0["decisions"]), True)

with open(_budget_file, "w") as f:
    _json.dump({"date": ovp._pacific_today(), "searches": 2}, f)
res_b1 = ovp.official_video_for_article(TEAM_ART, token="fake-token",
                                        channels=[NZC])
check("12 one budget unit lets the live search run",
      res_b1["status"], "accepted")
check("12 live search consumed the unit", len(live_calls) >= 1, True)
ovp.search_channel_videos = _orig_search
ovp.fetch_region_restriction = _orig_region
ovp.SEARCH_BUDGET_PATH = _orig_budget_path
ovp.DAILY_SEARCH_BUDGET = _orig_budget_cap

# ── 13. region layer: US audience playability ────────────────────────────
check("13 allowed PK-only is not US-playable",
      ovp.region_allows_us({"allowed": ["PK"]}), False)
check("13 allowed incl US is US-playable",
      ovp.region_allows_us({"allowed": ["US", "PK"]}), True)
check("13 blocked IN only is US-playable",
      ovp.region_allows_us({"blocked": ["IN"]}), True)
check("13 blocked US is not US-playable",
      ovp.region_allows_us({"blocked": ["US"]}), False)
check("13 no restriction is US-playable",
      ovp.region_allows_us({}), True)

res_pk = ovp.official_video_for_article(
    ART, search_fn=fake_search_ok, channels=CHANNELS,
    region_fn=lambda vid: {"allowed": ["PK"]})
check("13 PK-only candidate rejected end-to-end",
      res_pk["status"], "rejected")
check("13 PK-only rejection names the region",
      any("region-blocked for US" in (d.get("reason") or "")
          for d in res_pk["decisions"]), True)

res_in = ovp.official_video_for_article(
    ART, search_fn=fake_search_ok, channels=CHANNELS,
    region_fn=lambda vid: {"blocked": ["IN"]})
check("13 IN-blocked candidate still accepted",
      res_in["status"], "accepted")

res_unknown = ovp.official_video_for_article(
    ART, search_fn=fake_search_ok, channels=CHANNELS,
    region_fn=lambda vid: None)
check("13 unverifiable region fails closed",
      res_unknown["status"], "rejected")

print()
if FAILURES:
    print(f"FAILURES ({len(FAILURES)}): {FAILURES}")
    sys.exit(1)
print("ALL PASS")
