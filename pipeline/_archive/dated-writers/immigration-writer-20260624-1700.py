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

article1_body = """The fourth annual Capitol Hill Day looked, from the outside, like every other lobbying push that fills Washington's calendar: lanyards, talking points, a summit reception to follow. What set it apart was arithmetic. Nearly 200 Indian American delegates from 25 states fanned out across more than 125 Congressional offices on Tuesday, June 23 — the largest single-day advocacy effort the community has ever mounted, organised by the Foundation for India and Indian Diaspora Studies (FIIDS).

The timing was not accidental. The diaspora is being squeezed on multiple fronts at once: a proposed $100,000 H-1B fee tied up in the courts, an "unavailable" EB-2 India category in the July visa bulletin, a 75% jump in citizenship fees, and a steady drumbeat of what delegates described as anti-Hindu and anti-India sentiment. For a community used to lobbying quietly through campaign cheques and corporate clout, the shift to organised, in-person pressure marks a change in tactics.

## What the delegates asked for

FIIDS built its pitch around five priority areas: Indo-Pacific trade and security, the broader US-India strategic partnership, recognition of Indian American contributions, immigration reform "for US innovation," and critical-minerals supply-chain security. But for the rank-and-file delegate, one item dominated the conversations in Congressional offices — the per-country green card cap.

The 7% country limit on employment-based permanent residency is the single rule that turns an Indian engineer's green card wait into a multi-decade ordeal while a similarly qualified applicant from a smaller country waits a year or two. FIIDS has long argued for scrapping it, and the group again pressed lawmakers to support backlog-reduction legislation. Khanderao Kand, the group's chief of policy and strategy, framed the day in transactional terms: "This is a moment to translate influence into policy impact."

## The sympathetic audience problem

The delegates did not lack for warm words. Congressman Raja Krishnamoorthi, the Illinois Democrat who has previously introduced backlog-reduction measures, told the gathering that Indian Americans — "four million strong," the most educated and most prosperous minority in the country — were nonetheless "facing new challenges," and urged them to run for office at every level. "If you don't have a seat at the table, you're on the menu," he said. Congressman Suhas Subramanyam echoed the call for greater representation. Senator Roger Marshall, a Kansas Republican, praised the community as living proof that legal immigration works.

The trouble with sympathetic audiences is that sympathy is cheap. Versions of these speeches have been delivered at FIIDS events for years — the April 2025 advocacy day pushed the identical demand to abolish country caps, and a smaller June 2026 outing two weeks earlier hit the same notes. The bills exist; the votes do not. Backlog-reduction proposals have repeatedly cleared one chamber only to die in the other, and the current Congress has shown far more appetite for restricting work visas than for clearing the green card queue.

## Why this matters to Indian Americans

For the roughly 1.1 million Indians stuck in the employment-based green card backlog, Tuesday's optics are encouraging and the substance is unresolved. The community has finally found its organised voice — 200 delegates is a credible show of force, and the move to encourage diaspora members to seek elected office is the kind of long-game investment that eventually changes outcomes. Representation compounds.

But nobody on an H-1B should plan their next five years around a legislative fix. The structural reality is unchanged: the per-country cap remains law, retrogression is worsening, and the political center of gravity in Washington is tilted toward enforcement, not expansion. The advocacy is necessary precisely because it is not yet sufficient.

The more actionable takeaway is the one Krishnamoorthi pressed hardest. A community that contributes across technology, medicine, academia and small business but lacks proportional political representation will keep getting speeches instead of statutes. The diaspora's clout in Silicon Valley and on hospital wards has not translated into clout in committee rooms. Capitol Hill Day is a down payment on changing that — but the bill for the green card backlog is still coming due, and it will not be paid by a single day of meetings, however large.

For now, the practical advice for an Indian professional watching from an H-1B is unromantic: keep building your own immigration options, support the advocacy, and treat any promised legislative relief as a bonus rather than a plan."""

