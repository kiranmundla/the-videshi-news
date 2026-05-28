#!/usr/bin/env python3
"""
Videshi Lifestyle-Health + Markets-Finance Writer
Run: 2026-05-27 19:00 PDT
Articles:
1. GLP-1 drugs linked to slowing cancer spread (lifestyle-health)
2. Food dyes linked to diabetes & cancer risk (lifestyle-health)
3. India markets: first yearly decline in a decade (markets-finance)
"""

import json, os, sys, uuid, requests, urllib.parse
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- Image Sourcing ---
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    topic_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Create topic first
    cat = article["category"]
    vertical_map = {
        "lifestyle-health": "culture",
        "markets-finance": "economy",
        "news": "politics",
        "entertainment": "culture",
        "sports": "sports",
        "technology": "tech",
        "nri-world": "diaspora",
        "food": "culture",
        "travel": "culture",
        "immigration": "policy"
    }
    vertical = vertical_map.get(cat, "culture")

    topic_payload = {
        "id": topic_id,
        "canonical_title": article["headline"][:200],
        "vertical": vertical,
        "category": cat,
        "status": "published",
        "score_total": 0,
        "signal_count": 1,
        "created_at": now,
        "updated_at": now
    }
    r_topic = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_topics",
        headers=HEADERS,
        json=topic_payload
    )
    if r_topic.status_code not in (200, 201):
        print(f"  ⚠ Topic creation: {r_topic.status_code} {r_topic.text[:100]}")
        return None

    payload = {
        "id": art_id,
        "topic_id": topic_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": cat,
        "vertical": vertical,
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        result = r.json()
        returned_id = result[0]["id"] if isinstance(result, list) and result else art_id
        print(f"  ✓ Published: {article['headline'][:60]}... [{returned_id}]")
        return returned_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:200]}")
        return None


# --- Articles ---

articles = []

# ============================================================
# ARTICLE 1: GLP-1 Drugs and Cancer (lifestyle-health)
# ============================================================
art1_body = """A Cleveland Clinic study of 12,112 cancer patients has found that GLP-1 receptor agonists — the drug class that includes Ozempic, Wegovy and Zepbound — are associated with significantly lower rates of cancer progression across four major tumour types. The findings were posted on 21 May on the American Society of Clinical Oncology website ahead of the annual ASCO meeting.

## The Numbers That Matter

The study, led by Dr Mark David Orland of the Taussig Cancer Institute, compared cancer patients taking GLP-1 drugs against a matched group taking DPP-4 inhibitors, another class of Type 2 diabetes medication. Researchers tracked whether Stage 1 through Stage 3 cancers advanced to Stage 4.

The reductions were substantial. Among non-small cell lung cancer patients, 10 per cent of GLP-1 users progressed to Stage 4, compared with 22 per cent of those on DPP-4 inhibitors. Breast cancer progression dropped from 20 per cent to 10 per cent. Colorectal cancer fell from 22 per cent to 13 per cent. Liver cancer went from 28 per cent to 19 per cent.

Patients whose tumours had higher levels of the GLP-1 receptor itself lived longer. In breast cancer patients, higher GLP-1 receptor expression was linked to a 45 per cent lower risk of death.

## Why This Matters for South Asians

South Asians carry the highest burden of Type 2 diabetes of any ethnic group on earth. In the United States alone, Indian Americans are diagnosed with diabetes at nearly four times the rate of white Americans when adjusted for body mass index. Millions are already on GLP-1 medications or their earlier-generation alternatives.

The implications are double-edged. If you or your parents are taking semaglutide or a related drug for diabetes or weight management, you may already be receiving a cancer-protective benefit that neither you nor your doctor expected. But the study also raises uncomfortable questions about access. GLP-1 drugs remain expensive — Ozempic lists at roughly $900 per month without insurance in the US — and South Asian patients in India and the broader diaspora are far less likely to have access to these medications than those in the West.

## What the Experts Say

Dr Marcin Chwistek of the Fox Chase Cancer Center called the consistency across tumour types particularly noteworthy. "Data this large and this consistent warrant a prospective randomised trial," he said.

Researchers cautioned that the study is observational, not a randomised controlled trial, and cannot prove the drugs directly slowed cancer growth. But they noted no increase in serious side effects, including pancreatitis, among cancer patients on GLP-1 medications.

The working hypothesis is that GLP-1 drugs may fight cancer through multiple pathways — reducing chronic inflammation, altering tumour metabolism and improving immune system surveillance. All three mechanisms are especially relevant for South Asians, who tend toward higher baseline inflammatory markers.

## What to Do With This Information

Do not start taking Ozempic because of this study. That would be reckless. But if you are already on a GLP-1 medication for diabetes or weight management, these findings suggest the drug may be doing more for you than you realised. Discuss the results with your doctor at your next appointment.

If you have a parent or relative in India on older-generation diabetes drugs like metformin or sulfonylureas, this study adds to the growing evidence that GLP-1 medications may offer benefits that extend well beyond blood sugar control. The conversation about upgrading their treatment is worth having — with their endocrinologist, not at the dinner table."""

