#!/usr/bin/env python3
"""Write 3 articles for the May 17 2026 evening cycle."""
import os, json, uuid, requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
API = f"{SUPABASE_URL}/rest/v1"
NOW = datetime.now(timezone.utc).isoformat()

articles = []

# ── Article 1: Adani SEC Settlement (markets-finance) ──────────────────

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The Adanis Agreed to Pay $18 Million. The Real Price Was Always Political.",
    "subheadline": "A quiet SEC settlement ends America's headline fraud case against Gautam Adani — but in New Delhi, Rahul Gandhi is already framing it as a Modi bailout.",
    "slug": "adani-sec-settlement-18-million-political-price-20260517",
    "category": "markets-finance",
    "vertical": "business",
    "urgency": "breaking",
    "is_featured": True,
    "score_total": 82,
    "topic_id": "d3f27533-54e5-4110-bd08-dde9950ec53b",
    "tags": ["Adani Group", "SEC", "Gautam Adani", "Sagar Adani", "DOJ", "Rahul Gandhi", "NRI investors", "Adani Green Energy"],
    "sources": [
        {"url": "https://www.law.com/2026/05/17/feds-appear-set-to-drop-criminal-case-against-adani-following-sec-civil-settlement/", "name": "Law.com"},
        {"url": "https://www.livemint.com/companies/adani-sec-settlement-2026", "name": "Mint"},
        {"url": "https://www.the420.in/gautam-adani-sagar-adani-sec-fraud-settlement/", "name": "The420"},
        {"url": "https://www.latestly.com/agency-news/india-news-gautam-adani-agrees-to-pay-usd-6-million-to-settle-us-sec-fraud-case/", "name": "LatestLY"},
        {"url": "https://www.thehindubusinessline.com/companies/adani-sec-settlement-may-end-us-civil-proceedings/", "name": "The Hindu Business Line"},
    ],
    "diaspora_angle": "NRI investors who hold Adani stocks through Indian brokerage accounts or ADR-equivalent instruments watched the group shed — then recover — tens of billions in market cap since the November 2024 indictment. The settlement directly involved American investors who bought $175 million of a $750 million Adani Green Energy bond issue. For the diaspora, the case is a stress test of whether Indian conglomerates can survive US regulatory scrutiny without lasting capital-market damage.",
    "image_search_query": "Gautam Adani press conference 2026",
    "image_entities": ["Gautam Adani", "SEC", "Adani Group headquarters"],
    "image_must_show": "Gautam Adani at a public event or Adani Group corporate imagery",
    "body": """On Friday, Gautam Adani and his nephew Sagar Adani agreed to pay a combined $18 million to the United States Securities and Exchange Commission, closing a civil case that had threatened to become the most consequential corporate fraud prosecution involving an Indian conglomerate on American soil.

The terms are modest by Wall Street standards: $6 million from Gautam Adani, $12 million from Sagar Adani. Neither admitted wrongdoing. A federal judge is expected to sign off on Monday, and the U.S. Department of Justice is reportedly preparing to dismiss parallel criminal charges — the ones that carried the real sting when they were unsealed in November 2024.

## What the Case Was Actually About

The SEC alleged that the Adanis made false and misleading statements to American investors during a $750 million bond offering by Adani Green Energy in 2021, of which roughly $175 million was raised from U.S.-based buyers. At the heart of the indictment were claims of an elaborate bribery scheme: prosecutors alleged that Adani Group executives had offered hundreds of millions of dollars to Indian government officials to secure above-market-rate energy purchase agreements.

Adani Group has consistently denied the allegations, calling them baseless and politically motivated. The settlement, notably, sidesteps any admission of the bribery claims — a point legal analysts say is significant.

"The SEC's willingness to settle on these terms suggests they faced real jurisdictional hurdles," said one securities lawyer quoted by The Hindu Business Line. "The Foreign Corrupt Practices Act angle was always going to be difficult to prosecute when the alleged bribery targets were Indian officials and the primary conduct occurred in India."

## The Market Verdict

Investors had already begun pricing in a resolution. Adani Group stocks surged in the days leading up to the settlement announcement, with the conglomerate recovering a significant portion of the market capitalisation it had lost since the Hindenburg Research short-seller report in January 2023 and the subsequent U.S. indictment.

The settlement removes a major overhang for Adani's global capital-raising ambitions. The group has been locked out of certain Western debt markets and faced enhanced due diligence from international banks since the indictment. With criminal charges likely to be dropped, those doors could reopen — a crucial consideration as Adani pursues massive infrastructure projects in ports, airports, renewable energy, and data centres.

## The Political Fallout in India

In New Delhi, Congress leader Rahul Gandhi wasted no time. Within hours of the settlement reports, he accused Prime Minister Narendra Modi of negotiating an "Adani release deal" with U.S. authorities — implying that diplomatic capital during Modi's recent multi-nation tour had been spent not on trade or security, but on shielding a politically connected billionaire.

"The Prime Minister went to America and came back with a deal — not for India's farmers, not for India's youth, but for Adani," Gandhi said in a statement, framing it as evidence of crony capitalism.

The BJP dismissed the accusation as "desperate politicking," noting that the settlement was a matter between private parties and a U.S. regulatory agency, and that no Indian government official was a party to the proceedings.

## What NRIs Should Watch

For the Indian diaspora, this case was never just about one billionaire. Adani Group's stocks are among the most widely held by NRI retail investors through Indian brokerage accounts. The indictment had triggered margin calls, portfolio losses, and a crisis of confidence in Indian corporate governance standards.

The settlement, paradoxically, may reassure markets without actually resolving the underlying governance questions. The SEC case is over, but the DOJ's criminal investigation — while expected to be dropped — has not been formally terminated. And the bribery allegations themselves remain unaddressed: no Indian regulatory body has opened a parallel investigation into the claims.

For NRI investors recalibrating their India portfolios, the takeaway is cautiously positive but incomplete. The legal risk premium on Adani stocks has shrunk dramatically. Whether the governance risk premium should follow is a different question entirely — and one that $18 million cannot answer.""",
    "published_at": NOW,
    "status": "published",
})

