#!/usr/bin/env python3
"""Insert 3 fresh immigration articles for The Videshi (2026-06-22 1600).
Topics:
  1. Documented Dreamers / America's Children Act
  2. The true cost of an H-1B in 2026 (fee stack)
  3. AI layoffs & the 60-day clock (Opendoor India shutdown + tech layoff wave)
All status=review, is_editorial=False, category/vertical=immigration.
"""
import os, json, subprocess, sys

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"]

ARTICLES = [
# ------------------------------------------------------------------ 1
{
  "slug": "documented-dreamers-americas-children-act-indian-aging-out-21-green-card-backlog-20260622",
  "category": "immigration",
  "vertical": "immigration",
  "urgency": "medium",
  "headline": "They Grew Up American. At 21, the Law Tells Them to Leave.",
  "subheadline": "The bipartisan America\u2019s Children Act would protect roughly 250,000 \u2018Documented Dreamers\u2019 \u2014 children who came legally on their parents\u2019 work visas \u2014 from aging out of status. Indian families, trapped in the longest green card lines, have the most to lose.",
  "diaspora_angle": "The decades-long employment green card backlog for Indians is precisely what causes children to age out: their parents are still waiting in line when the kids turn 21. No community is more exposed to the aging-out problem than Indian H-1B families.",
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/United_States_Capitol_west_front_edit2.jpg/1280px-United_States_Capitol_west_front_edit2.jpg",
  "image_caption": "The US Capitol in Washington, where the bipartisan America\u2019s Children Act has been reintroduced to protect Documented Dreamers from aging out.",
  "image_attribution": "Architect of the Capitol / Wikimedia Commons (Public domain)",
  "tags": ["documented-dreamers", "americas-children-act", "aging-out", "green-card-backlog", "legislation", "immigration"],
  "sources": [
    {"name": "Senator Alex Padilla \u2014 Padilla, Paul, Ross, Miller-Meeks Introduce Bipartisan Bill to Protect Documented Dreamers", "url": "https://www.padilla.senate.gov/newsroom/press-releases/"},
    {"name": "Senator Dick Durbin \u2014 Durbin Joins Introduction of Bipartisan Bill Protecting Documented Dreamers", "url": "https://www.durbin.senate.gov/newsroom/press-releases"},
    {"name": "Rep. Deborah Ross \u2014 Bipartisan, Bicameral Bill to Protect Documented Dreamers", "url": "https://ross.house.gov/media/press-releases"},
    {"name": "The Indian Eye \u2014 \u2018Documented dreamers\u2019 of Indian diaspora in US face uncertain future", "url": "https://theindianeye.com/"}
  ],
  "body": """Muhil Ravichandran was two years old when her family moved to the United States. She has spent more than two decades here \u2014 school, friends, a life \u2014 yet she now faces the prospect of self-deporting to a country she barely remembers. \"Due to the green card backlog, I had aged out by the time my parents finally received their green cards,\" she says. \"My future is now uncertain.\"

Her story is not unusual. It is the defining injustice facing a group that immigration advocates call \"Documented Dreamers\": an estimated 250,000 young people who came to America legally as dependent children on their parents' work visas, grew up American in every respect except citizenship, and then lose their legal status the moment they turn 21.

## How a legal childhood becomes an illegal adulthood

The mechanics are cruelly simple. US immigration law lets the children of visa holders remain as dependents only until their 21st birthday. For most nationalities, that is a non-issue: the family secures permanent residency long before the eldest child ages out. For Indians, it is a trap.

The employment-based green card system caps the share any single country can claim each year. Because Indian applicants vastly outnumber those slots, the queue for an India-born professional now stretches across decades \u2014 by some estimates, longer than a working lifetime. Parents who arrived on an H-1B in their twenties may still be waiting when their children reach adulthood. When the clock strikes 21, the child is no longer a dependent. They must find their own visa, leave, or fall out of status entirely.

These are not strangers to America. Many have known no other home. They were educated in American schools, often graduating from American universities, and they are statistically among the most accomplished young people the country produces. And yet the law treats their 21st birthday as an eviction notice.

## A rare bipartisan fix

Into this gap steps the America's CHILDREN Act, reintroduced by an unusually broad coalition: Senators Alex Padilla, a California Democrat, and Rand Paul, a Kentucky Republican, alongside Representatives Deborah Ross of North Carolina and Mariannette Miller-Meeks of Iowa. The Senate version has drawn cosponsors spanning the ideological spectrum \u2014 Dick Durbin, Susan Collins, Chris Coons, Kevin Cramer, John Curtis, Angus King, Amy Klobuchar and Lisa Murkowski among them.

The bill would do three core things. It would lock in a child's age on the date their parents file for a green card, so that years lost in the backlog no longer push them past the cutoff. It would let children who have spent at least eight years in the country as dependents and graduated from a US institution apply for permanent residency. And it would grant work authorization to those qualifying for age-out protection, ending the limbo in which talented graduates cannot legally hold a job.

\"Fixing this loophole puts in place a policy most Americans assume already exists,\" says Dip Patel, founder of Improve The Dream, the advocacy group that has become the movement's organising force. The bill is endorsed by an equally cross-cutting set of organisations, from the free-market Americans for Prosperity to the National Immigration Forum.

## Long odds, high stakes

For all its bipartisan sheen, the bill faces a Congress that has not passed meaningful legal-immigration reform in years and is consumed by fights over the H-1B program, fees and enforcement. Versions of this legislation were introduced in 2021 and 2023 and went nowhere. The political oxygen in 2026 is being spent elsewhere.

That makes the stakes for Indian families especially acute. Every month of inaction pushes more children past 21. Families that have done everything the system asked \u2014 entered legally, paid taxes, built careers, raised children who excelled \u2014 are watching those children priced out of the only country they know, not by any failing of their own but by an arithmetic of quotas no individual can escape.

For the diaspora, the Documented Dreamers are a mirror. They are the second generation that the H-1B bargain was supposed to reward, and their predicament exposes how the green card backlog has stopped being merely a wait and become a generational rupture. Whether Washington acts before more of them age out is, for now, an open question \u2014 and for families counting birthdays, an agonising one."""
},
# ------------------------------------------------------------------ 2
{
  "slug": "true-cost-h1b-2026-fee-stack-100000-proclamation-indian-workers-20260622",
  "category": "immigration",
  "vertical": "immigration",
  "urgency": "medium",
  "headline": "What an H-1B Actually Costs in 2026, Line by Line",
  "subheadline": "Before the $100,000 proclamation fee, sponsoring a single H-1B worker already meant a stack of charges that climbed past $3,000. Add the new fee and the bill for one petition can clear $103,000 \u2014 reshaping who gets hired, and who gets left behind.",
  "diaspora_angle": "Indians receive the largest share of H-1B visas by far, so the rising cost of sponsorship falls hardest on Indian workers \u2014 especially at the small consultancies and startups that cannot absorb a six-figure fee, and on entry-level candidates whose salaries no longer justify the spend.",
  "image_url": "https://images.pexels.com/photos/5466789/pexels-photo-5466789.jpeg?auto=compress&cs=tinysrgb&w=1200",
  "image_caption": "US currency. The cumulative government cost of sponsoring a new H-1B worker now runs to six figures under the 2025 presidential proclamation.",
  "image_attribution": "olia danilevich / Pexels",
  "tags": ["h1b", "visa-fees", "100k-fee", "cost-of-sponsorship", "employers", "immigration"],
  "sources": [
    {"name": "DavidsonMorris \u2014 H-1B Visa Costs 2026: Full Employer & Worker Guide", "url": "https://www.davidsonmorris.com/h1b-visa-costs/"},
    {"name": "LegalClarity \u2014 H-1B Fee Increase: Current Costs and the New $100K", "url": "https://legalclarity.org/"},
    {"name": "Fragomen \u2014 DHS Proposes Fee Rule with Significant Increases for Employment-Based Petitioners", "url": "https://www.fragomen.com/insights/"},
    {"name": "SHRM \u2014 Compliance News: Employers with H-1B Visas Face $100,000 Fee", "url": "https://www.shrm.org/"}
  ],
  "body": """For years the cost of hiring an H-1B worker was a line item employers grumbled about but rarely questioned. In 2026 it has become a strategic decision \u2014 and for many smaller firms, a deterrent. The reason is not a single charge but an accumulation of them, capped by a presidential fee so large it dwarfs everything that came before.

Here is what sponsoring one new H-1B worker now involves, item by item.

## The standard stack

Start with the entry ticket. To enter the annual lottery, an employer pays a registration fee that jumped from a token $10 to **$215** \u2014 a more than twentyfold increase. Win a slot, and the petition itself begins.

The base Form I-129 filing fee rose from $460 to **$780** for most employers, a 70% increase, with a reduced $460 rate preserved for small businesses and non-profits. On top sits the **$500** Fraud Prevention and Detection fee and the ACWIA training fee of **$1,500** for larger employers (or $750 for those with fewer than 25 staff). Then there is the newest addition, a **$600** Asylum Program Fee levied on nearly every I-129 petition, intended to subsidise the asylum system.

Tally those and a large employer was already paying roughly **$3,380** in government fees per new hire before September 2025 \u2014 and that is before optional premium processing, which buys faster adjudication for **$2,805** and rises with inflation, and before attorney fees that typically run $2,500 to $7,500.

## The fee that changed the math

Then came Presidential Proclamation 10973, which imposed a **$100,000** fee on new H-1B petitions requiring consular processing. Litigation has swirled around it \u2014 a federal judge in Massachusetts struck it down as an unauthorised tax, and the matter is on appeal \u2014 but its mere existence has already reset employer behaviour.

With the proclamation fee layered on, the all-in government cost of a single new H-1B for a large employer reaches roughly **$103,380**, according to one breakdown. For a small employer it is about $102,010, and even a qualifying non-profit \u2014 exempt from several charges \u2014 lands near $100,960. The $100,000 fee, in other words, swamps every other cost combined. What was a $3,380 decision is now a $103,000 one.

## Who pays \u2014 and who gets cut

On paper, almost all of these fees are the employer's responsibility; only the $205 visa application fee and, in narrow circumstances, premium processing may fall to the worker. In practice, the burden reshapes the labour market in ways that land squarely on Indian professionals, who receive the largest share of H-1B visas of any nationality.

The first casualties are the entry-level and the offshore-adjacent roles. A six-figure sponsorship cost is easy to justify for a senior engineer commanding a high salary; it is impossible to justify for a junior analyst. The fee effectively prices out younger Indian candidates and recent graduates whose compensation cannot absorb the spend \u2014 the very people the program once served as a launchpad.

The second casualties are the small sponsors. The large technology firms \u2014 Amazon, Apple, Google, Meta, Microsoft \u2014 and the big IT consultancies can write a $100,000 cheque. The mid-sized consultancy, the startup, the regional hospital sponsoring a physician cannot. As sponsorship concentrates among a handful of giants, the diversity of employers willing to hire Indian talent narrows sharply.

## The bottom line for the diaspora

For an Indian worker weighing a US career, the fee stack is more than an employer's accounting problem. It changes who will sponsor them, at what stage of their career, and for what salary. It pushes the H-1B further toward senior, high-wage hires and away from the early-career pipeline. And it adds yet another reason for talent to weigh alternatives \u2014 Canada, the Gulf, or the booming global capability centres back home in India \u2014 against an American path that grows costlier by the filing.

Whether the $100,000 fee survives the courts will determine just how steep that path becomes. But even the standard stack, quietly ratcheted up over the past two years, has already made the H-1B a markedly more expensive proposition than it was \u2014 and the people who feel it first are the ones it was built to attract."""
},
# ------------------------------------------------------------------ 3
{
  "slug": "ai-layoffs-h1b-60-day-clock-opendoor-india-shutdown-indian-tech-workers-20260622",
  "category": "immigration",
  "vertical": "immigration",
  "urgency": "high",
  "headline": "AI Is Erasing the Jobs That Anchored India\u2019s Tech Diaspora",
  "subheadline": "Opendoor shut its entire India operation in a single stroke, citing AI \u2014 250 jobs gone. With more than 110,000 tech layoffs logged globally this year, Indian H-1B workers in America face a 60-day clock that AI is winding tighter.",
  "diaspora_angle": "For Indian H-1B holders, a layoff is not just a lost paycheck \u2014 it starts a 60-day countdown to find a new sponsor or leave the country. The AI-driven layoff wave hits this community at both ends: eliminating offshore jobs in India and threatening the onshore jobs that H-1B status depends on.",
  "image_url": "https://images.pexels.com/photos/9300765/pexels-photo-9300765.jpeg?auto=compress&cs=tinysrgb&w=1200",
  "image_caption": "An empty office workstation. AI-driven restructuring is eliminating both offshore roles in India and onshore positions that H-1B status depends on.",
  "image_attribution": "Mikhail Nilov / Pexels",
  "tags": ["ai-layoffs", "h1b", "60-day-grace-period", "tech-layoffs", "opendoor", "immigration"],
  "sources": [
    {"name": "Outsource Accelerator \u2014 Opendoor closes India operations entirely as AI replaces offshore work", "url": "https://news.outsourceaccelerator.com/"},
    {"name": "The Hindu \u2014 Opendoor shuts India operations, lays off 250 employees; embraces AI", "url": "https://www.thehindu.com/business/"},
    {"name": "TechCrunch \u2014 Opendoor\u2019s India exit is fueling a bigger conversation about AI and outsourcing", "url": "https://techcrunch.com/"},
    {"name": "The Port Journal \u2014 TCS and Opendoor fuel worries over AI impacting India\u2019s tech jobs", "url": "https://theportjournal.com/"}
  ],
  "body": """On a Tuesday in June, some 250 employees at the proptech firm Opendoor reported to offices in Chennai and Bengaluru. By the evening, the offices were closing for good. The American home-buying company was shutting its India operation entirely \u2014 and, unusually, it said why in plain terms: artificial intelligence had made the work redundant.

The closure is among the most direct documented cases of a US technology company explicitly naming AI automation, rather than ordinary cost-cutting, as the reason for eliminating offshore headcount. Opendoor's chief executive, Kaz Nejatian, framed it as part of a broader \"Opendoor 2.0\" redesign that rebuilt operations around AI-native processes run by smaller US-based teams, with proximity to American customers as a stated design principle. The company's global workforce had already contracted by nearly a third over the previous year; the India shutdown eliminated most of what remained offshore.

## A pattern, not an outlier

Opendoor is a small company, but its move crystallised a fear rippling through India's technology sector. Tata Consultancy Services, the bellwether of Indian IT, has signalled it may slow hiring. Industry trackers have logged more than 110,000 tech-worker layoffs globally in 2026, with large reductions at the biggest names. The debate that Opendoor reignited \u2014 is AI finally coming for outsourcing? \u2014 is no longer hypothetical.

For the Indian diaspora, the threat arrives from two directions at once. In India, AI is hollowing out the offshore delivery jobs that built the country's IT economy. In America, the same automation wave is thinning the onshore engineering and operations roles that hundreds of thousands of Indians hold on H-1B visas. The community is exposed at both ends of the same pipeline.

## The 60-day clock

What makes the onshore risk uniquely punishing is a rule most American workers never have to think about. When an H-1B worker loses their job, federal regulations grant a grace period of up to 60 days to find a new sponsoring employer, change to another visa status, or leave the country. Miss the window and lawful status lapses.

Sixty days is a brutally short runway in a hiring market that AI is actively cooling. A laid-off Indian engineer must not merely find a new job but find an employer willing and able to sponsor an H-1B transfer \u2014 a commitment that, in 2026, also means navigating sharply higher petition costs. Every week spent interviewing is a week off the clock. For families with children in school, mortgages, and spouses on dependent visas, the countdown turns a professional setback into an existential one.

The squeeze is compounded by timing. The same firms most aggressively adopting AI are often the largest H-1B sponsors. When they restructure, they release into the market precisely the workers whose ability to remain in the country depends on being quickly re-hired \u2014 just as the number of available roles contracts.

## Hedging against the clock

The uncertainty has pushed many Indian professionals to think defensively. Immigration advisers report rising interest in self-petitioned green card categories that do not tie a worker's status to a single employer \u2014 the EB-1A for individuals of extraordinary ability and the national interest waiver chief among them. The logic is straightforward: a green card application that an employer cannot revoke is insurance against the 60-day clock.

Others are reconsidering geography altogether. India's global capability centres \u2014 the in-house technology and operations hubs that multinationals run on Indian soil \u2014 are expanding even as outsourced delivery shrinks, offering a domestic landing spot for talent that might once have headed to Silicon Valley. The Gulf and Canada continue to court skilled Indians with faster, more predictable residency paths.

## A different kind of disruption

Layoff waves are not new to the diaspora; the tech sector has weathered several. What is new is the driver. Previous downturns were cyclical \u2014 markets fell, companies cut, hiring eventually resumed. An AI-driven restructuring is structural. When a company rebuilds its operations around automation, the eliminated roles do not come back when conditions improve; they simply cease to exist.

For Indian workers who staked their American lives on the durability of tech employment, that distinction matters enormously. The 60-day clock was always a source of anxiety. AI has made the ground beneath it shift \u2014 and, for the moment, it is shifting in only one direction."""
}
]


def insert(article):
    payload = dict(article)
    payload["sources"] = json.dumps(article["sources"])
    payload["is_editorial"] = False
    payload["is_featured"] = False
    payload["status"] = "review"
    body = json.dumps([payload])
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", body,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        res = json.loads(out.stdout)
    except Exception:
        return False, out.stdout[:500]
    if isinstance(res, list) and res and res[0].get("id"):
        wc = len(article["body"].split())
        return True, f"{res[0]['id']}  (~{wc} words)"
    return False, str(res)[:500]


if __name__ == "__main__":
    print("Inserting", len(ARTICLES), "immigration articles (status=review)\n")
    ok = 0
    for a in ARTICLES:
        success, msg = insert(a)
        flag = "OK " if success else "FAIL"
        if success: ok += 1
        print(f"[{flag}] {a['slug']}\n        {msg}\n")
    print(f"Done: {ok}/{len(ARTICLES)} inserted.")
