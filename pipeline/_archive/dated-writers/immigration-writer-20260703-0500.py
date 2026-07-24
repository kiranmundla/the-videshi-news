#!/usr/bin/env python3
"""Immigration writer — July 3 2026, 05:00 PDT batch."""

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


# ─────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────

art1_body = """India has signed social security agreements with 19 countries. Britain, as of July 15, will become the twentieth. The United States, where more Indians work on temporary visas than in any other nation, is not on the list. It has never been on the list.

The India-UK Double Contribution Convention, negotiated as part of the broader Comprehensive Economic and Trade Agreement signed last July, will exempt roughly 75,000 Indian professionals on short-term assignments in Britain from paying into the UK's National Insurance system. Instead, they will continue contributing only to India's Employees' Provident Fund. The savings, according to government estimates reported by The Hindu Business Line, will exceed $500 million a year for Indian companies and their employees.

The mechanics are straightforward. An Indian IT engineer posted to London for three years currently pays social security contributions in both countries — to India's EPFO and to Britain's National Insurance. That dual contribution can run to £11,000–12,000 per month per worker. Under the new arrangement, the UK contribution disappears for assignments up to five years. India had originally pushed for a three-year window; the final deal extended it to five, a concession that Commerce Minister Piyush Goyal called a milestone for Indian service exporters.

## Why the US comparison stings

The United States has totalization agreements with more than 30 countries, including Australia, Canada, Japan, South Korea, Germany, and the United Kingdom itself. India is not among them. The absence is not for want of trying — Indian officials have raised the issue in bilateral discussions for over a decade — but negotiations have never reached the finish line.

The practical cost to Indian workers in America is significant. Every H-1B holder pays 6.2 per cent of their salary into Social Security and 1.45 per cent into Medicare, with their employer matching both. For a software engineer earning $130,000, that amounts to roughly $10,000 a year in combined employee contributions alone. To collect Social Security retirement benefits, a worker must accumulate 40 quarters of coverage — effectively ten years of work. Most H-1B holders, trapped in per-country green card backlogs that stretch decades, will either age out of the queue or return to India before reaching that threshold. Their contributions remain in the US Treasury.

The Social Security Administration has acknowledged this asymmetry. In the absence of a totalization agreement, there is no mechanism for India-based retirees to claim credit for years worked in America, nor for returning Indian professionals to port their US contributions back into the Indian system.

## What the UK deal reveals about Washington

The India-UK agreement did not materialise in isolation. It was part of a trade deal that both governments treated as a strategic priority. Britain offered social security concessions because it wanted Indian market access for its goods and services; India reciprocated because its IT sector needed cost relief in a post-Brexit labour market.

Washington, by contrast, has never packaged immigration relief into its trade framework with India. The current bilateral trade negotiations — where US Trade Representative Jamieson Greer recently met Indian counterparts in New Delhi and Deputy Assistant Secretary Bethany Poulos Morrison declared the two sides "very, very close" — focus overwhelmingly on goods: tariffs on agricultural products, pharmaceuticals, and auto parts. Worker mobility provisions, if they exist in the draft text, have not been publicly identified.

India's negotiators have tried to widen the aperture. After the $100,000 H-1B fee proclamation in September 2025, Commerce Minister Goyal's team explicitly raised the movement of skilled professionals during trade talks in Washington, according to Bloomberg. But tariff arithmetic dominates the agenda. A totalization agreement, which would require separate statutory action by the Social Security Administration, sits outside the trade framework entirely.

## What it means for the diaspora

For the roughly 600,000 Indian nationals on H-1B visas in the United States, the India-UK deal is a reminder of what bilateral goodwill can accomplish — and what its absence costs. Britain's 75,000 Indian workers will save thousands of pounds per posting. America's Indian workforce, many times larger, will continue paying into a system most of them will never draw from.

The missing totalization agreement also compounds the green card backlog. Without portability of social security credits, the financial penalty for returning to India after fifteen years of US employment is not merely the loss of a career trajectory — it is the forfeiture of more than a decade of mandatory contributions. For workers stuck in the EB-2 India queue, where wait times exceed 40 years by some estimates, the calculation is grimly circular: you cannot stay long enough to vest, and leaving means writing off every dollar you paid in.

India now has social security agreements spanning four continents. It has one with Portugal and one with Hungary. It does not have one with the country where its largest professional diaspora lives and works. That gap will become harder to ignore as the July 15 implementation date in London arrives — and as trade negotiators in Washington continue to talk about everything except the money sitting in accounts that no Indian worker will ever collect."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Got Britain to Stop Double-Taxing Its Workers. The US Will Not Even Discuss It",
    "subheadline": "The India-UK social security deal takes effect July 15, saving 75,000 Indian professionals $500 million a year. America's 600,000 H-1B holders still pay into a system most will never draw from.",
    "slug": make_slug("india-uk-social-security-deal-us-totalization-gap-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers in the US pay ~$10,000/year into Social Security they will likely never collect, while India's new UK deal saves professionals $500M annually — highlighting why the absence of a US-India totalization agreement costs the diaspora real money.",
    "tags": ["social-security", "totalization-agreement", "india-uk", "h1b", "trade-deal", "green-card-backlog"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/uk-social-security-exemption-to-save-indians-500-million-a-year/article69264889.ece"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/18/uk-grants-five-year-social-security-relief-to-75000-indian-professionals-under-trade-pact/"},
        {"name": "UK Government DCC Explainer", "url": "https://www.gov.uk/government/publications/uk-india-double-contributions-convention-dcc-explainer"},
        {"name": "US Social Security Administration - International Agreements", "url": "https://www.ssa.gov/international/agreements_overview.html"},
        {"name": "Bloomberg / The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/india-seeks-access-for-workers-in-us-trade-talks-after-h-1b-blow/article69154632.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Piyush_Goyal_crop.jpg/330px-Piyush_Goyal_crop.jpg",
    "image_caption": "Commerce Minister Piyush Goyal, who signed the India-UK trade agreement that includes the social security provision",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────

art2_body = """The domestic visa renewal pilot is dead. Third-country interviews are banned. Consulate appointments in India are backed up to Summer 2027. And leaving the country on an H-1B now risks triggering a $100,000 fee that your employer probably will not pay.

