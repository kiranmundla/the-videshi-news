#!/usr/bin/env python3
"""
The Videshi — Lifestyle-Health & Markets-Finance Writer
Generates 2 lifestyle-health + 1 markets-finance articles per run.
"""

import json, os, sys, time, uuid, subprocess, re, urllib.parse, requests
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image helpers ──

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
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get('Content-Type', '')
        cl2 = int(r2.headers.get('Content-Length', 0))
        if r2.status_code == 200 and 'image' in ct2:
            if cl2 > 5000:
                return True
            # Read first chunk to check size
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=20,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None

        ct = r.headers.get('Content-Type', 'image/jpeg')
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(upload_url, data=r.content,
                          headers={
                              'apikey': SUPABASE_KEY,
                              'Authorization': f'Bearer {SUPABASE_KEY}',
                              'Content-Type': ct,
                              'x-upsert': 'true'
                          }, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(article_slug, person_name=None, pexels_query=None, pexels_fallback=None):
    """Source image following the hierarchy: Wikipedia → Pexels → None."""
    img_url = None
    attribution = "The Videshi"

    # 1. Try Wikipedia for person articles
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"

    # 2. Fallback to Pexels
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)

    # 3. Validate and upload
    if img_url:
        if validate_image_url(img_url):
            filename = f"{article_slug}.jpg"
            final_url = upload_to_supabase_storage(img_url, filename)
            if final_url:
                return final_url, attribution
        else:
            print(f"  ⚠ Image validation failed for {img_url[:60]}...")

    return None, None


def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'sources': json.dumps(article.get('sources', [])),
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if r.status_code in (200, 201):
        print(f"  ✅ Published: {article['headline'][:60]}... [{article['category']}]")
        return art_id
    else:
        print(f"  ❌ Publish failed: {r.status_code} {r.text[:300]}")
        return None


# ── Article definitions ──

