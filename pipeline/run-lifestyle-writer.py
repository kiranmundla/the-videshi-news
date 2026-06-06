#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer
Generates 2 lifestyle-health + 1 markets-finance articles.
"""

import requests
import json
import os
import subprocess
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(filepath):
    try:
        with open(os.path.expanduser(filepath)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val
    except FileNotFoundError:
        pass

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

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
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image using curl (Python urllib gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                src = p.get("src", {})
                url = src.get("large2x") or src.get("large") or src.get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate an image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:60]}... ({cl} bytes)")
            return True
        # Try GET as fallback (some servers don't support HEAD properly)
        r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct2:
            # Read enough to check size
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                print(f"  ✓ Image validated via GET: {url[:60]}...")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def find_best_image(person_name=None, commons_queries=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    # Try Wikipedia person image first
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, "Wikimedia Commons"

    # Try Wikimedia Commons
    if commons_queries:
        for q in commons_queries:
            results = fetch_wikimedia_commons_images(q, limit=5)
            for r in results:
                url = r.get("url") or r.get("original_url")
                if url and validate_image(url):
                    return url, "Wikimedia Commons"

    # Try Pexels
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            return url, "Pexels"

    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}...")
            return True
        print(f"  ✓ Published (no return data)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False

# ============================================================
# ARTICLE 1: Lifestyle-Health — Obesity Drug Race at ADA 2026
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Obesity Drug Race at ADA 2026")
print("="*60)

img1_url, img1_attr = find_best_image(
    commons_queries=["obesity drug GLP-1", "Roche pharmaceuticals", "American Diabetes Association meeting"],
    pexels_query="medical research laboratory pharmaceutical"
)

article1_body = """The American Diabetes Association's annual meeting in New Orleans this week has turned into a battleground for the next generation of obesity drugs. Three companies presented data that could reshape how South Asians — who develop type 2 diabetes at lower body weights and younger ages than any other ethnic group — manage weight and metabolic risk.

## Roche's Injection Hits 22.7 Per Cent Weight Loss in Under a Year

The biggest headline came from Roche. Its experimental drug enicepatide, a once-weekly injection that mimics both GLP-1 and GIP hormones, helped patients lose 22.7 per cent of their body weight in just 48 weeks. Among those on the highest dose, more than a quarter lost at least 30 per cent. Critically, the weight-loss trajectory showed no sign of a plateau, meaning patients could lose even more with longer treatment.

For context, Novo Nordisk's blockbuster Wegovy produces about 15 per cent weight loss over 68 weeks. Eli Lilly's Zepbound, currently the market leader for efficacy, delivered 25.5 per cent over 84 weeks. Roche achieved comparable results in roughly half the time.

Manu Chakravarthy, Roche's head of cardiovascular and metabolism development, said the data supports moving to late-stage trials. "There was no hint of any plateau at week 48," he said.

## An Obesity Pill That Does Not Damage the Liver

Structure Therapeutics presented equally significant news from a different angle: its oral obesity drug aleniglipron showed no signs of liver injury, the safety concern that has haunted every company trying to make a GLP-1 pill. Patients on the once-daily tablet lost up to 39 pounds over 44 weeks, with only 10.4 per cent discontinuing treatment.

The appeal of a pill over a weekly injection is obvious. For the millions of South Asians in the diaspora managing prediabetes or metabolic syndrome, swallowing a tablet is a lower barrier than injecting at home. Structure plans to begin its late-stage programme in the third quarter of 2026.

## Zealand and Roche Bet on Gentler Side Effects

Denmark's Zealand Pharma, working with Roche, presented tolerability data for petrelintide, an amylin-based drug that works differently from GLP-1 agents. Only 1.5 per cent of patients dropped out due to gastrointestinal side effects — the nausea and vomiting that plague existing treatments. While petrelintide's weight loss is more modest at 10.7 per cent over 42 weeks, its tolerability profile could make it a strong combination partner with other drugs.

## Why This Matters for South Asians

The urgency is not academic. A landmark study published this year in the Journal of the American Heart Association found that South Asian men had a 30.7 per cent prevalence of prediabetes at age 45, compared with 3.9 per cent among white men. By age 55, South Asian men and women were at least twice as likely to develop type 2 diabetes as their white counterparts — despite reporting healthier diets, lower alcohol use, and comparable exercise habits.

The MASALA study at Northwestern University called this mismatch between healthy behaviour and clinical risk "surprising" and identified the 40s as "a critical window when risk is already high, but disease is still preventable."

