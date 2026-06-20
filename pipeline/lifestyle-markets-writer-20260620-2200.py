#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 22:00 UTC batch.
Topics:
  1. Semmelweis University / UK Biobank (468,629 adults, ~11-yr follow-up): light-to-moderate
     coffee (0.5-3 cups/day) linked to 12% lower all-cause mortality, 17% lower CV death,
     21% lower stroke risk — lifestyle-health
  2. Northwestern Medicine (Arteriosclerosis, Thrombosis, and Vascular Biology / AHA):
     sleep-aligned overnight fasting — stop eating 3h before bed, dim lights, extend fast
     ~2h — cut sleeping blood pressure 3.5% and heart rate 5% WITHOUT changing calories — lifestyle-health
  3. RBI June MPC minutes: panel held repo at 5.25%, cut FY27 GDP growth forecast to 6.6%
     from 6.9%, flagged West Asia conflict as a risk to inflation/growth/external balances — markets-finance
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
# ARTICLE 1: Moderate coffee protects the heart (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Few Cups of Coffee a Day May Be Quietly Guarding Your Heart, a Study of 468,000 Adults Finds",
    "subheadline": "Drinking up to three cups of coffee a day was linked to a 17 percent lower risk of dying from heart disease and a 21 percent lower stroke risk, according to a long-running analysis of nearly half a million adults \u2014 a reassuring finding for a diaspora that runs on filter coffee and chai alike.",
    "slug": "moderate-coffee-lower-heart-disease-stroke-death-risk-uk-biobank-semmelweis-468000-adults-diaspora-20260620-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Coffee and chai are woven into daily diaspora life \u2014 South Indian filter coffee, the office cortado, the evening cup of tea \u2014 yet many Indians carry an inherited wariness that caffeine strains the heart, so robust evidence that moderate coffee is protective rather than harmful speaks directly to how NRI households think about their morning ritual.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 How Much Coffee Everyday Could Help Prevent Heart Disease? (Semmelweis University; UK Biobank)", "url": "https://knowridge.com/2026/06/how-much-coffee-everyday-could-help-prevent-heart-disease/"},
        {"name": "European Journal of Preventive Cardiology \u2014 Light to moderate coffee consumption is associated with lower risk of death: a UK Biobank study", "url": "https://academic.oup.com/eurjpc"}
    ]),
    "body": """Few daily rituals are as universal as the morning cup. Coffee is the most widely used stimulant on earth, and for the Indian diaspora it sits alongside chai as the drink that starts the day. Yet for decades it carried a quiet suspicion \u2014 that caffeine strains the heart, raises blood pressure and is something to be cut back on. A large new analysis from researchers at Semmelweis University in Hungary pushes firmly in the other direction: for most people, a moderate coffee habit appears to protect the heart rather than harm it.

## What the Study Looked At

The team drew on the UK Biobank, one of the world's largest long-term health databases, and followed 468,629 adults who showed no signs of heart disease when the research began. The participants averaged about 56 years of age, and slightly more than half were women. Researchers tracked their health for between 10 and 15 years, comparing outcomes against how much coffee they drank.

The group was split three ways. About 22 percent did not drink coffee regularly. Nearly 58 percent drank between half a cup and three cups a day \u2014 the light-to-moderate group. And around 19 percent drank more than three cups daily.

## The Findings

The results favoured the moderate drinkers. Compared with people who did not drink coffee regularly, those who had between half a cup and three cups a day had a 12 percent lower risk of dying from any cause over the follow-up period. They also had a 17 percent lower risk of dying from heart disease and a 21 percent lower risk of stroke.

The benefit was strongest in that moderate band. Pushing past three cups a day did not add to the protection in the same clear way, which fits a recurring theme in coffee research: the sweet spot is moderate, habitual intake rather than ever-larger amounts. In a subgroup who underwent detailed cardiac imaging, regular coffee drinkers also showed heart-structure patterns that ran against, rather than with, the usual changes of ageing.

## Why Coffee Might Help

Coffee is far more than caffeine. It is rich in antioxidants and other bioactive compounds called polyphenols, which researchers believe may reduce inflammation and support the lining of blood vessels. Those mechanisms remain partly speculative, and the scientists were careful to note an important limit: this is observational research. It can show a strong association between moderate coffee drinking and better heart outcomes, but it cannot prove that the coffee itself is the cause. People who drink moderate coffee may differ in other ways that also protect the heart.

A few practical caveats matter. The protective signal is about the coffee, not what often goes into it \u2014 heavy sugar, syrups and cream can erase the benefit. People with certain conditions, such as poorly controlled arrhythmias or anxiety, and those who are pregnant are usually advised to be more cautious with caffeine and should follow their doctor's guidance.

## Why It Matters for the Diaspora

For Indian-origin households, the message lands on familiar ground. South Indian filter coffee, the office espresso, and the ever-present cup of chai are daily fixtures, and many carry an inherited belief that caffeine is hard on the heart. This study, layered on a growing body of similar findings, suggests the opposite for moderate drinkers: a couple of cups a day is more likely to sit on the protective side of the ledger.

That matters all the more because people of South Asian descent face elevated rates of heart disease, often striking earlier than in other populations. None of this makes coffee a treatment, and it is no substitute for the basics \u2014 not smoking, staying active, managing blood pressure and cholesterol, and eating well. But for NRIs who quietly worried that their daily cup was a vice, the evidence offers permission to enjoy it. The catch is in the preparation: keep it moderate, and go easy on the sugar and cream that can turn a heart-friendly habit into a liability."""
})

