#!/usr/bin/env python3
"""Immigration writer — 2026-07-10 13:00 PDT run. Three articles."""

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

# ──────────────────────────────────────────────
# ARTICLE 1: Asha Sharma / Xbox / Fed appointment
# ──────────────────────────────────────────────

art1_body = """Xbox CEO Asha Sharma laid off 1,600 employees this week. On Thursday, the Federal Reserve appointed her to an advisory task force on productivity and jobs. The juxtaposition was too much for the internet to handle.

Sharma, who was born in Wisconsin to parents of Indian heritage, has become the unlikely focal point of a national fury that has fused corporate layoffs, H-1B visa politics, and anti-Indian racism into a single, combustible news cycle.

## The Numbers That Lit the Fuse

Microsoft announced it would cut 4,800 positions across the company. Within Xbox, Sharma's division, 1,600 roles were eliminated. In a memo obtained by the Associated Press, Sharma described the division's finances bluntly: "Our business today is not healthy. We are operating at margins that are 3-10x lower than comparable platform and publishing businesses."

At the same time, data from U.S. Citizenship and Immigration Services showed that Microsoft had been approved to hire 2,273 foreign workers on H-1B visas earlier this year. The optics — thousands fired, thousands of visa workers approved — provided ammunition to critics who have long argued the program displaces American workers.

"Every single employer is exploiting the H-1B visa program," said the Project for Immigration Reform.

Rep. Riley Moore, R-W.Va., called for the program's outright elimination. "This is INSANE. LEGAL immigration is a major problem," Moore wrote. "It's long past time to end the H-1B scam."

Microsoft pushed back. "These decisions are based on business need, not visa status," a spokesperson told Fox News Digital. "H-1B employees were also impacted by job eliminations in the U.S."

## Then Came the Fed Appointment

On the same day the backlash crested, the Federal Reserve announced Sharma's appointment to a newly created task force on "Productivity and Jobs," alongside Andreessen Horowitz co-founder Marc Andreessen and Stanford economist Charles I. Jones. New Fed Chairman Kevin Warsh framed the appointments as part of a push to "sharpen our performance as an institution."

The timing was gasoline on an open flame.

"It's like asking El Chapo to lead the DEA," one critic wrote on X. Another called it "totally unexplainable." A third accused the Fed of trying to "incentivize" the mass layoff of American workers.

## The Racial Dimension

What makes this story especially raw for Indian Americans is how quickly the criticism turned explicitly racial. Sharma was born in Wisconsin — she is American — yet critics on social media seized on her Indian heritage as the explanation for the layoffs.

"Her one function is to purge white Americans and replace them with Indian cheap foreign labor," one X user wrote, in a post that circulated widely.

This is not a fringe sentiment. According to the 2026 Indian American Attitudes Survey conducted by the Carnegie Endowment for International Peace, 48 percent of Indian Americans report encountering racist posts targeting their community "very or somewhat often" on social media since early 2025. One in four has been called a slur.

The attacks on Sharma illustrate the bind that Indian-American executives face: business decisions made for financial reasons are reframed through a racial lens, and the H-1B program — which draws 73 percent of its workers from India, according to Pew Research — becomes the connective tissue.

## Vance Adds Fuel

The same week, Vice President JD Vance announced that the Department of Labor had launched "dozens of subpoenas and investigations into foreign fraudsters who are trying to take advantage of the H-1B visa program."

"American jobs ought to go to American workers and not foreign fraudsters," Vance said at a press conference in Milwaukee.

The probe is legitimate and targets real abuse. But its timing, alongside the Xbox layoffs and the Fed appointment, has created a political environment where Indian professionals — including those born and raised in the United States — feel the crosshairs tightening.

## What This Means for the Diaspora

For the roughly 5.2 million Indian Americans in the United States, the Sharma episode is a case study in how quickly professional achievement can be weaponized. A CEO running a division at subpar margins makes a restructuring decision and is recast as an agent of foreign labor replacement — not because of her policies, but because of her last name.

The Federal Reserve appointment, whatever its merits, has become a proxy for a deeper argument about who belongs in American leadership. That argument is no longer just about visas. It is about identity.

And for the thousands of Indian H-1B workers at Microsoft and elsewhere who are now watching the 60-day clock tick after their own layoffs, the message is grimly clear: the system they navigated with care is under attack from every direction — the administration, the legislature, and the public square."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "She Was Born in Wisconsin. The Internet Blamed Her Indian Heritage for Xbox's Layoffs",
    "subheadline": "Xbox CEO Asha Sharma cut 1,600 jobs, got appointed to a Federal Reserve task force, and became the latest Indian-American executive to face racially charged fury over the H-1B program.",
    "slug": make_slug("asha-sharma-xbox-layoffs-fed-appointment-anti-indian-backlash"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian-American corporate leaders are being racially targeted for business decisions, with the H-1B program used as a cudgel against professionals who are American-born citizens.",
    "tags": ["h1b", "microsoft", "xbox", "asha-sharma", "federal-reserve", "anti-indian", "racism", "layoffs"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox News", "url": "https://foxnews.com/politics/ceo-under-fire-mass-layoffs-amid-foreign-worker-hiring-spree-now-appointed-feds-task-force-jobs"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/10/us-news/fury-erupts-as-us-brand-fires-1600-employees-after-securing-thousands-of-foreign-worker-visas/"},
        {"name": "Carnegie Endowment IAAS 2026", "url": "https://carnegieendowment.org/russia-eurasia/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg/1280px-Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg",
    "image_caption": "Aerial view of Microsoft's Redmond campus, where the company announced 4,800 layoffs this week",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 2: Carnegie IAAS 2026 Survey
# ──────────────────────────────────────────────

art2_body = """Half of Indian Americans say they have been personally discriminated against in the past year. One in four has been called a slur. Nearly a third have stopped talking about politics online for fear of being targeted.

