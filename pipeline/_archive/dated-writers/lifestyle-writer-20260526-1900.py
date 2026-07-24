#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-26 19:00 PDT run
2 articles:
  1. 2026 ACC/AHA Cholesterol Guidelines — new Lp(a) testing recommendation
     for all adults, LDL testing starting at age 10, lower LDL targets (<55 for
     high-risk). South Asians have 25% prevalence of elevated Lp(a) (>50 mg/dL),
     469 million South Asians worldwide with elevated Lp(a), MI nearly 10 years
     earlier than Europeans, 2-fold higher ASCVD risk. Lp(a) is 80-90% genetically
     determined — diet and exercise CANNOT change it. New drugs in pipeline
     (pelacarsen, olpasiran, lepodisiran) can reduce Lp(a) by 65-98%.
     NRI angle: Every Indian American should get Lp(a) tested — most have never
     heard of it. 1 in 4 South Asians has elevated Lp(a). The "healthy cholesterol"
     panel your doctor orders doesn't include it. You need to ask. Your parents
     in India need to ask. The 2018 guidelines already flagged South Asian
     ancestry as a "risk enhancer" — now 2026 guidelines recommend universal Lp(a)
     screening. Statins don't lower Lp(a) but they DO lower the LDL that rides
     alongside it. The PREVENT calculator now estimates 30-year risk from age 30.

  2. JAMA Network Open (May 2026): 38,283 women from Nurses' Health Study II,
     12-year follow-up surrounding menopause. 11 dietary patterns compared.
     Planetary Health Diet (plant-forward) had lowest obesity risk (HR 0.46 — 54%
     reduction). Low-insulinemic diet had largest reduction in weight gain
     (-0.28 kg/year). Foods linked to MOST weight gain: processed meats, sodium,
     potatoes, French fries. Foods linked to LEAST weight gain: nuts, legumes,
     whole grains, fruits, vegetables.
     NRI angle: The traditional Indian thali IS the planetary health diet — dal
     (legumes), sabzi (vegetables), roti (whole grain), raita (fermented dairy),
     chutney (herbs/spices), with minimal processed meat. Indian women face
     menopause earlier (average 46-47 vs 51 in Western populations) and have
     higher diabetes risk. The immigration dietary shift from thali to processed
     American food tracks the weight gain pattern the study identifies. The
     solution is not a new diet plan — it's the old one.
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
for check_term in ["cholesterol guidelines lpa lipoprotein", "acc aha cholesterol 2026", "lpa south asian", "menopause planetary health diet", "menopause weight gain nurses health", "planetary health diet obesity menopause"]:
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
# ARTICLE 1: The Cholesterol Number Your Doctor Never Checks
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "One in Four South Asians Has a Genetic Cholesterol Marker That Doubles Heart Attack Risk. The Standard Lipid Panel Does Not Test for It. New 2026 Guidelines Say Every Adult Should Be Tested Once. Most Indian Americans Have Never Heard of It."
art1_subheadline = "The 2026 ACC/AHA dyslipidemia guidelines — issued in March 2026 by the American Heart Association, the American College of Cardiology, and nine other professional organizations — recommend for the first time that every adult receive a one-time blood test for lipoprotein(a), or Lp(a), a genetically determined cholesterol particle that is 80 to 90 percent inherited and cannot be reduced through diet, exercise, or lifestyle changes. Approximately 25 percent of South Asians have elevated Lp(a) levels above 50 mg/dL, compared with 20 percent of White and 10 percent of East Asian individuals. Elevated Lp(a) in South Asians increases the risk of myocardial infarction by 2.14-fold, contributes to MI onset nearly 10 years earlier than in European populations, and may explain a significant portion of the cardiovascular disparity that traditional risk factors — diabetes, hypertension, LDL cholesterol, obesity — do not fully account for. Globally, an estimated 469 million South Asians carry elevated Lp(a), representing one-third of the world's total elevated Lp(a) burden. The guidelines also recommend LDL cholesterol testing starting at age 10, set a new LDL target of 55 mg/dL or below for very high-risk individuals, and introduce the PREVENT risk calculator for 30-year cardiovascular risk estimation from age 30. Three drugs currently in clinical trials — pelacarsen, olpasiran, and lepodisiran — can reduce Lp(a) levels by 65 to 98 percent. Until they are approved, knowing your Lp(a) level changes your entire risk calculus."
art1_slug = make_slug("lipoprotein-a-lpa-south-asian-heart-attack-cholesterol-guidelines-2026")
art1_category = "lifestyle-health"

