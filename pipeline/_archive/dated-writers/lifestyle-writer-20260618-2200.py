#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 22:00 UTC batch.
Topics:
  1. DPP/DPPOS 21-year follow-up (JAMA): lifestyle, not metformin, cut multimorbidity — lifestyle-health
  2. Blood vitamin C levels tied to better-preserved brain structure (PLOS ONE, Hirosaki) — lifestyle-health
  3. RBI scraps interest-rate caps on FCNR(B) and long NRE deposits till Sept 30 — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0618b.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0618b.bin"):
            with open("/tmp/_img_dl0618b.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0618b.bin")
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
# ARTICLE 1: DPP 21-year — lifestyle beats metformin (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Cheap Diabetes Drug Was Hailed as a Longevity Pill. A 21-Year Study Says Diet and Exercise Beat It.",
    "subheadline": "Tracking adults with prediabetes for more than two decades, researchers found that an intensive diet-and-exercise program lowered the risk of piling up multiple chronic diseases \u2014 while metformin, the drug touted as an anti-ageing wonder, did no better than a placebo.",
    "slug": "dpp-dppos-lifestyle-beats-metformin-multimorbidity-21-year-jama-prediabetes-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "diabetes-prevention",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians develop prediabetes and Type 2 diabetes earlier and at lower body weights than almost any other group, and metformin is one of the most prescribed drugs in Indian households worldwide \u2014 so the finding that a structured diet-and-exercise routine, not the pill, is what actually held off the cascade of chronic disease over 21 years speaks directly to how the NRI community should weight medication against daily habits.",
    "sources": json.dumps([
        {"name": "JAMA \u2014 Lifestyle and Metformin Interventions and Risk of Multimorbidity in Adults With Prediabetes (2026)", "url": "https://jamanetwork.com/journals/jama"},
        {"name": "New York Post \u2014 Two simple habits may outperform a popular longevity wonder drug: study", "url": "https://nypost.com/health/"}
    ]),
    "body": """For years, the humble diabetes pill metformin has been quietly recast as something close to a fountain of youth. Doctors and biohackers alike have credited the decades-old drug with slowing ageing, cutting the risk of long COVID, even extending lifespan. Now a study following adults for more than two decades has put that reputation to a hard test \u2014 and found that two unglamorous habits did the job better.

## What the Researchers Tracked

The findings, published in the journal *JAMA*, come from one of the most important long-running experiments in preventive medicine: the **Diabetes Prevention Program (DPP)** and its follow-up, the DPP Outcomes Study. Beginning in 1996, researchers at 27 sites across the United States enrolled 3,234 adults at high risk of developing diabetes and randomly assigned them to one of three groups \u2014 an intensive lifestyle program, the drug metformin, or a placebo \u2014 for three years, then followed them for decades afterward.

The lifestyle arm was specific and demanding: a low-fat, low-calorie diet paired with at least 150 minutes of physical activity a week, with a goal of modest weight loss. Metformin participants took the standard medication. The placebo group took a dummy pill.

## The Two-Decade Verdict

What the researchers wanted to know was not just who developed diabetes, but who accumulated **multimorbidity** \u2014 two or more chronic conditions at once. They pulled Medicare claims data for 1,173 participants and tracked 15 common ailments, including hypertension, cancer, dementia, Alzheimer's disease, chronic kidney disease, heart failure, osteoporosis and stroke.

Over 21 years of follow-up, the numbers told a clear story. Multimorbidity eventually struck most people in every group \u2014 these were high-risk adults growing old \u2014 but the lifestyle group fared measurably best: 82 percent developed multiple chronic conditions, compared with 85 percent in the metformin group and 87 percent in the placebo group. After adjusting for other factors, the lifestyle intervention was associated with a significantly lower risk of multimorbidity than placebo. Metformin, strikingly, showed no significant difference from placebo at all.

"Among adults with prediabetes at baseline, lifestyle intervention, but not metformin, was associated with a lower risk of multimorbidity during 21 years of follow-up," the authors concluded.

## Why This Is Not a Knock on Metformin

It is worth being precise about what the study does and does not say. Metformin remains a proven, inexpensive and valuable drug for treating Type 2 diabetes and for delaying its onset in many high-risk people \u2014 earlier DPP results showed it cut progression to diabetes, just less powerfully than lifestyle change. What this analysis questions is the broader, trendier claim that metformin is a general-purpose shield against the diseases of ageing. On that larger promise, over two decades, it did not outperform a sugar pill.

The study also has limits. It is an observational follow-up rather than a fresh randomized trial of multimorbidity, and most participants eventually developed chronic disease regardless of group. But the size, length and rigor of the DPP make its signal hard to dismiss.

## Why It Lands Hard for the Diaspora

For the Indian diaspora, this research touches a nerve. South Asians are diagnosed with prediabetes and Type 2 diabetes earlier and at lower body weights than most populations \u2014 the so-called "thin-fat" pattern of more body fat and less muscle for a given size. Metformin is one of the most commonly prescribed drugs in NRI households, often started early and leaned on as the main line of defence.

The temptation, in busy two-income immigrant families, is to treat the prescription as the solution and the diet as optional. This study reframes that bargain. The pill has its place, but the durable protection against the slow stacking of heart disease, kidney trouble and dementia came from sustained movement and disciplined eating \u2014 not from the medicine cabinet.

## What To Actually Do

The recipe is neither new nor expensive. Aim for at least 150 minutes of activity a week \u2014 brisk walking counts \u2014 and build a diet around vegetables, whole grains, dal and lean protein rather than refined carbohydrates and fried snacks, the staples that creep into diaspora kitchens. If you or a parent takes metformin for prediabetes, keep taking it as prescribed, but do not let it crowd out the daily habits. The trial's lesson, after 21 years, is blunt: the drug helps, but the walk and the plate are what carry you."""
})

