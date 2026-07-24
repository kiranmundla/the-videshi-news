#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 18:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. Yale/Geriatrics study: nearly half of adults 65+ improved in cognition,
     physical function, or both over 12 years (HRS, n>11,000); positive beliefs
     about aging strongly predicted improvement. Lead author Becca Levy. — lifestyle-health
  2. National Sleep Foundation study in journal Sleep (n>3,100): adults who feel
     older than their chronological age report worse sleep — insomnia, irregular
     patterns, daytime fatigue; "how old do you feel?" as a screening cue.
     Backed by Karolinska RSPB 2024 + Korean Sleep & Headache studies. — lifestyle-health
  3. GIFT City as a new route for Indian residents/NRIs into global markets —
     fund-level taxation (after-tax redemptions), LRS $250k limit, 20% TCS over
     Rs10 lakh, US-stock capital-gains/dividend mechanics; AIF assets up ~300% YoY
     to ~$12bn. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800z.bin"):
            with open("/tmp/_img_dl1800z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800z.bin")
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
# ARTICLE 1: Yale aging-mindset study (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Aging Doesn't Have to Mean Decline \u2014 Nearly Half of Older Adults Got Sharper or Stronger, a Yale Study Finds",
    "subheadline": "Tracking more than 11,000 older Americans for over a decade, Yale researchers found that 45 percent improved in memory, mobility, or both \u2014 and the people most likely to gain were those who held a more hopeful view of growing old.",
    "slug": "yale-aging-mindset-older-adults-improve-cognition-physical-function-geriatrics-health-retirement-study-diaspora-20260624-1800",
    "category": "lifestyle-health",
    "vertical": "longevity",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many Indian diaspora families care for ageing parents and grandparents across continents, and the cultural script of later life is often one of inevitable frailty and dependence; this study suggests that mindset itself shapes how elders age \u2014 a reason to treat older relatives as capable of growth rather than quietly writing off their decline.",
    "sources": json.dumps([
        {"name": "Yale School of Public Health \u2014 'New study challenges notion that aging means decline, finds many older adults improve over time'", "url": "https://ysph.yale.edu/news-article/new-study-challenges-notion-that-aging-means-decline-finds-many-older-adults-improve-over-time/"},
        {"name": "Medical Xpress \u2014 'Study finds 45% of adults 65 and older improved over 12 years'", "url": "https://medicalxpress.com/news/2026-adults-older-years.html"},
        {"name": "New York Post \u2014 'Yale study finds the secret to aging well over 65'", "url": "https://nypost.com/"}
    ]),
    "body": """The story we tell about old age is, almost always, a story of decline \u2014 a slow downhill slide of fading memory, slowing steps and shrinking horizons. A new study from Yale University suggests that story is, for a great many people, simply wrong. Over more than a decade, nearly half of the older adults the researchers followed got measurably better, not worse \u2014 and a surprising factor predicted who improved.

## What the Researchers Did

The study, published in the journal Geriatrics, was led by Dr. Becca R. Levy, a professor of social and behavioural sciences at the Yale School of Public Health and one of the world's leading experts on the psychology of ageing. Her team drew on the Health and Retirement Study, a large, federally supported survey that has tracked a nationally representative group of older Americans for years.

The researchers followed more than 11,000 participants aged 65 and over for up to 12 years. They measured two things repeatedly: cognition, using a standard performance assessment of memory and mental arithmetic, and physical function, gauged by walking speed \u2014 a measure geriatricians treat as a vital sign because it tracks so closely with disability, hospitalisation and survival.

## The Findings

The headline number upends the usual narrative. Over the follow-up period, 45 percent of participants improved in at least one of the two domains. About 32 percent got better cognitively and 28 percent improved physically, and many of those gains were large enough to be considered clinically meaningful \u2014 not statistical noise, but real, noticeable change.

"Many people equate ageing with an inevitable and continuous loss of physical and cognitive abilities," Levy said. "What we found is that improvement in later life is not rare, it's common, and it should be included in our understanding of the ageing process." If the figures were extrapolated to the whole United States, the authors noted, they would imply that more than 26 million older people are experiencing genuine improvement in how they function.

## The Power of Mindset

The most striking part of the study was not that people improved, but who did. Participants who held more positive beliefs about ageing at the outset \u2014 who disagreed with statements like "the older I get, the more useless I feel" and agreed that "I am as happy now as when I was younger" \u2014 were significantly more likely to improve in both cognition and physical function. The link held up even after the researchers accounted for age, sex, education, depression and the burden of chronic disease.

Why would attitude translate into sharper memory or a faster walk? Levy's earlier work offers clues: people with a more hopeful view of ageing tend to stay more active, follow medical advice more closely, manage stress better and recover more fully from illness and injury. Belief, in other words, shapes behaviour, and behaviour shapes the body.

## The Caveats

This is observational research, and it cannot prove that optimism causes improvement; it is possible that people who were already healthier simply felt better about ageing. The cognitive and physical measures, while well validated, are relatively coarse, and the self-reported beliefs capture only a slice of a person's outlook. Still, the size of the sample, the length of the follow-up and the consistency with Levy's prior experiments make the pattern hard to dismiss. The authors are careful to say the finding adds to our picture of ageing rather than rewriting it wholesale.

## Why It Matters for the Diaspora

For Indian-origin families scattered across the United States, Britain, Canada and beyond, this research lands close to home \u2014 often literally, in the spare bedroom where an ageing parent lives, or on the weekly video call to grandparents back in India. Diaspora households frequently carry a deep reverence for elders alongside a quiet fatalism about their decline: the assumption that once a parent crosses a certain age, the only direction is down, and the role of the family is to manage that descent gently.

This study argues for a different posture. It suggests that older relatives are not closed books but people still capable of gaining ground \u2014 sharper, steadier, happier \u2014 and that how the family frames ageing may itself be part of the medicine. Encouraging an elderly parent to keep walking, to keep learning, to stay socially and mentally engaged, and gently pushing back on the belief that decline is inevitable, may do more than offer comfort. For a community that places the care of its elders near the centre of its values, the science offers a hopeful instruction: expect more, not less, of old age."""
})

