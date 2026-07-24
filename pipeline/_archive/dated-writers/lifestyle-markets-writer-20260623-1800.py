#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 10:00 UTC batch.
Topics (checked against last-3-day articles to avoid dupes):
  1. Hearing loss is one of the largest MODIFIABLE risk factors for dementia —
     a new All of Us analysis (16,270 adults) found severe hearing loss carried
     an odds ratio of 6.76 for dementia, and the randomized ACHIEVE-style
     hearing-aid trial (~1,000 adults 70-84) cut cognitive decline by nearly 50%
     in high-risk elders. — lifestyle-health
  2. Microplastics found inside the human eye — the first study to detect
     microplastics in the trabecular meshwork (20 glaucoma patients) tied the
     plastic burden tightly to higher intraocular pressure, hinting at a new,
     under-recognised pathway in glaucoma. — lifestyle-health
  3. Indian IT stocks slump after Accenture trims its FY26 revenue guidance to
     3-4%; brokerages warn FY27 for Indian IT could be weaker than the Street
     expects as AI and cautious client spending cloud the outlook. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000z.bin"):
            with open("/tmp/_img_dl1000z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000z.bin")
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
# ARTICLE 1: AQP4 gene + sleep interaction in Alzheimer's (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Why Poor Sleep Harms Some Brains More Than Others May Come Down to a Single Gene",
    "subheadline": "A new study of a brain-cleaning gene called AQP4 found that the same sleep habits can speed or slow early Alzheimer's-type changes depending on which version of the gene a person carries \u2014 a clue to why two people who sleep alike can age so differently.",
    "slug": "aqp4-gene-sleep-interaction-alzheimers-grey-matter-edith-cowan-precision-health-diaspora-20260623-1800",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Sleep is one of the few dementia risk factors anyone can actually change, and for a diaspora that often runs on jet lag, late shifts and a strong family history of dementia, the finding that a person's genes decide how much their sleep matters is a practical nudge to treat rest as preventive medicine, not a luxury.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 'Study links genes and sleep habits to Alzheimer's risk' (Edith Cowan University, Centre for Precision Health)", "url": "https://www.news-medical.net/news/20260622/Study-links-genes-and-sleep-habits-to-Alzheimers-risk.aspx"},
        {"name": "Alzheimer's & Dementia \u2014 Porter, T., et al. (2026), 'Evidence for direct and sleep-moderated relationships between aquaporin-4 genetic variants and Alzheimer's disease phenotypes' (DOI: 10.1002/alz.71516)", "url": "https://alz-journals.onlinelibrary.wiley.com/doi/10.1002/alz.71516"}
    ]),
    "body": """We have long been told that bad sleep is bad for the brain. A new study from Australia adds a twist that makes the advice both more personal and more urgent: how much your sleep matters for your brain may depend on a single gene you were born with. The same restless nights that leave one person's brain largely untouched may be quietly accelerating decline in another \u2014 and the difference comes down to the genetic machinery the brain uses to clean itself overnight.

## A Gene That Helps the Brain Take Out the Trash

The research, from the Centre for Precision Health at Edith Cowan University in Perth, focused on a gene called aquaporin-4, or AQP4. It is not a household name, but its job is fundamental. AQP4 helps control the movement of fluid through the brain, and that flow powers what scientists call the glymphatic system \u2014 in effect, the brain's built-in waste-disposal network. This clean-up runs most actively while we sleep, washing away metabolic debris including the amyloid and tau proteins that build up in Alzheimer's disease.

That is why sleep and dementia have always seemed linked: skimp on sleep, and the brain has less time to take out its own trash. What the new work shows is that the efficiency of that clean-up is not the same for everyone. It is tuned, in part, by which version of the AQP4 gene a person inherits.

## What the Study Found

The team examined 13 common variants of the AQP4 gene and matched them against participants' self-reported sleep patterns, brain scans and cognitive tests. The interaction was striking. For people carrying certain variants, shorter sleep duration was tied to faster loss of grey matter \u2014 the tissue packed with the brain's working cells. Others, who reported taking longer to fall asleep, showed structural changes associated with reduced brain volume. And crucially, the direction of the effect flipped depending on the variant a person carried.

"Our study shows that individuals carrying certain AQP4 variants showed faster grey matter loss when they reported shorter sleep," said Dr. Ayeisha Milligan Armstrong, who worked on the research. "It's not just which genes you carry \u2014 it's how those genes interact with the world around you. The same variant can look protective or detrimental depending on how someone is sleeping. That's important, because sleep is one of the few modifiable factors people can actually act on."

The findings, published in the journal Alzheimer's & Dementia, also showed that the way cognitive performance changed over time differed between people with sleep disturbances, again according to their genetic make-up.

## A Step Toward Personalized Prevention

The researchers are careful about how far to push the result. "We've known for a while that poor sleep and Alzheimer's risk are linked," said Dr. Tenielle Porter. "What this shows is that rather than assuming everyone at risk follows the same pathway, a more targeted and personalised approach to Alzheimer's prevention may be needed. But we're not at the point of recommending genetic testing; our findings need replication in larger and more diverse cohorts."

That caution matters. The sleep data was self-reported, the study captures associations rather than proof of cause, and the cohort needs to be repeated in larger and more varied populations before anyone starts ordering AQP4 gene tests. The authors call instead for genetics-informed clinical trials \u2014 studies that would test whether deliberately improving sleep can offset inherited risk and change long-term brain outcomes.

"This moves us closer to understanding why some people decline faster than others, even when they have similar risk on paper," said Professor Simon Laws, the centre's director. "Identifying who is most vulnerable, and who is most likely to benefit from a particular lifestyle intervention, is where precision health needs to go."

## Why It Matters for the Diaspora

For now, no one can hand you your AQP4 profile, and that is rather the point: when you cannot know whether you drew the protective card or the vulnerable one, the safe assumption is that your sleep counts. That message lands with particular force in diaspora life, which is often structured against good rest \u2014 the night shifts of medicine and IT, the perpetual jet lag of long-haul visits home, the late video calls timed to a relative twelve hours away, the screen-lit insomnia of a demanding job in a new country.

Dementia also looms large in many Indian families' health histories, and South Asians face rising rates of the diabetes and vascular disease that compound the risk. The study reframes a familiar piece of advice into something more pointed: protecting sleep is not about feeling rested tomorrow, but about giving the brain the nightly window it needs to clear the very proteins that drive Alzheimer's \u2014 and for some people, that window may be doing far more work than they realise. Keeping a regular sleep schedule, treating conditions such as sleep apnoea that fracture the night, and guarding rest as carefully as diet or exercise is advice that costs nothing and, for an unlucky genetic few, could matter enormously."""
})

