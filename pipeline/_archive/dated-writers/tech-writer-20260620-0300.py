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

khosla_body = """Vinod Khosla has made a fortune betting on what comes next. The Sun Microsystems co-founder and early backer of OpenAI rarely talks his own book quietly. So when he told the SparX podcast this month that India's $200-billion IT services and business-process-outsourcing industry "will be gone," the line travelled fast through Bengaluru, Hyderabad and the WhatsApp groups of Indian engineers in New Jersey and the Bay Area.

The timing made it sting. The same week, Accenture — the world's largest IT outsourcer and a bellwether for the Indian firms that follow it — reported its weakest quarterly bookings in six quarters and watched its stock plunge to a nine-year low. The sell-off spread instantly to the Nasdaq-listed shares of Infosys and Wipro, and India's Nifty IT index slid for a fourth straight session, shedding roughly 8% in a week.

## What Khosla actually said

Khosla's argument is blunt: AI agents can now do the application development, testing, maintenance and process work that built India's outsourcing empire, and they can do it faster and cheaper than a billable human. The traditional pipeline — engineering degree, campus placement, a stable IT career — is, in his telling, cracking.

He is not alone in the worry, even inside the industry. Microsoft disclosed that TCS, Infosys and Wipro together now deploy about 300,000 Copilot licences, double the number from December, across more than a quarter of their combined 1.15-million workforce. That is great news for Microsoft. It is a harder story for an industry whose core billing model still charges clients by the head.

The headcount numbers already show the strain. TCS shed more than 23,000 jobs last year in its largest-ever layoff drive. Analysts expect the H-1B wage-weighting rule and the $100,000 consular fee to push even more onshore work offshore, squeezing the entry-level roles that once absorbed waves of fresh graduates.

## Why this lands differently for the diaspora

For Indian Americans, this is not abstract market commentary — it is a story about their cousins, their college batchmates, and in many cases their own first rung in America. The classic NRI journey often ran through one of these firms: a campus offer in Pune or Chennai, an L-1 or H-1B transfer to a client site in Texas or New Jersey, then a green-card queue and a suburb with good schools. That ladder is the one Khosla says is being kicked away at the bottom.

There are two distinct anxieties here. The first is for family back home: parents who measured success by a TCS or Infosys badge are watching the safest career in middle-class India wobble. The second is for the diaspora itself. NRIs hold these stocks directly and through India-focused funds; a structural derating of IT services hits portfolios built on the assumption that Indian tech is a one-way bet.

## The other side of Khosla's case

Khosla did not only deliver a eulogy. He argued India is unusually well-positioned to *deploy* AI across the world's businesses and industries — provided its companies move fast and stop defending the old model. The firms that own client relationships, domain knowledge and data could pivot from selling labour to selling outcomes. Wipro has already built a Bengaluru centre to run Anthropic's Claude; HCLTech has taken a stake in Sarvam, an Indian sovereign-AI startup; Cognizant has wired ServiceNow's AI agents into its own stack.

Whether that pivot arrives fast enough to offset the erosion is the open question. The Indian majors report their first-quarter results in July, and investors who just watched Accenture stumble will be reading the guidance closely. For an Indian engineer at Google wondering whether to jump to a services firm, or an NRI investor deciding whether to add to an India IT position, Khosla's warning is less a prediction than a deadline: adapt, or be automated.

## Sources

The reporting here draws on Khosla's SparX podcast remarks, Microsoft's Copilot deployment disclosure, and market coverage of the Accenture-led IT sell-off."""

