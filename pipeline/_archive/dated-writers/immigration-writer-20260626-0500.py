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

# ---------------------------------------------------------------------------
# ARTICLE 1 — DHS citizenship fee hike
# ---------------------------------------------------------------------------
body1 = """The path to a U.S. passport has always had a price. Under a rule the Department of Homeland Security floated on June 22nd, that price is about to climb by three-quarters — and the discounts that made citizenship reachable for lower-income immigrants would disappear entirely.

The proposal targets Form N-400, the naturalization application, and Form N-336, the form used to appeal a denial. The paper N-400 fee would rise from $760 to $1,330, a 75% increase. File online and it climbs from $710 to $1,280, up 80%. Botch the application and want to appeal? The N-336 paper fee jumps from $830 to $1,475. At the consular exchange rate of roughly ₹96 to the dollar, a paper citizenship application alone would cross ₹1.26 lakh before a single document is notarised.

## Why DHS says it is doing this

The agency's argument is bureaucratic but blunt: the current fees "do not recover the full cost of thoroughly adjudicating applications for naturalization." DHS says expanded screening and vetting — mandated by recent executive orders — costs more, and that applicants, not taxpayers, should foot the bill. In its own words, the department "no longer believes naturalization benefit requests should get lower fees at the potential expense of other immigration benefits."

That is a sharp reversal of decades of policy. Previous administrations of both parties kept naturalization cheap on the theory that turning permanent residents into citizens was a public good worth subsidising. DHS now estimates the increases would raise more than $430 million a year. About a million people apply for citizenship annually.

The detail that worries advocates most is not the headline number — it is the quiet elimination of fee waivers and reduced-fee options for low-income applicants. The only carve-out that survives is for qualifying U.S. military service members. Everyone else pays full freight.

## What it means for Indian Americans

Indians are one of the largest groups in the naturalisation queue, and they sit at the exact pressure point this rule creates. The typical Indian green-card holder is not the struggling applicant the waiver was built for — many are H-1B veterans with comfortable salaries who can absorb a few hundred extra dollars. For them, the fee hike is an irritant, not a wall.

But the picture is not uniform. Indian families often naturalise in clusters — a worker, a spouse who left a career to raise children on an H-4, an ageing parent who became a permanent resident through family sponsorship. Run three or four N-400s through a household at $1,330 each and the bill approaches the cost of a return trip to India. The spouse with no independent income and the retired parent living on savings are precisely the people who would have qualified for a waiver — and precisely the people the new rule cuts off.

There is also a timing calculation. For permanent residents who have been deferring naturalisation — a common pattern among Indians who keep one eye on the option of returning home — the message is to file now. The rule carries a mandatory 60-day public comment period after it is published in the Federal Register, and DHS can revise it before issuing a final version. That window is the cheapest insurance available: an application filed under the current schedule is grandfathered at the current price.

## The bigger pattern

The fee hike does not stand alone. It lands in the same month as a July visa bulletin that made EB-2 India unavailable, a contested $100,000 H-1B fee working its way through the courts, and a proposal to put a four-year clock on student visas. Each measure is defended on its own terms — cost recovery here, national security there — but the cumulative effect is a legal-immigration system that is getting more expensive and less forgiving at every stage, from the F-1 stamp to the oath of allegiance.

For a community that has treated U.S. citizenship as the natural endpoint of a decades-long journey, the proposal reframes the finish line as one more toll booth. It is still passable. It is just no longer cheap, and for the poorest applicants, it may no longer be open at all.

## What to watch

The rule is a proposal, not law. Watch the Federal Register publication date — it starts the 60-day clock — and any signal from immigration groups about a legal challenge to the elimination of fee waivers, which is the provision most vulnerable to litigation. Until a final rule takes effect, today's fees still apply."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — H.R. 9157, Chip Roy's bill
# ---------------------------------------------------------------------------
body2 = """A bill introduced this month would not tweak the H-1B program. It would dismantle the version of it that Indian professionals have spent thirty years building a life around.

H.R. 9157 — the American White-Collar Worker Jobs Act of 2026, introduced by Representative Chip Roy (R-TX) on June 4th — proposes the most sweeping structural overhaul of the visa since its creation in 1990. It is proposed legislation, not enacted law; it has been referred to the House Judiciary Committee with no hearing scheduled and no Senate companion. But its contents are worth reading closely, because they sketch where the restrictionist wing of Congress wants the program to go.

## What the bill would change

Four provisions matter most.

First, it scraps the lottery. Instead of awarding the 65,000 regular-cap and 20,000 master's-cap visas by random draw, H.R. 9157 would rank applicants by wage and hand visas to the highest bidders first.

Second, it raises the floor dramatically. Today's prevailing-wage system runs from Level I (the 17th percentile) to Level IV (the 67th). The bill replaces that with a single floor at the **75th percentile** for the occupation in its local area — or the employer's actual wage for comparable U.S. workers, whichever is higher. A software developer in San Francisco, who today carries a Level I wage near $134,000, would see that floor pushed substantially higher.

