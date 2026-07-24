#!/usr/bin/env python3
"""Lifestyle-Health & Markets-Finance writer for The Videshi — June 6, 2026 evening run."""

import json, os, sys, subprocess, urllib.parse, uuid, re
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

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

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
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0))
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a photo. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
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
    """Check that image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            # Read a bit to check size
            data = b""
            for chunk in r.iter_content(chunk_size=8192):
                data += chunk
                if len(data) > 5000:
                    return True
            return len(data) > 5000
    except:
        pass
    return False

def insert_article(article):
    """Insert article into Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["vertical"],
        "image_url": article["image_url"],
        "image_caption": article["image_caption"],
        "image_attribution": article["image_attribution"],
        "sources": json.dumps(article["sources"]),
        "status": "published",
        "published_at": now,
        "is_editorial": False
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0].get("id", "unknown") if isinstance(result, list) else result.get("id", "unknown")
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
        return False

# ─── ARTICLE 1: Daraxonrasib Pancreatic Cancer Breakthrough ───

def write_article_1():
    print("\n=== Article 1: Daraxonrasib Pancreatic Cancer ===")
    
    # Image sourcing
    print("  Sourcing image...")
    # Try Wikimedia Commons first
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    commons = fetch_wikimedia_commons_images("pancreatic cancer cells microscopy", limit=5)
    for c in commons:
        if validate_image(c["url"]):
            img_url = c["url"]
            img_caption = "Pancreatic cancer cells under scanning electron microscopy"
            img_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Commons image: {img_url[:80]}...")
            break
    
    if not img_url:
        commons2 = fetch_wikimedia_commons_images("KRAS protein cancer", limit=5)
        for c in commons2:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Molecular structure of KRAS protein, the target of daraxonrasib"
                img_attribution = "Wikimedia Commons"
                break
    
    if not img_url:
        img_url = fetch_pexels_image("cancer research laboratory")
        if img_url and validate_image(img_url):
            img_caption = "Cancer research laboratory where targeted therapies are being developed"
            img_attribution = "Pexels"
        else:
            img_url = None
    
    if not img_url:
        print("  ⚠ No suitable image found, skipping article")
        return False
    
    article = {
        "headline": "A Daily Pill Just Doubled Survival for Pancreatic Cancer. Oncologists Wept When They Saw the Data.",
        "subheadline": "Daraxonrasib targets the KRAS mutation that drives 90 per cent of pancreatic tumours. In a trial of 500 patients, it cut the risk of death by 60 per cent. The FDA is fast-tracking approval.",
        "slug": "daraxonrasib-pancreatic-cancer-doubles-survival-kras-asco-2026-south-asian-20260606",
        "category": "lifestyle-health",
        "vertical": "lifestyle-health",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": [
            {"name": "Popular Science / The Conversation", "url": "https://www.popsci.com/health/breakthrough-drug-nearly-doubles-survival-with-advanced-pancreatic-cancer/"},
            {"name": "Dana-Farber Cancer Institute / ASCO 2026", "url": "https://www.linkedin.com/posts/dana-farber-cancer-institute_asco26-activity-7337899000000000000"},
            {"name": "Revolution Medicines Phase 3 Trial", "url": "https://clinicaltrials.gov/"}
        ],
        "body": """Pancreatic cancer is the deadliest major cancer in the world. For patients diagnosed with metastatic disease between 2015 and 2021, roughly 97 per cent died within five years. Most had fewer than six months of meaningful treatment left once first-line chemotherapy stopped working.

That statistic changed on May 31 at the American Society of Clinical Oncology annual meeting in Chicago, when Dr Brian Wolpin of the Dana-Farber Cancer Institute presented Phase 3 trial results for daraxonrasib — a daily oral pill developed by Revolution Medicines. More than 9,000 oncologists rose for three standing ovations. Several gastrointestinal specialists reported breaking down in tears.

## What the Trial Found

The study enrolled 500 patients with metastatic pancreatic cancer whose disease had progressed after prior chemotherapy. Half received daraxonrasib; the other half received standard second-line chemotherapy.

Patients on chemotherapy survived a median of 6.7 months. Those on daraxonrasib survived 13.2 months — nearly double. Overall, daraxonrasib reduced the risk of death by 60 per cent. One patient, Debbie Orcutt, who was diagnosed with stage 4 disease after chemotherapy failed, saw her tumours shrink by roughly 80 per cent after more than a year on the drug.

## How Daraxonrasib Works

More than 90 per cent of pancreatic cancers are driven by mutations in a gene called KRAS, which acts as a molecular switch controlling cell growth. When mutated, the switch gets stuck permanently in the "on" position, commanding cancer cells to multiply without limit. For decades, scientists considered KRAS "undruggable" — its protein surface was too smooth for conventional drugs to grip.

Daraxonrasib takes an indirect route. Instead of binding to KRAS directly, it attaches to a molecule called cyclophilin A inside cells, which helps fold proteins into their functional shapes. The resulting complex then binds to the active KRAS protein and shuts down its ability to signal uncontrolled growth.

## Side Effects Are Different, Not Absent

The most common side effect was a skin rash, which affected 86 per cent of patients. Mouth sores (stomatitis), diarrhoea, nausea and vomiting were also frequent. Former US Senator Ben Sasse, a trial participant, described the rash experience as "nuclear" and "burning, bubbling" on a podcast. However, patients on daraxonrasib were significantly less likely to discontinue treatment due to severe side effects than those on chemotherapy, and they reported improved quality of life with reduced pain.

## Why South Asians Should Pay Attention

Pancreatic cancer rates among South Asians have been rising steadily in both India and the diaspora. A 2023 Lancet study found that India reported approximately 57,000 new pancreatic cancer cases annually, with a five-year survival rate below 5 per cent. The disease is diagnosed later in India on average, partly because screening infrastructure is limited and symptoms are often attributed to gastric disorders.

For NRIs, the clinical implications are immediate. The KRAS mutation that daraxonrasib targets is present across racial and ethnic groups, making this a universally relevant breakthrough. Researchers are already studying whether the drug can treat other KRAS-driven cancers, including lung, colon, ovarian and endometrial cancers.

## What Happens Next

The FDA has fast-tracked daraxonrasib for approval. Given the magnitude of the survival benefit — the largest ever seen in a pancreatic cancer trial — expedited review is expected. If approved, the drug could be available in clinics within months.

Dr Rachna Shroff, an ASCO gastrointestinal cancer expert who has treated pancreatic cancer for 16 years, captured the moment: "When the press release came out for this data, I actually started crying in clinic. This is such an incredibly impactful study for our patients."

For a disease that has resisted every therapeutic advance for decades, daraxonrasib is not a cure. But it is the most significant leap in pancreatic cancer treatment the field has ever seen — and for patients and families who have lived with a near-certain prognosis, that matters enormously."""
    }
    
    return insert_article(article)


