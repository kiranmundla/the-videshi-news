#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 21:30 batch
Topics: 1) Kevin Warsh sworn in as new Fed Chair — what it means for India and NRIs
        2) H-1B registrations plunge 38.5% for FY2027 — the immigration pipeline for Indians narrows from every direction
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "60"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Kevin Warsh Is the New Fed Chair. For India's Economy and Every NRI in America, the Consequences Are Already Arriving.
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("kevin-warsh-new-fed-chair-india-nri-rupee-rates-economy")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Kevin Warsh Is the New Fed Chair. For India's Economy and Every NRI in America, the Consequences Are Already Arriving.",
        "subheadline": "On Friday, Kevin Warsh was sworn in as the 17th Chair of the Federal Reserve in a White House ceremony — the first time a Fed chair has been sworn in at the White House in 40 years. He inherits an economy that looks nothing like the one he was nominated to manage: US inflation has climbed to 3.8 percent, mortgage rates have hit 6.51 percent, money markets are pricing in a rate hike for the first time since 2023, and the 10-year Treasury yield is at its highest level since January 2025. For India, which has seen $22 billion in foreign portfolio investment flee in under three months, a rupee weakening past ₹94 to the dollar, and an RBI that may now be forced to hike rates to defend the currency, the new Fed chair is not a distant Washington story. It is the story of whether your home loan EMI goes up, whether your NRI deposits earn more or less, whether the remittance you send home buys more or fewer rupees, and whether the US mortgage you are paying on a Bay Area apartment gets more expensive before it gets cheaper.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "The Fed chair matters to every NRI in two directions simultaneously. In America, Warsh's decisions will determine mortgage rates — which just hit 6.51 percent, the highest since August 2025. For the Indian tech worker in the Bay Area paying $4,500 a month on a variable-rate mortgage, or the young professional in New Jersey trying to buy their first home, Warsh's first FOMC meeting in June could mean the difference between rates stabilising and rates climbing further. The housing market in the US is the most active spring in years, but affordability has deteriorated since mid-February. A rate hike would freeze it. In India, the consequences flow through the rupee. A hawkish Fed — rates held steady or hiked — strengthens the dollar, which weakens the rupee, which makes oil imports more expensive, which drives up petrol and cooking gas prices, which raises inflation, which forces the RBI to hike its own rates, which raises EMIs on home loans and car loans for every family in India. The $22 billion in foreign investment that has left Indian markets in three months is partly driven by exactly this dynamic: when US rates are high and rising, global capital flows to the dollar and away from emerging markets. NRI fixed deposits, which currently offer 7-7.5 percent for dollar deposits, may see rates adjusted. Remittances — India's single largest source of foreign exchange at over $100 billion annually — buy more rupees when the rupee is weak, but the purchasing power of those rupees is eroded by the inflation that caused the weakness in the first place. There is no version of the Warsh era that is simple for Indians on either side of the ocean.",
        "tags": ["Fed", "Kevin Warsh", "Federal Reserve", "interest rates", "India", "rupee", "NRI", "mortgage", "RBI", "inflation", "Trump", "economy", "FPI outflows", "EMI", "housing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Warsh elected chair of U.S. Fed's rate-setting committee", "url": "https://www.reuters.com/business/finance/warsh-elected-chair-us-feds-rate-setting-committee-2026-05-22/"},
            {"name": "CNN — Kevin Warsh sworn in as Fed chair at pivotal moment for US economy", "url": "https://www.cnn.com/2026/05/22/economy/kevin-warsh-fed-chair-sworn-in/index.html"},
            {"name": "Realtor.com — Kevin Warsh Is the New Fed Chair: What It Means for Mortgage Rates and Housing", "url": "https://www.realtor.com/research/kevin-warsh-fed-chair-housing-mortgage-rates/"},
            {"name": "PaisaKawach — New Fed Chair, Iran Talks Stall Again, and India Bleeds $22 Billion — Weekend Briefing", "url": "https://paisakawach.com/news/new-fed-chair-iran-talks-india-markets-weekly-briefing-may-23-2026"},
            {"name": "StockTwits — Kevin Warsh Will Be Sworn In As Fed Chair — Bond Markets Aren't Giving Him a Grand Welcome", "url": "https://stocktwits.com/news/kevin-warsh-fed-chair-bond-markets"}
        ]),
        "score_total": 90,
        "status": "published",
        "published_at": now,
        "body": """On Friday afternoon, Kevin Warsh placed his hand on a Bible in the East Room of the White House and was sworn in as the 17th Chair of the Federal Reserve. Justice Clarence Thomas administered the oath. Warsh's wife, Jane Lauder — heiress to the Estée Lauder fortune — stood beside him. President Trump watched from feet away, having chosen to host the ceremony at the White House rather than at the Federal Reserve building, a break from tradition that had not occurred in 40 years.

"I want Kevin to be totally independent," Trump said at the ceremony. "Don't look at me, don't look at anybody, just do your own thing and do a great job."

Hours later, at a rally, Trump told supporters that interest rates would come down "very quickly."

The contradiction between those two statements is the defining tension of the Warsh era — and it is a tension that will determine interest rates, currency values, mortgage costs, and investment flows that touch the lives of 1.4 billion Indians and 4.5 million Indian Americans.

## The Economy He Inherits

When Trump nominated Warsh in late January, the US economy looked very different. Inflation was near the Fed's 2 percent target. Markets were pricing in multiple rate cuts. AI euphoria was driving stocks to records. The appointment seemed like a gift: Warsh would arrive, preside over rate cuts, and take credit for a booming economy.

Then the Iran war began. Oil prices spiked 45 percent. US gasoline prices surged 21 percent. Headline CPI inflation climbed from 2.4 percent to 3.8 percent — the highest in three years. The 10-year Treasury yield hit 4.56 percent, its highest level since January 2025. The 30-year yield crossed 5.08 percent — a 31-month high. Mortgage rates climbed to 6.51 percent, up 53 basis points in just 12 weeks.

Money markets have now fully priced in at least one rate hike in 2026. This is the exact opposite of what anyone expected five months ago. Warsh was supposed to be the chair who cut rates. Instead, he may be the chair who raises them.

His first FOMC meeting is in three weeks. The committee he inherits is already signalling caution: three governors logged soft dissents at the last meeting in favour of future hikes, deliberately putting their data-driven views on record before Warsh arrived. Jerome Powell, whom Warsh replaces as chair but who remains on the board as a governor, is staying specifically to safeguard institutional independence — an almost unprecedented arrangement.

The Senate confirmed Warsh by a vote of 54 to 45, the most divisive confirmation of a Fed chair in modern history. Only one Democrat — John Fetterman of Pennsylvania — crossed the aisle.

## Why India Cannot Ignore This

The Federal Reserve sets interest rates for the United States. But in a world where the dollar is the reserve currency, where oil is priced in dollars, and where global capital flows follow the yield differential between US and emerging market assets, the Fed chair's decisions ripple through every economy on earth. India, as the world's fifth-largest economy and a country that imports 85 percent of its crude oil, is among the most exposed.

Here is how the transmission works:

If Warsh holds rates steady or signals a hike, the dollar strengthens. A stronger dollar means the rupee weakens. A weaker rupee means India pays more for oil imports — which are priced in dollars. Higher oil costs widen India's current account deficit, which puts further downward pressure on the rupee. The Reserve Bank of India may then be forced to raise its own interest rates to defend the currency and contain imported inflation. Higher RBI rates mean higher EMIs on home loans, car loans, and personal loans for hundreds of millions of Indian households.

This is not a hypothetical chain of events. It is already happening. The rupee has weakened past ₹94 to the dollar — down more than 10 percent in 12 months. Foreign portfolio investors have pulled $22.2 billion out of Indian equities in under three months, exceeding the entire record annual outflow of 2025. Brent crude is at $107 per barrel. The RBI, which cut its repo rate to 5.25 percent in December 2025, is now facing calls from analysts — including Emkay Global — to reverse course and hike rates as early as the next monetary policy committee meeting.

India's chief economic advisor has publicly criticised private companies for failing to invest despite strong profitability. Reliance Industries, India's largest company, is deploying capital not in India but in the United States — building what Trump has called "the first refinery in 50 years" in America. Capital that should be anchoring India's growth cycle is flowing in the wrong direction.

## What NRIs in America Feel Directly

For Indian Americans, the Warsh appointment hits on multiple fronts simultaneously.

Mortgage rates are the most immediate. At 6.51 percent, the 30-year fixed mortgage rate is at its highest point since August 2025. For the Indian tech worker in Seattle who has been waiting for rates to drop before buying a home, or the couple in the Bay Area whose adjustable-rate mortgage is about to reset, Warsh's first FOMC decision matters in the most personal way possible. A rate hike would push mortgage rates toward 7 percent — a level that would freeze an already strained housing market.

The housing market itself is showing resilience — this is the most active spring for home sales since 2022, with new listings and contract signings up nationally. But affordability has deteriorated since mid-February, and any further rate increase could tip the balance. Realtor.com's analysis notes that even if Warsh eventually moves toward cuts, it would not automatically lower mortgage rates: if markets believe cuts are politically motivated rather than data-driven, long-term yields could actually rise as inflation expectations get priced in.

For NRIs sending money home, the math is paradoxical. A weaker rupee means each dollar buys more rupees — which looks good on paper. But the inflation that caused the rupee's weakness erodes what those rupees can actually buy. Your parents' grocery bill in Hyderabad or Pune is higher. Their cooking gas is more expensive. The purchasing power of the remittance you send has not improved as much as the exchange rate suggests.

NRI fixed deposits — a popular savings vehicle that currently offers 7 to 7.5 percent for dollar-denominated deposits — may see rate adjustments depending on how the RBI responds. If the RBI hikes rates to defend the rupee, NRI deposit rates could rise. But the conditions that produce those higher rates — inflation, currency weakness, capital flight — are not conditions any depositor should celebrate.

## The Independence Question

The most consequential question about the Warsh era is not what he will do with rates. It is whether he will do what the data demands or what the president wants.

Warsh served as a Fed governor from 2006 to 2011, where he was known as an inflation hawk. During his confirmation hearings, he appeared to shift toward a more dovish posture — advocating for the possibility of rate cuts. Critics argued the shift was designed to align with Trump's well-known preference for lower rates. Supporters argued it reflected a genuine reading of the economic data at the time of his nomination.

The data has since moved decisively against cuts. Inflation at 3.8 percent, with gasoline prices up 21 percent and food prices elevated, does not support lower interest rates by any conventional central banking framework. Governor Christopher Waller said this week that the next rate move is "just as likely to be a raise as a cut." JP Morgan expects rates on hold through all of 2026 with possible hikes in early 2027.

If Warsh holds firm and lets the data guide his decisions, he establishes credibility — but risks Trump's public wrath. If he pushes for cuts despite the data, he risks the Fed's institutional credibility, which could trigger a bond market sell-off that would raise long-term rates and mortgage costs even as short-term rates fall.

As Realtor.com's chief economist put it: "A chair that is not data-dependent cannot be independent. Those are not two separate qualities. They are the same quality."

## What Comes Next

Warsh's first FOMC meeting is in June. Markets will parse every word of his first press conference for signals about whether the Fed is tilting toward a hike, a hold, or — against all odds — a cut. The bond market has already made its view clear: the 10-year yield at 4.56 percent and money markets pricing in a hike suggest that investors expect rates to stay elevated or rise.

For India, the next three months are a gauntlet. The new Fed chair. Oil above $100. An Iran deal that may or may not materialise. A rupee under structural pressure. An RBI that may be forced to reverse its rate-cutting cycle. FPI outflows that show no sign of stopping. And a global capital environment where the United States — with its AI boom, its strong dollar, and its rising yields — is sucking investment away from every emerging market, India included.

For NRIs, the calculus is simpler and more personal. If you have a mortgage, watch the June FOMC meeting. If you send money home, understand that a weak rupee is a symptom of conditions that hurt your family's purchasing power even as the exchange rate flatters your transfer. If you hold NRI deposits, the interest rate may rise — but so will the inflation it is trying to compensate for. And if you are investing in Indian equities from abroad, know that the Nifty at 20 times forward earnings is cheaper than it has been in years — but cheap can get cheaper when $22 billion is walking out the door.

The Federal Reserve does not set policy for India. But in a world where the dollar is king, where oil is priced in dollars, and where global capital follows the yield, the person who sits in the Fed chair's seat in Washington determines the cost of living in Mumbai, the value of the rupee in Dubai, and the mortgage payment in Cupertino. Kevin Warsh now sits in that seat. What he does with it will be felt by Indians on every continent.
"""
    })
