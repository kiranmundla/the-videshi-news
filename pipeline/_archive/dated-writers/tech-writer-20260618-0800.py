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

article1_body = """Qualcomm spent two decades as the company inside your phone. This week it made its clearest statement yet that the phone is no longer where the money will be — and it is willing to spend up to $10 billion to prove it.

The chipmaker is in talks to buy Tenstorrent, a private AI-chip startup, for between $8 billion and $10 billion, according to a report from The Information. The deal would be Qualcomm's largest ever, and it is timed to land just before the company's June 24 investor day, where it is expected to lay out an aggressive new data-center strategy. Wall Street has already voted: the stock is up roughly 68% over three months, and rose more than 3% in premarket trading on the news.

## Why the phone company wants a data-center business

The logic is not subtle. Qualcomm's smartphone revenue is under pressure — squeezed by memory-supply constraints, inventory adjustments, and the slow grind of a mature market. Year-over-year revenue growth has slipped to about 5%, with a sequential decline in the most recent quarter. The forward price-to-earnings ratio sits around 20, cheap next to Nvidia's 32 or Broadcom's 64. Investors are discounting the old Qualcomm even as they bid up the possibility of a new one.

That new one is built on inference — the cheaper, higher-volume cousin of AI training. Qualcomm's pitch is that running AI models is a power-efficiency problem, not a raw-horsepower problem, and that its mobile heritage of squeezing performance out of every watt is exactly the skill the data center now needs. J.P. Morgan analyst Samik Chatterjee estimates Qualcomm could target more than $3 billion in data-center revenue for fiscal 2027, scaling toward $35 billion by 2031.

The Tenstorrent deal would buy more than chips. It would bring in Jim Keller, the legendary engineer behind silicon at AMD, Apple, and Tesla, who now runs the startup. In the AI-chip arms race, a single architect of Keller's reputation can move a company's credibility overnight.

## The diaspora angle: a new column on the spreadsheet

For the Indian engineer in the Bay Area or Austin, Qualcomm has always been a recognizable name — a frequent H-1B sponsor and a place where a large share of the chip-design and modem-software workforce is of Indian origin. A serious data-center business changes the internal map. It means new teams in server silicon, AI compilers, and systems software, and it means those jobs grow inside a company that is suddenly competing with Nvidia and Broadcom for the same scarce talent.

It also matters for the India story. Qualcomm runs some of its largest engineering centers outside the United States in Bengaluru and Hyderabad, and a pivot to data-center and edge-AI silicon tends to deepen that footprint rather than shrink it. The chip-design work that India has quietly specialized in for twenty years — the unglamorous verification, the physical design, the modem firmware — is precisely the kind of work that scales when a company opens a new product line.

There is a hardware-and-glasses subplot too. Alongside the data-center push, Qualcomm used Augmented World Expo to launch Snapdragon Reality Elite, a platform for mixed-reality glasses that runs a three-billion-parameter language model on-device at 45 tokens per second. CEO Cristiano Amon says the company is working on more than 40 AI wearable devices. The bet is that whatever replaces the smartphone — glasses, pins, earbuds with cameras — will still have a Qualcomm chip inside it.

## What to watch

The June 24 investor day is the real catalyst. Qualcomm is expected to name a marquee customer for a custom data-center chip, and to put hard numbers behind its AI-silicon roadmap. If the targets exceed expectations, the re-rating of the stock continues. If they read as pipeline rather than profit — devices described, not yet sold — the skepticism returns. J.P. Morgan, tellingly, has placed Qualcomm on "Positive Catalyst Watch" while keeping a Neutral rating, "awaiting evidence of execution."

For NRI investors who hold Qualcomm directly or through index funds, the question is whether this is a genuine second act or an expensive attempt to buy relevance in a market Nvidia already owns. The Tenstorrent talks suggest Qualcomm knows it cannot build that credibility fast enough on its own. Ten billion dollars is a lot to pay for a head start — but in the AI-chip race, falling a generation behind costs far more."""

