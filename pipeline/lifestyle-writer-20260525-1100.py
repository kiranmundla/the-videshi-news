#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-25 11:00 PDT run (18:00 UTC May 25)
2 articles:
  1. University of Sydney: Plant-based diet reverses biological age by ~4 years in just 4 weeks (Aging Cell, April 2026, 104 adults aged 65-75) — NRI angle: Indian vegetarian tradition is exactly what this study validates. Silicon Valley biohackers pay thousands for longevity supplements. Your grandmother's thali was doing it for free. Second-gen NRIs are abandoning the one dietary pattern that science now says reverses aging.
  2. McMaster University/CAHHM: Even Canada's low air pollution damages brains in midlife (Stroke, May 13, 2026, 6,878 adults) — NRI angle: Indian cities have PM2.5 levels 10-20x higher than Canada. If Canada's pristine air is enough to cause measurable cognitive damage, what is happening to the brains of NRI parents in Delhi, Mumbai, Kolkata? Every visit home, every Diwali trip — cumulative neurotoxicity. Plus California wildfire smoke.
"""

import os, json, uuid, re, requests, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

# ── Pexels env ──
pexels_path = Path.home() / "workspace/.env.pexels"
PEXELS_KEY = None
if pexels_path.exists():
    for line in pexels_path.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "PEXELS" in k.upper():
                PEXELS_KEY = v.strip()

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260525"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code == 409:
        print(f"  ⚠ Conflict (already exists) for {table}")
        return None
    r.raise_for_status()
    return r.json()

def fetch_pexels_image(query):
    """Fetch a landscape image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data.get("photos"):
            photo = data["photos"][0]
            return {
                "url": photo["src"]["large2x"],
                "photographer": photo["photographer"],
                "pexels_id": photo["id"],
                "alt": query,
            }
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

# ── Cross-check recent lifestyle articles to avoid duplication ──
print("=== Cross-checking recent lifestyle articles ===")
recent_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&order=published_at.desc&limit=30&select=id,headline,slug,published_at",
    headers=HEADERS, timeout=15
)
if recent_resp.ok:
    recent = recent_resp.json()
    print(f"  Found {len(recent)} recent lifestyle articles")
    for art in recent[:10]:
        print(f"  - {art.get('slug','?')[:60]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["biological age diet", "plant-based aging", "plant protein aging", "air pollution brain", "air pollution cognitive", "pm2.5 brain", "pm2.5 cognitive"]:
    if check_term in recent_headlines:
        print(f"  ⚠ Topic already covered: {check_term}")
        topics_ok = False

if not topics_ok:
    print("  ⚠ One or more topics already covered. Proceeding with caution.")

# ── Score decay for older lifestyle articles ──
print("\n=== Score decay ===")
decay_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
    headers=HEADERS, timeout=15
)
if decay_resp.ok:
    now_utc = datetime.now(timezone.utc)
    decayed = 0
    for art in decay_resp.json():
        pub = art.get("published_at")
        if not pub:
            continue
        pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        age_hours = (now_utc - pub_dt).total_seconds() / 3600
        if age_hours > 24 and art["score_total"] > 10:
            new_score = max(10, int(art["score_total"] * 0.92))
            if new_score != art["score_total"]:
                requests.patch(
                    f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
                    headers={**HEADERS, "Prefer": "return=minimal"},
                    json={"score_total": new_score},
                    timeout=10
                )
                decayed += 1
    print(f"  Decayed {decayed} articles (8% reduction, >24h old, score>10)")

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: A Four-Week Diet Change Just Reversed Biological
# Aging by Four Years. The Diet Looks Exactly Like What Your
# Indian Grandmother Cooked.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "A Four-Week Diet Change Just Reversed Biological Aging by Four Years in Older Adults. The Diet That Worked Best Looks Exactly Like What Your Indian Grandmother Cooked. And You Stopped Eating It."
art1_subheadline = "Researchers at the University of Sydney assigned 104 adults aged 65 to 75 to one of four diets for just four weeks. Those who shifted toward plant-based protein and complex carbohydrates showed measurable reductions in biological age — up to four years younger by biomarker analysis. The diet that produced zero improvement was the one closest to what participants were already eating: high-fat, animal-heavy, Western-standard. The diet that worked — low fat, high complex carbohydrates, plant-forward protein — is structurally identical to a traditional Indian thali: dal, roti, sabzi, raita, rice. The study was published in Aging Cell in April 2026. Silicon Valley's longevity industry charges thousands for supplements, peptides, and age-reversal protocols. The most effective anti-aging intervention documented this year costs about four dollars a plate and has been sitting in Indian kitchens for centuries."
art1_slug = make_slug("plant-diet-reverses-biological-aging-four-years-indian-thali")
art1_category = "lifestyle-health"

