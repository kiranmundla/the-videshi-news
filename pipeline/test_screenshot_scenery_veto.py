#!/usr/bin/env python3
"""
test_screenshot_scenery_veto.py — regression battery for the
SCREENSHOT / UI + SCENERY vetoes in the shared evaluator
(reel_entity_sourcing.evaluate_commons_page, 2026-11-02).

The disease: the Nov 1 identity fixes (cards 1ed2bf866,
inlines e2477cc9e) and the depicts name-agreement for persons
(31a811126) closed wrong-person / wrong-place sourcing, but
identity-VALID editorial junk still passed — the entities are
companies / topics, not persons, so no name agreement applies:

  - Microsoft exit-offer X post, card 2 (2026-11-01): a
    Surface Laptop Go photographed displaying a
    Persian-language Microsoft Word document — a depicts
    (P180) file of Microsoft (Q2283). The same file was also
    placed as the article's inline (provenance ledger
    2026-11-02T01:13:17Z).
  - Windows 11 X post, card 2 (2026-11-01): a German-language
    Windows Update UI screenshot — the P18 of Windows Update
    (Q383295) itself, filed by Commons under 'Screenshots
    by PantheraLeo1359531 in 2025'. Also placed as an inline.
  - Indiaspora H-1B X post, card 3 (2026-11-01): 'BigRiver
    .jpg', an estuary in Mendocino Headlands State Park —
    a depicts file of the United States (Q30). Identity-
    valid, editorially unrelated to the story.
  (Identifications are exact: file-page metadata + the card
  cache SHA1 key ad360caab28e514b for the river photo;
  report: goals/videshi-migration/hidden_files/
  x-batch-verify-20261101-evening/report.md.)

The fix, in the ONE evaluator every consumer shares (cards,
inlines, reels, shadow sourcer):
  1. ui_capture_subject — a candidate whose own evidence
     marks it as a software screenshot / UI capture (a
     category segment or the description naming
     'screenshot'), or whose named subject is a personal
     device displaying content (laptop / smartphone / tablet
     in title or categories), rejects for every entity and
     route. An entity that IS the device is exempt.
  2. scenery_subject + the identity-route scenery rule — a
     candidate whose evidence marks it as generic natural
     scenery (natural-feature marker, no structure or site)
     passes ONLY when its evidence also names the entity or
     an alias: the depicted place IS the entity or its own
     named site. Buildings / campuses are structure
     subjects, exempt by construction.
  3. The 3 incident files are on their entities' corpus
     blocklists in entity_registry.json (the Windows Update
     screenshot additionally under Microsoft Windows, whose
     resolution carries the same story context).

Keepers that MUST still source (real file-page metadata):
TCS SIPCOT Building (campus), NSE Exchange Plaza, Bombay
Stock Exchange 3, the Microsoft West Campus aerial, and the
Apple Park aerial — the last also guards the 2026-11-02
wildlife-veto false positive on the Commons maintenance
category 'Extracted images' ('extracted' joined the binomial
genus-stop list, same remedy as 'Blurred images' /
'People smiling' in 31a811126).

Offline: evaluator fixtures are the files' real metadata;
 card / inline paths run on the stubbed harnesses of
test_card_identity_sourcing.py / test_inline_identity
_sourcing.py with open-search seams rigged to raise.

Run: python3 test_screenshot_scenery_veto.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _p in (HERE / ".pylibs",):
    if _p.exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from PIL import Image  # noqa: E402

import social_card as sc  # noqa: E402
import article_picture_pass as P  # noqa: E402
import reel_entity_sourcing as res  # noqa: E402
import entity_resolve as ER  # noqa: E402
from verified_sourcer import registry_only_resolve  # noqa: E402

FAILS = []
PASSES = [0]


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name
          + (f" — {detail}" if detail and not cond else ""))
    if cond:
        PASSES[0] += 1
    else:
        FAILS.append(name)


# ── Commons page fixtures (the files' REAL metadata) ───────
def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats="", mime="image/jpeg"):
    return {"title": title,
            "imageinfo": [{
                "url": "https://upload.wikimedia.org/wikipedia/"
                       "commons/"
                       + title.removeprefix("File:").replace(
                           " ", "_"),
                "descriptionurl": "https://commons.wikimedia.org/"
                                  "wiki/" + title.replace(
                                      " ", "_"),
                "width": w, "height": h, "mime": mime,
                "extmetadata": {
                    "ImageDescription": {"value": desc},
                    "Categories": {"value": cats},
                    "LicenseShortName": {"value": license_short},
                    "Artist": {"value": "Fixture Photographer"},
                }}]}


LAPTOP = "A platinum Microsoft Surface Laptop Go.jpg"
LAPTOP_PAGE = commons_page(
    f"File:{LAPTOP}", 2201, 1791,
    desc="a platinum Microsoft Surface Laptop Go",
    cats="Buildings in Sirjan|Self-published work|Files with "
         "coordinates missing SDC location of creation|2010s "
         "laptops|Surface Laptop Go")
WINUPDATE = ("Windows Update – VirtualBox Windows 11 24H2 "
             "(Version 10.0.26100.1742) 04 02 2025 18 22 "
             "13crop.png")
WINUPDATE_PAGE = commons_page(
    f"File:{WINUPDATE}", 2497, 783, license_short="Public domain",
    desc="About box of Windows 11 24H2.",
    cats="Windows Update|PD text|PD-text missing SDC copyright "
         "status|Files uploaded by PantheraLeo1359531|"
         "Screenshots by PantheraLeo1359531 in 2025|Windows 11, "
         "version 24H2",
    mime="image/png")
BIGRIVER = "BigRiver.jpg"
BIGRIVER_PAGE = commons_page(
    f"File:{BIGRIVER}", 3072, 2048, license_short="CC BY-SA 2.5",
    desc="Big River , in the Big River Unit of Mendocino "
         "Headlands State Park , Mendocino, California.",
    cats="Taken with Canon EOS D60|Big River (California)|"
         "Files with coordinates missing SDC location of "
         "creation|Files by User:David Eppstein from "
         "en.wikipedia")

TCS_PAGE = commons_page(
    "File:TCS SIPCOT Building.jpg", 4032, 2399,
    desc="SIPCOT TCS OFFICE",
    cats="Self-published work|Images from Wiki Loves Earth "
         "2017 in India|FoP-India|Uploaded via Campaign:wle-in|"
         "Files with coordinates missing SDC location of "
         "creation|Images from Wiki Loves Earth 2017|India "
         "photographs taken on 2017-05-31|Images from Wiki "
         "Loves Earth missing SDC depicts|Images from Wiki "
         "Loves Earth missing SDC location of creation|TCS "
         "Siruseri Campus")
NSE_PAGE = commons_page(
    "File:NSE Exchange Plaza.jpg", 5760, 3840,
    desc="National Stock Exchange of India Corporate Office",
    cats="Buildings in India|Self-published work")
# The file's real pixel size (428x572) is below the evaluator
# floor — the fixture carries card-suite dimensions so the
# VETO behaviour is what is exercised, not the dims gate.
BSE_PAGE = commons_page(
    "File:Bombay Stock Exchange 3.jpg", 2291, 1917,
    license_short="CC BY-SA 2.0",
    desc="The Mumbai Stock Exchange stands tall, and is "
         "scaling new heights",
    cats="Flickr images reviewed by FlickreviewR|Phiroze "
         "Jeejeebhoy Towers")
MS_CAMPUS_PAGE = commons_page(
    "File:Aerial Microsoft West Campus August 2009.jpg",
    4752, 3168, license_short="Public domain",
    desc="The west campus of Microsoft, Redmond, Washington, "
         "taken from about 1,500'. The photo is looking "
         "south-east. The west campus is bounded on the west "
         "by 148th Ave, on the east by SR 520, and on the "
         "north (foreground) by 40th St.",
    cats="Microsoft Redmond campus|Taken with Canon EOS 500D|"
         "Self-published work|PD-self|Aerial photographs of "
         "Redmond, Washington")
APPLE_PARK_PAGE = commons_page(
    "File:Aerial view of Apple Park.jpg", 6179, 3476,
    desc="Aerial view of Apple Park , the corporate "
         "headquarters of Apple Inc. , located in Cupertino , "
         "California . The roof is covered in solar panels "
         "with an output of 17 MW p , making it one of the "
         "biggest solar roofs in the world . Photo taken from "
         "a Cessna 172M .",
    cats="April 2018 in California|Self-published work|"
         "Extracted images|FoP-United States|Files with "
         "coordinates missing SDC location of creation|Aerial "
         "photographs of Apple Park")

EV = res.evaluate_commons_page


def ev(page, entity, route, type_=None, aliases=(),
       blocked_keys=None):
    return EV(page, entity, route, identity_verified=True,
              blocked_keys=blocked_keys, entity_type=type_,
              entity_aliases=list(aliases))


def real_blocked(name):
    r = registry_only_resolve(name, "")
    return {ER.file_key(b) for b in (r or {}).get(
        "blocked_files") or []}


# ══ 1. The veto helpers on the incident evidence ═══════════
check("helper: laptop file is a ui-capture subject",
      res.ui_capture_subject(
          "Microsoft", f"File:{LAPTOP}",
          "a platinum Microsoft Surface Laptop Go",
          "Buildings in Sirjan|2010s laptops|Surface Laptop Go"))
check("helper: Windows Update P18 is a ui-capture subject",
      res.ui_capture_subject(
          "Windows Update", f"File:{WINUPDATE}",
          "About box of Windows 11 24H2.",
          "Windows Update|Screenshots by PantheraLeo1359531 "
          "in 2025"))
check("helper: BigRiver is a scenery subject",
      res.scenery_subject(
          f"File:{BIGRIVER}",
          "Big River , in the Big River Unit of Mendocino "
          "Headlands State Park , Mendocino, California.",
          "Big River (California)"))
check("helper: TCS campus is NOT a scenery subject",
      not res.scenery_subject(
          "File:TCS SIPCOT Building.jpg", "SIPCOT TCS OFFICE",
          "TCS Siruseri Campus"))
check("helper: Microsoft campus is NOT a scenery subject",
      not res.scenery_subject(
          "File:Aerial Microsoft West Campus August 2009.jpg",
          "The west campus of Microsoft, Redmond, Washington",
          "Microsoft Redmond campus"))

# ══ 2. Evaluator: the 3 bad files reject on the VETO ═══════
# (blocked_keys=None — the rule itself must fire, the
# blocklist is only the second layer.)
cand, row = ev(LAPTOP_PAGE, "Microsoft",
               "identity — depicts (P180) of Q2283",
               type_="company", aliases=["Microsoft"])
check("evaluator: laptop depicts file rejected (ui-capture)",
      cand is None and "ui-capture" in row["reason"],
      row["reason"])
cand, row = ev(WINUPDATE_PAGE, "Windows Update",
               "identity — P18 of Q383295", type_="other",
               aliases=["Windows Update",
                        "Microsoft Windows Update"])
check("evaluator: Windows Update screenshot P18 rejected "
      "(ui-capture)",
      cand is None and "ui-capture" in row["reason"],
      row["reason"])
cand, row = ev(BIGRIVER_PAGE, "United States",
               "identity — depicts (P180) of Q30", type_="other",
               aliases=["United States"])
check("evaluator: BigRiver depicts file rejected (scenery)",
      cand is None and "scenery" in row["reason"],
      row["reason"])

# ══ 3. Evaluator: the blocklist layer fires first ══════════
cand, row = ev(LAPTOP_PAGE, "Microsoft",
               "identity — depicts (P180) of Q2283",
               type_="company", aliases=["Microsoft"],
               blocked_keys=real_blocked("Microsoft"))
check("evaluator: laptop rejected by the corpus blocklist",
      cand is None and "blocklist" in row["reason"],
      row["reason"])
cand, row = ev(WINUPDATE_PAGE, "Windows Update",
               "identity — P18 of Q383295", type_="other",
               aliases=["Windows Update"],
               blocked_keys=real_blocked("Windows Update"))
check("evaluator: Windows Update screenshot rejected by "
      "the corpus blocklist",
      cand is None and "blocklist" in row["reason"],
      row["reason"])
cand, row = ev(BIGRIVER_PAGE, "United States",
               "identity — depicts (P180) of Q30", type_="other",
               aliases=["United States"],
               blocked_keys=real_blocked("United States"))
check("evaluator: BigRiver rejected by the corpus blocklist",
      cand is None and "blocklist" in row["reason"],
      row["reason"])
check("registry: the 3 incident files are blocklisted",
      ER.blocked_file("Microsoft", f"File:{LAPTOP}")
      and ER.blocked_file("Windows Update",
                          f"File:{WINUPDATE}")
      and ER.blocked_file("Microsoft Windows",
                          f"File:{WINUPDATE}")
      and ER.blocked_file("United States",
                          f"File:{BIGRIVER}"))
check("registry: the Microsoft campus keeper is NOT blocked",
      not ER.blocked_file(
          "Microsoft",
          "File:Aerial Microsoft West Campus August 2009.jpg"))

# ══ 4. Evaluator: the 5 keepers still source ═══════════════
KEEPERS = [
    ("TCS SIPCOT Building", TCS_PAGE, "Tata Consultancy "
     "Services", "identity — P18 of Q13227919", "company",
     ["Tata Consultancy Services", "TCS"]),
    ("NSE Exchange Plaza", NSE_PAGE, "National Stock "
     "Exchange of India", "identity — P18 of Q638740",
     "company", ["National Stock Exchange of India"]),
    ("Bombay Stock Exchange 3", BSE_PAGE, "Bombay Stock "
     "Exchange", "identity — depicts (P180) of Q000000",
     "company", ["Bombay Stock Exchange"]),
    ("Microsoft West Campus aerial", MS_CAMPUS_PAGE,
     "Microsoft", "identity — P18 of Q2283", "company",
     ["Microsoft"]),
    ("Apple Park aerial", APPLE_PARK_PAGE, "Apple Inc.",
     "identity — P18 of Q312", "company",
     ["Apple Inc.", "Apple"]),
]
for label, page, ent, route, type_, aliases in KEEPERS:
    cand, row = ev(page, ent, route, type_=type_,
                   aliases=aliases)
    check(f"evaluator keeper: {label} still sources",
          cand is not None, row["reason"])

# ══ 5. Exemptions are narrow, not blanket ══════════════════
cand, row = ev(LAPTOP_PAGE, "Surface Laptop Go",
               "identity — depicts (P180) of Q000001",
               type_="other", aliases=["Surface Laptop Go"])
check("exemption: the device itself (Surface Laptop Go) "
      "still sources its own product photo",
      cand is not None, row["reason"])
cand, row = ev(BIGRIVER_PAGE, "Mendocino Headlands State "
               "Park", "identity — depicts (P180) of Q000002",
               type_="place",
               aliases=["Mendocino Headlands State Park"])
check("exemption: the depicted place AS the entity "
      "(Mendocino Headlands State Park) still sources",
      cand is not None, row["reason"])

# ══ 6. CARD path (social_card._entity_image_for_card) ══════
PAGES = {}
DEPICTS = {}
DOWNLOADS = []


def resolution(name, qid, type_="other", p18=None,
               blocked=(), aliases=()):
    return {"name": name, "aliases": list(aliases) or [name],
            "qid": qid, "p18_file": p18, "type": type_,
            "method": "registry", "confidence": "high",
            "blocked_files": list(blocked), "notes": ""}


def card_net(resolutions):
    def _file_info(title):
        return PAGES.get(title if title.startswith("File:")
                         else f"File:{title}")
    return {"resolve_entity":
            lambda name, ctx="": resolutions.get(name),
            "depicts": lambda qid: [
                {"title": t} if isinstance(t, str) else t
                for t in DEPICTS.get(qid, [])],
            "commons_file_info": _file_info}


def _fake_download(url):
    DOWNLOADS.append(url)
    return Image.new("RGB", (1600, 1200), (20, 30, 50)), \
        object()


sc._download_entity_image = _fake_download


def _boom(*a, **k):
    raise AssertionError("open search called on the card path")


res.commons_search = _boom
res.brave_links = _boom
_orig_card_entities = sc._card_entities


def card_source(entities, net):
    sc._card_entities = lambda text, ctx: list(entities)
    try:
        return sc._entity_image_for_card(
            "card text", {}, [], net=net)
    finally:
        sc._card_entities = _orig_card_entities


def produced_file(got):
    return None if got is None else got[2]["file_url"]


MS_RES = resolution("Microsoft", "Q2283", type_="company",
                    p18="Aerial Microsoft West Campus "
                        "August 2009.jpg")
PAGES.update({p["title"]: p for p in
              [LAPTOP_PAGE, MS_CAMPUS_PAGE]})
DEPICTS.update({"Q2283": [f"File:{LAPTOP}"]})
got = card_source(["Microsoft"], card_net(
    {"Microsoft": MS_RES}))
check("card path: Microsoft sources its campus, never the "
      "laptop depicts file",
      produced_file(got) is not None
      and "West_Campus" in produced_file(got),
      str(produced_file(got)))
MS_RES_NOP18 = resolution("Microsoft", "Q2283",
                          type_="company", p18=None)
got = card_source(["Microsoft"], card_net(
    {"Microsoft": MS_RES_NOP18}))
check("card path: laptop-only Microsoft offer fails closed "
      "to navy", got is None)

PAGES.update({WINUPDATE_PAGE["title"]: WINUPDATE_PAGE})
WU_RES = resolution("Windows Update", "Q383295",
                    p18=WINUPDATE,
                    aliases=["Windows Update",
                             "Microsoft Windows Update"])
got = card_source(["Windows Update"], card_net(
    {"Windows Update": WU_RES}))
check("card path: Windows Update screenshot P18 fails "
      "closed to navy", got is None)

PAGES.update({BIGRIVER_PAGE["title"]: BIGRIVER_PAGE})
US_RES = resolution("United States", "Q30", p18=None)
DEPICTS.update({"Q30": [f"File:{BIGRIVER}"]})
got = card_source(["United States"], card_net(
    {"United States": US_RES}))
check("card path: BigRiver-only United States offer fails "
      "closed to navy", got is None)

PAGES.update({TCS_PAGE["title"]: TCS_PAGE,
              APPLE_PARK_PAGE["title"]: APPLE_PARK_PAGE})
TCS_RES = resolution("Tata Consultancy Services",
                     "Q13227919", type_="company",
                     p18="TCS SIPCOT Building.jpg",
                     aliases=["Tata Consultancy Services",
                              "TCS"])
got = card_source(["Tata Consultancy Services"], card_net(
    {"Tata Consultancy Services": TCS_RES}))
check("card path keeper: TCS SIPCOT campus still sources",
      produced_file(got) is not None
      and "TCS_SIPCOT" in produced_file(got),
      str(produced_file(got)))
APPLE_RES = resolution("Apple Inc.", "Q312", type_="company",
                       p18="Aerial view of Apple Park.jpg",
                       aliases=["Apple Inc.", "Apple"])
got = card_source(["Apple Inc."], card_net(
    {"Apple Inc.": APPLE_RES}))
check("card path keeper: Apple Park aerial still sources",
      produced_file(got) is not None
      and "Apple_Park" in produced_file(got),
      str(produced_file(got)))

# ══ 7. INLINE path (article_picture_pass._source_inlines) ══
def identity_net(resolutions=None, depicts_by_qid=None,
                 pages_by_title=None, items_by_qid=None,
                 cache=None):
    calls = {"search": []}

    def _boom_search(q, limit=10):
        calls["search"].append(q)
        raise AssertionError(
            "open Commons search consulted by the inline "
            "route")

    def _boom_brave(q, n=8):
        calls["search"].append(q)
        raise AssertionError(
            "Brave discovery consulted by the inline route")

    return {
        "commons_search": _boom_search,
        "brave_links": _boom_brave,
        "fetch_text": lambda url, timeout=15: "",
        "commons_file_info":
            lambda title: (pages_by_title or {}).get(title),
        "verify_url": lambda url: {"ok": True, "width": 2400},
        "person_cache": lambda name: (cache or {}).get(name),
        "download_verify": lambda url, dest: [2400, 1500],
        "resolve_entity":
            lambda name, context="":
                (resolutions or {}).get(name),
        "depicts": lambda qid, limit=10:
            (depicts_by_qid or {}).get(qid, []),
        "wikidata_item":
            lambda qid: (items_by_qid or {}).get(qid),
    }


def ent(name, kind="org/place"):
    return {"name": name, "kind": kind, "source": "headline",
            "sourceable": True}


def run_inlines(article, ents, net, want=3):
    rec = {"ledger": [], "notes": []}
    return P._source_inlines(article, [ent(e) for e in ents],
                             "", net, want, set(), rec,
                             lambda *a: None), rec


ARTICLE = {"slug": "veto-regression",
           "headline": "Veto regression fixture",
           "body": "Fixture body."}
ALL_INLINE_PAGES = {p["title"]: p for p in [
    LAPTOP_PAGE, WINUPDATE_PAGE, BIGRIVER_PAGE, TCS_PAGE]}

picks, _ = run_inlines(
    ARTICLE, ["Microsoft"],
    identity_net(
        resolutions={"Microsoft": resolution(
            "Microsoft", "Q2283", type_="company")},
        depicts_by_qid={"Q2283": [{"title": f"File:{LAPTOP}"}]},
        pages_by_title=ALL_INLINE_PAGES))
check("inline path: laptop depicts file yields no inline",
      picks == [], str([p.get("title") for p in picks]))

picks, _ = run_inlines(
    ARTICLE, ["Windows Update"],
    identity_net(
        resolutions={"Windows Update": resolution(
            "Windows Update", "Q383295", p18=WINUPDATE,
            aliases=["Windows Update",
                     "Microsoft Windows Update"])},
        pages_by_title=ALL_INLINE_PAGES))
check("inline path: Windows Update screenshot P18 yields "
      "no inline", picks == [],
      str([p.get("title") for p in picks]))

picks, _ = run_inlines(
    ARTICLE, ["United States"],
    identity_net(
        resolutions={"United States": resolution(
            "United States", "Q30")},
        depicts_by_qid={"Q30": [{"title": f"File:{BIGRIVER}"}]},
        pages_by_title=ALL_INLINE_PAGES))
check("inline path: BigRiver depicts file yields no inline",
      picks == [], str([p.get("title") for p in picks]))

picks, _ = run_inlines(
    ARTICLE, ["Tata Consultancy Services"],
    identity_net(
        resolutions={"Tata Consultancy Services": resolution(
            "Tata Consultancy Services", "Q13227919",
            type_="company", p18="TCS SIPCOT Building.jpg",
            aliases=["Tata Consultancy Services", "TCS"])},
        pages_by_title=ALL_INLINE_PAGES))
check("inline path keeper: TCS SIPCOT campus still sources "
      "an inline",
      len(picks) == 1
      and "TCS SIPCOT" in (picks[0].get("title") or ""),
      str([p.get("title") for p in picks]))

print()
print(f"{PASSES[0]} passed, {len(FAILS)} failed")
if FAILS:
    print("FAILURES:", FAILS)
    sys.exit(1)
print("ALL PASS")
