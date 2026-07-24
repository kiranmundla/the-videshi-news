#!/usr/bin/env python3
"""Write 4 articles for The Videshi — news writer run 2026-05-19"""

import json
import os
import uuid
import datetime
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

TODAY = "20260519"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

articles = []

# ─────────────────────────────────────────────────────
# ARTICLE 1: nri-world — H-1B Visa Debate
# Topics: 4b2b9d8c, 33f10289, 8de47dcb
# ─────────────────────────────────────────────────────
articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "4b2b9d8c-e744-49df-8291-d5ae70561f07",
    "headline": "DeSantis Calls Out Silicon Valley's H-1B 'Hypocrisy' as Indian Workers Face an Uncertain American Dream",
    "subheadline": "The Florida governor accuses tech giants of pushing AI layoffs while lobbying for cheap foreign labour — and the diaspora is caught in the crossfire",
    "slug": f"desantis-h1b-hypocrisy-indian-workers-uncertain-american-dream-{TODAY}",
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "H-1B visa holders — overwhelmingly Indian — face a dual threat: AI displacing the jobs they came for, and a political class using them as a talking point. For NRIs weighing a US move, the calculus has never been more complex.",
    "tags": ["H-1B", "Ron DeSantis", "AI jobs", "immigration", "Silicon Valley", "Indian workers", "visa policy"],
    "urgency": "high",
    "sources": [
        "American Bazaar Online — 'Trump ally Ron DeSantis questions tech industry over AI and H-1B visas' (May 2026)",
        "Market Pulse — 'DeSantis Blasts Tech Giants AI-Driven Layoffs and H-1B Hypocrisy'",
        "Benzinga — Mustafa Suleyman AI white-collar job automation comments",
        "US DHS H-1B filing data 2025-2026"
    ],
    "score_total": 78,
    "status": "published",
    "published_at": NOW,
    "body": """Florida Governor Ron DeSantis has fired a broadside at America's biggest technology companies, accusing them of a glaring contradiction: warning that artificial intelligence will destroy white-collar jobs while simultaneously lobbying Washington to expand the H-1B visa programme that brings hundreds of thousands of skilled foreign workers — most of them Indian — to the United States each year.

## The Tweet That Lit the Fuse

"Tech folks forecasting the end of white-collar jobs while at the same time clinging to foreign visa programmes that utilise cheap labour," DeSantis wrote on X this week, adding that it was "not hard to see why people view Big Tech unfavourably." The comment was a direct response to remarks by Microsoft's AI chief, Mustafa Suleyman, who warned that AI systems could automate many professional roles within 18 months.

DeSantis's intervention lands at a volatile intersection of technology policy and immigration politics. The H-1B programme has long been the primary gateway for Indian engineers and IT professionals seeking to work in the United States, with Indians accounting for roughly 72 per cent of all approved H-1B petitions in recent years.

## A Shifting Landscape

The numbers tell a story of an industry in flux. H-1B filings from several major tech firms — including Amazon, Google, and Meta — declined sharply in late 2025 even as their AI investments accelerated. Meta alone announced plans to reassign 7,000 employees into AI-focused roles while cutting thousands of managerial positions. Microsoft, Google, and a wave of smaller firms have followed suit, framing AI as both an existential priority and a reason to rethink headcount.

For Indian tech workers on H-1B visas, the implications are acute. A layoff does not simply mean searching for a new job; it starts a 60-day clock to find a new sponsor or leave the country. Workers who have spent a decade in the US green card backlog — a line that for Indian nationals can stretch to 40 years — risk losing everything overnight.

## The Political Squeeze

DeSantis has already backed legislation in Florida restricting H-1B hiring at state universities and has positioned himself as a champion of "American workers first." His comments align with a broader Republican push, amplified during President Trump's second term, to tighten scrutiny of corporate immigration programmes while arguing that US workers deserve greater protection during technological upheaval.

Yet the political landscape is not monochrome. Congresswoman Pramila Jayapal, a Seattle Democrat of Indian origin, struck a different note this week, expressing concern over immigrant families "living in fear" amid the shifting enforcement climate. Indian-American advocacy groups have warned that anti-H-1B rhetoric risks painting an entire community — one that generates billions in tax revenue and has founded a disproportionate share of US startups — as a liability rather than an asset.

## The Diaspora Calculus

On social media and in WhatsApp groups from Sunnyvale to Hyderabad, the debate has turned intensely personal. One widely shared post from an Indian software engineer cautioned prospective migrants to "think very carefully about moving to America in 2026," citing declining opportunities, rising hostility, and an AI-driven job market that no longer guarantees the stability that once made the H-1B route worthwhile.

The irony is not lost on observers: the same Indian engineers who built the AI systems now threatening to automate jobs are among the first to feel the consequences. India's IT outsourcing giants — TCS, Infosys, Wipro — have historically been among the largest H-1B sponsors, and any tightening of the programme reverberates through Bengaluru and Pune as much as through San Jose.

## What Comes Next

DeSantis did not announce new policy proposals in his latest remarks, but the direction of travel is clear. A bipartisan push for H-1B reform — raising minimum salary thresholds, capping per-employer allocations, and linking visa renewals to market conditions — is gaining momentum in Congress. For Indian professionals, the question is no longer just "Can I get a visa?" but "Is the visa still worth it?"

The American Dream has not died. But for hundreds of thousands of Indians who have staked their careers on it, the fine print has never been more daunting — or more politically charged.""",
    "word_count": 680
})

