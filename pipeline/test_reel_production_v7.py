#!/usr/bin/env python3
"""
test_reel_production_v7.py — production-adoption checks for
Reels v7 (2026-10-24):

  * reel_produce.py (the production entry the cron invokes)
    renders through reel_renderer_v7 with the BLACK stage by
    default, navy on --stage, and the verdict keeps the exact
    shape reel_publish.py gates on.
  * The rollback switch (USE_V7_RENDERER = False) routes the
    same produce flow to the v6 renderer.
  * reel_entity_sourcing.py: route order (Commons -> official
    -> discovery), the identity / license / resolution gates
    rejecting for the right reasons, beat assignment, and the
    never-block-the-reel fallback when sourcing fails outright.

All network is stubbed. Run:  python3 test_reel_production_v7.py
"""
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image

import reel_produce
import reel_entity_sourcing as S
import reel_renderer_v7  # imported AFTER reel_produce: this is the
                         # module object produce's lazy import sees

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(f"{name} (got {got!r})", got == want)


ARTICLE = {
    "id": "test-id", "slug": "acme-corp-opens-campus",
    "headline": "Acme Corp Opens New Campus as CEO Jane Doe "
                "Cuts the Ribbon",
    "category": "technology",
    "image_url": "https://example.com/hero.jpg",
    "body": "Acme Corp opened its campus on Monday. Jane Doe, "
            "the Acme Corp chief executive, spoke. Acme Corp "
            "employs 4,000 people; Jane Doe said hiring continues.",
}
SCRIPT = {
    "hook_line": "Acme Corp opens its new campus",
    "news_summary": "Acme Corp opened its new headquarters "
                    "campus on Monday, with CEO Jane Doe cutting "
                    "the ribbon.",
    "hook_stat": {"big": "4,000", "eyebrow": "TECHNOLOGY",
                  "sub": "jobs at the new Acme campus"},
    "stats": [{"big": "4,000", "label": "JOBS AT THE CAMPUS"},
              {"big": "2026", "label": "YEAR THE CAMPUS OPENED"}],
    "diaspora_bullets": ["Indian engineers are a large share of "
                         "Acme's workforce"],
    "key_entities": ["Acme Corp", "Jane Doe"],
    "payoff": "Jane Doe said Acme Corp will keep hiring through "
              "the year.",
    "versus": None, "story_mood": "news",
}


# ── Part 1: produce wiring (stubbed gates + renderers) ─────────────
print("── produce: v7 renderer + black stage by default ──")
captured = {}


def fake_render_v7(script, hero, inlines, music, outdir, **kw):
    captured.update(kw)
    captured["inlines"] = inlines
    video = Path(outdir) / "fake.mp4"
    video.write_bytes(b"\0" * 2048)
    (Path(outdir) / "render-manifest.json").write_text("{}")
    return video, {"video": str(video)}


def fake_render_v6(script, hero, music, outdir, name, **kw):
    captured["v6"] = True
    video = Path(outdir) / "fake.mp4"
    video.write_bytes(b"\0" * 2048)
    (Path(outdir) / "render-manifest.json").write_text("{}")
    return {"video": str(video)}


def run_produce(argv_extra, tmp):
    script_p = Path(tmp) / "script.json"
    article_p = Path(tmp) / "article.json"
    script_p.write_text(json.dumps(SCRIPT))
    article_p.write_text(json.dumps(ARTICLE))
    outdir = Path(tmp) / "output"
    argv = ["reel_produce.py", "--script", str(script_p),
            "--article-file", str(article_p),
            "--outdir", str(outdir)] + argv_extra
    old_argv = sys.argv
    sys.argv = argv
    try:
        code = reel_produce.main()
    finally:
        sys.argv = old_argv
    verdict = json.loads((outdir / "verdict.json").read_text())
    return code, verdict


_orig = {
    "run_gate": reel_produce.reel_factcheck.run_gate,
    "download_hero": reel_produce.download_hero,
    "fetch_inlines": reel_produce.fetch_inline_images,
    "source_extras": reel_produce.reel_entity_sourcing.source_extras,
    "render_v7": reel_renderer_v7.render_reel_v7,
    "render_v6": reel_produce.reel_renderer.render_reel,
    "run_qa": reel_produce.reel_frame_qa.run_qa,
    "flag": reel_produce.USE_V7_RENDERER,
}
reel_produce.reel_factcheck.run_gate = lambda s, a, use_llm=True: {
    "verdict": "pass", "held_claims": [], "llm": {"cost_usd": 0.0}}


