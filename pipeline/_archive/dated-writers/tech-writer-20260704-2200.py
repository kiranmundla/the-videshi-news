#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-04 22:00 PDT run"""

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


# ──────────────────────────────────────────────────
# ARTICLE 1: Tata Electronics Data Breach
# ──────────────────────────────────────────────────

article1_body = """India's government has opened a formal investigation into a ransomware attack on Tata Electronics that spilled confidential documents linked to Apple's unreleased iPhone 18 Pro, Tesla, Qualcomm, and TSMC onto the dark web. S. Krishnan, secretary at the Ministry of Electronics and Information Technology, confirmed the probe on Thursday — the first official acknowledgement from New Delhi that the breach had reached the highest levels of policy concern.

"We are investigating," Krishnan told reporters, adding that the incident had been reported to India's Computer Emergency Response Team, or CERT-In.

## What Leaked

The ransomware group World Leaks claims to have published more than 200,000 files — roughly 630 gigabytes — from Tata Electronics' systems. Cybersecurity researchers who reviewed portions of the dump say it includes component supplier lists, manufacturing specifications, internal communications, and photographs of iPhone 18 Pro models undergoing drop tests at a Tata plant, dated early 2026. Several files reportedly carry Apple's "confidential" watermark and internal code names consistent with the iPhone 18 Pro generation.

Documents referencing Tesla projects, Qualcomm chip designs, and TSMC process details were also found in the trove, though the full authenticity of the leaked material has not been independently verified. Apple has begun examining the matter. Neither Apple nor Tesla has commented publicly.

Tata Electronics says it detected the intrusion several weeks ago and activated its cybersecurity protocols. Operations, the company insists, remain unaffected. It has hired an unnamed global consultancy to conduct a forensic audit and has restricted internal access to sensitive systems.

## Why It Matters for India's Manufacturing Ambitions

The timing could hardly be worse. India is on track to assemble 26 per cent of the world's iPhones this year, up from just 6 per cent four years ago, according to Counterpoint Research. Foxconn's new Devanahalli plant near Bengaluru began commercial iPhone shipments in June, and Apple's CEO Tim Cook has confirmed that the majority of iPhones sold in the US for the June quarter were manufactured in India.

Tata Electronics sits at the heart of this transformation. The Tata group entered electronics manufacturing largely to position India as a credible alternative to China in Apple's supply chain — a bet that has attracted billions in investment, government subsidies under the Production Linked Incentive scheme, and enormous diplomatic goodwill. A breach that exposes pre-release product designs and proprietary supplier relationships strikes at precisely the trust that makes the partnership work.

## The Diaspora Angle

For Indian-origin engineers in Cupertino and across Silicon Valley, the breach is uncomfortably close to home. Many have spent careers inside Apple's famously secretive product development culture, where component details are compartmentalised and leaks trigger immediate supply chain audits. That a partner factory in India — one hand-picked to reduce dependence on China — could expose iPhone 18 Pro supplier lists and drop-test images before the device's expected September launch is the kind of incident that reverberates through procurement teams for years.

For NRI investors, the breach adds a risk premium to the otherwise compelling Make in India thesis. Tata group stocks, already a favourite among diaspora investors, now carry a new variable: whether India's electronics manufacturing ecosystem can protect the intellectual property of the world's most valuable company.

## What Happens Next

CERT-In's investigation will likely focus on how World Leaks gained access — whether through a supply chain vulnerability, phishing, or an unpatched system. The outcome matters beyond Tata. India's credibility as a manufacturing destination for global tech giants now rests, in part, on whether it can demonstrate that cybersecurity standards match the speed of its factory buildout.

Apple, for its part, faces a quieter reckoning. Its aggressive diversification away from China depends on trusting newer, less battle-tested partners with some of the most sensitive information in consumer technology. The Tata breach is the first major test of whether that trust can hold."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "A Ransomware Gang Just Leaked Apple's iPhone 18 Pro Secrets From a Tata Factory. India Is Investigating.",
    "subheadline": "The breach exposed supplier lists, component designs, and drop-test photos of unreleased iPhone models — threatening the trust at the heart of Apple's India manufacturing bet.",
    "slug": make_slug("tata-electronics-breach-apple-iphone-18-pro-india"),
    "category": "technology",
    "vertical": "cybersecurity",
    "diaspora_angle": "Indian-origin Apple engineers face supply chain trust fallout; NRI investors in Tata stocks now price in IP security risk as Make in India's credibility is tested.",
    "tags": ["cybersecurity", "apple", "tata", "make-in-india", "iphone", "supply-chain", "ransomware"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-investigating-tata-data-leak-that-exposed-apple-iphone-secrets-2026-07-03/"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/24/tata-electronics-hit-by-cyber-breach-involving-apple-and-tesla-data/"},
        {"name": "Reuters (supplier details)", "url": "https://www.reuters.com/business/media-telecom/apple-iphone-18-pro-supplier-list-parts-photos-exposed-tata-data-leak-2026-06-29/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Smartphone circuit boards in an electronics manufacturing facility",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────────
# ARTICLE 2: Nvidia's Revenue-Sharing AI Factory Model
# ──────────────────────────────────────────────────

article2_body = """Jensen Huang has spent the past three years selling GPUs to anyone who would buy them. Now Nvidia wants something extra: a slice of the revenue those GPUs generate.

