#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 06:00 UTC batch.
Topics:
  1. Strength training and longevity: a study in the British Journal of Sports
     Medicine (>147,000 US adults, up to 30 yrs follow-up, 35,000+ deaths) finds
     90-120 min/week of resistance training tied to a 13% lower risk of death
     from any cause, 19% lower from heart disease, 27% lower from neurological
     disease — with no extra benefit beyond two hours — lifestyle-health
  2. RBI minutes: India's rate panel held the repo at 5.25% on June 5 and chose
     a "wait-and-watch" stance even as the Iran-war oil spike sent the rupee
     tumbling; some in the market now bet on HIKES (HSBC sees 50bps H2) — a
     reversal of the usual rate-cut hope, with inflation forecast lifted to 5.1%
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0622z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0622z.bin"):
            with open("/tmp/_img_dl0622z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0622z.bin")
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
# ARTICLE 1: Subjective age & sleep (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Two Hours of Lifting a Week May Be a Sweet Spot for Living Longer, a 147,000-Person Study Finds",
    "subheadline": "Tracking more than 147,000 American adults for up to three decades, researchers found that 90 to 120 minutes of strength training each week was tied to a 13 percent lower risk of dying from any cause \u2014 with sharper drops for heart and neurological disease, and, tellingly, no extra payoff for grinding out more than two hours.",
    "slug": "strength-training-resistance-90-120-minutes-week-lower-death-risk-bjsm-study-diaspora-20260622-0600",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indians abroad carry an outsized burden of diabetes and heart disease, and the gyms many already pay for go underused \u2014 so a study pinpointing two hours of weekly lifting as a longevity sweet spot offers the diaspora a concrete, time-boxed target rather than a vague call to 'exercise more.'",
    "sources": json.dumps([
        {"name": "British Journal of Sports Medicine \u2014 Resistance training, aerobic activity and long-term mortality in US adults", "url": "https://bjsm.bmj.com/"},
        {"name": "Medical News Today \u2014 90-120 minutes of strength training per week may help extend lifespan", "url": "https://www.medicalnewstoday.com/articles/strength-training-90-120-minutes-week-longer-life"},
        {"name": "NewsNation / WCIA \u2014 Resistance training associated with lower risk of death, study finds", "url": "https://www.wcia.com/news/national/lifting-weights-may-help-you-live-longer-study/"}
    ]),
    "body": """The longevity advice that sticks tends to be specific. Not "move more," but a number you can hold in your head and plan a week around. A large new study offers exactly that for strength training, and the number is reassuringly small: about two hours a week, and no more.

## What the Study Found

Published in the British Journal of Sports Medicine, the analysis drew on more than 147,000 American adults enrolled in three large, long-running health studies, some followed for up to 30 years. Over that span, more than 35,000 of the participants died, giving researchers a deep well of data to mine. Every two years, people reported how much time they spent on resistance training \u2014 lifting weights or using weight machines \u2014 alongside their aerobic activity such as walking, cycling and swimming.

When the team lined those habits up against deaths from all causes, as well as deaths specifically from heart disease, cancer, respiratory illness and neurological conditions, a clear dose emerged. People who did 90 to 120 minutes of strength training a week had a 13 percent lower risk of dying from any cause than those who did none. That same window was tied to a 19 percent lower risk of dying from cardiovascular disease and a striking 27 percent lower risk of death from neurological diseases.

## The Sweet Spot \u2014 and the Ceiling

The most useful finding may be where the benefit stopped. Pushing past two hours a week of lifting did not lower the overall risk of death any further. The curve flattened. For anyone who has felt guilty about not living in the gym, that is liberating news: the payoff is front-loaded, and the bulk of it is captured well before strength training becomes a second job.

Smaller doses helped too. Even 30 to 59 minutes of resistance training a week was associated with a 12 percent lower risk of dying from cancer specifically. And the lowest overall risk of death turned up among people who paired moderate-to-high strength training with higher levels of aerobic exercise \u2014 a reminder that the two forms of movement are partners, not rivals.

"Aerobic activity and resistance training may benefit health through different pathways, so it is important to study them separately and together," said Yiwen Zhang, a postdoctoral research fellow at the Harvard T.H. Chan School of Public Health and the study's first author. The corresponding author, Harvard professor of nutrition and epidemiology Edward Giovannucci, noted that while aerobic exercise's longevity benefits are well established, "what has been less clear is how resistance training relates to long-term mortality risk."

## How to Read It Honestly

A few caveats keep the finding in proportion. This is an observational study, so it shows association rather than proof that lifting weights causes a longer life; people who strength-train may differ in other healthy ways. The exercise data came from people's own reports, which are imperfect. And the study captured mortality, not quality of life \u2014 though strength training's benefits for muscle mass, bone density, balance and metabolic health are well documented elsewhere, and matter enormously as people age.

There was one boundary worth noting. For people already doing very large amounts of aerobic activity \u2014 roughly five to six hours of jogging or 11 hours of brisk walking a week \u2014 adding strength training did not appear to lower their risk further. For nearly everyone short of that elite volume, however, the resistance work added something aerobic exercise alone did not.

## Why It Matters for the Diaspora

For Indians settled abroad, the finding lands on a sensitive nerve. South Asians carry a well-documented, elevated risk of type 2 diabetes and heart disease, often at lower body weights than other populations, and a tendency to store fat around the organs that strength training and muscle mass help counter. Yet resistance work is frequently the part of fitness that gets skipped \u2014 crowded out by long work hours, family obligations and the assumption that a walk or the treadmill is enough.

The practical takeaway is unusually clean. Two sessions a week, 45 minutes to an hour each, covering the major muscle groups, lands a person squarely in the 90-to-120-minute window the study flags \u2014 and the data says there is little reason to do more for longevity's sake. For a community that prizes return on effort, this is an efficient bargain: a modest, finite time commitment, much of it doable at home with minimal equipment, against a measurable cut in the risks that the diaspora is already statistically more likely to face. The gym membership many already hold may be one of the better-value medical investments available, if only the weights get used."""
})