# ============================================================
# ARTICLE 2: Vitamin C blood levels & brain structure (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Vitamin in Your Morning Orange May Help Keep Your Brain Younger, a Study of 2,000 Adults Finds",
    "subheadline": "Japanese researchers measured vitamin C directly in the blood of older adults \u2014 not just their diets \u2014 and found that those with higher levels had better-preserved gray matter and stronger connections in a brain network central to memory.",
    "slug": "vitamin-c-blood-levels-brain-gray-matter-default-mode-network-plos-one-hirosaki-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "brain-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Vegetarian and plant-forward Indian diets are often rich in vitamin C from citrus, amla, guava, peppers and leafy greens \u2014 but the heavy boiling and long cooking common in desi kitchens destroys much of it, making this a rare case where a traditional diaspora strength can quietly become a deficiency that may matter for the ageing brain.",
    "sources": json.dumps([
        {"name": "PLOS ONE \u2014 Association between blood vitamin C levels, brain structure and default mode network connectivity in older adults (Hirosaki University, 2026)", "url": "https://journals.plos.org/plosone/"},
        {"name": "Health.com \u2014 Low Vitamin C Levels Linked to Poorer Brain Health in Older Adults", "url": "https://www.health.com/vitamin-c-brain-health"}
    ]),
    "body": """Vitamin C is the nutrient everyone thinks they understand: good for colds, found in oranges, easy to get. New research from Japan suggests it may also be quietly tied to something far more consequential \u2014 how well the brain holds its shape into old age.

## A Sharper Way to Measure

The study, published in the journal *PLOS ONE*, stands out for a simple but important reason. Most past research on vitamin C and the brain relied on asking people what they ate, a notoriously unreliable method. Here, scientists at Hirosaki University measured vitamin C **directly in the blood** of their participants, giving a far more accurate picture of how much was actually circulating in the body.

They drew on roughly 2,000 older adults living in Hirosaki City \u2014 the average age was 69, and most were women \u2014 who had blood samples taken and underwent MRI brain scans. The scans let researchers calculate the volume of gray matter and white matter and assess the wiring of a key brain system called the **default mode network (DMN)**, a set of regions involved in memory, self-reflection and internal thought.

## What They Found

The pattern was consistent. People with lower blood levels of vitamin C tended to have less gray matter and weaker connectivity within the default mode network \u2014 both of which are early signatures of age-related cognitive decline. The link held even after the researchers accounted for age, education, smoking, diabetes, hypertension and other lifestyle factors.

"Our study demonstrates that older adults with higher blood levels of vitamin C tend to have better-preserved brain structure \u2014 gray matter \u2014 and stronger connections within the default mode network, a crucial brain network involved in memory and cognitive function," said Tomohiro Shintaku, an assistant professor of radiology at Hirosaki University Graduate School of Medicine.

Why might that be? Vitamin C is one of the brain's most important antioxidants. The brain consumes enormous amounts of oxygen and is therefore especially vulnerable to oxidative stress, the slow cellular wear that accumulates with age. Vitamin C helps neutralise that damage \u2014 and the brain works hard to keep its own vitamin C levels high, a sign of how much it depends on the nutrient.

## The Caveats That Matter

This is the part too many headlines skip. The study is **observational**: it found an association, not proof that low vitamin C causes brain shrinkage or that loading up on the vitamin will protect anyone. As Shintaku himself cautioned, the research could not establish cause and effect. It also relied on a single blood draw per person, which may not reflect long-term vitamin C status, and did not account for every relevant factor, such as body weight and socioeconomic status.

In other words, no one should rush out to megadose on supplements. There is, in fact, little evidence that high-dose vitamin C pills help a well-nourished person, and the body simply excretes what it cannot use. The takeaway is subtler: maintaining adequate vitamin C, ideally through food, may be one more modifiable piece of the brain-ageing puzzle.

## Why the Diaspora Should Pay Attention

For Indian families, there is an unexpected wrinkle. On paper, the traditional Indian diet is rich in vitamin C \u2014 amla (Indian gooseberry) is one of the densest natural sources on earth, and guava, citrus, capsicum, tomatoes and leafy greens are kitchen staples. But vitamin C is fragile. It breaks down with heat, light and prolonged cooking, and the long simmering, deep frying and reheating common in many desi kitchens can strip much of it away before it reaches the plate.

That makes this a rare case where a genuine dietary strength can quietly turn into a shortfall. An older NRI parent eating "plenty of vegetables" may still be getting far less usable vitamin C than the menu suggests \u2014 particularly if fresh fruit is scarce and most produce arrives heavily cooked.

## What To Actually Do

Lean on raw and lightly cooked sources: a piece of fresh fruit daily, a squeeze of lemon over food, raw tomato and cucumber, a guava or orange in season, or amla in the cooler months. Cook vegetables more lightly \u2014 steaming and quick stir-frying preserve far more vitamin C than long boiling. For most people, food beats pills. And treat this not as a reason to panic-buy supplements, but as one more small, cheap habit that may help the ageing brain hold its ground."""
})

