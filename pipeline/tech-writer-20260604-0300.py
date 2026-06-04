#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 03:00 UTC run"""

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

def verify_image(url):
    """Verify image URL returns 200 and is > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image OK: {url[:80]}... ({cl} bytes)")
            return True
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(6000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  ✓ Image OK (via GET): {url[:80]}... ({len(chunk)}+ bytes)")
            return True
    except Exception as e:
        print(f"  ✗ Image check failed: {e}")
    return False

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────
# ARTICLE 1: NVIDIA H-1B Hiring Surge
# ──────────────────────────────────────────────

art1_body = """Jensen Huang's NVIDIA secured certification for roughly 1,200 H-1B visa positions during the first two quarters of fiscal 2026, a 20 per cent increase over the same period a year earlier. In any other hiring cycle, that would be a routine data point. In this one, it is an outlier that says more about the rest of Silicon Valley than it does about NVIDIA.

Google's approved H-1B hires fell from approximately 5,100 to 2,200 over the identical window — a drop of nearly 57 per cent. Amazon's approvals declined from about 6,100 to 4,300. Meta, which slashed thousands of jobs in its "year of efficiency" and never fully reversed course, has similarly pulled back from foreign recruitment. The pattern is unmistakable: the companies that built their engineering cultures on immigrant talent are now spending less to sustain them.

For the roughly 71 to 73 per cent of H-1B visa holders who are Indian nationals, the divergence is not academic. Under current immigration rules, most H-1B workers who lose a job have 60 days to find a new sponsor or leave the country. When the employer cutting headcount is also the employer most likely to sponsor a visa, the 60-day clock becomes less a safety net and more a countdown.

## Where NVIDIA's money goes

NVIDIA is not merely hiring more foreign workers; it is paying them at rates that place it at the top of the H-1B wage distribution. Federal filings show base salaries for Principal Research Scientists ranging from $272,000 to $431,250, while Architecture Directors can earn up to $488,750 — before stock and bonuses. Huang has said publicly that he "personally reviews everybody's compensation" and considers global talent acquisition essential to what he calls the "AI Agent Era."

These pay bands matter more than they once did. Under a final USCIS rule that took effect on 27 February 2026, the H-1B lottery now weights applications by wage level. A Wage Level IV role — the kind NVIDIA overwhelmingly sponsors — has four times the selection probability of a Wage Level I position. The rule was designed to prioritise highly skilled, highly paid workers. It has, in practice, created a system in which companies that pay the most get the most visas.

## The $100,000 question

The wage-weighted lottery is only one half of a structural shift. A supplemental $100,000 processing fee, introduced under the Trump administration's immigration overhaul, allows applicants to have their cases adjudicated within 15 days rather than the standard 7.5-month timeline. DHS Secretary Markwayne Mullin testified before the Senate Appropriations Subcommittee on 2 June that more than 200,000 of the 286,000 H-1B applications received in fiscal year 2026 opted for the expedited track — a figure that implies roughly $20 billion in fee revenue from a single visa category.

For Indian tech workers, the implications cut both ways. Those employed at well-capitalised firms like NVIDIA face no obstacles: the company covers visa costs and the premium processing fee is a rounding error on a $400,000 salary. But for workers at mid-tier IT services firms, consulting shops, or startups, the $100,000 fee is prohibitive. The system is bifurcating. At the top, visa sponsorship is more accessible than ever. Below that tier, it is becoming quietly unaffordable.

## What this means for Indian professionals

The H-1B programme has long functioned as the primary gateway for Indian engineering talent into the American technology sector. The new economics of that gateway — weighted lotteries, six-figure processing fees, and a shrinking pool of sponsors — are reshaping who gets through and on whose terms.

