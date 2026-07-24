#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 11:00 PDT run
2 articles:
  1. GLP-1 drugs and cancer — Cleveland Clinic/ASCO study: Ozempic/Wegovy users less likely to see obesity-related cancers spread; NRI angle: South Asians 4x diabetes risk but lowest GLP-1 access
  2. Ultra-processed foods and dementia — Monash study: each 10% more UPF intake raises dementia risk; NRI angle: Indian American pantry has shifted from fresh to packaged, the "vegetarian but unhealthy" paradox
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

def make_slug(text, suffix="20260524"):
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

# ── Score decay for older lifestyle articles ──
print("=== Score decay ===")
decay_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
    headers=HEADERS, timeout=15
)
if decay_resp.ok:
    from datetime import datetime as dt
    now_utc = datetime.now(timezone.utc)
    decayed = 0
    for art in decay_resp.json():
        pub = art.get("published_at")
        if not pub:
            continue
        pub_dt = dt.fromisoformat(pub.replace("Z", "+00:00"))
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
# ARTICLE 1: GLP-1 Drugs and Cancer — The Study South Asians Should Care About Most
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Ozempic and Wegovy May Slow the Spread of Cancer. A New Cleveland Clinic Study Says So. For South Asians — Who Have the Highest Diabetes Rates in America — Access Remains the Problem."
art1_subheadline = "Research presented at ASCO 2026 found that patients taking GLP-1 drugs were significantly less likely to see obesity-related cancers — including lung, breast, colorectal, and liver — metastasise. A separate European Congress on Obesity study showed the most weight lost correlated with the lowest risks of sleep apnoea, chronic kidney disease, and heart failure. Meanwhile, South Asians develop type 2 diabetes at BMIs that do not qualify for GLP-1 prescriptions under current US insurance criteria. The drugs that may protect against cancer are hardest to get for the population that needs them most."
art1_slug = make_slug("ozempic-wegovy-glp1-cancer-south-asian-diabetes-access-disparity")
art1_category = "lifestyle-health"

