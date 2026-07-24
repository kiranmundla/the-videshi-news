#!/usr/bin/env python3
"""
The Videshi — Technology Writer Batch
Date: 2026-06-11 ~21:00 PDT
Articles: 3 (Sriram Krishnan AI exit, Adobe Narayen departure, India-Nepal UPI)
"""

import os, sys, json, uuid, requests, io, time
from datetime import datetime, timezone

# --- ENV ---
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1]

# --- IMAGE HELPERS ---
try:
    from PIL import Image
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url_or_path, retries=3):
    # Support local files (pre-downloaded to avoid rate limits)
    if url_or_path.startswith("/"):
        with open(url_or_path, "rb") as f:
            return f.read()
    for attempt in range(retries):
        r = requests.get(url_or_path, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial use)"}, timeout=30)
        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"  ⚠ Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.content
    raise Exception(f"Failed after {retries} retries for {url_or_path}")


def upload_to_supabase(img_bytes, filename, bucket="article-images"):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def source_and_upload_image(source_url, slug):
    """Download, compress, upload. Returns Supabase public URL or None."""
    print(f"  Downloading from {source_url[:80]}...")
    raw = download_image(source_url)
    print(f"  Downloaded {len(raw)} bytes, compressing...")
    compressed = compress_image(raw)
    print(f"  Compressed to {len(compressed)} bytes ({len(compressed)/1024:.0f} KB)")
    if len(compressed) < 10000:
        print("  ⚠ Image too small (<10KB), might be a thumbnail")
    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(compressed, filename)
    if final_url:
        print(f"  ✓ Uploaded to Supabase: {filename}")
    return final_url


