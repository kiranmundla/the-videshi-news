#!/usr/bin/env python3
"""Lifestyle & Markets writer for The Videshi — 2026-06-08 run"""

import json, os, sys, uuid, datetime, requests

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
NOW = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def insert_article(article):
    """Insert article into Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Published: {article['slug']} (id: {aid})")
        return True
    else:
        print(f"  ✗ FAILED: {r.status_code} — {r.text[:300]}")
        return False


# ═══════════════════════════════════════════════════════════
# ARTICLE 1: Gut Microbiome + Cancer Immunotherapy
# Category: lifestyle-health
# ═══════════════════════════════════════════════════════════

article1_body = """The idea that the trillions of bacteria living inside your gut might determine whether a cancer drug saves your life sounds like the premise of a science fiction novel. It is not. It is the subject of nearly 100 active clinical trials, a field that the National Institutes of Health Director recently called "mind-blowing," and a story that begins, improbably, with chickens.

Dr Sumanta Pal, a kidney cancer specialist at City of Hope Cancer Center in Los Angeles, traces his interest in the microbiome to a conversation over a decade ago with a biostatistician named Dr Paul Frankel. Frankel mentioned that poultry operations had long observed a correlation between gut bacteria and the health of their animals. Farmers would limit how often they cleaned litter when chickens were thriving, and they fed pigs inulin — a fiber prebiotic — to boost beneficial Bifidobacteria. "They knew exactly what they were doing," Frankel said.

What the livestock industry understood intuitively, oncology is now proving in clinical trials.

## The First Major Probiotic Cancer Trial

In the coming days, a kidney cancer patient at University Hospitals Seidman Cancer Center in Cleveland will become the first participant in the largest trial ever to test whether a probiotic pill can amplify cancer immunotherapy. The National Cancer Institute-funded study will enrol nearly 700 people with advanced renal cell carcinoma across multiple centres. Each will swallow capsules of CBM588 — a strain of Clostridium butyricum that has been sold over the counter in Japan since the 1960s for gastrointestinal complaints — alongside their standard immunotherapy.

"We're hoping to change the standard of care," said Dr Pedro Barata, one of three principal investigators on the trial.

The study builds on earlier Phase 1 results that stunned researchers. When CBM588 was added to a combination of cabozantinib and nivolumab, the objective response rate among kidney cancer patients jumped from 20 per cent in the control group to 74 per cent in the probiotic group. In an earlier trial with nivolumab and ipilimumab, progression-free survival improved significantly with CBM588.

Researchers at Cardiff University and Kumamoto University in Japan published the first clear biological explanation earlier this year. The probiotic activates a specialised population of T-cells called Vγ9Vδ2 T-cells, which can recognise and kill cancer cells directly. It is the kind of mechanistic clarity that turns a promising observation into a credible therapeutic strategy.

## Why Your Gut Holds a Third of Your Immune System

The human intestine has a surface area roughly 20 times larger than the skin. According to Dr Marcel van den Brink, president of City of Hope, this vast landscape holds about a third of all the body's T-cells and B-cells — the immune system's primary weapons against cancer. Because these cells are immersed in a dense ecosystem of bacteria, the gut is where the immune system learns to fight invaders and abnormal cells.

Disrupt that ecosystem — through broad-spectrum antibiotics, a sugar-heavy diet, or chemotherapy — and outcomes suffer. Van den Brink and colleagues analysed fecal samples from more than 1,300 bone marrow transplant recipients and found that dysbiosis, an imbalance in gut bacteria, was directly linked to death.

At the CHUM Microbiome Centre in Montreal, Dr Arielle Elkrief's team doubled the number of lung cancer patients who responded to immunotherapy when they combined it with fecal microbiota transplants from healthy volunteers. The results were published in Nature Medicine.

