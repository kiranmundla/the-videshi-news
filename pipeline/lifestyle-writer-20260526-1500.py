#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-26 15:00 PDT run
2 articles:
  1. NutriNet-Santé cohort study (Diabetes Care, May 20, 2026 + European Journal
     of Epidemiology, April 9, 2026): 100,000+ participants, food dyes linked to
     38% increased risk of type 2 diabetes and 14% increased cancer risk.
     KEY FINDING: Curcumin (E100) — when used as a food ADDITIVE — associated with
     49% increased risk of type 2 diabetes. Beta-carotenes (E160a) 44%. Caramel
     colorings (E150) 43%. Natural food dyes NOT safer than synthetic ones.
     The researchers (EREN team, INSERM, Sorbonne Paris Nord) explain: substances
     stripped from their original food matrix and purified behave differently in the
     body. Beta-carotene is antioxidant in carrots but risky as isolated additive.
     Same for curcumin: protective in turmeric (food matrix with piperine, fiber,
     other polyphenols) but associated with diabetes risk when extracted, purified,
     and added to processed foods or supplements.
     NRI angle: Indian Americans face this from multiple directions: (a) the turmeric
     supplement industry ($2B+) sells isolated curcumin as a health product;
     (b) processed "golden milk" products use E100; (c) MAHA/Kennedy pushing
     "natural" dyes as replacement for synthetic dyes — French study shows natural
     dyes are equally associated with risk. South Asians already have 4x diabetes
     risk at lower BMI. Your mother's haldi in dal — in the food matrix with oil,
     black pepper, fiber — is not the same as a curcumin capsule.

  2. European Heart Journal (May 22, 2026): 112,000+ participants from NutriNet-Santé
     cohort. Food preservatives linked to 29% greater risk of high blood pressure
     and 16% higher risk of heart attacks/stroke. Even "natural" antioxidant
     preservatives (citric acid, ascorbic acid/vitamin C) linked to 22% greater
     risk of high blood pressure. 8 specific preservatives identified: potassium
     sorbate (E202), potassium metabisulphite (E224), sodium nitrite (E250),
     ascorbic acid (E300), sodium ascorbate (E301), sodium erythorbate (E316),
     citric acid (E330), rosemary extracts (E392). Ascorbic acid also specifically
     linked to cardiovascular disease. NRI angle: South Asians have the highest
     rates of cardiovascular disease of any ethnic group globally. Traditional
     Indian kitchen preserved food through turmeric, mustard oil, salt, sun-drying,
     and fermentation — no chemical preservatives. The pickle your grandmother made
     lasted a year without E202 or E250. The "mango chutney" from the American
     grocery store has potassium sorbate. The deli meat in your kids' lunchbox has
     sodium nitrite. The shift from home-preserved Indian food to American
     preservative-laden food tracks the cardiovascular risk.
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