NVIDIA's expansion is real, but it is also narrow. The company employs roughly 30,000 people globally. Google, Amazon, and Meta collectively employ more than 500,000. When the larger employers retreat from foreign hiring, NVIDIA's 200 additional visa certifications do not fill the gap. They merely illustrate how concentrated the demand for elite AI talent has become — and how exposed everyone else is to a system that increasingly rewards scale and salary above all else."""

art1_image = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg"

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA Is Hiring 20 Per Cent More H-1B Workers. Google and Amazon Are Cutting Theirs.",
    "subheadline": "As 200,000 applicants pay $100,000 each for faster visa processing, the H-1B system is splitting into two tiers — and Indian tech workers are on both sides of the divide.",
    "slug": make_slug("nvidia-h1b-hiring-google-amazon-retreat-indian-workers"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "Indians hold 71-73% of H-1B visas. NVIDIA's hiring surge benefits elite AI engineers while the $100K processing fee and shrinking sponsor pool squeeze mid-tier Indian workers at IT services firms.",
    "tags": ["h-1b", "nvidia", "immigration", "indian-tech-workers", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Business Insider / NDTV", "url": "https://www.ndtv.com"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com"},
        {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com"},
        {"name": "The Hindu BusinessLine (DHS testimony)", "url": "https://www.thehindubusinessline.com"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": art1_image,
    "body": art1_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 2: Sarvam AI Voice Platform
# ──────────────────────────────────────────────

art2_body = """Sarvam AI, the Bengaluru-based startup that has built India's most commercially successful voice AI stack, is preparing to open its conversational agents platform to the general public. Until now, Sarvam Samvaad — the company's voice AI product — has been available only to enterprises willing to navigate a waitlist and commit to high conversation volumes. That is about to change.

Sources familiar with the plans told Inc42 that Sarvam will replace its enterprise-only onboarding with a self-serve platform where any business, developer, or individual can sign up, receive free credits, and begin deploying voice AI agents without a procurement cycle. A freemium tier with usage limits is under consideration, with paid plans for unrestricted access. The pricing model is still being finalised, but the direction is clear: Sarvam wants the long tail.

## Voice, not text, is the revenue engine

The shift matters because voice AI has become the company's primary commercial anchor. While Sarvam initially attracted attention for its Indic-language foundation models — a 2-billion-parameter model trained on four trillion tokens across ten Indian languages — the business reality has tilted decisively toward its voice agent stack. According to Inc42, voice agents now contribute roughly 80 per cent of Sarvam's current $12 million annual recurring revenue.

The product handles what text chatbots cannot in India: genuine multilingual customer interactions over the phone, in WhatsApp, and within apps. Tata Capital, one of Sarvam's anchor clients, uses the platform for multilingual loan servicing. Sri Mandir, a religious content startup, processes payments through Sarvam's voice agents — more than 270,000 transactions to date. In a country where 22 official languages and 19,000 dialects make keyboard-based AI impractical for the majority of the population, voice is not a feature. It is the product.

## The unicorn bid

The commercial expansion arrives alongside a reported fundraise that would catapult Sarvam into unicorn territory. The startup is in discussions to raise $250 million from a consortium that includes NVIDIA, existing investor Accel, and HCLTech. If closed at that figure, the round would value Sarvam at over $1 billion, making it India's first dedicated AI-infrastructure unicorn — a distinction that has until now been conspicuously absent from the world's largest pool of AI engineering talent.

The investor mix is telling. NVIDIA's participation signals that Sarvam's voice stack runs on GPU infrastructure that Jensen Huang wants to see proliferate. HCLTech's involvement connects the startup to one of India's largest IT services firms and its global enterprise client base. And Lightspeed investor Hemant Mohapatra recently disclosed that Sarvam plans to open a San Francisco office and pursue global go-to-market ambitions — a move that would pit it directly against ElevenLabs and its ElevenAgents voice AI platform.

## Why NRIs should pay attention

