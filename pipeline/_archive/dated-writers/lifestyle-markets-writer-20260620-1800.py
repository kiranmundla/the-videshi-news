#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 18:00 UTC batch.
Topics:
  1. ENDO 2026 (Chicago; Diego Espinoza-Peralta, Mexican Society of Nutrition & Endocrinology):
     menopausal hormone therapy linked to ~69% lower risk of low bone mineral density
     in hips/spine in 387 postmenopausal women (DXA, 2021-2025) — lifestyle-health
  2. JCEM (Ruth Frikke-Schmidt, Copenhagen): Mendelian-randomization study of 500,000+
     adults finds high BMI and high blood pressure are DIRECT causes of vascular dementia,
     not just markers — lifestyle-health
  3. FPI flows turn net positive in India this week (₹1,209 cr inflow, Jun 16-20, NSDL)
     as Nifty/Sensex rally on US-Iran peace deal + softer oil, after a record $30.8bn
     2026 outflow — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0620e.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0620e.bin"):
            with open("/tmp/_img_dl0620e.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0620e.bin")
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
# ARTICLE 1: Hormone therapy protects bone density (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Hormone Therapy May Quietly Be Protecting Older Women's Bones, a New Study Finds",
    "subheadline": "Postmenopausal women on hormone therapy were about 69 percent less likely to have low bone density in their hips and spine, according to research presented at the Endocrine Society's annual meeting \u2014 a reminder that menopause reshapes the skeleton long before any fracture.",
    "slug": "menopausal-hormone-therapy-69-percent-lower-low-bone-density-dxa-endo-2026-women-diaspora-20260620-1800",
    "category": "lifestyle-health",
    "vertical": "womens-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian women tend to reach lower peak bone mass and develop osteoporosis at younger ages and lower body weights than many other groups, yet hormone therapy remains stigmatised and under-discussed in many Indian families \u2014 making this fresh evidence on its skeletal benefits especially relevant for NRI women navigating menopause far from extended family support.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 Hormone therapy may help older women keep their bones strong (ENDO 2026; Diego Espinoza-Peralta)", "url": "https://knowridge.com/2026/06/hormone-therapy-help-older-women-keep-their-bones-strong/"},
        {"name": "Endocrine Society \u2014 ENDO 2026 annual meeting research presentations", "url": "https://www.endocrine.org/news-and-advocacy/news-room"}
    ]),
    "body": """Menopause is most often talked about in terms of hot flashes and mood swings. But one of its most consequential effects unfolds silently, deep inside the body: bones begin to lose their strength. New research presented at ENDO 2026, the Endocrine Society's annual meeting in Chicago, suggests that menopausal hormone therapy may do far more than ease the familiar symptoms \u2014 it may also help keep ageing bones intact.

## Why Bones Weaken After Menopause

Healthy bone looks solid, but it is in fact constantly remodelling itself: old bone is broken down and new bone is built up in a lifelong cycle. Estrogen helps keep that balance tilted toward building. When estrogen levels fall sharply after menopause, the scale tips the other way, and bones can lose minerals year after year.

That gradual erosion leads first to osteopenia, an early stage of bone loss, and then potentially to osteoporosis, in which bones become fragile and break easily. A stumble that would have caused a bruise in younger years can fracture a hip, wrist or spine. Hip fractures in particular can be life-altering: some older adults never fully regain their mobility or independence afterward.

## What the New Study Found

The researchers reviewed 387 postmenopausal women who had undergone bone-density scans, known as DXA scans, between 2021 and 2025. About a third of the women were using menopausal hormone therapy; the remaining two-thirds were not.

The difference was striking. Women on hormone therapy were roughly 69 percent less likely to show low bone mineral density in their hips and spine than women who were not using it. Crucially, the finding held up even after the researchers adjusted for other things that shape bone health \u2014 age, vitamin D levels, smoking, how long it had been since menopause, and other medical conditions.

"The findings suggest that hormone therapy itself may help protect bones," said Dr. Diego Espinoza-Peralta, who led the study and serves as vice president of the Mexican Society of Nutrition and Endocrinology, rather than the benefit being explained away by other factors.

## A Treatment That Fell Out of Favour

Hormone therapy has been used for decades to relieve hot flashes, night sweats and disrupted sleep. But its use dropped sharply after early studies raised concerns about possible risks, and many women have remained wary ever since. A growing body of more recent research has been re-examining the treatment, and this study adds to the case that, for some women, it may offer two benefits at once: relief from menopausal symptoms and stronger bones.

The researchers were careful about the limits of their work. Because the study was retrospective \u2014 looking back at existing scans rather than randomly assigning treatment \u2014 it cannot prove that hormone therapy caused the better bone density. The number of women was also relatively modest, and larger trials are needed to confirm the effect. Hormone therapy is not right for everyone, and the decision depends on a woman's age, personal and family medical history, and individual risk factors.

## Why It Matters for the Diaspora

For Indian and wider South Asian women, the message is worth pausing on. Research has repeatedly shown that South Asians tend to reach a lower peak bone mass and can develop osteoporosis earlier and at lower body weights than many Western populations \u2014 a vulnerability often compounded by low vitamin D levels and diets that can fall short on calcium.

Yet menopause and hormone therapy remain awkward, under-discussed subjects in many Indian households. For NRI women going through the transition far from the extended family networks that once carried this knowledge informally, the practical takeaway is to treat bone health as an active project, not an afterthought: ask for a DXA scan around menopause, keep up weight-bearing and resistance exercise, stay on top of calcium and vitamin D, and have an honest conversation with a doctor about whether hormone therapy fits their own risk profile. The bones lost in silence in the years after menopause are far harder to rebuild than to protect."""
})

