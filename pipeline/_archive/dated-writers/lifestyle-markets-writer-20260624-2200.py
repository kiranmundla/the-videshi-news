#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 22:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. 30-year, ~150,000-person study (3 US cohorts) finds strength training is
     linked to longevity — a 90-120 min/week "sweet spot" cut all-cause death
     ~13%, CVD death ~19%, neurological death ~27%; pairing strength with
     aerobic exercise cut risk ~45%. — lifestyle-health
  2. DPP/DPPOS: a 3-year diet-and-exercise lifestyle program in people with
     prediabetes was linked to a 21% lower risk of MULTIMORBIDITY (2+ chronic
     diseases) over 20+ years — benefit held even after excluding diabetes.
     (JAMA, 2026) — lifestyle-health
  3. India's bond-market opening: after scrapping capital-gains tax on foreign
     holdings of G-secs (June 5) and widening the FAR window, foreign money is
     trickling in (Fairfax's ~$1bn buy) and a Bloomberg Global Aggregate Index
     review looms mid-2026 — but high hedging costs and a weak rupee are the
     real test. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1010z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1010z.bin"):
            with open("/tmp/_img_dl1010z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1010z.bin")
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
# ARTICLE 1: Strength training & longevity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Lifting Weights Just an Hour or Two a Week Is Linked to a Longer Life, a 30-Year Study Finds",
    "subheadline": "Tracking nearly 150,000 people for three decades, researchers found a clear sweet spot \u2014 about 90 to 120 minutes of strength training a week \u2014 tied to lower death rates, with the biggest gains against heart disease and dementia when weights were paired with everyday aerobic activity.",
    "slug": "strength-training-longevity-150000-people-30-year-study-90-120-minutes-cardiovascular-dementia-diaspora-20260624-2200",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Strength training is still rare in many Indian and South Asian households \u2014 walking is the default, the gym is seen as vanity, and women in particular are often steered away from weights \u2014 yet this is precisely the community that carries an outsized burden of diabetes and heart disease that building muscle helps blunt.",
    "sources": json.dumps([
        {"name": "ScienceAlert / The Conversation \u2014 'Strength Training Is Linked to Longevity, 30-Year Study Finds' (Jack McNamara, University of East London)", "url": "https://www.sciencealert.com/strength-training-is-linked-to-longevity-30-year-study-finds"},
        {"name": "Inc. \u2014 'New Research Reveals How Exercise Variety Significantly Increases Longevity'", "url": "https://www.inc.com/jeff-haden/hope-to-live-a-longer-healthier-life-new-research-reveals-how-exercise-variety-significantly-increases-longevity.html"}
    ]),
    "body": """For decades, lifting weights has been filed under vanity \u2014 something you do to build biceps or look good on a beach, not something a doctor prescribes. A large new analysis spanning three decades suggests that framing has it backwards. Strength training, it turns out, may be one of the simplest things a person can do to live longer \u2014 and the amount required is far more modest than most people assume.

## A Thirty-Year Window

The study drew on three of the longest-running health investigations in the United States, which together followed nearly 150,000 nurses and other health professionals for up to 30 years. Every couple of years, participants reported how much time they spent on strength training and on aerobic exercise such as walking, cycling and swimming. Over the three decades, almost 36,000 of them died \u2014 a grim but statistically powerful dataset that let researchers trace how muscle-strengthening activity related to the risk of dying early.

What emerged was a clear sweet spot. People who did roughly 90 to 120 minutes of strength training a week \u2014 an hour and a half to two hours, spread across a few short sessions \u2014 had about a 13 percent lower risk of dying from any cause than those who did none at all.

## Where the Benefit Lands Hardest

The protective effect was not spread evenly. It was strongest against two of the biggest killers in the modern world. People hitting that strength-training range had a 19 percent lower risk of dying from cardiovascular disease \u2014 the umbrella term for heart attacks and strokes \u2014 and a striking 27 percent lower risk of dying from neurological conditions, mainly dementia.

Crucially, more was not better. Beyond about two hours of weightlifting a week, the risk stopped falling. This is a liberating finding for anyone intimidated by the idea of living in a gym: the longevity dividend appears to be banked early, with a couple of short weekly sessions, not with punishing daily marathons under the barbell.

The single best result came from combining strength work with aerobic activity. Doing the recommended 150 minutes a week of moderate aerobic exercise on its own was linked to a 26 to 43 percent lower risk of death. But pairing plenty of that aerobic movement with one to two hours of strength training pushed the risk down furthest of all \u2014 by around 45 percent. The two are not rivals competing for your time; they work best as partners.

## Why Muscle Matters So Much

Why would lifting weights ripple out into the heart and brain? The answer lies in what muscle actually does once it is built. Skeletal muscle is one of the body's most metabolically active tissues. After a meal, it is where most of the sugar in the blood gets sent \u2014 muscle mops up roughly 80 percent of circulating glucose, burning it or storing it rather than letting it linger or convert to fat. Keeping muscle strong therefore helps the body manage blood sugar and guards against type 2 diabetes, itself a major driver of heart disease and early death.

Muscle is also an organ that talks. When muscles contract, they release hormone-like messengers called myokines into the bloodstream that dampen the chronic, low-grade inflammation quietly underlying heart disease, diabetes and many cancers. Those same signals reach the liver, fat tissue, blood vessels, bone and even the brain. Regular resistance training can lower blood pressure and keep arteries flexible rather than stiff \u2014 and the improvements in blood sugar and blood vessels that protect the heart are also tied to a lower risk of dementia, which may explain that 27 percent drop in neurological deaths.

## The Caveats

This was observational research, so while it shows a powerful association, it cannot prove that lifting weights directly causes a longer life. People who strength-train may be healthier in other ways, though the researchers adjusted for many such factors, including diet, smoking and aerobic activity. Strength training was self-reported, and the study could not capture how hard people actually trained. Still, the consistency across nearly 150,000 people and 30 years gives the finding real weight.

## Why It Matters for the Diaspora

In many Indian and South Asian families, exercise means a walk \u2014 a morning loop around the park, a few rounds after dinner. Walking is wonderful, but it is almost entirely aerobic, and this research suggests it leaves a large part of the longevity equation untouched. Strength training remains culturally underused: the gym is often dismissed as vanity, weights are seen as the preserve of young men, and women in particular are frequently discouraged from lifting at all, sometimes well into the years when preserving muscle and bone matters most.

That is a costly gap for a community carrying an unusually high burden of type 2 diabetes and heart disease, often at lower body weights than other populations. The encouraging part of this study is how achievable the target is. Two short sessions a week working the major muscle groups \u2014 squats, a few resistance-band pulls, bodyweight movements at home, lifting whatever is heavy \u2014 alongside the daily walk already woven into family life appears to be enough. For older relatives, building and keeping muscle is also the strongest defence against the falls, fractures and frailty that steal independence. The message is not to abandon the evening walk, but to add a little resistance to it \u2014 and to retire the idea that lifting weights is only about how you look."""
})

