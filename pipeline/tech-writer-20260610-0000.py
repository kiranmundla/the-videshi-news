#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 00:00 UTC run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# --- Env setup ---
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
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


# --- Image helpers ---
def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase article-images bucket."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ⚠ Not an image ({ct}): {img_url[:60]}")
            return img_url
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes)")
            return img_url
        compressed = compress_image(raw)
        print(f"  Image: {len(raw)} → {len(compressed)} bytes")

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        up_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(up_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            final = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded → {final[:80]}")
            return final
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:100]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url


# ============================================================
# ARTICLE 1: Anthropic Fable 5 + Indian IT
# ============================================================
art1_id = str(uuid.uuid4())
art1_slug = make_slug("anthropic-fable-5-mythos-class-indian-it-agent-security")

art1_body = """Anthropic dropped two announcements on Tuesday that, taken together, tell you exactly where the AI industry is headed. The company released Claude Fable 5 — the first "Mythos-class" model available to the general public — and upgraded its restricted Mythos model to version 5 for the roughly 200 organisations in its Project Glasswing cybersecurity programme. Both moves land less than a week after Anthropic filed confidentially for an IPO, with a private valuation of $965 billion.

Fable 5 is, by Anthropic's own account, the most capable model it has ever shipped publicly. It outperforms the Opus 4.8 tier on software engineering, analytics, and complex multi-step reasoning. But there is a catch: if a user queries Fable 5 about exploiting a software vulnerability, building a bioweapon, or anything else Anthropic deems high-risk, the model quietly downgrades the response to Opus 4.8. "We wanted to be able to provide this level of intelligence for general users in a safe manner," said Dianne Penn, Anthropic's head of product management.

The guardrailed approach is a calculated bet. Mythos Preview — the version without those guardrails — uncovered more than 10,000 high or critical-severity software vulnerabilities in its first weeks with Project Glasswing partners. That raw power is precisely why Anthropic has kept it locked to a vetted list that includes the U.S. government, Verizon, and Microsoft. The upgrade to Mythos 5 gives those partners more capability while the public gets the safety-filtered Fable 5.

## Indian IT Steps Into the Agentic Safety Business

The more consequential story for Indian tech professionals, however, is what is happening around these models. On the same day, Rubrik announced "Project Hourglass" — an alliance with global systems integrators to deliver its Agent Cloud platform for Claude Code and Claude Cowork to enterprise clients. The partner list reads like a Bengaluru roll call: Cognizant, HCLTech, Wipro, alongside Deloitte and NTT Data.

Rubrik's Agent Cloud tackles what is becoming the central anxiety of the agentic era: AI agents that write, deploy, and modify code autonomously, often faster than security teams can review. According to Rubrik Zero Labs, 86 per cent of cybersecurity leaders expect AI agents to outpace their organisation's security guardrails within the next year. The platform offers runtime security, behavioral guardrails, and the industry's only "Agent Rewind" capability to reverse unintended actions.

For Cognizant, HCLTech, and Wipro, this is a pivotal positioning play. These firms have spent years building practices around cloud migration, DevOps, and managed security. The agentic era gives them a natural next act: managing the blast radius of autonomous AI systems for the same Fortune 500 clients they already serve. At PegaWorld 2026, held the same week, Cognizant's CEO Ravi Kumar S. discussed the "AI Builder" approach to enterprise transformation, and the company won the Blueprint Pioneer Award for scaling more than 30 agentic deployments.

## What This Means for NRIs

For Indian engineers working at American companies that are adopting Claude Code and similar tools, the implications are immediate. AI agents are writing production code at firms like Stripe, where Fable 5 reportedly "compressed months of engineering into days." That is productivity manna. It is also a new class of risk — a single rogue commit from an unsupervised agent can cascade through a codebase before anyone notices.

The defensive side of that equation is where careers will be built. Indian cybersecurity firms and the Indian operations of global GSIs are likely to see rising demand for agentic governance skills. And with both Anthropic and OpenAI now racing toward IPOs — OpenAI filed its own confidential S-1 on Monday — the capital flowing into frontier AI will only accelerate the deployment of these systems.

Fable 5 is priced at $10 per million input tokens and $50 per million output tokens. It costs more than Opus 4.8 but uses fewer tokens per task, bringing the per-task cost down. For the growing army of Indian-origin developers building on Anthropic's API, the maths just got more interesting."""

