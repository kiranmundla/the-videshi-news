#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-01 00:00 UTC batch"""
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


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: US Commerce closes chip export loophole
# ─────────────────────────────────────────────────────────────────────

art1_body = """The U.S. Department of Commerce issued surprise weekend guidance on Sunday closing a year-old loophole that may have allowed hundreds of thousands of America's most advanced AI chips — including Nvidia's Blackwell and Rubin processors and AMD's MI350x — to reach Chinese entities through their overseas subsidiaries.

The move was unusual in both timing and candour. The guidance, posted to the Commerce Department's website on a Sunday, declared that license requirements for advanced chips now apply to entities headquartered in China regardless of where those entities are physically located. A subsidiary in Malaysia, a branch office in Singapore, a shell in Dubai — none of these now offer an end-run around U.S. export controls.

## How the Door Opened

The loophole traces back to May 2025, when the Trump administration announced it would not enforce the AI Diffusion rule issued in the final days of the Biden presidency. That rule had governed global access to AI chips with a country-tiered licensing system. By declining to enforce it, the Commerce Department inadvertently created a gap: Chinese companies could — and apparently did — purchase advanced chips through subsidiaries outside China.

Chris McGuire, a former State Department official and technology policy expert, called it "a HUGE problem" in a social media post on Sunday. "Chinese companies have been buying these chips, very likely at scale," he wrote. One chip industry source with deep supply-chain knowledge estimated the volume at "hundreds of thousands" of units over the past year.

Neither Nvidia nor AMD responded to requests for comment.

## What It Means for the AI Supply Chain

The closure lands days before Computex 2026, where Jensen Huang is set to unveil Nvidia's Vera Rubin platform and its first consumer PC chips. It adds a new layer of complexity to an already fraught semiconductor trade environment. Nvidia has already excluded China from its Q2 revenue guidance, projecting $91 billion in data centre revenue without a single yuan from the world's second-largest AI market. AMD, meanwhile, has maintained a modest 4 per cent share in China through a diversified product portfolio spanning CPUs, GPUs, and FPGAs.

For the broader AI infrastructure build-out — the $150 billion annual investment cycles now flowing through Taiwan, the hyperscaler capital expenditure wars, the race to fill data centres with next-generation accelerators — the tighter controls mean more supply could flow to non-Chinese buyers, potentially easing some of the allocation pressure that has kept delivery times long and prices high.

## The Diaspora Dimension

For the thousands of Indian engineers at Nvidia and AMD — many of whom are on H-1B or L-1 visas — the geopolitical tug-of-war over chip exports is not abstract policy. It shapes which products their teams prioritise, which markets their work serves, and ultimately which roles grow or shrink. Nvidia alone employs over 10,000 engineers in India and has been expanding its Bangalore and Hyderabad operations as China revenue disappears.

India's own semiconductor ambitions add another dimension. As the U.S. tightens controls on Chinese access to advanced chips, India's $10 billion semiconductor mission — including the Tata Electronics fab in Dholera and Micron's Gujarat facility — becomes strategically more relevant. India is not yet making cutting-edge logic chips, but its packaging and assembly capabilities are positioned to capture overflow from a supply chain being forcibly rewired away from Chinese entities.

For NRI investors holding NVDA or AMD stock, the immediate read is neutral to slightly positive: tighter controls reduce the risk of a geopolitical blowback that could trigger wider sanctions, while Nvidia's decision to exclude China revenue from guidance means the hit is already priced in. The longer game depends on whether these controls hold — and whether the hundreds of thousands of chips that already slipped through end up powering the Chinese AI capabilities they were meant to prevent.

The Commerce Department did not respond to a request for comment on that question."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Just Closed a Year-Old Loophole. Hundreds of Thousands of AI Chips May Have Already Slipped Through.",
    "subheadline": "The Commerce Department issued surprise Sunday guidance blocking Nvidia and AMD chip sales to Chinese subsidiaries abroad — a gap that existed for a full year.",
    "slug": make_slug("us-commerce-ai-chip-export-loophole-nvidia-amd-china"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at Nvidia and AMD face shifting team priorities as China revenue vanishes; India's Dholera and Gujarat fabs gain strategic relevance as the chip supply chain rewires away from Chinese entities; NRI investors in NVDA/AMD should note the geopolitical risk reduction.",
    "tags": ["semiconductors", "nvidia", "amd", "china", "export-controls", "geopolitics", "indian-engineers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/us-takes-step-halt-nvidia-ai-chip-shipments-chinese-firms-outside-china-2026-05-31/"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/us-moves-tighten-ai-chip-export-rules-chinese-firms-overseas"},
        {"name": "Bloomberg Tax", "url": "https://news.bloombergtax.com/daily-tax-report/us-moves-to-close-ai-chip-loophole-for-china-firms-abroad-rtrs"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: HPE AI server business
# ─────────────────────────────────────────────────────────────────────

art2_body = """Hewlett Packard Enterprise's stock closed at $43.04 on Friday, up 12.6 per cent in a single session and roughly 80 per cent for the year. For a company that spent years as the unglamorous half of the HP split, the number tells a straightforward story: enterprise AI infrastructure is no longer a niche line item. It is the business.

