#!/usr/bin/env python3
"""Immigration writer — July 1, 2026 9 PM run"""
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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────

art1_body = """The July 2026 Visa Bulletin reads like a slow-motion wall-off for Indian professionals chasing a green card. The Department of State has marked EB-2 India as "Unavailable" — the blunt bureaucratic shorthand for "no visa numbers left" — and it will stay that way through the end of the fiscal year on September 30. If you are an Indian national with an EB-2 petition, approved or pending, no green card can be issued in your category until at least October.

The EB-2 category covers advanced-degree professionals, persons of exceptional ability, and most National Interest Waiver cases. It is, by volume, where the largest chunk of Indian tech workers, engineers, and researchers sit in the green card queue. In the June bulletin, the final action date was September 1, 2013 — already a 13-year backlog. Now even that date has vanished, replaced by a "U" on both the Final Action and Dates for Filing charts.

## EB-1 Slides Backward, EB-3 Barely Moves

The damage is not confined to EB-2. EB-1 India, the category for multinational executives, outstanding researchers, and persons of extraordinary ability, retrogressed two months to October 15, 2022. In June it stood at December 15, 2022. The State Department has warned that further retrogression — or outright unavailability — could follow before the fiscal year closes.

EB-3 India offered the month's only forward movement, advancing half a month to January 1, 2014. For the roughly 200,000 Indian professionals waiting in this category, the date barely registers. The line stretches back more than twelve years.

EB-5 unreserved — the traditional investor green card path — is also unavailable for India through September 30. The set-aside categories for rural, high-unemployment, and infrastructure investments remain current, but those apply only to investors whose project structure qualifies under the specific designations.

## USCIS Doubles Down on Final Action Dates

Adding pressure, USCIS has confirmed that employment-based adjustment-of-status applicants must use the Final Action Dates chart in July — not the more favourable Dates for Filing chart. This has been the pattern since May 2026, and it narrows the filing window considerably.

The distinction matters. The Dates for Filing chart typically carries later cutoff dates, which means more people can submit I-485 applications. When USCIS restricts filers to Final Action Dates, applicants whose priority dates fall between the two charts lose the ability to file altogether. For EB-2 India, the question is moot this month — there is no date to hit.

## What Happens to Pending Cases

A pending I-485 is not denied because a category goes unavailable. USCIS simply cannot approve the green card until a visa number opens up. Employment Authorisation Documents, advance parole, H-1B portability, and AC21 job-change protections all continue to apply during the unavailability window.

But the uncertainty compounds. Families with children approaching age 21 face Child Status Protection Act calculations that grow more fraught with every month of retrogression. Spouses on H-4 EADs must renew their work permits without knowing when the underlying green card case will move. And anyone considering a job change must weigh AC21 portability against the risk of being in limbo for three more months at minimum.

## The October Reset

Visa numbers reset on October 1 when fiscal year 2027 begins. The State Department has indicated that the EB-2 India final action date may return to at least the September 1, 2013 level seen in May and June, though that depends on worldwide demand and the continued immigrant visa processing pause for certain nationalities.

The fundamental arithmetic has not changed. India's 7 per cent per-country cap on employment-based green cards forces hundreds of thousands of applicants to compete for roughly 9,800 visas per year across all EB categories. Rest-of-world demand is now consuming nearly all available numbers, leaving India and China to absorb whatever is left.

For an Indian engineer who filed a PERM application in 2012, the July bulletin means the wait is not twelve years and counting — it is twelve years and paused. The line does not move when the door is closed.

## What You Should Do Now

Check your exact priority date and the petition category attached to your approved or pending I-140. If you are in EB-2 India, confirm that your EAD and advance parole documents remain valid and plan renewals well in advance. If you hold an EB-1 petition with a priority date after October 15, 2022, prepare for additional retrogression before the fiscal year ends. And if your employer has discussed an EB-2 to EB-3 downgrade as a strategy, understand that EB-3 India at January 1, 2014 is still years behind most EB-2 priority dates — the move may not accelerate anything in the short term.

The August and September bulletins will determine whether EB-1 India joins EB-2 in full unavailability. Until then, the July bulletin delivers the clearest message the immigration system can send: the queue for Indian green cards is not just long. Parts of it are temporarily closed."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "EB-2 India Just Went Dark. No Green Cards Until October",
    "subheadline": "The July 2026 Visa Bulletin marks EB-2 India as 'Unavailable' through September 30, EB-1 India retrogresses two months, and EB-3 barely moves — leaving hundreds of thousands of Indian professionals frozen in place.",
    "slug": make_slug("eb2-india-unavailable-july-visa-bulletin-green-card"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Most Indian H-1B holders in tech and engineering sit in the EB-2 queue — this bulletin means zero green card approvals in that category for at least three months, extending wait times that already stretch past a decade.",
    "tags": ["eb-2", "visa-bulletin", "green-card-backlog", "uscis", "immigration", "eb-1", "eb-3", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/july-2026-visa-bulletin-eb-2-and-eb-5-india-unavailable-eb-1-india-retrogresses/"},
        {"name": "Capitol Immigration Law Group", "url": "https://www.cilawgroup.com/resources/blog/july-2026-visa-bulletin/"},
        {"name": "WR Immigration (Wolfsdorf)", "url": "https://www.wolfsdorf.com/eb-2-india-unavailable-through-september-30-2026/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/adjustment-of-status-filing-charts-from-the-visa-bulletin"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "An open passport with visa stamps — the kind of document Indian green card applicants know too well",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────

art2_body = """The date is July 1, 2026, and across the world's busiest immigration systems, a set of new rules have gone live simultaneously. The United States, the United Kingdom, Australia, and Japan — four of the top five destinations for Indian workers, students, and tourists — have each tightened their entry requirements in ways that, taken together, amount to a coordinated rethinking of who gets in, how fast, and at what cost.

