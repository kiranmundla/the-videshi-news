#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 14:00 UTC batch.
Topics:
  1. Harvard/BMJ 30-year, 150k study: 90-120 min/week strength training = longevity sweet spot — lifestyle-health
  2. JAMA: combined oral contraceptive pill linked to more binge-eating days in young women — lifestyle-health
  3. Sensex/Nifty snap 5-day rally as Nifty IT plunges to 3-year low on Accenture warning — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0619.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0619.bin"):
            with open("/tmp/_img_dl0619.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0619.bin")
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
# ARTICLE 1: Harvard/BMJ strength-training longevity sweet spot (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Harvard Just Found the Strength-Training Sweet Spot for a Longer Life. It Is Less Than You Think.",
    "subheadline": "Following 150,000 adults for more than three decades, researchers report that about 90 to 120 minutes of strength training a week is tied to the biggest drop in the risk of early death \u2014 and that piling on far more brings little extra benefit.",
    "slug": "strength-training-longevity-sweet-spot-90-120-minutes-harvard-bmj-150000-adults-diaspora-20260619-1400",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Strength training is the great blind spot in many Indian-origin households \u2014 elders walk for cardio but rarely lift, even as South Asians carry more body fat and less muscle for their size, raising diabetes and heart risk; a finding that just 15-20 minutes of resistance work a day moves the longevity needle makes the habit feel achievable rather than gym-bro intimidating.",
    "sources": json.dumps([
        {"name": "The BMJ \u2014 Resistance training and mortality: 30-year follow-up of ~150,000 adults (2026)", "url": "https://www.bmj.com/"},
        {"name": "Inc. \u2014 Harvard Researchers Just Determined the Longevity Sweet Spot for Strength Training", "url": "https://www.inc.com/"},
        {"name": "Fox News \u2014 Weekly weightlifting sweet spot may be linked to longer life, study finds", "url": "https://www.foxnews.com/health"}
    ]),
    "body": """For years the public-health message about exercise has been dominated by one number: 150 minutes of moderate cardio a week. Walk, jog, cycle, swim. But the weights rack \u2014 the dumbbells, the resistance bands, the bodyweight squats \u2014 has been treated as optional, a bonus for the gym-obsessed. A sweeping new study suggests that is a mistake, and it puts a refreshingly small number on how much lifting it actually takes to live longer.

## What the Researchers Did

The analysis, published in *The BMJ*, drew on roughly 150,000 adults tracked for more than 30 years \u2014 one of the longest and largest looks at strength training and survival ever assembled. Researchers connected to the Harvard T.H. Chan School of Public Health asked a question the science had largely left fuzzy: not whether strength training helps, but exactly how much of it delivers the most benefit.

The answer landed in a tighter band than many would guess. Around **90 to 120 minutes of strength training per week** \u2014 a little over a quarter of an hour a day \u2014 was associated with the steepest reduction in the risk of dying early.

## The Numbers

At that sweet spot, the study reported that strength training was tied to roughly a **13 percent lower overall risk of premature death** and about a **19 percent lower risk of dying from heart disease**, compared with doing none. Those are meaningful reductions from a habit most people could fit into two or three short sessions a week.

Crucially, the curve flattened after that. People who logged far more than two hours of lifting a week did not keep stacking up survival benefits in proportion to the extra effort. As with cardio, where the longevity payoff plateaus somewhere around 300 minutes a week, more is not endlessly better \u2014 there is a point of diminishing returns.

The lowest death risk of all was found in people who combined moderate strength training with solid aerobic activity, reinforcing a theme that runs through the recent evidence: the two kinds of exercise are partners, not rivals.

## Why Strength Training Earns Its Place

For decades, resistance training was framed as something for athletes and bodybuilders \u2014 about looks, not health. That framing is collapsing. Muscle is now understood as a metabolic organ: it soaks up blood sugar, supports insulin sensitivity, protects bone density, and guards against the frailty and falls that quietly end independence in old age. A companion study published this month in *JACC*, the journal of the American College of Cardiology, found that resistance training lowered major cardiovascular risk in women even on top of the protection from aerobic exercise.

There are caveats worth stating plainly. These are observational findings \u2014 they show a strong association, not airtight proof that lifting causes longer life \u2014 and participants reported their own exercise, which is never perfectly accurate. But the size and length of the data make the signal hard to wave away.

## Why It Matters for the Diaspora

This research lands on a real gap in Indian-origin households. The cultural default for staying healthy is the morning or evening walk \u2014 excellent cardio, deeply ingrained, and often the entire fitness routine for an entire generation. Strength training rarely features. Yet South Asians are known to carry a "thin-fat" body composition: more visceral fat and proportionally less muscle for a given weight, a pattern linked to higher diabetes and heart-disease risk that shows up earlier and at lower body weights than in many other populations.

Building and keeping muscle is one of the most direct counters to that profile \u2014 and this study says it does not require a punishing schedule or a fancy gym membership.

## What To Actually Do

Aim for **two to three short sessions a week**, totalling around 90 to 120 minutes. You do not need a gym: bodyweight squats, push-ups (against a wall or counter for beginners), chair stands, lunges, and resistance bands all count. Older parents can start with the basics \u2014 standing up from a chair without using the arms, ten times, is a legitimate strength exercise. Pair it with the daily walk rather than replacing it. The headline from three decades of data is encouraging: the dose that protects you is smaller, and more reachable, than the fitness industry has led you to believe."""
})

