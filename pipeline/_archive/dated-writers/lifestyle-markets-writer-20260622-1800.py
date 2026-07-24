#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 18:00 UTC batch.
Topics:
  1. Obesity / estrone fuels breast cancer in postmenopausal women (Georgetown,
     Nature Reviews Endocrinology). Estrone produced in fat tissue drives
     inflammation + tumor growth, unlike estradiol; GLP-1 drugs may help by
     cutting body fat. — lifestyle-health
  2. Nitrate-rich vegetables + the oral microbiome lower blood pressure,
     especially in older adults (Exeter beetroot-juice trial; King's College
     London gum proof-of-concept). — lifestyle-health
  3. RBI sold net $8.9bn in April defending the rupee; forex reserves at a
     one-year low of $671.6bn; FY26 net dollar sales a record $53.13bn. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800z.bin"):
            with open("/tmp/_img_dl1800z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800z.bin")
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
# ARTICLE 1: Obesity, estrone and breast cancer (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Lesser-Known Estrogen Made in Body Fat May Explain Why Obesity Drives Breast Cancer After Menopause",
    "subheadline": "Scientists are zeroing in on estrone, a hormone churned out by fat tissue, as a hidden engine of postmenopausal breast cancer \u2014 and the finding helps explain why weight, and the new generation of weight-loss drugs, may matter more for risk than once thought.",
    "slug": "estrone-body-fat-obesity-postmenopausal-breast-cancer-georgetown-glp1-diaspora-20260622-1800",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian women carry a rising burden of both central obesity and breast cancer that often strikes earlier than in Western populations, yet awareness of the link between body fat and hormone-driven tumors remains low in many diaspora households \u2014 making the science of estrone a timely, actionable nudge toward waistline and metabolic health, not just mammograms.",
    "sources": json.dumps([
        {"name": "Nature Reviews Endocrinology \u2014 Estrone, obesity and postmenopausal breast cancer", "url": "https://www.nature.com/nrendo/"},
        {"name": "Knowridge Science Report \u2014 A hidden hormone may explain why obesity raises breast cancer risk", "url": "https://knowridge.com/2026/06/a-hidden-hormone-may-explain-why-obesity-raises-breast-cancer-risk/"},
        {"name": "Georgetown University Lombardi Comprehensive Cancer Center", "url": "https://lombardi.georgetown.edu/"}
    ]),
    "body": """For decades, the story of estrogen and breast cancer has revolved around a single hormone: estradiol, the powerful estrogen that dominates a woman's reproductive years. But a growing body of research is shifting attention to a quieter cousin \u2014 estrone \u2014 and the spotlight may help explain one of oncology's most stubborn puzzles: why carrying excess weight so sharply raises the risk of breast cancer after menopause.

## The Hormone Made in Fat

Before menopause, the ovaries are the body's estrogen factory, pumping out estradiol. After menopause, that production largely shuts down \u2014 but estrogen does not disappear. Instead, the body's fat tissue takes over as the main source, converting other hormones into estrone, a weaker but still biologically active estrogen.

That hand-off is where the trouble may begin. The more fat tissue a woman carries, the more estrone her body produces. Researchers, including teams whose work has been synthesized in journals such as Nature Reviews Endocrinology and at centers like Georgetown's Lombardi Comprehensive Cancer Center, estimate that postmenopausal women with obesity can have estrone levels several times higher than their leaner peers. In a body no longer making much estradiol, estrone becomes the dominant estrogen \u2014 and a steady one, bathing breast tissue in hormonal signals year after year.

## Why Estrone Behaves Differently

What makes the finding compelling is that estrone does not appear to be a mere stand-in for estradiol. Emerging evidence suggests it interacts with breast cells in its own way, tilting them toward inflammation and growth. Where estradiol's effects are comparatively well mapped, estrone seems to favor signaling pathways that encourage cells to proliferate and that stoke the low-grade, chronic inflammation increasingly recognized as fertile ground for cancer.

That distinction matters because most hormone-driven breast cancers are fueled by estrogen binding to receptors on tumor cells. If estrone is both abundant in women with obesity and especially prone to driving inflammation and cell division, it offers a mechanism \u2014 not just a correlation \u2014 for why excess body fat after menopause is so consistently tied to higher breast cancer risk.

## The Weight-Loss Drug Angle

The hypothesis carries a provocative corollary. If fat tissue is the factory and estrone the product, then shrinking the factory should cut output. That is where the new generation of GLP-1 weight-loss medications \u2014 the drugs sold as Ozempic, Wegovy and their kin \u2014 enters the conversation.

By driving significant reductions in body fat, these drugs could, in theory, lower estrone levels and with them the hormonal pressure on breast tissue. Researchers are careful to flag that this remains a hypothesis rather than a proven benefit; no one is prescribing weight-loss injections to prevent breast cancer, and long-term studies will be needed to test whether falling estrone translates into fewer tumors. But the biological logic is coherent enough that it has become an active question in cancer prevention research.

## How to Read It

The science here is still maturing, and the usual cautions apply. Hormone biology is intricate, individual risk depends on far more than estrone alone \u2014 genetics, reproductive history, alcohol, physical activity and family history all weigh in \u2014 and a plausible mechanism is not the same as a clinical guarantee. Estrone is best understood as one important piece of a larger picture, not a master switch.

Still, the practical thrust is clear and consistent with long-standing advice: maintaining a healthy weight after menopause is among the more powerful levers a woman has over her breast cancer risk, and the estrone story explains why the lever works.

## Why It Matters for the Diaspora

For the Indian diaspora, the message lands on sensitive ground. South Asian women are prone to central obesity \u2014 fat carried around the abdomen \u2014 even at body weights that look unremarkable on the scale, a pattern sometimes called being "thin on the outside, fat on the inside." Breast cancer, meanwhile, is rising in Indian and diaspora communities and often appears at younger ages than in Western populations, frequently caught late because of low screening uptake and lingering stigma.

The estrone research reframes weight not as a cosmetic concern but as a hormonal one with direct bearing on cancer risk. For NRI families, that argues for taking waistline and metabolic health seriously \u2014 through diet, physical activity and, where appropriate, medical support \u2014 alongside the mammograms and self-exams that catch disease once it has started. The hopeful note is one of agency: a risk factor rooted in body fat is, unlike genes or age, one a woman can do something about."""
})

