#!/usr/bin/env python3
"""
test_picture_pass_guards.py — regression tests for the
2026-10-26 picture-pass guards (hero subject gate, entity
hygiene, era gate, inline duplicate check).

Every fixture is modeled on a VERIFIED Oct 25–26 live failure:
  * Air India Toronto–Mumbai hero filled with a Biman
    Bangladesh 787 (entity: the place 'Toronto Pearson').
  * Infosys Q2 hero filled with a Goldman Sachs building
    (entity: a company the story merely cited).
  * Redistricting hero keyed to the quoted analyst
    'Nathan Gonzales'; FDA story matched to a Dunzo rider +
    a Jain temple (body-only / place-only matches).
  * Appeals-court article: 'Reuters vehicle used in
    Palestine' (entity fragment 'Reuters. The') + a Reuters
    Building inline (a news OUTLET as entity).
  * 'Secret Toronto' formed across the possessive in
    "Victoria's Secret Toronto"; "New Zealand's" standing
    as an entity.
  * 1939 archival Queen Street photo inside a 2026 Toronto
    Diwali story; a 2022 White House Diwali photo captioned
    as Times Square 2026.

All network is stubbed. Run:
  python3 test_picture_pass_guards.py   (exit 0 = all pass)
"""
import sys
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


def stub_net(pages_by_query=None, cache=None):
    pages_by_query = pages_by_query or {}
    calls = {"search": []}

    def commons_search(q, limit=10):
        calls["search"].append(q)
        for key, pages in pages_by_query.items():
            if key.lower() in q.lower():
                return pages
        return []

    net = {
        "commons_search": commons_search,
        "commons_file_info": lambda title: None,
        "brave_links": lambda q, n=8: [],
        "fetch_text": lambda url, timeout=15: "",
        "verify_url": lambda url: {"ok": True, "width": 2400},
        "person_cache": lambda name: (cache or {}).get(name),
        "download_verify": lambda url, dest: [2400, 1500],
    }
    return net, calls


# ── B. entity hygiene: sentence spans, outlets, fragments ──────────
print("entity hygiene")
check("'Reuters. The' rejected (sentence boundary)",
      P._entity_hygiene_reject("Reuters. The") is not None)
check_eq("_sane_image_entity('Reuters. The') is None",
         P._sane_image_entity("Reuters. The"), None)
check_eq("outlet 'Reuters' is not a sane image entity",
         P._sane_image_entity("Reuters"), None)
check_eq("outlet 'Hindustan Times' is not a sane image entity",
         P._sane_image_entity("Hindustan Times"), None)
check_eq("outlet 'Associated Press' rejected by hygiene",
         P._entity_hygiene_reject("Associated Press") is not None,
         True)
check("possessive form \"New Zealand's\" rejected",
      P._entity_hygiene_reject("New Zealand's") is not None)
check("stopword-final fragment rejected",
      P._entity_hygiene_reject("Festival Of") is not None)
check_eq("a real name passes hygiene",
         P._entity_hygiene_reject("Reserve Bank of India"), None)
check_eq("an honorific period is not a sentence span",
         P._entity_hygiene_reject("Dr. Arun Raghavan"), None)
check_eq("initials are not a sentence span",
         P._entity_hygiene_reject("U.S. Congress"), None)
check("'August. The' rejected (sentence boundary)",
      P._entity_hygiene_reject("August. The") is not None)
check("'GeekWire. Microsoft' rejected (sentence boundary)",
      P._entity_hygiene_reject("GeekWire. Microsoft")
      is not None)
check_eq("a brand with an internal possessive passes hygiene",
         P._entity_hygiene_reject("Victoria's Secret"), None)

OUTLET_ART = {
    "headline": "Appeals Court Weighs Deportation Case",
    "body": "<p>The court heard arguments on Monday. Judges "
            "asked about the deportation policy.</p>",
    "image_entities": ["Reuters", "Reuters. The",
                       "Hindustan Times"],
}
outlet_names = [e["name"]
                for e in P.extract_article_entities(OUTLET_ART)]
check("no outlet entity survives extraction",
      not any("Reuters" in n or "Hindustan" in n
              for n in outlet_names), str(outlet_names))

