#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-30 12:00 UTC run"""

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
        "headline": "The World Cup Kicks Off in Three Weeks. DHS Wants to Shut Down the Airports.",
        "subheadline": "Seven of eleven FIFA host cities are on the sanctuary city list. If Homeland Security pulls customs officers, millions of international visitors — including tens of thousands of Indian fans and families — may have nowhere to land.",
        "slug": make_slug("world-cup-sanctuary-city-airports-indian-fans-dhs"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans planning to host family visiting from India this summer, attend World Cup matches, or travel internationally through major hub airports face direct disruption. Newark — 12 miles from the World Cup final venue — processes 5 million returning Americans annually.",
        "tags": ["world-cup", "sanctuary-city", "airports", "dhs", "immigration", "fifa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/us-travel-group-warns-closing-newark-airport-international-travel-could-cost-8-2026-05-30/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/dhs-chief-warns-us-could-halt-international-flights-cargo-newark-over-immigration-2026-05-29/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/05/29/trump-sanctuary-city-airports-world-cup/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/these-fifa-host-cities-could-see-chaos-if-trump-shuts-down-customs-at-airports/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/270085/pexels-photo-270085.jpeg",
        "body": """The FIFA World Cup begins on June 11. The final takes place on July 19 at MetLife Stadium in East Rutherford, New Jersey — twelve miles from Newark Liberty International Airport.

On the same week that ticketholders are booking flights and sorting out hotel rooms, Homeland Security Secretary Markwayne Mullin went on Fox News and said his department is "currently drawing up plans" to stop processing international flights at airports in sanctuary cities. His reasoning: local law enforcement in places like northern New Jersey aren't helping federal immigration agents access detention facilities.

The U.S. Travel Association responded Friday with a blunt warning. Pulling customs officers from Newark alone would cost the American economy $8 billion annually. Five million Americans who transit through Newark each year would find their return flights "diverted or canceled." And with the World Cup weeks away, the damage to America's reputation as a destination for international visitors would be "significant and lasting."

## Seven of Eleven Host Cities Are Targets

Here is the uncomfortable math. Eleven American cities are hosting World Cup matches: Atlanta, Boston, Dallas, Houston, Kansas City, Los Angeles, Miami, New York/New Jersey, Philadelphia, San Francisco, and Seattle. The Department of Justice has labeled all but four of them — Atlanta, Dallas, Houston, and Kansas City — as sanctuary jurisdictions. That means seven host cities, including three with four of the nation's ten busiest international airports, are theoretically on the chopping block.

A Washington Examiner analysis found that the three most affected metro areas — New York, Los Angeles, and San Francisco — handle over 50 million international arrivals annually across their major airports. If customs processing disappears from JFK, LaGuardia, Newark, LAX, SFO, and SEA-TAC simultaneously, the international aviation system doesn't just bend — it breaks.

## Why Indian Americans Should Pay Attention

The World Cup disruption is the headline, but the fallout hits Indian Americans on multiple fronts.

**Summer travel season.** June through August is peak season for parents and relatives flying from India to visit family in the U.S. Mumbai, Delhi, and Hyderabad routes feed into exactly the airports under threat — Newark, JFK, SFO, LAX. A customs shutdown wouldn't just affect World Cup fans; it would affect every international arrival at those airports, including family reunion trips that were booked months ago.

**H-1B workers in transit.** Indian professionals on H-1B visas who travel internationally for work or personal reasons re-enter through these same airports. A customs suspension means they physically cannot re-enter the United States at those ports. The alternatives — flying into Dallas, Atlanta, or Miami and connecting domestically — assume those airports can absorb the overflow. They almost certainly cannot.

**Consular stamping returnees.** Thousands of Indians travel to India each summer for H-1B or H-4 visa stamping at U.S. consulates in Chennai, Hyderabad, Mumbai, Delhi, and Kolkata. They return to the U.S. through hub airports that are now at risk. If a stamped passport gets you to Newark but there's nobody to process you through customs, the stamp is worthless.

## Even the Cabinet Is Divided

Not everyone in the administration is on board. Transportation Secretary Sean Duffy pushed back during a congressional hearing last week: "We shouldn't shut down air travel in a state that doesn't agree with our politics." Acting Attorney General Todd Blanche called the option "extreme" but said it needed to be considered.

The tension reveals the policy for what it is — immigration enforcement leveraged as economic punishment against entire metropolitan regions. The collateral damage includes every international traveler, every cargo shipment, every airline schedule, and every business that depends on global connectivity.

## What to Watch

The immediate trigger is Newark. DHS has specifically threatened to reassign customs officers from the airport over a dispute about access to the Delaney Hall detention facility in New Jersey. If Mullin follows through, it would effectively shut Newark to international arrivals — three weeks before the World Cup final in the same metro area.

For Indian Americans, the practical advice is straightforward: monitor the situation daily, have backup routing plans for any international travel this summer, and understand that flights booked into sanctuary-city airports carry a new and unprecedented risk. The government that is stamping your visa and the government that is threatening to close the airport are the same government.

The World Cup was supposed to be a celebration of American openness. It may instead become a showcase of how immigration enforcement can be weaponized against the very infrastructure that makes global connection possible."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Safety Net Is Gone — H-4 Spouses Are Losing Work Authorization While USCIS Takes Months to Respond",
        "subheadline": "The 540-day automatic extension for H-4 EAD renewals was killed in October 2025. Now Indian spouses are being pulled off payrolls, losing driver's licenses, and filing mandamus lawsuits to force the government to process their paperwork.",
        "slug": make_slug("h4-ead-auto-extension-dead-indian-spouses-work"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "H-4 EAD holders are overwhelmingly Indian women married to H-1B workers. The end of automatic extensions disproportionately impacts Indian families in tech hubs like the Bay Area, Seattle, and New Jersey, where dual income is often essential to afford housing and childcare.",
        "tags": ["h4-ead", "work-authorization", "indian-spouses", "uscis", "mandamus"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Dickinson Wright Immigration Blog", "url": "https://immigration.dickinson-wright.com/2026-h1b-employer-punch-list/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/category/nonimmigrant-family/"},
            {"name": "Berry Appleman & Leiden LLP", "url": "https://www.bal.com/category/employment-based-visas/"},
            {"name": "USCIS Policy Alert", "url": "https://www.uscis.gov/policy-manual"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8400605/pexels-photo-8400605.jpeg",
        "body": """For years, the system worked like this: if you were an H-4 spouse with an Employment Authorization Document and you filed your renewal on time, your work authorization automatically extended for up to 540 days while USCIS got around to processing it. The extension was a lifeline. It kept people on payrolls, kept health insurance active, kept driver's licenses valid. It acknowledged what everyone knew — that USCIS was slow, and punishing applicants for the agency's own delays was absurd.

On October 30, 2025, the Interim Final Rule took effect. The 540-day automatic extension is dead. So is the 180-day extension that existed before it. H-4 EAD holders who file renewals on or after that date now wait with no safety net. When the current card expires, work authorization stops — even if the renewal application is sitting in a USCIS queue somewhere in Nebraska.

## The Numbers Behind the Crisis

USCIS processing times for Form I-765 — the Employment Authorization Document application — currently run between three and seven months, depending on the service center and the category. For H-4 EAD renewals specifically, the timelines have been erratic. Some applicants report receiving new cards in eight weeks. Others have been waiting five months with no update.

The problem is structural. Without the automatic extension, any processing delay beyond the card's expiration date creates a gap in work authorization. During that gap, the applicant cannot legally work. Their employer must take them off payroll. In many states, a lapsed EAD also means a lapsed driver's license, since the license was tied to the immigration document.

The Government Accountability Office has documented the systemic failures. The number of EAD applications surged 80% between 2015 and 2020, while USCIS staffing and processing capacity failed to keep pace. The GAO found the agency lacked a sustainable workforce recruiting plan, didn't request adequate funding, and had no reliable case management system. Those structural problems remain unfixed in 2026.

## Who This Hits Hardest

H-4 EAD eligibility is narrow by design. Only H-4 spouses whose H-1B partner has an approved I-140 immigrant petition, or who is in extended H-1B status under AC21, qualify for work authorization. This population is overwhelmingly Indian. Indian nationals account for roughly three-quarters of H-1B holders, and by extension, a similar share of H-4 EAD holders.

The typical profile: a woman with professional qualifications — often in tech, finance, healthcare, or education — who followed her husband to the United States and spent years building a career under H-4 EAD authorization. She contributes an estimated share of the $7.5 billion that H-4 spouses collectively add to the U.S. economy.

Now she's being told to stop working and wait. Not because she did anything wrong, not because her eligibility changed, but because the government eliminated the mechanism that accounted for its own processing delays.

## The Mandamus Option

Immigration attorneys are seeing a surge in mandamus lawsuit inquiries from H-4 EAD holders. A writ of mandamus asks a federal court to compel USCIS to adjudicate a pending application that has been unreasonably delayed. It is not cheap — legal fees typically run several thousand dollars — and it is not guaranteed. But for someone who has been off payroll for three months with no indication that USCIS will act, it may be the only lever available.

The Murthy Law Firm noted in a March 2026 advisory that mandamus may be an option "provided that the H-4 EAD renewal has been pending for longer than what a court might consider reasonable." The challenge is defining "reasonable" when the agency itself offers no binding timeline.

Some attorneys report that the mere filing of a mandamus complaint accelerates adjudication — USCIS would rather process the application than litigate. But that dynamic effectively means that access to work authorization now depends on the ability to afford a lawyer and a federal lawsuit.

## The Catch-22 Nobody Mentions

The elimination of automatic extensions exists in a policy landscape that is simultaneously hostile on multiple other fronts. USCIS has expanded discretionary denials using "country-specific factors" from the travel ban. Processing times for I-485 adjustment of status are running 8 to 14 months. The proposed end of "duration of status" for F-1 students would add yet another population competing for USCIS processing bandwidth.

For H-4 families, the math is straightforward and punishing. The green card backlog for EB-2 India stretches decades. The H-1B spouse will remain on temporary status for years. The H-4 spouse's ability to work depends entirely on a government agency that has been told to process faster, funded to stay the same, and restructured to do less.

## What Indian Families Can Do

**File early.** Submit the I-765 renewal as early as possible — USCIS accepts filings up to 180 days before the current EAD expires. Every day of lead time matters.

**Track processing times.** Check the USCIS processing times page weekly for your specific service center and category. If your case exceeds the posted range, you have a stronger foundation for expedite requests or mandamus action.

**Consider premium processing.** As of March 2026, premium processing is available for certain I-765 categories. Check whether your H-4 EAD category qualifies — the fee is steep but the 15-day guarantee may be worth it.

**Document the work authorization gap.** If your EAD expires before the renewal is processed, keep records of the gap — dates, employer communications, financial impact. This documentation supports both mandamus filings and potential future claims.

**Consult an immigration attorney.** The regulatory landscape changes frequently. An attorney familiar with H-4 EAD cases can advise on expedite requests, mandamus timing, and alternative strategies.

The elimination of automatic extensions was framed as ending a Biden-era policy. In practice, it transferred the cost of government inefficiency from the agency to the applicant — and the applicants absorbing that cost are disproportionately Indian women who were already navigating one of the most restrictive immigration pathways in the developed world."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
