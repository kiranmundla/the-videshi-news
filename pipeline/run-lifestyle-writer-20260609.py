#!/usr/bin/env python3
"""
Videshi Lifestyle-Health + Markets-Finance Writer
Run date: 2026-06-09
Articles:
  1. (lifestyle-health) Retatrutide triple-G drug: sleep apnea, weight loss, knee pain
  2. (lifestyle-health) Walking patterns and cardiovascular risk — how you walk matters
  3. (markets-finance) Shrinkflation hits India as Iran war squeezes margins — NRI impact
"""

import json, os, sys, uuid, io, time, re
from datetime import datetime, timezone
import requests
from PIL import Image

# ── Env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image helpers ────────────────────────────────────────────────────────
def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
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
        if r.status_code == 200 and r.headers.get("Content-Type","").startswith("image"):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes): {url[:80]}")
        else:
            print(f"  ⚠ Download failed: HTTP {r.status_code} for {url[:80]}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    """Upload JPEG to article-images bucket, return public URL."""
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(upload_url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)//1024}KB)")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
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
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key")
        return None
    try:
        import subprocess
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels: found image for '{query}'")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def source_image(slug, person_name=None, wiki_queries=None, pexels_query=None):
    """Multi-source image search, compress, upload to Supabase. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url:
            candidates.append({"url": url, "source": "Wikimedia Commons", "relevance": 3})

    # Source 2: Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons(q, limit=3)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "Wikimedia Commons", "relevance": 2})

    # Source 3: Pexels
    if pexels_query:
        url = fetch_pexels(pexels_query)
        if url:
            candidates.append({"url": url, "source": "Pexels", "relevance": 1})

    # Pick best and upload
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        raw = download_image(c["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) > 5000:
                final_url = upload_to_supabase(compressed, f"{slug}.jpg")
                if final_url:
                    return final_url, c["source"]
    
    print(f"  ⚠ No valid image found for {slug}")
    return None, None

def insert_article(article):
    """Insert article into p2_articles. Returns article ID or None."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Retatrutide Triple-G Drug
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ARTICLE 1: Retatrutide Triple-G Drug")
print("="*70)

art1_slug = "retatrutide-triple-g-obesity-drug-sleep-apnea-knee-pain-south-asian-ada-20260609"
art1_headline = "The Most Powerful Obesity Drug Ever Tested Just Crushed Sleep Apnea and Knee Pain in a Single Trial. South Asians Are in the Crosshairs."
art1_subheadline = "Eli Lilly's retatrutide, which targets three hormones at once, reduced sleep apnea severity by 61 per cent and knee pain by 73 per cent while delivering 28 per cent body weight loss. For a community with the highest rates of metabolic disease in the world, this is not just another headline."

art1_body = """The drug does not have an elegant name. Retatrutide sounds like a chemical compound because it is one. But the numbers it just posted at the American Diabetes Association conference in New Orleans are the kind that rearrange a medical field.

In a Phase 3 trial involving adults with obesity and moderate-to-severe obstructive sleep apnea, a once-weekly injection of retatrutide reduced sleep apnea severity by 60.6 per cent. In the same study, it cut knee osteoarthritis pain by up to 73.1 per cent. Separately, patients with obesity lost 28 per cent of their body weight, and adults with type 2 diabetes experienced significant drops in blood sugar levels. All of this from a single molecule.

Eli Lilly, the Indiana-based pharmaceutical company behind the drug, calls retatrutide a "triple G" — a reference to its mechanism. Unlike Ozempic or Zepbound, which target one or two gut hormones, retatrutide simultaneously activates receptors for GLP-1, GIP, and glucagon, the three hormones most directly involved in appetite, metabolism, and fat storage.

## Why South Asians Cannot Afford to Look Away

Here is the part that matters for the diaspora. South Asians have the highest rates of metabolic syndrome of any ethnic group on the planet. Type 2 diabetes strikes South Asians at lower body weights, younger ages, and with greater ferocity than it does Europeans. The MASALA study, which tracks cardiometabolic health in South Asian Americans, has documented prevalence rates of diabetes and prediabetes that dwarf national averages.

Obstructive sleep apnea is tightly linked to this metabolic burden. Studies published in the journal *Sleep* have shown that South Asians develop sleep apnea at significantly lower BMI thresholds — a pattern attributed to differences in craniofacial anatomy and visceral fat distribution. A South Asian man with a BMI of 26 can have the same apnea severity as a white man at BMI 32.

This means a drug that simultaneously attacks obesity, sleep apnea, and joint degeneration is not a general-interest science story. It is a direct answer to the cluster of conditions that define South Asian metabolic risk.

## The Safety Question That Lingers

The trial results published in *The Lancet* on Saturday included one finding that will draw scrutiny. Among patients with type 2 diabetes taking the lowest dose, 2 per cent experienced major adverse cardiovascular events. Eli Lilly noted these events were not necessarily caused by the drug, and the numbers are small enough that they may fall within statistical noise. But for a community already at elevated cardiovascular risk, this will need longer-term data to resolve.

The gastrointestinal side effects that have plagued the entire GLP-1 class are present here too, though Lilly claims retatrutide's tolerability is competitive with existing drugs. The key comparison will come when retatrutide's full safety profile is stacked against tirzepatide, Lilly's own blockbuster Zepbound, which is already approved for sleep apnea.

## A Market Race With Billions at Stake

Eli Lilly and Novo Nordisk are locked in an extraordinary arms race. Novo's semaglutide powers Ozempic and Wegovy. Lilly's tirzepatide drives Mounjaro and Zepbound. Now retatrutide is being positioned as the next generation — stronger, broader, and aimed at replacing or complementing the drugs that have already created a $50 billion global market.

For the 30 million South Asians living in the United States and the millions more across the UK, Canada, and the Gulf, the practical question is when retatrutide might reach the market and at what cost. Current GLP-1 drugs already strain insurance coverage and cost $1,000 or more per month out of pocket. A triple-agonist with superior efficacy could command premium pricing that puts it out of reach for much of the community that needs it most.

## What Comes Next

Lilly has not disclosed when it plans to submit retatrutide for regulatory approval, but the Phase 3 data presented in New Orleans is the kind that typically precedes a filing within 12 to 18 months. If approved, it would be the first triple-hormone obesity drug on the market.

For diaspora families watching a parent or sibling struggle with the intertwined burdens of diabetes, sleep apnea, and joint pain — all of which feed each other in a vicious cycle — a drug that addresses all three simultaneously is not incremental. It is the kind of intervention this community has been waiting for, assuming the price and access barriers do not slam the door shut.

*Sources: Reuters, Eli Lilly ADA 2026 presentations, The Lancet, MASALA Study*"""

# Image: Try Wikimedia Commons for "obesity drug injection" or similar
img1_url, img1_attr = source_image(
    art1_slug,
    person_name=None,
    wiki_queries=["Eli Lilly headquarters Indianapolis", "GLP-1 receptor agonist", "obesity treatment injection"],
    pexels_query="medical injection pharmaceutical drug"
)

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": img1_url,
    "image_caption": "Eli Lilly headquarters in Indianapolis, Indiana — home of the company behind retatrutide",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "sources": json.dumps(["Reuters", "Eli Lilly ADA 2026 presentations", "The Lancet", "MASALA Study"]),
    "published_at": datetime.now(timezone.utc).isoformat()
}
if not img1_url:
    art1.pop("image_url")
    art1.pop("image_caption")
    art1.pop("image_attribution")

id1 = insert_article(art1)

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Walking Patterns and Heart Disease
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ARTICLE 2: Walking Patterns and Heart Disease")
print("="*70)

art2_slug = "walking-pattern-cardiovascular-risk-continuous-sessions-south-asian-heart-20260609"
art2_headline = "It Is Not How Much You Walk. It Is How You Walk. A New Study Says the Difference Is 67 Per Cent."
art2_subheadline = "A UK Biobank study of over 6,000 adults found that consolidating the same number of steps into continuous 10-to-15-minute walks — instead of scattering them across the day — reduced cardiovascular events by up to 67 per cent. For South Asians, who carry the world's highest heart disease burden, this reframes everything."

art2_body = """The fitness industry has spent a decade selling you a number: 10,000 steps. The implicit promise was simple — hit the count, however you get there, and your heart is covered. A study published in *Annals of Internal Medicine* says that promise was incomplete, and the missing piece may matter more than the number itself.

Researchers from the Universidad Europea and the University of Sydney analysed accelerometer data from 6,399 participants in the UK Biobank who averaged fewer than 8,000 steps per day — people who, by conventional fitness standards, were not particularly active. They tracked not just how many steps each person took, but how those steps were distributed across the day.

During a median follow-up of 7.9 years, 331 cardiovascular events occurred, including heart attacks, strokes, and cardiovascular deaths. The finding that emerged was striking: among people with the same total daily step count, those who concentrated their walking into one or two continuous sessions of at least 10 to 15 minutes had a 60 to 67 per cent lower risk of cardiovascular events than those whose steps came from scattered short bouts of less than five minutes.

The difference was not marginal. It was the gap between a modest lifestyle modification and a pharmaceutical intervention.

## The Scattered-Step Trap

Think about how most people accumulate steps during a workday. A walk from the parking lot to the office. A trip to the coffee machine. A few laps around the kitchen while dinner simmers. By evening, the step counter might read 6,000 or 7,000 — respectable enough to feel productive. But the study suggests these scattered micro-walks may not trigger the sustained cardiovascular stimulus that protects against heart disease.

The mechanism is likely tied to how the heart and vascular system respond to continuous moderate-intensity exercise. A 15-minute brisk walk raises heart rate into a zone that improves endothelial function, enhances blood flow, and triggers anti-inflammatory signalling. A 90-second walk to the printer does not.

For South Asians, this distinction carries extra weight. The community has the highest age-adjusted rates of coronary artery disease in the world. The INTERHEART study found that South Asians suffer heart attacks nearly a decade earlier than other ethnic groups, and physical inactivity is one of the modifiable risk factors that contributes disproportionately to that burden.

## What This Means for the Diaspora

The diaspora lifestyle is, in many ways, optimised for scattered steps. Long desk-bound workdays in tech and finance. Car-dependent suburbs in the Bay Area, New Jersey, and Greater Toronto. Social lives that revolve around meals rather than movement. Weekend temple visits where the longest walk is from the parking lot to the prayer hall.

None of these patterns are wrong. But the study suggests they are insufficient, even when the step counter tells a reassuring story. The fix, however, is not a gym membership or a marathon training plan. It is something far simpler: one or two dedicated walking sessions of 10 to 15 minutes each day, at a pace brisk enough to make conversation slightly effortful.

A morning walk before the commute. A post-dinner loop around the neighbourhood. A lunch break spent walking, not scrolling. The study says these modest, concentrated efforts may deliver cardiovascular protection that a day full of fragmented movement cannot match.

## The 10,000-Step Myth, Reconsidered

The 10,000-step target, it is worth noting, was never based on rigorous science. It originated as a marketing slogan for a Japanese pedometer in the 1960s. Subsequent research has validated the general principle that more movement is better, but this latest study adds a crucial qualifier: continuity matters as much as quantity.

For a community that already faces elevated cardiovascular risk at lower body weights and younger ages, this is not a footnote. It is a reframing. The question is no longer "did I hit my step count?" but "did I walk long enough, without stopping, for my heart to notice?"

The answer, according to the data, needs to be at least 10 minutes. Preferably 15. Every day.

*Sources: Annals of Internal Medicine (October 2025), UK Biobank, INTERHEART Study, Universidad Europea / University of Sydney*"""

# Image: Walking / exercise
img2_url, img2_attr = source_image(
    art2_slug,
    person_name=None,
    wiki_queries=["walking exercise park", "brisk walking health", "people walking outdoors"],
    pexels_query="brisk walking park morning exercise"
)

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": img2_url,
    "image_caption": "A morning walk in the park — research now shows continuous walking sessions protect the heart far more than scattered steps",
    "image_attribution": img2_attr or "Pexels",
    "sources": json.dumps(["Annals of Internal Medicine", "UK Biobank", "INTERHEART Study", "Universidad Europea / University of Sydney"]),
    "published_at": datetime.now(timezone.utc).isoformat()
}
if not img2_url:
    art2.pop("image_url")
    art2.pop("image_caption")
    art2.pop("image_attribution")

id2 = insert_article(art2)

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 3: Shrinkflation Hits India — Iran War Squeezes Consumers
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ARTICLE 3: Shrinkflation Hits India")
print("="*70)

art3_slug = "india-shrinkflation-price-hikes-iran-war-dabur-hul-nri-remittance-impact-20260609"
art3_headline = "Your Maggi Packet Just Got Smaller. So Did Everything Else. The Iran War Is Shrinking India's Grocery Aisle."
art3_subheadline = "From Dabur to Maruti, Indian companies are cutting grammage, hiking prices, and rerouting supply chains as the Iran war drives up oil, freight, and input costs. For NRIs sending money home, every rupee now buys measurably less."

art3_body = """Mohit Malhotra, the global CEO of Dabur, said something last week that every Indian household will eventually notice on the shelf before they notice it in the news. "We are reducing grammage because we can't breach those price points," he told Reuters, explaining why the company is shrinking product sizes instead of raising prices outright.

He is not alone. Hindustan Unilever, Godrej Consumer Products, and Britannia have all rolled out low- to mid-single-digit price hikes across categories. Automakers Maruti Suzuki, Mahindra, Tata Motors, and Hyundai Motor India have raised sticker prices. Airlines IndiGo and Air India are trimming capacity on fuel-heavy international routes and hiking fares. The squeeze is moving through every layer of the Indian consumer economy.

The cause is not subtle. The Iran war, which began on February 28, has disrupted global trade routes, pushed benchmark oil prices 30 per cent higher, and driven gas prices up 75 per cent. For India, which imports roughly 90 per cent of its oil, the impact is systemic. The Strait of Hormuz — through which a fifth of the world's crude and liquefied natural gas transits — remains effectively blockaded, with Tehran blocking most shipping and Washington imposing its own blockade on Iranian ports.

## The Grammage Game

Shrinkflation is not new to India. During previous commodity cycles, companies have quietly reduced product sizes while holding the sticker price constant, particularly on the 10- to 20-rupee packs that dominate mass-market retail. What is different this time is the breadth. This is not one category or one company. It is a synchronised response across consumer goods, automobiles, airlines, and logistics.

The rupee's slide — it hit a new low against the dollar last month before recovering slightly to 95.35 on Tuesday — is compounding the pain. A weaker rupee makes imports more expensive, raising input costs for everything from palm oil in soap to crude-oil derivatives in packaging.

"We are among the world's most vulnerable countries," economist Jayati Ghosh warned, noting that higher oil and fertiliser costs, weaker Gulf demand, softer remittances, and potential capital outflows could stoke inflation and slow growth simultaneously.

Hindustan Unilever has responded by cutting advertising spend. Others are trimming non-essential travel and marketing costs. But as Axis Direct analyst Uttam Kumar Srimal noted, "the scope for further cost-cutting is gradually narrowing." Prolonged commodity inflation could force sharper price hikes or outright margin hits.

## What NRIs Are Already Feeling

For the millions of Indians living in the United States, United Kingdom, Canada, and the Gulf, this is not an abstract macro story. It is showing up in the monthly wire transfer.

When an NRI in Houston sends $500 home, the rupee equivalent has already shrunk because of the currency slide. Now that money buys less once it arrives. The same monthly grocery bill in Delhi, Mumbai, or Chennai covers fewer items — or smaller ones — than it did three months ago. Flight tickets to India for summer visits are significantly more expensive, as airlines pass fuel surcharges through to passengers.

Remittances themselves are under pressure. Workers in the Gulf states, which account for a significant share of inward remittances to India, face their own cost-of-living increases as the war disrupts regional economies. The double compression — weaker rupee on one side, inflation on the other — means the purchasing power of diaspora money is being eroded from both ends.

## Supply Chains in Motion

Indian companies are not just raising prices and cutting sizes. They are actively reworking supply chains. Dabur is routing shipments through Egypt and Turkey to avoid Middle East disruptions. Britannia is bringing some production back to India. Arvind Fashions has advanced inventory purchases to lock in costs and shifted to more local suppliers. Trent, the Tata Group retailer behind the Gen-Z brand Zudio, is tweaking raw materials and packaging to hold the line on prices.

"My priority is not to take prices up," said Umashan Naidoo, head of customer and beauty at Trent. But for most companies, the math is becoming unavoidable.

The Indian government has already disbursed 1.2 trillion rupees — roughly $12.6 billion — to oil refiners and retailers to subsidise pump prices during the first 78 days of the war. The fertiliser ministry has sought to double its budgeted subsidy fund for the current fiscal year. These are not normal measures. They are crisis spending designed to insulate consumers from the worst of the shock.

## The Road Ahead

The Reserve Bank of India sees inflation averaging 5.1 per cent in the year to March 2027, up from 3.48 per cent in April. Economic growth is expected to slip to 6.6 per cent from 7.7 per cent the previous year. Interest rate swap markets are pricing in at least 25 basis points of rate hikes over the next three months.

For Indian consumers, the question is whether this is the peak of the squeeze or the beginning of a longer adjustment. For NRIs, it is simpler: the money you send home now buys less than it did in January, and there is no sign of that trend reversing while oil remains above $90 a barrel and the Strait of Hormuz stays contested.

Aditi Anjana, a Mumbai-based communications professional in her 30s, put it plainly to Reuters: "I have no family to feed, no school fees, and no monthly payments on a car. I'm still watching my spending as prices are up for almost everything, from travel to packaged food."

If a single professional in Mumbai is tightening her belt, imagine the calculus for a family of four.

*Sources: Reuters, Reserve Bank of India, HSBC Research, Axis Direct, Barclays Research*"""

# Image: Indian grocery / consumer goods
img3_url, img3_attr = source_image(
    art3_slug,
    person_name=None,
    wiki_queries=["Indian grocery store products", "consumer goods India supermarket", "FMCG products India"],
    pexels_query="Indian grocery store shopping aisle products"
)

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "image_url": img3_url,
    "image_caption": "Indian consumer goods on store shelves — pack sizes are shrinking as companies absorb rising input costs",
    "image_attribution": img3_attr or "Pexels",
    "sources": json.dumps(["Reuters", "Reserve Bank of India", "HSBC Research", "Axis Direct", "Barclays Research"]),
    "published_at": datetime.now(timezone.utc).isoformat()
}
if not img3_url:
    art3.pop("image_url")
    art3.pop("image_caption")
    art3.pop("image_attribution")

id3 = insert_article(art3)

# ── Summary ──────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
results = [
    ("lifestyle-health", art1_slug, id1, bool(img1_url)),
    ("lifestyle-health", art2_slug, id2, bool(img2_url)),
    ("markets-finance", art3_slug, id3, bool(img3_url)),
]
for cat, slug, aid, has_img in results:
    status = "✓" if aid else "✗"
    img_status = "📷" if has_img else "⚠️ no image"
    print(f"  {status} [{cat}] {slug} → {aid} {img_status}")

all_ok = all(r[2] for r in results)
print(f"\nOverall: {'ALL INSERTED ✓' if all_ok else 'SOME FAILED ✗'}")
sys.exit(0 if all_ok else 1)
