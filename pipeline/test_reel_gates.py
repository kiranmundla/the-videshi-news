#!/usr/bin/env python3
"""
test_reel_gates.py — unit tests for the Phase 1 reel pipeline gates.

Covers the failure classes the rebuild exists to kill:
  - fabricated QA (no hardcoded qa_passed / constant score anywhere),
  - unmeasured text (fit must raise, never crop silently),
  - thumbnail upscales (photo floor refuses small sources),
  - invented facts (fact-check gate holds wrong numbers/names/years
    and free-invented eyebrows — the D2 class),
  - carousel quote fabrication (verbatim-substring check).

Run: python3 -u test_reel_gates.py   (no network, no LLM, no ffmpeg)
"""
import json, re, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer
import reel_factcheck
import carousel_render

PASS = FAIL = 0


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name} {extra}")


ARTICLE = {
    "slug": "test-story",
    "headline": "Nine Indian-American Republicans Face H-1B Backlash",
    "subheadline": "Nine candidates contest the November 3 vote.",
    "category": "immigration",
    "body": ("<p>Nine Indian-American Republicans are running. The fee "
             "is $100,000 and fines reach $250,000. APS Fellowship "
             "nominees may not exceed one-half of 1% of members. "
             "Pei-Ling Chan Endowed Chair, University of Alabama in "
             "Huntsville, spoke. A factory reported 2 crore in sales "
             "and production down a quarter.</p>"),
    "sources": [],
}

GOOD_SCRIPT = {
    "hook_line": "H-1B CRACKDOWN HITS ELECTIONS",
    "news_summary": "Nine Indian-American Republicans are running.",
    "hook_stat": {"big": "$250,000", "sub": "fines on the table",
                  "eyebrow": "ELECTIONS 2026"},
    "stats": [{"big": "$100,000", "label": "The new H-1B fee"}],
    "diaspora_bullets": ["Check H-1B status with counsel"],
    "payoff": "Nine careers on the November 3 ballot.",
    "key_entities": ["H-1B"],
}
# NOTE: eyebrow ELECTIONS 2026 needs 2026 grounded — add it via body.
ARTICLE["body"] = ARTICLE["body"].replace(
    "the November 3 vote", "the November 3, 2026 vote")
ARTICLE["subheadline"] = "Nine candidates contest the November 3, 2026 vote."


def det(script, article=ARTICLE):
    return reel_factcheck.run_gate(script, article, use_llm=False)


print("── renderer: locked recipe")
check("saturation locked at 1.18 (not 1.25)",
      reel_renderer.ENH["saturation"] == 1.18)
check("safe zone right edge is the 930 rail limit",
      reel_renderer.PANEL_X1 == 930)
check("bottom safe limit is the raised 1580",
      reel_renderer.BOT_SAFE == 1580)
check("photo floor is 1080 wide", reel_renderer.MIN_PHOTO_W == 1080)

print("── renderer: measured text fit")
try:
    reel_renderer.fit_block("word " * 120, 800, 78, max_w=200,
                            max_lines=2)
    check("over-long text raises TextFitError", False)
except reel_renderer.TextFitError:
    check("over-long text raises TextFitError", True)
f, lines, sz = reel_renderer.fit_block(
    "A perfectly ordinary headline for a reel", 800, 78, max_lines=2)
check("ordinary text fits with real metrics",
      all(reel_renderer.text_width(f, ln) <= reel_renderer.TEXT_MAX_W
          for ln in lines))

print("── renderer: photo floor")
from PIL import Image
with tempfile.TemporaryDirectory() as td:
    small = Path(td) / "small.jpg"
    Image.new("RGB", (800, 600), (20, 20, 20)).save(small)
    music = Path(__file__).parent / "music" \
        / "anthemic-triumph-eternal-hope.mp3"
    try:
        reel_renderer.render_reel(GOOD_SCRIPT, small, music, td, "x",
                                  log=lambda *a: None)
        check("800px photo refused (PhotoTooSmallError)", False)
    except reel_renderer.PhotoTooSmallError:
        check("800px photo refused (PhotoTooSmallError)", True)

print("── fact-check: deterministic grounding")
rep = det(GOOD_SCRIPT)
check("honest script passes", rep["verdict"] == "pass",
      json.dumps(rep["held_claims"]))
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["hook_stat"]["big"] = "$999,999"
check("wrong number held", det(bad)["verdict"] == "fail")
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["hook_stat"]["big"] = "$250"
check("truncated amount $250 vs article $250,000 held",
      det(bad)["verdict"] == "fail")
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["news_summary"] = "Nine Indian-American Democrats are running."
check("wrong name held", det(bad)["verdict"] == "fail")
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["hook_stat"]["eyebrow"] = "ELECTIONS 2023"
check("ungrounded eyebrow year held", det(bad)["verdict"] == "fail")
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["hook_stat"]["eyebrow"] = "TOTALLY MADE UP"
check("free-invented eyebrow held", det(bad)["verdict"] == "fail")
bad = json.loads(json.dumps(GOOD_SCRIPT))
bad["stats"][0]["big"] = "2031"
check("wrong year held", det(bad)["verdict"] == "fail")

print("── fact-check: number normalization")
nums = reel_factcheck.article_number_set(ARTICLE["body"])
check("'one-half of 1%' grounds 0.5", 0.5 in nums)
check("spelled 'Nine' grounds 9", 9.0 in nums)
check("'2 crore' grounds 20000000", 20000000.0 in nums)
check("'down a quarter' grounds 25", 25.0 in nums)
check("comma number $250,000 grounds 250000", 250000.0 in nums)

print("── fact-check: entity extraction")
ents = reel_factcheck.extract_entities(
    "Pei-Ling Chan Endowed Chair, University of Alabama in Huntsville")