# ============================================================
# ARTICLE 2: Nitrate-rich veg, oral microbiome, blood pressure (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Bacteria in Your Mouth Help Beetroot Lower Blood Pressure \u2014 and It Works Best as You Age",
    "subheadline": "Two new studies show that nitrate-rich vegetables like beetroot reshape the oral microbiome to ease blood pressure in older adults, and that a surprising trick \u2014 chewing ordinary sugary gum \u2014 can amplify the effect.",
    "slug": "nitrate-vegetables-beetroot-oral-microbiome-blood-pressure-older-adults-exeter-kings-college-diaspora-20260622-1800",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "High blood pressure is one of the most common and dangerous chronic conditions in the Indian diaspora, and the foods at the heart of this research \u2014 beetroot, leafy greens and other nitrate-rich vegetables \u2014 are already fixtures of the South Asian kitchen, offering NRI families a low-cost, drug-free lever that grows more effective with age.",
    "sources": json.dumps([
        {"name": "Free Radical Biology and Medicine \u2014 Dietary nitrate, the oral microbiome and blood pressure in older adults (University of Exeter)", "url": "https://www.sciencedirect.com/journal/free-radical-biology-and-medicine"},
        {"name": "University of Exeter \u2014 Beetroot juice and the oral microbiome", "url": "https://www.exeter.ac.uk/news/"},
        {"name": "King's College London \u2014 Chewing gum and dietary nitrate metabolism", "url": "https://www.kcl.ac.uk/news"}
    ]),
    "body": """One of the simplest ways to nudge blood pressure down may pass through an unexpected place: the community of bacteria living in your mouth. Two new studies have sharpened the picture of how nitrate-rich vegetables like beetroot lower blood pressure \u2014 and revealed that the benefit is strongest in exactly the people who need it most, older adults.

## How Vegetables Talk to Your Mouth

The science turns on a tidy bit of biological teamwork. Leafy greens, beetroot and other nitrate-rich vegetables flood the body with dietary nitrate. But humans cannot make much use of it alone; the crucial first step is performed by bacteria living on the tongue, which convert nitrate into nitrite. That nitrite is later transformed into nitric oxide, a molecule that relaxes and widens blood vessels, easing the pressure inside them.

In other words, the blood-pressure benefit of a beetroot salad depends on having the right microbes in your mouth \u2014 and on not wiping them out. It is one of the clearest everyday examples of the human body and its microbial passengers working as a single system.

## The Beetroot Trial

The first study, led by researchers at the University of Exeter, put that system to the test across the generations. The team recruited two groups: 39 younger adults, and 36 older adults aged roughly 67 to 79. Both groups drank concentrated beetroot juice twice a day for two weeks, then repeated the exercise with a placebo juice stripped of its nitrate.

The results split sharply by age. In the older adults, the nitrate-rich beetroot juice produced a meaningful drop in blood pressure \u2014 and reshaped the oral microbiome, suppressing bacteria associated with inflammation, including a group called Prevotella, while encouraging bacteria such as Neisseria that are linked to healthier nitrate processing. In the younger adults, the same juice barely moved blood pressure at all.

The likely explanation is that younger bodies already produce nitric oxide efficiently, leaving little room for improvement, while older adults \u2014 whose natural nitric oxide production declines with age \u2014 have more to gain from a dietary boost. It is a rare case where a healthy intervention works better, not worse, with age.

## The Chewing-Gum Twist

The second study, from King's College London, added a curious practical wrinkle. Working with 14 healthy volunteers, researchers tested whether the type of gum people chewed after consuming nitrate changed how much nitrite their bodies produced. The answer was yes \u2014 and counterintuitively, ordinary sugary gum outperformed the sugar-free kind, significantly boosting nitrite production and producing a short-term blood-pressure-lowering effect.

The finding is a proof of concept rather than a dietary recommendation; no one is suggesting people take up a sugary gum habit, with all its costs to dental health. But it demonstrates that the mouth's nitrate-processing machinery can be deliberately tuned, opening the door to future strategies \u2014 perhaps targeted lozenges or probiotics \u2014 that help the body wring more cardiovascular benefit from the vegetables people already eat.

## How to Read It

These are early, small studies, and they measure short-term effects rather than years of heart outcomes. The chewing-gum result in particular should not be mistaken for health advice. What the research establishes is a mechanism and a direction: nitrate-rich vegetables genuinely help lower blood pressure, the oral microbiome is a key intermediary, and the benefit is most pronounced in older adults.

There is also a cautionary footnote. Because the mouth's bacteria are essential to the process, habits that disrupt them \u2014 such as heavy use of antibacterial mouthwash \u2014 may blunt the blood-pressure benefit of a healthy diet, a trade-off worth keeping in mind.

## Why It Matters for the Diaspora

For the Indian diaspora, the practical payoff is considerable. Hypertension is rampant among South Asians, often developing earlier and contributing to the community's elevated rates of heart disease and stroke. And the foods at the center of this research are already staples of the Indian kitchen: beetroot, spinach and other leafy greens, and a vegetable-forward tradition rich in exactly the nitrates the body can put to work.

The message for NRI families, especially older ones, is encouraging and low-cost. Building meals around nitrate-rich vegetables \u2014 a beetroot sabzi, palak, methi and other greens \u2014 is a drug-free lever on blood pressure that appears to grow more effective with age, the very time when the heart needs the help most. It is a reminder that some of the most modern findings in cardiovascular science point back to the simplest advice: eat your vegetables, and let the bacteria do the rest."""
})