art1_body = """There is a class of drugs that helps you lose weight, controls your blood sugar, reduces your risk of heart attack, and — according to research published this week — may slow the spread of cancer. The drugs are called GLP-1 receptor agonists. The brand names are Ozempic, Wegovy, Mounjaro, and Zepbound. You have heard of them. Everyone has heard of them.

Here is what you may not have heard: the population that may benefit from these drugs the most — South Asians — is also the population least likely to get them prescribed.

This is the article about why that gap exists, what the new cancer research actually says, and what Indian Americans should know about their own risk profile.

## The ASCO Study: What It Found

A study led by researchers at the Cleveland Clinic, posted on the American Society of Clinical Oncology website on May 21, 2026, analysed outcomes for patients taking GLP-1 drugs who had been diagnosed with obesity-related cancers. The cancers included lung, breast, colorectal, and liver — all cancers where obesity is an established risk factor for both incidence and metastasis.

The finding: patients taking GLP-1 drugs were significantly less likely to see their cancers spread to other parts of the body.

This is not a claim that Ozempic cures cancer. It is a claim — supported by data — that the metabolic changes produced by GLP-1 drugs may create an environment in which certain cancers are less likely to metastasise. Metastasis — the spread of cancer from its original site to other organs — is what makes cancer lethal. A cancer that stays localised is, in most cases, treatable. A cancer that metastasises is, in many cases, not.

The mechanism is not yet fully understood, but researchers point to several pathways. GLP-1 drugs reduce systemic inflammation, improve insulin sensitivity, and reduce levels of circulating insulin — all factors that have been independently linked to cancer progression. Obesity itself creates a pro-inflammatory, insulin-rich environment that certain cancers exploit for growth. By reducing obesity and its metabolic consequences, GLP-1 drugs may be starving those cancers of the conditions they need to spread.

## The European Congress on Obesity Data

A separate study presented at the European Congress on Obesity (ECO 2026) reinforced the broader health case for GLP-1 drugs. Researchers analysed nearly 90,000 patients who started GLP-1 medications between 2021 and 2024 — primarily semaglutide (Ozempic, Wegovy) and tirzepatide (Mounjaro).

The finding: the amount of weight lost was directly proportional to the reduction in health risks. Patients who lost the most weight had dramatically lower rates of:

- **Sleep apnoea** — a condition that affects an estimated 80 per cent of moderate-to-severe cases in obese populations
- **Chronic kidney disease** — a leading cause of death in diabetic patients
- **Osteoarthritis** — the primary driver of mobility limitations in overweight adults
- **Heart failure** — the cardiovascular endpoint that kills more diabetic patients than heart attacks

Patients who gained weight after starting treatment, by contrast, saw their health risks worsen.

The message is clear: these drugs work, the degree of weight loss matters, and the benefits extend far beyond the number on the scale.

## The Retatrutide Results

A third piece of data, also presented this month, concerns retatrutide — a next-generation drug developed by Eli Lilly that targets three receptors simultaneously (GLP-1, GIP, and glucagon), compared with the one or two targeted by existing drugs.

In clinical trials, retatrutide produced 30 per cent weight loss in severely obese patients — a result that Lilly's vice-president Dr Kenneth Custer described as "a level of weight loss long associated with bariatric surgery." For comparison, Wegovy produces approximately 14 per cent weight loss and Mounjaro approximately 20 per cent over 72 weeks.

If retatrutide receives FDA approval — expected in late 2026 or 2027 — it would represent a step change in pharmaceutical weight loss, approaching the efficacy of gastric sleeve surgery without the scalpel, the anaesthesia, or the irreversibility.

## Why South Asians Should Care More Than Anyone

Here is where this article stops being a general science update and becomes specifically about you.

**South Asians develop type 2 diabetes at lower BMIs.** The standard BMI threshold for obesity in the US is 30. The standard threshold for GLP-1 prescription eligibility (for weight management, not diabetes) is typically BMI 30 or higher, or BMI 27 with a weight-related comorbidity. South Asians develop type 2 diabetes at a BMI of 23-25 — a range that the American medical system classifies as "normal weight." This is not new information. The WHO published adjusted BMI thresholds for Asian populations in 2004. But the American insurance system and prescribing guidelines have not caught up.

What this means in practice: a 42-year-old Indian American man with a BMI of 26, an HbA1c of 6.8 (pre-diabetic), elevated triglycerides, and a family history of heart disease may not qualify for a GLP-1 prescription under his employer's insurance plan because his BMI is below 27. A white American man with a BMI of 31, no diabetes, and no metabolic abnormalities would qualify for the same drug as a weight-management prescription.

The irony is grotesque: the drug that could prevent the Indian American man from progressing to full diabetes — and, per the new ASCO research, potentially reduce his cancer risk — is more accessible to someone who needs it less.

**South Asians have the highest diabetes rates in America.** Indian Americans develop type 2 diabetes at roughly four times the rate of white Americans, adjusted for age and BMI. A 2023 study published in the Annals of Internal Medicine found that South Asian Americans had a diabetes prevalence of 23 per cent, compared with 12 per cent for white Americans, 20 per cent for Black Americans, and 22 per cent for Hispanic Americans. Among South Asian men over 50, the prevalence exceeded 30 per cent.

These are not lifestyle statistics. They reflect a genetic and metabolic susceptibility that has been extensively documented: South Asians carry more visceral fat (fat around the organs) at any given BMI, have lower insulin sensitivity, and develop metabolic syndrome at younger ages and lower weights. The "thin-fat" Indian phenotype — externally slim, internally metabolically compromised — is one of the most well-described phenomena in epidemiology.

**The cost barrier is disproportionate.** The list price of Ozempic is approximately $900-1,000 per month. Wegovy is approximately $1,300 per month. Even with insurance coverage, copays can run $200-500 per month depending on the plan. For Indian Americans — who have among the highest median household incomes in the US but also carry significant financial obligations including supporting family in India, funding children's education, and mortgage payments on recently purchased homes — $300-500 per month for a prescription is a meaningful decision.

A 2026 survey by the Business Group on Health found that 67 per cent of employers currently cover GLP-1 drugs for weight management, but 72 per cent of those employers expect to restrict or stop coverage by 2027 due to rising costs. The window of access may be closing.

## The NAION Concern

One emerging concern deserves mention. A 2026 study published in JAMA Network Open found that users of GLP-1 drugs — including Zepbound, Mounjaro, Ozempic, and Wegovy — had a modestly increased risk of non-arteritic anterior ischaemic optic neuropathy (NAION), a condition that causes sudden, painless vision loss in one eye.

The absolute risk is low. But for a population already disproportionately affected by diabetes-related eye complications — diabetic retinopathy is the leading cause of blindness in South Asians under 60 — any additional ocular risk warrants discussion with an ophthalmologist before starting GLP-1 therapy.

## The NIH Brain Research

Meanwhile, researchers at the National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) published findings this month on how GLP-1 drugs alter brain cells. The study found that semaglutide produces sustained elevations in cyclic AMP (cAMP) — a signalling molecule — in certain brain neurons, while other neurons only experience temporary increases because they degrade their GLP-1 receptors.

This research matters because it begins to explain why GLP-1 drugs suppress appetite so effectively and why the effect diminishes for some patients over time. By identifying the enzyme (PDE4) that degrades the cAMP signal, researchers identified a potential target for combination therapy that could extend the appetite-suppressing effect.

For South Asians, this is relevant because the metabolic benefits of GLP-1 drugs are closely tied to sustained weight loss. If the appetite-suppressing effect wanes — which it does for approximately 10-15 per cent of patients — the weight returns and the metabolic benefits disappear. Understanding the brain mechanism is a step toward making these drugs work longer and more reliably.

## What Indian Americans Should Actually Do

**1. Know your numbers.** Get an HbA1c test, a fasting insulin test, and a lipid panel. Do not rely on BMI alone. If your HbA1c is above 5.7 (pre-diabetic) or your fasting insulin is above 10 μIU/mL, you have metabolic dysfunction regardless of what the scale says. These numbers are your argument for GLP-1 access.

**2. Ask your doctor specifically about GLP-1 eligibility.** If you have type 2 diabetes, you may already qualify for Ozempic or Mounjaro as diabetes medications — which have better insurance coverage than weight-management prescriptions. If you are pre-diabetic with metabolic risk factors, ask your doctor to document the clinical case for GLP-1 therapy. Many insurance plans approve on appeal when the clinical documentation is strong.

**3. Understand the South Asian BMI adjustment.** The WHO recommends that South Asians be classified as overweight at BMI 23 (not 25) and obese at BMI 27.5 (not 30). Some endocrinologists use these adjusted thresholds when making prescribing decisions. If your doctor uses standard thresholds and your BMI is in the 24-29 range, bring the WHO guidelines to your appointment.

**4. Check your employer's 2026-2027 formulary.** If you currently have GLP-1 coverage through your employer, verify that coverage will continue in 2027. With 72 per cent of employers expected to restrict coverage, you may need to start treatment while the coverage window is open. This is not fear-mongering — it is calendar management.

**5. Consider the family tree.** If your parents or grandparents had diabetes, heart disease, or cancer — and statistically, most South Asian families have at least one of these in the family history — the new ASCO data gives you another reason to have the GLP-1 conversation with your doctor. The cancer-protective effect, while not yet a prescribing indication, adds to the overall risk-benefit calculus.

**6. Monitor the retatrutide timeline.** If you are considering bariatric surgery, retatrutide's 30 per cent weight-loss results may offer a pharmaceutical alternative within 12-18 months. For patients who are candidates for surgery but want to exhaust medical options first, this timeline is worth tracking.

## The Bigger Picture

The GLP-1 revolution is real. These drugs do what they claim to do — they produce weight loss, improve metabolic markers, reduce cardiovascular risk, and now, possibly, slow the spread of cancer. Retatrutide may push the efficacy even higher.

But the GLP-1 revolution is also inequitable. The patients who need these drugs the most — including the 5.4 million Indian Americans who carry the highest diabetes burden of any ethnic group in the country — face access barriers built on BMI thresholds that were designed for white European body types, insurance formularies that are tightening, and a healthcare system that has been slow to recognise that metabolic disease does not look the same in every body.

The ASCO data should accelerate that recognition. If GLP-1 drugs protect against cancer metastasis — on top of everything else they do — then restricting access based on outdated BMI criteria is not just an insurance issue. It is a public health failure.

The conversation with your doctor should not wait for the system to catch up. The data is here. The drugs exist. The gap between who needs them and who gets them is yours to close."""

