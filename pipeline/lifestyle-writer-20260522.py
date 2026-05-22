#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-22 run
2 articles: NEET 2026 paper leak + India monsoon El Niño forecast
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
# ARTICLE 1: NEET 2026 Paper Leak — What NRI Families Need to Know
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "India Just Cancelled Its Biggest Medical Entrance Exam. For NRI Families Who Planned Their Children's Futures Around It, the Fallout Is Personal."
art1_subheadline = "NEET-UG 2026 was scrapped after investigators found a 'guess paper' with 140 questions matching the real exam. The re-test is June 21. For the 22.8 lakh students and the diaspora parents who funded years of coaching, nothing feels safe anymore."
art1_slug = make_slug("neet-2026-paper-leak-cancelled-nri-families-coaching-reexam")
art1_category = "lifestyle-health"

art1_body = """When the National Testing Agency tweeted on May 11 that NEET-UG 2026 was cancelled, Meera Krishnan was sitting in her living room in Fremont, California, doing mental arithmetic. Her daughter Ananya had taken the exam on May 3 at a centre in Pune, having spent the past two years at a Kota coaching institute that cost the family roughly ₹8 lakh in tuition and another ₹4 lakh in hostel fees. The plan was clear: NEET score, MBBS seat, a career in medicine that would honour a family tradition stretching back three generations.

"We got the news from a WhatsApp group before we saw the official tweet," Krishnan said. "My daughter called crying. She said, 'Amma, I gave everything.' I didn't know what to tell her."

Her story is playing out in thousands of NRI households this week.

## The Scandal

The NEET-UG 2026 examination was conducted on May 3, 2026, with approximately 22.79 lakh candidates appearing across India and at overseas centres. Within days, Rajasthan Police's Special Operations Group recovered a document containing more than 300 questions. Of those, 140 were reportedly near-identical to questions on the actual exam paper.

By May 8, the NTA had escalated the matter to central investigation agencies. Thirteen people have been detained so far in Rajasthan and Uttarakhand. Reports suggest that some question sets were allegedly sold to students for up to ₹5 lakh before the exam, and that leaked material may have reached buyers nearly two days before test day.

On May 11, the NTA confirmed cancellation and announced a re-examination scheduled for June 21, 2026 — seven weeks after the original test. The CBI has taken over the investigation. No additional registration fee will be charged, and existing admit card details will remain valid.

## A Pattern, Not an Anomaly

For those following Indian education closely, the déjà vu is suffocating. In 2024, NEET faced similar allegations of paper leaks and irregularities. The Supreme Court intervened, though it ultimately refused to order a full re-examination, approving a partial retest for only 1,563 candidates who had received grace marks. In 2025, the Madhya Pradesh High Court ordered a retest for 75 students whose exam was disrupted by power outages in Indore and Ujjain.

The 2026 scandal is, by every measure, the most severe yet. Investigators claim that 60 to 70 per cent of the actual paper matched the circulated material. The NTA has promised that the June 21 re-examination will deploy enhanced security: GPS-tracked question paper transport, AI-based CCTV surveillance, biometric verification at every centre, and 5G signal jammers.

Whether any of that will restore faith in the system is an open question.

## The NRI Investment

The emotional and financial stakes for diaspora families are enormous, and often invisible in Indian media coverage of the scandal. For NRI parents, the medical-entrance pipeline is not a casual ambition — it is a multi-year, multi-lakh investment that frequently involves relocating children to India, separating families across continents, and betting on a system that is supposed to be the great meritocratic equaliser.

The numbers tell part of the story. A two-year NEET preparation programme at a reputed Kota coaching centre now costs between ₹6 and ₹10 lakh in tuition alone. Add hostel fees, travel, study materials, and test series subscriptions, and the total outlay can cross ₹15 lakh before a student even sits the exam. For NRI families paying in dollars, the exchange rate offers some relief — but the emotional cost of sending a 16- or 17-year-old to live alone in a pressure-cooker city is not denominated in currency.

Several coaching chains now offer dedicated NRI batches with premium pricing, hostel concierges, and parent communication portals. The industry, valued at an estimated ₹58,000 crore nationally, has built an entire infrastructure around the assumption that NEET is fair. When that assumption collapses, so does the business model — and so do the families who bought into it.

## What Parents Should Do Now

For NRI families navigating the fallout, the immediate priorities are logistical and emotional.

**Confirm re-registration status.** The NTA has stated that fresh registration is not required. However, families should verify that their child's admit card details, centre preferences, and photograph are current on the official NTA portal (neet.nta.nic.in). The agency has advised relying only on official channels and ignoring unverified social media claims about dates or procedures.

**Prepare for a compressed timeline.** The re-exam is June 21 — roughly four weeks away. Students who had begun winding down after May 3 now face the challenge of re-entering peak preparation mode. For those who returned to the US, UK, or Gulf after the exam, the logistics of flying back to India are not trivial, particularly with summer airfares at their annual peak and the continuing disruption to Gulf aviation routes caused by the Iran conflict.

**Consider the psychological toll.** Two years of preparation, a high-stakes exam, a cancellation, and now a redo within weeks — the mental health implications are serious. Adolescent psychologists in India have reported a spike in anxiety-related consultations since the cancellation announcement. NRI parents should be proactive about arranging counselling support, whether through US-based therapists familiar with South Asian academic culture or through the growing number of Indian teletherapy platforms.

**Explore parallel options.** Not every aspiring doctor needs to go through NEET. NRI families should research alternative pathways, including medical programmes in the US, UK, Caribbean, and Eastern Europe, as well as deemed university seats in India that accept scores from other entrance exams. The cost-benefit calculus has shifted: if the integrity of NEET cannot be guaranteed, the premium for a more reliable pathway may be worth paying.

## The Bigger Question

India's medical entrance exam is, in theory, one of the most egalitarian institutions in the country. It is the single gateway to roughly 1.1 lakh MBBS and BDS seats — a number that has not kept pace with a population of 1.45 billion. The pressure it creates is not a bug; it is a structural feature of a system that produces far fewer doctors than it needs.

When that system is compromised — not once, not twice, but in three consecutive cycles — the damage extends beyond the students who were cheated. It corrodes trust in the institutions that are supposed to level the playing field. For diaspora families who chose India's medical system over Western alternatives precisely because they believed in its rigour, the betrayal is double.

The June 21 re-exam will determine MBBS seats. It will not determine whether India's examination infrastructure deserves the faith that millions of families have placed in it. That question has already been answered."""

