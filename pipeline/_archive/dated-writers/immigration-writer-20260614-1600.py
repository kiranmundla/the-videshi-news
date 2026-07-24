#!/usr/bin/env python3
"""Immigration writer — 2026-06-14 16:00 UTC run"""

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
# ARTICLE 1: EB-1A approval rate collapse
# ──────────────────────────────────────────────

article1_body = """Every quarter, USCIS publishes a set of numbers that most immigration attorneys treat like a diagnostic scan. In the fourth quarter of fiscal year 2025, the scan came back ugly: the EB-1A "extraordinary ability" approval rate fell to roughly 53 per cent, down from about 67 per cent for the full year. Nearly half of all petitions were denied or returned with a Request for Evidence.

The timing could not be worse. EB-1A filings are surging. Approximately 7,300 petitions were filed in the first quarter of 2025 alone — more than a 50 per cent jump from the previous quarter — and the annual total is tracking close to 50 per cent above 2024's figure. Indian professionals, who make up more than 70 per cent of all H-1B beneficiaries, are a disproportionate share of the new applicants.

## The H-1B exit strategy

The arithmetic behind the rush is straightforward. With the $100,000 H-1B fee hanging over every new petition — struck down by a federal judge on June 8 but already reinstated pending appeal — the traditional employer-sponsored pathway has become a gamble that many professionals are unwilling to take. The EB-1A, by contrast, allows individuals to self-petition without an employer sponsor, based entirely on a demonstrated record of extraordinary achievement.

For a senior software architect at Google or a principal data scientist at a healthcare startup, the pitch from immigration attorneys has been consistent: build your case around publications, patents, peer reviews, and measurable impact, and you can sidestep the H-1B lottery entirely. The green card, if approved, comes with no per-country backlog — a critical distinction for Indians who face decades-long waits in the EB-2 and EB-3 queues.

## USCIS tightens the screws

But the agency that adjudicates these petitions has been recalibrating what counts as "extraordinary." Immigration attorneys report a parallel rise in Requests for Evidence and closer examination at the final merits stage, with officers placing greater weight on whether an applicant's recognition is selective, independently validated, and sustained over time.

The shift is measurable. A PR firm specialising in earned media for visa petitioners announced on June 11 a new "Final Merits" service — an expedited media relations offering specifically designed for applicants who have received an RFE on a pending petition. The service exists because the market for it has exploded: more petitioners are reaching the final merits stage only to be told their evidence is insufficient.

The practical consequence is a narrowing window. USCIS data from Q4 FY2025 shows that the agency is not simply rubber-stamping the surge in applications. Officers are scrutinising whether media coverage is earned or paid, whether awards are genuinely selective, and whether citation counts reflect real influence or self-referential padding.

## What this means for Indian professionals

For the roughly 400,000 Indian nationals waiting in the EB-2 and EB-3 backlogs, the EB-1A had become the most viable alternative — a meritocratic route that rewarded individual achievement over employer sponsorship. The approval rate collapse does not close that door, but it does raise the threshold considerably.

The calculus now demands genuine preparation, not a hasty portfolio assembled after the H-1B lottery results land. Attorneys recommend building an EB-1A case over 12 to 18 months: securing peer review invitations, publishing in recognised journals, speaking at industry conferences, and documenting the real-world impact of one's technical contributions. A petition assembled in six weeks, padded with pay-for-play awards and sponsored media placements, is exactly the profile USCIS has learned to flag.

For Indian tech professionals weighing their options, the message from the data is clear: the EB-1A remains open, but treating it as a shortcut rather than a rigorous demonstration of excellence is now a coin flip at best."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Every Other EB-1A Petition Is Now a Rejection",
    "subheadline": "Filings surged 50 per cent as Indian professionals fled the H-1B chaos — but USCIS approval rates have cratered to 53 per cent, turning the 'extraordinary ability' route into a coin flip.",
    "slug": make_slug("eb1a-approval-rate-collapse-indian-professionals-filing-surge"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian tech professionals account for most of the EB-1A filing surge; the plummeting approval rate directly threatens their primary alternative to the broken H-1B and decades-long EB-2/EB-3 green card backlog.",
    "tags": ["eb-1a", "uscis", "immigration", "green-card", "h1b", "indian-professionals"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Global Talent PR / PRNewswire", "url": "https://www.morningstar.com/news/pr-newswire/20260611ny69137/global-talent-pr-launches-final-merits-service-for-eb-1a-petitioners-responding-to-requests-for-evidence"},
        {"name": "CXOToday", "url": "https://www.cxotoday.com/news-analysis/eb-1a-visa-filings-surge-as-indian-professionals-shift-away-from-h-1b/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "An open passport displaying immigration visa stamps",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 2: Wild Wild East book on H-1B wage theft
# ──────────────────────────────────────────────

article2_body = """A new investigative book has put a dollar figure on what thousands of Indian H-1B workers have long known but rarely been able to prove: the system that brings them to America is also the system that steals from them. *Wild Wild East: Exiled Americans, Enslaved Indians, and the Systemic Abuse of the H-1B Visa Programme*, by journalist Tanul Thakur, documents at least $121.48 million in verified wage theft over two decades — and argues the actual unrecorded extraction is conservatively a hundredfold higher.

