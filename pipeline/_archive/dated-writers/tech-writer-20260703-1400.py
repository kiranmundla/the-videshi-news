#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-03 14:00 PT run
Two articles covering fresh angles across semiconductor and cybersecurity beats.
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


# ──────────────────────────────────────────────
# ARTICLE 1 — Custom AI Chip Arms Race
# Beat: Semiconductor Geopolitics / Global Tech
# ──────────────────────────────────────────────

article1_body = """The custom-chip arms race in artificial intelligence entered a new phase this week. Anthropic, the company behind the Claude AI models, is in early talks with Samsung Electronics to manufacture a bespoke processor on Samsung's cutting-edge 2-nanometer process, according to a report by The Information on Thursday. The move comes barely nine days after OpenAI unveiled "Jalapeño," a custom inference chip co-designed with Broadcom and set to be manufactured by TSMC later this year.

Two of the world's three most valuable AI companies are now actively building their own silicon. The third, Google, has been running its own Tensor Processing Units for the better part of a decade.

## Breaking Free from Nvidia

The push is not hard to understand. Nvidia commands roughly 80 per cent of the AI accelerator market, and that dominance has produced real bottlenecks. AI labs report multi-quarter waits for GPU allocations. Compute costs consume 60 to 70 per cent of some companies' operating budgets. When your largest expense is controlled by a single supplier, building an alternative is not ambition — it is insurance.

Anthropic's war chest makes the gamble feasible. The company raised $65 billion in its Series H round in May, reaching a valuation of $965 billion. Samsung, SK Hynix, and Micron all participated as investors, making Samsung simultaneously a shareholder and a potential manufacturing partner — an arrangement that aligns incentives neatly.

OpenAI's approach is further along. Jalapeño, its first custom inference ASIC, was taped out in a nine-month development cycle with Broadcom and is expected to go into production at TSMC in the third quarter. The chip targets inference workloads — the cheaper, higher-volume end of the AI compute stack — rather than the massive training runs that still require banks of Nvidia's H200 and Vera Rubin GPUs.

## Why Samsung?

Anthropic's reported interest in Samsung Foundry rather than TSMC is the more surprising detail. TSMC held a 70.4 per cent share of the global foundry market in the fourth quarter of 2025 and remains the default manufacturer for cutting-edge chips. Samsung's foundry business has struggled with yields on its most advanced nodes.

But there is logic to the bet. Samsung's 2nm process uses gate-all-around transistor architecture, a generational leap that promises better power efficiency. And when a single Taiwanese company makes seven out of every ten advanced chips on the planet, diversification has genuine strategic value — particularly for a company like Anthropic that has staked its identity on independence. The hire of Clive Chan, an early member of OpenAI's own chip team, signals that this is not a negotiating ploy leaked for leverage against Nvidia. It is an engineering buildout.

## What This Means for Indian Engineers

For the thousands of Indian semiconductor professionals working in chip design across the Bay Area, Austin, and Bengaluru, the custom-chip wave represents an unprecedented talent scramble. The AI labs' nascent silicon teams are actively recruiting from Broadcom, Qualcomm, AMD, and Nvidia itself. The binding constraint in every custom-chip programme is not capital or manufacturing capacity — it is people who know how to design a processor from scratch.

The trend intersects directly with India's semiconductor ambitions. Samsung is building assembly, test, and packaging capacity in India. The broader India Semiconductor Mission has approved eight major projects, including Tata Electronics' $14 billion mega-fab in Dholera, Gujarat. If the AI industry diversifies its manufacturing away from TSMC's concentration in Taiwan, India's emerging position in chip packaging and testing — the segment nearest to commercial readiness — becomes strategically more valuable.

## Not the End of Nvidia

Custom chips promise two to three times better performance-per-watt on specific workloads compared with general-purpose GPUs. But they carry enormous risk. A single tapeout at leading-edge nodes costs $300 to $500 million, and a failed design cannot easily pivot. Most AI companies will continue to need Nvidia's hardware for training, which remains the computationally heavier task.

For NRI investors holding Nvidia stock, the custom-chip wave is a long-term concern but not an immediate threat — the company's current-quarter revenue growth still exceeds 50 per cent. But the direction of travel is unmistakable: the biggest AI buyers are becoming their own chip designers, and the foundries willing to manufacture their silicon — whether in Hsinchu, Hwaseong, or eventually Dholera — will capture the next layer of value."""


# ──────────────────────────────────────────────
# ARTICLE 2 — RBI Flags AI Cyber Threat
# Beat: Cybersecurity / Indian Tech Ecosystem
# ──────────────────────────────────────────────

