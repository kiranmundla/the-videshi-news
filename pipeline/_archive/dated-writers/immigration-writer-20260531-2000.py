#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-31 20:00 UTC run"""
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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────────────────────

art1_body = """The United States and India are entering what diplomats on both sides are calling the final stretch of a bilateral trade agreement — and the immigration implications for Indian Americans could be larger than anything in the deal's official text.

A US delegation led by the Chief Trade Negotiator arrives in New Delhi on June 1 for four days of talks aimed at closing out the interim agreement framework that President Trump and Prime Minister Modi announced on February 7. Commerce Secretary Howard Lutnick, speaking last week, said he was "very optimistic" about the outcome, while Ambassador Vinay Gor told reporters he expects the deal to be "signed over the next few weeks and months." Secretary of State Marco Rubio went further: "We are on the verge of making that happen."

The trade numbers provide the backdrop. Bilateral goods-and-services trade has swollen from $20 billion two decades ago to over $220 billion today, and both governments are eager to formalise access terms before the 150-day window on Section 122 auxiliary tariffs expires. India is expected to reduce duties on American industrial goods, agricultural products, and energy commodities. Washington, in turn, is offering access to advanced semiconductor chips and support for "giant data centres" on Indian soil.

## Where Immigration Enters the Frame

Trade agreements between major economies rarely stay in their lane. The US-India relationship is no exception.

The single most concrete immigration signal from the current negotiations is the domestic visa renewal pilot programme confirmed by Julie Stufft, the State Department's Deputy Assistant Secretary for Visa Services. Beginning in December, the programme will issue 20,000 H-1B visa renewals inside the United States over three months. "The vast majority of those will be Indian nationals," Stufft said. The programme is explicitly designed to reduce wait times at Indian consulates — where interview slots in Chennai and Hyderabad currently stretch three to four months out — and to let consular posts "concentrate on new applicants."

The pilot sits alongside a more provocative idea floated by Lutnick himself: a "Trump Gold Card" immigration programme for entrepreneurs, offering flexibility on tax arrangements and residency status. Details remain thin, but the concept tracks with the administration's stated preference for high-value immigrants over volume-based systems.

## The Missing Agreement

What the trade deal almost certainly will not include is the item Indian professionals have wanted for decades: a US-India totalization agreement on social security.

India signed exactly such a deal with the United Kingdom earlier this year, covering employees on temporary assignments of up to 36 months and eliminating double social security contributions. The agreement forms part of the India-UK Comprehensive Economic and Trade Agreement and is expected to take effect in the first half of 2026.

No equivalent exists with the United States. Indian H-1B workers and green card holders contribute an estimated $1 billion annually to US Social Security — money most will never recoup because they either return to India before vesting (which requires 40 quarters, or roughly 10 years) or age out of the system while stuck in the green card backlog.

The Trade Promotion Council of India has pushed for a totalization agreement to be included in the trade deal. Washington has shown no interest. The US currently has totalization agreements with 25 countries; India is not among them.

## What to Watch For

The June 1-4 talks will cover market access, customs facilitation, non-tariff barriers, investment promotion, and "economic security alignment." None of these categories explicitly references immigration, but each one shapes the environment in which visa policy operates. A trade deal that increases Indian investment in American data centres, for instance, creates demand for L-1 intra-company transferees. Agricultural concessions could affect the seasonal labour provisions that Sikh and Punjabi farming communities in California depend on.

For the 4.4 million Indian Americans and the hundreds of thousands of Indian nationals on temporary work visas, the trade deal is not an immigration bill. But it is the closest thing to an immigration framework that Washington and New Delhi will produce this year. The details — and the omissions — deserve close reading.

*This article is general information, not legal advice.*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Trade Deal That Could Quietly Reshape Indian Immigration to America",
    "subheadline": "US and Indian negotiators meet June 1-4 to finalise a bilateral trade agreement. The immigration provisions nobody's talking about could matter more than the tariff lines.",
    "slug": make_slug("india-us-trade-deal-immigration-gold-card-totalization"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders contribute $1 billion annually to US Social Security they may never collect. The trade deal could — but likely won't — address the missing totalization agreement, while a domestic visa renewal pilot and a new 'Trump Gold Card' programme signal where the real immigration movement is happening.",
    "tags": ["trade-deal", "india-us", "totalization", "h1b", "visa-renewal", "trump-gold-card"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/"},
        {"name": "Ministry of External Affairs, India", "url": "https://mea.gov.in/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6949994/pexels-photo-6949994.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────────────────────

art2_body = """More than 6,000 international student visas have been revoked in recent months. Over 4,700 SEVIS records — the electronic tethers that keep foreign students in legal status — have been terminated, many without prior notice. Graduate enrolments from abroad fell 15 percent in the latest Open Doors data. And Indian families, who send more students to America than any country except China, are watching the numbers and doing the maths.

The crackdown is not an abstraction. It has a name. Ranjani Srinivasan, an Indian citizen and doctoral student in Urban Planning at Columbia University, had her F-1 visa revoked on March 5 for alleged involvement in "activities supporting Hamas." Six days later, she used the CBP Home App — the government's new voluntary departure tool — to self-deport. Secretary of Homeland Security Kristi Noem called her a "terrorist sympathiser" on social media and said she was "glad" to see the app used.