article2_body = """Sriram Krishnan, the most senior Indian-American voice on artificial intelligence inside the Trump White House, is leaving at the end of June. His exit closes an unusually consequential 18-month run — and reopens a question the diaspora has been circling for a year: who speaks for technology, and for the immigrants who build it, in this administration?

Krishnan announced the departure on X, calling the job "the privilege of a lifetime." He will stay on as an outside adviser, according to White House AI and crypto point man David Sacks, but the day-to-day role of Senior White House Policy Advisor on Artificial Intelligence ends with the month. He is said to be leaving to launch a new technology initiative.

## A short tenure with a long shadow

Krishnan's resume reads like a tour of Silicon Valley's last two decades — product leadership at Microsoft, Twitter, Yahoo, Facebook, and Snap, then a partnership at Andreessen Horowitz. He started his career as a founding member of Windows Azure. Time named him a Person of the Year in 2025 as an "Architect of Artificial Intelligence."

Inside government, he was a principal author of the administration's "AI Action Plan," the July 2025 blueprint that prioritized data-center construction and federal AI adoption over heavy regulation. He worked closely with Sacks on a string of executive orders, including one challenging state-level AI laws and another, released just this week, that asks leading AI developers to voluntarily submit their most capable models for government cybersecurity testing before public release.

That last order is not academic. It landed in the same news cycle as the Anthropic affair — the administration's move to cut off access to Anthropic's most advanced models for foreign nationals and G7 governments after Amazon flagged a potential cybersecurity jailbreak. Anthropic, which employs many foreign-born researchers, said the restriction effectively barred its own staff from working on its latest systems. The episode crystallized exactly the tension Krishnan spent his tenure managing: how to chase "American AI dominance" without strangling the immigrant talent that powers American AI in the first place.

## The diaspora angle: representation, and its limits

For Indian Americans, Krishnan's appointment in late 2024 was a genuine milestone. Indiaspora and other community groups celebrated it as proof that the diaspora had reached the room where technology policy is actually written. Here was someone who understood both the visa system and the venture-capital system, sitting at the Office of Science and Technology Policy.

His exit is a more complicated signal. The policies he helped shape have been double-edged for Indian tech workers. The data-center buildout and the light-touch regulatory posture are good for the companies that employ the diaspora. But the same administration has pushed a proposed $100,000 H-1B fee — struck down by a federal judge this week, then immediately appealed — and overseen restrictions, like the Anthropic action, that fall hardest on foreign-born engineers. Having an Indian-American in the AI chair did not soften the immigration squeeze. It is a reminder that representation in a senior role and protection for the broader community are not the same thing.

The Anthropic episode also feeds a debate now running hot in India itself: if Washington can switch off access to frontier models for foreign nationals overnight, every government and enterprise outside the United States has a reason to want its own. That is part of why Bengaluru's Sarvam just became a unicorn on a sovereign-AI pitch, and why "who owns the AI we run on" has become a boardroom question from Mumbai to New Jersey.

## What comes next

The bigger near-term question is who fills the vacuum. Sacks remains influential as co-chair of the President's Council of Advisors on Science and Technology, but the policy-advisor seat carried specific weight — coordinating AI strategy across agencies, running "AI diplomacy" at forums like the Paris summit, and steering federal AI adoption. Whoever takes it will inherit an unfinished agenda: a bipartisan frontier-AI safety bill working through Congress, a patchwork of state laws the administration wants to override, and a foreign-policy tightrope on model access.

For the diaspora, the lesson of Krishnan's run is worth holding onto. A seat at the table matters. But the table is set by forces — immigration politics, great-power competition, the raw economics of compute — that no single adviser, however well-placed, can fully bend."""