Third — and this is the line that should stop every Indian student cold — it abolishes Optional Practical Training and STEM-OPT outright. Those programs let international graduates work for up to three years after finishing a degree. They are the primary bridge from an F-1 student visa to an H-1B. Remove them and a newly minted graduate would have to leave the country the moment the diploma is handed over.

Fourth, it ends dual intent. Under current law an H-1B holder can hold the visa and pursue a green card at the same time. The bill legally severs the two, converting the H-1B into a strictly temporary, non-renewable stay with no built-in path to permanent residence.

## Why this hits Indians hardest

Indian nationals account for roughly 71% of all H-1B approvals. Any change to the program's mechanics lands disproportionately on them, but H.R. 9157's specific design is almost surgically targeted at the Indian career arc.

The classic Indian pathway is: arrive on an F-1, graduate, use OPT/STEM-OPT to gain experience and a sponsor, win the H-1B lottery, then spend years — often more than a decade, given EB-2 India backlogs — converting that into a green card through adjustment of status. H.R. 9157 cuts that chain in three places at once. No OPT means no bridge out of school. The wage-ranked selection favours senior, highly paid workers over entry-level graduates — the very cohort Indians have traditionally entered through. And ending dual intent severs the green-card endgame that justified the whole journey.

A worker on an entry-level salary, fresh out of a master's program, would be close to unselectable under a wage-ranked system. The students hit hardest are not the exceptions — they are the median Indian STEM graduate the program was built to absorb.

## How seriously to take it

Soberly, but not fearfully. As of late June, neither DHS nor USCIS has endorsed or opposed the bill, and the FY 2027 cap season proceeded under existing rules. No hearing is on the calendar. Most bills introduced in any given Congress die in committee, and a measure this disruptive to the tech industry — which lobbies hard on H-1B — faces a steep climb.

The reason to track it anyway is that it reads less like a one-off and more like the statutory completion of executive actions already under way: the September 2025 proclamation that imposed a $100,000 H-1B fee, and the December 2025 move to a wage-weighted selection. H.R. 9157 would make permanent in law what the administration has been trying to do by rule.

## What to do now

