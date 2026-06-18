#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 10:00 UTC batch.
Topics:
  1. NOX4 muscle protein explains why staying active preserves strength with age (Science Advances) — lifestyle-health
  2. 24-hour blood-pressure swings tied to poorer brain health & dementia risk (Monash, Neurology) — lifestyle-health
  3. NSE files draft papers for long-delayed IPO — India's largest bourse, ~$3bn offer-for-sale — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0618.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0618.bin"):
            with open("/tmp/_img_dl0618.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0618.bin")
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
# ARTICLE 1: NOX4 muscle protein & healthy aging (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Scientists Found the Muscle Switch That Exercise Flips On. It May Explain Why Movement Keeps You Strong With Age.",
    "subheadline": "A protein called NOX4 falls as we grow older and inactive \u2014 and when researchers stripped it from muscle, animals grew frail, lost muscle and developed insulin resistance. Exercise restored it, offering a molecular clue to why staying active protects the ageing body.",
    "slug": "nox4-muscle-protein-exercise-aging-strength-science-advances-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians lose muscle earlier and carry more body fat at the same weight than most populations, making age-related frailty and insulin resistance a quiet diaspora epidemic \u2014 and this research underlines that for the NRI parent or professional, regular movement is not optional but a biological necessity that flips on the body's own repair machinery.",
    "sources": json.dumps([
        {"name": "Fox News Health \u2014 One muscle protein may hold the key to staying stronger as you age, study finds", "url": "https://foxnews.com/health/one-muscle-protein-may-hold-key-staying-stronger-you-age-study-finds"},
        {"name": "Science Advances \u2014 NOX4 in skeletal muscle, exercise adaptation and metabolic health (2026)", "url": "https://www.science.org/journal/sciadv"}
    ]),
    "body": """Everyone past a certain age knows the feeling: the staircase that used to be nothing now leaves the knees complaining, the grip that loosens, the slow erosion of strength that arrives whether you invite it or not. Scientists have long preached that exercise slows this decline. Now they may have found one of the molecular switches that explains why \u2014 and why letting the body go still is so costly.

## The Protein Nobody Was Watching

Researchers, publishing in the journal *Science Advances*, zeroed in on a protein called **NOX4**. It is not a household name like collagen or insulin, but it turns out to sit close to the centre of how muscle adapts to the demands placed on it. The team found that NOX4 naturally declines with both age and inactivity \u2014 a double penalty, since the two so often travel together.

To test what the protein actually does, the scientists removed NOX4 from the muscles of mice. The results were striking and, for anyone worried about ageing, sobering. The animals grew weaker, lost muscle mass, and developed a cluster of problems that read like a catalogue of old age: frailty, insulin resistance and even signs of liver disease.

## Why Exercise Is the Antidote

The encouraging half of the finding is what happened in the other direction. When older mice exercised, their NOX4 levels were restored. In other words, physical activity appears to switch the protein back on \u2014 nudging muscle to repair itself and adapt, exactly the process that fades when a body sits still for years.

"Researchers believe NOX4 helps muscles repair themselves and adapt to the physical demands of exercise," the study's authors explained. That single sentence reframes a familiar truth. Exercise is not merely burning calories or building visible muscle; it is keeping a repair system online that would otherwise wind down.

Josephine Hunt, a fitness educator and founder of The Resilience Revolution in New Jersey who was not involved in the work, put it plainly. "The emerging NOX4 research is exciting because it helps explain something exercise scientists have observed for decades. Physical activity does far more than strengthen muscles," she said. "Exercise appears to activate biological signalling pathways that help the body adapt, repair and become more resilient over time."

## The Caveats Worth Keeping

This is, importantly, a mouse study, and the authors are careful to say so. Findings in mice do not automatically translate to humans, and no one is about to prescribe a NOX4 pill. But the team did not stop at rodents. They also examined muscle samples from younger and older men and found the same pattern \u2014 NOX4 declining with age \u2014 which is what makes the work more than an animal curiosity. Whether boosting the protein directly could help humans stay strong remains an open question for future research.

What is not in doubt is the practical lesson hiding inside the molecular detail: the most reliable way we currently have to keep NOX4 \u2014 and the repair machinery it governs \u2014 working is to move.

## Why This Matters for the Diaspora

For the Indian diaspora, the finding lands on a sensitive nerve. South Asians are known to develop insulin resistance and Type 2 diabetes at lower body weights than other groups, and tend to carry more fat and less muscle for a given size \u2014 the so-called "thin-fat" phenotype. Muscle is not just about strength; it is one of the body's largest sinks for blood sugar, and losing it accelerates the metabolic troubles the community is already prone to.

That makes age-related muscle loss, or sarcopenia, a particularly quiet threat for NRIs \u2014 the desk-bound IT professional, the parent who stopped playing sport decades ago, the grandparent whose world has shrunk to a few rooms. The NOX4 research adds a molecular reason to a cultural blind spot: in many South Asian households, structured strength training is still seen as vanity or the preserve of the young, not as preventive medicine for the middle-aged and elderly.

## What To Actually Do

The takeaway is unglamorous and free. Resistance work \u2014 bodyweight squats, resistance bands, light weights \u2014 two or three times a week is the most direct way to keep muscle and its repair systems switched on. Walking and aerobic activity help, but they do not replace loading the muscles. Start small and build, especially after fifty, when the decline steepens. And treat a parent's fading grip or unsteady stairs not as the unavoidable price of age, but as a signal that the body's repair switch needs flipping back on. The science is increasingly clear: movement is not optional maintenance. It is the maintenance."""
})

