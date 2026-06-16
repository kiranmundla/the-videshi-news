#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-16 06:00 UTC batch.
Topics:
  1. Sleep timing / social jet lag + diabetes risk, diet quality buffer (NHANES) — lifestyle-health
  2. Sugar-free / zero-sugar diets backfire on gut + metabolism (ENDO 2026, Dasman) — lifestyle-health
  3. FCNR(B) deposit rate war: 6-7.1% dollar rates for NRIs after RBI June 5 measures — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl6.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl6.bin"):
            with open("/tmp/_img_dl6.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl6.bin")
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
# ARTICLE 1: Sleep timing / social jet lag + diabetes (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It Is Not Just How Long You Sleep \u2014 It Is When. A 7,270-Person Study Ties Late Nights to Diabetes.",
    "subheadline": "Analysing a nationally representative US health survey, researchers found that night owls and people whose weekend sleep drifts more than half an hour from their weekday schedule carried a roughly 45 per cent higher odds of diabetes. The striking part: a high-quality diet substantially blunted the damage from that weekend drift \u2014 a finding with direct force for a diaspora that eats late, works across time zones, and prides itself on home cooking.",
    "slug": "sleep-timing-social-jet-lag-diabetes-risk-diet-quality-buffer-nhanes-diaspora-20260616",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian households are famous for late dinners, midnight family calls across continents and weekend schedules that swing wildly from weekday ones \u2014 the exact 'social jet lag' this study links to diabetes \u2014 yet the same research shows the diaspora's home-cooked, vegetable-and-pulse-heavy diet can be a genuine shield, making this a rare piece of actionable, culturally specific science.",
    "sources": json.dumps([
        {"name": "Journal of the Academy of Nutrition and Dietetics (Associations of Sleep Timing and Regularity With Diabetes and Interactions With Diet Quality Among Adults)", "url": "https://pubmed.ncbi.nlm.nih.gov/41207557/"},
        {"name": "DOI: 10.1016/j.jand.2025.156228", "url": "https://doi.org/10.1016/j.jand.2025.156228"},
        {"name": "National Health and Nutrition Examination Survey (NHANES), CDC", "url": "https://www.cdc.gov/nchs/nhanes/index.htm"}
    ]),
    "body": """For years the health message about sleep has been simple and one-dimensional: get your seven to eight hours. A new analysis of more than 7,000 American adults complicates that tidy advice in a way the South Asian diaspora should sit up and read. It is not only how long you sleep that shapes your risk of diabetes. It is when you sleep, and how erratically your schedule swings from one day to the next.

## What the Study Looked At

Researchers drew on the National Health and Nutrition Examination Survey, the gold-standard health snapshot of the US population, examining 7,270 adults aged 20 and older who answered detailed questions about their sleep and completed validated 24-hour dietary recalls. Diabetes was not left to self-report alone; it was defined rigorously, using a prior physician diagnosis, an HbA1c of 6.5 per cent or higher, a fasting glucose of 126 mg/dL or higher, or the use of insulin or oral diabetes medication. Of the group, 1,494 people \u2014 about 15 per cent \u2014 met that bar.

The investigators then asked two questions that the standard "sleep eight hours" guidance ignores entirely. First, does your chronotype \u2014 whether you are naturally an early bird or a night owl \u2014 matter? Second, does "social jet lag," the gap between your sleep timing on work days and free days, carry its own risk?

## The Findings

The answers were unambiguous. People with a late chronotype \u2014 the committed night owls \u2014 had 45 per cent higher odds of diabetes than earlier sleepers (odds ratio 1.45). And those whose sleep timing drifted by more than half an hour between weekdays and weekends \u2014 a very modest amount of social jet lag \u2014 had 44 per cent higher odds (odds ratio 1.44). Both associations survived a strict statistical correction for multiple comparisons, meaning they were not statistical flukes.

In plain terms: staying up late by nature, and letting your sleep schedule lurch around from day to day, each travelled with a meaningfully higher chance of carrying diabetes. The body, it seems, keeps a clock, and routinely overriding it appears to register in blood sugar.

## The Part That Should Reassure the Diaspora

Here is where the study turns from alarming to genuinely useful. The researchers tested whether diet quality interacted with these sleep patterns \u2014 and it did. Among people with social jet lag greater than half an hour, those eating a medium-quality diet had 38 per cent lower odds of diabetes, and those eating a high-quality diet 37 per cent lower odds, compared with people eating a low-quality diet (odds ratios of 0.62 and 0.63). The statistical interaction was significant.

Put bluntly: a good diet substantially buffered the diabetes risk that came with an irregular sleep schedule. The damage from social jet lag was not fixed and fated. It bent considerably in the presence of better food.

## Why This Lands on the Diaspora Specifically

Few communities are as structurally prone to social jet lag as the global Indian diaspora. Dinners routinely run past 9 or 10 at night. Family WhatsApp calls and festival greetings are timed to India, eight to thirteen hours out of sync with American and British clocks, pulling people awake at hours their bodies would rather sleep. Tech workers \u2014 a huge slice of the NRI population \u2014 take late standups with Bangalore and let weekend schedules slide far from the weekday grind. The result is a community quietly marinating in exactly the chronobiological risk this study flags, on top of an already elevated baseline susceptibility to diabetes.

But the same community holds the buffer in its own kitchen. The traditional Indian plate \u2014 dense in vegetables, dals, whole grains and home cooking, light on the ultra-processed packaged food that drags diet scores down \u2014 is precisely the kind of high-quality diet that softened the risk in this analysis. The diaspora that cannot easily fix its time-zone-scrambled sleep can still pull the most powerful protective lever it has.

## What To Actually Do

The practical takeaways are concrete. Anchor your wake time, even on weekends, keeping the weekday-to-weekend drift under that half-hour threshold the study identified; consistency appears to matter more than the occasional perfect night. Night owls cannot rewrite their biology overnight, but nudging dinner and screens earlier shifts the whole schedule in the protective direction. And for anyone whose work or family life makes irregular sleep unavoidable, the message is not despair but emphasis: the quality of what is on your plate is not a side issue. In this data, it was strong enough to offset much of the harm.

The old advice to simply sleep more was never wrong. It was just incomplete. When you sleep, how steadily you sleep, and what you eat around it turn out to be three dials on the same machine \u2014 and the diaspora controls at least one of them entirely."""
})

