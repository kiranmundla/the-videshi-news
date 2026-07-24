#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

body1 = """The cheapest way for an American company to hire a freshly minted master's graduate is, often, to hire one who isn't American. That is not an accident of the market. It is written into the tax code, and a cluster of bills now moving through Congress wants to delete it.

At the centre sits the Optional Practical Training programme, the bridge that lets foreign students on F-1 visas work for a year after graduation — three years for those with STEM degrees. For the roughly 35% of OPT participants who are Indian, the largest single nationality in the programme, it is the indispensable runway between a US degree and an H-1B. And for the employers who hire them, it comes with a quiet discount: neither the worker nor the company pays FICA, the 15.3% payroll tax that funds Social Security and Medicare.

## A 15.3% wedge

The exemption is old and, on its own terms, mundane. Students on campus jobs are exempt too. But critics have seized on what happens after graduation, when an OPT worker can spend up to three years in a full-time off-campus job while their American classmate's employer is writing FICA cheques from day one. The Center for Immigration Studies pegs the annual cost of the exemption at around $4 billion. A more recent analysis from the Institute for Progress estimates that ending it would raise $27–36 billion over a decade, with a central figure of $32 billion.

Senator Tom Cotton turned that arithmetic into legislation. His OPT Fair Tax Act (S.2940), introduced on 30 September 2025 and referred to the Senate Finance Committee, would strip the exemption and require both OPT workers and their employers to pay FICA at the standard rate. "Our tax code shouldn't incentivize businesses to hire foreign workers," Cotton said in announcing the bill.

A blunter companion measure waits in the House. The Fairness for High-Skilled Americans Act (H.R.2315), introduced by Representative Paul Gosar and a roster of hardline co-sponsors, would not tax OPT — it would abolish it outright, barring work authorisation for F-1 graduates unless Congress passes a future law expressly reviving it.

## Why this lands on Indian families first

Run the numbers from a graduate's side of the table. An Indian student finishing a US master's in computer science — the single most common OPT profile, as nearly a third of 2024 participants majored in CS — might earn $90,000 in a first STEM-OPT job. A FICA bill would carve roughly $6,885 a year from that paycheque, with the employer matching it. Over a three-year STEM-OPT window, the worker's share alone approaches $21,000, money that today stays in the bank account of someone who, by definition, cannot yet vote and may never qualify for the Social Security benefits the tax funds.

That last point is the bitter twist. An OPT worker who loses the H-1B lottery three times and goes home will have paid into Social Security and collected nothing. The exemption, for all the "corporate welfare" framing around it, was partly a recognition that taxing people for a retirement system they will likely never draw on is its own kind of unfairness.

The employer side matters too, because it shapes who gets hired. The companies that lean hardest on OPT labour are the same names that dominate Indian diaspora career aspirations — Amazon, Google, Microsoft, Meta, and the big university systems. Strip the discount and the marginal calculation that nudges a recruiter toward an international candidate flattens. In a labour market already bruised by AI-driven white-collar layoffs, removing even a small cost advantage could push hiring decisions toward domestic graduates at the margin.

## The odds, and the timing

Neither bill has moved past committee. S.2940 sits in Finance; H.R.2315 in House Judiciary. In an ordinary year, that is where such measures quietly die. But this is not an ordinary year for high-skilled immigration. The exemption fight rides alongside a $100,000 H-1B petition fee, a proposed end to the open-ended student-visa duration, and an administration openly hostile to what it calls the "student-visa-to-guestworker pipeline." A revenue-raising tax change is also exactly the kind of provision that can be folded into a larger budget bill, where it needs no standalone vote.

For Indian students weighing a US degree in 2026, the message is to model the downside. The sticker price of an American master's no longer ends at tuition. It may soon include a payroll tax on the very work authorisation that made the degree worth buying — and, in the harsher version, the loss of that work authorisation altogether.

**Sources:** Congress.gov (S.2940, H.R.2315); Senator Tom Cotton press office; Institute for Progress; Center for Immigration Studies; Niskanen Center."""

