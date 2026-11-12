#!/usr/bin/env python3
"""
test_reel_v8.py — unit checks for Reels v8 (reel_renderer_v8.py,
adopted 2026-11-11 on Kiran's approval of the GPT-benchmark
sample): the distinct-image planner (never re-crop; the visa
Short failure), the scene-person rule inside it, content
derivation from the unchanged production script schema
(editorial hook title-casing, big-stat arrow form, V-1/V-2
option rows), block fitting inside the QA safe geometry, the
chrome's QA-band discipline, and the topical-stock route's
eligibility + signage screens (reel_stock_sourcing.py) plus
the producer's candidate assembly / footer derivation.

Run:  python3 test_reel_v8.py    (exits 1 on any failure)
"""
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer_v8 as V8
import reel_stock_sourcing as STOCK
import reel_produce as RP
from PIL import Image

FAILS = []


def check(name, cond):
    print(("  ✓ " if cond else "  ✗ ") + name)
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(f"{name} (got {got!r})", got == want)


VISA = {
    "hook_line": "INDIA CUTS VISA CATEGORIES FROM 13 TO NINE, "
                 "RENAMES TOURIST VISA AS VISITOR VISA",
    "hook_stat": {"big": "13 TO 9", "eyebrow": "BY THE NUMBERS",
                  "sub": "Main visa categories India will "
                         "consolidate into nine"},
    "stats": [{"big": "49 TO 23",
               "label": "Sub-categories, cut under the Home "
                        "Ministry's Visa Manual review"},
              {"big": "70%",
               "label": "Of visa application form fields to "
                        "be cut"}],
    "diaspora_bullets": [
        "V-1 is for short visits, V-2 for longer stays",
        "Visitor Visa covers visiting friends or relatives"],
    "key_entities": ["Visitor Visa", "Tourist Visa",
                     "Union Home Ministry", "Visa Manual"],
    "news_summary": "India will consolidate its 13 main visa "
                    "categories into nine and cut sub-categories "
                    "from 49 to 23 under a Union Home Ministry "
                    "review of the Visa Manual, 2019, renaming "
                    "the Tourist Visa as the Visitor Visa.",
    "payoff": "Applicants should keep using the current "
              "categories until the new structure is notified.",
}
BEATS = ["hook", "news", "hero", "grid", "diaspora", "payoff"]
TEXTS = {k: " ".join(V8.R.SCENE_TEXTS[k](VISA, "Immigration"))
         for k in BEATS}


def _cand(tmp, name, color, size=(2400, 1600), person=None,
          kind="inline"):
    p = Path(tmp) / name
    Image.new("RGB", size, color).save(p)
    return {"label": name, "kind": kind, "path": str(p),
            "size": list(size), "person": person,
            "provenance": {"route": "test"}}


print("── distinct-image planner: never re-crop ──")
with tempfile.TemporaryDirectory() as tmp:
    cands = [_cand(tmp, f"c{i}.jpg", (i * 30, 40, 90))
             for i in range(6)]
    plans = V8.plan_v8_images(BEATS, cands, TEXTS)
    check_eq("six distinct candidates cover six scenes",
             [p["candidate"]["label"] for p in plans],
             [c["label"] for c in cands])
    check("no image repeats across beats",
          len({p["candidate"]["path"] for p in plans}) == 6)
    try:
        V8.plan_v8_images(BEATS, cands[:5], TEXTS)
        check("five candidates for six scenes RAISES the hold",
              False)
    except V8.DistinctImagesError as e:
        check("five candidates for six scenes RAISES the hold",
              "re-cropping" in str(e))
    dup = cands[:5] + [dict(cands[0])]
    check_eq("a duplicate file (same content, new name) does "
             "not count as distinct",
             len(V8.usable_distinct(dup)), 5)
    small = _cand(tmp, "small.jpg", (1, 2, 3), size=(800, 500))
    check_eq("a below-floor image does not count as usable",
             len(V8.usable_distinct(cands[:5] + [small])), 5)

