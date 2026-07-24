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
        "headline": "The $800,000 Escape Hatch: Why Indians Are Pouring Into the EB-5 Investor Visa",
        "subheadline": "As H-1B costs balloon and the EB-2 queue stretches past 15 years, mid-career Indians are buying their way around the line — but the investor route's safety valve is starting to close too.",
        "slug": make_slug("eb5-investor-visa-india-surge-unreserved-retrogression-escape-hatch"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the Indian professional staring down a 15-year EB-2 wait, the EB-5 investor green card has become the fastest legal way out of visa limbo — but its concurrent-filing advantage may vanish before the fiscal year ends.",
        "tags": ["eb5", "green-card", "investor-visa", "immigration", "backlog"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaVerge — Indian EB-5 Retrogression Warning", "url": "https://www.visaverge.com/news/indian-eb-5-visa-retrogression-warning-may-2026-update/"},
            {"name": "US Immigration Advisor — EB-5 Visa India 2026", "url": "https://www.usimmigrationadvisor.com/eb-5-visa-india/"},
            {"name": "Mondaq — Top 26 EB-5 Insights For Investors In 2026", "url": "https://www.mondaq.com/unitedstates/inward-foreign-investment/top-26-eb-5-insights-for-investors-in-2026"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US passport with hundred-dollar bills, illustrating the EB-5 investment route to permanent residence.",
        "image_attribution": "Pexels",
        "body": """For years, the EB-5 investor visa was the immigration equivalent of flying business class: technically available, vaguely embarrassing to mention, and used mostly by the wealthy who could not be bothered to wait. That reputation is fading fast. A growing number of mid-career Indian professionals — software engineers, doctors, finance executives — are now writing checks of $800,000 or more, not because they are rich hobbyists, but because every other door to a green card has either jammed shut or grown ruinously expensive.

The math is brutally simple. The EB-2 employment-based queue for Indians now stretches past 15 years because of per-country caps that treat a nation of 1.4 billion the same as Iceland. The H-1B has become a gauntlet of weighted lotteries, a now-litigated $100,000 fee on new petitions, and the rollback of the automatic H-4 spouse work-permit extension. For someone who has already burned a decade in temporary status, the EB-5 offers something none of the others can: a path that does not depend on an employer, a lottery, or a wage tier.

## Why the surge is happening now

EB-5 grants permanent residence to foreign nationals who invest $800,000 in a targeted employment area — rural or high-unemployment zones — or $1,050,000 elsewhere, provided the investment creates at least ten American jobs. Indian demand has climbed sharply between fiscal 2023 and 2025, according to immigration attorneys tracking petition volumes, driven almost entirely by the deteriorating outlook in the H-1B and EB-2 lanes.

The appeal for Indians who are already in the United States is a feature called concurrent filing. Eligible investors can file Form I-526E (the investment petition) and Form I-485 (adjustment of status) at the same time, which lets them apply for interim work and travel permits while their case is pending. For a family that has spent years tethered to a single employer's sponsorship, that independence is worth more than the money.

## The window is narrowing

Here is the catch, and it is a significant one. The State Department warned in the May 2026 Visa Bulletin that "sufficient demand and increased use by India in the EB-5 unreserved visa categories may necessitate retrogression of the final action date or render the category unavailable" before the fiscal year closes on September 30. The India EB-5 unreserved final-action date already sits at May 1, 2022. Attorneys at firms including Davies & Associates have predicted a cutoff could appear in upcoming bulletins.

If the unreserved category retrogresses, Indians lose the concurrent-filing advantage — the very thing that makes EB-5 attractive to people already living in the country. New investors could still file the I-526E petition, but the ability to file I-485 alongside it, and thus get those interim work and travel permits, would be postponed by years.

The reserved set-aside categories — Rural, High-Unemployment Area, and Infrastructure — remain current for India as of the June 2026 bulletin, which is why immigration lawyers are urging clients to file in those lanes promptly to lock in availability before the same demand pressure catches up with them.

## What it means for the diaspora

For the Indian American community, the EB-5 boom is a quiet referendum on the rest of the system. People do not part with $800,000 lightly; they do it when the alternatives have become unbearable. The route is not without friction — RBI and the Liberalised Remittance Scheme cap how much money can leave India, Tax Collected at Source on remittances eats into timelines, and USCIS scrutiny of source-of-funds documentation has intensified, with regional-center loan structures drawing particular attention.

There is also a generational tilt. EB-5 is increasingly being used by parents to secure status for children who risk "aging out" of dependent eligibility at 21 while stuck in the EB-2 backlog — buying a green card outright to outrun a clock the family never set.

The investor visa was designed as a niche program for capital, not a release valve for skilled workers trapped by a broken queue. That it is now being used as one tells you most of what you need to know about where employment-based immigration stands in 2026. For Indians who can afford it, the message from immigration attorneys is consistent: if you are going to do this, file before the window closes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indians Still Want to Study Abroad. They Just Stopped Choosing America",
        "subheadline": "US student visas for Indians fell 69% in peak 2025 months. The students didn't quit — they rerouted to Germany, the Netherlands and Ireland, and the diversion may be permanent.",
        "slug": make_slug("indian-students-rerouting-germany-netherlands-ireland-us-f1-decline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The collapse in Indian students choosing the US is reshaping who joins the diaspora a decade from now — fewer Indian-origin graduates feeding the H-1B pipeline that built Silicon Valley's Indian American leadership class.",
        "tags": ["f1-visa", "students", "opt", "immigration", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Collegedunia — Where Indian Students Are Going Instead of US and UK in 2026", "url": "https://collegedunia.com/news/where-indian-students-going-instead-us-uk-2026"},
            {"name": "The Hindu BusinessLine — Indian student enrolment in US falls nearly 7%", "url": "https://www.thehindubusinessline.com/news/education/indian-student-enrolment-in-us-falls-nearly-7-amid-stricter-visa-rules/article.ece"},
            {"name": "Outlook Business — US Clears Visa Rule Change, Foreign Students May Face Stay Limits", "url": "https://www.outlookbusiness.com/economy-and-policy/us-visa-rule-change-foreign-students-stay-limits-indians"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International graduates in gowns celebrate outdoors, as Indian students increasingly look beyond the US.",
        "image_attribution": "Pexels",
        "body": """The number of Indians studying abroad fell 6.1% in 2025 — from 1.33 million to 1.25 million — the first decline after three straight years of growth, according to India's Ministry of External Affairs. The easy reading is that ambition cooled. The data says the opposite. Indian students did not stop wanting to leave; they stopped choosing the destinations that used to be automatic, and America is at the top of the list they are walking away from.

The proximate cause is access, not appetite. US F-1 visas for Indian students dropped 69% in peak months of 2025 as consulates throttled appointments and rejections climbed. Canada rejected roughly 80% of Indian study-permit applications after raising financial thresholds. Australia doubled its post-study work-visa fee to AUD 4,600. The three countries that for two decades absorbed the bulk of Indian student migration all tightened at once.

## The reroute, not the retreat

What the headline decline obscures is where those students went instead. Germany now hosts 59,419 Indian students — more than double the 28,905 it had in 2020. The Netherlands, Ireland, Japan and Singapore are all reporting accelerating Indian enrolment. These are not consolation prizes; they are deliberate choices by students who ran the numbers and concluded that a German master's with a predictable post-study work pathway beats a US degree shadowed by visa uncertainty and a $100,000 H-1B fee waiting at the other end.

For the US specifically, the erosion is measurable. SEVIS data shared with India's Rajya Sabha showed Indian students in American institutions fell from 378,787 in February 2025 to 352,644 in February 2026 — a 6.9% drop. The 2024-25 Open Doors report still counted roughly 363,000 Indian students, the largest international cohort in the country, but the trajectory is now clearly downward.

## A rule change that adds to the chill

The exodus is unfolding just as Washington prepares to make the US less hospitable to the students who do come. A Department of Homeland Security proposal, cleared by the White House Office of Management and Budget in June, would scrap the long-standing "duration of status" system that lets F-1 students stay for the length of their program. In its place: fixed terms of admission, with extensions requiring fresh USCIS paperwork for anyone whose degree runs long.

That hits Indians disproportionately. A large share pursue doctoral, research and specialised programs that routinely exceed four years — exactly the students who would be forced to file for extensions mid-degree under the new regime. The proposal would also cut the post-completion grace period from 60 days to 30, shrinking the window to find a job, change status, or pack up and leave. Once published in the Federal Register, it moves toward implementation later this year.

## Why the diaspora should care

This is not merely an education story; it is a demographic one. The Indian American leadership class that now runs Google, Microsoft, Adobe and IBM was built on a pipeline that began with F-1 students who stayed on OPT, won the H-1B lottery, and eventually naturalised. Choke the front of that pipeline and you change who the diaspora is a decade from now.

The students rerouting to Berlin and Amsterdam today are the engineers, founders and executives who will build their careers — and pay their taxes, and raise their children — somewhere other than the United States. For Indian American families who measured success partly by their ability to bring the next generation over, the shift is personal. The pathway that brought many of them to America is quietly closing behind them, and the talent that would have followed is learning German instead."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Is Slamming the Door on Legal Immigration. The Bill Is Coming Due",
        "subheadline": "Indian green-card numbers have nearly halved in two years, student arrivals are falling, and economists warn the squeeze on legal migration is now dragging on growth itself.",
        "slug": make_slug("legal-immigration-decline-economic-cost-indians-green-card-workforce"),
        "category": "immigration",
        "vertical": "economy",
        "diaspora_angle": "Indians are the single largest source of America's skilled legal immigrants, so the broad clampdown on lawful migration lands hardest on the diaspora — and the economic fallout, from slower growth to a strained Social Security fund, will be felt by the very communities being turned away.",
        "tags": ["legal-immigration", "green-card", "economy", "workforce", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USA Today — How Trump's immigration policies hurt legal immigration, data reveals", "url": "https://www.usatoday.com/story/news/nation/2026/06/23/trump-legal-immigration-data/"},
            {"name": "Outlook Business — US Plans 75% Citizenship Fee Hike", "url": "https://www.outlookbusiness.com/economy-and-policy/us-citizenship-fee-hike-indian-green-card-holders"},
            {"name": "The Indian Eye — US asks foreign nationals to apply for Green Cards from home country", "url": "https://theindianeye.net/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The US Capitol in Washington, where legal-immigration policy is being rewritten in 2026.",
        "image_attribution": "Pexels",
        "body": """When politicians talk about cracking down on immigration, the picture they conjure is of the border. The numbers tell a different story. The sharpest contraction in 2026 is happening to legal immigration — the doctors, engineers and graduate students who arrive with paperwork in hand — and Indians, who supply more of America's skilled lawful migrants than any other nationality, are absorbing the brunt of it.

The data is stark. Indian green-card recipients fell from 127,010 in 2022 to 78,070 in 2023, then to 66,800 in 2024, according to Office of Homeland Security Statistics figures — nearly halving in two years. Indian student enrolment is down almost 7% year over year. And the policy machinery has kept tightening: a $100,000 fee on new H-1B petitions (since struck down by a Massachusetts federal court but under appeal), a 75% hike in the naturalisation fee with waivers eliminated, the end of automatic work-permit extensions, and a new USCIS memo directing many green-card seekers to return to their home countries to file.

## The "go home to apply" turn

That last change captures the shift in posture. On Friday, USCIS announced that adjustment of status within the United States would now be treated as an "extraordinary form of relief," granted only in limited cases. "From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," spokesman Zach Kahler said.

For Indians, "home country" is not a quick errand. With consular appointment backlogs already stretching into months and the EB-2 queue running past 15 years, a requirement to process abroad converts an administrative step into an open-ended disruption of careers and families. A later clarification softened the edges — applicants who provide an "economic benefit" or serve the "national interest" may still process domestically — but the default has flipped from welcome to suspicion.

## Where the bill lands

Economists are increasingly blunt that this is not a free policy. After most large American cities saw population declines following the pandemic, the recovery that began in 2024 slowed again in 2025, a trend experts largely attribute to falling international migration. "When the workforce starts to decline, that means less economic growth," said David Bier of the Cato Institute. "It's a real problem for the country that the administration has taken such a hard line, even against legal immigration."

There is a fiscal dimension too. Immigrants — documented and undocumented — pay into Social Security even though most will collect little or nothing for years, and the trust fund supporting more than 75 million Americans is projected to run dry in 2032. Choking off the inflow of working-age, tax-paying skilled migrants removes a quiet subsidy at precisely the moment the math gets harder.

## The diaspora's double bind

Indian Americans occupy an uncomfortable position in this story. They are simultaneously one of the most economically successful immigrant communities in the country and the group most exposed to the clampdown, because they dominate the legal, employment-based pipeline being squeezed. The naturalisation fee hike lands on the Indians at the front of the citizenship line; the green-card processing memo lands on the Indians stuck in the longest queue; the student-visa throttle lands on the largest international cohort.

Some of the harshest measures have already been partially reversed by courts or after public backlash — the H-1B fee was struck down, cancelled student visas were largely reinstated after more than 100 lawsuits. But experts caution that even temporary restrictions do lasting damage, because they signal to the world's most mobile talent that the United States is no longer a sure bet. The students rerouting to Germany and the investors filing EB-5 petitions before the window closes are reading that signal clearly. The question for America is not whether it can turn the talent away. It is whether it can afford to."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
