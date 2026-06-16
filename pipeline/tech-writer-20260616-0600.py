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
        "headline": "Adobe Is Tearing Down Its Paywall. Shantanu Narayen's Last Big Bet Is Free.",
        "subheadline": "The Indian-origin CEO who built Adobe into a $200-billion subscription machine is now giving its AI tools away to widen the funnel — and a CFO just bolted to a chip company.",
        "slug": make_slug("adobe-freemium-pivot-narayen-firefly-cfo-exit"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Adobe is one of the largest employers of Indian engineers in the Bay Area and India, and its freemium gamble signals how the AI squeeze is reshaping careers and stock options for the diaspora that helped build it.",
        "tags": ["adobe", "shantanu-narayen", "firefly", "ai", "indian-tech", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks (ADBE Q2 Earnings Call)", "url": "https://www.zacks.com/stock/news/2026/06/12/adbe-q2-earnings-call-centers-on-freemium-ai-push-raised-outlook"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/adobe-raises-annual-forecasts-cfo-exit-2026-06-11/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/adobe-cfo-marvell-software-ai"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg/330px-Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Adobe Chairman and CEO Shantanu Narayen, who is steering the company toward a freemium AI model before he steps down.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For most of Shantanu Narayen's 18 years running Adobe, the strategy was elegantly simple: build software so good that professionals would pay a monthly fee forever. Photoshop, Illustrator, Premiere — all rolled into Creative Cloud, all metered, all recurring. It turned Adobe into one of the most reliable cash machines in software.

On its second-quarter earnings call this month, Narayen began dismantling that logic.

Adobe told investors it will lean far harder into a **freemium** model — letting new users in the door without an immediate paywall — because artificial intelligence is changing how people find and buy creative tools faster than the company expected. Narayen said the market is increasingly shaped by conversational interfaces and intent-based searches, and that Adobe now sees a chance to widen the top of its funnel the way the free Acrobat Reader once did decades ago.

The numbers underneath were not weak. Adobe beat on both earnings and revenue, posting $6.62 billion for the quarter, and raised its full-year forecast to as much as $26.6 billion. AI-first annual recurring revenue tripled to more than $500 million. President David Wadhwani said traffic to adobe.com rose over 40% year over year, with early Firefly, Express and Acrobat AI Assistant usage strong enough to justify the giveaway.

Wall Street hated it anyway. The stock fell roughly 5% after hours and is down more than 37% on the year. Analysts cut targets — Stifel pulled its rating to Hold, UBS trimmed to $225 — fretting that "stepping on the gas" of free user acquisition sacrifices near-term recurring-revenue visibility. The deeper fear is existential: that AI image and design tools from frontier labs and rivals like Figma and Canva will commoditize the very thing Adobe charges for.

## The CFO who left for a chipmaker

If the strategy shift unsettled investors, the executive exit alarmed them. Chief Financial Officer Dan Durn announced he is leaving — to take the same job at Marvell Technology, a custom AI-chip and networking firm.

The optics are brutal. Adobe is down 42% this year; Marvell is up well over 200%, riding the AI hardware boom that NVIDIA's Jensen Huang has suggested could make it a trillion-dollar company. A finance chief trading a marquee software brand for a chip supplier reads, to nervous shareholders, like a verdict on where the value is migrating: from the application layer to the silicon underneath it.

Durn's departure also lands just three months after Narayen himself said he would step down once a successor is named, leaving Adobe's leadership unusually thin at the top during its most consequential strategic turn in a decade. Steve Day, a senior corporate-finance executive, steps in as interim CFO.

## Why the diaspora is watching

This is not abstract corporate theater for Indian Americans. Adobe employs thousands of Indian-origin engineers across San Jose and its large Noida and Bengaluru centers, and Narayen — a Hyderabad-born, Osmania University graduate — has long been a fixture on every "Indians running global tech" list alongside Satya Nadella and Sundar Pichai.

For an Indian engineer holding Adobe RSUs, a stock down 42% is a tangible cut to net worth and, for visa holders, a complication in the green-card math that often hinges on stable employment and compensation. A freemium pivot that prioritizes user growth over margin can mean leaner teams and tighter headcount in exactly the product groups where many of those engineers sit.

There is a strategic read, too. Adobe's bet is that owning the workflow — letting an AI agent orchestrate Photoshop, Premiere and Illustrator from a single prompt, in native file formats — is more durable than charging per seat. Its Firefly AI Assistant, which can even route through Anthropic's Claude, is the wedge. If Narayen is right, the company's successor inherits a wider, freer top of funnel. If he is wrong, Adobe will have given away its pricing power in a market that no longer needs permission to make an image.

Either way, the next Adobe CEO may well be Indian-origin again — internal succession chatter has centered on Wadhwani among others. Whoever it is will inherit a company betting that the safest way to survive the AI era is to stop charging at the door."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "UPI Just Reached the Eiffel Tower. For NRIs, the Rupee Is Quietly Going Global.",
        "subheadline": "India's payment rail is now live in France, Qatar, Malaysia and a dozen other countries — turning a domestic utility into soft power, and a real convenience for the diaspora that sends money and travels home.",
        "slug": make_slug("upi-international-expansion-france-qatar-nri-dpi"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "UPI's cross-border push means NRIs can increasingly pay with an Indian app abroad and connect home remittances to a real-time rail — reshaping how the diaspora moves money between India and the West.",
        "tags": ["upi", "fintech", "npci", "digital-payments", "india-tech", "ondc"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/modi-and-macron-discuss-upi-expansion-in-france-during-bilateral-talks-says-mea/"},
            {"name": "PR Newswire (NPCI International / PayNet)", "url": "https://en.prnasia.com/releases/apac/npci-international-signs-agreement-with-payments-network-malaysia.shtml"},
            {"name": "Reuters", "url": "https://www.reuters.com/breakingviews/digital-payments-could-increase-central-bank-bloat-2026-06-14/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6205512/pexels-photo-6205512.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A shopper scans a QR code to pay by phone — the interface India's UPI is now exporting to merchants worldwide.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Stand at the base of the Eiffel Tower today and you can pay for your ticket by scanning a QR code with an Indian banking app. The same is true at the flagship Galeries Lafayette, several French airports, and — within weeks — at Charles de Gaulle in Paris and the airport in Nice.

That is not a tourist gimmick. It is the clearest sign yet that India's Unified Payments Interface, the free real-time rail that processes billions of domestic transactions a month, has become an instrument of statecraft and a genuine convenience for the diaspora.

During Prime Minister Narendra Modi's visit to Nice for the Bharat Innovates 2026 showcase, Foreign Secretary Vikram Misri confirmed that he and President Emmanuel Macron discussed expanding UPI across more French cities. UPI launched in Paris in July 2024; France saw a reported 40% jump in Indian tourist arrivals in the year after, and acceptance is now spreading to airports and retail. Separately, Commerce Minister Piyush Goyal switched on UPI at a Lulu Hypermarket in Qatar — and NPCI's international arm signed a deal with Malaysia's PayNet to let Indian travelers scan DuitNow QR codes there, with reciprocity to follow.

The live list is now long: the UAE, Singapore, Bhutan, Nepal, Sri Lanka, Mauritius, Qatar, France, with South Korea and Cambodia recently added. India is, in effect, exporting its plumbing.

## Why this is a diaspora story, not a tourism one

For Non-Resident Indians, the immediate hook is obvious. The "One World" wallet — a prepaid UPI instrument foreign visitors can load with an international card — means an NRI visiting Mumbai no longer needs an Indian bank account to tap and pay at a chaiwala or an Uber. Reverse the direction and the diaspora can increasingly use familiar Indian apps abroad rather than juggling cards and foreign-transaction fees.

The bigger prize is remittances. NRIs send tens of billions of dollars home every year, and that money has historically crawled through correspondent banks at painful spreads. As UPI links to other countries' instant rails — Singapore's PayNow link is already live, and Malaysia and the UAE are wiring up — the architecture for near-instant, low-cost cross-border transfers is quietly being assembled. A Reuters analysis this week placed UPI alongside Brazil's Pix as the systems dragging the rich world toward real-time retail payments; the EU's own instant-payments rules are essentially catching up to what India built in 2016.

## The strategic subtext

There is a geopolitical layer the diaspora should not miss. The same week UPI spread through France, the Financial Times reported China is launching a cross-border digital-payments network aimed at challenging dollar dominance. India is playing the same game with a friendlier face: rather than confronting Visa and Mastercard head-on, NPCI is stitching India's rail into partner countries' national QR standards, one bilateral deal at a time.

For an Indian engineer in New Jersey or London, this is also a career signal. The Digital Public Infrastructure stack — UPI, Aadhaar-based KYC, ONDC — is becoming an exportable product, and the firms building and securing it (from NPCI to fintechs like PhonePe, Razorpay and Paytm) are increasingly hiring for global, not just domestic, scale. The talent that returns to India, or builds cross-border fintech from abroad, is riding a rail that now runs from a Hyderabad kirana store to the foot of the Eiffel Tower.

The rupee is not yet a global currency. But the way Indians pay is fast becoming a global standard — and for the diaspora, that means the distance between "home" and "here" is shrinking one QR code at a time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jayshree Ullal's Arista Built the Plumbing for the AI Boom. Now It's Going 1.6 Terabit.",
        "subheadline": "The Indian-origin CEO of the most underrated company in AI just launched networking gear for racks packed with hundreds of thousands of chips — and the diaspora's quiet networking dynasty keeps compounding.",
        "slug": make_slug("arista-jayshree-ullal-1-6-terabit-ai-fabric-launch"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Jayshree Ullal is one of the wealthiest self-made women in tech and a rare Indian-origin woman running a major US chip-adjacent company; Arista's AI networking surge is a diaspora success story that rarely makes headlines next to NVIDIA.",
        "tags": ["arista-networks", "jayshree-ullal", "ai-infrastructure", "data-center", "indian-tech", "semiconductors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/arista-networks-anet-1-6t-launch-ai-fabrics-data-center"},
            {"name": "Business Wire (Arista Q1 2026 results)", "url": "https://www.businesswire.com/news/home/arista-networks-reports-first-quarter-2026-financial-results"},
            {"name": "The Motley Fool (ANET Q1 2026 transcript)", "url": "https://www.fool.com/earnings/call-transcripts/2026/05/05/arista-anet-q1-2026-earnings-call-transcript/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Jayshree_Ullal_Arista_CEO.jpg/330px-Jayshree_Ullal_Arista_CEO.jpg",
        "image_caption": "Jayshree Ullal, Chairperson and CEO of Arista Networks, which makes the high-speed networking that ties AI data centers together.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Everyone knows NVIDIA sells the chips that power the AI boom. Far fewer know who builds the high-speed plumbing that lets tens of thousands of those chips actually talk to each other. The answer, increasingly, is a Santa Clara company run by a London-born, Delhi-and-Bengaluru-raised engineer named Jayshree Ullal.

This month Arista Networks introduced its 7060XE7 Series — a family of **1.6 terabit** networking platforms built for rack-scale AI infrastructure. In plain terms: as AI clusters balloon from thousands of accelerators to hundreds of thousands, the bottleneck stops being the chips and becomes the network that connects them. Arista's new gear is designed precisely for that scale, and it is why the company keeps outgrowing its own forecasts.

The growth is staggering for a firm most consumers have never heard of. Arista reported first-quarter 2026 revenue of $2.71 billion, up 35% year over year, with operating margins near 48%. On the earnings call, the company raised its full-year outlook to roughly $11.5 billion in revenue and lifted its AI-fabrics target from $3.25 billion to $3.5 billion. It sits on more than $12 billion in cash and securities against modest liabilities — a rare combination of hypergrowth and a fortress balance sheet.

## The quietest power player in the diaspora

Ullal's story is one the Indian American community tells too rarely. She took Arista public in 2014, grew it from a scrappy challenger to Cisco into a networking giant now worth far more than many household-name software firms, and in the process became one of the wealthiest self-made women in technology. She remains both Chairperson and CEO — a level of durable control few founders or operators of either gender hold.

She is also a counterexample to the usual diaspora narrative. The Indian-origin leadership story is dominated by software and services CEOs — Nadella, Pichai, Narayen. Ullal runs a hardware-adjacent infrastructure company at the physical heart of the AI build-out, the layer where money is being spent fastest and where supply chains, not slideware, decide winners. On the Q1 call, the company flagged rising memory and silicon costs as the real challenge — the language of a firm shipping atoms, not just bits.

## Why it matters to Indian engineers

For the diaspora, Arista is both an opportunity and a signal. The company is hiring aggressively in networking, ASIC design and systems software — fields where Indian engineers are heavily represented — and expanding facilities in Santa Clara with an estimated $180 million in capital spending this year. As big software employers like Google and Amazon trim headcount, AI-infrastructure firms are absorbing exactly the kind of hardware and systems talent that visa-holding engineers bring.

There is an investing angle, too. Many NRIs hold the AI trade almost entirely through NVIDIA and the megacaps. Arista represents the "picks and shovels behind the picks and shovels" — the networking fabric that every hyperscaler must buy regardless of which chip vendor wins. When $1.3 trillion briefly evaporated from AI chip stocks last week before rebounding, infrastructure names like Arista were caught in the same whipsaw, a reminder that the whole stack now moves together.

The deeper point is about who builds the foundations of the AI era. While the headlines chase model launches and CEO feuds, a woman from the Indian diaspora has spent a decade quietly building the connective tissue without which none of those models run. At 1.6 terabits, Jayshree Ullal's bet on the network just got bigger — and so did the diaspora's footprint in the least glamorous, most indispensable corner of the boom."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
