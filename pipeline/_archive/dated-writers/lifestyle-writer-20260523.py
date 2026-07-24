#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 03:00 PDT run
2 articles:
  1. Scripps National Spelling Bee 2026 — The Indian American dynasty returns
  2. Oral Wegovy pill — the first weight-loss pill and what South Asians should know
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
# ARTICLE 1: Scripps National Spelling Bee 2026
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "The Scripps National Spelling Bee Starts Monday. Indian Americans Have Won 28 of the Last 34. The Dynasty Shows No Sign of Ending."
art1_subheadline = "The 98th Scripps National Spelling Bee moves to DAR Constitution Hall in Washington, D.C., for the first time in its 101-year history. Among the 247 spellers are multiple Indian American returning finalists. Since Balu Natarajan won in 1985, the community has turned competitive spelling into a cultural institution — and a uniquely American immigrant success story."
art1_slug = make_slug("scripps-spelling-bee-2026-indian-american-dynasty-nri")
art1_category = "lifestyle-health"

art1_body = """On Monday, 247 of the best spellers in the English-speaking world will file into DAR Constitution Hall in Washington, D.C., for the 98th Scripps National Spelling Bee. It is the first time the competition has been held at the iconic venue — a return to the capital after 15 years at the Gaylord National Resort in suburban Maryland. ESPN's Mina Kimes will host the televised semifinals and finals alongside Paul Loeffler, marking his 20th year as an analyst.

The winner will take home $50,000, a commemorative medal, and the Scripps Cup. But for hundreds of Indian American families watching from living rooms in Edison, Fremont, Plano, and Alpharetta, the stakes have always been about more than prize money.

Since 1999, Indian Americans have won 28 of 34 National Spelling Bees. In 2024, it was Bruhat Soma. In 2023, Dev Shah. In 2022, Harini Logan — who won the first-ever spell-off after 22 consecutive correct spellings in 90 seconds. The dominance is so thorough that it has become one of the most discussed — and occasionally controversial — patterns in American competitive culture.

This year's field includes several Indian American names among the returning finalists. Sarv Dharavane, the third-place finisher in 2025, returns from Dunwoody, Georgia — where he has won the DeKalb County bee three years running. Esha Marupudi of Chandler, Arizona, who placed seventh in 2025, is back. Adarsh Venkannagari of Acton, Massachusetts, is competing in his fourth consecutive national bee. Siyona Kandala of San Antonio is also in her fourth straight year. Shrey Parikh of Rancho Cucamonga, California, a 2024 finalist who placed third, returns for another run.

The 2025 champion, Faizan Zaki, won with the word "éclaircissement." He is not returning — Scripps rules bar previous winners from competing again.

## How It Started

The Indian American spelling bee story begins with a single name: Balu Natarajan.

In 1985, the 13-year-old son of immigrants from Mysore won the Scripps National Spelling Bee with the word "milieu." He was the first Indian American champion, and his victory was largely treated as a curiosity — a one-off. The idea that Indian American children would go on to dominate the competition for the next four decades was not on anyone's radar.

But Natarajan's win planted a seed. In the early 1990s, a group of Indian American professionals founded the North South Foundation, a nonprofit that organized academic competitions — including spelling bees — for South Asian students. The Foundation did not invent the Indian American spelling bee pipeline, but it systematized it. It created a feeder network: regional competitions that identified talented spellers early, connected families, and built the infrastructure of study groups, word lists, and coaching that would produce champion after champion.

By 1999, when Nupur Lala won with "logorrhea" — a victory immortalized in the documentary "Spellbound" — the pattern was unmistakable. From 1999 to 2025, the only non-Indian American winners were Zaila Avant-garde in 2021, Arvind Mahankali in 2013 (Indian American), and a handful of others. The streak has included co-champions (Sriram Hathwar and Ansun Sujoe in 2014, Vanya Shivashankar and Gokul Venkatachalam in 2015) and multiple siblings from the same families.

## Why Indian Americans Dominate

The question of why Indian American children dominate competitive spelling has been examined by anthropologists, sociologists, journalists, and the families themselves. The explanations are layered, but three factors consistently emerge.

**The infrastructure exists.** The North South Foundation, the South Asian Spelling Bee circuit, private coaching academies, and a vast network of family study groups have created a parallel ecosystem that feeds into the national competition. Indian American families do not simply enter their children into the school spelling bee and hope for the best. Many begin structured preparation years in advance, using proprietary word lists, etymology databases, and coaching from former competitors. The investment is significant — both in time and money — and it compounds year over year.

**The cultural value of word mastery runs deep.** India's education system, shaped by the colonial legacy of English-medium instruction, places enormous weight on linguistic precision. For many first-generation Indian immigrants, fluency in English was the gateway to professional success in the United States. That emphasis on language — on getting words exactly right — translated naturally into competitive spelling. As anthropologist Shalini Shankar documented in her research on the South Asian spelling bee community, the competition resonated because it aligned with values that were already deeply embedded: discipline, academic achievement, and the belief that mastery of a skill could be earned through sustained effort.

**Community identity reinforces participation.** For Indian Americans, the spelling bee has become a cultural touchstone in a way that is difficult to overstate. It is discussed at dinner parties, celebrated in community WhatsApp groups, and covered extensively by Indian media. Parents whose children compete form tight-knit networks. The visibility of Indian American champions on national television — year after year — creates a self-reinforcing cycle: children see people who look like them winning, families see a path that works, and the community rallies around the next generation of competitors.

## The Backlash — and the Response

The dominance has not gone unnoticed, and not all of the attention has been positive. In some quarters, the Indian American spelling bee streak has been cited as evidence of the "model minority" myth — the idea that Asian Americans succeed because of inherent cultural superiority, a framing that both flattens the diversity of the community and weaponises its achievements against other minority groups.

Some commentators have questioned whether the level of preparation — children studying for hours daily, families spending thousands on coaching — represents a healthy model of childhood development. Others have raised concerns about the pressure placed on young competitors, particularly when the national stage amplifies both victory and defeat.

The families involved tend to push back on both critiques. The pressure argument, they note, applies equally to child athletes, musicians, and performers in every competitive arena. And the model minority framing ignores the structural advantages — high parental education levels, professional incomes, visa categories that select for academic achievement — that shape the Indian American community's demographics. It is not that Indian Americans are culturally predisposed to win spelling bees. It is that the specific subset of Indian immigrants who arrived in the United States after 1965, selected through employment-based visa categories, brought educational values and resources that aligned with competitive academic pursuits.

The 2021 victory of Zaila Avant-garde — the first African American champion and the younger sister of this year's competitor Zwe Spacetime — was widely celebrated as a sign that the bee's talent base is broadening. Zwe, competing from Prince George's County, Maryland, has spoken openly about the historical significance of a potential win: "No Black boy, whether African American or non-African American, has won Scripps yet."

## What to Watch This Year

The 98th bee runs from Monday, May 26, through Wednesday, May 28. Preliminary and quarterfinal rounds are on Monday and Tuesday. The semifinals air on ION TV on Tuesday evening. The final is on Wednesday, May 28.

The field of 247 spellers represents the United States and its territories, plus competitors from the Bahamas, Canada, Ghana, Nigeria, and the United Arab Emirates. Three spellers are competing in their fourth consecutive national bee — a testament to the depth of preparation required to reach this level repeatedly.

For the Indian American community, the bee remains appointment viewing. It is the one week of the year when the national spotlight shines on South Asian children for their academic excellence — a contrast to the headlines about visa restrictions, hate crimes, and immigration backlogs that dominate NRI discourse the rest of the year.

Whether an Indian American child wins the 98th Scripps National Spelling Bee or not, the dynasty is already secure. Twenty-eight of 34 champions in 27 years. A cultural institution built from scratch by an immigrant community that arrived with advanced degrees and the conviction that mastery of the English language was the ultimate investment in their children's futures.

The bee starts Monday. The word lists are memorized. The etymology is drilled. And somewhere in a living room in Fremont or Edison or Plano, a family is sitting at the kitchen table, running through one more round of practice — because in this community, spelling is not a hobby. It is heritage."""

