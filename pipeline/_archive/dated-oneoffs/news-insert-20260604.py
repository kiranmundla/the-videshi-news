#!/usr/bin/env python3
"""
Insert 3 news articles (images already uploaded to Supabase storage).
"""
import json, os, requests
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

now = datetime.now(timezone.utc).isoformat()

# ─── ARTICLE BODIES ───

body1 = """The United States has officially exhausted its entire allocation of Employment-Based Second Preference (EB-2) immigrant visas for Indian nationals for Fiscal Year 2026, shutting down one of the most critical pathways to permanent residency for tens of thousands of highly skilled professionals already living and working in America.

The Department of State confirmed in a notice issued on May 22 that all available EB-2 visas allocated to applicants chargeable to India have been fully used, in coordination with US Citizenship and Immigration Services (USCIS). As a result, US embassies and consulates worldwide have been instructed not to issue additional EB-2 visas to Indian applicants for the remainder of the fiscal year. Processing will not resume until October 1, when FY 2027 begins and annual limits reset.

## Who Gets Hurt

The EB-2 category is the primary immigration channel for professionals holding advanced degrees or demonstrating exceptional ability — software engineers, data scientists, physicians, researchers, senior executives, and other specialists who form the backbone of America's knowledge economy. Under current law, the EB-2 allocation accounts for 28.6 percent of the worldwide employment-based immigration quota, while a per-country cap limits any single nation to no more than seven percent of total employment-based and family-sponsored visas combined.

For Indian nationals, who represent the single largest source country for employment-based immigration, this statutory cap has created a backlog stretching over a decade. The June 2026 Visa Bulletin shows the EB-2 India filing cut-off date sitting at July 15, 2014 — meaning applicants who filed twelve years ago are only now becoming eligible for final adjudication. USCIS has also announced it will use the more restrictive Final Action Dates chart for June, rather than the Dates for Filing chart, further tightening the pipeline.

## A Pattern That Repeats

This is not an anomaly. The EB-2 cap was exhausted for Indian applicants in FY 2024 (September 2024), FY 2025 (September 2025), and now FY 2026 — each year hitting the ceiling earlier. In FY 2026, the quota ran dry in May, the earliest exhaustion in recent memory. Immigration attorneys say the accelerating timeline reflects both rising demand from India's growing technology workforce and the structural inadequacy of a per-country cap system that treats India — with 1.4 billion people — the same as countries with populations a fraction of its size.

## What Applicants Can Do

For the estimated hundreds of thousands of Indian professionals caught in the backlog, the options are limited but not nonexistent. Applicants with approved I-140 petitions can continue to maintain their H-1B status and accrue time toward the six-year limit. Those eligible for a National Interest Waiver (NIW) under EB-2 may file independently without employer sponsorship, though the underlying backlog still applies. Some may explore EB-1 classification, which has a separate and typically more current priority date, though the qualifications are significantly more demanding.

The Biden-era executive actions that temporarily eased processing have not been renewed under the current administration, and legislative reform — including proposals to eliminate per-country caps entirely — remains stalled in Congress despite bipartisan support in previous sessions.

## The Diaspora Impact

For Indian families in the US, the EB-2 freeze is not an abstract policy matter. It determines whether a spouse can work, whether children age out of dependent status before a green card materialises, and whether a decade of building a life in America leads to permanence or forced departure. Advocacy groups including the Immigration Voice coalition have renewed calls for Congress to pass the EAGLE Act, which would phase out per-country caps over nine years, but the bill has not advanced in the current session.

The annual limits will reset on October 1, 2026, when FY 2027 begins. Until then, the pipeline is frozen — and the line just got longer.

*Sources: US Department of State, USCIS June 2026 Visa Bulletin, Berry Appleman & Leiden LLP, Manifest Law*"""

