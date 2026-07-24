#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 10:00 UTC batch.
Topics:
  1. GLP-1 users move LESS, not more — exercise falls after weight-loss drugs (ENDO 2026) — lifestyle-health
  2. It's not just how much fruit/veg you eat — flavanol quality drives heart benefit (Food & Function, 30,000) — lifestyle-health
  3. RBI's record $110bn FX forward book caps the rupee's oil-driven relief — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000.bin"):
            with open("/tmp/_img_dl1000.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000.bin")
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
# ARTICLE 1: GLP-1 users move LESS, not more (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Weight-Loss Drugs Were Supposed to Get People Moving. A New Study Found They Quietly Sit Down More.",
    "subheadline": "Tracking 753 adults on Ozempic-style medications with fitness monitors, researchers found their daily steps and exercise minutes fell after starting the drugs \u2014 not rose. Because these medications strip away muscle along with fat, the slump is exactly the wrong response, and it carries a sharp warning for the growing number of diaspora families now reaching for them.",
    "slug": "glp-1-ozempic-wegovy-users-exercise-physical-activity-declines-endo-2026-muscle-loss-diaspora-20260619-1000",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GLP-1 drugs like Ozempic and Wegovy are spreading fast through Indian-American and broader diaspora households already at elevated risk of muscle-poor, fat-heavy bodies and early diabetes; this study warns that the very people most drawn to the injections may be undercutting them by moving less, and losing the muscle they can least afford to lose.",
    "sources": json.dumps([
        {"name": "New York Post \u2014 GLP-1 users may be making a major weight-loss mistake, new study suggests (June 2026)", "url": "https://nypost.com/2026/06/18/health/glp-1-users-may-be-making-a-major-weight-loss-mistake/"},
        {"name": "Endocrine Society / ENDO 2026 \u2014 study led by Dr. Sajana Maharjan, HSHS St. John's Hospital, presented in Chicago (June 2026)", "url": "https://www.endocrine.org/news-and-advocacy/news-room"}
    ]),
    "body": """The promise of the new weight-loss drugs was always bigger than the number on the scale. Lose the weight, the thinking went, and people would feel lighter, move more, and build the kind of active life that keeps the pounds off for good. A new study suggests the opposite is quietly happening: people on these medications are moving less, not more.

## What the Researchers Found

The study, presented this week at ENDO 2026, the Endocrine Society's annual meeting in Chicago, is described by its authors as the first of its kind to use objective fitness-tracker data rather than relying on what people say about their habits. Researchers drew on a National Institutes of Health research program that linked participants' medical records with activity recorded by wearable devices, and analysed 753 adults with obesity who started a GLP-1 medication such as semaglutide, liraglutide, dulaglutide or tirzepatide \u2014 the family that includes Ozempic and Wegovy. The group was mostly female, with an average age of about 53.

Comparing each person's activity before and after they began treatment, the picture was consistent and disappointing. Average daily steps fell from 5,047 to 4,487. Moderate-to-vigorous physical activity \u2014 the brisk, heart-raising kind that does the most good \u2014 dropped from 28 minutes a day to 22. The largest declines showed up in men and in people with joint or muscle pain. Age, heart failure and prior stroke did not change the pattern.

"Although many might assume that losing weight with these medications would lead to increased physical activity, our study found no evidence that it did," said study lead Dr. Sajana Maharjan of HSHS St. John's Hospital in Springfield, Illinois.

## Why Sitting Down Is the Wrong Move

This matters more than it might first appear, because of how the drugs work. GLP-1 medications reduce both fat and lean muscle mass. When weight comes off rapidly, a meaningful slice of it is muscle \u2014 the tissue that keeps you strong, steady on your feet, and metabolically healthy as you age.

That is precisely why physical activity, and resistance training in particular, is not an optional add-on for someone on these drugs. It is the main defence against losing strength and muscle along with the fat. "Physical activity is essential for preserving strength and long-term health," Maharjan noted. A person who responds to the drug by moving less is doing the one thing most likely to accelerate muscle loss \u2014 and to leave them weaker, not just lighter.

"The findings in our study reinforce that exercise cannot be optional for people taking these medications," Maharjan said. "People need targeted interventions that encourage physical activity alongside medication for obesity."

## The Caveats

This is preliminary research, presented at a conference rather than yet published in a peer-reviewed journal, and it shows an association rather than proving cause. The study cannot say exactly why activity fell \u2014 reduced appetite and lower energy intake, nausea, or simply the absence of any prompt to exercise could all play a part. The cohort skewed female and middle-aged, so the numbers may differ in other groups. But the direction of the finding, backed by objective device data rather than self-report, is hard to wave away.

## Why the Diaspora Should Pay Attention

GLP-1 drugs are spreading rapidly, and Indian-American and broader South Asian households are very much part of that wave. The community is unusually prone to a body type that carries relatively little muscle and more visceral fat, and to type 2 diabetes that strikes early and at lower weights \u2014 exactly the profile that makes these medications attractive, and exactly the profile that can least afford to lose muscle.

For a diaspora family weighing one of these drugs, the lesson is not to avoid them but to use them properly. The injection handles appetite and weight; it does nothing to build or protect muscle. That job still falls to movement \u2014 ideally strength training two or three times a week alongside regular walking, and enough protein to support what exercise builds. Treat the drug as one half of a plan, not the whole of it. The people who do best on these medications are likely to be those who keep moving while the weight comes off, not those who let the needle do all the work."""
})

