#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-10 20:00 UTC run"""

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


# ── ARTICLE 1 ─────────────────────────────────────────────────────────
art1_body = """The ink on Judge Leo Sorokin's ruling was barely dry when a Republican congressman from Utah stepped up with a legislative fix.

On June 9 — one day after a federal court in Boston struck down President Trump's $100,000 H-1B visa fee as an unconstitutional tax — Representative Mike Kennedy began promoting the PROTECT Act, a bill that would codify the exact same fee at the congressional level, removing the legal vulnerability that doomed the executive order.

The logic is blunt. Sorokin's 42-page ruling hinged on a single constitutional point: only Congress has the power to levy taxes. Trump's September 2025 proclamation, the judge found, imposed a fee so large and so punitive that it functioned as one. Twenty state attorneys general agreed and sued.

Kennedy's bill sidesteps that objection entirely. By writing the $100,000 minimum into statute, Congress would be exercising the taxing authority the Constitution reserves for it. No executive overreach, no constitutional defect.

## What the PROTECT Act Would Require

Under Kennedy's legislation, employers sponsoring an H-1B worker would pay whichever amount is higher: the prevailing wage for the position, or a flat $100,000 floor. Companies would also need to document that they actively sought American workers and failed to find qualified candidates before turning abroad.

Kennedy told the Daily Caller News Foundation that he views the figure as "a good baseline" and remains open to raising it. "Anybody applying for an H-1B visa needs to be willing at least at a minimum to pay $100,000," he said, "to make sure that our employers in the country are not gaming the system to the disadvantage of American workers."

## The Stakes for Indian Professionals

The H-1B programme issued roughly 283,000 visas to Indian nationals in 2024 — more than 70 per cent of all H-1B visas granted that year, and six times the number issued to China, the next-largest beneficiary. Any structural change to the programme's cost model hits Indian workers and Indian IT services firms disproportionately.

Before Trump's proclamation, sponsoring an H-1B worker cost employers between $2,000 and $5,000 in filing fees. At $100,000, the economics shift dramatically. Only 85 employers had paid the fee as of mid-February, USCIS disclosed in a March court filing — effectively freezing the programme.

If the PROTECT Act passes, the freeze becomes permanent law rather than a contested executive action. Companies like Walmart, which paused H-1B sponsorships after the proclamation took effect, would face the same calculus under a congressional mandate that courts would have far less latitude to overturn.

## A Circuit Split Complicates the Picture

Sorokin's ruling is not the last word. In a separate challenge last December, U.S. District Judge Beryl Howell in Washington declined to block the fee, siding with the administration. The resulting split between circuits all but guarantees the Supreme Court will eventually weigh in.

But Kennedy's bill renders that appellate contest partly academic. If Congress codifies the fee before the court resolves the split, the constitutional question evaporates. The executive did not impose a tax — the legislature did.

White House spokesperson Taylor Rogers said the administration "is confident this order will be reversed on appeal." But the PROTECT Act suggests the administration is hedging: if the courts fail, Congress picks up the torch.

## What Indian Americans Should Watch

The bill faces a long road. It needs committee hearings, floor votes in both chambers, and a presidential signature. Democratic opposition is likely — the same state attorneys general who successfully sued over the executive order would resist a legislative version.

But the bill's existence signals something larger: the $100,000 price tag for H-1B sponsorship now has bipartisan institutional momentum, from the Oval Office to Capitol Hill to the federal bench. For the roughly 730,000 Indian H-1B holders in the United States, the question is no longer whether the fee will stick. It is which branch of government will be the one to make it permanent."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Judge Killed the Fee — Now Congress Wants to Resurrect It",
    "subheadline": "One day after a federal court struck down Trump's $100,000 H-1B charge, a Utah lawmaker introduced a bill to write it into statute. For Indian workers, the threat just changed addresses.",
    "slug": make_slug("protect-act-congress-codify-100k-h1b-fee-kennedy"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals receive over 70% of all H-1B visas. If Congress codifies the $100,000 sponsorship fee into law, it becomes nearly impossible to challenge in court — turning a temporary executive freeze into a permanent barrier for hundreds of thousands of Indian professionals and the companies that employ them.",
    "tags": ["h1b", "uscis", "immigration", "protect-act", "congress", "h1b-fee"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Daily Caller News Foundation", "url": "https://dailycaller.com/2026/06/10/mike-kennedy-h1b-visa-fee-trump-american-workers-immigrants/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/09/politics/trump-h1b-visa-fee-federal-judge/index.html"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/obama-appointed-judge-blocked-trump-birthright-citizenship-order-strikes-again-throws-out-visa-overhaul"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29704418/pexels-photo-29704418.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "The US Capitol building in Washington, DC, where the PROTECT Act faces its legislative journey",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ── ARTICLE 2 ─────────────────────────────────────────────────────────
art2_body = """In 1990, Congress created the H-1B visa programme to funnel the world's best-educated workers into American companies. Thirty-six years later, a growing faction in that same Congress wants to burn the programme down.

Since January, at least a dozen Republican lawmakers have backed four separate bills targeting the H-1B system — proposals that range from tightening eligibility to outright abolition. No other six-month stretch in the programme's history has produced this level of coordinated legislative hostility.

