#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 02:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Adelaide University 18-month trial (200+ adults with obesity): intermittent
     fasting matched calorie-counting on weight loss but was psychologically
     easier — dieters didn't feel they had to consciously restrict; ~15% of the
     weight loss was explained by that improved sense of control. — lifestyle-health
  2. Oxford-led RCT (88 UK adults, treatment-resistant depression): a 6-week
     ketogenic diet improved depression scores slightly more than a phytochemical
     control diet (~10-point vs ~8-point PHQ-9 drop). — lifestyle-health
  3. June 24 rally: Sensex +790 (76,991), Nifty reclaims 24,000, banking + IT
     lead as Brent crude crashes to 4-month lows post-Hormuz and RBI eases
     rate-hike fears + lets banks lend to NRIs against FX deposits; rupee
     firms to 94.65. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0200z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0200z.bin"):
            with open("/tmp/_img_dl0200z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0200z.bin")
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
# ARTICLE 1: Intermittent fasting vs calorie counting (lifestyle-health)
# ============================================================
articles.append({
    "headline": "For Yo-Yo Dieters, the Trick May Be When You Eat, Not How Much You Count",
    "subheadline": "An 18-month Australian trial found intermittent fasting matched old-fashioned calorie counting for weight loss \u2014 but felt far easier, because dieters never had to police every mouthful. About a sixth of their success came down to that lighter mental load alone.",
    "slug": "intermittent-fasting-vs-calorie-counting-yo-yo-dieters-adelaide-18-month-trial-psychological-control-diaspora-20260625-0200",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "In Indian and South Asian homes food is love, hospitality and ritual \u2014 the calorie-counting diet, with its weighing of every roti and ladoo, collides head-on with that culture, which is exactly why a fasting approach the community already knows from vrat and Ekadashi may prove far easier to live with.",
    "sources": json.dumps([
        {"name": "Knowridge / Adelaide University \u2014 'Can\u2019t stick to a diet? Try intermittent fasting for weight loss'", "url": "https://knowridge.com/2026/06/cant-stick-to-a-diet-try-intermittent-fasting-for-weight-loss/"},
        {"name": "University of Adelaide / SAHMRI \u2014 Prof. Leonie Heilbronn, 18-month intermittent fasting vs calorie-restriction trial", "url": "https://www.adelaide.edu.au/newsroom/"}
    ]),
    "body": """Anyone who has tried to lose weight knows the quiet exhaustion of it: the mental arithmetic before every meal, the guilt after a second helping, the running tally that never switches off. A new study from Australia suggests that for the people who struggle most \u2014 the chronic yo-yo dieters \u2014 the answer may not be a better calorie count, but escaping the counting altogether.

## Two Roads to the Same Weight

Researchers at the University of Adelaide and the South Australian Health and Medical Research Institute set out to compare two of the most common ways people try to slim down. They recruited more than 200 people living with obesity and followed them for 18 months \u2014 an unusually long window for a diet study, long enough to see not just whether weight came off but whether it stayed off.

Participants were split into three groups. One followed an intermittent fasting plan: on three non-consecutive days each week, they ate just 30 percent of their energy needs in a single morning window between 8am and noon, then fasted for the next 20 hours; on the other four days, they ate normally. A second group did conventional calorie restriction, eating about 70 percent of their usual intake every day. A third group received standard care and general healthy-eating advice.

When the results came in, both active diets produced similar amounts of weight loss. On the scale, in other words, fasting and calorie-cutting finished in a dead heat.

## The Difference Was in the Head, Not the Hips

What set them apart was not the kilograms but the experience of getting there. The study was designed to look specifically at the psychology of dieting \u2014 how each approach affected eating behaviour, mood, sleep and overall quality of life. And here the two diverged sharply.

People in the calorie-restriction group described the familiar grind: they had to consciously think about holding back, monitoring portions and resisting the urge to overeat, day after day. The fasting group reported something different. Because their restriction was confined to a few defined windows, they did not feel they had to overhaul their everyday relationship with food or stay on guard at every meal.

The researchers were able to put a number on that mental relief. The improved sense of control reported by the fasting group accounted for roughly 15 percent of their weight loss \u2014 a measurable chunk of success traceable not to a clever metabolic trick but simply to the diet feeling more livable.

"While many diets can result in weight loss, they may be difficult to stick to and this makes keeping that weight off long-term more challenging," said Professor Leonie Heilbronn, who led the work. "The results of our study indicate intermittent fasting could offer an alternative pathway for people who find conventional dieting challenging."

## Why Sustainability Beats Severity

The finding lands on one of the oldest truths in weight management: the best diet is the one you can actually keep doing. Most diets work in the short term and most fail in the long term, not because the science is wrong but because the daily discipline becomes unbearable. By concentrating the hard part into a few hours on a few days, intermittent fasting may sidestep the slow erosion of willpower that sinks so many calorie-counting attempts.

It is worth being clear about the limits. This was a structured trial with a specific, fairly demanding fasting protocol \u2014 a 20-hour fast is not trivial, and intermittent fasting is not advisable for everyone, particularly people with diabetes on certain medications, those with a history of eating disorders, pregnant women, or anyone underweight. Both diets demanded real commitment, and neither is magic. What the study offers is not a verdict that fasting is superior, but evidence that for people who have repeatedly bounced off conventional diets, a different structure might finally stick.

## Why It Matters for the Diaspora

For Indian and South Asian families, this research speaks to a particular tension. Food is woven into love, faith and welcome \u2014 the guest who refuses a third helping, the festival table groaning with sweets, the grandmother who measures affection in ghee. Against that backdrop, the calorie-counting diet can feel almost antisocial, an endless act of refusal at the very table where the family gathers. It is no wonder so many give up.

Intermittent fasting may sit more comfortably with both the culture and the wiring. The community already carries an outsized burden of obesity-linked diabetes and heart disease, often appearing at lower body weights than in other populations, which makes sustainable weight control genuinely urgent. And fasting itself is not foreign \u2014 it is built into the calendar, from Ekadashi and Navratri vrat to the disciplined fasts observed across faiths. A method that lets you eat freely with family on most days, and concentrate the restraint into a few, may map onto diaspora life far better than a regime that asks you to weigh every roti. For those who have lost and regained the same ten kilos more times than they can count, the most useful takeaway may be permission to stop counting \u2014 and to try changing when they eat instead."""
})

