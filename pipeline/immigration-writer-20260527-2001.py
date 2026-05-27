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
        "headline": "Your Tax Return Is Now a Tracking Device",
        "subheadline": "The IRS admitted to sharing 42,695 taxpayer addresses with ICE illegally. For Indian immigrants who file every return on time, their compliance has become a liability.",
        "slug": make_slug("irs-ice-tax-data-sharing-indian-immigrants-tracking"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders, OPT students, and green card applicants are among America's most diligent tax filers. The IRS-ICE data pipeline means the very records they file to demonstrate good faith could be used to locate and remove them. For the roughly 1 million Indians in various stages of the immigration queue, this creates an impossible bind: file taxes and risk exposure, or stop filing and violate federal law.",
        "tags": ["irs", "ice", "tax-data", "immigration", "h1b", "privacy", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Immigration Policy Tracking Project", "url": "https://immpolicytracking.org/policies/reported-dhs-asks-irs-for-information-about-undocumented-immigrants/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-spouses-sue-us-over-ending-automatic-work-permit-extensions"},
            {"name": "EFF - IRS-ICE Data Sharing", "url": "https://www.eff.org/deeplinks/2025/04/irs-ice-immigrant-data-sharing-agreement-betrays-data-privacy-and-taxpayers-trust"},
            {"name": "ProPublica", "url": "https://www.propublica.org/article/irs-building-system-share-taxpayer-data-ice"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6863251/pexels-photo-6863251.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For years, immigration lawyers gave their Indian clients the same advice: file your taxes, keep your records clean, stay in the system. It was the baseline proof of good faith — evidence that you played by the rules while waiting a decade or more for a green card that Congress never seemed to make available.

That advice now carries a footnote the size of a freight train.

## The Pipeline Nobody Voted For

In April 2025, the Department of Homeland Security and the IRS signed a memorandum of understanding that created a framework for sharing taxpayer data with Immigration and Customs Enforcement. The stated purpose was narrow: help ICE locate individuals with final removal orders who were under federal criminal investigation.

The reality was broader. DHS initially asked for data on 700,000 people. Within weeks, that request expanded to up to 7 million suspected undocumented immigrants. The IRS was asked to hand over home addresses, employer information, bank names, IP addresses, and Social Security or taxpayer-identification numbers.

IRS executives pushed back. They told DHS that the request likely violated the narrow criminal investigation exemptions in federal tax privacy law. The acting IRS commissioner, Melanie Krause, resigned in protest. Several senior officials followed her out the door.

The data started flowing anyway.

## 42,695 Violations

In February 2026, an IRS official filed a court declaration admitting what privacy advocates had feared. The agency had improperly shared the last known addresses of 42,695 taxpayers with ICE — people for whom DHS lacked sufficient information to positively identify. The MOU called for the IRS to only *confirm* addresses when DHS provided matching data. Instead, the IRS simply handed over addresses for thousands of people ICE could not independently verify.

ICE, for its part, stored the data on an unauthorized computer and cross-referenced it against its own databases — actions a federal judge in Massachusetts called "impermissible use."

Two federal courts are now pulling in opposite directions. A D.C. Circuit panel ruled in February 2026 that Section 6103 of the Internal Revenue Code *does* authorize the IRS to disclose address information upon a valid government request. A Massachusetts district court issued a preliminary injunction halting ICE's use of the data entirely, finding a "substantial likelihood" that the entire arrangement violated both the Administrative Procedure Act and federal tax law.

The contradictions are unresolved. The data has already been shared. And the IRS has not committed to notifying the people whose records were illegally disclosed.

## What This Means on an H-1B

Here is the dissonance that keeps Indian professionals awake at 2 a.m. in Sunnyvale and Jersey City: you are *required* to file U.S. taxes. Your W-2 income, your address, your employer's name and EIN — all of it goes to the IRS every April. You do this because the law demands it and because every immigration attorney you have ever consulted told you that tax compliance is the floor of credible good standing.

Now that floor has a trap door.

The current data-sharing arrangement is nominally targeted at people with final removal orders. But the legal infrastructure is in place for something much wider. ProPublica reported in July 2025 that the IRS was building an automated system to give ICE direct access to taxpayer address data — a pipeline that would bypass individual review by IRS officials entirely.

For the roughly 1 million Indian nationals waiting in various stages of the employment-based green card backlog, this is not abstract. Many have been in the United States for 10, 15, even 20 years. They have W-2s, mortgages, children in American schools. Their immigration cases are not criminal — they are simply stuck in a queue that Congress has not updated since 1990.

But the system that is supposed to protect their tax data no longer treats them as taxpayers first. It treats them as data points in an enforcement pipeline.

## The Compliance Trap

Immigration attorneys report a new and deeply uncomfortable question from clients: *Should I still file my taxes?*

The answer, legally, is unambiguous — yes, you must. Failing to file creates its own set of problems, including potential bars to adjustment of status and grounds for removal. But the emotional calculus has shifted. For families who have spent decades building lives in compliance with every rule, the revelation that their tax records were shared illegally — and that courts cannot agree on whether to stop it — registers as a betrayal of the compact they thought they had with the system.

The EFF estimates the data-sharing arrangement could cost the Treasury $313 billion in lost tax revenue over a decade if immigrant communities stop filing. That number is speculative, but the underlying logic is not: a surveillance system built on a compliance database will eventually destroy the compliance it depends on.

## What Happens Next

The Massachusetts injunction remains in effect. The D.C. Circuit ruling stands. The Supreme Court has not weighed in. Congress has shown no interest in legislating clarity.

For Indian immigrants — the single largest group in the H-1B and employment-based green card systems — the practical advice has not changed: file your taxes, keep your records, consult your attorney. But the trust that made that advice feel like a bargain, rather than a gamble, is harder to extend with each court filing that reveals how the system actually works behind the curtain."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "She Has a Stanford PhD and Can't Work — The H-4 EAD Crisis Is Erasing Indian Women from the American Workforce",
        "subheadline": "Washington killed the 540-day automatic work permit extension. Now tens of thousands of H-1B spouses — 80% of them women — are losing jobs they held for years.",
        "slug": make_slug("h4-ead-crisis-indian-women-workforce-work-permit"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian families on H-1B visas are overwhelmingly affected. The typical H-4 EAD holder is a highly educated Indian woman — often with a master's or PhD — who followed her spouse to the US and built a career while waiting years for a green card. The elimination of automatic extensions is destroying dual-income Indian households and forcing skilled professionals out of the workforce entirely.",
        "tags": ["h4-ead", "h1b-spouses", "women", "work-permit", "dhs", "lawsuit", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-spouses-sue-us-over-ending-automatic-work-permit-extensions"},
            {"name": "Permits Foundation", "url": "https://www.permitsfoundation.com/news/h-4-spouses-in-us-now-face-increased-uncertainty-with-elimination-of-ead-automatic-extension/"},
            {"name": "Visa Lawyer Blog", "url": "https://www.visalawyerblog.com/category/h4-spouses/"},
            {"name": "Best Migration Consultant", "url": "https://bestmigrationconsultant.com/us-extends-h4-ead-work-permits-540-days/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3784295/pexels-photo-3784295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The woman sitting across from the immigration attorney in Cupertino has a PhD in electrical engineering from Stanford and eight years of experience at a semiconductor company. She designed circuits that went into devices used by millions of people. Last month, her employment authorization expired. She is now, in the eyes of the U.S. government, not permitted to work.

Her husband is on an H-1B visa. His I-140 was approved in 2019. Their priority date for an EB-2 India green card is sometime in 2048, give or take a decade. She held an H-4 Employment Authorization Document that let her work while they waited. That EAD has now lapsed, and the system that was supposed to renew it automatically no longer exists.

## What Washington Took Away

In October 2025, the Department of Homeland Security published an interim final rule eliminating the 540-day automatic extension of Employment Authorization Documents. The Biden administration had introduced the extended grace period in 2022 to address mounting backlogs — USCIS processing times for EAD renewals had stretched well beyond six months in some service centers, leaving tens of thousands of workers in limbo between an expired card and a pending application.

The Trump administration killed the extension with immediate effect. DHS cited national security and public safety concerns, invoking an executive order on screening foreign nationals. The agency skipped the standard notice-and-comment period, using a "good cause" exception to make the rule effective the moment it hit the Federal Register.

The rationale was broad: "prioritize the proper vetting and screening of aliens before granting a new period of employment authorization." The impact was specific: it fell hardest on H-4 visa holders, the spouses of H-1B workers, who are the only dependent visa category required to apply separately for work authorization.

## The Numbers Behind the Policy

Over 80% of H-4 EAD holders are women. The overwhelming majority are Indian. They are not trailing spouses in any traditional sense — they are engineers, data scientists, product managers, physicians, and researchers who followed their partners to the United States and built careers of their own.

Under the old system, an H-4 spouse could file for EAD renewal up to 180 days before expiration and continue working while USCIS processed the application. The 540-day automatic extension meant that even if USCIS took a year to adjudicate, the worker stayed employed. It was an imperfect patch on a broken system, but it worked.

Without that extension, the math is brutal. USCIS processing times for I-765 applications (the EAD form) currently average four to eight months, depending on the service center. An H-4 spouse who files for renewal on day one of the 180-day window faces a minimum two-month gap between when her current EAD expires and when the new one is likely to arrive. During that gap, she cannot legally work.

For employers, this means a skilled employee disappears from the workforce with no predictable return date. For families, it means losing 40 to 60 percent of household income while still carrying a Bay Area mortgage or a New Jersey property tax bill.

## The Lawsuit

In January 2026, a group of H-1B spouses filed suit against DHS in the Central District of California. The complaint — *Doe v. U.S. Department of Homeland Security* — argues that the interim final rule violated the Administrative Procedure Act on two grounds: it was arbitrary and capricious, and DHS failed to establish good cause for bypassing notice-and-comment rulemaking.

The plaintiffs include workers at an accounting firm, an office supply company, and a national bank. Some had already lost employment authorization by the time the suit was filed. Their attorneys argue that DHS's stated justification — additional screening — is pretextual. The agency already operates continuous vetting programs that monitor individuals without requiring point-in-time adjudication of each application.

"The administration's true rationale, stripping the ability of people lawfully in the U.S. to sustain themselves, is embarrassingly obvious," the complaint states.

DHS has not backed down. A USCIS spokesperson connected the elimination of automatic extensions to the broader immigration enforcement agenda, arguing that the renewals "posed a security risk that allowed bad actors to continue to work in this country."

## The Biometric Escalation

The work permit restrictions are not the only pressure on H-4 families. In November 2025, DHS published a proposed rule to massively expand biometric collection for all immigration applicants — including DNA testing, iris scans, and voiceprints. The rule would apply to anyone filing for an immigration benefit, including EAD applications.

For H-4 spouses already navigating a system that requires separate applications for status extensions, work authorization, and travel documents, the biometric expansion adds another layer of cost, delay, and surveillance. Privacy advocates, including the Electronic Privacy Information Center, have argued that the proposal violates existing privacy laws and creates a genetic database with no clear limits on retention or use.

## The Invisible Workforce Crisis

What makes the H-4 EAD situation different from the broader H-1B debate is its invisibility. These are not new arrivals competing for cap slots. They are people who have been living and working in the United States for years, often decades, contributing to the tax base, raising American-citizen children, and filling roles in industries that cannot find enough qualified workers.

The Permits Foundation, an international organization that tracks work rights for accompanying partners, noted that the H-4 cohort is "already thoroughly vetted" and suggested that "it should be possible to enable streamlined work authorization processing while also ensuring the necessary scrutiny for public safety."

That suggestion assumes a system interested in distinguishing between genuine security concerns and bureaucratic leverage. The current evidence points in a different direction.

## What Indian Families Should Know

H-4 EAD holders should file Form I-765 as early as the 180-day window allows — not a day later. Immigration attorneys are advising clients to assemble documentation for expedite requests based on severe financial loss, which USCIS still accepts on a case-by-case basis. Employers should identify affected workers early and plan for potential workforce gaps.

The *Doe v. DHS* lawsuit is in its early stages. No injunction has been issued. The rule remains in full effect.

For the woman in Cupertino with the Stanford PhD, the immediate future involves waiting — for a card, for a court, for a Congress that has not meaningfully updated the immigration system since she was in elementary school. She is qualified to design the chips that power the phones in the pockets of the people who wrote the rule. She just is not qualified, at this moment, to earn a paycheck."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
