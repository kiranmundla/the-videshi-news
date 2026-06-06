#!/usr/bin/env python3
"""
Videshi Lifestyle & Markets Writer — June 6, 2026 run
Publishes 1 lifestyle-health + 1 markets-finance article.
"""

import requests
import json
import os
import time
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

def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            for p in photos:
                src = p.get('src', {})
                url = src.get('large2x') or src.get('large') or src.get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return {
                        'url': url,
                        'alt': p.get('alt', query),
                        'photographer': p.get('photographer', 'Pexels')
                    }
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images with retry."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    for attempt in range(2):
        try:
            if attempt > 0:
                time.sleep(3)
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
                    print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
                return results
            elif r.status_code == 429:
                print(f"  ⚠ Wikimedia 429 (attempt {attempt+1}), retrying...")
                continue
        except Exception as e:
            print(f"  ⚠ Wikimedia error: {e}")
    return []

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

def download_and_upload_image(image_url, slug, retries=2):
    """Download image, compress, upload to Supabase storage."""
    for attempt in range(retries):
        try:
            if attempt > 0:
                time.sleep(2)
            print(f"  Downloading (attempt {attempt+1}): {image_url[:100]}...")
            # Use curl for downloads to avoid 429/403 issues
            result = subprocess.run(
                ['curl', '-sS', '-L', '-H', f'User-Agent: {UA}', 
                 '--max-time', '20', '-o', '/tmp/videshi_img_dl.jpg', '-w', '%{http_code}', image_url],
                capture_output=True, text=True, timeout=25
            )
            http_code = result.stdout.strip()
            if http_code != '200':
                print(f"  ⚠ Download failed: HTTP {http_code}")
                if http_code == '429' and attempt < retries - 1:
                    continue
                return None
            
            with open('/tmp/videshi_img_dl.jpg', 'rb') as f:
                raw_bytes = f.read()
            
            if len(raw_bytes) < 5000:
                print(f"  ⚠ Image too small: {len(raw_bytes)} bytes")
                return None

            compressed = compress_image(raw_bytes)
            size_kb = len(compressed) / 1024
            print(f"  Compressed: {size_kb:.0f} KB")

            filename = f"{slug}.jpg"
            upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
            
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
                print(f"  ✓ Uploaded to Supabase: {filename}")
                return public_url
            else:
                print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"  ⚠ Download/upload error: {e}")
    return None

def source_image(slug, commons_queries, pexels_queries):
    """Multi-source image search: Wikimedia Commons then Pexels. Returns (url, caption, attribution)."""
    # Try Wikimedia Commons first  
    for query in commons_queries:
        results = fetch_wikimedia_commons_images(query)
        if results:
            for r in results:
                uploaded = download_and_upload_image(r["url"], slug)
                if uploaded:
                    return uploaded, r.get("title", "").replace("File:", ""), "Wikimedia Commons"
            break  # Had results but download failed, try Pexels
        time.sleep(1)
    
    # Pexels fallback
    for query in pexels_queries:
        pexels = fetch_pexels_image(query)
        if pexels:
            # Pexels URLs need compression param
            pexels_url = pexels["url"]
            if '?' not in pexels_url:
                pexels_url += '?auto=compress&cs=tinysrgb&w=1200'
            uploaded = download_and_upload_image(pexels_url, slug)
            if uploaded:
                return uploaded, pexels.get("alt", ""), "Pexels"
    
    return None, "", ""

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
        return "inserted"
    else:
        print(f"  ⚠ Insert failed: {r.status_code} {r.text[:400]}")
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

This is particularly relevant for diaspora Indians who have adopted the American deli-sandwich habit or rely heavily on frozen processed meat products, a dietary pattern that barely existed a generation ago in South Asian households.

## No Safe Level

The study's most unsettling finding is that moderate consumption was not safe either. Even people with middling levels of ultraprocessed food intake had a meaningfully higher risk than those who ate the least.

"Just to say, 'well, I don't eat all my calories from ultraprocessed foods, I'm safe' — it really shows there may not be a safe level," said Cindy W. Leung, associate professor of public health nutrition at Harvard T.H. Chan and a co-author of the study.

## The Flip Side: Whole Foods Protect

The study did not just catalogue risk. It also found that people who ate the most minimally processed whole foods — fresh fruits, vegetables, whole grains, fish, and unprocessed meats — had a 41 per cent lower risk of dementia.

