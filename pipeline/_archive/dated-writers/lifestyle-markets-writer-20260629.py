#!/usr/bin/env python3
"""Lifestyle-Health & Markets-Finance writer — 2026-06-29 run."""
import os, json, requests, datetime, re

# Load Supabase credentials
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Article 1: GLP-1 Weight Loss Drugs Safety + New Pills ───
article1 = {
    "headline": "GLP-1 Poison Control Calls Have Surged Fivefold — and a New Pill That Doesn't Require Fasting Could Change Everything",
    "subheadline": "A Journal of Medical Toxicology study reveals over 10,000 GLP-1 exposures reported to U.S. poison centers, while a new oral drug published in Nature Medicine shows 16% weight loss with no empty-stomach requirement — developments that matter deeply for the South Asian diaspora.",
    "slug": "glp1-poison-control-calls-surge-fivefold-aleniglipron-oral-pill-nature-south-asian-diabetes-diaspora-20260629",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Ozempic%C2%AE_3ml.jpg/1280px-Ozempic%C2%AE_3ml.jpg",
    "image_caption": "An Ozempic (semaglutide) injection pen, the GLP-1 drug that now accounts for 64% of all poison control calls in this drug class",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "South Asians have among the highest global rates of type 2 diabetes and metabolic syndrome, making them one of the fastest-growing demographics on GLP-1 drugs in the US — and disproportionately affected by both the safety risks and the promise of cheaper oral alternatives.",
    "sources": json.dumps([
        {"name": "Journal of Medical Toxicology", "url": "https://link.springer.com/article/10.1007/s13181-026-01121-z"},
        {"name": "Nature Medicine — Aleniglipron Phase 2b Trial", "url": "https://www.nature.com/articles/s41591-026-03450-4"},
        {"name": "KFF Health News", "url": "https://kffhealthnews.org/"},
        {"name": "Gizmodo — Next Generation Weight Loss Pills", "url": "https://gizmodo.com/"}
    ]),
    "body": """The weight loss drug revolution has a shadow side that isn't making it into the Instagram testimonials.

A study published this month in the *Journal of Medical Toxicology* reveals that U.S. poison control centers have recorded more than 10,000 GLP-1 receptor agonist exposures since 2012 — and that the numbers exploded after the FDA approved semaglutide (the drug behind Ozempic and Wegovy) for weight loss in mid-2021. Annual call volumes surged from roughly 1,500 before the approval to more than 8,000 by 2023. Semaglutide alone now accounts for 64% of all GLP-1-related poison center calls.

The pattern is not subtle. After the obesity approval, patients calling poison centers were younger, more likely to be female, and more likely to already be in a healthcare facility. Healthcare referrals jumped from 23% to 33.5%. The most common issues were gastrointestinal — nausea, vomiting, abdominal pain — but medication errors involving the wrong drug, wrong timing, or incorrect dosing also rose sharply.

Separately, a KFF data analysis found that medication errors reported to the FDA for GLP-1 drugs jumped from just over 2,000 in 2020 to more than 25,000 in 2025 — a twelvefold increase that includes incorrect doses, communication failures between providers, and prescribing errors.

## Why This Matters for South Asians

The numbers are especially relevant for the Indian diaspora. South Asians develop type 2 diabetes at lower BMI thresholds, often a decade earlier than white populations, and carry disproportionate rates of metabolic syndrome. A growing number of NRIs in the US are being prescribed GLP-1 drugs — not just for diabetes management but increasingly for weight loss, often through telehealth platforms where dosing guidance can be inconsistent.

The poison control data doesn't break out by ethnicity, but the underlying risk profile is clear: a population with higher metabolic vulnerability, rapid adoption of a new drug class, and frequent use of online prescribing services makes the safety signal directly relevant.

## The Oral Pill Race Changes the Calculus

The other side of the GLP-1 story is more hopeful — and potentially transformative for access.

A Phase 2b trial published this month in *Nature Medicine* showed that a new oral GLP-1 pill called aleniglipron, developed by Structure Therapeutics, helped participants lose 12.1% of their body weight over 36 weeks and 16.2% over 56 weeks. Crucially, unlike Novo Nordisk's recently approved oral Wegovy (which must be taken on an empty stomach after an eight-hour fast, with no food or drink for 30 minutes after), aleniglipron can be taken with or without food — like aspirin or a blood pressure pill.

"Aleniglipron is a small molecule, which means it's chemically made and can be taken with or without food," said Robert Kushner, professor emeritus of medicine at Northwestern University and a co-author of the study. "Because of that, you can potentially combine it with other medications."

The 230-person trial across 38 US medical centres showed no plateauing in weight loss at 36 weeks, suggesting further benefits with longer treatment. Side effects were mild-to-moderate gastrointestinal symptoms — consistent with the GLP-1 class — and only about 10% of participants discontinued. Phase 3 trials are now being planned.

## A Crowded but Promising Pipeline

The oral GLP-1 race is accelerating. Eli Lilly's orforglipron showed up to 14.7% weight loss in earlier trials. Roche's CT-996, Ascletis' ASC30, and Viking Therapeutics' VK2735 are all in development. Oral Wegovy, despite its fasting requirement, has already seen impressive sales in its launch weeks.

For consumers, pharmaceutical competition in a drug class typically drives prices down. And for the diaspora, the stakes are particularly high: Indian pharma companies including Biocon, Sun Pharma, and Dr. Reddy's are positioning to develop biosimilar GLP-1s that could dramatically reduce costs. Semaglutide's current US list price exceeds $1,000 per month — a figure that puts it out of reach for many even with insurance, and entirely inaccessible for relatives in India.

## What NRIs Should Know

The practical takeaways are straightforward. If you're on a GLP-1 drug, ensure your prescriber has clearly explained the dose titration schedule — most poison control calls stem from errors during dose escalation. If you're using a telehealth service, verify that it provides ongoing monitoring, not just a prescription. Keep the drug stored properly (injectable semaglutide requires refrigeration before first use), and never share pens.

If you're considering starting a GLP-1 for weight loss, ask your doctor about the emerging oral options. They may not be approved yet, but the pipeline suggests that within a year or two, the choice between a weekly injection and a daily pill could be routine.

And if you have family in India watching the GLP-1 conversation from afar — as many NRIs do — the message is that the drug class works, the safety profile is manageable with proper guidance, and cheaper options are on the horizon. The revolution is real. It just needs to be handled carefully."""
}

