#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 06:00 UTC batch"""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Google Cloud data centre fire in India ──────────────────

art1_body = """A fire at a third-party data centre in Delhi has knocked out a chunk of Google Cloud's Indian network, sending Sundar Pichai's cloud division scrambling to reroute traffic across three of the country's biggest metros.

Alphabet's Google Cloud confirmed on Tuesday that the blaze triggered an emergency power shutdown at the facility, isolating a local point of presence in Delhi and slashing network capacity across the metropolitan area. The incident rippled outward, degrading connectivity for customers in Chennai and Mumbai as well — the trio of cities that together anchor India's digital economy.

Google declined to say which third-party operator runs the facility, when the fire started, or whether anyone was hurt. The company's status page offered little comfort: "no workaround" was available while engineers explored "additional traffic mitigation measures."

## The Fragility Behind the Growth Story

The outage arrives at an awkward moment. Google, Amazon, and Microsoft have collectively pledged more than $50 billion in Indian data centre and cloud investments over the next five to seven years, courting Prime Minister Modi's government with visions of AI-ready infrastructure coast to coast. Alphabet alone signalled an $80 billion AI infrastructure raise earlier this month. But Tuesday's disruption is a reminder that India's cloud backbone still leans heavily on third-party colocation providers — many of whom operate under patchwork fire-safety regulations that vary by state.

India now hosts more than 2,100 Global Capability Centres employing 2.36 million professionals, plus a fast-growing ecosystem of startups running production workloads on public cloud. When a single Delhi facility goes dark, the blast radius extends well beyond Google's own services. Payment gateways, fintech APIs, and enterprise SaaS products that route through GCP's Mumbai and Delhi regions all felt the latency spikes.

## Why NRIs Should Care

For Indian Americans working at Google — and there are tens of thousands — the incident is a visceral reminder of the infrastructure gap between their employer's US operations and its fastest-growing international market. Google's own data centres in the US are purpose-built fortresses with redundant power, fire suppression, and physical security that would make a bank vault jealous. In India, the company still relies on third-party facilities where standards can be uneven.

NRI investors tracking Alphabet stock should note that India is one of Google Cloud's priority growth markets, projected to contribute meaningfully to the division's revenue by 2028. Any pattern of outages — or worse, a customer data incident — could slow that growth trajectory.

For the broader diaspora, the fire also raises questions about India's readiness for the AI infrastructure buildout that everyone from Tata to Micron is betting on. Data centres are not just server racks; they are critical national infrastructure. If a fire at one facility can degrade service across three major cities, the redundancy math does not yet add up.

Google says restoration efforts are ongoing. For the startups and enterprises that depend on its Indian infrastructure, the wait continues — with no workaround in sight."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "A Data Centre Fire Just Exposed Google Cloud's India Problem.",
    "subheadline": "A blaze at a third-party facility in Delhi knocked out Google Cloud connectivity across three major Indian metros. The $50 billion infrastructure promise suddenly looks fragile.",
    "slug": make_slug("google-cloud-india-data-centre-fire-outage-delhi"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tens of thousands of Indian Americans work at Google; NRI investors are exposed to Alphabet stock; Indian startups running on GCP felt the outage directly; raises questions about India's AI infrastructure readiness.",
    "tags": ["google-cloud", "data-centre", "india-infrastructure", "sundar-pichai", "cloud-outage"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/fire-third-party-facility-disrupts-google-cloud-network-traffic-india-2026-06-10/"},
        {"name": "Bhasha Times", "url": "https://bhashatimes.com/google-cloud-outage-hits-india-after-fire-at-data-centre/"},
        {"name": "Google Cloud Status", "url": "https://status.cloud.google.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Google_Servers.jpg/1280px-Google_Servers.jpg",
    "image_caption": "Google server racks inside a company data centre",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2: Apple opens AI tools to developers at WWDC ──────────────

art2_body = """Apple spent two years promising developers that AI would come to their apps. At WWDC 2026, it finally handed over the tools — and the bill is zero for most of them.

The headline from Monday's Platforms State of the Union was not Siri's chatbot makeover or the Liquid Glass polish on iOS 27. It was the developer stack underneath: a Foundation Models framework that now routes seamlessly between on-device inference and Apple's Private Cloud Compute, a brand-new Core AI framework for running custom large language models locally on Apple silicon, and an Xcode 27 that embeds coding agents from Anthropic, Google, and OpenAI directly into the IDE.

## Free Cloud AI for the Long Tail

The most consequential announcement may be the quietest. Developers enrolled in the App Store Small Business Program — those with fewer than two million lifetime first-time downloads — can now access Apple's next-generation Foundation Models on Private Cloud Compute at no cost. No API fees. No metered billing. Just a Swift API call.

