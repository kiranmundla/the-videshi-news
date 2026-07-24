#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-08 04:00 UTC"""

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
# ARTICLE 1: PERM 501-Day Processing Crisis
# ──────────────────────────────────────────────

art1_body = """Five hundred and one days. That is how long, on average, the Department of Labor now takes to process a single PERM labor certification through analyst review — the mandatory first step on the road to an employment-based green card.

The latest DOL processing data, updated through 30 April 2026, puts the figure in stark terms. Cases currently under analyst review were filed in February 2025. Audit reviews are pulling from November 2025. And the average calendar-day count for analyst determinations completed in March 2026 hit 501 days — up from roughly 460 in late 2025 and a figure that would have seemed absurd five years ago.

For most immigrant workers, PERM is an abstract bureaucratic hurdle. For Indian H-1B holders in their fifth or sixth year of status, it is a ticking bomb.

## The six-year wall

Under current law, an H-1B worker is limited to six years of stay in the United States. Extensions beyond six years are available only if a PERM labor certification or I-140 immigrant petition was filed at least 365 days before the H-1B's expiration — a provision under the American Competitiveness in the Twenty-First Century Act (AC21).

The arithmetic is unforgiving. The total PERM timeline — from prevailing wage determination through DOL adjudication — now runs roughly 28 to 36 months. Add in the recruitment phase, the filing itself, and any audit delays, and an employer who begins the process at the start of an employee's fourth year may still be cutting it dangerously close to the six-year wall.

"Filing a labor certification during the sixth year of H-1B status has become an increasingly high-risk strategy," immigration attorney Keshab Raj Seadie warned in a recent analysis. "Employers and foreign national professionals who delay initiating the green card process until the final year of H-1B validity may face serious immigration consequences, including loss of work authorization and forced departure from the United States."

## India's double bind

The processing bottleneck lands hardest on Indian nationals, who account for roughly three-quarters of all H-1B approvals and face the longest employment-based green card backlogs in the system.

The June 2026 Visa Bulletin tells the story: EB-2 India's final action date sits at 15 January 2015. EB-3 India: also 15 January 2015. That is an eleven-year gap between a priority date and the possibility of a green card. So even if PERM is approved and an I-140 filed and approved, the wait for the actual green card stretches more than a decade.

The practical reality: an Indian engineer who arrived on an H-1B in 2024 may not receive a green card until the late 2030s or beyond, assuming the backlog does not worsen further. In the interim, they remain tethered to their sponsoring employer, unable to change jobs freely until they reach the I-485 filing stage — if their priority date ever becomes current.

## The audit trap

PERM processing is not just slow; it is unpredictable. Cases flagged for audit face an additional six to twelve months of delay, and the audit rate has been climbing. An audited case filed in the fifth year of H-1B status can easily push past the six-year limit, leaving the worker with no legal basis to remain.

There is no premium processing for PERM. No fee accelerates DOL adjudication. Unlike the I-140, where employers can pay $2,965 for a 15-business-day decision, the PERM queue moves at exactly one speed: bureaucratic.

## The alternatives are narrowing too

Some Indian professionals have turned to the EB-2 National Interest Waiver (NIW), which bypasses the PERM requirement entirely and allows self-petitioning. But even that route has tightened — NIW denial rates have climbed to 37 per cent, higher than EB-1A extraordinary ability petitions.

The EB-1A category, long considered the fast track, now requires EB-1 India priority dates as well, with the June 2026 visa bulletin showing a cutoff of 1 December 2023.

For the roughly 862,000 Indian nationals estimated to be in the employment-based green card backlog, the PERM processing crisis is not an inconvenience. It is the difference between staying in the country and being forced to leave — not because of any fault of their own, but because a government queue cannot keep up with the demand it created."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Five Hundred and One Days — The PERM Queue That Could Force You Out of America",
    "subheadline": "Labor Department processing times have swelled to nearly seventeen months, trapping Indian H-1B workers between a six-year visa wall and an eleven-year green card backlog.",
    "slug": make_slug("perm-501-day-processing-crisis-indian-h1b-green-card"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders face the longest PERM waits and the deepest green card backlogs. A 501-day average processing time means workers who don't start early enough in their H-1B tenure risk losing work authorization entirely — not because of any rule violation, but because the queue moved slower than their visa clock.",
    "tags": ["perm", "green-card", "h1b", "uscis", "dol", "processing-times", "eb2-india", "visa-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "DOL OFLC Processing Times", "url": "https://flag.dol.gov/programs/perm/processing-times"},
        {"name": "Manifest Law — PERM Processing Times 2026", "url": "https://manifestlaw.com/perm-processing-times/"},
        {"name": "Beyond Border Global — PERM Timeline Guide", "url": "https://beyondborderglobal.com/perm-approval-time-2026/"},
        {"name": "Alma — EB-2 PERM Green Card Timeline", "url": "https://tryalma.com/resources/eb-2-perm-green-card-timeline"},
        {"name": "EduDaily24 — USCIS Visa Bulletin June 2026", "url": "https://en.edudaily24.com/uscis-visa-bulletin-june-2026/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_2.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_2.jpg",
    "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body,
}

# ──────────────────────────────────────────────
# ARTICLE 2: 7% Country Cap on H-1B Admissions
# ──────────────────────────────────────────────

art2_body = """Buried in the American White-Collar Worker Jobs Act of 2026 — the bill introduced by Republican Congressman Chip Roy of Texas on 4 June — is a provision that has received far less attention than the proposal to end the H-1B-to-green-card pipeline: a seven per cent per-country cap on H-1B admissions.

