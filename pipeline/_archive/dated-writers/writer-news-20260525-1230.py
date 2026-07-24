#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 12:30 UTC batch
Topics: 1) Iran MOU revealed as 14 points + both sides walk back expectations + Rubio "another way" from Delhi
        2) India turns net importer of finished steel — Chinese/Korean/Japanese steel flooding in
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
# ARTICLE 1: Iran's 14-Point MOU + Both Sides Walk Back + Rubio "Another Way"
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("iran-mou-14-points-service-fees-hormuz-rubio-another-way-india")
headline1_prefix = "iran just revealed the deal"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Iran Just Revealed the Deal Is a 14-Point Document. There Will Be No Tolls in the Strait — but There Will Be 'Service Fees.' The US Secretary of State, Standing in New Delhi, Said If Talks Fail America Will Deal With Iran 'Another Way.'",
        "subheadline": "On Monday, Iran's Foreign Ministry spokesperson Esmaeil Baghaei held a weekly briefing that quietly rewrote the terms of the debate. The proposed Memorandum of Understanding with the United States contains 14 points, he said, and is focused on ending the war and lifting the US naval blockade of the Strait of Hormuz — in exchange for Iran ensuring safe transit through the waterway. There will be no tolls, Baghaei said. But there will be a cost for 'services' — navigation, environmental protection — under a protocol to be agreed with Oman. Nuclear talks are not part of the current framework; they would begin only during a 60-day period if the accord is signed. Iranian sources told Reuters that 'feasible formulas' could be found for the enriched uranium stockpile, including diluting the material under IAEA supervision — not shipping it out of the country as the US has demanded. A conclusion has been reached on many topics, Baghaei added, but that 'does not mean we're close to signing an agreement.' Hours later in New Delhi, US Secretary of State Marco Rubio told reporters that the US would give diplomacy 'every chance to succeed' — but if talks fail, Washington will deal with Iran 'another way.' Oil fell 5 percent to two-week lows. The rupee gained. And India, hosting Rubio for the Quad Foreign Ministers' Meeting tomorrow, finds itself positioned at the exact intersection of the deal's promise and the threat of its collapse.",
        "slug": slug1,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "If you are tracking the Iran deal from a desk in San Jose or a kitchen in Plano, Monday gave you the most important 24 hours of actual detail since Trump first claimed the deal was 'largely negotiated' on Saturday. The weekend was noise — a Truth Social post, an Axios leak, Iranian denials, Republican fury. Monday was substance. Iran's foreign ministry spokesperson laid out the architecture: 14 points. No tolls but service fees. Nuclear talks deferred. Enriched uranium stays in-country but may be diluted under IAEA watch. And the US Secretary of State, standing on Indian soil where your parents or in-laws may live, said the alternative to diplomacy is something darker. For NRI families, the 'service fees' distinction matters more than it sounds. If ships passing through the Strait of Hormuz pay navigation and environmental fees to Iran — even nominal ones — it establishes a precedent that Iran controls the waterway. Insurers will price that control into every tanker's voyage. Shipping companies will build it into freight rates. And those costs will land, as all energy costs do, in the price of the LPG cylinder your mother uses to cook dinner. The rupee gained on Monday — it touched a two-week high against the dollar — because oil dropped 5 percent on deal hopes. MUFG, the Japanese megabank, said in a note that the rupee rally 'could extend toward 100' if the Iran conflict persists but that 'a meaningful easing' would need an actual agreement ensuring Hormuz transit. RBI Governor Sanjay Malhotra said the central bank would do 'whatever is required' to ensure orderly forex movement. Translation: the RBI is intervening in currency markets daily and will continue doing so regardless of the deal's outcome. Your remittance dollars are being managed, not freed.",
        "tags": ["Iran", "MOU", "14 points", "Hormuz", "Rubio", "New Delhi", "Quad", "Jaishankar", "service fees", "Baghaei", "IAEA", "uranium", "ceasefire", "oil", "rupee", "RBI", "Malhotra", "NRI", "energy", "India"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Iran and US play down hopes for imminent breakthrough in war", "url": "https://www.reuters.com/world/middle-east/rubio-says-us-will-find-another-way-if-iran-talks-fail-2026-05-25/"},
            {"name": "Reuters — Rupee gains to two-week high, forward premiums dip as oil prices slump", "url": "https://www.reuters.com/markets/currencies/rupee-gains-two-week-high-forward-premiums-dip-oil-prices-slump-2026-05-25/"},
            {"name": "Business Today — Oil Tumbles To 2-Week Low As Iran Deal Hopes Trigger Risk Selloff", "url": "https://www.businesstoday.com.my/2026/05/25/oil-tumbles-to-2-week-low-as-iran-deal-hopes-trigger-risk-selloff/"},
            {"name": "NewKerala — Jaishankar: Indo-Pacific Key Energy Lifeline for Quad", "url": "https://www.newkerala.com/news/a/indo-pacific-become-big-energy-lifeline-jaishankar-ahead-quad-865.htm"},
            {"name": "The Indian Eye — Marco Rubio offers US energy as much India will buy", "url": "https://theindianeye.com/2026/05/22/marco-rubio-offers-us-energy-as-much-india-will-buy/"},
            {"name": "Jewish News — US official: Iran deal to be signed in coming days; Trump derides 'loser' critics", "url": "https://jewishnews.com/articles/us-official-iran-deal-to-be-signed-in-coming-days-trump-derides-loser-critics"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "body": """For three days, the Iran deal existed as a cloud of contradictory claims. Trump said it was largely done. Iran said it was not. Axios published terms. Iran's Fars News Agency called them lies. Republican senators revolted. Oil prices whipsawed. Nobody could point to a specific document with specific terms that both sides acknowledged.

On Monday, Iran's Foreign Ministry spokesperson Esmaeil Baghaei changed that. In a weekly briefing that received far less attention than Trump's Truth Social posts, Baghaei revealed the structural architecture of the proposed agreement — and in doing so, made it clear that the deal both sides are discussing is simultaneously more advanced and more fragile than either has publicly admitted.

## The 14-Point Document

The proposed Memorandum of Understanding contains 14 points, Baghaei said. It is focused on two core objectives: ending the war and lifting the US naval blockade of the Strait of Hormuz, in exchange for Iran taking steps to ensure safe transit through the waterway.

This is the first time either side has confirmed a specific number of points in the framework. The 14-point structure suggests a detailed, negotiated document — not the broad outlines that Trump's social media posts implied. It also suggests that the sticking points are specific and technical, not merely rhetorical.

Baghaei said the potential accord contained no specific details on management of the strait. This is a notable omission. For days, the core dispute has been whether Iran would retain control of Hormuz or whether it would become an open, unmanaged waterway. The absence of specific management language in the 14 points suggests this is being deliberately left ambiguous — a negotiating technique that allows both sides to claim victory but guarantees a future dispute over interpretation.

## No Tolls, but 'Service Fees'

Baghaei made a distinction that will echo through insurance boardrooms and shipping company headquarters from London to Singapore.

Iran will not charge tolls for ships passing through the Strait of Hormuz, he said. However, there will be a cost for "services" — navigation, environmental protection, and related functions — under a protocol to be agreed with Oman, which shares the opposite shore of the waterway.

The difference between a toll and a service fee is, in legal terms, vast. A toll implies sovereignty over a passage — the right to charge for transit. A service fee implies the provision of something in return: navigation assistance, environmental monitoring, port services. In practical terms, both extract money from every vessel transiting the strait. But the framing matters enormously for international law, for insurance pricing, and for the long-term question of who controls the most important waterway in the global energy system.

If Iran charges service fees — even modest ones — it establishes an institutional presence in the strait that did not exist before the war. Ships will interact with Iranian service providers. Navigation will follow Iranian-determined routes. Environmental protocols will be Iranian-designed. The practical effect is management without the legal label of control.

Shipping analysts who followed the Houthi crisis in the Red Sea will recognise the pattern. Formal agreements mean less than operational reality. If every tanker captain must coordinate with Iranian services before transiting Hormuz, Iran controls the strait regardless of what the MOU says.

## Nuclear Talks Are Not on the Table — Yet

Baghaei was explicit: nuclear issues are not part of the current negotiations. The 14-point framework deals with the war and the strait. Nuclear talks would begin only during a subsequent 60-day period, if the framework accord is agreed and signed.

This directly contradicts the impression created by Trump's Saturday post, in which he implied that Iran had agreed to give up its nuclear ambitions as part of the deal. Baghaei's clarification confirms what Iranian sources have said throughout: the nuclear programme is a separate track, to be discussed on a separate timeline, with separate conditions.

However, Iranian sources offered Reuters a significant new detail on Monday. They said that "feasible formulas" could be found to resolve the dispute over Iran's highly enriched uranium stockpile — including diluting the material under the supervision of the UN's International Atomic Energy Agency.

This is a meaningful shift. The US has demanded that Iran's enriched uranium be physically removed from the country — shipped to Russia or a third party, as was done under the 2015 JCPOA framework. Iran's Supreme Leader has reportedly issued a directive that uranium "must not leave the country." Dilution under IAEA supervision offers a middle path: the material stays in Iran but is rendered unusable for weapons purposes under international monitoring.

Whether this formula is acceptable to the US — and more importantly, to Israel, which was excluded from the negotiations — remains unknown. But the fact that Iranian sources are floating it through Reuters suggests it is an active element of the back-channel discussions.

## Rubio's Threat From New Delhi

While Baghaei was briefing reporters in Tehran, US Secretary of State Marco Rubio was standing in New Delhi — 4,000 kilometres away, in the capital of the country most economically affected by the Hormuz closure — delivering a very different message.

The US would give diplomacy "every chance to succeed," Rubio told reporters. But if talks fail, Washington will deal with Iran "another way."

The phrasing was deliberate. "Another way" is the diplomatic euphemism for military escalation — a return to the bombing campaign that killed thousands in Iran before the April 8 ceasefire. Rubio delivered it not from Washington or the Pentagon but from India, where External Affairs Minister S. Jaishankar was hosting him for the most consequential visit by a US Secretary of State to New Delhi in years.

There was a "pretty solid thing on the table," Rubio said, "in terms of their ability to open up the strait, get the strait open, enter into a very real, significant, time-limited negotiation on the nuclear matter, and hopefully we can pull it off."

The word "hopefully" is not typically in the vocabulary of a Secretary of State describing a deal that is nearly complete. Neither is "pretty solid." Both suggest that the US knows the framework is real but is not confident it will survive the remaining sticking points.

## What Rubio Offered India

Rubio's New Delhi visit was not only about Iran. Before departing for the trip, he told American reporters in Miami: "We want to sell them as much energy as they'll buy."

This is a significant statement. The US is now actively positioning itself as an alternative energy supplier to India — not just for the duration of the Hormuz crisis, but as a structural shift in the bilateral energy relationship. US LNG exports, US crude, and even Venezuelan oil (under US supervision) are all on the table.

Rubio also revealed that Venezuela's interim President Delcy Rodriguez was expected to visit India this week to discuss oil sales. However, Indian sources subsequently told The Hindu BusinessLine that Rodriguez was "not visiting India next week" — the visit was tied to the International Big Cat Alliance summit, which was postponed due to the Ebola outbreak in Africa.

The mixed signals on the Venezuela visit capture the broader dynamic perfectly. Everyone is positioning for a post-Hormuz energy order. Nobody knows when — or if — it will arrive.

## The Quad Meeting

Tomorrow, May 26, Rubio will sit with Jaishankar, Australia's Penny Wong, and Japan's Toshimitsu Motegi for the Quad Foreign Ministers' Meeting in New Delhi. It is the first such meeting in nearly a year, and the agenda has been reshaped entirely by the Hormuz crisis.

Jaishankar framed the meeting's significance at the joint press conference with Rubio on Saturday. "Looking ahead, the Indo-Pacific is going to become more and more important with the passage of time," he said. "It will even become a big energy lifeline."

The phrase "energy lifeline" is new in Quad vocabulary. The grouping was founded on security — freedom of navigation, counterbalancing China's maritime expansion, preserving the rules-based order in the Indo-Pacific. Energy was a secondary concern. The Hormuz crisis has elevated it to the primary one.

If the Iran deal collapses and the strait remains closed, the Indo-Pacific's energy routes become not just important but essential. Oil from Australia's northwest shelf, LNG from the US Gulf Coast via Pacific routes, crude from Southeast Asian producers — all of these bypass the Middle East entirely. The Quad, as a grouping of the four largest maritime democracies in the Pacific basin, would become the institutional framework for managing this alternative energy architecture.

Jaishankar knows this. His framing is not speculative — it is a hedge. If Hormuz reopens, India returns to its traditional suppliers and the Quad remains a security forum. If Hormuz stays closed, the Quad becomes the energy forum that keeps India's lights on.

## Oil Falls, Rupee Gains

The markets moved on Monday as if the deal were closer than the rhetoric suggests.

Brent crude dropped 4.55 percent to $98.83 per barrel — a two-week low. West Texas Intermediate fell 4.73 percent to $92.03. Both prices represent the lowest levels since May 7 and reflect a market that is pricing in at least partial resolution of the Hormuz blockade.

The Indian rupee gained to a two-week high against the dollar, buoyed by the oil price drop. MUFG, the Japanese banking giant, said in a research note that the "recent USD/INR rally could extend towards the 100 level should the Iran conflict persist" — but that a "meaningful easing" in currency pressure would require a confirmed agreement ensuring Hormuz transit.

RBI Governor Sanjay Malhotra, in a media interview on Monday, said the central bank would do "whatever is required" to ensure orderly movement in the foreign exchange market. The statement is both reassuring and alarming: it confirms the RBI is actively intervening in currency markets, spending foreign reserves to prevent the rupee's decline from becoming disorderly. India's forex reserves have already dropped by an estimated $30 billion since February as the RBI defends the currency.

## The Shape of the Deal

What emerged on Monday is the clearest picture yet of what both sides are actually negotiating:

**The framework (14 points):** End the war. Lift the US blockade. Reopen the Strait of Hormuz with Iranian "services" (not free passage, not tolls, but a third category). Extend the ceasefire.

**The nuclear track (separate, 60 days):** Begin after the framework is signed. Discuss enrichment suspension and uranium stockpile disposition. Iran's position: dilute under IAEA supervision, do not remove from the country. US position: remove or neutralise the material completely.

**The unresolved issues:** Israel's exclusion from negotiations. Lebanon's ongoing war. Iran's demand for frozen assets to be released as a precondition. Sanctions relief timeline. The definition of "safe transit" and who enforces it.

**The alternatives:** Rubio's "another way" — military escalation. Iran's "services" framework — de facto control of Hormuz. India's "energy lifeline" — a Pacific-centric alternative to Middle Eastern oil routes.

The deal is real in the sense that both sides acknowledge a 14-point document exists. It is not real in the sense that neither side agrees on what the document means.

## What This Means for India

India is playing every angle simultaneously — and doing it well.

Jaishankar hosts Rubio and the Quad, positioning India as an indispensable partner for US energy and security interests. India buys Venezuelan oil under US sanction waivers, Russian oil despite Western pressure, and received its first Iranian cargo in seven years. India sides with China at the WTO against UK steel tariffs one week, then sits with the US-led Quad the next.

This is not hypocrisy. It is the foreign policy of a country that imports 85 percent of its oil, has a rupee at ₹95, fuel prices at historic highs, and 1.4 billion people whose daily lives depend on the cost of energy. India cannot afford to choose sides because choosing sides means choosing to lose access to one of its energy suppliers.

The Quad meeting tomorrow will produce a communiqué about the rules-based order and maritime cooperation. Behind the communiqué, the real conversation will be about oil: who has it, who can ship it, who can sell it to India, and what happens if the Strait of Hormuz — the choke point that defines India's energy security — remains under dispute.

For every Indian family in America sending money home, the Monday numbers tell the story. Oil fell 5 percent. The rupee gained. Gold dropped. Markets rose. But none of it is settled. The 14-point MOU is a framework for a deal that does not yet exist, negotiated by two sides that cannot agree on what they have agreed to, watched by a world that is pricing in resolution while preparing for collapse.

India is watching because its economy is on the line. And on Monday, both sides gave India — and the world — the clearest view yet of how close, and how far, the deal actually is."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India Turns Net Importer of Finished Steel — Chinese Steel Floods In
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-net-steel-importer-china-korea-japan-dumping-tata-jsw")
headline2_prefix = "india just became a net importer"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India Just Became a Net Importer of Steel for the First Time. Chinese, Korean, Japanese, Vietnamese, and Russian Steel Is Flooding In. Imports Are Up 31 Percent. And India's Own Steel Giants — Tata, JSW, SAIL — Are Watching Their Domestic Market Get Eaten.",
        "subheadline": "Provisional government data reviewed by Reuters on Monday shows that India imported 0.7 million metric tons of finished steel in April 2026 — up 30.8 percent from a year earlier. Exports were 0.5 million tons, up 24.9 percent but not enough to prevent India from becoming a net importer of the material that builds its bridges, highways, metro systems, and apartment towers. China led the import surge, followed by South Korea, Japan, Vietnam, and Russia. Finished steel consumption hit 13 million tons in April, up 8.2 percent year-on-year, but domestic crude steel production rose only 3.9 percent to 13.8 million tons — the gap between what India consumes and what it produces is widening, and foreign steel is filling it. This is not an abstract trade statistic. India is the world's second-largest crude steel producer. It was supposed to be expanding capacity to 300 million tons by 2030 under the National Steel Policy. Instead, it is importing steel from the countries it intended to compete with. The causes are convergent: China's construction slowdown has left its mills with massive overcapacity and nowhere to sell except markets like India; Trump's 50 percent tariffs on Indian steel have made US-bound exports uneconomic; and the Hormuz crisis has disrupted shipping routes that Indian steelmakers used to reach European and Middle Eastern buyers. For every Indian worker in a steel plant in Jamshedpur, Bellary, or Rourkela — and for every NRI whose family's economic stability traces back to India's industrial base — this is a red flag.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "If your family is from Jharkhand, Odisha, Chhattisgarh, or Karnataka — the states where India's steel industry employs millions directly and tens of millions indirectly — Monday's Reuters data should alarm you. India imported 0.7 million metric tons of finished steel in April, up 31 percent from a year ago. It exported only 0.5 million tons. For the first time, India is buying more steel from the world than it sells. The top five sources are China, South Korea, Japan, Vietnam, and Russia — countries that are either dumping excess capacity (China's construction sector has collapsed, leaving its mills desperate for export markets) or rerouting steel that can no longer reach the US (Trump's 50 percent tariffs have made American-bound exports uneconomic for everyone). India's steel giants — Tata Steel, JSW Steel, Steel Authority of India, Jindal Steel & Power — built their expansion plans on the assumption that domestic demand growth (8.2 percent in April) would be met by domestic supply. Instead, foreign steel is arriving cheaper, faster, and in larger volumes. The Indian Steel Association has been pushing for safeguard duties and a border adjustment tax to protect domestic producers, but the Modi government has been reluctant to act — partly because cheaper imported steel keeps construction costs down for the PM Gati Shakti infrastructure programme, and partly because India just sided with China at the WTO against Britain's steel safeguard measures, making it politically awkward to impose its own. For NRIs who invest in Indian steel stocks, the implications are direct: Tata Steel, JSW, and SAIL share prices have underperformed the Sensex this year. For those whose families work in steel towns, the implications are existential. When Indian mills lose domestic market share to Chinese steel priced below production cost, the first casualties are contract workers, then shifts, then entire plants. Jamshedpur was built by Tata Steel. If Tata Steel's domestic market shrinks because Chinese flat-rolled coils arrive at Indian ports at prices no Indian mill can match, Jamshedpur's economy shrinks with it.",
        "tags": ["India", "steel", "imports", "China", "South Korea", "Japan", "Vietnam", "Russia", "Tata Steel", "JSW", "SAIL", "Jindal", "dumping", "safeguard duty", "WTO", "Trump tariffs", "manufacturing", "economy", "NRI", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — India turns net importer of finished steel in April, data shows (May 25, 2026)", "url": "https://www.reuters.com/world/china/india-turns-net-importer-finished-steel-april-data-shows-2026-05-25/"},
            {"name": "The Hindu BusinessLine — India joins forces with China, Japan against UK steel curbs at WTO", "url": "https://www.thehindubusinessline.com/economy/india-joins-forces-with-china-japan-against-uk-steel-curbs-at-wto/article71011967.ece"},
            {"name": "EximGuru — Trump's new move could hammer India's factories, wreck exports and jobs", "url": "https://www.eximguru.com/news/trump-tariffs-india-steel-exports-jobs"},
            {"name": "BigMint — India steel index rises nearly 2% w-o-w amid safeguard duty buzz, tight supplies", "url": "https://www.bigmint.co/news/india-steel-index-safeguard-duty"},
            {"name": "Kallanish — Imports influx hits Indian stainless steel capacity utilisation", "url": "https://api.kallanish.com/news/imports-influx-indian-stainless-steel-capacity"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_plus1,
        "body": """India is the world's second-largest producer of crude steel. It has the world's largest reserves of iron ore. It has invested tens of billions of dollars in expanding steel capacity under the National Steel Policy, which targets 300 million tons of annual production by 2030. Narendra Modi has made steel — along with semiconductors, defence, and renewable energy — a centrepiece of his Make in India manufacturing vision.

And in April 2026, India imported more finished steel than it exported.

Provisional government data reviewed by Reuters on Monday reveals a trade reversal that, while it may prove temporary, exposes the structural vulnerabilities of India's industrial base at a moment when it can least afford them.

## The Numbers

India imported 0.7 million metric tons of finished steel in April — up 30.8 percent from a year earlier. It exported 0.5 million metric tons — up 24.9 percent, but not enough to prevent a net import position of approximately 200,000 tons.

The top sources of imported steel were China, South Korea, Japan, Vietnam, and Russia, in that order.

Finished steel consumption in India reached 13 million tons in April, up 8.2 percent year-on-year — reflecting the relentless pace of infrastructure construction under PM Gati Shakti, the expansion of housing under Pradhan Mantri Awas Yojana, and the continued buildout of metro systems, highways, and industrial corridors.

But domestic crude steel production reached only 13.8 million tons, up 3.9 percent. The gap between consumption growth (8.2 percent) and production growth (3.9 percent) is the story. India's mills cannot keep up with India's demand. Foreign steel is filling the shortfall.

## Why China Is Leading the Surge

China produces more steel than the rest of the world combined — approximately 1.05 billion tons per year. For decades, most of that steel was consumed domestically, feeding the largest construction boom in human history. Apartment towers, high-speed rail, bridges, highways, and industrial parks absorbed Chinese steel as fast as mills could produce it.

That era is over. China's property sector has been in crisis since 2021. Evergrande, Country Garden, and dozens of smaller developers have defaulted. New housing starts have fallen more than 50 percent from their peak. The construction industry that consumed 60 percent of China's steel output is contracting.

The result is an ocean of surplus steel with nowhere to go inside China. Chinese mills — many of them state-owned and unable to shut down without political consequences — are exporting at prices that undercut domestic producers in every market they enter. India, with the fastest-growing major economy and the largest infrastructure programme in the developing world, is the most attractive destination.

Chinese steel exports globally declined 9.7 percent year-on-year in the first half of 2026, partly because of new export licensing rules introduced by Beijing. But the steel that is being exported is heavily concentrated in markets without effective trade defences — and India, despite being the world's second-largest producer, has been slow to erect them.

## The Trump Tariff Effect

India's steel export markets have simultaneously contracted. The most significant blow came from the United States, where President Trump imposed 50 percent tariffs on Indian steel and aluminium imports. India exported approximately $4.56 billion worth of steel to the US annually before the tariffs. That trade has now been made largely uneconomic.

The tariff impact is not limited to the direct US trade. When Indian steel cannot reach America, it stays in the domestic market or seeks other export destinations. But those destinations — Europe, the Middle East, Southeast Asia — are themselves being flooded by Chinese steel. The result is a squeeze from both ends: imports rising as Chinese steel arrives at Indian ports, and exports stalling as traditional markets close or become uncompetitive.

The Hormuz crisis has compounded the export problem. Indian steelmakers used the Strait of Hormuz route to reach buyers in the UAE, Saudi Arabia, and Turkey. With the strait effectively closed since February, shipping routes to these markets have lengthened by weeks and shipping costs have risen by $6-10 per ton. Indian steel that was competitively priced for Middle Eastern buyers is now too expensive to ship.

## The WTO Contradiction

India's trade policy on steel is caught in a contradiction of its own making.

Last week, India joined China, Japan, Brazil, Australia, and others at the World Trade Organization in opposing the United Kingdom's steel safeguard measures, which are set to take effect on July 1, 2026. The complainants argued that global steel overcapacity should not be addressed through import restrictions but by tackling root causes. They questioned whether the UK's measures were consistent with WTO rules.

The argument India made at the WTO — that safeguard duties are an inappropriate response to overcapacity — is the exact argument China would make if India imposed safeguard duties on Chinese steel imports. India has, in effect, undermined its own legal position for protecting its domestic steel industry from the dumping it is now experiencing.

The Indian Steel Association (ISA) has been lobbying aggressively for a border adjustment tax on steel imports. The ISA argues that Indian steelmakers face higher domestic taxes and compliance costs than their Chinese and Korean competitors, creating an unlevel playing field. A border adjustment tax would equalize these costs at the point of import.

The Ministry of Steel has been sympathetic. It recently asked the Ministry of Finance to withdraw anti-dumping tariffs on low-ash metallurgical coke imports — a raw material for steel production — to help domestic mills reduce input costs. But on the broader question of steel import protection, the Modi government has been hesitant.

The reason is infrastructure. India is building at a pace that requires every available ton of steel. If safeguard duties raise the price of imported steel, they raise the cost of every highway, metro line, bridge, and housing project in the country. The government's infrastructure ambitions conflict directly with its industrial policy ambitions. You cannot simultaneously build the cheapest possible roads and protect the most expensive possible steel mills.

## India's Steel Giants Under Pressure

The import surge has real consequences for the companies that define India's industrial identity.

**Tata Steel,** headquartered in Jamshedpur, Jharkhand, is India's largest private-sector steel producer. The company has invested over ₹12,000 crore in expanding its Kalinganagar plant in Odisha, adding 5 million tons of annual capacity. That investment was predicated on growing domestic demand absorbing new supply. If Chinese imports capture the marginal demand growth instead, Tata Steel's expansion economics deteriorate.

**JSW Steel,** led by Sajjan Jindal, operates India's largest single-location steel plant in Bellary, Karnataka. JSW has been among the most aggressive Indian steelmakers in pursuing export markets, particularly in the US and Europe. Trump's tariffs and the Hormuz disruption have hit JSW's export revenue directly. The company's share price has underperformed the Sensex by approximately 12 percent year-to-date.

**Steel Authority of India Limited (SAIL),** the government-owned steelmaker, operates plants across Bhilai, Durgapur, Rourkela, and Bokaro. SAIL's cost structure is higher than private competitors, making it more vulnerable to cheap imports. The company has been struggling with modernisation and efficiency improvements for years. A sustained period of import competition could force difficult decisions about capacity and employment.

**Jindal Steel & Power (JSPL)** has positioned itself as an infrastructure-focused steelmaker, supplying rails, structural steel, and heavy plates for India's construction boom. JSPL's product mix gives it some insulation from commodity-grade Chinese imports, but the company's margins are under pressure from rising raw material costs and weakening export realisations.

## The Employment Dimension

India's steel industry directly employs approximately 600,000 people. The indirect employment — in mining, transport, fabrication, construction, and services — is estimated at 2.5 to 3 million. The industry is concentrated in specific regions: Jharkhand (Jamshedpur, Bokaro), Odisha (Rourkela, Angul, Kalinganagar), Chhattisgarh (Bhilai, Raigarh), Karnataka (Bellary), West Bengal (Durgapur, Burnpur), and Andhra Pradesh (Visakhapatnam).

These are not metropolitan economies with diversified employment bases. They are steel towns. When steel production falls, the entire local economy contracts — from the dhaba outside the plant gate to the school that educates workers' children. The communities most at risk from Chinese steel dumping are among the least equipped to absorb economic shocks.

India's steel employment is also heavily tiered. Permanent employees at major producers like Tata, JSW, and SAIL have union protections and relatively stable employment. But a significant portion of the workforce — estimated at 40-50 percent in some plants — consists of contract workers with minimal protections. When production is cut, contract workers are the first to lose shifts. They have no severance, no union representation, and no alternative employment in a steel town.

## What Happens Next

The April data point is a single month. India has been a net exporter of steel for most of the past decade, and it may return to that position as exports recover and the Hormuz situation resolves. But the structural forces driving the import surge are not temporary:

**China's overcapacity is permanent.** Beijing has pledged to reduce excess steel capacity, but political constraints — employment in steel-dependent regions, state ownership of major mills, local government revenue from steel production — make meaningful cuts unlikely. Chinese steel will continue to seek export markets for years.

**Trump's tariffs are in place.** There is no indication that the 50 percent tariff on Indian steel will be reduced as part of the bilateral trade negotiations. The US market is effectively closed to Indian steel for the foreseeable future.

**The Hormuz crisis is ongoing.** Even if a deal is signed, shipping analysts expect Hormuz traffic to reach only 40 percent of pre-war levels by year-end. Indian steel exports to the Middle East will remain disrupted.

**India's demand keeps growing.** The 8.2 percent consumption growth in April reflects an economy that is building infrastructure at unprecedented scale. If domestic production cannot keep pace — and production growth of 3.9 percent suggests it cannot — imports will continue to fill the gap.

The government faces a classic industrial policy dilemma. Protecting domestic steelmakers means higher costs for infrastructure projects that employ tens of millions. Not protecting them means ceding market share to China, Korea, and Japan — undermining the Make in India vision and risking employment in India's steel belt.

Modi's National Steel Policy envisioned India as a 300-million-ton steel powerhouse by 2030, exporting to the world. In April 2026, India was buying steel from the world. The gap between ambition and reality has rarely been wider."""
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
    slug1: "diplomatic press conference podium flags international",
    slug2: "steel factory molten metal industrial manufacturing",
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
    msg = f"news: Iran 14-point MOU + India steel net importer ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
