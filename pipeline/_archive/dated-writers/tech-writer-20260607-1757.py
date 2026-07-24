#!/usr/bin/env python3
"""Videshi Technology Writer – 2026-06-07 18:00 UTC batch"""

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
# ARTICLE 1: SpaceX IPO
# ──────────────────────────────────────────────
art1_body = """SpaceX is five days from becoming the most expensive initial public offering in history. When Elon Musk's rocket-and-satellite conglomerate begins trading on the Nasdaq on June 12 under ticker SPCX, it will carry a price tag of roughly $1.77 trillion — eclipsing Saudi Aramco's 2019 debut by nearly every measure. The company plans to sell 555.6 million shares at a fixed price of $135 each, raising $75 billion in a single transaction. Bloomberg reports the deal is already oversubscribed.

For NRI investors who watched Indian IPOs like Hyundai India and Swiggy with keen interest last year, the numbers are in a different galaxy. Morgan Stanley, one of SpaceX's underwriters, projects the company could generate $3.4 trillion in cumulative revenue by 2040. That projection rests on three legs: Starlink satellite broadband, the Starship launch vehicle, and a nascent AI computing business built around orbital data centres.

The reality is more complicated. SpaceX reported $18.67 billion in revenue for 2025, a 33 per cent increase from the prior year. But it also posted a net loss of $4.9 billion, swinging from a $791 million profit in 2024. Only Starlink generates cash. The rocket launch business and everything else continue to burn it.

Morningstar analyst Nicolas Owens offered a blunt assessment on a Friday webinar: the company's financial projections, which include a claim to a $28.5 trillion total addressable market, are not grounded in reality. "That essentially equals every dollar spent on mobile services on Earth," he said of the $1.6 trillion connectivity TAM alone. The Motley Fool went further, warning the deal could amount to "the greatest transfer of wealth from retail buyers to insiders in memory."

## Why This Matters to Indian Tech Workers

SpaceX employs hundreds of Indian-origin engineers across its Hawthorne, Boca Chica, and Redmond facilities. For those on H-1B or L-1 visas, the IPO creates a complex calculus. Pre-IPO stock grants — common at SpaceX — become liquid on listing day, but the 180-day lockup for most employees means the actual payday arrives in December. Tax planning gets thorny: the spread between grant price and market price on vesting triggers ordinary income tax, and with a $135 share price, the bills can be substantial.

For NRI investors outside SpaceX, the question is simpler but no less fraught. Musk will retain approximately 82.4 per cent of voting power after the IPO, a governance structure that gives shareholders almost no say in the company's direction. The fixed pricing — unusual for an IPO of this size — signals Musk's determination to dictate terms rather than test market demand through traditional bookbuilding.

## The Bigger Picture

SpaceX is not arriving alone. Anthropic, maker of the Claude chatbot, filed a confidential S-1 this week, and OpenAI is expected to follow before year-end. The three companies could collectively raise $240 billion at a combined valuation exceeding $4 trillion. For Indian investors who have built portfolios around FAANG stocks and Indian tech unicorns, this is the beginning of a new asset class: pre-profit AI infrastructure companies priced like sovereign wealth funds.

The chip selloff that wiped over $1 trillion from semiconductor stocks on Friday — triggered by Broadcom's decision to merely reiterate rather than raise its AI revenue guidance — serves as a warning. Markets have priced in perfection. Anything less gets punished. SpaceX's IPO will test whether that appetite for AI-adjacent growth extends to a company that loses $4.9 billion a year and is controlled by the world's most unpredictable CEO.

Proceed with open eyes."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SpaceX Is About to Become History's Biggest IPO. Indian Investors Should Read the Fine Print.",
    "subheadline": "Elon Musk's $1.77 trillion rocket company lists June 12. It lost $4.9 billion last year and gives shareholders almost no voting power.",
    "slug": make_slug("spacex-ipo-177-trillion-nri-investors-fine-print"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "Indian-origin SpaceX engineers face complex tax implications from pre-IPO grants going liquid; NRI investors evaluating the IPO must contend with Musk's 82% voting control and a company that burns billions annually; the deal marks the start of a new asset class — pre-profit AI infrastructure companies — that will reshape NRI tech portfolios.",
    "tags": ["spacex", "ipo", "elon-musk", "nri-investors", "nasdaq", "starlink"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/us/chip-selloff-erases-over-1-trillion-stock-market-value-2026-06-06/"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/07/will-spacex-aiming-for-the-biggest-ipo-ever-soar/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/can-spacex-live-up-to-wall-streets-multitrillion-dollar-hype/"},
        {"name": "Stocktwits", "url": "https://stocktwits.com/news/article/spcx-ipo-record-75-billion-offering-is-already-oversubscribed/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Falcon_9_first_stage_at_LZ-1%28two%29.jpg/1280px-Falcon_9_first_stage_at_LZ-1%28two%29.jpg",
    "image_caption": "A SpaceX Falcon 9 first stage lands at Landing Zone 1 after a mission",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 2: Indian Semiconductor Startups at France
# ──────────────────────────────────────────────
art2_body = """Three Indian semiconductor startups will represent the country at Bharat Innovates 2026, a deep-tech showcase running June 14 to 16 in Nice, France. VerveSemi, AGNIT Semiconductors, and Netrasemi have been selected under a Ministry of Education initiative to put India's chip design capabilities in front of European investors, manufacturers, and defence buyers. It is a small delegation, but the signal it sends is outsized: India is no longer content to merely assemble electronics. It wants to design the silicon inside them.

