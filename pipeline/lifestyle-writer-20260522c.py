#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-22 23:00 PDT run
2 articles:
  1. US extends Ebola travel ban to green card holders — NRI impact
  2. New 2026 cholesterol guidelines — South Asian heart disease paradox
"""

import os, json, uuid, re, requests, subprocess, time
from datetime import datetime, timezone

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260523"):
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

def sb_patch(table, filter_str, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filter_str}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: US Extends Ebola Travel Ban to Green Card Holders
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "The US Just Extended Its Ebola Travel Ban to Green Card Holders. For NRIs, This Is Unprecedented — and It Should Be a Wake-Up Call."
art1_subheadline = "For the first time, lawful permanent residents who have been in the DRC, Uganda, or South Sudan are barred from entering the United States. India has launched airport screening. The WHO has declared an international emergency. And the 2026 FIFA World Cup in the US is five weeks away."
art1_slug = make_slug("us-ebola-travel-ban-green-card-holders-nri-india-airport")
art1_category = "lifestyle-health"

art1_body = """Green card holders have historically been untouchable when it comes to US entry restrictions. The CDC's COVID-era Title 42 order did not apply to them. President Trump's various travel bans did not apply to them. For the millions of Indian-Americans who hold lawful permanent resident status, the green card has always meant one thing above all else: the right to come home.

That changed on Friday.

The US Centers for Disease Control and Prevention announced that it is temporarily banning the entry of lawful permanent residents who have been in the Democratic Republic of Congo, Uganda, or South Sudan within the previous 21 days, citing concerns over the rapidly spreading Ebola outbreak. The order was issued under Title 42 of US public health law, the same authority used during the COVID-19 pandemic to restrict border crossings.

"Applying this authority to lawful permanent residents for a limited period of time provides a balance between protecting public health and managing emergency response resources," the CDC said in a statement.

This is not a theoretical concern for most Indian-Americans. But the precedent it sets — and the broader Ebola situation it reflects — should concern every NRI with a green card, a pending immigration case, or summer travel plans that route through international hubs.

## The Outbreak: Bigger Than the Numbers Suggest

The current Ebola outbreak is caused by the Bundibugyo strain, a rare variant of the virus that went undetected for weeks after the first known death on April 20, 2026. Authorities initially tested for the more common Zaire strain and came up negative, allowing the virus to spread silently until a suspected super-spreader event — possibly a funeral — in early May accelerated transmission across the DRC and into Uganda.

As of this week, the WHO reports approximately 600 suspected cases and 139 suspected deaths. But the London-based MRC Centre for Global Infectious Disease Analysis estimates the actual case count may already exceed 1,000. "The true magnitude remains uncertain," it said.

The WHO has declared the outbreak a Public Health Emergency of International Concern — the highest level of alarm the organisation can issue. It has also raised the risk of the Bundibugyo strain becoming a national outbreak in the DRC to "very high."

There is no approved vaccine for the Bundibugyo strain. The most promising experimental shot is estimated to be six to nine months away from clinical trials.

## What the US Has Done

The US response has escalated rapidly over the past week. On May 18, the Department of Homeland Security and CDC imposed a 30-day ban prohibiting non-US passport holders from the DRC, Uganda, and South Sudan from entering the country. US citizens and green card holders were initially exempt.

On May 21, the State Department announced that all US-bound travellers who have been in any of the three countries within 21 days must enter exclusively through Washington Dulles International Airport for enhanced CDC screening. Delta Air Lines has begun postponing travel for non-US nationals from the affected countries. The State Department has paused visa issuance for anyone who has been in the three countries within 21 days of planned travel.

And on Friday, May 23, the CDC extended the ban to green card holders — crossing a line that not even the COVID pandemic prompted.

The rationale is straightforward: Ebola's incubation period is up to 21 days, and an infected person can appear completely healthy during that window. Unlike COVID, Ebola is not airborne — it spreads through direct contact with bodily fluids — but its case fatality rate for the Bundibugyo strain is estimated at 25 to 35 per cent, far higher than any respiratory virus.

## What India Has Done

India has no confirmed Ebola cases. But Delhi's Indira Gandhi International Airport issued a public health advisory on May 21, citing a Directorate General of Health Services notice, for passengers arriving from or transiting through the DRC, Uganda, and South Sudan.

