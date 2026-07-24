#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Called IBM's Indian-Born CEO a 'Legend.' Now He's Handed Arvind Krishna's Quantum Bet a Federal Tailwind.",
        "subheadline": "Two new White House executive orders fast-track a working quantum computer by 2028 and post-quantum encryption by 2031 — and IBM, run by a Chennai-trained engineer, is the named beneficiary.",
        "slug": make_slug("arvind-krishna-ibm-quantum-trump-executive-orders-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "An IIT Kanpur graduate now runs the company Washington is leaning on to win the quantum race — a milestone for Indian-American engineers and a signal to NRIs holding IBM stock or eyeing quantum careers.",
        "tags": ["quantum-computing", "ibm", "arvind-krishna", "indian-tech", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ibm-stock-jpmorgan-upgrade-quantum"},
            {"name": "CoinCentral", "url": "https://coincentral.com/ibm-stock-jumps-4-as-jpmorgan-upgrades-and-trump-backs-quantum-push/"},
            {"name": "IANS", "url": "https://ianslive.in/us-accelerates-race-for-quantum-leadership"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Arvind_Krishna_at_SXSW_2025.jpg/1280px-Arvind_Krishna_at_SXSW_2025.jpg",
        "image_caption": "IBM chief executive Arvind Krishna speaking at SXSW in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """When President Donald Trump signed two executive orders on quantum computing in the Oval Office this week, the cameras caught a familiar face among the executives looking on: Arvind Krishna, the Chennai-trained engineer who has run IBM since 2020. Trump has called him a "legend." This week the praise came with policy attached.

The first order directs the federal government to stand up a research-grade quantum computer by 2028, with the Department of Energy defining the technical requirements and a national laboratory likely to host the machine. The second accelerates Washington's shift to post-quantum cryptography, pulling key deadlines forward to 2031 to guard financial systems and government networks against the day quantum machines can crack today's encryption. Together they amount to the most aggressive federal push the sector has seen.

## Why IBM, and why now

IBM is not the only company in the quantum race, but it is the one with the most credibility on Capitol Hill. In May, the Commerce Department and IBM each pledged $1 billion to build Anderon, a standalone quantum foundry. Days later the company committed $10 billion to quantum research and manufacturing over five years, on top of a $5 billion cybersecurity initiative through Red Hat. Krishna's pitch in the Oval Office was characteristically understated: government backing, he said, "is what both of these will achieve" in pulling private capital off the sidelines.

Wall Street has noticed. JPMorgan upgraded IBM to Overweight this week and lifted its price target to $291 from $270, citing an acceleration in the company's software business — now roughly 45% of revenue but nearly two-thirds of profit — and optionality on quantum. The stock rose more than 4% to around $263 even as the broader Nasdaq fell, and it has logged some of its best weeks in decades on quantum enthusiasm. IBM reports second-quarter earnings on July 22.

There is a caveat worth keeping in view. IBM does not expect a fault-tolerant quantum supercomputer until 2029 — a year after the government's new 2028 target for a research-grade machine. Google, whose president Ruth Porat also attended the signing, has warned that "Q-Day," when quantum systems can break global encryption, may arrive faster than the 2030s consensus assumes. The timelines are ambitious, and missing them is the obvious risk in the bull case.

## The diaspora angle

For Indian Americans, the symbolism is hard to miss. The company Washington is betting on to keep the United States ahead in the defining computing race of the next decade is led by an IIT Kanpur graduate who arrived as a student and rose through the engineering ranks. Krishna sits alongside Sundar Pichai, Satya Nadella and Shantanu Narayen in a generation of Indian-origin chief executives now steering the strategic priorities of American technology — and, increasingly, of American industrial policy.

The practical stakes are closer to home than the geopolitics suggest. Tens of thousands of Indian engineers work across IBM's research and software divisions in the US and at its large operations in Bengaluru and Pune, and a federally funded quantum build-out means hiring in exactly the areas — error correction, cryptography, materials science — where Indian and Indian-American researchers are heavily represented. The post-quantum cryptography mandate, meanwhile, will ripple into every bank, cloud provider and security firm that employs diaspora talent, forcing a multi-year migration of the encryption that underpins online life.

For NRI investors, IBM has quietly become one of the steadier ways to hold the AI-and-quantum theme without paying the nosebleed multiples attached to chipmakers. The shares trade on the strength of recurring software revenue, with quantum as the call option. Whether that option pays off depends on physics and on deadlines that even IBM admits are tight.

## What's next

Watch the July 22 earnings call for any revision to IBM's 2029 fault-tolerance timeline — a pull-forward would be the single biggest catalyst, and JPMorgan flagged exactly that. Watch, too, for how quickly the Department of Energy translates the executive order into procurement, and whether the Anderon foundry breaks ground on schedule. For a community well represented in both the labs building these machines and the enterprises that will have to defend against them, the quantum race has stopped being abstract."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron Just Told Wall Street the Memory Shortage Runs Past 2027. For the Diaspora, That's a Bill Coming Due.",
        "subheadline": "Sanjay Mehrotra's company posted a blowout quarter and locked in $22 billion of advance customer commitments — but the same AI hunger that minted the gains is about to make laptops and phones pricier.",
        "slug": make_slug("micron-earnings-memory-shortage-2027-mehrotra-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "An Indian-born CEO is riding the AI memory boom to record results, but the resulting chip shortage will quietly raise the cost of the laptops, phones and PC upgrades NRI families buy on both sides of the world.",
        "tags": ["micron", "semiconductors", "sanjay-mehrotra", "ai", "memory-chips"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-forecasts-strong-quarterly-results"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/micron-shares-jump-chip-shortage"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/micron-stock-soars-results-blow-past-expectations"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron Technology chief executive Sanjay Mehrotra",
        "image_attribution": "Wikimedia Commons",
        "body": """Micron Technology, the only American maker of the high-bandwidth memory that every AI accelerator depends on, delivered a quarter this week that even by 2026 standards looked unreal. Revenue more than quadrupled year-over-year to $41.46 billion, gross margins jumped to nearly 85%, and the company guided to as much as $51 billion in revenue for the current quarter — well above the $43 billion Wall Street had penciled in. The stock surged more than 12% after hours. Run by Sanjay Mehrotra, the Indian-born engineer who co-founded SanDisk before taking the helm at Micron, the company crossed a $1 trillion market value in late May and is among the best performers in the S&P 500 this year.

## The number that matters more than the beat

Behind the headline was a structural shift. Micron disclosed $22 billion in advance commitments from 16 "strategic customer agreements" — multi-year deals in which data-center, automotive and consumer buyers effectively pre-fund future supply to lock in volume and pricing. Remaining performance obligations across those deals run to roughly $100 billion. Earlier in the week the company signed a long-term supply agreement with Anthropic and took an equity stake in the AI lab.

The blunt message from Mehrotra: the shortage is not a passing cyclical spike. He told analysts the company has "no line of sight" to when supply will catch up with demand, and that tight conditions will persist beyond 2027. Memory makers are pouring capacity into high-bandwidth memory for AI, which leaves conventional DRAM and NAND — the chips inside ordinary laptops, phones and SSDs — increasingly scarce.

## Why an NRI should read past the stock price

That last point is where this stops being an earnings story and becomes a household one. When the world's memory makers prioritize HBM for AI data centers, the everyday memory that goes into consumer electronics gets squeezed, and prices drift up. Anyone planning to buy a laptop for a college-bound kid, upgrade a gaming PC, or replace a phone over the next two years is looking at a market where one of the cheapest, most commoditized components has turned into a bottleneck. The effect is global: it hits a family in Edison shopping at Best Buy and a cousin in Pune shopping on Flipkart alike.

There is a sharper edge for India specifically. The country's semiconductor ambitions lean heavily on assembly, packaging and — eventually — memory, and a structural memory shortage strengthens the case for the fabs and packaging plants now rising in Gujarat and Assam. Micron's own assembly-and-test facility in Sanand, Gujarat, the first major chip plant of India's semiconductor mission, suddenly looks well-timed against a market where memory is the scarce resource rather than the throwaway one.

## The investor's dilemma

For the NRI investor, Micron presents the classic late-cycle puzzle. The fundamentals are extraordinary and the stock still trades at a single-digit-to-low-teens forward multiple — cheap on paper for a company growing this fast. But that very multiple is the market's way of saying it does not believe these earnings are durable; it is pricing in a peak. Memory has always been a brutally cyclical business, and the advance customer commitments are partly an attempt to break that cycle by guaranteeing demand. Whether they succeed is the whole debate.

What is not in doubt is the immediate read-through. The AI build-out that has enriched Micron's shareholders is the same force that will quietly raise the cost of the devices the diaspora buys. The boom and the bill are two sides of the same chip.

## What's next

Watch Micron's Sanand output ramp and any signal on whether the company brings memory packaging — not just assembly — to India. Watch consumer DRAM and SSD pricing through the back half of 2026 for the first clear pass-through to retail. And watch whether rivals Samsung and SK Hynix follow Micron into multi-year pre-funded supply deals, which would confirm that the memory market has genuinely been reordered rather than merely overheated."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A $7 Billion Chip Deal Just Bet That AI's Next Battleground Isn't the Data Center. It's the Light Switch.",
        "subheadline": "Onsemi's all-stock takeover of Synaptics pushes the chip industry toward 'physical AI' — and lands squarely on the edge-computing skills a generation of Indian engineers has been building.",
        "slug": make_slug("onsemi-synaptics-7-billion-edge-physical-ai-chip-deal-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The pivot from cloud AI to 'edge' AI in everyday devices reshapes where chip jobs and skills will be valuable — a direct read for Indian engineers and NRI investors tracking the semiconductor sector beyond Nvidia.",
        "tags": ["semiconductors", "edge-ai", "onsemi", "synaptics", "physical-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/onsemi-buy-synaptics-7-billion-all-stock-deal"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/onsemi-synaptics-edge-ai-acquisition"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/on-semiconductor-synaptics-all-stock-deal"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6636497/pexels-photo-6636497.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a semiconductor chip on a circuit board",
        "image_attribution": "Pexels",
        "body": """The biggest names in the AI chip boom — Nvidia, Micron, Broadcom — have built their fortunes inside the data center. On Thursday, ON Semiconductor placed a different bet. The Arizona-based analog chipmaker agreed to buy Synaptics in an all-stock deal worth about $7 billion, a wager that the next phase of AI happens not in the cloud but in the physical world: the car, the factory floor, the doorbell, the light switch.

The market's first reaction was skeptical. Onsemi shares fell more than 7% after hours, even though the stock has surged 119% this year. Synaptics holders, getting 1.35 Onsemi shares apiece — a 19% premium — saw their stock jump 11%. The deal is expected to close in mid-2027 and to add to earnings within 18 months, with around $200 million in annual synergies.

## What 'physical AI' actually means

Onsemi is known for the unglamorous analog chips that manage power and signals in cars and industrial equipment. Synaptics brings the other half of the puzzle: edge-AI processors, human-machine interface technology, wireless connectivity and the Astra embedded-compute platform that lets devices run AI locally rather than phoning a data center for every decision.

"As artificial intelligence moves beyond the cloud and into the physical world," chief executive Hassane El-Khoury said, "the next phase of innovation will depend on systems that can sense, decide, act and adapt in real time." Onsemi frames it as four pillars working together — power, sense, connected compute, and control — and estimates the shift could expand its addressable market by anywhere from $30 billion to $243 billion by 2030. That enormous range is itself a tell: nobody knows how big edge AI gets, only that it is coming.

## Why the diaspora should track the edge, not just the cloud

For Indian and Indian-American engineers, the strategic read matters more than the deal terms. The AI job market has fixated on a narrow band of cloud and large-model work concentrated at a handful of hyperscalers. Edge AI widens the field. It rewards exactly the skills that have long been strengths in India's engineering base and its diaspora: embedded systems, low-power chip design, firmware, sensor fusion and the hard discipline of making intelligence run on a budget of milliwatts rather than megawatts.

That is also where India's own semiconductor strategy is quietly placing its chips. Rather than trying to out-build Taiwan's leading-edge fabs, New Delhi has bet on chip design and on the mature-node, power-and-sensing silicon that goes into cars, appliances and industrial gear — precisely the Onsemi-Synaptics sweet spot. Both companies run engineering and design operations in India, and a combined entity chasing physical AI is likely to lean harder on that talent, not less.

For the NRI investor, the deal is a reminder that the semiconductor trade is broader than the megacap AI names. Edge AI, automotive silicon and industrial chips are a slower, less hype-driven corner of the market — but one with a longer runway and less exposure to a single data-center spending cycle. The after-hours sell-off in Onsemi reflects worry about paying up at the top of a chip-valuation surge; the bet underneath it is that intelligence in everyday objects is a decade-long shift, not a quarter's story.

## What's next

Watch for regulatory review and any rival bid before the mid-2027 close — Synaptics had already been deepening its edge-AI roadmap through a licensing deal with Broadcom, which makes it a strategically contested asset. Watch whether other analog and IoT chipmakers respond with their own "physical AI" acquisitions, the way Texas Instruments moved on Silicon Labs earlier this year. And for anyone building a career or a portfolio around chips, watch the quiet migration of AI value from the data center to the edge — where a great deal of Indian engineering talent already lives."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")

print(f"\nInserted {len(inserted)}/{len(articles)} articles.")
for h in inserted:
    print(" -", h)