That threshold covers the overwhelming majority of the App Store's developer base. For indie studios and early-stage startups, the economics are transformative: cloud-hosted AI inference, the single biggest cost in building intelligent apps, drops to zero. The framework also supports third-party models through a new LanguageModel protocol, with Google's Gemini (via Firebase AI Logic) and Anthropic's Claude available at launch.

Apple confirmed the Foundation Models framework will go open source later this summer — a move that would have been unthinkable even two years ago from a company that once treated its AI stack as a state secret.

## Xcode 27: The IDE Becomes an Agent Host

The other half of the story is Xcode 27, which Apple now positions as "the best place to code with agents." The update integrates coding agents from all three major AI labs — Anthropic, Google, and OpenAI — directly into the development workflow. These are not autocomplete suggestions. They are autonomous agents that can write tests, interact with the simulator through a new Device Hub, try ideas in Playgrounds, and validate their own work across multi-turn conversations.

Xcode 27 also supports the Model Context Protocol for plug-ins, with GitHub and Figma offering first-party integrations. The IDE itself is now Apple Silicon-only, 30 percent smaller, and ships with Xcode Cloud running up to twice as fast on M-series chips.

Craig Federighi, Apple's SVP of Software Engineering, framed the pitch plainly: developers get on-device models for privacy-sensitive tasks, cloud models for heavy reasoning, and third-party models for specialised domains — all through one API surface.

## What This Means for Indian Developers

India is one of Apple's fastest-growing developer markets. The country's iOS developer community has expanded rapidly as iPhone adoption climbs in urban centres, and Indian-origin engineers are disproportionately represented at Apple itself and across the App Store ecosystem.

The free Private Cloud Compute tier is particularly significant for Indian indie developers and bootstrapped startups, who often face tighter infrastructure budgets than their Silicon Valley peers. A Bengaluru-based developer building a health app or an education tool can now ship AI features that run partly on-device and partly in Apple's cloud — without paying a rupee for inference.

The open-sourcing of Foundation Models also opens a path for Indian AI researchers and IIT computer science departments to study, fine-tune, and build on Apple's production-grade models. For Indian IT services firms like TCS, Infosys, and Wipro, which maintain large iOS development practices for enterprise clients, the agentic Xcode update means faster delivery cycles and lower labour costs per feature.

