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
        "headline": "Blackstone's AirTrunk Just Committed $21 Billion to Build a Data Centre Near Mumbai. It Won't Be the Last.",
        "subheadline": "India's data centre market is attracting more than $630 billion in commitments from foreign tech giants this year alone. The AI infrastructure gold rush is reshaping Maharashtra's industrial belt — and NRI investment portfolios.",
        "slug": make_slug("airtrunk-21-billion-data-centre-maharashtra-india-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's data centre boom creates a new asset class for NRI investors. Blackstone, which already directs 40% of its $50B India portfolio to Maharashtra, is signalling that Indian digital infrastructure is now investable at sovereign-wealth scale. NRIs tracking Reliance, Adani, and Anant Raj should watch this sector closely.",
        "tags": ["data-center", "india-infrastructure", "blackstone", "airtrunk", "ai-infrastructure", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/airtrunk-invest-21-billion-india-data-centre-2026-06-01/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-anant-raj-invest-26-billion-haryana-data-centre-cloud-services-2026-06-01/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/sterling-wilson-sees-indian-data-centre-boom/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India's data centre market just received its largest single foreign commitment. AirTrunk, the Blackstone-backed Australian data centre operator, has signed a letter of intent to build a 3-gigawatt facility in Maharashtra's Raigad Penn Growth Centre, on the outskirts of Mumbai. The price tag: $21.05 billion.

The announcement, confirmed by Maharashtra's chief minister on X, is remarkable not for its ambition but for how unremarkable it has become. India is now fielding data centre investment proposals the way it once fielded textile factory bids — except each one costs more than a mid-sized country's annual GDP.

## The Numbers Behind the Rush

AirTrunk's Maharashtra play is part of a staggering wave. More than $630 billion in data centre investments are expected from US tech giants in India this year, lured by government tax breaks for foreign firms operating domestic facilities. Reliance and Adani have separately committed roughly $110 billion and $100 billion to AI and data infrastructure. Anant Raj, a New Delhi-based firm, signed a $2.6 billion memorandum of understanding with Haryana's government on the same day.

India's data centre market, valued at $5.55 billion in 2025, is projected to reach $13.11 billion by 2034 according to IMARC Group. The country's installed capacity is expected to leap from 12 gigawatts to 20 gigawatts by 2030. Sterling & Wilson, a data centre infrastructure builder, reported its order book hitting ₹1,770 crore in FY26, with a ₹1,900 crore target for FY27.

## Why Maharashtra

Blackstone is no stranger to Maharashtra. The private equity giant directs nearly 40 per cent of its $50 billion India investment portfolio to the state, with over $20 billion committed across Mumbai, Pune, and other cities. AirTrunk's choice of Raigad — close to Mumbai's financial infrastructure, submarine cable landing stations, and a deep talent pool — follows the logic that has made the state India's preferred data centre corridor.

AirTrunk already operates Asia-Pacific's largest data centre network, with facilities across Australia, Japan, Hong Kong, Malaysia, and Singapore. India will be its seventh market, and potentially its most consequential. As founder Robin Khuda put it at a Forbes conference last year: "This is the single-biggest gold rush in human history."

## The Power Question Nobody Wants to Answer

There is a catch. Even Blackstone CEO Stephen Schwarzman has warned that electricity supply could constrain data centre expansion globally. A 3-gigawatt facility in Maharashtra would consume more power than some Indian states generate. India's grid is improving, but renewable energy capacity, transmission infrastructure, and industrial-grade power reliability remain uneven outside the top metro corridors.

The government is betting that tax incentives and land allotments will attract both the capital and the infrastructure investment to close the gap simultaneously. Whether that bet pays off will determine if India becomes a genuine AI compute hub or merely a land-banking exercise for patient capital.

## What NRIs Should Watch

For Indian Americans tracking investment opportunities back home, data centre infrastructure is emerging as a distinct asset class. Anant Raj, Sterling & Wilson, and Adani Group's data centre subsidiaries all trade on Indian exchanges. Blackstone's own stock (BX) gives indirect exposure through AirTrunk and its QTS platform globally. The real question is whether India can solve the power equation before the capital gets impatient."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora Just Bought an AI Security Company Every Week for a Year. Tomorrow He Has to Show It All Works.",
        "subheadline": "Palo Alto Networks reports Q3 earnings on June 2 after completing five AI-related acquisitions in twelve months, including the $25 billion CyberArk deal. The Indian-origin CEO's bet: that AI agents will need security budgets bigger than the humans they replace.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-portkey-ai-security-earnings"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Nikesh Arora, born in Ghaziabad and a former Google and SoftBank executive, is now running the most consequential AI security strategy in enterprise tech. For Indian engineers in cybersecurity — one of the fastest-growing specialisations on H-1B petitions — Palo Alto's hiring and acquisition spree directly shapes career trajectories.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "ai-security", "indian-tech-leaders", "agentic-ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/palo-alto-networks-panw-completes-acquisition-of-ai-gateway-provider-portkey-1528773/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/palo-alto-reports-earnings-ai-security/"},
            {"name": "CRN", "url": "https://www.crn.com/news/security/2025/palo-alto-networks-aims-to-plant-the-flag-in-agentic-ai-with-cyberark-deal-ceo-nikesh-arora"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/palo-alto-networks-why-its-worth-buying-before-june-2"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "body": """On May 29, Palo Alto Networks quietly completed the acquisition of Portkey, an AI gateway provider that most people outside the cybersecurity industry have never heard of. It was the fifth AI-related acquisition Nikesh Arora has closed in the past twelve months. On June 2, when the company reports its fiscal Q3 earnings, the Ghaziabad-born CEO will need to demonstrate that this aggressive strategy is producing revenue, not just press releases.

## The Portkey Play

Portkey's technology acts as a central nervous system for AI agent traffic — monitoring, orchestrating, and governing autonomous AI systems that can independently execute tasks across enterprise networks. It processes trillions of tokens and provides real-time runtime protection. Palo Alto has folded it into its Prisma AIRS security platform, creating what the company calls a unified solution combining AI runtime security, agent identity verification, and deep observability.

The logic is straightforward, even if the execution is not. As businesses move from experimental chatbots to agents that can access private data, send emails, execute trades, and modify databases, each agent becomes a new attack surface. Prompt injection, unauthorized actions, data exfiltration, runaway costs — these are not theoretical risks. They are current ones.

## The CyberArk Anchor

The Portkey deal is the finishing touch on a much larger edifice. In February, Palo Alto completed its $25 billion acquisition of CyberArk, the identity security specialist whose Venafi division handles machine identity management. Arora's thesis is explicit: AI agents will soon outnumber humans on enterprise networks, and each one will need identity governance at least as rigorous as what companies apply to employees.

"CyberArk allows us the opportunity to plant the flag in the future market of agentic AI," Arora told analysts after the deal was announced. Combined with Portkey's gateway, Chronosphere's observability, and Idira's identity verification, Palo Alto now claims to offer the most comprehensive AI security stack in the industry.

## The Earnings Test

Wall Street expects adjusted earnings per share of 80 cents — flat with the year-ago quarter — on revenue of $2.9 billion, up 29 per cent. The acquisitions have driven strong top-line growth but compressed margins and diluted shares. Investors will scrutinise remaining performance obligations (RPOs) as a forward indicator of whether enterprise customers are actually buying the integrated platform or treating Palo Alto as yet another vendor in a crowded security stack.

The stock has been on a tear. Palo Alto shares surged 6.7 per cent on June 1 alone, pushing the market capitalisation past $230 billion. Over the past year, the stock has more than doubled from its 52-week low of $139.57. Channel checks from cybersecurity integrators suggest strong demand, but the Q3 report will reveal whether that demand is translating into the platform-level commitments Arora needs.

## The Diaspora Dimension

Arora's career arc — IIT BHU to Fidelity to T-Mobile to Google (where he was chief business officer under Pichai) to SoftBank to Palo Alto — is the kind of trajectory that has become almost routine among Indian-origin tech executives, yet remains extraordinary in scale. In March, he personally bought $10 million worth of Palo Alto stock, a vote of confidence that institutional investors noticed.

For Indian cybersecurity professionals, many of whom work at the company's Santa Clara headquarters or at its growing India engineering centres, the acquisition spree is reshaping career paths. AI security — encompassing agent identity, runtime protection, and prompt injection defence — is emerging as one of the most in-demand specialisations in enterprise tech. Palo Alto's bet is that it can own this category before anyone else assembles the pieces."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Deploying AI to Fight AI. The Cybersecurity Arms Race Just Arrived in New Delhi.",
        "subheadline": "A joint task force of MeitY, RBI, and the Finance Ministry is building an 'AI-against-AI' defence system for India's digital infrastructure, prompted by Anthropic's Claude Mythos model that can find zero-day vulnerabilities in decades-old code.",
        "slug": make_slug("india-ai-against-ai-cybersecurity-meity-rbi-claude-mythos"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's digital public infrastructure — UPI, Aadhaar, DigiLocker — handles billions of transactions that directly affect NRIs sending money home, accessing government services, or investing in Indian markets. A cybersecurity breach in this infrastructure would have immediate consequences for the diaspora's financial lives.",
        "tags": ["cybersecurity", "india-ai", "meity", "rbi", "anthropic", "claude-mythos", "digital-india", "upi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/govt-plans-ai-push-to-fortify-digital-infra-cybersecurity/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3928384-india-ascends-to-5th-place-in-global-digitalization-a-new-digital-powerhouse"},
            {"name": "Business Standard (via Communications Today)", "url": "https://www.communicationstoday.co.in/govt-plans-ai-push-to-fortify-digital-infra-cybersecurity/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5380603/pexels-photo-5380603.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India's government has decided that the only thing capable of defending its digital infrastructure against AI-powered cyberattacks is more AI. According to two finance ministry officials, the Ministry of Electronics and Information Technology (MeitY), the Reserve Bank of India, and the Finance Ministry are building a joint task force to deploy artificial intelligence as a defensive cybersecurity layer across India's critical digital systems.

"We have planned an AI-against-AI approach," one official told Business Standard.

The trigger, apparently, was Anthropic's Claude Mythos.

## The Mythos Problem

Claude Mythos, Anthropic's latest advanced generative AI model, has demonstrated the ability to locate dormant vulnerabilities hidden in decades-old code and exploit them. According to Anthropic, the model can identify and exploit zero-day vulnerabilities across major operating systems and web browsers when directed to do so. The company launched Project Glasswing in April, granting preview access to select organisations — Amazon Web Services, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorgan Chase, Microsoft, NVIDIA, and Palo Alto Networks among them — to use the model for defensive security work.

In its pilot phase, Anthropic said Mythos Preview had already uncovered thousands of high-severity vulnerabilities, including some affecting every major operating system and web browser.

For India, this is not an abstract concern. "Manual audits are not enough to fill all gaps," a second official said. "We need to deploy AI to scan the system for older dormant bugs."

## Why India Cannot Afford to Wait

India's digital public infrastructure is not a nice-to-have. UPI processes billions of transactions monthly. Aadhaar underpins welfare transfers for hundreds of millions of citizens. DigiLocker, ONDC, and the emerging digital rupee system are adding new layers of complexity — and new attack surfaces — every quarter.

A successful cyberattack on any of these systems would not merely be an IT incident. It would be a financial stability event affecting banks, merchants, and the hundreds of millions of Indians who have leapfrogged directly from cash to digital payments.

The officials stressed that India's infrastructure is not starting from zero. "Just a year ago, our IT infrastructure withstood countless cybersecurity attacks during Operation Sindoor," one official said, referencing the military operations that triggered coordinated cyber probes against Indian government systems.

## The Anthropic Connection

MeitY is now in direct contact with Anthropic and the US government to secure early access to Claude Mythos for defensive purposes. "We also need to verify whether the Mythos AI model is actually capable of what Anthropic claims," an official added — a dose of healthy scepticism that is warranted given the model's extraordinary claimed capabilities.

The broader worry, though, extends beyond any single model. Powerful AI systems are rapidly lowering the skill threshold for discovering and exploiting software vulnerabilities. What once required a team of experienced security researchers can now, at least in theory, be attempted by anyone with access to the right model and the right prompts. India's task force is being assembled with this acceleration in mind.

Finance Minister Nirmala Sitharaman convened a high-level meeting with bank heads in April to assess AI-related cybersecurity risks. Public sector banks have since committed to increasing IT infrastructure and cyber resilience spending.

## What This Means for NRIs

For Indian Americans who send money home through UPI-linked apps, invest through Indian brokerages, or access government services via Aadhaar-linked platforms, the security of India's digital infrastructure is directly personal. A breach in UPI's payment rails or Aadhaar's authentication system would affect cross-border remittances, portfolio access, and identity verification.

India's climb to fifth on the 2026 CHIPS-Combined global digitalization index — up from eighth — reflects both the scale of its digital ambitions and the expanding surface area that needs defending. The country now ranks as the world's fourth-largest digital services exporter, generating $328 billion in trade. That digital economy is only as durable as the security architecture protecting it.

The AI-against-AI approach is a pragmatic acknowledgement that the old playbook — manual code audits, periodic penetration testing, reactive patching — is no longer sufficient for a country running some of the world's largest real-time digital payment and identity systems. Whether India can build this capability fast enough to stay ahead of the threat is the question that keeps the task force working late."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
