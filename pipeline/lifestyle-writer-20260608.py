#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-08 run"""

import json, os, requests, uuid
from datetime import datetime, timezone

# Load Supabase creds
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

supabase = load_env('~/.env.supabase')
SUPABASE_URL = supabase['SUPABASE_URL']
SUPABASE_KEY = supabase['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert_article(article):
    """Insert article into Supabase"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('headline', 'N/A')[:60]}... (id: {data[0].get('id', 'N/A')[:12]})")
        else:
            print(f"  ✓ Inserted (raw): {r.text[:100]}")
    else:
        print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")

now = datetime.now(timezone.utc).isoformat()

# =========================================
# ARTICLE 1: Survodutide Obesity Drug Failure
# =========================================
article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Obesity Drug That Was Supposed to Fix Your Liver Just Lost One in Four Patients to Side Effects",
    "subheadline": "Survodutide showed impressive liver fat reduction in Phase 3 trials but a 19 per cent dropout rate from gut problems. South Asians, who carry the highest fatty liver burden globally, have reason to pay attention.",
    "slug": "survodutide-obesity-liver-drug-side-effects-south-asian-fatty-liver-masld-20260608",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Stage_of_liver_damage_high.jpg/1280px-Stage_of_liver_damage_high.jpg",
    "image_caption": "Stages of liver damage from healthy tissue to fatty liver disease and cirrhosis",
    "image_attribution": "Wikimedia Commons",
    "published_at": now,
    "sources": json.dumps([
        "Reuters — Zealand Pharma shares drop 25% after a quarter of patients quit obesity drug trial",
        "Wall Street Journal — Zealand Pharma Shares Slide After Boehringer Study Shows Obesity Shot's Side Effects",
        "MarketWatch — Zealand Pharma loses a fifth of its value as many users gave up taking weight-loss drug during trial",
        "Boehringer Ingelheim — SYNCHRONIZE-1 and SYNCHRONIZE-MASLD Phase 3 data",
        "Novo Nordisk — Wegovy pill prescriptions surpass 3 million"
    ]),
    "body": """The weight loss drug race just got a reality check.

Survodutide, an experimental obesity injection developed by Boehringer Ingelheim and Denmark's Zealand Pharma, posted deeply mixed results from two Phase 3 trials presented at the American Diabetes Association's 2026 Scientific Sessions over the weekend. The drug cut liver fat by up to 63 per cent and visceral fat by 34 per cent — numbers that had scientists paying close attention. But nearly one in four patients taking the highest dose dropped out of the trial because they could not tolerate the side effects.

Zealand Pharma's stock collapsed 25 per cent on Monday morning in Copenhagen, its worst single-day loss in years, dragging the company's year-to-date decline past 47 per cent.

## What Survodutide Promised

Survodutide is a dual agonist — it activates both the GLP-1 and glucagon receptors, a mechanism designed to do more than just suppress appetite. The GLP-1 pathway reduces hunger. The glucagon pathway is thought to act directly on the liver, reducing hepatic fat, resolving inflammation and potentially reversing the early stages of fibrosis.

For people with metabolic dysfunction-associated steatotic liver disease — the condition formerly known as non-alcoholic fatty liver disease, or NAFLD — this was a potentially transformative combination. The SYNCHRONIZE-MASLD trial showed that up to 84.2 per cent of patients on survodutide achieved at least a 30 per cent reduction in liver fat, compared with 24.3 per cent on placebo. Weight loss averaged 12.2 per cent in the liver-focused trial and reached 16.6 per cent in the broader obesity study.

## The Tolerability Problem

But the dropout numbers tell a different story. In the main obesity trial, SYNCHRONIZE-1, 19 per cent of patients on survodutide stopped treatment because of gastrointestinal side effects — nausea, vomiting, diarrhea and constipation. At the highest 6-milligram dose, the figure reached 25 per cent. On placebo, the dropout rate was just 2.9 per cent.

For context, Novo Nordisk's Wegovy and Eli Lilly's Zepbound showed discontinuation rates of just 7 per cent and 6 per cent in their respective trials.

Analysts at Goldman Sachs said the low tolerability is "likely to limit utilization in the obesity market." Barclays called the safety profile "disappointing." Jefferies pointed to a tolerability worse than therapies already on the market.

Boehringer attributed part of the problem to a rigid dosing schedule that left little room for patients to reduce their dose when side effects hit. By the time more flexibility was introduced, roughly three-quarters of patients had fewer than three months of treatment remaining.

## Why South Asians Should Be Watching

The fatty liver finding matters enormously for the Indian diaspora. South Asians have among the highest global prevalence of MASLD — studies show rates exceeding 30 per cent in urban populations in India and elevated rates among diaspora communities in the US, UK and Canada. The condition is closely linked to the metabolic profile that defines South Asian cardiovascular risk: central obesity, insulin resistance, dyslipidemia and visceral fat accumulation, often at BMIs that Western guidelines would classify as normal.

There is currently no approved drug specifically for MASLD. Survodutide's liver data represented one of the most promising results yet. But if a quarter of patients cannot stay on the drug long enough to benefit, the practical value shrinks dramatically.

## The Bigger Picture

Meanwhile, the weight loss drug market continues to accelerate elsewhere. Novo Nordisk announced on Sunday that prescriptions for its Wegovy pill — an oral semaglutide tablet launched in January 2026 — have surpassed three million in just five months. That translates to roughly one prescription filled every five seconds, making it one of the most successful pharmaceutical launches in American history.

More than 80 per cent of those prescriptions went to patients who had never used a GLP-1 drug before, suggesting the pill is expanding the market rather than cannibalising injections.

The weight loss drug landscape is now splitting into two clear lanes. In one, proven therapies like semaglutide are moving from injection pens to daily pills, trading maximum efficacy for convenience and tolerability. In the other, next-generation drugs like survodutide promise more targeted metabolic benefits — attacking liver fat, preserving muscle mass — but at the cost of side effects that many patients cannot endure.

For the millions of South Asians living with fatty liver disease and no approved treatment, the question is not whether better drugs are coming. The question is whether they will come in a form people can actually take."""
}

# =========================================
# ARTICLE 2: Laughter and Children's Brain Development
# =========================================
article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Laughter Rewires Your Child's Brain Faster Than Flashcards. The Science Says It Is Not Even Close.",
    "subheadline": "New research shows laughter activates the prefrontal cortex, floods the brain with dopamine and builds resilience before children can even speak. Diaspora parents pushing academics first may want to read this twice.",
    "slug": "laughter-brain-development-children-prefrontal-cortex-diaspora-parenting-20260608",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/5278985/pexels-photo-5278985.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Children laughing and playing together outdoors on a sunny day",
    "image_attribution": "Pexels",
    "published_at": now,
    "sources": json.dumps([
        "Fox News / SWNS — Scientists reveal surprising brain benefit of laughter: It's a mental workout",
        "Dr. Jacqueline Harding, Middlesex University London — The Brain That Loves to Laugh",
        "PLOS ONE — The neurodevelopmental basis of humor appreciation: A fNIRS study of young children",
        "Stanford University — Researchers Use fMRI to Study How Humor Activates Kids' Brain Regions"
    ]),
    "body": """There is a scene that plays out in Indian households across the diaspora every evening. The homework is done. The math tutor has left. The violin practice is over. And somewhere between the structured enrichment and the bedtime routine, a child laughs — not at a lesson, not at an app, but at something genuinely, irreducibly funny. A sibling's face. A dog chasing its tail. The absurdity of a word repeated too many times.

According to a growing body of neuroscience research, that unscripted moment of laughter may be doing more for the child's brain development than every structured activity that preceded it.

## The Brain That Loves to Laugh

Dr. Jacqueline Harding, an early childhood development expert at Middlesex University in London, argues in her new book *The Brain That Loves to Laugh* that laughter is not a byproduct of learning — it is a driver of it. Her research, reported this week, shows that laughter activates broad neural networks across the brain, including motor regions and the prefrontal cortex, long before children learn to speak.

The prefrontal cortex is the brain's command centre for planning, decision-making and impulse control — the very region that parents spend years trying to develop through structure and discipline. Laughter, it turns out, lights it up like few other activities can.

"When we see children laugh, we witness the brilliance of the brain in action: learning, connecting and growing," Harding told SWNS. "Hope and humour, it seems, are not just the seasoning of life, but foundational to a recipe for healthy development."

## The Chemistry of Joy

At a molecular level, the effects are striking. Laughter decreases cortisol and epinephrine — the hormones associated with stress and anxiety — while simultaneously increasing dopamine, serotonin and endorphins. This is not a modest shift. It is a wholesale neurochemical environment change, creating the conditions under which the brain is most receptive to learning and memory formation.

Laughter also boosts oxytocin, the hormone that deepens emotional bonds between parents and children. In a diaspora context where extended family is often thousands of miles away, this matters. The parent-child bond carries more of the emotional weight when grandparents, aunts and uncles are a video call rather than a presence in the next room.

Prolonged stress does the exact opposite. It impairs learning, suppresses immune function and alters the developing limbic system — the brain's emotional command centre. "The emotional state of young children directly influences how they navigate their way through the world," Harding said.

## The Incongruity Engine

What makes laughter particularly powerful for cognitive development is that it requires the brain to do something difficult: resolve incongruity. Humour, at its core, is the brain detecting that something does not fit the expected pattern and then making sense of the mismatch. This process engages working memory, boosts creativity and builds the neural flexibility that cognitive scientists call "executive function."

Research from Stanford University using fMRI scans found that funny videos activated two key brain regions in children aged 6 to 12 — the temporal-occipital-parietal junction, which processes perceived incongruities, and the mesolimbic reward system, which registers pleasure. In children, both hemispheres were activated; in adults, only the left side lights up. This bilateral activation suggests that humour is literally helping the young brain build the neural architecture it will use for the rest of its life.

## The Diaspora Parenting Dilemma

South Asian diaspora parenting exists in a unique tension. There is the inherited emphasis on academic achievement, structured learning and measurable outcomes — the marks, the grades, the admissions. And there is the growing scientific consensus that unstructured play, spontaneous joy and yes, laughter, are not luxuries to be squeezed in after the real work is done. They are the real work.

This is not an argument against academic rigour. It is an argument against the assumption that every hour of a child's day must be optimised, structured and productive in a way that looks productive to an adult.

The research suggests that a child laughing at the dinner table is building prefrontal cortex capacity. A child playing an absurd made-up game with a sibling is exercising working memory. A child who feels safe enough to be silly is developing the emotional resilience that will carry them through adolescence, exam pressure and the particular stresses of growing up between cultures.

## What Parents Can Do

Harding's advice is deceptively simple: create moments of spontaneous play and joyful connection. Not scheduled fun. Not app-based enrichment. Not laughter engineered by a curriculum. The kind of laughter that happens when a parent does something unexpected, when a joke lands badly and becomes funnier for it, when the family surrenders the plan and follows the moment.

Your grandmother, who told stories and cracked jokes while the children sat around her, was not filling time. She was building brains. The science has finally caught up to what she already knew."""
}

# =========================================
# ARTICLE 3: Indian IT Stocks Crash
# =========================================
article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Wipro Just Hit a Three-Year Low. The AI Bubble That Inflated Indian IT Is Now Deflating It.",
    "subheadline": "Nifty IT fell 2 per cent on Monday as Nasdaq's worst day in a year sent shockwaves through Bengaluru. Semiconductors crashed 10 per cent on Friday. Many NRI tech workers hold these stocks. Here is what is happening.",
    "slug": "wipro-tcs-nifty-it-crash-ai-selloff-nasdaq-nri-tech-workers-stocks-20260608",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/S3_and_S4_Building_SJP2_Wipro_Sarjapur_office_Photo_182805.jpg",
    "image_caption": "Wipro's Sarjapur office campus in Bengaluru, home to thousands of IT workers",
    "image_attribution": "Wikimedia Commons",
    "published_at": now,
    "sources": json.dumps([
        "Reuters — Indian shares decline to two-month lows on oil spike, Asia selloff",
        "The Hindu BusinessLine — Wipro, TCS drag Nifty IT 2% lower after Nasdaq crash, AI selloff",
        "Barron's — The Jobs Report Hit Solar and AI Stocks. Here's Who Can Handle Higher Interest Rates",
        "Investopedia — Nasdaq, S&P 500 Close Higher, Led by Tech Shares",
        "Outlook Business — Sensex, Nifty Fall Nearly 1% Amid Geopolitical Escalation"
    ]),
    "body": """The AI trade that lifted Indian IT stocks for much of the past two years turned against them on Monday.

Wipro crashed 8.4 per cent to ₹187, touching its lowest price in three years. TCS fell 2.4 per cent to ₹2,144. The Nifty IT index opened down 2 per cent — or 593 points — to 28,418 before staging a partial recovery. Infosys, HCL Tech, Persistent Systems and Coforge all traded in the red. Tech Mahindra was the only major IT stock to hold above water.

The trigger was not in India. It was in the United States, where the Nasdaq Composite plunged more than 4 per cent on Friday — its worst session in over a year — as the AI-driven rally that had powered American tech stocks to record highs finally cracked.

## What Broke

Three forces converged on Friday.

First, the US added 272,000 jobs in May, far more than expected. Markets had been pricing in rate cuts later this year. The strong jobs report shattered that narrative. The probability of a Federal Reserve rate hike by December 2026 jumped to 72.3 per cent, up from 45.2 per cent a week earlier, according to CME FedWatch data.

Second, Broadcom's earnings — released Wednesday — showed a slight revenue miss and a weaker-than-expected near-term forecast for AI chips. The PHLX Semiconductor Index collapsed 10.3 per cent on Friday, its largest single-day drop since March 2020. Nvidia, Micron and other AI darlings were among the heaviest casualties.

Third, Iran launched missiles at Israel over the weekend after Israeli strikes on Beirut, driving Brent crude above $97 a barrel — a 4.3 per cent jump — and deepening risk aversion across Asia. South Korea's KOSPI fell 8.3 per cent. Japan's Nikkei lost 3.9 per cent. The MSCI Asia ex-Japan index tumbled 3.5 per cent.

India's Sensex closed 719 points lower at 73,524. The Nifty 50 settled at 23,123, down 1.04 per cent, marking its lowest close in two months.

## Why IT Got Hit the Hardest

Indian IT companies derive the majority of their revenue from American clients. When US tech spending slows or when the narrative around AI shifts from "growth at any cost" to "show me the returns," Indian IT firms — which sell the consulting, implementation and maintenance services around these technologies — feel it immediately.

The AI spending boom of 2024 and 2025 lifted Indian IT stocks disproportionately. Investors priced in the assumption that every major Western enterprise would need Indian IT services to deploy generative AI across their operations. That assumption is now being questioned.

Wipro's decline to a three-year low is partly idiosyncratic — the stock fell after its buyback record date, and the company has underperformed peers on revenue growth. But the scale of the IT selloff is sector-wide. Devarsh Vakil, head of prime research at HDFC Securities, attributed the damage to "heavy losses in the semiconductor industry" following the strong jobs report, which "increased the likelihood of a Federal Reserve interest rate hike."

Higher US interest rates hurt Indian IT in two ways. They reduce the present value of future earnings — punishing growth stocks — and they strengthen the dollar, which paradoxically helps IT revenue in rupee terms but reduces the appetite of foreign portfolio investors for Indian equities.

## The NRI Dimension

For the diaspora, this matters beyond portfolio returns.

Hundreds of thousands of NRIs work at Wipro, TCS, Infosys and HCL — either directly in India or at their US, UK and Canadian offices. Many hold company stock, ESOPs or Indian IT mutual funds as part of their investment portfolio. Some hold these stocks in Indian demat accounts as part of a broader India allocation.

The question now is whether Friday's crash was a correction within a secular AI trend — a healthy reset before the next leg up — or the beginning of something more structural.

The US market offered an early answer on Monday. The Nasdaq recovered about 1 per cent in early trading, and the PHLX Semiconductor Index jumped more than 5 per cent as investors bought the dip. But this came with a caveat: Treasury yields continued to rise, oil remained above $96, and the CPI data due Wednesday is expected to show US inflation surging above 4 per cent for the first time since 2023.

## What to Watch

There are three numbers to monitor in the coming weeks.

The first is US CPI on Wednesday. If inflation prints above expectations, rate hike fears will solidify and tech stocks will face another round of selling.

The second is Q4 FY26 earnings from Indian IT companies, which begin reporting later this month. Revenue guidance and deal pipeline commentary will reveal whether the AI spending thesis is intact or whether clients are pulling back.

The third is FPI flows. Foreign portfolio investors have already pulled more money out of India in 2026 than in all of 2025. If the dollar strengthens further on rate hike expectations, that exodus will accelerate.

Indian IT remains a well-run sector with strong balance sheets and global client relationships. But the narrative that lifted these stocks — that AI would create an unstoppable wave of technology spending — is being tested for the first time. For NRIs holding Indian IT stocks, the next month will reveal whether the thesis holds or whether a recalibration is overdue."""
}

# Insert all articles
print("Inserting articles...")
print()
print("Article 1: Survodutide / Fatty Liver")
insert_article(article1)
print()
print("Article 2: Laughter / Brain Development")
insert_article(article2)
print()
print("Article 3: Indian IT / AI Selloff")
insert_article(article3)
print()
print("Done!")
