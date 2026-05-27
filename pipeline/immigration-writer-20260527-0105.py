#!/usr/bin/env python3
"""Immigration writer – 2026-05-27 01:05 PDT batch"""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────
# ARTICLE 1: The NIW Trap
# ──────────────────────────────────────────────

article_1_body = """The pitch has never been simpler: skip the H-1B lottery, skip the employer sponsorship treadmill, file your own green card petition through the EB-1A or EB-2 National Interest Waiver. Immigration lawyers from New York to the Bay Area are selling the self-petition route as the escape hatch from a work-visa system that has never been more hostile to Indian professionals. There is just one problem. USCIS is slamming the door on that route too.

## The Numbers That Matter

In the first quarter of fiscal year 2025, the EB-2 NIW had an approval rate of 62.8 percent. By Q4 of the same year, that number had collapsed to 35.7 percent — a near-halving in twelve months. Over the full fiscal year, USCIS adjudicated 35,395 NIW petitions and denied 15,863 of them, producing an overall approval rate of just 55.2 percent. For a category that routinely cleared 70-plus percent in prior years, the trajectory is unmistakable.

The EB-1A, the "extraordinary ability" green card, has not published the same granular quarterly data. But immigration attorneys report a parallel increase in Requests for Evidence and outright denials, particularly for Indian applicants in technology and engineering — fields where the volume of petitions has surged.

## Why Indians Are Flooding These Categories

The traditional path — H-1B to PERM labor certification to EB-2/EB-3 green card — has become something between a decade-long endurance test and an outright trap. The EB-2 India priority date sits at January 15, 2015, meaning applicants who filed eleven years ago are only now reaching the front of the line. The EB-3 India backlog is even worse.

Then came the one-two punch of 2026. The $100,000 consular processing fee on new H-1B cases filed from abroad. The PM-602-0199 memo reclassifying adjustment of status as "extraordinary relief" rather than standard procedure. The 38.5 percent plunge in H-1B registrations for FY 2027. The 110,000 tech layoffs triggering 60-day departure countdowns for visa holders.

Against that backdrop, self-petition routes look like rational self-preservation. The EB-1A lets you file without an employer. The NIW waives the job offer and labor certification requirement entirely. Both allow you to control your own timeline instead of depending on a company that might lay you off next quarter.

The American Immigration Lawyers Association noted in April 2026 that "high-impact professionals are increasingly choosing EB-1A and EB-2 NIW green cards over the H-1B visa due to USCIS's lottery uncertainty, structural changes, and $100,000 consular processing fees." Law firms specializing in self-petitions report that Indian clients now make up the majority of their NIW caseloads.

## The Catch

But the math is turning against applicants. The NIW requires proving your work has "substantial merit and national importance" under the three-prong *Matter of Dhanasar* framework. USCIS adjudicators have reportedly tightened their interpretation of what counts — particularly on the third prong, which asks whether waiving the job offer requirement benefits the United States. Attorneys say the agency is demanding more granular evidence of economic impact and issuing more RFEs on cases that would have sailed through two years ago.

The EB-1A is even more demanding. The *Kazarian* two-step test requires meeting at least three of ten regulatory criteria for "extraordinary ability," then surviving a holistic merits review. Indian engineers with strong publication records but no Nobel Prize are discovering that "extraordinary" is being defined upward.

And there is an additional bottleneck for Indian nationals: even with an approved I-140, you still wait for a visa number. The EB-1 India priority date has already retrogressed this year. The EB-2 India wait remains measured in decades, not years. Premium processing can speed the I-140 adjudication to 45 business days for NIW or 15 days for EB-1A, but it cannot move the visa bulletin.

## What This Means for You

The self-petition route is still real. For Indian professionals with genuinely exceptional track records — significant citations, patents, revenue impact, or industry recognition — the EB-1A remains the fastest permanent path. For founders and researchers whose work aligns with recognized national priorities in AI, biotech, clean energy, or advanced computing, the NIW can work. But the era of "anyone with a master's degree and a decent resume can file a NIW" is over.

The practical advice from immigration attorneys: start building your evidence portfolio now, even if you are years from filing. Document revenue impact. Collect recommendation letters from recognized figures. Track citations and media coverage. And budget realistically — attorney fees for NIW petitions run $6,000 to $20,000, and a denial means starting over.

The deeper issue is structural. Indian professionals are being squeezed from every direction — tighter H-1B rules, a hostile AOS environment, longer backlogs, and now higher denial rates on the very alternatives they were told to pursue. The escape hatch exists, but the window is narrowing faster than most people realize."""