These are not anecdotes. They are findings from the 2026 Indian American Attitudes Survey, a nationally representative study of 1,000 Indian American adults conducted by the Carnegie Endowment for International Peace in partnership with YouGov. Published earlier this year, the survey captures a community that is economically successful, politically engaged, and increasingly afraid.

## The Scope of the Problem

The numbers are stark and have remained stubbornly consistent. In 2020, 2024, and 2026, roughly half of Indian Americans reported personal experiences with discrimination — the share has barely moved across three survey waves.

What has changed is the texture. Skin color is the most frequently cited reason for discrimination (36 percent of those who report it), followed by country of origin (21 percent) and religion (17 percent). Stores and malls are the most common setting (42 percent), followed by job applications (38 percent) and cultural or religious activities (31 percent).

Online, the picture is worse. Forty-eight percent of respondents say they encounter racist posts targeting Indian Americans "very or somewhat often" on social media. The survey showed respondents an actual anti-Indian tweet from X and asked how frequently they see content like it. Nearly half said: regularly.

The emotional toll is measurable. Half of those who see such content say it makes them angry. A third feel anxious. Thirty-one percent feel fearful.

## Changing Behavior, Not Changing Countries

What makes these findings particularly significant is not just the prevalence of discrimination but how it is reshaping daily life.

Nearly one-third of Indian Americans (31 percent) say they now avoid discussing or engaging with politics on social media — the single most common behavioral change. Twenty-one percent avoid leaving and re-entering the United States. The same share avoid displaying political signs or bumper stickers. Nineteen percent have stopped wearing Indian dress or attire in public.

This is not flight. It is withdrawal. Indian Americans are not leaving the country — only 14 percent say they frequently think about it — but they are pulling back from public life. They are editing themselves.

Those who do consider leaving cite frustration with U.S. politics (58 percent), cost of living (54 percent), and personal safety (41 percent). Strikingly, most do not envision returning to India. Sixty-two percent of those who have thought about leaving would choose a third country. India is the preferred destination for only one in four.

## Immigration Policy: The Sharpest Edge

The survey reveals that immigration is the policy area where Indian Americans feel most directly targeted. Sixty-four percent disapprove of Trump's immigration policies, with the H-1B visa program's $100,000 fee drawing opposition from two-thirds of respondents.

Even among Indian-American Republicans — who broadly support Trump's immigration stance at 76 percent — support cracks when specific policies are examined. Republican respondents narrowly support the H-1B fee, but they split almost evenly on ending birthright citizenship.

The most opposed policy, across party lines, is the deportation of immigrants to third countries, which 74 percent of all respondents reject.