tesla_body = """Tesla now has five showrooms in India, and the newest one sits in the most fitting address it could have picked: HITEC City in Hyderabad, the glass-and-steel district where tens of thousands of Indian software engineers — many with siblings and college friends now in the Bay Area — go to work every day. The Experience Center opened to the public on June 17, joining locations in Mumbai's Bandra Kurla Complex, Delhi's Aerocity, Gurugram and Bengaluru's Whitefield.

On display are the two cars Tesla is actually selling in India: the 2026 Model Y Premium Rear-Wheel Drive and the larger, three-row Model Y L. The pricing tells you exactly who the company is courting.

## The price of an American badge

The Model Y RWD starts at ₹50.89 lakh — roughly $61,000 — with EMIs from about ₹39,990 a month. The six-seat Model Y L starts at ₹61.99 lakh, near $74,000. In the United States, the same RWD Model Y stickers well under $50,000. Indian buyers are paying a steep premium, the product of import duties on fully-built cars Tesla still ships in rather than manufactures locally.

That gap is the whole story. Tesla is not yet building in India; it is testing whether enough affluent Indians will pay a luxury-import price for a mainstream-American car. Hyderabad, Bengaluru and the BKC are not random — they are where India's tech wealth and returning-NRI money concentrate.

## Why an NRI in Fremont should care

For the Indian diaspora, Tesla's India rollout is a familiar mirror held up at an odd angle. Many NRIs own a Model Y in California for around $48,000 and now watch family in Hyderabad quoted $61,000-plus for a comparable car. The arbitrage is a recurring diaspora frustration: the same global brand, priced as aspirational luxury back home.

It also matters for anyone tracking the US-India trade conversation. Tesla's reluctance to localise production has been a live point in tariff negotiations; Washington wants lower Indian auto duties, and India wants manufacturing commitments before it grants them. Every showroom Tesla opens without a factory keeps that standoff in view. NRI investors holding Tesla stock are effectively betting on whether Elon Musk eventually builds in India or keeps treating it as an import market.

## A test, not a takeover

Five experience centers in under a year signals intent, not dominance. India's EV market is still small and fiercely price-sensitive, dominated at the affordable end by Tata Motors and, in two-wheelers, by a shaken-out field where Ola Electric just lost half its market share. Tesla is entering at the very top, where competition is thin but so is volume.

The complimentary Wall Connector for orders before June 30, the home-charging support across states, the careful direct-to-consumer playbook — all of it reads like a company gathering data on Indian demand before committing capital. For the diaspora watching from abroad, the more interesting question is not how many Model Ys sell in Hyderabad this quarter. It is whether Tesla's India experiment ends with a factory that finally narrows the price gap their families keep complaining about.

## Sources

Reporting based on Tesla's India announcement of its Hyderabad Experience Center and coverage of its India pricing and retail footprint."""