print(f"\n📰 Article 1: Anthropic Fable 5")
art1_img_src = fetch_wikipedia_person_image("Dario Amodei")
art1_img = upload_to_supabase(art1_img_src, f"{art1_id}.jpg") if art1_img_src else ""


# ============================================================
# ARTICLE 2: UPI Global Expansion
# ============================================================
art2_id = str(uuid.uuid4())
art2_slug = make_slug("upi-cambodia-nepal-nine-countries-global-expansion")

art2_body = """India's Unified Payments Interface has quietly conquered a ninth country. On June 2, NPCI International Payments Limited and Cambodia's ACLEDA Bank announced that Indian travellers can now pay at over 4.5 million Cambodian merchants using UPI through the national KHQR code. Five days later, India and Nepal launched a UPI-NPI peer-to-peer linkage during Foreign Minister Jaishankar's meeting with his Nepali counterpart, enabling cross-border remittances between the two countries' payment rails.

The twin moves bring UPI's international footprint to nine nations — the UAE, Singapore, Bhutan, Nepal, Sri Lanka, France, Mauritius, Qatar, and now Cambodia — with Central Asian markets (Kazakhstan, Uzbekistan, Kyrgyzstan) next in the pipeline through a PayU–8B partnership. What started as a domestic QR-code revolution processing 21 billion transactions a month is becoming India's most successful technology export.

## From Domestic Tool to Global Infrastructure

The expansion strategy is methodical. Rather than asking foreign countries to adopt UPI wholesale, NPCI International links India's rails to each nation's existing payment system — Bakong in Cambodia, PayNow in Singapore, NPI in Nepal — creating bilateral bridges that preserve local sovereignty while enabling interoperability. India has also joined Project Nexus alongside Malaysia, the Philippines, Singapore, and Thailand, a multilateral framework for instant cross-border retail payments.

The Cambodia linkage is particularly telling. ACLEDA Bank, the country's largest commercial bank, gave UPI access to every merchant on the KHQR network in a single integration. "This collaboration not only strengthens real-time payment connectivity between our two ecosystems but also lays the groundwork for deeper tourism and commercial engagement," said Ritesh Shukla, NPCI International's CEO.

## What This Means for Indian Americans

For the Indian diaspora, each new UPI country is one fewer reason to fumble with foreign exchange. NRIs travelling to Southeast Asia, the Middle East, or France can now open their familiar PhonePe or Google Pay app and scan a QR code, with the rupee conversion handled instantly. No foreign bank account, no tourist SIM card, no cash.

The Nepal linkage has a deeper resonance. India-Nepal remittance corridors are among the busiest in South Asia, and the UPI-NPI bridge promises to reduce friction — and cost — for the millions of workers and families who move money across the border. The Kuwait-India corridor already records transaction costs of 2.1 per cent, well below the UN's 3 per cent benchmark, but many other corridors still face bloated chains of intermediaries and inflated fees.

For NRI investors, UPI's international expansion is quietly building the revenue base for the fintech ecosystem they are already betting on. Every cross-border transaction that flows through NPCI's rails strengthens the case for PhonePe's reported IPO ambitions and for the broader ecosystem of payment processors, neo-banks, and remittance platforms that sit on top of India's digital public infrastructure.

## The Bigger Game

UPI's global push is inseparable from India's broader Digital Public Infrastructure diplomacy. Aadhaar, DigiLocker, and UPI together form a stack that India is now actively exporting — offering developing countries a proven alternative to building payments infrastructure from scratch. More than 30 million Indians are expected to travel abroad by 2026, contributing $20-25 billion in tourism spending. Every one of those travellers is now a walking advertisement for Indian fintech.

The technology is free. The standards are open. The lock-in is cultural: once an Indian traveller gets accustomed to paying abroad with the same app they use to split a dinner bill in Bengaluru, the switching cost becomes zero — and the network effect becomes India's moat."""

print(f"\n📰 Article 2: UPI Global Expansion")
# UPI is not a person article, use Pexels
art2_pexels = "https://images.pexels.com/photos/6205512/pexels-photo-6205512.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_img = upload_to_supabase(art2_pexels, f"{art2_id}.jpg")


