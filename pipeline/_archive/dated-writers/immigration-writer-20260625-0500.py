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

A1_BODY = """The Trump administration is one signature away from killing a safety net that has quietly kept hundreds of thousands of foreign workers employed through America's permanent processing delays. The White House Office of Management and Budget is now reviewing a final rule that would permanently end the automatic extension of employment authorization documents — the work permits known as EADs — for people who file to renew them. Once OMB clears it and the rule is published, the change moves from temporary to locked in.

For the Indian diaspora, this is not an abstract regulatory footnote. It is the difference between a spouse keeping her job and being forced to stop working overnight because a government office is slow.

## What the rule actually does

Until late last year, an immigrant who filed a timely EAD renewal automatically kept the right to work — for up to 540 days — while USCIS processed the paperwork. The logic was simple: the government's own backlogs should not cost a lawfully present worker their paycheck. That cushion was built up over two administrations, expanded to 540 days in 2022 to absorb pandemic-era delays.

In October 2025, DHS issued an interim final rule scrapping that automatic extension for most categories, effective for renewals filed on or after October 30. The justification, per USCIS Director Joseph Edlow, was "robust alien screening and vetting" — the idea that the government should re-check someone's background before re-authorizing their work, rather than letting authorization roll over automatically. "Working in the United States is a privilege, not a right," Edlow said at the time.

The rule now at OMB converts that interim measure into a permanent one. An earlier interim rule eliminating the grace period for pending renewals already took effect; this finalizes the architecture.

## Why Indian families are squarely in the crosshairs

The group most exposed here is one Indians know intimately: H-4 EAD holders — overwhelmingly the spouses of H-1B workers, and overwhelmingly Indian women. An estimated 90,000-plus H-4 work permits are in circulation, the large majority held by Indian nationals stuck in the decade-plus EB-2 and EB-3 green card backlog. A lawsuit brought by spouses of H-1B workers in the Central District of California is already challenging the broader rollback.

Here is the trap. An H-4 EAD is tied to the spouse's underlying status and must be renewed periodically. With automatic extension gone, the worker's authorization simply ends on the printed expiration date — even if a renewal has been sitting in a USCIS queue for months. The current I-765 work-permit processing time runs anywhere from under two months to nearly 20 months depending on the case. If the renewal lands on the slow end, the worker stops working, loses income, and may have to be taken off payroll by an employer that cannot legally keep them.

The same exposure hits adjustment-of-status applicants — Indians who filed I-485 while waiting out the backlog and rely on an EAD to work in the interim — as well as certain other categories. STEM OPT students and some statutory groups retain protections, but the broad middle of the diaspora workforce does not.

## What to do before the rule bites

The only real defense is time. USCIS allows EAD renewals to be filed up to 180 days before expiry, and immigration attorneys are now uniformly advising clients to file at the earliest possible moment rather than waiting. The math is unforgiving: if processing takes ten months and you file four months out, you have engineered your own six-month gap in work authorization.

Employers with large Indian H-4 and adjustment-of-status populations face their own compliance headache. Once the rule is final, a receipt notice paired with an expired EAD is no longer valid proof of work authorization — meaning HR teams must track expiration dates far more aggressively or risk I-9 violations.

## The bigger pattern

The EAD change does not stand alone. It sits alongside the end of the F-1 "duration of status" framework, expanded social-media vetting for H-1B and H-4 applicants, and a visa-stamping interview-waiver program that has been shut to work-visa holders. The connective tissue is a deliberate shift from convenience to friction — more touchpoints, more re-vetting, more chances for a lawfully present worker to fall out of status through no fault of their own.

For a community whose green card wait is measured in decades, the message is blunt: the gaps between renewals are no longer cushioned, and the cost of a government delay now lands on the immigrant, not the agency."""

