#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 08:30 UTC batch
Topics: 1) Iran deal "largely negotiated" — Axios terms, Iran disputes, India impact
        2) India rewrites oil supply map — Venezuela surges, Russia drops, first Iranian cargo in 7 years (Reuters/Kpler data)
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
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

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Iran Deal "Largely Negotiated" — What the Terms Are, Why Iran Disputes Them, and What It Means for India
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("iran-deal-largely-negotiated-hormuz-60-day-ceasefire-india-oil-rupee")
headline1_prefix = "trump says a deal with iran"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Says a Deal With Iran Has Been 'Largely Negotiated.' Iran Says Trump's Claims Are 'Incomplete and Inconsistent With Reality.' India Is Watching Because Its Economy Depends on Who Is Telling the Truth.",
        "subheadline": "On Saturday, President Trump announced on Truth Social that a Memorandum of Understanding to end the 84-day Iran war had been 'largely negotiated.' Axios reported the terms: a 60-day ceasefire extension during which the Strait of Hormuz would reopen with no tolls, Iran would clear its mines, the US would lift its naval blockade and issue sanctions waivers allowing Iran to sell oil freely, and Iran would commit to never pursuing nuclear weapons while negotiating suspension of its enrichment programme and removal of its highly enriched uranium stockpile. Within hours, Iran's Fars News Agency called Trump's claims 'incomplete and inconsistent with reality,' saying the strait 'will remain under Iranian management' with tolls, that uranium 'must not leave the country' per Supreme Leader Khamenei's directive, and that nuclear issues have not been discussed. Iran's Tasnim Agency added that no MOU is possible without the release of frozen Iranian assets in the first step. Republican Senators Graham and Wicker called the reported terms a 'disaster.' Israel was reportedly frozen out and sees the deal as 'very big problem.' White House economist Kevin Hassett said energy prices would 'plummet' once a deal is signed. For India — which imports 85 percent of its crude oil, has watched the rupee fall past ₹95, and has endured four fuel price hikes since February — the question of whether the Strait of Hormuz actually reopens is not geopolitics. It is the price of cooking gas.",
        "slug": slug1,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "If you are an Indian family in America sending money home, this deal — or its collapse — will determine whether your next remittance buys 15 kilograms of rice or 12. The rupee has fallen past ₹95 to the dollar. Petrol is ₹113 a litre. LPG cylinders have been hiked four times since February. All of this traces back to one waterway: the Strait of Hormuz, through which 45 percent of India's oil imports used to flow before the Iran war shut it in February. If the deal Trump announced is real — if Hormuz actually reopens, mines are cleared, and tankers start flowing — crude prices will drop, the rupee will stabilise, and the cascading inflation that has hit everything from dal to electricity in your parents' city will begin to ease. White House economist Kevin Hassett said Sunday that energy prices would 'plummet' and a 'gusher of oil' from Saudi and UAE reserves would come online. But if Iran is right — if the strait remains under Iranian management with tolls, if nuclear issues are not on the table, if frozen assets must be released before Iran commits to anything — then the deal Trump announced is diplomatic theatre, and the oil crisis that is slowly grinding Indian household budgets to dust will continue. Shipping expert Sal Mercogliano estimates that even with a deal, Hormuz traffic will reach only 40 percent of pre-war levels by year end. The Red Sea still has not normalised since the Houthi attacks in 2023. For India's 1.4 billion people, and for the 4.4 million Indians in America whose families feel every rupee movement, this is not a news cycle. It is a cost-of-living crisis with no confirmed end date.",
        "tags": ["Iran", "Trump", "Hormuz", "oil", "India", "rupee", "ceasefire", "nuclear", "Khamenei", "Graham", "Wicker", "Hassett", "Rubio", "Pakistan", "Israel", "OPEC", "crude oil", "inflation", "NRI", "remittance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Axios says proposed US-Iran deal involves opening strait during 60-day ceasefire extension", "url": "https://www.reuters.com/world/asia-pacific/axios-says-proposed-us-iran-deal-involves-opening-strait-during-60-day-ceasefire-2026-05-24/"},
            {"name": "Fox News — Trump economist points to 'great signs' of easing inflation, predicts fuel costs will 'plummet' with Iran deal", "url": "https://foxnews.com/media/trump-economist-points-great-signs-easing-inflation-predicts-fuel-costs-plummet-iran-deal"},
            {"name": "Naked Capitalism — Iran War: Trump Announces Deal with Iran Already Disputing His Claims; Strait Traffic Expected to Reach Only 40% by Year End", "url": "https://www.nakedcapitalism.com/2026/05/iran-war-trump-announces-iran-deal-with-iran-already-disputing-his-claims-hawk-heads-exploding-even-if-pact-concluded-strait-of-hormuz-traffic-expected-to-reach-only-40-of-old-level-by-year-end.html"},
            {"name": "The Hill — GOP Sens. Lindsey Graham, Roger Wicker blast reports of 60-day ceasefire deal with Iran", "url": "https://thehill.com/policy/defense/gop-senators-blast-iran-deal-ceasefire"},
            {"name": "Tasnim News Agency — No MoU Possible without Release of Iran's Frozen Assets", "url": "https://www.tasnimnews.com/en/news/2026/05/25/no-mou-possible-without-frozen-assets"},
            {"name": "Daily Caller — Trump Cautions Against Criticisms Over Potential Iran Deal", "url": "https://dailycaller.com/2026/05/24/trump-iran-deal-criticisms/"}
        ]),
        "score_total": 89,
        "status": "published",
        "published_at": now_iso,
        "body": """On Saturday evening, President Donald Trump posted on Truth Social that a Memorandum of Understanding to end the 84-day war with Iran had been "largely negotiated" following "a very good call" with key world leaders. He said final details were "currently being discussed and will be announced shortly."

Within hours, Iran called it a lie. Not politely. Not diplomatically. A lie.

Iran's Fars News Agency, which operates as a quasi-official mouthpiece for the regime, said Trump's claims were "incomplete and inconsistent with reality." Iran's Tasnim News Agency went further, reporting that the Supreme Leader had issued a directive that enriched uranium "must not leave the country." And a Tasnim source added that no MOU was possible without the prior release of Iran's frozen assets — a precondition the US has not acknowledged.

For India, which imports 85 percent of its crude oil, has watched the Strait of Hormuz — the waterway through which nearly half of those imports used to flow — remain effectively closed for three months, and has seen the rupee collapse past ₹95 while petrol crosses ₹113 a litre, the question of who is telling the truth is not academic. It is the difference between relief and ruin.

## What Trump Claims the Deal Contains

The most detailed account of the proposed terms came from Axios, which cited a US official on Saturday. According to the report, the deal involves:

**A 60-day ceasefire extension.** The current ceasefire, in place since April 8, would be extended for two additional months. During this period, both sides would negotiate the outstanding issues.

**Reopening of the Strait of Hormuz.** Iran would agree to clear the naval mines it deployed in the strait and allow ships to pass freely, with no tolls. The US would simultaneously lift its naval blockade on Iranian ports.

**Sanctions waivers for oil sales.** The US would issue sanctions waivers allowing Iran to sell oil freely during the 60-day period. The US would also agree to negotiate over lifting broader sanctions and unfreezing Iranian funds held abroad.

**Nuclear commitments.** Iran would commit to never pursuing nuclear weapons. It would enter negotiations over suspending its uranium enrichment programme and removing its stockpile of highly enriched uranium. According to Axios, Iran gave the US "verbal commitments about the scope of the concessions it's willing to make" on enrichment and nuclear material through mediators.

**Pakistan-mediated.** Pakistan's Prime Minister Shehbaz Sharif confirmed that talks could take place "very soon" following a call with Trump and other Middle Eastern leaders. Pakistan's army chief Asim Munir concluded what was described as a "highly productive" visit to Iran on Saturday.

A Trump administration official told the Daily Caller that a formal MOU was expected "within days" but that "communication with Iranian leadership moves very slowly."

## What Iran Says

Iran's response was swift, detailed, and contradictory to nearly every claim Trump made.

**On the Strait of Hormuz:** Fars reported that "according to the latest exchanged text, if a possible agreement is reached, the Strait of Hormuz will still be under Iran's management." The agency said Iran had agreed to allow the number of passing ships to return to pre-war levels, but this "does not mean 'free passage' to the pre-war situation in any way." Management of the strait — including determining the route, time, manner of passage, and issuing permits — would remain "exclusively under the control and discretion of the Islamic Republic of Iran." Iran also indicated it would continue extracting tolls.

**On nuclear commitments:** Tasnim reported that claims Iran had agreed to hand over its highly enriched uranium or suspend enrichment above 3.6 percent for a decade were "completely false." Iran has consistently insisted on sequencing: resolve the war and Strait of Hormuz issues first, then — and only then — discuss nuclear matters. Supreme Leader Mojtaba Khamenei reportedly issued a directive that uranium "must not leave the country."

**On preconditions:** Tasnim quoted an informed source saying that "no agreement will be reached without the release of a specified portion of Iran's frozen assets in the very first step and a clear mechanism for the continued guaranteed release of all frozen assets." Iran accused the US of "consistently obstructing the negotiations and changing its positions."

**On Trump's announcements:** Fars described Trump's posts as "primarily for promotional purposes and media consumption." According to the agency, US officials actually told Iran to "ignore" Trump's Truth Social posts. Whether this is true or Iranian spin is impossible to verify, but the assertion itself reveals the depth of the credibility gap between the two sides.

**On the scope of the deal:** Iran's Foreign Ministry said negotiations were focused on ending the war "on all fronts, including Lebanon." This is a critical addition. Israel has continued launching air strikes on southern Lebanon — killing at least 3,123 people since March 2 — despite the ceasefire and ongoing peace negotiations. If Iran insists that any final deal must also cover Lebanon, and Israel is not a party to the talks, the deal has a structural hole that no amount of diplomatic language can fill.

## Israel Was Frozen Out

The Times of Israel reported that Israel was not included in the negotiations and that Israeli officials view the emerging deal as a "very big problem." This is significant because any agreement that ends the Iran war without addressing Israel's ongoing military operations in Lebanon — and without securing Israel's agreement to cease hostilities — leaves the core conflict unresolved.

Trump's Truth Social post listed Turkey, Pakistan, and Jordan among the parties to the deal. Israel was conspicuously absent. The practical question is whether the US can enforce a deal that Israel did not sign and may actively oppose.

## Republican Hawks Revolt

Even the terms Trump presented — which are substantially more favourable to the US than what Iran says it has agreed to — triggered immediate backlash from Trump's own party.

Senator Roger Wicker, the Republican chairman of the Senate Armed Services Committee, wrote on X: "The rumoured 60-day ceasefire — with the belief that Iran will ever engage in good faith — would be a disaster." He said the effects of Operation Epic Fury, the joint US-Israel military campaign, would "be for naught" if the deal went forward.

Senator Lindsey Graham warned that a premature deal could "fundamentally shift the balance of power in the Middle East in Iran's favour." He questioned whether Iran could be denied the ability to threaten global oil supply by blocking the Strait again in the future.

Former Secretary of State Mike Pompeo posted on X — in a message that received 3 million views on a Saturday night of a holiday weekend — that the deal "seems straight out of the Wendy Sherman-Robert Malley-Ben Rhodes playbook: Pay the IRGC to build a WMD programme and terrorise the world. Not remotely America First."

## The White House Economic Case

White House National Economic Council Director Kevin Hassett presented the optimistic scenario on Fox News Sunday.

"We expect energy prices as soon as there's a deal to plummet," he said. He predicted that Saudi Arabia and the UAE could bring offline reserves back to full capacity once the strait reopens, creating a "gusher of oil" that would drive prices down rapidly.

Hassett's remarks came shortly after Trump-nominated Kevin Warsh was sworn in as the new Federal Reserve chair, replacing Jerome Powell. Hassett said that falling energy prices would give Warsh "a lot of room for the Fed to do the right thing and lower rates."

The logic is straightforward: a deal reopens Hormuz, oil floods the market, crude drops, inflation eases, the Fed cuts rates, and the economic pain of the past three months reverses. It is a compelling chain of events — if every link holds.

## Why Shipping Experts Are Sceptical

Sal Mercogliano, one of the most widely followed maritime shipping analysts, offered a more sobering assessment. In an interview with Mario Nawfal, he said that even if a deal is signed exactly as the US presents it, Strait of Hormuz traffic is expected to reach only about 40 percent of pre-war levels by the end of 2026.

The reasons are structural. Hundreds of very large crude carriers are sitting outside the Persian Gulf, waiting. Insurers will need to reassess risk before covering transit. Port infrastructure in Iran has been degraded by the blockade. And if Iran retains management of the strait — as it insists — with tolls, route control, and passage permits, the risk calculus for shipowners changes fundamentally.

Mercogliano drew a parallel to the Red Sea. After Houthi attacks began disrupting shipping through the Suez Canal route in late 2023, major container carriers rerouted around the Cape of Good Hope. Despite a subsequent ceasefire, most high-value shipping has not returned to the Red Sea. The rerouting that was supposed to be temporary has become structural.

If the same pattern repeats in the Persian Gulf, a deal would bring diplomatic relief but not economic relief — at least not at the speed the White House is promising.

## What This Means for India

India is uniquely exposed to the outcome of these negotiations. The numbers tell the story:

**Oil dependency:** India imports 85 percent of its crude oil. Before the war, approximately 45 percent of those imports transited the Strait of Hormuz. The strait's closure forced Indian refiners to scramble for alternatives — Russian oil, Venezuelan crude, Brazilian supplies, African barrels — at higher costs and longer delivery times.

**Currency pressure:** The rupee has fallen past ₹95 to the dollar, driven primarily by the energy price shock. Every dollar India spends on more expensive crude from longer supply chains is a dollar of additional current account deficit pressure.

**Fuel prices:** Petrol has crossed ₹113 per litre. LPG cylinders have been hiked four times since February. Diesel, which powers agriculture and trucking, has risen correspondingly, pushing up the cost of food transport and, ultimately, food prices.

**Inflation cascade:** The Reserve Bank of India has been forced to balance inflation fighting with growth support. If energy prices drop as Hassett predicts, the RBI gets room to cut rates. If they do not, the stagflationary pressure — high prices plus slowing growth — continues.

**Diplomatic positioning:** India has deliberately maintained relationships with all sides: it imports oil from Russia, buys from the US, received its first Iranian cargo in seven years via a Washington waiver, and has kept channels open with Gulf states. External Affairs Minister Jaishankar's formulation at the Rubio press conference — "a big country, if you want to de-risk, looks at multiple sourcing" — captures India's approach. But that approach works only if there are multiple sources to buy from. A Hormuz deal, even a partial one, would restore options.

**Remittances:** For the 4.4 million Indians in America, every rupee movement changes the purchasing power of money sent home. At ₹85, a $1,000 remittance bought ₹85,000. At ₹95, the same transfer buys ₹95,000 — good for the sender, devastating for the Indian economy's import bill. A deal that stabilises crude and strengthens the rupee back toward ₹85-90 would rebalance this equation.

## The Fundamental Uncertainty

The honest assessment is that no single point of agreement has been confirmed by both sides.

The US says Hormuz will reopen freely. Iran says it stays under Iranian management with tolls.

The US says Iran has given verbal commitments on nuclear material. Iran says the nuclear issue has not been discussed and uranium will not leave the country.

The US implies the deal is days away. Iran says no MOU is possible without frozen assets released first.

Trump's own party says the deal, even as Trump describes it, is a disaster.

Israel was not consulted and views it as a threat.

Shipping experts say even with a deal, normalisation is years away.

This is not a done deal. It is not even a deal with an agreed outline. It is two parties describing completely different documents, surrounded by sceptics on all sides, with a shipping industry that has already learned the hard way that ceasefires in the Middle East do not mean safe passage.

For India, the prudent response is the one Jaishankar has already articulated: diversify, do not depend on any single route or supplier, and wait for verified facts rather than announced ones. But prudence does not solve the immediate problem. The rupee is falling now. Fuel prices are rising now. Families in India are paying more for dal and electricity and cooking gas now.

If Trump's deal is real, relief could come within weeks. If it is not, the crisis deepens into a second quarter with no end in sight.

India is watching because it has no choice. Its economy depends on who is telling the truth. And right now, nobody knows."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India Has Completely Redrawn Its Oil Supply Map in 90 Days
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-oil-supply-map-redrawn-venezuela-brazil-russia-hormuz-kpler")
headline2_prefix = "india has completely redrawn"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India Has Completely Redrawn Its Oil Supply Map in 90 Days. Venezuela Is Now Its Fifth-Largest Supplier. Russia Dropped From 50 Percent to 35. And India Just Received Its First Iranian Cargo in Seven Years.",
        "subheadline": "New data from Kpler, reported by Reuters on May 25, reveals the full scale of India's emergency oil supply chain realignment since the Strait of Hormuz crisis began in February. Russia, which supplied nearly half of India's crude in March, has dropped to 35 percent. The UAE rebounded from 230,600 barrels per day to 669,700 — tripling in one month — because it has a pipeline that bypasses Hormuz. Saudi Arabia held steady at 619,500 bpd for the same reason. Brazil became the fourth-largest supplier. Venezuela — a country under US sanctions that India barely imported from a year ago — surged to fifth place and is on course to become fourth in May. India skipped Iraqi purchases entirely because Iraq has no route that avoids the strait. And in a diplomatic move that would have been unthinkable six months ago, India received its first Iranian oil shipment in seven years, enabled by a temporary waiver from Washington meant to stabilise global prices. Overall imports fell 15.5 percent year-on-year to 4.57 million barrels per day. OPEC's share of India's imports rose from 30 percent to 45 percent in April, helped partly by the UAE's exit from OPEC in May, which freed it from output quotas. For every Indian family paying ₹113 for a litre of petrol, this data explains why: the oil is coming from farther away, through longer routes, at higher costs, from countries India was not buying from three months ago.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "Three months ago, your parents' cooking gas came from a supply chain that had operated the same way for decades. Middle Eastern crude, shipped through the Strait of Hormuz, refined in Jamnagar or Paradip, distributed as petrol, diesel, and LPG across India's 800 million energy consumers. That supply chain no longer exists in its old form. The data Reuters published on May 25 — sourced from Kpler, the gold standard for global oil tracking — shows that India has executed the fastest oil supply realignment in the history of the global energy market. Russia went from 50 percent to 35 percent. The UAE tripled. Brazil and Venezuela appeared from nowhere on the supplier list. Iraq disappeared. And Iran reappeared for the first time since 2019, in an extraordinary diplomatic footnote that reveals how desperate the situation has become. For NRIs, this matters in the most tangible way possible. Every barrel that now travels from Venezuela instead of Iraq adds shipping days and cost. Every barrel from Brazil instead of Kuwait adds fuel surcharges that refiners pass downstream. When Indian Oil Corporation or Bharat Petroleum pays more for crude, your family pays more for petrol, diesel, and the LPG cylinder that heats their kitchen. The 15.5 percent drop in overall imports means India is not just paying more per barrel — it is getting fewer barrels. That is the definition of a supply crisis that has not yet peaked. And the question of whether it eases depends on a deal between Trump and Iran that, as of Sunday morning, neither side can agree actually exists.",
        "tags": ["India", "oil", "crude", "Venezuela", "Brazil", "Russia", "UAE", "Iran", "Hormuz", "Kpler", "Reuters", "OPEC", "energy", "rupee", "petrol", "LPG", "supply chain", "refineries", "NRI", "economy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India turns to Latin American, African oil after Hormuz disruption (May 25, 2026)", "url": "https://www.reuters.com/business/energy/india-turns-latin-american-african-oil-after-hormuz-disruption-2026-05-25/"},
            {"name": "The Business Standard — Can Venezuelan oil save India amid the Hormuz energy crisis?", "url": "https://tbsnews.net/can-venezuelan-oil-save-india-amid-hormuz-energy-crisis"},
            {"name": "Dainik Jagran — Venezuela India's 3rd Largest Oil Supplier Amid Hormuz Crisis", "url": "https://english.dainikjagranmpcg.com/venezuela-india-3rd-largest-oil-supplier-hormuz-crisis"},
            {"name": "Fox News — Trump economist says fuel costs will 'plummet' with Iran deal", "url": "https://foxnews.com/media/trump-economist-points-great-signs-easing-inflation-predicts-fuel-costs-plummet-iran-deal"},
            {"name": "Reuters — Axios: proposed US-Iran deal involves opening strait during 60-day ceasefire extension", "url": "https://www.reuters.com/world/asia-pacific/axios-says-proposed-us-iran-deal-involves-opening-strait-during-60-day-ceasefire-2026-05-24/"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_plus1,
        "body": """In January 2026, India's oil supply map was simple. Russia was the largest supplier, at nearly 50 percent of all imports. The Middle East — Saudi Arabia, Iraq, the UAE, Kuwait — collectively supplied most of the rest. Latin America and Africa were minor players. Iran had not sold a barrel of oil to India in seven years.