art1_body = """Your last annual physical included a lipid panel. The results showed four numbers: total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides. Your doctor reviewed them, possibly adjusted your statin dose, and sent you home.

There is a fifth number that was not on that panel. It is the single strongest genetic risk factor for heart attack in South Asians. It is present in one out of every four people of Indian, Pakistani, Bangladeshi, Sri Lankan, or Nepali descent. It cannot be lowered by diet, exercise, weight loss, or any currently approved medication. And unless you specifically ask for it, your doctor will almost certainly never test you for it.

It is called lipoprotein(a), written as Lp(a) and pronounced "L-P-little-a." And in March 2026, for the first time, the American Heart Association and the American College of Cardiology recommended that every adult in the United States be tested for it at least once in their lifetime.

## What Lp(a) Is

Lp(a) is a cholesterol-carrying particle in the blood. It is structurally similar to LDL — the "bad cholesterol" that everyone knows about — but with one critical addition: a protein called apolipoprotein(a), or Apo(a), that is covalently bonded to the ApoB100 core of the LDL particle.

This additional protein changes everything about how the particle behaves. LDL delivers cholesterol to cells. Lp(a) delivers cholesterol to cells AND promotes inflammation, AND carries oxidized phospholipids that damage arterial walls, AND has a structural similarity to plasminogen (the protein that dissolves blood clots) without plasminogen's clot-dissolving function. Lp(a) essentially mimics the body's clot-dissolving system while doing the opposite: it interferes with clot breakdown and promotes clot formation.

The result is a particle that is simultaneously atherogenic (builds plaque), pro-inflammatory (damages arteries), and pro-thrombotic (promotes clots). It is, in cardiovascular terms, a triple threat.

## Why South Asians Are Disproportionately Affected

Lp(a) levels are 80 to 90 percent genetically determined. They are set by the LPA gene, which controls the size and production rate of the Apo(a) protein. Unlike LDL, which responds to diet, exercise, and medication, Lp(a) levels are largely fixed from birth. You cannot lower your Lp(a) by running marathons, eating vegetables, or losing weight.

The global distribution of elevated Lp(a) — defined as levels above 50 mg/dL — is not uniform across populations. According to a comprehensive review published in the Journal of the American Heart Association:

**South Asians: approximately 25 percent have elevated Lp(a)** — translating to an estimated 469 million people worldwide, or one-third of the global burden of elevated Lp(a).

**African-descent populations: approximately 30 percent** have elevated Lp(a).

**White/European populations: approximately 20 percent.**

**East Asian populations: approximately 10 percent.**

For South Asians, this genetic burden compounds an already elevated cardiovascular risk. Multiple studies across four decades have consistently shown that South Asians have approximately twice the risk of coronary heart disease compared with White populations, even after adjusting for traditional risk factors. The UK Biobank analysis of 501,472 participants found a hazard ratio of 2.03 for atherosclerotic cardiovascular events in South Asians versus White individuals — and this elevated risk persisted even after correcting for diabetes, hypertension, and adiposity.

South Asians also experience heart attacks nearly 10 years earlier than Europeans. A 40-year-old Indian American man is at the cardiovascular risk level of a 50-year-old White American man. The 2018 cholesterol guidelines already recognised this: they explicitly listed South Asian ancestry as a "risk enhancer" for cardiovascular disease. The 2026 guidelines go further.

The INTERHEART study confirmed that elevated Lp(a) increased the risk of myocardial infarction by 2.14-fold in South Asians, compared with a 1.3 to 1.8-fold increase in other ethnic groups. The effect is larger in this population.

## What the 2026 Guidelines Actually Say

The 2026 ACC/AHA dyslipidemia guidelines were issued in March 2026 by 11 professional organisations and represent the first comprehensive update since 2018. Here are the five changes that matter most for Indian Americans:

**1. Universal Lp(a) testing.** Every adult should receive a one-time blood test for Lp(a). This is the first time the AHA/ACC have recommended universal screening for this biomarker. An Lp(a) level above 125 nmol/L (approximately 50 mg/dL) indicates higher cardiovascular risk. If you have a first-degree relative with elevated Lp(a), testing is especially urgent.

**2. LDL testing starting at age 10.** The guidelines recommend having a child's LDL levels checked at around age 10, primarily to identify familial hypercholesterolemia — a genetic condition causing very high cholesterol from birth. Only 11 percent of US children aged 9 to 21 are currently screened for lipid disorders.

**3. Lower LDL targets.** Very high-risk individuals — those who have had a heart attack or stroke plus additional risk factors like diabetes or hypertension — should now target LDL below 55 mg/dL, down from 70 mg/dL in the 2018 guidelines. Most people should aim for LDL below 100 mg/dL.

**4. 30-year risk estimation.** The new PREVENT risk calculator estimates cardiovascular risk over 30 years, not just 10 years. It should be used starting at age 30. This is important for young Indian Americans who may have low 10-year risk but substantial 30-year risk because of genetic factors, family history, and Lp(a) status.

**5. Expanded medication options.** While statins remain the foundation, the guidelines now more clearly position ezetimibe and PCSK9 inhibitors for patients who cannot achieve their LDL targets with statins alone. This is especially relevant for South Asians, who often have atherogenic dyslipidemia (high triglycerides, low HDL, small dense LDL) that is only partially addressed by statins.

## Why Your Standard Lipid Panel Misses It

The standard lipid panel — the one ordered at every annual physical — measures total cholesterol, LDL, HDL, and triglycerides. It does not measure Lp(a).

This is not an oversight. Lp(a) testing was historically considered unnecessary because there was no approved drug to lower it. The clinical logic was: why test for something you cannot treat? The 2026 guidelines reject this reasoning for two reasons.

First, knowing your Lp(a) status changes your entire cardiovascular risk profile. A South Asian man with "normal" LDL of 95 mg/dL but an Lp(a) of 150 nmol/L has a fundamentally different risk calculus than a South Asian man with the same LDL and an Lp(a) of 20 nmol/L. The first man may benefit from earlier statin initiation, more aggressive LDL lowering, or coronary artery calcium scoring — all decisions that hinge on knowing the Lp(a) level.

Second, three drugs in clinical trials can reduce Lp(a) by 65 to 98 percent:

**Pelacarsen** (Novartis/Ionis) — an antisense oligonucleotide that targets the mRNA encoding Apo(a) in the liver. The HORIZON phase 3 trial enrolled over 8,000 participants and results are expected in 2026. Pelacarsen reduced Lp(a) by approximately 80 percent in phase 2 trials.

**Olpasiran** (Amgen) — a small interfering RNA (siRNA) that also targets Apo(a) mRNA. The OCEAN(a)-Outcomes phase 3 trial is enrolling over 6,000 participants. Olpasiran reduced Lp(a) by up to 98 percent in phase 2 trials.

**Lepodisiran** (Eli Lilly) — another siRNA targeting Lp(a) production. Phase 2 results showed reductions of up to 97 percent.

When these drugs reach the market — likely 2027 or 2028 — the clinical question will shift from "should we test?" to "why didn't we test sooner?" Knowing your baseline Lp(a) now positions you for treatment when it becomes available.

## What Lp(a) Cannot Do — And What Statins Can

Here is the paradox: statins do not lower Lp(a). In some cases, statins may slightly increase Lp(a) levels. But statins are still the primary treatment recommendation for people with elevated Lp(a). Why?

Because the goal is not to lower Lp(a) directly (no approved drug can do this yet). The goal is to reduce the total atherogenic burden — the combined plaque-building potential of all cholesterol-carrying particles in the blood. Lp(a) is one contributor to this burden. LDL is another. If you cannot lower Lp(a), lowering LDL as aggressively as possible reduces the total burden.

Think of it like a highway with two lanes of traffic heading toward an accident (plaque formation). You cannot close the Lp(a) lane yet. But you can dramatically reduce traffic in the LDL lane. The total congestion — the total atherogenic burden — decreases even though one lane remains fully open.

This is why the 2026 guidelines set lower LDL targets for high-risk patients (below 55 mg/dL) and why knowing your Lp(a) status matters even before Lp(a)-lowering drugs are available. If your Lp(a) is elevated, you need your LDL to be lower to compensate.

## The Conversation Your Parents Need to Have

If you are reading this in the Bay Area, New Jersey, Houston, Chicago, or any other Indian American concentration, consider this: your parents — whether they live in the US or in India — have a one-in-four chance of carrying elevated Lp(a). They almost certainly have never been tested for it. Their cardiologist in India may not have ordered the test. Their primary care physician in the US almost certainly did not.

The test costs between $20 and $75 and is increasingly covered by insurance. It requires a simple blood draw and results are available in a few days. It needs to be done only once because Lp(a) levels are genetically fixed and do not change significantly over a lifetime.

If the result is elevated (above 50 mg/dL or 125 nmol/L), the clinical implications are immediate:

**Aggressive LDL lowering.** The LDL target should be set at the lower end of the new guidelines — 55 mg/dL for high-risk patients, below 70 mg/dL for intermediate-risk patients. Statins, ezetimibe, and PCSK9 inhibitors (evolocumab, alirocumab) may be needed in combination.

**Coronary artery calcium scoring.** A CAC scan can determine whether elevated Lp(a) has already resulted in plaque buildup. The 2026 guidelines recommend CAC scoring as a tool for reclassifying risk in intermediate-risk patients.

**Family screening.** Lp(a) is inherited. If one parent has elevated Lp(a), there is an approximately 50 percent chance that each child has inherited it. The guidelines recommend testing first-degree relatives of anyone with elevated levels.

**Monitoring for clinical trials.** As pelacarsen, olpasiran, and lepodisiran approach FDA approval, patients with documented elevated Lp(a) will be the first candidates for treatment. Having a baseline measurement positions you for enrollment in ongoing trials or for prescription access when the drugs are approved.

## The Test That Changes the Numbers

The mortality data tells a consistent story across four decades of US death records: South Asians have a proportionate mortality from coronary artery disease that is 28 to 60 percent higher than White Americans, depending on the decade and study. The UK Biobank shows a 2-fold increase in atherosclerotic events. The INTERHEART study shows a 2.14-fold increase in MI risk from elevated Lp(a) specifically in South Asians.

These are not small effects. These are not effects that can be fully explained by diabetes, diet, or lifestyle. They are partly genetic. And the specific genetic mechanism — elevated Lp(a) in one-quarter of the South Asian population — is now testable, quantifiable, and soon treatable.

The 2026 ACC/AHA guidelines have made the recommendation. Every adult should be tested once. For South Asians, the recommendation is not just reasonable — it is urgent. You have a one-in-four chance of carrying a risk factor that doubles your heart attack risk, that your doctor has never checked, and that three drugs in late-stage clinical trials may soon be able to reduce by 80 to 98 percent.

The test costs less than a dinner out. It takes five minutes of blood draw. The result does not change over your lifetime, so you only need it once. And it may be the single most important number you learn about your own cardiovascular health.

Ask your doctor for an Lp(a) test. Then tell your parents to ask theirs."""

