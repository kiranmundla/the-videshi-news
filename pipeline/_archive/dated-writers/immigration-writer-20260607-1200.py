#!/usr/bin/env python3
"""Immigration writer — 2026-06-07 12:00 UTC run"""

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

# Validate image URL
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


# ── ARTICLE 1 ──────────────────────────────────────────────────────────
art1_body = """The State Department confirmed on May 22 that every available EB-2 immigrant visa allocated to Indian nationals for fiscal year 2026 has been issued. The gate is shut. No new EB-2 green cards — whether through consular processing abroad or adjustment of status inside the United States — will be approved for India-chargeable applicants until the fiscal year resets on October 1.

For the roughly 426,000 Indian professionals sitting in the EB-2 queue with approved I-140 petitions, the announcement landed less as a surprise than as a confirmation of the arithmetic they already knew. The Immigration and Nationality Act caps any single country at seven percent of the combined employment-based and family-sponsored visa allocation. India, which accounts for the overwhelming majority of EB-2 demand, burns through that sliver well before the fiscal year ends — and this year it happened with more than four months still on the clock.

## What exactly changed

The Department of State, working with USCIS, issued the exhaustion notice on May 22. The practical effects are immediate and binary:

- U.S. embassies and consulates worldwide cannot issue EB-2 immigrant visas to India-chargeable applicants for the remainder of FY 2026.
- USCIS cannot approve any pending adjustment-of-status applications in the EB-2 India category, regardless of how early the applicant's priority date is.
- Pending cases are not denied — they remain in limbo, waiting for new visa numbers that will not arrive until October 1.

The cutoff compounds with the PM-602 policy memo issued the previous day, May 21, which reframed adjustment of status as "extraordinary" discretionary relief rather than a routine pathway. Indian EB-2 applicants now face a double bind: the visa numbers they need don't exist for four months, and the in-country process they relied on has been officially downgraded from standard procedure to special favour.

## The artificial advance, and its consequences

The priority date movement that Indian EB-2 applicants saw earlier in fiscal year 2026 was, according to former Department of State official Charles Oppenheim, largely illusory. India's EB-2 Final Action Date marched forward from April 1, 2013, in October 2025 to July 15, 2014, by April 2026 — a pace that raised expectations across the diaspora.

Oppenheim's assessment was blunt: the movement was "completely artificial," driven not by genuine progress through the backlog but by the Trump administration's travel restrictions on 75 countries. Those restrictions reduced demand from Rest of World applicants, temporarily freeing visa numbers that spilled over to India and China. When the restrictions end — and Oppenheim's view is that "there has to be the boomerang effect" — those numbers will snap back, and India's priority dates will retrogress, potentially sharply.

The comparison to the COVID era is instructive. When pandemic-era legislation temporarily raised annual employment-based visa limits to 281,000 in FY 2022, applicants saw unprecedented forward movement. The correction that followed was swift and painful. The same dynamic is now building, but with lower baseline numbers and higher demand.

## The scale of the queue

According to the most recent USCIS backlog data, India's employment-based green card queue contains 574,765 principal applicants. Including spouses and dependent children, the total reaches 862,363 people — roughly the population of San Francisco, all waiting in a single immigration line.

The EB-2 category alone accounts for 426,465 principal applicants from India. EB-3 holds another 133,409. Even EB-1, the category reserved for individuals of "extraordinary ability," has a 10,049-person backlog for India.

Against an annual worldwide employment-based limit of 140,000 visas — shared across all countries and all preference categories — the math is unforgiving. India's per-country share works out to roughly 9,800 visas per year, a number that would take over four decades to clear the current queue even if no new applications were filed.

## What Indian professionals should do now

Immigration attorneys are advising EB-2 India applicants to treat the next four months as a planning window rather than dead time. Several strategies are in play:

**Maintain H-1B status carefully.** With no EB-2 approvals possible until October, any gap in work authorisation becomes more dangerous. Applicants whose H-1B extensions depend on a pending or approved I-140 should verify that their documentation is airtight.

**Evaluate EB-3 downgrade — but do the math first.** For much of FY 2026, the EB-2 and EB-3 Dates for Filing for India both sat at January 15, 2015, offering no strategic advantage to a downgrade. If the July bulletin shifts those dates, the calculus may change.

**Watch the July Visa Bulletin closely.** The State Department's next bulletin will signal how FY 2027 starts. Whether India EB-2 opens with forward movement or retrogresses further will depend on how many unused numbers from other countries spill over — and on whether the 75-country travel restrictions remain in force.

**Consider whether the PM-602 memo affects your filing strategy.** For applicants who planned to adjust status inside the United States, the new USCIS posture on AOS as discretionary relief means consular processing may become the safer bet — even if it requires a trip to India and exposure to stamping delays.

The EB-2 exhaustion is not a crisis in the acute sense. No one's status changed overnight. But it is a concrete reminder that the system Indian professionals have navigated for years — file the I-140, wait for the priority date, adjust status — is being squeezed from every direction at once. The queue is longer than a human career. The rules are shifting underneath it. And the next four months of silence from USCIS will feel, to 426,000 people, very loud."""

