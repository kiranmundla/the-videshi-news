#!/usr/bin/env python3
"""Immigration writer — 2026-06-02 08:00 UTC run"""

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

# ──────────────────────────────────────────────
# ARTICLE 1
# ──────────────────────────────────────────────

art1_body = """July's Visa Bulletin hasn't dropped yet, but the State Department has already told you what it's going to say. If you hold an Indian passport and a green card dream, every employment-based category is now moving in the wrong direction — simultaneously.

## EB-2 India: Mathematically Dead Through September

On May 22, the State Department's Visa Office made it official: India has exhausted its EB-2 per-country allocation for Fiscal Year 2026. The category will display "U" — Unavailable — on both the Final Action Dates and Dates for Filing charts through September 30. No ambiguity, no wiggle room, no late-fiscal-year miracle. The June bulletin already showed EB-2 India's Final Action Date plunging from July 15, 2014 to September 1, 2013 before the shutters came down entirely.

For the roughly 400,000 approved I-140 petitions waiting in the EB-2 India queue, this means four months of enforced paralysis. Pending I-485 applications won't be denied — USCIS simply cannot approve them until a visa number reappears on October 1. Employment Authorization Documents, advance parole travel permits, H-1B portability rights, and AC21 job-change protections all remain intact during the freeze. But no one gets a green card.

## EB-1 India: The "Safe" Category Isn't Safe Anymore

EB-1 India already retreated 107 days in the June bulletin — from April 1, 2023 to December 15, 2022 — the sharpest single-month retrogression in four years. The bulletin's Section E warning was blunt: "further retrogressions, or making the categories unavailable, may be necessary" if India's pro-rated EB-1 limit is reached.

Attorney forecasts from Wolfsdorf Rosenthal, Fragomen, and Shusterman converge on a July Final Action Date somewhere between August and October 2022 — a further two-to-five-month pullback. The possibility of EB-1 India going "Unavailable" before September 30 is no longer academic. For the thousands of Indian nationals who pivoted their green card strategy to EB-1A self-petitions or EB-1C multinational manager transfers specifically to escape the EB-2 backlog, this is the escape route narrowing in real time.

## EB-5 Unreserved India: The Loudest Warning in the Bulletin

Section H of the June bulletin deployed the State Department's sharpest language — specifying retrogression or unavailability "in the next month" rather than the vague "in the coming months" applied elsewhere. That phrasing is the bureaucratic equivalent of a foghorn.

Indian investors now account for nearly a quarter of all EB-5 filings, up from four percent five years ago. The surge reflects a rational calculation: why wait 12 years in EB-2 when $800,000 to $1,050,000 buys a faster path? But rational calculations have a ceiling, and the EB-5 Unreserved category has hit it. The July outcome will be either a significant retrogression from the current May 1, 2022 cutoff — likely back into late 2020 or early 2021 — or an outright "U" listing through September.

The set-aside categories (Rural, High Unemployment, Infrastructure) remain "Current" and are not subject to the Section H warning. They are now the only EB-5 lane without a flashing red light, and the window to file under them before global demand catches up is shrinking every quarter.

## EB-3 India and China: Movement, but Don't Celebrate

EB-3 India is forecast to advance roughly 30 days in July, moving from December 15, 2013 to approximately January 15, 2014. EB-3 China should see a similar increment. This is the one category not actively contracting for India, but 30 days of forward motion on a priority date from 2013 is the immigration equivalent of a participation trophy.

For anyone contemplating an EB-2 to EB-3 downgrade — a strategy that gained traction in earlier fiscal years — the math doesn't work. EB-3 India's predicted January 2014 cutoff sits well behind the EB-2 India priority dates of most applicants who filed in the 2014-2016 peak years. The downgrade offers no short-term relief.

## USCIS Locked to Final Action Dates — Third Month Running

USCIS shifted to requiring Final Action Dates for employment-based adjustment of status filings in May and held that determination through June. July will almost certainly be the third consecutive month. This matters because the more permissive Dates for Filing chart allows applicants to submit I-485 forms — and access EADs and advance parole — even when their green card can't yet be approved. With USCIS on Final Action, that door stays shut for anyone whose priority date falls between the two charts.

## What This Means for Your Kitchen Table

If you're an Indian H-1B worker with an approved I-140 and a pending I-485, nothing changes operationally — your case remains pending, your EAD stays valid, your job portability rights are intact. The pain is psychological and strategic: four months of zero progress, no approvals, and the knowledge that EB-1 and EB-5 are contracting behind you.

If you haven't yet filed I-485 and your priority date is after September 2013 in EB-2, you cannot file until October at the earliest. Use the summer to ensure your PERM, I-140, and supporting documentation are bulletproof for when the window reopens.

If you're evaluating EB-5, the set-aside categories are the last lane without a barricade. File before the next fiscal year's demand data forces the State Department's hand there too.

The July bulletin will publish in mid-June. When it does, expect the numbers to confirm what the warnings already said: FY-2026's final quarter is the most contractionary stretch for Indian green cards in at least a decade."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Five Categories, One Direction — July's Visa Bulletin Could Be the Worst Month for Indians This Decade",
    "subheadline": "EB-2 India is confirmed dead through September. EB-1 is retrograding. EB-5 faces its loudest warning ever. And USCIS won't even let you use the filing chart.",
    "slug": make_slug("july-visa-bulletin-forecast-india-multi-category-contraction"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Every employment-based green card pathway for Indian nationals is contracting simultaneously in Q4 FY-2026. EB-2 India is unavailable, EB-1 India is retrograding, EB-5 Unreserved India faces imminent retrogression, and USCIS is locked to Final Action Dates. For the hundreds of thousands of Indian H-1B workers with pending green card applications, this is the most restrictive quarter in a decade.",
    "tags": ["green-card", "visa-bulletin", "eb2-india", "eb1-india", "eb5", "uscis", "immigration", "retrogression"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/visa-bulletin/july-2026-visa-bulletin-complete-analysis-and-forecast/"},
        {"name": "USCIS Adjustment of Status Filing Charts", "url": "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/adjustment-of-status-filing-charts"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/united-states/"},
        {"name": "Murthy Law Firm", "url": "https://www.murthy.com/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7009478/pexels-photo-7009478.jpeg",
    "is_editorial": False,
    "body": art1_body,
}

# ──────────────────────────────────────────────
# ARTICLE 2
# ──────────────────────────────────────────────

art2_body = """The layoff email arrives on a Tuesday. By Wednesday, your corporate badge is deactivated. By Thursday, your immigration attorney has told you what you already know: you have 60 days to find a new employer willing to sponsor your H-1B, change to a different visa status, or leave the country. Your house, your kid's school enrollment, your ten years of building a life in America — all of it now runs on a countdown timer shorter than a Netflix subscription cycle.

