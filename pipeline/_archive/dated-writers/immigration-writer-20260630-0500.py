#!/usr/bin/env python3
"""
Immigration article writer for The Videshi — 2026-06-30 05:00 run.
Two articles:
1. Indian doctors / AAPI angle on H-1B $100K fee ruling
2. OPT/STEM OPT threat for Indian students — USCIS Director Edlow's agenda
"""
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

# ── Article 1 ──────────────────────────────────────────────────────────

art1_body = """The court ruling that struck down the $100,000 H-1B visa fee was reported as a win for the technology industry. It was. But the people who stood to lose the most were not software engineers in Sunnyvale. They were physicians treating patients in towns most Americans could not find on a map.

The American Association of Physicians of Indian Origin — AAPI, the largest organisation of Indian-origin doctors in the United States — called the ruling "a healthcare victory, not a political victory." Its president, Dr Amit Chakrabarty, was blunt about the stakes: had the fee survived, hospitals in underserved communities would have pulled job offers, left positions unfilled, and watched patients travel hours for care that used to be down the road.

## The numbers behind the white coat

International medical graduates — physicians trained outside the United States and Canada — make up roughly a quarter of the country's practising doctors. In rural and underserved areas, the share is closer to 40 per cent. More than half of all internal medicine trainees are IMGs. In specialties where workforce shortages are most acute — geriatrics, nephrology, endocrinology, infectious disease — they are not a supplement. They are the workforce.

A large share of these physicians are Indian-born. They arrive through J-1 exchange visitor programmes, transition to H-1B sponsorship, and often commit to serving in Health Professional Shortage Areas for years before they can begin the green card process. The pipeline is slow, precarious, and utterly essential to the functioning of the American healthcare system.

## What $100,000 would have meant

The maths was simple and punishing. A resident physician earns roughly $55,000 to $70,000 a year. A community hospital sponsoring that resident on an H-1B visa would have been asked to pay an additional $100,000 — a fee that in many cases would have exceeded the physician's annual salary.

"There's no way that this inner-city, single, not-big hospital is going to be able to afford $100,000 per physician to come in," Bobby Mukkamala, president of the American Medical Association, told *Medscape*. Mukkamala practises in Flint, Michigan — not rural, but deeply underserved, where 30-odd IMG residents arrive every year to staff the wards. His own parents, both IMGs from India, came to Flint in 1970 to practise.

The Association of American Medical Colleges projects a deficit of up to 86,000 physicians by 2036. Pricing out the very doctors willing to serve where American graduates will not does nothing to close that gap.

## A ruling, not a resolution

U.S. District Judge Leo Sorokin struck down the fee on June 9, ruling it was an unlawful tax Congress never authorised. But the D.C. Circuit has upheld a separate challenge, and a third lawsuit is pending in San Francisco. The legal landscape is fractured across three appellate circuits, and the White House has vowed to appeal.

For now, the fee is blocked. But hospitals are not planning on the basis of "for now." Several programme directors have told immigration attorneys they are already scaling back IMG hiring — not because the fee is in effect, but because the uncertainty itself is a cost they cannot bear.

## The diaspora angle

The pattern is familiar to anyone who has tracked the Indian immigration story: policies designed to regulate one part of the system — in this case, tech outsourcing — end up wounding another. Indian-origin physicians do not game the H-1B system. They do not displace American workers. They fill vacancies that American medical graduates have chosen not to take. They do it in Flint and rural Nebraska and safety-net hospitals across Appalachia.

AAPI has called for physician-specific exemptions from any future fee structure. Dr Chakrabarty's argument is not that doctors deserve special treatment. It is that patients in underserved communities deserve care — and that the physicians willing to provide it should not be treated as collateral damage in a fight about Silicon Valley staffing models.

"Policies that create barriers for physicians ultimately become barriers for patients," he said. It is hard to argue with that."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "One in Four American Doctors Trained Abroad. The Fee Nearly Drove Them Out",
    "subheadline": "The $100,000 H-1B surcharge was designed to deter tech outsourcers. It almost emptied rural hospitals instead.",
    "slug": make_slug("indian-doctors-aapi-h1b-fee-ruling-rural-healthcare-imgs"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Thousands of Indian-origin physicians staff underserved American hospitals on H-1B visas; the $100,000 fee threatened to price them out and collapse care in communities that depend on them.",
    "tags": ["h1b", "healthcare", "aapi", "immigration", "physicians", "uscis", "indian-doctors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye — AAPI Statement", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Medscape — Rural H-1B Docs", "url": "https://www.medscape.com/"},
        {"name": "STAT News — H-1B and Physician Workforce", "url": "https://www.statnews.com/"},
        {"name": "Education Week — Judge Strikes Down Fee", "url": "https://www.edweek.org/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6129240/pexels-photo-6129240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A doctor examines a patient in a hospital room — international medical graduates make up one in four US physicians",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ── Article 2 ──────────────────────────────────────────────────────────

art2_body = """The man who runs U.S. Citizenship and Immigration Services has a clear view of what international students should be allowed to do after they graduate: nothing.

