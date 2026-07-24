#!/usr/bin/env python3
"""Immigration writer — July 10, 2026 01:00 AM PT run"""
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
        "headline": "Your Green Card Means Nothing at the Border Now. The Supreme Court Just Said So",
        "subheadline": "The Blanch v. Lau ruling lets CBP treat returning green card holders with pending charges as first-time applicants. Immigration lawyers are telling clients: do not leave the country.",
        "slug": make_slug("green-card-blanch-lau-supreme-court-do-not-travel-pending-charges"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian green card holders who regularly travel to India for family events, weddings, or emergencies now face the risk of being denied re-entry if they have any pending legal matter — even a minor traffic misdemeanor that has not been resolved.",
        "tags": ["green-card", "supreme-court", "blanch-v-lau", "travel-warning", "cbp", "deportation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TheTravel", "url": "https://www.thetravel.com/us-green-card-holders-warned-do-not-travel-following-supreme-court-rule-change/"},
            {"name": "Alston & Bird LLP", "url": "https://www.alston.com/"},
            {"name": "Supreme Court of the United States", "url": "https://www.supremecourt.gov/"},
            {"name": "South Bend Tribune", "url": "https://www.southbendtribune.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/US_Supreme_Court.JPG/1280px-US_Supreme_Court.JPG",
        "image_caption": "The United States Supreme Court building in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the green card has been shorthand for permanence. A lawful permanent resident could travel abroad, visit family, attend a funeral, and come home without a second thought. The Supreme Court just rewrote that assumption.

In *Blanch v. Lau*, decided in late June, the court ruled 6–3 that a green card holder returning from international travel can be treated as someone "seeking admission" — effectively a first-time entrant — if they have pending criminal charges involving a crime of moral turpitude. The ruling does not require a conviction. It does not require an admission of guilt. A pending charge is enough.

Immigration attorney Jacob Saposnik responded with a blunt YouTube video titled "Green Card Holders: DO NOT TRAVEL With Pending Charges." His advice has since been echoed by major immigration law firms, including Alston & Bird, which published a detailed advisory warning that the ruling's reach extends beyond the obvious cases.

## What the ruling actually changes

The case centered on Muk Choi Lau, a Chinese citizen who became a lawful permanent resident in 2007. In 2012, New Jersey charged him with trademark counterfeiting. While awaiting trial, he briefly left the country. When he tried to return, Customs and Border Protection officers questioned him at the airport, learned of the pending charge, and confiscated his green card.

Under Section 1101(a)(13)(C)(v) of the Immigration and Nationality Act, a lawful permanent resident can be reclassified as someone "seeking admission" if they have committed an offense listed in the inadmissibility provisions — including crimes involving moral turpitude. Before *Blanch v. Lau*, courts were divided on whether a pending charge, as opposed to a conviction, could trigger this provision. The Supreme Court resolved that split in the government's favour.

The practical consequence: a green card holder who leaves the United States with an unresolved legal matter may not be allowed back in. They can be detained, placed in removal proceedings, and stripped of their permanent resident status — all without ever having been found guilty.

## The charges that trigger it

The ruling applies most directly to crimes of moral turpitude, a category that includes fraud, forgery, theft, embezzlement, tax evasion, perjury, and bribery. Controlled substance offences and aggravated felonies carry similar risks under separate statutory provisions.

But Alston & Bird warned that the impact extends further. Green card holders could face scrutiny even if:

- Their case is still pending and no conviction exists
- They have not admitted the conduct
- The charge may ultimately be reduced, dismissed, or resolved favourably
- They have previously travelled without incident

The firm advised that even minor misdemeanor charges warrant extreme caution before leaving the country.

## Why this hits the Indian diaspora hardest

Over 14 million people in the United States hold green cards. Indians represent one of the largest employment-based green card populations, and the community's ties to India — family obligations, religious ceremonies, business interests — make international travel not a luxury but a necessity.

Consider the H-1B worker who spent a decade in the green card backlog, finally received permanent residency, and now faces a pending DUI charge from a traffic stop. Before *Blanch v. Lau*, they could travel to India for a parent's medical emergency and return without issue. Now, Customs and Border Protection has Supreme Court backing to confiscate their green card at the airport and initiate deportation proceedings.

The timing compounds the problem. The ruling arrives alongside a cascade of immigration restrictions: the adjustment-of-status policy requiring green card applicants to leave the country, the $100,000 H-1B fee (struck down then reinstated on appeal), and USCIS processing delays that have pushed wait times past 400 days for basic applications. For Indian green card holders, the message from every branch of government is the same: stay put, stay quiet, and do not assume your status is secure.

## What to do now

Immigration attorneys are uniform in their guidance: if you hold a green card and have any unresolved legal matter — pending charges, an outstanding warrant, even an old traffic citation that was never formally dismissed — consult an immigration lawyer before booking a flight. The cost of a legal consultation is trivial compared to the cost of being stranded abroad while your permanent residency is revoked.

The Supreme Court has made the border a courtroom. For green card holders with any shadow on their record, leaving the country is now a gamble that no lawyer would recommend taking."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Green Card Hiring Test Has Not Changed Since 2004. The DOL Just Announced It Will",
        "subheadline": "The Department of Labor plans the first major overhaul of the PERM labour certification process in two decades. Employers will face stricter recruitment documentation, digital hiring audits, and a new requirement to account for recent layoffs.",
        "slug": make_slug("perm-labor-certification-overhaul-dol-green-card-hiring-rules"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers waiting for employer-sponsored green cards — already facing EB-2 India backlogs stretching decades — will now contend with a tougher, slower, and more expensive PERM process that could discourage employers from sponsoring at all.",
        "tags": ["perm", "green-card", "department-of-labor", "employment-immigration", "h1b", "hiring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/us-green-card-sponsorship-overhaul-could-raise-hiring-bar-for-employers"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg",
        "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """The Permanent Labor Certification programme — known universally as PERM — is the gatekeeping mechanism that every employer must clear before sponsoring a foreign worker for an employment-based green card. It requires companies to prove that no qualified American worker is available for the role, through a structured recruitment process and government review.

The rules governing that process were written in 2004. The Department of Labor has now announced it intends to rewrite them.

According to Bloomberg Law, the department wants to modernise PERM to reflect two decades of change in how companies actually hire. The focus areas: digital recruitment practices, candidate evaluation criteria, and — crucially — how recent corporate layoffs factor into whether an employer should be permitted to sponsor a foreign worker at all.

## What changes are on the table

The proposed overhaul targets several pillars of the current PERM framework.

**Recruitment documentation.** Under the existing rules, employers must conduct a series of recruitment steps — job postings, advertising, internal notices — and document that no qualified US worker applied or was rejected for legitimate reasons. The new rules would demand stronger, more granular documentation of those efforts, with particular scrutiny on digital job platforms where modern hiring actually happens. The 2004 framework was written for newspaper classifieds and campus job fairs. It predates LinkedIn, Indeed, and algorithmic job matching.

**Layoff consideration.** This is the most consequential proposed change. The revised rules would require PERM reviewers to examine whether the sponsoring employer has recently laid off American workers in the same or similar roles. Under the current framework, an employer can lay off an entire department of US workers and simultaneously file PERM applications for foreign replacements — a practice that has drawn bipartisan criticism for years. The proposed revision would make recent layoffs a significant negative factor in the certification decision.

**Digital hiring audits.** The DOL wants to update how it audits employer recruitment. Currently, audits focus on whether the prescribed recruitment steps were completed. The new approach would examine whether those steps were conducted in good faith — whether the job requirements were tailored to exclude American applicants, whether salary offerings were competitive, and whether the employer's broader hiring patterns suggest a preference for foreign workers over domestic candidates.

## The PERM bottleneck is already severe

The overhaul announcement arrives at a moment when the PERM system is already under extreme strain. Average processing times for labour certification applications have ballooned to over 400 days, according to DOL data — up from roughly 180 days in 2019. The backlog affects every employment-based green card category, but hits EB-2 and EB-3 applicants from India hardest. These are the categories that most H-1B workers use when their employers sponsor them for permanent residency.

A stricter PERM process layered on top of existing delays creates a compounding problem. If employers face more documentation requirements, higher audit rates, and the risk that recent layoffs will disqualify their applications, some will decide that sponsoring foreign workers is not worth the cost and complexity. For Indian professionals already navigating multi-decade green card backlogs, fewer employer sponsorships means fewer paths to permanence.

## The tech layoff connection

The layoff-consideration provision is not abstract. In the past twelve months alone, Microsoft has cut nearly 15,000 positions, Meta eliminated 8,000 roles, and Oracle's headcount dropped by 21,000. These same companies are among the largest sponsors of H-1B workers and, by extension, among the most frequent PERM filers.

The revised rules would force a direct reckoning: a company that laid off 4,800 workers — as Microsoft did this week — would face heightened scrutiny if it simultaneously filed PERM applications for foreign workers in similar roles. The current system treats those two actions as unrelated. The proposed system would not.

For Indian IT professionals at these companies, the implications are stark. An H-1B worker who survived a layoff round but whose PERM application has not yet been filed may find their employer unwilling to initiate the process, knowing the recent layoffs would invite a DOL audit.

## The broader pattern

The PERM overhaul fits neatly into the administration's wider immigration agenda: the $100,000 H-1B fee (struck down, reinstated, appealed), the wage-weighted H-1B lottery, the DOL Inspector General's fraud probe targeting Indian IT outsourcers, and the adjustment-of-status restrictions that now require green card applicants to leave the country.

Each of these policies operates independently. Together, they form a system designed to make employer-sponsored immigration progressively more expensive, more time-consuming, and more legally perilous. For the Indian professional on an H-1B visa — already paying into Social Security without a totalization agreement, already waiting decades for a green card, already navigating consular appointment backlogs — the PERM overhaul is another turn of the screw.

The Department of Labor has not yet published a proposed rule or set a timeline for implementation. But the signal is clear: the hiring test that has governed green card sponsorship for twenty years is about to get significantly harder to pass."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