article3_body = """A shopper at Galeries Lafayette in Nice can now pay with the same app a vegetable vendor uses in Pune. India's Unified Payments Interface went live this week at one of France's premier retail destinations — and a few weeks after launching in Cambodia, the quiet globalization of India's digital-payments rail is starting to look less like a series of pilots and more like a strategy.

Commerce Minister Piyush Goyal announced the France rollout on X, framing the launch at Galeries Lafayette Nice Massena as "another significant step in UPI's global expansion." It was built with Lyra Collect and NPCI International Payments Limited (NIPL), the overseas arm of the system's operator. UPI already works at the Eiffel Tower, and officials say it is coming to the airports in Nice and Paris, including Charles de Gaulle.

The France news followed UPI's debut in Cambodia in early June, where Indian travelers can now scan the country's national KHQR codes at more than 4.5 million merchant outlets. Cambodia became the eighth country to accept UPI for merchant payments, joining the UAE, Singapore, Bhutan, Sri Lanka, Mauritius, Nepal, and France.

## A rail built at home, exported abroad

UPI is the plumbing behind India's cashless boom — nearly 20 billion transactions a month at home, running over more than 700 million QR touchpoints. What NIPL is doing now is unbundling that success into two distinct exports.

The first is merchant acceptance for travelers: an Indian tourist in Nice or Phnom Penh pays from their home bank account, with the exchange rate shown at the moment of payment. The second, and more strategic, is the rail itself — NIPL increasingly sells UPI as a template that other countries can adopt to build their own instant-payment systems, with talks underway across Africa and South America. The Reserve Bank of India and NIPL have a stated goal of reaching 20 countries by fiscal 2029.

## The diaspora angle: remittances and a familiar wallet

For the Indian diaspora, this is more than travel convenience, though that part is real — anyone flying home through a UPI-enabled airport or shopping in a UPI-enabled European store gets to skip the foreign-card markup.

The deeper prize is remittances. The UPI-PayNow linkage with Singapore already lets people send money between the two countries in seconds, a direct benefit to the large Indian community there — students, migrant workers, professionals — who move small sums home often. India remains the world's largest recipient of remittances, pulling in well over $100 billion a year, and a meaningful slice of that flows back through expensive, slow legacy channels. Every new cross-border UPI corridor is a quiet threat to the fee structures of traditional money-transfer operators.

There is also a softer dividend the diaspora tends to feel viscerally: the wallet on your phone in Mumbai now works abroad. For NRIs who hold Indian bank accounts and bounce between countries, UPI's spread means one familiar payment method follows them — no fumbling for local cash, no per-swipe card fees, no currency confusion at the till.

## The geopolitics underneath the QR code

It is no accident that the France launch was announced by a commerce minister and tied directly to Prime Minister Modi's conversations with President Macron. UPI has become an instrument of soft power — a way for India to plant a piece of its own digital public infrastructure inside other economies, and to position itself as the developing world's preferred alternative to American card networks and Chinese payment giants.

For Indian software engineers abroad, that matters professionally. UPI, Aadhaar, and the broader "India Stack" have become a globally studied model of digital public infrastructure, and the people who understand how it was built are increasingly in demand at fintechs and central banks worldwide. The expertise that the diaspora carries — how a billion-person payment system actually works at scale — is becoming an exportable skill in its own right.

## What to watch

The hard part is the second phase. Most of these launches start one-directional — Indian travelers paying abroad — before the reverse corridor, letting foreign visitors pay in India, switches on. Cambodia's two-way link is still being built. The faster NIPL closes those loops, and the more remittance corridors like the Singapore one it can replicate, the more UPI shifts from a tourist convenience to genuine financial infrastructure for the 35-million-strong Indian diaspora. The QR code at Galeries Lafayette is a start, not a finish."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Is Betting $10 Billion That the Phone Era Is Over. The Data Center Is the New Battleground.",
        "subheadline": "The chipmaker is in talks to buy Tenstorrent and its star engineer Jim Keller, days before an investor day meant to convince Wall Street it can challenge Nvidia. For the Indian engineers who staff its chip-design ranks, it's a whole new product line.",
        "slug": make_slug("qualcomm-tenstorrent-data-center-pivot-jim-keller-indian-chip-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Qualcomm employs thousands of Indian-origin chip engineers in the US and runs huge design centers in Bengaluru and Hyderabad; a pivot into data-center AI silicon reshapes the careers and job map for that workforce.",
        "tags": ["qualcomm", "ai-chips", "data-center", "indian-tech", "semiconductors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-stock-ai-chip-data-center"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-talks-buy-tenstorrent-information-reports-2026-06-16/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/qualcomm-snapdragon-reality-elite-ai-wearables/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Cristiano_Amon_%28President_%26_CEOQualcomm%29_%2854916855494%29_%28cropped%29.jpg",
        "image_caption": "Qualcomm President and CEO Cristiano Amon, who is steering the company toward data-center and edge-AI silicon",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sriram Krishnan Is Leaving the White House AI Job. The Diaspora Got a Seat at the Table — and a Lesson in Its Limits.",
        "subheadline": "The most senior Indian-American voice on AI policy exits at the end of June, just as Washington restricts foreign access to frontier models and revives a $100,000 H-1B fee. Representation, it turns out, isn't the same as protection.",
        "slug": make_slug("sriram-krishnan-white-house-ai-advisor-exit-diaspora-h1b-anthropic"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "An Indian-American held the top AI policy seat in the White House, but the administration's H-1B fee and foreign-national model restrictions hit Indian tech workers hardest — a pointed lesson on the gap between having representation and having protection.",
        "tags": ["sriram-krishnan", "ai-policy", "white-house", "h1b", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/white-house-ai-policy-adviser-krishnan-leave-position-2026-06-07/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/08/sriram-krishnan-leaving-white-house-ai-advisor-role/"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/amazon-ceo-talks-us-officials-anthropic-crackdown"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
        "image_caption": "Sriram Krishnan, the outgoing Senior White House Policy Advisor on Artificial Intelligence",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "You Can Now Pay With UPI at a Department Store in Nice. India's Payment Rail Is Quietly Going Global.",
        "subheadline": "Within weeks, UPI has gone live in France and Cambodia, pushing past eight countries for merchant payments. For the diaspora, the real prize isn't tourist convenience — it's faster, cheaper remittances.",
        "slug": make_slug("upi-france-nice-cambodia-global-expansion-npci-diaspora-remittances"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "UPI's overseas rollout means NRIs get a familiar payment app abroad and, more importantly, cheaper instant cross-border remittances that threaten the fees of legacy money-transfer operators.",
        "tags": ["upi", "npci", "digital-payments", "remittances", "india-stack"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Madhyamam", "url": "https://www.madhyamam.com/world/upi-launched-nice-massena-france-global-expansion"},
            {"name": "ANI / Industries News", "url": "https://computer-services.industriesnews.net/upi-cambodia-npci-4-5-million-merchants"},
            {"name": "Mint", "url": "https://www.livemint.com/news/rbi-npci-upi-20-countries-2029"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/278430/pexels-photo-278430.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smartphone displaying a QR code for a contactless digital payment",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️  {art['slug']}: only {wc} words — SKIPPING")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