POSS_ART = {
    "headline": "Toronto Diwali Festival Draws Thousands",
    "body": "<p>Shoppers thronged the Victoria's Secret "
            "Toronto flagship before the parade. The "
            "Victoria's Secret Toronto store stayed open "
            "late for Diwali shoppers.</p>",
    "image_entities": ["Secret Toronto"],
}
poss_names = [e["name"]
              for e in P.extract_article_entities(POSS_ART)]
check("'Secret Toronto' never forms across a possessive",
      "Secret Toronto" not in poss_names, str(poss_names))
check("_possessive_fragment sees the possessive tail",
      P._possessive_fragment(
          "Secret Toronto",
          ("", "the Victoria's Secret Toronto flagship")))
BRAND_ART = {
    "headline": "Mall Opens Late for Diwali Shoppers",
    "body": "<p>Shoppers visited Victoria's Secret on "
            "Saturday. The Victoria's Secret store reported "
            "record Diwali weekend sales.</p>",
    "image_entities": ["Victoria's Secret"],
}
brand_names = [e["name"]
               for e in P.extract_article_entities(BRAND_ART)]
check("the brand itself ('Victoria's Secret') survives",
      "Victoria's Secret" in brand_names, str(brand_names))

# ── B. quoted-source persons ────────────────────────────────────────
print("quoted-source persons")
GONZALES_BODY = (
    "<p>The proposed maps would shift three districts, "
    "analysts said. “The new lines clearly favour one party "
    "in the fall,” said Nathan Gonzales, an analyst with "
    "Inside Elections, and Nathan Gonzales added that "
    "litigation was likely within weeks.</p>")
check("a person the body only quotes is a quoted source",
      P._is_quoted_source("Nathan Gonzales", GONZALES_BODY))
NARRATIVE_BODY = (
    "<p>Nathan Gonzales presented the new district maps at "
    "the hearing on Monday morning. The maps redraw three "
    "districts across the state.</p>")
check("a narrative subject is NOT a quoted source",
      not P._is_quoted_source("Nathan Gonzales", NARRATIVE_BODY))
REDISTRICT_ART = {
    "headline": "North Carolina Republicans Advance New "
                "Congressional Maps",
    "body": GONZALES_BODY + "<p>More reaction followed.</p>"
    + "<p>Filler paragraph for length. </p>" * 30,
    "image_entities": None, "category": "news",
    "image_url": None, "image_backfill_blocked": False,
}
redistrict_ents = {e["name"]: e for e in
                   P.extract_article_entities(REDISTRICT_ART)}
gonz = redistrict_ents.get("Nathan Gonzales")
check("quoted analyst extracted but tagged quoted_source",
      gonz is not None and gonz.get("quoted_source") is True,
      str(redistrict_ents))
check("quoted analyst is not a headline subject",
      "nathan gonzales" not in P.headline_subject_names(
          REDISTRICT_ART,
          list(redistrict_ents.values())))

# A quoted analyst named in the HEADLINE is still refused:
# the quote is the story's hook, the analyst is not its
# subject picture.
GONZALES_HEADLINE_ART = {
    "headline": "Nathan Gonzales Warns New Maps Face "
                "Court Fight",
    "body": GONZALES_BODY, "image_entities": None,
    "category": "news",
}
gh_ents = P.extract_article_entities(GONZALES_HEADLINE_ART)
GONZALES_PAGE = commons_page(
    "File:Nathan Gonzales analyst portrait.jpg", 2000, 1400,
    desc="Nathan Gonzales, political analyst, at a panel.",
    cats="Nathan Gonzales")
net_g, calls_g = stub_net(
    pages_by_query={"Nathan Gonzales": [GONZALES_PAGE]})
rec_g = {"ledger": [], "notes": []}
pick_g = P._source_hero(GONZALES_HEADLINE_ART, gh_ents, "",
                        net_g, 1200, set(), rec_g,
                        lambda *a: None)
check("headline-named quoted analyst still refused as hero",
      pick_g is None
      and any("QUOTES" in r.get("reason", "")
              for r in rec_g["ledger"]),
      str(rec_g["ledger"]))