# ============================================================
# ARTICLE 3: RBI April dollar sales, forex reserves drawdown (markets-finance)
# ============================================================
articles.append({
    "headline": "The RBI Burned Through Nearly $9 Billion in a Single Month Defending the Rupee \u2014 and Reserves Are at a One-Year Low",
    "subheadline": "Fresh central bank data show the Reserve Bank of India sold a net $8.9 billion in April to slow the rupee's slide, capping a record fiscal year of intervention as foreign reserves fell to $671.6 billion and the currency clawed back from an all-time low.",
    "slug": "rbi-net-dollar-sales-april-89-billion-forex-reserves-one-year-low-rupee-defence-nri-investor-20260622-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The scale of the RBI's dollar-selling tells NRIs how hard their central bank is working to keep the rupee from sliding further \u2014 a direct signal on the value of remittances, NRE and FCNR deposits, and India-bound investments, and on whether the recent record lows are a floor or a way station.",
    "sources": json.dumps([
        {"name": "Reserve Bank of India \u2014 Monthly Bulletin (June 2026)", "url": "https://www.rbi.org.in/Scripts/BS_ViewBulletin.aspx"},
        {"name": "Reuters \u2014 RBI's net dollar sales and forex reserves data", "url": "https://www.reuters.com/world/india/"},
        {"name": "The Economic Times \u2014 Forex reserves, rupee and RBI intervention", "url": "https://economictimes.indiatimes.com/markets"}
    ]),
    "body": """The numbers tucked into the Reserve Bank of India's latest monthly bulletin read like a battlefield report. To keep the rupee from sliding too fast, India's central bank sold a net $8.9 billion in the foreign exchange market in April alone \u2014 and the cumulative cost of that defense, stretched across the past fiscal year, has reached a record.

## What the Data Show

In April, the RBI bought $16.23 billion and sold $25.17 billion in the spot market, leaving net sales of $8.94 billion. That followed an even larger net sale of about $9.8 billion in March, underscoring how relentlessly the central bank has had to lean against the currency's weakness.

Taken together, the figures cap an extraordinary year. Across the 2025-26 fiscal year, the RBI's cumulative net dollar sales reached $53.13 billion \u2014 a record, and far above the $34.51 billion it sold the previous year. Defending the rupee, in short, has become one of the central bank's most expensive and persistent tasks.

The strain shows in the reserve pile. India's foreign exchange reserves have fallen to $671.6 billion, a one-year low. The RBI's gold holdings, by contrast, were left untouched in tonnage terms at 880.52 tonnes, though their dollar value slipped from about $120.2 billion to $112.6 billion as gold prices eased \u2014 a reminder that reserves shrink not only when they are spent but when markets reprice what is held.

## Why the RBI Has Been Selling

The backdrop is a rupee that has been under sustained pressure. The currency tumbled to a record low near 96.96 per dollar last month before recovering some ground; on Monday it traded around 94.68. A central bank does not try to fix a currency at a particular level, but it does sell dollars to smooth disorderly moves and prevent a one-way slide that could stoke imported inflation and rattle confidence.

Much of the pressure has come from foreign investors heading for the exits. Overseas funds have pulled a record $30.6 billion from Indian equities so far in 2026, a powerful outflow that has weighed on the rupee. There are tentative signs of a turn: on Friday, foreign portfolio investors bought a net $515.2 million of Indian shares, their biggest single-day purchase since February \u2014 a small but watched flicker of returning appetite.

## The Market Mood Now

For the moment, the mood on Dalal Street is cautiously firmer. The benchmark Sensex rose 291 points on Monday to 77,094, while the Nifty 50 added 90 points to 24,103, helped by easing global risks and softer oil. Brent crude has slipped below $80 a barrel, a relief for an economy that imports most of its energy and a tailwind for both the rupee and the inflation outlook.

Yet the underlying tension has not vanished. The RBI's heavy intervention and shrinking reserves are a measure of how much effort it is taking to hold the line, and a reserve cushion that keeps thinning gives the central bank less room to maneuver if pressure returns. The recent recovery in the rupee owes as much to cheaper oil and a pause in outflows as to any decisive shift in the fundamentals.

## Why It Matters for NRIs

For the diaspora, the bulletin is more than a set of macro statistics. The intensity of the RBI's dollar-selling is a direct readout on how hard India is working to keep the rupee from weakening further \u2014 and that has immediate consequences for NRI finances. A weaker rupee stretches every dollar of remittances sent home and lifts the home-currency value of NRE and FCNR deposits, even as it dents the dollar worth of India-based equity and fund holdings.

The fall in reserves to a one-year low is the figure to watch. Ample reserves are India's shock absorber, the buffer that reassures global investors and gives the RBI firepower to steady the currency in a crisis. A steady drawdown does not signal danger on its own \u2014 $671.6 billion is still a substantial war chest, covering many months of imports \u2014 but it narrows the margin for comfort.

For NRIs weighing when to remit or how to position India-bound savings, the takeaway is neither alarm nor complacency. The rupee has bounced off its record low, foreign selling has paused, and oil has cooled \u2014 but the central bank's record intervention and shrinking reserves show those gains were hard-won. As ever in volatile currency weather, the wiser course is to anchor decisions to long-term goals rather than to a single month's headlines, while watching the reserve trend as a barometer of how much pressure still lies beneath the surface."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["pink ribbon breast cancer awareness", "mammography medical screening equipment", "woman doctor medical consultation health"],
                          ["breast cancer awareness pink ribbon", "woman health medical checkup"], None),
    articles[1]["slug"]: (["fresh beetroot vegetables red", "beetroot juice glass healthy drink", "leafy green vegetables spinach fresh"],
                          ["beetroot juice fresh", "fresh beetroot vegetables"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee banknotes currency", "Indian rupee coins money"],
                          ["indian rupee currency notes money", "reserve bank india"], None),
}
img_captions = {
    articles[0]["slug"]: "Researchers are focusing on estrone, an estrogen produced by body fat, to explain why obesity raises postmenopausal breast cancer risk",
    articles[1]["slug"]: "Nitrate-rich beetroot lowers blood pressure with the help of bacteria in the mouth, and the effect is strongest in older adults",
    articles[2]["slug"]: "The Reserve Bank of India sold a net $8.9 billion in April to defend the rupee, with forex reserves falling to a one-year low",
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
