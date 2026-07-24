#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 05:00 PDT"""

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
        "headline": "EB-1 India Just Went Backward — The 'Extraordinary Ability' Fast Track Hits a Wall",
        "subheadline": "The June 2026 Visa Bulletin retrogressed EB-1 India by three and a half months in a single update. For thousands of Indian researchers, founders, and senior engineers who thought they'd picked the express lane, the queue just got longer.",
        "slug": make_slug("eb1-india-retrogression-june-visa-bulletin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "EB-1A has long been the go-to escape hatch for Indian professionals stuck in the EB-2/EB-3 backlog — researchers with top-cited papers, startup founders with patents, senior engineers with significant contributions. This retrogression directly impacts thousands in the diaspora who invested heavily in EB-1A petitions expecting faster processing, and raises the question of whether any green card pathway remains viable within a reasonable timeframe.",
        "tags": ["eb-1a", "visa-bulletin", "retrogression", "green-card", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Department of State — Visa Bulletin for June 2026", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "LegalClarity — EB-1A Priority Date for India: Backlog and Filing Rules", "url": "https://legalclarity.org/eb-1a-priority-date-for-india-backlog-and-filing-rules/"},
            {"name": "U.S. Department of State — Visa Bulletin for May 2026", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7235900/pexels-photo-7235900.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The EB-1 category was supposed to be different. While EB-2 and EB-3 applicants from India stare at priority dates from 2012 or earlier, EB-1 — reserved for people with "extraordinary ability," outstanding professors, and multinational executives — was meant to move faster. No labor certification required. No employer-driven PERM process eating up a year before you even file. Just raw merit meeting a visa number.

That story just got harder to tell.

## The Numbers

The June 2026 Visa Bulletin, published by the State Department, moved the Final Action Date for EB-1 India from April 1, 2023 to December 15, 2022 — a backward slide of roughly three and a half months in a single monthly update. The Dates for Filing cutoff sits at December 1, 2023.

To put that in plain terms: if you filed your I-140 petition on January 1, 2023, you went from being eligible for green card approval in May to being locked out in June. One bulletin update erased months of forward progress.

This isn't a new phenomenon. EB-1 India has been subject to periodic retrogression for years, a consequence of the statutory 7% per-country cap that treats a nation of 1.4 billion people the same as one with 5 million. But the speed of this particular reversal caught immigration attorneys and applicants off guard.

## Why EB-1A Matters to the Diaspora

EB-1A — the "extraordinary ability" subcategory — has become the preferred route for a specific slice of Indian professionals in America: researchers with heavily cited publications, engineers who hold patents at major tech companies, startup founders with demonstrated traction, and senior scientists whose work shapes their fields. Unlike EB-2 and EB-3, there's no labor certification, no dependency on a single employer's sponsorship timeline, and historically, faster movement through the queue.

The premium processing fee for an I-140 petition is now $2,965, and many applicants pay it gladly for the certainty of a 15-business-day decision. But that $2,965 buys speed on the petition only — not on the visa number itself. An approved I-140 sitting behind a retrogressed cutoff date does nothing except unlock H-1B extensions beyond the six-year cap. A useful benefit, certainly, but not the green card it was supposed to lead to.

## Children at Risk

For Indian families, the backlog carries a particular cruelty: children aging out. Under immigration law, a child turns into an adult at 21, losing eligibility as a derivative beneficiary on a parent's green card application. The Child Status Protection Act offers partial relief through a formula that subtracts the time an I-140 petition was pending from the child's age. But the math only works if the parent's priority date becomes current before the adjusted age crosses 21.

A three-and-a-half-month retrogression may sound technical. For a family whose child is 20 years and 8 months old with a priority date that was just barely current, it's the difference between staying together and starting a separate immigration case from scratch.

## The 7% Cap Problem

The root cause is structural. U.S. immigration law caps any single country at 7% of total employment-based green cards issued per fiscal year — roughly 9,800 visas. India and China, which produce the largest volumes of qualified applicants in technology, research, and healthcare, consistently exhaust their allocations while dozens of other countries leave theirs unused.

A "spillover" mechanism exists: unused visas from EB-4 and EB-5 categories cascade to EB-1, and surplus EB-1 numbers flow down to EB-2. In good fiscal years, this spillover can push EB-1 India dates forward by months. In lean years — when every category runs hot — the opposite happens. June 2026 appears to be the latter.

## What You Can Do

If your priority date is behind the December 15, 2022 cutoff, the practical advice hasn't changed, but the urgency has increased:

**Check the bulletin monthly.** EB-1 India moves unpredictably. A retrogression one quarter can reverse the next if spillover numbers come through late in the fiscal year (which ends September 30). Don't assume this month's trend holds.

**Get your I-485 filed the moment your date becomes current.** Once a pending I-485 is on file, it stays pending even if dates retrogress afterward. You also gain access to an Employment Authorization Document and advance parole for international travel — benefits that decouple your work and travel from H-1B sponsor dependency.

**Protect your priority date.** It survives job changes and even category changes. If you have an older EB-2 or EB-3 priority date from a previous employer, it can follow you into an EB-1A petition. That earlier date might be the difference between current and stuck.

**Talk to an attorney about your children's CSPA calculations.** The aging-out formula is unforgiving and the one-year filing window after dates become current adds another layer of complexity. Don't leave this to guesswork.

The EB-1A path was never supposed to feel like EB-2 India. For now, it does."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "110,000 Layoffs, 60 Days to Leave — Inside the H-1B Survival Scramble of 2026",
        "subheadline": "Tech companies are cutting jobs at an accelerating pace. For Indian H-1B workers, each pink slip starts a 60-day countdown that can upend a decade of life in America.",
        "slug": make_slug("h1b-layoffs-60-day-grace-period-survival"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest group of H-1B visa holders, and the 60-day grace period disproportionately affects them because many have been in the U.S. for years — even decades — waiting for green cards in the EB-2/EB-3 backlog. A layoff doesn't just mean finding a new job; it means finding a new H-1B sponsor within 60 days or abandoning a green card queue position that took years to reach.",
        "tags": ["h1b", "layoffs", "tech", "60-day-rule", "immigration", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18 — 60 days or leave? US tech layoffs put Indian H-1B workers under pressure", "url": "https://www.storyboard18.com/how-it-works/60-days-or-leave-us-tech-layoffs-put-indian-h-1b-workers-under-pressure-98850.htm"},
            {"name": "Gulte — Tough Times Ahead for H-1B Hopefuls", "url": "https://gulte.com/"},
            {"name": "Layoffs.fyi — Tech Layoff Tracker 2026", "url": "https://layoffs.fyi/"},
            {"name": "Bhaskar English — US H-1B, Green Card Rules Tightened", "url": "https://bhaskarenglish.in/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9301906/pexels-photo-9301906.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The email arrives on a Tuesday morning. Your position has been eliminated. There's a severance package, an HR contact, and a link to outplacement services. For most American workers, it's a career setback. For an Indian professional on an H-1B visa, it's the start of a 60-day immigration emergency.

The numbers tell the scale of the problem. According to Layoffs.fyi, more than 110,000 tech workers across 144 companies have lost their jobs in 2026 so far. Meta, Amazon, and Oracle are among the firms that have cut staff in recent rounds. Indians, who make up the single largest nationality among H-1B beneficiaries, are disproportionately exposed.

## The 60-Day Clock

Under current U.S. immigration regulations, an H-1B worker whose employment is terminated enters a 60-day "grace period." During those 60 days, you can find a new employer willing to sponsor an H-1B transfer, change to another visa category, or leave the country. There is no extension. There is no pause button.

Sixty days sounds manageable when the job market is hot. In a year where tech hiring has contracted sharply and companies are scrutinizing headcount with new intensity, the window feels more like a trapdoor.

"We are seeing a significant spike in RFEs and Notices of Intent to Deny on B-1/B-2 change-of-status applications filed by laid-off H-1B workers," said Rajiv Khanna, a U.S.-based immigration attorney, in a statement to the Economic Times. The message is clear: even the backup options are getting harder.

## More Than a Job Loss

For Indian H-1B holders, the stakes extend far beyond the next paycheck. Many have been in the U.S. for 8, 10, even 15 years, working their way through the employment-based green card backlog. An EB-2 India priority date from 2015 might still be years from becoming current. A layoff doesn't just threaten your income — it threatens your position in a queue you've been standing in for a decade.

If you can't find a new H-1B sponsor within 60 days and you leave the country, your I-140 petition remains valid (assuming it's been approved for 180 days). But re-entering on a new H-1B requires a new employer, a new petition, and possibly a new lottery registration if you're starting fresh. The practical disruption is enormous.

Then there are the lives built around that visa stamp. Mortgages. Children in school mid-semester. A spouse on an H-4 visa whose own work authorization — if they have an EAD — depends entirely on the primary H-1B holder's status. When one person gets laid off, the entire family's legal presence in the country enters a countdown.

## The Options

Immigration attorneys describe several paths that laid-off H-1B workers are pursuing, each with its own risks:

**H-1B transfer to a new employer.** The gold standard, but it requires finding a company willing to sponsor within 60 days. In a contracting job market, this is getting harder. Premium processing ($2,805) can accelerate the petition decision to 15 business days, but the employer still needs to file.

**Change of status to B-2 visitor visa.** Buys time by shifting to tourist status, but USCIS has been issuing RFEs and denials at elevated rates. The B-2 doesn't allow work, so you're burning savings while waiting for a new opportunity. And the recent USCIS memo tightening adjustment of status rules adds another layer of uncertainty — converting from B-2 back to a work visa or green card path may face higher scrutiny than before.

**H-4 dependent status.** If your spouse is on their own H-1B, you can shift to H-4 dependent status. This keeps you in legal status but limits your work options unless you qualify for an H-4 EAD.

**F-1 student visa.** Some workers enroll in graduate programs to shift to student status. It's expensive and slow, but it provides a legal bridge and potentially a new OPT period down the line.

**Leave for Canada or Europe.** An increasing number of Indian professionals are looking at Canada's Express Entry system, the UK's High Potential Individual visa, or Germany's Opportunity Card as alternatives to the U.S. immigration treadmill. The talent pipeline that Brookings recently warned about isn't just hypothetical — it's becoming a real migration pattern.

## The Compound Effect

What makes 2026 particularly difficult is the convergence of multiple pressures. H-1B registrations for FY2027 dropped 38.5% to 211,600 — a signal that employers are pulling back on sponsorship. The new USCIS memo on adjustment of status has narrowed the pathway from temporary visa to green card. The $100,000 fee proposal for certain H-1B applications, while still under discussion, has sent a chilling signal through hiring pipelines.

Add mass layoffs to that mix and you get a population of highly skilled, deeply rooted Indian professionals facing a system that's squeezing them from every direction simultaneously.

## What You Should Do Right Now

If you're on an H-1B and your company is announcing layoffs — or if you suspect yours might — the preparation starts before the email arrives:

**Keep your immigration documents current and accessible.** I-797 approval notices, I-94 records, passport validity, I-140 receipt and approval notices. If you need to file quickly, you can't afford to be searching for paperwork.

**Build your network now.** The 60-day clock rewards people who already have warm connections at companies that sponsor H-1B transfers. Reach out to recruiters who specialize in visa-sponsored positions.

**Consult an immigration attorney before you need one.** Understanding your specific options — based on your visa history, family situation, and green card queue position — takes time. Don't wait for the layoff to start that conversation.

**Know your severance terms.** Some companies will keep you technically employed for a period after notification, which preserves your H-1B status longer than the official 60-day grace period. This is negotiable, and it matters enormously.

The 60-day rule was designed as a reasonable transition period. In 2026, it feels more like a stress test — one that tens of thousands of Indian families are taking without having signed up for it."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
