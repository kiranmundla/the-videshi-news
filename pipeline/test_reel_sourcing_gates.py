#!/usr/bin/env python3
"""
test_reel_sourcing_gates.py — regression tests for the
2026-10-27 port of the article picture pass's identity gates
into the reel entity sourcer (via picture_gate_shared.py).

Every fixture is modeled on a VERIFIED 2026-10-26 pulse-reels
failure (candidate metadata below is the files' real Commons
title/description/categories, fetched 2026-10-27):
  * 'PERM' (the US labor-certification programme) sourced
    Perm, Russia — the Kama River bridge + the passenger ship
    "Moskva-210" — for a White House / Department of Labor
    story.
  * A v2 attempt sourced the Moscow 'White House' (Moskva
    River) for the entity 'White House' (Washington).
  * 'Times of India' — a cited OUTLET auto-added as an
    entity — sourced a portrait of its journalist Jug
    Suraiya, used as hero + grid scenes for a Drishyam 3
    box-office story.
Keepers are the same runs' GOOD accepts (the Frances Perkins
Building, Keith Sonderling) plus the Drishyam run's Ajay
Devgn still and a Microsoft campus frame: the gates must
reject namesakes without costing the story its real pictures.

All network is stubbed. Run:
  python3 test_reel_sourcing_gates.py   (exit 0 = all pass)
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_entity_sourcing as S

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(name, got == want, f"got {got!r}, want {want!r}")


def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats="", artist="A Photographer"):
    return {"title": title, "imageinfo": [{
        "url": "https://upload.wikimedia.org/wikipedia/commons/"
               + title.replace("File:", "").replace(" ", "_"),
        "width": w, "height": h, "mime": "image/jpeg",
        "descriptionurl": "https://commons.wikimedia.org/wiki/"
                          + title.replace(" ", "_"),
        "extmetadata": {
            "LicenseShortName": {"value": license_short},
            "UsageTerms": {"value": license_short},
            "ImageDescription": {"value": desc},
            "Categories": {"value": cats},
            "Artist": {"value": artist}}}]}


FIXTURES = Path(__file__).resolve().parent / "test-fixtures" \
    / "reel-sourcing-gates"


def load_run(name):
    """The failed runs' own article.json + script.json, copied
    verbatim into test-fixtures/reel-sourcing-gates/ (the run
    dirs themselves carry ~180 MB of renders and are not
    committed)."""
    article = json.loads(
        (FIXTURES / f"{name}-article.json").read_text())
    script = json.loads(
        (FIXTURES / f"{name}-script.json").read_text())
    entities = S.extract_entities(article, script)
    return article, script, entities, \
        S.build_story_context(article, script, entities)


# ── the failed stories, from their committed fixtures ──────
perm_article, perm_script, perm_entities, perm_ctx = \
    load_run("perm")
drish_article, drish_script, drish_entities, drish_ctx = \
    load_run("drishyam")
ms_article, ms_script, ms_entities, ms_ctx = \
    load_run("microsoft")

print("── story context ──")
check("PERM story context places it in the US + India, "
      "never Russia",
      "united states" in perm_ctx["countries"]
      and "india" in perm_ctx["countries"]
      and "russia" not in perm_ctx["countries"],
      str(perm_ctx["countries"]))
check("Drishyam story context places it in India",
      "india" in drish_ctx["countries"],
      str(drish_ctx["countries"]))
check("'Times of India' really is auto-extracted for the "
      "Drishyam story (the failure's precondition)",
      "Times of India" in drish_entities, str(drish_entities))

# ── 1. the outlet gate ──────────────────────────────────────
print("── outlet gate ──")
check("is_outlet_entity: 'Times of India'",
      S.is_outlet_entity("Times of India"))
check("is_outlet_entity: 'The Hindu' (leading The)",
      S.is_outlet_entity("The Hindu"))
check("is_outlet_entity: 'Microsoft' is not an outlet",
      not S.is_outlet_entity("Microsoft"))

JUG_TITLE = ('File:Jug Suraiya, Indian journalist, formerly '
             'with the "Junior Statesmen" and then '
             '"Times of India" 02.jpg')
jug_page = commons_page(
    JUG_TITLE, 2432, 4320,
    desc='Jug Suraiya, Indian journalist, formerly with the '
         '"Junior Statesmen" and then "Times of India"',
    cats="Jug Suraiya|Self-published work|Book signing in 2011")
cand, row = S.evaluate_commons_page(
    jug_page, "Times of India", "A — Wikimedia Commons",
    context=drish_ctx)
check("Jug Suraiya under 'Times of India' rejected as outlet",
      cand is None and "outlet" in row["reason"], row["reason"])

# The outlet entity is never even queried by source_extras.
queries = []


def recording_search(q, limit=10):
    queries.append(q)
    return []


stub_net = {"commons_search": recording_search,
            "commons_file_info": lambda title: None,
            "brave_links": lambda q, n=8: [],
            "fetch_text": lambda url, timeout=15: "",
            "download": lambda url, dest: None,
            # Identity route (2026-10-31): nothing resolves
            # offline in this suite — entities fail closed.
            "resolve_entity": lambda name, ctx="": None,
            "depicts": lambda qid, limit=10: []}
with tempfile.TemporaryDirectory() as tmp:
    prov = S.source_extras(drish_article, drish_script,
                           Path(tmp) / "supp", own_count=1,
                           log=lambda *a: None, net=stub_net)
check("source_extras never queries the outlet entity",
      not any("Times of India" in q for q in queries),
      str(queries))
check("...but the ledger records the outlet rejection",
      any("outlet" in r.get("reason", "")
          for r in prov["candidate_ledger"]))
check("...and provenance still lists it as extracted",
      "Times of India" in prov["entities"])

# ── 2. the country/domain contradiction gate (PERM) ───────
print("── namesake/context gate: PERM ──")
perm_bridge = commons_page(
    "File:Perm. Kama River. Kommunalny Bridge "
    "P6232022 2575.jpg", 3863, 2575,
    desc="Perm. Kama River. Kommunalny Bridge",
    cats="Kommunalny Bridge (Perm)|Self-published work|"
         "Russia photographs taken on 2021-06-23|"
         "Kama River in Perm")
cand, row = S.evaluate_commons_page(
    perm_bridge, "PERM", "A — Wikimedia Commons",
    context=perm_ctx)
check("Perm, Russia bridge rejected for 'PERM' the programme",
      cand is None and "russia" in row["reason"], row["reason"])

perm_ship = commons_page(
    "File:Perm. Kama River. Passenger river ship "
    "Moskva-210 P6242370 2575.jpg", 3862, 2575,
    desc='Perm. Kama River. Passenger river ship "Moskva-210"',
    cats="2021 in Perm Krai|Perm Krai photographs taken on "
         "2021-06-24|Kama River in Perm|Moskva-210 (ship, 1988)")
cand, row = S.evaluate_commons_page(
    perm_ship, "PERM", "A — Wikimedia Commons",
    context=perm_ctx)
check("Perm, Russia river ship rejected for 'PERM'",
      cand is None and "russia" in row["reason"], row["reason"])

moscow_wh = commons_page(
    "File:Russian White House and ships on Moskva River.jpg",
    4488, 2970,
    desc="Moscow. A view on Krasnopresnenskaya Embankment "
         "from Taras Shevchenko Embankment: a police boat "
         "goes up the Moskva River; on the river front: the "
         "Russian White House.",
    cats="Moscow photographs taken on 2017-07-23|FoP-Russia|"
         "Rivers of Russia in 2017|Buildings in Moscow "
         "photographed in 2017")
cand, row = S.evaluate_commons_page(
    moscow_wh, "White House", "A — Wikimedia Commons",
    context=perm_ctx)
check("Moscow 'White House' rejected for Washington's",
      cand is None and "russia" in row["reason"], row["reason"])
cand, row = S.evaluate_commons_page(
    moscow_wh, "White House", "A — Wikimedia Commons")
check("control: without a story context the same file "
      "passes (the context gate does the rejecting)",
      cand is not None, row["reason"])

# ── 3. the depicted-person gate (Jug Suraiya) ───────────────
print("── depicted-person gate ──")
cand, row = S.evaluate_commons_page(
    jug_page, "India", "A — Wikimedia Commons",
    context=drish_ctx)
check("Jug Suraiya portrait rejected under a non-outlet "
      "entity: he is not a Drishyam story subject",
      cand is None and "depicted person" in row["reason"]
      and "Jug Suraiya" in row["reason"], row["reason"])

# ── 4. the person namesake gate (Shadab Khan pair) ─────────
print("── person namesake gate ──")
sports_article = {
    "headline": "Shadab Khan Takes Four Wickets as Pakistan "
                "Beat New Zealand in Karachi Thriller",
    "category": "sports",
    "body": "Shadab Khan, the Pakistan leg-spinner, took "
            "four wickets in Karachi. The cricketer was "
            "named player of the match."}
sports_script = {"key_entities": ["Shadab Khan"],
                 "news_summary": "Shadab Khan starred with "
                                 "the ball for Pakistan."}
sports_ctx = S.build_story_context(
    sports_article, sports_script, ["Shadab Khan"])
actor_page = commons_page(
    "File:Shadab Khan (actor).jpg", 2000, 2500,
    desc="Shadab Khan, an actor and author, at a book "
         "launch in 2019",
    cats="Shadab Khan (actor)|Male film actors")
cand, row = S.evaluate_commons_page(
    actor_page, "Shadab Khan", "A — Wikimedia Commons",
    context=sports_ctx)
check("the ACTOR Shadab Khan rejected for the cricketer's "
      "story (domain contradiction)",
      cand is None and "namesake" in row["reason"],
      row["reason"])
cricketer_page = commons_page(
    "File:Shadab Khan in 2023.jpg", 2400, 1600,
    desc="Shadab Khan, Pakistani cricketer, bowling for "
         "Pakistan in a T20 international in Karachi",
    cats="Shadab Khan|Pakistan international cricketers")
cand, row = S.evaluate_commons_page(
    cricketer_page, "Shadab Khan", "A — Wikimedia Commons",
    context=sports_ctx)
check("the CRICKETER Shadab Khan accepted for his own story",
      cand is not None, row["reason"])

# ── keepers: the same runs' good accepts survive ────────────
print("── keepers ──")
perkins = commons_page(
    "File:Frances Perkins Building of the United States "
    "Department of Labor in Washington, D.C. - 1.jpg",
    6720, 4480, license_short="CC BY 2.0",
    desc="Washington, DC – frances perkins Building "
         "Official Department of Labor Photograph*** "
         "Photographs taken by the federal government are "
         "generally part of the public domain.",
    cats="November 2017 in Washington, D.C.|Files from the "
         "U.S. Department of Labor Flickr stream|"
         "Frances Perkins Building")
cand, row = S.evaluate_commons_page(
    perkins, "Department of Labor", "A — Wikimedia Commons",
    context=perm_ctx)
check("keeper: Frances Perkins Building (Dept of Labor HQ)",
      cand is not None, row["reason"])

keith = commons_page(
    "File:Keith Sonderling (55510883049).jpg", 8192, 5464,
    desc="Acting U.S. Secretary of Labor Keith Sonderling "
         "speaking with attendees at the Republican Jewish "
         "Coalition's 2026 Annual Leadership Summit in Las "
         "Vegas, Nevada.",
    cats="Photographs by Gage Skidmore|Keith Sonderling|"
         "2026 Republican Jewish Coalition's Annual "
         "Leadership Summit")
cand, row = S.evaluate_commons_page(
    keith, "Keith Sonderling", "A — Wikimedia Commons",
    context=perm_ctx)
check("keeper: Keith Sonderling portrait (story subject, "
      "own category, 'Labor' agreement)",
      cand is not None, row["reason"])

dc_wh = commons_page(
    "File:White House in Washington, D.C. 2024.jpg",
    4000, 2667,
    desc="The White House, official residence and workplace "
         "of the President of the United States, in "
         "Washington, D.C.",
    cats="White House|Washington, D.C.")
cand, row = S.evaluate_commons_page(
    dc_wh, "White House", "A — Wikimedia Commons",
    context=perm_ctx)
check("keeper: the Washington White House for 'White House'",
      cand is not None, row["reason"])

ajay = commons_page(
    "File:Ajay Devgn .jpg", 1280, 720,
    desc="Ajay devgn is a bollywood actor, known for "
         "blockbuster films like singham, golmaal series",
    cats="Self-published work|Ajay Devgan in 2020")
cand, row = S.evaluate_commons_page(
    ajay, "Ajay Devgn", "A — Wikimedia Commons",
    context=drish_ctx)
check("keeper: Ajay Devgn still for the Drishyam story",
      cand is not None, row["reason"])

ms_campus = commons_page(
    "File:Microsoft headquarters, Redmond.jpg", 4000, 3000,
    desc="Microsoft corporate headquarters campus in "
         "Redmond, Washington, United States",
    cats="Microsoft campus|Buildings in Redmond, Washington")
cand, row = S.evaluate_commons_page(
    ms_campus, "Microsoft", "A — Wikimedia Commons",
    context=ms_ctx)
check("keeper: Microsoft campus for the buyouts story",
      cand is not None, row["reason"])

# ── kind-split refinements (from the live dry run) ─────────
print("── kind-split refinements ──")
keith_geneva = commons_page(
    "File:Keith Sonderling 2025 ILO Plenary.jpg", 2600, 1668,
    license_short="CC0",
    desc="Keith Sonderling, Acting U.S. Secretary of Labor, "
         "addressing the International Labour Organization "
         "plenary in Geneva, Switzerland",
    cats="Keith Sonderling|International Labour Conference "
         "2025")
cand, row = S.evaluate_commons_page(
    keith_geneva, "Keith Sonderling", "A — Wikimedia Commons",
    context=perm_ctx)
check("person exemption: the story's own subject "
      "photographed abroad (Geneva) is still the person",
      cand is not None, row["reason"])

south_facade = commons_page(
    "File:White House South Facade 2016.jpg", 3000, 2000,
    desc="The south facade of the White House in "
         "Washington, D.C., during the 2016 Olympic team "
         "visit",
    cats="White House|Views of the White House from the "
         "south")
cand, row = S.evaluate_commons_page(
    south_facade, "White House", "A — Wikimedia Commons",
    context=perm_ctx)
check("'White House' is a place, not a person: an Olympic "
      "mention in its evidence is no domain contradiction",
      cand is not None, row["reason"])

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
