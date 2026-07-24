#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 14:00 PDT run"""
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

# ---------------------------------------------------------------------------
# ARTICLE 1: Qualcomm AI Acquisition Spree
# ---------------------------------------------------------------------------
art1_body = """Qualcomm is spending its way into the AI infrastructure business with a pair of acquisitions that, if both close, would total nearly $14 billion — a figure larger than the company's entire revenue from smartphone chips last quarter.

The confirmed deal is Modular, an AI software startup that Qualcomm agreed to buy last week in an all-stock transaction valued at roughly $4 billion. Modular builds a software layer that lets AI models run across different processors without requiring developers to rewrite code for each chip. In plainer terms, it is a direct challenge to CUDA, the programming platform that has made NVIDIA the default choice for virtually every AI developer on the planet.

"We believe the future belongs to developer-friendly, horizontal platforms that can run across diverse compute environments," Qualcomm CEO Cristiano Amon said in a statement announcing the deal.

The second acquisition, still under negotiation, is potentially more consequential. The Information reported that Qualcomm is in talks to acquire Tenstorrent, a Canadian AI chip startup led by legendary chip architect Jim Keller, for between $8 billion and $10 billion. Keller previously designed processors at Apple, Tesla, and AMD. Tenstorrent builds accelerators for training and running AI models based on the open-source RISC-V instruction set — a bet that the AI chip market need not be dominated by proprietary architectures.

## The Indian Engineering Backbone

For the roughly 20,000 Indian engineers who work at Qualcomm's San Diego headquarters and its Hyderabad and Bengaluru offices, the acquisitions signal a dramatic expansion in the kind of work available. Qualcomm has been one of the largest H-1B visa sponsors in the semiconductor industry for over a decade, and these deals shift its engineering centre of gravity from mobile phone modems toward AI infrastructure — a field where Indian talent is already concentrated.

Akash Palkhiwala, Qualcomm's Indian-origin Chief Financial Officer, has been the strategic architect of the company's AI pivot. At the company's recent investor day, he projected more than $15 billion in AI infrastructure revenue by fiscal 2029 — up from essentially nothing today. That projection now rests partly on whether Modular's software can pry developers away from NVIDIA's ecosystem and whether Tenstorrent's RISC-V chips can compete in data centres dominated by Arm and x86 architectures.

## What NRI Investors Should Watch

Qualcomm shares fell about 4% on the Modular announcement and dipped another 1% on the Tenstorrent report. Wall Street's concern is straightforward: paying $14 billion for two startups — one of which has raised only $380 million and another valued at roughly $2.6 billion in its last funding round — is a significant bet for a company whose revenue still depends overwhelmingly on smartphone chips.

But the strategic logic is compelling. If AI inference (running trained models, as opposed to training them) becomes the larger market — as many analysts now expect — then owning both the hardware (Tenstorrent's chips, Qualcomm's own Dragonfly processors) and the software (Modular's cross-platform layer) could position Qualcomm as the first credible alternative to NVIDIA's vertically integrated stack.

For Indian semiconductor professionals, whether in San Diego or Hyderabad, the message is clear: the next decade of chip careers will be shaped not by mobile phones, but by data centres.

*Sources: Reuters, The Information, Motley Fool, The Register*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Qualcomm Is Spending $14 Billion to Break NVIDIA's Grip on AI. Its Indian-Origin CFO Is the Architect.",
    "subheadline": "A $4 billion software deal and a potential $10 billion chip acquisition signal the most aggressive AI pivot in semiconductor history — with thousands of Indian engineers at the centre.",
    "slug": make_slug("qualcomm-14-billion-ai-modular-tenstorrent-palkhiwala"),
    "category": "technology",
    "vertical": "semiconductors",
    "diaspora_angle": "Qualcomm employs thousands of Indian engineers on H-1B visas and its Indian-origin CFO Akash Palkhiwala is architecting the company's $14B AI acquisition strategy — directly relevant to NRI semiconductor professionals and investors.",
    "tags": ["qualcomm", "nvidia", "semiconductors", "ai-chips", "indian-tech-leaders", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-buy-startup-modular-4-bln-ai-software-push-2026-06-24/"},
        {"name": "The Information (via Reuters)", "url": "https://www.reuters.com/technology/qualcomm-talks-buy-tenstorrent-information-reports-2026-06-16/"},
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/29/qualcomm-remaking-itself-ai-company-shares-cheap/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/16/qualcomm_tenstorrent/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Qualcomm_headquarters.jpg/1280px-Qualcomm_headquarters.jpg",
    "image_caption": "Qualcomm headquarters in San Diego, California",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ---------------------------------------------------------------------------
# ARTICLE 2: Microsoft Copilot Class Action
# ---------------------------------------------------------------------------
art2_body = """A securities fraud class action lawsuit filed against Microsoft alleges that the company misled investors about the performance and adoption of its AI products — a legal blow that arrives as Satya Nadella's AI-first strategy faces its most serious credibility test.

