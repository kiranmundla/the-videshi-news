#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-30 17:00 PT run.
Inserts 2 fresh immigration articles into Supabase.
"""

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


# ── Article 1 ──────────────────────────────────────────────────────────────────

article1_body = """\
The $800,000 investment was supposed to be the shortcut. For a growing number of Indian families — tech professionals tired of the EB-2 backlog, business owners hedging against H-1B chaos, parents stacking the deck for children who might want to study in the United States — the EB-5 investor visa had become the escape hatch. Pay up, create jobs, get a green card without waiting decades in line.

That hatch just slammed shut, at least until October.

The U.S. Department of State confirmed in early June that all available EB-5 unreserved immigrant visa numbers for applicants chargeable to India have been exhausted for fiscal year 2026. No further visas in this category will be issued to Indian nationals until the annual allocation resets on October 1, when FY 2027 begins.

## What happened

Under the Immigration and Nationality Act, the annual EB-5 visa limit is 7.1 per cent of the worldwide employment-based total, with 68 per cent of that allocation going to unreserved categories. A separate per-country cap limits nationals of any single country to no more than 7 per cent of the combined employment-based and family-sponsored visas each year.

India hit that ceiling. The EB-5 Reform and Integrity Act of 2022 had routed unused reserved visas from FY 2024 into the unreserved pool for FY 2026 — a one-time top-up that temporarily inflated supply. Indian demand, stoked by years of green card frustration in other employment categories, consumed the entire allocation well before the fiscal year's September 30 close.

"It means all available visa numbers for this specific group — India, unreserved — have been used," said Joseph Barnett, an EB-5 attorney at WR Immigration.

## Who gets hurt

The most immediate disruption falls on investors already near the finish line: those waiting abroad for immigrant visa issuance, applicants inside the United States pursuing adjustment of status, and spouses and children whose cases depend on the principal investor's visa availability.

Pending cases inside the U.S. are not cancelled. But USCIS cannot grant final approval without an available visa number, so adjustment applications will sit in administrative limbo until October at the earliest.

For investors who haven't yet filed, the signal is starker. The unreserved category is becoming what EB-2 India has been for years: a line with no visible end. Immigration attorney Oliver Yang of Reid & Wise cautioned against reading too much into the immediate pause but noted it "confirms earlier Visa Bulletin indications that retrogression or visa unavailability was likely."

## The reserved loophole

There is one escape clause. The EB-5 reserved categories — set aside for rural area projects (20 per cent of annual allocation), high-unemployment area projects (10 per cent), and infrastructure projects (2 per cent) — remain current and unaffected by the India-specific pause. No warnings have appeared in prior visa bulletins suggesting these categories will become unavailable this fiscal year.

For Indian investors who haven't yet committed capital, the calculus has shifted overnight. A rural EB-5 project, once seen as a niche play for investors willing to accept less glamorous locations, now offers something the unreserved pool cannot: a path that remains open.

Dennis Tristani of Tristani Law noted that unused unreserved visa numbers will not flow into reserved categories this fiscal year, but the reserved pipeline remains clear. "The EB-5 reserved categories remain current," he said.

## A September deadline looms

There is an additional wrinkle. The RIA's grandfathering provisions protect investors who file before September 30, 2026, locking in current investment thresholds and TEA benefits. After that date, new regulations or fee increases could raise the bar further.

For Indian investors contemplating EB-5, the window is narrowing from both ends: unreserved visas are gone until October, reserved categories remain open but could face their own pressure if demand surges, and the grandfathering deadline is three months away.

## The bigger picture

India's EB-5 cap hit is a symptom of the same disease afflicting every employment-based immigration category: a statutory framework designed for a different era colliding with massive, sustained demand from Indian nationals. The per-country caps that create 80-year EB-2 backlogs are now doing the same to investor visas, only faster.

