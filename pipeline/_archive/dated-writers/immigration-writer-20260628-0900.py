#!/usr/bin/env python3
"""Immigration article writer for The Videshi — 2026-06-28 09:00 PT run."""

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

# ─── ARTICLE 1: F-1 Duration of Status Rule ───

article1_body = """The rule that kept a generation of Indian students in America without a hard deadline is about to vanish.

The Department of Homeland Security's final rule eliminating "Duration of Status" for F-1 student visas cleared the Office of Management and Budget's review on June 17 — the last bureaucratic gate before publication in the Federal Register. Once published, it takes effect in 60 days. Universities are already bracing for a September intake under a regime that did not exist when their current students applied.

## What Duration of Status Actually Does

Under the current system, an F-1 student enters the United States with no fixed departure date stamped on their I-94 arrival record. Instead, the notation reads "D/S" — Duration of Status — meaning the student may remain as long as they maintain valid enrollment and comply with visa rules. A PhD candidate who needs six years to finish a dissertation simply keeps going. An OPT applicant who files before their program ends stays covered without a separate government filing.

It is, in immigration terms, a rare pocket of flexibility in a system otherwise built on deadlines.

## Seven Changes That Matter

The proposed rule — originally published August 28, 2025, and now finalised after tens of thousands of public comments — rewrites the F-1 framework in seven ways:

**A four-year cap replaces open-ended stays.** Every F-1 student's I-94 will show a specific end date: either their program completion date or four years from entry, whichever comes first. Doctoral students, whose programs routinely stretch to six or seven years, will need to file formal extensions.

**Extensions require USCIS approval and a $1,965 fee.** Currently, a university's Designated School Official updates a student's record in SEVIS — no government application, no fee. Under the new rule, students must file Form I-539 with USCIS. Premium processing, for those who can afford it, costs an additional $2,075.

**The grace period drops from 60 to 30 days.** After completing a program or OPT, students currently have 60 days to depart, transfer schools, or change status. That window gets halved — a meaningful squeeze for anyone waiting on H-1B lottery results or scrambling for a job offer.

**Graduate students cannot change their major or transfer.** This is the most restrictive provision. An Indian student admitted for a Master's in Computer Science at one university cannot switch to Data Science or transfer to another institution at any point during their program.

**Undergraduates cannot change majors or transfer in their first year.** A slightly lighter version of the same restriction.

**No pursuing the same or lower-level degree.** A student who has completed a Master's degree in F-1 status cannot return for a second Master's — effectively killing the "second master's" pathway that many Indian professionals have used to maintain status while waiting for H-1B selection.

**English language training capped at 24 months.** Students in foundation or language programs face a cumulative limit.

## Why Indians Bear the Heaviest Load

Indians are the second-largest group of international students in the United States, with over 330,000 enrolled. They are also, by far, the largest group in the H-1B lottery — and the group most likely to lose that lottery and need a fallback.

The architecture of that fallback has, for years, rested on Duration of Status. An Indian graduate who doesn't get picked in the H-1B draw in April can enroll in a new academic program (often a second Master's), maintain F-1 status through D/S, use CPT to keep working, and try the lottery again the following year. It is clunky, expensive, and stressful — but it works. The proposed rule attacks every link in that chain simultaneously.

Danielle Goldman, co-founder and CEO of the immigration platform Build, told The Indian Eye that the impact would ripple through the American talent pipeline. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial share of the US artificial intelligence workforce, and many entered through exactly the student-to-OPT-to-H-1B pathway this rule constricts.

## What Students Should Do Now

Immigration attorneys are advising current F-1 students to take stock before the rule lands. Students nearing the end of a program should file OPT applications immediately rather than waiting. Those considering a transfer or major change should complete it before the rule's effective date. And anyone on a second Master's program should ensure their SEVIS record is current and their DSO is aware of the coming changes.

The rule's 60-day effective window means the earliest it could bite is mid-August — right as fall semester begins. For the roughly 330,000 Indian students in the United States, a framework they have relied on for decades is being replaced by one that treats every year beyond the fourth as a privilege requiring government permission and a four-figure fee.

The flexibility was never guaranteed. But losing it all at once, in seven simultaneous changes, is the kind of policy event that reshapes migration patterns for a generation."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Rule That Let Indian Students Stay Indefinitely Just Cleared Its Final Review",
    "subheadline": "DHS's Duration of Status elimination — seven changes that hit Indian F-1 holders hardest — passed OMB review on June 17 and is heading to the Federal Register. The 60-day countdown starts on publication.",
    "slug": make_slug("f1-duration-of-status-elimination-indian-students-dhs"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are the second-largest international student group in the US and the most reliant on Duration of Status for fallback pathways after H-1B lottery losses. The rule's ban on second Master's degrees and transfer restrictions dismantle the exact chain Indian graduates have used to maintain legal status.",
    "tags": ["f1-visa", "duration-of-status", "uscis", "international-students", "opt", "h1b", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Marquette University OIE", "url": "https://today.marquette.edu/2026/05/international-students-and-scholars-updates-legal-resources-travel-guidance/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Collegedunia", "url": "https://collegedunia.com/usa/article/us-proposes-to-end-duration-of-status-for-f1-students"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/06/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
        {"name": "American Institute of Physics", "url": "https://www.aip.org/fyi/visa-and-immigration-policy-elimination-of-duration-of-status"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "International students on a university campus in the United States",
    "image_attribution": "Pexels",
    "body": article1_body,
}

# ─── ARTICLE 2: India-US Social Security Totalization ───

article2_body = """Every two weeks, roughly 600,000 Indian workers in the United States watch 7.65 per cent of their paycheque vanish into Social Security and Medicare — taxes that fund a retirement system most of them will never collect from. Their employers match the contribution, dollar for dollar. By one Indian government estimate, the combined annual outflow exceeds $4 billion.

