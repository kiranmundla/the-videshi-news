#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 14:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Resistance training + aerobic exercise sharply cuts type 2 diabetes risk — a
     new JAMA Network Open prospective cohort study of 143,715 US health
     professionals followed ~19 years; >=2h/week resistance training cut T2D risk
     by ~27% (HR 0.73), and combining it with aerobic activity + less TV cut risk
     by 62% (HR 0.38). — lifestyle-health
  2. Fat quality over fat quantity — a review in Trends in Endocrinology &
     Metabolism (Cell Press, Univ. of Barcelona/CIBERDEM) argues palmitic acid
     (saturated) impairs insulin action while oleic acid (olive oil) protects it,
     suggesting the TYPE of fat matters more than the total amount for diabetes
     risk. — lifestyle-health
  3. Jio Platforms files DRHP for India's biggest-ever IPO — ~Rs 35,000-40,000cr
     ($3.8bn) fresh issue of 270m shares, all proceeds to repay debt + fund 5G/AI,
     NO offer-for-sale so marquee 2020 backers (Meta, Google, KKR, PIF) can't cash
     out; valuation debate $131bn-$180bn. — markets-finance
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
# ARTICLE 1: Resistance + aerobic exercise cuts T2D risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Lifting Weights, Not Just Walking, May Be the Missing Piece in Holding Off Diabetes",
    "subheadline": "Tracking nearly 144,000 adults for almost two decades, researchers found that regular strength training cut the risk of type 2 diabetes \u2014 and pairing it with aerobic exercise and less screen time cut that risk by more than half.",
    "slug": "resistance-training-aerobic-exercise-type-2-diabetes-risk-jama-network-open-143715-adults-diaspora-20260624-1400",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians develop type 2 diabetes earlier, at lower body weights, and at far higher rates than most populations \u2014 yet exercise in many diaspora households still means a walk, if anything, with strength training seen as optional or vain; this study reframes resistance work as a core piece of prevention for the community most at risk.",
    "sources": json.dumps([
        {"name": "JAMA Network Open (2026) \u2014 Zhang T, Zhang Y, Lee DH, et al., 'Long-Term Resistance Training and Risk of Type 2 Diabetes' (DOI: 10.1001/jamanetworkopen.2026.19420)", "url": "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2850563"},
        {"name": "News-Medical \u2014 'Strength training plus cardio cuts type 2 diabetes risk the most'", "url": "https://www.news-medical.net/news/20260623/Strength-training-plus-cardio-cuts-type-2-diabetes-risk-the-most.aspx"}
    ]),
    "body": """For decades, the standard prescription for warding off type 2 diabetes has been some version of \"get moving\" \u2014 walk more, take the stairs, get your steps in. A large new study suggests that advice, while sound, has been quietly leaving out half the equation. The other half is muscle.

## What the Researchers Did

The study, published in the journal JAMA Network Open, is a prospective cohort analysis \u2014 a design that follows large groups of people forward in time to see who develops a disease and what behaviours precede it. The researchers pooled data from three of the most respected long-running health databases in the United States: the Health Professionals Follow-up Study and the two Nurses' Health Studies, which together have tracked the habits and health of doctors, nurses and other healthcare workers for years.

In all, 143,715 adults who were free of diabetes, major heart disease and cancer at the outset were followed for nearly two decades. Every two to four years, participants reported how much time they spent on resistance training \u2014 weights, resistance bands, bodyweight work \u2014 alongside their aerobic activity and how much television they watched, a stand-in for sedentary time. Over roughly 19 years of follow-up, 10,038 of them developed type 2 diabetes.

## The Findings

The pattern was striking and consistent. Compared with people who did no strength training at all, those who did at least two hours a week had a 27 percent lower risk of developing type 2 diabetes. The benefit grew with consistency: middle-aged adults who kept up high levels of resistance training over time \u2014 even as little as 30 minutes a week, done reliably \u2014 had a 42 percent lower risk.

But the headline number came when the researchers looked at exercise in combination. People who met the recommendations for both resistance training and aerobic activity \u2014 at least an hour of strength work and a meaningful dose of brisk movement each week \u2014 while keeping television to under two hours a day had the lowest risk of all: a 62 percent reduction. The two forms of exercise, in other words, were not interchangeable. They stacked.

Crucially, the protective effect held up even after the researchers accounted for body weight, waist size and intentional weight loss \u2014 meaning the benefit was not simply a matter of exercise helping people stay slim. Muscle appears to do something for blood-sugar control that goes beyond the number on the scale.

## Why Muscle Matters for Blood Sugar

The biology offers a clean explanation. Skeletal muscle is the body's largest sink for glucose; after a meal, it soaks up sugar from the bloodstream, and it does so more readily when it is worked and well-conditioned. Resistance training builds and maintains that muscle and improves insulin sensitivity \u2014 the body's ability to respond to the hormone that ushers glucose out of the blood and into cells. As people age and muscle quietly wastes away, that buffering capacity shrinks, and blood sugar has fewer places to go.

## The Caveats

The authors are careful about the limits of their work. This is observational research, which can show a strong, durable association but cannot by itself prove cause and effect. People who train consistently also tend to eat better, smoke less and live healthier lives overall, and while the researchers adjusted for many such factors, residual confounding cannot be ruled out. The study population was also overwhelmingly white and made up of healthcare professionals, so the precise numbers may not transfer perfectly to other groups. The authors call for more diverse studies with objective measures of strength training to pin down the ideal type and dose.

## Why It Matters for the Diaspora

For people of Indian and South Asian origin, this lands on urgent ground. The community carries one of the highest burdens of type 2 diabetes in the world, often developing it a decade earlier and at lower body weights than other populations \u2014 a phenomenon doctors link partly to a body composition that tends toward less muscle and more visceral fat, sometimes called the \"thin-outside, fat-inside\" pattern. That makes preserving and building muscle not a cosmetic concern but a metabolic one.

Yet in many diaspora households, exercise, when it happens, still means the evening walk \u2014 valuable, but only part of the story. Strength training is frequently dismissed as the preserve of the young, the vain or the gym-obsessed, and is especially neglected by women and older adults, precisely the groups who stand to gain the most. This research argues for a cultural rethink: a couple of strength sessions a week, using nothing more than resistance bands, a pair of dumbbells or one's own body weight at home, layered on top of the familiar walk. For a community fighting diabetes on the front line, the evidence suggests the most powerful prevention may be the one it has been skipping."""
})

