#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 02:00 UTC batch.
Topics:
  1. Midlife cardiorespiratory fitness — a 24,576-adult study (JACC) ties higher
     midlife fitness to a longer life span and health span, fewer diseases. — lifestyle-health
  2. Short-term diet change — a 4-week trial (Aging Cell) found shifting to a
     plant-forward, complex-carb diet narrowed the gap between biological and
     chronological age, suggesting ageing markers can move fast. — lifestyle-health
  3. NSE IPO — the National Stock Exchange filed for a ~Rs.30,000-crore pure
     offer-for-sale, set to be India's largest-ever public issue, handing a
     windfall to long-time holders. — markets-finance
"""

import json, os, io, subprocess, urllib.parse, re
from datetime import datetime, timezone
import requests

# ---- env ----
for env_file in ("~/.env.supabase", "~/workspace/.env.supabase", "~/workspace/.env.pexels"):
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0200z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0200z.bin"):
            with open("/tmp/_img_dl0200z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0200z.bin")
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
# ARTICLE 1: Midlife cardiorespiratory fitness (lifestyle-health)
# ============================================================
articles.append({
    "headline": "How Fit You Are in Midlife May Forecast How Long \u2014 and How Well \u2014 You Live, a 24,000-Person Study Finds",
    "subheadline": "Adults with higher cardiorespiratory fitness measured on a treadmill in midlife went on to live longer, fall ill less often and stretch out their healthy years, according to a large analysis published in the Journal of the American College of Cardiology.",
    "slug": "midlife-cardiorespiratory-fitness-longer-lifespan-healthspan-treadmill-jacc-24576-adults-diaspora-20260623-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry an outsized burden of heart disease and diabetes, often at lower body weights than other groups, and aerobic fitness is one of the few levers that pushes back on both \u2014 making this evidence that a midlife habit of brisk movement can buy healthy years especially relevant to NRI families.",
    "sources": json.dumps([
        {"name": "Journal of the American College of Cardiology \u2014 Midlife cardiorespiratory fitness, lifespan and healthspan (24,576-adult study)", "url": "https://www.jacc.org/"},
        {"name": "Healthline \u2014 3 Studies Link Diet, Fitness, Multivitamins to Slower Aging", "url": "https://www.healthline.com/health-news/multivitamins-diet-fitness-slow-aging-process"}
    ]),
    "body": """Of all the numbers a doctor can take \u2014 blood pressure, cholesterol, blood sugar \u2014 one of the most powerful may be the one rarely measured: how well your heart and lungs deliver oxygen when you push your body. A large new analysis suggests that this single quality, cardiorespiratory fitness, measured in midlife, is a strikingly good predictor of how long and how well a person will live.

## What the Study Found

Researchers assessed 24,576 adults aged 65 or younger, gauging their cardiorespiratory fitness with a treadmill test \u2014 the gold-standard way to measure how efficiently the heart and lungs supply oxygen to working muscles. They then tracked health outcomes over time, looking not just at how long people lived but at how many of those years were spent free of disease.

The pattern was clear and consistent. Men with higher midlife fitness enjoyed a roughly 3% longer life span, a 2% longer "health span" \u2014 the stretch of life lived in good health \u2014 and 9% fewer diseases over the follow-up. Women showed similar benefits. The findings, published in the Journal of the American College of Cardiology, add to a deep body of evidence that fitness is not merely a marker of vanity or athletic ambition but a vital sign in its own right.

## Why Fitness Is Such a Strong Signal

Cardiorespiratory fitness sits at the crossroads of nearly every system that ages: the heart, the blood vessels, the lungs, the muscles and the metabolism. A body that moves oxygen efficiently tends to have more flexible arteries, better blood-sugar control, lower chronic inflammation and stronger muscles. Improving fitness, in other words, is less a single intervention than a lever that nudges many risk factors at once.

That is why aerobic capacity has repeatedly outperformed more familiar measures in predicting who develops heart disease, diabetes and stroke, and who does not. "This study confirms our understanding of cardiorespiratory fitness as a marker of future health outcomes, and should encourage all of us to make physical activity a part of our daily lives," cardiologist Cheng-Han Chen told Healthline, commenting on the research.

## The Encouraging Part

What makes fitness different from age or genetics is that it can be changed. Unlike the calendar, cardiorespiratory fitness responds to training at almost any stage of life. Regular aerobic activity \u2014 brisk walking, cycling, swimming, jogging, climbing stairs \u2014 measurably raises it within weeks, and the gains translate into the kind of outcomes this study tracked.

