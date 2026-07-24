#!/usr/bin/env python3
"""Videshi Technology Writer — July 1, 2026 5:00 PM PDT run.
Inserts 3 fresh tech articles targeting the Indian American diaspora.
"""
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
    # ─── ARTICLE 1: OpenAI hires Prabhjeet Singh as India MD ───
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI's New India Chief Is an IIT-IIM Alum Who Ran Uber for a Decade",
        "subheadline": "Prabhjeet Singh, who expanded Uber across India and South Asia for 11 years, will lead OpenAI's second-largest market. He starts in September.",
        "slug": make_slug("openai-prabhjeet-singh-india-md-uber-iit"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An IIT Kharagpur and IIM Ahmedabad alumnus now leads OpenAI's India strategy — a signal that the AI labs are drawing from the same elite Indian talent pipeline as FAANG, with product decisions increasingly shaped by India's 100 million ChatGPT users.",
        "tags": ["openai", "india", "ai", "iit", "chatgpt", "leadership", "uber"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-26/"},
            {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/tech/openai-appoints-former-uber-india-chief-prabhjeet-singh-as-first-india-managing-director-mp99"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/02/16/india-has-100m-weekly-active-chatgpt-users-sam-altman-says/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/leadership/indias-leadership-footprint-grows-as-openai-names-ubers-prabhjeet-singh-india-md-46362"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "OpenAI CEO Sam Altman at a meeting in February 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """OpenAI has appointed Prabhjeet Singh as its first Managing Director for India, placing an IIT Kharagpur and IIM Ahmedabad alumnus at the helm of one of the company's most consequential global markets.

Singh, who served as President of Uber India and South Asia for nearly 11 years, will join OpenAI in September and report to Kiran Mani, the company's Asia Pacific Managing Director. He will be OpenAI's most senior executive in the country, overseeing consumer growth, enterprise adoption, partnerships, regulatory engagement, and operations.

The hire signals how seriously Sam Altman's company takes India. OpenAI disclosed in February that India had crossed 100 million weekly active ChatGPT users — making it the platform's second-largest market after the United States. Nearly half of those users are between 18 and 24 years old, and Indians use OpenAI's coding assistant Codex at three times the global median rate.

## From ride-hailing to the AI frontier

Singh's career arc reads like a diaspora playbook in reverse. He began at Lehman Brothers in London, moved to McKinsey & Company where he rose to Associate Partner, and then joined Uber in 2015 — well before ride-hailing had cracked India's chaotic transport market.

Over the next decade, he expanded Uber's footprint across India, Sri Lanka, and Bangladesh, launching Auto, Moto, and Shuttle products that adapted the global platform to local realities. His team also integrated Uber with India's Open Network for Digital Commerce (ONDC) and pushed electric mobility partnerships — the kind of regulatory and ecosystem navigation that OpenAI now needs in spades.

## The political dimension

India's AI policy landscape is both welcoming and watchful. Prime Minister Narendra Modi hosted Altman, Anthropic's Dario Amodei, and Google's executives at the AI Impact Summit earlier this year. The government has embraced AI as a national priority, but policymakers are also weighing how much to rely on American AI providers versus building sovereign alternatives like Sarvam AI and Bhavish Aggarwal's Krutrim.

Singh's mandate will be as much political as commercial. OpenAI established its first India office in New Delhi in November 2025 and plans additional offices in Mumbai and Bengaluru this year. But it faces stiff competition: Google offered Indian students a free year of its AI Pro plan, and India accounts for the highest global usage of Gemini for learning. The domestic AI startup ecosystem is also growing fast, with companies pitching themselves as India-first alternatives to American platforms.

## Why NRIs should pay attention

For Indian Americans working in AI — and there are tens of thousands at OpenAI, Google, Microsoft, Anthropic, and Meta — Singh's appointment is a data point in a larger pattern. The leadership pipeline between India's premier engineering institutions and the top of global tech is no longer confined to FAANG companies. The AI labs are drawing from the same talent pool, and India is becoming a market that shapes product strategy, not just a source of engineers.

OpenAI's sub-$5 ChatGPT Go tier, initially launched for India's price-sensitive market and later made free for a year, was the company's first significant departure from its one-price-everywhere approach. That product decision was driven by Indian user data. As Singh takes the reins, expect more India-specific moves — from enterprise partnerships with Tata, Infosys, and Reliance to deeper integration with India's digital public infrastructure stack.

An Uber spokesperson thanked Singh for his "leadership and lasting contributions" during his decade-long journey with the company. The real test will be whether he can do for OpenAI in India what he did for Uber: take a Western technology platform and make it indispensable in a market that rewards adaptation over imposition."""
    },

    # ─── ARTICLE 2: Google Gemini Spark launches on macOS ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Gave Its AI Agent a Desktop. It Costs $100 a Month and It Wants Your Files.",
        "subheadline": "Gemini Spark launched on macOS with third-party integrations, real-time tracking, and an Indian-origin DeepMind VP leading the engineering. The desktop agent war is on.",
        "slug": make_slug("google-gemini-spark-macos-desktop-agent"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An Indian-origin VP of Engineering at Google DeepMind co-leads the Gemini Spark launch. For millions of Indian tech professionals using Google Workspace, the choice of desktop AI agent is becoming as consequential as the choice of operating system a decade ago.",
        "tags": ["google", "gemini", "ai-agent", "macos", "sundar-pichai", "desktop", "productivity"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/01/gemini-spark-googles-agentic-assistant-is-now-available-on-mac/"},
            {"name": "Google Blog", "url": "https://blog.google/products/gemini/gemini-spark-updates/"},
            {"name": "Engadget", "url": "https://www.engadget.com/ai/gemini-spark-comes-to-googles-gemini-app-for-macos-130038498.html"},
            {"name": "Android Authority", "url": "https://www.androidauthority.com/gemini-spark-mac-desktop-automation-3581932/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Google CEO Sundar Pichai at a public event in 2023",
        "image_attribution": "Wikimedia Commons",
        "body": """Google on Wednesday rolled out Gemini Spark to its macOS desktop app, turning the AI chatbot into a full-blown desktop agent that can sort your files, build spreadsheets from invoices, and eventually take orders from your phone while you commute home.

The macOS launch, announced on June 30, brings Gemini Spark into direct competition with Anthropic's Claude Desktop, Microsoft's Copilot, and a growing field of AI desktop agents that promise to eliminate the drudgery of digital housekeeping. Spark was first unveiled at Google I/O in May, but the macOS rollout makes it the first Google AI product to work directly with files on a user's computer — a boundary the company has historically been cautious about crossing.

## What Spark actually does

In its current beta, Spark can organise and rename files, create Google Workspace documents from local sources, and turn scattered invoices into budgeting worksheets. Google says users will "soon" be able to assign multi-step tasks remotely from their phones — asking Spark to find a specific file on their Mac, extract a revenue figure, and email it before they reach their desk.

The agent also gained new integrations with Google Tasks and Google Keep, addressing a gap that reviewers flagged after Spark's initial launch. Third-party connections now include Canva, Dropbox, Instacart, OpenTable, and Zillow Rentals — a roster that suggests Google sees Spark as more than a productivity tool. Reserving tables, ordering groceries, designing flyers, and booking apartment tours are all on the roadmap.

Google also introduced support for custom Model Context Protocol (MCP), an emerging open standard that lets developers connect their own apps and data sources directly into Spark. For developers in Bengaluru and Hyderabad building on Google's ecosystem, MCP support is significant — it means Spark can be tailored to enterprise workflows without waiting for Google to ship a native integration.

## The Indian engineering connection

The Gemini Spark launch was co-led by Srinivasan (Cheenu) Venkatachary, Vice President of Engineering at Google DeepMind, alongside Product Director Adam Coimbra. Venkatachary's prominent role underscores the depth of Indian-origin leadership within Google's AI infrastructure — from Sundar Pichai at the top to the engineering executives building the products that define the company's strategy.

India is also Google's most active market for AI adoption in education. The company offered Indian students a free one-year subscription to its AI Pro plan last year, and India accounts for the highest global usage of Gemini for learning. Spark, currently available only to Google AI Ultra subscribers in the US at $100 per month, will likely follow the same trajectory of eventual Indian pricing tiers.

## The real competition is for the workspace

The desktop agent war is, at its core, a fight over who controls the modern knowledge worker's operating environment. Microsoft has Copilot embedded in Office. Anthropic's Claude Desktop can work with local files. Apple is weaving Siri into its own AI stack with Google Gemini models on the backend.

For Indian tech professionals — who constitute one of the largest populations of knowledge workers globally — the choice of desktop AI agent is becoming as consequential as the choice of operating system was a decade ago. Google's advantage is its existing workspace ecosystem: Gmail, Docs, Sheets, Calendar, Keep, and Tasks are already the default for millions of Indian businesses and startups.

The $100 monthly price tag will limit Spark's initial audience to enterprise customers and power users. But Google's track record in India suggests aggressive pricing will follow. For the thousands of Indian engineers building AI-powered automation tools, Gemini Spark is less a competitor than a platform signal: the future of personal computing is agentic, and the companies that get there first will define how the next generation of knowledge work gets done.

Privacy will be the sticking point. Google says Spark only accesses files and folders users explicitly allow — but handing an AI agent the keys to your desktop files, work documents, and third-party apps requires a level of trust that many users, particularly in enterprise environments with sensitive data, may not be ready to extend. The next battleground isn't capability. It's permission."""
    },

    # ─── ARTICLE 3: Agnikul Cosmos + ICEYE SAR partnership ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Agnikul Just Signed a Deal to Launch Radar Satellites. The Partner Is Finnish.",
        "subheadline": "Agnikul Cosmos and Finland's ICEYE will build sovereign SAR satellite capabilities in India, announced at the Bharat Innovates summit with Modi and Macron present.",
        "slug": make_slug("agnikul-iceye-sar-satellite-partnership-india-space"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's private space sector is becoming a real investment and career proposition for NRIs in aerospace — Agnikul's $500M valuation and sovereign SAR satellite deal represent both return-to-India pathways and cross-border business opportunities.",
        "tags": ["agnikul-cosmos", "iceye", "space-tech", "sar-satellite", "india-space", "isro", "deep-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/agnikul-cosmos-signs-mou-with-iceye-for-launch-of-sar-satellites/article71166019.ece"},
            {"name": "StartupNews.fyi", "url": "https://startupnews.fyi/2026/07/01/indias-agnikul-finnish-iceye-pact-sovereign-sar-satellites/"},
            {"name": "Wikipedia - AgniKul Cosmos", "url": "https://en.wikipedia.org/wiki/AgniKul_Cosmos"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Agnibaan_Republic_Day_Parade_2025.jpg/1280px-Agnibaan_Republic_Day_Parade_2025.jpg",
        "image_caption": "Agnikul Cosmos's Agnibaan rocket displayed at India's Republic Day Parade 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Agnikul Cosmos, the IIT Madras-incubated startup that builds rockets with 3D-printed engines, has signed a partnership with Finland's ICEYE to launch and operate Synthetic Aperture Radar (SAR) satellites from India — a deal that could give the country its first sovereign, all-weather space-based surveillance capability.

The Memorandum of Understanding was announced at the Bharat Innovates summit in Nice, France, where Indian Prime Minister Narendra Modi and French President Emmanuel Macron were both present. Srinath Ravichandran, Agnikul's co-founder and CEO, described the collaboration not as a simple launch services contract but as an "end-to-end solution" — combining Agnikul's launch vehicles with ICEYE's radar technology and ground infrastructure for intelligence applications.

## Why SAR matters

Unlike conventional optical satellites that need clear skies and daylight, SAR satellites use radio waves that can penetrate cloud cover, dense vegetation, and darkness. For India — a country where monsoon clouds obscure large parts of the subcontinent for months at a time — this is not an academic distinction. SAR imagery can track ship movements, monitor border activity, detect infrastructure changes, and assess disaster damage regardless of weather conditions.

ICEYE, founded in Helsinki in 2014, operates the world's largest constellation of commercial SAR microsatellites and has supplied imagery to governments and defence agencies across Europe and the United States. Under the new agreement, ICEYE will explore building local SAR manufacturing capabilities in India while leveraging Agnikul's launch infrastructure.

"India is an important market for us as demand for sovereign intelligence capabilities continues to grow globally," said Rafał Modrzewski, ICEYE's co-founder and CEO.

## Agnikul's trajectory

Agnikul has moved fast since its successful sub-orbital test launch in 2024, which featured the world's first single-piece 3D-printed semi-cryogenic rocket engine. The company, valued at over $500 million as of March 2026, can now 3D-print an entire engine in seven days — a 97 percent reduction from traditional manufacturing timelines. Its Agnibaan rocket is designed for flexible, on-demand small satellite launches carrying payloads between 30 kg and 300 kg.

The Tamil Nadu government took an equity stake in Agnikul earlier this year through its industrial arm TIDCO — the first time an Indian state government has directly invested in a space startup. The company has also partnered with Neevcloud to prototype a space-based AI data centre, targeting a launch as early as 2027.

Ravichandran told The Hindu BusinessLine that work on the collaboration has already begun, with software systems and interfaces being developed ahead of deployment. He did not reveal a specific launch date but said the companies are looking to begin as early as possible.

## The diaspora angle

India's private space sector is growing into a serious proposition for NRI investors and professionals. Agnikul, Skyroot Aerospace, Pixxel, and Dhruva Space are collectively reshaping what was once an ISRO monopoly into an open market. For Indian Americans in the aerospace and defence industries — many of whom work at SpaceX, Northrop Grumman, Lockheed Martin, and Boeing — these companies represent both a professional network and a potential return-to-India pathway.

The ICEYE partnership also sits at the intersection of two geopolitical trends that matter to the diaspora. India's space reforms, championed by IN-SPACe (the Indian National Space Promotion and Authorisation Centre), have opened the sector to private players in ways that would have been unthinkable five years ago. Simultaneously, the global demand for sovereign intelligence capabilities — particularly SAR imagery that does not depend on American or Chinese satellite networks — has created a market that India is well-positioned to serve.

For a startup that began in an IIT Madras lab, the trajectory from 3D-printed engines to sovereign surveillance satellites is a striking acceleration. Whether Agnikul can deliver on the operational demands of SAR constellation management — a far more complex challenge than launching a single sub-orbital demonstrator — will determine whether India's private space sector graduates from promising to consequential."""
    },
]

# Insert articles
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
