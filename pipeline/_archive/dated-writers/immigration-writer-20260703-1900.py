#!/usr/bin/env python3
"""Immigration writer — 2026-07-03 19:00 PT run."""
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

# ─── ARTICLE 1 ───────────────────────────────────────────────
art1_body = """Dozens of Democratic lawmakers sent a pointed letter to USCIS Director Joseph Edlow on July 3, demanding that the agency withdraw its May 21 policy memorandum redefining adjustment of status as an "extraordinary form of relief." The pushback, led by Senators Alex Padilla and Dick Durbin alongside Representatives Jamie Raskin and Pramila Jayapal, marks the most organised Congressional resistance yet to the Trump administration's quiet rewriting of the green card process.

## What the memo actually does

The May 21 memorandum instructs USCIS adjudicators to treat in-country green card processing — known as adjustment of status, or AOS — as a discretionary privilege rather than a standard pathway. Under the new framework, applicants must demonstrate that their continued presence in the United States serves the "national interest" or provides an "economic benefit." Neither term appears in the Immigration and Nationality Act, and the memo provides no guidance on how officers should apply them.

In practical terms, the policy steers applicants toward consular processing abroad — flying to a US embassy overseas to complete their green card interview. For an Indian engineer in Silicon Valley with a pending EB-2 petition, that could mean returning to India for an appointment at a consulate already managing a years-long backlog.

## The Democrats' argument

The lawmakers' letter does not mince words. "This is simply incorrect," they wrote of the memorandum's assertion that AOS is "administrative grace." They pointed to the Immigration and Nationality Act of 1952, which established adjustment of status precisely because Congress recognised that many eligible immigrants already lived in the country and should not be forced to leave it.

The letter raises nine specific questions, including whether the policy has an effective date (no one seems to know), how "national interest" will be defined (USCIS has not said), whether adjudicators have received training (unclear), and whether the State Department was consulted before the memo issued (apparently not).

The Democrats also noted a practical absurdity: pushing more applicants to overseas consulates would increase demand at posts that already cannot keep pace. Wait times for immigrant visa interviews at US embassies in India regularly stretch beyond a year. Forcing applicants out of the country to process their cases would separate them from spouses, children, and employers for months or longer.

## Why this cuts deeper for Indians

Indian nationals are the single largest group of employment-based green card applicants. The EB-2 India category went "unavailable" in the July 2026 visa bulletin — no new green cards until at least October. For Indians already in the adjustment pipeline, the memo introduces a new source of uncertainty: even if your priority date becomes current, an adjudicator could now exercise "discretion" to deny your in-country application and tell you to process at a consulate instead.

The risk is not theoretical. Immigration attorneys have already reported cases where USCIS officers have cited the memo to request additional evidence or issue administrative holds on pending AOS applications. Combined with the agency's 11-million-case backlog and processing freezes across multiple service centres, the memo effectively creates a second filter — one with no statutory basis — between an Indian applicant and a green card.

Jayapal, herself a naturalised citizen born in Chennai, called the policy "an attack on families who followed every rule and played by the system's terms." Whether the letter moves USCIS to withdraw the memo remains to be seen. The agency has not publicly responded.

## What to watch

The nine questions in the letter carry a deadline — Democrats have asked for a response within 30 days. If USCIS fails to answer or doubles down, the issue could escalate through oversight hearings or litigation. Several immigration advocacy groups, including the American Immigration Lawyers Association, have already signalled that the memo may be vulnerable to an Administrative Procedure Act challenge for bypassing notice-and-comment rulemaking.

For now, Indian applicants with pending AOS cases should consult their attorneys about whether their filings could be affected — particularly those in employment-based categories where consular processing abroad would restart wait times from scratch."""

