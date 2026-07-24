#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 10:00 UTC batch.
Topics:
  1. Exercise rivals medication and therapy for depression and anxiety — umbrella
     review of hundreds of trials, British Journal of Sports Medicine — lifestyle-health
  2. US POINTER trial: a structured, multi-domain lifestyle program (MIND diet,
     exercise, brain training, health monitoring) slowed cognitive decline in 2,111
     at-risk older adults over 2 years — Alzheimer's Association / JAMA — lifestyle-health
  3. India's IT sector hits a three-year low after Accenture's cautious outlook;
     Infosys, TCS, Wipro, HCLTech slide — what it means for the diaspora workforce
     and NRI investors — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621j.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621j.bin"):
            with open("/tmp/_img_dl0621j.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621j.bin")
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
# ARTICLE 1: Exercise rivals medication for depression/anxiety (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Exercise May Work as Well as Pills or Therapy for Depression and Anxiety, a Review of Hundreds of Trials Finds",
    "subheadline": "An umbrella analysis of hundreds of clinical studies involving tens of thousands of people concludes that regular movement \u2014 from brisk walking to yoga \u2014 can ease symptoms of depression and anxiety to a degree often comparable with medication or talk therapy.",
    "slug": "exercise-depression-anxiety-as-effective-medication-therapy-bjsm-umbrella-review-diaspora-20260621-1000",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Mental health remains heavily stigmatised in many South Asian households, where therapy can feel taboo and antidepressants are quietly resisted \u2014 so evidence that ordinary, low-cost movement can rival those treatments offers NRI families a private, accessible first step that sidesteps both the stigma and the cost and waiting lists of formal care abroad.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 Could Exercise Be the Best Natural Treatment for Depression and Anxiety?", "url": "https://knowridge.com/2026/06/could-exercise-be-the-best-natural-treatment-for-depression-and-anxiety/"},
        {"name": "British Journal of Sports Medicine \u2014 umbrella review of exercise for depression and anxiety", "url": "https://bjsm.bmj.com/"},
        {"name": "World Health Organization \u2014 Physical activity fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/physical-activity"}
    ]),
    "body": """Depression and anxiety are among the most common health conditions of modern life, touching hundreds of millions of people across every age group and corner of the world. The standard treatments \u2014 medication, counselling, or a combination of the two \u2014 help many. But they do not help everyone, they can carry side effects, and in much of the world they are expensive, hard to access, or wrapped in stigma. A large body of research now points to a remedy that is cheap, widely available and sitting in plain sight: movement.

## What the Research Found

Scientists pulled together hundreds of earlier clinical trials involving tens of thousands of participants \u2014 children and teenagers, working adults, new mothers, and older people, men and women alike. They compared many forms of activity: aerobic exercise such as running, brisk walking, swimming, cycling and dancing; strength training with weights; and gentler mind-body practices such as yoga and tai chi.

The pattern was striking and consistent. Across nearly every type of exercise, people who stayed physically active reported meaningfully lower levels of depression and anxiety than those who did not. More notably, the size of the improvement was often similar to what is seen with antidepressant medication or talking therapies. The analysis was published in the British Journal of Sports Medicine.

That last point is what gives the finding weight. Exercise is not being floated as a vague wellness tip; it is being measured against the front-line treatments doctors already prescribe, and holding its own.

## Why Movement Helps the Mind

The reasons appear to run deeper than simply "feeling good after a workout." Aerobic exercise, which raises the heart rate and breathing, improves blood flow throughout the body, including the brain. Researchers believe it nudges up the production of brain chemicals that regulate mood and dampen the stress response.

Physical activity also improves sleep, lifts energy, and delivers a quiet sense of achievement \u2014 each of which chips away at the machinery of depression. For anxiety, the study found that shorter programmes of gentle to moderate activity, lasting up to about two months, worked especially well. Practices such as yoga, stretching and slow cycling seemed to calm the body's stress response without overtaxing it.

## The Social Ingredient

One of the more human findings was that people improved most when they exercised with others or under some form of supervision. A walking group, a fitness class, a recreational team \u2014 these add encouragement and accountability, but they also break the isolation that so often accompanies depression. For people who feel lonely or withdrawn, the company can matter as much as the cardio.

The researchers also flagged particularly strong benefits for two groups under heavy strain: young adults and women who had recently given birth. Both face major life upheavals that raise the risk of mental health difficulties, and for both, movement offered a practical way to steady the mind.

## The Honest Caveats

None of this means exercise should replace professional care. For severe depression or anxiety, medication and therapy remain essential, and the researchers are explicit that movement is best seen as a powerful addition rather than a substitute. The trials also varied so widely in length, intensity and type that no single "perfect prescription" emerged \u2014 the right dose still depends on the person.

But the core message is clear and encouraging: regular movement is one of the simplest, safest and most accessible ways to protect mental health, and it asks for little more than a pair of shoes and a willingness to begin.

## Why It Matters for the Diaspora

For many in the Indian diaspora, mental health still sits in the shadows. Therapy can feel like an admission of failure, antidepressants are eyed with suspicion, and the family instinct is often to "push through" rather than seek help. That silence has a cost \u2014 immigrant communities face real pressures from isolation, long working hours, caregiving across continents and the strain of building a life far from home.

Exercise offers a way in that asks for no diagnosis and carries no stigma. A daily walk, a yoga session in the living room, a weekend cricket or badminton game with friends \u2014 these are culturally familiar, low-cost and private, and the evidence suggests they do real work for the mind, not just the body. None of it removes the need for a doctor when the struggle is serious. But for a community that often resists formal mental health care, the science points to a first step that is already within reach, and already part of the culture."""
})

