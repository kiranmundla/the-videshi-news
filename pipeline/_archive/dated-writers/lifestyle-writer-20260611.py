#!/usr/bin/env python3
"""
The Videshi Lifestyle & Markets Writer — 2026-06-11 batch
Writes 2 lifestyle-health + 1 markets-finance articles
"""

import os, json, requests, urllib.parse, uuid, re
from datetime import datetime, timezone

# Load env
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                if url and ii.get("mime", "").startswith("image/"):
                    width = ii.get("thumbwidth") or ii.get("width", 0)
                    height = ii.get("thumbheight") or ii.get("height", 0)
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": height
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a topic image using curl (urllib gets 403)."""
    if not PEXELS_API_KEY:
        return None
    import subprocess
    try:
        encoded = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={encoded}&per_page=5&orientation=landscape",
             "-H", f"Authorization: {PEXELS_API_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET for servers that don't support HEAD
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            # Read first chunk to check size
            chunk = r.raw.read(6000)
            if len(chunk) >= 5000:
                print(f"  ✓ Image validated via GET: {ct}")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Article inserted: {data[0].get('id', 'unknown')} — {article['headline']}")
            return data[0]
        print(f"  ✓ Article inserted: {article['headline']}")
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ================================================================
# ARTICLE 1: VERVE-102 Gene Editing — Lifestyle-Health
# ================================================================
print("\n=== ARTICLE 1: VERVE-102 Gene Editing Cholesterol Shot ===")

# Image: Search for gene editing / CRISPR / cholesterol
print("Sourcing image...")
img1_url = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons for CRISPR/gene editing
commons_results = fetch_wikimedia_commons_images("CRISPR gene editing therapy")
for r in commons_results:
    if r["width"] >= 600 and validate_image(r["url"]):
        img1_url = r["url"]
        img1_caption = "CRISPR gene editing technology used in the VERVE-102 therapy"
        img1_attribution = "Wikimedia Commons"
        break

if not img1_url:
    commons_results = fetch_wikimedia_commons_images("gene therapy cardiovascular")
    for r in commons_results:
        if r["width"] >= 600 and validate_image(r["url"]):
            img1_url = r["url"]
            img1_caption = "Gene therapy research targeting cardiovascular disease"
            img1_attribution = "Wikimedia Commons"
            break

if not img1_url:
    img1_url = fetch_pexels_image("DNA laboratory medical research")
    if img1_url and validate_image(img1_url):
        img1_caption = "Laboratory research into gene-based medical treatments"
        img1_attribution = "Pexels"
    else:
        img1_url = None

article1_body = """One injection. One appointment. And your cholesterol drops by 62 per cent — permanently.

That is the promise of VERVE-102, a gene-editing therapy developed by Eli Lilly that has just delivered its most compelling clinical data yet. Published in *The New England Journal of Medicine* in May 2026, the Phase I Heart-2 trial showed a single intravenous infusion reduced LDL cholesterol by up to 62 per cent and the PCSK9 protein by up to 88 per cent. The effects held steady for at least 18 months.

For South Asians, who suffer from coronary artery disease at rates two to four times higher than the general population and often a full decade earlier, this is not an incremental advance. It is a potential inflection point.

## How It Works

VERVE-102 uses base editing, a refined form of CRISPR gene editing, to disable the PCSK9 gene in the liver. PCSK9 is a protein that destroys the receptors responsible for clearing LDL — so-called bad cholesterol — from the bloodstream. By switching off the gene that makes it, the therapy mimics a naturally occurring mutation found in people who are born with lifelong low cholesterol and virtually no heart disease.

"There's actually human beings that are born with naturally occurring mutations in this same gene that lead to lifelong, low cholesterol levels, and they have no side effects," said Dr Joshua Knowles, a cardiologist at Stanford Medicine. "The idea was: can we mimic that through this kind of CRISPR editing approach?"

The therapy is delivered using a lipid nanoparticle — essentially a molecular envelope engineered to carry the gene-editing machinery directly to the liver. An earlier version caused some liver toxicity in initial patients, but the reformulated delivery system in VERVE-102 was well tolerated across all 35 trial participants. No serious adverse events were reported.

