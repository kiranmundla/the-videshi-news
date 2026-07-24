#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-06 09:00 UTC batch"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ─── Wikipedia person image helper ───
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ═══════════════════════════════════════════════════════════
# ARTICLE 1: Indian Immigrants Founded 96 US Unicorns
# ═══════════════════════════════════════════════════════════

art1_body = """India now leads every nation on earth in producing the founders of America's billion-dollar startups. That is not an aspiration or a projection. It is the conclusion of a new analysis by the National Foundation for American Policy, published this week, which found that Indian immigrants have founded or co-founded 96 US unicorn companies — more than Israel (60), the United Kingdom (47), and China (41) combined at the top two spots.

The numbers are striking in their density. Of approximately five million Indian immigrants living in the United States, roughly one in every 50,000 has gone on to create a company valued at a billion dollars or more. Collectively, immigrant-founded unicorns — 455 of America's 775 total — carry a combined valuation exceeding $5 trillion. That figure is larger than the entire German stock market.

## The IIT Pipeline

The report underscores what anyone in Bay Area tech circles already suspects: the Indian Institutes of Technology are the most efficient founder factories in the world. IIT Delhi alone produced 16 unicorn founders. IIT Bombay contributed 14. The pathway is well-worn — IIT to Stanford or MIT, a few years at Google or McKinsey, then a garage and a pitch deck. Seventy-six of the 96 Indian unicorn founders first arrived in the United States as international students.

Perplexity's Aravind Srinivas, an IIT Madras graduate, sits at the top of the value table. His AI search company is now valued at $20 billion, making it the highest-valued US unicorn with an Indian founder. Prasanna Sankar's Rippling, Deepak Pathak and Abhinav Gupta's Skild AI, Mohit Aron's Cohesity, and Manu Kumar's Carta fill out the upper ranks.

## The Paradox: Scale Without Size

But the NFAP data contains a subtle sting. Despite leading in absolute numbers, Indian-founded unicorns are conspicuously absent from the very top of the valuation league. The five most valuable US unicorns — SpaceX ($1.5 trillion), Anthropic ($965 billion), OpenAI ($852 billion), Databricks ($134 billion), and Stripe ($106.7 billion) — have no Indian founders. The majority of the 96 Indian-founded companies are valued below $10 billion.

The Hindu Business Line put it bluntly: Indian immigrant founders are "not shooting for the stars." Experts cite the cultural conservatism of the Indian middle class — a pipeline optimised for stable employment and executive careers rather than the existential risk of entrepreneurship. Indians have excelled at running other people's trillion-dollar companies (Nadella at Microsoft, Pichai at Google, Krishna at IBM) but are only now beginning to build their own.

## What This Means for You

For Indian tech professionals in the US, the data is both vindication and challenge. The ecosystem that produced these 96 founders — IIT admissions, F-1 visas, H-1B sponsorship, the cultural permission to leave a safe FAANG job — is under direct political pressure. USCIS processing delays have lengthened. The 60-day grace period after a layoff remains a ticking clock. And the very immigration pathways that delivered one in 50,000 Indians to unicorn-founder status are being questioned in Washington.

Israel, with a far smaller diaspora, produces 43.4 unicorn founders per 100,000 first-generation immigrants. India produces 2.5. The absolute numbers are impressive. The per-capita gap suggests an enormous reservoir of untapped potential — and a system that still channels most Indian talent toward employment rather than enterprise.

The question for the next decade is whether the pipeline that built 96 unicorns can build 960. The talent is there. The capital is there. What remains unclear is whether the immigration architecture — and the cultural nerve — will keep pace.

**Sources:**
National Foundation for American Policy (NFAP), June 2026; The Hindu Business Line; Livemint; Stanford Venture Capital Initiative"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Immigrants Built 96 US Unicorns. None Cracked the Top Five.",
    "subheadline": "A new NFAP study finds India leads the world in producing billion-dollar startup founders — but the biggest prizes still elude them.",
    "slug": make_slug("indian-immigrants-96-us-unicorns-nfap-report"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian immigrants have founded 96 US unicorns worth $5 trillion, making India the world's top source of billion-dollar startup founders. IIT Delhi (16 founders) and IIT Bombay (14) are the pipeline. But amid tightening immigration policy and H-1B uncertainty, the infrastructure that enabled this is under threat.",
    "tags": ["indian-founders", "unicorns", "silicon-valley", "startups", "nfap", "h1b", "iit"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "National Foundation for American Policy", "url": "https://nfap.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-is-largest-source-for-immigrant-founders-of-us-unicorns/article69656234.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market/"},
        {"name": "GKToday", "url": "https://www.gktoday.in/topic/india-leads-in-us-unicorn-founders/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/7413911/pexels-photo-7413911.jpeg",
    "image_caption": "Entrepreneur presenting a startup pitch to investors",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ═══════════════════════════════════════════════════════════
# ARTICLE 2: UPI Goes Live in Cambodia
# ═══════════════════════════════════════════════════════════

art2_body = """India's Unified Payments Interface went live in Cambodia on June 2, connecting Indian travellers to over 4.5 million merchant terminals across the country through a simple QR code scan. The launch, a collaboration between NPCI International Payments Limited and Cambodia's ACLEDA Bank, adds another country to UPI's expanding international network — and puts India's homegrown payment rails in direct competition with Visa and Mastercard across Southeast Asia.

