#!/usr/bin/env python3
"""Immigration writer — 2 July 2026, 17:00 PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ──────────────────────────────────────────────────────────

article1_body = """\
The filing window for FY 2027 H-1B cap-subject petitions closed on 30 June. It was the first season run under a wage-weighted lottery, and the numbers already look nothing like the system Indian applicants have known for a decade.

Under the old random draw, every registration had an equal shot. Under the new rule, which took effect on 27 February 2026, each registration is assigned one to four lottery entries based on the Department of Labor's prevailing-wage tier for the job. A Level IV position — the highest-paid quartile — gets four entries. A Level I position gets one. The math is blunt: a senior data scientist in San Francisco is four times more likely to be drawn than a junior QA analyst in a suburb of Dallas.

## Selection rates doubled

The shift was visible immediately. Immigration firm Fragomen reported average selection rates above 50 per cent this season, with some employers seeing 65 per cent or higher. In 2024, under the random lottery, the rate was 26 per cent. In 2025, it climbed to 35 per cent — partly because USCIS's new beneficiary-centric system stamped out the duplicate-registration fraud that had inflated the pool for years.

The jump to 50-plus per cent does not mean the visa got easier to obtain. It means far fewer people entered the draw.

## Why registrations plummeted

Three forces thinned the field. First, the $100,000 fee that President Trump imposed on new H-1B petitions in September 2025 changed the arithmetic for cost-sensitive employers. Indian IT outsourcers — Infosys, Wipro, TCS, Cognizant — built their American staffing model on high-volume, moderate-wage placements. At a hundred thousand dollars a head, that model does not pencil out for every role.

Second, the weighted system itself created a deterrent. If a company knows its Level I and Level II candidates have slim odds, it registers fewer of them. Fragomen noted that employers "did not register beneficiaries who are assuming lower-salaried, entry-level positions at the same rate as in previous years."

Third, broader economic headwinds — layoffs across Meta, Amazon, Oracle, and dozens of mid-tier firms — reduced hiring activity outright. Fewer open roles means fewer registrations.

## What this means for Indians

Indians account for more than 70 per cent of approved H-1B petitions in a typical year. The weighted system does not penalise nationality directly, but it penalises the wage profile that has historically characterised a large share of India-born petitions. Entry-level and mid-level IT services positions, the bread and butter of Indian outsourcers, now compete at a structural disadvantage.

Higher-paid Indian applicants — those at large tech companies, biotech firms, financial institutions, and research universities — are likely better off under this system. Their wages tend to sit at Level III or IV, giving them three or four lottery entries.

The divide is sharpening: a senior machine-learning engineer at Google has never had better odds. A systems analyst at a mid-tier consultancy has never had worse.

## What happens next

Petitions filed before the 30 June deadline will now be adjudicated by USCIS. If approved, employment under FY 2027 H-1B status can begin on 1 October 2026. USCIS has not announced whether it will conduct a second lottery this year — it ran two in 2023 and 2024, but only one in 2025. Given the elevated selection rates, a second round seems unlikely.

Meanwhile, the new Form I-129 (edition 02/27/26) is mandatory for all FY 2027 cap petitions. Any petition filed on the old form will be rejected. Employers also face the $100,000 fee for petitions involving consular notification — a category that disproportionately affects Indian workers renewing from abroad.

For the thousands of Indians who were not selected or whose employers chose not to register them at all, the fallback options are familiar and unsatisfying: wait for next year's lottery, pivot to an O-1 or L-1, pursue an employer-sponsored EB-2 or EB-3 green card (with its decade-plus backlog for India), or explore the self-petition routes — EB-1A and NIW — that are drawing record applications and, increasingly, record denials.

