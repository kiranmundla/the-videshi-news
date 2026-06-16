#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-16 02:00 UTC batch.
Topics:
  1. South Asian cardiometabolic risk at age 45 (MASALA/MESA, JAHA) — lifestyle-health
  2. Moderate-carb vs low-carb / whole grains for heart health — lifestyle-health
  3. Gold price correction + JP Morgan $6,000 forecast: buying window for NRIs? — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl3.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl3.bin"):
            with open("/tmp/_img_dl3.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl3.bin")
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

def source_image(slug, commons_queries, pexels_queries):
    candidates = []
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
# ARTICLE 1: South Asian cardiometabolic risk at 45 (lifestyle-health)
# ============================================================
articles.append({
    "headline": "South Asians Are Already in Trouble by 45 \u2014 Even the Ones Eating Right. A 2,700-Person Study Found the Window.",
    "subheadline": "Combining two decades-long American cohorts, Northwestern researchers found that South Asian adults arrive at midlife with the highest rates of prediabetes and high blood pressure of any group \u2014 despite reporting healthier diets, less alcohol and lower body weight. At 45, nearly a third of South Asian men already had prediabetes, against just 4 per cent of white men. The paradox points to a risk that builds long before the diet advice ever arrives.",
    "slug": "south-asian-cardiometabolic-risk-age-45-masala-mesa-prediabetes-paradox-diaspora-screening-20260616",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The study draws on South Asian adults living in America and pinpoints the early-40s as the window when diabetes and hypertension risk is already high but still preventable \u2014 a direct, actionable message for NRI families who assume that eating well and staying slim is enough to keep heart disease at bay.",
    "sources": json.dumps([
        {"name": "Journal of the American Heart Association (MASALA + MESA longitudinal analysis)", "url": "https://www.ahajournals.org/doi/10.1161/JAHA.124.038374"},
        {"name": "Northwestern Now (U.S. South Asians face elevated heart risk at age 45)", "url": "https://news.northwestern.edu/stories/2026/02/u-s-south-asians-face-elevated-heart-risk-at-age-45-despite-reporting-healthier-habits"},
        {"name": "Physician's Weekly (Higher Cardiometabolic Risk by 45 for US South Asians)", "url": "https://www.physiciansweekly.com/"}
    ]),
    "body": """There is a story the South Asian diaspora likes to tell itself about health: we cook at home, we eat our vegetables, we do not drink much, and we are not heavy the way our American neighbours are. So heart disease, the thinking goes, is somebody else's problem. A major new study out of Northwestern Medicine takes that comforting story apart, and it does so with the most unsettling kind of evidence \u2014 the kind that holds even after you account for all the things people are doing right.

Published in the Journal of the American Heart Association, the analysis combined two of the longest-running cardiovascular cohort studies in the United States: MASALA, which has tracked South Asian adults for years, and MESA, which follows white, Black, Hispanic and Chinese adults. By pooling 2,700 people who were between 45 and 55 when their respective studies began, researchers could ask a question that had never been answered with this precision: at exactly what age does South Asian heart risk diverge from everyone else's?

## The Answer Was 45

The numbers are stark. At age 45, South Asian men had a prediabetes prevalence of 31 per cent \u2014 against just 4 per cent for white men, 10 per cent for Black and Hispanic men, and 13 per cent for Chinese men. That is not a modest gap; it is an order of magnitude. South Asian men also had higher rates of hypertension (25 per cent, versus 18 per cent in white men and 6 per cent in Chinese men) and higher rates of abnormal cholesterol and triglycerides than even Black men, a group with well-documented cardiovascular burden.

South Asian women followed the same trajectory. By 45, nearly one in five had prediabetes \u2014 roughly double the rate of white, Black, Hispanic and Chinese women. And by 55, both South Asian men and women were at least twice as likely to have developed full diabetes as white adults.

## The Paradox

What makes the findings genuinely disorienting is the lifestyle data sitting alongside them. The same South Asian participants reported healthier diets, lower alcohol use, comparable levels of physical activity and lower average body-mass index than most of the other groups. They were, by the standard checklist, doing better. And they were still sicker.

"The mismatch between healthier lifestyle behaviours and clinical risk was surprising," said senior author Dr. Namratha Kandula, a professor of general internal medicine and epidemiology at Northwestern's Feinberg School of Medicine, who leads the MASALA study. "This paradox tells us we're missing something fundamental to what is driving this elevated risk among South Asians."

The leading explanation is one The Videshi has reported on before in other contexts: South Asians tend to carry fat around their internal organs even at a normal or low BMI \u2014 the so-called "thin-outside, fat-inside" pattern \u2014 and they show greater insulin resistance and poorer insulin secretion than other groups even before any diagnosis. Crucially, this pattern appears to begin in childhood. Kandula points to early-life nutrition, environment and stress as factors that may load the dice well before a person's first adult cholesterol test.

## Why the Number 45 Matters

The temptation is to read all this as fatalism \u2014 if eating well does not protect us, why bother? That is precisely the wrong lesson. The study's real contribution is the timeline. "We've now identified a critical window in the 40s when risk is already high, but disease is still preventable," Kandula said. The danger is not that prevention does not work; it is that South Asians and their doctors tend to start looking a decade too late, after damage has accumulated silently.

## What Diaspora Families Should Do

The clinical takeaways are specific. Kandula urges South Asian adults to be screened earlier and more aggressively than standard guidelines suggest \u2014 checking blood pressure, fasting glucose or HbA1c, a full cholesterol panel, and lipoprotein(a), a genetically driven risk factor often missed in routine bloodwork, before middle age rather than after. A normal weight is not a reason to skip any of this; in the South Asian body it can actively mislead.

The behavioural levers still matter, but they have to be calibrated to this higher baseline. That means treating resistance training as non-negotiable to offset the low muscle mass South Asians tend to carry, minimising refined carbohydrates and sugary drinks that the South Asian metabolism handles especially poorly, and pushing for culturally specific guidance rather than generic advice that ignores the rice, the ghee and the family history.

The blunt message for the diaspora is this: the family that prides itself on home cooking and slim frames is not exempt. It may simply be the family that, reassured by all the right habits, never thinks to get tested until the forties are gone."""
})