# ============================================================
# ARTICLE 2: Global heat-stress intensification (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Dangerous Heat Now Reaches More of the World \u2014 and the Nights Are No Longer a Refuge",
    "subheadline": "A new analysis finds the share of the planet exposed to severe heat stress climbed from 16% to 22% over fifty years, with brutal heat spreading into regions that never knew it and \u2018tropical nights\u2019 stripping away the body's chance to cool down and recover.",
    "slug": "global-heat-stress-intensification-tropical-nights-nature-climate-change-health-diaspora-20260623-1800",
    "category": "lifestyle-health",
    "vertical": "public-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Heat is a health story that bridges the diaspora's two worlds at once \u2014 family in Indian cities enduring some of the planet's most punishing summers, and relatives in the UK, North America and Scandinavia now facing heat their homes were never built for, making this a rare risk that touches both ends of the migration journey.",
    "sources": json.dumps([
        {"name": "Phys.org / AFP \u2014 'Heat stress exposure climbed from 16% to 22% worldwide over 50 years, study shows'", "url": "https://phys.org/news/2026-06-stress-exposure-climbed-worldwide-years.html"},
        {"name": "Nature Climate Change \u2014 Emerton, R., et al. (2026), 'Global heat stress intensification and its expanding footprint on the human population' (DOI: 10.1038/s41558-026-02670-5)", "url": "https://www.nature.com/articles/s41558-026-02670-5"}
    ]),
    "body": """Heat is no longer a problem confined to the places that have always been hot. A sweeping new study finds that dangerous heat stress has expanded its footprint across the planet over the past half-century \u2014 reaching into regions that historically never experienced it, and, just as worryingly, robbing people of the cool nights their bodies rely on to recover. For a diaspora rooted in some of the hottest countries on earth and scattered across some of the fastest-warming ones, it is a health warning that follows the family wherever it lives.

## What the Study Measured

Publishing in the journal Nature Climate Change, researchers led by Rebecca Emerton looked not at temperature alone but at heat stress \u2014 a more complete measure of what the human body actually endures, combining heat with humidity, wind and other factors into a "feels-like" reading. By that measure, the share of the global population exposed to strong heat stress rose from about 16 percent to 22 percent over the fifty years the study examined.

That six-point jump sounds modest until it is translated into people. It means hundreds of millions more human beings are now routinely subjected to conditions the body struggles to cope with \u2014 the kind of heat that overloads the heart, thickens the blood, strains the kidneys and turns ordinary outdoor work into a hazard.

## Heat Is Spreading Into New Territory

Perhaps the most unsettling finding is geographic. Severe heat stress is "expanding into areas of the globe where historically it's not been experienced," Emerton said. Very strong heat stress, defined as a feels-like temperature of at least 38 degrees Celsius, has now reached parts of North America, the United Kingdom and even Scandinavia \u2014 places whose homes, hospitals, workplaces and habits were simply never designed around it.

This is a crucial point about why heat kills. Much of the danger comes not from the absolute temperature but from a lack of preparation: no air conditioning, buildings built to trap warmth, populations with no cultural memory of how to behave in a heatwave. A temperature that would pass as an ordinary summer day in Chennai can become a mass-casualty event in a northern European city caught off guard.

## The Vanishing Cool of Night

The study also tracked a quieter, more insidious trend: the rise of relentlessly hot nights. The researchers documented a global increase in "tropical nights," when the feels-like temperature never drops below 20 degrees Celsius.

The night matters more than most people appreciate. The body uses the cooler hours of darkness to shed the heat it accumulated during the day, easing the strain on the heart and allowing real, restorative sleep. "When you can't get any relief, and your body can't cool down, that becomes very dangerous for people's health, particularly for vulnerable people," Emerton said. Without that nightly reprieve, heat stress compounds day after day, and the toll falls hardest on the elderly, the very young, the ill, and those working or living without cooling.

The analysis ran only through 2024, but Emerton noted that the punishing heatwaves already striking Europe this year suggest the trend has not let up.

## Why It Matters for the Diaspora

Few communities straddle this story as completely as the Indian diaspora. On one side are family members in India, where cities regularly endure some of the most extreme and humid heat on the planet, and where hot nights in dense urban neighbourhoods can be deadly. On the other are relatives who have settled in Britain, Canada, the northern United States and beyond \u2014 places now being blindsided by heat their infrastructure was never built to handle, where a flat with no air conditioning can become a trap during a heatwave.

The practical lessons cut across both. For elderly parents anywhere, a heatwave is a medical event, not just discomfort: hydration, shade, cooling and a genuinely cool place to sleep can be the difference between recovery and a hospital visit. Chronic conditions common in the community, from heart disease to diabetes and kidney problems, all raise the danger. And the loss of cool nights argues for taking sleep environment seriously \u2014 a fan, a cooler room, a cold shower before bed \u2014 wherever the family happens to be. The study's larger message is that heat is no longer someone else's climate; it is a health risk arriving on doorsteps that never expected it."""
})