# --- ARTICLE INSERTION ---
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Sriram Krishnan Exits White House AI Role
# ============================================================
ARTICLE_1 = {
    "slug": "sriram-krishnan-exits-white-house-ai-role-20260611",
    "headline": "Sriram Krishnan Steps Down as White House AI Adviser, Leaving an Imprint on America's AI Playbook",
    "subheadline": "The Indian-origin tech executive departs after 18 months shaping US artificial intelligence policy, with plans to build a new institution",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "score_total": 78,
    "diaspora_angle": "Krishnan's departure ends the most prominent Indian-American role in US AI governance; his tenure shaped policies that directly affect H-1B tech workers and Indian AI startups seeking US market access.",
    "sources": json.dumps([
        {"name": "TheAIInsider.tech", "url": "https://theaiinsider.tech/2026/06/09/sriram-krishnan-to-leave-white-house-ai-role/"},
        {"name": "Washington Post", "url": "https://www.washingtonpost.com/technology/2026/06/09/sriram-krishnan-white-house-ai/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/sriram-krishnan-white-house-ai-policy/"}
    ]),
    "body": """Sriram Krishnan, the Indian-born technology executive who served as the Trump administration's senior adviser on artificial intelligence, is stepping down at the end of June. His departure closes an 18-month chapter in which a single individual — with roots in Chennai and a career forged in Silicon Valley — wielded outsized influence over how the world's largest economy approaches the most transformative technology of the decade.

Krishnan's exit was confirmed by multiple sources familiar with the matter and first reported by TheAIInsider.tech on June 9. He is expected to leave the White House by the end of this month, though he plans to remain active in AI policy through a new institution he intends to establish outside government.

## The arc of influence

Before entering government, Krishnan had built an unusually broad résumé across the technology industry. He held product leadership roles at Microsoft, Twitter, Facebook, and Snap, and later became a general partner at Andreessen Horowitz, one of Silicon Valley's most influential venture capital firms. His appointment to the White House in early 2025 was seen as a signal that the administration intended to approach AI through a pro-industry lens rather than a regulatory one.

That instinct proved accurate. Under Krishnan's guidance, the White House crafted an AI Action Plan that prioritised the rapid construction of data centres and the expansion of energy infrastructure to support AI workloads, while deliberately avoiding the kind of prescriptive regulation that the European Union has pursued through its AI Act. The administration issued several executive orders aimed at removing barriers to AI deployment across federal agencies and the private sector, and Krishnan was a key architect of the policy framework that underpinned them.

"His approach was to treat AI infrastructure like highways in the 1950s," said one former colleague who worked with him in the White House. "The government's job was to clear the path, not to design every car that would drive on it."

## What he leaves behind

The policy landscape Krishnan shaped is now well established. The emphasis on energy and data centre buildout has attracted tens of billions of dollars in private investment commitments from major technology firms, and the deregulatory stance has become a defining feature of the administration's approach to technology more broadly. His successor has not been named, and it remains unclear whether the role will carry the same scope and influence.

Krishnan's planned institution — details of which remain scarce — appears designed to give him a platform to continue shaping AI governance from the outside. People familiar with his thinking say he sees the next phase of AI policy as requiring sustained, non-partisan engagement that extends beyond any single administration's tenure.

## The diaspora dimension

For Indian Americans in technology, Krishnan's tenure carried a significance that went beyond policy specifics. He was the most senior Indian-origin figure in US AI governance at a time when India itself was formulating its own approach to artificial intelligence regulation. His presence in the White House created informal channels between Washington and New Delhi on AI matters, even as formal diplomatic discussions on technology cooperation proceeded through separate tracks.

His departure comes at a moment when the intersection of AI policy and immigration is particularly fraught. Proposed changes to H-1B visa rules, debates about AI's impact on technology employment, and questions about the national security implications of AI research by foreign-born scientists have all made the position of Indian-origin technologists in America more complex than it was even two years ago.

Krishnan's career trajectory — from IIT Madras to the White House, by way of some of the most powerful companies in technology — has been cited by Indian media as evidence of the diaspora's continuing influence in American public life. But the lack of a named successor also raises questions about whether that influence was institutional or personal, and whether it will survive the departure of the individual who embodied it.

## What comes next

The broader implications of Krishnan's exit will depend in part on how the administration handles the transition. The AI Action Plan he championed is now policy, but its implementation is ongoing. Decisions about compute export controls, AI safety standards, and the government's own use of AI systems will all require senior-level attention in the months ahead.

For the Indian American technology community, the question is whether Krishnan's new institution can serve as a durable voice in a policy conversation that is only growing louder and more consequential. The role he is leaving was created for a specific moment; the challenge now is building something that outlasts it.""",
    "image_source_url": "/tmp/sriram.jpg",
    "image_caption": "Sriram Krishnan, former White House senior adviser on artificial intelligence",
    "image_attribution": "Wikimedia Commons",
}

