#!/usr/bin/env python3
"""
test_card_identity_sourcing.py — regression battery for the
CARD path's identity-only entity sourcing (social_card.py,
2026-11-01), the card-path twin of
test_reel_identity_sourcing.py.

The disease: _entity_image_for_card keyword-searched Commons /
Brave by entity name (routes A/B/C) and policed the hits with
token gates. The gates kept losing to namesakes and token
collisions, and the wrong photos reached LIVE X posts and
queued decks:

  - 'STAR' (the NEERI green-cracker acronym) → a Hubble
    starburst galaxy photo — Green Crackers post, X
    2026-11-01, tweet 2116916453488075016.
  - 'OTT' (streaming abbreviation) → a portrait of Ott
    Järvela, an Estonian sports journalist — Manoj Bajpayee
    deck, X 2026-10-31.
  - 'New York' (place) → 'September 14 2001.jpg', a 9/11
    Ground Zero photo — Bhavitha Mandava deck, X 2026-10-31.
  - the Ramayana Part 1 review deck (X 2026-11-01) → an 1835
    East India Company 2 Mohurs coin and a Pentagon photo of
    US Deputy Secretary of Defense Kathleen Hicks.
  - the IAF-chief deck (X 2026-11-01) → portraits of Maharaja
    Ranjit Singh and Hugh Trenchard for a story about Air
    Marshal Ashutosh Dixit.
  - the Jailer 2 decks (2026-11-01) → 'Karnataka Rs' sourced
    a Dudda RS town photo; 'South India' a Darasuram temple
    night photo.

The fix mirrors the reel fix (afc1c643e): open search is
ABOLISHED on the card path. Entities are triaged (outlet →
language → category label), resolved through entity_resolve
(registry-first), and the only candidates are the resolved
Wikidata item's P18 and depicts (P180) files, each re-run
through the shared file gates plus the entity's corpus
blocklist. A single-token entity may source only through the
curated registry (a bare token's live label agreement cannot
tell a company from a common noun). Anything unresolved,
ambiguous, low-confidence or identity-mismatched fails
closed to a navy text card.

The wrong files above were identified EXACTLY (SHA1 match
against the card download cache, 2026-11-01) and seeded into
entity_registry.json's corpus blocklist; this suite proves
the blocklist fires at the evaluator and that the files can
never be produced again, while proven keepers (the exchanges'
own buildings, the White House P18, the IAF chief's own
portrait, Kathleen Hicks's own portrait when she IS the
entity) still source.

Offline: resolution is verified_sourcer.registry_only_resolve
(the real registry), depicts / file-info are fixtures, the
download is stubbed, and reel_entity_sourcing's open-search
seams are rigged to raise — if any code path ever calls them
again, this suite fails loudly.

Run: python3 test_card_identity_sourcing.py
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
import reel_entity_sourcing as res  # noqa: E402
import entity_resolve as ER  # noqa: E402
from verified_sourcer import registry_only_resolve  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


# ── Commons page fixtures (real file metadata) ─────────────
def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats=""):
    return {"title": title,
            "imageinfo": [{
                "url": "https://upload.wikimedia.org/wikipedia/"
                       "commons/"
                       + title.removeprefix("File:").replace(
                           " ", "_"),
                "descriptionurl": "https://commons.wikimedia.org/"
                                  "wiki/" + title.replace(" ", "_"),
                "width": w, "height": h, "mime": "image/jpeg",
                "extmetadata": {
                    "ImageDescription": {"value": desc},
                    "Categories": {"value": cats},
                    "LicenseShortName": {"value": license_short},
                    "Artist": {"value": "Fixture Photographer"},
                }}]}


def png_page(title, w, h, **kw):
    page = commons_page(title, w, h, **kw)
    page["imageinfo"][0]["mime"] = "image/png"
    return page


# The wrong files — SHA1-exact identifications (2026-11-01).
WTC = "September 14 2001.jpg"
WTC_PAGE = commons_page(
    f"File:{WTC}", 1312, 2000, license_short="Public domain",
    desc="The World Trade Center on September 14, 2001, "
         "during rescue and recovery operations at Ground Zero.",
    cats="World Trade Center|September 11 attacks")
JARVELA = ("Ott Järvela at the Opinion Festival 2022 in "
           "Paide, Estonia.jpg")
JARVELA_PAGE = commons_page(
    f"File:{JARVELA}", 5616, 3744,
    desc="Ott Järvela at the Opinion Festival 2022 in Paide, "
         "Estonia.", cats="Ott Järvela|Opinion Festival 2022")
COIN = "India 1835 2 Mohurs.jpg"
COIN_PAGE = commons_page(
    f"File:{COIN}", 5752, 2923,
    desc="Two mohurs, East India Company, 1835. The reverse "
         "depicts Rama, hero of the Ramayana.",
    cats="Coins of British India|Rama")
HICKS_MEETING = ("United States Deputy Secretary of Defense "
                 "Kathleen Hicks meets with India Foreign "
                 "Secretary Vikram Misri at the Pentagon, USA "
                 "on September 25, 2024 - 1.jpg")
HICKS_MEETING_PAGE = commons_page(
    f"File:{HICKS_MEETING}", 4348, 2899,
    license_short="Public domain",
    desc="Deputy Secretary of Defense Kathleen Hicks meets "
         "with Indian Foreign Secretary Vikram Misri at the "
         "Pentagon, Washington, D.C.",
    cats="Kathleen Hicks|Vikram Misri")
RANJIT = ("A portrait of Maharaja Ranjit Singh seated with "
          "Dhian Singh and Kharak Singh.jpg")
RANJIT_PAGE = commons_page(
    f"File:{RANJIT}", 2048, 2466, license_short="Public domain",
    desc="A portrait of Maharaja Ranjit Singh seated with "
         "Dhian Singh and Kharak Singh.",
    cats="Ranjit Singh|Paintings")
TRENCHARD = ("Hugh Trenchard was the first Chief of the Air "
             "Staff, presiding over the foundation of the RAF "
             "in 1918, when the Royal Naval Air Service and "
             "the Royal Flying Corps were united as the new "
             "Royal Air Force. Art.IWMART325.jpg")
TRENCHARD_PAGE = commons_page(
    f"File:{TRENCHARD}", 6842, 8247,
    license_short="Public domain",
    desc="Hugh Trenchard was the first Chief of the Air "
         "Staff, presiding over the foundation of the RAF "
         "in 1918.", cats="Hugh Trenchard|Imperial War Museum")
STARBURST = ("Starburst in NGC 4449 (captured by the Hubble "
             "Space Telescope).jpg")
STARBURST_PAGE = commons_page(
    f"File:{STARBURST}", 8736, 5630,
    license_short="Public domain",
    desc="A starburst galaxy, NGC 4449, captured by the "
         "Hubble Space Telescope.",
    cats="NGC 4449|Hubble Space Telescope")
DUDDA = "Dudda RS town, Hassan.jpg"
DUDDA_PAGE = commons_page(
    f"File:{DUDDA}", 1401, 1097,
    desc="Dudda RS town, Hassan district, Karnataka.",
    cats="Hassan district")
DARASURAM = ("Darasuram, Airavatesvara Temple, Mandapa at "
             "night 4, India.jpg")
DARASURAM_PAGE = commons_page(
    f"File:{DARASURAM}", 4032, 2688,
    desc="Darasuram, Airavatesvara Temple, mandapa at night, "
         "Tamil Nadu, India.",
    cats="Airavatesvara Temple|Darasuram")

# Keepers — the resolved items' own files.
NYC_P18 = ("NYC Downtown Manhattan Skyline seen from Paulus "
           "Hook 2019-12-20 IMG 7347 FRD (cropped).jpg")
NYC_P18_PAGE = commons_page(
    f"File:{NYC_P18}", 3869, 2580,
    desc="Downtown Manhattan skyline, New York City, seen "
         "from Paulus Hook.",
    cats="Skyline of Manhattan|New York City in December "
         "2019|Hudson River")
NSE_PLAZA_PAGE = commons_page(
    "File:NSE Exchange Plaza.jpg", 5760, 3840,
    desc="National Stock Exchange of India Corporate Office",
    cats="Buildings in India|Self-published work")
BSE_P18_PAGE = commons_page(
    "File:Bombay Stock Exchange 3.jpg", 2291, 1917,
    license_short="CC BY 2.0",
    desc="The Bombay Stock Exchange building in Mumbai, "
         "India", cats="Phiroze Jeejeebhoy Towers")
WH_P18_PAGE = commons_page(
    "File:WhiteHouseSouthFacade.JPG", 4000, 2667,
    desc="The White House south facade, Washington, D.C.",
    cats="White House")
MS_P18_PAGE = commons_page(
    "File:Aerial Microsoft West Campus August 2009.jpg",
    4000, 3000,
    desc="Aerial view of the Microsoft West Campus, Redmond, "
         "Washington.", cats="Microsoft campus")
SC_P18_PAGE = commons_page(
    "File:Supreme Court of India 01.jpg", 4000, 2667,
    desc="The Supreme Court of India building, New Delhi.",
    cats="Supreme Court of India")
US_COURT_PAGE = commons_page(
    "File:US Supreme Court Building.jpg", 4000, 2667,
    desc="The Supreme Court of the United States, "
         "Washington, D.C.", cats="Supreme Court of the "
    "United States")
DIXIT_P18 = "Air Marshal Ashutosh Dixit, VCAS.png"
DIXIT_PAGE = png_page(
    f"File:{DIXIT_P18}", 1145, 1421,
    license_short="Public domain",
    desc="Air Marshal Ashutosh Dixit, Vice Chief of the Air "
         "Staff, Indian Air Force.",
    cats="Ashutosh Dixit|Indian Air Force")
HICKS_P18 = "Kathleen H. Hicks, Deputy Secretary of Defense.jpg"
HICKS_P18_PAGE = commons_page(
    f"File:{HICKS_P18}", 2240, 2800,
    license_short="Public domain",
    desc="Kathleen H. Hicks, Deputy Secretary of Defense, "
         "official portrait.", cats="Kathleen Hicks")
CAT_HQ_PAGE = commons_page(
    "File:Caterpillarhq.JPG", 2816, 2112,
    license_short="Public domain",
    desc="Caterpillar Inc. world headquarters, Peoria, "
         "Illinois.", cats="Caterpillar Inc.")
CAT_INSECT_PAGE = commons_page(
    "File:Chenille chevrefeuille.jpg", 2272, 1704,
    desc="Chenille chevrefeuille — a caterpillar (larva) on "
         "honeysuckle.", cats="Lepidoptera larvae")
SOUDHA_PAGE = commons_page(
    "File:Vidhana Soudha Bangalore.jpg", 4000, 3000,
    desc="Vidhana Soudha, seat of the Karnataka state "
         "legislature, Bangalore.",
    cats="Vidhana Soudha|Bangalore")
REGION_MAP_PAGE = commons_page(
    "File:South India region map.png", 2000, 2200,
    desc="Map of the South India region.",
    cats="Maps of South India")
KEITH_PAGE = commons_page(
    "File:Keith Sonderling (55510883049).jpg", 8192, 5464,
    desc="Acting U.S. Secretary of Labor Keith Sonderling "
         "speaking at a leadership summit.",
    cats="Keith Sonderling")
CAMPAGNOLO_PAGE = commons_page(
    "File:Campagnolo Super Record EPS rear derailleur.jpg",
    4000, 3000,
    desc="Campagnolo Super Record EPS electronic bicycle "
         "groupset.", cats="Campagnolo")

ALL_PAGES = {p["title"]: p for p in [
    WTC_PAGE, JARVELA_PAGE, COIN_PAGE, HICKS_MEETING_PAGE,
    RANJIT_PAGE, TRENCHARD_PAGE, STARBURST_PAGE, DUDDA_PAGE,
    DARASURAM_PAGE, NYC_P18_PAGE, NSE_PLAZA_PAGE, BSE_P18_PAGE,
    WH_P18_PAGE, MS_P18_PAGE, SC_P18_PAGE, US_COURT_PAGE,
    DIXIT_PAGE, HICKS_P18_PAGE, CAT_HQ_PAGE, CAT_INSECT_PAGE,
    SOUDHA_PAGE, REGION_MAP_PAGE, KEITH_PAGE,
    CAMPAGNOLO_PAGE]}


# ── stubbed network ────────────────────────────────────────
PAGES = {}
DEPICTS = {}
FILE_INFO_CALLS = []
DOWNLOADS = []


def make_net(resolve=registry_only_resolve):
    def _file_info(title):
        FILE_INFO_CALLS.append(title)
        return PAGES.get(title if title.startswith("File:")
                         else f"File:{title}")
    return {"resolve_entity": resolve,
            # production depicts_candidates yields dicts —
            # fixtures author titles, the stub wraps them into
            # the production shape.
            "depicts": lambda qid: [
                {"title": t} if isinstance(t, str) else t
                for t in DEPICTS.get(qid, [])],
            "commons_file_info": _file_info}


def _fake_download(url):
    DOWNLOADS.append(url)
    img = Image.new("RGB", (1600, 1200), (20, 30, 50))
    return img, object()


_orig_download = sc._download_entity_image
sc._download_entity_image = _fake_download

# Open search is abolished: rig the seams to explode so any
# regression that calls them fails this suite loudly.
def _boom(*a, **k):
    raise AssertionError("open search called on the card path")


_orig_search = res.commons_search
_orig_links = res.brave_links
res.commons_search = _boom
res.brave_links = _boom

_orig_card_entities = sc._card_entities


def pin(entities):
    sc._card_entities = lambda text, ctx: list(entities)


def unpin():
    sc._card_entities = _orig_card_entities


def source(text, ctx, entities=None, net=None):
    if entities is not None:
        pin(entities)
    try:
        return sc._entity_image_for_card(
            text, ctx, [], net=net or make_net())
    finally:
        if entities is not None:
            unpin()


def reset(pages=None, depicts=None):
    PAGES.clear()
    PAGES.update(pages if pages is not None else ALL_PAGES)
    DEPICTS.clear()
    DEPICTS.update(depicts or {})
    FILE_INFO_CALLS.clear()
    DOWNLOADS.clear()


def produced_file(got):
    return None if got is None else got[2]["file_url"]


def resolve_no_p18(name, ctx):
    """The real registry resolution with the P18 unavailable —
    models the depicts route carrying the card (and exercises
    the corpus blocklist at the evaluator)."""
    r = registry_only_resolve(name, ctx)
    if r:
        r = dict(r, p18_file=None)
    return r


# ── contexts ───────────────────────────────────────────────
GC_CTX = {
    "headline": "Green Crackers for Diwali 2026: Types, "
                "Rules and How to Verify the QR Code",
    "body": "CSIR-NEERI has certified green cracker "
            "formulations including SWAS, SAFAL, SHHL and "
            "STAR, which cut emissions by up to 30 percent.",
    "slug": "green-crackers-diwali-2026-types-rules-verify-qr",
    "category": "news"}
OTT_CTX = {
    "headline": "Manoj Bajpayee Says OTT Has Given Sidelined "
                "Actors Respect and a Living",
    "body": "Manoj Bajpayee said streaming platforms have "
            "changed casting in Mumbai.",
    "slug": "manoj-bajpayee-ott-sidelined-actors",
    "category": "entertainment"}
BHAVITHA_CTX = {
    "headline": "Bhavitha Mandava Rings the Award Bell for "
                "Chanel in Hyderabad",
    "body": "The model from Hyderabad walked for Chanel in "
            "New York this week.",
    "slug": "bhavitha-mandava-instagram-rings-award-chanel",
    "category": "entertainment"}
RAMAYANA_CTX = {
    "headline": "Ramayana Part 1 Review: Critics Praise the "
                "Spectacle, Split on the Story",
    "body": "Nitesh Tiwari's Ramayana Part 1, starring "
            "Ranbir Kapoor as Rama and Sai Pallavi as Sita, "
            "opened to packed houses.",
    "slug": "ramayana-part-1-review-critics-praise",
    "category": "entertainment"}
IAF_CTX = {
    "headline": "Ashutosh Dixit Takes Charge as the 29th "
                "Chief of the Indian Air Force",
    "body": "Air Marshal Ashutosh Dixit took charge as the "
            "29th Chief of the Air Staff in New Delhi.",
    "slug": "ashutosh-dixit-takes-charge-29th-iaf-chief",
    "category": "news"}
JAILER_CTX = {
    "headline": "Jailer 2 First Indian Film to Cross Rs 75 "
                "Crore in All Four South Markets",
    "body": "Rajinikanth's sequel crossed Rs 75 crore in "
            "Karnataka and Tamil Nadu, trade reports said.",
    "slug": "jailer-2-first-film-75-crore-all-four-south",
    "category": "entertainment"}
MARKET_CTX = {
    "headline": "Sensex Surges 905 Points as Banking Stocks "
                "Lead",
    "body": "Indian equity benchmarks rallied on Thursday.",
    "slug": "sensex-surges-905-points", "category":
    "markets-finance"}
CAT_CTX = {
    "headline": "Caterpillar Earnings Preview: EPS Seen at "
                "$5.54 as Machinery Demand Cools",
    "body": "Caterpillar is expected to report quarterly "
            "earnings on Thursday.",
    "slug": "caterpillar-earnings-preview",
    "category": "markets-finance"}
SC_CTX = {
    "headline": "Supreme Court Rules Out Blanket Firecracker "
                "Ban",
    "body": "The Supreme Court of India refused a blanket "
            "ban ahead of Diwali.",
    "slug": "supreme-court-firecracker-ban",
    "category": "news"}
HICKS_CTX = {
    "headline": "Kathleen Hicks to Lead Pentagon Review of "
                "Pacific Posture",
    "body": "Deputy Secretary of Defense Kathleen Hicks "
            "will lead the review.",
    "slug": "kathleen-hicks-pentagon-review",
    "category": "news"}


# ═══ 0. the abolition invariants ═══════════════════════════
net = sc._card_net()
check("card net exposes ONLY identity seams (no search)",
      set(net) == {"resolve_entity", "depicts",
                   "commons_file_info"},
      str(sorted(net)))

# ═══ 1. STAR → Hubble starburst (Green Crackers) ═══════════
reset()
got = source("NEERI's STAR formulation uses iron oxide "
             "instead of barium nitrate.", GC_CTX)
check("STAR card: no photo (real extraction, registry "
      "guard)", got is None)
check("STAR card: starburst file never requested",
      not any("Starburst" in t for t in FILE_INFO_CALLS),
      str(FILE_INFO_CALLS))

def _live_star(name, ctx):
    return {"query": name, "name": "Star", "aliases": ["Star"],
            "qid": "Q523", "p18_file": STARBURST,
            "p18_quality": 8736, "type": "other",
            "method": "live", "confidence": "high",
            "confusables": [], "blocked_files": [],
            "notes": ""}


reset()
got = source("STAR crackers cut emissions by 30 percent.",
             GC_CTX, entities=["STAR"],
             net=make_net(resolve=_live_star))
check("STAR card: even a live 'Star' (Q523) resolution "
      "fails closed — single-token registry-only rule",
      got is None)
check("STAR card: starburst never requested on the live "
      "route either",
      not any("Starburst" in t for t in FILE_INFO_CALLS))

# ═══ 2. OTT → Ott Järvela ══════════════════════════════════
reset()
got = source("OTT platforms have given sidelined actors "
             "respect and living wages.", OTT_CTX)
check("OTT card: no photo (registry no-identity guard)",
      got is None)
check("OTT card: Järvela portrait never requested",
      not any("Järvela" in t for t in FILE_INFO_CALLS),
      str(FILE_INFO_CALLS))

# ═══ 3. 'New York' place card → 9/11 WTC photo ═════════════
reset(depicts={"Q60": [f"File:{WTC}", f"File:{NYC_P18}"]})
got = source("The show moved from Hyderabad to New York "
             "this season.", BHAVITHA_CTX, entities=["New York"],
             net=make_net(resolve=resolve_no_p18))
check("New York card: WTC file blocked at the evaluator, "
      "the city's own skyline sources",
      got is not None
      and "Paulus_Hook" in (produced_file(got) or ""))
check("New York card: WTC file was OFFERED and rejected "
      "(the blocklist did the work)",
      f"File:{WTC}" in FILE_INFO_CALLS)
reset(depicts={"Q60": [f"File:{WTC}"]})
got = source("The show moved from Hyderabad to New York "
             "this season.", BHAVITHA_CTX, entities=["New York"],
             net=make_net(resolve=resolve_no_p18))
check("New York card: WTC as the only candidate -> navy "
      "(a place never sources an associated event)",
      got is None)

# ═══ 4. Ramayana deck → coin + Hicks ═══════════════════════
reset()
got = source("The spectacle is mounted on a scale Indian "
             "cinema has rarely attempted.", RAMAYANA_CTX,
             entities=["Ramayana"])
check("Ramayana card: no photo (no-identity guard — the "
      "name spans epic, films and series)", got is None)
check("Ramayana card: coin and Hicks files never requested",
      not any(("Mohurs" in t or "Hicks" in t)
              for t in FILE_INFO_CALLS),
      str(FILE_INFO_CALLS))

# ═══ 5. IAF-chief deck → Ranjit Singh + Trenchard ══════════
reset()
got = source("He is the 29th chief of the Indian Air "
             "Force.", IAF_CTX, entities=["Indian Air Force"])
check("IAF card: no depicts fixture -> navy; the Ranjit "
      "Singh and Trenchard portraits are never requested",
      got is None
      and not any(("Ranjit" in t or "Trenchard" in t)
                  for t in FILE_INFO_CALLS),
      str(FILE_INFO_CALLS))
reset(depicts={"Q330658": [f"File:{RANJIT}",
                           f"File:{TRENCHARD}"]})
got = source("He is the 29th chief of the Indian Air "
             "Force.", IAF_CTX, entities=["Indian Air Force"])
check("IAF card: both portraits blocked even when offered "
      "as depicts", got is None)
reset()
got = source("Air Marshal Ashutosh Dixit took charge in "
             "New Delhi.", IAF_CTX,
             entities=["Ashutosh Dixit"])
check("IAF card: the chief's OWN verified portrait sources "
      "(positive control)",
      got is not None and got[2]["entity"] == "Ashutosh Dixit"
      and "VCAS" in (produced_file(got) or ""))

# ═══ 6. Jailer 2: 'Karnataka Rs' → Dudda; region cards ═════
reset()
got = source("In Karnataka, it collected Rs 75 crore.",
             JAILER_CTX, entities=["Karnataka Rs"])
check("'Karnataka Rs' fragment: no photo (unresolvable)",
      got is None)
check("'Karnataka Rs': Dudda file never requested",
      not any("Dudda" in t for t in FILE_INFO_CALLS))
reset(depicts={"Q1185": [f"File:{DUDDA}",
                         "File:Vidhana Soudha Bangalore.jpg"]})
got = source("In Karnataka, it collected Rs 75 crore.",
             JAILER_CTX, entities=["Karnataka"])
check("Karnataka card: Dudda blocked at the evaluator; "
      "the state's own legislature sources",
      got is not None
      and "Vidhana_Soudha" in (produced_file(got) or ""))
reset(depicts={"Q542146": [f"File:{DARASURAM}"]})
got = source("Across South India the run continues.",
             JAILER_CTX, entities=["South India"])
check("South India card: Darasuram temple blocked even "
      "when offered as depicts (a part is not the region)",
      got is None)
reset(depicts={"Q542146": ["File:South India region map.png"]})
got = source("Across South India the run continues.",
             JAILER_CTX, entities=["South India"])
check("South India card: a region map is not a photograph "
      "-> navy", got is None)

# ═══ 7. Kathleen Hicks: blocked meeting photo, own ═════════
# portrait sources when she IS the entity.
reset(depicts={"Q104587353": [f"File:{HICKS_MEETING}",
                              f"File:{HICKS_P18}"]})
got = source("Kathleen Hicks will lead the Pentagon "
             "review.", HICKS_CTX, entities=["Kathleen Hicks"],
             net=make_net(resolve=resolve_no_p18))
check("Hicks card: the Misri-meeting photo is blocked on "
      "her own entry; her official portrait sources",
      got is not None
      and "Deputy_Secretary_of_Defense.jpg"
      in (produced_file(got) or ""))

# ═══ 8. keepers through the registry (old suite's accepts) ═
reset(depicts={"Q638740": ["File:NSE Exchange Plaza.jpg"]})
PAGES.pop("File:National Stock Exchange of India 2.jpg",
          None)
got = source("Trading volumes rose at the NSE.", MARKET_CTX,
             entities=["NSE"])
check("keeper: NSE's own plaza sources via depicts",
      got is not None
      and "Exchange_Plaza" in (produced_file(got) or ""))
reset()
got = source("The Sensex jumped 905 points.", MARKET_CTX,
             entities=["Sensex"])
check("keeper: the Sensex's own exchange building (P18)",
      got is not None
      and "Bombay_Stock_Exchange" in (produced_file(got)
                                      or ""))
reset()
got = source("The ceremony was held at the White House.",
             HICKS_CTX, entities=["White House"])
check("keeper: White House P18 sources",
      got is not None
      and "WhiteHouseSouthFacade" in (produced_file(got)
                                      or ""))
reset()
got = source("Microsoft announced new campus hiring.",
             MARKET_CTX, entities=["Microsoft"])
check("keeper: Microsoft campus P18 sources",
      got is not None
      and "Microsoft_West_Campus" in (produced_file(got)
                                      or ""))
reset()
got = source("The Supreme Court refused a blanket ban.",
             SC_CTX, entities=["Supreme Court"])
check("keeper: India's Supreme Court (registry identity, "
      "P18) sources; the US court file is never requested",
      got is not None
      and "Supreme_Court_of_India" in (produced_file(got)
                                       or "")
      and not any("US Supreme Court" in t
                  for t in FILE_INFO_CALLS))
reset()
got = source("Trading at the BSE closed higher.",
             MARKET_CTX, entities=["BSE"])
check("'BSE' bare acronym: ambiguous (exchange vs disease) "
      "and unregistered -> fail closed to navy", got is None)

# ═══ 9. blocklist fires at the evaluator (Caterpillar) ═════
reset(depicts={"Q459965": ["File:Chenille chevrefeuille.jpg",
                           "File:Caterpillarhq.JPG"]})
got = source("Caterpillar reports earnings on Thursday.",
             CAT_CTX, entities=["Caterpillar"],
             net=make_net(resolve=resolve_no_p18))
check("Caterpillar card: insect blocked, HQ sources",
      got is not None
      and "Caterpillarhq" in (produced_file(got) or ""))

# ═══ 10. triage: outlet / language / category / metrics ════
reset()
got = source("An Economic Times analysis shows the trend.",
             MARKET_CTX, entities=["Economic Times"])
check("triage: outlet entity never sources", got is None)
reset()
got = source("The Hindi version earned Rs 43.8 crore.",
             JAILER_CTX, entities=["Hindi"])
check("triage: language entity never sources", got is None)
reset()
got = source("Benchmarks fell across the board.",
             MARKET_CTX, entities=["Markets Finance"])
check("triage: category-label pseudo-entity never sources",
      got is None)
reset()
got = source("EPS is seen at $5.54 for the quarter.",
             CAT_CTX, entities=["EPS"])
check("triage: 'EPS' metric (registry no-identity) -> navy; "
      "the Campagnolo file is never requested",
      got is None
      and not any("Campagnolo" in t for t in FILE_INFO_CALLS))

# ═══ 11. live-resolution discipline ════════════════════════
def _live_jailer3(name, ctx):
    return {"query": name, "name": "Jailer 3",
            "aliases": ["Jailer 3"], "qid": "Q999999998",
            "p18_file": "Jailer 3 poster.jpg",
            "p18_quality": 2000, "type": "work",
            "method": "live", "confidence": "high",
            "confusables": [], "blocked_files": [],
            "notes": ""}


reset()
got = source("Jailer 2 crossed Rs 75 crore in Karnataka.",
             JAILER_CTX, entities=["Jailer 2"],
             net=make_net(resolve=_live_jailer3))
check("live discipline: 'Jailer 2' resolved to 'Jailer 3' "
      "fails names_agree (numeral veto) -> navy",
      got is None)
check("names_agree: sequel numerals veto",
      ER.names_agree("Jailer 2", "Jailer 3") is False
      and ER.names_agree("Jailer 2", "Jailer") is True)


def _live_keith(name, ctx):
    return {"query": name, "name": "Keith Sonderling",
            "aliases": ["Keith Sonderling"],
            "qid": "Q999999999",
            "p18_file": "Keith Sonderling (55510883049).jpg",
            "p18_quality": 8192, "type": "person",
            "method": "live", "confidence": "high",
            "confusables": [], "blocked_files": [],
            "notes": ""}


reset()
got = source("Keith Sonderling addressed the summit.",
             HICKS_CTX, entities=["Keith Sonderling"],
             net=make_net(resolve=_live_keith))
check("live discipline: a multi-token live resolution that "
      "AGREES still sources (the path is not registry-only "
      "for names)", got is not None
      and got[2]["entity"] == "Keith Sonderling")

# ═══ 12. corpus blocklist seeds (SHA1-exact, 2026-11-01) ═══
for ent_name, fname in [
        ("New York City", WTC), ("OTT", JARVELA),
        ("Indian Air Force", RANJIT),
        ("Indian Air Force", TRENCHARD), ("STAR", STARBURST),
        ("Ramayana", COIN), ("Kathleen Hicks", HICKS_MEETING),
        ("Karnataka", DUDDA), ("South India", DARASURAM)]:
    check(f"blocklist: {ent_name} blocks its wrong file",
          ER.blocked_file(ent_name, fname))
check("blocklist: Hicks's own portrait is NOT blocked",
      not ER.blocked_file("Kathleen Hicks", HICKS_P18))

sc._download_entity_image = _orig_download
res.commons_search = _orig_search
res.brave_links = _orig_links
unpin()

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
