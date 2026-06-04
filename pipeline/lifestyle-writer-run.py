#!/usr/bin/env python3
"""Lifestyle & Markets writer — June 4, 2026 run"""
import requests, json, os, io, uuid, urllib.parse, time, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ============================================================
# IMAGE SOURCING
# ============================================================
def fetch_wikipedia_person_image(person_name):
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
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA}, timeout=15
        )
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
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        encoded = urllib.parse.quote(query)
        cmd = f'curl -sS "https://api.pexels.com/v1/search?query={encoded}&per_page=5" -H "Authorization: {PEXELS_KEY}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for p in photos:
            url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
            if url:
                print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
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

def download_and_upload(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {img_url[:60]}")
            return None
        ct = r.headers.get('Content-Type', '')
        if not ct.startswith('image/'):
            print(f"  ⚠ Not an image ({ct}): {img_url[:60]}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Too small ({len(r.content)} bytes)")
            return None

        compressed = compress_image(r.content)
        print(f"  Compressed: {len(r.content)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:60]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:100]}")
            return None
    except Exception as e:
        print(f"  ⚠ Download/upload error: {e}")
        return None

def source_image(person_name, topic_queries, slug):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    for q in topic_queries:
        commons = fetch_wikimedia_commons(q, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
        if commons:
            break

    # Source 3: Pexels
    for q in topic_queries:
        pexels = fetch_pexels_image(q)
        if pexels:
            candidates.append({"url": pexels, "source": "pexels", "priority": 3})
            break

    # Pick best and upload
    candidates.sort(key=lambda x: x["priority"])
    for c in candidates:
        filename = f"{slug}.jpg"
        final_url = download_and_upload(c["url"], filename)
        if final_url:
            attribution = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return final_url, attribution

    print(f"  ⚠ No image found for {slug}")
    return None, None

# ============================================================
# ARTICLE INSERTION
# ============================================================
def insert_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    vertical_map = {
        "lifestyle-health": "culture",
        "markets-finance": "economy"
    }

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": article["category"],
        "vertical": vertical_map.get(article["category"], "news"),
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", "The Videshi"),
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "created_at": now,
        "updated_at": now
    }

    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        print(f"✅ Published: {article['headline'][:60]}...")
        return art_id
    else:
        print(f"❌ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ============================================================
# ARTICLES
# ============================================================

articles = []

# --- ARTICLE 1: Bladder cancer immunotherapy ---
articles.append({
    "headline": "An Immunotherapy Drug Just Kept 85 Per Cent of Bladder Cancer Patients Tumour-Free Without Surgery. It Could Change Everything.",
    "subheadline": "A trial at the Institute of Cancer Research shows durvalumab combined with chemoradiation may spare thousands from life-altering bladder removal surgery.",
    "slug": "bladder-cancer-immunotherapy-durvalumab-asco-2026-surgery-spared-south-asian-20260604",
    "category": "lifestyle-health",
    "sources": json.dumps([
        {"name": "The Sun / Institute of Cancer Research", "url": "https://www.thesun.co.uk"},
        {"name": "ASCO 2026 Annual Meeting", "url": "https://meetings.asco.org"},
        {"name": "NIAGARA Phase 3 Trial / NEJM", "url": "https://www.nejm.org"},
        {"name": "OncLive GU Cancer 2026", "url": "https://www.onclive.com"}
    ]),
    "person_name": None,
    "image_queries": ["bladder cancer treatment immunotherapy", "cancer immunotherapy drug infusion", "cancer treatment chemotherapy"],
    "body": """For most people diagnosed with muscle-invasive bladder cancer, the conversation with their surgeon ends the same way: the bladder has to come out. Radical cystectomy — the surgical removal of the entire bladder — has been the standard of care for decades. It works, but the trade-offs are severe. Many patients live the rest of their lives with a stoma bag. Others face sexual dysfunction, chronic infection risk, and a recovery that can stretch across months.

A new trial presented at the American Society of Clinical Oncology annual meeting in Chicago may have just rewritten that playbook.

## The Trial That Changed the Room

Researchers at the Institute of Cancer Research in London and the Royal Marsden NHS hospital enrolled 54 patients with muscle-invasive bladder tumours — the kind that has spread into the muscle wall of the organ and would normally require surgical removal. Instead of operating, they gave patients the immunotherapy drug durvalumab alongside the same chemotherapy and radiation therapy that would typically precede surgery.

The results were striking. At the one-year mark, 85 per cent of patients who received the durvalumab combination were still cancer-free. In the comparison group, which received standard chemoradiation without immunotherapy, just 60 per cent remained disease-free.

"Keeping the bladder means people can avoid major, life-changing surgery and maintain more of their normal daily function and independence," said Professor Nick James, the trial's lead investigator. "I expect this approach to be practice-changing."

## How Durvalumab Works

Durvalumab is a checkpoint inhibitor. It works by blocking PD-L1, a protein that cancer cells use to hide from the immune system. By removing that shield, durvalumab allows the body's own immune cells to recognise and attack the tumour. The drug is already approved and in clinical use for lung cancer and, since March 2025, for perioperative bladder cancer treatment in combination with chemotherapy based on the earlier NIAGARA phase 3 trial.

That larger NIAGARA study had already demonstrated the potential. In a randomised trial of over 1,000 patients, those who received perioperative durvalumab plus chemotherapy before surgery had significantly better event-free survival than those on chemotherapy alone — a hazard ratio of 0.68, with 24-month event-free survival rates of 67.8 per cent versus 59.8 per cent.

The new ASCO 2026 data goes further. It suggests that for a significant subset of patients, surgery may not be necessary at all.

## Why This Matters for the Diaspora

Bladder cancer is one of the most common cancers worldwide, and India carries a disproportionate share of the burden. The country records over 18,000 new cases annually, and studies have linked higher rates in parts of India to industrial chemical exposure, tobacco chewing, and contaminated groundwater.

For NRI families, this has practical implications. Ageing parents in India who are diagnosed with muscle-invasive bladder cancer currently face a difficult choice: undergo major surgery at a hospital that may have limited post-operative support, or seek treatment abroad at enormous cost. A bladder-sparing immunotherapy regimen could transform the landscape — especially as durvalumab is already manufactured by AstraZeneca and available in Indian hospitals.

For South Asians in the US and UK, the development is equally relevant. Men of South Asian descent are diagnosed with bladder cancer at rates comparable to or slightly below the general population, but outcomes tend to be worse because of later diagnosis. A treatment that preserves the bladder and maintains quality of life could be especially valuable for patients who delay seeking care due to cultural stigma around urological conditions.

## What Comes Next

The trial remains small — 54 patients is a proof of concept, not a definitive study. Larger randomised trials are already in the pipeline. The ongoing KEYNOTE-866 trial is evaluating pembrolizumab, another checkpoint inhibitor, in a similar bladder-sparing setting. Meanwhile, exploratory work with circulating tumour DNA (ctDNA) biomarkers is helping researchers identify which patients are most likely to respond to immunotherapy and which may still need surgery.

Professor James and his team are cautiously optimistic. The data does not mean surgery is obsolete for bladder cancer. But it does mean that for a growing number of patients, the question is shifting from "when do we operate" to "do we need to operate at all."

For a disease that has been treated essentially the same way for half a century, that is a significant shift."""
})

# --- ARTICLE 2: Turmeric / Curcumin under scrutiny ---
articles.append({
    "headline": "Turmeric Is 2026's Herb of the Year. But the Science Behind Curcumin May Not Be What You Think.",
    "subheadline": "The West spent $275 million studying curcumin. Indian families have been drinking haldi doodh for centuries. A new review asks who was right.",
    "slug": "turmeric-curcumin-herb-of-year-2026-science-review-haldi-south-asian-20260604",
    "category": "lifestyle-health",
    "sources": json.dumps([
        {"name": "New Scientist", "url": "https://www.newscientist.com"},
        {"name": "American College of Healthcare Sciences", "url": "https://achs.edu"},
        {"name": "International Journal of Molecular Sciences / PMC", "url": "https://pmc.ncbi.nlm.nih.gov"},
        {"name": "Frontiers in Nutrition", "url": "https://www.frontiersin.org"}
    ]),
    "person_name": None,
    "image_queries": ["turmeric powder spice golden", "turmeric curcumin Indian spice", "haldi turmeric root powder"],
    "body": """If you grew up in an Indian household, you did not need a clinical trial to know about turmeric. A scraped knee got a paste of haldi and coconut oil. A cough earned you a glass of warm milk with a quarter teaspoon stirred in. Turmeric was not a supplement. It was infrastructure.

Now, in 2026, the International Herb Association has named turmeric its Herb of the Year. The golden spice has arrived — again — in the Western wellness spotlight, championed by influencers, supplement brands, and a multibillion-dollar nutraceutical industry. But a critical new examination from New Scientist, published on June 1, asks a question that might sting: does the science actually hold up?

## The $275 Million Question

Curcumin is the compound in turmeric responsible for its deep yellow colour and most of its claimed health benefits. Since the early 2000s, it has been studied for its anti-inflammatory, anti-cancer, anti-Alzheimer's, and anti-arthritis properties. US health agencies alone have spent more than $275 million on curcumin research since 1990.

Much of that research was inspired by the work of Bharat Aggarwal, a biochemist formerly at the University of Texas MD Anderson Cancer Center. Starting in the early 2000s, Aggarwal published over 100 papers showing that curcumin reduces inflammation and kills tumour cells. His research helped launch the turmeric latte craze and the curcumin supplement industry, which is now worth billions globally.

The problem is that a significant portion of Aggarwal's work has been retracted. His papers drew scrutiny for image manipulation and data irregularities. The University of Texas investigated and Aggarwal retired in 2015. Dozens of his publications have since been pulled from journals.

This does not mean curcumin is useless. But it does mean that the foundation on which much of the supplement industry's marketing was built has cracks.

## What the Science Actually Shows

When researchers strip away the retracted studies and focus on rigorous clinical trials, a more nuanced picture emerges. A comprehensive scoping review published in the International Journal of Molecular Sciences examined curcumin trials from 1900 to 2020. The strongest evidence supports anti-inflammatory effects — which aligns with what Ayurvedic practitioners have said for millennia.

For joint health, the evidence is reasonably solid. A randomised clinical trial found that turmeric extract performed comparably to ibuprofen for knee osteoarthritis pain, with fewer gastrointestinal side effects. A 2025 meta-analysis found modest improvements in working memory and processing speed with bioavailable curcumin formulations.

For cancer, the picture is far less clear. While curcumin shows activity against cancer cells in laboratory settings, translating that into clinical results has been difficult. The core problem is bioavailability: curcumin is poorly absorbed by the gut, rapidly metabolised, and quickly eliminated. Most of what you swallow in a capsule never reaches your bloodstream in meaningful concentrations.

Researchers at the University of South Australia and McMaster University have developed nano-emulsified curcumin formulations that increase bioavailability by 117 per cent. But these are experimental, not what you find on a pharmacy shelf.

## The Haldi Doodh Paradox

Here is where it gets interesting for the diaspora. Indian families were never consuming curcumin isolates in 500-milligram capsules. They were eating turmeric as part of whole food — in dal, in sabzi, in warm milk with black pepper and ghee. Black pepper contains piperine, which increases curcumin absorption by up to 2,000 per cent. Fat — from ghee, coconut oil, or milk — further aids absorption.

In other words, the traditional preparation may have been solving the bioavailability problem all along, centuries before pharmaceutical scientists identified it.

This does not validate every Ayurvedic health claim. But it does suggest that the Western approach of isolating a single compound, putting it in a capsule, and testing it in a controlled trial may miss the synergistic effects of whole-food preparations. The American College of Healthcare Sciences, which championed turmeric's Herb of the Year designation, makes a similar point: turmeric powder is rich in curcuminoids that support systemic inflammation and gut health, while the essential oil contains volatile sesquiterpenes with antimicrobial properties. Used together, they may be more effective than either alone.

## What NRI Families Should Know

The turmeric supplement market is projected to exceed $1.5 billion globally by 2027. For South Asians in the US, UK, and Canada, the irony is palpable: the same ingredient that sat in every kitchen cabinet is now being sold back at premium prices in capsule form, often with lower bioavailability than a simple cup of haldi doodh.

That said, caution is warranted. High-dose curcumin supplements have been linked to liver damage in some case reports, particularly those marketed as "enhanced absorption" formulations. The European Food Safety Authority has flagged several such products. If you are taking curcumin supplements alongside other medications, especially blood thinners or diabetes drugs, consult your doctor.

The bottom line is this: turmeric in food, prepared the way your grandmother made it, remains a reasonable part of a healthy diet. The supplement aisle is where the science gets thin and the marketing gets thick. The 2026 Herb of the Year designation is well earned — but the reasons have more to do with a 4,000-year track record in Indian kitchens than with the last two decades of clinical trials."""
})

# --- ARTICLE 3: SpaceX IPO ---
articles.append({
    "headline": "SpaceX Just Set the Price for the Largest IPO in History. Here Is What NRI Investors Need to Know.",
    "subheadline": "At $135 a share and a $1.75 trillion valuation, SpaceX's June 12 Nasdaq debut will dwarf every public offering before it. The numbers are extraordinary — and so are the risks.",
    "slug": "spacex-ipo-75-billion-largest-history-135-share-nasdaq-nri-investors-20260604",
    "category": "markets-finance",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Times (UK)", "url": "https://www.thetimes.com"},
        {"name": "CNBC / Morningstar", "url": "https://www.cnbc.com"},
        {"name": "SpaceX SEC Filing", "url": "https://www.sec.gov"}
    ]),
    "person_name": "Elon Musk",
    "image_queries": ["SpaceX rocket launch Falcon", "SpaceX Starlink satellite launch", "SpaceX Falcon 9 launch pad"],
    "body": """SpaceX has done what no company in history has attempted: it set a fixed price for its initial public offering a full week before trading begins, skipping the traditional price-discovery process that Wall Street has used for decades, and dared investors to take it or leave it.

In an amended filing with the SEC on Wednesday, SpaceX said it will sell 555,555,555 shares at $135 each, raising approximately $75 billion. The offering will value the company at around $1.75 trillion. Trading is expected to begin on the Nasdaq on June 12 under the ticker SPCX.

If it goes through at these terms, it will be the largest IPO in history — nearly three times the $25.6 billion raised by Saudi Aramco in 2019. SpaceX would immediately rank among the ten most valuable publicly traded companies in the United States, surpassing Meta Platforms, Berkshire Hathaway, and Elon Musk's own Tesla, which had a market capitalisation of $1.3 trillion on Wednesday.

## The Numbers Behind the Valuation

SpaceX reported $18.7 billion in revenue in 2025, including sales from its xAI artificial intelligence unit. At a $1.75 trillion valuation, that puts the company at roughly 93.6 times its annual sales. For context, the aggregate price-to-sales ratio of the S&P 500 is 3.38. Tesla, often considered an expensive stock, had a price-to-sales ratio of 16.73 at the end of 2025.

Morningstar analysts have already flagged the valuation as "significantly overvalued." In a note published earlier this week, they wrote: "We think the company has been significantly overvalued and investors will have opportunities to buy the stock at more attractive levels after the IPO."

SpaceX reported revenue of $4.7 billion in the first quarter of 2026 alone, but also posted a net loss of $4.3 billion. The xAI unit continues to lose money. Revenue growth is real, but profitability remains distant.

## What Is Actually Being Sold

The heart of SpaceX's revenue is not rockets. It is Starlink, the satellite internet business, which generated $11.4 billion in 2025 — 61 per cent of total revenue. By the first quarter of 2026, Starlink's share had risen to 69 per cent. The service had 10.3 million subscribers across 155 countries by March 31, 2026.

SpaceX's prospectus also reveals plans to deploy orbital AI computing satellites as early as 2028, and to build solar-powered data centres in space. The company is targeting what it calls a total addressable market of $28.5 trillion across its businesses — a figure that would encompass global internet access, satellite communications, space launch, and orbital computing.

The rocket business remains critical but is increasingly a means to an end. SpaceX has pioneered reusable rockets that have transformed the economics of space launch, but the real valuation story is Starlink's recurring subscription revenue and the AI infrastructure play.

## Why This Matters for Indian Investors

India has the second-largest pool of retail investors in the world after the United States, and NRI investors increasingly participate in US equity markets through platforms like Vested, Groww, and INDmoney. The SpaceX IPO is generating enormous interest in diaspora investment circles, but several factors deserve careful attention.

First, access. SpaceX has said it will give retail investors a larger role in IPO allocations than is typical, but the $135-per-share price means a single lot represents a significant commitment. The conditional offer-to-purchase window opens on June 4, and brokerage platforms are already scrambling to process paperwork.

Second, governance. Musk is expected to hold 84.4 per cent of voting power after the IPO. This dual-class structure means outside shareholders will have minimal influence on corporate decisions. For Indian investors accustomed to SEBI's governance norms, this is a different landscape entirely.

Third, valuation risk. At 93.6 times sales, SpaceX is priced not for what it earns today but for what it might become in a decade. The comparison is not to other aerospace companies — Lockheed Martin trades at 1.7 times sales — but to the most optimistic scenarios for AI infrastructure and global internet dominance. If Starlink's subscriber growth slows, or if orbital computing proves harder than projected, the stock could face substantial downward pressure.

Fourth, the Musk factor. SpaceX's fortunes are deeply intertwined with its founder's public persona, his political entanglements, and his management of multiple companies simultaneously. Indian investors who remember the volatility around Tesla's various controversies should calibrate their expectations accordingly.

## The Broader Market Context

The SpaceX IPO lands in a market that is simultaneously euphoric about AI and rattled by geopolitics. The S&P 500 hit record highs earlier this week before pulling back on Wednesday as US-Iran hostilities escalated. Brent crude settled at $97.81 a barrel. Gold fell on expectations that war-driven inflation will keep interest rates elevated.

A syndicate of more than 21 banks has been assembled to support the deal. The roadshow begins on Thursday, with pricing expected on June 11 and trading commencing June 12.

For NRI investors, the SpaceX IPO is not a decision to make lightly. The company is extraordinary — it has reshaped the space industry and built a satellite internet network that reaches half the planet. But extraordinary companies at extraordinary valuations do not always make extraordinary investments. The history of blockbuster IPOs is littered with examples of companies that took years to grow into their debut-day prices.

If you are considering participating, know what you are buying: a long-duration bet on Elon Musk's vision for space, AI, and connectivity, priced at a level that assumes most of that vision will come true. The upside is genuinely enormous. So is the risk of buying at the top."""
})

