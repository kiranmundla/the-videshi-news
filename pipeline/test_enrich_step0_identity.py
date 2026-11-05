#!/usr/bin/env python3
"""
test_enrich_step0_identity.py — regression corpus for the
2026-11-04 closure of the LAST open-search inline route:
enrich-articles.py Step 0 `find_inline_images` (Kiran's go,
2026-11-04; the same identity-only treatment as social cards
1ed2bf866 and picture-pass inlines e2477cc9e).

The deleted route extracted GPT "visual topics" from an
article and searched Wikimedia Commons by topic string. A
topic is not identity, and reviewers stripped ~24 wrong
inlines it produced across Nov 3-4 alone. Step 0 now sources
ONLY through article_picture_pass's identity path (verified
person_images cache -> the resolved entity's P18 -> its
depicts (P180) files through the shared evaluator + corpus
blocklist + place locality gate), via the real
extract_article_entities + _source_inlines machinery — this
suite drives find_inline_images end to end.

The corpus replays the route's own worst outputs:
  * the Dutch farm-wagon watercolor (Rijksmuseum drawing,
    RP-T-1952-254) inserted into Google stories THREE times
    (Dreambeans, then the Google exit-offers article);
  * the 1690 "Le Cheval rayé / Tenture des Indes" tapestry
    on the Indian-American voters story (climbed on "Indes");
  * a Fort Bragg, CALIFORNIA food-bank photo inside the
    Montville, NEW JERSEY food pantry story;
  * the Election_day.svg choropleth on a midterms story;
  * the 2026-10-13 "Chelsea 3" incident (vessel topic ->
    Chelsea Clinton photo) that the retired type-gate suite
    guarded — under identity sourcing the vessel's name is
    not even an extractable entity and the Clinton file is
    unreachable.
Plus keepers from test_inline_identity_sourcing.py's corpus
(Rishabh Pant's P18, the genuine Palestine Action protest
photo, a genuine New Jersey pantry photo) that must still
source through the new Step 0 path.

Every wrong case must produce NO inline. The search seams are
rigged to raise: if Step 0 ever consults open search again,
this suite fails loudly. All network is stubbed. Run:
  python3 test_enrich_step0_identity.py  (exit 0 = all pass)
"""
import os
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
mod = SourceFileLoader(
    "enrich_articles",
    str(_HERE / "enrich-articles.py")).load_module()

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(name, got == want, f"got {got!r}, want {want!r}")


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


def identity_net(resolutions=None, depicts_by_qid=None,
                 pages_by_title=None, items_by_qid=None,
                 cache=None):
    """A net whose ONLY sourcing seams are the identity ones.
    The search seams raise — Step 0 must never consult them."""
    calls = {"search": [], "resolve": [], "file_info": []}

    def _boom_search(q, limit=10):
        calls["search"].append(q)
        raise AssertionError(
            "open Commons search consulted by Step 0")

    def _boom_brave(q, n=8):
        calls["search"].append(q)
        raise AssertionError(
            "Brave discovery consulted by Step 0")

    def resolve(name, context=""):
        calls["resolve"].append(name)
        return (resolutions or {}).get(name)

    def file_info(title):
        calls["file_info"].append(title)
        return (pages_by_title or {}).get(title)

    net = {
        "commons_search": _boom_search,
        "brave_links": _boom_brave,
        "fetch_text": lambda url, timeout=15: "",
        "commons_file_info": file_info,
        "verify_url": lambda url: {"ok": True, "width": 2400},
        "person_cache": lambda name: (cache or {}).get(name),
        "download_verify": lambda url, dest: [2400, 1500],
        "resolve_entity": resolve,
        "depicts": lambda qid, limit=10:
            (depicts_by_qid or {}).get(qid, []),
        "wikidata_item": lambda qid: (items_by_qid or {}).get(qid),
    }
    return net, calls


def resolution(name, qid, type_="other", method="registry",
               p18=None, blocked=(), aliases=(),
               confidence="high", notes="", description=None):
    r = {"name": name, "aliases": list(aliases), "qid": qid,
         "p18_file": p18, "type": type_, "method": method,
         "confidence": confidence, "blocked_files": list(blocked),
         "notes": notes}
    if description:
        r["description"] = description
    return r


def step0(article, net):
    return mod.find_inline_images(
        article["headline"], article["body"],
        article.get("image_url", ""),
        category=article.get("category"), net=net)


