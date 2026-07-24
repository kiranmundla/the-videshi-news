#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 00:00 UTC batch"""
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
# ARTICLE 1: Legal analysis of the AoS memo
# ─────────────────────────────────────────────

article1_body = """The USCIS policy memo issued on May 22 — declaring adjustment of status an "extraordinary act of administrative grace" — sent shockwaves through Indian immigrant communities across the United States. WhatsApp groups lit up. Reddit threads exploded. Even Alexa, according to one immigration attorney, began telling users that "adjustment of status has been canceled."

It hasn't been. And the gap between what the memo actually says and what the internet has decided it means is wide enough to drive a USCIS filing fee through.

## What the Memo Actually Does

The memo instructs USCIS officers to apply stricter discretionary scrutiny when adjudicating I-485 adjustment of status applications. It reframes the process not as a statutory right but as an "extraordinary act of administrative grace" — language designed to give officers broader latitude to deny or delay cases.

Critically, it does *not* abolish adjustment of status. It does not revoke INA Section 245, the statute that has governed in-country green card processing for five decades. A policy memo written on a government keyboard, as immigration attorney David Yurkofsky bluntly noted, "does not erase fifty years of statutory law and federal court decisions."

## The Numbers USCIS Can't Ignore

Here's the institutional reality that panic-stricken social media posts overlook: USCIS currently has over one million pending adjustment of status applications. Those applicants have collectively paid approximately $1.5 billion in filing fees — fees that fund the agency's operations, since USCIS is almost entirely fee-funded.

The idea that the agency would simply torch the process that keeps its lights on strains credulity. Immigration attorneys widely expect legal challenges, and the memo's characterization of a congressionally created process as mere "administrative grace" is the kind of overreach that federal courts have historically slapped down.

## What H-1B Holders Should Actually Know

The memo contains specific protections that much of the coverage has ignored entirely. It explicitly states that filing for adjustment of status is *not inconsistent* with maintaining nonimmigrant status for dual-intent visa categories — meaning H-1B, O-1, and E-3 holders retain meaningful protection.

Officers are also directed to weigh "positive equities" including U.S. citizen children, home ownership, deep community ties, established employment, and the practical reality that consular processing at many overseas posts is currently suspended or severely backlogged. For Indian applicants specifically, the Chennai and Mumbai consulates already face wait times stretching well beyond a year for immigrant visa interviews.

## Higher Scrutiny Is Not Abolition

The honest assessment: adjustment of status cases will likely become harder. More interviews. More Requests for Evidence. Longer processing times. Stricter review of whether applicants have maintained valid status throughout their time in the US.

For Indian professionals — who make up the single largest group of pending employment-based I-485 applicants — this means tighter documentation requirements and potentially longer waits on top of an already glacial EB-2 India backlog. Attorneys are advising clients to ensure their immigration files are immaculate: no gaps in status, no unauthorized employment, strong employer support letters.

But "harder" is not "impossible," and the distinction matters enormously for families who have built lives, bought homes, and enrolled children in American schools over the past decade while waiting in the green card queue.

## The Legal Challenge Is Coming

Multiple immigration law organizations are already analyzing the memo's vulnerabilities. The core legal problem: Congress created adjustment of status through legislation. An executive agency characterizing a congressional statute as discretionary "grace" rather than statutory entitlement sets up a textbook Administrative Procedure Act challenge.

Immigration attorney groups, including the American Immigration Lawyers Association, are expected to coordinate litigation if the memo begins producing denials that contradict established case law. The precedent from prior administrations attempting similar overreach through policy memos — several were struck down or walked back under legal pressure — gives immigration attorneys cautious optimism.

## What to Do Now

For the roughly 400,000 Indian nationals with pending or planned adjustment of status applications: do not withdraw your case. Do not make irreversible decisions based on WhatsApp forwards or social media panic. Consult a qualified immigration attorney who has actually read the memo — not someone summarizing someone else's summary of a headline about the memo.

The immigration system is tightening. That much is clear. But it has not collapsed, and the legal infrastructure that protects applicants has not been repealed by a policy memo, no matter how aggressively it is worded."""

