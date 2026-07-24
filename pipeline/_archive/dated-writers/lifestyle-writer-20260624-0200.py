#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 02:00 UTC batch.
Topics:
  1. Lancet eBioMedicine RCT: high-dose omega-3 (DHA) reached the brain but did NOT improve memory/cognition — lifestyle-health
  2. Cell Metabolism / USC (Longo): methionine-restricted "longevity diet" — specific amino acids may matter more than total protein — lifestyle-health
  3. India private-sector growth cools to 3-month low; resurgent dollar + Fed rate-hike bets pressure rupee, markets pull back — markets-finance
"""

import json, os, io, subprocess, urllib.parse, re
from datetime import datetime, timezone
import requests

# ---- env ----
for env_file in ("~/.env.supabase", "~/workspace/.env.pexels"):
    p = os.path.expanduser(env_file)
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY") or os.environ.get("PEXELS_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

# ---------------- image helpers ----------------
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:70]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for _, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
                    continue
                title = page.get("title", "").lower()
                if any(b in title for b in ("flag_of", "coat_of_arms", "emblem", "_map", "location_", "logo", "seal_of")):
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  \u2713 Commons: {len(results)} imgs for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
        out = subprocess.run(["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}", url],
                             capture_output=True, text=True, timeout=30)
        data = json.loads(out.stdout)
        photos = data.get("photos", [])
        if photos:
            src = photos[0]["src"]
            chosen = src.get("large2x") or src.get("large") or src.get("original")
            print(f"  \u2713 Pexels img for '{query}'")
            return chosen
    except Exception as e:
        print(f"  \u26a0 Pexels error '{query}': {e}")
    return None

def download_bytes(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except Exception:
        pass
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0624.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0624.bin"):
            with open("/tmp/_img_dl0624.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0624.bin")
            if len(data) > 5000:
                return data
    except Exception as e:
        print(f"  \u26a0 download error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    if not HAVE_PIL:
        return img_bytes
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()
    except Exception as e:
        print(f"  \u26a0 compress error: {e}")
        return img_bytes

def upload_to_supabase(img_bytes, filename):
    try:
        url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                   "Content-Type": "image/jpeg", "x-upsert": "true"}
        r = requests.post(url, headers=headers, data=img_bytes, timeout=60)
        if r.status_code in (200, 201):
            public = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded {filename} ({len(img_bytes)//1024} KB)")
            return public
        else:
            print(f"  \u2717 Upload failed {filename}: {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"  \u26a0 upload error: {e}")
    return None

def source_image(slug, commons_queries, pexels_queries, person=None):
    candidates = []
    if person:
        wiki = fetch_wikipedia_person_image(person)
        if wiki:
            candidates.append((wiki, "Wikimedia Commons"))
    for q in commons_queries:
        for r in fetch_wikimedia_commons_images(q)[:3]:
            candidates.append((r["url"], "Wikimedia Commons"))
        if candidates:
            break
    for q in pexels_queries:
        px = fetch_pexels_image(q)
        if px:
            candidates.append((px, "Pexels"))
            break
    for url, attribution in candidates:
        raw = download_bytes(url)
        if not raw:
            continue
        comp = compress_image(raw)
        if len(comp) < 10000:
            continue
        final = upload_to_supabase(comp, f"{slug}.jpg")
        if final:
            return final, attribution
    print(f"  \u26a0 No image sourced for {slug}")
    return None, None

# ---------------- DB insert ----------------
def insert_article(article):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=representation"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=headers,
                         json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"  \u2713 Inserted: {article['slug']} (id: {data[0]['id'] if data else 'ok'})")
        return True
    print(f"  \u2717 FAILED: {article['slug']} \u2014 {resp.status_code}: {resp.text[:300]}")
    return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
articles = []

# ============================================================
# ARTICLE 1: Omega-3 supplement & memory (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A High-Dose Omega-3 Pill Reached the Brain but Did Nothing for Memory, a Gold-Standard Trial Finds",
    "subheadline": "In a two-year randomized trial of older adults at risk of dementia, daily fish-oil-style DHA more than doubled omega-3 levels in the blood and reached the brain \u2014 yet it failed to improve memory, thinking or the size of the brain\u2019s memory centre any more than a placebo.",
    "slug": "omega-3-dha-supplement-no-memory-cognition-benefit-lancet-ebiomedicine-randomized-trial-diaspora-20260624-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Fish-oil and omega-3 capsules are among the most popular over-the-counter supplements in Indian-origin households, often bought in bulk and taken for years in the belief they protect the aging brain; this rigorous trial is a reminder that for most people the money may be better spent on diet and exercise than on a daily pill.",
    "sources": json.dumps([
        {"name": "The Lancet eBioMedicine \u2014 randomized controlled trial of high-dose DHA supplementation and cognition", "url": "https://www.thelancet.com/journals/ebiom/home"},
        {"name": "CNN \u2014 Taking an omega-3 supplement doesn\u2019t boost memory or cognition, study finds", "url": "https://www.cnn.com/2026/06/19/health/omega-3-supplement-memory-cognition-wellness"}
    ]),
    "body": """For years, the omega-3 capsule has been sold as a quiet act of self-defence for the aging brain \u2014 a daily dose of the same fats found in oily fish, taken in the hope of holding memory loss at bay. A new clinical trial, built to the highest scientific standard, has just delivered an inconvenient verdict: the pills reached the brain, but the brain was no better for it.

