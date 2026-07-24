#!/usr/bin/env python3
"""
Tech writer – 2026-06-30 batch (2 articles)
Inserts technology articles into Supabase with status='review'.
"""

import json, os, re, subprocess, sys, uuid
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    """Source a dotenv file into os.environ."""
    if not os.path.exists(path):
        print(f"⚠️  env file not found: {path}")
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"

if not SUPABASE_URL or not SUPABASE_KEY:
    sys.exit("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

# ── image sourcing helpers ───────────────────────────────────────────────────

def fetch_wikipedia_image(name):
    """Get a person/topic image from Wikipedia REST API."""
    slug = name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
    try:
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        if img and "fbcdn" not in img:
            return img
    except Exception as e:
        print(f"  Wikipedia lookup failed for '{name}': {e}")
    return None


def search_commons(query, limit=5):
    """Search Wikimedia Commons for images."""
    url = (
        "https://commons.wikimedia.org/w/api.php"
        f"?action=query&generator=search&gsrnamespace=6&gsrsearch={query}"
        f"&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime"
        f"&iiurlwidth=1200&format=json"
    )
    try:
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        pages = data.get("query", {}).get("pages", {})
        results = []
        for p in pages.values():
            info = (p.get("imageinfo") or [{}])[0]
            thumb = info.get("thumburl") or info.get("url")
            w = info.get("width", 0)
            mime = info.get("mime", "")
            title = p.get("title", "")
            if thumb and "image" in mime and w >= 400:
                # Skip SVGs, logos, flags, icons
                skip_words = ["flag", "logo", "icon", "coat of arms", "seal of", ".svg"]
                if any(sw in title.lower() for sw in skip_words):
                    continue
                results.append({"url": thumb, "title": title, "width": w})
        return results
    except Exception as e:
        print(f"  Commons search failed for '{query}': {e}")
    return []


def search_pexels(query):
    """Search Pexels for a photo."""
    if not PEXELS_API_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=landscape"
    try:
        r = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}", url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            p = photos[0]
            return {
                "url": p["src"]["large2x"],
                "caption": p.get("alt", query),
                "attribution": f"Photo by {p['photographer']} on Pexels"
            }
    except Exception as e:
        print(f"  Pexels search failed for '{query}': {e}")
    return None


def source_image(strategies):
    """Try image strategies in order. Each is (type, query).
    Returns (url, caption, attribution) or (None, None, None)."""
    for strategy_type, query in strategies:
        print(f"  Trying {strategy_type}: {query}")
        if strategy_type == "wikipedia":
            img = fetch_wikipedia_image(query)
            if img:
                return img, f"{query}", f"Wikimedia Commons / Wikipedia"
        elif strategy_type == "commons":
            results = search_commons(query)
            if results:
                best = results[0]
                title_clean = best["title"].replace("File:", "").rsplit(".", 1)[0].replace("_", " ")
                return best["url"], title_clean, "Wikimedia Commons"
        elif strategy_type == "pexels":
            result = search_pexels(query)
            if result:
                return result["url"], result["caption"], result["attribution"]
    return None, None, None


# ── articles ─────────────────────────────────────────────────────────────────

ARTICLES = []

# ── ARTICLE 1: Tata Breach iPhone 18 Pro Escalation ──────────────────────────

