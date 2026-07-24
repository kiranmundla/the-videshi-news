#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 14:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. BMJ Medicine study — VARIETY of physical activity (not just total volume) linked
     to ~19% lower all-cause mortality and 13-41% lower mortality from CVD/cancer/
     respiratory/other causes, after adjusting for total activity. — lifestyle-health
     (Distinct from recent strength-training-longevity & resistance-vs-aerobic pieces:
      this is about MIXING activity types.)
  2. ATTICA 20-year cohort (3,042 Greek adults, European J. Nutrition) — plant-based
     "sustainable" Mediterranean-style pattern linked to 26% lower CVD hazard per SD,
     61% lower in top vs bottom adherence; high-calorie low-white-meat pattern raised
     risk. — lifestyle-health (Distinct: this is dietary PATTERN over 20 years.)
  3. India disinvestment drive / IRFC OFS — govt selling up to 2% of IRFC at Rs91 floor,
     non-retail leg oversubscribed 1.59x, retail leg opens Thursday; FY proceeds
     Rs16,480 cr so far across Coal India/NHPC/GIC/Central Bank/NLC; FY27 target
     Rs800bn. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1400z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1400z.bin"):
            with open("/tmp/_img_dl1400z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1400z.bin")
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
# ARTICLE 1: Variety of exercise & longevity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Much You Move, but How Many Ways \u2014 Exercise Variety Is Linked to a Longer Life",
    "subheadline": "A large analysis finds that people who mix walking, lifting, cycling and other activities have lower death rates than those who rely on a single form of exercise \u2014 even after accounting for how much they do in total.",
    "slug": "exercise-activity-variety-lower-mortality-bmj-medicine-study-mixing-walking-strength-cardio-diaspora-20260625-1400",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many in the Indian diaspora settle into one fitness rut \u2014 the daily treadmill walk, the weekend cricket match, the gym routine that never changes \u2014 so evidence that mixing activity types adds years, independent of how much you do, offers a practical, low-cost upgrade for busy NRI households trying to outrun the community\u2019s high cardiometabolic risk.",
    "sources": json.dumps([
        {"name": "BMJ Medicine \u2014 study on physical activity variety and mortality risk", "url": "https://bmjmedicine.bmj.com/"},
        {"name": "Inc. \u2014 'New Research Reveals How Exercise Variety Significantly Increases Longevity'", "url": "https://www.inc.com/jeff-haden/hope-to-live-a-longer-healthier-life-new-research-reveals-how-exercise-variety-significantly-increases-longevity/91364880"},
        {"name": "European Journal of Preventive Cardiology \u2014 resistance training and all-cause mortality", "url": "https://academic.oup.com/eurjpc"}
    ]),
    "body": """Most fitness advice boils down to a single number: do more. Walk more steps, log more minutes, lift more often. A new analysis suggests the body keeps a second ledger that we tend to ignore \u2014 not how much you move, but in how many different ways. And on that measure, variety appears to buy extra years of life.

## A Different Question About Exercise

The study, published in *BMJ Medicine*, set out to test something most research overlooks. Large investigations have repeatedly shown that the total volume of physical activity \u2014 the sheer quantity of movement \u2014 is one of the strongest predictors of how long a person lives. But people do not just differ in how much they move; they differ in the kinds of movement they do. Some run and nothing else. Some only lift. Some garden, cycle, swim and walk in roughly equal measure.

To capture this, the researchers built a "variety" score reflecting how many distinct types of physical activity a person regularly engaged in, then tracked deaths over time. Crucially, they adjusted for total activity levels, so the comparison was not simply between active and inactive people. It was between people doing similar overall amounts of exercise, but in narrow versus broad ways.

## What the Numbers Showed

The pattern was striking. After accounting for total physical activity, participants with the highest variety scores had roughly a 19 percent lower risk of death from any cause compared with those in the lowest-variety group. The benefit extended across the major killers: those who mixed their activities showed between 13 and 41 percent lower mortality from cardiovascular disease, cancer, respiratory disease and other causes.

In plain terms, two people could be logging the same number of active hours each week, yet the one spreading those hours across several types of movement tended to live longer. The variety itself \u2014 not just the volume \u2014 seemed to matter.

## Why Mixing It Up May Help

The likely explanation lies in how the body adapts. Different activities stress the system in different ways, and each adaptation tends to occur within a relatively narrow band. Endurance work such as brisk walking, running or cycling drives a volume-based adaptation: the heart's chambers enlarge, it pumps more efficiently, and the circulatory system grows more resilient. Strength training drives a pressure-based adaptation instead, thickening and strengthening the heart's walls and building muscle that protects against frailty and metabolic disease.

Do only one, and you reap one set of benefits. Do both, plus the balance, mobility and coordination demanded by other pursuits, and the adaptations stack. A body trained in many directions is, in effect, prepared for more of what aging and illness throw at it. The same logic extends beyond the heart to muscles, bones, balance and metabolism, each of which responds to a different kind of demand.

A few caveats are in order. This is observational research, so it shows association rather than proof of cause and effect; it is possible that people who exercise in varied ways differ in other healthy habits. The findings do not mean a dedicated runner or weightlifter should abandon what they love and what works. Doing a great deal of one beneficial activity remains far better than doing little of anything. The message is additive, not corrective: keep the staple, but widen the menu.

## Why It Matters for the Diaspora

For many Indian-origin families abroad, exercise, when it happens, often settles into a single groove. There is the parent who walks the same neighbourhood loop every evening, the uncle whose only workout is the Sunday cricket or badminton game, the professional who lifts at the gym but sits the rest of the day. These are good habits, and they should continue. But this research suggests the next gain may come not from doing more of the same, but from adding something different.

That matters especially for a community carrying an outsized burden of heart disease and type 2 diabetes, frequently at younger ages and lower body weights than other groups. The prescription here is unusually accessible: the walker could add two short strength sessions with resistance bands at home; the lifter could take up swimming or cycling; the weekend athlete could fold in some daily mobility or a brisk walk. None of it requires a trainer, a membership or much time. It asks only for range. In a culture that prizes discipline and routine, the counterintuitive lesson is that a little variety, layered onto what you already do, may be one of the simplest investments available in a longer, healthier life."""
})

