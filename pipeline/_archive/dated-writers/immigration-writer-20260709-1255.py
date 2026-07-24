#!/usr/bin/env python3
"""Immigration writer — July 9, 2026 1:00 PM run"""
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

# ─────────────────────────────────────────────
# Article 1: H-1B Renewals Hit Record
# ─────────────────────────────────────────────

article1_body = """The numbers do not lie, but they do mislead. The US Citizenship and Immigration Services approved 273,026 petitions for "continuing employment" in the first nine months of fiscal year 2026 — already closing in on the full-year record of roughly 291,542 approvals. With three months left in the fiscal year, it is virtually certain that H-1B renewal activity will set a new high.

That headline figure, widely shared by immigration trackers and Indian media outlets, appears to contradict the White House's aggressive posture on work visas. The Trump administration imposed a $100,000 fee on certain H-1B applications (since struck down and reinstated on appeal), pushed a wage-weighted lottery that favours higher salaries, and launched a sweeping fraud investigation into the H-1B and PERM programmes. Tighter scrutiny at every turn — and yet, the renewal count keeps climbing.

## The cap-exempt loophole that isn't a loophole

The explanation is structural, and it matters for anyone trying to read the immigration weather. These 273,026 approvals are not new workers entering the country. They are extensions, employer transfers, and amendments for people already holding H-1B status. The annual cap of 85,000 — the number that generates the lottery, the anxiety, and the headlines — applies only to first-time H-1B petitions. Once a worker is inside the system, renewing or switching employers is cap-exempt and uncapped.

This means an Indian engineer in Seattle who changes jobs from Amazon to Microsoft generates a new approved petition. The same engineer extending her stay for another three years generates another one. A single worker can account for multiple approvals over the course of her career. USCIS does not publish deduplicated headcounts, so the headline number overstates the number of unique individuals holding H-1B status at any given time.

## What this means for Indian professionals

The data sends a forked message. For the roughly 200,000 Indians already working on H-1B visas in the United States, the renewal pipeline is functioning normally. Employers are investing in retaining their existing foreign workforce: extending stays, transferring workers between subsidiaries, and amending petitions to reflect new roles or locations. The cap-exempt system has absorbed the policy turbulence without visible disruption.

For first-time applicants, the picture is grimmer. The annual lottery remains a coin toss. The wage-weighted selection model, expected to take effect for FY 2027, will disadvantage entry-level applicants — precisely the tier where fresh Indian graduates compete. Indian nationals accounted for roughly 71 per cent of all approved H-1B beneficiaries in fiscal year 2024, a dominance that makes any policy shift disproportionately consequential for this population.

## The quiet divergence

What the record renewal numbers reveal is a two-track immigration system. The front door — the lottery, the consular appointments, the $100,000 fee litigation — is narrow, expensive, and increasingly unpredictable. The side door — renewals, transfers, extensions — remains wide open, uncapped, and largely uncontroversial.

For Indian professionals already inside the system, the message is clear: stay put. Changing employers is straightforward. Extending your stay is routine. Leaving the country for visa stamping is the risk — consular backlogs at Indian posts stretch into 2027, and the social media vetting mandate has slowed interview throughput to a fraction of pre-2025 levels.

For those still trying to get in, the record renewal count is cold comfort. It tells them that once you are inside, the system works. Getting inside is the part that is broken."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "H-1B Renewals Just Hit a Record. The Fine Print Tells a Different Story",
    "subheadline": "USCIS approved 273,000 continuing-employment petitions in nine months — but these are not new workers entering the country, and the distinction matters enormously for Indians still waiting outside the door.",
    "slug": make_slug("h1b-renewals-record-high-cap-exempt-not-new-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold roughly 71% of all H-1B visas. The record renewal numbers benefit those already in the US, while first-time Indian applicants face a lottery, wage-weighted selection, and consular backlogs stretching into 2027.",
    "tags": ["h1b", "uscis", "visa-renewals", "immigration", "cap-exempt", "indian-workers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/news/h-1b-visa-renewals-reach-record-high-despite-stricter-us-policies-heres-why"},
        {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/temporary-workers/h-1b-specialty-occupations-and-fashion-models/h-1b-cap-season"},
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A hand holding an open passport with travel and visa stamps",
    "image_attribution": "Pexels",
    "body": article1_body.strip(),
}

# ─────────────────────────────────────────────
# Article 2: $100K Fee Legal Whiplash
# ─────────────────────────────────────────────

article2_body = """A federal judge struck down the $100,000 H-1B visa fee on June 8. Four days later, the government won a stay that put the fee right back. For Indian professionals and the companies that employ them, this is not an abstraction. It is a six-figure question mark hanging over every hiring decision and every trip home.

