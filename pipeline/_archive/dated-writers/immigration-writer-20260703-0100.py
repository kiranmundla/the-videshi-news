#!/usr/bin/env python3
"""Immigration writer — July 3 2026, 01:00 PDT run."""
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1 — Mandatory Detention Circuit Split
# ──────────────────────────────────────────────────────────────────────
art1_body = """\
The 5th U.S. Circuit Court of Appeals ruled on Thursday that Immigration and Customs Enforcement cannot hold immigrants for more than 90 days under the Trump administration's mandatory detention policy without giving them a chance to seek release on bond. The 2-1 decision, handed down by a New Orleans-based panel, is the latest blow to the administration's aggressive reinterpretation of a federal immigration statute — and it virtually guarantees the Supreme Court will have the final word.

Judge Leslie Southwick, a George W. Bush appointee writing for the majority, grounded the ruling in the Fifth Amendment's due process clause. "It is part of the historic majesty of this long-ago founding charter that it makes no exceptions in providing basic rights to those within our boundaries, including a right to be heard when personal liberty is taken," Southwick wrote. Judge Cory Wilson, a Trump appointee, dissented, arguing the majority "marginalizes the Constitution's express grant of plenary authority over immigration matters to Congress."

## How We Got Here

For roughly three decades, the immigration system operated under a straightforward division. People apprehended at the border — "applicants for admission" — could be held in mandatory detention without a bond hearing. People arrested inside the country, even if undocumented, generally had the right to appear before an immigration judge and argue for release.

In 2025, the Trump administration upended that distinction. The Department of Homeland Security adopted a novel interpretation of 8 U.S.C. § 1225(b)(2)(A), declaring that non-citizens who entered without inspection — regardless of whether they had lived in the United States for years or decades — qualify as "applicants for admission" subject to mandatory detention. The Board of Immigration Appeals formalised the position in September 2025, and immigration judges across the country began ordering detention without bond hearings.

The legal backlash was immediate. More than 400 district judges, appointed by presidents of both parties, rejected the new reading. The cases then moved to the federal appeals courts, where the results have split.

## The Circuit Split: 4-2 and Widening

The scorecard is now lopsided. The Second, Sixth, Tenth, and Eleventh Circuits have all rejected the administration's mandatory detention policy. The 10th Circuit's decision, issued just days ago on June 30, explicitly called the policy constitutionally suspect: "There is little justification, let alone a strong one, for detaining every one of the millions of unadmitted noncitizens in our country," Judge Richard Federico wrote.

Only two circuits — the Fifth (in an earlier, separate panel ruling in February) and the Eighth — have sided with the government. Thursday's ruling creates an unusual situation: two panels of the same 5th Circuit have now reached opposite conclusions, with the February panel endorsing the detention policy and the July panel requiring bond hearings after 90 days.

The administration has already asked the Supreme Court to resolve the split, filing a certiorari petition last week.

## Why This Matters for Indian Americans

At first glance, mandatory detention might seem like a border-enforcement issue irrelevant to someone on an H-1B or holding a green card. It is not.

The administration's reinterpretation rests on the idea that anyone who entered without inspection — or whose status is questioned — can be classified as an "applicant for admission" and detained without a hearing. Immigration attorneys have flagged that this expansive reading creates risks even for long-term legal residents whose paperwork hits a snag, whose employer fails to file an extension on time, or who fall into a grey area during a status change.

In practical terms, the circuit split means your rights depend on geography. An Indian national detained by ICE in New York (Second Circuit) would likely get a bond hearing. The same person transferred to Louisiana (Fifth Circuit, under the February ruling) might not. Rebecca Cassler, a lawyer at the American Immigration Council, said the 5th Circuit's Thursday ruling was a step toward closing that gap, but until the Supreme Court speaks, the patchwork remains.

For the roughly 600,000 Indian nationals in the employment-based green card backlog — many of whom have lived in the United States for 15 or 20 years on H-1B extensions — the stakes are structural. Any disruption in status, even a bureaucratic delay, could theoretically trigger the mandatory detention framework. The Supreme Court's eventual ruling will determine whether the system treats long-term residents differently from people stopped at the border, or whether the distinction has been permanently erased.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Courts Said No. Two Said Yes. The Supreme Court Will Decide Who Gets a Bond Hearing",
    "subheadline": "The 5th Circuit ruled Thursday that ICE cannot detain immigrants beyond 90 days without a chance to seek release. With federal appeals courts split 4-2, the mandatory detention question heads to the nation's highest court.",
    "slug": make_slug("mandatory-detention-circuit-split-scotus-bond-hearing-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals in the employment-based green card backlog — many with 15-20 years of US residence — face structural risk from an expansive mandatory detention policy that could strip bond hearing rights based on geography alone.",
    "tags": ["immigration", "mandatory-detention", "supreme-court", "bond-hearing", "circuit-split", "h1b", "due-process"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trump-administration-cannot-hold-migrants-without-bond-hearings-past-90-days-2026-07-02/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/appeals-court-blocks-trump-admin-holding-migrants-without-bond-over-90-days"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/litigation/doj-migrant-mandatory-detention-policy-rejected-at-tenth-circuit"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3399879-court-clampdown-on-mandatory-detention-appeals-court-ruling-shakes-up-immigration-policy"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
    "image_caption": "The United States Supreme Court building at dusk in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2 — Duration of Status Proposed Rule / OPT Overhaul
# ──────────────────────────────────────────────────────────────────────
art2_body = """\
On May 5, the Department of Homeland Security published a proposed rule that would fundamentally alter how international students live and work in the United States. The measure would scrap "Duration of Status" — the decades-old framework that allows F-1 visa holders to remain in the country as long as they maintain valid student status — and replace it with a hard four-year admission cap. Extensions beyond that window would require a formal application to USCIS and its chronically overstretched adjudication machinery.

