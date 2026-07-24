#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 02:00 UTC batch.
Topics:
  1. University of Reading / Harvard / UC Davis (Food and Function, 30,000+ US+UK adults):
     flavanols (berries, apples, green tea, broad beans) linked to heart protection; fewer
     than 20% hit the ~500 mg/day intake tied to lower CV death — lifestyle-health
  2. Hirosaki University, Japan (PLOS ONE, 2,044 older adults): higher blood vitamin C linked
     to better-preserved gray matter and stronger default-mode-network connectivity — lifestyle-health
  3. Gold's sixth straight down/flat week, grinding toward $4,000 off the February ~$5,600
     record — a hawkish Fed dot plot + 13-month-high dollar + the US-Iran deal unwinding the
     war premium, not fear, now drive bullion — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621a.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621a.bin"):
            with open("/tmp/_img_dl0621a.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621a.bin")
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
# ARTICLE 1: Flavanols protect the heart (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It Is Not Just How Many Fruits You Eat, but Which Ones \u2014 a Study of 30,000 Adults Points to a Missing Nutrient",
    "subheadline": "An international team tracking more than 30,000 adults in the US and UK found that fewer than one in five people get enough flavanols \u2014 the heart-protective compounds packed into berries, apples, broad beans and green tea \u2014 even among those who already eat their five-a-day.",
    "slug": "flavanols-berries-apples-green-tea-heart-disease-reading-harvard-food-function-30000-adults-diaspora-20260621-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry one of the world's highest burdens of early heart disease, and many diaspora households equate 'eating healthy' with simply piling on fruit and vegetables \u2014 so a finding that the specific foods rich in flavanols (green tea, apples with the skin, berries, broad beans) matter more than raw servings offers NRIs a precise, low-cost lever for the one disease that hits their community hardest and youngest.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 Hidden Nutrient in These Fruits May Strongly Protect Your Heart (University of Reading; Harvard Medical School; UC Davis)", "url": "https://knowridge.com/2026/06/hidden-nutrient-in-these-fruits-may-strongly-protect-your-heart/"},
        {"name": "Food and Function \u2014 study published June 8, 2026 (University of Reading)", "url": "https://pubs.rsc.org/en/journals/journalissues/fo"}
    ]),
    "body": """For years the public-health message about the heart has been refreshingly simple: eat more fruit and vegetables. A large new study suggests that advice, while sound, may be missing half the picture \u2014 because not all produce is created equal, and the foods that matter most for the heart are not always the ones people reach for.

## What the Researchers Did

The work was carried out by an international team drawn from the University of Reading, Harvard Medical School, the University of California, Davis, and the food company Mars, Inc. Their findings were published on June 8, 2026, in the journal Food and Function. The team examined dietary information from more than 30,000 adults living in the United States and the United Kingdom \u2014 a scale that lends the conclusions real weight.

Crucially, the researchers did not simply count servings. They focused on a family of natural plant compounds called flavanols, and used biomarker measurements to estimate intake more accurately than studies that rely on people remembering what they ate.

## The Missing Nutrient

Flavanols are found in a specific set of foods: blueberries, blackberries, plums, cherries, apples, broad beans and green tea, among others. Over the years, research has linked them to better blood-vessel function, healthier circulation and a lower risk of cardiovascular disease \u2014 the umbrella term for heart attacks, strokes and heart failure that kills millions every year.

The headline finding was sobering. Fewer than 20 percent of participants reached the intake level previously associated with heart-health benefits. The earlier COSMOS trial had pointed to around 500 milligrams of flavanols a day as the threshold tied to a lower risk of dying from heart disease; most people in the new analysis fell well short.

What made it more striking was that many participants who were already following general healthy-eating advice still did not get enough. Two people might each eat five servings of fruit and vegetables a day, yet one could take in far more flavanols depending on the exact foods chosen. A cup of green tea or a bowl of blackberries delivers a great deal; some other perfectly healthy foods deliver very little.

## What It Means \u2014 and What It Doesn't

The study is large and used biomarkers rather than guesswork, which is its strength. But the researchers were careful about its limits: it shows a strong association, not proof that flavanol-rich foods directly prevent heart disease. People who eat more of these foods may differ in other ways that also protect the heart.

Even so, the practical message is encouraging precisely because it is so easy to act on. Small swaps \u2014 enjoying berries, eating apples with the skin on, adding broad beans to a meal, or drinking green tea \u2014 can lift flavanol intake without any dramatic change in diet. The findings could eventually nudge dietary guidelines toward naming specific beneficial foods rather than treating all produce as interchangeable.

## Why It Matters for the Diaspora

For the Indian diaspora, the timing is pointed. People of South Asian descent face elevated rates of heart disease, often arriving a decade earlier than in other populations. Many NRI households already work hard at eating well, equating health with sheer volume of fruit and vegetables on the plate. This study reframes the task: it is not only how much produce you eat, but which kinds.

The good news is how naturally several of these foods slot into a diaspora kitchen. Green tea is an easy daily ritual; apples and berries are supermarket staples; broad beans sit comfortably alongside the legumes already central to Indian cooking. None of this replaces the fundamentals \u2014 not smoking, staying active, and keeping blood pressure, blood sugar and cholesterol in check. But for a community that loses too many people to heart disease too young, a cheap, simple tweak to what goes in the fruit bowl is a lever worth pulling."""
})

