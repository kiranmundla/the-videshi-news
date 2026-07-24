#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Swiggy Rider Can Now Start a Mutual Fund in a Few Taps. India Just Wired Investing Into the Gig Economy.",
        "subheadline": "Swiggy's tie-up with Zerodha Fund House lets delivery partners invest from Rs 100 straight through their rider app. It is a small feature with a big idea behind it — formal finance reaching the people the formal economy usually skips.",
        "slug": make_slug("swiggy-zerodha-fund-house-gig-workers-mutual-funds"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who hold Swiggy stock or watch India's fintech rails, this is a live test of whether digital public infrastructure can pull millions of informal workers into formal investing — the next frontier after UPI moved money and Aadhaar moved identity.",
        "tags": ["fintech", "swiggy", "zerodha", "gig-economy", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/swiggy-ties-up-with-zerodha-fund-house-to-enable-delivery-partners-to-invest-in-mutual-funds/article69730000.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/personal-finance/swiggy-ties-up-with-zerodha-fund-house-to-enable-delivery-partners-to-invest-in-mutual-funds"},
            {"name": "Z-Connect by Zerodha", "url": "https://zerodha.com/z-connect/zerodha-fund-house"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Swiggy_delivery_partner.jpg/1280px-Swiggy_delivery_partner.jpg",
        "image_caption": "A Swiggy delivery partner on the road in India. Riders can now invest part of their earnings in mutual funds through the same app they use for deliveries.",
        "image_attribution": "Wikimedia Commons",
        "body": """On Tuesday, Swiggy announced a feature that will not make a single delivery faster or a single meal hotter. It is, on its face, modest: the company's delivery partners can now invest part of what they earn in mutual funds, starting from as little as Rs 100, directly through the rider app they already open dozens of times a day.

The idea underneath it is anything but modest.

## What was launched

Swiggy has partnered with Zerodha Fund House, the asset-management arm built by India's largest discount broker, to put investing inside the workflow of a gig worker. The money goes directly into Zerodha Fund House's schemes, and a partner can then manage the investment through the fund house's WhatsApp channel — no separate broking account, no branch visit, no paperwork pile.

"With this partnership, we are making it easier for our delivery partners to invest their earnings and, in turn, become financially independent as well as invest for their future," said Saurav Goyal, Swiggy's senior vice-president for its driver and delivery organisation. The framing is deliberate: not a perk, but a financial tool "designed for them."

## Why this is harder than it sounds

The reason gig workers rarely invest is not ignorance. It is cash-flow shape. A salaried employee earns once a month and can set up an automatic deduction the day after payday. A delivery rider earns in short, irregular cycles — a busy weekend, a slow Tuesday, a surge during rain — and spends in the same rhythm. Traditional systematic investment plans, built around predictable monthly salaries, simply do not fit that life.

Vishal Jain, CEO of Zerodha Fund House, put the problem plainly. "For millions of gig workers, building long-term savings can be difficult when incomes are earned and spent in short cycles," he said. "A Swiggy delivery partner can now save a part of their weekly earnings into a mutual fund in a few taps and withdraw it whenever they need." The withdrawal flexibility matters as much as the low entry point: a worker who cannot lock money away for a decade can still build a buffer they can reach in an emergency.

## The bigger pattern

This is the latest move in what Jain has elsewhere called the "UPI moment" for investing. India spent the last decade building digital public infrastructure — Aadhaar for identity, UPI for payments — that turned slow, branch-bound services into instant, phone-native ones. Zerodha Fund House went live on the government-backed Open Network for Digital Commerce precisely to ride those rails into corners of the country that formal finance never reached.

The Swiggy tie-up is that thesis applied to a specific, large, underserved population. Mutual-fund assets in India have compounded at roughly 20% a year for a decade, yet penetration among informal workers sits in the low single digits. The gap is not demand; it is friction. Embedding a fund inside an app a rider already trusts removes the friction in one stroke.

It is also part of a broader push by India's delivery platforms to take their workforces seriously. Just this month, logistics firm Delhivery rolled out an accident-insurance and health-cover programme for its frontline staff. The competition for riders is intensifying, and financial benefits are becoming a recruiting and retention weapon, not just corporate goodwill.

## Why the diaspora should watch

For Indians abroad, this lands on two levels. The first is investment: Swiggy is a listed company, and NRIs who own it — or who track India's consumer-tech sector as a proxy for the homeland economy — are watching whether platforms can deepen their relationships with workers beyond per-order payouts. Features like this raise switching costs and build loyalty in a notoriously churn-heavy labour market.

The second is structural, and more interesting. The diaspora has watched India leapfrog physical banking with UPI; many NRIs now pay street vendors in Bengaluru by phone more easily than they pay for parking in California. Investing is the next layer of that leapfrog. If a delivery rider in Indore can build a mutual-fund corpus from his weekly earnings without ever filling a form, the model becomes exportable — the kind of inclusion infrastructure other developing economies, and their own diasporas, will study.

## What's next

The hard part is behaviour, not technology. Making investing possible in a few taps does not make people do it, and the real test is how many of Swiggy's hundreds of thousands of partners actually start — and keep — investing once the novelty fades. Defaults, nudges and trust will decide that.

But the direction is set. India keeps finding ways to fold its informal economy into its formal one, one app feature at a time. A rider quietly building savings between deliveries may be the most Indian fintech story of the year."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Foreign Satellite Giants Are Stuck at India's Door. Mukesh Ambani Just Decided to Build His Own Constellation.",
        "subheadline": "As Starlink and Amazon wait on Delhi's security clearances, Jio says it will build a sovereign low-Earth-orbit network for India — a bet that connectivity from space should be Indian-owned.",
        "slug": make_slug("jio-sovereign-leo-satellite-constellation-starlink-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who send devices, money and expectations of connectivity back to rural India have a direct stake in who controls the satellite broadband that finally reaches the village — a foreign operator on a licence, or a sovereign Indian network built to stay.",
        "tags": ["space-tech", "jio", "reliance", "satellite-internet", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Light Reading", "url": "https://www.lightreading.com/satellite/india-s-jio-bets-on-5g-ai-and-satellite-for-next-growth-phase"},
            {"name": "RCR Wireless News", "url": "https://www.rcrwireless.com/20260622/satellite/india-tightens-scrutiny-foreign-satellite-operators-jio-expands"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/dot-drops-draft-spectrum-rules-starlink-and-jio-satellite-excluded-completely"}
        ]),
        "score_total": 77,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Constellation_satellites_in_low_Earth_orbits_%28artist%E2%80%99s_impression%2C_not_to_scale%29_%28noirlab2022a%29.jpg/1280px-Constellation_satellites_in_low_Earth_orbits_%28artist%E2%80%99s_impression%2C_not_to_scale%29_%28noirlab2022a%29.jpg",
        "image_caption": "An artist's impression of a low-Earth-orbit satellite constellation. Jio says it will build a sovereign LEO network for India.",
        "image_attribution": "Wikimedia Commons / NOIRLab",
        "body": """For three years, the story of satellite internet in India has been a waiting story. Elon Musk's Starlink, Bharti-backed Eutelsat OneWeb, Amazon's LEO project and the Jio-SES joint venture have all filed paperwork, lobbied Delhi and queued for the security and spectrum clearances that would let them switch on service. None has been allowed to start selling broadband to ordinary Indians.

This week, Reliance signalled it is done waiting on others. At the company's annual shareholder meeting, Jio chairman Akash Ambani said the company will evaluate building a sovereign low-Earth-orbit (LEO) satellite constellation for India — its own fleet, its own ground stations, its own end-to-end "space to ground" broadband platform.

## The dual-track bet

Ambani was careful to frame it as a hedge, not a gamble. "Jio is evaluating the development of a sovereign low Earth orbit satellite constellation for India," he told shareholders. "We are also partnering with the leading global constellation providers by leasing satellite capacity, so that we can accelerate service availability while building our own long-term sovereign capability."

In plain terms: lease someone else's satellites now to get service running, while spending years and billions to build a domestic network that India ultimately owns. Reliance has already begun constructing the ground-station infrastructure that both its leased partners and its future satellites will need. Reports earlier this year suggested the plan could eventually stretch to satellites, payloads, launch vehicles and user terminals — a full domestic stack.

## Why "sovereign" is the operative word

The backdrop explains the ambition. India's Department of Telecommunications has dragged out final approvals for satellite operators over national-security concerns: cross-border data flows, the behaviour of foreign-controlled networks during a geopolitical crisis, and who can switch a constellation off. A recent draft of spectrum rules pointedly left non-geostationary operators — the LEO players — outside the framework entirely, freezing commercial rollouts even for licensed firms.

That regulatory caution is precisely the gap a sovereign operator is built to fill. Analysts note that companies backed by Indian groups — Bharti's OneWeb stake, Reliance's satellite venture with Luxembourg's SES — are likely to benefit from a regime that rewards local infrastructure and domestic control. Delhi wants connectivity that reaches the unserved village without handing a foreign company a kill switch over critical communications. Jio is offering to be that answer.

## The scale problem nobody can wish away

There is a sober counterpoint. Even India's largest telecom operator cannot conjure a Starlink-class constellation overnight. Starlink has thousands of satellites in orbit; a from-scratch Indian network will take years to approach useful coverage. Most analysts expect the realistic near-term outcome to be a hybrid: foreign constellations operating under tight Indian oversight, in partnership with domestic telcos, while the sovereign network is slowly built behind them. India will remain reliant on international capacity for a while yet.

## What it means for the diaspora

For Indians abroad, this is not abstract. The diaspora is deeply invested — financially and emotionally — in whether rural India gets online. NRIs fund schools, send smartphones home, run businesses that depend on relatives being reachable, and increasingly back the connectivity startups serving Bharat. The question of who provides the satellite link to a Himalayan town or a Sundarbans island is, for many, a question about their own families.

A sovereign network also speaks to a sentiment the diaspora knows well: the preference for India to own its strategic infrastructure rather than rent it. The same instinct that drives the semiconductor mission and the sovereign-AI push now extends to orbit. For NRIs who hold Reliance shares — among the most widely held stocks in Indian portfolios at home and abroad — Jio's space ambitions are also a long-duration bet on the next leg of the company's growth, after telecom and retail.

## What's next

Watch three things. First, whether the DoT's final spectrum framework brings LEO operators in from the cold and on what security terms. Second, how Reliance structures the "evaluate" into a committed plan — capital, timeline, launch partners. And third, whether Starlink and Amazon finally clear India's gates, and what room is left for them once a sovereign champion has the government's ear.

The waiting game is ending. The ownership game is beginning."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indians Are Putting Solar on the Roof Faster Than Anyone Expected. Investors Just Poured Rs 510 Crore Into the Company Riding That Wave.",
        "subheadline": "SolarSquare's new funding round, led by Lightspeed, is a bet that rooftop solar has crossed from subsidy story to consumer habit — powered by the PM Surya Ghar scheme and rising electricity bills.",
        "slug": make_slug("solarsquare-funding-india-rooftop-solar-pm-surya-ghar"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs funding solar panels on the family home back in India, or eyeing the country's clean-energy boom as an investment, SolarSquare's raise marks the moment rooftop solar stopped being a green gesture and became a mainstream consumer purchase.",
        "tags": ["cleantech", "solar", "solarsquare", "renewable-energy", "indian-startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechScoop India", "url": "https://techscoopindia.com/solarsquare-secures-53-million-to-expand-rooftop-solar-solutions-2026/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/solarsquare-in-talks-to-raise-up-to-60m-india-rooftop-solar/"},
            {"name": "Entrackr", "url": "https://entrackr.com/2024/12/solarsquare-raises-40-mn-in-series-b-led-by-lightspeed/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Rooftop_Solar_panels_on_homes_in_Mehsana%2C_Gujarat%2C_India.jpg/1280px-Rooftop_Solar_panels_on_homes_in_Mehsana%2C_Gujarat%2C_India.jpg",
        "image_caption": "Rooftop solar panels on homes in Mehsana, Gujarat. India's residential solar market is drawing major venture capital.",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, rooftop solar in India was a story told in PowerPoint — a slide about energy transition, a chart about 2030 targets, a government scheme few households actually used. The panels were expensive, the paperwork was punishing, and the whole thing felt like something for the future.

A Rs 510 crore cheque just landed on that future.

## The round

SolarSquare, a Mumbai-based residential solar company, has raised about $53 million in a Series C round led by Lightspeed, the venture firm whose India portfolio includes Razorpay and Zepto. Existing backers — Elevation Capital, Chris Sacca's Lowercarbon Capital, Zerodha's Rainmatter and Good Capital — joined in. The round takes SolarSquare's total funding past $100 million and roughly doubles the valuation it carried 18 months ago.

The company says it now runs at a Rs 1,000 crore annual revenue run-rate and has installed solar on close to 50,000 homes. Founded in 2015 by Shreya Mishra, Neeraj Jain and Nikhil Nahar, it started in business-to-business work before pivoting to consumers in 2021 — and the consumer bet is what investors are now paying up for.

## Why money is flowing into Indian rooftops

The funding is less about one company than about a market that has quietly tipped. India became the world's third-largest solar power producer in 2025, behind only China and the United States. Its installed solar capacity has surged from around 3 gigawatts in 2014 to more than 150 GW in 2026. The country is targeting 500 GW of renewable capacity by 2030, with solar expected to supply more than half of it.

Two forces are pulling solar onto ordinary roofs. The first is the PM Surya Ghar scheme, the government's residential-solar subsidy programme, which has sharply cut the upfront cost of going solar. The second is simpler: electricity tariffs keep rising, and a household that installs panels is, in effect, locking in cheaper power for two decades. When the maths flips from "green gesture" to "lower bill," adoption stops depending on idealism.

SolarSquare's pitch is to remove the remaining friction. It positions itself as an end-to-end brand — design, installation, government permits, financing and maintenance handled in one place — so a homeowner does not have to assemble a project out of contractors and subsidy forms. That full-service model is exactly what turns a complicated infrastructure decision into a consumer purchase.

## A sector, not a one-off

The SolarSquare round is part of a broader cleantech surge. GPS Renewables recently raised Rs 635 crore; Newtrace pulled in $6.3 million; investors are circling rooftop, utility-scale and green-hydrogen plays alike. India's cleantech economy is projected to reach $152 billion by 2030, and venture firms that spent the last cycle chasing fintech and quick-commerce are visibly rotating capital toward energy.

## The diaspora connection

This is one of the rare India-tech stories where the diaspora is often a direct participant, not just an observer. Putting solar on the parents' house is a common NRI project — a tangible upgrade to the family home that also cuts a recurring bill the children abroad frequently help pay. A company that makes that process turnkey, with financing and maintenance bundled in, is solving a problem many diaspora families have wrestled with from 8,000 miles away.

There is an investment angle too. NRIs looking to back India's growth beyond IT services and consumer apps have few clean ways to play the energy transition; a maturing, venture-funded residential-solar leader is the kind of company that could eventually list and offer exactly that exposure. SolarSquare's backers — Lightspeed, Elevation, Rainmatter — are the same names that defined India's last startup decade, and their move into solar is a signal about where the next one is headed.

## What's next

The questions now are about execution at scale: can SolarSquare expand into new cities while keeping installation quality high and service responsive, and can it reach profitability as it grows? The company has used the fresh capital to deepen technology and widen its geographic footprint. Rooftop solar has won the argument on economics. The race now is to win the living rooms — one home, one roof, one falling electricity bill at a time."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  [{len(art['body'].split())} words]")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