ARTICLES.append({
    "id": str(uuid.uuid4()),
    "headline": "The Tata Breach Just Got Worse. iPhone 18 Pro Supplier Maps and Drop-Test Photos Are Now on the Dark Web.",
    "subheadline": "A Reuters review of newly leaked files reveals component-to-supplier maps, confidential Apple watermarks, and factory photographs of unreleased iPhones — escalating what was already India's biggest corporate cyber breach.",
    "slug": "tata-electronics-breach-iphone-18-pro-supplier-maps-dark-web-apple-20260630",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "diaspora_angle": "India's 26% share of global iPhone production rests on Tata's credibility as Apple's newest major assembler. NRI engineers at Apple, TSMC, and Qualcomm face professional fallout as supplier relationships are exposed; investors in Tata Group companies confront a trust deficit with no clear resolution timeline.",
    "tags": ["Tata Electronics", "Apple", "iPhone 18 Pro", "cybersecurity", "data breach", "World Leaks", "India manufacturing", "supply chain", "dark web", "ransomware"],
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
        {"name": "Counterpoint Research", "url": "https://www.counterpointresearch.com/"},
        {"name": "AppleInsider", "url": "https://appleinsider.com/"}
    ]),
    "score_total": 72,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_strategies": [
        ("commons", "iPhone assembly manufacturing"),
        ("commons", "Tata Electronics semiconductor"),
        ("commons", "Apple iPhone factory"),
        ("pexels", "electronics manufacturing circuit board"),
    ],
    "body": """When Tata Electronics acknowledged in early June that ransomware group World Leaks had exfiltrated 630 gigabytes of data from its systems, the company framed the incident as a containable breach. Six files reviewed by Reuters on Sunday suggest it is anything but.

The newly surfaced documents map dozens of components inside Apple's unreleased iPhone 18 Pro models to the specific companies that supply them — chips on the main circuit board, battery elements, camera modules. Several carry Apple's "confidential" watermark and internal codenames consistent with the iPhone 18 Pro generation. Alongside the supplier lists sit photographs of iPhones undergoing drop tests at a Tata plant, dated early 2026, depicting a grey slab-shaped handset with a triple-rear-camera array and the Apple logo.

Apple, according to a person familiar with the matter, considers these details sensitive and is alarmed that documents relating to unreleased models are circulating on the dark web. The data lays bare which suppliers Apple draws on for each part — and where it relies on just a few — exposing both its bargaining leverage and its vulnerabilities.

## Why This Escalation Matters

The earlier tranche of leaked files had already revealed component-design papers for older iPhones, some Tesla parts, and documents belonging to TSMC and Qualcomm. But the new material strikes at the commercial heart of Apple's most guarded product cycle. Supplier allocations for an unreleased device are among the most tightly controlled secrets in consumer electronics; they shape negotiations worth billions and can move the stocks of component makers overnight.

For Apple, the stakes extend beyond intellectual property. The company has spent years cultivating Tata as its newest major assembler, a cornerstone of the broader strategy to shift iPhone production out of China. India is now on track to make 26 per cent of the world's iPhones in 2026, up from just 6 per cent four years ago, according to Counterpoint Research. The breach threatens to erode the trust that underpins that expansion.

Tata Electronics, led by CEO Randhir Thakur — a former Intel and Applied Materials executive recruited specifically to steer the conglomerate's semiconductor and electronics ambitions — has restricted internal access to sensitive systems and hired a global consultant for a forensic audit. But the leaked supplier maps suggest the damage may already be irreversible in scope.

## The Diaspora Dimension

For the estimated tens of thousands of Indian-origin engineers working across Apple's supply chain — at Cupertino, at TSMC's Arizona fab, at Qualcomm's San Diego campus — the breach has professional implications that transcend geography. Supplier relationships they helped build are now public. Internal project codenames they used in daily work have been stripped of their confidentiality.

The fallout also touches India's broader manufacturing credibility. Prime Minister Narendra Modi's "Make in India" electronics push has attracted more than $6 billion in committed semiconductor and electronics investments. Foxconn inaugurated a new Bengaluru iPhone factory just last week and plans to hire 25,000 workers. But those investments rest on the assumption that India can protect the kind of sensitive intellectual property that Apple demands of its partners.

## What Comes Next

World Leaks, which has previously claimed responsibility for a Nike breach, posted the Tata data on the dark web after what security researchers describe as a failed extortion negotiation. Reuters has not been able to verify the full authenticity of the data independently.

Apple and Tata did not respond to Reuters' queries. Neither did World Leaks.

The immediate question is whether the breach changes Apple's calculus on how quickly it funnels more production to Tata. The company already works with Foxconn and Pegatron in India, and diversifying assembler risk within the country would be a logical response. But Tata's vertically integrated pitch — assembling iPhones *and* supplying components — is precisely what made it strategically valuable. A cybersecurity failure at that nexus is harder to ring-fence.

For NRI investors holding Tata Group stocks, the breach compounds an already volatile quarter. Tata Consultancy Services posted its first annual revenue decline in over two decades, while Tata Motors navigates the EV transition. The conglomerate's electronics arm was supposed to be the growth story. Instead, it is now the reputational risk.

The 204,341 files on the dark web are not going anywhere. The question is how many more of them contain information that Apple — and India — cannot afford to have in the open."""
})

