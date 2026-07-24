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

body1 = """The math that used to rescue a laid-off Indian engineer no longer works. For two decades, the script after a pink slip was familiar: find a new employer inside the 60-day grace window, file a transfer, and if the timing slipped, fly to Hyderabad or Mumbai, get a fresh visa stamp, and come back. Annoying, expensive, survivable. That last escape hatch now carries a $100,000 price tag — and it is changing the arithmetic of survival for thousands of Indian professionals.

More than 110,000 technology workers across 144 companies were cut in the first quarter of 2026 alone, according to layoff trackers. Immigration lawyers estimate H-1B holders make up anywhere from 10% to 30% of those losses, and Indians hold roughly 70% of all H-1B visas. The overlap is not abstract. It is a specific, large population of people who now have to do something they have never had to do before: calculate whether returning to America is worth six figures.

## The clock that does not care about severance

The single most dangerous misunderstanding about a layoff is when the countdown starts. Under the federal rule, the 60-day grace period begins on the last day of actual employment — not when severance ends, not when COBRA lapses, not when HR finishes offboarding. A generous severance package does nothing to extend H-1B status. Workers who assume otherwise can quietly slide into unlawful presence, which triggers the three- and ten-year re-entry bars that turn a temporary setback into a decade-long exile.

Inside those 60 days, the options are well-worn: port the H-1B to a new sponsoring employer, change to B-2 visitor status to buy a few months of lawful job-hunting (no work allowed), switch to F-1 and go back to school, or move onto a spouse's H-4 if one qualifies. None of these are new. What is new is what happens when none of them land in time.

## When the exit becomes a $100,000 door

Previously, a worker who couldn't fix their status in 60 days had a fallback: leave the country, have a new employer file a petition, get stamped at a consulate, and re-enter. The presidential proclamation that attached a $100,000 fee to certain new H-1B petitions requiring consular processing has poisoned that well. A worker who must depart and re-enter may now find their new employer staring at a six-figure surcharge simply to bring them back — a cost few mid-level engineers can ask a new boss to absorb.

A federal judge in Massachusetts struck down that fee in June, calling it an unauthorized tax, but the government is widely expected to appeal, and immigration attorneys are still advising clients to plan as if the fee could be reinstated. The uncertainty itself is the problem: a worker deciding in July whether to risk a trip to India cannot know what the rule will be when they try to come home.

## Why this lands hardest on Indians

For most nationalities, a layoff is a scheduling headache. For Indians, it collides with a green-card backlog measured in decades. An engineer from almost any other country whose I-485 is pending can ride out a layoff with relative ease; an Indian in the EB-2 or EB-3 queue may have an approved I-140 but no current priority date, meaning the adjustment-of-status protections that shield others simply are not available yet. They have done everything right for ten years and still have the fewest cushions.

The compounding cruelty is consular wait times. Even a worker willing to swallow the cost and fly home faces interview backlogs that, at some posts, stretch many months. A 60-day domestic clock and a multi-month consular queue do not fit inside each other. For families with school-age children, mortgages, and a spouse on an H-4, the gap is not a paperwork problem. It is a life uprooted.

## What to actually do

Lawyers are converging on the same advice: act in the first week, not the last. Keep pay stubs, I-94 records, and approval notices current and accessible. If a green-card process is underway, find out exactly where it stands — an I-140 approved for more than 180 days can preserve priority-date portability and unlock H-1B extensions past the six-year limit. Explore the compelling-circumstances EAD, the O-1 for high achievers, and cap-exempt employers like universities and nonprofit research institutions, which sidestep both the lottery and, often, the fee debate entirely.

The grace period was always tight. What changed in 2026 is that the back door — the one everybody quietly relied on — now costs more than most people's annual salary. For Indian H-1B holders, the message is blunt: the 60 days were never really 60 days, and the trip home is no longer cheap insurance."""

