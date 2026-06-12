#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-12 18:00 UTC batch"""

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

# ──────────────────────────────────────────────
# ARTICLE 1: Google Gemini 3.5 Live Translate
# ──────────────────────────────────────────────

article1_body = """Google has spent two decades trying to crack machine translation. On Monday, Sundar Pichai's team shipped the closest thing yet to a universal interpreter — and for the roughly five million Indian Americans who toggle between English and a mother tongue every single day, this one lands differently.

Gemini 3.5 Live Translate is a streaming speech-to-speech model that handles over 70 languages in continuous real-time. Unlike older systems that wait for a speaker to finish a sentence, parse it, and spit out a translation after a pause that kills any conversational rhythm, the new model generates translated audio just a few seconds behind the speaker. It preserves intonation, pacing, and pitch — meaning your grandmother in Chennai hears something that sounds vaguely like you, not a robot reading a transcript.

The rollout spans three surfaces. The Google Translate app on Android and iOS gets a new listening mode. The Gemini Live API enters public preview for developers. And Google Meet — the default video platform for thousands of Indian IT companies and their diaspora clients — jumps from five supported translation languages to over 70, with more than 2,000 language pairs available in a single meeting.

## Why the diaspora should pay attention

For NRI families, this is not an incremental upgrade. It is a category shift. Hindi, Tamil, Telugu, Bengali, Kannada, Malayalam, Marathi, Gujarati, and Punjabi are all among the supported languages. The practical implications are immediate: a product manager in San Jose running a Google Meet with a vendor in Hyderabad no longer needs both parties to struggle through English. A second-generation Indian American whose spoken Tamil is rusty can have a real-time translated phone call with an aunt in Madurai without the stilted back-and-forth of typing into Google Translate.

Southeast Asian ride-hailing giant Grab is already using the API to let drivers and passengers communicate across languages during pickups. LiveKit, Pipecat, and Vision Agents are building voice translation products on the same foundation. The platform play is obvious: Google is trying to make Gemini the default translation layer for every conversation that crosses a language boundary, whether it happens over Meet, in a call centre, or at a hospital reception desk.

## The competitive angle

The timing is deliberate. Apple just unveiled a rebuilt Siri at WWDC 2026, powered — ironically — by Google's own Gemini models. Microsoft has been weaving Copilot into Teams with its own real-time translation features. OpenAI's voice mode handles a handful of languages. None of them match the breadth or the streaming fluidity that Google is claiming here.

For Indian-origin professionals working across borders — and there are a lot of them — the question is which platform becomes the invisible translation layer in their daily workflow. Google is betting that owning the model, the app, and the enterprise video stack gives it an unbeatable advantage.

There is a catch, as always. Google says the model handles noisy, real-world environments, but anyone who has used voice translation in a crowded Indian wedding hall knows that "handles" is doing a lot of work. Speaker intonation preservation sounds impressive in a demo; whether it survives rapid code-switching between Hindi and English — the default communication mode of every NRI household — remains to be seen.

Still, the direction is unmistakable. The language barrier that has defined immigrant life for generations — the one that makes doctor visits stressful, parent-teacher conferences awkward, and family calls shorter than they should be — just got thinner. Sundar Pichai, a Tamil-speaking immigrant himself, would know exactly how much that matters."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sundar Pichai's Google Just Shipped a Real-Time Interpreter for 70 Languages — and Hindi Is on the List",
    "subheadline": "Gemini 3.5 Live Translate turns phone calls, Google Meet sessions, and everyday conversations into seamless multilingual exchanges. For NRI families, it could change everything.",
    "slug": make_slug("google-gemini-live-translate-hindi-nri-families"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Hindi, Tamil, Telugu, Bengali, and other Indian languages are among the 70+ supported — NRI families can now have real-time voice-translated calls with relatives in India without awkward pauses or robotic output.",
    "tags": ["google", "sundar-pichai", "gemini", "ai-translation", "nri-families", "google-meet"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Google Blog", "url": "https://blog.google/products/translate/gemini-3-5-live-translate/"},
        {"name": "Gadgets360", "url": "https://www.gadgets360.com/ai/news/google-gemini-3-5-live-translate-multilingual-conversations-8200156"},
        {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/google-gemini-3-5-live-translate-real-time-speech-translation-phone-calls-online-meetings-11749549186614.html"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/gemini-3-5-live-translate-debuts-with-natural-sounding-voice-translation"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, at a 2023 event",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 2: Meta x Reliance 168MW Data Center
# ──────────────────────────────────────────────

article2_body = """When Meta invested $5.7 billion in Jio Platforms in 2020, the sceptics called it a bet on WhatsApp payments. When the two companies formed a $100 million AI joint venture last year, it looked like a software play. Now the relationship has gone physical, and the scale is hard to ignore.