The mechanics are straightforward. Indian visitors can open any UPI-enabled app — Google Pay, PhonePe, Paytm — and scan a Bakong KHQR code at restaurants, retail shops, and tourist spots across Cambodia. The payment settles in real time, debited directly from the user's Indian bank account. No international card surcharges. No currency conversion kiosks. No fumbling with riel banknotes.

## From Bhutan to Phnom Penh

Cambodia is the latest addition to a corridor that now spans at least ten countries. UPI-based payments are already operational in Singapore (via the PayNow link since 2023), the UAE, France, Bhutan, Nepal, Mauritius, Sri Lanka, and Qatar. A partnership with PayU and 8B is extending the system into Central Asia, covering Kazakhstan, Uzbekistan, and Kyrgyzstan. India has also joined Project Nexus alongside Malaysia, the Philippines, Singapore, and Thailand to build a multilateral instant payments network.

The RBI and NPCI have been methodical about this expansion. Each new corridor begins with person-to-merchant payments for Indian travellers, then scales to bidirectional flows. The Cambodia deployment follows this playbook: Phase 1 covers Indian tourists paying at Cambodian merchants. Phase 2, expected in the coming months, will allow Cambodian visitors to scan UPI QR codes at millions of merchant locations across India.

## Why NRIs Should Pay Attention

The surface story is convenience for tourists. The deeper story is infrastructure dominance. India processed over 14 billion UPI transactions per month in 2025, making it the largest real-time digital payment system on the planet. UPI now accounts for 85.5 per cent of all retail payments in India. By internationalising this system, India is exporting not just a payment protocol but a financial architecture that could eventually handle remittances — the $137.7 billion annual flow that sustains millions of Indian families.

For the five million Indians living in the United States and the broader diaspora, the implications are practical. If UPI corridors mature to handle person-to-person transfers at near-zero cost, the remittance industry — currently dominated by Western Union, Wise, and a constellation of fintech middlemen charging 2-5 per cent per transaction — faces genuine disruption. The Kuwait-India corridor already operates at 2.1 per cent, below the UN's 3 per cent benchmark. As more corridors come online, the cost of sending money home could fall further.

## The Competitive Landscape

India is not the only country building international payment rails. China's Alipay and WeChat Pay are deeply embedded across Southeast Asia. Indonesia and China recently launched the world's largest bilateral QR interoperability corridor. Singapore's PayNow, Thailand's PromptPay, and Malaysia's DuitNow are all part of the same regional integration push.

But UPI has a structural advantage: it is bank-agnostic, app-agnostic, and operated as public infrastructure rather than a proprietary platform. Any bank and any app can plug in. That openness — and the sheer scale of India's 1.4 billion population base — gives NPCI leverage that private payment networks cannot match.

The Cambodia launch is incremental. But incremental is how infrastructure scales. Every new QR code terminal, every new country corridor, every Phase 2 that flips on bidirectional flows brings India closer to building the global payment layer that Visa built in the credit card era. For the diaspora, the endgame is a world where sending money home costs nothing and takes seconds. We are not there yet. But we are closer than we were last week.

