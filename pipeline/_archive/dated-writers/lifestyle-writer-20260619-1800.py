#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 18:00 UTC batch.
Topics:
  1. Nature Metabolism review of 1.5M cancer cases: high BMI now linked to 19 cancers (up from 13) — lifestyle-health
  2. ENDO 2026: GLP-1 weight-loss drugs may raise testosterone + improve sperm quality in men with obesity — lifestyle-health
  3. AMFI: SIP inflows hit all-time high Rs 26,688 cr in May even as equity fund inflows slump to 12-month low — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0619b.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0619b.bin"):
            with open("/tmp/_img_dl0619b.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0619b.bin")
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
# ARTICLE 1: Obesity now linked to 19 cancers (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Carrying Extra Weight Now Linked to 19 Cancers, Not 13 \u2014 and South Asians Show Up in the Fine Print",
    "subheadline": "Pooling more than 1.5 million cancer cases across 23 countries, a sweeping new review widens the list of weight-related cancers and finds the risks differ sharply by sex and region \u2014 with striking gaps in data on South Asian populations.",
    "slug": "obesity-bmi-linked-19-cancers-nature-metabolism-review-1-5-million-cases-south-asia-diaspora-20260619-1800",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians develop diabetes and heart disease at lower body weights than Western populations, yet this very review flags that South Asia is badly under-represented in long-term cancer data \u2014 meaning diaspora families are being handed risk numbers built largely on European and East Asian bodies, and should treat even a modest waistline as a cancer-prevention issue, not just a cosmetic one.",
    "sources": json.dumps([
        {"name": "Nature Metabolism \u2014 Adiposity and cancer: systematic review and meta-analysis (2026)", "url": "https://www.nature.com/articles/s42255-026-01542-8"},
        {"name": "News-Medical \u2014 Higher BMI raises risk for 19 cancers as global review expands the obesity-cancer link", "url": "https://www.news-medical.net/news/20260617/Higher-BMI-raises-risk-for-19-cancers-as-global-review-expands-the-obesity-cancer-link.aspx"}
    ]),
    "body": """For years, the warning that carrying extra weight raises the risk of cancer came with a tidy number attached: 13 types. That figure, endorsed by the World Cancer Research Fund and the International Agency for Research on Cancer, has anchored public-health messaging for over a decade. A vast new analysis says the real number is higher \u2014 and that the picture looks different depending on who you are and where you live.

## What the Researchers Did

The study, published in *Nature Metabolism*, is one of the largest of its kind ever assembled. Researchers pooled data from 226 peer-reviewed studies covering more than **1.5 million documented cancer cases** across 23 countries and six world regions, capturing 557 separate links between body mass index (BMI) and cancer across 25 common cancer types.

To make the numbers comparable, every result was standardised to the effect of a **5-unit rise in BMI** \u2014 roughly the difference between a healthy weight and the lower end of obesity for many adults. And because observational data can only show correlation, the team layered in Mendelian randomization, a technique that uses inherited genetic variants as stand-ins for lifelong weight, to probe whether the links were likely to be causal. Smoking-related cancers were checked using data only from lifelong never-smokers, to strip out tobacco as a hidden driver.

## What They Found

Higher BMI was significantly linked to **19 distinct cancer types** \u2014 six more than the 13 in current consensus statements. Newly implicated were leukemia, non-Hodgkin lymphoma, bladder cancer and glioma, a type of brain tumour, none of which had previously been on the official list.

The strength of the link varied enormously \u2014 nearly 20-fold across cancer types. At the extreme, each 5-unit rise in BMI was tied to a **58 percent higher risk of endometrial cancer** and a 47 percent higher risk of one form of oesophageal cancer. (The review also reported some inverse associations, including lower premenopausal breast cancer risk, which scientists think reflects the complex way body fat interacts with hormones at different life stages.)

## The Regional Twist That Matters Most

The finding most relevant to the Indian diaspora is not a single number but a warning about the numbers themselves. The review found that risk is **not uniform across populations**. Postmenopausal breast cancer risk tied to rising BMI was roughly double in East Asian women compared with European women. Colorectal cancer risk rose more steeply in men than women; gallbladder cancer risk rose more steeply in women.

Crucially, the authors flagged that **South Asia, Africa and Central America remain badly under-represented** in the long-term cancer data \u2014 even in this expanded review. In plain terms: the risk estimates the world relies on were built largely on European and East Asian bodies. For people of Indian origin, who already metabolise body fat differently, that is a real gap, not an academic footnote.

## Why It Hits Home for the Diaspora

South Asians are known to carry a "thin-fat" body composition \u2014 more visceral fat and less muscle for a given weight \u2014 and develop diabetes and heart disease at lower BMIs than many other groups. Standard BMI cut-offs already under-estimate metabolic risk in Indian-origin people, which is why Indian health guidelines use a lower obesity threshold (BMI 25) than Western ones (BMI 30).

This review extends that logic to cancer. If body fat is biologically more harmful at lower weights in South Asians, then the cancer risk attached to a "slightly heavy" reading on the scale may be understated for diaspora families relying on Western charts.

## The Caveats Worth Keeping

This is a review of observational studies, and even with genetic analysis layered on, it shows strong, consistent association rather than airtight proof for every cancer. BMI is also a blunt tool \u2014 though notably, the study found waist circumference performed about as well as BMI in predicting risk, reinforcing that where fat sits matters.

## What To Actually Do

The practical message is unchanged but sharpened: keeping weight and especially waistline in a healthy range is one of the most powerful, modifiable levers against cancer \u2014 alongside not smoking. For diaspora families, two specifics matter. First, use **South Asian-specific BMI and waist cut-offs** (a waist over 90 cm for men and 80 cm for women signals raised risk) rather than Western ones. Second, treat the usual healthy habits \u2014 mostly plants, minimal ultra-processed food, regular movement, decent sleep \u2014 not as vanity projects but as the cheapest cancer-prevention tools available. The list of cancers tied to weight just got longer; the playbook for lowering the risk did not."""
})