Meta Platforms will lease a 168-megawatt AI-enabled data centre in Jamnagar, Gujarat, built and operated by Mukesh Ambani's Reliance Industries. It is Meta's first custom-built data centre on Indian soil. Construction has already started, with delivery expected within two years. The facility will run on renewable energy and use desalinated seawater for cooling — a critical detail in a country where water stress has derailed data centre projects in Pune, Chennai, and Noida.

The numbers tell a clear story. At 168 megawatts, the Jamnagar facility is roughly a tenth of India's entire operational data centre capacity. Reliance has committed $110 billion over seven years to AI infrastructure. Adani has pledged another $100 billion. The Indian government is offering foreign companies a 20-year tax break on local data centre usage. India's data centre market, currently valued at around $7 billion, is projected to nearly double to $13.1 billion by 2034.

## What NRI investors should watch

For the Indian American investor class — the ones tracking Reliance on the BSE, waiting for the Jio IPO, and wondering whether India's AI story is real — this deal is a signal worth reading carefully.

First, Reliance is positioning itself as a single-window provider for hyperscale AI infrastructure: design, construction, renewable power, connectivity, and operations, all under one roof. That is the Ambani playbook — vertical integration that locks in the customer and locks out competitors. Meta gets a turnkey facility; Reliance gets a marquee anchor tenant that validates the entire Jamnagar AI corridor.

Second, the renewable energy component is substantial. Meta is separately contracting nearly one gigawatt of new renewable capacity in India through deals with CleanMax (837 MW of solar and wind) and Fourth Partner Energy (88 MW). The company says it will cover the full cost of energy and water for the Jamnagar site. For a country where data centre power demands are growing faster than the grid can serve them, that kind of self-sufficiency is not altruism — it is a prerequisite.

Third, the location is strategic. Jamnagar is home to Reliance's flagship refinery complex, the world's largest single-site oil refinery. The industrial infrastructure — power, water, roads, port access — is already there. Converting parts of a fossil fuel campus into an AI compute hub is exactly the kind of energy transition narrative that plays well with ESG-conscious institutional investors, many of whom sit in New York and London.

## The bigger picture

India is now receiving the same hyperscale data centre treatment that Southeast Asia got five years ago and the Middle East got three years ago. Amazon, Microsoft, and Google have all expanded their India cloud regions. But Meta's move is different. This is not a cloud region for retail customers. It is a built-to-suit facility that will likely host Meta's Llama AI models and serve as infrastructure for the company's 300-million-plus Indian user base on Facebook and its even larger WhatsApp footprint.

For Indian-origin professionals in Silicon Valley who have watched their companies build data centres everywhere except India, this is a turning point. The compute is finally going home. Whether Reliance can deliver on time, on budget, and at the quality Meta demands is the open question — but Ambani has a track record of building large things fast, and Meta has nowhere else to go for this kind of capacity in India.

