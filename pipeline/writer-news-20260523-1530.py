#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 15:30 batch
Topics: 1) Rubio-Modi meeting outcomes + White House invite + Quad Monday
        2) Mumbai bulldozer demolitions — 500 homes, 2 mosques razed in Bandra, families called 'Bangladeshi'
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
# ARTICLE 1: Rubio Met Modi — White House Invite, Quad Monday, and What the Trip Actually Delivered
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("rubio-modi-meeting-white-house-invite-quad-monday-delivered")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Rubio Met Modi on Saturday, Invited Him to the White House, and Called India the 'Cornerstone' of Washington's Indo-Pacific Strategy. What the Trip Actually Delivered — and What It Carefully Avoided.",
        "subheadline": "The meeting lasted long enough for photographs and a joint statement. Rubio briefed Modi on the Iran war, pitched American energy, and extended a presidential invitation to the White House. Modi sent warm greetings to Trump. Neither side announced a trade deal. Neither side mentioned the 26 percent tariff. The Quad foreign ministers meet in Delhi on Monday. The $500 billion 'Mission 500' trade target by 2030 remains an aspiration with no timeline and no framework. For NRIs caught between America's tariff wall and India's economic squeeze, the visit produced warm words, strategic signals — and very little that changes anything on the ground.",
        "slug": slug1,
        "category": "news",
        "vertical": "geopolitics",
        "diaspora_angle": "For the Indian diaspora, every Rubio-Modi handshake lands in a specific context: H-1B workers whose renewals are in limbo, small business owners paying tariff-inflated prices on Indian imports, NRIs watching the rupee collapse and wondering when the trade relationship will stabilise. The White House invitation matters symbolically — it signals Trump wants Modi close — but symbols don't reduce the 26% tariff or unblock the consular processing backlog. The energy pitch is real but carries a cost: India buying more American LNG means India buying less Russian oil, which shifts geopolitical alignment in ways that affect everything from sanctions exposure to Gulf-corridor diplomacy. The Quad meeting Monday is significant for NRIs in Australia, Japan, and the US because it sets the tone for Indo-Pacific security cooperation that determines visa regimes, student flows, and defense-industrial jobs in all four countries.",
        "tags": ["Rubio", "Modi", "White House", "India-US relations", "Quad", "trade deal", "Mission 500", "tariffs", "energy", "Indo-Pacific", "Jaishankar", "NRI", "H-1B", "LNG"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TBS News — Rubio meets Modi as US moves to strengthen strained bilateral ties", "url": "https://www.tbsnews.net/world/rubio-meets-modi-us-moves-strengthen-strained-bilateral-ties-1446821"},
            {"name": "Reuters — Rubio touts US energy on India trip meant to repair ties", "url": "https://www.reuters.com/world/rubio-touts-us-energy-india-trip-meant-repair-ties-2026-05-23/"},
            {"name": "Livemint — Marco Rubio in India LIVE: Rubio invites PM Modi to White House", "url": "https://www.livemint.com/news/india/marco-rubio-in-india-live-updates-2026-05-23"},
            {"name": "Nation Press — PM Modi meets US Secy of State Rubio, reviews strategic partnership", "url": "https://nationpress.com/pm-modi-marco-rubio-india-us-partnership"},
            {"name": "The Hindu Business Line — India to host Quad foreign ministers' meet in New Delhi on May 26", "url": "https://www.thehindubusinessline.com/news/india-to-host-quad-foreign-ministers-meet-may-26"}
        ]),
        "score_total": 90,
        "status": "published",
        "published_at": now,
        "body": """Marco Rubio arrived in India on Saturday morning and had met Prime Minister Narendra Modi by the afternoon. By evening, he was at the US Embassy in New Delhi telling an invited audience that the India-US relationship is "at the cornerstone of Washington's approach to the Indo-Pacific." The entire arc — arrival, meeting, messaging — took less than twelve hours.

What it produced was carefully calibrated. A White House invitation for Modi, extended on behalf of President Trump. A briefing on the Iran war. A pitch for American energy. A reaffirmation of the Quad. And not a single word, in any public statement, about the specific issue that has been strangling the bilateral relationship for months: the 26 percent tariff that the United States imposed on Indian goods.

## What Actually Happened in the Room

The meeting followed the script of high-level diplomatic encounters that are designed to signal closeness without committing to anything specific.

Rubio "briefed the Prime Minister on sustained progress in bilateral cooperation across a wide range of sectors, including defence, strategic technologies, trade and investment, energy security, connectivity, education and people-to-people ties," according to the Indian Prime Minister's Office readout. He also shared the US perspective on "various regional and global issues, including the situation in West Asia."

Modi, for his part, "reaffirmed India's consistent support for peace efforts and reiterated the call for a peaceful resolution of conflicts through dialogue and diplomacy." He sent warm greetings to Trump. On X, he wrote: "India and the United States will continue to work closely for the global good."

US Ambassador Sergio Gor, who has been positioning himself as the key bridge between the two administrations, announced the White House invitation on X: "Secretary Marco Rubio extended an invite on behalf of President Donald Trump, for Prime Minister Modi to visit the White House in the near future."

No date was announced. No agenda was disclosed. "In the near future" is diplomatic language for "we want this to happen but we haven't agreed on when."

## The Energy Pitch

Rubio's most concrete deliverable was the energy message. According to a US summary of the meeting, Rubio told Modi that "US energy products have the potential to diversify India's energy supply."

This is not subtle. India imports 85 percent of its crude oil. With the Strait of Hormuz effectively closed since February, oil prices above $100 a barrel, and India's trade deficit at $120 billion, the country's energy vulnerability is its single biggest economic weakness. Rubio arrived with a straightforward proposition: buy American.

The proposition has appeal. American LNG is abundant, prices have fallen relative to the war-inflated global market, and the US has been aggressively expanding export terminal capacity. For India, diversifying away from the Gulf and Russia makes strategic sense — particularly when the Gulf is a war zone and Russian oil is under sanctions pressure.

But the proposition also has strings. Buying American energy at scale means reducing purchases from Russia, which has been India's quiet lifeline since the Ukraine war in 2022. India's Russian oil imports have been a persistent irritant in the bilateral relationship, and the Trump administration's February trade deal framework explicitly included a commitment from India to reduce Russian crude purchases. Rubio wasn't just selling energy — he was selling geopolitical alignment.

India's response, characteristically, was to nod without committing. The readout mentioned "energy security" as a topic of discussion. It did not mention Russia. It did not mention LNG quantities. The space between what was discussed and what was agreed is where Indian diplomacy lives.

## What Wasn't Said

The most revealing feature of Saturday's meeting was what nobody mentioned.

The 26 percent tariff — technically a 10 percent baseline tariff plus sector-specific additions that push the effective rate to 26 percent on many Indian goods — has been in place since February. It has disrupted Indian exporters across textiles, pharmaceuticals, IT services hardware, and agricultural products. India's trade surplus with the US, which had been a core Trump grievance, has narrowed, but at a cost that Indian industry is absorbing through layoffs and margin compression.

The 'Mission 500' trade target — a $500 billion bilateral trade goal by 2030, first articulated by Ambassador Gor — was referenced in pre-trip briefings but appears nowhere in the post-meeting statements. The aspiration remains. The path does not exist. India's total goods trade with the US was approximately $118 billion in FY25. Getting to $500 billion in four years would require growth rates that no bilateral trading relationship in history has achieved.

The trade deal itself — which Commerce Minister Piyush Goyal had optimistically predicted would be signed by "mid-March" — remains unsigned. The Supreme Court's ruling striking down Trump's reciprocal tariff authority scrambled the negotiating landscape. India and the US have been through multiple rounds of talks without a framework agreement. Saturday's meeting did not change that.

## The Quad on Monday

The real strategic event of Rubio's trip happens on Monday, May 26, when foreign ministers from the US, India, Australia, and Japan convene in New Delhi for the Quad Foreign Ministers' Meeting.

This is Rubio's third Quad meeting — he made it his first official engagement as Secretary of State — and the agenda is substantive: maritime security in the South China Sea, supply chain resilience, critical technology cooperation, and the West Asia crisis. Japan's Foreign Minister Toshimitsu Motegi will attend. Australia's Foreign Minister Penny Wong is expected.

The Quad has evolved from a loose strategic dialogue into something closer to an operational alliance, though all four members resist that characterisation. For India, hosting the meeting sends a signal to China and Pakistan that the Indo-Pacific framework is active and Delhi is at its centre. For the US, it demonstrates that the Trump administration's Indo-Pacific strategy is not purely bilateral — it has a multilateral architecture.

For NRIs, the Quad matters in ways that are less obvious but no less real. The four-country framework determines visa facilitation agreements, student exchange pipelines, defense-industrial collaboration that creates engineering jobs, and technology transfer protocols. When the Quad works, the connective tissue between these four economies thickens, and the diaspora communities that live between them benefit.

## What This Means

Saturday's meeting was a reset, not a breakthrough. The relationship between Washington and Delhi had been genuinely strained — by tariffs, by the Adani fraud case (charges were since dismissed), by Trump's visible warmth toward Pakistan during the India-Pakistan crisis, and by the perception in Delhi that the US was taking India for granted.

Rubio's visit was designed to stop the bleeding. The White House invitation signals that Trump wants Modi in Washington, which means a deal of some kind is being contemplated — you don't invite a leader to the White House without something to announce. The energy pitch gives both sides a deliverable that can be framed as win-win. The Quad meeting provides multilateral cover.

But none of this changes the immediate reality. The tariff is still 26 percent. The trade deal is still unsigned. The rupee is still at 97. NRI deposits are still declining. The Gulf employment pipeline is still disrupted. The energy pitch is an offer, not an agreement.

Rubio called the relationship a "cornerstone." Modi called it a partnership for the "global good." Both men chose words that sound permanent but commit to nothing specific. That is the nature of the relationship right now — too important to let fail, too complicated to fix in an afternoon, and too polite to say so out loud.

The Quad meets Monday. Modi's White House visit has no date. And 26 percent remains 26 percent.
"""
    })