## The Machinery of Revocation

The stated reasons for the 6,000-plus revocations range from criminal offences (assault, DUI, burglary) to alleged terrorism support to participation in protests "deemed disruptive or politically sensitive." It is the last category that has drawn the most controversy. An estimated 200 to 300 cases involve students whose pro-Palestine activism on campus was classified as potential terror support under the Immigration and Nationality Act's broad provisions.

The State Department has simultaneously expanded its social media vetting regime. Mexico joined Brazil, Colombia, the Philippines, and other countries in May under the strictest screening tier, where applicants must publicly disclose social media accounts. The expanded rule now covers H-1B workers, students, exchange visitors, religious workers, and several dependent visa categories.

For Indian students, the convergence is especially uncomfortable. India is the second-largest source of F-1 visa holders. Indians accounted for a disproportionate share of the 343,981 eligible H-1B registrations in FY2026 — and many of those registrants entered the US pipeline as F-1 students on OPT or STEM OPT. The path from Indian university to American campus to H-1B petition is the single most common immigration trajectory for Indian professionals. Every disruption to the student pipeline ripples forward.

## The Numbers That Should Worry New Delhi

The Open Doors 2024-25 report showed total international student numbers up 7 percent year-over-year, masking a sharper decline underneath. New enrolments dropped 7 percent. Graduate enrolments — the category where Indian students are most concentrated — fell 15 percent. Undergraduate enrolments, dominated by Chinese students, rose 5 percent.

The graduate decline is the signal worth tracking. Indian students in American master's and doctoral programmes are not casual visitors. They are the feedstock of the H-1B system, the STEM OPT extension pipeline, and eventually the EB-2 and EB-3 green card queues. A sustained decline in Indian graduate enrolments does not just affect universities. It reshapes the composition of the American tech workforce over the following decade.

Students who do enrol are arriving into a different environment. The 90-day unemployment limit on standard OPT and 150-day limit on STEM OPT now operate alongside mandatory social media checks, an expanded SEVIS compliance regime, and the knowledge that a single protest attendance could — in the government's current interpretation — jeopardise an entire immigration trajectory. The chilling effect is not speculative. Multiple reports describe students deleting social media accounts, avoiding political discussions, and declining to attend campus events.

## The Employer Feedback Loop

The student visa crackdown connects directly to the employer side of the equation. Companies sponsoring H-1B visas already face the $100,000 fee (currently challenged in federal court), the 38 percent collapse in FY2027 registrations, and an administrative environment where USCIS site visits are surging. Now add a shrinking pool of OPT-eligible graduates.

The arithmetic is not complicated. Fewer Indian students means fewer OPT workers means fewer H-1B petitions means fewer green card applications. The current policy framework is not just restricting immigration at the point of entry. It is constricting the pipeline at the source.

## What Indian Families Are Calculating

For a middle-class family in Hyderabad or Pune weighing whether to spend $80,000 to $150,000 on an American master's degree, the calculus has shifted. The OPT-to-H-1B conversion rate of roughly 35 percent was already a gamble. Layer on the $100,000 employer fee, the social media audits, the SEVIS termination risk, the 60-day grace period after layoffs, and the green card backlog that stretches decades — and the expected return on that education investment looks materially worse than it did two years ago.

Canada, the UK, Germany, and Australia are all actively recruiting Indian students. Canada's Express Entry system, for all its recent turbulence, still offers a permanent residency timeline measured in months rather than decades. Australia's post-study work rights are expanding. The UK's Graduate Route visa gives two years of unrestricted work after graduation.

America's competitive position in the global market for Indian talent is not collapsing overnight. But it is eroding, one revoked SEVIS record at a time. The 6,000 number is a data point. The trend line behind it is the story.

*This article is general information, not legal advice.*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Six Thousand Visas Revoked — The Student Crackdown Reshaping Indian Families' American Calculus",
    "subheadline": "Mass F-1 visa revocations, SEVIS terminations, and social media audits are not just restricting entry. They are constricting the pipeline that feeds the entire Indian immigration system.",
    "slug": make_slug("f1-visa-revocations-sevis-indian-students-pipeline"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families spending $80K-$150K on American master's degrees face a radically altered risk calculus: OPT-to-H-1B conversion at 35%, $100K employer fees, social media audits, SEVIS termination risk, and a green card backlog measured in decades. The student pipeline that feeds Indian immigration to America is under structural pressure.",
    "tags": ["f1-visa", "student-visa", "sevis", "indian-students", "opt", "h1b-pipeline", "social-media-screening"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CollegeChalo", "url": "https://www.collegechalo.com/news/trumps-visa-crackdown"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/"},
        {"name": "Visa Lawyer Blog", "url": "https://www.visalawyerblog.com/"},
        {"name": "Open Doors / IIE", "url": "https://opendoorsdata.org/"},
        {"name": "Department of Homeland Security", "url": "https://www.dhs.gov/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
