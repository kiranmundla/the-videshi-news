#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 02:00 UTC batch.
Topics:
  1. "How old do you feel?" — a National Sleep Foundation study presented at
     SLEEP 2026 (>3,100 adults) finds that feeling OLDER than your chronological
     age predicts worse sleep: more insomnia, less regular sleep, more daytime
     impairment — and poorer self-reported physical health — lifestyle-health
  2. India's domestic investors now absorb foreign selling: DIIs bought ~Rs
     82,165 cr in May while FIIs sold ~Rs 32,963 cr; SIPs at Rs 30,954 cr (up
     16% YoY, 9.64 cr accounts); MF industry AUM Rs 81.58 lakh cr; equity funds'
     63rd straight month of net inflows — a structural shift in who drives the
     Indian market — markets-finance
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
    "headline": "How Old Do You Feel? Your Answer May Reveal How Well You're Sleeping, a New Study Finds",
    "subheadline": "In more than 3,100 adults, those who felt older than their actual age reported markedly worse sleep \u2014 more insomnia, less regular sleep and greater daytime fatigue \u2014 and, through that poor sleep, worse physical health, suggesting a single honest question can flag a problem long before a clinic visit does.",
    "slug": "subjective-age-feeling-older-poor-sleep-insomnia-national-sleep-foundation-sleep-2026-diaspora-20260622-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Chronically short, late and irregular nights are almost a way of life in the diaspora \u2014 split between work hours here and family calls to India \u2014 so a study showing that simply feeling older than your years is an early warning sign of poor sleep gives NRIs a quick, free self-check before fatigue hardens into ill health.",
    "sources": json.dumps([
        {"name": "Sleep (journal) / SLEEP 2026 annual meeting \u2014 National Sleep Foundation study on subjective age and sleep health", "url": "https://academic.oup.com/sleep"},
        {"name": "Medical Xpress \u2014 Feeling older than your age linked to poorer sleep and worse daytime functioning", "url": "https://medicalxpress.com/news/2026-06-older-age-linked-poorer-daytime.html"},
        {"name": "New York Post \u2014 One question may reveal whether your body is getting the rest it needs, study finds", "url": "https://nypost.com/2026/06/21/health/one-question-may-reveal-whether-your-body-is-getting-rest/"}
    ]),
    "body": """There is a question doctors rarely ask and most of us answer instinctively: not how old are you, but how old do you *feel*? New research suggests that gut answer carries real information \u2014 and that when the number runs ahead of the calendar, the culprit may be sitting in your bedroom.

## A Simple Question, a Telling Answer

A study from the National Sleep Foundation, presented at the SLEEP 2026 annual meeting and appearing in the journal Sleep, examined more than 3,100 adults. Each was asked how old they felt, and their answers were measured against their actual, chronological age. The gap between the two has a name in the research literature: "age discrepancy."

Researchers then lined that gap up against careful measures of sleep \u2014 insomnia symptoms, the regularity of people's sleep patterns, overall sleep health, and the degree of daytime impairment they reported. The pattern was striking and consistent. Adults who felt older than their years slept worse on nearly every measure: more insomnia, less regular sleep, lower overall sleep health, and more daytime fatigue and difficulty functioning.

"Adults who felt older than their actual age consistently reported poorer sleep outcomes, including more insomnia symptoms, less regular sleep, and greater daytime impairment," said principal investigator Joseph M. Dzierzewski, a clinical psychologist and senior vice president of research and scientific affairs at the National Sleep Foundation.

## Not Just a Proxy for Getting Older

The obvious objection \u2014 that older people simply feel older and sleep worse \u2014 does not hold up here. The link between feeling older and sleeping poorly remained significant even after the researchers accounted for participants' actual age, sex, race, and their levels of depression and anxiety. In other words, the *mismatch* itself, independent of how old someone truly is, was a meaningful signal.

The study went a step further with what statisticians call mediation analysis, which tries to trace how one thing leads to another. It found that feeling older than one's age was associated with poorer self-reported physical health largely *through* its links to insomnia, irregular sleep and daytime impairment. The chain ran from a subjective feeling, to measurably worse sleep, to a worse sense of one's own health.

## Why the Mind's Clock Tracks the Night

The finding fits a growing body of work on "subjective age" \u2014 how old a person feels in body and mind, which can diverge sharply from the date on their passport. Earlier experimental research from Stockholm University found that just two nights of restricted sleep made people feel more than four years older, while well-rested nights had the opposite effect. Feeling older, that research argued, is not merely a mood; it can shape behaviour, dampening energy, motivation to exercise and the will to eat well and stay social \u2014 a slow spiral that feeds back into health.

This being an observational study presented at a conference, it shows association rather than proof of cause, and it leans on people's own reports of how they sleep and feel. Sleep and subjective age almost certainly influence each other in both directions. But the practical value is hard to miss: the question "how old do you feel?" is free, instant, and may surface a sleep problem long before someone thinks to mention fatigue to a doctor.

## What to Actually Do

The fixes the researchers and sleep bodies point to are the familiar fundamentals, and they work precisely because sleep responds to routine. The American Academy of Sleep Medicine frames good sleep as adequate in duration, good in quality, appropriately timed, regular, and free of disturbances \u2014 a useful checklist. A consistent sleep and wake time, even on weekends; a wind-down that pulls screens and bright light out of the last hour; a cool, dark, quiet room; and caution with late caffeine and alcohol are the levers with the strongest evidence behind them. Persistent insomnia, by contrast, is worth taking to a clinician, as the first-line treatment is a structured behavioural therapy rather than a pill.

## Why It Matters for the Diaspora

For Indians abroad, sleep is often the first thing sacrificed. Lives are run across two clocks \u2014 the working day in New York, London or Toronto, and the WhatsApp calls, festivals and family emergencies that arrive on India's timetable, half a world out of sync. Late, short and irregular nights become normal, dressed up as the price of staying connected to both worlds.

This study offers the diaspora a quiet diagnostic. If you feel older than your years \u2014 stiff, foggy, depleted in a way the calendar does not justify \u2014 the answer may not be age at all, but the sleep you have quietly been giving up. For a community already carrying elevated risks of diabetes and heart disease, both of which are worsened by poor sleep, protecting the night is not indulgence; it is among the cheapest forms of preventive medicine available. The first step costs nothing: ask yourself how old you feel, and listen to the answer."""
})

