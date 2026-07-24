#!/usr/bin/env python3
"""Videshi Writer — News/NRI-World/Technology/Markets-Finance batch for 2026-05-19."""

import json, os, sys, uuid, requests
from datetime import datetime, timezone

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def sb_patch(table, filter_str, data):
    h = dict(HEADERS)
    h["Prefer"] = "return=minimal"
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filter_str}", headers=h, json=data)
    r.raise_for_status()

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── ARTICLE 1: Marco Rubio India Visit / Quad Talks ──────────────
article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Marco Rubio Heads to India This Week. For the Diaspora, the Quad Meeting in Delhi Could Reshape What Comes Next.",
    "subheadline": "The US Secretary of State will visit Kolkata, Agra, Jaipur and New Delhi from May 23-26, capping the trip with a Quad foreign ministers' meeting as West Asia tensions and trade negotiations demand attention.",
    "slug": "rubio-india-visit-quad-talks-20260519",
    "category": "news",
    "vertical": "politics",
    "urgency": "high",
    "score_total": 92,
    "status": "published",
    "published_at": now,
    "tags": ["Marco Rubio", "Quad", "US-India relations", "Jaishankar", "diplomacy", "Indo-Pacific"],
    "diaspora_angle": "Rubio's four-day India trip and the Quad foreign ministers' meeting in New Delhi directly impact diaspora interests — from visa policy signals to trade terms that affect NRI remittances and business ties.",
    "sources": json.dumps([
        {"name": "Devdiscourse/PTI", "url": "https://www.devdiscourse.com/article/politics/3914485-us-secretary-of-state-marco-rubio-to-visit-india-from-may-23-26"},
        {"name": "Media House Press", "url": "https://mediahousepress.co.in"},
        {"name": "Currato", "url": "https://currato.com"}
    ]),
    "image_search_query": "Marco Rubio India visit Quad foreign ministers meeting",
    "image_must_show": "Marco Rubio, S Jaishankar, Quad flags",
    "body": """Marco Rubio is coming to India. And for the first time in Donald Trump's second term, his top diplomat is making the kind of multi-city, multi-day visit to India that signals something larger than a courtesy call.

The US State Department confirmed on Monday that Secretary of State Rubio will travel to India from May 23-26, stopping in Kolkata, Agra, Jaipur and New Delhi. The trip follows his attendance at the NATO Foreign Ministers meeting in Sweden on May 22 — meaning India is, quite literally, where Rubio goes after conferring with America's closest military allies.

## The Quad Convenes in Delhi

The headline event lands on May 26: a Quad foreign ministers' meeting in New Delhi, bringing together Rubio, Australian Foreign Minister Penny Wong, Japanese Foreign Minister Motegi Toshimitsu and Indian External Affairs Minister S. Jaishankar.

The Quad — shorthand for the Quadrilateral Security Dialogue between the US, India, Japan and Australia — has evolved from a loose strategic forum into something with real teeth. Last year's Quad summit in Wilmington produced concrete deliverables: a Critical and Emerging Technology Initiative, joint maritime patrols in the Indo-Pacific and an ambitious semiconductor supply-chain partnership that directly involves Indian facilities.

The New Delhi session is expected to address what none of the four governments can avoid: the fallout from the West Asia crisis. With the Iran-Israel standoff still simmering and oil markets jittery — Brent briefly touched $87 last week — the Quad partners need to coordinate on energy security, shipping lane protection and the economic ripple effects hitting all four nations.

## Why This Matters to NRIs

For the Indian diaspora, the subtext of this visit runs deeper than communiqués.

**Visa and immigration signals.** Rubio has been the public face of the Trump administration's tighter visa-vetting regime. His earlier remarks defending H-1B reforms and stricter student visa screening made headlines across Indian-American communities. Any softening — or hardening — of tone during this trip will be parsed carefully by the roughly 4.4 million Indian Americans whose professional networks depend on fluid cross-border mobility.

**Trade terms that hit home.** The US recently imposed tariffs on Indian goods while simultaneously pressuring New Delhi over Russian oil imports. For NRIs who run import-export businesses, invest in Indian markets or send remittances that get squeezed by currency fluctuations (the rupee hit a record low of 96.70 against the dollar this week), the trade framework that emerges from these conversations has direct financial consequences.

**Defence cooperation and the jobs it creates.** The $428 million Apache helicopter and M777 howitzer support deals approved earlier this month point to a deepening defence-industrial relationship. Indian-American engineers and defence contractors are increasingly embedded in this supply chain. The Quad's tech and defence agenda isn't abstract geopolitics — it's career infrastructure for a growing segment of the diaspora.

## The Multi-City Choreography

Rubio's itinerary is notable for what it includes beyond Delhi. Kolkata — rarely on the diplomatic circuit — suggests engagement with eastern India's economic corridors and possibly the Bay of Bengal security framework. Agra and Jaipur signal the cultural diplomacy that the State Department uses to underline the "people-to-people" dimension of the relationship, a theme that resonates directly with diaspora identity.

State Department spokesman Tommy Pigott kept the official readout terse: energy, security, trade and defence cooperation would anchor the discussions. But diplomatic sources suggest the conversations will also touch on AI governance, critical minerals sourcing from India and the Quad's fellowship programmes that send hundreds of Indian students to American universities annually.

## What's Next

The Quad meeting comes just weeks before India is expected to host a full Quad Leaders' Summit later this year — potentially in August or September, with Prime Minister Modi aiming to use it as a centrepiece of India's diplomatic calendar.

For NRIs watching from Houston, London or Sydney, the stakes are concrete. The visa regime, the trade balance, the defence contracts and the technology partnerships being discussed in New Delhi this week will shape the corridors through which the diaspora moves, works and invests for the next several years.

Rubio's four-day trip may be billed as routine diplomacy. For the Indian diaspora, nothing about it is routine.""",
    "word_count": 680,
}