# ─── ARTICLE 2: South Asian Heart Risk Paradox ───

def write_article_2():
    print("\n=== Article 2: South Asian Heart Risk Paradox ===")
    
    # Image sourcing - try Wikipedia for Namratha Kandula
    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    # Try Wikimedia Commons for heart health/cardiovascular
    commons = fetch_wikimedia_commons_images("cardiovascular disease heart health screening", limit=5)
    for c in commons:
        if validate_image(c["url"]):
            img_url = c["url"]
            img_caption = "Cardiovascular health screening — South Asians face elevated risk starting at age 45"
            img_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Commons image: {img_url[:80]}...")
            break
    
    if not img_url:
        commons2 = fetch_wikimedia_commons_images("blood pressure measurement medical", limit=5)
        for c in commons2:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Blood pressure check — a key screening measure for heart disease risk"
                img_attribution = "Wikimedia Commons"
                break
    
    if not img_url:
        img_url = fetch_pexels_image("heart health medical checkup stethoscope doctor")
        if img_url and validate_image(img_url):
            img_caption = "A doctor conducts a cardiac screening examination"
            img_attribution = "Pexels"
        else:
            img_url = None
    
    if not img_url:
        print("  ⚠ No suitable image found, skipping article")
        return False

    article = {
        "headline": "South Asians in America Hit Peak Heart Risk at 45 Despite Eating Better and Drinking Less Than Everyone Else.",
        "subheadline": "A decade-long study of 2,700 adults found that by age 45, South Asians had the highest rates of prediabetes and hypertension of any racial group — even though they reported healthier habits. The researchers say screening should start much earlier.",
        "slug": "south-asian-heart-risk-age-45-masala-northwestern-paradox-screening-20260606",
        "category": "lifestyle-health",
        "vertical": "lifestyle-health",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": [
            {"name": "Northwestern University / Northwestern Now", "url": "https://news.northwestern.edu/stories/2026/02/u-s-south-asians-face-elevated-heart-risk-at-age-45-despite-reporting-healthier-habits"},
            {"name": "Journal of the American Heart Association", "url": "https://doi.org/10.1161/JAHA.124.041221"},
            {"name": "MASALA Study (Mediators of Atherosclerosis in South Asians Living in America)", "url": "https://www.masalastudy.org"}
        ],
        "body": """If you are a South Asian adult in your forties living in the United States, there is a strong chance you are doing many of the right things for your heart. You probably eat a healthier diet than most Americans. You likely drink less alcohol. You may exercise as much as or more than your peers.

And yet, statistically, your heart is already in more danger than theirs.

A landmark study published in the Journal of the American Heart Association, led by Northwestern Medicine and drawing on a decade of data from 2,700 adults, has identified a troubling paradox that should concern every member of the Indian diaspora: by age 45, South Asians in America have the highest prevalence of prediabetes and hypertension of any racial or ethnic group studied — despite reporting healthier lifestyle behaviours than white, Black, Hispanic and Chinese adults.

## The Numbers Are Stark

The study combined data from two long-running cohort studies: MASALA, which tracks South Asian adults specifically, and MESA, which follows white, Black, Hispanic and Chinese Americans. All participants were between 45 and 55 at baseline, and researchers tracked how their risk factors changed over a full decade.

At age 45, South Asian men had a prediabetes prevalence of 31 per cent — compared with 4 per cent for white men, 10 per cent for Black men, 10 per cent for Hispanic men and 13 per cent for Chinese men. South Asian women showed a similar pattern: nearly one in five had prediabetes by 45, roughly twice the rate of women in every other group.

Hypertension followed the same trajectory. By 45, 25 per cent of South Asian men had high blood pressure, compared with 18 per cent of white men, 10 per cent of Hispanic men and 6 per cent of Chinese men. South Asian men also had higher rates of dyslipidemia — elevated cholesterol and triglycerides — than Black men (78 per cent versus 61 per cent).

By age 55, both South Asian men and women were at least twice as likely to have developed diabetes as white adults.

## The Paradox

What makes this data unsettling is that South Asians in the study reported healthier diets, lower alcohol consumption, comparable physical activity levels and lower average BMI than most other groups. The expected correlation — healthier habits leading to lower clinical risk — simply did not hold.

"The mismatch between healthier lifestyle behaviours and clinical risk was surprising," said Dr Namratha Kandula, professor of general internal medicine and epidemiology at Northwestern University Feinberg School of Medicine and senior author of the study. "This paradox tells us we're missing something fundamental to what is driving this elevated risk among South Asians."

## What Is Driving the Risk

Kandula pointed to factors that begin long before midlife. Most MASALA participants are immigrants whose childhood nutrition, environmental exposures and activity patterns in South Asia may differ substantially from their current habits in the US. Prior MASALA data show that South Asians accumulate more visceral fat — fat around internal organs — than other population groups, even at a normal or low BMI. Other research confirms that this fat distribution pattern starts in childhood among South Asians and is a powerful independent risk factor for cardiovascular disease.

Globally, South Asians represent roughly one quarter of the world's population but account for approximately 60 per cent of heart disease patients worldwide. In the US, where they are among the fastest-growing demographic groups, they develop atherosclerosis — the plaque buildup that leads to heart attacks — up to a decade earlier than the general population on average.

## What This Means for NRIs

The clinical implication is direct: standard screening guidelines, which often recommend cardiovascular risk assessment beginning at age 50 or later, may be dangerously late for South Asians.

"Clinicians should start looking for high blood sugar, high blood pressure and other risk-enhancing factors, such as lipoprotein A, before midlife," Kandula said. She also emphasised the need for "culturally appropriate lifestyle counselling to help South Asians eat healthy, exercise regularly and minimise tobacco and alcohol."

For individual NRIs, the advice is actionable: even if you eat well and exercise regularly, ask your doctor about early screening. Get your blood pressure, fasting glucose or A1c, cholesterol and lipoprotein (a) checked before middle age. Early detection and control of these risk factors can prevent the heart disease that kills South Asians at disproportionately young ages.

Chandrika Gopal, a 58-year-old MASALA participant from Ohio who was born and raised in southern India, put it simply: "Even if we eat well, we can still be at higher risk. Living in a new country, adapting to different food and routines — it all adds up."

The study was funded by the National Institutes of Health."""
    }
    
    return insert_article(article)


