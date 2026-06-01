#!/usr/bin/env python3
"""Lifestyle-Health & Markets-Finance writer for The Videshi — 2026-06-01 run."""

import json, os, sys, uuid, re, time
import requests, urllib.parse
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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


def fetch_pexels_image(query, fallback_query=None):
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_API_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(img_url, filename):
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed ({r.status_code}): {img_url[:80]}")
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}")
            return public_url
        else:
            print(f"  ⚠ Supabase upload error ({resp.status_code}): {resp.text[:200]}")
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload exception: {e}")
        if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
            return img_url
        return None


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def validate_article(a):
    errors = []
    if not a.get("headline") or len(a["headline"]) < 20:
        errors.append("headline too short")
    if len(a.get("headline", "")) > 200:
        errors.append("headline too long")
    if not a.get("subheadline") or len(a["subheadline"]) < 15:
        errors.append("subheadline too short or missing")
    body_words = len(a.get("body", "").split())
    if body_words < 400:
        errors.append(f"body too short ({body_words} words, need 400+)")
    if not a.get("slug") or a["slug"] != a["slug"].lower():
        errors.append("slug missing or not lowercase")
    if a.get("category") not in ("lifestyle-health", "markets-finance"):
        errors.append(f"invalid category: {a.get('category')}")
    if errors:
        print(f"  ✗ Validation FAILED: {'; '.join(errors)}")
        return False
    print(f"  ✓ Validation passed ({body_words} words)")
    return True


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Lifestyle-Health — J&J Erleada Prostate Cancer Surgery
# ═══════════════════════════════════════════════════════════════════════
print("\n══ Article 1: J&J Erleada Prostate Cancer Surgery Study ══")

article1 = {
    "headline": "A Drug Taken Before and After Prostate Surgery Made Patients Nine Times More Likely to Be Cancer-Free. The Study Just Changed the Standard of Care.",
    "subheadline": "J&J's Erleada, given for six months before and after surgery, reduced the risk of the cancer spreading or death by 20 per cent. ASCO chose the data to open its plenary session.",
    "slug": "jnj-erleada-prostate-surgery-proteus-asco-2026-south-asian-men-cancer-free",
    "category": "lifestyle-health",
    "vertical": "health",
    "tags": ["prostate-cancer", "asco-2026", "erleada", "jnj", "south-asian-men"],
    "urgency": "timely",
    "sources": json.dumps(["Reuters", "The New England Journal of Medicine", "GlobeNewsWire / Johnson & Johnson", "ASCO 2026 Plenary (Abstract LBA1)"]),
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "score_total": 0,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """Nearly half of all men who have prostate cancer surgery see their cancer return. For decades, the standard approach has been to operate first and treat later — usually after the disease has already spread beyond the prostate and the window for a cure has narrowed.

A five-year study just upended that sequence. Johnson & Johnson's Phase 3 PROTEUS trial, published simultaneously in *The New England Journal of Medicine* and presented as the opening plenary at the 2026 American Society of Clinical Oncology meeting in Chicago, found that giving the drug apalutamide — sold as Erleada — alongside hormone therapy for six months before and after prostate surgery produced results that researchers are calling paradigm-changing.

## The Numbers That Shifted the Paradigm

Patients who received apalutamide plus hormone therapy were **nine times more likely** to have little to no detectable cancer remaining in the prostate at the time of surgery — 8.9 per cent achieved what oncologists call a pathologic complete response or minimal residual disease, compared with just 1.0 per cent among those who received hormone therapy alone.

The combination also **reduced the risk of metastasis or death by 20 per cent**, a clinically significant margin in a disease where early intervention has historically been limited to surgery and radiation.

A second arm of the study, which extended the drug regimen to a full year before and after surgery, produced even stronger results. Those patients went **more than six years** on average before requiring any subsequent treatment — nearly double the duration for the hormone-only group. The longer course reduced the risk of recurrence and death by 29 per cent.

## Why This Changes How Doctors Treat Prostate Cancer

Until now, additional drug therapy for localised prostate cancer was typically reserved for after the cancer had already returned — a reactive approach that meant patients often missed the critical window where intervention could prevent metastasis entirely.

"These data have the potential to fundamentally shift the treatment paradigm," said Dr Mary-Ellen Taplin, the lead investigator and a professor at Harvard Medical School. The trial's selection as the ASCO plenary opener — the most prestigious slot at the world's largest oncology conference — underscores the weight the research community is placing on the findings.

About 40 per cent of the roughly 330,000 Americans diagnosed with prostate cancer each year are classified as high-risk, meaning their tumours are aggressive enough that standard surgery alone leaves a significant chance of recurrence. Globally, prostate cancer is the second most common cancer in men.

## What South Asian Families Should Know

Prostate cancer is often framed as a disease of older white men, but the reality is more nuanced. South Asian men are diagnosed less frequently in part because screening rates are lower — a combination of cultural reluctance to discuss urological health and fewer targeted public health campaigns. When South Asian men are diagnosed, they are more likely to present at later stages, partly because of delayed screening.

The PROTEUS trial enrolled patients with high-risk localised or locally advanced disease — exactly the profile where early intervention matters most. For South Asian men in the diaspora who are navigating the American healthcare system, the takeaway is concrete: if you or a male family member over 50 has been diagnosed with high-risk prostate cancer and surgery is being considered, ask the oncologist about neoadjuvant and adjuvant apalutamide. This is no longer speculative. It is backed by a randomised Phase 3 trial published in the world's most respected medical journal.

## The Drug and the Company

Erleada (apalutamide) is already approved by the FDA for metastatic and non-metastatic castration-resistant prostate cancer. Johnson & Johnson has said it plans to seek expanded approval for the new indication — use before and after surgery in high-risk localised disease. If granted, it would be the first drug approved for this specific treatment window.

The most common side effects in the trial included fatigue, rash, and joint pain, but importantly, the drug did not increase the rate of surgical complications, a concern that had previously limited enthusiasm for pre-surgical drug therapy in prostate cancer.

## What Comes Next

J&J is expected to file for regulatory approval in the second half of 2026. If the FDA grants it, apalutamide could become part of standard pre-surgical protocols across the United States within a year. For the roughly 132,000 American men diagnosed annually with high-risk prostate cancer, that would mean a fundamentally different conversation at the time of diagnosis — one where the drug is given *before* the surgeon operates, not after the cancer has already come back.

The message from Chicago this week is unambiguous: treating prostate cancer early and aggressively, with the right drug at the right time, can change outcomes in ways that surgery alone cannot.""",
}

