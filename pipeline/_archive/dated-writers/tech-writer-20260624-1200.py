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
        "headline": "Qualcomm Spent Two Decades Selling Phone Chips. In a Single Month It Has Bid Up to $14 Billion to Escape Them.",
        "subheadline": "Back-to-back talks to buy Modular and Tenstorrent are Qualcomm's bid to crash Nvidia's data-center party — and a fresh battleground for the Indian engineers who design these chips.",
        "slug": make_slug("qualcomm-modular-tenstorrent-data-center-ai-chip-acquisitions-nvidia-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Qualcomm's pivot from handsets to AI data centers is creating a new tier of high-value silicon and software jobs in San Diego and the Bay Area — the kind of roles Indian-American chip designers and ML-infrastructure engineers are positioned to fill.",
        "tags": ["qualcomm", "ai-chips", "semiconductors", "data-center", "silicon-valley", "nvidia"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Qualcomm nearing deal for AI chip startup Modular", "url": "https://www.reuters.com/technology/qualcomm-nearing-deal-ai-chip-startup-modular-bloomberg-news-reports-2026-06-22/"},
            {"name": "Barron's — Qualcomm Stock Falls but Has a Plan to Save AI Rally", "url": "https://www.barrons.com/articles/qualcomm-stock-price-ai-modular"},
            {"name": "Reuters — Qualcomm in talks to provide custom chip-design services to ByteDance", "url": "https://www.reuters.com/technology/qualcomm-talks-provide-custom-chip-design-services-bytedance-sources-say-2026-06-23/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg",
        "image_caption": "Tower servers in a data center, the market Qualcomm is racing to enter with a pair of AI acquisitions",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For most of the smartphone era, Qualcomm was the quiet toll collector of mobile computing: its modems and Snapdragon processors sat inside billions of handsets, and its patent licensing arm collected a cut of nearly every phone sold. That business is now shrinking. Global smartphone shipments are on course for their steepest annual contraction on record, and a surge in memory-chip prices has squeezed handset margins. So Qualcomm is doing something it has rarely done at this scale — buying its way out.

In the space of weeks, the company has lined up two of the largest acquisitions in its history, both aimed squarely at the artificial-intelligence data center. According to Bloomberg, Qualcomm is in advanced talks to buy Modular Inc., an AI infrastructure-software startup, for about $4 billion — more than double the $1.6 billion valuation Modular fetched in a funding round just nine months ago. Separately, The Information reports Qualcomm is negotiating to acquire chip designer Tenstorrent for $8 billion to $10 billion. Together, that is up to $14 billion to assemble, almost overnight, a credible challenge to Nvidia in the one market Qualcomm has never owned.

## Why the rush

Nvidia controls the AI training market so thoroughly that rivals have stopped trying to beat it head-on and instead are carving out adjacent ground: inference (running trained models cheaply), custom silicon for hyperscalers, and the software that ties chips together. Qualcomm's bets map onto exactly that. Modular, founded in 2022 by ex-Google engineers Chris Lattner and Tim Davis, builds software that lets AI models run efficiently across many kinds of hardware — a direct attack on the lock-in created by Nvidia's CUDA software. Tenstorrent, led by legendary chip architect Jim Keller, designs the processors themselves.

Qualcomm has already teased a major data-center customer on its earnings call and is expected to name it at an investor day this week. UBS analyst Timothy Arcuri estimates the data-center and "agentic" AI opportunity could ultimately add some $20 billion to Qualcomm's financial model. Markets are skittish about the price tag — the stock fell sharply this week amid a broad tech selloff — but the strategic logic is hard to argue with: diversify, or stay hostage to a phone market in decline.

## Why it matters to the diaspora

This is not abstract corporate maneuvering for Indian-American technologists; it is a job map being redrawn. The hardest, best-paid work in AI right now sits in exactly the two layers Qualcomm is buying into — low-level chip architecture and the systems software that makes accelerators usable. Those teams in San Diego, Santa Clara and Austin are disproportionately staffed by Indian-origin engineers, many of them IIT and US-graduate-school alumni who came up through the modem and GPU worlds. A Qualcomm that suddenly needs to build a data-center silicon-and-software stack from a standing start will be hiring aggressively for precisely those skills.

There is an India angle to the supply side, too. Qualcomm runs one of its largest engineering centers outside the United States in Hyderabad and Bengaluru, where thousands of designers already work on its chips. A data-center push typically flows work to those campuses — good news for engineers weighing whether to build a career at home or chase an H-1B to the Valley. And for NRI investors, Qualcomm is quietly becoming an AI-infrastructure story rather than a fading phone-chip play, a re-rating that has lifted the stock even as the handset business slips.

The cautionary note is valuation. Paying up to $14 billion for two pre-profit assets, in a week when a trillion dollars evaporated from the Nasdaq on AI-bubble fears, is the kind of bet that ages either very well or very badly. Qualcomm is also hedging in directions that complicate the picture: it is separately in talks to design custom chips for China's ByteDance, even as Washington tightens the screws on chip exports. For the engineers who will actually build all this, the lesson is the one the AI era keeps repeating — the leverage belongs to those who can design the hardware and the software that runs on it. Qualcomm just bid $14 billion to prove it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian IT Giant Just Won the Job of Running a US Chipmaker's Computers. The Twist Is What's Replacing the Humans.",
        "subheadline": "Infosys expanded its GlobalFoundries deal to run the chipmaker's entire enterprise IT on AI and automation — a glimpse of how India's outsourcing model is reinventing itself, and what it means for the engineers inside it.",
        "slug": make_slug("infosys-globalfoundries-ai-managed-services-it-deal-automation-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian IT services firms employ tens of thousands of NRIs in the US; the shift from people-heavy outsourcing to AI-run 'managed services' decides whose jobs survive and which skills now command a premium.",
        "tags": ["infosys", "indian-it", "ai", "globalfoundries", "outsourcing", "automation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CXOToday — Infosys and GlobalFoundries Expand Strategic Collaboration", "url": "https://cxotoday.com/press-release/infosys-and-globalfoundries-expand-strategic-collaboration-for-ai-powered-it-operations/"},
            {"name": "Seeking Alpha — GlobalFoundries selects Infosys for AI-managed services", "url": "https://seekingalpha.com/news/globalfoundries-selects-infosys-to-provide-ai-managed-services-across-it-operations"},
            {"name": "Outlook Business — AI will amplify IT firms, not replace them: Nilekani", "url": "https://www.outlookbusiness.com/corporate/ai-will-not-replace-it-firms-but-amplify-them-infosys-nilekani"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31665489/pexels-photo-31665489.jpeg",
        "image_caption": "Close-up of a computer processor; Infosys will run GlobalFoundries' enterprise IT under a new AI-led contract",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Infosys has won an expanded, multi-year contract to take over the day-to-day technology operations of GlobalFoundries, one of the world's largest contract chipmakers. On paper it reads like a routine outsourcing renewal. Read the fine print and it is something more interesting: a working model of how the business that built India's middle class is trying to survive the technology now eating it.

Under the deal, Infosys will run GlobalFoundries' end-to-end application, infrastructure, data and service-desk operations — essentially the entire internal IT estate of a global manufacturer that runs fabs across the US, Europe and Asia. Crucially, GlobalFoundries is not just renewing a labor contract. It is shifting to what the industry calls a "managed services" model, where the supplier is paid for outcomes — fewer outages, faster fixes, lower total cost — rather than for bodies on seats. The lever that makes those outcomes possible is AI and automation.

## From headcount to outcomes

For two decades, the Indian IT services pitch was simple arithmetic: smart engineers, English-speaking, at a fraction of US wages. That arithmetic is breaking. AI coding tools and automated operations are collapsing the number of people needed to keep an enterprise running, and clients know it. Accenture just had its worst week on record on exactly this fear, and the selloff has dragged down TCS, Infosys, Wipro and Cognizant alongside it.

Infosys's answer, on display in the GlobalFoundries deal, is to stop selling labor and start selling automation. Anand Swaminathan, the executive leading the engagement, framed it as moving the client "from reactive IT management to predictive and autonomous service delivery" — corporate-speak for: the AI catches the problem before a human would have. Chairman Nandan Nilekani made the strategy explicit at the company's annual meeting this month, arguing AI will "amplify" IT firms rather than replace them, and pointing to a $400 billion AI-first services opportunity by 2030. The bet is that someone still has to integrate, secure and govern all this AI inside large enterprises — and that someone can be Infosys.

## What it means for the diaspora

This is the story that should hold the attention of every Indian engineer working at a TCS, Infosys or Cognizant office in New Jersey, Texas or the Bay Area. The "managed services" transition is, bluntly, a decision about whose job survives. Routine application support and service-desk roles — long the entry rung for thousands of H-1B and L-1 workers — are exactly the work being automated away. The premium is shifting to people who can design the automation, wire AI agents into mission-critical systems, and own data governance and security. Infosys, TCS and Wipro have collectively pushed Microsoft Copilot to more than 300,000 employees in a frantic effort to move their own workforce up that ladder.

For NRIs whose visa status is tied to these employers, the stakes are concrete. A firm winning AI-led contracts is a firm with a future in the US market — and continued sponsorship. But the same shift that keeps Infosys relevant also means fewer of the commodity roles that historically anchored the H-1B pipeline. The engineers who reskill into AI operations, cloud and security keep their seat at the table; those who don't are increasingly exposed in a year that has already seen Oracle cut 21,000 jobs and the broader tech sector shed more than 110,000.

For investors in the diaspora who hold Infosys ADRs or track the Indian IT index, the GlobalFoundries win is a small but telling data point: the order book is still growing, and the highest-value deals now carry an "AI-led" label. Whether that is enough to offset the margin pressure from automation is the question that will define the sector's next two years. The contract to run a chipmaker's computers, it turns out, is really a referendum on the future of Indian IT itself."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian-Born CEO Out-Earned Tim Cook and Satya Nadella. His Own Shareholders Have Voted No Seven Times.",
        "subheadline": "Nikesh Arora's roughly $100 million package put him among the S&P 500's highest-paid bosses. The fight over whether he's worth it is a window into how the diaspora's corner-office generation is now judged.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-highest-paid-ceo-pay-say-on-pay-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin executives now run some of America's most valuable companies; how shareholders judge their pay versus their performance sets the template for the next generation of NRI leaders climbing the corporate ladder.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-ceo", "executive-pay", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DainikNews — Two Indians Among America's Highest-Paid S&P 500 CEOs", "url": "https://dainiknewslive.in/two-indians-among-americas-highest-paid-sp-500-ceos/"},
            {"name": "Inc. — A CEO's Stock Grew 800% but People Keep Voting No on His Pay", "url": "https://www.inc.com/sam-blum/nikesh-arora-palo-alto-networks-say-on-pay-vote.html"},
            {"name": "Barron's — Palo Alto Stock Rises. Its CEO Made a $10 Million Purchase.", "url": "https://www.barrons.com/articles/palo-alto-networks-stock-ceo-purchase"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Nikesh Arora, CEO of Palo Alto Networks, speaking at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Nikesh Arora belongs to a very small club. According to a Wall Street Journal tally of the S&P 500's highest-paid chief executives, Arora — who runs the cybersecurity firm Palo Alto Networks — landed in the top ten with a package worth roughly $100 million, more than Apple's Tim Cook or Microsoft's Satya Nadella took home. He was one of two Indian-origin names on the list; the other, Welltower's Shankh Mitra, ranked second overall with an extraordinary $821 million, trailing only Elon Musk.

That an executive born and schooled in India now sits among the best-paid corporate leaders in the United States is, in one sense, simply the latest milestone in a familiar arc. But Arora's case carries a complication the celebratory headlines tend to skip: his own shareholders keep voting against his pay.

## The "no" that doesn't count

Palo Alto Networks holds an unusual distinction — it has lost more shareholder "say-on-pay" votes than any other S&P 500 company since 2015, according to a Bloomberg analysis. Most investors rejected Arora's package again last December, the seventh such rebuke in just over a decade. Because these votes are nonbinding, Arora collects his money anyway.

His defense is performance, and the numbers are genuinely striking. Palo Alto's stock is up roughly 800% since he took over in 2018, adding something on the order of $100 billion to its market value. "You can correlate the amount I've gotten paid to the $100 billion," he has said. The board calls him "a world-class, exceptionally talented CEO." The skeptics counter that the structure — enormous stock grants that vest regardless of how the package polls — divorces pay from accountability, and that a 7% one-year return against the industry benchmark hardly justifies a nine-figure check.

## Why the diaspora should care

For Indian-Americans, this is more than gossip about a rich man's paycheck. The generation of NRIs who arrived as engineers in the 1990s and 2000s has now produced a critical mass of CEOs — Pichai, Nadella, Narayen, Krishna, Arora, Mehrotra, and a lengthening list below them. How those leaders are judged sets the template for everyone climbing behind them. The earlier wave was celebrated almost uncritically as proof of diaspora arrival. Arora's pay fight signals a more mature, more scrutinizing phase: the community's corner-office leaders are now held to the same governance debates, activist pressure and shareholder revolts as any other American executive. That is, arguably, the real marker of having arrived — to be argued about, not just admired.

There is a practical thread, too, for the many diaspora professionals who hold these companies in their portfolios and 401(k)s. Palo Alto is a core holding in countless tech and cybersecurity funds, and Arora's compensation is a live governance question that affects how investors should think about the stock. Cybersecurity itself has rarely been more central — the same week these pay rankings circulated, India's Tata Electronics disclosed a breach in which a ransomware group claimed to have stolen Apple and Tesla design files, a reminder of why firms like Palo Alto command the valuations that make their CEOs rich in the first place.

The deeper point is about how success is now measured. For the first generation of Indian-American executives, the achievement was simply reaching the top. For Arora's cohort, the harder test has arrived: justifying the rewards once they are there, to shareholders who are increasingly willing to say no — even when the company can't be forced to listen."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