The latest and most comprehensive salvo landed on June 4, when Texas Representative Chip Roy introduced the American White-Collar Worker Jobs Act of 2026. It would shorten the H-1B visa from six years to two, eliminate the Optional Practical Training programme that bridges foreign students into the workforce, end dual intent — the longstanding policy allowing visa holders to simultaneously pursue a green card — and cap any company's non-immigrant workforce at five per cent of its US headcount.

For the roughly 730,000 Indian professionals holding H-1B visas, Roy's bill would dismantle the entire immigration pipeline many have spent a decade navigating.

## Four Bills, Four Angles of Attack

Roy's bill is the latest in a sequence that has accelerated since January.

**The End H-1B Now Act** (January 2, introduced by Georgia's Marjorie Taylor Greene) would phase the programme to zero over roughly a decade, cutting annual visa issuances from 85,000 to 10,000 in the first year and reducing further every year until none remain. A narrow exemption preserves visas for physicians, surgeons, and nurses.

**The EXILE Act** (February 9, introduced by Florida's Greg Steube) skips the gradual approach entirely. It would suspend the H-1B programme by the following year.

**The End H-1B Visa Abuse Act of 2026** (April 22, introduced by Arizona's Eli Crane and backed by seven Republican co-sponsors) would impose a three-year moratorium, cut the annual cap to 25,000, require a minimum salary of $200,000, and bar visa holders from bringing their families to the United States.

**The American White-Collar Worker Jobs Act** (June 4, introduced by Roy) is the most granular, touching wages, employer caps, dual intent, OPT, and the duration of the visa itself.

None of these bills has become law. None is guaranteed to reach a floor vote. But their cumulative weight reveals a strategic shift: the H-1B programme is no longer being questioned at the margins. It is being questioned at its foundations.

## Why Indian Workers Bear the Brunt

Indians account for roughly 73 per cent of all H-1B approvals and dominate the programme across technology, healthcare, and engineering. The Indian IT services industry — TCS, Infosys, Wipro, HCLTech — has long relied on the H-1B to deploy engineers at US client sites.

Roy's bill takes particular aim at outsourcing firms with its five per cent non-immigrant cap. According to Livemint, India's top ten IT outsourcers collectively held about 11,000 active H-1B visas as of March 2026, each earning at least half their revenue from the US market.

The industry is already adjusting. TCS chief executive K. Krithivasan has said the firm is deploying "fewer people than the number of approvals each year" as part of a "consistent reduction in dependency on visa-based talent." Cognizant CEO Ravi Kumar has described "significantly reduced dependency on visas" alongside increased US-local hiring and nearshore capacity.

But individual H-1B holders — the software engineer waiting for a green card, the researcher stuck in the EB-2 backlog — have no such institutional cushion.

## A Right to Sue

One provision in Roy's bill stands out for its novelty: a private right of action. Any American worker displaced by a non-immigrant visa holder could sue the employer in federal court. If enacted, it would turn every hiring decision involving an H-1B worker into a potential lawsuit, adding legal risk on top of the financial and administrative costs already stacking up.

"United States workers have the right not to be displaced by nonimmigrant workers," the bill states. "Any United States worker who is displaced by a non-immigrant shall have a cause of action in tort."

## What Comes Next

None of the four bills has advanced to committee markup. The legislative bar is high, and business groups from the US Chamber of Commerce to the American Medical Association have argued that restricting the programme would damage American competitiveness and deepen talent shortages.

Russell Stamets, an immigration attorney at Circle of Counsels in New Delhi, summed up the dynamic: "The current administration and its MAGA base are super clear: they want to drastically reduce immigration to the US. They are ruthlessly pursuing that goal at multiple levels."

For Indian Americans — particularly those on H-1B visas, those waiting for green cards, and those still planning their American futures from campuses in Hyderabad and Pune — these bills represent something more than political noise. They represent a coordinated effort to close the door through which millions have entered."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Four Bills, Twelve Lawmakers, One Target — The H-1B Programme Has Never Faced This",
    "subheadline": "Since January, Republican legislators have introduced proposals to phase out, suspend, gut, or abolish the visa that 730,000 Indian professionals depend on. A legislative history of the most coordinated assault on H-1B since its creation in 1990.",
    "slug": make_slug("four-bills-republican-assault-h1b-programme-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold roughly 73% of all H-1B visas. Each of the four bills — from Greene's phase-out to Roy's dual-intent elimination — targets a different leg of the pipeline that Indian professionals use to build careers in the United States. The cumulative effect would close multiple pathways simultaneously.",
    "tags": ["h1b", "congress", "chip-roy", "immigration-reform", "opt", "green-card"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/companies/is-2026-the-death-knell-for-h-1b-visa-holders-11780829488222.html"},
        {"name": "Travel & Leisure Asia", "url": "https://www.travelandleisureasia.com/global/people/us-may-end-permanent-residency-via-h1b-visa-route/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/10/mike-kennedy-h1b-visa-fee-trump-american-workers-immigrants/"},
        {"name": "NDTV", "url": "https://www.ndtv.com"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
    "image_caption": "Texas Representative Chip Roy, who introduced the American White-Collar Worker Jobs Act on June 4",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ── INSERT ─────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