The advisory instructs travellers showing symptoms — fever, fatigue, headache, muscle pain, vomiting, diarrhoea, unexplained bleeding, or sore throat — to immediately report to airport health officers before immigration clearance. Any traveller developing symptoms within 21 days of arrival must seek immediate medical care and disclose their travel history.

The Union Health Ministry has confirmed enhanced surveillance at all international airports. The India-Africa Health Summit, which was scheduled for this period, has been postponed due to Ebola concerns.

## Why NRIs Should Pay Attention

For the vast majority of Indian-Americans, the direct risk of Ebola exposure is negligible. The affected countries are not on typical NRI travel routes. But there are several reasons this outbreak matters beyond the immediate travel ban.

**The green card precedent is historic.** This is the first time in modern US immigration history that lawful permanent residents have been subject to a Title 42 entry ban. Immigration attorneys are already flagging the implications: if public health authorities can bar green card holders from entry for Ebola, the legal framework now exists to do so for future outbreaks. For the hundreds of thousands of Indian green card holders who travel internationally — particularly those who visit India for extended periods and transit through Middle Eastern or African hubs — this creates a new category of risk to monitor.

**The FIFA World Cup complicates everything.** The 2026 FIFA World Cup begins in the United States on June 11, less than three weeks away. The Congo national football team is already rearranging its travel plans due to the Ebola restrictions. Tens of thousands of travellers from across Africa will be converging on US cities for the tournament. The intersection of mass international travel and an active Ebola outbreak is precisely the scenario that epidemiologists have warned about for years.

**Airport screening has limits.** Former CDC chief Robert Redfield has publicly expressed concern that the outbreak could become a "very significant pandemic." While the current consensus is that Ebola is unlikely to spread widely in countries with strong healthcare infrastructure, the Bundibugyo strain's novelty — no approved vaccine, no proven treatment, and a long period of undetected spread — means the situation is more uncertain than any Ebola outbreak since 2014.

**Summer travel season is here.** Millions of NRIs are currently in various stages of booking, planning, or executing summer trips to India. Those whose itineraries include layovers in African transit hubs — Addis Ababa, Nairobi, Johannesburg — or who have business connections in East Africa should review their routes. While the current restrictions apply specifically to the DRC, Uganda, and South Sudan, the geographic spread of the outbreak could trigger additional restrictions on short notice.

## What to Do

If you are a green card holder with any recent or planned travel to or through the DRC, Uganda, or South Sudan, you are currently barred from entering the United States. Contact your immigration attorney immediately.

If you are a US citizen travelling internationally, you are still permitted to enter the US, but you will be routed through Washington Dulles for enhanced screening if you have been in any of the three countries within 21 days. Factor this into your travel plans.

If you are travelling to India this summer, check whether your route includes transit through any East African hub. Most India-bound flights from the US route through the Middle East (Dubai, Doha, Abu Dhabi) or Europe (London, Frankfurt), which are not affected. But some itineraries, particularly from the US East Coast, include connections through Addis Ababa (Ethiopian Airlines) or Nairobi — review these carefully.

Monitor the WHO and CDC advisories. The situation is evolving daily. The 30-day ban was issued on May 18 and escalated to green card holders within five days. Further escalation — including potential restrictions on travellers transiting through additional countries — cannot be ruled out.