The first weighted lottery delivered exactly what it promised: more visas for higher-paid workers, fewer for everyone else. Whether that constitutes reform or merely redistribution depends on which side of the wage line you stand.\
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-1B Filing Window Just Closed. The First Weighted Lottery Changed Everything",
    "subheadline": "Selection rates doubled to over 50 per cent — but only because far fewer people entered the draw. Entry-level Indian IT workers took the biggest hit.",
    "slug": make_slug("h1b-fy2027-weighted-lottery-filing-deadline-closes"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The new wage-weighted H-1B lottery structurally disadvantages the entry-level and mid-level IT services positions that have historically been the primary pathway for Indian workers to reach the United States.",
    "tags": ["h1b", "uscis", "weighted-lottery", "fy2027", "immigration", "visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS — FY 2027 H-1B Registration Selection Completed", "url": "https://www.uscis.gov/newsroom/alerts/fy-2027-h-1b-initial-registration-selection-process-completed"},
        {"name": "Fragomen — H-1B Cap Lottery Results FY 2027", "url": "https://www.fragomen.com/insights/h-1b-cap-lottery-results-fy-2027-what-employers-should-do-now.html"},
        {"name": "SHRM — USCIS Completes H-1B Lottery", "url": "https://www.shrm.org/topics-tools/news/hr-news/uscis-completes-h-1b-lottery"},
        {"name": "Lexology — USCIS Finalizes Wage Weighted H-1B Cap Selection Rule", "url": "https://www.lexology.com/library/detail.aspx?g=uscis-finalizes-wage-weighted-h1b-cap-selection-rule"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in New York City",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────

article2_body = """\
By most accounts, around 15,000 Indian technology professionals left the United States for good in 2025. LinkedIn data, cited by Bloomberg, shows a 40 per cent year-on-year increase in Indian tech workers relocating back to India. The numbers for 2026 are tracking higher.

This is not a protest march. There is no manifesto. It is an actuarial calculation made by thousands of individuals who ran the numbers on their American lives and concluded the expected value had turned negative.

## The push

Start with the layoffs. More than 110,000 technology workers lost their jobs in the United States in 2025, and the cuts have continued into 2026. Meta, Amazon, Oracle, LinkedIn — the companies that once anchored the H-1B ecosystem — are restructuring around artificial intelligence, shedding roles they deem redundant. For an American citizen, a layoff is a setback. For an H-1B holder, it is a 60-day countdown. Find a new sponsor within two months or leave the country.

The 60-day grace period assumes a functioning job market. What it encounters instead is a market where employers are slower to hire, more reluctant to sponsor visas, and increasingly conscious of the $100,000 fee now attached to new H-1B petitions. Recruiters report that some companies have quietly removed "will sponsor" from job listings altogether.

Stack the policy changes on top. The July 2026 visa bulletin marked EB-2 India as "unavailable" — no employment-based second-preference green cards will be issued to Indian nationals until the new fiscal year begins in October. The adjustment-of-status pathway, which allowed green card applicants to remain in the US while their cases were processed, has been restricted to "extraordinary circumstances." The naturalization fee jumped 75 per cent. Immigration court appeal fees went from $110 to $975.

And then there is the social-media vetting. Since December 2025, US consulates in India have required an online-presence review for every H-1B and H-4 visa applicant. The policy created what immigration lawyers call "operational constraints" — a euphemism for a backlog that has pushed interview appointments out by three to six months. Workers who flew to India for a routine visa stamp found themselves stranded, unable to return to their jobs.

## The pull

India, meanwhile, is hiring. Meta, Amazon, Microsoft, Apple, Google, and Netflix collectively added tens of thousands of engineering and operations roles in India in 2025, expanding their global capability centres in Bengaluru, Hyderabad, and Gurugram. The salaries are lower than in the US, but when you factor in the cost of immigration uncertainty — the legal fees, the years in green-card limbo, the risk of an overnight layoff resetting your life — the gap narrows.

The Indian government has noticed. Programmes like Bharat-Talent and Bharat-Return offer fast-track visas and tax incentives to returning non-resident professionals. India's startup ecosystem, which crossed $100 billion in combined valuation in 2025, provides a landing pad for founders who might have once built their companies in Silicon Valley.

## The counter-argument

Not everyone is leaving. Vaibhav Domkundwar, a San Francisco-based venture capitalist and founder of Better Capital, has argued that the "reverse brain drain" narrative is overblown. Most H-1B holders have mortgages, children in American schools, and spouses whose careers are rooted in the US. "Moving back to India is non-trivial," he wrote on LinkedIn. "And it's definitely not about better opportunities."

He is probably right about the majority. But 15,000 is not the majority. It is the leading edge — the people whose calculation tipped first, whose green-card wait was longest, whose layoff came at the worst moment. The question is whether the policy environment stabilises before the leading edge becomes a wave.

## The competing destinations

India is not the only beneficiary. Canada, Germany, the UAE, Singapore, and Australia have all expanded skilled-worker visa programmes that are explicitly designed to attract the talent the US is making uncomfortable. China launched its own version of the H-1B — the K visa — last year, targeting Indian engineers specifically. The global talent market has not been this competitive since the post-2008 scramble.

For the Indian diaspora in America, the picture is unsettling. The system that brought them here — the H-1B-to-green-card pipeline that powered decades of Indian success in Silicon Valley, Wall Street, and academic medicine — is not broken in the dramatic, overnight sense. It is being disassembled, one policy memo and one fee increase at a time, by an administration that views the programme as a labour market problem rather than an innovation engine.

Fifteen thousand left. The rest are watching.\
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Fifteen Thousand Indian Engineers Left America This Year. The Rest Are Watching",
    "subheadline": "Layoffs, a frozen green-card queue, and an immigration system that punishes every misstep are pushing India's best out of the US. The countries competing for them are ready.",
    "slug": make_slug("indian-tech-reverse-migration-15000-leaving-us"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The reverse migration of Indian tech professionals directly affects the NRI community — these are colleagues, neighbours, and family members whose decade-long American lives are being upended by a convergence of layoffs, visa restrictions, and a green-card backlog that offers no resolution.",
    "tags": ["h1b", "reverse-migration", "brain-drain", "layoffs", "green-card", "immigration", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Nearshore Americas — Indian Tech Workers Return Home", "url": "https://nearshoreamericas.com/h1b-impact-many-indian-tech-workers-return-home/"},
        {"name": "Bloomberg / LinkedIn Data — 40% Increase in Indian Professionals Returning", "url": "https://www.bloomberg.com/news/articles/2025-india-tech-workers-returning"},
        {"name": "Xpheno Staffing Data — 15,000 Professional Returnees", "url": "https://xpheno.com/"},
        {"name": "Medium — The Great Reverse Migration 2026", "url": "https://medium.com/origins/the-great-reverse-migration-2026"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1381415/pexels-photo-1381415.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A traveller waits with luggage at an airport departure lounge",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ── Insert ──────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
