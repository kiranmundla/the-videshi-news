#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 10:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Exercise during the weight-maintenance phase reduces weight regain — a new
     Scientific Reports systematic review/meta-analysis (11 RCTs, 568 people)
     found exercisers regained ~2.81 kg less than controls. — lifestyle-health
  2. Maternal heart health linked to child developmental delay — a study of 8,000+
     mothers (Life's Essential 8 framework) found kids of mothers with low
     cardiovascular health had a 62% higher risk of developmental delay at age 4.
     — lifestyle-health
  3. India's weak foreign direct investment — net FDI fell to just $7.7bn in
     FY26 vs Vietnam's $20.2bn and Indonesia's $24.2bn; CII chief urges faster
     arbitration/dispute resolution and deeper reform to lift growth to 8-10%.
     — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1010z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1010z.bin"):
            with open("/tmp/_img_dl1010z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1010z.bin")
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
# ARTICLE 1: Exercise prevents weight regain (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Hardest Part of Losing Weight Is Keeping It Off \u2014 a New Review Says Exercise Is the Glue",
    "subheadline": "Pooling 11 clinical trials, researchers found that people who kept exercising after losing weight regained nearly three kilograms less than those who stopped \u2014 a small but remarkably consistent edge in the war against the rebound.",
    "slug": "exercise-prevents-weight-regain-meta-analysis-scientific-reports-11-trials-maintenance-phase-diaspora-20260624-1000",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Crash diets and quick weight loss before a wedding or a trip home are a familiar ritual in many Indian families \u2014 and so is the quiet return of the kilos months later; this review reframes the goal from losing weight to defending it, a message that matters for a diaspora facing high rates of diabetes and heart disease.",
    "sources": json.dumps([
        {"name": "Scientific Reports (2026) \u2014 Wang, Chen, Xu & Dai, 'The effects of exercise interventions on weight regain after weight loss: a systematic review and meta-analysis' (DOI: 10.1038/s41598-026-57804-8)", "url": "https://www.nature.com/articles/s41598-026-57804-8"},
        {"name": "News-Medical \u2014 'Lost weight is less likely to return when exercise follows obesity treatment'", "url": "https://www.news-medical.net/news/20260623/Lost-weight-is-less-likely-to-return-when-exercise-follows-obesity-treatment.aspx"}
    ]),
    "body": """Anyone who has dieted knows the cruel arithmetic of weight loss: the pounds come off with effort, then creep back with a vengeance. The first act \u2014 losing the weight \u2014 gets all the attention. The second act \u2014 keeping it off \u2014 is where most people quietly lose the plot. A new analysis pulling together a decade of clinical trials lands on a simple, if unglamorous, conclusion: the thing that holds weight loss in place is exercise.

## What the Researchers Did

The study, published in the journal Scientific Reports, is a systematic review and meta-analysis \u2014 a method that gathers many separate trials and pools their results to see what the weight of evidence actually says. The authors searched five major research databases and applied a strict filter: they wanted only randomized controlled trials, the gold-standard design, that tested exercise specifically during the maintenance phase, the period after someone has already lost weight.

That focus matters. Plenty of research looks at exercise as a way to shed kilos in the first place, where its effect is famously modest. Far less has examined whether exercise helps people hold the line afterwards. In the end, eleven trials involving 568 participants met the bar. The people in them had already lost weight \u2014 through low-calorie diets or, in some studies, bariatric surgery \u2014 and were then randomly assigned either to an exercise program or to a control group, with interventions running from roughly twelve to fifty-three weeks.

## The Headline Number

The pooled result was clear and, unusually for this kind of research, statistically clean. Participants who exercised during the maintenance phase regained significantly less weight than those who did not \u2014 a mean difference of about 2.81 kilograms, or roughly six pounds. Crucially, the eleven studies pointed in the same direction with essentially no statistical heterogeneity, meaning the trials agreed with one another despite differing in their participants, their weight-loss methods and their exercise routines. When findings hold up across such variety, researchers take them more seriously.

The exercise itself was nothing exotic. Across the trials it included resistance training, aerobic fitness work, walking, stationary cycling and even deep-water running. Adherence was generally good, and there was no meaningful difference in drop-out rates between the exercise and control groups \u2014 a reassuring sign that people can actually stick with these programs.

## What It Doesn't Settle

The authors are careful to keep their claim modest. The benefit, while consistent, is small \u2014 a few kilograms, not a transformation. The evidence on body fat specifically was weaker and inconclusive: while exercisers tended to lose more fat mass, that result did not reach statistical significance once the variation between studies was accounted for. With only eleven trials, the researchers could not reliably test for publication bias, and they flagged that the exercise prescriptions were a mixed bag, the adherence definitions varied, and some of the underlying studies were older or carried a risk of bias.

In short, exercise helps you keep weight off, but the science cannot yet say precisely which type, how much, or for how long delivers the best protection. The authors call for longer trials with standardized exercise plans and objective tracking to nail those details down.

## Why It Lands Now

The timing is pointed. As GLP-1 drugs like Ozempic and Wegovy drive dramatic weight loss for millions, doctors are increasingly worried about what happens when people stop taking them \u2014 and about the muscle lost along with the fat. A separate strand of recent research has warned that many people on these drugs are moving less, not more, which can undercut the benefit. This meta-analysis slots neatly into that debate: whether the weight came off through diet, surgery or medication, staying active afterwards appears to be a hedge against the rebound.

The practical message is refreshingly old-fashioned. The goal is not a punishing gym regimen but a durable habit \u2014 a mix of regular movement and some strength work that you can sustain after the diet ends and the motivation fades.

## Why It Matters for the Diaspora

In many Indian and South Asian households, weight loss tends to be event-driven \u2014 a crash diet before a wedding, a son's graduation, or a long-awaited trip back home \u2014 followed by a slow, almost inevitable return to old habits and old numbers on the scale. That pattern is especially costly for a community that carries an outsized burden of type 2 diabetes, high blood pressure and heart disease, often at lower body weights than other populations. For South Asians, even modest, lasting weight control can meaningfully shift cardiometabolic risk.

This research quietly reframes the whole project. The win is not the dramatic before-and-after photo; it is the unremarkable maintenance that follows. A brisk daily walk, a couple of strength sessions a week, cycling to the shops \u2014 the kinds of activity woven into ordinary life rather than reserved for a crash program \u2014 are precisely what the data favours. For diaspora families who already organise life around community, the most durable version may be the most social one: a regular walking group, a weekend badminton game, a shared routine that outlasts any single diet. The kilos, this evidence suggests, are kept off not in a burst of willpower but in the steady, boring rhythm of staying active."""
})