print("── planner: scene-person rule ──")
with tempfile.TemporaryDirectory() as tmp:
    person = _cand(tmp, "person.jpg", (9, 9, 9),
                   person="Gautam Adani")
    others = [_cand(tmp, f"g{i}.jpg", (i * 20, 1, 2))
              for i in range(6)]
    plans = V8.plan_v8_images(BEATS, [person] + others, TEXTS)
    placed = {p["beat"]: p["candidate"]["label"] for p in plans}
    check("a person photo no beat names is never placed",
          "person.jpg" not in placed.values())
    ambani_texts = dict(TEXTS)
    ambani_texts["diaspora"] = "Why It Matters To You Gautam " \
                                "Adani at 26th"
    plans = V8.plan_v8_images(BEATS, [person] + others,
                              ambani_texts)
    placed = {p["beat"]: p["candidate"]["label"] for p in plans}
    check_eq("the same photo is placed on the beat that names "
             "him", placed["diaspora"], "person.jpg")

print("── content derivation (production schema, unchanged) ──")
check_eq("hook headline is the editorial title-case form",
         V8.scene_content("hook", VISA, "Immigration")
         ["headline"],
         "India cuts visa categories from 13 to nine, renames "
         "tourist visa as visitor visa")
check_eq("mixed-case headlines pass through untouched",
         V8.editorial_title("India Cuts Its Visa List"),
         "India Cuts Its Visa List")
check_eq("acronyms survive title-casing",
         V8.editorial_title("US RAISES H-1B FEE"),
         "US raises H-1B fee")
check_eq("big stat takes the arrow form",
         V8.big_stat_display("13 TO 9"), "13 → 9")
check_eq("non-arrow stats pass through",
         V8.big_stat_display("70%"), "70%")
rows, rest = V8.parse_option_rows(VISA["diaspora_bullets"])
check_eq("V-1/V-2 bullet parses into option rows", rows,
         [{"label": "V-1", "value": "For short visits"},
          {"label": "V-2", "value": "For longer stays"}])
check_eq("the remaining bullet stays as support", rest,
         ["Visitor Visa covers visiting friends or relatives"])
check_eq("diaspora kicker is the reader-impact beat",
         V8.scene_content("diaspora", VISA, "Immigration")
         ["kicker"], "WHAT IT MEANS FOR YOU")
check_eq("hero beat big stat comes from hook_stat",
         V8.scene_content("hero", VISA, "Immigration")
         ["big_stat"], "13 → 9")

print("── block fitting inside the QA geometry ──")
for k in BEATS:
    spec = V8.scene_content(k, VISA, "Immigration")
    s, h, _parts = V8.fit_block(spec)
    check(f"{k}: block fits ({h}px at {s:.2f})",
          h <= V8.BLOCK_MAX_H)
    check(f"{k}: block bottom stays above the panel "
          f"({V8.BLOCK_BOTTOM} <= {V8.PANEL_Y})",
          V8.BLOCK_BOTTOM <= V8.PANEL_Y)
check("masthead glyphs start below the QA y<118 band",
      V8.MASTHEAD_Y >= 118)
check("scene text column stays inside the QA x bands",
      V8.MARGIN >= 48 and V8.MARGIN + V8.TEXT_MAX_W <= 952)
check("footer panel is house navy (blue 58 defeats the QA "
      "stroke signature by construction)",
      V8.NAVY == (11, 29, 58))

print("── chrome paint: progress + footer land on the panel ──")
bg = Image.new("RGB", (V8.W, V8.H), (70, 80, 90))
bg = V8.paint_chrome(bg, "Immigration",
                     "Source: The Hindu • 11 NOV 2026",
                     "Stock imagery: Pexels", 2, 6)
check_eq("panel pixel is navy",
         bg.getpixel((10, V8.PANEL_Y + 10)), V8.NAVY)
seg_y = V8.PANEL_Y + 16 + 3
filled = bg.getpixel((V8.MARGIN + 4, seg_y))
check(f"an elapsed scene's segment is gold-light ({filled})",
      filled == V8.GOLD_LIGHT)