# ============================================================
# ARTICLE 2: Subjective age & sleep (lifestyle-health)
# ============================================================
articles.append({
    "headline": "One Question \u2014 'How Old Do You Feel?' \u2014 May Reveal Whether You're Sleeping Well Enough",
    "subheadline": "A new study of more than 3,100 adults finds that people who feel older than their actual age tend to sleep worse, pointing to a single, disarmingly simple cue that something may be off with your rest.",
    "slug": "subjective-age-feeling-older-poor-sleep-quality-national-sleep-foundation-journal-sleep-3100-adults-diaspora-20260624-1800",
    "category": "lifestyle-health",
    "vertical": "sleep-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Sleep is the quiet casualty of immigrant life \u2014 long commutes, late shifts, calls timed to family in India, and the grind of building a life in a new country all erode it; this research hands the diaspora a free, instant self-check on whether that chronic rest deficit is catching up with them.",
    "sources": json.dumps([
        {"name": "Fox News \u2014 'This one question may reveal whether your body is getting the rest it needs, study finds' (National Sleep Foundation, journal Sleep)", "url": "https://www.foxnews.com/health/this-one-question-may-reveal-whether-your-body-getting-rest-it-needs-study-finds"},
        {"name": "New York Post \u2014 'One question may reveal whether your body is getting the rest it needs, study finds'", "url": "https://nypost.com/"},
        {"name": "Balter LJT & Axelsson J, Proc Biol Sci (Royal Society B), 2024 \u2014 'Sleep and subjective age: protect your sleep if you want to feel young' (DOI: 10.1098/rspb.2024.0171)", "url": "https://pubmed.ncbi.nlm.nih.gov/38531399/"}
    ]),
    "body": """We track our sleep with rings, watches and apps that spit out scores and graphs. A new study suggests one of the most revealing measures may be far simpler, and entirely free: just ask yourself how old you feel. People who feel older than their birthdays say they are, researchers have found, tend to be the ones sleeping worst.

## The Study

The research, led by scientists at the National Sleep Foundation and published in the journal Sleep, involved more than 3,100 adults. The method was almost startlingly plain. Participants were asked a single question \u2014 "How old do you feel?" \u2014 and their answers were compared against detailed measures of sleep quality, sleep consistency and how well they functioned during the day.

The pattern was clear and consistent. People who reported feeling older than their chronological age also reported worse sleep across the board: more insomnia symptoms, more irregular sleep patterns, and more daytime fatigue. They were also more likely to rate their overall physical health as poor. The gap between how old you are and how old you feel, in short, appears to be a quiet readout of how rested your body actually is.

## Why "Subjective Age" Matters

The idea has a robust scientific lineage. A 2024 study from Sweden's Karolinska Institutet, published in the Proceedings of the Royal Society B, put the relationship to a direct test. In a controlled experiment, just two nights of restricted sleep \u2014 four hours in bed \u2014 made people feel an average of 4.4 years older than they did after nights of plentiful rest. The same study found that moving from feeling fully alert to feeling extremely sleepy was associated with feeling a full decade older. A separate population study from South Korea found that adults who felt older than their age had measurably poorer sleep quality, an association strongest in women and in middle-aged and older adults.

The mechanism is intuitive. Poor sleep leaves people foggy, irritable, low on energy and slow to recover \u2014 exactly the constellation of feelings we associate with growing old. "I've worked with many people who come in saying they feel older than they are. They're exhausted, mentally foggy, less patient, less motivated," said Jonathan Alpert, a psychotherapist not involved in the study. "Poor sleep is often a major part of the picture."

## A Useful Self-Check, Not a Diagnosis

The appeal of the finding is its practicality. Most people will never undergo a formal sleep study, but everyone can pause and ask how old they feel relative to their actual age. A persistent sense of feeling older, the researchers suggest, is worth treating as a prompt \u2014 a nudge to look honestly at sleep habits before chalking fatigue up to age itself.

The caveats matter. This is largely cross-sectional, correlational work; feeling older and sleeping poorly travel together, but the studies cannot fully untangle which drives which, and other factors \u2014 depression, anxiety, chronic illness \u2014 feed into both. Feeling older is a signal to investigate, not a diagnosis, and genuine sleep disorders need proper medical assessment. Still, as a free, instant gut-check, the question is hard to beat.

## Why It Matters for the Diaspora

For the Indian diaspora, sleep is often the first thing sacrificed and the last thing acknowledged. The texture of immigrant and NRI life conspires against rest: long commutes and longer work hours, shift work in healthcare and hospitality, the pull of family obligations, and the peculiar tax of living several time zones from loved ones \u2014 the late-night and early-morning calls to parents in India, the festivals and cricket matches watched at odd hours, the weddings attended over video at 3 a.m. local time. Add the cultural tendency to wear exhaustion as a badge of hard work and devotion, and chronic sleep debt can become invisible, simply the price of building a life abroad.

This research offers the community a small, powerful tool that costs nothing and needs no device. The next time a long stretch leaves you feeling far older than your years, treat it not as proof that age is catching up, but as a question worth asking about your sleep. Protecting rest \u2014 a consistent bedtime, a wind-down free of screens, guarding the hours around it \u2014 may be one of the simplest ways to feel, and very likely to be, younger."""
})