# ── structural: the open-search route is gone, not bypassed ──────
print("route deletion")
check("GPT topic extractor is deleted",
      not hasattr(mod, "_extract_inline_visual_topics"))
check("entity-type gate (search-pool police) is deleted",
      not hasattr(mod, "_inline_type_gate"))
check("no Commons search call remains inside find_inline_images",
      "search_wikimedia_commons" not in
      mod.find_inline_images.__code__.co_names)

# ── the farm-wagon watercolor (Google stories, x3) ───────────────
print("2026-11-03/04 corpus — Boerenwagen watercolor")
WAGON = ("File:Boerenwagen, van achteren gezien, "
         "RP-T-1952-254.jpg")
WAGON_PAGE = commons_page(
    WAGON, 2400, 1600, license_short="CC0",
    desc="Identificatie Titel(s): Boerenwagen, van achteren "
         "gezien Objecttype: tekening aquarel Objectnummer: "
         "RP-T-1952-254 Vervaardiging Vervaardiger: tekenaar: "
         "Simon Andreas Krausz Datering: 1770 - 1825",
    cats="Simon Andreas Krausz|Farm wagons|"
         "Rijksmuseum collection",
    artist="Simon Andreas Krausz")
GOOGLE_ART = {
    "headline": "Google DeepMind Staff Offered Voluntary "
                "Exit Packages",
    "body": "<p>Google DeepMind offered voluntary exit "
            "packages to some staff on Tuesday. Google "
            "DeepMind confirmed the offers, the third such "
            "programme this year.</p>",
    "category": "technology", "slug": "google-exit-offers",
}
GDM_RES = resolution("Google DeepMind", "Q-TEST-GDM",
                     type_="company",
                     blocked=["Boerenwagen, van achteren "
                              "gezien, RP-T-1952-254.jpg"])
net, calls = identity_net(
    resolutions={"Google DeepMind": GDM_RES},
    depicts_by_qid={"Q-TEST-GDM": [{"title": WAGON}]},
    pages_by_title={WAGON: WAGON_PAGE})
res = step0(GOOGLE_ART, net)
check_eq("wagon offered as depicts + corpus blocklist -> "
         "NO inline", res, [])

net, calls = identity_net(
    resolutions={"Google DeepMind": resolution(
        "Google DeepMind", "Q-TEST-GDM", type_="company")},
    depicts_by_qid={"Q-TEST-GDM": [{"title": WAGON}]},
    pages_by_title={WAGON: WAGON_PAGE})
res = step0(GOOGLE_ART, net)
check_eq("wagon offered as depicts with the blocklist "
         "bypassed -> still NO inline (evaluator rejects "
         "the drawing's own evidence)", res, [])

net, calls = identity_net(
    resolutions={"Google DeepMind": GDM_RES},
    depicts_by_qid={"Q-TEST-GDM": []},
    pages_by_title={})
res = step0(GOOGLE_ART, net)
check_eq("clean depicts set -> NO inline, and the wagon "
         "file was never read", res, [])
check("the wagon never reached the file reader",
      WAGON not in calls["file_info"], str(calls["file_info"]))

# ── the 1690 tapestry (Indian-American voters) ───────────────────
print("2026-11-03 corpus — Tenture des Indes tapestry")
TAPESTRY = "File:Le Cheval rayé - Tenture des Indes.jpg"
TAPESTRY_PAGE = commons_page(
    TAPESTRY, 2400, 1800,
    desc="Le Cheval rayé (The Striped Horse), tapestry from "
         "the Tenture des Indes series, woven at the "
         "Gobelins manufactory, c. 1690, after designs from "
         "Dutch Brazil.",
    cats="Tenture des Indes|Gobelins tapestries|Zebras in art")
VOTERS_ART = {
    "headline": "Midterm Elections: Indian Americans Emerge "
                "as a Decisive Voting Bloc",
    "body": "<p>Indian Americans turned out in record "
            "numbers on Tuesday. Campaigns courted Indian "
            "Americans in swing districts across three "
            "states, and Indian Americans could decide "
            "several close races.</p>",
    "category": "news", "slug": "indian-american-voters",
}
net, calls = identity_net(
    resolutions={"Indian Americans": resolution(
        "Indian Americans", "Q-TEST-IA", type_="other",
        blocked=["Le Cheval rayé - Tenture des Indes.jpg"])},
    depicts_by_qid={"Q-TEST-IA": [{"title": TAPESTRY}]},
    pages_by_title={TAPESTRY: TAPESTRY_PAGE})
