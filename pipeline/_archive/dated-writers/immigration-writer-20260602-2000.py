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

def verify_image(url):
    """Verify image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            print(f"  ⚠️ Image returned {r.status_code}: {url[:80]}")
            return False
        ct = r.headers.get("Content-Type", "")
        if "image" not in ct:
            print(f"  ⚠️ Image Content-Type is {ct}: {url[:80]}")
            return False
        cl = int(r.headers.get("Content-Length", 0))
        if cl > 0 and cl < 5000:
            print(f"  ⚠️ Image too small ({cl} bytes): {url[:80]}")
            return False
        return True
    except Exception as e:
        print(f"  ⚠️ Image check failed: {e}")
        return False

# ============================================================
# ARTICLE 1: NVIDIA's H-1B Hiring Surge
# ============================================================

art1_body = """The numbers tell a story the immigration debate tends to miss. While Google's H-1B certifications fell 57 per cent year-over-year to roughly 2,200 and Amazon's dropped 30 per cent to about 4,300, NVIDIA pushed in the opposite direction — reaching approximately 1,200 certifications in the first half of Fiscal Year 2026, a 20 per cent increase from the year prior.

The divergence is not accidental. It is the predictable outcome of three policy shifts that, taken together, have redrawn the economics of sponsoring foreign workers in the United States.

## The $100,000 filter

The Presidential Proclamation signed in September 2025 imposed a $100,000 supplemental fee on certain H-1B petitions filed for workers applying from outside the country. For companies already under margin pressure or in the middle of layoff cycles, that surcharge effectively priced them out of overseas recruitment. For NVIDIA, whose Principal Research Scientists earn base salaries between $272,000 and $431,250 and whose Architecture Directors can command up to $488,750, the fee is a rounding error on total compensation.

The result is a kind of natural selection. Companies that pay at the top of the market can absorb the cost without flinching. Everyone else must rethink whether the petition is worth filing at all.

## The weighted lottery tilts the table

A final rule that took effect on February 27, 2026, replaced the random H-1B lottery with a wage-weighted selection system. Wage Level IV roles now have a four-times-greater chance of selection than Wage Level I positions. USCIS itself predicted a 48 per cent reduction in Level I selections and a 107 per cent increase in Level IV selections.

For Indian IT consulting firms and staffing companies — which historically sponsored large volumes of workers at lower wage levels — the new math is devastating. For NVIDIA and its peers competing for scarce AI and semiconductor talent at elite pay bands, the odds have never been better.

## What PM-602-0199 means for the pipeline

On May 21, 2026, USCIS issued Policy Memorandum PM-602-0199, reframing adjustment of status as an act of "administrative grace" rather than an entitlement. A clarification on June 1 softened the blow slightly: applicants who "provide an economic benefit or otherwise are in the national interest" would likely continue on their current path, while others might be directed to apply from abroad.

Read between the lines and the two-tier structure becomes explicit. High-earning H-1B holders at companies like NVIDIA — workers whose roles align with national interest language around AI and advanced computing — sit on firmer ground. Workers at mid-tier companies, particularly those in commoditised IT roles, face growing uncertainty about whether their green card journey can even proceed inside the country.

## The diaspora calculation

For the roughly 300,000 Indian nationals on H-1B visas, this reshuffling carries personal stakes. Those who landed at AI-heavy firms with generous compensation may find the current environment oddly favourable: the weighted lottery prefers them, the fee doesn't deter their employers, and the national interest carve-out in PM-602-0199 shields their adjustment applications.

But the majority of Indian H-1B workers do not earn $300,000. They work at consulting firms, mid-size IT shops, and healthcare companies where wage levels cluster at Level I and II. For them, the $100,000 fee makes new sponsorship harder to justify, the weighted lottery reduces their odds, and the AOS policy memo adds a layer of risk to green card applications already mired in decade-long backlogs.