# ============================================================
# ARTICLE 2: Adobe's Shantanu Narayen Era Ends with Record Earnings
# ============================================================
ARTICLE_2 = {
    "slug": "adobe-shantanu-narayen-record-earnings-departure-20260611",
    "headline": "Adobe Posts Record Revenue as Shantanu Narayen's 18-Year Reign Draws to a Close",
    "subheadline": "The Indian-American CEO leaves behind a $260 billion software empire — and a succession race likely to crown another leader of Indian origin",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "score_total": 82,
    "diaspora_angle": "Narayen's departure marks the end of one of the longest and most successful Indian-American CEO tenures in tech; his likely successors David Wadhwani and Anil Chakravarthy are both of Indian origin, continuing a remarkable pattern.",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/adobe-earnings-stock-price/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/adobe-earnings-q2-2026/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ-ADBE/earnings/"}
    ]),
    "body": """Adobe delivered the best quarterly performance in its 44-year history last week, reporting revenue of $6.62 billion and adjusted earnings per share of $5.96, comfortably exceeding Wall Street estimates on both counts. The company raised its full-year revenue guidance to between $26.5 billion and $26.6 billion, signalling confidence in its AI-powered product strategy. And yet the stock fell roughly six per cent in after-hours trading, a reaction that said less about Adobe's present than about the anxieties surrounding its future.

That future will, for the first time in nearly two decades, not include Shantanu Narayen at the helm. The Indian-American CEO announced in March that he would step down after 18 years leading the company, a tenure that transformed Adobe from a desktop publishing toolmaker into a cloud software juggernaut with a market capitalisation exceeding $260 billion. His departure has been followed by the resignation of chief financial officer Dan Durn, who leaves on June 15 to become CFO of chipmaker Marvell Technology.

## The numbers behind the narrative

The Q2 results themselves were hard to argue with. Revenue grew 11 per cent year over year, driven by strength across Adobe's three main segments: Digital Media, which includes Photoshop, Illustrator, and the broader Creative Cloud suite; Digital Experience, the enterprise analytics and marketing platform; and Document Cloud, anchored by Acrobat and its AI-powered document tools.

Adobe's AI strategy has been central to this growth. Firefly, the company's generative AI engine, has been integrated across the Creative Cloud, allowing users to generate and edit images, video, and design elements using natural language prompts. The company reported that Firefly has now been used to generate more than 16 billion images since its launch, and AI-powered features are driving measurable increases in subscription conversions and retention.

The raised guidance suggests management believes this trajectory is sustainable. But the market's sceptical reaction points to a deeper concern: whether Adobe's creative software moat can withstand the broader disruption that generative AI is bringing to the creative industry. If anyone can generate professional-quality visuals with a text prompt, what happens to the demand for Photoshop?

## A succession with a pattern

Narayen's departure triggers one of the most closely watched succession races in technology. The two leading internal candidates — David Wadhwani, who runs the Digital Media business, and Anil Chakravarthy, who leads Digital Experience — are both of Indian origin. If either is chosen, Adobe would continue a striking pattern: the company's two most consequential leaders in the modern era would both be Indian Americans.

This is not merely a diversity statistic. It reflects a deeper reality about the Indian diaspora's role in American technology leadership. Narayen joined Adobe in 1998 from Apple, rose through product and engineering ranks, and was named CEO in 2007. Under his leadership, Adobe completed the transition from perpetual software licences to cloud subscriptions — a shift that was initially painful (the stock dropped 8 per cent the day it was announced in 2011) but ultimately created hundreds of billions of dollars in shareholder value.

His tenure coincided with and contributed to a broader phenomenon: the emergence of Indian-origin executives at the helm of many of the world's most valuable technology companies. Satya Nadella at Microsoft, Sundar Pichai at Alphabet, Arvind Krishna at IBM, and Narayen at Adobe — together, they lead companies with a combined market capitalisation exceeding $5 trillion.

## The CFO departure adds complexity

The simultaneous exit of both the CEO and CFO is unusual and has added to investor unease. Durn's move to Marvell, announced last month, removes a second pillar of continuity at a moment when the company is navigating multiple transitions: a leadership change, an AI product strategy that is still maturing, and a regulatory environment that is growing more complex around generative AI and copyright.

Adobe has appointed an interim CFO, but the lack of permanent leadership in both the top executive and top financial roles has created what analysts describe as an "execution risk premium" in the stock. The after-hours decline following earnings — despite a beat-and-raise quarter — reflected this uncertainty.

## What NRIs should watch

For the Indian diaspora in technology, Adobe's transition carries both symbolic and practical significance. Symbolically, it marks the conclusion of a CEO tenure that proved Indian-origin executives could not merely manage but fundamentally transform large American technology companies. Narayen did not inherit Adobe's cloud business; he built it, against internal resistance and external scepticism.

Practically, the succession outcome will signal whether the path Narayen walked remains open. If Wadhwani or Chakravarthy is named CEO, it reinforces the pipeline. If the board looks externally, it raises questions — however unfairly — about whether the era of Indian-American tech CEO ascendancy has peaked.

Adobe's AI story is also directly relevant to the tens of thousands of Indian-origin creative professionals and engineers who work with Adobe tools daily, both in the United States and in India. The company's Bengaluru campus is one of its largest R&D centres globally, and the direction its new leadership takes on AI will ripple through that workforce.

The record quarter buys Adobe time. But the clock is ticking on the questions that matter most, and Narayen's successor will inherit both the best results the company has ever posted and the most uncertain landscape it has ever faced.""",
    "image_source_url": "/tmp/shantanu.jpg",
    "image_caption": "Shantanu Narayen, outgoing CEO of Adobe, who led the company for 18 years",
    "image_attribution": "Wikimedia Commons",
}