The Ebola virus has killed more people in Africa than any single infectious disease outbreak since HIV/AIDS. For NRIs, the direct health risk remains low. But the policy risk — the precedent of barring green card holders from entry, the cascading travel restrictions, the intersection with the World Cup — is a signal worth taking seriously."""

art1_sources = [
    "https://www.reuters.com/business/healthcare-pharmaceuticals/us-extends-ebola-travel-ban-green-card-holders-2026-05-23/",
    "https://www.livemint.com/news/india/attention-flyers-delhi-airport-issues-advisory-as-ebola-virus-death-toll-surges-to-100-11779342831555.html",
    "https://www.devdiscourse.com/article/business/3377285-update-2-as-ebola-cases-rise-americans-returning-from-drc-must-enter-us-via-washington-airport",
    "https://statnews.com/2026/05/19/u-s-issues-ebola-travel-restrictions-first-infected-american-identified/",
    "https://www.cdc.gov/media/releases/2026/s0519-ebola-transcript.html",
]

print("=== Article 1: US Ebola Ban Extended to Green Card Holders ===")
print(f"Word count: {len(art1_body.split())}")

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
    "tags": ["Ebola", "green card", "travel ban", "NRI", "CDC", "Title 42", "WHO", "PHEIC", "DRC", "Uganda", "Delhi airport", "FIFA World Cup", "immigration"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "First-ever Title 42 ban on green card holders — historic precedent for NRI permanent residents. US Ebola travel restrictions escalating during peak summer travel season. India screening at Delhi airport. FIFA World Cup in US starting June 11 adds mass-travel risk.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: New Cholesterol Guidelines & South Asian Heart Disease Paradox
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "America's New Cholesterol Guidelines Say Start Screening at 30. For South Asians, That May Already Be Too Late."
art2_subheadline = "The 2026 ACC/AHA dyslipidemia guidelines recommend earlier, more aggressive cholesterol treatment. But a landmark study of 2,700 South Asian adults found they develop heart disease risk factors a full decade before other Americans — despite reporting healthier diets and more exercise. The paradox is finally getting the attention it deserves."
art2_slug = make_slug("cholesterol-guidelines-2026-south-asian-heart-disease-lpa")
art2_category = "lifestyle-health"

art2_body = """At age 45, nearly one in three South Asian men in the United States already has prediabetes. One in four has hypertension. Nearly four in five have abnormal cholesterol or triglyceride levels. And they report eating healthier diets, drinking less alcohol, and exercising at rates comparable to or better than white, Black, Hispanic, and Chinese Americans.

This is the South Asian heart disease paradox — and the new 2026 cholesterol management guidelines from the American College of Cardiology and the American Heart Association are the closest the medical establishment has come to acknowledging that what works for most Americans does not work the same way for South Asians.

The guidelines, published in the Journal of the American College of Cardiology, represent the most significant update to cholesterol management in nearly a decade. They recommend that doctors begin broader cardiovascular prevention starting at age 30 — a sharp departure from previous frameworks that focused primarily on 10-year risk in patients over 40. They lower LDL cholesterol targets to 70 mg/dL for high-risk individuals and 55 mg/dL for very high-risk patients. And critically, they recommend universal testing for lipoprotein(a), or Lp(a) — a genetically inherited cholesterol particle that has long been identified as a particular risk factor for South Asians.

For the Indian diaspora, these guidelines are not just medical news. They are a policy shift that validates what cardiologists treating South Asian patients have argued for years: the standard American risk calculator has been systematically underestimating heart disease risk in this population.

## The Numbers That Should Alarm You

A landmark longitudinal study led by Northwestern Medicine, published earlier this year in the Journal of the American Heart Association, followed 2,700 adults and found that South Asians develop cardiovascular risk factors far earlier and at far higher rates than any other ethnic group in the United States.

At age 45, South Asian men had a prediabetes prevalence of 31 per cent — compared to 4 per cent for white men, 10 per cent for Black men, 10 per cent for Hispanic men, and 13 per cent for Chinese men. By age 55, both South Asian men and women were at least twice as likely to have developed diabetes as white adults.

South Asian men at 45 had higher rates of hypertension (25 per cent) than white men (18 per cent), Hispanic men (10 per cent), and Chinese men (6 per cent). They had higher rates of dyslipidemia — abnormal cholesterol and triglyceride levels — than Black men: 78 per cent versus 61 per cent.

South Asian women showed the same pattern. By 45, nearly one in five had prediabetes — roughly double the rate of white, Black, Hispanic, and Chinese women.

"The mismatch between healthier lifestyle behaviours and clinical risk was surprising," said Dr. Namratha Kandula, the study's senior author and professor at Northwestern University Feinberg School of Medicine. "This paradox tells us we're missing something fundamental to what is driving this elevated risk among South Asians."

## The Lp(a) Factor

The new guidelines' recommendation for universal Lp(a) testing is particularly significant for South Asians. Lipoprotein(a) is a genetically determined particle — you cannot meaningfully lower it through diet, exercise, or standard statin therapy. It is measured once in a lifetime and does not fluctuate with lifestyle changes.