# ============================================================
# ARTICLE 2: Lifestyle program & multimorbidity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Three Years of Diet and Exercise Paid Off for Two Decades \u2014 Far Beyond Diabetes, a New Study Finds",
    "subheadline": "People with prediabetes who followed an intensive diet-and-exercise program were 21% less likely to pile up multiple chronic diseases over the next 20-plus years \u2014 and the protection held even after diabetes itself was taken out of the equation.",
    "slug": "lifestyle-program-multimorbidity-21-percent-lower-risk-dpp-prediabetes-20-year-jama-study-diaspora-20260624-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians slide from prediabetes to diabetes faster and younger than most populations, and rarely stop there \u2014 heart disease, kidney trouble and more tend to stack up; this study shows a few years of disciplined diet and movement at the prediabetes stage can blunt that whole cascade decades later, not just the diabetes.",
    "sources": json.dumps([
        {"name": "ScienceAlert \u2014 'These Lifestyle Changes Help Lower Your Risk of Chronic Disease For Decades'", "url": "https://www.sciencealert.com/these-lifestyle-changes-help-lower-your-risk-of-chronic-disease-for-decades"},
        {"name": "JAMA (2026) \u2014 Salive et al., Diabetes Prevention Program Outcomes Study; via University of Colorado Anschutz Medical Campus", "url": "https://news.cuanschutz.edu/news-stories/lifestyle-change-program-linked-to-fewer-chronic-diseases-decades-later"}
    ]),
    "body": """Most of us think of a diet as a short, sharp project: a few disciplined months, a number hit on the scale, then back to normal life. A new study built on more than two decades of data offers a more hopeful idea \u2014 that a relatively brief stretch of healthy living can keep paying dividends long after it ends, and against a far wider range of illnesses than anyone set out to prevent.

## A Famous Experiment, Revisited

The research draws on one of the most influential studies in preventive medicine: the Diabetes Prevention Program and its long-running follow-up, the Diabetes Prevention Program Outcomes Study. These tracked thousands of people for more than twenty years to see how lifestyle changes shape health over a lifetime.

For this new analysis, researchers from institutions across the United States examined the records of 1,173 people who had originally enrolled with prediabetes \u2014 blood sugar high enough to signal danger but not yet diabetes. At the start, participants were split into three groups: one taking a daily placebo, one taking the diabetes drug metformin, and one placed on an intensive diet-and-exercise regimen aimed at losing at least 7 percent of body weight. Those routines ran for just three years.

## A Benefit That Outlived the Program

Then the researchers waited \u2014 and watched. Over more than two decades of follow-up, the group that had done the diet and exercise was significantly less likely to develop combinations of chronic diseases. Specifically, those assigned to the lifestyle program had a 21 percent lower risk of multimorbidity \u2014 defined as having two or more chronic conditions \u2014 than those who had taken the placebo.

The list of conditions the researchers tracked was long and sobering: hypertension, heart failure, coronary artery disease, cardiac arrhythmias, high cholesterol, stroke, arthritis, asthma, cancer, chronic kidney disease, chronic obstructive pulmonary disease, dementia including Alzheimer's, depression, osteoporosis and diabetes. The team adjusted for age, sex, race and ethnicity, alcohol consumption and body mass index, which strengthens confidence in the link.

The most telling detail: even after the researchers removed diabetes \u2014 the disease the original program was designed to prevent \u2014 from the tally, the overall risk of accumulating chronic diseases remained lower in the lifestyle group. The benefit, in other words, was not just about dodging diabetes. It was about aging with fewer illnesses, full stop.

By contrast, the metformin group showed little difference from the placebo group on this measure, suggesting the broad, durable protection came specifically from the diet-and-exercise package rather than from medication alone.

## What It Does and Doesn't Prove

"Preventing diabetes is critically important, but preventing the accumulation of multiple chronic diseases as people age may have even broader implications for quality of life, independence, and healthcare costs," said Marcel Salive of the National Institute on Aging. Epidemiologist Dana Dabelea of the Colorado School of Public Health added that the findings "highlight the long-term value of healthy eating, regular physical activity, and weight management."

The usual caution applies: this is observational analysis, so it can show a strong association but cannot prove cause and effect beyond doubt. And there is a sobering footnote. Across the entire study population \u2014 including those in the lifestyle group \u2014 85 percent eventually developed at least two chronic conditions. Healthy living delays and reduces the burden of disease in aging; it does not abolish it. Longer life, the data quietly reminds us, is not automatically healthier life.

## Why It Matters for the Diaspora

For South Asians, this study lands on a fault line in the community's health. People of Indian origin develop type 2 diabetes earlier, at lower body weights, and progress from prediabetes to full diabetes faster than most other populations \u2014 and the disease rarely travels alone. It tends to drag heart disease, kidney problems, high blood pressure and more along with it, exactly the kind of multimorbidity this research is about.

That makes the prediabetes stage a uniquely valuable window for the diaspora, and one too often waved away as "borderline sugar" until it tips over. This study's encouraging message is that the intervention does not have to be lifelong perfection \u2014 a sustained few years of disciplined eating and movement at that borderline moment was linked to fewer stacked-up diseases decades on. The tools are familiar and culturally within reach: shifting from refined carbohydrates and fried snacks toward vegetables, pulses and whole grains, building in regular movement, and treating a modest 5-to-7 percent weight loss as a serious medical goal rather than a cosmetic one. For families where a prediabetes result is common and often shrugged off, the research reframes that result as an opportunity \u2014 a chance to bend the whole arc of later-life health, not just one number on a lab report."""
})