Jensen Huang has said he "personally reviews everybody's compensation" and considers global talent vital to the "AI Agent Era." That philosophy happens to align perfectly with every policy lever Washington has pulled in the past year. The uncomfortable truth for Indian tech workers is that the immigration system is no longer neutral ground — it now actively favours the most expensive talent and the companies wealthy enough to sponsor them.

The rest are left to do the arithmetic on whether America still adds up."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA Is Hiring More H-1B Workers. Everyone Else Is Pulling Back.",
    "subheadline": "The $100,000 visa fee and wage-weighted lottery have split Silicon Valley into winners and losers — and the divide falls along salary lines that most Indian tech workers are on the wrong side of.",
    "slug": make_slug("nvidia-h1b-hiring-surge-100k-fee-silicon-valley-retreat"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Most Indian H-1B holders work at consulting firms and mid-tier IT companies at Wage Level I-II, where the $100K fee and weighted lottery create compounding disadvantages. The two-tier H-1B market now favours the highest earners — a minority of Indian workers — while the majority face worse odds, higher employer reluctance, and growing uncertainty about green card processing.",
    "tags": ["h1b", "nvidia", "100k-fee", "weighted-lottery", "silicon-valley", "indian-tech-workers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/nvidia-adds-h-1b-workers-despite-100000-visa-fee-as-silicon-valley-pulls-back/"},
        {"name": "USCIS H-1B Employer Data Hub", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"},
        {"name": "Federal Register — Weighted Lottery Rule", "url": "https://www.federalregister.gov/"},
        {"name": "USCIS Policy Memorandum PM-602-0199", "url": "https://www.uscis.gov/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "body": art1_body
}

# ============================================================
# ARTICLE 2: Day 1 CPT Crackdown
# ============================================================

art2_body = """On May 5, 2026, the Department of Homeland Security proposed a rule that would dismantle one of the last remaining safety nets for international graduates who lose the H-1B lottery: the Duration of Status framework that has governed F-1 student visas for decades.

Under the current system, F-1 students may remain in the United States as long as they maintain valid student status. That flexibility has allowed graduates who fail to secure an H-1B — a majority in any given year, given lottery odds — to enrol in a second master's programme, activate Curricular Practical Training on Day 1, and continue working legally while they wait for another shot at the lottery.

The proposed rule would replace Duration of Status with a fixed admission period of up to four years. Extensions beyond that would require formal USCIS approval, not just a university registrar's sign-off. A separate provision would cut the F-1 grace period after status ends from 60 days to 30 days.

## The Day 1 CPT lifeline

The phrase "Day 1 CPT" has become shorthand for a workaround that tens of thousands of Indian graduates rely on. The mechanics are straightforward: enrol in a new academic programme at a university that offers immediate CPT eligibility, and begin or continue working from the first day of classes. Critics call it a loophole. For the workers who use it, it is often the only legal pathway between an H-1B denial and deportation.

Danielle Goldman, co-founder and CEO of immigration consultancy Build, put it bluntly: "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working.'"

The proposed rule does not explicitly ban Day 1 CPT. But by imposing a four-year cap with USCIS-controlled extensions, it makes the strategy far harder to execute. A student who has already spent four years on an F-1 — completing a master's and a period of OPT — would need to petition USCIS rather than simply enrolling in a new programme. That petition is discretionary, and in the current enforcement climate, discretionary decisions have trended in one direction.

## Thirty days instead of sixty

The grace period reduction sounds technical until you consider what happens inside those 30 days. A student whose OPT ends or whose programme concludes has that window to find an employer willing to sponsor an H-1B, file a change of status, or pack up and leave. Under current rules, 60 days provides a narrow but workable timeline. At 30 days, the margin evaporates — particularly for workers in cities where immigration attorneys are booked weeks in advance and employer HR departments move at their own pace.

## The Indian student pipeline under pressure

Indians are the largest group of international students in the United States, with over 331,000 enrolled as of the 2023-24 academic year. They are also disproportionately concentrated in the fields most affected: computer science, data science, AI, and engineering. Many arrive expecting a clear pathway from F-1 to OPT to H-1B to green card. That pathway was always narrow, but it was at least navigable.

New enrolment data suggests the chill is already setting in. The Institute of International Education's Fall 2025 snapshot found a 17 per cent decline in new international student arrivals, with Indian students among the hardest-hit cohorts. A Hindu Business Line analysis of SEVIS data found a 28 per cent year-over-year drop in active Indian students by March 2025. Universities that rely on international tuition — sometimes amounting to $55 billion annually across the sector — are starting to feel the revenue impact.

## What it means for families back home

In Hyderabad, Pune, and Bangalore, the American master's degree has long been treated as a reliable investment. Parents take loans, sell property, and mortgage futures on the assumption that two years of study will lead to a job, then a visa, then eventually a green card. The proposed rule does not make that investment worthless, but it makes the return far less certain.

Goldman's advice to students was pragmatic: develop multiple backup plans rather than relying on H-1B lottery selection or Day 1 CPT alone. That is sensible counsel, but it also concedes the ground — the system that once rewarded persistence now punishes it.

The proposed rule is open for public comment. Whether it survives in its current form depends on the volume and quality of pushback from universities, employers, and the immigrant communities it would most directly affect. The comment period is the last point of leverage before the rule becomes final."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Day 1 CPT Escape Hatch Is Closing — and Indian Graduates Have the Most to Lose",
    "subheadline": "A proposed DHS rule would replace Duration of Status with a four-year cap, cut the F-1 grace period in half, and make the workaround that tens of thousands of Indian students rely on far harder to execute.",
    "slug": make_slug("day-1-cpt-crackdown-f1-duration-status-indian-graduates"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are the largest international student group in the US and disproportionately rely on Day 1 CPT as a bridge between H-1B lottery failures. The proposed rule directly threatens the study-to-work pipeline that families in India have treated as a reliable investment for decades. Enrollment is already dropping — 28% fewer active Indian students by March 2025.",
    "tags": ["f1-visa", "day-1-cpt", "duration-of-status", "indian-students", "h1b-lottery", "opt"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Institute of International Education", "url": "https://www.iie.org/"},
        {"name": "Hindu Business Line — SEVIS Data Analysis", "url": "https://www.thehindubusinessline.com/"},
        {"name": "GoElite — IIE Fall 2025 Snapshot", "url": "https://goelite.com/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body
}

# ============================================================
# ARTICLE 3: USCIS Site Visits Surge
# ============================================================

art3_body = """If you are on an H-1B visa and your employer has not yet briefed you on what happens when a USCIS officer shows up unannounced at your workplace, that conversation is overdue. The Fraud Detection and National Security directorate — the unit within USCIS responsible for site inspections — is conducting more targeted visits than at any point in the programme's history, and the consequences of a bad visit have never been steeper.

## The rule that changed everything

On January 17, 2025, the H-1B Modernization Rule took effect. Among its provisions was one that received far less attention than the wage-weighted lottery: the codification of employer cooperation with USCIS site visits as a legal obligation. Before the rule, refusal to cooperate with an FDNS inspection was frowned upon but carried ambiguous consequences. Now it is written into regulation. Failure or refusal to cooperate can result in denial or revocation of pending or approved H-1B petitions, and referral to ICE or the Bureau of Diplomatic Security for further investigation.

That is not a warning. It is a promise backed by regulatory text.

## What a targeted visit looks like

FDNS conducts two types of site visits. Administrative visits are random audits under the Administrative Site Visit and Verification Programme. Targeted visits are initiated through tips — from USCIS adjudicators who detect anomalies in petitions, from consular officers during visa interviews, or from the VIBE (Validation Instrument for Business Enterprises) system that cross-references employer data.

In practice, targeted visits have become the dominant mode. An FDNS officer typically arrives unannounced at the work location listed on the H-1B petition. They verify that the petitioning employer exists, that the H-1B worker is physically present at the stated worksite, that the duties match the petition, and that the salary matches the Labor Condition Application.

Officers may interview the H-1B worker directly. Questions cover job duties, hours, work location, and salary. In targeted visits, the questioning can go deeper — probing for inconsistencies between what was filed and what is actually happening on the ground.

## Why Indian H-1B workers should pay attention

Three features of the current environment make site visits particularly consequential for Indian nationals on H-1B visas.

First, the consulting and staffing model — in which an H-1B worker is placed at a client site rather than working at the petitioning employer's office — has long been an FDNS focus. Companies with a high ratio of H-1B workers to domestic employees, or those petitioning for workers who perform duties off-site, face elevated scrutiny. Indian IT staffing firms, which account for a significant share of H-1B petitions filed at lower wage levels, fall squarely into this category.

Second, the Department of Labor's Wage and Hour Division has parallel authority to audit H-1B employers for compliance with prevailing wage requirements. With the DOL having recently hiked prevailing wages across all four levels, the gap between what was filed on an LCA and what is actually being paid may have widened for some employers. A DOL audit that surfaces wage violations can trigger an FDNS referral, creating a two-front compliance problem.

Third, the H-1B Modernization Rule introduced new requirements around the specificity of job descriptions and worksite designations. Petitions filed under the old, looser standards may not withstand scrutiny under the new framework, particularly if the worker's actual role has evolved since the petition was approved.

## What you should do now

Immigration attorneys are advising both employers and workers to prepare as though a visit could happen tomorrow. The checklist is not complicated, but it requires attention.

Employers should designate a single point of contact responsible for liaising with FDNS officers, draft an internal protocol for site visits, and maintain readily accessible copies of every H-1B worker's petition, LCA, and payroll records. Workers should ensure they can articulate their job duties in terms that match the filed petition — not in the language of whatever project they happen to be working on this month.

If you receive notice of a visit, contact immigration counsel immediately. You have the right to have an attorney present, whether in person or by phone. Do not volunteer information beyond what is asked. Do not speculate about other workers' cases. Answer honestly, stay calm, and let the process run.

The FDNS site visit programme has existed since 2010. What has changed is not the existence of inspections but their intensity, their legal teeth, and the political will behind them. In the current climate, compliance is not optional — it is the difference between keeping your visa and losing it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "USCIS Officers Are Showing Up at Your Office — Here's What Every H-1B Worker Needs to Know",
    "subheadline": "The H-1B Modernization Rule made cooperation with site visits a legal obligation. FDNS targeted inspections are surging. For Indian workers at staffing firms and client sites, preparation is no longer optional.",
    "slug": make_slug("uscis-fdns-site-visits-h1b-compliance-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian IT consulting and staffing firms are a primary FDNS target due to high H-1B-to-domestic-worker ratios and off-site placements. Indian H-1B workers at client sites face the highest risk of a targeted visit — and under the new rule, a failed inspection can trigger petition revocation and ICE referral, putting entire families' immigration status in jeopardy.",
    "tags": ["h1b", "uscis", "fdns", "site-visits", "compliance", "indian-workers", "modernization-rule"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LinkedIn — H1B Employer Compliance Guide", "url": "https://www.linkedin.com/"},
        {"name": "USCIS H-1B Modernization Final Rule", "url": "https://www.federalregister.gov/"},
        {"name": "Fragomen — USCIS Employer Site Visits FAQ", "url": "https://www.fragomen.com/"},
        {"name": "Berry Appleman & Leiden — H-1B Compliance Reminder", "url": "https://www.bal.com/"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body
}

# ============================================================
# Verify images and publish
# ============================================================

articles = [art1, art2, art3]

for art in articles:
    print(f"\n📝 {art['headline']}")
    img_ok = verify_image(art["image_url"])
    if not img_ok:
        print(f"  ⚠️ Image verification failed, publishing anyway")
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ Published: {art['slug']}")
    except Exception as e:
        print(f"  ❌ Failed: {art['slug']}: {e}")
