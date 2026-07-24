#!/usr/bin/env python3
"""Immigration writer — 2026-06-27 21:00 PT run"""
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


# ─────────────────────────────────────────────
# ARTICLE 1: Social media vetting at consulates
# ─────────────────────────────────────────────

article1_body = """The State Department calls it an "online presence review." For Indian professionals trying to get an H-1B visa stamp at a U.S. consulate, it feels more like a digital strip-search — one that has added months to what used to be a routine process.

Since December 15, 2025, every H-1B applicant and their H-4 dependents have been required to set all social media profiles to "public" before their consular interview. Officers now review posts, comments, photos, affiliations, and activity across Facebook, Instagram, LinkedIn, X, TikTok, and YouTube as standard national security vetting. The requirement previously applied only to students and exchange visitors. Its expansion to the work-visa population — the single largest category of which is Indian — has triggered a bottleneck that shows no sign of clearing.

## The Queue That Keeps Growing

The numbers are stark. Employment-based visa appointments at India's five consular posts now carry wait times of 75 to more than 125 days, according to immigration law firm Fragomen. Chennai sits at 75 days. Hyderabad, 93. Mumbai, 88. New Delhi, 100. Kolkata — once a workaround for applicants willing to travel to a quieter post — has surged to 126 days.

Demand for U.S. visas from India has risen roughly 80 percent over the past five years, yet the State Department has added no new consular staff at its India mission. The additional time required for social media reviews has compounded an already strained system. Beginning in December 2025, consulates mass-rescheduled H-1B and H-4 interviews originally set for mid-December into March, April, and even June 2026. Applicants received little warning and were allowed only one free reschedule. Miss that slot, and the MRV fee — $205 for work visas — has to be repaid.

## The ESTA Trap

Buried in the fine print is a consequence most applicants discover too late. Applications that cannot be approved on the spot are "temporarily denied" while the online presence review is completed. That temporary refusal — even if the visa is ultimately granted — permanently renders the applicant ineligible for the Electronic System for Travel Authorization, the visa waiver that allows quick trips to the U.S. from eligible countries.

For Indian nationals, who are not eligible for ESTA under the Visa Waiver Program anyway, this is a moot point. But for H-1B holders who are citizens of ESTA-eligible countries such as the United Kingdom, Germany, or Japan, the policy creates a lasting mark on their immigration record. Immigration attorneys have flagged the disparity: a routine security review can produce a permanent blemish with no appeal.

## What to Clean Up Before You Fly

Immigration lawyers are now advising clients to audit their social media months before any planned travel for stamping. The guidance is specific: ensure employment history, job titles, and affiliations visible on LinkedIn and other platforms match the DS-160 application and petition materials exactly. Remove or privatize content that could be misread as political advocacy or affiliation with groups on U.S. sanctions lists. Even old, forgotten accounts can surface in a review.

The practical advice from firms like Reddy Neumann Brown is blunter: do not travel to India for visa stamping unless you absolutely must. If your current visa stamp is expired but your I-797 petition approval is valid, you can continue working in the U.S. — you just cannot leave and re-enter without a fresh stamp. Anyone who does travel risks being stranded abroad for four to six months while their interview and review are processed. Few employers can hold a role open that long, and many cannot legally allow remote work from India due to export-control, payroll, and tax constraints.

## A System Under Strain

The State Department frames the expanded vetting as essential national security. "Every visa adjudication is a national security decision," its December announcement read. Applicants must not "intend to harm Americans and our national interests."

No one disputes the right to screen. But immigration attorneys argue the execution is punishing the compliant. The 1.4 million visas issued to Indian nationals in 2025 represent the largest single-country demand on the U.S. consular network. Adding a labor-intensive review layer without adding staff was always going to produce exactly what it has: a system buckling under its own ambition.

For the H-1B worker weighing a trip home for a wedding, a family emergency, or a routine holiday, the calculation has changed. The visa stamp that used to take two weeks now takes two quarters. And the social media profiles that once felt private are now part of the application file."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Instagram Is Now Part of Your Visa Application. Indian Consulates Are Buckling Under the Load",
    "subheadline": "Six months after the State Department expanded social media vetting to H-1B workers, visa stamping wait times at India's five consulates have ballooned to 75–125 days — and the backlog is still growing.",
    "slug": make_slug("social-media-vetting-h1b-india-consulate-wait-times-backlog"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Every H-1B holder who needs to travel to India for stamping faces a 75–125 day wait at consulates, turning a two-week trip into a three-month ordeal that can cost them their job.",
    "tags": ["h1b", "visa-stamping", "social-media-vetting", "consulate", "uscis", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "U.S. State Department", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/visanews/expanded-screening-h1b-h4.html"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-us-consulates-in-india.html"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/state-dept-adds-social-media-review-h1b-h4-visa-applicants"},
        {"name": "Duane Morris LLP", "url": "https://www.duanemorris.com/alerts/state_department_expands_social_media_screening_h1b_h4_applicants_1225.html"},
        {"name": "Reddy Neumann Brown PC", "url": "https://rnlawgroup.com/blog/stop-holiday-travel-for-stamping/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_06.jpg/1280px-Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_06.jpg",
    "image_caption": "Visa applicants outside the U.S. Embassy in New Delhi, July 2023",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ──────────────────────────────────────────────────
# ARTICLE 2: Ambassador Gor says H-1B not targeting India
# ──────────────────────────────────────────────────

article2_body = """Sergio Gor, the United States Ambassador to India, wants Indians to stop worrying about H-1B visas. The review of the programme, he told Outlook Business this week, is "part of a broader overhaul of America's immigration system" and should not be "viewed as being directed at any particular country."