# ── A. hero subject gate: the Air India / Biman fixture ────────────
print("hero subject gate — Air India vs Biman (Toronto Pearson)")
AIR_INDIA_ART = {
    "headline": "Air India Launches Only Direct Toronto-Mumbai "
                "Flight for Winter Season",
    "body": "<p>Air India will operate the route from Toronto "
            "Pearson this winter. Toronto Pearson said the "
            "flight departs Terminal 1. Air India crew will "
            "staff the service.</p>"
            "<p>Passengers welcomed the direct link.</p>"
            + "<p>Filler paragraph to clear the word floor "
              "today. </p>" * 50,
    "image_entities": None, "category": "news",
    "image_url": None, "image_backfill_blocked": False,
    "slug": "air-india-toronto-mumbai",
}
BIMAN_PAGE = commons_page(
    "File:Biman at Toronto Pearson Airport 13.jpg", 6000, 4000,
    license_short="CC0 1.0",
    desc="A Biman Bangladesh Airlines Boeing 787 Dreamliner "
         "on the Toronto Pearson ramp, operating the Dhaka "
         "flight during the winter season.",
    cats="Toronto Pearson International Airport|"
         "Biman Bangladesh Airlines")
ai_ents = P.extract_article_entities(AIR_INDIA_ART)
ai_names = [e["name"] for e in ai_ents]
check("Air India + Toronto Pearson both extracted",
      "Air India" in ai_names and "Toronto Pearson" in ai_names,
      str(ai_names))
ai_subjects = P.headline_subject_names(AIR_INDIA_ART, ai_ents)
check("Air India is a headline subject",
      "air india" in ai_subjects)
check("Toronto Pearson is NOT a headline subject",
      "toronto pearson" not in ai_subjects)
net_ai, calls_ai = stub_net(
    pages_by_query={"Toronto Pearson": [BIMAN_PAGE]})
rec_ai = {"ledger": [], "notes": []}
pick_ai = P._source_hero(AIR_INDIA_ART, ai_ents, "", net_ai,
                         1200, set(), rec_ai, lambda *a: None)
check("hero REJECTED: the Biman photo keyed to the place "
      "mention never becomes the Air India hero",
      pick_ai is None)
check("hero gate ledgered for Toronto Pearson",
      any("hero subject gate" in r.get("reason", "")
          and r.get("entity") == "Toronto Pearson"
          for r in rec_ai["ledger"]))
check("non-subject entity never even searched for the hero",
      not any("Toronto Pearson" in q for q in calls_ai["search"]),
      str(calls_ai["search"]))
# Same article end-to-end: hero stays an honest miss, but the
# place picture remains INLINE-eligible (inline gates apply).
net_ai2, _c = stub_net(
    pages_by_query={"Toronto Pearson": [BIMAN_PAGE]})
rec_ai2 = P.process_article(AIR_INDIA_ART, net=net_ai2,
                            apply=False, log=lambda *a: None)
check("end-to-end: no hero proposed for the Air India story",
      rec_ai2["hero"]["proposed"] is None)
check("end-to-end: Toronto Pearson still inline-eligible",
      any(p["entity"] == "Toronto Pearson"
          for p in rec_ai2["inlines"]["proposed"]))

# ── A. hero subject gate: the Infosys / Goldman fixture ────────────
print("hero subject gate — Infosys vs Goldman Sachs")
INFOSYS_ART = {
    "headline": "Infosys Shares Fall 4% After Q2: Brokerages "
                "Split Between Buy And Hold Targets",
    "body": "<p>Infosys reported Q2 results on Thursday. "
            "Goldman Sachs kept its neutral rating on Infosys. "
            "Goldman Sachs analysts cited margin pressure at "
            "Infosys through the quarter.</p>"
            + "<p>Filler paragraph for length. </p>" * 30,
    "image_entities": None, "category": "markets-finance",
    "image_url": None, "image_backfill_blocked": False,
    "slug": "infosys-q2",
}
GOLDMAN_PAGE = commons_page(
    "File:Goldman Sachs headquarters New York.jpg", 2400, 1500,
    desc="Goldman Sachs headquarters, the investment bank, "
         "at 200 West Street, New York.",
    cats="Goldman Sachs")