def _fake_hero(url, dest):
    Image.new("RGB", (1600, 1200), (40, 60, 90)).save(dest)


reel_produce.download_hero = _fake_hero
reel_produce.fetch_inline_images = lambda a, o, log=print: []
reel_produce.reel_entity_sourcing.source_extras = \
    lambda a, s, d, own, log=print: {"extras": []}
reel_renderer_v7.render_reel_v7 = fake_render_v7
reel_produce.reel_renderer.render_reel = fake_render_v6
reel_produce.reel_frame_qa.run_qa = lambda v, m, q: {
    "qa_score": 9.5, "qa_passed": True, "failing_checks": []}

with tempfile.TemporaryDirectory() as tmp:
    code, verdict = run_produce([], tmp)
    check_eq("produce exits ready", code, 0)
    check_eq("verdict status ready", verdict["status"], "ready")
    check_eq("verdict driver is the production driver",
             verdict["driver"], "reel_produce.py")
    check_eq("verdict names the v7 renderer",
             verdict["render"]["renderer"], "reel_renderer_v7.py")
    check_eq("verdict records the black stage",
             verdict["render"]["stage_color"], "black")
    check_eq("renderer received the black stage",
             captured.get("stage"), "black")
    check("renderer received an extras dict",
          isinstance(captured.get("extras"), dict))
    check_eq("sourcing ran in ladder mode (own=1 < 5)",
             verdict["sourcing"]["mode"], "ladder")
    check_eq("publish-gate fields intact",
             (verdict["factcheck"]["verdict"],
              verdict["qa"]["passed"], verdict["qa"]["score"]),
             ("pass", True, 9.5))
    pack = Path(verdict.get("tiktok_pack") or "")
    check("TikTok pack written beside the verdict", pack.exists())
    if pack.exists():
        pack_text = pack.read_text()
        check("pack = MP4 path + caption, no bare URL anywhere",
              pack_text.startswith("VIDEO: ")
              and "CAPTION:" in pack_text
              and "http://" not in pack_text
              and "https://" not in pack_text)
        check("caption leads with the hook and carries hashtags",
              SCRIPT["hook_line"] in pack_text
              and "#TheVideshi" in pack_text)

with tempfile.TemporaryDirectory() as tmp:
    captured.clear()
    code, verdict = run_produce(["--stage", "navy"], tmp)
    check_eq("--stage navy reaches the renderer",
             captured.get("stage"), "navy")
    check_eq("verdict records navy when asked",
             verdict["render"]["stage_color"], "navy")

print("── produce: one-line rollback to v6 ──")
reel_produce.USE_V7_RENDERER = False
with tempfile.TemporaryDirectory() as tmp:
    captured.clear()
    code, verdict = run_produce([], tmp)
    check_eq("rollback produce exits ready", code, 0)
    check("v6 renderer was called", captured.get("v6") is True)
    check_eq("verdict names the v6 renderer",
             verdict["render"]["renderer"], "reel_renderer.py")
    check_eq("sourcing skipped under v6 (v6 has no extras path)",
             verdict["sourcing"]["mode"], "skipped")
reel_produce.USE_V7_RENDERER = _orig["flag"]
reel_produce.reel_factcheck.run_gate = _orig["run_gate"]
reel_produce.download_hero = _orig["download_hero"]
reel_produce.fetch_inline_images = _orig["fetch_inlines"]
reel_produce.reel_entity_sourcing.source_extras = \
    _orig["source_extras"]
reel_renderer_v7.render_reel_v7 = _orig["render_v7"]
reel_produce.reel_renderer.render_reel = _orig["render_v6"]
reel_produce.reel_frame_qa.run_qa = _orig["run_qa"]


# ── Part 2: sourcing gates + route order (stubbed network) ─────────
print("── sourcing: gates reject for the right reasons ──")


def cpage(title, w, h, lic, desc, mime="image/jpeg",
          cats="Category:Test"):
    return {"title": title, "imageinfo": [{
        "url": "https://upload.wikimedia.org/wikipedia/commons/x/"
               + title.replace(" ", "_"),
        "descriptionurl": "https://commons.wikimedia.org/wiki/"
                          + title.replace(" ", "_"),
        "width": w, "height": h, "mime": mime,
        "extmetadata": {
            "LicenseShortName": {"value": lic},
            "UsageTerms": {"value": lic},
            "ImageDescription": {"value": desc},
            "Categories": {"value": cats},
            "Artist": {"value": "Test Photographer"}}}]}


