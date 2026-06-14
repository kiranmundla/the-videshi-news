#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "GIFT City Is No Longer a Policy Experiment. NRI Wealth Managers Are Starting to Notice.",
        "subheadline": "India's first international financial services centre has approved its inaugural family investment fund, drawn endorsements from Singapore's diplomats, and begun attracting Gulf-based NRI capital fleeing regional instability.",
        "slug": make_slug("gift-city-ifsc-nri-investment-wealth-management"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs managing wealth across multiple jurisdictions now have a credible India-linked alternative to Dubai and Singapore — one that offers tax advantages, lower costs, and direct access to Indian markets without the regulatory friction of onshore investing.",
        "tags": ["nri", "diaspora", "gift-city", "investment", "wealth-management", "ifsc", "finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bar and Bench", "url": "https://www.barandbench.com/view-point/gift-city-2026-indias-rising-magnet-for-nri-investments"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/some-lenders-hike-rates-fx-deposits-non-resident-indians-2026-06-10/"},
            {"name": "IFSCA", "url": "https://ifsca.gov.in/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5859962/pexels-photo-5859962.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Modern financial district skyline in India at dusk",
        "image_attribution": "Pexels",
        "body": """For years, GIFT City was the kind of project that drew nods at policy conferences and blank stares from wealth managers. A gleaming financial centre rising between Ahmedabad and Gandhinagar, it had ambition, tax incentives, and a regulatory framework that read well on paper. What it lacked was traction — the kind that comes when real money starts moving through real structures.

That is beginning to change. In April 2026, the International Financial Services Centres Authority approved the first Foreign Family Investment Fund under its 2025 regulations, a milestone that transforms GIFT City from an abstract opportunity into a jurisdiction where NRI family offices can actually park and manage capital. The approval was not merely symbolic. It validated a regulatory architecture that allows flexible wealth structuring — alternative investment funds, cross-border estate planning, succession vehicles — within a framework that is domestically aligned but globally oriented.

## The Gulf factor

The timing is not accidental. Geopolitical turbulence in the Middle East has quietly reshuffled how Gulf-based NRIs think about concentration risk. Dubai's structural advantages remain formidable — its infrastructure, liquidity, and network effects are decades ahead. But months of regional instability have reinforced an uncomfortable truth: keeping all your wealth domiciled in a single jurisdiction, however well-run, is a bet on geography as much as on governance.

GIFT City is not pitching itself as a Dubai replacement. The more honest framing — and the one gaining ground among NRI wealth advisors — is that it offers a complementary India-linked node in a multi-hub structure. Singapore for Asia-Pacific exposure, Dubai for the Gulf corridor, and now GIFT City for direct, tax-efficient access to Indian markets. The diversification logic is straightforward, even if the execution is still maturing.

## What the numbers say

The financial incentives are concrete. Entities registered in GIFT City's IFSC enjoy exemptions from securities transaction tax, certain capital gains benefits, and tax holidays that make the jurisdiction materially cheaper than onshore Indian alternatives. Operating costs are lower than Dubai or Singapore. For NRIs who have long complained about the regulatory friction of investing in India through NRE and NRO accounts — the paperwork, the FEMA compliance, the repatriation headaches — GIFT City offers a cleaner pathway.

Indian banks are playing their part. Following the Reserve Bank of India's decision in early June to absorb the full hedging cost for three-to-five-year non-resident deposits, several lenders hiked FCNR deposit rates by as much as 300 basis points. State Bank of India, HDFC Bank, and AU Small Finance Bank are now offering between 5.25% and 7.1% on dollar deposits — rates that make the India corridor genuinely competitive for NRI capital that might otherwise sit in lower-yielding Western accounts.

## Singapore takes notice

In May, Singapore's High Commissioner to India, Simon Wong, singled out GIFT City during a visit to Gujarat, highlighting increasing Singaporean investment and expressing optimism about its emergence as a hub for USD-INR bond issuance, international banking, and fintech innovation. When Singapore's diplomatic establishment starts name-checking a competing financial centre, the signal is worth reading carefully.

## The caveats

None of this means GIFT City has arrived. Liquidity across IFSC exchanges is improving but still trails mature markets by a wide margin. The ecosystem — banks, asset managers, insurers, fund administrators — is growing but remains thin compared to what Singapore or Dubai offer. Real estate opportunities in the zone are tied to how quickly the surrounding infrastructure scales, making them a long-term play rather than an immediate yield story.

The most honest assessment of GIFT City in mid-2026 is that it is developed enough to be credible but early enough to offer meaningful upside. For NRIs with a structured approach and a long investment horizon, the asymmetry is real: entering now means navigating an incomplete ecosystem, but also securing positioning before the crowd arrives. Waiting may bring maturity, but likely at the cost of the early-mover advantage that makes frontier jurisdictions interesting in the first place.

The question is no longer whether GIFT City will matter to NRI wealth planning. It already does. The question is whether it will matter enough, fast enough, to justify the capital commitments being asked of early participants. The answer to that is still being written — in Gujarat, one fund approval at a time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Few Dollars in His Pocket, Thirty-Five Years Later: Arvind Raman Now Runs America's Standards Agency",
        "subheadline": "The Indian-born engineer who arrived at Purdue with almost nothing has been confirmed by the U.S. Senate as director of the National Institute of Standards and Technology — and undersecretary of commerce.",
        "slug": make_slug("arvind-raman-nist-director-indian-american-purdue"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Raman's journey from India to the helm of NIST — the agency that sets America's technology standards — is a distilled version of the Indian immigrant arc: arrive with nothing, build a career through sheer competence, and end up shaping the infrastructure of the country that took you in.",
        "tags": ["nri", "diaspora", "indian-american", "nist", "arvind-raman", "leadership", "science"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Purdue University", "url": "https://www.purdue.edu/newsroom/releases/2025/Q2/raman-confirmed-as-u.s.-undersecretary-of-commerce-for-standards-and-technology-lundstrom-appointed-dean-of-engineering.html"},
            {"name": "Manufacturing Dive", "url": "https://www.manufacturingdive.com/news/senate-confirms-arvind-raman-nist-director/747123/"},
            {"name": "IANS via Suryaa", "url": "https://www.suryaa.com/176320-from-india-to-nist-raman-outlines-innovation-agenda.html"},
            {"name": "ASME", "url": "https://www.asme.org/topics-resources/content/trump-nominates-dr-arvind-raman-asme-fellow-to-lead-nist"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg/1280px-Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg",
        "image_caption": "Neil Armstrong Hall of Engineering at Purdue University, where Arvind Raman served as dean",
        "image_attribution": "Wikimedia Commons",
        "body": """When Arvind Raman appeared before the Senate Commerce Committee in March, he did not open with his CV. He opened with a memory. "I first came to the United States 35 years ago from India, actually to study engineering at Purdue University," he told the senators. "I only had a few dollars in my pocket at the time."

His first paycheque as a research assistant was weeks away. He survived on a university loan designed for students with no credit history and clothes from the local Goodwill store. "And today," he said, "I'm the dean of engineering at that great institution."

On 18 May, the Senate confirmed Raman as undersecretary of commerce for standards and technology and director of the National Institute of Standards and Technology — the 125-year-old agency that underpins everything from the precision of atomic clocks to the safety standards of American manufacturing. The vote was 46-45, part of a broader package of nominees that passed largely along party lines. He assumed the role on 1 June.

## The institution he inherits

NIST is not a household name, but its fingerprints are everywhere. The agency maintains the fundamental measurement standards that allow American industry to function — the reference clocks, the calibration protocols, the cybersecurity frameworks that Fortune 500 companies build their systems around. When your phone syncs its time, when a semiconductor fab calibrates its lithography tools, when a hospital verifies the dosage accuracy of a radiation machine, NIST's work is somewhere in the chain.

Raman inherits the agency at a moment when its mandate has never been broader. Artificial intelligence, quantum computing, advanced materials, semiconductor manufacturing — each of these domains requires the kind of measurement science and standardisation work that NIST was built to do. The CHIPS Act has funnelled billions into domestic semiconductor production, and NIST is central to ensuring those investments translate into globally competitive manufacturing.

## The Purdue years

Before Washington, Raman spent more than two decades at Purdue, rising from assistant professor to the John A. Edwardson Dean of the College of Engineering — one of the largest engineering programmes in the United States. His research focused on nonlinear mechanics at the nanoscale, work that earned him an ASME Fellowship and the Gustus L. Larson Memorial Award. He served as associate editor of the ASME Journal of Dynamic Systems, Measurements and Controls.

But his impact at Purdue extended well beyond the lab. Under his deanship, the college deepened its ties with industry — the kind of academic-corporate partnerships that produce both research breakthroughs and employable graduates. It is precisely this bridge-building instinct that his supporters say makes him suited for NIST, an agency whose effectiveness depends on its relationships with private industry as much as its internal capabilities.

## What he has said he will do

Raman's testimony before the Senate committee was heavy on a single theme: American competitiveness. "NIST has been foundational to advancing American industrial competitiveness," he said. "If confirmed, I look forward to helping write the next chapter for NIST — that of maximum American innovation enabled by accelerating technology innovation in partnership with industries, with entrepreneurs, with stakeholders."

The emphasis on semiconductors was pointed. "I'm very supportive of whatever we can do to make sure advanced manufacturing moves ahead here in America in whatever way possible," he told the committee. For an agency that will play a central role in implementing the CHIPS Act's manufacturing standards, the signal was clear: NIST under Raman will lean heavily into the industrial policy agenda that both parties have embraced.

## The diaspora dimension

Raman's confirmation adds another name to the growing roster of Indian-born leaders running American institutions — from Satya Nadella at Microsoft and Sundar Pichai at Alphabet to Shailesh Jejurikar at Procter & Gamble. But there is something distinct about a role like NIST director. This is not a corporate appointment. It is a position of public trust, confirmed by the United States Senate, overseeing an agency that literally defines the standards by which American industry operates.

For the generation of Indian engineers who arrived in the 1980s and 1990s with student visas and ambition, Raman's arc is both familiar and extraordinary. The Goodwill clothes, the student loans, the slow climb through the tenure track — these are details that resonate across thousands of kitchens in Edison and Fremont and Plano. What is less common is where the climb ended: not in a corner office, but at the helm of the agency that keeps America's technological infrastructure honest."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Karnataka's New Chief Minister Has a Plan for 1.8 Million Overseas Kannadigas: Give Them Their Own Department",
        "subheadline": "Ten days into his tenure, D.K. Shivakumar is reviving a Congress manifesto promise to create a dedicated NRI department — modelled on Kerala's — to channel diaspora investment and address the grievances of Kannadigas abroad.",
        "slug": make_slug("karnataka-nri-department-shivakumar-kannadiga-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the estimated 1.8 million Kannadigas scattered across 34 countries, the promise of a dedicated state department means a single window for investment facilitation, property disputes, and welfare support — replacing the current maze of uncoordinated bureaucratic departments.",
        "tags": ["nri", "diaspora", "karnataka", "shivakumar", "kannadiga", "investment", "governance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NRI Focus", "url": "https://nrifocus.com/kannadiga-nris-ask-karnataka-chief-minister-for-separate-ministry-to-solve-issues/"},
            {"name": "Coastal Digest", "url": "https://www.coastaldigest.com/karnataka-ready-set-separate-department-nris-says-d-k-shivakumar"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/pravasi-short-news-12-06-2026/"},
            {"name": "Sahil Online", "url": "https://sahilonline.org/karnataka-will-have-separate-secretariat-for-nris-to-invest-in-the-state-dk-shivakumar/"}
        ]),
        "score_total": 73,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/85/DK_Shivakumar_speech.jpg",
        "image_caption": "Karnataka Chief Minister D.K. Shivakumar addressing a public gathering",
        "image_attribution": "Wikimedia Commons",
        "body": """D.K. Shivakumar has been Chief Minister of Karnataka for barely a fortnight, and he is already reviving a promise that has followed him for three years. During a week that saw him address the NITI Aayog council in New Delhi and pitch Bengaluru's infrastructure needs to the Centre, Shivakumar confirmed plans to create a dedicated department for non-resident Kannadigas — a separate governmental body tasked with everything from channelling diaspora investment to resolving the property disputes that plague NRIs who own land back home.

The announcement is not new in spirit. Shivakumar, then deputy chief minister, first floated the idea in July 2023, shortly after the Congress-led government took power. The party had included the commitment in its election manifesto. IT-BT Minister Priyank Kharge submitted a draft note. A vice-chairman was appointed. And then, as tends to happen with manifesto promises that lack a crisis to force them forward, the idea drifted into the bureaucratic middle distance.

What has changed is Shivakumar himself. He became chief minister on 3 June, replacing Siddaramaiah in a leadership transition that was as much about consolidating Congress's position in the state as about policy direction. With the top job comes the authority to push the NRI department from draft note to functioning institution. By the accounts of those briefed on the plan, he intends to do so within the next budget cycle.

## The Kerala model

The template Shivakumar is working from is not obscure. Kerala's Department of Non-Resident Keralites' Affairs — known as NORKA — has operated since 1996, providing a single-window system for the state's enormous Gulf diaspora. NORKA handles everything from repatriation assistance for stranded workers to investment facilitation for returning NRIs. It runs a welfare fund, a pension scheme, and a helpline that fields thousands of calls a year.

For Karnataka, the comparison is instructive but imperfect. Kerala's diaspora is concentrated heavily in the Gulf states, where the relationship between worker and state government is often one of vulnerability — labour disputes, visa problems, medical emergencies. Karnataka's 1.8 million NRIs are more geographically dispersed across 34 countries and skew more heavily toward professionals in North America, Europe, and Australia. Their needs are different: investment facilitation, property management, OCI card hassles, and the perennial frustration of navigating multiple state departments from twelve time zones away.

## What the delegation demanded

The urgency behind the announcement can be traced to a 42-member delegation of NRIs from 34 countries that met with the previous government at Suvarna Vidhana Soudha in Belagavi. The delegation, led by deputy chairperson of the NRI forum and MLC Dr. Arathi Krishna, was blunt about the problem.

Dr. Ronald Colaco, a businessman based in the Middle East, reminded the government that the single-window clearance system works in Kerala. "The current system is cumbersome as it involves visiting several different departments," he told the chief minister. The message was clear: Kannadiga NRIs want to invest in their home state, but the bureaucratic architecture makes it unreasonably difficult.

The numbers support the frustration. Karnataka is India's leading state for services exports, accounting for more than 40 per cent of the national total. Bengaluru alone has more IT professionals than the entire state of California, a figure Shivakumar cited at the NITI Aayog meeting. Yet the state has no institutional mechanism to engage its overseas population as investors, let alone as a constituency with distinct welfare needs.

## The investment angle

The economic logic for a dedicated NRI department is straightforward. India's total inward remittances — roughly $120 billion annually — remain the highest in the world. But remittances are blunt instruments: money sent to family members, deposited in savings accounts, perhaps funnelled into local real estate. What state governments want is something more targeted — diaspora capital directed toward infrastructure, startups, manufacturing, and the tier-two and tier-three cities that need it most.

Karnataka's pitch is that it has the ecosystem to absorb sophisticated investment. The state's startup density, its research institutions, and its IT corridor give it a natural advantage over states that are competing for NRI capital with fewer absorptive structures. What it lacks is the institutional plumbing to match willing investors with viable opportunities — the investment facilitation, the regulatory handholding, the single point of contact that reduces the transaction costs of investing from abroad.

Whether Shivakumar's department will deliver on that promise depends on execution — always the weakest link in Indian governance. A department without autonomy, budget, or empowered leadership will end up as another layer of bureaucracy rather than a solution to it. But the political will, at least for now, appears genuine. For 1.8 million Kannadigas abroad, a dedicated department would signal something they have long wanted to hear: that their home state considers them worth organising around."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