The United States has signed totalization agreements — bilateral treaties that eliminate this double taxation — with 30 countries. France has one. South Korea has one. Even the Czech Republic has one. India does not.

That gap is about to get harder to ignore.

## What a Totalization Agreement Actually Does

A totalization agreement between two countries does two things. First, it prevents workers on temporary assignments from paying social security taxes in both countries simultaneously. An Indian software engineer on a three-year H-1B posting in San Francisco would pay into India's Employees' Provident Fund but be exempt from American FICA taxes — or vice versa, depending on the agreement's structure. Second, it allows workers to combine contribution periods across both countries to qualify for benefits. An Indian national who works ten years in the US and fifteen in India could "totalize" those periods to meet the minimum threshold for American Social Security benefits.

Without such an agreement, the math is punishing. The US requires 40 quarters — roughly ten years — of covered employment to qualify for retirement benefits. An H-1B worker who spends seven years in America, pays tens of thousands into Social Security, then returns to India gets nothing. The money is gone. It does not transfer. It does not follow them home.

## The India-UK Template

In February 2026, India and the United Kingdom signed a Social Security Agreement as part of their Comprehensive Economic and Trade Agreement. The deal exempts employees on temporary assignments of up to 36 months from contributing to the host country's social security system. It covers workers subject to either country's social security rules, regardless of nationality, and requires employers to obtain a certificate of coverage confirming continued home-country contributions.

The UK agreement does not include totalization of benefit periods — it is narrower than a full totalization pact — but it establishes a framework India has publicly said it wants to replicate with Washington.

## Why It Has Not Happened With the US

The obstacle is not technical. India submitted comprehensive data on its social security schemes — the Employees' Provident Fund, the National Pension System, ESIC — to the US years ago, meeting a precondition Washington had set for starting negotiations. India's Ministry of Labour and the Ministry of External Affairs have both signalled willingness.

The holdup is political. American policymakers have historically worried that a totalization agreement with India would reduce revenue flowing into the already-strained Social Security trust fund. The Congressional Budget Office has estimated that Social Security's trust fund will be depleted by 2032. Against that backdrop, any agreement that exempts hundreds of thousands of Indian workers from FICA contributions faces resistance, regardless of its bilateral logic.

