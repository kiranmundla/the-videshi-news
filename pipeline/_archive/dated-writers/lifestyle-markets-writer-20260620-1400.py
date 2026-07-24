#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 14:00 UTC batch.
Topics:
  1. ENDO 2026 (T4DM sub-study, Adelaide; Gary Wittert): testosterone alone is no
     substitute for lifestyle change in older men with central obesity & prediabetes — lifestyle-health
  2. ENDO 2026 (LIFE-MILCH, Univ. of Parma; Maria Elisabeth Street): endocrine-disrupting
     chemicals (BPA, phthalates, parabens, pesticides) found in breast milk & infant urine — lifestyle-health
  3. RBI April balance-of-payments: BoP swings to deficit on FPI outflows, but worker
     remittances jump to $16bn and current account turns to surplus — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0620d.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0620d.bin"):
            with open("/tmp/_img_dl0620d.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0620d.bin")
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
# ARTICLE 1: Testosterone no substitute for lifestyle change (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Testosterone Alone Won't Fix Diabetes Risk in Older Men, a New Follow-Up Finds — the Lifestyle Still Has to Change",
    "subheadline": "A long-running Australian trial found that testosterone can improve body composition, blood sugar and libido in older men with belly fat and prediabetes \u2014 but only when paired with diet and exercise, not as a shortcut around them.",
    "slug": "testosterone-not-replacement-lifestyle-change-older-men-prediabetes-t4dm-substudy-endo-2026-diaspora-20260620-1400",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian men carry an outsized burden of type 2 diabetes and abdominal obesity, often at lower body weights than other groups \u2014 and as testosterone therapy is marketed ever more aggressively to middle-aged NRIs, this study is a timely reminder that there is no hormonal shortcut around diet and exercise.",
    "sources": json.dumps([
        {"name": "Endocrine Society \u2014 Testosterone alone is not a replacement for lifestyle changes in older men at risk of T2D (ENDO 2026; Gary Wittert, T4DM)", "url": "https://www.endocrine.org/news-and-advocacy/news-room/2026/"},
        {"name": "Medical Dialogues \u2014 Testosterone alone not replacement for lifestyle changes in older men at risk of T2D, suggests study", "url": "https://medicaldialogues.in/"}
    ]),
    "body": """Testosterone has become one of the most talked-about \u2014 and most heavily marketed \u2014 hormones of middle age, sold as a fix for everything from flagging energy to thickening waistlines. But new research presented at the Endocrine Society's annual meeting delivers a sober caveat: in older men at high risk of diabetes, testosterone helps only when it rides on the back of real lifestyle change. It is not a substitute for one.

## What the Study Looked At

The findings come from a sub-study of the T4DM trial \u2014 Testosterone for the Prevention of Type 2 Diabetes Mellitus \u2014 a randomised, double-blind, placebo-controlled study first published in 2021. The original trial enrolled 1,007 men aged 50 to 74 who were either at high risk of developing type 2 diabetes or had been newly diagnosed with it. Every participant was enrolled in a lifestyle programme; on top of that, half received testosterone injections and half a placebo.

The earlier results were striking: testosterone plus the lifestyle programme cut the likelihood of diabetes being present after two years by about 40 percent. The new analysis, led by Gary Wittert of Adelaide University and the Royal Adelaide Hospital, followed a subset of 121 of those men for an additional two years to see what happened once the structured trial wound down.

## The Key Finding

\"Testosterone treatment alone is not a replacement for lifestyle intervention, weight management or standard diabetes prevention in older men with central obesity and prediabetes or early T2D,\" Wittert said.

In other words, the hormone delivered genuine benefits \u2014 improvements in body composition, glucose metabolism and sexual desire \u2014 but those gains depended on the men staying engaged with the diet and exercise programme underneath. Testosterone was an amplifier of healthy behaviour, not a replacement for it. Strip away the lifestyle effort, and the chemistry alone could not carry the load.

Type 2 diabetes is a vast and growing problem: more than 40 million Americans have been diagnosed, and over 115 million more are estimated to have prediabetes. The disease is most common in adults over 45 and is tightly bound to abdominal obesity and the loss of muscle mass and strength that creeps in with age. Catching it early, and treating it, sharply reduces the risk of complications down the line.

## A Word of Caution on the Testosterone Boom

The timing is notable. American health authorities have recently moved to loosen restrictions on testosterone replacement therapy, proposing to lift limits on its use in men with age-related low testosterone after newer data suggested the heart risks may be smaller than once feared. That regulatory shift, combined with relentless direct-to-consumer marketing of \"low-T\" clinics, means more middle-aged men than ever are being offered the hormone.

This study is a useful counterweight to the hype. Testosterone is not a weight-loss drug, and it is not a diabetes cure. The men who benefited were already doing the hard work of changing how they ate and moved; the hormone helped them get more out of that effort. For anyone hoping a prescription will let them skip the gym and the kitchen, the message is blunt: it won't.

## Why It Matters for the Diaspora

For Indian and wider South Asian men, the findings land close to home. The community is genetically predisposed to type 2 diabetes and to carrying fat around the abdomen \u2014 the very \"central obesity\" the study focused on \u2014 often at body weights that look unremarkable on the scale. Diabetes frequently strikes South Asians a decade earlier than it does many other populations.

As wellness culture and hormone clinics court NRIs in the United States, Britain, Canada and the Gulf, the temptation to reach for a testosterone shot as a quick fix is real. This research reframes the conversation. The foundation of preventing diabetes remains what it has always been: losing the weight around the middle, building muscle through resistance work, and eating in a way that keeps blood sugar in check. Testosterone, for the men for whom it is appropriate, may help \u2014 but only as a partner to that work, never as a stand-in for it."""
})