## Why South Asians Should Be Watching

Heart disease is the leading killer of South Asians worldwide, and the diaspora carries its own set of compounding risk factors: higher rates of insulin resistance, smaller and denser LDL particles that are harder to clear, elevated lipoprotein(a), and a genetic predisposition to metabolic syndrome.

Statins, the default treatment for decades, work for many — but compliance is a persistent problem. Roughly half of patients stop taking them within a year, often citing muscle pain, fatigue, or simply forgetting. PCSK9 inhibitor injections, available since 2015, are more effective but require shots every two weeks or visits every six months. Insurance often denies them.

A one-time treatment that permanently lowers cholesterol eliminates the compliance problem entirely. For NRI families watching parents in India manage five or six medications a day, or for first-generation immigrants who skipped their own screening because the system felt too complicated, VERVE-102 represents something qualitatively different: a treatment that works even if you never come back.

## What Comes Next

Eli Lilly has received FDA fast-track designation for VERVE-102 and plans to begin Phase 2 trials by the end of 2026. The expanded study will involve several hundred patients with hyperlipidemia and high cardiovascular risk — a population that disproportionately includes South Asians.

The cost question looms large. Gene therapies in other fields have launched at price points north of $500,000 per treatment. Lilly has not disclosed pricing, but the company's bet is that the maths will work out: the lifetime savings from preventing heart attacks, stent placements, and chronic medication could offset a steep upfront cost.

"The idea that this would be kind of a one-and-done approach — maybe the expense would be high upfront, but the downstream savings would be high later," Dr Knowles said.

Whether insurers, governments, and healthcare systems agree is another matter entirely. But for a community that has been managing the world's highest burden of heart disease with century-old tools, the possibility of editing the problem at its genetic source is worth more than cautious optimism.

It is worth watching very closely.

*Sources: The New England Journal of Medicine (May 2026), KTVU/Stanford Medicine, Eli Lilly corporate communications, European Journal of Preventive Cardiology*"""

article1 = {
    "headline": "One Shot to End Cholesterol for Life. A Gene-Editing Therapy Just Proved It Can Be Done.",
    "subheadline": "VERVE-102 reduced LDL by 62 per cent with a single injection. For South Asians carrying the world's highest heart disease burden, this is not incremental. It is foundational.",
    "body": article1_body,
    "slug": "verve-102-gene-editing-cholesterol-one-shot-lilly-south-asian-heart-disease-20260611",
    "category": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": img1_url or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": json.dumps([
        {"name": "The New England Journal of Medicine", "url": "https://www.nejm.org"},
        {"name": "KTVU / Stanford Medicine", "url": "https://ktvu.com/news/no-more-statins-one-time-treatment-high-cholesterol-could-lower-heart-attack-risk-life"},
        {"name": "Eli Lilly", "url": "https://www.lilly.com"},
        {"name": "Wikipedia - Verve PCSK9 Gene Therapy", "url": "https://en.wikipedia.org/wiki/Verve_PCSK9-inhibitor_gene_therapy"}
    ])
}

if img1_url:
    result1 = insert_article(article1)
else:
    print("  ⚠ No image found, inserting without image")
    article1["image_url"] = ""
    result1 = insert_article(article1)


# ================================================================
# ARTICLE 2: Vitamin D — Lifestyle-Health
# ================================================================
print("\n=== ARTICLE 2: Vitamin D Deficiency Year-Round in South Asians ===")

print("Sourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

# Wikimedia Commons for vitamin D / sunlight / supplements
commons_results = fetch_wikimedia_commons_images("vitamin D supplement sunlight")
for r in commons_results:
    if r["width"] >= 600 and validate_image(r["url"]):
        img2_url = r["url"]
        img2_caption = "Vitamin D supplements may be necessary year-round for South Asians"
        img2_attribution = "Wikimedia Commons"
        break

if not img2_url:
    img2_url = fetch_pexels_image("vitamin D sunlight health supplements")
    if img2_url and validate_image(img2_url):
        img2_caption = "Vitamin D deficiency persists even during summer months for some groups"
        img2_attribution = "Pexels"
    else:
        img2_url = None

article2_body = """Every summer, the same assumption returns: get outside more, and your vitamin D will sort itself out. For South Asians living in the West, a new study says that assumption is dangerously wrong.

