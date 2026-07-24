#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-26 14:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Penn State FAST-2 — a 4-minute daily home strength routine (4 moves x 30s:
     push-ups, chair stands, resistance-band rows, stair stepping) improved
     mobility, balance and leg strength in inactive adults 65+ with walking
     difficulty over 12 weeks; 81% adherence, no adverse events. Published in
     PLOS One (Sciamanna/Dandekar). Angle: falls are a top cause of death in
     elders; tiny dose, huge function gain. — lifestyle-health
     (DISTINCT from prior strength-training-longevity epi piece and the
      4-minute-falls angle is new; this is a randomized intervention.)
  2. Exercise during the weight-MAINTENANCE phase cuts weight regain after
     diet/drugs/bariatric surgery — meta-analysis of 11 RCTs / 568 adults,
     mean -2.81 kg less regain vs control; fat-mass effect inconclusive.
     Published in Scientific Reports. Angle: the GLP-1 era's quiet question —
     how to keep weight off once you stop. — lifestyle-health
     (DISTINCT: none of the recent diet/sleep/movement-snack pieces cover
      weight-regain maintenance or the post-Ozempic keep-it-off problem.)
  3. NRIs shift from remitters to investors — GIFT City wealth platform Belong
     reports 2x inflows ($3m->$6m), $36m AUM run-rate, 25k users, strongest
     demand from UAE/Qatar; NRIs treating India as a portfolio-allocation
     destination, not just remittances/real estate. Sits against the RBI's
     FCNR-B push and record remittances. — markets-finance
     (DISTINCT: prior finance pieces were NSE IPO, IRFC OFS, rupee/FCNR-B,
      gold, SIP flows, bonds, Meta-CRED — none cover the GIFT City NRI
      investment-behaviour shift.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000.bin"):
            with open("/tmp/_img_dl1000.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000.bin")
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
        for r in fetch_wikimedia_commons_images(person)[:3]:
            candidates.append((r["url"], "Wikimedia Commons"))
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
# ARTICLE 1: USC longevity diet / methionine (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Four Minutes a Day: A Tiny Strength Routine Sharply Improved Balance and Leg Power in Older Adults",
    "subheadline": "A home workout of just four exercises, 30 seconds each, left frail adults over 65 stronger and steadier on their feet after 12 weeks \u2014 a low-barrier answer to the falls that are among the leading causes of death in old age, Penn State researchers report.",
    "slug": "penn-state-fast-2-four-minute-daily-strength-routine-older-adults-balance-falls-plos-one-sciamanna-diaspora-20260626-1400",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Aging Indian parents and grandparents \u2014 often living with NRI children abroad or alone back home while their families are overseas \u2014 are exactly the group most at risk from falls and least likely to take up a gym routine, so a free, four-minute, equipment-light workout that can be coached over video and done in a living room offers diaspora families a realistic way to protect elders' independence across distance.",
    "sources": json.dumps([
        {"name": "Penn State University \u2014 'Four-minute daily workout improves strength, balance in older adults'", "url": "https://www.psu.edu/news/medicine/story/four-minute-daily-workout-improves-strength-balance-older-adults"},
        {"name": "Dandekar, S., et al. (2026), 'Brief daily functional strength training to improve functional performance in older adults with mobility disability: A randomized trial', PLOS One", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0336748"}
    ]),
    "body": """Most exercise advice for older people asks for more than many can give: a gym membership, a 30-minute block, a routine of sets and repetitions that feels daunting before it even begins. A new study suggests the bar can be set far lower. Four minutes a day, at home, with almost no equipment, was enough to measurably improve strength and balance in frail adults over 65 \u2014 the very qualities that keep people on their feet and out of hospital.

## A Four-Minute Prescription

The research, published in the journal *PLOS One*, was led by Christopher Sciamanna and Smita Dandekar at the Penn State College of Medicine. The team built a home-based program they called Functional Activity Strength Training, or FAST-2, designed around a single insight: that the reason so few older adults strength-train is not unwillingness but the complexity and length of conventional routines.

"Exercise is actually really complicated, because you have to decide how many repetitions, how far, how many sets, how much rest and how many times per week," said Dandekar. FAST-2 strips all of that away. The workout is four exercises, performed for 30 seconds each with 30-second rests between them \u2014 four minutes from start to finish. The moves are deliberately ordinary: push-ups (which can be done against a wall or kitchen counter), chair stands, two-arm rows with a resistance band, and stair stepping.

## What the Trial Found

The researchers recruited 97 sedentary adults aged 65 and older who already had some difficulty walking, with an average age of 74. Before the study, these participants were managing just 18 minutes of physical activity in an entire week. They were randomly split into a group that did the daily routine and a control group that did not, with video coaching at the start and at weeks two, four and eight to check form and progress, plus daily email reminders.

Over 12 weeks, the differences were striking. Compared with the control group, those doing the four-minute routine cut their time on the Five-Times Sit-to-Stand test by 2.3 seconds, held a one-legged stance 3.6 seconds longer, and managed 4.2 more chair stands in 30 seconds \u2014 all meaningful gains in the kind of strength and balance that everyday life depends on. Crucially, participants stuck with it, completing the workout on 81 percent of days, and no significant adverse events were reported.

"The human body is designed to improve very quickly," Sciamanna said. "And just a few repetitions of an exercise performed regularly can lead to huge improvements. Exercise is about forward thinking \u2014 think about what you want to be able to do and train for it."

## Why Small Doses Matter

The backdrop is sobering. Unintentional injuries such as tripping and falling are among the leading causes of death for adults 65 and older, according to the US Centers for Disease Control and Prevention, and mobility \u2014 the simple ability to rise from a chair, climb stairs and stay balanced \u2014 is one of the strongest predictors of independent living. Yet fewer than one in five older adults meet the recommended two days a week of muscle-strengthening activity, often because the routines feel too long, too painful or too complicated.

A few caveats apply. The trial was relatively small and lasted 12 weeks, so it cannot show whether the gains hold over years or actually reduce falls and fractures in the long run. Participants received regular video coaching and reminders, support that may have boosted their adherence beyond what an unsupervised person would manage. Still, the core message \u2014 that a tiny, sustainable dose can move the needle on function \u2014 is hard to ignore.

## Why It Matters for the Diaspora

For the Indian diaspora, the finding speaks to a quiet, growing worry: aging parents. Many NRIs live oceans away from elders who are either alone in India or have joined their children abroad, and the fear of a fall \u2014 a broken hip, a hospital stay, a sudden loss of independence \u2014 hangs over those long-distance relationships.

What FAST-2 offers is a tool suited to exactly that situation. It needs no gym, costs almost nothing, and fits in a living room; the resistance band and a sturdy chair are all the equipment required. It can be demonstrated and checked over a video call, turning a weekly family catch-up into a coaching session. For diaspora families looking for a concrete way to protect a parent's mobility from a distance, four minutes a day may be one of the highest-return investments they can make."""
})

