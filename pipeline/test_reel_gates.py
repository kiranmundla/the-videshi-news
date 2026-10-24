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

print("── renderer: heuristic anchor center-damping (2026-10-23 —")
print("          the Downing St door clipped by a lamp-arch focal guess)")
dx, dy = reel_renderer.damp_anchor(0.655, 0.087)
check("damp_anchor(0.655) -> 0.5775 (half the offset kept)",
      abs(dx - 0.5775) < 1e-9, f"{dx}")
check("damp_anchor(0.087) -> 0.2935", abs(dy - 0.2935) < 1e-9, f"{dy}")
check("center anchor is unmoved by damping",
      reel_renderer.damp_anchor(0.5, 0.5) == (0.5, 0.5))
import focal_point as _fp
_orig_focal = _fp.compute_focal_point
try:
    _fp.compute_focal_point = lambda _b: (0.9, 0.1)
    plain = Image.new("RGB", (1000, 800), (30, 30, 30))
    hbox, hmethod = reel_renderer.detect_face_box(plain)
finally:
    _fp.compute_focal_point = _orig_focal
check("heuristic path reports raw + damped anchors",
      "raw=(0.900,0.100)" in hmethod
      and "damped=(0.700,0.300)" in hmethod, hmethod)
check("heuristic box is built from the DAMPED anchor",
      abs((hbox[0] + hbox[2] / 2) / 1000 - 0.7) < 0.01,
      f"box={hbox}")
if CHAK.exists():
    cimg2 = Image.open(CHAK).convert("RGB")
    # Replicate detect_face_box's own geometry: it detects on the
    # ≤800px downscale and maps the box back by the same factor.
    import cv2 as _cv2
    _arr = np.array(cimg2)
    _h, _w = _arr.shape[:2]
    _s = 800 / max(_h, _w) if max(_h, _w) > 800 else 1.0
    if _s != 1.0:
        _arr = _cv2.resize(_arr, (int(_w * _s), int(_h * _s)))
    faces = reel_renderer.yunet_faces(_arr)
    if faces:
        _fx, _fy, _fw, _fh, _sc = max(faces,
                                      key=lambda f: f[2] * f[3])
        raw_box = tuple(int(round(v / _s))
                        for v in (_fx, _fy, _fw, _fh))
        fbox, fmethod = reel_renderer.detect_face_box(cimg2)
        check("face-detected box is EXACT (no damping on the face path)",
              fmethod.startswith("yunet") and "damped" not in fmethod
              and tuple(fbox) == raw_box,
              f"{fmethod} box={fbox} raw={raw_box}")

print("── fact-check: LLM verdict attribution (2026-10-24 — the drift")
print("          that held the Nasdaq payoff and the SpaceX sample:")
print("          judge verdicts mapped positionally shifted by one")
print("          field and left the last claims 'missing')")
SPX_ARTICLE = {
    "slug": "spx-test",
    "headline": "SpaceX Launches 27 Starlink Satellites From "
                "California",
    "subheadline": "",
    "body": ("<p>SpaceX launched 27 Starlink satellites from "
             "California on the fourth attempt after three scrubs. "
             "Booster B1063 completed its 36th flight. More than "
             "11,100 Starlink satellites are now in orbit, with "
             "service active in 174 markets. Starlink added 1.6 "
             "million customers in the third quarter. Each California "
             "launch adds capacity to the network. Falcon 9 remains "
             "the vehicle building out Starlink from California.</p>"),
    "sources": [],
}
SPX_SCRIPT = {
    "hook_line": "27 SATELLITES, FOURTH ATTEMPT",
    "news_summary": "SpaceX launched 27 Starlink satellites from "
                    "California on the fourth attempt.",
    "hook_stat": {"big": "27",
                  "sub": "Starlink satellites launched from "
                         "California on the fourth attempt",
                  "eyebrow": "BY THE NUMBERS"},
    "stats": [{"big": "36TH", "label": "Flight for booster B1063"},
              {"big": "11,100+",
               "label": "Starlink satellites now in orbit"},
              {"big": "174",
               "label": "Markets where Starlink service is active"}],
    "diaspora_bullets": [
        "Starlink added 1.6 million customers in the third quarter",
        "Each California launch adds capacity to the network"],
    "payoff": "Falcon 9 remains the vehicle building out Starlink "
              "from California.",
    "key_entities": ["SpaceX", "Starlink", "Falcon 9"],
}
check("SpaceX-shaped script passes deterministic layer",
      reel_factcheck.run_gate(SPX_SCRIPT, SPX_ARTICLE,
                              use_llm=False)["verdict"] == "pass")
_spx_claims = reel_factcheck.collect_claims(SPX_SCRIPT)
_spx_eligible = [(i, c) for i, c in enumerate(_spx_claims)
                 if c["field"] not in
                 reel_factcheck._JUDGE_EXEMPT_FIELDS]
# Unit: echo beats id. A verdict carrying stats[1].label's id but
# stats[2].label's exact text belongs to stats[2].label.
_by_field = {c["field"]: (i, c) for i, c in _spx_eligible}
_att, _un = reel_factcheck.attribute_verdicts(
    _spx_eligible,
    [{"id": "stats[1].label",
      "claim": _by_field["stats[2].label"][1]["text"],
      "verdict": "supported", "reason": "about markets"}])
check("drifted verdict attributed by echoed text, not by id",
      _att.get(_by_field["stats[2].label"][0], {}).get("reason")
      == "about markets"
      and _by_field["stats[1].label"][0] not in _att
      and _un == 0, str((_att, _un)))