By May, that map had been torn up and redrawn from scratch.

New data from Kpler, the global commodity tracking firm, reported by Reuters on May 25, reveals the full extent of India's emergency oil supply chain realignment. It is the fastest restructuring of energy sourcing by any major economy in modern history, forced by a three-month war that shut the waterway through which nearly half of India's crude used to flow.

## The Numbers

The headline numbers tell the story of a country scrambling to keep its refineries running.

**Russia:** Still India's largest supplier, but its share dropped from nearly 50 percent in March to approximately 35 percent in April. In absolute terms, Russian imports fell to 1.6 million barrels per day in April — down 29.4 percent from March — partly because Nayara Energy shut its 400,000-bpd Vadinar refinery for maintenance. In May, Russian imports are expected to rebound to about 1.9 million bpd.

**UAE:** The most dramatic rebound. Imports from the United Arab Emirates surged to 669,700 bpd in April from just 230,600 bpd in March — nearly tripling in a single month. The reason is geography: the UAE has the ADCOP pipeline, which runs from Abu Dhabi's oil fields to the port of Fujairah on the Gulf of Oman, completely bypassing the Strait of Hormuz. When every other Gulf route was blocked, the UAE pipeline became India's lifeline.

**Saudi Arabia:** Steady at approximately 619,500 bpd. Saudi Arabia also has a pipeline that bypasses Hormuz — the East-West Pipeline running from Abqaiq to the Red Sea port of Yanbu. This gave Saudi crude an alternative route that kept it flowing when strait-dependent competitors could not ship.