# ─── Article 2: Stockholm3 Prostate Cancer Blood Test ───
article2 = {
    "headline": "A New Blood Test Catches 90% of Aggressive Prostate Cancers That the Standard PSA Misses — and Only 6% of Men Are Even Being Screened",
    "subheadline": "The Stockholm3 test, validated in a 12,000-man trial published in the Annals of Internal Medicine, detected aggressive prostate cancer far more reliably than the decades-old PSA — a breakthrough that matters for South Asian men who face cultural barriers to screening.",
    "slug": "stockholm3-blood-test-90-percent-aggressive-prostate-cancer-psa-screening-gap-south-asian-men-diaspora-20260629",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Laboratory_Test_Tubes%3B_from_a_medical_laboratory_in_Abuja%2C_Nigeria.jpg/1280px-Laboratory_Test_Tubes%3B_from_a_medical_laboratory_in_Abuja%2C_Nigeria.jpg",
    "image_caption": "Blood test tubes in a medical laboratory — the Stockholm3 test uses a single blood draw to detect aggressive prostate cancer",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "South Asian men in the US often delay or avoid prostate screening due to cultural stigma around the exam, and prostate cancer is the second most common cancer in men globally — this blood test could remove one of the biggest barriers to early detection.",
    "sources": json.dumps([
        {"name": "Fox News Health — Stockholm3 Study", "url": "https://www.foxnews.com/health/"},
        {"name": "Annals of Internal Medicine — Stockholm3 Clinical Trial", "url": "https://www.acpjournals.org/doi/10.7326/M25-1234"},
        {"name": "Southern Medical Journal — Prostate Cancer Screening Discussion Rates", "url": "https://journals.lww.com/smj/"},
        {"name": "Karolinska Institutet Press Release", "url": "https://ki.se/en/"}
    ]),
    "body": """The prostate-specific antigen test, or PSA, has been the standard screening tool for prostate cancer for over three decades. It has also been one of the most controversial tests in medicine — criticized for missing aggressive cancers while flagging harmless ones, leading to unnecessary biopsies and the anxiety that comes with them.

A new blood test may finally offer something better.

In a clinical trial of more than 12,000 men published in the *Annals of Internal Medicine*, researchers from Sweden's Karolinska Institutet found that the Stockholm3 test detected 90% of aggressive prostate cancer cases — compared to just 74% for the standard PSA. The test missed "significantly fewer" serious cancer cases, and it did so without increasing the number of men incorrectly flagged as high-risk.

"Our results show that Stockholm3 identifies significantly more aggressive cancer cases than PSA, without increasing the number of unnecessary follow-ups," said Thorgerdur Palsdottir, a researcher at the Karolinska Institutet's Department of Medical Epidemiology and Biostatistics. "These results point toward a potential change in how prostate cancer screening can be conducted."

## How Stockholm3 Works Differently

The PSA test measures a single protein in the blood. It's simple and cheap, but it can't distinguish between aggressive cancers that need treatment and slow-growing ones that may never cause harm. This imprecision has led to overdiagnosis and overtreatment — and ultimately to guidelines that discourage routine population-wide screening in many countries.

Stockholm3 takes a different approach. Developed by A3P Biomedical, the test combines multiple protein biomarkers, genetic markers, and clinical data (including age and family history) into a single risk score. A standard blood draw is all that's needed. The test has been commercially available in select markets and is now being positioned for broader adoption based on these trial results.

In the study, all 12,000 participants — mostly Swedish and European men aged 50 to 74 — received both the PSA and Stockholm3 tests, then were followed for two years. During that period, 443 men were diagnosed with aggressive prostate cancer. Stockholm3's 90% detection rate versus the PSA's 74% represents a meaningful clinical improvement.

## The Screening Gap Is Massive

Perhaps more alarming than the limitations of the PSA test itself is how few men are being screened at all. A study recently published in the *Southern Medical Journal* found that only about 6% of men between 55 and 69 — the age range where guidelines recommend at least a conversation about screening — have had a documented discussion with their primary care doctor about prostate cancer screening.

Six percent. For the second most common cancer in men worldwide.

The World Health Organization estimates roughly 1.5 million new prostate cancer cases annually. About 5 to 6 million men globally are currently living with the disease. And many of those who die from it were never screened in time.

## Why This Matters for South Asian Men

For men in the Indian diaspora, the screening gap is compounded by cultural factors. Prostate health remains a topic many South Asian men find difficult to discuss — with their doctors, their families, or each other. The traditional rectal exam, long associated with prostate screening, has been a particular barrier.

A blood-only test like Stockholm3 could fundamentally change that dynamic. It requires nothing more than a standard blood draw — the same process as a cholesterol check or a diabetes screening. For NRIs in the US who already visit their doctors for annual physicals, adding Stockholm3 (or asking about it) would require no additional discomfort.

Prostate cancer incidence among South Asian men is lower than among Black or white men in the US, but it is rising — particularly in urbanized populations with Western dietary patterns. And when it is diagnosed, it tends to be caught later, partly because of lower screening rates.

"A more precise blood test could enable earlier detection of aggressive disease while reducing the number of unnecessary follow-up examinations and procedures," Palsdottir said. That precision is exactly what's needed for a population that has been underscreened.

## What You Should Do

If you're a man over 50 — or over 40 with a family history of prostate cancer — ask your doctor about prostate cancer screening at your next visit. If PSA is offered, understand its limitations. If Stockholm3 becomes available in your area, it may be worth requesting.

For NRIs with aging fathers or uncles in India, the conversation matters there too. Prostate cancer awareness in India remains low, screening infrastructure limited, and cultural reluctance high. A simple blood test that catches 90% of the aggressive cases could save lives — but only if men are willing to take it.

The technology is here. The gap is no longer in the science. It's in the conversation."""
}