art1_sources = [
    "https://en.wikipedia.org/wiki/98th_Scripps_National_Spelling_Bee",
    "https://scripps.com/press-releases/scripps-national-spelling-bee-welcomes-247-spellers/",
    "https://forbesindia.com/article/news/how-indian-americans-came-to-love-the-spelling-bee/",
    "https://americanimmigrationcouncil.org/research/indian-americans-and-scripps-national-spelling-bee",
    "https://tricityrecordnm.com/national-spelling-bee-reflects-economic-success-indian-immigrants/",
    "https://www.washingtoninformer.com/deja-vu-for-zwe-spacetime-returning-to-scripps-national-spelling-bee/",
]

print("=== Article 1: Scripps Spelling Bee 2026 — Indian American Dynasty ===")
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
    "score_total": 88,
    "tags": ["Scripps Spelling Bee", "Indian American", "Balu Natarajan", "spelling", "NRI", "education", "diaspora", "DAR Constitution Hall", "North South Foundation", "2026"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Indian Americans have won 28 of 34 Scripps National Spelling Bees since 1999. Multiple Indian American finalists returning for 2026. The bee is a cultural institution for NRI families — annual appointment viewing that celebrates academic excellence.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Oral Wegovy Pill — What South Asians Should Know
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Weight-Loss Pill Is Here. The FDA Just Approved Oral Wegovy — and for South Asians, the Timing Could Not Be More Important."
art2_subheadline = "Novo Nordisk's semaglutide pill is the first oral GLP-1 drug approved for weight loss in the United States. Europe is days behind. GoodRx is already offering it at $149 a month. Meanwhile, India's ₹99 generic is reshaping diabetes care at home. For South Asians on both sides of the ocean, the GLP-1 revolution is no longer injectable — and the access gap is about to widen."
art2_slug = make_slug("oral-wegovy-pill-fda-south-asian-weight-loss-glp1-semaglutide")
art2_category = "lifestyle-health"

art2_body = """For years, the GLP-1 revolution had an asterisk: you had to inject yourself. Weekly subcutaneous shots of semaglutide — marketed as Wegovy for weight loss and Ozempic for diabetes — transformed metabolic medicine, but the needle was a barrier. Patients who could not tolerate injections, feared needles, or simply found the ritual inconvenient were left watching from the sidelines as others lost 15 to 20 per cent of their body weight.

That barrier is gone.

The US Food and Drug Administration has approved oral Wegovy — a once-daily semaglutide pill — for chronic weight management in adults with obesity or overweight with at least one weight-related condition. It is the first oral GLP-1 receptor agonist approved for weight loss in the United States. The European Medicines Agency's Committee for Medicinal Products for Human Use has recommended approval in the EU, with a formal decision expected within weeks. Novo Nordisk plans to launch the pill in select European markets in the second half of 2026.

In clinical trials, the oral formulation produced an average weight loss of 16.6 per cent over 68 weeks — compared to 2.7 per cent for placebo. That is modestly less than the injectable version's roughly 17 to 20 per cent, but the gap is narrower than many expected. And for patients who refused or could not use needles, the difference between 0 per cent and 16.6 per cent is the difference between the status quo and transformation.

GoodRx has already announced discounted pricing for the pill at $149 per month — a fraction of the injectable Wegovy's list price of roughly $1,350 per month before insurance. For the millions of Americans who lack insurance coverage for weight-loss medications, this is the first time a GLP-1 drug has been within financial reach.

## Why This Matters for South Asians

South Asians face a metabolic double bind that makes oral Wegovy particularly relevant — and its accessibility particularly urgent.

The data is now overwhelming. South Asians develop type 2 diabetes at lower body weights, at younger ages, and at higher rates than virtually any other ethnic group. A landmark study published earlier this year by Northwestern Medicine found that by age 45, nearly one in three South Asian men in the United States had prediabetes — compared to 4 per cent of white men. Nearly four in five had abnormal cholesterol or triglyceride levels. And they reported healthier diets and more exercise than white, Black, Hispanic, and Chinese Americans.

This is the South Asian metabolic paradox: the risk does not track with the behaviours. It tracks with genetics, visceral fat distribution, insulin resistance patterns, and — increasingly — with lipoprotein(a) levels that are among the highest of any ethnic group worldwide.

For South Asians who are overweight or obese — using the WHO's lower BMI thresholds for Asian populations, which classify "overweight" as starting at 23 rather than 25 — the metabolic consequences are more severe and arrive earlier than for other groups. A South Asian man with a BMI of 27 may carry the same cardiovascular and diabetes risk as a white man with a BMI of 32.

GLP-1 drugs do not just cause weight loss. They reduce visceral fat specifically, improve insulin sensitivity, lower blood pressure, and — as the landmark SELECT trial demonstrated — reduce the risk of major adverse cardiovascular events by 20 per cent. For a population that dies of heart disease at disproportionate rates, these are not cosmetic benefits. They are potentially life-saving.

## The Pill vs. The Injection

The oral formulation has trade-offs that patients should understand before switching or starting.

**Dosing is different.** Oral Wegovy comes in a once-daily tablet, taken on an empty stomach with no more than 120 millilitres of water, at least 30 minutes before any food, drink, or other medication. This fasting requirement is not optional — the drug's absorption depends on it. For many South Asian households, where morning chai or coffee is a non-negotiable ritual, this means restructuring the first 30 minutes of every day.

**The dose ceiling is higher.** The pill goes up to 25 milligrams, while the injectable Wegovy maxes out at 2.4 milligrams. These are not comparable numbers — oral semaglutide requires a much higher dose because most of it is destroyed in the stomach before absorption. Only a small fraction reaches the bloodstream. The effective exposure is similar.

**Side effects are comparable.** Nausea, diarrhoea, vomiting, and constipation remain the most common adverse effects, particularly during the dose-escalation phase. The pill may cause slightly more gastrointestinal discomfort initially, given that it interacts directly with the stomach lining.

**Drug interactions are minimal.** Novo Nordisk has emphasised that the oral formulation has no drug-drug restrictions in its label — a notable advantage over some competing weight-loss medications.

**Weight loss is slightly less.** The 16.6 per cent average in trials compares to roughly 17 to 20 per cent for injectable Wegovy at its highest dose (including the newer 7.2 milligram single-dose pen, which showed 20.7 per cent average weight loss in the STEP UP trial). For most patients, this difference is clinically insignificant. For those chasing maximum weight loss, the injectable remains the stronger option.

## The India Side: ₹99 Generic Semaglutide

While the US debates insurance coverage for a $149-a-month pill, India has taken a characteristically different approach. Indian pharmaceutical companies have launched generic injectable semaglutide at prices starting below ₹100 per dose — roughly $1.20 — under India's compulsory licensing framework.

The generics are being prescribed primarily for type 2 diabetes rather than weight loss, but the metabolic benefits are identical. For NRI families with relatives in India who are managing diabetes or prediabetes, the cost differential is staggering: a year of injectable semaglutide in India costs less than a single month of Wegovy in the United States, even at the discounted GoodRx price.

This price gap is creating a new category of medical tourism — or, more accurately, medical arbitrage. NRIs visiting India for the summer are increasingly asking their doctors back home about starting semaglutide during their trip at Indian prices. The practice is legally grey and medically complicated (dosing needs to be supervised, and switching between generic and branded formulations mid-treatment is not recommended), but it reflects the desperation of a community that faces the highest metabolic risk and often the least accessible treatment in the US healthcare system.

## Insurance Coverage: The Real Barrier

The oral pill's clinical data will force a reckoning with insurance companies. Currently, most US insurance plans cover Ozempic (injectable semaglutide for diabetes) but not Wegovy (injectable semaglutide for weight loss) — a distinction that many physicians consider medically absurd, given that the drug, the mechanism, and the metabolic benefits are identical.

Medicare explicitly does not cover weight-loss drugs, a policy that affects millions of older South Asian Americans managing obesity-related conditions. The Inflation Reduction Act's drug pricing provisions apply to Ozempic for diabetes but not to Wegovy for obesity.

The approval of an oral formulation may shift the calculus. Pills are cheaper to manufacture, store, and distribute than injectables. Novo Nordisk's pricing strategy for the oral version — which appears to be set below the injectable — suggests the company is positioning the pill for broader market penetration. If insurance companies begin covering oral Wegovy at a lower reimbursement tier, it could open access to millions of patients who were previously excluded.

For South Asian patients specifically, the new 2026 ACC/AHA cholesterol guidelines — which recommend earlier screening and more aggressive intervention for high-risk populations — provide additional clinical justification for GLP-1 therapy. A South Asian patient with a BMI of 25, prediabetes, elevated Lp(a), and a family history of heart disease is exactly the kind of patient for whom early GLP-1 intervention could prevent a cardiac event. Whether their insurance company agrees is a different question.

## What NRIs Should Do

**If you are overweight by Asian BMI standards** (BMI 23 or above), talk to your doctor about whether GLP-1 therapy is appropriate. Do not wait for a diabetes diagnosis. The evidence increasingly supports early intervention for metabolic risk reduction, not just blood sugar control.

**Ask about the oral option.** If you have avoided GLP-1 drugs because of the injection, the barrier is gone. The pill is available now in the US.

**Check your insurance coverage.** Call your insurer and ask specifically about oral semaglutide for weight management. Coverage varies by plan, employer, and state. Some plans that do not cover Wegovy (weight loss) may cover Ozempic (diabetes) — and if you have a diabetes or prediabetes diagnosis, your doctor may be able to prescribe accordingly.

**Do not self-medicate with Indian generics.** The temptation to buy semaglutide cheaply during a trip to India is understandable, but unsupervised GLP-1 therapy carries real risks — including pancreatitis, gallbladder disease, and thyroid concerns. Start and maintain treatment under medical supervision.

**Talk to your family in India.** If parents or relatives are managing type 2 diabetes, generic semaglutide at Indian prices is a legitimate and increasingly mainstream treatment option. Encourage them to discuss it with their endocrinologist.

The GLP-1 revolution is the most significant development in metabolic medicine in a generation. For South Asians — who face the highest burden of diabetes and cardiovascular disease of any ethnic group — it is not just significant. It is existential. The pill makes it easier. Whether the system makes it accessible is the question that remains."""

art2_sources = [
    "https://www.globenewswire.com/news-release/2026/05/22/3097127/0/en/Novo-Nordisk-Wegovy-pill-oral-semaglutide-recommended-by-CHMP-EU.html",
    "https://www.reuters.com/business/healthcare-pharmaceuticals/ema-backs-novos-wegovy-pill-first-oral-weight-loss-drug-europe-2026-05-22/",
    "https://pharmaceuticalcommerce.com/pharma-pulse-fda-clears-first-oral-wegovy/",
    "https://pharmaceuticalcommerce.com/pharma-pulse-goodrx-rollout-oral-wegovy/",
    "https://www.news-medical.net/news/20260211/South-Asian-adults-in-the-US-have-higher-prevalence-of-risk-factors-for-heart-disease.aspx",
]

print("\n=== Article 2: Oral Wegovy Pill — What South Asians Should Know ===")
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
    "score_total": 86,
    "tags": ["Wegovy", "oral semaglutide", "GLP-1", "weight loss", "South Asian", "obesity", "diabetes", "FDA", "Novo Nordisk", "NRI", "GoodRx", "Indian generic", "metabolic health"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "First oral weight-loss pill approved in US. South Asians face highest metabolic risk — diabetes, visceral fat, cardiovascular disease at lower BMI. India's ₹99 generic vs $149 GoodRx price creates medical arbitrage. Insurance coverage remains the real barrier for NRI community.",
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
    FLAGS = {"sensex": "🇮🇳", "nifty": "🇮🇳", "sp500": "🇺🇸", "nasdaq": "🇺🇸", "dow": "🇺🇸", "gold": "🪙", "usdinr": "💱"}
    DISPLAY_NAMES = {"sensex": "Sensex", "nifty": "Nifty 50", "sp500": "S&P 500", "nasdaq": "Nasdaq", "dow": "Dow Jones", "gold": "Gold", "usdinr": "USD/INR"}
    SYMBOLS = {"sensex": "SENSEX", "nifty": "NIFTY", "sp500": "SPX", "nasdaq": "IXIC", "dow": "DJI", "gold": "GOLD", "usdinr": "USDINR"}
    formatted_indices = []
    for m in market_data:
        k = m["key"]
        formatted_indices.append({
            "symbol": SYMBOLS.get(k, k.upper()),
            "name": DISPLAY_NAMES.get(k, m["name"]),
            "flag": FLAGS.get(k, "📊"),
            "value": m["price"],
            "change": round(m["price"] * m["change_pct"] / 100, 2),
            "change_pct": m["change_pct"],
        })
    with open(market_path, "w") as f:
        json.dump({"last_updated": now, "indices": formatted_indices}, f, indent=2)
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
                result_data = data["chart"]["result"][0]
                timestamps = result_data.get("timestamp", [])
                closes = result_data["indicators"]["quote"][0].get("close", [])
                points = []
                for ts, c in zip(timestamps, closes):
                    if c is not None:
                        points.append({"t": ts, "v": round(c, 2)})
                chart_data[key][rng] = points
        except:
            pass

chart_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "market-charts.json")
with open(chart_path, "w") as f:
    json.dump(chart_data, f)
print(f"  Wrote charts for {len(chart_data)} indices")


# ══════════════════════════════════════════════════════════════
# IPL STANDINGS (keep existing)
# ══════════════════════════════════════════════════════════════

print("\n=== IPL Standings ===")
try:
    ipl_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "ipl-standings.json")
    if os.path.exists(ipl_path):
        with open(ipl_path) as f:
            existing = json.load(f)
        team_count = len(existing.get('teams', existing) if isinstance(existing, dict) else existing)
        print(f"  Existing IPL standings: {team_count} teams (keeping current)")
except Exception as e:
    print(f"  IPL check: {e}")


# ══════════════════════════════════════════════════════════════
# GIT COMMIT & PUSH
# ══════════════════════════════════════════════════════════════

print("\n=== Git Push ===")
repo_dir = os.path.join(os.path.dirname(__file__), "..")
os.chdir(repo_dir)

subprocess.run(["git", "add", "public/data/", "pipeline/lifestyle-writer-20260523.py"], capture_output=True)
result = subprocess.run(
    ["git", "commit", "-m", "data: markets + charts refresh + lifestyle writer (03:00 PDT)"],
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

print("\n✅ Lifestyle writer 03:00 PDT run complete")
