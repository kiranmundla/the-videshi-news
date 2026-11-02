#!/usr/bin/env python3
"""
test_reel_identity_sourcing.py — regression suite for the
2026-10-31 reel-sourcer identity rebuild.

The five cases are the five reels that passed fact-check +
frame QA 10.0 and were withheld on Kiran's visual check
because the old open-search ladder could not tell a word's
senses apart (run dirs under pipeline/reel-runs/; article +
script copied verbatim into test-fixtures/
reel-identity-sourcing/):

  1. caterpillar — Caterpillar Inc. earnings sourced insect
     photos ('Alice 05a-1116x1492.jpg', the Tenniel
     illustration; 'Chenille chevrefeuille.jpg', a fox moth
     caterpillar) on the bare token "caterpillar".
  2. blackstone — Blackstone the firm sourced photos of the
     TOWNS Blackstone, MA ('Blackstone Free Public Library,
     Blackstone MA.jpg') and Blackstone, VA ('Blackstone, VA
     - commercial downtown.JPG').
  3. chevron — Chevron earnings sourced a Ukrainian military
     shoulder patch ('Chevron 185th GvTBAP.png'), a
     chevron-pattern masonry photo ('Hovedbygningen NTNU
     stonemasonry.JPG'), and a World Bank IP-finance panel
     portrait via the pseudo-entity 'Markets Finance'.
  4. abbvie — the same IP-finance panel photo as the hero-stat
     scene, again via 'Markets Finance'.
  5. jailer — Jailer 2 Hindi box office sourced a Hindi
     alphabet chart ('Hindi aksharamala.jpg') and a language
     map ('Hindi language native speakers.png') for the entity
     'Hindi', and a NASA solar eruption ('Magnificent CME
     Erupts on the Sun - August 31.jpg') for 'Sun Pictures'
     decomposed to 'Sun'. The run's Rajinikanth portrait
     ('Rajinikanth at the Inauguration of MGR Statue.jpg')
     was legitimate and must survive.

For each case the suite asserts:
  * open search is NEVER consulted (the commons_search /
    brave seams record calls; there must be none);
  * none of the previously-sourced wrong files is produced;
  * every produced extra came through the identity route
    (P18 / depicts of a resolved Wikidata item);
  * the specific failure mechanism is ledgered (language
    non-visual, category-label pseudo-entity, unresolved
    entity fail-closed, corpus blocklist at the evaluator).

Network is fully stubbed: resolution is the REAL registry
(verified_sourcer.registry_only_resolve — offline, no cache-
back), depicts yields and file metadata are fixtures modeled
on the real Commons records measured 2026-10-31.

Run:  python3 test_reel_identity_sourcing.py  (exit 0 = pass)
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image

import entity_resolve as ER
import reel_entity_sourcing as S
from verified_sourcer import registry_only_resolve

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


FIXTURES = Path(__file__).resolve().parent / "test-fixtures" \
    / "reel-identity-sourcing"


def load_case(name):
    article = json.loads(
        (FIXTURES / f"{name}-article.json").read_text())
    script = json.loads(
        (FIXTURES / f"{name}-script.json").read_text())
    return article, script


def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats="", mime="image/jpeg"):
    return {"title": title, "imageinfo": [{
        "url": "https://upload.wikimedia.org/wikipedia/commons/x/"
               + title.replace("File:", "").replace(" ", "_"),
        "width": w, "height": h, "mime": mime,
        "descriptionurl": "https://commons.wikimedia.org/wiki/"
                          + title.replace(" ", "_"),
        "extmetadata": {
            "LicenseShortName": {"value": license_short},
            "UsageTerms": {"value": license_short},
            "ImageDescription": {"value": desc},
            "Categories": {"value": cats},
            "Artist": {"value": "Fixture Photographer"}}}]}


# File metadata for the identity-route candidates the stub
# depicts/P18 production can surface (modeled on the real
# Commons records measured 2026-10-31; titles are the real
# file titles, dimensions the real widths with plausible
# heights where only the width was recorded).
PAGES = {
    # Caterpillar Inc. Q459965 — registry P18 + a depicts
    # machinery photo (the route's real yield class).
    "File:Caterpillarhq.JPG": commons_page(
        "File:Caterpillarhq.JPG", 2400, 1600,
        desc="Caterpillar Inc. world headquarters, Peoria, "
             "Illinois", cats="Category:Caterpillar Inc."),
    "File:Caterpillar 432 backhoe loader.jpg": commons_page(
        "File:Caterpillar 432 backhoe loader.jpg", 3000, 2000,
        desc="Caterpillar backhoe loader at work",
        cats="Category:Caterpillar Inc."),
    # Blackstone Q880942 — registry P18 is 846px wide: below
    # the reel floor, so the honest outcome is no extra.
    "File:Blackstone HQ - 345 Park Avenu.jpg": commons_page(
        "File:Blackstone HQ - 345 Park Avenu.jpg", 846, 560,
        desc="Blackstone headquarters, 345 Park Avenue",
        cats="Category:Blackstone Group"),
    # Chevron Q319642 — registry P18 + the real depicts yield.
    "File:Chevron Headquarters 2022.jpg": commons_page(
        "File:Chevron Headquarters 2022.jpg", 4000, 2667,
        desc="Chevron Corporation headquarters",
        cats="Category:Chevron Corporation"),
    "File:Big Oil 2022.jpg": commons_page(
        "File:Big Oil 2022.jpg", 2250, 1500, "CC BY 4.0",
        desc="Chevron refinery", cats="Category:Chevron"),
    "File:Chevron Barrow Island Visit October 2021.jpg":
        commons_page(
            "File:Chevron Barrow Island Visit October "
            "2021.jpg", 3574, 2383, "CC BY 4.0",
            desc="Chevron Barrow Island operations visit",
            cats="Category:Chevron"),
    # AbbVie Q14662364 — depicts yield is logos + one small
    # photo: both must fail the file gates.
    "File:AbbVie logo.png": commons_page(
        "File:AbbVie logo.png", 2000, 2000, "CC BY-SA 4.0",
        desc="AbbVie logo", mime="image/png"),
    "File:AbbVie executive portrait.jpg": commons_page(
        "File:AbbVie executive portrait.jpg", 631, 631,
        desc="AbbVie executive"),
    # Rajinikanth Q60068 — registry P18 is 800px (below the
    # floor); the depicts yield carries the legitimate MGR
    # Statue portrait from the original run.
    "File:Rajinikanth Felicitates Writer Kalaignanam.jpg":
        commons_page(
            "File:Rajinikanth Felicitates Writer "
            "Kalaignanam.jpg", 800, 533,
            desc="Rajinikanth felicitates writer Kalaignanam",
            cats="Category:Rajinikanth"),
    "File:Rajinikanth at the Inauguration of MGR Statue.jpg":
        commons_page(
            "File:Rajinikanth at the Inauguration of MGR "
            "Statue.jpg", 1200, 1800,
            desc="Rajinikanth at the inauguration of the MGR "
                 "statue", cats="Category:Rajinikanth"),
}

# Real depicts yields measured 2026-10-31, by QID.
DEPICTS = {
    "Q459965": [{"title": "File:Caterpillar 432 backhoe "
                          "loader.jpg"}],
    "Q319642": [{"title": "File:Big Oil 2022.jpg"},
                {"title": "File:Chevron Barrow Island Visit "
                          "October 2021.jpg"}],
    "Q14662364": [{"title": "File:AbbVie logo.png"},
                  {"title": "File:AbbVie executive "
                            "portrait.jpg"}],
    "Q60068": [{"title": "File:Rajinikanth at the Inauguration "
                         "of MGR Statue.jpg"}],
}


def make_net(calls):
    def resolve(name, ctx=""):
        calls.append(("resolve", name))
        return registry_only_resolve(name, ctx)

    def depicts(qid, limit=10):
        calls.append(("depicts", qid))
        return DEPICTS.get(qid, [])

    def download(url, dest):
        Image.new("RGB", (1600, 1200), (30, 40, 50)).save(dest)

    return {
        "commons_search": lambda q, limit=10:
            (calls.append(("commons_search", q)) or []),
        "brave_links": lambda q, n=8:
            (calls.append(("brave", q)) or []),
        "fetch_text": lambda url, timeout=15: "",
        "commons_file_info": lambda title: PAGES.get(title),
        "download": download,
        "resolve_entity": resolve,
        "depicts": depicts,
    }


IP_FINANCE = ("IP Finance Dialogue – Expanding Horizons on "
              "IP Finance and Valuation - 53346909618.jpg")

CASES = {
    "caterpillar": {
        "wrong": ["Alice 05a-1116x1492.jpg",
                  "Chenille chevrefeuille.jpg",
                  "Beacon Power New York - 20 MW Flywheel "
                  "Energy Storage.jpg",
                  "Power County Wind Farm 002.jpg"],
    },
    "blackstone": {
        "wrong": ["Blackstone Free Public Library, "
                  "Blackstone MA.jpg",
                  "Blackstone, VA - commercial downtown.JPG",
                  "Delhi, India, Khas Mahal 2, Red Fort.jpg",
                  "Hampi, India, Lotus Mahal.jpg"],
    },
    "chevron": {
        "wrong": ["Chevron 185th GvTBAP.png",
                  "Hovedbygningen NTNU stonemasonry.JPG",
                  IP_FINANCE],
    },
    "abbvie": {
        "wrong": [IP_FINANCE, "AbbVie.jpg"],
    },
    "jailer": {
        "wrong": ["Hindi aksharamala.jpg",
                  "Hindi language native speakers.png",
                  "Magnificent CME Erupts on the Sun - "
                  "August 31.jpg"],
    },
}


def run_case(name):
    article, script = load_case(name)
    calls = []
    with tempfile.TemporaryDirectory() as tmp:
        prov = S.source_extras(article, script, Path(tmp),
                               own_count=1, log=lambda *a: None,
                               net=make_net(calls))
    return prov, calls


def extra_keys(prov):
    keys = set()
    for e in prov["extras"]:
        for v in (e.get("file_url"), e.get("subject"),
                  e.get("path")):
            k = ER.file_key(v)
            if k:
                keys.add(k)
    return keys


def ledger_reasons(prov):
    return " | ".join(r.get("reason", "")
                       for r in prov["candidate_ledger"])


for case, spec in CASES.items():
    print(f"── case: {case} ──")
    prov, calls = run_case(case)
    kinds = [c[0] for c in calls]
    check("open search never consulted (no Commons search, "
          "no Brave)", "commons_search" not in kinds
          and "brave" not in kinds, str(kinds))
    keys = extra_keys(prov)
    for wrong in spec["wrong"]:
        check(f"wrong file NOT produced: {wrong}",
              ER.file_key(wrong) not in keys)
    for e in prov["extras"]:
        check(f"extra via identity route only: "
              f"{e.get('path')}",
              str(e.get("route", "")).startswith("identity"))

# ── case-specific failure mechanisms ────────────────────────
print("── mechanisms: caterpillar ──")
prov, _ = run_case("caterpillar")
reasons = ledger_reasons(prov)
check("'Power & Energy' fails closed (no verified identity)",
      "no verified identity" in reasons
      and "Power & Energy" in reasons)
check("'Markets Finance' rejected as the category label",
      "category label" in reasons and "Markets Finance"
      in reasons)
check("Caterpillar Inc. identity candidates accepted "
      "(P18/depicts)", any(
          str(r.get("verdict", "")).startswith("USED")
          or r.get("verdict") == "accepted"
          for r in prov["candidate_ledger"]
          if "Caterpillar" in str(r.get("candidate", ""))))

print("── mechanisms: blackstone ──")
prov, _ = run_case("blackstone")
check("Blackstone P18 (846px) rejected at the reel floor — "
      "honest navy outcome, no town photos",
      prov["extras"] == []
      and "resolution" in ledger_reasons(prov),
      str([e.get("path") for e in prov["extras"]]))

print("── mechanisms: chevron ──")
prov, _ = run_case("chevron")
reasons = ledger_reasons(prov)
check("'Markets Finance' pseudo-entity rejected as category "
      "label (the IP-finance photo's route is closed)",
      "category label" in reasons
      and "Markets Finance" in reasons)
check("Chevron identity extras produced (P18/depicts of "
      "Q319642)", len(prov["extras"]) >= 1,
      str([e.get("path") for e in prov["extras"]]))

print("── mechanisms: abbvie ──")
prov, _ = run_case("abbvie")
reasons = ledger_reasons(prov)
check("'Markets Finance' rejected as category label",
      "category label" in reasons)
check("AbbVie depicts yield fails the file gates (logo + "
      "sub-floor photo) — no AbbVie extra",
      not any("abbvie" in (e.get("path") or "").lower()
              for e in prov["extras"])
      and ("logo" in reasons or "diagram/map" in reasons)
      and "resolution" in reasons,
      str([e.get("path") for e in prov["extras"]]))

print("── mechanisms: jailer ──")
article, script = load_case("jailer")
entities = S.extract_entities(article, script)
check("precondition: 'Hindi' really is extracted for the "
      "Jailer story", "Hindi" in entities, str(entities))
prov, calls = run_case("jailer")
reasons = ledger_reasons(prov)
resolved_names = [c[1] for c in calls if c[0] == "resolve"]
check("'Hindi' rejected as a non-visual language entity",
      "non-visual" in reasons and "Hindi" in reasons)
check("'Hindi' never even reaches the resolver",
      "Hindi" not in resolved_names, str(resolved_names))
check("'Sun Pictures' resolved AS A WHOLE (never decomposed "
      "to 'Sun')", "Sun Pictures" in resolved_names
      and "Sun" not in resolved_names, str(resolved_names))
accepted_titles = [r.get("candidate", "")
                   for r in prov["candidate_ledger"]
                   if r.get("verdict") == "accepted"
                   or str(r.get("verdict", ""))
                   .startswith("USED")]
check("the legitimate Rajinikanth MGR Statue portrait "
      "survives the identity route",
      any("MGR Statue" in t for t in accepted_titles),
      str(accepted_titles))
check("Rajinikanth P18 (800px) rejected at the reel floor",
      "resolution" in reasons)

# ── the corpus blocklist at the evaluator ───────────────────
print("── corpus blocklist (evaluator, identity route) ──")
BLOCKED_CASES = [
    ("Caterpillar", "File:Alice 05a-1116x1492.jpg"),
    ("Caterpillar", "File:Chenille chevrefeuille.jpg"),
    ("Blackstone",
     "File:Blackstone Free Public Library, Blackstone MA.jpg"),
    ("Blackstone",
     "File:Blackstone, VA - commercial downtown.JPG"),
    ("Sun Pictures",
     "File:Magnificent CME Erupts on the Sun - August 31.jpg"),
    ("Hindi", "File:Hindi aksharamala.jpg"),
    ("Hindi", "File:Hindi language native speakers.png"),
    ("Chevron", "File:" + IP_FINANCE),
    ("AbbVie", "File:" + IP_FINANCE),
]
for entity, title in BLOCKED_CASES:
    res = registry_only_resolve(entity, "")
    blocked = {ER.file_key(b) for b in res.get("blocked_files")
               or [] if ER.file_key(b)}
    page = commons_page(title, 3000, 2000,
                        desc="fixture", cats="")
    cand, row = S.evaluate_commons_page(
        page, entity, "identity — test",
        identity_verified=True, blocked_keys=blocked)
    # 'Hindi' files reject even earlier, at the language gate
    # (non-visual entities are refused before the blocklist is
    # consulted) — either reason is a rejection for the right
    # cause; every other case must name the blocklist itself.
    ok_reason = "blocklist" in row["reason"] or (
        entity == "Hindi" and "non-visual" in row["reason"])
    check(f"blocklist rejects {title} for {entity!r}",
          cand is None and ok_reason, row["reason"])

# ── 2026-11-02: the Ambani reel (three wrong pictures) ─────
# The published reel (deleted on Kiran's order) carried: the
# Mount Charleston Wilderness (Nevada) trail photo as its news
# scene — a depicts (P180=Q298547) file for Mukesh Ambani
# whose own metadata never mentions him (polluted Commons
# structured data), and the only depicts candidate clearing
# the size floor after the wildlife veto false-rejected the
# two genuine Ambani photos below; a Gautam Adani portrait
# behind the '$6.3 BILLION' stat scene (the article's inline,
# placed with no scene check); and a 'Stop Adani' protest
# photo as the payoff filler (assignment by role affinity,
# the payoff text names nobody). Metadata below is the real
# Commons record for each file, fetched 2026-11-02.
print("── 2026-11-02 ambani: depicts name agreement + "
      "blocklist ──")
NEVADA = ("2015-07-13 09 54 15 View northeast along the "
          "North Loop Trail about 8.1 miles west of the "
          "trailhead in the Mount Charleston Wilderness, "
          "Nevada.jpg")
NEVADA_PAGE = commons_page(
    f"File:{NEVADA}", 3264, 2448,
    desc="View northeast along the North Loop Trail about "
         "8.1 miles west of the trailhead in the Mount "
         "Charleston Wilderness, Nevada",
    cats="Self-published work|July 2015 in Nevada|Files with "
         "coordinates missing SDC location of creation|"
         "United States photographs taken on 2015-07-13|"
         "North Loop Trail (Spring Mountains National "
         "Recreation Area)|Famartin's 2015 photos|Famartin's "
         "July 2015 photos")
CNBC_CATS = ("Taken with Canon EOS 5D|CC-Zero|Mukesh Ambani|"
             "Blurred images|Self-published work|Kamal Nath "
             "in 2007|Men holding awards")
CNBC_PAGE = commons_page(
    "File:Mukesh Ambani Receives CNBC India Business Award, "
    "2007.jpg", 2790, 1829, license_short="CC0",
    desc="Mukesh Ambani is given the CNBC India Business "
         "Award, 2007 by the then Minister Kamal Nath.",
    cats=CNBC_CATS)
CLINTON_CATS = ("Taken with Nikon D300|PD US Government|"
                "Mukesh Ambani|Ratan Naval Tata|Files with "
                "derivative versions|People smiling|CC-PD-Mark|"
                "3 people in India|India photographs taken on "
                "2008-07-18|People sitting in India|Hillary "
                "Rodham Clinton with businesspeople|Hillary "
                "Rodham Clinton in July 2009|Hillary Rodham "
                "Clinton in Mumbai")
CLINTON_PAGE = commons_page(
    "File:ClintonTataAmbani.jpg", 3216, 2136,
    license_short="Public domain",
    desc="Secretary Clinton meets with India's business "
         "leaders. From left to right: Ratan Tata, Charmain "
         "of the Tata Group; Secretary Clinton; Mukesh "
         "Ambani, Chairman and Managing Director of Reliance "
         "Industries.",
    cats=CLINTON_CATS)
AMBANI_RES = registry_only_resolve("Mukesh Ambani", "")
AMBANI_BLOCKED = {ER.file_key(b)
                  for b in AMBANI_RES.get("blocked_files") or []
                  if ER.file_key(b)}
DEPICTS_ROUTE = "identity — depicts (P180=Q298547)"

check("registry: the Nevada trail file is on Mukesh "
      "Ambani's corpus blocklist",
      ER.file_key(NEVADA) in AMBANI_BLOCKED)
cand, row = S.evaluate_commons_page(
    NEVADA_PAGE, "Mukesh Ambani", DEPICTS_ROUTE,
    identity_verified=True, blocked_keys=AMBANI_BLOCKED,
    entity_type="person",
    entity_aliases=AMBANI_RES.get("aliases"))
check("Nevada trail file rejected for Ambani (blocklist)",
      cand is None and "blocklist" in row["reason"],
      row["reason"])
cand, row = S.evaluate_commons_page(
    NEVADA_PAGE, "Mukesh Ambani", DEPICTS_ROUTE,
    identity_verified=True, blocked_keys=set(),
    entity_type="person",
    entity_aliases=AMBANI_RES.get("aliases"))
check("Nevada trail file rejected by depicts NAME "
      "AGREEMENT alone (no blocklist): its metadata never "
      "names Ambani", cand is None
      and "never" in row["reason"]
      and "depicts" in row["reason"], row["reason"])
cand, row = S.evaluate_commons_page(
    NEVADA_PAGE, "Mukesh Ambani",
    "identity — Wikidata P18 (Q298547)",
    identity_verified=True, blocked_keys=set(),
    entity_type="person",
    entity_aliases=AMBANI_RES.get("aliases"))
check("P18 route is EXEMPT from the depicts name check "
      "(identity by construction proper)",
      cand is not None, row["reason"])

print("── 2026-11-02 ambani: wildlife-veto false positives ──")
check("'Blurred images' category is not a species "
      "(CNBC award photo)", not S.wildlife_subject(
          "Mukesh Ambani", CNBC_CATS))
check("'People smiling' category is not a species "
      "(Clinton/Tata/Ambani photo)",
      not S.wildlife_subject("Mukesh Ambani", CLINTON_CATS))
check("a real binomial category still marks wildlife",
      S.wildlife_subject("Tamil Nadu",
                         "Corvus splendens heads|Birds of "
                         "India"))
for page, label in ((CNBC_PAGE, "CNBC award photo"),
                    (CLINTON_PAGE, "Clinton/Tata/Ambani photo")):
    cand, row = S.evaluate_commons_page(
        page, "Mukesh Ambani", DEPICTS_ROUTE,
        identity_verified=True, blocked_keys=AMBANI_BLOCKED,
        entity_type="person",
        entity_aliases=AMBANI_RES.get("aliases"))
    check(f"keeper: the genuine {label} passes the depicts "
          "route (names him; no wildlife veto)",
          cand is not None, row["reason"])

# ── 2026-11-02: scene-person rule (assignment) ──────────────
print("── 2026-11-02 ambani: scene-person rule ──")
AMBANI_SCRIPT = {
    "hook_line": "AMBANI ADDS $6.3 BILLION IN A DAY AS "
                 "RELIANCE SHARES JUMP 11.6% ON RECORD "
                 "QUARTERLY PROFIT",
    "hook_stat": {"big": "$6.3 BILLION",
                  "eyebrow": "BY THE NUMBERS",
                  "sub": "Mukesh Ambani's one-day gain, the "
                         "biggest on Forbes' real-time "
                         "billionaires list"},
    "stats": [{"big": "11.6%",
               "label": "Reliance share jump, closing at "
                        "Rs 1,300"},
              {"big": "40.6%",
               "label": "Profit rise to Rs 25,548 crore"},
              {"big": "$88.8 BILLION",
               "label": "Ambani net worth, ranked 23rd "
                        "globally"}],
    "diaspora_bullets": [
        "Ambani stays India's richest person, ahead of "
        "Gautam Adani at 26th",
        "Reliance was the biggest gainer on the Nifty 50"],
    "key_entities": ["Mukesh Ambani", "Reliance Industries",
                     "Forbes", "Nifty 50"],
    "news_summary": "Mukesh Ambani added $6.3 billion in a "
                    "single session as Reliance Industries "
                    "shares surged 11.6% after a stronger-"
                    "than-expected September quarter, "
                    "according to Forbes' real-time "
                    "billionaires list.",
    "payoff": "The quarter, not the rich list, is the story "
              "— a refining-led beat and record group profit.",
    "versus": "", "story_mood": "celebratory",
}
ADANI_RES = registry_only_resolve("Gautam Adani", "")
ADANI_CAND = {
    "entity": "Gautam Adani", "entity_type": "person",
    "entity_aliases": ADANI_RES.get("aliases") or [],
    "title": "File:Gautam Adani Net Worth.jpg",
    "subject": "Gautam Adani", "role": "establishing",
    "file_url": "https://upload.wikimedia.org/x/"
                "Gautam_Adani_Net_Worth.jpg",
    "size": [1280, 900], "route": DEPICTS_ROUTE,
    "license": "CC BY-SA 4.0", "artist": ""}
PROTEST_CAND = {
    "entity": "Gautam Adani", "entity_type": "person",
    "entity_aliases": ADANI_RES.get("aliases") or [],
    "title": "File:Gautam Adani outside Frydenberg's office "
             "- Frydenberg-jmp 5531.jpg",
    "subject": "Stop Adani protest outside Josh Frydenberg's "
               "Camberwell office, Melbourne",
    "role": "people",
    "file_url": "https://upload.wikimedia.org/x/protest.jpg",
    "size": [4928, 3280], "route": DEPICTS_ROUTE,
    "license": "CC BY-SA 2.0", "artist": "Julian Meehan"}
assigned = S.assign_beats([ADANI_CAND], AMBANI_SCRIPT,
                           "Markets Finance", need=4)
check("Adani portrait NOT assigned to the hero/stat scene "
      "(its text is about Ambani's gain)",
      "hero" not in assigned)
check("Adani portrait NOT assigned to the payoff scene",
      "payoff" not in assigned)
check("Adani portrait NOT assigned to news/grid either "
      "(neither names him)",
      "news" not in assigned and "grid" not in assigned)
check("Adani portrait MAY back the diaspora scene — its "
      "bullet names Gautam Adani",
      assigned.get("diaspora") is ADANI_CAND)
assigned = S.assign_beats([PROTEST_CAND], AMBANI_SCRIPT,
                           "Markets Finance", need=4)
check("'Stop Adani' protest photo NOT used as payoff "
      "filler (payoff names nobody)",
      "payoff" not in assigned)

# ── 2026-11-02: the full ladder on the Ambani story ────────
print("── 2026-11-02 ambani: full ladder ──")
AMBANI_ARTICLE = {
    "slug": "ambani-adds-6-3-billion-reliance",
    "headline": AMBANI_SCRIPT["hook_line"],
    "title": AMBANI_SCRIPT["hook_line"],
    "category": "markets-finance",
    "summary": AMBANI_SCRIPT["news_summary"],
    "body": "Mukesh Ambani added $6.3 billion. Reliance "
            "Industries shares surged. Forbes now ranks "
            "Ambani 23rd in the world and India's richest "
            "person, ahead of Gautam Adani at 26th. Gautam "
            "Adani has $79.12 billion.",
}
AMBANI_PAGES = dict(PAGES)
AMBANI_PAGES.update({
    "File:Mukesh Ambani.jpg": commons_page(
        "File:Mukesh Ambani.jpg", 268, 355,
        desc="Mukesh Ambani", cats="Mukesh Ambani"),
    f"File:{NEVADA}": NEVADA_PAGE,
    "File:Mukesh Ambani Receives CNBC India Business Award, "
    "2007.jpg": CNBC_PAGE,
    "File:ClintonTataAmbani.jpg": CLINTON_PAGE,
})
AMBANI_DEPICTS = {
    "Q298547": [{"title": f"File:{NEVADA}"},
                {"title": "File:Mukesh Ambani Receives CNBC "
                          "India Business Award, 2007.jpg"},
                {"title": "File:ClintonTataAmbani.jpg"}],
}


def ambani_net(calls):
    net = make_net(calls)
    net["commons_file_info"] = \
        lambda title: AMBANI_PAGES.get(title)
    net["depicts"] = lambda qid, limit=10: \
        AMBANI_DEPICTS.get(qid, [])
    return net


calls = []
with tempfile.TemporaryDirectory() as tmp:
    prov = S.source_extras(AMBANI_ARTICLE, AMBANI_SCRIPT,
                           Path(tmp), own_count=1,
                           log=lambda *a: None,
                           net=ambani_net(calls))
keys = extra_keys(prov)
check("ladder: the Nevada trail file is NOT produced",
      ER.file_key(NEVADA) not in keys)
check("ladder: Nevada rejection is ledgered (blocklist)",
      "blocklist" in ledger_reasons(prov)
      and NEVADA[:30] in " | ".join(
          str(r.get("candidate", ""))
          for r in prov["candidate_ledger"]))
check("ladder: genuine Ambani depicts photos ARE produced "
      "(CNBC / Clinton)",
      any("cnbc" in (e.get("path") or "").lower()
          or "clintontataambani" in (e.get("path") or "").lower()
          for e in prov["extras"]),
      str([e.get("path") for e in prov["extras"]]))
check("ladder: Ambani person photos land ONLY on scenes "
      "whose text names him (news/hero)",
      all(e["beat"] in ("news", "hero")
          for e in prov["extras"]),
      str([(e["beat"], e.get("path"))
           for e in prov["extras"]]))

# ── 2026-11-02: inline person resolution ───────────────────
print("── 2026-11-02 ambani: inline person resolution ──")
INLINE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/0/0e/"
    "Gautam_Adani_Net_Worth.jpg?utm_source=commons."
    "wikimedia.org&utm_campaign=imageinfo",
    "https://upload.wikimedia.org/wikipedia/commons/9/99/"
    "Random_Person_at_Event.jpg",
    "https://images.thedailyjagran.com/images/2026/11/02/"
    "template/image/Mukesh-Ambani-PTI-1793626671501.webp",
]


def inline_net():
    net = make_net([])
    net["depicts"] = lambda qid, limit=10: \
        [{"title": "File:Gautam Adani Net Worth.jpg"}] \
        if qid == "Q5527865" else []
    net["file_depicts"] = lambda title: \
        ["Q999999"] if "Random_Person" in title else []
    net["item_info"] = lambda qid: \
        ("Random Person", "person") if qid == "Q999999" \
        else (None, "other")
    return net


persons = S.resolve_inline_persons(
    INLINE_URLS, AMBANI_ARTICLE, AMBANI_SCRIPT,
    net=inline_net())
check("inline #1 resolves to Gautam Adani (it is his "
      "depicts file)", persons.get(0) == "Gautam Adani",
      str(persons))
check("an inline depicting a person outside the story "
      "still resolves, under that person's own name",
      persons.get(1) == "Random Person", str(persons))
check("a non-Wikimedia inline stays generic (no person)",
      2 not in persons, str(persons))

# ── the names_agree numeral veto (live dry-run find) ───────
print("── names_agree numeral veto ──")
check("'Jailer 2' does NOT agree with 'Jailer 3' (a "
      "different film)", not ER.names_agree("Jailer 2",
                                            "Jailer 3"))
check("'Jailer 2' still agrees with 'Jailer' (number dropped "
      "is not a mismatch)", ER.names_agree("Jailer 2",
                                            "Jailer"))
check("'Skyrizi' agrees with its generic name via alias",
      ER.names_agree("Skyrizi", "risankizumab", ["Skyrizi"]))

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURES: {FAILS}")
    sys.exit(1)
print("✅ all reel identity sourcing checks passed")