For hundreds of thousands of Indian H-1B holders in the United States, the net effect is a travel ban that nobody voted on and nobody signed. It arrived in pieces — a policy change here, an executive action there — and it is now functionally complete.

## The pilot that disappeared

Between January 2024 and April 2024, the State Department ran a domestic visa renewal pilot that allowed a narrow group of H-1B holders to get their visa stamps renewed inside the United States, without flying abroad. The programme was limited — it applied only to workers whose previous H-1B visas had been issued by US consulates in Canada or India during specific windows — but it offered a proof of concept. For those who qualified, it eliminated the central anxiety of the H-1B travel cycle: the fear that leaving America means you cannot get back in.

The pilot ended on April 1, 2024. It has not been renewed, revived, or replaced. Immigration attorney Ana Gabriela Urizar of Manifest Law puts it plainly: "Domestic visa renewal is no longer an option."

## The walls close further

In September 2025, the State Department rolled back third-country interview options, requiring most H-1B applicants to schedule visa stamping appointments exclusively in their home country. An Indian engineer who previously might have ducked into a US consulate in Canada or Mexico for a quick stamp now must fly to Chennai, Hyderabad, Mumbai, or New Delhi — and contend with whatever backlog awaits.

What awaited, starting December 15, 2025, was a new social media vetting mandate. The Department of State announced that all H-1B and H-4 applicants would undergo an "online presence review," with consular officers instructed to examine LinkedIn profiles, Facebook accounts, Instagram feeds, and other social media for content bearing on national security and admissibility.

The vetting requirement, according to the law firm Tafapolsky & Smith, created immediate "operational constraints." Consulates reduced the number of interviews they could conduct each day. The result was mass rescheduling. Appointments originally set for December 2025 and January 2026 were pushed to March, April, and in some cases as far as July 2026. By March 2026, immigration firm Manifest Law reported that some applicants were receiving appointment dates as far out as Summer 2027.

According to Fragomen, one of the world's largest immigration practices, US consulates in India now show wait times of 75 to more than 115 days for employment-based visa appointments. That does not include processing time after the interview — which can add weeks more.

## The $100,000 shadow

