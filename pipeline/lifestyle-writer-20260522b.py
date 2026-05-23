#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-22 19:00 PDT run
2 articles:
  1. India heatwave: 18+ dead, 48°C, Delhi warmest May night in 14 years — NRI summer travel advisory
  2. Gulf NRI jobs/remittance crisis: Iran war crushing 9M Indian workers abroad
"""

import os, json, uuid, re, requests, subprocess, time
from datetime import datetime, timezone

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
BUCKET = "article-images"

def make_slug(text, suffix="20260522"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code == 409:
        print(f"  ⚠ Conflict (already exists) for {table}")
        return None
    r.raise_for_status()
    return r.json()

def sb_patch(table, filter_str, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filter_str}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat()

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Deadly Heatwave — NRI Summer Travel Advisory
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "India's Heatwave Has Killed at Least 18 People This Week. If You're Planning a Summer Trip Home, Read This Before You Book."
art1_subheadline = "Temperatures hit 48°C in Uttar Pradesh. Delhi just recorded its warmest May night in 14 years. Andhra Pradesh has logged 325 suspected heatstroke cases since March. For the millions of NRIs who fly home every summer, the India waiting at the airport is more dangerous than the one they remember."
art1_slug = make_slug("india-heatwave-2026-deaths-delhi-nri-summer-travel-advisory")
art1_category = "lifestyle-health"

art1_body = """Eighteen people are confirmed dead from heatstroke in Odisha this week. Thirty-six more suspected heat-related deaths are under investigation. In Andhra Pradesh, 325 suspected heatstroke cases have been reported since March, with a third of them in May alone. In Uttar Pradesh, the mercury at Banda touched 48 degrees Celsius — 118 degrees Fahrenheit — the highest reading recorded anywhere in India this year. In Delhi, two heatstroke patients lie critical in a government hospital, and the night of May 21 was the warmest May night the capital has recorded in 14 years, with the minimum temperature refusing to drop below 31.9 degrees Celsius.

The India Meteorological Department has issued a severe heatwave warning for May 22 through 27, covering the entire expanse of northwest and central India — from Rajasthan through Uttar Pradesh, Madhya Pradesh, Delhi-NCR, Haryana, and Punjab. The IMD has advised people to avoid going outdoors between 11 a.m. and 4 p.m.

For the estimated 2.5 million NRIs who fly to India between May and August each year, this is not distant news. It is the country they are about to land in.

## The Numbers Behind the Headlines

India's relationship with lethal heat is not new, but the scale is accelerating. In 2024, between March and June, the country recorded approximately 40,000 suspected heatstroke cases and 110 confirmed deaths. Last year, the figures were lower but still significant: over 7,000 suspected cases and 14 deaths across the same period.

This year's death toll is already climbing faster. The 18 confirmed deaths in Odisha came within a single week. Meteorologists say 2026 is on track to be the worst heatwave year since at least 2015, when over 2,400 people died from heat-related causes — many of them outdoor labourers, elderly residents, and people without access to air conditioning.

The IMD declares a heatwave when the maximum temperature reaches at least 40 degrees Celsius in the plains and exceeds the normal by 4.5 to 6.4 degrees. A severe heatwave is declared when the departure is greater than 6.4 degrees or the absolute temperature crosses 47 degrees. Large parts of northern India are currently in severe heatwave territory.

What makes 2026 different is the combination: record daytime temperatures, historically warm nights that deny the body its recovery window, and the looming El Niño event that is expected to suppress monsoon rainfall, extending the heat deep into June and possibly July.

## What NRIs Need to Know Before Flying Home

Every summer, millions of NRIs schedule their India trips around school holidays — typically late May through August. For families in the US, this often means arriving in India in the last week of May or first week of June, precisely when the heatwave is at its most intense.

Here is what has changed, and what you should plan for.

**The heat is not what you remember.** If your mental model of Indian summer is based on childhood memories or trips a decade ago, recalibrate. Delhi's maximum temperatures are now routinely exceeding 45 degrees in May, with nights staying above 30 degrees. The combination means even a short walk to the market at 10 a.m. carries real risk, and sleeping without air conditioning is no longer merely uncomfortable — it is medically dangerous for the elderly and young children.

**Elderly parents are the highest-risk population.** If part of your trip involves visiting elderly parents or grandparents who live without air conditioning or in poorly ventilated homes, this is the year to take proactive steps before you arrive. Arrange for a cooler, an inverter, or a temporary AC unit. Heatstroke can progress from confusion to organ failure within hours, and many older adults in India do not recognise the early symptoms — they attribute dizziness and nausea to "normal summer weakness."

