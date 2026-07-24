#!/usr/bin/env python3
"""Technology writer — 2026-07-06 06:00 PDT run"""

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


# ──────────────────────────────────────────
# ARTICLE 1: Indian IT Q1 Earnings "Perfect Storm"
# ──────────────────────────────────────────

art1_body = """\
India's largest software exporters are walking into earnings season with the wind blowing straight into their faces. Tata Consultancy Services reports its April-to-June results on Thursday, kicking off what nine brokerages have already warned will be a thoroughly underwhelming quarter for the country's $315 billion IT sector.

The numbers tell a sobering story. While India's top six IT firms — TCS, Infosys, HCLTech, Wipro, Tech Mahindra, and LTIMindtree — are expected to post around 14 per cent year-on-year revenue growth in rupee terms, nearly all of that is a mirage created by the rupee's sharp depreciation against the dollar. Strip out the currency effect, and constant-currency revenue growth collapses to a mere 2.8 per cent.

**A storm with three fronts**

Nomura's analysts called it a "perfect storm," and the metaphor holds. The first front is AI-driven pricing pressure. As companies across the globe deploy AI tools and agents to cut costs and accelerate software development, the traditional IT services model — built on billing for engineer-hours — is being squeezed. Clients want more done with fewer people, and they want it cheaper.

The second is macroeconomic caution. Enterprise technology budgets have not recovered from the austerity that took hold during 2024's geopolitical shocks. JPMorgan now sees Indian IT revenue growth staying below 3-4 per cent for the "foreseeable future." Citi expects a fourth consecutive year of subdued growth.

The third is geopolitical turbulence. Middle East tensions, continued US-China friction, and uncertainty around trade policy have made corporate boards reluctant to green-light the large, multi-year digital transformation projects that Indian IT firms depend on.

**The AI agent paradox**

Perhaps the most unsettling signal comes from TCS's own chairman, N. Chandrasekaran, who recently said the "day is not far" when the company would have an equal number of AI agents and employees. TCS cut more than 12,000 jobs last July and saw headcount fall by 23,000 on a net basis in the fiscal year ended March 2026.

This is the paradox at the heart of the Indian IT story. The same AI that could unlock new consulting revenue is simultaneously cannibalising the labour-intensive delivery model that built these companies. Fears about this structural disruption dragged the Nifty IT index down 9.5 per cent in the June quarter, even as India's broader Nifty 50 gained 6.9 per cent.

**What NRI investors should watch**

For the Indian American community — which holds significant positions in TCS, Infosys, and Wipro through direct equity, ADRs, and retirement portfolios — this earnings week is a litmus test. The questions that matter are not about this quarter's numbers, which are already baked in. They are about forward guidance.

Will TCS signal that its AI consulting pipeline is converting to revenue? Will Infosys revise its FY27 guidance downward or hold the line? Can HCLTech's enterprise software bets provide a counter-narrative?

And for the estimated 5.9 million people employed by India's IT sector — including hundreds of thousands whose careers are intertwined with the diaspora through H-1B pathways, GCC rotations, and onsite deployments — the answer to one question matters more than any earnings number: is the industry adapting fast enough, or is the storm still building?

TCS reports on July 10. Infosys, HCLTech, and Wipro follow later in the month.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's IT Giants Walk Into Earnings Week Facing a 'Perfect Storm.' The Numbers Already Look Bleak.",
    "subheadline": "Nine brokerages warn of just 2.8% constant-currency growth as AI pricing pressure, weak client budgets, and Middle East turbulence converge. TCS reports Thursday.",
    "slug": make_slug("india-it-giants-perfect-storm-q1-earnings-tcs"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors hold significant positions in TCS, Infosys, and Wipro through ADRs and retirement portfolios — this earnings week tests whether the sector's structural shift has a floor.",
    "tags": ["tcs", "infosys", "indian-it", "ai", "earnings", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-it-firms-face-muted-q1-ai-shift-weak-demand-weigh-2026-07-06/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/top-it-companies-likely-to-post-subdued-q1-fy27-revenue-growth-says-brokerage"},
        {"name": "Reuters (April preview)", "url": "https://www.reuters.com/world/india/indian-it-firms-near-term-outlook-muted-clients-cut-spending-ai-risks-mount-2026-04-24/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Server racks in a modern data center, the infrastructure backbone of India's $315 billion IT services industry",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}


# ──────────────────────────────────────────
# ARTICLE 2: Persistent Systems × Nagarro
# ──────────────────────────────────────────

art2_body = """\
When Persistent Systems offered 81 euros per share for Munich-based Nagarro — a 140 per cent premium to the stock's undisturbed closing price — the market did not reward the ambition. Persistent's shares fell 11 per cent, hitting a near 15-month low. The deal, valued at $1.45 billion including debt, is the largest acquisition by a mid-tier Indian IT firm in years.