Current obesity drugs cost between $1,000 and $1,500 per month without insurance in the United States, putting them out of reach for many. If the new entrants reach market — and analysts expect the obesity drug market to exceed $100 billion annually within a decade — competition should drive prices down and expand access.

## What Comes Next

Roche plans to move enicepatide into Phase 3 trials. Structure will launch its late-stage programme for aleniglipron this quarter. Zealand and Roche are designing a Phase 3 strategy for petrelintide as both a standalone and combination therapy. The FDA is expected to review Eli Lilly's oral GLP-1, orforglipron, for approval in the coming weeks, which would be the first oral GLP-1 on the US market.

For diaspora families with a history of diabetes, these developments are worth watching closely. The drugs are not yet available, but the science is moving faster than at any point in the last two decades."""

article1 = {
    "headline": "Three Obesity Drugs Just Stole the Show at ADA 2026. South Asians Should Pay Close Attention.",
    "subheadline": "Roche's injection hit 22.7 per cent weight loss in 48 weeks. An oral pill showed no liver damage. A third drug barely caused nausea. The obesity treatment landscape is about to change.",
    "body": article1_body,
    "slug": "obesity-drugs-ada-2026-roche-enicepatide-structure-aleniglipron-south-asian-diabetes-20260606",
    "category": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_url,
    "image_caption": "Researchers present new obesity drug data at the American Diabetes Association annual meeting",
    "image_attribution": img1_attr or "Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/structures-experimental-obesity-pill-shows-no-signs-liver-injury-2026-06-05/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/roche-obesity-drug-helps-patients-shed-227-weight-mid-stage-trial-2026-06-05/"},
        {"name": "Journal of the American Heart Association (MASALA Study)", "url": "https://www.ahajournals.org/doi/10.1161/JAHA.124.038500"},
        {"name": "Reuters — Zealand petrelintide tolerability", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/zealand-touts-promising-tolerability-data-obesity-drug-mid-stage-study-2026-06-05/"}
    ])
}

insert_article(article1)


# ============================================================
# ARTICLE 2: Lifestyle-Health — Gut Microbiome and Cancer
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: Gut Microbiome and Cancer Immunotherapy")
print("="*60)

img2_url, img2_attr = find_best_image(
    commons_queries=["gut microbiome bacteria", "intestinal bacteria microscopy", "probiotics bacteria culture"],
    pexels_query="gut bacteria microbiome health"
)

article2_body = """A kidney cancer patient at University Hospitals Seidman Cancer Center in Cleveland will soon swallow a capsule of bacteria alongside their regular immunotherapy drugs. They will be the first participant in the first late-phase clinical trial testing whether a common probiotic can amplify cancer treatment.

The trial, funded by the National Cancer Institute, will enrol nearly 700 people with advanced renal cell carcinoma across multiple hospitals. They will take CBM588, a strain of Clostridium butyricum that is already sold over the counter in Japan for gastrointestinal complaints, while receiving standard immunotherapy.

"We're hoping to change the standard of care," said Dr Pedro Barata, one of three principal investigators on the study.

## How Gut Bacteria Shape Cancer Treatment

The science linking gut bacteria to cancer outcomes has advanced rapidly. The American Society of Clinical Oncology now lists nearly 100 ongoing studies testing ways to manipulate the gut microbiome to help treat cancer. A meta-analysis published in BMC Cancer, covering 22 studies and 3,274 patients, found that probiotic supplementation alongside immune checkpoint inhibitors improved progression-free survival by 37 per cent and overall survival by 47 per cent.

The mechanism centres on a simple anatomical fact: the surface area of the human intestine is about 20 times larger than the area covered by skin, and it holds roughly a third of all the body's T-cells and B-cells. These immune cells are immersed in bacteria, and the gut serves as a proving ground where the immune system learns to distinguish invaders from healthy tissue.

"You go from having an Amazon rainforest, with 300 or 400 different bacteria living in a finely developed ecosystem, and you go to having a single bug," said Dr Marcel van den Brink, president of City of Hope Cancer Center, describing what happens when aggressive antibiotics wipe out beneficial bacteria. "I mean, my God!"

## The Fibre Connection

A seminal 2021 study at MD Anderson Cancer Center found that patients eating a high-fibre diet responded better to melanoma immunotherapy: for every 5-gram increase in daily fibre intake, the risk of cancer progression or death fell 30 per cent. Certain gut bacteria metabolise fibre into short-chain fatty acids that improve T-cell survival, prevent harmful bacteria from proliferating, and suppress inflammation.

