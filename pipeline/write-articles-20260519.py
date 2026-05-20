#!/usr/bin/env python3
"""Write and publish articles for the Videshi - 2026-05-19 news cycle."""
import json, os, uuid, datetime, requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

now = datetime.datetime.now(datetime.timezone.utc).isoformat()

articles = [
    {
        "id": str(uuid.uuid4()),
        "topic_id": "8af933ab-8997-4c2b-b879-91f81dee4fd5",
        "headline": "Sundar Pichai Just Declared 2026 the Year of the AI Agent — Here's What That Means for the Diaspora's Tech Army",
        "subheadline": "Google I/O 2026 unveiled Gemini 3.5 Flash, a personal AI agent called Spark, and Samsung-powered smart glasses — all steered by the Indian-born CEO reshaping how the world computes.",
        "body": """Sundar Pichai walked onto the Shoreline Amphitheatre stage in Mountain View on Monday and, without fanfare, announced the end of AI as a standalone chatbot feature. At Google I/O 2026, the company's annual developer conference, the Indian-born CEO laid out a vision in which artificial intelligence is no longer a product sitting inside an app — it is the operating system of everything Google makes.

The numbers alone are staggering. Google now processes more than 3.2 quadrillion tokens per month, a sevenfold increase from the same period last year. The Gemini app has crossed 900 million users globally. And the company disclosed $190 billion in capital expenditure commitments to build the infrastructure that powers it all.

## Gemini 3.5 Flash: Faster, Cheaper, Smarter

The centrepiece of the keynote was Gemini 3.5 Flash, a model Google claims is four times faster than comparable frontier AI systems and significantly cheaper to run. Pichai demonstrated that the model was able to generate an entire operating system in 12 hours — a feat designed to underscore its capacity for sustained, complex work. Gemini 3.5 Flash is available immediately in the Gemini app and across Google's developer platforms, with Gemini 3.5 Pro scheduled for release next month.

Alongside Flash, Google introduced Gemini Omni, a multimodal model that combines video, image, text, and audio inputs into a single prompt to generate video output. Users can describe a shot, specify camera angles, and feed in reference footage — Gemini Omni handles the rest. It is now live for Google AI Plus, Pro, and Ultra subscribers.

## Spark: Your Personal AI Agent

Perhaps the most consequential announcement was Gemini Spark, Google's new personal AI agent. Powered by Gemini 3.5, Spark can take action on a user's behalf, running long-duration tasks in the background on dedicated virtual machines in Google Cloud — no need to keep the device open. It will be integrated across Gmail, Google Docs, and Google Keep, with a summer rollout planned.

This is where the diaspora connection sharpens. For the estimated 500,000 Indian tech professionals in the United States alone — many of whom built their careers on mastering Google's ecosystem — the shift to agentic AI represents both an opportunity and a reckoning. Engineers who can build on Spark's architecture will find themselves in extraordinary demand. Those whose roles can be automated by it face a harder question.

## Smart Glasses and Universal Cart

Google also unveiled Android XR-powered smart glasses developed in partnership with Samsung, with designs from Gentle Monster and Warby Parker. Two categories of wearables were announced: audio-only glasses and models with integrated displays. The glasses support Gemini-powered features including live translation, navigation, and hands-free task execution — a direct challenge to Meta's Ray-Ban smart glasses.

On the commerce side, Google introduced Universal Cart, built on a new Universal Commerce Protocol. The feature lets users shop seamlessly while using Search, watching YouTube, reading Gmail, or chatting in the Gemini app, working across merchants and services. Agentic booking — where Google Search can autonomously find, price, and book venues — will roll out in the US this summer.

## What NRIs Should Watch

The subtext of I/O 2026 is that Google, under Pichai's leadership, is betting the company on AI agents that can act autonomously. For the Indian diaspora — which has an outsized presence in Silicon Valley, contributes significantly to Google's engineering workforce, and sends billions in remittances to a country building its own AI ambitions — this is personal.

India's own AI ecosystem stands to benefit. Google's Antigravity coding platform, now at version 2.0, gives Indian developers direct access to the same agentic tools powering the company's internal products. And with India already among the top markets for the Gemini app, the country is positioned as both a consumer and a builder in this new era.

When Pichai took a moment mid-keynote to reflect on the pace of change, he used a phrase that landed differently for the millions watching from Bengaluru, Hyderabad, and the Bay Area: "We're building for a billion more." For the diaspora's tech army, the message was unmistakable — the future is being shaped by one of their own, and the window to shape it alongside him is narrowing fast.""",
        "diaspora_angle": "Sundar Pichai, an Indian-born CEO, is steering Google's most consequential AI pivot. For 500,000+ Indian tech workers in the US and millions of developers in India, the shift to agentic AI reshapes career trajectories, startup opportunities, and India's AI ecosystem.",
        "vertical": "technology",
        "tags": ["Google I/O 2026", "Sundar Pichai", "Gemini AI", "AI agents", "smart glasses", "Indian tech workers"],
        "urgency": "breaking",
        "sources": [
            {"url": "https://www.gadgets360.com/ai/news/google-io-2026-everything-announced-gemini-3-5-flash-omni-spark-model-universal-cart-11519674", "name": "Gadgets 360"},
            {"url": "https://blog.google", "name": "Google Official Blog"},
            {"url": "https://www.gadgetbridge.com/tech-news/google-io-2026-gemini-goes-agentic/", "name": "GadgetBridge"},
            {"url": "https://www.livemint.com/technology/google-io-2026-highlights-gemini-3-5-flash-antigravity-2-0-ai-overhaul-google-search-11747679009063.html", "name": "Mint"}
        ],
        "slug": "sundar-pichai-google-io-2026-gemini-ai-agents-smart-glasses-20260519",
        "word_count": 720,
        "status": "published",
        "published_at": now,
        "category": "technology",
        "score_total": 92,
        "image_url": None,
        "image_attribution": None,
        "image_entities": ["Sundar Pichai", "Google I/O 2026", "Gemini AI", "smart glasses"],
        "image_must_show": "Sundar Pichai on stage at Google I/O 2026, or the Google I/O event stage with Gemini branding",
        "image_search_query": "Sundar Pichai Google I/O 2026 keynote stage"
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": "e8f333fe-c34f-49bd-b23e-ef0243134214",
        "headline": "A Storm Killed 111 People in Uttar Pradesh in Three Hours. For NRIs With Family There, the Phone Calls Haven't Stopped.",
        "subheadline": "Winds reaching 130 km/h tore through 26 districts on May 13, with Prayagraj bearing the worst of a disaster that drew condolences from Moscow to Abu Dhabi — and left thousands of diaspora families scrambling for news.",
        "body": """The storm arrived after dark on Tuesday, May 13, and by the time it passed three hours later, at least 111 people were dead across Uttar Pradesh — India's most populous state and the ancestral home of millions of NRIs scattered across the United States, the United Kingdom, Canada, and the Gulf.

Winds gusting up to 130 kilometres per hour swept through 26 districts between 8 PM and 11:30 PM IST, uprooting trees, snapping electricity poles, and flattening mud-brick homes that offered no resistance. The state's Relief Commissioner's Office confirmed 72 injuries, 179 livestock deaths, and damage to more than 227 houses. The true toll, officials have acknowledged, is likely higher.

## Prayagraj: The Epicentre

The Hindu pilgrimage city of Prayagraj was the worst hit, reporting at least 21 deaths — though local accounts suggest the number may be closer to 30. Seven people died in Handia, four in Phulpur, three in Soraon, and two in Meja. A widely circulated video from Bareilly showed a man being lifted into the air while trying to secure a tin roof; he survived, but the footage became a visceral symbol of the storm's fury.

Mirzapur recorded 19 deaths, Sant Ravidas Nagar 16, and Fatehpur 11. In Fatehpur, Additional District Magistrate Avinash Tripathi confirmed that eight of the nine dead — including five women — perished in the Khaga tehsil alone when walls collapsed on them. In Kanpur Dehat, a 19-year-old girl was struck by lightning while standing under a tree with her goats; many of the animals died alongside her.

## A Pattern That Climate Scientists Warned About

The storm was not a one-off. Scientists tracking India's weather patterns have linked such events to rising temperatures and increasingly erratic monsoon-adjacent weather systems. Wind speeds of 130 km/h during a pre-monsoon thunderstorm are consistent with what climate researchers have been warning about — that the March-to-June window is producing storms of escalating intensity. The 2018 dust storms in the same region killed over 120 people; eight years later, the infrastructure remains unprepared.

## The Government Response

Chief Minister Yogi Adityanath directed all Divisional Commissioners and District Magistrates to distribute financial assistance to affected families within 24 hours. The Relief Commissioner's Office said it was in continuous communication with district officials to ensure funds reached victims. Opposition leader Akhilesh Yadav called for immediate provision of food, shelter, and medical treatment.

The disaster drew attention from beyond India's borders. Russian President Vladimir Putin sent a message of condolence. The United Arab Emirates Ministry of Foreign Affairs issued a formal statement of solidarity. Singapore's High Commissioner Simon Wong expressed sympathy for the victims and their families.

## What the Diaspora Is Feeling

For the millions of Uttar Pradesh natives living abroad, the storm hit a nerve that transcends geography. UP is not just India's most populous state — it is the single largest source of Indian emigration. The Lucknow, Prayagraj, Varanasi, and Gorakhpur corridors feed diaspora communities from New Jersey to Leicester to Sharjah.

When a storm kills over a hundred people in three hours in districts where many NRIs still have parents, grandparents, and ancestral property, the impact is immediate and personal. Social media filled with frantic check-in posts. WhatsApp groups for UP-origin communities in the US and UK became informal relief coordination channels. Some diaspora organisations began raising funds for affected families, though no large-scale organised effort had emerged as of this writing.

The deeper concern is structural. Mud-brick construction, inadequate storm-warning systems, and the absence of storm shelters in rural UP mean that the next severe weather event — and climate scientists say there will be one — will produce similar casualties. For NRIs who send remittances to these same districts, the question is whether that money can be channelled toward resilience, or whether it will continue to arrive as post-disaster relief.

The storm of May 13 is over. The vulnerability that made it so deadly is not.""",
        "diaspora_angle": "Uttar Pradesh is the single largest source of Indian emigration. Millions of NRIs from UP live in the US, UK, Canada, and the Gulf, with family still in affected districts like Prayagraj, Mirzapur, and Fatehpur. The disaster triggered frantic check-ins and informal relief efforts across diaspora communities.",
        "vertical": "domestic",
        "tags": ["Uttar Pradesh storm", "Prayagraj", "natural disaster", "climate change", "NRI families", "relief efforts"],
        "urgency": "breaking",
        "sources": [
            {"url": "https://watchers.news/2026/05/14/severe-thunderstorms-leave-over-100-dead-across-uttar-pradesh-india/", "name": "The Watchers"},
            {"url": "https://www.southmatters.com/news/up-storm-tragedy-hailstorms-uttar-pradesh/", "name": "South Matters"},
            {"url": "https://www.reuters.com/sustainability/climate-energy/nearly-90-killed-storm-lashes-indias-most-populous-state-uttar-pradesh-2026-05-14/", "name": "Reuters"}
        ],
        "slug": "uttar-pradesh-storm-111-dead-prayagraj-nri-families-20260519",
        "word_count": 710,
        "status": "published",
        "published_at": now,
        "category": "news",
        "score_total": 88,
        "image_url": None,
        "image_attribution": None,
        "image_entities": ["Prayagraj storm damage", "Uttar Pradesh thunderstorm", "uprooted trees"],
        "image_must_show": "Storm damage in Prayagraj or Uttar Pradesh — uprooted trees, damaged structures, relief efforts",
        "image_search_query": "Uttar Pradesh storm damage Prayagraj May 2026"
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": "920cabfd-c273-4ec3-a56a-4a6d9831f70f",
        "headline": "An NRI Forgot Seven Bullets in a Bengaluru Hotel Room. Now He's in Judicial Custody and His Passport Is Gone.",
        "subheadline": "Arman Mutaahar, a 34-year-old US resident, left a loaded Ruger magazine at the Jayamahal Palace Hotel — and discovered the hard way that India's Arms Act does not care about American gun norms.",
        "body": """Arman Mutaahar checked into the Jayamahal Palace Hotel in Bengaluru on the night of April 27 and checked out the next morning. It was a routine overnight stay — until he called the hotel shortly after leaving to inform the staff that he had accidentally left behind a magazine loaded with seven live rounds of ammunition in his room.

The hotel staff inspected the room and found exactly what he described: a Ruger-brand magazine containing seven live bullets. They tried to get Mutaahar to collect it. He did not return. On May 6, the hotel manager filed a police complaint.

## The Arms Act Does Not Negotiate

That complaint set in motion a legal process that has upended the 34-year-old NRI's life. Police at the J.C. Nagar station registered a case under the Arms Act — India's strict federal law governing the possession of firearms, ammunition, and related materials. The law makes no distinction between a loaded weapon and a forgotten magazine. Possession of live ammunition without a valid Indian licence is a criminal offence, full stop.

Mutaahar was summoned to the police station on May 6 and, during questioning, admitted to illegally possessing the ammunition. Police seized the Ruger magazine along with his passport, mobile phone, laptop, and other documents. He was produced before a court on May 7, which granted 10 days of police custody for further investigation. On May 14, he was remanded to judicial custody, where he remains.

## The Cultural Chasm

The case reads like a cautionary parable about the gap between American and Indian gun laws — a gap that many NRIs either underestimate or simply do not think about until it is too late.

In most US states, possessing a loaded magazine is unremarkable. An estimated 81.4 million Americans own firearms, and ammunition can be purchased at grocery stores and petrol stations in much of the country. A magazine left behind in a hotel room would typically be treated as a lost-and-found item, not a criminal matter.

India operates in an entirely different legal universe. The Arms Act of 1959, along with its subsequent amendments, treats unauthorised possession of ammunition as a serious offence punishable by imprisonment ranging from one to seven years. There is no exception for foreign nationals, no grace period for accidental possession, and no provision that accounts for the norms of the traveller's home country.

This is not the first time an NRI has been caught in this legal thicket. In a separate but parallel case, the Karnataka High Court recently quashed charges against a US-based engineer who had been found carrying a single bullet — but only after he had already returned to the United States. Mutaahar has not been as fortunate; with his passport confiscated, he is stuck in India pending the outcome of his case.

## What Every NRI Traveller Should Know

The incident highlights a practical risk that diaspora communities rarely discuss: the items that are legal and unremarkable in your country of residence can land you in prison in India. This applies not just to ammunition but to a range of items — certain medications, satellite phones, high-capacity power banks on some airlines, and even some types of knives.

For the estimated 18 million members of the Indian diaspora, travel to India is often routine — visiting family, attending weddings, handling property matters. The familiarity of the journey can breed complacency about the legal environment. Mutaahar's case is a reminder that India's laws apply to everyone on Indian soil, regardless of where their passport was issued or what their home country's laws permit.

Legal experts advise NRIs to thoroughly check their luggage and personal items before travelling to India, to familiarise themselves with India's Arms Act and other regulations that differ sharply from Western norms, and to consult a local lawyer immediately if they find themselves on the wrong side of Indian law.

Mutaahar remains in judicial custody in Bengaluru. His case is ongoing.""",
        "diaspora_angle": "The case exposes a critical legal gap that many NRIs overlook: items legal in the US (firearms, ammunition) can result in serious criminal charges in India under the Arms Act. With 18 million diaspora members routinely travelling to India, this is a practical cautionary tale.",
        "vertical": "diaspora",
        "tags": ["NRI arrest", "Bengaluru", "Arms Act India", "gun laws", "travel warning", "US India legal differences"],
        "urgency": "developing",
        "sources": [
            {"url": "https://www.devdiscourse.com/article/law-order/3914081-bengaluru-nri-held-for-illegal-possession-of-seven-live-ammunition-rounds", "name": "DevDiscourse"},
            {"url": "https://www.livelaw.in/news-updates/karnataka-hc-lets-off-gun-enthusiast-us-engineer-charged-carrying-bullets", "name": "LiveLaw"}
        ],
        "slug": "nri-arrested-bengaluru-ammunition-hotel-arms-act-20260519",
        "word_count": 690,
        "status": "published",
        "published_at": now,
        "category": "nri-world",
        "score_total": 85,
        "image_url": None,
        "image_attribution": None,
        "image_entities": ["Jayamahal Palace Hotel Bengaluru", "Ruger ammunition", "Indian police"],
        "image_must_show": "Jayamahal Palace Hotel Bengaluru exterior, or a conceptual image of ammunition/legal proceedings",
        "image_search_query": "Jayamahal Palace Hotel Bengaluru"
    }
]

# Insert articles
for article in articles:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"✅ Published: {article['headline'][:80]}...")
        print(f"   ID: {data[0]['id'] if isinstance(data, list) else data['id']}")
        print(f"   Slug: {article['slug']}")
    else:
        print(f"❌ Failed: {article['headline'][:60]}... — {resp.status_code}: {resp.text}")

# Mark topics as published
topic_ids = [a["topic_id"] for a in articles]
for tid in topic_ids:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers=HEADERS,
        json={"status": "published", "updated_at": now}
    )
    if resp.status_code in (200, 204):
        print(f"✅ Topic {tid} marked published")
    else:
        print(f"❌ Topic update failed: {tid} — {resp.status_code}: {resp.text}")

print("\n✅ Article writing complete!")