The three companies could hardly be more different in what they build, and that is the point.

## VerveSemi: The Analogue Bridge

VerveSemi, based in Greater Noida and founded in 2017, makes mixed-signal and analogue chips — the components that let the physical world talk to digital systems. In February 2026, it closed a $10 million Series A round led by investor Ashish Kacholia and Unicorn India Ventures, a round the company says was oversubscribed several times over. Its chips now appear in EV motor controllers and space-grade sensors, two markets where reliability outranks raw speed.

For an industry that obsesses over nanometre nodes and AI accelerators, analogue design is the quiet workhorse. Nearly every piece of electronics — from a car's battery management system to a satellite's power supply — relies on analogue chips that convert real-world signals into digital data.

## AGNIT: Gallium Nitride for Defence

AGNIT Semiconductors is a spin-off from the Indian Institute of Science in Bengaluru, the result of roughly 15 years of lab research in gallium nitride (GaN). Founded in 2019, it calls itself India's first vertically integrated GaN company — meaning it controls the entire chain from wafer growth to finished component. In 2023, the Ministry of Defence signed a contract with AGNIT for advanced GaN semiconductors destined for next-generation radars and electronic warfare jammers.

GaN's advantages are well known in the industry: it handles higher frequencies and power densities than traditional silicon, which makes it essential for 5G base stations, defence systems, and fast chargers. The strategic dimension matters: India currently imports most of its high-frequency defence electronics. A domestic source changes the procurement calculus.

## Netrasemi: Edge AI, Made in Kerala

Netrasemi, founded in 2020 in Thiruvananthapuram, builds power-efficient chips for edge AI. Its flagship A2000, fabricated on TSMC's 12-nanometre process, recently reached silicon bring-up — the stage where a chip is powered on for the first time and tested. IT Minister Ashwini Vaishnaw described it as India's first edge AI system-on-chip. The company has raised approximately ₹125 crore from backers including Zoho and Unicorn India Ventures, with commercial volumes targeted for 2027.

The A2000 is designed for surveillance cameras, drones, and robotics — markets where processing must happen on the device rather than in the cloud, because latency and bandwidth constraints make round trips impractical.

## The Diaspora Opportunity

For the estimated 100,000-plus Indian semiconductor professionals working in the United States — at NVIDIA, Intel, Qualcomm, Broadcom, and dozens of smaller firms — these startups represent a shift they have watched from afar for two decades. India's chip design ecosystem has historically been a services play: engineers in Bengaluru and Hyderabad working on American companies' designs, not their own.

The India Semiconductor Mission has approved 10 major projects across six states, representing ₹1.60 lakh crore (roughly $19 billion) in cumulative investment. Tata Electronics is building a fabrication plant in Dholera, Gujarat. Micron's $2.75 billion ATMP facility in Sanand is 60 per cent complete. The IIT Delhi-Cadence innovation lab, announced last week, aims to train the next generation of chip designers using industry-grade EDA tools.

