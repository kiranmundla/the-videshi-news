#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 22:00 UTC batch.
Topics:
  1. Fish oil / high-dose omega-3 (DHA) FAILS to protect the ageing brain — a
     2-year, double-blind, placebo-controlled USC trial (eBioMedicine, Jun 18)
     in 365 at-risk adults: DHA reached the brain but did nothing for memory,
     cognition or hippocampal shrinkage — lifestyle-health
  2. A daily multivitamin (+ cocoa flavanols) modestly SLOWED biological ageing
     in ~958 older adults over 2 years on epigenetic "clocks" (COSMOS-Clock
     substudy) — context within wider diet/fitness longevity research
     — lifestyle-health
  3. RBI's FCNR(B) dollar-deposit drive: full hedging-cost subsidy till Sep 30,
     rate caps lifted, banks now seeking to fund deposits via GIFT City — a bid
     to pull tens of billions from the diaspora and steady the rupee
     — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621z.bin"):
            with open("/tmp/_img_dl0621z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621z.bin")
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
# ARTICLE 1: Fish oil / omega-3 fails to protect the brain (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Fish-Oil Pills Did Reach the Brain \u2014 but Did Nothing for Memory, a Two-Year Trial of At-Risk Adults Finds",
    "subheadline": "In a rigorous double-blind study, high doses of the omega-3 DHA clearly raised omega-3 levels in the brains of older adults at risk for Alzheimer's, yet brought no improvement in memory, thinking or the shrinkage of the brain's memory centre \u2014 a sobering result for a supplement Americans spend over a billion dollars a year on.",
    "slug": "omega-3-fish-oil-dha-no-cognitive-benefit-alzheimer-risk-usc-ebiomedicine-trial-diaspora-20260621-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Fish-oil capsules are a fixture of the diaspora medicine cabinet \u2014 reached for as cheap insurance for the brain, especially in largely vegetarian Indian households that eat little oily fish \u2014 so a gold-standard trial showing the pills do not protect memory is a pointed reminder for NRI families to spend on the lifestyle basics that do, rather than on a supplement that does not.",
    "sources": json.dumps([
        {"name": "eBioMedicine (The Lancet) \u2014 USC trial of high-dose DHA supplementation in adults at risk for Alzheimer's disease", "url": "https://www.thelancet.com/journals/ebiom/home"},
        {"name": "CNN Health \u2014 Taking an omega-3 supplement doesn't boost memory or cognition", "url": "https://www.cnn.com/2026/06/18/health/omega-3-fish-oil-algae-supplement-wellness"},
        {"name": "Medical Xpress \u2014 Fish oil supplements may not prevent Alzheimer's-related decline, clinical trial suggests", "url": "https://medicalxpress.com/news/2026-06-fish-oil-supplements-alzheimer-decline.html"}
    ]),
    "body": """Few supplements enjoy the easy goodwill of fish oil. Sold as cheap insurance for the heart and the brain, omega-3 capsules sit in millions of medicine cabinets, taken on the quiet faith that they keep the mind sharp into old age. A new clinical trial delivers an uncomfortable verdict: even when the omega-3 demonstrably reaches the brain, it does not appear to protect memory at all.

## A Carefully Built Test

The study, published on June 18 in the Lancet journal eBioMedicine and led by Dr. Hussein Yassine, director of the Center for Personalized Brain Health at the University of Southern California, was designed to give omega-3 its best possible shot. Researchers recruited 365 adults aged 55 to 80 who rarely ate fish and who carried at least one risk factor for dementia \u2014 obesity, a sedentary lifestyle, high blood pressure or high cholesterol. Nearly half carried the APOE4 gene, the strongest common genetic risk factor for late-onset Alzheimer's and the group thought most likely to benefit, because their brains struggle to process fats efficiently.

In this randomized, double-blind, placebo-controlled design \u2014 the gold standard of medical evidence \u2014 half the participants took 2,000 milligrams of docosahexaenoic acid (DHA), a key omega-3, every day for two years. The other half took a placebo. Both groups also took a B-vitamin complex. Crucially, the researchers did not simply assume the supplement worked; they checked.

## The Pill Worked. The Brain Did Not Improve.

It did reach its target. Omega-3 levels in red blood cells climbed from about 4.9 percent to 11 percent in those taking the supplement, and DHA in the cerebrospinal fluid that bathes the brain rose by an average of 17 percent after six months \u2014 confirming the nutrient had crossed into the brain, even in APOE4 carriers.

And yet, after two years, the people taking DHA did no better on memory and thinking tests than those on placebo. Brain scans told the same story: the supplement did not slow the shrinkage of the hippocampus, the brain's memory hub and a key marker of ageing and Alzheimer's risk, nor reduce cell loss in other Alzheimer's-related regions \u2014 regardless of APOE4 status.

"Despite biochemical target engagement, no differences in cognition or brain structure were observed over 24 months," the authors concluded. As Yassine put it, "We all wish there was a silver bullet for preventing Alzheimer's, but our findings showed that fish oil supplements do not appear to protect brain health."

## Why the Disconnect

The result deepens a long-running puzzle. Population studies have repeatedly found that people who eat oily fish tend to have healthier brains, and omega-3s genuinely help build the connections between brain cells. But trial after trial of omega-3 *supplements* has failed to translate that promise into measurable protection. The new study suggests the problem may not be getting omega-3 into the brain \u2014 that part worked \u2014 but how an ageing or already-compromised brain metabolises and uses it once it arrives. Yassine's team is now turning to that question.

There are caveats. The trial ran for two years, and dementia develops over decades; a longer or earlier intervention might read differently. The participants already had low omega-3 levels and elevated risk, so the findings may not generalise to everyone. And none of this argues against eating fish, which delivers omega-3s alongside a whole package of nutrients in a form the body handles differently from a capsule.

The deeper message from the researchers was about where to put one's faith. "Staying healthy throughout life remains the most powerful tool we have for reducing Alzheimer's risk \u2014 including regular exercise, quality sleep, and a balanced diet," Yassine said, likening brain care to routine maintenance on a car engine. The supplement, by contrast, looked like "a drop in the ocean."

## Why It Matters for the Diaspora

For Indian families abroad, fish oil occupies a particular place. It is among the most commonly bought supplements in diaspora households, often taken precisely because so many Indians are vegetarian or eat little of the oily fish \u2014 salmon, mackerel, sardines \u2014 that omega-3 guidance is built around. The capsule becomes a stand-in, a tidy purchase that feels like caring for an ageing parent's mind or one's own.

This trial should reset that calculation. It does not say omega-3 is harmful, and for those with genuinely low levels there may be other reasons to consider it. But it is a clear signal that the pill is not a shortcut to a protected brain, and that money and hope poured into supplements may be better spent elsewhere. The interventions with real evidence behind them are the unglamorous ones the diaspora already knows: daily movement, decent sleep, controlling blood pressure and blood sugar, and a plate heavy on vegetables, whole grains and \u2014 for those who eat it \u2014 actual fish rather than a soft-gel substitute. For a community carrying an outsized burden of diabetes and heart disease, both of which feed dementia risk, that is where the leverage truly lies."""
})