article2_body = """Buried beneath the headline-grabbing 75% hike in citizenship fees is a quieter proposal that may hit Indian families harder where it actually hurts: the price of fighting back. The Trump administration has moved to triple — and in some cases multiply ninefold — the fees charged for filing motions and appeals in the nation's immigration courts.

The numbers are stark. The form to appeal an immigration judge's decision to the Board of Immigration Appeals currently costs $110. Under the proposed rule from the Justice Department's Executive Office for Immigration Review (EOIR), that jumps to $975 — an increase of nearly 800%. Forms for applicants seeking cancellation of removal would climb from $100 to more than $300. The rule is scheduled for publication in the Federal Register and will take effect only after a public comment period, but the direction of travel is unmistakable.

## A tax on due process

EOIR's stated rationale is mundane: the fees "have remained static, not accounting for inflation or any other intervening changes" in processing costs. That is technically true — many of these fees had not moved in years. But inflation does not explain an 800% jump, and the timing places the increase within a broader pattern. Last November the administration proposed charging for asylum applications for the first time in US history, alongside an 83% increase in the naturalization fee. In October it imposed a $1,000 parole fee. The N-400 citizenship fee hike to as much as $1,330 landed just last week.

Taken together, these are not isolated accounting adjustments. They function as a cumulative toll on every stage of the immigration process — and the appeals-fee increase specifically raises the cost of contesting a government decision. Immigration advocates have been blunt: higher filing fees will deter immigrants from appealing deportation orders, even meritorious ones. A fee waiver exists in some cases, but navigating it adds another layer of friction for people already under pressure.

## Where Indians fit in

It is tempting to assume immigration-court fights are someone else's problem — the preserve of asylum seekers and those in removal proceedings, not the H-1B engineer or the EB-2 doctor. That assumption is increasingly wrong.

Indians are now the largest group of irregular migrants reaching the US from outside the Western Hemisphere, and a growing number find themselves in removal proceedings. But the exposure runs further up the income ladder than most diaspora families realise. As enforcement intensifies, lawful immigrants are being swept into court too: green card holders flagged at the border over old charges, students who fell out of status during a paperwork gap, workers whose change-of-status applications were denied and who must now contest the finding. When the government says no, the immigration court is often the only venue to say "wait."

A $975 appeal fee changes the calculus for exactly those people. For a family already paying $1,330 to naturalize, premium-processing surcharges, and attorney fees that routinely run into five figures, the appeals toll is one more reason to give up rather than fight a questionable decision. That is, critics argue, precisely the point: deterrence dressed as cost recovery.

## The bigger pattern

What makes this proposal worth watching is not its size alone but its placement in a system being re-engineered fee by fee. Each individual increase is defensible on its own narrow terms — agencies should recover costs, fees should track inflation. But the aggregate effect is a structure in which every door now has a turnstile, and the turnstiles are getting more expensive at the same time the rules behind them are tightening.

For the Indian diaspora, the lesson is procedural rather than dramatic. The community's immigration strategy has long focused on the front end — winning the lottery, clearing the backlog, securing the stamp. The fee changes are a reminder that the back end matters too: the ability to contest a denial, appeal an adverse ruling, or buy time when something goes wrong is now materially more expensive.

The proposed rule faces a public comment period before it can be finalized, and that window is the moment for affected communities and advocacy groups to weigh in. For now, the practical takeaway is to treat any immigration filing — even a routine one — as higher-stakes than before. The cost of getting it wrong, and then trying to fix it, has just gone up."""