This is where South Asian diets, when eaten in their traditional form, shine. Lentil-based dals, vegetable sabzis, freshly ground spice mixes, chapatis made from whole wheat, and fermented foods like idli and dosa are almost entirely composed of minimally processed ingredients. The protective effect is baked into the cuisine itself.

## Why These Foods Damage the Brain

Researchers suspect several pathways. Ultraprocessed foods are linked to obesity, Type 2 diabetes, and cardiovascular disease — all known dementia risk factors. But emerging science suggests more direct mechanisms.

Emulsifiers, the additives that give processed foods their smooth texture, can alter the gut microbiome in ways that trigger chronic inflammation. Nitrites, used as preservatives in processed meats, also drive inflammation. And in animal studies, artificial sweeteners like aspartame have been shown to impair learning and memory.

Dr Dariush Mozaffarian, a cardiologist and director of Tufts University's Food Is Medicine Institute, notes that the gut-brain connection is increasingly recognised as central to cognitive health. The additives in ultraprocessed foods may be disrupting that connection in ways scientists are only beginning to understand.

## The Diaspora Trap

For NRI families, the pattern is familiar. First-generation immigrants often maintain traditional cooking habits. Their children, raised on American convenience culture, drift toward processed foods. By the third generation, the dal-chawal baseline has been replaced by cereal bars, frozen pizza, and protein shakes.

University of Kansas researchers have found that roughly 70 per cent of the American diet now consists of ultraprocessed foods. If South Asian diaspora households mirror even half of that shift, the cognitive consequences this study describes become directly relevant.

Social isolation — another known risk factor — appeared to amplify the association between ultraprocessed food consumption and cognitive impairment, suggesting that elderly NRIs living alone and relying on convenience foods may face compounded risk.

## What You Can Do

The study is observational — it cannot prove that ultraprocessed foods directly cause dementia. But the pattern is consistent across multiple large studies and strong enough to act on.

The practical advice is straightforward: cook more, using whole ingredients. Read labels and avoid products with ingredients that do not exist in any kitchen — emulsifiers, high-fructose corn syrup, artificial sweeteners, and flavour enhancers. Swap processed meats for freshly cooked proteins. Replace packaged snacks with fruits, nuts, and homemade options.

For South Asian families, the easiest intervention may be the most culturally obvious: go back to basics. Your grandmother's kitchen was not trying to prevent dementia. It was just feeding people real food. It turns out that may be the same thing.

