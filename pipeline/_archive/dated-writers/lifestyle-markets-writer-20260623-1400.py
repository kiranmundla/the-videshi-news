#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 10:00 UTC batch.
Topics (checked against last-3-day articles to avoid dupes):
  1. Hearing loss is one of the largest MODIFIABLE risk factors for dementia —
     a new All of Us analysis (16,270 adults) found severe hearing loss carried
     an odds ratio of 6.76 for dementia, and the randomized ACHIEVE-style
     hearing-aid trial (~1,000 adults 70-84) cut cognitive decline by nearly 50%
     in high-risk elders. — lifestyle-health
  2. Microplastics found inside the human eye — the first study to detect
     microplastics in the trabecular meshwork (20 glaucoma patients) tied the
     plastic burden tightly to higher intraocular pressure, hinting at a new,
     under-recognised pathway in glaucoma. — lifestyle-health
  3. Indian IT stocks slump after Accenture trims its FY26 revenue guidance to
     3-4%; brokerages warn FY27 for Indian IT could be weaker than the Street
     expects as AI and cautious client spending cloud the outlook. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000z.bin"):
            with open("/tmp/_img_dl1000z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000z.bin")
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
# ARTICLE 1: Semaglutide and bone fractures (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Weight-Loss Drug That Was Feared to Weaken Bones May Actually Help Protect Them",
    "subheadline": "In a study of nearly 60,000 adults with type 2 diabetes, those on semaglutide \u2014 the drug behind Ozempic and Wegovy \u2014 broke fewer bones than people on rival weight-loss treatments, easing a long-standing worry that rapid weight loss leaves the skeleton fragile.",
    "slug": "semaglutide-ozempic-lower-bone-fracture-risk-type-2-diabetes-endo-2026-stanford-59000-adults-diaspora-20260623-1400",
    "category": "lifestyle-health",
    "vertical": "metabolic-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indians carry one of the world's heaviest burdens of type 2 diabetes and are increasingly being prescribed GLP-1 drugs in India and abroad \u2014 so reassurance that semaglutide does not appear to crumble the bones of diabetic patients, and may even guard them, speaks directly to millions of NRI families weighing whether a parent or partner should start one of these medicines.",
    "sources": json.dumps([
        {"name": "New York Post \u2014 'Ozempic and Wegovy may strengthen bones in Type 2 diabetes patients, study finds' (ENDO 2026 presentation, Dr. Jairo Nore\u00f1a, Stanford)", "url": "https://nypost.com/2026/06/19/health/ozempic-and-wegovy-may-strengthen-bones-in-type-2-diabetes-patients/"},
        {"name": "Knowridge Science Report \u2014 'Could a Popular Weight-Loss Drug Also Protect Bones?'", "url": "https://knowridge.com/"},
        {"name": "Diabetes, Obesity and Metabolism \u2014 'Associations of Semaglutide With Skeletal Outcomes in People With Obesity, With and Without Type 2 Diabetes: A Target Trial Emulation' (TriNetX cohort)", "url": "https://pubmed.ncbi.nlm.nih.gov/"}
    ]),
    "body": """For all the headlines about waistlines, one quiet anxiety has trailed the blockbuster weight-loss drugs from the start: what does losing weight that fast do to your bones? Decades of research had taught doctors a hard rule \u2014 shed a lot of weight, and you usually shed bone density with it, raising the risk of fractures later. New findings presented to one of the world's biggest gatherings of hormone specialists now suggest that semaglutide, the active ingredient in Ozempic and Wegovy, may break that rule, and possibly turn it on its head.

## What the Researchers Found

A team led by Dr. Jairo Nore\u00f1a, then an endocrinology fellow at Stanford University Medical Center, combed through the medical records of more than 59,000 adults with type 2 diabetes treated between 2016 and 2023. They deliberately excluded anyone who had already broken a bone or was taking osteoporosis medication, so they could focus on new fractures that occurred only after treatment began.

More than 26,000 of those patients were taking semaglutide. The comparison group of over 33,000 was on other widely used weight-loss or diabetes drugs \u2014 dulaglutide, phentermine-topiramate, or bupropion-naltrexone. As expected, the semaglutide users lost more weight. The surprise was in the breaks: 794 fractures among the semaglutide group, against 1,045 in the comparison group. After the numbers were adjusted, semaglutide was tied to roughly a 15 percent lower risk of fracture.

The work was unveiled at ENDO 2026, the Endocrine Society's annual meeting held in Chicago in mid-June, and it dovetails with a separate, larger analysis published in the journal Diabetes, Obesity and Metabolism. That study, drawing on a vast electronic health-record network and matching patients carefully, found that among people with obesity and type 2 diabetes, starting semaglutide was associated with a meaningfully lower risk of major osteoporotic fractures over three years compared with other glucose-lowering drugs and usual care.

## Why This Was Counterintuitive

The result runs against an old and reasonable fear. When the body sheds weight quickly, bones bear less mechanical load, and the skeleton can respond by thinning. Some earlier, smaller trials had picked up worrying signals \u2014 markers of bone breakdown rising, bone mass at the hip and spine dipping \u2014 in people on semaglutide who lost weight. Doctors had every reason to wonder whether the drugs were quietly setting patients up for fractures down the line.

What the new, large real-world datasets suggest is that, at least in people with type 2 diabetes, that fear may be overblown. One intriguing thread of laboratory and imaging research even hints that GLP-1 drugs might act directly on bone metabolism in ways that partly offset the losses that come with shedding weight. Diabetes itself weakens bone quality, so a drug that controls blood sugar well may be protecting the skeleton through that route too.

## The Important Caveats

This is not the final word, and the researchers are the first to say so. Both studies are observational \u2014 they mine existing records rather than randomly assigning patients to a drug \u2014 which means they can reveal associations but cannot prove that semaglutide directly prevents fractures. Unmeasured differences between the groups could be doing some of the work. Tellingly, the protective signal in the larger analysis showed up in people who had type 2 diabetes, but not in those who had obesity without diabetes, a reminder that the picture is more complicated than a simple "bone-strengthening drug" headline.

"This work is an important early step," Dr. Nore\u00f1a cautioned, calling for proper prospective trials that follow patients forward in time. The sensible takeaway is not that semaglutide builds bone, but that the worst fears about it crumbling bone in diabetic patients have not borne out \u2014 and may even be the opposite.

## Why It Matters for the Diaspora

India is often called the diabetes capital of the world, and the condition shadows the diaspora wherever it settles, driven by genetics, diet and the metabolic quirks that make South Asians prone to diabetes at lower body weights than many other groups. As GLP-1 drugs spread \u2014 now manufactured and prescribed in India, and increasingly used by NRIs abroad \u2014 families everywhere are wrestling with the same question: is this medicine safe for an ageing parent, a spouse, or themselves?

Bone health sits squarely inside that calculation, because a hip fracture in later life can be a turning point from independence to frailty, and South Asians already face elevated osteoporosis risk, often with lower vitamin D and calcium intake. These findings offer cautious reassurance that, for people with type 2 diabetes, semaglutide is unlikely to be silently weakening the skeleton, and may be doing the reverse. The practical advice barely changes: anyone on these drugs, especially older adults, should keep up protein, calcium and vitamin D, stay physically active to load the bones, and discuss a bone-density check with their doctor. But the news removes one more reason to hesitate over a treatment that, for many diabetic patients, is proving genuinely transformative."""
})