The numbers explain why this matters. Indians currently receive roughly 73 per cent of all H-1B visas awarded annually — about 47,450 of the 65,000 regular cap. Under Roy's bill, no single country could account for more than seven per cent of the allocation. On the existing cap, that ceiling would be 4,550 visas for Indian nationals.

That is a 90 per cent reduction, overnight.

x-official:https://x.com/chiproytx/status/2062683867991900226

## A cap that already exists — and one that doesn't

The per-country limit is a familiar concept in immigration law, but it has only ever applied to employment-based and family-based green cards, where no single country can receive more than seven per cent of the annual allocation. That cap is the primary reason Indian nationals face an eleven-year wait for EB-2 and EB-3 green cards — there are vastly more qualified applicants from India than the per-country limit allows.

What Roy's bill proposes is extending this same logic to the H-1B programme, which has never had a per-country restriction. H-1B visas are allocated based on employer petitions and, under the new wage-weighted system, salary levels. The nationality of the worker has been irrelevant.

Introducing a seven per cent cap on a temporary work visa would fundamentally change who American employers can hire. Technology companies, consulting firms, hospitals, and research institutions — which collectively sponsor the majority of Indian H-1B workers — would find their candidate pools sharply restricted not by qualification, but by passport.

## Who fills the gap?

The bill does not increase the overall H-1B cap. It simply redistributes who receives the existing 65,000 visas. In practice, this would mean slots currently going to Indian engineers, data scientists, and healthcare professionals would be reallocated to nationals of other countries — whether or not qualified candidates from those countries are available.

The Indian IT industry, which has already reduced H-1B filings by 46 per cent over the past five years according to USCIS data, would face near-total exclusion. Major outsourcing firms — Tata Consultancy Services, Infosys, Wipro, HCL Technologies — that have historically sponsored thousands of workers would be limited to a few hundred at most.

American technology companies would not be spared either. Amazon, Microsoft, Google, Apple, and Meta — which rank among the top sponsors of Indian talent — would find themselves competing for a drastically smaller pool of available Indian workers.

## The bill's other provisions compound the effect

The country cap does not exist in isolation. Roy's bill would simultaneously:

- **Reduce H-1B duration from six years to two years**, eliminating the time most workers need to begin the green card process
- **End dual intent**, requiring H-1B holders to maintain a residence abroad and demonstrate no intention to stay permanently
- **Eliminate OPT**, cutting off the post-graduation work pathway used by roughly 95,000 Indian students annually
- **Require employers to prove no American workers are available**, with mandatory domestic advertising and a ban on hiring H-1B workers if the company has recently conducted layoffs

Taken together, the provisions would not merely reform the H-1B programme — they would dismantle the entire pipeline that has funnelled Indian technical talent into the American economy for three decades.

## The likelihood question

Roy is retiring from Congress, and the bill faces uncertain prospects. Immigration restrictionists — including the Federation for American Immigration Reform, the Immigration Accountability Project, and US Tech Workers — have endorsed it. But the technology industry, which depends on H-1B hiring, will oppose it vigorously.

The Trump administration has shown appetite for H-1B restrictions: the $100,000 fee on new petitions, the wage-weighted lottery, and heightened denial scrutiny all arrived in the past year. But a statutory seven per cent country cap would require congressional action, not executive discretion.

For Indian professionals already in the United States, the bill is a reminder of something many have learned the hard way: in American immigration law, the rules can change faster than any queue moves. And in a system where India already supplies three-quarters of the skilled workforce, any cap on nationality is, by arithmetic alone, a cap on India."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Seven Per Cent — The Hidden Provision That Would Slash Indian H-1B Visas by Ninety Per Cent",
    "subheadline": "A buried clause in the Chip Roy bill would cap any single country's H-1B admissions at 4,550 per year. Indians currently receive about 47,000.",
    "slug": make_slug("seven-percent-country-cap-h1b-india-chip-roy-bill"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians receive roughly 73% of all H-1B visas. A 7% per-country cap would reduce that to about 4,550 — a 90% cut that would reshape every Indian professional's calculus about working in America, from first-year engineers to senior architects who have built careers around the assumption that H-1B availability isn't rationed by nationality.",
    "tags": ["h1b", "country-cap", "chip-roy", "immigration-reform", "indian-workers", "congress"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://outlookbusiness.com"},
        {"name": "Nagaland Post (IANS)", "url": "https://nagalandpost.com"},
        {"name": "The Hindu Business Line", "url": "https://thehindubusinessline.com"},
        {"name": "Latestly", "url": "https://latestly.com"},
        {"name": "Heritage Foundation — H-1B Special Report", "url": "https://heritage.org"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
    "image_caption": "U.S. Representative Chip Roy of Texas, sponsor of the American White-Collar Worker Jobs Act of 2026",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body,
}

# ──────────────────────────────────────────────
# PUBLISH
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