# ============================================================
# ARTICLE 2: GLP-1 drugs & male fertility / testosterone (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Weight-Loss Drugs May Do Something Unexpected for Men: Lift Testosterone and Improve Sperm",
    "subheadline": "Early data presented at a major endocrinology meeting suggests GLP-1 medicines like Ozempic may raise testosterone and improve sperm quality in men with obesity \u2014 a tentative finding in a field where male fertility is rarely discussed openly.",
    "slug": "glp-1-weight-loss-drugs-testosterone-sperm-quality-men-obesity-endo-2026-fertility-diaspora-20260619-1800",
    "category": "lifestyle-health",
    "vertical": "mens-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Male infertility is one of the most stigmatised and silently borne health issues in Indian families, where the burden of childlessness is too often placed on women; framing it as a treatable, hormonally-influenced medical condition \u2014 one that weight and metabolic health can move \u2014 gives diaspora couples a less shame-laden, more clinical way to seek help.",
    "sources": json.dumps([
        {"name": "People \u2014 Study Shows GLP-1 Medications Could Boost Male Testosterone Levels and Sperm Count", "url": "https://people.com/study-shows-glp-1-medications-boosted-male-testosterone-levels-and-sperm-count-11998939"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (research presentations)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """The weight-loss drugs that have reshaped how the world treats obesity may carry an unexpected bonus for men. New research suggests that GLP-1 medications \u2014 the class that includes Ozempic and Wegovy \u2014 could raise testosterone levels and improve sperm quality in men carrying excess weight. The finding is preliminary, but it touches a subject Indian families rarely talk about out loud: male fertility.

## What the Researchers Found

The data, presented at **ENDO 2026**, the Endocrine Society's annual meeting in Chicago, tracked men aged 18 to 65 who were prescribed GLP-1 medications over **24 weeks** of treatment. According to co-author Dr. Pratibha Natesh, an endocrinologist at Warwick Medical School in the UK, the men showed measurable improvements in testosterone levels, sperm count, and the size and shape of their sperm \u2014 all key markers of male fertility.

The researchers suggested the benefit may come not just from weight loss itself, but from the way these drugs **reduce inflammation and metabolic stress**, both of which can suppress sperm production. That distinction matters, because it hints the drugs might help through more than one biological route.

## Why This Is Notable

For men with obesity, the usual medical option for low testosterone has been testosterone replacement therapy. But that treatment carries a paradox: supplemental testosterone can actually **suppress the body's own sperm production**, making it a poor choice for men who want to father children. A medication that lifts testosterone naturally, while improving sperm quality rather than harming it, would be a meaningful alternative.

Dr. Lidia M\u00ednguez Alarc\u00f3n of Brigham and Women's Hospital and Harvard Medical School, who was not involved in the study, called the results promising, noting that good semen quality and healthy testosterone have long been tied to better overall health in men.

## The Caveats Are Significant

This research is at an early stage, and the scientists themselves stress that more data and controlled trials are needed before anyone draws firm conclusions. It was presented at a conference, a stage where findings are shared before full peer-reviewed publication.

There is also a genuine counter-signal worth stating plainly. Dr. Amin Herati, director of male infertility and men's health at Johns Hopkins Hospital, who was not part of the research, cautioned that **sudden, rapid weight changes** \u2014 whether from bariatric surgery or GLP-1 drugs \u2014 can in some cases temporarily harm fertility. The likely reconciliation is that gradual, sustained improvement in metabolic health helps, while crash-style weight loss may not. No man trying to conceive should start or stop a medication on the strength of one conference abstract.

## Why It Resonates in Diaspora Homes

Male infertility affects an estimated 186 million people worldwide and, by some estimates, plays a role in about half of all couples who struggle to conceive. Yet in many Indian families, it remains one of the most stigmatised and least-discussed health topics. The cultural weight of childlessness is too often placed on women, while the possibility of a male factor goes unexamined \u2014 sometimes for years.

Reframing fertility as a **treatable medical condition tied to metabolic health**, rather than a source of private shame, can change that conversation. South Asian men carry high rates of obesity-linked metabolic disease, often at lower body weights, which makes the link between weight, hormones and fertility especially relevant for the community.

## What To Actually Do

The takeaway is not "ask your doctor for Ozempic to have a baby." It is that **metabolic health and fertility are connected**, and that the connection is becoming better understood. Men who are overweight and struggling to conceive should seek a proper evaluation rather than assuming the issue lies elsewhere. The evidence-backed basics still apply for everyone: regular exercise, less ultra-processed food, limiting sedentary time, avoiding excessive heat to the groin (hot tubs, laptops on laps), and reducing exposure to toxic chemicals. For some men, getting metabolic health under control \u2014 with or without medication, under a doctor's guidance \u2014 may turn out to do double duty. And simply making male fertility a topic that can be discussed at all is, in many households, the harder and more important step."""
})

# ============================================================
# ARTICLE 3: SIP all-time high even as equity inflows slump (markets-finance)
# ============================================================
articles.append({
    "headline": "Indians Pulled Back From the Stock Market in May \u2014 but Their Monthly SIPs Hit a Record Anyway",
    "subheadline": "Equity mutual fund inflows fell 40 percent to a 12-month low as global jitters spooked lump-sum investors, yet automated SIP contributions climbed to an all-time high of \u20b926,688 crore \u2014 a sign of how deeply disciplined investing has taken root.",
    "slug": "sip-record-high-26688-crore-equity-fund-inflows-12-month-low-amfi-may-2026-nri-investor-20260619-1800",
    "category": "markets-finance",
    "vertical": "personal-finance",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs who invest in Indian mutual funds through SIPs to stay financially anchored to home, the data is reassuring: India's market is now propped up by steady domestic discipline rather than fickle foreign money, meaning the rupee-cost-averaging strategy many diaspora investors quietly run every month is exactly the behaviour holding the market up.",
    "sources": json.dumps([
        {"name": "India Tribune / IANS \u2014 SIP inflows hit all-time high of Rs 26,688 crore in May", "url": "https://www.indiatribune.com/"},
        {"name": "Mint \u2014 Equity mutual fund inflows fall 40% to one-year low of \u20b922,907 crore in May: AMFI Data", "url": "https://www.livemint.com/"},
        {"name": "Outlook Money \u2014 Amfi Data May 2026: Inflows in Equity Mutual Funds Decline 40%, Lowest Intake So Far in 2026", "url": "https://www.outlookmoney.com/"}
    ]),
    "body": """India's mutual fund data for May tells two stories at once \u2014 and the contrast between them reveals something important about how the country now invests. On one hand, money flowing into equity mutual funds slumped to its lowest level in a year. On the other, the steady drip of monthly Systematic Investment Plans (SIPs) climbed to an all-time high. Caution and discipline, it turns out, can rise together.

## The Slump

According to data from the Association of Mutual Funds in India (AMFI), net inflows into equity mutual funds fell about **40 percent to \u20b922,907 crore in May**, down from \u20b938,440 crore in April. That was the weakest monthly intake of 2026 so far. The pullback was broad: large-cap, mid-cap and small-cap funds all saw inflows shrink.

The cause was nerves. With crude oil swinging violently and uncertainty hanging over the US-Iran peace deal, investors who write big lump-sum cheques turned cautious. "The lower inflows is due to extreme volatility in the markets," AMFI chief executive Venkat Chalasani noted. Industry voices were quick to frame it as "healthy consolidation" after months of strong buying rather than a reversal of sentiment \u2014 but the cooling was real.

## The Record

And yet, beneath that cautious headline, the most reliable line in the entire report hit a new high. **SIP contributions rose to an all-time record of \u20b926,688 crore in May**, edging past April's \u20b926,632 crore. The number of contributing SIP accounts climbed to **8.56 crore**, and total assets held through SIPs jumped to \u20b914.61 lakh crore, now more than a fifth of the entire mutual fund industry's assets.

This is the crucial signal. When markets wobble, lump-sum investors hesitate \u2014 they wait, they watch, they second-guess. But SIP investors, by design, keep buying automatically, month after month, regardless of headlines. May's data shows that this automated discipline did not just hold up; it grew, even as discretionary money retreated. India's equity funds have now logged **63 straight months of positive inflows**, a streak unbroken since March 2021.

## Why the Difference Matters

The gap between falling lump-sum flows and rising SIPs marks a structural shift in Indian investing. For decades, the Indian market lived and died by foreign institutional money \u2014 when overseas investors sold, the market fell. That framework is increasingly dated. Domestic flows, led by SIPs from ordinary retail investors, are now large enough to absorb foreign selling. In recent months, the market has risen even as foreign investors pulled money out, because disciplined domestic buyers stepped into the gap.

In other words, the Indian market now has a stabiliser built from the monthly salaries of millions of ordinary savers. It is slower-moving, stickier, and far less prone to panic than hot foreign capital.

## Why NRIs Should Care

For the diaspora, this is more than a domestic story. Many NRIs run SIPs into Indian mutual funds \u2014 a simple way to stay financially anchored to home, build a rupee nest egg, and bet on India's long-term growth without timing the market. The May data is quietly reassuring for them on two counts.

First, it validates the strategy. **Rupee-cost averaging** \u2014 investing a fixed sum every month so you buy more units when prices are low and fewer when high \u2014 is precisely the behaviour that just propped up the market through a jittery month. The discipline diaspora investors practise is now a systemic force.

Second, it speaks to resilience. A market underpinned by steady domestic SIPs is less likely to crater on a single bad foreign-policy headline than one dependent on skittish overseas flows. For an NRI thinking in five- and ten-year horizons, that durability matters more than any single month's number.

## The Bottom Line

May was not a story of Indians fleeing the market. It was a story of two different kinds of investor behaving exactly as their nature dictates \u2014 the impulsive lump-sum buyer pausing on bad news, the disciplined SIP investor carrying on regardless. The record SIP figure is the more telling of the two. It says the habit of steady, automated, long-term investing has sunk deep roots in India, deep enough to hold the market up when sentiment turns. For diaspora investors quietly running their own SIPs from abroad, the lesson is simple: the boring strategy is winning."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["measuring tape waist obesity", "obesity overweight health waist", "body mass measurement scale"],
                          ["measuring tape waist", "weight scale health"], None),
    articles[1]["slug"]: (["semaglutide injection pen", "ozempic insulin pen injection", "weight loss medication pen"],
                          ["medication injection pen", "weight loss injection"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "Indian rupee banknotes money", "stock market trading screen India"],
                          ["indian rupee notes money", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A waist measurement; a review of 1.5 million cancer cases links higher BMI to 19 cancer types",
    articles[1]["slug"]: "A GLP-1 injection pen; early data suggests the weight-loss drugs may improve testosterone and sperm quality in men",
    articles[2]["slug"]: "Indian rupee notes; monthly SIP contributions hit a record even as equity fund inflows slumped in May",
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