CALLS = []


def fake_commons_search(query, limit=10):
    CALLS.append(("commons", query))
    if "Acme" in query:
        return [
            cpage("File:Acme Corp Campus.jpg", 4160, 3120,
                  "CC BY 4.0",
                  "Acme Corp headquarters campus in Bengaluru",
                  cats="Category:Acme Corp"),
            cpage("File:Acme Corp Old Building.jpg", 2200, 1500,
                  "GFDL", "Acme Corp building, older wing",
                  cats="Category:Acme Corp"),
            cpage("File:Acme Corp Front.jpg", 1024, 768,
                  "CC BY 4.0", "Acme Corp front view",
                  cats="Category:Acme Corp"),
            cpage("File:Neoscona sp 01.JPG", 3000, 2000,
                  "CC BY 4.0", "Neoscona spider macro on a leaf"),
            cpage("File:Acme Corp logo.png", 2000, 2000,
                  "CC BY 4.0", "Acme Corp logo",
                  mime="image/png"),
        ]
    if "Jane Doe" in query:
        return [
            cpage("File:John Doe at conference.jpg", 2400, 1600,
                  "CC BY 4.0", "John Doe speaking at a conference"),
            cpage("File:Jane Doe portrait.jpg", 2000, 2500,
                  "CC BY-SA 4.0",
                  "Jane Doe, chief executive of Acme Corp"),
        ]
    return []


def fake_download(url, dest):
    CALLS.append(("download", url))
    Image.new("RGB", (1600, 1200), (30, 40, 50)).save(dest)


FAKE_NET = {
    "commons_search": fake_commons_search,
    "commons_file_info": lambda title: None,
    "brave_links": lambda q, max_results=8:
        (CALLS.append(("brave", q)) or []),
    "fetch_text": lambda url, timeout=15: "",
    "download": fake_download,
}

with tempfile.TemporaryDirectory() as tmp:
    prov = S.source_extras(ARTICLE, SCRIPT, Path(tmp) / "supp",
                           own_count=1, log=lambda *a: None,
                           net=FAKE_NET)
    extras = {e["beat"]: e for e in prov["extras"]}
    check("campus assigned (news beat, entity + establishing)",
          extras.get("news", {}).get("label", "")
          .startswith("acme-corp-campus"), str(extras.keys()))
    check("portrait assigned (payoff beat mentions Jane Doe)",
          "portrait" in extras.get("payoff", {}).get("label", ""),
          str(extras.keys()))
    reasons = " | ".join(r.get("reason", "")
                          for r in prov["candidate_ledger"])
    check("GFDL file rejected on license",
          "license" in reasons and "GFDL" in reasons)
    check("1024x768 file rejected on resolution",
          "resolution" in reasons and "1024x768" in reasons)
    check("spider macro rejected on identity",
          "identity" in reasons)
    check("wrong-person file rejected on identity",
          reasons.count("identity") >= 2)
    used = [r for r in prov["candidate_ledger"]
            if str(r.get("verdict", "")).startswith("USED")]
    check_eq("two extras marked USED in the ledger", len(used), 2)
    kinds = [c[0] for c in CALLS]
    check("route order: Commons searched before Brave discovery",
          kinds.index("commons") < kinds.index("brave")
          if "brave" in kinds else True)
    for e in prov["extras"]:
        check(f"extra {e['label']} carries full provenance",
              all(e.get(k) for k in ("source_page", "file_url",
                                     "license", "size", "path")))


print("── sourcing: failure falls back, never raises ──")


def dead_commons(query, limit=10):
    raise RuntimeError("network down")


DEAD_NET = {**FAKE_NET, "commons_search": dead_commons,
            "brave_links": lambda q, max_results=8: (_ for _ in ())
            .throw(RuntimeError("search down"))}
with tempfile.TemporaryDirectory() as tmp:
    try:
        prov = S.source_extras(ARTICLE, SCRIPT, Path(tmp) / "supp",
                               own_count=1, log=lambda *a: None,
                               net=DEAD_NET)
        check("dead network -> empty extras, no exception",
              prov["extras"] == [])
    except Exception as e:
        check("dead network -> empty extras, no exception", False,
              str(e))

print("── sourcing: pure gates ──")
check_eq("CC BY-SA accepted",
         S.license_verdict({"LicenseShortName":
                            {"value": "CC BY-SA 4.0"}})[0], True)
check_eq("GFDL rejected",
         S.license_verdict({"LicenseShortName":
                            {"value": "GFDL"}})[0], False)