**Brazil:** Emerged as the fourth-largest supplier to India, up from a marginal position before the crisis. Brazilian heavy crude, shipped across the Atlantic and around the Cape of Good Hope, now makes a journey of roughly 40 days to reach Indian ports — compared to the 5-7 day transit from the Persian Gulf before the war.

**Venezuela:** The most geopolitically surprising entry. Venezuela — a country under US sanctions, with a crumbling oil infrastructure, and a political relationship with India that was functional but never central — has surged to become India's fifth-largest crude supplier. It is on course to move into fourth place in May, overtaking Brazil. Venezuelan heavy grades, particularly Merey and Diluted Crude Oil, are attractive to Indian refiners because they trade at steep discounts to benchmark crude. What Indian refineries lose in quality, they gain in price — a tradeoff that makes sense when every barrel is expensive and hard to find.

**Iraq:** Disappeared. India skipped Iraqi purchases entirely in April because Iraqi exports were halted. Iraq has no pipeline bypassing the Strait of Hormuz. Every barrel of Iraqi crude must transit the waterway. When the strait closed, Iraq's supply to India went to zero.

**Iran:** The most extraordinary line item. India received its first Iranian oil shipment in seven years, enabled by a temporary waiver from Washington that was designed to help stabilise global prices. The last time India bought Iranian crude was in 2019, when it stopped imports to comply with US sanctions under Trump's first term. The fact that the same administration that imposed those sanctions is now granting waivers to allow Iranian oil sales reveals how profoundly the Hormuz crisis has reshuffled the geopolitical deck.

