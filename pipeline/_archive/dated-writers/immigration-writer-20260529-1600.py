#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-05-29 16:00 UTC run."""
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


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Green Card Fingerprints Just Expired — USCIS Is Re-Running Every Background Check in the System",
        "subheadline": "An enhanced FBI security vetting process that took effect April 27 has frozen approvals across hundreds of thousands of pending immigration cases. Indian applicants, who already face the longest waits in the system, are bearing the heaviest burden.",
        "slug": make_slug("uscis-fbi-fingerprint-revetting-green-card-freeze-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold the largest share of pending employment-based I-485 applications in the USCIS pipeline. With EB-2 India already retrogressed by ten months in the June visa bulletin, the fingerprint re-vetting adds a second layer of delay — one that could push cases past fiscal year cutoffs and waste visa numbers that took decades of waiting to reach.",
        "tags": ["uscis", "fbi", "fingerprint", "green-card", "i-485", "background-check", "delays"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Morgan Lewis LawFlash", "url": "https://www.morganlewis.com/pubs/2026/04/uscis-fingerprint-delays-expected-impact-on-green-card-processing-and-backlog"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/us-mandates-what-it-calls-enhanced-security-checks-immigration-applicants-2026-04-29/"},
            {"name": "Clark Hill PLC / JD Supra", "url": "https://www.jdsupra.com/legalnews/uscis-announces-enhanced-security-9283746/"},
            {"name": "Envoy Global", "url": "https://www.envoyglobal.com/resources/uscis-implements-new-fingerprint-based-security-checks"},
            {"name": "Goel & Anderson Immigration Law", "url": "https://www.goellaw.com/blog/uscis-fingerprint-re-vetting-2026"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8382611/pexels-photo-8382611.jpeg",
        "body": """On April 27, USCIS flipped a switch that nobody outside the agency saw coming. Every pending immigration application requiring fingerprint-based background checks — green cards, naturalizations, asylum cases, family-based petitions — was quietly placed under an adjudication hold while the agency re-runs each applicant's prints through a new enhanced FBI security system.

No press conference. No Federal Register notice. Just an internal memo directing officers to stop approving cases until the new checks cleared.

## What Actually Changed

The technical change sounds mundane: USCIS upgraded its connection to the FBI's Next Generation Identification (NGI) system to receive "enhanced criminal history record information" with every fingerprint submission. The practical consequence is anything but mundane.

Every pending case where fingerprints were collected before April 27 must now be resubmitted through the new system. Officers cannot approve a case — even one fully adjudicated and ready for a green card — until the enhanced check clears. Newly filed cases go to the back of the queue, behind the mountain of re-vetting that must happen first.

"Given the extraordinarily large volume of cases that will require fingerprint processing, this new system is expected to result in substantial adjudication delays," Morgan Lewis wrote in an April 30 advisory, one of the first law firms to flag the change publicly.

The only exception so far: naturalization cases where oath ceremonies were already scheduled. Everything else waits.

## The Scale of the Problem

USCIS does not publish real-time pending case counts broken down by application type and fingerprint status. But the scope is staggering. The agency had 12 million pending applications as of early 2026, according to Democratic lawmakers who recently demanded answers from the agency. Even if only a fraction require fingerprint-based vetting, the re-submission queue could easily number in the millions.

Reuters confirmed the policy through an internal USCIS email sent to the Refugee, Asylum and International Operations Directorate, reporting that "USCIS will begin receiving enhanced criminal history record information (CHRI) for all fingerprint-based background checks submitted to the FBI's Next Generation Identification system."

The directive traces back to an executive order signed in February requiring DHS immigration authorities to "access criminal history record information in the custody of federal criminal justice agencies to the maximum extent permitted by law."

## Why Indian Applicants Get Hit Hardest

For most green card applicants from other countries, the delay is an inconvenience measured in weeks or months. For Indians, it compounds decades of existing dysfunction.

Indian nationals account for the largest share of pending employment-based I-485 (adjustment of status) applications. The EB-2 India category just lost ten months of priority date progress in the June 2026 visa bulletin. Many Indian applicants filed their I-485s years ago and have been patiently waiting for their priority dates to become current — only to now face an additional bureaucratic hold that has nothing to do with their individual cases.

The timing is particularly cruel. Fiscal year 2026 ends September 30. Every day an approval sits frozen is a day closer to the annual visa number expiration deadline. If USCIS cannot clear the re-vetting backlog fast enough, visa numbers that were supposed to go to Indian applicants who have waited 10, 15, or 20 years could simply evaporate — unused.

And the fingerprint re-vetting comes on top of the May 21 adjustment of status memo, which instructs officers to treat in-country green card processing as "extraordinary discretionary relief." Indian H-1B holders are now facing a one-two punch: a policy memo that questions their right to adjust status domestically, and a procedural freeze that prevents their cases from being decided at all.

## What Immigration Lawyers Are Seeing

Clark Hill, a national law firm tracking the rollout, noted an additional wrinkle: officers have reportedly been told not to initiate new fingerprint checks for cases they intend to deny. In other words, the enhanced screening is focused on cases moving toward approval — meaning denials may actually speed up while approvals grind to a halt.

The firm also warned that greater access to detailed criminal history data could increase the volume of Requests for Evidence and Notices of Intent to Deny, "including for matters that previously drew less attention, such as non-conviction arrests, juvenile records, or sealed cases."

For the average Indian tech worker with a clean record, this is unlikely to surface new issues. But for anyone who has ever had a traffic-related arrest, a dismissed misdemeanor, or even a fingerprint mismatch — scenarios more common than you might think after a decade or more in the U.S. — the enhanced system could generate unexpected complications.

## What You Can Do

Immigration attorneys are advising clients to take several practical steps:

**Check your case status regularly.** The USCIS online portal will not flag the fingerprint hold specifically, but unusual delays in processing after an interview may signal the re-vetting queue.

**Do not file new biometrics proactively.** USCIS is resubmitting prints internally using what is already on file. Unless USCIS specifically contacts you, no action is required.

**If you have a pending I-485 and your priority date is current**, consult an attorney about whether filing a congressional inquiry or ombudsman complaint could help move your case out of the hold queue. These mechanisms have historically been effective at unsticking individual cases.

**Plan for extended processing times.** If your work authorization depends on a pending I-485 (via an EAD combo card), ensure your renewal is filed well in advance. Expired EADs during the re-vetting freeze could leave you unable to work.

The administration has characterized the delays as temporary. USCIS has not, however, provided any timeline for when the re-vetting backlog will clear. For Indian applicants who have built careers, bought homes, and raised families in the United States while waiting for a green card, "temporary" is a word that lost its meaning a long time ago."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Years and Out — The Proposed Rule That Could End 'Duration of Status' for Every Indian Student in America",
        "subheadline": "The White House is reviewing a DHS proposal to replace the open-ended student visa framework with fixed four-year terms. For the 330,000 Indian students in the U.S., it would mean reapplying for permission to stay — or leaving.",
        "slug": make_slug("duration-of-status-f1-four-year-limit-indian-students"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the second-largest international student population in the U.S. and the fastest-growing segment of F-1 visa holders. A four-year cap would disproportionately affect those pursuing multi-year PhD programs, post-doctoral research, and STEM OPT extensions — the very pipeline that feeds the H-1B workforce.",
        "tags": ["f1-visa", "duration-of-status", "student-visa", "indian-students", "opt", "stem"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Visa Lawyer Blog (Sapochnick)", "url": "https://www.visalawyerblog.com/category/non-citizens/"},
            {"name": "Fakhoury Global Immigration", "url": "https://fakhouryglobal.com/fgi-update-this-weeks-summary-of-u-s-and-global-immigration-news/"},
            {"name": "GyanDhan Connect", "url": "https://discussions.gyandhan.com/newsverse/upcoming-u-s-immigration-rule-may-end-or-limit-opt-for-international-students"},
            {"name": "CollegeChalo", "url": "https://collegechalo.com/articles/trump-visa-crackdown-6000-international-student-visas/"},
            {"name": "RegInfo.gov (RIN 1653-AA95)", "url": "https://www.reginfo.gov/public/do/eAgendaViewRule?pubId=202510&RIN=1653-AA95"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg",
        "body": """Since 1975, international students on F-1 visas have operated under a simple principle: stay enrolled, stay legal. The framework — known as "duration of status" — means an F-1 holder can remain in the United States for as long as they are pursuing a full course of study at an approved institution, without needing to reapply for a fixed term of admission.

That half-century arrangement is now under direct threat. The White House Office of Information and Regulatory Affairs is reviewing a proposed DHS rule (RIN 1653-AA95) that would replace duration of status with a fixed four-year admission period. After four years, students would need to apply for an extension — a process that introduces new opportunities for denial, new paperwork, new fees, and new anxiety.

## What the Rule Would Do

The proposed regulation, submitted by DHS to the White House for review in May, would impose a maximum four-year period of admission for F-1 students. Some categories of exchange visitors on J visas and foreign media representatives on I visas would also be affected.

Under current rules, a student admitted in F-1 status is authorized to remain for the "duration of status" — essentially, until they complete their program, graduate, and exhaust any post-completion work authorization. A PhD student who spends six years on their dissertation, then three years on STEM OPT, is covered the entire time by their original admission.

Under the proposed rule, that same student would need to apply for an extension after four years. If the extension is denied — or simply delayed past the expiration date — the student falls out of status. They become unlawfully present. They may be barred from re-entering the United States for three or ten years, depending on how long the overstay lasts.

The rule does not eliminate the F-1 visa category or immediately change anyone's enrollment. But it transforms the student visa from an open-ended permission tied to academic progress into a fixed-term authorization subject to government renewal.

## The Numbers Tell the Story

Indian students are at the center of this change. According to Open Doors data, more than 330,000 Indian students were enrolled in U.S. institutions in the 2024-25 academic year, making India the second-largest source country after China. Indian enrollment has been growing at double-digit rates, driven overwhelmingly by STEM graduate programs — exactly the programs most likely to exceed four years.

A typical Indian PhD candidate in computer science, electrical engineering, or biotechnology spends five to seven years in their program. Add a year of OPT and up to two years of STEM OPT, and you are looking at a student who might need to apply for extensions two or even three times during their academic career in the United States.

Each extension is a decision point where the government can say no. And in the current enforcement climate — where 6,000 student visas were revoked in a single sweep in 2025, where USCIS Director Joseph Edlow has publicly questioned the legal basis for OPT, where social media screening is now mandatory for H-1B and H-4 applicants — each decision point carries real risk.

## The OPT Connection

The duration of status rule does not directly change OPT or STEM OPT. But immigration analysts have flagged the connection. If duration of status is replaced with fixed terms, DHS could deny extension requests for students approaching the end of their program — effectively cutting off their eligibility for OPT before they graduate.

The Fakhoury Global Immigration analysis put it bluntly: "Replacing 'duration of status' with fixed visa terms could make it difficult for students to transition to OPT, as DHS could deny extension requests or subject applicants to increased vetting and scrutiny."

This matters because OPT and STEM OPT are the primary bridge between an Indian student's academic career and their entry into the U.S. workforce. Without OPT, there is no practical path from an F-1 to an H-1B for most Indian graduates. Kill duration of status, and you create a mechanism to strangle OPT without ever formally eliminating it.

## What Parents and Students Should Know

The rule is still in the review stage. It has not been published as a proposed rule in the Federal Register, which means there will be a public comment period before it can take effect. Immigration attorneys expect legal challenges if DHS moves forward, given that duration of status has been in continuous use for five decades and courts have generally upheld the government's discretion to maintain it.

But "still in review" is not the same as "unlikely to happen." This administration has moved faster on immigration enforcement changes than any in recent memory. The weighted H-1B lottery, the $100,000 fee for certain employers, the adjustment of status memo, the enhanced FBI fingerprint checks — all went from proposal to implementation in months, not years.

For Indian families currently planning to send a son or daughter to a U.S. university, the practical implications are worth considering:

**Program length matters more than ever.** A two-year master's program fits comfortably within a four-year window including OPT. A PhD program does not. Students in longer programs should factor in the possibility of extension applications, including the cost (potentially hundreds of dollars in fees) and the risk of denial.

**Alternative destinations are real options.** Canada's Post-Graduation Work Permit gives graduates up to three years of open work authorization without renewal. Germany's EU Blue Card offers permanent residency eligibility in as little as 21 months. The UK's Graduate Route provides two years of post-study work. Each of these countries is actively recruiting the same Indian STEM talent that the U.S. system is making harder to retain.

**Current students are not yet affected.** The rule must go through the formal rulemaking process before it applies to anyone. Students currently enrolled under duration of status should continue their programs as planned. But they should also keep documentation meticulous and stay in close contact with their Designated School Official in case the landscape shifts.

The broader pattern is hard to miss. The H-1B lottery was restructured to favor higher wages. OPT is under formal review for elimination. The adjustment of status pathway to a green card was just reclassified as "extraordinary discretionary relief." And now the foundational framework that allows international students to complete their education in the United States may be converted into a fixed-term permission that the government can revoke every four years.

Each policy change, taken individually, has a defensible rationale. Taken together, they form a systematic narrowing of every pathway that connects an Indian student's arrival in the United States to their eventual permanent residency. The question Indian families are increasingly asking is not whether any single rule will pass — it is whether the cumulative trajectory leaves any viable path at all."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
