#!/usr/bin/env python3
"""Tech writer — 2 articles for July 14, 2026 AM run."""

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
# ARTICLE 1: MeitY Pushes Back on OpenAI/Anthropic
# ──────────────────────────────────────────────

article1_body = """India's IT ministry has quietly asked central government ministries to hold off on deploying AI models built by OpenAI and Anthropic for cybersecurity and related government functions. The directive, first reported by ThePrint and confirmed through an internal office memorandum, rejected a finance ministry proposal to use GPT-5.5 for vulnerability discovery — and it signals a deeper unease about who controls the AI tools that defend a nation's digital infrastructure.

## The Finance Ministry Wanted GPT-5.5. MeitY Said No.

The pushback began after representatives of both OpenAI and Anthropic approached several Indian government ministries with proposals to deploy their frontier models for cybersecurity use. The finance ministry was receptive. In a six-page letter titled *In light of LLMs being used: AI-based vulnerability discovery, AI-assisted cybersecurity capabilities and implementation*, it laid out a case for adopting GPT-5.5 to scan code, discover software flaws, and assist in incident response.

A department under MeitY rejected the proposal in a memorandum issued last week. The memo does not permanently bar the use of foreign AI models. Instead, it questions the timing and warns against premature deployment of systems whose risks have not been fully assessed.

## The Dual-Use Problem

The concern is not abstract. Advanced AI models that can identify vulnerabilities for defenders can also be weaponised by attackers. OpenAI and Anthropic have both acknowledged this dual-use risk and built safeguards around their most capable cyber-focused systems.

Anthropic's handling of Claude Mythos Preview illustrates the tension. The cybersecurity-focused model was initially restricted to about 50 organisations — Amazon, Google, Microsoft, Apple, NVIDIA, CrowdStrike, Palo Alto Networks and the UK's AI Security Institute — through a programme called Project Glasswing. By June 2026, access had expanded to roughly 150 organisations across more than 15 countries, including India.

But in the same month, Anthropic temporarily suspended access to its advanced models for foreign nationals to comply with US export controls. Access was restored within a day, but the episode laid bare a structural reality: access to frontier AI can be switched off by decisions made in Washington, not New Delhi.

## India's Sovereign AI Push Gets a New Argument

The directive gives fresh ammunition to advocates of India's sovereign AI programme. The Centre has committed ₹10,372 crore to the IndiaAI Mission, which funds subsidised GPU infrastructure, startup financing, and domestic foundation models. Sarvam AI, which raised $234 million in June at a $1.5 billion valuation, and the BharatGen consortium represent India's bet on building homegrown alternatives.

Union IT Minister Ashwini Vaishnaw recently called for an entirely new AI law, arguing that the Information Technology Act, drafted in the early 2000s, was never designed for a world where AI systems can autonomously discover zero-day exploits.

Finance Minister Nirmala Sitharaman added weight in April, warning financial institutions that AI could automate vulnerability discovery, enable malicious code interference, and make cyberattacks "faster and harder to detect."

"The tools of attack are evolving at high speed, and the tools of defence must evolve even faster," she said.

## Why This Matters to the Diaspora

For the roughly 300,000 Indian-origin professionals working across Silicon Valley and the broader US tech sector, this is not just a trade-policy story. Thousands of Indian-Americans work directly at OpenAI and Anthropic — building the very models that India's government is now waving off. The directive creates an uncomfortable dynamic where the technology built partly by Indian talent is being deemed too risky for India's own government infrastructure.

For NRI investors and founders eyeing India's AI market, the takeaway is clearer: India is not going to outsource its AI security stack. The domestic AI infrastructure play — compute, models, governance — is not a political talking point. It is becoming procurement policy.

The bigger question is whether India's homegrown models can match frontier capabilities in time to matter. Sarvam's 105-billion-parameter model is impressive for Indian languages, but cybersecurity requires a different kind of intelligence: reasoning about code, understanding exploit chains, and operating at the speed of machine-generated attacks. That gap will define whether the MeitY memo was prudent caution or a costly delay."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Quietly Tells Its Ministries to Hold Off on OpenAI and Anthropic for Cybersecurity Work",
    "subheadline": "A MeitY memo rejected a finance ministry proposal to deploy GPT-5.5 for vulnerability discovery. The directive raises hard questions about who controls the AI tools defending a nation's digital infrastructure.",
    "slug": make_slug("india-meity-openai-anthropic-cybersecurity-hold-off"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Thousands of Indian-Americans work at OpenAI and Anthropic, building the models India's government is now deeming too risky. The directive signals that India will build its own AI security stack — shaping procurement policy and creating opportunities for domestic AI companies that NRI investors and founders should watch.",
    "tags": ["ai-regulation", "cybersecurity", "india-ai", "openai", "anthropic", "sovereign-ai", "meity"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/buzz/meity-asks-ministries-to-hold-off-on-openai-anthropic-models-for-cybersecurity-report/"},
        {"name": "ThePrint", "url": "https://theprint.in"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/india-must-build-resilient-software-and-hardware-systems-to-withstand-cyber-threats-meity-secretary/article71215870.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
    "image_caption": "Union IT Minister Ashwini Vaishnaw has called for a new AI law to address frontier model risks",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 2: Indian AI Funding Surges 4X in H1 2026
# ──────────────────────────────────────────────

article2_body = """Indian AI startups raised $676 million across 57 deals in the first half of 2026 — a fourfold surge from the $162 million raised in the same period last year. The numbers, drawn from Inc42's newly released *Indian Tech Startup Funding Report, H1 2026*, mark the strongest six-month stretch ever for India's AI ecosystem. They also underline a stubborn reality: the gap with American AI companies is not shrinking. It is accelerating.