body2 = """The New York State Senate has adopted Resolution J1935, urging Governor Kathy Hochul to proclaim August 15, 2026, as India Independence Day in the State of New York — a formal legislative recognition that reflects the growing political weight of the Indian-American community in one of America's most influential states.

The resolution was sponsored by State Senator Jeremy Cooney, a Democrat from Rochester who made history in 2020 as the first Asian American elected to state office from upstate New York. Cooney, who was adopted from an orphanage in Kolkata and raised by a single mother in Rochester, has become one of the most prominent advocates for Indian-American interests in New York's legislature.

## What the Senators Said

During deliberations on the resolution, multiple senators offered remarks that went beyond pro-forma ceremony. Senator Joseph P. Addabbo Jr. quoted Mahatma Gandhi — "the future depends on what we do in the present" — calling the message an enduring inspiration for Indian Americans. Senator John C. Liu noted that India has been "a model of democracy for actually a lot longer than our country," and praised the Indian-American community's contributions across New York.

Senator Jeremy Zellner described the Indian-American community as "woven into the fabric of our everyday life" in his district. "They are our neighbours raising families here, working in critical professions, and helping shape the character of our region," he said.

Senator Toby Ann Stavisky called for continuing the "tradition of friendship" between India and the United States, noting that the similarities between the two democracies outweigh their differences.

## Why It Matters for the Diaspora

New York is home to one of the largest Indian-American populations in the Western Hemisphere, with particularly dense communities in Queens, Jersey City, and the wider metropolitan area. The resolution explicitly acknowledged the community's contributions to STEM, business, the arts, philanthropy, defence, and government at all levels — a legislative record that carries weight in future policy debates around immigration, trade, and cultural recognition.

The Consulate General of India in New York issued a statement expressing "sincere gratitude" to Senator Cooney and the full chamber, noting that the senators' remarks reflected the "deep people-to-people bonds" between the two nations and the "growing role of the Indian-American diaspora in strengthening communities across New York."

## A Growing Pattern of Recognition

The resolution follows a broader trend of American legislatures formally recognising Indian heritage. New York adopted a similar resolution commemorating the 75th anniversary of the Indian Constitution in November 2025, also sponsored by Cooney. Several other states, including New Jersey, Texas, and California, have adopted their own Indian Independence Day proclamations in recent years, reflecting the community's demographic growth and increasing civic engagement.

India will celebrate its 80th Independence Day on August 15, 2026. For the nearly 4.5 million Indian Americans across the country — and the estimated 700,000 in New York State alone — the Senate resolution is not just a symbolic gesture. It is a legislative acknowledgement that the community's presence has moved from the margins to the mainstream of American public life.

*Sources: New York State Senate Resolution J1935, The Indian EYE, hi INDiA, India Weekly*"""

body3 = """India's consumer watchdog has imposed its most high-profile penalties yet under the country's dark patterns framework, fining edtech giant PhysicsWallah ₹5 lakh and cybersecurity firm McAfee Software India ₹1 lakh for deploying manipulative interface designs that steered users into purchases and subscriptions they did not explicitly choose.

The Central Consumer Protection Authority (CCPA), in orders issued on Wednesday by Chief Commissioner Nidhi Khare and Commissioner Anupam Mishra, directed both companies to immediately discontinue the identified practices and ensure consumers can make decisions "without manipulation or pressure."

## What PhysicsWallah Did

The CCPA took suo motu cognisance of practices on PhysicsWallah's platform and identified three distinct violations — all textbook examples of the design tricks that India's 2023 dark patterns guidelines were written to prevent.

The most striking finding involved a ₹10 donation to the PW Foundation that was automatically pre-selected during checkout and bundled into the final payment amount without explicit consumer consent. This practice — known as "basket sneaking" in regulatory parlance — meant users were paying for something they never chose.

When users attempted to remove the ₹10 charge, the platform displayed emotionally manipulative messages about children's education, healthcare, and marriages — a technique classified as "confirm shaming," designed to make consumers feel guilty about protecting their own wallets.

The regulator also flagged courses advertised as "free" that required users to hand over their mobile numbers and email addresses before access was granted. The CCPA noted that the course material was identical across accounts, meaning the personal data collection served no functional purpose for delivering the service.

The authority emphasised that a large proportion of PhysicsWallah's users are students, including minors, making the violations "particularly significant" from a consumer protection standpoint.

## What McAfee Did

McAfee's violations were simpler but no less calculated. The CCPA examined the company's subscription renewal interface and found it presented two options to users: "Renew Now" and "Accept Risk." The second option — the one that would let a consumer decline renewal — was framed as a dangerous choice, implying that users would be exposed to immediate cybersecurity threats if they did not continue paying.

The regulator identified four overlapping dark patterns in McAfee's interface: confirm shaming (making non-renewal feel irresponsible), interface interference (giving visual prominence to the renewal button), trick questions (using emotionally loaded language instead of neutral options), and forced action (not providing a clearly visible opt-out).

## Why the Fines Are Small but the Signal Is Loud

At ₹5 lakh and ₹1 lakh respectively, the penalties are trivially small for companies of this scale — PhysicsWallah was valued at over $1 billion at its last funding round, and McAfee is a global cybersecurity corporation. But regulatory observers say the real significance lies in the precedent.

These are among the first enforcement actions under the Guidelines for Prevention and Regulation of Dark Patterns, 2023 — a framework that India adopted ahead of most countries. The guidelines define 13 categories of dark patterns, from drip pricing and subscription traps to bait-and-switch and disguised advertising. The CCPA's willingness to act suo motu, without waiting for consumer complaints, signals that the regulator intends to be proactive rather than reactive.

For India's booming edtech, SaaS, and e-commerce sectors — where pre-ticked checkboxes, forced data collection, and guilt-tripping cancellation flows are standard practice — the message is clear: the 2023 rules have teeth, and the regulator is now using them.

## What It Means for NRIs

For Indian professionals working in technology abroad, the CCPA's enforcement is a notable development. India is building a consumer protection regime that in some areas now exceeds what exists in the US, where the Federal Trade Commission has pursued dark patterns cases but Congress has not enacted comprehensive legislation equivalent to India's 2023 guidelines. The approach offers a model that other countries, including those with large Indian diaspora populations, may follow.

*Sources: CCPA Order, Storyboard18, Livemint, Exchange4Media, BizzBuzz*"""