For the Indian diaspora, Sarvam represents a rare species: an Indian AI company building foundational technology rather than assembling someone else's APIs. The founders, IIT alumni Vivek Raghavan and Pratyush Kumar, have built models from scratch rather than fine-tuning Meta's Llama or OpenAI's GPT. The company's Sarvam 2B model and Shuka AudioLM are open-source, trained on synthetic data, and optimised for Indian language patterns that global models handle poorly.

The commercial implications extend to NRI-run businesses with Indian customer bases. A diaspora entrepreneur operating a fintech, healthcare, or education platform that serves users in India can now — or will soon — deploy multilingual voice agents without building the underlying language infrastructure. At a reported price of one rupee per minute of conversation, the unit economics are designed for Indian-scale deployment.

Sarvam's bet is straightforward: in a market of 1.4 billion people where most prefer to speak rather than type, the company that owns the voice layer owns the AI interface. Whether it can hold that position against global competitors with deeper pockets and a San Francisco address will determine whether India's AI story remains one of talent export or becomes one of product export as well."""

art2_image = "https://images.pexels.com/photos/5083215/pexels-photo-5083215.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Sarvam AI Is Opening Its Voice Platform to Everyone. It Wants to Be India's First AI Unicorn.",
    "subheadline": "The Bengaluru startup's voice agents already handle 80% of its revenue. A $250 million raise from NVIDIA and HCLTech would fund the leap from enterprise-only to self-serve — and from India to San Francisco.",
    "slug": make_slug("sarvam-ai-voice-platform-public-unicorn-250m-raise"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "IIT-alumni founded, building from-scratch Indian-language AI models. NRI entrepreneurs can deploy multilingual voice agents for Indian customer bases at ₹1/minute. NVIDIA and HCLTech backing signals global ambitions.",
    "tags": ["sarvam-ai", "indian-startup", "voice-ai", "unicorn", "nvidia"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com"},
        {"name": "TechCrunch", "url": "https://techcrunch.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": art2_image,
    "body": art2_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 3: TSMC CEO Bullish at Shareholders Meeting
# ──────────────────────────────────────────────

art3_body = """TSMC's chief executive C.C. Wei told shareholders on 4 June that the company sees no sign of the AI boom easing. Speaking at the annual shareholders' meeting in Hsinchu, Wei said customers continue to express a positive outlook for AI demand and that adoption is accelerating across consumer, enterprise, and sovereign applications. The statement would have been unremarkable a year ago. In the current climate — with semiconductor valuations stretched, memory prices surging, and data centre capital expenditure approaching a trillion-dollar trajectory — it functions as a stress test of the entire AI supply chain.

TSMC is not a neutral observer in this conversation. It is the conversation. The company manufactures the most advanced chips for NVIDIA, Apple, AMD, Qualcomm, and Anthropic, among others. When Jensen Huang says data centre buildouts could hit $1 trillion by 2028, he is describing a world in which TSMC's factories run at capacity for years. When Intel's Lip-Bu Tan unveils Crescent Island at Computex, he is announcing a chip that will be manufactured on TSMC's process nodes. Even competitors depend on TSMC to compete.

## The numbers behind the confidence

Wei's bullishness is grounded in specific production data. TSMC's 3-nanometre technology accounted for approximately 25 per cent of first-quarter 2026 revenue. The company has entered mass production on its 2-nanometre node and is scaling 3nm capacity simultaneously. In April, TSMC raised its full-year revenue forecast and increased capital spending to meet what it described as "relentless hunger" for advanced chips.

The demand picture is being shaped by a structural shift in how computing power is consumed. AI training runs that once required thousands of GPUs now require tens of thousands. Inference workloads — the computation needed to actually run AI models for end users — are growing even faster as products like Claude, Gemini, and GPT move from research tools to enterprise infrastructure. Anthropic's annualised revenue surged from $10 billion to $47 billion in the first five months of 2026 alone. Every dollar of that revenue translates, eventually, into silicon orders at TSMC's fabs.