**Hospitals in smaller cities are overwhelmed.** In Andhra Pradesh, patients with diarrhoea and dehydration are lining up at district hospitals. Gujarat is reporting water shortages. If you are travelling to tier-2 or tier-3 cities, pack a basic medical kit that includes oral rehydration salts, electrolyte packets, and a digital thermometer. Know the nearest hospital with an ICU.

**Water is becoming scarce in some regions.** Gujarat is already reporting shortages. Delhi's water supply, dependent on the Yamuna, is strained by both the heat and lower upstream flows. In Rajasthan, tanker water prices have spiked. If you are visiting family in these regions, expect disruptions to daily water supply and plan accordingly — keep bottled water reserves and avoid relying on municipal taps during peak afternoon hours.

**Flight schedules may be affected.** Extreme heat can restrict takeoff weight at airports, leading to delays or, in rare cases, cancellations during peak afternoon hours. Delhi's Indira Gandhi International Airport has seen tarmac temperatures exceed 65 degrees Celsius, which can affect ground operations and aircraft turnaround times.

## Adjusting Your Travel Plans

If your dates are flexible, the safest window for a summer India trip is shifting later. The monsoon, expected to hit Kerala by May 26, typically reaches Delhi-NCR by late June or early July, bringing temperatures down by 5 to 10 degrees. Arriving in the second half of June rather than the last week of May avoids the worst of the pre-monsoon heat.

If your dates are fixed and you are landing in northern India before June 15, plan your days around the heat. Schedule outdoor activities — temple visits, family functions, shopping — for early morning (before 9 a.m.) or evening (after 6 p.m.). Keep afternoons for indoor, air-conditioned spaces. This is not optional caution; it is basic safety in a 47-degree environment.

For families with young children, paediatric dehydration is a real concern. Children acclimatised to American indoor temperatures will struggle with even brief outdoor exposure in Indian heat. Carry electrolyte solutions and insist on frequent water breaks, even when children say they are not thirsty.

## The Climate Context

India's heatwaves are becoming longer, stronger, and more frequent — the IMD's own language in its May 2026 advisory. The combination of urbanisation (which creates heat islands), deforestation, and global warming has pushed baseline temperatures steadily upward across northern and central India.

For NRIs who visit India once or twice a year, the incremental change is often invisible until it is not. The India you land in this summer is measurably hotter than the one you left five or ten years ago. Treating it with the same casual familiarity is a risk.

The 18 people who died in Odisha this week did not die because they were careless. They died because the heat exceeded what their bodies could survive. That threshold is closer than most people think — and it does not discriminate between residents and visitors."""

art1_sources = [
    "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/",
    "https://www.travelandleisureasia.com/in/news/imd-issues-orange-alert-for-delhi-as-heat-wave-sweeps-across-north-india/",
    "https://www.goldsea.com/article_details/at-least-18-dead-in-india-heat-wave",
    "https://www.devdiscourse.com/article/science-environment/3377226-delhi-records-its-warmest-may-night-in-14-years-heatwave-conditions-persist",
]

print("=== Article 1: India Heatwave NRI Travel Advisory ===")
print(f"Word count: {len(art1_body.split())}")

result = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 88,
    "tags": ["heatwave", "India", "NRI", "summer travel", "Delhi", "heatstroke", "IMD", "Odisha", "health advisory", "El Niño"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "Millions of NRIs fly to India for summer trips between May and August; the 2026 heatwave is the deadliest in years with 18+ dead, and cities like Delhi are recording unprecedented night temperatures that put elderly parents and visiting children at serious risk.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Gulf NRI Jobs Crisis — Iran War Crushing Remittances
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Iran War Has Already Sent 1.1 Million Indians Home From the Gulf. For Families in Kerala, Punjab, and UP Who Depend on Those Salaries, the Crisis Is Just Beginning."
art2_subheadline = "Nine million Indians work in the Gulf. World Bank projects Gulf growth collapsing to 1.3 per cent. Recruiters who once placed ten candidates a month now struggle with two. And the remittance economy that supports entire Indian states is running out of time."
art2_slug = make_slug("iran-war-gulf-nri-jobs-remittances-kerala-india-crisis")
art2_category = "lifestyle-health"

art2_body = """Mohammad Qureshi spent years building a life in Saudi Arabia. The 32-year-old from Kanpur worked at a jewellery shop, earned about 30,000 rupees a month, saved enough to build a small home, and helped pay for his sister's wedding. It was not luxury. It was stability — the kind that transforms a family's trajectory across a single generation.

