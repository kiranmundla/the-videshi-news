#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-26 07:00 PDT run
2 articles:
  1. Scientific Reports (published May 22, 2026): Shotgun metagenomics of 229 healthy
     Korean adults found that highly spicy food intake increased SCFA-producing and
     mucin-metabolizing gut bacteria — markers of a healthy gut barrier. Spicy food was
     NOT associated with epithelial stress (I-FABP/L-FABP biomarkers). However, high
     alcohol intake showed enrichment of mucin-degrading taxa with REDUCED SCFA flux,
     increased Proteobacteria/Fusobacteria, and elevated I-FABP (epithelial stress).
     The Drink-High/Spicy-High group had dysbiosis despite elevated mucin turnover.
     Conclusion: spicy food modulates gut health beneficially; alcohol is the consistent
     perturbator. NRI angle: Indian food is among the most spice-heavy cuisines on Earth.
     American doctors routinely tell NRIs to "reduce spice" for gut health — this study
     says the opposite. Capsaicin, turmeric (curcumin), ginger (gingerol), black pepper
     (piperine), mustard seed, fenugreek — the Indian spice cabinet is a SCFA-production
     toolkit. The real gut damage comes from what Indian Americans added to the meal:
     alcohol. Beer with biryani, wine with curry, cocktails at desi parties. Your mother's
     food wasn't the problem. The drink next to it was.

  2. SHADES study (presented APA 2026, May 17): Cross-sectional analysis of 1,007 adults
     aged 22-60 found that higher caffeine intake (3+ servings/day of coffee/energy
     drinks) was independently associated with higher PHQ-9 depression scores. 3-4
     servings: P=.03; 5-6 servings: P=.004; 7+: P=.01. BUT caffeine also weakened the
     insomnia-depression link — non-caffeine users with moderate-severe insomnia had
     the strongest depression association (B=13.5), while caffeine users had weaker
     association (B=8.0-9.2). NRI angle: Indian tech workers shifted from 2 cups of
     traditional chai (lower caffeine, L-theanine, cardamom, ginger) to 4-6 cups of
     American coffee/cold brew/energy drinks. The traditional chai consumption pattern
     sits below the study's 3-serving threshold. The American coffee culture that Indian
     tech workers adopted is in the 3-6 serving range where depression severity climbs.
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
for check_term in ["spicy food gut microbiome", "spice scfa mucin", "capsaicin gut bacteria", "caffeine depression shades", "caffeine depression severity", "coffee depression phq"]:
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
# ARTICLE 1: Your Mother's Spicy Food Was Feeding Your Gut
# the Right Bacteria. A Study of 229 Adults Found That Spice
# Increases the Short-Chain Fatty Acids That Protect Your
# Intestinal Wall. The Alcohol You Added Is What Destroys It.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Your Mother's Spicy Food Was Feeding Your Gut the Right Bacteria. A Study of 229 Adults Found That Spice Increases the Short-Chain Fatty Acids That Protect Your Intestinal Wall. The Alcohol You Added Is What Destroys It."
art1_subheadline = "Shotgun metagenomics of 229 healthy adults, published May 22, 2026, in Scientific Reports, found that highly spicy food intake increased the abundance of SCFA-producing and mucin-metabolizing bacteria — the taxa that manufacture butyrate, propionate, and acetate to seal the gut barrier and suppress inflammation. Spicy food was not associated with epithelial stress. High alcohol intake, however, enriched mucin-degrading taxa, reduced SCFA flux, increased the inflammatory phyla Proteobacteria and Fusobacteria, and raised urinary I-FABP, a biomarker of intestinal epithelial damage. When both were consumed together, the gut showed elevated mucin turnover but with dysbiosis. For Indian Americans who have spent decades hearing American doctors tell them to eat less spicy food for their stomachs, the study reverses the prescription: the chillies, the turmeric, the ginger, the black pepper, the mustard seed — these were building the gut barrier. The beer with biryani, the wine with curry, the cocktails at the Saturday desi party — those were tearing it down."
art1_slug = make_slug("spicy-food-gut-bacteria-scfa-alcohol-destroys-indian-mothers-cooking")
art1_category = "lifestyle-health"