inf_ents = P.extract_article_entities(INFOSYS_ART)
inf_subjects = P.headline_subject_names(INFOSYS_ART, inf_ents)
check("Infosys is the headline subject",
      "infosys" in inf_subjects)
check("Goldman Sachs is NOT a headline subject",
      "goldman sachs" not in inf_subjects)
net_inf, calls_inf = stub_net(
    pages_by_query={"Goldman Sachs": [GOLDMAN_PAGE]})
rec_inf = {"ledger": [], "notes": []}
pick_inf = P._source_hero(INFOSYS_ART, inf_ents, "", net_inf,
                          1200, set(), rec_inf, lambda *a: None)
check("hero REJECTED: the Goldman building never becomes "
      "the Infosys hero (subject yields nothing -> honest miss)",
      pick_inf is None)
check("Goldman never searched for the hero slot",
      not any("Goldman" in q for q in calls_inf["search"]),
      str(calls_inf["search"]))

# ── A. hero subject gate: FDA place/company-only matches ───────────
print("hero subject gate — FDA body-only matches")
FDA_ART = {
    "headline": "FDA Approves First At-Home Flu Treatment "
                "for Children",
    "body": "<p>The FDA cleared the treatment on Monday. A "
            "Dunzo rider delivered the first kits across the "
            "city, and Dunzo said demand was strong. Families "
            "near the Jain Temple welcomed the news; the Jain "
            "Temple hall hosted an awareness camp.</p>"
            + "<p>Filler paragraph for length. </p>" * 30,
    "image_entities": None, "category": "news",
    "image_url": None, "image_backfill_blocked": False,
    "slug": "fda-flu-treatment",
}
JAIN_PAGE = commons_page(
    "File:Jain Temple in Toronto.jpg", 3000, 2000,
    desc="A Jain temple in Toronto where families gather "
         "for weekend classes and community events.",
    cats="Jain Temple")
fda_ents = P.extract_article_entities(FDA_ART)
net_fda, calls_fda = stub_net(
    pages_by_query={"Jain Temple": [JAIN_PAGE]})
rec_fda = {"ledger": [], "notes": []}
pick_fda = P._source_hero(FDA_ART, fda_ents, "", net_fda,
                          1200, set(), rec_fda, lambda *a: None)
check("hero REJECTED: place-only/body-only matches (Dunzo, "
      "Jain Temple) never carry an FDA hero",
      pick_fda is None)
check("Jain Temple never searched for the hero slot",
      not any("Jain" in q for q in calls_fda["search"]),
      str(calls_fda["search"]))

# ── C. era gate ─────────────────────────────────────────────────────
print("era gate")
QUEEN_1939_PAGE = commons_page(
    "File:Queen Street West, Toronto, 1939.jpg", 2400, 1600,
    desc="Queen Street West looking east in Toronto, 1939.",
    cats="Queen Street West")
cand, row = P.evaluate_article_candidate(
    QUEEN_1939_PAGE, "Queen Street", "A — test", 800, 450,
    entity_kind="org/place", story_years=frozenset({2026}))
check("1939 archival street photo rejected for a 2026 story",
      cand is None and "era" in row.get("reason", ""),
      row.get("reason", ""))
cand, row = P.evaluate_article_candidate(
    QUEEN_1939_PAGE, "Queen Street", "A — test", 800, 450,
    entity_kind="org/place")
check("pre-2000 title year rejected even without story years",
      cand is None and "era" in row.get("reason", ""))
cand, row = P.evaluate_article_candidate(
    QUEEN_1939_PAGE, "Queen Street", "A — test", 800, 450,
    entity_kind="org/place", story_historical=True)
check("the same archival photo is fine for a historical story",
      cand is not None, row.get("reason", ""))
WH_2022_PAGE = commons_page(
    "File:White House Diwali celebration 2022.jpg", 3000, 2000,
    desc="Diwali celebration at the White House in 2022.",
    cats="Diwali at the White House")
cand, row = P.evaluate_article_candidate(
    WH_2022_PAGE, "White House", "A — test", 800, 450,
    entity_kind="org/place", story_years=frozenset({2026}))
check("2022 White House Diwali photo rejected for the 2026 "
      "Times Square story (different year's event)",
      cand is None and "era" in row.get("reason", ""),
      row.get("reason", ""))
