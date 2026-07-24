#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-27 14:00 PDT run"""

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

# ── ARTICLE 1 ─────────────────────────────────────────────────────────────
art1_body = """Meta has handed the keys to the world's largest messaging platform to an Indian fintech entrepreneur who never earned an engineering degree.

Kunal Shah, the 47-year-old founder of credit-card rewards platform CRED, will take charge of WhatsApp globally, succeeding Will Cathcart, who led the app for nearly seven years. The appointment, announced this week alongside Meta's $900 million investment in CRED, is arguably the most consequential leadership move in Indian tech this year — and it sends a pointed message about where Silicon Valley sees its next growth engine.

## The Deal Behind the Title

The arrangement is unusual even by Big Tech's standards. Meta's $900 million flows into CRED through a mix of primary subscription and secondary share purchases, giving the social media giant roughly 20 per cent of the Bengaluru-based fintech. Shah retains his personal stake but steps back from day-to-day operations, with Miten Sampat — who has led strategy and finance since 2020 — taking over as interim chief executive.

CRED is now valued at approximately $4.5 billion on a post-money basis, a partial recovery from its 2022 peak of $6.4 billion. The company recently crossed $325 million in annual revenue across payments, lending, insurance, and wealth management, and posted its first profitable quarter earlier this year.

"Kunal built CRED into one of India's most important technology companies, and he brings the kind of builder mentality and global perspective that will serve him well in running the world's biggest messaging app," Mark Zuckerberg said in a statement.

## Why WhatsApp Needs an Indian Builder

The logic of the appointment is geographical as much as it is strategic. India is WhatsApp's largest market, home to more than 500 million of its 3 billion-plus global users. Yet the platform's push into digital payments has produced mixed results. WhatsApp Pay gained traction but has been consistently outpaced by PhonePe and Google Pay in the UPI ecosystem. Commerce integrations remain nascent.

Shah's track record suggests he understands something about consumer behaviour that pure technologists often miss. He built FreeCharge into one of India's earliest digital payments successes before selling it to Snapdeal for roughly $400 million in 2015. CRED, launched in 2018, grew to 17 million members by turning the mundane act of paying credit-card bills into a rewards-driven habit loop.

Meta's chief product officer Chris Cox, in an internal memo reviewed by Reuters, described Shah as possessing "an intuitive grasp of the immense, global product potential for WhatsApp" and "an immense entrepreneurial energy combined with a natural humanism."

## The Super-App Question

Industry observers are reading the move as a signal that Zuckerberg's long-dormant super-app ambition is back on the table. China has WeChat, Southeast Asia has Grab and GoTo — but no single platform in India has successfully combined messaging, payments, commerce, and financial services at scale. Every major Indian conglomerate has tried. Tata, Jio, Adani — none have cracked the code.

WhatsApp, with its unmatched distribution in India and increasingly across Brazil and Indonesia, is the most plausible candidate. Shah, who has spent two decades thinking about payments, consumer incentives, and trust-based platforms in emerging markets, may be the most plausible person to try.

## What It Means for Indian Americans

For the Indian American tech community, Shah's appointment adds a striking new name to an already formidable roster of Indian-origin leaders running global platforms — Pichai at Alphabet, Nadella at Microsoft, Mohan at YouTube. But Shah's trajectory is different. He never attended an IIT or worked his way up a corporate ladder in the Valley. He is a Mumbai-bred entrepreneur whose career was forged entirely in the Indian startup ecosystem.

That distinction matters. It suggests the pipeline of Indian tech leadership is diversifying — not just IIT-to-Stanford-to-FAANG, but founder-to-global-CEO. For NRI investors, the deal also puts a spotlight on CRED's IPO trajectory: with Meta now a strategic investor and Shah's departure creating a succession story, a public listing feels closer than ever.

https://www.instagram.com/p/DZ46EBrINui/

For the diaspora, this is no longer just about Indians running American companies. It is about an American company deciding it needs an Indian builder to understand its largest market — and, perhaps, to rethink its entire product."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Just Handed WhatsApp to a Mumbai Founder Who Never Wrote a Line of Code",
    "subheadline": "Kunal Shah, the CRED founder who turned credit-card bills into a rewards empire, will lead the world's biggest messaging app. Meta is betting $900 million that an Indian entrepreneur can build the super-app Silicon Valley never could.",
    "slug": make_slug("kunal-shah-whatsapp-head-meta-cred-900m-super-app"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Shah joins Pichai, Nadella, and Mohan on the roster of Indian-origin leaders running global platforms — but as the first founder-CEO, not a corporate climber. NRI investors should watch CRED's IPO trajectory closely.",
    "tags": ["meta", "whatsapp", "kunal-shah", "cred", "fintech", "indian-tech-leaders", "super-app"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/22/whatsapp-gets-new-chief-as-meta-taps-indias-cred-founder-kunal-shah-and-invests-900m-in-startup/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/whatsapps-pick-indian-fintech-founder-signals-scale-payment-ambitions-2026-06-25/"},
        {"name": "Mint", "url": "https://www.livemint.com/opinion/online-views/street-cred-how-creds-kunal-shah-might-help-metas-zuckerberg-realize-his-dream-of-a-super-app-11750912430027.html"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
    "image_caption": "Kunal Shah, founder of CRED, now leads WhatsApp globally",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ── ARTICLE 2 ─────────────────────────────────────────────────────────────
art2_body = """The pipeline that once moved Indian engineers in a single direction — Hyderabad to Hyd-tech Park to the Bay Area — is reversing. And neither end is ready for it.