# ============================================================
# ARTICLE 2: Flavanol quality, not just quantity, drives heart benefit (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Eating Your Five-a-Day May Not Be Enough. A 30,000-Person Study Says It Is the Right Plants That Protect the Heart.",
    "subheadline": "An international study measuring actual blood markers in more than 30,000 people in Britain and America found that fewer than one in five get enough flavanols \u2014 the plant compounds tied to lower cardiovascular risk \u2014 even among many who hit their fruit-and-vegetable targets. For the diaspora, the fix lies in foods already close at hand: tea, apples, berries and dark chocolate.",
    "slug": "flavanols-fruit-vegetable-quality-heart-health-food-function-30000-reading-harvard-diaspora-20260619-1000",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Diaspora families are told endlessly to eat more fruit and vegetables, but this research shows the protective payoff depends on which plants \u2014 and the richest everyday sources of heart-friendly flavanols, led by tea, are already staples in South Asian homes if chosen with intent.",
    "sources": json.dumps([
        {"name": "SciTechDaily \u2014 Your Diet Could Be Missing the Key Ingredient for Heart Protection (June 2026)", "url": "https://scitechdaily.com/your-diet-could-be-missing-the-key-ingredient-for-heart-protection/"},
        {"name": "Food & Function \u2014 flavanol biomarker analysis of 30,000+ adults in the UK and US (University of Reading, Harvard Medical School, UC Davis, Mars Inc., 2026)", "url": "https://pubs.rsc.org/en/journals/journalissues/fo"}
    ]),
    "body": """The advice has been the same for a generation: eat more fruit and vegetables, aim for your five a day, and your heart will thank you. A large new study does not overturn that, but it adds a crucial twist \u2014 when it comes to the heart, which plants you choose may matter as much as how many.

## What the Study Measured

Researchers from the University of Reading, Harvard Medical School, the University of California, Davis, and the food company Mars, Inc. examined data from more than 30,000 people in the United Kingdom and the United States. Crucially, instead of relying only on the notoriously unreliable food questionnaires people fill in about what they eat, the team measured biomarkers in the body \u2014 objective chemical signatures that reveal how much of certain compounds a person is actually getting.

The compounds in question are flavanols, naturally occurring plant chemicals found in foods such as tea, apples, berries, grapes and cocoa. A growing body of evidence links them to better blood-vessel function, lower blood pressure and reduced cardiovascular risk. The study was published in the journal Food & Function.

The headline finding was stark. Fewer than one in five participants consumed enough flavanols to reach the levels previously associated with meaningful heart benefits. More striking still, that shortfall persisted even among many people who were comfortably meeting the recommended targets for fruit and vegetable intake. In other words, you can eat your five a day and still fall short of the specific compounds that do some of the heaviest lifting for cardiovascular health.

## Quantity Versus Quality

This is the heart of the study's message. Healthy-eating campaigns have long focused on quantity \u2014 more servings, more colour on the plate. But not all fruits and vegetables are equal in flavanol content. A diet heavy in, say, potatoes and bananas can hit a serving target while delivering relatively little of these particular compounds, whereas a cup of tea, a handful of berries or an apple punches well above its weight.

The finding helps explain a long-standing puzzle in nutrition research: why studies of overall fruit and vegetable intake sometimes show weaker heart benefits than expected. If the protective effect is concentrated in specific compounds found in only some plants, then counting servings alone will always be a blunt instrument.

## The Caveats

This was an observational study built on biomarker and dietary data, so it maps associations rather than proving that raising flavanol intake will lower any individual's risk of heart disease. One of the funders, Mars, Inc., has a commercial interest in cocoa flavanols, which is worth noting even though the use of objective biomarkers across tens of thousands of people lends the work real weight. And flavanols are not a magic bullet \u2014 they sit within a wider pattern of diet, activity and genetics that together shape heart health.

## Why It Matters for the Diaspora

For Indian and South Asian families, who face heart disease earlier and more often than most populations, the practical takeaway is unusually convenient: the single richest everyday source of dietary flavanols is tea \u2014 already brewed in vast quantities in diaspora kitchens. The catch is in the preparation. The flavanol benefit comes from the tea itself, not from drowning each cup in sugar and heavy cream, and the same logic applies to cocoa, where dark chocolate carries the compounds that milk chocolate largely loses.

The broader lesson reframes the familiar advice. Eating more plants is still right, but the diaspora can do better by leaning toward the flavanol-rich ones \u2014 tea, apples, berries, grapes and good dark chocolate \u2014 rather than treating all produce as interchangeable. It is not about eating more so much as eating smarter, and many of the best choices are already sitting in the pantry."""
})

