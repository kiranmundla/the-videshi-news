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
        "headline": "A Chipmaker Micron Once Nearly Bought Just Became Korea's Most Valuable Company",
        "subheadline": "SK Hynix has overtaken Samsung on the back of the AI memory boom. The same supercycle is about to land on Micron's Gujarat plans — and on every NRI portfolio holding a chip name.",
        "slug": make_slug("sk-hynix-overtakes-samsung-memory-supercycle-micron-gujarat-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs holding Micron, Nvidia or chip ETFs are riding a memory supercycle whose pricing power runs straight through to Micron's Gujarat fab and India's semiconductor ambitions.",
        "tags": ["semiconductor", "memory", "micron", "sk-hynix", "ai", "indian-tech", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — SK Hynix dethrones Samsung", "url": "https://www.reuters.com/technology/sk-hynix-dethrones-samsung-electronics-south-koreas-most-valuable-company-2026-06-22/"},
            {"name": "MarketWatch — Micron earnings preview", "url": "https://www.marketwatch.com/story/microns-earnings-are-a-must-watch-market-event"},
            {"name": "AInvest — Micron supply story", "url": "https://www.ainvest.com/news/micron-memory-cycle-supply-story-demand-story/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/51165/cpu-processor-electronics-computer-51165.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A processor die under macro lens; memory chips have become the AI boom's scarcest component.",
        "image_attribution": "Pexels",
        "body": """South Korea woke up on Monday to a changing of the guard. SK Hynix, a memory maker that two decades ago was so buried in debt that Micron tried to buy it for scrap, briefly passed Samsung Electronics to become the most valuable company in the country. Its shares are up more than 340% this year. Samsung, which had held the top spot since 2000, was left a rounding error behind.

The headline is Korean. The story is not.

## What actually moved

SK Hynix is the dominant supplier of high-bandwidth memory — HBM — the specialised stacks of DRAM that sit next to every Nvidia GPU in every AI data centre. As Nvidia's chips have grown hungrier, HBM has gone from a commodity to the single scarcest, highest-margin component in the AI build-out. SK Hynix has ridden that to a $1.35 trillion market capitalisation. Samsung, which also makes phones, screens and logic chips, simply has more ballast.

The same current is about to surface on a Wednesday that matters far more to American investors: Micron reports fiscal third-quarter earnings on June 24. The Idaho company has guided to roughly $33.5 billion in revenue, a record gross margin near 81%, and earnings per share around $19.15 — up nearly 1,000% from a year ago. Micron has already locked in price and volume for its entire calendar-2026 HBM output. This is not a demand surprise. It is a supply squeeze: the three big memory makers are holding capacity below historical norms while shifting wafers toward HBM, and prices are doing the rest.

## Why an NRI should read past the ticker

For the large slice of the diaspora that holds Micron, Nvidia or a semiconductor ETF, this is the quarter that tells you whether the chip rally is a bubble or a regime. Micron now trades at a price-to-earnings ratio above 50 and is, by FactSet's reckoning, one of the top two contributors to S&P 500 earnings growth this period alongside Nvidia. Strip those two out and the index's earnings growth nearly halves. A lot of American retirement money is, knowingly or not, leveraged to whether Sanjay Mehrotra's commentary on Wednesday confirms that memory stays tight into 2027.

There is a second, quieter line that runs through Gujarat. Micron is building its first Indian facility — an assembly and test plant near Sanand — and the economics of this supercycle decide how fast that footprint grows and how many engineering and operations roles it anchors. The diaspora professional weighing a move back, or a cross-border posting, is watching the same margin line as the day trader, for very different reasons.

## The uncomfortable part

A memory boom is a tax on everything else. As Micron and its Korean rivals pour capacity into HBM for Nvidia's next-generation Vera Rubin platform, they pull it away from the ordinary DRAM and NAND that goes into laptops, phones and servers. That is why Tim Cook has already called Apple's coming price hikes "unavoidable," and why a memory shortage is rippling into consumer-device costs. The NRI buying an iPhone in New Jersey and the one trading Micron in a Fremont brokerage account are, this quarter, on opposite ends of the same supply curve.

## What to watch

The number on Wednesday is almost a formality — Micron's guidance all but guarantees a record. What matters is the language around pricing and supply for 2027, and any read on how the India fab fits the capacity map. If Mehrotra signals that tightness persists, the Korean rally and the American one are the same trade, and it has further to run. If he hedges, the most crowded corner of the market gets a cold shower.

Either way, the lesson of SK Hynix is worth keeping. A company the industry had written off in 2003 — penny stock, creditor control, nearly sold for parts — is now Korea's most valuable, because it owned the one thing AI could not get enough of. In a cycle this concentrated, the whole game is being on the right side of scarcity."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Mukesh Ambani Just Filed the Papers for India's Biggest-Ever IPO. The Next Generation Is Running It.",
        "subheadline": "Jio Platforms' draft prospectus is in with SEBI, valuing a company Google and Meta already own slices of at up to $180 billion. For NRIs, it is the rare chance to buy India's digital backbone directly.",
        "slug": make_slug("jio-platforms-ipo-drhp-filed-sebi-ambani-180-billion-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Jio's listing gives NRIs a direct way to own India's largest telecom and digital-services platform — but the fresh-issue-only structure and India's softening market change the calculus on whether to chase it.",
        "tags": ["jio", "reliance", "ipo", "ambani", "digital-india", "nri-investors", "telecom"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine — Jio board approves DRHP", "url": "https://www.thehindubusinessline.com/companies/reliance-jio-board-approves-drhp-for-ipo-before-sebi/"},
            {"name": "WSJ — Reliance's Jio Platforms to seek India listing", "url": "https://www.wsj.com/business/reliance-jio-platforms-india-listing"},
            {"name": "Inc42 — Jio files DRHP for fresh-issue-only IPO", "url": "https://inc42.com/buzz/jio-files-drhp-for-fresh-issue-only-ipo/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mukesh_Ambani.jpg",
        "image_caption": "Reliance Industries chairman Mukesh Ambani, who announced the Jio Platforms IPO filing at the company's 49th AGM.",
        "image_attribution": "Wikimedia Commons",
        "body": """At Reliance Industries' 49th annual general meeting on Friday, Mukesh Ambani let the moment breathe. "With great delight, let me tell you that the Board of Jio Platforms has approved the Draft Red Herring Prospectus earlier today, and it will be filed with SEBI today," he told shareholders, calling it "a deeply emotional moment." Then he named the people who would run it: Isha, Akash and Anant Ambani — the next generation, leading what is shaping up to be the largest IPO in Indian history.

The numbers are large enough to warrant the theatre. Brokerages peg Jio Platforms' value at around $180 billion, with estimates running from $130 billion up. The offering is a fresh issue of up to 270 million new shares; an offer-for-sale component was reportedly dropped in the final stretch over valuation disagreements. Financial Times reporting puts the target raise near $4 billion, which alone would top Hyundai Motor India's $3.3 billion listing as the biggest market debut the country has seen.

## Why this is a technology story, not just a telecom one

Jio is filed under "telecom" out of habit. It is, in practice, India's digital infrastructure. Since launching in 2016 it has become the country's largest mobile operator and pulled more than $20 billion from a who's who of global capital — Meta, Google, KKR, Silver Lake, General Atlantic, Saudi Arabia's Public Investment Fund. Reliance still owns about 66% of Jio Platforms; Meta holds nearly 10%, Google 7.7%. The capital from the IPO is earmarked for next-generation network rollout, AI and data-centre ventures, and enterprise digital services. Ambani noted that Jio leapt from rank 340 to 20 globally in patent-innovation velocity in a single year — the only Indian company in the top 20.

For an NRI, that distinction matters. Buying Jio is not buying a phone company. It is buying the rails — payments, cloud, connectivity, increasingly AI — that the rest of India's consumer internet runs on.

## The catch for diaspora investors

Here is where enthusiasm needs a cold towel. The fresh-issue-only structure means every rupee raised goes into the company, not into the pockets of existing holders — generally a healthier signal, but it also means no anchor of selling shareholders setting an early price floor. And the backdrop is not friendly: the benchmark Sensex is down nearly 10% this year, listing activity has been subdued, and the Middle East conflict has weighed on India as a major oil importer. The NSE itself just filed for its own IPO this week. A mega-listing into a soft tape is a real test of appetite.

There is also the perennial NRI friction. Direct participation in an Indian IPO requires the right account plumbing — typically an NRE/NRO setup and a demat account, with FEMA rules governing how much and through which route. Many in the diaspora will find it simpler to get Jio exposure through Reliance Industries shares or India-focused funds than to chase the primary allocation. None of that is a reason to skip it; it is a reason to set it up before the price band drops, not after.

## What to watch next

The DRHP is filed, not cleared. SEBI and the exchanges still have to sign off, and the price band — the figure that turns a $180 billion valuation from a brokerage guess into a number you can act on — comes later, through book-building. The next real signal is how institutional anchors price the book. Jio has spent a decade proving it can scale; the IPO is the moment the public market decides what that scale is worth.

For a diaspora that has watched India's digital economy from a distance — using the UPI rails on trips home, watching Reliance from afar — this is the rare moment the backbone itself goes on sale. Whether you buy or simply watch, it is worth understanding before the band is set."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Everyone Is Rushing to IPO Their AI Company. The Indian-Born CEO of Perplexity Says He'll Wait Until 2028.",
        "subheadline": "As Anthropic and OpenAI line up for the public markets, Aravind Srinivas is holding Perplexity back — even as a CNN copyright suit and a brutal cost war test the startup that picked a fight with Google.",
        "slug": make_slug("perplexity-aravind-srinivas-2028-ipo-anthropic-openai-cnn-suit-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Aravind Srinivas is the latest Indian-origin founder building a frontier AI company in the US; his measured IPO call and cost strategy are a tell for diaspora engineers and investors weighing where the AI money actually goes.",
        "tags": ["perplexity", "aravind-srinivas", "ai", "ipo", "indian-founders", "openai", "anthropic"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Marketing-Interactive — Perplexity eyes 2028 IPO", "url": "https://www.marketing-interactive.com/perplexity-eyes-2028-ipo"},
            {"name": "Outlook Business — Srinivas multi-model vision at COMPUTEX", "url": "https://www.outlookbusiness.com/perplexity-ceo-multi-model-ai-vision-taiwan"},
            {"name": "Storyboard18 — Perplexity launches Search as Code", "url": "https://www.storyboard18.com/perplexity-search-as-code-aravind-srinivas"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Aravind_Srinivas_2024.jpg",
        "image_caption": "Perplexity co-founder and CEO Aravind Srinivas, who says the company will not pursue a public listing before 2028.",
        "image_attribution": "Wikimedia Commons",
        "body": """The fashionable move in artificial intelligence this month is to file for an IPO. Anthropic has confidentially submitted a draft registration to the SEC. OpenAI is widely expected to follow. The wave is on. Aravind Srinivas, the Chennai-born, IIT Madras- and Berkeley-trained CEO of Perplexity, told CNBC he is not riding it: Perplexity plans to go public in 2028, "regardless of how investors respond" to the listings ahead of it.

In a market addicted to momentum, choosing to wait is itself a statement.

## A familiar arc, a contrarian call

Srinivas belongs to a now-recognisable cohort — Indian-origin founders and executives building the core of American AI. He started Perplexity as an answer engine that openly picked a fight with Google search, and pushed the incumbent into shipping AI answers of its own. The company has since moved well past a chat box: its "Perplexity Computer," launched this year, orchestrates as many as 20 different AI models as a "team of agents," and a new "Search as Code" architecture has the system generate Python to query its own search stack rather than making one tool call at a time.

His IPO restraint tracks a clear thesis. Srinivas told CNBC that the success or failure of the Anthropic and OpenAI debuts would have broad implications for the whole AI sector — a strong showing lifts everyone — but that Perplexity's own timeline does not bend to it. He defended the eye-watering valuations of frontier labs while warning that a sustained slowdown in model innovation could puncture them. That is a more honest framing than most: ride the wave, but know what would end it.

## The cost war is the real story

The line diaspora engineers should underline is about money, not models. Srinivas argues enterprises are becoming more selective about AI spending — prioritising performance and cost efficiency over raw usage — and that lower-cost open-source models will increasingly do the job where they can match results. Perplexity's strategy, he has said, is to "own the models you can" and keep costs down rather than depend entirely on the most expensive frontier systems.

For the thousands of Indian engineers inside OpenAI, Anthropic, Google and Meta — and the founders among the diaspora building on top of them — that is a forecast worth heeding. The first phase of the AI boom rewarded whoever had the biggest model. The phase Srinivas is describing rewards whoever can deliver a good-enough answer cheaply, at scale, with the right orchestration. The "harness," as he puts it, not the model, is the product. That shift changes which skills are scarce and which companies survive.

## The headwinds he's not advertising

Waiting until 2028 also buys time to clean up messes. Perplexity is being sued by CNN over alleged AI copyright infringement — part of a broader fight between AI firms and publishers that is far from settled and that hangs over any future valuation. Building an answer engine on the open web is cheap until the courts decide what that content costs. A 2028 listing gives the litigation, and the licensing market it will shape, room to resolve before public investors have to price it.

## Why it matters from Edison to Bengaluru

For the NRI tracking where AI value actually accrues, Perplexity is a useful instrument precisely because it is not a frontier lab. It is a bet that the winners of the next phase will be the orchestrators and cost-disciplined application builders, not only the model giants. Srinivas declining to rush — while OpenAI and Anthropic sprint for the exits — is either the discipline of a founder who knows his unit economics, or the caution of one who knows his legal exposure. Probably both.

The diaspora has plenty of CEOs already running the giants. Srinivas represents the next question: who builds the durable, profitable layer on top of them. His answer, for now, is to keep building and skip the party — and that restraint may be the most informative thing any AI founder has said this month."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
