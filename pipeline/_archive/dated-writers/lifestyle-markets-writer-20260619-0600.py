#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 06:00 UTC batch.
Topics:
  1. Legumes/lentils: cheapest plant protein linked to lower blood pressure and mortality — lifestyle-health
  2. Teen sleep quality tied to mental health, BMI and screen time (PLOS One, 5,713 adolescents) — lifestyle-health
  3. India's banks rush into dollar bonds under new RBI subsidised hedging window — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0600.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0600.bin"):
            with open("/tmp/_img_dl0600.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0600.bin")
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
# ARTICLE 1: Legumes — cheapest plant protein, lower BP & mortality (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Cheapest Protein in the Indian Kitchen May Be the Most Protective. New Research Keeps Pointing to the Humble Dal.",
    "subheadline": "A run of nutrition research keeps landing on the same unglamorous conclusion: legumes \u2014 the lentils, chickpeas and beans at the heart of Indian cooking \u2014 lower blood pressure, protect the heart and, in one landmark study of older adults, were the single most protective food group for survival. For a diaspora drifting toward Western convenience food, it is a reminder that the answer was on the thali all along.",
    "slug": "legumes-lentils-dal-blood-pressure-mortality-cardiometabolic-cheapest-plant-protein-diaspora-20260619",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Lentils, chickpeas and beans are the protein backbone of Indian vegetarian cooking, yet many diaspora families quietly eat less dal as schedules tighten and Western convenience food creeps in; the science says the cheapest item in their pantry is also one of the most protective against the heart disease and diabetes that strike South Asians early.",
    "sources": json.dumps([
        {"name": "Men's Journal \u2014 Eating This Cheap Plant Protein Daily Can Lower Blood Pressure (June 2026)", "url": "https://www.mensjournal.com/food/cheap-plant-protein-legumes-benefits"},
        {"name": "Food Habits in Later Life \u2014 landmark seven-year survival study of 785 adults aged 70+ across Japan, Sweden, Greece and Australia", "url": "https://pmc.ncbi.nlm.nih.gov/"}
    ]),
    "body": """In a world chasing the next expensive supplement, one of the best-evidenced foods for a long, healthy life costs a few rupees a serving and has sat at the centre of Indian cooking for thousands of years. It is the legume \u2014 the lentil, chickpea and bean family that becomes dal, chana, rajma and sambar. A steady stream of nutrition research keeps circling back to it.

## The Survival Signal

The most striking evidence comes from a landmark study, Food Habits in Later Life, in which researchers tracked 785 adults aged 70 and older across Japan, Sweden, Greece and Australia for up to seven years, recording what they ate and who survived. Out of every food group analysed, legumes emerged as the single most protective dietary predictor of survival. The numbers were precise: for every additional 20 grams of legumes eaten per day \u2014 a couple of spoonfuls of dal \u2014 the risk of death over the study period fell by roughly seven to eight percent.

That is a remarkable return on a food most Western diets ignore. Legumes appear repeatedly in studies of the world's longest-lived populations, from the Mediterranean to Okinawa, and the reason is not mysterious once you look at what they contain.

## Why They Work

"Legumes provide protein, fiber, B vitamins, minerals such as magnesium and potassium, polyphenols, and other bioactive compounds, while also being naturally low in saturated fat and generally low on the glycemic index," says registered dietitian Jennifer Pallian. That combination acts on several of the body's most important health levers at once.

The blood-pressure benefit is among the best documented. Potassium and magnesium help relax blood vessels and counter the effects of sodium, while the high fibre content steadies blood sugar and blunts the post-meal spikes that, over years, damage arteries. "Consumption of legumes has been linked with a lower risk of cardiovascular disease, as well as favorable effects on risk factors such as high blood pressure, dyslipidemia, obesity, and type 2 diabetes-related markers," Pallian notes. Legumes also contain plant sterols and stanols, natural compounds that block some cholesterol absorption in the gut and help lower LDL, the harmful kind.

The nutrient density is easy to underestimate. A single cup of cooked lentils delivers about 18 grams of protein and 15.6 grams of fibre \u2014 well over half a day's recommended fibre \u2014 for a modest 230 calories, plus more than a third of the daily requirement for iron. Few foods pack that much nutrition into so little money.

## The Quiet Drift Away

Here is the uncomfortable part for many diaspora households. The legume tradition is strongest in exactly the cuisines that built around it \u2014 Indian, Middle Eastern, Latin American, Mediterranean \u2014 and weakest in the standard American diet that immigrant families gradually absorb. As work intensifies, commutes lengthen and children gravitate to Western convenience food, the daily pot of dal that anchored the home kitchen back in India can quietly become a weekend ritual rather than an everyday staple.

That drift matters more for South Asians than for almost anyone else. The community develops type 2 diabetes and heart disease earlier, and at lower body weights, than most populations. The very foods being edged out \u2014 lentils, chickpeas, beans \u2014 are precisely those that protect against the conditions the diaspora is most prone to. The dal was never the boring part of the meal to be replaced; it was the medicine hiding in plain sight.

## What To Actually Do

You do not need to overhaul your kitchen. The simplest move is to bring legumes back to daily, not occasional, status \u2014 a bowl of dal with dinner, chana in a salad, rajma or chole midweek, a handful of roasted chickpeas instead of chips. Aim for at least one legume-based serving a day; the survival data suggested benefits from amounts as small as a couple of spoonfuls scaled up.

Variety helps, because different legumes bring slightly different nutrient profiles \u2014 lentils for iron and protein, chickpeas for fibre, soy and tofu for complete protein. Keep an eye on how they are prepared: the benefits come from the legume, not from drowning it in cream, ghee or salt. And for families managing blood pressure, cholesterol or blood sugar, this is one dietary change with deep evidence behind it and almost no downside. The cheapest thing in the pantry may also be the most valuable."""
})