# ============================================================
# ARTICLE 3: GIFT City new route to global markets (markets-finance)
# ============================================================
articles.append({
    "headline": "India Opens a New Door to the World's Markets \u2014 and It Runs Through GIFT City",
    "subheadline": "A wave of new funds is letting Indians invest in US stocks and global assets through the country's tax-neutral financial hub, with the fund itself shouldering the tax \u2014 but the fine print on remittance limits and levies still rewards a careful reading.",
    "slug": "gift-city-new-route-global-markets-us-stocks-fund-level-tax-lrs-tcs-nri-investor-20260624-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GIFT City is being built explicitly to court the diaspora's capital, and for NRIs weighing how to hold global assets with an Indian foot, the new IFSC funds change the calculus on tax, repatriation and paperwork \u2014 exactly the friction points that have long made cross-border investing a headache.",
    "sources": json.dumps([
        {"name": "Value Research \u2014 'Indians get a new route to the world's markets via GIFT City'", "url": "https://www.valueresearchonline.com/stories/"},
        {"name": "Mint \u2014 'Buying US stocks via GIFT City? Here's how capital gains and dividend tax work'", "url": "https://www.livemint.com/money/personal-finance"},
        {"name": "Mondaq \u2014 'GIFT City: India's Tax And Repatriation Revolution For Global Capital: A 2026 Perspective'", "url": "https://www.mondaq.com/"}
    ]),
    "body": """For most of its history, India's financial system has pointed inward. Strict caps on how much money individuals can send abroad, punishing tax rates on foreign income, and a thicket of compliance forms have made it genuinely hard for Indians to own a slice of the world's markets. A new generation of funds based in Gujarat International Finance Tec-City \u2014 GIFT City, India's tax-neutral financial enclave \u2014 is trying to change that, and the structure they use is novel enough to be worth understanding before the marketing gloss sets in.

## What GIFT City Funds Are

GIFT City is an International Financial Services Centre, a zone that operates under offshore-style rules even though it sits on Indian soil. The new vehicles launching there are retail funds that behave, on the surface, much like ordinary mutual funds: an investor puts in money, the fund buys a portfolio of global assets \u2014 US stocks, ETFs, international themes \u2014 and the investor redeems units later. Fund houses including PPFAS and DSP are among those building products for the platform, with minimum tickets pitched around 5,000 dollars to keep them within reach of a broad base of investors.

## The Big Difference: Tax at the Fund Level

The most important structural departure is how tax works. In a normal arrangement, each investor calculates and pays capital-gains tax on foreign assets themselves \u2014 an annual chore that, for direct holders of US shares, can mean wrestling with multiple jurisdictions. In the GIFT City structure, the fund itself is the taxpayer.

"The taxation is at the fund level," as one fund manager put it. "That means the fund will be paying taxes whenever it sells securities or receives dividends or interest, and the proceeds in the hands of investors on redemption are net of tax \u2014 effectively tax-free." In other words, the investor receives after-tax money and is spared the yearly filing headache that comes with do-it-yourself foreign investing. It is a genuine simplification \u2014 though, as managers are quick to caution, tax frameworks can change, and the benefit holds only as long as the current regime does.

## The Limits That Still Apply

The new route does not dissolve every constraint. Money invested through these funds still flows out under the Reserve Bank of India's Liberalised Remittance Scheme, which caps an individual's outbound transfers at 250,000 dollars a year. The relevant limit, in other words, is now your personal LRS headroom rather than any industry-wide ceiling.

Then there is Tax Collected at Source. Remittances above 10 lakh rupees in a financial year attract a 20 percent TCS \u2014 and crucially, that threshold is measured across all of a person's remittances in the year, not just a single transaction. The roughly 5,000-dollar minimum on many of these funds is pitched deliberately below that line so smaller investors can participate without immediately triggering the higher levy. TCS, it is worth remembering, is recoverable when you file your return; it is a cash-flow drag, not a permanent cost.

## A Hub Built to Pull Capital Home

The funds are one piece of a much larger ambition. GIFT City's IFSC has been growing fast \u2014 alternative investment fund assets there reportedly jumped around 300 percent year on year to roughly 12 billion dollars by early 2026 \u2014 as India tries to build a domestic answer to Singapore and Dubai. The pitch is explicit about its target: India's roughly 18-million-strong diaspora, which sends home some 100 billion dollars in remittances each year, and the high-net-worth residents who have long parked global ambitions offshore. By offering offshore-style tax treatment and easier repatriation on Indian ground, GIFT City is courting reverse capital flows it has historically struggled to capture.

## Why It Matters for the Diaspora

For non-resident Indians, GIFT City is not an abstraction \u2014 it is being purpose-built with them in mind. Many NRIs already navigate a frustrating split: global earnings and global investing ambitions on one side, an Indian financial footprint and Indian family ties on the other, with repatriation limits, NRO account ceilings and DTAA uncertainty grinding in between. The new IFSC funds, and the dollar-denominated products increasingly clustered in the zone, are aimed squarely at smoothing that friction.

The sensible approach is curiosity tempered by diligence. The fund-level tax model is a real convenience, and the platform's momentum is striking, but the structure is still young, the products vary, and the LRS and TCS mechanics reward anyone who reads the offer document rather than the headline. For diaspora investors weighing how to hold global assets with one foot in India, GIFT City is a development worth watching closely \u2014 and worth approaching with the same patience the seasoned money is showing."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["happy elderly couple walking outdoors", "senior adults exercise active aging", "older woman smiling park walking"],
                          ["happy senior couple walking", "active elderly people outdoors"], None),
    articles[1]["slug"]: (["woman sleeping bed peaceful rest", "person tired waking up morning bed", "bedroom sleep alarm clock"],
                          ["woman sleeping peacefully bed", "tired person bed morning"], None),
    articles[2]["slug"]: (["GIFT City Gandhinagar Gujarat towers", "Gujarat International Finance Tec City buildings", "Mumbai financial district skyline"],
                          ["modern financial district skyline india", "stock market trading screen"], None),
}
img_captions = {
    articles[0]["slug"]: "A new Yale study finds nearly half of adults over 65 improved in memory, mobility, or both \u2014 with a hopeful view of aging a key factor",
    articles[1]["slug"]: "A new study links feeling older than one's age to poorer sleep, offering a simple self-check on whether the body is getting enough rest",
    articles[2]["slug"]: "GIFT City, India's tax-neutral financial hub in Gujarat, is opening new fund routes for Indians and NRIs to invest in global markets",
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