The refinery town that powered India's fossil fuel era is being repurposed for the AI era. The symbolism is almost too neat."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Picks Ambani's Jamnagar for Its First India AI Data Centre — and the Scale Is Hard to Ignore",
    "subheadline": "A 168-megawatt facility, renewable energy deals worth nearly a gigawatt, and a $110 billion infrastructure bet. The Meta-Reliance partnership just went from software to steel.",
    "slug": make_slug("meta-reliance-jamnagar-data-centre-ai-india"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors tracking Reliance and the Jio IPO should note Meta's anchor tenancy as a validation signal for India's hyperscale AI infrastructure play — the compute is finally going home.",
    "tags": ["meta", "reliance", "mukesh-ambani", "data-center", "india-ai", "jamnagar", "renewable-energy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-deepens-partnership-with-ambanis-reliance-with-ai-data-centre-2026-06-10/"},
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/meta-reliance-india-ai-data-center/"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/meta-leases-first-india-ai-data-center-from-reliance/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/meta-and-reliance-industries-partner-to-develop-168-mw-ai-enabled-data-centre-in-gujarat/article69671234.ece"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mukesh_Ambani.jpg",
    "image_caption": "Mukesh Ambani, chairman of Reliance Industries",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 3: Apple WWDC 2026 / iOS 27 Siri AI
# ──────────────────────────────────────────────

article3_body = """Apple just rebuilt Siri from the ground up. It runs on Google's Gemini models. It understands context, reads your screen, chains multi-step commands, and works across every Apple device. And if you are in India or China, you cannot use it.

At WWDC 2026 on Sunday, Apple unveiled iOS 27, macOS Golden Gate, and a radically redesigned Siri AI that represents the company's most aggressive push into artificial intelligence. The new Siri is not a chatbot bolted onto a phone — it is a system-level assistant that can search your photos, draft emails, summarise documents, identify objects through your camera, and coordinate actions across apps. Apple mentioned Siri over 100 times during the 90-minute keynote. The message was clear: this is Apple's answer to Google's Gemini, OpenAI's GPT, and Microsoft's Copilot.

But Siri AI launches in English first, and Apple has confirmed it will not be available in India or China at launch while it "works through regulatory requirements." The EU gets a partial block too — no Siri AI on iPhone or iPad, though Mac, Watch, and Vision Pro are fine. The company supports 16 languages for Apple Intelligence overall, but the flagship AI features that dominated the keynote are geofenced.

## What India gets — and what it does not

India does get some useful additions. iOS 27 introduces Hindi and Marathi Scribble support for Apple Pencil, allowing handwritten input in those scripts. Natural language time formats now work in Hindi. Alternate calendars for India support the current time zone while travelling. These are quality-of-life improvements for the roughly 250 million iPhone users in India.

What India does not get is the headline feature. No Siri AI. No on-screen awareness. No multi-step commands. No intelligent tab management in Safari. No AI-powered Smart Reply in Messages. The gap between an iPhone 17 in San Francisco and an iPhone 17 in Mumbai just became a feature canyon.

For the Indian diaspora, this creates an odd situation. NRI parents buying iPhones for relatives in India — a common practice — will be buying a device that runs a meaningfully different operating system. The phone is the same hardware, the price is nearly the same, but the software experience is tiered by geography. Apple has effectively created a two-class iPhone, and India is in the second class.

## The Gemini irony

The most striking detail from WWDC is one that Apple would rather you not dwell on: Siri AI is powered by Google's Gemini models. Apple, the company that built its identity on vertical integration and controlling every layer of the stack, is running its flagship AI feature on a competitor's technology. The move speaks to how far behind Apple fell in the AI race. It could not build a competitive large language model in-house fast enough, so it licensed one from the company whose search engine it has spent two decades trying to replace.

For Indian-origin engineers at both companies — and there are thousands — the arrangement is a fascinating workplace dynamic. Google's AI team, led by Sundar Pichai, is effectively powering Apple's most important new product feature. Demis Hassabis's DeepMind built the models. Apple's engineers in Cupertino (and Hyderabad, where Apple has a major development centre) are integrating them into iOS. The two companies remain fierce competitors in hardware, services, and search, even as one runs on the other's AI.

## The regulatory question

Apple says India's exclusion is about regulatory compliance, not technical limitation. India does not yet have a comprehensive AI governance framework — the government has said it is drafting one — but it does have data localisation requirements and content moderation rules that complicate AI deployment. China's situation is more explicitly regulatory, with strict rules on generative AI that require government approval before launch.

The practical question for Indian consumers and the diaspora is when, not whether, Siri AI arrives in India. Apple has historically been slow to roll out new features in the country — Apple Pay took years — but the competitive pressure from Google's Gemini features on Android, which are already available in India in multiple languages, may force a faster timeline.

For now, the world's most valuable company just told a billion people that its best new feature is not for them. That is a strange way to grow in your fastest-expanding market."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Rebuilds Siri on Google's AI — but India Will Not Get It Anytime Soon",
    "subheadline": "iOS 27's flagship feature is geofenced out of India and China at launch. For NRI families, it means the same iPhone now runs a meaningfully different operating system depending on where you live.",
    "slug": make_slug("apple-siri-ai-ios-27-india-geofenced-gemini"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRIs buying iPhones for family in India will discover the device runs a two-tier operating system — Siri AI, the headline WWDC feature, is geofenced out of India at launch.",
    "tags": ["apple", "siri-ai", "ios-27", "wwdc-2026", "india", "gemini", "google", "geofencing"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/11/250-changes-ios-27-macos-golden-gate/"},
        {"name": "Gadget Bridge", "url": "https://www.gadgetbridge.com/trending/apple-wwdc-2026-ios-27-siri-ai/"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/06/apple-wwdc-2026/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/tech/12-biggest-apple-wwdc-2026-takeaways-you-need-know"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
    "image_caption": "Tim Cook, CEO of Apple, at a March 2026 event",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body.strip()
}

# ──────────────────────────────────────────────
# Insert all articles
# ──────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
