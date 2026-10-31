#!/usr/bin/env python3
"""Tests for verified_sourcer's live-replay logic guards and the
shadow inline path (inline_decide) — image rebuild, 2026-10-31.

A. Guards added after the LIVE corpus replay exposed them
   (corpus-replay-live.json): fed the real articles of the 25
   offline-not-replayable incidents, the unguarded path resolved
   headline common nouns to confident wrong identities
   ('Ordering' → partial order, 'Profit' → income tax, 'SEBI'
   → Serbia, 'Yulu' → fish sauce) and accepted live winners
   that do not bear the queried name ('Adrian Abraham', a
   9-year-old guitarist, → Adrian Jacobs, a rugby player).
   _subject_eligible + identity_agrees are the fixes; these
   tests pin them.

B. inline_decide: subjects + named co-subjects only (fixed
   tagging via article_picture_pass.subject_and_cosubject_names),
   per-entity P18/depicts sourcing, canonical-key dedup against
   the hero, blocklist refusal, the 3-inline cap, and shadow
   records carrying surface="inline".

C. Venue identity (baps-acceptance.md case 1): an org-level
   identity must not present, unlabeled, as a venue-specific
   story's venue. Venue-specific = org (or has_local_instances)
   primary + a city co-subject / headline venue pattern. The
   BAPS/Dallas fixture serves its org depicts ONLY as a labeled
   file photo; a generic BAPS story serves unlabeled; a Toronto
   mandir file never serves unlabeled for a Dallas story; a
   venue-tied file serves unlabeled; no candidate at all is
   none/venue-unverified.

Run: python3 -u test_verified_sourcer.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verified_sourcer as vs

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _res(name, qid="Q1", p18="Photo.jpg", width=2400, etype="person",
         blocked=None, method="wikidata-sitelinks", confidence="high",
         notes=""):
    return {"query": name, "name": name, "qid": qid,
            "p18_file": p18, "p18_quality": width, "type": etype,
            "method": method, "confidence": confidence,
            "confusables": [], "blocked_files": blocked or [],
            "notes": notes}


NO_DEPICTS = lambda qid: []  # noqa: E731
tmp = tempfile.mkdtemp()
shadow = os.path.join(tmp, "shadow.jsonl")

# ── A. identity agreement + subject eligibility ────────────────
print("A. live-replay guards")
check("identity_agrees: exact label",
      vs.identity_agrees("Nashik", _res("Nashik")))
check("identity_agrees: plural-insensitive",
      vs.identity_agrees("Indian-American", _res("Indian Americans")))
check("identity_agrees: type-word suffix allowed",
      vs.identity_agrees("Republican", _res("Republican Party")))
check("identity_agrees: honorific prefix allowed",
      vs.identity_agrees("Justice Vikram Nath", _res("Vikram Nath")))
check("identity_agrees: different person rejected",
      not vs.identity_agrees("Adrian Abraham", _res("Adrian Jacobs")))
check("identity_agrees: SEBI is not Serbia",
      not vs.identity_agrees("SEBI", _res("Serbia")))
check("identity_agrees: word is not a concept",
      not vs.identity_agrees("Yulu", _res("fish sauce")))
check("identity_agrees: surname-only is not a full name",
      not vs.identity_agrees("Trump", _res("Donald Trump")))
check("identity_agrees: registry resolutions exempt (curated "
      "alias)", vs.identity_agrees(
          "Nifty", _res("NIFTY 50", method="registry")))

sebi_art = {"slug": "sebi", "headline": "SEBI Moves on KYC",
            "image_entities": ["SEBI"], "body": "<p>Story.</p>"}
r = vs.decide(sebi_art,
              resolver=lambda n, c: _res("Serbia", qid="Q403",
                                         p18=None),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: name-mismatched live winner treated as unresolved",
      r["decision"] == "none"
      and any(a.get("outcome") == "name-mismatch"
              for a in r["attempts"]))

r = vs.decide({"slug": "nath", "headline": "Justice Vikram Nath "
                                           "speaks",
               "image_entities": ["Justice Vikram Nath"],
               "body": "<p>Story.</p>"},
              resolver=lambda n, c: _res("Vikram Nath"),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: honorific-bearing live winner served",
      r["decision"] == "image")

calls = []


def _tracking_resolver(n, c):
    calls.append(n)
    return _res(n)


ord_art = {"slug": "ord",
           "headline": "Ordering Goes Digital for Delhi "
                       "Restaurants",
           "body": ("<p>Ordering has moved online across the "
                    "capital.</p><p>Digital Ordering grew sharply "
                    "this year, and Ordering volumes doubled for "
                    "small restaurants.</p>"),
           "image_entities": None}
r = vs.decide(ord_art, resolver=_tracking_resolver,
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: headline common noun is never resolved as a "
      "subject", r["decision"] == "none" and calls == [],
      f"resolver calls: {calls}")

tv_art = {"slug": "tv", "headline": "Testville Fair Draws "
                                   "Record Crowds",
          "body": ("<p>Testville welcomed thousands of visitors "
                   "on Saturday.</p><p>Testville officials said "
                   "the fair was the largest in a decade.</p>"),
          "image_entities": None}
r = vs.decide(tv_art, resolver=_tracking_resolver,
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: unregistered single-token subject never sourced",
      r["decision"] == "none" and calls == [],
      f"resolver calls: {calls}")

# ── B. inline_decide ───────────────────────────────────────────
print("B. inline_decide (shadow)")
CHESS = {
    "slug": "fixture-chess",
    "headline": "Meera Krishnan Wins National Chess Title in "
                "Chennai",
    "body": ("<p>Meera Krishnan won the national chess title in "
             "Chennai on Sunday, defeating defending champion "
             "Divya Deshmukh in a tense final round.</p>"
             "<p>Divya Deshmukh, the top seed, had led the "
             "standings until the penultimate round of the "
             "championship.</p>"
             "<p>The win makes Meera Krishnan the youngest "
             "champion in the history of the event.</p>"
             "<p>The ceremony drew a large crowd. Former world "
             "champion Viswanathan Anand attended as chief guest "
             "and presented the trophy. Viswanathan Anand praised "
             "the growing strength of Indian chess in his "
             "address.</p>"),
    "image_entities": None}

CHESS_RES = {
    "Meera Krishnan": _res("Meera Krishnan",
                           p18="Meera Krishnan playing chess.jpg",
                           width=2000),
    "Divya Deshmukh": _res("Divya Deshmukh",
                           p18="Divya Deshmukh 2024.jpg",
                           width=1800),
    "Viswanathan Anand": _res("Viswanathan Anand",
                              p18="Viswanathan Anand 2023.jpg",
                              width=2400),
}
inline_calls = []


def _chess_resolver(n, c):
    inline_calls.append(n)
    return CHESS_RES.get(n)


ishadow = os.path.join(tmp, "inline-shadow.jsonl")
r = vs.inline_decide(CHESS, resolver=_chess_resolver,
                     depicts_fn=NO_DEPICTS, info_fn=None,
                     log_path=ishadow)
placed_names = [p["entity"] for p in r["inlines"]]
check("co-subject from the lede is placed",
      placed_names == ["Divya Deshmukh"], f"got {placed_names}")
check("mentioned-only entity yields NO inline and is never "
      "resolved", "Viswanathan Anand" not in placed_names
      and "Viswanathan Anand" not in inline_calls,
      f"calls: {inline_calls}")
check("hero file key reported for dedup",
      r["hero_file_key"] == "meera krishnan playing chess.jpg")
check("subject's own hero file is deduped, not repeated inline",
      all(p["file_key"] != r["hero_file_key"] for p in r["inlines"])
      and any(a.get("outcome", "").startswith("duplicate of hero")
              for a in r["attempts"]))
lines = open(ishadow).read().strip().splitlines()
recs = [json.loads(x) for x in lines]
check("shadow records carry surface=inline",
      recs and all(x.get("surface") == "inline" for x in recs))
check("placed inline logged with its file key",
      any(x["file_key"] == "divya deshmukh 2024.jpg"
          and x["decision"] == "image" for x in recs))

# blocklisted file refused (P18 and depicts both blocked)
BLOCK_ART = {"slug": "block", "headline": "Example Org Opens HQ",
             "image_entities": ["Example Org"],
             "body": "<p>Story.</p>"}
blocked_depicts = lambda qid: [  # noqa: E731
    {"title": "File:Blocked Ceremony.jpg",
     "file_key": "blocked ceremony.jpg",
     "url": "https://upload.wikimedia.org/blocked.jpg",
     "width": 3000, "height": 2000, "license": "CC BY 4.0"}]
r = vs.inline_decide(
    BLOCK_ART,
    resolver=lambda n, c: _res("Example Org",
                               p18="Blocked Ceremony.jpg",
                               blocked=["Blocked Ceremony.jpg"]),
    depicts_fn=blocked_depicts, info_fn=None, log_path=ishadow)
check("blocklisted file refused as inline (P18 + depicts)",
      r["decision"] == "none" and r["inlines"] == [])

# cap: 5 curated subjects, hero takes the first, max 3 inlines
CAP_ART = {"slug": "cap", "headline": "Many Entities Story",
           "image_entities": ["Alpha One", "Beta Two", "Gamma "
                              "Three", "Delta Four", "Epsilon Five"],
           "body": "<p>Story.</p>"}
r = vs.inline_decide(
    CAP_ART,
    resolver=lambda n, c: _res(n, p18=f"{n} photo.jpg"),
    depicts_fn=NO_DEPICTS, info_fn=None, log_path=ishadow)
check("inline cap is 3 beyond the hero",
      len(r["inlines"]) == 3
      and r["hero_file_key"] == "alpha one photo.jpg"
      and any(a.get("outcome") == "skipped: inline cap"
              for a in r["attempts"]),
      f"got {len(r['inlines'])} inlines")

# hero decisions still log surface=hero
vs.decide(sebi_art, resolver=lambda n, c: _res("Serbia", p18=None),
          depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
hrec = json.loads(open(shadow).read().strip().splitlines()[-1])
check("hero shadow records carry surface=hero",
      hrec.get("surface") == "hero")

# ── C. venue identity ──────────────────────────────────────────
print("C. venue identity (org-level identity, venue story)")
BAPS_ART = {
    "slug": "baps-dallas",
    "headline": "Dallas BAPS Mandir Expects 12,000 for Diwali "
                "Annakut and Fireworks on November 10",
    "image_entities": ["BAPS", "Dallas"],
    "body": ("<p>The BAPS Shri Swaminarayan Mandir in Irving "
             "hosts its Diwali celebration on Tuesday.</p>"),
}
BAPS_RES = _res("BAPS", qid="Q4936220", p18=None, width=None,
                etype="org")
BAPS_RES["has_local_instances"] = True
DALLAS_RES = _res("Dallas", qid="Q16558", p18=None, width=None,
                  etype="place")
VENUE_RES = {"BAPS": BAPS_RES, "Dallas": DALLAS_RES}
venue_resolver = lambda n, c: VENUE_RES.get(n)  # noqa: E731

AKSHAR_DEPICTS = lambda qid: [{  # noqa: E731
    "title": "File:Akshar_pursotam.jpg",
    "file_key": "akshar pursotam.jpg",
    "url": "https://upload.wikimedia.org/akshar.jpg",
    "width": 3000, "height": 2000, "license": "CC BY-SA 4.0"}]
# the acceptance case's actual evidence: an unidentified BAPS
# mandir's shrine — description/categories name NO location
AKSHAR_EVIDENCE = lambda ref: {  # noqa: E731
    "description": "Humanity Goal of entire life",
    "categories": ["Hindu saints", "Self-published work"],
    "depicts_qids": ["Q4936220"]}

r = vs.decide(BAPS_ART, resolver=venue_resolver,
              depicts_fn=AKSHAR_DEPICTS, info_fn=None,
              evidence_fn=AKSHAR_EVIDENCE, log_path=shadow)
check("BAPS/Dallas: org-level depicts serves ONLY as a labeled "
      "file photo", r["decision"] == "image"
      and r["route"] == "wikidata_depicts"
      and r["label"] == "file_photo",
      f"got {r['decision']}/{r['route']}/{r['label']}")
check("BAPS/Dallas: label_text names the org generically",
      r["label_text"] == "File photo: a BAPS mandir",
      f"got {r['label_text']!r}")
check("BAPS/Dallas: caption does not claim the story's venue",
      bool(r["caption"]) and "not the Dallas venue" in r["caption"]
      and "Irving" not in r["caption"],
      f"got {r['caption']!r}")
rec = json.loads(open(shadow).read().strip().splitlines()[-1])
check("BAPS/Dallas: shadow record carries the label fields",
      rec.get("label") == "file_photo"
      and rec.get("label_text") == "File photo: a BAPS mandir")

BAPS_GENERIC = {
    "slug": "baps-generic",
    "headline": "BAPS Charities Launches Nationwide Food Drive",
    "image_entities": ["BAPS"],
    "body": "<p>BAPS Charities announced the drive.</p>",
}
r = vs.decide(BAPS_GENERIC, resolver=venue_resolver,
              depicts_fn=AKSHAR_DEPICTS, info_fn=None,
              evidence_fn=AKSHAR_EVIDENCE, log_path=shadow)
check("generic BAPS org story (no city co-subject) still serves "
      "unlabeled", r["decision"] == "image" and r["label"] is None
      and r["label_text"] is None and r["caption"] is None)

TORONTO_DEPICTS = lambda qid: [{  # noqa: E731
    "title": "File:BAPS Shri Swaminarayan Mandir Toronto.jpg",
    "file_key": "baps shri swaminarayan mandir toronto.jpg",
    "url": "https://upload.wikimedia.org/toronto.jpg",
    "width": 2600, "height": 1800, "license": "CC BY-SA 4.0"}]
TORONTO_EVIDENCE = lambda ref: {  # noqa: E731
    "description": "BAPS Shri Swaminarayan Mandir in Toronto, "
                   "Ontario",
    "categories": ["BAPS Shri Swaminarayan Mandir, Toronto"],
    "depicts_qids": ["Q4936220", "Q4834612"]}
r = vs.decide(BAPS_ART, resolver=venue_resolver,
              depicts_fn=TORONTO_DEPICTS, info_fn=None,
              evidence_fn=TORONTO_EVIDENCE, log_path=shadow)
check("different-city venue file (Toronto mandir) never serves "
      "unlabeled for a Dallas story",
      r["decision"] == "image" and r["label"] == "file_photo",
      f"got label={r['label']!r}")

DALLAS_DEPICTS = lambda qid: [{  # noqa: E731
    "title": "File:Dallas BAPS Mandir Diwali.jpg",
    "file_key": "dallas baps mandir diwali.jpg",
    "url": "https://upload.wikimedia.org/dallas.jpg",
    "width": 2800, "height": 1900, "license": "CC BY-SA 4.0"}]
DALLAS_EVIDENCE = lambda ref: {  # noqa: E731
    "description": "Diwali annakut celebrations at the Dallas "
                   "BAPS mandir",
    "categories": ["BAPS temples in Texas"],
    "depicts_qids": ["Q4936220"]}
r = vs.decide(BAPS_ART, resolver=venue_resolver,
              depicts_fn=DALLAS_DEPICTS, info_fn=None,
              evidence_fn=DALLAS_EVIDENCE, log_path=shadow)
check("venue-tied file (its own record names Dallas) serves "
      "unlabeled", r["decision"] == "image" and r["label"] is None
      and "venue-tied" in r["reason"])

r = vs.decide(BAPS_ART, resolver=venue_resolver,
              depicts_fn=NO_DEPICTS, info_fn=None,
              evidence_fn=AKSHAR_EVIDENCE, log_path=shadow)
check("venue-specific story with no candidate at all -> "
      "none/venue-unverified",
      r["decision"] == "none"
      and r["reason"].startswith("venue-unverified"),
      f"got {r['decision']}/{r['reason'][:40]}")

BAPS_PATTERN_ART = {
    "slug": "baps-pattern",
    "headline": "Dallas BAPS Mandir Hosts Diwali Celebration",
    "image_entities": ["BAPS"],
    "body": "<p>The mandir hosts its Diwali celebration.</p>",
}
r = vs.decide(BAPS_PATTERN_ART,
              resolver=lambda n, c: BAPS_RES if n == "BAPS" else None,
              depicts_fn=AKSHAR_DEPICTS, info_fn=None,
              evidence_fn=AKSHAR_EVIDENCE, log_path=shadow)
check("headline pattern alone (<City> <Org> <venue>) triggers "
      "the venue rule", r["decision"] == "image"
      and r["label"] == "file_photo"
      and r["label_text"] == "File photo: a BAPS mandir",
      f"got {r['decision']}/{r['label']}/{r['label_text']!r}")

# the registry flag extends venue-capability beyond type "org";
# an unflagged company is NOT venue-capable
STORE_ART = {
    "slug": "megamart-dallas",
    "headline": "Dallas MegaMart Store Opens to Long Lines",
    "image_entities": ["MegaMart", "Dallas"],
    "body": "<p>Story.</p>",
}
MEGA_RES = _res("MegaMart", qid="Q777",
                p18="MegaMart Storefront.jpg", etype="company")


def _mega_resolver(flag):
    def r_(n, c):
        if n == "MegaMart":
            d = dict(MEGA_RES)
            d["has_local_instances"] = flag
            return d
        if n == "Dallas":
            return DALLAS_RES
        return None
    return r_


r = vs.decide(STORE_ART, resolver=_mega_resolver(False),
              depicts_fn=NO_DEPICTS, info_fn=None,
              evidence_fn=None, log_path=shadow)
check("company WITHOUT has_local_instances: city story "
      "unaffected (unlabeled)", r["decision"] == "image"
      and r["label"] is None)
r = vs.decide(STORE_ART, resolver=_mega_resolver(True),
              depicts_fn=NO_DEPICTS, info_fn=None,
              evidence_fn=lambda ref: {
                  "description": "A MegaMart storefront at dusk",
                  "categories": [], "depicts_qids": []},
              log_path=shadow)
check("company WITH has_local_instances: org P18 serves only "
      "as a labeled file photo", r["decision"] == "image"
      and r["label"] == "file_photo"
      and r["label_text"] == "File photo: a MegaMart store",
      f"got {r['label']}/{r['label_text']!r}")

# classification never writes the registry: with the default
# (caching) resolver, a registry place name classifies from the
# registry alone and the registry file is byte-identical after
import entity_resolve as _er  # noqa: E402

_reg_bytes_before = open(_er.REGISTRY_PATH, "rb").read()
_cls = vs._classify("Nashik", "", _er.resolve)
check("_classify: registry place classifies via the default "
      "resolver without touching the registry file",
      _cls is not None and _cls.get("type") == "place"
      and open(_er.REGISTRY_PATH, "rb").read() == _reg_bytes_before)
_cls2 = vs._classify("Dallas", "", venue_resolver)
check("_classify: non-default resolvers pass through",
      _cls2 is not None and _cls2.get("type") == "place")

# _all_candidates ordering agrees with candidates_for's winner
MIX_DEPICTS = lambda qid: [  # noqa: E731
    {"title": "File:Narrow Hall.jpg", "file_key": "narrow hall.jpg",
     "url": "https://upload.wikimedia.org/narrow.jpg",
     "width": 1600, "height": 900, "license": "CC BY 4.0"},
    {"title": "File:Wide Hall.jpg", "file_key": "wide hall.jpg",
     "url": "https://upload.wikimedia.org/wide.jpg",
     "width": 3000, "height": 2000, "license": "CC BY 4.0"}]
mix_res = _res("Mix Org", qid="Q9", p18="Mix Org logo.png",
               width=3000, etype="org")
one, _ = vs.candidates_for(mix_res, MIX_DEPICTS, None)
allc, _ = vs._all_candidates(mix_res, MIX_DEPICTS, None)
check("_all_candidates[0] is candidates_for's winner",
      one is not None and allc and one["file_key"]
      == allc[0]["file_key"] == "wide hall.jpg"
      and len(allc) == 2)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