# ============================================================
# ARTICLE 2: Multivitamin modestly slows biological ageing (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Daily Multivitamin Modestly Slowed the Body's Biological Clock in a Two-Year Trial \u2014 but the Effect Was Small",
    "subheadline": "Using 'epigenetic clocks' that read the chemical wear on DNA, researchers found older adults who took a daily multivitamin with cocoa flavanols for two years aged slightly more slowly at the cellular level than those on a placebo \u2014 a tantalising but modest result that sits alongside stronger evidence for diet and fitness.",
    "slug": "daily-multivitamin-cocoa-flavanols-epigenetic-clock-biological-aging-cosmos-substudy-diaspora-20260621-2200",
    "category": "lifestyle-health",
    "vertical": "longevity",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Multivitamins are a staple of NRI households \u2014 mailed to students abroad and pressed on ageing parents \u2014 so evidence that the pills nudge biological ageing only modestly, while diet and fitness move it far more, helps the diaspora spend its health budget where the returns are largest rather than on a daily tablet alone.",
    "sources": json.dumps([
        {"name": "Healthline \u2014 3 Studies Link Diet, Fitness, Multivitamins to Slower Aging", "url": "https://www.healthline.com/health-news/diet-fitness-multivitamins-slower-aging"},
        {"name": "Brigham and Women's Hospital / COSMOS trial \u2014 multivitamins, cocoa flavanols and epigenetic ageing", "url": "https://www.brighamandwomens.org/"},
        {"name": "Aging Cell \u2014 short-term dietary changes and biological age in older adults", "url": "https://onlinelibrary.wiley.com/journal/14749726"}
    ]),
    "body": """The dream of a pill that slows ageing is as old as medicine, and rarely closer than in a marketing brochure. So when researchers reported that a humble daily multivitamin appeared to nudge the body's biological clock, it was worth a closer, sceptical look. The finding is real \u2014 but the size of the effect, and the company it keeps, matter just as much as the headline.

## Reading the Body's True Age

The work centres on a distinction that has reshaped ageing science: the gap between chronological age, the years since you were born, and biological age, the actual wear and tear accumulating in your cells. Scientists now estimate biological age using "epigenetic clocks," tools that measure chemical tags on DNA \u2014 patterns of methylation that shift in predictable ways as the body ages. When biological age runs ahead of chronological age, it signals faster ageing and, on average, a higher risk of disease and earlier death.

In a substudy drawing on the large COSMOS trial, researchers followed 958 older adults for two years. Participants took either a daily Centrum Silver multivitamin combined with 500 milligrams of cocoa flavanols \u2014 plant compounds found in cocoa \u2014 or a placebo. At the end, those on the active supplement showed slightly slower biological ageing on the epigenetic clocks than the placebo group.

## A Real but Modest Signal

The crucial word is *slightly*. This was not a fountain of youth; it was a small, measurable slowing of a cellular process, detectable across a large group over two years. Such effects can be statistically genuine while remaining modest for any single individual, and it is not yet clear whether a small shift on an epigenetic clock translates into a longer, healthier life. Epigenetic clocks are powerful research tools, but they are still being validated as predictors of real-world outcomes, and a flattering reading on one does not guarantee more good years.

The supplement finding also did not arrive alone. It is part of a cluster of recent research mapping how everyday choices shape the pace of ageing, and the other pieces point to stronger levers. Studies have linked higher midlife cardiorespiratory fitness \u2014 the kind built by regular aerobic exercise \u2014 to a longer lifespan and a slower onset of heart disease, diabetes and stroke. And work published in the journal Aging Cell suggested that even short-term dietary changes, particularly shifting toward a diet rich in plant-based foods, can narrow the gap between biological and chronological age in older adults.

"Although everyone ages over time, there may be simple ways to delay the aging process and help us live not only longer but also better," said Dr. Sidong Li, a postdoctoral researcher at Brigham and Women's Hospital in Boston, summarising the broader hope behind this line of research.

## How to Read It Sensibly

The honest takeaway is one of proportion. A daily multivitamin appears to do a little, and it is generally safe and inexpensive, so for those with genuine dietary gaps it is a reasonable, low-stakes choice. But the larger and more reliable gains in slowing biological ageing come from the parts of life that are harder to bottle: moving the body regularly, building cardiovascular fitness, and eating a diet built around vegetables, fruit, whole grains and legumes rather than refined and ultra-processed foods.

A supplement, in other words, is a supplement \u2014 a top-up, not a substitute for the foundations. The most striking thread across these studies is not that any single pill is magic, but that biological ageing is more malleable than once believed, and that ordinary habits can measurably shift it.

## Why It Matters for the Diaspora

In diaspora homes, the multivitamin is almost a cultural object. Bottles are mailed to students starting university abroad, pressed into the hands of visiting relatives, and lined up on the kitchen counters of ageing parents as a daily act of care. The instinct is loving and not wrong \u2014 but this research is a useful corrective to the idea that the tablet is doing the heavy lifting.

For a community with high rates of diabetes, heart disease and vitamin D and B12 deficiencies, targeted supplementation has a real place, ideally guided by a doctor and a blood test rather than habit. Yet the evidence keeps pointing the same way: the largest returns on a family's health come from fitness and food, not from the supplement aisle. For NRI families weighing where to invest time, attention and money in their parents' and their own longevity, the message is to treat the multivitamin as the small bonus it appears to be \u2014 and to put the real effort into the walking shoes, the kitchen and the gym, where the biological clock seems to move the most."""
})