article3_body = """For a decade, the standard advice to an ambitious Indian professional in America was simple: win the H-1B lottery, get your employer to file a green card, and settle in for a wait measured in decades. The H-1B was the front door. In 2026, a growing number of Indians are deciding the front door is jammed — and reaching for a side entrance marked "extraordinary ability."

The logic is being forced by a brutal pile-up of bad news. The H-1B lottery is a coin flip at best. A proposed $100,000 fee, currently blocked in court but very much alive on appeal, threatens to price out all but the most senior candidates. A new wage-weighted selection rule, effective for the FY2027 cap season, stacks the odds against entry-level applicants. And the EB-2 India green card category just went "unavailable" in the July visa bulletin — the worst word in the system. For Indians born under the per-country cap, the conventional employment-based path now stretches well past the horizon.

## The extraordinary-ability pivot

Enter the EB-1A and O-1 visas, twin categories built for people of "extraordinary ability." Immigration attorneys report a marked rise in Indian professionals — particularly in AI, machine learning, data science and the biosciences — exploring these routes as the H-1B environment sours.

Their appeal is structural. The O-1 nonimmigrant visa has no annual cap and no lottery; it can be issued quickly and renewed indefinitely. The EB-1A immigrant visa is even more powerful: it leads directly to a green card, requires no labor certification, and — crucially — needs no employer sponsorship. An applicant can self-petition. For an Indian worker who has spent years tethered to a single sponsoring employer, the prospect of controlling one's own immigration destiny is the whole point.

There is a further, technical sweetener that sophisticated applicants prize. The EB-1A green card backlog for India, while real, is dramatically shorter than EB-2 or EB-3 — often two to three years rather than a decade-plus. And an applicant who already holds an approved EB-2 I-140 can "port" that earlier priority date to an EB-1A petition, keeping their place in line while upgrading to the faster category.

## The catch: the bar is genuinely high

None of this is a loophole, and the pivot comes with a sharp caveat. "Extraordinary ability" is not a marketing phrase; it is a legal standard that requires demonstrating sustained national or international acclaim and a position among the small percentage at the very top of one's field. Meeting three of the ten EB-1A criteria gets an applicant in the door, but USCIS applies a "final merits determination" that trips up many otherwise strong candidates. A capable mid-career engineer with solid work and a few publications is not, in the agency's eyes, automatically extraordinary.

The practical playbook attorneys describe is therefore a multi-year, multi-layer one: file EB-2 NIW first to lock in a priority date and, with an approved I-140, extend H-1B status indefinitely under the AC21 provisions; build the record — citations, judging, original contributions, media coverage — that an EB-1A demands; use an O-1A as a bridge for immediate work authorization while the EB-1A is pending. It is less a single visa than a portfolio strategy, and it rewards deliberate career-building over years.

## Why this matters to Indian Americans

For the diaspora, the extraordinary-ability pivot is both an opportunity and a sorting mechanism. The opportunity is real: thousands of Indian professionals genuinely qualify and have simply never been told the H-1B was not their only path. For an AI researcher with a strong publication record or a founder with demonstrable impact, the O-1/EB-1A route can shave a decade off the green card timeline and sever the dependence on a single employer that makes a layoff feel like deportation.

The sorting is the uncomfortable part. As the H-1B narrows, the immigration system increasingly rewards those who can document elite achievement — and leaves the competent-but-ordinary majority with fewer options. The Indian engineer doing solid, unglamorous work at a mid-tier firm is exactly the profile the new rules squeeze hardest.

The honest advice for 2026 is to stop treating the H-1B as the default and start treating immigration as a strategy. For those with the record to support it, the extraordinary-ability path is no longer exotic — it is becoming the smart play. For everyone else, the message is to start building that record now, because the front door is only getting narrower."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "200 Delegates, Five Asks, One Old Problem: Inside the Diaspora's Biggest Capitol Hill Push",
        "subheadline": "Indian Americans staged their largest-ever advocacy day on June 23 — but the green card backlog they came to fight is still stuck in the same place it was last year.",
        "slug": make_slug("fiids-capitol-hill-day-200-delegates-green-card-backlog-cap"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the 1.1 million Indians trapped in the employment-based green card backlog, the FIIDS Capitol Hill Day shows the community finally finding an organised voice — but no Indian on an H-1B should plan their future around a legislative fix that the votes don't yet exist to pass.",
        "tags": ["green-card", "h1b", "fiids", "capitol-hill", "country-cap", "backlog", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Nation Press — Indian Americans descend on Capitol Hill", "url": "https://www.nationpress.com/"},
            {"name": "The Hindu BusinessLine — Indian-American lawmakers urge diaspora to enter politics", "url": "https://www.thehindubusinessline.com/"},
            {"name": "LatestLY/PTI — FIIDS Holds Advocacy Day on Immigration Reforms, US-India Ties", "url": "https://www.latestly.com/"},
            {"name": "hi INDiA/IANS — Capitol Hill backs stronger India-US partnership", "url": "https://www.hiindia.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Raja_Krishnamoorthi_official_photo.jpg",
        "image_caption": "Congressman Raja Krishnamoorthi, who has introduced green card backlog-reduction legislation, addressed the FIIDS Capitol Hill gathering",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forget the Citizenship Fee. The Cost of Appealing a Deportation Is About to Jump 800%",
        "subheadline": "A quieter Justice Department proposal would triple — and in places multiply ninefold — the fees to file motions and appeals in immigration court, raising the price of fighting a government 'no.'",
        "slug": make_slug("eoir-immigration-court-appeal-fees-triple-800-percent-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are now the largest group of irregular migrants from outside the Western Hemisphere, and lawful immigrants — green card holders flagged at the border, students with status gaps, workers with denied filings — are increasingly swept into removal proceedings where a $975 appeal fee changes whether a questionable decision gets contested at all.",
        "tags": ["immigration-court", "eoir", "appeals", "fees", "deportation", "due-process", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NBC Palm Springs/CNN — Trump administration looks to triple fees for some immigration court filings", "url": "https://nbcpalmsprings.com/"},
            {"name": "Bloomberg Law — Trump DHS Proposal Would Hike Naturalization Fees", "url": "https://news.bloomberglaw.com/"},
            {"name": "The Travel — US to make obtaining American passports more expensive for certain applicants", "url": "https://www.thetravel.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11505601/pexels-photo-11505601.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A judge's gavel resting on US currency, symbolising the rising cost of contesting immigration decisions",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "With the H-1B Door Jammed, Indians Are Quietly Reaching for the 'Extraordinary Ability' Side Entrance",
        "subheadline": "As the lottery, the $100,000 fee and an 'unavailable' EB-2 India category close off the conventional path, the EB-1A and O-1 visas are moving from exotic to mainstream — for those who can clear a genuinely high bar.",
        "slug": make_slug("eb1a-o1-extraordinary-ability-pivot-indians-h1b-alternative"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian professionals in AI, data science and the biosciences staring down a decade-plus EB-2 wait, the self-petition EB-1A and uncapped O-1 can sever the dependence on a single employer and shave years off the green card timeline — but the 'extraordinary ability' standard sorts the elite from the merely competent.",
        "tags": ["eb1a", "o1-visa", "niw", "green-card", "h1b-alternative", "extraordinary-ability", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Tighter student visa rules may impact Indians in US", "url": "https://theindianeye.com/"},
            {"name": "Colombo Hurd Law — The Strategic Path to Green Cards for Indian Professionals", "url": "https://colombohurdlaw.com/"},
            {"name": "Lexology — New Wage-Weighted H-1B Cap Selection Process Effective Feb 27, 2026", "url": "https://www.lexology.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37839843/pexels-photo-37839843.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A scientist at work in a research laboratory, the kind of profile that can qualify for EB-1A and O-1 extraordinary-ability visas",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article3_body
    }
]

# word count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"[wc] {art['slug']}: {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
