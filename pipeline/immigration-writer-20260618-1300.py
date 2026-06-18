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

article1_body = """The rule that let hundreds of thousands of Indian women work in America is now sitting on a bureaucrat's desk in its final draft. When it surfaces for public comment — and the Department of Homeland Security has told a federal court it is in the last stages of writing it — the clock will start ticking on the H-4 employment authorization program that has anchored two-income Indian households since 2015.

DHS confirmed the rule's status in a court filing tied to *Save Jobs USA v. DHS*, the long-running lawsuit brought by a group of American technology workers who argue the program lets foreign spouses compete for their jobs. For years the case bounced between dismissal and appeal. What changed is the government's posture: rather than defend the H-4 EAD, the administration now wants to dismantle it, and it has been meeting with the Office of Management and Budget and outside parties to shape the proposed regulation before publication.

## Who actually holds these permits

The H-4 visa goes to dependents of H-1B workers. Since more than 70% of H-1B holders are Indian, the dependent population skews overwhelmingly Indian too — and overwhelmingly female. The work permit, created by the Obama administration in 2015, is available to H-4 spouses whose H-1B partner has cleared a key green-card milestone: either an approved I-140 immigrant petition, or an H-1B extension past the sixth year based on a pending labor certification.

In practice, that describes a very specific person: the wife of an Indian engineer who has been stuck in the employment-based green-card backlog for years, sometimes more than a decade. During that wait, she built a career — in software, finance, medicine, consulting — on the strength of a permit the government is now preparing to revoke.

## Why this lands harder on Indians than anyone else

The cruelty of the timing is mathematical. Indian nationals face the longest green-card queues of any nationality because of per-country caps that treat a country of 1.4 billion the same as a country of four million. The July 2026 visa bulletin made the point brutally: EB-2 India is now listed as "unavailable," meaning no movement at all. Families who once expected the wait to end are now told it may stretch indefinitely.

The H-4 EAD was the pressure valve. It meant a household did not have to survive on one income while the primary applicant's green card crawled forward. Strip it away, and a family that has lived in the United States for a decade — bought a house, enrolled children in local schools, paid into Social Security — suddenly loses half its earning power overnight. The affected workers are not new arrivals. They are established professionals, and many of their employers will be scrambling to replace them.

## What happens next, and when

Nothing changes immediately. DHS has told the court that eligible H-4 spouses may continue to apply for and renew their EADs until further notice. Even after the proposed rule is published, it would not take effect right away: the agency must collect public comments — and a "robust public response" is already expected — then review them and issue a final rule, a process that typically takes several months and often longer for a contested regulation.

That leaves a window. Immigration attorneys are advising H-4 holders to renew existing permits as early as the rules allow, rather than waiting until they near expiry. Anyone newly eligible — whose H-1B spouse just cleared the I-140 threshold — is being told to file now rather than gamble on the program surviving.

## The bigger pattern

The H-4 fight does not stand alone. It arrives alongside the contested $100,000 fee on new H-1B petitions, the proposal to replace students' "duration of status" with a fixed four-year clock, and expanded social-media vetting across nearly every immigration benefit. Each measure, taken individually, is defensible in the administration's framing as a tightening of a system it considers too loose. Taken together, they read as a steady narrowing of the path that brought a generation of Indian professionals — and their families — into American life.

For the Indian American household watching all this, the message is uncomfortable but clear: the second income that made the long green-card wait bearable can no longer be assumed. The rule is not final. But it is closer than it has ever been, and the families it targets have the most to lose and the least time to plan."""

