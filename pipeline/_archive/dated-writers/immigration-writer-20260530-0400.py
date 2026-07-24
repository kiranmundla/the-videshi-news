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
        "headline": "They Showed Up Without Calling — Inside the USCIS Site Visit Surge That's Putting H-1B Workers on Deportation Watch",
        "subheadline": "FDNS officers are visiting more workplaces than ever, and for the first time, a failed site visit can trigger removal proceedings — not just a denied petition.",
        "slug": make_slug("uscis-fdns-site-visits-h1b-deportation-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold roughly 73% of all H-1B visas. Every uptick in site visit volume lands disproportionately on Indian workers and the companies that sponsor them — from TCS and Infosys to mid-size IT consultancies across the Sun Belt.",
        "tags": ["h1b", "uscis", "fdns", "site-visits", "immigration", "deportation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "GreenCardMaker Weekly Update", "url": "https://www.greencardmaker.com/blog?page=1"},
            {"name": "BAL - Berry Appleman & Leiden", "url": "https://www.bal.com/"},
            {"name": "Holland & Knight", "url": "https://www.hklaw.com/en/insights/publications/2014/04/unexpected-uscis-site-visits-expanded-to-l-visa-hol"},
            {"name": "Foley & Lardner", "url": "https://www.foley.com/insights/publications/2017/04/h1b-sponsors-prepare-for-site-visits-and-increased/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7731326/pexels-photo-7731326.jpeg",
        "body": """The knock comes without warning. No appointment, no email, no letter. A USCIS Fraud Detection and National Security officer walks into your office lobby, asks the receptionist for you by name, and wants to see where you sit, what you do, and whether the job described in your H-1B petition matches the work you actually perform.

This is an FDNS site visit, and in 2026, they are happening more frequently, more aggressively, and with far higher stakes than at any point in the program's history.

## The numbers behind the surge

USCIS has not published a formal count of FY-2026 site visits — the agency never does — but the signals are unmistakable. Immigration attorneys at firms including BAL, Fragomen, and Holland & Knight report a sharp increase in both random administrative visits and targeted compliance inspections since January 2026. The FDNS unit has been expanding its investigator headcount steadily, and the Trump administration's December 2024 final rule on H-1B modernization formally codified USCIS authority to conduct unannounced visits at headquarters, satellite offices, and third-party worksites.

The GreenCardMaker weekly immigration briefing for May 29, 2026, flagged the trend explicitly: "USCIS Site Visits Are Increasing: How H-1B and L-1 Employees and Employers Can Prepare and Avoid Visa Revocation, NTA Proceedings, and Possible Deportation."

That last phrase — possible deportation — is the new part.

## What changed: from denial to removal

Under previous administrations, a failed site visit typically resulted in a Request for Evidence, a petition denial, or at worst, a revocation of the approved H-1B. The worker could seek a new sponsor, change status, or depart voluntarily.

The current enforcement posture has expanded the consequences. USCIS officers are now authorized to refer cases directly to ICE when site visits reveal potential fraud — and "fraud" can include discrepancies as routine as a mismatch between the job title on the petition and the actual duties performed, or a worker sitting at a different office than the one listed on the Labor Condition Application.

A referral can trigger a Notice to Appear in immigration court, placing the worker in formal removal proceedings. For an Indian H-1B holder who has been in the United States for eight or ten years, waiting in the EB-2 or EB-3 green card backlog, a single NTA can collapse a decade of careful immigration planning.

## Who gets visited

FDNS runs two kinds of site visits. Administrative visits under the ASVVP program are random — a statistical sample designed to measure baseline compliance. Targeted visits are triggered by tips from USCIS adjudicators who spot anomalies in petitions, referrals from State Department consular officers, or flags from the USCIS Validation Instrument for Business Enterprises system.

Three employer categories face elevated scrutiny in 2026:

**H-1B dependent employers** — companies where more than 15% of the workforce holds H-1B status. This captures most of the large Indian IT services firms operating in the United States.

**Third-party placement firms** — any company that staffs H-1B workers at client sites. The December 2024 final rule limits initial H-1B petitions and first extensions to 18 months for third-party placements, and site visits now verify that the worker is actually performing the described specialty occupation at the listed client.

**Employers filing senior roles for recent graduates** — a pattern USCIS has flagged since early 2026, where a petition describes a Level III or Level IV wage role but the beneficiary has fewer than two years of post-graduation experience.

## What the officer asks

FDNS investigators follow a structured protocol, but the questions are deliberately open-ended. Workers should expect to be asked about their specific daily tasks, their reporting chain, the tools and technologies they use, their work schedule, and their salary. Officers may also ask to see the physical workspace, review project documentation, and interview coworkers or supervisors.

The investigator is comparing every answer against the petition filed with USCIS. A software engineer whose petition says "designs and implements machine learning models" but who describes spending most of the day on manual QA testing creates exactly the kind of discrepancy that generates a targeted follow-up — or worse.

## What Indian workers should do now

**Review your own petition.** Request a copy of your approved I-129 and the supporting Labor Condition Application from your employer. Read the job description, the stated duties, the work location, and the wage level. If any of those have changed since the petition was filed, your employer may need to file an amended petition before a site visit catches the gap.

**Know your LCA posting.** Your employer is required to post the LCA at your worksite. If you work at a client site, the LCA must be posted there too. If you have never seen it, ask your employer's immigration counsel.

**Coordinate with your employer.** Frontline staff — receptionists, office managers, security guards — should know that FDNS visits are legitimate government inspections and should not turn officers away or refuse access. Refusal to cooperate with a site visit can itself be grounds for petition revocation under the codified rules.

**Do not volunteer information beyond the question asked.** Be truthful, precise, and brief. If the investigator asks what you do, describe your current duties accurately. Do not speculate about company strategy, other employees' immigration status, or topics outside the scope of your petition.

The FDNS surge is not a crackdown on a specific nationality. But with roughly 400,000 Indians currently holding H-1B status in the United States — by far the largest national cohort — any increase in enforcement volume lands heaviest on this community. And in an environment where a site visit finding can now cascade into removal proceedings, the margin for administrative sloppiness has disappeared entirely."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The July Visa Bulletin Forecast Is Out — and EB-2 India Is Just the Beginning",
        "subheadline": "EB-2 India is formally unavailable through September 30. EB-1 India is retrogressing further. EB-5 Unreserved India faces the State Department's most aggressive warning language of the fiscal year.",
        "slug": make_slug("july-visa-bulletin-eb2-india-unavailable-eb1-eb5-risk"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals in the EB-2 category — the single largest pool of employment-based green card applicants — face a complete shutdown of approvals for at least four months. With EB-1 India also contracting, the traditional escape routes are narrowing simultaneously.",
        "tags": ["green-card", "visa-bulletin", "eb2", "eb1", "eb5", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge - July 2026 Visa Bulletin Forecast", "url": "https://www.visaverge.com/visa-bulletin/july-2026-visa-bulletin-complete-analysis-and-forecast/"},
            {"name": "EB5 Beyond - EB-2 India Unavailable", "url": "https://www.eb5beyond.com/"},
            {"name": "Wolfsdorf Rosenthal - India EB-2 and EB-3 Analysis", "url": "https://www.wolfsdorf.com/"},
            {"name": "VisasUpdate - EB-2 India 2026", "url": "https://www.visasupdate.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """On May 22, 2026, the State Department's Visa Office posted a terse, definitive announcement: India's per-country limit in the EB-2 category had been reached for Fiscal Year 2026. That single sentence locked out tens of thousands of Indian professionals from green card approvals for the rest of the fiscal year — and the July Visa Bulletin, due in mid-June, will make the damage official across three employment-based categories simultaneously.

This is not a retrogression. It is a shutdown.

## EB-2 India: mathematically dead until October

When a per-country limit is exhausted, the State Department lists the affected cell as "U" — Unavailable — on both the Final Action chart and the Dates for Filing chart. For EB-2 India, that designation will appear in every remaining bulletin of FY-2026: July, August, and September. No EB-2 India immigrant visa can be issued at any consulate worldwide. No EB-2 India adjustment of status application can be approved by USCIS. The category resets on October 1, 2026, when Fiscal Year 2027 begins.

The June bulletin already showed the damage: the EB-2 India Final Action Date had collapsed from July 15, 2014 in May to September 1, 2013 in June — a retrogression of more than ten months in a single bulletin. Former State Department official Charlie Oppenheim had warned for months that the forward movement earlier in FY-2026 was "completely artificial," driven by the administration's suspension of visa processing in 75 countries. Those unused visa numbers had briefly flowed to India, inflating priority dates. The correction was inevitable; its severity was not.

For the roughly 400,000 Indians with pending EB-2 petitions, the practical question is narrow: what still works during the unavailability window?

The answer is more than nothing. Pending I-485 applications remain on file — USCIS does not deny them. Employment Authorization Documents issued under pending adjustment continue to be valid. Advance parole travel documents remain active. H-1B portability under AC21 is unaffected. The green card simply cannot be stamped until a visa number becomes available again.

## EB-1 India: the next domino

With EB-2 India exhausted, demand pressure is migrating upward to EB-1. The June bulletin already retrogressed EB-1 India by 107 days, pulling the Final Action Date from April 1, 2023 to December 15, 2022. The State Department's own Section E language was unambiguous: "further retrogressions, or making the categories unavailable, may be necessary in the coming months."

Attorney forecasts from Wolfsdorf Rosenthal, Fragomen, BAL, Shusterman, and Murthy converge on a July EB-1 India Final Action Date somewhere between August and October 2022 — a further two to five month pull-back from the June date. A formal "U" listing for EB-1 India before September 30 is also on the table if the category approaches its own pro-rated annual limit.

This matters directly to Indian professionals who pivoted to EB-1A (extraordinary ability) or EB-1C (multinational manager) as alternatives to the EB-2 backlog. The escape hatch is narrowing.

## EB-5 Unreserved India: the sharpest warning in the bulletin

The June bulletin used the State Department's most aggressive warning language of the fiscal year in Section H, specifying "the next month" — not the vaguer "coming months" applied to other categories. That timing-specific phrasing is the State Department's telegraph for imminent action.

The likely July outcome for EB-5 Unreserved India is either a meaningful retrogression from the current May 1, 2022 Final Action Date back into late 2020 or early 2021, or an outright "U" listing through September 30. The EB-5 set-aside categories — Rural, High Unemployment, and Infrastructure — are statutorily separate and remain Current. They are not affected by this warning.

For Indian investors who routed through the unreserved EB-5 path to avoid the employment-based backlogs, the July bulletin could eliminate that advantage for the rest of the fiscal year.

## The EB-3 downgrade trap

When EB-2 India goes unavailable, the instinctive reaction is to consider downgrading to EB-3 India. The math does not support it. EB-3 India's predicted July Final Action Date is approximately January 15, 2014 — a full year behind EB-2 India's last active date. Most EB-2 India applicants have priority dates well past 2014, making a downgrade counterproductive.

Immigration attorneys describe it as trading a frozen queue for a longer one.

## What to watch in mid-June

The July 2026 Visa Bulletin is expected to publish in mid-June. Three things will determine how bad the quarter gets:

**EB-1 India's Final Action Date.** If it pulls back past October 2022 or lists as "U," the entire employment-based pipeline for Indian nationals will be functionally closed across three preference categories simultaneously.

**EB-5 Unreserved India's disposition.** A retrogression is painful; an unavailability designation is a complete halt. The Section H language strongly suggests one of the two.

**USCIS chart determination.** USCIS has used Final Action Dates for employment-based adjustment of status for two consecutive months. A switch back to the more permissive Dates for Filing chart is unlikely given the unavailability landscape, but any movement here affects who can file new I-485s.

For the Indian diaspora, the message from the July forecast is structural, not tactical. The per-country cap system that allocates identical visa quotas to India (population 1.4 billion) and Iceland (population 380,000) continues to produce outcomes that no amount of individual planning can overcome. The artificial forward movement earlier this fiscal year briefly disguised that reality. The correction has now arrived, and it will hold through at least September 30."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