Active technology job openings in India fell to 93,000 in June 2026, a 28-month low, according to staffing firm Xpheno. The 14 per cent month-on-month decline is stark enough. The year-on-year drop of 17 per cent, and the near-collapse at the extremes — senior-level openings down 67 per cent, entry-level down 44 per cent — suggest something structural, not cyclical.

Into this shrinking market are walking thousands of Indian tech professionals who once occupied corner desks at Amazon, Google, and Microsoft.

## The Numbers Behind the Reverse Migration

In the first half of 2026 alone, an estimated 7,300 tech workers returned to India from the United States, according to industry reports. The drivers are familiar: over 100,000 tech layoffs across American firms, of which roughly 25,000 are estimated to involve H-1B visa holders. Stricter visa regulations, including a proposed $100,000 sponsorship fee that remains tangled in court challenges, have made the math of staying in America increasingly hostile.

The return migration trend is expected to outpace outbound movement to the US before the end of 2026 — a reversal that would have been unthinkable five years ago.

But the assumption that India would absorb these professionals seamlessly has collided with reality.

## A Market That Cannot Absorb Them

The mismatch is both quantitative and qualitative. TCS, India's largest IT employer, extended just 25,000 fresher offers in its most recent campus hiring cycle — roughly half the 40,000-plus it routinely offered in prior years. Across the sector, direct campus hiring remains 30 to 35 per cent below historical levels.

"Post-pandemic, there has been a shift to hyper-elasticity with the overall hiring outlook turning conservative," said Kamal Karanth, co-founder of Xpheno, the specialist staffing firm whose data underpins most workforce analyses of the Indian tech sector.

Returnees face a particular set of obstacles. Indian employers frequently view them with suspicion, worried they will decamp for the US at the first opportunity. The salaries these professionals commanded abroad — often five to ten times their Indian equivalents — create expectations that few domestic firms can or will meet. And many returnees arrive with deep but narrow specialisations built for American product companies, not for the project-based, client-servicing model that still dominates Indian IT.

## AI Is Reshaping the Floor, Not Just the Ceiling

The hiring decline is not merely a recession-era headcount freeze. AI-powered automation and copilots are fundamentally changing how enterprises scale. Companies are asking whether technology can improve output without increasing workforce size — and the answer, increasingly, is yes.

Entry-level roles are absorbing the heaviest blow. The 44 per cent year-on-year decline in entry-level openings reflects not just cautious budgets but a genuine reduction in the work that junior engineers once performed. Code generation, testing, documentation, basic data analysis — the entry ramps that built a generation of Indian tech careers are being flattened by the very tools those careers helped create.

Senior roles are disappearing too, but for different reasons. Organisations are flattening structures, expecting leaders to drive business outcomes rather than manage headcount. The 67 per cent decline in senior openings is a structural shift, not a hiring pause.

## Where the Opportunities Survive