# ============================================================
# ARTICLE 2: Sleep-aligned fasting improves heart/metabolic markers (lifestyle-health)
# ============================================================
articles.append({
    "headline": "When You Stop Eating at Night May Matter as Much as What You Eat, a Northwestern Study Finds",
    "subheadline": "Adults at higher cardiometabolic risk who stopped eating three hours before bed, dimmed the lights and extended their overnight fast by about two hours saw their sleeping blood pressure fall 3.5 percent and heart rate drop 5 percent \u2014 without changing a single calorie.",
    "slug": "sleep-aligned-fasting-overnight-blood-pressure-heart-rate-northwestern-circadian-atvb-diaspora-20260620-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Late dinners are a cultural norm in many Indian households \u2014 9 or 10 pm meals, often heavy, are routine \u2014 and South Asians carry outsized rates of high blood pressure and diabetes, so a finding that simply shifting the last meal earlier can improve overnight heart health offers a low-cost lever that fits diaspora life without demanding a new diet.",
    "sources": json.dumps([
        {"name": "Northwestern Now \u2014 Sleep-aligned fasting improves heart and blood-sugar markers", "url": "https://news.northwestern.edu/"},
        {"name": "Arteriosclerosis, Thrombosis, and Vascular Biology (American Heart Association)", "url": "https://www.ahajournals.org/journal/atvb"}
    ]),
    "body": """Most diet advice fixates on two questions: how much you eat and what you eat. A new study from Northwestern Medicine adds a third that may be just as powerful \u2014 when you eat, relative to when you sleep. By nudging people to finish eating earlier and align their overnight fast with their body's natural sleep-wake rhythm, researchers improved measures of heart and metabolic health without anyone cutting a single calorie.

## A Simple Shift in Timing

The study focused on middle-aged and older adults at higher risk for cardiometabolic disease \u2014 the cluster of conditions including high blood pressure, high blood sugar and excess weight that drives heart attacks and strokes. Participants were asked to make three modest changes: stop eating about three hours before bedtime, dim the lights in the evening, and extend their overnight fast by roughly two hours.

Crucially, the researchers did not ask anyone to eat less. Calorie intake stayed the same. The only thing that changed was the timing of the eating window and the evening light environment, both tuned to work with the body's circadian clock rather than against it.

## What Happened

The benefits showed up where they matter. During sleep, participants' blood pressure dipped by about 3.5 percent and their heart rate fell by around 5 percent. The improvements extended into the daytime as well, touching both cardiovascular and blood-sugar markers. The findings were published in Arteriosclerosis, Thrombosis, and Vascular Biology, a journal of the American Heart Association.

"Timing our fasting window to work with the body's natural wake-sleep rhythms can improve the coordination between the heart, metabolism and sleep, all of which work together to protect cardiovascular health," said Dr. Daniela Grimaldi, the study's first author and a research associate professor of neurology in the division of sleep medicine at Northwestern University Feinberg School of Medicine.

## Why Timing Matters

The body runs on an internal clock that governs hormones, blood pressure, body temperature and how efficiently it handles sugar and fat. That machinery is tuned to expect food during daylight and rest at night. Eating a large meal close to bedtime forces the digestive and metabolic systems to work overtime during the hours they are built to wind down \u2014 keeping blood pressure and heart rate elevated when they should be falling. Aligning the fast with sleep, the researchers suggest, lets those systems do their nightly recovery work undisturbed.

The study was modest in size, and the authors are careful not to oversell it: this is an early, encouraging signal, not a prescription, and larger trials are needed. But the appeal of the approach is precisely its simplicity. It asks nothing about which foods to give up or how much to shrink a plate \u2014 only that the kitchen close a few hours earlier.

## Why It Matters for the Diaspora

For Indian-origin families, the timing angle is unusually relevant. Late dinners are a cultural fixture \u2014 meals at 9 or 10 pm, often substantial and carbohydrate-heavy, followed not long after by bed. Layer that on top of the well-documented South Asian vulnerability to high blood pressure, insulin resistance and type 2 diabetes, and the habit of eating late may be quietly working against a population already at elevated risk.

The practical takeaway costs nothing. For NRIs juggling long workdays and family routines, shifting dinner earlier, keeping the last few hours before bed food-free, and dimming the lights in the evening are changes that fit into existing life rather than upending it. No new diet, no calorie counting \u2014 just a clock. This study suggests that small adjustment may pay off where it counts most: in the quiet hours when the heart is supposed to rest."""
})

