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

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
