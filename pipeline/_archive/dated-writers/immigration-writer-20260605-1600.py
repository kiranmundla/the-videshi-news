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
        "headline": "A Federal Judge Just Told USCIS It Cannot Rewrite Immigration Law by Memo",
        "subheadline": "A Rhode Island ruling invalidating blanket USCIS policies against 39 countries sets a legal precedent that could reshape how courts view the agency's authority — including over Indians waiting in the green card line.",
        "slug": make_slug("federal-judge-uscis-travel-ban-39-countries-memo-indian-precedent"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "While India is not on the travel ban list, the ruling's core finding — that USCIS cannot unilaterally adopt blanket policies to deny immigration benefits without proper authority — directly threatens the legal foundation of other USCIS memo-based policies that do affect Indians, including PM-602 (the adjustment of status discretionary memo), the $100K H-1B premium, and the new I-485 interview framework.",
        "tags": ["uscis", "travel-ban", "court-ruling", "immigration-law", "green-card", "indian-immigrants"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us-judge-invalidates-trump-policies-targeting-immigrants-39-countries-2026-06-05/"},
            {"name": "Manifest Law", "url": "https://manifestlaw.com/uscis-halts-processing-19-countries-potential-travel-ban/"},
            {"name": "NYIC", "url": "https://nyic.org/2025/12/trump-halts-legal-immigration-39-countries/"},
            {"name": "Fisher Phillips LLP", "url": "https://www.fisherphillips.com/en/news-insights/uscis-streamline-nonimmigrant-dependent-spouses-employment-authorization.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077326/pexels-photo-6077326.jpeg",
        "image_caption": "A gavel striking a sound block in a courtroom",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """U.S. District Judge John McConnell did something on Friday that immigration lawyers have been waiting for all year: he told USCIS, in no uncertain terms, that it cannot adopt sweeping policies that effectively deny immigration benefits to entire nationalities without following the law.

The ruling, issued from the federal courthouse in Providence, Rhode Island, struck down a series of USCIS policies that had barred people from 39 African, Asian, Latin American, and Middle Eastern countries from receiving final decisions on their asylum, work permit, green card, and citizenship applications. The policies had been in effect since late 2025, when the Trump administration expanded its travel ban and then used a USCIS policy memo to freeze the processing of virtually all immigration benefits for nationals of those countries.

## What the Judge Actually Said

McConnell's ruling found that USCIS had adopted these blanket holds without proper rulemaking, without adequate notice, and without the statutory authority to unilaterally deny benefits that Congress had made available. The judge ruled the policies "unlawful" — a word that matters enormously in immigration law, because it means the policies were not merely unwise or harsh but legally invalid from the start.

The 39 countries on the list include Afghanistan, Iran, Somalia, Yemen, Cuba, Venezuela, and several others. India is conspicuously absent. But immigration attorneys say the ruling's significance extends far beyond the specific countries named.

## Why Indians Should Be Paying Attention

The legal reasoning in McConnell's decision strikes at the heart of how USCIS has been operating for the past year. The agency has increasingly relied on internal policy memos — rather than formal rulemaking — to make sweeping changes to how immigration benefits are adjudicated. The PM-602 memo that rewrote adjustment of status as "discretionary grace" rather than a standard process? A policy memo. The new I-485 interview framework that added four invasive questions? A policy memo. The guidance treating H-1B holders as presumptive immigrants? A policy memo.

McConnell's ruling establishes that USCIS cannot use this mechanism to effectively create new law. When a policy memo operates to deny benefits that the statute makes available, it crosses the line from guidance into unlawful action.

For the roughly 1.2 million Indians in the employment-based green card backlog, this distinction is not academic. The PM-602 memo — which tells USCIS officers to treat adjustment of status as an extraordinary remedy rather than a routine process — operates in exactly the same way as the 39-country freeze: it uses internal guidance to deny a benefit that the Immigration and Nationality Act explicitly provides.

## The Litigation Landscape

Several lawsuits challenging USCIS policies that directly affect Indian nationals are already working through the federal courts. The PM-602 memo faces at least two pending challenges. The $100,000 H-1B premium processing fee, imposed by executive proclamation rather than legislation, is being challenged on similar grounds — that the executive branch exceeded its statutory authority.

McConnell's ruling does not automatically invalidate these other policies. But it provides a roadmap. Federal judges in other districts will look at how McConnell analyzed USCIS's authority, how he weighed the agency's claimed justifications against the statutory text, and how he applied the Administrative Procedure Act's requirements for notice and rulemaking.

"The significance is in the framework," said one immigration attorney who tracks USCIS litigation. "The court said you cannot achieve through memo what Congress has not authorized through statute. That principle applies to every USCIS policy memo, not just the ones involving the travel ban countries."

## What Happens Next

The ruling is expected to face an immediate appeal from the Department of Justice. The government will likely seek a stay pending appeal, arguing that the judge overstepped by invalidating nationwide policies based on a single district court case.

But even if the ruling is stayed, the legal arguments it validates are already being incorporated into challenges to other USCIS policies. For Indian H-1B holders watching the PM-602 memo turn their green card path from a bureaucratic process into a discretionary gamble, Friday's ruling from Rhode Island is the first real sign that courts are willing to draw a line.

The question now is whether other judges will follow."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Leave America to Keep Your Green Card — The Catch-22 Buried in the PM-602 Memo",
        "subheadline": "The USCIS memo pushing green card applicants toward consular processing sounds like a procedural tweak. For Indians on H-1B visas, it is a trap that could trigger departure bars, consulate backlogs, and years of limbo.",
        "slug": make_slug("pm602-consular-processing-trap-indian-h1b-green-card-catch22"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals face the worst-case scenario under PM-602: the longest EB-2/EB-3 backlogs (decades), the most crowded consular appointment calendars (Indian consulates are rescheduling 90-120 days out), and the highest stakes (most are mid-career professionals with families, mortgages, and children in American schools). Being pushed to consular processing means leaving jobs, triggering potential unlawful presence bars, and waiting months for visa stamping — all while the backlog clock keeps ticking.",
        "tags": ["pm-602", "consular-processing", "adjustment-of-status", "green-card", "h1b", "india", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Orange Law", "url": "https://orangelaw.us/uscis-pm-602-0199-what-it-means-for-your-green-card/"},
            {"name": "Immigration Monitor", "url": "https://immigrationmonitor.com/adjustment-of-status-vs-consular-processing-after-may-21-2026/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/green-card-process-changes-in-us-heres-what-it-means-for-indian-applicants"},
            {"name": "Pew Research Center", "url": "https://www.pewresearch.org/short-reads/2026/06/02/majority-of-new-green-cards-have-gone-to-immigrants-already-living-in-us/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "image_caption": "A hand holding an open passport with various visa stamps",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The USCIS memo known as PM-602-0199 has been described in headlines as a policy shift, a guidance update, a procedural change. Immigration attorneys who have spent the past two weeks reading it line by line are using a different word: trap.

The memo, issued on May 21, formally reframes adjustment of status — the process by which immigrants already living in the U.S. apply for green cards without leaving the country — as an act of "administrative grace" rather than a standard procedure. USCIS officers are now instructed to treat domestic adjustment as an extraordinary remedy, available only when applicants can demonstrate "unusual or even outstanding equities." Everyone else, the memo implies, should be processed through consular channels in their home country.

For most immigrant groups, this is an inconvenience. For Indians on H-1B visas, it is a minefield.

## The Bars Nobody Is Talking About

Here is the part that most coverage of PM-602 has missed: consular processing requires you to leave the United States. And for many Indians who have been living and working here for years, leaving triggers a legal mechanism that could lock them out.

Under the Immigration and Nationality Act, anyone who has accumulated more than 180 days of unlawful presence in the U.S. and then departs faces a three-year bar on reentry. More than a year of unlawful presence triggers a ten-year bar. These bars are automatic. They are not discretionary. And they cannot be waived for most employment-based applicants.

The critical question is whether an H-1B holder can accumulate unlawful presence. The answer, increasingly, is yes — and more easily than most people realize. A gap between H-1B approvals, a period of unemployment exceeding the 60-day grace window, time spent on a pending application after a status change was technically denied — any of these can create unlawful presence that the holder may not even know about.

Under the old system, this was largely irrelevant. If you adjusted status within the U.S., you never departed, and the bars were never triggered. PM-602 changes the calculus. By pushing applicants toward consular processing, the memo forces the very departure that activates the bars.

## The India Consulate Bottleneck

Even for applicants with perfectly clean status histories, consular processing through India presents its own nightmare. U.S. consulates in Mumbai, Delhi, Chennai, Hyderabad, and Kolkata have been rescheduling H-1B and H-4 visa appointments 90 to 120 days out, according to the Greenberg Traurig immigration practice. The backlogs are a direct consequence of new social media screening requirements and enhanced vetting procedures implemented earlier this year.

An Indian H-1B holder who is told to complete green card processing through consular channels must first obtain an immigrant visa appointment at one of these consulates. That means flying to India, waiting weeks or months for the appointment, attending the interview, and then waiting for administrative processing — which can add another 30 to 90 days. During this entire period, the applicant is not working in the United States. Their H-4 spouse, if they had an EAD, has lost work authorization. Their children are missing school.

And if the consulate issues a 221(g) administrative processing hold — which has become routine for applicants in technology fields — the wait extends further. There is no timeline, no appeal, and no way to return to the U.S. on the expired H-1B stamp while the case is pending.

## The Numbers Tell the Story

Pew Research Center data published this week shows that 61 percent of Indian immigrants who received green cards in fiscal year 2024 did so through adjustment of status within the United States. Nationwide, 69 percent of all employment-based green cards were processed domestically. The system was built around the assumption that qualified applicants already living and working in the U.S. would stay here while their cases were decided.

PM-602 inverts that assumption. It tells USCIS officers that domestic processing is the exception, not the rule — and that applicants who entered on temporary visas should expect to leave.

For Indian nationals in the EB-2 and EB-3 backlog, where wait times already stretch into decades because of per-country caps, this creates a grotesque paradox. You must wait in line for years, sometimes over a decade, for your priority date to become current. When it finally does, you must now convince a USCIS officer that your case presents "extraordinary equities" — or get on a plane to India and risk the bars, the consulate backlog, and months without income.

## What Immigration Attorneys Are Advising

The emerging legal consensus, based on analysis published this week by multiple immigration practices, is threefold.

First, document everything. Any applicant who may be affected by PM-602 should compile a detailed record of their status history, including every I-94 entry, every H-1B approval notice, every gap between petitions, and every period of authorized versus unauthorized employment. The goal is to be able to prove, definitively, that no unlawful presence has accrued — so that consular processing, if forced, does not trigger the bars.

Second, consider filing early. For applicants whose priority dates are approaching, filing the I-485 now — before the memo's full impact is felt — may preserve the adjustment pathway. USCIS has not announced any policy to retroactively deny already-filed cases under the new discretionary standard, though attorneys warn this could change.

Third, explore alternatives. The EB-1A extraordinary ability category, the National Interest Waiver pathway, and certain cap-exempt H-1B positions may offer routes that are less vulnerable to the discretionary framework. None of these is a simple substitute, but for applicants with strong profiles, they may be the only reliable path forward.

## The Bigger Picture

PM-602 is not a standalone policy. It is the latest in a series of USCIS actions — the $100,000 H-1B fee, the I-485 interview changes, the new discretionary framework — that collectively amount to a fundamental restructuring of how employment-based immigration works in the United States. Each policy on its own is significant. Together, they create a system where staying legally, working legally, and waiting legally is no longer enough.

For the Indian professionals who built careers, families, and lives in this country on the promise that the system would eventually process their applications, PM-602 is the clearest signal yet that the rules have changed — and that the safety of adjusting status from within the United States can no longer be taken for granted."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
