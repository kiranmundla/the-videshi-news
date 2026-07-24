#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 21:00 UTC run."""
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

def verify_image(url):
    """Verify image URL is accessible and substantial."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        r2 = requests.get(url, timeout=10, stream=True)
        if r2.status_code == 200 and "image" in r2.headers.get("Content-Type", ""):
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠️ Image verification failed for {url[:80]}: {e}")
    return False


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────
art1_body = """Salil Parekh earned ₹82.6 crore ($8.69 million) last year. The median Infosys employee earned ₹11.1 lakh. That is a ratio of 742 to one.

The numbers, disclosed in Infosys's annual report released on Friday, tell a story about more than one man's pay cheque. They capture the state of an industry that employs over 300,000 people in India — and tens of thousands more in the United States — while facing the most significant structural threat since the 2008 recession.

## The Pay Package

Parekh's compensation breakdown is instructive. His fixed salary was ₹8.5 crore — roughly $900,000, modest by Fortune 500 standards. The variable pay and incentives added ₹23.35 crore. But the real number is the ₹50.75 crore he realised from exercising restricted stock units granted in prior years. Stock options now account for over 61 per cent of his total pay.

By comparison, K. Krithivasan, CEO of the larger rival Tata Consultancy Services, earned $2.96 million for the same fiscal year. TCS had a higher revenue growth rate. Parekh's pay was nearly three times Krithivasan's, driven almost entirely by equity.

The dollar figure actually fell from $9.44 million in fiscal 2025, but not because of a pay cut. The Indian rupee depreciated 9.88 per cent against the dollar during the year, which deflated the conversion. In rupee terms, Parekh's compensation rose.

## The AI Cloud Over Bengaluru

The compensation disclosure landed at a delicate moment. Indian IT stocks fell to their lowest point in three years earlier this month after OpenAI announced a new services-led venture — a direct incursion into the territory that Infosys, TCS, Wipro, and HCL have dominated for two decades.

Infosys projected revenue growth of just 1.5 to 3.5 per cent in constant currency terms for fiscal 2027. That is below what analysts expected. India's $315 billion IT services sector, which built its empire on executing other companies' technology projects, now faces clients who are increasingly asking whether AI agents can do the same work for less.

The median employee pay increase at Infosys was 4 per cent. The average annual salary increase, including promotions, was 11 per cent. Those are respectable numbers. But the 742x ratio speaks to a deeper question: whether the economics of Indian IT outsourcing — which created a prosperous middle class of engineers earning ₹10-30 lakh annually — can survive the shift to AI-automated services.

## What This Means for the Diaspora

For the estimated 40,000 to 60,000 Indians working at Infosys's US operations — many on H-1B and L-1 visas — the company's growth trajectory is not an abstract metric. Slower growth means fewer new projects, fewer visa transfers, and greater scrutiny of headcount.

For NRI investors, Infosys (listed as INFY on NASDAQ and INFY.NS on the NSE) remains one of the most liquid Indian ADRs. The stock's performance dictates whether Parekh's equity grants appreciate or stagnate, which in turn shapes the calculus of whether leadership continuity is worth the premium. Parekh's current five-year term as CEO ends in March 2027, and the annual report notably did not address an extension.

The question facing Infosys — and by extension, every major Indian IT employer — is whether the industry can pivot from being the world's back office to being the world's AI builder. That transformation will determine whether the 742x ratio is a reflection of value created, or a relic of an era that is ending.

Parekh's stock options say the board believes he can navigate the transition. The median employee earning ₹11 lakh does not have that luxury of time."""

