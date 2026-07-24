#!/usr/bin/env python3
"""
Videshi TECHNOLOGY Writer — June 22, 2026 (09:00 UTC run)
3 NEW technology articles (status=review, category=technology):
  1. Broadcom's AI-chip quarter: $10.8B AI revenue (+143% YoY), $100B 2027
     target; CEO Hock Tan; custom ASICs for Google/Anthropic/OpenAI. Diaspora
     angle: Indian engineers at the heart of Broadcom; NRI AVGO holders.
  2. Skyroot's Vikram-1 — India's first private orbital launch, imminent from
     Sriharikota; first space-tech unicorn ($1.1B); Ram Shriram joins board.
  3. L&T spins up LTN Compute under Vyoma.AI as India's data-centre pipeline
     hits 8.33 GW — the sovereign-AI infrastructure race. Diaspora angle:
     where the diaspora's data (and capital) will increasingly live.
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")


load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error: {e}")
    return []


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    return c["url"]
            return commons[0]["url"]
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}); trying curl: {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    r_content = f.read()
                if len(r_content) < 5000:
                    return None
            except Exception:
                return None
        else:
            r_content = r.content
        if len(r_content) < 5000:
            print(f"  \u26a0 Too small: {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        if len(compressed) < 5000:
            return None
        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY
        })
        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ─── Article 1: Broadcom AI-chip quarter ───────────────────────────────────────

def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Broadcom AI-chip surge / Hock Tan")
    print("=" * 60)

    slug = "broadcom-ai-chip-revenue-surge-hock-tan-google-anthropic-openai-20260622"
    headline = "The Other AI Chip Giant: How Broadcom Quietly Built a $56 Billion-a-Year Silicon Machine"
    subheadline = "Broadcom's AI semiconductor revenue jumped 143% to $10.8 billion in a single quarter, and CEO Hock Tan is now guiding to more than $100 billion by 2027. Behind the numbers sits an army of engineers, many of them Indian, designing the custom chips that Google, Anthropic and OpenAI cannot get from Nvidia."

    body = """When investors think about the companies minting money from artificial intelligence, one name dominates the conversation: Nvidia. But a quieter giant in San Jose has spent the past two years assembling a chip business that, on its current trajectory, will rival anything in the industry. In its fiscal second quarter of 2026, Broadcom reported that AI semiconductor revenue had surged 143% from a year earlier to a record $10.8 billion. Total revenue climbed 48% to $22.2 billion, and adjusted earnings before interest, taxes, depreciation and amortisation rose 52% to $15.2 billion — a 69% margin that most hardware companies can only dream of.

The headline figure, though, was a forecast. On the earnings call, chief executive Hock Tan told analysts the company expects AI semiconductor revenue to accelerate to $16 billion in the current quarter, up more than 200% year on year, and to reach roughly $56 billion for the full fiscal year — about 180% higher than 2025. He then reiterated a target that once sounded fanciful: AI chip revenue "in excess of $100 billion" in 2027. Bookings for AI semiconductors in the quarter alone topped $30 billion against the $10.8 billion the company actually shipped, a sign of customer commitments stacking up far ahead of supply.

## The ASIC Bet

Broadcom's edge is not the general-purpose graphics chip that made Nvidia famous. It is the application-specific integrated circuit, or ASIC — silicon designed to do one job extraordinarily well. For years, ASICs were a niche product for video processors and crypto miners. With AI, the calculus changed. Hyperscale customers who know precisely which models they want to run can use a custom accelerator as a scalpel, rather than reaching for the Swiss Army knife of a general-purpose GPU. That means buying only the silicon they will fully use, and burning less power doing it.

That pitch has won Broadcom a roster of six core customers, including Alphabet's Google, Meta, Anthropic and OpenAI. In April, the company signed a long-term agreement with Google to develop and supply multiple generations of its Tensor Processing Units and the networking gear that ties them together. Networking now accounts for nearly 40% of Broadcom's AI revenue — the unglamorous switches and interconnects without which a data centre full of accelerators is just expensive sand.