# ── Article 2: Modi Netherlands Visit (news) ──────────────────────────

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Modi's Hague Playbook: 17 Deals, a Semiconductor Handshake, and a Press Freedom Spat",
    "subheadline": "India and the Netherlands elevated ties to a strategic partnership — then the Dutch Prime Minister brought up minority rights, and the mood shifted.",
    "slug": "modi-netherlands-strategic-partnership-press-freedom-20260517",
    "category": "news",
    "vertical": "politics",
    "urgency": "daily",
    "is_featured": False,
    "score_total": 75,
    "topic_id": "f48867ea-1a8e-46a2-bc8e-e3f48d7deea4",
    "tags": ["PM Modi", "Netherlands", "Rob Jetten", "strategic partnership", "semiconductors", "ASML", "Tata Electronics", "press freedom", "India-EU relations"],
    "sources": [
        {"url": "https://pmindia.gov.in/en/news_updates/roadmap-of-india-netherlands-strategic-partnership-2026-2030/", "name": "PMO India"},
        {"url": "https://www.latestly.com/agency-news/world-news-unparalleled-momentum-pm-modi-hails-india-netherlands-outcomes/", "name": "LatestLY"},
        {"url": "https://www.livemint.com/news/india/pm-modi-netherlands-visit-2026", "name": "Mint"},
        {"url": "https://www.thehindubusinessline.com/economy/india-netherlands-strategic-partnership/", "name": "The Hindu Business Line"},
        {"url": "https://newsdive.net/mea-disputes-dutch-pm-comments-press-freedom/", "name": "NewsDive"},
    ],
    "diaspora_angle": "An estimated 40,000 Indians and PIOs live in the Netherlands — a small but influential community concentrated in The Hague, Amsterdam, and Eindhoven (home to ASML and Philips). The semiconductor partnership between Tata Electronics and ASML could create talent pipelines that benefit Indian engineers. The press freedom exchange, meanwhile, resonated with diaspora communities who regularly field questions from Western colleagues about democratic backsliding in India.",
    "image_search_query": "PM Modi Netherlands Rob Jetten The Hague May 2026",
    "image_entities": ["PM Modi", "Rob Jetten", "The Hague"],
    "image_must_show": "PM Modi meeting Dutch PM Rob Jetten or at The Hague diplomatic event",
    "body": """Prime Minister Narendra Modi's stop in The Hague on Saturday was supposed to be the uncomplicated leg of a five-nation European tour — a handshake-heavy afternoon of memoranda, a photo opportunity at the Afsluitdijk dam, and warm words about €2 billion in potential renewable-energy investments. For the most part, it was. India and the Netherlands signed 17 agreements and formally elevated bilateral ties to a "Strategic Partnership," backed by a five-year roadmap running through 2030.

Then Dutch Prime Minister Rob Jetten mentioned press freedom and minority rights, and the diplomatic choreography stuttered.

## The Deal Sheet

The centrepiece is a semiconductor collaboration agreement between Tata Electronics and ASML, the Dutch lithography giant whose extreme ultraviolet machines are arguably the most strategically important pieces of industrial equipment on earth. India has been courting ASML for years as part of its push to build domestic chip fabrication capacity; this MoU, while short on binding commitments, signals that the relationship has moved beyond exploratory talks.

Beyond chips, the 17 outcomes span green hydrogen development, dairy-sector training (the Netherlands is the world's second-largest agricultural exporter), critical minerals supply chains, defence cooperation, water management, and a joint Indo-Pacific framework. Bilateral trade between the two countries reached $27.8 billion last year, and Dutch foreign direct investment in India stands at $55.6 billion — making the Netherlands India's fourth-largest source of FDI.

"This is unparalleled momentum," Modi said at a joint press appearance, calling the partnership a convergence of Indian scale and Dutch innovation.

## The Uncomfortable Moment

Jetten, however, did not confine his remarks to the transactional. In comments that India's Ministry of External Affairs later characterised as based on "misunderstandings," the Dutch PM raised concerns about press freedom and the treatment of minority communities in India — topics that Western European leaders have increasingly broached in bilateral settings but rarely at joint pressers.

The MEA response was swift and pointed. In an official statement, the ministry said India's democratic credentials were "well-established," cited the country's diverse population and inclusive governance, and noted that minority communities in India had grown in absolute numbers — an implicit rebuttal to claims of systemic marginalisation.

The exchange was diplomatic in tone but unmistakable in substance. It followed a pattern: India increasingly treats such public remarks as protocol breaches, while European leaders — particularly from the Netherlands, Scandinavia, and Germany — view them as standard democratic-values signalling.

## Why Semiconductors Matter More Than the Spat

For the Indian diaspora in Europe and North America, the press freedom exchange will dominate dinner-table conversations. But the semiconductor deal is arguably the more consequential development.

India's ambition to become a chip-manufacturing hub hinges on access to ASML's technology. The company's EUV lithography systems cost upwards of $200 million each and take years to deliver. A formal partnership framework with Tata Electronics — which is building a fabrication plant in Gujarat — could accelerate India's position in the global semiconductor supply chain at a moment when both the U.S. and EU are actively reshoring chip production away from East Asia.

For Indian engineers in the Netherlands — many of whom work at ASML's Eindhoven campus or at Philips — the partnership could create reverse-migration pathways and joint research opportunities that did not previously exist.

## The Bigger Picture

Modi's Netherlands visit is the second stop on a tour that has already included meetings in multiple European capitals. The strategic partnership is India's latest in a growing portfolio that now includes France, Germany, the UK, and the EU itself. Each partnership is structured slightly differently, but the pattern is consistent: India offers market access and demographic scale; European partners offer technology, capital, and — increasingly — geopolitical alignment against Chinese overcapacity.

The press freedom friction, uncomfortable as it was, is unlikely to derail the economic logic. But it serves as a reminder that India's deepening ties with Europe come with a rhetorical tax that Modi's government finds irksome — and that European electorates expect their leaders to collect.""",
    "published_at": NOW,
    "status": "published",
})