## What the Trial Did

The study was a randomized, double-blind, placebo-controlled clinical trial \u2014 the gold standard of medical evidence, published in the Lancet journal *eBioMedicine*. Researchers enrolled 365 people aged 55 to 80 who did not have dementia but who started with extremely low omega-3 levels and carried at least one risk factor for dementia, such as obesity, a sedentary lifestyle, high blood pressure or raised cholesterol.

Crucially, nearly half the participants carried at least one copy of the **APOE4 gene** \u2014 the most important common genetic risk factor for Alzheimer's. People with APOE4 are thought to be the group most likely to benefit from supplementation, because their brains struggle to process fats efficiently.

Half the volunteers were given a high dose of an algae-based omega-3 supplement \u2014 2,000 milligrams of DHA every day for 24 months. The other half took a placebo. Both groups also took a vitamin B complex. Over the two years, everyone underwent MRI brain scans, blood draws and repeated cognitive testing.

## The Pills Worked \u2014 the Benefit Didn't

The first thing the data showed is that the supplement did exactly what it was supposed to do biologically. Omega-3 levels in red blood cells climbed from 4.9 percent to 11 percent in the treatment group. Measures of DHA in the cerebrospinal fluid \u2014 the liquid that bathes the brain \u2014 rose by an average of 17 percent after six months, confirming the fat was crossing into the brain. The same increases appeared even in people carrying the APOE4 gene.

And yet, when it came to what actually matters, there was nothing. "Despite evidence that levels of omega-3 had risen in the brains of people who took the supplement, there were no improvements in cognition or the size of the hippocampus," the brain's memory centre, one of the researchers noted. As lead author Dr. Hussein Yassine put it, "there was no real difference between people taking an omega-3 supplement and those taking a placebo."

## Why the Result Matters

This is not the first time a popular brain supplement has failed under rigorous testing, and that pattern is the real story. Observational studies \u2014 which simply track what people already do \u2014 had long hinted that fish-eaters and omega-3 users had healthier brains. But such studies cannot separate the pill from everything else that tends to travel with it: people who take supplements often eat better, exercise more and see doctors more regularly.

When researchers strip those confounders away with a randomized trial, the apparent benefit frequently evaporates. One expert in the field captured the broader lesson bluntly, comparing a single supplement to "a drop in the ocean" against the tide of an unhealthy overall lifestyle.

That said, the trial does leave a door ajar. The participants were chosen precisely because they were at risk and already had low omega-3 levels, and the study was relatively short at two years. Dr. Yassine suggested that a healthier person, or someone supplementing earlier in life, might still derive some benefit. What the trial does rule out is the simple, seductive idea that a high-dose capsule can reverse or halt cognitive decline once risk has set in.

## What Diaspora Families Should Take From It

In many Indian-origin households, the supplement shelf is a small monument to good intentions \u2014 fish oil, turmeric capsules, multivitamins, glucosamine \u2014 often bought on trips home in bulk, shared among relatives and taken for years without a doctor ever weighing in. Omega-3 is among the most trusted of these, precisely because it carries the halo of "natural" and "heart-healthy."