# The gate's own pixel math over the chrome-only panel: no
# glyph signature may form in the y>1602 band (the first v8
# proof failed exactly here — gold segments + rule line).
import numpy as _np
import reel_frame_qa as _QA
_flat = Image.new("RGB", (V8.W, V8.H), (70, 80, 90))
_flat = V8.paint_chrome(_flat, "Immigration",
                        "Source: The Hindu • 11 NOV 2026",
                        "Stock imagery: Pexels", 3, 6)
_mask = _QA.detect_text_mask(_np.array(_flat))
check("chrome forms no glyph signature in the footer band",
      int(_mask[1602:, :].sum()) == 0)
check("chrome forms no glyph signature in the top band",
      int(_mask[:118, :].sum()) == 0)
# The progress segments sit at the panel's top strip so the
# assembly zoom can never push them into the y>1602 band
# (gold blends form gold-core pixels there — proof, run 7).
_seg_bottom_out = (V8.PANEL_Y + 16 + 6) * 1.07 \
    - 0.3 * V8.H * 0.07
check(f"progress segments stay above the QA band at max "
      f"zoom (out y {_seg_bottom_out:.0f} < 1602)",
      _seg_bottom_out < 1602)

print("── motion: eased zoom has no staircase ──")
_zs = [V8.zoom_at_v8(n / V8.FPS) for n in
       range(int(V8.TOTAL * V8.FPS) + 1)]
_dz = [b - a for a, b in zip(_zs, _zs[1:])]
check("zoom is monotonic non-decreasing",
      all(d >= 0 for d in _dz))
check("zoom starts at 1.00 and ends at 1.07",
      abs(_zs[0] - 1.0) < 1e-9 and abs(_zs[-1] - 1.07) < 1e-9)
_ddz = [abs(b - a) for a, b in zip(_dz, _dz[1:])]
check(f"per-frame zoom delta changes gradually (max second "
      f"difference {max(_ddz):.2e} << the delta itself)",
      max(_ddz) < max(_dz) * 0.05)
check("no frame-to-frame zoom jump exceeds 0.0005 (a whole-"
      "pixel step at 2x would be ~0.00046 in scale on the "
      "window, applied in one frame, every frame)",
      max(_dz) < 0.0005)
_white = Image.new("RGB", (V8.W, V8.H), (255, 255, 255))
_scrimmed = V8.apply_side_scrims(_white)
_px = _scrimmed.load()
check("side scrims push edge whites below the QA core "
      "threshold (<=235) across the reachable band",
      all(_px[x, 960][0] <= 235 for x in range(0, 86))
      and all(_px[x, 960][0] <= 235 for x in range(925, 1080)))
last_x = V8.MARGIN + 5 * ((V8.W - 2 * V8.MARGIN - 5 * 16) // 6
                          + 16) + 4
check_eq("an unreached scene's segment stays dim",
         bg.getpixel((last_x, seg_y)), V8.SEG_OFF)

print("── stock route: eligibility (fail closed) ──")
visa_article = {"slug": "india-visa-categories-cut-13-to-9",
                "headline": "India Cuts Visa Categories From "
                            "13 to Nine",
                "category": "immigration", "body": ""}
ok, why = STOCK.is_concept_policy_story(visa_article, VISA)
check(f"visa story is stock-eligible ({why})", ok)
person_article = {"slug": "x", "headline": "Adani Group Capex",
                  "category": "markets-finance", "body": ""}
person_script = dict(VISA, key_entities=["Gautam Adani"],
                     hook_line="ADANI GROUP ANNOUNCES CAPEX")
ok, why = STOCK.is_concept_policy_story(person_article,
                                        person_script)
check(f"named-person story is stock-ineligible ({why})",
      not ok)
plain_article = {"slug": "y", "headline": "Local Team Wins "
                                          "Final",
                 "category": "sports", "body": ""}
plain_script = dict(VISA, key_entities=["Chennai Stadium"],
                    hook_line="LOCAL TEAM WINS FINAL",
                    news_summary="The local team won the final "
                                 "on Sunday.")
ok, why = STOCK.is_concept_policy_story(plain_article,
                                        plain_script)
check(f"no policy/concept signal is ineligible ({why})",
      not ok)

print("── stock route: signage + dimension screens ──")
ok, why = STOCK.alt_text_locale_ok(
    "People walking in an airport terminal", set())