## Tan's Long Game

Hock Tan, the Malaysian-born, 74-year-old engineer turned dealmaker, has been a rainmaker for two decades. Including dividends, Broadcom's shares are up roughly 34,000% under his stewardship. His early playbook was private-equity-flavoured: buy dominant, mature chip companies, strip costs and raise prices. He later applied the same discipline to enterprise software with the VMware acquisition. In the AI era, that patient consolidation has positioned Broadcom to capture economics across the whole stack — accelerators, networking and software — rather than betting on any single product.

## Why the Diaspora Should Watch

For the Indian diaspora, Broadcom is more than a ticker. The company's design centres in San Jose, Bengaluru and Hyderabad are staffed with thousands of engineers of Indian origin, the chip architects and verification specialists who turn a hyperscaler's specification into working silicon. The custom-ASIC boom is, in a real sense, a story about the value of the deep semiconductor talent the diaspora has built over a generation — the same talent pool India is now racing to expand at home, with the government projecting a need for a million semiconductor professionals by 2032.

There is a portfolio angle, too. AVGO is one of the most widely held single stocks among NRI investors in the United States, a staple of the 401(k) and brokerage accounts of Indian-American professionals who work in or around the technology industry. After a sharp run and a recent pullback to around $411, the question of whether Broadcom can keep beating its own guidance is not academic for them; it is a line item.

Finally, the build-out Broadcom is feeding has a direct line back to India. The data-centre capacity rising across Mumbai, Hyderabad and Chennai will be stuffed with exactly this class of silicon. As India tries to host more of its own AI compute rather than renting it from abroad, the chips designed in San Jose — by engineers who learned their craft in Chennai and Pune — will be among the most consequential imports it buys."""

    wc = len(body.split())
    print(f"  Body word count: {wc}")

    print("  Sourcing image (Pexels semiconductor macro)...")
    img_url = "https://images.pexels.com/photos/6636497/pexels-photo-6636497.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    final_img_url = download_and_compress(img_url, slug)

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": "Custom AI accelerators are the engine of Broadcom's record quarter" if final_img_url else "",
        "image_attribution": "Pexels" if final_img_url else "",
        "sources": json.dumps([
            "The Motley Fool \u2014 Could Broadcom Be the Best Way to Invest in AI Right Now? (June 2026): fiscal Q2 2026 AI semiconductor revenue $10.8B (+143% YoY); consolidated revenue $22.2B (+48%); adjusted EBITDA $15.2B (69% margin); free cash flow $10.3B; Q3 guidance AI revenue $16B (+200% YoY), total $29.4B, operating margin ~67%; partnerships with Google, Anthropic, OpenAI",
            "Zacks.com \u2014 Broadcom Q2 Earnings Call Spotlights AI Demand Surge (June 4, 2026): non-GAAP EPS $2.44 on $22.19B revenue, beating estimates; CEO Hock Tan said AI semiconductor revenue $10.8B (+143% YoY); AI bookings over $30B against $10.8B shipped; Q3 guide $29.4B revenue, $16B AI",
            "Broadcom Q2 2026 Earnings Transcript (The Motley Fool) \u2014 Hock Tan: total revenue record $22.2B (+48%), semiconductor revenue $15B (+79%); networking ~40% of AI revenue; full-year FY2026 AI semiconductor revenue expected $56B (+~180% vs FY2025); reiterated FY2027 AI revenue 'in excess of $100 billion'; April long-term agreement with Google for multiple generations of TPUs and AI networking",
            "Barron's \u2014 Broadcom Holds the Best AI Hand This Side of Nvidia, Thanks to CEO Hock Tan (June 2026): shares up ~34,000% including dividends under Tan; ASIC strategy vs Nvidia general-purpose GPUs; profit projected at $57B for fiscal year through October; MarketBeat: AVGO closing price $411.35 on 06/18/2026"
        ]),
        "diaspora_angle": "Broadcom's custom-chip boom rides on deep semiconductor talent \u2014 much of it Indian, in San Jose, Bengaluru and Hyderabad \u2014 the very talent pool India is racing to expand at home; AVGO is also a staple of NRI investment portfolios, and the silicon it designs will fill India's fast-growing AI data centres.",
        "tags": ["Broadcom", "Hock Tan", "AI chips", "semiconductors", "Nvidia", "Google TPU", "diaspora engineers", "AVGO"],
        "urgency": "medium",
        "score_total": 82,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: Skyroot Vikram-1 ───────────────────────────────────────────────

def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Skyroot Vikram-1 orbital launch")
    print("=" * 60)

    slug = "skyroot-vikram-1-india-first-private-orbital-launch-unicorn-ram-shriram-20260622"
    headline = "India's First Private Rocket Is on the Pad. Its Backers Include an Alphabet Board Member."
    subheadline = "Skyroot Aerospace, founded by two former ISRO engineers, is days away from attempting India's first orbital launch by a private company. A fresh $60 million round has made it the country's first space-tech unicorn — and put Silicon Valley investor Ram Shriram on its board."

    body = """On a launch pad at the Satish Dhawan Space Centre in Sriharikota, a 23-metre rocket named Vikram-1 is being readied for a flight that, if it succeeds, will rewrite the rules of India's space industry. Built by the Hyderabad startup Skyroot Aerospace, it is poised to become the first orbital launch vehicle designed, built and flown by a private Indian company. The launch window is expected to open in June and span about a month, with the rocket set to place multiple small satellites into low-Earth orbit above 400 kilometres.