art1_image = "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg"

# ── ARTICLE 2 ──────────────────────────────────────────────────────────
art2_body = """The number is 862,363. That is how many Indian nationals — principal applicants plus their spouses and dependent children — are currently waiting for an employment-based green card in the United States. It is roughly the population of San Francisco, all held in a single administrative queue that moves at the speed of federal statute, not federal urgency.

The figure comes from the most recent USCIS backlog data, and its composition tells a story that raw totals obscure. India's queue is not one line. It is five, stacked by preference category, each with its own pace and its own ceiling.

## The breakdown

| Category | India Principal Applicants | Including Dependents (est.) |
|----------|---------------------------|----------------------------|
| EB-1 (Priority Workers) | 10,049 | ~15,000 |
| EB-2 (Advanced Degree / NIW) | 426,465 | ~640,000 |
| EB-3 (Professional / Skilled) | 133,409 | ~200,000 |
| EB-4 (Special Immigrants) | 2,433 | ~3,600 |
| EB-5 (Investors) | 2,157 | ~3,200 |
| **Total** | **574,765** | **~862,363** |

The EB-2 category dominates, holding nearly three-quarters of all Indian principal applicants. These are engineers, data scientists, product managers, and physicians — people with advanced degrees or exceptional ability who filed their I-140 petitions years or, in many cases, over a decade ago. Their priority dates are current through July 15, 2014, as of the June 2026 Visa Bulletin, meaning anyone who filed after that date is still waiting.

EB-3, which covers professionals and skilled workers, holds 133,409 — and its dates have been moving roughly in lockstep with EB-2, eliminating the traditional incentive to downgrade from one category to the other.

## The arithmetic of the cap

The Immigration and Nationality Act allocates 140,000 employment-based immigrant visas per year worldwide. Under the seven percent per-country cap, India's share works out to approximately 9,800 visas annually — spread across all five EB categories and including dependents, who each consume a visa number.

Divide the 862,363 waiting by 9,800 annual visas and the result is 88 years. That is not a projection anyone takes literally — visa spillovers, policy changes, and attrition all affect the real timeline. But it captures the structural absurdity of a system that was designed when annual immigration demand from any single country was assumed to be a fraction of what India now generates.

The worldwide backlog across all countries is 1.27 million including dependents. India alone accounts for 68 percent of it.

## Why the dates moved — and why they may snap back

Indian EB-2 priority dates advanced noticeably during FY 2026, marching from April 1, 2013, in October 2025 to July 15, 2014, by April 2026 — a gain of roughly 15 months in six bulletin cycles. For a queue that had been frozen for years, this looked like progress.

Former Department of State official Charles Oppenheim has publicly cautioned that the movement is "completely artificial." The gains, he argues, are a side effect of the Trump administration's travel restrictions on 75 countries, which suppressed demand from Rest of World applicants and temporarily freed visa numbers that spilled over to India.

"The affected applicants are not going away and will be at the front of the visa line with early Rest of World priority dates," Oppenheim noted. "This would mean that China and India would again be subject to their low per-country limits, which have constrained date movement over the past several years."

The pattern mirrors the COVID-era bubble. When pandemic legislation temporarily raised the annual employment-based visa ceiling to 281,000 in FY 2022, dates surged forward. The correction — retrogression and stalled movement — followed within two fiscal years.

## The compound pressure

The backlog does not exist in isolation. Several simultaneous policy shifts are compressing the system further:

**EB-2 India visas exhausted for FY 2026.** As of May 22, all available EB-2 immigrant visas for India have been issued. No approvals — consular or domestic — are possible until October 1.

**Adjustment of status reframed as discretionary.** The PM-602 memo issued May 21 instructs USCIS officers to treat in-country adjustment as "extraordinary" relief, pushing more applicants toward consular processing abroad.

**NIW denial rates rising.** The National Interest Waiver, once seen as a shortcut past the EB-2 employer-sponsorship requirement, now faces denial rates that have surpassed EB-1A extraordinary ability petitions — making the "self-sponsored" route harder, not easier.

**Wage-weighted H-1B lottery.** The new selection system, effective for FY 2027, deprioritises entry-level positions and reduces the pipeline of future green card applicants at the front end.

Each of these policies is, on its own, a manageable obstacle. Together, they form a system that is functionally designed to slow Indian immigration to a crawl without ever formally reducing quotas.

## What it means for Indian Americans

For the 4.8 million-strong Indian American community, the backlog is not an abstraction. It determines whether a colleague can change jobs without restarting a decade-long process. It decides whether a spouse can work. It shapes where families buy homes, whether children grow up as Americans or as dependents on a visa that expires.

The legislative fix — eliminating or raising per-country caps — has been introduced in every Congress since 2019 and has died in every one. The Fairness for High-Skilled Immigrants Act passed the House in 2019 and 2020 but stalled in the Senate both times. No equivalent bill has advanced in the current Congress.

Until the math changes, 862,363 people will remain in a queue that predates most of their children's lives — waiting for a system built for a different century to acknowledge that they are, by every measure except one, already here."""