ARTICLES = [
    # ── LIFESTYLE-HEALTH #1 ──
    {
        "headline": "The Eight-Hour Eating Window Millions of Indian Tech Workers Swear By Was Just Linked to a 91 Per Cent Higher Risk of Cardiovascular Death",
        "subheadline": "A study of 20,000 Americans and a 2026 systematic review of real-world eating patterns both point to the same conclusion: aggressive intermittent fasting may be doing more harm than good for the people who need heart protection most.",
        "slug": "eight-hour-eating-window-91-percent-cardiovascular-death-south-asian-intermittent-fasting-20260528",
        "category": "lifestyle-health",
        "person_name": None,
        "pexels_query": "healthy meal time clock eating",
        "pexels_fallback": "intermittent fasting clock food",
        "image_caption": "The timing of meals may matter more than the restriction itself, researchers say.",
        "sources": [
            "American Heart Association Epidemiology and Prevention 2024 — 8-hour TRE and cardiovascular mortality",
            "European Journal of Clinical Nutrition (2026) — systematic review and meta-analysis of TRE observational studies",
            "Cheng et al. (2024) — U-shaped curve: eating windows under 10h and over 14h both raise CVD risk",
            "Reuters (2026) — India's heatwave and health burden context"
        ],
        "body": """The most popular diet in Indian tech culture may be the most dangerous one for Indian hearts.

A landmark analysis of more than 20,000 American adults, presented at the American Heart Association's Epidemiology and Prevention conference, found that people who restricted their eating to an eight-hour window — the textbook 16:8 intermittent fasting protocol — had a 91 per cent higher risk of dying from cardiovascular disease compared to those who ate across 12 to 16 hours. The risk was even higher among people who already had heart disease or cancer.

South Asians already face double the rate of atherosclerotic cardiovascular disease compared to non-Hispanic white Americans, according to a 2024 review in the American Journal of Preventive Cardiology. Layer an aggressive fasting protocol on top of that genetic predisposition, and you are not optimising — you are compounding risk.

## The U-Shaped Curve Your Wellness Influencer Did Not Mention

A 2026 systematic review and meta-analysis published in the European Journal of Clinical Nutrition, covering observational studies of community-dwelling adults across multiple countries, found that the relationship between eating windows and cardiometabolic health is not linear. It is U-shaped.

Cheng et al. (2024) documented the curve explicitly: eating windows shorter than 10 hours and longer than 14 hours were both associated with an increased risk of cardiovascular disease and all-cause mortality. The sweet spot — the range where hypertension, dyslipidemia, and metabolic syndrome risk dropped — sat between 10 and 14 hours.

Currenti et al. (2021) found that eating within a 10-hour window was associated with 76 per cent lower odds of hypertension and 74 per cent lower odds of dyslipidemia. But push that window below eight hours, and the protective effect reverses. Each additional hour of nightly fasting beyond a certain threshold was associated with increased insulin levels, increased C-reactive protein, and decreased HDL cholesterol — the good cholesterol that South Asians are already statistically low on.

## Why This Hits South Asians Harder

The biology is specific. South Asian Americans develop diabetes, prediabetes, and hypertension earlier than any other ethnic group in the United States, according to a multi-ethnic cohort study published in Frontiers in Public Health. The standard BMI threshold for diabetes screening is 25; for South Asians, researchers at Harvard now recommend 20.

Indian vegetarian diets are already lower in protein density than Western diets. Compressing the eating window to eight hours often means skipping breakfast — the meal most Indian families build around dal, roti, and sabzi. That missed meal is not just calories. It is the protein, potassium, and fibre that the American Heart Association's 2026 dietary guidelines now prioritise.

The Indian tech worker pattern is particularly concerning. Late dinners after long shifts. Skipped breakfasts to hit a fasting target. Coffee as a meal replacement until noon. Then a compressed eating frenzy in the afternoon and evening — precisely the pattern the European Journal of Clinical Nutrition review associates with elevated triglycerides and blood pressure.

## What the Evidence Actually Supports

The data does not say fasting is useless. It says the dose matters enormously.

A 2026 review in PubMed found that time-restricted eating with a 10-to-12-hour window can reduce body weight by 3 to 5 per cent, improve glycated haemoglobin by 0.3 to 0.5 percentage points, and reduce total cholesterol by 6 to 7 per cent in healthy populations. Those are meaningful numbers for a South Asian adult managing early metabolic syndrome.

But the same body of evidence shows that pushing below 10 hours produces diminishing returns and increasing harm — especially for people with pre-existing cardiovascular risk, which includes a disproportionate share of the South Asian population.

The clinical recommendation emerging from the 2026 literature is straightforward: eat your first meal within two hours of waking. Eat your last meal at least three hours before sleeping. Keep the window between 10 and 14 hours. Do not skip meals to extend the fast.

## The Conversation Your Family Doctor Is Not Having

South Asians have the lowest rate of anxiety medication use in America, the lowest rate of colon cancer screening, and now, potentially, the highest rate of adopting a fasting protocol that may not suit their cardiovascular profile. The pattern is consistent: a community that self-optimises aggressively but often without the ethnic-specific data to optimise correctly.

If you are an NRI following 16:8 intermittent fasting, the 2026 evidence suggests a simple recalibration. Widen the window. Eat breakfast. Let your mother's three-meals-a-day instinct guide you more than your fitness tracker's fasting countdown.

The traditional Indian eating pattern — early breakfast, full lunch, lighter dinner, no snacking after sunset — lands almost exactly inside the 10-to-14-hour window the data now supports. Your grandmother was not doing intermittent fasting. She was doing something better."""
    },

    # ── LIFESTYLE-HEALTH #2 ──
    {
        "headline": "A Nine-Day Yoga Retreat Changed Participants' Gut Bacteria Faster Than Any Probiotic on the Market. The Science of Why Is Finally Catching Up to the Tradition.",
        "subheadline": "A systematic review of yoga and meditation's effects on the gut microbiome finds that ancient Indian practices reshape the bacteria in your digestive tract — and the mechanism runs through a pathway Western medicine is only beginning to map.",
        "slug": "yoga-meditation-gut-microbiome-systematic-review-ayurveda-science-20260528",
        "category": "lifestyle-health",
        "person_name": None,
        "pexels_query": "yoga meditation peaceful morning",
        "pexels_fallback": "yoga practice sunrise",
        "image_caption": "Yoga and meditation may reshape the gut microbiome through the gut-brain axis, researchers find.",
        "sources": [
            "BMC Complementary Medicine and Therapies — Arhatic Yoga meditation retreat single-arm pilot study",
            "Frontiers in Neuroscience (2026) — Brain-gut-microbiota axis bidirectional review",
            "Ghahari (2026) Experimental Physiology — Psychobiotics and the microbiota-gut-brain axis",
            "Global Wellness Institute (2026) — The Science of Yoga Initiative trends",
            "News-Medical.net — Yoga and meditation show promise for gut health (systematic review)"
        ],
        "body": """The gut-brain axis is the most talked-about frontier in medicine. And the practice that appears to modulate it most rapidly is one that India exported to the world thousands of years ago.

A single-arm pilot study published in BMC Complementary Medicine and Therapies tracked participants through a nine-day Arhatic Yoga meditation retreat that combined breathwork, meditation, and a vegetarian diet. By day three, the oral microbiome had already shifted significantly. By day nine, the gut microbiome had converged toward a profile enriched in beneficial bacteria — improved gut barrier function, enhanced immune modulation, and stronger gut-brain axis signalling.

No commercially available probiotic produces that speed of change. Most clinical trials of probiotic supplements show modest shifts after four to eight weeks. The yoga retreat did it in nine days.

## The Gut-Brain Axis Your Ancestors Understood Intuitively

A 2026 review published in Frontiers in Neuroscience mapped the bidirectional Brain-Gut-Microbiota Axis in unprecedented detail. The gut and brain communicate through the vagus nerve, through immune signalling molecules, and through metabolites produced by gut bacteria. When this axis is disrupted — through stress, poor diet, or sedentary living — the downstream effects include not just digestive problems but anxiety, depression, neuroinflammation, and accelerated cognitive decline.

What the review makes explicit is that stress is the single largest disruptor of the gut-brain axis. Chronic stress alters gut permeability, shifts microbial composition toward inflammatory species, and suppresses the production of short-chain fatty acids that feed the gut lining. Meditation and yoga directly target the stress pathways that drive this cascade.

A companion paper in Experimental Physiology by Ghahari (2026) introduced the concept of psychobiotics — interventions that improve mental health through the gut microbiome. The authors argue that yoga and meditation qualify as psychobiotic interventions, not because they introduce new bacteria, but because they create the physiological conditions — reduced cortisol, improved vagal tone, lower systemic inflammation — in which beneficial bacteria thrive.

## What Yoga Does That a Pill Cannot

The systematic review of yoga and meditation's effects on gut health, summarised in News-Medical.net, identified a consistent pattern across studies: practitioners showed enrichment of beneficial bacterial genera associated with better digestion, stronger immunity, and improved mental wellbeing. The mechanism is not dietary — several studies controlled for diet and still found microbiome shifts attributable to the practice itself.

The key appears to be the vagus nerve. Yoga's deep breathing techniques — pranayama in the Indian tradition — directly stimulate vagal tone. Higher vagal tone is associated with reduced inflammation, improved gut motility, and a microbiome that favours Lactobacillus, Bifidobacterium, and Faecalibacterium — the genera that produce butyrate, the fatty acid that maintains the integrity of the intestinal lining.

This is not a marginal effect. The Arhatic Yoga study showed what the researchers called a "strong selection pressure" on beneficial microbes — the yoga practice was actively reshaping the microbial ecosystem, not merely nudging it.

## Why This Matters for the Diaspora

The Global Wellness Institute's 2026 Science of Yoga Initiative report documents that yoga is evolving from a flexibility practice to a science-based health intervention, with research now linking it to genomic changes, neurowellness markers, and personalised health protocols.

For the Indian diaspora, this creates an ironic situation. The practice that originated in India and that most NRI families grew up around is now being validated by Western institutions — but many second-generation Indian Americans have abandoned it in favour of gym culture, HIIT workouts, and protein shake regimens. The 2024 review in the American Journal of Preventive Cardiology noted that South Asian Americans report less physical activity than other ethnic groups, but the type of activity may matter as much as the quantity.

The evidence suggests that a daily yoga and pranayama practice does something a treadmill cannot: it rewires the gut-brain communication pathway that governs inflammation, immune response, and metabolic health — the exact triad that makes South Asians disproportionately vulnerable to heart disease and diabetes.

## A Practical Framework

The studies converge on a minimum effective dose. Twenty to thirty minutes of yoga that includes pranayama (breathwork), asana (postures), and a brief meditation component appears to produce measurable changes in stress biomarkers within weeks and detectable microbiome shifts within one to two months of consistent practice.

For NRIs managing the particular stress load of immigrant life — career pressure, cultural dislocation, family obligations across time zones — the practice offers a dual benefit. It addresses the gut-brain axis disruption that chronic stress produces. And it reconnects you to a tradition your body may be biologically primed to respond to.

The Ayurvedic texts did not have the vocabulary of the microbiome. But they described a digestive fire — agni — that determined health, mood, and longevity. The science is catching up to the metaphor. The fire, it turns out, is bacterial."""
    },

    # ── MARKETS-FINANCE ──
    {
        "headline": "The RBI Just Ran a $5 Billion Currency Auction. Banks Bid Nearly $10 Billion. India's June Market Will Reward Stock Pickers, Not Index Funds.",
        "subheadline": "Foreign investors have pulled $24 billion from Indian equities this year. The rupee hit 96.96 to the dollar. But the RBI's oversubscribed FX swap, record domestic fund flows, and a shift to sector-specific positioning suggest June belongs to those who choose carefully.",
        "slug": "rbi-5-billion-fx-swap-india-june-stock-pickers-market-nri-strategy-20260528",
        "category": "markets-finance",
        "person_name": None,
        "pexels_query": "Mumbai Bombay stock exchange India finance",
        "pexels_fallback": "Indian currency rupee trading",
        "image_caption": "The RBI's $5 billion FX swap drew nearly $10 billion in bids, signalling strong demand for rupee liquidity.",
        "sources": [
            "Reuters (May 27, 2026) — India on track to become stock-pickers' market in June",
            "Reuters (May 26, 2026) — Indian central bank's $5 billion FX swap subscribed nearly twice over",
            "Reuters (May 2026) — India stocks set for first yearly drop in over a decade",
            "Reuters (May 2026) — Indian shares end flat; foreign investors have offloaded $24.3 billion in 2026",
            "Copley Fund Research (May 2026) — India fund weights fall below 10% for first time since 2021"
        ],
        "body": """India's markets closed on Wednesday with the Nifty 50 at 23,913.7 points — almost exactly where it started the month. They will stay closed on Thursday for a local holiday. When they reopen, the game changes.

Two brokerages — Systematix and Axis Direct — published their June outlook on the same day, and their core message was identical: the broad market rally is over. What replaces it is a stock-pickers' market, where sector selection and individual positioning will determine returns, not passive index exposure.

For NRI investors still running SIPs into broad Nifty 50 index funds, that is a signal worth taking seriously.

## The FX Swap That Tells the Real Story

On Tuesday, the Reserve Bank of India conducted a $5 billion three-year dollar/rupee buy-sell swap. The auction received bids worth $9.8 billion — nearly double the amount on offer. The RBI accepted 141 of the 254 bids, setting the premium cutoff at 9.10 rupees.

The mechanics matter. By buying dollars and selling rupees through the initial leg of the swap — settling Friday — the RBI injects rupee liquidity back into a banking system that has been running dry. India's banking system liquidity surplus has averaged below 2 trillion rupees in May, less than 0.8 per cent of deposits. The central bank has been burning through forex reserves to defend the rupee, and that defence drains rupee liquidity from the system.

The oversubscription tells you two things. First, banks are desperate for rupee liquidity — $9.8 billion in demand for a $5 billion facility is not routine. Second, the market expects the RBI will need to do more. Goldman Sachs is forecasting 50 basis points of rate hikes in India, driven by high imported energy costs, current account deficit concerns, and currency sensitivity from the Iran war's impact on oil prices.

If you hold rupee-denominated assets — NRE fixed deposits, Indian mutual funds, property — the forward curve just moved against you. The three-year forward premium dropped to 9 rupees from 9.25 after the auction, meaning the market is pricing a weaker rupee trajectory over the next three years.

## What $24 Billion in Foreign Selling Actually Means

Foreign institutional investors have sold $24.3 billion of Indian equities in 2026 so far, surpassing the record annual outflows set last year. In the same period, they bought $25 billion of Taiwanese shares, largely riding the AI hardware boom through TSMC.

Copley Fund Research's May report puts the damage in context: average India weights in global emerging market funds have fallen to 9.94 per cent — the first time below 10 per cent since January 2021, and a collapse from the 17.47 per cent peak in August 2024. The report called India "the runt of the litter among Asia's Big Four."

But the domestic story is the opposite. India's mutual fund industry hit 82 lakh crore rupees in assets. Systematic Investment Plans continue to pour in. Market-wide derivatives rollover stood at 94.2 per cent in the May series, outperforming both three-month and six-month averages — a sign that domestic participants are not leaving.

The result is a tug of war. Foreign money is selling the index. Domestic money is buying specific sectors. The net effect is a flat benchmark with enormous dispersion underneath.

## Where the Smart Money Is Positioning

Systematix and Axis Direct both identified the same three sectors showing open-interest-backed accumulation — meaning real money is building positions, not just speculating:

**Metals.** India's infrastructure push and global commodity restocking are supporting metal prices. Steel and aluminium producers are seeing fresh long positions build.

**Pharma.** Defensive in a volatile market, but also benefiting from the weaker rupee, which boosts dollar-denominated export revenue. Indian generics makers are seeing renewed interest.

**Power.** India's electricity demand is surging under the worst heatwave in a decade. Power generation and transmission companies are attracting capital as the country confronts its energy infrastructure limits.

The brokerages also flagged IT as primed for a sharp short-covering bounce. Foreign investors are heavily short Indian IT stocks. If those crowded shorts begin to unwind — triggered by any positive earnings revision or rupee weakness that benefits exporters — the move could be violent and fast.

## What NRIs Should Consider

The Nifty 50 is expected to trade between 23,000 and 25,000 in June. That is a 2,000-point range — roughly 8 per cent — which is wide enough for active traders but directionless for passive holders.

For NRIs running monthly SIPs into broad index funds, the play is patience. The macro headwinds — oil prices, foreign outflows, potential rate hikes — will keep the index rangebound. Your SIP is buying at reasonable valuations, but do not expect quick returns.

For NRIs willing to be selective, the evidence points to tilting toward metals, pharma, and power — either through sector-specific mutual funds or direct stock positions if you have a demat account.

For NRIs holding dollar deposits and considering repatriation, the arithmetic has shifted. The rupee at 95.50 — down from 83 a year ago — means your dollars buy 15 per cent more Indian assets than they did twelve months ago. But Goldman's rate hike forecast and the RBI's aggressive dollar defence suggest the rupee could weaken further. There is no obvious urgency to convert.

The one thing the data does not support is doing nothing while pretending the old playbook still works. India is no longer a rising-tide market. It is a market that rewards research, sector conviction, and tactical timing. June will prove that."""
    }
]


# ── Main execution ──

def main():
    print("=" * 60)
    print("The Videshi — Lifestyle-Health & Markets-Finance Writer")
    print(f"Run time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    published = 0
    failed = 0

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n--- Article {i}/{len(ARTICLES)}: {article['category']} ---")
        print(f"Headline: {article['headline'][:70]}...")

        # Word count check
        word_count = len(article['body'].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ❌ REJECTED: Below 400-word minimum")
            failed += 1
            continue

        # Headline length check
        if len(article['headline']) > 200:
            print(f"  ⚠ Headline is {len(article['headline'])} chars (max 200)")

        # Image sourcing
        print(f"  Sourcing image...")
        img_url, img_attr = source_image(
            article['slug'],
            person_name=article.get('person_name'),
            pexels_query=article.get('pexels_query'),
            pexels_fallback=article.get('pexels_fallback')
        )

        article['image_url'] = img_url
        article['image_attribution'] = img_attr or ''

        # Publish
        art_id = publish_article(article)
        if art_id:
            published += 1
        else:
            failed += 1

        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"Results: {published} published, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