Researchers at Newcastle University have found that vitamin D levels remained consistently low throughout the year among older adults and people from minoritised ethnic backgrounds in northern Britain — even during peak summer months. The study, published in the *European Journal of Clinical Nutrition*, analysed nearly 300 participants and found that the expected seasonal recovery in vitamin D simply did not happen.

More than half of older adults had insufficient vitamin D. Among participants from minoritised ethnic groups, the rates were even higher.

## Why South Asians Are Especially Vulnerable

The biology is straightforward and unforgiving. Vitamin D is produced when ultraviolet B rays from the sun reach the skin. Darker skin pigmentation — common across the South Asian population — contains more melanin, which acts as a natural sunscreen and reduces UVB absorption by up to 50 per cent compared to lighter skin. In northern latitudes like the UK, Canada, and much of the northern United States, UVB intensity is already weak for seven to eight months of the year.

The result is a double filter: reduced UVB reaching the skin, and reduced skin capacity to convert what does arrive.

Add to this the cultural factors that compound the deficit. Many South Asian women wear clothing that covers the arms and legs, reducing sun exposure. Traditional diets, while nutritionally rich, are often low in vitamin D — paneer, dal, and roti do not naturally contain meaningful amounts unless fortified. And the diaspora's indoor-heavy work culture, from long office hours to screen-dominated evenings, further limits sun exposure.

Studies have repeatedly shown that South Asians in the UK have some of the lowest vitamin D levels of any ethnic group. A 2023 Lancet review found that 70 to 100 per cent of South Asians in northern Europe were vitamin D deficient, compared with 30 to 40 per cent of the general white population.

## The Health Consequences Are Not Subtle

Vitamin D is not a wellness fad. It is essential for calcium absorption, bone density, and immune function. Chronic deficiency has been linked to osteoporosis, muscle weakness, increased fracture risk, and impaired immune response. Emerging research has also connected low vitamin D to higher rates of cardiovascular disease, type 2 diabetes, and certain cancers — conditions that already disproportionately affect South Asians.

For older adults in the diaspora, the risks compound. Bone density declines with age, and vitamin D deficiency accelerates that decline. Falls and fractures — the cascade that begins with a stumble and ends in a hospital bed — are significantly more common in vitamin D-deficient older adults.

"What's striking about these findings is that vitamin D levels didn't improve, even in the summer months when we would usually expect them to recover," said Professor Bernard Corfe, co-leader of the study. "If you are in a higher-risk group, you can't assume that spending more time outdoors in summer will solve the problem."

## What the Diaspora Should Actually Do

The NHS has recommended since 2016 that everyone in the UK take a daily 10-microgram (400 IU) vitamin D supplement from October through March. For South Asians, the evidence increasingly suggests that this should be year-round — and possibly at higher doses.

The Indian Council of Medical Research recommends 600 IU daily for adults, but many endocrinologists treating vitamin D deficiency in South Asian patients prescribe 1,000 to 2,000 IU daily as a maintenance dose, with higher loading doses for those already deficient.

Dietary adjustments can help at the margins. Oily fish (salmon, mackerel, sardines), egg yolks, and fortified foods like cereals and plant milks provide some vitamin D. But diet alone is rarely sufficient to correct deficiency, particularly in populations with multiple risk factors.

The simplest intervention is a daily supplement. They cost less than a cup of chai. And yet uptake among South Asians remains stubbornly low — in part because the condition is invisible until it is not.

The next phase of the Newcastle study will focus on developing culturally appropriate approaches to improving vitamin D levels, including tailored dietary advice and community health programmes.

Until then, the message is simple: the sun is not enough.

