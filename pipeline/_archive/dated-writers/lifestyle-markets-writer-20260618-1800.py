#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 18:00 UTC batch.
Topics:
  1. Higher dietary polyphenol intake linked to reduced pain sensitivity and migraine disability (PLOS One, Jun 2026) — lifestyle-health
  2. Healthy plant-based diet cuts cancer-cardiometabolic multimorbidity risk (EPIC + UK Biobank, 407,618 participants) — lifestyle-health
  3. RBI's FEMA amendment opens repatriable rupee accounts for NRI stock investors (Notification FEMA 395(4)/2026-RB) — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800.bin"):
            with open("/tmp/_img_dl1800.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800.bin")
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
# ARTICLE 1: Polyphenols & migraine (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Eat More Plant Polyphenols and You May Hurt Less \u2014 New Research Links Diet to Migraine Relief",
    "subheadline": "A study published this month in PLOS One found that people who ate more polyphenol-rich foods \u2014 berries, green tea, coffee, herbs and spices \u2014 reported lower pain sensitivity and less migraine-related disability. For a diaspora whose traditional kitchen is built on turmeric, ginger and green tea, the implications are quietly encouraging.",
    "slug": "dietary-polyphenols-reduced-pain-migraine-disability-plos-one-2026-diaspora-turmeric-20260618",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Migraine is strikingly common among South Asian women, and the polyphenols this study credits with easing pain \u2014 from turmeric and ginger to green tea and spices \u2014 are precisely the compounds that fill a traditional Indian kitchen, suggesting the diaspora may already hold a dietary lever it rarely thinks to pull.",
    "sources": json.dumps([
        {"name": "PLOS One \u2014 Higher dietary polyphenol intake is associated with reduced pain sensitivity and migraine-related disability (Bertotti, Rold\u00e1n-Ruiz, L\u00f3pez-Moreno et al., 2026)", "url": "https://journals.plos.org/plosone/"},
        {"name": "Nutrition Reviews \u2014 Dietary interventions in migraine patients: a systematic review (2025)", "url": "https://academic.oup.com/nutritionreviews"}
    ]),
    "body": """For the tens of millions who live with migraine, the search for relief usually runs through the pharmacy. A study published this month in the open-access journal PLOS One points, more quietly, toward the kitchen \u2014 suggesting that what fills the plate may shape how much the head hurts.

## What the Researchers Found

The study, from a team including Bertotti, Rold\u00e1n-Ruiz and L\u00f3pez-Moreno, examined the relationship between dietary polyphenols and pain. Polyphenols are a large family of natural compounds found in plant foods \u2014 the antioxidants that give berries their colour, green tea its astringency, and herbs and spices much of their character. The researchers measured how much of these compounds people consumed and compared it with two outcomes: their general sensitivity to pain, and, among those with migraine, how much the condition disrupted their lives.

The pattern was consistent. Higher dietary polyphenol intake was associated with lower pain sensitivity across participants. And among migraine sufferers specifically, those eating more polyphenol-rich foods reported less migraine-related disability \u2014 fewer days lost, less interference with work and family, a lighter overall burden.

## The Biology Beneath the Link

The finding does not come out of nowhere. Migraine is increasingly understood as a condition with a strong inflammatory and neurovascular component, and polyphenols are known to act on exactly those pathways. In laboratory and animal studies, these compounds suppress neuroinflammation in part by dampening NF-\u03baB signalling, a master switch for inflammatory genes, and by mopping up the oxidative stress that sensitises pain pathways. A calmer, less inflamed nervous system is, in theory, a less migraine-prone one.

The same research group had earlier published a systematic review in Nutrition Reviews surveying dietary interventions in migraine patients, part of a growing body of work taking food seriously as a lever on the condition. Related research has linked adherence to a Mediterranean diet \u2014 rich in polyphenols from olive oil, vegetables and fruit \u2014 with lower migraine frequency and disability, and omega-3 fatty acids have shown prophylactic promise in trials.

## The Honest Caveats

This is observational research, and the usual caution applies with force: an association between high polyphenol intake and less pain does not prove the polyphenols caused the relief. People who eat more berries, greens and spices tend to differ in many other ways \u2014 they may exercise more, sleep better or carry less metabolic risk \u2014 and those differences can muddy the picture. Diet is also notoriously hard to measure accurately. What the study offers is not a cure but a credible, low-risk direction: eating more polyphenol-rich whole plant foods is good for the body in countless documented ways, and it may, this research suggests, ease the burden of migraine too.

## Why This Matters for the Diaspora

For the Indian diaspora, the finding lands on fertile ground. Migraine is strikingly common among South Asian women, often weathered in silence and folded into the general expectation that they simply cope. Yet the polyphenols the study credits are not exotic supplements to be bought \u2014 they are the everyday architecture of a traditional Indian kitchen.

Turmeric, with its polyphenol curcumin, anchors countless dishes. Ginger, long used in Indian households as a folk remedy for nausea and headache, is rich in bioactive polyphenols. Green tea, cloves, cinnamon, black pepper, and the deep bench of Indian spices are all polyphenol-dense. So are the lentils, vegetables and fruit at the heart of a balanced Indian vegetarian diet. The diaspora, in other words, may already possess the dietary tools this research points to \u2014 and lose them precisely when families drift toward refined, processed, Westernised eating.

## What To Actually Do

Lean into polyphenol-rich whole foods rather than reaching for a supplement bottle, since the evidence is strongest for foods, not pills. Keep the spice rack working \u2014 turmeric, ginger, cinnamon and pepper earn their place. Favour berries, leafy greens, whole fruit, green tea and coffee in moderation. Hold on to the polyphenol-dense bones of a traditional diet rather than displacing them with packaged convenience food. And treat diet as a complement to, not a replacement for, proper medical care: anyone with frequent or severe migraine should still see a doctor, while recognising that the plate is a lever worth pulling."""
})