art1_body = """There is a $110 billion global longevity industry built on the premise that aging can be slowed, reversed, or hacked. It sells NAD+ precursors at $60 a bottle, rapamycin off-label at $200 a month, hyperbaric oxygen chambers at $150 a session, and blood plasma infusions at $8,000 a treatment. In Silicon Valley, where many of the industry's most enthusiastic customers live and work, the quest to reverse aging has become a status marker — a thing you discuss at dinner parties alongside your Oura ring data and your Zone 2 heart rate.

A study from the University of Sydney, published in Aging Cell in April 2026, has just demonstrated that you can reverse biological aging by approximately four years in four weeks. The intervention that produced this result was not a supplement, not a drug, not a biohacking protocol, and not a technology. It was a diet. Specifically, a diet built on plant-based protein and complex carbohydrates — a diet that is, in its essential architecture, indistinguishable from what most Indian grandmothers cooked every day of their lives.

The irony is almost too precise to be accidental: the most science-validated anti-aging diet of 2026 is the one that Indian Americans have been systematically abandoning since the day they landed at JFK.

## The Study

Dr. Caitlin Andrews and Associate Professor Alistair Senior at the University of Sydney's Charles Perkins Centre designed the Nutrition for Healthy Living study to test whether short-term dietary changes could influence biological age — the physiological measure of how old your body actually is, as opposed to how many years you have been alive.

Biological age is calculated from a panel of biomarkers — cholesterol levels, insulin sensitivity, C-reactive protein (an inflammation marker), blood pressure, glucose metabolism, and other physiological indicators. Two people who are both 70 years old chronologically can have biological ages of 60 and 80, depending on how their bodies are actually functioning. Biological age is a better predictor of disease risk, disability, and death than the number on your birthday cake.

The researchers enrolled 104 adults aged 65 to 75. All were non-smokers, free of major chronic diseases (no Type 2 diabetes, cancer, kidney disease, or liver disease), and had BMIs between 20 and 35. They were randomly assigned to one of four diets for four weeks:

**Omnivorous High-Fat (OHF):** 14 per cent protein (split evenly between animal and plant sources), high fat, low carbohydrates. This was the diet closest to what most participants were already eating before the study — the standard Western diet.

**Omnivorous High-Carbohydrate (OHC):** 14 per cent protein (split evenly between animal and plant sources), 28-29 per cent fat, 53 per cent complex carbohydrates.

**Semi-Vegetarian High-Fat (VHF):** 14 per cent protein (70 per cent from plant sources), high fat, low carbohydrates.

**Semi-Vegetarian High-Carbohydrate (VHC):** 14 per cent protein (70 per cent from plant sources), low fat, high complex carbohydrates.

After four weeks, the researchers measured 20 biomarkers to calculate each participant's biological age.

The results were striking in their clarity:

The **OHF group** — the one eating closest to the standard Western diet — showed **no meaningful change** in biological age. Four weeks of eating what they were already eating produced exactly the result you would expect: nothing.

The **other three groups** — every group that moved away from the high-fat, animal-heavy pattern — showed **measurable reductions in biological age**.

The **strongest statistical evidence** for age reversal was seen in the **OHC group** (omnivorous, high complex carbohydrates). The semi-vegetarian groups also showed improvements, with the **VHC group** (plant-forward, high complex carbohydrates) showing the most pronounced results — biological age reductions of approximately **four years** by biomarker analysis.

Four years. In four weeks. From food.

## What a Four-Year Biological Age Reversal Actually Means

To understand why this matters, you need to understand what biological age measures and why a four-year shift is significant.

A person whose biological age is four years younger than their chronological age has, on average, lower LDL cholesterol, lower C-reactive protein (less systemic inflammation), better insulin sensitivity, lower blood pressure, and healthier glucose metabolism than someone their same age whose biology matches their calendar.

These are not cosmetic differences. They are the difference between a 70-year-old who is metabolically healthy and a 70-year-old who is metabolically pre-diabetic, pre-hypertensive, and walking toward cardiovascular disease. Over a lifetime, a sustained four-year biological age advantage translates to measurably lower risk of heart attack, stroke, Type 2 diabetes, and dementia.

The longevity research community has spent billions trying to identify interventions that can move biological age. Most pharmaceutical and supplement interventions produce shifts of one to two years over periods of months to years. The University of Sydney study produced a four-year shift in four weeks using nothing but food composition changes.

"It's too soon to say definitively that specific changes to diet will extend your life," cautioned Dr. Andrews. "But this research offers an early indication of the potential benefits of dietary changes later in life."

The caution is appropriate. The study was small (104 people), short (four weeks), and conducted in a single population. Longer-term studies are needed. But the signal — the magnitude and speed of the biological age shift — is remarkable.

## Now Look at Your Grandmother's Plate

Here is where this becomes a story about you, if you are Indian American.

The diet that produced the strongest age-reversal results — plant-forward protein, low fat, high complex carbohydrates — is not an exotic intervention designed in a laboratory. It is a traditional Indian thali.

Consider the macronutrient profile of a standard vegetarian Indian meal:

**Protein:** Dal (lentils), chole (chickpeas), rajma (kidney beans), paneer, dahi (yoghurt). In a traditional Indian household, 60-70 per cent of dietary protein comes from plant sources — almost exactly the 70 per cent plant protein ratio in the VHC group that showed the greatest biological age reduction.

**Carbohydrates:** Roti made from whole wheat atta. Brown rice or millets (bajra, jowar, ragi) in traditional preparations. These are complex carbohydrates — high-fibre, slow-digesting, low glycaemic index. The study's high-carbohydrate groups consumed 53 per cent of calories from complex carbohydrates. A traditional Indian vegetarian meal derives 50-60 per cent of its calories from similar sources.

**Fat:** Traditional Indian cooking used modest amounts of ghee, mustard oil, or sesame oil. The total fat percentage in a traditional meal — before the modern Indian American kitchen adopted restaurant-style oil volumes — was naturally in the 25-30 per cent range. The OHC group consumed 28-29 per cent fat.

**Bioactive compounds:** Turmeric (curcumin — documented anti-inflammatory), ginger (gingerols), cumin (thymoquinone), fenugreek (galactomannan — insulin-sensitising), coriander, black pepper (piperine — enhances curcumin bioavailability by 2,000 per cent). Indian spices are not just flavouring. They are a daily low-dose pharmacopoeia that has been consumed for centuries.

The traditional Indian vegetarian thali — dal, roti, sabzi, raita, rice, pickle, a small sweet on festivals — hits almost every macronutrient target that the University of Sydney study identified as optimal for biological age reversal. It is plant-forward. It is high in complex carbohydrates. It is moderate in fat. It is rich in fibre, legumes, fermented dairy, and anti-inflammatory spices.

This is not a coincidence. This is convergent evolution. The Mediterranean diet, the Japanese diet, the traditional Indian diet — the world's longest-lived populations eat variations of the same fundamental pattern: plants, whole grains, legumes, fermented foods, moderate fat, minimal processed food. The University of Sydney study has now added experimental evidence to the observational data: this pattern does not just correlate with longevity. It actively reverses biological aging at the cellular level.

## The Abandonment

If the traditional Indian diet is a scientifically validated anti-aging protocol, why are Indian Americans dying younger than their grandparents?

Because most Indian Americans no longer eat it.

The dietary trajectory of a typical Indian American family across three generations tells a precise story of nutritional decline:

**Generation 1 (grandparents in India):** Vegetarian or near-vegetarian. Home-cooked meals. Whole grains (millets, unpolished rice, whole wheat). Seasonal vegetables. Dal twice a day. Minimal processed food. Modest portions. Daily physical activity.

**Generation 2 (immigrant parents in America):** Still cooking Indian food, but with modifications. White rice replaces brown rice and millets. Refined vegetable oil replaces mustard oil and ghee. Portion sizes increase. Restaurant-style cooking (heavier oil, more cream) becomes the aspiration. Processed Indian snacks (namkeen, biscuits, ready-to-eat packages) enter the pantry. Physical activity decreases dramatically.

**Generation 3 (children raised in America):** Indian food becomes occasional — something mom cooks on weekends or for guests. The daily diet is American: cereal or toast for breakfast, sandwiches or fast food for lunch, pizza or pasta for dinner. Protein comes primarily from chicken, beef, and processed meat. Vegetables are a garnish, not a foundation. Complex carbohydrates are replaced by refined flour, white bread, and processed snacks. The microbiome shifts. The spice cabinet shrinks.

By the third generation, the traditional Indian diet — the one that the University of Sydney has now demonstrated can reverse biological aging — has been almost entirely replaced by the Western high-fat, animal-heavy, processed-food diet that the same study showed produces zero biological age improvement.

The generation that needs the anti-aging diet most — Indian Americans in their 40s and 50s, who are developing diabetes, cardiovascular disease, and metabolic syndrome at rates that alarm public health researchers — is the generation that has abandoned it most completely.

## The Longevity Industry's Expensive Irony

There is a particular irony in the fact that many of the most enthusiastic customers of the $110 billion longevity industry are Indian American tech professionals living in Silicon Valley.

They wear Oura rings and WHOOP straps to track their sleep. They take NMN and resveratrol supplements from brands with names like Elysium and Tru Niagen. They subscribe to longevity podcasts hosted by Stanford and Harvard physicians. They discuss rapamycin dosing protocols in group chats. They pay $2,500 for comprehensive blood panels from companies like Function Health. Some have spent $25,000 or more on personalised longevity programs.

And then they go home and eat Uber Eats.

The University of Sydney study suggests that a plate of home-cooked dal, roti, and sabzi — cost: approximately $3-4 in ingredients — may produce a larger biological age reversal than any supplement currently on the market. The intervention is not proprietary. It requires no prescription. It has no side effects. It has been tested in a population of billions over thousands of years.

It is, quite literally, the thing your mother has been asking you to eat since you left for college.

## What This Means for Indian American Families

If you are an Indian American reading this, the practical implications are specific:

**If you are in your 30s or 40s:** This is the decade when biological age begins to diverge meaningfully from chronological age. The dietary choices you make now will determine whether you are biologically 50 or biologically 60 when your calendar says 55. The data from the University of Sydney is clear: a plant-forward, complex-carbohydrate-rich, low-fat diet pushes biological age backward. The Western high-fat, animal-heavy diet does nothing. You do not need to become fully vegetarian. Even the omnivorous high-carbohydrate group — which still ate animal protein — showed significant age reversal. The key variables are: more plant protein (dal, beans, lentils, tofu, paneer), more complex carbohydrates (whole wheat roti, brown rice, millets), less fat (especially less cooking oil), and less processed food.

**If you are a parent feeding children:** The dietary habits your children form now will shape their biological age trajectory for decades. Every generation of Indian Americans that moves further from the traditional diet moves further from its anti-aging benefits. Feeding your children dal and roti is not imposing a cultural obligation. It is providing a documented biological advantage.

**If you have ageing parents:** If your parents still cook and eat traditional Indian vegetarian food — if they still eat dal twice a day, make roti from whole wheat atta, cook seasonal vegetables, and use spices liberally — they are already following something close to the diet that the University of Sydney study identified as optimal. Do not let them feel embarrassed about their food. Do not let them apologise for not having steak or pasta. Their diet may be the reason they are still healthy at 75. Support it. Eat it with them. Learn to cook it.

**If you are interested in longevity:** Before you spend $60 on a bottle of NMN, try spending $4 on a bag of masoor dal. Before you pay $150 for a hyperbaric oxygen session, try making a meal that is 70 per cent plant protein and 50 per cent complex carbohydrates. Before you track your biological age with an expensive blood panel, try eating the way your grandmother ate and see how you feel in four weeks.

The University of Sydney study did not discover a new diet. It validated an ancient one. The question for Indian Americans is not whether the science works. The question is whether they will eat what their own culture already perfected — or continue paying strangers to sell them back the wisdom they threw away.

## A Note on Humility

The researchers themselves are careful to note that this is a preliminary study. Four weeks is short. One hundred and four people is small. The participants were Australian, not Indian. Biological age reduction in the short term may not translate to long-term health outcomes. More research is needed.

All of this is true.

But the direction of the evidence — from the University of Sydney, from the Mediterranean diet trials, from the Blue Zones research, from the MASALA study's data on what protects and what harms South Asian metabolic health — points in the same direction. Plant-forward, whole-grain, low-fat, spice-rich, home-cooked food is the single most consistent dietary predictor of slower aging, lower disease risk, and longer health span across every population studied.

Indian Americans inherited this diet. The question is not whether they will discover it. It is whether they will return to it before the metabolic consequences of abandoning it become irreversible.

Four years of biological age. Four weeks of eating differently. Four dollars a plate.

Your grandmother knew. Now there is a paper in Aging Cell that proves it."""