articles.append({
    "headline": "The Diabetes Drug Millions of South Asians Already Take May Be Quietly Slowing Their Cancer. A Cleveland Clinic Study of 12,112 Patients Found the Evidence.",
    "subheadline": "GLP-1 drugs like Ozempic cut cancer progression by up to 55 per cent across four tumour types. South Asians, who carry the world's highest diabetes burden, may be benefiting without knowing it.",
    "body": art1_body,
    "slug": "glp1-ozempic-cancer-progression-cleveland-clinic-south-asian-diabetes-20260527",
    "category": "lifestyle-health",
    "sources": [
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/health/2026/05/23/glp-1-drugs-cancer-may-reduce-cancer-progression/90218499007/"},
        {"name": "American Society of Clinical Oncology (ASCO)", "url": "https://www.asco.org"},
        {"name": "Fox News Health", "url": "https://www.foxnews.com/health/ozempic-style-drugs-linked-major-slowdown-cancer-spread"}
    ],
    "image_search": {"pexels": "diabetes medication pills prescription", "pexels_fallback": "medical research laboratory"},
    "image_caption": "GLP-1 receptor agonists, originally developed for diabetes, are showing unexpected cancer-protective properties",
    "image_attribution": "Pexels"
})

# ============================================================
# ARTICLE 2: Food Dyes and Diabetes/Cancer (lifestyle-health)
# ============================================================
art2_body = """Two landmark studies from the NutriNet-Santé cohort — published in Diabetes Care and the European Journal of Epidemiology — have found that high consumption of food dyes is associated with a 38 per cent increase in Type 2 diabetes risk and a 14 per cent increase in overall cancer risk. The research, conducted with more than 100,000 participants tracked over 14 years, is the first large-scale epidemiological study to document the connection between colour additives and chronic disease.

## What the Studies Found

Researchers at INSERM and Sorbonne Paris Nord University divided participants into three groups based on their exposure to food dyes. Those in the highest third — people who regularly consumed a soda, a ready-made meal and a dessert cream — faced sharply elevated risks compared with the lowest-exposure group.

The diabetes findings, published on 20 May in Diabetes Care, showed a 38 per cent higher risk of Type 2 diabetes. For cancer, published in the European Journal of Epidemiology, the numbers were a 14 per cent higher overall risk, climbing to 21 per cent for breast cancer and 32 per cent for postmenopausal breast cancer.

But here is the twist that should alarm every Indian kitchen: curcumin used as a food additive (E100) was associated with a 49 per cent increased risk of Type 2 diabetes. Beta-carotenes (E160a) showed a 44 per cent higher risk. Caramel colourings (E150) added 43 per cent.

## The Curcumin Paradox

The finding about curcumin will seem counterintuitive to anyone raised in an Indian household. Turmeric is the backbone of Indian cooking, used for centuries as an anti-inflammatory spice. But the curcumin in a supplement or a food additive is not the same molecule in the same context.

"Some substances, when removed from their original food matrix and separated from nutrients and fibers, no longer provide the same health benefits once isolated, purified and reintroduced into ultra-processed foods," explained Mathilde Touvier, INSERM research director who coordinates the study.

When your mother grinds turmeric into dal, the curcumin is embedded in a matrix of fibre, fat and other phytochemicals that modulate its absorption and metabolism. When a food manufacturer extracts curcumin and adds it as E100 to a packaged snack, that context is gone. The molecule is the same. The metabolic response is not.

## The American Processed Food Trap

This matters for the Indian diaspora because the dietary transition that happens after immigration is almost universally toward more processed food. The family that cooked every meal from scratch in Hyderabad or Pune starts buying pre-made sauces, packaged snacks, coloured beverages and ready meals in Houston or London.

A third study from the same team, published in the European Heart Journal, found that preservatives — sulfites and nitrites — were associated with a 24 per cent increased risk of hypertension. South Asians already have the highest cardiovascular death rate of any ethnic group.

The pattern is consistent: the further you move from whole-food cooking toward processed alternatives, the more additive exposure accumulates, and the more chronic disease risk stacks.

## What This Means for Your Kitchen

The message is not that all food additives will kill you. It is that the dose matters, the frequency matters, and the food matrix matters. One packaged meal is not a health crisis. A daily diet built around processed food — which is increasingly what second-generation diaspora children eat — introduces cumulative exposure to dozens of colour additives, preservatives and emulsifiers that traditional Indian cooking never contained.

The United States, under Health Secretary Robert Kennedy Jr, is preparing to ban eight synthetic colourings by the end of the year. European regulations are already stricter. But even the natural additives used by European manufacturers are not harmless in industrial concentrations.

Your grandmother did not need a PhD in food chemistry to feed you safely. She used turmeric, not E100. She used tamarind, not citric acid. She used jaggery, not caramel colouring. The epidemiology is finally catching up to what her kitchen already knew."""