# ============================================================
# EXECUTION
# ============================================================
print("=" * 60)
print("LIFESTYLE & MARKETS WRITER — June 4, 2026")
print("=" * 60)

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:60]}...")
    print(f"Category: {article['category']}")
    print(f"{'='*60}")

    # Source image
    print("\n🖼️  Sourcing image...")
    img_url, img_attr = source_image(
        article.get("person_name"),
        article["image_queries"],
        article["slug"]
    )
    article["image_url"] = img_url
    article["image_attribution"] = img_attr or "The Videshi"

    # Validate article quality
    word_count = len(article["body"].split())
    print(f"\n📝 Word count: {word_count}")
    assert word_count >= 400, f"Article too short: {word_count} words"
    assert len(article["headline"]) <= 200, f"Headline too long: {len(article['headline'])} chars"
    assert len(article["subheadline"]) >= 15, f"Subheadline too short"
    assert article["slug"] and not article["slug"].startswith("http"), "Invalid slug"

    # Parse sources
    if isinstance(article["sources"], str):
        article["sources"] = article["sources"]  # Already JSON string

    # Insert
    print("\n💾 Inserting into database...")
    art_id = insert_article(article)
    if art_id:
        print(f"   ID: {art_id}")

    time.sleep(1)

print("\n" + "=" * 60)
print("✅ All articles processed")
print("=" * 60)