South Asians have among the highest Lp(a) levels of any ethnic group worldwide. Studies have consistently shown that elevated Lp(a) is a major contributor to the excess cardiovascular risk observed in this population — the risk that persists even after controlling for standard factors like diet, weight, and exercise.

Until the 2026 guidelines, Lp(a) testing was not part of standard screening. Most South Asian Americans have never had their Lp(a) measured. Many primary care physicians have never ordered the test. The new guidelines give it a formal recommendation for the first time, which means insurance coverage should follow — though implementation will take time.

If you are South Asian and have never had your Lp(a) tested, this is the single most actionable takeaway from the new guidelines. Ask your doctor at your next visit. If your Lp(a) is elevated, it does not change your diet or exercise plan — but it significantly changes your risk profile and may warrant earlier statin therapy or more aggressive LDL targets.

## Why Standard Risk Calculators Fail South Asians

The American Heart Association's PREVENT risk calculator, which the new guidelines incorporate, is a significant improvement over the older Pooled Cohort Equations. But even PREVENT has limitations when applied to South Asian patients.

The fundamental problem is one of data. Most cardiovascular risk models were built on cohorts that either excluded South Asians entirely or included them in numbers too small to generate population-specific risk curves. The MASALA study — the only large, long-term cardiovascular cohort specifically studying South Asians in the US — has been producing data since 2010, but its findings are still being integrated into clinical practice guidelines.

The result is a systematic blind spot. A 42-year-old South Asian man with an LDL of 140 mg/dL, no diabetes, normal blood pressure, and a healthy lifestyle might score as "low risk" on a standard calculator. But the MASALA data suggest his actual risk profile is closer to that of a 52-year-old white man with the same numbers — because South Asians develop atherosclerosis, the plaque buildup that leads to heart attacks, a full decade earlier than the general population.

The new guidelines address this partly by recommending coronary artery calcium (CAC) scans — imaging that can detect silent plaque buildup regardless of what the calculator says. For South Asians who score as "borderline" or "intermediate" risk, a CAC scan can reveal whether disease is already developing and tip the treatment decision toward intervention.

## What the Diaspora Gets Wrong About Heart Health

There is a persistent belief in many South Asian families that vegetarianism is inherently protective against heart disease. It is not. While plant-based diets can lower certain risk factors, the South Asian vegetarian diet is often high in refined carbohydrates — white rice, naan, sweets — and cooked in ghee or oil in quantities that push caloric intake well above what the body needs. The metabolic consequences of this dietary pattern are compounded by a genetic predisposition toward visceral fat — fat stored around organs rather than under the skin — which is metabolically active and drives insulin resistance, inflammation, and cardiovascular disease.

Prior data from the MASALA study show that South Asians have more visceral fat than other population groups, even at a normal or low BMI. Other studies show that this fat pattern starts in childhood and persists across generations, regardless of migration status or adopted Western dietary habits.

The implication is uncomfortable but important: a South Asian person with a "normal" BMI of 23 may carry the same metabolic risk as a white person with a BMI of 28. Standard BMI cutoffs, designed for European populations, systematically undercount obesity risk in South Asians. The WHO has acknowledged this by recommending lower BMI thresholds for Asian populations — but most US clinicians still use the standard cutoffs.

## What NRIs Should Do Now

The 2026 guidelines are not just for cardiologists. They are designed to be implemented by primary care physicians — the doctors most NRIs actually see. Here is what the guidelines mean in practical terms for South Asian patients.

**Get your Lp(a) tested.** This is a one-time blood test. If your Lp(a) is elevated (above 50 mg/dL or 125 nmol/L), it permanently changes your risk category. Tell your doctor you want it included in your next lipid panel. If your insurance does not cover it, it typically costs $30 to $50 out of pocket.

**Request a CAC scan if you are over 40.** If you are over 40, male, and South Asian — or over 45 and female — ask about a coronary artery calcium scan. A score of zero is highly reassuring. A score above zero, even in the absence of symptoms, may warrant statin therapy under the new guidelines. CAC scans cost $75 to $300 out of pocket and are increasingly covered by insurance.

