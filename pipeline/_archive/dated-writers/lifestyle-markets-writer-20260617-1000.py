#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-17 10:00 UTC batch.
Topics:
  1. Flavanol-rich foods (berries, apples, green tea) beat generic '5-a-day' for heart health — lifestyle-health
  2. Three servings of whole grains slow waistline & metabolic creep (18-yr Framingham analysis) — lifestyle-health
  3. India's record $30bn foreign-outflow tide turns; FPIs net buy as oil cools, RBI steadies rupee — markets-finance
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
# ARTICLE 1: Flavanols beat generic 5-a-day (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Five-a-Day May Not Be Enough for Your Heart. The Foods That Matter Most Are Hiding in Plain Sight.",
    "subheadline": "A study of more than 30,000 adults in the US and UK found that even people who hit their fruit-and-vegetable targets rarely got enough flavanols \u2014 the plant compounds tied to a sharply lower risk of dying from heart disease. The fix is in specific foods: berries, apples with skin, beans and green tea.",
    "slug": "flavanols-five-a-day-heart-health-berries-green-tea-apples-reading-harvard-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The diaspora dutifully fills the fridge with fruit and vegetables, but a new analysis shows the heart benefit hinges on which ones \u2014 and several of the richest sources (apples, beans, the chai-adjacent habit of green tea) slot easily into an Indian kitchen already built around dal, sabzi and a daily cup.",
    "sources": json.dumps([
        {"name": "University of Reading / Food & Function \u2014 Ottaviani et al., estimated flavanol intake in 30,000+ US and UK adults", "url": "https://www.reading.ac.uk/news"},
        {"name": "New York Post \u2014 If eating 5 fruits and veggies a day isn't enough to keep a healthy heart, what's the solution?", "url": "https://nypost.com/"},
        {"name": "COSMOS trial (prior evidence) \u2014 ~500 mg/day flavanols and cardiovascular mortality", "url": "https://www.cosmostrial.org/"}
    ]),
    "body": """The advice has been drilled into a generation: eat your five a day. It turns out the number may be the wrong thing to count. A new study suggests that for the heart, *which* fruits and vegetables you eat matters far more than how many \u2014 and that most people, even the diligent ones, are missing the compounds that do the heavy lifting.

## What the Researchers Found

A team drawing on researchers from the University of Reading, Harvard Medical School, the University of California, Davis and Mars, Inc. analysed dietary data from more than 30,000 adults across the United States and the United Kingdom. Their focus was flavanols \u2014 a family of plant compounds, found in certain fruits, vegetables and green tea, that earlier trials have linked to better cardiovascular health.

The headline result, published in the journal *Food & Function*, was sobering. Even among people who met official dietary guidelines for fruit and vegetable intake, fewer than 25 percent reached an estimated flavanol intake of 500 milligrams a day \u2014 the level associated with cardiovascular benefit in previous research. Hitting your five a day, in other words, is no guarantee you are getting the part that protects your heart.

## Why the Number Misleads

The reason is that flavanol content varies wildly from food to food. Two people can both eat five servings of produce a day and absorb dramatically different amounts of these compounds, depending entirely on their choices. A plate of iceberg lettuce, cucumber and white potato technically counts toward the target while delivering almost no flavanols.

The foods that stood out as especially rich sources were specific and, for the most part, humble: plums, blackberries, cranberries, cherries, apples eaten with their skin, strawberries, blueberries, broad beans, pinto beans, and green tea. Green tea, the researchers noted, was one of the single most concentrated sources they identified.

The findings build on the COSMOS study, one of the largest clinical trials of flavanols, which suggested that consuming around 500 milligrams a day could significantly reduce the risk of dying from cardiovascular disease.

## What the Scientists Are Saying

"Flavanols can significantly reduce the risk of dying from cardiovascular disease, but only if you consume enough of them," said Dr. Javier Ottaviani, the study's lead author.

He was pointed about where people go wrong. "Most people assume that eating plenty of fruit and vegetables covers this, but what this research shows is that the specific choices you make matter far more than the total amount. Including a handful of blackberries, a whole apple or having a cup of green tea alongside your meal could make a real difference to how much of these beneficial compounds you consume and absorb from the diet."

Professor Gunter Kuhnle of the University of Reading was careful not to throw out the old message. The five-a-day guidance, he stressed, remains important; the science is simply getting more precise about which plant compounds do what. Future dietary advice, he suggested, may eventually carry specific targets for flavanols themselves.

## The Honest Caveats

This was an observational analysis of *estimated* flavanol intake, not a trial measuring heart attacks and deaths directly \u2014 so it strengthens an association rather than proving cause and effect. The 500 mg threshold comes from earlier trials, and the authors themselves note that dedicated dietary reference values for flavanols may still be needed. None of this is a license to swap a balanced diet for a fistful of blueberries and call it cardiology.

## Why It Lands for the Diaspora

South Asians carry one of the world's highest burdens of early heart disease, often striking a decade sooner than in other populations. For a community already anxious about cholesterol and family history, the practical takeaway here is unusually friendly: the richest flavanol sources fold neatly into an Indian kitchen. Apples and pears with the skin on, a bowl of berries, broad beans and pinto-style legumes that rhyme with rajma and chana, and \u2014 perhaps easiest of all \u2014 a daily cup of green tea alongside the familiar chai.

## What To Actually Do

Keep the five a day, but make a few of them count harder. Reach for berries, plums, cherries and whole apples over watery, low-flavanol produce. Leave the skin on. Lean into beans, already a staple of the vegetarian diaspora plate. And consider adding a cup of green tea to the daily routine \u2014 not as a replacement for medicine or movement, but as one of the simplest, cheapest upgrades the evidence currently supports.
"""
})

