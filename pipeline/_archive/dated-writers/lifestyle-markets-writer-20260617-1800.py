#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-17 14:00 UTC batch.
Topics:
  1. GLP-1 weight-loss drugs quietly cut physical activity (ENDO 2026) — lifestyle-health
  2. US POINTER trial: structured lifestyle plan slows brain ageing — lifestyle-health
  3. India's IT index, gutted 27% by AI fears, becomes the contrarian trade — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1400.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1400.bin"):
            with open("/tmp/_img_dl1400.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1400.bin")
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
# ARTICLE 1: Resistance-training "sweet spot" longevity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Longevity Sweet Spot Is Not the Gym Rat's. Just 90 Minutes of Weights a Week Cut Death Risk in a 30-Year Study.",
    "subheadline": "Harvard researchers followed nearly 150,000 adults for three decades and found that 90 to 119 minutes of strength training a week was the dose linked to the lowest risk of dying \u2014 from any cause, from heart disease and from brain disease. Pile on more and the benefit flattens. Pair it with cardio and it deepens.",
    "slug": "resistance-training-90-119-minutes-week-longevity-bjsm-harvard-30-year-study-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians lose muscle earlier and carry more dangerous visceral fat than most populations, yet weight training is still treated as vanity in many diaspora households \u2014 this 30-year study reframes a modest 90 minutes a week of resistance work as a longevity prescription, not gym vanity.",
    "sources": json.dumps([
        {"name": "British Journal of Sports Medicine \u2014 Zhang et al., Long-term resistance training with all-cause and cause-specific mortality (dose-response and joint associations with aerobic activity)", "url": "https://bjsm.bmj.com/"},
        {"name": "BMJ Group press release \u2014 90-120 weekly minutes of strength training may be optimal for lowering death risk", "url": "https://bmjgroup.com/90-120-weekly-minutes-of-strength-training-may-be-optimal-for-lowering-death-risk/"},
        {"name": "Drugs.com / HealthDay \u2014 Resistance Training Tied to Lower Risk for Death Across Causes", "url": "https://www.drugs.com/news/"}
    ]),
    "body": """For years, the longevity conversation has belonged to cardio \u2014 the runners, the brisk walkers, the step-counters. Strength training was for building muscle, not buying years. A new 30-year study turns that assumption on its head, and the headline number is unexpectedly small.

## What the Researchers Found

The analysis, published in the British Journal of Sports Medicine, drew on three of the largest and longest-running health datasets in the world: the Health Professionals Follow-Up Study (1992\u20132022), the Nurses' Health Study (2002\u20132021) and the Nurses' Health Study II (2003\u20132021). Together they cover 147,374 adults \u2014 31,540 men and 115,834 women \u2014 followed for up to three decades. Over that span, the researchers documented nearly 35,800 deaths.

Led by Yiwen Zhang of the Harvard T.H. Chan School of Public Health, the team asked a simple question that, surprisingly, had little solid evidence behind it: does lifting weights help you live longer, and if so, how much is enough?

Every two years, participants reported how many minutes they spent each week on strength training \u2014 weights, machines, or bodyweight moves such as push-ups, squats and lunges \u2014 and on aerobic activity. The researchers then tracked who died, and of what.

## The Number That Matters

The benefit did not climb endlessly with effort. It peaked in a narrow band: 90 to 119 minutes of strength training a week. At that dose, participants had a 13 percent lower risk of death from any cause (hazard ratio 0.87), a 19 percent lower risk of dying from cardiovascular disease (HR 0.81) and a striking 27 percent lower risk of death from neurological diseases such as dementia and Parkinson's (HR 0.73).

Crucially, going beyond 120 minutes a week added nothing measurable to the all-cause benefit. The relationship was what statisticians call a "quadratic" curve \u2014 it rises, then plateaus. More time under the barbell did not buy more years.

Cancer told a different story. There, the protective signal showed up only at lower doses \u2014 1 to 29 minutes a week (HR 0.91) and 30 to 59 minutes (HR 0.88) \u2014 with the clearest links to lower colorectal, bladder and breast cancer mortality, though the case numbers were small.

## Cardio Plus Weights Is the Real Winner

The single most powerful finding was about combination. People who logged high levels of aerobic activity alongside one to two hours of weekly strength training had the lowest mortality of all \u2014 up to 58 percent lower than those who were inactive. As the authors put it, the results "support current recommendations encouraging both types of activity to maximize longevity benefits."

In other words, this is not an argument for abandoning the morning walk. It is an argument for adding two short strength sessions to it.

## The Caveats

This is observational research, so it shows association, not proof of cause. Strength-trainers tended to be younger, leaner and healthier to begin with, and the researchers adjusted for those factors but cannot eliminate them entirely. Exercise was self-reported, which invites error. And the cohorts \u2014 health professionals and nurses \u2014 are not a perfect mirror of the general population. Still, the size, the 30-year horizon and the consistency across men and women make the signal hard to dismiss.

## Why It Lands for the Diaspora

For Indian-American and wider diaspora families, the finding is unusually pointed. South Asians are prone to sarcopenia \u2014 age-related muscle loss \u2014 and to the "thin-fat" body type, where a normal-looking frame hides excess visceral fat and too little muscle. Both raise the risk of the early diabetes and heart disease that stalk the community. Muscle is one of the body's main glucose sinks; building and keeping it is a direct hedge against the diaspora's signature metabolic problems.

Yet in many desi homes, lifting weights is still seen as the preserve of bodybuilders and the young, not a health staple for parents and elders. This study reframes it. Ninety minutes a week is two 45-minute sessions, or three half-hour ones \u2014 achievable with resistance bands, light dumbbells or bodyweight at home, no gym membership required.

## What To Actually Do

Aim for the sweet spot, not the extreme: roughly 90 to 120 minutes of resistance work across two or three sessions a week. Cover the major muscle groups \u2014 legs, back, chest, core. Keep the aerobic base \u2014 brisk walking, cycling, swimming \u2014 because the combination, not either alone, produced the largest gains. For older relatives, start light and prioritise form over load; even modest amounts cut risk. And treat consistency over decades, not intensity in any single week, as the thing that actually moves the needle.
"""
})

