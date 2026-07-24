#!/usr/bin/env python3
"""Videshi Technology Writer — July 3, 2026 5:00 PM run."""
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
    # ─────────────────────────────────────────────────────────
    # ARTICLE 1: Google Gemini Spark on macOS
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Pichai's Google Just Put an AI Agent on Your Mac. It Sorts Your Files, Books Tables and Orders Groceries.",
        "subheadline": "Gemini Spark turns Google's chatbot into a desktop automation tool that touches local files — a first for any major AI assistant. Apple, whose own Siri now runs on Gemini, is watching.",
        "slug": make_slug("google-gemini-spark-mac-ai-agent-pichai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin CEO Sundar Pichai's latest move puts Google ahead in the AI agent race, with implications for Indian engineers at Google and Indian SaaS companies competing in the automation space.",
        "tags": ["google", "gemini", "sundar-pichai", "ai-agents", "apple", "indian-tech-leaders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/07/01/google-gemini-spark-comes-to-mac/"},
            {"name": "Engadget", "url": "https://www.engadget.com/ai/gemini-spark-comes-to-googles-gemini-app-for-macos-143054498.html"},
            {"name": "Gadgets 360", "url": "https://www.gadgets360.com/ai/news/google-gemini-spark-macos-ai-desktop-automation-files-apps-8095411"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Google CEO Sundar Pichai at a company event in 2023",
        "image_attribution": "Wikimedia Commons",
        "body": """Google has turned its Gemini chatbot into something qualitatively different: a desktop agent that can open, sort and act on files sitting on your hard drive. On July 1, the company rolled out Gemini Spark for macOS, adding a dedicated Spark tab to the sidebar of its Gemini desktop app that lets the AI touch local files — not just answer questions about them.

The distinction matters. Until now, mainstream AI assistants have lived inside a chat window, responding to queries but never reaching into your actual computer. Spark crosses that line. Users can ask it to sort PDFs from a bloated Downloads folder into labelled subfolders, pull invoice figures from locally saved files and build a Google Workspace spreadsheet on a recurring schedule, or reorganise project directories. You decide which folders it can see; you can revoke access at any time.

## Beyond the desktop

Google also announced a wave of third-party integrations for Spark on web and mobile. New connected apps include Google Tasks, Google Keep, Canva, Dropbox, Instacart, OpenTable and Zillow Rentals. The practical effect: Spark can convert your Keep notes into task lists, reserve a restaurant table, order groceries or book an apartment tour — all from a single prompt.

More consequentially for developers, Google is adding support for custom Model Context Protocol (MCP) servers, an open standard that lets users plug additional services directly into Spark. Think of it as a universal adapter for AI agents — and Google is betting that its ecosystem will be the one developers build for.

Spark also gains what Google calls "real-time topic tracking," a proactive monitoring feature that watches blogs, news sites, social media, finance feeds, sports, weather and email, then alerts users when specified conditions are met. It is, in effect, a personal intelligence layer that runs continuously in the background.

## The price — and the irony

Gemini Spark for macOS is in beta, available to Google AI Ultra subscribers aged 18 and over in the United States. The price: $99 per month. That puts it squarely in premium territory, competing less with free chatbots and more with dedicated productivity tools.

The deeper irony will not be lost on the tech industry. Apple's own revamped Siri, announced at WWDC 2026, runs on Google's Gemini models under the hood. Apple analyst Ming-Chi Kuo has argued that the "real test" for Apple is whether it can deliver better AI experiences than Google using the same underlying technology. With Spark, Google is making that test harder by shipping agent capabilities on Apple's own platform before Apple does.

## Why the diaspora should care

For Indian Americans in tech, this is a story about one of their own shaping the industry's direction. Sundar Pichai, who grew up in Chennai and studied at IIT Kharagpur before arriving at Stanford, is presiding over what may be Google's most consequential product pivot since the launch of Chrome. Gemini now has over 650 million monthly active users and 13 million developers building with its tools — figures Google disclosed alongside the launch of Gemini 3 and its advanced Deepthink variant.

For the thousands of Indian engineers at Google — many on H-1B visas — Spark represents a shift in what they are building. The company is moving from a search-first model to an agent-first model, and teams across Mountain View, Bangalore and Hyderabad are being reorganised around this priority.

The ripple effects extend to India's SaaS ecosystem. Companies like Freshworks, Zoho and BrowserStack have built thriving businesses on productivity automation. If Google's AI agent can handle file management, scheduling and task orchestration out of a $99-per-month box, the competitive pressure on standalone tools will intensify. The question for Indian SaaS founders is no longer whether AI agents are coming for their market — it is whether Google's agent gets there first.

For now, Spark is a Mac-only beta in the US. Google says a future update will let users start tasks on their Mac from a phone. If that works, the line between a chatbot and an operating system will have blurred beyond recognition — and the person who blurred it grew up in a two-room apartment in Madurai."""
    },
    # ─────────────────────────────────────────────────────────
    # ARTICLE 2: South Korea's $591 Billion Semiconductor Plan
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "South Korea Just Bet $591 Billion on Chips. India's Semiconductor Dream Looks Like a Rounding Error.",
        "subheadline": "Samsung and SK Hynix will build new mega-fabs, double memory chip output and race to own the AI supply chain. India's $10 billion chip mission has a long way to go.",
        "slug": make_slug("south-korea-591-billion-semiconductor-india-chip"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRI investors tracking semiconductor stocks and Indian engineers working at Samsung, SK Hynix and Micron, South Korea's massive bet reshapes the global chip map — and raises hard questions about India's own fab ambitions.",
        "tags": ["semiconductors", "samsung", "sk-hynix", "india-chips", "ai-infrastructure", "micron-india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynix-spend-64-billion-flash-memory-chip-plants-under-broader-ai-investment-2026-07-02/"},
            {"name": "KED Global", "url": "https://www.kedglobal.com/semiconductors/newsView/ked202506300012"},
            {"name": "Wccftech", "url": "https://wccftech.com/samsung-ready-to-tackle-intel-tsmc-with-its-1-4nm-process-tech-aiming-mass-production-for-2029/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Semiconductor_Wafer_of_Microelectronics.jpg/1280px-Semiconductor_Wafer_of_Microelectronics.jpg",
        "image_caption": "A semiconductor wafer used in microelectronics manufacturing",
        "image_attribution": "Wikimedia Commons",
        "body": """South Korea has decided to go all in. This week, Seoul unveiled a 911 trillion won ($591 billion) semiconductor investment plan that makes every other country's chip ambitions look tentative. The plan spans new memory fabs in the southwest, advanced packaging facilities, and a second chip cluster outside the Seoul metropolitan area — a political and industrial gamble on a scale that even the United States, with its $52 billion CHIPS Act, has not attempted.

At the centre of this bet are two companies: Samsung Electronics and SK Hynix, the world's two largest memory chipmakers. They plan to invest a combined 800 trillion won ($500 billion) to build four front-end fabs in South Jeolla Province, creating what Seoul hopes will become a second semiconductor heartland.

## SK Hynix goes big on NAND

SK Hynix, which has emerged as the AI boom's biggest winner thanks to its dominance in High Bandwidth Memory (HBM) chips, provided details of its own plans on Thursday. CEO Kwak Noh-jung announced 100 trillion won ($64 billion) for two facilities in Cheongju: 80 trillion won for a new NAND flash memory fab by 2029, and 20 trillion won for a chip packaging plant by late 2027.

The urgency is real. AI hyperscalers — Microsoft, Google, Amazon, Meta — are consuming memory chips at a rate that has pushed DRAM and NAND prices to historical highs. SK Hynix's market capitalisation briefly touched $1.3 trillion this week, within striking distance of Samsung as South Korea's most valuable listed company. Its planned Nasdaq ADR listing, targeted for July 10, could raise up to $29 billion — potentially the largest tech listing in a decade.

Samsung, meanwhile, is accelerating construction of a mega-fab at its Pyeongtaek complex by six months and eyeing 1.4-nanometre chip production by 2029 using ASML's latest high-NA EUV lithography tools. It has also secured its first chip order from Elon Musk's Neuralink for a fourth-generation brain-computer interface chip, expanding a relationship that already includes a $16.5 billion Tesla AI chip contract.

## India's $10 billion reality check

For India, the numbers are sobering. The India Semiconductor Mission, launched with approximately $10 billion in incentives, has attracted commitments from Tata Electronics (a fab in Dholera, Gujarat), Micron Technology (an assembly and test facility in Sanand, Gujarat) and CG Semi. These are real projects, and India's first commercially produced chips are expected by 2027.

But the scale gap is enormous. South Korea's plan is sixty times larger than India's entire semiconductor budget. Where Samsung and SK Hynix are building cutting-edge fabs at the 4nm and sub-2nm nodes, India's initial facilities will focus on older, less advanced technologies — the 28nm and 40nm processes that the industry moved past years ago.

This does not mean India's bet is wrong. Every major semiconductor nation started with mature-node fabs and worked up. Taiwan's TSMC began as a foundry for other people's designs at trailing nodes. India's advantage is its massive engineering talent pipeline — thousands of Indian-origin semiconductor professionals already work at Samsung, SK Hynix, Micron, Intel and TSMC — and its growing domestic market for chips in everything from smartphones to electric vehicles.

## What NRIs should watch

For Indian Americans in the semiconductor industry, South Korea's investment surge has direct implications. Indian engineers at Samsung's Austin, Texas fab and SK Hynix's US operations will be at the forefront of this expansion. Those tracking stocks have watched SK Hynix surge more than 400% in two years, while Micron — led by Indian-origin CEO Sanjay Mehrotra — posted a record $41 billion quarter fuelled by AI memory demand.

The investment arms race also matters for NRIs considering reverse migration. India's chip fabs will need thousands of experienced semiconductor professionals, and the government is actively courting diaspora talent. Tata Electronics has already begun hiring Indian engineers from global chipmakers for its Dholera facility.

But the hard truth remains: building a semiconductor ecosystem takes decades, not budget cycles. South Korea has been at it since the 1980s. India is just getting started. The $591 billion plan is not just an investment — it is a statement about how much it costs to be a serious player in the industry that will define the rest of the century. For India, the question is not whether it can match that figure, but whether it can build a sustainable chip industry before the window of opportunity — driven by AI demand, geopolitical realignment and supply chain diversification — closes."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