# ============================================================
# ARTICLE 2: Vitamin C and brain aging (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Common Vitamin in Citrus and Greens Is Linked to a Better-Preserved Brain in Older Age",
    "subheadline": "In more than 2,000 older adults, those with higher blood levels of vitamin C had more grey matter and stronger memory-network connections on brain scans \u2014 the first study to tie measured vitamin C, not just diet surveys, to the brain's structure.",
    "slug": "vitamin-c-blood-levels-brain-structure-grey-matter-default-mode-network-hirosaki-plos-one-2044-adults-diaspora-20260623-1400",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian cuisine is rich in the very foods that deliver vitamin C \u2014 amla, citrus, guava, tomatoes, green chillies and leafy saag \u2014 yet long cooking and changing diets can strip it away, making this a timely, low-cost reminder for diaspora families that protecting an ageing parent's mind may start with what is on the plate.",
    "sources": json.dumps([
        {"name": "PLOS ONE \u2014 study of 2,044 older adults in Hirosaki City, Japan, linking plasma vitamin C to grey-matter volume and default-mode-network connectivity (Dr. Tomohiro Shintaku, Hirosaki University)", "url": "https://journals.plos.org/plosone/"},
        {"name": "New York Post / Fox News Digital \u2014 'Common vitamin may influence brain aging in ways scientists didn't expect'", "url": "https://nypost.com/2026/06/16/health/common-vitamin-may-influence-brain-aging-in-ways-scientists-didnt-expect/"},
        {"name": "Medical News Today commentary \u2014 Dr. Dung Trinh, Healthy Brain Clinic, on vitamin C and brain health", "url": "https://www.medicalnewstoday.com/"}
    ]),
    "body": """It is one of the most familiar nutrients on earth, the thing parents push when a cold is coming and the reason orange juice has a healthy halo. Now vitamin C is turning up in an unexpected place: brain scans of older adults. New research finds that people with higher blood levels of the vitamin tend to have better-preserved brain structure and stronger connections in a network tied to memory and thinking \u2014 a hint that something as ordinary as a daily helping of citrus or greens may help the ageing mind hold its shape.

## What the Study Did

Researchers in Japan, publishing in the journal PLOS ONE, studied 2,044 older adults living in Hirosaki City. The participants, with an average age of 69 and about 61 percent women, were already enrolled in a long-running project on dementia and heart-disease risk. Crucially, the team measured the actual level of vitamin C in participants' blood rather than relying on people's memories of what they ate, and paired that with MRI scans to calculate the volume of grey and white matter in the brain.

Even after accounting for age, smoking, diabetes and other lifestyle factors, a pattern emerged: those with lower vitamin C levels tended to have lower brain-tissue volumes and weaker structural networks. Those with higher levels showed better-preserved grey matter and stronger connectivity within the default mode network \u2014 a web of brain regions central to memory and self-reflection, and one of the first to falter in Alzheimer's disease and depression.

"While diets rich in vitamin C are known to lower the risk of cognitive decline, our study is the very first to demonstrate a direct association between actual blood plasma vitamin C levels and the structural connectivity of the default mode network," said Dr. Tomohiro Shintaku of Hirosaki University, who led the work. Because the vitamin C was measured directly in blood, he argued, the link is more reliable than studies that estimate intake from food questionnaires.

## Why Vitamin C and the Brain

There are plausible biological reasons. Vitamin C is a powerful antioxidant that mops up the kind of cellular damage that accumulates with age, and the brain, with its intense energy use, is especially exposed to that damage. The vitamin is also needed to make certain neurotransmitters and to keep blood vessels healthy. And because humans, unlike most animals, cannot manufacture vitamin C themselves, every bit must come from the diet \u2014 which is precisely why what we eat matters so directly.

## The Caveats Are Real

The researchers are careful not to oversell. The study is observational and captured a single snapshot in time, so it can show an association but cannot prove that vitamin C preserves the brain or that swallowing supplements would help. It rested on one blood measurement per person. The effect was modest next to heavyweight risk factors such as high blood pressure and high blood sugar. And the participants were almost entirely older Japanese adults, so the findings may not translate neatly to other populations.

Independent experts struck the same note of caution. "The study does not prove that vitamin C prevents cognitive decline or that taking supplements will improve brain health," said Dr. Dung Trinh of the Healthy Brain Clinic. "It is best viewed as a signal that vitamin C status may be one piece of a much larger brain-health picture." In other words, this is a reason to eat well, not a reason to reach for a pill bottle \u2014 and certainly not a substitute for managing blood pressure, blood sugar and exercise.

## Why It Matters for the Diaspora

For Indian families, the practical lesson lands close to home, because the kitchen is already stocked with the answer. India is unusually rich in vitamin C foods \u2014 amla, the gooseberry long prized in Ayurveda, is among the densest natural sources on earth, and guava, citrus, tomatoes, green chillies and leafy greens like saag and methi all deliver it in abundance. The catch is how the food is treated: vitamin C is fragile, and the long simmering, reheating and heavy frying common in many kitchens can destroy much of it.

The takeaway is gentle and achievable. Encouraging an ageing parent to eat some raw or lightly cooked vitamin C-rich food daily \u2014 a piece of fruit, a fresh salad, a squeeze of lemon over a finished dish, a spoon of amla \u2014 is cheap, culturally familiar and carries no downside. It will not single-handedly stave off dementia. But in the larger effort to protect the brain across a lifetime, it is one more small, sensible habit that costs almost nothing and fits effortlessly into the food the diaspora already loves."""
})