The company has also begun charging more for its monopoly position. Reports indicate TSMC has implemented a 15 per cent price increase for 3nm chips, squeezing customers' margins while simultaneously confirming how tight supply remains. When your customers accept a double-digit price hike without switching suppliers, pricing power is not a negotiating tactic — it is a structural advantage.

## What Computex revealed about TSMC's centrality

The week of Wei's shareholder address coincided with Computex 2026 in Taipei, where every major chipmaker paid implicit tribute to TSMC. NVIDIA confirmed that its Vera Rubin platform has entered full production with 150 Taiwanese suppliers powering the ramp. Intel announced Crescent Island, its first dedicated AI GPU — a chip that will sample in the second half of 2026 on TSMC's process technology. AMD showcased new gaming and data centre processors. Qualcomm launched the Snapdragon X2 Elite for mini-PCs. Each announcement, regardless of the company making it, was an announcement about TSMC capacity.

## The India connection

For Indian semiconductor professionals — and there are tens of thousands of them across TSMC's customer base in the United States — Wei's outlook has direct career implications. TSMC's confidence that AI demand will sustain "mid-to-high fifties" compound annual growth rates in AI accelerator revenue through 2029 means that design engineering, verification, and packaging roles at NVIDIA, AMD, Intel, and Qualcomm will remain in demand. The chip shortage is no longer about supply bottlenecks; it is about an industry that cannot build capacity fast enough for a market that keeps expanding.

For India specifically, the implications extend beyond talent. The TRUST initiative between India and the United States, the Tata Electronics fab under construction in Dholera, and Micron's Gujarat facility are all downstream bets on the same demand curve that Wei described to shareholders. If the AI boom sustains as TSMC projects, India's semiconductor ambitions acquire a tailwind. If it stalls, those multi-billion-dollar fabs become expensive monuments to bad timing.

Wei's message to shareholders was, in essence, a message to the entire semiconductor food chain: we are not at the peak. Whether that is confidence or conviction will be tested in the quarters ahead. But TSMC's order book suggests that, for now, the customers writing the cheques agree."""

art3_image = "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "TSMC's C.C. Wei Told Shareholders the AI Boom Shows No Sign of Easing. Every Chipmaker at Computex Proved His Point.",
    "subheadline": "From NVIDIA's Vera Rubin to Intel's Crescent Island, every major chip announcement this week ran through TSMC's fabs. The company raised prices 15 per cent and its customers paid without flinching.",
    "slug": make_slug("tsmc-cc-wei-shareholders-ai-boom-computex-india"),
    "category": "technology",
    "vertical": "technology",
    "is_editorial": False,
    "diaspora_angle": "Tens of thousands of Indian semiconductor professionals across TSMC's customer base (NVIDIA, AMD, Intel, Qualcomm) face sustained demand. India's own fab ambitions (Tata Dholera, Micron Gujarat, TRUST initiative) ride on the same AI demand curve.",
    "tags": ["tsmc", "semiconductors", "ai-boom", "computex-2026", "india-semiconductor"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Barchart / Intel Computex", "url": "https://www.barchart.com"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com"},
        {"name": "MarketBeat / TSMC Analysis", "url": "https://www.marketbeat.com"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": art3_image,
    "body": art3_body.strip()
}


# ──────────────────────────────────────────────
# Verify images and insert articles
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    print(f"\n{'='*60}")
    print(f"Article: {art['headline'][:70]}...")
    print(f"Slug: {art['slug']}")

    # Verify image
    if not verify_image(art["image_url"]):
        print(f"  ⚠ Image verification failed, inserting anyway")

    # Check word count
    words = len(art["body"].split())
    print(f"  Word count: {words}")
    if words < 400:
        print(f"  ✗ SKIPPING: below 400-word minimum")
        continue

    try:
        sb_post("p2_articles", art)
        print(f"  ✅ Published: {art['slug']}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