# ============================================================
# ARTICLE 2: Obesity + high blood pressure as direct causes of dementia (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Carrying Extra Weight Does Not Just Raise Dementia Risk \u2014 It May Directly Cause It, a Study of 500,000 People Finds",
    "subheadline": "Using a genetics-based method that mimics a randomised trial, researchers concluded that high body weight and high blood pressure are not merely warning signs but direct causes of vascular dementia \u2014 making them, in the authors' words, an \u201cunexploited opportunity\u201d for prevention.",
    "slug": "high-bmi-blood-pressure-direct-cause-vascular-dementia-mendelian-randomization-jcem-500000-diaspora-20260620-1800",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry abdominal fat and develop high blood pressure and diabetes at lower body-mass thresholds than other populations, often a decade earlier \u2014 so a study identifying excess weight and hypertension as direct, modifiable causes of dementia speaks straight to a diaspora that already lives with elevated cardiometabolic risk.",
    "sources": json.dumps([
        {"name": "The Journal of Clinical Endocrinology & Metabolism \u2014 High Body Mass Index as a Causal Risk Factor for Vascular-Related Dementia: A Mendelian Randomization Study (Ruth Frikke-Schmidt et al.)", "url": "https://academic.oup.com/jcem"},
        {"name": "Endocrine Society \u2014 People with obesity may have a higher risk of dementia", "url": "https://www.endocrine.org/news-and-advocacy/news-room"},
        {"name": "Medical News Today \u2014 Vascular dementia: Keeping weight in check may aid prevention", "url": "https://www.medicalnewstoday.com/"}
    ]),
    "body": """For years, doctors have noted that people who are overweight or have high blood pressure tend to face a higher risk of dementia. The open question was always whether those conditions actually cause the brain decline, or whether they simply travel alongside it. A study in The Journal of Clinical Endocrinology & Metabolism now offers an unusually firm answer: high body weight and high blood pressure appear to be direct causes of vascular dementia, not just companions to it.

## How the Researchers Got to "Cause"

Proving cause and effect in human health is notoriously hard, because people who are heavier or have higher blood pressure differ in countless other ways \u2014 diet, exercise, income, illness \u2014 that can muddy any link. To cut through that, the team led by Dr. Ruth Frikke-Schmidt, chief physician at Copenhagen University Hospital\u2013Rigshospitalet and professor at the University of Copenhagen, used a technique called Mendelian randomization.

The method leans on a quirk of genetics. Certain common gene variants nudge a person toward a higher body mass index, and those variants are handed down from parents to children essentially at random \u2014 much as a drug-versus-placebo assignment is randomised in a clinical trial. By tracking whether people who inherited "higher-BMI" gene variants also went on to develop dementia, the researchers could test for a causal link while sidestepping the lifestyle confounders that trip up ordinary observational studies. They drew on data from more than 500,000 people taking part in long-term health studies in Denmark and the United Kingdom.

## What They Found

The results were consistent across multiple datasets and analytic methods. A higher BMI was directly linked to vascular dementia \u2014 the form caused by reduced or blocked blood flow to the brain \u2014 with the risk running, depending on the group and method, from roughly 54 percent to nearly double.

The study also pinpointed how much of that danger flows through blood pressure. Elevated systolic pressure (the top number) accounted for about 18 percent of the link between high BMI and vascular dementia, and elevated diastolic pressure (the bottom number) for about 25 percent. In other words, a substantial chunk of the harm that excess weight does to the brain appears to travel along the pipeline of high blood pressure.

"This study shows that high body weight and high blood pressure are not just warning signs, but direct causes of dementia," Frikke-Schmidt said. "The treatment and prevention of elevated BMI and high blood pressure represent an unexploited opportunity for dementia prevention."

## Why This Is Hopeful News

There is no cure for dementia, and the disease steals memory, language and independence as it progresses. That makes prevention the most powerful lever available \u2014 and this study reframes two of the most common, treatable conditions in modern life as genuine targets for protecting the brain. Losing weight and controlling blood pressure are not glamorous interventions, but they are within reach for most people through diet, physical activity, and, where needed, medication.

One caveat: the study population was of European ancestry, so the precise numbers may not transfer directly to other groups, and more data across populations is needed.

## Why It Matters for the Diaspora

That caveat is exactly where the diaspora angle sharpens. South Asians are known to accumulate fat around the abdomen and to develop high blood pressure, insulin resistance and type 2 diabetes at lower body weights and younger ages than many other populations \u2014 the so-called "thin-fat" phenotype. A person of Indian origin can look slim on the scale while carrying the very metabolic risks this study links to brain decline.

For NRIs in the United States, Britain, Canada and the Gulf, the practical lesson is to treat waistline and blood pressure as brain-health numbers, not just heart-health ones. Regular blood-pressure checks, attention to abdominal weight rather than the bathroom scale alone, and early action on borderline readings are cheap, available tools. The same habits that protect the heart, this research suggests, may also be quietly defending the mind."""
})

