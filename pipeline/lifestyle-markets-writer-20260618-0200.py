#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 02:00 UTC batch.
Topics:
  1. BCAAs + exercise cut fatigue and lifted mood in older adults (UT Health San Antonio RCT) — lifestyle-health
  2. Insomnia linked to higher atrial fibrillation risk (JAHA, 1.8M Japanese adults) — lifestyle-health
  3. India's defence production hits record Rs 1.78 lakh crore; defence stocks surge — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0200.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0200.bin"):
            with open("/tmp/_img_dl0200.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0200.bin")
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
# ARTICLE 1: BCAAs + exercise for older adults (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Cheap Amino-Acid Supplement Plus Exercise Cut Older Adults' Fatigue Almost in Half, a Pilot Trial Finds",
    "subheadline": "In a controlled study of obese older adults, those who paired eight weeks of exercise with branched-chain amino acids saw fatigue fall 45 percent and depressive symptoms drop \u2014 while the placebo group's tiredness nearly doubled. The findings hint at a low-cost way to help aging bodies recover from the very exercise meant to keep them strong.",
    "slug": "bcaa-branched-chain-amino-acids-exercise-older-adults-fatigue-mood-ut-health-trial-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many diaspora families care for aging parents who eat largely vegetarian diets that can fall short on the leucine-rich protein that guards against age-related muscle loss \u2014 making an affordable amino-acid strategy especially relevant for South Asian elders at high risk of sarcopenia and frailty.",
    "sources": json.dumps([
        {"name": "Journal of Cachexia, Sarcopenia and Muscle / UT Health San Antonio \u2014 BCAA supplementation with exercise in older adults (PubMed 40860958)", "url": "https://pubmed.ncbi.nlm.nih.gov/40860958/"},
        {"name": "UT Health San Antonio \u2014 Newsroom", "url": "https://news.uthscsa.edu/"}
    ]),
    "body": """Exercise is medicine for the aging body \u2014 but for many older adults, it comes with a side effect that quietly derails the whole project: it wears them out. A new pilot trial suggests that a cheap, widely available supplement, taken alongside a workout routine, may take the edge off that exhaustion and even lift mood in the bargain.

## What the Researchers Tested

The study, led by researchers at UT Health San Antonio and published in a peer-reviewed journal, was small by design \u2014 a pilot meant to test whether a bigger trial is worth running. It enrolled 20 older adults, average age around 70, all of whom were obese, a group at high risk of losing muscle and mobility as they age.

For eight weeks, everyone followed the same supervised exercise program. The difference was what they took alongside it. Half the participants received a daily dose of branched-chain amino acids, or BCAAs \u2014 three essential amino acids (leucine, isoleucine and valine) that the body uses to build and repair muscle. The other half received a placebo. Neither the participants nor the researchers measuring outcomes knew who got which until the study ended.

## The Results

The gap between the two groups was striking. The BCAA group reported a 45 percent drop in fatigue over the eight weeks. The placebo group went the other way \u2014 their reported fatigue nearly doubled, rising about 92 percent, as the cumulative load of regular exercise took its toll on bodies that struggled to recover.

The benefits were not limited to tiredness. The amino-acid group also showed a 29 percent reduction in depressive symptoms, a meaningful change for a population in which low mood and isolation are common. And their bodies grew measurably more capable: the BCAA group posted significant improvements in handgrip strength, in the number of chair stands they could perform (a standard test of leg power and a strong predictor of independence), and in the time it took to walk 400 meters.

Taken together, the picture is of older adults who not only felt less drained but moved better and felt brighter \u2014 the opposite of the worn-down trajectory of the placebo group.

## Why It Might Work

The logic rests on a well-known problem of aging called anabolic resistance. As people get older, their muscles become less responsive to the protein they eat and to the stimulus of exercise, so they need more of the right building blocks to achieve the same repair. Leucine, the headline amino acid in BCAAs, is the one that most directly flips the switch on muscle-protein synthesis.

By topping up these specific amino acids, the researchers reasoned, older bodies may recover more completely between exercise sessions \u2014 turning a routine that would otherwise accumulate as fatigue into one that builds strength. Better recovery, in turn, may explain the lift in mood and energy.

## The Caveats

This was a pilot study of just 20 people over eight weeks, and that is its central limitation. The findings are promising but preliminary; they need to be confirmed in a larger, longer trial before anyone treats BCAAs as a proven therapy. The participants were all obese older adults, so the results may not transfer cleanly to leaner or younger people. Supplements are also not a substitute for getting protein from food, and very high amino-acid intake is not automatically better. Anyone with kidney disease or other chronic conditions should talk to a doctor before adding amino-acid supplements, since protein handling can be a real concern. The honest takeaway is that this is an encouraging signal, not a finished prescription.

## Why It Lands for the Diaspora

For Indian and South Asian families, the findings touch a tender and practical nerve: the care of aging parents. South Asian elders are at elevated risk of sarcopenia \u2014 the progressive loss of muscle mass and strength that drives falls, frailty and loss of independence \u2014 and the largely vegetarian diets common in many Indian households, while rich in many virtues, can fall short on leucine, which is most concentrated in animal proteins like dairy, eggs and meat.

That gap matters. An older relative eating a traditional vegetarian thali may be getting plenty of carbohydrate and a fair amount of protein by volume, yet still under-hitting the specific amino-acid threshold that aging muscle needs to rebuild. For these families, the study points to an affordable, accessible lever \u2014 and a reminder to pay attention not just to how much protein an elder eats, but to its quality and amino-acid profile.

## What To Actually Do

Start with food, not pills. For older vegetarians, that means prioritizing leucine-rich sources within their diet \u2014 dairy like paneer, dahi and milk, plus eggs for those who eat them, soy foods like tofu and edamame, and combinations of dal with grains. Pair that with regular resistance and walking exercise, which remains the single most powerful intervention for aging muscle. For those who exercise but feel persistently wiped out afterward, a BCAA or leucine supplement is worth discussing with a doctor as a recovery aid \u2014 it is inexpensive and, in this trial, well tolerated. And watch for the larger studies to come: if they confirm the pilot, a simple amino-acid strategy could become a standard part of keeping aging bodies strong.
"""
})

