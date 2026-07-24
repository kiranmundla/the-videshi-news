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
        "headline": "India's First Insurtech IPO of 2026 Opens Friday. The Grey Market Is Telling Investors to Slow Down.",
        "subheadline": "Turtlemint wants ₹883 crore to chase insurance in India's small towns. NRIs hunting the next fintech listing should read the muted premium before the hype.",
        "slug": make_slug("turtlemint-ipo-insurtech-india-nri-investors-grey-market"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who treat Indian fintech IPOs as a way to keep money working back home need to weigh Turtlemint's still-unprofitable model and flat grey-market premium before subscribing through their GIFT City or NRE-linked demat accounts.",
        "tags": ["fintech", "ipo", "insurtech", "indian-tech", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inc42", "url": "https://inc42.com/buzz/turtlemint-ipo-to-open-on-june-19-price-band-set-at-rs-144-152/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/turtlemint-ipo-to-open-on-friday-heres-all-you-need-to-know"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/turtlemint-fintech-solutions-raises-397-crore-from-anchor-investors/article69648000.ece"},
            {"name": "IBS Intelligence", "url": "https://ibsintelligence.com/ibsi-news/insurtech-turtlemint-eyes-106m-ipo-as-indias-digital-insurance-market-expands/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A stock-market display showing live trading data ahead of an Indian primary-market debut.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India's IPO calendar has a habit of turning fintech founders into paper billionaires before their companies turn a single rupee of profit. Turtlemint is about to test whether that trick still works in 2026.

The Mumbai-based insurance distribution platform opens its initial public offering to retail investors on Friday, June 19, and closes it on June 23. The price band is ₹144 to ₹152 a share, valuing the company at roughly ₹4,513 crore — about $475 million — at the top end. Turtlemint is raising up to ₹883 crore: a fresh issue of ₹660.72 crore that goes to the company, plus an offer for sale worth ₹221.95 crore that goes to existing shareholders cashing out. Shares are set to list on the BSE and NSE on June 29.

It is, notably, the first insurtech to brave India's public markets in 2026 — and the first real test of whether investor appetite for technology-led financial firms has survived a year of valuation resets at Razorpay, Zepto and the NSE itself.

### What Turtlemint actually does

Founded in 2015, Turtlemint runs what it calls a "phygital" model: a slick app and a network of roughly several lakh advisors who sell health, life and motor insurance in places where buying a policy still means talking to a human. Between April 2022 and December 2025, the company says it facilitated more than 21.8 million policies and generated over ₹10,066 crore — about $1.2 billion — in premiums. It has since bolted on mutual funds, loans and credit cards.

The pitch is the same one every Indian fintech makes: insurance penetration in India is dismally low by global standards, the addressable market is enormous, and a tech-enabled distributor can grab it cheaply. Turtlemint is explicitly chasing Tier 3 and Tier 4 towns — the small-city India that diaspora families often come from and still send money to.

### The number NRIs should not ignore

Here is the catch. Turtlemint is still losing money, and management's own line is that profitability should come "very soon" after listing — a phrase that should make any seasoned investor reach for the prospectus rather than the buy button.

The market seems to agree. Ahead of the issue, the grey-market premium — the unofficial price at which shares trade before listing — was reported at between ₹0 and ₹2 per share. In plain English, the smart money is pricing in essentially no listing-day pop. That is a sharp contrast to the frenzied premiums that greeted earlier Indian tech debuts, and it tells you the institutional crowd is treating this as a long-term bet, not a flip.

There is one reassuring signal on the other side of the ledger. On June 18, Turtlemint raised ₹397 crore from 32 anchor investors at the top of the band, with marquee names including ICICI Prudential, Mirae Asset, Amansa Holdings and BNP Paribas taking part. Domestic mutual funds soaked up 42.5% of the anchor allocation. When India's biggest fund houses commit at the ceiling price, it lends the offering credibility even if the grey market is yawning.

### Why this lands on a diaspora investor's desk

For non-resident Indians, Turtlemint sits at the intersection of two trends they care about. The first is the steady opening of India's primary markets to NRI money — through NRE-linked demat accounts and, increasingly, the GIFT City gateway that now lets Indian brokerages route overseas capital into domestic listings. The second is the diaspora's emotional and financial tether to small-town India, exactly the market Turtlemint is targeting.

But sentiment is a poor underwriter. Turtlemint cofounders Anand Prabhudesai and Dhirendra Mahyavanshi are each selling over 20 lakh shares in the OFS, pocketing roughly ₹32 crore and ₹34 crore respectively. Early backers Peak XV, Nexus, Blume and Granite Asia are trimming too. Insiders taking chips off the table is normal at IPO — but it is also a reminder that the people who know the company best are happy to sell at this price.

The honest read for a diaspora investor: this is a structural-growth story in a real market, not a guaranteed listing-day windfall. The flat grey-market premium is the tell. If you believe in India's insurance under-penetration over a five-year horizon, Friday is your entry. If you are hunting for a quick listing gain to wire back into your NRE account, the market is quietly suggesting you wait.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An IIT Just Open-Sourced an AI That Thinks in 22 Indian Languages. It Could Outlast the Billion-Dollar Startups.",
        "subheadline": "While Sarvam raises unicorn rounds, IIT Bombay's BharatGen is quietly building sovereign AI as public infrastructure — and the diaspora's engineers may matter more here than its investors.",
        "slug": make_slug("bharatgen-iit-bombay-sovereign-ai-22-indian-languages-diaspora"),
        "category": "technology",
        "vertical": "ai",
        "diaspora_angle": "Indian-origin AI researchers abroad, who often feel locked out of building for their mother tongues at Western labs, now have an open, government-backed platform to contribute to — and NRI parents get AI that actually understands the languages their kids are losing.",
        "tags": ["ai", "sovereign-ai", "indian-tech", "iit", "open-source"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/iit-bombay-showcases-bharatgen-at-bharat-innovates-2026.htm"},
            {"name": "IANS / IANSlive", "url": "https://www.ianslive.in/india-ai-firm-joins-g7-tech-talks-in-france"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17483868/pexels-photo-17483868.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A digital rendering of a neural network, illustrating large-language-model development.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India's sovereign-AI story has, until now, been told mostly in venture-capital terms. Sarvam turned unicorn this week with a $234 million round led by HCLTech. Krutrim has Ola's billions behind it. The narrative is one of startups racing to build a homegrown answer to OpenAI before global access dries up.

There is a quieter version of that story, and it does not have a cap table. At Bharat Innovates 2026 in Nice, France, IIT Bombay unveiled BharatGen — an open, multilingual AI ecosystem built not as a company but as public infrastructure, in the same spirit that gave India UPI and Aadhaar.

### What was actually launched

BharatGen is not a single model. It is a stack, and the breadth is the point. At its core sits Param2, a foundational language model with reasoning, coding and tool-calling abilities across all 22 scheduled Indian languages. Around it: Shrutam2, a multilingual speech-recognition and speech-to-text engine; Sooktam2, a text-to-speech system capable of zero-shot voice cloning; and Patram, a vision model trained specifically to read Indian documents — the messy, multi-script paperwork that trips up Western OCR.

It is being built at IIT Bombay's computer science department under Professor Ganesh Ramakrishnan, with a team of more than 60 researchers, engineers and linguists. Crucially, it is open. Where a startup guards its weights as the asset that justifies its valuation, BharatGen is being released as a platform others can build on — for governance, healthcare, education, finance, insurance and even cultural preservation.

### Why "open" changes the math

The timing is not subtle. Just days before BharatGen's showcase, a U.S. export order briefly cut Indian users off from Anthropic's top models — a stark reminder that access to frontier AI is now a geopolitical lever, not a market given. India's response has two prongs. The commercial prong is Sarvam and its peers, betting that regional champions can carve out durable positions. The public prong is BharatGen, betting that the most important AI infrastructure should be a commons, not a product.

For a country that has watched its digital public goods — UPI, the Aadhaar stack, DigiLocker — become the envy of the developing world, the logic is familiar. You do not rent the foundation of national infrastructure from a vendor who can switch it off.

### Where the diaspora comes in

This is where Indian Americans should pay attention, and not as investors. The diaspora's contribution to global AI has been overwhelmingly as labor inside other people's labs — the Indian-origin researchers at OpenAI, DeepMind, Meta AI and Anthropic whose names appear on the papers but whose work serves English-first products. Many of them have spoken privately about the strangeness of building world-class models that cannot hold a conversation in the language they grew up speaking.

An open, government-backed platform changes that calculus. BharatGen is the kind of project a researcher in Sunnyvale or New Jersey can actually contribute to — submitting language data, fine-tuning for a dialect, building an application — without quitting their job or moving back. For the academically inclined diaspora, it offers something a startup equity grant cannot: the chance to put your mother tongue into the foundation layer of a technology that a billion people will use.

There is a softer dividend too. Second-generation diaspora kids are losing their heritage languages at a steady clip. AI that genuinely understands Marathi, Tamil, Bengali or Punjabi — that can read a grandparent's handwritten letter or voice-clone a bedtime story — is not a novelty for these families. It is a thread back to a culture that distance keeps fraying.

### The realistic caveat

Open and ambitious does not mean finished. The frontier labs are racing on multi-hour agentic tasks; BharatGen's models are foundational but unproven at that scale, and academic projects in India have a long history of strong launches followed by funding droughts. Param2 will be judged not by its press release in Nice but by whether developers actually build on it.

Still, the strategic instinct is right. The startups will chase the enterprise money, as they should. But the version of sovereign AI that endures may be the one with no shareholders to answer to — and the diaspora, for once, gets to build rather than just staff it.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "At the G7's AI Table, Seven Companies Got a Seat. Only One Was Indian — and It's a Two-Year-Old Startup.",
        "subheadline": "Sarvam's Pratyush Kumar sat beside Sam Altman and Demis Hassabis at Evian. For the diaspora, the symbolism is bigger than the startup.",
        "slug": make_slug("g7-evian-ai-summit-sarvam-india-only-firm-diaspora"),
        "category": "technology",
        "vertical": "ai",
        "diaspora_angle": "After a decade of Indian-origin executives running other countries' tech giants, a homegrown Indian AI company sitting at the G7 table marks a shift the diaspora has waited for — from running the West's companies to representing India's own.",
        "tags": ["ai", "india", "g7", "sovereign-ai", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANSlive", "url": "https://www.ianslive.in/india-ai-firm-joins-g7-tech-talks-in-france"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/sarvam-turns-unicorn-after-234-million-fundraise.htm"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion-2026-06-15/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6950018/pexels-photo-6950018.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Leaders gathered around a conference table at a high-level international summit.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For the better part of a decade, the story of India in global technology has been a story of borrowed thrones. Sundar Pichai runs Google. Satya Nadella runs Microsoft. Arvind Krishna runs IBM, Shantanu Narayen runs Adobe, Nikesh Arora runs Palo Alto Networks. The diaspora's pride has been real, but it has always come with an asterisk: these are Indians running other people's companies.

Something quietly different happened at the G7 summit in Evian, France, on Wednesday.

When world leaders sat down for a working lunch on the future of AI and the digital economy, the invited technology executives were a who's-who of the frontier: OpenAI's Sam Altman, Google DeepMind's Demis Hassabis, Anthropic's Dario Amodei, Meta's Alexandr Wang, Mistral's Arthur Mensch, Cohere's Aidan Gomez. And one Indian company — Sarvam AI, represented by co-founder Pratyush Kumar.

Sarvam was the only Indian firm in the room.

### Why that sentence matters

Read the guest list again. Every other company there is American, French or Canadian. The session was attended by U.S. President Donald Trump alongside Emmanuel Macron, Keir Starmer, Friedrich Merz, Giorgia Meloni, Sanae Takaichi and Mark Carney, plus the EU's Antonio Costa and Ursula von der Leyen. This was the table where the people who write AI policy talk to the people who build AI.

For India to have a seat — not through a diaspora CEO of a Western giant, but through an Indian-founded, Bengaluru-based company — is a genuine first. And the company holding it is barely two years old.

Sarvam was founded by former AI4Bharat researchers Vivek Raghavan and Pratyush Kumar. This week it became India's newest AI unicorn, raising $234 million in the first close of a planned $300 million Series B at a $1.5 billion valuation. HCLTech led with $150 million for a 10.5% stake — the largest bet an Indian IT services major has ever made on a homegrown foundation-model company. Bessemer joined; Khosla Ventures and Peak XV followed on.

### The timing is the message

The Evian invitation came days after a U.S. export order briefly cut Indian users off from Anthropic's most capable models — a vivid demonstration that access to frontier AI can be revoked by a government an ocean away. India's argument, made repeatedly this month, is that access is not ownership. Sarvam's presence at the G7 table, alongside the very labs whose models were just restricted, was the cleanest possible statement of that case.

It is also a recognition by the G7's own members that AI governance written without the global South is governance with a hole in it. India is the world's largest country, a vast market, and increasingly a producer rather than merely a consumer of AI. Leaving it out of the room had become untenable.

### What it means for the diaspora

For Indian Americans, the shift is psychological as much as strategic. The community has spent years celebrating its executives — the Pichais and Nadellas held up at every family gathering and every Macron speech as proof of what Indians can do. That pride is earned. But it is the pride of a talented workforce, not of an industry India owns.

A homegrown company at the G7 table points to a different future: one where the diaspora's engineers and capital flow not only into Silicon Valley's giants but back into Indian companies competing at the frontier on their own terms. Sarvam plans to launch its agentic AI stack next month and a dedicated voice-AI stack soon after. If it delivers, the next NRI engineer weighing a return to Bengaluru is not choosing between a Western salary and a patriotic pay cut — she is choosing between two genuine frontiers.

### The sober footnote

Symbolism is not capability. The frontier labs at that lunch are shipping models that complete multi-hour agentic tasks; Sarvam is raising the money to begin competing on exactly that terrain. A seat at the table is an invitation, not a victory. India's models still have to close a gap measured in research years, not press releases.

But invitations precede arrivals. For a diaspora long accustomed to running the West's companies, watching India send its own to the G7 table is a small, genuine turning of the page.
"""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