# ── ARTICLE 2: Indian IT Year 2 AI Deflation / JP Morgan FY27 Warning ───────

ARTICLES.append({
    "id": str(uuid.uuid4()),
    "headline": "JP Morgan Just Told Indian IT to Brace for Year Two of AI Deflation. The Numbers Are Getting Worse.",
    "subheadline": "A new research note warns that every major Indian IT company faces Q1 FY27 guidance cuts as AI-led pricing erosion enters its second year — and this time, deal closures are stalling too.",
    "slug": "jp-morgan-indian-it-fy27-guidance-cuts-ai-deflation-year-two-20260630",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "diaspora_angle": "Hundreds of thousands of Indian nationals on H-1B visas work at or are subcontracted through these firms; hiring freezes and reduced onsite deployment directly affect visa renewals and green card pipelines. NRI investors hold significant positions in IT stocks that have collectively shed $26 billion in market value this quarter.",
    "tags": ["Indian IT", "JP Morgan", "AI deflation", "TCS", "Infosys", "HCLTech", "Wipro", "FY27", "guidance cut", "H-1B", "enterprise AI"],
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "ICICI Direct Research", "url": "https://www.icicidirect.com/"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/"}
    ]),
    "score_total": 68,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_strategies": [
        ("commons", "Infosys Bangalore campus"),
        ("commons", "Indian IT industry office"),
        ("wikipedia", "Infosys"),
        ("pexels", "software engineers office India"),
    ],
    "body": """The Indian IT services industry has been telling itself a story for three years: the slowdown is cyclical, the AI opportunity is coming, and the sector's 5.9 million employees will ride the next wave just as they rode the last one. JP Morgan's latest research note, released on June 28, suggests that story needs a rewrite.

The bank has cut its Q1 FY27 revenue growth assumptions for every major Indian IT company — TCS, Infosys, HCLTech, Wipro, Tech Mahindra, and LTIMindtree — citing delays in deal closures, slowing revenue conversion, and what it calls "Year 2" of generative-AI deflation. The message is blunt: the headwinds are structural, not seasonal.

"IT services industry has been stuck at 2–3 per cent revenue growth over the last three years," the JP Morgan report states. "With AI deflation in Year 2, we see further headwinds over the next two years. We do not expect large-caps to hit mid-single-digit growth and hover around 3–4 per cent revenue growth."

## The Deflation Arithmetic

The core problem is not that AI is failing Indian IT — it is that AI is succeeding in ways that shrink the traditional billable-hours model. HCLTech became the first major company to quantify the impact, estimating a 3–5 per cent pricing erosion in engagements where AI tools replace manual work. ICICI Direct Research projects that AI-led deflation could run at 2–3 per cent annually for the next two years.

That might sound modest. But for an industry that has been growing at just 2–3 per cent in revenue terms, a 3 per cent pricing headwind effectively zeros out organic growth. The arithmetic is unforgiving: you need to win significantly more work just to stay flat.

The deal pipeline itself is under pressure. JP Morgan attributes this to a confluence of factors: geopolitical uncertainty delaying client decisions, enterprises redirecting budgets from traditional IT services toward AI tokens and cloud spending, and a growing client willingness to use AI tools in-house rather than outsource the work.

TCS reported its first annual revenue decline in more than two decades this spring. Infosys guided FY27 revenue growth at just 1.5–3.5 per cent in constant currency — below even subdued expectations. Accenture's guidance cut last week wiped billions off Indian IT stocks in a single session.

## The Counter-Narrative

The industry is not without ammunition. TCS's AI-related revenue has crossed $2.3 billion, with over 700 active engagements. Infosys won 96 large deals in FY26, including three mega deals, with net-new business representing 55 per cent of total contract value. Nasscom projects that AI could unlock a $300–400 billion incremental addressable market by 2030.

But there is a timing problem. The revenue from AI engagements — building AI platforms, migrating legacy systems, creating agentic workflows — has not yet reached the scale needed to offset the deflation in traditional services. And the transition is cannibalising existing contracts: clients who once paid for 100 engineers to maintain an application now use AI-assisted teams of 30 to do the same work, then ask for a price cut on the renewal.

"The risk is that AI creates new work but also reduces revenue from old work," as one analyst put it. For companies that derive 70 per cent or more of their revenue from application maintenance and support, the maths of that transition is precarious.

## What This Means for the Diaspora

The slowdown ripples directly into the lives of hundreds of thousands of Indian nationals on H-1B visas in the United States. Indian IT firms are among the largest H-1B sponsors; when they freeze hiring or reduce onsite deployment ratios — as multiple companies have signalled — the consequences extend beyond quarterly earnings.

Visa renewals depend on active employment. Green card processing backlogs, already measured in decades for Indian-born applicants, become more fraught when the sponsoring employer is cutting costs. Fresh graduates from IITs and NITs who once treated an offer from TCS or Infosys as a reliable launchpad now face a tighter funnel at the entry level, even as these companies promise to retrain existing staff for AI roles.

For NRI investors, the numbers are stark. The Nifty IT index is the worst-performing sector of 2026, with foreign institutional investors pulling $8.5 billion from IT stocks in calendar 2025 alone — nearly half of total foreign exits from Indian equities that year.

## The Structural Question

The deeper issue is whether the Indian IT model — labour arbitrage at scale, delivered from campuses in Bengaluru, Hyderabad, and Pune — can survive a technology that explicitly reduces the need for labour. Every major company insists the answer is yes, pointing to new AI-services revenue streams and the sheer complexity of enterprise transformations that still require human judgment.

JP Morgan is less certain. Its note implies that mid-single-digit growth, once the floor for the industry, is now the ceiling for the foreseeable future. For a sector that built India's middle class and powered the largest wave of skilled immigration to the United States, that ceiling feels uncomfortably low."""
})