# ── Article 3: Indian Worker Killed in Moscow Drone Strike (nri-world) ─

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "An Indian Worker Died in Moscow's Deadliest Drone Night. Thousands More Remain in the Line of Fire.",
    "subheadline": "Ukraine launched over 1,000 drones at Russia on May 17. One struck a site in the Moscow region where Indian nationals were working. The embassy is scrambling — but the bigger question is why so many Indians are still there.",
    "slug": "indian-worker-killed-moscow-drone-strike-ukraine-20260517",
    "category": "nri-world",
    "vertical": "world",
    "urgency": "breaking",
    "is_featured": True,
    "score_total": 80,
    "topic_id": "287b2eb7-9c47-42a6-b64c-30c90c7e4b58",
    "tags": ["Russia-Ukraine war", "Indian diaspora", "Moscow drone strike", "Indian embassy Russia", "NRI safety", "Zelenskyy", "conflict zone workers"],
    "sources": [
        {"url": "https://news.webindia123.com/articles/indian-national-killed-moscow-drone-strike/", "name": "WebIndia123"},
        {"url": "https://www.livemint.com/news/india/indian-staffer-killed-drone-attack-moscow/", "name": "Mint"},
        {"url": "https://www.latestly.com/world/indian-national-killed-moscow-drone-strike/", "name": "LatestLY"},
        {"url": "https://www.tezzbuzz.com/indian-worker-killed-moscow-drone-strike/", "name": "TezzBuzz"},
        {"url": "https://nampa.org/moscow-may-2026-afp-indian-worker-killed-ukraine-drone/", "name": "AFP via NAMPA"},
    ],
    "diaspora_angle": "Thousands of Indian nationals work in Russia — in construction, IT services, security, and increasingly in roles that place them near military or dual-use infrastructure. The killing of an Indian worker in a drone strike is a grim milestone that forces New Delhi to reckon with the safety of its citizens in a country it has studiously avoided criticising over the war. For NRIs watching from the West, it exposes the uncomfortable geopolitics of India's Russia balancing act.",
    "image_search_query": "Moscow drone strike damage May 2026",
    "image_entities": ["Moscow", "drone strike", "Indian embassy Russia"],
    "image_must_show": "Aftermath of drone strike damage in Moscow region or Indian embassy response",
    "body": """An Indian national was killed and three others were injured on Saturday when Ukrainian drones struck a site in the Moscow region where they were working — casualties in what Russian authorities described as the single largest drone assault on the country since the war began in February 2022.

The Indian Embassy in Moscow confirmed the death in a statement, saying officials had visited the site and met with the three injured Indians, who are receiving medical treatment. The embassy did not identify the deceased or the injured, citing privacy and ongoing communication with families in India. It said consular assistance was being provided.

## The Scale of the Attack

Ukraine launched more than 1,000 drones at targets across Russia over a 24-hour period beginning late Friday. Russian air defences claimed to have intercepted the vast majority — over 556 according to one official count, with 81 shot down in the Moscow region alone — but the sheer volume overwhelmed coverage in several areas, causing damage to residential buildings, infrastructure, and what Ukrainian officials described as military-adjacent sites.

President Volodymyr Zelenskyy defended the strikes as a "justified response" to sustained Russian bombardment of Ukrainian cities, claiming the targets were legitimate and that civilian areas were not intentionally struck. Moscow called the attack an act of terror and vowed retaliation.

For the Indian worker who died, the geopolitical framing is irrelevant. He was in the wrong place in a war that India has officially stayed neutral on — and that neutrality now has a human cost measured in Indian blood.

## Indians in Russia: The Invisible Workforce

The killing spotlights a diaspora presence that rarely makes headlines. Thousands of Indian nationals work across Russia, concentrated in Moscow and St. Petersburg but increasingly dispersed to secondary cities and industrial zones. They work in construction, IT outsourcing, security services, and — according to multiple reports over the past two years — in roles that place them near or within facilities that could be considered dual-use by a belligerent.

The Indian government has issued periodic advisories urging citizens in Russia to "exercise caution" and "stay away from conflict zones," but has stopped short of recommending evacuation or restricting travel. The economic incentives for Indian workers in Russia — where labour shortages caused by sanctions and military mobilisation have driven up wages — have continued to draw new arrivals even as the war has intensified.

The three injured Indians are reportedly stable. But the incident raises questions that the embassy's consular response alone cannot answer: How many Indian nationals are currently working in or near areas at risk of drone strikes? What safety protocols, if any, have their employers implemented? And what obligations does the Indian government have to citizens who have voluntarily entered an active conflict zone for employment?

## New Delhi's Tightrope

India's response to the killing will be closely watched. New Delhi has maintained a carefully calibrated position on the Russia-Ukraine war — abstaining from UN votes condemning Russia, continuing to purchase discounted Russian oil, and hosting both Russian and Ukrainian officials for back-channel discussions. Prime Minister Modi's personal relationship with President Vladimir Putin has been a cornerstone of this approach.

But a dead Indian citizen changes the calculus, however slightly. The opposition is likely to demand a stronger travel advisory. Diaspora advocacy groups in the United States and United Kingdom — where Indian communities are closely attuned to the war's human toll — may push for more explicit safety measures.

The MEA's statement on Saturday was measured: it expressed condolences, confirmed assistance to the injured, and said it was "in touch with Russian authorities." It did not attribute blame, criticise the drone strike, or comment on the broader conflict — a studied neutrality that mirrors India's UN posture.

## The Diaspora Dimension

For the million-plus Indian-origin residents of the United States, Canada, and the United Kingdom, the Moscow killing is a reminder that the Indian diaspora's exposure to global conflict zones extends far beyond the well-publicised evacuations from Sudan and Ukraine in earlier years.

Indian workers in Russia occupy a peculiar position: they are there by choice, drawn by economic opportunity, but they are also there because India's diplomatic relationship with Russia has created a permissive environment for labour migration that would not exist if New Delhi had joined Western sanctions.

The worker who died on Saturday — whose name, age, hometown, and family circumstances remain unknown as of this writing — is the latest in a long line of Indians abroad whose individual tragedies illuminate the consequences of collective geopolitical choices. His death will not change India's Russia policy. But it should, at minimum, prompt a harder look at the protections available to Indian citizens who have been, in effect, encouraged by the absence of discouragement to seek their fortunes in a war zone.""",
    "published_at": NOW,
    "status": "published",
})

