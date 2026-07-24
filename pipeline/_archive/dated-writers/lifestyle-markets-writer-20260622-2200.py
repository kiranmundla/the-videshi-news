#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 22:00 UTC batch.
Topics:
  1. Coffee timing — morning-only coffee drinkers had the largest reductions in
     death from any cause and from cardiovascular disease in a 40,000-adult
     NHANES analysis (European Heart Journal). — lifestyle-health
  2. The protein gap — more than 1 in 3 older adults fall short of protein, with
     vegetarians and meal-skippers most exposed; muscle, frailty and the case
     for spreading protein across meals. — lifestyle-health
  3. Gold defied its safe-haven reputation during the Iran war, falling ~10% in
     India even as conflict raged; now JP Morgan sees up to 40% upside by
     year-end. What it means for the diaspora's favourite asset. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl2200z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl2200z.bin"):
            with open("/tmp/_img_dl2200z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl2200z.bin")
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
# ARTICLE 1: Coffee timing (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Health Benefits of Coffee May Hinge on the Clock: Morning Drinkers Lived Longer in a 40,000-Person Study",
    "subheadline": "People who confined their coffee to the hours before noon had the sharpest reductions in death from any cause \u2014 and from heart disease \u2014 while all-day sippers saw no such benefit, a large U.S. analysis published in the European Heart Journal found.",
    "slug": "morning-coffee-timing-lower-mortality-cardiovascular-death-nhanes-european-heart-journal-40000-adults-diaspora-20260622-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Coffee and chai are woven into the rhythm of Indian and diaspora households \u2014 the morning cup, the evening catch-up, the late-night work fuel \u2014 and this research suggests that simply pulling caffeine earlier in the day, rather than giving it up, may be the cheapest longevity tweak an NRI can make.",
    "sources": json.dumps([
        {"name": "NHLBI (NIH) \u2014 When it comes to the health benefits of coffee, timing may count", "url": "https://www.nhlbi.nih.gov/news/2025/when-it-comes-health-benefits-coffee-timing-may-count"},
        {"name": "European Heart Journal \u2014 Coffee drinking timing and mortality (Tulane/Harvard analysis)", "url": "https://academic.oup.com/eurheartj"},
        {"name": "Frontiers in Nutrition \u2014 Timing of coffee consumption and insulin resistance", "url": "https://www.frontiersin.org/"}
    ]),
    "body": """For millions of people, coffee is less a drink than a daily ritual \u2014 the cup that starts the morning, the one that rescues the afternoon, the late espresso that powers a deadline. A growing body of research now suggests that the timing of that ritual may matter as much as the habit itself, and that the longevity benefits long associated with coffee may belong mostly to those who keep it to the morning.

## What the Study Found

Researchers analysed nutrition data from more than 40,000 American adults followed for close to a decade, sorting coffee drinkers into two broad patterns: those who confined their intake to the morning \u2014 roughly between 4 a.m. and noon \u2014 and those who drank it throughout the day. About half the participants drank coffee at all; of those, more than a third were morning-only drinkers, while a smaller group sipped from morning to night.

The contrast in outcomes was striking. Adults who limited coffee to the morning were about 16% less likely to die from any cause over the follow-up period than people who drank no coffee, and roughly 31% less likely to die from cardiovascular disease. Those who drank coffee at all hours, by comparison, showed no such survival advantage \u2014 the benefit attached to the morning pattern, not to coffee in general. The findings were published in the European Heart Journal.

## Why Timing Might Matter

The researchers offer two leading explanations, both biologically plausible. The first is sleep. Caffeine has a long half-life, lingering in the body for hours, and an afternoon or evening cup can quietly erode sleep quality and disrupt the body's circadian rhythm. Poor sleep is itself tied to higher blood pressure, inflammation and cardiovascular risk, so all-day caffeine may simply be cancelling out coffee's upside by degrading rest.

The second explanation centres on inflammation. The anti-inflammatory compounds in coffee \u2014 present whether the brew is caffeinated or decaf \u2014 may do the most good in the morning, when the body's inflammatory markers tend to peak. Drinking coffee when inflammation is naturally highest could mean its protective chemistry lands when it is needed most.

A separate strand of research points in the same direction. Studies examining coffee timing and insulin resistance have found that morning-pattern drinkers show more favourable metabolic markers than all-day drinkers, hinting that the morning advantage extends beyond the heart to how the body handles blood sugar.

## The Caveats

This is observational research, and the usual cautions apply firmly. The study can establish a strong association but not prove that morning coffee causes longer life; people who drink only in the morning may differ in other ways \u2014 more regular routines, better sleep habits, healthier lifestyles overall \u2014 that the analysis cannot fully strip out. The authors themselves stress that more work is needed before anyone rewrites dietary guidance.

What the findings do not say is also worth underlining. This is not a verdict against coffee, nor a reason for non-drinkers to start. It is a nudge about pattern: for people who already drink coffee, shifting the cups earlier appears, at worst, harmless and, at best, meaningfully protective.

## How to Read It

The practical takeaway is unusually low-cost. Most longevity advice asks for sacrifice \u2014 less sugar, more exercise, fewer late nights. This asks mainly for a reshuffle. Keep the coffee; move it forward. Front-load caffeine into the morning, treat the afternoon and evening as caffeine-light, and the same habit may deliver more benefit and less sleep disruption.

## Why It Matters for the Diaspora

For the Indian diaspora, caffeine is rarely just coffee. Chai punctuates the day in many households \u2014 a morning cup, a mid-afternoon break, an after-dinner round with guests \u2014 and filter coffee holds a near-sacred place in South Indian homes. The same timing logic applies: the late cups that feel most social may be the ones quietly costing sleep.

The message is gentle and actionable, which is what makes it travel well in families that prize their tea and coffee rituals. No one needs to abandon a cherished habit. Pulling the caffeine earlier \u2014 keeping the evening chai light or switching it to a decaf or herbal alternative \u2014 is the kind of small, sustainable change that fits real life. For NRIs juggling demanding jobs and odd hours across time zones, where late-night caffeine is an occupational hazard, the research is a reminder that when you drink may shape how much good the cup actually does."""
})

