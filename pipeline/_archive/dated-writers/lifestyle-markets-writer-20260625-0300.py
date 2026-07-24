#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 03:00 PDT batch.
Topics (checked against last-3-day articles to avoid dupes):
  1. Loneliness — not just being alone — drives faster cognitive decline and a
     shorter life. UC Davis-led study of 175,000 adults across 18 countries,
     Journal of Personality and Social Psychology (Jun 15, 2026). — lifestyle-health
  2. Cholesterol-lowering drugs (statins & PCSK9 inhibitors) may have effects
     well beyond the heart — weight, testosterone, lung function, brain size.
     UniSA Mendelian-randomization study, British Journal of Clinical
     Pharmacology. — lifestyle-health
  3. India's market story is now powered by retail SIPs, not foreign money —
     JP Morgan: monthly SIP flows up 48% YoY to ~Rs 31,000 cr even as FPIs sold
     ~$36bn over FY25-26 and the Nifty's 2-yr return is roughly flat. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0300z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0300z.bin"):
            with open("/tmp/_img_dl0300z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0300z.bin")
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
# ARTICLE 1: Loneliness vs isolation, cognition (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It Isn't Being Alone That Ages the Mind \u2014 It's Feeling Lonely, a 175,000-Person Study Finds",
    "subheadline": "Drawing on data from 18 countries, researchers found that the perception of loneliness, far more than simply living a solitary life, predicted faster cognitive decline and a shorter life \u2014 a distinction with real consequences for how families care for ageing parents.",
    "slug": "loneliness-not-isolation-cognitive-decline-shorter-life-uc-davis-175000-18-countries-jpsp-study-diaspora-20260625-0300",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For Indian families spread across continents \u2014 children in the US or UK, parents back home \u2014 this study reframes the worry: a grandparent who lives alone but feels connected may fare far better than one surrounded by people yet quietly lonely, a nuance that should reshape how the diaspora thinks about long-distance caregiving.",
    "sources": json.dumps([
        {"name": "University of California, Davis \u2014 'Loneliness Drives Cognitive Impairment, Can Lead to Shorter Life, Study Suggests'", "url": "https://www.ucdavis.edu/news/loneliness-drives-cognitive-impairment-and-shorter-life-more-social-isolation-new-study"},
        {"name": "Journal of Personality and Social Psychology (Jun 15, 2026) \u2014 Yoneda et al., loneliness, social isolation and cognitive impairment across 18 countries", "url": "https://psycnet.apa.org/record/2026-jpsp-loneliness-cognition"}
    ]),
    "body": """There is a particular kind of ache that has nothing to do with how many people are in the room. You can sit at a crowded dinner table, surrounded by family, and still feel unseen. New research suggests that this feeling \u2014 loneliness, the perception of being disconnected \u2014 may be doing quiet, measurable damage to the ageing brain, and doing it more forcefully than the simple fact of living alone.

## A Distinction That Matters

For years, public-health messaging has tended to blur two ideas together: social isolation, which is the objective state of having little contact with others, and loneliness, which is the subjective sense of lacking the connection you want. They sound like the same problem. They are not.

"Loneliness is a perception," said Tomiko Yoneda, an assistant professor of psychology at the University of California, Davis, and the study's lead author. "You could be surrounded by a crowd of people and still feel lonely, whereas isolation is just being alone. Some people might not be lonely at all and be completely content in their solitude."

That difference is the heart of the new study, published in the Journal of Personality and Social Psychology in mid-June. Yoneda led a team of 24 researchers who pooled data from roughly 175,000 adults over the age of 50, drawn from large ageing surveys across 18 countries. Participants reported how often they felt lonely and how frequently they had contact with others, and the researchers tracked how they moved between stages of cognitive function \u2014 and toward the end of life \u2014 over time.

## What the Numbers Showed

The findings were striking in their consistency. Loneliness was reliably associated with a higher risk of cognitive impairment and a shorter life, even after the researchers accounted for social isolation. Social isolation on its own, by contrast, was not consistently tied to cognitive decline and had only a weak link to a shorter life.

The magnitudes were modest but meaningful. A ten per cent increase in how often someone reported feeling lonely was associated with an eight-to-nine per cent higher risk of slipping into severely impaired cognition, and of moving from no impairment into mild impairment. Loneliness was also linked to a three per cent lower chance of recovering from mild cognitive impairment back to normal \u2014 a hint that easing loneliness might matter not just for prevention but for recovery.

"Loneliness may be most prominent in the early stages of cognitive impairment, but it is also a risk factor after impairment develops," said Eileen K. Graham of Northwestern University, the study's supervising author. "Lonelier individuals may be more likely to progress to more severe stages and less likely to recover."

## What It Doesn't Prove

The usual cautions apply. This is observational research, built on statistical modelling of self-reported feelings, and it cannot prove that loneliness directly causes the brain to decline. Reverse causation is a genuine worry: early, undetected cognitive changes might themselves make a person feel more isolated and lonely, rather than the other way around. The researchers used advanced multistate models designed to track these transitions over time, which strengthens the case, but a model is not an experiment.

What the study does do is sharpen the target. If it is the felt quality of connection, rather than the raw count of social contacts, that tracks most closely with brain health, then interventions need to be aimed there \u2014 at meaning and belonging, not merely at attendance.

## A Practical Turn

The authors are pragmatic about what follows. They suggest hospitals and care organisations could screen for loneliness the way they screen for other risk factors, and that communities could build more genuine opportunities for older adults to feel they belong. For individuals worried about decline, the advice is refreshingly human: invest in the relationships that actually make you feel connected, not just the ones that fill the calendar.

It lands at a moment when loneliness is increasingly treated as a public-health emergency in its own right. The former US Surgeon General famously likened its mortality toll to smoking up to 15 cigarettes a day, and the World Health Organization estimates one in six people worldwide experiences loneliness. Against that backdrop, a study that separates the feeling from the circumstance offers something useful: a clearer sense of what, exactly, we should be trying to fix.

## Why It Matters for the Diaspora

Few communities live this finding as acutely as the Indian diaspora. The classic arrangement \u2014 adult children building careers in the United States, Canada, Britain or the Gulf while elderly parents remain in Pune, Kochi or Ludhiana \u2014 turns the question of an ageing parent's wellbeing into a daily anxiety conducted over video calls. This research offers an unexpected reassurance and a warning in the same breath. A parent who lives alone but is woven into a temple group, a neighbourhood, a circle of old friends may be protected in ways a worried child cannot see; a parent in a busy joint family who nonetheless feels like a burden or an afterthought may be quietly at greater risk.

The practical takeaways travel well across distance. Regular, genuine contact \u2014 the kind where a parent feels heard, not just checked on \u2014 matters more than its frequency. So does helping older relatives stay rooted in local community life rather than relying solely on family. And for the diaspora's own ageing first generation, often isolated by language, weather and distance from extended kin, the message is a prompt to build belonging deliberately, before the loneliness sets in.
"""
})

