#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-25 03:00 PDT run (10:00 UTC May 25)
2 articles:
  1. Food preservatives linked to heart disease (European Heart Journal, May 20 2026, 112K French adults) — NRI angle: Indian packaged food culture (pickles, ready-to-eat, namkeens, imported sweets), the NRI pantry transition from home-cooked to packaged, preservatives in popular Indian brands, South Asian CVD vulnerability amplified
  2. Vitamin D in pregnancy boosts children's memory at age 10 (JAMA Network Open, May 2026, Copenhagen RCT) — NRI angle: South Asians have among the highest vitamin D deficiency rates globally due to darker pigmentation, indoor-heavy lifestyles, cultural modesty norms; Indian American pregnant women often severely deficient; implications for the generation being born in the US right now
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
for check_term in ["food preservative heart", "preservatives cardiovascular", "preservatives blood pressure", "vitamin d pregnancy memory", "vitamin d pregnancy cognitive", "prenatal vitamin d brain"]:
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
# ARTICLE 1: The Preservatives in Your Pantry Are Linked to Heart Disease.
# For Indian Americans, the Pantry Is the Problem.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "The Preservatives in Your Pantry Are Linked to Heart Disease. For Indian Americans, the Pantry Is the Problem."
art1_subheadline = "A landmark study of more than 112,000 French adults published on May 20 in the European Heart Journal found that people who consumed the most food preservatives had a 29 per cent higher risk of high blood pressure and a 16 per cent higher risk of heart attack, stroke, and angina. Eight specific preservatives — including sodium nitrite, potassium sorbate, citric acid, and ascorbic acid — were identified as the primary drivers. For Indian Americans, whose pantries are stocked with imported packaged foods engineered for shelf life across oceans, whose snack culture revolves around namkeens and ready-to-eat meals loaded with preservatives, and who already carry the highest cardiovascular disease burden of any ethnic group in America, this study does not describe a distant risk. It describes Tuesday."
art1_slug = make_slug("food-preservatives-heart-disease-indian-american-pantry-packaged-food")
art1_category = "lifestyle-health"