*Sources: European Journal of Clinical Nutrition (May 2026), Newcastle University, The Lancet (2023 review), NHS UK guidelines, Indian Council of Medical Research*"""

article2 = {
    "headline": "The Sun Cannot Save You. A New Study Says South Asians Stay Vitamin D Deficient All Year.",
    "subheadline": "Newcastle University found that ethnic minorities in Britain showed no seasonal recovery in vitamin D — even in summer. The diaspora's biology, diet, and lifestyle make this a year-round problem with no passive fix.",
    "body": article2_body,
    "slug": "vitamin-d-deficiency-year-round-south-asian-diaspora-newcastle-study-20260611",
    "category": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": img2_url or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": json.dumps([
        {"name": "European Journal of Clinical Nutrition", "url": "https://doi.org/10.1038/s41430-026-01760-z"},
        {"name": "SciTechDaily / Newcastle University", "url": "https://scitechdaily.com/researchers-discover-a-hidden-vitamin-d-problem-that-persists-year-round/"},
        {"name": "Medical Dialogues", "url": "https://medicaldialogues.in"},
        {"name": "NHS UK", "url": "https://www.nhs.uk/conditions/vitamins-and-minerals/vitamin-d/"}
    ])
}

if img2_url:
    result2 = insert_article(article2)
else:
    print("  ⚠ No image found, inserting without image")
    article2["image_url"] = ""
    result2 = insert_article(article2)


# ================================================================
# ARTICLE 3: NRI Deposit Rate Surge — Markets-Finance
# ================================================================
print("\n=== ARTICLE 3: NRI Fixed Deposit Rates Surge ===")

print("Sourcing image...")
img3_url = None
img3_caption = ""
img3_attribution = ""

# Try Wikipedia for RBI
wiki_rbi = fetch_wikipedia_person_image("Reserve Bank of India")
if wiki_rbi and validate_image(wiki_rbi):
    img3_url = wiki_rbi
    img3_caption = "The Reserve Bank of India headquarters in Mumbai"
    img3_attribution = "Wikimedia Commons"

if not img3_url:
    commons_results = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai")
    for r in commons_results:
        if r["width"] >= 600 and validate_image(r["url"]):
            img3_url = r["url"]
            img3_caption = "The Reserve Bank of India, which announced the FCNR deposit incentives"
            img3_attribution = "Wikimedia Commons"
            break

if not img3_url:
    img3_url = fetch_pexels_image("Indian currency finance banking")
    if img3_url and validate_image(img3_url):
        img3_caption = "Indian banks are offering unprecedented rates on NRI foreign currency deposits"
        img3_attribution = "Pexels"
    else:
        img3_url = None

article3_body = """If you are an NRI with dollars sitting in a US savings account earning 4 per cent, Indian banks just made you a better offer. Some of them are offering nearly double.

In a coordinated response to the Reserve Bank of India's new foreign exchange incentive package, at least half a dozen Indian banks hiked interest rates on Foreign Currency Non-Resident — or FCNR(B) — deposits by as much as 300 basis points on Tuesday. The rates, effective immediately, represent the most aggressive NRI deposit pricing India has seen in years.

AU Small Finance Bank is now offering 7.10 per cent on three-year US dollar deposits. Yes Bank is at 7 per cent for three years and 7.10 per cent for five. Karur Vysya Bank and Tamilnad Mercantile Bank have both moved to 7 per cent for three-to-five-year maturities, up from under 4 per cent just days earlier. HDFC Bank, India's largest private lender, hiked by 235 to 265 basis points to 6 per cent. State Bank of India, the country's largest bank, raised rates by up to 300 basis points, now offering 5.25 to 6 per cent depending on deposit size and tenure.

More banks are expected to announce revised rates this week.

## Why Now

The catalyst is the RBI's June 6 forex package, the most sweeping set of measures the central bank has deployed this year to attract dollar inflows and stabilise the rupee.

The rupee has been Asia's second-worst performing currency in 2026, falling 6 per cent against the dollar and hitting record lows in May. Capital outflows, elevated oil import costs from the Iran conflict, and a widening current account deficit have all conspired to drain foreign exchange reserves.

The RBI's response was multi-pronged. The centrepiece: the central bank will bear the full hedging cost for banks raising fresh three-to-five-year FCNR(B) deposits until 30 September 2026. Hedging cost — the price of protecting against rupee-dollar exchange rate fluctuations — has historically eaten 1.5 to 2.5 percentage points of the return on dollar deposits in India. By absorbing this cost, the RBI has effectively unlocked that margin for banks to pass on to depositors.