Public-health guidance has long converged on a achievable target: about 150 minutes of moderate aerobic activity a week, or roughly 22 minutes a day. That is the threshold associated in other large studies with several added years of life expectancy. The midlife window matters because fitness built in one's 40s and 50s appears to set the trajectory for the decades that follow.

## The Caveats

This is observational research, so it shows a strong association rather than ironclad proof of cause and effect. Fitter people may differ in other ways \u2014 they may smoke less, eat better or have fewer underlying conditions \u2014 and some of the advantage could reflect those differences. The treadmill test also measures a snapshot, not a lifetime of activity.

Still, the consistency of the finding across sexes, and its agreement with decades of prior work, make the practical message robust: raising fitness is one of the most reliable bets a person can make for a longer, healthier life.

## How to Read It

The takeaway is not to chase elite athleticism. The largest jumps in benefit come from moving the least-fit people up a notch \u2014 going from sedentary to lightly active, from no walking to a daily brisk walk. For most adults, the simplest prescription is to build aerobic movement into the rhythm of the day and treat it as non-negotiable as brushing teeth.

## Why It Matters for the Diaspora

For the Indian diaspora, this evidence lands on sensitive ground. South Asians develop heart disease and type 2 diabetes at higher rates and often younger ages than many other populations, frequently while appearing slim \u2014 a phenomenon doctors link to where the body stores fat and how it handles insulin. Cardiorespiratory fitness is one of the few tools that directly counters both threats.

Yet the realities of diaspora life \u2014 long hours at desks, demanding commutes, the cultural centrality of rich food and the relative novelty of structured exercise in many family routines \u2014 can crowd out movement. The study reframes the stakes. A daily brisk walk, a few cycling sessions a week, taking the stairs, playing a sport on the weekend \u2014 these are not just calorie-burning chores but deposits into a fitness account that pays out in healthy years. For NRI parents balancing careers and families, the most valuable health habit may be the simplest: keep the heart and lungs working hard enough, often enough, to stay fit through midlife and beyond."""
})

# ============================================================
# ARTICLE 2: Short-term diet change & biological age (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Your Body's \u2018Biological Age\u2019 May Start Falling in Just Four Weeks on a Plant-Forward Diet, a New Trial Suggests",
    "subheadline": "Older adults who shifted toward complex carbohydrates and more plant-based foods narrowed the gap between their biological and chronological age within a month \u2014 a sign that the body's ageing markers can move surprisingly fast.",
    "slug": "short-term-diet-change-lowers-biological-age-four-weeks-plant-forward-complex-carbs-aging-cell-diaspora-20260623-0200",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Traditional Indian cooking is already built around the plant-forward, complex-carbohydrate foods this trial favoured \u2014 lentils, vegetables, whole grains and legumes \u2014 meaning many diaspora families are a few deliberate swaps, not a wholesale overhaul, away from a diet linked to younger biological ageing.",
    "sources": json.dumps([
        {"name": "Aging Cell \u2014 Short-term dietary change and Klemera-Doubal biological age in older adults", "url": "https://onlinelibrary.wiley.com/journal/14749726"},
        {"name": "Healthline \u2014 3 Studies Link Diet, Fitness, Multivitamins to Slower Aging", "url": "https://www.healthline.com/health-news/multivitamins-diet-fitness-slow-aging-process"}
    ]),
    "body": """The idea that diet shapes how we age is hardly new. What is striking about a recent trial is the speed: in just four weeks, older adults who changed how they ate narrowed the gap between their biological age and the number of birthdays they had celebrated. It is a reminder that the body's ageing clock, far from being fixed, can respond to the plate within weeks.

## What the Study Did

Published in the journal Aging Cell, the trial set out to test whether short-term dietary change could move a measure called biological age \u2014 an estimate, calculated here using an algorithm known as the Klemera-Doubal Method, of how old a person's body appears at the cellular and metabolic level, as distinct from their chronological age.

Older participants were assigned to one of four eating patterns: omnivorous and high-fat, omnivorous and high-carbohydrate, semi-vegetarian and high-fat, or semi-vegetarian and high-carbohydrate. Researchers measured the gap between each person's biological and chronological age at the start and again after just four weeks.

## The Result

The diet that most resembled participants' usual way of eating \u2014 omnivorous and high-fat \u2014 produced no meaningful change. But the other three patterns told a different story. Compared with that baseline group, those who moved toward higher-carbohydrate or semi-vegetarian eating showed a significant reduction in the gap between their biological and chronological age. In plain terms, their bodies looked metabolically younger than before.

The authors concluded that the biggest improvements clustered around diets rich in complex carbohydrates and plant-based foods \u2014 not the refined sugars and white flour that the word "carbohydrate" often conjures, but the slow-digesting kind found in whole grains, legumes, vegetables and pulses.