# ============================================================
# ARTICLE 2: Vitamin C and brain aging (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Common Vitamin May Be Quietly Shaping How the Brain Ages, a Study of 2,000 Older Adults Finds",
    "subheadline": "Older adults with higher blood levels of vitamin C had better-preserved gray matter and stronger connections in a key memory network, Japanese researchers report \u2014 the first study to tie measured vitamin C in the blood, not just diet surveys, directly to brain structure.",
    "slug": "vitamin-c-blood-levels-brain-gray-matter-default-mode-network-hirosaki-plos-one-2044-adults-diaspora-20260621-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Vegetarian and predominantly plant-based diets are common across Indian diaspora households, and the citrus fruits, berries, tomatoes and green leafy vegetables that supply vitamin C are kitchen staples \u2014 so a finding that blood levels of this everyday nutrient track with healthier brain ageing speaks directly to NRI families thinking about how to protect memory and cognition in their parents and themselves.",
    "sources": json.dumps([
        {"name": "New York Post \u2014 Common vitamin may influence brain aging in ways scientists didn't expect (Hirosaki University)", "url": "https://nypost.com/2026/06/16/health/common-vitamin-may-influence-brain-aging-in-ways-scientists-didnt-expect/"},
        {"name": "PLOS ONE \u2014 Hirosaki University study of plasma vitamin C and brain MRI markers", "url": "https://journals.plos.org/plosone/"}
    ]),
    "body": """Vitamin C is one of the most familiar nutrients in the kitchen \u2014 the stuff of orange juice and the first thing many reach for at the start of a cold. New research from Japan suggests it may also be quietly involved in something far more consequential: how the brain holds up as we age.

## What the Study Found

The work, published in the journal PLOS ONE, came out of Hirosaki University and drew on 2,044 residents of Hirosaki City who had originally been recruited into a long-running study of dementia and heart-disease risk. Their average age was 69, and 61 percent were women.

Researchers used MRI scans to measure the volume of gray matter and white matter in participants' brains, then compared those measurements against the level of vitamin C circulating in their blood. Even after accounting for age, smoking, diabetes and other lifestyle factors, a clear pattern emerged: people with lower vitamin C levels tended to have lower brain-tissue volumes and weaker structural network patterns.

"Older adults with higher blood levels of vitamin C tend to have better-preserved brain structure (gray matter) and stronger connections within the default mode network," said Tomohiro Shintaku, an assistant professor in the radiology department at Hirosaki University's graduate school of medicine. The default mode network is a crucial set of brain regions involved in memory and cognition \u2014 and one of the first to be disrupted in conditions such as Alzheimer's disease and depression.

## Why This One Is Different

Diets rich in vitamin C have long been linked to a lower risk of cognitive decline. What sets this study apart, the researchers say, is that it is the first to connect actual measured vitamin C in the blood \u2014 rather than estimates from food questionnaires \u2014 directly to the structural connectivity of that memory network. Blood measurement is more accurate than asking people to recall what they ate, which makes the association harder to dismiss.

"What I found most fascinating is that we could detect such clear associations between a single nutritional factor and large-scale brain networks in a robust cohort of over 2,000 older adults," Shintaku said. Because the human body cannot manufacture vitamin C on its own, he added, it has to come from the daily diet.

## The Important Caveats

The researchers were candid about the study's limits, and so should any reader be. It is observational and cross-sectional \u2014 a single snapshot \u2014 which means it can show an association but cannot prove that vitamin C causes healthier brain ageing. Each participant had only one blood measurement. And because nearly all the participants were older Japanese adults, the findings may not translate neatly to other populations.

The link was also relatively modest next to established risk factors such as high blood pressure and high blood sugar. Larger studies, including UK Biobank research involving more than 9,000 people, suggest vitamin C is just one of several factors that shape brain health. As one independent physician put it, the study "does not prove that vitamin C prevents cognitive decline or that taking supplements will improve brain health. It is best viewed as a signal that vitamin C status may be one piece of a much larger brain-health picture."

## Why It Matters for the Diaspora

For Indian-origin families, the practical takeaway is reassuringly ordinary. The advice is not to rush out for high-dose supplements \u2014 the signal here is about getting enough through food, not megadosing. And the foods that deliver it are already diaspora staples: citrus fruits, berries, tomatoes, amla, guava, capsicum and the green leafy vegetables that anchor so much vegetarian cooking.

That matters because many NRI households are actively thinking about cognitive health \u2014 watching ageing parents, and increasingly themselves, for the early signs of memory trouble. This study does not hand them a cure. But it adds a gentle, low-cost data point to a familiar message: a colourful, vegetable-and-fruit-forward plate, the kind already common in Indian kitchens, may be doing the ageing brain quiet favours alongside the heart it is better known for protecting."""
})