It is a polished diplomatic line, delivered at a moment when both governments are trying to finalize a bilateral trade agreement and keep the relationship warm ahead of a potential Trump visit to New Delhi. As reassurances go, it is professional. As analysis, it collides with every available data point.

## The Numbers India Cannot Ignore

Indians received 71 percent of all H-1B visas approved last year, according to USCIS data. No other country comes close. When the Trump administration imposed a $100,000 filing fee on new H-1B petitions last September, the policy was facially neutral — it applied to every nationality. In practice, it hit Indian-heavy IT consulting firms hardest, because those firms file the most petitions and operate on margin structures that cannot absorb a six-figure per-worker surcharge.

The fallout has already arrived. India's six largest IT services companies — TCS, Infosys, Cognizant, HCL Technologies, Wipro, and Tech Mahindra — received 11,041 H-1B approvals in the fiscal year ending March 2026, a 40 percent decline from the prior year's 18,469. TCS absorbed the steepest drop, falling by more than 3,200 approvals to 2,885. Infosys, the only firm to gain, received 3,195 — a reprieve, not a trend.

## Every Policy Change Has an Indian Address

The $100,000 fee was the opening salvo, but the cascade that followed has been broader and sharper. The weighted lottery system, effective for the FY2027 cap season, restructured H-1B selection to prioritize higher-paid workers. That sounds meritocratic in theory. In practice, it disadvantages the mid-tier salary placements that Indian outsourcing firms specialize in — the $80,000-to-$110,000 software engineers placed at client sites across the Midwest and South.

The social media screening mandate, introduced in December 2025, requires all H-1B and H-4 applicants to make their profiles public for consular review. Wait times at Indian consulates have since ballooned to 75–125 days for employment-based visa appointments. The new USCIS signature rule taking effect July 10 adds another procedural tripwire — a deficient signature, previously a delay, will now trigger a denial. The proposed four-year cap on F-1 student visas targets the pipeline of Indian STEM graduates who are the primary feedstock for future H-1B petitions.

None of these policies names India. All of them, by the weight of demography and industry structure, land on Indians first and hardest.

## The Diplomatic Context

Gor's remarks do not exist in a vacuum. They arrive as Trade Representative Jamieson Greer and Commerce Minister Piyush Goyal are in the final stages of negotiating a bilateral trade agreement — a deal both sides want before the end of 2026. Immigration is the Indian government's most sensitive domestic constituency on the U.S. relationship. Every H-1B restriction produces headlines in Indian media and pressure on New Delhi to extract concessions.

The Ambassador's framing — that the U.S. is simply reforming an immigration system mismanaged by prior administrations, and that India's own stance against illegal migration aligns with Trump's — is tailored for that audience. It separates the legal immigration crackdown from India's concerns by routing the conversation through shared values on border enforcement.

## What the Diaspora Hears

For the Indian professional in Sunnyvale or Plano — the one whose EB-2 green card wait has stretched past a decade, whose spouse's H-4 work permit may be rescinded, whose company just paid $100,000 to renew their H-1B petition — the Ambassador's reassurance rings hollow. The question was never whether the policy was *aimed* at India. It was whether the policy *lands* on India.

By that measure, the answer is unambiguous. Indian nationals filed 72.3 percent of H-1B registrations in the FY2026 lottery. They hold the longest employment-based green card backlog of any country — EB-2 India is currently marked "unavailable" in the July 2026 visa bulletin. They are the most frequent visitors to U.S. consulates in the world's largest democracy, where appointment wait times have tripled.

A policy can be universal in design and targeted in effect. That distinction matters more to the person standing in line at the Hyderabad consulate than to the person delivering remarks about it from the embassy in Chanakyapuri."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "'H-1B Isn't Targeting India,' Says America's Envoy. The Numbers Disagree",
    "subheadline": "Ambassador Sergio Gor calls the H-1B overhaul a system-wide reform. Indian IT firms just lost 40 percent of their approvals, EB-2 India is marked 'unavailable,' and consulate wait times have tripled.",
    "slug": make_slug("ambassador-gor-h1b-not-targeting-india-data-disagrees"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The ambassador's reassurance matters less than the data: Indians hold 71% of H-1B approvals, face the longest green card backlogs, and absorb the heaviest impact of every policy change — regardless of intent.",
    "tags": ["h1b", "india-us-relations", "sergio-gor", "immigration-policy", "indian-it"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/final-hurdles-remain-h-1b-isnt-targeting-india-says-us-ambassador-sergio-gor"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/top-it-firms-h-1b-visas-slump-40-tcs-worst-hit-while-infosys-gains-11717401234567.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/china/chinas-new-k-visa-beckons-foreign-tech-talent-us-hikes-h-1b-fee-2025-10-01/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sergio_Gor%2C_official_portrait_%282025%29.jpg",
    "image_caption": "U.S. Ambassador to India Sergio Gor, official portrait, 2025",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}


# ─────────────────
# Insert articles
# ─────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
