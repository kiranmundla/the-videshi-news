#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 14:00 UTC batch.
Topics:
  1. Midlife sleep problems tied to lower psychological well-being a decade later, stronger in women (SLEEP 2026 / MIDUS) — lifestyle-health
  2. Cutting sugar out entirely can backfire on gut health and metabolism (ENDO 2026, Dasman Diabetes Institute) — lifestyle-health
  3. Gold's record rally falters as the Fed holds rates and hints at a hike — what it means for diaspora gold buyers — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1400.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1400.bin"):
            with open("/tmp/_img_dl1400.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1400.bin")
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
# ARTICLE 1: Midlife sleep & psychological well-being (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Bad Sleep in Your Forties and Fifties May Quietly Shape How You Feel a Decade Later \u2014 Especially for Women",
    "subheadline": "A study presented at SLEEP 2026 tracked nearly 600 middle-aged and older adults for nine years and found that those who struggled to sleep ended up with lower psychological well-being years on. The link held firm for women but faded for men once other factors were stripped out.",
    "slug": "midlife-sleep-problems-psychological-wellbeing-women-sleep-2026-midus-study-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Sleep is the first thing to go for diaspora women juggling demanding careers, young children and ageing parents across time zones \u2014 and this research suggests the broken nights of midlife are not just an inconvenience but a long-term risk to how they will feel and function a decade from now.",
    "sources": json.dumps([
        {"name": "Medical Xpress \u2014 Poor sleep in middle-aged women is associated with lower psychological well-being nearly a decade later (SLEEP 2026)", "url": "https://medicalxpress.com/news/2026-06-poor-sleep-middle-aged-women.html"},
        {"name": "Psychiatry Advisor \u2014 SLEEP: Sleep Problems Linked to Later Psychologic Well-Being", "url": "https://www.psychiatryadvisor.com/news/sleep-sleep-problems-linked-to-later-psychologic-well-being/"}
    ]),
    "body": """A bad night's sleep feels like a problem you wake up from. New research suggests the cost can linger far longer than the morning grogginess \u2014 reaching, in fact, nearly a decade into the future, and weighing more heavily on women than on men.

## What the Researchers Found

The study, presented at SLEEP 2026, the annual meeting of the Associated Professional Sleep Societies held in Baltimore from June 14 to 17, followed 574 middle-aged and older adults over roughly nine years. The participants came from the long-running Midlife in the United States study, and were assessed at two points \u2014 once between 2005 and 2006, and again between 2013 and 2017. At each visit they completed the Pittsburgh Sleep Quality Index, a standard measure of sleep trouble, and a detailed 42-item questionnaire gauging psychological well-being.

The pattern was clear. People who reported more sleep problems at the first visit tended to score lower on psychological well-being at the second \u2014 a relationship that survived even after the researchers adjusted for age, sex, education, employment, whether someone had a partner, the number of illnesses they carried, and their starting level of well-being.

## The Sex Difference

The most striking finding was not the link itself, long suspected, but how unevenly it fell. When the researchers separated men and women, the association was substantially stronger for women. In the unadjusted analysis, the effect of sleep problems on later well-being was roughly B = \u22123.23 for women versus \u22122.00 for men. After accounting for all the other factors, the link remained statistically significant for women (B = \u22121.63) but effectively dissolved for men (B = \u22120.44).

"Sleep problems appear to have lasting negative effects on psychological well-being over nearly a decade, and these effects were more pronounced among females in our sample," said lead author Fumiko Hamada, a doctoral student at the University of South Florida in Tampa, who conducted the work with Monica Walters of the University of Michigan. "This suggests that sleep may be a particularly important long-term risk factor for psychological well-being in women."

## Why Women May Be More Vulnerable

The finding sits on top of a well-documented imbalance. Women are more likely than men to report insomnia and other sleep disturbances, and according to the American Academy of Sleep Medicine, healthy sleep is not just about hours logged but about quality, regular timing, and the absence of disorders. The hormonal shifts of perimenopause and menopause \u2014 which arrive squarely in the midlife window the study examined \u2014 are notorious for fragmenting sleep, and may help explain why the long shadow falls harder on women.

## The Honest Caveats

This is observational research presented at a conference, which carries two cautions. First, an association is not proof of cause: poor sleep may erode well-being, but lower well-being can also wreck sleep, and the two likely feed each other. Second, conference findings have typically not yet cleared the full scrutiny of peer review. What the study adds is not a prescription but a direction of travel \u2014 a reason to treat midlife sleep as something worth protecting rather than enduring.

## Why This Matters for the Diaspora

For the Indian diaspora, the finding lands on a familiar pressure point. The diaspora woman in her forties and fifties is often the household's shock absorber \u2014 holding down a demanding job, raising children, and managing the health and emotional needs of parents who may be eight thousand miles and ten and a half hours away. Late-night phone calls to India, the mental load of running two households across time zones, and the cultural expectation that she simply copes all conspire against sleep.

There is also a quieter cultural barrier. In many South Asian families, a woman's exhaustion is normalised as devotion, and sleep is the first thing sacrificed and the last thing complained about. This research reframes that sacrifice: the broken nights are not a neutral cost of caregiving but a measurable risk to the very resilience the family depends on.

## What To Actually Do

Treat persistent sleep trouble as a health issue, not a personality trait or an unavoidable phase. Keep a consistent sleep and wake schedule, since regularity matters as much as duration. Raise menopausal sleep disruption explicitly with a doctor rather than waiting it out, because treatable causes are often missed. And for families, recognise that protecting the sleep of the household's primary caregiver \u2014 often a wife, mother or daughter \u2014 is not indulgence but an investment in how she will feel and function for the next decade."""
})

