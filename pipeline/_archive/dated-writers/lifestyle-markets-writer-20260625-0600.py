#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 06:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Dasman Diabetes Institute (Kuwait) 16-week mouse study presented at ENDO 2026:
     a COMPLETELY sugar-free low-fat diet unexpectedly disrupted the gut microbiome,
     caused insulin resistance, intestinal/liver inflammation and fatty-liver changes
     despite no weight gain. Lesson: balance beats elimination. — lifestyle-health
     (Distinct from recent IF-vs-calorie & keto-depression pieces: this is about
      cutting sugar entirely backfiring.)
  2. Stony Brook / SLEEP 2026 (Future of Families cohort, ~2,011 + actigraphy 295):
     poor sleep regularity and insomnia in adolescence (age 15) predicted worse
     general health, hospitalization and lower life satisfaction in young adulthood
     (age 22). — lifestyle-health
  3. India gold demand slump: domestic prices ~Rs1.46 lakh/10g (lowest since early
     April), dealers quoting discounts up to $54/oz, first gold-ETF monthly outflow
     in a year, India deliberately discouraging gold buying to defend the rupee amid
     high oil import bills. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0600z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0600z.bin"):
            with open("/tmp/_img_dl0600z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0600z.bin")
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
# ARTICLE 1: Sugar-free diet backfires (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cutting Out Sugar Entirely May Backfire, a New Study Warns \u2014 Balance Beats Elimination",
    "subheadline": "In a 16-week experiment, animals fed a low-fat diet stripped of all table sugar developed gut imbalance, insulin resistance and early fatty-liver changes \u2014 even though they gained no extra weight. The lesson, researchers say, is that the body needs balanced carbohydrates, not a zero.",
    "slug": "sugar-free-diet-gut-microbiome-insulin-resistance-fatty-liver-dasman-endo-2026-balanced-carbs-diaspora-20260625-0600",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Sugar has become the villain of choice in diaspora wellness circles \u2014 'no-sugar' challenges, sugar-free mithai and zero-sugar swaps are everywhere among health-conscious NRIs guarding against the community\u2019s steep diabetes risk \u2014 so a study suggesting that total elimination can harm gut and metabolic health is a timely reminder that balance, not a blanket ban, is what protects the body.",
    "sources": json.dumps([
        {"name": "Fox News Health \u2014 'Zero sugar, more problems? Study reveals surprising gut health effects'", "url": "https://www.foxnews.com/health/zero-sugar-problems-study-reveals-surprising-gut-health-effects"},
        {"name": "Endocrine Society / ENDO 2026 \u2014 Rasheed Ahmad et al., Dasman Diabetes Institute, sucrose-free low-fat diet mouse study", "url": "https://www.endocrine.org/news-and-advocacy/news-room"},
        {"name": "Where The Food Comes From \u2014 'New Animal Study Finds Sugar-Free Low-Fat Diet May Be Linked To Gut Imbalance, Insulin Resistance, And Fatty Liver Changes'", "url": "https://wherethefoodcomesfrom.com/"}
    ]),
    "body": """For years the advice has felt almost self-evident: sugar is the enemy, so the less of it the better, and zero would be best of all. A new study presented at one of the world's biggest hormone-science meetings complicates that tidy story. It suggests that taking sugar all the way down to nothing \u2014 at least in one common dietary pattern \u2014 may do more harm than good.

## A Test of Total Elimination

Researchers at the Dasman Diabetes Institute in Kuwait City set out to answer a question that, surprisingly, had gone largely unexamined: what happens when you remove sugar entirely, rather than simply cutting back? They presented their findings at ENDO 2026, the Endocrine Society's annual meeting in Chicago.

The team fed two groups of mice a low-fat diet for 16 weeks. The diets were identical but for one variable. One group's food contained a normal amount of sucrose \u2014 ordinary table sugar. The other group's food was completely sugar-free. Over the four months, the scientists tracked a wide battery of measures: body weight, glucose tolerance, insulin sensitivity, circulating metabolic hormones, inflammation in the colon and liver, and the makeup of the gut microbiome.

## Thinner, but Not Healthier

The most striking part of the result is what did not happen. The mice on the sugar-free diet did not gain extra weight; on the scale, they looked no worse than the control group. By the crude yardstick most dieters use, the sugar-free regimen looked like a success.

Underneath the surface, the picture was very different. The sugar-free animals developed impaired glucose control and insulin resistance \u2014 the metabolic machinery that, in humans, sits at the root of type 2 diabetes. Their gut bacteria fell out of balance. They showed inflammation in the intestines and the liver, along with early fatty-liver changes. In other words, the diet that produced no weight gain was quietly degrading the very systems that weight is supposed to be a proxy for.

"Completely removing sucrose from a low-fat diet may unexpectedly disrupt gut health and promote inflammation and metabolic dysfunction, highlighting that balanced nutrition is more important than simply eliminating sugar," said Rasheed Ahmad, principal scientist and head of the Immunology and Microbiology Department at the institute, which was founded by the Kuwait Foundation for the Advancement of Sciences.

## Why Zero Might Be Worse Than Some

How could removing something widely blamed for ill health make things worse? The researchers point to the gut. The trillions of microbes living in the intestine feed on carbohydrates, and stripping out a familiar source appears to have shifted that ecosystem in an unhealthy direction \u2014 reducing helpful bacteria and tilting the balance toward inflammation. Because the gut microbiome talks constantly to the body's metabolism and immune system, a disturbance there can ripple outward into insulin signalling and liver fat.

"The study highlights the importance of maintaining balanced dietary carbohydrates to support gut and immune homeostasis," Ahmad said.

A few caveats deserve emphasis. This was a study in mice, not people, and animal results do not translate directly to the human body; the findings are a signal for further research, not a clinical instruction. The diet tested was an extreme one \u2014 the complete absence of sucrose \u2014 not the moderate sugar reduction most health guidance actually recommends. Nobody is suggesting people should eat more sugar. The mainstream advice to cut back on added sugars, sugary drinks and ultra-processed sweets remains solidly grounded. What this work questions is the leap from "less" to "none," and the assumption that the most aggressive possible cut is automatically the healthiest.

## Why It Matters for the Diaspora

In diaspora wellness culture, sugar has been cast as the supervillain. No-sugar months, sugar-free barfi and ladoo, monk-fruit and stevia swaps, and proud declarations of having "quit sugar entirely" have become badges of discipline among health-conscious Indians abroad. The impulse is understandable: people of South Asian origin carry an outsized risk of type 2 diabetes and often develop it at lower body weights and younger ages than other groups, so the fear of sugar is rooted in a real and pressing danger.

But this study is a useful corrective to the all-or-nothing instinct. The body, it suggests, is not built for zeroes; it runs on balance. The healthier path is almost certainly the unglamorous middle \u2014 cutting added sugars and sweet drinks sharply while keeping a sensible base of wholesome carbohydrates like dal, vegetables, fruit and whole grains that feed a thriving gut. For a community that swings hard between festival tables piled with sweets and punishing elimination diets, the most valuable takeaway may be that the answer to too much sugar is not none of it. Moderation, the oldest and least fashionable advice in nutrition, keeps proving stubbornly hard to beat."""
})

