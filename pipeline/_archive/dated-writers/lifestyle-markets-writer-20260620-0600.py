#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 06:00 UTC batch.
Topics:
  1. ENDO 2026 (Wenzhou Medical, Dr Xuejiang Gu): long daytime naps (>30 min) linked to higher MASLD/fatty-liver risk in T2D — lifestyle-health
  2. JACC / Harvard (Nurses' Health Study, 117K women): >=2h/wk resistance training → 20% lower CVD, 44% lower MI risk in women — lifestyle-health
  3. Jio Platforms files DRHP for ~$3.8bn IPO — India's largest ever; fresh issue of up to 270m shares — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0620b.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0620b.bin"):
            with open("/tmp/_img_dl0620b.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0620b.bin")
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
# ARTICLE 1: Long daytime naps & fatty liver in diabetics (lifestyle-health)
# ============================================================
articles.append({
    "headline": "That Long Afternoon Nap May Be Quietly Stressing a Diabetic's Liver, a New Study Warns",
    "subheadline": "Researchers tracking people with type 2 diabetes found that daytime naps longer than 30 minutes were linked to a higher risk of fatty liver disease \u2014 and combined with poor night sleep, the risk more than tripled.",
    "slug": "long-daytime-naps-fatty-liver-masld-risk-type-2-diabetes-endo-2026-wenzhou-diaspora-20260620-0600",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The afternoon nap is woven into Indian family life \u2014 the post-lunch 'aaram' is practically a cultural institution \u2014 even as type 2 diabetes and fatty liver disease run rampant through the community. A study suggesting that long naps may be quietly raising liver-disease risk in diabetics speaks directly to a habit most NRI households never think twice about.",
    "sources": json.dumps([
        {"name": "OnlyMyHealth \u2014 Long Daytime Naps May Increase Liver Disease Risk in People with Diabetes (ENDO 2026, Dr Xuejiang Gu, Wenzhou Medical University)", "url": "https://www.onlymyhealth.com/long-daytime-naps-may-increase-liver-disease-risk-in-people-with-diabetes-research-12977623728"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (June 13-16, 2026)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """In countless Indian homes, the long afternoon nap is sacrosanct \u2014 a heavy lunch, the heat of the day, and an hour or two of "aaram" to sleep it off. New research presented at the Endocrine Society's annual meeting suggests that for the millions of diaspora families living with type 2 diabetes, that habit may carry a hidden cost: a higher risk of fatty liver disease.

## What the Researchers Found

The study tracked people with type 2 diabetes and sorted them into four groups based on their sleep patterns: good nighttime sleep with short naps, good nighttime sleep with long naps, poor nighttime sleep with short naps, and poor nighttime sleep with long naps. A "long" nap was defined as a daytime sleep lasting more than 30 minutes.

Participants were followed for a little over three years on average. During that window, 379 people developed metabolic dysfunction-associated steatotic liver disease, or MASLD \u2014 the condition formerly known as non-alcoholic fatty liver disease, in which fat builds up in the liver and, over time, can drive inflammation, scarring and serious liver damage.

The pattern that emerged was striking. People who took long daytime naps had a higher risk of developing MASLD \u2014 even if they slept well at night. And the danger compounded: those who combined poor nighttime sleep with long daytime naps faced the steepest risk of all.

"Long naps appear to increase the likelihood of MASLD independently," explained Dr. Xuejiang Gu, the lead researcher from the First Affiliated Hospital of Wenzhou Medical University in China. He noted that poor nighttime sleep, together with long naps, can more than triple the risk of developing the disease in people with type 2 diabetes.

## Why Sleep and the Liver Are Linked

On the surface, an afternoon nap and the state of one's liver seem unconnected. But sleep is deeply entwined with metabolism. Disrupted or excessive sleep can throw off the body's handling of glucose and fat, fuel insulin resistance, and promote the very processes that cause fat to accumulate in the liver. Long daytime naps are also often a marker of poor-quality nighttime sleep, daytime fatigue, or an underlying metabolic problem \u2014 so they can signal trouble even when they are not directly causing it.

What makes this finding genuinely useful, the researchers stressed, is that sleep is something people can change. Unlike genetics or age, napping habits and nighttime sleep are modifiable. The team suggested that asking patients a few simple questions about their sleep could help doctors flag those at greater risk of liver disease \u2014 a cheap, easy screen for a condition that usually creeps up silently.

## Why This Lands Hard in Diaspora Homes

For the Indian diaspora, this research touches two raw nerves at once.

The first is diabetes. South Asians develop type 2 diabetes earlier, at lower body weights, and at far higher rates than most other populations. Type 2 diabetes is a near-constant presence in NRI families, often spanning generations under the same roof.

The second is fatty liver. MASLD has become quietly epidemic among Indians, including those who are lean and who drink little or no alcohol \u2014 a phenomenon doctors increasingly call "lean NAFLD" that is unusually common in South Asians. It frequently travels alongside diabetes, and the two conditions feed each other.

Layered on top is culture. The post-lunch nap is a fixture of Indian life, especially for older relatives, the retired, and anyone working from home. It is rarely seen as a health risk \u2014 if anything, it is treated as a wholesome, restful tradition. This study does not say the nap itself is harmful for everyone. But for the large slice of the diaspora already living with diabetes, it is a reason to look more closely at a daily habit that has always seemed benign.

## What To Actually Do

The takeaways here are practical, not alarmist. If you or an older family member has type 2 diabetes, the message is not to banish rest, but to be smart about it. Keep daytime naps short \u2014 the study's own dividing line was 30 minutes, and sleep experts generally favour "power naps" of 20 to 30 minutes over long ones. A long, regular nap may be worth mentioning to a doctor, partly because it can be a sign of poor nighttime sleep that is worth fixing.

Above all, protect nighttime sleep, since the worst outcomes clustered among those with poor night sleep *and* long naps. And given how common both diabetes and fatty liver are in the community, it is reasonable for diabetic adults to ask their doctor about a simple liver check. The broader lesson is one the study's authors made plainly: for people with diabetes, sleep belongs on the same list as diet and exercise \u2014 a daily habit that quietly shapes long-term health."""
})

# ============================================================
# ARTICLE 2: Resistance training & heart disease in women (JACC, Harvard) (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Two Hours of Lifting a Week Cut Women's Heart-Attack Risk by 44 Percent, a Harvard Study of 117,000 Women Finds",
    "subheadline": "A new analysis in the Journal of the American College of Cardiology followed women for decades and found that resistance training delivered outsized protection against heart disease \u2014 a finding with particular weight for South Asian women, who face heart trouble earlier and harder.",
    "slug": "resistance-training-women-44-percent-lower-heart-attack-risk-jacc-harvard-nurses-health-study-diaspora-20260620-0600",
    "category": "lifestyle-health",
    "vertical": "womens-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian women carry an elevated, often under-recognised risk of heart disease, yet strength training remains culturally coded as a man's pursuit in many Indian families. A landmark study showing that just two hours of lifting a week slashes women's heart-attack risk speaks directly to a community where the gym is rarely seen as a place for mothers and aunties \u2014 and where the cost of that gap is measured in early heart disease.",
    "sources": json.dumps([
        {"name": "Journal of the American College of Cardiology \u2014 Resistance training and cardiovascular disease risk in women (Nurses' Health Study, Tianyue Zhang et al., June 17, 2026)", "url": "https://www.jacc.org/"},
        {"name": "Harvard T.H. Chan School of Public Health \u2014 Nurses' Health Study", "url": "https://www.hsph.harvard.edu/"},
        {"name": "MedicalXpress \u2014 Resistance training linked to lower heart disease risk in women", "url": "https://medicalxpress.com/"}
    ]),
    "body": """Cardio has long owned the conversation about heart health \u2014 the running, the brisk walking, the steps counted on a wrist. A major new study suggests that for women, the weights deserve at least as much credit. Published this week in the *Journal of the American College of Cardiology* (JACC), it found that women who did regular resistance training had dramatically lower rates of heart disease, with the single most eye-catching number being a 44 percent reduction in heart-attack risk.

## A Vast, Decades-Long Dataset

The strength of the finding lies in the data behind it. Researchers drew on the Nurses' Health Study I and II \u2014 among the largest and longest-running investigations of women's health ever conducted \u2014 following 117,025 women over many years. That scale lets scientists tease apart the effect of one behaviour, like lifting weights, from the noise of everything else in people's lives.

The lead author, Dr. Tianyue Zhang of the Harvard T.H. Chan School of Public Health, and senior author Edward Giovannucci examined how much resistance training the women did and what happened to their hearts over time. The results were clear and graded: women who engaged in at least two hours of resistance training per week had roughly a 20 percent lower risk of major cardiovascular disease overall \u2014 and a 44 percent lower risk of heart attack specifically \u2014 compared with women who did none.

Crucially, the benefit appeared on top of, not instead of, aerobic exercise. Women who combined resistance training with cardio fared best of all, suggesting the two forms of exercise protect the heart through complementary routes rather than competing for the same effect.

## Why Muscle Matters for the Heart

The mechanisms make biological sense. Resistance training builds and preserves muscle, which acts as a metabolic sink for blood sugar, improving insulin sensitivity and helping keep type 2 diabetes \u2014 a powerful driver of heart disease \u2014 at bay. It improves body composition, lowers blood pressure over time, and helps manage cholesterol and chronic inflammation. For women specifically, strength training also defends against the loss of muscle and bone that accelerates after menopause, a period when cardiovascular risk climbs sharply.

The JACC editorial leadership took notice. The journal's editor-in-chief, the prominent Yale cardiologist Harlan Krumholz, has repeatedly emphasised that resistance training is too often left out of heart-health advice aimed at women. This study adds hard, large-scale evidence to a message that has struggled to break through.

## Why South Asian Women Should Pay Attention

For the diaspora, the finding carries extra freight. South Asians as a group face a well-documented, elevated risk of cardiovascular disease, developing it earlier and at lower body weights than many other populations. South Asian women, in particular, often see their risk underestimated \u2014 by doctors and by themselves \u2014 because heart disease is still wrongly thought of as a men's problem. Diabetes, a major amplifier of heart risk, is also disproportionately common in the community.

Then there is culture. In many Indian families, strength training is quietly coded as a young man's pursuit \u2014 the gym is for sons, not for mothers and aunties. Women's exercise, when it happens at all, tends to be walking or the occasional yoga class. Both are valuable, but neither builds muscle the way resistance training does. The result is a community in which the women at meaningfully elevated heart risk are often the least likely to be doing the one form of exercise this study links to the largest drop in heart attacks.

## What To Actually Do

The practical bar set by the study is encouraging precisely because it is modest: about two hours of resistance training a week. That can be split into two or three sessions, and it does not require a fancy gym. Bodyweight movements \u2014 squats, push-ups, lunges, planks \u2014 resistance bands, or a few household weights at home all count. The point is to challenge the muscles regularly.

For South Asian women, especially those approaching or past menopause, or with a family history of diabetes or heart disease, this is worth treating as preventive medicine rather than vanity. Pairing strength work with the walking or cardio many already do appears to offer the best protection of all. As ever, anyone with existing health conditions should check with a doctor before starting, and beginners are wise to learn good form to avoid injury. But the headline is simple and hard to ignore: for a woman's heart, lifting is not optional extra credit \u2014 it may be among the most powerful protections available."""
})

# ============================================================
# ARTICLE 3: Jio Platforms files for record IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "Jio Files for India's Biggest-Ever IPO \u2014 and for the First Time, the Diaspora Can Own a Piece of It",
    "subheadline": "Mukesh Ambani's Jio Platforms has filed papers for a Mumbai listing aiming to raise around $3.8 billion, eclipsing every IPO India has seen. For NRIs who use Jio to call home, the company they rely on is about to become one they can invest in.",
    "slug": "jio-platforms-files-record-ipo-3-8-billion-india-largest-ambani-drhp-nri-investor-20260620-0600",
    "category": "markets-finance",
    "vertical": "markets",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Jio is the invisible infrastructure of diaspora life \u2014 the SIM in a parent's phone, the data behind every video call home, the connection that keeps NRI families tethered to India. Now the company behind it is filing for the country's largest-ever IPO, turning a service the diaspora depends on into an asset it can, for the first time, actually own a share of.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Ambani's Jio Platforms files for $3.8 billion IPO that could be India's biggest", "url": "https://www.reuters.com/business/ambanis-jio-platforms-eyes-record-38-billion-indian-ipo-sources-say-2026-06-19/"},
        {"name": "The Hindu BusinessLine \u2014 Jio files for likely record IPO as focus shifts from buildout to monetisation", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reliance Industries \u2014 Mukesh Ambani AGM shareholder address (June 19, 2026)", "url": "https://www.ril.com/"}
    ]),
    "body": """India's stock market is about to meet its biggest test yet. On June 19, at Reliance Industries' annual shareholder meeting, chairman Mukesh Ambani confirmed that Jio Platforms \u2014 the telecom-to-AI giant at the heart of his empire \u2014 had filed its draft prospectus for a Mumbai listing. The offering aims to raise around $3.8 billion, which would make it the largest initial public offering in India's history.

## The Numbers Behind the Headline

According to the filing and people familiar with the process, the IPO targets a fundraising of roughly 360 billion rupees, or about $3.81 billion, equal to around 2.9 percent of the company's post-issue equity. The deal is structured as a fresh issue of up to 270 million new shares \u2014 meaning the money raised flows into the company rather than to existing shareholders cashing out.

If it lands at that size, the listing would surpass Hyundai Motor India's roughly 27,870-crore-rupee offering from 2024, currently the country's biggest. Brokerages estimate the issue could ultimately raise between 33,000 crore and 38,000 crore rupees and value the company somewhere between 12 and 15 lakh crore rupees. Outside estimates of Jio's worth have ranged widely \u2014 Jefferies has pegged it near $180 billion in the past, while more recent calculations tied to the IPO price imply a valuation closer to $131 billion.

"The Jio IPO is described as the most important value creation milestone this year," Ambani told shareholders.

The proceeds have a clear, somewhat sobering purpose: the bulk will go toward repaying debt. Jio plans to use an estimated 27,500 crore rupees of the money to pay down borrowings at Reliance Jio Infocomm, its telecom arm \u2014 debt repayment that could absorb the lion's share of what the offering raises. The company framed this as clearing the decks for its next phase: "5G network densification and expansion, fixed broadband penetration, AI and cloud services."

## A Company the Diaspora Already Knows

Jio is not an abstraction to the Indian diaspora \u2014 it is part of daily life. It is the world's second-largest telecom operator by single-country subscribers, trailing only China Mobile, with roughly 500 million users, and it carries around 60 percent of all of India's data traffic. For NRIs, Jio is very often the SIM in a parent's phone back home, the network behind every WhatsApp video call to family, the cheap data that transformed how a billion-plus Indians \u2014 and their relatives abroad \u2014 stay connected.

That ubiquity is exactly why the IPO is notable for overseas Indians. Jio Platforms also houses Reliance's AI, cloud and enterprise businesses, and it already counts marquee global names among its backers \u2014 Meta holds 9.99 percent and Google 7.73 percent, stakes acquired during the 2020 fundraising spree that pulled in over 1.5 lakh crore rupees from a who's who of global investors. Until now, that kind of exposure to Jio was the preserve of sovereign wealth funds and private-equity giants. A public listing changes that.

## What It Means for NRIs

For the diaspora, the listing turns a service into a potential investment \u2014 but it warrants a clear-eyed look rather than blind enthusiasm.

First, **NRIs can participate, within rules**. Overseas Indians can invest in Indian IPOs through NRE or NRO accounts and the proper portfolio routes, subject to the regulatory framework and the categories the issue sets aside. Anyone interested should sort out the right account structure and talk to a broker or advisor well before the issue opens.

Second, **read what the prospectus actually says**. The romance of owning a piece of Jio should not obscure the fundamentals. Jio Platforms reported a consolidated net profit of about 30,064 crore rupees on revenue of roughly 1.49 lakh crore in the last financial year \u2014 real, growing profitability. But the company has also flagged significant indebtedness, large outstanding tax claims, and a capital-intensive business that swallows a fifth of its revenue in spending each year. That most of the IPO money goes to paying down debt rather than funding new growth is a detail worth weighing.

Third, **mind the timing and the mood**. The listing arrives just as India's markets have cooled, rattled by geopolitical tension in the Gulf and softer global sentiment. A mega-IPO of this size will test how much appetite investors really have. Final terms, pricing and the listing date can still shift before the offer opens.

The bigger picture is symbolic as much as financial. For the diaspora, Jio has long been the invisible thread connecting them to home. Soon it may also be a line on their brokerage statement \u2014 a rare chance to own a share of the infrastructure that carries their own voices back to India."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["man sleeping nap sofa afternoon", "person sleeping daytime rest", "human liver anatomy medical"],
                          ["man napping on couch afternoon", "person sleeping daytime"], None),
    articles[1]["slug"]: (["woman lifting dumbbell weights gym", "woman strength training exercise", "woman fitness workout weights"],
                          ["woman lifting weights gym", "woman strength training dumbbells"], None),
    articles[2]["slug"]: (["Reliance Jio store India", "Mukesh Ambani Reliance", "smartphone India mobile network"],
                          ["smartphone mobile india", "indian rupee stock market"], "Mukesh Ambani"),
}
img_captions = {
    articles[0]["slug"]: "A study of people with type 2 diabetes linked daytime naps over 30 minutes to higher fatty-liver risk",
    articles[1]["slug"]: "A Harvard study of 117,000 women found two hours of resistance training a week cut heart-attack risk by 44%",
    articles[2]["slug"]: "Jio Platforms has filed for what would be India's largest-ever IPO, aiming to raise around $3.8 billion",
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
