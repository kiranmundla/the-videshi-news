#!/usr/bin/env python3
"""
test_inline_identity_sourcing.py — regression corpus for the
2026-11-01 inline identity fix (Kiran: "Fix the inline route
now"). Open search is abolished for inlines in the live picture
pass: _source_inlines may only draw on the verified
person_images cache, the resolved entity's P18 file, or files
that DEPICT the resolved entity (Commons P180), each through
the shared evaluator with identity_verified=True and the
entity's corpus blocklist, plus a locality gate for places.

The corpus replays:
  * 2026-11-01's wrong inlines (all caught after the fact by
    review passes, none by a gate): the London, Ontario police
    HQ + 2008 Scientology protest + Neasden Temple Diwali files
    on the Palestine Action (London, UK) story; the Vrindavan
    temple aerial on the Uttarakhand Char Dham story; the
    Nordic-combined skier on the women's cricket World Cup
    story; the Mission: Impossible premiere photo on the
    Ramayana stories; the Ajmer fairground on the Jailer 2
    story; the Strasbourg lithograph on the US midterms story.
  * The 2026-10-26 set (from the day's memory log): Canva
    Research -> Wikimania space photo; 'Saudi Arabia' ->
    pilgrim at Masjid Al Haram; 'Middle East' -> Faqua village;
    Federation Square, Nicholls ACT for Melbourne's; the
    'Secret Toronto' possessive fragment; outlet entities.
  * Verified keepers that must still source (the genuine
    Palestine Action protest photo, a Kedarnath depicts file,
    a Melbourne Federation Square photo, P18 + cache person
    portraits, the Toronto Pearson ramp photo doctrine).

Every wrong case must produce NO inline. The search seams are
rigged to raise: if the inline route ever consults open search
again, this suite fails loudly.

All network is stubbed. Run:
  python3 test_inline_identity_sourcing.py  (exit 0 = all pass)
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


def identity_net(resolutions=None, depicts_by_qid=None,
                 pages_by_title=None, items_by_qid=None,
                 cache=None):
    """A net whose ONLY sourcing seams are the identity ones.
    The search seams raise — the inline route must never
    consult them."""
    calls = {"search": [], "resolve": [], "file_info": []}

    def _boom_search(q, limit=10):
        calls["search"].append(q)
        raise AssertionError(
            "open Commons search consulted by the inline route")

    def _boom_brave(q, n=8):
        calls["search"].append(q)
        raise AssertionError(
            "Brave discovery consulted by the inline route")

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


def run_inlines(article, ents, net, want=3):
    rec = {"ledger": [], "notes": []}
    picks = P._source_inlines(article, ents, "", net, want, set(),
                              rec, lambda *a: None)
    return picks, rec


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


def ent(name, kind="org/place", sourceable=True, source="headline"):
    return {"name": name, "kind": kind, "source": source,
            "sourceable": sourceable}


# ── 2026-11-01: London (Palestine Action, London UK) ─────────────
print("2026-11-01 corpus — London")
LONDON_ART = {
    "headline": "Palestine Action Protest at US Embassy in "
                "London Sees 325 Arrested",
    "body": "<p>Hundreds gathered in London on Saturday. "
            "Police made 325 arrests near the US embassy.</p>",
    "category": "news", "slug": "palestine-action-london",
}
ONTARIO_HQ = ("File:London Police Services headquarters, "
              "London, Ontario, 2026-07-31.jpg")
COS_PROTEST = "File:London Feb 10 2008 CoS protest AB 6.JPG"
PROTEST_PAGE = commons_page(
    "File:Palestine Action Protest, London, Saturday 6th "
    "September - 04.jpg", 4000, 3000,
    desc="A Palestine Action protest in London on Saturday "
         "6 September.",
    cats="Palestine Action|Protests in London")
SKYLINE_PAGE = commons_page(
    "File:London Skyline (125508655).jpeg", 2048, 1152,
    license_short="CC BY-SA 3.0",
    desc="The London skyline at dusk.",
    cats="Skylines of London")
ONTARIO_PAGE = commons_page(
    ONTARIO_HQ, 2400, 1500,
    desc="Headquarters of the London Police Service in "
         "London, Ontario, Canada.",
    cats="London Police Service|Buildings in London, Ontario")
LONDON_ITEM = {
    "description": "capital and largest city of England and "
                   "the United Kingdom",
    "located_in": ["Greater London"], "country": "United Kingdom"}
LONDON_RES = resolution(
    "London", "Q84", type_="place",
    p18="London Skyline (125508655).jpeg",
    blocked=["London Police Services headquarters, London, "
             "Ontario, 2026-07-31.jpg",
             "London Feb 10 2008 CoS protest AB 6.JPG"])

net, calls = identity_net(
    resolutions={"London": LONDON_RES},
    depicts_by_qid={"Q84": [{"title": PROTEST_PAGE["title"]}]},
    pages_by_title={PROTEST_PAGE["title"]: PROTEST_PAGE,
                    SKYLINE_PAGE["title"]: SKYLINE_PAGE},
    items_by_qid={"Q84": LONDON_ITEM})
picks, rec = run_inlines(LONDON_ART, [ent("London")], net)
check("keeper: London sources a genuine London picture "
      "(P18 skyline or the real protest photo)",
      len(picks) == 1
      and picks[0]["title"] in (SKYLINE_PAGE["title"],
                                PROTEST_PAGE["title"]),
      str([p["title"] for p in picks]))

net, calls = identity_net(
    resolutions={"London": LONDON_RES},
    depicts_by_qid={"Q84": [{"title": ONTARIO_HQ}]},
    pages_by_title={ONTARIO_HQ: ONTARIO_PAGE},
    items_by_qid={"Q84": LONDON_ITEM})
picks, rec = run_inlines(LONDON_ART, [ent("London")], net)
check_eq("London, Ontario police HQ offered as depicts -> "
         "NO inline (corpus blocklist)", picks, [])
check("the blocklist rejection is ledgered",
      any("corpus" in r.get("reason", "")
          for r in rec["ledger"]), str(rec["ledger"]))

LONDON_RES_NOBLOCK = resolution(
    "London", "Q84", type_="place",
    p18="London Skyline (125508655).jpeg")
net, calls = identity_net(
    resolutions={"London": LONDON_RES_NOBLOCK},
    depicts_by_qid={"Q84": [{"title": ONTARIO_HQ}]},
    pages_by_title={ONTARIO_HQ: ONTARIO_PAGE,
                    SKYLINE_PAGE["title"]: SKYLINE_PAGE},
    items_by_qid={"Q84": LONDON_ITEM})
picks, rec = run_inlines(LONDON_ART, [ent("London")], net)
check("with the blocklist bypassed, the LOCALITY gate alone "
      "rejects the Ontario HQ (the pick is the genuine skyline)",
      len(picks) == 1
      and picks[0]["title"] == SKYLINE_PAGE["title"]
      and any("locality" in r.get("reason", "")
              for r in rec["ledger"]), str(rec["ledger"]))

net, calls = identity_net(
    resolutions={"London": LONDON_RES},
    depicts_by_qid={"Q84": [{"title": COS_PROTEST}]},
    pages_by_title={COS_PROTEST: commons_page(
        COS_PROTEST, 2400, 1600,
        desc="Church of Scientology protest in London, "
             "10 February 2008.",
        cats="Anonymous protests")},
    items_by_qid={"Q84": LONDON_ITEM})
picks, rec = run_inlines(LONDON_ART, [ent("London")], net)
check_eq("2008 Scientology protest offered as depicts -> "
         "NO inline (corpus blocklist)", picks, [])

# Home Office: the registry record carries NO Wikidata item —
# resolution itself fails closed, the Neasden file is never read.
NEASDEN = ("File:Home Secretary & Prime Minister Diwali visit "
           "to Neasden Temple to Neasden Temple in 2021.jpg")
net, calls = identity_net(
    resolutions={"Home Office": resolution(
        "Home Office", None,
        blocked=["Home Secretary & Prime Minister Diwali visit "
                 "to Neasden Temple to Neasden Temple in "
                 "2021.jpg"])})
picks, rec = run_inlines(
    LONDON_ART, [ent("Home Office")], net)
check_eq("'Home Office' (no Wikidata identity) -> NO inline",
         picks, [])
check("the Neasden Temple file was never even read",
      NEASDEN not in calls["file_info"], str(calls["file_info"]))

# ── 2026-11-01: Char Dham (Uttarakhand) vs Vrindavan ─────────────
print("2026-11-01 corpus — Char Dham")
CHARDHAM_ART = {
    "headline": "Uttarakhand Chopper Crash Probe Widens: "
                "Two-Pilot Rule for Char Dham Operators",
    "body": "<p>The Char Dham yatra routes in Uttarakhand "
            "face new rules after the crash.</p>",
    "category": "news", "slug": "uttarakhand-chopper-crash",
}
VRINDAVAN = ("File:Aerial View of Char Dham Vrindavan from "
             "National Highway.jpg")
VRINDAVAN_PAGE = commons_page(
    VRINDAVAN, 4000, 2250,
    desc="Aerial view of the Char Dham temple complex in "
         "Vrindavan, Uttar Pradesh.",
    cats="Char Dham Vrindavan|Hindu temples in Uttar Pradesh")
KEDARNATH_PAGE = commons_page(
    "File:Kedarnath Temple in Uttarakhand.jpg", 3200, 2000,
    desc="Kedarnath Temple, one of the Char Dham sites, in "
         "the Garhwal Himalayas of Uttarakhand.",
    cats="Kedarnath|Hindu temples in Uttarakhand")
CHARDHAM_ITEM = {
    "description": "four Hindu pilgrimage sites in "
                   "Uttarakhand, India",
    "located_in": ["Uttarakhand"], "country": "India"}
CHARDHAM_RES = resolution(
    "Char Dham", "Q-TEST-CD", type_="place",
    blocked=["Aerial View of Char Dham Vrindavan from "
             "National Highway.jpg"])

net, calls = identity_net(
    resolutions={"Char Dham": CHARDHAM_RES},
    depicts_by_qid={"Q-TEST-CD": [{"title": VRINDAVAN}]},
    pages_by_title={VRINDAVAN: VRINDAVAN_PAGE},
    items_by_qid={"Q-TEST-CD": CHARDHAM_ITEM})
picks, rec = run_inlines(CHARDHAM_ART, [ent("Char Dham")], net)
check_eq("Vrindavan aerial offered as depicts -> NO inline "
         "(corpus blocklist)", picks, [])

net, calls = identity_net(
    resolutions={"Char Dham": resolution("Char Dham",
                                         "Q-TEST-CD",
                                         type_="place")},
    depicts_by_qid={"Q-TEST-CD": [{"title": VRINDAVAN}]},
    pages_by_title={VRINDAVAN: VRINDAVAN_PAGE},
    items_by_qid={"Q-TEST-CD": CHARDHAM_ITEM})
picks, rec = run_inlines(CHARDHAM_ART, [ent("Char Dham")], net)
check_eq("with the blocklist bypassed, the LOCALITY gate "
         "alone rejects Vrindavan for the Uttarakhand circuit "
         "(Uttar Pradesh != Uttarakhand)", picks, [])
check("the locality rejection is ledgered",
      any("locality" in r.get("reason", "")
          for r in rec["ledger"]), str(rec["ledger"]))

net, calls = identity_net(
    resolutions={"Char Dham": CHARDHAM_RES},
    depicts_by_qid={"Q-TEST-CD": [
        {"title": KEDARNATH_PAGE["title"]}]},
    pages_by_title={KEDARNATH_PAGE["title"]: KEDARNATH_PAGE},
    items_by_qid={"Q-TEST-CD": CHARDHAM_ITEM})
picks, rec = run_inlines(CHARDHAM_ART, [ent("Char Dham")], net)
check_eq("keeper: a genuine Char Dham site photo (Kedarnath) "
         "still sources", len(picks), 1)

# ── 2026-11-01: World Cup (cricket) vs FIS Nordic Combined ───────
print("2026-11-01 corpus — World Cup")
WC_ART = {
    "headline": "One Year On: India's Women Recall the World "
                "Cup Win That Changed Everything",
    "body": "<p>The India women's cricket team lifted the "
            "World Cup a year ago.</p>",
    "category": "sports", "slug": "india-women-world-cup",
}
FIS = ("File:2026-01-17 FIS Nordic Combined World Cup Oberhof "
       "2026 – Women's Individual Compact by Sandro Halank"
       "–138.jpg")
CRICKET_PAGE = commons_page(
    "File:India women cricket team celebrating.jpg", 3000, 2000,
    desc="The India women's cricket team celebrating a wicket "
         "during the World Cup final.",
    cats="India women's national cricket team")
WC_RES = resolution(
    "Cricket World Cup", "Q-TEST-CWC", aliases=["World Cup"],
    blocked=["2026-01-17 FIS Nordic Combined World Cup Oberhof "
             "2026 – Women's Individual Compact by Sandro "
             "Halank–138.jpg"])
net, calls = identity_net(
    resolutions={"World Cup": WC_RES},
    depicts_by_qid={"Q-TEST-CWC": [{"title": FIS}]},
    pages_by_title={FIS: commons_page(
        FIS, 2400, 1600,
        desc="Katharina Gruber in the FIS Nordic Combined "
             "World Cup at Oberhof.",
        cats="FIS Nordic Combined World Cup")})
picks, rec = run_inlines(WC_ART, [ent("World Cup")], net)
check_eq("Nordic-combined skier offered for 'World Cup' -> "
         "NO inline (corpus blocklist)", picks, [])
net, calls = identity_net(
    resolutions={"World Cup": WC_RES},
    depicts_by_qid={"Q-TEST-CWC": [
        {"title": CRICKET_PAGE["title"]}]},
    pages_by_title={CRICKET_PAGE["title"]: CRICKET_PAGE})
picks, rec = run_inlines(WC_ART, [ent("World Cup")], net)
check_eq("keeper: a genuine cricket World Cup photo still "
         "sources", len(picks), 1)

# ── 2026-11-01: fragment entities (Part One / Crore / Election) ──
print("2026-11-01 corpus — fragment entities fail closed")
MI = ("File:Mission Impossible – Dead Reckoning Part one "
      "(53019462143).jpg")
net, calls = identity_net(
    resolutions={"Part One": resolution("Part One", None)})
picks, rec = run_inlines(
    {"headline": "Ramayana Part One: Rs 4,000 Crore Budget "
                  "Fuels Advance Booking Buzz",
     "body": "<p>Ramayana Part One is mounted on a huge "
             "budget.</p>",
     "category": "entertainment", "slug": "ramayana-4000-crore"},
    [ent("Part One")], net)
check_eq("'Part One' fragment (no identity) -> NO inline; "
         "the Mission: Impossible premiere photo is unreachable",
         picks, [])
check("the MI file was never read", MI not in calls["file_info"])

AJMER = "File:Krash chauhan aagyo ajmer.jpg"
net, calls = identity_net(
    resolutions={"Crore Entertainment": resolution(
        "Crore Entertainment", None)})
picks, rec = run_inlines(
    {"headline": "Jailer 2 Box Office: First Tamil Film to "
                  "Cross Rs 800 Crore",
     "body": "<p>Jailer 2 entered the Rs 800 crore club.</p>",
     "category": "entertainment", "slug": "jailer-2-800-crore"},
    [ent("Crore Entertainment")], net)
check_eq("'Crore Entertainment' fragment -> NO inline; the "
         "Ajmer fairground photo is unreachable", picks, [])
check("the Ajmer file was never read",
      AJMER not in calls["file_info"])

STRASBOURG = ("File:A. Dusch Elections à Strasbourg "
              "Schwoertag inv. CE LXIII.56 a.jpg")
net, calls = identity_net(
    resolutions={"Election Day": resolution("Election Day",
                                            None)})
picks, rec = run_inlines(
    {"headline": "US Midterm Results 2026: When Winners Are "
                  "Announced, State Timings",
     "body": "<p>Election Day counting continues across "
             "states.</p>",
     "category": "news", "slug": "us-midterm-results-2026"},
    [ent("Election Day")], net)
check_eq("'Election Day' generic concept -> NO inline; the "
         "Strasbourg lithograph is unreachable", picks, [])
check("the Strasbourg file was never read",
      STRASBOURG not in calls["file_info"])

# ── 2026-10-26 set ────────────────────────────────────────────────
print("2026-10-26 corpus")
net, calls = identity_net()
picks, rec = run_inlines(
    {"headline": "Canva Research Shows Teams Ship Designs "
                  "Faster",
     "body": "<p>Canva Research published new findings.</p>",
     "category": "technology", "slug": "canva-research"},
    [ent("Canva Research")], net)
check_eq("Oct 26: 'Canva Research' has no identity -> NO "
         "inline (was: a Wikimania space-research photo)",
         picks, [])

net, calls = identity_net(
    resolutions={"Saudi Arabia": resolution(
        "Saudi Arabia", "Q-TEST-SA", type_="place")},
    depicts_by_qid={"Q-TEST-SA": []},
    items_by_qid={"Q-TEST-SA": {
        "description": "country in West Asia",
        "located_in": [], "country": "Saudi Arabia"}})
picks, rec = run_inlines(
    {"headline": "Oil Prices Ease as Saudi Arabia Signals "
                  "Output Steady",
     "body": "<p>Saudi Arabia kept output steady.</p>",
     "category": "markets-finance", "slug": "oil-prices"},
    [ent("Saudi Arabia")], net)
check_eq("Oct 26: 'Saudi Arabia' with no depicts files -> NO "
         "inline (was: a pilgrim at Masjid Al Haram)", picks, [])

net, calls = identity_net()
picks, rec = run_inlines(
    {"headline": "Rupee Rally Pauses as Middle East Tensions "
                  "Simmer",
     "body": "<p>The rupee tracked Middle East developments."
             "</p>",
     "category": "markets-finance", "slug": "rupee-rally"},
    [ent("Middle East")], net)
check_eq("Oct 26: 'Middle East' region has no single identity "
         "-> NO inline (was: the village of Faqua)", picks, [])

FEDSQ_ART = {
    "headline": "Diwali in Victoria: Federation Square Hosts "
                "Festival of Lights",
    "body": "<p>Federation Square in Melbourne hosts the "
            "Diwali celebration.</p>",
    "category": "news", "slug": "diwali-victoria",
}
FEDSQ_ITEM = {
    "description": "public square in Melbourne, Victoria, "
                   "Australia",
    "located_in": ["Melbourne", "Victoria"],
    "country": "Australia"}
FEDSQ_RES = resolution("Federation Square", "Q-TEST-FS",
                       type_="place")
NICHOLLS_PAGE = commons_page(
    "File:Federation Square, Nicholls.jpg", 2400, 1600,
    desc="Federation Square cultural precinct in Nicholls, "
         "Canberra.",
    cats="Federation Square, Nicholls|Sculptures in the "
         "Australian Capital Territory")
MELB_PAGE = commons_page(
    "File:Federation Square Melbourne at dusk.jpg", 3200, 2000,
    desc="Federation Square in Melbourne at dusk during the "
         "Diwali festival.",
    cats="Federation Square, Melbourne|Diwali in Melbourne")
net, calls = identity_net(
    resolutions={"Federation Square": FEDSQ_RES},
    depicts_by_qid={"Q-TEST-FS": [
        {"title": NICHOLLS_PAGE["title"]}]},
    pages_by_title={NICHOLLS_PAGE["title"]: NICHOLLS_PAGE},
    items_by_qid={"Q-TEST-FS": FEDSQ_ITEM})
picks, rec = run_inlines(FEDSQ_ART, [ent("Federation Square")],
                         net)
check_eq("Oct 26: Federation Square, Nicholls ACT offered for "
         "Melbourne's -> NO inline (locality gate)", picks, [])
check("the locality rejection is ledgered",
      any("locality" in r.get("reason", "")
          for r in rec["ledger"]), str(rec["ledger"]))
net, calls = identity_net(
    resolutions={"Federation Square": FEDSQ_RES},
    depicts_by_qid={"Q-TEST-FS": [{"title": MELB_PAGE["title"]}]},
    pages_by_title={MELB_PAGE["title"]: MELB_PAGE},
    items_by_qid={"Q-TEST-FS": FEDSQ_ITEM})
picks, rec = run_inlines(FEDSQ_ART, [ent("Federation Square")],
                         net)
check_eq("keeper: Melbourne's own Federation Square photo "
         "still sources", len(picks), 1)

net, calls = identity_net()
picks, rec = run_inlines(
    {"headline": "Toronto Diwali Festival Draws Thousands",
     "body": "<p>Shoppers thronged Toronto stores.</p>",
     "category": "news", "slug": "toronto-diwali"},
    [ent("Secret Toronto", sourceable=False)], net)
check_eq("Oct 26: 'Secret Toronto' possessive fragment is not "
         "sourceable -> NO inline, resolution never attempted",
         picks, [])
check("'Secret Toronto' never reached the resolver",
      "Secret Toronto" not in calls["resolve"])

net, calls = identity_net()
picks, rec = run_inlines(
    {"headline": "Appeals Court Weighs Deportation Case",
     "body": "<p>The court heard arguments.</p>",
     "category": "news", "slug": "appeals-court"},
    [ent("Reuters")], net)
check_eq("Oct 26: outlet entity 'Reuters' triaged -> NO inline",
         picks, [])
check("the outlet never reached the resolver",
      "Reuters" not in calls["resolve"])

net, calls = identity_net()
picks, rec = run_inlines(
    {"headline": "Hindi Trailer of Jailer 2 Trends Online",
     "body": "<p>The Hindi trailer trended.</p>",
     "category": "entertainment", "slug": "jailer-2-hindi"},
    [ent("Hindi")], net)
check_eq("language entity 'Hindi' triaged -> NO inline",
         picks, [])
check("the language never reached the resolver",
      "Hindi" not in calls["resolve"])

# ── keepers: persons (P18 + verified cache) ───────────────────────
print("keepers — persons")
PANT_PAGE = commons_page(
    "File:Rishabh Pant in 2024.jpg", 2000, 1400,
    desc="Rishabh Pant, Indian cricketer, during a Test "
         "match.",
    cats="Rishabh Pant")
net, calls = identity_net(
    resolutions={"Rishabh Pant": resolution(
        "Rishabh Pant", "Q-TEST-RP", type_="person",
        p18="Rishabh Pant in 2024.jpg")},
    pages_by_title={PANT_PAGE["title"]: PANT_PAGE})
picks, rec = run_inlines(
    {"headline": "Rishabh Pant Century Puts India on Top",
     "body": "<p>Rishabh Pant scored a century.</p>",
     "category": "sports", "slug": "pant-century"},
    [ent("Rishabh Pant", kind="person")], net)
check("keeper: a person's P18 portrait still sources",
      len(picks) == 1 and "P18" in picks[0]["route"],
      str([p.get("route") for p in picks]))
check("the P18 pick carries full provenance",
      bool(picks) and all(picks[0].get(k) for k in
                          ("attribution", "verification",
                           "license", "source_page")))

net, calls = identity_net(
    cache={"Ajay Kumar Srivastava":
           "https://storage.test/verified/srivastava.jpg"})
picks, rec = run_inlines(
    {"headline": "Indian Overseas Bank Profit Jumps 56%",
     "body": "<p>Ajay Kumar Srivastava led the bank.</p>",
     "category": "markets-finance", "slug": "iob-profit"},
    [ent("Ajay Kumar Srivastava", kind="person",
         source="body")], net)
check("keeper: the verified person_images cache still "
      "sources a person inline",
      len(picks) == 1
      and picks[0]["route"] == "person_images cache",
      str([p.get("route") for p in picks]))

# ── resolution discipline ─────────────────────────────────────────
print("resolution discipline")
INFY_PAGE = commons_page(
    "File:Infosys campus in Bengaluru.jpg", 3000, 1800,
    desc="The Infosys campus in Bengaluru.",
    cats="Infosys")
INFY_ART = {"headline": "Infosys Results Beat Street "
                        "Estimates",
            "body": "<p>Infosys reported strong results.</p>",
            "category": "markets-finance", "slug": "infosys-q2"}
net, calls = identity_net(
    resolutions={"Infosys": resolution(
        "Infosys", "Q-TEST-INF", type_="company",
        method="wikidata-sitelinks", p18=INFY_PAGE["title"])},
    pages_by_title={INFY_PAGE["title"]: INFY_PAGE})
picks, rec = run_inlines(
    INFY_ART, [ent("Infosys", source="image_entities")], net)
check_eq("single-token entity + LIVE resolution -> NO inline "
         "(registry only)", picks, [])
net, calls = identity_net(
    resolutions={"Infosys": resolution(
        "Infosys", "Q-TEST-INF", type_="company",
        p18=INFY_PAGE["title"])},
    pages_by_title={INFY_PAGE["title"]: INFY_PAGE})
picks, rec = run_inlines(
    INFY_ART, [ent("Infosys", source="image_entities")], net)
check_eq("single-token entity + REGISTRY resolution -> "
         "sources", len(picks), 1)

net, calls = identity_net(
    resolutions={"Jailer 2": resolution(
        "Jailer 3", "Q-TEST-J3", method="wikidata-context")})
picks, rec = run_inlines(
    {"headline": "Jailer 2 Box Office Storm Continues",
     "body": "<p>Jailer 2 continued its run.</p>",
     "category": "entertainment", "slug": "jailer-2-bo"},
    [ent("Jailer 2")], net)
check_eq("live resolution naming a different entity "
         "('Jailer 3', numeral veto) -> NO inline", picks, [])

net, calls = identity_net(
    resolutions={"Mercury": resolution(
        "Mercury", "Q-TEST-ME", method="wikidata-context",
        confidence="low",
        notes="ambiguous: planet, element and car brand "
              "candidates")})
picks, rec = run_inlines(
    {"headline": "Mercury Rises in the Evening Sky",
     "body": "<p>Mercury was visible at dusk.</p>",
     "category": "news", "slug": "mercury-sky"},
    [ent("Mercury")], net)
check_eq("ambiguous low-confidence resolution -> NO inline",
         picks, [])

# ── intra-result dedup + serve variant ───────────────────────────
print("intra-result dedup / serve variant")
LEMELLE = "File:Indian Overseas Bank at Lemelle.jpg"
LEMELLE_PAGE = commons_page(
    LEMELLE, 5969, 3979,
    desc="Image of Indian Overseas Bank, Lemelle branch.",
    cats="Indian Overseas Bank|Bank branches in India")
net, calls = identity_net(
    resolutions={"Indian Overseas Bank": resolution(
        "Indian Overseas Bank", "Q-TEST-IOB", type_="company",
        p18="Indian Overseas Bank at Lemelle.jpg")},
    depicts_by_qid={"Q-TEST-IOB": [{"title": LEMELLE},
                                   {"title": LEMELLE}]},
    pages_by_title={LEMELLE: LEMELLE_PAGE})
picks, rec = run_inlines(
    {"headline": "Indian Overseas Bank Profit Jumps 56%",
     "body": "<p>Indian Overseas Bank's profit surged.</p>",
     "category": "markets-finance", "slug": "iob-profit-2"},
    [ent("Indian Overseas Bank")], net)
check_eq("the same file offered as P18 AND twice as depicts "
         "is considered once and picked once", len(picks), 1)
check_eq("its file page was read exactly once",
         calls["file_info"].count(LEMELLE), 1)

BIG_PAGE = commons_page(
    "File:Reserve Bank of India headquarters Mumbai.jpg",
    6000, 4000,
    desc="The headquarters of the Reserve Bank of India in "
         "Mumbai.",
    cats="Reserve Bank of India",
    url="https://upload.wikimedia.org/wikipedia/commons/2/29/"
        "RBI_headquarters.jpg",
    size=50_000_000)
net, calls = identity_net(
    resolutions={"Reserve Bank of India": resolution(
        "Reserve Bank of India", "Q-TEST-RBI", type_="company",
        p18="Reserve Bank of India headquarters Mumbai.jpg")},
    pages_by_title={BIG_PAGE["title"]: BIG_PAGE})
picks, rec = run_inlines(
    {"headline": "RBI Opens New Data Centre",
     "body": "<p>The Reserve Bank of India opened the "
             "centre.</p>",
     "category": "news", "slug": "rbi-data-centre"},
    [ent("Reserve Bank of India")], net)
check("oversized identity original is served via its 1920px "
      "variant, not the raw file",
      len(picks) == 1
      and picks[0]["file_url"] ==
      "https://upload.wikimedia.org/wikipedia/commons/thumb/"
      "2/29/RBI_headquarters.jpg/1920px-RBI_headquarters.jpg"
      and picks[0].get("serve_variant") is True,
      str([p.get("file_url") for p in picks]))

# ── 2026-11-11: generic concepts never source inlines ──────
print("2026-11-11 corpus — concept block")
AMD_ART = {
    "headline": "AMD Data Center Revenue Beats Estimates as "
                "AI Demand Surges",
    "body": "<p>Advanced Micro Devices said data center "
            "revenue rose sharply in the quarter.</p>",
    "category": "markets-finance", "slug": "amd-data-center",
}
SYLLA_PAGE_I = commons_page(
    "File:Assane SYLLA.jpg", 1600, 2000,
    desc="Assane Sylla, a systems engineer, photographed at "
         "a conference in Dakar.",
    cats="Men of Senegal|Data centers")
CERN_PAGE_I = commons_page(
    "File:CERN Server 03.jpg", 2400, 1600,
    desc="Servers in the CERN data centre.",
    cats="CERN data centre")
DC_RES = resolution("Data Center", "Q671224", type_="other",
                    p18="CERN Server 03.jpg")
net, calls = identity_net(
    resolutions={"Data Center": DC_RES},
    depicts_by_qid={"Q671224": [{"title": SYLLA_PAGE_I["title"]}]},
    pages_by_title={SYLLA_PAGE_I["title"]: SYLLA_PAGE_I,
                    CERN_PAGE_I["title"]: CERN_PAGE_I})
picks, rec = run_inlines(AMD_ART, [ent("Data Center")], net)
check("concept: 'Data Center' produces NO inline (neither "
      "the SYLLA depicts portrait nor its own P18)",
      picks == [], str([p["title"] for p in picks]))
check("concept: the rejection is ledgered as a concept block",
      any("concept" in (r.get("reason") or "")
          for r in rec["ledger"]), str(rec["ledger"]))

GOLD_ART = {
    "headline": "Gold Prices Hit a Record as Investors Seek "
                "Safety",
    "body": "<p>Gold extended its rally on Monday.</p>",
    "category": "markets-finance", "slug": "gold-prices-record",
}
SULE_PAGE_I = commons_page(
    "File:Sule Pagoda 2018.jpg", 2400, 1600,
    desc="The Sule Pagoda in Yangon, Myanmar.",
    cats="Sule Pagoda|Yangon")
GOLD_RES = resolution("Gold", "Q897", type_="other",
                      p18="Gold-crystals.jpg")
net, calls = identity_net(
    resolutions={"Gold": GOLD_RES},
    depicts_by_qid={"Q897": [{"title": SULE_PAGE_I["title"]}]},
    pages_by_title={SULE_PAGE_I["title"]: SULE_PAGE_I})
picks, rec = run_inlines(GOLD_ART, [ent("Gold")], net)
check("concept: 'Gold' produces NO inline (Sule Pagoda "
      "depicts climb blocked)", picks == [],
      str([p["title"] for p in picks]))

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