# ============================================================
# ARTICLE 2: Going completely sugar-free backfires (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cutting Out Sugar Entirely Sounds Healthy. A New Study Suggests It Can Backfire on Your Gut.",
    "subheadline": "Researchers at Kuwait's Dasman Diabetes Institute fed mice a low-fat diet for 16 weeks \u2014 one group with table sugar, one with none at all. The completely sugar-free group did not gain weight, but developed disrupted gut bacteria, inflammation, insulin resistance and early signs of fatty liver.",
    "slug": "sugar-free-diet-gut-health-metabolism-backfire-dasman-endo-2026-mice-study-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Diaspora families are increasingly going 'sugar-free' to fight the community's high rates of diabetes \u2014 swapping out everything from chai sugar to sweets \u2014 yet this research is an early warning that the goal should be balance and moderation, not total elimination, especially for a population already prone to metabolic disease.",
    "sources": json.dumps([
        {"name": "Fox News Health \u2014 Zero sugar, more problems? Study reveals surprising gut health effects (ENDO 2026)", "url": "https://www.foxnews.com/health/zero-sugar-more-problems-study-reveals-surprising-gut-health-effects"},
        {"name": "New York Post \u2014 Going sugar-free can mess with your gut and metabolism: study", "url": "https://nypost.com/2026/06/14/health/going-sugar-free-can-mess-with-your-gut-and-metabolism-study/"}
    ]),
    "body": """Sugar has become the dietary villain of the age, and for good reason \u2014 Americans, and increasingly Indians at home and abroad, consume far more of it than any health authority recommends, fuelling obesity, type 2 diabetes and heart disease. So the instinct to cut it out entirely feels like obvious wisdom. A new study offers an unexpected and slightly inconvenient twist: going completely sugar-free may do its own kind of damage.

## What the Study Did

The research, presented at ENDO 2026, the Endocrine Society's annual meeting in Chicago, came from the Dasman Diabetes Institute in Kuwait City. Scientists there ran a 16-week experiment on two groups of mice. Both were fed a low-fat diet \u2014 the kind generally considered healthy \u2014 with one critical difference. One group's food contained a standard amount of sucrose, ordinary table sugar. The other group's food contained no sucrose at all.

Over the four months, the researchers tracked a wide range of markers: body weight, how well the animals processed glucose, their sensitivity to insulin, levels of metabolic hormones, signs of inflammation, and the precise makeup of their gut bacteria.

## The Surprising Result

By the end, both groups of mice weighed about the same \u2014 the sugar-free diet delivered no weight advantage. But beneath the surface, the completely sugar-free animals were worse off. They developed an imbalance in their gut microbes, rising inflammation in the intestines and liver, impaired glucose control, insulin resistance, and changes associated with fatty liver disease.

"Completely removing sucrose from a low-fat diet may unexpectedly disrupt gut health and promote inflammation and metabolic dysfunction," said Dr. Rasheed Ahmad, principal scientist and head of the Immunology and Microbiology Department at the institute. The lesson he drew was not a defence of sugar but a plea for balance: "balanced nutrition is more important than simply eliminating sugar."

"The findings suggest that complete removal of sucrose from a low-fat diet may negatively affect gut microbiota and metabolic health," Ahmad added. "The study highlights the importance of maintaining balanced dietary carbohydrates to support gut and immune homeostasis."

## How To Read It \u2014 and How Not To

A few cautions are essential before anyone reaches for the sugar bowl in celebration. This was a study in mice, not humans, and rodent metabolism does not map neatly onto our own. It was presented at a conference, meaning it has not yet completed full peer review. And crucially, it does not license a high-sugar diet \u2014 the harms of excess sugar are among the best-established findings in nutrition science. What the study challenges is the fashionable extreme of total elimination, suggesting that the body's gut and metabolic systems may rely on some baseline of dietary carbohydrate to function smoothly.

The most reasonable reading is the unglamorous middle: too much sugar is harmful, near-zero may also carry costs, and the target is moderation within an overall balanced diet.

## Why This Matters for the Diaspora

For the Indian diaspora, the finding speaks directly to a live trend. South Asians develop insulin resistance and type 2 diabetes at lower body weights than most populations, and awareness of that risk has spawned a wave of "sugar-free" zeal in diaspora kitchens \u2014 artificial sweeteners in the chai, the banishment of mithai, sugar-free everything marketed aggressively to a health-anxious community.

This research is a nudge toward nuance. The danger for South Asians has never been a teaspoon of sugar in tea; it is the cumulative load \u2014 the sweets at every festival, the sugary drinks, the refined carbohydrates that dominate many diaspora diets. Swinging to the opposite extreme of total elimination, while feeling virtuous, may miss the point and, this study hints, even introduce new problems.

## What To Actually Do

Aim for moderation rather than elimination. Cut the obvious excess \u2014 sugary drinks, the second and third helping of dessert, the hidden sugar in packaged snacks \u2014 rather than chasing a zero-sugar ideal. Keep complex carbohydrates such as whole grains, legumes and vegetables in the diet, since these feed a healthy gut. Be wary of "sugar-free" processed products, which often swap sugar for additives of their own. And treat balance, not purity, as the goal \u2014 the body, it turns out, may not thank you for taking a good idea too far."""
})

