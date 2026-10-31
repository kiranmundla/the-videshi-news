#!/usr/bin/env python3
"""Tests for the shadow hero path (verified_sourcer) and the
failure-corpus replay (corpus_replay) — image rebuild §3
evaluation protocol.

A. verified_sourcer.decide with stub resolvers (offline): P18
   pass, width exception band, hard floor, logo fall-through to
   depicts, blocklist filtering inside depicts, and fail-closed
   outcomes.
B. decide with the REAL registry-only resolver (offline):
   ambiguous namesake abstention, language non-visual, no-QID
   anchor, the blocked namesake file never served.
C. Corpus replay over the real 123-case corpus (offline,
   deterministic): totals, the design §3 ship bar (>=95% of
   replayable wrongs rejected), and the specific evidentiary
   cases the registry was seeded from. A failure here is the
   regression signal the suite exists for — re-review the case,
   don't tune the assertion.

Run: python3 -u test_corpus_replay.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import corpus_replay as cr
import entity_resolve as er
import verified_sourcer as vs

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _res(name="Example Person", qid="Q123", p18="Example Person 2024.jpg",
         width=2400, etype="person", blocked=None, conf=None,
         method="registry", confidence="high", notes=""):
    return {"query": name, "name": name, "qid": qid,
            "p18_file": p18, "p18_quality": width, "type": etype,
            "method": method, "confidence": confidence,
            "confusables": conf or [], "blocked_files": blocked or [],
            "notes": notes}


def _depicts(cands):
    return lambda qid: cands


NO_DEPICTS = lambda qid: []  # noqa: E731

# ── A. decide() with stubs ──────────────────────────────────────
print("A. verified_sourcer.decide (stubbed)")
tmp = tempfile.mkdtemp()
shadow = os.path.join(tmp, "shadow.jsonl")
art = {"slug": "example-slug", "headline": "Example Person wins award",
       "image_entities": ["Example Person"], "body": "<p>Story.</p>"}

r = vs.decide(art, resolver=lambda n, c: _res(),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("P18 pass -> image/wikidata_p18",
      r["decision"] == "image" and r["route"] == "wikidata_p18")
check("P18 url is the Commons file path",
      "Special:FilePath/Example_Person_2024.jpg" in (r["url"] or ""))
lines = open(shadow).read().strip().splitlines()
rec = json.loads(lines[-1])
check("shadow line written with slug/decision/route",
      rec["slug"] == "example-slug" and rec["decision"] == "image"
      and rec["route"] == "wikidata_p18"
      and rec["file_key"] == "example person 2024.jpg")

r = vs.decide(art, resolver=lambda n, c: _res(width=900),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("width 900 -> image with documented-exception reason",
      r["decision"] == "image" and "documented" in r["reason"])

r = vs.decide(art, resolver=lambda n, c: _res(width=500),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("width 500 + no depicts -> none (hard floor)",
      r["decision"] == "none")

r = vs.decide(art, resolver=lambda n, c: _res(p18="Example Corp logo.png",
                                              width=3000),
              depicts_fn=_depicts([{"title": "File:Example Corp HQ.jpg",
                                    "file_key": "example corp hq.jpg",
                                    "url": "https://upload.wikimedia.org/hq.jpg",
                                    "width": 2000, "height": 1200,
                                    "license": "CC BY-SA 4.0"}]),
              info_fn=None, log_path=shadow)
check("logo P18 -> falls through to depicts",
      r["decision"] == "image" and r["route"] == "wikidata_depicts")

r = vs.decide(art, resolver=lambda n, c: _res(p18="",
                                              blocked=["Bad File.jpg"]),
              depicts_fn=_depicts([
                  {"title": "File:Bad File.jpg",
                   "file_key": "bad file.jpg",
                   "url": "https://upload.wikimedia.org/bad.jpg",
                   "width": 3000, "height": 2000, "license": "CC BY 4.0"},
                  {"title": "File:Good File.jpg",
                   "file_key": "good file.jpg",
                   "url": "https://upload.wikimedia.org/good.jpg",
                   "width": 1600, "height": 900, "license": "CC BY 4.0"}]),
              info_fn=None, log_path=shadow)
check("blocked depicts candidate skipped, next wins",
      r["decision"] == "image" and r["file_key"] == "good file.jpg")

r = vs.decide(art, resolver=lambda n, c: _res(
                  p18="Bad File.jpg", blocked=["Bad File.jpg"]),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("blocked P18 + no depicts -> none",
      r["decision"] == "none")

r = vs.decide({"slug": "s", "headline": "Nothing here"}, log_path=shadow)
check("no subjects -> none", r["decision"] == "none")

# ── B. decide() with the real registry-only resolver ────────────
print("B. verified_sourcer.decide (registry-only, offline)")
reg_kw = {"resolver": vs.registry_only_resolve,
          "depicts_fn": NO_DEPICTS, "info_fn": None,
          "log_path": shadow}

r = vs.decide({"slug": "mandeep", "headline": "Mandeep Singh shines",
               "image_entities": ["Mandeep Singh"], "body": ""}, **reg_kw)
check("ambiguous namesake, no discriminating context -> none/abstain",
      r["decision"] == "none" and "ambiguous" in r["reason"])

r = vs.decide({"slug": "mandeep-hockey",
               "headline": "Mandeep Singh scores in field hockey "
                           "Pro League win",
               "image_entities": ["Mandeep Singh"], "body": ""}, **reg_kw)
check("hockey context resolves the hockey player; his 145px P18 "
      "fails the floor -> none (fail closed)",
      r["decision"] == "none"
      and any(a.get("entity") == "Mandeep Singh (field hockey)"
              and a.get("route") == "wikidata_p18"
              and not a.get("ok") for a in r["attempts"]))

r = vs.decide({"slug": "hindi", "headline": "Jailer 2 Hindi version",
               "image_entities": ["Hindi"], "body": ""}, **reg_kw)
check("language subject -> none (non-visual)",
      r["decision"] == "none"
      and any(a.get("outcome") == "non-visual" for a in r["attempts"]))

r = vs.decide({"slug": "ott", "headline": "OTT platforms merge",
               "image_entities": ["OTT"], "body": ""}, **reg_kw)
check("no-QID subject -> none (no identity anchor)",
      r["decision"] == "none"
      and any(a.get("outcome") == "no-qid" for a in r["attempts"]))

shadab_depicts = _depicts([
    {"title": "File:Shadab Khan at photo shoot.jpg",
     "file_key": "shadab khan at photo shoot.jpg",
     "url": "https://upload.wikimedia.org/actor.jpg",
     "width": 3000, "height": 2000, "license": "CC BY-SA 3.0"},
    {"title": "File:Shadab Khan bowling 2023.jpg",
     "file_key": "shadab khan bowling 2023.jpg",
     "url": "https://upload.wikimedia.org/bowling.jpg",
     "width": 1800, "height": 1200, "license": "CC BY 4.0"}])
r = vs.decide({"slug": "shadab",
               "headline": "Shadab Khan century seals Pakistan win",
               "image_entities": ["Shadab Khan"], "body": ""},
              resolver=vs.registry_only_resolve,
              depicts_fn=shadab_depicts, info_fn=None,
              log_path=shadow)
check("cricketer resolved by context; blocked actor file in "
      "depicts is rejected, genuine candidate served",
      r["decision"] == "image"
      and r["file_key"] == "shadab khan bowling 2023.jpg")

# ── C. corpus replay ────────────────────────────────────────────
print("C. corpus replay (123 cases, offline)")
with open(cr.DEFAULT_CORPUS) as f:
    corpus = json.load(f)
reg = er.load_registry()
results = cr.replay(corpus, reg)
summary = cr.summarize(results)
by_id = {r["id"]: r for r in results}

check("corpus has 123 incidents", summary["total"] == 123)
check("determinations sum to total",
      summary["rejected"] + summary["still_wrong"]
      + summary["not_replayable"] == 123)
check("ship bar: >=95% of replayable wrongs rejected",
      summary["rejected_pct_of_replayable"] >= 95.0,
      f"got {summary['rejected_pct_of_replayable']}")
check("no still-wrong cases in the current replay",
      summary["still_wrong_ids"] == [],
      f"got {summary['still_wrong_ids']}")

for cid, mech in [(35, "corpus-blocklist"), (38, "corpus-blocklist"),
                  (100, "corpus-blocklist"),
                  (113, "non-visual-entity"),
                  (114, "non-visual-entity"),
                  (21, "confusable-adjudication"),
                  (77, "confusable-adjudication"),
                  (108, "confusable-adjudication")]:
    check(f"#{cid} rejected via {mech}",
          by_id[cid]["determination"] == "rejected"
          and by_id[cid]["mechanism"] == mech,
          f"got {by_id[cid]['determination']}/{by_id[cid]['mechanism']}")

# #27/#123 were "honestly not replayable" ONLY because the bank
# was unregistered and the sibling (Maurya) felicitation file is
# unblocked. The corpus-replay-live curation list directed
# registering Indian Overseas Bank (Q2003611), with the explicit
# note that doing so changes these cases' premise — they are
# replayable now, and the wrong files (open-route products, not
# in {P18} ∪ depicts(Q2003611)) are rejected. The person-entry
# blocklist discipline is unchanged (#100 still pins it).
check("#27 replayable after IOB curation: rejected, bank "
      "adjudicated, depicts recall plausible",
      by_id[27]["determination"] == "rejected"
      and by_id[27]["mechanism"] == "route-abolition"
      and by_id[27]["intended_entities"] == ["Indian Overseas Bank"]
      and by_id[27]["recall"] == "found_depicts_plausible",
      f"got {by_id[27]}")
check("#123 replayable after IOB curation: rejected",
      by_id[123]["determination"] == "rejected"
      and by_id[123]["intended_entities"] == ["Indian Overseas Bank"],
      f"got {by_id[123]}")
# #30 (and its twin #29): registering Diwali (curation list)
# changed the replay's READING, not the outcome. The descriptor
# 'Diwali 2026 in the UAE' now text-matches the curated festival
# entry, so the replay adjudicates Diwali as the story entity
# and the Patan photo is rejected via the inline route-abolition
# branch before confusable adjudication is reached (the live
# path's subject is the extractor's/intent's, not the replay's
# text match). What must not regress: the wrong file is still
# positively identified as the Patan temple's own P18, the
# determination is still rejected, and the Bur Dubai temple's
# data gap is still real — asserted at the registry level,
# where it does not depend on text matching.
check("#30 still rejected; wrong file still identified as the "
      "Patan temple P18",
      by_id[30]["determination"] == "rejected"
      and by_id[30]["wrong_file_key"]
      == er.file_key("Lalitpur Patan Durbar Square 2023 02.jpg"),
      f"got {by_id[30]['determination']}/{by_id[30]['wrong_file_key']}")
_bur_dubai = next(e for e in reg["entities"]
                  if e["name"] == "Krishna Mandir, Bur Dubai")
check("#30 data gap persists in the registry itself (Bur Dubai "
      "temple: no QID, no P18)",
      _bur_dubai["wikidata_qid"] is None
      and _bur_dubai["p18_file"] is None)
check("#19 recall: Infosys campus P18 found",
      by_id[19]["recall"] == "found_p18")
check("#26 recall: the swapped-in TCS SIPCOT file IS the "
      "registry P18",
      by_id[26]["recall"] == "found_p18"
      and by_id[26]["recall_entity"] == "Tata Consultancy Services")
# #30's recall is deliberately NOT pinned anymore: with Diwali
# curated, the replay credits the festival's P18 for the
# descriptor 'Diwali 2026 in the UAE' — a plausible image for a
# Diwali guide, but not the temple photo the corpus asked for.
# The temple gap itself is pinned at the registry level above,
# where text matching cannot mask it.
expl_ids = {r["id"] for r in results if r["explicit_correct_existed"]}
check("explicit correct-existed set is {18,19,26,27,50,88}",
      expl_ids == {18, 19, 26, 27, 50, 88}, f"got {sorted(expl_ids)}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED (offline set)")
