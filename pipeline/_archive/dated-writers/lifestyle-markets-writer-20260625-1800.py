#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 18:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. University of Arizona / USC study (Alzheimer's & Dementia, 23,000+ adults) —
     three sleep behaviours (sleeping outside 7-9h range, frequent daytime napping,
     sleeplessness) linked to greater white-matter-lesion volume = marker of brain
     aging years later. — lifestyle-health
     (Distinct from recent adolescent-sleep, subjective-age, and AQP4-gene pieces:
      this is white-matter brain-aging in a 23k-adult MRI cohort.)
  2. University of Toronto study (Radiology, June 2026, 11,000+ adults) — long-term
     air pollution at levels near/below regulatory safe limits linked to more advanced
     coronary artery disease; women +81% risk; +23% odds of heart disease per pollution
     increment. — lifestyle-health (Distinct: environmental cardiology, not diet/exercise.)
  3. RBI FCNR(B) hedging-cost subsidy (announced June 5, clarified June 23) — central
     bank absorbs full FX hedging cost on fresh 3-5yr FCNR(B) deposits till Sep 30;
     banks now offering ~6-7%, leverage via GIFT City could push returns to 12-15%;
     Nomura sees $55bn inflows, Axis up to $100bn. — markets-finance (diaspora core)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800z.bin"):
            with open("/tmp/_img_dl1800z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800z.bin")
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
# ARTICLE 1: Sleep habits & brain aging (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Three Everyday Sleep Habits May Be Quietly Aging the Brain, a 23,000-Person Study Finds",
    "subheadline": "Sleeping outside the recommended seven-to-nine-hour window, napping often during the day and struggling with sleeplessness were each linked to more of the brain damage that builds up with age \u2014 and all three, researchers note, can be changed.",
    "slug": "sleep-habits-brain-aging-white-matter-lesions-arizona-usc-23000-adults-alzheimers-dementia-study-diaspora-20260625-1800",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian-origin professionals abroad routinely run on short, broken sleep \u2014 late video calls with family in India, demanding jobs across time zones, the cultural habit of the afternoon nap \u2014 so evidence that these specific patterns may accelerate brain aging hands the diaspora a concrete, no-cost lever to protect long-term cognitive health.",
    "sources": json.dumps([
        {"name": "SciTechDaily \u2014 'These 3 Common Sleep Habits May Be Aging Your Brain Faster'", "url": "https://scitechdaily.com/these-3-common-sleep-habits-may-be-aging-your-brain-faster/"},
        {"name": "Ally, M., Aslan, D.H., Sayre, M.K. et al. \u2014 'Associations of sleep behaviors with white matter hyperintensity volume in middle-aged to older adults,' Alzheimer's & Dementia (2026)", "url": "https://alz-journals.onlinelibrary.wiley.com/doi/10.1002/alz.71457"}
    ]),
    "body": """We tend to talk about sleep as a single thing \u2014 you either got enough of it or you didn't. A large new study suggests the brain keeps a more detailed record. It is not just how long you sleep, but the particular shape of your sleep habits, that appears to track with how fast the brain ages.

## A Big Look at Sleep and the Aging Brain

The research, published in the journal *Alzheimer's & Dementia*, drew on brain scans and questionnaire data from more than 23,000 middle-aged and older adults in a large biomedical database. It was led by scientists at the University of Arizona, working with the University of Southern California, and it set out to do something most sleep studies skip: break sleep down into separate behaviours rather than treating it as one overall measure.

Participants first answered questions between 2006 and 2010 about five sleep behaviours \u2014 how long they slept, whether they napped during the day, whether they had bouts of sleeplessness, whether they unintentionally dozed off, and whether they snored. About nine years later, those same people underwent brain MRI scans. Researchers then measured the volume of white matter lesions, areas of damage in the brain's wiring that accumulate with age and are linked to a higher risk of dementia, including Alzheimer's disease.

## Which Habits Stood Out

At first, all five behaviours were associated with more white matter damage. But the picture sharpened after the researchers accounted for blood-vessel health and other lifestyle factors that also shape the brain \u2014 high blood pressure, smoking and physical inactivity. Three behaviours remained clearly linked to a larger volume of brain lesions: sleeping outside the recommended range of seven to nine hours, frequent daytime napping, and greater sleeplessness. Snoring and accidental daytime dozing no longer stood out once those other factors were considered.

A closer look at sleep duration found that people who slept fewer than seven hours a night carried higher lesion volumes than those who stayed within the recommended window. "Our findings suggest that having too little sleep may lead to greater white matter lesion volumes in the brain as we age," said Gene Alexander, the study's senior author, who noted the data could not say as much about people who habitually sleep longer.

## The Napping Puzzle

The napping result is the most counterintuitive, because other research has found that short naps can sharpen alertness and thinking. The authors are careful here. Their questionnaire did not capture how long individual naps lasted or when people took them, so a brief, occasional afternoon nap may behave very differently over time from long or frequent ones. The finding is a flag for further study, not a verdict against the nap itself.

A few caveats apply to the study as a whole. It is observational, so it shows association rather than proof that sleep habits cause brain aging; sleep was self-reported, which is imperfect; and the brain scans came years after the sleep questions. Still, the size of the sample and the consistency of the signal give it real weight. The encouraging thread, the authors stress, is that all three flagged behaviours are modifiable. "Sleep is one of those potentially modifiable risk factors," Alexander said. "If we can improve the quality of our sleep, it may help reduce the impacts of brain aging and maybe even lower the risk for dementias like Alzheimer's disease."

## Why It Matters for the Diaspora

For many in the Indian diaspora, the habits this study scrutinises are practically a way of life. There is the parent who takes calls from relatives in India late into the night, the professional juggling work across continents and time zones, the student pulling long hours, and a culture that has long made room for the afternoon nap. None of that is unhealthy by itself, but the research suggests the cumulative pattern \u2014 chronically short nights, broken sleep, heavy daytime napping \u2014 may quietly cost the brain over the decades.

That matters because the community already carries elevated rates of high blood pressure and diabetes, both of which compound the vascular damage seen in these scans. The practical takeaway is unusually accessible and free. Aiming for a consistent seven to nine hours, treating chronic sleeplessness rather than enduring it, and being thoughtful about long or frequent daytime naps are within reach of most households, no prescription or gadget required. In a community that prizes hard work and family obligation, often at the expense of rest, the study reframes good sleep not as indulgence but as one of the simplest long-term investments in a sharper, healthier mind."""
})

