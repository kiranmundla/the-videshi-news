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
# ARTICLE 1: GLP-1 drugs cut physical activity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Skinny Jab Has a Hidden Catch. People on Ozempic Are Quietly Moving Less, Not More.",
    "subheadline": "A first-of-its-kind study tracking the Fitbit data of more than 750 adults found that daily steps and exercise both fell after they started a GLP-1 weight-loss drug \u2014 the opposite of what most assume. Because these medicines also strip away muscle, doctors warn that moving is no longer optional.",
    "slug": "glp1-ozempic-wegovy-physical-activity-decline-fitbit-endo-2026-muscle-loss-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GLP-1 jabs are sweeping through diaspora WhatsApp groups and family circles as the fix for the stubborn 'thin-fat' South Asian midriff \u2014 but this study warns that losing weight on the drug while moving less can shed the very muscle that protects against the community's early diabetes and heart disease.",
    "sources": json.dumps([
        {"name": "Endocrine Society / ENDO 2026 \u2014 Maharjan et al., physical activity declines after starting GLP-1 obesity treatment (All of Us / Fitbit cohort)", "url": "https://www.endocrine.org/news-and-advocacy/news-room"},
        {"name": "Fox News Health \u2014 Ozempic users may be making a major weight-loss mistake, new study suggests", "url": "https://www.foxnews.com/health"},
        {"name": "Drugs.com MedNews \u2014 People Walk, Exercise Less After Starting Ozempic, Zepbound", "url": "https://www.drugs.com/news/"}
    ]),
    "body": """The promise of the so-called skinny jab is seductive in its simplicity: take a weekly injection, eat less, watch the weight fall away. But a new study suggests the drugs may carry a hidden behavioural cost \u2014 people on them appear to move less, not more, even as they shed pounds.

## What the Researchers Found

The analysis, presented at ENDO 2026, the Endocrine Society's annual meeting in Chicago, is described by its authors as the first of its kind. Researchers drew on the National Institutes of Health's All of Us Research Program, which links participants' medical records with data from their Fitbit activity trackers \u2014 an unusually objective way to measure movement, free of the guesswork that plagues self-reported exercise.

From a pool of nearly 2,000 adults with obesity who started a GLP-1 medication, the team studied 753 who had enough wearable-device data to analyse. The cohort was mostly women, with an average age of about 53. The researchers compared each person's activity before and after they began treatment.

The numbers moved the wrong way. Average daily steps fell from 5,047 to 4,487 \u2014 a drop of roughly 560 steps a day. Moderate-to-vigorous physical activity, the kind that genuinely taxes the heart and lungs, slipped from 28 minutes a day to 22.

## Who Slacked Off Most

The decline was not evenly spread. Men cut back far more sharply than women, logging 986 fewer daily steps after starting a GLP-1, against 445 fewer for women. People already living with joint or muscle pain fell off a cliff \u2014 679 fewer steps a day \u2014 while those without such pain barely changed, dropping just 22 steps.

Crucially, the team found no evidence that losing weight motivated anyone to become more active. The intuitive story \u2014 lose the weight, feel lighter, start moving \u2014 simply did not show up in the data.

## Why It Matters More Than It Sounds

A few hundred steps might seem trivial. The problem is what GLP-1 drugs do to the body alongside fat loss. Medications such as semaglutide (Ozempic, Wegovy) and tirzepatide (Mounjaro, Zepbound) reduce not only fat but also lean muscle mass. Research suggests roughly a quarter to 40 percent of the weight lost on these drugs can come from lean tissue, including muscle.

Muscle is not cosmetic. It underpins metabolism, strength, balance, mobility and healthy ageing, and it is one of the body's main buffers against blood-sugar problems. Losing it while also moving less is close to a worst-case combination.

"While many assume that weight loss leads naturally to increased physical activity, our study suggests otherwise," said lead researcher Dr. Sajana Maharjan of HSHS St. John's Hospital in Springfield, Illinois. "The findings in our study reinforce that exercise cannot be optional for people taking these medications. People need targeted interventions that encourage physical activity alongside medication for obesity."

## The Caveats

This was a retrospective, observational study presented at a conference, and has not yet been through full peer review. It shows an association over time, not proof that the drugs themselves caused people to slow down \u2014 appetite suppression can reduce overall energy, and the cohort skewed female and middle-aged, so the findings may not generalise to everyone. None of it argues against the drugs, which have helped millions lose dangerous weight. It argues for pairing them with movement.

## Why It Lands for the Diaspora

GLP-1 medications have moved fast through Indian-American households and the wider diaspora, talked about across family group chats as the answer to the stubborn belly fat that standard diets never seem to shift. South Asians are especially prone to that visceral, around-the-organs fat and to losing muscle as they age \u2014 the so-called "thin-fat" pattern that drives the community's outsized rates of early diabetes and heart disease.

That makes this study's warning unusually relevant. For a population already low on muscle mass, dropping weight on a jab while sliding into a quieter, more sedentary routine could trade one health risk for another.

## What To Actually Do

If you or a family member is on a GLP-1, treat strength training as part of the prescription, not an extra. Two short resistance sessions a week \u2014 bodyweight squats, resistance bands, light weights \u2014 help defend the muscle the drug puts at risk. Keep a daily step target and watch it, since the wearable data shows the slide is easy to miss. Prioritise protein at meals to support muscle retention. And raise the issue directly with your doctor: the medicine handles appetite, but it cannot lift a single weight for you.
"""
})