articles.append({
    "headline": "A Study of 100,000 People Found That Food Dyes Raise Diabetes Risk by 38 Per Cent and Cancer Risk by 14 Per Cent. Your Grandmother's Kitchen Did Not Use a Single One of Them.",
    "subheadline": "The NutriNet-Santé cohort study is the first to link colour additives to chronic disease at scale. Curcumin as an additive — not as turmeric — was the worst offender.",
    "body": art2_body,
    "slug": "food-dyes-diabetes-cancer-risk-100000-nutrinet-curcumin-additive-indian-kitchen-20260527",
    "category": "lifestyle-health",
    "sources": [
        {"name": "Le Monde", "url": "https://www.lemonde.fr/en/environment/article/2026/05/22/high-consumption-of-food-dyes-linked-to-increased-risk-of-type-2-diabetes-and-cancer_6753721_114.html"},
        {"name": "Diabetes Care (journal)", "url": "https://diabetesjournals.org/care"},
        {"name": "European Journal of Epidemiology", "url": "https://link.springer.com/journal/10654"}
    ],
    "image_search": {"pexels": "Indian spices turmeric cooking kitchen", "pexels_fallback": "colorful processed food snacks"},
    "image_caption": "Turmeric in whole-food form offers anti-inflammatory benefits. As an isolated food additive, it was linked to a 49 per cent increase in diabetes risk.",
    "image_attribution": "Pexels"
})

# ============================================================
# ARTICLE 3: India Markets First Yearly Decline (markets-finance)
# ============================================================
art3_body = """Indian equities are on course for their first annual decline in more than a decade, according to a Reuters poll of 24 analysts published on 27 May. The Nifty 50 has fallen 8.5 per cent since January. The Sensex has dropped 10.8 per cent. Foreign portfolio investors have sold more than $23 billion of Indian stocks this year, surpassing last year's record outflows. And the rupee has hit an all-time low of 96.96 against the dollar.

## The Scale of the Unravelling

A year ago, India was the world's most celebrated emerging market. Fund managers from New York to Singapore were overweight Indian equities. The Nifty traded at 26,000. The narrative was simple: fastest-growing major economy, young demographics, digital infrastructure, Modi's reform agenda. That narrative has cracked.

The benchmark Nifty 50 was forecast to end 2026 at 26,000 — roughly flat from current levels after recovering from the drawdown. If realised, the annual decline of about 0.5 per cent would be India's first yearly loss since 2015. The Sensex is projected to end the year at 84,150.

"Everyone wants returns at the end of the day," said Rajat Agarwal, Asia equity strategist at Société Générale. "The returns are not there, earnings growth is almost negligible to very low. AI is where the flavour of the town is right now and this is where India, not just we lack it, we are actually on the wrong side."

South Korea's AI-laden KOSPI index has surged more than 200 per cent in a year. India's information technology stocks index has fallen by more than a third since December 2024.

## Three Crises Converging

The first crisis is capital flight. Foreign portfolio investors now own a record-low share of Indian equities. Domestic institutional investors, buoyed by monthly SIP inflows from retail investors, have been absorbing the selling. Without them, analysts estimate the Nifty would be near 19,000 to 20,000 — not 24,000.

The second crisis is the rupee. The currency hit 96.96 per dollar last week before recovering to about 95.50 on RBI interventions. The central bank just conducted a $5 billion dollar-rupee swap that attracted nearly $10 billion in bids, underscoring the desperation for dollar liquidity. Goldman Sachs is forecasting another 50 basis points of rate hikes for India, driven by imported energy costs and a widening current account deficit.

The third crisis is oil. The Iran-Israel war, now three months old, has kept the Strait of Hormuz partially blocked and Brent crude near $100 per barrel. India imports over 85 per cent of its oil. Every $10 increase in crude widens the trade deficit, weakens the rupee and feeds inflation.

## What This Means for NRI Money

If you hold Indian mutual funds through a US-based brokerage or an Indian demat account, your portfolio has likely lost 15 to 20 per cent in dollar terms this year — the equity drawdown compounded by rupee depreciation.

India's GDP data for Q1 2026 is due on 28 May. The consensus forecast is 6.5 per cent year-on-year growth, which sounds robust until you factor in that nominal GDP growth is barely ahead of inflation, corporate earnings are stagnant, and exports are contracting.

The RBI is quietly dusting off its 2013 playbook — NRI bonds, FCNR deposit schemes and emergency swaps — to attract dollar inflows. If you have a US dollar account, expect your Indian bank to start calling you with offers.

For NRI investors who have been dollar-cost-averaging into Indian equities through SIPs, the mathematics remains sound over a five-to-ten-year horizon. But the next three to six months carry meaningful downside risk. A slim majority of analysts — 13 of 24 — expect a further correction.

## The Structural Problem

The deeper issue is not cyclical but structural. India has not built significant exposure to the global AI trade. It has not produced a company in the league of TSMC, Samsung or NVIDIA. Its IT services giants — Infosys, TCS, Wipro — are labour-arbitrage businesses, not innovation engines.

"A culture of innovation — that thing is absent in our country," said Kishan Gupta, director at CD Equisearch. As long as that remains true, India will continue to trade at a premium it cannot justify when global capital has cheaper, higher-return alternatives."""