# ============================================================
# ARTICLE 2: 24-hour blood pressure variability & brain health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It Is Not Just How High Your Blood Pressure Is. How Much It Swings May Quietly Age Your Brain.",
    "subheadline": "A Monash University study tracking blood pressure around the clock found that bigger 24-hour swings were tied to worse memory and problem-solving \u2014 a decline equivalent to roughly seven extra years of brain ageing \u2014 and to visible signs of injury on brain scans.",
    "slug": "blood-pressure-variability-24-hour-brain-health-cognition-monash-neurology-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Hypertension is rampant and frequently undertreated among South Asians, and most diaspora families judge it by a single clinic reading \u2014 yet this research suggests the hidden danger lies in the swings between readings, a pattern only round-the-clock monitoring can catch, reframing how NRIs should manage their own and their ageing parents' blood pressure.",
    "sources": json.dumps([
        {"name": "Medical Xpress \u2014 Blood pressure swings over 24 hours tied to poorer brain health (Monash University)", "url": "https://medicalxpress.com/news/2026-05-blood-pressure-hours-poorer-brain.html"},
        {"name": "Neurology \u2014 Gibson et al., Association of 24-Hour Blood Pressure Variability With Cognition and Brain MRI Markers of Structural Change in Adults in Mid- to Late-Life (2026)", "url": "https://www.neurology.org/doi/10.1212/wnl.0000000000214935"}
    ]),
    "body": """Most people think they know their blood pressure. It is the number the doctor reads off a cuff at a clinic, scribbled into a chart, declared fine or worrying. New research from Monash University suggests that single number, taken once in a quiet room, may be hiding the part that matters most for the brain: how much blood pressure swings across the day and night.

## What the Researchers Did

Scientists at Monash's Turner Institute for Brain and Mental Health used continuous monitoring devices to track the blood pressure of 225 Australians aged between 55 and 80 over a full 24-hour period \u2014 capturing the rises and falls a clinic visit never sees. They then matched those patterns against tests of thinking and memory, and against brain MRI scans looking for signs of structural injury.

The results, published in the journal *Neurology*, were clear in two directions. Greater **variability** in blood pressure over the day was associated with poorer cognition \u2014 specifically planning, problem-solving and memory. And higher **average** blood pressure over the 24 hours was associated with greater evidence of vascular brain injury on the scans.

## A Striking Comparison

The numbers translate into something uncomfortably concrete. "Even a modest increase in blood pressure variability was linked to lower performance on cognitive tests, equivalent to roughly seven years of additional aging," said first author Madeline Gibson, a PhD candidate in clinical neuropsychology.

Seven years. That is the gap a fluctuating blood pressure may quietly impose on a brain, long before anyone notices a lapse in memory.

"Our study shows that blood pressure is associated with subtle brain changes that can occur long before memory or thinking problems become apparent," Gibson said. The damage, in other words, accumulates silently.

## Why Swings, Not Just Highs, Matter

Doctors have understood for decades that sustained high blood pressure damages the brain. What is newer here is the focus on variability \u2014 the swings themselves. The study points to plausible mechanisms: injury to the brain's white matter tracts, the wiring that connects regions, and altered function of the blood-brain barrier, the protective filter that keeps harmful substances out of brain tissue.

Senior author Professor Matthew Pase argued the finding exposes a blind spot in routine care. "The research indicates that standard blood pressure readings taken at a doctor's clinic may not provide the full picture," he said. "Most people think of blood pressure as a single number taken in a doctor's clinic, but blood pressure is dynamic. Blood pressure rises and falls across the day and night, and those fluctuations may carry important information about brain health."

## The Honest Caveats

The study is observational, which means it can show an association but not prove that the swings directly cause the brain changes. "Whether managing blood pressure variability could slow or reverse these brain changes is not yet known," Gibson noted. The cohort was also modest in size and drawn from one country. What the research adds is not a treatment, but a sharper lens \u2014 and a reason to look beyond the single clinic number.

## Why This Hits Home for the Diaspora

For the Indian diaspora, the implications are pointed. Hypertension is widespread among South Asians and frequently caught late or treated loosely, often judged by an annual reading at a check-up. The community's elevated burden of heart disease, stroke and now dementia makes the brain stakes especially high.

There is a practical cultural wrinkle, too. Many NRI families manage an ageing parent's health from a distance, relying on whatever number a relative reports from a home monitor or a clinic visit. This research suggests that an occasional snapshot \u2014 or worse, a reading taken only when symptoms flare \u2014 can miss the very pattern that predicts trouble.

## What To Actually Do

Ask a doctor about 24-hour ambulatory blood pressure monitoring, especially for older relatives or anyone with borderline readings \u2014 it captures the swings a clinic visit cannot. Take home readings at consistent times rather than at random, and track the spread, not just the peak. Stick to prescribed medication on schedule, since erratic dosing can itself drive variability. And treat midlife, as the researchers stress, as a key window: protecting the brain's wiring is far easier than repairing it once memory begins to fade."""
})