This has always been the brutal arithmetic of the H-1B visa. What's new in 2026 is the engine driving the layoffs: artificial intelligence. And the same technology displacing roles is making it harder to find a replacement sponsor in time.

## The AI Layoff Wave Hits Different

Tech companies are cutting headcount at a pace not seen since the 2022-2023 correction, but the 2026 cuts carry a distinct signature. They're not driven by over-hiring during a pandemic boom or interest rate panic. They're driven by AI-powered workflow consolidation — entire teams of mid-level engineers, QA analysts, and data processors being replaced by systems that run 24 hours a day without visa sponsorship.

For H-1B holders, this isn't just a job loss. The visa is employer-sponsored, meaning the status is directly tied to the petitioning company. When employment ends — layoff, termination, or resignation — the visa status technically lapses from that date. USCIS recognizes a grace period of up to 60 consecutive days, but this is not an extension of H-1B status. It's a limited window to take corrective action.

Sixty days sounds manageable in a normal market. In a market where AI is simultaneously eliminating the very roles you were hired for, it becomes a sprint through quicksand.

## The Numbers Behind the Squeeze

The math is stark. H-1B registrations dropped to 358,000 for FY2026 — down from 478,000 the prior year and 780,000 at the peak. The $215 registration fee (up from $10) and USCIS's fraud crackdown explain part of the decline, but the bigger factor is structural: companies are hiring fewer specialty-occupation workers because AI is absorbing the work.

Indian nationals still account for roughly three-quarters of all H-1B approvals, which means Indians bear the bulk of whatever happens to the program. India's six largest IT services companies — TCS, Infosys, HCL, Wipro, Tech Mahindra, and LTIMindtree — have collectively reduced H-1B filings by 46 percent over five years, according to USCIS data. They're building nearshore centers, hiring locally in the United States, and integrating automation into delivery.