article_1 = {
    "id": str(uuid.uuid4()),
    "headline": "The NIW Approval Rate Just Cratered to 35% — And That Was Supposed to Be the Escape Route",
    "subheadline": "Indian professionals are flooding EB-1A and EB-2 NIW self-petition categories to escape the H-1B trap. USCIS is tightening those too.",
    "slug": make_slug("niw-approval-rate-crash-eb1a-self-petition-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders facing 11-year EB-2 backlogs, $100K fees, and the AOS crackdown are turning to self-petition routes — but NIW denials nearly doubled in one year, from 37% to 64% in Q4 FY2025. The alternative escape route is closing.",
    "tags": ["niw", "eb-1a", "self-petition", "green-card", "uscis", "h1b-alternative", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AILA - Think Immigration: Beyond the H-1B Visa", "url": "https://www.aila.org/library/think-immigration-beyond-the-h-1b-visa-eb-1a-and-eb-2-niw-green-cards"},
        {"name": "Manifest Law - EB-2 NIW Requirements and Costs 2026", "url": "https://manifestlaw.com/blog/eb2niw-visa/"},
        {"name": "USCIS Immigration and Citizenship Data (FY2025 adjudications)", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "body": article_1_body,
}

# ──────────────────────────────────────────────
# ARTICLE 2: Supreme Court Silences Immigration Judges
# ──────────────────────────────────────────────

article_2_body = """On May 26, the U.S. Supreme Court handed the Trump administration another win in its campaign to consolidate control over the immigration system. The unsigned ruling in *Margolin v. National Association of Immigration Judges* did not decide whether the government can legally muzzle the 750 judges who preside over deportation hearings, asylum claims, and green card adjudications. It simply ensured that nobody will find out anytime soon.

## What the Court Actually Did

The case involves a 2017 policy — updated in 2021 — that requires every immigration judge in the country to obtain supervisor approval before making any public statement related to their work. That includes speeches, panel appearances, media interviews, and even personal-capacity remarks if the judge was invited because of the role or is discussing agency-related topics.

The National Association of Immigration Judges (NAIJ) challenged the policy as a prior restraint on speech, arguing it violated the First Amendment. A lower court agreed to hear the case. The 4th U.S. Circuit Court of Appeals kept it alive on jurisdictional grounds the judges themselves had not raised.

The Supreme Court reversed on precisely that procedural point. The justices invoked the "party-presentation principle" — courts should not decide issues the parties did not raise — and sent the case back to administrative proceedings through the Merit Systems Protection Board, the federal workplace dispute system.

The practical effect: the speech restriction stays in force. The constitutional question remains unanswered. And the judges who see the immigration system's failures firsthand cannot tell the public what they see.

## Why This Matters to Indians With Pending Cases

There are roughly 750 immigration judges in the United States. They adjudicate deportation orders, asylum petitions, bond hearings, and — critically for the Indian diaspora — immigration benefit cases where USCIS decisions are contested. The Executive Office for Immigration Review, which houses the immigration courts, operates under the Department of Justice and has a case backlog exceeding 3 million.

For the hundreds of thousands of Indian nationals with pending green card applications, H-1B extensions under review, or adjustment of status cases caught in the PM-602-0199 crackdown, immigration judges are the last line of institutional accountability. When processing times balloon, when policies shift mid-application, when USCIS denies cases that would have been approved two years ago — immigration judges are the people positioned to identify systemic problems.

Under the speech restriction, they cannot do that publicly. A judge who has seen a pattern of questionable denials in EB-2 cases cannot write about it. A judge who believes the AOS "extraordinary relief" framework is being applied inconsistently cannot say so at a legal conference without supervisory approval — approval that comes from the same administration whose policies the judge might critique.

## The Broader Pattern

The ruling fits a larger consolidation effort. Over 80 new immigration judges have been hired since May 21, 2026, as part of what the administration describes as a push to accelerate deportations. The Supreme Court has issued 35 emergency orders in the current term, most allowing the administration to keep restrictive policies in place while litigation proceeds.

Solicitor General D. John Sauer argued that allowing judges to bypass administrative channels would create "a new loophole" and "wreak havoc" with federal employment law. Attorney General Pamela Bondi framed the victory as a defense of presidential authority against "gross judicial overreach."

Alex Abdo, litigation director at the Knight First Amendment Institute, called the decision a failure to protect public servants' speech rights. "Forcing public employees to wade through cumbersome and potentially futile administrative proceedings before challenging prior restraints allows unconstitutional censorship to persist," Abdo said.

## The Silence Tax

For Indian immigrants navigating a system that has become materially harder in 2026, the Supreme Court ruling adds an invisible cost. The people who adjudicate your case cannot tell you — or anyone — what is going wrong inside the system. Processing delays, inconsistent standards, policy confusion: all of it stays behind closed doors.

The 750 judges will keep showing up to work. They will keep adjudicating cases. But the public conversation about whether the immigration system is functioning fairly will be missing one of the few voices that actually knows."""

article_2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Supreme Court Just Made Sure the Judges Who Decide Your Case Can't Talk About It",
    "subheadline": "A May 26 ruling keeps 750 immigration judges under a speech gag while the constitutional fight gets buried in administrative proceedings. For Indians with pending cases, the silence is the point.",
    "slug": make_slug("supreme-court-immigration-judges-speech-gag-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With 3+ million cases backlogged, processing times ballooning, and the AOS crackdown creating confusion, immigration judges are the only institutional actors who see the system's failures firsthand. The Supreme Court just ensured they cannot tell the public what they see — including patterns in how Indian green card and H-1B cases are being adjudicated.",
    "tags": ["supreme-court", "immigration-judges", "free-speech", "uscis", "deportation", "first-amendment", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters - Supreme Court sides with Trump in fight tied to speech curbs on immigration judges", "url": "https://www.reuters.com/legal/supreme-court-sides-with-trump-fight-tied-speech-curbs-immigration-judges-2026-05-27/"},
        {"name": "VisaVerge - Supreme Court Rules on Immigration Judge Speech Case 2026", "url": "https://www.visaverge.com/news/trump-wins-supreme-court-ruling-in-dispute-over-speech-limits-for-immigration-judges/"},
        {"name": "Knight First Amendment Institute statement", "url": "https://knightcolumbia.org/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg",
    "body": article_2_body,
}

# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [article_1, article_2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