# ============================================================
# ARTICLE 3: Reliance AGM 2026 growth blueprint (markets-finance)
# ============================================================
articles.append({
    "headline": "Reliance Lays Out a Five-Year Plan to Double Its Earnings \u2014 With AI and the Sun at the Centre",
    "subheadline": "At its 49th AGM, Mukesh Ambani's conglomerate paired a record-profit year with bold targets: doubling consolidated EBITDA, a \u20b91-trillion FMCG business, an AI push across every product, and 200,000 green-energy jobs \u2014 even as the stock trades well below its peak.",
    "slug": "reliance-agm-2026-double-ebitda-ai-new-energy-fmcg-record-profit-nri-investor-20260623-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Reliance is the single heaviest weight in the Sensex and Nifty that anchor most NRI India portfolios and mutual-fund SIPs, so its five-year bet on AI, consumer brands and solar energy is, in effect, a bet on the direction of the entire market the diaspora invests in \u2014 and a preview of where India's economy is trying to go.",
    "sources": json.dumps([
        {"name": "Outlook Business \u2014 'Reliance Shares Rally 3% as Mukesh Ambani Confirms Jio IPO Filing, Targets Doubling EBITDA and \u20b91 Trillion FMCG Revenue'", "url": "https://www.outlookbusiness.com/"},
        {"name": "Trade Brains \u2014 'Reliance AGM 2026: Record Profit, Jio IPO Approval, Green Energy Expansion and more'", "url": "https://tradebrains.in/"},
        {"name": "The Wall Street Journal \u2014 'Reliance's Jio Platforms to Seek India Listing'", "url": "https://www.wsj.com/"}
    ]),
    "body": """When Mukesh Ambani stood before shareholders at Reliance Industries' 49th annual general meeting, the mood music had changed. For years, the conglomerate's investment case rested on its willingness to spend big and build platforms ahead of the market. This year, with the stock languishing well below its peak, investors wanted something different \u2014 proof that all that spending will turn into earnings. Ambani's answer was a five-year blueprint built around two ideas: artificial intelligence woven through everything the company touches, and energy built, as his son put it, "on Indian sunshine."

## A Record Year, and a Demand for More

The backdrop was strong. Reliance reported a record financial performance for FY26, with revenue of roughly \u20b911.76 lakh crore, up nearly 10 percent year on year, and net profit climbing about 18 percent to \u20b995,754 crore. EBITDA \u2014 a measure of core operating profit \u2014 reached around \u20b92.08 lakh crore. By almost any yardstick, it was a good year for a company that spans oil refining, petrochemicals, telecom, retail and clean energy.

Yet the share price told a more sceptical story. Over the prior six months the stock had fallen about 15 percent, against a 10 percent decline in the Sensex, and it trades at a meaningful discount to its 52-week high. The market, in other words, has been waiting for the payoff. The AGM was Ambani's attempt to spell out exactly when and how it arrives.

## The Headline Targets

The boldest promise was financial: Reliance aims to double its consolidated EBITDA over the next five years. For a company already earning more than \u20b92 lakh crore at that level, doubling it is an enormous undertaking that would reshape India's corporate landscape.

The growth is meant to come from several engines at once. The consumer business was given a hard number \u2014 a target of \u20b91 trillion in gross revenue for its fast-moving consumer goods arm by FY30, a direct challenge to the entrenched giants of Indian retail. The much-anticipated listing of Jio Platforms moved from promise to process, with the board approving the draft red herring prospectus and filing it with the market regulator SEBI; the offering involves issuing up to 270 million new shares, and brokerages have pegged Jio's value at around $180 billion, which would make it one of the largest IPOs in Indian history.

## AI Everywhere, and a Bet on the Sun

Two strategic themes ran through the meeting. The first was artificial intelligence. Ambani announced plans to embed AI across all of Reliance's consumer and enterprise products, building an ecosystem that leans on the company's vast telecom network, data infrastructure and enormous customer base. The pitch to investors is that Jio should be seen not as a telecom operator but as a digital and AI platform capable of commanding a premium valuation.

The second was clean energy, and here the rhetoric was at its most ambitious. The company said its New Energy business \u2014 anchored by its Giga Complex and the Kutch solar farm \u2014 would create some 200,000 green jobs. "The world built its old energy on Middle Eastern oil. The world will now build its new energy on Indian sunshine," Anant Ambani told the meeting, framing the shift as not just an energy story but a geopolitical and economic one for a country that has long sent dollars abroad to buy crude.

## The Reasons for Caution

Investors have heard grand visions from Reliance before, and the market's muted reaction reflects a focus that has shifted from announcements to execution \u2014 cash flows, monetisation and value unlocking. Doubling EBITDA in five years is a steep climb; the FMCG and AI ambitions face fierce, well-funded competition; and the Jio IPO, while filed, still depends on regulatory approvals and on equity-market conditions that have been subdued all year, with the Sensex down nearly 10 percent in 2026. Promises are not profits, and the company now has to deliver against its own numbers.

## Why It Matters for the Diaspora

For NRI investors, Reliance is not just another stock \u2014 it is one of the largest single constituents of the Sensex and Nifty, the indices that sit at the core of most India-focused mutual funds, ETFs and SIPs that the diaspora uses to stay invested back home. When Reliance sets a five-year direction, it is effectively steering a large slice of the market the diaspora owns.

The blueprint is also a window into where India's economy is trying to head: toward homegrown AI, branded consumer goods for a rising middle class, and a pivot from imported oil to domestic solar power. Each of those themes carries implications for inflation, the trade balance and the rupee that shape the value of money sent home. The Jio listing, when it comes, could become a marquee opportunity for diaspora investors hunting exposure to India's digital economy. The sensible posture is the same one the wider market has adopted: take the ambition seriously, but watch the execution \u2014 because for once, Reliance has put hard targets on the table against which it can be judged."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["person sleeping bed night rest", "elderly person sleeping peacefully", "human brain MRI scan neurology"],
                          ["person sleeping peacefully bedroom", "senior adult sleeping rest"], None),
    articles[1]["slug"]: (["heat wave city sun summer", "people fanning extreme heat", "sun haze hot weather urban"],
                          ["extreme heat wave city summer", "hot sun heatwave people"], None),
    articles[2]["slug"]: (["Mukesh Ambani", "Reliance Industries headquarters Mumbai", "solar power plant India energy"],
                          ["solar power plant panels", "corporate skyscraper business"], "Mukesh Ambani"),
}
img_captions = {
    articles[0]["slug"]: "Researchers found a brain-cleaning gene called AQP4 shapes how strongly sleep affects early Alzheimer's-type changes",
    articles[1]["slug"]: "A new study finds severe heat stress now reaches 22% of the world's population, up from 16% five decades ago",
    articles[2]["slug"]: "Mukesh Ambani used Reliance's 49th AGM to set a five-year target of doubling the conglomerate's core earnings",
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
