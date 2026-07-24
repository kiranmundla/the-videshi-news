#!/usr/bin/env python3
"""Immigration writer — 2026-07-05 07:00 PDT batch."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1: NIW/EB-1A Approval Rates Crashing ──────────────────────

article1_body = """The green card backlog for Indian nationals in the EB-2 and EB-3 employer-sponsored categories stretches decades. So tens of thousands of Indian professionals have turned to the two self-petition routes that bypass the labour certification grind: the EB-2 National Interest Waiver and the EB-1A Extraordinary Ability petition.

For years, these were the exit ramp. File on your own terms, skip the employer sponsorship dance, and — if the petition held up — land a green card years faster than the traditional queue. Between 2020 and 2022, it worked spectacularly. The NIW approval rate touched 96 per cent in FY2022 as USCIS ploughed through a modest pool of filings during the pandemic. EB-1A hovered around 75 per cent.

Then the rush arrived, and the gates narrowed.

## The Numbers Tell the Story

USCIS I-140 adjudication data through the end of FY2025 shows a collapse in approval rates that has not attracted the attention it deserves:

**EB-2 National Interest Waiver:**
- FY2022: ~96 per cent approved
- FY2023: ~80 per cent
- FY2024: ~71 per cent
- FY2025 full year: 55.2 per cent
- FY2025 Q4 alone: **35.7 per cent**

**EB-1A Extraordinary Ability:**
- FY2022-2024: 70-75 per cent range
- FY2025 full year: 66.9 per cent
- FY2025 Q4: **~53 per cent**

By contrast, the O-1 nonimmigrant visa for extraordinary ability — which grants temporary status, not a green card — still clears 90 per cent. The difference tells you something: USCIS is tightening the permanent-residence gate while leaving the temporary pathway alone.

## Why Approvals Are Falling

Two forces are at work. First, filing volumes have surged. More people are applying for EB-1A and NIW than at any point in the programme's history. Indian professionals, in particular, have flooded the pipeline as the traditional H-1B-to-green-card path has become nearly impassable. When a programme designed for a few thousand filings a year receives multiples of that, every application faces more scrutiny.

Second, USCIS adjudicators are applying existing frameworks with sharper teeth. In NIW cases, officers are demanding measurable, demonstrated impact on the United States — not projections, not sector-wide claims, but concrete evidence that the petitioner's work extends beyond a single employer. In EB-1A cases, the agency's two-step "final merits" analysis has become the kill zone: even applicants who satisfy five or six of the ten regulatory criteria are being denied at the second step, where an officer decides subjectively whether the record shows "sustained national or international acclaim."

## A Federal Court Pushes Back

One Indian professional fought that subjective denial and won. In *Mukherji v. Miller* (D. Neb., January 28, 2026), journalist Anahita Mukherji challenged USCIS after the agency conceded she met five of the ten EB-1A criteria — well above the required three — but denied her petition at the final merits stage.

The U.S. District Court for the District of Nebraska did not merely remand the case. It vacated the denial and ordered approval, finding that USCIS's two-step framework was adopted through internal policy memos without the notice-and-comment rulemaking required by the Administrative Procedure Act. In the court's words, the denial was "arbitrary and capricious."

The decision leans on *Loper Bright Enterprises v. Raimondo*, the 2024 Supreme Court ruling that overturned *Chevron* deference and required courts to exercise independent judgement on agency actions. *Mukherji* is limited to one district — it does not bind USCIS nationally — but immigration attorneys say it provides persuasive authority for future challenges.

## What This Means for Indian Professionals

The strategic calculus has shifted. Filing a single NIW petition and waiting was once a reasonable bet. Today, with approval rates below 36 per cent in the most recent quarter, it is closer to a coin flip — and a coin flip that costs thousands of dollars in legal fees and months of preparation.

Immigration attorneys now advise a dual-filing strategy: submit both an EB-2 NIW and an EB-1A petition simultaneously. The two are independent, and a denial on one does not affect the other. Critically, priority dates are portable between employment-based categories — so a professional who secures an NIW approval and later builds an EB-1A case can carry forward the earlier priority date, potentially shaving years off the green card wait.