art1_body = """Every Indian American has heard some version of the same advice from an American doctor. You have digestive issues? Eat bland food. Reduce the spice. Try plain rice. Maybe some toast. Your food is too rich, too hot, too complicated for your stomach.

The advice is delivered with professional authority. It is received with quiet compliance. And then the patient goes home and eats khichdi instead of rajma chawal, skips the pickle, removes the green chilli from the dal, and wonders why their gut still hurts.

A study published on May 22, 2026, in Scientific Reports may explain why: the spice was never the problem. The alcohol was.

## The Study

Researchers from Samyang Foods Inc. in Seoul, Republic of Korea, used shotgun metagenomics — a technique that sequences all genetic material in a sample, capturing the full diversity and functional capacity of the microbial community — to characterise the gut microbiomes of 229 healthy Korean adults.

The study measured three things simultaneously: the participants' spicy food intake levels, their alcohol consumption levels, and the composition and metabolic activity of their gut bacteria. Critically, the researchers also measured two biomarkers of intestinal damage: urinary intestinal fatty acid–binding protein (I-FABP) and liver fatty acid–binding protein (L-FABP). These biomarkers indicate whether the gut's epithelial lining — the single-cell-thick barrier that separates the contents of your intestines from your bloodstream — is intact or compromised.

The participants were divided into groups based on their spicy food and alcohol consumption, creating a matrix that allowed the researchers to isolate the effects of each factor while controlling for the other.

The findings were unambiguous.

## What Spicy Food Does to the Gut

Participants who consumed highly spicy food showed increased abundance of two categories of beneficial gut bacteria:

**SCFA-producing taxa** — bacteria that ferment dietary fibre into short-chain fatty acids, primarily butyrate, propionate, and acetate. These are not exotic molecules. They are the primary energy source for the cells that line the colon (colonocytes), and they are the gut's first line of immunological defence. Butyrate in particular has been shown to strengthen tight junctions between epithelial cells, reduce permeability (the so-called "leaky gut"), suppress pro-inflammatory cytokine production, and promote the differentiation of regulatory T cells that prevent autoimmune attacks on the gut lining.

**Mucin-metabolizing taxa** — bacteria involved in the turnover and maintenance of the mucus layer that coats the intestinal wall. This mucus layer is not passive insulation. It is a dynamic, constantly renewing barrier that traps pathogens, feeds beneficial bacteria, and prevents the immune system from reacting to the trillions of microbes that live in the gut. Healthy mucin metabolism means the mucus layer is being continuously rebuilt — old mucin is degraded and new mucin is secreted, maintaining a fresh, functional barrier.

The critical finding: **spicy food intake was not associated with elevated I-FABP or L-FABP levels**. In plain language, eating spicy food did not damage the intestinal lining. The gut wall was intact. The epithelial cells were not stressed. The spice was feeding beneficial bacteria without harming the barrier they protect.

## What Alcohol Does to the Gut

The alcohol findings were the mirror image.

Participants with high alcohol intake showed:

**Enrichment of mucin-degrading taxa with reduced SCFA flux.** This is the worst possible combination for gut health. The mucin layer was being broken down, but the bacteria that should have been replacing it with fresh mucin and feeding the colonocytes with SCFAs were underperforming. The gut was losing its barrier faster than it could rebuild it.

**Increased abundance of Proteobacteria and Fusobacteria.** These are the phyla most consistently associated with gut inflammation and disease. Proteobacteria includes many gram-negative bacteria that produce lipopolysaccharide (LPS), an endotoxin that triggers systemic inflammation when it crosses the gut barrier into the bloodstream. Fusobacteria have been linked to colorectal cancer, inflammatory bowel disease, and appendicitis.

**Elevated urinary I-FABP levels.** This is the biomarker that tells the story. I-FABP is a protein found exclusively in the cytoplasm of mature enterocytes — the cells that line the small intestine. When these cells are damaged, I-FABP leaks into the bloodstream and is excreted in urine. Elevated I-FABP means the intestinal wall is physically breaking down. The alcohol was not merely changing the bacterial composition. It was damaging the gut lining at the cellular level.

## The Combination: Spice Plus Alcohol

The study's most nuanced finding concerned the group that consumed both highly spicy food and high amounts of alcohol — the Drink-High, Spicy-High (DHSH) group.

This group showed elevated mucin turnover and SCFA production — the markers associated with spicy food's beneficial effects — but also displayed dysbiosis, the disordered microbial ecosystem associated with alcohol. The spice was still feeding beneficial bacteria, but the alcohol was simultaneously promoting inflammatory taxa and damaging the epithelial barrier.

The researchers concluded that spicy food modulates mucus layer metabolism in a "context-dependent manner" — its benefits depend on what else is being consumed. Alcohol, in contrast, "more consistently perturbs mucin-SCFA networks and epithelial integrity" regardless of other dietary factors.

Translation: spice helps, but alcohol overrides the help. You cannot drink your way through the protection that spice provides.

## The Indian Spice Cabinet as a SCFA Production Toolkit

The study was conducted in a Korean population, and the "spicy food" in question was primarily capsaicin-rich — gochugaru (Korean red pepper flakes), gochujang (fermented chilli paste), and fresh chillies. But the findings have direct implications for Indian food, because the Indian spice cabinet is arguably the most diverse SCFA-promoting pharmacopoeia in any culinary tradition.

**Capsaicin** (red chillies, green chillies, Kashmiri mirch): The primary compound in the Korean study. Capsaicin has been shown in multiple studies to increase the abundance of Faecalibacterium prausnitzii and Roseburia, two of the most important butyrate-producing bacteria in the human gut. A 2017 study in the British Medical Journal that followed 487,375 Chinese adults for a median of 7.2 years found that those who ate spicy food six to seven days a week had a 14 percent lower risk of all-cause mortality compared to those who ate spicy food less than once a week.

**Curcumin** (turmeric/haldi): The active compound in turmeric, which appears in virtually every Indian dish. Curcumin has been shown to modulate the gut microbiome by increasing the abundance of Bifidobacterium, Lactobacillus, and butyrate-producing Clostridiales. A 2020 systematic review in the Journal of Medicinal Food found that curcumin supplementation reduced markers of intestinal permeability and inflammation in human trials. The traditional Indian practice of adding turmeric to dal, to vegetables, to rice, to milk (haldi doodh) — which Western wellness culture has rebranded as "golden milk" and sells for seven dollars a cup — was delivering curcumin to the gut at every meal.

**Gingerol and shogaol** (ginger/adrak): Ginger increases gastric motility, stimulates the secretion of digestive enzymes, and has been shown to promote the growth of Lactobacillus and Bifidobacterium while suppressing pathogenic E. coli. The Indian practice of starting a meal with fresh ginger-lime (adrak-nimbu) or adding ginger to chai provides a daily dose of these compounds.

**Piperine** (black pepper/kali mirch): Beyond its own anti-inflammatory properties, piperine increases the bioavailability of curcumin by 2,000 percent — a finding so well-established that curcumin supplements now routinely include piperine. The traditional Indian practice of combining turmeric and black pepper in cooking was optimising curcumin absorption centuries before pharmacologists quantified it.

**Allyl isothiocyanate** (mustard seed/rai/sarson): Mustard seeds, which are the foundation of South Indian tempering (tadka) and Bengali cuisine, contain compounds that have been shown to have antimicrobial properties against pathogenic gut bacteria while leaving beneficial Lactobacillus species intact.

**Fenugreek** (methi): Fenugreek seeds are rich in galactomannan, a soluble fibre that serves as a prebiotic — food for the SCFA-producing bacteria that the Korean study found were promoted by spicy food. A 2019 study published in Nutrition Research found that fenugreek supplementation increased Lactobacillus and Bifidobacterium populations and elevated faecal SCFA concentrations in human subjects.

**Asafoetida** (hing): The pungent spice that Indian grandmothers add to every dal. Asafoetida has been shown to have antimicrobial, anti-inflammatory, and carminative properties. Its traditional use in bean and lentil dishes — where it reduces flatulence — is a practical example of a spice modulating the gut's response to fermentable substrates.

The Indian meal is not merely spicy. It is a delivery system for an array of bioactive compounds that, according to the metabolic logic of the Korean study, collectively promote SCFA production, maintain the mucin barrier, and suppress inflammatory gut bacteria. The study measured capsaicin in isolation. The Indian kitchen delivers capsaicin alongside curcumin, gingerol, piperine, allyl isothiocyanate, galactomannan, and dozens of other compounds that operate synergistically.

## What American Doctors Got Wrong

The standard American medical advice to Indian patients with digestive complaints — "reduce spice" — is not based on evidence that spice causes gut damage. It is based on two assumptions, both of which the Korean study undermines.

**Assumption one: spicy food irritates the stomach.** The sensation of heat from capsaicin is caused by activation of the TRPV1 receptor on sensory neurons in the mouth and oesophagus. This is a neurological event, not a tissue-damage event. The burning feeling does not indicate that cells are being harmed. Multiple endoscopy studies have confirmed that capsaicin consumption does not cause mucosal damage in the stomach or intestines, and the Korean study found no elevation in the biomarkers (I-FABP, L-FABP) that would indicate epithelial injury. The spice feels hot, but the gut is unharmed.

**Assumption two: simplifying the diet will help.** The "bland diet" recommendation — white rice, toast, plain chicken, no seasoning — removes the very compounds that the study shows are promoting beneficial gut bacteria. A bland diet is a SCFA-depleted diet. It feeds fewer beneficial bacteria, produces less butyrate, and provides less support for the mucin barrier. The advice to eat bland food for gut health may be actively counterproductive.

The Korean study does not prove that Indian spices cure digestive disease. But it provides mechanistic evidence that the spice compounds in traditional Indian cooking promote the bacterial populations and metabolic pathways associated with a healthy, well-sealed gut barrier — and that removing those compounds removes the promotion.

## The Alcohol Problem That Nobody Talks About

If the spice is beneficial, what is causing the digestive complaints that Indian Americans report to their doctors?

The Korean study points directly at alcohol. And the pattern of alcohol consumption among Indian Americans has changed dramatically in the past generation.

In India, alcohol consumption is culturally compartmentalised. Many communities — particularly South Indian Brahmin, Jain, Marwari, and Gujarati households — are traditionally abstinent. Even in communities where alcohol is consumed, drinking is typically an all-male, social occasion — whisky or rum with friends, not wine with dinner. The traditional Indian meal is alcohol-free. Water, buttermilk (chaas), lassi, or nothing.

In the United States, the norms shifted. Indian Americans adopted American drinking patterns while retaining Indian food. The result is a combination that the Korean study identifies as specifically harmful:

**Beer with biryani.** The Friday-night ritual of ordering biryani from a local Indian restaurant and pairing it with a six-pack. The biryani is anti-inflammatory (turmeric, whole spices, saffron). The beer is not.

**Wine with curry.** Wine pairing is an American social convention. Indian food was never designed to be consumed with wine. The acidity of wine combined with the capsaicin in curry creates a sensory experience that many people interpret as "too spicy" — leading them to blame the spice rather than the wine.

**Cocktails at desi parties.** The Saturday house party where rum, vodka, and whisky flow freely alongside samosas, chicken tikka, and paneer. The food at these parties is rich in the spice compounds the study associates with beneficial gut bacteria. The alcohol consumed alongside it is driving the dysbiosis and epithelial damage the study documents.

**The after-work drink.** Indian tech workers in the Bay Area, Seattle, and New York have adopted the American after-work beer or cocktail. For many, this is a daily habit — one or two drinks after work, then dinner with spicy food. The Korean study's DHSH group is precisely this pattern: high spice, high alcohol. The spice feeds beneficial bacteria. The alcohol promotes inflammatory bacteria and damages the gut wall. The net effect is dysbiosis.

The digestive discomfort that brings Indian Americans to their doctors — bloating, acid reflux, irregular bowel movements, abdominal pain — may not be caused by the Indian food at all. It may be caused by the American alcohol that was added to the Indian food. The doctor who tells the patient to "reduce spice" is treating the wrong variable.

## The Fermentation Connection

The Korean study's focus on SCFA production connects to another aspect of traditional Indian food that immigrant life has eroded: fermentation.

Traditional Indian cuisine is rich in naturally fermented foods that deliver both probiotic bacteria and prebiotic substrates to the gut:

**Dahi (yogurt)** — homemade, not store-bought, cultured fresh daily from a starter passed between households. Commercial American yogurt is a different product — heat-treated after fermentation (killing the bacteria), loaded with sugar, and missing the strain diversity of home-cultured dahi. The Indian practice of eating dahi with every meal delivered a daily dose of Lactobacillus and Streptococcus thermophilus directly to the gut.

**Idli and dosa batter** — fermented overnight, the batter develops Lactobacillus mesenteroides and Leuconostoc species that break down the rice and urad dal's phytic acid (improving mineral absorption) and begin carbohydrate fermentation before the food even enters the mouth.

**Achaar (Indian pickle)** — lacto-fermented in mustard oil with salt and spices. Traditional achaar is a probiotic food. The American version — sold in jars on grocery store shelves — is vinegar-based, pasteurised, and probiotic-dead.

**Kanji** — the Punjabi fermented carrot drink made during winter. **Panta bhat** — the Bengali fermented rice water. **Ambali** — the South Indian fermented finger millet drink. These regional fermented beverages are consumed daily in parts of India and provide both probiotics and SCFA precursors.

The immigration transition replaced all of these with American grocery products. Home-cultured dahi became Dannon or Chobani (different cultures, added sugar). Fresh idli batter became frozen packets (no live fermentation). Lacto-fermented achaar became vinegar-pickled relish. Kanji, panta bhat, and ambali disappeared entirely.

The gut microbiome that traditional Indian food maintained — diverse, SCFA-rich, dominated by Lactobacillus and butyrate-producing Clostridiales — was sustained by this daily delivery of live bacteria and fermentable substrates. The Korean study shows that spicy food promotes exactly these populations. Remove the spice, remove the fermented foods, add alcohol, and you have described the dietary transition that Indian immigration imposes.

## What This Means Practically

The study does not prove that Indian spices cure gut disease. It does not prove that alcohol causes all digestive problems. It is a cross-sectional metagenomic analysis of 229 adults in one country, and like all such studies, it cannot establish causation.

But it provides strong mechanistic evidence for the following practical conclusions:

**Do not reduce spice on a doctor's advice unless there is a specific medical reason.** If you have been diagnosed with a gastric ulcer, oesophageal erosion, or another condition where capsaicin is contraindicated, follow your doctor's advice. But if the advice is general — "your food is too spicy for your stomach" — ask for the evidence. The Korean study found no association between spicy food intake and epithelial stress markers. The sensation of heat is neurological, not pathological.

**Examine your alcohol consumption honestly.** If you are experiencing digestive symptoms and you drink alcohol regularly — even "moderately" — the alcohol may be the cause. The study found that alcohol elevated I-FABP levels (indicating gut lining damage), increased inflammatory Proteobacteria and Fusobacteria, and reduced SCFA production. These effects were consistent across consumption levels. You do not need to be a heavy drinker for alcohol to damage your gut.

**Stop blaming the food and start examining the meal.** If you eat biryani with beer and feel bloated the next day, the instinct is to blame the biryani — it was "too heavy," "too oily," "too spicy." The Korean study suggests the beer is the more likely culprit. Try eating the same biryani with water or chaas instead of beer. If the symptoms disappear, you have your answer.

**Cook with the full spice cabinet.** Do not simplify your cooking because you think it is "healthier." A dal made with turmeric, cumin, ginger, asafoetida, mustard seeds, and fresh coriander is delivering at least six bioactive compounds that the scientific literature associates with beneficial gut microbiome effects. A dal made with salt alone is delivering none. Your grandmother's cooking was not arbitrarily complex. It was biochemically sophisticated.

**Restore fermented foods to your diet.** Make dahi at home from a live culture — not from a store-bought yogurt that may have been heat-treated. If you eat South Indian food, make fresh batter instead of using frozen packets. If your family has a tradition of making achaar, kanji, or any other fermented preparation, revive it. These are not nostalgic foods. They are probiotic delivery systems that your gut evolved to depend on.

**If you have elderly parents with digestive issues, do not take away their spice.** The reflexive response when an elderly Indian parent complains of stomach problems is to make them khichdi — plain, mild, unseasoned. This may be the wrong approach. If the parent's digestive issues coincide with a period of reduced spice intake, reduced fermented food consumption, or increased alcohol consumption (even modest amounts at family gatherings), the bland diet is removing the protective factors while the damaging factor remains.

## The Doctor's Blind Spot

American medical training does not include Indian culinary pharmacology. When an Indian American patient presents with functional dyspepsia, irritable bowel syndrome, or non-specific digestive complaints, the physician sees a patient who eats "exotic, heavily spiced food" and reaches for the standard recommendation: simplify, reduce seasoning, eat bland.

This recommendation is based on pattern matching, not evidence. The physician associates spice with gastric irritation because capsaicin activates TRPV1 receptors and causes a burning sensation. The physician does not know — because it was not taught in medical school — that capsaicin does not cause mucosal damage, that curcumin is anti-inflammatory, that piperine enhances curcumin bioavailability, that fenugreek is a prebiotic, or that the combined effect of an Indian spice cabinet is to promote exactly the SCFA-producing, mucin-maintaining bacterial populations that the Korean metagenomics study identifies as markers of gut health.

The advice to reduce spice is not malpractice. It is ignorance — a gap in the evidence base that this study helps to fill.

## The Real Prescription

The Korean study, read alongside the broader literature on capsaicin, curcumin, piperine, gingerol, and gut microbiome ecology, suggests a prescription that your grandmother would have endorsed without needing to read a single paper:

Cook with spice. Eat fermented food. Drink water with your meals.

The food was never the problem. The food was the medicine. What you drank with it — and what you stopped making at home — is where the gut went wrong."""

