#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Brought AI to the World's Cheapest Phones. India Will Feel It First.",
        "subheadline": "Gemini Go replaces Google Assistant on Android devices with just 2GB of RAM — a move that could put conversational AI in the hands of 300 million Indians who've never had it.",
        "slug": make_slug("google-gemini-go-android-budget-phones-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI families have long bought budget Android phones for relatives back home. Those ₹7,000 handsets — the ones that could barely run WhatsApp smoothly — now get the same AI assistant that powers Pixel flagships. For diaspora Indians who've been tech support for their parents' phones, Gemini Go could be the update that finally closes the gap.",
        "tags": ["google", "gemini", "android-go", "india", "sundar-pichai", "ai", "budget-phones"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PhoneArena", "url": "https://www.phonearena.com/news/google-gemini-go-android-go-low-end-devices"},
            {"name": "GSMArena", "url": "https://www.gsmarena.com/google_gemini_go_android_go-news-68124.php"},
            {"name": "Go Gadget News", "url": "https://gogadgetnews.com/google-gemini-expands-to-android-go/"},
            {"name": "The Mobile Indian", "url": "https://www.themobileindian.com/news/google-announces-gemini-go-for-android-go-devices"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai, CEO of Alphabet and Google",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Sundar Pichai's Google has been systematically replacing its old Google Assistant with Gemini, the company's generative AI platform, across every device category — smartwatches, cars, smart speakers, flagship phones. This week, it reached the final frontier: the cheapest phones on the planet.

Gemini Go, announced quietly through a Google support page, is a stripped-down version of the company's AI assistant built specifically for Android Go devices — the lightweight edition of Android designed for phones with as little as 2GB of RAM. It replaces Assistant Go, the basic voice-command tool that handled alarms and phone calls but couldn't hold a conversation.

The shift matters because it isn't incremental. Assistant Go was essentially a decision tree — you said a keyword, it matched an action. Gemini Go is a conversational AI model. It can process context, handle follow-up questions, accept uploaded photos and documents, and string together multi-step tasks. The gap between what a ₹7,000 Redmi phone could do and what a ₹80,000 Pixel could do just narrowed considerably.

## Why India Is Ground Zero

India is the world's largest market for Android Go devices. Hundreds of millions of Indians use budget smartphones as their primary — often only — computing device. These are the phones that run on Unisoc and MediaTek Helio chips, sold by Xiaomi, Samsung, and Realme in tier-2 and tier-3 cities.

Until this week, those users were locked out of the generative AI revolution. ChatGPT requires a decent phone and a stable connection. Google's own Gemini app wouldn't install on most Android Go hardware. The AI divide wasn't just about access to the internet — it was about access to AI itself.

Gemini Go breaks that wall. Users can now ask their phone to find a nearby restaurant with specific criteria, dictate and send messages by voice, upload a document and ask questions about it, or get contextual answers that actually understand what they're asking. It launches through the Google Search app — long-press the Home button, same as before, but the brain behind it has fundamentally changed.

## The Engineering Trick

Running a large language model on 2GB of RAM is, on paper, absurd. Most consumer-facing LLMs struggle on devices with four times that memory. Google appears to be using a hybrid approach: a tiny on-device model handles wake-word detection and basic intent classification, while heavier reasoning gets offloaded to Google's Vertex AI cloud infrastructure.

The result is a system that feels responsive on budget hardware while drawing on the same Gemini backbone that powers Google's most capable products. The tradeoff is clear — you need a data connection for anything beyond basic commands — but in a country where Jio offers 2GB of daily data for ₹199 a month, that's a manageable constraint.

## What NRIs Should Watch

For diaspora Indians who've spent years being the unofficial tech support line for family back home, Gemini Go could be quietly transformative. The parent in Lucknow who calls about every notification, the grandparent in Chennai who can't figure out Google Maps — these are people who could now simply talk to their phone and get an intelligent answer.

There's a business angle too. Google is capturing an enormous stream of conversational data from emerging markets — data that will train the next generation of multilingual, context-aware AI models. India's linguistic diversity, with its 22 official languages and hundreds of dialects, is precisely the kind of training ground Google needs to build AI that works everywhere.

The strategic logic is Pichai at his most methodical: don't wait for the hardware to catch up. Bring the AI to the hardware that exists. It's the same instinct that drove Google's investment in UPI-compatible payment systems and YouTube Go years before either seemed commercially obvious.

Gemini Go is rolling out gradually — Google's "gradual rollouts" are notorious for taking weeks — but the direction is clear. The most consequential AI deployment of the year might not be a new frontier model or a $75 billion IPO. It might be a lightweight assistant landing on a phone that costs less than dinner for two in Cupertino."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Is About to Open an AI Agent App Store. Indian Developers Should Pay Attention.",
        "subheadline": "WWDC 2026 kicks off Monday with a revamped Siri, a standalone chatbot app, and what could be the most significant platform shift since the original App Store — an AI agent marketplace.",
        "slug": make_slug("apple-wwdc-2026-ai-agent-app-store-siri-indian-developers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India is the second-largest source of iOS apps on the App Store. Thousands of Indian developers and startups in Bengaluru, Hyderabad, and Pune build for Apple's ecosystem. An AI agent marketplace is a new distribution channel — and a new revenue stream — for the same developer community that already supplies a significant share of the enterprise iOS workforce in Silicon Valley.",
        "tags": ["apple", "wwdc", "siri", "ai-agents", "app-store", "ios", "indian-developers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/06/what-to-expect-from-wwdc-2026/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/apples-wwdc-will-be-a-make-or-break-moment-for-the-companys-fledgling-ai-strategy"},
            {"name": "The Information", "url": "https://www.theinformation.com/articles/apple-siri-google-gemini-nvidia-blackwell"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/apple-stock-wwdc-2026-ai-siri/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Tim Cook, CEO of Apple Inc.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When Apple holds its Worldwide Developers Conference keynote on Monday, the headline will be Siri. The revamped assistant — now powered by Google's Gemini models running on Nvidia's Blackwell chips — has been delayed so many times since its 2024 announcement that its arrival in iOS 27 will feel less like a launch and more like an exorcism.

But the real story for developers isn't the chatbot. It's the platform underneath it.

According to The Information, Apple plans to introduce an AI agent integration with the App Store — a framework that would let third-party developers build autonomous agents capable of booking reservations, managing tasks, editing documents, and controlling smart home devices, all orchestrated through Siri. Think of it as the App Store, but for AI workers rather than apps.

## The Platform Shift

The original App Store, launched in 2008, created a $1.1 trillion ecosystem. It turned every iPhone into a platform and every developer with a good idea into a potential business. The AI agent store could do the same for a new category of software — programs that don't wait for you to open them but instead act on your behalf.

Bank of America estimates that an agentic Siri could generate up to $30 billion in additional revenue for Apple by 2030. That figure assumes Apple takes its standard platform cut — and that developers actually build agents worth using. Both assumptions depend on the developer tools Apple unveils Monday.

What's known so far: Siri will get a standalone app, similar to ChatGPT or Claude, with persistent chat history, contextual awareness, and the ability to understand what's on your screen. The Dynamic Island on newer iPhones will feature a permanently accessible Siri animation. Users will be able to swipe down for a "Search or Ask" interface. Siri will also integrate into Camera and Photos for visual intelligence — point your phone at something and ask questions about it.

## Why Indian Developers Are Positioned to Win

India is the second-largest source of iOS applications on the App Store, behind only the United States. The country's developer ecosystem has grown from a handful of outsourcing shops to a sophisticated network of product studios, indie developers, and venture-backed startups. Bengaluru alone has more registered Apple Developer Program members than most European countries.

An AI agent marketplace is a greenfield opportunity. Unlike traditional apps, which require polished interfaces and design systems, agents are fundamentally about logic, workflow orchestration, and domain expertise. Indian developers — particularly those with deep enterprise experience from years of building backend systems for global clients — are unusually well-suited to this shift.

Consider the use cases: an agent that monitors your investment portfolio and rebalances based on market conditions. An agent that coordinates your family's travel across time zones. An agent that manages rental properties, handles tenant communication, and files maintenance requests. These aren't whimsical ideas — they're the kinds of workflow-heavy, logic-dense applications that Indian engineering teams have been building for decades, just never as consumer products with their own distribution channel.

## The Technical Architecture

Apple's approach diverges from competitors in one critical way: privacy-tiered processing. Simple requests — setting a timer, sending a text — will run entirely on-device using Apple's distilled AI models. Moderate queries will route through Apple's own servers. Only the most demanding requests will flow to Google Cloud, where they'll run on Nvidia's Blackwell B200 chips with hardware-level encryption.

This three-tier system is Apple's attempt to preserve its privacy brand while admitting that its own silicon can't keep pace with the frontier models from Google and OpenAI. Craig Federighi's 2024 promise that all cloud processing would happen on Apple servers has quietly been abandoned. The company tried to run a distilled version of Gemini on its Private Cloud Compute infrastructure and found it too slow.

For developers, the architecture means building agents that work across processing tiers — handling simple tasks locally and complex reasoning in the cloud, without the user noticing the handoff. Apple's developer tools will need to abstract this complexity away, or the agent ecosystem will struggle to gain traction.

## The Stakes

WWDC 2026 is being described by analysts as Apple's most consequential developer event since the iPad launch. Wedbush's Dan Ives, Apple's most vocal bull with a $400 price target, calls it "a pivotal moment" for AI monetization. JPMorgan's Samik Chatterjee sees the new Siri as the catalyst for the iPhone 18 upgrade cycle this fall.

For the thousands of Indian engineers at Apple's Cupertino campus — and the tens of thousands more building for iOS from Hyderabad and Pune — the agent platform represents something rarer than a product launch. It's a new distribution primitive. The last time Apple created one of those, it minted millionaires from their dorm rooms.

Whether WWDC 2026 delivers on that promise depends on Monday's keynote. The AI agent App Store is either the next trillion-dollar platform or another Siri feature that ships late and underwhelms. Apple's track record with AI suggests healthy scepticism. Its track record with platforms suggests the opposite."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
