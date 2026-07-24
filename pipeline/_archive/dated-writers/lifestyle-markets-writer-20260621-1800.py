#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 18:00 UTC batch.
Topics:
  1. Visceral fat "metabolic memory" — a Circulation study (Ben-Gurion, CENTRAL +
     DIRECT-PLUS trials, 10-yr follow-up, 3T MRI) finds cutting hidden belly fat
     leaves lasting protection against type 2 diabetes even after weight regain
     — lifestyle-health
  2. Intermittent fasting, the gut microbiome and depression — a Chiba/Zhengzhou
     mouse study shows time-restricted eating buffered stress-induced depression,
     protected brain myelin and reshaped gut bacteria via the gut-brain axis
     — lifestyle-health
  3. RBI rejects offshore settlement (Euroclear) for its sovereign bonds, keeping
     trading on the domestic NDS-OM platform even after scrapping foreign-investor
     taxes — what it means for the rupee and diaspora investors — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621x.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621x.bin"):
            with open("/tmp/_img_dl0621x.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621x.bin")
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
# ARTICLE 1: Visceral fat "metabolic memory" (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Lose the Hidden Belly Fat and the Body Seems to Remember \u2014 Even After the Weight Comes Back, a 10-Year Study Finds",
    "subheadline": "Following dieters for a decade with high-resolution MRI scans, researchers found that cutting visceral fat \u2014 the deep fat around the organs \u2014 left a lasting shield against type 2 diabetes, even in people who regained nearly all the weight they had lost.",
    "slug": "visceral-fat-metabolic-memory-lasting-diabetes-protection-circulation-ben-gurion-central-direct-plus-diaspora-20260621-1800",
    "category": "lifestyle-health",
    "vertical": "metabolic-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians are famously prone to storing fat deep in the abdomen around their organs at low body weights \u2014 the 'thin-fat' build behind their outsized diabetes risk \u2014 so a study showing that shrinking visceral fat buys lasting protection, even after the scale creeps back, reframes what success means for diaspora families battling weight regain.",
    "sources": json.dumps([
        {"name": "Circulation \u2014 Long-term visceral adiposity dynamics and incident type 2 diabetes (CENTRAL and DIRECT-PLUS follow-up)", "url": "https://www.ahajournals.org/journal/circ"},
        {"name": "Knowridge \u2014 Why Belly Fat Is So Harmful to Your Heart Health", "url": "https://knowridge.com/2026/06/why-belly-fat-is-so-harmful-to-your-heart-health/"},
        {"name": "Ben-Gurion University of the Negev \u2014 research summary on visceral fat and metabolic memory", "url": "https://in.bgu.ac.il/en/"}
    ]),
    "body": """For most people, a diet is judged by a single number. The weight comes off, the diet worked; the weight comes back, the effort was wasted. A new long-term study suggests that the scale has been telling us only part of the story \u2014 and that the body may quietly hold on to the benefits of healthy living long after the pounds return.

## A Decade of Watching the Fat, Not the Scale

The research, published in the cardiology journal Circulation and led by scientists at Ben-Gurion University of the Negev with international collaborators, followed participants from two major dietary trials known as CENTRAL and DIRECT-PLUS. Those trials had tested a range of eating patterns \u2014 Mediterranean, low-fat, low-carbohydrate, and a plant-rich green-Mediterranean diet paired with exercise \u2014 over an initial 18 months.

What set this study apart was what came next. Through a follow-up project called FIT, the researchers kept tracking participants for five and then ten years, and they did not rely on bathroom scales. Using high-resolution 3.0-Tesla MRI scanners, they measured the body's fat with rare precision, separating visceral fat \u2014 the deep fat packed around the internal organs \u2014 from liver fat, pancreatic fat, and the softer fat under the skin.

By the time of the long-term follow-up, 366 participants had completed their assessments \u2014 and most had regained nearly all the weight they originally lost. On the scale, the interventions looked like a failure. The MRI scans said otherwise.

## The "Metabolic Memory"

The imaging revealed that abdominal fat stores remained lower than before the diets began, and crucially, the reductions in visceral fat were partially preserved even years later. Professor Iris Shai, who led the work, described the effect as a kind of metabolic memory \u2014 the body appearing to retain biological benefits from earlier fat loss even as weight crept back.

And those benefits were not abstract. Every 10 percent reduction in visceral fat achieved during the original intervention was tied to roughly a 30 percent lower risk of developing type 2 diabetes over the follow-up years. The relationship was dose-dependent: a 5 percent cut corresponded to about a 17 percent lower risk, a 15 percent cut to a 40 percent reduction, and a 20 percent cut to roughly halving the future risk of diabetes.

Strikingly, no other fat depot behaved this way. Fat in the liver, the pancreas, and under the skin did not consistently predict future diabetes risk. Visceral fat stood alone \u2014 and the protective effect held even after accounting for weight changes, physical activity, and how closely people had stuck to their diets.

## Why Visceral Fat Is the Villain

Visceral fat is not just inert padding. Wrapped around the organs, it behaves almost like an organ itself, pumping out hormones, inflammatory chemicals, and signalling molecules that ripple through the whole body. That is why it has long been linked to insulin resistance, high cholesterol, heart disease, and type 2 diabetes far more than the fat you can pinch at the waist.

The new finding adds a hopeful twist: shrinking that deep fat, even temporarily, appears to leave a durable imprint on metabolic health. The study also tied visceral-fat loss to lasting improvements in insulin resistance and in the severity of metabolic syndrome.

## The Caveats

The researchers are careful about what the data can and cannot prove. The follow-up phase was observational, so it cannot establish cause and effect outright, and participants may have differed in ways that influenced their health. The findings will need confirmation in other populations.

But the practical message is unusually encouraging. People who regain weight after a healthy stretch should not assume the effort was for nothing. The internal gains \u2014 especially around the organs \u2014 may keep paying dividends for years. And it strengthens the case that waist measurement and imaging, not the BMI number alone, may be the better gauge of long-term risk.

## Why It Matters for the Diaspora

Few groups should read this study more closely than the Indian diaspora. South Asians are well documented to store a disproportionate share of their fat viscerally \u2014 deep in the abdomen, around the organs \u2014 even at body weights that look perfectly normal. This is the heart of the 'thin-fat' phenotype that helps explain why people of Indian origin develop type 2 diabetes earlier, at lower weights, and in greater numbers than most other populations, a vulnerability that travels with them to the United States, Britain, Canada and the Gulf.

For diaspora families, weight regain after a hard-won diet is a familiar and demoralising cycle, often treated as proof that nothing works. This research reframes that despair. Even a temporary reduction in the dangerous visceral fat \u2014 through a Mediterranean-style plate, more vegetables, regular movement, and less refined carbohydrate \u2014 may bank protection against diabetes that outlasts the diet itself. The lesson is not to chase a number on the scale but to target the hidden fat that South Asian bodies are most prone to storing, and to take heart that the effort is not erased the moment the weight returns."""
})