# ── ARTICLE 2: Google I/O 2026 ───────────────────────────────────
article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Google I/O 2026: Sundar Pichai Unveiled an AI Empire Processing 3.2 Quadrillion Tokens a Month. Here's What It Means for India.",
    "subheadline": "From Gemini 3.5 Flash and a 24/7 personal AI agent called Spark to $180 billion in infrastructure spending, here are the announcements NRIs in tech should actually care about.",
    "slug": "google-io-2026-sundar-pichai-gemini-india-20260519",
    "category": "technology",
    "vertical": "technology",
    "urgency": "high",
    "score_total": 91,
    "status": "published",
    "published_at": now,
    "tags": ["Google I/O", "Sundar Pichai", "Gemini", "AI", "Android", "TPU", "Antigravity"],
    "diaspora_angle": "Sundar Pichai — born in Madurai, raised in Chennai — is leading the world's most consequential AI company. The I/O announcements directly affect Indian developers, the 8.5 million building on Google's models, and the diaspora tech workforce.",
    "sources": json.dumps([
        {"name": "Google Blog", "url": "https://blog.google/innovation-and-ai/sundar-pichai-io-2026/"},
        {"name": "Mint", "url": "https://livemint.com"},
        {"name": "Shacknews", "url": "https://shacknews.com"}
    ]),
    "image_search_query": "Sundar Pichai Google I/O 2026 keynote stage",
    "image_must_show": "Sundar Pichai on stage, Google I/O branding",
    "body": """Sundar Pichai walked onto the stage at Shoreline Amphitheatre in Mountain View on Monday and did what he has done every May for a decade — except this time, the numbers he quoted sounded like they belonged to a different species of company.

3.2 quadrillion tokens processed per month. Up from 480 trillion a year ago. Up from 9.7 trillion two years ago. That is a 330x increase in two years — a rate of growth that makes Moore's Law look quaint.

Google I/O 2026 was not a product launch event. It was a declaration that the company Pichai runs — the one he joined as a product manager in 2004, the one built by two Stanford PhD students in a Menlo Park garage — now operates the largest AI infrastructure on the planet.

## The Numbers That Matter

Start with Gemini 3.5 Flash, the model Google released to everyone on Monday. It is, by Google's benchmarks, better than the previous Gemini 3.1 Pro across nearly every measure — and it runs four times faster than comparable frontier models from OpenAI or Anthropic. At less than half the price.

Pichai made the cost argument explicit: companies processing a trillion tokens a day could save over $1 billion annually by shifting 80% of their workloads to Flash. That is a direct shot at OpenAI's pricing, and it is aimed squarely at the enterprises — many of them in India's IT corridor — that are currently blowing through their annual AI budgets by May.

Then came the infrastructure reveal. Google will spend approximately $180 to $190 billion in capital expenditure this year. That is six times its 2022 capex. Most of it goes into data centres, TPU fabs and the networking backbone required to keep 3.2 quadrillion tokens moving every month.

The new TPU 8t chip — optimised for training — delivers three times the raw computing power of its predecessor and can distribute training across more than one million TPUs globally. Its inference counterpart, TPU 8i, is built for speed: Pichai emphasised that "27 years of working on Search taught us that latency matters."

## Gemini Spark: Your 24/7 AI Agent

The consumer headline was Gemini Spark, a personal AI agent that lives in the Gemini app, runs on dedicated virtual machines in Google Cloud and operates around the clock — no laptop required. It handles long-horizon tasks in the background, integrates with third-party tools through MCP (Model Context Protocol), and will soon work directly inside Chrome as an agentic browser.

Think of it as Google's answer to the agentic AI wave: instead of you going to the AI with a prompt, the AI goes out into the world on your behalf, checking your email, tracking prices, managing research tasks and reporting back. Beta access for Google AI Ultra subscribers starts next week in the US.

For Indian developers — and there are hundreds of thousands of them building on Google's stack — the Antigravity 2.0 platform may be even more consequential. It is evolving from a coding environment into an agent management platform where anyone can orchestrate autonomous AI agents, powered by a version of Flash that runs 12 times faster than competing frontier models.

## What This Means for Indian Tech

The diaspora angle here is not subtle. Pichai is the most powerful Indian-born executive in technology. The infrastructure he is building employs tens of thousands of Indian engineers directly and creates the platform on which millions more build their livelihoods.

Over 8.5 million developers worldwide now build applications on Google's models monthly. A significant share of them are in India, where Google's AI products have deeper penetration than in almost any other market. AI Overviews in Search alone has 2.5 billion monthly active users globally; India is its largest market outside the US.

The broader signal for NRIs in tech is this: the AI race has entered its infrastructure phase. It is no longer about who has the cleverest model — it is about who can deploy at planetary scale while keeping costs low enough for the rest of the world to build on top.

Google, under a Madurai-born CEO, is making the case that it is that company. Whether you work at a Bengaluru startup training models on Google Cloud, or you are a product manager at a Bay Area company evaluating which AI vendor to commit to, Monday's announcements change the calculus.

The Gemini era is not coming. According to the numbers Pichai shared on Monday, it is already here — processing 3.2 quadrillion reasons per month to believe him.""",
    "word_count": 730,
}

