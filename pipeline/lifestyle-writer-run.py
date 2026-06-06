#!/usr/bin/env python3
"""
Videshi Lifestyle & Markets Writer — June 6, 2026 run
Publishes 1 lifestyle-health + 1 markets-finance article.
"""

import requests
import json
import os
import uuid
import io
import subprocess
from datetime import datetime, timezone

# === Load env ===
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# === Image helpers ===

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            # Pick the first landscape photo
            for p in photos:
                src = p.get('src', {})
                url = src.get('large2x') or src.get('large') or src.get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return {
                        'url': url + '?auto=compress&cs=tinysrgb&w=1200',
                        'alt': p.get('alt', query),
                        'photographer': p.get('photographer', 'Pexels')
                    }
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_and_upload_image(image_url, slug):
    """Download image, compress, upload to Supabase storage."""
    try:
        print(f"  Downloading: {image_url[:100]}...")
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get('Content-Type', '')
        if not ct.startswith('image/'):
            print(f"  ⚠ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  Compressed: {size_kb:.0f} KB")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        
        # Try upsert
        resp = requests.put(
            upload_url,
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'image/jpeg',
                'x-upsert': 'true'
            },
            data=compressed,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=SB_HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0].get('id')
        return None
    else:
        print(f"  ⚠ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Ultraprocessed Foods and Dementia (lifestyle-health)
# ============================================================

def write_article_1():
    print("\n=== Article 1: Ultraprocessed Foods & Dementia ===")
    
    slug = "ultraprocessed-foods-58-percent-dementia-risk-harvard-study-south-asian-diet-20260606"
    headline = "Ultraprocessed Foods Raise Your Dementia Risk by 58 Per Cent. Harvard Tracked 5,300 People for a Decade."
    subheadline = "Processed meats are the worst offenders. Whole foods cut risk by 41 per cent. For South Asians abandoning traditional diets, the numbers are a warning."
    
    body = """Your grandmother's kitchen had no ingredient labels because there were no ingredients to list. Turmeric, cumin, ghee, rice, lentils — everything came from a market stall or a pantry shelf. A generation later, many NRI households run on a different fuel: frozen dinners, packaged snacks, instant noodles, sliced deli meats, and sugar-laden cereals. A new Harvard study says the cost of that shift may include your brain.

## The Study

Researchers at Harvard's T.H. Chan School of Public Health followed more than 5,300 American adults aged 50 and older for nearly nine years. They tracked what each person ate, then watched who developed dementia or cognitive impairment, while adjusting for education, income, smoking, physical activity, and alcohol use.

The results, published this week in a special ultraprocessed-food edition of the American Journal of Public Health, are blunt. People who ate the most ultraprocessed foods — roughly a kilogram a day of items like packaged cookies, chips, hot dogs, and frozen meals — had a 58 per cent higher risk of developing dementia and a 46 per cent higher risk of cognitive impairment compared to those who ate the least.

## Processed Meats Are the Worst

When the scientists broke down which ultraprocessed foods did the most damage, processed meats topped the list. Bacon, hot dogs, sliced ham, sausages — the staples of American grab-and-go eating — were independently linked to the highest dementia and cognitive impairment risk.

This is particularly relevant for diaspora Indians who have adopted the American deli-sandwich habit or rely heavily on frozen processed meat products, a dietary pattern that barely existed a generation ago.

## No Safe Level

The study's most unsettling finding is that moderate consumption was not safe either. Even people with middling levels of ultraprocessed food intake had a meaningfully higher risk than those who ate the least.

"Just to say, 'well, I don't eat all my calories from ultraprocessed foods, I'm safe' — it really shows there may not be a safe level," said Cindy W. Leung, associate professor of public health nutrition at Harvard T.H. Chan and a co-author.

## The Flip Side: Whole Foods Protect

The study did not just catalogue risk. It also found that people who ate the most minimally processed whole foods — fresh fruits, vegetables, whole grains, fish, and unprocessed meats — had a 41 per cent lower risk of dementia.

This is where South Asian diets, when eaten in their traditional form, shine. Lentil-based dals, vegetable sabzis, freshly ground spice mixes, chapatis made from whole wheat, and fermented foods like idli and dosa are almost entirely composed of minimally processed ingredients. The protective effect is baked into the cuisine.

## Why These Foods Damage the Brain

Researchers suspect several pathways. Ultraprocessed foods are linked to obesity, Type 2 diabetes, and cardiovascular disease — all known dementia risk factors. But emerging science suggests more direct mechanisms.

Emulsifiers, the additives that give processed foods their smooth texture, can alter the gut microbiome in ways that trigger chronic inflammation. Nitrites, used as preservatives in processed meats, also drive inflammation. And in animal studies, artificial sweeteners like aspartame have been shown to impair learning and memory.

Dr Dariush Mozaffarian, a cardiologist and director of Tufts University's Food Is Medicine Institute, notes that the gut-brain connection is increasingly recognised as central to cognitive health.

## The Diaspora Trap

For NRI families, the pattern is familiar. First-generation immigrants often maintain traditional cooking habits. Their children, raised on American convenience culture, drift toward processed foods. By the third generation, the dal-chawal baseline has been replaced by cereal bars, frozen pizza, and protein shakes.

University of Kansas researchers have found that roughly 70 per cent of the American diet now consists of ultraprocessed foods. If South Asian diaspora households mirror even half of that shift, the cognitive consequences this study describes become directly relevant.

## What You Can Do

The study is observational — it cannot prove that ultraprocessed foods directly cause dementia. But the pattern is consistent across multiple large studies and strong enough to act on.

The practical advice is straightforward: cook more. Use whole ingredients. Read labels and avoid products with ingredients that do not exist in any kitchen — emulsifiers, high-fructose corn syrup, artificial sweeteners, and flavour enhancers.

For South Asian families, the easiest intervention may be the most culturally obvious: go back to basics. Your grandmother's kitchen was not trying to prevent dementia. It was just feeding people real food. It turns out that may be the same thing.

*Sources: American Journal of Public Health, June 2026; Harvard T.H. Chan School of Public Health; Wall Street Journal; CNN*"""

    # Image sourcing
    print("  Sourcing image...")
    
    # Try Wikimedia Commons first
    candidates = []
    commons_results = fetch_wikimedia_commons_images("ultraprocessed food processed meat junk food")
    for r in commons_results[:3]:
        candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
    
    if not commons_results:
        commons_results = fetch_wikimedia_commons_images("processed food supermarket")
        for r in commons_results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
    
    # Pexels fallback
    pexels = fetch_pexels_image("ultraprocessed food packaged snacks grocery store")
    if pexels:
        candidates.append({"url": pexels["url"], "source": "pexels"})
    
    if not candidates:
        pexels = fetch_pexels_image("processed meat deli counter")
        if pexels:
            candidates.append({"url": pexels["url"], "source": "pexels"})
    
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    if candidates:
        best = candidates[0]
        uploaded = download_and_upload_image(best["url"], slug)
        if uploaded:
            image_url = uploaded
            if best["source"] == "wikimedia_commons":
                image_attribution = "Wikimedia Commons"
                image_caption = "Packaged ultraprocessed foods linked to significantly higher dementia risk in a decade-long Harvard study"
            else:
                image_attribution = "Pexels"
                image_caption = "Ultraprocessed packaged foods increasingly dominate American grocery aisles and diaspora kitchen shelves"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "American Journal of Public Health, June 2026",
            "Harvard T.H. Chan School of Public Health",
            "Wall Street Journal",
            "CNN"
        ])
    }
    
    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Article 1 published: {art_id}")
    else:
        print("  ✗ Article 1 failed")
    return art_id


