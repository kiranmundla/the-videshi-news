#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 14:00 UTC batch.
Topics:
  1. JAMA Neurology / Harvard (Nurses' + Health Professionals cohorts, 159,347
     people): head-to-head of six healthy diets for cognition — DASH stood out,
     41% lower risk of self-reported cognitive decline (highest vs lowest
     adherence). Observational. — lifestyle-health
  2. Alzheimer's & Dementia / University of Bristol & Copenhagen (Mendelian
     randomization, >1M people): genetically lower LDL cholesterol (~1 mmol/L)
     linked to substantially lower dementia risk (up to ~80% in some groups);
     same proteins targeted by statins/ezetimibe. Not proof drugs prevent
     dementia. — lifestyle-health
  3. Indian rupee/bonds outlook: rupee +0.8% to 94.32 (best week in 11 weeks)
     on lower oil after US-Iran deal; now tracking a 1-year-high dollar and
     hawkish Fed; bonds keyed to pace of foreign inflows after RBI's debt-market
     tax/access measures (seen drawing ~$30-50bn). — markets-finance
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
# ARTICLE 1: DASH beats five other diets for the aging brain (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Diet Built to Lower Blood Pressure Just Beat Five Rivals at Protecting the Aging Brain",
    "subheadline": "In a Harvard-led comparison of nearly 160,000 people, the DASH eating pattern outperformed the Mediterranean diet and four others, with the most faithful followers showing a 41 percent lower risk of cognitive decline decades later.",
    "slug": "dash-diet-beats-mediterranean-mind-cognitive-decline-jama-neurology-harvard-159000-diaspora-20260622-1400",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians face an unusually high burden of both hypertension and dementia, yet the brain-protective DASH pattern \u2014 heavy on vegetables, fruit, whole grains, beans and low-fat dairy, light on salt and sweets \u2014 maps neatly onto a thoughtfully built Indian thali, giving NRI families a culturally familiar template that may guard the heart and the mind at once.",
    "sources": json.dumps([
        {"name": "JAMA Neurology \u2014 Dietary Patterns and Cognitive Health in US Adults", "url": "https://jamanetwork.com/journals/jamaneurology"},
        {"name": "Inc. \u2014 Massive New Harvard Study: Eat Like This for a Stronger Brain", "url": "https://www.inc.com/bill-murphy-jr/want-a-sharper-brain-a-massive-harvard-study-of-159347-people-says-start-eating-like-this/91363580"},
        {"name": "Harvard T.H. Chan School of Public Health \u2014 Diet and cognitive health", "url": "https://hsph.harvard.edu/"}
    ]),
    "body": """For years the Mediterranean diet has worn the crown in nutrition's annual beauty contests, lauded for its olive oil, fish and longevity. A large new study from Harvard has staged a rare head-to-head, scoring six well-regarded eating patterns against one another for what they do to the aging brain \u2014 and a more workmanlike diet, built decades ago simply to lower blood pressure, came out on top.

## What the Study Found

The research, published in JAMA Neurology, drew on three of the longest-running cohorts in American medicine: the Nurses' Health Study, its sequel Nurses' Health Study II, and the Health Professionals Follow-Up Study. Together they cover 159,347 participants, most of them women, enrolled at an average age of 44 and tracked for decades.

A Harvard-affiliated team led by Hui Chen, with senior researchers including the prominent nutrition epidemiologists Walter Willett and Alberto Ascherio, scored each person's diet on adherence to six established healthy patterns: the Mediterranean diet, the MIND diet, an empirical plant-based pattern, an empirical anti-inflammatory pattern, the Alternative Healthy Eating Index, and DASH \u2014 short for Dietary Approaches to Stop Hypertension. They then followed decades of self-reported cognitive decline, backed by objective cognitive testing in a subset.

All six diets were linked to better cognition in later life. But DASH stood clearly apart. People with the highest adherence to it had a 41 percent lower risk of cognitive decline than those with the lowest adherence \u2014 a connection more than twice as strong as some earlier work had suggested.

## What's Actually on a DASH Plate

The striking part is how ordinary the DASH plate is. The diet was devised in the 1990s not to protect memory but to bring down blood pressure; the cognitive payoff appears to be a bonus. It emphasizes vegetables, fruits and whole grains; fat-free or low-fat dairy, fish, poultry, beans, nuts and vegetable oils; and it limits foods high in saturated fat, along with sugary drinks and sweets. Crucially, it also keeps a firm lid on salt.

That overlaps heavily with the Mediterranean diet, and the resemblance is not accidental. The differences sit at the margins: DASH leans harder on dairy and on cutting sodium, while the Mediterranean pattern leans on olive oil and fish. In this comparison, those small distinctions added up to a measurable gap in favor of DASH.

## How to Read It Honestly

The usual cautions apply, and they matter. This is observational research, which can show a strong association but cannot prove that the diet itself caused better cognition. Diet was captured through food-frequency questionnaires filled out over many years, a method prone to recall error. And the participant pool skews heavily toward women and toward health professionals \u2014 nurses and doctors \u2014 who may differ from the wider population in income, health literacy and habits.

None of that erases the signal. When nearly 160,000 people followed for decades line up behind one eating pattern as the strongest dietary predictor of late-life cognition, the result is hard to wave away. It does not crown DASH as a magic shield; it suggests that, among already-healthy diets, the details of emphasis \u2014 more produce and low-fat dairy, less salt and sugar \u2014 may nudge the odds in the brain's favor.

## Why It Matters for the Diaspora

For the Indian diaspora, the finding lands on doubly sensitive ground. Hypertension is widespread among South Asians, and dementia risk is rising as the community ages abroad. A diet that was purpose-built to lower blood pressure, and now appears to protect the brain as well, addresses two of the population's most pressing vulnerabilities at once.

It is also unusually easy to adopt without abandoning the kitchen. A well-balanced thali \u2014 generous on sabzi and dal, leaning on whole grains like brown rice, millets and whole-wheat roti, with curd, beans and nuts \u2014 already sketches the DASH blueprint. The adjustments are familiar ones: ease up on salt and salty pickles and papads, cut back on mithai and sugary chai, and favor fruit and vegetables over fried snacks.

The deeper message is one of reassurance. Protecting memory in old age may not require an exotic regimen or an expensive supplement. For many diaspora families, it may mean cooking much as their grandparents did \u2014 a little less salt, a little less sugar, a lot more on the plate that grew from the ground."""
})

