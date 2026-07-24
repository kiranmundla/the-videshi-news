#!/usr/bin/env python3
"""Immigration writer — July 4, 2026 morning run."""

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


# ── ARTICLE 1: OPT under coordinated attack ───────────────────────────

art1_body = """The Optional Practical Training programme was designed as a modest concession — a year of supervised work experience for international graduates before they returned home. Over two decades it swelled into something far larger: a bridge between American classrooms and American cubicles, used by close to 300,000 foreign graduates in the 2024-25 cycle alone. Now the federal government is pulling that bridge apart, plank by plank.

In May, acting ICE Director Todd Lyons called a press conference to announce what he described as rampant fraud inside OPT. His investigators had flagged nearly 10,000 students and linked employers. They found locked buildings listed as work sites for hundreds of supposed trainees. One company claimed three OPT workers on paper; records showed nearly 500 students connected to it. When agents asked basic questions, responses were redirected to contacts in India.

"This is not accidental," Lyons said. "It is deliberate, coordinated, and criminal." He called OPT a "magnet for fraud" and promised "more actions are forthcoming."

The language matters. Washington does not typically hold press conferences about administrative fraud in student work programmes. The spectacle was, in the view of many immigration analysts, a deliberate exercise in narrative construction — laying the groundwork for restricting or dismantling OPT altogether.

## The four-front squeeze

The fraud crackdown is only one piece of what amounts to a coordinated assault on the student-to-worker pipeline. Consider the other three fronts closing in simultaneously.

First, the Duration of Status overhaul. DHS proposed in May replacing the existing system — which lets students remain as long as they maintain their status — with a hard four-year cap. Extensions would require USCIS approval, not a university official's sign-off. Since most degree programmes plus OPT exceed four years, nearly every Indian graduate seeking post-study work would need to petition the government for permission to stay. That rule is expected to take effect in September.

Second, the weighted H-1B lottery. The December 2025 final rule, applied for the first time in the March 2026 registration cycle, gives four chances to the highest-paid applicants and just one chance to entry-level workers. International graduates fresh out of OPT — who are almost by definition at the bottom of the salary ladder — now face sharply worse odds. The pathway from classroom to OPT to H-1B to green card, already narrow, has become a bottleneck.

Third, the travel ban processing pause. Since January, OPT applications from students originating in 39 countries subject to the expanded travel ban have been frozen. They cannot work until processing resumes. No timeline has been given.

## Why Indians are disproportionately exposed

Indians account for roughly half of all OPT and STEM OPT participants in the United States at any given time — an estimated 150,000 people. They are concentrated in precisely the STEM fields (computer science, data science, AI, engineering) that the programme was expanded to serve. A 2025 NAFSA survey found that 54 per cent of current international students would not have chosen America without OPT.

The USCIS director, Joseph Edlow, has not been subtle about his intentions. At his confirmation hearing last year he said he wanted a regulatory framework that would "remove the ability for employment authorisations for F-1 students beyond the time that they are in school." The Center for Immigration Studies, a think tank influential in the current administration, published a piece in National Review in May titled "End It, Don't Mend It."

For Indian students who took out loans, moved across an ocean, and planned their careers around the degree-to-OPT-to-H-1B pipeline, the message is unmistakable. The pipeline that built Silicon Valley's Indian workforce — from Sundar Pichai's generation to the present — is being disassembled not by accident, but by design. Whether the intent is reform or elimination, the effect for the next generation of Indian graduates is the same: the American bridge is closing, and there is no obvious replacement on the other side."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ten Thousand Students Flagged. The OPT Pipeline That Built Silicon Valley Is Under Siege",
    "subheadline": "ICE calls the post-graduation work programme a 'magnet for fraud.' The crackdown is one front in a coordinated four-pronged attack that could dismantle the pathway 150,000 Indians depend on.",
    "slug": make_slug("opt-fraud-crackdown-four-front-attack-indian-students"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are roughly half of all OPT and STEM OPT participants in the US — an estimated 150,000 people. The coordinated dismantling of the student-to-worker pipeline threatens the career pathway that an entire generation of Indian tech workers was built on.",
    "tags": ["opt", "stem-opt", "f1-visa", "uscis", "ice", "immigration", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/05/us-immigration-officials-allege-opt-is-being-widely-abused-and-say-more-actions-are-forthcoming/"},
        {"name": "India Today", "url": "https://www.indiatoday.in/education-today/news/story/us-opt-crackdown-2026-ice-probes-10000-foreign-students-for-fraud-links-2911648-2026-05-14"},
        {"name": "ICEF Monitor — Duration of Status", "url": "https://monitor.icef.com/2026/05/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
        {"name": "Center for Immigration Studies / National Review", "url": "https://cis.org/Krikorian/OPT-Foreign-Student-Work-Program-End-It-Dont-Mend-It"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ── ARTICLE 2: Canada closing doors to Indian students ────────────────

art2_body = """For a generation of Indian students, Canada was the safety valve. When H-1B lottery odds cratered and American consulates turned hostile, the pitch from Ottawa was seductive: study here, work here, stay here. Between 2015 and 2023, Indians became Canada's largest source of international students by a wide margin. Entire neighbourhoods in Brampton and Surrey were reshaped by the influx. Recruitment agents in Punjab operated like travel agencies, moving thousands of young Indians north each semester.