res = step0(VOTERS_ART, net)
check_eq("tapestry offered as depicts + corpus blocklist "
         "-> NO inline", res, [])

net, calls = identity_net(
    resolutions={"Indian Americans": resolution(
        "Indian Americans", "Q-TEST-IA", type_="other")},
    depicts_by_qid={"Q-TEST-IA": [{"title": TAPESTRY}]},
    pages_by_title={TAPESTRY: TAPESTRY_PAGE})
res = step0(VOTERS_ART, net)
check_eq("tapestry offered as depicts with the blocklist "
         "bypassed -> still NO inline (evaluator rejects "
         "it)", res, [])

# ── Fort Bragg CA photo in the Montville NJ story (locality) ─────
print("2026-11-03 corpus — Fort Bragg vs Montville, NJ")
FORT_BRAGG = "File:Fort Bragg Food Bank volunteers.jpg"
FORT_BRAGG_PAGE = commons_page(
    FORT_BRAGG, 2400, 1600,
    desc="Volunteers distribute groceries at a food bank "
         "in Fort Bragg, California.",
    cats="Food banks in California|Fort Bragg, California")
NJ_KEEPER = ("File:Volunteers stock shelves at a New Jersey "
             "food pantry.jpg")
NJ_KEEPER_PAGE = commons_page(
    NJ_KEEPER, 3200, 2000,
    desc="Volunteers stock shelves at a food pantry in "
         "Newark, New Jersey.",
    cats="Food banks in New Jersey")
NJ_ART = {
    "headline": "Montville Diwali Fundraiser Stocks Kiwanis "
                "Food Pantry Shelves",
    "body": "<p>The Kiwanis Food Pantry in Montville "
            "collected donations across New Jersey this "
            "week. Volunteers said the New Jersey drive "
            "raised 7,000 dollars for the Kiwanis Food "
            "Pantry shelves.</p>",
    "category": "news", "slug": "montville-food-pantry",
}
NJ_RES = resolution(
    "New Jersey", "Q-TEST-NJ", type_="place",
    description="state in the Mid-Atlantic region of the "
                "United States")
NJ_ITEM = {"description": "state in the Mid-Atlantic and "
                          "Northeastern United States",
           "located_in": ["New Jersey"],
           "country": "United States"}
net, calls = identity_net(
    resolutions={"New Jersey": NJ_RES},
    depicts_by_qid={"Q-TEST-NJ": [{"title": FORT_BRAGG}]},
    pages_by_title={FORT_BRAGG: FORT_BRAGG_PAGE},
    items_by_qid={"Q-TEST-NJ": NJ_ITEM})
res = step0(NJ_ART, net)
check_eq("Fort Bragg, California photo offered for a New "
         "Jersey story -> NO inline (locality gate)", res, [])

net, calls = identity_net(
    resolutions={"New Jersey": NJ_RES},
    depicts_by_qid={"Q-TEST-NJ": [{"title": FORT_BRAGG},
                                  {"title": NJ_KEEPER}]},
    pages_by_title={FORT_BRAGG: FORT_BRAGG_PAGE,
                    NJ_KEEPER: NJ_KEEPER_PAGE},
    items_by_qid={"Q-TEST-NJ": NJ_ITEM})
res = step0(NJ_ART, net)
check("keeper: with the California photo rejected, the "
      "genuine New Jersey pantry photo still sources",
      len(res) == 1 and res[0][0] == "New Jersey"
      and "New_Jersey" in res[0][1], str(res))

# ── Election_day.svg choropleth (midterms) ───────────────────────
print("2026-11-02 corpus — Election_day.svg")
ELECTION_SVG = "File:Election day.svg"
ELECTION_SVG_PAGE = commons_page(
    ELECTION_SVG, 2400, 1600,
    desc="Choropleth map of United States election results "
         "by state.",
    cats="Election maps of the United States",
    mime="image/svg+xml")