# ============================================================
# ARTICLE 2: Lower cholesterol tied to lower dementia risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "People Born With Naturally Lower Cholesterol Are Far Less Likely to Develop Dementia, a Million-Person Study Finds",
    "subheadline": "Using genetics to sidestep the bias of ordinary diet studies, researchers found that a modest lifelong reduction in cholesterol \u2014 the same effect statins aim for \u2014 was linked to a sharply lower risk of dementia, hinting that protecting the heart may also protect the mind.",
    "slug": "lower-ldl-cholesterol-genes-dementia-risk-mendelian-randomization-bristol-alzheimers-dementia-diaspora-20260622-1400",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry both elevated heart-disease risk and a high genetic predisposition to unhealthy cholesterol, and statins are already among the most prescribed drugs in Indian households \u2014 so evidence that lifelong lower cholesterol may also guard against dementia gives the diaspora one more reason to take a number they were already told to watch seriously.",
    "sources": json.dumps([
        {"name": "Alzheimer's & Dementia \u2014 Genetically low LDL cholesterol and risk of dementia", "url": "https://alz-journals.onlinelibrary.wiley.com/journal/15525279"},
        {"name": "Knowridge Science Report \u2014 Lowering Your Cholesterol May Help Prevent Dementia", "url": "https://knowridge.com/2026/06/lowering-your-cholesterol-may-help-prevent-dementia/"},
        {"name": "University of Bristol \u2014 Research news", "url": "https://www.bristol.ac.uk/news/"}
    ]),
    "body": """Doctors have long urged patients to keep their cholesterol in check for the sake of their hearts. A large new study suggests the payoff may reach higher \u2014 all the way to the brain. People who inherited genes that keep their cholesterol naturally low, researchers found, were markedly less likely to develop dementia.

## What the Study Found

The work, published in Alzheimer's & Dementia, the official journal of the Alzheimer's Association, was led by Dr. Liv Tybj\u00e6rg Nordestgaard during her time at the University of Bristol and Copenhagen University Hospital in Denmark. The team examined health data from more than one million people, a scale that let them trace long-term patterns hard to detect in smaller studies.

Their focus was a clever one. Rather than ask what people ate or which pills they took \u2014 questions tangled up with income, lifestyle and habit \u2014 the researchers used a method called Mendelian randomization. It leans on the fact that the genes a person inherits are fixed at birth and largely independent of how they live. By comparing people who carry gene variants that naturally lower cholesterol with those who do not, scientists can approximate a lifelong, real-world experiment without waiting decades for one.

Tellingly, the variants they studied affect the very same proteins that today's cholesterol drugs \u2014 statins and ezetimibe \u2014 are designed to target. The results were striking: even a relatively small reduction in cholesterol, about one millimole per liter, was linked to a significantly lower risk of dementia. In some groups, the reduction in risk reached as much as 80 percent.

## What It Does Not Prove

The caveats here are as important as the headline. Mendelian randomization strengthens the case that lower cholesterol is doing something causal, rather than merely traveling alongside other healthy traits. But Dr. Nordestgaard was careful to stress what the study cannot say: it does not prove that taking cholesterol-lowering medication will prevent dementia. Genes that lower cholesterol from birth are not the same as starting a drug in middle or old age, and the brain's decline unfolds over decades.

The likely mechanism points back to the blood vessels. One leading explanation is atherosclerosis \u2014 the buildup of cholesterol and other deposits that narrow and stiffen arteries, including those feeding the brain. Reduced blood flow, or tiny clots forming in damaged vessels, may injure brain tissue gradually and contribute to memory loss and other signs of dementia. Lower cholesterol may simply keep those pipes cleaner for longer.

Dr. Nordestgaard suggested the natural next step is long clinical trials, perhaps lasting 10 to 30 years, to test directly whether lowering cholesterol with medication protects the brain. Until then, the finding is best read as a strong, biologically plausible signal rather than a prescription.

## Why It Matters for the Diaspora

For the Indian diaspora, the message reinforces a warning the community has already heard. South Asians carry an elevated, well-documented risk of heart disease, often striking earlier and at lower body weights than in other groups, and many also have a genetic tilt toward unhealthy cholesterol profiles, including high LDL and lipoprotein(a). Statins are among the most commonly prescribed medicines in Indian households at home and abroad.

This study adds a second front to that familiar advice. The same number NRIs were told to monitor for their hearts may also bear on whether they keep their memory sharp into old age \u2014 making cholesterol checks, and the lifestyle and, where prescribed, medication that bring it down, feel less like single-organ maintenance and more like whole-body, whole-life protection.

The practical takeaways are unglamorous and unchanged: get cholesterol tested, know the LDL number, and address it through the proven levers \u2014 a diet rich in vegetables, fiber and healthy fats, regular exercise, not smoking, and medication when a doctor advises it. What is new is the stakes. For a community already primed to take its hearts seriously, the brain may be quietly riding along."""
})

