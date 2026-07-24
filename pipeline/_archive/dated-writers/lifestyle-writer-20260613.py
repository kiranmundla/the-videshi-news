#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-13 batch."""

import json, os, uuid, subprocess, sys
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article):
    """Insert a single article into Supabase."""
    import requests
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"  ✓ Inserted: {article['slug']} (id: {data[0]['id'] if data else 'ok'})")
        return True
    else:
        print(f"  ✗ FAILED: {article['slug']} — {resp.status_code}: {resp.text[:200]}")
        return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ============================================================
# ARTICLE 1: Parkinson's Gene Therapy (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Single Brain Injection Restored Dopamine in 87% of Parkinson's Patients. The Gene Therapy Era May Have Arrived.",
    "subheadline": "A Phase 1 trial of BBM-P002, a dual-target gene therapy, showed sustained motor improvement after 12 months with no serious side effects — offering hope to the estimated one million Indians living with Parkinson's and to diaspora families watching from abroad.",
    "slug": "parkinsons-gene-therapy-bbm-p002-dopamine-phase-1-trial-south-asian-diaspora-20260613",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17483868/pexels-photo-17483868.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A digital rendering of the human brain, illustrating the neural pathways targeted by gene therapy",
    "image_attribution": "Pexels",
    "diaspora_angle": "Parkinson's disease affects an estimated one million Indians and is rising sharply in the diaspora; gene therapy breakthroughs will reach high-income countries first, leaving NRI families navigating a two-tier access system.",
    "sources": json.dumps([
        {"name": "Nature Medicine", "url": "https://www.nature.com/articles/s41591-026-04262-4"},
        {"name": "Archyde", "url": "https://www.archyde.com/bbm-p002-gene-therapy-shows-promise-in-parkinsons-phase-1-trial-highlights-safety-motor-improvements/"},
        {"name": "World Health Organization", "url": "https://www.who.int/news-room/fact-sheets/detail/parkinson-disease"}
    ]),
    "body": """For decades, treating Parkinson's disease has meant managing a slow, inevitable decline. Levodopa — the gold-standard drug since the 1960s — temporarily replenishes dopamine but loses its grip over time, leaving patients with worsening tremors, stiffness, and the cruel motor fluctuations that define late-stage disease. A new trial, published this week in Nature Medicine, suggests the first real alternative may be approaching.

BBM-P002, a dual-target gene therapy developed by a consortium including the University of Oxford and Sweden's Karolinska Institute, was injected into the brains of 15 early-stage Parkinson's patients in a Phase 1 trial. After 12 months, 87 per cent showed measurable improvement on the Unified Parkinson's Disease Rating Scale — the clinical benchmark for motor function. None developed dyskinesia, the involuntary movements that plague long-term levodopa users. None suffered cognitive decline. No serious adverse events were reported.

"This is the first time we've seen a gene therapy not only halt symptom progression but also show functional recovery," said Dr Lars Forsgren, lead neurologist at the Karolinska Institute and co-author of the study.

## How It Works — and Why It Is Different

The therapy takes a fundamentally different approach from existing treatments. Instead of flooding the brain with a dopamine precursor and hoping for conversion, BBM-P002 delivers two genes directly into the putamen — the brain region most affected by Parkinson's. One gene encodes tyrosine hydroxylase, which converts the amino acid tyrosine into L-DOPA. The other encodes aromatic L-amino acid decarboxylase, which converts L-DOPA into dopamine itself. Together, they restore the full dopamine production pathway in a single surgical infusion.

This dual-target mechanism is what separates BBM-P002 from earlier gene therapy attempts, which delivered only one enzyme and produced inconsistent results. By rebuilding both steps of the biosynthesis chain, the therapy enables surviving neurons to manufacture dopamine on their own — potentially for years after a single treatment.

The comparison with existing options is stark. Levodopa's efficacy declines after five to 10 years. Deep brain stimulation requires implanted hardware and periodic battery replacements. BBM-P002, if it holds up in larger trials, could offer durable relief from a one-time procedure.

## The Scale of the Problem — and the South Asian Dimension

Parkinson's disease is the fastest-growing neurological disorder in the world. Globally, more than 10 million people live with it, and incidence has risen 20 per cent over the past decade. India alone accounts for an estimated one million cases, the second-highest national burden after China. Among the Indian diaspora in the United States, the United Kingdom, and Canada, the disease carries a particular weight: families separated by continents often watch a parent's or grandparent's decline from thousands of miles away, coordinating care across time zones and healthcare systems that do not speak to each other.

South Asian populations also face specific biological vulnerabilities. Studies have identified genetic variants in the LRRK2 and GBA genes that appear at elevated frequencies in certain South Asian subgroups and are associated with higher Parkinson's risk. Environmental exposures — including pesticides used in Indian agriculture — are another established risk factor that connects homeland and diaspora communities.

## The Access Question

If BBM-P002 progresses to approval, it will almost certainly arrive in high-income countries first. The projected cost per patient — between 200,000 and 300,000 US dollars — places it alongside other gene therapies in the upper reaches of pharmaceutical pricing. Phase 2 trials, enrolling 60 to 80 patients across the US, UK, and Sweden, are expected to begin in 2027. If those succeed, Phase 3 could launch by 2029, with potential FDA approval by 2032.

For NRI families, this creates a familiar dilemma. A parent diagnosed in Delhi or Chennai may not have access to a therapy available at a medical centre in Boston or London. "We're seeing a two-tier system emerge," warned Dr Maria Del Park of the WHO's Neurological Disorders Unit. "Gene therapies will first be available in high-income countries, leaving low-resource settings behind unless global funding mechanisms are put in place."

The National Institutes of Health estimates that Parkinson's costs the American healthcare system 25 billion dollars annually. If BBM-P002 reduces the years patients spend on escalating medication regimens and in assisted care, the economic case for broader access could strengthen quickly.

## What Comes Next

The therapy is not a cure. It targets dopamine deficiency — the downstream consequence of Parkinson's — rather than the upstream cause: the misfolding of alpha-synuclein protein and the neuroinflammation that progressively destroys brain cells. "This is a critical step, but not the finish line," Dr Forsgren said. "The holy grail remains a therapy that targets alpha-synuclein itself."

For now, patients and families should focus on evidence-based management. Regular aerobic exercise has been shown to improve dopamine sensitivity. Clinical trial participation remains one of the few ways to access experimental treatments before commercial availability — the Parkinson's Foundation reports that 40 per cent of trial enrollees gain such access.

But the significance of this moment should not be understated. For the first time, a gene therapy for Parkinson's has demonstrated both safety and functional recovery in humans. The road to approval is long. The road to equitable global access is longer. But the direction of travel has changed."""
})