# ============================================================
# ARTICLE 2: Plant-based Mediterranean diet & CVD (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Plant-Forward Mediterranean Diet Was Tied to a 26% Lower Heart-Disease Risk Over 20 Years, a Study Finds",
    "subheadline": "Following more than 3,000 Greek adults for two decades, researchers found that those who ate the most vegetables, fruit, legumes, grains and fish had dramatically lower cardiovascular risk \u2014 while calorie-heavy diets light on lean meat fared worst.",
    "slug": "plant-based-mediterranean-diet-26-percent-lower-cvd-attica-20-year-study-european-journal-nutrition-diaspora-20260625-1400",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A plant-forward pattern built on vegetables, legumes, whole grains and fish maps closely onto traditional Indian vegetarian and coastal cooking \u2014 so for a diaspora whose diets have drifted toward calorie-dense, processed convenience food abroad, this 20-year evidence is a reminder that the heart-protective template may already sit in their own kitchens.",
    "sources": json.dumps([
        {"name": "News Medical \u2014 'Plant-based Mediterranean-style diet cuts heart disease risk by 26%'", "url": "https://www.news-medical.net/news/20260624/Plant-based-Mediterranean-style-diet-cuts-heart-disease-risk-by-2625.aspx"},
        {"name": "Sigala, Damigou, Dalmyras et al. \u2014 'Sustainable diets and long-term cardiovascular disease outcomes; insights from the 20-year follow-up ATTICA study (2002\u20132022),' European Journal of Nutrition 65, 169 (2026)", "url": "https://link.springer.com/article/10.1007/s00394-026-04022-7"}
    ]),
    "body": """The Mediterranean diet has been praised for so long that it risks sounding like a cliche. But a study that followed the same group of adults for two full decades has put a hard number on the payoff, and it is a large one: people whose everyday eating most closely resembled a plant-forward Mediterranean pattern had markedly lower odds of developing heart disease over twenty years.

## Two Decades of Watching What People Eat

The findings come from the ATTICA Study, a long-running cohort of 3,042 healthy adults from the Attica region of Greece, recruited at the turn of the century and followed with assessments at five, ten and twenty years. By the two-decade mark, 1,988 participants had complete cardiovascular records. The study's strength is precisely this length: rather than catching people in a single snapshot, it watched how their habits and their hearts played out over a span of life long enough for disease to actually develop.

Instead of scoring people against a fixed checklist, the researchers let the data reveal how people genuinely ate. Three broad dietary patterns emerged. The first was plant-based and "sustainable" \u2014 rich in vegetables, fruit, legumes and nuts, grains, fish and seafood, with some dairy. The second was a Western pattern, heavy in red meat, potatoes, sweets and eggs. The third was a high-calorie pattern that exceeded the body's energy needs while being notably low in white meat such as poultry.

## A Steep Difference in Risk

Over the twenty years, 36 percent of participants experienced a cardiovascular event. When the researchers adjusted for age, socioeconomic status, clinical factors and lifestyle, the dietary signal was clear and strong. Each one-standard-deviation increase in adherence to the plant-based, sustainable pattern was associated with a 26 percent lower risk of developing cardiovascular disease over the two decades.

The gap between the extremes was even more dramatic. Participants in the highest-adherence group for the plant-forward pattern had a 61 percent lower adjusted risk of cardiovascular disease over twenty years than those in the lowest-adherence group. At the other end, greater adherence to the high-calorie, low-white-meat pattern was linked to higher lifetime cardiovascular risk and a heavier overall disease burden, measured in years of healthy life lost. Physical activity, unsurprisingly, lowered risk; smoking raised it.

## What the Pattern Actually Looks Like

The diet that performed best is not exotic or expensive. At its core sit vegetables and fruit eaten in variety, legumes and nuts as everyday protein, whole grains rather than refined ones, fish and seafood, and olive oil in place of less healthy fats, with animal products kept modest. It is, in essence, the traditional eating of the Mediterranean rim before processed convenience food arrived \u2014 and it lines up closely with the latest dietary guidance from major heart associations, which emphasise plants, whole grains, healthy fats and minimally processed foods while limiting added sugar, salt and ultra-processed products.

The study has limits worth noting. Diet was self-reported through questionnaires, which can be imperfect; the patterns were derived statistically, involving some interpretation; and as an observational study in a single Mediterranean population, it shows association rather than proof of cause, and may not transfer perfectly to other groups. Still, its length, size and consistency add real weight to a now-deep body of evidence pointing in the same direction.

## Why It Matters for the Diaspora

For Indian-origin families, the most useful insight may be how familiar the winning template is. A plant-forward plate built on vegetables, dals and legumes, whole grains and, for those who eat it, fish, is not a foreign import \u2014 it is close to the everyday cooking of much of India, from vegetarian thalis to the fish-and-rice traditions of the coasts. The protective pattern is, in many ways, already part of the culinary inheritance.

The challenge is drift. Life abroad, with its long commutes, demanding jobs and aisles full of cheap processed food, tends to push diets toward exactly the calorie-dense, low-quality eating the study flags as harmful \u2014 more takeaways, more refined carbohydrates, more sugar and red meat, fewer vegetables and pulses. Layered on top of the community's well-documented vulnerability to heart disease and diabetes, that shift carries real cost. The encouraging takeaway is that the correction does not require a fashionable new regimen or supplements. It means leaning back into a way of eating many diaspora kitchens already know how to do \u2014 more plants, more pulses, more whole grains, less processed convenience \u2014 and trusting that, over the long run measured in this study, it pays off in the organ that matters most."""
})