article1_sources = json.dumps([
    {"name": "USCIS Official Announcement", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
    {"name": "David Yurkofsky Legal Analysis", "url": "https://www.linkedin.com/pulse/stop-panic-david-yurkofsky-8yeoe"},
    {"name": "CNN", "url": "https://www.cnn.com/2026/05/23/politics/trump-green-card-process"},
    {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/national/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69612068.ece"}
])


# ─────────────────────────────────────────────
# ARTICLE 2: Mandatory E-Verify Act of 2026
# ─────────────────────────────────────────────

article2_body = """On May 22 — the same day USCIS dropped its bombshell adjustment-of-status memo — Senators Katie Britt and Tommy Tuberville of Alabama quietly introduced a bill that could reshape the employment landscape for every foreign worker in the United States: the Mandatory E-Verify Act of 2026.

The bill would require *all* U.S. employers, regardless of size, to use the federal E-Verify system to confirm that every new hire is legally authorized to work. It would enhance civil and criminal penalties for employing unauthorized workers, strengthen fraud prevention measures within E-Verify, and prohibit states from blocking or restricting employers' access to the system.

Ten Republican senators have signed on as co-sponsors, including Ted Cruz, Lindsey Graham, Tom Cotton, and Marsha Blackburn — a roster that signals serious legislative intent, not a messaging exercise.

## What E-Verify Actually Is

E-Verify is a Department of Homeland Security web portal that lets employers check a new hire's work authorization documents against government databases. Currently, its use is mandatory only for federal contractors and in certain states (Arizona, Mississippi, Alabama, South Carolina, among others). Most private employers use it voluntarily, if at all.

Making it universal would close what Britt's office calls a "30-year gap in enforcement" since the system was first piloted in 1996. Roughly 10.8 million unauthorized workers currently hold U.S. jobs, according to the bill's sponsors — workers that mandatory E-Verify would theoretically screen out.

## Why Indian Professionals Should Pay Attention

On its face, mandatory E-Verify targets unauthorized employment — not H-1B holders, not green card applicants, not anyone with legal work authorization. But immigration policy rarely works in neat categories, and the second-order effects matter.

**Employer caution will increase.** When penalties for hiring unauthorized workers ratchet up, employers become more risk-averse about *all* immigration-related hiring. Small and mid-size companies — the ones that already find H-1B sponsorship paperwork daunting — may decide the compliance burden is no longer worth it. For Indian professionals, whose H-1B sponsorships are disproportionately concentrated at large tech companies and IT consulting firms, this could narrow the field of willing sponsors further.

**Document scrutiny will tighten.** E-Verify checks already flag "tentative non-confirmations" (TNCs) for legitimate workers when name spellings, document numbers, or citizenship records don't match cleanly across databases. Indian workers with anglicized name variations, multiple passport renewals, or name-change histories are particularly susceptible to TNC headaches that require time-consuming resolution — all while their employment authorization hangs in administrative limbo.

**The staffing industry faces the biggest disruption.** Indian IT consulting firms — Infosys, TCS, Wipro, HCL, and the network of smaller staffing companies that collectively sponsor thousands of H-1B workers — would face universal verification requirements for their entire U.S. workforce. Several of these firms have previously faced scrutiny over employment practices; mandatory E-Verify adds another compliance layer at a moment when the industry is already absorbing the $100,000 H-1B visa fee imposed by the One Big, Beautiful Bill.

## The Broader Tightening Pattern

The E-Verify bill doesn't exist in isolation. It lands in a week that also produced the USCIS adjustment-of-status memo, data showing H-1B registrations dropped 38.5% for FY2027, and an IRS proposal to add citizenship questions to tax returns.

Taken individually, each policy is defensible on its own terms. Taken together, they form a comprehensive tightening of the employment-immigration nexus that affects legal immigrants as much as — if not more than — unauthorized ones. The Indian professional community, which has played by the rules for decades while waiting in green card backlogs that stretch beyond retirement age, finds itself absorbing the collateral impact of policies designed for a different target.

## What Happens Next

The Mandatory E-Verify Act faces a longer legislative path than executive memos. It needs committee hearings, floor votes, and reconciliation with any competing House versions. Business lobbies — including the U.S. Chamber of Commerce, which has historically opposed mandatory E-Verify due to compliance costs and error rates — will weigh in heavily.

But the political math has shifted. Immigration enforcement polls well, and ten Senate co-sponsors on introduction day signals the bill has legs. If it reaches a vote, the question for Indian professionals won't be whether E-Verify affects them directly — it almost certainly won't block anyone with valid work authorization. The question is whether it makes the entire ecosystem around legal immigration sponsorship a little more hostile, a little more cautious, and a little less willing to take on the paperwork and risk that bringing a skilled foreign worker to the United States already entails.

For a community that has spent years navigating an immigration system that was merely slow, the emerging reality is a system that is slow, suspicious, and increasingly expensive — all at once."""

article2_sources = json.dumps([
    {"name": "Senator Tommy Tuberville Press Release", "url": "https://www.tuberville.senate.gov/newsroom/press-releases/tuberville-britt-introduce-mandatory-e-verify-legislation-to-crack-down-on-illegal-immigration/"},
    {"name": "Senator Katie Britt Press Release", "url": "https://www.britt.senate.gov/newsroom/press-releases/us-senator-katie-britt-leads-mandatory-e-verify-legislation/"},
    {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/senate/3444962/katie-britt-drops-e-verify-bill/"},
    {"name": "Conservative Journal Project", "url": "https://conservativejournalproject.com/katie-britt-bill-makes-e-verify-mandatory-for-all-employers/"}
])


# ─────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "One Million Pending Cases, $1.5 Billion in Fees — Why the USCIS Memo Won't Kill Adjustment of Status",
        "subheadline": "Immigration attorneys are pushing back on the panic. The May 22 memo tightens scrutiny but doesn't abolish a five-decade-old statute — and the legal challenges are already being drafted.",
        "slug": make_slug("uscis-aos-memo-legal-analysis-what-it-actually-means"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals represent the single largest group of pending employment-based I-485 applications. The memo means tougher documentation standards and longer waits — but not the end of in-country green card processing that WhatsApp panic suggests.",
        "tags": ["uscis", "adjustment-of-status", "green-card", "h1b", "immigration-law", "i-485"],
        "urgency": "high",
        "sources": article1_sources,
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Mandatory E-Verify Act Just Dropped — And Legal Immigrants May Feel It Most",
        "subheadline": "A new Senate bill backed by ten Republicans would require every U.S. employer to verify work authorization. The target is unauthorized workers, but the collateral damage could reach H-1B sponsors and Indian IT firms.",
        "slug": make_slug("mandatory-e-verify-act-2026-indian-workers-impact"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT consulting firms and H-1B-dependent employers face a new compliance layer on top of the $100K visa fee. Mandatory E-Verify could make smaller companies even less willing to sponsor work visas, narrowing options for Indian professionals.",
        "tags": ["e-verify", "employment", "h1b", "immigration", "legislation", "it-industry"],
        "urgency": "medium",
        "sources": article2_sources,
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7731331/pexels-photo-7731331.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": article2_body
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