# ============================================================
# ARTICLE 2: Healthy plant-based diet cuts multimorbidity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Not All Vegetarian Diets Are Equal: A 400,000-Person Study Shows Why the Quality of Plant Foods Decides Your Health",
    "subheadline": "Pooling data from more than 407,000 adults across Europe and Britain, researchers found that a diet built on healthy plant foods sharply lowered the risk of developing both cancer and heart-and-metabolic disease together \u2014 while a plant-based diet heavy on refined grains, sugar and fried food did the opposite. The effect was strongest in adults under 60.",
    "slug": "healthy-plant-based-diet-cuts-cancer-cardiometabolic-multimorbidity-epic-uk-biobank-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The Indian diaspora often equates 'vegetarian' with 'healthy' \u2014 yet a diet of white rice, fried snacks, sweets and refined flour is plant-based and harmful, while one of dal, vegetables and whole grains is plant-based and protective; this study draws exactly that line, and it matters enormously for a community already prone to diabetes and heart disease.",
    "sources": json.dumps([
        {"name": "Diabetologia / EPIC \u2013 UK Biobank pooled analysis \u2014 Healthy plant-based diet index and risk of cancer-cardiometabolic multimorbidity (2026)", "url": "https://link.springer.com/journal/125"},
        {"name": "American Journal of Clinical Nutrition \u2014 NHANES analysis of plant-based diet indices, obesity and mortality", "url": "https://academic.oup.com/ajcn"}
    ]),
    "body": """\"Vegetarian\" and \"healthy\" are often treated as the same word. A large new study is a pointed reminder that they are not \u2014 and that for the millions who eat a plant-based diet, the single most important question is which plants.

## What the Study Did

Researchers pooled data from two of the largest nutrition cohorts in the world: the European Prospective Investigation into Cancer and Nutrition, known as EPIC, and the UK Biobank. Together they covered 407,618 adults, whose diets were scored and whose health was tracked over years. The team's focus was not any single disease but multimorbidity \u2014 the increasingly common and dangerous situation of carrying more than one major chronic illness at once, specifically the overlap of cancer with cardiometabolic disease such as heart disease, stroke and type 2 diabetes.

Crucially, the researchers did not lump all plant-based eating together. They used a healthy plant-based diet index, or hPDI, which rewards whole grains, fruits, vegetables, legumes, nuts and healthy oils, and an unhealthy plant-based diet index, or uPDI, which captures refined grains, sugary drinks, sweets, fried foods and other low-quality plant foods. Both are plant-based. Only one is good for you.

## The Findings

The split was stark. A higher healthy plant-based diet score was associated with a substantially lower risk of developing cancer-cardiometabolic multimorbidity. Each 10-point increase in the hPDI was linked to a roughly 19% lower risk in the UK Biobank cohort \u2014 a hazard ratio of 0.81 \u2014 and about 11% lower in EPIC, a hazard ratio of 0.89. The protective effect was notably stronger in adults under 60, suggesting that the choices of midlife matter most.

The unhealthy plant-based diet pulled in the opposite direction, raising the risk of the same clustered diseases. The lesson is not that meat is the enemy or that going vegetarian is automatically virtuous; it is that a plant-based plate built on refined carbohydrates and fried, sugary food carries real harm, while one built on whole, minimally processed plants is powerfully protective.

The pattern echoes other recent work. A US analysis using NHANES data found that adults in the highest tier of a healthy plant-based diet index had dramatically lower odds of obesity and a markedly reduced risk of death from any cause, compared with those eating lower-quality plant foods.

## The Caveats

As observational research, the study shows association rather than airtight causation, and dietary self-reports are always imperfect. But the size of the cohorts, the consistency across two independent populations, and the biological plausibility \u2014 whole plant foods deliver fibre, polyphenols and healthy fats while refined ones spike blood sugar and inflammation \u2014 give the findings real weight.

## Why This Matters for the Diaspora

For the Indian diaspora, few findings are more directly relevant. Vegetarianism is woven into the culture, and with it a comfortable assumption that the diet is healthy by default. The data say otherwise. A plate of white rice, deep-fried snacks, sugary mithai, and refined-flour breads is thoroughly plant-based \u2014 and squarely in the territory the study flags as harmful. A plate of dal, mixed vegetables, whole grains like millet and brown rice, and modest healthy fats is plant-based too \u2014 and protective.

This distinction is not academic for South Asians, who develop type 2 diabetes and heart disease at lower body weights and younger ages than most populations. A diaspora family can be proudly vegetarian and still be eating its way toward exactly the clustered diseases this study warns about, simply by leaning on refined and fried foods. The good news is that the protective version of the diet is also the traditional one, before convenience food crept in.

## What To Actually Do

Judge a vegetarian diet by its quality, not its label. Build meals around whole grains, legumes, vegetables, fruit and nuts \u2014 the dal-sabzi-whole-grain template at its best. Cut back on the refined and fried staples that quietly dominate many diaspora kitchens: white rice in excess, fried snacks, sweets, and refined-flour breads. Recognise that midlife is the highest-leverage window, when the protective effect appears strongest. And resist the false comfort that vegetarian automatically means healthy \u2014 the plants you choose decide the outcome."""
})