else:
    print(f"  ⚠ Skipping Warsh Fed Chair article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: H-1B Registrations Just Dropped 38.5 Percent. The Immigration Pipeline for Indians Is Narrowing From Every Direction.
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("h1b-registrations-drop-38-percent-fy2027-indians-immigration")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "H-1B Registrations Just Dropped 38.5 Percent. The Immigration Pipeline for Indians in America Is Narrowing From Every Direction.",
        "subheadline": "On Thursday, USCIS released its FY2027 H-1B registration data: the number of applications plummeted from 343,981 to 211,600 — a 38.5 percent drop. The agency framed it as a crackdown on 'mass, low-wage registrations.' Indians, who account for 71 percent of all approved H-1B applications, are the most affected group. One day later, USCIS announced that green card applicants must now leave the country to apply — ending the Adjustment of Status process that allowed people to stay in the US while waiting. And on Saturday, Secretary of State Rubio, visiting India, announced an 'America First' visa policy that 'prioritises business professionals.' In the span of 72 hours, the three pillars of the Indian tech immigration pipeline — entry via H-1B, transition to green card, and the promise that you could build a life while you waited — have all been weakened simultaneously. For the estimated 500,000 Indians in the green card backlog and the hundreds of thousands who apply for H-1B visas each year, this is not a policy adjustment. It is a structural contraction of the path that brought a generation of Indian engineers, doctors, and researchers to America.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "This story is the story of the Indian immigration pipeline — and that pipeline is narrowing from every end simultaneously. At the entry point: H-1B registrations down 38.5 percent, with USCIS now favouring US master's degree holders (71.5 percent of selections, up from 57 percent) and higher-wage applicants (only 17.7 percent in the lowest wage category). The $100,000 minimum salary proclamation Trump signed in September 2025 has already filtered out a significant portion of the applications that Indian IT services companies traditionally filed. At the middle: the Adjustment of Status elimination means that the years-long wait for a green card — already the longest for Indians, with some EB-2 and EB-3 applicants waiting since 2012 — can no longer be spent in the US. The process that allowed you to work, pay taxes, enrol your children in school, and build a life while waiting has been reclassified as 'extraordinary relief.' At the output: Rubio's 'America First' visa policy in India sounds welcoming on paper, but it fast-tracks business visitors, not immigrants. The message to the Indian tech worker who has been in America for a decade, whose children were born here, and who is still waiting for a green card: you are welcome to visit, but staying is no longer the default assumption. Zoho CEO Sridhar Vembu responded to the green card change on X, calling for Indian tech companies to build in India rather than sending talent abroad. His post went viral — because it articulated what many Indians in America are beginning to feel: the system that invited them is now pushing them out, and perhaps the answer is to stop trying to enter a door that keeps closing.",
        "tags": ["H-1B", "immigration", "USCIS", "green card", "NRI", "Indian Americans", "tech workers", "Trump", "visa", "Sridhar Vembu", "Rubio", "adjustment of status", "backlog", "FY2027"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "DevDiscourse/PTI — H-1B registrations down in FY27; more approvals for higher degrees, salaries", "url": "https://www.devdiscourse.com/article/headlines/3918409-h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries"},
            {"name": "The Hindu Business Line — New USCIS policy could force H-1Bs seeking Green Cards to apply from home countries", "url": "https://www.thehindubusinessline.com/news/world/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69612345.ece"},
            {"name": "The Raisina Hills — Trump's New Green Card Rule Leaves H-1B Indians in Limbo", "url": "https://theraisinahills.com/trumps-new-green-card-rule-leaves-h1b-indians-in-limbo/"},
            {"name": "Bhaskar English — US H-1B, Green Card Rules Tightened — Indian Professionals Concerned", "url": "https://bhaskarenglish.in/us-h1b-green-card-rules-tightened-indian-professionals-concerned/"},
            {"name": "Outlook Business — Trump Administration Ends US-Based Green Cards for Temporary Visa Holders", "url": "https://www.outlookbusiness.com/economy-and-policy/trump-administration-ends-us-based-green-cards-for-temporary-visa-holders"}
        ]),
        "score_total": 91,
        "status": "published",
        "published_at": now,
        "body": """In the span of 72 hours this week, three things happened that, taken together, represent the most significant contraction of the Indian immigration pipeline to America in a generation.

On Thursday, USCIS released its FY2027 H-1B registration numbers. The total dropped from 343,981 to 211,600 — a 38.5 percent decline. The agency celebrated the reduction, posting on X: "This data is a clear sign that the days of abusing the programme with mass, low-wage registrations are over."

On Friday, USCIS announced that green card applicants who are already living in the United States must now, as a default, return to their home countries to apply — effectively ending the Adjustment of Status process that has been the standard path to permanent residency for decades.

On Saturday, Secretary of State Marco Rubio arrived in India and announced an "America First" visa policy that would "prioritise professionals and business leaders."

Each of these developments was reported as a separate story. Together, they are one story — and it is the most consequential immigration story for Indians since the H-1B programme was created in 1990.

## The H-1B Contraction

The 38.5 percent drop in H-1B registrations is not a statistical blip. It is the intended result of multiple policy changes that have been stacking up since Trump returned to office.

In September 2025, Trump signed a proclamation requiring that H-1B petitions be accompanied by a minimum salary payment of $100,000. This single measure eliminated a significant proportion of the applications that Indian IT services companies — Infosys, TCS, Wipro, HCL — traditionally filed for entry-level and mid-level workers. The Indian IT outsourcing model, which depended on bringing workers to the US at competitive salaries and billing American companies a premium, has been structurally disrupted.

The numbers confirm this. USCIS reported that only 17.7 percent of all selected H-1B registrations for FY2027 were in the lowest wage category. In prior years, that proportion was significantly higher. The programme is being reshaped to favour higher-wage, higher-credential applicants — particularly those with US master's degrees, who now make up 71.5 percent of selections, up from 57 percent last year.

"We're approving more applicants with advanced degrees and higher salaries — especially those who studied at US universities," USCIS said. The subtext is clear: the H-1B is being narrowed from a broad pipeline that served the Indian IT industry into a selective filter for the most credentialed and highest-paid.

For the Indian student graduating from a US university with a master's in computer science, the odds have actually improved. For the mid-career engineer at an Indian IT company hoping to transfer to a US client site, the door is closing.

Indians account for approximately 71 percent of all approved H-1B applications in recent years. No other country comes close — China is a distant second. The 38.5 percent overall decline, applied disproportionately to the types of applications Indians historically dominated, means the absolute number of Indians entering the US on H-1B visas will fall sharply in the coming fiscal year.

## The Green Card Elimination

The H-1B was always meant to be a temporary visa. But for Indians, it became the beginning of a decade-long journey toward permanent residency — a journey defined by the green card backlog.

The backlog exists because of per-country caps: no single country can receive more than 7 percent of employment-based green cards in any year. Since Indians make up the majority of employment-based applicants, the queue is staggeringly long. Some EB-2 applicants have been waiting since 2012. Some EB-3 applicants face estimated wait times of 50 to 80 years. There are an estimated 400,000 to 500,000 Indians in this queue.

Until Friday, these applicants could wait in the United States. They filed Form I-485 — the Adjustment of Status application — and continued working, paying taxes, building lives. Their spouses could work on Employment Authorisation Documents. Their children could attend school. The wait was interminable, but at least it was conducted from within the country where they had built their lives.

USCIS has now reclassified Adjustment of Status as "an extraordinary form of relief" — available only in exceptional circumstances, at the discretion of USCIS officers. The default path is now consular processing: return to your home country, schedule an interview at a US consulate, and wait.

For an Indian family that has been in the United States for 15 years — with American-born children, a mortgage, a community, and a job — the instruction to "return to your home country to apply" is not a procedural adjustment. It is an upheaval.

Immigration attorneys across the country report a flood of panicked calls. The questions are practical: Will I lose my job? Can I come back? What happens to my children's school? What about my house? There are no clear answers. The policy memo directs officers to evaluate "extraordinary circumstances" on a case-by-case basis but does not define what qualifies.

## The 72-Hour Convergence

What makes this week different from previous immigration policy changes is the convergence. It is not one thing. It is three things at once, and they interact.

The H-1B contraction reduces the number of Indians who enter the pipeline. The Adjustment of Status elimination destabilises the Indians who are already in the pipeline. And Rubio's "America First" visa announcement in India — which fast-tracks business visitor visas, not immigrant visas — sends the message that India's professionals are welcome to visit but not necessarily to stay.

Mark Krikorian, the executive director of the Centre for Immigration Studies, responded to the H-1B numbers by saying the "only real solution is to abolish the H-1B programme altogether, along with OPT and more." His view is at the restrictionist extreme, but the policy direction is moving in his direction — not in one dramatic stroke, but in incremental tightening across every dimension of the system.

Zoho CEO Sridhar Vembu responded to the green card change on X with a post that went viral across Indian tech communities. His argument: Indian tech companies should build in India rather than routing talent through the US immigration system. "We have been sending our best people into a broken system that treats them as disposable," he wrote. The post resonated because it articulated a sentiment that has been growing among Indian professionals in America: the system that invited them is systematically making it harder for them to stay.

## What the Numbers Actually Mean

The combined impact of these changes will take months to fully materialise. But the trajectory is clear.

Fewer Indians will enter the US on H-1B visas. Those who do will need to earn higher salaries, hold higher degrees, and work for employers willing to meet the new requirements. The Indian IT services model — which brought hundreds of thousands of workers to the US over three decades — is being disrupted not by technology or competition but by policy.

Those already in the US face a fundamentally altered landscape. The green card backlog was already the longest for any nationality. The Adjustment of Status elimination adds logistical burden, family separation risk, and job disruption to a process that was already measured in decades. Legal challenges are being prepared, and immigration advocates expect injunctions. But litigation takes time, and the uncertainty is immediate.

The Indian government has not commented publicly on the H-1B numbers. External Affairs Minister S. Jaishankar's meeting with Rubio on Saturday was described as focused on trade and strategic cooperation. But behind the diplomatic language, India's position is clear: it wants its nationals treated fairly, and it has leverage — as both the largest source of H-1B talent and a trade partner the US is actively courting.

## What NRIs Should Do Right Now

For Indians currently in the US on H-1B visas with pending green card applications:

Do not make irreversible decisions based on a policy memo. The Adjustment of Status change will face legal challenges. Multiple immigration attorney groups and advocacy organisations are already preparing litigation. A federal injunction could restore the previous process.

Consult an immigration attorney immediately if your I-485 is pending. Your specific situation — priority date, employer, family circumstances, visa type — determines your exposure. The memo creates a grey area around "extraordinary circumstances" that your attorney can help you navigate.

If you are considering buying a home, factor in the uncertainty. The combination of the green card policy change and rising mortgage rates (now 6.51 percent) creates a dual risk for Indian families who may need to leave the country and may face higher borrowing costs if they stay.

For Indian students currently in the US or considering US programmes: the H-1B changes actually favour you if you hold a US master's degree. The 71.5 percent selection rate for US advanced degree holders is the highest on record. But the pathway beyond the H-1B — from temporary visa to permanent resident — is now more uncertain than at any point in the programme's history.

For Indians in India considering the US: the cost-benefit calculation has shifted. The H-1B is harder to get, the green card wait is now also a geographic disruption, and the salary threshold of $100,000 limits the types of roles available. Canada, the UK, Germany, and Australia are positioning themselves as alternatives — and their immigration systems, while imperfect, do not impose the same combination of per-country caps, decade-long backlogs, and policy uncertainty.

The Indian immigration pipeline to America built Silicon Valley, staffed America's hospitals, and generated billions in tax revenue and innovation. This week, that pipeline narrowed from every direction at once. Whether it narrows further, or whether legal challenges and political pressure reverse the trend, will be determined in the coming months. For the millions of Indians whose lives are built around the assumption that the path to America remains open, those months will feel very long.
"""
    })
else:
    print(f"  ⚠ Skipping H-1B article — slug already exists: {slug2}")


# ── Insert articles ──
if articles:
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        try:
            result = sb_post("p2_articles", article)
            print(f"  ✓ Article {i}: {article['headline'][:80]}...")
            print(f"    Slug: {article['slug']}")
            if result:
                print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Article {i} FAILED: {e}")
else:
    print("\nNo new articles to insert (all duplicates).")

print("\nDone.")
