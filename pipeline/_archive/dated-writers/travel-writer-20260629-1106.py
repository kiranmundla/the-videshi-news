#!/usr/bin/env python3
"""Travel writer — 2026-06-29 11:06 run. Two articles:
1. Kailash Mansarovar Yatra advisory (52 pilgrims stranded in Nepal)
2. US tourist visa wait times surge across Indian consulates
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def sb_post(table, data):
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Kailash Mansarovar Yatra ─────────────────────────────────

article1_body = """After six years of suspension and months of diplomatic groundwork between New Delhi and Beijing, the Kailash Mansarovar Yatra was supposed to be a triumphant return. Instead, the 2026 season has opened with a cautionary tale: 52 Indian pilgrims stranded in Kathmandu, caught between shady tour operators and a Chinese border that would not let them through.

The Ministry of External Affairs issued an urgent advisory on June 28, warning citizens not to begin the pilgrimage without every required document in hand — a Chinese visa, a Travel Permit for the Tibetan Autonomous Region, and a Restricted Area Permit for Nepal, depending on the route. The advisory was unusually blunt: "Commencing travel without confirmed documentation or in anticipation of obtaining the necessary documentation increases the likelihood of being stranded."

## What Went Wrong in Kathmandu

The stranded pilgrims had booked through private tour operators who assured them the Chinese entry permits would be "arranged en route." They were not. The pilgrims reached Nepal only to discover that the Chinese Embassy in Kathmandu does not issue group visas for the yatra — those must be obtained through the Chinese Embassy in New Delhi before departure. NCP(SP) MP Supriya Sule flagged the crisis on social media and called on External Affairs Minister S. Jaishankar to intervene.

The MEA has since directed Indian missions in Nepal and China to provide support to the stranded group, but the incident underscores a basic problem: a pilgrimage that demands high-altitude fitness and spiritual preparation is being sold by operators with neither the licensing nor the logistics to deliver.

## A Yatra Reborn — and Tightly Controlled

The Kailash Mansarovar Yatra was suspended in 2020 after the Galwan Valley clash froze India-China border relations. Its resumption in 2026 is part of a broader diplomatic thaw — the first batch of pilgrims crossed into China via Nathu La Pass in Sikkim on June 20, nine days before the advisory dropped.

But the renewed yatra operates under strict constraints. China has allocated a quota of roughly 1,000 Indian pilgrims for the entire year, spread across 20 batches of 50. Two approved routes exist: Lipulekh Pass in Uttarakhand and Nathu La in Sikkim. The official government-organised yatra selects participants through a computerised, gender-balanced lottery via a dedicated MEA portal.

Private operators offer an alternative — and a riskier one. The MEA's advisory specifically targets this channel, urging pilgrims to verify that their operator is "duly registered and authorised." There is no centralised registry of approved private operators, which means due diligence falls entirely on the pilgrim.

## What NRIs Planning a Family Yatra Need to Know

For the Indian American diaspora, the Kailash Mansarovar Yatra carries deep significance. Many NRIs plan it as a once-in-a-lifetime journey for elderly parents — a spiritual milestone that families save and prepare for over years. The 2026 resumption sparked fresh interest across community forums and WhatsApp groups in the US.

Here is what families need to verify before anyone books:

**Documents required (non-negotiable):** A valid Indian passport with at least six months' remaining validity, a Chinese group visa (applied through an authorised operator via the Chinese Embassy in New Delhi), a Tibet Tourism Bureau permit, and a Restricted Area Permit for the Nepal route segments. OCI cardholders cannot undertake the yatra — Indian citizenship is mandatory.

**Medical fitness:** Pilgrims must pass a comprehensive medical examination. The route climbs above 19,500 feet at Dolma La Pass, and altitude sickness is a serious risk. The MEA recommends carrying personal medications and adequate travel insurance that covers high-altitude medical emergencies and evacuation.

**Financial preparation:** Remote stretches of the route lack ATMs, banking services, and mobile connectivity. Cash and satellite communication devices are strongly recommended.

