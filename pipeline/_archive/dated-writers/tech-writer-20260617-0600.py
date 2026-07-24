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
        "headline": "TCS Cut 12,000 Jobs From the Middle. The Layer That Built India's IT Industry Is the One AI Is Erasing.",
        "subheadline": "Chandrasekaran says Tata Consultancy Services will soon run as many AI agents as people. For the diaspora, the pyramid that funded a generation of H-1B careers is being flattened from the inside.",
        "slug": make_slug("tcs-12000-layoffs-middle-management-ai-agents-india-it"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The Indian IT pyramid that has trained and exported tech talent to the US for three decades is being hollowed out at the middle, reshaping the career ladder for the next wave of would-be H-1B engineers and the families already here.",
        "tags": ["indian-it", "tcs", "ai-jobs", "h1b", "automation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint — Why India's middle managers are becoming obsolete", "url": "https://www.livemint.com/companies/news/natural-intelligence-on-the-ropes-why-indias-middle-managers-are-becoming-obsolete-ai-tcs-cognizant-it-services-11718000000000.html"},
            {"name": "Outlook Business — Infosys Bucks Layoff Trend Despite AI Disruption", "url": "https://www.outlookbusiness.com/corporate/infosys-bucks-layoff-trend-despite-ai-disruption-across-it-sector"},
            {"name": "Inc. — Gartner Predicts AI Will Eliminate 50 Percent of These Roles", "url": "https://www.inc.com/jeff-haden/gartner-predicts-ai-will-eliminate-50-percent-of-these-roles.html"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
        "image_caption": "Tata Sons chairman N. Chandrasekaran, who told shareholders AI will cut TCS hiring",
        "image_attribution": "Wikimedia Commons",
        "body": """India's software industry invented the idea that you could run a global IT department from a tower in Bengaluru. It is now discovering that the same automation it sells to clients works just as well on its own org chart.

Tata Consultancy Services, the country's largest IT employer, retrenched roughly 12,000 people in the financial year that ended in March — "primarily in the middle and senior grades," in the company's own phrasing. That is a striking admission from a firm that ended the year with just under 600,000 employees and that, for a generation, grew headcount almost mechanically with revenue. At the company's annual general meeting last week, chairman N. Chandrasekaran was unusually direct about where this goes. Asked whether AI would reduce hiring, he said: "Absolutely." The company, he added, would eventually run as many AI agents as it has human staff.

### The layer that funded a generation

To understand why this matters to Indian Americans specifically, look at the shape of what is being cut. The classic IT-services firm is a pyramid: a thin senior band of architects, a thick middle of delivery managers and project leads, and a vast junior base writing, testing and documenting code. Phil Fersht of HFS Research describes the middle as the industry's economic engine — the coordination layer that existed to manage armies of juniors.

AI is dissolving that logic from both ends. It now does a meaningful share of the junior work, which means fewer juniors, which means far less of the middle-management coordination that juniors required. Gartner expects one in five organizations to use AI to flatten structure and eliminate more than half of current middle-management roles. In Indian IT, that pressure lands on the exact cohort — six to fifteen years of experience, earning ₹16–40 lakh — that has historically been the feeder pool for onsite US deployments and, eventually, H-1B and green-card sponsorship.

### Not everyone is cutting

The response across the sector is splitting, and the split is instructive. Cognizant has earmarked job cuts of its own. But Infosys, the No. 2 player, is taking the opposite public stance. CEO Salil Parekh has flatly ruled out layoffs, saying the firm has not cut staff in the past year and plans to hire around 20,000 freshers again in FY27. His framing is that AI "expands the scope of work rather than shrinking it," with the company already drawing about 5.5% of revenue from AI services and building in-house platforms and agents with partners like OpenAI and Anthropic.

Both things can be true. Entry-level demand is softening even at the firms that are still hiring, and the nature of the fresher's job is changing from "write the code" to "supervise the agent that writes the code." A recent PwC analysis of more than a billion job ads found that AI-exposed entry-level roles are now seven times as likely to demand senior-level judgment as the least-exposed ones. The ladder isn't just narrowing; its bottom rungs are being raised out of reach of true beginners.

### Why the diaspora should watch closely

For Indian families in New Jersey, the Bay Area or the Dallas suburbs, the Indian IT pyramid has never been an abstraction. It is the pipeline. The mid-career manager TCS is now letting go is the same profile that, a decade ago, would have been rotated onto a US client site and started the long climb toward permanent residency. As that middle thins, two consequences follow.

First, the supply of "ready-made" onsite candidates from the big services firms shrinks, even as US visa policy itself grows more hostile — the proposed $100,000 H-1B application fee, struck down this week by a federal judge and now headed to appeal, hangs over every staffing model that depends on cheap mobility. Second, the diaspora's younger relatives back home face a brutal new math: the engineering-graduate glut that India's IT sector used to absorb has nowhere obvious to go.

The optimistic reading, voiced by Parekh and others, is that this is a repricing, not a collapse — judgment-rich work survives and pays more, while "labour arbitrage" work disappears. The pessimistic reading is that an entire middle class built on coordinating juniors is being asked to reinvent itself in real time. Either way, the era when an Indian IT job was a near-guaranteed escalator to the West is ending. What replaces it will be decided over the next few quarters, in earnings calls and AGMs that the diaspora would do well to read line by line."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora Spent $30 Billion Rebuilding Palo Alto Networks for the Age of AI Agents",
        "subheadline": "The CyberArk and Chronosphere deals bet that every AI agent now needs its own identity and its own guard. For Indian engineers, it is the clearest map yet of where security jobs are moving.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-cyberark-agentic-ai-security"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "An Indian-origin CEO is reshaping the entire cybersecurity industry around agentic AI, and the skills shift he is betting on — identity and machine-to-machine security — is exactly where the next decade of Indian-American tech careers will be built.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "agentic-ai", "indian-ceo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CRN — Palo Alto Networks Completes $3.3B Acquisition Of Chronosphere", "url": "https://www.crn.com/news/security/2026/palo-alto-networks-completes-3-3b-acquisition-of-chronosphere-for-ai-observability-push"},
            {"name": "Palo Alto Networks — Completes Acquisition of CyberArk", "url": "https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-cyberark"},
            {"name": "Cybersecurity Dive — Palo Alto Networks CEO sees AI as demand driver", "url": "https://www.cybersecuritydive.com/news/palo-alto-networks-arora-ai-demand-driver/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks chairman and CEO Nikesh Arora, who has led the company's $30 billion AI-security acquisition spree",
        "image_attribution": "Wikimedia Commons",
        "body": """When Nikesh Arora left a half-billion-dollar pay package at SoftBank to run Palo Alto Networks in 2018, the joke in Silicon Valley was that he had taken a demotion. Eight years later, he has turned a firewall company into the most aggressive consolidator in cybersecurity — and his thesis about why is one every Indian engineer in the industry should understand.

In the space of a few months, Palo Alto Networks has closed its $25 billion purchase of identity-security firm CyberArk — by far the largest deal in its history — and a $3.35 billion acquisition of observability startup Chronosphere, while also picking up an agentic-endpoint startup called Koi. Add the smaller deals and Arora has committed something on the order of $30 billion in a single buying spree. His explanation, delivered to Wall Street analysts, was blunt: "The AI cycle is moving fast."

### The bet: agents need guards too

The logic threading these deals together is a specific view of what AI does to security. Arora's argument is that as AI agents proliferate inside enterprises — software that doesn't just answer questions but takes actions, moves data and calls other systems — the attack surface explodes. "More infrastructure, more machine-to-machine activity and new classes of risk that simply didn't exist before," as he put it on a recent earnings call.

That reframing is why he bought CyberArk. The old model of identity security was about humans logging in. The new model, Arora says, has to "secure every identity — human, machine, and agent." Each AI agent your company spins up is effectively a new employee with credentials, and every one of those credentials is a door. CyberArk guards the doors; Chronosphere watches what comes through them; and both are being folded into Cortex AgentiX, Palo Alto's agentic-security platform.

### A signal, not just a strategy

Arora has put his own money behind the thesis. When cybersecurity stocks sold off this spring on fears that a powerful new Anthropic model could both perform security functions and defeat traditional defenses, he bought roughly $10 million of Palo Alto shares on the open market in a single day, lifting his direct-and-indirect stake to around $162 million. He has been pointed about rejecting the bear case that AI makes security software obsolete: AI, he insists, is the demand driver, the thing that "expands the attack surface area," not the thing that shrinks the market.

The market hasn't always rewarded the boldness — the stock was hammered after a cautious forecast even as quarterly revenue rose 15% to $2.6 billion — but the strategic direction is unambiguous.

### Why this matters to the diaspora

Cybersecurity is one of the densest concentrations of Indian-origin talent in American tech, from SOC analysts in Plano to product leaders in Santa Clara, and Arora is one of the most prominent Indian-American CEOs reshaping it. His acquisition map is, in effect, a hiring map. The categories he is paying billions to own — identity security, AI observability, agentic endpoint protection — are precisely the skills that will be in demand as the rest of the enterprise world races to deploy agents safely.

For an Indian engineer weighing where to specialize, that is actionable intelligence. The traditional security roles built around perimeter defense and human access management are commoditizing; the roles built around securing non-human identities and monitoring autonomous systems are where a $30 billion bet says the money is going. For the many diaspora professionals who already hold roles at CyberArk and the acquired firms, the consolidation also brings the usual integration churn — accelerated roadmaps, but also overlapping teams.

There is a geopolitical footnote, too. As part of the CyberArk deal, Palo Alto plans a secondary listing on the Tel Aviv Stock Exchange under the ticker "CYBR," cementing Israel's role as its R&D backbone. Arora is building a company that spans Silicon Valley, Israel and a large engineering base in India — a structure that looks a lot like the distributed, multi-hub future of tech itself. The man running it just told the industry exactly where he thinks the next decade of security work will live."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest EV Wave Yet Starts This Week. Ola's Collapse Shows Why Speed Was Never the Point.",
        "subheadline": "Sixteen electric launches are lined up against seven new petrol models over nine months. The startup that once owned half the scooter market has lost more than half its volume — a cautionary tale for NRI investors chasing the India EV story.",
        "slug": make_slug("india-ev-launch-wave-2026-ola-electric-collapse-ather-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs increasingly hold Indian EV stocks and watch the clean-mobility story as a proxy for India's growth — but the Ola Electric collapse is a hard lesson that disruption hype and durable execution are very different bets.",
        "tags": ["india-ev", "ola-electric", "ather-energy", "clean-energy", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine — India's EV expansion kicks off June 15", "url": "https://www.thehindubusinessline.com/companies/indias-ev-expansion-kick-off-june-15-with-16-rollouts-vs-7-ice-models/article69000000.ece"},
            {"name": "The Hindu BusinessLine — TVS overtakes Ola to lead EV FY26 two-wheeler market", "url": "https://www.thehindubusinessline.com/companies/tvs-overtakes-ola-to-lead-ev-fy26-two-wheeler-market-bajaj-ather-follow/article69000001.ece"},
            {"name": "Reuters — Ola Electric to invest $208.5 million in EV, cell tech units", "url": "https://www.reuters.com/business/autos-transportation/indias-ola-electric-invest-2085-million-ev-cell-tech-units-2026-05-15/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Black_OLA_Electric_scooters.jpg/1280px-Black_OLA_Electric_scooters.jpg",
        "image_caption": "Ola Electric scooters lined up at a showroom; the company's two-wheeler volumes fell more than 53% in FY26",
        "image_attribution": "Wikimedia Commons",
        "body": """Starting this week, India's car and scooter market enters its busiest electric stretch yet. Over the next nine months, automakers plan to roll out roughly ten battery-electric vehicles, four plug-in hybrids and two hybrids — sixteen electrified launches against just seven all-new petrol and diesel models. The cycle opens with Mercedes-Benz's S450e plug-in hybrid, followed quickly by Toyota's Urban Cruiser EV and Tata's Sierra EV, and runs through nearly every major brand from Maruti and Hyundai to BYD and BMW.

For NRI investors who treat India's EV transition as a clean bet on the country's growth, the headline is seductive: for every new combustion vehicle entering the market, almost two electrified ones are lining up behind it. But the more important story this week is a cautionary one, and it belongs to the company that was supposed to lead all of this.

### The fall of the disruptor

Ola Electric once looked unstoppable. In early FY25 it commanded roughly 49% of India's electric two-wheeler market and projected the swaggering image of a Silicon Valley-style disruptor transplanted to Bengaluru. In FY26 its volumes collapsed more than 53%, to about 160,000 units from over 344,000 a year earlier. The cause was not a clever competitor's master stroke. It was service failures, supply constraints and the unglamorous operational debt that piles up when you scale faster than you can support customers.

The market it once dominated has redistributed to players that move less loudly. TVS has overtaken Ola to lead the FY26 two-wheeler EV race, with Bajaj and Ather close behind; their iQube, Chetak and Rizta models now account for nearly 70% of sales. Legacy manufacturers, it turns out, had a moat the startups underestimated: distribution depth, service networks and supply-chain control. Hero's Vida volumes leapt 184%. Ather, the other startup standout, grew 75% and plans to expand from 700 stores to more than 1,100 by March 2027 — opening, on average, more than a store a day. Ola, meanwhile, is shrinking its footprint from about 4,000 outlets to roughly 700.

### The "Hail Mary"

Ola's stock has nonetheless rallied as much as 60% over two months, which tells you something about how Indian markets are pricing this sector. Investors are no longer valuing Ola as a scooter maker — on volumes and margins it would be punished — but as a vertically integrated EV platform. The company is pouring $208.5 million into vehicle and battery-cell units, building its own Bharat Cell production rather than importing, and betting that owning the full stack from cell to software justifies a future-prospects valuation rather than a sales-multiple one.

Analysts at Mint have called this a "Hail Mary" pass, and the description is fair. Building a battery ecosystem is a vastly harder problem than selling scooters, and execution risk is high. If management stumbles, the rally is a temporary reprieve, not a turnaround.

### What NRIs should take from it

Three lessons travel well across the ocean. First, India's EV demand is real and broadening — no longer a niche, but moving simultaneously into ₹10-lakh hatchbacks, family SUVs and ₹2-crore luxury sedans, helped along by high fuel costs, tightening efficiency norms and even Prime Minister Modi's public nudges toward fuel conservation. The total-addressable-market story is intact.

Second, the winners are increasingly the operators, not the showmen. For a diaspora investor used to backing disruption narratives, the FY26 reshuffle is a reminder that in India's hardware-heavy mobility market, after-sales service and supply chains are the moat, not viral launches.

Third, the policy layer is turning from carrot to stick. Delhi's draft EV policy would bar new petrol three-wheeler registrations from 2027 and require all new two-wheelers to be electric from 2028 — a more interventionist phase than the purchase-subsidy era. That raises the ceiling for EV makers but also the execution bar.

The sixteen launches arriving over the coming months will generate plenty of excitement back home and in diaspora WhatsApp groups alike. The Ola episode is the footnote worth pinning to every one of them: in this market, the company that grows the loudest is not the one that lasts the longest."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
