#!/usr/bin/env python3
"""Immigration writer — 2026-06-03 20:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ─────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────

art1_headline = "Not Just Tech Workers — Senators Want H-1B Fee Waivers for the Doctors and Teachers Keeping Rural America Alive"

art1_subheadline = "At DHS Secretary Mullin's first Senate budget hearing, Alaska's Murkowski and Maine's Collins made the case that a $100,000 visa fee is gutting the workforce pipelines rural communities cannot afford to lose."

art1_body = """The $100,000 H-1B fee introduced last September was designed to make foreign hiring more expensive. It succeeded. But the senators who showed up to DHS Secretary Markwayne Mullin's first budget hearing on Tuesday were not there to talk about Silicon Valley. They were there to talk about hospitals with empty operating rooms and schools that cannot find a math teacher.

## The Doctors

Senator Susan Collins of Maine opened the exchange. Rural hospitals in her state depend on foreign-trained physicians to keep their doors open. Under the old system, a small critical-access hospital could sponsor an H-1B doctor for a few thousand dollars in filing fees. Under the new system, the same hospital owes $100,000 before the physician even gets off the plane.

Collins pressed Mullin directly: could the administration create exemptions for doctors serving communities where local recruitment has provably failed? Mullin's answer was notably conciliatory. "We do have some authority and flexibility to be able to waive some of this on a case-by-case basis," he told the subcommittee.

He went further: "We're happy to look into it, look at language, try to get it better."

For an administration whose immigration posture has ranged from restrictive to hostile, "happy to look into it" counts as an open door.

## The Teachers

Senator Lisa Murkowski of Alaska followed Collins with a parallel concern. School districts in Alaska's remote communities have relied on internationally recruited teachers for years. These are not prestige postings. They are villages accessible only by bush plane, where the nearest grocery store might be a hundred miles away.

"I'll follow up with you about the issue that I raised previously with regards to H-1B visas for teachers," Murkowski told Mullin. "I know Senator Collins raised it for medical professionals, but we're really anxious about this as school districts are looking to bring on and hire more of our teachers."

Murkowski did not provide specific data during the hearing, but Alaska's teacher shortage has been documented for decades. The state's reliance on out-of-state and international recruitment is structural, not optional.

## The Numbers

The scale of the $100,000 fee's adoption is staggering. Mullin told the subcommittee that of 286,000 H-1B applications received in FY2026, more than 200,000 applicants paid the $100,000 premium. Those who paid get their petitions processed in roughly 15 days. Everyone else waits 7.5 months.

That 70 percent uptake rate tells two stories at once. First, that the fee works as a revenue mechanism — the government is collecting north of $20 billion from a single visa category. Second, that the system has effectively split into two tiers: those who can pay, and those who cannot.

Rural hospitals and school districts overwhelmingly fall into the second category.

## Why This Matters to Indian Americans

Indian-origin physicians are the backbone of rural American healthcare. According to the American Association of Physicians of Indian Origin, roughly 20 percent of all physicians in the United States are of Indian descent, and a disproportionate share serve in medically underserved areas — the exact communities Collins and Murkowski represent.

The same pattern holds, to a lesser degree, in education. Indian-trained math and science teachers have been recruited through H-1B programs to fill gaps in districts that cannot attract American graduates.

If the fee waiver push gains traction, it would create the first formal carve-out in the $100,000 regime — a crack in a wall that tech companies, consulting firms, and immigration attorneys have been trying to breach since September.

## What Happens Next

Mullin's hearing was an appropriations session, not a rulemaking. No fee waiver was announced. But the "case-by-case" language matters because it signals internal DHS flexibility without requiring Congressional action.

For Indian professionals in healthcare and education, the message is cautious but real: the administration is listening to the senators who represent the communities that need you most. Whether that translates into formal policy or remains a hearing-room concession is the question that will define the next few months.

The $100,000 fee was built for Infosys and Google. It was not built for a 25-bed hospital in rural Maine or a one-room school in the Alaskan bush. The senators who made that case on Tuesday may have just given DHS the political cover to draw that distinction."""

art1_sources = [
    {"name": "IANS", "url": "https://ianslive.in/lawmakers-seek-h-1b-relief-for-foreign-teachers--20260603064203"},
    {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100-000-h-1b-visa-fees"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/over-2-lakh-applicants-paid-for-faster-h-1b-visa-processing-in-fy2026-dhs-says/article69648210.ece"}
]

# ─────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────

art2_headline = "Your Visa Was Approved. The Screening Never Stopped. What Every Indian Traveler Needs to Know This Summer."

art2_subheadline = "The US Embassy in India has issued an unusual public reminder that visa vetting continues after approval — landing in the middle of a summer crunch where some consulates are booking slots 10 months out."

art2_body = """Most visa applicants assume the hard part is getting approved. The interview, the documentation, the wait. Once the stamp lands in your passport, you exhale. The US Embassy in India wants you to stop exhaling.

In a notice posted this week, the Embassy stated plainly that visa screening and vetting continue even after a visa has been granted. "We use all available information in our visa screening and vetting to identify visa applicants who are inadmissible to the United States, including those who pose a threat to U.S. national security," the statement reads.

