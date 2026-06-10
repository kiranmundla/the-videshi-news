#!/usr/bin/env python3
"""Immigration writer — 2026-06-10 00:00 UTC run."""

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

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: The 60-Day Grace Period Under Siege
# ─────────────────────────────────────────────────────────────────────

art1_headline = "Sixty Days and a Suitcase — The Safety Net That 730,000 Indian H-1B Workers Can No Longer Trust"
art1_subheadline = "Between tech layoffs, USCIS issuing Notices to Appear during grace periods, and a Congressional bill that would halve H-1B tenure to two years, the 60-day window after job loss has never been more precarious for Indian visa holders."
art1_body = """Lose your H-1B job on a Monday, and by Tuesday the clock is already running. You have sixty calendar days — not business days, calendar days — to find a new sponsor, change your visa status, or pack seventeen years of an American life into checked luggage and fly to Hyderabad. For roughly 730,000 H-1B holders in the United States, an estimated three-quarters of them Indian nationals, this is not a hypothetical. It is the terms and conditions of their presence in the country.

The sixty-day grace period, codified in 2017 under 8 CFR 214.1(l)(2), was meant as a humane buffer. Before it existed, H-1B workers who lost their jobs were technically out of status the same day — a regulatory cruelty that left even compliant professionals in legal limbo during the time it took to find a new employer. The rule gave workers in H-1B, L-1, O-1, and several other classifications a two-month runway to sort their lives out.

In 2026, that runway is crumbling at both ends.

## The layoff machine has not stopped

The technology sector shed over 260,000 jobs in 2024 and 2025 combined, and the contraction has not ended. Companies from enterprise software to fintech continue restructuring, and Indian H-1B holders are disproportionately represented in the affected workforce. When Cognizant, Infosys, or a mid-size SaaS startup cuts headcount, the employees who are American citizens file for unemployment. The employees who are Indian H-1B holders file for survival.

The grace period is discretionary, not guaranteed. USCIS adjudicators have the authority to issue a Notice to Appear — the document that initiates removal proceedings — at any point during those sixty days. Immigration attorneys report a measurable uptick in NTAs being served to H-1B holders who have filed for a change of status or a transfer but whose petitions are still pending when the sixty-day window closes.

## What the clock actually allows

Under the regulation, the sixty-day period begins the day employment is terminated — not the last day of the pay period, not the day the severance runs out, but the actual date the employer-employee relationship ends. During this window, an H-1B worker has several options, each carrying its own risks.

The fastest route is an H-1B transfer to a new employer. Under portability rules, a worker can begin employment with the new sponsor as soon as the transfer petition is filed with USCIS, without waiting for approval. But finding a willing employer in sixty days — one that will sponsor the petition, pay the prevailing wage, and absorb the filing costs — is considerably harder than the regulation makes it sound.

The next option is a change of status, typically to B-1/B-2 visitor status. This preserves lawful presence but strips the worker of employment authorisation. For someone with a mortgage in Sunnyvale and children in school, stepping into tourist status is a financial death sentence disguised as legal compliance.

For those with extraordinary ability credentials, an O-1 petition offers a lifeline — but the evidentiary bar is high, the filing timeline is tight, and premium processing fees of $2,965 (after the March 2026 hike) add to the financial pressure of an already devastating job loss.

## The Chip Roy bill would make it worse

Representative Chip Roy's American White-Collar Worker Jobs Act of 2026, introduced on June 4, would slash the H-1B visa duration from six years to two. If enacted, the bill would also eliminate dual intent — the legal doctrine that allows H-1B holders to simultaneously hold temporary status and pursue a green card. Without dual intent, the grace period becomes less of a bridge and more of an exit ramp. There is no next step if permanent residency is no longer a possibility.

The bill would also bar companies that have recently conducted layoffs from filing new H-1B petitions. For Indian IT outsourcers — companies like TCS, Infosys, and Wipro that routinely restructure their American workforce — this provision would functionally close the front door while bricking shut the back.

## What every Indian H-1B holder should know right now

Immigration attorneys advising diaspora clients are consistent on three points. First, maintain meticulous employment records — termination letters, final pay stubs, and any written documentation of the end date. USCIS may request proof of when the clock started. Second, do not wait until week four to begin a transfer process. The strongest H-1B transfers are filed in the first two weeks, before administrative processing delays can eat into the remaining window. Third, consider filing for change of status to B-2 as a backup even while pursuing a transfer — the change-of-status petition preserves lawful presence if the transfer falls through.

The sixty-day grace period was designed for a labour market that no longer exists — one where a skilled engineer could reasonably find a new sponsor between one pay cheque and the next. In the current environment, sixty days is not a safety net. It is a stopwatch.

x-official:https://x.com/USCIS/status/1929246017358045241"""