The chipmaker unveiled a new business model this week that pairs hardware sales with revenue-sharing agreements, turning Nvidia from a one-time equipment vendor into something closer to a landlord who collects rent long after the keys are handed over. Chief Financial Officer Colette Kress announced the initiative in a blog post on Wednesday, calling it a way to build a recurring, "usage-linked earnings stream" while expanding access to AI infrastructure for startups and researchers who cannot afford to build their own.

## How It Works

Under the DSX AI Factories programme, Nvidia partners with cloud infrastructure providers who build and operate large-scale GPU clusters. These operators sell computing services to AI developers — model builders, inference providers, enterprise customers — and Nvidia takes a cut of the cloud revenue on top of its standard hardware sale. In exchange, Nvidia offers credit support and financing mechanisms that help partners commit to larger deployments without fronting the entire bill.

The first two launch partners illustrate the scale Nvidia is targeting. Sharon AI, an Australian firm, plans to deploy up to 40,000 Grace Blackwell GB300 GPUs. Firmus Technologies is building a data centre campus in Batam, Indonesia, designed to scale to 360 megawatts and accommodate up to 170,000 Nvidia GPUs. Other ecosystem partners already aligned with the DSX platform include CoreWeave, Crusoe, Lambda, Nebius, Nscale — and, notably, India's Yotta Data Services.

## The India Connection

Yotta's inclusion in Nvidia's launch roster is significant. The Hiranandani group-backed data centre operator runs India's largest hyperscale campus in Navi Mumbai and has been aggressively expanding capacity. Under Nvidia's new model, Indian AI startups — companies like Sarvam AI, which just became India's second AI unicorn after raising $234 million, or Krutrim, Ola's AI venture — could access Nvidia's most advanced hardware through Yotta without navigating the prohibitive economics of building their own GPU infrastructure.

Indian AI startup funding surged more than fourfold in the first half of 2026, reaching $676 million across 57 deals, according to Inc42. But compute access remains the single biggest bottleneck. Training and deploying large language models requires thousands of GPUs running continuously for weeks — hardware that most startups simply cannot purchase outright. Nvidia's revenue-sharing model offers a middle path: access now, payment proportional to usage later.

## What Nvidia Gets Out of It

The arrangement is not altruism. Nvidia posted 85 per cent year-over-year revenue growth in its most recent quarter (fiscal 2027 Q1, ended April) and its diluted earnings per share have risen roughly 2,800 per cent over three years. But the company faces a structural question: what happens when the initial infrastructure buildout slows?

Revenue-sharing provides a hedge. If demand for new GPUs plateaus — or if an AI bust materialises — Nvidia still earns recurring income from the hardware already deployed, provided utilisation stays high. It is a page from the enterprise software playbook: sell the platform, then clip the coupon on every transaction that runs through it.

The model also deepens Nvidia's lock-in. Once a cloud provider's revenue depends on Nvidia-powered infrastructure, switching to AMD or custom silicon becomes a decision that affects not just hardware procurement but the economics of an entire business relationship.

## Why Diaspora Engineers Should Pay Attention

For the thousands of Indian-origin engineers at AI companies across the Bay Area, Seattle, and Bengaluru, the shift is both strategic and personal. Many are building or advising startups that need GPU access at scale. A revenue-sharing model that includes Indian infrastructure partners lowers the barrier to building AI companies with Indian-resident teams and Indian compute — a practical accelerant for the growing trend of dual-geography AI ventures.

For NRI investors, the move reinforces why Nvidia's valuation — currently around $4.8 trillion — reflects a business model that is still expanding its surface area. The company is no longer just the arms dealer of the AI boom. It is positioning itself as the toll collector.

The question, as with all toll roads, is whether the traffic keeps flowing."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nvidia Doesn't Just Want to Sell You GPUs Anymore. It Wants a Cut of Your Revenue, Too.",
    "subheadline": "The chipmaker's new revenue-sharing model with AI cloud providers — including India's Yotta Data Services — creates a recurring income stream while lowering the barrier for cash-strapped AI startups.",
    "slug": make_slug("nvidia-revenue-sharing-ai-factory-model-yotta-india"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian AI startups gain access to Nvidia's top-tier GPUs through Yotta Data Services' inclusion in the DSX programme; NRI engineers building dual-geography AI ventures benefit from India-based compute at scale.",
    "tags": ["nvidia", "ai-infrastructure", "gpu", "yotta", "indian-startups", "revenue-sharing", "jensen-huang"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/blog/nvidia-unlocks-ai-compute-at-scale-capital-partners-to-power-ai-infrastructure-buildout/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/artificial-intelligence/nvidia-offers-revenue-sharing-model-for-aspiring-ai-startups"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/no-cash-for-gpus-nvidias-new-plan-lets-ai-startups-scale-anyway"},
        {"name": "TechGig", "url": "https://www.techgig.com/tech-news/nvidia-introduces-revenue-sharing-model-for-ai-startups-132014"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Nvidia CEO Jensen Huang, whose company is expanding from hardware sales into recurring AI cloud revenue",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