# ============================================================
# ARTICLE 3: India bond-market opening / foreign inflows (markets-finance)
# ============================================================
articles.append({
    "headline": "India Threw Open Its Bond Market to the World. The World Is Still Deciding Whether to Walk In.",
    "subheadline": "After scrapping the tax on foreign holdings of government bonds and widening access, India has lured early buyers \u2014 including a rare $1 billion bet by Canada's Fairfax \u2014 and is angling for a coveted Bloomberg index seat. But a weak rupee and steep hedging costs may yet keep the big money cautious.",
    "slug": "india-bond-market-opening-foreign-inflows-capital-gains-tax-far-bloomberg-index-fairfax-nri-investor-20260624-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "India's push to pull global money into its government bonds runs on the same engine the diaspora is being courted with \u2014 dollar deposits, GIFT City, index inclusion \u2014 and the outcome will shape the yields, the rupee and the investment options NRIs see when they decide how much of their savings to send home.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'Canada's Fairfax buys nearly $1 billion of Indian bonds in rare move, sources say'", "url": "https://www.reuters.com/markets/asia/canadas-fairfax-buys-nearly-1-billion-indian-bonds-rare-move-sources-say-2026-06-23/"},
        {"name": "Reuters \u2014 'India bond-tax moves to catalyse foreign debt inflows, bolster bid for global index inclusion'", "url": "https://www.reuters.com/world/india/india-bond-tax-moves-catalyse-foreign-debt-inflows-bolster-bid-global-index-2026-06-10/"},
        {"name": "Mint \u2014 'India's Bloomberg aggregate index entry hinges on demand, rupee'", "url": "https://www.livemint.com/market/stock-market-news/indias-bloomberg-aggregate-index-entry-hinges-on-demand-rupee.html"}
    ]),
    "body": """India has spent years trying to convince the world's biggest investors to lend it money. This month it removed one of the largest obstacles \u2014 and is now learning that opening the door is not the same as filling the room.

## The Tax That Stood in the Way

On June 5, India scrapped the capital-gains tax that foreign investors had to pay on their holdings of Indian government bonds. It sounds technical, but the change strikes at a long-standing irritant. For global funds, the prospect of an Indian tax bill on top of currency risk and paperwork was a reason to look elsewhere. Removing it makes Indian government securities more attractive on a relative basis and, crucially, simpler to own.

The early response was tangible. In the first weeks after the tax was removed, Indian bonds drew about $2 billion from overseas investors \u2014 more than the $1.6 billion they had attracted in the entire first five months of the year. Alongside the tax change, the Reserve Bank of India widened its Fully Accessible Route, the channel that lets foreigners buy designated government bonds without quantitative limits, to include all new issues of 15-, 30- and 40-year debt. The message to global capital was unambiguous: India wants you in, across the whole curve.

## A Rare Vote of Confidence

The most eye-catching endorsement came last week, when Fairfax, the Canadian investment group run by India-born financier Prem Watsa, bought nearly $1 billion of Indian government debt in a single move \u2014 a rare purchase for a firm that is not a regular player in the market. Sources said the buy was partly to bring capital into the country ahead of a possible deal involving government-owned IDBI Bank, and that India's new tax exemption was what made the transaction viable in the first place. Fairfax concentrated its buying at the shorter end of the curve, snapping up the bulk through a recently auctioned 2029 bond.

It was, in miniature, exactly the kind of flow India is hoping to unlock at scale: large, long-term money drawn in by a friendlier rulebook.

## The Bigger Prize \u2014 and the Catch

The real target is bigger than any single buyer. India is campaigning for inclusion in the Bloomberg Global Aggregate Index, one of the benchmarks that the world's index-tracking funds are obliged to follow. Getting in would bring not one-off purchases but durable, predictable inflows, much as India's earlier entry into JPMorgan's emerging-market debt index did. A Bloomberg committee is reviewing the question, with a major update expected around the middle of 2026, and India's finance ministry has been lobbying hard for a yes.

But the obstacle has quietly shifted. The operational complaints \u2014 access, taxes, paperwork \u2014 have largely been addressed. What remains is colder and harder to fix: whether global fund managers actually see enough value in Indian bonds to want them. The math is unforgiving. Once a foreign investor fully hedges the currency risk, the yield on an Indian government bond can shrink to under 4 percent \u2014 barely competitive with safer US Treasuries. "Whether you hedge or don't hedge, it's a losing proposition," one senior bank economist put it bluntly, questioning whether managers would even propose India for inclusion this year unless yields rise. Elevated hedging costs and persistent worries about the rupee's trajectory have dulled the appeal that the tax cut was meant to sharpen.

## A Currency Under Pressure

That rupee anxiety is not abstract. The currency has been hovering near 94.85 to the dollar, pressured by a resurgent greenback that has climbed to a 13-month high on rising bets that the US Federal Reserve will raise interest rates. A weaker, more volatile rupee raises the cost of hedging and eats into the returns a foreign bondholder ultimately takes home. India's central bank has been intervening to curb disorderly moves and rolling out measures to attract dollar inflows, and RBI Governor Sanjay Malhotra has called talk of an Indian rate hike "premature." The result is a delicate balancing act: India is simultaneously trying to defend its currency and make its debt appealing to the very investors that currency weakness scares away.

## Why It Matters for the Diaspora

For non-resident Indians, this is not a distant macro story \u2014 it runs on the same machinery now being used to court the diaspora directly. The push to draw global money into government bonds, the concessional dollar-deposit schemes, the build-out of GIFT City and the chase for index inclusion are all parts of one effort to pull foreign capital toward India and steady the rupee. The outcome shapes the things NRIs actually feel: the yields available on Indian fixed income, the strength of the rupee against the dollars and pounds they earn, and the breadth of safe, accessible ways to invest back home.

There is a useful signal in here too. The same hedging math that gives global funds pause \u2014 strong returns in rupee terms can evaporate once currency risk is priced in \u2014 is exactly what an NRI weighing an Indian bond or deposit should run on their own savings. India's reforms have genuinely lowered the barriers to investing; whether the rewards justify the currency risk is now the question every foreign investor, diaspora included, has to answer for themselves. Watching whether the big institutional money commits \u2014 and whether that Bloomberg seat finally arrives \u2014 is one of the clearest tells of how much confidence the world, and the diaspora, should place in lending to India."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["dumbbell strength training gym", "person lifting weights barbell", "weight training fitness exercise"],
                          ["strength training dumbbell gym", "person lifting weights"], None),
    articles[1]["slug"]: (["healthy vegetables diet food", "person walking exercise outdoor health", "fresh vegetables healthy eating"],
                          ["healthy food vegetables diet", "walking exercise outdoor"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee currency banknotes", "Mumbai financial district skyline"],
                          ["indian rupee banknotes currency", "Mumbai skyline financial"], None),
}
img_captions = {
    articles[0]["slug"]: "A 30-year study of nearly 150,000 people links one to two hours of weekly strength training to a longer life",
    articles[1]["slug"]: "A new analysis finds a few years of diet and exercise can reduce chronic disease risk for decades",
    articles[2]["slug"]: "India's bond-market reforms aim to lure global investors as a weak rupee tests their appetite",
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
