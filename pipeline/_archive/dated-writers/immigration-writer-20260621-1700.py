#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

article1_body = """The H-1B lottery has always been a gamble. For the Indian graduate who loses it, the consolation prize has long been the same: re-enroll somewhere, keep working, and roll the dice again next March. A proposed Department of Homeland Security rule, now sitting with the White House for review, would quietly remove that escape hatch — and the students most exposed are Indian.

The mechanism at the center of this is **Day 1 CPT**, a workaround that lets an F-1 student begin Curricular Practical Training employment from the first day of a new academic program rather than after a year of study. In practice, a graduate who strikes out in the H-1B lottery enrolls in a second master's program — often at a school built around exactly this market — and keeps drawing a paycheck while waiting for another shot at the cap. It is legally aggressive, frequently litigated, and, for tens of thousands of Indians in software, AI, machine learning, and data science, the difference between staying in the country and going home.

## What the rule would change

The DHS proposal, published in the Federal Register on August 28, 2025, would scrap the decades-old "duration of status" framework that lets F-1 students remain as long as they are pursuing a valid course of study. In its place comes a fixed admission ceiling — most students admitted for no more than four years, with formal extension requests adjudicated by USCIS officers who will never meet the applicant.

Two features of the draft bite hardest. First, it shortens the post-completion grace period from 60 days to 30 — halving the window a graduate has to find a sponsor, transfer, or change status before falling out of legal status. Second, it explicitly restricts the academic maneuvers that make Day 1 CPT work: the rule would bar students from starting a new program at the same or a lower degree level, and limit graduate students from switching programs mid-stream.

Immigration attorney Danielle Goldman put the consequence bluntly. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorization to continue working,'" she said. That sentence describes the entire Day 1 CPT industry.

## Why Indians are the most exposed

Indians make up the single largest bloc of international students in the United States and a disproportionate share of H-1B lottery entrants. With the FY2027 selection rate hovering around 35 percent, roughly two of every three registrants are turned away each year. Day 1 CPT has functioned as the pressure valve for that losing majority — a way to remain employed and try again.

Close that valve and shorten the grace period, and the math turns brutal. A graduate who loses the lottery in March and whose OPT expires in the summer would have 30 days to leave. The "study your way to another lottery" strategy, never officially blessed, would become far harder to attempt. Goldman warned the fallout reaches employers too: foreign nationals make up a substantial slice of the US AI talent pool, and companies "will either struggle because they won't have the talent or they will have to get creative and find alternate solutions" — cap-exempt H-1Bs at universities and nonprofits, or O-1 visas for the genuinely exceptional.

## What is — and isn't — settled

The crucial caveat: this is still a proposed rule. It has cleared White House review in draft form but the final rule has not been published, and it is not in effect. Lawyers are urging students not to act on social-media panic. A 2020 version of the same idea was withdrawn after litigation, and any final rule restricting practical training is near-certain to draw lawsuits of its own, possibly an injunction.

But the direction of travel is unmistakable. Between the wage-weighted lottery that now favors senior, higher-paid roles, the shrinking grace period, and the assault on Day 1 CPT, the improvised pathways an entire generation of Indian graduates relied on are narrowing at once. For a 23-year-old finishing a US master's this year, the advice from counsel is uncomfortable but consistent: secure a real sponsor early, document everything, and stop treating a second enrollment as a safety net. The net is being pulled away.
"""