def make_slug(text, suffix="20260526"):
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
        print(f"  - {art.get('slug','?')[:70]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()
recent_slugs = " ".join([a.get("slug", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["food dye diabetes curcumin", "curcumin e100 additive", "food coloring diabetes cancer", "preservative hypertension heart", "preservative blood pressure cardiovascular", "sodium nitrite citric acid heart"]:
    if check_term in recent_headlines or check_term in recent_slugs:
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
# ARTICLE 1: The Curcumin Paradox
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "The Curcumin in Your Supplement Is Not the Same as the Turmeric in Your Dal. A Study of 100,000 Adults Found That Curcumin Used as a Food Additive Was Associated with a 49 Percent Increased Risk of Type 2 Diabetes. The Turmeric Your Mother Cooked With Was in a Completely Different Molecular Context."
art1_subheadline = "Two studies from the NutriNet-Santé cohort — one published May 20, 2026, in Diabetes Care, the other in the European Journal of Epidemiology — analyzed food additive exposure in more than 100,000 French adults over an average of eight years. High exposure to food dyes was associated with a 38 percent increased risk of type 2 diabetes and a 14 percent increased risk of cancer overall. Curcumin (E100), when used as an isolated food coloring additive, was associated with a 49 percent increased risk of type 2 diabetes. Beta-carotene (E160a) showed a 44 percent increase. Caramel coloring (E150) showed 43 percent. The researchers — from INSERM, Sorbonne Paris Nord University, and the EREN team — explain why: when bioactive compounds are stripped from their original food matrix, separated from the fibers, fats, and co-occurring nutrients that modulate their absorption and metabolism, they behave differently in the body. Curcumin in turmeric, consumed with black pepper, oil, and fiber in a traditional Indian dal, is not the same substance as curcumin extracted, purified, concentrated into a 500-milligram capsule, and swallowed with water. The food matrix is not packaging. It is pharmacology."
art1_slug = make_slug("curcumin-supplement-not-turmeric-dal-food-additive-49-percent-diabetes")
art1_category = "lifestyle-health"

art1_body = """There is a jar of turmeric capsules in every Indian American household. The capsules cost between twenty and sixty dollars for a sixty-day supply. They contain curcumin — the yellow polyphenol extracted from the turmeric rhizome — in concentrations of 500 to 1,500 milligrams per capsule, often formulated with piperine (black pepper extract) to boost bioavailability by up to 2,000 percent.

There is also a bag of haldi in every Indian American household. The bag costs two to four dollars from the Indian grocery store. It contains ground turmeric root — curcumin still embedded in its original food matrix alongside volatile oils (turmerone, ar-turmerone, zingiberene), dietary fiber, minerals, and dozens of other polyphenols. A typical serving of turmeric in a dal or sabzi delivers 30 to 50 milligrams of curcumin, not 500.

The supplement industry treats these as the same substance at different doses. A study published this month suggests they are not.

## The Studies

Two studies from the NutriNet-Santé cohort, conducted by researchers from INSERM (France's National Institute of Health and Medical Research), Sorbonne Paris Nord University, and the Epidemiology of Nutrition Research Team (EREN), analyzed food additive exposure in more than 100,000 French adults followed for an average of eight years.

The first, published on May 20, 2026, in Diabetes Care — a journal of the American Diabetes Association — examined the relationship between food dye exposure and type 2 diabetes risk. The second, published in the European Journal of Epidemiology, examined food dyes and cancer risk.

NutriNet-Santé is uniquely positioned to conduct this research. It is the only large cohort that quantifies additive exposure at the level of individual food brands. Every six months, more than 180,000 participants provide detailed 24-hour food logs that include specific brand names. Researchers then cross-reference these logs with the Open Food Facts database and the French Food Observatory to identify which additives — and how much of each — participants actually consumed.

Participants were divided into thirds based on their exposure to each food dye: the top third (highest exposure), the middle third, and the bottom third (lowest exposure). The researchers then compared disease incidence across these groups over the study period (2009 to 2023-2024), adjusting for tobacco use, alcohol consumption, sociodemographic profile, physical activity, overall diet quality, and body mass index.

## The Findings

High exposure to food dyes — both synthetic and natural — was associated with:

**A 38 percent increased risk of type 2 diabetes** compared to the lowest-exposure group.

**A 14 percent increased risk of cancer overall**, rising to 21 percent for breast cancer and 32 percent for postmenopausal breast cancer.

But the most striking findings concerned individual "natural" food colorings — the very additives that the Make America Healthy Again (MAHA) movement and the FDA are promoting as safer alternatives to synthetic dyes:

**Curcumin (E100)** — the yellow compound extracted from turmeric and used to color mustards, cheeses, baked goods, yogurts, ice creams, and beverages — was associated with a **49 percent increased risk of type 2 diabetes**.

**Beta-carotene (E160a)** — extracted from carrots or red palm oil, used to color cheese, yogurt, cakes, and fruit drinks — was associated with a **44 percent increased risk of type 2 diabetes** and a **41 percent increased risk of breast cancer**.

**Caramel coloring (E150)** — used in colas, baked goods, ice cream, and sauces — was associated with a **43 percent increased risk of type 2 diabetes** and a **15 percent increased risk of cancer overall**.

**Anthocyanins** — extracted from fruits and vegetables, used to color beverages and confections — were associated with a **40 percent increased risk of type 2 diabetes**.

Mathilde Touvier, INSERM research director and principal investigator of the NutriNet-Santé study, offered a blunt assessment: "Natural food additives are not proof of safety for consumers."

## Why the Same Molecule Behaves Differently

The finding that sounds paradoxical — curcumin is associated with diabetes risk as an additive but protective in turmeric — has a precise biochemical explanation. And it is not about dose, though dose matters. It is about the food matrix.

When you eat turmeric in a dal, you are not consuming curcumin in isolation. You are consuming curcumin embedded in a complex food matrix that includes:

**Turmerone and ar-turmerone** — volatile oils that make up 30 to 40 percent of turmeric essential oil. These compounds have been shown to enhance the regeneration of neural stem cells in animal studies and have anti-inflammatory properties independent of curcumin. They also affect curcumin's solubility and absorption kinetics.

**Dietary fiber** — turmeric root contains approximately 21 grams of fiber per 100 grams. Fiber slows gastric emptying, modulating the rate at which curcumin enters the small intestine and is absorbed. This slow-release mechanism means the body processes curcumin gradually, at physiological concentrations, rather than receiving a bolus of 500 milligrams at once.

**Lipids** — Indian cooking dissolves turmeric in oil or ghee. Curcumin is lipophilic (fat-soluble). When it is dissolved in fat and consumed with a meal, it is absorbed through the lipid absorption pathway — incorporated into chylomicrons in the intestinal epithelium and transported via the lymphatic system. This is a different absorption route than swallowing a curcumin capsule with water, which delivers the compound directly to the liver via the portal vein for rapid first-pass metabolism.

**Piperine** — black pepper is added to almost every Indian dish that contains turmeric. Piperine inhibits glucuronidation — the liver's primary mechanism for metabolising curcumin and preparing it for excretion. This is well-known; it is why supplement manufacturers add piperine to curcumin capsules. But in a meal, piperine arrives alongside fiber, fat, and dozens of other compounds. In a capsule, piperine arrives alongside concentrated curcumin and nothing else. The pharmacokinetics are different.

**Other polyphenols** — turmeric contains demethoxycurcumin and bisdemethoxycurcumin, which have anti-inflammatory and antioxidant properties of their own. These are partially or fully removed during the extraction process that produces pharmaceutical-grade curcumin.

Touvier summarised this phenomenon in the Le Monde interview: "Some substances, when removed from their original food matrix and separated from nutrients and fibers, no longer provide the same health benefits once isolated, purified, and reintroduced into ultra-processed foods."

This is the food matrix effect. The matrix is not packaging. It is pharmacology. The food determines how the molecule is absorbed, metabolised, distributed, and excreted. Change the matrix, change the biology.

## The Indian American Curcumin Problem

Indian Americans face the curcumin paradox from three directions simultaneously.

**Direction one: the supplement.** The global curcumin supplement market was valued at approximately $2.1 billion in 2025, with the United States as the largest market. Indian Americans are disproportionate consumers of curcumin supplements — partly because of cultural familiarity with turmeric, partly because of the Ayurvedic tradition that frames haldi as a healing substance, and partly because American wellness culture has adopted turmeric as a superfood.

The typical curcumin supplement delivers 500 to 1,500 milligrams of isolated curcumin per capsule — ten to fifty times the amount in a serving of turmeric in cooking. Many formulations include "enhanced bioavailability" technologies (piperine, liposomal encapsulation, phytosome complexes) designed to overcome curcumin's naturally poor absorption. The marketing positions this as a feature. The NutriNet-Santé study raises the question of whether it is a risk.

**Direction two: the processed "turmeric" product.** The American grocery market is now saturated with processed products that use turmeric or curcumin as a marketing ingredient: turmeric lattes (sold as powder mixes), golden milk concentrates, turmeric-infused kombucha, turmeric gummies, turmeric protein bars, turmeric ice cream, and turmeric-flavoured snacks. Many of these products use E100 (curcumin as a food colouring) to achieve a vivid yellow colour that suggests higher turmeric content than actually present. The consumer sees "turmeric" on the label and assumes the health benefits of traditional turmeric use. The product delivers isolated curcumin in a processed food matrix — exactly the exposure pattern the NutriNet-Santé study associates with diabetes risk.

**Direction three: the ubiquity of E100 in processed foods.** Curcumin (E100) is one of the most widely used natural food colorings in the world. It appears in products that have nothing to do with turmeric or Indian food: American mustard, cheddar cheese, butter, margarine, processed cheese products, flavoured yogurts, ice cream, baked goods, canned soups, pasta sauces, confectionery, and snack foods. Indian Americans who eat these products are consuming E100 without knowing it — in addition to whatever curcumin they take as a supplement and whatever turmeric products they buy from the "wellness" aisle.

## The Diabetes Context

The NutriNet-Santé finding that curcumin as a food additive is associated with a 49 percent increased diabetes risk lands in a population already at extraordinary risk.

South Asians — including Indian Americans — have four times the risk of type 2 diabetes compared to European Americans, at lower body mass indices. The threshold BMI for diabetes risk in South Asians is approximately 23 kg/m², compared to 30 kg/m² for European Americans. A South Asian who is "normal weight" by American BMI standards may already be metabolically obese by South Asian standards.

The reasons are partly genetic (higher visceral fat deposition, lower lean muscle mass, insulin resistance at lower fat levels) and partly dietary — and this is where the curcumin paradox becomes acute. The dietary transition of Indian immigration involves simultaneously:

**Reducing traditional turmeric consumption** — as home cooking declines and restaurant/takeout/processed food consumption increases, the daily dose of turmeric-in-food-matrix drops. A household that cooked dal every night in India may cook it twice a week in America. The other five nights are pizza, pasta, takeout Chinese, Trader Joe's frozen meals, and DoorDash.

**Increasing isolated curcumin consumption** — through supplements purchased at Costco, Whole Foods, or Amazon, and through processed "turmeric" products. The supplement provides 10x to 50x the curcumin dose of cooking, without the food matrix.

**Increasing exposure to E100 in processed foods** — through the general American diet, which uses curcumin as a colouring in foods that have no relationship to turmeric.

The net effect is a paradoxical reversal: less turmeric in the food matrix (protective), more curcumin outside the food matrix (potentially risky). The Indian American who takes a curcumin supplement "because turmeric is healthy" may be increasing their diabetes risk while reducing the very dietary pattern that made turmeric protective in the first place.

## The MAHA Problem

The Trump administration's Make America Healthy Again initiative, led by Health Secretary Robert F. Kennedy Jr., has made the elimination of artificial food dyes a signature policy. The FDA has approved several new natural food colors since May 2025 and is preparing to ban eight synthetic colorings by the end of 2026. States including California, West Virginia, and Utah have passed laws restricting synthetic dyes. Major food companies — General Mills, WK Kellogg, and others — have announced plans to replace synthetic dyes with natural alternatives.

The intended direction is clear: synthetic dyes are dangerous, natural dyes are safe, let us replace the former with the latter.

The NutriNet-Santé study directly undermines this logic. The natural food dyes in the study — curcumin, beta-carotene, anthocyanins, caramel — showed associations with diabetes and cancer risk that were comparable to or greater than synthetic dyes. Curcumin's 49 percent diabetes risk increase was higher than any synthetic dye in the study.

This does not mean natural dyes are more dangerous than synthetic dyes. It means the distinction between "natural" and "synthetic" is not the relevant variable. The relevant variable is: is the substance in its original food matrix, or has it been extracted, purified, and reintroduced into a processed food? The answer to that question is the same for natural and synthetic additives: both are isolated substances consumed outside their biological context.

For Indian Americans, the MAHA push is particularly concerning. If food manufacturers replace Red 40 with beta-carotene and Yellow 5 with curcumin (E100), the resulting products will be marketed as "made with natural colours" — and Indian Americans will be disproportionately inclined to trust them because they recognise "turmeric" and "curcumin" as familiar, ancestral, safe. The NutriNet-Santé data suggests that trust may be misplaced.

## What the Supplement Industry Does Not Tell You

The curcumin supplement industry is built on a specific evidence base: dozens of studies showing that curcumin has anti-inflammatory, antioxidant, and anti-cancer properties in cell cultures, animal models, and some human trials. This evidence is real. Curcumin does modulate NF-κB signaling, does inhibit COX-2, does scavenge reactive oxygen species, and does show antiproliferative effects in cancer cell lines.

But the industry extrapolates from mechanism to population health in a way the evidence does not support. The clinical trials of curcumin supplements in humans have been, to put it generously, disappointing. A 2017 review in the Journal of Medicinal Chemistry titled "The Essential Medicinal Chemistry of Curcumin" concluded that curcumin is a PAINS compound (pan-assay interference compound) — a molecule that produces false positive results in many drug-screening assays because of its chemical instability, reactivity, and fluorescence. The authors called curcumin "a cautionary tale" and noted that despite thousands of papers, no curcumin clinical trial has produced an FDA-approved drug.

The NutriNet-Santé study adds an epidemiological dimension to this caution. At the population level, among 100,000 adults consuming curcumin as a food additive over eight years, the association is not with benefit but with risk. The 49 percent increased diabetes risk may not be caused by curcumin itself — it may be confounded by the processed food matrix in which E100 is consumed. But the direction of the association is the opposite of what the supplement industry promises.

## What This Means for Your Kitchen

The practical lesson is not that turmeric is dangerous. The practical lesson is that turmeric is not curcumin.

When you add half a teaspoon of haldi to a tadka of mustard seeds, cumin, and curry leaves in hot ghee, you are creating a lipid-dispersed, matrix-embedded delivery system for curcumin, turmerone, and dozens of co-occurring polyphenols. The curcumin is absorbed slowly, through the lymphatic system, at physiological concentrations. This is what your grandmother did. This is what the epidemiological data from Indian populations — lower cancer rates, lower inflammatory disease burden — is based on.

When you swallow a 500-milligram curcumin capsule with water, you are delivering a pharmacological dose of an isolated polyphenol directly to the liver for first-pass metabolism. No fiber to slow absorption. No turmerone for synergy. No lipid matrix for lymphatic transport. No food.

When you eat processed foods coloured with E100, you are consuming curcumin stripped from the food matrix, dissolved in whatever medium the manufacturer chose, at whatever concentration was needed to achieve the desired shade of yellow. You have no idea how much curcumin you are consuming because E100 is listed as "colour (turmeric)" on the label, with no quantity specified.

The NutriNet-Santé study cannot prove that isolated curcumin causes diabetes. It is observational. But it provides the strongest population-level signal to date that the health effects of a compound depend on the matrix in which it is consumed — and that extracting a compound from turmeric and putting it in a capsule or a processed food does not replicate the health effects of cooking with turmeric.

## The Prescription Your Grandmother Already Wrote

Cook with haldi. Half a teaspoon in the dal. A quarter teaspoon in the sabzi. A pinch in the rice. Dissolved in ghee or oil, alongside black pepper, in a dish that contains fiber, fat, and protein.

Do not take a curcumin supplement unless your physician has prescribed it for a specific condition — and even then, discuss the NutriNet-Santé findings and ask whether the evidence supports isolated curcumin for your particular indication.

Do not trust "natural" food colours any more than synthetic ones. Read ingredient lists. If a processed food lists curcumin (E100), turmeric extract, or turmeric oleoresin as a colouring, it is delivering isolated curcumin outside the food matrix.

Do not buy "golden milk" mixes, "turmeric lattes," or "turmeric-infused" processed products and assume you are getting the health benefits of cooking with turmeric. You are getting curcumin in a processed food matrix — the exposure pattern the NutriNet-Santé study associates with risk.

Your grandmother did not take supplements. She cooked. The two-dollar bag of haldi from the Indian grocery store, used a quarter teaspoon at a time in a hot pan with oil and black pepper, is the evidence-based intervention. The sixty-dollar bottle of curcumin capsules from Whole Foods is the experiment.

The food was never just an ingredient. It was always the context."""

art1_sources = [
    "https://doi.org/10.2337/dc25-2472",
    "https://www.lemonde.fr/en/environment/article/2026/05/22/high-consumption-of-food-dyes-linked-to-increased-risk-of-type-2-diabetes-and-cancer_6753721_114.html",
    "https://www.wsj.com/health/natural-food-colors-embraced-by-maha-linked-to-health-problems-bf538cfa",
    "https://link.springer.com/article/10.1007/s10654-026-01197-3",
]

print("\n=== Article 1: Curcumin Paradox / Food Dye Diabetes / Supplement vs Turmeric ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: turmeric powder and root, Indian spice preparation
art1_image = fetch_pexels_image("turmeric powder golden yellow spice traditional Indian")
if not art1_image:
    art1_image = fetch_pexels_image("haldi turmeric root and powder colorful spice")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

result1 = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 92,
    "tags": ["curcumin", "turmeric", "haldi", "food dyes", "E100", "diabetes", "type 2 diabetes", "food additive", "supplement", "NutriNet-Santé", "INSERM", "food matrix", "MAHA", "Kennedy", "FDA", "natural food coloring", "beta-carotene", "caramel coloring", "South Asian", "Indian American", "NRI", "diabetes risk", "piperine", "black pepper", "golden milk", "turmeric supplement", "processed food", "ultra-processed", "Diabetes Care", "European Journal of Epidemiology"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "NutriNet-Santé cohort (100,000+ adults, Diabetes Care May 20, 2026): Curcumin (E100) as food additive associated with 49% increased type 2 diabetes risk. Beta-carotene (E160a) 44%. Caramel (E150) 43%. Natural food dyes NOT safer than synthetic. NRI angle: Indian Americans face the curcumin paradox from three directions: (1) curcumin supplements ($2B+ market, 500-1500mg isolated doses) — no food matrix, pharmacological bolus; (2) processed 'turmeric' products (golden milk mixes, turmeric lattes, turmeric gummies) using E100 for color; (3) ubiquitous E100 in American processed foods (mustard, cheese, yogurt, baked goods). Meanwhile, traditional haldi use (half-teaspoon in dal, dissolved in ghee with black pepper and fiber) is declining as home cooking frequency drops. South Asians have 4x diabetes risk at lower BMI. The supplement industry extrapolates from cell culture to population health without evidence. MAHA push for 'natural' dyes may increase E100 exposure. The food matrix — fiber, volatile oils, lipids, piperine, co-occurring polyphenols — is not packaging; it is pharmacology. Your grandmother's haldi in dal is the evidence-based intervention. The curcumin capsule is the experiment.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Preservatives and Heart Disease
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Eight Common Food Preservatives Were Linked to High Blood Pressure in a Study of 112,000 Adults. South Asians Have the Highest Cardiovascular Death Rate of Any Ethnic Group. Your Grandmother's Kitchen Did Not Use a Single One of Them."
art2_subheadline = "A study published in the European Heart Journal on May 22, 2026, using data from the NutriNet-Santé cohort of more than 112,000 French adults followed over a decade, found that food preservatives were associated with a 29 percent greater risk of elevated blood pressure and a 16 percent higher risk of heart attacks, stroke, and angina. Eight specific preservatives — potassium sorbate, potassium metabisulphite, sodium nitrite, ascorbic acid, sodium ascorbate, sodium erythorbate, citric acid, and rosemary extracts — were each independently linked to higher blood pressure. Even the so-called natural antioxidant preservatives, including citric acid and ascorbic acid (vitamin C), were associated with a 22 percent increased risk of hypertension. For South Asian Americans — the ethnic group with the highest age-adjusted cardiovascular mortality rate in the United States — these findings describe the chemical infrastructure of the food system they adopted when they immigrated. The traditional Indian kitchen preserved food through turmeric, mustard oil, salt, sun-drying, fermentation, and acidification with tamarind or raw mango. None of these methods required potassium sorbate, sodium nitrite, or sodium erythorbate. The American kitchen does."
art2_slug = make_slug("eight-preservatives-blood-pressure-112000-south-asian-heart-grandmother")
art2_category = "lifestyle-health"

art2_body = """The achar that your grandmother made — the mango pickle, the lime pickle, the mixed vegetable pickle — lasted for a year. Sometimes two years. It sat in a ceramic jar on the kitchen shelf, exposed to the ambient temperature of a North Indian summer that regularly exceeds 45°C, and it did not spoil.

It did not spoil because the traditional Indian preservation system is remarkably effective. Raw mango or lime was cut and coated in salt, which drew out moisture through osmosis and created a hypertonic environment hostile to bacterial growth. Mustard oil — which contains allyl isothiocyanate, a potent antimicrobial — was heated and poured over the salted fruit. Turmeric, red chilli powder, fenugreek, and mustard seeds were added — each contributing its own antimicrobial and antioxidant compounds. The jar was sealed and placed in the sun for several days, during which lacto-fermentation began: beneficial Lactobacillus bacteria consumed the sugars, produced lactic acid, and lowered the pH to levels that prevented pathogenic bacterial growth.

The result was a preserved food that contained no potassium sorbate (E202), no sodium nitrite (E250), no sodium erythorbate (E316), no potassium metabisulphite (E224), and no citric acid (E330) as an additive. It was preserved through salt, oil, spice, and microbial ecology. It was also, incidentally, a probiotic food.

A study published this month suggests that the distinction between these two preservation systems — the traditional and the industrial — may matter for your heart.

## The Study

The study, published on May 22, 2026, in the European Heart Journal, used data from the NutriNet-Santé cohort — the same French population study that produced the food dye research. More than 112,000 adults above the age of 15, who tracked every bite of food by brand name for three days every six months, were followed over approximately a decade. Researchers identified 58 different preservatives in the participants' diets, cross-referenced brand-level ingredient data with the Open Food Facts and French Food Observatory databases, and compared preservative exposure levels with cardiovascular outcomes recorded in the French national health care system.

The headline findings:

**Non-antioxidant preservatives** — the ones that work by killing bacteria, mould, and yeast — were associated with a **29 percent greater risk of elevated blood pressure** and a **16 percent higher risk of heart attacks, stroke, and angina**.

**Antioxidant preservatives** — the "natural" ones used to prevent browning and rancidity, including citric acid and ascorbic acid — were associated with a **22 percent greater risk of high blood pressure**.

**One additive — ascorbic acid (E300), commonly known as vitamin C — was specifically linked to cardiovascular disease.** Not hypertension alone. Cardiovascular disease: the composite outcome of heart attacks, stroke, and angina.

## The Eight Preservatives

The researchers conducted a deep dive on 17 preservatives consumed by at least 10 percent of participants and found eight with statistically significant associations with higher blood pressure:

**Potassium sorbate (E202)** — used in wine, baked goods, cheese, and sauces to inhibit mold and yeast growth. Found in sliced bread, tortillas, packaged cakes, flavored yogurts, salad dressings, and soft drinks.

**Potassium metabisulphite (E224)** — releases sulfur dioxide when dissolved. Found in wine, beer, cider, juice, dried fruits, and fermented beverages. Also used in some restaurant preparations to keep pre-cut potatoes and salads from browning.

**Sodium nitrite (E250)** — a chemical salt used in processed meats: bacon, ham, hot dogs, deli meats, sausages, salami, and pepperoni. Sodium nitrite is the preservative that gives processed meats their pink colour and is classified by the WHO's International Agency for Research on Cancer (IARC) as a Group 1 carcinogen when consumed in processed meat.

**Ascorbic acid (E300)** — synthetic vitamin C, used as an antioxidant preservative in juices, cereals, bread, processed meats, and beverages. Not the same as the vitamin C naturally present in an orange or amla.

**Sodium ascorbate (E301)** — the sodium salt of ascorbic acid, used in processed meats and beverages.

**Sodium erythorbate (E316)** — a stereoisomer of ascorbic acid, used primarily in processed meats as a curing accelerator alongside sodium nitrite.

**Citric acid (E330)** — naturally present in lemons and citrus fruits, but manufactured industrially from Aspergillus niger mold fermentation. Used in soft drinks, candy, canned goods, frozen foods, sauces, and thousands of other processed products. One of the most ubiquitous additives in the American food supply.

**Rosemary extracts (E392)** — extracted from rosemary leaves, used as a natural antioxidant in oils, snack foods, and processed meats.

## The "Natural" Fallacy

The study's most significant contribution is its demolition of the assumption that "natural" preservatives are safe.

Citric acid is found in lemons. Ascorbic acid is vitamin C. Rosemary extract comes from a herb. These are the preservatives that health-conscious consumers feel good about seeing on ingredient lists. When they appear on a label, the consumer reads "natural," thinks "safe," and moves on.

The NutriNet-Santé data says otherwise. The five antioxidant preservatives linked to hypertension — ascorbic acid, sodium ascorbate, sodium erythorbate, citric acid, and rosemary extracts — are all "natural" in origin. And they are all associated with a 22 percent increased risk of high blood pressure.

Mathilde Touvier, the principal investigator, explained the mechanism: "Naturally occurring ascorbic acid and added ascorbic acid — which may be chemically manufactured — may have different impacts on health. The results observed here for these food additives are not true for natural substances found in fruits and vegetables."

This is the same food matrix principle identified in the food dye study. Vitamin C in an orange is consumed alongside fiber, flavonoids, hesperidin, and hundreds of other phytochemicals that modulate its absorption and biological effects. Ascorbic acid (E300) in a juice drink or a processed meat product is an isolated compound in an industrial food matrix. The body does not treat them the same way.

## What This Means for South Asian Americans

South Asians — Indians, Pakistanis, Bangladeshis, Sri Lankans — have the highest age-adjusted cardiovascular mortality rate of any ethnic group in the United States. The reasons are well-documented: genetic predisposition to higher lipoprotein(a) levels, atherogenic dyslipidemia (high triglycerides, low HDL, small dense LDL particles), higher visceral adiposity at lower BMI, insulin resistance, and elevated inflammatory markers.

These genetic predispositions are not new. They existed in the Indian population for millennia. What changed is the food environment.

The traditional Indian diet — even with its generous use of ghee, salt, and sugar — was almost entirely free of chemical preservatives. The foods that the Indian kitchen preserved were preserved through ancient techniques that relied on the biochemistry of salt, oil, acid, and beneficial bacteria:

**Salt curing** — vegetables, fish, and meat were preserved in heavy salt, which created osmotic conditions that prevented bacterial growth. Dry fish (shutki in Bengali, karuvadu in Tamil, suka in Konkani) was cured with salt and sun-dried. No E250. No E202.

**Oil immersion** — pickles, chutneys, and preserves were immersed in mustard oil or sesame oil. The oil created an anaerobic barrier that prevented aerobic bacterial growth, while the allyl isothiocyanate in mustard oil provided active antimicrobial protection.

**Fermentation** — dahi, idli batter, dosa batter, kanji, panta bhat, appam, and dozens of other preparations were preserved through controlled fermentation. The lactic acid produced by Lactobacillus and other beneficial bacteria lowered the pH and created conditions that inhibited pathogenic bacteria. The fermented food was simultaneously preserved and probiotic.

**Acidification** — tamarind, raw mango (amchur), kokum, and lime juice were used to lower the pH of chutneys, rasam, and preserved preparations. The acid provided natural preservation without citric acid (E330) from an Aspergillus niger bioreactor.

**Spice-based preservation** — turmeric (antimicrobial, antioxidant), mustard seed (antimicrobial), fenugreek (antimicrobial), asafoetida (antimicrobial), clove (eugenol — one of the most potent natural antimicrobials known), and cinnamon (cinnamaldehyde — antibacterial, antifungal) were used not only for flavour but for preservation.

**Sun-drying** — papads (pappadums), vadis (dried lentil nuggets), and dried vegetables were dehydrated in the sun, reducing water activity below the threshold required for bacterial growth.

None of these methods involve potassium sorbate. None involve sodium erythorbate. None involve industrially manufactured citric acid. And none are associated with a 29 percent increased risk of elevated blood pressure in a study of 112,000 adults.

## The Immigration Transition

When an Indian family immigrates to the United States, the traditional preservation system collapses almost immediately. The reasons are practical, not cultural:

**No sun-drying.** American apartment living and suburban homeowner association rules do not accommodate the practice of laying papads and vadis on rooftops or balconies in the sun. The sun-dried papad is replaced by the packaged papad — which contains citric acid (E330) and sometimes potassium sorbate (E202) to extend shelf life.

**No home fermentation.** The daily rhythm of setting dahi from a live culture, fermenting idli batter overnight, or preparing kanji requires time and temperature control that American work schedules and air-conditioned houses make difficult. The home-fermented dahi is replaced by Dannon or Chobani — pasteurised products that may contain sodium benzoate or potassium sorbate as preservatives.

**No homemade pickle.** The labour-intensive process of cutting, salting, oiling, and sun-maturing achar is replaced by store-bought Indian pickles — which, when manufactured for the American market, often contain citric acid, potassium sorbate, and sodium benzoate instead of relying solely on salt, oil, and fermentation.

**Processed meat introduction.** The traditional Indian diet is largely vegetarian or includes fresh meat and fish cooked the same day. Processed meats — bacon, ham, hot dogs, deli meats, sausages — are an American introduction. Indian American children grow up eating ham sandwiches for school lunch, pepperoni pizza at birthday parties, and bacon at weekend brunches. Every serving of processed meat delivers sodium nitrite (E250) and sodium erythorbate (E316) — two of the eight preservatives identified in the European Heart Journal study.

**Snack replacement.** The homemade Indian snack — fresh samosas, pakoras, murukku, chivda — is replaced by packaged American snacks: chips, crackers, granola bars, protein bars, trail mixes. These products routinely contain citric acid, ascorbic acid, and other preservatives. The Indian grocery store snacks (packaged mixture, packaged sev, packaged murukku) sold in the American market also contain preservatives that the homemade versions did not.

**Beverage replacement.** Water, buttermilk (chaas), nimbu pani, and lassi are replaced by soft drinks, juice, sports drinks, and flavoured water — all of which contain citric acid (E330) and often potassium sorbate or sodium benzoate.

The aggregate effect is a massive increase in daily preservative exposure. An Indian American who eats a ham sandwich for lunch (sodium nitrite, sodium erythorbate), drinks a juice box (citric acid, ascorbic acid), has a granola bar for a snack (citric acid), and opens a bottle of wine with dinner (potassium metabisulphite) has consumed four of the eight preservatives linked to hypertension in the European Heart Journal study — in a single day. Their grandmother, eating home-preserved food in India, consumed zero.

## The Preservative-Hypertension Pipeline

The European Heart Journal study found that 35 percent of foods containing preservatives are not classified as ultra-processed. Preservatives, as lead author Anaïs Hasenböhler noted, "are ubiquitous." They appear in foods that many consumers consider healthy: whole-grain bread, yogurt, juice, dried fruit, wine, and salad dressing.

This ubiquity creates a cumulative exposure that no single food choice can address. Hasenböhler's recommendation was direct: "There is no food group/item to remove from the diet in order to fix things. These results also support the recommendations for consumers to favour non-to-minimally-processed foods."

For South Asian Americans, "non-to-minimally-processed foods" is not an abstract dietary recommendation. It is a description of the food system their families operated for centuries. The dal, the sabzi, the roti, the rice, the raita, the chutney — these are minimally processed foods. They are preserved by cooking, by spice, by acid, and by fermentation. They do not contain E202 or E250 or E316 or E330.

The solution to preservative exposure is not a new supplement, a special diet, or a detox programme. It is what Tracy Parker, nutrition lead at the British Heart Foundation, stated plainly: choose fresh, uncooked, unprocessed items. Or, as Hasenböhler added, "frozen options which are preserved through low temperature, not necessarily through the addition of food additive preservatives."

## What You Can Do This Week

**Read ingredient lists for preservatives, not just calories and macros.** Look for E202, E224, E250, E300, E301, E316, E330, and E392 — or their common names: potassium sorbate, sodium nitrite, ascorbic acid (as an additive, not a nutrient), citric acid, rosemary extract. These are the eight preservatives the European Heart Journal study links to hypertension.

**Eliminate or reduce processed meats.** This is the single highest-impact change. Bacon, ham, hot dogs, deli meat, sausages, and pepperoni deliver sodium nitrite and sodium erythorbate — preservatives linked to both hypertension and cancer. If your children eat deli meat sandwiches for school lunch, consider alternatives: leftover sabzi in a roti wrap, hummus and vegetables, or home-cooked chicken sliced and packed cold.

**Make achar at home.** The raw materials — raw mangoes or lemons, mustard oil, salt, red chilli, turmeric, mustard seeds, fenugreek — cost less than a jar of store-bought pickle and produce a product that is preserved without chemical additives. If you did not learn from your family, there are detailed recipes from every Indian regional tradition available online. The process takes thirty minutes of preparation and a week of sun-maturation.

**Switch from packaged to homemade snacks when possible.** Homemade chivda, murukku, and shakarpara require no preservatives because they are fried (reducing water activity) and consumed within days. Packaged versions of the same snacks contain preservatives because they are designed to sit on a shelf for months.

**Check your bread.** Many commercial breads contain potassium sorbate or citric acid. Bread baked fresh and frozen does not require preservatives. Indian rotis and chapatis, made from whole wheat flour and cooked the same day, contain no preservatives at all.

**Replace juice with whole fruit.** Commercial juice contains citric acid (E330) and often ascorbic acid (E300) as preservatives. An orange, an apple, or an amla contains natural citric acid and vitamin C in their original food matrix — the form the NutriNet-Santé researchers specifically said is not associated with the risk their study identified.

## The Kitchen as Pharmacy

The European Heart Journal study cannot prove that these eight preservatives cause hypertension and cardiovascular disease. It is observational. Confounders exist. The people who eat more preservatives may differ from those who eat fewer in ways the study did not fully capture.

But the study provides the most comprehensive evidence to date that preservative exposure — not just ultra-processed food in general, but specific chemical preservatives identified by name and E-number — is associated with the cardiovascular outcomes that disproportionately kill South Asian Americans.

The traditional Indian kitchen did not need a European Heart Journal study to avoid these compounds. It avoided them because the technology of preservation it developed over centuries — salt, oil, acid, fermentation, spice, dehydration — was effective, elegant, and sufficient. The preservatives that the study links to hypertension are solutions to problems that the Indian kitchen had already solved.

The question for Indian Americans is not whether to adopt a new diet. It is whether to return to the old one — the one that preserved food without preserving the conditions for cardiovascular disease."""

art2_sources = [
    "https://academic.oup.com/eurheartj/advance-article/doi/10.1093/eurheartj/ehaf289/8143622",
    "https://www.cnn.com/2026/05/20/health/food-preservatives-heart-risk-wellness",
    "https://www.news-medical.net/news/20260522/Common-food-preservatives-linked-to-higher-cardiovascular-disease-risks.aspx",
    "https://medicaldialogues.in/cardiology/news/researchers-link-widely-used-food-preservatives-to-higher-heart-disease-risk-143247",
]

print("\n=== Article 2: Preservatives Blood Pressure / South Asian Heart / Grandmother's Kitchen ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: traditional Indian pickle/achar jar, or Indian spices for preservation
art2_image = fetch_pexels_image("Indian pickle achar jar traditional spices mango")
if not art2_image:
    art2_image = fetch_pexels_image("traditional Indian food preservation spices turmeric mustard")
if not art2_image:
    art2_image = fetch_pexels_image("Indian kitchen spices jars traditional cooking")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

result2 = sb_post("p2_articles", {
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
    "tags": ["food preservatives", "hypertension", "blood pressure", "cardiovascular disease", "heart attack", "stroke", "sodium nitrite", "potassium sorbate", "citric acid", "ascorbic acid", "E250", "E202", "E300", "E330", "European Heart Journal", "NutriNet-Santé", "South Asian", "Indian American", "NRI", "processed meat", "achar", "pickle", "traditional preservation", "fermentation", "mustard oil", "salt curing", "sun drying", "ultra-processed food", "natural preservatives", "antioxidant preservatives"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "European Heart Journal (May 22, 2026): 112,000+ adults, 8 food preservatives linked to hypertension (29% increased risk), 16% higher heart attacks/stroke. Even 'natural' antioxidant preservatives (citric acid, ascorbic acid) showed 22% increased hypertension risk. NRI angle: South Asians have the highest age-adjusted cardiovascular mortality of any US ethnic group. Traditional Indian kitchen preserved food through turmeric, mustard oil, salt, sun-drying, fermentation, and natural acidification (tamarind, raw mango) — zero chemical preservatives. Immigration collapsed this system: no sun-drying (apartment living), no home fermentation (work schedules, AC), no homemade pickle (time), plus introduction of processed meats (sodium nitrite in every school lunchbox ham sandwich), packaged snacks (citric acid), juice (ascorbic acid as preservative), wine (potassium metabisulphite). A single day's American eating hits 4 of 8 identified preservatives. Grandmother's kitchen hit zero. The traditional Indian preservation system — salt, oil, spice, fermentation — was sufficient, effective, and not associated with the cardiovascular outcomes that disproportionately kill South Asian Americans.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result2:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
subprocess.run(["git", "add", "-A"], capture_output=True)
commit_msg = "lifestyle: curcumin paradox food dye + preservatives heart disease (2026-05-26 15:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