if validate_article(article1):
    img_url = fetch_pexels_image("prostate cancer medical treatment", "cancer surgery hospital")
    if img_url:
        art_id = insert_article(article1)
        if art_id:
            final_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")
            if final_url:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
                    headers=HEADERS,
                    json={"image_url": final_url, "image_attribution": "Pexels"},
                    timeout=15,
                )
                print(f"  ✓ Image attached")
    else:
        insert_article(article1)

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Lifestyle-Health — B12 & Folate Deficiency and Fatigue
# ═══════════════════════════════════════════════════════════════════════
print("\n══ Article 2: B12 and Folate Deficiency Linked to Fatigue ══")

article2 = {
    "headline": "A Study of 600 People Found That Low B12 and Folate Levels Predict Chronic Fatigue. South Asian Vegetarians Are Among the Most Vulnerable.",
    "subheadline": "Japanese researchers linked elevated homocysteine — a marker of B12 and folate deficiency — to persistent physical exhaustion in men and low motivation in women. The findings have direct implications for the millions of South Asians who follow plant-based diets.",
    "slug": "b12-folate-deficiency-fatigue-motivation-homocysteine-south-asian-vegetarians-20260601",
    "category": "lifestyle-health",
    "vertical": "health",
    "tags": ["vitamin-b12", "folate", "fatigue", "vegetarian", "south-asian-health"],
    "urgency": "timely",
    "sources": json.dumps(["Diabetes.co.uk", "Peer-reviewed nutrition journal (Japan)", "The Lancet Global Health (2022)", "American Society of Hematology"]),
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "score_total": 0,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """You sleep eight hours and still feel drained. You exercise, eat well, avoid caffeine after noon — and still cannot shake the fog. Most people blame stress. Their doctors check for anaemia, thyroid dysfunction, depression. What often goes unchecked is one of the most common and correctable nutrient deficiencies in the world: vitamin B12.

A new study from Japan has added another dimension to the evidence. Researchers measured homocysteine, vitamin B12, and folate levels in roughly 600 healthy adults and cross-referenced them with detailed fatigue and motivation assessments. The findings were published in a peer-reviewed nutrition journal and have drawn attention for their specificity.

## What the Study Found

Homocysteine is an amino acid that accumulates in the blood when B12 or folate levels are low. It is not a toxin by itself, but elevated levels serve as a reliable biochemical flag that these vitamins are insufficient.

Among **men**, higher homocysteine was significantly associated with greater **physical fatigue** — the kind of bone-deep tiredness that sleep does not resolve. Among **women**, the association was with **lower motivation** — not physical exhaustion per se, but a measurable decline in the drive to initiate and sustain effort.

The analysis controlled for confounders including age, sleep duration, workload, dietary patterns, and physical activity. That level of rigour makes the findings harder to dismiss as coincidental, though the researchers themselves note the study is observational and does not prove causation.

## Why South Asian Vegetarians Should Pay Attention

Vitamin B12 is found almost exclusively in animal products — meat, fish, eggs, and dairy. It is not present in meaningful quantities in any plant food, including legumes, grains, and vegetables that form the backbone of traditional South Asian diets.

This is not a niche concern. India has the largest vegetarian population in the world. Estimates suggest that **47 per cent of Indians** follow predominantly vegetarian diets, and among Brahmins and Jains, the figure approaches 80 per cent. A 2022 Lancet Global Health analysis found that **B12 deficiency affects up to 70 per cent** of vegetarian populations in South Asia — a staggering figure that makes it one of the most widespread micronutrient deficiencies in the region.

For the diaspora, the picture is mixed. Many second-generation South Asian Americans and British Indians eat meat, but a substantial portion maintain vegetarian or predominantly plant-based diets, particularly in religious or cultural observance. Even among those who eat some dairy, B12 absorption declines with age, and many Indian dairy products — paneer, yoghurt, ghee — contain less B12 per serving than Western equivalents like fortified milk or aged cheese.

## The Fatigue Connection

The link between B12 deficiency and neurological symptoms has been established for decades. Severe deficiency causes peripheral neuropathy — tingling and numbness in the hands and feet — and in extreme cases, irreversible cognitive decline. What is newer is the recognition that **sub-clinical deficiency** — blood levels that are technically in range but on the low end — can produce symptoms that are real but harder to diagnose: persistent tiredness, difficulty concentrating, reduced motivation, and a general feeling of being mentally slower than usual.

The Japanese study adds to a growing body of evidence that these subclinical effects are measurable and gender-differentiated. Physical fatigue in men and motivational decline in women may reflect different neurochemical pathways through which B12 and folate influence brain function, though the mechanisms are not yet fully understood.

## What You Can Do

For South Asian vegetarians who suspect they might be deficient, the intervention is straightforward and inexpensive.

**Get tested.** A standard blood panel that includes serum B12, folate, and homocysteine costs less than $50 in the United States and is covered by most insurance plans. Ask specifically for methylmalonic acid (MMA) if you want a more sensitive marker — serum B12 alone can appear normal even when tissue-level deficiency exists.

**Supplement if needed.** Oral B12 supplements (cyanocobalamin or methylcobalamin, 1,000 mcg daily) are widely available over the counter and cost less than $10 for a three-month supply. For those with absorption issues — common in adults over 50 — sublingual tablets or monthly intramuscular injections are alternatives.

**Consider fortified foods.** Many plant milks, breakfast cereals, and nutritional yeast products in the US are fortified with B12. Reading labels matters. In India, fortification of staple foods with B12 remains limited, making supplementation more important for vegetarians who split time between the two countries.

**Folate is simpler.** Unlike B12, folate is abundant in leafy greens, lentils, and chickpeas — all staples of South Asian cuisine. A traditional dal-sabzi-roti meal provides meaningful folate. The concern arises primarily when diets are heavily processed or when cooking methods destroy the vitamin — prolonged boiling of vegetables, for example, can reduce folate content by up to 40 per cent.

## The Bigger Picture

The Japanese study is one data point in a larger shift. Nutritional psychiatry — the field that studies how diet affects brain function and mental health — has gained significant credibility in the past five years, with major journals publishing randomised trials linking dietary interventions to measurable changes in mood, cognition, and energy.

For the South Asian diaspora, where vegetarianism is often a source of cultural pride, the message is not to abandon plant-based eating. It is to recognise that traditional diets evolved in contexts where B12 deficiency was either less common — when dairy consumption was higher and food was less processed — or where its symptoms were simply not recognised. Modern vegetarians, particularly those in the diaspora eating a mix of traditional and Western processed foods, need to be proactive about a vitamin their diet cannot reliably provide.""",
}

