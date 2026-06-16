#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-16 14:00 UTC batch.
Topics:
  1. Cardiac MRI 'remodeling' predicts cancer years before diagnosis (UCLA/MESA, JAHA) — lifestyle-health
  2. Step-count studies: 7-9k steps cut cancer + CVD risk (NCI / Circulation meta-analysis) — lifestyle-health
  3. NRIs can legally cut (or zero out) tax on Indian mutual-fund gains via DTAA — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl14.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl14.bin"):
            with open("/tmp/_img_dl14.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl14.bin")
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
# ARTICLE 1: Cardiac MRI remodeling predicts cancer (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Your Heart May Whisper About Cancer Years Before It Appears. A New MRI Study Just Caught the Signal.",
    "subheadline": "Following more than 6,000 healthy adults for 18 years, UCLA Health researchers found that subtle changes in heart structure on MRI \u2014 a thicker left ventricle, a weaker left atrium \u2014 were linked to a higher risk of later developing breast, colorectal and other cancers. It is an association, not a cause, but it deepens the case that heart disease and cancer share hidden roots.",
    "slug": "cardiac-mri-remodeling-predicts-cancer-risk-mesa-ucla-jaha-south-asian-heart-diaspora-20260616",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians already carry an outsized, early burden of the exact heart changes this study flags \u2014 thickened hearts, high blood pressure, diabetes \u2014 so for the diaspora the finding reframes aggressive heart-risk control not just as cardiac protection but as a possible second line of defence against cancer too.",
    "sources": json.dumps([
        {"name": "Journal of the American Heart Association (cardiac structure/function and incident cancer, MESA)", "url": "https://www.ahajournals.org/journal/jaha"},
        {"name": "Knowridge Science Report (Could Your Heart Reveal Cancer Risk Years Before Diagnosis?)", "url": "https://knowridge.com/2026/06/could-your-heart-reveal-cancer-risk-years-before-diagnosis/"},
        {"name": "Multi-Ethnic Study of Atherosclerosis (MESA), UCLA Health", "url": "https://www.uclahealth.org/"}
    ]),
    "body": """For most of modern medicine, the heart and the tumour have lived on opposite sides of the hospital. Cardiologists watch arteries and chambers; oncologists watch cells dividing out of control. A new study from UCLA Health suggests the wall between those two worlds may be thinner than anyone assumed \u2014 and that the heart, scanned carefully enough, might hint at a cancer still years away.

## What the Researchers Did

The work, published in the Journal of the American Heart Association, drew on one of the most respected datasets in cardiovascular science: the Multi-Ethnic Study of Atherosclerosis, or MESA. Beginning in 2000, MESA enrolled more than 6,000 adults aged 45 to 84 \u2014 deliberately spanning White, Black, Hispanic and Chinese American communities \u2014 none of whom had known heart disease when they joined.

At the outset, each participant underwent a cardiac MRI, among the most precise tools available for measuring the size, shape and function of the heart's chambers and muscle. Researchers then followed them for an average of 18 years, recording who went on to develop cancer.

## The Finding

Over that long window, 790 participants were diagnosed with cancer \u2014 breast, colorectal, lung and prostate among them. When the team matched those diagnoses against the original scans, a pattern surfaced. People who had shown subtle signs of what doctors call cardiac remodeling \u2014 small early shifts in the heart's structure or function \u2014 were more likely to develop cancer later.

Two associations stood out. Women with greater heart-muscle mass in the left ventricle, the heart's main pumping chamber, had a higher risk of breast cancer. And people with poorer function in the left atrium, an upper chamber, were more likely to develop colorectal cancer. As signs of remodeling rose, cancer rates tended to rise with them.

## The Crucial Caveat

This is an association, not a verdict. Lead author Dr. Xinjiang Cai was explicit that the study does not show heart changes cause cancer \u2014 only that the two travel together, and that unknown factors could be driving both. The study is observational, meaning it cannot establish cause and effect, and the authors are clear that larger studies are needed to confirm the signal and uncover the biology behind it.

What makes the work notable is not proof but precision. Earlier research had already tied elevated heart-related blood markers and coronary calcium scores to future cancer. This study went further, using detailed MRI to detect changes in the heart's architecture long before any disease became obvious \u2014 pushing the possible warning window back by years.

## Why It Might Be True

The link is less surprising than it first sounds. Heart disease and cancer are the two leading causes of death worldwide, and they share a long list of risk factors: smoking, obesity, diabetes, high blood pressure, poor diet and physical inactivity. Beneath those lifestyle overlaps run shared biological currents \u2014 chronic inflammation chief among them \u2014 that can quietly damage both the heart muscle and the cellular machinery that keeps cancer in check. A heart subtly remodeling under that strain may simply be the most visible gauge of a body-wide process.

## Why the Diaspora Should Pay Attention

For the Indian diaspora, the study lands on familiar and uncomfortable ground. South Asians develop cardiovascular disease earlier and at lower body weights than most other populations, with disproportionately high rates of diabetes, hypertension and the kind of left-ventricular thickening this research flags. The community is, in other words, already over-represented in exactly the cardiac changes the study links to cancer.

That overlap reframes a message NRIs have heard for years. Aggressive control of blood pressure, blood sugar and weight has always been sold as heart protection. If this line of research holds, the same discipline \u2014 the same statin conversation, the same blood-pressure cuff, the same daily walk \u2014 may be doing double duty, lowering cancer risk as a quiet bonus. Current guidelines already urge tight management of these factors when early heart changes appear; the study hints that doing so could pay dividends in two of medicine's hardest diseases at once.

## The Practical Takeaway

No one should read a cardiac MRI as a cancer test today, and the researchers would be the first to say so. The honest message is humbler and, in its way, more useful: the body is interconnected, and the heart may be an early honest reporter of trouble that has not yet declared itself. For a diaspora that tends to take heart symptoms seriously but cancer screening less so, the practical move is unglamorous and proven \u2014 keep up with blood-pressure and diabetes checks, stay current on age-appropriate cancer screening, and treat a doctor's worry about an enlarging heart as a reason to tighten the whole picture, not just the cardiac one."""
})