# ============================================================
# ARTICLE 2: Air pollution & heart disease (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Even 'Safe' Air May Be Hardening the Heart's Arteries, a Large Imaging Study Finds",
    "subheadline": "Scanning the hearts of more than 11,000 adults, researchers found that long-term exposure to air pollution \u2014 even at levels below regulatory limits \u2014 was tied to more advanced coronary artery disease, with women facing a markedly higher risk.",
    "slug": "air-pollution-coronary-artery-disease-toronto-radiology-11000-adults-even-safe-levels-women-heart-diaspora-20260625-1800",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian-origin families straddle two air-quality worlds \u2014 long stays in some of the planet's most polluted cities back home and daily life in Western suburbs assumed to be clean \u2014 so a finding that even 'safe' air damages arteries reframes pollution as a heart risk the diaspora carries in both places, on top of an already high genetic burden of cardiovascular disease.",
    "sources": json.dumps([
        {"name": "Science News \u2014 'Even \u2018safe\u2019 air pollution levels may affect heart health'", "url": "https://www.sciencenews.org/article/air-pollution-safe-levels-heart-health"},
        {"name": "Drugs.com / HealthDay \u2014 'Air Pollution Might Contribute To Clogged Arteries, Heart Disease Risk'", "url": "https://www.drugs.com/news/air-pollution-might-contribute-clogged-arteries-heart-disease-risk.html"},
        {"name": "Radiological Society of North America \u2014 study in Radiology (June 2026), University of Toronto", "url": "https://pubs.rsna.org/journal/radiology"}
    ]),
    "body": """Most people think of dirty air as a problem for the lungs, and as something that mainly afflicts the world's smog-choked megacities. A large new imaging study complicates both assumptions. It suggests air pollution is also a heart problem \u2014 and that even the relatively clean air of wealthy Western cities, at levels regulators call safe, may be quietly hardening people's arteries.

## Looking Inside the Heart

The study, published in the June 2026 issue of *Radiology*, was led by researchers at the University of Toronto and is one of the largest of its kind. Rather than counting heart attacks after the fact, the team looked directly inside the chest. They analysed cardiac CT scans from more than 11,000 adults, taken between 2012 and 2023 at three major hospitals in the Toronto area, examining the arteries for the calcium deposits and plaque that narrow them and set the stage for a heart attack.

To estimate each person's exposure, the researchers used patients' postal codes to match them to long-term local levels of fine particle pollution and nitrogen dioxide, the kind produced by traffic, industry and the burning of fossil fuels. Then they compared that exposure to what the scans revealed inside the arteries.

## A Dose-Response Signal

The pattern was consistent and pointed in one direction. For each increment of long-term exposure to fine particulate pollution, the researchers found an 11 percent increase in calcium buildup in the coronary arteries, 13 percent greater odds of more extensive plaque, and 23 percent greater odds of having coronary artery disease overall. Nitrogen dioxide showed similar trends, though with smaller effects.

Two findings stand out. First, the associations held even at exposure levels near or below current regulatory safety limits. "There may be no 'floor' at which air quality can be considered entirely safe for the human heart," said cardiac surgeon Salil Deo of Case Western Reserve University, who was not involved in the work. Second, the risk was not evenly shared: women showed a notably higher vulnerability, with one analysis pointing to an 81 percent increased risk of heart disease tied to long-term particle exposure.

"Even at exposure levels below current Canadian air quality standards, long-term air pollution was independently associated with more advanced coronary artery disease," said senior author Kate Hanneman of the University of Toronto. The implication, she argued, is that pollution "belongs alongside blood pressure, cholesterol and smoking as a modifiable cardiovascular risk factor."

## How Dirty Air Reaches the Heart

The study cannot prove that pollution causes heart disease; it is observational. Notably, when the researchers adjusted for established risk factors such as high blood pressure and cholesterol, the link weakened \u2014 a clue that pollution may do part of its damage by worsening those very conditions. The leading explanation is that inhaled fine particles trigger inflammation and oxidative stress that ripple out from the lungs into the bloodstream and blood-vessel walls, accelerating the slow furring-up of the arteries.

The scale of the problem is large. Experts estimate air pollution contributes to several million of the roughly 20 million cardiovascular deaths worldwide each year, and earlier work had already linked it to heart attacks and strokes. What this study adds is a direct, inside-the-body view of how years of exposure track with the buildup of disease itself, not just the dramatic events at the end.

## Why It Matters for the Diaspora

For Indian-origin families, the finding lands in a particularly personal way, because the diaspora lives across two very different air worlds. Many spend extended stretches in India, where cities routinely rank among the most polluted on earth, with winter particulate levels many times what this study examined. The rest of the year is often spent in Western suburbs assumed to be clean. This research suggests neither setting is risk-free for the heart, and that the comparatively "good" air abroad still carries a measurable cost over time.

That is sobering for a community already predisposed to heart disease at younger ages and lower body weights than many other groups. It does not mean pollution can simply be wished away, but it does argue for taking it seriously as a heart-health factor rather than only a respiratory nuisance. Practical steps \u2014 tracking local air-quality indices, using indoor air purifiers and good ventilation, timing outdoor exercise away from heavy-traffic hours and the worst pollution days, and being especially mindful during long visits to high-pollution Indian cities \u2014 are modest defences. The larger message is a shift in mindset: for a diaspora keeping one eye on the cardiac risks in its genes, the air it breathes, in both homelands, deserves a place on the same list."""
})