**Know your LDL target.** The new guidelines set LDL targets at 70 mg/dL for high-risk patients and 55 mg/dL for very high-risk patients. If you have elevated Lp(a), a family history of heart disease, diabetes, or a CAC score above zero, your target may be lower than you think. Many South Asian patients are currently being undertreated because their doctors are using outdated targets of 100 or 130 mg/dL.

**Talk to your parents.** Heart disease kills more Indians — in India and in the diaspora — than any other cause. If your parents are in India and over 50, encourage them to get screened. The new guidelines were written for the American healthcare system, but the underlying science applies globally. India's own burden of cardiovascular disease is staggering: heart attacks in Indians occur, on average, a decade earlier than in Western populations and account for roughly 28 per cent of all deaths in the country.

**Do not assume vegetarianism is protection.** If you or your family follows a vegetarian diet, audit its actual composition. High intake of refined carbohydrates, fried foods, and cooking fats can negate the cardiovascular benefits of avoiding meat. The MASALA study found that despite reporting healthier diets, South Asians still had the highest prevalence of metabolic risk factors — suggesting that "healthy" as self-reported does not always translate to "healthy" as measured.

Globally, South Asians make up roughly one-quarter of the world's population but account for approximately 60 per cent of heart disease patients worldwide. In the United States, where they are among the fastest-growing demographic groups, they develop atherosclerosis up to a decade earlier than the general population.