The catch? Siri AI itself will not be available in India at launch — Apple is working through regulatory requirements. But the developer tools ship globally, meaning Indian developers can build AI-powered apps for the global market even before Apple Intelligence reaches Indian consumers."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Just Made Cloud AI Free for Most Developers. Indian Builders Should Pay Attention.",
    "subheadline": "Foundation Models going open source, free Private Cloud Compute for small developers, and Xcode 27 with Claude, Gemini, and ChatGPT baked in. WWDC's developer story is bigger than Siri.",
    "slug": make_slug("apple-wwdc-foundation-models-xcode-27-free-ai-developers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is one of Apple's fastest-growing dev markets; free cloud AI removes cost barrier for Indian indie devs and startups; IT services firms (TCS, Infosys, Wipro) with iOS practices benefit from agentic Xcode; Foundation Models open-sourcing opens research doors for IITs.",
    "tags": ["apple", "wwdc", "foundation-models", "xcode", "ai-developers", "indian-developers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/09/apple-wwdc-2026-platforms-state-of-the-union/"},
        {"name": "Apple via BusinessWire", "url": "https://www.businesswire.com/news/home/20260609174692/en/Apple-accelerates-app-development-with-new-intelligence-frameworks-and-advanced-tools"},
        {"name": "Google Blog", "url": "https://blog.google/products/gemini/gemini-apple-developers/"},
        {"name": "iPhone in Canada", "url": "https://www.iphoneincanada.ca/2026/06/09/apple-just-unveiled-xcode-27-with-chatgpt-claude-and-gemini-built-in/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Craig_Federighi_at_Apple_WWDC_2019.jpg/1280px-Craig_Federighi_at_Apple_WWDC_2019.jpg",
    "image_caption": "Craig Federighi, Apple SVP of Software Engineering, presents at WWDC",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ── Article 3: Broadcom, Apollo, Blackstone $35B AI platform ───────────

art3_body = """Broadcom, Apollo Global Management, and Blackstone's credit and insurance arm have launched a $35 billion platform to finance the physical infrastructure that AI companies cannot build fast enough on their own.

The platform, called AI XPV, will underwrite more than 20 gigawatts of compute capacity through 2028 — roughly the electricity consumption of a mid-sized country — using Broadcom's custom chips and networking hardware. Its first customer: Anthropic, which will use the initial tranche to build out more than one gigawatt of compute infrastructure for training and running its Claude models.

Broadcom CEO Hock Tan framed it as a marriage of silicon roadmaps and patient capital. "This combines Broadcom's technology roadmap with long-term capital to support the growing demand for AI computing infrastructure," he said Tuesday.

## The Numbers Behind the Noise

Twenty gigawatts is a staggering figure. For context, India's entire data centre capacity was estimated at roughly 1.3 gigawatts in early 2026, and the country's ambitious target is to reach 4 gigawatts by 2030. The AI XPV platform alone plans to finance five times India's current capacity in under three years.

The $35 billion initial tranche is just the beginning. Apollo and Blackstone are positioning themselves as the primary capital partners for what they see as a structural shift: AI infrastructure buildouts are too large and too capital-intensive for even the biggest tech companies to finance entirely from their balance sheets. OpenAI, Anthropic, Google, and Meta are all spending at rates that make traditional tech capex look modest — Alphabet alone signalled an $80 billion infrastructure raise this month.

Private capital is rushing in to fill the gap, and the returns are attractive: long-term contracts, predictable power consumption, and technology partners with clear roadmaps.

## Broadcom's Quiet Indian Empire

Broadcom does not make headlines the way NVIDIA or Apple do, but it is one of the most consequential employers of Indian engineering talent in the semiconductor industry. The company's design centres in Bengaluru and Hyderabad employ thousands of engineers working on custom AI accelerators (XPUs), networking ASICs, and the switching fabric that holds hyperscale data centres together.

Hock Tan, who is Malaysian-born and Stanford-educated, has built Broadcom into a $900 billion company through a relentless acquisition strategy — VMware, Symantec's enterprise division, CA Technologies — and a design philosophy that prioritises custom silicon over general-purpose chips. The AI XPV platform extends that logic: rather than compete with NVIDIA on GPUs, Broadcom is building the bespoke infrastructure layer that AI companies need around their GPU clusters.

For Indian engineers at Broadcom, the platform means job security and career growth. Custom AI chip design is the highest-demand skill in the semiconductor industry, and Broadcom's Indian centres are at the heart of it.

## What NRIs Should Watch

The AI infrastructure financing boom has three implications for the Indian diaspora.

First, NRI investors holding Broadcom stock (AVGO) should understand that the AI XPV platform shifts risk. Broadcom is not fronting $35 billion of its own capital; it is providing the technology while Apollo and Blackstone provide the financing. That is a capital-light model that could boost margins without ballooning the balance sheet.

Second, the platform's scale underscores how far behind India remains in data centre capacity. If 20 gigawatts of AI compute is being built in the US and Europe over the next three years, India's 1.3-gigawatt base looks increasingly insufficient for a country that aspires to be an AI power. The "picks and shovels" investment thesis — that India can profit from AI through electricity, cooling, and physical infrastructure — requires dramatically faster buildout than anything currently planned.

Third, the Anthropic connection matters. Anthropic recently expanded its India leadership team and is scaling Claude adoption across Indian enterprises and startups. If its compute capacity triples through the AI XPV platform, the downstream effect on Indian AI development could be substantial — more API capacity, lower latency for Indian users, and a larger footprint for Indian engineers contributing to safety research."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Broadcom Just Raised $35 Billion for AI Infrastructure. India's Data Centre Gap Just Got Wider.",
    "subheadline": "The AI XPV platform with Apollo and Blackstone will finance 20 gigawatts of compute — fifteen times India's entire data centre capacity. Broadcom's Indian engineers are at the centre of the build.",
    "slug": make_slug("broadcom-apollo-blackstone-35-billion-ai-infrastructure-xpv"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Broadcom employs thousands of Indian engineers in Bengaluru/Hyderabad design centres; NRI investors hold AVGO stock; India's 1.3GW data centre capacity dwarfed by 20GW AI XPV target; Anthropic expanding India operations with new compute.",
    "tags": ["broadcom", "ai-infrastructure", "apollo", "blackstone", "anthropic", "data-centre", "semiconductor"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/broadcom-apollo-blackstone-launch-35-billion-ai-infrastructure-platform"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/09/tech/openai-anthropic-spacex-ipo-ai-wall-street/index.html"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260602PD224/google-cloud-capex-ai-infrastructure.html"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Hock_Tan_2022.png",
    "image_caption": "Hock Tan, CEO of Broadcom, architect of the AI XPV platform",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ── Insert all articles ────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