# ============================================================
# ARTICLE 2: Fat quality vs quantity & diabetes (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Much Fat You Eat, but Which Kind \u2014 a Diabetes Review Shifts the Blame",
    "subheadline": "Scientists reviewing the molecular evidence argue that palmitic acid, common in palm oil, fried food and baked goods, quietly sabotages insulin, while the oleic acid in olive oil and nuts may shield against it \u2014 pointing to fat quality, not quantity, as the real lever.",
    "slug": "dietary-fat-quality-palmitic-oleic-acid-insulin-resistance-type-2-diabetes-review-trends-endocrinology-diaspora-20260624-1400",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Palm oil and reused frying oil are everywhere in the Indian diaspora's kitchens and takeaways \u2014 in packaged snacks, sweets, namkeen and restaurant fryers \u2014 making palmitic acid an unusually heavy presence in desi diets already burdened by sky-high diabetes rates; this review suggests swapping the oil, not just cutting the fat, could matter more than calorie-counting.",
    "sources": json.dumps([
        {"name": "Trends in Endocrinology & Metabolism (Cell Press, 2026) \u2014 Palomer X, Rodr\u00edguez-Calvo R, Tajes M, Wahli W, V\u00e1zquez-Carrera M, 'Palmitic and oleic acids in type 2 diabetes mellitus' (DOI: 10.1016/j.tem.2026.01.003)", "url": "https://www.cell.com/trends/endocrinology-metabolism/abstract/S1043-2760(26)00003-9"},
        {"name": "Medical Xpress \u2014 'Quality versus quantity of fat in the diet affects development of diabetes'", "url": "https://medicalxpress.com/news/2026-quality-quantity-fat-diet-affects.html"}
    ]),
    "body": """For years, dietary advice on fat has swung between extremes \u2014 fat is the enemy, then fat is fine, then it depends. A new scientific review cuts through the confusion with a sharper claim: when it comes to diabetes, the question is less how much fat you eat than what kind. Two of the most common fats in the human diet, the review argues, pull in opposite directions \u2014 one undermining the body's response to insulin, the other helping to protect it.

## The Two Fats at the Centre

The review, published in the Cell Press journal Trends in Endocrinology & Metabolism, was led by researchers at the University of Barcelona and Spain's CIBER network for diabetes research. It focuses on two fatty acids that dominate what most people eat: palmitic acid and oleic acid.

Palmitic acid is a saturated fat. It is the most common saturated fatty acid in many modern diets, found in palm oil, dairy, cocoa butter, red meat and, abundantly, in the processed and fried foods that fill supermarket shelves \u2014 margarine, cereals, sweets, baked goods and fast food. Oleic acid, by contrast, is a monounsaturated fat. It is the signature fat of olive oil, and is also plentiful in nuts, avocados, sunflower seeds and canola oil.

The review's central finding is that these two fats are not metabolically equivalent. \"Palmitic acid, a saturated fatty acid widely found in foods, is associated with impaired insulin sensitivity, whereas oleic acid, abundant in olive oil, may have a protective effect against these metabolic disorders,\" said Professor Manuel V\u00e1zquez-Carrera, who led the work.

## What Palmitic Acid Does Inside the Cell

The strength of the review lies in its account of the molecular machinery. According to the first author, Xavier Palomer, palmitic acid \"promotes the accumulation of potentially toxic bioactive lipids, fosters low-grade chronic inflammation, and contributes to the dysfunction of cellular organelles\" \u2014 specifically the endoplasmic reticulum and the mitochondria, the cell's protein-folding and energy-producing structures.

Each of those processes interferes with insulin signalling, the chain of molecular events by which the hormone insulin tells cells to absorb glucose from the blood. When that signalling is blunted, blood sugar rises and the slow march toward type 2 diabetes begins. Oleic acid appears to do the reverse: rather than generating toxic byproducts, it is stored relatively harmlessly as inert triglycerides, and it can counteract several of the damaging effects palmitic acid sets in motion.

## A Shift in Emphasis \u2014 With Caveats

The practical upshot, the authors stress, is a change in emphasis. \"This review highlights the significant role of the quality of dietary fat, rather than the total amount consumed,\" V\u00e1zquez-Carrera noted. It helps explain why diets rich in monounsaturated fat \u2014 the Mediterranean diet being the classic example \u2014 are repeatedly linked to lower rates of type 2 diabetes.

The review is candid about the unsettled science. It is a synthesis of laboratory and observational evidence, not a single controlled trial, and the authors note that some recent population studies have found weaker or even conflicting links, partly because oleic acid's effect may depend on whether it comes from a plant or an animal source, and because fatty acids in real food never travel alone. They call for randomized intervention trials that distinguish fats by their source, processing and specific molecular form before firm dietary rules are written. This is, in short, a compelling mechanistic argument rather than the final word.

## Why It Matters for the Diaspora

For the Indian diaspora, the review touches a nerve that runs straight through the kitchen. Palm oil is one of the most widely used cooking and processing fats in South Asian food \u2014 cheap, heat-stable and ubiquitous in packaged namkeen, biscuits, instant noodles, sweets and the deep fryers of countless takeaways and home kitchens. Combined with the diaspora's already elevated risk of type 2 diabetes, that makes palmitic acid an unusually prominent guest at the table.

The encouraging part of this research is how actionable it is. It does not demand a low-fat life of deprivation; it suggests a swap. Cooking in oils richer in monounsaturated fat \u2014 olive, groundnut or mustard oil \u2014 in place of palm oil and repeatedly reheated frying oil; leaning on nuts and seeds for fat rather than packaged fried snacks; and treating ultra-processed foods, where palmitic acid hides in bulk, as occasional rather than daily. For families who often equate healthy eating with simply eating less, the message is more hopeful and more precise: it may matter less how much oil is in the pan than which oil it is."""
})