The irony is pointed. EB-5 was marketed to Indian families precisely as the route that avoided the backlog problem. For a while, it worked. Now, with demand outstripping supply in the unreserved pool, Indian investors face the same essential challenge they tried to buy their way out of — too many people, not enough numbers, and a system that will not budge.
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's EB-5 Investor Green Cards Just Ran Out. The Escape Hatch Is Closing",
    "subheadline": "The State Department has exhausted all unreserved EB-5 visa numbers for Indian nationals in FY 2026. No new investor green cards until October — and the reserved category may be next.",
    "slug": make_slug("eb5-india-unreserved-visa-cap-exhausted-fy2026"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families who turned to the $800,000 EB-5 investment route to escape the decades-long EB-2/EB-3 green card backlog now face a new wall — the unreserved investor visa pool is empty until October, forcing a pivot to rural and high-unemployment projects before the September 30 grandfathering deadline.",
    "tags": ["eb5", "green-card", "investor-visa", "immigration", "uscis", "visa-bulletin"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Envoy Global", "url": "https://www.envoyglobal.com/resources/immigration-news/india-eb-5-unreserved-visa-cap-reached-for-fy-2026"},
        {"name": "BAL Immigration", "url": "https://www.bal.com/bal-news/united-states-eb-5-unreserved-visa-limit-met-for-india/"},
        {"name": "NPZ Law Group", "url": "https://visaserve.com/india-hits-the-eb-5-unreserved-visa-limit-for-fy-2026-what-indian-investors-need-to-know/"},
        {"name": "EB5Investors.com", "url": "https://www.eb5investors.com/news/india-exhausts-eb-5-unreserved-visa-cap"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/indian-eb-5-visa-pause-fy-2026-unreserved-limits-reached/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────────────

article2_body = """\
The numbers are extraordinary. Bilateral trade in goods and services between India and the United States has grown from $20 billion to over $220 billion in two decades. A U.S. Trade Representative delegation left New Delhi on Wednesday after another round of negotiations. India's Commerce Minister Piyush Goyal says the first tranche could be signed by mid-July. A senior State Department official calls it "very, very close."

And yet, across hundreds of pages of framework documents, tariff schedules, and reciprocal-access commitments, the issue that most directly affects the 4.4 million Indian Americans living in the United States barely registers.

## A deal about things, not people

The proposed Bilateral Trade Agreement — launched by President Trump and Prime Minister Modi in February — is primarily a goods deal. Agriculture access, steel and aluminium tariffs, digital trade standards, and energy security dominate the negotiating agenda. U.S. Ambassador Sergio Gor told Indian media last week the deal was "99 per cent there."

What is conspicuously absent is any formal commitment on talent mobility — H-1B processing timelines, visa portability, mutual recognition of professional qualifications, or guaranteed pathways from student visa to work authorisation. These are the issues that define daily life for hundreds of thousands of Indian professionals in America, and they are nowhere near the table.

"Mobility continues to be treated as an auxiliary topic, often parked in side conversations or overlooked entirely in trade talks," wrote Krishan Sharma of Bennett University and Nida Rahman of the University of Petroleum and Energy Studies in a recent analysis for the East Asia Forum.

## What other countries got

The absence is not inevitable. When India negotiated the 2022 Australia-India Economic Cooperation and Trade Agreement, New Delhi secured significant commitments on student, professional, and worker mobility — including temporary visa access for 1,800 Indian yoga instructors and chefs. The deal included time-bound visa processing standards, bridging mechanisms from student status to work, and multi-year, multiple-entry terms for intra-company transferees.

India asked. Australia said yes. The United States has not been asked.

Sharma and Rahman argue India should propose a "mobility annex" to the U.S. deal: time-bound processing standards, job-change portability for high-skill visas, and a trusted-employer track for vetted firms. "If India and the United States want to build a resilient economic relationship," they wrote, "the framework of any trade agreement must reflect today's realities."

## The paradox of Mission 500

The administration has set a target of $500 billion in bilateral trade by 2030 — what officials call "Mission 500." Deputy Assistant Secretary Bethany Poulos Morrison said last week the deal would open India's market of 1.4 billion people to American goods "on reciprocal and mutually beneficial terms."

But trade in services — the category that includes IT consulting, software development, and the work performed by every H-1B holder — already accounts for a substantial portion of the bilateral relationship. Indian IT firms alone saw their H-1B visa approvals fall to less than half their 2015 levels by 2024. The $100,000 annual H-1B fee, the wage-weighted lottery, the crackdown on Day-1 CPT, and the elimination of Duration of Status for F-1 students have collectively made it harder, slower, and more expensive for Indian talent to work in the United States.

A services economy cannot thrive without the people who power it. A trade deal that addresses goods but ignores the human infrastructure of services trade is, as Sharma and Rahman put it, "an offer half made."

## What Indian Americans want to hear

For the Indian professional on an H-1B — watching the EB-2 queue stretch past 2040, paying a $100,000 fee that a federal judge struck down but the government kept collecting, worrying about whether their spouse's H-4 EAD will arrive before the gap in work authorisation — the trade deal is background noise. Tariff schedules do not help when your visa stamping appointment in Chennai is nine months out.

A mobility annex would not solve every problem. Congressional reform of per-country caps, a genuine fix to the green card backlog, and a rational H-1B fee structure all require legislation that neither party seems inclined to pursue. But a bilateral commitment to processing standards and visa portability — the kind of commitment India secured from Australia — would be more than rhetoric. It would be a contractual obligation between two governments, enforceable and measurable.

India's negotiators have leverage they rarely possess: Washington wants this deal signed before midterm politics consume the agenda. If New Delhi is willing to offer expanded goods access and regulatory cooperation, it should demand something in return for the 4.4 million Indian Americans whose professional lives are governed by visa rules that no trade framework has ever addressed.

The deal is 99 per cent done. The 1 per cent that matters most to the diaspora has not been written.
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The India-US Trade Deal Is '99 Per Cent Done.' Nobody Is Talking About Visas",
    "subheadline": "As Washington and New Delhi race to close a historic trade agreement by mid-July, experts warn that talent mobility — the issue that most directly affects millions of Indian Americans — is being left off the table.",
    "slug": make_slug("india-us-trade-deal-talent-mobility-visa-missing"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "A $500 billion trade target means nothing to the Indian professional stuck in a decades-long green card queue. Experts argue India should demand a 'mobility annex' — processing guarantees, visa portability, and trusted-employer tracks — as part of the deal, the way it did with Australia.",
    "tags": ["india-us-trade", "h1b", "immigration", "talent-mobility", "trade-deal", "diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/first-tranche-us-india-trade-deal-likely-by-mid-july-says-india-trade-minister-2026-06-06/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/30/us-expects-to-close-trade-deal-with-india/"},
        {"name": "East Asia Forum", "url": "https://eastasiaforum.org/2025/09/11/dont-sideline-talent-in-india-us-trade-talks/"},
        {"name": "IndUS Business Journal", "url": "https://www.indusbusinessjournal.com/india-u-s-to-hold-new-talks-june-23-24-on-interim-trade-deal/"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_meets_the_President_of_the_United_States%2C_Mr._Donald_J._Trump_on_the_sidelines_of_the_52nd_G7_Summit_in_Evian.jpg/1280px-thumbnail.jpg",
    "image_caption": "Prime Minister Narendra Modi meets President Donald Trump on the sidelines of the G7 Summit in Évian",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ── Insert ─────────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