art1_sources = [
    "https://www.ahajournals.org/doi/10.1161/JAHA.124.040361",
    "https://newsroom.heart.org/news/2026-acc-aha-dyslipidemia-guidelines",
    "https://professional.heart.org/en/guidelines-and-statements/prevent-calculator",
    "https://www.uchicagomedicine.org/forefront/heart-and-vascular-articles/new-cholesterol-guidelines-five-takeaways",
    "https://www.drugtopics.com/view/american-college-of-cardiology-american-heart-association-update-guidelines-for-the-management-of-dyslipidemia",
]

print("\n=== Article 1: Lp(a) / South Asian Heart Risk / 2026 Cholesterol Guidelines ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: This is about a medical concept (cholesterol/blood test), not a specific person
# Use Pexels for medical/health imagery
art1_image = fetch_pexels_image("blood test medical laboratory cholesterol heart health")
if not art1_image:
    art1_image = fetch_pexels_image("heart health medical stethoscope red")
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
    "score_total": 93,
    "tags": ["lipoprotein(a)", "Lp(a)", "cholesterol", "heart attack", "myocardial infarction", "South Asian", "Indian American", "NRI", "ACC/AHA", "guidelines", "2026", "LDL", "cardiovascular disease", "ASCVD", "genetic risk", "pelacarsen", "olpasiran", "lepodisiran", "statin", "PREVENT calculator", "coronary artery calcium", "lipid panel", "familial hypercholesterolemia", "UK Biobank", "INTERHEART", "atherogenic dyslipidemia"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "2026 ACC/AHA guidelines recommend universal one-time Lp(a) testing for all adults — first time ever. 25% of South Asians have elevated Lp(a) (>50 mg/dL), 469 million worldwide, one-third of global burden. Lp(a) is 80-90% genetic, CANNOT be lowered by diet or exercise. Elevated Lp(a) increases MI risk 2.14-fold in South Asians (higher than any other ethnic group). South Asians have MI nearly 10 years earlier than Europeans, 2x ASCVD risk even after adjusting for diabetes/hypertension/obesity. Standard lipid panel does NOT include Lp(a) — you must specifically ask. Guidelines also: LDL testing from age 10, LDL target <55 mg/dL for high-risk, PREVENT calculator for 30-year risk from age 30. Three drugs in phase 3 trials (pelacarsen 80%, olpasiran 98%, lepodisiran 97% Lp(a) reduction) — expected 2027-2028. Every Indian American adult should get Lp(a) tested once. $20-75, simple blood draw, result is fixed for life. Tell your parents.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Planetary Health Diet and Menopause
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "A Study of 38,283 Women Found That the Diet Most Effective at Preventing Obesity During Menopause Was Plant-Forward, Rich in Legumes and Whole Grains, and Low in Processed Meat. It Looks Exactly Like a Traditional Indian Thali."
art2_subheadline = "A study published in JAMA Network Open in May 2026, using data from the Nurses' Health Study II — one of the largest and longest-running women's health studies in the world — compared 11 different dietary patterns in 38,283 women over 12 years surrounding menopause. The Planetary Health Diet Index, a plant-forward eating pattern emphasizing whole grains, legumes, nuts, fruits, vegetables, and unsaturated fats while minimizing red and processed meats, had the lowest risk of obesity: a hazard ratio of 0.46, meaning women who adhered most closely to this pattern had a 54 percent lower risk of becoming obese during menopause compared with those who adhered least. The low-insulinemic diet — high in fiber-rich foods that limit blood sugar spikes and low in processed meats, potatoes, and fried foods — showed the largest reduction in annual weight gain: 0.28 fewer kilograms per year. The traditional Indian thali — dal, sabzi, roti, raita, chutney — naturally aligns with both patterns. It is legume-centered, plant-forward, whole-grain based, fiber-rich, and contains minimal processed meat. Indian women, who experience menopause an average of four to five years earlier than Western women and face elevated diabetes risk at lower BMI, may find the most effective menopause weight management strategy in the dietary pattern their grandmothers already followed."
art2_slug = make_slug("menopause-planetary-health-diet-thali-obesity-54-percent-nurses-study")
art2_category = "lifestyle-health"

art2_body = """The average woman gains 0.80 kilograms per year during the 12 years surrounding menopause. Over a decade, that is nearly 10 kilograms — about 22 pounds — of weight that arrives gradually enough to seem inevitable but accumulates relentlessly enough to reshape health outcomes for the remaining decades of life.

This weight gain is not caused by eating more. It is driven by the hormonal and metabolic changes of the menopausal transition: declining estrogen levels that alter fat distribution from hips and thighs to the abdomen, reduced insulin sensitivity, changes in the gut microbiome, and shifts in basal metabolic rate. The body's relationship with food changes even when the food does not.

What does change outcomes, according to a study published in JAMA Network Open in May 2026, is the pattern of what women eat — and one dietary pattern outperformed all others at preventing obesity during this transition. It is called the Planetary Health Diet. And it looks remarkably like what Indian women have been eating for centuries.

## The Study

The research used data from the Nurses' Health Study II, which enrolled 116,429 female registered nurses aged 25 to 42 in 1989 and followed them for three decades. For this analysis, researchers examined 38,283 women over approximately 12 years surrounding their menopause — defined as six years before and six years after the cycle when menstruation ceased for at least one year.

Diet was assessed every four years using validated food frequency questionnaires covering more than 130 food items by specific brand name and portion size. Weight was self-reported biennially.

The researchers compared 11 dietary patterns simultaneously within the same cohort — the first study to do so in the context of menopause. The patterns included:

- Plant-based diet index (PDI) and its healthy and unhealthy variants
- Mediterranean diet (MedDiet)
- DASH diet (Dietary Approaches to Stop Hypertension)
- Planetary Health Diet Index (PHDI) — based on the EAT-Lancet reference diet
- Low-carbohydrate diet (LCD) and its healthy and unhealthy variants
- Empirical dietary inflammatory pattern (EDIP)
- Empirical dietary index for hyperinsulinemia (EDIH)
- Ultra-processed food (UPF) intake

The question was straightforward: over 12 years and 340,122 person-years of follow-up, which dietary pattern was associated with the least weight gain and the lowest risk of developing obesity?

## The Results

Two patterns emerged as the clear leaders.

**The Planetary Health Diet Index (PHDI)** had the lowest risk of obesity: a hazard ratio of 0.46 (95% confidence interval, 0.42 to 0.51). Women in the highest quintile of adherence to this diet had a **54 percent lower risk of becoming obese** during menopause compared with women in the lowest quintile. No other dietary pattern came close to this magnitude of protection.

**The reverse empirical dietary index for hyperinsulinemia (reverse EDIH)** — effectively a low-insulinemic diet — showed the largest reduction in annual weight gain: **0.28 fewer kilograms per year** compared with the lowest-adherence group. Over 12 years, this translates to approximately 3.4 kilograms (7.5 pounds) less weight gain.

For obesity prevention specifically, the PHDI and reverse EDIH were the only two patterns with hazard ratios below 0.55. The Mediterranean diet and DASH performed well but were significantly less protective than the PHDI against obesity.

The food groups driving these results were remarkably consistent:

**Foods associated with the MOST weight gain and highest obesity risk:** red and processed meats, sodium, potatoes (especially French fries and fried potatoes), and ultra-processed foods.

**Foods associated with the LEAST weight gain and lowest obesity risk:** nuts, legumes, whole grains, fruits, vegetables, vegetable protein, and unsaturated fats.

## What the Planetary Health Diet Is

The Planetary Health Diet was developed by the EAT-Lancet Commission in 2019 — a collaboration of 37 scientists from 16 countries tasked with defining a diet that could feed 10 billion people by 2050 while remaining within planetary environmental boundaries. It is not a weight loss diet. It was designed for sustainability. That it also turns out to be the most effective dietary pattern for preventing menopausal obesity is a scientific bonus.

The pattern emphasises:

- **Whole grains** as the primary caloric source
- **Legumes** (beans, lentils, chickpeas) as a major protein source
- **Nuts and seeds** daily
- **Vegetables and fruits** in abundance
- **Unsaturated fats** (olive oil, nut oils, seed oils) over saturated fats
- **Fish and poultry** in moderate amounts
- **Dairy** in moderate amounts
- **Red meat** limited to approximately one serving per week
- **Processed meat** minimised or eliminated
- **Added sugars** limited
- **Starchy vegetables** (potatoes) limited

Read that list again. Now consider what a traditional Indian thali looks like.

## The Thali Is the Planetary Health Diet

A standard North Indian thali: dal (lentils — legumes), roti (whole wheat — whole grains), sabzi (seasonal vegetables — vegetables), raita (yoghurt with cucumber — fermented dairy), achar (pickle — fermented condiment), and a small portion of rice.

A standard South Indian thali: sambar (lentils with vegetables — legumes plus vegetables), rasam (tamarind-spiced broth — plant-based), rice (whole grain when using hand-pounded or brown rice), kootu (vegetable-lentil stew — legumes plus vegetables), poriyal (dry vegetable dish — vegetables), appalam (lentil wafer), curd (fermented dairy), and payasam on special occasions.

A standard Gujarati thali: dal (legumes), rotli (whole wheat), shaak (vegetable — often two different preparations), kachumber (raw salad), kadhi (yoghurt-based curry), rice, and a small sweet.

Every regional thali in India — Punjabi, Bengali, Maharashtrian, Tamil, Kerala, Rajasthani, Odia — follows the same structural pattern:

**Legumes as the protein centerpiece.** Not meat. Dal, sambar, rasam, kadhi, chana, rajma, chole — legumes in every meal, often in multiple preparations. This is the single most important structural alignment with the Planetary Health Diet.

**Whole grains as the caloric base.** Roti, chapati, phulka (whole wheat), bajra roti (pearl millet), jowar roti (sorghum), nachni roti (finger millet), rice. Indian cuisine uses a diversity of whole grains that Western diets do not.

**Vegetables in every meal, often multiple preparations.** A single thali may include a wet sabzi, a dry sabzi, a raw salad (kachumber), and vegetables incorporated into the dal or sambar.

**Fermented dairy in moderation.** Dahi, raita, chaas, lassi — fermented dairy products that provide probiotics alongside calcium and protein.

**Nuts and seeds.** Ground nuts in chutneys, sesame in preparations, peanuts in poha, coconut in South Indian cooking. Not as a separate course, but integrated throughout.

**Minimal red meat.** Even in non-vegetarian Indian households, red meat was traditionally consumed once or twice a week at most. The daily protein came from dal, not goat curry.

**No processed meat.** Traditional Indian cuisine has no category for processed meat. No bacon, no ham, no hot dogs, no deli slices, no sausage. This absence — which Americans might view as a limitation — is precisely the dietary feature the JAMA study identifies as most protective.

**Spices that modulate insulin response.** Turmeric, fenugreek, cinnamon, black pepper, cumin — multiple spices used daily in Indian cooking have documented effects on glucose metabolism and insulin sensitivity. A low-insulinemic diet is, in part, an Indian-spiced diet.

The JAMA study did not set out to validate Indian cuisine. It compared 11 dietary patterns in 38,283 American nurses. But the dietary pattern it identified as most protective against menopausal obesity — plant-forward, legume-centred, whole-grain based, low in processed meat, rich in nuts and vegetables — is structurally identical to what millions of Indian women eat every day. Or rather, what they used to eat.

## The Immigration Disruption

Indian American women face menopausal weight management from a unique and disadvantaged position. Not because of their genetics — though South Asian women do tend to accumulate visceral fat at lower BMI — but because immigration systematically dismantles the very dietary pattern the JAMA study identifies as most protective.

**The legume collapse.** A woman who ate dal twice a day in India may eat it twice a week in America. The protein gap is filled by cheese (pizza, pasta, sandwiches), processed meat (deli sandwiches for the children's school lunches, which become the mother's lunch too), and protein bars and shakes. Legume consumption drops by 60 to 80 percent after immigration, taking with it the most protective element of the Indian dietary pattern.

**The processed meat introduction.** The traditional Indian diet contains zero processed meat. The American diet introduces it through every social channel: school lunches, office catering, birthday parties, barbecues, sporting events, and the convenience of a ham sandwich when there is no time to cook. The JAMA study identifies processed meat as one of the food groups most strongly associated with weight gain during menopause.

**The whole grain to refined grain shift.** Hand-rolled roti from whole wheat atta becomes store-bought naan (refined flour). Brown or hand-pounded rice becomes white rice — or disappears entirely in favour of pasta, white bread, and packaged grain products. Millet rotis (bajra, jowar, ragi) — which require specific flours and cooking techniques — disappear completely.

**The snack transformation.** Home-made chivda, murukku, and poha are replaced by chips, crackers, granola bars, and packaged snacks — ultra-processed foods that the JAMA study associates with the highest weight gain during menopause.

**The cooking time collapse.** The Indian thali requires daily cooking — grinding spices, soaking dal, chopping vegetables, making roti by hand. American work schedules, nuclear family structures (no joint family to share cooking), and the availability of convenient alternatives mean that thali-from-scratch happens less and less frequently. The gap is filled by restaurant food, takeout, and processed meals that do not follow the thali pattern.

The net effect: Indian American women enter menopause having partially or fully abandoned the dietary pattern that a study of 38,283 women identifies as the single most protective against menopausal obesity. They enter it carrying the South Asian genetic predisposition to visceral fat accumulation, insulin resistance, and type 2 diabetes at lower BMI. And they enter it earlier: Indian women experience menopause at an average age of 46 to 47, compared with approximately 51 in Western populations — meaning the metabolic disruption begins four to five years sooner.

## The Low-Insulinemic Advantage

The second-best performing dietary pattern in the JAMA study — the low-insulinemic diet — offers additional insight into why the Indian thali is protective.

A low-insulinemic diet is one that minimises the body's insulin response to food. It is not the same as a low-carbohydrate diet (which performed poorly in this study for menopause weight management). It is about the type of carbohydrate and the overall food matrix.

Foods that produce high insulin responses: refined grains (white bread, white rice, packaged cereals), potatoes (especially fried), sugar-sweetened beverages, processed meats, and highly processed snack foods.

Foods that produce low insulin responses: legumes, whole grains, nuts, non-starchy vegetables, fermented dairy, and foods high in fiber and healthy fats.

The Indian thali is naturally low-insulinemic. Dal has a low glycaemic index because the protein and fiber in lentils slow glucose absorption. Roti made from whole wheat atta has a lower glycaemic response than white bread. The combination of fiber (from vegetables and legumes), fat (from ghee, oil, and nuts), protein (from dal and dairy), and spices (fenugreek and cinnamon both improve insulin sensitivity) in a single thali creates a meal that generates a modest, sustained insulin response rather than a spike.

Compare this with a typical American lunch: a turkey sandwich on white bread with chips and a juice box. Refined grain, processed meat, fried potato, and sugar — every component generates a high insulin response. It is not that the American lunch has more calories (it may not). It is that the insulin response pattern is fundamentally different.

The JAMA study found that women with the most insulinemic diets gained 0.28 more kilograms per year than women with the least insulinemic diets. Over the 12-year menopausal window, that is 3.4 kilograms — approximately 7.5 pounds — of additional weight gain attributable not to how much women ate but to how their bodies responded to what they ate.

## The Practical Return

The most effective menopause weight management strategy identified by a 30-year study of 38,283 women is not a new diet plan, a supplement regimen, or a meal delivery service. It is a dietary pattern that Indian women have practiced for centuries.

The prescription is not complicated:

**Eat dal every day.** Masoor, moong, toor, chana, urad — rotate the lentils, but eat legumes daily. This single practice aligns with the most protective feature of both the Planetary Health Diet and the low-insulinemic diet.

**Make roti from whole wheat atta, or better, from millet.** Bajra roti, jowar roti, ragi roti — these are higher in fiber and micronutrients than wheat roti and have lower glycaemic responses. Indian grocery stores in every major American metro stock these flours.

**Cook sabzi daily.** Seasonal vegetables, minimally processed, cooked with spices. The specific vegetable matters less than the practice of eating vegetables at every meal.

**Use curd and raita.** Fermented dairy provides probiotics, calcium, and protein with a low insulin response. Homemade dahi from whole milk, set daily — the simplest Indian kitchen practice and one of the most nutritionally valuable.

**Eliminate processed meat.** This is the easiest dietary change for Indian American women who grew up in India, because the concept of processed meat is foreign to the cuisine they were raised on. The challenge is the family members — especially children — who have adopted American eating patterns.

**Limit potatoes and fried foods.** Aloo in every sabzi is a North Indian default that the data does not support. Replace aloo gobi with gobi matar. Replace aloo paratha with mooli paratha. Reduce the frequency of fried snacks — samosas, pakoras, puris — to occasional rather than regular.

**Eat nuts daily.** A handful of almonds, walnuts, or peanuts. In Indian cuisine, this is already present: peanut chutney in South India, kaju in Gujarati cooking, badam milk as a tradition. Formalise it as a daily practice.

## The Paradox of Proximity

The most striking aspect of the JAMA Network Open findings, for Indian American women, is the proximity of the solution to the problem. The dietary pattern identified as most protective against menopausal obesity across 11 patterns and 38,283 women is not exotic, not expensive, not difficult to source, and not culturally unfamiliar. It is the dietary pattern of the Indian kitchen.

The problem is not knowledge. Indian American women know how to cook dal. They know how to make roti. They know what a thali looks like. The problem is that immigration — work pressure, nuclear family structure, children's food preferences, social eating norms, and the gravitational pull of American processed food convenience — has systematically eroded the daily practice of the very dietary pattern that the science now validates as most protective.

The JAMA study did not set out to prove that the Indian thali prevents menopausal obesity. But by comparing 11 dietary patterns and finding that the one most closely aligned with traditional Indian eating — plant-forward, legume-centred, whole-grain based, low in processed meat — was the most protective by a wide margin, it arrived at a conclusion that Indian grandmothers would find entirely unsurprising.

The thali was never just a meal. It was a metabolic strategy disguised as lunch."""

art2_sources = [
    "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2849168",
    "https://www.healthline.com/health-news/plant-forward-diets-may-help-with-menopause-weight-gain",
    "https://www.eatingwell.com/the-1-diet-to-manage-menopausal-weight-gain-according-to-science-11980839",
    "https://nypost.com/2026/05/21/health/2-diets-found-to-prevent-menopause-weight-gain/",
]

print("\n=== Article 2: Menopause / Planetary Health Diet / Indian Thali ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: Indian thali — traditional Indian meal plate with dal, roti, sabzi
art2_image = fetch_pexels_image("Indian thali traditional meal plate dal roti")
if not art2_image:
    art2_image = fetch_pexels_image("Indian food dal lentil curry vegetable rice plate")
if not art2_image:
    art2_image = fetch_pexels_image("healthy plant based meal legumes vegetables whole grains")
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
    "tags": ["menopause", "weight gain", "obesity", "planetary health diet", "Indian thali", "dal", "legumes", "whole grains", "Nurses Health Study", "JAMA Network Open", "low insulinemic diet", "plant-based", "processed meat", "South Asian", "Indian American", "NRI", "women's health", "perimenopause", "insulin resistance", "visceral fat", "millet", "roti", "sabzi", "fermented dairy", "ragi", "bajra", "jowar", "diabetes risk"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "JAMA Network Open (May 2026): 38,283 women from Nurses' Health Study II, 12-year follow-up surrounding menopause, 11 dietary patterns compared. Planetary Health Diet had lowest obesity risk (HR 0.46 — 54% reduction). Low-insulinemic diet had largest reduction in weight gain (-0.28 kg/year). NRI angle: The traditional Indian thali IS the planetary health diet — dal (legumes), sabzi (vegetables), roti (whole grain), raita (fermented dairy), nuts, spices, minimal processed meat. Indian women face menopause 4-5 years earlier (average 46-47 vs 51 Western), have higher diabetes risk at lower BMI, and accumulate visceral fat more readily. Immigration systematically dismantles the thali: legume consumption drops 60-80%, processed meat introduced, whole grains → refined grains, cooking from scratch replaced by processed convenience. The net effect: Indian American women abandon the most protective dietary pattern precisely when they need it most. The solution is return, not discovery — the Indian grandmother's kitchen was always the evidence-based intervention.",
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
commit_msg = "lifestyle: Lp(a) cholesterol guidelines + menopause planetary health diet thali (2026-05-26 19:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
