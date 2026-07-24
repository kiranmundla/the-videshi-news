#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-15 22:00 UTC batch.
Topics: Lean fatty liver (MASLD) in South Asians, Air pollution & dementia (UK Biobank),
        El Nino / monsoon deficit threat to India's economy.
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl2.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl2.bin"):
            with open("/tmp/_img_dl2.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl2.bin")
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
# ARTICLE 1: Lean fatty liver in South Asians (lifestyle-health)
# ============================================================
articles.append({
    "headline": "You Can Be Slim and Still Have a Dangerous Fatty Liver. For South Asians, the Standard Tests Often Miss It.",
    "subheadline": "Up to 45 per cent of fatty liver disease in Asian populations occurs in people of normal weight, and the lean form carries an equal or higher risk of death, cirrhosis and liver cancer than the obese kind. Worse, the blood-test scores doctors rely on to flag liver scarring were built on white patients \u2014 and a body of research shows they systematically under-detect damage in South Asians.",
    "slug": "lean-masld-fatty-liver-south-asians-fibrosis-tests-unreliable-thin-outside-fat-inside-20260615",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians develop fatty liver disease at normal body weights and lower BMIs than other groups, yet the non-invasive blood-score tests doctors use to screen for liver scarring were validated mainly on white patients and have been shown to miss advanced disease in South Asian patients \u2014 leaving many diaspora adults falsely reassured by a 'normal' result.",
    "sources": json.dumps([
        {"name": "BMJ Open Gastroenterology (non-invasive markers unreliable in South Asians)", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5050069/"},
        {"name": "mol-SHARE: adipocyte hypertrophy & fatty liver in South Asians (Diabetologia)", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"name": "Review: long-term outcomes of lean vs non-lean MASLD (PMC)", "url": "https://pmc.ncbi.nlm.nih.gov/"}
    ]),
    "body": """There is a comforting assumption baked into how most people think about fatty liver disease: it is a problem of the overweight. Shed the pounds, the logic goes, and the fat melts off the liver too. For the South Asian diaspora, that assumption is not just wrong \u2014 it is dangerous. A growing body of evidence shows that South Asians develop fatty liver at normal weights, that the lean form of the disease is at least as deadly as the obese form, and that the very tests doctors use to catch it tend to fail in South Asian patients.

The disease now has a clumsy new name \u2014 metabolic dysfunction-associated steatotic liver disease, or MASLD, the rebranding of what was long called non-alcoholic fatty liver disease (NAFLD). The name change matters less than the numbers. MASLD is the fastest-growing cause of chronic liver disease and liver cancer worldwide, and it affects roughly a third of all adults. What is less appreciated is how much of it hides in people who look perfectly healthy.

## Thin on the Outside, Fat on the Inside

Across global studies, lean individuals account for between 5 and 20 per cent of all fatty liver cases. In Asian cohorts, that figure climbs to around 45 per cent \u2014 nearly half. This is the "thin outside, fat inside" phenotype that researchers have repeatedly flagged in South Asians: a normal number on the bathroom scale concealing fat packed around the organs and inside the liver itself.

The biology behind it is now reasonably well understood. The mol-SHARE study, which compared healthy South Asians with white Caucasians, found that even after adjusting for age, sex and BMI, South Asians had markedly more liver fat, more visceral (deep abdominal) fat, less lean muscle mass, higher fasting insulin and lower levels of the protective hormone adiponectin. Their fat cells were physically larger and stored fat less efficiently, spilling it instead into the liver and other organs where it does the most metabolic harm. In short, the South Asian body tends to store fat in exactly the wrong places, and it begins doing so at weights that would never trigger concern under standard guidelines.

## The Lean Form Is Not the Mild Form

For years, lean fatty liver was quietly assumed to be the gentler version of the disease. The data say otherwise. Reviews of long-term outcomes find that people with lean MASLD face an equal or higher overall mortality rate than their overweight counterparts \u2014 one analysis put the increase at roughly 1.6-fold for all-cause death \u2014 along with elevated risks of advanced fibrosis, cirrhosis and hepatocellular carcinoma, the most common form of liver cancer.

This upends the conventional clinical paradigm. A patient who is not obese, whose weight and routine bloodwork look unremarkable, may nonetheless be carrying a liver quietly progressing toward irreversible scarring. The absence of obvious risk factors becomes its own risk: nobody thinks to look.

## The Tests That Fail South Asians

The most troubling piece concerns the tools doctors use to decide who needs further investigation. Because liver biopsy is invasive, clinicians rely on non-invasive scores \u2014 the NAFLD fibrosis score, the FIB-4 index, the APRI ratio and others \u2014 that combine routine blood markers and metabolic measures to estimate how much scarring a liver has accumulated.

The problem is that these scores were largely developed and validated in white populations. When researchers tested them against actual biopsy results in South Asian patients, they found the scores were significantly less sensitive at detecting advanced fibrosis. In one specialist-centre study, the relative likelihood of a correct diagnosis was nearly twice as high in white patients as in South Asians. South Asian patients in that study were younger and had lower BMIs and lower rates of obesity \u2014 yet comparable rates of diabetes and actual liver injury. The metabolic-based scores, in other words, were quietly missing real disease in precisely the people most prone to it. (One bright spot: transient elastography, the ultrasound-based "FibroScan," performed accurately across both groups.)

## What Diaspora Families Should Do

The practical takeaways are clear, and they cut against ingrained habits. First, a normal weight and a normal set of routine liver enzymes do not rule out fatty liver disease in a South Asian adult \u2014 especially in anyone with type 2 diabetes, a strong family history, or central weight carried around the waist. Second, if liver fat is suspected, ask specifically about imaging-based assessment such as a FibroScan rather than relying solely on calculated blood-score indices, which may falsely reassure. Third, the levers that work are the familiar ones, but they apply even to the slim: cutting refined carbohydrates and sugary drinks, building muscle through resistance training to offset the low lean mass South Asians tend to carry, limiting alcohol, and getting screened early rather than waiting for symptoms that often arrive only once damage is advanced.

The uncomfortable lesson is that for the South Asian diaspora, "I'm not overweight, so my liver is fine" is a sentence that has misled too many people for too long. The fat that matters most is the kind the mirror cannot show."""
})

# ============================================================
# ARTICLE 2: Air pollution & dementia (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Air Pollution Is Ageing the Brain and Driving Dementia. A Half-Million-Person Study Just Mapped How.",
    "subheadline": "Tracking 488,000 adults, researchers found that the most polluted air raised dementia risk by up to 20 per cent \u2014 and traced the mechanism to accelerated biological ageing and visible shrinkage of the brain. For a diaspora whose parents and relatives live in some of the world's dirtiest air, the findings move pollution from an abstract worry to a measurable threat to the mind.",
    "slug": "air-pollution-dementia-brain-aging-atrophy-uk-biobank-488000-study-diaspora-india-pm25-20260615",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many NRIs have aging parents and relatives living in Indian cities that rank among the most polluted on earth, and a major new study quantifying how fine-particle pollution accelerates brain aging and dementia risk turns a familiar background anxiety into concrete grounds for action \u2014 from air purifiers to relocation decisions.",
    "sources": json.dumps([
        {"name": "Journal of Nutrition, Health & Aging (UK Biobank cohort, 488,348 participants)", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"name": "Stroke / McMaster University (everyday pollution and cognition)", "url": "https://medicalxpress.com/news/2026-05-everyday-air-pollution-poorer-brain.html"},
        {"name": "NIH Research Matters (air pollution linked to dementia)", "url": "https://www.nih.gov/news-events/nih-research-matters"}
    ]),
    "body": """For decades, air pollution was filed away as a lung-and-heart problem \u2014 the cause of asthma attacks, bronchitis and heart disease, but surely not something that reached the brain. That comfortable separation is collapsing. A wave of large studies published this year has established that the fine particles we breathe do not stop at the lungs; they accelerate the ageing of the entire body and visibly shrink the brain, raising the risk of dementia. And the scale of the new evidence makes it hard to dismiss.

The most striking entry comes from an analysis of 488,348 adults in the UK Biobank, none of whom had dementia when the study began. Researchers tracked their exposure to a suite of pollutants \u2014 fine particulate matter known as PM2.5, larger PM10 particles, and the traffic gases nitrogen dioxide and nitrogen oxides \u2014 and followed who went on to develop dementia.

## The Numbers

The results were consistent and sobering. Compared with people breathing the cleanest air, those exposed to the highest levels faced meaningfully higher dementia risk: about 14 per cent higher for PM2.5, 9 per cent for PM10, and a striking 20 per cent higher for nitrogen dioxide, the gas that pours out of traffic and the burning of fossil fuels. These are not trivial increments spread across a population of hundreds of millions worldwide.

What sets this study apart is that it did not stop at the correlation. The researchers asked how pollution does its damage, and the answer points to two intertwined pathways. First, dirty air accelerates biological ageing \u2014 the gap between a person's chronological age and the older "biological age" their cells actually exhibit. Second, it is associated with shrinkage across global and regional brain structures, the kind of atrophy that precedes cognitive decline. Using statistical modelling, the team showed that accelerated ageing and brain shrinkage together help explain the link between foul air and dementia. Pollution, in effect, makes the brain old before its time.

## A Pattern, Not a Fluke

This is not one outlier study. A separate analysis of more than 317,000 UK Biobank participants found that particulate pollution and nitrogen dioxide were consistently tied to higher dementia risk, while access to green space appeared protective. Research out of McMaster University, published in the journal Stroke, found that even in Canada \u2014 a country with some of the cleanest air in the world \u2014 people in more polluted areas scored worse on tests of memory and mental speed and showed small but visible signs of brain damage on MRI scans, with the effect more pronounced in women. And NIH-funded work has identified pollution from agriculture and wildfire smoke as particularly tied to dementia cases.

The throughline is that there appears to be no safe threshold. Harm is showing up even at pollution levels considered low by international standards, which means the danger is not confined to a handful of notorious megacities.

## Why This Lands Differently for the Diaspora

For NRIs, this research is not academic. It collides directly with one of the diaspora's most common and emotionally fraught realities: aging parents who still live in India. Delhi, Mumbai, Kolkata and dozens of smaller Indian cities routinely record PM2.5 levels many times the World Health Organization's safe limit, especially in the winter months when crop burning and cooler air trap pollutants close to the ground. The figures that this study links to a 14 to 20 per cent rise in dementia risk are, in much of urban India, an ordinary day.

That reframes a familiar anxiety. The worry about a parent's cough or a relative's breathlessness has always been about the lungs. This research says the same air may also be eroding their memory and accelerating cognitive decline \u2014 a far more frightening prospect, and one that unfolds invisibly over years.

## What Can Actually Be Done

The findings are not a counsel of despair, because exposure is partly modifiable. Practical steps that the evidence supports include running high-quality HEPA air purifiers in the rooms where elderly relatives sleep and spend most of their time; tracking the local air quality index and keeping windows shut and outdoor activity limited on the worst days; wearing well-fitted N95-grade masks outdoors during severe episodes; and, where it is feasible, favouring greener, less traffic-choked neighbourhoods, since proximity to green space showed a protective signal in the data.

For families weighing bigger decisions \u2014 whether to move a parent to a cleaner city, or to sponsor relocation abroad \u2014 the dementia link adds a serious new variable to a calculation that used to centre on convenience and companionship. None of this is simple, and air purifiers are no substitute for clean air at the source. But the research delivers an unambiguous message: the air our families breathe is not just a respiratory matter. It is, increasingly, a question of how well their minds will age."""
})

