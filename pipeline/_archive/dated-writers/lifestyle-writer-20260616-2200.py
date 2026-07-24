#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-16 22:00 UTC batch.
Topics:
  1. Social-media 'strangers' (never-met contacts) tied to loneliness (Primack et al. 2026) — lifestyle-health
  2. Protein intake & healthy aging — the vegetarian-diaspora angle (npj Aging/ELSA + SHARE 38k) — lifestyle-health
  3. Rupee rally toward 92-93 on Iran peace + oil drop + RBI measures — NRI remittance timing — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl22.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl22.bin"):
            with open("/tmp/_img_dl22.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl22.bin")
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

def source_image(slug, commons_queries, pexels_queries):
    candidates = []
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
# ARTICLE 1: Social-media strangers & loneliness (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Loneliest People Online Have the Most Followers They Have Never Met. A New US Study Names the Trap.",
    "subheadline": "Surveying a nationally representative sample of American adults, researchers found that those whose social-media contacts were mostly people they had never met in person were more than twice as likely to be lonely. The number of close real-life friends in the feed made no difference at all \u2014 a finding that cuts to the heart of how the diaspora stays connected across oceans.",
    "slug": "social-media-never-met-contacts-loneliness-primack-study-diaspora-digital-connection-20260616",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For a diaspora that lives much of its social life on screens \u2014 WhatsApp groups with relatives in India, Instagram follows of strangers back home, parasocial bonds with creators and celebrities \u2014 the study warns that filling the feed with people you have never actually met can deepen loneliness rather than cure it, while the cure is the harder, offline work of being with the people you already know.",
    "sources": json.dumps([
        {"name": "Annals of Behavioral Medicine / SAGE (Closeness of Social Media Contacts and Loneliness Among US Adults: A Nationally Representative Study)", "url": "https://journals.sagepub.com/home/abm"},
        {"name": "Nature Communications (Social isolation and loneliness, brain structure and 11 neurological/psychiatric disorders, UK Biobank, 383,421 participants)", "url": "https://www.nature.com/ncomms/"},
        {"name": "World Health Organization \u2014 Report of the WHO Commission on Social Connection", "url": "https://www.who.int/publications"}
    ]),
    "body": """The promise of social media was that no one would ever be alone again. Two decades on, a nationally representative study of American adults has put an uncomfortable number on how that promise curdled \u2014 and the culprit is not screen time, but who is on the other side of the screen.

## What the Study Measured

Researchers led by Brian Primack surveyed 1,512 US adults aged 30 to 70 and asked them two simple questions about the people they follow and friend online. What share of their social-media contacts had they never met in person? And what share did they consider close personal friends? They then measured loneliness using a validated four-item scale from the National Institutes of Health, and adjusted for age, income, education and other factors that muddy such comparisons.

The results, published in a peer-reviewed behavioural-medicine journal, were lopsided in a way the researchers did not expect.

## The Finding That Should Give Everyone Pause

People in the top quartile for contacts they had **never met in person** had more than double the odds of being lonely \u2014 an adjusted odds ratio of 2.33 \u2014 compared with those who had the fewest such contacts. The relationship was linear: the more strangers in the feed, the lonelier the person tended to be.

And the mirror-image hope \u2014 that loading your network with close personal friends would protect you \u2014 simply did not materialise. The number of close real-life friends among someone's online contacts had no significant association with loneliness at all. Filling the feed with people you actually know did not help; filling it with people you do not know hurt.

## Association, Not Destiny

The usual caveat is essential here. This is a cross-sectional study, a snapshot in time, and it cannot prove that following strangers causes loneliness. The arrow may point the other way: lonely people may reach out to strangers online precisely because their offline world feels thin. Most likely both are true, each feeding the other in a loop.

But the finding does not stand alone. It lands inside a fast-growing body of evidence that social disconnection is a genuine medical risk, not a soft one. A UK Biobank analysis of more than 383,000 people tied social isolation and loneliness to higher rates of eleven neurological and psychiatric disorders \u2014 depression, dementia, stroke and more \u2014 with inflammatory markers in the blood partly mediating the link. The World Health Organization, for its part, has stood up a full Commission on Social Connection, framing loneliness as a public-health emergency on par with smoking.

## Why This Cuts Close for the Diaspora

Few communities live as much of their social life online as the Indian diaspora. The architecture of NRI life almost demands it: the family WhatsApp group that pings at 3 a.m. India time, the cousins' weddings watched through someone's shaky phone camera, the Instagram follows of cricketers and Bollywood stars and home-town pages that keep the motherland one scroll away. For a first-generation immigrant who left a dense web of relatives behind, the phone is not a distraction from connection \u2014 it often feels like the connection itself.

The study's warning is precise. The relatives and friends you actually know, scattered though they are, are not the problem. It is the accumulating layer of people you have never met \u2014 the influencers, the strangers in the comments, the parasocial attachments to creators who do not know you exist \u2014 that correlates with the empty feeling after an hour of scrolling. The feed can be 90 per cent strangers and still feel busy. The study suggests that busyness is part of the trap.

## The Second-Generation Wrinkle

There is a generational fault line here too. The children of immigrants \u2014 raised on these platforms, often the family's bridge to a wider American social world \u2014 may be most exposed to the never-met-in-person dynamic, given how much of Gen Z friendship begins and lives online. Parents who fret that their teenager has hundreds of online friends but few who come to the house may, this research suggests, be worrying about the right thing.

## What To Actually Do

The practical takeaway is neither a digital detox nor a guilt trip. It is a recalibration of where effort goes. Converting online ties into offline ones \u2014 turning the WhatsApp cousin into a phone call, the local-community Facebook group into a temple visit or a potluck, the follower into a coffee \u2014 is the move the evidence supports. So is pruning, gently, the share of the feed given over to strangers whose lives generate envy or comparison without warmth.

For older NRI parents, often the loneliest cohort of all, the lesson is to resist the temptation to let the screen substitute for the sabha. A video call with grandchildren beats a passive scroll; a real gathering beats both. And for the diaspora's many tech workers, who built these platforms and live on them, the finding is a quiet rebuke to the founding myth of their own industry. Connection, it turns out, was never about the size of the network. It was about whether you had actually met the people in it."""
})