# ============================================================
# ARTICLE 2: Agatston-2.0 Heart Scan AI Upgrade (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Heart Scan That Saved Millions of Lives Just Got Its First AI Upgrade. For South Asians, It Could Not Have Come Sooner.",
    "subheadline": "Agatston-2.0, published in the American Journal of Preventive Cardiology, uses artificial intelligence to detect hidden coronary calcium in patients whose conventional scans showed a clean zero — a finding that matters disproportionately for a community with two to four times the average cardiovascular risk.",
    "slug": "agatston-2-ai-coronary-calcium-score-upgrade-south-asian-heart-disease-risk-20260613",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/13176452/pexels-photo-13176452.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A CT scanner used for cardiac imaging in a modern hospital facility",
    "image_attribution": "Pexels",
    "diaspora_angle": "South Asians suffer heart attacks at younger ages and higher rates than almost any other ethnic group; an AI upgrade that catches early coronary calcium missed by conventional scans could save thousands of diaspora lives.",
    "sources": json.dumps([
        {"name": "American Journal of Preventive Cardiology", "url": "https://doi.org/10.1016/j.ajpc.2026.101698"},
        {"name": "HeartLung Corporation press release", "url": "https://www.wcia.com/business/press-releases/ein-presswire/919291405/after-36-years-coronary-calcium-score-gets-its-first-major-upgrade-agatston-2-0-led-by-heartlung-ai-and-dr-agatston/"},
        {"name": "Multi-Ethnic Study of Atherosclerosis (MESA)", "url": "https://www.mesa-nhlbi.org/"}
    ]),
    "body": """If you are a South Asian adult living in the United States, the United Kingdom, or Canada, there is a reasonable chance your doctor has ordered — or will order — a coronary artery calcium scan. The test, which uses a low-dose CT to measure calcified plaque in your heart's arteries, has been one of preventive cardiology's most powerful tools for more than three decades. A score of zero has meant reassurance: your near-term risk of a heart attack is very low.

A landmark study published this week in the American Journal of Preventive Cardiology says that reassurance may have been premature for some patients. And given what we know about South Asian cardiovascular biology, the implications are significant.

## What Agatston-2.0 Changes

The original Agatston score, introduced in 1990 by Dr Arthur Agatston and colleagues, revolutionised cardiovascular prevention by giving physicians a noninvasive, quantifiable measure of coronary artery disease. It has been validated in hundreds of studies and is recommended by every major cardiology society. But it was built on technical assumptions from the late 1980s — a fixed 130-Hounsfield-unit density threshold, 2.5-to-3-millimetre CT slice thickness — that can miss very small, low-density, or fragmented plaques.

Agatston-2.0, developed by a multi-institutional team led by Dr Morteza Naghavi of HeartLung Corporation and Dr Agatston himself, replaces those rigid thresholds with AI-based coronary segmentation and continuous voxel-wise calcium quantification. In plain terms: instead of applying a binary cutoff to each CT slice, the AI examines every three-dimensional pixel of the coronary arteries and assigns a continuous calcium measurement.

The results are striking. Among 3,965 participants from the Multi-Ethnic Study of Atherosclerosis and the Framingham Heart Study who had a conventional CAC score of zero, Agatston-2.0 detected coronary calcium in 862 — nearly 22 per cent. Those individuals had roughly double the long-term coronary heart disease incidence: 7.7 per cent over 20 years, compared with 3.8 per cent for those whose AI-enhanced score also came back at zero.

"These findings refine the Power of Zero," said Dr Naghavi. "A conventional CAC score of zero remains extremely valuable, but Agatston-2.0 can distinguish a truly clean zero from a zero that may contain early subthreshold calcified disease."

## Why This Matters More for South Asians

The epidemiology is well established but still underappreciated. South Asians develop coronary artery disease a decade earlier than white populations, suffer heart attacks at higher rates, and die from cardiovascular disease more frequently — even after adjusting for traditional risk factors like cholesterol, blood pressure, and diabetes. The MASALA study, the first large US longitudinal study of South Asian cardiovascular health, has documented that South Asians carry more coronary calcium at younger ages and have higher rates of subclinical atherosclerosis than other ethnic groups.

This creates a specific problem with the conventional CAC score. A 40-year-old South Asian man whose scan returns a zero may be told he has a clean bill of cardiovascular health. But the MASALA data suggest his baseline risk is already elevated by ethnicity, metabolic profile, and family history. If Agatston-2.0 can detect early, subthreshold calcification that the conventional score misses, it could identify exactly the patients who fall through the current screening gap.

The study drew participants from MESA, which includes a multiethnic cohort, and Framingham, which is predominantly white. South Asian-specific validation data will be critical. But the direction is clear: a more sensitive calcium score could disproportionately benefit the population that needs it most.

## What Patients Should Know

Agatston-2.0 is not yet available in clinical practice. It requires regulatory validation, integration into CT software, and acceptance by insurance systems. The study's authors describe it as a proof of concept that needs replication in additional cohorts before it can become a new clinical standard.

For South Asian patients today, the practical guidance remains unchanged but urgent. Ask your physician about a coronary artery calcium scan if you are over 40, have a family history of heart disease, or carry metabolic risk factors — even if your cholesterol panel looks normal. If your CAC score comes back at zero, take the reassurance but do not treat it as a guarantee. Continue managing the modifiable risks: exercise, diet, blood pressure, blood sugar, and — if your physician recommends it — statin therapy.

The broader significance of Agatston-2.0 lies in what it signals about the future of cardiovascular screening. The test that defined preventive cardiology for a generation was built on technology and assumptions from the 1980s. Its AI-driven successor could catch what was always there but invisible — early disease hiding behind a reassuring number. For a community that has long known its heart disease risk is different, that upgrade could not have come sooner."""
})

