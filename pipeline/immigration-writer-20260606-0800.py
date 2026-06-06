#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-06 08:00 UTC"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # ── Article 1: CFPB immigration status mortgage guidance ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Visa Is Now a Credit Score — The CFPB Just Told Banks to Check Your Immigration Status Before Approving a Mortgage",
        "subheadline": "A new federal guidance says lenders may be obligated to factor in whether deportation could disrupt your income. For H-1B holders, that means your six-figure salary might not be enough.",
        "slug": make_slug("cfpb-banks-immigration-status-mortgage-h1b-lending"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders — the largest skilled immigrant group in the US — face immediate consequences. Even those earning $200K+ with pristine credit could see higher scrutiny, longer approvals, or outright denials if lenders decide their temporary visa status represents a repayment risk. Combined with the FHA ban on non-permanent residents, this narrows the path to homeownership for the very professionals America recruited to build its tech sector.",
        "tags": ["cfpb", "mortgage", "h1b", "immigration", "lending", "homebuying"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox Business", "url": "https://foxbusiness.com/politics/trump-admin-tell-banks-immigration-status-may-considered-mortgage-credit-decisions"},
            {"name": "PYMNTS", "url": "https://www.pymnts.com/consumer-finance/2026/cfpb-advises-lenders-to-consider-applicants-immigration-status/"},
            {"name": "HousingWire", "url": "https://www.housingwire.com/articles/cfpb-guidance-points-lenders-to-borrower-immigration-status/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8292879/pexels-photo-8292879.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A mortgage broker and client reviewing loan application documents",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The Consumer Financial Protection Bureau dropped a quiet bombshell on Friday. In a policy statement scheduled for publication in the Federal Register on Monday, June 8, the agency told banks and credit unions they may be *obligated* to consider a borrower's immigration status when deciding whether to approve a mortgage or credit card.

The statement invokes the Truth in Lending Act and Regulation Z, which require creditors to assess a consumer's ability to repay before extending credit. The CFPB's position: if a borrower's immigration status could change their ability to earn income — say, through deportation or visa expiration — lenders must account for that risk.

"This statement emphasizes to creditors that these requirements may obligate consideration of a consumer's immigration status, especially where removal from the United States may disrupt the consumer's income," the CFPB wrote.

Russ Vought, the OMB director who also serves as acting CFPB head, previewed the move on X the day before. His framing was blunter: "An individual's illegal immigration status must be factored into their 'ability to repay' under the Truth in Lending Act."

## What This Actually Means for H-1B Holders

The guidance targets undocumented borrowers most explicitly, but its language sweeps far wider. The CFPB acknowledged that "there are a range of lawful immigration statuses under U.S. law" and that lenders should not assume "consumers with different lawful statuses have identical abilities to repay."

That sentence should alarm every Indian professional on an H-1B visa. An H-1B is, by definition, temporary. It must be renewed. It is tied to a specific employer. A layoff triggers a 60-day clock to find a new sponsor or leave the country. Under this guidance, a lender looking at an H-1B holder's mortgage application can reasonably ask: what happens if this person loses their job?

The math has always favored Indian tech professionals. A senior software engineer at Google earning $250,000 with $100,000 in savings is, by any conventional lending standard, an excellent credit risk. But if the CFPB's guidance leads banks to weight visa status alongside income — treating temporary authorization as a risk factor — that calculus changes.

## The FHA Wall Was Already Up

This guidance lands on top of an existing barrier. In May 2025, the Trump administration directed the Department of Housing and Urban Development to bar non-permanent residents from accessing FHA-insured mortgages. The impact was immediate: according to data from John Burns Research and Consulting, the share of FHA loan volume issued to non-permanent residents collapsed from 6% in April 2025 to less than 1% by June, and to virtually zero by late summer.

FHA loans have long been a gateway for first-time homebuyers, including many Indian professionals making their first major purchase in the US. That door is now shut.

The CFPB guidance adds a second lock. FHA blocked one product category. This guidance could reshape how *all* lenders — conventional, jumbo, credit union — evaluate immigrant borrowers across *all* credit products, including credit cards.

## The Dallas Preview

A Bloomberg investigation published this week offers a preview of what happens when Indian buyers exit a housing market. In Collin County, north of Dallas — where the Indian-born population swelled to 116,000 from 70,000 in half a decade — home prices have fallen nearly 9% year-over-year. Builders who designed homes with north-facing puja rooms and spice kitchens for Indian buyers now sit on backlogs of unsold inventory.

One builder, Tradition Homes, saw South Asian buyers drop from 70% of sales to below 30%. A real estate agent in Frisco reports that his phone, once ringing with eager buyers, now rings with sellers desperate to cut losses. One client holds two properties worth over $1 million each and is weighing a move back to India. Another financed an $800,000 home almost entirely with debt — the property is now underwater.

## What Comes Next

The CFPB's statement is technically guidance, not regulation. It does not carry the force of law, and it does not impose new rules. What it does is remind banks that existing law already permits — and may require — considering immigration status.

For risk-averse lenders, that reminder may be enough. Compliance departments tend to read federal guidance as direction, not suggestion. If a bank ignores this guidance and a borrower on a temporary visa defaults after losing status, the CFPB has effectively written the regulator's argument for the enforcement action.

Indian professionals weighing a home purchase in 2026 face a landscape that looks nothing like it did two years ago. The $100,000 H-1B petition fee has slowed new arrivals. The FHA ban has eliminated one mortgage pathway. The CFPB guidance may constrict others. And a proposed bill in Congress — the American White-Collar Worker Jobs Act — would shorten the H-1B from six years to two, compressing the timeline in which any lender could reasonably expect repayment.

The message from Washington is consistent, if unstated: if your right to stay is temporary, your ability to build wealth here should be treated as temporary too."""
    },

    # ── Article 2: Chip Roy dual intent bill ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Years and Out — The Bill That Would Kill the H-1B-to-Green-Card Pipeline for Good",
        "subheadline": "Chip Roy's American White-Collar Worker Jobs Act would end 'dual intent,' cut the H-1B to two years, and tell a million Indian professionals in the green card queue that the wait was always going to end this way.",
        "slug": make_slug("chip-roy-dual-intent-h1b-two-years-green-card-kill"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the estimated 1.2 million Indian nationals in the employment-based green card backlog — many with EB-2 priority dates stuck at July 2014 — this bill would be existential. The entire architecture of their American life depends on dual intent: the legal fiction that you can be a temporary worker while simultaneously pursuing permanent residency. Remove it, and the green card queue becomes a line to nowhere.",
        "tags": ["h1b", "green-card", "dual-intent", "chip-roy", "immigration-reform"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-seeks-to-end-green-card-pathway/article71068304.ece"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/05/chip-roy-targets-egregious-h1b-abuses-protecting-white-collar-jobs/"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Chip_Roy_118th_Congress.jpg/330px-Chip_Roy_118th_Congress.jpg",
        "image_caption": "Congressman Chip Roy (R-TX), sponsor of the American White-Collar Worker Jobs Act",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For nearly four decades, the H-1B visa has operated on a convenient ambiguity. You arrive as a temporary worker. You file for a green card through your employer. You wait — in India's case, you wait for a decade or more — while renewing your H-1B in three-year increments. The law calls this "dual intent," and it has been the scaffolding on which hundreds of thousands of Indian professionals have built careers, bought homes, raised American-born children, and waited.

Congressman Chip Roy wants to tear that scaffolding down.

The American White-Collar Worker Jobs Act, which Roy formally introduced last week with co-sponsor Eli Crane of Arizona, would eliminate dual intent from the H-1B program entirely. Under the bill, H-1B applicants would be required to demonstrate that they maintain a residence abroad and do not intend to abandon it — a requirement that mirrors tourist and student visas but has never applied to H-1B holders.

The provision is buried in a bill that has drawn attention for other reasons: replacing the H-1B lottery with a wage-based selection system, requiring employers to prove they tried to hire American workers first, and abolishing the Optional Practical Training program for foreign graduates. But for Indians already in the United States, the dual intent provision is the one that would restructure their lives.

## What Dual Intent Actually Does

Dual intent is not a loophole. It is a deliberate feature of the Immigration and Nationality Act, established to allow temporary workers to pursue permanent residency without the legal contradiction that would otherwise arise: if you must prove you intend to leave, you cannot simultaneously apply to stay.

For Indian professionals, dual intent is not an abstract legal concept. It is the mechanism that lets someone file a PERM labor certification, wait for an I-140 approval, file an I-485 adjustment of status application, and renew their H-1B indefinitely while the green card queue inches forward. Remove dual intent, and every step of that process collapses.

An H-1B holder who "maintains a residence abroad and does not intend to abandon it" cannot, by definition, file for adjustment of status. They cannot credibly claim to seek permanent residency while simultaneously swearing they plan to leave. The bill does not merely slow the green card pipeline for H-1B holders. It dynamites it.

## The Two-Year Cap

Roy's bill compounds the dual intent elimination with a second structural change: cutting the maximum H-1B duration from six years to two. Under current law, an H-1B is initially granted for three years and can be extended for another three. Beyond that, holders whose green card petitions have been pending for more than a year can receive one-year extensions indefinitely under the American Competitiveness in the Twenty-First Century Act.

The bill would repeal those extension provisions. Two years. No renewals tied to green card processing.

For context: the median time from H-1B arrival to green card approval for an Indian EB-2 applicant is currently estimated at 12 to 15 years. The June 2026 Visa Bulletin has the EB-2 India Final Action Date at July 15, 2014. The math is not subtle. A two-year H-1B with no extensions and no green card pathway means most Indian professionals would arrive, work for 24 months, and leave.

## Who Supports It

The bill is backed by US Tech Workers, the Immigration Accountability Project, and the Federation for American Immigration Reform — organizations that have long argued the H-1B program suppresses wages for American STEM workers.

"The bill will effectively address many of the egregious aspects of the H-1B visa programme that have not merely encouraged but enabled corporations, universities, and NGOs to displace our most productive workers with cheaper and more quiescent foreigners," said Kevin Lynn, president of US Tech Workers.

Crane, the Arizona co-sponsor, framed it in generational terms: "Congress should be doing everything in our power to prioritise our own citizens rather than facilitating their displacement."

Roy himself is retiring from Congress after losing a primary for Texas attorney general to fellow Republican Mayes Middleton. The bill reads like a parting shot — sweeping enough to reshape the entire skilled immigration system, introduced by a lawmaker with no political future to protect.

## The Odds

Previous attempts to overhaul the H-1B program through legislation have consistently failed. The tech industry lobbies aggressively to protect the program, and Congress has historically preferred to let the executive branch make incremental changes through regulation rather than take politically risky votes on immigration.

But the legislative environment has shifted. The Trump administration has already imposed a $100,000 fee on new H-1B petitions, implemented a wage-weighted lottery that favors higher-paid applicants, and directed agencies to restrict adjustment of status through the PM-602 memo. The Brookings Institution reported this week that only about 85 companies have paid the new fee, and that the FY2027 H-1B cap was hit in just 25 days — suggesting the program's economics are already changing.

Roy's bill pushes further than any executive action has gone. Whether it passes is almost beside the point. Its provisions — dual intent elimination, two-year caps, OPT abolishment — represent the outer boundary of what restrictionists want. And in a Congress that has already funded $70 billion in immigration enforcement, that boundary may be closer to the center than it used to be.

## What It Means for You

If you are an Indian professional on an H-1B with a pending green card application, this bill would not affect you tomorrow. It is a proposal, not a law. But it signals where the political energy is moving.

The combination of executive action and legislative pressure is systematically dismantling the assumption that an H-1B is a stepping stone to permanent residency. The $100,000 fee makes it harder to get in. The wage-weighted lottery makes it harder to get selected. The PM-602 memo makes adjustment of status harder to complete. And now a bill would eliminate the legal doctrine that makes the entire sequence possible.

For the million-plus Indians in the green card queue, the question is no longer how long the wait will be. It is whether the line still leads anywhere."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