# ============================================================
# ARTICLE 2: Step count cuts cancer + CVD risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Magic Number Is Not 10,000. New Research Says 7,000 Steps Already Cuts Cancer and Heart Risk Sharply.",
    "subheadline": "A large NCI-led analysis found that walking 7,000 steps a day was tied to 11 per cent lower cancer risk and 9,000 steps to 16 per cent lower \u2014 with benefits plateauing after that. A separate Circulation meta-analysis found heart-disease risk falling steadily up to about 8,000 steps. Pace barely mattered. Volume did.",
    "slug": "daily-steps-7000-9000-cancer-cardiovascular-risk-nci-circulation-meta-analysis-diaspora-20260616",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The diaspora's sedentary desk-and-car lifestyle \u2014 long tech-job hours, suburban driving, little incidental walking \u2014 collides with an already-elevated risk of diabetes, heart disease and several cancers, making a free, gym-free target of 7,000\u20139,000 daily steps one of the highest-value health levers available to NRIs and their ageing parents.",
    "sources": json.dumps([
        {"name": "National Cancer Institute (Cancer risk decreases with more physical activity)", "url": "https://www.cancer.gov/news-events/cancer-currents-blog"},
        {"name": "Circulation / American Heart Association (Prospective Association of Daily Steps With Cardiovascular Disease: A Harmonized Meta-Analysis)", "url": "https://www.ahajournals.org/journal/circ"},
        {"name": "Annals of Internal Medicine (Step Accumulation Patterns and Risk for Cardiovascular Events and Mortality)", "url": "https://www.acpjournals.org/journal/aim"}
    ]),
    "body": """The figure of 10,000 steps a day has been repeated so often it feels like medical law. It is not. The number was born as a marketing slogan for a 1960s Japanese pedometer, and a wave of recent research is quietly retiring it \u2014 replacing a round, intimidating target with a lower, evidence-backed one that most people can actually hit.

## The Cancer Evidence

The strongest new signal comes from a large analysis led by the National Cancer Institute, drawing on people who wore activity trackers and were then followed for years. After a mean follow-up of nearly six years, those with the highest daily physical activity had a 26 per cent lower risk of developing cancer than the least active.

The step-count breakdown was especially clean. Compared with people taking 5,000 steps a day, cancer risk was 11 per cent lower at 7,000 steps and 16 per cent lower at 9,000 steps. Beyond 9,000, the benefit flattened out. Crucially, it was the volume of steps \u2014 not the pace \u2014 that mattered. Strolling counted. The researchers concluded that less active people could lower their cancer risk simply by adding more walking, at any speed, to the day.

## The Heart Evidence

A separate harmonised meta-analysis published in Circulation, the American Heart Association's flagship journal, told a parallel story for the cardiovascular system. Pooling multiple studies, researchers found the risk of heart disease fell steadily as daily steps rose, with the protective curve leveling off at roughly 8,000 steps a day. Among people free of heart disease at the start, those in the highest step quartile had something like 45 per cent lower risk of a cardiovascular event than the lowest.

A third study, in the Annals of Internal Medicine, added a useful wrinkle for the busy: among under-active adults, those who accumulated their steps in longer continuous bouts \u2014 ten or fifteen minutes at a stretch \u2014 had lower mortality and heart-disease risk than those who got the same total in scattered fragments. A purposeful walk, in other words, may beat the same number of steps grabbed in tiny bursts.

## What It All Adds Up To

The convergence is the point. Three independent lines of evidence, looking at two of the deadliest disease groups, land in the same zone: meaningful protection arrives somewhere between 7,000 and 9,000 steps a day, well short of the mythical 10,000. The returns are steep at the bottom \u2014 the jump from sedentary to moderately active buys the most \u2014 and they taper near the top.

That reframing matters psychologically. For someone logging 3,000 steps, 10,000 feels like a wall. Seven thousand feels like a walk after dinner. And because pace barely registered in the cancer data, there is no need to power-walk or sweat; the body appears to be counting movement, not intensity.

## Why This Is Tailor-Made for the Diaspora

Few groups need this message more than the Indian diaspora. A large slice of the community works long hours at desks in tech and professional jobs, commutes by car through suburban sprawl, and gets almost no incidental walking of the kind that fills a European or urban-Indian day. That sedentary default collides with a genetic and metabolic profile already tilted toward diabetes, early heart disease and elevated risk of several cancers \u2014 a combination The Videshi has reported on repeatedly.

For ageing NRI parents in particular, a step target is gentler and more achievable than the gym memberships and structured workouts they tend to avoid. There is no equipment, no cost, no embarrassment, and no learning curve \u2014 a 20-minute walk after dinner, a loop of the parking lot, a habit of taking the stairs. The same smartwatch many in the community already wear turns the goal into a visible, daily score.

## The Honest Footnotes

These are observational studies, which can show association but not prove cause, and the usual caveats apply: people who walk more may differ in other healthy ways. Anyone with heart, joint or balance problems should start gently and check with a doctor. And walking does not replace strength training, which protects the muscle mass South Asians lose early.

But the headline is liberating rather than demanding. The most consequential exercise target for avoiding cancer and heart disease is not a punishing 10,000 steps \u2014 it is a reachable 7,000 to 9,000, accumulated at any pace, ideally in a few real walks. For a diaspora that drives everywhere and sits all day, that is perhaps the cheapest insurance policy on the market."""
})

