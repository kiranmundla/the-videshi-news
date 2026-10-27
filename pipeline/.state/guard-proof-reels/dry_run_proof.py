#!/usr/bin/env python3
"""
dry_run_proof.py — 2026-10-27 proof for the reel-sourcer
identity gates. NO rendering, NO publishing: it fetches the
REAL Commons metadata for the exact files the 2026-10-26
pulse run accepted, and runs them through the patched
evaluate_commons_page with the story context built from the
failed runs' own article.json + script.json. It also runs
source_extras end-to-end on the PERM story with downloads
into this scratch dir, to show the namesakes never reach
the extras list. Run from pipeline/:
  python3 -u .state/guard-proof-reels/dry_run_proof.py
"""
import json
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PIPE))
import reel_entity_sourcing as S

OUT = Path(__file__).resolve().parent
lines = []


def say(msg=""):
    print(msg)
    lines.append(msg)


def load_run(slug):
    d = PIPE / "reel-runs" / slug
    article = json.loads((d / "article.json").read_text())
    script = json.loads((d / "script.json").read_text())
    entities = S.extract_entities(article, script)
    return article, script, entities, \
        S.build_story_context(article, script, entities)


def judge(ctx, entity, title):
    page = S.commons_file_info(title)
    if not page:
        say(f"  !! could not fetch {title}")
        return
    cand, row = S.evaluate_commons_page(
        page, entity, "DRY-RUN — real Commons metadata",
        context=ctx)
    verdict = "ACCEPTED" if cand else "rejected"
    say(f"  [{verdict}] entity={entity!r} :: {title}")
    say(f"      reason: {row['reason']}")


PERM = "2026-10-26-perm-green-card-overhaul-clears-white-house-review"
DRISH = "2026-10-26-drishyam-3-franchise-crosses-1000-crore-worldwide"

say("=" * 72)
say("PERM story (US immigration; PERM = the DOL programme)")
pa, ps, pe, pctx = load_run(PERM)
say(f"entities: {pe}")
say(f"story countries: {sorted(pctx['countries'])}")
say("-- the namesakes the 2026-10-26 run ACCEPTED (v1 + v2):")
judge(pctx, "PERM",
      "File:Perm. Kama River. Kommunalny Bridge "
      "P6232022 2575.jpg")
judge(pctx, "PERM",
      "File:Perm. Kama River. Passenger river ship "
      "Moskva-210 P6242370 2575.jpg")
judge(pctx, "White House",
      "File:Russian White House and ships on Moskva River.jpg")
say("-- the same run's GOOD accepts (must stay accepted):")
judge(pctx, "Department of Labor",
      "File:Frances Perkins Building of the United States "
      "Department of Labor in Washington, D.C. - 1.jpg")
judge(pctx, "Keith Sonderling",
      "File:Keith Sonderling (55510883049).jpg")

say()
say("=" * 72)
say("Drishyam 3 story (box office)")
da, ds, de, dctx = load_run(DRISH)
say(f"entities: {de}")
say(f"story countries: {sorted(dctx['countries'])}")
say("-- the namesake the run ACCEPTED as hero + grid:")
judge(dctx, "Times of India",
      'File:Jug Suraiya, Indian journalist, formerly with '
      'the "Junior Statesmen" and then "Times of India" 02.jpg')
judge(dctx, "India",
      'File:Jug Suraiya, Indian journalist, formerly with '
      'the "Junior Statesmen" and then "Times of India" 02.jpg')
say("-- the run's GOOD accept (must stay accepted):")
judge(dctx, "Ajay Devgn", "File:Ajay Devgn .jpg")

say()
say("=" * 72)
say("source_extras end-to-end on the PERM story (real "
    "Commons searches; downloads land in this scratch dir)")
prov = S.source_extras(pa, ps, OUT / "supp-perm", own_count=1,
                       log=lambda *a: None)
say(f"extras: {[(e['beat'], e['label']) for e in prov['extras']]}")
bad = [e for e in prov["extras"]
       if "perm" in e["label"].lower()
       and "perkins" not in e["label"].lower()]
say(f"Perm-Russia extras present: {bool(bad)}")
for r in prov["candidate_ledger"]:
    if "namesake" in r.get("reason", "") or \
            "russia" in r.get("reason", "").lower():
        say(f"  ledger namesake rejection: {r['candidate']} "
            f"— {r['reason'][:150]}")

(OUT / "dry-run-output.txt").write_text("\n".join(lines) + "\n")
say()
say("saved: .state/guard-proof-reels/dry-run-output.txt")