# ── Insert articles ────────────────────────────────────────────────────

for art in articles:
    art["word_count"] = len(art["body"].split())
    resp = requests.post(f"{API}/p2_articles", headers=HEADERS, json=art)
    if resp.status_code in (200, 201):
        data = resp.json()
        aid = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"✅ Published: [{art['category']}] {art['headline'][:60]}... (id={aid[:8]}, {art['word_count']} words)")
    else:
        print(f"❌ FAILED [{art['category']}]: {resp.status_code} {resp.text[:200]}")

# ── Mark topics as published/rejected ──────────────────────────────────

# Topics used in articles
published_topics = [
    "d3f27533-54e5-4110-bd08-dde9950ec53b",  # Adani settlement
    "b4827ac0-e29b-4f2a-83ac-94a67aaae96e",  # Adani stocks surge (merged into article 1)
    "3e07e233-8e74-4e74-b4ab-ecfc8a3f2db3",  # Rahul Gandhi on Adani (merged into article 1)
    "f48867ea-1a8e-46a2-bc8e-e3f48d7deea4",  # Modi Netherlands visit
    "8143de57-7a65-4ab5-9c96-47934fa9d835",  # India rejects Dutch PM press freedom remarks (merged into article 2)
    "287b2eb7-9c47-42a6-b64c-30c90c7e4b58",  # Indian killed in Moscow
]

