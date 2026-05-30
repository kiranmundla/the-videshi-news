#!/usr/bin/env python3
"""News writer for The Videshi - 2026-05-30 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# Load Supabase credentials
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = None
try:
    with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1]
except:
    pass

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                img_url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {img_url[:80]}...")
                return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return img_url  # Fall back to direct URL
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {ur.status_code} {ur.text[:200]}")
            # If it's a wikimedia or pexels URL, those are permanent - use directly
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url

def publish_article(article):
    """Publish article to Supabase."""
    article_id = str(uuid.uuid4())
    
    # Source image
    print(f"\n📰 Publishing: {article['headline']}")
    img_url = None
    
    if article.get("person_name"):
        img_url = fetch_wikipedia_person_image(article["person_name"])
        if not img_url and article.get("person_alt"):
            img_url = fetch_wikipedia_person_image(article["person_alt"])
    
    if not img_url and article.get("pexels_query"):
        img_url = fetch_pexels_image(article["pexels_query"], article.get("pexels_fallback"))
    
    if img_url:
        filename = f"{article_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article["image_url"] = final_url
        if "upload.wikimedia.org" in (img_url or ""):
            article["image_attribution"] = "Wikimedia Commons"
        else:
            article["image_attribution"] = "The Videshi"
    
    payload = {
        "id": article_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['slug']}")
        return True
    else:
        print(f"  ✗ Failed: {r.status_code} {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: CUET-UG 2026 Technical Glitch
# ============================================================

article_1 = {
    "headline": "CUET-UG 2026 Delayed Across India After TCS Technical Glitch. The Timing Could Not Be Worse.",
    "subheadline": "The Common University Entrance Test was delayed by two hours at centres in Delhi, Noida, Bangalore, and Varanasi — the fourth national exam controversy in two months.",
    "slug": "cuet-ug-2026-tcs-technical-glitch-exam-delay-nta-neet-education-crisis-20260530",
    "person_name": None,
    "pexels_query": "students examination hall India",
    "pexels_fallback": "university entrance exam students",
    "sources": [
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "Careers360", "url": "https://news.careers360.com"}
    ],
    "body": """The Common University Entrance Test for undergraduate admissions — CUET-UG 2026 — was delayed by approximately two hours at examination centres across India on Saturday after a technical glitch at Tata Consultancy Services, the National Testing Agency's technology partner.

The disruption affected centres in Delhi, Noida, Ambala, Varanasi, Bangalore, Kanpur, and other cities. Candidates who arrived for the morning session at 8:15 AM found themselves waiting past 10:30 AM before the exam could begin. The afternoon session was pushed back from 3:00 PM to 4:00 PM, with revised reporting from 2:30 PM.

## TCS Took the Blame

The NTA issued a statement on X attributing the failure entirely to TCS. "M/s TCS has reported that a technical glitch at their end delayed the commencement of CUET (UG) 2026 at some centres on 30.05.2026," it read. The agency said the issue had been resolved and that affected candidates would receive "full compensatory time so that no candidate is disadvantaged."

TCS separately confirmed the disruption, calling the two-hour delay a problem that was "promptly identified and resolved." The company said its teams were "actively monitoring all systems" and reaffirmed its "commitment to working closely with NTA to ensure seamless conduct of computer-based tests."

But the assurances did little to stem the criticism.

## The Fourth Crisis in Two Months

The CUET-UG delay is now the fourth major examination controversy to hit the NTA since late March. The NEET-UG 2026 paper leak, which the Supreme Court has publicly excoriated the agency for, remains unresolved. The CBSE's On-Screen Marking system has produced scoring discrepancies that parents and students have challenged in court. And SSC examinations have drawn their own complaints about irregularities.

AAP leader Saurabh Bharadwaj pointed to a structural risk in Saturday's failure. "If some students get access to the exam paper at 9:30 AM while others get at 11:30 AM, does it not mean a major breach?" he asked on X.

## Opposition Called It a Pattern

Congress leader Rahul Gandhi connected the CUET glitch to the broader pattern. "NEET. CBSE. SSC. And today CUET. Four exams. One crore children. Not a single one conducted with honesty," he posted. "Claims of 'vishwa guru,' but can't conduct even one exam in the country."

AAP national convenor Arvind Kejriwal took a similar line, framing Saturday's disruption as evidence of systemic failure under the current administration. The Congress party shared video footage showing large crowds of students stranded outside examination centres, describing the situation as "beyond the Modi government's capability."

## What This Means for Diaspora Families

CUET-UG is the gateway to admission at 261 universities, including all 45 central universities. For NRI families with children applying to Indian institutions — whether for undergraduate degrees or as a backup to Western admissions — the test's integrity matters directly. A compromised or chaotic examination process makes Indian university admissions less attractive at precisely the moment when several central universities have been expanding their international outreach.