# ============================================================
# ARTICLE 2: US POINTER lifestyle trial slows cognitive decline (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Structured Lifestyle Program Slowed Brain Aging in 2,000 Older Adults \u2014 and the Recipe Is Strikingly Ordinary",
    "subheadline": "In the largest lifestyle trial of its kind, the U.S. POINTER study found that a structured mix of exercise, a brain-friendly diet, mental challenge and regular health checks protected memory and thinking better than a self-guided version of the same habits.",
    "slug": "us-pointer-trial-structured-lifestyle-mind-diet-exercise-slows-cognitive-decline-2111-adults-diaspora-20260621-1000",
    "category": "lifestyle-health",
    "vertical": "brain-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry an elevated and earlier-onset risk of diabetes, high blood pressure and vascular disease \u2014 the very conditions that feed cognitive decline \u2014 and the trial's brain-protective diet leans on leafy greens, beans, nuts and whole grains that map closely onto a home-cooked Indian kitchen, making this one of the rare prevention strategies the diaspora can adopt without abandoning its own food.",
    "sources": json.dumps([
        {"name": "Tallahassee Democrat \u2014 Recipe for brain health includes physical and cognitive exercise", "url": "https://www.tallahassee.com/"},
        {"name": "JAMA \u2014 Structured vs Self-Guided Multidomain Lifestyle Interventions for Global Cognitive Function: The US POINTER Randomized Clinical Trial", "url": "https://jamanetwork.com/"},
        {"name": "Alzheimer's Association \u2014 U.S. POINTER Study", "url": "https://alz.org/us-pointer/overview.asp"}
    ]),
    "body": """For years, the advice on protecting the aging brain has felt frustratingly vague: eat well, stay active, keep your mind busy. A major American clinical trial has now put hard numbers behind that folk wisdom \u2014 and found that how seriously you pursue those habits may matter as much as the habits themselves.

## The Largest Trial of Its Kind

The U.S. POINTER study \u2014 short for the U.S. Study to Protect Brain Health Through Lifestyle Intervention to Reduce Risk \u2014 enrolled 2,111 older adults aged roughly 60 to 79. All were at increased risk of cognitive decline because of factors such as a sedentary lifestyle, family history, or markers like high blood sugar or blood pressure, but none had significant impairment at the start. Launched by the Alzheimer's Association, it is the largest lifestyle intervention trial of its kind in the world, and notably diverse: about a third of participants came from underrepresented ethnic and racial groups.

Over two years, everyone was nudged toward the same broad lifestyle. The crucial difference was how. One group followed a structured programme with set targets, regular team meetings, intensity and accountability. The other took a self-guided approach \u2014 the same goals, but largely on their own terms.

## Both Helped. Structure Helped More.

Both groups saw their cognition improve over the two years. But the structured group did measurably better, with a statistically significant edge in global thinking and memory scores. The benefit held up across key subgroups, suggesting it was not driven by one narrow slice of participants. The findings were published in JAMA.

The takeaway is subtle but important. It is not that one group followed magic habits and the other did not \u2014 both did the right things. It is that structure, accountability and a bit of intensity squeezed more protection out of the same ingredients.

## The Recipe Is Ordinary

What makes the trial quietly radical is how unremarkable the "recipe" is. The structured group followed four pillars:

- **Physical exercise:** 30 to 35 minutes of moderate-to-intense aerobic activity four times a week, plus strength and flexibility work twice a week.
- **Cognitive exercise:** a computer-based brain-training programme three times a week, alongside other mentally and socially engaging activities.
- **Nutrition:** the MIND diet \u2014 heavy on dark leafy greens, berries, nuts, beans, whole grains, olive oil and fish, and light on sugar and unhealthy fats.
- **Health monitoring:** regular checks on blood pressure, weight and key lab results.

None of it requires a prescription, a gadget or a clinic. It is the kind of routine a motivated person could assemble from a neighbourhood park, a kitchen and a public library.

## What It Does \u2014 and Doesn't \u2014 Prove

The researchers are careful. Both groups improved partly because repeated testing tends to lift scores \u2014 a "practice effect" they adjusted for. And the trial measured cognitive performance over two years, not whether anyone ultimately avoided dementia; longer follow-up, including brain-imaging and blood-biomarker analysis, is underway to clarify how durable and clinically meaningful the benefit really is.

Still, the direction is encouraging and consistent with earlier work such as Finland's FINGER trial. Multiple healthy habits, pursued together and with discipline, appear to give the aging brain real protection \u2014 and the more structured the effort, the greater the payoff.

## Why It Matters for the Diaspora

For the Indian diaspora, this lands close to home in more ways than one. South Asians develop diabetes, high blood pressure and heart disease earlier and at lower body weights than many other groups \u2014 and those are precisely the conditions that quietly erode the brain over decades. A prevention strategy that targets all of them at once is tailor-made for a community that carries this clustered risk.

The diet pillar is the easiest sell. The MIND diet's emphasis on leafy greens, beans, lentils, nuts and whole grains overlaps heavily with a traditional home-cooked Indian plate \u2014 saag, dal, rajma, vegetables and millets are already on the table. The work, for many NRI households, is less about adopting foreign foods than about leaning back into the simpler home cooking that convenience and takeout have crowded out, adding regular movement, keeping the mind engaged, and treating blood pressure and sugar as the brain issues they really are. The trial's deeper lesson may be the most useful one: doing these things casually helps, but doing them deliberately helps more."""
})