# ============================================================
# ARTICLE 2: Insomnia linked to atrial fibrillation (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Bad Sleep May Do More Than Tire You Out \u2014 A Study of 1.8 Million People Links Insomnia to an Irregular Heartbeat",
    "subheadline": "In one of the largest analyses of its kind, Japanese researchers found that people with insomnia had a 14 percent higher chance of developing atrial fibrillation, the irregular heart rhythm that raises the risk of stroke. The link was strongest in women and in adults under 65.",
    "slug": "insomnia-atrial-fibrillation-afib-risk-japan-jaha-1-8-million-study-heart-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry a well-documented double burden of disrupted sleep and early heart disease, and diaspora life adds its own insomnia triggers \u2014 late-night calls across time zones, shift work and chronic stress \u2014 making the sleep-heart connection especially worth heeding for the community.",
    "sources": json.dumps([
        {"name": "Journal of the American Heart Association (JAHA) \u2014 Insomnia and incident atrial fibrillation, May 2026", "url": "https://www.ahajournals.org/journal/jaha"},
        {"name": "American Heart Association \u2014 Newsroom", "url": "https://newsroom.heart.org/"}
    ]),
    "body": """Most people think of a bad night's sleep as a problem for the next morning \u2014 groggy, irritable, reaching for another coffee. A large new study suggests the consequences may run deeper, reaching all the way to the rhythm of the heart itself.

## What the Researchers Found

The analysis, published in May 2026 in the Journal of the American Heart Association, drew on an enormous pool of data: roughly 1.8 million people in Japan, ages 49 to 68. Researchers tracked who had insomnia and who went on to develop atrial fibrillation, or afib \u2014 a common irregular and often rapid heart rhythm that can lead to blood clots, stroke and heart failure.

After adjusting for a long list of other risk factors \u2014 things like high blood pressure, diabetes, body weight and lifestyle \u2014 people with insomnia had a 14 percent greater chance of developing atrial fibrillation than those who slept well. In a dataset this large, that is a robust and hard-to-dismiss signal.

The risk was not spread evenly. The association between insomnia and afib was strongest among women and among people younger than 65 \u2014 a reminder that the toll of poor sleep on the heart may fall hardest on groups not always thought of as classic heart-rhythm patients.

## Why Atrial Fibrillation Matters

Atrial fibrillation is the most common sustained heart-rhythm disorder, affecting an estimated 5 percent of US adults, and its prevalence climbs with age. In afib, the heart's upper chambers quiver instead of beating cleanly, which can allow blood to pool and form clots. The danger is less the irregular beat itself than its consequences: afib is a leading cause of stroke and a significant driver of heart failure and hospitalization.

Crucially, afib is often silent or intermittent in its early stages \u2014 a flutter here, a skipped beat there \u2014 which means many people carry it without knowing until a serious event forces a diagnosis. Anything that helps identify who is at higher risk, and why, is therefore valuable.

## How Sleep and the Heart Are Connected

Researchers have several working theories for why insomnia might disturb heart rhythm. Chronic poor sleep keeps the body's stress-response system switched on, raising levels of stress hormones and keeping the sympathetic "fight or flight" nervous system in overdrive \u2014 both of which can make heart tissue more electrically irritable. Insomnia also fuels inflammation and raises blood pressure over time, two well-established contributors to afib. And disrupted sleep can throw off the autonomic balance that normally keeps the heartbeat steady through the night.

In short, the heart does important housekeeping during sleep, and when sleep is fragmented night after night, that maintenance suffers.

## The Caveats

This is an observational study, and that carries an important limit: it shows a strong association, not definitive proof that insomnia causes atrial fibrillation. It is possible that other factors linked to both poor sleep and heart disease explain part of the connection, even after statistical adjustment. The study population was Japanese, so the precise numbers may not transfer exactly to other ethnic groups. And insomnia in large datasets can be measured imperfectly. None of this erases the finding \u2014 a 14 percent rise across 1.8 million people is meaningful \u2014 but it does mean the right reading is "treat your sleep as part of your heart health," not "insomnia will give you afib."

## Why It Lands for the Diaspora

For the South Asian diaspora, the study sits at the intersection of two well-documented vulnerabilities. South Asians develop heart disease earlier and at lower body weights than many other populations, and rates of disrupted sleep and insomnia in the community are high. Diaspora life layers on its own sleep saboteurs: late-night phone calls to family across India's time zones, demanding shift work in healthcare, IT and hospitality, the chronic stress of building a life far from home, and the blue-lit scroll that pushes bedtime past midnight.

The finding that risk was highest in adults under 65 is particularly relevant for a community that already faces premature cardiac risk. It reframes the late nights that many diaspora professionals treat as a badge of hard work into something with a potential physiological cost \u2014 one that compounds the community's existing heart-health challenges.

## What To Actually Do

The encouraging flip side of this research is that sleep is modifiable. Treat insomnia as a health issue worth addressing, not a personal failing to push through. The most effective first-line treatment for chronic insomnia is not a pill but cognitive behavioral therapy for insomnia (CBT-I), now available through apps and clinicians. Basic sleep hygiene still matters: a consistent sleep and wake time, a cool dark room, limiting caffeine and late screens, and protecting the hours before bed from work and stressful calls. Anyone experiencing palpitations, an irregular or racing pulse, unusual breathlessness or dizziness should see a doctor, since afib is treatable and stroke risk can be managed once it is found. And for the diaspora specifically, it may be worth rethinking the cultural normalcy of the after-midnight call \u2014 the heart, it seems, keeps score.
"""
})