cand, row = P.evaluate_article_candidate(
    WH_2022_PAGE, "White House", "A — test", 800, 450,
    entity_kind="org/place", story_years=frozenset({2022}))
check("the same photo is fine for the 2022 story it depicts",
      cand is not None, row.get("reason", ""))
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
    "A — test", 800, 450, entity_kind="org/place",
    story_years=frozenset({2019}))
check("keeper: '(born 1993)' does not trip the era gate; "
      "the 2019 event photo fits the 2019 story",
      cand is not None, row.get("reason", ""))

# ── D. inline duplicate check ───────────────────────────────────────
print("inline duplicate check")
check_eq("body image URLs extracted (markdown + html)",
         P._body_image_urls(
             '<p>x</p>![a](https://u/1.jpg)'
             '<figure><img src="https://u/2.jpg"></figure>'),
         {"https://u/1.jpg", "https://u/2.jpg"})
DUP_URL = "https://upload.wikimedia.org/wikipedia/commons/dup.jpg"
DUP_PAGE_1 = commons_page(
    "File:Reserve Bank of India headquarters Mumbai.jpg",
    3200, 2000, url=DUP_URL,
    desc="The headquarters of the Reserve Bank of India in "
         "Mumbai, home of the Bank's first data centre.",
    cats="Reserve Bank of India")
DUP_PAGE_2 = commons_page(
    "File:Bhubaneswar skyline panorama.jpg", 6000, 3000,
    url=DUP_URL,
    desc="Panorama of Bhubaneswar, capital of Odisha, "
         "looking towards the new data centre.",
    cats="Bhubaneswar")
DUP_ART = {
    "headline": "Modi Inaugurates RBI Data Centre in "
                "Bhubaneswar",
    "body": "<p>The Reserve Bank of India opened its centre "
            "in Bhubaneswar.</p>",
    "category": "news",
}
two_ents = [
    {"name": "Reserve Bank of India", "kind": "org/place",
     "source": "headline", "sourceable": True},
    {"name": "Bhubaneswar", "kind": "org/place",
     "source": "headline", "sourceable": True},
]
net_dup, _c = stub_net(pages_by_query={
    "Reserve Bank of India": [DUP_PAGE_1],
    "Bhubaneswar": [DUP_PAGE_2]})
rec_dup = {"ledger": [], "notes": []}
picks_dup = P._source_inlines(DUP_ART, two_ents, "", net_dup,
                              3, set(), rec_dup, lambda *a: None)
check_eq("two entities, same file URL -> only one inline",
         len(picks_dup), 1)
check("the duplicate rejection is ledgered",
      any("duplicate" in r.get("reason", "")
          for r in rec_dup["ledger"]))
net_dup2, _c = stub_net(pages_by_query={
    "Reserve Bank of India": [DUP_PAGE_1]})
rec_dup2 = {"ledger": [], "notes": []}
picks_dup2 = P._source_inlines(
    DUP_ART, two_ents[:1], "", net_dup2, 3, set(), rec_dup2,
    lambda *a: None, exclude_urls=frozenset({DUP_URL}))
check_eq("a file already in the body is never re-added",
         picks_dup2, [])

# ── E. IOB felicitation photos (2026-10-26 root-cause fix) ─────────
# The IOB earnings story (a COMPANY story) shipped with two
# self-published CC0 ceremony photos of its CEO Ajay Kumar
# Srivastava with UP politicians — the Maurya file as hero,
# the Yogi file TWICE as inlines. Two systemic holes:
#   1. The person namesake gate's agreement was satisfied by
#      the markets-finance domain token 'chief' matching
#      'Chief Minister' / 'Deputy Chief Minister' in the
#      files' descriptions — a political office falsely
#      'agreeing' with a banking story. mask_title_phrases
#      now masks the phrase (shared gate module: the reel
#      sourcer is fixed by the same change).
#   2. Inline dedup compared raw URL strings; the same
#      Commons file in a different URL form (original with
#      utm params vs 1920px thumb vs self-hosted storage
#      URL) was invisible to it. Dedup now compares
#      canonical file identity.
# Fixtures below use the files' REAL Commons metadata
# (fetched 2026-10-30): titles, dimensions, descriptions,
# categories, licenses.
print("IOB felicitation-photo regressions")
import re as _re_iob
G = P._SHARED_GATES