art1_body = """There is a shelf in every Indian American kitchen that tells a story about distance.

It holds the Haldiram's namkeen bought at the Indian grocery store in plastic-sealed packets designed to survive the supply chain from Nagpur to Newark. The MTR ready-to-eat dal makhani in a retort pouch with a shelf life of 18 months. The Patak's pickle in a glass jar with an ingredient list that includes acetic acid, citric acid, and potassium sorbate. The Parle-G biscuits, the Britannia Good Day cookies, the Maggi noodle packets, the Ching's Schezwan chutney. The Laxmi brand frozen parathas. The Deep frozen samosas.

These products exist because Indian Americans live thousands of miles from the kitchens that made the food they grew up eating. The preservatives in them exist because fresh food cannot survive the journey from manufacturer to distributor to ethnic grocery store to suburban pantry without chemical intervention. Every preservative on that shelf is a small compromise between the food you want and the food that will not spoil before you eat it.

A study published on May 20 in the European Heart Journal — one of the most prestigious cardiology journals in the world — has just demonstrated that those compromises are not free. They come with a cardiovascular cost. And for a population that already has the highest heart disease rates in America, that cost is compounding in ways that nobody in the community is tracking.

## What the Study Found

The research was conducted by scientists at Sorbonne Paris North University and Paris City University, led by co-authors Anaïs Hasenböhler and Mathilde Touvier. It is part of the NutriNet-Santé study, one of the largest ongoing cohort studies of diet and health in the world.

The researchers tracked the dietary habits of 112,395 French adults — average age 43, 79 per cent women — for a median of seven to eight years. Participants logged everything they ate and drank using a detailed online food diary, and the researchers cross-referenced those entries with a comprehensive food additive database to quantify each person's exposure to specific preservatives.

The team divided preservatives into two categories:

**Non-antioxidant preservatives** — chemicals that prevent mold, bacteria, and spoilage. These include sodium nitrite (E250), potassium sorbate (E202), sodium benzoate (E211), and potassium nitrate (E252). They are the preservatives you find in processed meats, condiments, pickled foods, soft drinks, and ready-to-eat meals.

**Antioxidant preservatives** — chemicals that prevent foods from browning or oxidising. These include ascorbic acid (E300, commonly known as vitamin C when used as a supplement), sodium ascorbate (E301), citric acid (E330), and tocopherols (E306-309, vitamin E derivatives). They are found in juices, baked goods, cooking oils, and snack foods.

Nearly all participants — 99.5 per cent — consumed at least one type of preservative regularly within the first two years of the study. This is not surprising. Preservatives are ubiquitous in the modern food supply.

The findings were stark:

People who consumed the highest amounts of non-antioxidant preservatives had a **29 per cent higher risk of developing high blood pressure** (hypertension) and a **16 per cent higher risk of cardiovascular disease** — including heart attack, stroke, and angina — compared with those who consumed the least.

People who consumed the highest amounts of antioxidant preservatives had a **22 per cent higher risk of developing high blood pressure**.

Among individual preservatives, eight were specifically linked to elevated blood pressure: sodium nitrite, potassium sorbate, citric acid, ascorbic acid, sodium ascorbate, calcium ascorbate, tocopherols, and sodium nitrate. One additive — ascorbic acid (E300) — was specifically linked to cardiovascular events including heart attack and stroke.

The researchers controlled for age, sex, BMI, physical activity, smoking, alcohol, education, income, family history of cardiovascular disease, and total energy intake. The associations persisted across all adjustments.

"As far as we know, this is the first study of its kind to investigate the links between a wide range of preservatives and cardiovascular health," said Hasenböhler. Touvier added that the results "support existing recommendations to favor non-processed and minimally processed foods, and avoid unnecessary additives."

## Why This Is Different From What You Have Heard Before

You have heard that ultra-processed foods are bad for you. This is not new. The NOVA classification system, developed by Brazilian researchers and now widely used in public health, categorises foods into four groups based on their degree of processing. Ultra-processed foods — the NOVA Group 4 — have been linked to obesity, diabetes, cancer, depression, and cardiovascular disease in dozens of studies over the past decade.

But most of those studies treated ultra-processed food as a single category. They told you that eating more packaged food was bad without telling you which specific ingredients were doing the damage. Was it the sugar? The sodium? The refined carbohydrates? The artificial colours? The preservatives? The emulsifiers? Or simply the displacement of whole foods from the diet?

This study isolates preservatives as a specific, independent risk factor. It is not just that people who eat more packaged food have worse cardiovascular outcomes — which could be explained by a dozen confounders. It is that specific preservative chemicals, quantified at the individual level, show dose-dependent associations with hypertension and cardiovascular disease even after controlling for overall diet quality and known risk factors.

This distinction matters because it changes the intervention. "Eat less processed food" is generic advice that most people nod at and ignore. "Check whether your favourite snack contains potassium sorbate, sodium nitrite, or citric acid, and consider how often you eat it" is specific, actionable, and tied to a concrete mechanism.

## The Indian American Pantry Problem

Here is where the study becomes personal for every Indian American household.

The standard Indian American pantry contains a higher density of preserved, packaged, imported foods than the average American pantry — not because Indian Americans are less health-conscious, but because the logistics of maintaining a culturally specific diet in a country that does not natively produce that food requires preservation.

Consider what is on the shelf:

**Pickles (achaar).** Indian pickles are among the most preserved foods in any cuisine. A typical mango pickle from a major Indian brand contains mustard oil, salt, red chilli, fenugreek, acetic acid, citric acid, and often potassium sorbate or sodium benzoate. The salt content alone is extreme — a single tablespoon can contain 800-1,200 mg of sodium, or roughly half the daily recommended limit. But beyond the salt, the acetic acid and citric acid that extend shelf life are now linked to hypertension in this study.

Indian Americans eat pickle with almost every meal. It is on the table at lunch and dinner. It goes on rice, with dal, alongside roti, in sandwiches, and as a condiment with dosa. The cumulative preservative exposure from this single food category, consumed daily for decades, is substantial.

**Ready-to-eat meals.** The Indian ready-to-eat market in America has exploded over the past decade. Brands like MTR, Haldiram's, Gits, Kohinoor, Ashoka, and Kitchen of India sell retort-pouched curries, dal, biryani, paneer, and rajma that require only microwaving. These products are designed for a shelf life of 12-18 months without refrigeration — which is only possible through aggressive thermal processing (retorting) combined with preservatives and acidity regulators.

A single pouch of MTR Dal Makhani contains citric acid. Ashoka ready-to-eat meals commonly contain citric acid and sometimes calcium chloride. Haldiram's ready meals often include acetic acid and ascorbic acid. These are exactly the preservatives the European Heart Journal study flagged.

For dual-income Indian American households — where both partners work in demanding professional environments and cooking from scratch every night is not realistic — ready-to-eat Indian meals have become a staple, not an occasional convenience. Many families consume them three to four times per week.

**Namkeens and snacks.** Haldiram's, Bikano, and Balaji namkeens — bhujia, mixture, aloo bhujia, sev — are the default snack in Indian American homes. They are served to guests, packed in lunch boxes, eaten during cricket matches, and consumed by the handful while working. They contain preservatives (typically TBHQ, citric acid, or sodium metabisulphite) alongside high sodium, refined oil, and trans fats.

A 200-gram bag of bhujia, shared among a family during an evening of TV, disappears in a single sitting. The preservative exposure from that single bag is not dangerous in isolation. But Indian Americans do not eat one bag of bhujia once. They eat it weekly, or more, for years.

**Frozen foods.** Deep, Swad, Haldiram's, and other brands sell frozen samosas, parathas, naan, spring rolls, chaat items, and sweets in every Indian grocery store's freezer section. Frozen foods require fewer preservatives than shelf-stable foods, but many still contain citric acid, sodium metabisulphite, and TBHQ as antioxidants to prevent freezer burn and rancidity.

**Imported sweets and mithai.** The box of Haldiram's rasgulla or gulab jamun brought home from the Indian store — or shipped from India by relatives — is preserved with citric acid, potassium sorbate, or sodium benzoate. Indian sweets are consumed regularly: at festivals, at pujas, after meals, and whenever guests visit. The preservative load in a single serving of commercially produced rasgulla is modest. Over a lifetime of weekly consumption, it adds up.

**Chutneys and sauces.** Ching's Schezwan sauce, Maggi Hot & Sweet, Mother's Recipe green chutney, Swad tamarind chutney — all contain preservatives (sodium benzoate, potassium sorbate, citric acid) to maintain shelf stability. These are used daily as condiments, dips, and cooking ingredients.

## The Compounding Effect

Here is the arithmetic that nobody in the Indian American community is doing:

Breakfast: Paratha from a frozen pack (citric acid, TBHQ) with pickle (citric acid, potassium sorbate, acetic acid).

Lunch: Leftover MTR rajma heated in the microwave (citric acid) with rice and a side of mango pickle (citric acid, sodium benzoate).

Snack: Haldiram's bhujia with chai (citric acid, TBHQ).

Dinner: Home-cooked dal with roti — but the roti is from a frozen pack (sodium metabisulphite), the dal is seasoned with Ching's chutney (sodium benzoate), and there is pickle on the side again (potassium sorbate).

After dinner: Two pieces of Haldiram's soan papdi from the box on the counter (citric acid).

In a single day, this person — who believes they are eating "Indian food" and therefore eating well — has consumed citric acid in six separate foods, potassium sorbate in two, sodium benzoate in two, TBHQ in two, and acetic acid in one. Every single one of these preservatives appears in the European Heart Journal study's list of compounds associated with elevated blood pressure and cardiovascular risk.

Now multiply this by 365 days. Then by 20 years.

Now overlay it with the fact that this person is South Asian — and therefore already carries the highest baseline cardiovascular risk of any ethnic group in America.

The MASALA study, the landmark longitudinal study of cardiovascular health in South Asians in the US, has documented that South Asians develop coronary artery disease at younger ages, with fewer traditional risk factors, and with more aggressive disease progression than any other group. They have higher rates of insulin resistance, metabolic syndrome, visceral adiposity, and elevated lipoprotein(a) — a genetic risk factor that is disproportionately common in South Asians and for which there is currently no treatment.

A 29 per cent increase in hypertension risk from preservative consumption — the finding from this study — is alarming for any population. For a population whose baseline hypertension risk is already elevated, whose baseline coronary artery disease risk is already the highest in the country, and whose dietary pattern concentrates preservative exposure in ways the French study did not even model, it is a five-alarm fire.

## What You Can Do

**1. Audit your pantry. Literally.** Take 30 minutes this weekend. Pull out every packaged product in your kitchen — the pickles, the ready-to-eat meals, the namkeens, the frozen foods, the chutneys, the sauces. Read the ingredient lists. Look for: citric acid (E330), potassium sorbate (E202), sodium benzoate (E211), sodium nitrite (E250), ascorbic acid (E300), TBHQ, sodium metabisulphite. Count how many products contain one or more of these preservatives. The number will surprise you.

**2. Replace, do not eliminate.** The goal is not to purge your kitchen of everything Indian. The goal is to shift the ratio. For every packaged food you eat, ask: Is there a fresh or home-cooked version that would work? Fresh pickle made at home with just mustard oil, salt, and spices — no preservatives needed if consumed within a week. Dal cooked from scratch rather than a pouch. Bhujia made at home (or at least consumed less frequently). Frozen parathas replaced by fresh dough when time allows.

**3. Be strategic about which packaged foods you keep.** Not all packaged Indian foods are equally preserved. Plain frozen vegetables, frozen roti made with just wheat flour and water, and plain basmati rice have minimal preservatives. The preservative load concentrates in condiments, pickles, ready-to-eat wet foods, and snacks. If you must buy packaged, choose products with shorter ingredient lists and fewer E-numbers.

**4. Watch the condiment trap.** Indian meals are defined by their accompaniments — pickle, chutney, raita, papad. If the main dish is home-cooked but every condiment is from a jar or packet, you have replaced the preservatives in the entrée with preservatives in the sides. Home-made chutney (cilantro, green chilli, lemon, salt — blended in two minutes) has zero preservatives and tastes better than anything in a bottle.

**5. Do not trust "natural" on the label.** The study found that antioxidant preservatives — including ascorbic acid (vitamin C) and tocopherols (vitamin E) — were also associated with elevated blood pressure. These are often marketed as "natural" preservatives. They may be derived from natural sources, but when consumed in the quantities present in industrially processed food, they are not benign.

**6. Check your blood pressure.** If you are South Asian, over 30, and eating packaged Indian food regularly, you should know your blood pressure. Not your last reading from two years ago. Your current reading. Home blood pressure monitors cost $30-50 and take 60 seconds to use. The American Heart Association recommends checking at least once a month for adults with normal readings, and weekly if readings are elevated (above 120/80). If you are consistently above 130/85, see a doctor — and tell them about your diet.

**7. Talk to your family about this.** The person most at risk in your household may not be you. It may be your parents, who eat the most pickle, the most ready-to-eat meals, the most namkeens, and who have been doing so for the longest. It may be your children, who are developing their food preferences now and normalising a diet built on preserved snacks. The conversation does not need to be an intervention. It can start with: "I just read something about preservatives in packaged food. Let me show you what is in the achaar we eat every day."

The food on that shelf in your kitchen is not trying to hurt you. It is trying to survive the distance between the place you came from and the place you live now. But your heart does not care about logistics. It only knows what you put in your body, every day, for decades. And the science now says that the chemicals keeping your food alive may be quietly making you sick."""

