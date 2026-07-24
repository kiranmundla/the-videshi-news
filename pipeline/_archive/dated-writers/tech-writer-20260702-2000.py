#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 20:00 PT run"""

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
        "headline": "Concentrix Lost a Quarter of Its Value This Week. India's Call Centre Industry Is Next.",
        "subheadline": "The American outsourcing giant's stock crashed 24% after it warned that AI is eating into its business. With 1.65 million BPO workers in India, the shockwave is heading east.",
        "slug": make_slug("concentrix-crash-ai-bpo-india-call-centre"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian BPO workers face the sharpest edge of AI displacement, and NRI investors holding IT services stocks should reassess exposure to the outsourcing sector.",
        "tags": ["ai", "bpo", "concentrix", "outsourcing", "indian-it", "jobs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/concentrix-stock-plunge-ai-teleperformance"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/meet-ai-chatbots-replacing-indias-call-center-workers-2025-10/"},
            {"name": "Hedgeweek", "url": "https://www.hedgeweek.com/hedge-funds-up-call-centre-shorts-amid-ai-disruption-fears/"},
            {"name": "Nearshore Americas", "url": "https://nearshoreamericas.com/gen-ai-hits-india-cx-industry/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7035859/pexels-photo-7035859.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Customer service workers at a call centre workstation with headsets",
        "image_attribution": "Pexels",
        "body": """Concentrix, one of the world's largest customer experience companies, lost roughly a quarter of its market value this week after posting second-quarter results that Wall Street found deeply unimpressive — and issuing guidance that was worse.

The numbers were not catastrophic in isolation. Revenue of $2.46 billion was up 1.9% year-on-year. Adjusted earnings came in at $2.63 per share, a penny below estimates. But the guidance rattled investors: third-quarter earnings of $2.65 to $2.77 per share, against a consensus of $3.08. Full-year revenue of $9.93 to $10.03 billion, below the $10.11 billion analysts had pencilled in.

Shares fell 24% in a single session. Peer Teleperformance, the French outsourcing giant, dropped 11.5% in sympathy. Concentrix is now down 52% over the past twelve months and 39% year-to-date. Hedge funds have been increasing short positions against the entire call centre sector, according to Hedgeweek, treating it as a consensus "AI loser" trade.

## The India Question

For Indian professionals, this is not an abstract market story. India's business process management sector employs 1.65 million workers across call centres, payroll operations, and data-handling services. Concentrix alone operates multiple facilities in Bengaluru, Noida, Mumbai, and Hyderabad, with thousands of Indian employees handling customer service for some of the world's largest brands.

The displacement is already underway. Zomato laid off 600 customer support executives earlier this year, barely six months after hiring them, after deploying its AI platform Nugget — which now handles over 15 million customer interactions monthly and resolves up to 80% of queries autonomously. A former head of a customer experience vendor serving Airtel told Reuters that his team shrank from 15,000 agents to fewer than 4,000 after agentic AI arrived. "The first layer has almost vanished," a quality assurance manager at a Bangalore contact centre told Nearshore Americas.

Net headcount growth in India's BPM segment — which represents roughly one-fifth of the country's IT output — has cratered from 177,000 new workers in 2021-22 to fewer than 17,000 in each of the past two years, according to data from TeamLease Digital.

## The Structural Shift

What makes this moment different from previous waves of automation is the speed. Generative AI and agentic systems are not merely augmenting call centre workers — they are replacing entire tiers of the workforce. The conversational AI market is growing at 24% annually and is expected to reach $41 billion by 2030.

The irony is sharp. India's IT services sector — which represents 7.5% of GDP — was built on the proposition that skilled English-speaking workers could deliver services more cheaply than Western alternatives. AI undercuts that proposition at its foundation. The cost advantage that brought millions of jobs to Bengaluru and Hyderabad is being eroded by software that works around the clock, in every language, for a fraction of the cost.

Some analysts argue the sell-off is overdone. Emmanuel Cau, head of European equity strategy at Barclays, has said the sector has been categorised too broadly as an AI casualty, and that companies successfully integrating AI into their service offerings may yet find higher-margin business models. But the transition period — where old revenue declines faster than new revenue materialises — is precisely the danger zone.

## What NRIs Should Watch

For Indian Americans working in or invested in the IT services ecosystem, the Concentrix crash is a leading indicator. India's tier-1 IT giants — TCS, Infosys, Wipro, HCL Tech — are already grappling with what JP Morgan calls "AI deflation," where productivity gains reduce billable hours faster than new AI-related spending grows. The Nifty IT index has corrected 33% from its February peak.

The difference is that the large IT firms have diversified revenue streams, strong balance sheets, and the resources to pivot. Companies further down the value chain — the mid-tier BPO operators, the voice process vendors, the back-office service providers — have less runway. Entry-level roles, the traditional gateway for millions of young Indians into the formal economy, are disappearing fastest.

Prime Minister Modi has argued that "work does not disappear due to technology — its nature changes." That may prove true over a generation. In the near term, the nature of the change looks a lot like subtraction."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ShareChat Just Turned Profitable. Now It Wants $400 Million From Public Markets.",
        "subheadline": "India's homegrown social media platform, once burning through venture cash, has hit operational profitability and plans an IPO within five quarters. The secret weapon: 700 million micro-drama episodes watched daily.",
        "slug": make_slug("sharechat-ipo-400-million-profitable-micro-drama"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "ShareChat's IPO gives NRI investors a rare chance to bet on an Indian-built social platform competing directly with Meta and YouTube in the vernacular content space.",
        "tags": ["sharechat", "ipo", "indian-startup", "social-media", "micro-drama", "mohalla-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bloomberg via The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/sharechat-eyes-400-million-ipo-next-year-after-turning-operationally-profitable/article69753000.ece"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/sharechat-eyes-up-to-400-mn-ipo-in-fy28/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/sharechat-eyes-400-million-ipo-after-turning-operationally-profitable"},
            {"name": "BestMediaInfo", "url": "https://www.bestmediainfo.com/digital/sharechat-targets-up-to-400-million-ipo-next-year"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8204031/pexels-photo-8204031.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A person holding a smartphone displaying various mobile applications in India",
        "image_attribution": "Pexels",
        "body": """Mohalla Tech, the parent company of ShareChat, Moj, and QuickTV, is planning to raise up to $400 million through an initial public offering targeted over the next four to five quarters. The announcement, first reported by Bloomberg, comes after the company turned operationally profitable in the first quarter of FY27 — a milestone that would have seemed improbable two years ago, when the company was haemorrhaging cash and laying off staff.

"Our unit economics has now turned positive," Chief Financial Officer Manohar Charan told Bloomberg. "We will aim to list over the next four or five quarters."

## From Cash Burn to Cash Flow

ShareChat's turnaround has been surgical. After the venture funding boom of 2021-22 evaporated, the company spent the next two years cutting costs, shedding employees, killing unprofitable products, and reworking its business model from the ground up. Cash burn fell from ₹800 crore in FY24 to ₹219 crore in FY25, and has continued declining since.

Annual revenue has crossed ₹1,000 crore ($105 million) and is currently running at an annualised pace of up to ₹1,400 crore, with growth exceeding 30%. The company has posted nine consecutive months of positive cash flow. Together, ShareChat and Moj serve about 150 million monthly active users, primarily in India's smaller towns and cities through regional language content — exactly the demographic that Meta and YouTube have struggled to monetise effectively.

But the real story is micro-dramas.

## The QuickTV Bet

QuickTV, ShareChat's subscription-based micro-drama platform, has emerged as the unlikely engine of the company's revival. Micro-dramas — serialised stories told in episodes as short as 60 seconds — have become one of India's fastest-growing forms of digital entertainment. The format, which originated in China with platforms like ShortTV and ReelShort, has found fertile ground in India's massive mobile-first audience.

ShareChat estimates its platforms currently serve about 65 million monthly micro-drama viewers, roughly two-thirds of India's total audience for the format. Users are watching more than 700 million micro-drama episodes every day. The global micro-drama market is projected to grow at a compound annual growth rate of 31% to $4.5 billion by 2030, according to venture fund Lumikai.

What makes micro-dramas attractive as a business is the subscription model. Unlike advertising-dependent short video, which requires enormous scale before it generates meaningful revenue, subscription content converts viewers into paying users with predictable, recurring revenue. QuickTV now has around 3 million subscribers.

## The AI Edge

ShareChat is also betting on artificial intelligence across its platforms — for content recommendations, moderation, advertising targeting, and increasingly, content creation itself. The company plans to expand its in-house generative AI studio, and CFO Charan expects AI to improve margins by 5% to 7% over the next two years.

This is a meaningful competitive advantage. Indian social platforms have historically struggled against Meta's resources and Google's distribution. But AI-driven efficiency in content operations — moderating in 15 Indian languages, personalising feeds for wildly diverse audiences, automating ad targeting for small-town advertisers — is an area where local knowledge and language expertise matter as much as raw compute.

## What It Means for NRIs

For Indian Americans watching India's tech ecosystem, ShareChat's IPO would be notable for what it represents: a homegrown social media platform, built for vernacular India, competing against Meta and YouTube — and winning enough to go public.

The investor roster reads like a who's who of global venture: Lightspeed, Tiger Global, Snap, Google, and Twitter (pre-Musk). A successful listing would add to a growing pipeline of Indian consumer internet IPOs — following Zomato, Paytm, and Nykaa — and offer NRI investors direct exposure to India's digital entertainment economy.

The risks are real. ShareChat still operates in a brutally competitive market. Meta's Instagram Reels, YouTube Shorts, and the persistent spectre of TikTok's return to India all threaten the short-video business. The IPO plans are explicitly described as "not final and could change." And India's IPO market has been unkind to recent tech listings — Paytm's post-IPO collapse remains a cautionary tale.

But the fundamentals have shifted. Revenue is growing at 30%-plus. The company is operationally profitable. And the micro-drama format has given it a revenue stream that Meta cannot easily replicate.

If ShareChat manages to list successfully at a reasonable valuation, it would be that rarest of things in Indian tech: a company that survived the funding winter, found a real business model, and lived to tell the story in public markets."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