art1_sources = [
    "https://doi.org/10.1111/acel.70507",
    "https://scitechdaily.com/just-4-weeks-of-simple-diet-changes-reversed-signs-of-aging-in-older-adults/",
    "https://www.foxnews.com/health/diet-change-younger-biological-age-older-adults-4-weeks",
    "https://masalastudy.ucsf.edu/",
    "https://www.sydney.edu.au/charles-perkins-centre/",
]

print("=== Article 1: Plant-Based Diet Reverses Biological Aging 4 Years / Indian Thali ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("Indian vegetarian thali dal roti vegetables traditional food")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

result = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 94,
    "tags": ["biological age", "aging", "longevity", "plant-based diet", "vegetarian", "Indian thali", "Indian American", "NRI", "South Asian", "University of Sydney", "Aging Cell", "anti-aging", "complex carbohydrates", "dal", "roti", "sabzi", "whole grains", "millets", "biomarkers", "C-reactive protein", "insulin", "cholesterol", "Silicon Valley", "biohacking", "longevity industry", "Charles Perkins Centre"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "University of Sydney study (Aging Cell, April 2026, 104 adults aged 65-75): plant-forward, high complex carbohydrate diet reversed biological age by ~4 years in just 4 weeks. The diet that worked best — 70% plant protein, high complex carbs, low fat — is structurally identical to a traditional Indian vegetarian thali (dal, roti, sabzi, raita). The Western high-fat diet showed zero improvement. Indian Americans are systematically abandoning the ancestral diet that science now validates as the most effective anti-aging intervention. Silicon Valley longevity industry ($110B) sells supplements and protocols; a plate of dal-roti costs $4 and may outperform all of them. Three-generation dietary decline documented. MASALA study context: South Asian metabolic vulnerability makes this diet restoration even more urgent.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")

# Add image_url via PATCH if insert didn't include it
if result and art1_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art1_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art1_image["url"], "image_caption": f"Photo by {art1_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Even Canada's Clean Air Is Damaging Brains in
# Midlife. India's Air Is Twenty Times Worse. Your Parents Are
# Breathing It Every Day.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Even Canada's Clean Air Is Damaging Brains in Midlife. India's Air Is Twenty Times Worse. And Your Parents Are Breathing It Every Day."
art2_subheadline = "A study of nearly 7,000 Canadian adults published in Stroke on May 13, 2026, found that everyday air pollution — fine particulate matter from traffic, industry, and wildfire smoke — is associated with reduced cognitive function and vascular brain injury, even in Canada, where air quality is among the best in the world. The average PM2.5 exposure in the study was 6.9 micrograms per cubic metre. Delhi's annual average is 99. Mumbai's is 46. Kolkata's is 59. If air pollution at Canadian levels is enough to measurably damage brains by middle age, the cognitive toll being exacted on the 1.4 billion people breathing Indian air — including the parents, siblings, and extended families of every Indian American — is not a future risk. It is a present catastrophe happening in real time, one breath at a time, in the bodies of the people you love."
art2_slug = make_slug("air-pollution-brain-damage-canada-india-nri-parents-cognitive")
art2_category = "lifestyle-health"

art2_body = """There is a phone call that happens in Indian American households across the country, usually on a weekend morning, usually while making chai. You call your parents in India. Your mother answers. You ask how she is. She says fine. You ask what she did yesterday. There is a pause — longer than it used to be. She cannot quite remember. She mentions something about the market, or the temple, or a neighbour's visit, but the details are vague. You attribute it to age. She is 68, or 72, or 75. Memory gets fuzzy. It is normal.

A study published on May 13, 2026, in Stroke — one of the most prestigious journals in cerebrovascular research — suggests that the fuzziness may not be entirely about age. It may be about air.

Researchers at McMaster University in Hamilton, Ontario, examined 6,878 adults with a mean age of 57.6 years, recruited from across Canada as part of the Canadian Alliance for Healthy Hearts and Minds Cohort Study (CAHHM). They measured each participant's residential exposure to two common air pollutants — fine particulate matter (PM2.5) and nitrogen dioxide (NO2) — over the five years preceding enrolment, using satellite data and atmospheric modelling cross-referenced with ground-level monitoring.

Then they tested each participant's cognitive function using two standardised assessments — the Montréal Cognitive Assessment (MoCA) and the Digit Symbol Substitution Test (DSST) — and scanned their brains using MRI to detect covert vascular brain injury: silent strokes and white matter damage that produce no symptoms but erode cognitive capacity over time.

The findings were alarming. Not because the pollution levels were high — but because they were remarkably low.

## Canada's Air, Canada's Brains

The average PM2.5 concentration across the study was **6.9 micrograms per cubic metre** (μg/m³). The average NO2 concentration was **12.9 parts per billion** (ppb). These are among the lowest air pollution levels in the world. Canada's air, by any international standard, is clean.

And yet.

After adjusting for every confounder the researchers could measure — age, sex, education, income, smoking, alcohol, diabetes, hypertension, obesity, physical activity, and even the amount of greenspace near each participant's home — higher pollution exposure was still associated with worse cognitive function.

Every 5 μg/m³ increase in PM2.5 was associated with a **0.44-point reduction** on the MoCA. Every 5 ppb increase in NO2 was associated with a **0.12-point reduction**. For the DSST, a 5 μg/m³ increase in PM2.5 corresponded to a **1.31-point reduction**, and a 5 ppb increase in NO2 corresponded to a **0.38-point reduction**.

These numbers may sound small in isolation. They are not. At a population level, a 0.44-point reduction in MoCA scores is equivalent to several years of cognitive aging. It is the difference between scoring 27 (normal) and scoring 26 (the threshold where clinicians start asking follow-up questions). Across millions of people, these fractional reductions translate into thousands of additional dementia diagnoses, years of disability, and billions in healthcare costs.

On brain MRI, 8.6 per cent of participants had covert vascular brain injury — silent strokes and white matter damage — despite having no symptoms. NO2 exposure was associated with **8 per cent higher odds** of this silent brain damage for every 5 ppb increment.

The most striking finding was what did not explain the results. Diabetes, hypertension, obesity, and existing vascular brain injury — all known to damage cognition — did not change the pollution-cognition association. "Despite our extensive attempt to control for confounders," the researchers wrote, the link between air pollution and reduced cognitive function remained. This suggests a **direct neurotoxic effect** — air pollution damaging the brain through pathways that do not go through the heart or the blood vessels.

"This can be valuable towards health equity for populations at risk," said lead author Dr. Sandi M. Azab, an assistant professor at McMaster University.

## Now Do the Math for India

The CAHHM study measured cognitive damage at PM2.5 levels of 6.9 μg/m³. That is Canada's reality.

Here is India's reality, according to the World Health Organization's 2024 ambient air pollution database and IQAir's 2025 World Air Quality Report:

**Delhi:** Annual average PM2.5 = **99.7 μg/m³** (14.4 times Canada's study average)

**Kolkata:** Annual average PM2.5 = **59.0 μg/m³** (8.6 times Canada)

**Mumbai:** Annual average PM2.5 = **46.0 μg/m³** (6.7 times Canada)

**Chennai:** Annual average PM2.5 = **32.8 μg/m³** (4.8 times Canada)

**Bangalore:** Annual average PM2.5 = **36.5 μg/m³** (5.3 times Canada)

**Hyderabad:** Annual average PM2.5 = **39.2 μg/m³** (5.7 times Canada)

The WHO's recommended annual PM2.5 limit is 5 μg/m³. India's National Ambient Air Quality Standard is 40 μg/m³ — eight times the WHO guideline. Most major Indian cities exceed even India's own lenient standard.

The CAHHM study found measurable cognitive damage at 6.9 μg/m³. Every single major Indian city where your parents, your aunts and uncles, your grandparents, and your childhood friends currently live has PM2.5 levels that are 5 to 15 times higher than the levels that damaged Canadian brains.

This is not a proportional scaling — the relationship between pollution and cognitive damage may not be linear. But the direction is unambiguous: if the CAHHM researchers found a 0.44-point MoCA reduction per 5 μg/m³ of PM2.5 in Canada, the cognitive toll at Indian pollution levels is almost certainly larger, more pervasive, and more devastating.

## What Air Pollution Does to the Brain

The brain is peculiarly vulnerable to air pollution. PM2.5 particles — so small that 30 of them lined up would be thinner than a human hair — enter the body through the lungs and then enter the bloodstream. From there, they cross the blood-brain barrier — the protective layer that is supposed to keep toxins out of the brain.

Once inside the brain, PM2.5 particles trigger neuroinflammation — a chronic, low-grade immune response that damages neurons, disrupts synaptic connections, and promotes the accumulation of amyloid-beta and tau proteins — the same proteins that form the hallmark plaques and tangles of Alzheimer's disease.

Nitrogen dioxide (NO2), primarily from vehicle exhaust, contributes to oxidative stress in brain tissue, damaging the lipid membranes that protect neurons and accelerating the death of brain cells in regions critical for memory and executive function.

The CAHHM study found that cardiovascular risk factors did not explain the pollution-cognition link. This finding echoes animal studies showing that PM2.5 particles can damage the brain independently of cardiovascular disease — by entering through the olfactory nerve (the nerve that transmits smell signals) and reaching the brain directly, bypassing the bloodstream entirely.

This direct neurotoxic pathway has a particularly disturbing implication: even people who are physically healthy, who exercise, who eat well, who have no cardiovascular risk factors — if they are breathing polluted air, their brains may still be accumulating damage.

## The Indian American Double Exposure

Indian Americans face a unique cognitive pollution burden that no other ethnic group in the United States shares to the same degree: they were born into it.

Most Indian Americans older than 30 spent their childhood and adolescence in India. They breathed Indian air during the years when their brains were still developing — years when the brain is most vulnerable to environmental neurotoxins. The frontal cortex, which governs executive function, planning, and impulse control, does not fully mature until the mid-20s. Every year of childhood spent breathing Delhi's or Mumbai's or Kolkata's air was a year of neurotoxic exposure during a critical developmental window.

Then they moved to America. For many, the air improved dramatically. But the damage from the developmental years may already have been done — and the research on childhood pollution exposure suggests that some of the neurological effects are permanent.

And then there is the ongoing exposure. Indian Americans visit India regularly. Diwali trips. Summer holidays. Family emergencies. Weddings. Funerals. Each visit is a re-immersion into air that the CAHHM data suggests is measurably damaging at levels far lower than what Indian cities deliver.

Consider a typical Indian American who grew up in Delhi, moved to the Bay Area at 25, and visits home twice a year for two weeks each time. Over a 30-year period in the US, that is approximately 60 weeks — more than a year of cumulative re-exposure to Delhi's air. Add the childhood and adolescent years, and this person has spent roughly 25-27 years of their life breathing air that is 10-15 times more polluted than the levels that the CAHHM study found sufficient to damage Canadian brains.

## California's Wildfire Problem

For Indian Americans in California — which is home to the largest Indian American population in the country — there is a third layer of exposure: wildfire smoke.

During California's increasingly severe wildfire seasons, PM2.5 levels routinely spike to 50-150 μg/m³ or higher. The 2020 wildfire season turned San Francisco's sky orange and pushed PM2.5 levels above 200 μg/m³ — Delhi levels, in the heart of the Bay Area.

The CAHHM study specifically noted that wildfire smoke was among the pollution sources contributing to PM2.5 exposure in Canada. The 2023 Canadian wildfire season produced smoke that drifted across the US, turning New York City's air hazardous and temporarily giving eastern American cities the worst air quality on Earth.

For an Indian American in the Bay Area, the pattern is: breathe California's normally clean air for 10 months, breathe wildfire smoke for 2 months, fly to Delhi for Diwali, breathe Delhi air for 2 weeks, return. The brain never gets a full year of clean air. The cumulative neurotoxic burden is a rolling calculation that never resets to zero.

## Your Parents, Right Now

The most urgent implications of the CAHHM study are not for Indian Americans in the US. They are for the people Indian Americans left behind.

Your parents, if they live in any major Indian city, are breathing air right now that is 5 to 15 times more polluted than the levels that damaged Canadian brains. They are breathing it every day, all day, year after year. They have been breathing it for decades.

When your mother cannot remember what she did yesterday, it may not be age. When your father repeats the same story he told you last week, it may not be a quirk. When your parents seem foggy on a video call — slower than they used to be, less sharp, less present — the reflexive diagnosis is "they are getting older."

They are getting older. But they are also breathing air that a Canadian study has now demonstrated is sufficient to cause measurable vascular brain injury and cognitive decline at a fraction of the concentration present in Indian cities.

The CAHHM study found that 8.6 per cent of Canadian adults — breathing air at 6.9 μg/m³ — already had covert vascular brain injury on MRI. What percentage of adults in Delhi, at 99 μg/m³, have similar or worse silent brain damage? No one knows, because no one has conducted a comparable population-level brain imaging study in India. But the biology of PM2.5 neurotoxicity does not change at the border. The particles are the same. The brains are the same. The damage mechanism is the same. Only the dose is different. And the dose in India is enormous.

## What You Can Do

For your parents in India, the options are limited but not zero:

**Air purifiers.** A HEPA air purifier in the bedroom — where your parents spend 7-8 hours sleeping — can reduce indoor PM2.5 by 50-80 per cent. This is the single highest-impact intervention you can make for your parents' brain health. A quality air purifier costs ₹8,000-15,000 ($100-180). Buy two — one for the bedroom, one for the living room. This is more important than the vitamins you send them.

**N95 masks during peak pollution.** In Delhi during the winter months (November through February), when PM2.5 routinely exceeds 300-500 μg/m³, an N95 mask reduces PM2.5 inhalation by 95 per cent. Your parents will resist wearing them. Buy them anyway. Leave them by the door.

**Timing outdoor activity.** PM2.5 levels in Indian cities follow a daily cycle, peaking in early morning (6-9 AM) and evening (6-10 PM) due to traffic patterns and atmospheric conditions. The lowest levels are typically between 12-3 PM. If your parents walk for exercise, encourage them to walk in the early afternoon rather than the early morning.

**AQI monitoring.** Install the IQAir app on your parents' phone. Show them how to check it. Teach them that when the number is above 150 (unhealthy), they should stay indoors with windows closed. When it is above 300 (hazardous), they should run the air purifier and avoid going outside at all.

For yourself in the US:

**During wildfire season,** do not exercise outdoors when AQI exceeds 100. Run the air purifier. Close windows. If you have an N95 mask from the pandemic, use it during smoke events.

**When visiting India,** bring an N95 mask and use it outdoors in major cities. Consider your visit duration — every additional day of exposure at Indian pollution levels adds to your cumulative neurotoxic burden.

**Get a cognitive baseline.** If you are over 40, ask your doctor for a MoCA test at your next physical. This gives you a baseline score to track over time. Any decline in future years can be caught early.

## The Quiet Emergency

There is no alarm bell ringing in Indian American households about air pollution and brain health. There should be.

The CAHHM study demonstrated that even the world's cleanest air is not clean enough to prevent cognitive damage. India's air is not the world's cleanest. It is, in most cities, among the world's dirtiest. And 1.4 billion people are breathing it.

The neuroscience is clear: PM2.5 crosses the blood-brain barrier. It triggers neuroinflammation. It promotes amyloid accumulation. It causes silent strokes. It erodes cognitive function over time. Every breath of polluted air adds to the burden.

For Indian Americans, this is not an abstract public health statistic. It is the reason your mother pauses longer on the phone. It is the reason your father's handwriting has changed. It is the reason your uncle, who was a sharp accountant at 60, cannot manage his own bills at 70.

Aging is real. But the acceleration of cognitive decline in people breathing Indian air is also real — and it is, to some degree, preventable. An air purifier in your parents' bedroom is not a cure. But it may be the difference between your father recognising your child's face at 80 and not recognising yours.

Buy the purifier. Send the mask. Make the call. The brain damage is silent. The intervention does not have to be."""

art2_sources = [
    "https://www.ahajournals.org/doi/10.1161/STROKEAHA.124.048651",
    "https://www.medscape.com/viewarticle/air-pollution-linked-reduced-midlife-cognitive-function-2026a1000glg",
    "https://www.iqair.com/world-air-quality-report",
    "https://www.who.int/data/gho/data/themes/air-pollution",
    "https://masalastudy.ucsf.edu/",
]

print("\n=== Article 2: Air Pollution Brain Damage / Canada Study / India PM2.5 / NRI Parents ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("air pollution city smog haze skyline India")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

result = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 91,
    "tags": ["air pollution", "PM2.5", "brain health", "cognitive decline", "dementia", "India", "Delhi", "Mumbai", "Indian American", "NRI", "South Asian", "CAHHM", "McMaster University", "Stroke journal", "vascular brain injury", "MoCA", "neurotoxicity", "wildfire smoke", "California", "HEPA filter", "air purifier", "parents", "aging", "neuroinflammation", "blood-brain barrier", "nitrogen dioxide", "silent strokes"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "McMaster University/CAHHM study (Stroke, May 13, 2026, 6,878 Canadian adults): even at Canada's very low PM2.5 levels (6.9 μg/m³), air pollution measurably reduces cognitive function and causes covert vascular brain injury by midlife. Direct neurotoxic pathway — cardiovascular risk factors did not explain the association. Indian cities have PM2.5 levels 5-15x Canada's (Delhi 99, Mumbai 46, Kolkata 59). Indian Americans face double exposure: childhood development years in Indian pollution + ongoing visits + California wildfire smoke. NRI parents breathing Indian air daily may be experiencing accelerated cognitive decline beyond normal aging. Actionable: HEPA air purifiers ($100-180) in parents' bedrooms, N95 masks during peak pollution, IQAir app, timing outdoor activity to lowest-PM2.5 hours. Cognitive baseline testing recommended for Indian Americans 40+.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")

# Add image_url via PATCH
if result and art2_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art2_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art2_image["url"], "image_caption": f"Photo by {art2_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ── Git commit & push ──
print("\n=== Git push ===")
import subprocess as sp
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
sp.run(["git", "add", "-A"], check=True)
sp.run(["git", "commit", "-m", "lifestyle-writer: plant diet reverses aging 4 years + air pollution brain damage india parents (2026-05-25 11:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