art1_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/technology/infosys-ceos-compensation-rises-25-nearly-87-million-fiscal-2026-2026-05-29/"},
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/what-powered-salil-parekhs-82-cr-pay-package-at-infosys"},
    {"name": "Ainvest", "url": "https://www.ainvest.com/news/infosys-ceo-salil-parekh-compensation-fy26/"}
])


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────
art2_body = """Lenskart, India's largest eyewear company, has begun shipping its first AI-powered smart glasses — and the product is not a Ray-Ban knockoff built in Shenzhen. It is designed and engineered in India, runs on Google's Gemini AI, and can make UPI payments by scanning a QR code through its lens.

More than 35,000 people signed up for the waitlist before commercial launch. At ₹27,000 (roughly $285) for the standard version and ₹22,000 ($232) for early access users, the B by Lenskart smart glasses are priced to undercut Meta's Ray-Ban Gen 3 ($329) and Google's upcoming Gemini Pro glasses ($399) while offering something neither competitor does: payments built into the frame.

## What Is Inside the Frame

The hardware specifications are serious. A 12-megapixel Sony camera handles photos and video. Three microphones power voice interaction and calls. Directional speakers deliver audio without earbuds. The Qualcomm Snapdragon AR1 processor — the same chip family that powers Meta's Ray-Ban glasses — runs the show. The frame weighs 40 grams, which Lenskart claims is roughly 20 per cent lighter than comparable products on the market.

The software layer is where it gets interesting. The AI assistant, called Buddy, is powered by Google Gemini 2.5 Live and can converse in more than 40 languages, including Hinglish and several Indian regional languages. It responds using visual context — point the glasses at a restaurant menu and Buddy can explain the dishes, estimate calories, or translate from Tamil to English.

Lenskart is also opening its platform to third-party developers. The company has announced integrations for food delivery, entertainment, fitness tracking, and booking services — an explicit attempt to build what Peyush Bansal, Lenskart's co-founder and CEO, calls "India's first full-stack wearables ecosystem."

## The India Manufacturing Story

The strategic significance extends beyond the product itself. Lenskart is a vertically integrated manufacturer with over 2,000 retail stores across India, Singapore, and the Middle East. It went public in recent years and is now valued at several billion dollars. The decision to design and build smart glasses in-house, rather than white-labelling a Chinese ODM product, is a deliberate signal.

India's wearables market has historically been dominated by imported products and Chinese brands. Noise, BoAt, and Fire-Bolts of the world sell smartwatches at scale, but none have attempted AI-integrated glasses with their own software stack. Lenskart is the first Indian company to attempt a vertically integrated play in a category that Google, Meta, Samsung, Apple, and Xiaomi are all chasing globally.

## Why NRIs Should Pay Attention

For the Indian diaspora, Lenskart is already a familiar brand — the go-to stop for prescription glasses during trips home, now increasingly available in international markets. The smart glasses represent a different proposition: a Made-in-India consumer electronics product competing head-to-head with Silicon Valley in a category that barely existed three years ago.

The UPI integration is particularly telling. While Meta and Google are building glasses for Western consumers who pay with Apple Pay or Google Wallet, Lenskart is building for a market where 14 billion UPI transactions happen monthly. Scanning a QR code with your glasses and confirming payment by voice is the kind of feature that could define how a billion people interact with commerce.

The global smart glasses market is projected to reach $4 to 5 billion by 2030, growing at nearly 30 per cent annually. India is expected to be among the largest markets. Whether Lenskart can compete with the R&D budgets of Meta and Google is an open question, but it has one advantage those companies do not: it already has prescription lens customers walking into 2,000 stores, many of whom might replace their regular frames with a pair that happens to have an AI assistant built in.

For NRI investors tracking the next wave of Indian consumer technology — beyond Zomato and Swiggy — B by Lenskart is a product worth watching."""

art2_sources = json.dumps([
    {"name": "E-Commerce News India", "url": "https://www.ecommercenews.in/lenskart-launches-gemini-ai-smart-glasses-in-india/"},
    {"name": "Digit.in", "url": "https://www.digit.in/smartwatches-fitness-bands/lenskart-announces-b-by-lenskart-ai-smartglasses-with-gemini-live-assistant/"},
    {"name": "Medianama", "url": "https://www.medianama.com/2025/12/223-lenskart-to-launch-ai-smart-glasses-by-march-2026/"}
])


# ── ARTICLE 3 ──────────────────────────────────────────────────────────────────
art3_body = """Ravi Kumar S has spent $1 billion and two years trying to prove a thesis: that an Indian IT services company can build AI products, not just implement them for clients. On June 5, he will present the results at Cognizant's first-ever AI Forum, a one-day event in which the CEO and CFO Jatin Dalal will make the case to investors and enterprise clients that the bet is paying off.

The timing is deliberate. Indian IT services stocks are reeling from OpenAI's announcement of an enterprise services venture, which investors interpreted as a direct threat to the outsourcing model. Cognizant's stock has not been immune. Kumar needs to show that his company is on the other side of that disruption — the side that builds the AI, rather than the side that gets displaced by it.

## The AI Product Stack

Cognizant's AI play has three layers. The first is Neuro AI, a platform the company launched for enterprise-wide AI deployment. The latest addition is a cybersecurity module that uses AI for threat detection and risk management — a direct play against the growing market for AI-driven security tools, which Palo Alto Networks (led by fellow Indian-origin CEO Nikesh Arora) has been dominating.

The second layer is industry-specific AI solutions. Cognizant recently launched healthcare large language models in partnership with Google Cloud, designed for clinical documentation, drug development support, and patient data analysis. Healthcare is a sector where Indian IT companies have deep client relationships but have historically been confined to back-end IT management rather than clinical tools.

The third layer is the workforce transformation itself. Under Kumar's leadership, Cognizant ran what it claims was the world's largest vibe coding event — a generative AI hackathon involving 53,000 employees across 40 countries, which produced over 30,000 prototype projects and earned a Guinness World Record. The company says 20 per cent of its code is now written by machines, and that proportion is rising.

## From Infosys to Cognizant

Kumar's biography is itself a diaspora story. He spent over two decades at Infosys, rising to president before making the unusual move of departing for Cognizant — a New Jersey-headquartered company that, despite its American address, has always been deeply Indian in its workforce and client-serving model. He was named to the 2025 TIME 100 AI list, a recognition that placed him alongside the CEOs of OpenAI and Anthropic.

The challenge he faces is structural. Cognizant's revenue in recent quarters has been powered by large outsourcing deals, not AI product sales. The $1 billion AI investment is a bet on a future revenue mix that has not yet materialised at scale. Enterprise clients are interested in AI — but their spending patterns suggest caution. They want proof of ROI before committing to AI-first service models, and Cognizant needs to deliver those proof points faster than its competitors.

## The NRI Career Calculus

For the tens of thousands of Indian professionals who work at Cognizant's US operations — many of them in New Jersey, Texas, and the Bay Area — Kumar's AI transformation has direct career implications. The shift from traditional IT services to AI product development means different skills, different project structures, and potentially different visa categories.

Engineers who spent years managing legacy Java and .NET applications are now being retrained on prompt engineering, model fine-tuning, and agentic AI workflows. Those who adapt will find themselves in a growing market. Those who do not will be competing for a shrinking pool of traditional outsourcing roles.

The AI Forum on June 5 will be webcast live, and Wall Street analysts will be watching closely. Kumar has made his bet. The question now is whether he can demonstrate enough enterprise AI traction to justify the $1 billion spent — and convince investors that Cognizant is becoming an AI builder, not just an AI services reseller.

For the Indian-origin professionals who make up the backbone of companies like Cognizant, TCS, and Infosys, the answer to that question will shape the next decade of their careers."""