Judge Leo T. Sorokin of the US District Court for the District of Massachusetts made the core legal argument simple in *State of California v. Mullin*: the $100,000 charge was a tax, and only Congress has the power to impose taxes. President Trump introduced the fee via proclamation in September 2025, arguing the H-1B programme was being overused. Sorokin found that the executive branch had exceeded its authority. Twenty state attorneys general brought the challenge and prevailed on summary judgment.

The ruling vacated the proclamation in its entirety. For a few days, the biggest cost barrier to international hiring in a generation disappeared.

## Then the government appealed

On June 12, the Department of Homeland Security secured a limited stay from the court, temporarily reinstating the $100,000 fee while the case moves to the US Court of Appeals for the First Circuit. DHS filed its appellate brief on June 18, arguing that the fee is a permissible condition on entry — not a tax — within the president's broad authority over immigration.

The legal landscape is now a patchwork. In December, the DC District Court reached the opposite conclusion in *Chamber of Commerce v. DHS*, upholding the $100,000 fee. That decision, squarely at odds with Judge Sorokin's ruling, creates a circuit split — the kind of judicial disagreement that often draws the US Supreme Court's attention.

A merits decision from the First Circuit could take six to 18 months. If the circuits remain divided, the Supreme Court could pick up the case. Until then, the fee is back in force.

## Why this hits Indian workers hardest

The $100,000 fee applies specifically to H-1B petitions filed on behalf of workers located outside the United States — those going through consular processing. For Indian H-1B holders, this creates a cruel intersection with another crisis: the consular stamping backlog.

US consulates in India have been mass-rescheduling visa interviews since December 2025, when the State Department began requiring social media reviews of all H-1B and H-4 applicants. Interview slots at posts in Hyderabad, Chennai, Mumbai, and New Delhi have been pushed to 2027 in some cases. An Indian engineer who travels home for a family emergency and needs to get a new visa stamp now faces both a months-long wait for an interview and the prospect of a $100,000 fee on the petition that gets her back.

The math is punishing. A mid-career H-1B worker earning $120,000 would see the fee consume nearly a full year's salary. Most employers will not absorb this cost for routine transfers or extensions, effectively trapping workers who need consular processing in a financial no-man's-land.

## What employers should do now

Immigration attorneys are advising companies to treat the next six to 12 months as a planning window, not a pause. The specific guidance, outlined in a Bloomberg Law analysis, is practical:

Keep all consular-processing H-1B applications on hold. The fee is temporarily back, and filing now means paying $100,000 with no guarantee of a refund if the ruling stands. Companies that already paid the fee should note that no formal refund mechanism exists yet, though one could emerge if the First Circuit affirms Judge Sorokin's decision.

Audit your H-1B pipeline by visa status, location, and consular needs. Identify which workers can remain in the US through extensions and transfers — which are cap-exempt and fee-exempt — and which require consular processing.

Preserve alternative visa strategies. O-1 extraordinary ability visas, L-1 intracompany transfers, and employment-based green card pathways remain unaffected by the fee. Companies with international offices might consider parking affected workers abroad during the litigation.

## The deeper signal

What makes the fee fight politically revealing is what it says about the administration's strategy. The $100,000 charge was never designed to be permanent policy — it was designed to be a deterrent. Even if courts eventually strike it down, the years of uncertainty will have achieved its purpose: fewer companies willing to sponsor H-1B workers, fewer Indian professionals willing to risk the trip home for stamping, and fewer new entrants willing to bet their careers on a system that can change overnight.

For the 73 per cent of H-1B holders who are Indian, the legal whiplash is not an immigration footnote. It is a rolling tax on stability."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The $100,000 H-1B Fee Was Struck Down. Four Days Later, It Was Back",
    "subheadline": "A federal judge called it an unconstitutional tax. The government won a stay on appeal. Now the First Circuit, a circuit split, and possibly the Supreme Court will decide whether Indian workers pay the price.",
    "slug": make_slug("100k-h1b-fee-struck-down-reinstated-appeal-circuit-split"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The $100K fee targets consular-processing H-1B petitions — the pathway most Indian workers must use when they travel home for visa stamping. Combined with stamping backlogs stretching to 2027, it effectively traps many Indian professionals in the US or prices them out of returning.",
    "tags": ["h1b", "100k-fee", "federal-court", "immigration", "consular-processing", "circuit-split"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/legal-exchange-insights-and-commentary/h-1b-visa-fees-legal-whiplash-demands-employers-preparation"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/07/07/federal-judge-blocks-100000-fee-on-h-1b-visa-applications/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/11633645/pexels-photo-11633645.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A gavel resting on dollar bills atop the American flag, symbolising justice and the cost of immigration",
    "image_attribution": "Pexels",
    "body": article2_body.strip(),
}

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline']}: {e}")