check("clean English alt passes", ok)
ok, why = STOCK.alt_text_locale_ok(
    "Travelers at Hanoi airport, Vietnam", set())
check(f"unrelated-locale alt rejects ({why})", not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Bảng departures board at the airport", set())
check(f"non-Latin alt rejects ({why})", not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Taj Mahal at sunrise, India travel", set())
check("story-locale alt passes", ok)
ok, why = STOCK.alt_text_locale_ok(
    "Passengers checking the departure board at Hong Kong "
    "International Airport", set())
check(f"Hong Kong alt rejects ({why})", not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Crowds in the departure area of Amsterdam's Schiphol "
    "Airport", set())
check(f"Schiphol alt rejects ({why})", not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Flat lay image of a health passport with a COVID-19 "
    "QR code, calendar, and map",
    {"india", "visa", "categories"})
check(f"COVID health-passport alt rejects for a visa story "
      f"({why})", not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Two Ukrainian passports placed on a white surface",
    {"india", "visa", "categories"})
check(f"a foreign country's passports reject ({why})",
      not ok)
ok, why = STOCK.alt_text_locale_ok(
    "Nurse preparing a COVID-19 vaccine dose",
    {"covid", "vaccine", "booster"})
check("the same words pass when the story IS about them",
      ok)
check("stock dims floor: 4000x6000 original passes",
      STOCK.dims_ok_stock(4000, 6000))
check("stock dims floor: 1600x1200 rejects",
      not STOCK.dims_ok_stock(1600, 1200))
queries = STOCK.build_stock_queries(visa_article, VISA)
check("queries are topical scenes, never a person",
      all("adani" not in q.lower() for q in queries)
      and len(queries) >= 4)

print("── stock route: per-beat matching + resolution floors ──")
_form_script = dict(VISA)
_form_script["stats"] = [
    {"big": "~70%", "label": "fewer application form fields"},
    {"big": "49 → 23", "label": "subcategories"}]
_gq = STOCK.beat_queries(visa_article, _form_script, "grid")
check(f"a form-fields beat leads with the form query "
      f"({_gq[0]!r})",
      "form" in _gq[0])
_dq = STOCK.beat_queries(visa_article, VISA, "diaspora")
check("a visiting-family beat leads with a travel/family "
      "query, not the form query",
      "form" not in _dq[0])
ok, why = STOCK.photo_acceptable({"width": 1079,
                                  "height": 2000})
check(f"1079px wide is below the hard floor ({why})",
      not ok)
ok, why = STOCK.photo_acceptable({"width": 4000,
                                  "height": 6000})
check("4000x6000 clears the scene floors", ok)
ok, why = STOCK.photo_acceptable({"width": 1920,
                                  "height": 1280})
check(f"a 1920x1280 landscape's 9:16 window is too small "
      f"for a scene ({why})", not ok)
_ranked = STOCK.rank_photos([
    {"id": 1, "width": 1300, "height": 2000},
    {"id": 2, "width": 4000, "height": 6000},
    {"id": 3, "width": 2000, "height": 3000}])
check_eq("resolution ranking: >=1920px originals first, "
         "widest first",
         [p["id"] for p in _ranked], [2, 3, 1])

print("── planner: per-beat stock tags win their beat ──")
with tempfile.TemporaryDirectory() as tmp:
    _tagged = _cand(tmp, "tagged.jpg", (9, 9, 9),
                    kind="stock")
    _tagged["beat"] = "payoff"
    _plain = [_cand(tmp, f"p{i}.jpg", (i, i, i))
              for i in range(5)]
    _plans = V8.plan_v8_images(
        ["hook", "news", "hero", "grid", "diaspora",
         "payoff"], _plain + [_tagged])
    _by_beat = {p["beat"]: p["candidate"] for p in _plans}
    check("the payoff-tagged scene lands on the payoff beat "
          "even though it is last in priority order",
          _by_beat["payoff"] is _tagged)

print("── stock route: per-beat sourcing (stubbed network) ──")
_fake_photos = [
    {"id": 101, "width": 1300, "height": 2000,
     "alt": "Hand writing on a paper form",
     "url": "https://www.pexels.com/photo/101",
     "photographer": "A",
     "src": {"original": "https://img/101"}},
    {"id": 102, "width": 4200, "height": 5600,
     "alt": "Traveler with a suitcase at the airport",
     "url": "https://www.pexels.com/photo/102",
     "photographer": "B",
     "src": {"original": "https://img/102"}},
    {"id": 103, "width": 900, "height": 1400,
     "alt": "Airport terminal",
     "url": "https://www.pexels.com/photo/103",
     "photographer": "C",
     "src": {"original": "https://img/103"}}]


def _fake_search(q, key, per_page=8):
    if "form" in q:
        return [_fake_photos[0], _fake_photos[2]]
    return [_fake_photos[1], _fake_photos[2]]


def _fake_download(url, dest):
    pid = int(str(dest).split("-")[-1].split(".")[0])
    Image.new("RGB", (2400, 3200),
              (pid % 200, 40, 40)).save(dest)


_orig_search, _orig_dl = STOCK._pexels_search, STOCK._download
STOCK._pexels_search, STOCK._download = _fake_search, \
    _fake_download
try:
    with tempfile.TemporaryDirectory() as tmp:
        _prov = STOCK.source_stock_scenes(
            visa_article, _form_script, Path(tmp), 2,
            log=lambda *a: None, api_key="test",
            beats=["grid", "diaspora"])
        _by_beat = {s["beat"]: s for s in _prov["scenes"]}
        check_eq("one scene per requested beat",
                 sorted(_by_beat), ["diaspora", "grid"])
        check("the grid beat's scene came from the form "
              "query (its own text)",
              "form" in (_by_beat["grid"]["query"] or ""))
        check("every scene clears the 1080px hard floor and "
              "logs its dimensions",
              all(s["size"][0] >= 2400 - 1
                  for s in _prov["scenes"]))
        check("the 900px-wide photo never becomes a scene "
              "(below the hard floor)",
              all(s["pexels_id"] != 103
                  for s in _prov["scenes"]))
finally:
    STOCK._pexels_search, STOCK._download = _orig_search, \
        _orig_dl

print("── composition: never upscale ──")
_stamp = Image.new("RGB", (2009, 1361), (120, 110, 90))
_bg, _pl, _fb = V8.compose_bg(_stamp, (0.5, 0.5), None, 1000)
check(f"a 2009x1361 hero demotes instead of upscaling its "
      f"9:16 window ({_pl['mode']}, scale {_pl['scale']:.2f})",
      _pl["mode"] == "backdrop-demoted" and _pl["scale"] <= 1.0)
_big = Image.new("RGB", (4000, 6000), (60, 90, 120))
_bg, _pl, _fb = V8.compose_bg(_big, (0.5, 0.5), None, 1000)
check(f"a 4000x6000 original earns full-bleed cover "
      f"({_pl['mode']}, scale {_pl['scale']:.2f})",
      _pl["mode"] == "cover" and _pl["scale"] <= 1.0)

print("── producer: candidate assembly + footer ──")
with tempfile.TemporaryDirectory() as tmp:
    hero = _cand(tmp, "hero.jpg", (5, 5, 5), kind="hero")
    inl = [(Path(tmp) / "hero.jpg", (2400, 1600))]
    cands = RP.build_v8_candidates(
        Path(tmp) / "hero.jpg", (2400, 1600), [], {})
    check_eq("hero is candidate #1", cands[0]["kind"], "hero")
    art = {"sources": [{"name": "The Hindu", "url": "https://x"}],
           "published_at": "2026-11-11T16:48:59+00:00"}
    check_eq("footer source derives from the article's own "
             "sources + date", RP.footer_source_for(art),
             "Source: The Hindu • 11 NOV 2026")
    check_eq("no sources -> no invented source line",
             RP.footer_source_for({}), "")
check("v8 is the production renderer by default",
      RP._use_v8())
import os
os.environ["VIDESHI_REEL_RENDERER"] = "v7"
check("VIDESHI_REEL_RENDERER=v7 restores the v7 path",
      not RP._use_v8())
del os.environ["VIDESHI_REEL_RENDERER"]

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("✅ all v8 checks passed")