check_eq("public domain accepted",
         S.license_verdict({"LicenseShortName":
                            {"value": "Public domain"}})[0], True)
check("identity: Salil Parekh != Asha Parekh",
      not S.identity_ok("Salil Parekh", "File:Asha Parekh.jpg",
                        "Asha Parekh at an event", ""))
check("identity: full-name evidence passes",
      S.identity_ok("Salil Parekh", "File:Salil Parekh Davos.jpg",
                    "Salil Parekh at Davos", ""))
check("dims: 1024x768 is below the floor", not S.dims_ok(1024, 768))
check("dims: 4160x3120 passes", S.dims_ok(4160, 3120))
check("denylist catches logos", S.title_denied("File:Acme logo.png"))
check("need=0 assigns nothing",
      S.assign_beats([{"entity": "Acme Corp", "role": "people",
                       "subject": "Acme Corp staff"}],
                     SCRIPT, "Technology", 0) == {})

print("── sourcing: relevance discipline (first production run) ──")
# The 2026-10-24 Romanch run's wrong accepts, as regression cases.
warbler = cpage(
    "File:Bay-breasted warbler in Central Park (43472).jpg",
    3948, 2861, "CC BY-SA 4.0",
    "Bay-breasted warbler in Central Park, New York.",
    cats="Setophaga castanea|Birds of Central Park|"
         "Passeriformes of Central Park")
cand, row = S.evaluate_commons_page(warbler, "Central Park",
                                    "A — test")
check("warbler AT the park is not a picture OF the park",
      cand is None and "wildlife" in row["reason"], row["reason"])
district = cpage(
    "File:New York City Council District 12 (2013).png",
    2503, 2480, "CC BY-SA 4.0",
    "An outline of the New York City Council's 12th district, "
    "created using public data on QGIS.")
cand, row = S.evaluate_commons_page(district,
                                    "New York City Council",
                                    "A — test")
check("district outline map rejected as a graphic",
      cand is None and "map-type" in row["reason"], row["reason"])
carriage = cpage(
    "File:Central Park Horse Carriage (6279773432).jpg",
    3648, 2736, "CC BY 2.0", "Central Park",
    cats="Category:Central Park")
cand, row = S.evaluate_commons_page(carriage, "Central Park",
                                    "A — test")
check("a real carriage photo of the park passes every gate",
      cand is not None, row["reason"])
romanch_headline = {
    "headline": "New York Bans Horse-Drawn Carriages Under "
                "Romanch's Law, Honouring Indian Teen",
    "body": "Romanch's Law was adopted. The New York City "
            "Council voted."}
check_eq("topical hint strips entities + headline verbs",
         S.topical_hint(romanch_headline,
                        ["New York City Council", "Central Park",
                         "Romanch Mahajan"]),
         "horse drawn carriages")
check_eq("hint query leads for places/orgs",
         S.queries_for("Central Park", "horse drawn carriages")[0],
         "Central Park horse drawn carriages")
check("Central Park is a place, not a person",
      not S._looks_like_person("Central Park"))
check("Jane Doe is still a person",
      S._looks_like_person("Jane Doe"))
un_photo = cpage(
    "File:New York City United Nations UNO.jpg", 2592, 1944,
    "CC BY-SA 3.0",
    "The headquarters of the United Nations in New York City, "
    "home of the Security Council chamber.",
    cats="Category:United Nations")
cand, row = S.evaluate_commons_page(un_photo,
                                    "New York City Council",
                                    "A — test")
check("scattered tokens are not identity (UN photo vs City "
      "Council)", cand is None and "identity" in row["reason"],
      row["reason"])
doj_photo = cpage(
    "File:Department of Justice Washington DC.jpg", 3200, 2400,
    "CC BY-SA 4.0",
    "The Department of Justice Building in Washington.",
    cats="Category:Washington DC")
cand, row = S.evaluate_commons_page(doj_photo,
                                    "US Department of Justice",
                                    "A — test")
check("a contiguous agency phrase IS identity",
      cand is not None, row["reason"])
ents = S.extract_entities(romanch_headline, {})
check("headline-ese phrases that the body never repeats are "
      "not entities",
      "New York Bans Horse-Drawn Carriages" not in ents
      and "Honouring Indian Teen" not in ents, str(ents))
check("a headline phrase the body repeats survives (Romanch's "
      "Law)", "Romanch's Law" in ents, str(ents))

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("✅ all production v7 checks passed")