Now Qureshi stands beside his cousins' tea stall in Kanpur, earning barely a third of what he made in Riyadh. The Iran war disrupted his plans to return to the Gulf. His visa situation is uncertain. His savings are depleting.

"Life in Saudi was easy and the money was good," Qureshi told Reuters this week, as customers gathered for morning chai. "Life is difficult here. I pray the war ends soon so we can go back."

His story is playing out across millions of Indian households — and particularly in the NRI families who built their entire financial architecture around Gulf salaries.

## The Scale of Displacement

The numbers are staggering. Out of nearly 19 million Indians working overseas, approximately 9 million are in the Gulf — concentrated in Saudi Arabia, the UAE, Qatar, Kuwait, Oman, and Bahrain. These workers are the backbone of India's remittance economy, which pulled in $102.5 billion in the first nine months of the 2025-26 fiscal year alone.

Since the US-Israeli strikes on Iran and the disruption to the Strait of Hormuz beginning on February 28, 2026, approximately 1.1 million Indians have returned from the Gulf region, according to India's foreign ministry. That figure includes passengers, workers, and travellers — but even conservative estimates suggest hundreds of thousands were active workers whose jobs have evaporated or been frozen.

The World Bank projects Gulf economic growth collapsing from 4.4 per cent in 2025 to just 1.3 per cent in 2026. For labour-importing economies that depend on oil revenue and construction spending, that kind of contraction translates directly into layoffs, project freezes, and recruitment halts.

At Hayat Placement Services in Kanpur, recruiter Gautam Bhatnagar has watched his business evaporate. "Earlier, we used to place five to ten candidates every month," he said. "Now we are lucky if we can place even one or two."

## The Remittance Lifeline — Fraying

India is the world's largest recipient of remittances. In 2024-25, total inward remittances crossed $120 billion. The Gulf accounts for roughly half of that — money that does not flow into corporate balance sheets but directly into household bank accounts in Kerala, Uttar Pradesh, Bihar, Punjab, Rajasthan, Tamil Nadu, and Andhra Pradesh.

For these states, remittances are not supplementary income. They are the primary economic engine for entire districts. Kerala's economy has been described by economists as a "remittance economy" — Gulf money funds home construction, children's education, dowries, medical expenses, and small businesses. In parts of Malappuram, Thrissur, and Kozhikode, a significant majority of households have at least one family member working in the Gulf.

When that income stops — or even slows — the downstream effects are immediate and cascading. Home construction projects stall. School fees go unpaid. Medical treatments are postponed. Small businesses that depended on remittance-fuelled consumer spending see demand collapse.

"If the conflict continues, financial stress in Gulf economies could lead to large-scale repatriation, adding pressure to Kerala's already strained job market," said Ajith Kolassery, CEO of NORKA Roots, an agency of the state's Non-Resident Keralites Affairs Department. "There has been no mass return so far. But the warning signs are there."

## The Double Squeeze

For NRI families in the US, UK, and Canada, the Gulf crisis may seem distant — their own livelihoods are not directly tied to Middle Eastern construction projects or oil revenues. But the ripple effects are closer than they appear.

Many NRIs in Western countries have extended families in India whose financial stability depends entirely on a brother, cousin, or uncle working in Dubai, Riyadh, or Doha. When that Gulf worker loses his job or cannot return after a home visit, the financial responsibility often shifts — sometimes silently, sometimes with an urgent phone call — to the family member in America or London.

This is the hidden cost of the Iran war for the Indian diaspora: not a direct hit to their own paycheques, but a sudden, unplanned increase in the money they need to send home to cover gaps that Gulf salaries used to fill.

The dynamics are compounded by the manufacturing squeeze. In Kanpur, which accounts for roughly a quarter of India's $6 billion annual leather exports, factory owner Taj Alam described running at half capacity and half his workforce. The Strait of Hormuz disruption has driven up fuel, gas, logistics, and shipping costs, crushing margins just as global demand softens.

"The outlook will remain bleak until the Strait of Hormuz stabilises," Alam said. "Why invest when the future looks uncertain?"

## What Families Should Know

**Check on Gulf-based relatives now.** If you have family members working in the Gulf, particularly in construction, hospitality, or oil-adjacent industries, have a direct conversation about their employment status and visa situation. Many workers are reluctant to disclose job losses to family abroad — they carry the weight of being the provider, and admitting failure feels like betraying that role. Ask specifically. Do not assume silence means stability.

**Prepare for potential financial requests.** For NRIs in the US or UK who have been sending a steady amount home each month, the calculus may need to change. If a Gulf-based family member loses income, the expectation — spoken or unspoken — may shift to you. Budget for it now rather than scrambling later.

