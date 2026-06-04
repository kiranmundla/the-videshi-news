#!/usr/bin/env python3
"""
Lifestyle-Health + Markets-Finance writer for The Videshi.
Generates 2 lifestyle-health articles and 1 markets-finance article.
"""

import json, os, sys, uuid, requests, io, time, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import subprocess
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
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

def upload_to_supabase_storage(img_url, filename, retry=True):
    """Download image, compress, and upload to Supabase storage."""
    try:
        time.sleep(1)  # Rate limit courtesy
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        compressed_kb = len(compressed) / 1024
        print(f"  Image compressed: {len(r.content)/1024:.0f}KB → {compressed_kb:.0f}KB")

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        up = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def source_best_image(person_names, topic_terms, slug):
    """Multi-source image sourcing: Wikipedia → Wikimedia Commons → Pexels. Tries multiple candidates."""
    candidates = []

    # Source 1: Wikipedia for person articles
    for name in person_names:
        wiki_img = fetch_wikipedia_person_image(name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikimedia_commons", "relevance": "high", "caption_hint": name})
            break

    # Source 2: Wikimedia Commons
    for term in topic_terms:
        commons = fetch_wikimedia_commons_images(term)
        for c in commons[:3]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": "medium", "caption_hint": term})
        if commons:
            break

    # Source 3: Pexels
    for term in topic_terms:
        pexels_img = fetch_pexels_image(term)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": "low", "caption_hint": term})
            break

    if not candidates:
        print("  ⚠ No image candidates found")
        return None, None, None

    # Try each candidate until one uploads successfully
    for best in candidates:
        filename = f"{slug}.jpg"
        final_url = upload_to_supabase_storage(best["url"], filename)
        if final_url:
            attribution = "Wikimedia Commons" if best["source"] == "wikimedia_commons" else "Pexels"
            return final_url, attribution, best.get("caption_hint", "")
        print(f"  Trying next candidate...")
        time.sleep(1)

    print("  ⚠ All image candidates failed")
    return None, None, None


# ============================================================
# ARTICLE 1: Ultra-Processed Foods and Dementia Risk
# ============================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Ultra-Processed Foods and Dementia Risk")
    print("="*60)

    slug = "ultra-processed-foods-dementia-58-percent-risk-harvard-south-asian-diaspora-20260604"
    headline = "Ultra-Processed Foods Raise Dementia Risk by 58 Per Cent. South Asians in the West Are Eating More of Them Than Ever."
    subheadline = "A Harvard-led study of 5,000 older Americans finds processed meats are the biggest driver. The findings land as the Indian diaspora shifts further from traditional diets."

    body = """The largest study to date on ultra-processed foods and cognitive decline has landed a stark finding: older Americans who ate the most ultra-processed foods had a 58 per cent higher risk of developing dementia compared with those who ate the least.

The research, published this week in a special issue of the American Journal of Public Health, tracked more than 5,000 adults over nearly a decade. Led by Dr Heejin Lee and Professor Cindy Leung at Harvard's T.H. Chan School of Public Health, the study found that those with the highest intake also had a 46 per cent higher risk of mild cognitive impairment and a 47 per cent higher risk of either outcome combined.

## Processed Meats Are the Worst Offenders

When researchers broke down the data by food type, processed meats — bacon, hot dogs, deli ham, sausages — emerged as the single biggest contributor to dementia risk. The finding adds to a growing body of evidence that has already linked these products to colorectal cancer and cardiovascular disease.

"These associations held even after we adjusted for things like income, education, and a lot of lifestyle factors like smoking, physical activity, alcohol use, as well as baseline chronic disease risk," Leung said at a press briefing announcing the results.

The results are not limited to heavy consumers. Even moderate intake of ultra-processed foods was associated with elevated risk. "Just to say, 'well, I don't eat all my calories from ultra-processed foods, I'm safe' — it really shows there may not be a safe level," Leung warned.

## Why the Diaspora Should Pay Attention

Ultra-processed foods now account for nearly 70 per cent of what sits on American grocery store shelves. For Indian families who have settled abroad, the dietary shift has been well documented. Traditional home-cooked meals built around fresh vegetables, whole grains, and legumes are gradually being replaced or supplemented by packaged snacks, frozen meals, and sugary drinks — precisely the categories flagged in this research.

A companion study in the same journal issue, led by Cornell University, found that more than 60 per cent of Americans now view ultra-processed foods as addictive and harmful, with perceived risks roughly equivalent to alcohol. The bipartisan consensus has researchers hopeful that policy action could follow.

## The Biology Behind the Risk

Researchers believe the link operates through multiple pathways. Diets high in ultra-processed foods are strongly associated with obesity, Type 2 diabetes, and cardiovascular disease — all of which independently raise dementia risk. South Asians already face a disproportionate burden of these metabolic conditions, often developing them at lower body weights and younger ages than other ethnic groups.

But the ingredients themselves may also play a role. Emulsifiers, high-fructose corn syrup, and artificial additives common in ultra-processed foods have been shown to disrupt gut health and promote chronic inflammation — a process increasingly linked to neurodegeneration.

## What Minimally Processed Foods Can Do

The study also delivered good news. Adults who ate the most minimally processed foods — fresh fruits, vegetables, whole grains, fish, and unprocessed meats — had a 41 per cent lower risk of dementia. That is the kind of traditional diet that many South Asian households still know how to prepare, even if they do so less often.

## The Takeaway for NRI Families

The study does not prove that ultra-processed foods directly cause dementia. Observational research cannot establish that. But the pattern is consistent, the sample is large, and the effect size is substantial. For a diaspora community already at elevated metabolic risk, the findings are a pointed reminder that the convenience of processed food carries a cognitive price that may not reveal itself for decades.

The traditional Indian pantry — dal, sabzi, roti, rice, seasonal fruits — is not just cultural heritage. Increasingly, it looks like a defence against the diseases of Western modernity.

**Sources:** American Journal of Public Health (June 2026, special issue on ultra-processed foods); Harvard T.H. Chan School of Public Health; Cornell University; CNN Health"""

    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr, _ = source_best_image(
        [],
        ["ultra processed food junk food", "processed food snacks packaging", "packaged food grocery store"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "culture",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://ajph.aphapublications.org/",
            "https://www.cnn.com/2026/06/03/health/ultraprocessed-food-scientists-fed-up/",
            "https://news-medical.net/news/20260603/Americans-view-ultraprocessed-foods-as-addictive-and-harmful.aspx"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "Packaged ultra-processed foods on grocery store shelves in the United States",
        "image_attribution": img_attr or ""
    }

    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 2: Processed Meat and Cancer Risk (EPIC Study)
# ============================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Processed Meat and Stomach Cancer Risk")
    print("="*60)

    slug = "processed-meat-stomach-cancer-esophageal-epic-study-south-asian-diet-shift-20260604"
    headline = "One Extra Slice of Deli Meat a Day Raises Stomach Cancer Risk by 9 Per Cent. The Diaspora Diet Is Drifting in the Wrong Direction."
    subheadline = "A 14-year European study of 450,000 people links processed meat to stomach and oesophageal cancers. For NRI families eating more Western food, the data carries a specific warning."

    body = """A single extra serving of processed meat per day — one slice of ham, roughly 30 grams — raises the risk of stomach cancer by 9 per cent and oesophageal cancer by 13 per cent, according to the largest study of its kind ever conducted.

The findings come from the European Prospective Investigation into Cancer and Nutrition, known as EPIC, which tracked the health and diets of 450,112 people across Europe for an average of 14 years. The study included 131,426 men and 318,686 women.

## What the Numbers Show

During the follow-up period, 876 participants developed stomach cancer and 215 developed oesophageal adenocarcinoma — a cancer of the tube connecting the mouth to the stomach. After adjusting for lifestyle factors including smoking, alcohol use, and body weight, the dose-response relationship was clear.

Every additional 30 grams of processed meat per day was associated with:

- A 9 per cent increase in overall stomach cancer risk
- A 13 per cent increase in oesophageal adenocarcinoma risk

White meat did not escape scrutiny either. An extra 20 grams of chicken or turkey per day was linked to a 12 per cent higher risk of cancer in the main body of the stomach.

Researchers separated tumours by location and type — distinguishing between the upper and lower parts of the stomach, and between intestinal-type tumours, which form more organised structures, and diffuse-type tumours, in which cells scatter throughout tissue. The processed meat association was consistent across categories.

## A Dietary Transition in Progress

The EPIC study is European, but its implications travel. Processed meat consumption among Indian diaspora families in the United States, United Kingdom, and Canada has risen sharply over the past two decades. Weekend barbecues, school lunch boxes packed with deli meats, and breakfast routines that include bacon and sausage are now commonplace in NRI households — a departure from traditional vegetarian or semi-vegetarian diets that characterised previous generations.

The World Health Organisation classified processed meat as a Group 1 carcinogen in 2015, placing it alongside tobacco smoke and asbestos in terms of the certainty of evidence. The EPIC study extends that certainty into cancers of the upper digestive tract, where the data had previously been thinner.

## South Asians and Stomach Cancer

India has one of the lower stomach cancer rates globally, partly attributed to dietary patterns rich in vegetables, legumes, and spices with known anti-inflammatory properties. Turmeric, garlic, and ginger — staples of Indian cooking — have all been studied for their potential protective effects against gastrointestinal cancers.

But diaspora populations do not retain those protections automatically. Second and third-generation NRIs who have adopted Western dietary patterns face a risk profile that increasingly resembles the host population. The EPIC findings suggest that processed meat is one of the clearest modifiable risk factors in that transition.

## The Standard Serving Problem

A standard single slice of deli ham averages around 28 grams, according to USDA nutritional databases. That means even one sandwich a day puts a person at the threshold where risk begins to climb measurably. Two slices crosses it decisively.

The study does not suggest that any single meal causes cancer. But risk is cumulative, and the follow-up period — 14 years — is long enough to capture the kind of slow, steady damage that processed meat inflicts on the digestive tract.

## What Families Can Do

The most practical takeaway is substitution, not deprivation. Swapping processed meats for fresh-cooked chicken, fish, paneer, or legume-based proteins eliminates the risk without sacrificing convenience entirely. For families already cooking Indian food at home, the traditional thali — dal, sabzi, roti, raita — is precisely the kind of meal that does not appear anywhere in the study's risk tables.

**Sources:** European Prospective Investigation into Cancer and Nutrition (EPIC); Journal of Virology; Fox News Health; New York Post; USDA FoodData Central"""

    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr, _ = source_best_image(
        [],
        ["processed meat deli cold cuts", "stomach cancer research medical", "processed food health risk"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "culture",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.foxnews.com/health/one-extra-serving-processed-meat-day-linked-higher-cancer-risk",
            "https://nypost.com/2026/06/04/health/one-extra-serving-of-processed-meat-a-day-linked-to-higher-cancer-risk/",
            "https://www.who.int/news-room/questions-and-answers/item/cancer-carcinogenicity-of-the-consumption-of-red-meat-and-processed-meat"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "Assorted processed meats including deli ham, sausages, and bacon at a market counter",
        "image_attribution": img_attr or ""
    }

    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 3: RBI MPC Decision — Markets-Finance
# ============================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: RBI MPC Decision June 5")
    print("="*60)

    slug = "rbi-mpc-june-2026-repo-rate-hold-rupee-oil-nri-remittances-20260604"
    headline = "The RBI Decides on Rates Tomorrow. The Rupee Is at 95.75, Oil Is Near $97, and NRI Money Is Caught in the Middle."
    subheadline = "Most economists expect a hold at 5.25 per cent, but traders are split on whether a surprise hike could come. What the decision means for remittances, property investments, and equity markets."

    body = """The Reserve Bank of India's Monetary Policy Committee wraps up its three-day meeting on Friday, June 5, and will announce its decision at 10:00 a.m. IST. Governor Sanjay Malhotra faces a policy landscape that has grown considerably more complicated since the last meeting in April, when the committee held the repo rate steady at 5.25 per cent after a cumulative 125 basis points of cuts through 2025.

## The Case for Holding

Headline retail inflation remains well behaved. At 3.48 per cent in April, it sits comfortably below the RBI's 4 per cent target — the kind of number that would normally leave the door open for further easing. GDP growth remains resilient, and domestic consumption has held up despite global headwinds.

Most economists expect the committee to hold rates unchanged. The consensus is that the RBI will maintain its neutral stance while monitoring incoming data, particularly on inflation and the external account.

## The Case for a Surprise Hike

But beneath the headline inflation number, the picture is less reassuring. Wholesale price inflation has surged to 8.3 per cent, driven primarily by fuel and power costs. Brent crude is trading near $97 a barrel as the Strait of Hormuz remains largely closed three months into the US-Iran conflict. A ceasefire between Israel and Lebanon, announced late Wednesday, has offered a glimmer of hope for a broader de-escalation, but oil markets remain sceptical that the strait will reopen soon.

The rupee has weakened to 95.75 per dollar, having touched a lifetime low of 96.96 in mid-May before RBI intervention in spot and forward markets helped it recover. But traders warn that the relief may not last. If Friday's decision does not include measures to support the currency or attract dollar inflows, renewed pressure is expected.

Reuters reports that while most economists expect a hold, traders are more evenly split on whether the RBI will opt for a 25 basis point hike. Three foreign exchange traders told Reuters that a rate hike combined with hawkish messaging could push the rupee toward 94.80, though the move may face resistance at that level.

## What Is Happening at the Fed

The RBI's dilemma is complicated further by what is happening in Washington. New Federal Reserve Chairman Kevin Warsh faces his first policy meeting in two weeks amid rising inflation pressures driven by the same oil shock. The Fed's Beige Book, released on Wednesday, described a stagflationary combination of weakening consumer demand and rising cost pressures across most US regions.

Dallas Fed President Lorie Logan said on Wednesday that she is "increasingly concerned that higher interest rates could be necessary later this year," and futures markets now price a 75 per cent chance of a 25 basis point Fed rate hike before year-end. If the Fed tightens while the RBI holds, the interest rate differential narrows further, putting additional downward pressure on the rupee and on capital flows into India.

## What It Means for NRI Investors

**Remittances:** A weaker rupee means every dollar sent home buys more rupees — good news for families supporting relatives in India. But the volatility makes timing transfers difficult. If the RBI delivers a surprise hike and the rupee strengthens, NRIs who waited may get fewer rupees per dollar than they would today.

**Property investments:** Indian real estate has been buoyant, but a rate hike would raise mortgage costs domestically, potentially cooling demand. NRIs looking to buy property in India face a double calculation: the rupee exchange rate on their initial investment and the interest rate on any domestic financing.

**Equity markets:** A rate hike would create immediate selling pressure in rate-sensitive sectors — real estate, financials, and consumer discretionary. But if it is paired with measures to stabilise the rupee and attract foreign inflows, the medium-term impact on Indian equities could be neutral to positive.

**Fixed income:** Indian government bonds currently yield around 7.10 per cent on the 10-year benchmark. A hike could push yields to the 7.15-7.20 per cent range, making NRI fixed-income instruments slightly more attractive. The recent scrapping of capital gains tax on foreign bond investments adds to the appeal.

## The Bottom Line

The most likely outcome is a hold with hawkish commentary. But in a year where wholesale inflation is running at 8.3 per cent, oil is near $97, the rupee has lost 6.5 per cent, and the Fed is signalling higher rates, the RBI's room to stay patient is shrinking. For NRIs with money moving between India and the West, the next 24 hours are worth watching closely.

**Sources:** Reserve Bank of India; Reuters; The Hindu BusinessLine; Outlook Money; FXStreet"""

    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr, _ = source_best_image(
        ["Sanjay Malhotra RBI"],
        ["Reserve Bank of India Mumbai", "Indian rupee currency", "RBI monetary policy"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "vertical": "economy",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.thehindubusinessline.com/money-and-banking/rbi-mpc-meet-june-2026/article69652345.ece",
            "https://www.reuters.com/world/india/indian-rupee-dips-rbi-led-relief-may-fade-without-inflow-measures-2026-06-04/",
            "https://www.outlookmoney.com/banking/rbi-likely-to-hold-repo-rate-in-june-mpc"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai ahead of the June 2026 monetary policy decision",
        "image_attribution": img_attr or ""
    }

    art_id = insert_article(article)
    return art_id


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Starting lifestyle/markets writer at {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:50]}...")

    results = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            art_id = writer_fn()
            results.append(art_id)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    success = sum(1 for r in results if r)
    print(f"  Articles inserted: {success}/{len(results)}")
    for i, r in enumerate(results):
        status = f"✓ {r}" if r else "✗ FAILED"
        print(f"  Article {i+1}: {status}")

    if success < len(results):
        sys.exit(1)