# Unit: a stray verdict about a non-claim (the eyebrow) is dropped,
# never shifted onto a neighbouring claim.
_att, _un = reel_factcheck.attribute_verdicts(
    _spx_eligible,
    [{"id": "hook_stat.eyebrow", "claim": "BY THE NUMBERS",
      "verdict": "unsupported", "reason": "no such section"},
     {"id": "payoff",
      "claim": _by_field["payoff"][1]["text"],
      "verdict": "supported", "reason": "about the payoff"}])
check("stray non-claim verdict dropped, neighbour unaffected",
      _un == 1 and len(_att) == 1
      and _att[_by_field["payoff"][0]]["verdict"] == "supported",
      str((_att, _un)))
# Unit: unknown verdict strings are not attributed.
_att, _un = reel_factcheck.attribute_verdicts(
    _spx_eligible,
    [{"id": "payoff", "claim": _by_field["payoff"][1]["text"],
      "verdict": "maybe", "reason": "?"}])
check("unknown verdict string left unattributed", _att == {}
      and _un == 1, str((_att, _un)))

_orig_judge_call = reel_factcheck._judge_call
_seen_fields = []


def _fake_drift(ask_claims, article):
    """Round 1 replicates the SpaceX failure: the tail verdicts carry
    the right claim TEXT under the wrong ids, and two claims get no
    verdict at all. The re-ask (small list) is answered honestly."""
    _seen_fields.extend(c["field"] for c in ask_claims)
    texts = {c["field"]: c["text"] for c in ask_claims}
    if len(ask_claims) <= 2:
        return ([{"id": c["field"], "claim": c["text"],
                  "verdict": "supported", "reason": "re-ask ok"}
                 for c in ask_claims], 0.0, None)
    out = [{"id": c["field"], "claim": c["text"],
            "verdict": "supported", "reason": f"about {c['field']}"}
           for c in ask_claims[:7]]
    for wrong_id, right_field in (
            ("stats[1].label", "stats[2].label"),
            ("stats[2].big", "diaspora_bullets[0]"),
            ("stats[2].label", "diaspora_bullets[1]"),
            ("diaspora_bullets[0]", "payoff")):
        out.append({"id": wrong_id, "claim": texts[right_field],
                    "verdict": "supported",
                    "reason": f"about {right_field}"})
    return out, 0.0, None


try:
    reel_factcheck._judge_call = _fake_drift
    _seen_fields.clear()
    rep = reel_factcheck.run_gate(SPX_SCRIPT, SPX_ARTICLE,
                                  use_llm=True)
finally:
    reel_factcheck._judge_call = _orig_judge_call
check("drifted judge response still passes an honest script",
      rep["verdict"] == "pass", json.dumps(rep["held_claims"]))
check("eyebrow is never sent to the judge",
      "hook_stat.eyebrow" not in _seen_fields, str(_seen_fields))
check("eyebrow claim records no LLM verdict",
      next(c for c in rep["claims"]
           if c["field"] == "hook_stat.eyebrow")
      ["verdicts"]["llm"] is None)
check("the two unanswered claims were re-asked exactly once",
      rep["llm"]["reasked_claims"] == ["stats[1].label",
                                        "stats[2].big"],
      str(rep["llm"]))
check("drifted reasons land on the claims they are about",
      next(c for c in rep["claims"] if c["field"] == "payoff")
      ["llm_reason"] == "about payoff"
      and next(c for c in rep["claims"]
               if c["field"] == "diaspora_bullets[1]")
      ["llm_reason"] == "about diaspora_bullets[1]",
      json.dumps([(c["field"], c.get("llm_reason"))
                  for c in rep["claims"]]))
check("no judge errors on the recovered run",
      rep["judge_errors"] == [] and rep["llm"]["rounds"] == 2)


def _fake_silent_on_payoff(ask_claims, article):
    return ([{"id": c["field"], "claim": c["text"],
              "verdict": "supported", "reason": "ok"}
             for c in ask_claims if c["field"] != "payoff"],
            0.0, None)


try:
    reel_factcheck._judge_call = _fake_silent_on_payoff
    rep = reel_factcheck.run_gate(SPX_SCRIPT, SPX_ARTICLE,
                                  use_llm=True)
finally:
    reel_factcheck._judge_call = _orig_judge_call
_pay = next(c for c in rep["claims"] if c["field"] == "payoff")
check("claim the judge never answers is held as judge_error",
      rep["verdict"] == "fail" and "payoff" in rep["held_claims"]
      and _pay["verdicts"]["llm"] == "judge_error"
      and rep["judge_errors"] == ["payoff"], str(rep["held_claims"]))


def _fake_unsupported_payoff(ask_claims, article):
    return ([{"id": c["field"], "claim": c["text"],
              "verdict": "unsupported" if c["field"] == "payoff"
              else "supported", "reason": "checked"}
             for c in ask_claims], 0.0, None)


try:
    reel_factcheck._judge_call = _fake_unsupported_payoff
    rep = reel_factcheck.run_gate(SPX_SCRIPT, SPX_ARTICLE,
                                  use_llm=True)
finally:
    reel_factcheck._judge_call = _orig_judge_call
_pay = next(c for c in rep["claims"] if c["field"] == "payoff")
check("genuinely unsupported claim still holds, correctly labelled",
      rep["verdict"] == "fail" and rep["held_claims"] == ["payoff"]
      and _pay["verdicts"]["llm"] == "unsupported"
      and rep["judge_errors"] == [], str(rep["held_claims"]))

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