body2 = """Buried in the immigration code is a provision that most Indian H-1B holders have never heard of and a growing number now desperately need. It is called the compelling-circumstances employment authorization document — a one-year, renewable work permit designed for skilled workers trapped in the green-card backlog who lose their jobs through no fault of their own. In a year of mass tech layoffs, it has quietly become the last safety valve standing between a decade of waiting and a forced departure.

The rule was created in 2017 and broadened in late 2022, but it has always been more talked about than used. The standards are punishing, the awareness is low, and the trade-offs are real. Yet for the specific population it was built for — Indians with approved I-140 petitions and no current priority date — it may be the difference between staying and starting over.

## Who it is actually for

To qualify, a worker generally needs an approved I-140 immigrant petition, must be in valid E-3, H-1B, H-1B1, O-1, or L-1 status, must not have an immigrant visa immediately available based on the Visa Bulletin, and must demonstrate "compelling circumstances." That last phrase is the whole ballgame — and it is exactly the trap for Indians, because the backlog requirement is the easy part. Indians are the textbook case of people with approved petitions and priority dates that will not be current for years, sometimes decades.

The Cato Institute has estimated that the employment-based backlog could take an Indian applicant on the order of several decades to clear. As of recent counts, hundreds of thousands of Indians sit in the EB-2 and EB-3 queues. For this group, "no immigrant visa available" is not a hypothetical — it is their entire reality.

## The high bar of "compelling"

Here is where hope meets paperwork. The Department of Homeland Security has been explicit that job loss alone does not count as a compelling circumstance. An applicant must show something more: serious illness or disability, employer retaliation, substantial harm to the worker, or significant disruption to the employer. One example DHS itself offered is telling — a worker with a highly specialized skill set in a field like artificial intelligence, nuclear energy, or aeronautics who can prove that the same industry does not meaningfully exist back home.

That is a high wall, and it is meant to be. The agency designed the compelling-circumstances EAD as a narrow stopgap, not a parallel green-card track. As New York immigration attorney Cyrus Mehta has put it, the measure is of very limited scope and works only as a bridge when a job loss would derail a foreign worker's life in the United States. It keeps you lawfully present and stops the clock on unlawful presence — but it does not extend your nonimmigrant status, and it does not, by itself, lead to a green card.

## The catch nobody mentions until later

There is a meaningful downside that Indian families weigh carefully. Once you accept a compelling-circumstances EAD, you are generally no longer maintaining H-1B status — you are in a "period of authorized stay" instead. That distinction matters enormously. If you later want to return to H-1B status, you will typically have to leave the country, attend visa stamping at a consulate, and re-enter — which, in 2026, drops you straight into the same consular backlogs and the same $100,000-fee uncertainty that the EAD was supposed to help you avoid.

In practice, the compelling-circumstances EAD is best understood as a tourniquet, not a cure. It stops the immediate bleeding of a 60-day deadline. It does not heal the underlying wound of a backlog that has no end in sight.

## Why diaspora families should know it exists

The reason this matters for the Indian American community is simple: information asymmetry costs people their lives in this country. A laid-off worker who knows about this provision in week one has a fighting chance to file before the grace period expires. One who learns about it on day 61, after their status has already lapsed, may have already triggered a re-entry bar.

Community organizations and immigration attorneys are increasingly urging Indian H-1B holders with approved I-140s to map their options before a layoff ever happens — to know their priority date, keep their I-140 approval notice handy, and understand which doors are still open. The compelling-circumstances EAD is a narrow door, hard to walk through, and full of trade-offs. But for a population that has waited longer than anyone for permanent residency, knowing it is there is no small thing. In a year when the safety nets keep getting cut, the ones that remain are worth understanding before you need them."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The 60-Day Layoff Clock Was Never Really 60 Days. Now the Way Out Costs $100,000",
        "subheadline": "Tech layoffs are colliding with the new H-1B fee, and for Indian workers the old escape route — leave, get stamped, come back — has quietly become unaffordable.",
        "slug": make_slug("h1b-layoff-60-day-grace-period-100k-fee-reentry-trap-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold roughly 70% of H-1B visas and sit in a decades-long green-card backlog, so a layoff that others ride out easily can force them into a six-figure re-entry bill or a decade-long exile.",
        "tags": ["h1b", "layoffs", "60-day-grace-period", "100k-fee", "uscis", "green-card-backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Forbes / Fragomen: For Laid-Off Tech Workers On H-1B Visas, There Aren't Enough Jobs", "url": "https://www.fragomen.com/insights/forbes-for-laid-off-tech-workers-on-h-1b-visas-there-arent-enough-jobs-to-go-around.html"},
            {"name": "Nolo: Just Got Laid Off From H-1B Job — Do I Have Any Grace Period?", "url": "https://www.nolo.com/legal-encyclopedia/just-got-laid-off-h1b-grace-period.html"},
            {"name": "StudentEB5 H-1B Layoff Survival Guide (Connecticut Chronicle)", "url": "https://news.connecticutchronicle.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6803542/pexels-photo-6803542.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An H-1B software developer at work; tech layoffs in 2026 have left thousands of visa holders racing a 60-day clock.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Last Safety Valve for Backlogged Indians Is a Work Permit Almost Nobody Uses",
        "subheadline": "The compelling-circumstances EAD was built for exactly the trap Indian H-1B holders are in — but the bar is brutal and the trade-offs are real.",
        "slug": make_slug("compelling-circumstances-ead-h1b-layoff-green-card-backlog-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians with approved I-140s and no current priority date are the textbook case the compelling-circumstances EAD was designed for, yet most have never heard of it — and learning it exists in week one of a layoff, not day 61, can prevent a decade-long re-entry bar.",
        "tags": ["compelling-circumstances-ead", "h1b", "green-card-backlog", "i-140", "layoffs", "uscis"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Berardi Immigration Law: Tech Layoffs and Compelling Circumstances EAD", "url": "https://www.berardiimmigrationlaw.com/"},
            {"name": "TechGig: USCIS broadens compelling-circumstances EAD for laid-off workers", "url": "https://content.techgig.com/"},
            {"name": "Reddy Neumann Brown PC: Options for Nonimmigrant Workers as Layoffs Continue", "url": "https://www.rnlawgroup.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport filled with travel stamps; the compelling-circumstances EAD keeps a laid-off worker lawfully present without extending H-1B status.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] ~{wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