# ============================================================
# ARTICLE 2: The protein gap (lifestyle-health)
# ============================================================
articles.append({
    "headline": "More Than 1 in 3 Older Adults Fall Short on Protein \u2014 and Vegetarians and Meal-Skippers Are Most at Risk",
    "subheadline": "Despite a cultural obsession with high-protein everything, large dietary surveys keep finding that a third or more of adults over 50 miss the mark \u2014 a shortfall tied to weaker muscles, more frailty and poorer diets overall, and one that hits plant-forward eaters hardest.",
    "slug": "protein-gap-older-adults-vegetarians-meal-skipping-muscle-frailty-spread-across-meals-diaspora-20260622-2200",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A large share of the Indian diaspora eats vegetarian or near-vegetarian, leans on carbohydrate-heavy staples like rice and roti, and skips or front-loads meals around busy work and fasting schedules \u2014 exactly the pattern that leaves older adults short on protein and vulnerable to muscle loss, making this a quietly urgent issue in NRI homes.",
    "sources": json.dumps([
        {"name": "EurekAlert! / Abbott \u2014 Despite America's protein craze, adults are still missing the mark", "url": "https://www.eurekalert.org/news-releases"},
        {"name": "The Journal of Nutrition, Health & Aging \u2014 Low Dietary Protein Intakes in an Aging Population (NHANES analysis)", "url": "https://link.springer.com/journal/12603"},
        {"name": "Nutrients \u2014 Dietary Protein Intake Patterns and Inadequate Protein Intake in Older Adults", "url": "https://www.mdpi.com/journal/nutrients"}
    ]),
    "body": """Walk down any supermarket aisle and protein is everywhere \u2014 stamped on cereals, bars, shakes, even water. Yet for all the marketing, the science keeps delivering an awkward verdict: a large slice of the population, especially older adults, still does not get enough. And the people most exposed are often those whose diets look healthiest on the surface.

## The Persistent Shortfall

Analyses of large national nutrition surveys have repeatedly found that more than one in three adults over 50 fail to meet even the basic recommended protein intake \u2014 and among the oldest adults, the share missing the mark climbs toward half. The recommendation in question is itself modest: about 0.8 grams of protein per kilogram of body weight per day, a floor many nutrition scientists now consider too low for ageing bodies.

The shortfall is not trivial. Studies have found that a third of those falling short were missing as much as 30 grams of protein a day \u2014 the equivalent of roughly five eggs, or more than half a typical day's requirement. Crucially, low protein intake rarely travels alone. Adults who skimped on protein tended to have poorer diets across the board, eating fewer vegetables, beans, dairy and seafood, and coming up short on other nutrients such as zinc, vitamin C and vitamin D.

## Why It Matters as We Age

Protein is the raw material the body uses to build and maintain muscle, and the stakes rise sharply with age. Older adults lose muscle naturally in a process called sarcopenia, and inadequate protein accelerates that decline. Surveys consistently link low protein intake to more functional limitations \u2014 difficulty standing, climbing stairs, walking a quarter mile, even preparing meals \u2014 and, in the oldest adults, to measurably weaker grip strength.

That cascade matters because muscle is not merely about strength. It underpins balance and mobility, cushions against falls and fractures, and plays a role in metabolic health. A condition researchers call sarcopenic obesity \u2014 declining muscle masked by accumulating fat \u2014 is a particular danger, leaving older adults simultaneously heavier and weaker, and at higher risk of frailty and cardiovascular trouble.

## The Meal-Skipping Trap

One culprit recurs in the data: skipping meals. More than 40% of adults who fell short on protein ate fewer than three meals a day, often because of a busy schedule or the reduced appetite that can accompany age. The problem is compounded by how protein is distributed. Research suggests muscles respond best when protein arrives in adequate doses \u2014 roughly 25 to 30 grams \u2014 at each meal, yet most people load nearly all of it into dinner, leaving breakfast and lunch protein-poor. Studies across multiple countries have found that the vast majority of older adults fail to reach an adequate protein threshold at breakfast in particular.

## What to Do About It

The fix is less about powders than about pattern. Spreading protein evenly across the day \u2014 eggs, dairy or legumes at breakfast, not just a token of toast \u2014 helps the body use it more efficiently for muscle. A protein-containing snack before bed has also been linked to better overnight muscle support. And for those who can, modest resistance exercise multiplies the benefit, giving the body a reason to put that protein to work.

Importantly, the goal is achievable through ordinary food. Dairy, eggs, fish and meat are dense sources, but so are lentils, beans, chickpeas, soy, paneer, yoghurt and nuts \u2014 a point that matters enormously for plant-forward eaters.

## Why It Matters for the Diaspora

For the Indian diaspora, this is not an abstract nutrition debate. A large share of the community eats vegetarian or near-vegetarian, and traditional plates often lean heavily on carbohydrate staples \u2014 rice, roti, dosa \u2014 with protein as an afterthought rather than the anchor. Add the common rhythms of diaspora life \u2014 skipped or rushed breakfasts, religious fasts, long work hours \u2014 and the result is a population structurally prone to exactly the protein gap the surveys describe.

The encouraging news is that Indian cuisine is rich in plant proteins that need only to be elevated from side dish to centrepiece. A bigger serving of dal, paneer added to the morning meal, a bowl of chickpeas or rajma, a glass of milk or a cup of curd with each meal \u2014 these are culturally familiar moves, not foreign imports. For older NRIs especially, treating protein as a deliberate target at every meal, rather than a happy accident at dinner, may be one of the simplest ways to protect strength, independence and healthy ageing in the years that matter most."""
})