A seminal 2021 study from MD Anderson Cancer Center showed that for every five-gram increase in daily fibre intake, the risk of cancer progression or death from melanoma fell 30 per cent. Certain gut bacteria metabolise fibre into short-chain fatty acids that appear to improve T-cell survival and suppress inflammation.

## What This Means for the Diaspora

South Asians have something the Western diet often lacks: a food tradition built around fermented and fibre-rich foods. Dahi, idli, dosa, kanji, pickled achaar, fermented rice — these are not health fads. They are the dietary equivalent of what Frankel's poultry farmers were doing deliberately.

But the diaspora diet is changing. The shift toward processed food, refined carbohydrates, and frequent antibiotic use is quietly eroding the microbial diversity that traditional diets nurtured. Indian Americans are already at elevated risk for certain cancers, particularly gastrointestinal and renal cancers, and the microbiome connection makes dietary choices a frontline defence strategy.

Dr Pal urges caution about self-medicating with over-the-counter probiotics before trial data matures. "I know a lot of patients have been taking these supplements," he said. "But I really do urge them to wait for the data from the clinical trials to come out."

In the meantime, the evidence supports a simpler intervention: eat real food, eat fibre, eat fermented. City of Hope has already overhauled its inpatient menu, replacing the sugar-heavy nutrition shakes that were standard for decades with fresh salads, organic vegetables, and high-fibre meals.

"We're looking to make diet into a drug," van den Brink said. "But we're only just starting to learn how to manipulate it."

*Sources: CNN, Nature Medicine, Cardiff University, American Society of Clinical Oncology, City of Hope Cancer Center*"""

article1 = {
    "headline": "A Probiotic Pill Just Entered the Largest Cancer Trial of Its Kind. Your Dadi's Dahi May Have Been Training Your Immune System All Along.",
    "subheadline": "Nearly 700 kidney cancer patients will test whether a Japanese gut bacterium can amplify immunotherapy. The science traces back to chicken farmers, but the implications land squarely on the South Asian dinner table.",
    "body": article1_body,
    "slug": "cbm588-probiotic-cancer-immunotherapy-trial-gut-microbiome-south-asian-diet-20260608",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "image_url": "https://images.pexels.com/photos/30637886/pexels-photo-30637886.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Fermented vegetables in mason jars, a practice that nurtures the gut bacteria now linked to cancer treatment outcomes",
    "image_attribution": "Pexels",
    "status": "published",
    "published_at": NOW,
    "sources": json.dumps([
        "CNN — A healthier gut may be key to cancer care (June 2026)",
        "Nature Medicine — Nivolumab plus ipilimumab with or without live bacterial supplementation in metastatic renal cell carcinoma",
        "Cardiff University — International team identifies immune pathway (March 2026)",
        "American Society of Clinical Oncology — ~100 active gut microbiome cancer studies",
        "BMC Cancer — Modulating the gut microbiome to enhance cancer immunotherapy (meta-analysis, 2026)"
    ]),
    "is_editorial": False
}


# ═══════════════════════════════════════════════════════════
# ARTICLE 2: New Weight Loss Drugs Beyond Ozempic
# Category: lifestyle-health
# ═══════════════════════════════════════════════════════════

article2_body = """The American Diabetes Association meeting in New Orleans this week became the staging ground for a drug race that could reshape obesity treatment — and for once, the biggest headlines did not belong to Ozempic or Wegovy.

Two experimental drugs, working through entirely different biological pathways, posted results that challenge the dominance of Novo Nordisk and Eli Lilly in the weight loss market. Both carry implications that matter disproportionately for South Asians, the population with the highest metabolic disease burden on the planet.

## Petrelintide: Weight Loss Without the Nausea

Zealand Pharma, a Danish biotech backed by a $5.3 billion collaboration with Roche, presented expanded data from its Phase 2 ZUPREME-1 trial. Petrelintide, an amylin analog, produced weight loss of up to 10.7 per cent over 42 weeks — with a tolerability profile that stopped the obesity drug world in its tracks.