Immigration ranks as the fourth most important policy issue for Indian Americans (11 percent cite it as their top concern), behind inflation (21 percent), jobs (17 percent), and healthcare (13 percent). But it occupies a unique psychological space: it is the issue most directly connected to their presence in the country.

## A Community Between Parties

Politically, the survey paints a picture of a community drifting from its Democratic anchor without finding a Republican home.

Democrats remain the plurality at 46 percent, down from 52 percent in 2020. Republicans have grown modestly to 19 percent. But the fastest-growing group is independents, now at 29 percent — up six points since 2020. Indian Americans are not switching parties so much as they are becoming unmoored from both.

Seventy-one percent disapprove of Trump's overall job performance. Yet the Democratic Party's favorability among Indian Americans has also declined, from a rating of 60 in 2024 to 53 in 2026. Kamala Harris dropped from 62 to 52. Neither party is gaining ground; both are losing it.

The community's ideological center is moderate. Thirty-two percent identify as such, the largest single group — a four-point increase since 2024.

## What This Survey Gets Right

The IAAS is one of the few rigorous, recurring studies of Indian American political life. Its methodology — nationally representative, weighted, with a 3.6 percent margin of error — gives it a credibility that social media anecdotes cannot match.

Its central finding is simple and uncomfortable: Indian Americans are among the most educationally and economically successful groups in the country, and half of them experience discrimination regularly. They are not leaving, but they are shrinking — the space they occupy in public life, the things they say, the clothes they wear.