# ============================================================
# ARTICLE 3: Gold's strange war (markets-finance)
# ============================================================
articles.append({
    "headline": "Gold Was Supposed to Soar During the Iran War. It Fell Nearly 10% Instead \u2014 Now JP Morgan Sees a 40% Rebound",
    "subheadline": "The metal that diaspora families trust as a crisis hedge defied its safe-haven reputation, sliding even as conflict raged, before steadying near \u20b91.46 lakh per 10 grams. The episode is a sharp lesson in how gold really behaves \u2014 and why timing it is a fool's errand.",
    "slug": "gold-defied-safe-haven-iran-war-fell-10-percent-jp-morgan-40-percent-rebound-nri-investor-20260622-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Gold is the diaspora's instinctive store of value \u2014 bought for weddings, gifted at festivals, hoarded as insurance against bad times \u2014 so its counter-intuitive slide during an actual war, and the debate over where it goes next, speaks directly to how NRIs should size and time their single most emotional investment.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 Why Gold Didn't Behave Like a Safe Haven", "url": "https://www.thehindubusinessline.com/"},
        {"name": "India Bullion and Jewellers Association (IBJA) via Patna Press \u2014 Gold climbs to \u20b91.46 lakh, silver rebounds", "url": "https://www.patnapress.com/"},
        {"name": "WSJ / Dow Jones Market Data \u2014 Gold slips as Federal Reserve holds rates", "url": "https://www.wsj.com/"}
    ]),
    "body": """In the script most investors carry in their heads, gold is the asset that shines when the world goes dark. War, panic, crashing stocks \u2014 these are supposed to be gold's moment. So the metal's behaviour during this year's Iran war has unsettled a lot of received wisdom: as the conflict escalated, gold did not surge. It fell.

## A Safe Haven That Didn't Behave

The numbers tell the story. On 27 February, the day before the war began, 10 grams of gold in India cost about \u20b91.60 lakh. By 19 June, a day after the conflict ended, it had slipped to roughly \u20b91.45 lakh \u2014 a decline of about 10%. In the international market the drop was steeper still, with prices falling close to 20% from their peak over a similar stretch. For an asset whose entire reputation rests on rising amid fear, this was the opposite of the script.

Prices have since steadied. According to the India Bullion and Jewellers Association, 24-carat gold climbed back to about \u20b91.46 lakh per 10 grams on Monday, while silver rebounded toward \u20b92.37 lakh per kilogram. But both metals remain well below the records set earlier this year \u2014 gold touched an all-time high near \u20b91.76 lakh on 29 January before shedding nearly \u20b930,000 from that peak.

## Why Gold Fell When It Should Have Risen

Several forces conspired against the metal. The first was the dollar. Gold is priced in dollars, and as the war began the dollar index strengthened by around 3%. A stronger dollar makes gold more expensive for buyers outside the United States and tends to sap demand \u2014 and for India, the second-largest item in the import bill after crude, a firmer dollar inflated the cost and cooled appetite.

The second was profit-booking. Gold had already staged an extraordinary run, climbing more than 70% between 2025 and early 2026 in its best bull market since 1979. After gains of that magnitude, investors sitting on outsized profits had every incentive to lock them in. When stock and bond markets wobbled during the conflict, gold became one of the few places where hefty gains could still be cashed out \u2014 so investors sold the winner to cover the losers.

The third was the rate backdrop. With the U.S. Federal Reserve holding interest rates steady and several officials flagging the possibility of a hike later this year, the opportunity cost of holding a non-yielding asset like gold rose. Higher-for-longer rates are a headwind for bullion, and that gravity reasserted itself just as the geopolitical drama might have lifted prices.

## The Bull Case From Here

Yet the story is far from over. JP Morgan has estimated that gold prices could climb by as much as 40% by the end of 2026, a forecast rooted in expectations that rate-hike bets will fade, that central banks will keep diversifying away from U.S. Treasuries, and that lingering global uncertainty will sustain safe-haven demand over the medium term. Analysts note that waning rate-hike expectations are historically bullish for gold; the metal has already strung together several up sessions as some of that pressure eased.

The deeper lesson, market veterans argue, is humility. Gold's slide caught even seasoned bulls off guard, just as its 2025 rocket-ride surprised the forecasters who missed it. Because gold has no cash flows, it has no easily calculable fair value, making its swings harder to predict than those of stocks or bonds.

## How to Read It

The practical conclusion is not to chase. Buying gold in a panic, after a crisis has already erupted, has repeatedly proven a bad trade \u2014 the safe-haven bid is often already priced in, and the metal can fall just when intuition screams it should rise. Long-term analysis suggests gold delivers roughly 12-13% annualised returns for Indian investors who hold it over five years, but those returns arrive in short, unpredictable bursts. That argues for a steady, modest allocation \u2014 commonly 10 to 15% of a portfolio \u2014 held through the cycle rather than timed around headlines.

## Why It Matters for NRIs

For the Indian diaspora, gold is rarely a cold financial calculation. It is bought for weddings, gifted at Diwali and Akshaya Tritiya, passed down through generations, and hoarded as a deeply felt insurance policy against hard times. That emotional weight is precisely why the past few months are instructive. An asset many NRI families treat as a guaranteed crisis hedge just behaved like anything but, falling during an actual war.

The takeaway is not to abandon gold \u2014 its long-run record and its role as a portfolio diversifier remain intact \u2014 but to hold it with clearer eyes. For NRIs deciding whether to buy now, the disciplined approach is to size gold as a fixed slice of long-term savings and add to it steadily, rather than lurching in after a forecast of 40% gains or out after a 10% fall. Gold rewards patience and punishes timing, and this year's strange war drove the point home better than any textbook could."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["cup of coffee morning espresso", "coffee cup breakfast table", "filter coffee black drink"],
                          ["morning coffee cup", "coffee black drink"], None),
    articles[1]["slug"]: (["lentils legumes protein food bowl", "chickpeas beans dal Indian food", "eggs paneer protein food healthy"],
                          ["lentils beans protein food", "healthy protein plate eggs beans"], None),
    articles[2]["slug"]: (["gold bars bullion finance", "gold jewellery Indian bangles", "gold coins bullion investment"],
                          ["gold bars bullion", "gold jewellery india"], None),
}
img_captions = {
    articles[0]["slug"]: "A large U.S. study found that adults who drank coffee only in the morning had lower rates of death than all-day drinkers",
    articles[1]["slug"]: "Lentils, beans, dairy and eggs are dense protein sources, key for older adults and vegetarians at risk of falling short",
    articles[2]["slug"]: "Gold fell nearly 10% in India during the Iran war despite its safe-haven reputation, before steadying near \u20b91.46 lakh per 10 grams",
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