# ─────────────────────────────────────────────────────
# ARTICLE 2: news — Manipur Conflict
# Topics: d6b91666, 3bb98a51, 0234d360, 2d1736fc
# ─────────────────────────────────────────────────────
articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "d6b91666-7693-448f-b80f-072a0a798918",
    "headline": "Three Church Leaders Killed in Manipur Ambush as Naga-Kuki Violence Opens a Dangerous New Front",
    "subheadline": "The killing of Baptist pastors and a hostage crisis involving both communities signals that India's northeast conflict has metastasised beyond the original Meitei-Kuki fault line",
    "slug": f"manipur-church-leaders-killed-naga-kuki-violence-new-front-{TODAY}",
    "category": "news",
    "vertical": "news",
    "diaspora_angle": "The Manipur crisis — now in its third year — has galvanised diaspora communities in the US, UK, and Canada, where Kuki-Zo, Naga, and Meitei organisations lobby their host governments and raise funds. NRIs with family in the affected districts face mounting anxiety as violence escalates.",
    "tags": ["Manipur", "Naga-Kuki conflict", "church leaders", "ethnic violence", "northeast India", "hostage crisis"],
    "urgency": "high",
    "sources": [
        "Global India Broadcast News — 'Tensions rise in Manipur as Kuki Zo and Naga protest against the killing of church leaders'",
        "News Dive — 'Tensions Rise in Manipur Amidst Weddings, Abductions, and Disappearances in Kuki-Naga Conflict'",
        "Daily Kiran — 'Church Leaders Initiate Peace Efforts Amid Rising Tensions Between Kuki and Naga Communities'",
        "Wikipedia — 2023-2026 Manipur conflict overview"
    ],
    "score_total": 66,
    "status": "published",
    "published_at": NOW,
    "body": """Three senior leaders of the Thadou Baptist Association were killed and four others injured on Wednesday when militants ambushed two vehicles on the road between Kangpokpi and Churachandpur in Manipur's Kangpokpi district. A Naga man was killed in a separate attack in Noni district the same evening. The twin strikes mark a perilous escalation in a conflict that has now drawn in communities previously on its margins.

## A Third Axis of Violence

Since May 2023, Manipur's crisis has been defined primarily as a Meitei-Kuki ethnic war — one that has killed at least 258 people, displaced 60,000, and shattered religious sites on both sides. But the latest violence introduces a Naga-Kuki dimension that security analysts have long feared. The Tangkhul Naga and Kuki-Zo communities, who share parts of the state's hill districts, have been drawn into a cycle of retaliatory attacks and abductions that complicates an already intractable situation.

Following the ambush, both sides took hostages. Approximately 38 individuals from Kuki and Naga communities were detained in the immediate aftermath. While 28 — 14 from each group — were released by Friday, at least six Naga civilians remained in Kuki custody as of the weekend, prompting the United Naga Council to issue a Saturday afternoon deadline for their safe return.

## Parallel Protests, Conflicting Demands

The response was swift and organised on both sides. In Churachandpur, the Kuki Women's Organisation for Human Rights staged a massive rally to denounce the killing of the three pastors and submitted a memorandum to Union Home Minister Amit Shah demanding the reimposition of President's rule, a high-level investigation, and — critically — action on the long-standing political demand for a separate administration for the Kuki-Zo people.

In Imphal West, Naga civic bodies joined forces with the Coordination Committee on Integrity of Manipur to organise a human chain protest demanding the immediate release of the six Naga civilians. The Kuki-Zo Council, for its part, sent a formal appeal to Prime Minister Modi for a separate Union Territory — a demand that would redraw Manipur's political map entirely.

## The Church's Fragile Diplomacy

With the state government struggling to assert authority, church leaders stepped into the breach. A 10-member interfaith delegation met Chief Minister N. Biren Singh and his deputy, then split into two teams to engage directly with both communities in Kangpokpi and Senapati districts. By Thursday, the initiative had helped secure the release of 30 hostages.

But the peace effort faces a structural problem: the underlying grievances — land rights, political representation, ethnic identity, and access to resources — are unchanged. The Kuki-Zo demand for a separate administration is non-negotiable for its proponents and unacceptable to Meitei and Naga groups that see it as a partition of their state. Delhi's reluctance to wade into these waters has left a vacuum that armed groups are filling.

## A Crisis With No Off-Ramp

Three years in, the Manipur conflict shows no sign of resolution. The new Naga-Kuki front is particularly alarming because it fractures the hill-community solidarity that had occasionally served as a counterweight to Meitei dominance. Security forces, already stretched thin, now face multiple flashpoints across an increasingly fragmented landscape.

For the diaspora — Kuki-Zo, Naga, and Meitei communities in the US, UK, and Canada have been vocal fundraisers, lobbyists, and organisers since 2023 — the latest violence is a grim reminder that distance offers no insulation from the trauma. WhatsApp groups light up with each new incident; GoFundMe campaigns for displaced families circulate weekly. The fear, expressed by many NRIs with family in the affected districts, is that the killing of church leaders signals a conflict that is not winding down but widening.

India's national media has largely moved on from Manipur. The people living through it have not.""",
    "word_count": 650
})