**Operator verification:** Ask for the operator's MEA registration number and cross-check it with the Ministry. If an operator promises to arrange Chinese visas after departure, walk away.

## The Bigger Picture

The resumption of the Kailash Mansarovar Yatra is a genuine diplomatic achievement — a pilgrimage route that once seemed permanently severed by geopolitics is open again. But the 52 stranded pilgrims in Kathmandu are a reminder that bureaucratic friction at the India-China-Nepal tri-junction has not disappeared. It has just moved from the border post to the visa office.

For NRI families, the safest path remains the official government yatra. The application window typically closes in spring, so those planning for 2027 should watch the MEA portal starting in January."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "52 Pilgrims Stranded in Nepal Expose the Risks of the Kailash Mansarovar Yatra's Private-Operator Route",
    "subheadline": "The MEA's blunt advisory after India's most sacred Himalayan pilgrimage resumed for the first time since 2020 — and what every NRI family planning the yatra must verify before booking.",
    "slug": make_slug("kailash-mansarovar-yatra-pilgrims-stranded-nepal-mea-advisory-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Many NRIs plan the Kailash Mansarovar Yatra as a once-in-a-lifetime spiritual journey for elderly parents — the 2026 resumption sparked fresh interest, but the stranded-pilgrim crisis shows why families must verify every document before anyone departs India.",
    "tags": ["travel", "kailash-mansarovar", "pilgrimage", "mea-advisory", "india-china", "nepal"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "IANS via India News Stream", "url": "https://www.indianewsstream.com/india-cautions-its-citizens-against-undertaking-kailash-mansarovar-yatra-with-incomplete-documents/"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/spiritual/mea-urges-kailash-mansarovar-pilgrims-to-secure-chinese-visas-before-departure"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/headed-for-the-kailash-mansarovar-yatra-mea-issues-urgent-warning-to-secure-china-permit-and-visa-what-to-know-11751111200843.html"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/mea-warns-kailash-mansarovar-pilgrims-obtain-china-permits-visas-traveling/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Kailash_north.JPG",
    "image_caption": "Mount Kailash viewed from the north face in Tibet",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ── Article 2: US Visa Wait Times ───────────────────────────────────────

article2_body = """If your parents in India applied for a US tourist visa today in Mumbai, they would wait until April 2027 for an interview. In Hyderabad, the same. In Delhi, they would not sit across from a consular officer until March. The US State Department's latest wait-time data paints a grim picture for Indian families trying to bring relatives to America — and new screening protocols are making the bottleneck worse.

## The Numbers

The State Department's Global Visa Wait Times tracker, updated regularly, now shows the following B-1/B-2 (tourist and business) interview wait times at Indian consulates:

- **Mumbai:** 9.5 months average wait, next available appointment in 10 months
- **Hyderabad:** 9.5 months average wait, next available appointment in 9.5 months
- **New Delhi:** 7.5 months average wait, next available appointment in 8.5 months
- **Chennai:** 5.5 months average wait (next appointment data not available)
- **Kolkata:** 4 months average wait, next available appointment in 4 months

Mumbai and Hyderabad now rank among the longest B-1/B-2 wait times globally — worse than Lagos, Bogotá, or São Paulo. The backlog has worsened sharply: six months ago, Mumbai's average was closer to 7.5 months and Hyderabad's was under 8.

## What Changed

Two forces are compounding the delay. The first is raw demand. India is the world's largest nonimmigrant visa market, and the post-pandemic travel surge has not abated. The State Department has not matched this demand with additional consular staffing at its five Indian posts.

The second is new vetting. Since December 15, 2025, US consulates worldwide have implemented expanded screening protocols that include social media and digital footprint checks for visa applicants. While the State Department has not formally announced the policy shift, consulates in Chennai, Hyderabad, Mumbai, and New Delhi have been uniformly applying the new procedures, according to immigration law firms tracking the changes.

The practical impact: consulates have been rescheduling existing appointments en masse, pushing them 90 to 120 days further out. Administrative processing times after the interview have also lengthened, adding weeks or months of uncertainty for applicants who clear the interview but face additional scrutiny.

## Why This Hits NRIs Hardest

For Indian Americans, the tourist visa backlog is not an abstract immigration statistic — it is the reason your mother missed your child's birthday, or why your father cannot visit this Diwali.

The B-1/B-2 visa is the primary instrument for Indian family members who do not hold green cards or dual citizenship to visit the US. Unlike H-1B or L-1 work visas (which have wait times of 1.5 to 2 months in most Indian cities), tourist visa queues have ballooned because they receive lower processing priority and the applicant pool is enormous.

The timing is especially painful. Summer is peak season for family visits — grandparents coming to help with childcare while school is out, parents attending graduations and weddings. By the time a Mumbai applicant who files today gets an interview, that window will have closed entirely.

## What Families Can Do

**Apply early — absurdly early.** The State Department's own guidance now recommends applying "as far in advance as possible." For a planned Diwali 2026 visit, the application window has already passed in Mumbai and Hyderabad. Christmas 2026 is borderline. Families planning summer 2027 visits should file now.

**Choose your consulate strategically.** Kolkata's 4-month wait is less than half of Mumbai's. Chennai at 5.5 months is significantly faster than Delhi's 7.5. Indian applicants can apply at any US consulate in India, regardless of their home state. The trade-off is travel to a different city for the interview, but the time savings can be worth months.

**Check for interview waivers.** Applicants renewing a B-1/B-2 visa may qualify for the Dropbox (interview waiver) programme, which allows document submission without an in-person interview. All Dropbox submissions are processed centrally in New Delhi, but the waiver can be filed at Visa Application Centres in Chennai, Hyderabad, Kolkata, Mumbai, or New Delhi at no extra cost. Filing at centres in Ahmedabad, Bangalore, Chandigarh, Cochin, Jalandhar, or Pune carries a ₹1,200 fee.

**Monitor cancellation slots.** Consulates release additional appointment slots regularly. Applicants who have already scheduled an interview should check the booking portal frequently — many report finding earlier slots during off-peak hours, particularly late at night India time.

**Consider third-country consulates.** Indian nationals with an urgent need can apply as third-country nationals at US consulates outside India. Popular options include consulates in the UAE, Singapore, or Thailand, though applicants may need a visa for the transit country and should factor in travel costs.

## The Structural Problem

India's visa backlog is not a temporary post-pandemic hangover. It reflects a structural mismatch between the volume of Indian applicants — driven by one of the world's largest diasporas — and the fixed capacity of five US consular posts that have not added staff in proportion to demand. Until Washington invests in consular infrastructure in India at the scale the relationship demands, the wait will remain a tax on every NRI family trying to stay connected across the Pacific."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Getting Your Parents a US Visa Now Means a 10-Month Wait in Mumbai — and It's Getting Worse",
    "subheadline": "Hyderabad and Mumbai wait times have hit 9.5 months for tourist visas, new social media screening protocols are pushing appointments further out, and NRI families have fewer options than they think.",
    "slug": make_slug("us-visa-wait-times-india-mumbai-hyderabad-nri-parents"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "The B-1/B-2 tourist visa is how most NRI families bring parents and relatives to visit the US — with Mumbai and Hyderabad waits now at 9.5 months, summer and Diwali visits are effectively blocked unless families applied months ago.",
    "tags": ["travel", "visa", "us-visa", "immigration", "nri", "b1b2"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "US State Department — Global Visa Wait Times", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/longer-tourist-visa-queues-hyderabad-mumbai-delhi-face-delays/"},
        {"name": "Fragomen (Immigration Law Firm)", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-us-consulates-in-india.html"},
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/travel-news/us-visa-india-wait-times/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/88/US_Embassy_New_Delhi.jpg",
    "image_caption": "The US Embassy in New Delhi, where tourist visa wait times have climbed to 8.5 months",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ── Insert ──────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