# ============================================================
# ARTICLE 2: Endocrine-disrupting chemicals in breast milk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Hormone-Disrupting Chemicals Are Turning Up in Breast Milk and Babies' Urine, a New Study Finds",
    "subheadline": "Researchers who tested 336 mother-infant pairs found BPA, phthalates, parabens and pesticides in breast milk and in infants' bodies through their first six months \u2014 a reminder that everyday products carry hidden chemical passengers.",
    "slug": "endocrine-disrupting-chemicals-bpa-phthalates-breast-milk-infant-urine-life-milch-endo-2026-diaspora-20260620-1400",
    "category": "lifestyle-health",
    "vertical": "family-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Young diaspora families juggling plastic food containers, imported cosmetics and personal-care products will want to read this carefully \u2014 the chemicals the study tracked are common in exactly the everyday items that fill NRI households, and the researchers stress this is a call to reduce exposure, not to stop breastfeeding.",
    "sources": json.dumps([
        {"name": "Endocrine Society \u2014 EDCs found in breast milk and infant urine up to age 6 months (ENDO 2026; Maria Elisabeth Street, LIFE-MILCH project)", "url": "https://www.endocrine.org/news-and-advocacy/news-room/2026/street-press-release-endo-2026"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (June 2026)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """Breast milk is, by near-universal agreement, the best food a newborn can have. But new research presented at the Endocrine Society's annual meeting carries an uncomfortable finding: that milk, and the babies who drink it, can also carry traces of the hormone-disrupting chemicals woven into modern life.

## What the Researchers Did

A team led by Maria Elisabeth Street of the University of Parma in Italy drew on data from 336 mother-infant pairs enrolled in a project called LIFE-MILCH. They collected breast milk and infant urine samples at one month, three months and six months after birth, then screened them for more than 50 different chemicals \u2014 a roster that included bisphenols such as BPA, phthalates, parabens, polycyclic aromatic hydrocarbons and various pesticides.

These substances are known as endocrine-disrupting chemicals, or EDCs, because they interfere with the body's hormone signalling. \"Breast milk is the optimal nutritional source for any child and must be protected as it is a vehicle of environmental contaminants,\" Street said. \"Infancy represents a critical window of exposure since effects are magnified at this age, with damage becoming evident after many years.\"

## What They Found

The chemicals were not rare exceptions; many were the rule. BPA \u2014 the bisphenol long associated with plastics and food-can linings \u2014 was found in roughly half of breast milk samples at one month and again at six months. Nearly a third of infants had BPA in their urine soon after birth, and that figure climbed to more than two-thirds by six months of age.

Phthalates, the plasticisers that make materials soft and flexible, were the most pervasive of all: dibutyl phthalate turned up in more than 90 percent of breast milk samples at one month. Its presence in infant urine rose sharply over time, from about 30 percent at birth to nearly 80 percent by six months. Parabens, used as preservatives in cosmetics and personal-care products, were common in breast milk and increased in infant urine across the study. A pesticide called glufosinate and several other compounds also showed up repeatedly.

The pattern in many cases was the same: levels in the babies' urine climbed as the months passed, suggesting steady, accumulating exposure during a uniquely vulnerable stage of development.

## Why This Is Worrying \u2014 and What It Does Not Mean

EDC exposure has been linked in prior research to neurodevelopmental problems, disrupted hormonal activity at birth, and altered growth, weight and obesity later in life. The fact that these chemicals reach infants so consistently, and during a window when their developing systems are most sensitive, is precisely why endocrinologists pay attention.

It is crucial, though, to read the finding correctly. The researchers are emphatic that breast milk remains the best nutrition for infants, and nothing in the study is an argument against breastfeeding. Street notes that most of the chemicals detected trace back to everyday sources \u2014 nutrition habits and the products families use for personal and household care. The takeaway is not to stop nursing; it is to reduce the chemical load reaching mothers and babies in the first place. In Italy, the work has already spurred a prevention campaign, with several companies agreeing to monitor and cut these chemicals in their products.

## What Diaspora Families Can Take Away

For young Indian families abroad \u2014 often setting up new homes stocked with plastic tiffin boxes, imported beauty products and convenience packaging \u2014 the practical lessons are familiar but worth repeating. Storing and especially heating food in glass or steel rather than plastic, choosing personal-care products with simpler ingredient lists, washing fruit and vegetables well, and ventilating the home can all chip away at exposure.

None of this should breed anxiety in new parents already stretched thin. The study is best understood as a nudge toward small, sensible swaps, and as evidence for regulators and manufacturers that the products surrounding pregnancy and infancy deserve closer scrutiny. The goal, as the researchers put it, is to protect breast milk in a changing world \u2014 not to fear it."""
})

# ============================================================
# ARTICLE 3: India BoP deficit, remittances surge (markets-finance)
# ============================================================
articles.append({
    "headline": "Foreign Money Fled India in April, but a Record Surge in NRI Remittances Helped Cushion the Blow",
    "subheadline": "India's balance of payments slipped into a $6.6 billion deficit as portfolio investors pulled out, yet net transfers from overseas Indians jumped to $16 billion \u2014 and the RBI's push to draw NRI dollars may turn the tide next year.",
    "slug": "india-balance-of-payments-deficit-april-fpi-outflows-remittances-16-billion-surge-nri-investor-20260620-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This is the diaspora's economic footprint laid bare: as foreign funds fled Indian stocks, it was the money sent home by Indians working abroad \u2014 a record $16 billion in a single month \u2014 that helped steady the national accounts, underscoring how central NRIs have become to India's financial stability.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India posts balance of payments deficit in April on foreign portfolio outflows (RBI preliminary data)", "url": "https://www.reuters.com/world/india/"},
        {"name": "Reuters \u2014 Indian rupee's oil relief capped by RBI's FX book, interest payment hedges, bankers say", "url": "https://www.reuters.com/markets/currencies/"}
    ]),
    "body": """India's national balance sheet flashed a warning in April \u2014 and a quiet reassurance at the same time. The country's balance of payments fell into deficit as foreign investors yanked money out of its markets, even as a record flood of remittances from Indians working overseas helped keep the damage in check.

## The Numbers

According to preliminary data from the Reserve Bank of India, India's overall balance of payments recorded a deficit of $6.6 billion in April, a sharp reversal from the $500 million surplus in the same month a year earlier. The balance of payments is, in essence, a tally of all the money flowing into and out of a country; a deficit means more left than arrived.

The drag came almost entirely from the capital account, which captures investment flows. It saw an outflow of $11.3 billion in April 2026, against an inflow of $5.3 billion in the same month last year. Foreign portfolio investors \u2014 the global funds that buy and sell Indian stocks and bonds \u2014 have been heading for the exits all year, unsettled by the war in West Asia, higher oil prices and the search for better returns in American and East Asian technology stocks.

Yet beneath that, the picture was more encouraging. The current account, which tracks trade and transfers, swung to a surplus of $4.7 billion, a striking turnaround from a $4.8 billion deficit in April 2025. And net foreign direct investment \u2014 the longer-term, stickier kind of money \u2014 rose to $7.4 billion from just $1.6 billion a year earlier.

## The Diaspora's Decisive Role

The single most telling figure is the one that names the diaspora directly. Net transfers, which are dominated by remittances from Indian workers abroad, jumped to $16 billion in April, up from $9.4 billion a year earlier \u2014 a leap of nearly 70 percent.

That is the diaspora's economic weight made visible. As foreign funds pulled capital out of Indian equities, it was the money wired home by Indians in the Gulf, the United States, Britain, Canada and beyond that helped flip the current account into surplus and cushion the overall accounts. India has long been the world's largest recipient of remittances, but a single month at this scale underlines just how load-bearing those flows have become for the country's financial stability.

## What the RBI Is Doing

The central bank is leaning into exactly this strength. Over the past several weeks the RBI has rolled out a package of measures designed to pull in non-resident dollars: lifting interest-rate caps on NRI deposits, absorbing the hedging costs on foreign-currency deposits raised by banks, and offering a concessional facility to support external borrowing. The aim is to draw in stable foreign-currency inflows and steady the rupee, which had slumped to an all-time low near 97 per dollar last month before recovering to around 94.3.

Those interventions come at a cost. The RBI's short-dollar forward book has swollen to an estimated all-time high of nearly $110 billion, and the bank is widely expected to use incoming flows to rebuild its foreign-exchange reserves rather than let the rupee strengthen sharply. Analysts at Goldman Sachs and HDFC Bank both expect the currency's upside to stay capped as a result.

Still, the trajectory is improving. India reported a surprise surplus on both the current account and overall balance of payments for the January-to-March quarter, helped by strong services earnings, rising remittances and the central bank's currency swaps. Some economists now expect the country to post a balance-of-payments surplus in the 2026-27 fiscal year, with the NRI-focused deposit drive cited as a key reason.

## Why NRIs Should Care

For the diaspora, this is more than a macroeconomic footnote \u2014 it is a story in which they are the protagonists. The remittances NRIs send home are now a frontline buffer for the Indian economy, and the government and central bank are actively courting their savings with sweeter deposit terms, available for a limited window. For an overseas Indian weighing where to park dollars, the message is that India is, for now, paying up to attract them \u2014 and that the choice of where to send money home carries weight far beyond any single family's balance sheet."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["testosterone hormone vial syringe", "blood glucose test diabetes", "older man exercise gym"],
                          ["testosterone injection vial", "diabetes blood sugar test"], None),
    articles[1]["slug"]: (["breast milk feeding bottle", "mother breastfeeding infant", "plastic baby bottle BPA"],
                          ["mother breastfeeding baby", "baby bottle plastic"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "indian rupee currency notes dollar", "money transfer remittance"],
                          ["indian rupee dollar currency", "money remittance transfer"], None),
}
img_captions = {
    articles[0]["slug"]: "A long-running trial found testosterone aids diabetes-risk reduction only alongside diet and exercise, not as a substitute",
    articles[1]["slug"]: "A study of 336 mother-infant pairs detected BPA, phthalates and parabens in breast milk and infant urine",
    articles[2]["slug"]: "India's balance of payments slipped into deficit in April even as NRI remittances surged to a record $16 billion",
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
