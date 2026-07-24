#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

body1 = """The fight over the H-1B visa has played out this year mostly in the courts and the rule-making file. A Boston judge struck down the $100,000 petition fee in June; the administration is appealing; USCIS keeps rewriting the fine print on who gets selected and how cleanly they must file. But the quieter front is on Capitol Hill, where a growing bloc of lawmakers is trying to rewrite the program itself — not tweak it, but cap it, pause it, or in places dismantle it.

The most aggressive of the lot is the End H-1B Visa Abuse Act of 2026, introduced by Representative Eli Crane of Arizona with seven Republican cosponsors. It would pause all H-1B issuance for three years, and when the program resumed it would look almost unrecognizable.

## What the Crane bill would do

The bill is a maximalist wish list for restrictionists. It would:

- Cut the annual cap from 65,000 to 25,000 and scrap existing exemptions
- Replace the lottery with a wage-based ranking
- Set a **minimum H-1B salary of $200,000 a year**
- Require employers to certify they could not find a qualified American and have conducted no recent layoffs
- Bar third-party staffing firms from employing H-1B workers at all
- Forbid H-1B holders from bringing dependents to the United States
- End Optional Practical Training, the post-study work window for foreign graduates
- Prohibit H-1B workers from ever adjusting to permanent residency, locking the visa as a strictly temporary status

Read together, those provisions would not so much reform the H-1B as end it as a path most Indians actually use. A $200,000 floor prices out the early-career engineer. A ban on dependents fractures families. Cutting OPT severs the F-1-to-H-1B pipeline that funnels Indian students into the workforce. And barring adjustment of status would slam shut the green-card on-ramp that is the entire reason many take the visa in the first place.

## It is not one bill, it is a pattern

Crane's measure is the loudest, but it is not alone. Since January, at least a dozen Republican lawmakers have backed four separate bills aimed at restricting, suspending, or eliminating the program. In June, Representative Chip Roy of Texas floated a package of seven reforms that would cut the maximum H-1B stay from six years to two and require workers to prove they intend to go home — a direct attack on the dual-intent principle that lets H-1B holders pursue a green card.

On the Senate side, the politics are more bipartisan and therefore more durable. Judiciary Chairman Chuck Grassley and Ranking Member Dick Durbin have reintroduced their H-1B and L-1 Visa Reform Act, a perennial effort dating to 2007, with cosponsors spanning Tommy Tuberville, Richard Blumenthal, and Bernie Sanders. The same senators sent letters to Amazon, Google, Meta, and seven other large employers demanding to know why they file thousands of visa petitions while laying off American staff.

## Why Indians should care more than the headlines suggest

None of these bills has moved past introduction. Most will die in committee, as restrictionist H-1B bills usually do. The instinct, then, is to wave them away as noise.

That would be a mistake, for two reasons. First, a court can strike down a fee, but it cannot strike down a statute. The $100,000 fee fell because a judge decided the president lacked the authority to impose it by proclamation. If Congress writes the same restrictions into law, no court saves you. Legislation is the one track that outlasts the litigation.

Second, the center of gravity has shifted. When restriction draws cosponsors from Sanders on the left to Crane on the right, it is no longer a fringe position — it is the new baseline of the debate. Indians hold close to 70% of H-1B approvals, so any of these provisions, even diluted in negotiation, lands on the diaspora first. A family budgeting around a spouse's H-4 work permit, a graduate counting on OPT, an engineer assuming the visa leads to a green card: each of those assumptions is now a line item in a bill someone has filed.

The smart move is not panic but attention. Watch which provisions get attached to must-pass legislation, where the bipartisan Grassley-Durbin language travels, and whether any of it survives a markup. The courts have bought Indian H-1B holders some time. Congress is deciding what comes after."""