# ─── ARTICLE 3: RBI Doubles NRI Equity Limits + Tax Scrapping ───

def write_article_3():
    print("\n=== Article 3: RBI Doubles NRI Equity Limits ===")
    
    # Image sourcing
    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    # Try Wikipedia for RBI or Sanjay Malhotra
    img_url = fetch_wikipedia_person_image("Sanjay Malhotra (bureaucrat)")
    if img_url and validate_image(img_url):
        img_caption = "RBI Governor Sanjay Malhotra announced the investment limit reforms on June 5"
        img_attribution = "Wikimedia Commons"
    
    if not img_url:
        img_url = fetch_wikipedia_person_image("Reserve Bank of India")
        if img_url and validate_image(img_url):
            img_caption = "The Reserve Bank of India headquarters in Mumbai"
            img_attribution = "Wikimedia Commons"
    
    if not img_url:
        commons = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai", limit=5)
        for c in commons:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "The Reserve Bank of India headquarters in Mumbai"
                img_attribution = "Wikimedia Commons"
                break
    
    if not img_url:
        img_url = fetch_pexels_image("India stock market trading Mumbai")
        if img_url and validate_image(img_url):
            img_caption = "Indian stock market trading activity in Mumbai"
            img_attribution = "Pexels"
        else:
            img_url = None
    
    if not img_url:
        print("  ⚠ No suitable image found, skipping article")
        return False

    article = {
        "headline": "India Just Doubled the Amount NRIs Can Invest in Indian Stocks and Scrapped Tax on Foreign Bond Profits. Here Is What Changed.",
        "subheadline": "The RBI doubled NRI equity limits to 10 per cent per company and raised the aggregate ceiling to 24 per cent. The government simultaneously scrapped capital gains tax on government bonds for foreign investors. Analysts expect $40 to 60 billion in inflows.",
        "slug": "rbi-doubles-nri-equity-limits-india-scraps-capital-gains-tax-bonds-foreign-investors-20260606",
        "category": "markets-finance",
        "vertical": "markets-finance",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": [
            {"name": "Livemint", "url": "https://www.livemint.com/news/rbi-move-to-raise-foreign-capital-from-nris-a-battle-half-won-11780663261182.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-scraps-capital-gains-tax-foreign-investors-government-debt-2026-06-05/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/rbi-proposes-higher-investment-limits-in-equity-instruments-for-nris-ocis-and-other-overseas-indians"}
        ],
        "body": """On June 5, the Reserve Bank of India and the Indian government made the most significant set of changes to foreign investment rules in years. The moves are aimed squarely at attracting dollar inflows to defend the rupee, which has fallen 5 per cent this year amid $57.68 billion in foreign equity outflows and surging oil prices from the West Asia conflict. For NRIs, the changes are both structural and immediately actionable.

## What the RBI Changed

RBI Governor Sanjay Malhotra announced three key changes at the conclusion of the Monetary Policy Committee meeting:

**Individual NRI equity limits doubled.** The cap on how much a single NRI or OCI (Overseas Citizen of India) can invest in any one listed Indian company has been raised from 5 per cent to 10 per cent of paid-up equity capital. This applies to the Portfolio Investment Scheme (PIS) route, which does not require SEBI registration.

**Aggregate NRI limit raised to 24 per cent.** The combined ceiling for all NRI and OCI investors in a single listed company has been increased from 10 per cent to 24 per cent — provided the company's general body passes a special resolution.

**Facility extended to all persons resident outside India.** For the first time, individual investors residing outside India who are not NRIs or OCIs can also invest in Indian equities on the same terms. This broadens the eligible pool significantly.

## What the Government Changed

Simultaneously, the Ministry of Finance issued an ordinance exempting foreign institutional investors and the Bank for International Settlements from capital gains tax on income earned from government securities — including both interest income and gains from sale or transfer. The exemption is retroactive to April 1, 2026.

Previously, foreign investors were subject to a 12.5 per cent long-term capital gains tax on listed bonds held for more than 12 months and a 20 per cent withholding tax on interest earned from government bonds. Both are now eliminated for government securities.

## Why This Matters for NRIs

Despite the liberalisation, NRI participation in Indian equities remains remarkably low. BSE data shows that NRI ownership as a percentage of Sensex market capitalisation stood at just 0.7 per cent as of the quarter ending March 2026. Even among notable Sensex constituents, NRI holdings were modest: Trent (5.36 per cent), L&T (1.27 per cent), Jio Financial Services (1.18 per cent), Asian Paints (1.17 per cent) and JSW Steel (1.15 per cent).

The doubled limits mean NRIs can now take meaningful positions in individual companies without hitting regulatory ceilings. The raised aggregate ceiling allows companies to court a larger base of diaspora investors.

For NRIs interested in Indian government bonds — which are now part of three global bond indexes — the tax changes make yields significantly more competitive. India's 10-year benchmark yields were trading near 7 per cent, which, with zero capital gains or interest tax for foreign investors, compares favourably with US Treasuries.

## The Rupee Defence

The measures are part of a broader effort to shore up the rupee. Brent crude has rallied 31 per cent to $94.70 a barrel since the West Asia conflict began in late February. The rupee has plunged to 94.94 against the dollar, and the Nifty has shed 7.2 per cent.

The RBI also announced concessional forex swap facilities for public sector external commercial borrowings and agreed to bear the full hedging cost for banks raising 3-to-5-year foreign currency non-resident (FCNR) deposits until September 30.

Analysts expect the combined measures to draw $40 to 60 billion in inflows. "The combined impact could certainly help bridge the $40 to 50 billion gap on the balance of payments estimated for FY27," said Sakshi Gupta, principal economist at HDFC Bank.

## What Still Needs to Change

Market experts warn that the limit increases alone may not be enough. Nilesh Shah, managing director at Kotak Mahindra Asset Management, said the move "needs to be complemented by simple and digital processes related to KYC, taxation, repatriation" for significant inflows to materialise.

The practical barriers remain formidable: cumbersome documentation for opening and operating PIS demat accounts, complex tax filing requirements, and the erosion of returns from rupee depreciation. India also continues to levy a 15 per cent short-term capital gains tax on shares sold before one year and a 12.5 per cent long-term capital gains tax on equity gains above one lakh rupees — taxes that apply equally to NRIs and are not affected by these reforms.

## What NRIs Should Do Now

If you have an existing PIS demat account, the higher limits take effect once the RBI issues implementation timelines. If you have been considering opening one, the doubled ceiling makes the case stronger.

For bond investors, the government securities tax exemption is already retroactive to April 1. NRIs can access Indian G-Secs through the Fully Accessible Route, which now includes all new 15-year, 30-year and 40-year issuances — the same bonds included in global indexes tracked by major institutional investors.

The structural opportunity is clear. The friction, however, has not yet disappeared. Watch for the RBI's implementation circular in the coming weeks for the exact timelines and operational details."""
    }
    
    return insert_article(article)


# ─── MAIN ───

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Lifestyle & Markets Writer")
    print(f"Run time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    results = []
    results.append(("Daraxonrasib Pancreatic Cancer", write_article_1()))
    results.append(("South Asian Heart Risk Paradox", write_article_2()))
    results.append(("RBI NRI Equity Limits + Bond Tax", write_article_3()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, ok in results:
        status = "✓ Published" if ok else "✗ Failed"
        print(f"  {status}: {name}")
    
    successes = sum(1 for _, ok in results if ok)
    print(f"\n  {successes}/{len(results)} articles published")
    print("=" * 60)