# ============================================================
# ARTICLE 2: Maternal heart health & child developmental delay (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Mother's Heart Health Before Birth May Shape Her Child's Development, a Study of 8,000 Finds",
    "subheadline": "Children of mothers with poor cardiovascular health had a 62% higher risk of developmental delay by age four \u2014 across communication, movement, problem-solving and social skills \u2014 pointing to pregnancy as one of the earliest windows to protect a child's future.",
    "slug": "maternal-cardiovascular-health-child-developmental-delay-62-percent-lifes-essential-8-study-diaspora-20260624-1000",
    "category": "lifestyle-health",
    "vertical": "maternal-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian women carry unusually high rates of gestational diabetes, high blood pressure and heart disease, often undiagnosed, while pre-pregnancy health is rarely discussed in diaspora families fixated on the baby rather than the mother; this research makes a mother's own heart health a quiet but powerful lever over her child's lifelong development.",
    "sources": json.dumps([
        {"name": "New York Post \u2014 'Developmental issues in kids spike 62% when mom has key health issue'", "url": "https://nypost.com/2026/06/23/health/maternal-heart-health-linked-to-child-development/"},
        {"name": "Journal of the American Heart Association \u2014 'Maternal Early-Pregnancy Cardiovascular Health and Offspring Emotional, Behavioral, and Cognitive Outcomes in Adolescence'", "url": "https://www.ahajournals.org/doi/10.1161/JAHA.123.030220"}
    ]),
    "body": """We tend to think a child's development begins at birth. A growing body of research suggests it begins much earlier \u2014 and that one of the strongest early signals may be something easy to overlook: the mother's own heart health, measured before and during pregnancy. A large new study adds striking weight to that idea, finding that children born to mothers with poor cardiovascular health were markedly more likely to show developmental delays by the age of four.

## How the Study Was Done

Researchers analysed data on more than 8,000 mothers, scoring each one's cardiovascular health using the kind of comprehensive checklist cardiologists increasingly rely on. The score drew on eight factors: diet, physical activity, smoking, sleep, body mass index, blood lipids such as cholesterol, blood glucose \u2014 a marker of diabetes risk \u2014 and blood pressure. Based on those measures, the mothers were sorted into groups with high, moderate or low cardiovascular health.

The team then tracked the children and assessed them for developmental delays at age four, looking across five domains: communication, gross motor skills (whole-body movements like walking and jumping), fine motor skills (the precise movements of the hands and fingers), problem-solving, and personal-social skills.

## What They Found

The gap was large. Among mothers with high cardiovascular health, only 8.8 percent had children with developmental delays at age four. Among mothers with low cardiovascular health, that figure nearly doubled to 16.8 percent. Put in terms of risk, children of mothers with poor heart health had a 62 percent higher risk of developmental delay.

The effect was not confined to one narrow area. Lower maternal heart health was linked to delays across the board \u2014 communication, gross and fine motor skills, problem-solving and personal-social development \u2014 with personal-social skills the most affected of all. "Maternal heart health may play an incredibly important role in shaping long-term neurodevelopment outcomes," the researchers said in presenting the work.

## The Likely Mechanism

Why would a mother's cardiovascular health ripple into her child's brain development? The researchers point to the cascade of complications that poor heart health sets in motion during pregnancy. A mother in suboptimal cardiovascular shape is at significantly higher risk of adverse pregnancy outcomes \u2014 preeclampsia, gestational hypertension and spontaneous preterm delivery among them \u2014 which can cut short the time a baby has to develop fully in the womb.

There is also a more direct, mechanical explanation. A healthy heart pumps blood more effectively to the placenta, the organ that ferries oxygen and nutrients to the growing fetus. When that delivery system is compromised, the developing brain may simply receive less of what it needs at a critical time. The finding dovetails with a wider literature: a separate study published in the Journal of the American Heart Association found that mothers with suboptimal early-pregnancy cardiovascular health had children with higher odds of attention, behavioural and cognitive difficulties in adolescence.

## The Caveats

As with most studies of this kind, this is observational research, which can establish a strong association but cannot by itself prove that poor maternal heart health directly causes developmental delay. Many factors that shape both a mother's health and a child's development \u2014 income, education, access to care, environment \u2014 can be difficult to disentangle completely, though researchers adjust for as many as they can. And developmental delay at age four is not destiny; many children catch up.

What the study does offer is a hopeful reframing. Cardiovascular health is among the most modifiable things in medicine. Diet, movement, sleep, blood pressure and blood sugar can all be improved \u2014 and the research suggests that doing so before and during pregnancy may be, as the authors put it, one of the earliest opportunities to influence lifelong health outcomes for both mother and child.

## Why It Matters for the Diaspora

For South Asian families, this lands on sensitive and important ground. Women of Indian origin carry unusually high rates of gestational diabetes, high blood pressure and heart disease, frequently developing them at lower body weights and younger ages than other groups, and frequently undiagnosed until a pregnancy forces the issue. Yet in many diaspora households the conversation around pregnancy fixates almost entirely on the baby \u2014 the rituals, the diet for the child, the preparations \u2014 while the mother's own metabolic and cardiovascular health goes unexamined until something goes wrong.

This research argues for flipping that lens. A prospective mother's heart health is not just her concern; it is, on this evidence, an early investment in her child's brain. The practical takeaways are accessible and culturally familiar: a home-cooked, vegetable-and-pulse-forward diet over packaged convenience food, regular movement, attention to sleep, and \u2014 critically \u2014 getting blood pressure and blood sugar checked before trying to conceive, not after a complication appears. For a community that pours so much love and resource into its children, the message is that some of the most powerful protection begins with the mother, well before the baby arrives."""
})