Only 1.5 per cent of patients discontinued treatment due to gastrointestinal side effects. Nausea occurred in 19.6 per cent versus 6.2 per cent on placebo, but vomiting was rarer in the drug arm (3 per cent) than in the placebo group (6.2 per cent). Diarrhoea and constipation were below 7.5 per cent in both groups.

For context, Wegovy's pivotal trial saw nausea rates of 44 per cent, vomiting in 24 per cent, and diarrhoea in 30 per cent. The GI side effects of current GLP-1 drugs are the single biggest reason patients stop taking them, with real-world persistence at one year hovering around 30-40 per cent.

"People living with overweight and obesity need treatments they can stay on long-term," said Prof W Timothy Garvey of the University of Alabama at Birmingham. "These data highlight the potential of petrelintide to be just such a treatment."

Petrelintide works through amylin, a hormone co-secreted with insulin from pancreatic beta cells. Unlike GLP-1 drugs, which primarily suppress appetite through gut signalling, amylin restores sensitivity to leptin — the satiety hormone — and slows gastric emptying with less intestinal distress. Crucially, early signals suggest it may preserve muscle mass during weight loss, a limitation of current therapies that concerns physicians.

Phase 3 trials are planned for the second half of 2026.

## Enicepatide: 22.7 Per Cent Weight Loss in Under a Year

On the same day, Roche unveiled results for enicepatide, its own candidate that takes a different approach. This dual-acting drug mimics both GLP-1 and GIP hormones — like Lilly's Zepbound — but achieved 22.7 per cent weight loss in just 48 weeks.

That timeline matters. Novo Nordisk's Wegovy needed 68 weeks to reach about 15 per cent weight loss. In a recent head-to-head trial, Lilly's Zepbound delivered 25.5 per cent at 84 weeks. Enicepatide is on pace to match or exceed those numbers in substantially less time.

Among patients on the highest dose, 26 per cent lost at least 30 per cent of their body weight. The weight-loss trajectory showed "no hint of any plateau" at week 48, according to Roche's Manu Chakravarthy.

Treatment discontinuation due to side effects was 5.9 per cent — higher than petrelintide but still markedly lower than first-generation GLP-1 drugs.

## Why South Asians Cannot Afford to Wait

The World Health Organization uses a BMI threshold of 30 to define obesity. For South Asians, metabolic complications begin at BMI 23 — the point where a white European might be classified as merely overweight. Indian Americans develop type 2 diabetes at rates four times higher than the general population, often at younger ages and lower body weights.

Current GLP-1 drugs work but come with practical barriers: nausea severe enough to disrupt daily life, muscle loss that concerns aging patients, and costs that insurance does not always cover. A drug like petrelintide, with placebo-like tolerability and muscle preservation signals, could dramatically improve adherence in a population where metabolic intervention is most urgent.

The obesity drug market, which analysts project will exceed $100 billion annually, is moving from a monopoly to a marketplace. For the estimated 200 million South Asians worldwide living with metabolic syndrome, more options and fewer side effects are not abstract commercial developments. They are a matter of survival.