A2_BODY = """The most dangerous H-1B compliance risk of 2026 is not the $100,000 fee a Boston judge just struck down, nor the wage-weighted lottery, nor a bill stuck in Congress. It is something far more banal: an H-1B worker quietly moving to a new city to work remotely, and nobody filing the paperwork that move legally requires.

For the Indian professionals who make up roughly three-quarters of the H-1B workforce, the post-pandemic embrace of remote and hybrid work has opened a compliance trap that can detonate years later — at the worst possible moment, during a green card or extension filing.

## The rule almost nobody follows

Here is the mechanics most workers never learn until it is too late. Every location where an H-1B employee works — including a home office — must be listed on a Labor Condition Application (LCA) and covered by the petition. The trigger is the Metropolitan Statistical Area, or MSA.

Move within the same MSA, and you may not need an amended petition — but the employer must still post an LCA notice at the new address for ten business days and update the Public Access File. Move to a different MSA, and the employer must file an amended H-1B petition with a new LCA *before* the employee starts working from the new location, so the case reflects the correct local prevailing wage.

In practice, an H-1B worker who relocates from, say, Austin to the Bay Area to work remotely — without telling the immigration team — is out of status the day they start working from the new home. And because employers often only discover the move at the next extension filing, the worker can be out of compliance for months or years before anyone notices.

## Why this is getting more dangerous now

Two things have changed. First, under the 2025 H-1B Modernization Rule, USCIS can conduct unannounced site visits directly at home offices. The agency's Fraud Detection and National Security (FDNS) directorate sends officers — often with no warning — to verify that the employee lives at the listed address, does the job described in the petition, earns the stated wage, and that the employer relationship is real. Many of these are random compliance checks, not fraud investigations, but the consequences of a discrepancy are the same.

Second, detection has gone digital. The government now cross-references state tax filings against the residential addresses on record, and uses biometric appointments to catch mismatches. A worker who moved and kept quiet leaves a paper trail in their own tax return.

## What a single missed amendment can cost

The numbers are sobering. One documented case involved an engineer who relocated to San Francisco without an updated LCA: she had been underpaid by roughly \\$56,514 a year relative to the San Francisco prevailing wage, exposing her employer to about \\$113,028 in backpay liability — and putting her own extension and future green card at risk. Willful violations carry penalties up to \\$67,367 per violation plus backpay, and a three-year debarment from the program.

For an Indian worker years deep into the EB-2 or EB-3 backlog, the real terror is not the fine. It is that a compliance gap can surface during an I-140 or I-485 adjudication and jeopardize the green card they have waited a decade for.

## The diaspora's quiet exposure

This matters acutely for Indians for a structural reason: they are the most likely to be on H-1B for the longest time, because the green card queue forces them to stay in nonimmigrant status far longer than any other nationality. The longer you are on H-1B, the more life happens — a spouse's job in another city, a move closer to family, a cheaper housing market — and every one of those moves is, in immigration terms, an event.

The practical advice from attorneys is uncomfortable but clear: treat every address change as an immigration event, build an immigration review into any remote-work approval, and audit payroll addresses against immigration records. If USCIS knocks, an H-1B worker should answer honestly, confirm their identity and role, and immediately loop in their employer's designated representative or counsel.

The remote-work revolution made geography feel irrelevant. For H-1B Indians, it never was."""