The complaint, filed in the U.S. District Court for the Western District of Washington, covers the period between May 2025 and January 28, 2026 — the date Microsoft's stock plummeted 10% in a single session. Multiple law firms, including Bleichmar Fonti & Auld and Levi & Korsinsky, are now competing for lead plaintiff status. The deadline to join the class is August 11.

The allegations are specific and damning. Plaintiffs claim Microsoft failed to disclose that its Copilot products suffered from "significant brand positioning, user experience, usage, data siloing, computational capacity, organizational, and interoperability problems." The complaint further alleges that Microsoft's flagship AI model "ranked well below competitors on a number of benchmark tests" and that the company needed to divert billions in capital expenditure — and GPU and CPU capacity — away from its profitable Azure cloud business to prop up Copilot's competitive position.

## The Gap Between Promise and Adoption

The lawsuit crystallises a concern that has been simmering in enterprise boardrooms: Microsoft charged ahead with Copilot pricing (up to $30 per user per month for Microsoft 365 Copilot) before the product delivered enough value to justify the cost. According to the complaint, "Microsoft had failed to convert a significant percentage of its commercial Microsoft 365 users to paid Copilot subscriptions," and its AI offerings "had lost market share to rival products, a trend that was increasing."

This is not an abstract accounting dispute. It cuts to the heart of whether the largest AI investment cycle in corporate history — Microsoft alone has committed over $80 billion in capital expenditure for the current fiscal year — is generating returns proportional to the spending.

## Why Indian Americans Should Pay Attention

Microsoft is arguably the most widely held individual stock among Indian American technology professionals. Employees receive restricted stock units as a core component of compensation. NRI investors, drawn by Nadella's transformation narrative and Microsoft's cloud dominance, have concentrated positions in MSFT across brokerage accounts, 401(k) plans, and IRAs.

The 10% stock drop on January 28 alone wiped out roughly $250 billion in market capitalisation — a figure larger than the GDP of Pakistan. For Indian employees holding unvested RSUs, the decline directly reduced their expected compensation. For NRI investors who bought during the AI-fuelled run-up, the lawsuit raises uncomfortable questions about whether the rally was built on disclosed reality or curated optimism.

Nadella himself has not been personally named as a defendant, but several senior executives have. The broader risk for Microsoft is less the lawsuit itself — securities class actions are common in corporate America — and more what the discovery process might reveal about the internal gap between Copilot's public narrative and its actual adoption metrics.

The irony is hard to miss: the Indian-born CEO who transformed Microsoft from a Windows company into a cloud-and-AI colossus now faces a legal challenge arguing that the AI leg of that transformation was overpromised.