The question is whether it is a stroke of strategic genius or an expensive gamble at exactly the wrong time.

**The logic: buy what you cannot build fast enough**

Artificial intelligence is rewriting the competitive map of Indian IT. The traditional model — recruit thousands of engineers, train them on a client's systems, bill by the hour — is under existential pressure from AI-driven automation. Companies that lack specialised AI, cloud, and digital engineering capabilities risk becoming irrelevant within a few years.

Persistent, led by founder and chairman Anand Deshpande and CEO Sandeep Kalra, decided that building those capabilities organically would take too long. Nagarro, with roughly $1 billion in annual revenue, 18,500 employees, and deep roots in European enterprise clients, offers a shortcut. Nearly half of Nagarro's revenue comes from European customers — a market where Persistent currently earns just a tenth of its business.

"AI is reshaping our industry at an unprecedented pace," Deshpande said in the announcement. "Together, Persistent and Nagarro will be better positioned to help our clients navigate this new era."

**The combined entity: a $2.9 billion mid-tier powerhouse**

The deal would vault Persistent past Mphasis and Coforge to become India's seventh-largest IT services company, with combined revenue of roughly $2.9 billion. The acquisition follows Coforge's own $2.35 billion purchase of Encora earlier this year, signalling that India's mid-tier IT firms are on an aggressive M&A spree to acquire what AI demands: specialised talent, product engineering depth, and global delivery scale.

Barclays is backing the deal with €1.4 billion in committed financing. Persistent has already secured a roughly 21 per cent stake through a share purchase agreement with Nagarro's largest shareholder, Lantano Beteiligungen. Nagarro's management and supervisory boards support the transaction and intend to recommend acceptance.

**Why Wall Street is divided**

The analyst response has been strikingly polarised. CLSA maintained an outperform rating with a target of ₹6,520, arguing the deal values Nagarro at just 1.2x EV/sales — cheap by any standard for a digital engineering firm. PL Capital and Motilal Oswal also backed the acquisition.

But Citi retained a sell rating at ₹4,090, calling the deal expensive given Nagarro's historical growth trajectory. Equirus flagged "limited margin for execution errors," and Kotak set a reduce target of ₹4,700. The concerns are legitimate: Nagarro's margins have trailed Persistent's, and integration of a German firm with an Indian one — across cultures, time zones, and regulatory regimes — is notoriously difficult.

The BaFin angle adds intrigue. Nagarro's stock surged nearly 20 per cent on the Friday before the deal was announced, prompting CEO Manas Human to say he expects Germany's financial watchdog to investigate. Both Human and Kalra insist the planning teams were kept as small as possible.

**The diaspora lens**

For Indian Americans tracking India's tech evolution, this deal is a bellwether. Persistent, headquartered in Pune, employs thousands of engineers across the US and has been a beneficiary of the same GCC and nearshore trends that have reshaped Indian tech staffing. The Nagarro acquisition is a bet that Indian companies can compete not just on cost, but on capability — that a Pune-born firm can absorb a Munich-based one and emerge as a credible global AI engineering house.

