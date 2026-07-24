#!/usr/bin/env python3
"""
The Videshi News Writer — June 11, 2026 (v2)
3 fresh news articles: Opendoor India exit, IT stocks freefall, $3.6T AI IPO pipeline
"""

import os, json, sys, io, subprocess
import requests
from datetime import datetime, timezone
from PIL import Image

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.replace('export ', '').strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
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
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    try:
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image: {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            raw = r.content
            if len(raw) < 5000:
                print(f"  ⚠ Image too small: {len(raw)} bytes")
                return None
            compressed = compress_image(raw)
            print(f"  ✓ Downloaded & compressed: {len(raw)} -> {len(compressed)} bytes")
            return compressed
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {filename}")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
        return None

def source_image(searches_wiki_person=None, searches_commons=None, searches_pexels=None, slug="img"):
    """Try multiple image sources in priority order. Returns (url, attribution) or (None, None)."""
    # 1. Wikipedia person images
    if searches_wiki_person:
        for name in searches_wiki_person:
            wiki_url = fetch_wikipedia_person_image(name)
            if wiki_url:
                img_bytes = download_image(wiki_url)
                if img_bytes:
                    final = upload_to_supabase(img_bytes, f"{slug}.jpg")
                    if final:
                        return final, "Wikimedia Commons"

    # 2. Wikimedia Commons
    if searches_commons:
        for query in searches_commons:
            results = fetch_wikimedia_commons(query)
            for r in results[:2]:
                img_bytes = download_image(r["url"])
                if img_bytes:
                    final = upload_to_supabase(img_bytes, f"{slug}.jpg")
                    if final:
                        return final, "Wikimedia Commons"

    # 3. Pexels
    if searches_pexels:
        for query in searches_pexels:
            purl = fetch_pexels(query)
            if purl:
                img_bytes = download_image(purl)
                if img_bytes:
                    final = upload_to_supabase(img_bytes, f"{slug}.jpg")
                    if final:
                        return final, "Pexels"

    return None, None


# ══════════════════════════════════════════════
# ARTICLES
# ══════════════════════════════════════════════

ARTICLES = [
    {
        "slug": "opendoor-shuts-india-operations-ai-offshoring-silicon-valley-20260611",
        "headline": "Opendoor Just Shut Its India Operations. Its Stock Jumped 8 Percent.",
        "subheadline": "The home-buying platform says AI-native teams in the US can do what 250 workers in India used to do. Investors and outsourcing analysts say it is the beginning of a much larger shift.",
        "category": "news",
        "image_caption": "A technology campus in Bengaluru, the hub of India's outsourcing industry",
        "image_searches": {
            "commons": ["Bangalore Electronic City technology park", "Bengaluru IT corridor ITPL"],
            "pexels": ["India technology office building modern"]
        },
        "sources": ["TechCrunch", "Reuters", "Stocktwits", "Challenger Gray & Christmas"],
        "body": """Silicon Valley has spent two decades building a vast labour network in India. Opendoor just signalled that AI may be starting to unwind it.

The San Francisco-based home-buying platform announced on Wednesday that it is shutting down its entire India operation, affecting roughly 250 employees across offices in Chennai and Bengaluru. CEO Kaz Nejatian framed the decision as a natural consequence of Opendoor's shift toward smaller, AI-native teams based closer to its American customers.

"For years Opendoor built a large team in India to handle manual workflows across fragmented systems," Nejatian wrote on X. "As we've unified these systems and have hired small AI-native customer-facing teams throughout the US, we need all this operational work to be done in person and close to our customers."

## The Market Loved It

Wall Street's reaction was unambiguous. Opendoor's stock surged 8 percent on the announcement. The message from investors was clear: fewer people, more AI, lower costs.

"After today, Opendoor 2.0 will be a much smaller company by headcount, but a much larger company by impact," Nejatian added.

The company has been shrinking steadily. Securities filings show Opendoor employed 1,042 people globally at the end of 2025, down from 1,470 a year earlier. Its non-US workforce fell from 342 to 184 over the same period.

## A $100 Billion Industry Under Pressure

The closure is modest in absolute terms — 250 jobs at one company. But the reaction it triggered across Silicon Valley suggests something larger is at stake.

India is the world's largest Global Capability Centre market. More than 2,100 centres employ roughly 2.36 million people and generate nearly $100 billion in annual revenue, spanning IT, finance, engineering and R&D for multinational corporations.

The model works because of cost arbitrage: skilled Indian workers cost a fraction of their American counterparts. AI is now eroding that advantage.

"As manual work gets replaced by AI, a lot of jobs will be lost in India," wrote Sheel Mohnot, co-founder of Better Tomorrow Ventures, in response to the announcement. Keshav Lohia of Emergent Ventures called it a "watershed moment" for AI-driven operations.

Phil Fersht, chief executive of HFS Research, which tracks the global outsourcing industry, said the development should not be viewed simply as jobs moving from India to the US. "This is not an isolated restructuring," he told TechCrunch. "It is part of a much broader pattern we are starting to see as companies redesign operations around AI, automation, and much leaner workflows."

Fersht described the emerging model as "Services-as-Software" — companies combining AI, software and a thin layer of human expertise to deliver outcomes without continuously adding headcount.

## What It Means for NRIs and Indian Tech Workers

For the millions of Indians employed in the outsourcing and capability-centre ecosystem, the Opendoor exit is a warning shot. The sector has been India's most reliable employer of English-speaking graduates for over two decades.

The broader data is already shifting. AI accounted for nearly 40 percent of all announced US job cuts in May 2026, up from 7 percent in January, according to outplacement firm Challenger, Gray & Christmas. Technology sector layoffs in the US are running at three times the level of any other industry.

India's own IT giants are feeling the pressure. TCS cut more than 12,000 jobs last year, and its chairman has said the company expects an equal number of employees and AI agents in its workforce. The Nifty IT index has fallen for seven straight sessions, shedding 10.6 percent as fears mount that AI is restructuring the labour-intensive business model that built the $315 billion Indian IT sector.

## The Bigger Question

Opendoor is not the first company to close an India office. It will not be the last. The question is how quickly the economics tip — and whether India's workforce can retool fast enough to stay ahead of the machines that are starting to replace it.

*Sources: TechCrunch, Reuters, Stocktwits, Challenger Gray & Christmas*"""
    },
    {
        "slug": "india-it-stocks-seven-session-freefall-ai-disruption-nifty-20260611",
        "headline": "India's IT Stocks Have Fallen for Seven Straight Sessions. They Have Lost Over 10 Percent.",
        "subheadline": "Anthropic's new tools, Opendoor's India exit, and US inflation at a three-year high are hammering the sector that built modern India's middle class.",
        "category": "news",
        "image_caption": "The Bombay Stock Exchange in Mumbai, where India's IT sector is in a seven-session losing streak",
        "image_searches": {
            "commons": ["Bombay Stock Exchange building Mumbai", "Phiroze Jeejeebhoy Towers BSE"],
            "pexels": ["stock market trading screen financial data"]
        },
        "sources": ["Reuters", "TechCrunch", "Kotak Securities", "Challenger Gray & Christmas"],
        "body": """The Nifty IT index fell 1.6 percent on Thursday, extending a losing streak that has now lasted seven consecutive sessions and wiped out 10.6 percent of its value. For India's $315 billion IT services sector, the damage is no longer abstract. It is on the screen.

The selloff has been driven by a confluence of forces: rising fears that artificial intelligence will displace the labour-intensive outsourcing model, hotter-than-expected US inflation data, and a growing list of companies pulling work out of India entirely.

## A Perfect Storm

Three things hit at once this week.

First, Anthropic's new enterprise tools reignited the debate over whether AI agents can replace the armies of developers and testers that Indian IT firms deploy for their clients. TCS, India's largest IT services exporter, responded by partnering directly with Anthropic and announcing it would equip 50,000 workers with Claude. Its chairman said the company expects to eventually have an equal number of employees and AI agents.

Second, US consumer inflation came in at 4.2 percent for May — the hottest reading in three years, driven in large part by the Iran-war energy shock. The data has raised the spectre of a Federal Reserve rate hike rather than the cuts markets had been hoping for. Higher US rates would mean less spending on the IT outsourcing contracts that account for the bulk of Indian IT revenues.

Third, Opendoor's decision to shut its 250-person India operation and replace the workforce with AI-native teams in the US sent a chill through the sector. Investors cheered; Opendoor's stock jumped 8 percent.

## The Numbers

The Nifty IT index closed at its lowest level since October 2024 on Thursday. The benchmark Nifty 50 fell 0.23 percent to 23,161.6, while the Sensex shed 0.2 percent to 73,832.55. But the IT sector bore the brunt, with twelve of sixteen major sectors logging losses.

Broader markets are also hurting. Small-caps and mid-caps fell 0.7 and 0.8 percent respectively. Private banks were the lone bright spot, rising 0.6 percent on the back of the Reserve Bank of India's decision to offer concessional forex swaps for overseas borrowings and allow leverage on NRI deposits.

Since the Iran war broke out at the end of February, the Nifty 50 and Sensex have fallen 7.8 and 9 percent respectively, with roughly $29 billion in foreign capital leaving Indian markets.

## AI Is Not a Future Problem

"The key concern is that productivity improvements in software engineering are occurring much faster than in non-software domains," said Sumit Pokharna, senior vice president of fundamental research at Kotak Securities.

The fear is not that AI will eventually displace Indian IT workers. It is that it is happening now. According to Challenger, Gray & Christmas, AI accounted for nearly 40 percent of all announced US job cuts in May 2026, up from just 7 percent in January. Technology sector layoffs in the US are running at three times the level of the next most affected industry.

India's largest IT firms are already shrinking headcounts. TCS reported a net reduction of more than 23,000 employees in the fiscal year ended March 2026. Infosys struck its own Anthropic partnership in February. HFS Research has warned that the traditional model of billing by headcount is giving way to what it calls "Services-as-Software."

## What NRIs Should Watch

For NRIs holding Indian IT stocks — among the most popular holdings in diaspora portfolios — the seven-session rout is painful but not yet catastrophic. The IT index has roughly halved from its 2024 peak, and valuations are now at levels not seen since the pandemic.

The question is whether cheap is cheap enough when the business model itself is in question. Bulls argue that firms like TCS and Infosys will become AI-enabled rather than AI-disrupted. Bears say the fat margins of labour arbitrage are gone for good.

The next catalyst is the US Federal Reserve meeting next week. If the Fed signals rate hikes instead of cuts, the pain for Indian IT stocks — and the rupee — will deepen.

*Sources: Reuters, TechCrunch, Kotak Securities, Challenger Gray & Christmas*"""
    },
    {
        "slug": "spacex-openai-anthropic-trillion-dollar-ipo-pipeline-wall-street-20260611",
        "headline": "Three Trillion-Dollar Companies Are About to Hit Wall Street. All Three Are AI.",
        "subheadline": "SpaceX, Anthropic and OpenAI have a combined valuation of $3.6 trillion. Their IPOs will reshape indexes, investor flows and the entire narrative around AI stocks.",
        "category": "news",
        "image_caption": "Anthropic CEO Dario Amodei, whose company is valued at $965 billion ahead of its IPO",
        "image_searches": {
            "wiki_person": ["Dario Amodei", "Sam Altman"],
            "commons": ["Wall Street New York Stock Exchange building", "NYSE trading floor"],
            "pexels": ["Wall Street New York financial district"]
        },
        "sources": ["Reuters", "Bloomberg", "MarketWatch", "CNBC", "The Street", "New York Post"],
        "body": """The largest IPO pipeline in Wall Street history is not coming from banks, energy companies or pharmaceutical giants. It is coming from three AI companies, and their combined valuation exceeds the GDP of the United Kingdom.

SpaceX filed publicly with the SEC on May 20, targeting a $75 billion offering at a valuation of roughly $1.75 trillion — which would make it the largest IPO ever recorded. Anthropic, the company behind the coding assistant Claude Code, filed confidentially on June 1 after raising $65 billion in a funding round that valued it at $965 billion. OpenAI, the maker of ChatGPT, followed on Monday with its own confidential filing, targeting a valuation of up to $1 trillion.

Together, the three companies represent approximately $3.6 trillion in combined market value. According to Bloomberg, that is larger than the entire market capitalisation of every company that went public in 2021, the previous record year for US IPO volume.

## SpaceX Goes First

SpaceX is expected to begin trading this week on the Nasdaq. The company has set aside approximately 30 percent of its shares for retail investors — about $22.5 billion — a far larger allocation than the typical 5 to 10 percent.

But SpaceX is more than a rocket company. Through its merger with Elon Musk's xAI in February, it now bundles Grok, a real-time AI assistant powered by X.com data, alongside its Starlink satellite internet and launch businesses. Analysts at Wedbush have called the listing a "watershed moment" for the AI sector.

The risk, according to SpaceX's own S-1 filing, is that it "cannot predict" when or whether it will become profitable. None of the three companies currently is.

## Anthropic: The $965 Billion Challenger

Anthropic's valuation has skyrocketed on the back of Claude Code and its Mythos-class models, which have become critical tools for enterprise software development. The company released Claude Fable 5 this week — its most capable model yet for general use — with new safety guardrails that redirect dangerous queries to an older model.

The timing is deliberate. Anthropic is positioning itself as the responsible steward of powerful AI, a narrative that is central to its IPO pitch. On Wednesday, the company urged Congress to require safety tests for the most advanced AI models and to modernise unemployment benefit systems in preparation for AI-driven layoffs.

CEO Dario Amodei has drawn both admiration and scepticism for simultaneously warning about AI dangers and pursuing a near-trillion-dollar valuation. The Street noted that the "pause" rhetoric and the IPO filing are not contradictory — they are a strategy. "A credible pause favours whoever gets to define what a responsible pause looks like," it observed.

## OpenAI: The Quiet Filing

OpenAI's confidential filing was more subdued. "It may be a while because there are things we want to do that are likely easier as a private company," the company said. Reuters has reported that it is targeting a valuation of up to $1 trillion, with a debut potentially as early as September.

Goldman Sachs and Morgan Stanley are lead underwriters for both OpenAI and SpaceX. The concentration of advisory firepower in a single season is unprecedented.

Bridgewater's Greg Jensen reportedly told clients that OpenAI's implied 35x forward revenue multiple is "priced for a monopoly outcome that does not yet exist." That framing captures the central tension: these companies are valued on assumptions about AI dominance that have not yet been proven in public financial statements.

## What NRIs and Indian Investors Should Know

For the Indian diaspora — heavily represented in the AI workforce that built these companies — the IPOs carry both personal and financial significance. Indian-origin engineers are among the largest employee and equity-holder groups at all three firms.

The broader market implications are also significant. If $3.6 trillion in AI market value enters public indexes, it will force rebalancing of portfolios worldwide, including India-focused funds. The Nifty IT index, already in freefall, could face further pressure as capital rotates toward direct AI exposure in US markets.

Whether these valuations hold after listing is the trillion-dollar question. History says the first year of mega-IPO ownership tends to underperform broad indexes. But history has never seen three AI companies this large go public in the same quarter.

*Sources: Reuters, Bloomberg, MarketWatch, CNBC, The Street, New York Post*"""
    }
]

# ── Main ──
if __name__ == "__main__":
    print("The Videshi News Writer — June 11, 2026 (v2)")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}\n")

    results = []
    for art_data in ARTICLES:
        slug = art_data["slug"]
        print(f"\n{'='*60}")
        print(f"ARTICLE: {art_data['headline'][:60]}...")
        print(f"{'='*60}")

        # Source image
        searches = art_data.get("image_searches", {})
        img_url, img_attr = source_image(
            searches_wiki_person=searches.get("wiki_person"),
            searches_commons=searches.get("commons"),
            searches_pexels=searches.get("pexels"),
            slug=slug
        )

        if not img_url:
            print("  ⚠ No image sourced — inserting without image")

        article = {
            "headline": art_data["headline"],
            "subheadline": art_data["subheadline"],
            "body": art_data["body"],
            "slug": slug,
            "category": art_data["category"],
            "status": "review",
            "is_editorial": False,
            "image_url": img_url,
            "image_caption": art_data["image_caption"],
            "image_attribution": img_attr or "Wikimedia Commons",
            "sources": json.dumps(art_data["sources"]),
            "published_at": datetime.now(timezone.utc).isoformat()
        }

        art_id = insert_article(article)
        results.append((slug, art_id))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    success = 0
    for slug, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        if art_id:
            success += 1
        print(f"  {slug}: {status}")
    print(f"\n  {success}/{len(results)} articles inserted.")