Meanwhile, Big Tech presents a paradox that fuels political backlash. Google, Amazon, Microsoft, Uber, and eBay are simultaneously expanding teams in India — with 25 percent of companies adding headcount and 20 percent creating entirely new roles there, per January 2026 reporting — while maintaining large H-1B petition volumes in the US. Oracle filed for roughly 3,126 H-1B petitions in fiscal years 2025-2026 while cutting 16,000 corporate employees. The optics are toxic, and anti-H-1B sentiment from both left and right is leveraging these numbers.

## What the 60-Day Clock Actually Looks Like

The legal framework is simple. The lived experience is anything but.

During those 60 days, an H-1B worker must secure a new employer willing to file a transfer petition, change to a different status (B-1/B-2 visitor, H-4 dependent if a spouse holds an H-1B, or F-1 if returning to school), or make arrangements to leave.

Immigration attorney Sophie Alcorn, based in Silicon Valley, has described the dynamic bluntly: "People are freaking out." The fear isn't hypothetical. A laid-off H-1B holder who spent a decade in America — buying a home, putting children in school, accumulating student loan debt from US universities — faces the prospect of liquidating everything in two months.

The $100,000 H-1B fee imposed by executive proclamation in September 2025 adds another layer. Even employers willing to sponsor a transfer must absorb this cost (or argue for an exemption), making smaller companies and startups less likely to take on displaced H-1B workers. The fee has already driven a measurable offshoring trend: companies are finding it cheaper to create roles in Bangalore than to pay $100,000 per petition in San Jose.

## The Green Card Trap Makes It Worse

The cruelest dimension is the green card backlog. Many H-1B workers being laid off have approved I-140 immigrant petitions and pending I-485 adjustment of status applications — meaning they've been waiting years for a green card that remains perpetually out of reach. An EB-2 India priority date from 2014 is currently frozen until October. Losing your job doesn't cancel the I-140 (it remains valid for 180 days and beyond under certain conditions), but it does create a gap in your immigration status that requires careful management.

Workers with pending I-485 applications who have been in that status for more than 180 days can use AC21 portability to change employers without restarting the process. But this requires finding a job in the "same or similar" occupational classification — a standard that's being tested as AI reshapes what roles exist.

## What Displaced Workers Can Do Now

Immigration attorneys consistently advise several moves for H-1B holders facing AI-driven layoffs:

First, document everything from day one. The 60-day clock starts on the last day of employment, not the day you receive notice. Get the exact termination date in writing.

Second, file for transfer petitions aggressively. Premium processing ($2,805 for a 15-business-day adjudication) is worth every dollar when you're racing a 60-day deadline.

Third, consider a change of status to H-4 (if your spouse holds an H-1B) or B-1/B-2 (visitor) as a stopgap while you continue your job search. This buys time without abandoning your I-140 or I-485.

Fourth, if you have a pending I-485 with more than 180 days of processing time, use the AC21 portability provision. You are not chained to the employer who filed your green card petition.

The AI revolution is reshaping the American economy. For the three-quarters of a million Indian nationals navigating the H-1B system, it's also reshaping the terms of their right to stay."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Sixty Days and Counting — Inside the AI Layoff Scramble That H-1B Workers Can't Afford to Lose",
    "subheadline": "AI-driven job cuts are triggering the H-1B grace period for thousands of Indian tech workers. The shrinking market makes finding a new sponsor harder than ever.",
    "slug": make_slug("ai-layoffs-h1b-60-day-clock-indian-tech-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold roughly three-quarters of all H-1B visas. When AI-driven layoffs hit tech companies, Indians bear the disproportionate burden of the 60-day grace period scramble. Combined with the $100,000 H-1B fee, frozen EB-2 green card dates, and a shrinking job market for the roles AI is replacing, displaced Indian H-1B workers face the hardest path to staying in America in a generation.",
    "tags": ["h1b", "layoffs", "ai", "tech-workers", "immigration", "grace-period", "green-card", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "EB5 Visa Investments", "url": "https://www.eb5visainvestments.com/"},
        {"name": "Marketplace / NPR", "url": "https://www.marketplace.org/"},
        {"name": "TechGig", "url": "https://content.techgig.com/"},
        {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.com/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/52608/pexels-photo-52608.jpeg",
    "is_editorial": False,
    "body": art2_body,
}

# ──────────────────────────────────────────────
# PUBLISH
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
