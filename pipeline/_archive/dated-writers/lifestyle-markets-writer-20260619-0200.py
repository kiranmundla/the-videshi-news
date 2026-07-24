#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 02:00 UTC batch.
Topics:
  1. High-dose omega-3 (DHA) supplement failed to boost memory or cognition in a 2-year randomized trial (Lancet eBioMedicine, Jun 2026) — lifestyle-health
  2. Vitamin B3 (nicotinamide riboside) supplement helped older adults with peripheral artery disease walk farther (Northwestern/UF trial, Jun 2026) — lifestyle-health
  3. Foreign capital floods India's AI data-centre boom — CPP Investments $740M into CtrlS, Jabil-Adani platform, $50B+ pipeline — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800.bin"):
            with open("/tmp/_img_dl1800.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800.bin")
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
# ARTICLE 1: High-dose omega-3 fails to boost cognition (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A High-Dose Omega-3 Pill Was Supposed to Sharpen Aging Brains. A Two-Year Trial Found It Did Nothing.",
    "subheadline": "In a rigorous randomized trial published this week in the Lancet journal eBioMedicine, two years of high-dose DHA supplements raised omega-3 levels in the blood and even the brain \u2014 yet produced no improvement in memory, cognition or the size of the brain's memory centre. For a diaspora that treats fish-oil capsules as a daily insurance policy, the finding is a pointed reality check.",
    "slug": "omega-3-dha-supplement-no-cognition-memory-benefit-lancet-ebiomedicine-trial-diaspora-20260619",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Fish-oil and omega-3 capsules are among the most popular supplements in Indian-American medicine cabinets, often taken specifically to protect aging memory; this gold-standard trial suggests that for people who are otherwise unhealthy, the pills do not deliver the brain benefit so many quietly count on.",
    "sources": json.dumps([
        {"name": "The Lancet \u2014 eBioMedicine: randomized, double-blind, placebo-controlled trial of high-dose DHA on cognition and brain structure (Yassine et al., 2026)", "url": "https://www.thelancet.com/journals/ebiom/home"},
        {"name": "CNN Health \u2014 Taking an omega-3 supplement doesn't boost memory or cognition, study finds (June 2026)", "url": "https://www.cnn.com/health"}
    ]),
    "body": """Few supplements carry as much quiet faith as fish oil. Millions of people swallow an omega-3 capsule each morning in the belief that they are doing something good for an aging brain. A rigorous new trial, published this week in the Lancet journal eBioMedicine, delivers an uncomfortable verdict: for the people who took it, the high-dose pill did essentially nothing for memory or thinking.

## What the Trial Found

The study was a randomized, double-blind, placebo-controlled clinical trial \u2014 the design scientists consider the gold standard, because neither participants nor researchers knew who was getting the real supplement. It enrolled 365 people without dementia, aged between 55 and 80. Crucially, all of them started with extremely low omega-3 levels and carried at least one risk factor for dementia, such as obesity, a sedentary lifestyle, high blood pressure or high cholesterol. Nearly half carried at least one copy of the APOE4 gene, the group thought most likely to benefit because their brains struggle to process fats efficiently.

For two full years, the treatment group took a high dose of algae-derived omega-3 \u2014 2,000 milligrams of DHA every day \u2014 while the control group took a placebo. Both groups also took a B-vitamin complex. Throughout, participants underwent MRI brain scans, blood draws and cognitive testing.

The supplement unquestionably reached its target. Omega-3 levels in red blood cells climbed from 4.9% to 11% in those taking it, and DHA levels in the cerebrospinal fluid surrounding the brain rose by an average of 17% within six months. The biology worked exactly as intended \u2014 the fat got into the brain.

And yet, on the measures that mattered, nothing changed. There were no improvements in cognition and no preservation of the hippocampus, the brain's memory centre. \"In fact, there was no real difference between people taking an omega-3 supplement and those taking a placebo,\" said lead author Dr. Hussein Yassine.

## Why the Result Matters

This is not a small or sloppy study. It directly tested the popular assumption that loading the brain with omega-3 will protect memory, and it did so in precisely the population \u2014 low omega-3, elevated dementia risk \u2014 where a benefit was most plausible. The fact that DHA demonstrably reached the brain and still failed to move cognition is what makes the finding so striking. It suggests that in people already burdened by metabolic and cardiovascular risk, simply raising omega-3 levels is not enough to turn the tide.

The researchers were careful not to write omega-3 off entirely. Yassine noted that a healthier person may obtain a greater benefit from supplementation \u2014 a hint that the pills might help those whose brains are not already under inflammatory and metabolic strain. But for the unhealthy, higher-risk group that often reaches for supplements precisely because they are worried, the trial offers little comfort.

## The Bigger Picture

The omega-3 result lands amid a run of studies puncturing supplement optimism and pointing back toward basics. A separate analysis of the long-running Diabetes Prevention Program found that diet and exercise beat the much-hyped drug metformin at preventing the accumulation of chronic disease over two decades. The recurring lesson is that no capsule substitutes for the harder, less glamorous work of moving more, eating well and managing blood pressure, weight and blood sugar.

## Why This Matters for the Diaspora

In many Indian-American households, the fish-oil bottle sits on the kitchen counter as a kind of daily insurance \u2014 a hedge against the heart disease and cognitive decline that families have watched claim elders back home. Omega-3 capsules are among the most popular supplements in the community, often taken specifically to guard memory in later years. This trial is a reminder that the hedge may be thinner than assumed, especially for those carrying the extra weight, high blood pressure or sedentary habits common in the diaspora's high cardiometabolic-risk profile.

The deeper message is not anti-supplement so much as pro-fundamentals. South Asians develop diabetes and heart disease earlier and at lower body weights than most populations, and those same conditions are what appear to blunt any benefit a pill might offer. Addressing them directly \u2014 through diet, activity and medical care \u2014 is the lever that actually moves.

## What To Actually Do

Do not rely on an omega-3 capsule as brain insurance, particularly if you carry risk factors like obesity, high blood pressure or a sedentary routine. Prioritise eating fish and whole foods over isolated supplements, since whole-diet patterns still show the strongest links to brain health. Treat the modifiable risks \u2014 weight, blood pressure, blood sugar, activity \u2014 as the real cognitive-protection strategy. And before adding or continuing any supplement, talk to a doctor about whether it is doing anything for you, rather than buying it on faith."""
})