# ============================================================
# ARTICLE 2: Keto diet & treatment-resistant depression (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Strict Low-Carb Diet Eased Hard-to-Treat Depression in a New Trial \u2014 but Doctors Urge Caution",
    "subheadline": "In a UK study of people whose depression had resisted standard treatment, six weeks on a ketogenic diet brought a slightly bigger drop in symptoms than a healthy comparison diet \u2014 a tantalising hint that what we eat may reach the brain, not just the body.",
    "slug": "ketogenic-diet-treatment-resistant-depression-oxford-uk-randomized-trial-phq9-mental-health-diaspora-20260625-0200",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Depression remains heavily stigmatised in many Indian and South Asian families, where it is often hidden or dismissed rather than treated \u2014 so any evidence that a dietary change, framed as wellness rather than illness, can ease symptoms may reach people who would never walk into a psychiatrist\u2019s office.",
    "sources": json.dumps([
        {"name": "Medical News Today \u2014 'Depression, diabetes: How keto may help, per the latest evidence'", "url": "https://www.medicalnewstoday.com/articles/depression-diabetes-how-keto-may-help"},
        {"name": "Min Gao et al., University of Oxford \u2014 randomized trial of ketogenic vs phytochemical diet in treatment-resistant depression (88 UK adults)", "url": "https://www.ox.ac.uk/news"}
    ]),
    "body": """For most of the history of psychiatry, the brain and the dinner plate have been treated as separate worlds. A new clinical trial from the United Kingdom adds to a small but growing body of evidence that they may be more connected than we thought \u2014 and that, for some people with stubborn depression, what is on the plate might matter.

## A Trial in the Hardest Cases

The study focused on a particularly difficult group: people with treatment-resistant depression, meaning their symptoms had not lifted despite standard care. Researchers enrolled 88 adults in the UK, aged 18 to 65, all of whom scored 15 or higher on the PHQ-9, a widely used nine-item questionnaire that grades the severity of depression. A score in that range signals moderately severe to severe symptoms.

Participants were randomly assigned to one of two diets for six weeks. One group followed a ketogenic diet, restricting carbohydrates to 30 grams or less a day \u2014 the threshold that pushes the body into ketosis, a metabolic state in which it burns fat for fuel instead of sugar. The other group followed a phytochemical-rich control diet, built around plant compounds and broadly healthy eating. After six weeks, everyone returned to their usual way of eating, and the researchers checked back in at the 12-week mark.

## A Modest but Real Edge

When the follow-up data came in, both groups had improved \u2014 a reminder that paying close attention to diet, in any structured form, tends to help. But the ketogenic group did slightly better. Their depression scores fell by about 10 points on the PHQ-9, compared with roughly 8 points in the control group.

That is not a dramatic gap, but in a population whose depression had already defied treatment, even a modest additional improvement is noteworthy. It suggests the metabolic shift induced by ketosis may have effects that reach beyond weight and blood sugar, into mood itself.

Why might that be? Researchers have several working theories. Ketones, the fuel the body makes during ketosis, are an efficient energy source for the brain and may steady the way brain cells generate and use power. A very low-carbohydrate diet also tends to calm the blood-sugar spikes and crashes that can jangle mood, and may dampen the low-grade inflammation increasingly implicated in depression. None of this is settled science, but the threads are converging on the idea that metabolism and mental health are intertwined.

## The Caveats Are Important

The researchers themselves were careful not to oversell the result. "Keto should not be treated as a cure-all," cautioned Min Gao, an epidemiologist and health behaviour scientist at the University of Oxford who led the study, framing the findings as promising rather than definitive.

The cautions are substantial. The trial was small and short, and the diet itself is demanding: a true ketogenic regimen is restrictive, hard to sustain, and can bring side effects ranging from the so-called "keto flu" to changes in cholesterol. It is not appropriate for everyone, and it is emphatically not a replacement for antidepressants, therapy or medical supervision \u2014 anyone with depression should make changes in partnership with their doctor, not in place of treatment. What the study supports is not a prescription but a direction: that diet deserves to be studied seriously as one lever, among several, in mental health.

## Why It Matters for the Diaspora

In many Indian and South Asian families, depression still travels under a heavy cloud of stigma. It is frequently misread as weakness, laziness or a spiritual failing, hidden from relatives, and left untreated for years because seeking psychiatric help can feel shameful in a way that seeking help for a physical ailment does not. People will quietly endure suffering they would never tolerate from a bad knee or a racing heart.

That is precisely why research linking diet to mood can matter so much in the community. A change you make in the kitchen carries none of the stigma of a clinic visit; it can be framed, accurately, as looking after your health rather than admitting to mental illness. For a family more comfortable discussing sugar and cholesterol than sadness, that framing can be a door in. The honest message is a balanced one: this is early evidence, not a cure, and serious depression needs professional care. But the broader and more durable point is one the diaspora urgently needs to hear \u2014 that mental health is health, that the brain is an organ that responds to how the body is fed and cared for, and that there is no shame in tending to it. If a conversation about a low-carb diet is what finally gets a struggling relative talking, that alone is worth something."""
})