art3_sources = json.dumps([
    {"name": "PR Newswire / Barchart", "url": "https://www.barchart.com/story/news/32816766/cognizant-to-host-ai-forum-on-june-5-2026"},
    {"name": "Ainvest / TIME 100 AI", "url": "https://www.ainvest.com/news/cognizant-ceo-ravi-kumar-time-100-ai/"},
    {"name": "Gartner", "url": "https://www.gartner.com/en/articles/how-genai-is-changing-enterprise-it-ravi-kumar-cognizant"}
])


# ── IMAGE VERIFICATION ─────────────────────────────────────────────────────────
images = {
    "art1": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "art2": "https://upload.wikimedia.org/wikipedia/commons/3/36/Peyush_Bansal.jpg",
    "art3": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
}

print("Verifying images...")
for label, url in images.items():
    ok = verify_image(url)
    print(f"  {label}: {'✅' if ok else '❌'} {url[:80]}")


# ── BUILD ARTICLES ──────────────────────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Salil Parekh Earned ₹82.6 Crore Last Year. His Median Employee Made ₹11 Lakh.",
        "subheadline": "Infosys's annual report reveals a 742-to-1 pay ratio as AI disruption threatens the Indian IT model that created the gap in the first place.",
        "slug": make_slug("salil-parekh-infosys-ceo-pay-742x-median-ai-disruption"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of Indians work at Infosys US offices on H-1B and L-1 visas; the company's growth trajectory directly affects their career stability. NRI investors hold INFY as one of the most liquid Indian ADRs on NASDAQ.",
        "tags": ["infosys", "indian-it", "ceo-compensation", "ai-disruption", "h1b"],
        "urgency": "medium",
        "sources": art1_sources,
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": images["art1"],
        "body": art1_body,
        "is_editorial": False,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Lenskart Just Launched India's First AI Smart Glasses. 35,000 People Were Already in Line.",
        "subheadline": "The ₹27,000 glasses run on Google Gemini, make UPI payments, and speak Hinglish — and they were designed and built entirely in India.",
        "slug": make_slug("lenskart-b-gemini-ai-smart-glasses-india-upi"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Lenskart is familiar to most NRIs as India's largest eyewear chain. The smart glasses represent India's first vertically integrated consumer electronics play in a category dominated by Meta, Google, and Samsung — a signal that Indian hardware manufacturing is moving beyond smartwatches.",
        "tags": ["lenskart", "smart-glasses", "gemini-ai", "made-in-india", "upi", "wearables"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": images["art2"],
        "body": art2_body,
        "is_editorial": False,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Cognizant's Ravi Kumar Bet $1 Billion on AI. On June 5, He Has to Show It Worked.",
        "subheadline": "The Indian-origin CEO is hosting Cognizant's first AI Forum as OpenAI threatens the outsourcing model that built his industry.",
        "slug": make_slug("cognizant-ravi-kumar-1-billion-ai-forum-enterprise"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of Indian professionals work at Cognizant's US operations, many in New Jersey, Texas, and the Bay Area. Kumar's AI transformation directly affects their career paths — from traditional IT services to AI product development, which demands different skills and potentially different visa categories.",
        "tags": ["cognizant", "ravi-kumar", "enterprise-ai", "indian-it", "ai-transformation"],
        "urgency": "medium",
        "sources": art3_sources,
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": images["art3"],
        "body": art3_body,
        "is_editorial": False,
    },
]

# ── INSERT ──────────────────────────────────────────────────────────────────────
print("\nPublishing articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