If it works, it writes a playbook for the rest of the sector. If it stumbles, it becomes a cautionary tale about overpaying at the top of the AI hype cycle. Either way, the deal marks a decisive moment: Indian IT is no longer content to be the world's back office. It wants the front room.

Completion is expected by early 2027, pending regulatory approvals and shareholder acceptance.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Persistent Systems Just Made India's Boldest AI Bet — a $1.4 Billion Gamble on a German Software Firm",
    "subheadline": "The Pune-based IT company offered a 140% premium for Munich's Nagarro, splitting Wall Street down the middle. The deal could reshape India's mid-tier tech sector — or become its most expensive mistake.",
    "slug": make_slug("persistent-systems-nagarro-acquisition-indian-it-ai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Persistent employs thousands across the US and India — this acquisition tests whether Indian IT firms can compete on AI capability, not just cost, setting a precedent NRI investors and tech workers are watching closely.",
    "tags": ["persistent-systems", "nagarro", "indian-it", "mergers-acquisitions", "ai", "europe"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Mint", "url": "https://www.livemint.com/companies/news/can-billion-dollar-acquisitions-help-indian-it-firms-in-the-ai-era-11751612969671.html"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/persistent-systems-to-acquire-nagarro-envisions-global-ai-powerhouse-of-29-billion/article69739363.ece"},
        {"name": "Reuters Breakingviews", "url": "https://www.reuters.com/breakingviews/it-deal-manifests-saaspocalypse-opportunity-2026-07-03/"},
        {"name": "Verdict", "url": "https://www.verdict.co.uk/persistent-nagarro-acquisition/"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Ravi_Shankar_Prasad_administering_the_oath_of_secrecy_and_office_as_part_time_member_of_UIDAI_to_Shri_Anand_Deshpande%2C_Founder_%26_CEO%2C_Persistent_Systems%2C_in_New_Delhi.jpg/1280px-thumbnail.jpg",
    "image_caption": "Anand Deshpande, founder and chairman of Persistent Systems, who announced the company's biggest acquisition",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ──────────────────────────────────────────
# ARTICLE 3: AI Infrastructure / Memory Chips / Micron
# ──────────────────────────────────────────

art3_body = """\
Wall Street has been fixated on the Magnificent Seven all year. But a new UBS research note argues the real money in artificial intelligence is being made somewhere else entirely — in the companies that build the physical infrastructure the AI economy runs on. And one of the biggest beneficiaries is led by an Indian-American.

Sanjay Mehrotra's Micron Technology has risen more than 200 per cent this year. SK Hynix is up nearly 980 per cent over the past twelve months. Samsung's semiconductor division has surged 190 per cent. Meanwhile, the Magnificent Seven — Apple, Microsoft, Nvidia, Amazon, Alphabet, Meta, and Tesla — are collectively flat, down roughly 1 per cent since January.

UBS calls the divergence "extraordinary."

**The bottleneck thesis**

The investment case is deceptively simple. Every AI data centre needs two things in enormous quantities: computing power and memory. The computing side — dominated by Nvidia's GPUs — has been well understood by the market for years. The memory side has not.

High-bandwidth memory (HBM) chips, which sit next to GPUs and feed them the data they need to function, are now the binding constraint on AI infrastructure. Demand has outstripped supply so dramatically that memory chip prices have surged, driving Micron's DRAM revenue up 74 per cent sequentially in its most recent quarter — almost entirely from price increases, not volume growth.

J.P. Morgan analysts described these memory firms as companies that "own the bottleneck," arguing that "relentless demand turns scarcity into outsized returns." UBS's Holt research arm quantified the shift: economic profit for AI infrastructure companies — defined as semiconductors, semiconductor equipment, and US tech hardware excluding Apple — is forecast to surge from $200 billion in 2023 to $1.4 trillion by 2027, a 600 per cent jump. For the hyperscalers, the same metric moves from $200 billion to just $400 billion.

Memory stocks alone account for roughly half of the infrastructure group's projected gains.

**The Mehrotra factor**

Sanjay Mehrotra, who co-founded SanDisk in 1988 and took the helm at Micron in 2017, has quietly positioned the Boise, Idaho-based company at the centre of the AI supply chain. Micron is one of only three companies in the world capable of producing HBM at scale, alongside SK Hynix and Samsung.

For the Indian diaspora, Mehrotra's story carries particular resonance. Born in Kanpur, educated at the University of California, Berkeley, he built SanDisk into a flash memory pioneer before its $19 billion sale to Western Digital. At Micron, he has bet the company on AI infrastructure — and it is paying off. The firm's market capitalisation has crossed $1 trillion, placing it among the most valuable semiconductor companies on earth.

Micron is also building a $2.75 billion semiconductor assembly and test facility in Gujarat's Sanand industrial area, the first major American chipmaker to establish manufacturing operations in India under the country's semiconductor incentive programme. When operational, the plant will package advanced memory chips for AI and data-centre applications, creating thousands of engineering jobs in a region the Indian government is trying to position as a global chip hub.

**What this means for NRI investors**

The UBS note carries a clear portfolio implication. NRI investors who have been riding the Magnificent Seven may be overweight the companies spending on AI and underweight the companies supplying them. The hyperscalers — Google, Amazon, Meta, Microsoft — have committed hundreds of billions to AI data centres, but those capital expenditures are compressing their own returns on investment. The infrastructure suppliers, by contrast, are capturing the spending with pricing power that has no obvious ceiling while supply remains constrained.

UBS expects DRAM supply to remain tight until at least mid-2028. If that forecast holds, the current memory supercycle may have years left to run — and the Indian-American co-founder who bet on it three decades ago will have been proved right at a scale few imagined.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Wall Street Says the Real AI Money Isn't in the Magnificent Seven. It's in Memory Chips — and Sanjay Mehrotra's Micron Is Leading.",
    "subheadline": "UBS calls the shift 'extraordinary': AI infrastructure stocks are creating $1.4 trillion in economic value while the hyperscalers generate just $400 billion. The Indian-American CEO building a chip plant in Gujarat is at the centre of it.",
    "slug": make_slug("micron-sanjay-mehrotra-ai-memory-chips-infrastructure"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Micron CEO Sanjay Mehrotra, born in Kanpur, is leading one of the AI era's biggest winners — and building a $2.75B chip plant in Gujarat that could create thousands of Indian engineering jobs.",
    "tags": ["micron", "sanjay-mehrotra", "semiconductors", "ai-infrastructure", "memory-chips", "india-semiconductor", "nri-investors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "MarketWatch / UBS", "url": "https://www.marketwatch.com/story/ai-infrastructure-stocks-have-overtaken-the-tech-hyperscalers-in-a-shift-ubs-calls-extraordinary-9ee61fa9"},
        {"name": "Morningstar / UBS", "url": "https://www.morningstar.com/news/marketwatch/20260703195/ai-infrastructure-stocks-have-overtaken-big-tech-hyperscalers-in-an-extraordinary-shift-says-ubs-research-arm"},
        {"name": "Barron's / J.P. Morgan", "url": "https://www.barrons.com/articles/micron-ai-bottleneck-stocks-nvidia-sk-hynix-broadcom-55cac10c"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/stock-markets/micron-samsung-sk-hynix-tsmc-nvidia-when-bits-and-bytes-take-a-large-bite-of-the-stock-markets/article69617023.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
    "image_caption": "Sanjay Mehrotra, CEO of Micron Technology, whose bet on AI memory chips has made the company one of the decade's biggest winners",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip(),
}


# ──────────────────────────────────────────
# INSERT ALL
# ──────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