# ============================================================
# ARTICLE 2: Five-minute movement breaks (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Weight Comes Back. Exercise May Be the Quiet Reason It Comes Back Less",
    "subheadline": "Pooling 11 clinical trials, researchers found that people who exercised during the maintenance phase after losing weight \u2014 through dieting, drugs or surgery \u2014 regained nearly three kilograms less than those who did not, a timely finding in the age of weight-loss injections.",
    "slug": "exercise-maintenance-phase-cuts-weight-regain-meta-analysis-11-trials-scientific-reports-keep-it-off-glp1-diaspora-20260626-1400",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GLP-1 weight-loss drugs are spreading fast among affluent, health-conscious NRIs and urban Indians alike, and the hardest question \u2014 what happens when you stop, and the weight creeps back on a body already prone to diabetes and heart disease \u2014 is one this study speaks to directly, suggesting the cheapest, most durable insurance against regain is a habit of regular movement, not another prescription.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 'Lost weight is less likely to return when exercise follows obesity treatment'", "url": "https://www.news-medical.net/news/20260624/Lost-weight-is-less-likely-to-return-when-exercise-follows-obesity-treatment.aspx"},
        {"name": "Wang, J., Chen, Y., Xu, K., & Dai, J. (2026), 'The effects of exercise interventions on weight regain after weight loss: A systematic review and meta-analysis', Scientific Reports", "url": "https://www.nature.com/articles/s41598-026-57804-8"}
    ]),
    "body": """Losing weight is hard. Keeping it off is harder. For most people who shed kilos through dieting, medication or even surgery, some of that weight eventually finds its way back \u2014 a frustrating, well-documented rebound that has long made long-term weight management one of the thorniest problems in medicine. A new analysis offers a modest but reassuring piece of the answer: people who kept exercising after the weight came off regained less of it.

## What the Researchers Did

The study, published in the journal *Scientific Reports*, was a systematic review and meta-analysis \u2014 a method that pools the results of many separate trials to find a clearer signal than any one study can give. The reviewers searched five major medical databases for randomized controlled trials of adults with overweight or obesity who had already lost weight, then asked a focused question: did adding exercise during the maintenance phase that followed reduce how much weight crept back?

After screening more than 1,500 records, they settled on 11 trials involving 568 participants, published between 1996 and 2023. The participants, aged roughly 39 to 70, had lost weight through very low-calorie diets or bariatric surgery, and the exercise added afterward ran the gamut: resistance training, aerobic workouts, walking, cycling, even deep-water "aqua jogging." Interventions lasted from 12 to 53 weeks.

## A Small but Solid Benefit

The headline result was clear and consistent. Across nine trials that measured body weight, people who exercised during maintenance regained significantly less than those who did not \u2014 a mean difference of about 2.81 kilograms. Notably, this finding showed no statistical "heterogeneity," meaning the trials largely agreed with one another despite their differences, and the result held up under a stricter form of analysis. In a field crowded with conflicting claims, that consistency carries weight.

The picture was murkier for body fat specifically. Six trials looked at fat mass, and while the exercising groups tended to lose more of it, the effect was not statistically significant \u2014 the data simply varied too much to draw a firm conclusion. Encouragingly, people in the exercise groups were no more likely to drop out than those who did not exercise, suggesting the routines were sustainable rather than punishing.

The authors are candid about the limits. The number of trials was small, the exercise prescriptions varied widely, some of the evidence is decades old, and several studies carried a meaningful risk of bias. They stop short of declaring an optimal type or dose of exercise, framing their work as supportive rather than definitive: exercise is "a useful component of long-term weight management," not a guarantee.

## Why the Timing Matters

The finding lands at a pivotal moment. The arrival of GLP-1 drugs such as semaglutide and tirzepatide has made dramatic weight loss achievable for millions, but it has also sharpened an old anxiety. Studies of these medications show that when people stop taking them, much of the lost weight tends to return. That has turned "how do you keep it off?" into one of the most pressing questions in health \u2014 and made the unglamorous answer of regular physical activity newly relevant.

The mechanism is intuitive. Exercise burns energy, helps preserve the lean muscle that dieting and drugs can strip away, and improves the metabolic health that makes weight easier to regulate. It will not, on the evidence here, melt away fat on its own. But as a hedge against the rebound, the data suggest, movement earns its place.

## Why It Matters for the Diaspora

For the Indian diaspora, the stakes are unusually personal. Weight-loss injections have spread quickly among affluent, health-aware NRIs and, increasingly, among urban Indians \u2014 a community already carrying an outsized, early-onset burden of diabetes and heart disease, often at lower body weights than other groups. For South Asians, even modest regained weight can tip metabolic risk in the wrong direction.

That makes the keep-it-off problem especially consequential for diaspora families weighing these treatments. The study's quiet lesson is that the most durable safeguard is not another prescription but a sustained habit: walking, lifting, cycling \u2014 whatever can be kept up for years rather than weeks. For anyone who has worked hard to lose weight, by whatever means, the message is that the work of maintaining it is a different, ongoing project \u2014 and that staying active is among the surest ways to hold the line."""
})
# ============================================================
# ARTICLE 3: NRI investment shift / GIFT City (markets-finance)
# ============================================================
articles.append({
    "headline": "From Sending Money Home to Investing in India: The Quiet Shift in How NRIs Treat the Motherland",
    "subheadline": "A GIFT City wealth platform says its inflows doubled in two months as overseas Indians increasingly route fresh capital into Indian funds and deposits \u2014 a sign that the diaspora is starting to treat India as a portfolio bet, not just a place to wire money to family.",
    "slug": "nri-investment-shift-gift-city-belong-inflows-double-portfolio-allocation-not-remittances-ifsca-diaspora-nri-investor-20260626-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This story is about the diaspora's own money and a structural change in how it relates to India \u2014 the emergence of GIFT City as a single, tax-friendly, foreign-currency gateway lets NRIs build an India allocation without the old friction of NRE/NRO accounts and rupee risk, reframing the homeland from a duty to support into an investment opportunity to weigh.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 'Belong reports 2x jump in investment inflows as NRIs boost India allocation via GIFT City'", "url": "https://www.thehindubusinessline.com/money-and-banking/belong-reports-2x-jump-in-investment-inflows-as-nris-boost-india-allocation-via-gift-city/article71141202.ece"},
        {"name": "Reuters \u2014 'India File: Rupee gets diaspora lifeline \u2014 banks cash in'", "url": "https://www.reuters.com/world/india/india-file-rupee-gets-diaspora-lifeline-banks-cash-in/"}
    ]),
    "body": """For decades the financial relationship between the Indian diaspora and the homeland followed a familiar script. Money flowed one way \u2014 home \u2014 to support parents, fund a sibling's wedding, build a house in the village, or keep a savings account ticking over for an eventual return. India was a place you sent money to, out of duty and attachment. A new set of figures suggests that script is quietly being rewritten.

## A Doubling in Two Months

The signal comes from Belong, a GIFT City-based wealth platform built specifically for non-resident Indians and Overseas Citizens of India. The company says its investment inflows doubled to $6 million in March-April, up from $3 million in January-February, with the strongest demand coming from investors in the United Arab Emirates and Qatar. Founded in 2024, it has crossed 25,000 users across more than 80 countries and reports an annualised assets-under-management run rate of about $36 million, growing 20 to 30 percent month on month.

The numbers are small in the scale of India's economy, but the behaviour behind them is what the firm's leadership finds telling. "We are seeing a clear shift in investor behaviour," said co-founder and chief executive Ankur Choudhary. "Historically, the conversation was around sending money to India or maintaining assets in India for personal reasons. Today, more NRIs are approaching India as an investment destination and thinking about portfolio allocation rather than remittances alone." Crucially, the company says most of the recent money is fresh capital remitted from abroad specifically to invest \u2014 not existing rupee savings being reshuffled.

## Why GIFT City Is the Gateway

The enabler is GIFT City, the international financial centre in Gujarat that has spent years trying to become India's offshore hub. For NRIs, its appeal is practical. It lets investments be held in foreign currency, sidestepping the rupee risk that has long deterred diaspora money; it offers tax advantages on certain products; and it allows direct investing from overseas bank accounts under a single, globally aligned regulatory framework, rather than the patchwork of NRE and NRO accounts that has traditionally governed NRI finance.

On Belong's platform, US dollar-denominated fixed deposits remain the most popular product, with average ticket sizes above $20,000, while India-focused mutual funds based out of GIFT City account for around a fifth of inflows. Many users, the company says, already hold substantial global exposure through their countries of residence and are using GIFT City to deliberately dial up their India allocation \u2014 parking short-term savings in dollar deposits while channelling mutual funds toward long-term goals like retirement and children's education.

## A Bigger Backdrop

The shift dovetails with a broader official push to draw on the diaspora's wealth. The Reserve Bank of India recently moved to subsidise the hedging cost on foreign-currency non-resident deposits for three to five years, letting overseas Indians earn relatively high domestic interest rates \u2014 now around 6 to 7 percent \u2014 without taking on currency risk. Analysts at Nomura have estimated the scheme could pull in around $55 billion, and India remains the world's largest recipient of remittances, with inflows running at record levels.

A note of perspective is warranted. One platform's inflows, however fast-growing, are a sliver of the tens of billions the diaspora moves each year, and a single company's data can flatter a trend. GIFT City itself is still maturing, and its tax and regulatory advantages could evolve. The shift Choudhary describes is real but early \u2014 a change in posture more than a flood of capital, at least so far.

## Why It Matters for the Diaspora

For NRIs themselves, the development is worth watching because it is about their own money and their own relationship with India. The old model treated the homeland as an obligation; the emerging one treats it as an opportunity to be weighed against every other holding in a global portfolio. That reframing matters for a generation of diaspora professionals \u2014 in the Gulf, the US, the UK and Singapore \u2014 who are wealthier, more financially sophisticated, and more inclined to ask not just how to support family in India, but whether India belongs in their investment mix.

The infrastructure now exists to make that a low-friction choice: foreign-currency holdings, tax-efficient structures, and direct access from an overseas account through a single jurisdiction. Whether India earns a permanent place in diaspora portfolios will depend on its growth, its markets and its currency. But the question itself \u2014 invest in India, not just send money to it \u2014 is one a growing number of NRIs are now asking."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["senior exercise resistance band home", "older adult strength exercise", "elderly person exercising chair"],
                          ["senior fitness exercise home", "older adult resistance band workout"], None),
    articles[1]["slug"]: (["person exercising gym dumbbell fitness", "walking exercise outdoors fitness", "treadmill running exercise"],
                          ["fitness exercise workout person", "running walking exercise outdoors"], None),
    articles[2]["slug"]: (["Mumbai financial district skyline buildings", "Indian rupee money finance", "stock market trading screen india"],
                          ["indian rupee currency money", "financial district city skyline"], None),
}
img_captions = {
    articles[0]["slug"]: "A short, home-based strength routine improved balance and leg power in adults over 65, a Penn State trial found",
    articles[1]["slug"]: "Exercise during the weight-maintenance phase was linked to less weight regain after dieting or surgery",
    articles[2]["slug"]: "Overseas Indians are increasingly routing fresh capital into India through GIFT City investment products",
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