# ============================================================
# ARTICLE 2: Protein & healthy aging for the vegetarian diaspora (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Diaspora Worries About Cholesterol and Sugar. A Wave of New Studies Says the Quieter Danger Is Too Little Protein.",
    "subheadline": "Two large aging studies \u2014 one tracking 532 older Britons, another nearly 38,000 adults across 27 countries \u2014 found that people eating too little protein lost strength, mobility and independence faster, and died sooner. For a largely vegetarian diaspora that often eats well below the protein it needs, the message reframes the dal-and-rice plate.",
    "slug": "protein-intake-healthy-aging-vegetarian-diaspora-elsa-share-studies-muscle-frailty-20260616",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A large share of the Indian diaspora is vegetarian or near-vegetarian and tends to under-eat protein while over-eating refined carbohydrates \u2014 exactly the pattern these studies link to faster muscle loss, frailty and earlier death, making protein adequacy, not just sugar or fat, an urgent and under-discussed priority for NRIs and their ageing parents.",
    "sources": json.dumps([
        {"name": "npj Aging (Protein intake and its interaction with dietary patterns on clinical outcomes among older adults, English Longitudinal Study of Ageing)", "url": "https://www.nature.com/npjamd/"},
        {"name": "Nutrients / SHARE (Low Protein Intake Is Associated with the Risk of Functional Impairment in Older Adults, 38,073 adults across 27 countries)", "url": "https://www.mdpi.com/journal/nutrients"},
        {"name": "American Journal of Clinical Nutrition / Tufts University (whey protein supplementation and muscle in older adults)", "url": "https://ajcn.nutrition.org/"}
    ]),
    "body": """Walk into any Indian household and the dietary anxieties are predictable: the ghee, the sugar in the chai, the white rice, the family history of diabetes. Protein rarely makes the list. A clutch of new aging studies suggests that omission is itself a health risk \u2014 and one the diaspora is unusually prone to.

## The English Evidence

Researchers using the English Longitudinal Study of Ageing followed 532 adults aged 65 and over for six years, tracking what they ate against how their bodies held up. The pattern was consistent and stark. Older people eating high amounts of protein \u2014 whether measured as at least 0.8 to 1.0 grams per kilogram of body weight a day, or as 18 per cent or more of total calories \u2014 had lower risks of falls, of mobility limitations, of disability in the basic activities of daily living, of frailty, of declining walking speed, and of death itself.

The study, published in npj Aging, went further on a point that matters for the diaspora. Protein from animal sources, in particular, helped explain why healthy dietary patterns like the Mediterranean diet protected mobility. Protein was not a bystander in a good diet; it was a key working ingredient.

## The Pan-European Confirmation

If 532 people sounds small, a second study removes that worry. Drawing on the Survey of Health, Ageing and Retirement in Europe, an international team led from the University of Sharjah analysed more than 38,000 adults aged 50 and above across 27 countries, followed over several years. Those in the lowest tier of protein intake \u2014 measured by how often they ate dairy, eggs, legumes, fish and meat \u2014 had measurably higher odds of weak grip strength and of struggling with everyday tasks: walking 100 metres, kneeling, reaching overhead, pushing heavy objects.

The effects were modest per person but consistent across the huge sample, and they were sharper in specific groups. Men showed clear losses of strength; women aged 50 to 65 with low protein intake had more than double the odds of difficulty with basic self-care tasks. The conclusion was blunt: too little protein quietly erodes the physical independence that defines a good old age.

## The Twist on Supplements

Before anyone reaches for a tub of whey, a Tufts University study published in the American Journal of Clinical Nutrition adds a crucial qualifier. In older adults already getting the recommended amount of protein, piling on extra protein \u2014 the protein-boosted lattes, the fortified cereals, the shakes \u2014 did not build more muscle on its own. What built muscle was resistance exercise. Protein is the raw material; lifting is the signal that tells the body to use it. One without the other underperforms.

## Why the Diaspora Is Squarely in the Crosshairs

This is where the science meets a specific cultural reality. A large slice of the Indian diaspora is vegetarian or close to it, and traditional Indian vegetarian diets, for all their virtues, lean heavily on rice, wheat, and refined carbohydrates while running light on concentrated protein. Dal and dairy help, but the actual gram counts often fall well short of the 1.0 grams per kilogram these studies point to \u2014 especially for older adults, whose bodies extract protein less efficiently and who tend to eat less overall.

Layer that on top of a well-documented South Asian tendency toward low muscle mass and early sarcopenia, and the picture sharpens. The community already loses muscle younger; under-eating protein accelerates the slide. The result is the frail grandparent who cannot rise from a chair unaided, the parent whose fall becomes a fracture becomes a downward spiral \u2014 outcomes these studies tie directly to the protein gap.

## What a Higher-Protein Indian Plate Looks Like

The fix does not require abandoning vegetarianism or chasing American protein-marketing fads. It means deliberately front-loading protein the diaspora's own kitchen already contains: more dal and rajma and chana, paneer and curd and milk, soya, eggs for those who eat them, nuts and seeds, and \u2014 for non-vegetarians \u2014 fish, chicken and eggs at more meals than just dinner. Spreading protein across the day, rather than concentrating it in one meal, helps the ageing body absorb it. Aiming for a palm-sized portion of a protein-dense food at every meal is a simple rule of thumb.

And the Tufts finding makes the second half of the prescription non-negotiable. Protein without resistance training is a wasted opportunity. A pair of dumbbells, resistance bands, or even bodyweight squats and wall push-ups two or three times a week is what converts the extra dal into the strength to climb stairs at 80.

## The Reframe

None of this displaces the diaspora's real and justified worries about diabetes and heart disease. But it adds a missing one. For decades the community has been told what to cut \u2014 sugar, fried food, portion sizes. These studies are a reminder of something to add. The quietest threat to a long, independent old age may not be what is on the Indian plate, but what is missing from it."""
})