# ============================================================
# ARTICLE 2: US POINTER lifestyle trial slows brain ageing (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Two-Year Brain Experiment Just Proved You Can Slow Mental Decline. The Recipe Is Boring \u2014 and It Works.",
    "subheadline": "The landmark US POINTER trial put more than 2,000 at-risk older adults on a structured plan of exercise, the MIND diet, brain training and health check-ins. After two years, the group with the most structure and accountability showed measurably better thinking and memory than those left to do it alone.",
    "slug": "us-pointer-trial-structured-lifestyle-cognition-mind-diet-exercise-brain-aging-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Dementia carries deep stigma and few answers in many Indian families, where ageing parents are cared for at home; this trial offers a low-cost, drug-free playbook \u2014 much of it built on movement, vegetables, lentils and community \u2014 that maps neatly onto how the diaspora already lives.",
    "sources": json.dumps([
        {"name": "JAMA \u2014 Structured vs Self-Guided Multidomain Lifestyle Interventions for Global Cognitive Function: The US POINTER Randomized Clinical Trial", "url": "https://jamanetwork.com/journals/jama"},
        {"name": "Alzheimer's Association \u2014 U.S. POINTER study results and implications for brain health", "url": "https://www.alz.org/us-pointer"},
        {"name": "Tallahassee Democrat \u2014 Recipe for brain health includes physical and cognitive exercise", "url": "https://www.tallahassee.com/"}
    ]),
    "body": """For decades, the science of preventing dementia has been long on hope and short on proof. Plenty of studies linked healthy habits to sharper minds, but few could show, in a rigorous trial, that deliberately changing how people live actually protects the brain. A major US study has now done exactly that \u2014 and its conclusion is as unglamorous as it is encouraging.

## The Trial

The US POINTER study, run by the Alzheimer's Association, enrolled more than 2,000 older adults across five sites in the country. Participants were aged 60 to 79, sedentary, eating a suboptimal diet, and carrying additional risk factors for cognitive decline \u2014 a family history of memory problems, cardiometabolic risk, or other established red flags. In short, exactly the people most worth helping.

They were randomly split into two groups. Both were encouraged to do the same broadly healthy things: move more, eat better, challenge their minds, stay socially engaged and keep an eye on heart health. The difference was how. One group was self-guided, given general health education and left largely to its own devices. The other followed a structured program with far more intensity, accountability and support.

## The Recipe That Worked

The structured arm followed a routine specific enough to copy. It included 30 to 35 minutes of moderate-to-intense aerobic activity four times a week, plus strength and flexibility work twice a week. It prescribed computer-based brain training three times a week, alongside other intellectually and socially challenging activities. It asked participants to follow the MIND diet \u2014 heavy on dark leafy greens, berries, nuts, whole grains, olive oil and fish, and light on sugar and unhealthy fats. And it built in regular monitoring of blood pressure, weight and lab results, often anchored by frequent peer team meetings.

## The Result

Over the nearly two-year study, both groups improved their cognition \u2014 a measure combining executive function, episodic memory and processing speed. But the structured group improved more. The additional benefit, while modest in statistical terms, closely matched the trial's pre-set target and echoed the earlier Finnish FINGER trial that inspired it. The benefit held up across several key subgroups, suggesting it was not a quirk of one type of participant.

In plain terms: a more disciplined, supported version of healthy living bought these at-risk older adults a measurable edge in protecting their thinking and memory from the decline that often creeps in with age.

## The Honest Caveats

The researchers were careful, and so should readers be. Both groups got better, partly because of "practice effects" \u2014 people tend to score higher on repeated brain tests simply through familiarity \u2014 which the analysis adjusted for but could not entirely erase. The extra benefit of the structured program, though real and statistically significant, was small, and the study ran for two years; whether it translates into fewer dementia diagnoses over a decade is the question future analyses, including brain-imaging and biomarker data, will try to answer. This is not a cure, and it is not a pill. It is evidence that effort, structure and accountability matter.

## Why This Matters for the Diaspora

Few topics carry more quiet dread in Indian families than dementia. It is often stigmatised, rarely discussed openly, and frequently managed at home by adult children and spouses with little outside support. A drug-free, relatively low-cost playbook that demonstrably helps is precisely what such families lack.

The good news is how much of POINTER's recipe already rhymes with diaspora life. The MIND diet's emphasis on greens, beans, nuts and whole grains overlaps neatly with a vegetable-forward Indian plate of sabzi, dal and millets. Multi-generational households and temple, gurdwara and community networks supply the social engagement the trial prized. The missing pieces tend to be the structured exercise, the deliberate cognitive challenge, and the routine monitoring of blood pressure and blood sugar \u2014 the very things South Asians, with their early cardiometabolic risk, most need to track anyway.

## What To Actually Do

Treat brain health as a regimen, not a vague aspiration. Aim for roughly four aerobic sessions and two strength sessions a week. Push the diet toward greens, berries, nuts, whole grains and fish, and pull it away from sugar and fried excess. Keep the mind working with genuinely effortful learning \u2014 a language, an instrument, structured puzzles \u2014 not passive scrolling. Stay socially connected on purpose. And get blood pressure, blood sugar and cholesterol checked and managed. The trial's quiet lesson is that the boring stuff, done with structure and someone to hold you to it, is the closest thing yet to brain insurance.
"""
})

