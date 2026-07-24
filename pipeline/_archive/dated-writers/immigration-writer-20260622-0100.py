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

body1 = """The Trump administration's most expensive change to the H-1B program may turn out to be the one with no price tag attached. Tucked beneath the headline-grabbing $100,000 petition fee and the wage-weighted lottery is a Department of Labor proposal that would quietly rewrite the arithmetic of hiring a foreign worker — by raising the wage an employer must pay one in the first place.

The proposed rule, published in the Federal Register on March 27 and now working its way through the comment process, overhauls how the DOL calculates the "prevailing wage" — the salary floor beneath every H-1B, H-1B1, E-3 and PERM green-card filing. It does not touch the cap, the fee, or the lottery. It simply moves the floor up, and it moves it a long way.

## What Actually Changes

The current system pegs wages to four tiers drawn from federal occupational survey data. Entry-level Level I sits at the 17th percentile; the top Level IV at the 67th. The proposal lifts every tier: Level I to the 34th percentile, Level II to the 52nd, Level III to the 70th, and Level IV to the 88th.

On paper that is a percentile shuffle. In a paycheck it is real money. The DOL's own analysis estimates the average certified wage would climb roughly $14,000 a year per worker. For specific roles the jump is far steeper. Bloomberg Law, citing the agency's survey data, found an entry-level automotive engineer in Detroit would cost $16,000 more a year, and a Silicon Valley software engineer sponsored through the program would cost about $40,000 more.

The reach is the headline number. The Holland & Knight analysis of the rule notes the DOL estimates more than 75 percent of the labor condition applications certified between fiscal 2020 and 2024 would have fallen below the proposed new floors. In other words, three of every four H-1B-style positions filed in recent years were paid below what the government would now call market rate.

Secretary of Labor Lori Chavez-DeRemer framed it as worker protection. "This proposed rule will help ensure that employers pay foreign workers wages that reflect the real market value of their labor," she said, adding that "the continued abuse of the H-1B program by certain bad actors will no longer be tolerated."

## Why Indians Feel It First

Indians hold roughly 71 percent of approved H-1B petitions, so any change that makes the program costlier lands disproportionately on Indian workers and the companies that sponsor them. But the prevailing-wage rule cuts deeper than the visa itself, because it also governs PERM — the labor-certification step that anchors most employment-based green cards. The DOL itself noted that more than half of fiscal 2024 PERM applications involved workers already in H-1B status.

For an Indian professional that means the higher floor follows them from their first work visa all the way to the green-card queue they may sit in for a decade or more. A worker whose offered salary suddenly looks "below prevailing" could find an extension, an amendment, or a fresh PERM filing harder to clear — not because their pay was cut, but because the benchmark moved.

There is a sliver of timing relief. The rule is not retroactive: approved certifications and labor condition applications already on file are untouched, and lawyers expect the fiscal 2027 H-1B cap petitions due by June 30 to escape it, since their LCAs predate any effective date. The squeeze arrives afterward, on new filings and on extensions built on fresh LCAs.

## The Bigger Pattern

This is the third lever pulled on the same machine in under a year — the $100,000 fee, the wage-weighted selection that favors higher-paid candidates, and now a wage floor that pushes those same salaries up. Each reinforces the others. The clear signal to employers is to reserve the program for senior, highly paid hires and to think hard before sponsoring an entry-level graduate.

Immigration attorneys are blunt about the likely response. Some employers will pay up. Others, as Fragomen's Kevin Miner told Bloomberg Law, face "wage inflation that this would force" and "real money that hasn't been planned for." A few multinationals may simply expand the work offshore — a quiet boost to India's own capability centers, and a slow leak in the pipeline that has carried Indian talent to America for thirty-five years.

The rule still has to survive its comment period and the near-certain court challenge; a similar 2020 effort was blocked and abandoned. For now, the advice from counsel is unglamorous but practical: file extensions early, audit which roles sit at Levels I and II, and watch the Federal Register. The cheapest visa change in this round is the one most worth reading closely."""

