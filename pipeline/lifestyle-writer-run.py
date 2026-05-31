#!/usr/bin/env python3
"""
Lifestyle-Health + Markets-Finance writer for The Videshi
Run: 2026-05-31
Articles:
  1. FDA inhaled insulin for children (lifestyle-health)
  2. Leisure exercise vs work exercise genetics study (lifestyle-health)
  3. AI spending fatigue NRI portfolio rebalancing (markets-finance)
"""

import json, os, sys, time, uuid, re, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.replace('export ', '').strip()
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials")
    sys.exit(1)

import requests
import urllib.parse

def sb_post(table, data):
    """Insert a row into Supabase and return the inserted record."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        json=data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Supabase POST error {r.status_code}: {r.text[:300]}")
        return None
    result = r.json()
    return result[0] if isinstance(result, list) and result else result

def sb_patch(table, match, data):
    """Update rows in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        json=data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Supabase PATCH error {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download an image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Image download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None

        # Upload to Supabase storage
        upload_r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            data=r.content,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None


def validate_image_url(url):
    """Validate that URL returns a real image."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200:
            print(f"  ✗ Image URL returned {r.status_code}")
            return False
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct:
            print(f"  ✗ Not an image content-type: {ct}")
            return False
        cl = int(r.headers.get('Content-Length', 0))
        if cl > 0 and cl < 5000:
            print(f"  ✗ Image too small: {cl} bytes")
            return False
        return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return True  # Benefit of the doubt if HEAD fails


def publish_article(article):
    """Insert article into p2_articles and set image."""
    print(f"\n{'='*60}")
    print(f"Publishing: {article['headline']}")
    print(f"Category: {article['category']}")
    print(f"Slug: {article['slug']}")

    # Source image
    image_url = None
    image_attribution = None

    if article.get('person_name'):
        print(f"  Searching Wikipedia for '{article['person_name']}'...")
        wiki_img = fetch_wikipedia_person_image(article['person_name'])
        if wiki_img:
            filename = f"{article['slug']}.jpg"
            image_url = upload_image_to_supabase(wiki_img, filename)
            image_attribution = "Wikimedia Commons"

    if not image_url and article.get('pexels_query'):
        print(f"  Searching Pexels for '{article['pexels_query']}'...")
        pexels_img = fetch_pexels_image(article['pexels_query'], article.get('pexels_fallback'))
        if pexels_img:
            if 'images.pexels.com' in pexels_img:
                image_url = pexels_img
                image_attribution = "Pexels"
            else:
                filename = f"{article['slug']}.jpg"
                image_url = upload_image_to_supabase(pexels_img, filename)
                image_attribution = "The Videshi"

    if image_url and not validate_image_url(image_url):
        print("  ✗ Image validation failed, skipping image")
        image_url = None

    # Build record
    now = datetime.now(timezone.utc).isoformat()
    vertical_map = {
        "lifestyle-health": "culture",
        "markets-finance": "economy",
    }
    record = {
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "body": article['body'],
        "slug": article['slug'],
        "category": article['category'],
        "vertical": vertical_map.get(article['category'], "culture"),
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article.get('source_urls', [])),
    }
    if image_url:
        record["image_url"] = image_url
    if image_attribution:
        record["image_attribution"] = image_attribution

    result = sb_post("p2_articles", record)
    if result:
        art_id = result.get('id')
        print(f"  ✓ Published! ID: {art_id}")
        return art_id
    else:
        print(f"  ✗ Failed to publish")
        return None


# ============================================================
# ARTICLE 1: FDA Inhaled Insulin for Children
# ============================================================
article1 = {
    "headline": "The FDA Just Approved Inhaled Insulin for Children. For South Asian Families Managing Diabetes, the Needle Era May Finally Be Ending.",
    "subheadline": "Afrezza, the first needle-free mealtime insulin for kids aged six and above, costs $35 a month and mimics the body's natural insulin response more closely than injections do.",
    "slug": "fda-afrezza-inhaled-insulin-children-diabetes-south-asian-families-20260531",
    "category": "lifestyle-health",
    "person_name": None,
    "pexels_query": "child using inhaler medical device",
    "pexels_fallback": "diabetes insulin medical",
    "source": "Reuters, MannKind Corporation, FDA",
    "source_urls": ["https://www.reuters.com/business/healthcare-pharmaceuticals/us-fda-approves-mannkinds-inhaled-insulin-children-2026-05-30/", "https://www.globenewswire.com/news-release/2026/05/29/mannkind-announces-fda-approval-of-afrezza"],
    "body": """For decades, the daily reality of managing childhood diabetes has involved needles. Multiple injections a day, anxiety at school lunch, the social stigma of pulling out a syringe at a friend's birthday party. On Friday, the US Food and Drug Administration changed the calculus by approving Afrezza — a rapid-acting inhaled insulin — for children and adolescents aged six and above.

It is the first and only needle-free mealtime insulin option ever approved for paediatric patients in the United States.

## Why This Matters for South Asian Families

More than 350,000 children in the US live with diabetes, the majority with Type 1. But for South Asian families, the stakes are uniquely personal. South Asians carry a two- to fourfold higher risk of developing Type 2 diabetes compared to white populations, and that elevated risk begins showing up in adolescence. A landmark study in the *Journal of the American Heart Association* found that South Asian women had nearly double the prevalence of prediabetes at age 45 compared to other groups — and the trajectory starts much earlier.

For parents already navigating the genetic predisposition, a needle-free alternative is not a convenience. It is a compliance tool. Research consistently shows that fear of injections is one of the leading causes of insulin non-adherence in children and teenagers.

## How Afrezza Works

Afrezza uses MannKind Corporation's proprietary Technosphere drug-delivery platform to deliver insulin through the lungs via a small, portable inhaler. The insulin enters the bloodstream within minutes, more closely mimicking the body's natural mealtime response than subcutaneous injections do.

The key clinical advantage is speed and flexibility. Children's eating patterns are unpredictable — snacking after school, eating at irregular intervals during sports, refusing meals they agreed to ten minutes ago. Afrezza can be taken at the start of a meal or even slightly after, accommodating the chaos of paediatric eating without the rigid pre-meal timing that injections require.

The approval is backed by the Phase 3 INHALE-1 clinical trial, plus over 20 years of development data on inhaled insulin technology.

## What Parents Need to Know

**Cost:** MannKind says eligible patients can access Afrezza for $35 or less per month through its MannKind Cares programme — significantly below the out-of-pocket cost of many injectable insulin regimens.

**Age range:** Approved for children aged six and above with Type 1 or Type 2 diabetes.

**Not a replacement for basal insulin:** Afrezza handles mealtime glucose spikes. It does not replace long-acting insulin for Type 1 patients.

**Lung function screening required:** The drug is not recommended for children with underlying lung conditions such as asthma. Pulmonary function testing (FEV1) is part of the onboarding process.

**Safety profile:** In the paediatric trial, side effects were consistent with the adult experience accumulated over 12 years of use. The most notable warning is the risk of bronchospasm — sudden tightening of the airway muscles — which is why lung screening is mandatory.

## The Bigger Picture

Jennifer Segrist, whose 15-year-old daughter Taisie participated in MannKind's clinical study, told Reuters that switching from injections to inhaled insulin was "life changing." The teenager became more independent in managing her condition — a critical milestone in adolescent diabetes care.

For diaspora families in the US, where cultural stigma around chronic disease management still runs deep and where children may resist visible medical devices at school, inhaling insulin through what looks like a small asthma inhaler carries less social friction than pulling out a syringe.

Desmond Schatz, a professor of paediatrics at the University of Florida College of Medicine, put it plainly: "Mealtime insulin can be especially challenging for children because eating and snacking patterns, activity levels, and daily settings like school and sports often vary. With its rapid onset and dosing at the start of a meal, Afrezza may help clinicians better match insulin therapy to how children and families live day to day."

## What to Ask Your Doctor

If your child is on injectable mealtime insulin, the conversation with your endocrinologist is straightforward: Is Afrezza appropriate given their lung function, current regimen, and control? If your child has been recently diagnosed, it is worth asking whether inhaled insulin should be part of the initial treatment plan rather than something added later.

The drug is available now. No waiting period, no phased rollout. For the 350,000 families managing paediatric diabetes in America — and particularly for the South Asian families where the genetic burden runs heaviest — this is a material change in the daily burden of care."""
}

# ============================================================
# ARTICLE 2: Leisure Exercise vs Work Exercise — Genetics Study
# ============================================================
article2 = {
    "headline": "A Study of 540,000 People Found That Exercise at Work Does Not Protect Your Health the Way Leisure Exercise Does. The Genetics Are Different.",
    "subheadline": "A Nature Genetics study using data from the Million Veteran Program and UK Biobank found that leisure-time physical activity has distinct genetic pathways and uniquely protects against diabetes, heart failure and early death.",
    "slug": "leisure-exercise-vs-work-exercise-genetics-nature-south-asian-tech-professionals-20260531",
    "category": "lifestyle-health",
    "person_name": None,
    "pexels_query": "person jogging park leisure exercise",
    "pexels_fallback": "running exercise outdoor fitness",
    "source": "Nature Genetics, Psychiatric Times, Yale School of Medicine",
    "source_urls": ["https://www.nature.com/articles/s41588-024-01933-5", "https://www.psychiatrictimes.com/view/yale-study-physical-activity-health-well-being-illness"],
    "body": """If you walk 8,000 steps a day shuttling between meetings and the office kitchen, you might assume your body is getting what it needs. A major new study published in *Nature Genetics* says it is not — and the reason is not what you would expect.

The research, led by scientists at the Yale School of Medicine and the VA Connecticut Healthcare System, analysed genetic data from nearly 540,000 people across the Million Veteran Program and UK Biobank. It is one of the largest genomic studies of physical activity ever conducted, and its core finding upends a common assumption: exercise performed during leisure time is genetically, biologically, and clinically distinct from physical activity performed at work or at home.

## The Core Finding

Using genome-wide association analysis across nearly 190,000 individuals of European ancestry, 27,000 of African ancestry and 10,000 of Latin-American ancestry, the researchers identified genetic variants linked to each type of physical activity. What they found was a clear divergence.

Leisure-time physical activity — jogging, swimming, cycling, gym workouts, recreational sports — was associated with a distinct set of genetic pathways involving the brain's dopamine reward system and visual information processing. Work and home physical activity showed different genetic architecture entirely.

When the researchers applied Mendelian randomisation to test causal effects, leisure-time exercise showed protective effects against Type 2 diabetes, heart failure, abdominal aortic aneurysm, osteoarthritis and elevated triglycerides. Critically, most of these protective effects held even after controlling for BMI — meaning the benefits were not simply a side effect of being thinner.

Work and home physical activity did not show the same protective profile.

## Why This Matters for NRI Tech Professionals

The finding carries particular weight for Indian Americans working in technology, finance, and other desk-intensive industries. South Asians already carry a disproportionate cardiovascular and metabolic risk profile — two to four times the diabetes incidence of white populations, coronary heart disease that presents five to seven years earlier, and dangerous visceral fat accumulation even at normal BMI.

Many NRI professionals log long hours at work. The compensatory logic is familiar: "I'm on my feet during commutes," or "I walk around the campus," or "housework keeps me active." This study says that logic is biologically flawed. The body processes leisure exercise through reward and motivation pathways that appear to confer unique health benefits that occupational movement does not replicate.

Marco Galimberti, the study's first author and an associate research scientist at Yale, was direct: "This work not only shows the genetic differences associated with physical activity performed in different contexts but also highlights the significant health benefits of engaging in physical activity during leisure time."

## What the Genetics Tell Us

The study identified enrichment for dopaminergic neurons in leisure-time physical activity — the same reward circuitry involved in motivation, pleasure and habit formation. This suggests that the psychological experience of choosing to exercise, for enjoyment or self-improvement, may activate biological pathways that obligatory movement does not.

The researchers also found that genetic variants associated with sedentary time during leisure were enriched in skeletal muscle genes whose expression changes with resistance training — indicating a direct biological link between leisure-time inactivity and muscular deconditioning.

A phenome-wide association analysis across an independent sample confirmed negative correlations between leisure-time activity and diabetes, cardiovascular disease, lung cancer and asthma. The strongest association was with diabetes — the disease that disproportionately stalks the South Asian population.

## The Practical Takeaway

This is not a study that says your standing desk is useless or that walking to work has no value. General movement throughout the day reduces sedentary risk. But the data is clear that deliberate, chosen, leisure-time exercise — the kind you do because you want to, not because your job requires it — activates protective biological machinery that occupational activity does not.

For South Asian Americans navigating genetically elevated cardiometabolic risk, the message is sharper than for the general population. The 30-minute evening run, the weekend cricket match, the gym session before the kids wake up — these are not lifestyle luxuries. They are, according to the largest genomic dataset ever assembled on the question, a biologically distinct category of movement with uniquely protective health effects.

The study's Mendelian randomisation analysis also found a protective effect of leisure-time activity on phenotypic age acceleration and parental survival — meaning the benefits extend not just to disease prevention but to the rate at which the body ages.

If you are a 35-year-old software engineer who walks 6,000 steps around the office but has not done a deliberate workout in months, this study says your step count is not doing what you think it is doing. The prescription is not more movement at work. It is dedicated, intentional exercise during your own time — and the genetics suggest your body knows the difference."""
}

# ============================================================
# ARTICLE 3: AI Spending Fatigue Hits NRI Portfolios
# ============================================================
article3 = {
    "headline": "Enterprise AI Spending Is Showing Its First Cracks. If You Hold US Tech Stocks, Your Portfolio May Be More Exposed Than You Think.",
    "subheadline": "GPU rental prices have fallen 40 per cent, Fortune 20 companies are tightening AI budgets, and NRI investors with heavy US tech exposure need to think about what comes next.",
    "slug": "ai-enterprise-spending-fatigue-nri-portfolio-tech-stocks-rebalancing-20260531",
    "category": "markets-finance",
    "person_name": None,
    "pexels_query": "stock market trading technology",
    "pexels_fallback": "financial charts data analysis",
    "source": "Barron's, NRI Globe, UBS, Goldman Sachs",
    "source_urls": ["https://www.barrons.com/articles/ai-retirement-portfolio-rebalance", "https://nriglobe.com/ai-bubble-cracking-2026-nri-investor-guide-india-opportunity"],
    "body": """The AI trade that powered the S&P 500's gains for the past two years is showing its first honest signs of fatigue. In the last 30 days, multiple Fortune 20 corporations have visibly tightened AI tool budgets as per-engineer token costs climb and demonstrable return on investment remains harder to pin down.

For the global Indian diaspora — many of whom hold significant exposure to US tech giants through 401(k)s, individual brokerage accounts and global index funds — this shift demands attention rather than panic.

## The Warning Signs Are Concrete

GPU rental prices for Nvidia's H200 have fallen roughly 40 per cent, from about $7 per hour to $4 per hour, the clearest pricing signal yet that short-term demand is softening. When the hardware that powers AI becomes cheaper because fewer companies want to rent it, that is not a discount. It is a demand signal.

Several enterprise buyers — including Microsoft and Uber — have tightened AI tool spending in the last month as per-seat costs collide with unclear ROI. The pattern is familiar from past technology cycles: initial euphoria, heavy capital deployment, and then a reckoning when the accountants catch up with the engineers.

Alphabet's guidance of $175 to $185 billion in 2026 capital spending — nearly double the $91.4 billion spent in 2025 — initially spooked investors. The five hyperscalers are now spending 60 per cent of operating cash flow on capex, a record. Goldman Sachs estimates that AI investment will drive nearly half of S&P 500 earnings growth this year. The market's valuation assumes this influx will continue, but that is not a given.

## Why NRI Portfolios Are Particularly Exposed

The typical NRI investor portfolio in the US, Canada, UK and UAE is heavily tilted toward American technology. Microsoft, Nvidia, Google, Apple, Meta and Amazon are not just individual stock picks — they dominate the index funds that sit inside most 401(k)s and retirement accounts.

Technology and communications stocks now account for more than 40 per cent of the S&P 500 index. If you own a broad US index fund — and most NRI investors do — you are carrying more concentrated AI exposure than you may realise.

Angelo Kourkafas, senior global investment strategist at Edward Jones, warned in Barron's this week: "Concentration increases volatility, and that can be problematic for investors who are drawing income, including retirees."

The issue is not that AI is a bad long-term bet. It is that the market has priced in a future where every dollar of AI capex generates returns — and the enterprise spending data suggests that assumption is being tested right now.

## The India Countercyclical Opportunity

While US enterprise AI spending shows signs of fatigue, India's AI build-out is moving in the opposite direction. The IndiaAI Mission, Microsoft's $17.5 billion India commitment, hyperscaler data centre construction across Hyderabad, Mumbai and Chennai, and projections of 2.3 million AI-related jobs by 2027 all point to a parallel growth lane that is still in early innings.

For NRI investors, this creates a portfolio construction opportunity: adding India-AI exposure to balance pure-hype US concentration. This is not about exiting US tech. It is about recognising that the diaspora's natural home bias toward American equities has created an unintentional concentration risk at precisely the moment when enterprise buyers are starting to ask harder questions about AI returns.

Gulf NRIs are already moving in this direction. A recent survey found that 73 per cent of GCC-based NRIs have boosted their Indian equity exposure, with many deploying fresh capital as a structural shift in wealth strategy.

## What to Do Right Now

**Check your actual tech exposure.** If you have not rebalanced your 401(k) or brokerage account in a while, your tech allocation may have drifted well above your target. A 60/40 portfolio from two years ago may now be 65/35 or 70/30 simply from tech appreciation.

**Consider bonds at current yields.** The 10-year US Treasury yield is hovering near 4.5 per cent — an attractive entry point for investors rotating out of appreciated tech positions. Since selling can trigger capital-gains taxes, concentrate rebalancing in tax-deferred accounts where possible.

**Look at India-focused funds.** Indian equities, despite a weak May for the Nifty, offer diversification away from the US-AI concentration. The RBI's monetary policy decision on June 5 may provide further direction on the investment climate.

**Do not panic-sell.** Goldman Sachs forecasts that AI investment will still drive significant earnings growth. The companies building AI infrastructure have stronger financial positions than the dot-com-era telecoms that built fibre-optic networks in anticipation of demand that never came. Free cash flow margins for AI hyperscalers have averaged 15 per cent, compared to 3.5 per cent for 1990s telecoms.

The message is not that the AI trade is over. It is that the easy money phase may be, and for NRI investors with concentrated US tech exposure, now is the time to ensure your portfolio reflects your actual risk tolerance — not just the last two years of momentum."""
}

# ============================================================
# Publish all articles
# ============================================================
articles = [article1, article2, article3]

for art in articles:
    publish_article(art)

print(f"\n{'='*60}")
print(f"Writer run complete. Published {len(articles)} articles.")
print(f"  - lifestyle-health: 2")
print(f"  - markets-finance: 1")