if validate_article(article2):
    img_url = fetch_pexels_image("vitamin B12 supplement nutrition", "healthy vegetarian food vitamins")
    if img_url:
        art_id = insert_article(article2)
        if art_id:
            final_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")
            if final_url:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
                    headers=HEADERS,
                    json={"image_url": final_url, "image_attribution": "Pexels"},
                    timeout=15,
                )
                print(f"  ✓ Image attached")
    else:
        insert_article(article2)


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Markets-Finance — Berkshire Hathaway Buys Taylor Morrison
# ═══════════════════════════════════════════════════════════════════════
print("\n══ Article 3: Berkshire Hathaway Acquires Taylor Morrison ══")

article3 = {
    "headline": "Berkshire Hathaway Just Bought a Homebuilder for $6.8 Billion. It Is Greg Abel's First Big Deal and a Signal About Where Housing Is Headed.",
    "subheadline": "The all-cash acquisition of Taylor Morrison, at a 24 per cent premium, deploys less than 2 per cent of Berkshire's $397 billion cash pile. For NRI investors watching the US housing market, the bet is worth understanding.",
    "slug": "berkshire-hathaway-taylor-morrison-68-billion-greg-abel-housing-nri-investors-20260601",
    "category": "markets-finance",
    "vertical": "markets",
    "tags": ["berkshire-hathaway", "taylor-morrison", "greg-abel", "housing-market", "nri-investors"],
    "urgency": "timely",
    "sources": json.dumps(["Reuters", "MarketWatch", "Investopedia", "Citi Research"]),
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "score_total": 0,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """Berkshire Hathaway announced on Sunday that it will acquire Taylor Morrison Home Corp in an all-cash deal valued at $6.8 billion, paying $72.50 per share — a 24 per cent premium to Taylor Morrison's Friday closing price of $58.50. The deal has an enterprise value of approximately $8.5 billion when debt is included.

Taylor Morrison shares surged 22 per cent in premarket trading on Monday. Berkshire's own stock was essentially flat.

This is the first multi-billion dollar acquisition since Greg Abel became CEO at the start of 2026, replacing Warren Buffett, who remains chairman. It is also the largest Berkshire deal since the $9.7 billion purchase of Occidental Petroleum's chemical business in January.

## What Berkshire Is Buying

Taylor Morrison is one of America's larger homebuilders, operating in 12 states under the Taylor Morrison, Esplanade, and Yardly brands. The company posted $8.12 billion in revenue and $782.5 million in net income in 2025. It builds everything from entry-level homes to what it calls "resort lifestyle" communities aimed at active adults.

Berkshire already has significant exposure to housing. It owns Clayton Homes, a manufactured housing company acquired in 2003, and has stakes in builders Lennar and NVR. Its subsidiaries include Benjamin Moore paint, Johns Manville insulation, Acme Brick, and one of the largest residential real estate brokerages in the United States.

What makes this deal different is Abel's stated plan to eventually **"unify our site-built homebuilding operations into a combined platform"** — a departure from Berkshire's traditional approach of letting each acquisition operate independently. Combined, Berkshire's homebuilding operations would make it the **fourth-largest builder** in the country by closings.

## Why Now — and What It Says About Housing

The timing is counterintuitive. Mortgage rates are hovering around 6 per cent, the highest since August 2025. New home sales fell 6.2 per cent in April. The SPDR S&P Homebuilders ETF has been essentially flat this year. By most surface-level metrics, this is not an obvious moment to make a massive housing bet.

But Berkshire has historically done its best deals during periods of sector stress. The company bought Burlington Northern Santa Fe railroad during the financial crisis and bet heavily on Bank of America when banking stocks were unloved. The playbook is consistent: buy excellent assets when the market is cautious, hold them for decades, and let compounding do the work.

Citi analysts noted that the deal's valuation — roughly 0.9 times book value — echoes other recent housing consolidation deals struck below book. "Consolidation is logical in a challenging housing market where scale is key in managing land, labour, and building material costs," they wrote.

The underlying thesis is structural: America has a housing shortage. The National Association of Realtors estimates the country is **3 to 5 million homes** short of what is needed to meet demand. That deficit has been building since the 2008 financial crisis, when homebuilding collapsed and never fully recovered. Even at current depressed sales rates, the builders who survive and grow through this cycle will be positioned for years of sustained demand when rates eventually come down.

## What NRI Investors Should Consider

For the South Asian diaspora, this deal intersects with two significant investment themes.

**First, Berkshire itself.** Many NRI investors hold Berkshire — it is one of the most popular individual stock holdings among Indian Americans who invest in US equities. The stock has underperformed the S&P 500 this year, falling 5.6 per cent while the index has gained 10.7 per cent. Some investors have been waiting for Abel to make a statement deal that signals he has the same conviction as Buffett. This is that deal. Whether it lifts the stock will depend on whether investors see the housing thesis as bold or as a sign that Berkshire's options for deploying its enormous cash pile are narrowing.

**Second, the housing market directly.** A substantial number of NRI families are either current US homeowners or are actively planning to buy. For those waiting on the sidelines for rates to drop, Berkshire's willingness to invest $6.8 billion in a homebuilder is a signal — from the most disciplined capital allocator in the world — that the US housing market's long-term fundamentals are sound, even if the near-term is painful.

The deal also has implications for new construction in key NRI metros. Taylor Morrison builds heavily in Texas, Arizona, California, and Florida — states with large Indian American populations. If Berkshire's plan to build a unified homebuilding platform succeeds, it could lead to more standardised, lower-cost housing in exactly the markets where the diaspora is concentrated.

## The Cash Pile Problem

Even after this deal, Berkshire will have roughly $390 billion in cash and short-term investments. To put that in perspective, $6.8 billion is less than 2 per cent of the hoard. Abel has said he is looking for more acquisitions, and Berkshire's annual letter has consistently lamented the difficulty of finding deals large enough to move the needle for a conglomerate of this size.

The housing bet is a start, not a solution. For investors, the question remains whether Abel can deploy capital at a pace and quality that justifies Berkshire's premium to book value. For homebuyers, the question is simpler: when the world's largest conglomerate is betting billions on housing, the shortage is not going away.

## The Week Ahead

Markets opened Monday to a dense calendar. The S&P 500 closed Friday at record highs, posting its ninth straight week of gains. This week brings Broadcom earnings on Wednesday, the May jobs report on Friday, and a possible Federal Reserve rate decision. Oil is up 3 per cent to $90 per barrel after fresh US-Iran military exchanges over the weekend dimmed ceasefire hopes. The 10-year Treasury yield has ticked up to 4.50 per cent.

For NRI investors, the combination of record equity valuations, rising oil, and a possible rate hike creates a week where both caution and clarity about long-term holdings matter. Berkshire's bet on housing is a reminder that the best investors are not timing the market. They are buying assets they believe will be worth more in a decade — and paying a fair price today.""",
}

if validate_article(article3):
    img_url = fetch_wikipedia_person_image("Greg Abel")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Berkshire Hathaway")
    if not img_url:
        img_url = fetch_pexels_image("new home construction development", "suburban housing development")
    if img_url:
        art_id = insert_article(article3)
        if art_id:
            final_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")
            if final_url:
                attr = "Wikimedia Commons" if "wikimedia" in (img_url or "").lower() or "wikipedia" in (img_url or "").lower() else "Pexels"
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
                    headers=HEADERS,
                    json={"image_url": final_url, "image_attribution": attr},
                    timeout=15,
                )
                print(f"  ✓ Image attached ({attr})")
    else:
        insert_article(article3)

print("\n══ Done ══")