# ============================================================
# ARTICLE 2: Domestic flows absorb foreign selling (markets-finance)
# ============================================================
articles.append({
    "headline": "For Once, the Worry Is a Rate Hike: India's Central Bank Holds Steady as War-Driven Oil Tests Its Nerve",
    "subheadline": "Minutes of the June meeting show the RBI kept its key rate at 5.25 percent and chose to 'wait and watch' as an Iran-war oil spike sent the rupee tumbling and lifted its inflation forecast to 5.1 percent \u2014 even as some economists now bet the next move is up, not down, with HSBC penciling in half a point of hikes this year.",
    "slug": "rbi-minutes-rate-hold-wait-watch-iran-oil-inflation-rupee-hike-bets-nri-20260622-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs sending money home, parking savings in Indian deposits or holding rupee assets, the prospect of rate hikes rather than cuts flips the usual calculus \u2014 it can lift returns on Indian fixed deposits and steady the rupee, but it also signals that war-driven inflation, not growth, is now the force steering India's monetary policy.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India rate panel downplays case for pre-emptive rate move in meeting minutes", "url": "https://www.reuters.com/markets/asia/india-rate-panel-downplays-case-pre-emptive-rate-move-meeting-minutes-2026-06-19/"},
        {"name": "Reuters \u2014 Rupee drifts as oil dips; hawkish Fed risks, importer flows cap gains", "url": "https://www.reuters.com/markets/currencies/"},
        {"name": "AInvest \u2014 Indian Economy Faces Challenges Amidst West Asia Conflict: RBI Minutes", "url": "https://www.ainvest.com/news/indian-economy-faces-challenges-west-asia-conflict-rbi-minutes/"}
    ]),
    "body": """For most of the past two years, the question hanging over India's central bank was when it would start cutting rates to fuel growth. The minutes of its June meeting, released on Friday, mark a quiet but telling reversal: the debate now is whether the next move might be a hike. War in West Asia, and the oil-price shock it set off, has flipped the script.

## A Deliberate Pause

India's Monetary Policy Committee voted unanimously on June 5 to keep the policy repo rate \u2014 the rate at which it lends to commercial banks, and the anchor for borrowing costs across the economy \u2014 unchanged at 5.25 percent, holding its stance at "neutral." The minutes reveal a panel choosing patience over pre-emption, wary of acting on a shock whose duration no one can yet judge.

"We need to be watchful of the inflation trajectory," Governor Sanjay Malhotra wrote, adding that he preferred a "wait and watch" approach. Deputy Governor Poonam Gupta argued explicitly against a "preemptive policy pivot," saying the bank ought to "wait a bit more for global as well as weather related uncertainties to play out over the coming months." The caution cuts both ways: the committee is not rushing to cut rates to support growth, nor leaping to raise them to choke off imported inflation.

## The Oil Shock Behind the Caution

The source of the unease is a sharp rise in crude prices triggered by the Iran war, which sent the Indian rupee tumbling earlier in the period and revived fears of broad-based inflation. As a major energy importer, India feels an oil spike almost immediately \u2014 in fuel, transport and the cost of nearly everything that moves.

The numbers reflect the strain. The RBI lifted its retail inflation forecast for the financial year ending March 2027 to an average of 5.1 percent, up from 4.6 percent, while assuming an average crude price of $95 a barrel. Headline inflation stood at just under 4 percent in May, comfortably inside the bank's 2-to-6-percent tolerance band, but the forecast signals where officials fear it is heading. Growth has taken a hit too: GDP projections for 2026-27 were trimmed to 6.6 percent from 6.9 percent, citing supply-chain disruptions, elevated energy prices and the risk of a subnormal monsoon.

## Why Some Are Betting on Hikes

The war-driven oil surge prompted some in the market to wager that the RBI's next move will be upward. Analysts at HSBC went on record expecting the central bank to deliver 50 basis points \u2014 half a percentage point \u2014 of rate hikes in the second half of the year. That is a notable break from the easing bias that dominated expectations for much of the cycle.

There are crosscurrents, though, and they have turned more favourable since the meeting. Brent crude has since fallen back toward $79 a barrel, well below its conflict-period peak above $126, as signs of progress in U.S.-Iran peace talks eased fears. The rupee, hovering near 94.4 to the dollar, recently logged its best week in 11, helped by softer oil and robust foreign inflows into Indian government bonds \u2014 purchases that hit a 15-month high this month after the RBI rolled out measures to attract foreign currency. A complicating factor sits abroad: the U.S. Federal Reserve, under new Chair Kevin Warsh, has revived expectations of its own rate increases, pushing the dollar to a one-year high and limiting how far the rupee can rally.

## What It Does Not Settle

A neutral stance is, by design, a refusal to commit. The RBI has kept its options open precisely because the variables \u2014 oil, the monsoon, the Fed, the trajectory of the war \u2014 are unusually unsettled. Should oil stay subdued and the peace talks hold, the hike chatter may fade as quickly as it arrived. Should the conflict reignite and crude spike again, the pressure to act would intensify. For now, the bank is buying time.

## Why It Matters for NRIs

For the diaspora, this turn carries practical weight. Many NRIs route savings into Indian fixed deposits, NRE and NRO accounts, or rupee-denominated assets, and the direction of interest rates shapes both their returns and the currency in which those returns are held. A shift toward higher rates, rather than the cuts long anticipated, would tend to lift yields on Indian deposits and lend support to a rupee that has bruised remittance values in recent years.

But the deeper signal is about what is steering policy. India's central bank is no longer calibrating chiefly to growth; it is bracing against an external, war-driven inflation shock it cannot control. For NRIs weighing when to remit, where to park money, or how to read the rupee, the message from these minutes is to watch the price of oil and the path of the Iran conflict as closely as any domestic data \u2014 because, for the moment, those are the forces with their hands on India's monetary lever."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["weight lifting dumbbell gym", "strength training weights gym", "person exercising resistance training"],
                          ["person lifting weights gym", "strength training dumbbells"], None),
    articles[1]["slug"]: (["Reserve Bank of India building Mumbai", "Reserve Bank of India headquarters", "Indian rupee currency notes coins"],
                          ["reserve bank of india", "indian rupee money finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A new study links 90 to 120 minutes of weekly strength training to a lower risk of death from all causes",
    articles[1]["slug"]: "The Reserve Bank of India held its key rate at 5.25 percent as a war-driven oil spike clouded the inflation outlook",
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