There is also a structural mismatch. India's social security system is fragmented — the EPF covers formal-sector employees, the NPS covers government workers and voluntary participants, and ESIC covers lower-wage formal workers. The US Social Security Administration has historically preferred negotiating with countries that have a unified, contribution-based system.

## The Trade Deal Window

US Trade Representative Jamieson Greer visited India on June 24-25, meeting Commerce Minister Piyush Goyal to advance the Bilateral Trade Agreement. Both sides described "substantial progress" and committed to a deal that is "balanced and commercially meaningful."

India has positioned the totalization agreement as a services-sector ask alongside the trade deal — not embedded in the BTA itself, but pursued in parallel. As one source tracking the negotiations told The Hindu BusinessLine last year: "India could pursue a totalization pact with the US simultaneously with the proposed BTA."

The logic is straightforward. India is offering to lower tariffs on American goods and ease non-tariff barriers. In return, it wants relief for its services exports — and the single largest services export India sends to the United States is people. Specifically, highly skilled people on H-1B and L-1 visas whose labour generates billions in value for American companies while their FICA contributions generate billions for American retirees.

## What It Would Mean for the Diaspora

For the roughly 600,000 Indian nationals working in the US on temporary visas, a totalization agreement would mean one of two things: either an exemption from FICA taxes during their US posting (saving roughly $5,000-$8,000 per year for a worker earning $100,000), or the ability to count their US work years toward Indian social security benefits and vice versa.

For Indian IT companies — Infosys, TCS, Wipro, HCL — the savings would be even larger. They pay the employer's 7.65 per cent match on every H-1B and L-1 worker's salary. Across tens of thousands of employees, that adds up to hundreds of millions annually.

And for Indian Americans who have spent a decade or more in the US, earned their 40 quarters, and then returned to India, a totalization agreement would ensure their American benefits follow them home — a provision that currently exists for retirees who move to France, Germany, Japan, or South Korea, but not India.

The India-UK agreement was signed four months after the UK trade deal closed. If the India-US BTA reaches the finish line this summer, the totalization agreement may finally have the political cover it has lacked for two decades. For 600,000 Indian workers, the $4 billion question is whether Washington will treat their contributions as a two-way street — or continue collecting without ever paying back."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Workers Pay $4 Billion a Year Into Social Security. They Will Never See a Dime",
    "subheadline": "India signed a social security pact with the UK in February. It wants the same deal with Washington — and the trade talks may finally give it the leverage to ask.",
    "slug": make_slug("india-us-social-security-totalization-h1b-fica-4-billion"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Roughly 600,000 Indian H-1B and L-1 workers in the US pay FICA taxes they may never collect on. A totalization agreement would save each worker $5,000-$8,000 annually and allow returning Indians to claim US Social Security benefits — a right already available to workers from 30 other countries.",
    "tags": ["social-security", "totalization-agreement", "h1b", "fica", "india-us-trade", "indian-workers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/india-hopes-to-pursue-social-security-pact-with-us-simultaneously-with-trade-deal/article69504637.ece"},
        {"name": "Ministry of External Affairs, India", "url": "https://www.mea.gov.in/press-releases.htm?dtl/38951/Signing+of+Agreement+on+Social+Security+relating+to+Social+Security+Contributions+between+India+and+the+United+Kingdom"},
        {"name": "IRS – Totalization Agreements", "url": "https://www.irs.gov/government-entities/federal-state-local-governments/totalization-agreements"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-says-it-discussed-pathways-interim-trade-deal-with-us-2026-06-25/"},
        {"name": "Social Security Administration", "url": "https://www.ssa.gov/policy/docs/ssb/v79n4/v79n4p1.html"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7247413/pexels-photo-7247413.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Tax and financial documents representing the social security contributions of foreign workers",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ─── INSERT ───

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