# ============================================================
# ARTICLE 3: June 24 market rally — oil crash + RBI (markets-finance)
# ============================================================
articles.append({
    "headline": "Indian Markets Roar Back as Oil Crashes and the Central Bank Calms Rate Fears",
    "subheadline": "A day after a brutal selloff, the Sensex jumped nearly 800 points and the Nifty reclaimed 24,000, powered by banks and IT, as Brent crude tumbled to four-month lows on signs the Strait of Hormuz was reopening and the RBI signalled no rate hike is coming.",
    "slug": "india-markets-rebound-sensex-790-nifty-24000-oil-crash-hormuz-rbi-rate-fears-rupee-nri-investor-20260625-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The same falling oil price and steadier rupee that lifted Mumbai\u2019s indices directly shape what NRIs see \u2014 the value of remittances sent home, the returns on Indian equity and bond holdings, and the cost of the fuel and imports that drive India\u2019s inflation \u2014 and a fresh RBI rule now lets banks lend to non-resident Indians against their foreign-currency deposits.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 'Sensex jumps 790 points, Nifty reclaims 24,000 as banking and IT stocks power rally'", "url": "https://www.thehindubusinessline.com/markets/stock-market-highlights-24-june-2026/article69000000.ece"},
        {"name": "Reuters \u2014 'Banks, softer oil boost Indian shares; RBI eases rate concerns'", "url": "https://www.reuters.com/markets/asia/banks-softer-oil-boost-indian-shares-rbi-eases-rate-concerns-2026-06-24/"},
        {"name": "Outlook Business \u2014 'Banking, IT Stocks Drive 791-Point Sensex Rally; Nifty Crosses 24,000'", "url": "https://www.outlookbusiness.com/markets/banking-it-stocks-drive-791-point-sensex-rally-nifty-crosses-24000"}
    ]),
    "body": """Indian stocks staged a forceful recovery on Wednesday, clawing back most of the previous day's losses as a sharp fall in global oil prices and reassuring words from the central bank revived investors' appetite for risk. It was a vivid reminder of how quickly sentiment can swing \u2014 and of how much India's market mood rides on the price of a barrel of crude.

## A Sharp Snap-Back

The BSE Sensex climbed 790.54 points, or 1.04 percent, to close at 76,991.22, edging back toward the 77,000 mark. The broader NSE Nifty 50 advanced 197.55 points, or 0.83 percent, to settle at 24,021.65, reclaiming the psychologically important 24,000 level it had slipped below just a day earlier.

The rebound came directly on the heels of a punishing session. On Tuesday, the Sensex had tumbled 893 points and the Nifty had shed 279 points, dragged down by a global rout in technology and semiconductor shares that sent South Korea's Kospi plunging at one point by as much as 10 percent. Wednesday's rally did not erase all of that damage, but it went a long way toward steadying nerves. Market breadth was healthy, with advancing stocks outnumbering decliners on the BSE.

## Oil Does the Heavy Lifting

The single biggest driver was crude. Brent futures slid to their lowest level since late February \u2014 the day before the Iran war began \u2014 on signs that oil tankers stranded in the Gulf were finally set to move out of the Strait of Hormuz, the chokepoint through which a large share of the world's seaborne oil passes. As the threat of a prolonged supply squeeze eased, prices fell, and Indian markets exhaled.

For India, the world's third-largest oil consumer and an importer of the vast majority of the crude it burns, the price of oil is not an abstraction. It feeds straight into inflation, the trade deficit and the value of the rupee. Cheaper crude lightens the import bill, cools price pressures and takes weight off the currency. "The slide in crude has powered market gains as they have brightened the outlook for both the economy and markets after a challenging spell," said Aishvarya Dadheech, founder and chief investment officer at Fident Asset Management.

## The Central Bank Steadies the Ship

The second tailwind came from the Reserve Bank of India. Governor Sanjay Malhotra told ET Now that it was "premature" to talk about interest-rate hikes, saying the central bank did not yet see signs of inflation becoming broad-based. That single word did a lot of work. Markets had been rattled by fears that a resurgent US dollar and a hawkish Federal Reserve might force India to tighten in response; Malhotra's comments pushed back on that anxiety and reassured investors that borrowing costs would stay lower for longer \u2014 a boon for corporate earnings, consumption and equity valuations.

The RBI also handed the banks a concrete gift. The central bank clarified that lenders may extend loans to non-resident Indians against their foreign-currency deposits, improving funding flexibility and, the regulator hopes, drawing more dollar inflows to support the rupee. Bank stocks responded enthusiastically. The Nifty Bank index and the private-banks gauge each jumped around 1.7 to 1.9 percent, with HDFC Bank and ICICI Bank climbing about 2.5 percent each and State Bank of India adding 1 percent.

Information technology was the day's standout sector, with the Nifty IT index surging more than 2 percent. Heavyweights including Infosys, TCS, Tech Mahindra and Coforge led the charge, with realty, financial services and cement stocks also joining the advance. Eleven of the 16 major sectors finished higher.

## The Rupee Finds Its Feet

The currency, under sustained pressure from a dollar near 13-month highs, got some respite too. The rupee strengthened by 11 paise to 94.65 against the dollar, helped by the drop in crude prices that eased the demand for dollars to pay the oil bill. It was a modest move, but a welcome change of direction for a currency that had been grinding weaker for weeks. Analysts cautioned, however, that the market remains in a phase of consolidation and that the monsoon's progress \u2014 shaping up as India's weakest in over a decade \u2014 is still a near-term worry hanging over the outlook.

## Why It Matters for the Diaspora

For non-resident Indians, a single trading day in Mumbai threads through several things they feel directly. A firmer rupee changes the arithmetic of remittances \u2014 dollars and pounds sent home buy fewer rupees when the currency strengthens, a subtle but real shift for families supporting relatives or paying for property and education in India. The same currency move alters the rupee value of NRE and FCNR deposits and of any Indian equity or bond holdings sitting in a portfolio back home.

The RBI's new allowance for banks to lend to NRIs against their foreign-currency deposits is the most tangible development, opening a fresh source of liquidity for diaspora investors who want to borrow without breaking their dollar savings. And the broader signal \u2014 lower oil, easing inflation fears, a central bank in no hurry to raise rates \u2014 paints the macro backdrop against which any decision to send money home, buy Indian stocks or lock in a deposit gets made. Wednesday's bounce is a single session, not a trend, and the volatility of the past week is its own warning. But it underscores a durable truth for the diaspora investor: India's market is unusually sensitive to the price of oil and the posture of its central bank, and both moved in its favour on Wednesday."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["clock plate intermittent fasting meal", "healthy meal plate breakfast food", "empty plate fork knife diet"],
                          ["intermittent fasting clock plate", "healthy breakfast meal plate"], None),
    articles[1]["slug"]: (["ketogenic diet low carb food avocado eggs", "healthy fats avocado nuts salmon", "low carbohydrate diet meal"],
                          ["keto diet food avocado eggs", "healthy fats avocado salmon"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "BSE Sensex trading floor India", "Mumbai financial district skyline"],
                          ["Bombay Stock Exchange Mumbai", "Mumbai skyline financial district"], None),
}
img_captions = {
    articles[0]["slug"]: "An 18-month Australian trial found intermittent fasting matched calorie counting for weight loss but felt easier to sustain",
    articles[1]["slug"]: "A UK trial tested a strict ketogenic diet against a healthy comparison diet in people with treatment-resistant depression",
    articles[2]["slug"]: "The Sensex rallied nearly 800 points on June 24 as oil prices fell and the RBI eased rate-hike fears",
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