# ============================================================
# ARTICLE 2: Vitamin B3 (nicotinamide riboside) helps PAD patients walk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Common Vitamin B3 Supplement Helped Older Adults With Clogged Leg Arteries Walk Farther, a New Trial Finds",
    "subheadline": "In a six-month double-blind trial from Northwestern and the University of Florida, older adults with peripheral artery disease who took nicotinamide riboside \u2014 a form of vitamin B3 that boosts the cellular fuel NAD \u2014 walked meaningfully farther than those on a placebo, with the biggest gains among those who took their pills faithfully. Adding red-wine compound resveratrol added nothing.",
    "slug": "nicotinamide-riboside-vitamin-b3-nad-peripheral-artery-disease-walking-trial-diaspora-20260619",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Peripheral artery disease tracks closely with the diabetes and heart disease that strike South Asians early and hard, and supervised walking therapy is often out of reach for elders living far from medical centres or with family; an affordable daily supplement that modestly improves mobility speaks directly to that gap.",
    "sources": json.dumps([
        {"name": "Northwestern University & University of Florida \u2014 randomized double-blind trial of nicotinamide riboside in peripheral artery disease (McDermott, Leeuwenburgh et al., 2026)", "url": "https://www.northwestern.edu/"},
        {"name": "Knowridge Science Report \u2014 A popular vitamin B3 supplement may help older people walk farther (June 2026)", "url": "https://knowridge.com/2026/06/a-popular-vitamin-b3-supplement-may-help-older-people-walk-farther/"}
    ]),
    "body": """For the millions of older adults whose legs ache and cramp after a short walk, a new trial offers a modest but genuine glimmer of hope \u2014 and it comes in the form of an inexpensive, widely sold supplement.

## The Condition

Peripheral artery disease, or PAD, develops when the arteries carrying blood to the legs become narrowed or blocked, usually by the slow build-up of fatty deposits over many years. Starved of oxygen and nutrients, the leg muscles struggle during activity, producing the pain, cramping, weakness and heaviness that force sufferers to stop and rest. The discomfort eases with rest but returns the moment walking resumes, and over time the cycle erodes mobility and independence. In the United States alone, more than 8.5 million people over 40 live with PAD, and the condition signals broader trouble: the same artery-clogging process raises the risk of heart attack and stroke.

The standard advice is supervised exercise \u2014 structured, professionally guided walking sessions that gradually extend how far a patient can go before pain sets in. The trouble is access. Many patients live far from medical centres offering such programmes, or face barriers of transport, cost or time. That gap has pushed researchers to look for affordable, do-it-at-home alternatives.

## What the Researchers Did

A team from Northwestern University and the University of Florida tested nicotinamide riboside, a form of vitamin B3 that has surged in popularity \u2014 US sales reached roughly 60 million dollars in 2022 \u2014 on claims it may slow aging and boost energy. The trial enrolled 90 people with PAD, most around 71 years old, and randomly assigned them to either the supplement or an identical-looking placebo. Neither participants nor researchers knew who received which, the hallmark of a rigorous double-blind design.

After six months, the difference was measurable. On average, those taking nicotinamide riboside walked about 57 feet farther than the placebo group. In a six-minute walking test, the supplement group extended their distance by roughly 23 feet, while the placebo group actually walked about 34 feet less than they had at the start. And among participants who took at least 75% of their assigned pills, the improvement was far larger \u2014 more than 100 feet.

The researchers also tested whether adding resveratrol, the much-hyped compound in red wine, would amplify the effect. It did not; nicotinamide riboside alone carried the benefit.

## The Biology

The supplement is thought to work by raising levels of NAD, a substance every cell uses to produce energy and repair damage. NAD declines naturally with age, which may reduce muscles' ability to generate energy efficiently. For people with PAD, whose leg muscles already receive too little oxygen and fuel, topping up NAD may help those muscles use what energy they have more effectively \u2014 translating into a few more feet before the pain bites.

## The Honest Caveats

This was a small, six-month study, and the gains, while real, were modest \u2014 dozens of feet, not a transformation. Professor Christiaan Leeuwenburgh of the University of Florida, a study leader, called the results promising but stressed that larger and longer trials are needed to confirm safety and lasting benefit. Dr. Mary McDermott, a PAD specialist at Northwestern, said the team also hopes to study whether the supplement could help healthy older adults preserve mobility. In other words, this is an encouraging early signal, not a green light to abandon proven care.

## Why This Matters for the Diaspora

PAD does not arrive in isolation; it travels with diabetes and cardiovascular disease, the very conditions that strike South Asians earlier and at lower body weights than most populations. As the diaspora's first large immigrant generation ages, more elders are confronting exactly the kind of mobility-limiting vascular disease this study targets. And the access problem the researchers describe is acute in many immigrant families \u2014 elders who live far from specialist centres, who lean on adult children for transport, or who hesitate to navigate an unfamiliar healthcare system. An affordable daily supplement that nudges walking distance upward, taken alongside proper medical care, fits squarely into that reality.

## What To Actually Do

Treat nicotinamide riboside as a possible complement to, never a replacement for, the proven foundations of PAD care: supervised or structured walking, and aggressive management of the underlying risks \u2014 blood sugar, blood pressure, cholesterol and smoking. Anyone with leg pain on walking should see a doctor for a proper diagnosis rather than self-treating, because PAD is also a warning sign for the heart. If considering the supplement, discuss it with a physician, keep expectations realistic, and recognise that adherence mattered \u2014 the biggest gains went to those who took it consistently. And remember that the cheapest, best-evidenced intervention remains the one with no pill at all: keep walking."""
})

