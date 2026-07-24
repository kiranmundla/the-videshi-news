#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

articles = [
{
    "id": str(uuid.uuid4()),
    "headline": "EB-2 India Just Went Dark. The July Bulletin Says 'Unavailable' — and Means It",
    "subheadline": "For the first time this fiscal year, no EB-2 green cards will be issued to Indians at all. The number to watch now isn't a priority date. It's the calendar flipping to October.",
    "slug": make_slug("july-2026-visa-bulletin-eb2-india-unavailable-final-action-dates"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "EB-2 is the category most Indian H-1B professionals with advanced degrees are stuck in; its sudden 'Unavailable' status means no green card movement for them until at least October 2026.",
    "tags": ["visa bulletin", "eb-2", "green card", "uscis", "immigration", "backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Capitol Immigration Law Group — July 2026 Visa Bulletin", "url": "https://www.cilawgroup.com/news/july-2026-visa-bulletin"},
        {"name": "WR Immigration — June 2026 Visa Bulletin analysis", "url": "https://wolfsdorf.com/june-2026-visa-bulletin/"},
        {"name": "U.S. Department of State — Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
        {"name": "Lexology — June 2026 Visa Bulletin", "url": "https://www.lexology.com/"}
    ]),
    "score_total": 86,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport, the document at the center of every employment-based green card case",
    "image_attribution": "Pexels",
    "body": """The July 2026 Visa Bulletin carries a single word that should stop every India-born EB-2 applicant cold: **Unavailable.**

Not retrogressed. Not frozen at some date in 2013. Gone. For the remainder of fiscal year 2026 — which runs through September 30 — the State Department will issue no immigrant visas in the EB-2 India category at all. It is the tenth bulletin of the fiscal year, and the harshest.

## How we got here

The collapse did not come out of nowhere. It came in three steps, each grimmer than the last.

In June, EB-2 India had already retrogressed by more than ten months, snapping back to a final action date of September 1, 2013. Then, on May 22, the State Department quietly announced that the India EB-2 category had hit its annual per-country limit for FY2026. The July bulletin simply formalizes the consequence: with the numbers exhausted, the category is marked "U."

For context, EB-1 India also retrogressed — applicants now need a priority date before October 15, 2022 to file, a two-month step backward from June. EB-3 India, the one bright spot, inched forward half a month to January 1, 2014. China, by contrast, saw solid advancement in both EB-1 and EB-3, and family-sponsored applicants worldwide got a five-month leap in the F1 category.

USCIS confirmed it will continue using the more restrictive **Final Action Dates** chart for employment-based filings in July. That matters: it means the slightly more generous Dates for Filing chart is off the table for green card filings, so even applicants who thought they were close cannot submit an I-485.

## Why "Unavailable" is worse than it sounds

The cruelty of an "Unavailable" designation is that it severs the two things an applicant cares about: filing and approving.

An Indian EB-2 worker with a pending I-485 keeps their work permit and travel document. But no one with a fresh case can file, and no pending case can be approved with a green card until numbers free up — realistically not before the fiscal year resets on October 1, when each country gets a new annual allotment.

There is a darker undercurrent that immigration lawyers keep flagging. Former State Department official Charlie Oppenheim has argued that the forward movement Indian applicants briefly enjoyed earlier this year was "artificial" — a byproduct of the administration's policy pausing immigrant visa issuance for nationals of 75 countries, which freed up unused numbers that flowed to India and China. When that policy ends, he warns, there will be a "boomerang effect," and the corrective retrogression could be severe.

## What this means for the diaspora

For the roughly one million Indians waiting in employment-based green card lines — many of them on H-1B status, many with U.S.-born children racing the clock before they age out of dependent status — the July bulletin is a reminder that the backlog is not a queue that steadily shortens. It lurches forward and then slams shut.

The practical takeaways are narrow but real:

- **If your priority date is current and you have not filed I-485, you have already missed this window.** EB-2 India filing is closed until at least October.
- **EB-3 is the only India employment category still moving.** Applicants whose EB-2 cases are stuck are once again weighing the "downgrade" to EB-3, where a January 1, 2014 cutoff is now marginally ahead of where EB-2 sat in June.
- **EB-5, the investor route, remains current** for India's set-aside categories — which is precisely why wealthier applicants have been pouring into it as a backlog escape hatch.

October will bring a fresh allocation of visa numbers and, with it, EB-2 India should return from "Unavailable" to some date in 2013. But the lesson of this fiscal year is that the date giveth and the per-country cap taketh away. For most Indian applicants, the wait is still measured not in months but in administrations."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "With the U.S. Door Sticking, H-1B Indians Are Quietly Reaching for a Canadian One",
    "subheadline": "No country caps, no single-employer trap, and a points system that rewards exactly the profile Silicon Valley built. For backlogged Indians, Express Entry is starting to look less like a backup plan and more like the plan.",
    "slug": make_slug("h1b-indians-canada-express-entry-pr-backlog-alternative-2026"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Decades-long EB-2/EB-3 green card waits and a $100,000 fee scare are pushing India-born H-1B professionals to look north, where permanent residency carries no per-country quota.",
    "tags": ["h1b", "canada", "express entry", "green card", "backlog", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LinkedIn — H-1B Visa Holders: Your Special Pathway to Canada PR (Manoj Palwe)", "url": "https://www.linkedin.com/pulse/h-1b-visa-holders-your-special-pathway-canada-pr-manoj-palwe"},
        {"name": "Government of Canada — Express Entry", "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html"},
        {"name": "Reuters — Trump's $100,000 H-1B visa fee is unlawful, US judge rules", "url": "https://www.reuters.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/25696388/pexels-photo-25696388.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "The Toronto skyline at dusk; Canada's largest city is a top destination for Indian skilled migrants",
    "image_attribution": "Pexels",
    "body": """For a generation of Indian professionals, the H-1B was supposed to be a bridge — a few years of skilled work that ended at a green card and a settled life. In 2026, the bridge keeps getting longer, and a growing number of them are looking at the one running north instead.

The frustration is not abstract. The July visa bulletin marked EB-2 India as "Unavailable" for the rest of the fiscal year. The employment-based green card backlog for Indians now stretches past a decade and, by some estimates, well beyond two. And while a federal judge in Boston struck down the administration's $100,000 H-1B fee this month as an unlawful tax, the fact that such a fee was imposed at all — and that the government has vowed to appeal — has rattled the sense of stability the visa once promised.

## Why Canada keeps coming up

The appeal of the Canadian system is structural, not sentimental, and it lands squarely on the parts of the U.S. process that hurt Indians most.

**No per-country caps.** This is the single biggest difference. The decade-plus EB-2 and EB-3 waits exist because U.S. law limits any one country to roughly 7% of employment green cards each year — a rule that punishes high-demand countries like India and China. Canada's Express Entry has no such quota. A qualified applicant from Mumbai is assessed on the same timeline as one from anywhere else.

**No single-employer trap.** An H-1B is tethered to a sponsoring employer; a layoff starts a frantic 60-day countdown to find another sponsor or leave. Canadian permanent residency, by contrast, is not tied to one job. The security that an American green card represents is, in Canada, the entry ticket.

**A points system built for this exact profile.** Express Entry ranks candidates through the Comprehensive Ranking System (CRS), scoring age, education, work experience and language ability. The young, degree-holding, English-fluent software engineer that the H-1B program selects for is, almost by design, a strong Express Entry candidate. Provincial Nominee Programs (PNPs) add another route for those whose skills match a specific province's needs.

## The catch worth naming

None of this makes Canada a frictionless paradise. The CRS cutoff scores for an Invitation to Apply have climbed as applications surge, and older candidates or those with weaker language scores can find themselves below the line. Canadian salaries in tech run lower than U.S. ones, and the cost of housing in Toronto and Vancouver is punishing. For many H-1B holders, the honest calculation is not "Canada is better" but "Canada is certain, and the U.S. no longer is."

That certainty has real value for people whose lives are on hold. Career moves get postponed because changing jobs means re-running the green card clock. Home purchases wait. Some couples delay having children, or watch anxiously as a U.S.-born teenager approaches the age where they age out of dependent status and fall off the family's pending green card case entirely.

## What the diaspora should weigh

For Indian families in the U.S., the rational move is not to panic-apply but to keep options open. Many are doing exactly that — filing Express Entry profiles as insurance while continuing to live and work in America, ready to activate the Canadian path if a layoff, an aged-out child, or another policy shock forces the issue.

The deeper signal is for U.S. policymakers. The H-1B program was designed to attract and keep the world's best talent. When the most reliable way to secure that talent's future runs through Toronto rather than Texas, the program is quietly working against itself. For now, the people voting with their applications are the ones who waited longest — and finally stopped waiting."""
},
{
    "id": str(uuid.uuid4()),
    "headline": "The October 1 Pay Cut Nobody Warned You About: F-1 to H-1B and the FICA Surprise",
    "subheadline": "The day your H-1B kicks in, a chunk of your paycheck you never used to pay quietly disappears. For thousands of Indian students starting work this fall, the tax math changes overnight.",
    "slug": make_slug("f1-to-h1b-october-fica-tax-payroll-indian-students-2026"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are the largest group converting from F-1 (OPT) to H-1B each October; the moment status changes, the FICA payroll-tax exemption vanishes and take-home pay drops — a shock few plan for.",
    "tags": ["f-1", "opt", "h1b", "fica tax", "students", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IRS — Employers Must Withhold FICA Taxes for Aliens who Change Visa Status to H-1B", "url": "https://www.irs.gov/individuals/international-taxpayers/employers-must-withhold-fica-taxes-for-aliens-who-change-visa-status-to-h-1b"},
        {"name": "IRS — Foreign Student Liability for Social Security and Medicare Taxes", "url": "https://www.irs.gov/individuals/international-taxpayers/foreign-student-liability-for-social-security-and-medicare-taxes"}
    ]),
    "score_total": 72,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6927374/pexels-photo-6927374.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A person fills out a U.S. tax form; FICA withholding rules change the moment F-1 status converts to H-1B",
    "image_attribution": "Pexels",
    "body": """Most of the immigration news that frightens Indian students this year is about doors closing — shorter grace periods, narrower Day-1 CPT, a visa-stamping backlog. Here is one that is smaller, quieter, and lands directly in the bank account: the FICA tax cliff that arrives the day an F-1 student becomes an H-1B worker.

A fresh reminder from the Internal Revenue Service this week restated the rule that catches new H-1B workers off guard every fall. It is worth understanding before your first October paycheck, because the change is automatic and the dollar figure is not trivial.

## The exemption you didn't know you had

While you are on an F-1 (or J-1, M-1 or Q-1) visa as a nonresident, U.S. tax law exempts your wages from FICA — the combined Social Security and Medicare payroll tax. That exemption, set out in Section 3121(b)(19) of the tax code, is why students on Optional Practical Training (OPT) often see a slightly fatter paycheck than their American colleagues doing the same job. About 7.65% of your pay that a citizen co-worker loses to payroll tax, you keep.

Most students never notice the benefit, precisely because it shows up as money *not* taken. They notice when it ends.

## What changes on October 1

H-1B status almost always takes effect on **October 1**, the start of the federal fiscal year and the date cap-subject H-1B petitions activate. The IRS guidance is blunt: "The FICA tax exemption becomes inapplicable when a payee changes to H-1B non-immigrant status," and the employer "must start withholding FICA taxes on the effective date of the H-1B status change."

In plain terms: the day your H-1B begins, 6.2% of your wages (up to the annual Social Security wage base) and 1.45% for Medicare start coming out of every check. On a $110,000 salary, that is roughly $8,400 a year you were not paying the day before — about $700 a month in reduced take-home pay, appearing with no fanfare on the first pay period after your status flips.

## Why this hits Indian students hardest

Indians are, year after year, the single largest cohort moving from F-1/OPT to H-1B. The pipeline is well worn: a master's degree, a STEM OPT period, an H-1B lottery selection, and an October 1 start date. That makes this group the most exposed to a transition that almost no university orientation explains.

The pain is compounded by timing. Many new H-1B workers are simultaneously absorbing other first-year-of-status costs — and, this year, doing so against a backdrop of a green card backlog that gives them little long-term certainty in exchange for the new tax bill.

## How to plan for it

The cliff is unavoidable, but the shock is not. A few practical steps:

- **Budget for the drop before October.** Assume your take-home pay falls by roughly 7.65% the month your H-1B activates, and adjust rent and savings plans accordingly.
- **Check your pay stub in the first October cycle.** Confirm your employer started FICA withholding on the correct date. Errors cut both ways and are easier to fix early.
- **Don't expect a refund.** Unlike over-withheld income tax, FICA paid while you are properly in H-1B status is not refundable — it is simply owed. (FICA wrongly withheld while you were *still* on F-1 OPT, on the other hand, can be reclaimed.)
- **Factor it into job offers.** When comparing an OPT contract role to an H-1B salaried role, remember the post-October number is the one that counts.

It is a small line in a year full of large immigration anxieties. But for a newly minted H-1B professional opening that first post-conversion paycheck, the missing few hundred dollars is the most concrete reminder yet that the rules just changed — and that, on this one, there is no judge to appeal to."""
}
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