# ============================================================
# ARTICLE 2: "Just Rise" sit-to-stand lowers BP in post-menopausal women (lifestyle-health)
# ============================================================
articles.append({
    "headline": "You Do Not Need to Sit Less. You Need to Stand Up More Often. A New Trial Found Rising From Your Chair Lowers Blood Pressure.",
    "subheadline": "A UC San Diego study put post-menopausal women through three months of small changes and found something counterintuitive: simply standing up more frequently \u2014 about 25 extra times a day \u2014 nudged down blood pressure, while merely sitting less did not deliver a clear win.",
    "slug": "sit-to-stand-frequency-blood-pressure-postmenopausal-women-ucsd-rise-trial-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Diaspora women, especially after menopause, carry an outsized burden of hypertension and heart disease that often goes under-treated \u2014 and this study offers a no-cost, no-equipment habit that fits the desk-bound, family-juggling reality of many Indian-American households.",
    "sources": json.dumps([
        {"name": "UC San Diego Today / Herbert Wertheim School of Public Health \u2014 Just Rise: Study Finds Frequent Standing May Boost Heart Health After Menopause", "url": "https://today.ucsd.edu/"},
        {"name": "Circulation / American Heart Association \u2014 sit-to-stand and sit-less randomized trial in post-menopausal women (LaCroix et al.)", "url": "https://www.ahajournals.org/journal/circ"}
    ]),
    "body": """The advice to "sit less" has become a wellness clich\u00e9 \u2014 stand at your desk, take the stairs, do not binge an entire season in one slump. But a new clinical trial suggests the more useful instruction is subtly different, and easier to act on: stand up more often. Not stand longer. Stand up more frequently.

## What the Researchers Tested

The study, led by researchers at the University of California San Diego's Herbert Wertheim School of Public Health, focused on post-menopausal women \u2014 a group at sharply rising risk of high blood pressure and heart disease as the protective effects of oestrogen fade. Participants were divided into three groups over a three-month intervention.

One group was coached to "sit less" \u2014 to cut their total sitting time during the day. A second, the "sit-to-stand" group, was asked to focus on a single behaviour: rising from a seated position more often, regardless of how long they ultimately stood. A third control group received general health tips but was not asked to change its habits.

The design let the researchers separate two things that usually get lumped together: reducing sedentary time, and the simple mechanical act of standing up.

## The Counterintuitive Result

The "sit less" group succeeded at sitting less \u2014 cutting about 75 minutes of daily sitting \u2014 and showed some improvement in blood pressure. But the change did not reach statistical significance. Reducing sitting time, on its own, was not enough to move the needle convincingly.

The "sit-to-stand" group told a clearer story. These women increased the number of times they rose from a chair by an average of 25 a day. In return, their diastolic blood pressure \u2014 the lower number, which reflects pressure between heartbeats \u2014 fell by 2.24 mmHg more than the control group's. That is short of the 3\u20135 mmHg drop doctors consider clinically meaningful, but it is a measurable, real change achieved in just three months, with no medication and no equipment.

Notably, neither approach significantly improved blood sugar over the three months \u2014 a reminder that different health markers respond to different interventions and timelines.

## Why Standing Up Beats Standing Still

The finding fits a growing and sometimes confusing body of research. Other studies have found that simply standing for long stretches \u2014 the standing-desk craze \u2014 does little for blood pressure and may even raise the risk of circulatory problems like varicose veins. What seems to matter is the transition: the muscular act of getting up, which engages the large muscles of the legs and core, pumps blood and briefly raises the heart rate. It is movement, not posture, that does the work.

"What excites me most about this study is that women set their own goals and made a real difference in their sitting behaviors," said co-author Andrea Z. LaCroix, a distinguished professor at the school. "With a little coaching, we can teach ourselves to sit less and it makes a tangible difference to our short- and long-term health."

She offered a concrete target: "Stand up from sitting 25 extra times per day, like two times per hour over 12 hours \u2014 may be doable for so many of us."

## The Caveats

This was a modest, three-month trial in a specific group \u2014 post-menopausal women \u2014 so the findings may not transfer directly to men or younger people. The diastolic improvement, while real, fell short of the clinically significant threshold, and the researchers themselves suspect bigger benefits may need more than three months to emerge. They have applied for a new grant to test both behaviours over a longer period in older men and women.

## Why It Lands for the Diaspora

High blood pressure is one of the quiet epidemics of the Indian diaspora, and it is especially under-recognised in women, who often put family health ahead of their own. Many diaspora women in their fifties and sixties juggle desk jobs, caregiving and long sedentary stretches, while hypertension goes unmonitored until it shows up as something serious.

The appeal of this study is its sheer accessibility. It asks for nothing to buy and no block of time to carve out \u2014 just a behavioural nudge that folds into an ordinary day. For a community where heart disease strikes early and often, a free habit with a measurable payoff is worth taking seriously.

## What To Actually Do

Set a simple rule: stand up at least twice an hour. Use the rhythms of the day as cues \u2014 rise during every phone call, every ad break, every time the kettle boils, every time a WhatsApp message lands. Aim, as the researchers suggest, for roughly 25 extra stands a day. Pair it with whatever walking you already do; the goal is to break up sitting with frequent transitions, not to swap a sitting marathon for a standing one. And if blood pressure is already a concern, keep monitoring it \u2014 this is a complement to medical care, not a replacement.
"""
})