Dr Robert Jenq, director of the Microbiome Programme at City of Hope, said these fatty acids "also prevent harmful bacteria, function as nutrition for the lining of the colon and seem to suppress inflammation."

At the CHUM Microbiome Centre in Montreal, an intensive educational campaign reduced the proportion of lung cancer patients receiving antibiotics before immunotherapy from 20 per cent to 5 per cent, after research showed that heavy antibiotic use was independently associated with poor cancer outcomes.

## What This Means for the Diaspora

South Asians have one of the highest age-adjusted cancer mortality rates globally, and cancer incidence among the diaspora is rising as diets shift toward processed Western foods. But traditional Indian cuisine — dahi, idli, dosa, fermented pickles, kanji — is rich in naturally occurring probiotics and fermented foods that support microbial diversity.

This does not mean eating curd will cure cancer. But the research suggests that maintaining a diverse, fibre-rich diet and avoiding unnecessary antibiotics may give the immune system a better foundation to fight disease, whether or not cancer treatment is involved.

Dr Jenny Paredes at City of Hope is launching a trial that will track every bite that bone marrow transplant recipients eat during 40 days in hospital and 60 days at home, aiming to understand exactly how diet shapes the microbiome during treatment.

## The Complexity Ahead

The field faces enormous challenges. Even understanding how two bacterial strains interact does not predict what happens when a million coexist. Bacteria behave differently depending on which other bacteria are present, the condition of the gut, and even the time of day.

"The complexity problem is humbling," said Dr Paul Frankel, a biostatistician at City of Hope. "The comforting thing is that we've been remarkably good at making progress without complete knowledge."

For now, the practical advice from leading oncologists is straightforward: eat real food, prioritise fibre, avoid antibiotics unless they are clearly needed, and do not assume that over-the-counter probiotic supplements are a substitute for a healthy diet. The science is moving fast, but the ancient wisdom of feeding your gut well has never been more relevant."""

article2 = {
    "headline": "The First Major Trial of Probiotics for Cancer Treatment Just Began. The Science Behind It Is Rooted in Your Gut.",
    "subheadline": "Nearly 700 patients will test whether a common Japanese probiotic can boost immunotherapy. South Asians, whose traditional diets are rich in fermented foods, have reason to watch closely.",
    "body": article2_body,
    "slug": "probiotics-cancer-immunotherapy-gut-microbiome-trial-cbm588-south-asian-diet-20260606",
    "category": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_url,
    "image_caption": "Illustration of gut bacteria and the human intestinal microbiome",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/05/health/gut-microbiome-immunity-cancer-ghrc"},
        {"name": "BMC Cancer (Meta-analysis)", "url": "https://link.springer.com/article/10.1186/s12885-025-13571-3"},
        {"name": "Nature Medicine — CBM588 kidney cancer trial", "url": "https://www.nature.com/articles/s41591-022-01694-6"},
        {"name": "MD Anderson Cancer Center — fiber and melanoma", "url": "https://www.science.org/doi/10.1126/science.aaz7015"}
    ])
}

insert_article(article2)


# ============================================================
# ARTICLE 3: Markets-Finance — US Jobs Report
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: US Jobs Report May 2026")
print("="*60)

img3_url, img3_attr = find_best_image(
    commons_queries=["US Bureau of Labor Statistics", "Wall Street New York Stock Exchange", "Federal Reserve building"],
    pexels_query="stock market trading wall street"
)

article3_body = """The American economy added 172,000 jobs in May, more than double the 85,000 economists expected and the third consecutive month of strong employment growth. The unemployment rate held steady at 4.3 per cent. For NRI investors, H-1B workers, and anyone sending money home, this single data release reshapes the financial landscape for the rest of 2026.

## The Numbers That Changed Everything

May's payroll gain was not a fluke. The Bureau of Labor Statistics revised March upward to 214,000 (from 178,000) and April to 179,000 (from 115,000). Over the past three months, the economy has averaged 188,000 new jobs per month — nearly triple the pace of the same period in 2025, when average monthly gains were just 10,000.

The hiring was broad-based. Leisure and hospitality led with 70,000 new positions, likely driven by preparations for the FIFA World Cup. Local government added 55,000. Healthcare contributed another 35,000. Construction rose by 17,000.