# ============================================================
# ARTICLE 3: Gold's record rally falters (markets-finance)
# ============================================================
articles.append({
    "headline": "Gold's Record Run Has Stalled. After a Blistering Two-Year Rally, the Fed Just Took the Wind Out of It.",
    "subheadline": "Bullion that surged 64% in 2025 \u2014 its best year in nearly five decades \u2014 has slid back below $4,400 an ounce, sinking to a seven-month low this month as a US-Iran peace deal, falling oil and a Federal Reserve hinting at rate hikes drain the fear that powered the climb. In India, prices have eased even as a steep new import duty bites.",
    "slug": "gold-record-rally-stalls-fed-rate-hike-iran-deal-india-import-duty-nri-investor-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Gold is not merely an asset for the Indian diaspora but a cultural reflex \u2014 the default store of value, the wedding gift, the hedge sent home \u2014 and after years of one-way gains, the metal's sudden wobble forces NRIs to reckon with whether they are buying a safe haven or chasing a peak that has already passed.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Gold's record rally falters as bulls run into Fed rate expectations, stronger dollar", "url": "https://www.reuters.com/markets/commodities/"},
        {"name": "The Wall Street Journal \u2014 Gold Slips as Federal Reserve Holds Rates", "url": "https://www.wsj.com/livecoverage/stock-market-today-dow-sp500-nasdaq"}
    ]),
    "body": """For two years, gold did almost nothing but go up. The metal surged 64% in 2025 \u2014 its largest annual gain in 46 years \u2014 propelled by central banks hoarding bullion and investors scrambling for safety amid trade wars, doubts over Federal Reserve independence and the conflict in Ukraine. Then, in the space of a few weeks, the story changed. Gold has stumbled, and the forces that drove its record climb are quietly reversing.

## The Fall From the Peak

Spot gold touched an over six-month low of $4,022 an ounce earlier this month, having peaked at a record $5,318 back in late January. The slide knocked the metal below its 200-day moving average for the first time in two and a half years \u2014 a technical level that traders watch closely, and one that now sits overhead as resistance near $4,446 rather than support below. "That suggests the dynamic of the market has changed," one precious-metals trader told Reuters.

The week did bring a bounce: Comex gold settled around $4,359 an ounce after four consecutive higher sessions, its longest winning streak since May. But the metal remains roughly 18% below its January record and has given up most of the year's gains, hovering only slightly above where it started 2026.

## Why the Fear Faded

Gold thrives on fear, and three of its biggest fears have eased at once. A US-Iran agreement to wind down the Middle East war \u2014 with the prospect of the Strait of Hormuz reopening and Iranian oil returning to market \u2014 has drained the geopolitical premium that lifted bullion for months. Oil prices have tumbled to three-month lows as a result, cooling inflation expectations and reducing the case for gold as an inflation hedge.

The decisive blow came from the Federal Reserve. At its first meeting under new Chair Kevin Warsh, the central bank held interest rates steady but signalled, through its projections, that several officials now see the possibility of a rate increase later this year \u2014 a hawkish turn that dropped its earlier easing bias. Higher rates are gold's natural enemy, because the metal pays no yield and becomes less attractive when bonds and cash offer more. "Gold is currently caught between opposing forces," noted Antonio Di Giacomo of XS.com \u2014 declining geopolitical risk pulling it down, lingering policy uncertainty offering some floor.

Analyst Adrian Ash of BullionVault put the reframing bluntly: "While analysts were fixated on Trump's new world disorder, it now seems that last year's huge gains were driven in good part by rate-cut expectations." With those cuts now in doubt, a key pillar of the rally has cracked. Standard Chartered estimates that at least 270 tons of gold held in exchange-traded funds are now under water at prices below $4,250.

## The India Picture

In India, the world's second-largest gold consumer, the correction has played out with a local twist. Domestic prices eased to around \u20b91,51,360 per troy ounce in mid-June, down from the year's highs, with 24-carat gold near \u20b96,950 per gram. Softer prices nudged some jewellery buyers back into the market, though dealers report demand remains measured and confidence fragile.

A homegrown headwind is making itself felt. Last month India raised import duties on gold and silver to 15% from 6%, part of an effort to protect foreign-exchange reserves strained by oil imports. The higher levy keeps domestic prices elevated relative to global benchmarks and has dented investment appetite \u2014 India's physically backed gold ETFs logged their first net monthly outflow in a year in May, as investors booked profits after the earlier surge.

## What It Means for the Diaspora

For NRIs, gold is rarely a cold portfolio decision. It is the metal sent home for a sister's wedding, the coins gifted at Akshaya Tritiya and Dhanteras, the family hedge passed down through generations. That cultural pull is precisely why the current wobble demands a clear head. After a 64% year, buying gold now is not buying a bargain \u2014 it is buying an asset down from its peak but still historically expensive, with the rate winds turning against it.

The sober counsel is the familiar one. Gold remains a legitimate long-term hedge and diversifier, but it is not a one-way bet, and the past two years were exceptional rather than normal. NRIs weighing a purchase \u2014 whether bullion, ETFs or jewellery sent to India \u2014 should size the position to a diversification role, not a momentum trade, and remember that India's 15% import duty means the metal costs meaningfully more at home than the global price implies. The record run has paused; whether it resumes depends on the Fed, not on sentiment."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["woman insomnia sleepless", "person lying awake bed night", "tired woman bedroom morning"],
                          ["woman lying awake in bed at night", "tired woman insomnia bedroom"], None),
    articles[1]["slug"]: (["white sugar cubes", "sugar bowl spoon", "refined sugar crystals"],
                          ["sugar cubes white", "spoon of white sugar"], None),
    articles[2]["slug"]: (["gold bars bullion", "gold bullion ingots", "gold bullion bars stacked"],
                          ["gold bars bullion", "stacked gold bullion bars"], None),
}
img_captions = {
    articles[0]["slug"]: "A person lying awake at night; a new study links midlife sleep problems to lower well-being a decade later, especially in women",
    articles[1]["slug"]: "White sugar; a new study suggests cutting sucrose out entirely can disrupt gut health and metabolism",
    articles[2]["slug"]: "Gold bullion bars; bullion's record rally has stalled as the Federal Reserve hints at rate hikes",
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