# ============================================================
# ARTICLE 3: India markets longest winning streak in 2 months as oil eases (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Markets Just Logged Their Longest Winning Streak in Two Months. The Engine Is Cheaper Oil \u2014 and a Fragile Iran Deal.",
    "subheadline": "The Nifty 50 closed above 24,000 for the first time in weeks as benchmarks rose for a fourth straight session, riding a near-three-month low in crude after a US-Iran peace deal promised to reopen the Strait of Hormuz. For NRIs, falling oil is rocket fuel for the rupee and the inflation outlook \u2014 but the truce is far from sealed.",
    "slug": "india-markets-four-session-winning-streak-nifty-24000-oil-three-month-low-us-iran-deal-nri-investor-20260617",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs, this rally is a three-way win and a warning at once \u2014 cheaper oil eases India's import bill and supports the rupee that governs every remittance, while the fragility of the Iran truce means the gains rest on a deal that could still unravel.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's stock benchmarks log longest winning run in 2 months as oil prices ease", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 Indian shares climb on Gulf peace deal tracking global rally", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 Oil prices fall to fresh three-month low on hopes interim US-Iran deal will reopen Hormuz", "url": "https://www.reuters.com/business/energy/"}
    ]),
    "body": """India's stock market has been on its best run in two months, and the story behind the rally can be told in one word: oil.

## What Happened

On Wednesday, India's benchmarks rose for a fourth consecutive session \u2014 their longest winning streak in two months. The Nifty 50 added 0.4 percent to close at 24,085.70, reclaiming the psychologically important 24,000 mark, while the BSE Sensex gained 0.45 percent to 77,155.62. Across the four-session run, the two indexes have climbed roughly 4 percent and 4.5 percent respectively.

The fuel for the move was sitting in the commodities pits. Brent crude hovered around $79 a barrel after dropping 5.1 percent in the previous session to close near three-month lows. Just days earlier, oil had been trading above $90 for almost the entire span of the Iran war, which began in late February.

## The Catalyst: A Fragile Peace

The trigger was geopolitical. US President Donald Trump announced an interim deal to end the US-Israeli war with Iran, declaring the Strait of Hormuz \u2014 the chokepoint through which about 20 percent of the world's oil flows \u2014 would reopen. "Ships of the world, start your engines. Let the oil flow," he posted. A senior US official said Washington would waive sanctions on Iranian oil under the deal, raising the prospect of millions of additional barrels returning to global supply.

Markets did the math instantly. India imports the overwhelming majority of the crude it consumes, making it one of the biggest beneficiaries of any sustained drop in prices. "Lower crude prices are positive for Indian equities, for earnings in sectors that benefit from lower energy costs, while also supporting the macroeconomic fundamentals in the world's third largest oil importer," said Vikas Satija of Shriram Wealth.

## Why Oil Is Everything for India

For India, the price of crude is not just a line item \u2014 it is the master variable. Cheaper oil shrinks the import bill, narrows the trade deficit, takes pressure off inflation and, crucially, supports the rupee. In recent sessions the rupee has firmed, recovering from the bruising it took during the war, and India's 10-year bond yield has eased.

The backdrop makes the relief especially welcome. The Reserve Bank of India recently held its key rate at 5.25 percent but trimmed its growth forecast and raised its inflation projection to 5.1 percent, flagging stagflation risk from the conflict. It also rolled out measures to attract dollar inflows, including a capital-gains tax exemption for foreign investors on government-securities interest. Foreign investors had pulled a record $30 billion out of India in 2026 \u2014 a tide that some strategists now believe could begin to reverse if oil and the rupee stabilise.

## The Bull Case, and the Catch

Some on the Street are openly optimistic. "Now that the Iran war appears to be nearing an end, investors have a significant source of comfort," said Gaurav Bhandari of Monarch Networth Capital, who argued Indian equities "could be set for a strong four-to-six months, provided monsoon risks recede," and sees the Nifty reaching 27,000\u201328,000 by year-end. The India VIX, the market's fear gauge, has crashed to a three-month low, signalling that traders are pricing in calmer days.

But the foundation is thinner than the optimism suggests. The deal is an interim one, extending a tenuous ceasefire by 60 days, and the hardest questions \u2014 Iran's nuclear program chief among them \u2014 remain unresolved. Industry officials warn that even in the best case, Gulf energy exports could take weeks or months to normalise. Investment banks including Goldman Sachs, Morgan Stanley and Citi have lowered oil forecasts, but a flare-up could send crude \u2014 and Indian inflation \u2014 straight back up.

## What It Means for the Diaspora

For NRIs, this is a three-sided story. First, the rupee: a firmer currency means remittances buy fewer rupees, so those sending money home may find the window narrowing as the rupee strengthens on cheaper oil. Second, portfolios: diaspora investors holding Indian equities or India-focused funds have just enjoyed a sharp bounce, and the macro tailwind of low oil is genuinely supportive of earnings. Third, the risk: the entire rally is leveraged to a fragile truce. A diaspora investor reading the headlines should treat the four-session surge as a relief rally built on a deal that is signed in spirit but not yet sealed in fact.

The disciplined posture is the familiar one. The improvement in India's macro picture is real and worth respecting, but betting heavily on a 60-day ceasefire holding is a bet on geopolitics, not fundamentals. For long-horizon NRI investors, the case for staying invested in India has strengthened; the case for chasing this particular spike has not.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["strength training dumbbell exercise", "resistance training weights gym", "person lifting dumbbells"],
                          ["strength training weights", "dumbbell workout"], None),
    articles[1]["slug"]: (["woman standing up from chair", "older woman exercise home", "senior woman standing"],
                          ["woman getting up from chair", "older woman at home"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "BSE building Dalal Street", "Mumbai stock exchange"],
                          ["mumbai stock exchange", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A person training with dumbbells; a 30-year study found 90 to 119 minutes of weekly strength work cut death risk most",
    articles[1]["slug"]: "An older woman rising from a chair; a UCSD trial found standing up more often lowered blood pressure",
    articles[2]["slug"]: "The Bombay Stock Exchange in Mumbai; India's benchmarks logged their longest winning run in two months as oil eased",
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