# ============================================================
# ARTICLE 2: SpaceX IPO (markets-finance)
# ============================================================

def write_article_2():
    print("\n=== Article 2: SpaceX IPO ===")
    
    slug = "spacex-ipo-75-billion-largest-ever-spcx-nasdaq-nri-investor-guide-20260606"
    headline = "SpaceX Is About to Become the Largest IPO in History. Here Is What NRI Investors Should Know."
    subheadline = "A $75 billion raise, a $1.75 trillion valuation, and a June 12 Nasdaq debut. The numbers are unprecedented. So are the risks."
    
    body = """Six years ago, Saudi Aramco set the record for the largest public offering in history by raising $25.6 billion. Next week, SpaceX plans to nearly triple it.

Elon Musk's rocket and satellite company has confirmed an IPO price of $135 per share, targeting a raise of approximately $75 billion and a valuation of $1.75 trillion. Trading on the Nasdaq under the ticker SPCX is expected to begin on June 12, following pricing on June 11. More than 21 banks are underwriting the deal, the largest such group ever assembled for a single offering.

If those numbers hold, SpaceX would immediately become the seventh-largest publicly traded company in the United States, surpassing Tesla's current market capitalisation of around $1.6 trillion.

## What SpaceX Actually Is

SpaceX is three businesses inside one company.

The first is rockets. SpaceX has fundamentally lowered the cost of putting payloads into orbit through reusable rocket technology. No competitor is close.

The second is Starlink, a satellite-based broadband internet service with more than 10 million subscribers worldwide. Starlink is already profitable and growing fast. For NRIs with family in rural India or other regions with poor broadband, Starlink's value proposition is tangible — it beams internet from space to areas that terrestrial providers have never reached.

The third is AI. SpaceX's prospectus claims a quantifiable total addressable market of $28.5 trillion, of which a staggering $26.5 trillion is attributed to artificial intelligence opportunities through its Grok AI chatbot and related ventures. This is where the valuation debate gets heated.

## The Bull Case

The rocket business has no real peer. Starlink is profitable and expanding into mobile connectivity, enterprise services, and government contracts. Revenue rose 33 per cent to $18.67 billion in 2025. The company estimates its broadband and mobile connectivity market alone at $1.6 trillion.

SpaceX will also be fast-tracked into the Nasdaq 100 index just 15 trading days after listing, which means index funds that track the Nasdaq 100 will be forced to buy 10 to 15 per cent of outstanding shares. That mandatory passive buying could support the stock in its early weeks.

The IPO is also expected to draw massive retail participation, with up to five per cent of shares reserved for employees and select individuals through a direct share programme.

## The Bear Case

SpaceX posted a net loss of $4.94 billion in 2025. At a $1.75 trillion valuation, the company would trade at roughly 40 times estimated 2026 sales and 175 times EBITDA — multiples that make even the most expensive AI stocks look modest.

Morningstar analysts have valued SpaceX at closer to $780 billion, arguing that the AI business anchoring the premium valuation is unproven. "We don't see Grok as one of the leading AI labs today," one Morningstar analyst concluded, suggesting investors will find opportunities to buy at lower levels after the IPO.

Barron's has been equally cautious, writing that the stock "may be too big to reach escape velocity" and that fair value likely sits "nearer $1 trillion than $2 trillion."

## What This Means for NRI Investors

The SpaceX IPO lands in a complicated market moment. Wall Street just recorded its worst day of the year after a hot May jobs report showed 172,000 jobs added — more than double forecasts — pushing rate hike odds to 70 per cent. The Nasdaq fell 4.2 per cent on Friday, with chip stocks like Nvidia, Broadcom, AMD, and Intel dropping 6 to 15 per cent. The S&P 500's nine-week winning streak ended.

For NRI investors, the calculus involves several factors.

**Access:** Most NRI brokerage accounts with US-based platforms like Schwab, Fidelity, or Interactive Brokers can participate in secondary market trading once SPCX begins trading. IPO allocation is harder — it typically goes to institutional investors and high-net-worth clients of the underwriting banks.

**Tax:** Capital gains on US stocks are subject to US withholding and may also trigger reporting obligations in India under FEMA and DTAA provisions. Consult your CA or CPA before taking a position.

**Concentration risk:** If you already hold Tesla, Alphabet, Meta, or other tech mega-caps, adding SpaceX increases your exposure to a single sector and, in Tesla's case, a single founder. Musk's involvement is both SpaceX's greatest asset and its most unpredictable variable.

**Timing:** With rate hike fears elevated and tech valuations under pressure, the weeks after the IPO may offer better entry points than the first-day pop. Barron's and Morningstar both suggest patience.

## The Bigger Picture

SpaceX is the first of what is expected to be a wave of mega IPOs. Anthropic has already confidentially filed for its own offering. OpenAI is expected to follow. These listings will reshape index composition and sector weightings in ways that affect every diversified portfolio.

The coming week also brings the May CPI report, which will either calm or amplify inflation fears, and Oracle's earnings, which will test whether the AI trade has legs beyond semiconductors.

For NRI investors watching from both sides of the ocean, the SpaceX IPO is not just a stock to buy or skip. It is a signal of where capital markets are heading — and a test of whether the biggest valuation in IPO history can justify itself.

*Sources: Reuters; Wall Street Journal; Barron's; Motley Fool; Ainvest; GlobeNewsWire*"""

    # Image sourcing — SpaceX rocket
    print("  Sourcing image...")
    
    candidates = []
    
    # Wikimedia Commons: SpaceX rocket
    commons_results = fetch_wikimedia_commons_images("SpaceX Falcon rocket launch")
    for r in commons_results[:3]:
        candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
    
    if not commons_results:
        commons_results = fetch_wikimedia_commons_images("SpaceX Starship")
        for r in commons_results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
    
    # Pexels fallback
    pexels = fetch_pexels_image("rocket launch space SpaceX")
    if pexels:
        candidates.append({"url": pexels["url"], "source": "pexels"})
    
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    if candidates:
        best = candidates[0]
        uploaded = download_and_upload_image(best["url"], slug)
        if uploaded:
            image_url = uploaded
            if best["source"] == "wikimedia_commons":
                image_attribution = "Wikimedia Commons"
                image_caption = "A SpaceX Falcon rocket during launch — the company's reusable rocket technology underpins its record-breaking IPO valuation"
            else:
                image_attribution = "Pexels"
                image_caption = "A rocket launch representing SpaceX's historic path to the largest IPO in market history"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "Reuters",
            "Wall Street Journal",
            "Barron's",
            "Motley Fool",
            "Ainvest",
            "GlobeNewsWire"
        ])
    }
    
    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Article 2 published: {art_id}")
    else:
        print("  ✗ Article 2 failed")
    return art_id


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"=== Videshi Lifestyle/Markets Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    id1 = write_article_1()
    id2 = write_article_2()
    
    print(f"\n=== Done ===")
    print(f"  Article 1 (lifestyle-health): {id1}")
    print(f"  Article 2 (markets-finance): {id2}")