For a diaspora that has staked its American story on achievement and assimilation, the survey suggests the bargain is fraying."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Half of Indian Americans Report Discrimination. The Data Shows They Are Quietly Retreating",
    "subheadline": "A major Carnegie Endowment survey finds one in four Indian Americans has been called a slur since 2025, and nearly a third have stopped engaging with politics online out of fear.",
    "slug": make_slug("carnegie-iaas-2026-indian-americans-discrimination-survey"),
    "category": "immigration",
    "vertical": "diaspora-identity",
    "diaspora_angle": "This is the most comprehensive survey of Indian American political attitudes and discrimination experiences, with direct implications for how the diaspora navigates life in today's political climate.",
    "tags": ["indian-americans", "discrimination", "carnegie", "survey", "diaspora", "racism", "identity", "politics"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/russia-eurasia/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "YouGov", "url": "https://today.yougov.com/"},
        {"name": "Stop AAPI Hate", "url": "https://stopaapihate.org/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7581120/pexels-photo-7581120.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A diverse group of professionals in a modern office setting",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 3: DOL Prevailing Wage Increase
# ──────────────────────────────────────────────

art3_body = """The Department of Labor wants to nearly double the minimum salary threshold for entry-level H-1B workers. If finalized, it would be the most consequential change to employment-based immigration wage rules in more than twenty years — and Indian professionals would bear the brunt.

## What the DOL Proposed

On March 26, the DOL published a Notice of Proposed Rulemaking that would overhaul how prevailing wages are calculated for the H-1B, H-1B1, E-3, and PERM visa programs. The rule keeps the familiar four-tier wage structure that has been in place since 2005 but pushes every tier dramatically higher on the national wage distribution.

The shift looks like this:

- **Level I (Entry)**: From the 17th percentile to the 34th percentile
- **Level II (Qualified)**: From the 34th percentile to the 52nd percentile
- **Level III (Experienced)**: From the 50th percentile to the 70th percentile
- **Level IV (Fully Competent)**: From the 67th percentile to the 88th percentile

In plain terms: the DOL is arguing that the current wage floors are set "dramatically below the market rates which many American workers receive, particularly entry-level Americans and recent college graduates in science, technology, engineering, and math fields."

For a software developer in a mid-tier metro area currently classified at Level I, the required salary could jump by 30 percent or more. At Level IV, the threshold moves into the top 12 percent of the national wage distribution for the occupation — territory that many mid-career professionals do not reach.

## Why This Matters More Than the $100,000 Fee

The $100,000 H-1B application fee, struck down by a federal judge in June and currently under appeal, grabbed the headlines. But the prevailing wage proposal may prove more consequential. Here is why.

The fee was a one-time cost for the employer. The wage rule changes the ongoing cost of every H-1B employee, every year, for the duration of their employment. It also applies to PERM labor certifications — the first step in most EB-2 and EB-3 green card applications. That means it does not just affect new hires. It reprices the entire pipeline of Indians waiting for employer-sponsored green cards.

According to Economic Policy Institute data cited by the DOL, roughly 60 percent of H-1B positions certified by the agency were assigned wage levels below the national median for the occupation. The proposed rule would push Level II to the 52nd percentile — right at the median — making it mathematically impossible for the majority of current H-1B roles to continue at their present wage levels without reclassification.

## The Indian IT Model Under Pressure

Indian IT consulting firms — Infosys, Wipro, TCS, HCL, and others — have historically placed large numbers of H-1B workers at Level I and Level II wages. The business model depends on a wage arbitrage: hire skilled Indian engineers at prevailing-wage minimums that, while legally compliant, are well below what equivalent American workers earn.

The DOL's proposal attacks exactly this leverage point. By raising Level I from the 17th to the 34th percentile, it roughly doubles the minimum wage floor for entry-level H-1B roles compared to what some firms have been paying. Combined with the separate August proposal to tighten third-party client-site placement rules, the consulting-and-placement model that built Indian IT's American footprint is facing a two-front squeeze.

This is not theoretical. The DOL's Inspector General has already launched a sweeping investigation into H-1B fraud, with subpoenas targeting firms that allegedly underreport wage levels. Cognizant — the first named target — was found liable for discrimination against non-Indian employees in a separate federal lawsuit, partly on grounds related to its H-1B hiring practices.

## What Happens Next

The proposed rule is exactly that — a proposal. It must complete a formal notice-and-comment rulemaking process, with comments due 60 days after its Federal Register publication on March 27. It would apply only prospectively to new filings once effective, which immigration attorneys estimate would be late 2026 or early 2027 at the earliest.

But employers are not waiting. According to immigration law firm Berardi, companies planning H-1B or PERM cases "should start modeling the financial impact now." Mintz, another firm, advises clients to audit their current wage classifications against the proposed thresholds and assess whether existing employees would need raises to remain compliant if the rule is finalized.

## The Diaspora Calculus

For Indian professionals in the United States, the wage proposal introduces a new variable into an already unstable equation.

Higher wages are not inherently bad for workers — an Indian engineer paid at the 34th percentile instead of the 17th is, by definition, earning more money. The risk is not lower pay. It is fewer jobs.

If the cost of sponsoring an H-1B worker rises 30 percent at entry level, some employers will decide the math no longer works. They will hire domestically, relocate roles to India or Canada, or restructure positions to avoid the H-1B requirement entirely. For Indians in the green card backlog — some of whom have been waiting decades in the EB-2 and EB-3 queues — a PERM reclassification at a higher wage level could mean their employer reconsiders the sponsorship altogether.

The DOL has framed this as protecting American workers. For Indian professionals, it may end up protecting them out of the country."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Government Wants to Double Entry-Level H-1B Wages. The Math Is About to Break",
    "subheadline": "A proposed DOL rule would push the minimum salary for H-1B workers from the 17th to the 34th percentile — the biggest change to immigration wage rules in two decades, and a direct hit to the Indian IT consulting model.",
    "slug": make_slug("dol-prevailing-wage-increase-h1b-perm-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The proposed wage increase directly reprices the cost of employing Indian H-1B workers and affects PERM green card applications, threatening both new sponsorships and existing backlog cases.",
    "tags": ["h1b", "dol", "prevailing-wage", "perm", "green-card", "indian-it", "wages", "immigration-policy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Berardi Immigration Law", "url": "https://berardiimmigrationlaw.com/new-dol-rule-would-raise-h-1b-wages-to-34th-88th-percentile-what-employers-should-do-now/"},
        {"name": "Mintz", "url": "https://www.mintz.com/insights-center/viewpoints/2806/2026-04-16-department-labor-proposes-rule-increase-wage-levels"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/dol-proposed-rule-prevailing-wages-h1b-perm"},
        {"name": "Fox News", "url": "https://foxnews.com/politics/fury-erupts-us-brand-fires-1600-employees-after-securing-thousands-foreign-worker-visas"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg",
    "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ──────────────────────────────────────────────
# INSERT ALL ARTICLES
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