For Indians on or near the H-1B track, the practical advice is unchanged but more urgent: workers with pending green-card applications should map contingency plans with an attorney, since the loss of dual intent is the provision that would most directly upend adjustment-of-status filings. Cap-exempt employers — universities, nonprofit research institutes — remain a year-round option outside the lottery. And the O-1 and EB-1A "extraordinary ability" routes, which the bill does not directly touch, are drawing more interest precisely because they sidestep the machinery H.R. 9157 wants to rebuild."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — Global talent competition / rival visas
# ---------------------------------------------------------------------------
body3 = """For three decades the question for an ambitious Indian engineer was simple: how do I get to America? It is becoming a different question — where else will have me? — and a growing list of countries is competing to be the answer.

As Washington layers fee on fee and restriction on restriction, rival economies are doing the opposite: lowering barriers, scrapping employer-sponsorship requirements, and openly courting the STEM talent the United States is making harder to import. The shift is not yet a stampede, but the incentives are moving, and Indians — the world's most mobile pool of skilled migrants — are the prize everyone is chasing.

## Who is recruiting

China has been the loudest. Its new K visa, created under State Council rules in 2025 and legally effective from October 1st, targets young foreign STEM graduates and promises something the H-1B never has: entry, residence and the right to work **without a job offer or a sponsoring employer**. That single feature removes the biggest hurdle Indians face — the need for a company to roll the dice on sponsorship before they can even apply. Beijing's framing has been pointed. After the U.S. unveiled its $100,000 H-1B fee, Chinese officials publicly declared the country "welcomes global talent for technological and economic progress."

China is not alone. Immigration experts note that South Korea, Germany and New Zealand have all loosened skilled-migration rules. Australia reopened its Work and Holiday visa ballot for Indians aged 18 to 30. Germany's opportunity-card scheme and Canada's Express Entry system — long the default Plan B for H-1B Indians — continue to absorb applicants who have given up on the American lottery.

## The reality check

Before anyone books a flight to Shenzhen, the caveats matter. China's K visa, for all its fanfare, has been slow to materialise: months after taking legal effect, implementation guidance was still being finalised and the category was barely visible on official application portals. A sponsorship-free visa on paper is not the same as a functioning pathway in practice, and many Indian professionals remain wary of the political and personal risks of building a career inside China specifically.

The more realistic destinations are the established ones. Canada's proximity, English-language workplaces and clearer permanent-residence math have made it the genuine pressure-release valve — Indians have been quietly redirecting there for years. Europe offers stability but a harder cultural and linguistic on-ramp. The point is not that any single rival has cracked the code; it is that, collectively, the alternatives are now credible enough that "America or bust" is no longer the only rational plan.

## Why this matters for the diaspora

For Indian Americans already settled in the U.S., the talent drift is not an abstraction — it reshapes the community's future. The diaspora has historically renewed itself through a steady inflow of students and workers who became the next generation of founders, doctors and engineers. F-1 visa issuances to Indians collapsed more than 60% in 2025, and Indian student enrolment in the U.S. fell 6.9% year-on-year, the sharpest drop in over a decade. If the brightest Indian graduates increasingly choose Toronto, Berlin or Bangalore over Boston, the pipeline that built Silicon Valley's Indian-American leadership thins.

There is a homeward pull, too. Zoho founder Sridhar Vembu has publicly urged Indian professionals to "come home," and India's own technology sector — flush with capital and global-capability centres — is a more serious option than it was a decade ago. For families weighing whether a child should chase a U.S. degree, the calculus now includes a real chance the American door stays jammed.

## What to watch

Three signals will tell whether the drift becomes a trend. First, whether China's K visa actually starts issuing in volume after October. Second, Canadian and Australian intake numbers for Indian applicants over the next year. And third — the one that matters most — whether U.S. policy stabilises or keeps tightening. Talent follows certainty. Right now, the most certain thing about the American immigration system is that it keeps changing the rules, and every other country bidding for the same engineers knows it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Becoming American Just Got 75% Pricier — and the Discount for the Poor Is Gone",
        "subheadline": "DHS wants to raise the citizenship application fee to $1,330 and scrap fee waivers entirely. For Indian families naturalizing in clusters, the bill is about to add up.",
        "slug": make_slug("dhs-citizenship-n400-fee-hike-1330-waivers-eliminated-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest groups in the U.S. naturalization queue, and families that apply together — worker, H-4 spouse, retired parent — would lose the low-income fee waivers that made citizenship reachable.",
        "tags": ["uscis", "citizenship", "n-400", "naturalization", "dhs", "fees", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/nation/2026/06/24/trump-citizenship-fee-increase/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/us-plans-75-citizenship-fee-hike-indian-green-card-holders-may-face-costs-up-to-rs-1-lakh"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/world/us-citizenship-may-get-costlier-as-dhs-proposes-sharp-fee-hike"},
            {"name": "The Travel", "url": "https://www.thetravel.com/us-government-citizenship-fee-increase-proposal/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854812455082%29.jpg/1280px-2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854812455082%29.jpg",
        "image_caption": "New citizens take the Oath of Allegiance at a 2025 U.S. naturalization ceremony.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A New Bill Would Kill OPT, End Dual Intent, and Auction Off the H-1B by Salary",
        "subheadline": "Chip Roy's H.R. 9157 is the most sweeping rewrite of the H-1B since 1990. It is not law — but it is aimed squarely at the Indian career path.",
        "slug": make_slug("hr-9157-chip-roy-h1b-opt-abolished-dual-intent-wage-ranked-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up 71% of H-1B approvals and follow the exact F-1 to OPT to H-1B to green-card path the bill would sever in three places at once.",
        "tags": ["h1b", "opt", "stem-opt", "dual-intent", "chip-roy", "hr-9157", "legislation", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/h1b/rep-chip-roy-introduces-hr-9157-the-american-white-collar-worker-jobs-act-of-2026/"},
            {"name": "Congress.gov", "url": "https://www.congress.gov/bill/119th-congress/house-bill/9157"},
            {"name": "USCIS H-1B Cap Season", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-workers/h-1b-specialty-occupations-and-fashion-models/h-1b-cap-season"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
        "image_caption": "Representative Chip Roy (R-TX), who introduced H.R. 9157, the American White-Collar Worker Jobs Act of 2026.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Keeps Raising the Drawbridge. The Rest of the World Is Lowering Theirs",
        "subheadline": "As US visa costs climb, China, Germany, Canada and others are courting the Indian STEM talent Washington is making harder to import. The 'America or bust' era is ending.",
        "slug": make_slug("global-talent-competition-china-k-visa-canada-indians-h1b-alternatives"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The Indian-American community renews itself through an inflow of students and workers; if the brightest graduates pick Toronto or Berlin over Boston, the pipeline that built the diaspora's leadership thins.",
        "tags": ["k-visa", "china", "canada", "global-talent", "h1b-alternatives", "f1", "brain-drain", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/chinas-new-k-visa-beckons-foreign-tech-talent-us-hikes-h-1b-fee-2025-09-30/"},
            {"name": "C&EN (American Chemical Society)", "url": "https://cen.acs.org/policy/immigration/Chinas-K-visa-targets-global-STEM-talent/"},
            {"name": "EdSource", "url": "https://edsource.org/updates/u-s-colleges-face-steep-drop-in-international-student-visas"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/indian-student-enrolment-in-us-falls-nearly-7-amid-stricter-visa-rules/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3885535/pexels-photo-3885535.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traveler holds a passport and boarding pass at the airport, as skilled migrants weigh destinations beyond the US.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body3
    }
]

# word-count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  words={wc}  slug={art['slug']}")

print("--- inserting ---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