# ============================================================
# ARTICLE 3: BlackRock + Lighthouse Canton India thesis (markets-finance)
# ============================================================
articles.append({
    "headline": "BlackRock and Lighthouse Canton Say India Has Been 'Over-Punished.' The Contrarian Case for NRI Investors Is Getting Louder.",
    "subheadline": "After a record 30 billion dollars in foreign outflows, the world's largest asset manager and a major wealth firm argue that India's lack of a direct AI play is an advantage — not a liability — and that the worst of the selloff may be over.",
    "slug": "blackrock-lighthouse-canton-india-over-punished-nri-investors-contrarian-case-20260613",
    "category": "markets-finance",
    "vertical": "markets",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A stock market trading screen displaying financial data and price movements",
    "image_attribution": "Pexels",
    "diaspora_angle": "NRI investors who paused SIPs or sold India positions during the record $30 billion outflow are now hearing from BlackRock and Lighthouse Canton that the selloff has gone too far — a signal that could reshape diaspora portfolio decisions.",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "7Globe / Reuters", "url": "https://www.7globe.in/ai-oil-worries-have-over-punished-india-masked-long-term-investment-case-blackrock-says/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "body": """For most of 2026, the story of Indian equities has been a story of retreat. Foreign portfolio investors have pulled a record 30 billion dollars from the market. The Nifty 50 and the Sensex are down 11 and 13 per cent respectively. The heavyweight IT index has been hammered 27 per cent on fears of AI-led disruption. The Iran war, now in its fourth month, has spiked oil prices, pressured the rupee, and raised the spectre of wider supply shocks for the world's third-largest oil importer.

Against this backdrop, two of the world's most prominent investment voices have stepped forward with the same message: India has been punished too hard.

## BlackRock: "The Rotation Has Gone Too Far"

BlackRock, the world's largest asset manager with more than 14 trillion dollars under management, said this week that India's equity market has been "over-punished" for lacking a direct AI play and for its vulnerability to elevated oil prices. Natasha Sarkaria, the firm's EMEA investment strategy lead for wealth, told Reuters that India remains one of BlackRock's highest-conviction medium- to long-term emerging market trades.

"As long as India's GDP grows between 6 and 7 per cent, that's a nice sweet spot for the economy to keep growing, keep expanding," Sarkaria said.

The firm is positioned constructively — not at an "outright overweight" but with clear conviction that the selloff has created an entry point. BlackRock's India thesis rests on demographics, infrastructure spending, the strength of the financial sector, and what Sarkaria calls "derivative AI stories" — companies that benefit indirectly from the global AI infrastructure build-out without being semiconductor manufacturers themselves.

"It doesn't mean there are no derivative AI stories in India," Sarkaria said, pointing to industrials, materials, and utilities that serve as the picks-and-shovels suppliers to the AI revolution.

## Lighthouse Canton: "The Advantage of Absence"

On Friday, Abhay Laijawala, chief investment officer for India at Lighthouse Canton, a global wealth management firm with more than five billion dollars in assets, echoed BlackRock's assessment — and sharpened the argument further.

Foreign outflows from India may have "largely run their course," Laijawala told Reuters. The record capital flight, he argued, was driven by global investors piling into South Korea and Taiwan for their semiconductor and memory chip exposure. Those two markets have now overtaken India in market capitalisation. But concentration at that scale creates its own risk.

"When sector concentration reaches such levels, investors tend to fatally underprice the possibility that a risk could emerge from outside the core business model," Laijawala said.

South Korea and Taiwan have already begun logging foreign outflows in June, suggesting investors are trimming exposure on concerns about crowded positioning. India, by contrast, offers a deep and diversified listed universe tied to the next phase of AI spending — power infrastructure, data centres, electrical equipment, cooling systems, engineering, and capital goods.

"We have plenty of picks and shovels," Laijawala said. "The absence of the AI trade would be India's advantage."

## What Friday's Rally Told Us

The thesis got an immediate test on Friday, when signals of a possible US-Iran peace deal sent oil prices tumbling and triggered the strongest rally in Indian equities in two months. The Nifty jumped 1.99 per cent to 23,622.90. The Sensex surged 2.3 per cent to 75,527.95. More than seven lakh crore rupees were added to the market capitalisation of BSE-listed companies in a single session.

Brent crude fell four per cent below 87 dollars a barrel — a near two-month low. Oil marketing companies, airlines, tyre makers, and cement producers led the rally. Financials got a late boost from what traders described as likely foreign inflows, the first meaningful reversal after weeks of sustained selling.

For the week, India's blue-chip indices snapped a two-week losing streak, advancing 1.1 and 1.7 per cent respectively. Kotak Mahindra Bank, ICICI Bank, and HDFC Bank were among the top weekly gainers, rising between 3.4 and 6.9 per cent, buoyed by the central bank's recent easing of overseas borrowing rules for lenders.

## The NRI Calculation

For the millions of NRI investors who maintain equity exposure to India — through direct stock holdings, mutual fund SIPs, or NRE and NRO-linked portfolio accounts — the past five months have been a test of conviction. Many paused or reduced their systematic investment plans. Some booked losses and rotated into US-dollar assets or global tech funds that were outperforming.

The message from BlackRock and Lighthouse Canton is not that the pain is over. Near-term volatility is likely. Higher oil prices, rupee weakness, and rising input costs will feed through to corporate profits over the next two quarters. India's IT sector — the segment most NRI investors have historically over-weighted — remains under pressure from AI disruption fears and hot US inflation data that has fuelled expectations of a Federal Reserve rate hike by year-end.

But the medium-term signal is clear. Two of the most sophisticated institutional investors in global markets are telling their clients that the India trade has been oversold. BlackRock projects low double-digit earnings growth for MSCI India this year. India's economy grew a stronger-than-expected 7.8 per cent in the March quarter. The Reserve Bank of India has cut its fiscal 2027 growth forecast to 6.6 to 6.9 per cent — a downward revision, but still the fastest-growing major economy in the world.

For NRI investors who stayed in, the case for patience is strengthening. For those who left, the case for re-entry is being made by the people who manage the most money on earth."""
})

# ============================================================
# INSERT ALL ARTICLES
# ============================================================
print(f"\n{'='*60}")
print(f"Inserting {len(articles)} articles at {now}")
print(f"{'='*60}\n")

success = 0
for a in articles:
    if insert_article(a):
        success += 1

print(f"\n{'='*60}")
print(f"Done: {success}/{len(articles)} articles inserted successfully")
print(f"{'='*60}")