# ─── ARTICLES ───

articles = [
    {
        'headline': 'The US Just Froze EB-2 Visas for Indians. The Backlog Now Stretches Back to 2014.',
        'subheadline': 'All employment-based second-preference visas for Indian nationals have been exhausted for FY 2026. Processing will not resume until October.',
        'slug': 'us-eb2-visa-limit-exhausted-indians-fy2026-october-green-card-backlog',
        'body': body1,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': now,
        'is_editorial': False,
        'image_url': f'{SUPABASE_URL}/storage/v1/object/public/article-images/us-eb2-visa-limit-exhausted-indians-fy2026-october-green-card-backlog.jpg',
        'image_attribution': 'The Videshi',
        'sources': json.dumps(['US Department of State', 'USCIS Visa Bulletin June 2026', 'Berry Appleman & Leiden LLP', 'Bharat Horizon']),
    },
    {
        'headline': "New York's Senate Just Voted to Recognise India's Independence Day. The Man Behind It Was Adopted From Kolkata.",
        'subheadline': 'Resolution J1935 urges the governor to proclaim August 15, 2026, as India Independence Day across New York State. The sponsor, Jeremy Cooney, is the first Asian American elected to state office from upstate New York.',
        'slug': 'new-york-senate-resolution-india-independence-day-august-2026-jeremy-cooney',
        'body': body2,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': now,
        'is_editorial': False,
        'image_url': f'{SUPABASE_URL}/storage/v1/object/public/article-images/new-york-senate-resolution-india-independence-day-august-2026-jeremy-cooney.jpg',
        'image_attribution': 'The Videshi',
        'sources': json.dumps(['New York State Senate', 'The Indian EYE', 'hi INDiA', 'India Weekly']),
    },
    {
        'headline': 'India Just Fined PhysicsWallah for Sneaking a ₹10 Donation Into Every Checkout. McAfee Got Caught Too.',
        'subheadline': 'The consumer watchdog penalised both companies for dark patterns \u2014 auto-added charges, guilt-tripping cancellation screens, and data harvesting disguised as free courses.',
        'slug': 'ccpa-fines-physicswallah-mcafee-dark-patterns-consumer-protection-india',
        'body': body3,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': now,
        'is_editorial': False,
        'image_url': f'{SUPABASE_URL}/storage/v1/object/public/article-images/ccpa-fines-physicswallah-mcafee-dark-patterns-consumer-protection-india.jpg',
        'image_attribution': 'The Videshi',
        'sources': json.dumps(['CCPA', 'Storyboard18', 'Livemint', 'Exchange4Media', 'BizzBuzz']),
    }
]

for art in articles:
    url = f'{SUPABASE_URL}/rest/v1/p2_articles'
    r = requests.post(url, headers=HEADERS, json=art, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f'✓ Inserted: {art["headline"][:70]}... (id={art_id})')
    else:
        print(f'✗ Insert failed ({r.status_code}): {r.text[:300]}')

print("\nDone.")