# ── ARTICLE 3: Adani $275M Settlement ────────────────────────────
article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Adani Enterprises Just Paid $275 Million to the US Treasury to Make Its Iran Problem Disappear. Here's What NRIs Need to Know.",
    "subheadline": "The settlement over 32 alleged Iran sanctions violations is one of the largest ever involving an Indian company — and it closes one chapter while opening questions about what comes next for Gautam Adani's global ambitions.",
    "slug": "adani-275-million-settlement-us-treasury-iran-20260519",
    "category": "markets-finance",
    "vertical": "business",
    "urgency": "high",
    "score_total": 90,
    "status": "published",
    "published_at": now,
    "tags": ["Adani", "Gautam Adani", "OFAC", "Iran sanctions", "US Treasury", "settlement", "Indian conglomerates"],
    "diaspora_angle": "NRI investors hold significant positions in Adani stocks; the settlement clears a major regulatory overhang but raises governance questions that diaspora investors, particularly those subject to US compliance regimes, need to track.",
    "sources": json.dumps([
        {"name": "Mint", "url": "https://livemint.com"},
        {"name": "The S Bharat", "url": "https://thesbharat.com/adani-enterprises-reaches-275-million-settlement-with-us-over-alleged-iran-sanctions-violations/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/"},
        {"name": "Reuters", "url": "https://sahmcapital.com"}
    ]),
    "image_search_query": "Adani Group headquarters Gautam Adani",
    "image_must_show": "Adani Group, Gautam Adani, corporate",
    "body": """Adani Enterprises has agreed to pay $275 million — roughly ₹2,647 crore — to the US Treasury Department, settling allegations that the company violated American sanctions on Iran through 32 transactions involving liquefied petroleum gas shipped through intermediaries.

The settlement, confirmed this week, is among the largest sanctions-related agreements ever reached between an Indian corporate entity and the US government's Office of Foreign Assets Control (OFAC). Adani neither admitted nor denied wrongdoing.

For NRI investors who hold Adani stocks — and there are many, given the group's prominence in Indian portfolios — the deal is simultaneously a relief and a warning.

## What the US Government Alleged

According to OFAC, Adani Enterprises engaged in 32 LPG transactions over several years in which the cargoes originated from Iran but were routed through a Dubai-based trading firm in a way that obscured their source. The United States maintains comprehensive sanctions against Iran's oil, gas and petrochemical sectors, and companies anywhere in the world can face penalties if they participate in transactions involving sanctioned Iranian products — particularly when those transactions touch the US financial system or use dollar-denominated payments.

The alleged transactions involved complex international supply-chain arrangements. US investigators claimed the shipments were "structured in a way that obscured the actual source of the fuel," with documentation that did not explicitly identify Iranian origin.

Adani had previously dismissed the allegations as "baseless" when reports of the investigation surfaced in 2025.

## The Broader Legal Clean-Up

The $275 million OFAC settlement does not stand alone. It is part of a larger legal resolution that has unfolded over recent weeks:

**The SEC settlement.** Adani also reached a civil settlement with the Securities and Exchange Commission over bribery allegations — Gautam Adani personally paid $6 million in penalties, while his nephew Sagar Adani paid $12 million. The SEC case had alleged a $250 million bribery scheme connected to Indian solar energy contracts between 2020 and 2024.

**Criminal charges dropped.** Perhaps most significantly for markets, the US Department of Justice has moved to dismiss the criminal wire fraud charges that had been filed against Gautam and Sagar Adani. This removes the most severe legal threat — the prospect of a criminal conviction against the chairman of one of India's largest conglomerates.

Together, the three resolutions effectively close the American legal chapter that has hung over the Adani Group since late 2024, when the original indictment sent shockwaves through Indian stock markets and triggered a sharp sell-off in Adani shares.

## What It Means for NRI Investors

For the diaspora investment community, the implications cut both ways.

**The bullish read.** The settlement removes a massive regulatory overhang. Adani Enterprises' core operations — ports, airports, logistics, renewable energy, mining — remain intact. Analysts have noted that the company can absorb a $275 million payout without significant disruption to its balance sheet. Gautam Adani's net worth still sits around $82 billion. The stock is likely to respond positively to the removal of criminal liability.

**The cautious read.** NRIs who invest through US-based brokerage accounts or hold dual tax obligations need to understand the compliance signal. OFAC settlements are not footnotes — they go into a company's permanent compliance record. Institutional investors, particularly those with ESG mandates or US fiduciary obligations, may continue to treat Adani stocks with heightened due diligence requirements.

The case also underscores a broader reality: Indian conglomerates operating globally are increasingly subject to the extraterritorial reach of American sanctions law. If your supply chain touches sanctioned nations and your payments touch the US dollar system, OFAC can — and will — come knocking.

## The Bigger Picture

The Adani settlement arrives at a moment when India-US commercial ties are being reshaped by competing pressures. The Trump administration has imposed tariffs on Indian goods while simultaneously deepening defence cooperation. India continues to buy Russian crude oil despite US objections. The Adani case sits in this messy middle ground — a reminder that American regulatory power can reach deep into Indian boardrooms, even as the two governments publicly celebrate a strategic partnership.

For NRIs managing portfolios that include Indian conglomerates, the lesson is straightforward: the era of Indian companies operating in global markets without facing global regulatory scrutiny is over. The $275 million cheque Adani just wrote to the US Treasury is the price of admission to that new reality.""",
    "word_count": 720,
}

