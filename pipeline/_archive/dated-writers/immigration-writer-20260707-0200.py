#!/usr/bin/env python3
"""Immigration writer — July 7, 2026 02:00 UTC run.
Two articles: PERM 403-day backlog; USCIS new social media form requirements.
"""
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
        "headline": "Four Hundred and Three Days. That Is How Long the First Step of Your Green Card Now Takes",
        "subheadline": "The Department of Labor's PERM labour certification backlog has ballooned to over thirteen months, adding yet another brutal layer to the decades-long wait Indian professionals already face for permanent residency.",
        "slug": make_slug("perm-labor-certification-403-day-backlog-green-card-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians comprise the largest share of PERM applicants and already face decades-long EB-2/EB-3 green card backlogs — the 403-day PERM delay now adds over a year before the clock even starts.",
        "tags": ["perm", "green-card", "dol", "immigration", "backlog", "EB-2", "EB-3", "labor-certification"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Department of Labor FLAG Processing Times", "url": "https://flag.dol.gov/processingtimes"},
            {"name": "Waylit — Processing Times for PERM in 2026", "url": "https://waylit.com/perm-processing-times"},
            {"name": "Badmus & Associates — Surviving the 500-Day Wait", "url": "https://badmuslaw.com/surviving-the-500-day-wait-a-realistic-guide-to-perm-processing-timelines/"},
            {"name": "Bloomberg Law — Labor Department Eyes Immigration Changes in Broad Rule Plan", "url": "https://news.bloomberglaw.com/daily-labor-report/labor-department-eyes-immigration-changes-in-broad-rule-plan"},
            {"name": "Boundless — Green Card Processing Times 2026", "url": "https://www.boundless.com/immigration-resources/green-card-processing-time/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The Department of Labor just published its latest processing times, and the number lands like a gut punch: 403 calendar days. That is how long it now takes, on average, for the DOL to adjudicate a PERM labour certification through analyst review. The data, posted on flag.dol.gov as of June 30, 2026, means the government is currently working through applications filed in June 2025 — over thirteen months ago.

For anyone unfamiliar with the green card assembly line, PERM is Step One. Before your employer can file an I-140 immigrant worker petition, before you enter the visa bulletin queue, before you file for adjustment of status, the Department of Labor must first certify that no qualified American worker is available for your job. It is the foundation of the entire employment-based green card process. And that foundation now takes longer than a pregnancy.

## The full timeline is staggering

The 403-day PERM wait is not the end. It is the beginning. Once PERM is certified, your employer files the I-140 petition — currently processing at 8.1 months for regular cases, or 15 days with a $2,965 premium processing fee. Then you wait for your priority date to become current in the monthly visa bulletin. Then you file the I-485 adjustment of status application, which takes another 8 to 14 months.

For most Indian EB-2 applicants, the visa bulletin wait alone stretches back over a decade. The July 2026 visa bulletin marked EB-2 India as "unavailable" for the rest of the fiscal year, shutting the door until at least October. EB-3 India's final action date sits at late 2013.

Add it up: PERM (403 days) plus I-140 (8 months) plus visa bulletin wait (10-plus years for India) plus I-485 (roughly a year). A software engineer filing PERM today will not hold a green card for well over a decade. And that assumes nothing goes wrong.

## Audit cases face their own purgatory

Not every PERM application sails through analyst review. The DOL selects a significant number of cases for audit — a deeper review that requires employers to submit additional documentation about their recruitment process, the job requirements, and the candidate's qualifications.

Audited cases sit in a separate queue. As of June 30, the DOL is processing audit cases filed in December 2025, with an average processing time of 290 days. That is nearly ten months in the audit queue alone, on top of whatever time the case spent waiting before it was flagged.

If the audit results in a denial, the employer can file a reconsideration request. That queue is currently processing requests submitted in February 2026. The layering of delays is relentless.

## The prevailing wage bottleneck has eased, but the backlog has not

Before an employer can even file PERM, it must obtain a prevailing wage determination from the DOL. Earlier this year, prevailing wage requests filed in March 2026 saw over 7,700 applications still pending. By April, that number jumped to 16,070. May filings hit 18,524 pending applications.

The DOL has made progress on older prevailing wage requests — November 2025 filings are down to just four pending cases. But the sheer volume of new filings, particularly from the technology sector, keeps the pipeline under pressure.

## The DOL is rewriting the rules — for the first time in two decades

The processing times are not the only story. The Department of Labor announced in its latest regulatory agenda that it plans to overhaul the entire PERM system for the first time since 2004. The proposed rulemaking will modernise how the agency reviews employer applications, with new standards for recruiting qualified American workers and additional safeguards for domestic workers affected by layoffs.

The last time PERM regulations were updated, Facebook did not exist. The iPhone had not been invented. The technology landscape that drives most PERM filings today bears no resemblance to the one the rules were designed for.

For Indian professionals, the rulemaking carries a double edge. Modernised rules could streamline the process and reduce processing times. But the administration has signalled that new rules will also include significantly higher prevailing wage floors for H-1B workers, which feed directly into PERM wage requirements. Higher wage floors could make it harder — and more expensive — for employers to sponsor green cards for early-career professionals.

## What this means for Indian Americans

The PERM backlog is not an abstraction. It is the reason a senior software architect at Google waits over a year before the green card process formally begins. It is why a physician in rural Nebraska, already serving an underserved community, cannot even start the paperwork that might let her stay permanently. It is one more wall in a system that already asks Indian professionals to wait longer than any other nationality on earth for permanent residency.

For those currently in the queue, the practical advice is limited but important. Premium processing for the I-140 ($2,965 for a 15-day decision) can recover some time after PERM clears. Employers should begin the prevailing wage request as early as possible and ensure recruitment documentation is impeccable to avoid an audit. And anyone considering a green card through employment should understand that the clock starts ticking the day PERM is filed — not the day you decide you want one.

Four hundred and three days. For the first step. In a process measured in decades."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Wants Ten Years of Your Social Media. What Counts as 'Anti-American' Is Still Anyone's Guess",
        "subheadline": "New immigration forms will require applicants to disclose a decade of social media handles — including closed accounts — while the government's standard for rejecting visa applications based on 'anti-American' content remains deliberately undefined.",
        "slug": make_slug("uscis-ten-years-social-media-anti-american-undefined-forms"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B and green card applicants are among the largest groups affected by expanded social media disclosure requirements, and the vague 'anti-Americanism' standard creates particular uncertainty for politically active diaspora members.",
        "tags": ["uscis", "social-media", "anti-americanism", "visa", "forms", "disclosure", "h1b", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Stricter vetting, slower processing: How new immigration form changes are reshaping hiring for employers", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are--pracin-2026-07-06/"},
            {"name": "USCIS — USCIS to Consider Anti-Americanism in Immigrant Benefit Requests", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-to-consider-anti-americanism-in-immigrant-benefit-requests"},
            {"name": "Fragomen — USCIS to Consider a Foreign National's Support for Anti-American Ideologies", "url": "https://www.fragomen.com/insights/uscis-to-consider-anti-americanism.html"},
            {"name": "American Immigration Council — FOIA Request on Anti-Americanism Implementation", "url": "https://www.americanimmigrationcouncil.org/foia/uscis-implementation-anti-americanism"},
            {"name": "Fragomen — Visa Applicants Required to Disclose Social Media Use", "url": "https://www.fragomen.com/insights/visa-applicants-now-required-to-disclose-social-media-use-prior-contact-information.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16229745/pexels-photo-16229745.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Social media app icons on a smartphone screen",
        "image_attribution": "Pexels",
        "body": """The immigration forms you fill out are about to get a lot more personal. U.S. Citizenship and Immigration Services has indicated that updated versions of its core application forms will require applicants to disclose up to ten years of social media handles — double the current five-year window — including accounts that have already been closed. Applicants may also be asked to provide detailed information about immediate family members, including parents and siblings.

The expanded disclosure requirements, detailed in a Reuters analysis published this week, represent the latest front in the administration's effort to tighten immigration vetting. But the most troubling element is not the scope of the disclosure itself. It is what the government plans to do with the information — and how little it has said about where the line is.

## The 'anti-Americanism' standard nobody can define

In August 2025, USCIS announced that it would begin considering "anti-Americanism" as a negative factor when adjudicating immigration benefit requests — everything from work permits to green card applications. The agency expanded the types of benefit requests subject to social media vetting and declared that anti-American activity would be "an overwhelmingly negative factor in any discretionary analysis."

The announcement did not define "anti-American." It still has not.

USCIS pointed to longstanding statutory bars relating to communism, totalitarianism, and advocacy for the violent overthrow of the U.S. government. But immigration attorneys and civil liberties organisations have warned that the standard could be applied far more broadly. Fragomen, one of the world's largest immigration law firms, noted that "it is possible that adjudicators will apply their discretionary authority more broadly to other types of activity and other ideologies deemed to be anti-American."

The ambiguity raises difficult questions. Does criticism of a sitting president fall within scope? Could participation in a political protest — a "No Kings" rally, for instance — be viewed as problematic? What about a retweet of a critical op-ed, or a LinkedIn comment questioning a government policy?

## The FOIA request that has gone nowhere

The American Immigration Council, together with Just Futures Law, filed a Freedom of Information Act request in January 2026 seeking documents on how USCIS plans to implement its anti-Americanism screening. The request, updated in March 2026, remains pending. Six months in, the agency has produced no responsive documents.

The silence is itself a policy. Without clear guidance, applicants are left to self-censor — scrubbing old posts, deleting accounts, second-guessing whether a decade-old tweet might derail a green card application. Immigration attorneys report that clients are increasingly anxious about their digital footprint, with some deleting entire social media histories rather than risk an unknown standard.

## Operational delays are already biting

The expanded vetting is not just a theoretical concern. It is already causing measurable harm. When the State Department implemented social media screening for H-1B and H-4 visa applicants at U.S. consulates in December 2025, the operational impact was immediate. Consulates in India needed time to establish review processes and abruptly rescheduled visa appointments — in some cases pushing interviews from December 2025 to mid-2027.

H-1B holders who had travelled to India for visa stamping found themselves stranded for months, unable to return to their jobs. Employers could not keep positions vacant for that long. Some workers returned not to their desks but to unemployment.

The new form requirements threaten to extend those delays further. Reviewing ten years of social media for every applicant — including cross-referencing handles across multiple platforms, verifying closed accounts, and evaluating content — requires time, staffing, and infrastructure that USCIS has not demonstrated it possesses. The agency already faces a system-wide backlog, with Congressional Democrats demanding answers about processing delays across virtually every form category.

## CBP is searching your devices at the border

The social media dragnet extends beyond the application process. Foreign nationals entering the United States are increasingly subject to electronic device searches at the border by Customs and Border Protection. CBP officers may ask travellers to unlock laptops and phones, reviewing social media activity directly — a practice that falls within existing border search authority but that has escalated significantly in frequency.

For H-1B holders returning from international travel, this creates a double exposure. Your social media is reviewed when you apply for or renew your visa. It may be reviewed again when you land at JFK or SFO. The same content can be evaluated twice, by different officers, under different and equally undefined standards.

## What Indian Americans need to know

Indian nationals are among the largest groups affected by these changes. They file more H-1B petitions than any other nationality, represent the largest share of employment-based green card applicants, and are disproportionately represented in the visa stamping backlogs at U.S. consulates in India.

The practical implications are stark. Do not delete social media accounts in a panic — omitting a closed account that the government later discovers could itself be grounds for denial. Do audit your online presence carefully, with an immigration attorney if possible. Understand that the ten-year window means posts from 2016 could surface in a 2026 adjudication.

And recognise the uncomfortable truth at the centre of this policy: the government has created a screening standard without telling anyone what it screens for. Until that changes — through legislation, litigation, or the FOIA process — every visa applicant is guessing."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        print(f"   Headline: {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