body2 = """For most of three decades, the path was simple enough to fit on a napkin: come to America on an F-1 student visa, graduate, work on OPT, win the H-1B lottery, and grind through the green-card queue. Every rung of that ladder is now either more expensive, more crowded, or under review at the same time — and a growing number of Indian professionals are quietly looking for a different ladder altogether.

The pressure is cumulative rather than singular. A $100,000 fee now attaches to many new H-1B petitions. The lottery has been replaced by a wage-weighted selection that hands the highest-paid candidates up to four times the odds, leaving entry-level graduates at the back. The Department of Labor has proposed lifting the prevailing-wage floors that govern both H-1B and green-card filings. And a pending DHS rule would scrap the open-ended "duration of status" for students while halving the post-graduation grace period from 60 days to 30, narrowing the "Day 1 CPT" workaround many Indians lean on after an H-1B miss.

Stacked together, the message to a young Indian engineer is unambiguous: the front door has gotten narrower. So the search has turned to the side doors.

## The O-1 and the Cap-Exempt Route

Two alternatives keep surfacing in lawyers' offices. The first is the O-1 visa, for individuals of "extraordinary ability" — once the preserve of athletes and movie stars, now increasingly pursued by AI researchers, senior engineers and founders who can document awards, publications, patents or press. It has no annual cap and no lottery. It also has a high evidentiary bar and a heavier paperwork burden, which is precisely why it was long ignored.

The second is the cap-exempt H-1B. Petitions filed by universities, nonprofits affiliated with them, and nonprofit or government research organizations sit outside the annual cap entirely — no lottery, no $100,000 fee, and premium processing is available. For an Indian postdoc or a researcher willing to work at or for a qualifying institution, it is a path that the cap chaos simply does not touch.

Danielle Goldman, co-founder of the immigration-tech firm Build, has watched the pivot accelerate. As pathways tighten, she said, companies "will either struggle because they won't have the talent or they will have to get creative and find alternate solutions, including cap-exempt H-1B programmes and O-1 visas for highly accomplished professionals."

## Why It Matters to the Diaspora

For Indian Americans, this is not an abstract reshuffling of visa categories — it is a change in who gets to stay. Indians make up the largest single nationality in nearly every skilled-immigration channel, and they are also the most exposed to the entry-level squeeze, because so many arrive as students and first-time workers rather than as senior hires parachuting in on big salaries.

The alternatives are real but narrow. O-1 rewards the already-accomplished, which does little for a 24-year-old who just finished a master's degree. Cap-exempt H-1B requires the right kind of employer, and academic and nonprofit salaries rarely match Big Tech's. EB-1A, the extraordinary-ability green card some attorneys are steering clients toward, demands an even higher standard than the O-1. None of these is a mass-market substitute for the lottery that once admitted 85,000 people a year.

What the pivot really reveals is a sorting. The system is being retooled to favor the senior, the credentialed and the highly paid, and to discourage the entry-level pipeline that built much of the Indian-American professional class. The students who would have ridden the F-1-to-OPT-to-H-1B escalator now face a choice their predecessors did not: become demonstrably "extraordinary" early, find a cap-exempt employer, or look at Canada, the UK or a job back in India's booming capability centers.

## What to Do Now

Immigration counsel offer a consistent checklist. Anyone with a strong record — publications, patents, leadership, media — should explore O-1 or EB-1A sooner rather than later, because building that evidence takes years. Researchers should weigh cap-exempt employers seriously, even at a pay cut, for the cap-free stability they offer. Students should track the DHS duration-of-status rule closely, since a shorter grace period leaves less room to scramble after a lottery loss.

The escalator that carried a generation of Indians into American careers has not been switched off. But it has been slowed, narrowed and priced — and the people who navigate the next few years best will be the ones who stopped waiting for it and started reading the map for the stairs."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Forget the $100,000 Fee. The Quiet Wage Rule Is the H-1B Change That Follows Indians All the Way to the Green Card",
        "subheadline": "A Labor Department proposal would lift the salary floor on H-1B and PERM filings — and the government's own math says three in four recent positions sit below it.",
        "slug": make_slug("dol-prevailing-wage-rule-h1b-perm-salary-floor-indians-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold about 71% of H-1B petitions and dominate the PERM green-card queue, so a higher prevailing-wage floor raises the bar on their work visas, extensions and permanent-residency filings alike.",
        "tags": ["h1b", "prevailing wage", "perm", "department of labor", "green card", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Department of Labor — Proposed Rule on Prevailing Wage Methodology", "url": "https://www.dol.gov/newsroom/releases"},
            {"name": "Bloomberg Law — H-1B Wage Overhaul Proposal Adds to Sticker Shock for Employers", "url": "https://news.bloomberglaw.com/"},
            {"name": "Holland & Knight — DOL Targets Prevailing Wages: Sweeping Increases Proposed", "url": "https://www.hklaw.com/en/insights"},
            {"name": "SHRM — DOL Proposes Increasing Wage Minimums for H-1B, PERM Programs", "url": "https://www.shrm.org/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg",
        "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "As the H-1B Ladder Narrows, Indians Are Quietly Switching to the Side Doors",
        "subheadline": "With a $100,000 fee, a wage-weighted lottery and tighter student rules stacking up, Indian professionals are turning to O-1 and cap-exempt routes — but the alternatives reward only a few.",
        "slug": make_slug("o1-cap-exempt-h1b-alternative-routes-indians-lottery-squeeze"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest group in nearly every skilled-immigration channel and the most exposed to the entry-level squeeze, so the shift toward O-1 and cap-exempt visas reshapes who in the diaspora gets to stay.",
        "tags": ["h1b", "o-1 visa", "cap-exempt", "opt", "eb-1a", "immigration", "indian students"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE — Tighter student visa rules may impact Indians in US: Expert", "url": "https://theindianeye.com/"},
            {"name": "Fragomen — USCIS Premium Processing for Cap-Exempt H-1B Petitions", "url": "https://www.fragomen.com/insights/"},
            {"name": "USCIS — H-1B Cap-Exempt Petitions Guidance", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32213421/pexels-photo-32213421.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A scientist conducts research in a laboratory; cap-exempt H-1B and O-1 routes increasingly draw researchers and senior specialists.",
        "image_attribution": "Pexels",
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"-- {art['slug']} | {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