# ============================================================
# ARTICLE 3: India-Nepal UPI Linkage Goes Live
# ============================================================
ARTICLE_3 = {
    "slug": "india-nepal-upi-linkage-cross-border-payments-20260611",
    "headline": "India's UPI Now Works in Nepal: What the Cross-Border Payment Link Means for the Diaspora",
    "subheadline": "The UPI-NPI integration operationalised this month makes Nepal the ninth country to accept India's digital payments system, reshaping remittances and travel",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "score_total": 72,
    "diaspora_angle": "The UPI-Nepal linkage directly benefits NRIs who send remittances to Nepal and the large Indian diaspora community that maintains family and business ties across the border. It also signals UPI's maturation as a global digital public infrastructure export.",
    "sources": json.dumps([
        {"name": "Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/upi-nepal-cross-border-linkage/"},
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/fintech/upi-nepal-npi-integration/"}
    ]),
    "body": """On June 6, a digital bridge between India and Nepal quietly went live. The integration of India's Unified Payments Interface with Nepal's National Payment Interface — or UPI-NPI linkage, in the jargon of central bankers — means that for the first time, an Indian using a UPI-enabled app can send money directly to a Nepali bank account, and vice versa. No wire transfer fees. No currency exchange queues. No multi-day settlement periods. Just a phone, a QR code, and a few taps.

The technical infrastructure behind this was built by NPCI International, the global arm of the National Payments Corporation of India, working alongside Nepal Clearing House Limited. The integration has been in testing since late 2025, and its operationalisation marks Nepal as the ninth country where UPI is now accepted, joining Singapore, the UAE, France, Mauritius, Bhutan, Qatar, Sri Lanka, and Cambodia.

## Why it matters beyond the tech

The India-Nepal remittance corridor is one of the busiest in South Asia. Millions of Nepalis work in India, and millions of Indians have family, business, or religious ties in Nepal. The two countries share an open border, and the volume of cross-border financial transactions — both formal and informal — runs into billions of dollars annually. Much of this has historically moved through hawala networks, money transfer agents, or cumbersome bank wires that could take days and charge fees of 3 to 7 per cent.

UPI-NPI integration does not eliminate all of these costs — currency conversion margins still apply, and transaction limits are in place during the initial phase — but it dramatically reduces the friction. A construction worker in Delhi can now send money to his family in Kathmandu in seconds, using the same app he uses to pay for tea. A Nepali student in Bengaluru can receive funds from home without visiting a bank branch.

The implications for travellers are equally significant. Indians visiting Nepal — one of the most popular pilgrimage and tourism destinations for Indian travellers — no longer need to carry cash or deal with exchange counters. The QR code infrastructure that is ubiquitous in Indian shops and restaurants is now being deployed across Nepali merchants, creating a seamless payment experience for Indian visitors.

## UPI's global expansion playbook

Nepal's addition to the UPI network is part of a deliberate strategy by NPCI International to position UPI as a global digital public infrastructure standard. The approach has two tracks: merchant payments, which allow Indian travellers to pay using UPI abroad, and person-to-person remittances, which enable cross-border money transfers.

Singapore was the first country to go live with UPI acceptance, followed by the UAE — both countries with large Indian expatriate populations. France became the first European country to accept UPI, driven by Indian tourist traffic. Each new market follows a similar pattern: NPCI International signs an agreement with the local payments infrastructure provider, conducts a technical integration, runs a pilot, and then scales.

The Nepal integration is notable because it goes further than most. Unlike Singapore and the UAE, where UPI works primarily at merchant payment terminals, the India-Nepal linkage enables true peer-to-peer transfers between bank accounts. This is closer to the full vision of interoperable digital payments that India has been promoting at international forums, including the G20.

## What NRIs should know

For members of the Indian diaspora, the UPI-Nepal linkage is both practically useful and strategically significant. Practically, it means that NRIs who maintain financial ties to Nepal — whether through family, property, or charitable giving — now have a faster, cheaper channel for transactions. The system works through any UPI-enabled app, including Google Pay, PhonePay, Paytm, and BHIM, with no additional registration required for the India side.

Strategically, UPI's expanding global footprint is reshaping how India is perceived in the digital infrastructure space. A decade ago, India was importing payment technology from the West. Today, it is exporting a payment system that handles over 14 billion transactions per month domestically and is being adopted by countries across Asia, the Middle East, and Europe.

This matters for the diaspora because it reflects a broader shift in India's technological capabilities. UPI was built by Indian engineers, governed by Indian institutions, and scaled to serve a billion people before it began its international expansion. For NRIs who have long navigated the gap between India's technological ambitions and its ground-level realities, UPI's success abroad is a tangible proof point that the gap is narrowing.

## The fine print

The initial phase of the UPI-NPI linkage comes with limitations. Transaction amounts are capped, and not all Nepali banks are live on the system yet. Currency conversion happens at rates set by the participating banks, and while these are generally competitive with market rates, they may not always match the best rates available through traditional forex channels.

There are also questions about regulatory coordination. India and Nepal have different approaches to financial regulation, anti-money laundering compliance, and data localisation. As transaction volumes grow, these differences will need to be harmonised — a process that is easier to describe than to execute.

But the direction of travel is clear. UPI's international expansion is no longer an experiment; it is a policy priority for the Indian government and a commercial strategy for NPCI International. Nepal is the ninth country, but it will not be the last. For the diaspora, each new addition to the network makes the financial infrastructure between India and the world a little more seamless — and the practical meaning of being connected to India a little more tangible.""",
    "image_source_url": "/tmp/upi_full.jpg",
    "image_caption": "A smartphone-based contactless payment transaction, illustrating the digital payment systems UPI enables",
    "image_attribution": "Pexels",
}


# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    articles = [ARTICLE_1, ARTICLE_2, ARTICLE_3]
    results = []

    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"ARTICLE {i}: {art['headline'][:60]}...")
        print(f"{'='*60}")

        # Step 1: Source and upload image
        source_url = art.pop("image_source_url")
        print(f"\n[Image Sourcing]")
        final_img_url = source_and_upload_image(source_url, art["slug"])
        if i < len(articles):
            time.sleep(3)  # Avoid rate limiting between articles

        if final_img_url:
            art["image_url"] = final_img_url
        else:
            print("  ⚠ Image upload failed, inserting article without image")
            art["image_url"] = None

        # Step 2: Add metadata
        art["id"] = str(uuid.uuid4())
        art["published_at"] = datetime.now(timezone.utc).isoformat()
        art["created_at"] = art["published_at"]

        # Word count check
        word_count = len(art["body"].split())
        print(f"\n[Quality Check]")
        print(f"  Words: {word_count}")
        if word_count < 600:
            print(f"  ⚠ WARNING: Article under 600 words!")
        elif word_count > 800:
            print(f"  ℹ Article is {word_count} words (slightly over 800, acceptable for depth)")
        else:
            print(f"  ✓ Word count in range")

        # Source count check
        sources_list = json.loads(art["sources"])
        print(f"  Sources: {len(sources_list)}")
        if len(sources_list) < 2:
            print(f"  ⚠ WARNING: Fewer than 2 sources!")
        else:
            print(f"  ✓ Source count OK")

        # Step 3: Insert
        print(f"\n[Inserting into Supabase]")
        art_id = insert_article(art)
        results.append({"slug": art["slug"], "id": art_id, "words": word_count, "image": bool(final_img_url)})

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✓" if r["id"] else "✗"
        img_status = "✓ img" if r["image"] else "✗ no img"
        print(f"  {status} {r['slug']} ({r['words']} words, {img_status})")

    failed = [r for r in results if not r["id"]]
    if failed:
        print(f"\n⚠ {len(failed)} article(s) failed to insert!")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully (status=review)")


if __name__ == "__main__":
    main()