No treaty binds these changes. No joint communiqué announced them. But the policy direction is unmistakable: pre-departure digital screening is replacing at-the-border discretion, visa fees are climbing, financial proof requirements are steepening, and biometric verification is becoming the norm rather than the exception.

## United Kingdom: The ETA Is Now Mandatory

The UK's Electronic Travel Authorisation system, fully enforced since February 25, is now a settled fact of British travel. Indian nationals travelling to the UK for short visits, business trips, or transit must hold an approved ETA before boarding. Airlines enforce a strict "no permission, no travel" policy — passengers without an approved ETA will not be allowed to check in.

The ETA costs £16 (set to rise to £20), is linked electronically to the traveller's passport, and is valid for two years or until the passport expires. The system is designed to screen travellers before they reach a British airport, not after. For Indians who once relied on relatively flexible visitor visa arrangements, the ETA adds a digital checkpoint to every trip.

Dual citizens face a particular wrinkle. The system requires a clear identity match between passport data and immigration records, and dual citizens travelling on a non-UK passport may be flagged by automated screening. The Home Office advises British-Indian dual nationals to travel on their British passport or carry a Certificate of Entitlement.

## Australia: Higher Bars for Students

Australia's 2026 immigration overhaul places international students under sharper financial scrutiny. The government has increased the minimum savings requirement for student visa applicants and tightened documentation standards. Students must now demonstrate full-cost funding capacity upfront, with reduced allowance for reliance on part-time employment.

For Indian families sending children to Australian universities — a pipeline that sends roughly 100,000 students annually — the new requirements mean larger bank balances, more thorough documentation, and less room for borderline applications.

Australia has also expanded its biometric collection programme. First-time visa applicants from most countries, including India, must submit fingerprints and facial images at visa application centres. The data feeds into an automated border clearance system that replaces manual passport stamping with digital identity verification.

## Japan: Digital Pre-Screening Arrives

Japan, which opened its doors wider to Indian tourists and workers in recent years, has begun implementing its own digital pre-travel authorisation for visa-exempt travellers. While Indian nationals still require a full visa for Japan, the digital infrastructure being built around the system signals a shift toward automated screening for all categories.

Japan's immigration agency has expanded its use of biometric gates at major airports, including Narita, Haneda, and Kansai. Indian travellers with valid visas who have registered biometric data can use expedited lanes, but the overall processing environment has become more structured and less flexible for last-minute changes.

## The United States: Tiered Pricing and Structural Pressure

The American immigration system, already the most complex of the four, has layered additional mechanisms into its 2026 enforcement cycle. A premium fast-track processing option has been introduced for B-1/B-2 tourist and business visas, allowing applicants to pay additional fees to accelerate interview scheduling — though approval is not guaranteed.

Student financial verification has intensified. International students applying for F-1 visas in 2026 must demonstrate stronger upfront financial capacity, with USCIS and consular officers scrutinising funding sources more closely. This affects the roughly 270,000 Indian students enrolled in American universities, many of whom rely on a combination of loans, family support, and part-time work.

The structural visa backlog continues to constrain employment-based immigration, particularly under the per-country quota system that limits India to 7 per cent of available green cards annually — the same cap applied to countries with a fraction of India's applicant pool.

## What This Means for the Diaspora

For the estimated 4.8 million Indian-Americans and the millions more who travel between India and the West for work, study, and family, the July 1 changes represent a qualitative shift. Travel between India's diaspora hubs — Silicon Valley, London, Sydney, Tokyo — now requires more advance planning, more documentation, and more fees than at any point in the past decade.

The common thread is digital gatekeeping. Each country is building or expanding systems that decide admissibility before the traveller reaches the border. The UK's ETA, Australia's biometric programme, Japan's pre-screening infrastructure, and America's expanded vetting all share the same logic: screen first, admit later.

For an Indian software engineer on an H-1B visa planning a conference in London, a holiday in Tokyo, and a visit to a child studying in Melbourne, the new landscape means four separate digital authorisation systems, four sets of financial documentation requirements, and four different fee structures — all layered on top of the underlying visa or work permit for each country.

The era of showing up at the airport with a valid passport and a return ticket is not over, but it is shrinking. July 1 marks the day the borders went digital in earnest."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Countries Tightened Their Borders on the Same Day. Indians Travel to All of Them",
    "subheadline": "The US, UK, Australia, and Japan — the top destinations for Indian workers, students, and tourists — all enforced stricter visa rules from July 1. The era of digital gatekeeping is here.",
    "slug": make_slug("global-visa-crackdown-july-1-digital-borders-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are uniquely exposed to this coordinated tightening — the US, UK, Australia, and Japan are the four countries where the Indian diaspora is largest, and every new digital checkpoint and fee increase hits NRI travellers, students, and workers simultaneously.",
    "tags": ["visa-crackdown", "digital-borders", "uk-eta", "australia-immigration", "japan-visa", "uscis", "immigration", "india-diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/united-states-aligns-with-united-kingdom-australia-japan-massive-visa-crackdown-july-1-2026/"},
        {"name": "Ohio University (Global Border Controls 2026)", "url": "https://www.ohio.edu/global-affairs/global-border-controls-2026"},
        {"name": "Lexology (Immigration Spotlight 2026)", "url": "https://www.lexology.com/library/detail.aspx?g=immigration-spotlight-2026"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Immigration_at_Punta_Cana_Airport.jpg/1280px-Immigration_at_Punta_Cana_Airport.jpg",
    "image_caption": "An immigration checkpoint at an international airport — the physical border that digital systems are replacing",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ── INSERT ─────────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