# ============================================================
# ARTICLE 3: RBI FEMA amendment — repatriable rupee accounts for NRI stock investors (markets-finance)
# ============================================================
articles.append({
    "headline": "India Just Made It Easier for NRIs to Buy Indian Stocks \u2014 RBI Opens a New Repatriable Rupee Account",
    "subheadline": "The Reserve Bank of India has amended its foreign-exchange rules to let individuals living abroad open dedicated repatriable rupee accounts for investing in listed Indian shares, with sale proceeds free to be sent back overseas. A new 'Individual Foreign Investor' category streamlines the long-tangled plumbing of cross-border equity investment.",
    "slug": "rbi-fema-amendment-repatriable-rupee-account-nri-stock-investors-individual-foreign-investor-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Millions of NRIs want a stake in India's growth story but have long been deterred by a maze of account types, custodial rules and repatriation friction; this RBI amendment is aimed squarely at them, simplifying how a person abroad can buy Indian shares and \u2014 just as importantly \u2014 get their money back out.",
    "sources": json.dumps([
        {"name": "Reserve Bank of India \u2014 Notification No. FEMA 395(4)/2026-RB (Foreign Exchange Management amendment, June 13, 2026)", "url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx"},
        {"name": "The Economic Times \u2014 RBI eases FEMA rules for NRI and foreign individual investment in Indian equities", "url": "https://economictimes.indiatimes.com/markets"}
    ]),
    "body": """India has spent years courting the savings of its vast diaspora, with mixed success. The intent has never been the problem; the plumbing has. A fresh amendment from the Reserve Bank of India takes direct aim at that plumbing, making it materially easier for individuals living abroad to buy listed Indian shares \u2014 and, crucially, to take their money back out when they choose.

## What Changed

In Notification No. FEMA 395(4)/2026-RB, dated June 13, 2026, the RBI amended its Foreign Exchange Management regulations to allow individuals resident outside India to open designated repatriable rupee accounts for the specific purpose of investing in listed Indian equities. The change also creates a new reporting category \u2014 the Individual Foreign Investor, or IFI \u2014 intended to give overseas individuals a cleaner, dedicated route into Indian markets rather than forcing them through structures built for large institutions.

The word that matters most is repatriable. Under the amended rules, the proceeds from selling those shares can be remitted abroad or credited back to the designated account, removing one of the persistent anxieties that has kept diaspora money on the sidelines: the fear that capital sent into India is easy to put in and hard to get out. The framework also extends to investments in the National Pension System and mutual funds by NRIs and Overseas Citizens of India, broadening the set of instruments an overseas individual can hold on a repatriable basis.

## Why Now

The amendment does not arrive in isolation. It is part of a broader, deliberate push to draw foreign capital into Indian assets at a moment when the government is keen to deepen and diversify the investor base. Earlier this month, on June 5, India removed taxes on foreign investment in government securities \u2014 a move that produced an immediate response, drawing roughly $2 billion of inflows in two weeks, more than the $1.6 billion attracted in the first five months of the year combined.

Read together, the two steps signal a coherent strategy: lower the friction, clarify the rules, and let both institutions and individuals abroad participate more freely in financing India's growth. For a country running a persistent need for foreign capital, widening the door to its own diaspora is among the most natural moves available.

## The Practical Picture

For an NRI or OCI, the change should mean a simpler path from intent to investment. Historically, an overseas individual wanting to buy Indian shares has navigated a confusing array of account types \u2014 different rules for repatriable and non-repatriable money, portfolio investment scheme designations, custodial requirements and reporting obligations that vary by status. A dedicated repatriable rupee account, paired with the new IFI category, is meant to consolidate and clarify that route.

What remains essential is the detail, much of which depends on the operational guidelines and the way banks and brokers implement the framework. Tax treatment \u2014 including capital-gains rules and the benefits of Double Taxation Avoidance Agreements \u2014 continues to depend on the investor's country of residence and the specific instrument held. The headline reform opens the door; the precise mechanics will be set by the circulars and bank procedures that follow.

## What It Means for the Diaspora

For the diaspora, the appeal is straightforward. Many NRIs hold a deep conviction in India's long-term growth and want a direct stake in it, beyond the real estate and fixed deposits that have traditionally absorbed their rupee savings. Yet the gap between wanting to invest and actually doing so has been filled with paperwork and uncertainty, and plenty of would-be investors have simply given up. By creating a clear, repatriable channel built for individuals, the RBI is addressing the precise pain point that has deterred them.

The sober counsel still applies. Easier access is not a reason to invest, only a reason it is now simpler to do so. NRIs should weigh currency risk \u2014 returns earned in rupees must eventually be converted back \u2014 alongside the tax rules of their home country and the same diversification discipline that governs any equity investment. The reform removes friction; it does not remove risk. But for a diaspora long frustrated by the mechanics of investing back home, the door has just been opened meaningfully wider."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["green tea cup", "fresh berries bowl", "turmeric spice powder"],
                          ["green tea and berries", "colorful berries and spices"], None),
    articles[1]["slug"]: (["healthy vegetables legumes", "lentils dal bowl", "fresh vegetables whole grains"],
                          ["healthy plant based meal vegetables", "bowl of lentils and vegetables"], None),
    articles[2]["slug"]: (["Reserve Bank of India building", "Bombay Stock Exchange building", "Indian rupee currency"],
                          ["indian stock market trading", "indian rupee money"], None),
}
img_captions = {
    articles[0]["slug"]: "Green tea, berries and spices are rich in polyphenols; new research links higher polyphenol intake to lower pain sensitivity and migraine disability",
    articles[1]["slug"]: "Lentils, vegetables and whole grains; a 400,000-person study shows the quality of plant foods, not the vegetarian label, decides health outcomes",
    articles[2]["slug"]: "The Reserve Bank of India has amended its foreign-exchange rules to ease how individuals abroad invest in listed Indian shares",
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
