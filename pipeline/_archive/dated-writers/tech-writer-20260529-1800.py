#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-29 18:00 UTC run"""
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

# ============================================================
# ARTICLE 1: Intel $3.3B Substrate Plant in Odisha
# ============================================================

art1_body = """India's semiconductor ambitions just cleared another milestone — and this time, it's Intel writing the cheque.

The U.S. chipmaker announced on Friday that it will invest approximately $3.3 billion alongside 3DGS Inc. USA to build a substrate manufacturing plant in the eastern state of Odisha. The facility, planned for the Bhubaneswar-Khurda region, will focus on advanced packaging glass core substrates, high-density interconnect substrates, and associated semiconductor technologies. Construction is expected to span five to six years.

The project will create more than 1,800 direct high-skilled jobs — a meaningful number in a state that has historically been overshadowed by Gujarat, Karnataka, and Tamil Nadu in the electronics manufacturing race.

## Why Substrates Matter More Than You Think

Substrates are the unsung heroes of the semiconductor supply chain. They are the bedrock material on which chip components are mounted and electrically connected. Without advanced substrates, even the most brilliantly designed processor is just an expensive paperweight.

The global substrate market has become a critical bottleneck in AI chip production. As chipmakers like Nvidia, AMD, and Intel push toward increasingly complex multi-die architectures — where several chiplets are stitched together in a single package — demand for high-density interconnect substrates has surged. Japan's Ibiden and Shinko Electric have historically dominated this market. India had zero presence until now.

Glass core substrates, which the Odisha plant will manufacture, represent the next generation of the technology. Unlike traditional organic substrates, glass cores offer superior dimensional stability, thinner profiles, and better electrical performance — characteristics that are essential for the advanced packaging technologies powering AI data centres.

## The Bigger Picture: India's Semiconductor Constellation

The Intel-3DGS announcement adds another node to India's rapidly expanding semiconductor map. Micron's $2.75 billion ATMP facility in Sanand, Gujarat, is in cleanroom validation and approaching partial operations. Tata Electronics, in partnership with Taiwan's PSMC, is running trial production at its Dholera mega-fab. CG Semi's OSAT facility in Sanand has already begun pilot operations. And ASML recently agreed to equip the Dholera fab with lithography tools.

New Delhi has pledged billions in subsidies through the India Semiconductor Mission, and the strategy is becoming clearer: India is not trying to compete with TSMC on leading-edge logic fabrication. Instead, it is building a full-stack ecosystem around mature-node manufacturing, memory packaging, and now advanced substrate production — the connective tissue of the global chip supply chain.

## What NRIs Should Watch

For Indian American semiconductor professionals, the Odisha plant represents a tangible return-to-India opportunity. Intel's semiconductor workforce in the U.S. includes thousands of Indian-origin engineers in packaging, materials science, and process engineering. The Bhubaneswar facility will need exactly these skill sets.

For NRI investors, the signal is equally clear. India's semiconductor sector is no longer a government PowerPoint deck. Between Micron, Tata, CG Semi, and now Intel, over $10 billion in committed capital is being deployed across six states. The supply chain ecosystem — from substrate materials to OSAT to fab — is taking physical shape.

The boy who was once rejected for a U.S. visa three times, Sanjay Mehrotra, now runs a trillion-dollar chip company that is investing in Gujarat. The country that produces the world's largest share of chip designers is finally building the factories to match. And Intel just bet $3.3 billion that Odisha deserves a seat at the table."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Intel Just Bet $3.3 Billion on Odisha. India's Chip Map Now Has Five Fabs.",
    "subheadline": "The substrate plant in Bhubaneswar will manufacture the advanced packaging materials that AI chips desperately need — and India had zero capacity to produce until now.",
    "slug": make_slug("intel-3dgs-odisha-substrate-plant-india-semiconductor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian American semiconductor engineers now have a direct return-to-India pathway at Intel's Odisha plant; NRI investors see over $10B in committed chip capital across six Indian states.",
    "tags": ["semiconductor", "intel", "india", "odisha", "advanced-packaging", "chip-manufacturing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/intel-3dgs-set-up-33-billion-substrate-plant-indias-odisha-state-2026-05-29/"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/india"},
        {"name": "India Semiconductor Mission", "url": "https://www.indiasmiconductormission.in/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body
}

# ============================================================
# ARTICLE 2: MediaTek Dual-Sources Intel + TSMC for Google AI Chips
# ============================================================

art2_body = """The most consequential chip supply chain decision of the year may have just been made in Taipei — and Sundar Pichai's Google is at the centre of it.