def _toks(text):
    return set(_re_iob.findall(r"[a-z]+", (text or "").lower()))


check("'Chief Minister' no longer yields a bare 'chief'",
      "chief" not in _toks(G.mask_title_phrases(
          "Hon. Chief Minister of Uttar Pradesh")))
check("'Deputy Chief Minister' is masked too",
      "chief" not in _toks(G.mask_title_phrases(
          "with Deputy Chief Minister of Uttar Pradesh")))
check("'chief minister' becomes 'minister' (multi-domain, "
      "cannot agree or contradict alone)",
      "minister" in _toks(G.mask_title_phrases(
          "Chief Minister")))
check("a bare 'chief' (fund chief) still registers",
      "chief" in _toks(G.mask_title_phrases(
          "the fund chief spoke")))
check("'Chief Executive Officer' still masks to 'executive'",
      "chief" not in _toks(G.mask_title_phrases(
          "Chief Executive Officer"))
      and "executive" in _toks(G.mask_title_phrases(
          "Chief Executive Officer")))

IOB_ART = {
    "headline": "Indian Overseas Bank Profit Jumps 56% as It "
                "Targets $500 Million Fundraise",
    "body": "<p>Indian Overseas Bank's profit surged. "
            "Managing Director and CEO Ajay Kumar "
            "Srivastava said the bank targets a $500 "
            "million fundraise.</p>",
    "category": "markets-finance",
    "slug": "indian-overseas-bank-profit-jumps-56-targets-"
            "500-million",
}
IOB_ENTS = [
    {"name": "Indian Overseas Bank", "kind": "org/place",
     "source": "headline", "sourceable": True},
    {"name": "Ajay Kumar Srivastava", "kind": "person",
     "source": "body", "sourceable": True},
]
SRIV_CTX = P._person_context_terms(
    IOB_ART, "Ajay Kumar Srivastava", all_entities=IOB_ENTS)
check("the trap is real: the story's person context does "
      "contain the domain token 'chief'",
      "chief" in SRIV_CTX)
_FELICITATION_CATS = (
    "CC-Zero|Self-published work|All media needing "
    "categories as of 2026|Media needing categories as of "
    "25 July 2026")
YOGI_PAGE = commons_page(
    "File:Ajay Kumar Srivastava and hon. Yogi "
    "Adityanath.jpg", 1077, 1129, license_short="CC0",
    desc="Hon. Chief Minister of Uttar Pradesh with Ajay "
         "Kumar Srivastava",
    cats=_FELICITATION_CATS, artist="Ajay Srivastava.2026")
MAURYA_PAGE = commons_page(
    "File:Ajay Kumar Srivastava and Keshav Prasad "
    "Maurya.jpg", 1348, 758, license_short="CC0",
    desc="Ajay Kumar srivastava with Deputy Chief "
         "Minister of Uttar Pradesh",
    cats=_FELICITATION_CATS, artist="Ajay Srivastava.2026")
for _page, _label in ((YOGI_PAGE, "Yogi"), (MAURYA_PAGE,
                                          "Maurya")):
    cand, row = P.evaluate_article_candidate(
        _page, "Ajay Kumar Srivastava",
        "A — Wikimedia Commons", P.INLINE_MIN_W,
        P.INLINE_MIN_H, hint_terms=frozenset(),
        entity_kind="person", person_context=SRIV_CTX,
        person_domain="markets-finance")
    check(f"{_label} felicitation photo REJECTED as an "
          "inline for the bank-earnings story",
          cand is None
          and "namesake guard" in row.get("reason", ""),
          row.get("reason", ""))
cand, row = P.evaluate_article_candidate(
    MAURYA_PAGE, "Ajay Kumar Srivastava",
    "A — Wikimedia Commons", 1200, P.HERO_MIN_H,
    hint_terms=frozenset(), entity_kind="person",
    person_context=SRIV_CTX, person_domain="markets-finance")
check("Maurya felicitation photo REJECTED at hero floors "
      "too (gate-level; the subject gate is a second wall)",
      cand is None
      and "namesake guard" in row.get("reason", ""),
      row.get("reason", ""))