ELECTION_ART = {
    "headline": "US Midterm Results 2026: Winners Announced "
                "State by State",
    "body": "<p>Election Day counting continued across the "
            "country. Election Day officials said results "
            "would be certified within days.</p>",
    "category": "news", "slug": "us-midterm-results-2026",
}
net, calls = identity_net(
    resolutions={"Election Day": resolution(
        "Election Day", "Q-TEST-ED", type_="other")},
    depicts_by_qid={"Q-TEST-ED": [{"title": ELECTION_SVG}]},
    pages_by_title={ELECTION_SVG: ELECTION_SVG_PAGE})
res = step0(ELECTION_ART, net)
check_eq("Election_day.svg offered as depicts -> NO inline "
         "(not a photograph file)", res, [])

net, calls = identity_net()
res = step0(ELECTION_ART, net)
check_eq("no identity resolution anywhere -> NO inline "
         "(fail closed)", res, [])
check("the SVG was never read",
      ELECTION_SVG not in calls["file_info"])

# ── Chelsea 3 (the retired type-gate suite's incident) ───────────
print("2026-10-13 corpus — Chelsea 3")
CLINTON = "File:Chelsea Clinton.jpg"
net, calls = identity_net(
    pages_by_title={CLINTON: commons_page(
        CLINTON, 1200, 1500,
        desc="Chelsea Clinton in 2008.",
        cats="Chelsea Clinton in 2008")})
res = step0(
    {"headline": "Drone Attack Sinks Ship Off Bulgaria in "
                 "Black Sea",
     "body": "<p>A drone attack sank the Chelsea 3 off the "
             "Bulgarian coast late on Monday. The Chelsea 3, "
             "a general cargo vessel, went down in the Black "
             "Sea after an explosion on board. All crew "
             "members were rescued.</p>",
     "category": "news", "slug": "chelsea-3-drone-attack"},
    net)
check_eq("the Chelsea 3 incident article yields NO inline "
         "under identity sourcing", res, [])
check("the Chelsea Clinton file was never read",
      CLINTON not in calls["file_info"])

# ── keepers (fixtures from test_inline_identity_sourcing) ────────
print("keepers")
PANT = "File:Rishabh Pant in 2024.jpg"
PANT_PAGE = commons_page(
    PANT, 2000, 1400,
    desc="Rishabh Pant, Indian cricketer, during a Test "
         "match.",
    cats="Rishabh Pant")
net, calls = identity_net(
    resolutions={"Rishabh Pant": resolution(
        "Rishabh Pant", "Q-TEST-RP", type_="person",
        p18="Rishabh Pant in 2024.jpg")},
    pages_by_title={PANT: PANT_PAGE})
res = step0(
    {"headline": "Rishabh Pant Century Puts India on Top",
     "body": "<p>Rishabh Pant scored a century. Rishabh "
             "Pant hit nine fours as India took control of "
             "the match on day two.</p>",
     "category": "sports", "slug": "pant-century"}, net)
check("keeper: a person's P18 portrait still sources "
      "through Step 0",
      len(res) == 1 and res[0][0] == "Rishabh Pant"
      and res[0][1].endswith("Rishabh_Pant_in_2024.jpg")
      and len(res[0][2]) > 10, str(res))

PROTEST = ("File:Palestine Action Protest, London, Saturday "
           "6th September - 04.jpg")
PROTEST_PAGE = commons_page(
    PROTEST, 4000, 3000,
    desc="A Palestine Action protest in London on Saturday "
         "6 September.",
    cats="Palestine Action|Protests in London")
net, calls = identity_net(
    resolutions={"Palestine Action": resolution(
        "Palestine Action", "Q-TEST-PA", type_="org")},
    depicts_by_qid={"Q-TEST-PA": [{"title": PROTEST}]},
    pages_by_title={PROTEST: PROTEST_PAGE})
res = step0(
    {"headline": "Palestine Action Protest at US Embassy in "
                 "London Sees 325 Arrested",
     "body": "<p>Hundreds gathered in London on Saturday. "
             "Police made 325 arrests near the US embassy. "
             "Palestine Action supporters rallied outside "
             "the embassy as Palestine Action protests "
             "continued.</p>",
     "category": "news", "slug": "palestine-action-london"},
    net)
check("keeper: the genuine Palestine Action protest photo "
      "still sources through Step 0",
      len(res) == 1 and res[0][0] == "Palestine Action"
      and "Palestine_Action_Protest" in res[0][1], str(res))

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