# ─────────────────────────────────────────────────────
# ARTICLE 3: technology — Lenskart Smart Glasses
# Topic: 4114eac0
# ─────────────────────────────────────────────────────
articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "4114eac0-2697-4cdf-b1f0-c966d83ceaa7",
    "headline": "Lenskart Just Launched AI-Powered Smart Glasses for ₹22,000 — and 35,000 Indians Have Already Signed Up",
    "subheadline": "B by Lenskart packs Google Gemini, a 12 MP camera, and Hinglish-speaking AI into a 40-gram frame designed to be worn all day",
    "slug": f"lenskart-b-smart-glasses-google-gemini-india-launch-{TODAY}",
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Lenskart — already a household name among Indian-Americans who buy prescription glasses on trips home — is signalling that India can build consumer hardware to compete globally. For NRIs, it is also a reminder that India's tech ecosystem is no longer just a services play.",
    "tags": ["Lenskart", "smart glasses", "Google Gemini", "AI wearables", "India tech", "Peyush Bansal"],
    "urgency": "medium",
    "sources": [
        "Local Samosa — 'Lenskart Launches AI-Powered Smart Glasses B by Lenskart in India' (May 2026)",
        "Technuter — 'Lenskart Brings AI-Powered Smart Glasses to India with Early Access Launch'",
        "The Mainstream — 'Lenskart launches AI-powered smart glasses with Buddy assistant in India'",
        "Smartprix — India smart glasses pricing comparison May 2026"
    ],
    "score_total": 68,
    "status": "published",
    "published_at": NOW,
    "body": """Lenskart has officially launched B by Lenskart, a pair of AI-powered smart glasses that the company says were engineered entirely in India. The product, which went on early-access sale this week after accumulating more than 35,000 registrations since its waitlist opened on 31 March, is priced at ₹22,000 for early adopters and ₹27,000 at retail — a fraction of what comparable devices from Meta or Google cost in Western markets.

## What You Get for ₹22,000

The glasses weigh 40 grams — roughly the same as a standard pair of prescription frames — and pack a surprising amount of technology into that form factor. A 12 MP Sony sensor captures 4K photographs and HD video. A three-microphone array handles calls and voice commands. Directional speakers offer three modes (Discreet, Normal, and Boosted) for different environments. The battery, charged via a temple-tip cable that plugs into a phone charger, lasts a claimed 48 hours with a charging case.

But the headline feature is Buddy, an AI assistant powered by Google's Gemini model. Buddy can converse in over 40 languages, including Hinglish and several regional Indian languages, and is designed to respond contextually to what the wearer sees — a capability that positions it squarely against Meta's Ray-Ban smart glasses and their built-in Meta AI.

An LED indicator light activates automatically whenever photos or videos are being recorded — a privacy nod that the industry has largely settled on as a minimum standard.

## Why It Matters

Lenskart is not a hardware startup fumbling through its first product launch. It is India's largest eyewear retailer, with over 2,500 stores across the country and a customer base that extends into the diaspora. CEO Peyush Bansal — a Shark Tank India judge and a household name — has framed B by Lenskart as a statement of ambition: "We wanted to create smart glasses that are eyewear first, comfortable, stylish, and practical enough to be worn all day."

The "glasses first" philosophy is deliberate. Where many smart glasses feel like gadgets that happen to sit on your face, Lenskart has designed these to pass as normal eyewear — complete with Japanese ultra-thin blue-light lenses. The bet is that Indians will adopt wearable AI if it does not look like wearable AI.

## The Competitive Landscape

At ₹22,000 (roughly $260), B by Lenskart undercuts Meta's Ray-Ban Stories, which retail for $299 in the US and are not officially sold in India. Google's own AI glasses remain in prototype. Chinese competitors like Xiaomi's AI Smart Glasses (₹21,999) and Meizu's MYVU Force Blue (₹26,499) are listed in India but are largely still "upcoming." Lenskart, with its massive retail footprint and established supply chain, has a distribution advantage that no Chinese brand can match domestically.

The Qualcomm Snapdragon AR1 chip under the hood — the same platform powering several global smart glasses — ensures the hardware is competitive on paper. Whether Buddy's real-world AI performance matches the promise will be the real test.

## The Diaspora Angle

For NRIs who already buy Lenskart glasses on trips home (the brand's online prescription service is popular with overseas Indians), the smart glasses represent something larger: evidence that India's consumer technology sector is graduating from software services into hardware products designed to compete at the global frontier. Bansal has said he plans to take the product to international markets after the India launch.

The early-access numbers — 35,000 sign-ups before a single unit has shipped — suggest the appetite is real. Whether Lenskart can deliver on the promise of AI-powered eyewear that is affordable, comfortable, and genuinely useful will determine whether this becomes India's first globally relevant consumer hardware brand in a generation.""",
    "word_count": 630
})