body2 = """For most of its history, the H-1B programme has been policed lightly. Employers filed their paperwork, attested that they were paying the prevailing wage, and were rarely audited unless a disgruntled worker filed a complaint. That era is ending. Over the past nine months Washington has quietly assembled the plumbing for systematic, data-driven enforcement — and the firms most exposed are the Indian and Indian-American IT companies that file the largest volumes of petitions.

## From paperwork to pipeline

The shift has three moving parts. First came Project Firewall, the Department of Labor initiative announced in September 2025 that, for the first time, lets the Secretary of Labor personally initiate H-1B investigations — a sweeping authority that exists in statute but that no previous Secretary had ever exercised. It expands data sharing between Labor, Homeland Security, and State; permits employer audits without a worker complaint; and allows debarment of up to several years on top of civil penalties and back-wage orders.

Then came the connective tissue. The Department of Labor and DHS, acting through USCIS, signed a Memorandum of Agreement establishing a formal process by which USCIS refers suspected H-1B violations it spots while adjudicating petitions straight to the Department of Labor — "a source of information never previously accessed by the Department for enforcement purposes." In plain terms: the agency that approves your petition now feeds the agency that can investigate you.

The third piece arrived this week. On 22 June the President signed an executive order directing federal agencies to review their contractors' and subcontractors' use of foreign workers and any offshoring of jobs, with 120 days to report to the Office of Management and Budget. It also instructs Labor and DHS to tighten protections for US workers at H-1B job sites — including third-party placement sites, the staffing model that defines much of the Indian IT services industry.

## Why the staffing model is the bullseye

The mechanics matter. Many Indian-origin IT firms place H-1B workers not at their own offices but at client worksites — a bank, a retailer, an insurer. Long-anticipated rules would require the H-1B employer and the end client to jointly obtain the labor condition application, creating what immigration lawyers call de facto joint-employer liability. The client would suddenly share responsibility for H-1B wage and working-condition compliance, a legal exposure most corporate buyers of IT services have no appetite for.

That single change could reprice the entire body-shopping economy. If a US bank must take on compliance liability to keep an offshore-staffing contractor's H-1B workers on site, the easier path is to stop. The work either goes to a US worker or, more likely, migrates to an offshore delivery centre in Bengaluru or Hyderabad — which is precisely the reverse-migration trend already visible in India's booming global capability centres.

## What it means for the diaspora worker

For an individual Indian professional on an H-1B, heightened enforcement cuts both ways. Genuine compliance — being paid the actual prevailing wage, working the role and location on the petition — has never been more protective. The workers most at risk are those whose employers have been gaming the system: benching them between projects without pay, underpaying against the LCA, or placing them at sites never disclosed to the government. When an audit lands, it is often the worker, not just the employer, whose status unravels.

There is a quieter risk too. As referrals and audits multiply, processing slows and requests for evidence proliferate. A programme already reshaped this year by a $100,000 petition fee and a new wage-weighted lottery is now layering on an enforcement regime that makes every filing slower and every employer more cautious. For the smaller consultancies that have historically been the entry point for new Indian graduates, that caution can mean simply filing fewer petitions.

The political framing is "protecting American workers." The practical effect is a programme that increasingly rewards large, deep-pocketed, compliant employers and squeezes out the staffing intermediaries that built the Indian-American tech footprint over three decades. For a diaspora that has long treated the H-1B as a meritocratic ladder, the lesson of 2026 is that the ladder now comes with inspectors — and they have your petition data.

**Sources:** U.S. Department of Labor (Project Firewall; DOL–DHS Memorandum of Agreement); Fragomen immigration alert; Holland & Knight; Lexology H-1B enforcement analysis."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Tax Break That Makes Indian Grads Cheaper to Hire Is in Congress's Crosshairs",
        "subheadline": "Bills to end the OPT payroll-tax exemption — or scrap the programme entirely — would hit Indian students, the largest group on F-1 work authorisation, first and hardest.",
        "slug": make_slug("opt-fica-tax-exemption-cotton-fair-tax-act-indian-students-stem"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest nationality on OPT, so ending the payroll-tax exemption — or the programme itself — would directly raise the cost and lower the odds of the post-degree work runway that most Indian students depend on to reach an H-1B.",
        "tags": ["opt", "stem-opt", "f1-visa", "fica-tax", "indian-students", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Congress.gov — S.2940 OPT Fair Tax Act", "url": "https://www.congress.gov/bill/119th-congress/senate-bill/2940"},
            {"name": "Congress.gov — H.R.2315 Fairness for High-Skilled Americans Act", "url": "https://www.congress.gov/bill/119th-congress/house-bill/2315"},
            {"name": "Senator Tom Cotton — press release", "url": "https://www.cotton.senate.gov/news/press-releases/cotton-introduces-bill-to-end-tax-exemptions-for-foreign-workers"},
            {"name": "Institute for Progress — The Cost of the OPT FICA Exemption", "url": "https://ifp.org/the-cost-of-the-opt-fica-exemption/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31128500/pexels-photo-31128500.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students at a US university graduation ceremony, the gateway to OPT work authorisation",
        "image_attribution": "Pexels",
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Just Built a Machine to Audit H-1B Employers. Indian IT Firms Are the Target",
        "subheadline": "Project Firewall, a new data-sharing pact between Labor and USCIS, and a June 22 executive order together turn H-1B oversight from light-touch to systematic — and the staffing model many Indian firms use is the bullseye.",
        "slug": make_slug("h1b-enforcement-project-firewall-dol-dhs-moa-indian-it-staffing-audits"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian and Indian-American IT firms file the most H-1B petitions and rely on third-party worksite placement, the exact model the new enforcement regime is designed to scrutinise — putting both the companies and the diaspora workers they sponsor at heightened risk.",
        "tags": ["h1b", "project-firewall", "dol", "uscis", "enforcement", "indian-it", "lca"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Department of Labor — Project Firewall", "url": "https://www.dol.gov/newsroom/releases/osec/osec20250919"},
            {"name": "U.S. Department of Labor — DOL–DHS Memorandum of Agreement", "url": "https://www.dol.gov/newsroom/releases/eta/eta20250919"},
            {"name": "Fragomen — Trump Orders Review of Foreign Hiring by Federal Contractors", "url": "https://www.fragomen.com/insights/president-trump-orders-review-of-foreign-hiring-by-federal-contractors-directs-dhs-and-dol-to-increase-scrutiny-of-h-1b-program.html"},
            {"name": "Holland & Knight — Summary of Presidential Proclamation on Nonimmigrant Workers", "url": "https://www.hklaw.com/en/insights/publications/2025/09/summary-of-presidential-proclamation-restriction-on-entry"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061944/pexels-photo-8061944.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US visa and passport documents, central to H-1B petition compliance now under tighter federal scrutiny",
        "image_attribution": "Pexels",
        "body": body2,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