That door is now slamming shut.

Government data reported by Reuters shows that 74 per cent of Indian study permit applications were rejected in August 2025 — more than double the 32 per cent rejection rate in August 2023. The overall global refusal rate was 40 per cent. For Chinese applicants it was 24 per cent. India, once Canada's favourite source market, now has the highest study permit refusal rate of any country with more than 1,000 approved applicants.

The raw numbers are even more striking. Indian applicants fell from 19,175 in August 2023 to just 3,920 in August 2025 — an 80 per cent collapse. The University of Waterloo, home to Canada's largest engineering school, has seen a two-thirds decline in Indian enrolments over three to four years.

## Bill C-12 and the power to cancel en masse

Ottawa is not merely raising the bar for new applicants. It is seeking the legal authority to cancel existing visas in bulk.

Internal documents obtained by CBC News reveal that Immigration, Refugees and Citizenship Canada (IRCC), the Canada Border Services Agency (CBSA), and unnamed American partners have formed a working group to detect and cancel fraudulent visa applications. A presentation prepared for the Immigration Minister's office described India and Bangladesh as "country-specific challenges."

The proposed authority sits inside Bill C-12, drawn from the broader border legislation package Bill C-2. If passed, it would allow the government to revoke groups of temporary visas by executive order — a power that has alarmed more than 300 civil society groups, including the Migrant Rights Network, which warned it could enable a "mass deportation machine."

IRCC insists the proposed powers are "not aimed at any specific group of people or situation." The internal briefings that name India tell a different story.

## The fraud that triggered the crackdown

The crackdown did not materialise from thin air. In 2023, Canadian authorities uncovered nearly 1,550 study permit applications linked to fraudulent letters of acceptance, most originating from India. By 2024, an enhanced verification system had flagged more than 14,000 potentially fraudulent documents across all applicants. Processing times for Indian applications doubled from 30 days to 54 as resources were diverted to fraud checks.

The fraud was real, and it was concentrated in a specific corridor: Indian recruitment agents funnelling students to smaller Canadian colleges through fabricated acceptance letters. The result was a system in which legitimate applicants from top Indian universities were punished alongside fraudsters from diploma mills.

## Why this matters to the diaspora

For the roughly 700,000 Indians who hold some form of temporary status in Canada — students, workers, and permanent residency applicants — the mood has shifted from optimism to anxiety. The "study, work, stay" promise that drew them north has been quietly retired.

For Indians in America, the implications are equally pointed. Canada has long served as the Plan B: the country you pivot to when the H-1B lottery fails for the third time, when the green card backlog stretches past your children's college graduation, when the consulate cancels your stamping appointment and you cannot re-enter the country where your furniture sits. Entire immigration strategies were built on the assumption that if America did not work out, Canada would.

That assumption no longer holds. The simultaneous tightening of both the American and Canadian immigration systems means the two largest destinations for skilled Indian migrants are closing their doors at the same time. Australia has raised salary thresholds and ended visa hopping as of July 1. The United Kingdom has increased its skilled worker salary bar and tightened settlement rules.

The exits are closing, one by one. For Indian families weighing the move abroad — or already abroad and weighing whether to stay — the calculus has changed faster than anyone expected."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Canada Rejected Three in Four Indian Student Visas. Now It Wants the Power to Cancel the Rest",
    "subheadline": "A 74 per cent rejection rate, an 80 per cent collapse in applicants, and a new bill that would let Ottawa revoke visas in bulk. The Indian diaspora's Plan B is shutting down.",
    "slug": make_slug("canada-74-percent-rejection-indian-students-bill-c12"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Canada has long been the fallback for Indians when the US path fails — the country you pivot to after the H-1B lottery, the green card backlog, the consulate cancellation. With Ottawa now rejecting 74% of Indian student visas and seeking mass cancellation powers, that escape route is closing at the same time as America's.",
    "tags": ["canada", "student-visa", "immigration", "indian-students", "bill-c12", "study-permit"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/americas/fearing-fraud-canada-rejects-most-indian-study-permit-applicants-2025-11-03/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/11/04/indian-applicants-hit-hard-by-canadas-crackdown-on-student-visas/"},
        {"name": "CBC News (via Hindu Business Line)", "url": "https://www.thehindubusinessline.com/news/world/canadas-crackdown-on-student-visas-hits-indian-applicants-hard/article68838395.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/why-are-indian-student-visas-facing-record-74-rejection-in-canada-this-year-11730729987428.html"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/22039132/pexels-photo-22039132.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Simon Fraser University campus in Burnaby, British Columbia",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}


# ── Insert ─────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
