#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-28 12:00 UTC run"""
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


# ═══════════════════════════════════════════════
# ARTICLE 1: Sanctuary City Airports
# ═══════════════════════════════════════════════

article1_body = """Washington's immigration apparatus has a new pressure tactic, and this time the collateral damage is anyone who boards an international flight.

On Tuesday, Homeland Security Secretary Markwayne Mullin confirmed that the administration is "currently drawing up plans" to halt immigration and customs processing at major international airports located in so-called sanctuary cities. The targeted list reads like a directory of every airport Indian Americans actually use: JFK, Newark, San Francisco, Los Angeles, Chicago O'Hare, Boston Logan, Denver, Seattle-Tacoma, and Philadelphia.

The threat, first floated by Mullin in April during a funding dispute and now under "active consideration," would effectively shut down the ability of these airports to receive international flights. No CBP officers processing arrivals means no passport control, no customs clearance, and no entry — period.

## The Numbers Are Staggering

More than 50 million international travelers passed through the three New York-area airports alone last year. San Francisco International, the primary gateway for tech workers shuttling between Bangalore and the Bay Area, handles roughly 17 million international passengers annually. LAX processes even more.

Airlines for America, the trade group representing major carriers, warned that reducing customs staffing "would disrupt operations significantly for carriers, travelers and the flow of international cargo." The U.S. Travel Association, after meeting directly with Mullin, flagged what it called "devastating consequences" for communities dependent on international visitors.

## Why This Hits Indian Americans Hardest

The Indian diaspora in America is disproportionately concentrated in exactly the metropolitan areas on this list. The Bay Area, the New York–New Jersey corridor, Chicago, Seattle, Boston — these are not random sanctuary cities. They are the economic centers where H-1B holders work, where Indian families have built lives over decades, and where direct flights to Delhi and Mumbai actually land.

Consider the practical implications. An H-1B holder based in San Jose who needs to fly to Hyderabad for a family emergency and return through SFO — would they even be able to re-enter? A green card holder arriving at JFK from Delhi on Air India's direct route — would they be rerouted to… where, exactly? Houston? Miami? A connecting flight that turns a 16-hour journey into 24?

The administration has not spelled out logistics. There is no published timeline, no formal rulemaking, and no indication of how travelers already holding tickets would be handled. Mullin himself acknowledged "we're not initiating yet," but the signal is clear enough to create planning uncertainty for anyone with an international itinerary.

## The World Cup Collision

The timing is spectacularly bad. The 2026 FIFA World Cup kicks off next month across 16 American cities, with matches in New York, Los Angeles, San Francisco, Seattle, Boston, and Philadelphia — every single one a sanctuary jurisdiction on the target list. Millions of international visitors, including tens of thousands of Indian cricket-and-football fans, are expected to arrive through precisely these airports.

Shutting down international processing at these gateways during the World Cup would be, as one travel industry executive put it, "logistically insane." But the administration appears willing to use the threat as leverage against Democratic jurisdictions that have declined to cooperate with ICE enforcement operations.

## What Indian Americans Should Do Now

The honest answer is that there is nothing actionable yet — this remains a threat, not a policy. No executive order has been signed. No CBP officers have been withdrawn. But the trajectory of this administration's immigration posture has been to float ideas publicly, test the backlash, and then implement some version of the original plan.

Indian travelers with upcoming international trips through any of these airports should monitor developments closely. Those with flexibility on routing may want to identify alternative connection points (Dallas, Houston, Atlanta, and Miami are not on the sanctuary list). Employers sponsoring H-1B workers for international assignments should build contingency windows into travel schedules.

The broader pattern is unmistakable: immigration is no longer just about visas and forms. It is becoming a weapon in domestic political disputes, and legal immigrants are absorbing the shrapnel."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Flight Home Just Became a Political Weapon",
    "subheadline": "DHS is drawing up plans to halt customs processing at JFK, SFO, LAX, and six other airports where most Indian Americans land — and the World Cup starts in a month.",
    "slug": make_slug("dhs-sanctuary-city-airports-immigration-halt-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans are concentrated in exactly the sanctuary-city metros on DHS's target list — Bay Area, NYC-NJ corridor, Chicago, Seattle, Boston. Direct flights from India land at JFK, SFO, Newark, and LAX. Any disruption to international processing at these airports directly threatens the community's ability to travel, reunite with family, and return from visa stamping trips.",
    "tags": ["sanctuary-cities", "airports", "cbp", "dhs", "immigration-enforcement", "world-cup"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-drawing-up-plans-halt-immigration-customs-processing-sanctuary-city-airports-2026-05-27/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/05/27/us-news/dhs-head-doubles-down-on-plan-to-cripple-all-international-travel-into-airports-in-sanctuary-cities-including-nyc/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/dhs-eyes-suspension-of-international-traveler-processing-at-major-sanctuary-city-airports-in-the-usa-everything-you-need-to-know/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/mullin-weighs-using-airport-customs-leverage-against-sanctuary-cities"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/392265/pexels-photo-392265.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An international traveler at an airport terminal. Photo: Pexels",
    "body": article1_body
}

# ═══════════════════════════════════════════════
# ARTICLE 2: Five Dominos of Visa Stamping
# ═══════════════════════════════════════════════

article2_body = """If you are an Indian H-1B holder who has been refreshing the U.S. consulate appointment portal for months, watching your interview slot slide from December to March to June and now into 2027, you are not imagining things.

Visa stamping wait times in India have reached their worst levels in years — not because of one dramatic executive order, but because of five separate policy changes implemented within twelve months, each compounding the last. The result is a consular system that has effectively seized up for the majority of Indian work-visa holders, with no clear timeline for relief.