# ============================================================
# ARTICLE 2: Whole grains slow the waistline (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Three Servings of Whole Grains a Day Kept the Waistline in Check for 18 Years. The Refined Stuff Did the Opposite.",
    "subheadline": "Tracking more than 3,100 adults for nearly two decades, researchers using data from one of the longest-running heart studies found that people who ate at least three daily servings of whole grains gained far less around the middle \u2014 and saw smaller rises in blood sugar and blood pressure \u2014 than those who leaned on refined grains.",
    "slug": "whole-grains-three-servings-waistline-blood-sugar-framingham-18-year-study-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The diaspora plate runs heavy on white rice and refined-flour rotis, naan and parathas \u2014 exactly the foods this 18-year study ties to a creeping waistline and rising blood sugar; swapping in brown rice, whole-wheat atta, millets and oats is a low-effort move against the abdominal fat that drives South Asian diabetes.",
    "sources": json.dumps([
        {"name": "Framingham Heart Study analysis \u2014 whole grain intake, waist circumference and cardiometabolic risk over ~18 years (Tufts/USDA HNRCA, J. Nutrition)", "url": "https://www.framinghamheartstudy.org/"},
        {"name": "Knowridge Science Report \u2014 This simple food could prevent heart disease, high blood pressure, diabetes", "url": "https://knowridge.com/"},
        {"name": "American Heart Association \u2014 whole grains and cardiovascular health guidance", "url": "https://www.heart.org/en/healthy-living/healthy-eating"}
    ]),
    "body": """If there is a single, unglamorous food swap that the long-run evidence keeps rewarding, it is this one: trade refined grains for whole ones. A new analysis built on one of the most storied datasets in medicine has put fresh numbers on just how much that swap matters \u2014 measured not over weeks, but over nearly two decades.

## Eighteen Years of Watching the Waistline

The study drew on the Framingham Heart Study, the multi-generational investigation that has shaped much of what we know about cardiovascular disease, helping identify high blood pressure, high cholesterol, smoking, obesity and diabetes as major risk factors over the decades.

For this analysis, researchers followed more than 3,100 adults for nearly 18 years. Most were in their mid-fifties when the study began. Throughout, the team tracked the measures that quietly predict trouble: waist circumference, blood pressure, blood sugar, triglycerides, and HDL \u2014 the "good" cholesterol.

## What the Grains Did

The contrast was clear. Participants who ate at least three servings of whole grains a day saw a much slower increase in waist size than those who ate fewer. Over the study period, people with lower whole-grain intake added more than an inch to their waistline on average. Those who regularly ate more whole grains added only about half an inch.

Half an inch over 18 years may sound trivial. It is not. Abdominal fat is among the most metabolically dangerous fat in the body, and even modest restraint in its growth compounds into meaningful protection against diabetes and heart disease over a lifetime.

The benefits did not stop at the waist. Higher whole-grain eaters also showed smaller increases in blood sugar and blood pressure \u2014 the former a gateway to type 2 diabetes, the latter a leading driver of heart attack and stroke.

## The Refined-Grain Penalty

The flip side was just as telling. Participants who cut back on refined grains \u2014 white bread, white rice, sugary cereals, refined-flour products \u2014 generally fared better, with smaller increases in waist size and larger drops in triglycerides, the blood fats tied to cardiovascular risk.

The likely mechanism is no mystery. Whole grains keep their fibre, bran and germ, which slow digestion, blunt blood-sugar spikes and keep people fuller for longer. Refined grains strip most of that away, leaving a fast-digesting starch that nudges blood sugar up and appetite along with it.

## The Caveats

This is observational research: it shows a strong, durable association, not ironclad proof that whole grains alone caused the difference. People who eat more whole grains often exercise more and eat better overall, and the analysis cannot fully untangle every habit. Whole grains are also not a free pass \u2014 portion size still matters, and a "multigrain" label on a heavily processed product is not the same as an actual whole grain.

## Why This Matters for the Diaspora

Few populations should read this study more closely than the Indian diaspora. The traditional plate leans heavily on refined carbohydrates \u2014 polished white rice, maida-based naan and many restaurant breads, and refined-flour snacks \u2014 and South Asians are already prone to abdominal fat and early diabetes at lower body weights than other groups.

The encouraging part is how little has to change. Brown or hand-pounded rice in place of polished white; whole-wheat atta rotis, which many households already use; a return to millets like bajra, jowar and ragi that Indian cooking has prized for centuries; and oats or whole-grain options at breakfast. None of it requires abandoning the cuisine \u2014 only choosing its less-processed version.

## What To Actually Do

Aim for at least three servings of genuine whole grains a day, and treat refined grains as the occasional indulgence rather than the daily base. Read labels for "whole" as the first ingredient, not just "multigrain." Bring back millets. And keep the long view in mind: the payoff here is not a dramatic week-one result, but an inch you never put on \u2014 and the diabetes you may never get.
"""
})