# ============================================================
# ARTICLE 2: Birth-control pill & binge eating in young women (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Pill May Be Quietly Driving Food Cravings, a Study of Young Women Finds",
    "subheadline": "Tracking 422 women over two menstrual cycles, researchers found binge-eating episodes rose on the days they took active birth control pills \u2014 a hormonal link that held even after accounting for mood and other medications.",
    "slug": "combined-oral-contraceptive-pill-binge-eating-young-women-jama-michigan-422-study-diaspora-20260619-1400",
    "category": "lifestyle-health",
    "vertical": "womens-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Disordered eating is heavily stigmatised and rarely discussed in Indian families, and the contraceptive pill is increasingly used by young diaspora women \u2014 so framing sudden food cravings as a possible hormonal side effect, not a failure of willpower, gives mothers and daughters a less shame-laden way to talk about both binge eating and birth control.",
    "sources": json.dumps([
        {"name": "JAMA \u2014 Combined Oral Contraceptive Use and Daily Binge Eating in Young Women (2026)", "url": "https://jamanetwork.com/journals/jama"},
        {"name": "New York Post \u2014 Binge-eating mystery affecting millions of women may finally be solved: study", "url": "https://nypost.com/2026/06/17/health/women-more-likely-to-binge-eat-due-to-a-common-medication/"}
    ]),
    "body": """For millions of women, the sudden, almost uncontrollable urge to finish a tub of ice cream or a whole packet of chips can feel impossible to explain away. New research points to an unexpected and very common suspect: the birth control pill.

## What the Study Looked At

The findings, published in *JAMA*, come from researchers who followed **422 women aged 15 to 30** drawn from the Michigan State University Twin Registry. Participants kept daily records for **49 consecutive days** \u2014 roughly two menstrual cycles \u2014 logging both their episodes of overeating and exactly which birth control pill they took that day: an active hormone pill or an inactive placebo pill from the same pack.

That design is what makes the study unusual. Rather than comparing pill users with non-users, it tracked the same women day to day, letting researchers see whether binge eating tracked with the hormones in the pills themselves.

## What They Found

It did. Binge-eating episodes were **significantly more common on the days women took active birth control pills** than on the days they took inactive ones. The association held even after the researchers accounted for negative moods, stress and the use of other medications \u2014 factors that might otherwise explain the cravings. The pill did not, notably, appear to increase preoccupation with weight; the effect was specifically on episodes of overeating.

Combined oral contraceptives are the most widely prescribed form of hormonal birth control, used by an estimated 85 percent of women at some point in their lives, which is what makes even a modest effect worth understanding.

The researchers also noticed something hopeful. As the women kept logging their eating across the seven weeks, binge-eating episodes generally **declined** \u2014 suggesting that the simple act of tracking made participants more aware of their patterns and helped them regain a sense of control.

## The Caveats That Matter

This is where restraint is essential. The study's authors stressed that the findings are **preliminary**, and that no woman should toss out her pill packet on the strength of one study. It is the first large-scale look at day-to-day binge eating across active and inactive pill days, and it raises a question rather than settling it.

Dr. Deena Hailoo, an obesity medical director at Northwell Health who was not involved in the research, called the results intriguing but "far from definitive." She noted that researchers still need to test whether other hormonal methods \u2014 IUDs, vaginal rings, implants \u2014 produce similar effects before any firm conclusions can be drawn. The takeaway is not that the pill is dangerous; it is that hormones can nudge eating behaviour, even if they do not dictate it.

## Why It Resonates in Diaspora Homes

Disordered eating remains one of the least-discussed health topics in many Indian families. Binge eating in particular is often misread as greed or a lack of discipline rather than a recognised condition linked to depression and other complications \u2014 and it disproportionately affects girls and young women. At the same time, the contraceptive pill is increasingly used by young diaspora women, often without much open conversation at home about its side effects.

Reframing sudden cravings as a possible hormonal response, rather than a personal failing, can defuse a lot of shame. For a mother and daughter, it offers a gentler entry point into two conversations that are usually avoided at once: birth control and eating.

## What To Actually Do

If you take the combined pill and notice cravings spike in a predictable pattern, that is worth noting \u2014 not panicking over. **Keep a simple food and mood journal**; the study itself suggests the awareness alone can help. Bring the pattern to a doctor rather than self-adjusting, since there are many pill formulations and alternative methods, and the right choice is highly individual. And anchor the basics that blunt cravings for everyone: meals built on protein and fibre, regular movement, adequate sleep, and support rather than self-blame."""
})