# ============================================================
# ARTICLE 2: Sugar-free diets backfire on gut + metabolism (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cutting Sugar to Zero Backfired. A New Study Found Sugar-Free Diets Disrupted the Gut and Triggered Fatty Liver.",
    "subheadline": "Presented at the Endocrine Society's ENDO 2026 meeting, a 16-week study found that mice on a sucrose-free low-fat diet developed impaired glucose control, insulin resistance, gut microbial imbalance, intestinal inflammation and fatty liver changes \u2014 despite no difference in body weight. The lesson for a diaspora bombarded with 'quit sugar' wellness advice: the goal is balance, not elimination.",
    "slug": "sugar-free-zero-sucrose-diet-gut-microbiome-fatty-liver-insulin-resistance-endo-2026-diaspora-20260616",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The 'no sugar challenge' has swept diaspora wellness circles \u2014 WhatsApp diet groups, Indian fitness influencers, Navratri and Ekadashi-adjacent cleanses \u2014 yet this research suggests that for a population already prone to insulin resistance and lean fatty liver, swinging to total sugar elimination from a low-fat diet may do real metabolic harm rather than good.",
    "sources": json.dumps([
        {"name": "Endocrine Society (Sugar-free diets may disrupt gut microbiome \u2014 ENDO 2026)", "url": "https://www.endocrine.org/news-and-advocacy/news-room"},
        {"name": "News-Medical (Eliminating dietary sugar may disrupt gut health and promote inflammation)", "url": "https://www.news-medical.net/"},
        {"name": "Dasman Diabetes Institute, Kuwait", "url": "https://www.dasmaninstitute.org/"}
    ]),
    "body": """If there is one piece of dietary advice that has achieved near-religious status in diaspora wellness circles, it is this: cut the sugar. Quit-sugar challenges circulate on family WhatsApp groups. Indian fitness influencers preach total elimination. Festival fasts and cleanses lean on the same instinct \u2014 that sugar is poison and the less of it, the better. A study presented this month at ENDO 2026, the Endocrine Society's annual meeting in Chicago, suggests that for a low-fat diet, swinging all the way to zero may do the opposite of what the wellness gurus promise.

## The Experiment

Researchers at the Dasman Diabetes Institute in Kuwait City compared two groups of mice over 16 weeks. One group ate a low-fat diet containing sucrose \u2014 ordinary table sugar \u2014 in normal amounts. The other ate a low-fat diet with the sucrose stripped out entirely. The animals were then assessed across the metabolic spectrum: glucose tolerance, insulin sensitivity, circulating metabolic hormones, the composition of the gut microbiome, and inflammation in both the colon and the liver.

On paper, the sugar-free group should have looked healthier. They did not.

## What Went Wrong

The mice on the sucrose-free diet developed impaired glucose control, insulin resistance, a disturbed and imbalanced gut microbiome, intestinal inflammation and fatty-liver changes. Crucially, they showed no significant difference in body weight compared with the sugar-eating control mice. The harm was metabolic and microbial, not a matter of pounds gained or lost \u2014 which is exactly the kind of hidden damage that conventional weight-focused thinking misses.

"Completely removing sucrose from a low-fat diet may unexpectedly disrupt gut health and promote inflammation and metabolic dysfunction, highlighting that balanced nutrition is more important than simply eliminating sugar," said Rasheed Ahmad, principal scientist and head of the Immunology and Microbiology Department at the institute. Until this work, he noted, the consequences of stripping sugar out of a low-fat diet were essentially unstudied \u2014 the assumption that less is always better had never been properly tested.

## The Nuance That Matters

This is emphatically not a licence to reach for the mithai box or pour another sugary chai. The distinction the study draws is between two very different things: the naturally occurring sugars bound up in whole foods, and the added sugars dumped into processed products. Sugar exists naturally in fruits, vegetables, grains and dairy \u2014 foods that also carry fibre, vitamins, antioxidants and protein, all of which slow digestion and deliver a steadier release of energy rather than a spike-and-crash. The real metabolic villains are the added sugars in sugary drinks, packaged sweets and baked goods, which drive up blood pressure, fuel chronic inflammation and, over time, raise the risk of type 2 diabetes and heart disease.

The study's message is about balance and the microbiome, not indulgence. A healthy gut appears to need a baseline of dietary carbohydrate to maintain its microbial balance and immune homeostasis; starving it entirely, at least on a low-fat backdrop, backfired.

## Why the Diaspora Should Pay Close Attention

South Asians carry a documented predisposition to insulin resistance and to fatty liver disease \u2014 often at normal body weights, the so-called lean fatty-liver phenotype The Videshi has reported on before. That makes the diaspora a population where the wrong dietary swing can have outsized consequences. When a community already prone to these exact problems embraces extreme, all-or-nothing sugar elimination on the advice of an influencer rather than a physician, this research suggests the cure could aggravate the disease.

There is also a cultural trap here. The diaspora diet is rich in legitimate carbohydrate \u2014 rice, rotis, millets, fruit, dairy-based sweets at festivals \u2014 and the fashionable response has been to demonise all of it together. This study underscores how crude that framing is. The whole grain and the dal are not the enemy. The mithai-at-every-occasion and the daily soft drink are.

## The Practical Bottom Line

The honest, evidence-based path runs between the extremes. Cut added sugars aggressively \u2014 the sodas, the packaged biscuits, the syrup-soaked sweets eaten daily rather than ceremonially. But do not confuse that with eliminating carbohydrate or natural sugar altogether, especially on a low-fat diet, because the gut and the liver may pay a price that the bathroom scale never reveals.

For a diaspora that loves a dramatic cleanse, the science keeps landing on an unglamorous truth: balance beats elimination, and the microbiome rewards moderation over zeal."""
})

