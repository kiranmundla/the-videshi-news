#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Hired Six Times More Foreign Workers This Quarter — Google Cut Back by Two-Thirds",
        "subheadline": "Federal labour data reveals a stark divide in H-1B hiring: AI pure-plays are doubling down on foreign talent while legacy tech giants quietly retreat from the visa programme altogether.",
        "slug": make_slug("anthropic-openai-nvidia-h1b-surge-google-meta-retreat"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian engineers form the backbone of H-1B hiring at both AI startups and legacy tech firms. As the programme splits into two tiers — elite AI shops willing to pay any price and large employers pulling back — the career calculus for hundreds of thousands of Indian tech workers changes overnight.",
        "tags": ["h1b", "anthropic", "openai", "nvidia", "google", "tech-hiring", "ai-talent"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Business Insider (via EuropeSays)", "url": "https://www.europesays.com/people/104974/"},
            {"name": "Bhasha Times", "url": "https://bhashatimes.com"},
            {"name": "Global News Bulletin", "url": "https://globalnewsbulletin.in"},
            {"name": "USCIS FY2027 Registration Data", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-workers/h-1b-specialty-occupations/h-1b-electronic-registration-process"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6805161/pexels-photo-6805161.jpeg",
        "image_caption": "Tech professionals collaborating in a modern office workspace",
        "image_attribution": "Pexels",
        "body": """The H-1B visa programme has always been a single pipeline — one set of rules, one lottery, one fee schedule. But federal labour data from the second quarter of fiscal year 2026 tells a different story. The programme is splitting into two distinct economies, and Indian engineers are caught in the middle.

## The AI Shops Are Hiring Like It's 2021

Anthropic, the maker of Claude, filed 59 certified H-1B applications in Q2 2026, up from just 10 in the same quarter a year earlier — a 490 per cent increase. OpenAI filed 63, more than tripling its Q2 2025 count of 20. Nvidia, already the largest filer among the group, pushed its tally from 641 to 765.

These are not lottery registrations. They are Department of Labor certifications — applications that have been reviewed to confirm the prospective worker will be paid fairly and that existing employees will not be undercut. They include both new hires and extensions for current staff.

The numbers are small in absolute terms, but the trajectory is unmistakable. The companies building foundation models and designing the chips that run them are not merely tolerating the H-1B system's rising costs. They are leaning into it.

"The $100,000 H-1B visa fee represents a rounding error against the cost of not landing the right researcher," Raghu Shivakumar, a recruiter with Nexocean, told Business Insider.

## Big Tech Is Walking Away

The contrast could scarcely be sharper. Google saw a 64 per cent decline in certified H-1B applications over the same period, a reflection of its ongoing programme of rolling, team-specific layoffs. Meta, Microsoft, and Amazon all reported fewer filings compared with the prior year.

The reasons are layered. Mass layoffs across the tech sector — over 130,000 jobs lost in 2026 alone — have reduced headcount across the board. But something structural is happening too. Large firms are restructuring around what Meta internally calls "pods": smaller, more specialised teams that need fewer but more precisely skilled workers.

Several recruiters told Business Insider that some of these companies are now more comfortable standing up entire teams overseas — in London, Bangalore, Toronto — rather than navigating an H-1B system that has become both more expensive and less predictable.

## The Numbers Behind the Squeeze

The macro picture reinforces the divide. USCIS received just 211,600 properly submitted H-1B registrations for the fiscal year 2027 allocation, down from 343,981 the year before — a drop of 38.5 per cent. That continues a slide from the 2024 peak of nearly 781,000 registrations, when duplicate filings inflated the count.

Two policy shifts explain the decline. First, the beneficiary-centric selection process — introduced in 2024 — eliminated the advantage of filing multiple registrations for the same worker. Second, the new wage-based weighting system gives higher-paid applicants better odds in the lottery, effectively penalising entry-level roles. A Level IV wage earner gets four times the lottery entries of a Level I worker.

For AI companies offering researchers salaries of $300,000 to $690,000 — as Anthropic's own filings show — the new system is almost a tailored advantage. For Indian IT services firms placing workers at Level I or Level II wages, it is a structural headwind.

## What This Means for Indian Workers

Indians receive more than 70 per cent of all approved H-1B petitions annually. The programme's bifurcation creates two very different realities.

For the relatively small number of Indian AI researchers and infrastructure engineers with the right skills — experience in large language models, reinforcement learning, chip architecture — the market has never been hotter. Companies will pay almost anything, absorb any fee, and file regardless of policy uncertainty.

For the much larger cohort of Indian software engineers, QA testers, and IT consultants who have historically entered through the H-1B system, the walls are closing in. Fewer employers are filing. The lottery odds favour higher wages. And the $100,000 fee — currently struck down by a federal judge but facing appeal — hangs like a sword over the programme's economics.

Justin Parsons, a partner at Berry Appleman & Leiden, one of the most influential immigration law firms in the country, told Business Insider that some employers simply sat out this year's lottery while they waited to see how the new rules would play out.

That wait-and-see posture may be the most dangerous signal of all. When companies stop filing, the pipeline of Indian workers entering the United States does not merely slow — it begins to redirect. To Canada. To the UK. To Singapore. And once redirected, it rarely comes back."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every EB-2 Visa for India Is Gone — and the Wait Until October Just Got Longer",
        "subheadline": "The State Department has confirmed that India's EB-2 allocation for fiscal year 2026 is exhausted. For tens of thousands of Indian professionals with approved petitions, the next visa number will not arrive until the fiscal year resets on October 1.",
        "slug": make_slug("eb2-india-cap-exhausted-fy2026-no-visas-october"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The EB-2 category is the single largest pathway for Indian tech professionals to obtain green cards. Its annual exhaustion is not a surprise — it is a structural inevitability of per-country caps — but the timing matters for anyone tracking priority date movement or planning an I-485 filing.",
        "tags": ["green-card", "eb2", "india", "visa-bulletin", "backlog", "per-country-cap"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/wy7ymogfrlkv/"},
            {"name": "Ainvest", "url": "https://www.ainvest.com"},
            {"name": "U.S. Department of State Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "image_caption": "An open passport displaying multiple visa stamps from international travel",
        "image_attribution": "Pexels",
        "body": """Every year, it happens. And every year, it still stings.

The U.S. Department of State has confirmed, through coordination with USCIS, that all available EB-2 visa numbers for India have been used up for fiscal year 2026. No new EB-2 green cards will be issued to Indian nationals until the fiscal year resets on October 1 — and the queue that was already decades long just got a few months longer.

## The Arithmetic of Exhaustion

The EB-2 category is designed for professionals with advanced degrees or exceptional ability. It is, for practical purposes, the default green card pathway for the Indian tech worker in America: the software engineer with a master's degree from a U.S. university, the data scientist with a decade of experience, the product manager whose employer filed an I-140 petition years ago.

Demand from India has been punishingly high for years. The per-country cap — a provision of the Immigration and Nationality Act that prevents any single nation from receiving more than seven per cent of total employment-based green cards — ensures that India, which generates more demand than any other country, is perpetually oversubscribed.

The result is a backlog that now stretches well beyond a decade for EB-2 India. Priority dates — the timestamp that determines an applicant's place in the queue — have been effectively frozen for years. An Indian engineer who filed in 2012 may still be waiting.

## What the Exhaustion Actually Means

When the State Department says the EB-2 India allocation is exhausted, it triggers a specific set of consequences:

No new EB-2 green cards are issued to Indian nationals for the remainder of the fiscal year. U.S. consulates pause final visa stamping in the category. Applicants inside the United States who were waiting to file adjustment of status applications (Form I-485) are stuck. USCIS records remain active and cases stay valid, but nothing moves forward.

This is not a policy change. It is not a new restriction. It is the system working exactly as designed — which is precisely the problem.

## The Broader EB Landscape

The EB-2 exhaustion does not exist in isolation. The EB-5 investor visa category for India has also hit its unreserved cap for FY2026, with new issuances paused until October. The EB-1 category — reserved for individuals of extraordinary ability — remains marginally more accessible, but approval rates have been falling as USCIS applies stricter scrutiny.

Meanwhile, the June 2026 Visa Bulletin shows continued retrogression across multiple categories. For Indian applicants, the pattern is grimly familiar: priority dates advance by weeks or months, then snap back when demand outstrips supply.

The per-country cap system was designed in an era when immigration demand was distributed more evenly across nations. It was not built for a world in which a single country — India — generates more employment-based immigration demand than the next several countries combined.

## The Recapture Question

There is a path that could ease the backlog, at least partially. An estimated 230,000 employment-based green cards went unused between 1992 and 2022, lost to bureaucratic delays rather than lack of demand. Ajay Bhutoria, a member of the President's Advisory Commission on Asian Americans, Native Hawaiians, and Pacific Islanders, has formally recommended that these unused numbers be recaptured and processed in addition to the annual limit of 140,000.

The proposal aligns with bills introduced in recent congressional sessions, but none have passed. The political appetite for expanding legal immigration — even through administrative recapture of already-authorised numbers — remains thin in the current climate.

## What Indian Professionals Should Do Now

For anyone in the EB-2 India queue, the immediate action items are limited but important. First, monitor the monthly Visa Bulletin closely. Priority date movement in October, when the new fiscal year begins, will signal whether FY2027 starts with any meaningful advancement.

Second, consider whether the EB-1 or NIW (National Interest Waiver) categories offer a viable alternative. The NIW, in particular, has seen a surge in filings from Indian professionals — though approval rates have fallen sharply, and USCIS scrutiny of self-petitioned cases has intensified.

Third, for those whose employers are willing, explore concurrent I-140 filings in multiple categories. An approved EB-1 petition, even if the EB-2 is the primary pathway, provides optionality if priority dates move differently across categories.

The EB-2 India cap will reset in October. It will exhaust again, probably before the fiscal year is half over. The question is not whether this cycle will repeat — it is whether anyone in Washington is willing to break it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
