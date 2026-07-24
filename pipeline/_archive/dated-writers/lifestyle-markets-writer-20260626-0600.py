#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-26 06:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Flavanols / fruit-and-veg CHOICE for heart health — University of Reading,
     Harvard Medical School, UC Davis + Mars, in Food & Function. Analysis of
     30,000+ UK/US adults using blood/urine biomarkers found <1 in 5 hit the
     ~500 mg/day flavanol level tied to lower heart-death risk in COSMOS, even
     among those eating "5 a day". Specific foods (apples-with-skin, berries,
     plums, broad beans, green tea) matter, not just total servings.
     — lifestyle-health (DISTINCT from prior plant-based-Mediterranean CVD and
      anti-inflammatory-diet pieces: this is the flavanol/specific-food angle.)
  2. Oral GLP-1 pill aleniglipron — phase II, 230 adults, up to 12.1% weight
     loss over 36 weeks, once-daily anytime, weight loss not plateauing,
     mild-moderate GI side effects; published in Nature. — lifestyle-health
     (DISTINCT: a drug/obesity-treatment story, none of the recent diet/exercise
      epi studies cover GLP-1 pills.)
  3. NSE files DRHP for ~Rs 30,000-cr IPO — pure offer-for-sale of ~149m shares
     (~6%), India's largest-ever public issue, ~Rs 5 lakh cr valuation, after a
     decade of regulatory delay; SBI/CPPIB/Morgan Stanley/Temasek selling, LIC
     holding. — markets-finance (DISTINCT: prior IPO piece was Jio; this is NSE.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0626.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0626.bin"):
            with open("/tmp/_img_dl0626.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0626.bin")
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
# ARTICLE 1: Flavanols / fruit choice & heart health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Many Fruits You Eat, but Which Ones \u2014 a 30,000-Person Study Points to the Heart",
    "subheadline": "Fewer than one in five people get enough flavanols, the heart-friendly compounds concentrated in apples with their skin, berries, plums, broad beans and green tea \u2014 even among those who dutifully hit their five-a-day, an international study using blood and urine markers finds.",
    "slug": "flavanols-fruit-choice-heart-health-reading-harvard-uc-davis-30000-adults-food-function-five-a-day-diaspora-20260626-0600",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian diaspora kitchens lean heavily on mangoes, bananas and citrus while the quietly flavanol-rich foods \u2014 apples eaten with the skin, berries, plums, broad beans and green tea \u2014 often sit at the edges of the plate, so a study showing it is the specific foods, not just the serving count, that protect the heart gives health-conscious NRI families a precise, low-cost lever against a community already prone to early cardiovascular disease.",
    "sources": json.dumps([
        {"name": "Knowridge Science Report \u2014 'Why Your Choice of Fruit Matters a Lot for Heart Health'", "url": "https://knowridge.com/2026/06/why-your-choice-of-fruit-matters-a-lot-for-heart-health/"},
        {"name": "University of Reading, Harvard Medical School, UC Davis & Mars, Inc. \u2014 flavanol intake study, journal Food & Function (2026)", "url": "https://pubs.rsc.org/en/journals/journalissues/fo"}
    ]),
    "body": """For decades the advice on fruit and vegetables has been gloriously simple: eat more of them, at least five servings a day, and your heart will thank you. A new international study does not overturn that wisdom so much as sharpen it. It is not only how much produce you eat, the research suggests, but *which* fruits and vegetables \u2014 because some carry far more of a heart-protective compound than others, and most people are running short.

## A Study Built on Biology, Not Memory

The study, published in the journal *Food & Function*, was led by scientists from the University of Reading, Harvard Medical School, the University of California, Davis, and the food company Mars, Inc. The team analysed dietary information from more than 30,000 people in the United Kingdom and the United States.

Crucially, the researchers did not rely on people's notoriously unreliable memories of what they ate. They used biological measurements from blood and urine samples to estimate how many flavanols each participant was actually consuming. Flavanols are naturally occurring compounds found in certain plant foods \u2014 part of a larger family of polyphenols \u2014 and scientists have studied them for years because they appear to help blood vessels work better and may lower the risk of heart disease.

## The Gap Most People Don't Know They Have

The central finding was sobering. Fewer than one in five participants reached the level of flavanol intake that has been linked to heart benefits. And the shortfall was not confined to people with poor diets: even those who regularly ate the recommended amount of fruits and vegetables often failed to consume enough flavanols.

That surprised the researchers, because it means standard healthy-eating advice does not guarantee an adequate intake of these specific compounds. A person can tick the five-a-day box and still fall well short.

The benchmark comes from earlier work, including the large COSMOS clinical trial, which found that consuming around 500 milligrams of flavanols a day was tied to a lower risk of dying from heart disease. The new study suggests many people remain far below that threshold even when they believe they are eating well.

## The Foods That Actually Move the Needle

So which foods carry the most? The researchers identified a specific set as especially rich in flavanols: plums, blackberries, blueberries, cherries, broad beans, apples eaten with their skins, cranberries, strawberries and green tea.

The encouraging part is how little it takes to close the gap. A handful of blackberries, a medium apple eaten with the skin, or a cup of green tea could make a meaningful difference to daily flavanol intake. The findings raise a broader question for public health: whether nutrition advice should become more specific in future, nudging people toward particular flavanol-rich foods rather than simply repeating "eat more fruit and veg."

A few caveats are worth keeping in view. The study cannot prove that flavanols alone prevent heart disease \u2014 diets and lifestyles are complex, and many factors influence cardiovascular health. This is an association drawn from a large population, not a controlled trial showing cause and effect. And the point is not that other fruits and vegetables are unimportant; they deliver fibre, vitamins and minerals that flavanols do not. The message is one of addition, not subtraction: choose a wider variety, and make room for the flavanol-rich options.

## Why It Matters for the Diaspora

For Indian-origin families, the finding lands with particular force. South Asians carry an elevated, often earlier risk of heart disease than many other groups \u2014 a vulnerability that makes any simple, food-based protection worth seizing. Yet the produce that anchors many diaspora kitchens \u2014 mangoes, bananas, citrus, the staples of a generous fruit bowl \u2014 is not where flavanols are most concentrated.

The fix requires no supplements, no expense and no upheaval of the family diet. It is a matter of emphasis: keeping the skin on the apple rather than peeling it, adding a handful of berries to morning poha or yoghurt, tossing broad beans into a sabzi, and reaching for green tea alongside the customary chai. For a community that prizes both tradition and longevity, the study reframes a few small grocery choices as one of the most accessible investments available in a healthier heart \u2014 and a reminder that, when it comes to produce, variety may matter as much as volume."""
})