# ============================================================
# ARTICLE 3: Foreign investors turn net buyers this week (markets-finance)
# ============================================================
articles.append({
    "headline": "After a Record Exodus, Foreign Investors Tiptoed Back Into Indian Stocks This Week",
    "subheadline": "Foreign portfolio investors bought a net \u20b91,209 crore of Indian equities in the week to June 20 \u2014 a small but symbolically important turn after dumping a record $30 billion-plus through 2026, as a US-Iran peace deal and cheaper oil revived appetite for emerging markets.",
    "slug": "foreign-investors-turn-net-buyers-1209-crore-india-equities-us-iran-peace-oil-nifty-rally-nri-investor-20260620-1800",
    "category": "markets-finance",
    "vertical": "markets",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many NRIs hold Indian equities directly or through mutual funds and India-focused ETFs abroad, so a tentative reversal in foreign flows \u2014 the single biggest swing factor for Indian stocks this year \u2014 matters directly to diaspora portfolios and to anyone weighing whether the worst of 2026's sell-off is behind them.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian shares continue to rise as softer oil overpowers hawkish Fed", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "LiveMint / ANI \u2014 Foreign investors infuse \u20b91,209 cr in Indian equities this week; June net outflow at \u20b94,192 cr: NSDL", "url": "https://www.livemint.com/market/stock-market-news"}
    ]),
    "body": """For most of 2026, the story of India's stock market has been one of foreign money heading for the exits. So a modest line in the latest depository data carried outsized weight: in the week to June 20, foreign portfolio investors turned net buyers of Indian equities, pumping in a net \u20b91,209 crore. After months of relentless selling, even a small inflow felt like a change in the weather.

## The Scale of What Came Before

To appreciate why a roughly \u20b91,200-crore inflow is news, consider the backdrop. Foreign investors have offloaded a record sum from Indian stocks this year \u2014 figures cited through the period ran past $30 billion, an exodus driven by a spike in oil prices tied to Gulf hostilities, a sliding rupee, India's thin exposure to the artificial-intelligence boom that has powered Wall Street, and the lure of higher returns elsewhere. At one stretch, foreigners sold for 13 straight sessions.

That selling pressure is the single biggest reason Indian benchmarks underperformed many emerging-market peers for much of the year. So when the tide even briefly turned, markets noticed.

## What Changed

Two forces did most of the work. First, a preliminary US-Iran peace deal cooled the geopolitical temperature and sent oil prices tumbling \u2014 Brent fell to around $78 a barrel, a meaningful relief for India, which imports the bulk of its crude. Cheaper oil eases the pressure on India's import bill, its current account and its inflation outlook, all of which had been spooking investors.

Second, India's own policy machinery has been working to draw foreigners back, with the government and the Reserve Bank floating measures to support the rupee, attract foreign money into bonds, and review the long-term capital-gains tax. Analysts said the combination revived risk appetite. The benchmark Nifty 50 climbed to around 24,168 and the Sensex to roughly 77,410 by Thursday's close, with the indices gaining more than 4 percent over five sessions on the back of softer crude.

Market watchers attributed the week's foreign inflows partly to large block deals on offer and to buying linked to an FTSE index rebalancing, with notable activity on Wednesday and Friday. "Overall the Indian economy stands strong, driven by healthy economic growth, multi-year-low inflation, a rate cut by the RBI, as well as prospects of an above-normal monsoon," said Siddhartha Khemka of Motilal Oswal Financial Services.

## Not Out of the Woods

The turn is real but fragile. For the month of June as a whole, foreign investors remained net sellers, with outflows of about \u20b94,192 crore as of June 20 \u2014 though even that marked an improvement on the previous week's heavier \u20b95,402-crore outflow, a sign that the bleeding is at least slowing.

There are headwinds too. The US Federal Reserve paused rates but signalled a possible hike later in the year, which can sap foreign appetite for emerging markets like India and squeeze the overseas budgets that Indian IT exporters depend on. A weaker monsoon would pose an upside risk to inflation. And much of the geopolitical calm rests on a peace deal that is still preliminary.

## Why NRIs Should Care

For the diaspora, foreign flows are not an abstraction \u2014 they are, in many cases, their own money. Large numbers of NRIs hold Indian equities directly or through domestic mutual funds and India-focused ETFs listed abroad, and foreign-investor sentiment is the dominant short-term driver of where the broader market goes.

This week's data does not signal an all-clear; one positive week against a year of record selling is a flicker, not a trend. But for diaspora investors who watched their India holdings get battered through 2026, it offers the first tentative evidence that the conditions behind the sell-off \u2014 expensive oil, a falling rupee, geopolitical fear \u2014 may be starting to ease. Whether the flicker becomes a turn will depend on oil staying cheap, the rupee holding firm, and the monsoon behaving. For now, the smart posture is the one long-term investors always favour: watch the trend, not the day, and let the fundamentals \u2014 not the headlines \u2014 set the pace."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["bone density scan DXA osteoporosis", "human spine bone xray", "older woman doctor consultation"],
                          ["bone health osteoporosis xray", "senior woman health checkup"], None),
    articles[1]["slug"]: (["blood pressure measurement cuff", "human brain MRI scan", "doctor measuring blood pressure patient"],
                          ["blood pressure monitor measurement", "brain scan medical"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "stock market trading screen India", "indian rupee currency notes"],
                          ["stock market trading screen", "indian rupee currency finance"], None),
}
img_captions = {
    articles[0]["slug"]: "Researchers found postmenopausal women on hormone therapy had far lower odds of low bone density on DXA scans",
    articles[1]["slug"]: "A study of more than 500,000 people linked high BMI and blood pressure directly to vascular dementia risk",
    articles[2]["slug"]: "Foreign investors turned net buyers of Indian equities in the week to June 20 after a record 2026 sell-off",
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
