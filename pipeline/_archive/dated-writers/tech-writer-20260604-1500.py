#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 15:00 UTC run"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Skyroot Aerospace Just Became India's First Space-Tech Unicorn. Google's Earliest Backer Led the Round.",
        "subheadline": "Ram Shriram's Sherpalo, GIC, and BlackRock have valued the Hyderabad rocket maker at $1.1 billion — betting that India's private space race is about to get very real.",
        "slug": make_slug("skyroot-aerospace-unicorn-ram-shriram-space-tech"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Ram Shriram — the Indian-origin venture capitalist who wrote Google's first cheque — is now betting on Indian rockets. For NRI investors tracking deep-tech opportunities back home, Skyroot's billion-dollar milestone signals that India's space sector has graduated from ISRO press releases to institutional-grade dealmaking.",
        "tags": ["space-tech", "indian-startups", "skyroot", "ram-shriram", "unicorn"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/skyroot-aerospace-becomes-indias-first-space-tech-unicorn/"},
            {"name": "StartupPoint", "url": "https://startuppoint.in/skyroot-aerospace-targets-revenue-fy27/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Skyroot_Aerospace"},
            {"name": "Forbes India", "url": "https://www.forbesindia.com/article/take-one-big-story-of-the-day/with-skyroots-51-mln-funding-indian-space-tech-startups-seek-new-orbit/91593/1"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/90/Vikram-S_rocket%27s_Mission_Prarambh_04.webp",
        "image_caption": "Skyroot's Vikram-S rocket during Mission Prarambh at the Satish Dhawan Space Centre in Sriharikota",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India's private space industry just produced its first billion-dollar company, and the investor list reads like a who's-who of global capital.

Skyroot Aerospace, the Hyderabad-based rocket maker founded by two former ISRO scientists, has closed a $60 million funding round that values the company at $1.1 billion — making it India's first space-tech unicorn. The round was co-led by Ram Shriram's Sherpalo Ventures and Singapore's sovereign wealth fund GIC, with participation from BlackRock, the Greenko Group founders, Arkam Ventures, Playbook Partners, and the Shanghvi Family Office.

The name that matters most on that list is Shriram's. The Indian-origin venture capitalist wrote Google's first angel cheque in 1998, sat on Alphabet's board for over two decades, and built a track record that makes Silicon Valley founders return his calls. He is now joining Skyroot's board — a signal that this is not a charity bet on national pride but a calculated wager on commercial space economics.

## From ISRO Labs to Launchpads

Pawan Kumar Chandana and Naga Bharath Daka left ISRO in 2018 with an idea that most Indian investors at the time would have considered absurd: build rockets privately, in India, at a fraction of global costs. Eight years later, they have $160 million in total funding, a manufacturing facility being built in Telangana with a ₹500 crore investment agreement signed at Davos, and an upcoming launch that could rewrite the rules.

Skyroot's Vikram-S became India's first privately developed rocket to reach space in November 2022, hitting an altitude of 89.5 kilometres. The suborbital flight was a proof of concept. What comes next is the real business: Vikram-1, which the company calls India's first private orbital rocket, designed to deliver small satellites to low Earth orbit.

The timing is deliberate. The global small satellite launch market is projected to exceed $30 billion by 2030, driven by constellations for broadband internet, Earth observation, and defence surveillance. SpaceX dominates the heavy-lift segment, but hundreds of satellite operators need affordable, frequent rides to specific orbits — the kind of service that a nimble, cost-competitive Indian launcher can provide.

## Why NRIs Should Pay Attention

The investor composition tells a story that goes beyond Skyroot. GIC doesn't write $60 million cheques on sentiment. BlackRock-managed funds don't show up in pre-revenue rocket companies unless the risk-return calculus has shifted. The fact that both are backing an Indian space startup alongside Shriram suggests that global institutional capital now views India's space sector the way it viewed India's software industry in the early 2000s — as structurally undervalued and operationally competitive.

For Indian Americans in the aerospace and defence sectors — and there are thousands working at Boeing, Lockheed Martin, SpaceX, and NASA — Skyroot represents something unusual: a credible return-to-India opportunity in deep tech, not just in software. The company is targeting ₹977 crore in revenue by FY27, an ambitious figure for a company that has yet to complete an orbital launch, but one that reflects the order pipeline building around small satellite operators.

## The Bigger Picture

Skyroot is not alone. Agnikul Cosmos recently demonstrated a 3D-printed rocket engine with an 18.85-second quick-start, a feat no other company has achieved. Pixxel is building hyperspectral satellite constellations. Dhruva Space is working on satellite deployment systems. India's private space ecosystem now has over 200 startups, up from fewer than a dozen in 2019 — a direct consequence of the government opening up the sector through the Indian National Space Promotion and Authorisation Centre (IN-SPACe) and the broader India Semiconductor Mission framework.

The Vikram-2, which Skyroot plans to develop with the fresh capital, will carry a 1-tonne payload to orbit using an advanced cryogenic upper stage — the same class of technology that took ISRO decades and billions of dollars to master. If Skyroot can deliver it by its 2027 target, it will have compressed a national space programme's learning curve into a decade of startup execution.

Ram Shriram once turned a $250,000 bet on two Stanford graduate students into a stake in the world's most valuable advertising company. Whether Skyroot delivers similar returns depends on physics, not finance. But the fact that he's betting on Hyderabad's rocket scientists the way he once bet on Mountain View's search engineers is, in itself, the story."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tim Cook's Final WWDC Arrives Next Week. Apple's India Problem Is Arriving With It.",
        "subheadline": "As Cook prepares to hand Apple to John Ternus on September 1, his last developer keynote on June 8 will unveil Siri 2.0 and iOS 27 — while India's antitrust regulator closes in on the company's financials.",
        "slug": make_slug("apple-wwdc-2026-tim-cook-india-cci-siri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India now manufactures 30% of all iPhones, hosts 15.4 million Apple developers, and generated ₹444 billion in App Store developer billings in 2024. For Indian Americans in the Apple ecosystem — whether building apps, managing supply chains, or investing in AAPL — Cook's final WWDC and the CCI probe are two sides of the same strategic question: how much does Apple need India, and how much leverage does India now hold?",
        "tags": ["apple", "wwdc", "tim-cook", "india", "cci-antitrust", "siri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/02/apple-event-next-week-all-systems-glow/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/03/apple-agrees-to-reveal-india-revenue-in-order-to-avoid-massive-fine/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/apple-to-submit-india-financials-cci-probe"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/tim-cooks-net-worth-as-he-prepares-to-retire-as-apple-ceo"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple CEO Tim Cook, who will step down on September 1, 2026, and become executive chairman",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Tim Cook will take the stage at Apple Park on Monday, June 8, for the last time as the company's chief executive. It will be the most consequential developer keynote Apple has delivered in years — and the most complicated.

WWDC 2026 is where Apple will unveil iOS 27 and Siri 2.0, a ground-up rebuild of its voice assistant designed to compete directly with ChatGPT, Claude, and Gemini. The company has teased the event with the tagline "All systems glow," a likely reference to Siri's rumoured new interface — dark backgrounds with luminous elements that signal Apple's belated but aggressive entry into the AI assistant war.

But as Cook prepares to hand the company to John Ternus, his senior vice president of hardware engineering, on September 1, a quieter drama is unfolding 13,000 kilometres away. India's Competition Commission has finally forced Apple to submit the financial details of its Indian business — data the company has resisted handing over for years — as part of an antitrust investigation that found Apple "abused its dominant position" in the iPhone apps market.

## What WWDC Will Deliver

The centrepiece is Siri 2.0. Apple's assistant has been the punchline of the AI industry for three years while competitors shipped increasingly capable chatbots. iOS 27 will reportedly bring a dedicated Siri app, a "Search or Ask" feature in the Dynamic Island, and chatbot-level conversational intelligence powered by Apple's on-device AI models.

The update is also laying groundwork for Apple's first foldable iPhone, expected this September alongside Ternus's formal takeover. iOS 27 will support split-view multitasking on the iPhone for the first time, with an iPad-like interface when the device is unfolded. Apple is describing this as a "Snow Leopard" release — lighter on new features, heavier on performance and code cleanup — which suggests the company knows it has accumulated technical debt that needs clearing before a hardware revolution.

For developers, the stakes are immediate. The App Store's AI-enhanced search is already changing traffic patterns, and Siri deep links could reshape how users discover and interact with apps. Indian developers — all 15.4 million of them, according to GitHub data — stand to be disproportionately affected.

## The India Equation

Apple's relationship with India has become the most strategically important in its supply chain. The company now manufactures 30 per cent of all iPhones in India, up from virtually zero five years ago. Foxconn's Chennai plant, Tata's Hosur facility, and Foxconn's Pune operations are all running at capacity. In the last fiscal year, iPhones worth over $22 billion were assembled in India — a figure that makes the country indispensable to Apple's China-diversification strategy.

The developer side is equally significant. Indian developers earned their share of ₹444 billion in App Store billings and sales in 2024, with 80 per cent of that revenue coming from international markets. Indian-built apps have been downloaded over 755 million times globally. Apple's own Developer Centre in Bengaluru has become a pipeline for the kind of talent the company needs as it builds out its AI capabilities.

## The CCI Problem

Which makes the antitrust probe all the more delicate. The CCI investigation, launched in 2021 by a coalition that includes Tinder-owner Match and the Alliance of Digital India Foundation, found that Apple's App Store constitutes "an unavoidable trading partner" for developers, who are forbidden from using third-party payment systems for in-app purchases. Under India's updated competition law, fines can be calculated on global revenue — which for a company generating $111 billion per quarter could mean an eye-watering penalty.

Apple had been stalling, refusing to submit its India-specific financial data. A Delhi High Court judge last month told the company to "cooperate," and at a May 21 hearing, Apple's lawyer requested a "final extension" until June 25 to file the numbers.

The timing is not lost on observers. Cook is trying to exit on a high — announcing the AI features that will define Apple's next decade — while the company negotiates the terms of doing business in the market that now builds nearly a third of its flagship product.

## What Comes Next

Ternus, who has spent 25 years at Apple and led the hardware engineering team responsible for the M-series chips, iPhone industrial design, and Apple Vision Pro, represents a shift toward engineering-first leadership. Cook was an operations genius who turned Apple into the world's most efficient supply chain. Ternus is a product builder in a moment when Apple needs to ship genuine AI innovation, not just announce it.

For Indian Americans who work at Apple, develop for its platforms, or hold its stock — and given that AAPL remains one of the most widely held equities in Indian American portfolios — the next four months are a two-front story: whether Siri 2.0 can close the gap with OpenAI, and whether Apple can settle its India problem without losing the manufacturing base it spent five years building."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "AMD Just Hit a Record High. The Trillion-Dollar Club Is One Good Quarter Away.",
        "subheadline": "Lisa Su's chipmaker closed at $542 with an $885 billion market cap after landing a six-gigawatt OpenAI deal and reporting 57 per cent data-centre growth. Thousands of Indian engineers in Hyderabad are building the chips that got it there.",
        "slug": make_slug("amd-record-high-trillion-openai-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "AMD's Hyderabad and Bangalore design centres employ thousands of Indian engineers who are directly building the AI and data-centre chips driving the company toward a trillion-dollar valuation. For Indian Americans at AMD on H-1B visas or holding RSUs, the stock's trajectory is both a career validation and a wealth event. For NRI investors, AMD represents the rare semiconductor pure-play where Indian engineering talent is a core competitive advantage, not a cost centre.",
        "tags": ["amd", "semiconductors", "ai-chips", "hyderabad", "lisa-su", "trillion-dollar"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/amd-stock-price-trillion-dollar-market-value-nvidia"},
            {"name": "Barchart / Intel Computex", "url": "https://www.barchart.com/story/news/33988993/intel-sets-sights-on-nvidia-and-amd-with-upcoming-ai-data-center-chip-launch-by-year-end"},
            {"name": "Reuters / Broadcom", "url": "https://www.reuters.com/technology/broadcom-set-shed-300-billion-value-ai-results-fail-impress-2026-06-04/"},
            {"name": "Morgan Stanley Research", "url": "https://www.morganstanley.com/ideas/ai-memory-pricing-semiconductor"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg/1280px-SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg",
        "image_caption": "AMD CEO Lisa Su, who has led the company's transformation from a struggling CPU maker into an AI chip powerhouse",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Advanced Micro Devices closed at a record $542.52 on Wednesday, giving Lisa Su's company a market capitalisation of $884.6 billion. It needs to reach $551.94 to cross $900 billion. At the current trajectory, the trillion-dollar club — currently occupied by Apple, Microsoft, NVIDIA, Alphabet, Amazon, and Meta — may need to set another place at the table.

The numbers behind the run are not speculative. AMD's Q1 2026 data-centre revenue hit $5.8 billion, up 57 per cent year over year, driven by its EPYC server processors and Instinct MI accelerators that are now deployed at scale by hyperscalers and enterprise AI customers. The clincher was the OpenAI deal: a contract covering six gigawatts of computing capacity, which firmly planted AMD as the second supplier in the AI infrastructure stack that NVIDIA has dominated for three years.

At Computex 2026 this week in Taipei, AMD showed it has no intention of slowing down. The company unveiled the Ryzen AI Max+ Pro 495, a 16-core Zen 5 processor with a 40-compute-unit GPU aimed at AI workstations, alongside an AMD Halo mini PC designed to compete with NVIDIA's DGX Spark as a desktop AI development box. Unlike NVIDIA's ARM-based Spark, AMD's offering runs on x86 and supports Windows — a pragmatic choice that keeps it compatible with the enterprise software stack that most developers already use.

## The Hyderabad Factor

What rarely makes it into Wall Street research notes is where AMD's chips are actually designed. The company's engineering centres in Hyderabad and Bangalore are among its largest outside the United States, employing thousands of engineers who work on everything from CPU core design to GPU verification to AI accelerator firmware.

This is not outsourced testing. AMD India handles critical-path chip design work that directly feeds into the products driving the company's revenue growth. The EPYC processors that won the OpenAI contract were designed with significant contributions from Indian engineering teams. The Instinct MI series — AMD's answer to NVIDIA's H100 and B200 — runs through verification pipelines in Hyderabad before reaching tape-out.

For the Indian Americans who work at AMD in the United States, many of whom hold restricted stock units as part of their compensation, the stock's march toward a trillion dollars is both a professional and financial milestone. An engineer who joined AMD five years ago at $80 per share is sitting on a 575 per cent gain. For those on H-1B visas, the company's stability and growth provide the kind of employment security that visa holders prize above almost everything else — a counterpoint to the layoff waves that have swept through Google, Amazon, and Meta.

## Why the Street Is Bullish

Morgan Stanley's semiconductor team, led by Shawn Kim, published a note this week arguing that "agentic AI-driven CPU demand structurally favours AMD in cloud share gains." The thesis is straightforward: as AI workloads move from training to inference and agent orchestration, the balance of compute shifts from pure GPU parallelism toward CPU-GPU coordination — exactly the architectural sweet spot that AMD's integrated EPYC-plus-Instinct platform occupies.

The contrast with competitors is instructive. Broadcom, which reported record AI revenue of $10.8 billion in Q2, saw investors wipe $270 billion off its market value on Thursday because its guidance implied a growth deceleration. NVIDIA, despite forecasting $20 billion in CPU revenues this year from its new RTX Spark platform, trades at valuations that leave little room for disappointment. Intel, resurgent under Lip-Bu Tan with a stock up 442 per cent in 52 weeks, is still proving that its 18A process technology can deliver at scale.

AMD sits in a different position: expensive enough to reflect its AI momentum, but cheap enough relative to NVIDIA — at roughly 30 times forward earnings versus NVIDIA's 40-plus multiple — that institutional investors see it as the safer bet for continued AI infrastructure spending.

## The NRI Investment Case

For Indian investors, both in the diaspora and in India, AMD represents something specific. Unlike NVIDIA, whose Indian presence is primarily in sales and support, AMD's Indian engineering centres are a core part of the company's competitive infrastructure. When AMD wins a hyperscaler deal, Indian engineers designed a measurable portion of the silicon that closed it.

This is not a sentimental argument. It is a structural one. Companies whose engineering talent is distributed across cost-competitive geographies tend to sustain R&D spending advantages over time. AMD spends roughly 25 per cent of revenue on R&D, a figure it can maintain partly because its Indian centres deliver world-class chip design at Indian salary scales.

The trillion-dollar question — literally — is whether Lisa Su can sustain 57 per cent data-centre growth in a market where NVIDIA is spending $20 billion on new CPU products and Intel is executing one of the most aggressive turnarounds in semiconductor history. The answer probably depends less on Su's strategy, which has been consistently excellent, and more on whether the AI infrastructure buildout that Jensen Huang says will reach $1 trillion by 2028 actually materialises.

If it does, AMD's Hyderabad engineers will have designed a meaningful fraction of the chips that power it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
