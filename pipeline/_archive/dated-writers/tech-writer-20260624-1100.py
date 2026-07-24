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
        "headline": "UPI Was Built So Indians Could Split a Dinner Bill. It Just Went Live at a Paris Department Store.",
        "subheadline": "India's payments rail now works in eleven countries, from the Eiffel Tower to a Cambodian street market. For the diaspora, the home-screen app is quietly becoming a passport.",
        "slug": make_slug("upi-international-expansion-france-cambodia-nepal-npci-nri"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who fly home no longer need to juggle forex cards or cash across nine-plus countries — the same UPI app on their phone now pays merchants from Paris to Phnom Penh, and the corridor map is expanding toward the markets where the diaspora actually lives.",
        "tags": ["upi", "fintech", "npci", "digital-public-infrastructure", "indian-tech", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Whizsky — UPI Launches in France", "url": "https://whizsky.com/2026/upi-france-launch"},
            {"name": "TechObserver — India, Nepal Launch Direct UPI-NPI Link", "url": "https://techobserver.in/india-nepal-upi-npi-link"},
            {"name": "The Better Cambodia — UPI Across Cambodia", "url": "https://thebettercambodia.com/upi-cambodia-acleda-npci"},
            {"name": "Nation Press — UPI at Eiffel Tower, French airports", "url": "https://nationpress.com/upi-eiffel-tower-french-airports"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A shopper makes a contactless QR-code payment with a smartphone, the everyday gesture UPI is now exporting abroad.",
        "image_attribution": "Pexels",
        "body": """India's Unified Payments Interface was designed for a domestic problem: how to move a few hundred rupees between two phones without a card, a swipe machine, or a bank teller. A decade on, it settles more than 14 billion transactions a month and accounts for nearly half of all real-time payments on the planet. This month it crossed a different kind of threshold — it went live at a major department store in Paris, and at the Eiffel Tower and French airport terminals.

For the Indian diaspora, this is less a payments story than a travel story, and it has been arriving in instalments. In the first three weeks of June alone, NPCI International Payments (NIPL), the overseas arm of the National Payments Corporation of India, switched on three new corridors.

## Where the rail now runs

UPI now works for Indian travellers in roughly eleven markets: Singapore, the UAE, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka, Cambodia, the Maldives, and — through a separate Caribbean linkage — Guyana, the first country in that region to go live. Israel and Japan are slated for later in 2026, and the Reserve Bank has signalled plans to connect UPI to the European Central Bank's instant-settlement system, which would, in principle, light up the whole euro zone.

The June launches each broke a small barrier. France moved UPI out of diaspora-heavy corridors like the Gulf and into mainstream European retail — the first time the system has gone live at a flagship Western department store rather than a remittance counter. Cambodia's tie-up with the KHQR national QR standard opened 4.5 million merchants to anyone with a PhonePe, Google Pay, or Paytm app. And the India–Nepal link did something none of the others had: it enabled two-way, person-to-person transfers, not just tourist-to-merchant payments.

## Why the diaspora should care

The obvious benefit is the one every returning NRI feels at the airport: no forex card markups, no scrambling for cash, no Visa or Mastercard intermediary skimming a conversion fee. You scan, you pay in local currency, your home bank account settles in real time at a transparent rate. For a family that flies between New Jersey and Hyderabad twice a year, that is a genuine line-item saving.

The less obvious benefit is structural. The Nepal corridor's two-way capability is the template that matters for remittances. The US–India remittance flow is the largest in the world — Indians abroad sent home well over $100 billion last year — and almost all of it still moves through wire transfers and money-transfer operators that charge real money and take real time. A UPI-grade rail running directly between an American or British bank and an Indian one would compress that cost toward zero. The France and Nepal launches are proof the plumbing can be built; the question for the diaspora is when a Western corridor gets the same two-way treatment.

There is a soft-power layer, too. New Delhi has made digital public infrastructure — UPI, Aadhaar, the ONDC commerce network — a centrepiece of its pitch abroad, and ministers now narrate each new corridor on social media as a marker of national arrival. For Indian-American technologists, many of whom built the cloud and payments systems of Silicon Valley, watching a government-backed open protocol out-compete card networks on their adopted home turf is a particular kind of vindication.

## The fine print

UPI abroad is still mostly a one-way, tourist-facing tool. In most of the eleven countries an Indian visitor can pay a merchant, but a local cannot yet pay into India, and an NRI cannot use a foreign bank account to fund a UPI handle — the system is tied to an Indian bank and, in most cases, an Indian phone number. NRIs with NRE or NRO accounts and international mobile numbers from a handful of countries can now register, but the rollout is partial and bank-dependent.

For now, the practical advice is simple. If you are flying to France, Nepal, Cambodia, or the Gulf this summer, the app already on your phone will likely pay your way. The bigger prize — cheap, instant transfers back home from the countries where the diaspora actually earns — is visible on the roadmap, but not yet at the till.

## What's next

Watch the Europe and Japan launches, and watch for any announcement that extends two-way P2P transfers beyond Nepal. The day a US or UK corridor gets that capability is the day UPI stops being a travel convenience and starts competing with the remittance industry itself."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian-Born CEO Now Supplies the Memory for Claude — and Has Bought a Slice of the Company That Builds It.",
        "subheadline": "Micron's deal with Anthropic ties Sanjay Mehrotra's memory empire directly to a frontier AI lab, days before an earnings report that could show a tenfold jump in profit.",
        "slug": make_slug("micron-anthropic-deal-sanjay-mehrotra-hbm-claude-supply-nri"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "For NRI investors holding Micron and for the thousands of Indian engineers inside the memory and AI-infrastructure supply chain, the Anthropic pact is a signal that the chip cycle that funds their RSUs has shifted from boom-and-bust to a structural AI build-out — with an Indian-American CEO sitting at the chokepoint.",
        "tags": ["micron", "anthropic", "semiconductors", "hbm", "sanjay-mehrotra", "ai-infrastructure", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GlobeNewswire — Micron and Anthropic Announce Strategic Agreement", "url": "https://www.globenewswire.com/news-release/2026/06/22/3315307/14450/en/Micron-and-Anthropic-Announce-Strategic-Agreement-to-Scale-Next-Generation-AI-Infrastructure.html"},
            {"name": "Zacks — Micron Q3 FY2026 Earnings Preview", "url": "https://www.zacks.com/stock/news/micron-q3-2026-earnings-preview"},
            {"name": "TheStreet — Wall Street is watching one key Micron metric", "url": "https://www.thestreet.com/micron-q3-fiscal-2026-earnings"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19716297/pexels-photo-19716297.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A green memory module on a circuit board — the high-bandwidth memory at the centre of the AI build-out.",
        "image_attribution": "Pexels",
        "body": """Two days before it reports earnings, Micron Technology did something a memory-chip company rarely does: it signed a deal that reads less like a supply contract and more like a marriage. On June 22, Micron and Anthropic — the lab behind the Claude family of models — announced a strategic agreement spanning four things at once: joint work on memory and storage architecture, a multi-year supply commitment, Micron's own internal adoption of Claude, and a Micron investment into Anthropic's Series H funding round.

Strip away the press-release prose and the logic is stark. Frontier AI models are bottlenecked not by raw compute alone but by memory — the high-bandwidth memory (HBM) stacked alongside Nvidia's GPUs. There are only three companies on earth that make it at scale: Micron, SK Hynix, and Samsung. None has spare capacity. Anthropic, which had its most advanced models pulled from foreign access under US export controls earlier this month, is locking in supply for the long haul. Micron is locking in a marquee customer and taking an equity stake in the demand.

## The man at the chokepoint

Micron is run by Sanjay Mehrotra, who co-founded SanDisk before taking the top job in Boise in 2017. He is one of the cohort of Indian-born executives — alongside Nadella, Pichai, Arora, Narayen and Krishna — now running the American technology economy, but his company occupies a more physical kind of power than the software giants. Micron does not write code that sits on someone else's cloud; it fabricates the memory that the entire AI industry is starved of.

That scarcity is about to show up in the numbers. Micron reports fiscal third-quarter results after the close on June 24, and the guidance is extraordinary: revenue of roughly $33.5 billion, up about 40% from the prior quarter and roughly 260–285% year on year, with gross margins guided near 81% — a figure that would top even Nvidia's. Consensus earnings estimates cluster around $20 per share, against $1.91 in the same quarter last year. Morningstar projects Micron's net income for 2026 and 2027 will rank second only to Nvidia across the entire semiconductor index. That is not the profile of a cyclical memory company; it is, as one analyst put it, a structural AI-infrastructure play.

## Why this lands for the diaspora

Three reasons, in descending order of immediacy.

First, the investors. Micron is a staple of NRI portfolios — a US-listed semiconductor name with a recognisable Indian-American CEO and, lately, a 268% year-to-date run. The Anthropic deal matters to them because it addresses the one fear that haunts every memory bull: that this is just another cycle, and the crash is coming. A multi-year supply agreement anchored to a named frontier lab, plus an equity stake that aligns Micron with that lab's growth, is the company's argument that the demand is durable. The stock fell 13% on June 23 on a sympathy sell-off after Korean memory peers dropped — a reminder that the market has not fully decided whether to believe the structural story.

Second, the engineers. Thousands of Indians work across the memory and AI-infrastructure supply chain — at Micron, at the hyperscalers building data centres around Nvidia silicon, and at the AI labs themselves. The token-economics work Micron and Anthropic describe — squeezing more performance and energy efficiency out of each layer of the stack — is exactly the kind of systems engineering where Indian talent is concentrated. The deal is a hiring and roadmap signal as much as a financial one.

Third, the India fab. Micron is building an assembly-and-test plant in Sanand, Gujarat — the most advanced piece of India's semiconductor mission to actually break ground. Every dollar of margin the AI boom pours into Micron's balance sheet strengthens the case for deepening that India footprint. For semiconductor professionals weighing a move home, the health of Micron's core business is a direct input into whether the Gujarat bet expands or stalls.

## The catch

Micron has guided to roughly $20 billion in fiscal-2026 capital expenditure, up from about $13.8 billion, and floated a $200 billion long-term commitment to US memory production. HBM fabs take two to three years to come online, which means the company is front-loading spending precisely because it knows the current pricing power will not last forever. The Anthropic deal is a hedge against that day — a way to keep a guaranteed buyer when the supply crunch eventually loosens.

## What's next

The earnings print tonight is the immediate test. Watch the fourth-quarter guidance more than the reported quarter — analysts already expect over $42 billion in revenue next quarter, and any sign that pricing is still climbing would validate the structural thesis. And watch whether the Anthropic template repeats: if Micron signs a second frontier lab to a supply-plus-equity deal, the memory business will have quietly rewritten its own boom-and-bust reputation."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Cognizant Just Wired ServiceNow's AI Agents Into Its Own. The Indian IT Workforce Is the Experiment.",
        "subheadline": "An open-source 'agent orchestrator' lets one company's bots talk to another's. For the millions who staff India's services industry, it is a preview of the job that is being automated.",
        "slug": make_slug("cognizant-servicenow-ai-agents-neuro-orchestration-it-services-nri"),
        "category": "technology",
        "vertical": "it-services",
        "diaspora_angle": "Cognizant employs hundreds of thousands of Indians and is a top sponsor of H-1B workers in the US; its push to make AI agents do cross-platform enterprise work is a direct signal to NRI techies in IT services about which roles get automated first — and which become more valuable.",
        "tags": ["cognizant", "servicenow", "ai-agents", "it-services", "automation", "h1b", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insider Monkey — Cognizant Integrates ServiceNow AI Agents With Neuro AI", "url": "https://www.insidermonkey.com/blog/cognizant-servicenow-ai-agents-neuro-ai-accelerator"},
            {"name": "Cognizant Newsroom — Neuro AI Multi-Agent Accelerator", "url": "https://news.cognizant.com/neuro-ai-multi-agent-accelerator"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Servers in a data centre — the back-end where enterprise AI agents now coordinate work across platforms.",
        "image_attribution": "Pexels",
        "body": """The most consequential enterprise-tech announcements rarely sound dramatic. On June 18, Cognizant said its Neuro AI Multi-Agent Accelerator can now interoperate with ServiceNow's AI agents — meaning a bot built on one company's platform can be orchestrated alongside bots from another vendor, third-party tools, and custom-built systems, all inside a single environment. The phrase to underline is "without manual intervention."

That is the quiet centre of the story. For two decades, the Indian IT services giants — Cognizant, TCS, Infosys, Wipro, HCLTech — built their fortunes on manual intervention: armies of engineers connecting one enterprise system to another, running the help desks, processing the back-office workflows of Western banks and insurers. Cognizant's pitch now is that those connective tasks — registering agents, wiring tools together, coordinating workflows across sales, finance, supply chain and customer service — can be handled by an orchestration layer rather than by people. The accelerator is open-source, which lowers the barrier for clients to adopt it and, not coincidentally, for the work to scale without proportional headcount.

## Why a routine integration matters

Cognizant is not a household name in India the way TCS or Infosys are, but it is one of the largest private employers of Indian technology talent and a perennial top sponsor of H-1B visas in the United States. Its workforce is overwhelmingly Indian, split between delivery centres in Chennai, Hyderabad and Pune and on-site staff in New Jersey, Texas and the UK. When Cognizant signals where it thinks enterprise AI is heading, it is describing the future shape of the single largest employment pipeline for Indian engineers abroad.

And the signal is unambiguous. The industry's own leaders have been split in public. At Infosys's recent AGM, Nandan Nilekani argued AI would expand the services business rather than shrink it. Accenture, by contrast, had its worst week on record this month as investors priced in exactly the opposite fear. Cognizant's move lands on the Accenture side of that argument in practice if not in rhetoric: the value it is selling clients is fewer engineering hours to achieve the same automation.

## The diaspora calculation

For an Indian engineer on an H-1B at a US client site, or a delivery lead in Chennai, the orchestration story splits the workforce into two trajectories.

The roles most exposed are the integration and run-the-system jobs — the L1 and L2 support, the manual workflow stitching, the ticket triage — precisely the high-volume, entry-level work that has historically been the diaspora's foot in the door. If an open-source accelerator can register and coordinate agents across platforms, the headcount needed to do that by hand falls. For the IT services industry, where FY27 outlooks are already softening on AI-automation fears, that is the structural worry analysts keep flagging.

The roles that gain are the ones above the automation line: the architects who design which agents to deploy, the engineers who build the guardrails and audit trails that keep cross-platform workflows compliant, and the client-facing leads who translate a bank's messy reality into something an agent network can run. Cognizant is careful to stress that its framework respects existing access controls and audit logs — compliance work that still needs skilled humans. The diaspora professionals who move toward that work are likely to be more valuable, not less.

## What this means in practice

For NRIs in IT services, the practical takeaways are concrete. First, the H-1B base of the business is the most exposed to agentic automation, which compounds the pressure already coming from Washington's on-and-off visa fee fights. Second, the premium is shifting decisively from "I can integrate two systems" to "I can design and govern a fleet of agents that integrate themselves." Third, the open-source nature of these accelerators means the skill is learnable now, before it becomes a hiring requirement.

For NRI investors, Cognizant and its peers present a genuine fork. The same automation that threatens billable hours can, if the firms reprice their contracts around outcomes rather than headcount, expand margins. Which way it breaks — Nilekani's expansion or Accenture's contraction — is the central question hanging over the entire sector.

## What's next

Watch whether clients actually deploy these multi-agent frameworks in production rather than piloting them, and watch the next round of IT-services earnings for any commentary on headcount. The Cognizant–ServiceNow tie-up is a capability announcement; the workforce consequences show up a few quarters later, in the hiring numbers."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
