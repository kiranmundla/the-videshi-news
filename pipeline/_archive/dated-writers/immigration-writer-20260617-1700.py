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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Just Went Dark. The Door It Slammed May Have Opened a Narrow One Marked EB-3",
        "subheadline": "The July Visa Bulletin makes EB-2 India \"unavailable\" while EB-3 inches forward to January 2014 — reviving an old downgrade gambit that is suddenly the only game in town.",
        "slug": make_slug("eb2-india-unavailable-eb3-downgrade-july-2026-visa-bulletin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the hundreds of thousands of Indians stuck in the employment-based green card queue, the July bulletin removes EB-2 as an option entirely and turns the EB-3 downgrade into the only near-term path to file an I-485 and unlock a work permit and travel document.",
        "tags": ["green-card", "visa-bulletin", "eb2", "eb3", "india", "i-485"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Murthy Law Firm — July 2026 Visa Bulletin", "url": "https://www.murthy.com/2026/06/16/july-2026-visa-bulletin/"},
            {"name": "WR Immigration — June 2026 Visa Bulletin Analysis", "url": "https://wolfsdorf.com/june-2026-visa-bulletin/"},
            {"name": "Scott Legal, P.C. — EB-2 to EB-3 Downgrade", "url": "https://www.legalservicesincorporated.com/immigrant-visas/the-october-visa-bulletin-showed-that-green-cards-are-available-in-the-eb-3-category-sooner-than-in-the-eb-2-category/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8937453/pexels-photo-8937453.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US permanent resident card and supporting immigration documents",
        "image_attribution": "Pexels",
        "body": """The State Department released the July 2026 Visa Bulletin on June 16, and for Indian nationals waiting on an employment-based green card, it reads less like a calendar and more like a closing notice. EB-2 India, the category that carries most of the country's skilled-worker backlog, is now listed as **"unavailable."** No new adjustment-of-status filings in that category until it reopens, which will not happen before the fiscal year resets on October 1.

EB-1 India, the supposed fast lane, retrogressed too — backward to October 15, 2022. The only category moving the right direction is EB-3, which advanced to January 1, 2014. That single line is why immigration lawyers spent Tuesday fielding the same question on repeat: should I downgrade?

## What "unavailable" actually means

"Unavailable" is not retrogression. Retrogression moves the cutoff date backward but leaves the category open. Unavailable shuts it. An Indian applicant with an approved EB-2 I-140 cannot file Form I-485 in July on the strength of that petition, no matter how old the priority date. The visa numbers for the category are simply exhausted for FY2026, and the State Department has been blunt that further retrogressions across employment categories "may be necessary" before September 30.

For someone who has waited a decade, the practical loss is not abstract. An I-485 filing is what unlocks the Employment Authorization Document and advance parole — the work permit that lets a spouse take a job and the travel document that lets the family fly to India without a consular stamping ordeal. With EB-2 dark, that door is bolted.

## The downgrade gambit, revived

Enter the EB-3 downgrade, a maneuver Indian applicants last leaned on heavily during the pandemic-era bulletins. The mechanics: an applicant with an approved EB-2 I-140 whose priority date is current under EB-3 — anything before January 1, 2014 now qualifies — can have their employer file a fresh I-140 in the EB-3 category, then file the I-485 concurrently. The original priority date ports over. The EB-3 cutoff being ahead of a frozen EB-2 is exactly the inversion that makes this worth doing.

The smart version keeps both petitions alive. File a *new* EB-3 I-140 rather than amending the existing one, and the original EB-2 approval stays on the books. If EB-2 ever leapfrogs EB-3 again, the applicant can switch back. Amend instead of adding, and that EB-2 place in line vanishes.

## The catch nobody should ignore

Cutoff dates move both ways. An applicant who downgrades to EB-3 in July could watch EB-3 India retrogress in August — the bulletin's own language warns of "further retrogressions" ahead. That is survivable if the original EB-2 I-140 is preserved, painful if it was thrown away. There is also the matter of timing: USCIS confirmed it is using the more restrictive Final Action Dates chart, not Dates for Filing, so the January 2014 EB-3 cutoff is the real bar, not a softer filing date.

None of this is a do-it-yourself project. The downgrade involves a labor-condition step, a second petition, and a concurrent adjustment filing that has to be sequenced correctly. Filed wrong, it can strand an applicant with two pending petitions and no clean way back.

## Why this lands hard on Indians specifically

The per-country cap is the whole story. India produces far more EB-2 demand than its 7% slice of green cards can absorb, which is why an Indian engineer with a 2013 priority date is still waiting while a comparable applicant from almost anywhere else cleared the queue years ago. When the State Department runs short of numbers late in a fiscal year, India is the chargeability area that gets shut off first. EB-2 going unavailable in July is not a glitch — it is the per-country math arriving on schedule.

For families who have built fifteen years of life around an approved petition, the advice from practitioners is consistent and unromantic: check your priority date against the EB-3 chart, talk to counsel about a dual-petition downgrade before the window narrows further, and do not surrender the EB-2 I-140 to do it. The bulletin reopens October 1. Whether it reopens *favorably* for India is a separate, far less certain question."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Stopped Being Worth the Trouble. Now 40% More Indian Techies Are Going Home",
        "subheadline": "A $100,000 visa fee, a wage-weighted lottery, and four-month stamping lines are reversing a three-decade talent flow — and US tech giants are quietly following the engineers back to Bengaluru.",
        "slug": make_slug("h1b-reverse-migration-india-gcc-tech-talent-2026"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian professionals weighing whether to chase a US assignment or stay home, the calculus has flipped: the same Silicon Valley employers are now hiring in Bengaluru and Hyderabad, making the H-1B gamble look optional rather than essential.",
        "tags": ["h1b", "reverse-migration", "gcc", "india", "tech", "brain-drain"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Computerworld — Restrictive H-1B policies drive tech talent back to India", "url": "https://www.computerworld.com/article/restrictive-h1b-policies-drive-tech-talent-back-to-india.html"},
            {"name": "Nearshore Americas — H1B Impact: Many Indian Tech Workers Return Home", "url": "https://nearshoreamericas.com/h1b-impact-indian-tech-workers-return-home/"},
            {"name": "LiveMint — Why reverse brain drain is unlikely", "url": "https://www.livemint.com/news/india/h1b-visa-holders-not-coming-back-to-india.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36665297/pexels-photo-36665297.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern office building in a major Indian technology hub",
        "image_attribution": "Pexels",
        "body": """For thirty years the arrow pointed one way: India's best engineers boarded flights to San Jose, and the H-1B was the ticket. The arrow is now bending back. LinkedIn data analyzed by Bloomberg shows a **40% jump** over the past year in Indian tech professionals relocating from the United States to India — not a trickle of homesick exceptions, but enough movement to register as a trend with a name. Reverse migration.

The proximate cause is not subtle. A $100,000 fee now attaches to many new H-1B petitions filed for workers outside the country. The FY2027 lottery moved to a wage-weighted system that quadruples the odds for high earners and crushes them for entry-level candidates. And consular stamping lines in India have stretched past four months at major posts. Each of these alone would dent the program's appeal. Together they have changed what the H-1B *means*: less a golden ticket, more a high-cost, low-certainty bet.

## The employers moved first

Here is the twist that makes the return migration sustainable rather than tragic. The same American companies that once relocated Indian engineers to California are now hiring them in India. Meta, Apple, Google, Amazon, Microsoft, and Netflix collectively added more than **32,000 jobs in India during 2025**, an 18% year-over-year jump, according to staffing firm Xpheno. India's global capability centers — the in-house offshore arms of multinationals — now number over 1,700 and account for nearly 40% of the country's office space demand.

Forrester's Ashutosh Sharma argues the shift predates the fee. "Sourcing through offshore centers in India has long been a much more predictable path for US enterprises to gain access to technical talent at scale," he said. "This imposition of $100,000 H-1B fees has simply made it more difficult." In other words, the visa squeeze accelerated a migration of *work* that was already underway. The job did not disappear. It relocated to Bengaluru, and the engineer no longer has to leave home to do it.

## Not everyone is buying the homecoming story

The reverse-migration narrative has a skeptic worth hearing. Vaibhav Domkundwar, a San Francisco venture capitalist who backs Indian founders, has pushed back hard on the idea that established H-1B holders will pack up. "No one is coming back, folks," he wrote bluntly. His point: H-1B workers who have spent fifteen years in the US have homes, mortgages, kids in American schools, and lives built on continuity. They "work to live," he argues, and are not about to abandon settled lives over a policy cycle.

Both things can be true. The professional who arrived in 2010 and owns a house in Fremont is unlikely to leave. The graduate finishing a master's in 2026, staring down a wage-weighted lottery and a $100,000 employer fee, is a different decision-maker entirely. Recruiters in India report that 30-40% of students who study in the US are now applying for Indian jobs — a posture that would have been unthinkable five years ago.

## What it means for the diaspora

For Indian Americans, the trend reshapes the assumption that underpinned a generation of family decisions: that the US assignment was the obvious prize. The Indian government has leaned in with fast-track schemes and tax incentives for returnees, and the GCC boom means a returning engineer can often keep working for the same multinational at a fraction of the relocation friction.

The harder question is what this does to the pipeline that built the diaspora itself. If the entry-level rungs of the H-1B ladder are being sawed off — by fees that price out new hires and a lottery that favors the already-senior — then the community's traditional on-ramp narrows. The diaspora that exists will stay. The diaspora that *would have formed* may increasingly take shape in Hyderabad instead of Houston."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Lottery Stopped Being Random. For New Indian Grads, That Was the Whole Point",
        "subheadline": "USCIS's wage-weighted selection gives top earners four times the odds of entry-level candidates — and roughly 143,000 Indians on OPT just learned which side of that line they fall on.",
        "slug": make_slug("wage-weighted-h1b-lottery-opt-indian-graduates-fy2027"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Most Indian students on OPT are classified at the bottom two wage tiers, meaning the new system structurally disadvantages exactly the fresh graduates who have long relied on the H-1B as their bridge from a US degree to a US career.",
        "tags": ["h1b", "opt", "stem-opt", "f1", "lottery", "india", "students"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Collegedunia — FY2027 H-1B Wage Lottery Results", "url": "https://collegedunia.com/news/fy2027-h1b-wage-lottery-results-indian-opt-students"},
            {"name": "VisaHQ — H-1B lottery results trigger scramble for visa appointments", "url": "https://www.visahq.com/india/"},
            {"name": "Manifest Law — USCIS Confirms FY2026 H-1B Cap Is Full", "url": "https://www.manifestlaw.com/blog/uscis-confirms-fy-2026-h1b-cap-full"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "University graduates at a commencement ceremony",
        "image_attribution": "Pexels",
        "body": """For the first time in the H-1B program's history, the lottery was not a lottery. USCIS completed the FY2027 selection under a wage-weighted system, effective February 27, 2026, that ties an applicant's odds directly to how much they are paid. A candidate at the top wage tier got four entries in the pool. An entry-level candidate got one. The dice were loaded, and they were loaded against the newest arrivals.

For the estimated **143,000 Indian nationals** on OPT or STEM OPT who registered for FY2027, this is not a tweak. It is a structural rewrite of the pathway that has carried Indian graduates from a US classroom to a US paycheck for two decades.

## How the math now works

The system maps to the Department of Labor's four prevailing-wage levels. Level IV — fully competent, top of the pay range — earns four entries. Level III gets three. Level II gets two. Level I, the entry-level tier where most fresh graduates land, gets a single baseline entry.

| Wage level | Profile | Entries |
| --- | --- | --- |
| Level IV | Top of range, senior | 4× |
| Level III | Above median, experienced | 3× |
| Level II | Below median, qualified | 2× |
| Level I | Entry-level graduate | 1× |

A first-year OPT worker in their first real job is almost always classified Level I or Level II for their occupation and location. Experienced hires sit at III or IV. So a senior engineer being sponsored for a second or third H-1B attempt now carries double to quadruple the selection probability of the new master's graduate sitting beside them. The design intent, in the government's framing, is to retain high-value talent. The cost is borne, by construction, by the people just starting out.

## The squeeze gets worse downstream

Selection is only the first hurdle, and the others have grown taller. USCIS has confirmed the FY2026 cap is full with no second lottery expected — so anyone not selected is simply out for the cycle, and for students in their final year of OPT eligibility, that can mean their work authorization lapses within months.

Then comes stamping. Even Indians who *win* the lottery face consular wait times that have ballooned past 200 days at the Mumbai post and well into the autumn at Chennai, after the State Department ended pandemic-era interview waivers for most work visas. Roughly 65,000 principal H-1Bs need appointments, and by one practitioner's estimate 73% of them are Indian nationals. Winning the lottery and actually being able to work are now separated by a months-long bottleneck.

## What new graduates can realistically do

The advice from immigration counsel has shifted from "play the lottery and wait" to "build a backup before you need it." The alternatives being floated:

- **O-1 visa** for those who can document extraordinary ability — a higher bar, but no lottery and no cap.
- **Cap-exempt H-1Bs** through universities, nonprofits, and affiliated research institutions, which sidestep the numerical limit entirely.
- **Going back to school** to extend F-1 status and reset the clock, an imperfect but common stopgap.
- **Day-one CPT programs** that maintain work authorization, though these draw heavier scrutiny and demand careful vetting.

## The longer shadow over the diaspora

The wage-weighted lottery does something quieter than any single denial: it changes who gets to begin. The Indian American professional class was built largely by people who arrived young, won an entry-level H-1B, and climbed from there. A system that now hands the senior and the highly paid four times the odds doesn't just disadvantage this year's graduates — it narrows the on-ramp that created the community in the first place. For a 24-year-old finishing a STEM degree this spring, the message embedded in the new math is hard to miss: the ladder is still there, but the bottom rung has been raised."""
    }
]

inserted = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{inserted}/{len(articles)} articles inserted.")