# ============================================================
# ARTICLE 3: Foreign capital floods India's AI data-centre boom (markets-finance)
# ============================================================
articles.append({
    "headline": "The World's Biggest Investors Are Pouring Billions Into India's Data Centres \u2014 the Quiet Backbone of the AI Boom",
    "subheadline": "Canada's national pension fund just committed $740 million to an Indian data-centre operator, Apple supplier Jabil teamed up with Adani to build AI hardware in the country, and more than $50 billion of digital-infrastructure spending is now in the pipeline. As global capital races to build the physical plumbing of artificial intelligence, India is emerging as a favoured destination \u2014 and a fresh theme for NRI investors.",
    "slug": "india-data-centre-ai-boom-foreign-investment-cpp-ctrls-jabil-adani-nri-investor-20260619",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many NRIs work in the very technology and finance industries driving the global AI build-out, and want exposure to India's growth story beyond real estate and fixed deposits; the data-centre boom \u2014 backed by the world's largest pension funds and conglomerates \u2014 is becoming one of the most investable expressions of that story.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 CPP Investments to invest $740 million in India's CtrlS Datacenters (June 2026)", "url": "https://www.reuters.com/business/"},
        {"name": "Reuters \u2014 Apple supplier Jabil, Adani partner to build AI data center infra platform in India (June 2026)", "url": "https://www.reuters.com/technology/"}
    ]),
    "body": """The artificial-intelligence revolution is usually told as a story of chatbots and chips. Its less glamorous foundation is concrete, steel and cooling systems \u2014 the data centres where AI actually runs. And right now, some of the world's largest investors are racing to build that foundation in India.

## The Money Moving In

This week, Canada Pension Plan Investment Board, one of the world's largest pension managers, said it would invest 70 billion rupees \u2014 about $740 million \u2014 in India's CtrlS Datacenters and related projects. The structure is telling: CPP Investments will put 40 billion rupees toward an 8.2% stake in CtrlS, and commit up to 30 billion rupees more to a joint venture to develop data-centre campuses across India, in which it will own 48%. The partnership, the fund said, is designed to support CtrlS's expansion and build capacity to meet surging demand from cloud companies, AI applications and India's broader digital economy.

The CtrlS deal is one piece of a much larger wave. Days earlier, Jabil \u2014 the Florida-based electronics giant that counts Apple among its customers \u2014 announced a partnership with India's Adani Enterprises to build an integrated AI and data-centre infrastructure manufacturing platform in the country. The platform aims to serve global hyperscalers, co-location facilities and enterprise data centres, addressing what the companies called \"explosive\" demand for AI-ready hardware. Jabil simultaneously raised its annual profit forecast, citing AI-led demand, and now expects roughly $13.6 billion in AI-related revenue this year.

The numbers behind the trend are large. Jabil and Adani said India's digital infrastructure will see over $50 billion in planned spending across data-centre, cloud and AI ecosystems, and Adani alone has flagged plans to spend $100 billion on renewable-powered, AI-ready data centres by 2035. India's data-centre market is projected to nearly double to $13.11 billion by 2034, according to consulting firm IMARC Group.

## Why India, Why Now

Several forces are converging. US cloud majors \u2014 Amazon, Microsoft and Alphabet's Google \u2014 are expanding hyperscale capacity in India to serve a vast, rapidly digitalising population and to position compute closer to local users. New Delhi is actively courting the investment, with Electronics and IT Minister Ashwini Vaishnaw inaugurating a Jabil facility near Pune to manufacture critical AI data-centre components, framing it as part of Prime Minister Modi's \"Make in India, Make for the World\" push. Data-sovereignty rules that favour storing Indian data on Indian soil add further pull.

The timing also dovetails with a deliberate government effort to draw foreign capital more broadly. India recently removed taxes on foreign investment in government securities and eased rules for overseas individuals to invest in Indian equities \u2014 part of a coherent strategy to deepen and diversify the country's investor base at a moment when it is keen to fund its growth.

## The Sober View

Enthusiasm should be tempered with realism. Data centres are capital-intensive and power-hungry, and India's ambitions hinge on building enough reliable, increasingly renewable electricity to feed them \u2014 no small task. The sector is also riding the broader AI investment wave, which carries the risk of over-building if demand growth disappoints. And much of the most direct exposure sits within large conglomerates and private platforms rather than pure-play listed vehicles, meaning retail investors often gain exposure indirectly, through the parent companies, their suppliers, or infrastructure and power names that stand to benefit.

## What It Means for the Diaspora

For NRIs, the data-centre boom is one of the more resonant expressions of India's growth story. Many in the diaspora work in the very technology and finance sectors driving the global AI build-out, and understand intuitively why the physical infrastructure matters. For those seeking exposure to India beyond the traditional comfort zones of real estate and fixed deposits, the theme is increasingly investable \u2014 through the listed conglomerates, component makers, power producers and infrastructure firms riding the wave, and, with India's recently eased rules, through a simpler route into Indian equities than before.

The usual discipline applies. A powerful theme is not the same as a cheap or risk-free one, and the presence of the world's largest pension funds is a vote of confidence, not a guarantee. NRIs weighing exposure should mind valuations, currency risk and the same diversification rules that govern any investment. But the signal is hard to ignore: when Canada's pension giant and an Apple supplier are both planting flags in Indian data centres in the same week, the country's place in the AI build-out has moved from aspiration to fact."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["fish oil capsules supplement", "omega 3 softgel pills", "dietary supplement capsules"],
                          ["fish oil capsules", "omega 3 supplement pills"], None),
    articles[1]["slug"]: (["older adults walking outdoors", "senior person walking exercise", "elderly walking park"],
                          ["senior couple walking", "older people walking outdoors"], None),
    articles[2]["slug"]: (["data center servers", "server room data centre", "data center interior racks"],
                          ["data center servers", "server room technology"], None),
}
img_captions = {
    articles[0]["slug"]: "Omega-3 fish-oil capsules; a two-year randomized trial found high-dose DHA failed to improve memory or cognition in at-risk older adults",
    articles[1]["slug"]: "Older adults walking; a vitamin B3 supplement that boosts cellular NAD modestly improved walking distance in people with peripheral artery disease",
    articles[2]["slug"]: "Inside a data centre; global investors are pouring billions into India's data-centre capacity to power the AI boom",
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
