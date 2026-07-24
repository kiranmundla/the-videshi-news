#!/usr/bin/env python3
"""Videshi Technology Writer — June 30, 2026 (23:00 PT run)"""
import json, os, uuid, re, requests, urllib.parse
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


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ─────────────────────────────────────────────
# ARTICLE 1: Qualcomm's AI Data Center Pivot
# ─────────────────────────────────────────────

qualcomm_body = """Qualcomm has spent decades as the company inside your phone. Now it wants to be the company inside the data centre that thinks for you.

In a single week, the San Diego chipmaker announced a $3.9 billion all-stock acquisition of AI software startup Modular, unveiled a 250-core server CPU called the Dragonfly C1000, secured Meta as its first hyperscaler customer, and — according to The Information — entered talks to buy AI chip startup Tenstorrent for as much as $10 billion. Combined, the moves represent the most ambitious pivot in Qualcomm's four-decade history: from mobile-first to AI-everywhere.

## The CUDA Problem

The biggest barrier for any company trying to challenge Nvidia in AI computing is not hardware. It is software. Nvidia's CUDA platform, a programming framework that lets developers write code optimised for its GPUs, has locked in millions of engineers over 15 years. Competing chip companies — AMD, Intel, a parade of startups — have all struggled to break that grip.

Modular, founded in 2022 by Chris Lattner (the architect behind Apple's Swift programming language and LLVM) and Tim Davis, was built specifically to solve this. Its programming language, Mojo, lets developers write high-performance AI code once and run it across any hardware — Nvidia, AMD, or Qualcomm's own silicon. Its inference engine, Max, competes with open-source serving frameworks like vLLM but is designed to work without the hand-tuning those tools demand.

For Qualcomm, Modular is not just a software layer. It is the moat the company never had.

## The Hardware Stack

At its June Investor Day, Qualcomm revealed the Dragonfly C1000, a server-grade CPU built on its custom Oryon architecture with 250 cores clocked above 5 GHz. The chip is designed for agentic AI — the next wave of AI workloads where models do not just generate text but autonomously execute multi-step tasks.

Meta has signed a multi-year agreement to deploy the C1000 across its data centres, with shipments scaling in the second half of 2028. Microsoft CEO Satya Nadella appeared in a video endorsing Qualcomm's HBC (High Bandwidth Computing) inference chip, calling out its "high memory bandwidth and integrated compute" as unlocking improvements in cost and performance for Azure's AI infrastructure.

Then there is Tenstorrent. Reuters reported that Qualcomm is in talks to acquire the Toronto-based startup, led by legendary chip designer Jim Keller (who previously designed chips at AMD, Apple, and Tesla), for $8 billion to $10 billion. Tenstorrent builds accelerators on the open-source RISC-V architecture — a move that would free Qualcomm from its complicated licensing relationship with Arm.

## The Numbers

Qualcomm's stock has surged 66 per cent in three months. Management is projecting $15 billion in AI infrastructure revenue by fiscal 2029, up from effectively nothing today. The total addressable market it is chasing — combining data centre, edge computing, and automotive — is projected at $1.7 trillion by 2030.

## Why Indian Engineers Should Pay Attention

Qualcomm is one of the largest employers of Indian tech talent in the United States. Its San Diego headquarters and its R&D centres in Hyderabad, Bangalore, and Chennai together employ thousands of Indian engineers, many on H-1B visas. The company has historically been a top H-1B sponsor, consistently ranking among the top 20 employers filing H-1B petitions.

The AI pivot revalues their skills overnight. Engineers who spent careers optimising mobile processors — power efficiency, edge computing, on-device inference — now find themselves working on exactly the capabilities the AI data centre market demands. Qualcomm's bet on inference rather than training plays directly to the strengths of its mobile-computing DNA: doing more with less power.

For NRI investors, the stock's 66 per cent run-up reflects the market's early pricing of this transformation. But the real test arrives in 2027, when the HBC chip begins sampling and Qualcomm must prove it can win orders against an entrenched Nvidia in the most competitive market in technology."""

qualcomm_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-buy-startup-modular-4-billion-ai-software-push-2026-06-24/"},
    {"name": "The Register", "url": "https://www.theregister.com/2026/06/30/qualcomm_ai250_modular/"},
    {"name": "The Information (via Reuters)", "url": "https://www.reuters.com/technology/qualcomm-talks-buy-tenstorrent-information-reports-2026-06-15/"},
    {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/qcom-stock-pivots-from-mobile-to-ai-with-modular-deal-and-new-server-cpu/"},
    {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/29/qualcomm-remaking-itself-ai-company-shares-cheap/"}
])


# ─────────────────────────────────────────────
# ARTICLE 2: Kunal Shah → WhatsApp Global CEO
# ─────────────────────────────────────────────