article2_body = """For two decades, the H-1B lottery was a coin flip dressed up as a process: enter the pool, pray to the random-number generator, and hope. The data from the latest cycle confirms what immigration lawyers have been telling clients for a year — the coin flip is over, and the new game has a clear profile of who wins. Increasingly, the winner holds a US master's degree and commands a senior salary. For Indian graduates, that is both an opening and a warning.

## The numbers

Registrations for the FY2027 H-1B cap fell **38.5 percent** from the prior year, according to figures parsed from USCIS data — an extension of a multi-year collapse from the 2024 peak of nearly 781,000 entries. The drop is not a sign that demand for foreign talent has evaporated. It reflects the death of speculative, duplicate, and low-quality filings under two compounding reforms.

The first is the beneficiary-centric system, now in its third cycle, which limits each individual to one registration regardless of how many employers enter them. That alone strangled the multiple-entry gaming that once inflated the pool. The second, and more consequential, is the **wage-weighted selection** rule that DHS finalized for cap-subject filings. Under it, a Level IV (highest-paid) position earns **four** entries in the lottery, Level III gets three, Level II two, and Level I — entry-level — just one.

The effect on outcomes is stark. USCIS reported that **71.5 percent** of selected applicants held a US master's degree or higher, up from 57 percent the previous year. The advanced-degree exemption and credentials earned on American soil are no longer a marginal advantage. They are close to decisive.

## Why this reshapes the Indian calculus

Indians win the overwhelming majority of H-1B visas — by most counts close to three-quarters of approvals — so any structural change to selection lands on the diaspora first. The wage-weighted system rewards exactly the profile many established Indian professionals have built: years of experience, senior titles, Level III and IV salaries. For a mid-career engineer at a large tech firm, the new odds are markedly better than the old random draw.

For the fresh graduate, the signal is harsher. A new master's-holder applying for an entry-level role at a Level I wage now sits at the bottom of the weighting — one entry against a competitor's four. The "get any job, win the lottery, sort it out later" path that powered a generation of Indian students through the system is being squeezed from both ends: fewer entries for low wages, and, separately, a proposed crackdown on the Day 1 CPT re-enrollment trick that losers used to stay in the game.

## The compliance edge

There is a second message buried in the data. USCIS is openly mining FY2025 and FY2026 registrations for fraud and has promised to deny or revoke petitions — and refer cases for criminal prosecution — where it finds attempts to game the system. The registration fee jumped from $10 to $215, each entry now requires a valid, unique passport number, and petitions must survive a documentation standard that treats vague job descriptions like "software development" or "data analysis" as red flags for a Request for Evidence.

For Indian applicants and the employers sponsoring them, the practical takeaways are concrete. Wage level is now strategy, not paperwork: a role credibly classified at Level III or IV multiplies the chance of selection. Specialty-occupation documentation must draw a direct, defensible line between the degree and the daily duties. And the days of casting a wide, cheap net of registrations are gone — each entry must be one the employer is genuinely prepared to fund and defend through to October 1.

The lottery is not less competitive; the selection rate has actually climbed toward 35 percent as the junk filings vanish. But it now rewards a specific kind of candidate. The Indian professional who fits the new template — US degree, senior role, market-rate pay — has never had better odds. The one who doesn't is discovering that the system was redesigned, deliberately, to filter them out.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Lottery Loser's Last Trick Is About to Disappear — and Indian Grads Lean on It Most",
        "subheadline": "A DHS rule at the White House would gut Day 1 CPT and halve the grace period, closing the re-enrollment escape hatch H-1B rejects rely on.",
        "slug": make_slug("day-1-cpt-crackdown-30-day-grace-period-f1-indian-students-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Day 1 CPT and the 60-day grace period are the fallback that lets Indian graduates who lose the H-1B lottery keep working and try again — and a proposed rule would close both, hitting the largest international-student group hardest.",
        "tags": ["f1-visa", "day-1-cpt", "opt", "h1b", "uscis", "students", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE — Tighter student visa rules may impact Indians", "url": "https://theindianeye.com/"},
            {"name": "GoElite — DHS Plan Tightens Student Visas, Limits Training", "url": "https://goelite.com/"},
            {"name": "VisaVerge — F-1 SEVIS Termination & OPT Grace Period Rules 2026", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International graduates in caps and gowns celebrate at a university commencement ceremony",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Coin Flip Is Dead. The New System Rewards a Very Specific Indian Applicant",
        "subheadline": "Registrations fell 38.5% and 71.5% of those selected now hold a US master's degree — the wage-weighted lottery has a clear winner, and a clear loser.",
        "slug": make_slug("h1b-wage-weighted-selection-us-masters-71-percent-india-fy2027"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians win roughly three-quarters of H-1B visas, so the shift from a random lottery to a wage-weighted, advanced-degree-favoring system reshapes the odds for every Indian professional and student in the queue.",
        "tags": ["h1b", "uscis", "wage-level", "lottery", "us-masters", "opt", "fy2027"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaVerge — H-1B 2026: FY 2027 Lottery Registrations Drop 38.5%", "url": "https://www.visaverge.com/"},
            {"name": "Tafapolsky & Smith LLP — FY 2026 H-1B Cap Registration Statistics", "url": "https://www.tandslaw.com/"},
            {"name": "The Register — H-1B registrations dropped for FY 2026", "url": "https://www.theregister.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A team of software developers working together on computers in a modern office",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