*Sources: Zealand Pharma press release (June 5, 2026), Reuters, GlobeNewsWire, American Diabetes Association 2026 Scientific Sessions*"""

article2 = {
    "headline": "Two New Weight Loss Drugs Just Outperformed Wegovy With a Fraction of the Side Effects. South Asians Should Be Watching Closely.",
    "subheadline": "Petrelintide cut GI side effects to near-placebo levels. Enicepatide hit 22.7 per cent weight loss in 48 weeks. The obesity drug monopoly is cracking open, and the stakes are highest for the diaspora.",
    "body": article2_body,
    "slug": "petrelintide-enicepatide-new-weight-loss-drugs-ada-2026-south-asian-metabolic-20260608",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "image_url": "https://images.pexels.com/photos/8670445/pexels-photo-8670445.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Injectable weight loss medications and measuring tape, representing the new generation of obesity treatments presented at ADA 2026",
    "image_attribution": "Pexels",
    "status": "published",
    "published_at": NOW,
    "sources": json.dumps([
        "Zealand Pharma — ZUPREME-1 Phase 2 trial data presentation at ADA 2026 (June 5, 2026)",
        "Reuters — Zealand touts promising tolerability data for obesity drug (June 6, 2026)",
        "Reuters — Roche obesity drug helps patients shed 22.7% of weight in mid-stage trial (June 6, 2026)",
        "GlobeNewsWire — New data from Phase 2 ZUPREME-1 trial at the ADA 2026"
    ]),
    "is_editorial": False
}


# ═══════════════════════════════════════════════════════════
# ARTICLE 3: RBI Rate Cycle Reversal
# Category: markets-finance
# ═══════════════════════════════════════════════════════════

article3_body = """The Reserve Bank of India held its repo rate at 5.25 per cent on Friday. That was the expected decision. What was not expected — at least not by the majority of retail investors and NRIs still hoping for cheaper home loans — was the tone.

RBI Governor Sanjay Malhotra did not just pause. He warned. He raised the inflation projection for FY27 from 4.6 per cent to 5.1 per cent. He cut the GDP growth forecast from 6.9 per cent to 6.6 per cent. And he made it clear that the prolonged conflict in West Asia, elevated crude oil prices, and persistent supply-chain disruptions are not transitory headwinds. They are structural threats.

Multiple senior economists have now said what the RBI could not say explicitly: the next move may be up, not down. The easing cycle that began with a rate cut in December 2025 may already be over.

## The Voices Warning of a Hike

Aditi Nayar, Chief Economist at ICRA, was blunt: "As of now, we cannot rule out a rate hike in the third quarter of FY2027." That puts the window between October and December 2026.

Naveen Kulkarni, Chief Investment Officer at Axis Securities PMS, went further: "Apart from the oil price shock, a possible subpar monsoon will also push inflation higher. Moreover, the rupee has depreciated sharply against the dollar and has been the worst-performing currency in the emerging markets. We believe these factors collectively would drive the regulator to reverse the rate cycle in the coming policy meetings."

The rupee has fallen to levels not seen since the 2013 crisis. Foreign portfolio investors have pulled more money out of India in 2026 than in all of last year. Crude oil prices remain elevated due to the Middle East conflict and Strait of Hormuz disruptions. And monsoon forecasts are uncertain, which directly impacts food prices in an economy where food inflation has been the primary driver of headline CPI.

## What a Rate Hike Means for Your Money

For NRIs holding floating-rate home loans in India, a 25 basis point hike on a Rs 50 lakh, 20-year loan would increase the EMI by approximately Rs 788 per month — Rs 9,456 extra per year, and nearly Rs 1.9 lakh over the life of the loan. If the RBI hikes twice, as some analysts fear, those numbers double.

For NRIs considering property purchases in India, the window of stable borrowing costs may be closing. "If RBI were to raise lending rates, higher material costs would be compounded by more expensive loan rates," said Anuj Puri, Chairman of ANAROCK Group. Developers are already under pressure from rising construction input costs; passing those through to buyers alongside higher EMIs would squeeze affordability from both sides.

For remittances, a weaker rupee means more rupees per dollar — which sounds favourable until you account for the fact that property prices, construction costs, and inflation are rising in rupee terms. The net purchasing power of remittances is not improving as fast as the exchange rate suggests.

## The FCNR Opportunity — and Its Limits

The RBI announced subsidised hedging costs for banks on new FCNR(B) deposits — a clear signal that it wants NRI dollars. FCNR deposits, denominated in foreign currencies, let NRIs park dollars and earn interest without currency risk. The RBI is sweetening the deal to attract capital inflows and support the rupee.

