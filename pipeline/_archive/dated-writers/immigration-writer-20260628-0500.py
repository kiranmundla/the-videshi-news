#!/usr/bin/env python3
"""Immigration writer — 2026-06-28 0500 PT batch."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
# ARTICLE 1: Indian Student Exodus to Europe
# ──────────────────────────────────────────────────────────────────────

article1_body = """India sent 382,000 students to American universities last year. This year, the number is 352,000. The difference — roughly 30,000 young Indians who packed up, dropped out, or simply never enrolled — represents the sharpest single-year decline in Indian student presence in the United States in at least a decade.

And the exodus may only be warming up. Education consultants in India now warn that as many as 70,000 more students could leave in the coming academic year, citing a toxic cocktail of 10-to-11-month visa interview delays, hostile policy signals from Washington, and a growing sense that America no longer wants them.

## Where They're Going

The surprise winner is not Canada, not the United Kingdom, and not Australia — it is Germany.

Indian student enrollment at German universities has doubled in three years, rising from 28,905 in 2023 to 59,400 in the 2024–25 academic year, according to data from the German Academic Exchange Service (DAAD). Indians are now the single largest international student population in Germany, surpassing Chinese students for the first time. Overall, Germany now hosts more than 400,000 international students, making it the world's top non-English-speaking study destination.

The appeal is not hard to decode. Public universities in Germany charge little to no tuition. Post-graduation, students can stay for up to 18 months to find work. And there are now 2,400 English-taught degree programmes — roughly 1,930 at the master's level alone — eliminating the language barrier that once kept Indian applicants away.

"We are a very reliable partner," German Ambassador Dr. Philipp Ackermann told reporters earlier this year, in what felt like a pointed contrast to American immigration rhetoric. "When it comes to studying or researching in Germany, we don't check your social media before you arrive."

The comment was not subtle. The United States now requires social media screening for visa applicants, a policy that has added weeks to processing times and drawn sharp criticism from Indian consulate officials struggling with ballooning backlogs.

## The American Chill

The numbers tell a story that policy bulletins do not.

Under the current US administration, Indian students face visa interview waits of 10 to 11 months at embassies in India. The Mumbai and Hyderabad consulates — the two busiest for student visa applicants — reported wait times of 2.5 months just for an appointment slot earlier this year, with STEM applicants then facing additional administrative processing of four to six months. A student who applied in March might not receive a decision until November — well past the fall semester start date.

Then there are the policy headwinds. A proposed DHS rule would cap F-1 student visa duration at four years, eliminating the open-ended "duration of status" framework that allowed students to stay as long as they maintained enrollment. Another proposal would cut the post-program grace period from 60 days to 30. A separate bill, H.R. 9157, would abolish the Optional Practical Training programme entirely — the very bridge that allows Indian STEM graduates to work in the US for up to 36 months while seeking H-1B sponsorship.

For students already enrolled, the Day-1 CPT route — enrolling in a second master's programme to maintain work authorisation after failing the H-1B lottery — is also under threat, with DHS proposing rules that would narrow eligibility for repeated program enrollment.

## Canada Is No Refuge

India's other traditional destination, Canada, has cratered even more dramatically. Indian students now account for just 8 per cent of Canada's total international student population, down from 52 per cent in 2023, according to Prime Minister Mark Carney. The country's international student intake has fallen 60 per cent this year alone, the result of aggressive caps on study permits and tighter restrictions on post-graduation work visas.

The simultaneous closure of the American and Canadian doors is reshaping global student mobility in ways that would have been unimaginable five years ago.

## What This Means for Indian Families

For the Indian middle-class family saving for a child's American education, the calculus has changed. A US master's degree that once cost $60,000 to $80,000 in tuition alone now comes with an additional invisible tax: months of uncertainty, the risk of visa rejection, and no clear pathway to post-graduation employment.

Germany, by contrast, offers public university tuition of roughly €300 per semester in administrative fees, a structured 18-month job-search visa, and a government that is actively courting Indian talent rather than screening it. The blocked-account requirement of €11,904 per year — effectively a proof-of-funds deposit — is a fraction of what American universities charge in tuition alone.