# ============================================================
# ARTICLE 2: Domestic flows absorb foreign selling (markets-finance)
# ============================================================
articles.append({
    "headline": "Foreigners Keep Selling Indian Stocks. Indians Keep Buying \u2014 and That Has Quietly Rewired the Market",
    "subheadline": "In May, foreign investors pulled nearly Rs 33,000 crore out of Indian equities while domestic institutions poured in over Rs 82,000 crore \u2014 powered by a record Rs 30,954 crore of monthly SIP contributions across 9.64 crore accounts \u2014 a structural shift that means the old reflex of watching foreign flows to call the market is increasingly out of date.",
    "slug": "india-domestic-investors-absorb-foreign-selling-sip-record-dii-fii-structural-shift-nri-investor-20260622-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many NRIs still read foreign-investor outflows as a sell signal for Indian stocks, but a steady tide of domestic SIP money is now large enough to absorb that selling \u2014 a shift that should reframe how the diaspora thinks about timing, volatility and where the Indian market's real support now comes from.",
    "sources": json.dumps([
        {"name": "IANS / Vallum Capital \u2014 BFSI thematic funds lead May returns as SIP flows favour large caps", "url": "https://ianslive.in/bfsi-thematic-funds-lead-may-returns-as-sip-flows-favour-large-caps-report"},
        {"name": "Association of Mutual Funds in India (AMFI) \u2014 monthly mutual fund data", "url": "https://www.amfiindia.com/research-information/amfi-monthly"},
        {"name": "Reuters \u2014 Indian shares snap rally on IT drag; domestic flows cushion foreign selling", "url": "https://www.reuters.com/markets/asia/indian-shares-snap-five-session-rally-it-drag-2026-06-19/"}
    ]),
    "body": """For decades, the surest way to scare an Indian stock investor was to point at the exits and say the foreigners were leaving. Foreign institutional investors \u2014 the big overseas funds \u2014 were the market's swing factor, and when they sold, the index usually fell. That reflex is now badly out of date, and the latest monthly data shows just how thoroughly the ground has shifted.

## The Numbers Behind the Shift

In May, foreign institutional investors sold roughly Rs 32,963 crore of Indian equities. In any earlier era, that would have been a headwind strong enough to drag the market lower. Instead, it barely registered, because on the other side of the trade domestic institutional investors \u2014 mutual funds, insurers and pension money \u2014 bought about Rs 82,165 crore of stock, more than two and a half times what the foreigners offloaded.

The engine of that buying is no mystery. Monthly contributions through systematic investment plans, or SIPs \u2014 the standing instructions through which ordinary Indians drip a fixed sum into mutual funds each month \u2014 hit Rs 30,954 crore in May, up about 16 percent from a year earlier, spread across 9.64 crore active accounts. India's mutual fund industry held firm at Rs 81.58 lakh crore in assets at the end of May, and equity funds notched their 63rd consecutive month of net positive inflows. That is more than five unbroken years of money flowing in, month after month, regardless of headlines.

## Why This Is Structural, Not a Fluke

The crucial feature of SIP money is that it is largely automatic and indifferent to the news cycle. Because it arrives through standing instructions, it keeps buying through corrections, scares and selloffs \u2014 exactly when foreign money tends to flee. That gives the market a deep, steady pool of demand that simply was not there a decade ago, when domestic flows were too small to offset a serious foreign exodus.

The effect was on plain display this past week. India's IT index tumbled to a three-year low after a cautious forecast from Accenture rattled the sector, and heavyweight stocks like Reliance and HDFC Bank fell. Yet the broader market held up better than that drumbeat of bad news would once have implied, with the benchmarks still logging weekly gains, cushioned by domestic buying and easing oil prices. The foreign selling was real; its old power to dictate the index was not.

There is a quieter wrinkle in the flow data worth noting. Analysts point out that standing instructions on large-cap and flexi-cap index funds mechanically route retail savings toward the biggest, most liquid stocks, month after month, regardless of where the best returns were actually generated. In May, large-cap funds drew Rs 8,565 crore in inflows despite returning just 1.5 percent \u2014 the weakest of any category \u2014 while higher-performing small- and micro-cap funds drew far less. The autopilot that makes SIP money so stabilising also makes it somewhat indiscriminate.

## What It Does Not Mean

None of this makes the Indian market immune to gravity. Domestic flows can steady a selloff, but they cannot indefinitely defy weak earnings, stretched valuations or a genuine economic shock; a sharp enough downturn could test investors' resolve and slow the SIP machine itself. And foreign capital still matters at the margin \u2014 for currency stability, for sentiment, and for the largest, most globally exposed names. The point is narrower but important: foreign outflows alone are no longer a reliable signal of where the market is heading next.

## Why It Matters for NRIs

For the diaspora, this rewiring cuts to the heart of how many overseas Indians think about investing back home. A large share of NRIs still treats the monthly foreign-flow figure as a market thermometer \u2014 outflows mean danger, get out or stay away. That instinct is now misleading. The market's center of gravity has moved onshore, to tens of millions of domestic savers quietly buying every month.

The practical lessons are twofold. First, an NRI watching from abroad should be slower to panic at headlines about foreign selling, because the domestic bid is now deep enough to absorb a great deal of it. Second, the discipline that built this domestic juggernaut \u2014 steady, automatic, unglamorous monthly investing through ups and downs \u2014 is precisely the approach available to NRIs through their own rupee mutual fund SIPs, where permitted. The crore of small investors who reshaped the Indian market did not do it by timing foreign flows. They did it by not stopping. For diaspora investors weighing how to participate in India's long arc, that is the more durable model \u2014 and the more telling story in this month's data."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["person sleeping bed night", "insomnia tired awake bed", "alarm clock bedroom sleep"],
                          ["person sleeping in bed", "tired awake at night insomnia"], None),
    articles[1]["slug"]: (["Bombay Stock Exchange building Mumbai", "National Stock Exchange India building", "Indian rupee currency notes coins"],
                          ["indian stock market trading", "indian rupee money finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A new study links feeling older than one's age to poorer sleep, including more insomnia and greater daytime fatigue",
    articles[1]["slug"]: "Domestic mutual fund inflows have grown large enough to absorb foreign investors' selling of Indian equities",
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