But FCNR deposits are not a savings account. They are a tactical instrument best suited for NRIs who have surplus dollars, want rupee exposure without conversion risk, and are comfortable locking funds for one to five years. Current FCNR rates for dollar deposits range from 4.5 to 5.5 per cent — competitive with US CDs, but without FDIC insurance.

The government also exempted foreign institutional investors from capital gains tax on government securities — a measure aimed at boosting foreign inflows into the debt market and supporting the rupee. For retail NRIs, this signals that the authorities view rupee weakness as serious enough to deploy fiscal incentives, not just monetary tools.

## What NRIs Should Do Now

The consensus among analysts is not that a rate hike is certain, but that the probability has shifted meaningfully. Manoranjan Sharma, Chief Economist at Infomeric Ratings, described the RBI's stance as "not merely a pause — it is a strategic hold."

For NRIs, three actions make sense. First, if you hold a floating-rate home loan in India, stress-test your budget against a scenario where rates rise 50 basis points by year-end. Second, if you were waiting for further rate cuts before buying property, that wait may not be rewarded. Third, evaluate FCNR deposits while the RBI is actively incentivising them — these windows tend to close once the rupee stabilises.

The RBI is walking a tightrope between supporting growth and defending the currency. For the diaspora, the signal is clear: the era of cheap money in India is not coming back any time soon.

*Sources: Reserve Bank of India June 2026 MPC statement, Reuters, LiveMint, Outlook Money, The Hindu BusinessLine*"""

article3 = {
    "headline": "The RBI May Raise Interest Rates Next. The Era of Cheap Money in India Could Be Over.",
    "subheadline": "Senior economists warn of a rate hike by December. Floating-rate home loan EMIs could rise Rs 788 per month. For NRIs, the window of stable borrowing costs may be closing.",
    "body": article3_body,
    "slug": "rbi-rate-hike-warning-december-2026-nri-home-loans-emi-fcnr-deposits-20260608",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_03.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_03.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, where the MPC held rates at 5.25 per cent while warning of inflation risks",
    "image_attribution": "Wikimedia Commons",
    "status": "published",
    "published_at": NOW,
    "sources": json.dumps([
        "Reserve Bank of India — June 2026 Monetary Policy Committee statement",
        "Reuters — Indian shares hold gains after RBI rate pause; Instant View on rate decision",
        "LiveMint — Buy or sell: Sumeet Bagadia market analysis for June 8, 2026",
        "Outlook Money — RBI Keeps Repo Rate Unchanged at 5.25%: What It Means For Home Loan EMIs",
        "The Hindu BusinessLine — Stock Market Highlights June 5: Markets turn weak post RBI pause"
    ]),
    "is_editorial": False
}


# ═══════════════════════════════════════════════════════════
# PUBLISH ALL THREE
# ═══════════════════════════════════════════════════════════

print("=" * 60)
print("The Videshi — Lifestyle & Markets Writer — 2026-06-08")
print("=" * 60)

articles = [
    ("LIFESTYLE-HEALTH #1: Gut Microbiome + Cancer", article1),
    ("LIFESTYLE-HEALTH #2: New Weight Loss Drugs", article2),
    ("MARKETS-FINANCE: RBI Rate Hike Warning", article3),
]

results = []
for label, art in articles:
    print(f"\n📝 {label}")
    print(f"   Headline: {art['headline'][:80]}...")
    print(f"   Slug: {art['slug']}")
    print(f"   Category: {art['category']}")
    word_count = len(art['body'].split())
    print(f"   Word count: {word_count}")
    if word_count < 400:
        print(f"   ⚠ BELOW 400 WORD FLOOR — SKIPPING")
        results.append(False)
        continue
    ok = insert_article(art)
    results.append(ok)

print(f"\n{'='*60}")
print(f"Results: {sum(results)}/{len(results)} published successfully")
print(f"{'='*60}")