BANKER_PAGE = commons_page(
    "File:Ajay Kumar Srivastava at Indian Overseas Bank "
    "headquarters.jpg", 2400, 1500,
    desc="Ajay Kumar Srivastava, the bank's chief "
         "executive and a career banker, at the Indian "
         "Overseas Bank headquarters in Chennai.",
    cats="Ajay Kumar Srivastava|Indian Overseas Bank")
cand, row = P.evaluate_article_candidate(
    BANKER_PAGE, "Ajay Kumar Srivastava",
    "A — Wikimedia Commons", P.INLINE_MIN_W,
    P.INLINE_MIN_H, hint_terms=frozenset(),
    entity_kind="person", person_context=SRIV_CTX,
    person_domain="markets-finance")
check("a genuine bank-context photo of the same CEO is "
      "still ACCEPTED (agreement via the story's own "
      "vocabulary, not the political title)",
      cand is not None, row.get("reason", ""))

# Canonical-identity dedup: the same file in another URL
# form must read as the same file.
_LEMELLE_ORIG = (
    "https://upload.wikimedia.org/wikipedia/commons/6/63/"
    "Indian_Overseas_Bank_at_Lemelle.jpg"
    "?utm_source=commons.wikimedia.org"
    "&utm_campaign=imageinfo&utm_content=original")
_LEMELLE_THUMB = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "6/63/Indian_Overseas_Bank_at_Lemelle.jpg/"
    "1920px-Indian_Overseas_Bank_at_Lemelle.jpg")
_LEMELLE_STORAGE = (
    "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/"
    "object/public/article-images/indian-overseas-bank-"
    "profit-jumps-56-targets-500-million-indian-overseas-"
    "bank-at-lemelle-web.jpg")
check_eq("file key: API original with utm params",
         P._wikimedia_file_key(_LEMELLE_ORIG),
         "indian overseas bank at lemelle.jpg")
check_eq("file key: 1920px thumb form is the same file",
         P._wikimedia_file_key(_LEMELLE_THUMB),
         "indian overseas bank at lemelle.jpg")
check_eq("file key: the Commons title is the same file",
         P._wikimedia_file_key(
             "File:Indian Overseas Bank at Lemelle.jpg"),
         "indian overseas bank at lemelle.jpg")
LEMELLE_PAGE = commons_page(
    "File:Indian Overseas Bank at Lemelle.jpg", 5969, 3979,
    url=_LEMELLE_ORIG,
    desc="Image of Indian Overseas Bank, Lemelle branch — "
         "the bank's profit centre for its overseas "
         "fundraise business.",
    cats="Indian Overseas Bank|Bank branches in India")
_IOB_ORG_ENTS = IOB_ENTS[:1]
for _label, _kwargs in (
        ("thumb form already in the body",
         {"exclude_urls": frozenset({_LEMELLE_THUMB})}),
        ("self-hosted storage form already in the body",
         {"exclude_urls": frozenset({_LEMELLE_STORAGE})}),
        ("the file is the article's hero (thumb form)",
         {"hero_url": _LEMELLE_THUMB})):
    net_iob, _c = stub_net(pages_by_query={
        "Indian Overseas Bank": [LEMELLE_PAGE]})
    rec_iob = {"ledger": [], "notes": []}
    picks_iob = P._source_inlines(
        IOB_ART, _IOB_ORG_ENTS, "", net_iob, 2, set(),
        rec_iob, lambda *a: None, **_kwargs)
    check_eq(f"duplicate by identity, not URL string: "
             f"{_label}", picks_iob, [])
    check(f"the identity-duplicate rejection is ledgered "
          f"({_label})",
          any("duplicate" in r.get("reason", "")
              for r in rec_iob["ledger"]))
net_iob, _c = stub_net(pages_by_query={
    "Indian Overseas Bank": [LEMELLE_PAGE]})
rec_iob = {"ledger": [], "notes": []}
picks_iob = P._source_inlines(
    IOB_ART, _IOB_ORG_ENTS, "", net_iob, 2, set(), rec_iob,
    lambda *a: None)
check_eq("the same candidate IS picked when the article "
         "does not already carry it", len(picks_iob), 1)

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
