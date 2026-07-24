#!/usr/bin/env python3
"""Immigration writer — 2026-06-07 04:00 UTC run."""

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

articles = [
    # ── Article 1: Indian Deportations ──
    {
        "id": str(uuid.uuid4()),
        "headline": "One Thousand and Counting — India Walks a Deportation Tightrope With Washington",
        "subheadline": "The MEA says 1,076 Indian nationals have been deported from the US in 2026 so far. Behind the number is a delicate bilateral negotiation that could shape the future of legal migration for millions.",
        "slug": make_slug("india-deportation-tightrope-mea-bilateral-1076"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Every Indian professional in the US lives in a system where enforcement against undocumented migrants and restrictions on legal workers are converging. The MEA's diplomacy on deportations directly affects how Washington views the entire Indian migration pipeline — from irregular border crossers to H-1B holders.",
        "tags": ["deportation", "mea", "bilateral", "ice", "india-us"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/world/how-trumps-immigration-crackdown-is-affecting-indians-1-076-deportations-in-2026-11780713075195.html"},
            {"name": "Ministry of External Affairs — India", "url": "https://www.mea.gov.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7104991/pexels-photo-7104991.jpeg",
        "image_caption": "US international border port of entry on a clear day",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The number arrived without drama during a routine MEA press briefing on Friday: 1,076 Indian nationals deported from the United States in 2026, through early June.

It is a smaller number than you might expect. In all of 2025, the figure was 3,567. Pace-wise, 2026 is tracking slightly below last year. But numbers stripped of context are just arithmetic. What matters is what India is doing with them — and what it is trying to protect while accepting them back.

## The Diplomatic Calculation

MEA spokesperson Randhir Jaiswal framed India's position with deliberate neutrality: "We are in continuous dialogue with the US regarding migration and mobility to ensure that legal migration is facilitated while illegal migration is effectively curbed."

The sentence does a lot of work. It simultaneously concedes that India has a problem with irregular migration to the US, signals willingness to cooperate on enforcement, and draws a bright line between those cases and the hundreds of thousands of Indians who hold valid H-1B, L-1, F-1, and other legal status.

This is the tightrope. India cannot refuse to take back its nationals without poisoning the broader relationship — a lesson Colombia learned the hard way in early 2025 when a brief refusal triggered immediate trade reprisals. But India also cannot appear so eager to cooperate that it loses leverage on the issues that matter far more to its diaspora: H-1B fees, green card backlogs, and OPT protections.

## Who Gets Deported

The deportation figures encompass individuals across a wide spectrum: people with criminal records, overstayed visas, and undocumented border crossers. ICE's own public postings offer a window into the enforcement priorities. In a recent case, ICE Los Angeles arrested a 26-year-old Indian national whose criminal history included vehicle theft, grand theft, trespassing, and vandalism.

These are not the cases that keep H-1B holders awake at night. But they exist in the same political atmosphere. When a congressman argues for eliminating the H-1B-to-green-card pathway or a state attorney general launches an investigation into "ghost offices," the enforcement narrative against undocumented Indians provides the emotional backdrop.

India's verification protocols are structured but slow. When US authorities refer someone claiming Indian citizenship, the MEA conducts independent background checks and nationality confirmation before accepting responsibility. Jaiswal described this process during a September 2025 briefing: "Whenever there is a person who does not possess a legal status in any country, and he or she is referred to us with documents, and if there are claims that he or she is an Indian national, we do the background check, confirm the nationality and then we are in a position to take them back."

## The Shackles Question

India's cooperation has not been unconditional. External Affairs Minister S. Jaishankar addressed the Rajya Sabha on the treatment of deportees, confirming that India "strongly registered its concerns with the US authorities on the treatment of deportees, particularly with respect to use of shackles, especially on women and children."

The diplomatic language masks genuine friction. Earlier deportation flights drew opposition protests in Parliament, with MPs objecting to the perceived indignity of restraints on Indian nationals. Jaishankar noted that ICE's standard operating procedures for deportation by aircraft, effective since 2012, provide for the use of restraints, but added that women and children are not restrained. The Ministry has not received complaints about treatment on any flight after February 5, 2025.

## What This Means for Indian Americans

The deportation figures, while concerning in human terms, represent a tiny fraction of the approximately 4.8 million Indian-origin people in the United States. But the diplomatic dynamics they create are anything but marginal.

India's willingness to cooperate on deportations is being quietly leveraged in bilateral discussions on migration frameworks. New Delhi is pushing for expanded legal pathways — more visa appointment slots at Indian consulates, smoother H-1B stamping processes, and recognition of India's disproportionate contribution to the US skilled workforce.

The $70 billion enforcement bill that passed the US Senate this week will only accelerate deportation operations. For India, the challenge is ensuring that cooperation on enforcement buys goodwill on facilitation — not just more deportation flights.

The 1,076 is a number India can live with. The question is whether Washington remembers the other number: the hundreds of thousands of Indian professionals who followed every rule, paid every fee, and are still waiting for a system that works."""
    },

    # ── Article 2: EB-5 Investor Visa ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Eight Hundred Thousand Dollars and a Green Card — India's Wealthy Are Bypassing the H-1B Queue Entirely",
        "subheadline": "With H-1B fees at $100,000, EB-2 India backlogs stretching past a decade, and NIW denial rates climbing, the EB-5 investor visa has become the most reliable path to permanent residency for Indian families who can afford it.",
        "slug": make_slug("eb5-investor-visa-india-wealthy-bypass-h1b-queue"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian professionals stuck in the EB-2/EB-3 backlog or priced out by the $100,000 H-1B fee, the EB-5 represents a completely different calculus: trade money for certainty. The rural set-aside category currently has zero priority date backlog for Indian investors — the only US green card path where that is true.",
        "tags": ["eb5", "investor-visa", "green-card", "india", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NRI Globe", "url": "https://nriglobe.com/news/eb-5-investor-visa-2026-complete-guide-indian-investors/"},
            {"name": "US Immigration Advisor", "url": "https://usimmigrationadvisor.com/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg",
        "image_caption": "US passport with hundred-dollar bills and financial documents",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The math has changed. Not gradually, the way immigration policy usually shifts, but with the abruptness of a system that has priced out its own users.

An H-1B petition now costs $100,000 in proclamation fees alone. The EB-2 India backlog stretches past a decade. NIW denial rates have, by some measures, surpassed EB-1A. And the Chip Roy bill introduced last week would eliminate the H-1B-to-green-card pathway entirely.

Against this backdrop, a different number has started making sense to a specific subset of Indian families: $800,000. That is the minimum investment for an EB-5 investor visa in a Targeted Employment Area — and for those who can write the cheque, it has become the most predictable path to a US green card in 2026.

## The Rural Set-Aside: Zero Backlog

The EB-5 program was reformed in 2022 under the Reform and Integrity Act, which created three set-aside categories with reserved visa allocations: Rural (20% of annual EB-5 visas), High-Unemployment Areas (10%), and Infrastructure (2%).

For Indian investors, the Rural set-aside is transformative. According to the June 2026 US Visa Bulletin, all three set-aside categories remain current for India. In plain English: an Indian national filing under the Rural category today faces no priority date wait. The I-526E petition can be processed in 12-18 months, with a conditional green card following within 2-3 years of the initial investment.

Compare that to the EB-2 India queue, where the effective wait exceeds 10 years — or the H-1B lottery, where selection rates sit around 35% and the $100,000 fee has priced out most individual applicants and mid-tier employers.

## Who Is Buying In

The typical Indian EB-5 investor in 2026 does not fit the Silicon Valley H-1B stereotype. The profile, according to immigration consultancies in Mumbai and Bangalore that specialise in EB-5 deal structuring: net worth above $5 million, age 40-60, usually a successful business owner or senior executive at an Indian company.

The motivation is rarely about the investor themselves. It is about their children. Securing a green card before a 20-year-old ages out of dependent eligibility eliminates the need for an F-1 student visa — with all its attendant uncertainties about OPT, H-1B lottery odds, and the increasingly hostile regulatory environment for international students.

Family offices in Mumbai and Bangalore have emerged as intermediaries, specialising in matching Indian investors with Regional Center projects in rural Iowa, Nebraska, and Kansas. These agricultural and food-processing ventures qualify under the Rural set-aside and offer the double advantage of zero backlog and lower investment thresholds.

## The Real Cost

The $800,000 investment is the headline number. The all-in cost is closer to $1 million.

Legal fees run $30,000-$80,000. Regional Center administrative fees add $50,000-$80,000. USCIS filing fees total $12,600 ($11,160 for the I-526E plus $1,440 for biometrics). And the investment itself carries genuine risk — if the Regional Center project fails to create the required 10 full-time American jobs, both the capital and the green card are at stake.

Source-of-funds documentation is the single biggest obstacle for Indian applicants. USCIS requires detailed tracing of investment funds through the Indian banking system, often demanding 10-15 years of financial records, business sale documents, and tax returns. The Reserve Bank of India's Liberalised Remittance Scheme (LRS) caps outward remittances at $250,000 per financial year per individual, and Tax Collected at Source on LRS transactions adds to the cash-flow complexity.

## A Shrinking Window

The State Department has already warned that EB-5 unreserved visas for India may retrogress or become unavailable later in the fiscal year. The Rural set-aside's zero-backlog status is unprecedented for Indian-born applicants — and it will not last forever.

As more Indian investors discover the category, the priority date will retrogress. Immigration attorneys advising Indian clients are uniformly delivering the same message: act now, while the path remains clear.

The irony is not lost on anyone tracking the broader immigration landscape. The same system that charges a 26-year-old software engineer $100,000 for an H-1B petition and makes them wait a decade for a green card offers a parallel track where $800,000 and the right paperwork can deliver permanent residency in under three years. It is not a system designed for fairness. It is a system designed for those who can afford to navigate it.

For the estimated 1.2 million Indians in the employment-based green card queue, the EB-5 is not an option. For the few thousand who can afford it, it is increasingly the only option that works."""
    },

    # ── Article 3: Texas H-1B Crackdown ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Lone Star Freeze — Texas Writes Its Own H-1B Rules, and the Legal Questions Are Piling Up",
        "subheadline": "Governor Abbott froze state H-1B petitions, AG Paxton sent investigators to 30 businesses, and Ted Cruz questioned why school districts need foreign workers. Indian professionals in Texas are caught between a state crackdown and federal law.",
        "slug": make_slug("texas-lone-star-h1b-freeze-abbott-paxton-crackdown"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Texas is home to one of the largest concentrations of Indian H-1B workers in the country. The state-level crackdown directly threatens Indians working at public universities, state agencies, and companies that do business with the state — and could become a model for other states.",
        "tags": ["texas", "h1b", "abbott", "paxton", "crackdown", "state-level"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1742682/texas-holdem-governors-h-1b-pause-reveals-several-hole-cards"},
            {"name": "New York Post", "url": "https://nypost.com/"},
            {"name": "KPRC Houston", "url": "https://www.click2houston.com/"},
            {"name": "Gulte", "url": "https://www.gulte.com/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/84/2025_Texas_State_Capitol_02.jpg",
        "image_caption": "The Texas State Capitol building in Austin",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Immigration law in the United States is federal. This is constitutional bedrock, not a policy preference. Congress sets the rules, USCIS processes the petitions, and the State Department stamps the visas. States do not get to run their own immigration systems.

Texas has decided to test that proposition.

## The Governor's Freeze

On January 27, 2026, Governor Greg Abbott issued a directive to all state agencies and public universities: stop filing new H-1B visa petitions immediately. No grace period. No comment window. No prior notice to the thousands of foreign workers — the majority of them Indian — employed at institutions like Texas A&M, UT Austin, and the Texas Health and Human Services Commission.

The freeze runs through May 31, 2027, covering the entire upcoming Texas legislative session. Any new H-1B petition requires written authorisation from the Texas Workforce Commission, which has yet to publish the standards it will use to grant exceptions.

Abbott's letter framed the action in populist terms: "State government must lead by example and ensure that employment opportunities — particularly those funded with taxpayer dollars — are filled by Texans first."

The letter also demanded detailed reports from every affected institution: how many H-1B petitions filed in 2025, how many workers currently sponsored, their countries of origin, job classifications, visa expiration dates, and documentation showing efforts to hire qualified Texans before turning to foreign workers.

## The Attorney General's Investigators

Attorney General Ken Paxton escalated the pressure in parallel. His office issued Civil Investigative Demands — formal investigative subpoenas — to nearly 30 North Texas businesses suspected of H-1B fraud or abuse.

The investigation zeroed in on what Paxton's office called "ghost offices": businesses that listed a single-family home as their office address while claiming a separate, unfinished commercial building as their official worksite. The implication is that these companies were filing H-1B petitions for positions that did not exist at legitimate worksites — a form of visa fraud that has long plagued the staffing industry.

Then came Ted Cruz. The senator from Texas, never one to miss a populist talking point, publicly questioned why the Dallas Independent School District had spent roughly $2.5 million on H-1B visa legal services between 2020 and late September 2025. "I can't imagine any reason why Dallas ISD should need any H-1Bs," Cruz said.

The statement ignored the well-documented shortage of specialised teachers — in bilingual education, special education, and STEM subjects — that drives school districts across the country to sponsor foreign workers. Abbott's freeze, notably, does not apply to K-12 school districts, which fall outside the scope of state agencies with gubernatorially appointed heads.

## The Legal Minefield

Texas's actions create what immigration attorneys describe as a direct collision with federal law. The H-1B programme is entirely federal. The petition is filed with USCIS, the Labour Condition Application is certified by the US Department of Labor, and the visa is issued by the State Department. There is no state role in the process beyond the employer's own decision to participate.

Federal anti-discrimination law compounds the problem. Title VII of the Civil Rights Act prohibits discriminatory job advertisements expressing a preference for workers of a particular citizenship status. The Department of Justice's Immigrant and Employee Rights section protects all work-authorised individuals from citizenship or national origin discrimination.

Abbott's directive to prioritise "Texans" raises immediate questions: Who qualifies? Is a Texan defined by birth, residence, or citizenship? Can an asylee living in Houston apply? What about a US citizen who resides in California? The legal analysis, published by the immigration law firm behind the Mondaq report, concludes bluntly: "No" — affected Texas employers cannot legally prioritise "Texans first" in their hiring practices without violating federal law.

## The Indian Worker in the Middle

None of this is theoretical for the estimated 32,000 H-1B workers who received new approvals in the Dallas metro area alone during the Biden administration — the majority of them Indian nationals. Bloomberg's investigation found that Collin County's Indian-born population averaged more than 116,000 residents annually in the five years through 2024, up sharply from 70,000 in the preceding period.

The state-level crackdown has compounded the federal-level squeeze. Between the $100,000 H-1B proclamation fee, Project Firewall investigations, the wage-weighted lottery, and now a governor's freeze, Indian professionals in Texas face a hostile environment at every level of government.

The housing market tells the story in dollars. Home prices in the Collin County suburbs north of Dallas dropped nearly 9% year-over-year in February 2026. A luxury builder who once counted South Asian buyers as 70% of sales now reports that share below 30%, with more than 100 high-end homes sitting unsold.

## The Precedent Question

Texas has historically been the testing ground for state-level immigration actions. SB 4, passed in 2023, created a state-level deportation system — an aggressive challenge to federal preemption that remains under consideration by the Fifth Circuit.

The H-1B freeze is less dramatic but potentially more consequential. If Texas successfully establishes the principle that a state can dictate whether its agencies participate in federal visa programmes, other states with similar political appetites — Florida, Ohio, Iowa — will follow.

For Indian workers, the message from Austin is unambiguous: even following every federal rule is not enough when the state house is writing its own."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