# ============================================================
# ARTICLE 3: India's IT index becomes the contrarian trade (markets-finance)
# ============================================================
articles.append({
    "headline": "AI Fear Gutted India's IT Stocks by 27%. Now Some of the World's Biggest Investors Are Calling It a Bargain.",
    "subheadline": "The Nifty IT index has been hammered as investors bet that artificial intelligence will hollow out India's software outsourcing giants. But with BlackRock and others arguing the market has been 'over-punished,' the very sector everyone is fleeing is starting to look like the contrarian call of 2026.",
    "slug": "india-it-stocks-27-percent-fall-ai-disruption-tcs-infosys-contrarian-blackrock-nri-investor-20260617",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "India's IT giants are the bedrock of countless NRI portfolios and the employers of a generation of diaspora engineers \u2014 so the question of whether AI is a death sentence or an overblown panic for TCS, Infosys and Wipro is both a financial and a deeply personal one for Indian software professionals abroad.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India likely past peak outflows, AI gap its advantage, Lighthouse Canton says", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 AI, oil worries have 'over-punished' India, masked long-term investment case, BlackRock says", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "Reuters \u2014 Indian shares close flat as IT stocks decline for seventh session on AI-led disruption", "url": "https://www.reuters.com/markets/asia/"}
    ]),
    "body": """No corner of the Indian market has been punished harder in 2026 than the one that built its global reputation. The Nifty IT index \u2014 home to Tata Consultancy Services, Infosys, Wipro and their peers \u2014 has cratered as investors bet that artificial intelligence will erode the very business of writing code for hire. Now a contrarian case is forming: that the selloff has gone too far.

## The Damage

The numbers are brutal. Fears of AI-led disruption have driven the heavyweight IT index down roughly 27 percent this year, making it the single biggest drag on India's benchmarks. The Nifty 50 and Sensex were down about 11 and 13 percent on the year at their worst, with the technology rout doing much of the damage and a crude-oil spike from the Iran conflict compounding it.

At one stretch, Indian IT stocks fell for seven straight sessions, sliding more than 10 percent cumulatively. The trigger was specific: new AI tools, including a powerful release from Anthropic, revived fears that software work can be automated faster than almost any other white-collar task.

"The key concern is that productivity improvements in software engineering are occurring much faster than in non-software domains," said Sumit Pokharna, senior vice president of fundamental research at Kotak Securities \u2014 a neat summary of why the market has singled out IT for the harshest treatment.

## The Bull Case Hiding in the Wreckage

Yet some of the largest investors in the world are now arguing the punishment has overshot the crime. BlackRock, which manages more than $14 trillion globally, said this month that India's market had been "over-punished" for lacking a direct AI play and for its oil exposure \u2014 and that the selloff has masked, rather than broken, the country's long-term investment case.

"As long as India's GDP grows between 6% and 7%, that's a nice sweet spot for the economy to keep growing, keep expanding," said Natasha Sarkaria, an investment strategy lead at the firm, who argued "the rotation has gone too far." India's economy grew a stronger-than-expected 7.8 percent in the March quarter.

A sharper version of the argument comes from Lighthouse Canton, a wealth manager overseeing more than $5 billion. Its India chief investment officer, Abhay Laijawala, contends that India's lack of AI exposure \u2014 long treated as a glaring weakness \u2014 could prove an "advantage of absence." Foreign investors fled India this year and piled into South Korea and Taiwan, whose chip and memory giants briefly pushed both markets past India in total value.

"When sector concentration reaches such levels, investors tend to fatally underprice the possibility that a risk could emerge from outside the core business model," Laijawala said. South Korea and Taiwan have themselves begun logging outflows in June as investors trim crowded chip bets. India, by contrast, he argued, offers "plenty of picks and shovels" \u2014 power, data centres, electrical equipment, cooling systems, engineering and capital goods that feed the next phase of AI spending without the fragility of chip fabrication.

## The Two-Sided Risk

The bears are not obviously wrong. The threat to IT services is structural, not cyclical: if AI genuinely compresses the hours of human engineering a project needs, the headcount-and-billing model that built Indian IT comes under permanent pressure. The index has fallen for good reasons, and a cheap stock can stay cheap if its earnings are shrinking.

The bulls counter that India's services giants have weathered every prior technology shift \u2014 from mainframes to cloud \u2014 by selling the transition itself, and that AI adoption may ultimately mean more software work, not less, as enterprises scramble to rebuild their systems. Both cannot be fully right. The market is, in effect, pricing the most pessimistic version and daring contrarians to bet against it.

## What It Means for the Diaspora

For NRIs, this is not an abstract debate. India's IT majors are core holdings in countless diaspora portfolios, and they employ a generation of Indian-origin engineers around the world. The question of whether AI is an existential threat or an overblown panic is at once a portfolio decision and a career one.

The disciplined read avoids both extremes. A 27 percent drawdown has already priced in a great deal of fear, and when the planet's biggest asset managers start calling a sector "over-punished," the risk-reward has shifted from the days when these stocks traded at premium multiples. But a falling knife is still a knife. For diaspora investors with a long horizon, the case for nibbling at quality Indian IT names methodically \u2014 rather than chasing or fleeing in one move \u2014 has strengthened. The case for betting the house on a single quarter's narrative, in either direction, has not.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Ozempic semaglutide injection pen", "semaglutide injection", "Wegovy pen"],
                          ["weight loss injection pen", "ozempic medication"], None),
    articles[1]["slug"]: (["older adults exercising group", "senior citizens walking exercise", "elderly fitness class"],
                          ["seniors exercising group", "elderly people walking"], None),
    articles[2]["slug"]: (["Tata Consultancy Services building", "Infosys campus Bangalore", "Indian IT company office"],
                          ["software developers office india", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A semaglutide injection pen; a new study found activity fell after people started GLP-1 weight-loss drugs",
    articles[1]["slug"]: "Older adults exercising together; the US POINTER trial paired structured exercise with diet and brain training",
    articles[2]["slug"]: "A Tata Consultancy Services building; India's IT index has fallen about 27% in 2026 on AI-disruption fears",
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