Fresh deposits raised under the scheme are also exempt from cash reserve ratio (CRR) and statutory liquidity ratio (SLR) requirements — meaning banks can lend out the full amount rather than parking a chunk with the RBI. This makes each deposit dollar more profitable and gives banks even more room to offer competitive rates.

## The NRI Calculation

For an NRI in the United States, the comparison is now stark.

A high-yield savings account at Marcus, Ally, or Wealthfront currently pays 3.8 to 4.2 per cent. A three-year CD at a US bank pays roughly 4.0 to 4.5 per cent. An FCNR(B) deposit at AU Small Finance Bank pays 7.10 per cent — on a US dollar deposit, in US dollars, with no currency risk on principal or interest.

The last point is critical. Unlike NRE (Non-Resident External) deposits, which are denominated in rupees and expose the depositor to exchange rate fluctuations, FCNR(B) deposits are held in foreign currency. You put in dollars, you get back dollars plus interest. The exchange rate risk is the bank's problem, not yours.

Interest earned on FCNR(B) deposits is also tax-free in India. In the US, it is taxable as ordinary income, but the higher rate still delivers a significant after-tax advantage over domestic alternatives for most NRIs.

SBI economists estimate that $40 to $45 billion could flow into the FCNR(B) route under this window. The RBI has also opened the door for banks to provide guarantees to offshore lenders who lend to NRIs — allowing NRIs to borrow abroad at lower rates and deposit the funds in India at the higher FCNR(B) rates. In one illustrative scenario cited by CNBC-TV18, an NRI with $100,000 in capital leveraging this structure could effectively double their money in three years.

## The Catch

The window is temporary. The RBI's hedging subsidy runs until September 30, 2026, and the swap facility until October 16. Once the window closes, banks will almost certainly cut rates back to their pre-incentive levels.

There is also counterparty risk to consider. FCNR(B) deposits are covered by the Deposit Insurance and Credit Guarantee Corporation (DICGC) up to ₹5 lakh per bank — roughly $6,000 at current rates. For deposits above that threshold, particularly at smaller banks offering the highest rates, the protection is minimal. Sticking with SBI or HDFC Bank for larger deposits means accepting a slightly lower rate in exchange for systemic safety.

And for NRIs who need liquidity, the three-to-five-year lock-in is non-trivial. Premature withdrawal typically forfeits a significant portion of the interest earned.

## What to Do

For NRIs with idle dollar savings — particularly those who do not need the funds for three to five years — the current FCNR(B) window is arguably the best risk-adjusted return available anywhere in the dollar-denominated deposit market right now. The combination of RBI-backed hedging, tax-free interest in India, and rates that are 200 to 300 basis points above US alternatives is unusual.

The window will not last. If you are going to move, the time is now — or at least before September.

*Sources: Reuters, The Hindu BusinessLine, Storyboard18/CNBC-TV18, RBI circular (June 6, 2026), ainvest.com*"""

article3 = {
    "headline": "Indian Banks Are Offering NRIs 7 Per Cent on Dollar Deposits. The Window Closes in September.",
    "subheadline": "The RBI just removed the hedging cost that kept FCNR rates low. AU Small Finance Bank is at 7.10 per cent. SBI moved 300 basis points in a day. Here is what every NRI with idle dollars needs to know.",
    "body": article3_body,
    "slug": "nri-fcnr-deposit-rates-7-percent-rbi-hedging-subsidy-september-window-20260611",
    "category": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": img3_url or "",
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "Storyboard18 / CNBC-TV18", "url": "https://storyboard18.com"},
        {"name": "RBI", "url": "https://www.rbi.org.in"},
        {"name": "ainvest", "url": "https://www.ainvest.com"}
    ])
}

if img3_url:
    result3 = insert_article(article3)
else:
    print("  ⚠ No image found, inserting without image")
    article3["image_url"] = ""
    result3 = insert_article(article3)

print("\n=== DONE ===")
print(f"Articles inserted: {sum(1 for r in [result1, result2, result3] if r)}/3")