The timing caps an extraordinary stretch for the eight-year-old company. In May, Skyroot raised about $60 million in a round that valued it at $1.1 billion on a pre-money basis, making it India's first space-tech unicorn. The round was co-led by Sherpalo Ventures and Singapore's GIC, with roughly $10 million in structured debt managed by funds affiliated with BlackRock, and participation from Playbook Partners, Arkam Ventures and the founders of Greenko Group. The valuation more than doubled from the $500 million Skyroot commanded in 2023, a measure of how quickly global capital is warming to India's newly opened private space sector.

## From ISRO to a Garage to the Launch Pad

Skyroot was founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, two engineers who cut their teeth at the Indian Space Research Organisation. Their ambition was to build small-satellite launch rockets broadly comparable to those of American firms like Rocket Lab and Firefly Aerospace — vehicles cheap and nimble enough to offer dedicated rides to orbit on short notice. In 2022, their suborbital Vikram-S became the first privately built Indian rocket to reach space.

Vikram-1 is a far more ambitious machine. A four-stage vehicle standing roughly 23 metres tall, it is built from an all-carbon-composite structure to keep weight down, and its stages — named after the late president and aerospace scientist A.P.J. Abdul Kalam — are powered in part by 3D-printed engines. It can loft up to 350 kilograms to low-Earth orbit, and Skyroot says the design is built for rapid turnaround, with the goal of being assembled and launched within 24 hours. The rocket's components were flagged off from the company's Hyderabad facility earlier this spring, and the most critical pre-flight tests, including a payload fairing separation on flight hardware, have been completed.

## A State Stepping Back, A Sector Stepping Up

The launch is a milestone not just for one company but for a deliberate policy shift. For decades, India's space activity ran almost entirely through ISRO. Reforms over the past few years opened the field to private players, with the regulator IN-SPACe clearing missions and ISRO providing infrastructure and technical oversight. A successful Vikram-1 flight would validate that model, positioning Skyroot to win launch contracts from the Earth-observation and communications-satellite companies that increasingly need affordable, dedicated rides to orbit.

## Why the Diaspora Has a Front-Row Seat