# ============================================================
# ARTICLE 3: Sensex/Nifty snap rally as IT plunges on Accenture warning (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Five-Day Market Rally Just Snapped \u2014 and It Was the IT Giants That Broke It.",
    "subheadline": "The Sensex and Nifty slid on Friday as the Nifty IT index crashed to a three-year low, dragged down by an Accenture warning that has put Infosys, Wipro and TCS squarely in investors' crosshairs.",
    "slug": "sensex-nifty-snap-five-day-rally-it-stocks-three-year-low-accenture-warning-infosys-wipro-nri-investor-20260619-1400",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian IT is the diaspora's most personal trade \u2014 many NRIs work for or hold shares in Infosys, TCS, Wipro and Accenture itself, and a three-year low in the IT index driven by cautious US client spending speaks directly to both their portfolios and their job security in the tech corridors of New Jersey, Texas and the Bay Area.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian shares snap 5-session rally on IT drag; log weekly gains on oil slide (June 19, 2026)", "url": "https://www.reuters.com/world/india/"},
        {"name": "The Hindu BusinessLine \u2014 Stock Market Live, June 19: Sensex sheds over 800 pts, Nifty slips below 24,000 as IT stocks plunge", "url": "https://www.thehindubusinessline.com/markets/"}
    ]),
    "body": """India's stock market had been on a tear. For five straight sessions the benchmarks climbed, riding a slide in oil prices and a wave of optimism after an interim US-Iran peace deal. On Friday, the run ended \u2014 and the culprit was the one sector that matters most to the Indian diaspora: information technology.

## What Happened

The BSE Sensex fell about 0.78 percent to close near 76,803, while the broader Nifty 50 slipped 0.64 percent to around 24,013, dropping back below the closely watched 24,000 mark intraday. At its worst point in the session, the Sensex was down more than 800 points.

The damage was concentrated. The **Nifty IT index plunged roughly 3.7 percent to a three-year low**, single-handedly taking the wheels off a rally that had lifted the Sensex 4.8 percent and the Nifty 4.3 percent over the previous five days. Heavyweights Reliance Industries and HDFC Bank also fell, but it was the technology names that set the tone.

## The Accenture Trigger

The selling traces back to a warning from an American company that Indian investors watch like a weather vane: **Accenture**. The consulting and IT-services giant issued a weak revenue forecast and flagged a roughly $400 million hit tied to the Middle East, sending its shares lower in US trading and dragging Infosys and Wipro down alongside them before the Indian market even opened.

Why does an American firm's outlook hammer Indian stocks? Because Accenture and India's IT majors \u2014 Tata Consultancy Services, Infosys, Wipro, HCLTech \u2014 chase the same global pool of corporate technology budgets. "Accenture has effectively confirmed that clients remain highly cautious with their wallets," said Shashwat Singh, an analyst at Bajaj Broking. "Because Indian IT firms rely heavily on the same global pipeline for discretionary tech projects, Accenture's forecast is a warning for the entire sector."

In other words, when Accenture says Western clients are tightening spending, the market reads it as a direct preview of what Infosys and TCS will report.

## The Bigger Picture

Friday's drop should be kept in perspective. Even after the slide, both benchmarks finished the **week about 1.7 percent higher**, and fifteen of the sixteen major sectors had advanced over the stretch. The pullback looked, in part, like profit-booking after a sharp rally rather than a fresh crisis \u2014 pharma and healthcare stocks even traded higher as money rotated.

The macro backdrop is mixed. The rupee held roughly flat near 94.4 to the dollar, caught between improving inflows from India's measures to attract foreign capital and a firmer dollar after the US Federal Reserve struck a hawkish tone. Brent crude, meanwhile, rebounded toward $80 a barrel as fresh doubts surfaced about the durability of the Middle East ceasefire \u2014 a reminder that the oil relief underpinning the recent rally is not guaranteed to last.

## Why the Diaspora Should Care

For Indian-origin professionals abroad, IT is not an abstract sector \u2014 it is the family business. Many NRIs work for Infosys, TCS, Wipro, Cognizant or Accenture itself, hold their shares directly or through mutual funds back home, or have relatives whose livelihoods ride on the global tech-services pipeline. A three-year low in the IT index, driven explicitly by cautious US client spending, is therefore a double signal: a hit to portfolios and a flashing yellow light on hiring and project flow in the very corridors \u2014 New Jersey, Dallas, the Bay Area \u2014 where much of the diaspora works.

## The Bottom Line

The rally's engine sputtered exactly where the diaspora feels it most. The weekly gains are intact and the sell-off has the look of profit-taking, but the Accenture warning has reopened the central question hanging over Indian IT: when will corporate clients in the West loosen their grip on tech budgets? Until that answer turns, the sector that built the modern Indian middle class \u2014 and seeded much of its diaspora \u2014 will stay under pressure. NRI investors with heavy IT exposure may want to revisit how concentrated their bets really are."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["strength training dumbbells gym", "resistance training weights exercise", "person lifting weights fitness"],
                          ["strength training dumbbells", "weight lifting fitness"], None),
    articles[1]["slug"]: (["birth control pills contraceptive", "oral contraceptive pill pack", "medication pills blister pack"],
                          ["birth control pills", "contraceptive pill pack"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "stock market trading screen India", "BSE NSE India financial"],
                          ["stock market trading screen", "indian stock exchange"], None),
}
img_captions = {
    articles[0]["slug"]: "Strength training with weights; a 30-year study of 150,000 adults found 90-120 minutes a week is the longevity sweet spot",
    articles[1]["slug"]: "Combined oral contraceptive pills; a study links active-pill days to more binge-eating episodes in young women",
    articles[2]["slug"]: "An Indian stock-market display; the Sensex and Nifty fell as IT stocks slid to a three-year low",
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