# ============================================================
# ARTICLE 3: NSE IPO draft papers filed (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Largest Stock Exchange Is Finally Going Public. After a Decade of Delays, the NSE Just Filed Its IPO Papers.",
    "subheadline": "The National Stock Exchange \u2014 the world's busiest derivatives platform \u2014 has filed draft papers for a pure offer-for-sale of up to 149 million shares worth roughly $3 billion, ending a listing saga that began in 2016 and handing long-waiting investors a multi-billion-dollar windfall.",
    "slug": "nse-ipo-draft-papers-filed-offer-for-sale-3-billion-india-exchange-nri-investor-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The NSE is the exchange where most of India's listed wealth changes hands \u2014 the very market NRIs tap through index funds, ETFs and direct holdings \u2014 and owning a slice of the bourse itself, alongside a record year of Indian mega-listings, gives the diaspora a rare chance to bet on the plumbing of India's markets rather than any single stock.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors", "url": "https://www.reuters.com/world/india/"},
        {"name": "Mint \u2014 NSE files draft papers for long-awaited IPO", "url": "https://www.livemint.com/market/ipo"}
    ]),
    "body": """After nearly a decade of false starts, scandal and litigation, India's biggest stock exchange is finally heading for the public markets. The National Stock Exchange filed its draft red herring prospectus with the markets regulator late on Wednesday, setting in motion one of the most closely watched listings in the country's history \u2014 and a multi-billion-dollar payday for the investors who waited it out.

## The Shape of the Deal

The structure is unusual for its size. The offering is a **pure offer-for-sale** of up to 149 million equity shares by existing institutional shareholders \u2014 meaning no new capital will be raised and every rupee of proceeds flows to the sellers cashing out, not to the exchange itself. Based on grey-market prices, where NSE shares already trade at around \u20b92,000 apiece, the IPO is expected to be worth roughly \u20b929,780 crore, or over $3 billion.

That valuation places the exchange in rarefied company. With shares trading near \u20b92,000 in the unlisted market, the NSE is valued at some $57 billion \u2014 enough to rank among the world's most valuable bourses, behind only a handful including the London Stock Exchange Group. The exchange may price the issue at a 5 to 10 percent discount to private-market levels, around \u20b91,900 a share, sources told Reuters, a move one banker said would "attract incoming investors while not short-changing existing ones."

## Who Cashes In

The sellers read like a roll-call of Indian and global institutional capital. They include State Bank of India, Canada Pension Plan Investment Board, affiliates of Morgan Stanley, Singapore's Temasek, Bank of Baroda, General Insurance Corporation, New India Assurance, National Insurance and United India Insurance, among others. Top investors stand to reap a collective windfall estimated at around $2.6 billion.

A quirk of Indian regulation adds a twist: a stock exchange cannot list its own shares on its own platform. So the NSE \u2014 India's largest \u2014 will list on its smaller rival, the BSE.

## A Decade in the Making

This listing has been promised, delayed and nearly buried more than once. The NSE first filed IPO papers back in 2016, only to be engulfed in the so-called co-location scandal, in which it was accused of giving select brokers unfair, faster access to its servers. The case dragged on for years, the IPO was shelved, and the leadership was overhauled.

The path cleared only this year. Under new management, the NSE reached a settlement of roughly \u20b91,300 crore with the Securities and Exchange Board of India in January 2026, removing the regulatory cloud and opening the way to refile. The current syndicate is vast \u2014 around 20 investment bankers, with Kotak Mahindra Capital and Morgan Stanley India among the book-running lead managers \u2014 a measure of the deal's scale and complexity. With nearly 200,000 shareholders, the NSE is also India's largest unlisted company by number of investors, making the mechanics of the offering unusually intricate.

## The Bigger Picture

The NSE float does not arrive in isolation. It is shaping up to be one of two blockbuster Indian listings this year, alongside Mukesh Ambani's Reliance Jio, whose own roughly $4 billion IPO is expected to land in the coming months. Together they signal a banner year for India's primary market \u2014 even as foreign portfolio investors, who pulled a record $30.8 billion from Indian equities earlier in 2026, have only just begun tiptoeing back as buyers.

## What It Means for the Diaspora

For NRIs, the NSE is not an abstraction. It is the exchange behind the Nifty 50, the index that underpins most of the India-focused ETFs and mutual funds sitting in diaspora portfolios from New Jersey to Singapore. Buying into the bourse is, in effect, a bet on the rising volume of Indian trading itself \u2014 a toll-collector on the country's deepening capital markets, rather than a wager on any one company's fortunes.

The sober counsel applies here as to any hyped listing. This is an offer-for-sale, so none of the money strengthens the exchange's own balance sheet \u2014 insiders are selling, and the price reflects a rich private-market valuation. NRIs eligible to invest should read the draft prospectus closely for the real numbers on growth, regulatory risk and how the discount is finally set, rather than chasing the buzz of a decade-delayed debut. India's market plumbing is going public; whether it is a bargain depends, as always, on the price."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["senior strength training", "older adult weight lifting exercise", "elderly man dumbbell gym"],
                          ["older man lifting weights gym", "senior strength training"], None),
    articles[1]["slug"]: (["blood pressure measurement", "sphygmomanometer arm cuff", "blood pressure monitor patient"],
                          ["blood pressure monitor arm", "doctor measuring blood pressure"], None),
    articles[2]["slug"]: (["National Stock Exchange India building", "Bombay Stock Exchange building Mumbai", "stock exchange trading floor India"],
                          ["stock exchange building india", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "Strength training in older age; new research links the muscle protein NOX4 to how exercise preserves strength",
    articles[1]["slug"]: "A blood pressure measurement; a new study links 24-hour swings in blood pressure to poorer brain health",
    articles[2]["slug"]: "A stock exchange trading environment; India's NSE has filed draft papers for its long-delayed IPO",
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