**Overall:** India imported 4.57 million bpd in April — unchanged from March, but down 15.5 percent from a year earlier. India is not just paying more per barrel. It is importing fewer barrels. In a country where demand typically grows 3-4 percent annually, a 15.5 percent drop in supply is a shock absorber that only works if it is temporary.

## The OPEC Shift

OPEC's share of India's imports rose to 45.2 percent in April, up from approximately 30 percent in March. The rebound was driven almost entirely by the UAE's pipeline-enabled surge.

In May, the UAE formally exited OPEC, freeing it from the cartel's output quotas. This is significant for India because the UAE is now unconstrained in how much oil it can produce and sell. Abu Dhabi has approximately 4 million bpd of production capacity and has long chafed under OPEC quotas that forced it to produce below capacity. As an independent producer, the UAE can sell as much as India will buy — a structural shift that could make the UAE-India energy relationship the most important bilateral oil corridor in the post-Hormuz world.

## Why This Matters for Your Family

The abstract numbers have concrete consequences for every household in India.

**Shipping costs:** A barrel of crude from Venezuela travels approximately 12,000 nautical miles to reach India's western ports, compared to roughly 1,500 miles from the Persian Gulf. Shipping costs are typically $2-4 per barrel for Gulf routes. For Latin American and African routes, they can reach $6-10. Those costs are embedded in the price of every litre of petrol and diesel sold in India.