The weak spots were concentrated in finance, which lost 22,000 jobs and is down 107,000 since May 2025, and air transportation, which shed 8,700 positions following the collapse of Spirit Airlines.

Annual wage growth slowed to 3.4 per cent from 3.6 per cent in April. That sounds like good news for inflation, but household disposable income after inflation has now fallen for three straight months, and the personal saving rate is at a four-year low.

## The Fed Is Now More Likely to Raise Rates Than Cut Them

This is the headline that matters most for anyone with money in US markets. Before the jobs report, traders placed roughly 50 per cent odds on a rate hike by December. After the report, those odds jumped to about 70 per cent. The probability of any rate cut this year is now negligible.

The Federal Reserve's benchmark rate sits at 3.50 to 3.75 per cent. Kansas City Fed President Jeff Schmid said the central bank faces a choice between patience and raising rates to bring down inflation. San Francisco Fed President Mary Daly said policy is in a good place but the economy is too uncertain for forward guidance. The next FOMC statement comes on June 17.

For NRI investors in US equities, this is a headwind. Higher rates compress stock valuations, particularly in the technology sector. The Nasdaq fell 2.1 per cent on Friday, the S&P 500 dropped 1.1 per cent, and the Dow declined 0.3 per cent. Broadcom, already reeling from post-earnings selling, fell further alongside the broader chip sector.

## What This Means for H-1B Workers

The strong jobs data is a double-edged sword for Indian professionals on work visas. On one hand, broad-based hiring in healthcare, hospitality, and construction does not directly benefit the technology sector, where many H-1B holders work. Tech and finance, the two industries that employ the most Indian diaspora professionals, were the weakest performers in May.

On the other hand, a resilient overall economy reduces the risk of a recession-driven spike in layoffs. The labour force participation rate, at 61.8 per cent, has not recovered, partly because immigration enforcement has shrunk the available workforce. Economists estimate the economy now needs only zero to 50,000 jobs per month to keep up with working-age population growth — well below the current pace.

The median duration of unemployment rose to 11.6 weeks, the highest since November 2021. Younger, more educated workers are the ones struggling most to find new positions, according to Vanguard senior economist Adam Schickling.

## Remittances and the Rupee

A rising-rate environment in the US typically strengthens the dollar, which puts downward pressure on the rupee. The Reserve Bank of India held its repo rate at 5.25 per cent this week, and the rupee has been trading near historic lows around 96 to the dollar.

For NRIs sending money home, a stronger dollar means more rupees per remittance. But for those with NRE or NRO deposits in India, the gap between US and Indian rates narrows the relative attractiveness of parking money in Indian fixed deposits. With US Treasury yields rising and the two-year note hitting its highest level since February 2025, dollar-denominated savings and bonds are competing aggressively with rupee deposits.

## The Bottom Line

The US labour market is stronger than anyone expected three months ago. That is good for economic stability but bad for anyone hoping for rate cuts. If you hold US equities — particularly tech stocks — brace for continued volatility. If you are sending money home, the exchange rate is working in your favour. And if you are on an H-1B and worried about layoffs, the macro picture is your friend even if your specific sector is not hiring aggressively.

The next critical data point is the June CPI report, due in mid-July. If inflation stays elevated alongside strong employment, a December rate hike becomes the base case rather than a tail risk."""

article3 = {
    "headline": "The US Just Added 172,000 Jobs. Rate Hike Odds Hit 70 Per Cent. Here Is What Every NRI Needs to Know.",
    "subheadline": "May's payroll blowout was the third in a row. The Nasdaq fell 2.1 per cent. The dollar is strengthening. For H-1B workers, investors, and anyone sending money home, the calculus just shifted.",
    "body": article3_body,
    "slug": "us-jobs-report-may-2026-172000-rate-hike-70-percent-nri-h1b-remittances-20260606",
    "category": "markets-finance",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3_url,
    "image_caption": "The New York Stock Exchange on Wall Street reacted to strong US employment data",
    "image_attribution": img3_attr or "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/world-at-work/us-posts-another-month-strong-job-gains-may-unemployment-rate-steady-43-2026-06-05/"},
        {"name": "Bureau of Labor Statistics", "url": "https://www.bls.gov/news.release/empsit.nr0.htm"},
        {"name": "Barron's", "url": "https://www.barrons.com/livecoverage/stock-market-today-060626"},
        {"name": "CME FedWatch Tool", "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"}
    ])
}

insert_article(article3)

print("\n" + "="*60)
print("DONE — All 3 articles processed")
print("="*60)