# ============================================================
# ARTICLE 3: El Nino / monsoon deficit threat to India (markets-finance)
# ============================================================
articles.append({
    "headline": "El Ni\u00f1o Is Back, and India's Monsoon Has Started With a 26% Rain Deficit. Here Is What It Means for Markets and NRIs.",
    "subheadline": "Just as oil's crash and the rupee's rally lifted sentiment, a freshly declared El Ni\u00f1o and a weak start to the monsoon \u2014 rainfall ran 26 per cent below normal in early June \u2014 have introduced the one risk that could derail India's recovery: the rains that half its farmland depends on. For NRIs eyeing Indian equities and rupee-denominated deposits, the monsoon is now the variable to watch.",
    "slug": "el-nino-monsoon-deficit-26-percent-india-economy-rural-demand-inflation-nri-investor-20260615",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A weak monsoon directly threatens the rural demand, food inflation and rupee stability that underpin NRI investments and the purchasing power of remittances sent home \u2014 making this year's El Ni\u00f1o-shadowed season a concrete factor in diaspora financial decisions, from equity exposure to the timing of money transfers.",
    "sources": json.dumps([
        {"name": "Reuters (India monsoon slows, below-average rain seen)", "url": "https://www.reuters.com/world/india/"},
        {"name": "The Hindu BusinessLine / FAO (El Nino may hit India's monsoon)", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Mint (Climate Change and You: monsoon begins with 26% deficit)", "url": "https://www.livemint.com/"}
    ]),
    "body": """For the past week, the story in Indian markets has been relentlessly good. A US-Iran peace deal sent oil prices tumbling, the rupee bounced to a five-week high near 94.7 per dollar, and the Sensex and Nifty rallied around 3 per cent in two sessions. Investors who had spent the year watching foreign money flee finally had reasons to smile. But beneath the optimism, a quieter and far older risk has crept back onto the board \u2014 one that no peace treaty can fix. The monsoon has arrived weak, and El Ni\u00f1o is back.

## The Rains That Run the Economy

It is difficult to overstate how much rides on the June-to-September southwest monsoon. It delivers roughly 70 per cent of India's annual rainfall, recharges the reservoirs and groundwater the country lives on, and waters the nearly half of India's farmland that has no irrigation at all. About half the population still earns its livelihood from agriculture. When the rains are good, rural India spends \u2014 on tractors, two-wheelers, soap, packaged food and gold. When they fail, that demand evaporates, food prices spike, and the ripple reaches every corner of the economy.

This year the season has opened on the wrong foot. The monsoon made landfall in Kerala on June 4, a few days late, and then stalled. In the first ten days of June, India received rainfall 26.5 per cent below normal, as "western disturbances" from the Mediterranean slowed the system's advance. Central and northern regions \u2014 the country's crop belt \u2014 are forecast to see significantly below-normal rain over the following fortnight, threatening to delay the planting of summer-sown crops such as rice, cotton, soybeans and pulses.

## El Ni\u00f1o Raises the Stakes

The bigger shadow is El Ni\u00f1o, the Pacific warming pattern that has now officially begun and that historically weakens the Indian monsoon. The India Meteorological Department expects moderate-to-strong El Ni\u00f1o conditions to prevail through the season. The UN's Food and Agriculture Organization has warned that the pattern could put rainfed crops like rice and maize under stress across South Asia, and cautioned that a warmer planet could make this cycle more damaging than past ones. During the 2015-16 El Ni\u00f1o, India's maize output fell 4 per cent and rice production slipped 1 per cent.

There is a measure of cushion. The weather office's central forecast is for a roughly 10 per cent rainfall deficit, and India sits on plentiful stocks of rice and wheat, leaving it well placed to absorb a moderate 5-to-10 per cent shortfall. The government has also said fertiliser stocks are comfortable for the kharif sowing season, at 51 per cent of requirement versus a usual 33 per cent. The vulnerability lies elsewhere: pulses, oilseeds and vegetables, which are largely rainfed and prone to sharp price swings when the rains fall short. A hot, dry spell can send vegetable prices soaring \u2014 and food remains the most politically and economically sensitive component of Indian inflation.

## Why This Matters for the Markets

The monsoon sits at the intersection of nearly every variable NRIs care about. A poor season would stoke food inflation, complicate the Reserve Bank of India's room to support growth, dent the rural demand that drives a huge swathe of corporate earnings, and pressure the rupee just as it has begun to recover. Even the bullish voices on the Street hedge on this point: one chief executive forecasting a strong four-to-six-month run for Indian equities explicitly qualified it as conditional on "monsoon risks recede." In other words, the rally has priced in the good news on oil and the rupee \u2014 but not yet a bad monsoon.

The market impact is sector-specific. Consumer goods, two-wheeler, tractor and rural-facing lending stocks are the most exposed to a weak season, while a deficient monsoon tends to lift the fortunes of irrigation, agrochemical and, perversely, some fertiliser names. Gold, always a monsoon-and-inflation hedge in the Indian context, is another beneficiary when rural anxiety rises.

## The NRI Angle

For the diaspora, the monsoon translates into two concrete considerations. The first is investment: anyone adding to Indian equity exposure or weighing the much-discussed NSE IPO and the RBI's higher-yielding FCNR deposit window should treat the monsoon's progress through late June and July as a genuine risk factor, not background noise. A weak season could check the equity rally and reintroduce rupee volatility precisely as inflows were expected to return.

The second is more personal. Many NRIs send money to families in rural and semi-rural India, where a poor harvest hits household incomes directly. A deficient monsoon raises food costs and squeezes the very relatives those remittances support, which can change both the amount families send and the timing of transfers \u2014 a weaker rupee, after all, stretches each dollar further when sending money home.

The season runs to September, and its real shape will not be clear for weeks; the weather office expects the monsoon to gain momentum in the last week of June. Until then, the smart money is doing what Indian farmers have done for millennia: watching the sky."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["human liver anatomy medical", "fatty liver disease medical illustration", "liver ultrasound scan"],
                          ["liver health medical checkup", "abdominal ultrasound scan patient"]),
    articles[1]["slug"]: (["Delhi air pollution smog", "air pollution India city smog", "New Delhi smog skyline"],
                          ["city smog air pollution skyline", "air pollution haze traffic"]),
    articles[2]["slug"]: (["monsoon rain India agriculture", "India paddy field farmer monsoon", "monsoon clouds India farmland"],
                          ["monsoon rain rice paddy field", "indian farmer rice field rain"]),
}
img_captions = {
    articles[0]["slug"]: "A medical illustration of the human liver, the organ at the centre of South Asia's hidden fatty-liver epidemic",
    articles[1]["slug"]: "Smog blankets a city skyline, the kind of fine-particle pollution now tied to faster brain ageing and dementia",
    articles[2]["slug"]: "A farmer in a flooded paddy field during the monsoon, the rains that half of India's farmland depends on",
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