Global Capability Centres — the in-house offshore arms that companies like JPMorgan, Goldman Sachs, and Walmart operate in India — remain the brightest spot. Professionals with a decade or more of experience in a single domain, particularly in AI, cloud architecture, and cybersecurity, are still in demand. GCCs value the American experience that IT services firms discount.

Nvidia, which continues to expand hiring globally, represents the other end of the spectrum — companies riding the AI wave so aggressively that talent scarcity outweighs cost sensitivity.

## What It Means for Indian Americans

For every Indian engineer in the Bay Area watching colleagues get laid off, the calculus has shifted. The fallback plan — "I'll go back to India" — no longer guarantees a soft landing. India's tech market is tighter than it has been in over two years. Salaries in Bengaluru and Hyderabad have not kept pace with the expectations of someone accustomed to San Francisco compensation.

The strategic advice from workforce experts is blunt: if you have a decade-plus of deep specialisation in AI, cloud, or security, India's GCCs want you. If you are a generalist mid-career engineer hoping to slot back into the IT services machine that built your early career, the machine has moved on.

The one-way pipeline has become a traffic jam. And the tolls are rising at both ends."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Tech Job Market Hit a 28-Month Low. Thousands of Returning H-1B Workers Are Walking Into It.",
    "subheadline": "Active tech openings fell to 93,000 in June. Senior roles collapsed 67 per cent. And 7,300 H-1B returnees in the first half of 2026 are discovering that the fallback plan no longer guarantees a soft landing.",
    "slug": make_slug("india-tech-hiring-28-month-low-h1b-returnees-job-market"),
    "category": "technology",
    "vertical": "immigration",
    "diaspora_angle": "The 'I'll go back to India' fallback plan no longer guarantees a soft landing. Indian engineers in the Bay Area and beyond face a tighter market at both ends — stricter US visa rules AND a domestic hiring collapse.",
    "tags": ["h-1b", "india-tech-hiring", "layoffs", "reverse-brain-drain", "indian-tech-workers", "GCC"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Xpheno / Business Today", "url": "https://news.outsourceaccelerator.com/india-it-hiring-falls-to-28-month-low/"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/tech-talent-faces-challenges-finding-jobs-india-1b-return-2606/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/h-1b-returnees-face-cautious-ai-led-job-market-in-india-say-experts/article69195025.ece"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg",
    "image_caption": "A software developer at a dual-monitor workstation in a modern office",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ── ARTICLE 3 ─────────────────────────────────────────────────────────────
art3_body = """While Jensen Huang commands stage lights and Nvidia commands headlines, an Indian-origin engineer in Santa Clara has been quietly building the component that every AI data centre cannot function without.

Rajesh Vashist, the chairman and CEO of SiTime, runs a semiconductor company most people have never heard of. His stock has doubled this year. His earnings have grown at triple-digit rates for eight consecutive quarters. And he just closed a $3.2 billion acquisition that will nearly double his company's revenue. In a chip industry defined by thunderous capital expenditure announcements and geopolitical standoffs, SiTime is the precision instrument everyone overlooks — until the orchestra falls out of sync.

## What SiTime Actually Does

SiTime designs what are known as timing chips — semiconductors whose job is to set a steady beat for all the parts of a computer and keep them running together, like a conductor directing multiple groups of instruments. The company's MEMS (Microelectromechanical Systems) chips are used in over 400 applications, from AI data centres and autonomous vehicles to military aerospace systems, drones, and wearable devices.

The pitch is deceptively simple: more precise timing means more efficient computing. SiTime's newest line, called Chorus, delivers timing that is 10 times more precise than older quartz-based solutions. In an AI data centre where Nvidia's GPUs consume over 1,000 watts each, a more precise clock allows parts of the system to be briefly powered down when not in use. Over the multi-year life of a server, those milliseconds compound into meaningful energy savings.

"We deliver timing that they can rely on so that they can wake up their products and bring data more efficiently to them, rather than just running more often," Vashist told Reuters.

## The Renesas Deal Changes the Scale

In February 2026, SiTime announced a deal worth up to $3.2 billion to acquire timing assets from Japan's Renesas Electronics. The transaction, expected to close by year-end, will add roughly $300 million in first-year revenue to SiTime's $326.7 million in fiscal 2025 sales — effectively doubling the company's top line overnight.

But the deal is about more than revenue. The two companies will collaborate to integrate SiTime's Titan MEMS resonators into Renesas' microcontrollers and systems-on-chip. The result will be the first MCUs on the market that require no external timing components to operate — a significant simplification for automotive, industrial, and AI applications where size, power, and reliability are paramount.

Renesas CEO Hidetoshi Shibata has joined SiTime's board as part of the arrangement, and Vashist told Reuters the integration could eventually reach "billions of units."

## Stock Performance the Market Cannot Ignore

SiTime's financial trajectory has been exceptional. The company gapped up 28 per cent in a single session after its Q1 2026 earnings crushed expectations. The stock peaked at $901.81 in May before pulling back into a consolidation pattern. Even after the pullback, shares have outperformed 97 per cent of stocks tracked by Investor's Business Daily over the past 12 months.

Vashist projected 80 per cent growth in SiTime's AI data centre business for 2026 in a May CNBC interview — a figure that would have sounded like bravado from any other sub-$10-billion chipmaker. Coming from a company with eight straight quarters of triple-digit earnings growth, it reads more like understatement.

## The Indian-Origin Leadership Angle

Vashist is part of a growing cadre of Indian-origin semiconductor executives who are shaping the AI infrastructure stack. While the spotlight falls on consumer-facing leaders like Pichai and Nadella, the chip layer — where the physics meets the product — is increasingly Indian-led. Sanjay Mehrotra runs Micron. Cristiano Amon runs Qualcomm (with deep Indian engineering teams). Lip-Bu Tan, recently installed as Intel's CEO, has built much of his career alongside Indian technologists.

SiTime itself was co-founded by engineers from the Indian Institute of Technology system. The company's sixth-generation MEMS technology, called FujiMEMS, is years ahead of competitors, according to the company and independent analysts.

For NRI investors and engineers, the SiTime story offers a different template. This is not an IT services giant or a consumer app unicorn. It is deep-tech manufacturing, the kind of hard-science semiconductor work that India's own chip ambitions — from the Tata Electronics fab in Dholera to the Micron plant in Gujarat — are hoping to eventually produce domestically.

## Why This Matters for the AI Supply Chain

Every conversation about AI infrastructure gravitates toward GPUs, memory, and power. Timing rarely makes the list. But without precise synchronisation, the GPU cluster that cost $200 million to assemble underperforms. Data arrives late, computations fall out of sync, and energy is wasted keeping idle components running.

SiTime has positioned itself as the invisible layer that makes the visible layer work. As AI data centres scale from megawatts to gigawatts, the demand for precision timing scales with them. It is the kind of unsexy, indispensable technology that builds compounding value — and it is being built, in significant part, by Indian engineering talent."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Indian-Origin CEO You've Never Heard Of Is Powering Every AI Data Centre on Earth",
    "subheadline": "SiTime's Rajesh Vashist runs a precision timing chip company whose stock has doubled this year. His $3.2 billion Renesas deal and eight straight quarters of triple-digit growth make him the most important semiconductor CEO nobody is talking about.",
    "slug": make_slug("sitime-rajesh-vashist-timing-chip-ai-data-centre-renesas"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Vashist represents the Indian-origin deep-tech leadership layer that rarely makes headlines but is building the AI infrastructure stack. For NRI investors, SiTime offers a different template from IT services or consumer apps — hard-science semiconductor value.",
    "tags": ["semiconductors", "sitime", "rajesh-vashist", "ai-infrastructure", "mems", "indian-tech-leaders", "renesas"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/research/sitime-stock-sitm-data-center-semiconductor-chip-ai/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/sitime-introduces-chip-aimed-saving-power-ai-data-centers-2024-04-17/"},
        {"name": "EE Times", "url": "https://www.eetimes.com/sitime-bolsters-timing-portfolio-with-renesas-acquired-clocks/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/sitime-tech-could-go-into-billions-renesas-chips-sitime-ceo-says-2026-02-06/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg",
    "image_caption": "Close-up of a microprocessor circuit board with intricate semiconductor components",
    "image_attribution": "Pexels",
    "body": art3_body
}

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
