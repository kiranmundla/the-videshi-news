#!/usr/bin/env python3
"""Immigration writer — 2026-06-27 01:00 PDT run"""
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

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: H-4 EAD Program Rescission
# ──────────────────────────────────────────────────────────────────────

article1_body = """For a decade, the H-4 Employment Authorization Document gave spouses of certain H-1B workers something that sounds ordinary but was, in practice, revolutionary: the right to hold a job. Now the Department of Homeland Security is in the final stages of drafting a proposed rule that would end the programme altogether — and for the overwhelmingly Indian families who depend on it, the clock has started ticking.

DHS disclosed the status of the regulation in a filing with the U.S. Court of Appeals for the District of Columbia Circuit, where the long-running case *Save Jobs USA v. DHS* has been held in abeyance while the government prepares its move. The proposed rule was originally due in February but was pushed back while DHS completed an economic-impact analysis. The agency now says it is in the "final stages of clearance" before being sent to the Office of Management and Budget for review, with publication expected imminently.

## What the programme does — and who uses it

The H-4 EAD programme, created by the Obama administration in 2015, allows spouses of H-1B workers to apply for work authorisation under two conditions: the H-1B holder must have an approved I-140 immigrant petition, or must have received an H-1B extension beyond the standard six-year limit under the American Competitiveness in the Twenty-First Century Act.

In practice, this carves out a narrow but critical group — and roughly 90 per cent of its beneficiaries are Indian nationals. The reason is structural. Per-country caps on employment-based green cards mean Indian applicants in the EB-2 and EB-3 categories face wait times measured not in years but in decades. During that wait, the H-4 EAD has been the only mechanism allowing their spouses to work, contribute to household income, and maintain career continuity.

The numbers are not trivial. An estimated 100,000 H-4 visa holders currently hold valid EADs. Their incomes help cover mortgages, childcare, health insurance, and retirement savings in some of the most expensive metro areas in the country — the Bay Area, Seattle, New Jersey, northern Virginia. A dual-income household that reverts to single-earner status does not merely tighten its belt. For many, it breaks the financial model that made staying in the United States viable at all.

## A two-front attack on work authorisation

The H-4 EAD rescission does not arrive in isolation. It lands alongside a separate final rule — already at OMB for review — that would end automatic extensions of employment authorisation documents across 18 categories of noncitizens, including H-4 spouses. Under the current system, an H-4 EAD holder who files a timely renewal continues working while USCIS processes the application. Remove that automatic extension, and any gap between an expiring EAD and a pending renewal forces the spouse to stop working immediately, regardless of whether the renewal is approved weeks later.

Combined, the two regulatory actions create a pincer: the auto-extension rule opens a gap; the rescission rule closes the door. Immigration attorneys are urging eligible H-4 spouses to file EAD renewals as soon as they become eligible — up to six months before their current document expires — and to consider whether alternative visa classifications, such as an H-1B in their own name or an O-1 for extraordinary ability, might offer a more durable pathway.

## What happens next

Once OMB completes its review, DHS will publish the proposed rule in the Federal Register and open a public comment period, typically 30 to 60 days. After reviewing feedback, the agency will issue a final rule. There is no fixed timeline for that last step, but the administration has listed the rescission among its key regulatory priorities, which suggests an aggressive schedule.

The proposed rule would not take effect immediately upon publication. USCIS is expected to continue accepting and adjudicating H-4 EAD applications under current rules until the final regulation is implemented. But the window is narrowing, and immigration law firm Fragomen has warned that "termination of the programme could come within months of the release of the proposal."

For Indian families who built their American lives around the expectation that both partners could work, the message from Washington is clear enough: that expectation was always conditional, and the condition is about to change."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-4 Work Permit Was Never Guaranteed. Now DHS Is Drafting the Rule to End It",
    "subheadline": "The agency told a federal appeals court it is in the final stages of rescinding the programme that gave work authorisation to spouses of H-1B workers — a programme used overwhelmingly by Indians stuck in the green card backlog.",
    "slug": make_slug("h4-ead-rescission-dhs-final-stages-indian-spouses-work-permit"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "About 90% of H-4 EAD holders are Indian nationals whose spouses face decades-long green card waits — losing work authorisation would upend dual-income households across the Bay Area, Seattle, and the Northeast.",
    "tags": ["h4-ead", "uscis", "immigration", "h1b", "green-card-backlog", "indian-spouses"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/proposal-to-rescind-h-4-ead-regulation-moves-closer-to-completion.html"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/proposal-to-rescind-h-4-ead-program-could-come-soon.html"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/dhs-advances-rule-nixing-automatic-renewal-of-work-permits"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/h-4-ead-automatic-extension-2026-sj-res-99-senate-update/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8837770/pexels-photo-8837770.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A professional at work — for roughly 100,000 H-4 visa holders in the US, the right to hold a job may soon be rescinded",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: Day-1 CPT Crackdown
# ──────────────────────────────────────────────────────────────────────

article2_body = """It was never in the statute. It was never endorsed by USCIS. But for tens of thousands of Indian tech professionals stuck in the H-1B lottery's annual rejection cycle, Day-1 Curricular Practical Training became the immigration system's unofficial Plan B — enrol in a second master's programme, receive work authorisation on the first day of classes, and keep your career alive while you wait for next year's draw. Now the Department of Homeland Security's proposed student visa overhaul threatens to shut the door on the arrangement, and for the community that depends on it most, there is no obvious Plan C.

