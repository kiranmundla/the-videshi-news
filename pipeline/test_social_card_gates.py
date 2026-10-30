#!/usr/bin/env python3
"""
test_social_card_gates.py — regression tests for the
2026-10-29 card-gate patch in social_card.py (Kiran's go after
three straight days of wrong-entity cards on X/Facebook/
Threads, Oct 27–29).

The bug: _entity_image_for_card called the reel ladder's
evaluators WITHOUT a story context, and
picture_gate_shared.context_reject_reason returns None on a
falsy context — so the shared identity gates (country
contradiction / depicted person / person namesake) were
silently inert for every deck, and single-token entities
('EPS', 'NSE') matched Commons namesakes on one shared token.

Every bad fixture below is the REAL Commons file that shipped
(title/description/categories fetched from the Commons API
2026-10-29):
  * 'EPS' (Caterpillar earnings) -> Campagnolo Super Record
    EPS bicycle disk brake photos (Oct 28 + Oct 29, X).
  * 'NSE' (Sensex rally) -> portrait of Nigerian actress
    Nse Ikpe-Etim (Oct 29, X).
  * 'Spark Capital' / 'Capital' (Nifty) -> Gaisano Capital
    mall storefronts, Philippines (Oct 28, X).
  * 'Supreme Court' (India firecracker ruling) -> the US
    Supreme Court building; 'High Court' -> the High Court
    of Australia (Oct 29, X).
  * 'Google Services' (Alphabet) -> a blank Google Docs
    screenshot (Oct 28, X/Facebook).
  * 'For Indian' (H-1B fee deck) -> Indian elephant /
    rhinoceros wildlife photos (Oct 28, staged decks).
Extended 2026-10-30 with that morning's two live failures:
  * 'Hindi' (Jailer 2 Hindi box-office deck) -> a classroom
    alphabet chart and File:Black hole - Messier 87.jpg —
    languages are now non-visual in card hygiene.
  * 'Economic Times' (Samvat 2082 deck) -> the outlet's own
    logo via route B — card-local outlet supplement plus
    candidate-level branding rejection on every route.
Keepers are the reel suite's proven accepts (Frances Perkins
Building, Keith Sonderling, the Washington White House,
Microsoft campus) driven through the CARD path: the gates
must reject namesakes without costing real pictures.

All network is stubbed. Run:
  python3 test_social_card_gates.py   (exit 0 = all pass)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

import reel_entity_sourcing as res  # noqa: E402
import social_card as sc  # noqa: E402

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


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


# ── the real failure files (Commons API, 2026-10-29) ───────
CAMPAGNOLO = commons_page(
    "File:Campagnolo Super Record EPS 12S Disk Brake 01.jpg",
    3092, 3093, license_short="CC BY 2.0",
    desc="Campagnolo Super Record EPS 12S Disk Brake",
    cats="Flickr images reviewed by FlickreviewR 2|"
         "Campagnolo Super Record EPS")
ACTRESS = commons_page(
    "File:Nse Ikpe-Etim in 2016.jpg", 1991, 2866,
    desc="Likely Nse Ikpe Etim (based on derivative "
         "File:Nse Ikpe Etim.png)",
    cats="Nse Ikpe Etim|Self-published work|"
         "Images with extracted images")
GAISANO = commons_page(
    "File:Gaisano Capital Sogod.JPG", 1920, 1080,
    license_short="Public domain",
    desc="Gaisano Capital Sogod - first ever built mall in "
         "Southern Leyte",
    cats="Taken with Sony DSC-T300|PD-user|Sogod, Southern "
         "Leyte|Gaisano Capital|Gaisano")
US_COURT = commons_page(
    "File:Panorama of United States Supreme Court Building "
    "at Dusk.jpg", 3788, 1952, license_short="CC BY-SA 3.0",
    desc="Panorama of the west facade of United States "
         "Supreme Court Building at dusk in Washington, D.C., "
         "United States of America.",
    cats="Self-published work|Photographs by User:Jovianeye|"
         "Exterior of the United States Supreme Court Building")
AU_COURT = commons_page(
    "File:High Court of Australia, ACT - perspective "
    "controlled 1.jpg", 9817, 5869,
    desc="The High Court of Australia, in Canberra ACT, is "
         "an unusual and distinctive structure, built in the "
         "brutalist style, and features a public atrium with "
         "a 24-metre-high roof.",
    cats="High Court of Australia, Canberra, building "
         "exterior|FoP-Australia")
BLANK_DOC = commons_page(
    "File:Google Docs blank document February 2020.png",
    1920, 1080, license_short="Public domain",
    desc="An image of a blank document in Google Docs as of "
         "February 2020. The account logo circle in the top "
         "right has been made light grey. Created by taking "
         "a screenshot of the service.",
    cats="Google software|PD shape|PD text|Google services")
BLANK_DOC["imageinfo"][0]["mime"] = "image/png"
WIPO_SPEAKER = commons_page(
    "File:IP Finance Dialogue – Expanding Horizons on IP "
    "Finance and Valuation - 53346909618.jpg", 6000, 4000,
    license_short="CC BY 2.0",
    desc="IP Finance Dialogue – Expanding Horizons on IP "
         "Finance and Valuation, WIPO, Geneva",
    cats="World Intellectual Property Organization")
NIFTY_CTX = {
    "headline": "Nifty Down 13 Percent Faces Worst Year in "
                "Decade as Strategists Urge Caution",
    "body": "<p>Nifty has fallen 13 percent in 2026, its "
            "worst showing in a decade. Spark Capital "
            "analysts urged investors to stay cautious, "
            "citing stretched valuations and weak earnings "
            "breadth across Indian markets.</p>",
    "slug": "nifty-down-13-percent",
    "category": "markets-finance",
}
ELEPHANT = commons_page(
    "File:Indian elephant in Kaziranga National Park March "
    "2025 by Tisha Mukherjee 04.jpg", 4942, 3295,
    desc="Indian elephant (Elephas maximus indicus, "
         "Elephantidae, Proboscidea) in Kaziranga National "
         "Park, Assam, India.",
    cats="Elephas maximus indicus|Self-published work|"
         "Featured pictures of Elephantidae")

# ── keepers (the reel suite's proven accepts) ──────────────
PERKINS = commons_page(
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
KEITH = commons_page(
    "File:Keith Sonderling (55510883049).jpg", 8192, 5464,
    desc="Acting U.S. Secretary of Labor Keith Sonderling "
         "speaking with attendees at the Republican Jewish "
         "Coalition's 2026 Annual Leadership Summit in Las "
         "Vegas, Nevada.",
    cats="Photographs by Gage Skidmore|Keith Sonderling|"
         "2026 Republican Jewish Coalition's Annual "
         "Leadership Summit")
DC_WH = commons_page(
    "File:White House in Washington, D.C. 2024.jpg",
    4000, 2667,
    desc="The White House, official residence and workplace "
         "of the President of the United States, in "
         "Washington, D.C.",
    cats="White House|Washington, D.C.")
MS_CAMPUS = commons_page(
    "File:Microsoft headquarters, Redmond.jpg", 4000, 3000,
    desc="Microsoft corporate headquarters campus in "
         "Redmond, Washington, United States",
    cats="Microsoft campus|Buildings in Redmond, Washington")
# The exchanges' OWN buildings (real Commons metadata,
# fetched 2026-10-29 after the live smoke render showed the
# first agreement cut rejecting them on a plural: the story
# says 'stocks', the file says 'Stock Exchange').
BSE_BUILDING = commons_page(
    "File:BSE - Bombay Stock Exchange Building.jpg",
    2291, 1917, license_short="CC BY 2.0",
    desc="The Bombay Stock Exchange building in Mumbai, "
         "India",
    cats="Taken with Olympus FE-150 / X-730|Flickr images "
         "reviewed by trusted users|Phiroze Jeejeebhoy "
         "Towers")
NSE_PLAZA = commons_page(
    "File:NSE Exchange Plaza.jpg", 5760, 3840,
    desc="National Stock Exchange of India Corporate Office",
    cats="Buildings in India|Self-published work")


# ── story contexts (as render_card_set builds them) ────────
CAT_CTX = {
    "headline": "Caterpillar Earnings Preview: EPS Seen at "
                "$5.54 as Machinery Demand Cools",
    "body": "Caterpillar is expected to report quarterly "
            "earnings on Thursday, with analysts watching "
            "machinery demand and dealer inventories. The "
            "construction equipment maker has guided for "
            "steady revenue as infrastructure spending "
            "holds up.",
    "slug": "caterpillar-earnings-preview", 
    "category": "markets-finance"}
SENSEX_CTX = {
    "headline": "Sensex Surges 905 Points, Nifty Tops 22,900 "
                "as Banking and FMCG Stocks Lead",
    "body": "Indian equity benchmarks rallied on Thursday "
            "as banking and FMCG stocks led a broad advance. "
            "The Sensex jumped 905 points while the Nifty "
            "closed above 22,900, extending gains for a "
            "third straight session as foreign investors "
            "returned to Dalal Street.",
    "slug": "sensex-surges-905-points", 
    "category": "markets-finance"}
NIFTY_CTX = {
    "headline": "Nifty Logs Worst Year in a Decade as Spark "
                "Capital Urges Caution",
    "body": "The Nifty has fallen 13 percent this year, its "
            "worst showing in a decade. Spark Capital "
            "analysts urged investors to stay cautious, "
            "citing stretched valuations and weak earnings "
            "breadth across Indian markets.",
    "slug": "nifty-worst-year-decade", 
    "category": "markets-finance"}
SC_CTX = {
    "headline": "Supreme Court Rules Out Blanket Firecracker "
                "Ban, Warns Orders Must Not Become a Mockery",
    "body": "The Supreme Court of India on Thursday refused "
            "to impose a blanket ban on firecrackers ahead "
            "of Diwali, with Justices Sundresh and Varale "
            "observing that enforcement agencies in Delhi "
            "must ensure its orders are not reduced to a "
            "mockery. The bench was hearing petitions on "
            "Delhi air quality.",
    "slug": "supreme-court-firecracker-ban", "category": "news"}
GOOG_CTX = {
    "headline": "Alphabet Earnings Preview: Google Services "
                "and Cloud in Focus",
    "body": "Alphabet reports quarterly results on Tuesday, "
            "with investors focused on advertising revenue, "
            "Google Cloud growth and capital spending on "
            "data centers.",
    "slug": "alphabet-earnings-preview", "category": "technology"}
H1B_CTX = {
    "headline": "$100K H-1B Fee Case: Nurses' Group Asks "
                "Court for Summary Judgment",
    "body": "Global Nurse Force and other plaintiffs asked "
            "a federal court to strike down the $100,000 "
            "H-1B fee, arguing the administration exceeded "
            "its authority. The fee applies to new H-1B "
            "petitions filed by employers in the United "
            "States.",
    "slug": "h1b-100k-fee-case", "category": "immigration"}

FIXTURES = Path(__file__).resolve().parent / "test-fixtures" \
    / "reel-sourcing-gates"
PERM_ARTICLE = json.loads(
    (FIXTURES / "perm-article.json").read_text())
MS_ARTICLE = json.loads(
    (FIXTURES / "microsoft-article.json").read_text())
PERM_CTX = {"headline": PERM_ARTICLE.get("headline"),
            "body": PERM_ARTICLE.get("body"),
            "slug": PERM_ARTICLE.get("slug"),
            "category": PERM_ARTICLE.get("category")}
MS_CTX = {"headline": MS_ARTICLE.get("headline"),
          "body": MS_ARTICLE.get("body"),
          "slug": MS_ARTICLE.get("slug"),
          "category": MS_ARTICLE.get("category")}


# ── stubbed network ────────────────────────────────────────
_PAGES = []
_orig_search = res.commons_search
_orig_links = res.brave_links
_orig_download = sc._download_entity_image
_orig_card_entities = sc._card_entities


def stub_pages(pages):
    global _PAGES
    _PAGES = pages


def _fake_search(query, limit=8):
    return list(_PAGES)


def _no_links(query, n):
    return []


def _fake_download(url):
    return Image.new("RGB", (1600, 1000)), b"stub"


res.commons_search = _fake_search
res.brave_links = _no_links
sc._download_entity_image = _fake_download
LOGS = []


def source(text, ctx, entities=None):
    """Run the card sourcer with the stubbed ladder. When
    `entities` is given, pin _card_entities to it (the unit
    seam for entity strings production extraction produced
    verbatim on the failure days)."""
    if entities is not None:
        sc._card_entities = lambda t, c: list(entities)
    try:
        return sc._entity_image_for_card(
            text, ctx, [], log=LOGS.append)
    finally:
        sc._card_entities = _orig_card_entities


print("── entity hygiene ──")
ents = sc._card_entities(
    "For Indian professionals, the fee takes effect for new "
    "petitions filed after September.", H1B_CTX)
check("'For Indian' fragment is never a card entity",
      "For Indian" not in ents, str(ents))
check("hygiene: edge-stopword entity rejected",
      sc._card_entity_hygiene("For Indian") is not None)
check("hygiene: possessive rejected",
      sc._card_entity_hygiene("NSE's") is not None)
check("hygiene: outlet rejected",
      sc._card_entity_hygiene("Times of India") is not None)
check("hygiene: real entities pass",
      sc._card_entity_hygiene("Supreme Court") is None
      and sc._card_entity_hygiene("Spark Capital") is None
      and sc._card_entity_hygiene("Department of Labor")
      is None)

print("── the Oct 28–29 failures, through the card path ──")
stub_pages([CAMPAGNOLO])
got = source("EPS is expected at $5.54, with revenue seen "
             "near $16.2 billion for the quarter.", CAT_CTX)
check("Campagnolo bike brake rejected for 'EPS'", got is None)

stub_pages([ACTRESS])
got = source("The benchmark Nifty rose 238 points on the "
             "NSE as banking stocks led the rally.", SENSEX_CTX)
check("actress portrait rejected for 'NSE'", got is None)

stub_pages([GAISANO])
got = source("Spark Capital urged caution, citing "
             "stretched valuations.", NIFTY_CTX)
check("Gaisano mall rejected for 'Spark Capital'",
      got is None)
got = source("Capital flows turned cautious this week.",
             NIFTY_CTX, entities=["Capital"])
check("Gaisano mall rejected for fragment 'Capital'",
      got is None)

stub_pages([US_COURT])
got = source("The Supreme Court said a blanket ban would "
             "turn its orders into a mockery.", SC_CTX)
check("US Supreme Court building rejected for India's",
      got is None)
stub_pages([AU_COURT])
got = source("The High Court will hear the matter next "
             "month.", SC_CTX, entities=["High Court"])
check("High Court of Australia rejected for India's story",
      got is None)

stub_pages([BLANK_DOC])
got = source("Google Services revenue is expected to grow "
             "as advertising demand holds.", GOOG_CTX)
check("blank Google Docs screenshot rejected for "
      "'Google Services'", got is None)

stub_pages([ELEPHANT])
got = source("For Indian professionals, the fee takes "
             "effect for new petitions.", H1B_CTX,
             entities=["Indian"])
check("Kaziranga elephant rejected for the H-1B story",
      got is None)

print("── the category is not an entity ──")
check("the category pseudo-entity never reaches the card "
      "entity list",
      "Markets Finance" not in sc._card_entities(
          "Nifty 50 is down 13% in 2026, facing worst "
          "annual performance in over a decade.", NIFTY_CTX))
stub_pages([WIPO_SPEAKER])
got = source("Nifty 50 is down 13% in 2026, facing worst "
             "annual performance in over a decade.", NIFTY_CTX)
check("no WIPO conference speaker for the subject-less "
      "Nifty card — honest navy miss",
      got is None)

print("── context is the active ingredient (courts) ──")
cand, row = res.evaluate_commons_page(
    US_COURT, "Supreme Court", "A — Wikimedia Commons")
check("without context the US court file still passes "
      "(the pre-patch behaviour)", cand is not None)
ctx = res.build_story_context(
    SC_CTX, {"key_entities": ["Supreme Court"],
             "news_summary": "firecracker ban hearing"},
    ["Supreme Court"])
cand, row = res.evaluate_commons_page(
    US_COURT, "Supreme Court", "A — Wikimedia Commons",
    context=ctx)
check("with the story context the US court file is "
      "rejected", cand is None, row.get("reason", ""))

print("── keepers survive the card path ──")
stub_pages([PERKINS])
got = source("The Department of Labor will publish the "
             "final rule in the Federal Register.", PERM_CTX)
check("keeper: Frances Perkins Building (Dept of Labor)",
      got is not None and got[2]["entity"]
      == "Department of Labor",
      "" if got else "honest miss — " + "; ".join(LOGS[-3:]))
stub_pages([KEITH])
got = source("Keith Sonderling said the plan protects "
             "American workers.", PERM_CTX)
check("keeper: Keith Sonderling portrait",
      got is not None and got[2]["entity"]
      == "Keith Sonderling")
stub_pages([DC_WH])
got = source("The White House cleared the Labor "
             "Department plan on Monday.", PERM_CTX)
check("keeper: the Washington White House",
      got is not None and got[2]["entity"] == "White House")
stub_pages([BSE_BUILDING])
got = source("BSE Sensex rose 905.01 points, closing at "
             "74,151.04.", SENSEX_CTX, entities=["BSE"])
check("keeper: the BSE's own building for 'BSE'",
      got is not None and got[2]["entity"] == "BSE")
stub_pages([NSE_PLAZA])
got = source("NSE Nifty increased by 237.90 points to "
             "22,936.75.", SENSEX_CTX, entities=["NSE"])
check("keeper: NSE Exchange Plaza for 'NSE' (the actress "
      "is rejected, the exchange's own plaza is not)",
      got is not None and got[2]["entity"] == "NSE")
stub_pages([MS_CAMPUS])
got = source("Microsoft is offering a Voluntary Exit "
             "Offer to about 60,000 employees, roughly a "
             "quarter of its 223,000-person workforce.",
             MS_CTX, entities=["Microsoft"])
check("keeper: Microsoft campus (single-token agreement "
      "does not cost a genuine photo)",
      got is not None and got[2]["entity"] == "Microsoft",
      "" if got else "honest miss — " + "; ".join(LOGS[-3:]))

print("── the Oct 30 failures: languages + outlet branding ──")
# FAILURE 1 (X, 2026-10-30): the Jailer 2 Hindi box-office
# deck sourced pictures for the entity 'Hindi' — card 2 a
# classroom Hindi-alphabet wall chart, card 3 the real file
# below. A language is not a visual entity: it must never
# reach the ladder, from the card's own text OR the article
# fallback list (the black hole arrived via the fallback).
BLACK_HOLE = commons_page(
    "File:Black hole - Messier 87.jpg", 7416, 4320,
    license_short="CC BY 4.0",
    desc="The first direct image of a black hole, located "
         "in the core of the supergiant elliptical galaxy "
         "Messier 87 in the constellation Virgo.",
    cats="Messier 87|Black holes|Event Horizon Telescope|"
         "2019 in science")
JAILER_CTX = {
    "headline": "Jailer 2 Hindi Box Office Day 15: Profit "
                "at 68 Percent as Run Continues",
    "body": "Jailer 2's Hindi version earned Rs 43.8 crore "
            "in 15 days. The film achieved a profit of "
            "Rs 17.8 crore, or 68.46 percent, trade "
            "reports said.",
    "slug": "jailer-2-hindi-box-office-day-15-profit-68-percent",
    "category": "entertainment"}
check("hygiene: language names rejected",
      sc._card_entity_hygiene("Hindi") is not None
      and sc._card_entity_hygiene("Telugu") is not None
      and sc._card_entity_hygiene("English") is not None)
ents = sc._card_entities(
    "Jailer 2's Hindi version earned Rs 43.8 crore in "
    "15 days.", JAILER_CTX)
check("'Hindi' never reaches a card entity list",
      "Hindi" not in ents, str(ents))
stub_pages([BLACK_HOLE])
got = source("Jailer 2's Hindi version earned Rs 43.8 "
             "crore in 15 days.", JAILER_CTX)
check("black hole never sourced for the Jailer 'Hindi' "
      "card — navy fallback", got is None)
got = source("The film achieved a profit of Rs 17.8 "
             "crore, or 68.46%.", JAILER_CTX)
check("black hole never sourced via the article-entity "
      "fallback either", got is None)

# FAILURE 2 (X, 2026-10-30): the Samvat 2082 deck carried
# the Economic Times LOGO as card 2's photo, via route B —
# 'Economic Times' is missing from the shared outlet list,
# so the entity passed hygiene and the hosted evaluator
# returned the outlet's branding og:image. The card path
# now rejects branding candidates on every route, plus the
# entity via a card-local outlet supplement.
SAMVAT_CTX = {
    "headline": "Samvat 2082: Largecaps Fall as Smallcap "
                "Multibaggers Steal the Diwali Show",
    "body": "India's benchmark Nifty fell about 11 percent "
            "over Samvat 2082, with 83 large-cap stocks "
            "losing ground, an Economic Times analysis of "
            "the year since last Diwali shows.",
    "slug": "samvat-2082-largecaps-fall-smallcap-multibaggers-diwali",
    "category": "markets-finance"}
check("hygiene: 'Economic Times' rejected (card-local "
      "outlet supplement)",
      sc._card_entity_hygiene("Economic Times") is not None)
check("branding: outlet-domain URL rejected even with a "
      "neutral filename",
      sc._card_url_branding_reject(
          "https://economictimes.indiatimes.com/photo/"
          "104857442.cms"))
check("branding: outlet image-CDN subdomain rejected",
      sc._card_url_branding_reject(
          "https://img.etimg.com/thumb/et-image.jpg"))
check("branding: root social filename rejected",
      sc._card_url_branding_reject(
          "https://1stheadlines.com/og.jpg"))
check("branding: 'logo' in the filename rejected",
      sc._card_url_branding_reject(
          "https://example.org/assets/site-logo.png"))
check("branding: 'logo' as a mere directory marker is "
      "not, by itself, a rejection",
      not sc._card_url_branding_reject(
          "https://cdn.example.org/img/logo/photo_123.jpg"))
check("branding: a Commons keeper URL passes",
      not sc._card_url_branding_reject(
          "https://upload.wikimedia.org/wikipedia/commons/"
          "2/2e/BSE_-_Bombay_Stock_Exchange_Building.jpg"))

_orig_hosted = res.evaluate_hosted_page
ET_LOGO_CAND = {
    "entity": "Economic Times", "title": "The Economic Times",
    "file_url": "https://img.etimg.com/thumb/msid-104857442,"
                "width-1200,height-630/et-logo.jpg",
    "size": None,
    "source_page": "https://economictimes.indiatimes.com/",
    "license": "explicit CC / public-domain statement on "
               "the page",
    "artist": "", "subject": "The Economic Times",
    "role": "scene", "route": "B — official sources",
    "anchor": None, "needs_dims_check": True}


def _et_links(query, n):
    return ["https://economictimes.indiatimes.com/"]


def _et_hosted(url, entity, route, net, context=None):
    return dict(ET_LOGO_CAND), {"verdict": "accepted"}


stub_pages([])
res.brave_links = _et_links
res.evaluate_hosted_page = _et_hosted
got = source("India's benchmark Nifty fell about 11 "
             "percent over Samvat 2082, an Economic Times "
             "analysis shows.", SAMVAT_CTX,
             entities=["Economic Times"])
check("Economic Times logo rejected on the official-"
      "sources route", got is None)
res.brave_links = _no_links
res.evaluate_hosted_page = _orig_hosted

res.commons_search = _orig_search
res.brave_links = _orig_links
sc._download_entity_image = _orig_download

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