For the Indian diaspora, Skyroot's rise carries an unusually personal charge. One of the round's headline details is that Ram Shriram — the founder of Sherpalo Ventures, an early Google backer and a long-serving member of Alphabet's board — will join Skyroot's board. Shriram is among the most storied Indian-American investors in Silicon Valley, and his presence signals that the Valley's diaspora money, which has long flowed into software, is now placing bets on Indian deep tech and hardware.

That matters because space has historically been the preserve of governments and a handful of Western billionaires. A unicorn built by two ex-ISRO engineers, funded partly by a diaspora investor who helped shape Google, is a different kind of story — one in which India is not merely supplying talent to other people's space programmes but building its own commercial launch industry from the ground up.

There is a strategic dimension as well. As constellations of small satellites become the backbone of communications, navigation and Earth observation, sovereign launch capacity is a form of self-reliance the diaspora's home country has long sought. For NRIs watching from Houston, London or Toronto — many of whom grew up on the romance of ISRO's frugal moonshots — a private Indian rocket reaching orbit would be a moment of pride, and a sign that the next chapter of India's space story will be written as much by founders and venture capital as by government agencies."""

    wc = len(body.split())
    print(f"  Body word count: {wc}")

    print("  Sourcing image (Commons rocket / fallback Pexels launch)...")
    img_url = pick_commons([
        "Skyroot Aerospace Vikram rocket",
        "Satish Dhawan Space Centre launch",
        "rocket launch India ISRO"
    ])
    img_caption = "A private orbital rocket on the pad: India's space sector opens to startups"
    img_attribution = "Wikimedia Commons"
    final_img_url = download_and_compress(img_url, slug) if img_url else None
    if not final_img_url:
        img_url = "https://images.pexels.com/photos/796206/pexels-photo-796206.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
        final_img_url = download_and_compress(img_url, slug)
        img_caption = "A rocket lifts off; Skyroot aims to be India's first private firm to reach orbit"
        img_attribution = "Pexels"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "TechCrunch \u2014 India's first space tech unicorn emerges as Skyroot gears up for orbital launch: $60M round, $1.1B pre-money valuation, co-led by Sherpalo Ventures and GIC, ~$10M structured debt via BlackRock-affiliated funds; founders Pawan Kumar Chandana and Naga Bharath Daka (ex-ISRO, founded 2018); Vikram-1 flagged off to Sriharikota in April, targeting June launch; 350kg to LEO; Ram Shriram (Sherpalo founder, Alphabet board member) to join Skyroot board; valuation up from $500M in 2023",
            "AInvest \u2014 Skyroot Aerospace Prepares for Maiden Launch of Vikram-1 Orbital Rocket: launch window expected to open June 2026 and span a month; payloads into LEO above 400km; mission cleared by IN-SPACe with ISRO technical oversight; multi-stage vehicle, carbon composite, 3D-printed engines",
            "The Hindu BusinessLine \u2014 Vikram-1 nose cone heads to Sriharikota launch pad: 23-m rocket; all-carbon composite structure; high-thrust solid boosters; 3D-printed engine; stages named after A.P.J. Abdul Kalam; Telangana CM flagged off nose-cone transport; India's first private orbital launch attempt",
            "TechStory / Behind The Black \u2014 Skyroot completes Vikram-1 fairing separation test (April 8) on flight hardware; Vikram-S suborbital flight (Nov 18, 2022) was first privately built Indian rocket to reach space; success would let Skyroot compete with Rocket Lab's Electron for smallsat contracts"
        ]),
        "diaspora_angle": "Skyroot's leap from ISRO garage to unicorn is backed in part by Ram Shriram, the diaspora investor who helped build Google and now sits on Alphabet's board \u2014 a signal that Silicon Valley's Indian-American capital is moving into Indian deep tech, and a moment of pride for NRIs raised on ISRO's frugal moonshots.",
        "tags": ["Skyroot Aerospace", "Vikram-1", "space tech", "ISRO", "Ram Shriram", "startup unicorn", "Sriharikota", "private space"],
        "urgency": "high",
        "score_total": 84,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 3: L&T / Vyoma.AI and India's data-centre race ────────────────────