## How the backup plan works

Day-1 CPT exploits a gap in the regulatory architecture. Curricular Practical Training allows F-1 students to work in positions related to their field of study as part of their academic curriculum. Most students use it during or after completing a degree. But a growing number of accredited — and, critics say, dubiously accredited — universities began offering programmes designed specifically for working professionals who already held master's degrees and needed a new F-1 status to maintain legal work authorisation.

The model is straightforward: a student who completes an MS in computer science, enters the H-1B lottery, loses, and faces the end of their OPT or STEM OPT enrols in a second graduate programme at a CPT-friendly university. On day one, the university issues CPT authorisation. The student continues working at their existing employer while nominally pursuing another degree. The arrangement is technically legal — the university is accredited, the programme exists, the CPT is tied to a curriculum requirement — but it stretches the intent of the F-1 visa beyond what most regulators consider reasonable.

For Indian professionals, the arithmetic is simple. The H-1B lottery's selection rate hovers around 25 to 30 per cent in any given year. Under the new wage-weighted system that prioritises higher-salaried positions, mid-career workers at staffing or consulting firms face even steeper odds. With EB-2 and EB-3 India green card queues stretching past 2060, Day-1 CPT is not a shortcut — it is the only bridge between losing the lottery and leaving the country.

## What the proposed rules would change

On May 5, 2026, DHS submitted a proposed rule to OMB that would replace the current "Duration of Status" framework for F-1 student visas with a fixed admission period of up to four years. The rule cleared OMB review on June 17 and is expected to be published in the Federal Register imminently.

Among its provisions, the proposed rule would require students seeking programme extensions, transfers, or enrolment at a new degree level to file an Extension of Stay application with USCIS — replacing the current system where Designated School Officials at each university managed these changes internally. For anyone who already holds a master's degree, the practical effect is severe.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration services firm, in an interview with The Indian Eye.

The proposed rule would also reduce the grace period available to F-1 students after their status ends from 60 days to 30 days, further compressing the window to find an alternative pathway.

## The talent pipeline at stake

Goldman warned that the impact extends beyond students to the employers who hire them. Indian nationals constitute the largest international student group in the United States, with 363,019 enrolled in the 2024-25 academic year and 143,740 participating in OPT programmes. They dominate the AI, machine learning, software engineering, and data science talent pools that American tech companies say they cannot fill domestically.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," Goldman said. "The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions."

Those alternatives — cap-exempt H-1B positions at universities or research institutions, O-1 visas for individuals with extraordinary ability, or the increasingly difficult EB-1A and NIW self-petition routes — exist, but none of them scale to absorb the tens of thousands of professionals who currently rely on Day-1 CPT to remain in the workforce.

## What comes next

The proposed rule has not yet been published, and it will take effect 60 days after publication in the Federal Register. Universities and immigration advocacy groups are expected to challenge it, with NAFSA already preparing to document the concrete harms the regulation would impose on students, institutions, and employers.

But for Indian professionals currently enrolled in Day-1 CPT programmes or planning to use one as their fallback, the advice from immigration attorneys is urgent: do not assume the pathway will remain open. Explore O-1 eligibility, consider whether your employer can sponsor a cap-exempt H-1B, and — most importantly — do not let a grace period expire without a plan. The unofficial Plan B was always borrowed time. Washington just served the eviction notice."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Day-1 CPT Was the H-1B Lottery's Backup Plan. The Proposed Rules Would Kill It",
    "subheadline": "Tens of thousands of Indian tech professionals use a shadow enrolment system to keep working after losing the H-1B lottery. DHS's proposed student visa overhaul would close the loophole for good.",
    "slug": make_slug("day-1-cpt-crackdown-dhs-student-visa-h1b-indians-backup-plan"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Day-1 CPT is the de facto survival mechanism for Indian tech workers who lose the H-1B lottery year after year — with green card waits stretching past 2060, killing it would force tens of thousands out of the US workforce.",
    "tags": ["cpt", "f1-visa", "h1b-lottery", "uscis", "immigration", "indian-students", "day-1-cpt"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/06/us-to-end-duration-of-status-for-f-and-j-visas/"},
        {"name": "Northeastern University OGS", "url": "https://international.northeastern.edu/ogs/dhs-proposed-rule-on-f-and-j-duration-of-status/"},
        {"name": "Marquette University", "url": "https://today.marquette.edu/2026/05/international-students-and-scholars-updates-legal-resources-travel-guidance/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/27623232/pexels-photo-27623232.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A graduate student on a university campus — for many Indian professionals, re-enrolling in a second degree is the only way to stay and work in the US",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ──────────────────────────────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