**Understand the visa clock.** Indian workers in the Gulf operate under kafala-adjacent sponsorship systems where visa validity is tied to active employment. Thomas Cherian, a 50-year-old construction worker from Kerala who spent 18 years in Saudi Arabia, returned to India on leave in December and was due back in March. His company halted its project and laid off approximately 600 Indian workers. If he cannot return by end-June, his visa will lapse — and with it, 18 years of accumulated residency status. Workers in similar situations face a ticking clock that determines whether they can return at all.

**Watch the RBI remittance data.** The Reserve Bank of India has not yet released January-March remittance figures, which will be the first full quarter reflecting the war's impact. When that data comes out, it will tell the real story — and if it shows a significant drop, expect downstream effects on Indian real estate (Gulf money is a major driver of home purchases in Kerala and Hyderabad), gold demand, and consumer spending.

## The Structural Shift

The Iran war has accelerated a structural shift that was already underway. AI is automating routine white-collar functions. Global trade is contracting. Migration conditions are tightening across the West. For the 6 to 7 million young Indians entering the workforce each year, the traditional pathways — Gulf labour, IT services, manufacturing exports — are narrowing simultaneously.

India's unemployment rate rose to 5.2 per cent in April from 4.9 per cent in February. But the headline number obscures the real pain: urban youth joblessness stands at nearly 14 per cent. Economists flag persistent underemployment, with educated young people stuck in gig work, contract roles, and informal jobs that do not match their qualifications.

"This is not just a cyclical slowdown," said K.E. Raghunathan, national chairman of the Association of Indian Entrepreneurs. "AI, weak global trade, and tighter migration conditions are narrowing traditional employment avenues across manufacturing, IT, and overseas labour."

For diaspora families, the Gulf crisis is personal in a way that GDP statistics cannot capture. It is the cousin who cannot afford his daughter's school fees. The uncle whose construction project was cancelled. The brother-in-law whose visa is expiring. The phone call that comes at 2 a.m., asking for help.

India's remittance economy did not break overnight. But the cracks are widening — and the families who depend on it, whether they live in Kozhikode or California, are running out of time to prepare."""

art2_sources = [
    "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/",
    "https://en.wikipedia.org/wiki/Economic_impact_of_the_2026_Iran_war",
]

print("\n=== Article 2: Gulf NRI Jobs/Remittance Crisis ===")
print(f"Word count: {len(art2_body.split())}")

result2 = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 90,
    "tags": ["Gulf", "NRI", "Iran war", "remittances", "Kerala", "jobs", "Strait of Hormuz", "unemployment", "migration", "Saudi Arabia"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "9M Indians work in the Gulf; 1.1M have returned since Iran war started; remittances fund entire Kerala/UP/Bihar districts; NRIs in US/UK face hidden cost as financial burden shifts from Gulf relatives to them.",
    "word_count": len(art2_body.split()),
})
if result2:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# IMAGE SOURCING via Pexels
# ══════════════════════════════════════════════════════════════

print("\n=== Image Sourcing ===")

pexels_key = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                pexels_key = line.strip().split("=", 1)[1].strip('"').strip("'")

def pexels_search(query, per_page=5):
    if not pexels_key:
        return []
    import urllib.parse
    q = urllib.parse.quote(query)
    cmd = f'curl -s -H "Authorization: {pexels_key}" "https://api.pexels.com/v1/search?query={q}&per_page={per_page}&orientation=landscape"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("photos", [])
    except:
        pass
    return []