# ── image sourcing + insert ──────────────────────────────────────────────────

def insert_article(article):
    """Source image and insert article into Supabase."""
    strategies = article.pop("image_strategies")
    print(f"\n{'='*60}")
    print(f"📰 {article['headline'][:80]}...")
    print(f"  Slug: {article['slug']}")

    # Source image
    img_url, img_caption, img_attr = source_image(strategies)
    article["image_url"] = img_url
    article["image_caption"] = img_caption
    article["image_attribution"] = img_attr

    if img_url:
        print(f"  ✅ Image: {img_url[:80]}...")
    else:
        print(f"  ⚠️  No image found")

    # Word count check
    words = len(article["body"].split())
    print(f"  📝 Word count: {words}")
    if words < 550 or words > 900:
        print(f"  ⚠️  Word count outside 600-800 range (flexible)")

    # Insert via curl
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-w", "\n%{http_code}",
        "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    output = result.stdout.strip()
    lines = output.split("\n")
    http_code = lines[-1] if lines else "?"
    body = "\n".join(lines[:-1])

    if http_code.startswith("2"):
        print(f"  ✅ Inserted (HTTP {http_code})")
        return True
    else:
        print(f"  ❌ Insert failed (HTTP {http_code})")
        print(f"  Response: {body[:300]}")
        return False


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🚀 Tech Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Articles to insert: {len(ARTICLES)}")

    success = 0
    for article in ARTICLES:
        if insert_article(article):
            success += 1

    print(f"\n{'='*60}")
    print(f"📊 Results: {success}/{len(ARTICLES)} articles inserted successfully")
    if success < len(ARTICLES):
        print(f"⚠️  {len(ARTICLES) - success} article(s) failed")
    else:
        print("✅ All articles inserted!")