The book, reviewed in *The Indian Express* on June 13, arrives at a moment when the H-1B programme is under simultaneous attack from the White House, Congress, and the courts. But where the political debate centres on whether the programme displaces American workers, Thakur's investigation focuses on a different set of victims: the Indian workers themselves.

## The bench

The core mechanism is deceptively simple. An Indian IT consultancy — the kind known in diaspora shorthand as a "desi body shop" — sponsors an H-1B worker, brings them to the United States, and then has no immediate client assignment for them. The worker is placed "on the bench": technically employed, legally bound to the sponsoring company, but receiving no salary.

Federal law requires that H-1B workers be paid continuously from the moment they arrive. In practice, Thakur documents, certain consultancies maintain a payroll on paper — depositing taxes to satisfy federal oversight — while recovering the equivalent from the worker's future wages. The worker funds their own legal presence in the country.

The arrangement traps workers in a double bind. Leaving the sponsoring company means losing H-1B status and facing deportation. Complaining to authorities means the same. The visa is tied to the employer, and the employer knows it.

## The scale

The $121.48 million figure comes from verified official estimates — Department of Labor enforcement actions, court settlements, and documented legal filings accumulated over twenty years. Thakur, through extensive reporting, traces this through specific companies and individuals, including an entity called 4M that is documented engaging in simultaneous tax and immigration violations.

But the headline number understates the problem. Much of the wage theft goes unreported because the victims cannot report it without jeopardising their immigration status. The book argues that the actual financial extraction, obscured by corporate accounting and the enforced silence of vulnerable workers, runs into the billions.

## Both sides of the same coin

One of the book's sharper observations is that the American workers displaced by H-1B abuse and the Indian workers exploited within it are not adversaries — they are co-equal casualties of unregulated corporate behaviour. Thakur profiles Virgil Bierschwale, a displaced American tech worker who initially blamed foreign workers for his unemployment but, through direct contact with H-1B holders, came to recognise them as fellow victims of the same corporate strategy.

This reframing matters for the current policy debate. The Trump administration's $100,000 H-1B fee — now suspended pending appeal — was justified as protecting American workers from being replaced. But the fee does nothing to address the consultancy model that exploits Indian workers. If anything, it drives more workers toward the very body shops that promise to absorb the cost, further entrenching the exploitative pipeline.

## What the diaspora should know

For Indian professionals considering an H-1B through a staffing or consulting firm, the book is a practical warning. The red flags are specific: promises of placement "within weeks" of arrival, salary structures that kick in only after a client project starts, contracts that impose financial penalties for leaving before a set period, and sponsoring companies with a history of Department of Labor complaints.

The Department of Labor maintains a public database of H-1B employer applications, including prevailing wage determinations and any enforcement actions. Checking a prospective sponsor against that database before accepting an offer is no longer optional due diligence — it is basic self-preservation.

Thakur's investigation spans think tanks, media establishments, universities, and lobbying groups that have sustained the labour-shortage narrative enabling these practices. The $121 million in documented theft is the measurable portion of a system that has operated, largely unchecked, for a generation. The book's contribution is not to reveal something new, but to assemble the evidence in one place — and to insist that the people most harmed by H-1B abuse are not American workers alone, but the Indian workers the programme was supposed to benefit."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "One Hundred and Twenty-One Million Dollars in Stolen Wages",
    "subheadline": "A new investigative book documents two decades of systematic H-1B wage theft by 'desi body shops' — and argues the real number is a hundred times larger.",
    "slug": make_slug("wild-wild-east-h1b-wage-theft-indian-workers-body-shops"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The victims documented in this investigation are overwhelmingly Indian H-1B workers exploited by Indian-run consultancies — the same pipeline that many diaspora families have used or considered using to come to America.",
    "tags": ["h1b", "wage-theft", "body-shops", "immigration", "indian-workers", "exploitation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/la0z3hsvwfg5/"},
        {"name": "The Indian Express", "url": "https://indianexpress.com/"},
        {"name": "U.S. Department of Labor", "url": "https://www.dol.gov/agencies/whd/immigration/h1b"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg",
    "image_caption": "Developers working at computers in a modern tech office",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