## Why It Might Work So Fast

Four weeks is a short window for the body to reorganise itself, but many of the markers that feed into biological-age estimates \u2014 blood pressure, cholesterol, blood-sugar control, markers of inflammation \u2014 can shift quickly when eating changes. "It doesn't surprise me that this study showed that, in just four weeks, dietary changes that shift eating habits toward a more plant-forward pattern can have a meaningful impact on blood pressure, cholesterol, insulin sensitivity, and energy levels," preventive cardiology dietitian Michelle Routhenstein told Healthline.

Those cardiometabolic improvements matter because heart disease remains the leading cause of death worldwide, and a large share of cases is considered preventable through lifestyle. A diet that improves these markers is, in effect, lowering risk across the body's most consequential systems at once.

## The Caveats

The findings come with important limits. This was a short trial measuring a biological-age estimate, not a long-term study counting heart attacks, cancers or years of life. As Routhenstein cautioned, the changes are "changes in biomarkers, not direct evidence of fewer heart attacks, cancers, or longer life span," and she warned against the phrase "true age reversal," which can only be judged if improvements hold over the long term.

In other words, four weeks of better numbers is a promising start, not a guarantee of a longer life. The benefits would need to be sustained for years to translate into the outcomes most people care about.

## How to Read It

The encouraging message is one of agency and timing. "It is never too late to benefit from dietary changes," Routhenstein noted, pointing out that meaningful improvements appeared in older adults after only a month. The practical recipe is unglamorous but consistent with decades of nutrition science: lean toward plants, favour complex carbohydrates over refined ones, and treat heavy, fat-laden eating as the exception rather than the default.

## Why It Matters for the Diaspora

For the Indian diaspora, the most useful insight may be how little is required to start. The diet the study favoured \u2014 plant-forward, built on complex carbohydrates \u2014 maps closely onto the bones of traditional Indian cooking: dal, beans and chickpeas, vegetable sabzis, whole grains like millet and brown rice, and a culinary tradition that has long treated meat as one option among many rather than the centrepiece.

The risk, in diaspora kitchens, often lies in what has crept in: more refined flour, more fried snacks, more sugar, larger portions of rich restaurant-style dishes reserved historically for festivals. The study suggests that shifting back toward the plant-forward, whole-food version of one's own cuisine \u2014 more lentils and vegetables, fewer deep-fried and refined items, complex grains in place of white rice and maida \u2014 could begin paying dividends in weeks, not years. For older NRIs in particular, it is a reassuring case that the food of home, eaten in its traditional, plant-heavy form, may be one of the simplest ways to keep the body younger than the calendar."""
})