# ─────────────────────────────────────────────────────
# ARTICLE 4: markets-finance — Fuel Price Hike
# Topic: 27e00c79
# ─────────────────────────────────────────────────────
articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "27e00c79-7799-4b4d-975c-195e640700de",
    "headline": "Petrol Crosses ₹98 in Delhi as India Hikes Fuel Prices for the Second Time in Five Days",
    "subheadline": "The ₹3.90 combined rise since Friday ends a four-year price freeze — and analysts say more increases are coming as crude stays above $110 a barrel",
    "slug": f"petrol-diesel-price-hike-india-second-increase-five-days-{TODAY}",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "Rising fuel costs ripple through every aspect of the Indian economy that NRIs are connected to — from the cost of goods shipped to family, to Ola and Uber fares during visits home, to the household budgets of parents and relatives. For diaspora investors, OMC stock prices and inflation-linked bond yields are directly affected.",
    "tags": ["fuel prices", "petrol", "diesel", "India", "oil prices", "Iran conflict", "OMC", "inflation"],
    "urgency": "high",
    "sources": [
        "DriveSpark — 'Petrol, Diesel Prices Hiked Again By 90 Paise — Second Rise in Five Days' (May 19, 2026)",
        "LiveMint — 'Petrol, diesel prices hiked again! Fuel prices increased by 90 paise per litre'",
        "DevDiscourse — 'Petrol, diesel prices raised by 90 paise a litre, second hike under a week'",
        "Indian Oil Corporation — daily fuel price bulletin May 19, 2026"
    ],
    "score_total": 69,
    "status": "published",
    "published_at": NOW,
    "body": """India's state-run oil marketing companies — Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum — raised petrol and diesel prices by approximately 90 paise per litre on Tuesday, the second increase in five days. Combined with the ₹3-per-litre hike on 15 May that ended a near four-year price freeze, fuel costs have jumped ₹3.90 per litre since Friday. Petrol and diesel are now at their highest levels since May 2022.

## The Numbers

In Delhi, petrol now stands at ₹98.64 per litre and diesel at ₹91.58. Mumbai, burdened by higher state taxes, has crossed the psychological ₹107 mark for petrol at ₹107.59 per litre. Kolkata recorded the steepest increase among metros, with petrol climbing 96 paise to ₹109.70 per litre. Chennai and Bengaluru are not far behind, with petrol at ₹104.49 and ₹107.12 respectively.

CNG has not been spared. Rates rose ₹2 per kilogram on 15 May and another ₹1 per kilogram on Sunday, pushing prices in Delhi-NCR to ₹80.09 per kilogram — a blow to the auto-rickshaw and taxi fleets that millions depend on for daily transport.

## Why Now?

The trigger is geopolitical. US-Israeli strikes on Iran on 28 February and Tehran's subsequent retaliation disrupted oil flows through the Strait of Hormuz, one of the world's most critical energy chokepoints. India's crude import basket, which averaged $69 per barrel in February, surged to $113-114 in the weeks that followed.

India imports roughly 85 per cent of its crude oil. The state-owned retailers absorbed the price shock for nearly 11 weeks, racking up losses estimated at ₹750-1,000 crore per day. The 15 May revision was, by the government's own admission, "financially unavoidable." Tuesday's 90 paise addition offers further partial relief, but industry sources confirm significant under-recovery continues across all three OMCs.

## The Inflation Chain Reaction

Fuel prices in India function as a tax on everything. Trucking costs rise immediately, pushing up the price of food, consumer goods, and construction materials. The Reserve Bank of India's consumer price inflation reading for April, already elevated, is likely to worsen in May data. Economists at Goldman Sachs and Nomura have revised their India inflation forecasts upward, citing fuel as the primary driver.

The government has responded with a mix of demand suppression and symbolic measures: encouraging work-from-home arrangements and directing departments to limit official travel. But for the average Indian household — where fuel is a non-negotiable expense for everything from commuting to cooking — there is no meaningful offset.

## More Hikes on the Horizon

Analysts expect further revisions in the coming weeks. The gap between international crude prices and domestic retail rates remains substantial, and OMCs cannot sustain indefinite losses without threatening their balance sheets. Bharat Petroleum's Q4 results, released last week, showed resilient profits, but that was before the full impact of the price freeze hit. The market is watching HPCL and IOC earnings closely.

## What It Means for the Diaspora

For NRIs, the fuel price surge is felt through multiple channels. The cost of everything during visits to India — from Uber rides to restaurant bills — is climbing. Families back home face squeezed household budgets. Diaspora investors with exposure to Indian energy stocks face a complex picture: OMC shares rallied on the deregulation signal of the 15 May hike, but sustained high crude prices eat into margins regardless.

The bigger picture is macroeconomic. Rising fuel costs threaten India's growth trajectory at a moment when the economy was expected to accelerate past 7 per cent GDP growth. For the Viksit Bharat 2047 vision that the government has staked its credibility on, an oil shock is the last thing the playbook called for.""",
    "word_count": 670
})