*Sources: Reuters, Bleichmar Fonti & Auld, Levi & Korsinsky, Globe Newswire*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella's Microsoft Is Being Sued for Overhyping AI. Indian Investors Have the Most to Lose.",
    "subheadline": "A securities fraud class action alleges Microsoft misled investors about Copilot adoption and Azure AI performance. The stock has already dropped 10%.",
    "slug": make_slug("microsoft-copilot-class-action-nadella-nri-investors"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Microsoft under Indian-origin CEO Satya Nadella faces a securities fraud lawsuit over AI product claims — directly affecting NRI investors and Indian employees holding RSUs, who are among the most concentrated MSFT holders.",
    "tags": ["microsoft", "satya-nadella", "copilot", "ai-hype", "indian-tech-leaders", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bleichmar Fonti & Auld", "url": "https://www.bfalaw.com/cases/microsoft-class-action-lawsuit"},
        {"name": "Globe Newswire", "url": "https://www.globenewswire.com/news-release/2026/06/28/"},
        {"name": "ainvest.com", "url": "https://www.ainvest.com/news/microsoft-sued-over-ai-claims/"},
        {"name": "Levi & Korsinsky (via WCIA)", "url": "https://www.wcia.com/business/press-releases/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Microsoft CEO Satya Nadella at a company event",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ---------------------------------------------------------------------------
# ARTICLE 3: Delhi EV Policy
# ---------------------------------------------------------------------------
art3_body = """New Delhi just committed $1.59 billion over four years to electrify its roads — and the fine print includes a deadline that will force every motorcycle buyer in the capital to go electric by April 2028.

The policy, finalised on Monday, is India's most aggressive EV push to date. Car owners who scrap vehicles registered before April 2020 and replace them with an electric model will receive a cash incentive of ₹1 lakh (roughly $1,060). Buyers of battery electric cars priced under ₹30 lakh get full exemption from road tax and registration fees, which typically add 4% to 10% to the sticker price. Electric scooter buyers get ₹30,000 in the first year, tapering to ₹10,000 by year three.

The most radical provision: from April 1, 2028, Delhi will simply stop registering new petrol and diesel two-wheelers. No ban, no phase-out period — just a registration cutoff that makes internal combustion motorcycles effectively unsaleable in the capital.

Delhi will also install 32,000 new EV charging points across the city, addressing the infrastructure anxiety that has kept many buyers on the sidelines. Hybrids, notably, are excluded from the policy — a pointed signal to Toyota and Maruti Suzuki, which have lobbied hard for hybrid-inclusive incentives.

## Who Benefits

The policy is a direct tailwind for Tata Motors and Mahindra & Mahindra, which dominate India's electric car market. Tata's Nexon EV and Punch EV, both priced under ₹30 lakh, qualify for the full incentive stack. In the two-wheeler space, TVS Motor, Bajaj Auto, and Ather Energy stand to gain as Delhi's roughly 4 million scooter and motorcycle buyers are funnelled toward electric options.

Ola Electric, which once commanded half of India's e-scooter market, faces a more complex equation. The company has lost ground to legacy players with wider dealer networks, though its in-house 4680 Bharat Cell battery — manufactured at its Tamil Nadu Gigafactory — could give it a cost advantage as volumes scale.

## The China Factor

Meanwhile, a parallel shift is unfolding in how India sources its EV technology. Reuters reported this month that Tata Motors will use Chinese automaker Chery's carmaking platform to manufacture premium EVs in India. Both companies stressed the deal is a supply arrangement, not a technology transfer — a distinction that matters politically, given the freeze on Chinese business ties since the 2020 border clash.

But the reality is more nuanced. As one Indian government official told Reuters: "We are supportive of deals that lead to more local manufacturing or supply-chain shifts down the road." The subtext is pragmatic: India cannot build a competitive EV industry without Chinese battery chemistry and platform engineering, at least not yet.

## What NRIs Should Watch

For diaspora investors, the Delhi policy creates a clear dividing line in the Indian auto sector. Companies with strong EV portfolios — Tata Motors, Mahindra, TVS — are positioned for regulatory tailwinds, while those lagging on electrification face a shrinking addressable market in India's most prominent city.

The 2028 two-wheeler registration deadline is particularly significant. If other Indian states follow Delhi's lead — as they have historically done with emissions standards — the timeline for India's full EV transition could accelerate well beyond current market expectations. Tata Motors shares, already up more than 40% this year, may have further room to run.

For NRIs considering a return to India, the policy also has practical implications: the car you drive in Delhi is about to become a very different purchase decision.

*Sources: Reuters, Ola Electric shareholder communications, Tata Motors*"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Delhi Just Told 4 Million Motorcycle Owners to Go Electric. The Deadline Is 2028.",
    "subheadline": "India's capital commits $1.59 billion to its most aggressive EV policy yet — with cash incentives, a petrol two-wheeler ban, and a Chinese platform deal that complicates everything.",
    "slug": make_slug("delhi-ev-policy-1-59-billion-tata-ola-electric"),
    "category": "technology",
    "vertical": "clean-energy",
    "diaspora_angle": "Delhi's $1.59B EV policy directly impacts NRI investors holding Tata Motors, Mahindra, and Ola Electric stock, and reshapes the purchase calculus for anyone considering returning to India.",
    "tags": ["electric-vehicles", "delhi", "tata-motors", "ola-electric", "india-policy", "nri-investors", "clean-energy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/new-delhi-offers-residents-1000-scrap-old-cars-evs-curb-air-pollution-2026-06-29/"},
        {"name": "Reuters (China-India EV tech)", "url": "https://www.reuters.com/business/autos-transportation/chinese-ev-makers-are-shut-out-india-their-tech-isnt-2026-06-24/"},
        {"name": "Angel One (Ola Electric)", "url": "https://www.angelone.in/news/ola-electric-mobility-targets-full-transition-to-in-house-battery-cells"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4678065/pexels-photo-4678065.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An electric vehicle charging station with eco-friendly design",
    "image_attribution": "Pexels",
    "body": art3_body,
}

# ---------------------------------------------------------------------------
# INSERT ALL
# ---------------------------------------------------------------------------
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