# ============================================================
# ARTICLE 3: Sridhar Ramaswamy / Snowflake
# ============================================================
art3_id = str(uuid.uuid4())
art3_slug = make_slug("sridhar-ramaswamy-snowflake-agentic-enterprise-revenue")

art3_body = """Sridhar Ramaswamy has a $1.39 billion quarter and a warning for the software industry. The Indian-origin CEO of Snowflake delivered a 33 per cent revenue increase year-over-year and committed $6 billion to Amazon Web Services for Graviton compute and AI capacity — then promptly cautioned that the "SAASpocalypse" may not be over.

"We spend a lot of time thinking about what durable value is," Ramaswamy told attendees at Snowflake Summit 2026 in San Francisco, where he shared the stage with Anthropic co-founder Daniela Amodei. His point was precise: when agentic AI drives the marginal cost of building software toward zero, the pricing models that have sustained enterprise SaaS for two decades will shatter. Companies that cannot articulate why their product is worth paying for in an age of autonomous code-writing agents will be the first casualties.

## The Agentic Enterprise Takes Shape

Ramaswamy laid out Snowflake's answer in four building blocks: enterprise data as the immovable foundation, frontier AI models (Claude, GPT, Gemini) as the reasoning layer, existing applications (Salesforce, SAP, Zoom) as the action surface, and an agentic control plane — Snowflake's contribution — as mission control.

The product announcements backed the thesis. Snowflake Intelligence, a personal AI work agent, operates across tools in natural language. Cortex Code, rebranded to CoCo, is a coding agent that has already reached 7,100 customer accounts and, internally at Snowflake, doubled developer throughput while recovering the equivalent of 90 full-time employees in the sales organisation. The rebranded CoWork platform hit 5,000 accounts in Q1 FY27, doubling quarter-over-quarter.

Thomson Reuters reported a 3.4x workload improvement using CoCo. Internally, Snowflake deployed more than 100 automated workflows across finance, HR, marketing, and sales — eating its own cooking with demonstrable efficiency gains. Remaining performance obligations stood at $9.21 billion, with 779 customers generating more than $1 million in trailing 12-month product revenue.

## An Indian-Origin CEO With an Uncomfortable Message

Ramaswamy's trajectory mirrors a pattern familiar to the Indian diaspora. Born in India, he spent 15 years at Google rising to head its advertising business before joining Neeva, the privacy-focused search startup he founded, which Snowflake acquired in 2023 to bring him aboard as CEO.

His warning about durable value lands hardest in the Indian IT services sector. If agentic AI can compress transformation timelines from months to days — Cognizant won an award at PegaWorld 2026 for doing exactly that — then the labour-arbitrage model that built TCS, Infosys, and Wipro into global giants faces an existential question. TCS chairman N. Chandrasekaran said last week that AI agents could match his company's 500,000-strong headcount; Ramaswamy is describing the demand-side corollary. When the software itself costs less to build, every layer of the value chain gets repriced.

For NRI investors, Snowflake's numbers offer a real-time gauge of agentic AI adoption. The company's consumption-based pricing model means revenue tracks directly with how much compute enterprises are actually burning on AI workloads — not seats or licenses or promissory contracts. A 33 per cent growth rate says adoption is accelerating. The $6 billion AWS commitment says management believes it will keep accelerating.

## The Indian Engineer's Calculation

The Indian diaspora has an outsized stake in how the agentic enterprise plays out. Indian-origin engineers at Google, Microsoft, and Salesforce are among the first to integrate these tools into production workflows. Indian IT services firms will either become the orchestrators of agentic deployments — managing governance, safety, and rollback — or watch their margins compress as AI agents replace the billable hours they sell.

Ramaswamy is betting that the answer is data. Models come and go; enterprise data compounds. The CEO who built Google's ad business on the insight that data is the moat is now telling the world that the same logic applies to AI agents. For the 50,000-odd Indian-origin employees at companies building on Snowflake's platform, that bet is also a career thesis."""

print(f"\n📰 Article 3: Sridhar Ramaswamy / Snowflake")
art3_img_src = fetch_wikipedia_person_image("Sridhar Ramaswamy")
art3_img = upload_to_supabase(art3_img_src, f"{art3_id}.jpg") if art3_img_src else ""