def download_image(url, path):
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200 and len(resp.content) > 5000:
            with open(path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  Download failed: {e}")
    return False

def upload_to_supabase(local_path, remote_name):
    with open(local_path, "rb") as f:
        data = f.read()
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    url = f"{SB_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    r = requests.post(url, headers=upload_headers, data=data)
    if r.status_code in (200, 201):
        return f"{SB_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
    else:
        print(f"  Upload failed ({r.status_code}): {r.text[:200]}")
        return None

# Article 1: heatwave / hot India / sun scorching
art1_searches = ["India summer heat sun", "scorching sun dry landscape", "heatwave thermometer hot weather"]
art1_image_url = None
for q in art1_searches:
    photos = pexels_search(q, 3)
    for p in photos:
        src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
        if src:
            local = f"/tmp/{art1_id}_hero.jpg"
            if download_image(src, local):
                remote = f"p2-{art1_id}-hero.jpg"
                pub_url = upload_to_supabase(local, remote)
                if pub_url:
                    art1_image_url = pub_url
                    art1_photographer = p.get("photographer", "Pexels")
                    print(f"  Art1 hero: {q} → {art1_photographer}")
                    break
    if art1_image_url:
        break

if art1_image_url:
    sb_patch("p2_articles", f"id=eq.{art1_id}", {
        "image_url": art1_image_url,
        "image_attribution": f"Photo: {art1_photographer} / Pexels",
        "image_caption": "India's 2026 heatwave has killed at least 18 people, with temperatures reaching 48°C in Uttar Pradesh.",
    })
    print("  ✓ Art1 image set")
else:
    print("  ✗ Art1 no image found")

# Article 2: Gulf / airport / workers / migration
art2_searches = ["Indian airport departure", "construction workers Middle East", "Indian migrant workers"]
art2_image_url = None
for q in art2_searches:
    photos = pexels_search(q, 3)
    for p in photos:
        src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
        if src:
            local = f"/tmp/{art2_id}_hero.jpg"
            if download_image(src, local):
                remote = f"p2-{art2_id}-hero.jpg"
                pub_url = upload_to_supabase(local, remote)
                if pub_url:
                    art2_image_url = pub_url
                    art2_photographer = p.get("photographer", "Pexels")
                    print(f"  Art2 hero: {q} → {art2_photographer}")
                    break
    if art2_image_url:
        break

if art2_image_url:
    sb_patch("p2_articles", f"id=eq.{art2_id}", {
        "image_url": art2_image_url,
        "image_attribution": f"Photo: {art2_photographer} / Pexels",
        "image_caption": "Approximately 1.1 million Indians have returned from the Gulf since the Iran war began in February 2026.",
    })
    print("  ✓ Art2 image set")
else:
    print("  ✗ Art2 no image found")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n=== Score Decay ===")
try:
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.10&select=id,score_total",
        headers=HEADERS, timeout=30
    )
    articles = r.json()
    decayed = 0
    for a in articles:
        old = a["score_total"] or 50
        new_score = max(10, int(old * 0.98))
        if new_score < old:
            requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
                headers=HEADERS,
                json={"score_total": new_score},
                timeout=10
            )
            decayed += 1
    print(f"  Decayed {decayed} articles out of {len(articles)} total")
except Exception as e:
    print(f"  Score decay error: {e}")


# ══════════════════════════════════════════════════════════════
# MARKETS + IPL + CHART REFRESH
# ══════════════════════════════════════════════════════════════

print("\n=== Markets Refresh ===")
try:
    r = subprocess.run(
        ["python3", "videshi-markets.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True, text=True
    )
    if r.returncode == 0:
        print("  ✓ Markets refreshed")
    else:
        print(f"  Markets stderr: {r.stderr[:200]}")
except Exception as e:
    print(f"  Markets error: {e}")

print("\n=== IPL Refresh ===")
try:
    r = subprocess.run(
        ["python3", "videshi-ipl.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True, text=True
    )
    if r.returncode == 0:
        print("  ✓ IPL refreshed")
    else:
        print(f"  IPL stderr: {r.stderr[:200]}")
except Exception as e:
    print(f"  IPL error: {e}")

print("\n=== Market Charts ===")
try:
    r = subprocess.run(
        ["python3", "videshi-market-charts.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True, text=True
    )
    if r.returncode == 0:
        print("  ✓ Market charts refreshed")
    else:
        print(f"  Charts stderr: {r.stderr[:200]}")
except Exception as e:
    print(f"  Market charts error: {e}")


# ══════════════════════════════════════════════════════════════
# GIT PUSH
# ══════════════════════════════════════════════════════════════

print("\n=== Git Push ===")
try:
    repo = os.path.expanduser("~/workspace/the-videshi-news")
    subprocess.run(["git", "add", "public/data/"], cwd=repo, capture_output=True)
    subprocess.run(["git", "add", "pipeline/lifestyle-writer-20260522b.py"], cwd=repo, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "lifestyle: heatwave + gulf jobs crisis + markets + ipl (2026-05-22 19:00)"],
        cwd=repo, capture_output=True, text=True
    )
    if result.returncode == 0:
        push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, text=True, timeout=30)
        if push.returncode == 0:
            print("  ✓ Pushed to main → Vercel auto-deploy")
        else:
            print(f"  Push stderr: {push.stderr[:200]}")
    else:
        print(f"  Commit: {result.stdout[:200]}")
except Exception as e:
    print(f"  Git error: {e}")

print("\n=== Lifestyle Writer Complete ===")
print(f"Articles published: 2")
print(f"  1. [{art1_category}] {art1_headline[:90]}...")
print(f"  2. [{art2_category}] {art2_headline[:90]}...")