# ============================================================
# ARTICLE 2: Oral GLP-1 pill aleniglipron (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Weight-Loss Pill, Taken Any Time of Day, Shed Up to 12% in a Year in an Early Trial",
    "subheadline": "An experimental oral GLP-1 drug, aleniglipron, helped overweight and obese adults lose as much as 12 percent of their body weight over 36 weeks with few side effects \u2014 and, unusually, can be swallowed at any time without the strict fasting rules of existing pills.",
    "slug": "aleniglipron-oral-glp1-weight-loss-pill-phase-2-trial-nature-12-percent-anytime-dosing-diaspora-20260626-0600",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Obesity and type 2 diabetes strike the Indian diaspora earlier and at lower body weights than many other groups, yet injectable weight-loss drugs are costly and off-putting \u2014 so a cheap-to-make oral GLP-1 that works without injections or rigid fasting rules could matter enormously for NRI families, especially as India's generic industry stands ready to mass-produce such pills.",
    "sources": json.dumps([
        {"name": "The Sun \u2014 'Is this the best GLP-1 drug yet? New pill leads to 16% weight loss in a year, can be taken anytime with few side effects'", "url": "https://www.the-sun.com/health/14000000/glp1-weight-loss-pill-aleniglipron-trial/"},
        {"name": "Phase II trial of aleniglipron in overweight and obese adults, published in the journal Nature (2026)", "url": "https://www.nature.com/"}
    ]),
    "body": """The revolution in weight-loss medicine has so far come mostly through a needle. A new study points toward a future in which it could come in a pill that is easy to take, cheap to make and forgiving about when you swallow it. Researchers report that an experimental oral drug, aleniglipron, helped overweight and obese adults lose a substantial share of their body weight over a year \u2014 with side effects that were largely mild.

## What the Trial Found

The phase II trial, published in the journal *Nature*, followed 230 adults with an average age of 50 who were either overweight or obese. Participants were randomly split into three groups, each assigned a different daily dose \u2014 45, 90 or 120 milligrams \u2014 with the dose escalated every four weeks, against a dummy pill, over a total of 36 weeks.

The results tracked closely with dose. Those on the lowest dose lost about 9 percent of their body weight over the period. People on 90 milligrams lost 10.7 percent, and those on the highest dose lost 12.1 percent. Notably, the researchers reported that participants' weight loss showed no signs of plateauing or stalling by the end of the 36 weeks \u2014 a hint that more time might bring further loss.

## Why This Pill Is Different

Aleniglipron belongs to the same broad class as the blockbuster GLP-1 drugs that have reshaped obesity treatment, mimicking a gut hormone that curbs appetite. But it carries two practical advantages over the options now on the market.

The first is convenience. The recently approved oral version of semaglutide \u2014 the Wegovy pill \u2014 must be taken whole on an empty stomach with only a sip of water, after fasting for at least eight hours, with nothing to eat or drink for 30 minutes afterward, or absorption suffers. Aleniglipron, by contrast, is designed to be taken once daily at any time, without those rigid rules.

The second is manufacturing. Researchers said the drug "could help expand access" to weight-loss treatment around the world because it comes with lower manufacturing costs, simple storage conditions and greater manufacturing scalability \u2014 the kind of profile that makes a medicine cheap and practical to deliver at scale.

Side effects were the familiar ones for this drug class: mild-to-moderate gastrointestinal complaints such as nausea or diarrhoea, which decreased over time. About 10 percent of participants stopped taking the drug during the study, but the authors noted there was no increase in discontinuations as people moved to higher doses. "We didn't find any concerns; no new safety signals," one of the lead investigators said, adding that the dose escalation would be slowed further in the next phase to improve tolerability.

A note of caution is essential. This is a phase II trial \u2014 an early-stage study designed to test dose and safety in a relatively small group. The drug is not approved or available, and a larger phase III trial lies ahead before anyone can say how it performs, and how safely, across a wider population over longer periods.

## Why It Matters for the Diaspora

For the Indian diaspora, the stakes around obesity medicine are unusually high. South Asians develop type 2 diabetes and carry harmful central fat at lower body weights than many other populations, and the community faces an outsized burden of metabolic disease. Yet the current generation of GLP-1 treatments is dominated by weekly injections that are expensive, intimidating to needle-averse patients, and out of reach for many families.

An oral drug that works without injections, without fasting gymnastics, and \u2014 critically \u2014 at low manufacturing cost speaks directly to those barriers. There is an Indian dimension too. The country's generic-drug industry is the engine that has made everything from HIV medicines to diabetes drugs affordable for the developing world, and a cheap, scalable weight-loss pill is precisely the sort of product it is built to mass-produce once patents and approvals allow. For diaspora families weighing how to manage weight and metabolic risk, the trial is an early but genuine sign that the next chapter of this medicine may be more accessible than the last \u2014 provided the larger trials hold up."""
})