# ============================================================
# ARTICLE 3: Gold answers to the Fed, not the fear (markets-finance)
# ============================================================
articles.append({
    "headline": "Gold Is Supposed to Soar When the World Looks Dangerous. This Year It Is Doing the Opposite.",
    "subheadline": "Bullion has logged its sixth straight week of lower or flat closes and is grinding toward $4,000 \u2014 far below February's near-$5,600 record \u2014 even with a Middle East war and an unsigned ceasefire on the table. The reason is not fear, but a hawkish Federal Reserve and a dollar at a 13-month high.",
    "slug": "gold-price-falls-toward-4000-hawkish-fed-dollar-us-iran-deal-war-premium-unwinds-nri-investor-20260621-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Gold is the diaspora's default store of value \u2014 in wedding jewellery, in sovereign gold bonds, in the ETFs and coins NRIs buy to hedge a wobbly rupee \u2014 so a sharp, counter-intuitive slide in the metal even as geopolitical risk lingers is a direct signal to Indian-origin investors about whether their favourite safe haven is still doing the job they bought it for.",
    "sources": json.dumps([
        {"name": "FXStreet \u2014 Gold answers to the Fed, not the fear", "url": "https://www.fxstreet.com/news/gold-answers-to-the-fed-not-the-fear-202606192156"},
        {"name": "Reuters \u2014 Gold slips as hawkish Fed signals lift dollar, boost rate hike bets", "url": "https://www.reuters.com/world/india/gold-climbs-over-1-oil-drops-us-iran-interim-deal-2026-06-18/"}
    ]),
    "body": """Gold is meant to be the asset you want when the world turns frightening. That is what makes this year's price action so quietly remarkable. Bullion has just closed its sixth straight week of lower or flat finishes and is grinding toward the $4,000 mark \u2014 a long way below the near-$5,600 record it set in February \u2014 even as a Middle East war runs into its fourth month and an unsigned ceasefire keeps geopolitical risk firmly on the table. The metal that is supposed to thrive on exactly this backdrop is instead sliding. The explanation has almost nothing to do with fear, and almost everything to do with the US Federal Reserve.

## The Only Chart That Matters

For all the alarming headlines, gold has spent the past six weeks trading as a near-perfect inverse of US real yields. The Federal Reserve held its benchmark rate steady in June, but its updated "dot plot" \u2014 the chart of where policymakers expect rates to go \u2014 shifted sharply hawkish, with nine of nineteen officials now seeing a need for a rate hike later in the year. Markets responded by pricing in roughly an 85 percent chance of a US rate increase by December, up from 61 percent before the meeting.

That matters enormously for gold. The metal pays no interest, so when policy rates and real yields rise, the opportunity cost of holding it climbs and its appeal fades. A US dollar index sitting at a 13-month high does the rest, because a stronger dollar makes dollar-priced bullion more expensive for buyers everywhere else. Every bullish geopolitical impulse this spring has been overwhelmed by that single bearish force.

## Hot Inflation, Cold Metal

The cruel twist for gold's backers is that inflation is behaving exactly as it should to help them \u2014 and hurting them anyway. Headline US consumer prices leapt above 4 percent year-on-year in May, and the energy shock from the conflict pushed inflation expectations higher across the board. Ordinarily that is a textbook buy signal for an inflation hedge.

The catch is that markets trust the Fed to crush that inflation with higher rates. So the same data reads as both an inflation signal and a tightening signal at once \u2014 and the tightening signal wins. Gold ends up paying the bill for the very inflation it is supposed to protect against.

## The War Premium Unwinds

The geopolitical side has weakened too. The United States and Iran signed an interim agreement to wind down their conflict and reopen the Strait of Hormuz, defusing the tension that had injected a fear premium into gold during the spring. As that premium unwound, so did a chunk of the haven demand that had carried the metal toward its highs. Brent crude has tumbled to its lowest since early March, easing the inflation fears that had been gold's one remaining tailwind. Both of bullion's core demand pillars \u2014 its role as a hedge against loose money and its role as a refuge in turmoil \u2014 cracked at the same time.

## Why NRIs Should Care

For the Indian diaspora, gold is not an abstraction. It is wedding jewellery, sovereign gold bonds, the ETFs and coins that NRIs accumulate to hedge against a soft rupee and uncertain times. Watching the metal fall even as conflict simmers is a useful, if uncomfortable, lesson: gold is not a one-way bet on chaos. In the short run it answers to US interest rates and the dollar far more reliably than to the day's frightening headlines.

There is a silver lining for buyers. A pullback toward $4,000 makes accumulation cheaper for those building a long-term position or shopping ahead of the wedding season, and central banks in emerging economies \u2014 India among them \u2014 have kept adding to reserves through the cycle, a structural source of demand that does not vanish with the war premium. But for now the near-term path of least resistance points lower, and it will be set less by the Middle East than by the Fed. The next big test comes with US inflation data: a hot reading reinforces the case for hikes and could push gold through $4,000, while a soft print is the bulls' clearest route to a bounce. Either way, diaspora investors looking to gold for a steady anchor should expect it to keep dancing to Washington's tune, not the world's fears."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["fresh blueberries blackberries bowl", "green tea cup leaves", "apples fruit basket fresh"],
                          ["fresh berries bowl", "green tea cup"], None),
    articles[1]["slug"]: (["citrus fruits oranges vitamin", "fresh fruits vegetables citrus", "oranges lemons fruit"],
                          ["oranges citrus fruit fresh", "fresh fruit vegetables"], None),
    articles[2]["slug"]: (["gold bullion bars", "gold bars ingots", "gold coins bullion"],
                          ["gold bars bullion", "gold bullion finance"], None),
}
img_captions = {
    articles[0]["slug"]: "Flavanol-rich foods such as berries, apples and green tea were linked to better heart health in a 30,000-adult study",
    articles[1]["slug"]: "Citrus fruits and leafy vegetables are key sources of vitamin C, which a Japanese study tied to better-preserved brain structure",
    articles[2]["slug"]: "Gold has logged six straight weeks of lower or flat closes, sliding toward $4,000 amid a hawkish Fed",
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