The irony is sharp. Indian professionals turned to self-petition routes precisely because the employer-sponsored path was broken. Now the escape route itself is filling with traffic, and USCIS is installing speed bumps. The lesson is not that the door is closed — two in three EB-1A petitions still get through — but that a well-framed, evidence-heavy case is no longer optional. It is the price of entry."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two in Three EB-1A Petitions Still Pass. The NIW Is a Different Story",
    "subheadline": "The self-petition green card routes that Indian professionals turned to as an escape from the employer-sponsored backlog are seeing approval rates crash — NIW fell to 35.7 per cent last quarter.",
    "slug": make_slug("niw-eb1a-approval-rates-crash-mukherji-indian-professionals"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals trapped in decades-long EB-2/EB-3 employer-sponsored green card backlogs have flooded the NIW and EB-1A self-petition routes — and now those routes are getting harder too, with NIW approvals falling from 96% to 35.7% in three years.",
    "tags": ["niw", "eb-1a", "green-card", "uscis", "self-petition", "mukherji", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mondaq / Garfinkel Immigration Law Firm", "url": "https://www.mondaq.com/unitedstates/work-visas/1587398/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners"},
        {"name": "Wildes & Weinberg P.C.", "url": "https://www.wildeslaw.com/blog/a-federal-court-pushes-back-on-usciss-eb-1a-final-merits-denials"},
        {"name": "Scott Legal P.C. / LegalServicesIncorporated", "url": "https://www.legalservicesincorporated.com/immigration-law/federal-court-finds-eb-1a-final-merits-analysis-policy-unlawful/"},
        {"name": "Passage Immigration Law", "url": "https://passage.law/blog/eb1a-vs-niw-2026"},
        {"name": "Manifest Law — 2026 EB-1A & NIW Trends Report", "url": "https://manifestlaw.com/reports/eb1a-niw-trends"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/2023_green_card_front.jpg",
    "image_caption": "A 2023-series US permanent resident card, commonly known as a green card",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ── ARTICLE 2: The One Big Beautiful Bill — One Year On ────────────────

article2_body = """One year ago today, Donald Trump signed the One Big Beautiful Bill Act into law at a White House Fourth of July picnic. The sprawling legislative package rewrote tax policy, funded border operations, and buried inside its 1,116 pages a set of immigration fees that, taken together, represent the most expensive era in US visa history for Indian nationals.

The individual fees have been reported. What has not been tallied is the cumulative cost — what an Indian family on H-1B status now pays, start to finish, just to keep their American lives running.

## The New Fee Stack

Start with the headline charge. Trump's September 2025 executive proclamation imposed a **$100,000 fee** on new H-1B visa petitions — applicable when the worker enters the country or when a new H-1B-subject petition is filed from abroad. The fee is the subject of active litigation, with three federal circuits reaching different conclusions, virtually guaranteeing Supreme Court review. But until a court issues a nationwide injunction, the fee stands.

Layer on the One Big Beautiful Bill's provisions:

**$250 Visa Integrity Fee** — collected at the time of every nonimmigrant visa issuance at a US consulate. This applies per person: an H-1B holder, an H-4 spouse, and a child each pay separately. Family of three: $750.

**1 per cent remittance tax** — effective January 1, 2026, applied to cash transfers, money orders, and cashier's cheques sent abroad by non-citizens. The original House proposal was 5 per cent; fierce lobbying by the banking industry and pressure from Mexico brought it down. Transfers from US bank accounts via debit or credit card are exempt, but the typical H-1B worker sending money home to ageing parents in India via a hawala channel or Western Union pays the tax. India received $120 billion in remittances in 2023-24, with 28 per cent originating in the United States.

**$24 I-94 fee** — up from $6. Paid by every nonimmigrant who crosses a US land border. Indians transiting through Canada now pay four times the old price for a routine form.

**$13 ESTA fee** — up from $4. Less relevant to Indians (who require visas), but a signal of the direction.

**$100 annual surcharge** on pending asylum applications.

**$1,000 parole application fee** — up from $630.

## Add the Pre-Existing Costs

These new fees stack on top of a system that was already expensive:

The standard H-1B petition filing fee runs $1,710 (Form I-129 plus ACWIA training fee, fraud prevention fee, and public law fee). Premium processing adds $2,805. An H-4 dependent visa application is $185 plus the new $250 integrity fee. A green card application (Form I-485) costs $1,440 per person. And if the Adjustment of Status route is now "extraordinary" — as USCIS's May 2026 memo declares — the family must fly back to India for consular processing, adding $3,000 to $5,000 in travel and accommodation per trip.

The Executive Office for Immigration Review tripled its fees this year. An immigration appeal that once cost $110 now costs **$975**.

## What an Indian H-1B Family Actually Pays

Consider a senior software engineer in the Bay Area. She earns $180,000. Her employer files a new H-1B petition: $100,000 fee (which Crisil Intelligence estimates 30-70 per cent of IT companies will pass through to clients, and ultimately to workers through lower salary budgets). She gets the visa stamped at the US Consulate in Hyderabad: $190 MRV fee plus $250 integrity fee, times three for her family — $1,320. Her I-94 processing at the border: $72 for the family. She sends $1,000 a month to her parents in Pune: $120 a year in remittance tax.

Over a three-year H-1B term, before she even begins the green card process, the fee burden exceeds six figures.

## The Broader Signal

The Congressional Budget Office projects the Visa Integrity Fee alone will generate $28.9 billion over the 2025-2034 period. That is not a rounding error. It is a policy choice: immigration as a revenue centre.

For Indian IT services firms, the arithmetic is already reshaping staffing models. Between 2017 and 2025, H-1B headcount at TCS, Infosys, Wipro, and HCL Technologies nearly halved, from 34,507 to 17,997. The $100,000 fee accelerates a shift that was already under way — more offshore delivery, more nearshore capacity in Mexico and Canada, more local US hiring.

For individual professionals, the fees create a new decision framework. The total cost of maintaining an H-1B family's status in the United States — visas, petitions, consular trips, remittances, the eventual green card application — can now approach two to three years' worth of savings for a mid-career engineer. At some point, the calculation tips. India's booming GCC sector, paying competitive salaries in Bangalore and Hyderabad without the visa anxiety, starts to look less like a fallback and more like a rational choice.

That is not an accident. It is the design."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Bill That Made Immigration Expensive Turns One. Here Is What Indian Families Now Pay",
    "subheadline": "A year after the One Big Beautiful Bill Act, the cumulative cost of H-1B life in America — from the $100,000 petition fee to the $250 visa integrity charge to the 1 per cent remittance tax — adds up to something no one has tallied in full.",
    "slug": make_slug("one-big-beautiful-bill-anniversary-immigration-fees-indian-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B families now face the most expensive visa regime in US history — between the $100K petition fee, $250-per-person visa integrity charge, 1% remittance tax, $975 appeal fees, and mandatory consular trips, the total cost of maintaining legal status can approach six figures over a single H-1B term.",
    "tags": ["one-big-beautiful-bill", "visa-fees", "h1b", "remittance-tax", "visa-integrity-fee", "immigration-costs"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Lexology / Greenberg Traurig", "url": "https://www.lexology.com/library/detail.aspx?g=7c82c9f1-b6f0-4e5b-9073-8b764c0a1c5a"},
        {"name": "Greenspoon Marder LLP", "url": "https://www.gmlaw.com/insights/one-big-beautiful-bill-visas-will-cost-more/"},
        {"name": "ODI Think Change", "url": "https://odi.org/en/insights/why-taxing-remittances-will-harm-migrants-and-the-us-economy-trumps-big-beautiful-bill-act/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/donald-trumps-one-big-beautiful-bill-act-how-tax-on-remittances-are-set-to-impact-indians-in-us-11751555393088.html"},
        {"name": "VisaVerge — Crisil Analysis", "url": "https://www.visaverge.com/immigration-news/h-1b-surcharge-indian-it-firms-to-pass-30-70-to-clients/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A US passport beside hundred-dollar bills — the rising cost of maintaining visa status in America",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ── INSERT ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