# Topics to reject (low diaspora relevance, celebrity gossip, not newsworthy enough)
rejected_topics = [
    "0adeb35a-ebf1-4cac-b2d5-8c9bcbf6a83d",  # Savannah James (not diaspora)
    "4625ba23-0228-4d23-892f-e750d758ef53",  # CBSE re-evaluation fees (minor)
    "a0c2eee3-387e-4b2a-b66d-ee26cd4aa5ac",  # Supreme Court judge strength (minor)
    "83d08d09-9506-4403-bdda-c7998e966189",  # Shaheen Afridi dressing room spat (sports gossip)
    "9c29ab4f-1fa2-4559-a038-02ff183728ff",  # Vivek Dahiya pregnancy (celeb gossip - already covered in entertainment)
    "e2d9a49d-6fa9-4e76-b817-8ede6305804d",  # Rayudu on Narine (duplicate)
    "f5f126b9-8288-4a56-8054-4feb64da4305",  # Rayudu on Narine (duplicate)
    "e5c9c38e-65dd-41c7-958a-ad64b458577f",  # Venus Williams French Open (not diaspora)
    "cc0409df-06db-449f-aed2-227893ac6176",  # Alamgir Alam bail (minor legal)
    "e825aea5-d12b-4788-9dc9-dd7dbcc78cb1",  # ED arrests Mahesh Yogi fraud (minor)
    "7dea9f37-d87e-412a-91c6-c119ac523f3d",  # Calcutta HC dowry case acquittal (minor legal)
    "4d2a1ed4-73d4-493a-893b-eea9d52b56e5",  # NEET UG correction window (minor admin)
    "2c2e65e4-412b-40f6-a3b1-3f02bc2c0b6a",  # Virat Kohli retirement (sports, not this category)
    "ef542d67-1d08-46e4-af92-59b92d989334",  # Michael Jackson biopic (entertainment, not this category)
    "3fc62987-e864-4cbf-819c-62925e10709c",  # Lucknow lawyers clash (minor local)
]

for tid in published_topics:
    resp = requests.patch(
        f"{API}/p2_topics?id=eq.{tid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "published", "updated_at": NOW},
    )
    status = "✅" if resp.status_code in (200, 204) else "❌"
    print(f"{status} Topic {tid[:8]}... → published ({resp.status_code})")

for tid in rejected_topics:
    resp = requests.patch(
        f"{API}/p2_topics?id=eq.{tid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "rejected", "updated_at": NOW},
    )
    status = "✅" if resp.status_code in (200, 204) else "❌"
    print(f"{status} Topic {tid[:8]}... → rejected ({resp.status_code})")

print(f"\nDone. {len(articles)} articles published, {len(published_topics)} topics published, {len(rejected_topics)} topics rejected.")