MediaTek, the Taiwanese chip designer that most people associate with budget smartphone processors, confirmed on Friday that it now supports both TSMC's CoWoS and Intel's EMIB advanced packaging technologies for its custom AI chip designs. The company is one of the few semiconductor designers in the world to qualify both packaging ecosystems simultaneously.

The subtext is louder than the announcement: Intel's EMIB packaging is being considered for custom AI chips that MediaTek is designing for Alphabet's Google, according to two people familiar with the matter. MediaTek has not publicly identified Google as a customer and declined to comment.

## The TSMC Bottleneck Problem

To understand why this matters, you need to understand the advanced packaging bottleneck. Every major AI chip — from Nvidia's Blackwell to Google's TPUs to Amazon's Trainium — requires advanced packaging to stitch multiple chiplets into a single high-performance module. TSMC's CoWoS (Chip-on-Wafer-on-Substrate) technology has been the industry standard, but its capacity is heavily allocated. Nvidia alone consumes an enormous share.

For Google, which designs its own Tensor Processing Units and has one of the most aggressive AI infrastructure buildouts in the industry, relying on a single packaging source is a vulnerability. MediaTek's ability to offer Intel's EMIB as an alternative gives Google a second lane on the highway.

EMIB — Embedded Multi-die Interconnect Bridge — takes a fundamentally different approach from CoWoS. Instead of placing chips on a large silicon interposer, EMIB embeds small bridge chips directly into the package substrate. Intel's technology reportedly enables larger package scalability (8-12x reticle size by 2027, compared to CoWoS's 3.3x), with improved yield and lower costs for certain inference-focused chip designs.

## Intel's Foundry Renaissance

This is also a pivotal moment for Intel. The company's foundry business has been fighting for credibility after years of manufacturing stumbles. Landing Google's AI chip packaging work through MediaTek would be a marquee win that validates Intel's advanced packaging capabilities against TSMC.

Intel's stock has already surged 230% this year, largely on the back of resurgent CPU demand from the AI inference boom. Its EMIB packaging technology gaining traction with hyperscale AI customers adds another growth vector that investors are only beginning to price in.

MediaTek itself doubled its 2026 data center revenue forecast to $2 billion and estimates the total addressable market for custom AI ASICs could reach $70-80 billion by 2027. The company is targeting a 10-15% share of that market.

## The Pichai Connection

For the Indian American tech community, the Google thread in this story is significant. Sundar Pichai's Alphabet is now the second-most valuable company on Earth, with a market cap exceeding $4.7 trillion. The decisions Google makes about its AI chip supply chain ripple through thousands of engineering jobs, billions in capital expenditure, and the competitive positioning of the AI infrastructure stack that Indian engineers at Google work on daily.

Google's TPU programme employs hundreds of Indian-origin engineers across design, verification, software, and deployment. A dual-source packaging strategy doesn't just de-risk supply — it creates opportunities for engineers who understand both ecosystems.

