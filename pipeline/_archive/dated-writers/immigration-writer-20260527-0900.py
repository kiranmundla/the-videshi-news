#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-27 09:00 PDT"""
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
        "headline": "If They Can't Come to America, America Is Going to Them",
        "subheadline": "As H-1B restrictions tighten and visa uncertainty spikes, US corporations are responding with a simple workaround: hiring the same talent in Hyderabad, Bangalore, and Gurugram instead.",
        "slug": make_slug("gcc-boom-india-american-companies-hiring-h1b-alternative"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian Americans on H-1B visas, the GCC boom is a double-edged sword — it validates the talent pool Washington is restricting, but it also means the jobs that once required visa sponsorship are quietly migrating to India. Engineers in the US face a new competitive pressure: their employer can now hire equivalent talent at a fraction of the cost, without a single immigration form.",
        "tags": ["gcc", "h1b", "offshoring", "india-tech", "hyderabad", "corporate-hiring"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/american-airlines-plans-double-india-tech-hub-staff-sources-say-2026-05-27/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/global-firms-rethink-gcc-hiring-india-ai-shifts-skill-demand-2026-05-25/"},
            {"name": "Nasscom-Zinnov Report 2026", "url": "https://nasscom.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/in-ai-age-firms-chase-growth-but-with-fewer-workers-2026-05-25/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35175238/pexels-photo-35175238.jpeg",
        "body": """India has 2,117 global capability centres. They employ 2.36 million people. They generate nearly $100 billion in annual revenue. And every time Washington tightens the screws on work visas, that number ticks upward.

American Airlines announced this week that it plans to double headcount at its Hyderabad technology hub to roughly 800 employees by early 2027. Southwest Airlines, not to be outdone, said it would expand its own Hyderabad GCC to about 1,000 staff. JPMorgan Chase, Walmart, McDonald's, Nvidia, and Eli Lilly have all deepened their India operations in the past year alone.

These are no longer back-office cost centres shuffling spreadsheets across time zones. American Airlines' Hyderabad hub does software engineering, artificial intelligence, and cybersecurity — the same work its Fort Worth and Phoenix teams handle. Daimler Truck's India engineers are generating intellectual property. Kimberly-Clark's Indian team is using AI to build entire marketing campaigns.

## The Immigration Feedback Loop

The timing is not coincidental. As H-1B registrations crashed 38.5 percent this season and the One Big Beautiful Bill introduced a $100,000 surcharge on employer-sponsored visas, corporations did what corporations always do: found the path of least resistance.

Why spend $100,000 in fees, six months in lottery uncertainty, and years in green card limbo to bring one engineer to Texas when you can hire five engineers in Hyderabad for the same cost — with zero immigration paperwork?

"Companies are hiring fewer people, just as a matter of abundant caution," Lalit Ahuja, CEO of ANSR, which helps firms build and run global centres, told Reuters. But the quieter truth is that they are not hiring fewer people overall. They are hiring them somewhere else.

The Nasscom-Zinnov report released this month puts the shift in stark terms: India added roughly 500 new GCCs in five years, from about 1,600 in 2021 to 2,117 by the end of fiscal 2026. The acceleration is real, and it tracks almost perfectly with the escalation in US immigration restrictions.

## What It Means If You're Already Here

For Indian professionals on H-1B visas in the United States, the GCC boom creates an uncomfortable new dynamic. Your employer now has a well-staffed alternative in your home country. The business case for sponsoring your green card — already weakened by 15-year backlogs and rising fees — gets harder to make when the same role can be filled in Bangalore at a third of the total cost.

This does not mean mass layoffs of H-1B workers. Companies still need senior talent embedded with US clients, navigating US regulatory environments, and operating in US time zones. But the marginal hire — the one the manager was on the fence about sponsoring — increasingly goes to Hyderabad instead of Houston.

Microsoft India's president, Puneet Chandok, framed it in terms of talent quality rather than cost arbitrage: "The biggest challenge is to get the right talent with the right AI skill." But the subtext is clear. If the talent exists in India, and the visa path to America is expensive and uncertain, the work moves to where the talent is.

## The AI Twist

The GCC story has a second chapter that should concern every Indian professional planning a US career. As AI reshapes hiring, GCCs are becoming choosier about who they bring on. Forty percent of employers now prefer demonstrable AI skills or certifications over degrees, according to a Nasscom-Indeed joint report.

Entry-level positions are particularly vulnerable. "The zero-to-two-years experience bracket will go away is my assumption in the next few years," said Deena Dayalan, head of digital operations at Kimberly-Clark. Companies are not just moving work to India; they are moving *different* work — more specialized, more AI-native, more senior.

For Indian students currently studying in the US on F-1 visas, hoping to transition through OPT to H-1B to green card, this creates a pincer movement. The American visa path is narrowing from one direction. The Indian job market they might return to is narrowing from another — demanding skills that a fresh master's degree alone no longer guarantees.

## The Irony Washington Built

The deepest irony of the current immigration crackdown is that it may be accomplishing the opposite of its stated goal. The policy rationale for restricting H-1B visas is to protect American jobs and encourage domestic hiring. But when corporations respond by moving entire engineering teams to India, the jobs do not return to American workers. They simply leave the country entirely.

India's GCC sector generated $100 billion last year. If the current trajectory holds — and every signal from Washington suggests it will — that number will be considerably higher by 2028. America's immigration system is not keeping talent out. It is building the competition."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'Very, Very Slim' — Why a Top India Analyst Says the Old H-1B Is Gone for Good",
        "subheadline": "The Council on Foreign Relations' Sadanand Dhume warns Indian professionals to stop waiting for a return to normal. The MAGA movement's hostility to legal immigration is structural, not tactical.",
        "slug": make_slug("cfr-dhume-h1b-never-coming-back-maga-legal-immigration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the 627,000 Indians waiting in the green card backlog, Dhume's analysis carries a specific warning: the political coalition that controls US immigration policy is not sympathetic to employment-based immigration regardless of skill level. Planning around a Biden-era reversion is planning around a fantasy.",
        "tags": ["h1b", "india-us-relations", "cfr", "rubio", "maga", "immigration-policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNBC-TV18 / NgBreakingNews", "url": "https://ngbreakingnews.com/2026/05/india-us-ties-losing-steam-despite-rubio-visit-h-1b-system-unlikely-to-return-to-past-norms-expert/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/india/america-first-shadows-visit-by-rubio-to-repair-rift-with-india-1d72e023"},
            {"name": "Fox News", "url": "https://foxnews.com/politics/rubio-pushes-back-indias-concerns-us-visa-curbs-says-policy-must-america-first-trump"},
            {"name": "Atlantic Council", "url": "https://www.atlanticcouncil.org/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "body": """Sadanand Dhume has spent two decades analysing India-US relations. As a senior fellow at the Council on Foreign Relations, he has tracked every twist in the bilateral relationship through three American presidencies. His assessment of where the H-1B visa programme is headed is blunt.

"I personally think that the odds of the H-1B going back to what it was like during the Biden era, or before that, are very, very slim," Dhume told CNBC-TV18 this week, during Secretary of State Marco Rubio's four-day visit to India.

The remark was not casual. It was delivered as a considered verdict from one of Washington's most respected India watchers, and it lands differently from the usual immigration commentary because Dhume is not arguing that restrictions are temporary or cyclical. He is saying the system has permanently changed.

## The MAGA Arithmetic

Dhume's core argument is structural, not partisan. The MAGA movement that propelled Donald Trump to two terms did not limit its immigration scepticism to border crossings and asylum claims, as many Indian professionals initially assumed.

"There was a belief in certain quarters that it was hostile only to illegal immigration and not to legal immigration," Dhume said. That belief, he argued, was wrong.

The political coalition that dominates Republican politics — and by extension, immigration policy — views high-skilled immigration through the same restrictionist lens it applies to every other category. The EXILE Act, introduced by Florida Republican Greg Steube to abolish the H-1B entirely, is not a fringe proposal. It is a signal of where the party's base lives.

For Indian professionals, this distinction matters enormously. The standard coping mechanism for the past year has been to treat the current restrictions as a temporary adjustment — something that will ease once the political winds shift. Dhume is saying the winds have shifted permanently.

## Rubio's India Visit and the Limits of Reassurance

Rubio spent four days in India this week — four cities, a stop at the Taj Mahal, a Bollywood-themed embassy gala, and a phone call from Trump declaring "I love India." The pageantry was deliberate. India-US relations have been strained since last summer, when 50 percent tariffs (the highest new tariffs for any country in Asia), the "hellhole" social media repost, and the immigration crackdown created what Michael Kugelman of the Atlantic Council described as a "discordant soundtrack."

Rubio acknowledged that the visa changes would have a "disproportionate" impact on India. But he insisted they were global, not targeted. "It is not a system that is targeted at India," he said at a joint press conference with External Affairs Minister S. Jaishankar. "It is one that's being applied globally."

Jaishankar's response was notably direct: "While we cooperate to deal with illegal and irregular mobility, our expectation is that legal mobility would not be adversely impacted as a consequence."

Dhume read the exchange for what it was: diplomatic performance. "He has to say what he has to say; that's his job," Dhume noted of Rubio, while crediting him as one of the few administration figures capable of actual relationship repair.

## The Indian IT Factor

Dhume also offered a less comfortable observation for the Indian side. He suggested that some Indian outsourcing firms may have "stretched the original intent of the programme" — a reference to the longstanding criticism that IT services companies used H-1B visas primarily for lower-cost labour substitution rather than genuine specialty hiring.

"The US is rebooting it," he said.

The data backs this up. Major Indian IT firms — TCS, Wipro, HCL, and others — have seen H-1B approval rates collapse. Only Infosys has maintained a significant footprint, partly because it shifted its hiring model toward higher-wage, higher-skill positions years ago. The wage-based selection system introduced this year explicitly penalises the high-volume, lower-wage model that defined Indian IT's American presence for decades.

## What This Means for 627,000 Indians in the Queue

The practical implications for Indian professionals are severe.

Those already in the US on H-1B visas face a transformed landscape. The green card backlog stretches past 190 years for some EB-3 India applicants. The One Big Beautiful Bill, now in the Senate, does nothing to eliminate country caps — the single reform that would most benefit Indian nationals. The $100,000 employer fee proposed in the bill makes sponsorship more expensive. The consular processing memo, partially walked back but still legally effective, adds uncertainty to every adjustment-of-status application.

Those considering a US career from India face a probability calculation that has fundamentally changed. The H-1B lottery registration drop of 38.5 percent this season reflects employers doing that calculation already. Fewer companies are willing to enter a system where the costs are rising, the approval rates are falling, and the political environment signals that further restrictions are coming.

And those planning around a future political correction — a Democratic administration that restores the old rules — should note that even during the Biden era, EB-2 India priority dates barely moved. The backlog is a bipartisan failure. It predates Trump by decades.

## The Advice No One Wants to Hear

Dhume did not offer a solution. Foreign policy analysts rarely do. But the implicit message of his analysis is that Indian professionals should stop treating the current environment as an aberration and start treating it as the new baseline.

That means diversifying career options beyond a single US immigration pathway. It means evaluating Canada, the UK, Singapore, and the Gulf states — not as backup plans, but as genuine alternatives. It means accepting that the 25-year arc of deepening India-US immigration ties has entered a period of sustained contraction.

"I think it's very clear that over the past year or so, US-India ties have lost momentum," Dhume said. He was talking about the diplomatic relationship. But for the hundreds of thousands of Indians whose lives are structured around American work visas, the personal momentum has stalled too — and the expert consensus is that it will not soon recover."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