# ============================================================
# ARTICLE 3: FCNR(B) deposit rate war for NRIs (markets-finance)
# ============================================================
articles.append({
    "headline": "Indian Banks Just Doubled Dollar Deposit Rates for NRIs to 7%. The RBI Engineered It \u2014 and It Will Not Last.",
    "subheadline": "After the RBI agreed on June 5 to absorb the full hedging cost on fresh three-to-five-year FCNR(B) dollar deposits, banks have lifted rates from around 3 per cent to between 5.25 and 7.1 per cent. With no currency risk, these are among the most attractive dollar-denominated returns NRIs have seen in years \u2014 but the concessional window slams shut on September 30, and the offer is dollar-only.",
    "slug": "fcnr-b-deposit-rates-7-percent-nri-rbi-hedging-cost-september-window-dollar-deposits-20260616",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "FCNR(B) deposits are an NRI-only instrument, and the sudden jump to 6-7.1 per cent on a dollar deposit with zero currency risk \u2014 deliberately engineered by the RBI to pull diaspora dollars into India \u2014 is one of the most consequential, time-limited financial decisions facing NRI savers right now, with a hard September 30 deadline.",
    "sources": json.dumps([
        {"name": "Mint (Why FCNR deposits at 6-7.1% rates are attractive for NRIs)", "url": "https://www.livemint.com/"},
        {"name": "Reuters (Some lenders hike rates on FX deposits for non-resident Indians)", "url": "https://www.reuters.com/world/india/"},
        {"name": "The Hindu BusinessLine (FCNR (B) deposits: Banks may face a tricky situation)", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Outlook Money (RBI Reviews FCNR(B) Swap Scheme)", "url": "https://www.outlookmoney.com/"}
    ]),
    "body": """For most of the past decade, the FCNR(B) deposit \u2014 a dollar-denominated fixed deposit available only to non-resident Indians \u2014 was a financial afterthought. Rates hovered around 3 per cent, dull enough that inflows into the category collapsed to under a billion dollars in the last financial year. Then, almost overnight, the numbers changed. Banks are now offering between 5.25 and 7.1 per cent on these dollar deposits, and for NRIs weighing where to park their savings, that shift is too large to ignore.

## What the RBI Did

The catalyst was a deliberate piece of policy engineering. On June 5, as part of a broader package to defend a rupee that had slid to record lows near 97 per dollar, the Reserve Bank of India announced that it would bear the full hedging cost on fresh three-to-five-year FCNR(B) dollar deposits that banks mobilise through September 30, 2026. It also exempted these incremental deposits from the cash reserve ratio and statutory liquidity ratio \u2014 the slices of every deposit that banks normally must park unproductively with the regulator.

The economics of that are powerful. Hedging the currency risk on a dollar deposit used to eat into what banks could offer NRIs; with the RBI now absorbing that cost and waiving the reserve requirements, lenders suddenly enjoy a spread advantage of roughly 60 to 65 basis points over ordinary domestic deposits. They have passed much of it on. "Recent regulatory measures have meaningfully optimised hedging economics for banks, enabling us to offer significantly higher rates to NRI customers," said Uttam Tibrewal, deputy CEO of AU Small Finance Bank.

## The Rates on Offer

The response was swift and competitive. HDFC Bank, India's largest private lender, raised rates by 235 to 265 basis points to 6 per cent on three-to-five-year deposits. State Bank of India lifted rates by as much as 300 basis points, offering 5.25 to 6 per cent depending on deposit size and tenure. AU Small Finance Bank went to 7.1 per cent on three-year money, and Yes Bank set 7 to 7.1 per cent across three-to-five-year tenures.

To appreciate how unusual this is, consider what it is not. This is not a high rupee rate that quietly erodes when the currency falls \u2014 the trap that has historically caught NRE rupee depositors. It is a dollar rate, on a dollar deposit, with the currency risk borne by the RBI. An NRI earns the interest in dollars and is repaid in dollars. For diaspora savers who have watched the rupee lose nearly 6 per cent this year alone, a 7 per cent return with no exchange-rate exposure is a genuinely rare proposition.

## The Catches

Three caveats deserve emphasis before anyone rushes in. First, the concessional window is explicitly temporary. The RBI's hedging-cost support applies to deposits mobilised up to September 30, 2026. Banks are offering these rates for a limited period precisely because the subsidy behind them expires; the window to lock in is months, not years.

Second, the offer is dollar-only. Banks accept FCNR(B) deposits in sterling, euros, Australian, Canadian and Singapore dollars too, but the RBI's swap facility currently covers only the US dollar \u2014 so rates on other-currency deposits have not moved. NRIs holding savings in pounds or euros do not get this deal unless they convert to dollars and take on that conversion risk.

Third, there is a subtler trap that bankers themselves have flagged. The lure of these higher rates may tempt NRIs with existing FCNR(B) deposits to prematurely break them and roll the proceeds into fresh deposits. The Hindu BusinessLine reported that doing so means surrendering interest on the period the old deposit has already run, and may trigger penalties \u2014 so the headline rate can be partly clawed back by the cost of switching. The maths favours new money far more cleanly than it favours churning old deposits.

## What It Means for the Diaspora

For an NRI sitting on idle dollars \u2014 in a US savings account earning little, or waiting to be deployed \u2014 a three-to-five-year FCNR(B) deposit at 6 to 7.1 per cent, with the currency risk neutralised and the deadline looming, is one of the more compelling fixed-income options available right now. It is worth comparing offers across banks, since the spread between SBI's 5.25 per cent floor and AU's 7.1 per cent is substantial, and reading the premature-withdrawal terms before committing.

The broader context is that India wants this money. The whole apparatus \u2014 the hedging subsidy, the reserve exemptions, the RBI deputy governor personally urging bank chiefs to mobilise overseas funds \u2014 exists to pull diaspora dollars in and steady the rupee. Economists estimate the measures could attract $35 to $70 billion. For once, the NRI saver and the Indian central bank want the same thing, and the diaspora is being paid handsomely to oblige. The only catch is the clock."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["person sleeping bed night", "alarm clock bedroom sleep", "woman sleeping insomnia"],
                          ["person sleeping in bed at night", "alarm clock bedside morning"]),
    articles[1]["slug"]: (["sugar cubes spoon", "white sugar bowl", "refined sugar food"],
                          ["sugar cubes on table", "white sugar in bowl spoon"]),
    articles[2]["slug"]: (["US dollar banknotes currency", "indian rupee dollar exchange", "bank deposit money savings"],
                          ["us dollar bills cash stack", "money savings bank deposit dollars"]),
}
img_captions = {
    articles[0]["slug"]: "A person asleep at night; new research links late and irregular sleep timing to higher diabetes risk",
    articles[1]["slug"]: "Refined sugar, which a new study suggests should be moderated rather than eliminated entirely",
    articles[2]["slug"]: "US dollar banknotes; Indian banks are offering NRIs up to 7.1 per cent on dollar FCNR(B) deposits",
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