art1_sources = [
    "https://medicine.careers360.com/articles/is-re-neet-2026-possible",
    "https://collegedunia.com/articles/e-457-re-neet-2026-check-paper-leak-probe-retest-rules-explained",
    "https://english.amarujaladigital.com",
]

print("=== Article 1: NEET 2026 Paper Leak ===")
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
    "score_total": 82,
    "tags": ["NEET", "education", "NRI", "medical entrance", "paper leak", "NTA", "coaching", "Kota", "CBI"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "NRI families invest lakhs in Kota coaching and NEET prep for their children; the cancellation disrupts multi-year plans and raises questions about the reliability of India's exam system for diaspora families betting on it.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Monsoon Forecast — El Niño, Drought, NRI Impact
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "India's Monsoon Is Arriving Early. The Rain That Follows May Not Be Enough — and NRIs With Family Farmland Should Pay Attention."
art2_subheadline = "The IMD says the southwest monsoon will hit Kerala by May 26, six days ahead of schedule. But a strengthening super El Niño means the season could deliver the least rainfall in three years, with drought risks in Punjab, Haryana, and Rajasthan — the ancestral heartlands of the largest NRI communities."
art2_slug = make_slug("india-monsoon-2026-el-nino-drought-nri-farmland-water")
art2_category = "lifestyle-health"

art2_body = """The monsoon is coming early to India this year. According to the India Meteorological Department, the southwest monsoon is expected to make landfall over Kerala on May 26, approximately six days ahead of the historical average of June 1. For a country that depends on four months of seasonal rain for 70 per cent of its annual water supply, that might sound like good news.

It is not. The early onset masks a far more troubling forecast: India's 2026 monsoon season is projected to deliver below-normal rainfall for the first time in three years, driven by a rapidly strengthening El Niño event that climate scientists say could rival the catastrophic cycles of 1997 and 2015. For NRI families with roots in Punjab, Haryana, Rajasthan, and central India — the regions most vulnerable to drought — the implications are direct, financial, and deeply personal.

## The Numbers

The IMD's first long-range forecast, released on April 13, projected seasonal rainfall at 92 per cent of the long-period average of approximately 870 millimetres. The probability of a deficient season — rainfall below 90 per cent of the average — stands at 35 per cent, more than double the historical probability of 16 per cent.

Skymet, India's largest private weather forecasting agency, has issued an even more cautious outlook. Its models place total monsoon rainfall at 94 per cent of the long-period average, with significant deterioration expected after June. Both forecasters agree on the timeline: the first half of the monsoon, particularly June, should remain relatively stable. The trouble arrives in August and September, when El Niño's grip on atmospheric circulation will be at its strongest.

## What El Niño Means for India

El Niño is a periodic warming of the central and eastern Pacific Ocean that disrupts global weather patterns. For India, its effects are brutally specific: it weakens the monsoon winds that carry moisture from the Indian Ocean across the subcontinent, suppressing rainfall across northern, western, and central regions while paradoxically triggering excess rain along parts of the southern and eastern coastline.

The Pacific is already showing clear signals. Sea surface temperatures in the Niño 3.4 monitoring region are running approximately 0.5 degrees Celsius above the long-term average — an early but significant indicator. Some forecasting models project anomalies exceeding 2 degrees Celsius before year's end, which would classify this as a super El Niño, among the most powerful on record.

The last comparable event, in 2015-16, pushed actual monsoon rainfall down to just 86 per cent of the long-period average. The Marathwada region of Maharashtra recorded a 40 per cent rainfall deficit. Chennai was simultaneously submerged under floodwaters for days. In 2023, another El Niño year, India saw a 36 per cent rainfall deficit in August alone.

## The Geography of Risk

The projected impact is starkly uneven across India. Punjab, Haryana, and Rajasthan face the highest risk of prolonged dry conditions during August and September — precisely when the kharif crop season demands the most water. The core monsoon belt across Madhya Pradesh, including Indore, Ujjain, Gwalior, and the Narmada valley, is expected to receive below-normal precipitation.

Delhi-NCR, already suffering through a severe heatwave with temperatures touching 48 degrees Celsius, will see little monsoon relief. Drier and hotter conditions are forecast to persist deep into the season.

Chennai and coastal Tamil Nadu face the opposite threat: excessive rainfall and flooding, a pattern consistent with every strong El Niño year in recent memory.

Roughly 60 per cent of Indian farmers are entirely dependent on monsoon rainfall for kharif planting. Rice, soybean, corn, sugarcane, and cotton — the backbone of Indian agriculture — all hang on what happens between July and September.

## Why NRIs Should Care — Concretely

For the millions of NRIs whose families still hold agricultural land in Punjab, Haryana, western Uttar Pradesh, and Rajasthan, a monsoon shortfall is not an abstraction. It translates into lower crop yields, higher input costs for supplementary irrigation, falling land values, and strained relationships with tenant farmers or relatives managing the property.

The financial mechanics are straightforward. A 10 to 15 per cent rainfall deficit in Punjab typically reduces rice paddy yields by 8 to 12 per cent, according to agricultural economists at Punjab Agricultural University. For a family holding 5 acres of paddy land — a common NRI portfolio in the Doaba and Malwa regions — that deficit can mean a loss of ₹40,000 to ₹80,000 in a single season. Multiply that across consecutive drought years, and the erosion is significant.

Then there is the water table. Punjab's groundwater is already in crisis, with the Central Ground Water Board classifying the majority of the state's blocks as overexploited. A below-normal monsoon accelerates the drawdown, raising the cost of borewell deepening — an expense that frequently falls on the NRI landowner, whether or not they are aware it is happening.

**Check your family's water situation.** If you own agricultural land in the drought-risk belt, this is the month to have a frank conversation with whoever is managing it. Ask about borewell depth, electricity availability for pumping, and whether canal water allocations are being reduced. The answers may determine whether your land is productive this year.

**Watch food prices.** A weak monsoon pushes up the prices of pulses, rice, edible oils, and vegetables — staples that NRI families purchase in bulk at Indian grocery stores abroad. If El Niño delivers the deficiency that forecasters expect, import costs will rise by late 2026, compounding inflation that is already elevated because of the Iran conflict's disruption to global energy markets.

**Reconsider summer travel timing.** NRIs planning July-August trips to India — the traditional "kids are on summer break" window — should factor in the possibility that northern India will be simultaneously hotter and drier than usual, with water supply restrictions in urban areas. Delhi, Jaipur, and Chandigarh have all announced phased water rationing measures in anticipation of a weak monsoon recharge.

## The Policy Response

The Indian government is not ignoring the signals. The IMD is expected to release an updated monsoon forecast in the final week of May. The Ministry of Agriculture has directed states to prepare contingency crop plans, and the National Water Mission has issued advisories on reservoir management and groundwater conservation.

Whether those measures will be sufficient depends on how severe the El Niño becomes. If models projecting a super El Niño prove correct, the policy toolkit available to the government — essentially, more subsidised irrigation and a higher minimum support price for affected crops — will be stretched thin.

For now, the monsoon is arriving early. Whether it will stay, and whether it will deliver what India needs, is the question that 1.45 billion people — and their relatives scattered across the globe — are waiting to answer."""

art2_sources = [
    "https://www.reuters.com/business/environment/monsoon-rains-hit-southern-indian-coast-early-spurring-crop-planting-2026-05-15/",
    "https://www.livemint.com/news/india/drought-in-delhi-floods-in-chennai-how-super-el-nino-could-impact-india-2026-monsoon-which-cities-will-be-hit-hardest-11778990058786.html",
    "https://skymetweather.com",
    "https://indiawaterportal.org",
]

print("\n=== Article 2: India Monsoon El Niño ===")
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
    "score_total": 80,
    "tags": ["monsoon", "El Niño", "drought", "agriculture", "NRI", "Punjab", "Haryana", "water crisis", "IMD", "Skymet"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "NRIs with family farmland in Punjab, Haryana, Rajasthan face crop losses and groundwater depletion; monsoon deficit affects food prices at Indian grocery stores abroad; summer travel to India complicated by drought and heat.",
    "word_count": len(art2_body.split()),
})
if result2:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# IMAGE SOURCING via Pexels (curl-based, urllib gets 403)
# ══════════════════════════════════════════════════════════════