art2_body = """In the six months since President Trump's second inauguration, Republican lawmakers have introduced at least four separate bills targeting the H-1B visa programme. Taken individually, each is a long-shot piece of legislation unlikely to pass a divided Congress. Taken together, they represent the most sustained legislative assault on skilled-worker immigration in the programme's four-decade history — and every one of them would hit Indian professionals hardest.

## The bills

**The American White-Collar Worker Jobs Act of 2026** (Rep. Chip Roy, R-TX) is the most comprehensive. It would replace the H-1B lottery with a wage-based selection system, require employers to demonstrate "good-faith efforts" to hire American workers before filing a petition, and bar companies that have conducted recent layoffs from sponsoring H-1B workers. It would also end the Optional Practical Training programme entirely, cutting off the post-graduation work pathway that roughly 200,000 international students — a disproportionate number of them Indian — use each year. Perhaps most consequentially, it would sever the link between H-1B status and permanent residency, eliminating the visa as a pathway to a green card.

**The End H-1B Visa Abuse Act of 2026** (Rep. Eli Crane, R-AZ) proposes a three-year moratorium on all new H-1B issuances, followed by a cap reduction from 85,000 to 25,000 annually. Visa holders would need to earn at least $200,000 per year and would be prohibited from bringing dependents to the United States.

**The End H-1B Now Act** (former Rep. Marjorie Taylor Greene, R-GA) seeks a decade-long phase-out, reducing the cap each year until it reaches zero, with an annual exemption of 10,000 visas reserved exclusively for medical professionals.

**The EXILE Act** (Rep. Greg Steube, R-FL) is the bluntest instrument: it would eliminate the programme outright by the following fiscal year.

## The 5 per cent rule

Roy's bill includes a provision that has received less attention but could be more immediately damaging than any lottery reform. It caps the percentage of a US employer's workforce that can hold H-1B or L-1 visas at 5 per cent. India's major IT services firms — Infosys, TCS, Wipro, HCLTech — have historically relied on the programme to staff American client sites. Although these companies have reduced their visa dependency in recent years (TCS chief K. Krithivasan has said the firm deploys "fewer people than the number of approvals each year"), a hard 5 per cent cap would fundamentally alter the staffing model that generates the majority of the Indian IT sector's $108 billion in US export revenues.

The bill also creates a private right of action: any American worker displaced by a non-immigrant visa holder could sue the employer in federal court. That provision alone would change the calculus for companies weighing H-1B sponsorship against the risk of litigation.

## The odds — and the signal

None of these bills has committee hearings scheduled. The End H-1B Now Act, introduced by a lawmaker who subsequently lost her seat, is effectively dormant. The EXILE Act is a single page of legislative text without co-sponsors. Even Roy's more detailed proposal would face resistance from the tech industry lobby and business-oriented Republicans who view skilled immigration as an economic asset.

But the signal matters more than the odds. The 37 per cent drop in fresh H-1B approvals in FY2026 and the new weighted lottery favouring higher-paid workers suggest the administration is already achieving through executive action what legislation has not yet delivered. The bills serve as markers — establishing a policy floor that makes each successive executive restriction look moderate by comparison.

For Indian professionals, the message is consistent across all four proposals: the era of the H-1B as a reliable path from an Indian university to an American career is ending. Whether it ends through legislation, executive fiat, or the compounding friction of higher fees, longer waits, and tighter scrutiny, the trajectory points in one direction.

## What to do

Indian workers on H-1B should assess their alternatives now, not when a bill reaches the floor. That means evaluating O-1 eligibility for those with demonstrable expertise, exploring EB-1A or NIW self-petitions for green card independence from an employer, and — for those early in their careers — weighing whether India's own GCC boom, which has created over 500,000 tech jobs, offers a more stable long-term bet than a programme that four members of Congress want to eliminate and none are willing to defend."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Forty Democrats Told USCIS to Reverse Its Green Card Memo. The Agency Has Not Responded",
        "subheadline": "A bipartisan letter led by Padilla, Durbin, Raskin and Jayapal challenges the May 21 policy redefining adjustment of status as 'extraordinary relief' — a shift that could force Indian applicants to process green cards from overseas.",
        "slug": make_slug("democrats-challenge-uscis-adjustment-of-status-memo-jayapal"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the largest group of employment-based green card applicants. The USCIS memo adds a new discretionary hurdle to in-country processing, potentially forcing applicants to return to India for consular interviews amid already severe backlogs.",
        "tags": ["adjustment-of-status", "green-card", "uscis", "jayapal", "padilla", "immigration-policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/democrats-challenge-green-card-policy-shift--20260703062103"},
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/key-immigration-updates-affecting-employment-visas-in-2026"},
            {"name": "USCIS Policy Manual", "url": "https://www.uscis.gov/policy-manual"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
        "image_caption": "The United States Capitol building at dusk in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Bills. One Target. Congress Is Coming for the H-1B Programme",
        "subheadline": "Republican lawmakers have introduced a flurry of legislation to gut, pause, or eliminate the H-1B visa. None is likely to pass — but together they are redrawing the boundaries of what is politically possible.",
        "slug": make_slug("four-bills-h1b-programme-congress-roy-crane-greene"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold roughly 71 per cent of all H-1B visas. Every one of these bills — from Roy's OPT elimination to Crane's $200K salary floor — would disproportionately affect Indian tech workers and the IT services firms that employ them.",
        "tags": ["h1b", "congress", "legislation", "opt", "indian-it", "chip-roy", "immigration-reform"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Rep. Chip Roy Press Release", "url": "https://roy.house.gov/media/press-releases/rep-roy-introduces-legislation-end-h-1b-abuse-protect-american-tech-workers"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/us-lawmakers-intensify-push-against-h-1b-visas-is-2026-its-death-knell-11749828966222.html"},
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/key-immigration-updates-affecting-employment-visas-in-2026"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The US Immigration and Customs Enforcement building in Washington, D.C.",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
