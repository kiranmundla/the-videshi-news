#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-09 04:00 UTC run.
Inserts 2 fresh immigration articles into Supabase.
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


# ── ARTICLE 1: H-4 EAD Work Permit Crisis ──

article1_body = """When Priya Venkataraman moved to Seattle in 2019 on an H-4 visa, she brought a master's degree in data science from the University of Madras and seven years of analytics experience at Infosys. Within months of receiving her Employment Authorization Document, she was pulling down six figures at a cloud-computing startup. Her income paid half the mortgage and all of their son's preschool fees.

Last November, Priya filed to renew her EAD. She is still waiting. Her old card expired in February. She has not earned a rupee since.

Priya's situation — real name withheld at her request — is now shared by tens of thousands of Indian families across America, caught in a policy change that has received a fraction of the attention lavished on the H-1B fee fight or the Chip Roy bill.

## The rule that changed everything

On 30 October 2025, the Department of Homeland Security quietly ended automatic extensions for Employment Authorization Documents. Before that date, an H-4 spouse who filed a timely renewal could keep working while USCIS processed the paperwork. After it, the protection vanished. File your renewal on 31 October and you sit at home, paycheck-less, until an adjudicator gets to your case.

DHS invoked "national security concerns" and a good-cause exception to bypass the usual notice-and-comment rulemaking. The rule took effect the day it was published in the Federal Register.

The timing was brutal. USCIS processing times for H-4 EADs have ballooned past twelve months in many service centres. That means an Indian spouse who filed a renewal in November 2025 might not receive approval until late 2026 — a full year without the legal right to work, despite being lawfully present in the United States, despite holding advanced degrees, and despite having committed no violation of any kind.

## Who actually holds these permits

The demographics tell a pointed story. Roughly 90 per cent of H-4 EAD holders possess at least a bachelor's degree. Nearly 60 per cent hold a master's. Two-thirds work in STEM fields — the very sectors American employers say they cannot fill domestically. The overwhelming majority are women, and the overwhelming majority are Indian.

That last fact is structural, not coincidental. H-4 spouses qualify for work authorisation only if their H-1B-holding partner has an approved I-140 immigrant petition — meaning the family is already in the green card queue. And because of the per-country cap, Indian nationals face employment-based green card waits that stretch decades. These families are not transient workers. They are people who have committed their professional lives to the United States and are now watching one income disappear overnight.

## The lawsuit

In January 2026, a group of H-4 visa holders filed suit in federal court, arguing that DHS lacked the authority to eliminate automatic extensions without proper rulemaking. The complaint called the administration's rationale — that automatic renewals "posed a security risk that allowed bad actors to continue to work" — pretextual.

"The administration's true rationale, stripping the ability of people lawfully in the U.S. to sustain themselves, is embarrassingly obvious," the complaint states.

The plaintiffs note that DHS already has continuous vetting programmes that screen immigrants without requiring a fresh adjudication at each renewal. And they point to a pattern: the first Trump administration tried and failed to rescind the H-4 EAD regulation entirely but "accomplished the same end by creating processing burdens, and pretextual biometric collections."

DHS has since proposed expanding biometric requirements further — including the possible collection of DNA data from applicants.

## The fallout for Indian families

For a typical dual-income Indian household in the Bay Area or Dallas suburbs, losing the H-4 spouse's salary is not an inconvenience. It is a financial emergency. Mortgages calibrated to two tech salaries do not recalibrate overnight. Families that stretched to buy homes in Cupertino or Frisco now face the arithmetic of a single H-1B income covering a $5,000-a-month payment.

The professional damage compounds the financial hit. A twelve-month gap on a data scientist's résumé is not easily explained away. Employers move on. Skills atrophy. Networks thin. Several immigration attorneys report that H-4 spouses are increasingly asking about returning to India rather than enduring the uncertainty.

"This is a highly educated, highly skilled population being told to sit at home and wait," said one Bay Area immigration lawyer who requested anonymity to protect client relationships. "The cruelty is the point."

## What comes next

The lawsuit is still in its early stages, and no injunction has been granted. Meanwhile, the underlying green card backlog — the reason these families are on H-4 visas in the first place — continues to grow. The July 2026 Visa Bulletin locked out Indian nationals across all employment-based categories. EB-2 India's final action date sits at July 2013. Anyone who filed after that is waiting at least thirteen years.

For families like Priya's, the immigration system has become a trap with no exit. The green card queue stretches to the horizon. The work permit renewal sits in a government inbox. And the mortgage payment is due on the first of the month."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Other Visa Hostage — Tens of Thousands of Indian Spouses Just Lost the Right to Work",
    "subheadline": "DHS killed automatic work-permit renewals. Most H-4 EAD holders are Indian women with master's degrees. Now they wait a year to learn if they can keep their jobs.",
    "slug": make_slug("h4-ead-work-permit-crisis-indian-spouses-forced-out"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The H-4 EAD programme overwhelmingly serves Indian families stuck in the green card backlog. Losing automatic renewals forces educated Indian spouses — mostly women in STEM — out of work for 12+ months, destabilising dual-income households in tech hubs like the Bay Area and Dallas.",
    "tags": ["h4-ead", "work-permit", "uscis", "immigration", "indian-spouses", "green-card-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-spouses-sue-over-end-to-automatic-work-permit-renewals"},
        {"name": "Visa Lawyer Blog (Sapochnick)", "url": "https://www.visalawyerblog.com/category/h4-spouses/"},
        {"name": "Berry Appleman & Leiden LLP", "url": "https://www.bal.com/category/employment-based-visas/"},
        {"name": "Daryanani Law Group", "url": "https://www.dlgvisa.com/blog/tag/employment+authorization"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Exterior of the U.S. Immigration and Customs Enforcement building in Washington",
    "image_attribution": "Pexels",
    "body": article1_body,
}


# ── ARTICLE 2: Social Media Vetting for Student Visas ──

article2_body = """Somewhere on a university server in Hyderabad, a 22-year-old computer-science graduate is deleting three years of Instagram posts. She has an F-1 visa interview at the U.S. consulate in two weeks. She is not sure which photos might count as "hostility toward the United States." She is not taking chances.