# ============================================================
# ARTICLE 3: NRI mutual fund DTAA tax (markets-finance)
# ============================================================
articles.append({
    "headline": "NRIs Are Quietly Paying Tax They May Not Owe on Indian Mutual Funds. A Treaty Clause Can Erase It.",
    "subheadline": "Fund houses deduct tax at source on NRI mutual-fund gains \u2014 up to 20 per cent on short-term equity profits \u2014 but a string of tribunal rulings has confirmed that NRIs in countries like the UAE and Singapore can invoke their Double Taxation Avoidance Agreement and owe India nothing on those capital gains. The catch: you have to claim it, and most do not.",
    "slug": "nri-mutual-fund-capital-gains-dtaa-tds-refund-uae-singapore-itat-rulings-diaspora-20260616",
    "category": "markets-finance",
    "vertical": "personal-finance",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Millions of NRIs hold Indian mutual funds and silently accept 12.5\u201320 per cent tax deducted at source on their gains \u2014 yet those living in treaty-favourable jurisdictions like the UAE, Singapore and others may legally owe India zero, meaning the difference is real money the diaspora can reclaim simply by understanding and asserting their DTAA rights.",
    "sources": json.dumps([
        {"name": "Mint (NRIs can cut tax on mutual fund gains using DTAA \u2014 here's how)", "url": "https://www.livemint.com/money/personal-finance"},
        {"name": "Income Tax Appellate Tribunal rulings: Saket Kanoi (UAE) vs DCIT, 2024; Anushka Sanjay Shah (Singapore) vs ITO, 2025", "url": "https://itat.gov.in/"},
        {"name": "Angel One (Tax on Mutual Funds for NRIs: Implications & Benefits)", "url": "https://www.angelone.in/knowledge-center"}
    ]),
    "body": """For the millions of non-resident Indians who keep a foot in India's markets through mutual funds, tax has always been the quiet leak in the bucket. When they redeem units, the fund house deducts tax at source before the money ever reaches them \u2014 and most NRIs simply accept the smaller cheque as the cost of investing back home. A growing body of tribunal rulings says many of them are giving up money they do not actually owe.

## How NRI Mutual-Fund Gains Are Taxed by Default

Start with the domestic rules. Under India's tax law, gains on equity mutual funds held more than 12 months count as long-term and are taxed at 12.5 per cent on amounts above \u20b91.25 lakh a year. Sell sooner and short-term gains are taxed at 20 per cent. Debt funds bought on or after 1 April 2023 are taxed at the investor's slab rate, with no indexation relief.

The sting for NRIs is the mechanism: fund houses deduct tax at source (TDS) before disbursing proceeds, at rates that can run to 20 per cent on short-term equity gains. The money is gone before the investor decides anything \u2014 and that finality is exactly why so few question it.

## The Treaty That Changes the Math

Here is the part most NRIs miss. India has signed Double Taxation Avoidance Agreements \u2014 DTAAs \u2014 with dozens of countries, and a tax treaty can override domestic law. Where a treaty grants the exclusive right to tax capital gains to the investor's country of residence, India simply cannot levy the tax, regardless of what the domestic rate would have been.

For NRIs in the right jurisdiction, the consequence is dramatic. An investor in a country that does not tax capital gains \u2014 the UAE being the headline example \u2014 can end up owing tax to no one: not India, because the treaty hands taxing rights to the residence country, and not the UAE, because it levies no such tax. The leak does not just narrow; it closes.

## The Rulings That Made It Stick

This is not theory or aggressive interpretation. India's Income Tax Appellate Tribunal has affirmed it in case after case. In Saket Kanoi (UAE) vs DCIT, decided in Delhi in October 2024, the tribunal held that capital gains on Indian mutual funds for a UAE-based NRI are not taxable in India, because Article 13 of the India\u2013UAE treaty assigns taxing rights solely to the country of residence. In Anushka Sanjay Shah (Singapore) vs ITO, decided in Mumbai in March 2025, mutual-fund units were recognised as movable capital assets, and Article 13 of the India\u2013Singapore treaty was read to grant Singapore exclusive taxing rights.

Together, these decisions set a strong precedent: NRIs in countries with similar treaty wording can legally avoid Indian tax on mutual-fund gains, and can choose whichever route \u2014 domestic rules or the DTAA \u2014 leaves them better off.

## The Catch: You Have to Claim It

The treaty benefit is not automatic. The fund house deducts TDS regardless; the relief comes only when the investor asserts it. In practice that means filing an Indian income-tax return for the year, reporting the gains, invoking the relevant DTAA article, and claiming a refund of the tax wrongly withheld. It typically also requires a valid Tax Residency Certificate from the country of residence and the related treaty paperwork. Skip the filing, and the TDS the fund house took becomes a permanent donation to the Indian exchequer.

## Why This Matters for the Diaspora

This is money on the table, and the table is enormous. Indian mutual funds remain one of the diaspora's favourite vehicles for staying invested in the homeland's growth, and the Gulf alone hosts millions of Indian workers and professionals \u2014 precisely the UAE-resident profile the rulings vindicate. Singapore, with its large Indian professional community, sits in the same favourable position.

The asymmetry is stark: a UAE-based NRI and a US-based NRI can hold the identical fund, post the identical gain, and face wildly different final tax bills \u2014 not because of how they invested, but because of which treaty governs them and whether they bothered to claim it. The diaspora's instinct is to treat TDS as settled and move on. These rulings argue the opposite: for many, the deducted tax is a refund waiting to be claimed.

## The Prudent Footnote

Treaty outcomes hinge on the specific country, the exact treaty article and the individual's facts \u2014 a US or UK resident faces different rules than a UAE one, and residency status under Indian law must be correctly established. This is not a do-it-yourself area; a qualified cross-border tax adviser is worth the fee given the sums involved. But the principle is now well-settled, and the lesson for the diaspora is simple: before accepting that bite out of your mutual-fund redemption, find out what your treaty actually says. It may say you owe nothing."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["cardiac MRI heart scan", "human heart medical imaging", "MRI scanner hospital"],
                          ["cardiac mri scan", "heart medical imaging hospital"]),
    articles[1]["slug"]: (["people walking park exercise", "person walking outdoors fitness", "walking pedometer steps"],
                          ["people walking outdoors", "person walking exercise fitness"]),
    articles[2]["slug"]: (["mutual fund investment finance", "financial planning calculator documents", "Indian rupee banknotes money"],
                          ["financial planning calculator tax documents", "investment growth chart money"]),
}
img_captions = {
    articles[0]["slug"]: "A cardiac MRI scan; UCLA researchers linked subtle heart-structure changes on MRI to later cancer risk",
    articles[1]["slug"]: "A person out walking; new studies tie 7,000\u20139,000 daily steps to lower cancer and heart-disease risk",
    articles[2]["slug"]: "Mutual-fund and tax paperwork; NRIs in treaty-favourable countries can reclaim tax withheld on fund gains",
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
