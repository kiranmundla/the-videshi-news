#!/usr/bin/env python3
"""Immigration writer — 2026-06-30 13:00 PT run. Two articles."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
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

# ── Article 1 ──────────────────────────────────────────────────────────

art1_body = """OpenAI filed 27 first-time H-1B visa approvals in the first half of fiscal year 2026. That already surpasses its full-year total for fiscal 2025, which was 21. Stripe filed 46, up from 23. Databricks is absorbing 89 H-1B transfers from other employers.

The $100,000 fee that President Trump imposed on new H-1B petitions last September was supposed to slow foreign hiring and steer well-paid technical jobs to American workers. Nine months in, a PitchBook analysis of federal employment data reveals something the administration did not intend: the fee has widened the gap between the best-funded AI labs and everyone else, splitting the tech labour market into two tiers — those who can pay and those who cannot.

## The haves and the have-nots

Among the top 30 US startups by valuation, H-1B hiring is actually *up*. Companies sitting on billions in venture capital treat the fee as a rounding error in the race for AI researchers. "There is a correlation between dry powder and hiring, and there is also a correlation between the haves and the have-nots," Jody Thelander, founder of compensation specialist J. Thelander Consulting, told PitchBook.

Outside that top tier, the story is the opposite. Maxine Bayley, a partner at Duane Morris focused on immigration law, says she has had *zero* clients pay the fee so far. Companies are "pumping the brakes on new applications" and shifting to H-1B transfers from other employers — which do not trigger the $100,000 charge.

## The transfer market boom

The real action is now in poaching. Instead of importing talent from abroad (and paying the fee), AI labs are hiring visa holders already working in the United States. The 60-day transfer window that H-1B employees have when they change jobs has become the de facto talent pipeline.

The numbers are striking. OpenAI took on 126 H-1B transfers in the first half of fiscal 2026. Databricks absorbed 89. Rippling brought in 54. Anthropic — Sam Altman's chief rival in the foundation-model race — had 48 incoming transfers but sponsored only one new H-1B petition, effectively replacing fresh recruitment with lateral hires.

For the individual Indian engineer, this means your value depends less on what you know and more on where you already sit. If you are at a funded lab, you are a tradeable asset. If you are at a mid-tier consultancy or a seed-stage startup that cannot afford $100,000 per head, the door may already be closing.

## What the courts say

Legal challenges are stacking up, but so far the fee stands. In December, a US District Court judge dismissed the US Chamber of Commerce's lawsuit, finding the administration acted within its authority. The Chamber has appealed. A second case, brought by 20 Democratic state attorneys general, argues the fee imposes an unconstitutional barrier on employers and remains pending.

Neither case will be resolved before the FY 2027 hiring cycle — which opened on April 1 and closes today, June 30 — is complete. For this season at least, the fee is law.

## What this means for Indian professionals

Roughly three in four H-1B holders are Indian nationals. The two-tier split hits the community hardest because Indian professionals are present at every level of the tech labour market: senior AI researchers at OpenAI, mid-level developers at enterprise software firms, and entry-level consultants at IT outsourcers.

For those already inside well-funded companies, the fee paradoxically increases their leverage — they are expensive to replace, and transfer offers from rival labs come with signing bonuses designed to make the move painless. For those outside the charmed circle, the picture is bleaker. Startups that once provided the first H-1B sponsorship to fresh graduates are now telling immigration lawyers to look for cap-exempt alternatives or defer hiring.