# ============================================================
# ARTICLE 3: RBI MPC minutes cut FY27 growth to 6.6% (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Central Bank Holds Rates and Trims Its Growth Forecast as the West Asia War Clouds the Outlook",
    "subheadline": "Minutes from the Reserve Bank of India's June meeting show a rate panel content to wait and watch \u2014 holding the repo rate at 5.25 percent while cutting the FY27 growth forecast to 6.6 percent, as the conflict in West Asia muddies the trade-off between inflation and growth.",
    "slug": "rbi-mpc-minutes-hold-repo-5-25-cut-fy27-growth-6-6-percent-west-asia-conflict-nri-investor-20260620-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The RBI's growth and inflation calls shape everything NRIs care about back home \u2014 the value of the rupee against their salaries abroad, the returns on their Indian deposits and equities, and the cost of money for family and businesses in India \u2014 so the central bank's cautious posture and lowered growth forecast are a direct read on the climate for diaspora money.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India rate panel downplays case for pre-emptive rate move in meeting minutes", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "AInvest \u2014 Indian Economy Faces Challenges Amidst West Asia Conflict: RBI Minutes", "url": "https://www.ainvest.com/"}
    ]),
    "body": """When a central bank decides to do nothing, the reasons it gives can be as revealing as any rate move. The minutes of the Reserve Bank of India's June meeting, released this week, show a Monetary Policy Committee that chose to sit on its hands \u2014 keeping the benchmark repo rate at 5.25 percent and holding a neutral stance \u2014 while quietly trimming its expectations for how fast the economy will grow.

## A Wait-and-Watch Committee

The decision to hold was unanimous, but the tone was cautious. Members agreed that the conflict in West Asia poses significant risks to inflation, growth, external balances and financial-market stability, even as they acknowledged that India's underlying macroeconomic fundamentals remain robust. The phrase that captured the mood was "wait and watch": a preference for keeping options open rather than acting pre-emptively in a fog of global uncertainty.

"This flexibility is especially important during periods of high uncertainty," noted one of the panel's internal members. Among the external members, Ram Singh and Nagesh Kumar leaned toward the same patient approach, arguing for greater clarity and a close eye on growth before committing to any move.

## The Growth Forecast Comes Down

The most concrete signal was the revised outlook. The RBI now expects GDP growth of 6.6 percent for the 2026-27 fiscal year, down from the 6.9 percent it had projected in April. The committee attributed the markdown to prolonged supply-chain disruptions, elevated energy prices earlier in the conflict, and the risk of a subnormal monsoon \u2014 each a drag on an economy that had been one of the world's fastest-growing.

Not everyone was relaxed about inflation. Panel member Saugata Bhattacharya struck a more hawkish note, warning that the balance of risks had "tilted towards embedding inflationary pressures" \u2014 a reminder that the spike in oil prices during the hostilities could leave a lasting mark on prices even after crude retreats.

## The Rupee Backdrop

The meeting did not happen in a vacuum. While holding rates, the RBI has rolled out a series of measures to steady the rupee, which had fallen as much as 6 percent against the dollar this year before recovering more than 1 percent on the back of those steps and a drop in oil prices. Brent crude, which had soared above $100 a barrel at the peak of the Iran-US conflict, has since slid back toward $80 as the two sides negotiated a peace deal \u2014 a major relief for a country that imports the bulk of its oil.

That easing in oil is the single biggest reason the growth-inflation trade-off looks less punishing now than it did a month ago. But the committee was clearly unwilling to bank on it. A peace deal that is still preliminary, a monsoon that has yet to play out, and a US Federal Reserve signalling possible rate hikes all argue for keeping powder dry.

## Why NRIs Should Care

For the diaspora, the RBI's posture is a weather report on the climate for their money in India. A lower growth forecast tempers the outlook for Indian equities and corporate earnings, which matters to the many NRIs holding Indian stocks and mutual funds. A neutral rate stance, combined with the central bank's drive to attract dollar deposits, shapes the returns available on NRE and FCNR accounts that diaspora savers rely on. And the rupee's path \u2014 caught between cheaper oil pulling it up and the RBI's reserve-rebuilding pulling it back \u2014 directly affects how far remittances stretch when converted back home.

The headline takeaway is steadiness over drama. The RBI is signalling that it sees real risks but solid fundamentals, and that it would rather wait for clarity than gamble on a pre-emptive move. For diaspora investors, that argues for the same patience the central bank is showing: watch the monsoon, watch oil, and watch whether the peace deal holds, because those three variables \u2014 more than any single rate decision \u2014 will set the course for the rupee and the markets through the rest of the year."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["cup of coffee espresso", "coffee beans roasted", "filter coffee cup"],
                          ["cup of coffee morning", "coffee beans"], None),
    articles[1]["slug"]: (["person sleeping bed night", "dinner table evening meal", "alarm clock bedside night"],
                          ["person sleeping peacefully night", "clock bedside table"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "indian rupee currency notes", "RBI headquarters"],
                          ["indian rupee currency finance", "central bank building"], None),
}
img_captions = {
    articles[0]["slug"]: "A UK Biobank analysis of 468,629 adults linked moderate coffee intake to lower heart disease and stroke risk",
    articles[1]["slug"]: "A Northwestern study found stopping food three hours before bed lowered overnight blood pressure and heart rate",
    articles[2]["slug"]: "The RBI held its repo rate at 5.25 percent and cut its FY27 growth forecast to 6.6 percent in June",
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