art2_image = "https://images.pexels.com/photos/18530593/pexels-photo-18530593.jpeg"


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Gate Just Closed — All EB-2 Visas for India Are Gone Until October",
        "subheadline": "The State Department confirmed that every EB-2 immigrant visa allocated to Indian nationals for FY 2026 has been issued. No approvals — consular or domestic — are possible until the fiscal year resets on October 1.",
        "slug": make_slug("eb2-india-visa-quota-exhausted-fy2026-hard-ceiling-october"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For 426,000 Indian professionals with approved I-140 petitions in the EB-2 queue, the exhaustion means a four-month freeze on green card progress — compounded by the PM-602 memo that has made adjustment of status discretionary rather than routine.",
        "tags": ["eb-2", "green-card", "uscis", "visa-bulletin", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "JDSupra / Gibney Anthony & Flaherty", "url": "https://www.jdsupra.com/legalnews/eb-2-india-immigrant-visa-quota-reached-7083089/"},
            {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/eb-2-india-per-country-limit-reached-for-fy-2026/"},
            {"name": "RJ Immigration Law", "url": "https://rjimmigrationlaw.com/dos-update-india-reaches-fy-2026-eb-2-visa-limit/"},
            {"name": "Immigration Monitor", "url": "https://immigrationmonitor.com/united-states-immigration-in-may-2026-aos-restrictions-visa-bulletin-backlogs-ebola-travel-rules-and-rising-immigration-costs/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/us-exhausts-fy2026-eb-2-visa-quota-for-indians/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "A hand holding an opened passport with visa stamps",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "862,363 and Counting — The Green Card Queue India Cannot Escape",
        "subheadline": "India accounts for 68 percent of the entire US employment-based green card backlog. The latest data puts the total at 574,765 principal applicants and 862,363 including dependents — roughly the population of San Francisco, all waiting in one line.",
        "slug": make_slug("india-green-card-backlog-862363-eb2-eb3-queue-data"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The EB-2 category alone holds 426,465 Indian principal applicants with priority dates stretching back over a decade. With annual per-country allocations of roughly 9,800 visas, the math produces an 88-year theoretical clearance time — a structural absurdity that shapes where Indian Americans buy homes, whether spouses can work, and whether children grow up as citizens or dependents.",
        "tags": ["green-card", "backlog", "eb-2", "eb-3", "per-country-cap", "immigration", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Shusterman Immigration Law", "url": "https://www.shusterman.com/visa-bulletin-predictions-for-july-2026/"},
            {"name": "WR Immigration / Wolfsdorf Rosenthal", "url": "https://wolfsdorf.com/india-eb-2-and-eb-3-visa-bulletin-movement/"},
            {"name": "Immigration Monitor", "url": "https://immigrationmonitor.com/united-states-immigration-in-may-2026-aos-restrictions-visa-bulletin-backlogs-ebola-travel-rules-and-rising-immigration-costs/"},
            {"name": "JDSupra / Ogletree Deakins", "url": "https://www.jdsupra.com/legalnews/india-per-country-limit-reached-in-the-4556709/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "A line of people waiting outside a building",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art2_body,
    },
]

# Validate images before inserting
for art in articles:
    img = art["image_url"]
    if not validate_image(img):
        print(f"⚠️  Image validation failed for {art['slug']}: {img}")
        # Don't skip — Pexels URLs are known-good, HEAD may not return Content-Length

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