# ── INSERT ARTICLES ───────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    print(f"\nInserting: {art['headline'][:80]}...")
    result = sb_post("p2_articles", art)
    if isinstance(result, list) and len(result) > 0:
        print(f"  ✓ ID: {result[0]['id']}, slug: {result[0]['slug']}")
    else:
        print(f"  Result: {result}")

# ── MARK TOPICS AS PUBLISHED ─────────────────────────────────────
topic_ids = [
    "f65e9f28-5878-4d94-aca8-868dcccf6e6c",  # Marco Rubio
    "c9376372-00d1-4b51-98ae-d1272c487638",  # Google I/O
    "2d8acda5-11dc-4734-a11e-af2a562375eb",  # Adani settlement
]

for tid in topic_ids:
    sb_patch("p2_topics", f"id=eq.{tid}", {"status": "published", "updated_at": now})
    print(f"✓ Marked topic {tid[:12]}... as published")

# ── REJECT LOW-VALUE TOPICS ──────────────────────────────────────
# Reject topics that are too local, not diaspora-relevant, or already covered
reject_ids = [
    "1f9e3bc5-fee6-4010-a1f6-c0ae82106bae",  # Delhi CEO electoral roll - too local
    "3a5029e2-633f-44ee-b8e6-cee59a5ddded",  # Nepal Romeo-Juliet clause - Nepal, not India
    "8431685e-067c-4411-b888-514253cce80d",  # NYC manhole death - not India/diaspora
    "877ef075-4ade-49ef-9112-ec32e5b0b811",  # Maharashtra bike-taxi policy - too local
    "9dab2433-0dbd-416e-95f2-6872232e77b5",  # Punjab underground wiring - too local
    "93b16300-c8d5-473e-8e69-48f9bb107241",  # Mango founder Spain - not India/diaspora
    "75b1e6e1-1cbc-4c21-9346-787ecc425022",  # UK headteacher banned - not India/diaspora
    "4551942d-781f-43d8-baf9-ddbf61455b4e",  # How to dispute e-challans - too local/explainer
    "4bc594f6-c451-4b4d-88b3-43afdd837fad",  # TN SSLC results - too local
    "ec8aadf3-44ee-446d-890e-3a96ead27ca3",  # Kejriwal wedding gossip - celebrity gossip
    "39cdbe22-f19e-49ff-b938-a533206e1bb1",  # Doctor survives ECMO - individual medical story
    "cc61a723-4734-4d11-bb6e-dc7f8ce6f90b",  # WHO Ebola - not India-focused
    "1ec940be-3d4c-40c7-ac78-834ef352a983",  # Radioactive stardust - science, not India
    "be4729d5-8978-4670-92fc-d440892480c1",  # Preeclampsia treatment - medical, not India
    "168ed6ce-2640-4a40-8e01-105d38d7d5a7",  # SoCal wildfire - not India/diaspora
    "a7d6f8b6-9575-4112-85e5-5ba435d58b7c",  # Telangana couple murders - too local crime
    "993c7b18-bb79-4401-90e3-6e507c180d4c",  # Twisha Sharma dowry - local crime
    "dd588e2c-d4f2-47a9-972c-58fb8abfff02",  # NCSC Punjab Census terms - too niche
    "8c9f56aa-ab2c-4fa1-99bf-4cd4e7647838",  # London Tube strike - not India
    "3c4d157a-af67-42d0-86d7-b9afff43ae30",  # Skoda Epiq eSUV - not India-focused enough
    "c10104fe-b6df-4702-b8c4-89284ac7c529",  # Motorola phone launch - too product-specific
    "d96dd847-2a99-4007-af88-d2441e2bcdc1",  # RBI govt securities auction - too technical
    "917f4261-21f0-42fa-8e3c-f7827aa7792c",  # RBI VRR auction - too technical
    "914a708c-a54b-4548-b1e0-75fc47d9bb45",  # RBI cancels bank license - too niche
    "2e1d20c3-1a3f-40bc-8bbb-275c404a302a",  # UK petrol prices - not India
    "f3232158-0f7b-43ef-aaaf-05bb8c57732d",  # Bank of England stablecoin - not India
    "0bd8a6be-afb2-420b-9cfa-6b188be5535a",  # UK pension crisis - not India
]

for tid in reject_ids:
    sb_patch("p2_topics", f"id=eq.{tid}", {"status": "rejected", "updated_at": now})

print(f"\n✓ Rejected {len(reject_ids)} low-value topics")

# ── STORE ARTICLE IDS FOR IMAGE SOURCING ──────────────────────────
print(f"\n=== Article IDs for image sourcing ===")
for art in articles:
    print(f"{art['id']} | {art['category']} | {art['slug']}")

print("\nDone!")
