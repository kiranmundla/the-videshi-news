#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Months Left in the Fiscal Year and India's EB-2 Green Cards Are Already Gone",
        "subheadline": "The State Department has exhausted every last FY2026 EB-2 visa allocated to Indian nationals. Final Action Dates have cratered back to September 2013 — and the queue won't move again until October.",
        "slug": make_slug("eb2-india-quota-exhausted-fy2026-october-freeze"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indian tech professionals on H-1B visas with pending I-485 adjustment-of-status applications are now stuck in administrative limbo until October 1, 2026. For anyone who filed for an EB-2 green card in the last decade, the freeze means another four months of uncertainty — no approvals, no movement, no exceptions.",
        "tags": ["eb-2", "green-card", "visa-bulletin", "uscis", "backlog", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/"},
            {"name": "VisaVerge", "url": "https://visaverge.com/"},
            {"name": "UnitedSewa", "url": "https://unitedsewa.com/news/india-eb2-visa-limit-exhausted-for-fy2026/"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/tag/US-Visa/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7009478/pexels-photo-7009478.jpeg",
        "body": """The numbers are in, and they are zero. The U.S. State Department announced on May 26 that every EB-2 immigrant visa allocated to India-chargeable applicants for fiscal year 2026 has been used. Not a single green card in this category will be issued to an Indian national until the fiscal year resets on October 1.

The timing is brutal. Fiscal year 2026 still has four months left on the clock. For the agency to burn through an entire year's allocation by late May tells you everything about the scale of Indian demand pressing against a per-country cap that was designed for a different era.

## The Boomerang Nobody Wanted

The freeze did not come out of nowhere — but the way it arrived is instructive.

Earlier this fiscal year, EB-2 India Final Action Dates had been advancing at a pace that raised eyebrows. From April 2013 in October 2025, the cutoff marched forward to July 2014 by April 2026. Immigration attorneys noticed, and some were cautiously optimistic. They shouldn't have been.

The forward movement was artificial. The Trump administration's January 2025 suspension of immigrant visa processing for nationals of 75 countries — those deemed likely to use public assistance — had temporarily suppressed demand from Rest-of-World applicants. With fewer people in line globally, unused visa numbers spilled over to India's EB-2 queue. Dates moved forward because the competition thinned, not because Congress raised the cap.

Former Department of State official Charlie Oppenheim warned about exactly this scenario. "The movements are artificial and only based on the Administration's policy on visa processing for the 75 countries," he said. "Once it ends there has to be the boomerang effect."

The boomerang has landed. Final Action Dates for EB-2 India have now snapped back to September 2013 — erasing more than a year of apparent progress in a single correction.

## What This Means for Indian Professionals

The practical consequences are stark. USCIS cannot approve any pending I-485 adjustment-of-status applications in the EB-2 category for India-chargeable applicants until new visa numbers become available on October 1. U.S. consulates abroad cannot issue EB-2 immigrant visas to Indian nationals either. The pipeline is frozen at both ends.

This affects a population that skews heavily toward the Indian tech workforce in America — software engineers, data scientists, product managers, and researchers who have been waiting years (in many cases over a decade) for their priority date to become current. They remain on H-1B status, unable to change employers freely, unable to start businesses without visa complications, and unable to plan their lives with any certainty.

USCIS will continue to accept new EB-2 filings — you can still submit an I-485 if your priority date was current under the Dates for Filing chart before the freeze. But acceptance is not adjudication. Your application sits in the queue, consuming filing fees and attorney hours, while the government waits for the calendar to flip.

## The Structural Problem Remains

The per-country cap limits any single nationality to roughly 7% of the approximately 140,000 employment-based green cards issued annually. For India, which produces a disproportionate share of H-1B workers and STEM graduates, this arithmetic has created a backlog estimated at over a million applicants. At current issuance rates, some Indian professionals filed their initial PERM labor certifications before their children were born — and those children are now old enough to age out of derivative green card eligibility.

Congress has shown no appetite for legislative reform. The EAGLE Act and similar bills that would eliminate per-country caps have stalled repeatedly. The Fairness for High-Skilled Immigrants Act, reintroduced in various forms since 2011, remains stuck in committee.

## What October Brings — and What It Doesn't

When FY2027 opens on October 1, new visa numbers will become available and USCIS will resume adjudications. But the question is where the Final Action Date will land. If the 75-country ban remains in place, India may again see artificially advanced dates — only to face another mid-year exhaustion. If the ban is lifted, the restored global demand will push Indian dates backward further.

Either way, the fundamental mismatch between Indian demand and available supply is not going anywhere. The EB-2 freeze is not a bug in the system. It is the system working exactly as Congress designed it — which, for roughly 300,000 Indian families waiting in line, is the most damning part of all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Kolkata Is Running a Visa Experiment — and Indian Parents Are First in Line",
        "subheadline": "The U.S. Consulate in Kolkata has quietly launched pilot programs offering priority B1/B2 appointments for parents over 50, faster slots for business travelers, and mysterious new visa sub-categories that nobody can fully explain yet.",
        "slug": make_slug("kolkata-consulate-b1b2-pilot-parents-business-priority"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For NRI families who have spent years trying to bring aging parents to visit the United States, the Kolkata pilot represents the first concrete signal that the system might actually prioritize family ties. If the model works, it could spread to Mumbai, Hyderabad, and Chennai — the consulates where wait times currently stretch to 7 to 10 months.",
        "tags": ["b1-b2", "visa", "kolkata", "consulate", "parents", "family", "pilot"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travelobiz", "url": "https://travelobiz.com/us-consulate-kolkata-testing-new-b1-b2-visa-initiatives-india/"},
            {"name": "IMAD Travel", "url": "https://imadtravel.com/us-consulate-kolkata-b1-b2-visa-pilot-2026/"},
            {"name": "U.S. Consulate Kolkata (Twitter)", "url": "https://twitter.com/USAndKolkata"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "body": """Something unusual is happening at the U.S. Consulate General in Kolkata. While Mumbai wait times stretch past nine months and Hyderabad applicants queue for seven, Kolkata has begun running three pilot programs that could reshape how Indian families navigate the visitor visa system.

The programs — announced piecemeal through the consulate's social media posts in May — are not the product of new legislation or a policy directive from Washington. They appear to be a local initiative, branded under the "America First" rubric but operationally designed to move certain categories of applicants through the pipeline faster.

## Parents Get Priority

The headline measure is a priority appointment track for parents aged 50 and above who are visiting children legally residing in the United States. The consulate announced the program on May 7 with language that left little ambiguity about its intent: "Parents 50 years of age and over visiting children residing legally in the U.S. now benefit from priority appointment slots at Consulate Kolkata."

Eligibility criteria, as stated, include being over 50, having a child with legal U.S. residency, demonstrating a clear and verified travel purpose, and showing established family ties to the United States alongside strong ties to India. None of this creates a new visa category. The B1/B2 standards — temporary intent, proof of ties to home country, financial self-sufficiency — remain unchanged. What changes is the wait.

For the Indian diaspora, this hits a nerve that has been raw for years. The most common complaint in NRI WhatsApp groups is not about H-1B fees or green card backlogs — it's about getting elderly parents a visitor visa appointment before their health deteriorates further. A parent in Lucknow or Bhubaneswar who wants to see a grandchild in Houston should not need to wait nine months for an interview slot. Kolkata's pilot at least acknowledges that reality.

## Business Travelers Jump the Queue Too

On May 21, the consulate announced a second pilot targeting business travelers and genuine tourists. Framed as supporting "American economic priorities," the program offers shorter wait times for applicants whose travel strengthens U.S.-India commercial ties.

The beneficiary pool here is broader: frequent business travelers, individuals with strong financial records, tourists with established international travel histories, and applicants with legitimate short-term purposes. The consulate's social media explicitly invited applicants to "see if you qualify," though the specific qualifying criteria remain opaque.

For Indian IT professionals making client visits, procurement teams sourcing American equipment, or entrepreneurs attending trade shows, the faster track could eliminate a bottleneck that has pushed some business to virtual meetings or third-country routes. Whether this constitutes a meaningful shift or a marginal improvement depends entirely on how many slots Kolkata allocates to the priority queue.

## The Mystery Sub-Categories

The most intriguing development is also the least confirmed. Some applicants selecting Kolkata as their interview location have reported seeing four new sub-categories under the B1/B2 section during the application process:

- **Business Professionals** (conditions apply)
- **Parents Visiting Children with Legal Status** (conditions apply)
- **General Tourism & Travel** (for applicants with no past refusals)
- **Recent Visa Refusal (within 24 months)**

The sub-categories appeared in the online scheduling system, and screenshots have circulated on visa forums and social media. But the State Department has not issued any formal guidance explaining what the "conditions" entail or how selection into one sub-category versus another affects processing.

The fourth option — explicitly flagging applicants with a recent refusal — is particularly notable. Visa refusals under Section 214(b) are the most common outcome for Indian B1/B2 applicants, and the stigma of a prior denial makes subsequent applications significantly harder. Whether this sub-category creates a dedicated (and potentially slower) track for previously refused applicants, or simply collects data, is unclear.

## Kolkata Only — for Now

The pilot programs are limited to the Kolkata consulate. There is no confirmation that Mumbai, Hyderabad, Chennai, or New Delhi will adopt similar measures. Kolkata has historically been one of India's lower-volume consulates for U.S. visa processing, which may explain why it was chosen as the testing ground.

For applicants elsewhere in India, the calculus becomes: is it worth switching your interview location to Kolkata to access a priority track? Immigration advisors urge caution. Changing consulates affects appointment availability, travel logistics, and document handling. The priority slot does not change approval criteria — a faster interview does not mean a more lenient officer.

Still, the signal matters. If the Kolkata model demonstrates that triaging applicants by purpose and risk profile reduces wait times without compromising vetting standards, there is a credible path to expansion. And for the hundreds of thousands of Indian families caught in the visitor visa backlog, even a partial solution is worth watching."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