# ============================================================
# ARTICLE 3: RBI scraps rate caps on NRI deposits (markets-finance)
# ============================================================
articles.append({
    "headline": "India Just Cleared the Way for Banks to Pay NRIs More on Their Deposits \u2014 But Only Until September.",
    "subheadline": "The Reserve Bank of India has temporarily scrapped the interest-rate ceilings on fresh FCNR(B) and longer-tenure NRE deposits through September 30, freeing banks to compete for overseas money as New Delhi scrambles to defend a battered rupee.",
    "slug": "rbi-removes-interest-rate-caps-fcnr-nre-nri-deposits-september-rupee-defence-nri-investor-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This is one of the most directly actionable moves for NRIs all year: with rate caps lifted on FCNR(B) and long NRE deposits until September 30, banks are about to compete for diaspora dollars \u2014 meaning the rates Indians abroad earn on parked savings could jump, but only inside a closing window.",
    "sources": json.dumps([
        {"name": "Outlook Money \u2014 RBI Temporarily Removes Interest Rate Caps On Select NRI Deposits Till September 30", "url": "https://www.outlookmoney.com/banking/rbi-temporarily-removes-interest-rate-caps-on-select-nri-deposits-till-september-30"},
        {"name": "Reuters \u2014 India's measures to protect rupee seen drawing about $40 billion, analysts say", "url": "https://www.reuters.com/world/india/"}
    ]),
    "body": """The Reserve Bank of India has handed non-resident Indians a rare, time-limited gift: the prospect of higher returns on money parked back home. In notifications issued on June 17, the central bank temporarily withdrew the interest-rate ceilings that normally cap what banks can pay on certain non-resident deposits \u2014 a move designed less to reward the diaspora than to lure its dollars in to steady a sliding rupee.

## What Exactly Changed

Two categories of NRI deposit are affected. First, the cap on fresh **Foreign Currency Non-Resident (Bank)**, or FCNR(B), deposits with maturities of three to five years has been removed. These are deposits held in foreign currencies \u2014 dollars, pounds, euros \u2014 so the depositor carries no rupee-exchange risk during the term. Second, the RBI lifted the rate restriction on **Non-Resident External (NRE)** deposits with tenures of three years and above. Both relaxations cover fresh deposits and those renewed on maturity, and both run until September 30, 2026.

With the ceilings gone, banks are free to set their own rates on eligible deposits \u2014 which, in practice, means they can compete for overseas money by offering more. The RBI was explicit that this takes effect immediately and gives lenders "additional flexibility to mobilise foreign currency deposits."

## The Bigger Plan Behind It

The deposit move does not stand alone. It is the latest in a battery of measures New Delhi has rolled out this month to pull foreign capital into the country as the rupee buckles. Since the US-Iran conflict erupted in late February, the currency has shed more than 5 percent, hitting a record low near 96.83 to the dollar in May, while foreign investors yanked a record $30.8 billion out of Indian equities earlier in the year.

To stem the bleeding, the government has opened long-dated government bonds to unfettered foreign access, scrapped caps on short-term foreign bond investment, and exempted some overseas investors from capital-gains tax on government debt. Crucially for the deposit scheme, the RBI also introduced a concessional foreign-exchange swap facility \u2014 effectively agreeing to shoulder the roughly 2.5 percent annual cost of hedging fresh FCNR(B) deposits \u2014 so banks can offer attractive rates without eating the currency risk themselves. RBI Governor Sanjay Malhotra said the package would let banks "increase deposit rates for NRIs and OCI depositors."

Analysts think the combined measures could draw substantial sums. Estimates range from a minimum of $30 billion over four months to as much as $40\u201350 billion if banks aggressively chase FCNR flows, according to economists at HDFC Bank, Union Bank of India and YES Bank cited by Reuters.

## Why the Timing Is Urgent for India

The backdrop is a banking system short on deposits. Credit has outpaced deposit growth for three straight years \u2014 system bank credit grew 16.1 percent in FY26 against deposit growth of 13.5 percent \u2014 and fresh inflows into NRI schemes had actually been falling, down roughly 24 percent year-on-year in recent data. By letting banks pay more, the RBI is trying to reverse that slide and refill the funding tank while propping up the rupee at the same time.

## What It Means for the Diaspora

For NRIs, this is unusually concrete. Most diaspora investing advice is about long horizons and patience; this is a specific, closing window. Over the coming weeks, expect Indian banks to start advertising sharply better rates on three-to-five-year FCNR(B) deposits and on longer NRE fixed deposits, as they compete for exactly the kind of savings sitting in diaspora accounts from New Jersey to Dubai to Singapore.

A few cautions are worth keeping in view. FCNR(B) deposits are held in foreign currency, so they shield you from rupee depreciation \u2014 a real advantage given the currency's slide \u2014 while NRE deposits are rupee-denominated and rebuild that exchange risk into the equation. Interest on both is generally tax-free in India, but may be taxable in your country of residence, so check local rules. And the relaxation expires on September 30; rates locked in before then can run for the full deposit term, but the chance to lock them in will not last.

## The Bottom Line

India needs the diaspora's dollars, and for once it is willing to pay up for them. NRIs sitting on idle savings have a narrow, well-defined opportunity to earn more \u2014 by comparing FCNR(B) and NRE offers across banks now, weighing currency risk against tax, and acting before the window shuts in late September."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["healthy vegetables diet plate", "person walking exercise outdoors", "fresh vegetables market healthy food"],
                          ["healthy diet vegetables exercise", "person walking outdoors fitness"], None),
    articles[1]["slug"]: (["citrus fruits oranges vitamin C", "oranges lemons fresh fruit", "amla indian gooseberry fruit"],
                          ["fresh oranges citrus fruit", "sliced oranges vitamin c"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Reserve Bank of India headquarters", "Indian rupee currency notes"],
                          ["indian rupee currency notes", "reserve bank of india building"], None),
}
img_captions = {
    articles[0]["slug"]: "A diet rich in vegetables and regular exercise; a 21-year study found lifestyle change, not metformin, cut the risk of multiple chronic diseases",
    articles[1]["slug"]: "Citrus fruit, a key vitamin C source; a study links higher blood vitamin C to better-preserved brain structure in older adults",
    articles[2]["slug"]: "Indian currency; the RBI has lifted rate caps on select NRI deposits until September 30 to attract overseas funds",
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