articles.append({
    "headline": "India's Stock Market Is Heading for Its First Annual Loss in a Decade. Foreign Investors Have Pulled Out $23 Billion. The Rupee Just Hit an All-Time Low. Here Is What It Means for Your Money.",
    "subheadline": "A Reuters poll of 24 analysts forecasts the Nifty flat at best by year-end. Goldman Sachs expects more rate hikes. The RBI is courting NRI dollars. A guide for diaspora investors navigating the worst year since 2015.",
    "body": art3_body,
    "slug": "india-stock-market-first-yearly-decline-nifty-fpi-exodus-rupee-nri-investor-guide-20260527",
    "category": "markets-finance",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-stocks-set-first-yearly-drop-over-decade-foreign-investors-leave-2026-05-27/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-central-banks-5-billion-fx-swap-subscribed-nearly-twice-over-2026-05-26/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-track-become-stock-pickers-market-june-brokerages-say-2026-05-27/"}
    ],
    "image_search": {"pexels": "Indian stock exchange Bombay trading floor", "pexels_fallback": "stock market charts red decline"},
    "image_caption": "Indian equities are on track for their first annual decline since 2015, battered by foreign capital flight, a weak rupee and surging oil prices",
    "image_attribution": "Pexels"
})


# --- Main ---
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"Videshi Lifestyle/Markets Writer — {datetime.now()}")
    print(f"{'='*60}\n")

    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)}: {article['category']} ---")
        print(f"  Headline: {article['headline'][:80]}...")

        # Validate article quality
        word_count = len(article["body"].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ✗ REJECTED: Body too short ({word_count} words, min 400)")
            continue
        if len(article["headline"]) > 200:
            print(f"  ⚠ Headline long ({len(article['headline'])} chars) but keeping")
        if len(article["subheadline"]) < 15:
            print(f"  ✗ REJECTED: Subheadline too short")
            continue

        # Source image
        img_url = None
        search = article.pop("image_search", {})

        # Try Pexels
        if not img_url and search.get("pexels"):
            img_url = fetch_pexels_image(search["pexels"], search.get("pexels_fallback"))

        # Validate
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Image validation failed, dropping image")
            img_url = None

        article["image_url"] = img_url
        if not img_url:
            print(f"  ⚠ No image found, publishing without image")
            article["image_attribution"] = ""

        # Publish
        art_id = publish_article(article)
        if art_id:
            print(f"  ✓ Article {i} published successfully")
        else:
            print(f"  ✗ Article {i} failed to publish")

    print(f"\n{'='*60}")
    print(f"Writer run complete")
    print(f"{'='*60}\n")