The implications ripple well beyond paperwork. For Indian students, who form one of the largest contingents of international enrolees in the United States and account for a disproportionate share of H-1B lottery applicants, the proposed rule threatens to dismantle the network of workarounds that has kept thousands employed between lottery attempts.

## What the Rule Would Change

Three provisions stand out.

**A fixed clock instead of an open-ended stay.** Under the current Duration of Status system, an F-1 student's authorised presence is tied to maintaining valid enrolment, not to a calendar date. The proposed rule would replace that with a maximum four-year admission period. Any student needing more time — to complete a PhD, say, or to use Optional Practical Training — would have to file an extension with USCIS, pay the associated fees, and wait for approval.

**A shorter grace period.** When a student's F-1 status ends — after completing a degree or finishing OPT — they currently have 60 days to either depart, change status, or secure new employment sponsorship. The proposed rule would cut that window to 30 days. Immigration attorneys say the compressed timeline would leave graduates with almost no room to pivot if an H-1B petition falls through or a job offer collapses.

**A narrower path through Day 1 CPT.** Curricular Practical Training programmes that allow students to work on the first day of a new academic programme — commonly known as "Day 1 CPT" — have become a critical backstop for Indian engineers who fail the H-1B lottery. Thousands enrol in a second master's degree, often at schools that specialise in the arrangement, to maintain work authorisation while they try the lottery again. The proposed rule would restrict this pathway by requiring students to demonstrate that any new programme of study is academically distinct from their prior degree, rather than simply a vehicle for continued employment.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration technology firm, in a recent interview.

## The Numbers Tell the Story

Participation in the OPT programme has more than doubled since 2007, reaching 418,781 authorised participants in 2024, according to the Congressional Research Service. The STEM OPT extension — which grants an additional 24 months of work authorisation for science, technology, engineering, and maths graduates — has been the primary driver. For Indian students in computer science, data science, and AI, STEM OPT is not a bonus; it is the expected pathway. Without it, a single failed H-1B lottery could mean departure.

Meanwhile, F-1 visa grants to Indian students fell 69 per cent in the most recent reporting period. Fewer students are arriving; now the ones already here would face a tighter system too.

## Why Indian Americans Should Pay Attention

The Duration of Status change would not affect people who already hold H-1B visas or green cards. But it would reshape the pipeline that feeds both.

Indian IT companies, which still account for a significant share of H-1B sponsorship despite a 40 per cent decline in approvals, recruit heavily from the pool of Indian graduates on OPT and STEM OPT. If that pool shrinks — because students leave rather than navigating a more complex extension process, or because Day 1 CPT is no longer viable — employers will feel the pinch. Goldman warned that companies hiring in AI and machine learning, where foreign nationals constitute a substantial share of the talent pool, would face the sharpest constraints.

For Indian families with children approaching university age in the United States, the calculus changes too. An international student pathway that once offered a plausible route from F-1 to OPT to H-1B to green card now looks like a series of narrowing doors, each with a higher fee and a longer wait.

The proposed rule is currently in a 60-day public comment period. Immigration advocacy groups have signalled they will challenge it in court if finalised. But given the administration's track record of pushing rules through despite litigation, students and employers would be wise to plan as if it takes effect.

Companies, Goldman advised, "will either struggle because they won't have the talent or they will have to get creative and find alternate solutions" — including cap-exempt H-1B positions at universities, O-1 visas for individuals with extraordinary ability, and direct green card sponsorship that bypasses the H-1B stage entirely.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "DHS Wants to End 'Duration of Status.' Indian Students Would Lose Their Safety Net",
    "subheadline": "A proposed rule would replace the open-ended stay framework for F-1 students with a hard four-year cap, halve the post-graduation grace period, and narrow the Day 1 CPT workaround that keeps thousands of Indian engineers employed between H-1B lottery attempts.",
    "slug": make_slug("duration-of-status-f1-opt-overhaul-indian-students"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students form the largest F-1 cohort using OPT and STEM OPT as a bridge to H-1B. Ending Duration of Status and restricting Day 1 CPT would eliminate the workarounds that keep thousands employed between lottery attempts.",
    "tags": ["f1-visa", "opt", "stem-opt", "cpt", "duration-of-status", "indian-students", "uscis", "dhs"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Congressional Research Service", "url": "https://www.congress.gov/crs-product/R47800"},
        {"name": "Lexology / DHS Regulatory Agenda", "url": "https://www.lexology.com/library/detail.aspx?g=dhs-to-propose-overhaul-of-opt-program-for-international-students"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7972741/pexels-photo-7972741.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "International graduates celebrating at a university commencement ceremony",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}


# ──────────────────────────────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