# ============================================================
# ARTICLE 3: Rupee, bonds outlook as oil cools and dollar firms (markets-finance)
# ============================================================
articles.append({
    "headline": "The Rupee Just Had Its Best Week in Months. Now a Resurgent Dollar Will Test Whether It Holds.",
    "subheadline": "A drop in oil after the US-Iran peace deal pushed the rupee to 94.32, its strongest weekly run in 11 weeks \u2014 but a dollar at a one-year high and a hawkish Federal Reserve are pulling the currency back, while government bonds wait on the pace of foreign money returning.",
    "slug": "rupee-best-week-oil-falls-dollar-one-year-high-hawkish-fed-bonds-foreign-inflows-nri-investor-20260622-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Every move in the rupee reprices the remittances NRIs send home, the value of their NRE and FCNR deposits, and the returns on their Indian investments \u2014 so a week that swung from oil-driven relief to dollar-driven pressure is not abstract macro news for the diaspora but a direct signal on when to send money and what their India holdings are worth.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Rupee to track dollar moves, oil outlook; bonds to react on foreign investor activity", "url": "https://www.reuters.com/world/india/"},
        {"name": "Reuters \u2014 India's measures to protect rupee seen drawing about $40 billion, analysts say", "url": "https://www.reuters.com/markets/"},
        {"name": "Reuters \u2014 Indian shares hold gains after RBI rate pause; rupee support measures in focus", "url": "https://www.reuters.com/markets/asia/"}
    ]),
    "body": """For weeks, the Indian rupee danced to the price of oil. Now it has a new partner to watch \u2014 the U.S. dollar \u2014 and the change of music will decide whether the currency's recent relief rally has legs.

## A Good Week, and Why

The rupee rose 0.8 percent last week to 94.32 against the dollar, its best weekly performance in 11 weeks. At one point it touched 94.18, its strongest level since early May. The trigger was a sharp drop in crude prices after a U.S.-brokered peace deal eased the West Asia conflict that had kept oil elevated and the rupee under strain.

For an economy that imports the bulk of its oil, cheaper crude is close to an unalloyed good: it narrows the trade deficit, cools imported inflation and relieves pressure on the currency. The war premium that had pushed the rupee toward record lows began to unwind, and for a few sessions the market could breathe.

## The Dollar Takes Over

That breathing room is now being squeezed from a different direction. The U.S. dollar index climbed 1.1 percent last week to its highest level in a year, and two-year Treasury yields rose after the Federal Reserve struck a more hawkish tone than markets expected on rates and inflation. Investors have begun pricing in the possibility that the Fed could actually raise rates later this year \u2014 a sharp reversal of earlier hopes for cuts.

A stronger dollar and higher U.S. yields are the rupee's natural adversaries: they pull global capital toward American assets and away from emerging markets like India. "Oil had been the dominant driver for the rupee for some time. Now, the dollar is back in focus, which means you have to pay attention to incoming U.S. data," said Kunal Kurani of Mecklai Financial. Traders will parse a run of American releases this week \u2014 durable-goods orders and the Fed's preferred inflation gauge, the PCE price index \u2014 for clues to the central bank's next move.

## Bonds Wait on Foreign Money

India's government bonds, meanwhile, are taking their cue from a different question: how quickly foreign investors return. The answer hinges on a package of measures New Delhi and the Reserve Bank of India unveiled this month to lure dollars back after a record exodus \u2014 more than $30 billion pulled from Indian equities so far in 2026.

Among the steps: longer-dated government bonds were opened to unfettered foreign access, caps and concentration limits on short-term debt investment were scrapped, and overseas investors were exempted from capital-gains tax on government securities. The RBI also offered discounted forex swaps to ease dollar funding and agreed to bear hedging costs for banks raising three-to-five-year deposits from non-resident Indians through September.

Analysts think the package could draw real money. Estimates cluster around $30 billion to $50 billion of inflows over the coming months, enough to help bridge a balance-of-payments gap projected for the next fiscal year and to support both the rupee and bond prices. But the consensus is also that it will take time: the changes must filter through to investors, who then have to act. No one expects an overnight surge.

## Why It Matters for NRIs

For the diaspora, none of this is academic. The rupee's level sets the exchange rate on every remittance home, the worth of NRE and FCNR balances, and the dollar value of Indian stocks and funds. A week that began with oil-driven relief and ended with dollar-driven pressure is, in effect, a live readout on the trade-offs NRIs face daily.

The practical lessons are familiar but freshly relevant. A weaker rupee stretches dollars sent home further, rewarding those who time transfers around bouts of rupee softness. The RBI's hedging support for NRI deposits is a direct, if modest, sweetener aimed squarely at diaspora savings. And the broader push to pull foreign capital back into Indian bonds is a bet that the country can steady its currency without choking growth.

The honest summary is that the rupee sits at a crossroads of forces no single headline controls \u2014 oil, the dollar, the Fed, and the pace of returning capital. For NRIs, the wise posture is the one that always serves in volatile currency weather: watch the level, avoid trying to call the bottom, and let long-term goals, not a single jittery week, drive the decision of when to move money across the border."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["healthy vegetables fruits whole grains plate", "fresh vegetables salad bowl healthy food", "vegetables fruit nuts dairy table"],
                          ["healthy diet vegetables plate", "fresh vegetables fruit bowl"], None),
    articles[1]["slug"]: (["blood test cholesterol laboratory sample", "doctor patient blood pressure check", "medical blood vials laboratory"],
                          ["cholesterol blood test medical", "doctor checking patient health"], None),
    articles[2]["slug"]: (["Indian rupee banknotes currency", "Reserve Bank of India building Mumbai", "Bombay Stock Exchange building Mumbai"],
                          ["indian rupee currency notes", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A Harvard-led study found the DASH eating pattern was the strongest dietary predictor of late-life cognitive health",
    articles[1]["slug"]: "A study of more than a million people linked genetically lower cholesterol to a sharply reduced risk of dementia",
    articles[2]["slug"]: "The rupee posted its best week in months as oil prices fell, before a resurgent dollar tested the gains",
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