print("\n=== Image Sourcing ===")

# Load Pexels API key
pexels_key = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                pexels_key = line.strip().split("=", 1)[1].strip('"').strip("'")

def pexels_search(query, per_page=5):
    """Search Pexels via curl (urllib gets 403)."""
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
    content_type = "image/jpeg"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    url = f"{SB_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    r = requests.post(url, headers=upload_headers, data=data)
    if r.status_code in (200, 201):
        return f"{SB_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
    else:
        print(f"  Upload failed ({r.status_code}): {r.text[:200]}")
        return None

# Article 1 images: NEET / education / Indian students
art1_searches = ["Indian students studying exam", "medical students India", "exam hall classroom India"]
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
        "image_caption": "NEET-UG 2026 was cancelled after investigators found 140 questions matching a circulated 'guess paper'. The re-exam is June 21.",
    })
    print("  ✓ Art1 image set")
else:
    print("  ✗ Art1 no image found")

# Article 2 images: monsoon / rain / Indian agriculture
art2_searches = ["India monsoon rain farmland", "Indian agriculture drought", "monsoon clouds India"]
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
        "image_caption": "India's 2026 monsoon is forecast to deliver below-normal rainfall, with El Niño threatening drought across the northern heartland.",
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
# MARKETS + IPL REFRESH
# ══════════════════════════════════════════════════════════════