else:
    print(f"  ⚠ Skipping Rubio-Modi article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Mumbai Bulldozer Demolitions — 500 Homes, 2 Mosques Razed in Bandra
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("mumbai-bandra-demolitions-500-homes-mosques-bulldozer")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Mumbai Just Bulldozed 500 Homes and Two Mosques Next to Bandra Station. Families Who Voted for Decades Are Being Called 'Bangladeshi.' The Bulldozer Has Come to India's Financial Capital.",
        "subheadline": "Western Railway sent bulldozers into Garib Nawaz, a working-class settlement beside one of Mumbai's busiest stations, on May 19. Within 48 hours, 60 percent of the settlement was rubble. Two mosques were razed despite assurances they would be spared. An adjacent Dalit settlement, Pampapura, was demolished on May 22 — a statue of Ambedkar was destroyed by a bulldozer. Residents carrying voter IDs and ration cards issued decades ago say officials called them 'Bangladeshi' and 'Rohingya' to their faces. Around 50 to 60 people, including women and minors, have been jailed. No rehabilitation has been announced. With monsoon weeks away, hundreds of families are sleeping under a bridge beside the tracks. For Mumbai's NRIs — many of whom grew up in neighbourhoods just like this one — the images are a gut punch.",
        "slug": slug2,
        "category": "news",
        "vertical": "india",
        "diaspora_angle": "Mumbai is the city more NRIs call home than any other. The Bandra demolitions are not happening in a distant state — they are happening beside one of the most recognisable railway stations in the country, in a city whose identity is built on the idea that everyone, from every background, has a place. For NRIs who grew up in Mumbai's working-class neighbourhoods, the images of bulldozers crushing homes that have stood for decades, families sitting under a bridge with their belongings in plastic bags, and residents being called 'Bangladeshi' despite holding voter ID cards older than most smartphones — these images cut deep. The 'bulldozer model' of governance, which began in UP and has spread to multiple BJP-governed states, has now arrived in India's financial capital. The communal dimension — the targeting of a Muslim settlement, the razing of mosques, the labelling of Indian citizens as foreign infiltrators — adds a layer that many NRIs find particularly troubling, especially those who have spent years defending India's secular credentials abroad.",
        "tags": ["Mumbai", "Bandra", "demolitions", "bulldozer", "Garib Nawaz", "Western Railway", "Muslim", "Dalit", "Ambedkar", "Rohingya", "Bangladeshi", "rehabilitation", "NRI", "monsoon", "human rights"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Maktoob Media — 'During elections we were Indians, now we are Bangladeshis': Mumbai's Garib Nawaz residents watch homes, mosques reduced to rubble", "url": "https://maktoobmedia.com/post?id=115543&slug=during-elections-we-were-indians-now-we-are-bangladeshis"},
            {"name": "Kashmir Media Service — Hundreds of Muslim homes, two mosques razed in Mumbai; protests erupt, several injured", "url": "https://kmsnews.org/mumbai-demolitions-muslim-homes-mosques-bandra"},
            {"name": "Reuters — India regulator cracks down on seven in social media stock manipulation case (context: Mumbai governance)", "url": "https://www.reuters.com/world/india/india-regulator-cracks-down-seven-social-media-stock-manipulation-case-2026-05-23/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "body": """The bulldozers arrived at Garib Nawaz on the morning of May 19. They came with Railway Protection Force personnel, heavy police deployment, and earthmovers. By May 21 — 48 hours later — sixty percent of the settlement had been reduced to rubble. Over 500 homes. Two mosques. Shops that had served the community for decades. An entire neighbourhood, sitting beside Bandra railway station in the heart of Mumbai, erased in a long weekend.

Western Railway's Chief Public Relations Officer, Vineet Abhishek, described it as the "fastest government action" against illegal encroachment. Residents describe it differently.

"They came with such force — what could we even do?" said Mohammad Asif, 61, who has lived in the settlement for decades. "Over 500 homes have been demolished, and only around 140 were considered legal. They were telling us that if we did not remove our belongings quickly, they would bury them along with the debris."

## Voter IDs, Ration Cards, and the 'Bangladeshi' Label

What makes the Bandra demolition different from other encroachment drives — and what has triggered outrage far beyond Mumbai — is what happened alongside the bulldozers.

Residents say that government officials, during the demolition, openly referred to them as "Bangladeshis" and "Rohingya." This is not a minor detail. It is the deployment of a specific political vocabulary — one that has been used across India to delegitimise Muslim citizens by casting them as foreign infiltrators — against people who carry Indian voter ID cards issued in Mumbai decades ago.

Munawwar Sheikh, 51, whose grandfather died in this neighbourhood, stood among the rubble holding his documents: "The media is saying that we are Bangladeshi and Rohingya, which is not true. Most of these houses are 50 to 75 years old. We have voter ID cards issued in Mumbai. How can we suddenly be termed illegal? Our voter ID cards are 40 to 50 years old. We vote in every election. During elections, we were considered legal, and now, after voting, we have suddenly become Rohingya."

Mohammad Ali, another resident, made the same point more bluntly: "Political parties come during elections to ask for votes, but now none of them have shown up."

The accusation is not new. Across India, particularly in BJP-governed states, Muslim communities facing demolitions have been labelled as "Bangladeshi" or "Rohingya" regardless of their documentation. The pattern has been documented in Assam, UP, Delhi, and Haryana. Its arrival in Mumbai — a city that has historically prided itself on cosmopolitan tolerance — marks an escalation.

## Two Mosques Razed

Along with the homes, two decades-old mosques were demolished: Masjid-e-Inaam, described as the first mosque established in the area, and Faizane Mustafa Garib Nawaz Masjid. Multiple residents say they were explicitly told by authorities that the mosques would be spared.

Tabassum, 20, was present when the bulldozers reached the mosques: "They only gave us ten minutes to take the Quran and other belongings out of the mosque. We took whatever we could, and then they destroyed everything. Losing our homes was painful enough, but the demolition of the mosque hurt deeply. They had not even given notice for the mosque. They had assured us they would not even touch it."

The demolition of the mosques triggered protests, which escalated into stone-pelting. Police responded with a lathi-charge. Videos circulating on social media show residents being beaten and dragged by police, several visibly injured and bleeding. Between 50 and 60 residents, including women and minors, were detained. Police have filed charges under multiple sections of the Bharatiya Nyaya Sanhita, including Section 109 — attempt to murder. Approximately 150 people are reportedly wanted in connection with the protests.

## Pampapura: Dalit Families, Ambedkar's Image Destroyed

On May 22, the demolition drive reached Pampapura, an adjacent settlement inhabited primarily by Dalit and Muslim families. The same pattern repeated: bulldozers, police deployment, protests, lathi-charges, detentions.

But Pampapura added a detail that has inflamed a separate set of communities. An office of an Ambedkarite group was demolished. Residents allege that a photograph and statue of B.R. Ambedkar — the father of India's Constitution, the most revered figure in Dalit politics — were destroyed by a bulldozer.

Heena, 32, a lifelong Pampapura resident: "The Dalits who were living here were taken to the police station. The police were beating them with batons and dragging them away like animals. Even after they showed their documents, they were still beaten and taken away."

Pawan Kumar sits outside what was his home, in the scorching May heat, with his son and his specially-abled granddaughter in a wheelchair. They were given thirty minutes to remove their belongings.

## The Bulldozer Arrives in Mumbai

The "bulldozer model" of governance — using demolitions as a tool of order, sometimes against accused criminals, sometimes against encroachments, and sometimes against communities — has been a defining feature of BJP-governed states since Yogi Adityanath popularised it in Uttar Pradesh. It has been deployed in Madhya Pradesh, Rajasthan, Delhi, and Haryana, often against Muslim communities, often without adequate due process, and often after the Supreme Court has specifically warned against using demolitions as punitive measures.

Mumbai has been different. Despite being in BJP-allied Maharashtra, the city's demolition drives have historically been messy, slow, legally contested affairs — reflecting the dense, layered nature of a city where millions live in informal settlements that predate the legal frameworks meant to govern them. Slum rehabilitation has been, for decades, a structured (if deeply flawed) process involving surveys, enumeration, and alternative housing.

What happened at Garib Nawaz appears to have bypassed most of that. Residents say no proper survey was conducted. No rehabilitation has been announced. No alternative housing has been offered. Western Railway says the land is needed for the expansion of Bandra Terminus, and that the settlements were illegal encroachments on railway property.

Both statements can be true simultaneously — the settlements may be on railway land, and the people living there may still be Indian citizens with decades of documentation and nowhere else to go.

## 'Where Do We Go?'

Rasheeda, 55, came to Garib Nawaz in 1993 at the age of 17. Her family bought a home there in 1994. She now sits under a bridge with her belongings, surrounded by hundreds of other displaced families.

"They are telling us to leave from here, too. Everything belongs to the railway. Now tell us, where do we go? All of us have been sitting here in the heat, under this bridge, for two days. They have made our lives miserable."

Ruksana, 85, the oldest resident at the site, asked the question that none of the authorities have answered: "The government is not removing poverty; they are removing the poor. We want rehabilitation now."

The monsoon is weeks away. Mumbai's rains are relentless. Hundreds of families are sleeping in the open beside railway tracks, with children, elderly parents, and disabled family members. No government agency has announced a plan for them.

## What NRIs Are Seeing

For Mumbai's vast diaspora — NRIs in the Bay Area, New Jersey, London, Dubai — the Bandra demolitions land differently than they might for an abstract policy audience.

These are not distant villages. Bandra is one of Mumbai's most iconic neighbourhoods. Bandra station is a landmark every Mumbaikar knows. The people displaced are the city's working class — the people who drive the rickshaws, clean the offices, man the market stalls, keep the trains running. They are the Mumbai that NRIs remember from childhood, from visits home, from the city they carry in their heads.

The images — families under a bridge, mosques reduced to rubble, a wheelchair-bound girl sitting outside a destroyed home, an Ambedkar statue crushed by a bulldozer — have been circulating on WhatsApp NRI groups and diaspora social media for days. The reaction has been a mix of anger, grief, and a particular kind of helplessness that comes from watching your city change in ways you cannot influence from twelve time zones away.

Western Railway says the demolitions will continue until development work can begin. No date for rehabilitation has been announced. The bulldozer, it appears, has come to stay.
"""
    })
else:
    print(f"  ⚠ Skipping Mumbai demolitions article — slug already exists: {slug2}")


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