HPE reports fiscal Q2 2026 earnings after market close on Tuesday, and Wall Street is expecting revenue between $9.6 billion and $10.0 billion, with earnings per share of $0.54 — up from $0.38 a year ago. Those expectations are not wild optimism. They are extrapolations from a Q1 that already delivered $9.3 billion in revenue (up 18 per cent year-over-year), a record non-GAAP EPS of $0.65, and free cash flow of $708 million.

## The Juniper Effect

The standout number from Q1 was networking revenue, which surged 152 per cent on a reported basis. That figure is inflated by the Juniper Networks acquisition, but the strategic logic behind the deal is now proving out. Networking now accounts for about 30 per cent of HPE's total revenue and more than half of its operating profit. For a company historically defined by servers and storage, that is a structural transformation.

The Juniper integration is giving HPE what it lacked: a credible networking stack to sell alongside its AI server infrastructure. Hyperscalers and large enterprises do not buy AI compute in isolation — they buy racks, networking, and management software as a system. HPE can now offer a more complete package, which is reflected in its record $5.0 billion AI Systems backlog entering Q2.

## Where India Fits

HPE's India operations are among its largest globally. The company's Bangalore campus is one of its primary engineering centres, with thousands of engineers working on server firmware, cloud platform development, and — increasingly — AI infrastructure software. HPE India also serves as a significant delivery centre for its GreenLake cloud platform, the hybrid cloud operating model that management has positioned as a core growth vector.

For Indian engineers in the enterprise infrastructure space — whether at HPE, Dell, Cisco, or their Indian IT services counterparts — the AI server boom is reshaping career trajectories. The skills that matter are shifting from traditional rack-and-stack server management toward GPU cluster orchestration, high-bandwidth networking, and liquid cooling systems. HPE's AI server backlog is, in practical terms, a multi-year hiring signal for the Indian engineering talent pool that builds and maintains this infrastructure.

## The Investor View

For NRI investors, HPE's 80 per cent YTD run raises an obvious question: how much AI premium is already priced in? The stock's P/E ratio sits at an unusual -226 on a GAAP basis (owing to a negative net margin from acquisition-related charges), but the non-GAAP picture is cleaner. The company's FY 2026 EPS guidance of $2.30 to $2.50 puts the stock at roughly 17-19x forward earnings — not cheap by HPE's historical standards, but hardly Nvidia territory.

The risk, as with all AI infrastructure plays, is execution on the backlog. A $5 billion order book is only as good as the supply chain that fulfils it. Memory prices are rising sharply — RAM and SSD costs have surged this year as AI servers consume an outsized share of global production — and GPU allocation remains tight. HPE's ability to deliver on its backlog without margin compression will be the story on Tuesday.