# ============================================================
# ARTICLE 2: Cholesterol drugs beyond the heart (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cholesterol Pills May Touch More Than the Heart \u2014 a Genetic Study Maps Effects on Weight, Hormones and the Brain",
    "subheadline": "Using DNA rather than years of follow-up, Australian researchers found that statins and the newer PCSK9 inhibitors carry distinct side-effect signatures \u2014 from body fat and testosterone to lung function and even brain size \u2014 a reminder that two drugs aimed at the same target are not interchangeable.",
    "slug": "cholesterol-drugs-statins-pcsk9-mendelian-randomization-weight-testosterone-lung-brain-unisa-bjcp-diaspora-20260625-0300",
    "category": "lifestyle-health",
    "vertical": "medicine",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry one of the world's highest burdens of early heart disease, and statins are a fixture in many NRI households; this study is a nudge to treat cholesterol medication as a personalised decision \u2014 worth a real conversation with a doctor \u2014 rather than a one-size-fits-all pill.",
    "sources": json.dumps([
        {"name": "UniSA / Newswise \u2014 'One pill doesn't fit all: cholesterol study reveals effects on lung function and brain size'", "url": "https://www.newswise.com/articles/one-pill-doesn-t-fit-all-cholesterol-study-reveals-effects-on-lung-function-and-brain-size?sc=rsla"},
        {"name": "Knowridge Science Report \u2014 'Cholesterol Drugs May Influence Weight, Hormones, and Even the Brain' (British Journal of Clinical Pharmacology)", "url": "https://knowridge.com/2026/06/cholesterol-drugs-may-influence-weight-hormones-and-even-the-brain/"}
    ]),
    "body": """Cholesterol-lowering drugs are among the most prescribed medicines on earth \u2014 more than 200 million people take statins alone, by one widely cited estimate. They are also among the most quietly trusted: a small daily pill, taken for decades, to keep the arteries clear. A new study suggests that trust should come with curiosity, because these drugs appear to ripple through the body in ways that reach well beyond the heart \u2014 and that not all cholesterol drugs ripple the same way.

## A Clever Workaround

The research, led by PhD student Kitty Pham at the University of South Australia and published in the British Journal of Clinical Pharmacology, did not hand anyone a pill. Instead it used a technique called Mendelian randomization, which exploits the natural genetic lottery: people are born with small DNA variations that mimic the effect of cholesterol-lowering drugs, and by comparing those people you can estimate a drug's long-term effects without running a decades-long trial.

"This normally would not be practical in a clinical trial or for such a large sample size, but genetic analyses such as the one we have conducted can really help with drug safety profiling by uncovering links with diseases and biomarkers," said chief investigator Professor Elina Hypponen, who directs the Australian Centre for Precision Health at UniSA.

Crucially, the team compared two different classes of drug that lower the same "bad" LDL cholesterol by different mechanisms. Statins, the familiar workhorses such as Lipitor and Crestor, slow the body's production of cholesterol. PCSK9 inhibitors, a newer and more powerful class, help clear cholesterol from the blood and are typically reserved for people with very high levels or those who cannot tolerate statins.

## Different Pills, Different Footprints

The findings underline why that distinction matters. For PCSK9 inhibitors, the analysis turned up a signal pointing toward a possible higher risk of certain lung problems \u2014 a finding the researchers stress is preliminary, given how new the class is and how little is known about its long-term safety. It does not prove harm; it flags something worth watching.

For statins, the picture was mixed. The genetic analysis suggested statin use may be associated with a greater tendency toward weight or body-fat gain, echoing earlier evidence that links the statin target gene to a modestly higher risk of type 2 diabetes. It also pointed to lower testosterone \u2014 a hormone that matters for energy, mood, muscle, bone and sexual health in both men and women. Yet not every signal was unwelcome: the data also hinted that statins might be associated with a larger hippocampus, the brain region central to memory and emotion that tends to shrink in dementia and depression.

"Our study reveals associations with lung function and brain size, which may influence how these drugs are prescribed or repurposed in the future," Pham said. "These findings help us understand how people may react to different drugs and assess the viability of new drug pathways."

## How to Read It \u2014 and How Not To

The single most important caveat is also the most practical: this is not a reason to stop taking a prescribed cholesterol drug. Mendelian randomization estimates lifelong, genetically-driven tendencies; it is a tool for spotting possibilities, not a verdict on any individual's treatment. Statins and PCSK9 inhibitors remain highly effective at lowering cholesterol and cutting the risk of heart attacks and strokes, and that benefit is well established.

It is worth holding this study alongside other recent work that complicates the picture in the opposite direction. A large analysis from the University of Sydney and Oxford, drawing on more than 150,000 people in randomised trials, recently concluded that statins do not actually cause most of the side effects listed on their package leaflets \u2014 memory loss, mood changes and the rest appeared just as often in people taking dummy pills. Genetic studies and randomised trials are answering slightly different questions, and the honest summary is that the science is still being written.

What the new research adds is a case for precision. Two drugs that lower the same number on a blood test are not automatically equivalent in how they touch the rest of the body. For patients, the takeaway is not alarm but engagement: notice unexpected changes in weight, mood, energy or breathing, and raise them with a doctor, because sometimes a small adjustment improves both safety and quality of life.

## Why It Matters for the Diaspora

For the Indian diaspora, this is not an abstract debate. South Asians develop heart disease earlier and at lower body weights than many other populations, and statins are a familiar presence in NRI medicine cabinets, often started in middle age and taken for life. That makes the study's central message \u2014 that cholesterol drugs are not interchangeable and may carry person-specific trade-offs \u2014 especially relevant.

It argues for a more personalised conversation: which drug, at what dose, weighed against an individual's own risks for diabetes, hormonal health or lung disease. For a community that prizes both medical caution and family health, the practical move is simple. Keep taking what your doctor prescribed, but treat the annual check-up as a genuine review rather than a renewal, and bring up any side effects you have quietly been tolerating. Precision medicine only works when the patient is part of the conversation.
"""
})