kunal_body = """Kunal Shah started CRED in 2018 with a million dollars of his own money, a contrarian thesis about credit card bills, and an allergy to conventional startup playbooks. Eight years later, Meta is paying $900 million to invest in his company — and hiring him to run WhatsApp, the messaging app used by more than two billion people worldwide.

The announcement, made on June 22, is the most consequential Indian founder-to-global-CEO transition since Satya Nadella took over Microsoft. Shah will replace Will Cathcart, who led WhatsApp for seven years and oversaw a period where its user base more than doubled. Cathcart will remain at Meta in a new role focused on AI-powered consumer products.

## The CRED Arc

The numbers tell one story: CRED grew from zero to 17 million members, hit roughly $325 million in annual revenue across payments, lending, insurance, wealth, and commerce, and recorded its first profitable quarter in 2026. The company has raised over $900 million across eight rounds, conducted four ESOP buybacks, and secured a full stack of regulatory licences.

The less visible story is what attracted Meta. CRED built a premium consumer platform in India where users willingly share financial data in exchange for rewards — a behavioural loop that maps almost perfectly onto what Meta wants WhatsApp to become: a platform where people transact, not just chat.

Meta's $900 million investment, structured as a combination of primary capital and secondary share purchases, gives it approximately a 20 per cent minority stake in CRED at a post-money valuation of $4.5 billion. Importantly, Meta will not receive access to CRED's customer data — a stipulation that likely made the deal palatable to Indian regulators watching foreign tech investment closely.

## Running WhatsApp from Bengaluru

Shah will operate from Bengaluru, at least initially, though Meta's Menlo Park headquarters will require regular visits during the leadership transition. The decision to keep WhatsApp's global CEO in India is not symbolic. India is WhatsApp's largest market by a wide margin — over 500 million users — and the country where the app's commercial ambitions have advanced furthest, from UPI-integrated payments to business catalogues to customer service bots.

Meta's chief product officer Chris Cox, who recruited Shah, described him as someone with "strong, long-held views about how WhatsApp can become even more useful in people's lives." Translation: Shah has been hired to monetise WhatsApp without breaking it.

Miten Sampat, who has been leading strategy and finance at CRED and has worked alongside Shah since 2020, takes over as interim CEO.

## The Pattern

Shah's appointment follows a well-established but still remarkable pattern. Indian-origin executives now lead Alphabet, Microsoft, IBM, Adobe, Palo Alto Networks, Micron, FedEx, Arista Networks, and YouTube. Forbes's 2026 list of the 250 most successful living immigrants in the United States includes 26 of Indian origin.

But Shah's case is different. He is not an engineer who climbed a corporate ladder over two decades. He is a founder — someone who built a company, scaled it to profitability, and then was recruited to lead a platform that dwarfs anything he built, precisely because he built it.

## What It Means for the Diaspora

For NRIs, the appointment carries practical weight beyond symbolism. WhatsApp is the primary communication link between the diaspora and family in India — the app through which festival greetings are sent, medical updates are shared, and family group chats run perpetually. An Indian founder running it means the India use case is no longer a regional consideration in product decisions. It is the primary lens.

CRED's existing services also reach NRIs directly: the platform processes over 40 per cent of India's credit card bill payments. And Meta's investment signals that India's fintech ecosystem — long viewed by global investors as high-growth but high-risk — has matured enough to attract a $900 million bet from the world's largest social media company.

Shah, in his announcement, was characteristically direct: "The delta between WhatsApp today and its full potential is massive." The billions of users on the other side of that delta are about to find out what a CRED-founder's instincts look like at global scale."""

kunal_sources = json.dumps([
    {"name": "Livemint", "url": "https://www.livemint.com/companies/news/meta-s-4-5-billion-sandbox-what-s-at-stake-for-kunal-shah-whatsapp-and-cred-11750695696476.html"},
    {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/meta-cred-whatsapp/"},
    {"name": "The Indian Eye", "url": "https://theindianeye.com/cred-founder-kunal-shah-to-lead-whatsapp-globally/"},
    {"name": "PYMNTS", "url": "https://www.pymnts.com/meta/2026/meta-backs-indias-cred-and-hires-founder-to-run-whatsapp/"}
])


# ─────────────────────────────────────────────
# ASSEMBLE & INSERT
# ─────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Just Spent $4 Billion to Break Nvidia's Software Lock. It May Spend $10 Billion More.",
        "subheadline": "The Modular acquisition gives Qualcomm a CUDA rival. A Tenstorrent deal would give it an AI chip army. Meta and Microsoft are already signing up.",
        "slug": make_slug("qualcomm-modular-tenstorrent-nvidia-cuda-ai-data-center"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm is one of the largest H-1B employers of Indian engineers. Its AI pivot revalues mobile-computing skills overnight — and its Hyderabad, Bangalore, and Chennai R&D centres are central to the effort.",
        "tags": ["qualcomm", "nvidia", "ai-chips", "modular", "tenstorrent", "data-center", "indian-tech"],
        "urgency": "high",
        "sources": qualcomm_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Qualcomm_headquarters.jpg/1280px-Qualcomm_headquarters.jpg",
        "image_caption": "Qualcomm headquarters in San Diego, California",
        "image_attribution": "Wikimedia Commons",
        "body": qualcomm_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "CRED's Kunal Shah Is Now Running WhatsApp. Meta Paid $900 Million for That Handshake.",
        "subheadline": "The Indian founder who made credit card bills aspirational has been hired to monetise the world's largest messaging app. He'll do it from Bengaluru.",
        "slug": make_slug("kunal-shah-cred-whatsapp-ceo-meta-900-million"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "WhatsApp is the lifeline between NRIs and family in India. An Indian founder now runs the app that 500 million Indians use daily — and he's been hired to make it a commerce platform.",
        "tags": ["kunal-shah", "cred", "whatsapp", "meta", "indian-founders", "fintech"],
        "urgency": "high",
        "sources": kunal_sources,
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg/330px-Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
        "image_caption": "Kunal Shah, founder of CRED and new global CEO of WhatsApp",
        "image_attribution": "Wikimedia Commons",
        "body": kunal_body.strip()
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