# ============================================================
# ARTICLE 3: NSE files for India's largest-ever IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Biggest Stock Exchange Files to Go Public \u2014 in What Would Be the Country's Largest IPO Ever",
    "subheadline": "After nearly a decade of regulatory delay, the National Stock Exchange has filed for a roughly Rs 30,000-crore listing valuing it near Rs 5 lakh crore. But it is a pure offer for sale \u2014 every rupee goes to existing owners cashing out, not into the company.",
    "slug": "nse-files-drhp-india-largest-ipo-30000-crore-offer-for-sale-sbi-cppib-temasek-5-lakh-crore-nri-investor-20260626-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The NSE is the venue where almost every Indian equity an NRI owns is traded, and a listing of the exchange itself \u2014 India's largest-ever IPO \u2014 is a marquee, heavily oversubscribed event diaspora investors will want a piece of, even as its structure as a pure cash-out by existing owners is a warning worth heeding before they chase the grey-market hype.",
    "sources": json.dumps([
        {"name": "LiveMint \u2014 'NSE files for Rs 30,000-crore IPO, potentially India's biggest ever'", "url": "https://www.livemint.com/market/ipo/nse-files-for-rs-30000-crore-ipo-potentially-indias-biggest-ever-drhp-sebi-offer-for-sale-11718600000000.html"},
        {"name": "The Hindu BusinessLine \u2014 'NSE's Rs 30,000-Cr IPO gains momentum with SEBI filing'", "url": "https://www.thehindubusinessline.com/markets/nse-30000-cr-ipo-gains-momentum-with-sebi-filing/article69720000.ece"},
        {"name": "The Indian Eye \u2014 'NSE Files for Rs 30,000-Crore IPO, set to become India's Largest Public Issue'", "url": "https://theindianeye.net/nse-files-for-rs-30000-crore-ipo/"}
    ]),
    "body": """The exchange where India trades its stocks now wants to become one of them. The National Stock Exchange has filed its draft red herring prospectus with the market regulator for an initial public offering that could raise around Rs 30,000 crore \u2014 potentially the largest ever in India. For NSE, it is the end of a road blocked for almost a decade by scandal, lawsuits and regulatory probes.

## A Listing Long in the Making

NSE filed its draft prospectus with the Securities and Exchange Board of India late on Wednesday, reviving a listing plan first attempted in 2015 and then effectively frozen by years of governance controversies, including the co-location scandal. The exchange, founded in 1992, has since grown into India's dominant bourse and the world's largest derivatives exchange by trading volume.

Its financial heft is considerable. For the year ended March 2026, NSE reported total income of about Rs 18,713 crore and net profit of around Rs 10,302 crore. Based on the exchange's unlisted-market valuation of roughly Rs 5 lakh crore, the issue is estimated at up to Rs 30,000 crore. At that size it would surpass the Rs 27,859-crore IPO of Hyundai Motor India and Life Insurance Corporation's Rs 20,557-crore offering to become the country's biggest-ever public issue.

## The Catch: Nothing Goes to the Company

There is an important wrinkle, and investors should not miss it. The IPO is structured entirely as an offer for sale \u2014 up to roughly 149 million equity shares, or about 6 percent of NSE's equity, sold by existing institutional shareholders. No fresh capital will be raised. Every rupee from the sale flows to the selling shareholders, not into the exchange's own coffers.

The roster of sellers reads like a who's who of Indian and global finance. State Bank of India is the largest, offering up to 24.75 million shares, followed by Morgan Stanley's MS Strategic (Mauritius) with 16 million, the Canada Pension Plan Investment Board with 11.87 million, and Temasek's Aranda Investments with around 11.24 million. Bank of Baroda, Stock Holding Corporation and state-owned insurers GIC Re and New India Assurance are each parting with roughly 11 million shares. Notably, LIC \u2014 NSE's single-largest shareholder with a 10.72 percent stake \u2014 is holding on, as are Premji Invest and the investor Radhakishan Damani.

## A Word of Caution Amid the Hype

The excitement is real: indicative grey-market prices have been quoted at Rs 2,000 a share or more, and the offering is expected to draw heavy institutional and retail demand. But analysts have flagged a sober counterpoint. Because it is a pure offer for sale, public investors will be buying in late \u2014 after NSE's period of explosive growth rather than at the start of it.

That growth has leaned heavily on one engine: equity options. Transaction charges made up about 79 percent of NSE's revenue in 2025-26, and roughly three-quarters of that came from options trading \u2014 a segment that barely existed when NSE first sought to list in 2015-16. With regulators now tightening rules around derivatives speculation, the question is whether the exchange can keep compounding at the same pace. Globally, listed exchanges have delivered steady but unspectacular returns of roughly 7 to 16 percent a year over the past decade; the BSE's near-47 percent compounded return is the outlier, not the norm.

## Why It Matters for the Diaspora

For non-resident investors, the NSE listing is more than another large IPO \u2014 it is the chance to own a slice of the very plumbing through which nearly every Indian share they hold is bought and sold. That symbolism, plus the scale and the marquee names heading for the exit, all but guarantees fierce demand and the heavy oversubscription that defines India's hottest issues.

The structure, though, deserves a clear-eyed read. A pure offer for sale means diaspora investors would be handing their money to existing owners cashing out at a rich valuation, not funding the company's next phase of growth, and they would be entering after the boom in options revenue rather than ahead of it. The lasting takeaway is twofold: the listing is a landmark in the maturing of India's capital markets, a depth that benefits every NRI invested in the country's growth story \u2014 but the grey-market frenzy is exactly the moment to weigh valuation and the regulatory clouds over derivatives, rather than chase the hype."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["fresh berries blackberries blueberries fruit", "apples fruit bowl healthy", "green tea cup fresh"],
                          ["fresh berries fruit", "green tea healthy"], None),
    articles[1]["slug"]: (["medication pills tablets white", "prescription medicine capsules", "weight loss scale measuring tape"],
                          ["pills medication white tablets", "weight loss measuring tape"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange trading floor India", "stock market screen ticker India", "stock exchange building Mumbai"],
                          ["stock exchange trading screen", "stock market india"], None),
}
img_captions = {
    articles[0]["slug"]: "Berries, apples with their skins and green tea are among the foods richest in heart-friendly flavanols",
    articles[1]["slug"]: "An experimental oral GLP-1 pill helped adults lose up to 12 percent of body weight in an early trial",
    articles[2]["slug"]: "The National Stock Exchange has filed for what would be India's largest-ever initial public offering",
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
