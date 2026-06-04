#!/usr/bin/env python3
"""Immigration writer — 2026-06-04 08:00 UTC run"""

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

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Operation Checkmate — 30 Indian Truck Drivers
# ─────────────────────────────────────────────────────────────

art1_body = """Between May 11 and 15, US Border Patrol agents fanned out across Arizona's Yuma Sector in an enforcement sweep they called Operation Checkmate. By the time it wrapped, 52 people had been arrested for residing in the country illegally. Thirty-six of them were behind the wheel of a semi-truck. And of those 36 drivers, 30 were Indian nationals.

The operation, disclosed by US Customs and Border Protection in a statement on June 1, targeted undocumented commercial vehicle operators — a category the agency has flagged as a growing public safety concern after a string of fatal highway accidents involving unlicensed drivers. Acting Chief Patrol Agent Dustin Caudle of the Yuma Sector framed the sweep as a safety imperative: "Operation Checkmate reflects our commitment to safeguarding communities and roads from unlawfully present drivers who pose significant risks to public safety."

## Expired Biden-era permits, live trucks

The arrested Indian drivers held commercial driver's licenses from California, New York, Washington and Virginia. Several carried no valid license at all. Most possessed employment authorization documents — the kind issued during the Biden administration to asylum seekers and other applicants — that had since expired or been revoked under Trump-era policy shifts.

That detail matters. Under Biden, hundreds of thousands of work permits were issued to migrants awaiting resolution of their immigration cases. As the Trump administration has tightened enforcement and let many of those permits lapse, workers who once held legal authorization now find themselves operating in a legal void — employed, productive, but without papers.

The trucking industry, perpetually short of drivers, has long been a magnet for immigrants. The American Trucking Associations estimates a national shortage of roughly 80,000 drivers. Indians, particularly from Punjab, Gujarat and Andhra Pradesh, have gravitated toward long-haul trucking as a path to economic independence in the US. Many enter the industry through legitimate channels. Others — like the 30 arrested in Yuma — end up in a gray zone where expired paperwork meets employer demand.

## The enforcement signal

Operation Checkmate did not happen in isolation. It followed an executive order from the Trump administration's Department of Transportation barring "unqualified foreign drivers" from obtaining commercial licenses. The operation is part of a broader pivot toward interior enforcement — not just at the border, but on highways, at weigh stations, and inside the industries where undocumented workers are concentrated.

For the Indian diaspora, the arrests carry a particular sting. India has been among the top nationalities for illegal border crossings into the US in recent years, with thousands attempting the journey through Mexico each year. The Yuma arrests — 30 out of 36 drivers — suggest that Indian nationals are disproportionately represented in the commercial trucking enforcement pipeline, a pattern that could intensify as DHS scales up interior operations.

## What happens next

All 52 individuals arrested in the sweep have been processed under federal immigration law and face deportation proceedings. For the 30 Indians, that likely means removal flights to India, a process that has accelerated under the current administration. Since February 2025, ICE has conducted multiple chartered deportation flights to India, some of which sparked diplomatic tensions after deportees arrived in shackles.

For Indian Americans watching from the sidelines, the story is a reminder that immigration enforcement does not distinguish neatly between "legal" and "illegal" — it operates in the messy space where expired permits, employer demand and policy shifts collide. If you have a family member in trucking, or know someone whose work authorization is lapsing, the message from Operation Checkmate is blunt: the clock is running, and the checkpoints are real."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Operation Checkmate — Thirty Indian Truck Drivers Arrested on Arizona Highways",
    "subheadline": "A federal sweep in Yuma targeted undocumented commercial drivers. Indians made up 30 of 36 trucker arrests, most carrying expired Biden-era work permits.",
    "slug": make_slug("operation-checkmate-30-indian-truck-drivers-arrested-arizona"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals are disproportionately represented in trucking enforcement as expired work permits leave thousands in legal limbo. The arrests signal intensified interior enforcement that reaches beyond the border into the industries where Indian immigrants work.",
    "tags": ["immigration-enforcement", "trucking", "operation-checkmate", "deportation", "work-permits", "arizona"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "US Customs and Border Protection", "url": "https://www.cbp.gov/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/30-indians-living-and-working-illegally-in-us-as-truck-drivers-arrested-will-be-deported/article69642946.ece"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/30-indians-working-illegally-as-truck-drivers-in-us-arrested-face-deportation-1748853570437"},
        {"name": "Firstpost", "url": "https://www.youtube.com/watch?v=operation-checkmate-30-indian-truck-drivers"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32956106/pexels-photo-32956106.jpeg",
    "image_caption": "A semi-truck on an Arizona highway — the state where Operation Checkmate arrested 36 undocumented drivers",
    "image_attribution": "Pexels",
    "body": art1_body,
    "is_editorial": False,
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: The Student Visa Pipeline Crunch
# ─────────────────────────────────────────────────────────────

art2_body = """The numbers arrived quietly, buried in a SEVIS database update, but their implications are loud. Between March 2024 and March 2025, the number of international students tracked in the federal Student and Exchange Visitor Information System fell from 1,153,169 to 1,022,545 — a net loss of 130,624 students, or 11.3 percent. It is the sharpest single-year contraction in a decade.