The $100,000 fee was meant to shrink the H-1B programme. What it may actually be doing is concentrating its benefits among the richest employers in the world — while everyone else, and the early-career Indian engineers who depend on them, is priced out."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Hired More H-1B Workers After the $100,000 Fee. Your Startup Cannot Afford To",
    "subheadline": "A PitchBook analysis of federal data shows the fee has split Silicon Valley into two tiers: AI labs that shrug off the cost and everyone else being priced out of foreign hiring.",
    "slug": make_slug("openai-h1b-100k-fee-two-tier-ai-talent-market"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three in four H-1B holders are Indian. The fee concentrates visa sponsorship among the richest AI labs while freezing out the startups and mid-size firms that gave many Indian engineers their first US job.",
    "tags": ["h1b", "uscis", "immigration", "ai", "silicon-valley", "openai", "fees"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "PitchBook", "url": "https://pitchbook.com/news/articles/trumps-100k-h-1b-fee-was-meant-to-slow-foreign-tech-hiring-it-may-have-sped-it-up"},
        {"name": "Lexology — H-1B Wage Weighted Rule", "url": "https://www.lexology.com/library/detail.aspx?g=0a1f8e9a-8b3c-4b2a-9e5c-1d7f3a2b4c6e"},
        {"name": "US Chamber of Commerce v. DHS (Court Ruling)", "url": "https://www.uschamber.com/immigration/h-1b-visa-fee"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6803523/pexels-photo-6803523.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Tech professionals collaborating in a modern office environment",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ── Article 2 ──────────────────────────────────────────────────────────

art2_body = """Since January, at least a dozen Republican lawmakers have backed four separate bills that seek to restrict, suspend, or eliminate the H-1B visa programme entirely. None has passed committee. None has the votes to become law this term. But taken together, they represent the most sustained legislative assault on employer-sponsored work visas in the programme's nearly four-decade history — and every one of them is aimed, whether by design or arithmetic, at Indian professionals.

Here is what each bill would actually do if enacted.

## 1. The End H-1B Now Act — Marjorie Taylor Greene (January 2026)

The bluntest instrument. Greene's bill would phase out the H-1B programme over roughly a decade, cutting the annual cap each year until it reaches zero. A narrow exemption would preserve up to 10,000 visas per year for medical professionals — physicians, surgeons, and nurses. Everyone else — engineers, software developers, data scientists — would lose access.

**What it means for you:** If you are an Indian tech worker on an H-1B, this bill treats your job category as expendable. The medical carve-out would help Indian doctors in underserved rural areas, but the 600,000-plus Indian IT professionals in the pipeline would lose their primary pathway to working in the United States.

## 2. The EXILE Act — Greg Steube (February 2026)

Florida Republican Steube's bill is even more aggressive. The Ending Exploitative Imported Labor Exemptions Act would terminate the H-1B programme entirely by 2027 — no phase-out, no medical exemption. One and a half pages of legislation to end a programme that employs more than 730,000 workers and their 550,000 dependents.

**What it means for you:** Immediate disruption. If enacted, H-1B holders whose three-year terms expire after 2027 would have no mechanism to renew. Employers could not file new petitions. The visa extensions that keep hundreds of thousands of Indians in the green card queue would vanish.

## 3. The End H-1B Visa Abuse Act — Eli Crane (April 2026)

Crane's bill, which attracted seven Republican co-sponsors, takes a slightly different tack. Rather than eliminating the programme outright, it would impose a three-year moratorium on new H-1B visas, slash the annual cap from 85,000 to 25,000, and set a salary floor of $200,000 per year. It would also bar H-1B holders from bringing spouses and children to the United States.

**What it means for you:** The salary floor alone would disqualify the majority of current H-1B positions. According to USCIS data, the median H-1B salary in fiscal 2025 was approximately $118,000. A $200,000 threshold would restrict the visa to senior engineers at the largest firms — precisely the group that is already best positioned under the wage-weighted lottery. The family ban would force thousands of H-4 spouses and children to leave, or compel workers to choose between their career and their family.

## 4. The American White-Collar Worker Jobs Act — Chip Roy (June 2026)

The most detailed of the four, Roy's bill introduced seven structural changes. It would cut the maximum H-1B duration from six years to two, require applicants to prove they intend to return home (eliminating "dual intent" — the legal principle that lets H-1B holders pursue green cards simultaneously), repeal the H-1B extensions that keep green card applicants employed while they wait in the EB-2 and EB-3 backlogs, and eliminate Optional Practical Training, which lets F-1 students work for up to three years after graduation.

The bill also caps each employer's nonimmigrant workforce at 5 per cent of its US headcount — a provision aimed squarely at Indian IT outsourcers, many of which have historically relied on H-1B employees for a much larger share of their American operations.

It adds a legal weapon: any US worker displaced by a nonimmigrant would gain the right to sue the employer in federal court.

**What it means for you:** The dual-intent repeal is the most consequential clause for Indians. Right now, roughly 700,000 Indian nationals are waiting in the EB-2 and EB-3 green card backlogs, many for decades. They can work while they wait because their H-1B status is extended indefinitely as long as their green card case is pending. Remove that extension, and every one of those workers faces a two-year countdown to departure — backlog or no backlog.

## Why none of this is law yet — and why it matters anyway

All four bills face an uphill path. The tech industry, the US Chamber of Commerce, and a coalition of universities that rely on OPT students will lobby against them. Many Republican donors, particularly in the tech sector, oppose gutting H-1B. And legislative calendars in an election year are unpredictable.

But the direction is unmistakable. In 2024, no bill in Congress proposed eliminating the H-1B. In 2026, four do. The Overton window for what is politically possible has shifted.

Indian IT firms are reading the room. TCS chief executive K. Krithivasan said the company now deploys "fewer people than the number of approvals each year" and has been consistently reducing its dependency on visa-based talent. Cognizant CEO Ravi Kumar told analysts the company has "significantly reduced the dependency on visas, while increasing local hiring."

For the individual H-1B holder, none of these bills changes anything today. But each one signals what tomorrow's executive order or regulatory change might look like. The fee is already $100,000. The lottery already favours higher wages. Consular stamping appointments in India are booked into 2027. And now, four separate members of Congress want to end the programme altogether.

The legislative math may save the H-1B for another year. The political trajectory suggests the programme you entered is not the programme you will retire from."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Bills in Congress Want to End the H-1B. Here Is What Each Would Do to You",
    "subheadline": "From a ten-year phase-out to immediate termination, Republican lawmakers have introduced an unprecedented wave of legislation targeting the visa that employs three-quarters of a million workers — most of them Indian.",
    "slug": make_slug("four-bills-end-h1b-greene-steube-crane-roy-guide"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Every one of the four bills disproportionately affects Indian professionals, who make up 75% of H-1B holders. The dual-intent repeal in Roy's bill alone would upend 700,000 Indians in the green card backlog.",
    "tags": ["h1b", "congress", "immigration", "legislation", "green-card", "opt"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/companies/is-2026-the-death-knell-for-h-1b-visa-holders-11780829488222.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-seeks-to-end-green-card-pathway/article71068304.ece"},
        {"name": "PitchBook — H-1B Fee Analysis", "url": "https://pitchbook.com/news/articles/trumps-100k-h-1b-fee-was-meant-to-slow-foreign-tech-hiring-it-may-have-sped-it-up"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Capitol_Building_Full_View.jpg/1280px-Capitol_Building_Full_View.jpg",
    "image_caption": "The United States Capitol, where four bills targeting the H-1B programme have been introduced in 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}

# ── Insert ──────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