# ============================================================
# ARTICLE 3: India's foreign-outflow tide turns (markets-finance)
# ============================================================
articles.append({
    "headline": "After a Record $30 Billion Exodus, Foreign Money Is Edging Back Into India. The Tide May Be Turning.",
    "subheadline": "Foreign investors yanked a record $30.8 billion out of Indian equities in 2026 \u2014 then turned net buyers for the first time in 13 sessions as a US-Iran peace deal cooled oil and the RBI moved to steady the rupee. Wall Street firms now say India was 'over-punished,' and its absence from the AI trade may finally be an advantage.",
    "slug": "india-foreign-outflows-reversal-fpi-net-buyers-oil-rupee-ai-gap-nri-investor-20260617",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs who watched Indian equities and their rupee-denominated portfolios slide through a brutal first half of 2026, the early signs of a foreign-money reversal reframe the question from 'how much more will I lose?' to whether the worst is now behind \u2014 and whether the diaspora's home-country bias is, for once, the contrarian call.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian shares extend gains on US-Iran peace deal; FPIs turn net buyers after 13 sessions", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 India likely past peak outflows, AI gap its advantage, Lighthouse Canton says", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "The Hindu BusinessLine \u2014 Stock Market Today, June 16: Sensex gains 544 pts, Nifty settles at 23,989", "url": "https://www.thehindubusinessline.com/markets/"}
    ]),
    "body": """For most of 2026, the story of Indian markets has been one of departure. Foreign investors pulled money out in record amounts, the benchmarks slid, and India \u2014 long the darling of emerging-market portfolios \u2014 was left watching capital rush toward the semiconductor booms of South Korea and Taiwan. This week, for the first time in months, the current showed signs of flowing the other way.

## The Scale of the Exodus

The numbers behind the gloom are stark. Foreign portfolio investors have sold a record $30.8 billion of Indian equities so far in 2026, an outflow without precedent. The benchmark Nifty 50 and Sensex were down roughly 11 and 13 percent on the year at their worst, dragged by two forces: a 27 percent collapse in the heavyweight IT index on fears of AI-led disruption, and the crude-price spike that followed the Iran conflict, which began at the end of February.

For an economy that imports most of its oil, war in the Gulf is close to a worst case. It pressures inflation, the rupee and the trade deficit all at once. Money fled accordingly, and in the space of a month South Korea and Taiwan \u2014 riding the global chip and memory mania \u2014 overtook India in total market capitalisation.

## The Turn

Then the weather changed. The United States and Iran reached a preliminary agreement to end the war and reopen the Strait of Hormuz, with a memorandum of understanding due to be signed in Switzerland on Friday. Brent crude tumbled to around $80 a barrel, its lowest since early March, and the relief rippled straight into Indian assets.

The Nifty 50 climbed for a third straight session on Tuesday to settle at 23,989, while the Sensex closed at 76,808 \u2014 gains of 3.6 and 4 percent across the three days. The rupee firmed to 94.56 against the dollar.

The most telling signal was buried in the flows data. On Monday, foreign portfolio investors turned net buyers for the first time after 13 straight sessions of selling. The inflow was tiny \u2014 about $21 million \u2014 and the trend remained choppy, with FPIs selling again on Tuesday. But the symbolism was hard to miss.

"Coordinated steps by the government and the central bank to support the rupee and draw foreign investors into bonds are positives for markets as they could lead to a reversal of foreign outflows," said Vinit Bolinjkar, head of research at Ventura Securities.

## "Over-Punished" and the Advantage of Absence

A more provocative case is now circulating among global investors: that India was sold off too hard. Lighthouse Canton, a wealth and asset manager overseeing more than $5 billion, argues the outflows have largely run their course \u2014 and that India's *lack* of AI exposure, long treated as a weakness, could prove an "advantage of absence."

"When sector concentration reaches such levels, investors tend to fatally underprice the possibility that a risk could emerge from outside the core business model," said Abhay Laijawala, the firm's India chief investment officer. South Korea and Taiwan, he noted, have themselves begun logging outflows in June as investors trim crowded chip bets. India, by contrast, offers what he called "plenty of picks and shovels" \u2014 power, data centres, electrical equipment, cooling, engineering and capital goods that feed the next phase of AI spending without the fragility of chip fabrication. Asset-management giant BlackRock made a similar argument this week, saying India's market had been "over-punished" for lacking a direct AI play.

## The Caution Flags

Optimism has limits. Foreign investors are still net sellers for the year by a record margin, and a few days of buying do not undo months of exodus. Markets opened muted on Wednesday as caution set in ahead of the US Federal Reserve's decision, with new Chair Kevin Warsh expected to strike a possibly hawkish tone. Closer to home, India's monsoon has started with a worrying rain deficit, a risk that could stoke food inflation and cap the rally. And the Iran peace deal still has to be formally signed.

## What It Means for the Diaspora

NRIs have lived this year twice over \u2014 once in their Indian equity holdings, again in the rupee value of money sent or invested home. For them, the question is shifting from how much more there is to lose toward whether the bottom is in. Some strategists are openly bullish: one sees the Nifty reaching 27,000 to 28,000 by year-end if monsoon risks recede.

The disciplined read is more measured. A turn in foreign flows, cheaper oil and a steadier rupee are genuine tailwinds, and a market that has fallen this far carries less downside than one at its peak. But three good sessions are not a trend, and the monsoon and the Fed still loom. For diaspora investors with a long horizon and a home-country bias, the case for staying invested \u2014 even adding methodically \u2014 has strengthened. The case for chasing a three-day rally has not.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["blackberries fruit", "blueberries bowl", "green tea cup"],
                          ["fresh berries bowl", "blueberries blackberries"], None),
    articles[1]["slug"]: (["whole grain bread loaf", "brown rice grains", "millet grains bowl"],
                          ["whole grain bread oats", "brown rice bowl"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building", "BSE Mumbai", "stock market trading screen india"],
                          ["stock market trading screen", "financial district mumbai"], None),
}
img_captions = {
    articles[0]["slug"]: "Berries and green tea are among the richest sources of heart-protective flavanols",
    articles[1]["slug"]: "Whole grains; a near-18-year study tied three daily servings to a slower-growing waistline",
    articles[2]["slug"]: "A stock market display; foreign investors edged back into Indian equities this week",
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