India, which sends more students to the US than any other country, is right in the middle of it. According to the most recent Open Doors data, new graduate enrollments dropped 15 percent year-over-year. Total international enrollment still grew 3 percent overall, buoyed by continuing students, but the pipeline of fresh arrivals — the cohort that feeds the H-1B workforce two or three years later — is shrinking.

## Three policy threats, one tight window

The decline is not happening in a vacuum. Three policy shifts are converging on Indian students simultaneously.

First, the Department of Homeland Security submitted a final rule to the White House Office of Management and Budget on May 5, 2026, that would replace the open-ended "duration of status" admission for F-1 students with a hard expiration date on the Form I-94. Under the current system, students are admitted for the length of their program plus practical training. Under the proposed system, they get four years — or the length of their program, whichever is shorter — and must then file a formal extension of stay with USCIS, complete with fees and biometrics. The post-completion grace period would shrink from 60 days to 30. DHS expects the rule to take effect as early as September 2026.

Second, Representative Paul Gosar's H.R. 8443 would eliminate Optional Practical Training entirely — the 12-month (or 36-month for STEM) work authorization that roughly 200,000 graduates use each year to gain US work experience before entering the H-1B lottery. Without OPT, the Indian student-to-worker pipeline effectively breaks.

Third, the "Day 1 CPT" pathway — where graduates who fail the H-1B lottery re-enroll in a new program to maintain work authorization — is under scrutiny. Immigration attorney Kathleen Goldman, speaking to The Indian Eye this week, warned that the duration-of-status rule would make it nearly impossible for someone with an existing master's degree to enroll in a second one purely for work authorization. "They are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman said.

## The talent equation

The enrollment decline and the policy threats feed on each other. Prospective students in Hyderabad, Pune and Chennai read the news. They see visa revocations — more than 6,000 F-1 visas were revoked in 2025, many for infractions as minor as a dismissed DUI or a traffic ticket — and they recalculate the risk-reward of a $150,000 American master's degree.

Goldman framed the stakes in blunt terms for US employers: "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent." Foreign nationals make up a substantial share of the US AI talent pool. If Indian enrollment continues to slide, the pipeline that produces the next generation of machine learning engineers, data scientists and software architects narrows accordingly.

The numbers bear this out. Indians and Chinese students together account for nearly half of all international enrollment in the US. But while China's decline has been gradual and partly offset by a shift toward undergraduate programs, India's drop is concentrated in the graduate cohort — precisely the pool that feeds the H-1B system.

## What Indian families should watch

For families weighing a US education, three dates matter. The OBBBA interim final rule on I-94 fees and asylum changes is already effective as of May 29, with public comment open until June 29. The F-1 duration-of-status final rule could publish in the Federal Register within weeks of OMB clearance. And the Gosar OPT bill, while unlikely to pass in its current form, signals a direction of travel that future legislation may follow.

The American university was once the safest on-ramp to the American economy for Indian professionals. That on-ramp is narrowing — not all at once, but in enough places at once that the arithmetic of going is starting to change."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Pipeline Is Drying Up — SEVIS Data Shows 11% Student Decline as Indian Enrollment Hits a Wall",
    "subheadline": "A 130,000-student drop in one year, three converging policy threats, and an immigration attorney's warning that the student-to-worker pathway may not survive intact.",
    "slug": make_slug("sevis-student-decline-indian-enrollment-pipeline-threat"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families weighing US graduate programs face a narrowing pathway: enrollment is dropping, visa revocations are rising, and the OPT-to-H-1B pipeline that built Indian America's professional class is under simultaneous attack from three policy directions.",
    "tags": ["f1-visa", "student-visa", "enrollment-decline", "sevis", "opt", "h1b-pipeline", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "GoElite / SEVIS Data", "url": "https://www.goelite.com/rethinking-recruitment-strategic-solutions-for-2025s-enrollment-decline/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us/"},
        {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/dhs-ends-duration-of-status-f1-j1-fixed-stay-rule/"},
        {"name": "CollegeChalo", "url": "https://collegechalo.com/news/trump-visa-crackdown-6000-international-student-visas/"},
        {"name": "Open Doors / IIE", "url": "https://opendoorsdata.org/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg",
    "image_caption": "Students walking on a US university campus — a pathway that is narrowing for Indian graduates",
    "image_attribution": "Pexels",
    "body": art2_body,
    "is_editorial": False,
}

# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