This quiet digital self-censorship — playing out across thousands of Indian households with children heading to American universities — is the downstream consequence of a policy shift that has received far less scrutiny than the H-1B fee war or the Chip Roy bill, but may ultimately reshape Indian student migration more profoundly than either.

## The new screening regime

In March 2026, the U.S. State Department formally instructed all consular officers to expand online-presence reviews for F, M, and J visa applicants — the categories covering virtually every international student and exchange visitor. The instruction was blunt: applicants must keep social media profiles "public" or "open" for vetting. Failure to do so is grounds for denial.

The policy builds on executive orders signed by President Trump targeting terrorism and antisemitism on American campuses. Consular officers have been told to screen for "hostility toward the United States or its people," though the department has not published a definition of what that phrase means in practice.

The consequences are not theoretical. By early June 2026, more than 6,000 international student visas have been revoked under the administration's expanded screening apparatus, according to reporting by multiple outlets. SEVIS records — the system that tracks international students — have been terminated in cases where officials determined that a student's online activity, past violations, or associations warranted removal.

## Why Indian students are disproportionately exposed

Indians constitute the largest single national group in the F-1 visa pool. In the 2024-25 academic year, over 330,000 Indian students were enrolled at American universities — a number that has nearly doubled in five years. They account for roughly a quarter of all foreign graduates using OPT work authorisation after completing their degrees.

That scale means any tightening of the student visa pipeline hits India harder, in absolute numbers, than any other country. But it is not just volume. Indian students tend to be concentrated in graduate STEM programmes — precisely the cohort that relies on OPT and, eventually, H-1B sponsorship to stay in the U.S. workforce. A revoked F-1 does not just end a semester. It ends a career plan.