# ============================================================
# ARTICLE 3: India defence production record (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Defence Production Hits a Record \u20b91.78 Lakh Crore \u2014 and the Stocks Riding the Boom Just Surged",
    "subheadline": "Government data shows India's annual defence output jumped 15.6 percent to an all-time high, with exports leaping 62 percent to nearly \u20b938,500 crore and the private sector's share at a record. The Nifty India Defence index rose 3.9 percent as investors bet the 'Make in India' arms push has real momentum.",
    "slug": "india-defence-production-record-1-78-lakh-crore-exports-stocks-surge-make-in-india-nri-investor-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "India's defence-manufacturing boom has become one of the most-watched investment themes for NRIs seeking exposure to the country's industrial rise \u2014 a story of self-reliance and export ambition that resonates with diaspora investors looking beyond IT and banks for the next structural growth story.",
    "sources": json.dumps([
        {"name": "Ministry of Defence, Government of India \u2014 Press Information Bureau release on FY26 defence production", "url": "https://pib.gov.in/"},
        {"name": "The Economic Times \u2014 Markets: Nifty India Defence index", "url": "https://economictimes.indiatimes.com/markets"},
        {"name": "Press Trust of India \u2014 India defence production and exports data", "url": "https://www.ptinews.com/"}
    ]),
    "body": """India's push to build its own weapons \u2014 rather than buy them from abroad \u2014 just produced its strongest numbers yet, and the stock market took notice. Government figures show defence production has climbed to a record high, exports have surged, and the private sector is playing a bigger role than ever. On the day the data landed, India's defence stocks jumped almost 4 percent.

## The Record Numbers

According to data from the Ministry of Defence, India's defence production reached an all-time high of roughly \u20b91.78 lakh crore in the 2026 financial year \u2014 about \u20b91.78 trillion. That marks a 15.6 percent jump over the previous year and, more strikingly, a 110 percent increase since FY21. In five years, in other words, the value of what India makes for its own and others' militaries has more than doubled.

The export figures were even more dramatic. India's defence exports rose to about \u20b938,424 crore, a 62 percent leap over the prior year. Indian-made defence equipment now reaches more than 80 countries, and the number of exporters rose to 145 in FY26, up from 128 the year before \u2014 a sign that the export base is broadening, not just deepening among a few large players.

State-owned defence firms, the Defence Public Sector Undertakings or DPSUs, posted some of the sharpest gains: their exports jumped to \u20b921,071 crore, a 151 percent rise from \u20b98,389 crore a year earlier.

## The Private Sector Steps Up

Perhaps the most structurally important number was the private sector's share. Private defence firms accounted for about \u20b942,000 crore of total production \u2014 roughly 24 percent of the total, an all-time high, up from 22 percent the year before. That shift matters because for decades Indian defence manufacturing was dominated almost entirely by sprawling state-owned enterprises and ordnance factories. A rising private share signals a more competitive, more innovative industrial base, and it is exactly what the government's policy push has been trying to engineer.

## How the Market Reacted

Investors read the data as confirmation of a structural growth story, and they bought. The Nifty India Defence index \u2014 a basket of the country's listed defence manufacturers \u2014 surged 3.9 percent on the day. The move extended a powerful multi-year run that has made defence one of the best-performing themes on Indian exchanges, transforming once-sleepy public-sector names into market darlings and lifting a cohort of private suppliers along with them.

The rally reflects a bet that the order book is durable. India's military modernization needs are vast, the government has set escalating targets for both production and exports, and global demand for cost-competitive defence equipment has risen sharply amid worldwide rearmament. Each of those forces points toward sustained revenue for the companies in the index.

## The Bigger Picture: Self-Reliance

The numbers are the financial expression of a political project. India has long been one of the world's largest arms importers, a dependence that successive governments have treated as both a strategic vulnerability and an economic missed opportunity. The "Atmanirbhar Bharat," or self-reliant India, campaign \u2014 and its defence-specific "Make in India" thrust \u2014 has used import bans on certain categories, incentives for domestic production, and a tighter embrace of private and startup defence innovation to shift the balance toward home-grown supply.

The FY26 data suggests the strategy is bearing fruit: more made at home, more sold abroad, and a wider cast of companies doing the making.

## The Caveats

For all the momentum, a clear-eyed investor should note the risks. Defence stocks have run up enormously, and valuations in parts of the sector are stretched \u2014 a lot of future growth is already priced in, which leaves little room for disappointment. The business is also heavily dependent on government orders and budget cycles, so policy shifts or fiscal pressure can hit revenues. Execution risk is real, as large defence programs are prone to delays. And the export figures, while impressive in growth terms, still start from a relatively low base. A record year is genuine good news; it is not a guarantee that the same pace continues, nor that every listed name deserves its current price.

## Why It Lands for the Diaspora

For NRIs, India's defence boom has become one of the most talked-about ways to invest in the country's industrial rise. It is a story that resonates emotionally \u2014 national self-reliance, technological pride, India making rather than merely buying \u2014 and financially, as a structural theme distinct from the IT and banking stocks that have long dominated diaspora portfolios. Many NRIs gain exposure through defence-focused mutual funds, sector index funds and exchange-traded products available via their NRE and NRO investment accounts, rather than picking individual stocks.

The prudent diaspora approach mirrors the caveats above. The theme is powerful, but it has already delivered spectacular returns, which means new money is buying in at high valuations. Treating defence as one satellite holding within a diversified India allocation \u2014 rather than chasing the momentum with concentrated bets \u2014 is the way to participate in the self-reliance story without betting the portfolio on it.

## The Bottom Line

India's defence sector just posted record production, surging exports and a rising private share \u2014 a trifecta that validates years of policy effort and sent stocks up nearly 4 percent. For NRIs watching India's transformation from arms buyer to arms maker, it is a milestone worth understanding. Just remember that the market has already noticed: the opportunity is real, and so is the price tag attached to it.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["older adults exercising gym", "senior weight training", "elderly fitness exercise"],
                          ["senior exercise fitness", "older adults workout"], None),
    articles[1]["slug"]: (["person awake in bed insomnia", "woman sleeping bed night", "bedroom sleep night"],
                          ["insomnia sleepless night", "woman awake bed night"], None),
    articles[2]["slug"]: (["DRDO Tejas aircraft", "HAL Tejas fighter jet India", "Indian Army equipment defence"],
                          ["fighter jet military", "defense manufacturing"], None),
}
img_captions = {
    articles[0]["slug"]: "Older adults exercising; a UT Health San Antonio pilot trial found branched-chain amino acids cut fatigue 45 percent when paired with exercise",
    articles[1]["slug"]: "A study of 1.8 million people linked insomnia to a 14 percent higher risk of atrial fibrillation, with the strongest effect in women and adults under 65",
    articles[2]["slug"]: "India's defence production hit a record in FY26; the Nifty India Defence index surged 3.9 percent as exports jumped 62 percent",
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
