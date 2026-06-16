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
        "headline": "SpaceX Just Paid $60 Billion for Cursor. The Coding Tool Half of Bengaluru Already Lives In.",
        "subheadline": "Elon Musk's empire is buying the AI coding agent that automated the work of millions of engineers. For Indian developers who made Cursor a daily habit, the question is who owns their workflow now.",
        "slug": make_slug("spacex-anysphere-cursor-60-billion-ai-coding-indian-developers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cursor became the default coding tool inside Indian IT firms and Bay Area engineering teams stacked with Indian talent; an Elon Musk acquisition puts that daily workflow under new ownership just as AI is reshaping who gets hired.",
        "tags": ["ai", "indian-tech", "silicon-valley", "spacex", "coding"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — SpaceX locks in $60 billion Cursor deal", "url": "https://www.reuters.com/technology/"},
            {"name": "Reuters — SpaceX vaults past Amazon's market value", "url": "https://www.reuters.com/markets/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/89724/pexels-photo-89724.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A programmer writes code on a desktop computer, the kind of workflow AI coding agents like Cursor now automate",
        "image_attribution": "Pexels",
        "body": """Elon Musk's SpaceX has agreed to buy Anysphere, the startup behind the AI coding agent Cursor, for $60 billion in an all-stock deal — one of the largest acquisitions ever of a company that, four years ago, did not exist. For the millions of software engineers who now lean on Cursor to write, debug and ship code, the headline is not the price. It is the new landlord.

Cursor scaled faster than almost any developer tool in history. Founded in 2022, Anysphere built an editor that lets AI plan, write and test code alongside a human, and by this year it was generating roughly $2.6 billion in annualized business-to-business revenue. The acquisition, announced Monday, will fold that into SpaceX's growing enterprise-AI ambitions and is expected to close in the third quarter. Notably, SpaceX said it would not use proceeds from its record IPO last week to fund the deal.

### Why this lands hard in India and the diaspora

If you want to understand how deeply this matters, walk through an engineering floor in Bengaluru, Hyderabad or a Bay Area office where half the team grew up in India. Cursor is not a curiosity there — it is the default. India's IT services giants and the country's startup ecosystem adopted AI coding assistants aggressively, both because the tools genuinely speed up delivery and because clients began demanding "AI-native" development. Razorpay integrated its payment infrastructure with OpenAI's Codex; Indian IT firms have been racing to bake agentic coding into client work. Cursor sat at the center of that shift.

So the ownership question is not abstract. A tool that tens of thousands of Indian engineers open every morning now belongs to a company controlled by Musk, fused with his AI lab xAI. Pricing, data handling and India-specific availability all become decisions made inside that empire. For engineers on H-1B visas in the United States, watching their employers measure productivity in AI-assisted output, the consolidation is one more reminder that the tools defining their value are increasingly owned by a handful of American giants.

### The deflation problem underneath

The deal also crystallizes a fear that has been spreading through Indian tech: "AI deflation." As coding agents like Cursor make individual engineers dramatically more productive, the billable-hours model that built Tata Consultancy Services, Infosys, Wipro and HCLTech comes under pressure. Why pay for 50 engineers when 20 with Cursor can do the work? Indian IT employees, by many accounts, see this squeeze before management admits it. The companies are responding — HCLTech just took a $151 million stake in Sarvam AI, TCS partnered with Anthropic — but a $60 billion validation of AI coding's value only sharpens the point that the technology is moving from experiment to infrastructure.

There is opportunity in this too. Indian engineers are not merely consumers of these tools; they build them. The teams shipping AI coding products at OpenAI, Anthropic, Google and now SpaceX are thick with Indian-origin researchers and engineers. Aravind Srinivas, an IIT graduate, runs Perplexity at the center of the AI search race. The diaspora is on both sides of the deflation equation — at risk of displacement in commodity coding roles, and in command of the labs writing the replacements.

### What's next

Watch three things. First, whether SpaceX keeps Cursor available and affordably priced for the India market, or repositions it as a premium enterprise product. Second, whether the integration with xAI changes Cursor's underlying models — Indian developers have grown attached to its current behavior. Third, how India's IT majors respond: expect more equity stakes in domestic AI startups and louder "sovereign AI" messaging, as firms try to own intelligence rather than rent it from American buyers who keep getting bigger.

For now, the world's most-used AI coding tool has a new owner worth $2.7 trillion. The engineers who made it indispensable were not asked. They rarely are."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Razorpay Quietly Filed for a $600 Million IPO. India's Payments War Is Headed to the Stock Market.",
        "subheadline": "The Bengaluru fintech that processes payments for millions of Indian businesses wants to list by year-end — at half its 2021 peak valuation. For NRI investors, it is a direct bet on the rails the diaspora already uses to send money home.",
        "slug": make_slug("razorpay-600-million-confidential-ipo-india-payments-nri-investors"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "Razorpay runs the payment plumbing behind countless Indian merchants NRIs transact with daily; an IPO gives diaspora investors a rare pure-play stake in the UPI economy — but at a valuation that has been cut in half since 2021.",
        "tags": ["fintech", "indian-tech", "ipo", "razorpay", "upi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — India's Razorpay files IPO papers confidentially", "url": "https://www.reuters.com/business/finance/"},
            {"name": "PYMNTS — Razorpay Planning $600 Million IPO", "url": "https://www.pymnts.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A contactless payment made with a smartphone, the kind of digital transaction Razorpay processes for Indian merchants",
        "image_attribution": "Pexels",
        "body": """Razorpay, one of India's largest payment gateways, has confidentially filed draft papers for an initial public offering, taking the country's digital-payments war a decisive step toward the stock market. The Bengaluru company is targeting a raise of $600 million to $700 million and a debut by the end of the year, according to multiple reports following a newspaper advertisement on Monday.

The confidential route — increasingly favored by Indian startups including Swiggy and Meesho — lets Razorpay keep its financials private until just before launch. But the broad strokes are already public, and they tell a more sober story than the company's 2021 heyday. Razorpay is reportedly seeking a valuation of $5 billion to $6 billion, a sharp markdown from the $7.5 billion it commanded when it raised $375 million at the top of the funding cycle. For the financial year ending March 2025, it reported revenue of roughly $407 million and a net loss of $130 million.

### Why NRIs should pay attention

For the Indian diaspora, Razorpay is not an abstraction. It is the invisible layer behind a vast slice of online commerce in India — the checkout button on merchant sites, the UPI flow, the card processing, the business banking and payroll tools that small Indian companies run on. If you have paid an Indian merchant online, booked a service back home, or sent money into the Indian digital economy, there is a real chance Razorpay's rails carried it.

That makes the IPO one of the few opportunities for diaspora investors to take a direct, pure-play position in India's payments boom. PhonePe and Paytm are larger consumer brands, but Razorpay is the merchant-side infrastructure — closer to the plumbing than the faucet. As UPI expands internationally, recently reaching France and Qatar, the case for owning a piece of India's payment backbone grows more tangible for an NRI in New Jersey or London thinking about where the rupee economy is headed.

### The valuation reset is the real story

The halving of Razorpay's valuation since 2021 is not a Razorpay problem; it is a fintech-sector reckoning. Indian investors have repeatedly reset the prices of loss-making tech firms, and the public market remains cautious. PhonePe, which had filed to go public at a $9 billion to $10.5 billion valuation and received regulatory approval in January, halted its IPO this year, citing geopolitical conflict and market turmoil. Razorpay is moving ahead anyway — a signal of confidence, or of a window the company does not want to miss.

There are also the mechanics of becoming Indian again. Razorpay shifted its domicile back to India from the United States last year, reportedly at a cost of around $150 million in taxes — a price a generation of Indian startups is paying to list at home rather than abroad. It has also been busy on product: integrating its payment infrastructure with OpenAI's Codex platform and rolling out biometric authentication with Mastercard and Visa, as it tries to evolve from a payment gateway into a full-stack financial platform.

### What's next

The IPO will test investor appetite for Indian fintech at a moment of valuation discipline. Top banks — Kotak Mahindra Capital, Axis Capital, Citigroup, Goldman Sachs and JPMorgan — are reportedly working the deal, which suggests Razorpay intends to court global and institutional money, not just domestic retail. For diaspora investors, the watch items are clear: the final valuation when SEBI clears the filing, the path to profitability behind that $130 million loss, and whether Razorpay can convince a wary market that the payments war is one worth buying into. Backed by GIC, Y Combinator, Tiger Global, Peak XV and Lightspeed, it is one of India's most-watched fintech bets. Soon, anyone with a brokerage account may get to place their own."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tata's Bigbasket Just Hired an Amazon Veteran to Win the 10-Minute Grocery War",
        "subheadline": "Amit Nanda, who spent more than a decade building Amazon India, takes over a Tata-backed grocery giant fighting Blinkit, Zepto and Instamart for the right to deliver in minutes.",
        "slug": make_slug("bigbasket-amit-nanda-amazon-ceo-tata-quick-commerce-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Quick commerce reshaped how families in India shop — including the parents NRIs order groceries for from abroad; a Tata-backed leadership change signals how seriously India's biggest conglomerate is fighting for the 10-minute delivery market the diaspora increasingly relies on.",
        "tags": ["indian-tech", "quick-commerce", "tata", "ecommerce", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — India's Bigbasket names former Amazon veteran Amit Nanda as CEO", "url": "https://www.reuters.com/business/retail-consumer/"},
            {"name": "Reuters — India's quick commerce market", "url": "https://www.reuters.com/business/retail-consumer/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4254012/pexels-photo-4254012.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A worker packs groceries for delivery, the operational heart of India's fast-growing quick-commerce sector",
        "image_attribution": "Pexels",
        "body": """Bigbasket, the online grocery business backed by the Tata Group, has named Amit Nanda as its chief executive, handing the top job to a man who spent more than 11 years building Amazon's India operation. He replaces co-founder Hari Menon, who will stay on the board. The move, announced Tuesday, is a clear statement of intent: Tata wants to win India's brutal 10-minute grocery war, and it is recruiting from the company that taught India to shop online.

Nanda inherits a business in transition. Bigbasket built its name on scheduled, large-basket grocery delivery — the weekly shop, delivered to your door. But the Indian market moved underneath it. Quick commerce, the promise of groceries in ten minutes, has exploded into an $11.5 billion market in just five years, and it is now the battleground. The company said Nanda will lead its "next phase of growth," with particular emphasis on strengthening its position in quick commerce. Earlier this month, Bigbasket also appointed insider Seshu Kumar Tirumala as chief operating officer, rounding out a leadership reset.

### Why the diaspora should care

For NRIs, quick commerce is not just an India story — it is a family story. A large and growing number of diaspora users order groceries and essentials for parents and relatives back home from their phones abroad. The ten-minute delivery that feels like a novelty in some Western cities is now routine across urban India, and it has changed how an entire generation of families is provisioned. When an NRI in the Bay Area places an order for a parent in Bengaluru, the apps competing for that order — Bigbasket, Blinkit, Zepto, Instamart — are fighting a war whose outcome shapes daily life for people the diaspora cares about most.

The competitive field is crowded and well-funded. Bigbasket faces Swiggy's Instamart, Eternal's Blinkit, Amazon's Now, Walmart-backed Flipkart's Minutes, Reliance's JioMart and the aggressive upstart Zepto, which just filed an updated IPO prospectus seeking to raise thousands of crores. This is a capital-intensive, margin-thin business where speed and density of "dark stores" decide winners. Tata's deep pockets are an advantage; its track record in fast-moving consumer execution has been more mixed.

### The Amazon playbook meets the Tata balance sheet

Nanda's hire is the interesting part. Amazon India built the logistics muscle, customer obsession and operational discipline that defined Indian e-commerce for a decade. Bringing that DNA into a Tata-owned grocery platform is a bet that operational rigor — not just spending — wins quick commerce. Bigbasket has said it plans to roll out 10-minute food delivery nationwide, an ambitious expansion that will test exactly the kind of supply-chain orchestration Nanda spent his career building.

It also reflects a broader pattern worth noting for the diaspora: India's biggest conglomerates are increasingly run, at the operating level, by executives forged inside American tech giants. The talent that Amazon, Google and Microsoft trained — much of it Indian — is now flowing back into India's own champions. Nanda joining a Tata company from Amazon India is a small example of a large reversal, as homegrown firms recruit the very operators who built the foreign platforms they now compete against.

### What's next

Watch whether Bigbasket can close the speed gap with Blinkit and Zepto without torching its margins, and whether Tata is willing to fund a sustained price-and-delivery war. The 10-minute nationwide rollout is the signal to track — if it ships on schedule, Tata is serious. For the families on the receiving end of those deliveries, and the diaspora placing the orders, the competition is good news: faster service, lower prices, more choice. For the companies, it is a fight that will not have many survivors."""
    }
]

results = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        results.append((True, art['headline']))
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
        results.append((False, art['headline']))

print("\n=== SUMMARY ===")
for ok, h in results:
    print(("PUBLISHED" if ok else "FAILED") + ": " + h)