article2_body = """The Reserve Bank of India buried a significant warning in its biannual Financial Stability Report released this week. In a survey of the banking sector's cyber preparedness, AI-enabled attacks emerged as "the most important near-term challenge." The language was measured, the way central bank language always is. The implication was not.

India's digital payments infrastructure has scaled at a pace that makes most countries look glacial. UPI now handles 757 million transactions daily — a record set in June — and has gone live in ten countries, with Greece the latest addition. The Unified Payments Interface connects hundreds of banks and fintech applications, forming the rails on which India's consumer economy runs. It has also become a high-value target.

## What the RBI Found

The central bank's survey revealed that Indian banks have established "robust practices" in vulnerability assessment and penetration testing. Regulatory and board-level reporting of cyber incidents has matured. So far, so reassuring.

But two areas flagged as needing "further strengthening" tell a different story: employee cybersecurity awareness and forensic preparedness. Translated from central-bank-speak, India's banks can patch a known software vulnerability. They are less equipped to recognise a deepfake-assisted social engineering attack — or to preserve digital evidence after one succeeds.

## The AI Threat Vector

The RBI's concern centres on a new class of attack that exploits frontier AI capabilities. AI-generated phishing emails that mimic bank communications with unsettling accuracy. Deepfake voice and video used to impersonate executives and authorise fraudulent transactions. Adversarial AI tools that probe exposed systems faster than any manual triage can match.

Check Point Software's 2026 Exposure Gap Report, released this week, quantified the problem globally: critical vulnerability exposures more than doubled over the past year, while the window between a vulnerability's discovery and its exploitation has compressed from weeks to hours. "Automation and AI-assisted attack tools are reshaping both the scale and pace of exposure," the report noted.

The RBI's response is prescriptive. Banks must now deploy "advanced automated security stacks" capable of matching the speed of frontier AI models, including autonomous penetration testing platforms that run continuously without human intervention. API and digital-channel security — the plumbing behind UPI and third-party fintech integrations — has come under sharper supervisory scrutiny.

## Why NRIs Should Pay Attention

For the estimated 32 million non-resident Indians who maintain bank accounts in India — NRE, NRO, and FCNR deposits collectively hold well over $140 billion — the implications are direct. Cross-border transactions pass through multiple intermediaries, creating additional attack surfaces. International wire transfers and NRE account access, often managed through mobile apps from thousands of miles away, are precisely the kind of high-value targets that sophisticated attackers pursue.

The RBI's directive will funnel significant spending toward cybersecurity firms. Among the beneficiaries: Palo Alto Networks, led by Indian-origin CEO Nikesh Arora, which posted $3 billion in quarterly revenue last week and counts several Indian financial institutions among its clients. Indian cybersecurity startups are also positioned to ride the wave — firms like TAC Security, SAFE Security (formerly Lucideus), and CloudSEK are building AI-powered defence platforms tailored to Indian banking regulations.

## A Warning, Not a Verdict

The RBI also flagged a related concern: the AI-led stock market boom in some countries as a source of "financial fragility." Recent outperformance in some emerging markets has been driven by AI-linked companies rather than broad-based strength, the report noted, warning that sell-offs in these firms "could cause broader market declines in the US and cause spillovers to other markets through wealth effects."

The central bank's warning is not that Indian banks are failing. It is that the nature of the threat is changing faster than current defences can evolve. For NRIs, this means treating digital banking security as seriously as portfolio diversification: enabling two-factor authentication on every Indian account, monitoring NRE and NRO statements for irregular patterns, and recognising that even a well-crafted email or phone call from "your bank" might be something else entirely."""


# ──────────────────────────────────────────────
# Build article payloads
# ──────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Every AI Lab Wants Its Own Chip Now. The Race to Dethrone Nvidia Just Got Three-Way.",
        "subheadline": "Anthropic is in talks with Samsung to build a custom 2nm processor. OpenAI already taped out its inference chip with Broadcom. For Indian semiconductor engineers, the shift from buying GPUs to designing bespoke silicon opens a new frontier.",
        "slug": make_slug("ai-labs-custom-chip-race-anthropic-samsung-openai-broadcom"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian chip-design engineers are being heavily recruited by AI labs building custom silicon, and India's semiconductor mission benefits from the industry's push to diversify manufacturing away from TSMC.",
        "tags": ["semiconductors", "ai-chips", "anthropic", "openai", "samsung", "broadcom", "nvidia", "india-semiconductor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/02/anthropic-is-discussing-a-new-custom-chip-with-samsung/"},
            {"name": "The Information (via TalkMarkets)", "url": "https://talkmarkets.com/content/anthropic-is-building-its-own-ai-chip-and-samsung-could-make-it"},
            {"name": "Motley Fool (Broadcom custom chips)", "url": "https://www.fool.com/investing/2026/04/14/are-broadcoms-custom-ai-chips-the-key-to-future/"},
            {"name": "TrendForce (TSMC pricing)", "url": "https://www.trendforce.com/news/2026/05/27/tsmc-3nm-price-hike/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
        "image_caption": "Close-up of a semiconductor processor chip on a circuit board",
        "image_attribution": "Pexels",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Central Bank Just Called AI the Biggest Cyber Threat to Banking. Here's What That Means for Your Money.",
        "subheadline": "The RBI's latest Financial Stability Report flagged AI-enabled attacks as the most important near-term risk. With UPI processing 757 million transactions a day and NRI deposits exceeding $140 billion, the warning hits close to home.",
        "slug": make_slug("rbi-ai-cyber-threat-banking-nri-upi-security"),
        "category": "technology",
        "vertical": "cybersecurity",
        "diaspora_angle": "NRIs maintaining NRE/NRO/FCNR accounts in India face direct exposure as the RBI mandates banks upgrade to AI-speed defences against increasingly sophisticated cyber threats targeting cross-border transactions.",
        "tags": ["cybersecurity", "rbi", "ai-security", "upi", "nri-banking", "fintech", "digital-india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/ai-enabled-cyber-attacks-emerge-as-most-important-near-term-challenge-rbi"},
            {"name": "The420.in (RBI FSR analysis)", "url": "https://www.the420.in/rbi-flags-ai-enabled-cyber-attacks-as-top-near-term-threat-to-indian-banking-system/"},
            {"name": "Check Point Software (2026 Exposure Gap Report)", "url": "https://www.prnewswire.com/news-releases/check-point-exposure-gap-report-2026.html"},
            {"name": "Reuters (UPI record)", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg/1280px-General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg",
        "image_caption": "The Reserve Bank of India building in Kolkata",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