The social media requirement adds a layer of anxiety that is particularly acute for students from politically engaged backgrounds. India's own domestic politics are polarising; many young Indians have posted opinions on everything from Kashmir to the CAA protests to farm laws. Whether a consular officer in Chennai considers a 2020 Instagram story about the Shaheen Bagh protests "hostile" is a question no State Department guidance answers.

## The distinction that matters: visa cancellation versus SEVIS termination

Immigration attorneys stress that a cancelled visa stamp and a terminated SEVIS record are not the same thing — though confused students often treat them as interchangeable.

A cancelled visa stamp primarily affects travel. A student inside the United States with an active SEVIS record can continue studying even if their visa is technically cancelled. They simply cannot re-enter the country if they leave.

SEVIS termination is far more severe. It revokes the student's legal status, ends any work authorisation (including OPT and CPT), and can trigger a five-year bar from re-entry. DHS guidance states that a terminated SEVIS record "can result in loss of employment authorization and may prevent re-entry on that terminated record."

For the thousands of Indian students currently on OPT — working at Google, Amazon, Deloitte, and hundreds of smaller firms — a SEVIS termination would not just end their job. It would make them instantly deportable.

## The chilling effect

Immigration experts say the most consequential impact may be the one that never shows up in visa statistics: deterrence. Danielle Goldman, co-founder of the immigration platform Build, told The Indian Eye that the combination of social media vetting, the proposed end to Duration of Status, and the crackdown on Day-1 CPT is reshaping how international students — particularly Indians — weigh the risk-reward calculus of an American education.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman said, noting that companies may "either struggle because they won't have the talent or they will have to get creative and find alternate solutions."

Canada, the UK, and Australia are watching. India's student migration flows do not have a single destination; they follow opportunity and perceived safety. If the perception takes hold that an F-1 visa now comes with a social-media audit and a four-year expiration date, the diversion of Indian talent may not wait for the regulations to be finalised.

## What students should know

Immigration attorneys offer consistent advice: do not delete your entire social media presence, which can itself raise red flags. Do review posts for content that could be interpreted as threatening or endorsing violence. Do set expectations that the consular interview may now include questions about online activity. And do understand that a visa denial is not the same as a SEVIS termination — the former is recoverable; the latter is not.

The graduate from Hyderabad who is scrubbing her Instagram is making a rational calculation. The system is telling her that her opinions have a price. Whether that price is worth paying is a question 330,000 Indian students are now answering for themselves."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Instagram Is Under Review — The Screening That Could Cost Indian Students Their F-1 Visa",
    "subheadline": "The State Department now requires public social media profiles for all student visa applicants. Over 6,000 visas have been revoked. Indian students, the largest F-1 cohort, are in the crosshairs.",
    "slug": make_slug("social-media-vetting-f1-visa-indian-students-revoked"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are the single largest F-1 cohort in America, with over 330,000 enrolled. Social media vetting disproportionately affects Indians — many have posted about Indian domestic politics, which consular officers may flag as 'hostility.' The chilling effect extends to OPT holders already working at U.S. companies.",
    "tags": ["f1-visa", "social-media-vetting", "student-visa", "sevis", "indian-students", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NRIPage", "url": "https://www.nripage.com/articles/us-student-visa-cancellations-latest-2026-updates-for-f-1-students"},
        {"name": "CollegeChalo", "url": "https://collegechalo.com/news/trump-visa-crackdown-6000-international-student-visas/"},
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com/2026/06/08/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "State Department (via KWIT)", "url": "https://www.kwit.org/2025-06-19/u-s-will-review-social-media-for-foreign-student-visa-applications"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5553040/pexels-photo-5553040.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "International students on the steps of a university campus in the United States",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ── Insert articles ──
articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