# ============================================================
# ARTICLE 2: Teen sleep quality tied to mental health, BMI, screen time (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Study of 5,700 Teenagers Found What Wrecks Their Sleep \u2014 and Girls Are Paying the Steeper Price",
    "subheadline": "In a survey of 5,713 adolescents published in PLOS One, a third had poor sleep quality, and the biggest culprits were a familiar trio: mental health, body weight and screen time. Girls fared markedly worse than boys. For diaspora parents fighting the nightly battle over phones, the findings put hard numbers on an instinct they already had.",
    "slug": "teen-sleep-quality-mental-health-bmi-screen-time-plos-one-5713-adolescents-girls-diaspora-parents-20260619",
    "category": "lifestyle-health",
    "vertical": "family-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Diaspora parents wage a near-universal nightly struggle over screens and sleep with teenagers caught between academic pressure and phones; this large study names the three levers \u2014 screen time, weight and mental health \u2014 that actually move adolescent sleep, and flags that daughters may be carrying a heavier burden.",
    "sources": json.dumps([
        {"name": "PLOS One \u2014 Gender and residential differences in sleep quality among Chinese adolescents aged 13\u201318 years (Kang et al., June 2026)", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0349681"},
        {"name": "News-Medical \u2014 Teen sleep quality associated with mental health, BMI, and screen time (June 2026)", "url": "https://www.news-medical.net/news/20260618/Teen-sleep-quality-associated-with-mental-health-BMI-and-screen-time.aspx"}
    ]),
    "body": """Any parent of a teenager knows the nightly skirmish: the phone that will not go down, the light still glowing under the door past midnight, the groggy, irritable child at breakfast. A large new study puts hard numbers on what is actually driving poor adolescent sleep \u2014 and the answers are both reassuring and pointed, because they are largely things families can influence.

## What the Study Found

Researchers led by Jianying Li of Shanxi University surveyed 5,713 adolescents aged 13 to 18 across six cities, measuring their sleep with the widely used Pittsburgh Sleep Quality Index alongside data on body weight, physical fitness, sedentary time, screen time and mental health. The headline figure is sobering: 33.71 percent of the teenagers \u2014 one in three \u2014 had poor sleep quality.

When the researchers untangled what predicted bad sleep, three factors stood out. Higher body mass index, more sedentary time and more screen time were each associated with significantly greater odds of poor sleep. Running in the other direction, mental health emerged as the single strongest protective factor: teenagers with higher mental health scores had a lower risk of poor sleep across every measure the study tracked. The relationship almost certainly runs both ways \u2014 poor sleep worsens mood, and a troubled mood wrecks sleep \u2014 but the size of the effect underlines how tightly the two are bound.

## Daughters Are Faring Worse

One of the study's sharpest findings concerns gender. Female adolescents scored worse than males across nearly every sleep measure. Some 38.4 percent of girls were classified as having poor sleep quality, compared with 29.2 percent of boys \u2014 a gap too large to dismiss. The researchers also found that the damage done by higher body weight fell more heavily on girls' sleep than on boys'.

The study, published in the journal PLOS One, also found that teenagers in more rural areas slept worse than their urban peers, struggling more with how long it took to fall asleep, how long they slept and how often their sleep was disturbed.

## The Caveats

This was a cross-sectional study \u2014 a single snapshot in time \u2014 which means it can show that these factors travel together but cannot prove that one causes another. The sleep and behaviour data were also self-reported, which can introduce bias, and the survey did not capture the finer timing of when screens were used or when teenagers went to bed. The research was conducted in China, so the precise percentages may not map exactly onto a diaspora teenager in New Jersey or London. But the underlying relationships \u2014 screens, weight, mood and sleep \u2014 are consistent with a deep body of evidence from around the world.

## Why This Matters for the Diaspora

The nightly screen battle is close to universal in immigrant households, where teenagers are often squeezed between intense academic expectations and the pull of phones and social media. Many diaspora parents carry an instinct that the devices are stealing their children's sleep; this study hands them the numbers behind the hunch, and adds a layer they may not have weighed \u2014 that a daughter could be quietly bearing a heavier burden than a son.

It also reframes the problem usefully. Sleep is not a standalone issue to be fixed with an earlier bedtime alone. It sits at the centre of a web that includes physical activity, weight and \u2014 crucially \u2014 mental wellbeing, a subject still freighted with stigma in many South Asian families. Protecting a teenager's sleep may mean protecting their mental health, and vice versa.

## What To Actually Do

The practical levers map directly onto the findings. Rein in screen time, especially in the hour before bed, and keep phones out of the bedroom overnight rather than relying on willpower. Build in daily physical activity to cut sedentary time, which helps both sleep and weight. Treat a teenager's mood as part of the sleep equation, not separate from it \u2014 persistent low mood, anxiety or withdrawal deserves attention, and asking for help is a strength, not a failure. And keep a particularly watchful, supportive eye on daughters, who this research suggests may be struggling more than they let on. None of these require money or gadgets; they require attention, and the payoff is a better-rested, steadier teenager."""
})