The NTA had already postponed CUET-UG exams originally scheduled for May 28 in view of the revised Bakrid holiday date. Saturday's disruption compounds the scheduling chaos.

## The Bigger Question

India's national examination infrastructure is now a political liability. The NTA was created in 2018 specifically to professionalise the conduct of entrance exams. Seven years later, it faces credible accusations of paper leaks, vendor failures, and administrative incompetence across multiple exams in a single testing cycle.

The Supreme Court has already told the NTA to "learn from UPSC" — a pointed rebuke comparing the agency unfavourably to an institution that has conducted examinations without comparable controversy for decades. Whether Saturday's TCS glitch was a one-off technical failure or a symptom of deeper procurement and oversight problems, the cumulative damage to public trust is real and growing."""
}

# ============================================================
# ARTICLE 2: Abhishek Banerjee Attacked in Sonarpur
# ============================================================

article_2 = {
    "headline": "Abhishek Banerjee Was Pelted With Eggs, Stones, and Shoes in Sonarpur. He Wore a Cricket Helmet.",
    "subheadline": "The TMC general secretary visited families of party workers killed in post-poll violence. Protesters with black flags, eggs, and bricks met him at every stop.",
    "slug": "abhishek-banerjee-attacked-sonarpur-eggs-stones-post-poll-violence-bengal-20260530",
    "person_name": "Abhishek Banerjee (politician)",
    "person_alt": "Abhishek Banerjee",
    "pexels_query": None,
    "pexels_fallback": None,
    "sources": [
        {"name": "PTI", "url": "https://www.ptinews.com"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in"},
        {"name": "CNBC TV18", "url": "https://www.cnbctv18.com"},
        {"name": "India Today", "url": "https://www.indiatoday.in"}
    ],
    "body": """Trinamool Congress national general secretary Abhishek Banerjee was attacked with eggs, stones, shoes, and bricks during a visit to Sonarpur in West Bengal's South 24 Parganas district on Saturday. The Diamond Harbour MP donned a cricket helmet for protection as he navigated through crowds of hostile protesters who had gathered at multiple points along his route.

The visit — Banerjee's first major political outing since the West Bengal assembly election results were announced nearly three weeks ago — was intended as a show of solidarity with TMC workers and their families who had been targeted in post-poll violence.

## Black Flags, Eggs, and "Chor Chor" Chants

Before Banerjee even arrived in Sonarpur, groups of women were positioned along the route carrying eggs. BJP supporters had assembled with black flags and chanted "Go Back" slogans. His convoy encountered protests at multiple locations — near Patuli's Dhalai Bridge, in Kamrabad, and at several other points across Sonarpur.

As Banerjee entered the area on a motorcycle, protesters attempted to physically stop him. Despite the hostile reception, he pressed forward wearing the helmet. Videos circulating on social media showed security personnel surrounding and shielding the TMC leader as eggs and stones rained down.

Locals allegedly raised "chor chor" (thief, thief) slogans against him throughout the visit.

## "They Want to Kill Me"

Banerjee was unequivocal about who he held responsible. "It's all BJP-sponsored. Look what they have done. This is their example of democracy. It hasn't even been a month, and the police are nowhere to be seen," he told reporters from behind the security cordon.

"I will not move out from here till police and forces ensure security here. They are trying to break the house and they want to kill me," he added, claiming that adequate security had not been provided despite prior intimation to authorities.

## Post-Poll Violence: The Context

The attack occurred against the backdrop of post-election violence that has convulsed parts of Bengal since the assembly results were declared. A TMC worker named Sanju Karmakar was allegedly killed in post-poll violence in Beliaghata. Banerjee had visited Karmakar's family at the residence of TMC leader Kunal Ghosh before heading to Sonarpur to meet other affected families.

Post-poll violence is a recurring feature of Bengal's electoral cycles, but the scale and openness of the assault on a sitting MP — who is also the nephew of former Chief Minister Mamata Banerjee — marks an escalation. The TMC has been the ruling party in West Bengal for over a decade, but the recent assembly elections appear to have emboldened its opponents.

## CID Visit the Same Morning

Adding to the political charge of the day, a team from the state Criminal Investigation Department visited Banerjee's residence "Shantiniketan" on Harish Mukherjee Road earlier on Saturday in connection with an assembly signature forgery investigation. Staff and security personnel reportedly informed officers that neither Banerjee nor his family members were present.

## The Diaspora Dimension

West Bengal's political turbulence has long been of interest to the Bangladeshi and Bengali diaspora communities. The post-poll violence and Banerjee's dramatic confrontation come at a time when the TMC's political position in the state is being openly contested in ways that were rare during Mamata Banerjee's dominant years.

For NRIs from Bengal or with family connections to the state, the images from Sonarpur — a sitting MP in a cricket helmet, pelted with eggs and stones by people he came to represent — capture a political reality that is shifting faster than many expected."""
}

# ============================================================
# ARTICLE 3: Finance Ministry Inflation Warning
# ============================================================

article_3 = {
    "headline": "India's Finance Ministry Has Named the Single Biggest Risk to the Economy. It Is the Strait of Hormuz.",
    "subheadline": "The ministry's monthly economic report warns that fuel price hikes, a weak monsoon, and the Middle East conflict will push retail inflation higher in the coming months.",
    "slug": "india-finance-ministry-inflation-warning-hormuz-monsoon-fuel-prices-iran-war-20260530",
    "person_name": None,
    "pexels_query": "crude oil tanker shipping",
    "pexels_fallback": "India fuel petrol station",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Finance Ministry of India", "url": "https://www.finmin.nic.in"}
    ],
    "body": """India's finance ministry released its monthly economic report on Saturday with a warning that landed harder than the usual hedged language of government documents. The "single most consequential variable" for the Indian economy, it said, is the duration of the Strait of Hormuz disruption.

That sentence — buried in a document that otherwise described India's near-term outlook as one of "cautious resilience" — is the clearest official acknowledgement yet that the Iran war has become the central risk to India's economic trajectory.

## What the Report Actually Says

The ministry laid out a chain of pressures that it expects to push retail inflation higher in the coming months:

**Fuel prices have already risen.** Recent hikes in petrol and diesel prices — driven by India's dependence on imported crude — are now in the system. The report says "a sharp rise in upstream price pressures, along with recent increases in fuel prices, suggests a gradual pass-through to retail inflation through higher transport, energy, and food-related costs."

**The monsoon is expected to be weak.** India's weather department downgraded its monsoon forecast to 90% of the long-period average earlier this week — the weakest since 2015. An El Niño is expected to develop during the season, with moderate-to-strong intensity in the second half. "A significant rainfall deficit coupled with current geopolitical conditions could translate into food inflation, weakening rural demand and aggregate growth," the ministry warned.

**The rupee is under pressure.** The Indian currency has lost roughly 6% this year, driven by steep capital outflows. Overseas investors have pulled over $24 billion from Indian debt and equities between March and May alone. A weaker rupee makes imports more expensive, compounding the oil price effect.

## The Numbers Right Now

India's retail inflation was 3.48% in April — still comfortably below the Reserve Bank of India's 4% target. But the ministry's report makes clear that this headline number understates the building pressure.

Wholesale price inflation has already accelerated sharply. Brent crude remains roughly 27% above pre-war levels despite a 19% drop in May. And food prices, which account for nearly half the consumer price index basket, are vulnerable to a poor monsoon.

Some economists are projecting inflation could reach 5.5% if food prices spike during a deficient monsoon, according to IDFC First Bank's chief economist Gaura Sengupta. That would be well above the RBI's comfort zone and would complicate the central bank's June 5 policy decision.

## The RBI's Dilemma

The Reserve Bank has kept its key interest rate at 5.25% since its last cut in April. A Reuters poll of 56 economists showed that while 80% expect the RBI to hold in June, 11 now forecast a 25-basis-point hike — up from just one respondent in April's survey.

Capital Economics expects the RBI to raise rates to 6.00% before the end of the year, "contingent on the crisis coming to an end soon and energy prices dropping back." But others argue that rate hikes are the wrong tool for supply-side shocks.

"Interest rates are not a good tool to counter large supply shocks. Also, I do not think the RBI MPC will increase rates to defend the rupee since it is beyond the remit of the MPC," said Aditya Vyas, chief economist at STCI Primary Dealer.

## What NRIs Should Watch

For the Indian diaspora, the finance ministry's warning matters in three direct ways.

**Remittances lose value.** A weakening rupee means each dollar or pound sent home converts to more rupees — good news for recipients. But if inflation erodes that purchasing power, the benefit is illusory.

**Investment returns are at risk.** Indian equities posted monthly losses in May, with the Nifty 50 dropping 1.9% and the Sensex falling 2.8%. The combination of high oil prices, weak capital inflows, and a potential rate hike creates headwinds for anyone with India-linked portfolios.

**Property and consumption costs rise.** NRIs planning visits, purchases, or family support in India will face higher costs across transport, food, and services if the inflation pass-through plays out as the ministry expects.

The finance ministry releases its economic report monthly. This one reads less like a status update and more like a warning."""
}

# ============================================================
# PUBLISH ALL ARTICLES
# ============================================================

articles = [article_1, article_2, article_3]
success_count = 0
for article in articles:
    if publish_article(article):
        success_count += 1
    time.sleep(1)

print(f"\n✅ Published {success_count}/{len(articles)} articles")