body2 = """For Indian professionals on H and L visas, the hardest part of working in America right now is not getting approved. It is getting a stamp in a passport — and the workaround that used to rescue people in a hurry is quietly disappearing.

U.S. consulates across India are buried. Foreign nationals seeking employment-based nonimmigrant visas — the H, L, O and similar petition-based categories — are facing waits of 75 to more than 125 days to secure an appointment in Chennai, Hyderabad, Kolkata, Mumbai and New Delhi, according to immigration firm Fragomen. Demand has climbed for months, but consular staffing at the U.S. mission to India has not, and the queue has stretched accordingly.

## The escape hatch is closing

For years, the standard advice to an Indian visa holder stuck in a long domestic queue was simple: go somewhere else. Apply as a third-country national — a TCN — at a U.S. consulate in a nearby country with shorter waits, get the stamp, and fly back. Kolkata itself used to be the domestic shortcut, with an appointment backlog of just 13 days.

Both routes have now collapsed. Kolkata's wait has ballooned to roughly 126 days. And consulates outside India that once absorbed TCN applicants are restricting the practice, especially over the busy summer months, when posts prioritize their own residents. Canada, a popular TCN destination for Indians, sharply limits third-country processing during peak periods. The relief valve that let a worker dodge a five-month wait at home is, for many, no longer there.

## Why this is more dangerous than a slow line

A long appointment wait is an inconvenience. A long appointment wait combined with no alternative is a trap — and the trap has teeth specific to work-visa holders.

Consider the mechanics. An H-1B engineer in the United States whose visa stamp has expired can keep working as long as they stay put; the stamp is only needed to re-enter the country. But the moment they travel to India — for a wedding, a sick parent, a delayed green-card interview — they cannot return without a fresh stamp. If the appointment is 125 days out and the TCN option is shut, that person is stranded abroad for four months or more, away from their job, their home, and often their family.

That is not hypothetical. Indian H-1B workers stranded by visa delays have already become a tax headache for their own employers, who risk creating an unintended "permanent establishment" in India when a key worker is forced to do their U.S. job from Bengaluru for months. What began as a personal disruption metastasizes into a corporate compliance problem.

## The premium lane that skips work visas

There is a new fast-track on offer, but it is not for the people in this story. From July 1 to December 31, 2026, the State Department is running a pilot that lets applicants pay an extra $750, on top of the standard $185 fee, for an interview appointment within 10 business days at select posts including in India.

The catch, buried in the fine print, is that the expedite pilot applies to B-1 and B-2 visitor visas — business and tourism — not to H, L or other employment categories. So a tourist can pay to skip the line, while the H-1B engineer who actually keeps a U.S. company running cannot buy their way out of the 125-day wait. For the diaspora, it is a galling inversion: the visa that matters most to careers and families is the one with no premium lane.

## What to do about it

The practical advice from immigration lawyers has hardened into a single rule: if your visa stamp is expired or expiring and you are on an H or L, do not leave the United States unless you absolutely must. If travel is unavoidable, book the consular appointment before you book the flight, build in a months-long buffer, and check whether a genuine TCN slot exists in a third country before assuming one will.

The deeper point is structural. The backlog is a staffing problem the U.S. has chosen not to fix even as it markets a $750 line-skip to tourists. Until consular capacity in India catches up with demand, the country that supplies the largest share of America's skilled-visa workforce will keep watching its professionals get stuck at the door — and the door they could once slip through quietly is being bolted shut."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Forget the Courts. The Real Threat to the H-1B Is the Bill Pile Building in Congress",
        "subheadline": "A judge can strike down a fee, but not a statute. A dozen lawmakers are now pushing four bills to cap, pause or gut the visa Indians depend on most.",
        "slug": make_slug("h1b-congress-bills-crane-end-abuse-act-grassley-durbin-legislation-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold nearly 70% of H-1B approvals, so legislation that caps the visa, ends OPT, bars dependents or blocks the green-card path would land on the diaspora first — and unlike the struck-down $100,000 fee, a law cannot be undone by a court.",
        "tags": ["h1b", "congress", "legislation", "immigration", "opt", "green-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Rep. Eli Crane — End H-1B Visa Abuse Act of 2026", "url": "https://crane.house.gov/"},
            {"name": "Mint — US lawmakers intensify push against H-1B visas", "url": "https://www.livemint.com/companies/news/us-lawmakers-intensify-push-against-h-1b-visas-is-2026-its-death-knell"},
            {"name": "Senate Judiciary Committee — Grassley, Durbin H-1B and L-1 Visa Reform Act", "url": "https://www.judiciary.senate.gov/"},
            {"name": "Congress.gov — S.2928 H-1B and L-1 Visa Reform Act of 2025", "url": "https://www.congress.gov/bill/119th-congress/senate-bill/2928"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
        "image_caption": "The United States Capitol at dusk, where multiple bills targeting the H-1B visa program have been introduced.",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An H-1B Stamp in India Now Takes Four Months. The Escape Route Just Got Bolted Shut",
        "subheadline": "Work-visa appointment waits have hit 125 days across Indian consulates, and the third-country shortcut that used to rescue stranded professionals is disappearing.",
        "slug": make_slug("us-visa-stamping-india-tcn-third-country-backlog-h1b-l1-stranded"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "An Indian H-1B or L-1 worker who travels home and cannot get a visa stamp can be stranded abroad for months, away from job and family — and the third-country workaround that once cut the wait is now closing for most of the diaspora.",
        "tags": ["h1b", "l1", "visa-stamping", "consulate", "india", "third-country-national"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Update on Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/visa-appointment-backlogs-us-consulates-india.html"},
            {"name": "U.S. Department of State — Global Visa Wait Times", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"},
            {"name": "Travel And Tour World — Lengthy US Visa Wait Times Stretch Beyond a Year", "url": "https://www.travelandtourworld.com/"},
            {"name": "Outlook Traveller — US to offer faster visa appointments for an additional fee", "url": "https://www.outlooktraveller.com/"}
        ]),
        "score_total": 79,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport with U.S. visa documentation; appointment waits for work visas in India have stretched past four months.",
        "image_attribution": "Pexels",
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