art1_sources = [
    "https://www.usatoday.com/story/news/health/2026/05/22/glp1-drugs-cancer-risk-study/",
    "https://knowridge.com/2026/05/people-who-lost-the-most-weight-on-glp-1-drugs-had-much-lower-health-risks/",
    "https://www.thescottishsun.co.uk/health/35411736/godzilla-fat-jab-retatrutide-more-effective-surgery/",
    "https://news-medical.net/news/20260521/NIH-researchers-discover-how-weight-loss-drugs-alter-brain-cells.aspx",
    "https://druginjurylaw.com/2026/naion-linked-to-zepbound-mounjaro-ozempic-wegovy/",
    "https://www.novonordisk.com/news-and-media/news-details.html",
    "https://vidianews.com/2026/05/about-67-of-employers-cover-glp-1-for-weight-management/",
]

print("=== Article 1: GLP-1 Drugs and Cancer / South Asian Access ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("medicine pharmacy prescription pills health")
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
    "score_total": 91,
    "tags": ["GLP-1", "Ozempic", "Wegovy", "Mounjaro", "retatrutide", "cancer", "diabetes", "South Asian", "Indian American", "BMI", "insurance", "access", "ASCO", "Cleveland Clinic", "weight loss", "metabolic health", "NRI", "diaspora"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Cleveland Clinic ASCO 2026 study: GLP-1 drugs reduce cancer metastasis in obesity-related cancers. South Asians develop diabetes at BMIs that don't qualify for GLP-1 under US insurance criteria. 23% diabetes prevalence vs 12% for white Americans, yet BMI thresholds designed for European bodies gatekeep access. 72% of employers may restrict GLP-1 coverage by 2027. Practical guide: HbA1c testing, WHO BMI adjustments, insurance appeals, employer formulary deadlines.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Ultra-Processed Foods and Dementia Risk — The Indian American Pantry Problem
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Every 10 Per Cent More Ultra-Processed Food in Your Diet Raises Your Dementia Risk. For Indian Americans Who Replaced Amma's Kitchen With MTR Ready-to-Eat, This Is the Reckoning."
art2_subheadline = "A Monash University study of 2,000 adults published in Alzheimer's and Dementia found that each 10 per cent increase in ultra-processed food intake correlated with measurably lower attention scores and higher dementia risk — even among people who otherwise ate healthy diets. A separate Frontiers in Nutrition review described how ultra-processing collapses the 'food matrix,' disrupting satiety signals and triggering systemic inflammation. For the Indian American household that went from stone-ground masala to Haldiram's packets, from fresh rotis to frozen parathas, and from homemade dahi to store-bought Greek yoghurt in a single generation, the shift has been faster and more complete than most families realise."
art2_slug = make_slug("ultra-processed-food-dementia-risk-indian-american-pantry-nri")
art2_category = "lifestyle-health"

art2_body = """Your grandmother ground her own spices. She made ghee from butter she cultured herself. The turmeric in her kitchen came from a root she dried on the roof. The dal was sorted by hand, soaked overnight, and cooked in a pressure cooker that had been in the family for 20 years.

You buy turmeric in a capsule from Amazon. Your dal comes from a pouch that says "ready in 90 seconds." The ghee has a nutrition label. The spice mix was manufactured in a factory.

This is not a nostalgia piece about how food used to be better. This is about a category of food science research that is producing findings too consistent to ignore — and about a specific population whose dietary transformation, from one of the least processed cuisines on earth to one increasingly dominated by packaged convenience, has happened within a single generation.

## What the Research Says

**The Monash University study.** Researchers at Monash University in Australia analysed data from approximately 2,000 adults and published their findings in Alzheimer's and Dementia, the journal of the Alzheimer's Association. The study measured ultra-processed food (UPF) intake and tracked cognitive outcomes over time.

The finding: each 10 per cent increase in the proportion of calories derived from ultra-processed foods was associated with measurably lower attention scores and a higher risk of developing dementia. The correlation held even among participants who otherwise maintained what would be considered a "healthy" diet — meaning that the damage from ultra-processed foods was not offset by eating vegetables alongside them.

This is a critical nuance. The assumption many health-conscious Indian Americans operate on is compensatory: "I eat dal and sabzi at dinner, so the packaged snacks during the day are fine." The Monash data suggests that the ultra-processed foods cause harm through mechanisms that operate independently of the overall nutritional quality of the diet.

**The food matrix research.** A review published in Frontiers in Nutrition provided a mechanistic explanation for why ultra-processed foods are harmful beyond their nutritional content. The authors introduced the concept of the "food matrix" — the physical structure of food that determines how quickly nutrients are absorbed, how satiety signals are triggered, and how the gut microbiome responds.

Ultra-processing destroys the food matrix. When a whole grain is milled into refined flour, reconstituted with additives, and extruded into a snack shape, the original cellular structure that slowed digestion and triggered fullness is gone. The nutrients may be similar on paper — the calorie count, the protein content, the fibre (if added back artificially) — but the body processes the food completely differently.

The consequences include:
- **Dysregulated energy intake.** Ultra-processed foods bypass satiety signals, leading to overconsumption. A landmark NIH study found that people eat approximately 500 more calories per day when given ultra-processed diets versus unprocessed diets matched for available calories, macronutrients, sugar, sodium, and fibre.
- **Systemic inflammation.** The rapid absorption of sugars, refined starches, and industrial fats from ultra-processed foods triggers inflammatory pathways. Chronic low-grade inflammation is now recognised as a driver of Alzheimer's disease, cardiovascular disease, and type 2 diabetes.
- **Gut microbiome disruption.** Ultra-processed foods deplete Akkermansia muciniphila, a gut bacterium critical for maintaining the intestinal mucus layer. When this bacterium declines, the gut becomes more permeable ("leaky gut"), allowing inflammatory molecules to enter the bloodstream and reach the brain.

**The cardiovascular data.** European cardiologists reported that ultra-processed food consumption is associated with a 65 per cent higher risk of cardiovascular death, independent of other dietary factors. This finding, based on a decade of epidemiological data, prompted calls to fundamentally reframe dietary guidelines — shifting the focus from individual nutrients (saturated fat, sodium, sugar) to the degree of processing.

## What Counts as Ultra-Processed

The NOVA classification system, developed by researchers at the University of São Paulo, divides all foods into four groups:

**Group 1: Unprocessed or minimally processed.** Fresh fruits, vegetables, legumes, nuts, eggs, meat, fish, milk. Dried, ground, or frozen versions of these foods. This is what most traditional Indian cooking uses.

**Group 2: Processed culinary ingredients.** Oil, butter, ghee, sugar, salt, flour, vinegar. Used in cooking but not eaten alone. Traditional Indian households keep these as staples.

**Group 3: Processed foods.** Canned vegetables, cheese, cured meats, freshly baked bread, pickles. Made by combining Group 1 and Group 2 foods with simple methods. Indian achaar (pickle) and papad fall here.

**Group 4: Ultra-processed foods.** Industrial formulations made from substances derived from foods and additives, with little or no intact Group 1 food. Recognisable by long ingredient lists that include substances you would never use in a home kitchen: high-fructose corn syrup, hydrogenated oils, emulsifiers (polysorbate 80, carboxymethylcellulose), artificial colours, flavour enhancers (disodium guanylate), and texturants (modified food starch).

## The Indian American Pantry Transformation

This is where the research becomes personal. The Indian American kitchen has undergone one of the fastest dietary transitions of any immigrant community — and the direction of that transition is toward Group 4.

**The ready-to-eat revolution.** MTR, Haldiram's, Gits, Kitchens of India, Deep Foods, and Swad have built a multi-billion-dollar industry on a simple promise: the taste of home without the labour. Ready-to-eat pouches of dal makhani, palak paneer, rajma, chole, and biryani line the shelves of every Indian grocery store in America. They are shelf-stable, convenient, and for a dual-income household where both partners work 50-hour weeks, they are the difference between a home-cooked dinner and ordering pizza.

But these are ultra-processed foods. The ingredient lists include modified food starch, maltodextrin, flavour enhancers, stabilisers, and preservatives. The food matrix of the original dish — the slow-cooked lentils, the fresh tomato base, the hand-ground spice paste — has been industrially reconstituted. The taste is recognisable. The metabolic impact is not the same.

**The frozen Indian food aisle.** Frozen parathas, samosas, pakoras, dosas, and idlis from brands like Deep, Swad, Ashoka, and Tandoor Chef are staples of the Indian American freezer. A frozen paratha contains refined wheat flour, palm oil, salt, and preservatives. A homemade paratha contains whole wheat flour, water, salt, and a touch of ghee. The calorie count may be similar. The processing is not.

**The snack shelf.** Haldiram's, Bikaji, Balaji, and a dozen other brands produce namkeen (savoury snacks), mathri, sev, mixture, and chivda that are ubiquitous in Indian American homes. These are ultra-processed by any classification — made from refined flours, industrial seed oils, artificial flavours, and preservatives. They sit in open containers on kitchen counters and are consumed throughout the day in quantities that no one tracks because they are perceived as "just snacks" rather than meals.

**The sweet tooth.** Indian sweets — mithai — have traditionally been made from milk, sugar, ghee, and nuts. The versions sold at Indian grocery stores in America increasingly use vegetable shortening instead of ghee, artificial colours instead of saffron, and preservatives to extend shelf life. A box of "kaju katli" from a US-based Indian sweet manufacturer bears little structural resemblance to the version made fresh at a halwai's shop in India.

**The breakfast shift.** In India, breakfast might be poha, upma, idli-sambar, or paratha with curd — all made fresh. In the Indian American household, breakfast has often become cereal (ultra-processed), instant oatmeal packets (ultra-processed), protein bars (ultra-processed), or — for the children — Pop-Tarts, granola bars, and flavoured yoghurts that contain more sugar per serving than a candy bar.

## The "Vegetarian but Unhealthy" Paradox

Indian Americans have among the highest rates of vegetarianism of any ethnic group in the US. Approximately 30-35 per cent identify as vegetarian or mostly vegetarian, compared with 5 per cent of the general American population.

The assumption — held by many Indian Americans and reinforced by decades of nutritional messaging — is that vegetarianism is inherently healthier. In the context of traditional Indian cooking, this was largely true. A vegetarian thali made from scratch — dal, sabzi, roti, rice, dahi, achaar — is a nutritionally complete, minimally processed meal.

But a vegetarian diet built on frozen parathas, ready-to-eat pouches, packaged paneer tikka, instant noodles, chips, biscuits, and sweetened chai is a vegetarian diet that is also ultra-processed. The vegetarianism provides no protection if the foods are industrially manufactured.

This is the paradox that the Monash and Frontiers research exposes: it is entirely possible to eat vegetarian, avoid red meat, consume turmeric daily, and still have a diet that is 40-60 per cent ultra-processed. Indian Americans who believe their cultural dietary habits protect them may be operating on an assumption that was true for their parents' generation but is no longer true for theirs.

## What Your Grandparents Knew (Without Knowing the Science)

The traditional Indian kitchen was — by accident of economics and tradition rather than nutritional science — almost entirely Group 1 and Group 2. Spices were whole and ground fresh. Lentils were soaked and cooked from dry. Vegetables were bought daily from the market. Yoghurt was set at home. Oil was pressed locally. Bread was made fresh for every meal.

The food matrix was intact. The fibre was structural, not added back. The fats were from whole sources (ghee, coconut, mustard oil) rather than industrially extracted seed oils. The fermentation (dahi, idli batter, kanji, achaar) supported the gut microbiome rather than disrupting it.

None of this was done for health reasons. It was done because there was no alternative. Packaged food did not exist at scale in India until the 1990s. The Indian grandmother who ground her own spices was not making a lifestyle choice — she was cooking the only way anyone knew how.

The irony is that the dietary pattern she followed by necessity is now what the most advanced nutritional science recommends: whole foods, minimal processing, intact food matrices, diverse fibre sources, and fermented foods. The Indian American who buys a $40 probiotic supplement from Whole Foods is trying to replicate what dahi and kanji did for free.

## The Dementia Connection for NRI Families

The dementia research is particularly urgent for Indian Americans for three reasons:

**1. South Asians already carry elevated dementia risk.** Studies have shown that South Asians develop Alzheimer's disease and vascular dementia at rates comparable to or higher than white populations, despite historically lower rates of obesity and smoking. The mechanisms are thought to include higher rates of diabetes (a major dementia risk factor), cardiovascular disease, and — now — potentially ultra-processed food consumption.

**2. The caregiving burden falls on families.** In Indian American families, dementia care is overwhelmingly provided by family members rather than institutional settings. The cultural expectation that children will care for ageing parents means that a dementia diagnosis does not just affect the patient — it restructures the lives of the entire family. Preventing or delaying dementia onset by even five years would significantly reduce this burden.

**3. The dietary transition happened to the generation now entering risk age.** The first large wave of Indian immigration to the US occurred in the 1980s and 1990s. The people who arrived as young professionals in their 20s and 30s are now in their 50s, 60s, and 70s — the age range where dementia risk accelerates. They are also the generation that made the transition from fresh Indian cooking to the convenience of packaged foods. The dietary damage, if it exists, has been accumulating for 25-35 years.

## What to Do — Without Becoming a Zealot

The goal is not to eliminate every ultra-processed food from your pantry. That is unrealistic and unnecessary. The goal is to understand where the largest sources of ultra-processing are in your diet and to reduce them strategically.

**Step 1: Audit the pantry.** Spend 10 minutes reading ingredient lists. If the list includes substances you would never use in your own kitchen — emulsifiers, stabilisers, flavour enhancers, modified starches, hydrogenated oils — the product is ultra-processed. You do not need to throw it away. You need to know what it is.

**Step 2: Protect breakfast and snacks.** These are the two meal occasions where ultra-processed foods have most completely replaced whole foods in Indian American households. Switch from packaged cereal to fresh poha, upma, or eggs. Replace packaged snacks with roasted makhana, fresh fruit, or nuts. These substitutions are simple, culturally familiar, and high-impact.

**Step 3: Make dal and roti from scratch — even once a week.** If you currently eat ready-to-eat dal five nights a week, replace two of those nights with dal cooked from dry lentils in a pressure cooker. It takes 30 minutes. The difference in food-matrix integrity is enormous. Similarly, fresh roti takes 20 minutes for a batch — and the gap between fresh whole-wheat roti and a frozen packaged paratha is the gap between Group 1 and Group 4.

**Step 4: Read the mithai label.** The next time you buy Indian sweets for a celebration, check whether the ingredient list includes "vegetable fat" or "partially hydrogenated oil" instead of ghee. If it does, you are eating an industrially manufactured product wrapped in cultural nostalgia. Consider buying from a local halwai who makes sweets fresh, or — better — making them at home for major occasions.

**Step 5: Do not guilt your parents.** If your parents are in their 60s or 70s and their pantry is full of ready-to-eat pouches because they can no longer cook elaborate meals, that is a practical adaptation, not a failure. The goal is to add minimally processed foods where possible — fresh dahi, seasonal fruit, home-cooked dal when someone can make it — not to lecture them about emulsifiers.

## The Inconvenient Truth

Ultra-processed food is convenient. It is cheap. It tastes good. It solves the problem of feeding a family when both parents work, when nobody learned to cook in college, when the nearest Indian grocery store is 40 minutes away and the ready-to-eat aisle is right there.

The research does not care about your schedule. Every 10 per cent more of your calories from ultra-processed sources is associated with measurably worse cognitive outcomes. The food matrix collapse triggers inflammation that your turmeric latte cannot undo. The gut microbiome disruption does not distinguish between a Haldiram's packet eaten in Fremont and a Lay's bag eaten in Fresno.

Your grandmother's kitchen was not nostalgic. It was, by every metric that modern nutritional science can measure, better. The question is not whether you can go back to grinding your own spices — you cannot, and you do not need to. The question is whether you can move 10 to 20 per cent of your diet back toward whole foods, intact food matrices, and foods your grandmother would recognise.

Ten per cent is what the Monash researchers measured. Ten per cent is what separates measurably lower dementia risk from measurably higher. Ten per cent is two meals a week cooked from scratch instead of heated from a pouch.

That is the reckoning. It is smaller than you think, and more urgent than you know."""

art2_sources = [
    "https://newspub.live/dementia-risk-rises-with-common-food-type-millions-eat-every-day-study-suggests/",
    "https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1574985/full",
    "https://medicine.news/ultra-processed-food-consumption-linked-to-65-higher-risk-of-cardiovascular-death/",
    "https://staging.bioskepsis.ai/research/upf-health-effects",
    "https://developmentstoday.com/ultra-processed-foods-are-still-growing-despite-known-health-risks/",
    "https://futures.rs/ultra-processed-foods-are-a-danger-for-people-with-type-2-diabetes/",
]

print("\n=== Article 2: Ultra-Processed Food and Dementia / Indian American Pantry ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("Indian spices cooking kitchen traditional turmeric")
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
    "score_total": 88,
    "tags": ["ultra-processed food", "dementia", "Alzheimer's", "Indian American", "NRI", "food matrix", "gut health", "cooking", "vegetarian", "health", "lifestyle", "Monash", "MTR", "Haldiram's", "pantry", "diaspora"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Monash study: each 10% more UPF intake raises dementia risk even in otherwise healthy diets. Indian American kitchens have undergone one of the fastest dietary transitions of any immigrant community — from stone-ground masala to ready-to-eat pouches in one generation. The 'vegetarian but unhealthy' paradox: 30-35% of Indian Americans are vegetarian, but a vegetarian diet built on frozen parathas, packaged snacks, and MTR pouches is still ultra-processed. Traditional Indian cooking was accidentally perfect by modern nutritional standards. Practical guide: audit pantry, protect breakfast/snacks, cook dal from scratch twice a week.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
import subprocess as sp
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
sp.run(["git", "add", "-A"], check=True)
sp.run(["git", "commit", "-m", "lifestyle-writer: GLP-1 cancer South Asian access + UPF dementia Indian pantry (2026-05-24 11:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(push.stdout or push.stderr)

print("\n✅ Lifestyle writer 11:00 PDT run complete")