# ============================================================
# ARTICLE 2: Whole grains / moderate-carb diet heart health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Carb War Has a Verdict, and It Is Not Keto. For the Rice-and-Roti Diaspora, the News Is Better Than Expected.",
    "subheadline": "Two strands of new research land on the same conclusion: very-low-carb and ketogenic diets deliver sharp gains on a few markers but raise 'bad' cholesterol, while moderate-carb eating improves health across a broader range of measures \u2014 and whole grains, eaten by the serving, slow the spread of the waistline and blunt rising blood sugar. For South Asians told to fear every grain of rice, the distinction that matters is refined versus whole, not carb versus no-carb.",
    "slug": "moderate-carb-vs-keto-whole-grains-heart-health-south-asian-rice-roti-diaspora-diet-20260616",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian diets are built on rice, wheat and pulses, and the diaspora is frequently nudged toward extreme low-carb or keto regimes that are culturally alienating \u2014 the new evidence suggests a moderate, whole-grain-forward approach is both healthier across more measures and far easier to sustain on an Indian plate.",
    "sources": json.dumps([
        {"name": "Knowridge / dietary comparison review (low-carb vs moderate-carb and LDL cholesterol)", "url": "https://knowridge.com/"},
        {"name": "Framingham Heart Study analysis (whole grains, waist circumference and metabolic markers)", "url": "https://www.tuftsmedicalcenter.org/"},
        {"name": "American Heart Association dietary guidance", "url": "https://www.heart.org/en/healthy-living/healthy-eating"}
    ]),
    "body": """For a decade, the loudest voice in nutrition has belonged to the carbohydrate sceptics. Cut the rice, ditch the roti, embrace fat and protein, and watch the weight and the blood sugar fall. For the South Asian diaspora \u2014 a community both disproportionately prone to diabetes and culturally wedded to grain-based meals \u2014 that advice has carried a special sting, framing the food of home as the enemy. A fresh wave of research suggests the war was being fought on the wrong front. The useful distinction was never carbs versus no carbs. It was refined versus whole.

## What the Diet Comparison Actually Found

A broad comparison of people eating low-carbohydrate diets against those eating higher-carbohydrate diets produced a more nuanced picture than either camp tends to admit. Very-low-carb and ketogenic diets did deliver some of the largest improvements on specific measures \u2014 notably big drops in triglycerides, the blood fats tied to cardiovascular risk, along with weight and body-fat loss. That is real, and it is why these diets feel so effective in the first months.

But the same diets tended to raise LDL cholesterol, the so-called "bad" cholesterol most directly associated with heart disease. Moderate-carbohydrate diets, by contrast, delivered benefits across a broader range of health measures rather than dramatic gains in just a few. They improved the overall picture instead of trading one number for another. One reassuring wrinkle: the lipid ratios that many researchers consider a better gauge of cardiovascular health than LDL alone improved similarly across all the approaches \u2014 meaning the moderate path gave up little while raising less alarm.

## The Whole-Grain Evidence

The case for moderation gets sharper when you look at what kind of carbohydrate is on the plate. Drawing on the Framingham Heart Study \u2014 one of the most influential cardiovascular investigations ever run \u2014 researchers followed more than 3,100 adults for nearly 18 years, most of them in their mid-fifties at the start, tracking waist size, blood pressure, blood sugar, triglycerides and HDL cholesterol.

The people who ate at least three servings of whole grains a day saw their waistlines expand far more slowly than those who ate fewer: about half an inch over the study versus more than a full inch. They also showed smaller rises in blood sugar and blood pressure. Those who cut back on refined grains \u2014 white bread, white rice, maida-based snacks \u2014 fared better still, with smaller waist gains and larger drops in triglycerides. Even modest reductions in abdominal fat compound into meaningful protection over years, which matters acutely for South Asians, who store fat viscerally and at lower body weights than other groups.

## Why This Lands Differently on an Indian Plate

Here is the part the keto evangelists rarely mention: the traditional Indian plate is not inherently a problem. Whole grains are woven through the cuisine \u2014 brown and hand-pounded rice, whole-wheat atta, millets like ragi, bajra and jowar, plus the fibre and protein of dals and legumes. The damage in the modern diaspora diet tends to come from the refined drift: polished white rice in large portions, maida in naan, parathas and bakery items, and the sugary drinks and packaged snacks that travel with urban affluence.

That reframes the goal from deprivation to substitution. Swapping white rice for brown or for millets, choosing whole-wheat over maida, building meals around dal and vegetables, and keeping portions of refined grains in check accomplishes most of what an extreme low-carb diet promises \u2014 without the LDL penalty, and without asking a family to abandon the foods that anchor its meals.

## The Practical Bottom Line

For South Asians weighing the diet wars, the evidence points away from the extremes. Ketogenic eating can be a legitimate short-term tool for someone with specific metabolic goals and medical supervision, but it raises LDL and is notoriously hard to sustain on a grain-loving palate. A moderate, whole-grain-forward diet improves more health markers, is achievable on familiar food, and is far likelier to last the decades over which heart disease actually develops.

The next time a wellness influencer insists that rice is poison, the more accurate sentence is narrower and far more livable: refined grains in large portions are the risk; the whole grains your grandmother cooked were never the problem."""
})