**Refinery economics:** Indian refineries were optimised for Middle Eastern crude grades — light, sweet Arabian blends and medium-sour Iraqi Basrah. The switch to heavy Venezuelan grades, Brazilian pre-salt crude, and varied Russian Urals requires blending adjustments, different processing configurations, and sometimes reduced throughput. When refineries process crude they were not designed for, efficiency drops and costs rise.

**Fuel prices:** Petrol in India has crossed ₹113 per litre. Diesel, which powers the trucks that deliver food, construction materials, and consumer goods across the country, has risen proportionally. LPG — the cooking fuel used by over 300 million Indian households since the Ujjwala scheme expanded access — has been hiked four times since February. These are not market fluctuations. They are the direct cost of shipping oil from the other side of the world instead of across a strait.

**The rupee:** India's current account deficit widens when oil import costs rise. A wider deficit puts pressure on the rupee. The rupee has fallen past ₹95 to the dollar — a level that seemed improbable six months ago. For Indian exporters, the weak rupee helps margins. For everyone else — importers, consumers, families buying medicine or electronics — it means inflation on imported goods layered on top of inflation on fuel.

**Electricity:** India generates approximately 50 percent of its electricity from coal, but gas-fired and oil-fired power plants provide peaking capacity, especially during the summer demand surge. With LNG prices elevated due to the broader energy market disruption, electricity costs in states that rely on gas power — Gujarat, Maharashtra, Tamil Nadu — have risen. The heatwave driving demand to record levels has compounded the pressure.