# ============================================================
# ARTICLE 3: NSE IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Stock Exchange Is Going Public: NSE Files for a \u20b930,000-Crore IPO, Set to Be the Country's Largest Ever",
    "subheadline": "After nearly a decade of regulatory delay, the National Stock Exchange has filed for a pure offer-for-sale of about 6% of its equity \u2014 a listing that would hand long-time backers like Azim Premji and Radhakishan Damani a multi-billion-dollar windfall.",
    "slug": "nse-ipo-drhp-30000-crore-offer-for-sale-largest-india-listing-premji-damani-windfall-nri-investor-20260623-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The exchange where most NRI portfolios are effectively built \u2014 through Indian mutual funds, direct equities and the derivatives market \u2014 is itself about to list, giving the diaspora both a marquee investment opportunity and a clearer window into how India's market plumbing is valued.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors", "url": "https://www.reuters.com/"},
        {"name": "The Indian EYE \u2014 NSE Files for IPO worth \u20b930,000-Crore, set to become India's Largest Public Issue", "url": "https://theindianeye.com/"},
        {"name": "Inshorts / Bloomberg \u2014 Who could become richer from NSE's mega IPO?", "url": "https://www.inshorts.com/"}
    ]),
    "body": """For nearly a decade, India's largest stock exchange has sat in a peculiar position: the venue where the country's companies raise capital and list their shares, yet unable to list its own. That is about to change. The National Stock Exchange has filed its draft papers with the market regulator for an initial public offering estimated at around \u20b930,000 crore \u2014 a deal poised to become the largest in India's history.

## What NSE Has Filed

The exchange submitted its Draft Red Herring Prospectus to the Securities and Exchange Board of India, paving the way for a listing that has been delayed for years by regulatory hurdles, including the long-running co-location controversy. The structure is notable: this is a pure offer for sale, meaning NSE itself will raise no fresh capital. Instead, existing shareholders will sell roughly 148.9 million shares, about 6% of the exchange's equity.

The scale is hard to overstate. Industry estimates put the issue near \u20b930,000 crore, surpassing previous record Indian IPOs and ranking alongside Mukesh Ambani's planned Reliance Jio listing as one of the two largest the country has seen. Founded in 1992, NSE has grown into India's dominant bourse and the world's most active derivatives exchange by trading volume. For the year ended March 2026, it reported total income of \u20b918,713 crore and net profit of \u20b910,302 crore \u2014 a profit margin that explains the intense investor appetite.

## A Windfall for Long-Time Holders

Because the deal is an offer for sale, its immediate effect is to convert paper holdings in an unlisted company into cash and tradable stock for the investors who have waited years for an exit. NSE has more than 200,000 shareholders, and its shares change hands at close to \u20b92,000 in the unlisted market \u2014 a level that implies a valuation of roughly $57 billion, which would make it among the most valuable exchanges in the world.

The roster of beneficiaries reads like a who's who of Indian capital. According to Bloomberg estimates, billionaire Azim Premji's stake could be worth about $1.2 billion at a listing price near \u20b92,020 a share, while veteran investor Radhakishan Damani's holding could fetch around $835 million. Hero Group's Sunil Kant Munjal, Narayana Murthy's family office and the founding family of Haldiram's are among others positioned for sizeable gains. State-owned lenders such as the State Bank of India, a Singapore sovereign wealth fund and a Canadian pension manager are also set to pare holdings, with merchant bankers estimating a collective windfall of around $2.6 billion for top investors.

## The Pricing Question

Sources involved in the process suggest NSE may offer shares at a 5% to 10% discount to private-market valuations, with a price under discussion near \u20b91,900 a share \u2014 a level one person described as designed "to attract incoming investors while not short-changing existing ones." A final decision will follow investor roadshows, and SEBI's review of the prospectus will set the listing timeline, which could fall later this year.

State-owned general insurers \u2014 National Insurance, United India Insurance and Oriental Insurance \u2014 plan to offload chunks of their stakes, with potential gains of \u20b91,000 crore to \u20b92,100 crore. Analysts note the proceeds will strengthen balance sheets but are unlikely to resolve the deeper solvency challenges those insurers face.

## Why It Matters

Beyond the headline numbers, the listing is a milestone for India's capital markets. It promises transparent price discovery for shares that have long traded in an opaque unlisted market, and it hands long-frozen investors a clean exit. It also arrives at a moment of structural strength for Indian equities, where a surge of domestic retail money has been steadily absorbing foreign selling.

## How to Read It

For investors weighing the IPO, the usual discipline applies. A marquee name and a record-breaking size do not guarantee a bargain; the price relative to earnings, the discount to the unlisted market and the broader appetite for financial-infrastructure stocks will determine whether early buyers are rewarded. An offer-for-sale also means no new money flows into the business itself \u2014 the proceeds go to selling shareholders, not to fund growth.

## Why It Matters for NRIs

For the Indian diaspora, the NSE listing is unusually resonant. Most NRI exposure to India \u2014 whether through mutual funds, direct equities or the derivatives market \u2014 runs across the very exchange now going public. Owning a slice of that infrastructure, rather than only trading on it, is a novel proposition, and one likely to draw diaspora interest given the appetite for blue-chip Indian names.

The practical cautions are the same as for any NRI equity investment: eligibility and the application route depend on whether one invests through an NRE or NRO account and on the rules governing foreign participation in such offers, so checking the prospectus and one's broker's NRI process is essential before bidding. As with any hyped listing, the disciplined approach is to judge the deal on valuation and long-term fundamentals rather than on the celebrity of its backers or the size of its headline. But for a diaspora deeply invested in India's growth story, the chance to own a piece of the market's central institution is a genuine landmark."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["running exercise jogging outdoor", "treadmill cardio fitness exercise", "people jogging park fitness"],
                          ["running jogging exercise", "treadmill cardio gym"], None),
    articles[1]["slug"]: (["vegetables legumes plant based food bowl", "lentils whole grains healthy food", "fresh vegetables plant based diet"],
                          ["fresh vegetables healthy plant based", "vegetables legumes bowl"], None),
    articles[2]["slug"]: (["National Stock Exchange India building Mumbai", "Bombay Stock Exchange trading screen", "stock exchange trading floor india"],
                          ["stock exchange trading floor", "stock market screen finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A 24,576-adult study found that higher cardiorespiratory fitness in midlife was linked to a longer life span and fewer diseases",
    articles[1]["slug"]: "A four-week trial found that shifting toward plant-forward, complex-carbohydrate diets narrowed the gap between biological and chronological age",
    articles[2]["slug"]: "The National Stock Exchange has filed for a roughly \u20b930,000-crore offer-for-sale, set to be India's largest-ever public issue",
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