Here is what happened, in order, and why the combined effect is far worse than any individual change alone.

## Domino One: The Interview Waiver Window Shrank

In February 2025, the State Department quietly reduced the eligibility window for interview waiver renewals from 48 months to 12 months. If your previous visa expired more than a year ago, you were back in the in-person interview queue — even if you had renewed through the dropbox three times before without incident.

Immigration attorneys initially viewed it as manageable. In hindsight, it was the first crack.

## Domino Two: The Dropbox Disappeared

On September 2, 2025, the interview waiver program was gutted. Nearly every nonimmigrant visa category — H-1B, L-1, F-1, O-1, TN, J-1 — now requires an in-person interview regardless of renewal history. The age exemptions for children under 14 and adults over 79 were eliminated. The only categories still eligible for dropbox are diplomatic visas and a narrow slice of B-1/B-2 renewals.

Overnight, a massive volume of routine renewals flooded back into the in-person interview queue at consulates already running at limited capacity.

## Domino Three: Third-Country Processing Ended

Four days after the dropbox changes, the State Department closed another widely-used workaround. As of September 6, 2025, nonimmigrant visa applicants must schedule interviews only at the U.S. embassy or consulate in their country of nationality or residence.

The long-standing practice of booking faster appointments in Canada or Mexico was over. For Indian H-1B holders, this was devastating. India already had some of the longest consular wait times in the world, and third-country processing had served as the pressure valve for years.

## Domino Four: Social Media Vetting Crushed Throughput

Starting December 2025, the State Department expanded mandatory social media screening to H-1B and H-4 applicants. Every social media account used in the past five years must be set to public before the interview. Consular officers were directed to spend additional time per case reviewing online presence and digital footprints.

The operational impact was immediate. Posts in Mumbai and Hyderabad reportedly experienced significant drops in daily interview capacity. Consulates began canceling December and January appointments, rescheduling into later months. By late January 2026, all five U.S. consulates in India were showing "Not Available" for H-category visa stamping through the end of 2026 — with the first open slots appearing in May 2027.

Then in March 2026, the program expanded again to more than a dozen additional visa categories, including K-1 fiancé visas, R-1 religious worker visas, and even T and U visas for trafficking and crime victims.

## Domino Five: Adjustment of Status Became 'Extraordinary Relief'

On May 21, 2026, USCIS issued Policy Memorandum PM-602-0199, reclassifying adjustment of status — the standard path to a green card for people already in the U.S. — as "extraordinary relief." The memo instructs officers to view consular processing as the default pathway.

The memo does not change the statute. It does not define "extraordinary circumstances." It does not explain how pending I-485 applications filed before May 21 will be handled. But its practical effect is to potentially redirect hundreds of thousands of additional applicants into a consular system that is already gridlocked.

## The Compounding Effect

This is what most coverage misses. Before 2025, the consular system handled five streams of applicants: first-time filers, dropbox renewals, third-country applicants, family dependents, and immigrant visa cases. Two of those streams — dropbox and TCN — were routinely diverted away from in-person interview slots at home-country consulates.

After September 2025, all five streams pour into the same funnel. After December 2025, each interview takes longer because of expanded vetting. After May 2026, the funnel may absorb even more volume from the AOS redirects.

More demand. Reduced throughput. At the same posts. Simultaneously.

Someone whose H-1B stamping took two weeks in 2023 may now face wait times stretching well into 2027. The delays are not an accident or a temporary backlog. They are the predictable result of multiple policy changes designed to restrict access to legal immigration pathways, implemented within the same twelve-month window.

## What This Means for Indian H-1B Holders

The practical advice is grim but necessary. Do not travel internationally unless absolutely required — the risk of being stranded abroad for months is now real and documented. If you must travel, begin the appointment process immediately upon deciding, not upon booking flights. Congressional inquiries can sometimes help, but they cannot force a consulate to create interview slots that do not exist.

Employers sponsoring workers for international assignments should budget for multi-month absences and build contingency plans for remote work from India during the wait.

The political shorthand has always been that immigrants should "come the right way." What happens when the right way takes two years and counting?"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Five Policy Changes, Twelve Months, Zero Alternatives",
    "subheadline": "How a cascading series of consular rule changes broke visa stamping for Indian H-1B holders — and why wait times now stretch into 2027.",
    "slug": make_slug("five-dominos-visa-stamping-india-2027-wait"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders are the single largest group affected by the compounding consular processing changes. India's five U.S. consulates already had among the longest wait times globally; the elimination of dropbox renewals, third-country processing, and the addition of social media vetting have created a perfect storm where routine visa stamping — once a two-week errand — now risks months-long separation from jobs, homes, and families in America.",
    "tags": ["visa-stamping", "consular-processing", "h1b", "dropbox", "social-media-vetting", "india-consulates"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/why-is-my-us-visa-taking-so-long-how-five-consular-processing-changes-created-significant-delays-in-2026-and-why-the-new-aos-rule-may-increase-pressure-further/"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/expanded-social-media-vetting-delays-h-1b-visa-interviews/"},
        {"name": "Alcorn Law", "url": "https://alcorn.law/h-1b-visa-social-media-screening-2026-guide/"},
        {"name": "Khandelwa Law", "url": "https://khandelwalaw.com/h-1b-visa-stamping-processing-time-in-india-2026/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A passport held open — for many Indian H-1B holders, it now represents months of uncertainty. Photo: Pexels",
    "body": article2_body
}


# ═══════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