# ─────────────────────────────────────────────────────
# INSERT ARTICLES
# ─────────────────────────────────────────────────────
for a in articles:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=a
    )
    if resp.status_code in (200, 201):
        print(f"✅ Published: {a['headline'][:70]}...")
    else:
        print(f"❌ Failed ({resp.status_code}): {a['headline'][:70]}... | {resp.text[:200]}")

# ─────────────────────────────────────────────────────
# MARK TOPICS AS PUBLISHED / REJECTED
# ─────────────────────────────────────────────────────

# Topics used in articles → published
used_topics = [
    "4b2b9d8c-e744-49df-8291-d5ae70561f07",
    "33f10289-864d-474a-8a7b-86d5f43376ae",
    "8de47dcb-f108-4c7e-8e80-221b7760b79f",
    "d6b91666-7693-448f-b80f-072a0a798918",
    "3bb98a51-b5e6-41fa-a981-0f2b7458967a",
    "0234d360-915f-4b46-ad71-79c5c92b0268",
    "2d1736fc-09cc-4b28-8056-3bec2c048b30",
    "4114eac0-2697-4cdf-b1f0-c966d83ceaa7",
    "27e00c79-7799-4b4d-975c-195e640700de",
]

for tid in used_topics:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "published", "updated_at": NOW}
    )
    if resp.status_code in (200, 204):
        print(f"  ✓ Topic {tid[:8]} → published")
    else:
        print(f"  ✗ Topic {tid[:8]} failed: {resp.status_code}")

# Reject low-value / already-covered / non-diaspora topics
reject_topics = [
    "2d8acda5-11dc-4734-a11e-af2a562375eb",  # Adani settlement — already published
    "245ab235-c2fa-5abb-b20a-5fb42f86cfbc",  # Meta layoffs — already published
]

for tid in reject_topics:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "rejected", "updated_at": NOW}
    )
    if resp.status_code in (200, 204):
        print(f"  ✓ Topic {tid[:8]} → rejected (duplicate)")
    else:
        print(f"  ✗ Topic {tid[:8]} failed: {resp.status_code}")

print("\nDone writing articles.")