## The Surge in Context

The AI funding boom stands in stark contrast to the broader Indian startup landscape. Overall startup funding declined 9 percent year-on-year to $5.2 billion in H1 2026. Late-stage funding slumped 29 percent to $2.2 billion. Only five mega deals materialised across the entire ecosystem. Investors shifted toward smaller cheques spread across more companies — 501 deals, up 7 percent from last year.

AI bucked every one of those trends. Indian AI startups had raised roughly $1.8 billion cumulatively through all of 2025. In just the first half of 2026, the sector attracted nearly a third of that lifetime total in six months.

Sarvam AI, the Bengaluru-based sovereign AI company, accounted for the headline deal — a $234 million Series B round led by HCLTech's $150 million strategic investment, with Bessemer Venture Partners, Khosla Ventures, and Peak XV Partners also participating. The round valued Sarvam at $1.5 billion, making it India's second AI unicorn after Bhavish Aggarwal's Krutrim. Emergent, led by Mukund Jha, raised $70 million in the same window.

## Policy Tailwind, Not Just Hype

Unlike previous startup funding cycles in India, this one has a strong policy tailwind behind it. Roughly 66 percent of institutional investors surveyed in the Inc42 report said the IndiaAI Mission — approved with an outlay of ₹10,372 crore for subsidised compute, startup financing, and domestic foundation models — has influenced their AI investment thesis.

"The government is effectively lowering the cost of entry into AI," said Bhaskar Majumdar, founder of Unicorn India Ventures. Three structural shifts are driving confidence: hyperscalers like Microsoft, Google, and Amazon committing billions to build AI infrastructure in India; growing investment in sovereign compute and Indian-language foundation models; and enterprise AI adoption moving from pilots to production contracts.

Investors say the selectivity has also sharpened. Startups built as thin application layers on top of existing AI models are struggling to raise capital. The money is flowing to AI infrastructure, sovereign compute, vertical applications in banking and healthcare, and companies with proprietary data and recurring enterprise revenue.

## But the Global Gap Is Getting Wider

Here is the uncomfortable arithmetic. India's entire AI startup ecosystem raised $676 million in six months. In the same period, OpenAI closed a $112 billion round. Anthropic raised $65 billion in late May, pushing its valuation toward $965 billion. A single American AI company now raises more in one round than India's entire startup ecosystem has raised cumulatively — ever.

"What has been raised in India is still very minuscule compared to global AI investments," said Chetan Mehta, founding partner of AUM Ventures, which recently launched a ₹750 crore fund focused on frontier technologies. "The increase is encouraging, but we are still very early in this journey."

Mehta argued that deeper pools of domestic capital would help retain AI entrepreneurs who might otherwise relocate overseas in search of larger funding rounds and customer access. The flight of founders is not hypothetical — several Indian AI researchers have already moved to US-based labs offering compute budgets that dwarf anything available in India.

## What NRI Investors and Founders Should Watch

For the Indian diaspora, the numbers tell two stories. The optimistic one: India's AI ecosystem is no longer just talk. Real companies are raising real money, governments are backing them with real policy, and enterprise customers are paying for AI products. Sarvam's partnership with HCLTech gives it access to one of the world's largest enterprise client networks. That is a distribution advantage no American AI startup can match in the Indian market.

The cautious one: India is competing in a capital-intensive game where the US has a structural advantage in compute, talent, and venture scale. NRI investors — particularly those at firms like Khosla Ventures, Bessemer, and Lightspeed that already back Indian AI companies — are the connective tissue between these two ecosystems. Their capital allocation decisions over the next 12 months will shape whether India's AI surge is a blip or a breakout.

Investors increasingly expect M&A, not IPOs, to be the primary exit route for many Indian AI startups. Indian IT services giants — TCS, Infosys, HCLTech — are the obvious acquirers, as they race to add AI capabilities to their enterprise offerings.

"Gone are the days when you could just build wrappers on top of foundational models," Mehta said. "You have to build vertically focused products that solve real problems with an AI-first approach."

The money is moving in the right direction. Whether it is moving fast enough is the question India has not yet answered."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian AI Startups Raised $676 Million in Six Months. The Money Is Real, But the Gap With America Just Got Wider.",
    "subheadline": "AI funding surged 4X year-on-year in H1 2026, even as overall Indian startup funding declined 9 percent. Sarvam became India's second AI unicorn. It is still not close to enough.",
    "slug": make_slug("india-ai-startup-funding-676-million-h1-2026-gap"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors at Khosla Ventures, Bessemer, and Lightspeed are leading rounds in Indian AI startups. Their capital allocation decisions will shape whether India's AI surge becomes a breakout — and whether Indian-origin AI talent stays home or continues moving to US-based labs.",
    "tags": ["ai-funding", "india-ai", "sarvam-ai", "startup-ecosystem", "venture-capital", "sovereign-ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/features/indian-ai-startup-funding-soars-over-4x-yoy-in-h1-2026-but-is-it-enough-to-compete-globally/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion-2026-06-16/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Server racks in a modern data center powering the AI infrastructure buildout",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:80]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
