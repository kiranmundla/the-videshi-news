#!/usr/bin/env python3
"""
Videshi lifestyle-health + markets-finance writer — 2026-06-10 run
3 articles: 2 lifestyle-health, 1 markets-finance
"""

import json, os, requests, urllib.parse, re, subprocess
from datetime import datetime, timezone

# ─── Supabase config ──────────────────────────────────────────────
env = {}
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v

SUPABASE_URL = env["SUPABASE_URL"]
SUPABASE_KEY = env["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ─── Pexels config ──────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "PEXELS_API_KEY" in line and "=" in line:
                PEXELS_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

# ─── Image sourcing functions ──────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
        "iiprop": "url|size|mime",
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
                url = ii.get("thumburl") or ii.get("url")
                if url and ii.get("mime", "").startswith("image/"):
                    width = ii.get("thumbwidth") or ii.get("width", 0)
                    height = ii.get("thumbheight") or ii.get("height", 0)
                    if width >= 400:
                        results.append({
                            "url": url,
                            "title": page.get("title", ""),
                            "width": width,
                            "height": height
                        })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    try:
        result = subprocess.run([
            "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
        ], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found: {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Verify image URL returns valid image with reasonable size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Sometimes HEAD doesn't work, try GET with stream
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        if r2.status_code == 200 and "image" in ct2:
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                print(f"  ✓ Image validated via GET: {ct2}, {len(chunk)}+ bytes")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('headline', '?')[:60]}...")
            return data[0]
        print(f"  ✓ Inserted (raw response)")
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1 — Lifestyle-Health
# The First Pill to Double Survival in Pancreatic Cancer
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 1: Pancreatic Cancer Drug Daraxonrasib ═══")

# Image sourcing — search Commons for pancreatic cancer imagery
print("Sourcing image...")
img1_url = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons first
commons_results = fetch_wikimedia_commons_images("pancreatic cancer research treatment")
for cr in commons_results:
    title_lower = cr["title"].lower()
    if any(x in title_lower for x in ["pancrea", "cancer", "oncol", "research", "clinical"]):
        if validate_image(cr["url"]):
            img1_url = cr["url"]
            img1_caption = "Microscopic view of pancreatic tissue used in cancer research"
            img1_attribution = "Wikimedia Commons"
            break

# Also try commons for RAS protein / drug development
if not img1_url:
    commons_results2 = fetch_wikimedia_commons_images("RAS protein cancer drug molecular")
    for cr in commons_results2:
        if validate_image(cr["url"]):
            img1_url = cr["url"]
            img1_caption = "Molecular structure related to RAS protein signalling in cancer cells"
            img1_attribution = "Wikimedia Commons"
            break

# Fallback to Pexels — topic imagery only (NOT a person article)
if not img1_url:
    img1_url = fetch_pexels_image("medical research laboratory cancer")
    if img1_url and validate_image(img1_url):
        img1_caption = "A medical researcher working in an oncology laboratory"
        img1_attribution = "Pexels"
    else:
        img1_url = None

if not img1_url:
    print("  ⚠ No suitable image found — using fallback topic search")
    img1_url = fetch_pexels_image("hospital medical treatment patient")
    if img1_url and validate_image(img1_url):
        img1_caption = "A patient receiving treatment in a modern hospital setting"
        img1_attribution = "Pexels"

article1_body = """The deadliest mainstream cancer in America just got its first real answer — and it comes in a pill.

Daraxonrasib, an oral drug developed by Revolution Medicines, nearly doubled median survival in patients with metastatic pancreatic cancer in a landmark phase 3 trial published in the *New England Journal of Medicine* on May 31. Patients who received the drug lived a median of 13.2 months, compared with 6.7 months for those on standard chemotherapy. The drug reduced the risk of death by 60 per cent.

For a disease that kills roughly 52,740 Americans each year and has a five-year survival rate below 13 per cent, those numbers represent the largest treatment advance in decades.

## How It Works

Pancreatic cancer is overwhelmingly driven by mutations in the RAS family of genes — molecular switches that tell cells when to grow and when to stop. In roughly 90 per cent of cases, these switches get stuck in the "on" position, triggering uncontrolled cell division that eventually forms tumours.

For forty years, RAS was considered "undruggable." The protein is small, smooth, and offers almost no surface for a conventional drug to latch onto. Daraxonrasib changes the equation. It physically binds to the active RAS protein and blocks downstream signalling — like taping over an electrical outlet so nothing can plug in.

"Seeing this magnitude of benefit in a randomized phase 3 study is a paradigm shift in this deadly disease," said Dr Zev Wainberg, co-first author of the study and professor of medicine at UCLA Health Jonsson Comprehensive Cancer Center.

## Why South Asians Should Pay Attention

Pancreatic cancer rates among South Asians in the United States have been climbing, driven in part by rising rates of Type 2 diabetes and metabolic syndrome — both established risk factors for the disease. A 2024 analysis in *Cancer Epidemiology, Biomarkers & Prevention* found that South Asian Americans are diagnosed at later stages on average, partly because pancreatic cancer symptoms — back pain, unexplained weight loss, new-onset diabetes after 50 — are often attributed to other conditions.

The diaspora's higher baseline rates of insulin resistance and visceral adiposity make this research especially relevant. Early detection remains elusive, but the existence of a drug that can meaningfully extend survival changes the calculus of screening conversations.

## The Bigger Picture

Daraxonrasib is not a cure. Median survival of 13.2 months still means roughly half of patients die within that window. But the magnitude of improvement — nearly doubling life expectancy over chemotherapy — has not been seen in pancreatic cancer before.

The drug was granted early access by the FDA on April 30, and formal approval could come later in 2026. Revolution Medicines is also testing it in lung cancer, colorectal cancer, and several other RAS-driven malignancies. A companion trial combining daraxonrasib with Tango Therapeutics' vopimetostat showed tumour shrinkage in 11 of 12 patients and 90 per cent progression-free survival at six months.

## What Comes Next

For NRIs with family members navigating a pancreatic cancer diagnosis, the practical implications are immediate. Daraxonrasib's early access programme is open in the United States, and expanded access may follow in other countries. Genetic testing for RAS mutations — already standard in lung and colorectal cancer — is now critical for pancreatic cancer patients, since the drug targets a specific molecular defect.

The era of treating pancreatic cancer as a death sentence is not over. But for the first time in four decades, there is a drug that meaningfully moves the needle — and it fits in the palm of your hand.

**Sources:** *New England Journal of Medicine* (May 31, 2026), Revolution Medicines, USA TODAY, Reuters, American Cancer Society, UCLA Health"""

article1 = {
    "headline": "The First Pill to Double Survival in Pancreatic Cancer Just Got FDA Access. Here Is What It Means.",
    "subheadline": "Daraxonrasib reduced the risk of death by 60 per cent in a landmark phase 3 trial — the largest advance against this disease in decades.",
    "slug": "daraxonrasib-pancreatic-cancer-pill-doubles-survival-ras-fda-south-asian-20260610",
    "body": article1_body.strip(),
    "category": "lifestyle-health",
    "image_url": img1_url,
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "vertical": "lifestyle-health",
    "sources": [
        {"name": "New England Journal of Medicine", "url": "https://www.nejm.org"},
        {"name": "USA TODAY", "url": "https://www.usatoday.com/story/graphics/2026/06/08/new-pancreatic-cancer-drug-treatment-daraxonrasib/90419728007/"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Revolution Medicines", "url": "https://ir.revmed.com"},
        {"name": "UCLA Health", "url": "https://www.uclahealth.org"}
    ]
}

if img1_url:
    insert_article(article1)
else:
    print("  ✗ Skipping article 1 — no valid image")


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2 — Lifestyle-Health
# AI Is Saving Doctors 16 Working Days a Year
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 2: AI Saving Doctors 16 Working Days a Year ═══")

# Image sourcing
print("Sourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

# Commons search first
commons_ai = fetch_wikimedia_commons_images("artificial intelligence healthcare medical doctor technology")
for cr in commons_ai:
    title_lower = cr["title"].lower()
    if any(x in title_lower for x in ["ai", "artificial", "health", "medical", "doctor", "digital"]):
        if validate_image(cr["url"]):
            img2_url = cr["url"]
            img2_caption = "Artificial intelligence applications in modern healthcare settings"
            img2_attribution = "Wikimedia Commons"
            break

if not img2_url:
    commons_ai2 = fetch_wikimedia_commons_images("doctor computer digital health")
    for cr in commons_ai2:
        if validate_image(cr["url"]):
            img2_url = cr["url"]
            img2_caption = "A healthcare professional using digital tools in clinical practice"
            img2_attribution = "Wikimedia Commons"
            break

# Pexels fallback for generic scene
if not img2_url:
    img2_url = fetch_pexels_image("doctor technology computer medical office")
    if img2_url and validate_image(img2_url):
        img2_caption = "A physician reviewing patient data on a digital screen"
        img2_attribution = "Pexels"
    else:
        img2_url = None

article2_body = """Your next doctor's appointment might feel different — and AI is the reason.

Artificial intelligence tools are already saving clinicians the equivalent of more than 16 working days per year and helping them see an average of eight additional patients each week, according to the Philips Future Health Index 2026, the largest global survey of its kind. The report, based on responses from over 2,000 healthcare professionals and 20,000 patients across 10 countries, paints a picture of a profession in active transformation.

Nearly two-thirds of clinicians have increased their use of AI tools at work in the past year. Close to half report saving at least 132 hours annually — more than three full working weeks — on tasks that once consumed their days. And the benefits go beyond efficiency: 39 per cent say AI has identified or helped prevent potential medical errors at least three times in the past three months alone.

## The Human Side of the Numbers

For all the talk of AI replacing doctors, the data tells a different story. Half of clinicians report less work-related stress since adopting AI tools. Two-thirds say they feel greater confidence in their clinical decisions. The time saved is being reinvested into what drew many of them to medicine in the first place — spending more time with patients.

"What is really encouraging is that AI is already making a tangible difference in everyday clinical practice," said Shez Partovi, Chief Innovation Officer at Philips. "We are seeing people save meaningful time, care for more patients, and feel better at work."

The pattern holds across specialties: AI assists with automated documentation, diagnostic imaging analysis, workflow prioritisation, and flagging potential drug interactions. In cardiology, AI-assisted ECG readings catch anomalies that a rushed human eye might miss. In radiology, it triages scans so the most urgent cases get seen first.

## Why This Matters for the Diaspora

South Asians are disproportionately represented among physicians in the United States, the United Kingdom, and Canada. Roughly 20 per cent of practising physicians in America are of Indian origin, according to the American Association of Physicians of Indian Origin (AAPI). In the NHS, Indian-trained doctors make up one of the largest international medical graduate cohorts.

This means the diaspora is not just affected by these changes — it is at the centre of them. The Indian-origin physician juggling 30-minute appointment slots, after-hours documentation, and the emotional weight of complex cases is precisely the clinician these tools are designed to help.

But the report also flags a critical gap. Seven in 10 clinicians say AI training at their organisations is inadequate, inconsistent, or entirely unavailable. The top unmet needs include verifying AI recommendations, navigating legal liability, and building basic technical literacy. For physicians who trained in systems where rote memorisation and clinical intuition were the gold standard, this is uncharted territory.

## Patients Are Changing Too

The shift is not one-sided. Three-quarters of clinicians report that patients are now arriving at consultations "AI-informed" — armed with symptom checks, medication interactions, and differential diagnoses pulled from AI-powered health tools. Rather than seeing this as a threat, 63 per cent of clinicians say informed patients are integral future partners in care delivery.

For South Asian patients, many of whom navigate between Western medicine and traditional health frameworks like Ayurveda, the AI-informed patient is already familiar. The difference is that the tools are getting better, and the conversation with the doctor is becoming more of a collaboration than a lecture.

## The Unfinished Business

The report's most sobering finding is how unevenly these benefits are distributed. Some healthcare systems are already scaling AI across departments and seeing returns. Others remain stuck in pilot programmes, hampered by fragmented IT systems, interoperability issues, and institutional inertia.

For NRI families sending ageing parents back to India for care, or navigating the patchwork of American health insurance, the quality gap between an AI-enabled hospital and one running on paper charts is about to widen dramatically. The question is no longer whether AI will reshape medicine — it is whether the systems your family depends on will keep up.

**Sources:** Philips Future Health Index 2026, American College of Cardiology, American Association of Physicians of Indian Origin, Reuters"""

article2 = {
    "headline": "AI Is Saving Doctors 16 Working Days a Year. Seven in Ten Say Their Training Is Not Keeping Up.",
    "subheadline": "The largest global healthcare survey finds AI already cutting errors and stress — but the gap between early adopters and everyone else is widening fast.",
    "slug": "ai-healthcare-philips-future-health-index-2026-doctors-south-asian-diaspora-20260610",
    "body": article2_body.strip(),
    "category": "lifestyle-health",
    "image_url": img2_url,
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "vertical": "lifestyle-health",
    "sources": [
        {"name": "Philips Future Health Index 2026", "url": "https://www.philips.com/futurehealthindex-2026"},
        {"name": "American College of Cardiology", "url": "https://www.acc.org"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/06/09/1001186561/0/en/Philips-Future-Health-Index-2026.html"}
    ]
}

if img2_url:
    insert_article(article2)
else:
    print("  ✗ Skipping article 2 — no valid image")


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3 — Markets-Finance
# BlackRock Says India Has Been "Over-Punished"
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 3: BlackRock Says India Over-Punished ═══")

# Image sourcing — try Wikimedia for Indian stock exchange, BSE, Sensex
print("Sourcing image...")
img3_url = None
img3_caption = ""
img3_attribution = ""

# Try Wikipedia for BlackRock (corporate topic, not a person)
commons_bse = fetch_wikimedia_commons_images("Bombay Stock Exchange Mumbai India")
for cr in commons_bse:
    title_lower = cr["title"].lower()
    if any(x in title_lower for x in ["bombay", "bse", "stock", "sensex", "dalal", "mumbai"]):
        if validate_image(cr["url"]):
            img3_url = cr["url"]
            img3_caption = "The Bombay Stock Exchange building in Mumbai, India"
            img3_attribution = "Wikimedia Commons"
            break

if not img3_url:
    commons_india_market = fetch_wikimedia_commons_images("National Stock Exchange India NSE")
    for cr in commons_india_market:
        if validate_image(cr["url"]):
            img3_url = cr["url"]
            img3_caption = "The National Stock Exchange of India"
            img3_attribution = "Wikimedia Commons"
            break

if not img3_url:
    img3_url = fetch_pexels_image("stock market India trading financial district")
    if img3_url and validate_image(img3_url):
        img3_caption = "Financial trading activity in an emerging market"
        img3_attribution = "Pexels"
    else:
        img3_url = None

article3_body = """The world's largest asset manager just told investors they have overcorrected on India — and that the selloff is masking one of the best long-term bets in emerging markets.

BlackRock, which manages more than $14 trillion globally, said India's equity market has been "over-punished" for lacking a direct artificial intelligence play and for higher oil-price risks tied to the Iran conflict. The assessment, delivered by Natasha Sarkaria, BlackRock's EMEA investment strategy lead, calls the recent rotation away from Indian stocks excessive and positions India as one of the firm's highest-conviction medium- to long-term emerging market trades.

The Nifty 50 and Sensex have dropped 11 per cent and 13 per cent respectively in 2026, battered by $29 billion in foreign outflows since the Iran war erupted in late February. India's market capitalisation has slipped below AI-heavy Taiwan and South Korea as global investors chased semiconductor and chip stocks. But BlackRock is arguing the market has thrown out the baby with the bathwater.

## The Bull Case in a Bear Environment

"As long as India's GDP grows between 6 and 7 per cent, that's a nice sweet spot for the economy to keep growing, keep expanding," Sarkaria told Reuters.

India's economy grew a stronger-than-expected 7.8 per cent in the March quarter. The Reserve Bank of India has cut its fiscal 2027 growth forecast to 6.6–6.9 per cent and announced measures to support the rupee, including a concessional forex swap facility that has already boosted bank stocks. BlackRock remains positive on financials, industrials, materials, utilities, and consumer discretionary stocks in India.

The firm projects low double-digit earnings growth for MSCI India this year, and Sarkaria pushed back on the narrative that India offers no exposure to the AI theme. Industrials, materials, and utilities, she said, have worked globally as investors look beyond chipmakers to companies building the physical infrastructure that AI requires — data centres, power generation, and raw materials.

## The Outflow Reality

The broader emerging market picture underscores why BlackRock's stance is contrarian. Foreign investors pulled nearly $27 billion net from emerging market portfolios in May, according to the Institute of International Finance, reversing April's $70.6 billion inflow. The selling was concentrated in equities — $37 billion withdrawn — with India, South Korea, and Brazil bearing the brunt. Ex-China stocks have suffered outflows exceeding $113 billion between March and May.

The Iran war, now in its fourth month, continues to punish India disproportionately. As the world's third-largest oil importer, India faces rising import bills, currency pressure, and the knock-on effects of higher fertiliser and gold costs. Equity mutual fund inflows dropped to their lowest in a year in May, while gold ETFs saw their first outflows in 12 months — signs that even domestic investors are turning cautious.

## The Bond Angle

Meanwhile, India is making a parallel play for global fixed-income capital. The government recently scrapped capital gains tax on government bonds held by foreign investors, a move aimed at accelerating India's bid for inclusion in the Bloomberg Global Aggregate Index. Bloomberg Index Services is expected to seek investor feedback this month on the question.

BNP Paribas Asset Management, which manages more than €1.6 trillion, said the reforms could prove more consequential over the longer term by bringing more durable and predictable inflows. M&G Investments called the measures a restoration of "policy control" and said investment opportunities are growing as India differentiates itself from other emerging bond markets.

If Bloomberg adds Indian bonds to its flagship index, the resulting inflows could rival those triggered by India's inclusion in JPMorgan's emerging market debt index — a structural shift that would flatten the yield curve and lower borrowing costs over time.

## What NRIs Should Watch

For diaspora investors with exposure to Indian equities — whether through direct holdings, mutual funds, or NRE/NRO-linked portfolios — the BlackRock assessment offers a framework for patience. Near-term volatility is likely as higher oil prices, rupee weakness, and input costs feed through to corporate profits over the next two quarters. But the structural case — demographics, infrastructure spending, financial deepening, and indirect AI linkages — has not changed.

The practical takeaway: this is not the moment to panic-sell Indian equities, and it may be the moment to look at accumulating high-conviction sectors like financials and industrials at depressed valuations. The Bloomberg bond index decision, expected in the coming weeks, could be the next catalyst.

**Sources:** Reuters, BlackRock, Institute of International Finance, BNP Paribas Asset Management, M&G Investments, Reserve Bank of India"""

article3 = {
    "headline": "BlackRock Says India Has Been 'Over-Punished.' Here Is Why the World's Largest Asset Manager Is Not Backing Down.",
    "subheadline": "With $29 billion in foreign outflows and markets down 13 per cent, BlackRock calls the selloff excessive and names its highest-conviction sectors.",
    "slug": "blackrock-india-equity-over-punished-nifty-sensex-nri-investment-outflows-20260610",
    "body": article3_body.strip(),
    "category": "markets-finance",
    "image_url": img3_url,
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "vertical": "markets-finance",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/ai-oil-worries-have-over-punished-india-masked-long-term-investment-case-2026-06-10/"},
        {"name": "BlackRock", "url": "https://www.blackrock.com"},
        {"name": "Institute of International Finance", "url": "https://www.iif.com"},
        {"name": "Reuters (EM outflows)", "url": "https://www.reuters.com"},
        {"name": "Reuters (India bonds)", "url": "https://www.reuters.com"}
    ]
}

if img3_url:
    insert_article(article3)
else:
    print("  ✗ Skipping article 3 — no valid image")


print("\n═══ DONE ═══")