article2_body = """In a 130,000-person stretch of southwest Missouri, an 86-bed hospital keeps its doors open partly on the backs of foreign-born doctors — including a cardiologist from India who arrived through a visa waiver and stayed. Stories like that one, repeated across rural America, are why the fight over the $100,000 H-1B fee is not just a Silicon Valley story. It is a story about who will treat patients in the towns that American medical graduates routinely skip.

The fee, imposed by presidential proclamation in September 2025, has spent the past two weeks in legal whiplash. A Boston federal judge struck it down on June 8, ruling that the charge was effectively an unauthorized tax that only Congress can levy. Four days later the same judge paused his own order to let the government appeal, so as of mid-June the fee is back in force for H-1B petitions that run through a consulate. The First Circuit is now weighing whether it stays that way. For hospitals trying to plan their next residency class, the uncertainty is almost as damaging as the fee itself.

## Why Indian doctors are central to this

Indian physicians make up one of the largest cohorts of internationally trained doctors in the United States, and they are not evenly distributed. A 2025 study of more than 11,000 H-1B physicians found they account for nearly double the share of the doctor workforce in rural counties compared with urban ones — 1.6% versus 0.95% — and a larger share still in the poorest counties. In some communities, researchers found, foreign-trained doctors are one in three, or even one in two, of all physicians.

Many of them follow a specific path: medical school abroad, a US residency, then a J-1 visa waiver that lets them skip the mandatory two-year return home in exchange for serving a designated shortage area, before transitioning to H-1B status. That transition is exactly the moment the $100,000 fee can bite. For a rural hospital operating on thin margins, a six-figure surcharge per physician is not a line item — it is a hiring freeze.

## The numbers behind the anxiety

The Greater New York Hospital Association, which represents 260 mostly teaching hospitals, surveyed its members and found that a quarter had already paused, deferred, or limited the recruitment of physicians needing H-1B visas. Those hospitals collectively employ 1,100 H-1B medical residents and another 800 H-1B attending physicians. When recruitment decisions for incoming residents are made — rank-order lists are due weeks before Match Day — program directors have to decide whether they can even afford to consider a candidate who needs sponsorship.

The American Medical Association and the American Hospital Association both wrote to Homeland Security Secretary Kristi Noem warning that the fee would worsen an already severe physician shortage. Their argument is straightforward: the proclamation's stated goal was to stop companies from replacing American workers with cheaper foreign labor, but there is no surplus of American doctors waiting to take rural jobs that international graduates currently fill.

## The diaspora dimension

For Indian American families, this is personal in a way the tech-sector debate often is not. The cardiologist who immigrated in the 1970s to staff a Midwest hospital, the pediatrician who waived into an underserved county, the parent who built a life in a small town because that was where the visa allowed — these are the founding stories of much of the Indian American community outside the coastal tech hubs. The fee threatens to close that door for the next generation of Indian doctors, and with it a pipeline that rural America has quietly depended on for half a century.

There is a narrow exemption in the proclamation for petitions deemed in the "national interest," but legal scholars say the criteria are too vague and too narrow to reliably cover physicians. Hospital associations are pushing for a categorical, industry-wide carve-out for healthcare workers. Whether they get one may depend less on the First Circuit than on Congress, where a separate bill would write the $100,000 fee into permanent law.

## What to watch

The immediate signal is the appellate court's decision on whether the fee stays in effect during the appeal. Beyond that, watch for any move toward a healthcare exemption — and watch the rural hospitals. If recruitment numbers for the next residency cycle come in low, the consequences of this fee will show up not in a courtroom but in an emergency room where the wait for a doctor just got longer."""