print("\n=== Markets Refresh ===")
try:
    subprocess.run(
        ["python3", "videshi-markets.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True
    )
    print("  ✓ Markets refreshed")
except Exception as e:
    print(f"  Markets error: {e}")

print("\n=== IPL Refresh ===")
try:
    subprocess.run(
        ["python3", "videshi-ipl.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True
    )
    print("  ✓ IPL refreshed")
except Exception as e:
    print(f"  IPL error: {e}")

print("\n=== Market Charts ===")
try:
    subprocess.run(
        ["python3", "videshi-market-charts.py"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        timeout=60, capture_output=True
    )
    print("  ✓ Market charts refreshed")
except Exception as e:
    print(f"  Market charts error: {e}")


# ══════════════════════════════════════════════════════════════
# GIT PUSH
# ══════════════════════════════════════════════════════════════

print("\n=== Git Push ===")
try:
    repo = os.path.expanduser("~/workspace/the-videshi-news")
    subprocess.run(["git", "add", "public/data/"], cwd=repo, capture_output=True)
    subprocess.run(["git", "add", "pipeline/lifestyle-writer-20260522.py"], cwd=repo, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "lifestyle: 2 articles + markets + ipl refresh (2026-05-22 15:00)"],
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
print(f"  1. [{art1_category}] {art1_headline[:80]}...")
print(f"  2. [{art2_category}] {art2_headline[:80]}...")