**Sources:**
Reserve Bank of India; NPCI International Payments Limited; ET Edge Insights; The Daily Jagran; Policy Circle"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's UPI Just Went Live in Cambodia. Ten Countries and Counting.",
    "subheadline": "NPCI's QR-based payment system now covers 4.5 million Cambodian merchants, part of a methodical push to build a global remittance-killing payments layer.",
    "slug": make_slug("upi-live-cambodia-ten-countries-global-payments"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "UPI's international expansion could eventually disrupt the remittance industry that moves $137.7 billion annually to India. For NRIs sending money home through Wise, Western Union, or bank wires, UPI corridors operating at near-zero cost represent a direct alternative. The Cambodia launch is the latest signal that India's payment rails are going global.",
    "tags": ["upi", "digital-payments", "india-fintech", "cambodia", "npci", "remittances", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "ET Edge Insights", "url": "https://www.etedge-insights.com/technology/digital-payments/upi-goes-global-india-cambodia-enable-real-time-qr-payments/"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/technology/upi-expansion-continues-npci-takes-upi-to-cambodia-check-which-other-countries-support-indian-qr-based-payment-system"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/indias-unified-payments-interface-upi-goes-live-in-cambodia/"},
        {"name": "Policy Circle", "url": "https://www.policycircle.org/economy/upi-global-expansion/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg",
    "image_caption": "Close-up of a contactless payment using a smartphone and QR code",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ═══════════════════════════════════════════════════════════
# ARTICLE 3: Anthropic Files for $1 Trillion IPO
# ═══════════════════════════════════════════════════════════

art3_body = """Anthropic has filed a confidential S-1 prospectus with the SEC, setting the stage for what could be the largest technology IPO in history. The Claude maker is targeting a valuation that clears $1 trillion, building on a Series H round that valued it at $965 billion — eclipsing OpenAI's $852 billion to become the world's most valuable private AI company. The listing could arrive as early as this autumn.

The velocity of Anthropic's ascent is difficult to overstate. Its valuation has risen roughly fivefold in under a year: $183 billion in September 2025, $380 billion in February 2026, $965 billion in May. The company's annualised revenue run rate has ballooned to $47 billion, up from approximately $10 billion a year earlier. It expects $10.9 billion in revenue for the second quarter alone — more than double the prior period — and is on pace for its first profitable quarter.

## Claude Code: The Engine

The growth traces largely to one product. Claude Code, Anthropic's AI coding assistant, has become a magnet for enterprise customers willing to pay serious money to let AI write and ship their software. The tool reached $1 billion in annualised recurring revenue just six months after launch. Unlike ChatGPT, which relies heavily on consumer subscriptions, Anthropic has built its revenue base on enterprise contracts — a stickier, more defensible revenue stream.

To sustain this explosive compute demand, Anthropic has secured a $15-billion-a-year data centre lease and maintains cloud partnerships with both Amazon Web Services and Google Cloud. Amazon has poured over $8 billion into the company. Alphabet has invested more than $2 billion. Those two companies, one led by Andy Jassy and the other by Sundar Pichai, are betting that Anthropic's Claude models will become critical infrastructure for enterprise AI.

## Why This Matters for Indian Tech Professionals

The Anthropic IPO arrives at a moment of tectonic shifting in the AI labour market. The three companies preparing to go public — SpaceX ($1.75 trillion target), Anthropic, and eventually OpenAI — are expected to raise a combined $200 billion, marking the start of what analysts are calling the AI race's capital markets reckoning.

For Indian engineers at Amazon, Google, Microsoft, and Meta, the Anthropic story has immediate implications. Amazon and Alphabet employees hold equity in companies that are Anthropic's largest backers. A successful Anthropic IPO would validate those investments and could lift the stock prices of both parent companies. Conversely, the talent war between frontier AI labs and the cloud giants is intensifying. Anthropic, OpenAI, and DeepMind are all competing for the same pool of AI researchers — a pool in which Indian-origin scientists are disproportionately represented.

There is also the competitive dimension. Microsoft has publicly positioned Anthropic as its primary benchmark. If Claude continues to outperform on enterprise AI tasks, Microsoft's Copilot strategy — and by extension, Satya Nadella's AI bet — faces a more formidable challenger than many investors anticipated.

## The Valuation Question

The market appetite for AI IPOs will be tested severely in the coming months. SpaceX's listing later this month will gauge whether investors will pay 100x trailing revenue for a pre-profit company with extraordinary growth. Anthropic will face similar scrutiny. At $47 billion in annualised revenue and a near-trillion-dollar valuation, the company trades at roughly 20x revenue — expensive by any standard, but cheaper than SpaceX and potentially cheaper than OpenAI, which is reportedly targeting a $1 trillion IPO on just $25 billion in annualised revenue.

For NRI investors, the Anthropic IPO offers a rare chance to buy directly into the AI infrastructure layer that currently exists only in private markets. Most retail investors have been limited to proxy exposure through Amazon and Google stock. A public Anthropic would change that equation.

Whether the price will be right is another question entirely. The AI industry has shifted from a technology demonstration phase to a commercial validation phase. Revenue growth matters now. Margins matter. And the question Perplexity's Aravind Srinivas posed last week — who can generate the most value per watt per user — may ultimately determine which of these trillion-dollar bets pay off.

**Sources:**
FXStreet; TheStreet; Motley Fool; Zacks Investment Research; Fortune; CNBC"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic Just Filed for a Trillion-Dollar IPO. Amazon and Google Have Billions Riding on It.",
    "subheadline": "The Claude maker's $965 billion valuation and $47 billion revenue run rate set up the largest AI listing ever — with Sundar Pichai's Alphabet and Jeff Bezos's Amazon among the biggest beneficiaries.",
    "slug": make_slug("anthropic-trillion-dollar-ipo-amazon-google-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Amazon and Alphabet, led by Andy Jassy and Sundar Pichai respectively, have invested over $10 billion combined in Anthropic. Indian engineers at both companies hold equity that rises or falls with Anthropic's success. The IPO also intensifies the AI talent war, where Indian-origin researchers are disproportionately represented across frontier AI labs.",
    "tags": ["anthropic", "ipo", "ai", "claude", "amazon", "google", "sundar-pichai", "venture-capital"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "FXStreet", "url": "https://www.fxstreet.com/analysis/spacex-and-anthropic-the-most-exciting-ipos-ever-202606050103"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/investing/wall-streets-biggest-banks-just-landed-the-al-ipo-of-the-year"},
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/06/anthropic-claude-may-be-only-1-trillion-ipo-worth-buying/"},
        {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2462000/spacex-and-anthropic-the-most-exciting-ipos-ever"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Dario Amodei, CEO of Anthropic, at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ═══════════════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════════════

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