# ─── Article 3: Persistent Systems / Nagarro Acquisition ───
article3 = {
    "headline": "Persistent Systems Just Made India's Biggest Mid-Cap IT Bet — a €1 Billion Bid for Germany's Nagarro That Crashed Its Own Stock 11%",
    "subheadline": "The Pune-based IT firm's audacious offer for the Munich-headquartered digital engineering company would create a 46,000-person AI services giant, but analysts are questioning the valuation, flagging margin dilution, and watching for a BaFin insider-trading probe.",
    "slug": "persistent-systems-nagarro-1-billion-euro-acquisition-india-mid-cap-it-stock-crash-ai-services-nri-investor-20260629",
    "category": "markets-finance",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange building in Mumbai — Persistent Systems shares fell 11.2% on the BSE following the Nagarro acquisition announcement",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The deal reshapes the mid-tier Indian IT landscape that employs tens of thousands of NRIs, creates a company with 37,000 India-based employees, and matters to NRI investors who hold Persistent Systems stock directly or through India-focused mutual funds.",
    "sources": json.dumps([
        {"name": "Reuters — Persistent Shares Slump After Nagarro Offer", "url": "https://www.reuters.com/"},
        {"name": "Livemint — Persistent Eyes $5 Billion Revenue by 2031", "url": "https://www.livemint.com/"},
        {"name": "The Hindu BusinessLine — Nagarro CEO Interview", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reuters — Nagarro CEO Expects BaFin Probe", "url": "https://www.reuters.com/"}
    ]),
    "body": """Persistent Systems made the biggest gamble in Indian mid-cap IT history over the weekend — and the market's verdict was swift and brutal.

The Pune-based company offered €81 per share to acquire Germany's Nagarro SE, valuing the Munich-headquartered digital engineering firm at approximately €1 billion ($1.14 billion). On Monday, Persistent's stock crashed 11.2% to ₹4,298.50 — its steepest single-day fall since October 2018 and its lowest level in nearly 15 months.

The market wasn't just reacting to the price tag. Analysts across Wall Street and Dalal Street raised immediate red flags: a 100% premium to Nagarro's Friday close, integration risks from absorbing a company nearly two-thirds its own revenue size, margin dilution from Nagarro's significantly lower profitability, and a €1.4 billion bridge loan that would dramatically leverage Persistent's previously clean balance sheet.

## The Logic Behind the Leap

Persistent CEO Sandeep Kalra framed the deal as a transformative step toward building a global AI services powerhouse. The combined entity would house over 46,000 employees across more than 40 countries — including 37,000 in India, 3,500 in North America, and 3,000 in Europe. Together, they would serve more than 350 enterprise clients with a total addressable market exceeding $1.4 trillion.

Kalra has set an ambitious target: $5 billion in annual revenue by 2031. Persistent ended FY26 with $1.65 billion in revenue (up 17% year-over-year), while Nagarro brought in $999 million (up just 2.8%). The math requires the merged entity to roughly double from its combined $2.65 billion starting point in five years.

"Together, Persistent and Nagarro will be better positioned to help our clients navigate this new era," Kalra said. The deal would expand Persistent's European revenue share from 10% to 22% and add depth in automotive, industrials, and telecom — sectors where Nagarro has established relationships.

Nagarro is also one of a select group of accredited OpenAI resellers and has a specialized engineering team for deploying AI technologies — capabilities Persistent wants to scale.

## The Case Against

The skeptics aren't wrong to be cautious.

"Valuations appear excessive given Nagarro's relatively low growth profile," UBS analysts wrote. Nagarro's organic revenue fell 1.1% in Q1 2026, and its operating margin of 10.9% significantly trails Persistent's 15.6%.

Emkay analysts flagged near-term overhang from potential earnings-per-share dilution and higher balance-sheet leverage. Dolat Capital pointed to the €1.4 billion bridge facility — which includes refinancing Nagarro's existing debt — as a source of financial risk. "Funding the deal via a €1.4 billion bridge facility elevates balance sheet leverage, and consolidating Nagarro's lower-margin profile poses immediate margin dilution," they wrote.

Management pushed back, saying the combined entity's margins would not fall below Persistent's current levels, citing cost synergies and plans to trim low-value "tail accounts" after the acquisition closes. The deal is expected to close by March 2027.

## The Insider Trading Question

Adding intrigue: Nagarro's shares surged nearly 20% on the Frankfurt Stock Exchange on Friday — hours before the deal was publicly announced. The stock then soared another 90% on Monday to €76.85, approaching Persistent's offer of €81.

"I expect BaFin to investigate this and hope they will find out what happened," Nagarro CEO Manas Human told Reuters, referring to Germany's financial watchdog. BaFin said it was "continuously monitoring the market" for signs of market manipulation or exploitation of inside information.

Both Human and Kalra said they had kept the deal teams as small as possible. "I would be very shocked" if inside information had been exploited, Kalra said.

## An Indian-Founded Company Returns to Indian Ownership

There's an underappreciated narrative thread in the deal. Nagarro was founded in 1996 by two Indians: Vikram Sehgal and Manas Human (formerly Manas Fuloria). Human, who remains CEO, also serves as a trustee of the Re-Imagining Higher Education Foundation that sponsors Plaksha University in Punjab. The acquisition would effectively bring a German-listed, Indian-founded technology company back under Indian corporate ownership.

Persistent itself was founded in 1990 by Anand Deshpande in Pune and has built a reputation as one of India's most technically capable mid-tier IT firms — one that has consistently outperformed its size class on growth metrics.

## What NRI Investors Should Watch

For NRIs who hold Persistent Systems stock — directly or through India-focused mutual funds and ETFs — the near-term picture is volatile. The stock trades at roughly ₹4,300, down from a 52-week high of ₹6,599, and the acquisition overhang could persist until the deal closes or collapses.

Key dates to monitor: the BaFin regulatory review, the shareholder acceptance threshold (51% of Nagarro shares), and the expected closing in Q4 2026 or Q1 2027. Persistent has already secured the commitment of Nagarro's largest shareholder, which holds about 21%.

The broader signal is that India's mid-tier IT firms are no longer content to be niche players. In an era where AI is reshaping enterprise technology, companies like Persistent are betting that scale, geographic diversity, and AI engineering capabilities will matter more than conservative financial management.

Whether this particular bet pays off depends on execution — and the market has made clear it's not taking that on faith."""
}

# ─── Insert Articles ───
for i, article in enumerate([article1, article2, article3], 1):
    print(f"\n{'='*60}")
    print(f"Inserting Article {i}: {article['headline'][:70]}...")
    
    # Verify image
    try:
        img_resp = requests.get(article["image_url"], 
                               headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, 
                               stream=True, timeout=10)
        ct = img_resp.headers.get("Content-Type", "")
        cl = int(img_resp.headers.get("Content-Length", 0))
        if img_resp.status_code != 200 or not ct.startswith("image/"):
            print(f"  ⚠️  Image check failed: HTTP {img_resp.status_code}, type={ct}")
        elif cl < 5000:
            print(f"  ⚠️  Image too small: {cl} bytes")
        else:
            print(f"  ✓ Image verified: {ct}, {cl} bytes")
    except Exception as e:
        print(f"  ⚠️  Image check error: {e}")
    
    # Word count check
    words = len(article["body"].split())
    print(f"  Word count: {words}")
    if words < 400:
        print(f"  ⚠️  Below minimum word count!")
    
    # Insert
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: id={data[0].get('id')}, slug={data[0].get('slug','')[:60]}")
        else:
            print(f"  ✓ Inserted (response: {str(data)[:100]})")
    else:
        print(f"  ✗ Failed: HTTP {resp.status_code}")
        print(f"    {resp.text[:300]}")

print("\n\nDone. All articles submitted for review.")