*Sources: American Journal of Public Health, June 2026; Harvard T.H. Chan School of Public Health; Wall Street Journal; CNN*"""

    # Image sourcing
    print("  Sourcing image...")
    image_url, _, image_attribution = source_image(
        slug,
        commons_queries=["processed food packaged snacks", "ultraprocessed food"],
        pexels_queries=["processed food grocery aisle", "packaged food supermarket shelves", "junk food processed snacks"]
    )
    
    if not image_url:
        print("  ⚠ No image found, publishing without image")
    
    image_caption = "Ultraprocessed packaged foods increasingly dominate grocery aisles — and diaspora kitchen shelves" if image_url else ""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "lifestyle-health",
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

The first is rockets. SpaceX has fundamentally lowered the cost of putting payloads into orbit through reusable rocket technology. No competitor comes close to matching its launch cadence or cost structure.

The second is Starlink, a satellite-based broadband internet service with more than 10 million subscribers worldwide. Starlink is already profitable and growing fast. For NRIs with family in rural India or other regions with limited broadband access, Starlink's value proposition is real — it beams internet from space to areas that terrestrial providers have never reached.

The third is AI. SpaceX's prospectus claims a total addressable market of $28.5 trillion, of which a staggering $26.5 trillion is attributed to artificial intelligence opportunities through Grok, its AI chatbot, and related infrastructure ventures. This is where the valuation debate gets heated.

## The Bull Case

The rocket business has no real peer. Starlink is profitable and expanding into mobile connectivity, enterprise services, and government contracts. Revenue rose 33 per cent to $18.67 billion in 2025.

SpaceX will also be fast-tracked into the Nasdaq 100 index just 15 trading days after listing. Index funds tracking the Nasdaq 100 will be forced to buy 10 to 15 per cent of outstanding shares — mandatory passive buying that could support the stock in its early weeks.

Up to five per cent of IPO shares are reserved for employees and select individuals through a direct share programme, and the offering is expected to draw massive retail participation.

## The Bear Case

SpaceX posted a net loss of $4.94 billion in 2025. At a $1.75 trillion valuation, the company would trade at roughly 40 times estimated 2026 sales and 175 times EBITDA — multiples that make even the most expensive AI stocks look modest by comparison.

Morningstar analysts have valued SpaceX at closer to $780 billion, arguing that the AI business anchoring the premium valuation is unproven. "We don't see Grok as one of the leading AI labs today," one Morningstar analyst concluded, suggesting investors will find opportunities to buy at more attractive levels after the IPO.

Barron's has been equally cautious, writing that the stock "may be too big to reach escape velocity" and that fair value likely sits "nearer $1 trillion than $2 trillion."

## The Market Backdrop

The IPO lands in a volatile moment. Wall Street just recorded its worst day of 2026 after a hot May jobs report showed 172,000 jobs added — more than double what economists forecast — pushing rate hike odds to 70 per cent for 2026. The Nasdaq fell 4.2 per cent on Friday. Chip stocks including Nvidia, Broadcom, AMD, and Intel dropped 6 to 15 per cent. The S&P 500's nine-week winning streak came to an abrupt end.

Oil is trading near $93 a barrel amid the Iran conflict. Bitcoin has slid below $62,000. The 10-year Treasury yield has pushed past 4.5 per cent. This is the environment into which SpaceX will price itself.

## What NRI Investors Should Consider

**Access.** Most NRI brokerage accounts with US-based platforms like Schwab, Fidelity, or Interactive Brokers can participate once SPCX begins trading on the secondary market. IPO allocation is harder to get — it typically goes to institutional investors and high-net-worth clients of the 21 underwriting banks, led by Goldman Sachs, Morgan Stanley, and J.P. Morgan.

**Tax implications.** Capital gains on US stocks may be subject to US withholding and could trigger reporting obligations in India under FEMA and the Double Taxation Avoidance Agreement. NRIs holding SPCX should consult their chartered accountant or CPA on reporting requirements.

**Concentration risk.** If your portfolio already holds Tesla, Alphabet, Meta, or other tech mega-caps, adding SpaceX increases your exposure to a single sector — and, in Tesla's case, a single founder. Musk's involvement is both SpaceX's greatest asset and its most unpredictable variable.

**Timing.** With rate hike fears elevated and tech valuations under pressure, the weeks after the IPO may offer better entry points than a first-day pop. Both Barron's and Morningstar suggest patience.

## The Bigger Picture

SpaceX is the first of what is expected to be a wave of mega IPOs. Anthropic has confidentially filed for its own US offering. OpenAI is expected to follow. These listings will reshape index composition and sector weightings in ways that affect every diversified portfolio.

The coming week also brings the May CPI report, which will either calm or intensify inflation concerns, and Oracle's earnings, which will test whether the AI trade extends beyond semiconductors. The European Central Bank is also expected to hike rates on Thursday.

For NRI investors watching from both sides of the ocean, the SpaceX IPO is not just a stock to buy or skip. It is a signal of where capital markets are heading — and a test of whether the biggest valuation in IPO history can justify itself in a market that is suddenly less forgiving.

*Sources: Reuters; Wall Street Journal; Barron's; Motley Fool; Ainvest; GlobeNewsWire*"""

    # Image sourcing — SpaceX rocket
    print("  Sourcing image...")
    image_url, _, image_attribution = source_image(
        slug,
        commons_queries=["SpaceX Falcon 9 launch", "SpaceX rocket"],
        pexels_queries=["rocket launch night sky", "space rocket launch pad", "rocket launch flames"]
    )
    
    if not image_url:
        print("  ⚠ No image found, publishing without image")
    
    image_caption = "A SpaceX Falcon rocket during launch — the company's reusable rocket technology underpins its record-breaking IPO valuation" if image_url else ""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "vertical": "markets-finance",
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
    
    print(f"\n=== Summary ===")
    print(f"  Article 1 (lifestyle-health): {id1}")
    print(f"  Article 2 (markets-finance): {id2}")
    results = [id1, id2]
    successes = sum(1 for r in results if r)
    print(f"  {successes}/2 articles published successfully")