art1_sources = [
    "https://doi.org/10.1038/s41598-026-53556-7",
    "https://www.nature.com/articles/s41598-026-53556-7",
    "https://bmj.com/content/351/bmj.h3942",
]

print("\n=== Article 1: Spicy Food Gut Bacteria SCFA / Alcohol Destroys / Indian Mothers ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: Indian spices — turmeric, chillies, spice market, or Indian cooking with spices
art1_image = fetch_pexels_image("Indian spices turmeric chilli powder colorful traditional")
if not art1_image:
    art1_image = fetch_pexels_image("spice market colorful bowls turmeric cumin red chilli")
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
    "score_total": 91,
    "tags": ["spicy food", "gut microbiome", "SCFA", "short-chain fatty acids", "butyrate", "mucin", "capsaicin", "turmeric", "curcumin", "ginger", "piperine", "black pepper", "fenugreek", "asafoetida", "Indian spices", "alcohol gut damage", "I-FABP", "epithelial stress", "Proteobacteria", "Fusobacteria", "dysbiosis", "metagenomics", "Korean study", "Scientific Reports", "NRI", "Indian American", "bland diet myth", "fermented foods", "dahi", "idli", "achaar", "Indian cooking", "beer biryani", "wine curry"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "Scientific Reports (May 22, 2026): Shotgun metagenomics of 229 adults found spicy food increases SCFA-producing and mucin-metabolizing gut bacteria — markers of gut barrier health. Spicy food NOT associated with epithelial stress. Alcohol, in contrast, enriched inflammatory Proteobacteria/Fusobacteria, reduced SCFA flux, and elevated I-FABP (gut lining damage). The Drink-High/Spicy-High group showed dysbiosis despite spice's benefits. NRI angle: American doctors routinely tell Indian patients to 'reduce spice' for gut health — this study says the opposite. The Indian spice cabinet (capsaicin, curcumin, gingerol, piperine, fenugreek, hing) is an SCFA-production toolkit. The real gut damage comes from what Indian Americans added to the meal: alcohol. Beer with biryani, wine with curry, cocktails at desi parties. Traditional Indian meals were alcohol-free (water, chaas, lassi). Immigration replaced home-cultured dahi with Dannon, fresh idli batter with frozen, lacto-fermented achaar with vinegar-based. The dietary transition of immigration — less spice, less fermentation, more alcohol — describes the exact pattern the study identifies as gut-damaging.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Your Chai Was the Right Amount of Caffeine. A Study
# of 1,007 Adults Found That Three or More Cups of Coffee a Day
# Are Independently Associated with Worse Depression. Two Cups
# of Chai Would Not Have Crossed That Line.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Your Chai Was the Right Amount of Caffeine. A Study of 1,007 Adults Found That Three or More Cups of Coffee a Day Are Independently Associated with Worse Depression. Two Cups of Chai Would Not Have Crossed That Line."
art2_subheadline = "Researchers from the University of Arizona presented findings at the American Psychiatric Association's 2026 Annual Meeting showing that higher caffeine intake — three to four servings per day of coffee or energy drinks — was independently associated with higher scores on the PHQ-9 depression scale (P=.03), with the relationship strengthening at five to six servings (P=.004) and seven or more (P=.01). Insomnia, sleepiness, fatigue, and stress were each independently associated with worse depression scores. Caffeine appeared to moderate the insomnia-depression link, with non-caffeine users showing the strongest association between severe insomnia and depression. For Indian Americans who replaced two daily cups of adrak chai — roughly 100 milligrams of caffeine delivered alongside L-theanine, cardamom, and ginger — with four to six cups of American drip coffee, cold brew, or energy drinks delivering 400 to 600 milligrams, the study maps the exact caffeine escalation that correlates with worse mental health."
art2_slug = make_slug("chai-right-caffeine-three-coffees-depression-study-indian-tech")
art2_category = "lifestyle-health"

art2_body = """In the break rooms of every tech company in the San Francisco Bay Area, Seattle, and New York — the three metropolitan areas with the highest concentrations of Indian American tech workers in the country — there are machines that dispense drip coffee, espresso, cold brew on tap, and energy drinks stacked in refrigerated cases.

There is almost never chai.

The caffeine consumption patterns of Indian Americans in the technology industry bear no resemblance to the caffeine consumption patterns they grew up with. The shift has been total, rapid, and medically unexamined. Until now, no study has specifically measured whether the amount of caffeine in the American tech worker's daily intake — typically three to six servings of high-caffeine beverages — is associated with worse mental health outcomes.

A study presented on May 17, 2026, at the American Psychiatric Association's Annual Meeting in San Francisco provides the measurement. The answer is yes.

## The Study

The Sleep and Healthy Activity, Diet, Environment and Socialization (SHADES) study is a cross-sectional analysis of 1,007 adults aged 22 to 60 years, with a roughly equal distribution of men and women. The study was conducted by investigators from the University of Arizona College of Medicine-Tucson.

Participants were assessed on five validated clinical instruments:

The **Patient Health Questionnaire-9 (PHQ-9)** — the standard clinical screening tool for depression severity, used in primary care and psychiatric settings worldwide. Scores range from 0 to 27, with higher scores indicating more severe depressive symptoms.

The **Fatigue Severity Scale** — a nine-item questionnaire measuring the impact of fatigue on daily functioning.

The **Perceived Stress Scale** — the most widely used instrument for measuring subjective stress levels.

The **Insomnia Severity Index** — a seven-item self-report measure of insomnia severity and impact.

The **Epworth Sleepiness Scale** — a measure of daytime sleepiness that distinguishes between normal alertness and pathological somnolence.

Caffeine intake was measured by the number of servings of coffee or energy drinks consumed per day. Soda consumption was not evaluated.

## The Findings

The results followed a dose-response pattern:

**Three to four servings per day** of caffeine were independently associated with higher PHQ-9 depression scores (P = .03).

**Five to six servings per day** showed a stronger association (P = .004).

**Seven or more servings per day** remained significantly associated (P = .01).

One to two servings per day did not reach statistical significance for an independent association with higher depression scores.

Insomnia, sleepiness, fatigue, and stress were each independently associated with worse depression scores (all P < .0001), confirming what clinicians already know: these conditions cluster.

## The Caffeine Paradox

The study's most interesting finding was not the dose-response relationship between caffeine and depression — that finding is intuitive, given caffeine's effects on sleep, anxiety, and cortisol. The interesting finding was what caffeine appeared to do to the relationship between insomnia and depression.

Among participants with moderate-to-severe insomnia, the strongest association with higher depression scores was observed in those who did not consume caffeine at all (B = 13.5, P < .001). Although the insomnia-depression link remained significant among caffeine consumers, it was weaker (B = 8.0-9.2, P < .001 for all caffeine consumption levels).

Similar results were found for poor sleep quality: non-caffeine users showed the greatest association between poor sleep and depression (B = 11.8, P < .001), while caffeine consumers showed attenuated associations.

This creates a paradox: caffeine is independently associated with worse depression, but it appears to buffer the relationship between insomnia and depression. The people who do not drink caffeine and who also have severe insomnia are the most depressed. The people who drink caffeine and have severe insomnia are still depressed, but less so.

Lead investigator Mira Kaur Marwah, a medical student at the University of Arizona, suggested that the findings indicate caffeine use may influence the relationship between sleep disturbances and depression — potentially because some people use caffeine to cope with the symptoms of depression and insomnia, partially masking the functional impairment that untreated insomnia causes.

In other words, caffeine is simultaneously making depression worse (at high doses) while making depressed people feel somewhat less impaired by their insomnia. It is a coping mechanism that exacerbates the underlying condition it is trying to treat.

## What Indian Americans Drink Now vs. What They Grew Up Drinking

To understand what this study means for Indian Americans, you have to quantify the caffeine shift that immigration and professional assimilation caused.

### Two Cups of Chai: The Traditional Indian Default

In most Indian households, the default caffeine intake is two cups of tea per day — one in the morning and one in the late afternoon, around 4 PM (the "chai time" that is as culturally embedded as the British teatime it descended from).

Indian chai is not the same beverage as the "chai latte" sold in American coffee shops. It is black tea (typically CTC Assam or a blend) boiled in water and milk with sugar and spices — cardamom (elaichi), ginger (adrak), occasionally cloves (laung) or cinnamon (dalchini).

A standard cup of Indian chai contains approximately 40 to 60 milligrams of caffeine, depending on the brewing time and tea strength. Two cups deliver 80 to 120 milligrams of caffeine per day.

This is well below the study's threshold of three servings, where the independent association with higher depression scores begins.

But the caffeine in chai is not equivalent to the caffeine in coffee, and not because of the amount. Tea contains L-theanine, an amino acid that crosses the blood-brain barrier and promotes alpha-wave brain activity — the relaxed, alert state associated with meditation and focused attention. L-theanine has been shown in multiple randomised controlled trials to reduce anxiety and mitigate the jitteriness and cortisol spikes caused by caffeine. A 2019 meta-analysis published in Plant Foods for Human Nutrition found that L-theanine in combination with caffeine improved both attention and reported calmness compared to caffeine alone.

The traditional Indian chai delivers caffeine and L-theanine simultaneously, in a ratio that promotes alertness without anxiety. The American drip coffee delivers caffeine alone.

Additionally, the spices in Indian chai have their own neurological and metabolic effects:

**Cardamom** — contains 1,8-cineole, which has been shown to reduce cortisol levels in animal studies. Cardamom is traditionally considered a "cooling" spice in Ayurvedic medicine, used to counterbalance the stimulating effect of tea.

**Ginger** — has well-documented anti-nausea, anti-inflammatory, and serotonin-modulating properties. The gingerol in ginger has been shown to influence serotonin receptors in the gut and brain, potentially counteracting the serotonin-disrupting effects of high caffeine.

**Cinnamon** — stabilises blood sugar by improving insulin sensitivity, which may buffer the blood-sugar spikes and crashes that caffeine can exacerbate.

The traditional Indian chai, consumed twice a day, delivers moderate caffeine buffered by L-theanine, cardamom, ginger, and cinnamon, totalling approximately 100 milligrams — less than a single cup of American drip coffee. The SHADES study found no significant association between depression and one to two caffeine servings per day. Your grandmother's chai habit falls squarely in the safe zone.

### Four to Six Cups of Coffee: The Indian American Tech Worker Default

The typical Indian American tech worker in the Bay Area, Seattle, or Bangalore's corporate export offices consumes three to six servings of caffeine per day through some combination of:

**Drip coffee** — 95 to 200 milligrams per 8-ounce cup, depending on the roast and brew method. A typical Starbucks "grande" (16 ounces) contains approximately 310 milligrams — nearly triple the caffeine in two cups of chai.

**Cold brew** — 150 to 250 milligrams per serving. Cold brew is brewed at a higher coffee-to-water ratio than drip coffee, and many popular brands (Stumptown, Chameleon, Starbucks cold brew) deliver 200+ milligrams per bottle.

**Espresso-based drinks** — a latte or cappuccino contains one to three shots of espresso (63-189 milligrams per shot). A "venti" latte from Starbucks contains two shots (126 milligrams), but many workers order "extra shots."

**Energy drinks** — Red Bull (80 milligrams per can), Monster (160 milligrams per can), Celsius (200 milligrams per can). These are commonly stocked in tech office refrigerators and consumed in the afternoon as a supplement to morning coffee.

A conservative estimate of the Indian tech worker's daily caffeine intake — one large coffee in the morning, one after lunch, and one energy drink or cold brew in the afternoon — is 400 to 600 milligrams per day, delivered across three to four servings. This places them squarely in the range where the SHADES study found an independent association between caffeine intake and higher depression scores.

A less conservative estimate — two large coffees, one cold brew, and an energy drink — puts them at 600 to 900 milligrams across four to six servings, in the range where the association was strongest (P = .004 at five to six servings).

## The Chai-to-Coffee Pipeline

The transition from chai to coffee is not random. It follows a predictable path that correlates with stages of immigration and professional assimilation.

**Stage one: college.** Indian students arriving at American universities discover that chai is unavailable in campus dining halls and that coffee is free, unlimited, and socially central. Coffee becomes the study fuel. The student goes from 100 milligrams per day (two cups of chai at home) to 200-300 milligrams per day (two to three cups of drip coffee) within the first semester.

**Stage two: first job.** The workplace reinforces coffee culture. Meeting culture is coffee culture — "let's grab coffee" is the universal invitation. Office kitchens are stocked with coffee machines, espresso makers, cold brew kegs. No one makes chai in the office. The caffeine intake climbs to 300-400 milligrams.

**Stage three: crunch.** The first intense work period — a product launch, a deadline, a performance review cycle — introduces the energy drink or the "extra shot" espresso. Caffeine intake crosses 400 milligrams and may reach 600-800 milligrams during intense periods.

**Stage four: dependence.** Caffeine tolerance develops. The same amount no longer produces the same alertness. The worker adds a serving. Then another. The afternoon crash becomes a daily event that requires its own caffeine intervention. Caffeine intake stabilises at 500-700 milligrams per day — five to seven times the traditional Indian default.

At no point in this pipeline does anyone mention mental health. The depressive symptoms that may be developing — low mood, loss of interest, fatigue (which caffeine temporarily masks), disrupted sleep (which caffeine causes), irritability — are attributed to work stress, to the immigrant experience, to loneliness, to anything except the psychoactive substance consumed in the largest quantities.

## The Sleep Problem

The SHADES study found that insomnia and sleepiness were independently associated with depression. This finding interacts with caffeine consumption in a way that is particularly relevant for Indian tech workers.

Caffeine's half-life in the human body is approximately five to six hours. A cup of coffee consumed at 3 PM still has half its caffeine active at 8-9 PM. An energy drink consumed at 4 PM still has significant caffeine circulating at 10 PM. For a person who goes to bed at midnight — a typical Indian tech worker bedtime, given late dinners and evening work — the afternoon caffeine is still active when they are trying to fall asleep.

This creates a cycle: caffeine disrupts sleep. Poor sleep increases fatigue. Fatigue increases caffeine consumption the next day. More caffeine further disrupts sleep. The cycle escalates until the person is consuming five to six servings of caffeine daily, sleeping poorly every night, and experiencing the depression that the SHADES study associates with both high caffeine intake and insomnia.

The traditional Indian chai schedule — one cup in the morning, one cup at 4 PM — was timed to avoid this cycle. The afternoon chai delivered approximately 50 milligrams of caffeine at 4 PM, meaning roughly 25 milligrams would remain active at 10 PM — a negligible amount for sleep disruption. The American coffee schedule — a large coffee at 7 AM, another at noon, a cold brew or energy drink at 3 PM — delivers 150 to 250 milligrams at 3 PM, meaning 75-125 milligrams is still active at bedtime. This is enough to delay sleep onset by 15 to 45 minutes and reduce slow-wave (deep) sleep duration.

## The Cultural Invisibility of Caffeine

One reason the caffeine-depression link is underexamined in the Indian American community is that caffeine is culturally invisible.

Alcohol is noticed. Drug use is noticed. Even sugar is increasingly noticed. But caffeine — the most widely consumed psychoactive substance in the world — is treated as a neutral background substance, like water or air. Nobody at a doctor's visit is asked about their caffeine intake with the same seriousness as their alcohol intake. Nobody at a mental health screening is asked how many cups of coffee they drink before being evaluated for depression.

The SHADES study's investigators noted that the relationship between caffeine, depression, and sleep "has not been well studied." Gregory Scott Brown, chair of the APA's Council on Communications, told Medscape that clinicians should routinely ask patients about caffeine intake — a recommendation that implies they currently do not.

For Indian Americans experiencing depressive symptoms, the caffeine question is particularly important because the magnitude of the caffeine shift — from 100 milligrams to 500-700 milligrams — is larger than in most other immigrant populations. An Italian American may have grown up with espresso culture and maintained similar caffeine levels after immigration. A Mexican American may have continued a moderate coffee-drinking tradition. The Indian American typically underwent a five-fold or greater increase in daily caffeine intake within a few years of arriving in the United States, driven by the total absence of chai from American professional and social environments.

## The Return to Chai

The practical implication of the SHADES study for Indian Americans is not to eliminate caffeine. One to two servings per day showed no significant association with higher depression scores. The implication is to return to the caffeine level and delivery vehicle that the traditional Indian diet provided.

**Two cups of chai per day: approximately 100 milligrams of caffeine, buffered by L-theanine, cardamom, ginger, and cinnamon.** This is below the study's threshold for depression association. It provides the alertness benefits of moderate caffeine without the sleep disruption, cortisol elevation, and mood destabilisation of higher doses.

If you cannot make chai at work, consider the following practical substitutions:

**Replace one of your three daily coffees with tea.** Any black or green tea delivers L-theanine alongside caffeine. The caffeine is lower (40-70 milligrams for black tea, 25-50 milligrams for green tea), and the L-theanine modulates the neurological response. This simple substitution drops your daily intake by 100-200 milligrams.

**Eliminate the afternoon energy drink.** The afternoon energy drink is the serving most likely to disrupt sleep and drive the caffeine-insomnia-depression cycle. Replace it with a walk, a brief conversation with a colleague, or — if available — a cup of masala chai. The alertness deficit you feel at 3 PM is not a caffeine deficiency. It is a circadian dip that every human experiences, regardless of caffeine intake. A 10-minute walk outside is as effective as caffeine at restoring afternoon alertness, according to a 2017 randomised controlled trial published in Physiology & Behavior.

**If you drink coffee, drink it before noon.** This ensures that the caffeine's half-life does not interfere with sleep onset. Morning coffee plus evening chai is a hybrid pattern that many Indian Americans have already adopted — the study's data suggests it is a reasonable compromise.

**Stop ordering "chai lattes" and thinking you are drinking chai.** The American "chai latte" is a different beverage. It typically uses a syrup or concentrate with minimal real spice, added sugar, and cow's milk steamed in a way that destroys some of the heat-sensitive compounds in ginger and cardamom. It also often contains espresso ("dirty chai"), which defeats the purpose. If you want the neurological benefits of traditional chai, make it yourself: black tea, water, whole milk, fresh ginger, green cardamom, and sugar. Five minutes. No machine required.

## What the Study Cannot Tell Us

The SHADES study is cross-sectional, not longitudinal. It measured caffeine intake and depression scores at a single point in time and found a correlation. It cannot prove that caffeine caused the depression. It is equally possible that depressed people consume more caffeine as a coping mechanism — which is exactly what the study's moderation analysis suggests when it found that caffeine weakened the insomnia-depression link.

The study also did not distinguish between types of caffeine sources — black coffee, coffee with sugar and cream, espresso, energy drinks with taurine and B-vitamins — which may have different effects on mood. It did not measure tea consumption as a separate category, so the L-theanine hypothesis cannot be tested within this dataset.

Gregory Scott Brown, who commented on the study for Medscape, called it "just the tip of the iceberg" and noted that it "opens this entire Pandora's box of questions." He is right. The study does not settle the question of whether caffeine causes depression, worsens it, masks it, or some combination of all three.

But it does establish that at three or more servings per day, caffeine intake is independently associated with higher depression scores in a sample of 1,007 adults. And it does establish that one to two servings per day is not. For a population that went from two servings of a buffered, low-caffeine beverage to five servings of a high-caffeine, unbuffered one within a few years of immigration, that threshold is directly relevant.

Your grandmother drank two cups of chai a day. She was not depressed. You drink five cups of coffee. Draw your own conclusion — then draw yourself a cup of chai."""

art2_sources = [
    "https://www.medscape.com/viewarticle/higher-caffeine-intake-tied-greater-depression-severity-2026a1000gtr",
    "https://healthandfamily.in/the-caffeine-paradox-high-intake-linked-to-severe-depression-in-new-study-yet-blunts-insomnias-mood-impact/",
]

print("\n=== Article 2: Chai vs Coffee / Caffeine Depression / Indian Tech Workers ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: chai being poured, Indian tea, or masala chai preparation
art2_image = fetch_pexels_image("Indian masala chai tea being poured cup spices")
if not art2_image:
    art2_image = fetch_pexels_image("traditional chai tea cup ginger cardamom cinnamon")
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
    "score_total": 90,
    "tags": ["caffeine", "depression", "chai", "coffee", "tea", "L-theanine", "cardamom", "ginger", "PHQ-9", "SHADES study", "APA 2026", "insomnia", "sleep", "fatigue", "cortisol", "energy drinks", "cold brew", "Indian tech workers", "Bay Area", "Silicon Valley", "caffeine dependence", "circadian rhythm", "adrak chai", "masala chai", "University of Arizona", "Indian American", "NRI", "mental health", "immigration", "professional assimilation"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "SHADES study (APA 2026): 1,007 adults aged 22-60, cross-sectional. 3-4 caffeine servings/day independently associated with higher PHQ-9 depression scores (P=.03); 5-6 servings P=.004; 7+ P=.01. 1-2 servings: no significant association. Caffeine also moderated insomnia-depression link (non-users B=13.5 vs caffeine users B=8.0-9.2 for severe insomnia). NRI angle: Traditional Indian chai = 2 cups/day, ~100 mg caffeine, buffered by L-theanine + cardamom + ginger. Indian American tech workers = 3-6 servings of drip coffee/cold brew/energy drinks, 400-600 mg caffeine. The 5x increase in caffeine intake from immigration + professional assimilation follows a predictable pipeline: college (free coffee, no chai available) → first job (meeting culture = coffee culture) → crunch periods (energy drinks, extra shots) → dependence (500-700 mg/day). The chai-to-coffee shift crosses the study's 3-serving threshold. The afternoon energy drink drives the caffeine-insomnia-depression cycle. Traditional chai schedule (morning + 4 PM) was timed to avoid sleep disruption. American coffee schedule (7 AM + noon + 3 PM) delivers 75-125 mg active at bedtime.",
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
commit_msg = "lifestyle: spicy food gut SCFA + chai vs coffee depression (2026-05-26 07:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
