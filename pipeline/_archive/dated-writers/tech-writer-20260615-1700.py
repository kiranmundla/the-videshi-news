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
        "headline": "Satya Nadella Has a Warning for the AI Gold Rush: Don't Hand Your Company's Brain to a Stranger",
        "subheadline": "Microsoft's CEO says the winners of the AI era won't be the firms with the best model, but the ones that own their own 'learning loop.' For the millions of Indians building that infrastructure, it reframes the whole job.",
        "slug": make_slug("satya-nadella-frontier-ecosystem-human-token-capital"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tens of thousands of Indian engineers build the very AI platforms Nadella warns companies not to over-rely on, and his 'human capital plus token capital' framing is a direct argument for why their judgment still matters as the tools get smarter.",
        "tags": ["satya-nadella", "microsoft", "ai", "indian-tech", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/microsoft-ceo-satya-nadella-issues-stark-warning-on-future-of-business-ai-firms-could-capture-all-the-value-11750000000000.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/microsoft-ceo-calls-for-frontier-ai-ecosystem-to-ensure-broad-value-creation-across-economies/article69000000.ece"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/cant-let-few-ai-models-eat-everything-they-see-capture-all-returns-satya-nadella"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft Chairman and CEO Satya Nadella, who warned that a few AI providers could capture most of the economy's value",
        "image_attribution": "Wikimedia Commons",
        "body": """Satya Nadella spent the weekend doing something Microsoft's chief executive rarely does in public: warning customers about the very technology his company sells.

In a long post on X, Nadella argued that the firms that win the artificial-intelligence era will not be the ones renting the most powerful model. They will be the ones that build a unique "learning system" on top of those models — encoding their own expertise, decisions and institutional memory into something they own. A frontier model, he wrote, is like an engine. The real differentiator is the vehicle built around it. "A frontier without an ecosystem is not stable."

The blunter version came a sentence later. The world, he said, cannot let "a small number of centralised AI systems" eat everything they see and capture all the economic returns. "In my view, our priority has to be building a frontier ecosystem, not just a frontier model, so value flows broadly across every company, every industry, and every country."

It is a striking thing to hear from the man running one of the two or three companies most likely to be that small number.

### Human capital, and a new kind of capital

Nadella's framework rests on a coinage. Every company, he argues, will have to build two things. The first is **human capital** — the knowledge, judgment, relationships and pattern recognition of its people. The second is **token capital**, his term for the AI capability a firm builds and owns rather than borrows. The trap, in his telling, is assuming the second makes the first obsolete. It does not. "Human agency will be the driver of token capital growth," he wrote. "Without human direction, you have compute running in circles."

He has been circling this idea for a week. Days earlier he described "tokenmaxxing" — maximising AI token usage for its own sake — as "addictive," admitting Microsoft's own engineers do "a lot" of it, before cautioning: "Don't use frontier models for non-frontier problems." The throughline is a man trying to slow a stampede he helped start, asking enterprises to think about what they might quietly lose by outsourcing their thinking to a platform they do not control.

### Why an NRI engineer should read past the philosophy

For the large population of Indian-origin technologists inside the American AI machine, this is not abstract. They are disproportionately the people building Azure, Copilot and the customer deployments that sit on top — the literal construction crew for the "frontier ecosystem" Nadella describes. His argument is, in effect, a defence of their continued relevance against the louder narrative that AI will hollow out engineering jobs.

The logic cuts against the layoff panic. If the durable advantage is the learning loop — the judgment about *which* problems to point a model at, how to wire it into a business, what to keep in-house — then the premium shifts toward exactly the senior engineering and product judgment that experienced Indian professionals at Microsoft, Google and the enterprise-software belt have spent careers accumulating. Nadella is essentially telling the market that the commodity is the model, not the people who know how to deploy it.

There is a second audience: the Indian IT services giants. TCS, Infosys, Wipro and HCLTech sell exactly the integration layer Nadella is describing, and they have spent the past month fending off fears of "AI deflation" eating their margins. HCLTech just put $150 million into the Indian AI startup Sarvam, a bet on owning model capability rather than renting it — token capital, in Nadella's vocabulary, made literal. His framing hands these firms a sales pitch: the future is not the model, it's the loop, and building loops is what Indian IT has always done.

### The skeptic's footnote

It is worth holding the messenger at arm's length. Microsoft is a primary beneficiary of the centralisation Nadella warns against; its OpenAI stake and Azure dominance make it one of the gatekeepers most likely to "capture all the value." A warning against concentration, delivered by one of the concentrators, doubles as a competitive moat — encouraging every enterprise to build deep, sticky, Azure-shaped learning loops rather than shopping around.

But the underlying point survives the scrutiny. For an Indian engineer in Redmond, Bangalore or New Jersey wondering whether the next model release makes them redundant, Nadella's answer is unusually direct: the model is the engine, you are still the driver, and the firms that forget that will spend the decade running compute in circles."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wanted Apple's Factories. Now One of Them Is Accused of Poisoning the Wells Next Door.",
        "subheadline": "A Tata plant making iPhone parts near Bengaluru faces a shutdown threat over alleged groundwater contamination — a test of whether 'Make in India' can clear the bar its own farmers are setting.",
        "slug": make_slug("tata-apple-iphone-plant-hosur-groundwater-pollution"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Every NRI cheering India's rise as Apple's factory floor now has to reckon with the cost: the Tata plant central to that story stands accused of contaminating the farmland around it, and how India handles it signals whether the manufacturing boom is built to last.",
        "tags": ["tata-electronics", "apple", "make-in-india", "iphone", "manufacturing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-officials-survey-farms-around-tata-iphone-parts-plant-after-water-pollution-2026-06-15/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/tatas-iphone-parts-factory-contaminated-farmland-water-india-pollution-body-2026-06-13/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/13974251/pexels-photo-13974251.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Electronics assembly work of the kind Tata's Hosur plant performs for Apple's iPhone supply chain",
        "image_attribution": "Pexels",
        "body": """The factory near Hosur, 25 miles south of Bengaluru, is exactly the kind of place India has spent years courting. It makes back panels and other components for the iPhone. It belongs to Tata Electronics, now the second-biggest Apple supplier in South Asia after Taiwan's Foxconn and the centrepiece of Apple's campaign to build phones somewhere other than China. It is, in the official telling, the future.

On Monday, three district officials were instead walking the fields behind it, trailed by farmers pointing at their wells.

India's Tamil Nadu Pollution Control Board has warned Tata that it faces a forced shutdown unless it can explain why wastewater from the plant appears to have contaminated groundwater in adjacent agricultural land. According to a regulatory notice dated May 25 and reviewed by Reuters, five state inspections between December 2025 and May 2026 found that the plant discharged wastewater into an internal rainwater harvesting pond — which then overflowed and tainted "the open wells located in the adjacent agricultural lands." The board says Tata took no corrective action after an earlier instruction issued in December.

Tata disputes the finding. The company says an independent, accredited laboratory conducted its own analysis and concluded it was "in full compliance with all regulatory norms," and that it is "committed to responsible business practices and protection of the environment and local communities." Apple and Tata did not respond to Reuters' questions about Monday's survey.

### The farmers' version

The people who live next to the plant tell a less tidy story. P. Pushparaj, a farmer near the site, said he filed a complaint after noticing the discharge was "dirty and had a bad smell," and suspected it had hurt his crops. "We continued our agriculture, but we didn't get proper yields," he said. The district official leading Monday's walk, N. Velu, would say only: "We are here to assess the situation."

That gap — between a corporate lab certifying compliance and a farmer watching his yields fall — is the whole story in miniature. It is also the kind of dispute that India's manufacturing ambitions have not had to litigate at scale until now, because India has not had factories at this scale until now.

### Why this lands differently for the diaspora

For Non-Resident Indians, the rise of India as Apple's alternative to China has been a point of genuine pride and, increasingly, a thesis. It shows up in the stock case for Tata Group companies, in the bet that India can capture the electronics supply chain leaving China, in the broader story an NRI tells about the country they left being ready for the big leagues. The Hosur plant is a load-bearing part of that narrative.

Which is exactly why this matters beyond one factory. The question facing India is not whether it can attract the factories — it plainly can. It is whether it can run them to the standard that keeps them. Apple's supply-chain audits are notoriously exacting about labour and environmental compliance; a contamination finding that triggers a regulatory shutdown is the sort of thing that makes a procurement team in Cupertino quietly rebalance orders back toward Vietnam or Foxconn. The "China plus one" strategy that benefits India is not loyalty. It is a hedge, and hedges move.

There is a harder version of the diaspora question, too. Many NRIs left precisely the kind of place where industrial growth and environmental cost were treated as a fair trade — where a plant that fed the local economy was allowed to foul the local water because the jobs were worth it. Watching India climb the manufacturing ladder forces the question of whether the new India repeats that bargain or refuses it. A pollution board threatening to shut a marquee Apple supplier over a few farmers' wells is, in its own way, a sign of the second. Whether the threat holds is the part worth watching.

### What happens next

Tata now has to satisfy the pollution board or risk the shutdown. The likeliest outcome is a remediation order and continued operation — regulators rarely close flagship plants outright. But the episode has already done something useful: it has put a number on the unglamorous part of "Make in India." Building the factories was the easy half. Proving they can sit next to a working farm without ruining it is the half that decides whether the boom is durable — and whether the diaspora's pride in it is well placed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Zepto Wants $10 Billion and Has 10 Months of Cash. India's First Pure Quick-Commerce IPO Is a Dare.",
        "subheadline": "The Bengaluru 10-minute-delivery firm filed updated IPO papers to raise about ₹8,700 crore, with revenue up fivefold to ₹22,623 crore — and losses up nearly as fast. NRI investors get a front-row seat to a very Indian bet.",
        "slug": make_slug("zepto-ipo-drhp-quick-commerce-india-valuation"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Zepto is the first pure-play quick-commerce company to test India's public markets, and with US backers like Contrary and Kaiser Permanente cashing out, NRI investors weighing an India allocation have to decide whether 10-minute delivery is a business or a cash bonfire.",
        "tags": ["zepto", "ipo", "quick-commerce", "indian-startups", "nri-investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/market/stock-market-news/zeptos-roadshow-offers-clues-to-quick-commerces-next-phase-11750000000001.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indian-quick-commerce-firm-zepto-raise-up-837-million-ipo-2026-06-08/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/zepto-files-updated-ipo-papers-with-sebi-plans-8010-crore-fresh-issue/article69000001.ece"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7843985/pexels-photo-7843985.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A grocery fulfilment warehouse of the kind that powers quick-commerce 'dark store' networks",
        "image_attribution": "Pexels",
        "body": """The numbers in Zepto's updated prospectus read like two different companies stapled together. Revenue from operations grew roughly fivefold in two years, from ₹4,454 crore in FY24 to ₹22,623 crore in FY26. Losses, over the same stretch, widened nearly as fast — to ₹5,905 crore. The Bengaluru quick-commerce firm is now asking public investors to fund its next phase at a valuation reported to be around $7 billion, with some accounts putting the target as high as $10 billion. By one analysis, it has about ten months of cash runway left.

This is the deal on the table. Zepto filed its updated draft red herring prospectus with India's market regulator, SEBI, on June 8, proposing a fresh issue of ₹8,010 crore and an offer-for-sale of up to 113 million shares. It is targeting a July listing, which would make it the third quick-commerce player to go public in India after Eternal (which owns Blinkit) and Swiggy — and, notably, the first *pure-play* quick-commerce company to list. There is no food-delivery business or restaurant marketplace underneath to soften the story. It is 10-minute delivery, standing on its own, asking to be judged.

### Who's getting out

The offer-for-sale tells you who believes the story has peaked for them. The selling shareholders include Nexus Ventures, US-based Contrary Capital, Dubai's Razor Capital, and — strikingly — Kaiser Foundation Hospitals and the Kaiser Permanente Group Trust, the American healthcare giant's investment arms. The promoters — founders Aadit Palicha and Kaivalya Vohra, along with their family trusts — are not selling a single share.

That split is the most honest signal in the filing. The founders are holding; some of the earliest and most sophisticated outside money is taking the exit the IPO provides. Neither is a verdict. Both are information.

### The case, and the case against

The bull case is straightforward: India's urban consumer has been trained, fast, to expect groceries and increasingly everything else in ten minutes, and Zepto has 1,139 dark stores — the compact neighbourhood warehouses that make the speed possible — to serve that habit. Revenue doubling year over year is not a rounding error. Investment bankers noted that Zepto's roadshow disclosed unusually granular unit economics, including customer-acquisition cost, which one called a "willingness to be judged on those metrics later in the public market." Companies hiding the ball do not usually volunteer the ball.

The bear case is the runway. A firm burning enough to lose ₹5,900 crore a year, with rising customer-acquisition costs and roughly ten months of cash, is not raising capital because it wants to. The IPO proceeds go heavily toward more dark stores and the lease payments on existing ones — growth that has not yet shown it can turn profitable. And the competition is brutal and well-funded: Blinkit sits inside the ₹26.9-billion-dollar Eternal, Swiggy Instamart inside a $7.8-billion parent, plus Amazon, Flipkart and Tata's BigBasket all crowding the same ten-minute window.

### What an NRI investor should actually weigh

For the diaspora investor building an India allocation, Zepto is a clean test of conviction. Quick commerce is one of the genuinely new things India's internet economy has produced — not a copy of a Western model but a category India scaled first and hardest. Owning a piece of that has obvious appeal for anyone whose thesis is that India's consumption story is the trade of the decade.

But the structure rewards caution. This is a loss-making company listing into a competitive bloodbath, with early institutional backers heading for the door and a cash clock ticking audibly in the background. The relevant comparison is the recent record of Indian new-age IPOs, which have been volatile and frequently underwater for retail buyers who chased the listing-day pop. An NRI cannot simply click "buy" on a US brokerage either; participation typically runs through an NRE/NRO account and the foreign-portfolio or NRI investor route, with its own KYC and tax friction — short-term capital gains on Indian equity are taxed at 20%, and there are repatriation rules to track.

The cleaner read may be to treat the IPO as a data point rather than a position. How Zepto prices, who anchors it, and how it trades in its first months will say more about whether India's quick-commerce boom is a business or a beautifully funded experiment than any roadshow deck can. For most diaspora investors, watching that answer arrive is cheaper than paying ₹10 billion to find out."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