article3_body = """There is a deadline circled in red on every Indian EB-5 investor's calendar, and it is closer than most realize: September 30, 2026. After that date, the legal protection that guarantees the government will keep processing a regional-center investment petition — even if the program lapses — no longer applies to new filings. For Indian families weighing the million-dollar route to a green card, the window to lock in that safety net is now measured in weeks, not years.

The EB-5 program lets foreign nationals earn a green card by investing in a US business that creates American jobs: at least $800,000 in a designated Targeted Employment Area, or $1,050,000 elsewhere. For Indian families, its appeal is simple — it requires no employer sponsor, no H-1B lottery, and no decade-long wait in the employment-based backlog. As the H-1B path has grown more expensive and uncertain, EB-5 applications from India have surged, climbing from 750 in 2019 to more than 10,000 by 2022.

## What the September 30 deadline actually protects

Under the EB-5 Reform and Integrity Act of 2022, regional-center petitions "properly filed" on or before September 30, 2026 are grandfathered. That means USCIS must keep adjudicating them even if Congress lets the Regional Center Program lapse afterward. Petitions filed after that date carry no such guarantee. The grandfathering deadline — and a separate September 30, 2027 sunset — apply only to the regional-center pathway, the one most Indian investors use because it pools capital into large projects and counts jobs more generously. The direct, stand-alone EB-5 route is permanently authorized and does not expire.

For Indian-born applicants, the deadline matters more than for almost anyone else, and the reason is the backlog. India is a high-demand country in EB-5, which means even this premium pathway is not immune to retrogression. Filing before the deadline does two things at once: it locks in a priority date, and it locks in the grandfathering protection. Wait, and an investor risks losing both.

## The retrogression warning Indians cannot ignore

The July 2026 visa bulletin underscored why timing is everything. EB-5 Unreserved for India is now listed as "unavailable" on the final-action chart — the same status that hit EB-2 India this month. The set-aside categories tell a different story. Rural, high-unemployment, and infrastructure set-asides remain current for India, which is why advisers are steering Indian capital toward rural Targeted Employment Areas in particular.

That advice is showing up in the market. A Montana rural project in Whitefish just received its I-956F approval from USCIS and opened a second phase of investment, structured for a limited pool of EB-5 investors and projected to create more than 480 jobs — a 27% cushion above the minimum. Rural set-asides also carry priority processing, a meaningful edge when the standard category has gone dark.

## Why this is a diaspora story, not just an investor story

EB-5 is increasingly a family decision made across two generations and two countries. A common pattern: parents in India fund the investment so a child already studying in the United States on an F-1 visa can stay without depending on the H-1B lottery or the OPT pipeline — both of which have been squeezed this year by processing pauses and tougher rules. With EB-2 and now EB-5 Unreserved both showing "unavailable" for India, the rural set-aside has become the rare lane still moving.

The capital itself comes with its own friction. Indian investors must move money under the Reserve Bank of India's Liberalised Remittance Scheme, which caps individual annual outbound transfers — meaning an $800,000 investment often requires pooling across multiple family members and several years. That is precisely why advisers warn against waiting: assembling source-of-funds documentation, completing project due diligence, and clearing the remittance mechanics can take months on its own.

## The practical takeaway

For an Indian family seriously considering EB-5, the message from immigration attorneys is unusually direct: if you want the option to file by September 30, 2026, you should be planning now, not in the final weeks. The grandfathering protection is the closest thing the program offers to certainty, and certainty is in short supply across every other Indian immigration pathway this year. The door is open. It has a date stamped on it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Work Permit That Let Indian Wives Build Careers Is Now in Its Final Draft to Be Killed",
        "subheadline": "DHS has told a federal court the rule to rescind H-4 work authorization is nearly written. For Indian families stuck in the green-card backlog, it threatens the second income that made the wait survivable.",
        "slug": make_slug("h4-ead-rescission-rule-final-draft-indian-spouses-women"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "H-4 work permits go overwhelmingly to the Indian spouses of H-1B workers, so rescinding the program would wipe out the second income that keeps Indian families afloat during their decade-long green-card waits.",
        "tags": ["h4-ead", "h1b", "uscis", "dhs", "green-card-backlog", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — H-4 EAD Rescission Proposal Moves Closer to Completion", "url": "https://www.fragomen.com/insights/proposal-to-rescind-h-4-ead-regulation-moves-closer-to-completion.html"},
            {"name": "Fragomen — H-4 EAD Rescission Proposal Remains Under Federal Review", "url": "https://www.fragomen.com/insights/h-4-ead-rescission-proposal-remains-under-federal-review-dhs-confirms.html"},
            {"name": "Murthy Law Firm — July 2026 Visa Bulletin", "url": "https://www.murthy.com/2026/06/16/july-2026-visa-bulletin/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/3784295/pexels-photo-3784295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A professional woman working on a laptop — the kind of career an H-4 work permit makes possible for the spouses of H-1B visa holders.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The $100,000 H-1B Fee Is a Tech Story to Most. To Rural Hospitals, It's a Doctor Shortage",
        "subheadline": "Indian physicians fill the rural and low-income hospital jobs American graduates skip. The whiplash over Trump's six-figure visa fee is forcing hospitals to freeze the recruitment those communities depend on.",
        "slug": make_slug("h1b-100k-fee-indian-doctors-rural-hospitals-physician-shortage"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian doctors are heavily concentrated in rural and high-poverty US counties, so the $100,000 H-1B fee threatens both the next generation of Indian physicians and the communities that have relied on them for fifty years.",
        "tags": ["h1b", "100k-fee", "indian-doctors", "healthcare", "rural-hospitals", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AAMC — Hospitals depend on H-1B physicians. What happens now?", "url": "https://www.aamc.org/news/hospitals-and-health-systems-depend-h-1b-visa-sponsored-physicians-so-what-happens-now"},
            {"name": "Medscape — 5 Things Doctors Should Know About H-1B Visa Changes", "url": "https://www.medscape.com/viewarticle/5-things-doctors-should-know-about-h-1b-visa-changes-2026a1000abc"},
            {"name": "SHRM — Federal Court Strikes Down $100K H-1B Fee", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/federal-court-strikes-down-100k-h-1b-fee"},
            {"name": "WR Immigration — Court Temporarily Reinstates $100,000 H-1B Fee", "url": "https://wolfsdorf.com/court-temporarily-reinstates-uscis-authority-to-collect-100000-h-1b-consular-processing-fee/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8442619/pexels-photo-8442619.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A healthcare professional in a lab coat walking a hospital corridor, where internationally trained doctors fill critical staffing gaps.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian EB-5 Investors Have a September 30 Deadline — and the Standard Lane Just Went Dark",
        "subheadline": "A grandfathering cutoff guarantees the government will keep processing regional-center petitions filed by Sept. 30, 2026. With EB-5 India now 'unavailable,' advisers say the rural set-aside is the only lane still moving.",
        "slug": make_slug("eb5-india-grandfathering-deadline-september-2026-rural-set-aside"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "As the H-1B and student pathways tighten, Indian families are turning to EB-5, but a September 30, 2026 grandfathering deadline and India's 'unavailable' status mean the window to lock in the million-dollar green card is closing fast.",
        "tags": ["eb5", "investor-visa", "green-card", "visa-bulletin", "uscis", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Shusterman — Visa Bulletin July 2026", "url": "https://www.shusterman.com/visa-bulletin/"},
            {"name": "US Immigration Advisor — EB-5 Visa India 2026", "url": "https://usimmigrationadvisor.com/eb-5-visa-india/"},
            {"name": "Morningstar — USIF Alpine 93/40 Rural EB-5 Project Receives I-956F Approval", "url": "https://www.morningstar.com/news/business-wire/20260616872320/us-immigration-funds-alpine-9340-rural-eb-5-project-receives-uscis-i-956f-approval-as-phase-ii-offering-opens"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "The US Capitol dome, where the laws governing the EB-5 investor visa program and its grandfathering deadlines were written.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