## The Iran Variable

The first Iranian cargo in seven years is a small volume in the context of India's 4.57 million bpd total imports. But it is a politically enormous signal.

Washington granted the waiver to stabilise global prices — an acknowledgement that the Hormuz closure was hurting American allies more than it was hurting Iran. For India, the waiver was both a lifeline and a diplomatic statement: we will buy from whoever can supply us, including Iran, if the US permits it.

If the deal Trump announced on Saturday materialises and sanctions on Iranian oil are further relaxed, India could significantly increase Iranian imports. Before 2019, Iran was among India's top five suppliers, providing approximately 500,000 bpd of crude at prices that included generous credit terms. Iranian oil is geographically close (short shipping routes), chemically suited to Indian refineries, and historically priced at discounts to benchmark.

But this depends entirely on the deal's fate — and as of Sunday morning, neither side agrees on what the deal actually contains.

## What Happens Next

India's oil map will continue to evolve based on three variables:

**The Hormuz deal.** If the strait reopens, even partially, Iraq and Kuwait could resume exports, reducing India's dependence on distant suppliers. If Iran retains management of the strait with tolls and permits, as it insists, the calculus becomes murkier — shipowners and insurers will need time to assess the risk before routing tankers back through.

**The Russia relationship.** Russia remains India's largest supplier, but the relationship faces growing pressure. Western secondary sanctions, payment complications, and the reputational cost of being seen as Russia's energy partner all create friction. India has managed this through rupee-ruble payment arrangements and quiet diplomacy, but the equilibrium is fragile.