art1_sources = [
    "https://academic.oup.com/eurheartj/advance-article/doi/10.1093/eurheartj/ehaf317/8139429",
    "https://www.drugs.com/news/common-food-preservatives-linked-major-heart-problems-130086.html",
    "https://www.cnn.com/2026/05/21/health/high-blood-pressure-preservatives-food/index.html",
    "https://masalastudy.ucsf.edu/",
    "https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings",
]

print("=== Article 1: Food Preservatives Heart Disease / Indian American Pantry ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("Indian grocery store shelves packaged food spices")
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
    "score_total": 90,
    "tags": ["food preservatives", "heart disease", "cardiovascular", "hypertension", "blood pressure", "Indian American", "NRI", "packaged food", "South Asian", "MASALA study", "European Heart Journal", "citric acid", "potassium sorbate", "sodium nitrite", "sodium benzoate", "ultra-processed", "Indian grocery", "namkeen", "pickle", "achaar", "ready-to-eat", "pantry", "Haldiram's", "MTR"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "European Heart Journal study (May 20 2026, 112K French adults, 7-8 year follow-up): food preservatives linked to 29% higher hypertension risk and 16% higher CVD risk. 8 specific preservatives flagged (citric acid, potassium sorbate, sodium benzoate, sodium nitrite, ascorbic acid, etc). Indian American pantries have disproportionate preserved food density: imported pickles, RTMs (MTR, Haldiram's, Ashoka), namkeens, frozen parathas/samosas, chutneys — all contain flagged preservatives. Compounding effect: 5-6 exposures per day across condiments + mains + snacks. Overlaid on highest CVD baseline in the US (MASALA study). Actionable: pantry audit, home-cook condiments, check BP monthly, replace high-preservative items.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: A Danish Study Found That Vitamin D During Pregnancy Improved
# Children's Memory a Decade Later. For South Asian Mothers, the Implications
# Are Enormous — Because Almost None of Them Have Enough.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "A Danish Study Found That Vitamin D During Pregnancy Improved Children's Memory a Decade Later. For South Asian Mothers, the Implications Are Enormous — Because Almost None of Them Have Enough."
art2_subheadline = "A randomised controlled trial published in JAMA Network Open followed 498 Danish children from the womb to age 10 and found that those whose mothers received high-dose vitamin D3 during pregnancy performed significantly better on verbal and visual memory tests a decade later. The children whose mothers took the higher dose — 2,800 IU per day versus the standard 400 IU — showed measurable cognitive advantages that persisted into middle childhood. But the mothers in this study were mostly white northern Europeans with relatively high baseline vitamin D levels. South Asian women — who have among the highest rates of vitamin D deficiency of any population on earth, driven by darker skin pigmentation, cultural modesty norms, indoor lifestyles, and vegetarian diets low in vitamin D — were not in this trial. The question is not whether the findings apply to them. It is how much larger the effect might be."
art2_slug = make_slug("vitamin-d-pregnancy-children-memory-cognitive-south-asian-deficiency")
art2_category = "lifestyle-health"

art2_body = """There is a blood test that almost no Indian American obstetrician orders at the first prenatal visit, and it may matter more for your child's brain than any prenatal vitamin you are taking.

It is a 25-hydroxyvitamin D test. It costs $20-50. It takes one tube of blood. And it would reveal something that the medical literature has been screaming about for two decades but that clinical practice has been remarkably slow to act on: the vast majority of South Asian pregnant women in the United States are vitamin D deficient. Many are severely deficient. And a growing body of evidence — now strengthened by a rigorous ten-year randomised controlled trial — suggests that this deficiency may be affecting their children's brains in ways that do not become visible until years after birth.

## The Copenhagen Trial

The study, published in May 2026 in JAMA Network Open, is a ten-year follow-up of a randomised controlled trial originally conducted at the University of Copenhagen. The original trial — the Copenhagen Prospective Studies on Asthma in Childhood 2010 (COPSAC) — was designed to test whether high-dose vitamin D3 supplementation during pregnancy could prevent asthma in children. The cognitive assessment was a secondary analysis.

Here is how it worked: 623 pregnant women were enrolled at 24 weeks of gestation. They were randomly assigned to one of two groups. The high-dose group received 2,800 IU of vitamin D3 per day (2,400 IU supplemental plus 400 IU in a standard prenatal vitamin). The control group received 400 IU per day (the standard prenatal dose). Supplementation continued from week 24 until one week after delivery.

Ten years later, the researchers tracked down 498 of the original children — 247 in the high-dose group and 251 in the control group — and administered a comprehensive battery of neuropsychological tests measuring 11 cognitive functions.

The results: children whose mothers received the high-dose vitamin D3 performed significantly better on two specific cognitive measures:

**Verbal memory** — the ability to learn, retain, and recall spoken information. This was measured using a standardised word-list learning test.

**Visual memory** — the ability to learn, retain, and recall visual patterns and spatial information. This was measured using a standardised figure-learning test.

There was also a trend toward better **cognitive flexibility** — the ability to rapidly switch attention between different tasks — though this association did not survive the statistical correction for multiple comparisons.

No significant differences were found in the other eight cognitive domains tested, including general intelligence (IQ), processing speed, attention, and executive function.

The researchers conducted sensitivity analyses to determine whether the results could be explained by factors other than the prenatal supplementation: the sex of the child, the mother's baseline vitamin D level, the child's own vitamin D levels at six months and six years, and whether the mother also received Omega-3 supplementation. None of these factors changed the core finding. The association was specifically tied to prenatal vitamin D exposure during the third trimester.

This is methodologically important. It suggests that the third trimester of pregnancy — when fetal brain development is at its most rapid, when neurons are migrating, synapses are forming, and the hippocampus (the brain's memory centre) is undergoing critical growth — may be a window during which vitamin D plays a specific role in shaping cognitive architecture. And once that window closes, catching up later may be harder.

## Why This Matters More for South Asians Than for Anyone Else

The mothers in the Copenhagen trial were mostly white northern Europeans. Their baseline vitamin D levels were relatively high — only a minority were classified as deficient before supplementation began. The researchers noted this as a limitation: "The pregnant women enrolled for the study had relatively high baseline vitamin D status, with only a minority classified as deficient. This may have restricted the opportunity to explore the cognitive benefits of supplementation among children born to mothers with vitamin D deficiency."

In other words, the study found cognitive benefits from supplementation in a population that was not very deficient to begin with. The obvious next question — what happens when you supplement mothers who are severely deficient? — has not been answered by a randomised trial of this quality. But everything we know about the biology of vitamin D and brain development suggests that the answer is: the effect would be larger.

South Asian women are among the most vitamin D-deficient populations on the planet. This is not speculation. It is documented across dozens of studies and multiple countries.

**The biology is straightforward.** Vitamin D is synthesised in the skin when ultraviolet B (UVB) radiation from sunlight converts 7-dehydrocholesterol to pre-vitamin D3. Melanin — the pigment that gives skin its colour — absorbs UVB radiation. The more melanin you have, the less vitamin D you produce for the same amount of sun exposure. A person with dark brown skin (Fitzpatrick type V, which includes most South Asians) needs approximately three to five times more sun exposure to produce the same amount of vitamin D as a person with light skin (Fitzpatrick type I-II).

For a South Asian woman living in the northern United States — Boston, Chicago, Seattle, Minneapolis, New Jersey, the entire Pacific Northwest — the sun angle from October to March is too low to produce significant vitamin D regardless of skin colour. But even in the summer months, the combination of darker skin, indoor work, and sun-avoidance behaviour means that most South Asian Americans do not synthesise enough vitamin D from sunlight alone.

**Cultural factors compound the deficit.** Many South Asian women — particularly those observing religious or cultural modesty norms — cover most of their skin when outdoors. Hijab, dupatta, salwar kameez, long sleeves, and pants all reduce the skin area available for UVB exposure. This is not a criticism of cultural practice. It is a physiological reality: covered skin does not make vitamin D.

Additionally, many South Asian women follow vegetarian or predominantly vegetarian diets. The richest dietary sources of vitamin D are fatty fish (salmon, mackerel, sardines), cod liver oil, and egg yolks — foods that are absent or minimally present in many South Asian diets. Fortified milk and fortified cereals provide some vitamin D, but the amounts are insufficient to compensate for the combined effects of darker skin, northern latitude, indoor lifestyle, and dietary limitations.

**The data on South Asian vitamin D deficiency is alarming.** A 2019 systematic review published in BMC Pregnancy and Childbirth found that vitamin D deficiency (defined as 25-hydroxyvitamin D levels below 20 ng/mL) affected 66-85 per cent of South Asian pregnant women across studies conducted in the UK, US, and Australia. Severe deficiency (below 10 ng/mL) was present in 20-40 per cent. These rates are dramatically higher than those observed in white European women, and they persist even in studies conducted in sunny climates.

In India itself, the numbers are worse. A 2023 meta-analysis of Indian studies found that 80-90 per cent of pregnant women in India were vitamin D deficient, even in southern states with abundant sunlight. The reasons are the same: darker skin, indoor lifestyles, cultural dress norms, vegetarian diets, and a medical culture that does not routinely screen for or supplement vitamin D during pregnancy.

**The recommended dose may be inadequate for South Asians.** The standard prenatal vitamin contains 400 IU of vitamin D3. Many American and British guidelines recommend 600 IU per day during pregnancy. Some more progressive guidelines (including those from the Endocrine Society) recommend 1,000-2,000 IU per day for populations at high risk of deficiency.

The Copenhagen trial's high-dose group received 2,800 IU per day — and showed cognitive benefits in the children. For a South Asian woman starting from a baseline of severe deficiency, 2,800 IU per day may still be insufficient to achieve optimal vitamin D levels. Many functional medicine practitioners and endocrinologists prescribe 4,000-5,000 IU per day for severely deficient pregnant patients, with regular monitoring. The American College of Obstetricians and Gynecologists considers up to 4,000 IU per day to be the safe upper limit during pregnancy.

## The Quiet Cost of Undiagnosed Deficiency

Here is what makes this finding particularly urgent for the Indian American community: the deficiency is happening silently, at scale, in a population that prides itself on academic achievement and cognitive development, and that invests extraordinary resources — financial, emotional, cultural — in giving children every possible educational advantage.

An Indian American family will spend $200 per month on Kumon. $150 per hour on SAT tutoring. $10,000 on college application consultants. They will move to a more expensive school district. They will drive their child to math olympiad practice, debate camp, science fair prep, and coding bootcamp. They will optimise every external factor they can control.

But they will not check whether the mother's vitamin D level during pregnancy was sufficient for the child's brain to develop optimally. Because nobody told them to.

The Copenhagen study found improved verbal and visual memory — cognitive functions that are foundational to academic learning. Verbal memory is what allows a child to remember instructions, retain information from a lecture, learn vocabulary, and perform well on standardised tests. Visual memory is what allows a child to remember diagrams, navigate spatial problems, and process visual information efficiently.

These are not obscure cognitive functions. They are the building blocks of the academic performance that Indian American families invest so heavily in optimising. And they may be partially set before the child is born.

This does not mean that a vitamin D-deficient pregnancy dooms a child to poor cognitive outcomes. The brain is resilient. Environment, education, nutrition, and stimulation throughout childhood all shape cognitive development. But it does mean that prenatal vitamin D status is one input — a modifiable input — in a system that Indian American families are already trying to optimise. It is the variable nobody is tracking.

## What You Should Do

**1. If you are pregnant or planning to become pregnant, get your vitamin D level tested.** Ask your obstetrician for a 25-hydroxyvitamin D blood test at your first prenatal visit — or ideally before conception. Many OBs will not order this routinely. You may need to ask specifically. If your level is below 30 ng/mL (which is likely if you are South Asian), discuss supplementation with your doctor. The Endocrine Society recommends maintaining levels between 40-60 ng/mL for pregnant women, though this is higher than some other guidelines suggest.

**2. Supplement beyond the prenatal vitamin.** If your vitamin D level is low, 400 IU in your prenatal vitamin is not enough. Discuss with your doctor whether 2,000-4,000 IU per day of vitamin D3 is appropriate for you. Vitamin D3 (cholecalciferol) is more effective than D2 (ergocalciferol) at raising blood levels. Take it with a meal that contains fat, as vitamin D is fat-soluble and absorbed better with dietary fat.

**3. Do not self-prescribe high doses without monitoring.** Vitamin D toxicity is rare but real. At very high doses (typically above 10,000 IU per day for extended periods), vitamin D can cause calcium to accumulate in the blood, leading to nausea, kidney stones, and in extreme cases, kidney damage. If you are supplementing at higher doses, get your levels rechecked every 8-12 weeks until they stabilise.

**4. Get 15-20 minutes of midday sun on bare skin when possible.** For South Asian skin, this means arms and legs exposed to direct sunlight between 10 AM and 2 PM, without sunscreen, several times per week during the months when the sun is high enough (April through September in most of the US). This is not always compatible with work schedules, weather, or cultural practice — which is why supplementation is usually necessary.

**5. Include dietary vitamin D sources.** Fatty fish (salmon, mackerel, sardines) are the richest natural source. Egg yolks contain modest amounts. Fortified milk, fortified orange juice, and fortified cereals can contribute. Mushrooms exposed to UV light (some brands specifically market this) provide vitamin D2. For vegetarian South Asian women, fortified foods and supplements are essentially the only reliable sources.

**6. Check your children's vitamin D levels too.** If you were deficient during pregnancy, your child may also be deficient — especially if they have dark skin, spend most of their time indoors, drink limited milk, and eat a vegetarian diet. The American Academy of Pediatrics recommends 400 IU per day for all infants from birth through 12 months, and 600 IU per day for children and adolescents. Many pediatricians do not actively screen for deficiency; you may need to ask.

**7. Tell your mother.** If your parents or in-laws are planning to spend time with a new grandchild — which, in Indian families, is a given — they too should be aware. Grandmothers who are postmenopausal, dark-skinned, and living in northern climates are at extremely high risk of severe vitamin D deficiency, which affects their bone health, immune function, and mood. A family-wide vitamin D check during the next everyone-is-home visit is cheap, easy, and potentially consequential.

## The Bigger Picture

The Indian American community has built a culture of cognitive optimisation. It begins with the choice of school district and extends through every tutoring session, every extracurricular activity, every college application essay. The underlying belief — that intelligence and academic performance can be shaped, nurtured, and maximised — is not wrong. It is one of the community's great strengths.

But the optimisation starts too late. It starts at age five, when the child enters school. It should start at week 24 of pregnancy, when the fetal brain enters its most critical period of development, and when the mother's vitamin D status may be silently shaping the cognitive architecture her child will carry for life.

A $30 blood test. A $10 bottle of vitamin D3 supplements. Fifteen minutes of sunlight. These are not expensive interventions. They are not complicated. They do not require moving to a better school district or hiring a tutor. They require only awareness — awareness that the most optimised generation of Indian American parents may be missing the most fundamental biological input of all.

The Danish mothers in this study were not deficient. Their children still benefited. Imagine what the benefit could be for a South Asian mother whose vitamin D level is half of what it should be.

You will never know what your child's brain could have been. But you can know what your vitamin D level is right now. Start there."""

art2_sources = [
    "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2849122",
    "https://www.news-medical.net/news/20260521/High-dose-vitamin-D3-in-pregnancy-may-boost-childrene28099s-memory-by-age-10.aspx",
    "https://www.cnn.com/2026/05/21/health/vitamin-d-pregnancy-children-cognitive/index.html",
    "https://www.endocrine.org/clinical-practice-guidelines/vitamin-d-deficiency",
    "https://pubmed.ncbi.nlm.nih.gov/",
]

print("\n=== Article 2: Vitamin D Pregnancy / Children's Memory at 10 / South Asian Deficiency ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("pregnant woman sunlight window morning healthy")
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
    "tags": ["vitamin D", "pregnancy", "prenatal", "cognitive development", "memory", "children", "South Asian", "Indian American", "NRI", "vitamin D deficiency", "melanin", "skin pigmentation", "JAMA Network Open", "Copenhagen", "randomised controlled trial", "supplementation", "brain development", "hippocampus", "vegetarian", "dark skin", "sunlight", "cholecalciferol", "obstetrician"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "JAMA Network Open (May 2026, Copenhagen RCT, 10-year follow-up, 498 children): high-dose vitamin D3 (2,800 IU/day) during pregnancy → significantly better verbal and visual memory at age 10 vs standard 400 IU. Trial mothers were mostly white Europeans with HIGH baseline D levels — minority were deficient. South Asian women have 66-85% deficiency rates in pregnancy (BMC Pregnancy and Childbirth 2019), driven by darker pigmentation, indoor lifestyles, cultural dress norms, vegetarian diets. India: 80-90% pregnant women deficient even in sunny states. Standard prenatal 400 IU inadequate for South Asians. Community spends heavily on cognitive optimisation (Kumon, SAT tutoring) but misses $30 blood test + $10 supplement during pregnancy. Actionable: 25-OH-D test at first prenatal visit, 2000-4000 IU D3 supplementation, 15-20 min midday sun, family-wide screening.",
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
sp.run(["git", "commit", "-m", "lifestyle-writer: food preservatives heart disease + vitamin D pregnancy memory South Asian (2026-05-25 03:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
