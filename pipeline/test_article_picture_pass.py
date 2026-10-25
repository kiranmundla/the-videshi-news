#!/usr/bin/env python3
"""
test_article_picture_pass.py — unit tests for the enricher-side
article picture pass (article_picture_pass.py).

Covers: entity ranking + image_entities sanity (category junk
rejected), hero classification (blocked / null / Pexels / generic /
broken / verified-keep), the never-downgrade floor, license +
identity gates on Commons candidates (incl. the namesake and
wildlife-subject rejections), inline counting + placement rules
(enricher figure format, after intro, spread, capped), the
backfill-blocked whole-article skip, and the dry-run contract:
ZERO writes (patch function is never invoked).

All network is stubbed. Run:
  python3 test_article_picture_pass.py   (exit 0 = all pass)
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import article_picture_pass as P

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(name, got == want, f"got {got!r}, want {want!r}")


BODY = (
    '<div class="key-takeaways"><ul><li>Takeaway one.</li></ul>'
    '</div>'
    '<p>Intro paragraph about the Reserve Bank of India opening '
    'its new data centre in Bhubaneswar on Sunday.</p>'
    '<h2>What Was Announced</h2>'
    '<p>The Reserve Bank of India said the Bhubaneswar facility '
    'will anchor its cybersecurity training for banks across the '
    'country, with Narendra Modi attending the inauguration.</p>'
    '<p>Officials said the centre will train thousands of bank '
    'staff every year.</p>'
    '<h2>Why It Matters</h2>'
    '<p>Analysts said the Reserve Bank of India move signals a '
    'deeper push on digital-payment security.</p>'
    '<p>More detail on the programme and its first cohort.</p>'
    + '<p>Filler paragraph to clear the word floor. </p>' * 40
)

ARTICLE = {
    "id": "art-1", "slug": "modi-rbi-data-centre-bhubaneswar",
    "headline": "Modi Inaugurates RBI Data Centre in Bhubaneswar",
    "category": "news", "image_url": None,
    "image_caption": "", "image_attribution": "",
    "image_entities": ["Nri World", "Reserve Bank of India"],
    "image_backfill_blocked": False,
    "published_at": "2026-10-25T12:46:00Z",
    "body": BODY, "sources": [],
}


def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats="", artist="A Photographer",
                 mime="image/jpeg", size=None, url=None):
    info = {
            "url": url or
                   "https://upload.wikimedia.org/wikipedia/commons/"
                   + title.replace("File:", "").replace(" ", "_"),
            "width": w, "height": h, "mime": mime,
            "descriptionurl": "https://commons.wikimedia.org/wiki/"
                              + title.replace(" ", "_"),
            "extmetadata": {
                "LicenseShortName": {"value": license_short},
                "UsageTerms": {"value": license_short},
                "ImageDescription": {"value": desc},
                "Categories": {"value": cats},
                "Artist": {"value": artist},
            },
    }
    if size is not None:
        info["size"] = size
    return {"title": title, "imageinfo": [info]}


RBI_PAGE = commons_page(
    "File:Reserve Bank of India headquarters Mumbai.jpg",
    3200, 2000,
    desc="The headquarters of the Reserve Bank of India in "
         "Mumbai, home of the Bank's first data centre.",
    cats="Reserve Bank of India|Buildings in Mumbai")
NAMESAKE_PAGE = commons_page(
    "File:Asha Parekh in 2018.jpg", 2400, 3000,
    desc="Asha Parekh at an event in Mumbai.",
    cats="Asha Parekh")
WILDLIFE_PAGE = commons_page(
    "File:Bay-breasted Warbler in Central Park.jpg", 3000, 2000,
    desc="A bay-breasted warbler photographed in Central Park.",
    cats="Setophaga castanea|Passeriformes of Central Park")
GFDL_PAGE = commons_page(
    "File:Reserve Bank of India old building.jpg", 2600, 1700,
    license_short="GFDL",
    desc="The Reserve Bank of India building.",
    cats="Reserve Bank of India")
SMALL_PAGE = commons_page(
    "File:Reserve Bank of India gate.jpg", 900, 600,
    desc="Gate of the Reserve Bank of India.",
    cats="Reserve Bank of India")


def stub_net(pages_by_query=None, cache=None, verify=None):
    pages_by_query = pages_by_query or {}
    calls = {"patch": []}

    def commons_search(q, limit=10):
        for key, pages in pages_by_query.items():
            if key.lower() in q.lower():
                return pages
        return []

    net = {
        "commons_search": commons_search,
        "commons_file_info": lambda title: None,
        "brave_links": lambda q, n=8: [],
        "fetch_text": lambda url, timeout=15: "",
        "verify_url": verify or (lambda url: {"ok": True,
                                              "width": 2400}),
        "person_cache": lambda name: (cache or {}).get(name),
        "download_verify": lambda url, dest: [2400, 1500],
    }
    return net, calls


def recording_patch(calls):
    def _patch(article_id, payload):
        calls["patch"].append((article_id, payload))
        return True
    return _patch


# ── entity extraction / ranking ─────────────────────────────────────
print("entity extraction")
ents = P.extract_article_entities(ARTICLE)
names = [e["name"] for e in ents]
check("category junk 'Nri World' rejected from image_entities",
      "Nri World" not in names)
check("sane image_entities entry kept",
      "Reserve Bank of India" in names)
check("headline-named entity present (Bhubaneswar)",
      "Bhubaneswar" in names)
check("headline entities rank before body-only entities",
      names.index("Bhubaneswar")
      < len(names))
check_eq("entity cap respected", len(ents) <= P.MAX_ENTITIES, True)
check_eq("sane check: None rejected",
         P._sane_image_entity(None), None)
check_eq("sane check: category label rejected",
         P._sane_image_entity("Nri World"), None)
check_eq("sane check: plain name kept",
         P._sane_image_entity("Infosys"), "Infosys")
no_ents = P.extract_article_entities(
    {"headline": "Markets steady on Tuesday",
     "body": "<p>Stocks were flat.</p>", "image_entities": None})
check_eq("article with no entities yields none", no_ents, [])

# ── hero classification ─────────────────────────────────────────────
print("hero classification")
check_eq("blocked -> skip-blocked",
         P.classify_hero({**ARTICLE, "image_backfill_blocked": True},
                         None)[0], "skip-blocked")
check_eq("null hero -> fill",
         P.classify_hero(ARTICLE, None)[0], "fill")
check_eq("pexels hero -> replace",
         P.classify_hero(
             {**ARTICLE,
              "image_url": "https://images.pexels.com/photos/1/x.jpg"},
             {"ok": True, "width": 2400})[0], "replace")
check_eq("generic root og hero -> replace",
         P.classify_hero(
             {**ARTICLE,
              "image_url": "https://example.com/og-image.jpg"},
             {"ok": True, "width": 2400})[0], "replace")
check_eq("broken hero -> replace",
         P.classify_hero(
             {**ARTICLE,
              "image_url": "https://cdn.example.com/dead.jpg"},
             {"ok": False, "width": 0})[0], "replace")
check_eq("below-site-floor hero -> replace",
         P.classify_hero(
             {**ARTICLE,
              "image_url": "https://cdn.example.com/small.jpg"},
             {"ok": True, "width": 640})[0], "replace")
check_eq("verified hero -> keep",
         P.classify_hero(
             {**ARTICLE,
              "image_url": "https://upload.wikimedia.org/x.jpg"},
             {"ok": True, "width": 1600})[0], "keep")

print("never-downgrade floor")
check_eq("no current -> accept floor",
         P.hero_width_floor(None), P.HERO_MIN_W)
check_eq("2400px current -> capped at preferred",
         P.hero_width_floor(2400), P.HERO_PREF_W)
check_eq("1300px current -> replacement must be >= 1300",
         P.hero_width_floor(1300), 1300)

# ── candidate gates ─────────────────────────────────────────────────
print("candidate gates")
cand, row = P.evaluate_article_candidate(
    RBI_PAGE, "Reserve Bank of India", "A — test",
    P.HERO_MIN_W, P.HERO_MIN_H)
check("clean CC Commons file accepted", cand is not None)
check("attribution recorded",
      bool(cand and "Wikimedia Commons" in cand["attribution"]))
check("provenance fields present",
      bool(cand and cand["source_page"] and cand["license"]
           and cand["verification"]))
cand, row = P.evaluate_article_candidate(
    GFDL_PAGE, "Reserve Bank of India", "A — test",
    P.HERO_MIN_W, P.HERO_MIN_H)
check("GFDL rejected on license", cand is None
      and "license" in row["reason"])
cand, row = P.evaluate_article_candidate(
    SMALL_PAGE, "Reserve Bank of India", "A — test",
    P.HERO_MIN_W, P.HERO_MIN_H)
check("below-floor resolution rejected", cand is None
      and "resolution" in row["reason"])
cand, row = P.evaluate_article_candidate(
    NAMESAKE_PAGE, "Salil Parekh", "A — test", 800, 450)
check("namesake rejected on identity (Asha != Salil Parekh)",
      cand is None and "identity" in row["reason"])
cand, row = P.evaluate_article_candidate(
    WILDLIFE_PAGE, "Central Park", "A — test", 800, 450)
check("wildlife-at-the-place rejected (not a picture OF it)",
      cand is None)

# ── inline counting + placement ─────────────────────────────────────
print("inline placement")
check_eq("no figures counted in plain body",
         P.count_inline_figures(BODY), 0)
fig = ('<figure style="margin:28px auto;text-align:center">'
       '<img src="https://x/y.jpg"></figure>')
check_eq("html figures counted",
         P.count_inline_figures(BODY + fig + fig), 2)
picks = [("Reserve Bank of India",
          "https://upload.wikimedia.org/rbi.jpg",
          "Reserve Bank of India headquarters in Mumbai. "
          "The bank opened its Bhubaneswar centre on Sunday."),
         ("Bhubaneswar", "https://upload.wikimedia.org/bbsr.jpg",
          "Bhubaneswar. The inauguration took place in "
          "Bhubaneswar.")]
new_body = P.propose_body_with_inlines(BODY, picks)
check("figures inserted", new_body.count("<figure") == 2)
first_fig = new_body.index("<figure")
check("no figure before the first paragraph close",
      first_fig > new_body.index("</p>"))
check("no figure inside the key-takeaways intro block",
      first_fig > new_body.index("</div>"))
pos = [m for m in range(len(new_body))
       if new_body.startswith("<figure", m)]
check("figures not clustered (spread > 200 chars apart)",
      len(pos) == 2 and pos[1] - pos[0] > 200)
check("enricher figure format used (figcaption present)",
      "<figcaption" in new_body)

# ── full pass with stubbed network ──────────────────────────────────
print("process_article (dry-run)")
net, calls = stub_net(pages_by_query={"Reserve Bank of India":
                                      [RBI_PAGE]})
rec = P.process_article(ARTICLE, net=net, apply=False,
                        patch_fn=recording_patch(calls),
                        log=lambda *a: None)
check_eq("dry-run invoked the patch function ZERO times",
         len(calls["patch"]), 0)
check("hero fill proposed", rec["hero"]["action"] == "fill"
      and rec["hero"]["proposed"] is not None)
prov = rec["hero"]["proposed"] or {}
check("hero provenance complete",
      all(prov.get(k) for k in
          ("entity", "file_url", "source_page", "license",
           "attribution", "resolution", "verified_how")))
check("hero caption is two sentences or fewer",
      (rec["hero"].get("caption") or "").count(". ") <= 1)
check_eq("nothing applied in dry-run", rec["applied"], [])

print("process_article (backfill-blocked skip)")
blocked_art = {**ARTICLE, "image_backfill_blocked": True,
               "image_url": None}
sourcing_calls = []
net2, calls2 = stub_net()
net2["commons_search"] = lambda q, limit=10: (
    sourcing_calls.append(q), [])[1]
net2["verify_url"] = lambda url: (
    sourcing_calls.append(url), {"ok": True, "width": 10})[1]
rec2 = P.process_article(blocked_art, net=net2, apply=False,
                         patch_fn=recording_patch(calls2),
                         log=lambda *a: None)
check_eq("blocked article action is skip-blocked",
         rec2["hero"]["action"], "skip-blocked")
check_eq("blocked article: zero sourcing/probe calls",
         len(sourcing_calls), 0)
check_eq("blocked article: zero patches", len(calls2["patch"]), 0)

print("process_article (verified hero kept, inlines gated)")
rich = {**ARTICLE,
        "image_url": "https://upload.wikimedia.org/hero.jpg",
        "body": BODY + fig + fig}
net3, calls3 = stub_net()
rec3 = P.process_article(rich, net=net3, apply=False,
                         patch_fn=recording_patch(calls3),
                         log=lambda *a: None)
check_eq("verified hero kept", rec3["hero"]["action"], "keep")
check_eq("no hero proposal for a kept hero",
         rec3["hero"]["proposed"], None)
check_eq("2 existing figures -> no inline proposals",
         len(rec3["inlines"]["proposed"]), 0)

print("process_article (apply path uses the patch fn)")
net4, calls4 = stub_net(pages_by_query={"Reserve Bank of India":
                                        [RBI_PAGE]})
rec4 = P.process_article(ARTICLE, net=net4, apply=True,
                         patch_fn=recording_patch(calls4),
                         log=lambda *a: None)
check("apply mode patches the hero",
      any("image_url" in payload
          for _id, payload in calls4["patch"]))
check_eq("apply recorded", "hero" in rec4["applied"], True)

# ── run_pass dry-run contract ───────────────────────────────────────
print("run_pass dry-run contract")
net5, calls5 = stub_net(pages_by_query={"Reserve Bank of India":
                                        [RBI_PAGE]})
with tempfile.TemporaryDirectory() as td:
    rp = Path(td) / "report.json"
    hp = Path(td) / "report.html"
    report = P.run_pass(apply=False, net=net5,
                        patch_fn=recording_patch(calls5),
                        articles=[ARTICLE], log=lambda *a: None,
                        report_path=rp, html_path=hp)
    check("report JSON written", rp.exists())
    data = json.loads(rp.read_text())
    check_eq("report mode is dry-run", data["mode"], "dry-run")
    check_eq("summary counts the scanned article",
             data["summary"]["articles_scanned"], 1)
    check("review HTML written with before/after",
          hp.exists() and "BEFORE" in hp.read_text()
          and "PROPOSED" in hp.read_text())
check_eq("run_pass dry-run: zero patches overall",
         len(calls5["patch"]), 0)

# ── regression: 2026-10-25 validation-run failure modes ────────────
# Junk entities from headline/body extraction won hero slots:
# 'Coming Weeks' -> an NYC subway photo on an Aamir Khan story;
# 'Mann' -> a Mrs. Mann golf photo on the Mann Ki Baat story;
# 'American' -> a bison on a teen's yoga story; 'Host' -> a TV
# host's portrait on a restaurant story. The guards below are
# the fixes.
print("validation-run regressions")
KHAN = {
    "headline": "Aamir Khan Expects Final 3 Idiots Sequel Script "
                "Narration in Coming Weeks",
    "body": "<p>Aamir Khan said the final narration is expected "
            "in coming weeks. Aamir Khan spoke about the sequel "
            "and Rajkumar Hirani. Rajkumar Hirani directs.</p>",
    "image_entities": None,
}
khan_names = [e["name"] for e in P.extract_article_entities(KHAN)]
check("'Coming Weeks' not an entity (case-sensitive body repeat)",
      "Coming Weeks" not in khan_names)
check("full name 'Aamir Khan' extracted", "Aamir Khan" in khan_names)
check("fragment 'Aamir' suppressed by the full name",
      "Aamir" not in khan_names)
MANN = {
    "headline": "Modi Urges 'Vocal for Local' Festive Buying in "
                "139th Mann Ki Baat",
    "body": "<p>In Mann Ki Baat, the Prime Minister spoke. "
            "Mann Ki Baat reaches millions. Vocal for Local was "
            "the theme, and Vocal for Local matters.</p>",
    "image_entities": None,
}
mann_ents = P.extract_article_entities(MANN)
mann_names = [e["name"] for e in mann_ents]
check("'Mann Ki Baat' extracted as one entity",
      "Mann Ki Baat" in mann_names)
check("fragment 'Mann' suppressed", "Mann" not in mann_names)
check("fragment 'Baat' suppressed", "Baat" not in mann_names)
single = [e for e in P.extract_article_entities(
    {"headline": "Yoga Day Marked in Virginia",
     "body": "<p>Yoga practitioners gathered in Virginia. "
             "Virginia residents joined the Yoga session.</p>",
     "image_entities": None})]
check("single-token headline entity is marked not sourceable",
      all(not e["sourceable"] for e in single
          if len(e["name"].split()) == 1))
curated = P.extract_article_entities(
    {"headline": "Infosys Results Beat Street Estimates",
     "body": "<p>Infosys reported. Infosys gained.</p>",
     "image_entities": ["Infosys"]})
infosys = [e for e in curated if e["name"] == "Infosys"]
check("curated image_entities single token stays sourceable",
      bool(infosys) and infosys[0]["sourceable"])

net_ns, _c = stub_net(pages_by_query={"Reserve": [RBI_PAGE]})
frag_rec = {"name": "Host", "kind": "org/place",
            "source": "headline", "sourceable": False}
cands_ns, rows_ns = P.source_entity_images(
    frag_rec, ARTICLE, "", net_ns, 800, 450)
check_eq("non-sourceable entity yields no candidates",
         cands_ns, [])
check("non-sourceable rejection is ledgered",
      any("not identity proof" in r.get("reason", "")
          for r in rows_ns))

print("hero rank-first + aspect gate")
LAND_PAGE = commons_page(
    "File:Reserve Bank of India headquarters Mumbai.jpg",
    3200, 2000, desc="The headquarters of the Reserve Bank of "
    "India in Mumbai, home of the Bank's first data centre.",
    cats="Reserve Bank of India")
WIDE_PAGE = commons_page(
    "File:Bhubaneswar skyline panorama.jpg", 6000, 3000,
    desc="Panorama of Bhubaneswar, capital of Odisha, looking "
         "towards the new data centre.",
    cats="Bhubaneswar")
PORTRAIT_PAGE = commons_page(
    "File:Reserve Bank of India governor portrait.jpg", 1300,
    2000, desc="Portrait at the Reserve Bank of India data "
               "centre in Bhubaneswar.",
    cats="Reserve Bank of India")
net_rf, _c = stub_net(pages_by_query={
    "Reserve Bank of India": [LAND_PAGE],
    "Bhubaneswar": [WIDE_PAGE]})
two_ents = [
    {"name": "Reserve Bank of India", "kind": "org/place",
     "source": "headline", "sourceable": True},
    {"name": "Bhubaneswar", "kind": "org/place",
     "source": "headline", "sourceable": True},
]
rec_rf = {"ledger": [], "notes": []}
pick = P._source_hero(ARTICLE, two_ents, "", net_rf, 1200, set(),
                      rec_rf, lambda *a: None)
check("rank-first: headline entity's 3200w beats later 6000w",
      pick is not None
      and pick["entity"] == "Reserve Bank of India")
net_ap, _c = stub_net(pages_by_query={
    "Reserve Bank of India": [PORTRAIT_PAGE],
    "Bhubaneswar": [WIDE_PAGE]})
rec_ap = {"ledger": [], "notes": []}
pick2 = P._source_hero(ARTICLE, two_ents, "", net_ap, 1200, set(),
                       rec_ap, lambda *a: None)
check("portrait-orientation hero rejected, falls to next entity",
      pick2 is not None and pick2["entity"] == "Bhubaneswar")
check("aspect rejection ledgered",
      any("portrait orientation" in r.get("reason", "")
          for r in rec_ap["ledger"]))

# ── regression round 2: namesake topicality (validation run 2) ─────
# Exact-token identity is not topicality: Gibraltar's Main Street
# illustrated Disney World, the RUSSIAN White House illustrated
# US midterms, a Christmas tree illustrated Diwali — and
# headline-ese fragments ('Kid Again', 'Feels Like') sourced
# literal junk. The topicality gate + phrase denylist are the
# fixes.
print("topicality gate + headline-ese fragments")
OBAMA = {
    "headline": "Obama Warns Trump on Detroit and Cleveland "
                "Midterms",
    "body": "<p>Barack Obama spoke in Detroit. Obama addressed "
            "the midterms and the Detroit crowd.</p>",
    "image_entities": None,
}
RUSSIAN_WH_PAGE = commons_page(
    "File:Russian White House and ships on Moskva River.jpg",
    4488, 2970,
    desc="The Russian White House in Moscow, across the Moskva "
         "River.",
    cats="White House (Moscow)")
wh_hints = P._story_hint_terms(OBAMA, "White House")
check("hint terms exclude the entity's own tokens",
      "white" not in wh_hints and "house" not in wh_hints
      and "detroit" in wh_hints)
cand, row = P.evaluate_article_candidate(
    RUSSIAN_WH_PAGE, "White House", "A — test", 800, 450,
    hint_terms=wh_hints)
check("namesake building rejected on topicality", cand is None
      and "topicality" in row.get("reason", ""))
US_WH_PAGE = commons_page(
    "File:White House North Lawn in autumn.jpg", 4000, 2600,
    desc="The White House in Washington, photographed as voters "
         "weighed the midterms and the Trump agenda.",
    cats="White House")
cand, row = P.evaluate_article_candidate(
    US_WH_PAGE, "White House", "A — test", 800, 450,
    hint_terms=wh_hints)
check("on-topic same-name building accepted", cand is not None)
# Persons are exempt: an exact-name portrait with zero headline
# overlap in its evidence still sources.
MODI_PAGE = commons_page(
    "File:Narendra Modi addressing supporters.jpg", 2400, 1600,
    desc="Narendra Modi addressing supporters at a rally.",
    cats="Narendra Modi")
net_pm, _c = stub_net(pages_by_query={"Narendra Modi":
                                      [MODI_PAGE]})
modi_rec = {"name": "Narendra Modi", "kind": "person",
            "source": "headline", "sourceable": True}
cands_pm, _rows_pm = P.source_entity_images(
    modi_rec, ARTICLE, "", net_pm, 800, 450)
check("person exact-name pick exempt from topicality gate",
      len(cands_pm) == 1)
# Headline-ese fragments never become entities.
PARCEL = {
    "headline": "Diwali Parcel Makes Woman Abroad Feels Like "
                "a Kid Again",
    "body": "<p>She opened the parcel and felt like a Kid "
            "Again. The Kid Again feeling stayed all week, a "
            "real Kid Again moment.</p>",
    "image_entities": None,
}
parcel_names = [e["name"] for e in P.extract_article_entities(
    PARCEL)]
check("'Kid Again' fragment denied", "Kid Again" not in
      parcel_names)
check("'Feels Like' fragment denied", "Feels Like" not in
      parcel_names)
# Route B (official hosted) carries the same topicality gate.
_orig_hosted = P.RES.evaluate_hosted_page


def _fake_hosted(subject):
    def fake(link, entity, route, net):
        cand = {"entity": entity,
                "title": f"{subject} official photo",
                "file_url": "https://example.gov/x.jpg",
                "size": [3000, 2000], "source_page": link,
                "license": "Public domain", "artist": "",
                "subject": subject, "role": "scene",
                "route": route, "verification": "stub",
                "attribution": "Official source"}
        return cand, {"candidate": cand["title"], "route": route,
                      "entity": entity, "verdict": "accepted",
                      "reason": "stub accept"}
    return fake


rbi_rec = {"name": "Reserve Bank of India", "kind": "org/place",
           "source": "headline", "sourceable": True}
net_b, _c = stub_net()
net_b["brave_links"] = lambda q, n=8: (
    ["https://example.gov/news/story"]
    if "official" in q else [])
try:
    P.RES.evaluate_hosted_page = _fake_hosted("Moscow skyline")
    cands_b, rows_b = P.source_entity_images(
        rbi_rec, ARTICLE, "", net_b, 800, 450)
    check("route B off-topic hosted image rejected",
          cands_b == [] and any(
              "topicality" in r.get("reason", "")
              for r in rows_b))
    check("route B rejection leaves no false 'accepted' row",
          not any(r.get("verdict") == "accepted"
                  and "stub" in r.get("reason", "")
                  for r in rows_b))
    P.RES.evaluate_hosted_page = _fake_hosted(
        "Bhubaneswar data centre")
    cands_b2, _rows_b2 = P.source_entity_images(
        rbi_rec, ARTICLE, "", net_b, 800, 450)
    check("route B on-topic hosted image accepted",
          len(cands_b2) == 1)
finally:
    P.RES.evaluate_hosted_page = _orig_hosted

# ── regression round 3: kind markers + two-term threshold ────────────
# Run 3 still proposed Gibraltar's Main Street and Moscow's White
# House: both had been classified 'person' (any two Title Case
# words read as a name), exempting them from the gate; and a
# Christmas tree passed the Diwali gate on the word 'where'.
print("kind markers + topicality threshold")
KIND_ART = {
    "headline": "Obama Warns Trump on Detroit and Cleveland "
                "Midterms",
    "body": "<p>Officials at the White House responded on "
            "Sunday. Crowds filled Main Street in Detroit, and "
            "the White House spoke again as Main Street "
            "cheered. Narendra Modi was mentioned by officials. "
            "Narendra Modi trended online through the day.</p>",
    "image_entities": None,
}
kind_by_name = {e["name"]: e["kind"]
                for e in P.extract_article_entities(KIND_ART)}
check("'Main Street' is org/place, not a person",
      kind_by_name.get("Main Street") == "org/place")
check("'White House' is org/place, not a person",
      kind_by_name.get("White House") == "org/place")
check("a real person's name stays 'person'",
      kind_by_name.get("Narendra Modi") == "person")
UAE_ART = {
    "headline": "Diwali 2026 in the UAE: Fireworks, Festivals, "
                "Temples and Where to Celebrate",
    "body": "<p>Diwali celebrations across the Emirates.</p>",
    "image_entities": None,
}
uae_hints = P._story_hint_terms(UAE_ART, "Festival of Lights")
check("function word 'where' is not a hint term",
      "where" not in uae_hints)
check("pure-number token '2026' is not a hint term",
      "2026" not in uae_hints)
ONE_TERM_PAGE = commons_page(
    "File:Festival of Lights celebration.jpg", 3000, 2000,
    desc="Fireworks over the harbour at night.",
    cats="Festival of Lights")
cand, row = P.evaluate_article_candidate(
    ONE_TERM_PAGE, "Festival of Lights", "A — test", 800, 450,
    hint_terms=uae_hints)
check("one-term topical overlap is not enough", cand is None
      and "topicality" in row.get("reason", ""))
TWO_TERM_PAGE = commons_page(
    "File:Festival of Lights celebration.jpg", 3000, 2000,
    desc="Fireworks light the temples at night.",
    cats="Festival of Lights")
cand, row = P.evaluate_article_candidate(
    TWO_TERM_PAGE, "Festival of Lights", "A — test", 800, 450,
    hint_terms=uae_hints)
check("two-term topical overlap accepted", cand is not None)

# ── regression round 4: the first LIVE run (2026-10-25 10:15 PT) ────
# Step 0.25's first apply run shipped four junk inlines plus a map
# hero and a ~105 MB hero. Every fixture below is modeled on the
# actual Commons evidence that fooled the gates (fetched from the
# live file pages during remediation).
print("live-run regressions: subject position, fragments, "
      "portraits, maps, serve size")

# (1) 'Class XII' -> the Louis XII wing at Blois. The tokens
# matched scattered: 'xii' from the king's name, 'class' from the
# French 'classé' in the heritage description.
check("'Class XII' is a fragment entity",
      P._is_fragment_entity("Class XII"))
check("'Grade 10' is a fragment entity",
      P._is_fragment_entity("Grade 10"))
check("'World Weightlifting Championships' is not a fragment",
      not P._is_fragment_entity(
          "World Weightlifting Championships"))
check("'Reserve Bank of India' is not a fragment",
      not P._is_fragment_entity("Reserve Bank of India"))
SALEM_ART = {
    "headline": "Salem Records 97.28 Percent Class XII Higher "
                "Education Enrolment",
    "body": "<p>Salem district recorded the rise in Class XII "
            "enrolment. Class XII students led the state.</p>",
    "image_entities": ["Class XII", "Tamil Nadu"],
}
salem_by_name = {e["name"]: e
                 for e in P.extract_article_entities(SALEM_ART)}
check("extracted 'Class XII' is recorded but never sourceable",
      salem_by_name.get("Class XII", {}).get("sourceable")
      is False)
BLOIS_PAGE = commons_page(
    "File:Louis XII wing of the castle of Blois 01.jpg",
    4907, 2908,
    desc="Louis XII wing of the castle of Blois, Loir-et-Cher, "
         "France. This building is classé au titre des "
         "monuments historiques de la France.",
    cats="Monuments historiques classés|Castles in France "
         "photographed in 2018|Louis XII wing")
cand, row = P.evaluate_article_candidate(
    BLOIS_PAGE, "Class XII", "A — test", 800, 450,
    entity_kind="org/place")
check("Louis XII castle rejected for 'Class XII'",
      cand is None and "subject" in row.get("reason", ""))

# (2) A crow photographed IN Tamil Nadu: the entity is only the
# location; the file's subject is the bird (binomial with a
# descriptor tail in the categories, and in the description).
CROW_PAGE = commons_page(
    "File:Crow in Tamil Nadu 01.jpg", 5472, 3648,
    desc="Crow (Corvus splendens) in Tamil Nadu",
    cats="Self-published work|Corvus splendens heads")
check("binomial-with-tail category marks a wildlife subject",
      P.RES.wildlife_subject("Tamil Nadu",
                             "Self-published work|"
                             "Corvus splendens heads"))
cand, row = P.evaluate_article_candidate(
    CROW_PAGE, "Tamil Nadu", "A — test", 800, 450,
    hint_terms=P._story_hint_terms(SALEM_ART, "Tamil Nadu"),
    entity_kind="org/place")
check("crow located in Tamil Nadu rejected for 'Tamil Nadu'",
      cand is None and "wildlife" in row.get("reason", ""))

# (3) A portrait of Bryan Traynor filed under Breakthrough Prize
# winners: a non-person entity cannot be illustrated by a posed
# portrait of an associated person.
TRAYNOR_PAGE = commons_page(
    "File:Bryan Traynor, 2026.jpg", 1128, 903,
    license_short="CC0 1.0",
    desc="Bryan Traynor, 2026",
    cats="CC-Zero|Winners of the Breakthrough Prize in Life "
         "Sciences|Portrait photographs of physicians")
SEN_ART = {
    "headline": "Who Is Ashoke Sen? The Kolkata Physicist Who "
                "Unified String Theory",
    "body": "<p>Ashoke Sen won the Breakthrough Prize.</p>",
    "image_entities": None,
}
cand, row = P.evaluate_article_candidate(
    TRAYNOR_PAGE, "Breakthrough Prize", "A — test", 800, 450,
    hint_terms=P._story_hint_terms(SEN_ART, "Breakthrough Prize"),
    entity_kind="org/place")
check("Traynor portrait rejected for 'Breakthrough Prize'",
      cand is None and ("portrait" in row.get("reason", "")
                        or "subject" in row.get("reason", "")))

# (4) Bangalore's Raj Bhavan (renamed Lok Bhavan) for Manipur's
# Lok Bhavan: the entity phrase lives only in a category; the
# title/description subject is an event at a namesake building
# in another city.
RAJ_BHAVAN_PAGE = commons_page(
    "File:Independence day at Raj Bhavan, Bangalore (2025) "
    "53.jpg", 4080, 3072,
    desc="Independence day at Raj Bhavan, Bangalore (2025)",
    cats="Self-published work|Flowers at Lok Bhavan, Bengaluru|"
         "Independence day at Raj Bhavan, Bengaluru (2025)")
MANIPUR_ART = {
    "headline": "Congress Demands Manipur CM Resignation, "
                "Fresh Polls",
    "body": "<p>The Congress party demanded fresh polls in "
            "Manipur on Sunday.</p>",
    "image_entities": None,
}
cand, row = P.evaluate_article_candidate(
    RAJ_BHAVAN_PAGE, "Lok Bhavan", "A — test", 800, 450,
    hint_terms=P._story_hint_terms(MANIPUR_ART, "Lok Bhavan"),
    entity_kind="org/place")
check("Bangalore Raj Bhavan rejected for Manipur's "
      "'Lok Bhavan'", cand is None
      and "subject" in row.get("reason", ""))

# (5) The Cyclone hero slot took an OpenStreetMap mandals
# graphic: map markers live in the categories, which the old
# subject_denied never read.
MANDALS_PAGE = commons_page(
    "File:Andhra Pradesh Mandals-Telugu.png", 1920, 1046,
    mime="image/png",
    desc="Screenshot of the Query for a selected area (Query "
         "link http://overpass-turbo.eu/s/NWB )",
    cats="Self-published work|ODbL OpenStreetMap|OpenStreetMap "
         "maps of Andhra Pradesh|Mandals of Andhra Pradesh")
cand, row = P.evaluate_article_candidate(
    MANDALS_PAGE, "Andhra Pradesh", "A — test", 1200, 500,
    entity_kind="org/place")
check("OSM mandals graphic rejected as a map file",
      cand is None and "map/graphic" in row.get("reason", ""))

# (6) Keepers from the same run must still pass: an athlete AT
# the named championships, an opening ceremony OF the named
# Games, and a person's own exact-name portrait.
FUENTES_PAGE = commons_page(
    "File:Aremi Fuentes Zavala (born 1993) at the 2019 World "
    "Weightlifting Championships, Women's 76 kg.png",
    801, 603, mime="image/png", license_short="CC BY 3.0",
    desc="Aremi Fuentes Zavala at the 2019 World "
         "Weightlifting Championships.",
    cats="Aremi Fuentes Zavala|2019 World Weightlifting "
         "Championships")
cand, row = P.evaluate_article_candidate(
    FUENTES_PAGE, "World Weightlifting Championships",
    "A — test", 800, 450, entity_kind="org/place")
check("athlete at the named championships accepted",
      cand is not None, row.get("reason", ""))
BIRMINGHAM_PAGE = commons_page(
    "File:Birmingham 2022 Opening Ceremony.jpg", 4032, 3024,
    desc="Alexander Stadium at the opening ceremony to "
         "Birmingham 2022 Commonwealth Games.",
    cats="Birmingham 2022 Commonwealth Games|Alexander Stadium")
cand, row = P.evaluate_article_candidate(
    BIRMINGHAM_PAGE, "Commonwealth Games", "A — test", 800, 450,
    entity_kind="org/place")
check("opening ceremony of the named Games accepted",
      cand is not None, row.get("reason", ""))
SEN_PAGE = commons_page(
    "File:Dr. Ashoke Sen at Scottish Church College.jpg",
    1600, 1200,
    desc="Dr. Ashoke Sen at Scottish Church College.",
    cats="Ashoke Sen")
cand, row = P.evaluate_article_candidate(
    SEN_PAGE, "Ashoke Sen", "A — test", 800, 450,
    entity_kind="person")
check("person's own portrait accepted", cand is not None,
      row.get("reason", ""))

# (7) Serve-size gate (the ~105 MB Cyclone hero): an oversized
# Wikimedia original is served via its 1920px variant; an
# oversized file with no derivable variant is rejected.
CYCLONE_BIG_PAGE = commons_page(
    "File:Cyclone Mocha satellite view.jpg", 6000, 6000,
    desc="Satellite view of Cyclone Mocha over the Bay of "
         "Bengal.",
    cats="Cyclone Mocha",
    url="https://upload.wikimedia.org/wikipedia/commons/2/29/"
        "Cyclone_Mocha_satellite.jpg",
    size=109_822_325)
cand, row = P.evaluate_article_candidate(
    CYCLONE_BIG_PAGE, "Bay of Bengal", "A — test", 1200, 500,
    entity_kind="org/place")
check("oversized original served via its 1920px variant",
      cand is not None
      and cand["file_url"] ==
      "https://upload.wikimedia.org/wikipedia/commons/thumb/"
      "2/29/Cyclone_Mocha_satellite.jpg/1920px-"
      "Cyclone_Mocha_satellite.jpg"
      and cand["size"] == [1920, 1920],
      row.get("reason", ""))
HUGE_FOREIGN_PAGE = commons_page(
    "File:Bay of Bengal storm surge.jpg", 6000, 4000,
    desc="Storm surge along the Bay of Bengal coast.",
    cats="Bay of Bengal",
    url="https://cdn.example.com/huge.jpg", size=50_000_000)
cand, row = P.evaluate_article_candidate(
    HUGE_FOREIGN_PAGE, "Bay of Bengal", "A — test", 1200, 500,
    entity_kind="org/place")
check("oversized file with no host variant is flagged for "
      "self-compression, not rejected (compress-and-keep)",
      cand is not None
      and cand.get("oversize_original") == 50_000_000
      and cand.get("needs_dims_check") is True
      and cand["file_url"] == "https://cdn.example.com/huge.jpg",
      row.get("reason", ""))

# Compress-and-keep path 2 at verify time: the flagged pick is
# downloaded, resized to <=1920px, JPEG-compressed and uploaded
# to Supabase Storage; the served URL is the stored one, with
# the provenance noting the self-compression.
from PIL import Image as _PILImage
_uploads = {}


def _fake_download(url, dest):
    img = _PILImage.effect_noise((2400, 1600), 64).convert("RGB")
    img.save(dest, format="JPEG", quality=95)
    return [2400, 1600]


def _fake_upload(data, filename):
    _uploads[filename] = data
    return ("https://supabase.test/storage/v1/object/public/"
            "article-images/" + filename)


_oversize_cand = {
    "entity": "Bay of Bengal",
    "title": "File:Bay of Bengal storm surge.jpg",
    "file_url": "https://cdn.example.com/huge.jpg",
    "size": [2400, 1600], "route": "A — Wikimedia Commons",
    "license": "CC BY-SA 4.0", "verification": "stub",
    "oversize_original": 50_000_000, "needs_dims_check": True,
}
_net_oversize = {"download_verify": _fake_download,
                 "verify_url": lambda u: {"ok": True},
                 "upload_image": _fake_upload}
with tempfile.TemporaryDirectory() as _td:
    got = P._verify_pick(dict(_oversize_cand), _net_oversize,
                         _td, "bay-of-bengal-story",
                         lambda *a: None, min_w=1200, min_h=500)
check("path 2: oversized pick self-compressed + self-hosted",
      got is not None
      and got["file_url"].startswith(
          "https://supabase.test/storage/v1/object/public/"
          "article-images/")
      and got["_verified_size"] == [1920, 1280]
      and got.get("self_compressed") is True
      and "self-compressed from original" in
      got["verification"])
_uploaded = next(iter(_uploads.values()), b"")
check("path 2: uploaded bytes are a JPEG under the budget",
      _uploaded[:2] == b"\xff\xd8"
      and 0 < len(_uploaded) <= P.MAX_SERVE_BYTES)
_net_upload_fails = {"download_verify": _fake_download,
                     "verify_url": lambda u: {"ok": True},
                     "upload_image": lambda d, f: None}
with tempfile.TemporaryDirectory() as _td:
    got = P._verify_pick(dict(_oversize_cand),
                         _net_upload_fails, _td,
                         "bay-of-bengal-story", lambda *a: None,
                         min_w=1200, min_h=500)
check("path 3: upload failure rejects the pick", got is None)

# (7a) Indian state names are places, not persons: as
# 'persons' they were exempt from topicality/subject gates.
salem_kinds = {e["name"]: e["kind"]
               for e in P.extract_article_entities(SALEM_ART)}
check("'Tamil Nadu' extracts as org/place, not person",
      salem_kinds.get("Tamil Nadu") == "org/place")
CYCLONE_ENTS = {e["name"]: e["kind"] for e in
                P.extract_article_entities({
                    "headline": "Cyclone Arnab Red Alert in "
                                "Odisha, Andhra Pradesh Braces",
                    "body": "<p>Andhra Pradesh braced for the "
                            "cyclone. Andhra Pradesh officials "
                            "met on Sunday.</p>",
                    "image_entities": None})}
check("'Andhra Pradesh' extracts as org/place, not person",
      CYCLONE_ENTS.get("Andhra Pradesh") == "org/place")

# (7b) A worker photographed IN a place is not a picture OF
# the place: the entity phrase sits in the description's
# trailing location phrase (found by the post-hardening live
# dry-run, which proposed this for the same Salem article).
SILK_PAGE = commons_page(
    "File:Silk dyeing in Kumbakonam.jpg", 4000, 3000,
    desc="A man dyeing silk red in boiling water in "
         "Kumbakonam, Tamil Nadu.",
    cats="Silk dyeing|Kumbakonam")
cand, row = P.evaluate_article_candidate(
    SILK_PAGE, "Tamil Nadu", "A — test", 800, 450,
    entity_kind="org/place")
check("silk worker located in Tamil Nadu rejected",
      cand is None and "subject" in row.get("reason", ""))

# (7c) The reviewer's Cyclone hero — a captioned Wikimedia
# satellite GIF, served as the 1920px thumb — is a verified
# hero, never a 'generic og image' replacement target (the
# og-scrape heuristic blanket-rejects .gif).
CYCLONE_ART = {**ARTICLE,
               "image_url": "https://upload.wikimedia.org/"
               "wikipedia/commons/thumb/2/29/Cyclone_Mocha_"
               "Forms_in_Bay_of_Bengal_labels.gif/1920px-"
               "Cyclone_Mocha_Forms_in_Bay_of_Bengal_"
               "labels.gif"}
check_eq("Wikimedia GIF hero is kept, not 'generic'",
         P.classify_hero(CYCLONE_ART,
                         {"ok": True, "width": 1920})[0],
         "keep")

# (8) Topicality is whole-token now: 'sale' must not match
# 'Salem' as a substring of the evidence.
PORT_PAGE = commons_page(
    "File:Chennai Port at dawn.jpg", 3000, 2000,
    desc="Ships at the port of Chennai, near Salem.",
    cats="Chennai Port")
cand, row = P.evaluate_article_candidate(
    PORT_PAGE, "Chennai Port", "A — test", 800, 450,
    hint_terms=frozenset({"sale"}), entity_kind="org/place")
check("topicality: substring 'sale' in 'Salem' does not count",
      cand is None and "topicality" in row.get("reason", ""))

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