# ============================================================
# ARTICLE 3: RBI FCNR(B) hedging-cost subsidy (markets-finance)
# ============================================================
articles.append({
    "headline": "India Turns to Its Diaspora to Steady the Rupee \u2014 and Dangles an Unusually Sweet Deposit Deal",
    "subheadline": "By absorbing the cost of hedging, the Reserve Bank of India has let banks raise dollar-deposit rates to 6-7% for overseas Indians, with leverage potentially pushing returns far higher. Analysts see tens of billions in inflows.",
    "slug": "rbi-fcnr-b-hedging-cost-subsidy-nri-dollar-deposits-rupee-support-gift-city-leverage-nomura-55-billion-20260625-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This is a scheme built expressly for the diaspora: it lets overseas Indians earn elevated, currency-risk-free returns on dollar deposits in Indian banks, turning the community's savings into both a personal opportunity and a national lifeline for the rupee \u2014 the most directly NRI-targeted financial move of the year.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 'RBI permits domestic banks to extend credit against foreign currency deposits abroad'", "url": "https://www.thehindubusinessline.com/money-and-banking/rbi-permits-domestic-banks-to-extend-credit-against-foreign-currency-deposits-abroad/article69730000.ece"},
        {"name": "Reuters \u2014 'India's RBI to allow domestic banks to extend loans against overseas FX deposits'", "url": "https://www.reuters.com/world/india/indias-rbi-allow-domestic-banks-extend-loans-against-overseas-fx-deposits-2026-06-23/"},
        {"name": "LiveMint \u2014 'RBI allows banks to give loans for FCNR deposits'", "url": "https://www.livemint.com/industry/banking/rbi-allows-banks-to-give-loans-for-fcnr-deposits-fcnr-b-deposits-nri-dollar-deposits-rupee-11718000000000.html"}
    ]),
    "body": """When a currency comes under pressure, a central bank has a familiar toolkit: raise rates, spend reserves, talk tough. India has reached for something more distinctive. To steady a weak rupee, the Reserve Bank of India is leaning on the country's vast overseas population \u2014 and, in the process, has created an unusually attractive offer for diaspora savers.

## A Subsidy That Changes the Math

The mechanism is technical but the effect is simple. On June 5, as part of a broader package to draw in dollars, the RBI said it would absorb the full cost of hedging on fresh Foreign Currency Non-Resident (Bank), or FCNR(B), deposits with tenors of three to five years, through September 30. FCNR(B) accounts let non-resident Indians park money in foreign currency, typically dollars, in Indian banks, earning interest without taking on rupee exchange-rate risk.

The catch had always been the hedging cost. When a bank takes in dollars and wants to use the rupees, it must hedge the currency risk, and that cost ate into the rates it could offer. By stepping in to bear that cost \u2014 via a plain buy-sell foreign-exchange swap covering the principal \u2014 the RBI effectively drives the banks' hedging cost to zero. That frees lenders to pay far more. Banks have responded by lifting rates on these dollar deposits to around 6 to 7 percent, strikingly high for what is essentially a safe, fixed-income product denominated in dollars.

On June 23, the RBI went a step further, clarifying that banks and their overseas branches \u2014 including those in India's tax-neutral GIFT City \u2014 may extend loans to non-residents against these deposits and issue standby letters of credit. That opens the door to leverage. With borrowed dollars layered on top, analysts at Macquarie estimate returns could approach 12 percent, and Axis Bank suggests they could reach 15 percent at higher leverage \u2014 returns that start to look less like a bank deposit and more like equity.

## Why the Rupee Needs the Help

The backdrop is a difficult year for the currency. The rupee has weakened more than 6 percent in 2026, sliding to record lows near 95-96 per dollar before stabilising, battered by elevated crude-oil import bills during the Middle East conflict and by heavy foreign selling of Indian equities. Rather than burn through reserves defending the currency outright, New Delhi is trying to pull in stable, longer-term dollar flows \u2014 and the 37-million-strong Indian diaspora, with its deep pockets and emotional ties home, is the natural target.

The numbers analysts attach to the scheme are large. Nomura estimates it could draw about $55 billion, with the bulk arriving in August and September as the window closes; Axis Bank sees scope for as much as $100 billion. When banks convert those inflowing dollars into rupees with the RBI, it provides direct support to the currency, exactly the buffer policymakers want.

## The Banks Are Winners Too

Lenders stand to gain on several fronts. The inflows could revive deposit growth that has lagged in recent years, improve liquidity in the financial system and push down market interest rates \u2014 cheaper funding that has already nudged companies toward the bond market. Because these deposits are exempt from the usual reserve requirements, they are an especially efficient source of funds, analysts at Ambit Capital note, and they ease pressure on banks' loan-to-deposit ratios.

Investors have noticed. The Nifty Bank index has climbed roughly 7 percent over the past month, sharply outperforming the broader market, with large lenders that have a strong overseas presence \u2014 State Bank of India and HDFC Bank among them \u2014 seen as the biggest beneficiaries. There are caveats. The scheme is temporary, ending September 30; the eye-catching double-digit returns depend on leverage, which adds risk; and the headline deposit rates can vary by tenor and size.

## Why It Matters for the Diaspora

Few policy moves are aimed quite so squarely at non-resident Indians. For diaspora savers sitting on dollars, the proposition is genuinely unusual: a chance to earn elevated, currency-risk-free returns from a deposit in an Indian bank, with the central bank quietly underwriting the structure. For those willing to use the leverage now permitted through GIFT City and overseas branches, the potential returns climb higher still \u2014 though so does the complexity and the risk, and the leveraged version is not for everyone.

The deeper story is about the relationship between India and its overseas children. In moments of strain, the country has repeatedly turned to its diaspora \u2014 through remittances, through special bonds in past crises, and now through this deposit drive. The scheme lets NRIs do well for themselves while doing something for the rupee at the same time. The clock matters: the most attractive terms run only until September 30, so for diaspora investors weighing where to put their dollars, this is a window with a closing date \u2014 worth examining carefully, ideally with professional advice, before it shuts."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["person sleeping bed night", "woman sleeping pillow rest", "brain MRI scan medical imaging"],
                          ["person sleeping bed night", "woman asleep bedroom"], None),
    articles[1]["slug"]: (["air pollution smog city Delhi haze", "traffic smog urban air pollution", "industrial smokestack pollution sky"],
                          ["city smog air pollution skyline", "traffic pollution haze city"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee currency banknotes", "Reserve Bank of India headquarters"],
                          ["indian rupee currency money", "bank building finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A 23,000-person study links three common sleep habits to greater white-matter brain damage with age",
    articles[1]["slug"]: "A large imaging study tied long-term air pollution, even at safe levels, to more advanced coronary artery disease",
    articles[2]["slug"]: "The Reserve Bank of India is absorbing hedging costs to draw diaspora dollar deposits and support the rupee",
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