# ============================================================
# ARTICLE 3: Rupee rally & NRI remittance timing (markets-finance)
# ============================================================
articles.append({
    "headline": "The Rupee Just Hit a Five-Week High and May Climb to 92. For NRIs Sending Money Home, the Window Is Closing.",
    "subheadline": "A US\u2013Iran peace deal knocked oil prices to a three-month low and, stacked on the RBI's June measures to pull in dollars, sent the rupee surging for a third straight session to 94.56. One forecaster sees 92 per dollar by September. A stronger rupee is good news for India \u2014 but it means every dollar an NRI remits buys fewer rupees.",
    "slug": "rupee-rally-five-week-high-92-forecast-iran-peace-oil-nri-remittance-timing-20260616",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The rupee's direction is the single biggest variable in how much value an NRI's remittance or home-bound investment delivers \u2014 and with the currency now appreciating after months of weakness, the diaspora faces a narrowing window in which dollars still convert at favourable rates, a timing decision worth real money for anyone sending funds to family, servicing a loan, or funding property in India.",
    "sources": json.dumps([
        {"name": "Reuters (Indian rupee extends gains; US-Iran peace agreement details, Fed guidance awaited; rupee closes at 94.56)", "url": "https://www.reuters.com/markets/currencies/"},
        {"name": "Reuters (Rupee hits five-week high after oil plunges; traders eye further rally)", "url": "https://www.reuters.com/markets/currencies/"},
        {"name": "The Hindu BusinessLine (Oil retreat hands RBI an assist in boosting rupee's near-term outlook; 92 per dollar by September forecast)", "url": "https://www.thehindubusinessline.com/markets/forex/"}
    ]),
    "body": """For most of 2026, the story of the rupee has been one of grinding weakness \u2014 a record low near 97 to the dollar last month, billions in foreign money fleeing Indian stocks, and a central bank burning through its reserves to slow the slide. This week, the story flipped. And the reversal carries a direct, dollar-and-cents message for every non-resident Indian who moves money across the border.

## What Just Happened

On Tuesday the rupee closed up 0.2 per cent at 94.56 to the dollar, its third consecutive session of gains and a five-week high. The trigger was geopolitical: US President Donald Trump and Iran announced a preliminary deal to end their months-long war and reopen the Strait of Hormuz, the chokepoint through which roughly a fifth of the world's oil passes. Brent crude promptly tumbled below $81.50 a barrel, down from the war-inflated levels that had been punishing India \u2014 the world's third-largest oil importer, which buys nearly 90 per cent of its crude abroad.

Cheaper oil is oxygen for the rupee. It shrinks India's import bill, eases the current-account deficit, and cuts the dollar demand that oil companies generate \u2014 all of which lift the currency.

## The RBI's Hand on the Scale

The peace dividend did not arrive in a vacuum. At its June 5 policy meeting, the Reserve Bank of India left rates unchanged but rolled out a battery of measures explicitly designed to pull dollars into the economy, including the revival of a 2013-style window to mobilise funds from non-resident Indians and a subsidised hedging facility for overseas borrowing. Indian banks have already begun tapping it \u2014 HDFC Bank is reported to be raising at least $500 million in dollar bonds this week, with State Bank of India and Bank of Baroda close behind, and bankers expect $15 to $20 billion to flow in through this route over six months.

The combination \u2014 RBI machinery already building momentum, then oil collapsing on top of it \u2014 is why traders are suddenly bullish. Economists have upgraded India's balance-of-payments forecasts, with most now expecting a small surplus where they had feared a large deficit. One Singapore-based fund manager told reporters he expects the rupee to strengthen toward 92 per dollar by September, calling the currency undervalued.

## The Counterweights

Nobody is promising a straight line. Traders caution against a one-way rally, with near-term targets clustered around 93 to 94. The durability of the Iran peace deal is unproven \u2014 a preliminary agreement is not a permanent truce, and oil could spike again if it frays. India's monsoon has opened with a sizeable rain deficit, a risk to rural demand and food inflation. And the RBI itself may cap the appreciation: having built a record short-dollar forward book of around $104 billion defending the currency, it may use any strength to quietly unwind those positions rather than let the rupee run.

## Why This Is Money in NRI Pockets \u2014 or Out of Them

Here is the part the diaspora should read twice, because the same rupee move helps one NRI and hurts another. When the rupee strengthens \u2014 falls from 97 toward 92 per dollar \u2014 each dollar buys fewer rupees. For the millions who remit money to parents, service a home loan in India, pay for a wedding, or fund property, that is a real and rising cost. A family sending $2,000 a month home gets roughly \u20b910,000 less at 92 than they did at 97. The window in which dollars convert at the favourable, weak-rupee rates of recent months is, on these forecasts, closing.

The flip side applies to anyone moving the other way. NRIs repatriating funds from India to the US or UK \u2014 selling Indian assets, bringing back rental income, exiting investments \u2014 do better as the rupee strengthens, since their rupees fetch more dollars. And those holding rupee-denominated assets like Indian stocks or NRE deposits see the dollar value of those holdings rise as the currency climbs.

## The Practical Move

This is a timing decision, not a panic. For remitters, front-loading planned transfers \u2014 sending money for upcoming family needs or loan payments sooner rather than later, while the rupee is still relatively weak \u2014 captures the better rate before any further appreciation. The RBI's revived NRI deposit window, meanwhile, is offering unusually attractive dollar-deposit rates precisely because the central bank wants the diaspora's money; locking in those rates is its own opportunity, separate from the conversion question.

The broader lesson is one the diaspora relearns every cycle: the rupee is not background noise. It is the single biggest multiplier on the value of money moving between an NRI's two worlds. After months in which a weak rupee quietly rewarded everyone sending dollars home, the wind has shifted \u2014 and the smart response is to notice before the rate does it for you."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["person smartphone alone night", "loneliness person phone", "young woman using smartphone"],
                          ["person alone using phone night", "lonely person smartphone"]),
    articles[1]["slug"]: (["lentils dal pulses legumes", "cooked lentils food bowl", "eggs legumes protein food"],
                          ["lentils legumes protein food", "dal indian food bowl"]),
    articles[2]["slug"]: (["Indian rupee banknotes", "Reserve Bank of India building", "indian currency rupee notes money"],
                          ["indian rupee money currency", "indian rupee banknotes cash"]),
}
img_captions = {
    articles[0]["slug"]: "A person scrolling alone on a smartphone; a new US study links contacts never met in person to higher loneliness",
    articles[1]["slug"]: "A bowl of cooked lentils; new aging studies tie low protein intake to faster muscle loss and frailty",
    articles[2]["slug"]: "Indian rupee banknotes; the currency hit a five-week high this week with forecasts of further gains",
}
for art in articles:
    cq, pq = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq)
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