# ============================================================
# ARTICLE 2: Intermittent fasting, gut bacteria and depression (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Fasting May Protect the Mind by Reshaping the Gut, a New Study on Stress and Depression Suggests",
    "subheadline": "When stressed mice were put on a time-restricted eating schedule, they resisted depression-like behaviour, kept healthier insulation around their brain cells, and grew a more diverse gut microbiome \u2014 pointing to the gut-brain axis as a route to mental resilience.",
    "slug": "intermittent-fasting-gut-microbiome-depression-myelin-chiba-zhengzhou-gut-brain-axis-study-diaspora-20260621-1800",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many Indian families already practise periodic fasting for religious reasons \u2014 Ekadashi, Navratri, Karva Chauth, Ramadan \u2014 so research linking time-restricted eating to a healthier gut and steadier mood gives the diaspora a fresh, science-backed lens on a habit their traditions have long encouraged, at a time when immigrant stress and mental-health stigma run high.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 A Surprising Link Between Fasting, Gut Bacteria, and Depression", "url": "https://knowridge.com/2026/06/a-surprising-link-between-fasting-gut-bacteria-and-depression/"},
        {"name": "Chiba University Center for Forensic Mental Health \u2014 study on intermittent fasting and stress resilience", "url": "https://www.chiba-u.ac.jp/e/"},
        {"name": "First Affiliated Hospital of Zhengzhou University \u2014 gut-brain axis research", "url": "https://www.fcch.com.cn/"}
    ]),
    "body": """The idea that the gut and the brain are in constant conversation has moved from the fringe of science to its mainstream. A new study adds a provocative chapter to that story: it suggests that when you eat \u2014 not just what you eat \u2014 may help shield the brain against the corrosive effects of chronic stress, and that the gut's bacteria are part of the reason.

## What the Researchers Did

Scientists from Chiba University's Center for Forensic Mental Health in Japan and the First Affiliated Hospital of Zhengzhou University in China set out to test whether intermittent fasting could protect mental health, a question far less studied than fasting's well-known effects on metabolism and inflammation.

They exposed adult male mice to repeated psychological stress, then split them into two groups. One group could eat freely at any hour. The other followed an intermittent fasting schedule, eating only within limited time windows each day.

The behavioural differences were stark. The free-eating mice showed clear signs of depression-like behaviour \u2014 less interest in pleasurable activities, lower motivation, the rodent equivalents of the listlessness that marks human depression. The fasting mice appeared far more resilient, behaving as though the stress had affected them much less.

## A Look Inside the Brain and the Gut

The team then examined brain regions tied to memory, decision-making and emotional control. In the freely fed, stressed mice, chronic stress had damaged myelin \u2014 the fatty insulation that wraps nerve fibres and lets brain signals travel cleanly. Intermittent fasting largely prevented that damage and appeared to help restore healthier myelin.

Then came the gut. The fasting mice had a more diverse community of gut bacteria and a different balance of microbial species than their free-eating counterparts. Some of those bacterial groups were associated with healthier myelin and better behaviour; others tracked with worse outcomes. The pattern fits a growing body of work on the gut-brain axis, the two-way signalling network through which the trillions of microbes in the digestive tract appear to influence mood, cognition and the brain's physical structure.

The implication is that intermittent fasting may buffer the brain against stress at least partly by reshaping the gut's microbial ecosystem \u2014 a route quite different from the way antidepressant drugs work.

## Why This Is Interesting, and Why It Is Not the Whole Story

The finding is compelling because it links three things that are usually studied in isolation: eating patterns, the microbiome, and mental health. It also dovetails with separate research showing that exercise reshapes gut-derived compounds that reach the brain, and that disrupted sleep can damage the gut's lining \u2014 all pieces of the same emerging picture in which the gut sits at the centre of whole-body and mental health.

But the caveats are large and important. This was a study in mice, not people. Rodent models of depression are useful but imperfect stand-ins for the human condition, and the leap from a controlled fasting schedule in a lab to a person's real life is considerable. Intermittent fasting is not safe or advisable for everyone \u2014 it can be risky for people with a history of eating disorders, for those who are pregnant, diabetic, underweight, or on certain medications. No one should read this as a prescription to skip meals as a treatment for depression, which remains a serious illness that deserves professional care.

What the study does is sharpen a hypothesis worth taking seriously: that the timing of food, working through the gut, may be one of the levers that influence the brain's resilience to stress.

## Why It Matters for the Diaspora

For Indian families, the science is brushing up against something deeply familiar. Fasting is woven through the cultural and religious fabric of the subcontinent \u2014 the fortnightly Ekadashi, the nine days of Navratri, Karva Chauth, the dawn-to-dusk discipline of Ramadan observed by Indian Muslims. These traditions have long framed fasting as spiritual discipline; this research hints that the same rhythm of eating and abstaining may carry quiet benefits for the gut and, through it, the mind.

That resonance matters at a particular moment. The diaspora carries its own burdens \u2014 the strain of migration, long working hours, isolation from extended family, and a persistent stigma around mental illness that keeps many from seeking help. Depression and anxiety often go unspoken in South Asian households. A study suggesting that an accessible, culturally rooted habit like time-restricted eating might support mental resilience offers a gentle, non-clinical entry point into a conversation many families find hard to start. It is not a cure, and it is not a substitute for therapy or medication where those are needed. But it may help reframe fasting, already part of diaspora life, as something the body and mind can both draw strength from \u2014 and make the larger subject of mental health a little easier to approach."""
})