# ============================================================
# ARTICLE 3: India's banks rush into dollar bonds under new RBI subsidy (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Banks Are Rushing to Borrow Dollars Abroad \u2014 and the RBI Just Made It Cheaper to Do So",
    "subheadline": "HDFC Bank, State Bank of India and Bank of Baroda are all tapping the overseas dollar-bond market this month, the first to use a new Reserve Bank facility that subsidises the cost of hedging foreign borrowing. Bankers expect $15\u201320 billion to flow in over the next six months \u2014 a deliberate effort to defend the rupee and pull in foreign capital.",
    "slug": "india-banks-dollar-bonds-rbi-subsidised-hedging-window-hdfc-sbi-bank-of-baroda-rupee-nri-investor-20260619",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "NRIs hold a direct stake in the rupee's stability \u2014 through remittances, NRE/FCNR deposits and Indian bank shares \u2014 and this coordinated push to draw dollars into the banking system is one of the clearest signs of how hard New Delhi is working to steady the currency and fund the economy's growth.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's HDFC Bank to hit dollar bond market under new subsidised scheme, sources say (June 2026)", "url": "https://www.reuters.com/business/"},
        {"name": "Reuters \u2014 Top Indian state lenders eye first dollar bonds since RBI subsidy, sources say (June 2026)", "url": "https://www.reuters.com/business/finance/"}
    ]),
    "body": """India's biggest banks are heading overseas to raise dollars, and they are doing it through a brand-new door the central bank has just opened for them. The flurry of activity is a window into how India is fighting to steady its currency and keep foreign money flowing in \u2014 a story that touches every NRI with a stake in the rupee.

## What Is Happening

This week, HDFC Bank \u2014 India's largest private lender \u2014 said it was looking to raise at least $500 million through five-year dollar bonds. It follows reports that the state-run giants State Bank of India and Bank of Baroda are each planning to raise around $500 million the same way, targeting roughly $1 billion between them. All three are racing to be among the first to use a new Reserve Bank of India facility designed to make overseas borrowing cheaper.

HDFC Bank's deal carried initial pricing guidance of about 120 basis points over the comparable US Treasury yield, though bankers expected strong demand to pull the final cost below 100 basis points. The proceeds, according to people familiar with the terms, will fund the bank's overseas branches and subsidiaries and support its general business.

## The Clever Mechanism

The reason all of this is happening now is a policy tweak with outsized consequences. Earlier this month, the RBI said that external commercial borrowings with an average maturity of at least three years \u2014 raised by state-run companies and banks \u2014 would qualify for a currency swap facility at a fixed rate of 1.5 percent per year. In plain terms, the central bank is subsidising the cost of hedging, the insurance banks buy to protect themselves against the rupee weakening before they have to repay dollars.

Hedging is normally expensive, and that cost often makes overseas borrowing less attractive than it looks. By capping it at 1.5 percent, the RBI sharply lowers the all-in cost. One banker estimated the landed cost for these lenders at around 6.25 to 6.5 percent \u2014 cheaper than borrowing the equivalent at home in rupees. That gap is the whole point: it nudges banks to bring dollars into the country. Merchant bankers expect inflows of roughly $15 billion to $20 billion through this route over the next six months.

## Why India Is Doing This

The scheme is one piece of a deliberate, coordinated campaign. India has weathered a brutal year for capital flows, with foreign portfolio investors selling a record $30.8 billion of Indian equities in 2026 before only recently turning net buyers again. The rupee has been under pressure, and a steady supply of incoming dollars helps cushion it.

So New Delhi and the RBI have been pulling several levers at once. Alongside the hedging subsidy, the government has scrapped taxes on foreign investment in government bonds, eased rules for overseas individuals to buy Indian stocks, and lifted interest-rate caps on NRI deposits. Finance Minister Nirmala Sitharaman has acknowledged the country faces uncertainty over foreign exchange, oil and a possible monsoon shortfall, while pointing to these measures as a way to draw capital in. The dollar-bond push fits squarely into that strategy: get dollars into the banking system, ease pressure on the currency, and fund the economy's growth more cheaply.

## The Sober View

None of this is free of risk. Borrowing in dollars to lend or invest in rupees carries currency exposure, which is exactly why the hedging subsidy exists \u2014 and a subsidy is a cost the central bank ultimately bears. The strategy also leans on foreign appetite for Indian bank paper holding up; strong demand is expected, but global conditions can shift quickly, as this year's equity outflows showed. And cheaper overseas funding is a tailwind for bank margins, not a guarantee of it.

## What It Means for the Diaspora

For NRIs, the rupee is not an abstraction. It determines how far remittances stretch when sent home, what NRE and FCNR deposits are really worth, and how the Indian bank shares many hold in their portfolios perform. A coordinated effort to pull dollars into the banking system and steady the currency is, on balance, supportive of all three.

It is also a useful signal of intent. When India's largest private bank and its biggest state lenders all move to tap overseas markets in the same month, under a facility built expressly to make it cheaper, it tells you how seriously New Delhi is working to keep capital flowing and the rupee on a steadier footing. For diaspora investors weighing exposure to Indian banks or bonds, the policy backdrop has rarely been more deliberately accommodating \u2014 though, as always, currency risk and valuations deserve a clear-eyed look before acting."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["lentils dal bowl", "assorted legumes beans lentils", "cooked lentils food"],
                          ["lentils bowl", "assorted legumes beans"], None),
    articles[1]["slug"]: (["teenager using smartphone in bed", "teenager sleeping bed", "adolescent phone night"],
                          ["teenager phone bed night", "tired teenager smartphone"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee banknotes currency", "Mumbai financial district bank"],
                          ["indian currency rupee", "bank building finance"], None),
}
img_captions = {
    articles[0]["slug"]: "Lentils and legumes; research repeatedly links the cheap pantry staple to lower blood pressure and longer survival",
    articles[1]["slug"]: "A teenager on a phone at night; a study of 5,713 adolescents tied poor sleep to screen time, body weight and mental health",
    articles[2]["slug"]: "Indian rupee currency; India's banks are raising dollars overseas under a new RBI subsidised hedging window",
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