# ============================================================
# ARTICLE 3: Indian IT at three-year low after Accenture warning (markets-finance)
# ============================================================
articles.append({
    "headline": "India's IT Giants Just Hit a Three-Year Low \u2014 and a Warning From Accenture Lit the Fuse",
    "subheadline": "Infosys, TCS, Wipro and HCLTech tumbled as the Nifty IT index slid to its lowest in three years, after Accenture flagged cautious client spending and a $400 million hit from the Middle East \u2014 a chill that runs straight through the diaspora's most familiar industry.",
    "slug": "india-it-stocks-three-year-low-accenture-warning-infosys-tcs-wipro-hcltech-nri-investor-20260621-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian IT is the diaspora's home turf \u2014 it built the careers, H-1B visas and green cards of a huge share of NRIs in the United States, and its shares are a staple of NRI portfolios \u2014 so a slump driven by cautious global tech spending is both a portfolio question and a livelihood question for hundreds of thousands of Indian-origin tech workers abroad.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian shares snap 5-session rally on IT drag; log weekly gains on oil slide", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "The Hindu BusinessLine \u2014 Stock Market Live, June 19: Sensex sheds over 800 pts as IT stocks plunge", "url": "https://www.thehindubusinessline.com/markets/"},
        {"name": "USA Today / Times of India \u2014 Sensex closes over 600 points down as IT, HDFC Bank and RIL drag indices", "url": "https://www.usatoday.com/"}
    ]),
    "body": """For a brief, cheerful week, India's stock market looked like it had found its footing. A tentative U.S.-Iran peace deal had cooled oil prices, the rupee was steadying, and the benchmark indices had strung together five straight winning sessions. Then the country's technology giants \u2014 the engine of so much of corporate India and of the diaspora's professional class \u2014 brought the rally to an abrupt halt.

## A Three-Year Low

On Friday, the Nifty IT index fell about 3.7 percent to its lowest level in three years, dragging the broader market down with it. The BSE Sensex shed roughly 607 points, or 0.78 percent, to close at 76,802.90, while the Nifty 50 slipped 0.64 percent to 24,013.10. At its intraday worst, the Sensex had been down more than 940 points.

The damage was concentrated and brutal among the IT majors. Infosys was the single biggest loser on the Sensex, sliding about 6.7 percent. Tata Consultancy Services fell 3.5 percent, HCLTech dropped 2.7 percent, and Tech Mahindra ended 2.5 percent lower. The selling was not confined to technology \u2014 heavyweights HDFC Bank and Reliance Industries also fell \u2014 but IT was unmistakably the epicentre.

## The Spark: Accenture

The trigger came from across the world. Accenture, the global consulting and IT-services bellwether, delivered a cautious revenue outlook and warned of a roughly $400 million hit tied to the Middle East. Because Accenture competes for the same global pool of corporate technology budgets as India's outsourcing firms, its caution is read as a warning shot for the entire sector.

"Accenture has effectively confirmed that clients remain highly cautious with their wallets," one Mumbai analyst noted, adding that since Indian IT firms rely heavily on the same pipeline of discretionary tech projects, the forecast was "a warning for the entire sector." When the company that often reports first signals that clients are slow to spend, investors assume Infosys, TCS and Wipro will feel the same chill a quarter or two later.

## A Rally Built on Borrowed Calm

The drop is less dramatic when set against the run that preceded it. Over the previous five sessions, the Sensex had climbed about 4.8 percent and the Nifty 4.3 percent, lifted by falling oil and India's moves to defend the rupee and stem foreign outflows. Some of Friday's selling was simple profit-booking after that sprint.

But the deeper worry is structural. India's IT sector has spent the past two years contending with sluggish discretionary spending in its biggest markets, the United States and Europe, as Western clients delay or shrink technology projects amid economic uncertainty. Layer on the disruption that generative AI is bringing to the traditional outsourcing model \u2014 where revenue has long been tied to headcount \u2014 and a single cautious forecast is enough to send the whole sector to multi-year lows.

## What to Watch Next

The real test arrives with the first-quarter earnings season, when India's IT firms report their own numbers and, more importantly, their guidance for the year. If management commentary echoes Accenture's caution, the three-year low may not be the bottom. If demand proves more resilient than feared, Friday could look like an overreaction. Either way, the sector's direction now hinges on whether corporate clients abroad start loosening their technology budgets again.

## Why NRIs Should Care

No corner of the Indian market is woven more tightly into diaspora life than IT. For a generation of Indians in the United States, Britain, Canada and Australia, a job at Infosys, TCS, Wipro or Cognizant was the on-ramp \u2014 the campus placement, the onsite posting, the H-1B visa, eventually the green card and the suburban home. Hundreds of thousands of Indian-origin professionals abroad still work for these firms or their clients, which makes the sector's health a livelihood question as much as a market one.

It is also a portfolio question. Indian IT stocks are a fixture of NRI investments, both directly and through the index funds and ETFs that track the Nifty and Sensex. A three-year low can read as a buying opportunity for long-term believers in India's technology story \u2014 or as a warning that the headcount-driven outsourcing model is being slowly rewritten by AI. For diaspora investors, the prudent move is the unglamorous one: watch the upcoming earnings guidance rather than the daily swings, weigh how exposed each firm is to discretionary versus essential tech spending, and remember that a sector this central to the India story rarely stays out of favour forever \u2014 but rarely turns on a single day, either."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["people running outdoors exercise", "group jogging park exercise", "yoga class exercise outdoors"],
                          ["people running outdoors", "group exercise fitness"], None),
    articles[1]["slug"]: (["fresh leafy green vegetables healthy food", "mixed berries nuts healthy diet", "elderly couple walking exercise outdoors"],
                          ["healthy food vegetables berries", "senior couple walking"], None),
    articles[2]["slug"]: (["Infosys campus building Bangalore", "Tata Consultancy Services office building", "Bombay Stock Exchange building Mumbai"],
                          ["stock market trading screen", "office building technology company"], None),
}
img_captions = {
    articles[0]["slug"]: "A review in the British Journal of Sports Medicine found regular exercise can ease depression and anxiety as well as medication or therapy",
    articles[1]["slug"]: "The U.S. POINTER trial paired the MIND diet, rich in leafy greens, berries and nuts, with exercise and brain training to protect cognition",
    articles[2]["slug"]: "India's Nifty IT index fell to a three-year low as Infosys, TCS, Wipro and HCLTech slid after a cautious outlook from Accenture",
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