The statement was not triggered by any specific incident involving Indian nationals. India remains off the 2025 travel ban list, which restricts nationals from 12 countries entirely and imposes partial limits on seven others. But the Embassy's decision to publicize what has technically always been true — that visa approval is not the final word — carries a sharper edge in 2026.

## Why Now

The timing is not coincidental. Three pressures are converging on Indian visa applicants this summer.

First, the USTravelDocs portal — the digital front door for visa applications, fee payments, and interview scheduling — has been plagued by technical outages for weeks. Applicants across India, Australia, Japan, Germany, and Switzerland have reported errors in scheduling, payment processing, and account access. The Consular Electronic Application Center, used for immigrant visas, has faced its own intermittent failures.

Second, demand is surging. The US processed a record 1.4 million visa applications in India in 2024, and the 2026 numbers are trending higher. The summer travel season and the FIFA World Cup 2026 are compounding an already strained system.

Third, wait times across Indian consulates vary dramatically — and some are brutal. According to State Department data and consular tracking services, here is what applicants are facing for B1/B2 visitor visa interviews as of spring 2026:

Chennai leads at roughly three months. Kolkata sits around six and a half months. New Delhi ranges from five and a half to seven months. Hyderabad runs six and a half to eight months. And Mumbai — India's highest-demand city — is booking nine months out.

Work visas (H, L, O categories) move faster, typically around one month. Student visas can sometimes be scheduled within two weeks. But the bulk of Indian applicants — parents visiting children, tourists, and business travelers — are in the B1/B2 queue where the wait is longest.

## The Consulate Shopping Game

A quiet industry has sprung up around what immigration consultants call "consulate shopping." Large employers are routing employees to cities with shorter lines, even if it means booking domestic flights. Travel management firms report a spike in one-day turnaround itineraries — fly to Chennai for the interview, fly home the same evening.

The Kolkata consulate has gone further. In late May, it launched a pilot that introduces four new B1/B2 sub-categories: Business Professionals, Parents Visiting Children with Legal Status, General Tourism and Travel, and Recent Visa Refusal. The sub-categories appear to be an experiment in triage — sorting applicants by profile rather than forcing everyone through the same queue.

The State Department has also announced plans to add 100 consular officers in India during 2026, a significant expansion that acknowledges the bottleneck is a staffing problem, not just a demand problem.

## What This Means for the Diaspora

For Indian Americans sponsoring parents for a summer visit, the math is sobering. A B1/B2 appointment booked today in Mumbai would not come up until March 2027. Even the fastest option, Chennai, pushes into September 2026.

The Embassy's reminder about ongoing screening adds another layer of uncertainty. A visa in hand no longer guarantees smooth entry. Officers at ports of entry have always had discretion to turn travelers away, but the public statement suggests a more active posture — one where post-approval vetting is not merely possible but routine.

The practical advice is unglamorous but necessary. Apply early. Monitor appointment portals daily, especially late at night when canceled slots reappear. Consider applying through a consulate outside your home city if the wait is shorter. Keep your documentation current and consistent with what you submitted. And do not assume that the visa stamp in your passport is the last conversation you will have with US immigration.

The system is not broken in a way that prevents travel. It is broken in a way that punishes anyone who is not planning months ahead. For a diaspora community whose family ties depend on the B1/B2 pipeline, that is not an abstraction — it is the difference between your parents making it for Diwali or missing it entirely."""

art2_sources = [
    {"name": "The Indian Eye", "url": "https://theindianeye.com/us-embassy-in-india-warns-visa-holders-that-visa-screening-continues-even-after-visa-is-granted/"},
    {"name": "ainvest.com", "url": "https://www.ainvest.com/news/us-visa-website-outages-cause-delays-worldwide-amid-summer-travel-season-and-fifa-world-cup-2026-demand/"},
    {"name": "VisaHQ", "url": "https://www.visahq.com/united-states/"},
    {"name": "travelobiz", "url": "https://travelobiz.com/us-consulate-in-kolkata-pilots-3-new-b1-b2-visa-measures-for-applicants/"}
]

# ─────────────────────────────────────────────
# Build and insert
# ─────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("h1b-fee-waiver-rural-doctors-teachers-mullin-senate"),
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "Indian-origin physicians make up roughly 20% of US doctors, with a disproportionate share serving in medically underserved rural areas — exactly the communities where senators are now pushing for $100K fee waivers. Indian educators recruited for H-1B roles in remote school districts would also benefit.",
        "tags": ["h1b", "uscis", "immigration", "rural-healthcare", "teachers", "fee-waiver", "mullin"],
        "urgency": "high",
        "sources": json.dumps(art1_sources),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg/3840px-DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("us-embassy-india-visa-screening-summer-consulate-wait"),
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "Indian Americans sponsoring parents and family for visits face 3-to-9-month consulate waits depending on city, compounded by ongoing post-approval screening and portal outages — making summer 2026 planning critical for the B1/B2 pipeline the diaspora relies on.",
        "tags": ["visa", "india-consulate", "b1b2", "travel", "uscis", "summer-travel", "screening"],
        "urgency": "medium",
        "sources": json.dumps(art2_sources),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