art1_sources = json.dumps([
    {"name": "NRI Globe", "url": "https://nriglobe.com/h1b-60-day-grace-period-2026/"},
    {"name": "U.S. Code of Federal Regulations (8 CFR 214.1)", "url": "https://www.govinfo.gov/content/pkg/FR-2016-11-18/pdf/2016-27540.pdf"},
    {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
    {"name": "Nagaland Post (Chip Roy bill)", "url": "https://nagalandpost.com/us-lawmaker-introduces-bill-seeking-major-h-1b-overhaul/"},
    {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/how-a-broken-h-1b-visa-lottery-scheme-and-strict-us-immigration-policy-ruined-an-it-workers-american-dream/"}
])

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: The $8.5 Million Question — What Happens After the $100K Fee Ruling
# ─────────────────────────────────────────────────────────────────────

art2_headline = "Eight-Point-Five Million Dollars Paid, One Judge's Pen, and No Refund in Sight — The H-1B Fee Aftermath Nobody Is Explaining"
art2_subheadline = "A Boston federal judge has vacated Trump's $100,000 H-1B fee 'in its entirety.' But eighty-five employers already paid, a DC court upheld the same fee, and the administration says it will appeal. For Indian workers, the confusion is the point."
art2_body = """On Monday, U.S. District Judge Leo Sorokin in Boston declared the Trump administration's $100,000 H-1B visa fee unlawful and vacated it "in its entirety." The forty-two-page ruling was unambiguous: the fee is a tax, Congress never authorised it, and the executive branch overstepped. By the time the ink dried on the order, immigration lawyers across the country were fielding the same question from their Indian clients: so do we still have to pay?

The answer, infuriatingly, is: it depends on which federal circuit your employer files in.

## The circuit split, explained without the legalese

Judge Sorokin's ruling in the Massachusetts case directly contradicts a December 2025 decision by Judge Beryl Howell in Washington, D.C., who upheld the same fee as a lawful exercise of presidential authority. The D.C. ruling kept the fee in effect through at least September 2026, when the original proclamation was scheduled to expire. A third lawsuit, filed by religious groups and labour organisations in San Francisco, remains pending.

Three federal courts. Two opposite rulings. One fee that either does or does not exist, depending on geography.

For employers filing H-1B petitions through the USCIS service centres that fall within the First Circuit (which covers Massachusetts), Sorokin's ruling should functionally eliminate the $100,000 fee — at least until an appellate court says otherwise. For employers in jurisdictions covered by the D.C. Circuit, the fee remains operative under Howell's ruling. And for everyone else, the regulatory landscape is a fog.

## The eighty-five payments

As of February 15, USCIS had received exactly eighty-five payments of the $100,000 fee, totalling $8.5 million. These were mostly large technology companies and healthcare systems — the kinds of employers that could absorb a six-figure filing cost and decided the talent was worth the tax. Amazon alone received 19,301 H-1B approvals from 2024 through mid-2025, more than any other company. Microsoft secured 9,914. Apple, 8,075.

Sorokin's ruling vacates the policy in its entirety, which in legal terms means it is treated as though it never existed. Ordinarily, that would entitle the eighty-five paying employers to a full refund. But the administration has already indicated it will appeal, and a stay of the ruling — which would keep the fee in place during the appeal — is a near-certainty given the existing circuit split.

Until the appeals process concludes, or the Supreme Court resolves the conflict, those eighty-five payments sit in a regulatory escrow that nobody in government is eager to discuss.

## Why this matters to every Indian on an H-1B

Nearly three-quarters of all H-1B visa approvals go to Indian nationals. The $100,000 fee was never designed as a neutral policy instrument — it was a sledgehammer aimed at the programme's largest user base.

Before the fee, a standard H-1B filing cost employers between $960 and $7,595, depending on company size, premium processing elections, and fraud prevention surcharges. The $100,000 fee represented a 1,200 to 10,000 per cent increase. The result was predictable: H-1B petition filings fell off a cliff. Smaller employers — regional hospitals, mid-size engineering firms, university departments — stopped filing altogether. The workers they would have sponsored were overwhelmingly Indian.

The twenty state attorneys general who brought the Massachusetts lawsuit argued that the fee was crippling their ability to hire teachers, doctors, and university faculty. The American Medical Association called Sorokin's ruling "a victory for patients," noting that international medical graduates — a significant number of them Indian — fill critical roles in underserved and rural communities.

## What happens next

The administration has two paths. It can seek a stay from the First Circuit, which would freeze Sorokin's ruling while the appeal proceeds. Or it can fast-track a petition to the Supreme Court, arguing that the circuit split demands immediate resolution. Either way, the fee's status will remain contested well into 2027.

For Indian H-1B workers and the employers who sponsor them, the practical guidance from immigration attorneys is blunt: do not assume the fee is dead. File as though it still applies. Budget for the worst case. And watch the docket.

Judge Sorokin may have called the fee a tax. Judge Howell called it lawful. The Supreme Court will eventually call it something definitive. Until then, the $100,000 question remains exactly that — a question.

x-official:https://x.com/USCIS/status/1929246017358045241"""

art2_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
    {"name": "Wall Street Journal", "url": "https://www.wsj.com/us-news/law/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-71c9a021"},
    {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/09/trump-h1b-visa-fee-struck-down/84100519007/"},
    {"name": "Fox News", "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee-ruling-unconstitutional-tax"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/us-judge-strikes-down-trumps-100000-h-1b-visa-fee-as-unauthorised-tax/article69669281.ece"}
])


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("sixty-days-suitcase-h1b-grace-period-indian-workers-layoff"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "An estimated 730,000 H-1B holders live in the US, roughly 73% of them Indian nationals. Every layoff starts a 60-day countdown that can end in deportation. With the Chip Roy bill proposing to cut H-1B tenure to two years and eliminate dual intent, the grace period is under more pressure than ever.",
        "tags": ["h1b", "layoffs", "grace-period", "uscis", "immigration", "chip-roy"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "image_caption": "A hand holding an open passport with travel stamps at an immigration counter",
        "image_attribution": "Pexels",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("85-employers-paid-100k-h1b-fee-refund-circuit-split-aftermath"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Nearly 73% of H-1B approvals go to Indian nationals. The $100K fee represented a 1,200-10,000% increase over prior costs and caused petition filings to plummet — disproportionately affecting Indian workers and their sponsoring employers. The circuit split means the fee's fate remains uncertain into 2027.",
        "tags": ["h1b", "100k-fee", "circuit-split", "uscis", "sorokin", "immigration"],
        "urgency": "high",
        "sources": art2_sources,
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/United_States_Green_Card_%282023_edition%29.jpg",
        "image_caption": "A United States permanent resident card, the green card that hundreds of thousands of Indian professionals wait decades to receive",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