The broader signal is harder to argue with: enterprise buyers are committing real capital to AI infrastructure, and the companies building it — HPE, Dell, Cisco, and their upstream suppliers — are capturing that spend. For the Indian diaspora's engineering workforce, which is deeply embedded in this value chain from Bangalore to Houston, the AI server cycle is not a passing trend. It is a structural shift in where enterprise technology dollars flow."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "HPE's Stock Has Nearly Doubled This Year. A $5 Billion AI Backlog Explains Why.",
    "subheadline": "Hewlett Packard Enterprise reports Tuesday with Wall Street expecting $9.8 billion in revenue. Its Juniper deal and AI server orders have transformed the company.",
    "slug": make_slug("hpe-ai-server-backlog-5-billion-stock-earnings"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "HPE's Bangalore campus is one of its largest engineering centres globally, with thousands of Indian engineers working on AI infrastructure, cloud platforms, and server firmware. The $5B AI backlog is a multi-year hiring signal for Indian engineering talent in enterprise infrastructure.",
    "tags": ["hpe", "ai-servers", "enterprise-tech", "earnings", "bangalore", "indian-engineers", "data-center"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "CoinCentral", "url": "https://coincentral.com/hewlett-packard-hpe-stock-q2-earnings/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/HPE/earnings/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/hpe-ai-pivot-drives-robust-q2-2026-projections/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: AMD vs Nvidia — two China strategies
# ─────────────────────────────────────────────────────────────────────

art3_body = """Lisa Su flew to China quietly. Jensen Huang flew with the President.

The contrast between AMD's and Nvidia's recent approaches to the world's second-largest AI hardware market tells you everything about where each company stands — and what each stands to lose. As both CEOs converge on Computex 2026 in Taipei this week, their divergent China playbooks are shaping not just semiconductor geopolitics but the career prospects of thousands of Indian engineers who build these companies' products.

## The Scoreboard

The numbers are stark. Nvidia's market share in Chinese AI accelerators has collapsed from 95 per cent to effectively zero, the result of escalating U.S. export controls that have systematically cut off China's access to the world's most advanced GPU architectures. Every generation of chips — from A100 to H100 to Blackwell — has been progressively restricted, and Nvidia's latest fiscal guidance excludes China entirely from its data centre revenue projections.

AMD, by contrast, has maintained a modest but real 4 per cent share. The difference is structural: AMD sells not just GPUs but also CPUs and FPGAs, a diversified product portfolio that gives Chinese customers access to AMD silicon for workloads that do not trigger the highest-tier export controls. Where Nvidia's China business is binary — either the most advanced AI chips or nothing — AMD offers a spectrum.

## Two Styles of Diplomacy

When Jensen Huang visited Beijing in mid-May, he did so as part of a high-powered delegation accompanying U.S. President Donald Trump to meet Chinese leader Xi Jinping. The trip attracted enormous media attention and underscored Nvidia's position at the centre of the U.S.-China technology rivalry. Huang has been vocal about the unintended consequences of chip controls, arguing that restrictions on American companies create a vacuum that Chinese firms — particularly Huawei — are rapidly filling with domestic alternatives.

Su's visit, by comparison, was deliberately low-key. She met with Chinese partners and customers without fanfare, reinforcing relationships in a market where AMD still has room to operate. The quiet approach reflects both AMD's smaller geopolitical profile and a calculated bet that discretion serves better than spectacle in a market where the rules can change overnight.

Both CEOs are of Taiwanese descent, adding a personal dimension to their corporate strategies in a region where semiconductor supply chains, national identity, and geopolitical risk are tightly interwoven.

## The India Angle

For the Indian engineering workforce at both companies, the China strategies have tangible implications. Nvidia employs thousands of engineers in Bangalore and Hyderabad, and its India headcount has grown even as China revenue has disappeared — a deliberate shift of R&D resources toward markets that remain open. AMD's India operations, centred in Hyderabad and Bangalore, similarly support global product development but with less direct exposure to the China revenue question.

The broader consequence for Indian tech professionals is subtler. As both companies redirect product strategy away from China, India becomes a more important market and engineering hub. Nvidia's DGX Cloud partnership with Indian cloud providers, AMD's growing engagement with Indian OEMs, and both companies' expanding India R&D centres all point to the same conclusion: the engineers building the next generation of AI silicon are increasingly working from Indian campuses, even as the geopolitical battles play out thousands of miles away.

## What to Watch at Computex

Huang's keynote on Monday — at 8 p.m. PDT on Sunday for U.S.-based NRIs — is expected to showcase the Vera Rubin AI platform, Nvidia's first consumer PC chips, and expanded robotics initiatives. AMD's Lisa Su will not be at Computex this year, but the company's Zen 6 mobile processors and RDNA 5 GPU architecture are expected to surface through partner announcements.

For NRI investors weighing the two stocks, the China question is a lens, not a verdict. Nvidia's $1 trillion revenue forecast for AI chips excludes China and still overwhelms AMD's entire revenue base. AMD's China optionality is a hedge, not a thesis. The real question for both companies is whether the AI infrastructure build-out — now consuming $150 billion a year in Taiwan alone — sustains at this pace. If it does, both stocks have room to run. If it does not, the China market they cannot fully serve may end up mattering less than the demand curve they cannot fully meet."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Lisa Su Went to China Quietly. Jensen Huang Went with the President. Their Strategies Explain Everything.",
    "subheadline": "Nvidia's AI chip market share in China has dropped from 95 per cent to zero. AMD still holds 4 per cent. The divergent approaches of two Taiwanese-American CEOs are reshaping the industry.",
    "slug": make_slug("amd-nvidia-china-strategy-lisa-su-jensen-huang"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at both Nvidia and AMD are seeing their teams grow in India as China revenue shifts. Both companies expanding Bangalore and Hyderabad R&D operations. India increasingly important as both a market and engineering hub for AI chip development.",
    "tags": ["amd", "nvidia", "china", "geopolitics", "semiconductors", "computex", "lisa-su", "jensen-huang"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters via DevDiscourse", "url": "https://www.devdiscourse.com/article/technology/3373192-amd-and-nvidias-contrasting-paths-in-chinas-ai-market"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-ceo-kick-off-dominate-computex-gathering-taipei-2026-06-01/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/computex-nvidia-taiwans-expanding-role-ai-infrastructure-set-take-centre-stage-2026-05-30/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/163170/board-printed-circuit-board-computer-electronics-163170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