apple_body = """India will assemble roughly a quarter of the world's iPhones this year — about 26%, up from just 6% four years ago, according to Counterpoint Research. It is the clearest proof yet that Apple's bet on diversifying away from China is real. It is also, increasingly, a story about how hard that bet is to pull off.

The latest reminder came from Tamil Nadu, where India's pollution board issued a notice to a Tata-run iPhone components factory, alleging that wastewater from the plant contaminated farmland and groundwater. The board asked Tata to explain why power to the unit should not be cut and the facility shut. Apple, which enforces strict supplier rules on wastewater, did not comment.

## A supply chain still learning to walk

The pollution notice is the newest entry in a lengthening list of growing pains. A fire briefly halted component production at Tata's Hosur plant in 2024. Earlier this year, Foxconn recalled more than 300 Chinese engineers and technicians from its southern India facilities — the experienced hands who had been training local staff — in a move widely read as Beijing quietly resisting the migration of manufacturing know-how. Apple deliberately excluded Chinese suppliers from its India build-out; that choice is now being stress-tested.

None of these has derailed the larger trajectory. India crossed 20% of global iPhone output and kept climbing. But each incident underlines the same truth: China spent two decades perfecting iPhone assembly. India is about five years in, and the gap shows up in line efficiency, training depth and supplier maturity rather than in the phone you eventually buy.

## The diaspora angle: this is your family's job market

For Indian Americans, Apple's India push is one of the most tangible ways the "India rising" narrative becomes real economics. The Tamil Nadu and Karnataka plants employ hundreds of thousands of workers and anchor a components ecosystem that is creating exactly the kind of skilled manufacturing jobs India has long wanted to keep. Many NRIs have family in these states; the factories changing their hometowns' economies are the ones making the phone in their pocket.

There is an investment dimension too. The Tata Group is now the only domestic Indian iPhone assembler, and its electronics arm is scaling fast. NRIs who track Indian equities — or who follow the US-listed Apple supply chain — are watching whether India can convert assembly volume into genuine, higher-value manufacturing, or whether it stays a final-assembly stop while the valuable components are still imported.

## What's next

The pressure points are not going away. China is making it harder for skilled labour to leave; India's regulatory and environmental scrutiny is real and, in the Tata case, biting; and Apple is racing to localise displays and enclosures it still largely imports. Tim Cook has already warned that the next iPhone will cost more, blaming an AI-driven memory-chip crunch that runs partly through Micron's Indian-American CEO Sanjay Mehrotra — a reminder that the device sits at the intersection of half a dozen India-linked stories at once.

For the diaspora, the takeaway is not whether India hits 30% of iPhone output next year. It is that the messy, contested process of getting there — pollution notices, recalled engineers, supplier learning curves — is the real shape of India's manufacturing ambition, and it is unfolding in the towns their families still call home.

## Sources

Reporting draws on Reuters coverage of the Tata factory pollution notice, Counterpoint Research data on India's share of iPhone output, and earlier reporting on Foxconn's recall of Chinese engineers from its India plants."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Vinod Khosla Says India's $200 Billion IT Industry 'Will Be Gone.' The Diaspora's Oldest Career Ladder Is Wobbling.",
        "subheadline": "The Silicon Valley investor's warning landed the same week Accenture cratered and Infosys and Wipro shares tumbled — and it hits the exact path many NRIs took to America.",
        "slug": make_slug("vinod-khosla-india-it-industry-ai-disruption-tcs-infosys-wipro-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The TCS-to-H-1B-to-green-card pipeline was the classic NRI on-ramp to America; Khosla's warning that AI agents will gut Indian IT threatens both the careers of family back home and the portfolios of diaspora investors betting on Indian tech.",
        "tags": ["ai", "indian-tech", "it-services", "vinod-khosla", "h1b", "tcs-infosys-wipro"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint — Khosla warns India's IT industry will be gone", "url": "https://www.livemint.com/market/stock-market-news/india-200-billion-it-industry-gone-vinod-khosla-ai-agents-tcs-infosys-wipro-11718700000000.html"},
            {"name": "Mint — AI jitters trigger another sell-off in IT stocks", "url": "https://www.livemint.com/market/stock-market-news/ai-jitters-trigger-another-sell-off-in-it-stocks-accenture-infosys-wipro-11718600000000.html"},
            {"name": "Mint — TCS, Infosys, Wipro double Copilot AI licences", "url": "https://www.livemint.com/companies/news/tcs-infosys-wipro-double-copilot-ai-licences-microsoft-11718000000000.html"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/2024-03-14_SXSW_Vinod-Khosla_08741.jpg/3840px-2024-03-14_SXSW_Vinod-Khosla_08741.jpg",
        "image_caption": "Vinod Khosla, Sun Microsystems co-founder and venture capitalist, speaking at SXSW in 2024.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": khosla_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tesla Opened Its Fifth India Showroom in a Tech Hub Full of Future NRIs. The Price Tag Tells You Who It's Really For.",
        "subheadline": "The new Hyderabad Experience Center sells a Model Y for around $61,000 — far above its US price — as Tesla tests Indian demand without yet building a factory.",
        "slug": make_slug("tesla-india-fifth-showroom-hyderabad-model-y-price-nri-ev"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who bought a Model Y in California for under $50,000 are now watching family in Hyderabad get quoted $61,000-plus for the same car — a vivid example of import-duty arbitrage and a live issue in US-India trade talks Tesla investors are tracking.",
        "tags": ["tesla", "ev", "india", "model-y", "us-india-trade", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "FoneArena — Tesla opens 5th experience center in India in Hyderabad", "url": "https://www.fonearena.com/blog/tesla-fifth-experience-center-india-hyderabad-2026.html"},
            {"name": "The Hindu BusinessLine — Tesla opens first experience center in Hyderabad", "url": "https://www.thehindubusinessline.com/companies/tesla-opens-first-experience-center-in-hyderabad/article2026.ece"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12554294/pexels-photo-12554294.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Tesla electric vehicle on display in a brand showroom.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": tesla_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Will Build a Quarter of the World's iPhones This Year. A Pollution Notice Shows How Hard the Climb Still Is.",
        "subheadline": "Apple's bet to diversify out of China is working — but a Tata factory notice, recalled Foxconn engineers and a steep supplier learning curve reveal the growing pains behind the headline.",
        "slug": make_slug("apple-india-iphone-manufacturing-tata-foxconn-supply-chain-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Apple's Tamil Nadu and Karnataka plants are reshaping the hometown economies of millions of NRIs' families, turning the 'India rising' story into tangible skilled-manufacturing jobs — and a live bet for diaspora investors on whether India moves beyond final assembly.",
        "tags": ["apple", "iphone", "india-manufacturing", "foxconn", "tata-electronics", "supply-chain"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Tata's iPhone parts factory contaminated farmland water, India pollution body alleges", "url": "https://www.reuters.com/business/tata-iphone-parts-factory-contaminated-farmland-water-india-pollution-body-2026.html"},
            {"name": "Stocktwits — Apple's India iPhone ambitions hit by Foxconn staff recall", "url": "https://stocktwits.com/news-articles/markets/equity/apples-india-iphone-ambitions-hit-by-foxconn-staff-recall-report"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A worker assembles electronic components on a manufacturing line.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": apple_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