The shift is not yet a stampede. The United States still hosts the largest absolute number of Indian students worldwide, and American degrees still carry weight in the global job market. But the direction is unmistakable. When 30,000 students leave in a single year and 70,000 more are projected to follow, the question is no longer whether India's best and brightest are diversifying — it is whether America will notice before the pipeline dries up entirely."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "30,000 Indian Students Left America in One Year. Germany Doubled Its Intake.",
    "subheadline": "Indian enrollment in US universities fell from 382,000 to 352,000 as visa delays, hostile policy signals, and rising costs push students toward Europe — where Germany now hosts more Indian students than any other non-English-speaking country.",
    "slug": make_slug("indian-students-exodus-us-germany-europe-enrollment"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families saving for a child's American education now face 10-month visa delays, proposed OPT abolition, and a Day-1 CPT crackdown — while Germany offers free tuition, an 18-month post-graduation work visa, and no social media vetting.",
    "tags": ["f1-visa", "indian-students", "germany", "study-abroad", "opt", "student-visa", "europe"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national/news/indian-students-leave-us-visa-delays-job-hurdles-europe-138300311.html"},
        {"name": "ICEF Monitor / DAAD", "url": "https://monitor.icef.com/2025/12/there-are-now-more-than-400000-international-students-in-germany/"},
        {"name": "Collegedunia", "url": "https://www.collegedunia.com/news/germany-to-host-4-2-lakh-foreign-students-india-leads-articleid-80236"},
        {"name": "Y-Axis (German Ambassador quote)", "url": "https://www.y-axis.com/news/germany-emerges-as-top-stable-choice-for-indian-students-amid-visa-challenges/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6146995/pexels-photo-6146995.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "International students studying together on a university campus",
    "image_attribution": "Pexels",
    "body": article1_body
}


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: TPS Ruling + Healthcare Workforce + Indian Doctors
# ──────────────────────────────────────────────────────────────────────

article2_body = """The Supreme Court's ruling last week in *Mullin v. Doe* gave the Trump administration the green light to strip Temporary Protected Status from more than 350,000 Haitians and Syrians living in the United States. Within hours, nursing home operators, hospital administrators, and hospice directors began calculating how many days they had left.

The answer, for many, was not enough.

Roughly one-third of Haitian TPS holders — an estimated 115,000 people — work in the American healthcare system, concentrated in the elder-care facilities, long-term nursing homes, and home-health agencies that keep the country's ageing population alive. "There is no workforce waiting in the wings," said Katie Smith Sloan, president of LeadingAge, the association representing non-profit ageing services providers. "Staff and caregivers who support older adults every day — legal employees who in some of our communities represent 8 per cent or more of the entire workforce — can now lose their jobs overnight."

Republican Representative Mike Lawler of New York was blunter: the ruling, he said, "will create a crisis in our hospitals, nursing homes, and in the I/DD community."

## The Pressure on Indian Physicians

For Indian-origin physicians in the United States, the TPS healthcare exodus lands on an already-cracking foundation.

International Medical Graduates — physicians trained outside the US and Canada — make up approximately 25 per cent of the American physician workforce, according to the American Association of Physicians of Indian Origin (AAPI). In rural and underserved areas, that figure rises to 40 per cent. More than half of internal medicine trainees are IMGs. Indian-origin doctors are disproportionately represented in the specialties facing the most acute shortages: geriatrics, nephrology, endocrinology, and infectious disease — precisely the fields that serve the elderly populations now at risk of losing their TPS-protected caregivers.

The compounding problem is that Indian physicians themselves face mounting barriers. The $100,000 H-1B filing fee — struck down by a federal judge earlier this month but kept alive by a court stay pending appeal — threatened to make it financially impossible for rural hospitals and safety-net institutions to sponsor foreign-trained doctors. AAPI President Dr. Amit Chakrabarty called the court ruling blocking the fee "a healthcare victory, not a political victory," warning that "many hospitals would have struggled to absorb such a financial burden."

Even with the fee in legal limbo, the broader immigration environment has turned hostile. The EB-2 India green card category is now marked "unavailable" in the July 2026 Visa Bulletin — meaning no new employment-based green cards can be issued to Indian nationals in that category for the remainder of the fiscal year. The median wait time for an Indian-born physician in the EB-2 queue stretches past 13 years, with priority dates frozen at September 2013.

## A Bill That Could Help — If Anyone Cared

Sitting in the House Judiciary Committee, largely unnoticed, is H.R. 5283 — the Healthcare Workforce Resilience Act. Introduced in September 2025 by Representatives Brad Schneider (D-IL) and Don Bacon (R-NE), the bill would recapture up to 40,000 unused employment-based immigrant visas and reserve them exclusively for healthcare professionals: 25,000 for nurses and 15,000 for physicians.

The provision that matters most for Indian doctors is buried in Section 2(C): these recaptured visas would be **exempt from per-country caps**.

Under current law, no more than 7 per cent of employment-based green cards can go to nationals of any single country — a rule that treats India's billion-plus population identically to Liechtenstein's 39,000. The HWRA would bypass this bottleneck entirely for healthcare workers, allowing qualified Indian physicians to receive green cards based on their place in the queue rather than their place of birth.

The bill has attracted bipartisan support. In the previous Congress, its predecessor (H.R. 6205) gathered more than 28 co-sponsors. Medical associations, hospital groups, and immigration advocates have endorsed it. Yet it has not received a committee hearing, and no Senate companion bill has been introduced in the current session.

## The Math Does Not Work

America faces a projected shortage of between 37,800 and 124,000 physicians by 2034, according to the Association of American Medical Colleges. The nursing shortage is worse: the Bureau of Labor Statistics projects 193,100 annual openings for registered nurses through 2032, with supply consistently failing to meet demand.

Into this deficit, the SCOTUS TPS ruling injects an immediate loss of tens of thousands of healthcare workers — not in some future scenario, but within weeks of the court's decision taking practical effect. At the same time, the immigration system that is supposed to replenish the pipeline is actively making it harder for qualified foreign physicians to stay.

The Healthcare Workforce Resilience Act is not a comprehensive fix. Forty thousand visas will not close a six-figure workforce gap. But it would signal that Congress understands the connection between immigration policy and patient care — a connection that, at the moment, appears to be lost entirely.

For the Indian physician waiting 13 years for a green card while staffing an understaffed rural emergency department, the question is no longer academic. It is whether anyone in Washington is paying attention before the next shift goes unfilled."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "America's Nursing Homes Are About to Lose 115,000 Workers. A Bill to Help Indian Doctors Gathers Dust.",
    "subheadline": "The Supreme Court's TPS ruling will strip healthcare jobs from tens of thousands of workers. A bipartisan bill to recapture 40,000 green cards for physicians and nurses — exempt from country caps — sits untouched in committee.",
    "slug": make_slug("tps-ruling-healthcare-crisis-indian-doctors-hwra-bill"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian-origin physicians make up 25% of the US physician workforce and 40% in rural areas. The Healthcare Workforce Resilience Act would exempt 15,000 physician green cards from per-country caps — directly benefiting the 700,000 Indians stuck in the employment-based backlog.",
    "tags": ["tps", "scotus", "healthcare", "indian-doctors", "green-card", "nursing-shortage", "hwra"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "KFF Health News", "url": "https://kffhealthnews.org/morning-breakout/hospitals-hospices-nursing-homes-brace-for-loss-of-thousands-of-immigrant-workers-after-supreme-court-ruling/"},
        {"name": "AAPI (The Indian Eye)", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
        {"name": "Congress.gov — H.R. 5283", "url": "https://www.congress.gov/bill/119th-congress/house-bill/5283/text"},
        {"name": "Fox News (Rep. Lawler)", "url": "https://www.foxnews.com/politics/blue-state-leaders-erupt-supreme-courts-decision-ending-tps-protections-haitians-syrians"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6129676/pexels-photo-6129676.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A nurse providing care to a patient in a hospital room",
    "image_attribution": "Pexels",
    "body": article2_body
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