The honest message is not that omega-3 is harmful; for heart and triglyceride health the evidence is more favourable, and oily fish remains part of a genuinely healthy diet. The message is about expectations and priorities. The interventions with the strongest evidence for protecting the aging brain are unglamorous and free or cheap: controlling blood pressure and cholesterol, staying physically active, treating hearing loss, sleeping well and eating a largely plant-forward diet. A capsule is not a substitute for any of them.

For a diaspora family budgeting for an elderly parent's health, that reframing is worth real money. Before the next bulk order of fish-oil pills, the more powerful investment may be a brisk daily walk, a blood-pressure check and a conversation with a doctor about what the evidence actually supports."""
})

# ============================================================
# ARTICLE 2: USC longevity diet / methionine (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Much Protein You Eat, but Which Building Blocks \u2014 a New Longevity-Diet Study Suggests",
    "subheadline": "Scientists at USC report that fine-tuning a single amino acid, methionine, let mice eat more food yet lose fat without losing muscle \u2014 and that people eating the most animal protein had twice the rate of diabetes, hinting the kind of protein may matter more than the amount.",
    "slug": "usc-longevity-diet-methionine-amino-acid-protein-quality-frailty-healthspan-cell-metabolism-diaspora-20260624-0200",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The protein debate cuts to the heart of diaspora eating habits \u2014 from the dal-and-rice plant-based traditions of many Indian households to the high-protein, meat-heavy regimes popular in Western fitness culture \u2014 and this research suggests the traditional emphasis on plant proteins may carry an underappreciated metabolic advantage.",
    "sources": json.dumps([
        {"name": "Cell Metabolism \u2014 Fanti et al., Methionine-supplemented longevity diet increases growth hormone, GLP-1, and FGF21; reduces frailty; and promotes healthspan", "url": "https://www.sciencedirect.com/science/article/pii/S1550413126002251"},
        {"name": "News-Medical \u2014 USC study links modified longevity diet to longer lifespan", "url": "https://www.news-medical.net/news/20260623/USC-study-links-modified-Mediterranean-diet-to-longer-lifespan.aspx"}
    ]),
    "body": """For decades, dietary advice has fixated on a single number: grams of protein. Eat enough and you preserve muscle; eat too little and you grow frail. A new study from the University of Southern California complicates that tidy story, suggesting that the *type* of protein \u2014 specifically the balance of its amino-acid building blocks \u2014 may matter more than the total amount on the plate.

## The Experiment

The research, published in *Cell Metabolism* by a team led by longevity scientist Valter Longo and colleague Marco Fanti, centred on a diet they call the low-protein, low-methionine longevity diet, modelled on the eating patterns of long-lived populations such as traditional Italians and Okinawans. Methionine is an essential amino acid found in especially high amounts in animal foods \u2014 meat, fish, eggs and dairy.

Working with mice, the scientists adjusted methionine levels up and down while tracking weight, body composition, frailty and a suite of metabolic hormones. The standout finding, in Longo's words, was "remarkable": mice on the modified longevity diet "could eat more food than any other group and as many calories as any other group and yet lose fat without losing lean body mass \u2014 but only when methionine levels were low but sufficient."

In other words, getting one amino acid into a narrow sweet spot appeared to let the animals enjoy a generous diet while still shedding fat and protecting muscle. The diet raised levels of growth hormone, the gut hormone GLP-1 (the same pathway targeted by blockbuster weight-loss drugs) and FGF21, a hormone tied to metabolic health, while reducing frailty and extending healthspan.

## The Human Signal

The team also examined human data, and the pattern pointed the same way. Participants who ate the **highest levels of animal protein** \u2014 and therefore the most methionine and other essential amino acids \u2014 had a higher prevalence of obesity and **twice the rate of diabetes** compared with those eating little to no animal protein.

Strikingly, this held even though the high-animal-protein eaters consumed fewer total calories and otherwise had healthier nutrition. "This challenges the dogma that calorie reduction is necessary to lose weight," Longo said, "but it also tells us that we need to have a clear understanding of the mechanisms."

The balance turned out to be delicate in both directions. "Too little methionine caused frailty, but too much methionine abolished the benefits of this diet," Longo explained. The conclusion the researchers draw is that "overall protein intake may be less important than specific amino-acid intake."

## A Note of Caution

This is important context, not a prescription. The core findings come from mice, and the human portion is observational \u2014 it shows an association between high animal-protein diets and poorer metabolic outcomes, not definitive proof that swapping steak for lentils will add years to a life. The researchers themselves say the obvious next step is a controlled clinical trial of the diet in people, which has not yet been done. Methionine is also genuinely essential; the goal the study points to is a calibrated "low but sufficient" intake, not elimination, and anyone with specific medical or nutritional needs should not self-experiment without guidance.

## Why It Resonates in Diaspora Kitchens

Few questions divide a diaspora dinner table like protein. On one side sit the plant-forward traditions that many Indian households grew up with \u2014 dal, rajma, chana, paneer in moderation, vegetables and whole grains, with meat as an occasional rather than daily presence. On the other sits the high-protein, meat-and-whey culture of Western gyms and wellness influencers, which has pulled many second-generation diaspora youngsters toward heavy animal-protein intake.

This study lands squarely in the middle of that tension and offers a measure of vindication for the older approach. The traditional emphasis on plant proteins \u2014 naturally lower in methionine \u2014 may carry a metabolic advantage that the gram-counting, meat-maximising model overlooks. For families navigating diabetes and obesity, both of which strike South Asians at lower body weights and younger ages than many other groups, that is more than an academic point.

The practical takeaway is not to abandon protein but to think about its sources. Leaning on lentils, beans, tofu and other plant proteins, treating red and processed meat as occasional rather than central, and resisting the urge to chase ever-higher protein totals may be quietly aligned with how the longest-lived populations on earth have always eaten."""
})