# ============================================================
# ARTICLE 2: Teen sleep predicts young-adult health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Poor Sleep in the Teenage Years Casts a Long Shadow Into Adulthood, a New Study Finds",
    "subheadline": "Tracking young people from age 15 to 22, researchers found that irregular sleep and insomnia symptoms as a teenager predicted worse health, more hospital stays and lower life satisfaction years later \u2014 evidence that adolescent sleep is an investment, not a luxury.",
    "slug": "adolescent-sleep-insomnia-irregularity-predicts-young-adult-health-hospitalization-stony-brook-sleep-2026-diaspora-20260625-0600",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "In high-achieving Indian and South Asian households, late-night study, packed extracurriculars and the quiet glorification of running on little sleep are common among teenagers chasing top grades and college admissions \u2014 so evidence that adolescent sleep shapes health and wellbeing for years afterward speaks directly to how diaspora families weigh academic pressure against rest.",
    "sources": json.dumps([
        {"name": "Medical Xpress \u2014 'Poor sleep health in adolescence linked to hospitalization and worse health in young adulthood'", "url": "https://medicalxpress.com/news/2026-06-poor-health-adolescence-linked-hospitalization.html"},
        {"name": "Gina Marie Mathew et al., Stony Brook University (Renaissance School of Medicine) \u2014 SLEEP 2026 / SLEEPJ, Future of Families and Child Wellbeing Study", "url": "https://doi.org/10.1093/sleep/zsag091.0245"}
    ]),
    "body": """Teenagers are famous for treating sleep as optional \u2014 something to be sacrificed for a deadline, a screen or a social life, and made up for some other day. A new study suggests the bill for that habit may come due far later than anyone realises, arriving years afterward in the form of worse health, more hospital visits and a dimmer sense of wellbeing in young adulthood.

## Following the Same Young People for Seven Years

The research, presented at SLEEP 2026 \u2014 the annual gathering of the sleep-medicine field \u2014 and led by Gina Marie Mathew of the Renaissance School of Medicine at Stony Brook University, drew on the Future of Families and Child Wellbeing Study, a large, diverse, long-running American birth cohort. Its power lies in following the same individuals over time rather than taking a single snapshot.

Researchers measured sleep at age 15 in two ways. A subset of 295 young people wore wrist actigraphy monitors \u2014 devices that objectively track sleep and movement \u2014 while a larger group of 2,011 reported their own insomnia symptoms. The team then checked back when the participants had reached age 22, looking at their general health, whether they had been hospitalised overnight in the previous year, and how satisfied they felt with their lives. The analysis adjusted for sociodemographic factors and for the teenagers' health and wellbeing at the outset, helping to isolate the role of sleep itself.

## The Long Reach of a Restless Adolescence

The pattern that emerged was consistent and sobering. Teenagers with poorer sleep health \u2014 more irregular sleep and more insomnia symptoms \u2014 went on to report worse general health as young adults. They were more likely to have spent a night in hospital. Difficulty falling asleep in adolescence was also linked to lower odds of feeling satisfied with life at 22.

"Improving youth sleep regularity and insomnia symptoms among youth may protect young adult health, well-being, and overall quality of life," Mathew said. The findings, she noted, "highlight the importance of addressing sleep health early, as the potential effects on other aspects of health and well-being can persist into young adulthood."

Crucially, the study points to more than just how many hours teenagers clock. Regularity \u2014 going to bed and waking at consistent times \u2014 and the presence or absence of insomnia symptoms mattered too. A teenager who sleeps a ragged, unpredictable schedule, or who lies awake unable to drop off, may be storing up trouble even if the raw hours occasionally add up.

## What Healthy Teen Sleep Looks Like

Sleep specialists describe healthy rest as resting on several pillars: adequate duration, good quality, appropriate timing, regularity, and the absence of disorders. The American Academy of Sleep Medicine recommends that adolescents aged 13 to 18 get eight to ten hours on a regular basis. Many teenagers fall well short, squeezed by early school start times, homework, jobs, social lives and the gravitational pull of phones late into the night.

As an observational study, this research shows association rather than ironclad cause and effect, and it was presented at a conference, a stage that typically precedes full peer-reviewed publication. But it converges with a deep body of evidence that sleep in the adolescent years \u2014 a period of intense brain development \u2014 is foundational rather than disposable. The takeaway is not alarm but emphasis: the rest a 15-year-old gets is quietly shaping the adult they are becoming.

## Why It Matters for the Diaspora

In many Indian and South Asian families, academic achievement is treated as close to sacred, and the teenage years are organised around it. Late-night study sessions, coaching classes stacked on top of full school days, competitive entrance-exam preparation and a packed roster of extracurriculars are worn almost as proof of seriousness. Running on four or five hours of sleep can be quietly admired \u2014 evidence of a child who is working hard enough.

This study reframes that calculation. Sleep is not time stolen from achievement; it is part of the foundation that makes sustained achievement, and lasting health, possible. The very pressure meant to secure a teenager's future may, by eroding their sleep, be undermining the health and wellbeing they will carry into adulthood. For diaspora parents weighing one more hour of revision against one more hour of rest, the evidence increasingly favours rest. Protecting a regular bedtime, easing off the late-night screens and treating sleep as non-negotiable may be among the most consequential investments a family can make in a child \u2014 one whose returns show up not in the next exam, but in the decades that follow."""
})