# ============================================================
# ARTICLE 3: RBI's record FX forward book caps the rupee (markets-finance)
# ============================================================
articles.append({
    "headline": "Cheaper Oil Should Be Lifting the Rupee. India's Own Central Bank Is Quietly Holding It Back.",
    "subheadline": "The Reserve Bank of India's short-dollar forward book has ballooned to a record near $110 billion, and unwinding it \u2014 along with hedging the dollars Indian banks are now borrowing abroad \u2014 is set to cap the rupee's recovery even as oil sits at three-month lows. For NRIs, it explains why the currency has steadied near 94.5 rather than surged.",
    "slug": "rbi-record-fx-forward-book-110-billion-caps-rupee-oil-relief-reserves-nri-investor-20260619-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "NRIs watching the rupee to time remittances, deposits and Indian investments need to understand why a clear tailwind \u2014 cheap oil \u2014 is not translating into a stronger currency: the RBI's record forward-book overhang means dollar inflows are being absorbed to rebuild reserves rather than allowed to lift the rupee.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian rupee's oil relief capped by RBI's FX book, interest payment hedges, bankers say (June 2026)", "url": "https://www.reuters.com/markets/currencies/"},
        {"name": "The Hindu BusinessLine \u2014 Rupee's oil relief capped by RBI's FX book, interest payment hedges, bankers say (June 2026)", "url": "https://www.thehindubusinessline.com/markets/forex/"}
    ]),
    "body": """On paper, the Indian rupee should be having a good month. Global oil prices \u2014 the single biggest swing factor for a country that imports most of its crude \u2014 have slid to three-month lows, easing the import bill that usually drags the currency down. Yet the rupee has only recovered to around 94.5 per dollar, well off the gains such a drop might imply. The reason lies inside the Reserve Bank of India's own balance sheet.

## The Record Forward Book

At the centre of the story is a piece of central-bank plumbing called the forward book. To defend the rupee over the past year, the RBI intervened heavily in currency markets, much of it through forward contracts and the offshore non-deliverable forward market rather than by selling dollars outright on the spot market. The result is a short-dollar forward book that, according to two officials at foreign banks, has swollen to an all-time high of nearly $110 billion \u2014 up from about $96 billion in April.

That position now has to be managed, and unwinding it works against the currency. As those forward contracts mature, the RBI is expected to use periods of rupee strength to rebuild its spot foreign-exchange reserves and pare down the book, rather than letting the currency run higher. India's reserves have fallen from a peak of $728.5 billion in March to $681.6 billion, giving the central bank every incentive to soak up incoming dollars rather than spend the currency's good fortune on a rally.

## The Second Drag: Hedging the Banks' Dollars

There is a second, related weight on the rupee, and it stems from a policy the RBI itself introduced to help the currency. The central bank recently opened a subsidised hedging window encouraging Indian banks and state-run firms to borrow dollars overseas \u2014 a scheme HDFC Bank has already used to price a $750 million bond, with State Bank of India and Bank of Baroda lining up similar deals.

Those inflows are welcome, but the currency risk attached to them does not disappear; it is passed to the RBI through dollar-rupee swaps. Hedging that risk and the interest obligations on foreign-currency deposits raised by banks adds further to the forward-book overhang. The very inflows designed to support the rupee, in other words, also commit the central bank to absorbing them rather than allowing a sharp appreciation.

## What the Analysts Expect

The market consensus is that the rupee's upside is capped, not that it is in danger. "We do not expect a significant appreciation in the INR" on the back of these inflows, analysts at Goldman Sachs wrote, noting the flows "are likely to be absorbed by the RBI through rebuilding of its FX buffers, including unwinding a significantly large short dollar forward book." Sakshi Gupta, principal economist at HDFC Bank, made the same point: the drive to rebuild reserves alongside the forward-book overhang will be a drag that keeps the currency's gains limited.

The picture is not all negative. Economists have actually upgraded their forecasts for India's balance of payments following the RBI's interventions, with most now expecting a small surplus \u2014 a sharp reversal from earlier projections of a deficit. The currency has firmed from an all-time low near 97 last month. The point is simply that a steadier rupee, not a soaring one, is the realistic outcome.

## What It Means for the Diaspora

For NRIs, this is the difference between expectation and reality. The intuitive read \u2014 oil is cheap, so the rupee should jump and remittances sent home will buy less \u2014 does not hold this time, because the RBI is deliberately leaning against that move to repair its reserves and unwind its forwards.

For anyone timing a large remittance, a deposit decision or an investment into India, the takeaway is that the rupee is likely to trade in a steadier, range-bound fashion near current levels rather than stage a dramatic recovery. That stability is, on balance, a feature rather than a bug: the central bank is signalling that it wants to rebuild its defences and avoid the wild swings of the past year. The era of betting on a sharp rupee rally on the back of a single tailwind looks, for now, to be on hold \u2014 by design."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["semaglutide injection pen", "Ozempic injection pen", "insulin pen injection diabetes"],
                          ["weight loss injection pen", "medication injection pen hand"], None),
    articles[1]["slug"]: (["fresh fruits and vegetables assortment", "berries apples grapes fruit", "green tea cup leaves"],
                          ["colorful fruits vegetables berries", "fresh berries apples"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee banknotes currency", "Indian rupee money"],
                          ["indian rupee currency notes", "indian rupee money"], None),
}
img_captions = {
    articles[0]["slug"]: "An injection pen; a study of 753 GLP-1 users found their daily steps and exercise fell after starting the drugs",
    articles[1]["slug"]: "Fruits rich in flavanols; a 30,000-person study found most people fall short of the plant compounds tied to heart health",
    articles[2]["slug"]: "Indian rupee currency; the RBI's record forward book is set to cap the rupee's recovery despite cheaper oil",
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