# ============================================================
# ARTICLE 3: India PMI cooldown + dollar/Fed pressure on rupee (markets-finance)
# ============================================================
articles.append({
    "headline": "India\u2019s Economy Just Cooled to a Three-Month Low \u2014 and a Resurgent Dollar Is Squeezing the Rupee Again",
    "subheadline": "Fresh data show India\u2019s private-sector growth slowing and business confidence at its weakest in nearly four years, just as rising bets on a U.S. Federal Reserve rate hike push the dollar to a one-year high and drag the rupee and Indian stocks lower.",
    "slug": "india-private-sector-growth-three-month-low-pmi-dollar-fed-rate-hike-rupee-markets-pullback-nri-investor-20260624-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs, the twin pressures matter directly: a weaker rupee stretches the value of dollars sent home or invested in India, while a cooling economy and a hawkish Fed reshape the calculus on when to remit, when to buy Indian equities, and how much currency risk to carry.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 IT, metals drag Indian shares; weak business data, monsoon worries weigh", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 India\u2019s June private sector growth slips to three-month low as demand, confidence cool, PMI shows", "url": "https://www.reuters.com/markets/asia/"}
    ]),
    "body": """After a heady week-long rally, India's markets ran into a wall of softer data this week, and the message was sobering: the economy is cooling just as the global backdrop turns less friendly. A weakening growth pulse at home has collided with a resurgent U.S. dollar abroad, leaving both the rupee and Indian equities on the back foot.

## The Growth Pulse Is Easing

The clearest warning came from the closely watched purchasing managers' surveys. HSBC's flash India Composite PMI, compiled by S&P Global, fell to 57.4 in June from May's 59.3 \u2014 still firmly in expansion territory above the 50 mark, but the slowest pace in three months.

The detail beneath the headline was less reassuring. The services PMI dropped to a 17-month low of 57.3, while manufacturing growth eased to a three-month low of 54.5. New orders, the key gauge of demand, rose at their weakest pace since March, with firms citing competitive pressures and gas shortages. Job creation slowed to its weakest in the current six-month run of expansion. Most tellingly, business confidence slipped below its long-run average, with sentiment among goods producers sinking to its lowest in nearly four years.

The one silver lining was on prices: cost pressures eased for a third straight month to their lowest since January, and firms passed on the smallest price increases in six months \u2014 a welcome sign for inflation, even if it reflects soft demand.

## Markets Take the Hint

Investors responded by booking profits after a strong run. The Nifty 50 and the Sensex each fell about 1.16 percent on Tuesday, to 23,824 and 76,201 respectively, with the Nifty slipping back below the 24,000 level it had only just reclaimed. The pullback erased part of a powerful rally in which the two benchmarks had gained 4.1 and 4.4 percent over the previous seven sessions, lifted by falling oil prices and easing foreign outflows.

The damage was concentrated. Fourteen of the 16 major sectors fell. IT stocks slid 2.2 percent, still reeling from bellwether Accenture's weak demand outlook and fresh caution from Jefferies and Morgan Stanley. The metals index dropped 3.2 percent, tracking weaker global metal prices. Pharma was a rare bright spot, with Cipla leading gains.

## The Dollar Is the Bigger Story

What gives this pullback its edge is what is happening outside India. A churn in U.S. interest-rate expectations has pushed the dollar to its highest level in a year, with the dollar index climbing to 101.18. Money markets are now close to fully pricing in a Federal Reserve rate increase by September \u2014 a sharp reversal from earlier hopes of cuts.

That shift is rippling across Asia. The rupee ended modestly weaker at 94.7350 per dollar, and MSCI's gauge of Asian shares fell more than 3 percent. As one bank noted, "the adjustment higher in U.S. yields is creating a more challenging backdrop for risk assets." For India, the timing is awkward: the rupee had only just found relief after the Iran war, helped by cooling oil prices and active support from policymakers.

Traders now expect the rupee to face intermittent pressure, even as anticipated dollar inflows \u2014 via overseas foreign-currency deposits, borrowings and debt investments \u2014 keep the depreciation in check. Importers remain more active hedgers than exporters, a pattern unlikely to shift soon.

## What It Means for NRIs

For the diaspora, these crosscurrents land directly on the kitchen table. A stronger dollar and a softer rupee mean that money remitted home, or invested in Indian assets, stretches further in rupee terms \u2014 a genuine, if bittersweet, advantage for anyone sending funds to family or building a property corpus in India. Those weighing a transfer may find the current levels attractive relative to the rupee's stronger spells earlier in the year.

The flip side is risk. A cooling domestic economy and a hawkish Fed are exactly the conditions that can keep foreign investors cautious; overseas portfolio investors have already pulled a record amount out of Indian stocks this year, and a renewed bout of dollar strength could slow their tentative return. For NRIs holding Indian equities or rupee-denominated deposits, that argues for a clear-eyed view of currency exposure rather than assuming the recent rally will simply resume.

## What's Next

The near-term triggers are well flagged: the progress of the monsoon, the next round of U.S.-Iran talks and their effect on oil, and above all the Fed's trajectory. If crude stays subdued and the peace process holds, earnings visibility improves and foreign buyers could drift back. But with the dollar at a one-year high and India's own growth momentum easing, the path is narrower than it looked a week ago. For diaspora investors, the prudent posture is patience, diversification and a close eye on the currency \u2014 not a chase of the last rally."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["fish oil omega-3 capsules supplement", "fish oil softgel capsules", "dietary supplement capsules pills"],
                          ["fish oil capsules", "omega 3 supplement"], None),
    articles[1]["slug"]: (["lentils legumes beans pulses food", "dal lentils Indian food", "plant based protein legumes"],
                          ["lentils legumes", "plant based meal bowl"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "BSE building Dalal Street", "Indian rupee US dollar currency notes"],
                          ["stock market trading screen", "indian rupee currency"], None),
}
img_captions = {
    articles[0]["slug"]: "Omega-3 fish-oil capsules; a two-year randomized trial found high-dose DHA reached the brain but did not improve memory",
    articles[1]["slug"]: "Lentils and legumes; new research suggests the type of protein, not just the amount, may shape metabolic health",
    articles[2]["slug"]: "The Bombay Stock Exchange in Mumbai; Indian markets pulled back as growth cooled and a stronger dollar pressured the rupee",
}
for art in articles:
    cq, pq, person = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq, person=person)
    if url:
        art["image_url"] = url
        art["image_caption"] = img_captions[art["slug"]]
        art["image_attribution"] = attribution
    else:
        print(f"  \u26a0 {art['slug']} will publish without hero image")

# ============================================================
# INSERT
# ============================================================
print(f"\n{'='*60}\nInserting {len(articles)} articles at {now}\n{'='*60}\n")
success = 0
for a in articles:
    wc = len(a['body'].split())
    has_img = "img\u2713" if a.get("image_url") else "NO-IMG"
    print(f"  [{a['category']}] {a['slug']} \u2014 {wc} words \u2014 {has_img}")
    if insert_article(a):
        success += 1
print(f"\n{'='*60}\nDone: {success}/{len(articles)} articles inserted\n{'='*60}")