# ============================================================
# ARTICLE 3: India gold demand slump (markets-finance)
# ============================================================
articles.append({
    "headline": "India Is Quietly Talking Itself Out of Gold \u2014 and the World's Bullion Market Is Feeling It",
    "subheadline": "Domestic gold has slid to its lowest price since early April, dealers are quoting steep discounts, and the country's gold ETFs just logged their first monthly outflow in a year. Behind the cooling is a deliberate push to curb gold buying and defend a battered rupee.",
    "slug": "india-gold-demand-slump-domestic-price-discount-etf-outflow-rupee-defence-import-curbs-nri-investor-20260625-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Gold is woven into diaspora life \u2014 the wedding jewellery, the festival purchases, the rupee-denominated savings that NRIs hold as a hedge \u2014 so India\u2019s campaign to cool gold demand, the slide in domestic prices and the steep dealer discounts directly shape when and how non-resident Indians buy, gift and store the metal both abroad and back home.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'ASIA GOLD: Price volatility keeps India demand modest, China flips to discount'", "url": "https://www.reuters.com/markets/commodities/asia-gold-price-volatility-keeps-india-demand-modest-china-flips-discount-2026-06-20/"},
        {"name": "USA Today \u2014 'Will gold hit $5,000 again this year? Experts explain what\u2019s driving prices now'", "url": "https://www.usatoday.com/money/blueprint/investing/will-gold-hit-5000/"},
        {"name": "Patna Press / India Bullion and Jewellers Association (IBJA) \u2014 'Gold Climbs To Rs 1.46 Lakh, Silver Rebounds To Rs 2.37 Lakh As Bullion Prices Rise'", "url": "https://patnapress.com/"}
    ]),
    "body": """For a country that buys gold the way others buy bread, India is in an unusual mood. Demand for the metal that anchors its weddings, festivals and household savings has gone quiet \u2014 and the chill is being felt all the way out in the global bullion market. Behind it lies a rare and deliberate effort by the Indian state to talk its own citizens out of buying gold, all in the service of rescuing a struggling rupee.

## A Market Gone Cold

The numbers tell the story. Domestic gold prices fell to about 146,252 rupees per 10 grams in mid-June, the lowest level since early April. Yet even as prices eased \u2014 normally a cue for Indian buyers to pile in \u2014 the crowds did not come. Dealers across the country were quoting discounts of up to $54 an ounce below official domestic prices, a gap that includes India's hefty 15 percent import duty and 3 percent sales levy. That discount had widened sharply from around $35 the week before, a classic sign of weak local appetite: when sellers must cut prices to move metal, demand is soft.

"The price correction is helping bring buyers back to the market, but excessive volatility is prompting some buyers to wait for a clearer price trend," an Ahmedabad-based jeweller told Reuters. A Mumbai bullion dealer was blunter: "Investment demand has remained weak over the past few weeks."

The retreat extends to paper gold as well. India's physically backed gold exchange-traded funds recorded their first net monthly outflow in a year in May, as investors took profits after an earlier rally driven up by higher import duties. When even the ETF investors are heading for the exits, the cooling is broad.

## A Government Nudging People Away From Gold

What makes this slump unusual is that it is, in part, by design. India has spent much of 2026 discouraging its citizens from buying gold \u2014 an extraordinary stance in a country where the metal is cultural bedrock \u2014 and the motive is the rupee.

The logic runs through the country's foreign-exchange reserves. Gold, like oil, is priced and paid for in dollars. With crude oil costs elevated for much of the year amid conflict in the Middle East, India has already been spending heavily on dollars to fund its fuel imports, draining reserves and pressuring the currency. Layer large gold imports on top and the demand for dollars climbs further, weakening the rupee even more. By damping gold buying, New Delhi is trying to relieve that pressure. "This year, India has been discouraging its citizens from buying gold in hopes that it will help the value of the Indian Rupee," market analyst Mukerji told USA Today, noting that India "is a major player in the gold markets."

It appears to be working at the margin. The rupee, which had plunged to a record low near 97 per dollar earlier in the crisis, has since steadied, helped by firm central-bank intervention, a basket of policy measures to draw in dollar inflows, and a recent retreat in oil prices. Softer Indian demand is one quiet contributor to that stabilisation \u2014 and, because India is so large a buyer, it is also part of why global gold has struggled to reclaim its highs.

## Below the Peaks, and Volatile

Gold today sits well off its records. Having started the year near 133,000 rupees per 10 grams, the metal spiked to an all-time high of about 176,000 rupees in late January before sliding roughly 30,000 rupees from that peak. In dollar terms, prices have fallen more than 20 percent since the start of the Middle East conflict in late February, pressured by fears of energy-driven inflation and expectations that the US Federal Reserve may raise interest rates \u2014 a move that makes interest-bearing assets more attractive than gold, which pays nothing. The metal has been whipsawed all year by the dollar, central-bank policy and shifting risk appetite, with sharp corrections punctuating the swings.

## Why It Matters for the Diaspora

Few assets are as bound up with diaspora identity as gold. It is the jewellery handed down at weddings, the coins gifted at Diwali and Akshaya Tritiya, the discreet rupee-denominated hedge that many non-resident Indian families keep as ballast against uncertainty. So India's campaign to cool gold demand, and the price moves that follow, land squarely in the diaspora's lap.

For an NRI weighing a purchase, the current picture cuts two ways. Domestic prices are at multi-month lows and dealers are offering discounts, which can make this an attractive window to buy jewellery or coins, whether abroad or on a trip home. At the same time, the volatility is a genuine warning: a metal that can swing 30,000 rupees in months is not the placid store of value family lore often makes it out to be. And the bigger backdrop matters for anyone with money in India \u2014 the same rupee-defence effort that is nudging gold buyers to the sidelines is the one shaping the value of remittances, deposits and investments back home. For the diaspora, gold remains both a treasured tradition and, this year more than most, a reminder that even the most trusted of assets moves to the rhythm of oil, the dollar and the rupee."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["sugar cubes white sugar bowl", "sugar spoon white granulated", "gut intestine health illustration"],
                          ["sugar cubes bowl", "white sugar spoon"], None),
    articles[1]["slug"]: (["teenager sleeping bed", "person sleeping bedroom night", "alarm clock bedside sleep"],
                          ["teenager sleeping bed", "person asleep bedroom"], None),
    articles[2]["slug"]: (["gold jewellery India bangles", "gold bars bullion", "gold coins jewelry shop India"],
                          ["gold jewellery bangles india", "gold bars bullion"], None),
}
img_captions = {
    articles[0]["slug"]: "A 16-week study found that a low-fat diet with all table sugar removed harmed gut and metabolic health in mice",
    articles[1]["slug"]: "Researchers tracked young people from age 15 to 22, linking poor teenage sleep to worse adult health",
    articles[2]["slug"]: "Indian gold demand has cooled to multi-month lows as the country curbs buying to defend the rupee",
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
