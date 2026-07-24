#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 09:30 batch
Topics: 1) Trump reversal: "no rush" on Iran deal, blockade stays — India's energy vulnerability in focus
        2) Rubio-Jaishankar joint press conference fine print — visa reforms, anti-India racism, defense, multi-alignment
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

def make_slug(text, date_suffix="20260524"):
    slug = text.lower()
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
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Trump Reversal — "No Rush" on Iran Deal, Blockade Stays
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("trump-no-rush-iran-deal-blockade-stays-hormuz-india-oil-crisis")
if slug1 not in existing_slugs:
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "Twenty-Four Hours After Calling the Iran Deal 'Largely Negotiated,' Trump Says There Is No Rush. The Blockade Stays. India Imports Half Its Oil Through Hormuz.",
        "subheadline": "On Saturday, President Donald Trump told reporters the deal was close. On Sunday morning, he posted on Truth Social that the blockade would 'remain in full force and effect until an agreement is reached, certified, and signed' — and that both sides should 'take their time.' Iran's Supreme National Security Council has not approved the memorandum. Iran's military adviser to the Supreme Leader says Tehran retains 'the legal right to manage the Strait of Hormuz.' The head of Abu Dhabi National Oil Company said last week that even if the war ends now, full flows through the strait will not return before Q1 or Q2 of 2027. Only 33 ships passed through the strait in the last 24 hours — down from 140 on a typical pre-war day. About 50 per cent of India's crude oil and nearly 90 per cent of its LPG and LNG imports pass through Hormuz. Since the closure, India has rerouted 70 per cent of its crude imports through longer Arctic and Baltic sea routes. For every Indian family paying more for cooking gas and petrol, for every NRI watching the rupee slide past 97 to the dollar, Trump's Sunday morning reversal is not a diplomatic nuance. It is the difference between relief this summer and crisis through the winter.",
        "slug": slug1,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "For the Indian diaspora, the Hormuz blockade is not abstract geopolitics — it is the price of cooking gas in their parents' kitchen, the cost of the flight home, and the value of every dollar they remit. India is the world's third-largest oil consumer and imports over 85 per cent of its crude. Fifty per cent of that crude and 90 per cent of its LPG and LNG pass through the Strait of Hormuz. Since the strait closed, India has rerouted imports through Arctic and Baltic routes that are 40-60 per cent longer, adding $3-5 per barrel in shipping costs alone. The rupee has fallen past 97 to the dollar — eroding the purchasing power of NRI remittances, which totalled $125 billion in 2025. For the nine million Indians working in the Gulf — many of whom have already faced layoffs and salary cuts since the war began — the blockade's continuation means their host economies remain under stress. For Indian-Americans filling their own gas tanks in the United States, where prices have spiralled to their highest since 2008, Trump's reversal hits from both ends: higher costs at home and a weaker rupee when they send money back.",
        "tags": ["Iran", "Trump", "Hormuz", "blockade", "oil", "India", "energy", "LPG", "LNG", "rupee", "NRI", "Gulf", "ADNOC", "nuclear", "ceasefire", "oil prices"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump says no rush for Iran deal, US blockade stays", "url": "https://www.reuters.com/world/us/trump-says-iran-deal-largely-negotiated-dispute-over-strait-reopening-2026-05-24/"},
            {"name": "Reuters — Axios says proposed US-Iran deal involves opening strait during 60-day ceasefire extension", "url": "https://www.reuters.com/world/middle-east/axios-us-iran-deal-opening-strait-ceasefire-extension-2026-05-24/"},
            {"name": "India News Stream — Global oil prices climb as Iran indicates scepticism of agreement with US", "url": "https://indianewsstream.com/global-oil-prices-climb-iran-scepticism/"},
            {"name": "Barron's — Trump Says U.S. Will Not Rush a Peace Deal With Iran", "url": "https://www.barrons.com/articles/trump-iran-deal-no-rush-blockade-stays-2026-05-24"},
            {"name": "The Sun — Trump says US won't rush into deal with Iran", "url": "https://www.the-sun.com/news/35675432/trump-iran-deal-no-rush-blockade/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "body": """On Saturday evening, the world was told the Iran deal was close. President Donald Trump said Washington and Tehran had "largely negotiated" a memorandum of understanding. Axios reported a framework: a 60-day ceasefire extension, the Strait of Hormuz reopened with no tolls, Iran clearing its mines, the US lifting its port blockade, and sanctions waivers allowing Iran to sell oil freely. Gulf leaders — from Saudi Arabia, Qatar, the UAE, Jordan, Egypt, Turkey and Pakistan — called Trump to urge him to sign.

On Sunday morning, Trump reversed course.

"Both sides must take their time and get it right. There can be no mistakes!" he wrote on Truth Social. The US blockade on Iranian ships, he added, would "remain in full force and effect until an agreement is reached, certified, and signed."

Twenty-four hours. That is how quickly the prospect of relief evaporated.

## What Changed Overnight

The Saturday optimism was never as solid as the headlines suggested. Multiple obstacles remained, and Sunday's reversal exposed them.

**Iran's Supreme National Security Council has not approved the memorandum.** A senior Iranian source told Reuters that if the council approved the framework, it would be sent to Supreme Leader Ayatollah Mojtaba Khamenei for final sign-off. That approval has not come.

**Iran and the US disagree on what "reopening" means.** Iran's Tasnim news agency reported that differences remained over one or two clauses. Separately, a military adviser to Khamenei said Tehran retained "the legal right to manage the Strait of Hormuz" — language that suggests Iran intends to maintain control over which ships pass through, even after a deal. Iran's Fars News Agency went further: Tehran agreed only to allow the number of passing ships to return to pre-war levels, but "in no way" would this mean a return to free passage. Management of the strait would remain "exclusively under Iran's authority."

**The nuclear issue is unresolved.** The draft framework includes Iranian commitments to never pursue nuclear weapons and to negotiate a suspension of uranium enrichment. But Iran has enriched uranium to 60 per cent purity — far beyond what is needed for civilian power — and the gap between verbal commitments through mediators and a signed, verified agreement is enormous.

**Israel's position is unclear.** Israeli Prime Minister Benjamin Netanyahu spoke with Trump on Saturday but did not address the proposed deal publicly. An Israeli government statement said Netanyahu "stressed that Israel will maintain freedom of action against threats on all fronts, including Lebanon." Israel's parallel war in Lebanon — against the Iranian-backed Hezbollah militia — is intertwined with the Iran negotiations, and any deal that does not address Lebanon could face Israeli opposition.

## The Numbers That Matter for India

The Strait of Hormuz, before the war, carried approximately one-fifth of all global oil and liquefied natural gas shipments. Iran closed it with mines and threats to attack shipping after the US-Israeli bombing campaign began on February 28.

For India, the numbers are stark:

**50 per cent of India's crude oil imports pass through Hormuz.** India is the world's third-largest oil consumer and imports over 85 per cent of its crude. Half of that flows through a single chokepoint that has been effectively closed for nearly three months.

**Nearly 90 per cent of India's LPG and LNG imports transit the strait.** This is cooking gas — the fuel that hundreds of millions of Indian households depend on daily. The rerouting has added weeks to delivery times and billions to costs.

**India has rerouted 70 per cent of its crude imports via Arctic and Baltic routes.** These alternative routes are 40-60 per cent longer than the Hormuz route, adding $3-5 per barrel in shipping costs alone. The logistics are strained, and the costs are passed through to consumers.

**Only 33 ships passed through Hormuz in the last 24 hours.** Before the war, the daily average was 140. Iran's Revolutionary Guards said the ships that did pass required permission from Tehran — a far cry from the free and open waterway that existed before February.

**Even if the war ends now, full flows will not return before Q1 or Q2 of 2027.** The head of the Abu Dhabi National Oil Company said this last week. Mines need to be cleared. Insurance markets need to reopen. Shipping companies need to re-establish routes. The physical infrastructure of global oil transit does not switch on overnight.

## The Rupee, Remittances, and the Cost of Cooking Gas

The Indian rupee has fallen past 97 to the dollar. Foreign investors have pulled over $21 billion from Indian markets. NRI deposits in Indian banks have declined. The war's economic transmission mechanism is simple and brutal: higher oil prices → larger current account deficit → weaker rupee → higher inflation → eroded purchasing power.

For the 31 million-strong Indian diaspora, this hits from multiple directions:

**Remittances buy less.** India received approximately $125 billion in remittances in 2025 — the highest in the world. When the rupee weakens, the dollars, pounds, and dirhams that NRIs send home stretch further in nominal terms but are eroded by the inflation that the weak rupee itself creates. The net effect is a wash at best.

**Gulf workers face layoffs and salary pressure.** Nine million Indians work in the Gulf states — Saudi Arabia, the UAE, Qatar, Kuwait, Oman, and Bahrain. The Gulf economies depend on oil revenue. When the strait is closed and oil shipments are disrupted, even oil-producing states face logistical and revenue challenges. Construction projects slow. Spending contracts. The workers who feel it first are the ones on temporary visas with the fewest protections.

**Cooking gas prices have risen sharply in India.** The government has absorbed some of the increase through subsidies, but the fiscal cost is mounting. The Indian Oil Corporation's statement that "adequate supply of fuels is being maintained to all retail outlets" is a statement about logistics, not price. The supply is maintained; the cost is not.

**US gas prices are at their highest since 2008.** For Indian-Americans, the war has pushed petrol prices to levels that are drawing political backlash. California Governor Gavin Newsom has publicly clashed with Chevron over branded fuel markups. Trump himself has acknowledged the pain — "I appreciate everybody putting up with it for a little while" — while simultaneously insisting it "won't be much longer." His Sunday reversal suggests otherwise.

## Why Trump Pulled Back

The reversal is likely tactical rather than substantive. Trump's negotiating pattern throughout the war has been to alternate between maximalist threats and expressions of optimism, using the volatility itself as leverage.

But the domestic political cost is rising. A Reuters review found that Trump has mentioned his White House ballroom construction project — a renovation he is personally passionate about — at least 40 times this year, including nine times this month. He has mentioned the economy far less frequently, and his off-the-cuff comment earlier this month — "I don't think about Americans' financial situation" — was seized on by Democrats and went viral.

His approval ratings have been hit by the war's economic impact. With midterm elections approaching in November, Republican senators and strategists are increasingly worried about the optics of a president focused on a ballroom while Americans struggle to fill their gas tanks.

The "no rush" posture may be designed to create the impression that Trump is negotiating from strength — that the US can sustain the blockade indefinitely while Iran cannot. But the markets, the Gulf leaders, and India's petroleum ministry see the same data: the longer the blockade continues, the more structural the damage becomes.

## What Happens Next

The immediate question is whether Iran's Supreme National Security Council will approve the memorandum framework and send it to Khamenei. If it does, the deal could still happen within days. If it does not, the blockade continues, and the 33-ships-per-day trickle remains the new normal.

Secretary of State Marco Rubio, speaking in New Delhi on Sunday before the Quad Foreign Ministers Meeting, said there could be "good news in the next few hours" on the straits — but cautioned that "you can agree to things on paper; they actually have to be implemented."

India's External Affairs Minister S. Jaishankar, standing beside Rubio, offered a characteristically measured response: India would continue to diversify its energy sources and maintain multiple supply channels. "We have an obligation to our people to provide them energy at affordable and accessible rates," he said.

For the Indian household budgeting for June's cooking gas cylinder, for the NRI checking the rupee exchange rate before sending money home, for the Gulf worker wondering whether his contract will be renewed — the obligation Jaishankar described is one that the Strait of Hormuz, and the two men negotiating over its future, have made impossible to fulfil."""
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ Article 1 slug already exists: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Rubio-Jaishankar Press Conference — The Fine Print on Visas, Racism, Defence, and Multi-Alignment
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("rubio-jaishankar-press-conference-visa-racism-defence-india-us")
if slug2 not in existing_slugs:
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "Rubio Called the India-US Partnership 'One of the Most Important in the World.' Then He Announced an 'America First' Visa Policy, Dismissed Anti-Indian Racism as the Work of 'Stupid People,' and Said the Immigration Overhaul Was Not India-Specific. Here Is What Actually Happened at the Joint Press Conference.",
        "subheadline": "At Hyderabad House in New Delhi on Sunday, US Secretary of State Marco Rubio and External Affairs Minister S. Jaishankar held a joint press conference that covered visas, trade, defence, Iran, Pakistan, the Quad, energy, and anti-Indian racism in the United States. The headline was warm: Rubio called India a strategic partner, invited Modi to the White House, and praised the breadth of the bilateral relationship. The fine print was more complicated. Rubio announced an 'America First' visa schedule that would prioritise business professionals — a reform that may benefit some Indians but narrows the pipeline for others. He acknowledged $20 billion in Indian investment in the US economy but said immigration reforms were global, driven by 20 million illegal entrants, and that friction was inevitable during the transition. When asked about racist comments targeting Indian-Americans, he said every country has 'stupid people' and pivoted to his own immigrant background. Jaishankar pushed back more carefully — raising visa issues, asserting India's multi-alignment strategy, and noting that a 10-year major defence partnership had been renewed alongside a new underwater domain awareness roadmap. The trade deal remains unsigned. The Quad meets Monday.",
        "slug": slug2,
        "category": "news",
        "vertical": "politics",
        "diaspora_angle": "For the 4.8 million Indian-Americans and the hundreds of thousands of Indians on H-1B, F-1, and J-1 visas in the United States, the Rubio-Jaishankar press conference was the most consequential diplomatic event of the week — more so than the Iran negotiations, which feel distant, and more so than the Quad, which is structural. The visa reforms Rubio announced — an 'America First' schedule prioritising business professionals — will directly determine who gets to stay, who gets to come, and how long the process takes. The green card policy change announced two days earlier, requiring applicants to return to their home countries for consular processing, already sent shockwaves through Indian tech corridors in the Bay Area, Seattle, and New Jersey. Rubio's framing of anti-India racism as the work of 'stupid people' — while simultaneously citing his own Cuban immigrant parents — will strike many Indian-Americans as insufficient at a time when hate incidents targeting the community have been rising. Jaishankar's decision to raise visa issues publicly, alongside defence and trade, signals that New Delhi views the treatment of Indians abroad as a first-tier diplomatic priority, not a consular footnote.",
        "tags": ["Rubio", "Jaishankar", "India", "US", "visa", "H-1B", "F-1", "J-1", "green card", "racism", "Indian-Americans", "defence", "trade", "Quad", "Modi", "White House", "America First", "immigration", "NRI", "Hyderabad House"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CurrentIndia / Times of India — From anti India racism to visa issues: Key takeaways from Rubio-Jaishankar joint press conference", "url": "https://currentindia.com/channels/timesofindia/toi-india/from-anti-india-racism-to-visa-issues-key-takeaways-from-rubio-jaishankar-joint-press-conference/"},
            {"name": "Inshorts — Marco Rubio announces 'America First' visa policy in India for business travel", "url": "https://inshorts.com/en/news/marco-rubio-announces-america-first-visa-policy-in-india-for-business-travel"},
            {"name": "AIR News — Jaishankar, US Secretary Rubio Hold Strategic Talks in New Delhi", "url": "https://airnews.in/jaishankar-rubio-strategic-talks-new-delhi-2026/"},
            {"name": "News89 — Rubio Calls India-US Partnership Among World's Most Important In Talks With Jaishankar", "url": "https://news89.com/rubio-india-us-partnership-jaishankar/"},
            {"name": "NRI Page — Rubio Says US Green Card Rule for Indians Is Part of Global Reform", "url": "https://nripage.com/rubio-green-card-rule-global-reform/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "body": """The setting was familiar: Hyderabad House, New Delhi's preferred venue for high-level bilateral meetings, where the flags are arranged just so and the joint press conference follows a script refined over decades of diplomatic visits. But the substance of what US Secretary of State Marco Rubio and External Affairs Minister S. Jaishankar said on Sunday departed from the script in ways that matter.

This was the first joint press conference of Rubio's four-day India visit, coming after Saturday's meetings with Prime Minister Narendra Modi and National Security Advisor Ajit Doval. It covered the full sweep of the bilateral relationship: visas, trade, defence, Iran, Pakistan, the Quad, energy, and — unusually — anti-Indian racism in the United States.

Here is what was said, what it means, and what it does not.

## The Visa Announcement: "America First" for Business Professionals

Rubio announced a new "America First" visa schedule that would prioritise business professionals and leaders "who contribute to expanding India-US commercial ties." The policy sits alongside the broader green card reform announced two days earlier, which requires most applicants to leave the United States and complete the process from their home country through consular processing.

The framing is significant. "America First" is not just a slogan — it is the operational philosophy of the Trump administration's immigration policy. When applied to business visas, it creates a two-tier system: those who demonstrably contribute to US economic interests get priority; everyone else gets the standard queue.

For Indian IT companies that send thousands of workers to the US on H-1B and L-1 visas, this could be beneficial — if their workers qualify as "business leaders" under the new criteria. For Indian students on F-1 visas hoping to transition to Optional Practical Training and then H-1B sponsorship, the path may narrow. For families awaiting green cards through the employment-based backlog — a queue that stretches beyond 150 years for Indian nationals in the EB-2 and EB-3 categories — the consular processing requirement adds a new logistical and financial burden.

Rubio was explicit about the rationale: "We've had over 20 million people illegally enter the United States over the last few years, and we've had to address that challenge." The implication — that reforms targeting legal immigration pathways are a necessary side effect of addressing illegal immigration — is one that Indian professionals have heard before. The frustration is that they are being asked to absorb "friction" for a problem they did not create.

## Anti-Indian Racism: "Every Country Has Stupid People"

When a reporter asked about racist comments targeting Indian-Americans in the United States, Rubio's response was personal and, for many Indian-Americans, inadequate.

"I'll take that very seriously about the comments," he said. "I'm sure that there are people who have made comments online and in other places because every country in the world has stupid people. I'm sure there are stupid people here; there are stupid people in the United States who make dumb comments all the time."

He then pivoted to the broader narrative of American inclusion: "The United States is a very welcoming country. Our nation has been enriched by people who come to our country from all over the world." He cited his own parents, who migrated from Cuba in 1956.

The problem with the response is not that it is wrong — every country does have people who say hateful things — but that it does not acknowledge the specific pattern of anti-Indian hate that has intensified in the United States over the past two years. The rise in online abuse targeting Indian-Americans, the H-1B backlash on social media, and the documented cases of workplace discrimination and hate crimes against South Asians exist within a political context where immigration policy and cultural resentment are intertwined.

By framing racism as the work of "stupid people" rather than as a systemic concern, Rubio sidestepped the question of whether the administration's own immigration rhetoric — which frequently casts legal immigrants as competitors for American jobs — contributes to the environment in which that racism flourishes.

Jaishankar, for his part, raised visa issues during the formal talks, highlighting "the need to protect legal mobility" — diplomatic language for a straightforward message: India's foreign minister is watching how Indians are treated in America, and it is now a first-tier diplomatic issue, not a consular sidebar.

## Defence: The Quiet Wins

Away from the visa controversy, the defence side of the relationship produced concrete deliverables. Jaishankar confirmed that the two countries had renewed their 10-year major defence partnership framework agreement and signed a comprehensive underwater domain awareness roadmap.

The underwater domain awareness roadmap is particularly significant. It formalises cooperation on submarine detection, anti-submarine warfare, and seabed monitoring in the Indian Ocean — capabilities that are directly relevant to countering Chinese naval expansion in the region. India has been developing its own submarine fleet, including nuclear-powered submarines, and the roadmap provides a framework for sharing technology, intelligence, and operational protocols with the United States.

Jaishankar also noted the importance of incorporating "Make in India" principles and lessons from recent conflicts into defence cooperation. This is a reference to India's push to manufacture more military equipment domestically — a priority that sometimes creates tension with the US, which wants India to buy American systems rather than build its own.

## Trade: Still Unsigned

The interim trade deal that was first announced during Modi's US visit in February 2025 remains unsigned. More than three months after the announcement of the "interim deal," the text has not been finalised.

Rubio was characteristically optimistic: "We are hopeful that we will wind up with a trade agreement that is going to be enduring, beneficial to both sides, and sustainable." He noted that an Indian trade delegation had recently visited Washington and a US team was expected in New Delhi soon.

The target is ambitious: $500 billion in bilateral trade by 2030, up from approximately $200 billion today. The interim deal is expected to reduce tariffs on Indian imports from 26 per cent (the additional tariff imposed under Trump's reciprocal tariff framework) and address digital services, agriculture, and quota protections for sensitive sectors.

But as Richard Rossow of the Center for Strategic and International Studies noted: "The lack of a trade agreement — more than three months after the announcement of the interim deal — clouds other areas of engagement." The trade deal is the foundation on which the rest of the relationship is supposed to rest. Without it, every other area — from defence to technology to energy — operates on goodwill rather than contractual commitment.

## Jaishankar on Multi-Alignment: The India Doctrine

Perhaps the most revealing moment came when Jaishankar described India's foreign policy approach in the current geopolitical landscape.

"We are one of the very few countries with strong ties to the US, Israel, Iran and Gulf nations simultaneously," he said. "For us, the challenge is how to maintain all these relationships, how to protect our equities, how to advance our interests. We don't look at it as a zero-sum game. We have to manage and actually take care of all these accounts."

This is the India doctrine in a single paragraph. It is not non-alignment — the Cold War concept that implied equal distance from all blocs. It is multi-alignment: the deliberate cultivation of relationships with competing powers, justified by India's unique position as a country that buys oil from Iran, weapons from Russia, technology from the US, and investment from the Gulf, while maintaining diplomatic ties with Israel.

The doctrine has been tested by the Iran war. India has had to balance its energy dependence on Iran and the Gulf with its strategic partnership with the United States. Jaishankar's articulation — "We have to manage and actually take care of all these accounts" — is a polite way of saying that India will not sacrifice its interests to align exclusively with any single partner.

## Rubio on Pakistan: Reassurance Without Substance

Rubio was asked about the perception that renewed US engagement with Pakistan's military leadership — particularly General Asim Munir's role as mediator in the Iran ceasefire talks — was coming at India's expense.

"I don't view our relation with any country in the world as coming at the expense of our strategic alliance with India," Rubio said.

The statement is diplomatically correct and substantively empty. The United States has maintained parallel relationships with India and Pakistan for decades, and every administration has offered the same reassurance. India's concern is not that the US-Pakistan relationship exists, but that Pakistan's mediator role in the Iran talks gives Islamabad renewed strategic relevance at a time when India had been hoping the US would deprioritise Pakistan entirely.

## What the Press Conference Did Not Cover

What was not said matters as much as what was.

**There was no announcement of a timeline for the trade deal.** "Hopeful" and "soon" are not dates.

**There was no specific US commitment on the green card backlog for Indians.** The Employment-Based Green Card backlog for Indian nationals exceeds 150 years. Neither Rubio nor Jaishankar addressed structural reform of the country-cap system that creates this disparity.

**There was no discussion of the consular processing burden.** Requiring green card applicants to return to India for processing means tens of thousands of people will need to uproot their US lives — sell or sublet apartments, pull children from schools, explain gaps to employers — for a process that could take months. The logistics of this were not addressed.

**There was no public mention of the Khalistan issue or Canadian tensions.** India's dispute with Canada over the alleged targeting of Sikh separatists has been a significant bilateral irritant, and the US position on it has been ambiguous. It did not come up.

## The Quad Meets Monday

The Rubio-Jaishankar press conference is a prelude to Monday's Quad Foreign Ministers Meeting — the first in nearly a year. Rubio, Jaishankar, Australian Foreign Minister Penny Wong, and Japanese Foreign Minister Toshimitsu Motegi will discuss maritime security, critical minerals, Indo-Pacific strategy, and energy cooperation.

The Quad has been described as an "unannounced downgrade" by some analysts, since there has been no leader-level summit since the last one in September 2024. But Rubio insisted the relationship had not lost momentum, and Jaishankar described the Quad's cooperation in terms that were both aspirational and practical: "We are doing a lot with each other because we are maritime powers, and I see that growing. And we are doing a lot with each other because we are democratic powers."

For the Indian diaspora watching from the Bay Area, London, and Toronto, the press conference offered warm words and cold details. The strategic partnership is real. The visa system is getting harder. The racism is acknowledged but not addressed. The trade deal is coming — eventually. And the man standing at the podium calling India one of America's most important partners has just made it more difficult for Indians to become Americans."""
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ Article 2 slug already exists: {slug2}")

# ── Insert articles ──
if not articles:
    print("No new articles to insert")
    exit(0)

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug']} → {art['id']}")
    except Exception as e:
        print(f"❌ Failed to insert {art['slug']}: {e}")

print(f"\n✅ Done — {len(articles)} articles published")