check("comma breaks entity runs (no merged mega-entity)",
      "Pei-Ling Chan Endowed Chair" in ents
      and not any("University" in e and "Chair" in e for e in ents),
      str(ents))
check("shout-case yields no entities",
      reel_factcheck.extract_entities("H-1B CRACKDOWN HITS ELECTIONS")
      == [])

print("── carousel: verbatim quote gate")
spec = {
    "eyebrow": "IMMIGRATION",
    "cover_headline": "Nine Indian-American Republicans Face H-1B Backlash",
    "quote": {"text": "This sentence was never said by anyone.",
              "speaker": "Pei-Ling Chan Endowed Chair",
              "role": "University of Alabama in Huntsville"},
    "facts": ["Fines reach $250,000"],
    "end": {"headline": "Nine Indian-American Republicans Face H-1B Backlash",
            "line": "Nine candidates contest the November 3, 2026 vote."},
}
rep, ok = carousel_render.carousel_factcheck(spec, ARTICLE,
                                             use_llm=False)
check("invented quote fails verbatim check",
      rep["verbatim_quote"] is False and ok is False)
spec["quote"]["text"] = ("Fellowship nominees are capped at half a "
                          "percent of the membership.")
# (a faithful paraphrase — but NOT verbatim, so it must still fail)
rep, ok = carousel_render.carousel_factcheck(spec, ARTICLE,
                                             use_llm=False)
check("paraphrase is not passed off as a verbatim quote",
      rep["verbatim_quote"] is False)

print("── carousel: quote-less spec (facts-led set; regression for the")
print("          2026-10-14 DHS run's KeyError 'quote' crash)")
spec_noq = {k: v for k, v in spec.items() if k != "quote"}
rep, ok = carousel_render.carousel_factcheck(spec_noq, ARTICLE,
                                             use_llm=False)
check("quote-less spec: no crash, quote checks not applicable",
      rep["quote_present"] is False and rep["verbatim_quote"] is None
      and rep["speaker_grounded"] is None
      and rep["role_grounded"] is None)
check("quote-less spec passes on grounded text", ok is True,
      str(rep.get("verdict")))
spec_null = dict(spec_noq, quote=None)
rep2, ok2 = carousel_render.carousel_factcheck(spec_null, ARTICLE,
                                               use_llm=False)
check("explicit quote=None handled like a missing quote",
      rep2["quote_present"] is False and ok2 is True)

print("── renderer: YuNet face detection (2026-10-14 building-FP")
print("          regression — Haar 'face' in a bank wall vent held a reel)")
import numpy as np
check("YuNet model vendored in the repo (survives VM rebuilds)",
      reel_renderer.YUNET_MODEL.exists())
check("YuNet detector available at runtime",
      reel_renderer.yunet_faces(np.zeros((64, 64, 3),
                                         dtype=np.uint8)) is not None)
BUILDING = Path(__file__).parent / "test-fixtures" \
    / "idbi-bank-building.jpg"
if not BUILDING.exists():  # fall back to the original run artifact
    BUILDING = (Path(__file__).parent / "reel-runs"
                / "2026-10-14-cabinet-approves-fairfax-52878-crore"
                  "-idbi-bank-stake-sale" / "output" / "hero.jpg")
if BUILDING.exists():
    bimg = Image.open(BUILDING).convert("RGB")
    check("YuNet: zero detections on the IDBI building photo",
          reel_renderer.yunet_faces(np.array(bimg)) == [])
    _, bmethod = reel_renderer.detect_face_box(bimg)
    check("building photo takes the no-face path (Haar FP designed out)",
          bmethod.startswith("focal-heuristic"), bmethod)
else:
    print("  (building fixture missing — FP regression checks skipped)")
CHAK = (Path(__file__).parent / "reel-samples" / "phase1"
        / "sukanya-chakrabarti-american-physical-society-fellow"
          "-dark-matter" / "output" / "hero.jpg")
if CHAK.exists():
    cimg = Image.open(CHAK).convert("RGB")
    cbox, cmethod = reel_renderer.detect_face_box(cimg)
    # The approved Haar-era render recorded box (770,260,352,352):
    # chin at 45.8% of the photo height. YuNet must still find the
    # face, with a chin consistent with that approved placement.
    chin_frac = (cbox[1] + cbox[3]) / cimg.height
    check("real face still detected (Chakrabarti sample)",
          cmethod.startswith("yunet"), cmethod)
    check("chin consistent with the approved render (±6% of height)",
          abs(chin_frac - 0.458) <= 0.06, f"chin={chin_frac:.3f}")

print("── no fabricated QA anywhere in the new modules")
import ast
for mod in ("reel_renderer.py", "reel_factcheck.py", "reel_frame_qa.py",
            "reel_produce.py", "carousel_render.py"):
    src = Path(__file__).parent.joinpath(mod).read_text()
    # Blank the module docstring's lines first: it legitimately QUOTES
    # the old system's fabrication while explaining why it was
    # designed out. Code and comments are still scanned.
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    if tree.body and isinstance(tree.body[0], ast.Expr) \
            and isinstance(tree.body[0].value, ast.Constant) \
            and isinstance(tree.body[0].value.value, str):
        for ln in range(tree.body[0].lineno - 1,
                        tree.body[0].end_lineno):
            lines[ln] = "\n"
    code = "".join(lines)
    bad = re.findall(r"qa_passed\s*=\s*True|qa_score\w*\s*=\s*\d+\b"
                     r"|qa_score_actual\s*=\s*\d+", code)
    check(f"{mod}: no hardcoded QA verdict/score", not bad, str(bad))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