# ============================================================
# ARTICLE 3: RBI rejects offshore settlement for sovereign bonds (markets-finance)
# ============================================================
articles.append({
    "headline": "India Is Courting Foreign Bond Money \u2014 but the RBI Wants It Trading at Home, Not Through Euroclear",
    "subheadline": "Even after scrapping taxes to lure overseas investors into its government bonds, India's central bank is resisting offshore settlement platforms like Euroclear, insisting foreigners trade directly on the domestic system to keep the market's liquidity in one place.",
    "slug": "rbi-rejects-offshore-settlement-euroclear-sovereign-bonds-nds-om-foreign-investors-rupee-nri-investor-20260621-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "How freely foreign money flows into India's $1-trillion-plus government bond market shapes the rupee, India's borrowing costs and the stability of the assets NRIs hold back home \u2014 so the central bank's careful, on-its-own-terms opening of the market is a quiet signal about the financial backdrop against which the diaspora invests, remits and plans for retirement in India.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's central bank not in favour of offshore settlement for sovereign bonds, sources say", "url": "https://www.reuters.com/world/india/indias-central-bank-not-favour-offshore-settlement-sovereign-bonds-sources-say-2026-06-17/"},
        {"name": "Reserve Bank of India \u2014 Fully Accessible Route for foreign investment in government securities", "url": "https://www.rbi.org.in/"},
        {"name": "Clearing Corporation of India \u2014 NDS-OM secondary market platform", "url": "https://www.ccilindia.com/"}
    ]),
    "body": """India has spent six years cautiously prising open its government bond market to the world, most recently by scrapping the taxes that had kept many foreign investors away. Now, just as the money is starting to arrive, the country's central bank is drawing a firm line on one question: where that trading should actually happen.

## The Sticking Point

According to three sources familiar with the matter, the Reserve Bank of India (RBI) is not inclined to allow foreign investors to settle Indian government securities through offshore platforms such as Euroclear \u2014 one of the world's largest securities-settlement systems and the route global debt investors are most used to. Instead, the RBI wants overseas investors to participate directly on the Negotiated Dealing System-Order Matching (NDS-OM) platform, the domestic electronic system run through the Clearing Corporation of India for secondary-market trading in government bonds.

The logic, the sources say, is about liquidity. "Let all liquidity be on NDS-OM and let foreigners participate on NDS-OM. If we allow global clearing platforms, it will fragment liquidity," one of them said. The central bank believes that concentrating buying and selling on a single domestic, order-driven venue produces better price discovery and makes it easier to trade in size, rather than splintering the market across competing offshore systems.

The RBI did not respond to a request for comment, and a Euroclear spokesperson declined to comment.

## Why It Comes Up Now

For years the obstacle was tax. India had imposed capital-gains and withholding taxes on foreign investment in its bonds, and earlier discussions about offshore settlement never gained traction because the tax made the assets unattractive in the first place. On June 5, India removed those taxes on foreign investment in government securities \u2014 and the appetite has been immediate. Since then, Indian bonds have drawn about $2 billion from overseas investors, compared with $1.6 billion in the entire first five months of the year.

That surge has revived the settlement question. "Euroclear has become a habit for foreign debt investors," said Jayesh Mehta, vice chairman and chief executive of DSP Finance, but he argued that for an order-driven market like NDS-OM, "investing directly is a better option" from a liquidity standpoint.

The market is also opening through other doors. The financial-technology firm MarketAxess last year launched an electronic trading platform that lets foreign investors trade Indian government securities directly, plugged into the Clearing Corporation's NDS-OM system, and Bloomberg is in the process of linking up too. Both keep the trading anchored to the domestic platform rather than moving it offshore.

## The Bigger Prize

Behind the technical debate sits a far larger ambition. Indian government bonds have in recent years been admitted to global benchmarks such as the J.P. Morgan Emerging Market Bond Index and the Bloomberg local-currency emerging-market index, and a Bloomberg committee was due this month to review India's entry into a wider global bond index. Inclusion in these indices forces a wave of passive foreign money into the market, lowering India's borrowing costs over time.

The RBI's stance is a calculated bet that it can capture that money on its own terms \u2014 deepening the market without surrendering control of where and how it clears. It is the same instinct visible across India's recent financial-market moves: open the door, but keep the architecture domestic.

## Why It Matters for NRIs

For the diaspora, this is not the arcane plumbing it might first appear. The government bond market is the foundation of India's financial system. How freely foreign capital flows into it shapes the rupee's strength, the interest rates Indian borrowers pay, and the stability of the broader market in which non-resident Indians hold deposits, mutual funds and property.

A steady stream of foreign bond money tends to support the rupee and hold down yields \u2014 directly relevant to anyone in the diaspora watching the exchange rate before remitting money home, or weighing fixed-income investments in India for retirement. The RBI's preference for keeping settlement domestic also reflects a wider caution about volatile, hot foreign flows that can reverse quickly, the kind that have whipsawed the rupee in stressed periods. By insisting that foreign investors trade on home turf, the central bank is trying to attract long-term capital while limiting the destabilising swings that hurt ordinary savers \u2014 including NRIs \u2014 the most.

It is, in short, a glimpse of the financial backdrop against which the diaspora plans its India bets: a market opening up, but on India's own carefully guarded terms."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["abdominal MRI scan body fat", "measuring waist tape abdomen", "healthy mediterranean vegetables food"],
                          ["measuring waist tape", "healthy vegetables mediterranean food"], None),
    articles[1]["slug"]: (["empty plate clock fasting", "gut bacteria microbiome illustration", "healthy meal bowl vegetables"],
                          ["intermittent fasting empty plate clock", "healthy meal bowl"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee currency notes", "Bombay Stock Exchange Mumbai building"],
                          ["financial trading screen bonds", "indian rupee money finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A decade-long study used high-resolution MRI to track visceral fat, the deep fat around the organs that drives diabetes risk",
    articles[1]["slug"]: "A study in mice links time-restricted eating to a more diverse gut microbiome and greater resilience against stress-induced depression",
    articles[2]["slug"]: "The Reserve Bank of India wants foreign investors to trade its government bonds on the domestic NDS-OM platform rather than via offshore systems",
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