A3_BODY = """For two decades, the quiet luxury of the Indian H-1B holder's life in America was the dropbox. Visa expired? Renew it by courier from Hyderabad or Mumbai, skip the consular interview, fly back to the US in a week or two. That convenience is now gone — and the way it disappeared tells you everything about where US visa policy is heading.

## The door is shut, not narrowed

Earlier reporting framed the changes as a tightening: the interview-waiver window shrinking from 48 months to 12, the requirement that you renew in the same visa class. That was the 2025 story. The 2026 reality is harsher. Under State Department guidance that superseded all prior rules, the interview waiver — the formal name for the dropbox — has been reduced to an extremely narrow set of applicants, and for H-1B holders, the door is completely shut.

It does not matter whether your H-1B visa is still valid, expired last month, or was previously issued at the very consulate where you are applying. The interview waiver simply does not exist for the H-1B category anymore. The same is true for L-1, O-1, E-3, and crucially for families, the dependent H-4 and L-2 categories. Student visas — F, M, J and their dependents — are out too.

What survives is a short list: diplomatic and official visas, certain B-1/B-2 tourist and business renewals within 12 months, a newly added carve-out for H-2A agricultural workers, and some C-3 transit cases. The working diaspora is not on it.

## The detail that hits families hardest

Buried in the changes is an elimination that lands directly on Indian families: the age-based exemptions are gone. Previously, children under 14 and applicants over 79 could skip the in-person interview entirely. No longer. A family renewing H-4 visas for young children must now bring those children before a consular officer in person, like every other applicant — when appointments are already being scheduled months out.

For an NRI family planning a summer trip to India, this reshapes the calculus. A routine visit home now means every member, toddlers included, needs an in-person slot at a consulate running a backlog. Layered on top is mandatory social-media vetting for H-1B and H-4 applicants, introduced in late 2025, which itself triggered widespread interview rescheduling, pushing dates into the middle of 2026.

## The $750 mirage

Into this squeeze stepped what looked like relief. From July 1 through December 31, 2026, the State Department is piloting a program letting applicants pay an extra \\$750 — on top of the standard \\$185 fee — to secure an interview appointment within ten business days. Nearly four times the base fee for the privilege of jumping the queue.

Read the fine print, though, and the relief evaporates for exactly the people who need it most. The expedite applies to B-1/B-2 applicants — tourists and business visitors. It does not rescue an H-1B holder stranded in India waiting for a stamping appointment. And it guarantees only a faster interview, not a faster decision: background checks, administrative processing, and the final call all proceed at their usual pace. The list of participating posts in India has not even been confirmed.

So the diaspora faces a split screen. A relative coming to visit can buy speed. The H-1B engineer who flew home for a wedding and now cannot get a stamping slot cannot — and an H-1B stamp in India can now take around four months, with the third-country "interview shopping" escape route in places like Canada or Mexico effectively bolted shut by the same same-country-of-residence rules.

## Why this is more than an inconvenience

The cumulative effect changes how Indians on work visas live. The rational response to a four-month stamping wait and no dropbox is simply to not leave the United States — to skip the trip home, the family wedding, the ailing parent — because re-entry is no longer a sure thing on any predictable timeline.

That is a quiet tax on the diaspora that does not show up in any fee schedule: years of deferred visits, missed milestones, and the low-grade anxiety of being one expired stamp away from being stuck on the wrong side of the ocean. For a community that prides itself on staying connected to home, the closing of the dropbox is less a paperwork change than a redrawing of the line between here and there."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Work-Permit Safety Net Is About to Vanish. 90,000 Indian Spouses Are First in Line",
        "subheadline": "A final rule now at the White House would permanently kill the automatic EAD extension. For H-4 and green-card-backlog Indians, a slow USCIS queue could mean losing the right to work overnight.",
        "slug": make_slug("ead-automatic-extension-final-rule-omb-h4-spouses-indians-work-permit"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The end of automatic EAD extensions hits H-4 spouses and adjustment-of-status applicants — overwhelmingly Indians stuck in the decade-long green card backlog — who can now lose work authorization the moment their permit expires if USCIS is slow to renew it.",
        "tags": ["ead", "h4", "uscis", "work-permit", "green-card-backlog", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — DHS Advances Rule Nixing Automatic Renewal of Work Permits", "url": "https://news.bloomberglaw.com/daily-labor-report/dhs-advances-rule-nixing-automatic-renewal-of-work-permits"},
            {"name": "USCIS — DHS Ends Automatic Extension of Employment Authorization", "url": "https://www.uscis.gov/newsroom/news-releases/dhs-ends-automatic-extension-of-employment-authorization"},
            {"name": "Perkins Coie — DHS Ends Automatic Work Authorization Extensions", "url": "https://www.perkinscoie.com/insights/update/dhs-ends-automatic-work-authorization-extensions"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8372664/pexels-photo-8372664.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Immigration paperwork and a passport on a desk, representing EAD work-permit renewals",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": A1_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Move That Quietly Voids Your Status: Working Remotely From the Wrong City",
        "subheadline": "Relocating to work from home can put an H-1B worker out of status the day they start — and USCIS can now show up unannounced at the home office to check. Indians, on the visa longest, are the most exposed.",
        "slug": make_slug("h1b-remote-work-lca-amendment-fdns-home-office-site-visit-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold roughly three-quarters of H-1B visas and stay on them longest because of the green card backlog, making them the most likely to relocate for remote work — and the most likely to trigger an LCA-amendment compliance gap that can surface and derail a green card filing years later.",
        "tags": ["h1b", "remote-work", "lca", "uscis", "fdns", "compliance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "H-1B Remote Work Compliance: Locations, Amendments, and Risk (LinkedIn, Jun 22 2026)", "url": "https://www.linkedin.com/pulse/h-1b-remote-work-compliance-locations-amendments-risk-tomas-mendoza"},
            {"name": "Reddy Neumann Brown PC — H-1B Home Office Site Visits", "url": "https://www.rnlawgroup.com/h-1b-home-office-site-visits-what-employees-should-do-when-uscis-knocks-on-the-door/"},
            {"name": "Mondaq — Immigration Compliance For Remote Work", "url": "https://www.mondaq.com/unitedstates/work-visas/immigration-compliance-for-remote-work"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5387233/pexels-photo-5387233.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A professional working from a home office, where USCIS can now conduct unannounced H-1B site visits",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": A2_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Dropbox Is Dead for H-1B Indians. Even Toddlers Now Need an Interview",
        "subheadline": "The visa interview-waiver program is fully shut to work-visa holders, and the age waivers for children and the elderly are gone. The new $750 fast-track rescues tourists, not the H-1B engineer stranded in India.",
        "slug": make_slug("us-visa-interview-waiver-dropbox-shut-h1b-h4-age-waivers-removed-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian H-1B and H-4 families, the end of dropbox renewals, the removal of child and elderly interview waivers, and four-month stamping waits mean a trip home to India now risks getting stranded — quietly discouraging visits to family altogether.",
        "tags": ["visa-stamping", "dropbox", "interview-waiver", "h1b", "h4", "consulate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge — H-1B Dropbox Eligibility Changes 2026", "url": "https://www.visaverge.com/h1b/h-1b-dropbox-eligibility-changes-2026/"},
            {"name": "Ogletree — Changes to U.S. Mission India's Nonimmigrant Visa Processing", "url": "https://ogletree.com/insights-resources/blog-posts/changes-to-u-s-mission-indias-nonimmigrant-visa-processing/"},
            {"name": "Outlook Traveller — US To Offer Faster Visa Appointments Within 10 Days For An Additional Fee", "url": "https://www.outlooktraveller.com/destinations/international/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7235804/pexels-photo-7235804.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and US visa application, as interview-waiver dropbox eligibility narrows for Indian applicants",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": A3_BODY
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words={wc} | {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