# ============================================================
# ARTICLE 3: RBI FCNR(B) dollar-deposit drive & GIFT City (markets-finance)
# ============================================================
articles.append({
    "headline": "India Is Dangling Higher Dollar Rates to Pull NRI Money Home \u2014 and Banks Now Want to Route It Through GIFT City",
    "subheadline": "After the RBI agreed to absorb the hedging cost on fresh foreign-currency NRI deposits and scrapped the rate caps, banks have pushed dollar deposit rates to 6\u20137 percent and are seeking permission to fund the inflows through their offshore GIFT City units \u2014 part of a drive analysts think could draw $55 billion or more to steady the rupee.",
    "slug": "rbi-fcnr-b-dollar-deposit-scheme-hedging-subsidy-gift-city-nri-inflows-rupee-nri-investor-20260621-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This drive is aimed squarely at the diaspora's wallet: NRIs can suddenly earn 6\u20137 percent on dollar deposits in Indian banks \u2014 nearly double the old rates and with no currency risk \u2014 making it one of the most consequential personal-finance shifts for overseas Indians in years.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian banks push for lending via GIFT City units in dollar deposit scheme, sources say", "url": "https://www.reuters.com/world/india/indian-banks-push-lending-via-gift-city-units-dollar-deposit-scheme-sources-say-2026-06-19/"},
        {"name": "The Hindu BusinessLine \u2014 RBI seeks daily data from banks under its limited period measures to attract foreign capital", "url": "https://www.thehindubusinessline.com/money-and-banking/"},
        {"name": "Outlook Business \u2014 Why NRIs are rushing to break old deposits and reinvest at higher rates", "url": "https://www.outlookbusiness.com/"}
    ]),
    "body": """India wants the diaspora's dollars, and it is paying handsomely to get them. In a series of moves over the past few weeks, the Reserve Bank of India has rewired the economics of non-resident deposits to make parking foreign currency in an Indian bank far more lucrative than it has been in years \u2014 and the banking system is now scrambling to build the plumbing to handle the expected flood.

## What the RBI Has Done

The centrepiece, announced on June 5, is deceptively technical but powerful. The RBI has agreed to bear the full cost of currency hedging \u2014 through a concessional foreign-exchange swap window \u2014 on fresh Foreign Currency Non-Resident (Bank), or FCNR(B), deposits with tenures of three to five years, mobilised up to September 30, 2026. Hedging is normally a major expense for banks taking in dollars, and shifting that cost onto the central bank lets lenders pass the savings straight to depositors.

The RBI went further on June 17, temporarily scrapping the interest-rate ceilings on fresh FCNR(B) deposits of three to five years and on Non-Resident External (NRE) deposits of three years and above, again until the end of September. It also exempted the new FCNR(B) deposits from the cash reserve ratio and statutory liquidity ratio \u2014 the slices of deposits banks must normally set aside \u2014 so lenders can deploy the entire sum as loans.

The result has been immediate. Banks have lifted interest rates on three-to-five-year FCNR(B) dollar deposits to roughly 6 to 7.1 percent, up from the 3 to 4 percent on offer earlier. For a non-resident Indian, that is close to a doubling of the return \u2014 earned in dollars, with no exposure to a sliding rupee.

## The GIFT City Twist

Now the banks want to take it a step further. According to Reuters, lenders are seeking the RBI's permission to fund these dollar deposits through their branches in Gujarat International Finance Tec-City \u2014 GIFT City \u2014 India's tax-neutral financial hub, whose units operate under offshore banking rules. The mechanics echo a scheme last used in 2013: banks lend to a customer, who then parks the borrowed money in a dollar deposit, amplifying the inflow.

Banks argue their GIFT City units function much like foreign banks and should be allowed to provide such funding. "Most banks have branches in GIFT City, but many of them do not have a presence in foreign countries. If the leverage is not allowed through GIFT, these banks will have to depend on foreign lenders," said VRC Reddy, treasury head at Karur Vysya Bank. The RBI has not commented, and it remains unclear whether existing rules on leverage extend to these offshore branches.

The central bank is watching the flows closely. It has ordered banks to submit *daily* data on FCNR(B) deposits, external commercial borrowings and overseas foreign-currency borrowings raised under the new measures \u2014 a sign of how seriously it is tracking the response.

## Why India Is Doing This Now

The backdrop is a rupee under strain and a year of heavy foreign outflows from Indian stocks. By drawing in a large, relatively stable pool of foreign currency from the diaspora, the RBI can shore up its reserves and steady the currency without simply burning through dollars in the open market. It is a page from the 2013 playbook, when a similar swap window helped lift total NRI deposits from $71 billion to $127 billion over three years.

The stakes are sizeable. Total NRI deposits have stalled at about $166 billion, growing far more slowly than overall bank deposits. Brokerage Nomura estimates the new scheme could pull in around $55 billion, with the bulk arriving in August and September; some industry estimates run as high as $60\u201370 billion. "Compared to 2013, while U.S. dollar rates are much higher, the scheme will also provide leverage to investors, which will boost returns," Nomura wrote.

## Why It Matters for NRIs

For the diaspora, this is not abstract macroeconomics \u2014 it is a rare, time-limited opportunity sitting in plain sight. An NRI can now lock in 6 to 7 percent on a multi-year dollar deposit in an Indian bank, with the interest tax-free in India and no currency risk, since both the principal and the return stay in dollars. Against the backdrop of what banks are offering on dollar savings elsewhere, that is an unusually generous rate.

The catch is that the sweetened terms apply only to *fresh* deposits and renewals booked during the window, which closes on September 30. Existing FCNR(B) holders are stuck on their older, lower contracted rates \u2014 which is exactly why some large depositors are already asking banks whether they can break and rebook, and why banks are seeking clarity from the RBI on whether that is allowed.

For overseas Indians weighing where to hold their dollar savings \u2014 and for those who periodically debate moving money home \u2014 the next three months offer a genuinely better deal than the recent norm. As always, the fine print matters: tenure lock-ins, the specific bank's stability, premature-withdrawal rules, and how the interest is taxed in one's country of residence. But the broad signal is clear. India has rolled out the red carpet for the diaspora's dollars, and it has put a clock on the offer."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["fish oil omega 3 capsules supplement", "fish oil softgel pills", "salmon fish omega 3 food"],
                          ["fish oil capsules supplement", "omega 3 softgel pills"], None),
    articles[1]["slug"]: (["multivitamin tablets pills bottle", "vitamin supplement pills assorted", "dietary supplement capsules"],
                          ["multivitamin pills supplement", "vitamin tablets bottle"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee US dollar currency", "GIFT City Gandhinagar Gujarat building"],
                          ["us dollar indian rupee currency exchange", "dollar bank deposit money finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A two-year trial found high-dose omega-3 DHA reached the brain but did not improve memory in adults at risk for Alzheimer's",
    articles[1]["slug"]: "A two-year trial linked a daily multivitamin with cocoa flavanols to a modest slowing of biological ageing on epigenetic clocks",
    articles[2]["slug"]: "The Reserve Bank of India has sweetened terms on foreign-currency NRI deposits to draw the diaspora's dollars and steady the rupee",
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