# ============================================================
# INSERT ALL ARTICLES
# ============================================================
articles = [
    {
        "id": art1_id,
        "headline": "Anthropic Just Released Its Most Powerful Public Model. Indian IT Giants Are Already Building the Safety Net.",
        "subheadline": "Claude Fable 5 brings Mythos-class intelligence to the masses with cybersecurity guardrails. Cognizant, HCLTech, and Wipro are rushing to secure the agentic code it writes.",
        "slug": art1_slug,
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian IT services firms (Cognizant, HCLTech, Wipro) are positioning themselves as the security layer for enterprise AI agents. Indian-origin engineers at companies adopting Claude Code face both productivity gains and new governance demands.",
        "tags": ["anthropic", "claude", "fable-5", "ai-agents", "cybersecurity", "cognizant", "hcltech", "wipro", "ipo"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/anthropic-rolls-out-public-version-mythos-without-cybersecurity-capability-2026-06-09/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/anthropic-releases-new-mythos-class-model-to-general-public-with-guardrails-2026-06-09"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/anthropic-mythos-rollout-fable-5-2026-06-09"},
            {"name": "Rubrik via BusinessWire", "url": "https://www.businesswire.com/news/home/rubrik-gsi-agent-cloud-claude-code-project-hourglass"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": art1_img,
        "image_caption": "Dario Amodei, CEO of Anthropic, at TechCrunch Disrupt 2023",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": art2_id,
        "headline": "India's UPI Just Landed in Cambodia. That Makes Nine Countries and Counting.",
        "subheadline": "A Nepal cross-border linkage and 4.5 million Cambodian merchants in one week. India's most successful technology export is building a payment empire without anyone noticing.",
        "slug": art2_slug,
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "NRI travellers can now pay with their Indian apps in nine countries. The Nepal linkage directly reduces remittance costs for one of South Asia's busiest corridors. UPI's global expansion strengthens the fintech ecosystem NRIs are invested in.",
        "tags": ["upi", "digital-payments", "npci", "cambodia", "nepal", "fintech", "digital-public-infrastructure", "nri-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CoinGeek", "url": "https://coingeek.com/indias-upi-expands-to-cambodia-digital-health-ids-hit-900m/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/india-nepal-launch-upinpi-crossborder-payment-linkage"},
            {"name": "WhalesBook", "url": "https://whalesbook.com/article/upi-goes-global-why-indias-payment-expansion-matters"},
            {"name": "Policy Circle", "url": "https://www.policycircle.org/economy/upi-global-expansion/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": art2_img,
        "image_caption": "A customer scans a QR code for digital payment at a merchant terminal",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
    {
        "id": art3_id,
        "headline": "Sridhar Ramaswamy's Snowflake Just Posted $1.39 Billion in Revenue. His Warning for Indian IT Is Sharper.",
        "subheadline": "The Indian-origin CEO says the SAASpocalypse is not over. With 7,100 accounts on his AI coding agent and a $6 billion AWS bet, he may be right.",
        "slug": art3_slug,
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian-origin CEO leading a major cloud company. His warning about durable value directly threatens the labour-arbitrage model of Indian IT services. Indian engineers at Snowflake customers are early adopters of agentic workflows.",
        "tags": ["snowflake", "sridhar-ramaswamy", "agentic-ai", "saas", "indian-ceo", "cloud", "enterprise-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Forbes", "url": "https://www.forbes.com/sites/alexkonrad/snowflake-ceo-ramaswamy-saaspocalypse-agentic-ai/"},
            {"name": "Let's Data Science", "url": "https://letsdatascience.com/snowflake-ceo-risks-agentic-ai-saaspocalypse/"},
            {"name": "LinkedIn / Debasis Paul", "url": "https://www.linkedin.com/pulse/agentic-enterprise-snowflake-summit-2026/"},
            {"name": "Morningstar / BusinessWire", "url": "https://www.morningstar.com/news/business-wire/snowflake-summit-26-anthropic-daniela-amodei"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": art3_img,
        "image_caption": "Sridhar Ramaswamy, CEO of Snowflake, at a technology conference",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body,
    },
]

print("\n🚀 Inserting articles...\n")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n✅ Done — {len(articles)} articles submitted for review")