# ============================================================
# ARTICLE 3: Jio Platforms IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "Jio Files for India's Biggest-Ever IPO \u2014 but This Time, the Marquee Backers Don't Get to Cash Out",
    "subheadline": "Reliance's digital arm has filed papers for a roughly $3.8 billion listing, with every rupee earmarked for debt and growth \u2014 meaning the Meta, Google and Gulf investors who poured in during 2020 will have to wait their turn.",
    "slug": "jio-platforms-drhp-india-biggest-ipo-fresh-issue-no-offer-for-sale-debt-5g-ai-nri-investor-20260624-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Jio's listing will be the marquee Indian IPO of a generation, and NRIs \u2014 long among the most eager retail buyers of marquee Indian names \u2014 will be weighing whether to chase it; the unusual all-fresh-issue structure and the holding-company discount are exactly the fine print diaspora investors need to read before committing.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'Ambani's Jio Platforms files for $3.8 billion IPO that could be India's biggest, sources say'", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Communications Today \u2014 'Jio Platforms' big global backers sit out the IPO. They don't have a choice'", "url": "https://www.communicationstoday.co.in/jio-platforms-big-global-backers-sit-out-the-ipo-they-dont-have-a-choice/"},
        {"name": "The Wall Street Journal \u2014 'Reliance's Jio Platforms to Seek India Listing'", "url": "https://www.wsj.com/business/telecom/reliance-jio-platforms-india-ipo"}
    ]),
    "body": """India's stock market is about to get the listing it has been waiting years for. Jio Platforms, the telecom-and-technology arm of Mukesh Ambani's Reliance Industries, has filed its draft prospectus with the market regulator for an initial public offering that, by size, would be the largest in the country's history. But buried in the paperwork is a detail that sets this deal apart from almost every other blockbuster IPO: the early investors who made Jio one of the world's most valuable startups will not be selling a single share.

## The Numbers

Jio Platforms filed its draft red herring prospectus \u2014 the formal document that opens an IPO \u2014 with the Securities and Exchange Board of India on June 19. The offering is built around a fresh issue of 270 million new shares, with the final price to be set later through a book-building process. Estimates put the size in the range of 350 to 400 billion rupees, or roughly 3.8 billion dollars, which would comfortably eclipse India's previous record listings and rank among the biggest the market has seen.

To get there, Jio is diluting just 2.5 percent of its equity, taking advantage of a recent government rule that lets very large companies list with a smaller initial float than the usual minimum. Even at that sliver, the valuation under discussion is enormous: analysts have pegged Jio Platforms anywhere from around 131 billion dollars to as high as 180 billion, depending on how one values its tangle of telecom, digital, cloud and AI businesses.

## Where the Money Goes

What makes the structure unusual is the complete absence of an offer-for-sale component. In a typical mega-IPO, a fresh issue \u2014 new shares that raise money for the company \u2014 is paired with an offer for sale, in which existing shareholders sell some of their holdings and pocket the proceeds. Jio's filing has no such provision. Every rupee raised flows to the company itself.

The bulk of it has a clear destination. According to the prospectus, about 275 billion rupees of the proceeds will go to repay debt held by Reliance Jio Infocomm, the group's telecom operating company, with the remainder set aside for general corporate purposes and the costs of the issue. Repaying that debt, the company says, will leave it better positioned to keep investing in its priorities \u2014 densifying and expanding its 5G network, pushing fixed-line broadband deeper into Indian homes, and building out its artificial-intelligence and cloud services. Ambani has called the listing \"the most important value creation milestone this year.\"

## The Backers Who Have to Wait

The structure has a pointed consequence for Jio's celebrated roster of investors. In a frenzied stretch in 2020, at the height of the pandemic, Jio Platforms raised more than 1.5 lakh crore rupees from a who's who of global capital. Meta's affiliate took nearly 10 percent; Google took 7.73 percent; KKR, Vista Equity Partners, Silver Lake, Intel Capital, Saudi Arabia's Public Investment Fund, Abu Dhabi's Mubadala and Singapore's sovereign funds all bought in.

Because this IPO is a pure fresh issue, none of those marquee names will convert any of their paper wealth into cash at the listing. They are, in effect, sitting it out \u2014 not by choice, but by the design of the deal. Their exits, whenever they come, will have to wait for a later sale in the open market.

## The Investor's Dilemma

For all the excitement, analysts have flagged reasons for caution. Jio Platforms sits inside the sprawling Reliance conglomerate, and listed holding structures like it often trade at a \"holding company discount\" \u2014 the market values the parts at less than they might fetch on their own, because of the complexity of the ownership web. That, some analysts warn, could temper the immediate gains even for new buyers. The valuation itself remains a live debate, with estimates spanning nearly 50 billion dollars, a sign of how hard it is to price a business that spans a telecom giant, a digital-services empire and an AI ambition all at once.

## Why It Matters for the Diaspora

For non-resident Indians, the Jio IPO is likely to be the most talked-about Indian listing in years, and the temptation to participate \u2014 out of both financial interest and a sense of backing a marquee national champion \u2014 will be strong. But the very features that make this deal historic are the ones diaspora investors should study closely. The all-fresh-issue structure means the company, not its founders or early backers, is the one being recapitalised; the holding-company discount means a stake in Jio is not a clean, direct bet on its growth; and the wide valuation range means the listing price will matter enormously to the returns.

The sensible posture for NRIs is the same one the seasoned institutions are taking: interest tempered by patience. The IPO will test an Indian market that has cooled this year amid global jitters, and the listing timeline still depends on SEBI's review. For diaspora investors, this is a story worth following closely \u2014 but one to approach with the prospectus in hand rather than the headline alone."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["people strength training dumbbells gym", "woman resistance training weights", "older adult exercise resistance band"],
                          ["strength training dumbbells", "people lifting weights gym"], None),
    articles[1]["slug"]: (["olive oil pouring bottle food", "cooking oil kitchen frying", "olive oil nuts healthy fats"],
                          ["olive oil pouring", "cooking oil kitchen"], None),
    articles[2]["slug"]: (["Mukesh Ambani", "Reliance Jio store India", "Mumbai Bombay Stock Exchange building"],
                          ["Mumbai skyline business district", "stock exchange building india"], "Mukesh Ambani"),
}
img_captions = {
    articles[0]["slug"]: "A new 144,000-person study links regular strength training, alongside aerobic exercise, to a sharply lower risk of type 2 diabetes",
    articles[1]["slug"]: "A new review argues the type of fat \u2014 olive oil's oleic acid versus palm oil's palmitic acid \u2014 matters more than the amount for diabetes risk",
    articles[2]["slug"]: "Reliance Industries chairman Mukesh Ambani, whose Jio Platforms has filed for what would be India's largest-ever IPO",
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
