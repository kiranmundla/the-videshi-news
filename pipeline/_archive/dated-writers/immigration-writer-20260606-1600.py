#!/usr/bin/env python3
"""Immigration writer — 2026-06-06 16:00 UTC batch"""

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
    # ── ARTICLE 1: July 10 Signature Rule ──
    {
        "id": str(uuid.uuid4()),
        "headline": "One Wrong Signature and Your H-1B Is Dead — The July 10 Rule USCIS Hopes You Haven't Read",
        "subheadline": "Starting next month, a scanned signature or a missing ink mark on your petition could trigger an outright denial — no second chances, no Request for Evidence, no cure.",
        "slug": make_slug("july-10-uscis-signature-rule-h1b-denial-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals file the majority of H-1B petitions and are disproportionately exposed to procedural denials under the new rule.",
        "tags": ["h1b", "uscis", "signature-rule", "immigration", "july-2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/state-dept-official-says-h-1b-visa-rules-are-global-not-targeted-at-india/"},
            {"name": "Ahluwalia Law Offices", "url": "https://www.ahluwalialaw.com/blog/uscis-wet-signature-policy-avoiding-rejections-rfes/"},
            {"name": "USCIS Newsroom", "url": "https://www.uscis.gov/newsroom"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7567551/pexels-photo-7567551.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand signing an official document with a pen",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, a scanned signature on an H-1B petition was a minor annoyance — the kind of thing that might trigger a Request for Evidence, cost your employer a few weeks, and resolve itself with a fresh ink copy sent by FedEx. Starting July 10, 2026, it could end your case entirely.

U.S. Citizenship and Immigration Services is tightening its signature requirements for all benefit filings, including H-1B petitions and green card applications. Under the new policy, officers will have broader authority to deny submissions outright if they carry what USCIS considers a "deficient" signature — meaning anything that isn't a handwritten ink mark or a specifically authorized electronic signature.

## What changed

The shift was buried in a broader policy update that took effect earlier this year but carries a hard compliance deadline of July 10, 2026, for all petitions filed on or after that date. USCIS had previously maintained pandemic-era flexibility, accepting reproduced, faxed, and photocopied signatures on immigration forms. That flexibility is ending.

The new regime eliminates the safety net that existed for procedural mistakes. Where USCIS once issued a Request for Evidence — giving petitioners a chance to cure a signature deficiency — the agency now reserves the right to deny the petition without further notice. No RFE, no Notice of Intent to Deny. Just a rejection, a lost filing fee, and the need to start over.

Immigration attorneys have already flagged the change as a quiet escalation. "Minor clerical errors that once might have led to a Request for Evidence now face a greater risk of immediate denial, raising the cost of mistakes in already expensive filings," noted VisaVerge in its analysis of the policy shift.

## The math for Indian workers

Indian nationals account for roughly three-quarters of all H-1B visas approved in a typical fiscal year, according to Pew Research Center data. That concentration means any procedural tightening hits the Indian community hardest by sheer volume.

Consider the filing costs already in play: the base I-129 petition fee, the $100,000 proclamation fee for new H-1B entries introduced last year, and — for those who need speed — a premium processing fee that rose to $2,965 as of March 1, 2026. A denial on signature grounds means all of that is forfeited. The employer must refile from scratch, pay again, and hope the position hasn't been filled or eliminated in the interim.

For workers already in the United States on H-1B status, the stakes are higher still. A denied extension petition can trigger a gap in authorized employment, potentially starting the 60-day grace period clock that forces workers to either find a new sponsor or leave the country.

## What qualifies as a valid signature

Under the updated policy, USCIS requires one of two things: a handwritten ink signature on the original form, or an electronic signature through a USCIS-authorized platform. Scanned copies of handwritten signatures — the workaround that became standard practice during COVID-19 — are no longer guaranteed to be accepted.

The policy manual still technically permits reproduced signatures, but the practical enforcement has diverged sharply from the written text. Immigration lawyers report a pattern of RFEs and rejections at USCIS lockbox facilities, particularly during high-volume H-1B filing seasons. The July 10 deadline formalizes what has been happening informally for months.

Employers filing multiple petitions face particular risk. Large firms that process H-1B paperwork through centralized HR departments — often coordinating signatures across time zones between beneficiaries abroad and company officers in the United States — will need to overhaul their workflows. A signature collected digitally in Hyderabad and pasted into a form printed in Dallas may no longer pass muster.

## The bigger picture

The signature rule doesn't operate in isolation. It arrives alongside the salary-weighted H-1B lottery (effective since February 27, 2026), the $100,000 fee on new petitions, and the May 21, 2026, policy memorandum (PM-602-0199) that reframed adjustment of status as "discretionary grace" rather than an entitlement.

Together, these changes raise the procedural and financial bar for every stage of the H-1B lifecycle. The signature requirement may look like a technicality, but it functions as a compliance filter: one more point at which a petition can fail before USCIS ever reaches the substance of the case.

For the hundreds of thousands of Indian professionals navigating this system — and the employers who depend on them — the message from USCIS is clear: the era of administrative forgiveness is over. Starting July 10, the ink on the page matters as much as the merit of the petition."""
    },

    # ── ARTICLE 2: India-US Trade Deal and Immigration ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Ninety-Nine Percent Done — The India-US Trade Deal That Hasn't Solved the Immigration Problem",
        "subheadline": "India and the United States are weeks from signing a historic trade pact worth $220 billion in bilateral commerce. The one issue neither side wants to put on the table: what happens to 1.2 million Indians waiting for a green card.",
        "slug": make_slug("india-us-trade-deal-immigration-elephant-room-goyal"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals in the US are caught between two governments negotiating billions in trade while treating immigration as a separate — and unsolved — problem.",
        "tags": ["india-us-trade", "immigration", "green-card-backlog", "h1b", "piyush-goyal"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/first-tranche-us-india-trade-deal-likely-by-mid-july-says-india-trade-minister-2026-06-06/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/international-trade/india-us-may-execute-interim-trade-pact-by-july-minister-says"},
            {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/business/india-us-trade-deal-almost-done/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/state-dept-official-says-h-1b-visa-rules-are-global-not-targeted-at-india/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "India's Commerce Minister Piyush Goyal, who said the first tranche of the trade deal should be executed by mid-July",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """A high-level American trade delegation wrapped up four days of negotiations in New Delhi on June 4, led by chief negotiator Brendan Lynch. India's Commerce Minister Piyush Goyal told reporters on Friday that the first tranche of a bilateral trade agreement should be ready "by the middle of next month." U.S. Ambassador Sergio Gor went further, calling the deal "99 percent complete."

The numbers are impressive. Bilateral trade in goods and services has grown from $20 billion to over $220 billion in two decades. The interim agreement is expected to cover market access, customs facilitation, investment promotion, and economic security alignment. Both sides describe it as the foundation for a comprehensive Bilateral Trade Agreement that would reshape the economic relationship for years to come.

Missing from every press conference and every joint statement is the word that haunts roughly 1.2 million Indian nationals in the American immigration queue: visas.

## Trade talks, immigration silence

The diplomatic choreography is deliberate. The State Department sent Senior Official Andrew Pigott to a New York roundtable on June 5 — one day after the trade delegation left Delhi — to insist that U.S. visa laws "do not target India" and are "global visa laws being implemented with clarity." He did not mention the trade talks. The trade negotiators did not mention visas.

But the two issues are inseparable for the people caught in between. The same week Goyal was declaring the trade deal nearly done, DHS Secretary Markwayne Mullin told the Senate that 286,000 people had applied for H-1B visas in fiscal year 2026 and that more than 200,000 of them had paid the new $100,000 fee. The wage-weighted lottery, the PM-602 memo reframing adjustment of status as "discretionary grace," and the July 10 signature tightening — all of these changes landed during the same months that trade negotiators were exchanging drafts in Washington and Delhi.

India has historically resisted linking trade and immigration in formal negotiations, treating them as separate tracks. The United States has done the same, though for different reasons: immigration policy sits with Congress and the executive branch, not trade negotiators. The result is a structural blind spot. A deal that liberalizes goods and investment flows between two countries while the people who would execute that trade face a decade-long green card backlog.

## What the deal covers — and what it doesn't

The interim agreement, based on the February 7, 2026, joint statement framework, focuses on tariff reduction, non-tariff barriers, and customs streamlining. India is expected to gain preferential access over competitors in certain U.S. markets. In return, Washington wants lower barriers for American agricultural products and services.

What the deal does not cover: H-1B visa allocations, per-country green card caps, the $100,000 fee, or any pathway to clearing the employment-based backlog. These remain firmly outside the trade framework, governed by separate legislative and regulatory processes that show no sign of convergence.

For Indian professionals working in the United States, this creates a paradox. Their labor is essential to the industries — technology, healthcare, finance — that generate the trade volumes both governments are eager to celebrate. Yet the legal infrastructure governing their presence remains hostile: EB-2 India's priority date sits at July 15, 2014, meaning applicants filed more than a decade ago are only now reaching the front of the line. EB-3 India is even further back, at November 15, 2013.

## The diaspora's unasked question

Every trade deal comes with winners and losers. Indian exporters stand to benefit from reduced tariffs. American farmers may gain access to a market of 1.4 billion consumers. But the 600,000-odd Indian-born professionals in the United States who are simultaneously paying $100,000 visa fees, navigating a discretionary adjustment process, and watching their green card dates crawl forward by weeks per year — they are not at the table.

The trade deal, if signed by mid-July as Goyal projects, will be framed as a triumph of economic diplomacy. Both governments will claim credit. Neither will mention that the people who build the software, staff the hospitals, and manage the supply chains that make bilateral trade work are still waiting — some of them for longer than the entire negotiation has lasted.

Ambassador Gor called the remaining 1 percent of the deal the hardest part. For the Indian diaspora, the hardest part isn't the last 1 percent of a trade agreement. It's the 100 percent of an immigration system that no trade deal has ever been designed to fix."""
    },

    # ── ARTICLE 3: $100K Fee Senate Hearing — Rural America Impact ──
    {
        "id": str(uuid.uuid4()),
        "headline": "A Hospital in Maine Paid $100,000 for a Surgeon — Now Senators Want Exemptions to the H-1B Fee",
        "subheadline": "DHS Secretary Mullin told the Senate that 200,000 applicants paid the fee willingly. Senator Collins asked him to consider whether a rural hospital recruiting a single doctor should bear the same cost as a tech giant hiring hundreds.",
        "slug": make_slug("senate-hearing-100k-h1b-fee-rural-hospital-exemption"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-born doctors and educators serving underserved American communities are being priced out by a fee designed to curb Big Tech outsourcing.",
        "tags": ["h1b", "100k-fee", "rural-healthcare", "senate-hearing", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AviationA2Z", "url": "https://aviationa2z.com/index.php/2026/06/04/dhs-reveals-massive-demand-for-h-1b-visas-despite-100000-fee/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/state-dept-official-says-h-1b-visa-rules-are-global-not-targeted-at-india/"},
            {"name": "Dickinson Wright", "url": "https://immigration.dickinson-wright.com/2026-h-1b-employer-punch-list/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg/3840px-DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg",
        "image_caption": "DHS Secretary Markwayne Mullin testified before the Senate on H-1B demand and the $100,000 fee",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The number DHS Secretary Markwayne Mullin delivered to the Senate Appropriations Subcommittee on Homeland Security was designed to sound like a success story: 286,000 H-1B applications received so far in fiscal year 2026, with more than 200,000 applicants voluntarily paying the $100,000 fee that President Trump imposed last September.

"Over two lakh applicants chose to pay the $100,000 fee for their H-1B visas to work in the United States during the fiscal year 2026," Mullin told lawmakers on June 2. The math works out to more than $20 billion in fee revenue from a single visa category — a windfall that the administration frames as proof the program still attracts top talent despite the higher price of entry.

But two senators from opposite ends of the country heard something different in those numbers.

## Collins and the surgeon

Senator Susan Collins of Maine described a hospital in her state that had paid the $100,000 fee to recruit a surgeon from abroad. The hospital serves a rural region with no other source of surgical care within reasonable distance. The fee, Collins argued, represents a catastrophic financial burden for a small healthcare provider — one that absorbs it not because the position is low-value, but because there is literally no American applicant willing to relocate to rural Maine for the salary a community hospital can offer.

Collins urged DHS to consider exemptions for medical professionals who fill critical workforce gaps in underserved areas. The argument was not about opposing the fee in principle but about recognizing that a one-size-fits-all charge designed to deter outsourcing firms in Dallas and Hyderabad operates very differently when applied to a 50-bed hospital in Aroostook County.

## Murkowski and the teachers

Senator Lisa Murkowski of Alaska extended the argument to education. Rural school districts in Alaska face chronic teacher shortages, and some have turned to the H-1B program to recruit math and science teachers from abroad. The $100,000 fee makes that recruitment functionally impossible for public school systems operating on state funding.

Murkowski asked whether similar carve-outs could apply to educational institutions. Both she and Collins were making the same structural point: the fee was designed to filter out employers using the H-1B program for high-volume, lower-wage staffing. It is instead filtering out the employers least able to absorb an arbitrary six-figure surcharge.

## Mullin's response

The DHS secretary acknowledged both concerns and said the department would "examine potential solutions" and "explore ways to provide greater flexibility in specific cases where public needs are particularly urgent." He stopped short of committing to exemptions, regulatory action, or a timeline.

That language — examine, explore, consider — is the vocabulary of an administration that understands the political problem but has no mechanism to fix it without walking back a policy it championed. The $100,000 fee was introduced via presidential proclamation, not legislation, which means it can be modified by executive action. But any carve-out risks undermining the administration's message that the fee exists to protect American workers from wage suppression.

## Where Indian professionals fit

Indian-born workers make up roughly 75 percent of H-1B visa recipients in a typical year. They are also disproportionately represented in exactly the professions Collins and Murkowski described: healthcare and education in underserved communities.

Data from the Association of American Medical Colleges shows that international medical graduates — a substantial proportion of whom are Indian — fill nearly a quarter of residency positions in the United States. In rural hospitals, that share is significantly higher. The same pattern holds in STEM education, where H-1B teachers often serve in districts that cannot compete for domestic talent.

The $100,000 fee does not distinguish between an outsourcing firm placing a junior software developer at a client site and a rural hospital hiring its only cardiologist. Both pay the same amount. The outsourcing firm spreads the cost across hundreds of petitions and absorbs it as an operating expense. The hospital pays it once and feels it for years.

## The revenue question

Mullin's testimony inadvertently surfaced a tension at the heart of the policy. If 200,000 applicants paid $100,000 each, the program generated roughly $20 billion in revenue during a single fiscal year. That revenue now funds DHS operations, processing infrastructure, and enforcement — creating an institutional incentive to keep the fee in place regardless of its distributional effects.

Exemptions for healthcare and education would reduce that revenue stream. They would also require USCIS to create new adjudication categories, verification procedures, and compliance frameworks — adding bureaucratic complexity to a system already struggling with seven-and-a-half-month standard processing times.

The senators' questions on June 2 were the first public indication that members of Congress are ready to push for carve-outs. Whether DHS acts on its own or waits for legislation will determine how long rural hospitals and school districts continue paying a fee that was never meant for them — and how long the Indian doctors and teachers who serve those communities continue to be collateral damage in a policy fight about Big Tech."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