Layered on top of the consulate bottleneck is the $100,000 fee imposed by presidential proclamation in September 2025 on new H-1B petitions. The fee technically applies only to new petitions for workers outside the US who do not already hold a valid H-1B visa. Extensions and amendments filed from within the country are exempt.

But the distinction creates a perverse trap. An H-1B holder who travels abroad, lets their visa expire, and needs a new petition filed faces the fee. As Urizar warns: "Leaving the country while your case remains pending can trigger the $100,000 fee. Unless your employer has explicitly agreed to cover that cost, traveling carries a significant risk."

Most employers have not agreed to cover it. The result is a chilling effect on all international travel by H-1B holders, even those with technically valid visas. A missed connection, a delayed appointment, an unexpected administrative processing hold — any of these could convert a routine trip home into a six-figure bill.

## The drop box is narrower too

Even the expedited "drop box" route — where qualifying applicants could submit documents without an in-person interview — has been constricted. As reported by Cozen O'Connor, the State Department revised drop box eligibility to applicants renewing a visa in the same class that is either still valid or expired within the past twelve months. The previous window was 48 months. A worker whose H-1B visa expired 13 months ago, a common situation for those who avoided travel during the pandemic years, no longer qualifies.

## Families pay the price

The human cost is concentrated in the Indian community. India accounts for roughly 71 per cent of all H-1B approvals. The social media vetting delays, the third-country ban, and the fee risk converge on a single demographic: Indian tech workers and their families.

H-4 visa holders — the spouses and children of H-1B workers — face the same stamping bottleneck. A mother who travels to India for a family emergency may not be able to return for months. Parents age, children miss school milestones, weddings happen without the people who planned them.

Immigration firm Reddy Neumann Brown described the situation in stark terms: "Anyone with an expired visa who chooses to travel for stamping right now is putting themselves at risk of being stranded abroad for four to six months. Employers cannot keep an H-1B role vacant for half a year."

## No exit

The combined effect of these policies is an invisible cage. H-1B holders in America can work, pay taxes, and contribute to their communities. They cannot freely visit the country they came from. The system that invited them in has made it extraordinarily risky to step outside it.

No single policy created this trap. No single policy can undo it. But for the hundreds of thousands of Indian professionals who lie awake calculating whether they can risk a trip home for a parent's surgery or a sibling's wedding, the distinction between a de facto travel ban and a de jure one is academic. The cage works either way."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "You Cannot Leave America. The H-1B Travel Trap Is Now Complete",
    "subheadline": "Domestic renewal is dead, consulate appointments are backed up to 2027, and leaving triggers a $100,000 fee. Indian H-1B holders are functionally grounded.",
    "slug": make_slug("h1b-travel-trap-visa-stamping-consulate-backlog-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers — 71% of all H-1B approvals — face consulate wait times exceeding a year, a dead domestic renewal pilot, third-country interview bans, and a $100K fee risk that makes even routine trips home to India a career-ending gamble.",
    "tags": ["h1b", "visa-stamping", "consulate-backlog", "travel-ban", "social-media-vetting", "uscis"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/h1b-visa-stamping-in-usa/"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/lengthy-visa-appointment-backlogs-at-u-s-consulates-in-india.html"},
        {"name": "Tafapolsky & Smith LLP", "url": "https://www.tandslaw.com/resources/united-states-consulates-in-india-rescheduling-some-h-1b-and-h-4-visa-application-appointments-because-of-social-media-vetting-mandate/"},
        {"name": "Cozen O'Connor", "url": "https://www.cozen.com/news-resources/publications/2025/mass-cancellations-of-h-1b-visa-appointments-at-u-s-consulates-in-india"},
        {"name": "Reddy Neumann Brown PC", "url": "https://rnlawgroup.com/stop-holiday-travel-for-stamping-consulates-are-pushing-h-1b-h-4-interviews-to-mid-2026/"},
        {"name": "USCIS H-1B FAQ", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-workers/h-1b-specialty-occupations-and-fashion-models/h-1b-electronic-registration-process"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/US_Embassy_New_Delhi.jpg/1280px-US_Embassy_New_Delhi.jpg",
    "image_caption": "The US Embassy in New Delhi, where visa appointment backlogs now stretch months into the future",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