The 2026 guidelines will not fix this disparity overnight. But for the first time, the medical establishment is saying what South Asian cardiologists have been saying for years: start screening earlier, treat more aggressively, and stop assuming that standard risk tools capture the full picture for this population. The data is clear. The tools are available. The question is whether South Asian patients — and their doctors — will use them."""

art2_sources = [
    "https://medicalxpress.com/news/2026-05-cholesterol-guidelines-aim-heart-disease.html",
    "https://www.news-medical.net/news/20260211/South-Asian-adults-in-the-US-have-higher-prevalence-of-risk-factors-for-heart-disease.aspx",
    "https://www.ahajournals.org/doi/10.1161/JAHA.124.041221",
    "https://www.acc.org/Latest-in-Cardiology/Articles/2023/11/01/01/42/South-Asian-Cardiovascular-Health",
    "https://newsroom.heart.org/news/heart-disease-risk-factors-appeared-at-younger-age-among-south-asian-adults-in-the-u-s",
]

print("\n=== Article 2: Cholesterol Guidelines & South Asian Heart Disease ===")
print(f"Word count: {len(art2_body.split())}")

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
    "score_total": 87,
    "tags": ["cholesterol", "ACC", "AHA", "South Asian", "heart disease", "Lp(a)", "MASALA study", "dyslipidemia", "CAC scan", "NRI", "health guidelines", "statin", "cardiovascular"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "New 2026 cholesterol guidelines recommend screening from age 30 and universal Lp(a) testing — both critical for South Asians who develop heart disease a decade earlier than other groups. MASALA study shows South Asians have highest metabolic risk despite healthiest lifestyle reports.",
    "word_count": len(art2_body.split()),
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n=== Score Decay ===")
decay_resp = requests.patch(
    f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.0",
    headers={**HEADERS, "Prefer": "return=headers-only"},
    json={"score_total": "score_total - 1"},
    timeout=30,
)
# RPC approach for decay
decay_sql = """
UPDATE p2_articles
SET score_total = GREATEST(score_total - 1, 0)
WHERE status = 'published' AND score_total > 0
"""
# Use direct PATCH with computed column workaround
resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?select=id,score_total&status=eq.published&score_total=gt.0&limit=500",
    headers=HEADERS,
    timeout=30,
)
articles = resp.json() if resp.status_code == 200 else []
decayed = 0
for art in articles:
    old_score = art["score_total"]
    new_score = max(old_score - 1, 0)
    r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
        headers=HEADERS,
        json={"score_total": new_score},
        timeout=10,
    )
    if r.status_code < 300:
        decayed += 1
print(f"  Decayed {decayed}/{len(articles)} articles")


# ══════════════════════════════════════════════════════════════
# MARKETS REFRESH
# ══════════════════════════════════════════════════════════════

print("\n=== Markets Refresh ===")
MARKET_INDICES = [
    ("sensex", "BSE SENSEX", "^BSESN"),
    ("nifty", "NIFTY 50", "^NSEI"),
    ("sp500", "S&P 500", "^GSPC"),
    ("dow", "Dow Jones", "^DJI"),
    ("nasdaq", "NASDAQ", "^IXIC"),
    ("usdinr", "USD/INR", "USDINR=X"),
    ("gold", "Gold", "GC=F"),
]

market_data = []
for key, name, symbol in MARKET_INDICES:
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("chartPreviousClose", 0)
            change_pct = ((price - prev) / prev * 100) if prev else 0

            # Get historical for charts
            timestamps = data["chart"]["result"][0].get("timestamp", [])
            closes = data["chart"]["result"][0]["indicators"]["quote"][0].get("close", [])

            market_data.append({
                "key": key,
                "name": name,
                "symbol": symbol,
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "direction": "up" if change_pct >= 0 else "down",
                "updated": now,
            })
            print(f"  {name}: {price:,.2f} ({change_pct:+.2f}%)")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

if market_data:
    market_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "market-indices.json")
    os.makedirs(os.path.dirname(market_path), exist_ok=True)
    with open(market_path, "w") as f:
        json.dump(market_data, f, indent=2)
    print(f"  Wrote {len(market_data)} indices to market-indices.json")


# ══════════════════════════════════════════════════════════════
# MARKET CHARTS
# ══════════════════════════════════════════════════════════════

print("\n=== Market Charts ===")
CHART_RANGES = [("1d", "5m"), ("5d", "30m"), ("1mo", "1d"), ("1y", "1wk")]
chart_data = {}
for key, name, symbol in MARKET_INDICES:
    chart_data[key] = {}
    for rng, interval in CHART_RANGES:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={rng}&interval={interval}"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                result = data["chart"]["result"][0]
                timestamps = result.get("timestamp", [])
                closes = result["indicators"]["quote"][0].get("close", [])
                points = []
                for ts, c in zip(timestamps, closes):
                    if c is not None:
                        points.append({"t": ts, "v": round(c, 2)})
                chart_data[key][rng] = points
        except Exception as e:
            pass

chart_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "market-charts.json")
with open(chart_path, "w") as f:
    json.dump(chart_data, f)
print(f"  Wrote charts for {len(chart_data)} indices")


# ══════════════════════════════════════════════════════════════
# IPL STANDINGS
# ══════════════════════════════════════════════════════════════

print("\n=== IPL Standings ===")
try:
    ipl_url = "https://www.espncricinfo.com/series/ipl-2026-1473498/points-table-standings"
    r = requests.get(ipl_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    if r.status_code == 200:
        # Try to extract JSON data from the page
        import re as re2
        # Look for standings data in script tags
        json_match = re2.search(r'"standings":\s*(\[.*?\])', r.text)
        if json_match:
            print("  Found standings data in page")
        else:
            print("  IPL page loaded but standings extraction needs manual parsing")
    else:
        print(f"  IPL page returned {r.status_code}")
except Exception as e:
    print(f"  IPL standings: {e}")

# Try alternate source
try:
    ipl_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "ipl-standings.json")
    if os.path.exists(ipl_path):
        with open(ipl_path) as f:
            existing = json.load(f)
        print(f"  Existing IPL standings: {len(existing.get('teams', existing) if isinstance(existing, dict) else existing)} teams (keeping current)")
except Exception as e:
    print(f"  IPL check: {e}")


# ══════════════════════════════════════════════════════════════
# GIT COMMIT & PUSH
# ══════════════════════════════════════════════════════════════

print("\n=== Git Push ===")
repo_dir = os.path.join(os.path.dirname(__file__), "..")
os.chdir(repo_dir)

subprocess.run(["git", "add", "public/data/"], capture_output=True)
result = subprocess.run(
    ["git", "commit", "-m", "data: markets + charts refresh (23:00 PDT lifestyle writer)"],
    capture_output=True, text=True,
)
if result.returncode == 0:
    push = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ✗ Push failed: {push.stderr[:200]}")
else:
    print(f"  No changes to commit or commit failed: {result.stderr[:200]}")

print("\n✅ Lifestyle writer 23:00 PDT run complete")