# ============================================================
# ARTICLE 3: SIP-led financialisation (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Market Engine Has Quietly Switched Drivers \u2014 From Foreign Money to the Monthly SIP",
    "subheadline": "Even as foreign investors pulled roughly $36 billion out of Indian equities and the Nifty went almost nowhere for two years, ordinary savers kept feeding the market through automated monthly plans \u2014 a shift JP Morgan calls the country's new 'demand anchor.'",
    "slug": "india-sip-led-financialisation-retail-flows-fpi-selling-jp-morgan-demand-anchor-markets-nri-investor-20260625-0300",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "NRIs weighing whether to keep money in Indian equities should understand that the market is now propped up less by the foreign flows they watch in the headlines and more by a domestic savings wave \u2014 a structural change that affects both the risks and the resilience of any India allocation.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 'SIP drives India's capital despite weak equity returns: JP Morgan'", "url": "https://www.thehindubusinessline.com/markets/sip-drives-indias-capital-despite-weak-equity-returns-jp-morgan/article71136643.ece"},
        {"name": "Devdiscourse / Axis MF report \u2014 'Equity mutual fund inflows slump 40% in May amid geopolitical uncertainty; SIP flows stay above Rs 30,000 cr'", "url": "https://www.devdiscourse.com/article/business/3939082-equity-mutual-fund-inflows-slump-40-in-may-amid-geopolitical-uncertainty-sip-flows-stay-above-rs-30000-cr-axis-mf-report"}
    ]),
    "body": """For decades, the mood of India's stock market was set abroad. When foreign institutional investors bought, the indices soared; when they sold, the rupee wobbled and the headlines turned grim. That old reflex \u2014 watch what the foreigners do \u2014 is becoming a poor guide to where Indian equities are actually heading. A quieter, more domestic force is now doing much of the lifting, and it arrives in the same modest instalment every month.

## The Two-Year Test

The case for that shift is almost paradoxical. By the usual measures, the past two years should have been miserable for Indian equities. According to a new JP Morgan report initiating coverage on India's capital-markets sector, the benchmark Nifty 50 has delivered a two-year compound annual return of just 0.8 per cent in rupee terms \u2014 and minus 3.2 per cent in dollars. Over FY25 and FY26, foreign portfolio investors sold roughly $36 billion (about Rs 3.3 trillion) worth of Indian shares.

In an earlier era, that combination \u2014 flat returns and a foreign exodus \u2014 would have gutted the market. Instead it held. The reason, JP Morgan argues, is that "India's capital-markets story remains fundamentally driven by SIP-led financialisation, despite weak equity returns."

## What an SIP Actually Is

The acronym does a lot of work in Indian finance. A Systematic Investment Plan, or SIP, is simply an automated arrangement to invest a fixed sum into a mutual fund every month \u2014 often a few thousand rupees, debited quietly from a bank account regardless of whether the market is euphoric or fearful. Multiplied across tens of millions of households, those small, steady debits have become a tide.

The numbers are now substantial. JP Morgan notes that monthly industry SIP flows rose 48 per cent year-on-year to about Rs 310 billion in May 2026, and that cumulative equity and balanced-fund net inflows reached Rs 9.43 trillion, or roughly $109 billion. SIPs, the report says, have become "the sector's demand anchor," contributing 77 per cent of total equity and balanced net inflows in FY26.

A separate report from Axis Mutual Fund put SIP contributions at Rs 30,954 crore in May \u2014 above the Rs 30,000-crore mark for the third consecutive month \u2014 even as broader equity mutual-fund inflows slumped about 40 per cent amid geopolitical jitters. In other words, the discretionary, mood-driven money cooled, but the automated money kept coming.

## The "Set-and-Forget" Generation

What makes this durable is behaviour, not just maths. JP Morgan describes the resilience of SIP inflows as evidence of a growing "set-and-forget" investment culture among retail investors \u2014 people who have decided, in effect, to keep buying through the noise. That habit has been reinforced by financialisation more broadly: as Indians shift savings out of gold and property and into financial assets, the mutual fund has become a default destination rather than an exotic one.

The bank expects the inflows to continue, helped by supportive tax and policy measures. That is the optimistic reading: a deep, structural pool of domestic capital that cushions the market against the foreign outflows that once dictated its fate.

## The Risks Beneath the Comfort

There is a less comfortable interpretation worth keeping in view. A market propped up by automatic monthly buying, largely insensitive to valuation, can keep prices elevated even when underlying returns are thin \u2014 exactly the situation of the past two years. The danger is that "set-and-forget" has only ever been tested in a rising or sideways market. A genuinely deep, prolonged downturn that shakes retail confidence could see SIPs paused en masse, removing the very support that has held things up. The anchor is strong, but it has not yet been tested in a storm.

For now, though, the structural change is real and important. The question investors ask about India can no longer be answered just by tracking what foreigners are doing this week. The more telling number is the one that lands, quietly and automatically, in mutual funds on the first of every month.

## Why It Matters for the Diaspora

For non-resident Indians, this reframes how to think about an India allocation. Many NRIs still gauge the market by foreign-flow headlines \u2014 the same flows that have been negative for two years even as the market stayed afloat. Understanding that domestic SIPs are now the dominant marginal buyer changes the risk picture in both directions: it means Indian equities are more insulated from a foreign rush for the exits than they used to be, but also that valuations may stay stretched relative to the returns on offer.

It also matters practically. NRIs can themselves invest in Indian mutual funds and SIPs, subject to the usual KYC and tax rules, and the same discipline that has steadied the domestic market \u2014 small, automated, unemotional, long-horizon investing \u2014 is exactly the behaviour that tends to serve diaspora investors well. The lesson from India's last two years is not that returns are guaranteed; it is that consistency, more than timing, has been the thing that endured.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["lonely elderly man window", "senior woman alone thinking", "older person solitude portrait"],
                          ["lonely elderly person window", "senior alone at home"], None),
    articles[1]["slug"]: (["pills medication tablets close up", "prescription medicine pills hand", "white tablets pharmacy"],
                          ["cholesterol medication pills", "prescription tablets close up"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "Mumbai financial district BSE", "National Stock Exchange India"],
                          ["Mumbai skyline financial district", "stock exchange building india"], None),
}
img_captions = {
    articles[0]["slug"]: "A 175,000-person study across 18 countries found that feeling lonely, more than living alone, tracks with faster cognitive decline",
    articles[1]["slug"]: "A genetic study finds statins and PCSK9 inhibitors carry distinct effects beyond cholesterol, from weight and hormones to lung and brain",
    articles[2]["slug"]: "Mumbai's financial district, where domestic monthly investment plans have become the dominant force in Indian equities",
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