For NRI semiconductor engineers contemplating a return, the question is shifting from "Is there an industry to return to?" to "Which part of the value chain has the best opening?" The answer, as this French showcase suggests, may be design — where India's engineering talent has always been strongest and where the capital requirements are a fraction of what fabrication demands."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Chip Designers Just Landed on a Global Stage. France Is Watching.",
    "subheadline": "Three semiconductor startups — building analogue chips, gallium nitride defence components, and edge AI processors — will represent India at Bharat Innovates 2026 in Nice.",
    "slug": make_slug("india-semiconductor-startups-france-bharat-innovates"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "Over 100,000 Indian semiconductor professionals work in the US at NVIDIA, Intel, Qualcomm, and Broadcom; India's chip design ecosystem is shifting from a services play to building indigenous products; the $19 billion India Semiconductor Mission creates return-to-India career and investment opportunities for NRI engineers.",
    "tags": ["semiconductor", "india-semiconductor-mission", "vervesemi", "agnit", "netrasemi", "chip-design"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/indian-semiconductor-startups-france-bharat-innovates"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260601VL206/india-intel-semiconductor.html"},
        {"name": "NASSCOM", "url": "https://community.nasscom.in/communities/semiconductor/catalysing-next-generation-startups-semiconductor-design-space"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Close-up of electronic microchips on a circuit board",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 3: Tim Cook's Last WWDC + Siri Gemini
# ──────────────────────────────────────────────
art3_body = """When Tim Cook walks onto the stage at Apple Park on Monday morning for WWDC 2026, it will be for the last time as chief executive. In September, John Ternus — a 25-year Apple veteran who runs hardware engineering — takes the title. Cook moves to executive chairman. The transition, announced in April and approved unanimously by Apple's board, ends a 15-year CEO tenure that saw Apple's market value climb from $350 billion to peaks above $4 trillion.

But Cook does not get a farewell tour. He gets an exam.

The centrepiece of Monday's keynote is a rebuilt Siri, and the stakes are unusually personal. Apple promised a smarter voice assistant at WWDC 2024. Then again at WWDC 2025. Both times, delivery lagged. This time, the company has outsourced the problem: a custom 1.2-trillion-parameter Gemini model from Google will power Siri's most complex requests, running on Google's data centres equipped with NVIDIA's Blackwell B200 chips. The reported cost is $1 billion per year.

## What Changes for Users

Siri 2.0, as leakers have dubbed it, will land as part of iOS 27 this September. The headline features:

A **standalone Siri app** — not just a voice overlay but a full chatbot interface with conversation history, file uploads, and cross-device sync via iCloud. Think ChatGPT, but with deep hooks into Apple's own apps.

**Dynamic Island integration** — Siri will live permanently in the Dynamic Island on iPhone, accessible with a swipe rather than a voice command. An expanding cursor effect and a "Search or Ask" prompt replace the old floating orb.

**Agentic capabilities** — Siri will control device settings, read on-screen content, and pull personal context from Messages, Notes, Mail, and Calendar to answer questions. The word Apple is using internally is "agent," not "assistant."

**Third-party AI extensions** — an App Store system that lets users swap Siri's backend for ChatGPT, Claude, Grok, or any other model that meets Apple's API requirements. This is the most radical architectural decision: Apple is positioning itself as the orchestration layer, not the intelligence layer.

Privacy, always Apple's trump card, is handled through NVIDIA's hardware-based confidential computing. User queries sent to Google's servers are encrypted in a way that prevents even Google from reading the data in plaintext. It is an elegant engineering solution to an awkward business reality: Apple's own on-device models were not good enough.

## What It Means for Indian Engineers

Apple employs tens of thousands of Indian engineers across Cupertino, Austin, and Hyderabad. The CEO transition carries specific implications. Ternus is a hardware leader — he oversaw the engineering of every iPhone, iPad, and Mac for the past five years. Johny Srouji, who led Apple's custom silicon effort, becomes chief hardware officer. For the Indian engineers who design Apple's A-series and M-series chips in teams spanning California and India, this is a leadership structure that values what they build.

The Google partnership, meanwhile, puts Indian talent on both sides of the deal. Google's Gemini team includes a significant number of Indian-origin researchers and engineers. Neal Mohan, an Indian American, runs YouTube within the same Alphabet structure. The pipeline that carries Siri queries from iPhones to Google's Blackwell-powered data centres will be maintained, in substantial part, by Indian professionals at both companies.

For Indian app developers, the new Siri Extensions framework opens a genuine opportunity. Any developer who builds an AI model — or wraps one — can now plug into Siri's distribution. That is 1.5 billion active Apple devices, accessible through a voice interface.

## The Ternus Era Begins

Cook's legacy is operational excellence: supply chain mastery, services revenue, a stock price that compounded at 22 per cent annually. What he did not deliver was an AI strategy that matched the competition. The Siri rebuild, powered by a competitor's model, is simultaneously Cook's most honest admission and his most pragmatic decision. He is handing Ternus a company that finally has an AI product worth shipping, even if Apple did not build the brain inside it.

WWDC 2026 starts at 10 a.m. Pacific on Monday. The demos need to work."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Tim Cook's Last Keynote. Apple's Billion-Dollar Bet on Google's AI.",
    "subheadline": "WWDC 2026 on Monday will unveil a Siri rebuilt on a custom Google Gemini model, running on NVIDIA Blackwell chips. It is Tim Cook's final act as CEO — and his most consequential.",
    "slug": make_slug("tim-cook-last-wwdc-siri-gemini-google-apple"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "Apple employs tens of thousands of Indian engineers in Cupertino, Austin, and Hyderabad; the Ternus-Srouji leadership team values hardware — which is what Indian chip design teams build; Google's Gemini team has significant Indian-origin talent; the new Siri Extensions API opens a distribution channel to 1.5 billion devices for Indian app developers.",
    "tags": ["apple", "wwdc", "siri", "tim-cook", "google-gemini", "nvidia"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/apples-wwdc-will-be-a-make-or-break-moment-for-the-companys-fledgling-ai-strategy/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/technology/ios-27-arriving-tomorrow-compatible-devices-siris-big-ai-updates-and-expected-features/"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/tim-cooks-final-curtain-at-wwdc-2026/"},
        {"name": "PhoneArena", "url": "https://www.phonearena.com/news/what-to-expect-from-siri-at-wwdc-this-monday-and-afterward_id237431"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
    "image_caption": "Tim Cook, Apple's outgoing CEO, at a March 2026 event",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ──────────────────────────────────────────────
# PUBLISH
# ──────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
