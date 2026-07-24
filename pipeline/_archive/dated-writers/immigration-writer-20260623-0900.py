#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
    {
        "id": str(uuid.uuid4()),
        "headline": "The Last Step to Citizenship Just Got 75% More Expensive. Indians Are at the Front of the Line",
        "subheadline": "A proposed DHS rule would push the naturalization fee toward $1,330 and scrap waivers for low-income applicants — a quiet toll on the diaspora's most popular off-ramp from the visa system.",
        "slug": make_slug("n400-citizenship-fee-hike-75-percent-waivers-eliminated-indians-naturalization"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Naturalization is the one immigration milestone Indians can usually control on their own timeline — and a 75% fee jump plus the loss of waivers raises the cost of crossing that finish line for a community that files among the most green-card-to-citizenship conversions in the country.",
        "tags": ["citizenship", "naturalization", "uscis", "fees", "green-card", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/us-plans-75-citizenship-fee-hike-indian-green-card-holders-may-face-costs-up-to-1-lakh"},
            {"name": "CBS News (via Outlook)", "url": "https://www.cbsnews.com/news/citizenship-application-fee-increase-dhs/"},
            {"name": "Newsweek (via Outlook)", "url": "https://www.newsweek.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28513546/pexels-photo-28513546.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "American flags against a clear sky, an emblem of the naturalization ceremony that ends the citizenship journey",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For most Indians who navigate the American immigration maze, citizenship is the part that finally feels within reach. The green-card wait is set by a backlog no individual can budge. The H-1B is a lottery. But the N-400 — the application to naturalize — is the rare step where, after five years as a permanent resident, the timeline is largely your own. Now the price of that last step is set to jump sharply.

The Department of Homeland Security has proposed raising the paper-based N-400 citizenship fee by roughly 75%, from $760 to $1,330. The online filing fee would climb from $710 to $1,280. Appeals get steeper too: the paper N-336 appeal fee would rise 78% to $1,475, and its online version 83% to $1,425. DHS frames the increases as cost recovery — aligning fees with what it calls the "full costs" of adjudication, including expanded screening and vetting now baked into the process.

### The waiver question

The number that should worry the diaspora most is not the headline figure. It is the proposed elimination of fee waivers for low-income applicants. Today, an applicant who cannot afford the fee can apply for a reduction or a full waiver. Strip that out, and naturalization becomes a flat, non-negotiable toll — one that lands hardest on the parts of the Indian community least visible in the H-1B-and-six-figures stereotype: elderly parents who immigrated through family categories, spouses without independent income, service and small-business workers who built green-card lives without tech salaries.

DHS itself acknowledged, per Newsweek, that the changes could delay applications for many lawful permanent residents. The rule carries a 60-day public comment period once it publishes in the Federal Register, so nothing is final — but the direction of travel is unmistakable.

### Why Indians feel this first

India sits among the top countries of origin for U.S. green-card holders, and the community is large enough that even a per-application increase aggregates into real money. As of January 2026, Ministry of External Affairs data counts roughly 6.08 million Indians in the United States — about 3.77 million persons of Indian origin and 2.31 million non-resident Indians. A meaningful share of the green-card holders among them are eligible to naturalize and, historically, do so at high rates. Citizenship ends the priority-date anxiety, unlocks the ability to sponsor relatives without per-country caps, and removes the lingering risk that a policy shift reshapes the rules mid-wait.

That last point matters more than usual right now. The same administration that has proposed this fee hike raised H-1B costs from $2,000 to $100,000 last September — a fee a Boston federal court struck down this month as unlawful — and has tightened adjustment-of-status practice, visa interview waivers, and student-visa rules. For an Indian permanent resident watching each rung of the ladder get pricier or shakier, naturalizing as soon as eligible has become the rational hedge. The fee increase raises the cost of that hedge precisely when demand for it is climbing.

### The math for a family

Consider a common diaspora household: two parents who became permanent residents through an adult child's petition, plus an adult relative. Three N-400s at the new paper rate would run close to $4,000, where today they would total roughly $2,280 — and if any of them currently relies on a waiver, the gap is the entire fee, not just the increase. Layer that onto biometrics, legal help for anyone with a complicated record, and the time cost of the longer processing DHS itself flags, and the "free part" of the immigration journey starts to look like another expense to budget years ahead.

### What to watch

The proposal is not law. The 60-day comment window is the moment for affected communities, advocacy groups, and immigration attorneys to weigh in, and prior fee rules have been narrowed or delayed after public pushback. For Indians who are already eligible to naturalize, the practical takeaway is blunt: if you have been postponing the N-400, the cost of waiting is no longer just paperwork inertia — it may soon be several hundred dollars more, with fewer ways to ask for relief. The smart move is to check eligibility now and file before the rule lands, rather than after."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS, Infosys and the 40% H-1B Drop: India's IT Giants Are Quietly Walking Away From the Visa",
        "subheadline": "New U.S. data shows the six biggest Indian IT firms took 40% fewer H-1Bs this year — and the strategy behind the fall says more about the diaspora's future than the lottery does.",
        "slug": make_slug("indian-it-firms-h1b-approvals-fall-40-percent-tcs-infosys-offshore-local-hiring"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For two decades the Indian IT services firm was the most reliable on-ramp to America for engineers straight out of college; as TCS, Wipro and peers pivot to offshore delivery and local U.S. hiring, that entry door is narrowing, reshaping how the next generation of Indian tech workers can even reach the country.",
        "tags": ["h1b", "tcs", "infosys", "it-services", "offshore", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/top-it-firms-h-1b-visas-slump-40-tcs-worst-hit-while-infosys-gains-11718000000000.html"},
            {"name": "Reuters (via Livemint)", "url": "https://www.reuters.com/"},
            {"name": "National Foundation for American Policy / Nearshore Americas", "url": "https://nearshoreamericas.com/indias-it-giants-scale-back-h-1b-visa-dependence/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804071/pexels-photo-6804071.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software developers collaborating at a workstation, the kind of role Indian IT firms increasingly fill offshore or with local U.S. hires",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The story of how Indians came to dominate the H-1B visa is, at its heart, the story of a handful of Indian IT services firms. For two decades, companies like Tata Consultancy Services, Infosys and Wipro ran the most efficient talent pipeline in the world: recruit engineers off Indian campuses, train them, and ship them to client sites in New Jersey, Texas and California on H-1B visas. That pipeline is now visibly contracting — and the latest U.S. data shows it is no longer just a cyclical dip.

According to official figures, India's six largest IT services firms — TCS, Cognizant, Infosys, HCL Technologies, Wipro and Tech Mahindra — were granted 11,041 H-1B visas as of 31 March 2026, down about 40% from roughly 18,469 the year before. The decline is steep, broad, and concentrated at the top: TCS saw the sharpest fall, dropping about 3,242 to roughly 2,885. Infosys was the outlier, the only firm in the group to post more approvals than the prior year, at 3,195 — the highest of the six.

### A choice, not just a casualty

It would be easy to read this purely as Trump-era restriction biting. The costs are real: the administration's September 2025 move to raise H-1B fees toward $100,000 per petition (since struck down by a Boston court, now under appeal), expanded social-media vetting, and tighter scrutiny of first-time petitions have all raised the price and friction of bringing a worker onsite. New filings at India's top firms have been falling for years — the National Foundation for American Policy found a roughly 56% reduction across the decade, with fresh approvals hitting a decade low of about 4,573 in FY2025.

But the more important truth is that the firms are choosing to need fewer visas. Faced with rising costs and political uncertainty, they have leaned into offshore delivery from India, automation, sub-contracting through U.S.-based vendors, and hiring Americans directly. Cloud computing and AI have made it possible to deliver more from Bengaluru and Hyderabad and less from a client's office in Ohio. The visa was always a means to an end — putting skilled hands on a project — and the firms have found cheaper, less politically exposed ways to do that.

### What it means for the next engineer

For the diaspora, this is the consequential part. An entire generation of Indian-Americans arrived via the services-firm route: a campus offer from TCS or Infosys, a few years of domestic projects, then an H-1B deputation to a U.S. site, and eventually a green-card filing and a life built in an American suburb. That escalator is slowing.

The replacement path runs through U.S. tech giants. Amazon, Microsoft, Meta, Google and Apple now dominate new H-1B approvals — for the first time occupying the top spots once held by Indian firms. But those companies hire differently: they recruit individuals, often those already in the U.S. on F-1 student visas and OPT, for specialized AI, cloud and chip roles. The implication for an engineer in India is stark. The old model let a firm sponsor you from Pune. The new model increasingly expects you to already be in America — typically having paid for a U.S. master's degree — before the best-sponsored jobs are within reach.

### Renewals hold, new doors close

There is a cushion. Continuing-employment H-1B approvals — renewals and extensions for workers already in the U.S. — remain comparatively stable, with USCIS clearing more than 291,000 in FY2025 at low denial rates. So Indians already on H-1B at these firms are not being pushed out en masse. The squeeze is almost entirely on the front door: first-time petitions, the path for someone who has never set foot in the U.S. workforce.

### The bottom line

The 40% drop is not a one-year accident. It is the visible edge of a structural shift in how Indian IT works, accelerated by U.S. policy but ultimately driven by economics and technology. For the diaspora, the message is to stop treating the services-firm H-1B as the default route to America. The reliable on-ramps now are a U.S. degree, a direct offer from a U.S. employer, or a niche skill valuable enough to justify the rising cost of sponsorship. The visa that built the Indian-American tech middle class is still there — but the companies that handed it out by the thousands are no longer reaching for it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Green-Card Numbers Have Nearly Halved in Two Years. The Data Tells a Bigger Story",
        "subheadline": "Lawful permanent residency for Indians fell from 127,000 in 2022 to under 67,000 in 2024 — a decline that long predates the headline fee fights and points to a slower, structural cooling of legal immigration.",
        "slug": make_slug("indian-green-card-recipients-halved-2022-2024-legal-immigration-decline-data"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Behind every statistic is a family deferring a move, a parent's petition stalling, or an engineer rethinking America — and the near-halving of Indian green cards in two years is the clearest sign yet that the diaspora's pipeline into permanent U.S. life is thinning, not just at the visa stage but at the finish.",
        "tags": ["green-card", "legal-immigration", "permanent-residency", "data", "diaspora", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/nation/2026/06/23/trump-immigration-policies-legal-immigration-data/"},
            {"name": "Office of Homeland Security Statistics (via Outlook Business)", "url": "https://www.outlookbusiness.com/news/us-plans-75-citizenship-fee-hike-indian-green-card-holders-may-face-costs-up-to-1-lakh"},
            {"name": "Cato Institute (David Bier, via USA Today)", "url": "https://www.cato.org/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7758569/pexels-photo-7758569.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Statue of Liberty on Liberty Island, long the symbol of America's promise to immigrants",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The loudest immigration fights of 2026 — the $100,000 H-1B fee, the wage-weighted lottery, the shuttered visa dropbox — are about the doors into America. A quieter set of numbers is about who actually makes it all the way through. And for Indians, those numbers are falling fast.

The count of Indians granted lawful permanent residency — a green card — dropped from 127,010 in 2022 to 78,070 in 2023, and then to 66,800 in 2024, according to Office of Homeland Security Statistics data. That is a near-halving in two years. Crucially, much of that decline began before the most aggressive recent policy changes took effect, which means it cannot be explained away as a single proclamation or a single administration's enforcement push. Something more structural is cooling the flow.

### A national trend, felt sharply by Indians

The broader picture, laid out in fresh reporting, is of legal immigration slowing across the board. International migration into the U.S. has decelerated enough that demographers attribute a renewed slowdown in big-city population growth to it. The Cato Institute's David Bier put the economic logic plainly: when the workforce stops growing, "that means less economic growth… which means higher costs for consumers." Immigrants, documented and undocumented, also pay into a Social Security trust fund projected to run short by 2032 — benefits most of them will never collect.

For the Indian diaspora, the trend bites in a specific way. Indians are overwhelmingly employment-based immigrants, concentrated in EB-2 and EB-3 categories where the per-country cap has produced a backlog measured in decades. When the overall system tightens — slower processing, fewer approvals, categories going "unavailable" on the visa bulletin — Indians, sitting at the very back of the longest line, feel it first and worst. The July 2026 visa bulletin made that vivid by marking EB-2 India "unavailable" for the rest of the fiscal year.

### Why the finish line, not just the start, matters

It is tempting to focus on entry — the lottery, the student visa, the consular interview. But the green-card number measures something different and arguably more important: conversion. It counts the people who entered on a temporary status and successfully turned it into a permanent stake in the country. A falling number means the system is not just admitting fewer people; it is converting fewer of those already here into permanent residents.

That has cascading effects for the diaspora. A green card is the prerequisite for naturalization, for sponsoring parents and siblings without the worst per-country waits, and for the stability that lets a family buy a home or start a business without one eye on visa renewals. Fewer green cards today means fewer new citizens in five years, and a thinner sponsorship pipeline for the relatives still in India. The decline compounds quietly down the generations.

### The signal beneath the noise

Policy reversals have softened some of 2026's sharpest edges. Many cancelled student visas were reinstated after lawsuits; the $100,000 H-1B fee was struck down in court; a judge halted parts of the asylum and work-permit freeze. But experts warn that even temporary restrictions do lasting damage by signaling that skilled migrants may not be welcome. That signal shows up in choices that never reach a courtroom: the Indian PhD who takes a post in Canada instead, the family that decides not to relocate, the engineer who renews in India rather than risk a re-entry at a U.S. consulate.

### What the diaspora should take from it

The headline battles will keep generating drama, and some will be won in court. But the green-card data is the trend line underneath the noise, and it points down. For Indians weighing their American future, the practical reading is sober: permanent residency is not just harder to start than it was three years ago — it is being granted to fewer people, including fewer Indians, each year. Anyone with a viable filing should keep their underlying status valid and their paperwork current, because in a contracting system, the applicants who survive are the ones who never give the process an excuse to stall. The promise on Liberty Island has not been revoked. It has simply become a great deal slower to redeem."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nInserted {len(inserted)}/{len(articles)} articles:")
for h in inserted:
    print(f"  - {h}")