"What I want to see would be essentially a regulatory and sub-regulatory program that would allow us to remove the ability for employment authorizations for F-1 students beyond the time that they are in school," USCIS Director Joseph Edlow said at his confirmation hearing in May 2025. Fourteen months later, the regulatory machinery is catching up with the rhetoric.

## The proposed rule

On May 5, 2026, the Department of Homeland Security formally proposed eliminating "Duration of Status" — the framework that has governed F-1 student visas since 1979. Under the current system, international students may remain in the United States as long as they maintain valid student status. That includes the post-graduation work periods known as Optional Practical Training and STEM OPT, which together can provide up to three years of work authorisation.

The proposed rule would replace the open-ended stay with a fixed admission period of up to four years. Extensions — including for OPT — would require formal USCIS approval rather than the current university-managed process. The grace period after status ends would be cut from 60 days to 30. And students who already hold a master's degree would be barred from enrolling in a second programme at the same or lower level, a provision that effectively kills the Day 1 CPT pathway that thousands of Indians use to remain employed between H-1B lottery attempts.

The rule is expected to take effect in September 2026.

## Why Indians are the target

The numbers are not ambiguous. Indians represent approximately half of all participants in OPT and STEM OPT programmes, according to government data. They are the largest international student group entering American graduate programmes in STEM fields — the very fields where OPT usage is heaviest.

A 2025 survey by NAFSA and the Institute for Progress found that 54 per cent of current international students would not have chosen the United States if OPT did not exist. For Indians, the figure is likely higher: the entire F-1-to-OPT-to-H-1B pipeline is the dominant pathway for Indian professionals entering the American workforce.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of Build, an immigration advisory firm. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working.'"

## The double squeeze

The timing is not accidental. The new wage-weighted H-1B selection system, which went into effect for the FY2027 season, has already halved the odds for entry-level applicants — exactly the category most Indian OPT workers fall into. If OPT itself becomes harder to obtain or extend, the fallback for failed H-1B lottery entrants vanishes.

Goldman was direct about what this means for American employers: "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent." Foreign nationals make up a substantial share of the US AI talent pool. Companies that cannot hire them will either move the work offshore or stop competing at the frontier.

## 30,000 already left

The pipeline is already leaking. In the most recent academic year, approximately 30,000 Indian students left American universities — a figure that coincides with a doubling of Indian enrolment in German institutions. Canada, Australia, and the United Kingdom have all expanded post-study work rights in the same period that Washington has moved to contract them.

The International Council for Education and Foreign Student Affairs has warned that restricting OPT would undermine the core value proposition American universities offer international students: the ability to work after graduation and build a career. Without it, the calculus shifts sharply toward competitors.

## What to watch

The proposed rule is in its public comment period through late summer 2026. Immigration attorneys expect the final version to be published in late autumn, with the September timeline ambitious but not impossible. Court challenges are likely, particularly from universities and employer coalitions.

For Indian students currently enrolled or considering American programmes, the message is stark: the post-study work pathway that defined the American dream for a generation of Indian professionals is no longer guaranteed. Multiple backup plans — O-1 visas for exceptional talent, cap-exempt H-1B positions, or departure to friendlier jurisdictions — are no longer optional. They are essential."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Half of All OPT Workers Are Indian. The Man Running USCIS Wants to End the Programme",
    "subheadline": "A proposed rule would kill Duration of Status, gut post-study work rights, and close the Day 1 CPT escape hatch. The impact on Indian students would be immediate and severe.",
    "slug": make_slug("opt-stem-indian-students-uscis-edlow-duration-status-end"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians make up roughly half of all OPT and STEM OPT participants in the US; the proposed rule to eliminate Duration of Status and restrict post-study work threatens the primary pipeline through which Indian professionals enter the American workforce.",
    "tags": ["opt", "stem-opt", "f1-visa", "students", "uscis", "immigration", "indian-students", "day1-cpt"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye — Student Visa Rules", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "ICEF Monitor — Duration of Status", "url": "https://monitor.icef.com/"},
        {"name": "Ahluwalia Law — F-1 OPT Changes 2026", "url": "https://ahluwalialaw.com/"},
        {"name": "NAFSA/Institute for Progress Survey", "url": "https://www.nafsa.org/"},
        {"name": "USCIS — Premium Processing OPT", "url": "https://www.uscis.gov/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7683887/pexels-photo-7683887.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "International students on an American university campus — Indians make up roughly half of all OPT participants",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ── Insert ─────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