For NRI investors holding Alphabet stock, the takeaway is nuanced but positive: Google is not waiting in line behind Nvidia for TSMC's packaging capacity. It is actively building optionality — the kind of quiet, unglamorous supply chain work that separates companies that scale AI infrastructure from those that talk about it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Google Is Quietly Breaking Up With TSMC Exclusivity for Its AI Chips",
    "subheadline": "MediaTek confirmed it can build custom silicon using both TSMC and Intel packaging — and sources say Google's next-gen TPUs are the reason.",
    "slug": make_slug("google-mediatek-intel-emib-tsmc-cowos-ai-chips"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Sundar Pichai's Alphabet is diversifying its AI chip supply chain, affecting hundreds of Indian-origin TPU engineers at Google and signaling new career opportunities across both Intel and TSMC packaging ecosystems.",
    "tags": ["google", "mediatek", "intel", "tsmc", "ai-chips", "advanced-packaging", "sundar-pichai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/taiwans-mediatek-says-it-supports-both-tsmcs-intels-advanced-packaging-2026-05-29/"},
        {"name": "CryptoBriefing", "url": "https://cryptobriefing.com/mediatek-intel-chip-packaging/"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/chips"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17323801/pexels-photo-17323801.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body
}

# ============================================================
# ARTICLE 3: Nikesh Arora / Palo Alto Networks All-Time High
# ============================================================

art3_body = """Nikesh Arora bought $10 million of his own company's stock in late March, when Palo Alto Networks was trading at $147 a share. On Friday, the stock hit $277 — an all-time high — surging 7.4% in a single session. His March bet is now worth nearly $19 million.

The cybersecurity giant, which Arora has led since 2018, is having the kind of year that makes analysts recalibrate their models. The stock has nearly doubled from its 2026 low, the market capitalisation has crossed $209 billion, and Wedbush just raised its price target to $300.

All of this is happening while a rival, Zscaler, just cratered 32% after a dismal earnings report. Wall Street's verdict: Zscaler's problems are company-specific. The cybersecurity giants with the right AI strategy — Arora's Palo Alto chief among them — are in a different league entirely.

## The CyberArk Bet

The centrepiece of Arora's current strategy is the $25 billion acquisition of CyberArk, the identity security specialist. It is the largest M&A deal in cybersecurity history, and it is built on a single thesis: in the age of agentic AI, identity is the new perimeter.

"CyberArk allows us the opportunity to go ahead and plant the flag in the future market of agentic AI," Arora told analysts when the deal was announced. The logic is straightforward. As autonomous AI agents proliferate across enterprise systems — writing code, accessing databases, executing transactions — each agent needs identity credentials, privilege controls, and security monitoring. CyberArk's technology for managing machine identities, bolstered by its $1.5 billion acquisition of certificate authority Venafi, positions Palo Alto to secure this emerging attack surface.

The deal is expected to close by July 2026, and the company has guided for at least 37% adjusted free cash flow margins inclusive of CyberArk and its other recent acquisition, Chronosphere.

## The AI Catalyst

Wedbush analyst Dan Ives, who covers cybersecurity and is famously bullish on AI-driven growth, wrote this week that "AI will be the biggest growth catalyst for the cyber industry in the past 20 years rather than its demise." His field checks found that 8 out of 10 cybersecurity customers believe incumbent vendors with the right AI roadmap will win — not the AI-native startups trying to disrupt them.

Palo Alto's numbers support this thesis. In its most recent quarter (FQ2 2026), the company reported $2.59 billion in revenue, up 14.9% year-over-year, and non-GAAP EPS of $1.03, beating estimates by 9 cents. Next-generation security annual recurring revenue grew 29% to $5.9 billion. The fiscal Q3 report drops on June 2.

The company's AI-powered XSIAM platform (extended security intelligence and automation management), its SASE offering, and software firewalls are now driving the majority of incremental growth. Arora has guided toward a $15 billion ARR target by fiscal 2030 and 40%+ adjusted free cash flow margins by fiscal 2028.

## The Arora Arc

Nikesh Arora's journey reads like a case study in career reinvention. Born in Ghaziabad, Uttar Pradesh, he studied at IIT Varanasi before earning an MBA from Northeastern University in Boston. He rose to become Google's Chief Business Officer and then president of SoftBank before taking the helm at Palo Alto Networks.

When he arrived in 2018, Palo Alto was a respected but somewhat stodgy firewall company valued at roughly $20 billion. Under his leadership, it has transformed into a $209 billion platform company that spans cloud security, endpoint protection, AI-driven threat detection, and now identity security.

For Indian Americans working in cybersecurity — and there are tens of thousands across the Bay Area, the D.C. corridor, and enterprise security teams nationwide — Arora's ascent represents the broadening of the Indian-origin tech leadership narrative beyond software and semiconductors into the security infrastructure that underpins the entire digital economy.

## What Investors Should Watch

With earnings due Monday (June 2), the key metrics are next-generation security ARR growth (consensus expects continued 25%+ expansion), CyberArk integration timeline, and any update on the company's AI agent security roadmap. The stock is trading at a premium to its historical multiple, but in a sector where Zscaler's stumble just proved that execution quality determines everything, Arora's track record of beating estimates for eight consecutive quarters makes the premium look earned rather than speculative."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora's Palo Alto Networks Just Hit an All-Time High. He Bought $10 Million in Stock Two Months Ago.",
    "subheadline": "The IIT graduate turned cybersecurity CEO is betting that AI agents need identity security — and Wall Street is starting to agree, with the stock surging 7.4% in a single day.",
    "slug": make_slug("nikesh-arora-palo-alto-networks-all-time-high-cyberark"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "IIT Varanasi alumnus Nikesh Arora has transformed Palo Alto Networks into a $209B cybersecurity platform; tens of thousands of Indian Americans work in the cybersecurity sector that his company is reshaping.",
    "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "ai-security", "indian-tech-leaders", "agentic-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/palo-alto-crowdstrike-stocks-cybersecurity-zscaler-opportunity/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"},
        {"name": "CRN", "url": "https://www.crn.com/news/security/2025/palo-alto-networks-aims-to-plant-the-flag-in-agentic-ai-with-cyberark-deal-ceo-nikesh-arora"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "body": art3_body
}

# ============================================================
# PUBLISH
# ============================================================

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