def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: L&T LTN Compute / India data-centre pipeline")
    print("=" * 60)

    slug = "lt-vyoma-ltn-compute-india-sovereign-ai-data-centre-pipeline-8gw-20260622"
    headline = "A Construction Giant Wants to Be India's AI Landlord. It Just Built Another Company to Do It."
    subheadline = "Larsen & Toubro has quietly spun up a new compute subsidiary under its Vyoma.AI arm, as India's data-centre pipeline balloons to 8.33 gigawatts. The race to host the country's artificial intelligence — rather than rent it from abroad — is now a contest among India's biggest names."

    body = """Over the weekend, Larsen & Toubro filed a brief notice with India's stock exchanges that was easy to overlook: it had incorporated a step-down subsidiary, LTN Compute Private Limited, "for the purpose of establishing data centres and AI infrastructure." The new company is wholly owned by Vyoma.AI Limited, itself a subsidiary L&T created only in April. The capital figures are small for now. The ambition behind them is not.

L&T is best known as the engineering conglomerate that builds India's bridges, metros, refineries and defence systems. Over the past year it has been methodically reinventing itself as something else as well: a builder and operator of the physical infrastructure on which artificial intelligence runs. Vyoma is pitched as a "next-generation sovereign AI cloud and digital infrastructure platform," combining L&T's construction and engineering muscle with hyperscale cloud engineering, GPU computing and the management of advanced AI workloads. In February, the company partnered with the American chipmaker Nvidia to build gigawatt-scale AI data-centre infrastructure in India, marrying L&T's engineering with Nvidia's AI stack.

## The 8.33-Gigawatt Question

L&T's move lands amid a build-out without precedent in India. According to Knight Frank India, the country's total data-centre development pipeline has reached 8.33 gigawatts — more than five times its current live capacity of about 1.6 GW. Of that pipeline, 0.32 GW is under construction, 2.92 GW has reached the committed stage, and a striking 5.41 GW sits in early-stage development, nearly two-thirds of the total. The drivers are familiar: an explosion in AI adoption, the relentless growth of cloud computing, and data-localisation rules that increasingly require Indian data to be stored on Indian soil.

The geography is specialising. Mumbai anchors hyperscale deployments thanks to its connectivity and subsea-cable landings; Hyderabad is emerging as a preferred destination for AI-specific infrastructure; Chennai is positioning itself as a gateway for international data traffic; and Visakhapatnam has become one of India's most active greenfield markets, attracting gigawatt-scale proposals. L&T Vyoma has already broken ground on a 40 MW green, AI-ready facility at Mahape in Navi Mumbai, part of a plan to scale beyond 200 MW across Mumbai, Chennai, Bengaluru and Hyderabad, with a stated goal of capturing 10% of India's data-centre market by 2030.

## Power, Not Demand, Is the Bottleneck

The constraint is no longer whether customers will come. It is whether the electricity will. Analysts note that the real chokepoint for India's data-centre ambitions is the slow delivery of power infrastructure — grid connections, substations and local supply that lag the breakneck pace of announced projects. New capacity added since January was reportedly down even as demand stayed strong. Globally, AI already accounts for roughly a fifth of data-centre electricity use, and that demand is projected to double by 2030. India's planned spending of more than $50 billion across data centres, cloud and AI ecosystems will be tested against the harder reality of megawatts on the ground.

## What It Means for the Diaspora

For the Indian diaspora, the data-centre race is more consequential than its dry vocabulary suggests. Every time an NRI in New Jersey video-calls family in Pune, streams an Indian web series, pays a merchant in Mumbai through a digital wallet, or stores photographs in a cloud that, under localisation rules, must increasingly sit inside India, that traffic flows through exactly this infrastructure. As more of India's digital life is required to live on home soil, who builds and controls that capacity becomes a question of both economics and sovereignty.

There is an investment angle too. L&T is a blue-chip staple of Indian equity portfolios, including those of NRIs who allocate to India through mutual funds and direct holdings; its pivot from cyclical construction toward recurring data-centre and cloud revenue is the kind of re-rating story that draws diaspora capital. And the "sovereign AI" framing — the idea that India should host and govern its own compute rather than renting it from foreign hyperscalers — speaks to a generation of diaspora technologists who have spent their careers inside those same American cloud giants and now watch their ancestral country try to build an alternative.

L&T's tiny new subsidiary, in other words, is a marker in a much larger contest. Reliance, Adani, global players like RMZ and Colt, and a clutch of specialists are all racing to pour concrete and lay fibre for the AI age. The winners will become the landlords of India's digital economy — and the diaspora, whether it realises it or not, will be among their most frequent tenants."""

    wc = len(body.split())
    print(f"  Body word count: {wc}")

    print("  Sourcing image (Pexels data-centre servers)...")
    img_url = "https://images.pexels.com/photos/17489160/pexels-photo-17489160.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    final_img_url = download_and_compress(img_url, slug)

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": "Server racks: India's data-centre pipeline has reached 8.33 gigawatts" if final_img_url else "",
        "image_attribution": "Pexels" if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine \u2014 L&T sets up subsidiary for AI compute infrastructure (June 21, 2026): step-down subsidiary LTN Compute Private Limited formed 'for establishing data centres and AI Infra'; authorised share capital \u20b91 lakh; wholly owned by L&T subsidiary Vyoma.AI Limited",
            "Inc42 \u2014 L&T Incorporates AI Data Centre Subsidiary Vyoma.AI: Vyoma.AI launched April 22, authorised capital \u20b95 lakh, 100% owned by L&T; positioned as a next-generation sovereign AI cloud and digital infrastructure platform (hyperscale cloud engineering, GPU computing, advanced AI workloads); February partnership with Nvidia for gigawatt-scale AI data-centre infrastructure in India",
            "The Hindu BusinessLine / ANI (Knight Frank India) \u2014 India's data centre pipeline reaches 8.33 GW on AI and cloud demand surge (June 20-21, 2026): pipeline more than 5x current 1.6 GW live capacity; 0.32 GW under construction, 2.92 GW committed, 5.41 GW early-stage; Mumbai leads at 3.75 GW, then Hyderabad and Chennai; regional specialisation; Vizag gigawatt-scale greenfield proposals",
            "The Hindu BusinessLine \u2014 L&T Vyoma breaks ground on AI-ready data centre, plans 200 MW capacity expansion: 40 MW green AI-ready data centre at Mahape, Navi Mumbai (part of 100 MW campus); three-pillar strategy (hyperscale, AI-centric/sovereign cloud, colocation/BTS); roadmap >200 MW across Mumbai, Chennai, Bengaluru, Hyderabad; targeting 10% of India's data-centre market by 2030; CEO Seema Ambastha",
            "AInvest \u2014 India's $35 Billion Data Center Bet: power access, not demand, is the real constraint; new capacity since January down 11% YoY while demand stays strong; AI ~20% of global data-centre electricity, projected to double by 2030; >$50B planned India spend across data centre, cloud and AI"
        ]),
        "diaspora_angle": "Every NRI video call, streamed show, digital payment and cloud photo bound for India increasingly flows through Indian data centres under data-localisation rules \u2014 making the L&T-led 'sovereign AI' build-out a question of sovereignty and economics; L&T is also a blue-chip in NRI India portfolios pivoting toward recurring AI-infrastructure revenue.",
        "tags": ["Larsen & Toubro", "Vyoma.AI", "data centres", "sovereign AI", "Nvidia", "cloud computing", "India infrastructure", "AI compute"],
        "urgency": "medium",
        "score_total": 80,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    ids.append(write_article_3())
    print("\n" + "=" * 60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("=" * 60)
