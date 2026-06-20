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
        "headline": "Micron Heads Into Earnings With a Memory Shortage So Tight Even Apple Is Flinching",
        "subheadline": "Sanjay Mehrotra's company has become the AI boom's quiet kingmaker. For NRIs, the story runs from a Gujarat fab to the price of the next iPhone.",
        "slug": make_slug("micron-earnings-sanjay-mehrotra-ai-memory-gujarat-hbm-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Micron's Indian-origin CEO is building a $2.75 billion assembly plant in Gujarat, and the same memory crunch lifting his stock is about to raise prices on every device Indian American families buy.",
        "tags": ["semiconductors", "micron", "ai", "indian-tech", "gujarat-fab", "hbm"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Wall St Week Ahead: Micron earnings", "url": "https://www.reuters.com/markets/us/wall-st-week-ahead-investors-see-micron-earnings-pulse-check-ai-rally-2026-06-19/"},
            {"name": "Stocktwits — MU hits record high", "url": "https://stocktwits.com/news-articles/markets/equity/mu-hits-record-high-sndk-jumps"},
            {"name": "TheStreet — Micron analyst target before earnings", "url": "https://www.thestreet.com/investing/micron-stock-gets-higher-analyst-target-before-earnings"},
            {"name": "Reuters — Apple to raise prices on memory crunch", "url": "https://www.reuters.com/technology/apple-raise-prices-due-memory-chip-shortage-ceo-tells-wsj-2026-06-18/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg/330px-Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron Technology chief executive Sanjay Mehrotra, photographed in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of its history, Micron Technology was the kind of company only chip nerds and commodity traders cared about. Memory was a brutal, cyclical business — make a wafer, sell it cheap, watch prices collapse when supply caught up. Then artificial intelligence rewrote the rules, and the company run by Hyderabad-born Sanjay Mehrotra became one of the most important names in the AI build-out. When Micron reports fiscal third-quarter earnings on June 24, Wall Street will treat it as a verdict on the entire AI trade.

The numbers explain the obsession. Micron stock closed at a record $1,133.99 on Thursday, up nearly 9% in a single session and roughly 305% for the year. Management has guided to about $33.5 billion in quarterly revenue — more than the company earned in any *full year* through fiscal 2024 — with gross margins near a startling 81%. A year ago the same quarter brought in $9.3 billion. Analysts at Wedbush now carry a $1,300 price target.

### Why memory suddenly matters

The thing AI factories are starving for is not just Nvidia's GPUs. It is the high-bandwidth memory, or HBM, that sits beside them and feeds them data fast enough to keep up. Micron makes both HBM and the DRAM and NAND that go into everything else. Its production capacity for the year is essentially sold out. As one strategist put it, the demand is "through the roof in relation to chip capacity."

That scarcity is now leaking into the checkout aisle. On Wednesday, Apple's outgoing CEO Tim Cook told the Wall Street Journal that price increases on Apple products were "unavoidable" because of the memory crunch, calling the market unlike anything he had seen "in over 40 years." TechInsights estimates the next iPhone Pro could cost $270 more. When the world's most powerful consumer-electronics buyer says it can no longer shield customers, the squeeze is real.

### The diaspora's stake runs both ways

For Indian Americans, Micron is a two-sided story, and both sides are personal.

On the consumer side, the memory shortage Mehrotra's company is profiting from is the same one that will make the laptops, phones and game consoles in Bay Area and New Jersey households more expensive this autumn. The iPhone 18 and any new Mac are now likely to carry a memory tax.

On the opportunity side, Micron is one of the most visible Indian-origin success stories in semiconductors — and it has planted a flag in India itself. The company is building a $2.75 billion assembly and test facility in Sanand, Gujarat, its first in the country, anchoring the India Semiconductor Mission's pitch that the subcontinent can move up the chip value chain. For the NRI engineer weighing a move home, or the investor tracking which fabs actually get built, Micron's India plant is the clearest test of whether "Make in India" semiconductors translate from press release to packaged chip.

### What to watch on June 24

The bar is high enough to be dangerous. Micron has already guided to roughly $19.15 in non-GAAP earnings per share, and some analysts model slightly above that. Beating won't be enough on its own; investors want to hear that HBM strength is tightening broader DRAM pricing and that margins can hold near record levels into 2027 and beyond. The bearish case — flagged by several analysts — is that the stock has run so far that merely meeting expectations could trigger a sharp pullback, especially with SK Hynix planning to expand supply over the next five years.

For NRI investors who have ridden the AI rally through Nvidia and the broader chip complex, Micron's report is the cleanest read yet on whether the memory supercycle has more room — or whether the smartest move is to brace for both a stock wobble and a pricier phone."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tim Cook Says Apple's Price Hikes Are 'Unavoidable.' His Successor Inherits the Bill.",
        "subheadline": "A memory-chip crunch is forcing Apple to raise prices just as John Ternus prepares to take over in September — and Indian American buyers will feel it first.",
        "slug": make_slug("apple-tim-cook-price-hike-memory-john-ternus-iphone-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Apple devices are aspirational status objects in many Indian American homes, and a memory-driven price hike of up to $270 on the next iPhone lands just as a longtime hardware engineer takes the CEO seat.",
        "tags": ["apple", "tim-cook", "john-ternus", "iphone", "memory-chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Apple to raise prices due to memory chip shortage", "url": "https://www.reuters.com/technology/apple-raise-prices-due-memory-chip-shortage-ceo-tells-wsj-2026-06-18/"},
            {"name": "Engadget — Tim Cook says price increases unavoidable", "url": "https://www.engadget.com/mobile/tim-cook-says-apple-price-increases-are-unavoidable"},
            {"name": "Barron's — Under Tim Cook, Apple's stock soared", "url": "https://www.barrons.com/articles/apple-tim-cook-stock-ternus"},
            {"name": "TechCrunch — Tim Cook stepping down, John Ternus taking over", "url": "https://techcrunch.com/2026/04/20/tim-cook-stepping-down-as-apple-ceo/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg/330px-Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple chief executive Tim Cook, who steps down on September 1, 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """Tim Cook has spent fifteen years being diplomatic, so it was telling when Apple's outgoing chief executive used the word "unavoidable." In an interview with the Wall Street Journal published Wednesday, Cook confirmed what the industry had been dreading: Apple will raise prices to offset soaring memory and storage chip costs.

"We're doing our best to mitigate the huge increases that are being passed to us, and we've been trying to shield our customers from the increases, but the situation has become unsustainable," Cook said. He added, with the bluntness of a man who runs the most sophisticated supply chain on earth, "I've never seen anything like it in any area in over 40 years."

### The culprit is AI, again

The proximate cause is the same memory shortage driving Micron's stock to record highs. AI data centers are devouring the world's supply of DRAM and NAND, leaving consumer-electronics makers in a bidding war for what's left. "There's less supply at a time when consumers want devices and the memory guys are passing along huge price increases," Cook told the Journal.

Apple did not say how much or when, but the research firm TechInsights estimated the next iPhone Pro could cost $270 more than its predecessor. Price hikes on Macs and iPads could arrive even before the iPhone 18 launches in September. Apple, notably, has no intention of making its own memory: "We can't do everything," Cook said. "We know what we're good at."

### A handover with a sting

The timing is conspicuous. Cook steps down as CEO on September 1, becoming executive chairman, with hardware-engineering chief John Ternus taking the top job. By delivering the bad news himself, Cook spares his successor the optics of opening with a price increase. It is a characteristically orderly Cook exit — he leaves behind a company worth roughly $4.35 trillion, whose stock rose more than 1,200% on his watch — but the memory crunch is one problem he is handing over unsolved.

### Why this lands hard in Indian American homes

In much of the Indian diaspora, an Apple device is not just a gadget; it is a marker of arrival. The first-generation engineer who buys an iPhone Pro for a parent visiting from Pune, the student gifting AirPods after a first internship paycheck, the family that standardizes on Macs because the kids' school does — these are not edge cases. They are the core of Apple's most loyal, aspirational customer base.

A $270 jump on the flagship phone changes the math on those purchases, especially for families already absorbing higher costs everywhere else. It also reframes a quieter diaspora calculation: many NRIs buy Apple hardware on US trips to carry back to relatives in India, where Apple pricing already runs steep. If American prices climb too, that arbitrage shrinks.

There is a strategic footnote for the diaspora as well. Apple now assembles a growing share of its iPhones in India through Tata and Foxconn — a supply-chain shift Cook championed. The memory squeeze is a reminder that moving final assembly to India does not insulate Apple from the components, mostly made in Korea, Taiwan and the US, that actually set the price.

For Ternus, the message is clear before he has even started: the easy era of Apple quietly absorbing cost pressure is over. For the diaspora households that have made Apple a fixture of daily life, the next upgrade is going to sting — and the AI boom they read about in the headlines is the reason why."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Court Backs the Telegram Ban. For 150 Million Users, the Precedent Is the Real Story.",
        "subheadline": "A Delhi court upheld a temporary block of Telegram over a medical-exam leak — handing Modi's government a powerful new tool and unsettling a diaspora that lives on the app.",
        "slug": make_slug("telegram-india-ban-upheld-delhi-court-free-speech-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Telegram is a lifeline for NRIs coordinating family groups, community networks and business across borders; a court endorsing a government shutdown of an entire platform raises the stakes for everyone who relies on Indian internet access.",
        "tags": ["telegram", "india", "internet-freedom", "platform-regulation", "free-speech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Telegram loses bid to overturn India's blocking", "url": "https://www.reuters.com/technology/telegram-loses-bid-overturn-indias-temporary-blocking-app-2026-06-19/"},
            {"name": "Internet Freedom Foundation statement (via Reuters)", "url": "https://www.reuters.com/technology/telegram-loses-bid-overturn-indias-temporary-blocking-app-2026-06-19/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Telegram_app_icon_on_smartphone_screen_%28perspective_render%29_%2849896396508%29.jpg/1280px-Telegram_app_icon_on_smartphone_screen_%28perspective_render%29_%2849896396508%29.jpg",
        "image_caption": "The Telegram app icon displayed on a smartphone screen",
        "image_attribution": "Wikimedia Commons",
        "body": """A New Delhi court on Friday refused to overturn the Indian government's temporary block of Telegram, ruling that the shutdown — aimed at containing a leaked medical-school entrance exam — was "legal and reasonable." For a messaging app that counts India as its single biggest market, with more than 150 million users there, it was a sharp defeat. For the broader question of who controls India's internet, it may prove far more consequential.

### What happened

The government ordered Telegram blocked from June 16 to June 22 after the results of the country's medical-school admissions exam were scrapped amid allegations that the question paper had leaked. Indian telecom companies implemented the block within hours, and Google and Apple pulled the app from their stores. The state argued Telegram was a uniquely difficult case: blocked channels are easily recreated, and phone numbers and usernames can be concealed, creating what it called "a persistent enforcement challenge."

Delhi High Court Justice Tejas Karia agreed the government was "empowered ... to issue directions for blocking the public access to Telegram." Telegram, which says it removed more than 900 links tied to the leaked exam material, accused the government of omitting details of its proactive cooperation. Founder Pavel Durov has publicly argued the ban punishes ordinary users while the leaks simply migrate elsewhere.

### The precedent that worries activists

The Internet Freedom Foundation warned that the ruling "sets a concerning precedent with consequences for the open internet that extend well beyond this case." It is the most high-profile court clash between a global tech platform and Narendra Modi's government this year — and it follows last year's bitter fight with Elon Musk's X, after which the government trimmed the roster of officials who could order content takedowns.

The pattern is what unsettles civil-liberties groups: a specific, defensible grievance (an exam leak that upended the futures of lakhs of students) used to justify a tool — switching off an entire platform for a whole country — that can be reached for again under far broader circumstances.

### Why the diaspora should pay attention

For Indian Americans, Telegram is not abstract. It is where extended-family groups trade photos across time zones, where regional and alumni communities organize, where small cross-border businesses coordinate with suppliers and clients back home. A diaspora entrepreneur running a Bengaluru dev team or a Surat trading desk depends on uninterrupted access to the same Indian internet a court has now affirmed the government can selectively switch off.

There is also a values dimension that resonates in immigrant communities built partly on the promise of open expression. Many NRIs hold a complicated dual loyalty — pride in India's digital-public-infrastructure achievements, from UPI to Aadhaar, alongside unease at how the same state capacity can be turned toward control. Friday's ruling sharpens that tension. India's government can now point to judicial backing for shutting down a major app, and the next target may not come with as sympathetic a justification as a leaked exam.

The block is set to lift on June 22. The legal logic that enabled it is not going anywhere. For a diaspora that treats reliable connection to India as a given, that is the development worth watching — not the week Telegram went dark, but the precedent that made it lawful."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