# ============================================================
# ARTICLE 3: India's weak FDI / reform push (markets-finance)
# ============================================================
articles.append({
    "headline": "India Wants to Grow at 10%. First It Has to Explain Why Foreign Investment Has Dried Up.",
    "subheadline": "Net foreign direct investment fell to just $7.7 billion last year \u2014 a fraction of Vietnam's and Indonesia's \u2014 and India's top industry lobby says slow courts and five-year arbitration waits are scaring off the capital the country needs.",
    "slug": "india-weak-net-fdi-7-billion-cii-arbitration-dispute-resolution-reform-growth-nri-investor-20260624-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "NRIs are among the most natural foreign investors in India \u2014 through direct stakes, startups and property \u2014 yet the same slow courts and tangled dispute resolution that deter global capital are exactly what burn diaspora investors who get stuck in years-long litigation back home, making this a story about whether India can finally be trusted with their money.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'Indian industry lobby chief pushes for quicker dispute resolution to boost investment'", "url": "https://www.reuters.com/world/india/indian-industry-lobby-chief-pushes-quicker-dispute-resolution-boost-investment-2026-06-23/"},
        {"name": "Reuters \u2014 'IT, metals drag Indian shares; weak business data, monsoon worries weigh'", "url": "https://www.reuters.com/markets/asia/"},
        {"name": "The Hindu BusinessLine \u2014 'Stock Market Today Live, June 24'", "url": "https://www.thehindubusinessline.com/markets/stock-markets/"}
    ]),
    "body": """India loves to talk about its growth. It is the fastest-expanding major economy, the world's most populous nation, the supposed factory-in-waiting as companies look beyond China. But behind the optimism sits an awkward number that refuses to cooperate: foreign direct investment, the long-term money that builds factories and creates jobs, has slowed to a trickle.

## The Number That Doesn't Fit the Story

In the year ended March 2026, India attracted net foreign direct investment of just $7.7 billion. Set against the size of the economy and the scale of its ambitions, that figure is startlingly small \u2014 and it looks worse against the neighbours India likes to be compared with. Vietnam pulled in $20.2 billion and Indonesia $24.2 billion in 2024, each a far smaller economy than India's.

The gap between gross and net inflows tells part of the story. Money is still coming in, but a growing share is also going out, as some foreign companies repatriate profits or sell down stakes and exit. The result is that the capital actually staying and being put to work has thinned dramatically \u2014 at precisely the moment India is trying to position itself as the prime destination for global supply chains diversifying away from China.

## Why Capital Hesitates

This week R. Mukundan, president of the Confederation of Indian Industry \u2014 one of the country's most influential business lobbies \u2014 put a blunt finger on one of the reasons: India is too slow and too uncertain a place to resolve a dispute. "Arbitration has got to close in a matter of months," he said in an interview, arguing that India needs to build the capacity to settle disputes as quickly as rival jurisdictions such as Singapore.

He singled out a rule that requires foreign investors to spend up to five years pursuing remedies in India's own courts before they can take a dispute to international arbitration. "Even three years is too long," Mukundan said. For a global company weighing where to put a multi-billion-dollar plant, the prospect of being trapped for half a decade in an unpredictable legal system is a powerful deterrent \u2014 and a reason to choose Vietnam or Indonesia instead.

The criticism comes as India considers changes to its 2016 bilateral investment treaty framework, the legal architecture that governs how foreign investors are protected and how their disputes are handled. The five-year domestic-remedy requirement is one of the provisions under scrutiny.

## The Bigger Reform Agenda

Mukundan, who also runs Tata Chemicals, framed faster dispute resolution as one piece of a larger argument: that India can keep growing on its current settings, but cannot reach the 8 to 10 percent growth it aspires to without deeper reform. "Investment will still happen," he said. "But if you want to go to eight, nine, or 10 percent growth, we need to address these, we need to reform even more." He pointed to the overall ease and cost of doing business as the field on which India must compete, and said industry was still waiting on the conclusion of an India-U.S. trade deal that could unlock technology, capital and market access.

## A Tense Market Backdrop

The investment worry lands during a jittery stretch for Indian markets. After a strong seven-session rally driven by falling oil prices and easing Middle East tensions, the benchmark Nifty 50 and Sensex stumbled this week, dragged down by IT and metal stocks and by data showing private-sector activity cooling to a three-month low. Adding to the unease, a resurgent U.S. dollar \u2014 lifted by rising bets on a Federal Reserve rate hike \u2014 climbed to a one-year high, pressuring the rupee and Asian currencies broadly.

Foreign portfolio investors, a separate and more flighty category than direct investors, have already offloaded a record $30.6 billion of Indian stocks so far this year, though they turned net buyers briefly as oil cooled. The two flows tell a connected story: whether through the stock market or the factory floor, foreign capital has been cautious on India, and the government's challenge is to convince it to commit for the long haul.

## Why It Matters for the Diaspora

For non-resident Indians, this is more than an abstract macro debate \u2014 it is personal in a way that pure portfolio numbers are not. NRIs are among India's most natural long-term investors: they back startups, take direct stakes in family businesses, buy property and pour money into ventures back home out of both opportunity and attachment. And they are exposed to exactly the friction Mukundan is describing. Diaspora investors are among those most likely to find themselves entangled in India's slow courts \u2014 over a property dispute, an inheritance, a soured business deal \u2014 and to discover that resolution can take not months but years, sometimes decades.

So when industry pleads for faster arbitration and cleaner dispute resolution, it is arguing, in effect, for the conditions that would make the diaspora trust India with more of its capital. The FDI shortfall is a signal NRIs should read carefully: it reflects the same governance and ease-of-doing-business questions that determine whether their own money is safe and their disputes resolvable. The sensible posture is neither blind optimism nor retreat, but attention \u2014 watching whether the promised reforms to the investment treaty framework and the courts actually arrive, because those, more than any growth headline, will decide whether India becomes a place the diaspora can invest in with confidence rather than caution."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["people exercising outdoors fitness", "woman running exercise outdoor", "group fitness walking exercise"],
                          ["people exercising outdoor fitness", "woman jogging park"], None),
    articles[1]["slug"]: (["pregnant woman healthcare doctor", "pregnancy prenatal care", "pregnant woman blood pressure check"],
                          ["pregnant woman doctor checkup", "prenatal care pregnant"], None),
    articles[2]["slug"]: (["Mumbai financial district skyline", "Bombay Stock Exchange building", "India business district Mumbai"],
                          ["Mumbai skyline business district", "stock exchange building india"], None),
}
img_captions = {
    articles[0]["slug"]: "A new meta-analysis finds staying active after weight loss helps prevent the kilos from creeping back",
    articles[1]["slug"]: "A study of 8,000 mothers links poor cardiovascular health in pregnancy to higher developmental-delay risk in children",
    articles[2]["slug"]: "India's financial capital, Mumbai, where weak foreign direct investment is testing the country's growth ambitions",
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