**The Venezuela gamble.** Venezuela's oil infrastructure is degraded after years of underinvestment and mismanagement. Current production is approximately 900,000 bpd — a fraction of its 2015 peak of 2.8 million bpd. India's growing dependence on Venezuelan crude is a bet that Maduro's government can maintain production. If Venezuelan output falters, India loses a supplier it did not have three months ago and cannot easily replace.

The fundamental reality is that India's pre-February oil supply chain — efficient, proximate, and built over decades of infrastructure and relationships — cannot be rebuilt until the Strait of Hormuz is reliably open. Everything else is adaptation. The Kpler data shows that India has adapted with remarkable speed and resourcefulness. But adaptation is not normalisation. The oil is coming from farther away, through longer routes, at higher costs. And until the strait reopens — truly, verifiably, for commercial traffic at pre-war volumes — every Indian family will keep paying the price of that distance at the petrol pump, the gas stove, and the electricity meter."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Source images for articles ──
PEXELS_KEY = ""
pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "pexels" in k.lower():
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    return []

def get_pexels_image_url(query):
    photos = search_pexels(query)
    if photos:
        return photos[0]["src"]["large2x"]
    return None

image_queries = {
    slug1: "oil tanker ship strait ocean sunset",
    slug2: "oil refinery industrial pipeline petrochemical",
}

for art in articles:
    slug = art["slug"]
    query = image_queries.get(slug, "")
    if not query:
        continue
    img_url = get_pexels_image_url(query)
    if img_url:
        try:
            sb_patch("p2_articles", {"id": f"eq.{art['id']}"}, {"image_url": img_url})
            print(f"🖼️  Image set for {slug}: {img_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Image PATCH failed for {slug}: {e}")
    else:
        print(f"⚠️  No Pexels image found for {slug}")

# ── Score decay for news articles older than 12h ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

# ── Git commit & push ──
try:
    repo = Path.home() / "workspace" / "the-videshi-news"
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
    msg = f"news: Iran deal terms + India oil map redrawn ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