# ============================================================
# ARTICLE 3: India's record Russian crude pivot (markets-finance)
# ============================================================
articles.append({
    "headline": "India Just Bought More Russian Oil Than Ever \u2014 Right as Washington's Sanctions Waiver Expires",
    "subheadline": "After the Iran war scrambled global energy flows, Russia's share of India's crude imports has nearly doubled to almost half, hitting a record 2.55 million barrels a day in June \u2014 but a lapsed US waiver now forces a tricky choice on Delhi's refiners.",
    "slug": "india-record-russian-crude-imports-june-2026-us-sanctions-waiver-expires-hormuz-rupee-nri-investor-20260623-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "India's energy bill is the hidden hinge of its economy \u2014 it shapes inflation, the rupee NRIs send money in, and the stock indices the diaspora invests in \u2014 so how Delhi balances cheap Russian crude against renewed US sanctions pressure will ripple straight through the remittances and portfolios that tie the diaspora to home.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'India pivots to Russian crude and coal to mitigate Iran war fallout' (Kpler data on June import volumes)", "url": "https://www.reuters.com/"},
        {"name": "Outlook Business \u2014 'India's Oil Comeback: How Refiners Navigated the Strait of Hormuz Crisis'", "url": "https://www.outlookbusiness.com/"},
        {"name": "OilPrice.com \u2014 'The Hormuz Crisis Has Forced India to Rethink Its Energy Strategy'", "url": "https://oilprice.com/"}
    ]),
    "body": """India's oil map has been redrawn at remarkable speed. After a four-month war centred on Iran throttled energy flows through the Strait of Hormuz, the world's third-largest oil importer swung hard toward Russian crude to keep its refineries fed. By June, that pivot had reached a record: Russia is supplying almost half of all the oil India buys. The timing, however, is awkward, because the very American waiver that made those purchases easy has just lapsed.

## A Record Surge

According to data compiled by the commodity analytics firm Kpler, India's imports of Russian crude are set to hit a record high of roughly 2.55 million barrels per day in June, up from 2.13 million in May. That pushes Russia's share of India's total crude imports of about 5.29 million barrels a day to just under 50 percent \u2014 a dramatic leap from an average of around 23 percent in the three months before the war began on February 28.

The shift was born of necessity. When fighting effectively closed the Strait of Hormuz \u2014 the narrow waterway through which a large share of India's crude, LNG and cooking gas normally flows \u2014 India's crude imports tumbled nearly 14 percent in March, to 4.5 million barrels a day. India's weighted average crude price spiked from around $69 a barrel in March to more than $114 in April, a brutal jolt for an economy that imports the overwhelming majority of the oil it burns.

Russian barrels filled the gap. Indian refiners roughly doubled their purchases from Russia after the Trump administration temporarily waived sanctions on buying it, a move designed to calm global oil markets. Cargoes already at sea could be diverted quickly to Indian ports, and a maintenance restart at the Rosneft-backed Nayara Energy refinery in Gujarat, which leans heavily on Russian crude, added further demand. By June, total imports had climbed back above 5 million barrels a day \u2014 a near-complete recovery.

## The Catch: A Waiver That Expired

Here is the complication. That US sanctions waiver expired on June 17, and the Treasury did not extend it. In theory, India should now wind down its Russian purchases and return to Middle Eastern suppliers. Whether it actually does depends on how much confidence Delhi's government and refiners have in the fragile new calm in the Gulf \u2014 and on how much they are willing to test Washington's patience.

For now, India is hedging. It is still holding back from some Gulf producers: imports from Saudi Arabia are forecast at just 349,000 barrels a day in June, down sharply from 832,000 before the war. Refiners appear to be waiting to see whether tanker traffic through Hormuz, which has been picking up since an interim peace agreement, stays reliable before committing fully to a return.

## Why It Matters Beyond the Oil Market

Energy is the master variable of India's macroeconomy. Cheaper crude eases inflation, lightens the import bill, narrows the current-account deficit and takes pressure off the rupee; expensive crude does the opposite on every count. The government has worked hard to shield consumers \u2014 the petroleum minister noted that fuel prices at the pump rose only modestly even as oil companies absorbed heavy losses during the disruption. But that shield has fiscal costs, and a sustained return to pricier Middle East oil, or any fresh Hormuz scare, would feed straight through to prices, the deficit and the currency.

The deeper lesson, analysts say, is about vulnerability. The Hormuz shock exposed just how exposed India is, prompting talk of larger strategic reserves, deeper energy ties with the United States for LNG, and a faster push into renewables to dilute its dependence on imported fossil fuels. A world of bigger buffers may make India more resilient to the next shock \u2014 but building those buffers takes years.

## Why It Matters for the Diaspora

Few things connect the diaspora to India's fortunes as directly as the price of oil, even if the link is invisible. It moves the inflation rate that erodes the value of money sent home; it moves the rupee, which decides how far each remittance stretches for families in India; and it moves the Sensex and Nifty that anchor so many NRI portfolios. A cheaper, well-supplied oil market is quietly good news for diaspora savings and the relatives who depend on them.

For diaspora investors, the message is to watch the energy story as a leading indicator, not a sideshow. India's deft pivot to Russian crude bought it breathing room, but the expired waiver introduces real diplomatic and price risk into the months ahead. How Delhi threads the needle \u2014 keeping fuel affordable, the rupee steady and Washington onside \u2014 will shape the inflation and currency backdrop against which every India-linked investment, and every rupee wired home, is measured."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Ozempic semaglutide injection pen", "insulin pen diabetes medication", "human femur bone X-ray hip"],
                          ["semaglutide injection pen diabetes", "bone density scan elderly"], None),
    articles[1]["slug"]: (["fresh citrus fruits oranges vitamin C", "Indian gooseberry amla fruit", "green leafy vegetables fresh produce"],
                          ["fresh oranges citrus vitamin c", "leafy green vegetables healthy"], None),
    articles[2]["slug"]: (["crude oil tanker ship sea", "oil refinery India petroleum", "Jamnagar refinery oil terminal"],
                          ["oil tanker ship ocean crude", "petroleum refinery industry"], None),
}
img_captions = {
    articles[0]["slug"]: "A study of nearly 60,000 diabetes patients found semaglutide users had a lower fracture rate than those on rival weight-loss drugs",
    articles[1]["slug"]: "Citrus, amla, tomatoes and leafy greens are among the richest dietary sources of vitamin C, linked to better-preserved brain structure",
    articles[2]["slug"]: "Russia now supplies almost half of India's crude imports, with a record 2.55 million barrels a day arriving in June",
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