# ============================================================
# ARTICLE 3: Gold correction + JP Morgan $6,000 forecast (markets-finance)
# ============================================================
articles.append({
    "headline": "Gold Just Fell to a Six-Month Low \u2014 and JP Morgan Says It Is Heading to $6,000. For NRIs, the Dip Is the Story.",
    "subheadline": "After a 64 per cent surge in 2025, gold has stalled, sliding below $4,022 an ounce this month and dragging Indian prices to a six-month low near \u20b9146,000 per 10 grams. JP Morgan still forecasts $6,000 by year-end. With India's 15 per cent import duty, a recovering rupee and the Iran peace deal all pulling in different directions, diaspora buyers face a genuine decision: is this the buying window, or the start of a longer cooling?",
    "slug": "gold-six-month-low-jp-morgan-6000-forecast-india-tariff-rupee-nri-buying-window-20260616",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Gold sits at the centre of NRI financial life \u2014 wedding gifting, festival buying, portfolio hedging and money sent home \u2014 and the collision of a sharp price correction, a bullish $6,000 forecast, India's steep 15 per cent import duty and a recovering rupee turns the next few weeks into a concrete timing decision for diaspora families.",
    "sources": json.dumps([
        {"name": "Reuters (Gold's record rally falters as bulls run into Fed rate expectations)", "url": "https://www.reuters.com/markets/commodities/"},
        {"name": "The Hindu BusinessLine (Gold expected to touch $6,000/oz by end-2026: JP Morgan)", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reuters (ASIA GOLD: India gold demand ticks up as prices slip)", "url": "https://www.reuters.com/world/india/"}
    ]),
    "body": """Few assets are as woven into diaspora life as gold. It is the wedding gift, the festival purchase, the hedge of last resort and, for many NRI families, the most emotionally loaded line in the household budget. So when gold does something dramatic, the South Asian diaspora pays attention in a way few other markets command. And right now gold is doing two dramatic things at once: it is falling, and the world's largest bank is insisting it is about to soar.

## The Fall

After a blistering 2025 \u2014 a 64 per cent gain, the metal's biggest annual rise in 46 years \u2014 gold has run out of momentum. This month it touched an intra-year low of around $4,022 an ounce, its weakest since November, before steadying near $4,188. The trigger was prosaic: strong US jobs data revived expectations that the Federal Reserve might keep rates higher for longer, and even hike to fight energy-driven inflation. Higher rates and a firmer dollar are gold's natural enemies, since the metal pays no yield. The slide pushed gold below its 200-day moving average for the first time in two and a half years, a technical break that traders read as a genuine shift in mood.

In India, that translated into domestic prices dropping to roughly \u20b9146,000 per 10 grams, their lowest since early April. Crucially, the dip drew buyers back. Reuters reported that jewellery demand ticked up as the correction tempted bargain-hunters, with dealer discounts narrowing sharply \u2014 a sign that physical appetite, dulled by record-high prices, revives the moment gold looks affordable again.

## The Forecast

Against that softness sits a strikingly bullish call. JP Morgan Global Research expects gold to average $6,000 an ounce in the final quarter of 2026, with a path toward $6,300 by the end of 2027 \u2014 well above current levels. The bank acknowledges the present malaise: its own metals strategist described gold as stuck in "a bit of a technical no-man's land," trudging above the 200-day average and capped below the 50-day, with investors distracted by the prospect of Fed hikes. But the structural forces behind gold's multi-year run \u2014 relentless central-bank buying, geopolitical hedging and the search for safety \u2014 remain, in JP Morgan's view, largely intact. China's central bank, notably, added to its gold reserves for a 19th straight month in May.

## The Indian Complications

For NRIs, the global price is only half the equation. Two India-specific factors muddy the picture. The first is the import duty: last month India raised tariffs on gold and silver to 15 per cent from 6 per cent to ease pressure on foreign-exchange reserves, a steep markup that sits on top of a 3 per cent sales levy and makes domestic gold structurally more expensive than the global benchmark. The second is the rupee, which has just rallied to a five-week high near 94.7 per dollar after the US-Iran peace deal sent oil tumbling. A stronger rupee makes dollar-priced gold cheaper for Indian buyers \u2014 a tailwind that partly offsets the duty.

## What It Means for the Diaspora

The upshot is a real decision rather than a slogan. For families buying for an upcoming wedding or festival, the current correction \u2014 global prices off their highs, the rupee firmer \u2014 is arguably the most favourable window in months, and waiting for a JP Morgan-style surge to materialise risks paying considerably more. For purely investment-driven buyers, the calculus is more delicate: the $6,000 forecast is a forecast, not a promise, and it is explicitly contingent on geopolitics and Fed policy that nobody can call with confidence. Standard Chartered has noted that hundreds of tonnes of ETF gold are already in loss-making territory below $4,250, a reminder that the metal can stay soft for months.

A few principles cut through the noise. Gold is a hedge and a cultural asset, not a get-rich-quick trade, and the old discipline of buying in tranches rather than timing a single moment still serves diaspora buyers best. India's 15 per cent duty means the cheapest gold for many NRIs may be bought abroad and carried within legal limits, or held in dollar terms rather than as duty-laden domestic jewellery. And for those sending money home for a family purchase, the firmer rupee changes the maths of when to transfer.

Gold has spent the year confounding both bulls and bears. The honest read for the diaspora is that the dip is opportunity and the forecast is hope \u2014 and the wise buyer treats them as two different things."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["blood pressure measurement doctor patient", "diabetes blood glucose test", "medical checkup heart health"],
                          ["doctor checking blood pressure patient", "blood sugar glucose test diabetes"]),
    articles[1]["slug"]: (["whole grains brown rice millet", "indian whole wheat roti chapati", "millet grains bowl"],
                          ["whole grains brown rice bowl", "healthy indian thali rice lentils"]),
    articles[2]["slug"]: (["gold bars bullion", "gold jewellery india", "gold coins bullion finance"],
                          ["gold bars bullion finance", "indian gold jewellery wedding"]),
}
img_captions = {
    articles[0]["slug"]: "A clinician checks a patient's blood pressure, one of the risk factors South Asians show at strikingly young ages",
    articles[1]["slug"]: "Whole grains such as brown rice and millet, which research links to slower waistline growth and steadier blood sugar",
    articles[2]["slug"]: "Gold bullion, the asset at the centre of diaspora wedding, festival and investment decisions",
}
for art in articles:
    cq, pq = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq)
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