# ============================================================
# ARTICLE 3: India disinvestment drive / IRFC OFS (markets-finance)
# ============================================================
articles.append({
    "headline": "India Quietly Sells Down Its Crown Jewels \u2014 the IRFC Stake Sale Shows the Disinvestment Machine Is Back",
    "subheadline": "The government offloaded up to 2% of Indian Railway Finance Corporation at a discount, and institutions snapped it up. It is the latest in a string of stake sales as New Delhi leans on its state-owned giants to plug the budget.",
    "slug": "india-disinvestment-drive-irfc-ofs-2-percent-stake-rs91-floor-oversubscribed-dipam-fy27-target-nri-investor-20260625-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "These offer-for-sale windows in marquee state-owned companies are some of the most accessible entry points for NRIs to buy into India\u2019s infrastructure and banking story, often at a built-in discount \u2014 so the return of an active disinvestment calendar directly shapes where diaspora investors can put their money to work back home.",
    "sources": json.dumps([
        {"name": "Outlook Business \u2014 'Institutional Buyers Over-Subscribe Shares Reserved in IRFC OFS'", "url": "https://www.outlookbusiness.com/"},
        {"name": "The Hindu BusinessLine \u2014 'IRFC shares tumble nearly 6% as OFS opens for non-retail investors today, Govt to sell 2% stake'", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reuters \u2014 'India to sell up to 2% stake in Indian Railway Finance Corp'", "url": "https://www.reuters.com/"},
        {"name": "LiveMint \u2014 'IRFC share price falls 5% as OFS opens for non-retail investors today'", "url": "https://www.livemint.com/"}
    ]),
    "body": """India spent years promising to shrink the state's footprint in its economy and, for long stretches, struggling to deliver. This week offered a reminder that the machinery for doing it quietly is still humming. The government put up to 2 percent of Indian Railway Finance Corporation on the block, institutions lined up to buy, and another slice of a state-owned giant passed into private hands \u2014 without much drama, but with real money for the exchequer.

## The Mechanics of a Stake Sale

The instrument is an offer for sale, or OFS, a route that lets a major shareholder \u2014 here, the Government of India \u2014 sell shares directly through the stock exchanges. The Centre offered up to 26.13 crore shares, equal to a 2 percent stake, in IRFC, the financing arm that funds the building and modernisation of Indian Railways. It set a floor price of 91 rupees a share, a discount of nearly 8 percent to the previous close, and structured the deal as a 1 percent base sale with an additional 1 percent "green shoe" option to sell more if demand was strong.

That demand duly arrived. On the first day, reserved for non-retail and institutional investors, bids poured in for more than 18.7 crore shares against the roughly 11.8 crore set aside for them \u2014 an oversubscription of about 1.59 times. The government moved to exercise part of the oversubscription option, and the retail leg of the offer opened on Thursday. At the floor price, the sale is set to raise well over 2,300 crore rupees. The share price dipped close to 6 percent as the discounted stock hit the market, a typical and short-lived reaction to the supply of cheaper shares.

## A Disinvestment Calendar That Has Quietly Filled Up

What makes the IRFC sale notable is not its size but its company. It is the latest in a steady run of stake sales this fiscal year. The government has now sold minority holdings across five central public sector enterprises, banks and insurers, taking total disinvestment proceeds to about 16,480 crore rupees so far. The roster reads like a tour of India's state-owned heavyweights: roughly 5,542 crore rupees raised from Coal India, 4,357 crore from the power producer NHPC, 3,090 crore from the insurer GIC, 2,266 crore from Central Bank of India and 1,223 crore from NLC India.

Tellingly, the government has exercised the green-shoe oversubscription option in every OFS it has run this year, a sign that investor appetite for discounted blue-chip state shares remains robust. The strategy is deliberate: rather than the headline-grabbing, politically fraught business of fully privatising companies, New Delhi has leaned on incremental minority sales that raise cash, widen the public float and improve liquidity without ceding control. The Union Budget set a disinvestment and asset-monetisation target of 800 billion rupees, around $8.4 billion, for the coming fiscal year, and the current cadence of sales is how the government chips away at it.

## Why a Cash-Hungry Government Is Selling

The timing is not incidental. India is managing a delicate fiscal and currency moment \u2014 elevated oil import bills for much of the year, a rupee that slid to record lows before stabilising, and the constant need to fund infrastructure and welfare without blowing out the deficit. Disinvestment proceeds are a relatively painless source of revenue: they bring in money, they do not add to borrowing, and in a buoyant market they can be timed to fetch good value. For state-owned companies like IRFC, a larger free float can also make the stock more liquid and more widely held, which the government frames as a benefit to ordinary investors.

There are trade-offs. Selling at a discount to the market price, as these offers do, means leaving something on the table, and critics argue that recurring minority sales of profitable, dividend-paying companies amount to selling family silver to meet annual budget needs. IRFC itself remains a profitable, dividend-paying Navratna with a central role in railway financing; the government still holds the overwhelming majority of it even after the sale.

## Why It Matters for the Diaspora

For non-resident Indians looking to invest back home, these stake sales are more than fiscal housekeeping \u2014 they are a recurring door into India's growth story. An OFS in a marquee state-owned company is one of the more transparent and accessible ways to buy a piece of the country's railways, energy or banking backbone, frequently at a built-in discount to the prevailing price. As the disinvestment calendar fills up again, NRIs eligible to invest in Indian equities will see a steady stream of such windows.

The same episode also carries a note of caution. The discounted pricing and the immediate dip in IRFC's shares are reminders that an OFS is engineered to clear stock, not to guarantee a quick gain, and that these are cyclical, policy-driven companies whose fortunes move with government priorities. For the diaspora investor, the return of an active disinvestment drive is best read as a signal: India is once again willing to sell down its crown jewels in measured slices, and for those with the appetite and the patience, the opportunities to buy in \u2014 carefully \u2014 are multiplying."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["people exercising outdoors group", "jogging running park people", "dumbbell strength training gym"],
                          ["people exercising outdoors", "group fitness running"], None),
    articles[1]["slug"]: (["Mediterranean diet vegetables fruit table", "fresh vegetables salad bowl healthy", "legumes nuts grains healthy food"],
                          ["mediterranean diet vegetables", "healthy salad vegetables bowl"], None),
    articles[2]["slug"]: (["Indian Railways train locomotive", "Indian Railways express train", "Bombay Stock Exchange building Mumbai"],
                          ["indian railways train", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A new analysis links variety in physical activity, not just total volume, to lower mortality",
    articles[1]["slug"]: "A plant-forward Mediterranean diet of vegetables, legumes, grains and fish was tied to lower 20-year heart-disease risk",
    articles[2]["slug"]: "The government sold up to 2% of Indian Railway Finance Corporation in its latest disinvestment offer for sale",
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
