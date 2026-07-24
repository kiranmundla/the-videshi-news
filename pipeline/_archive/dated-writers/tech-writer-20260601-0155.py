#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-01 01:55 PDT run.
Publishes 3 articles: C2i Semiconductors chip tape-out, Anthropic India expansion, India PLI 2.0.
"""

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

# Verify images return HTTP 200 and are > 5KB
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD doesn't give Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return url
    except Exception as e:
        print(f"  ⚠ Image verification failed for {url[:60]}: {e}")
    return None


# ──────────────────────────────────────────────────────────────────────
# Article 1: C2i Semiconductors AI power chip tape-out
# ──────────────────────────────────────────────────────────────────────

c2i_img = verify_image("https://images.pexels.com/photos/1432673/pexels-photo-1432673.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")

c2i_body = """C2i Semiconductors, a Bengaluru-based startup barely a year old, has taped out a smart power stage chip designed to regulate and optimise energy delivery across AI data centre infrastructure. The milestone — sending a finalised chip design to a foundry for fabrication — is unremarkable in Hsinchu or San Jose. In India, it is nearly without precedent.

The chip was conceived, architected and verified entirely by C2i's Indian engineering team. It addresses a growing bottleneck in the AI stack: power. As GPU clusters scale from hundreds to tens of thousands of processors, the electricity needed to feed them has become a first-order engineering constraint. Data centres now consume roughly 1–2 per cent of global electricity, and the share is climbing fast. C2i's chip sits in the power delivery network between the grid and the processor, claiming over 96 per cent conversion efficiency — a meaningful improvement over the roughly 94 per cent offered by incumbent solutions from Texas Instruments, Infineon and Monolithic Power Systems.

## Backed by Serious Money

The tape-out comes on the heels of a $16.7 million Series A round. Peak XV Partners (formerly Sequoia India) led the initial $15 million tranche in February; TDK Ventures participated in both the original and an oversubscribed extension. The funding trajectory is notable: C2i raised a $4 million seed from Yali Capital in November 2024, less than five months after incorporation. Investors are betting that India's chip design talent — long exported to power-management teams at Texas Instruments, Analog Devices and Qualcomm — can build original products at home.

C2i's product line includes the Manas Controller, a software-defined power management system designed to work across varying processor architectures, and the Sarayu Power Stage, a modular design meant to scale for high-current AI workloads. The names — drawn from Sanskrit — are a quiet assertion: this is Indian IP for global infrastructure.

## Where This Fits in India's Semiconductor Ambitions

India's semiconductor mission has been building momentum across multiple fronts: Tata Electronics' Dholera fab, Intel's $3.3 billion Odisha substrate facility, ASML's equipment pipeline. But these are stories about multinational investment flowing in. C2i represents something different — an Indian-founded company designing original silicon for a global market.

Amitesh Sinha, CEO of the India Semiconductor Mission and additional secretary at the Ministry of Electronics and IT, framed it bluntly: "C2i's fundraise followed by design tape-out is a powerful demonstration that Indian innovation can extend across the technology stack, from the power grid to the chip level."

The Design Linked Incentive (DLI) scheme, which has supported 24 chip design projects and 105 companies, is starting to show returns. C2i is among the earliest to reach tape-out under that programme.

## Why NRIs Should Pay Attention

For the tens of thousands of Indian-origin engineers working in semiconductor design at Intel, Qualcomm, Broadcom and AMD offices from Santa Clara to Austin, the C2i story shifts a calculation. India has long been where you did verification and back-end design for someone else's chips. If a Peak XV-backed startup can tape out a competitive power chip with a Bengaluru team, the return-to-India proposition in semiconductors just became more credible.

The global AI infrastructure market — servers, networking, cooling, and now power delivery — is projected to exceed $300 billion by 2028. C2i is betting that some of that value can be captured by Indian-designed silicon, not just Indian-staffed design centres.

The chip now heads to fabrication. If it performs to spec, C2i plans a broader pipeline of semiconductor products focused on AI infrastructure. For a country that has spent decades designing chips for others, the shift to designing chips as its own products may prove to be the real tape-out moment."""

# ──────────────────────────────────────────────────────────────────────
# Article 2: Anthropic's aggressive India expansion
# ──────────────────────────────────────────────────────────────────────

anthropic_img = verify_image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg")

anthropic_body = """Anthropic has appointed Siddiq Zaman as Head of Partnerships for India, the latest in a series of leadership hires signalling that the $65 billion AI company considers the Indian market worth staffing up for — not just selling into. Zaman joins Irina Ghose, the former Microsoft India managing director who was named Anthropic's India MD earlier this year when the company opened its Bengaluru office, its second in Asia after Tokyo.

The appointments are not cosmetic. India is now Claude's second-largest market globally, and the company says its India run rate has doubled since it announced expansion plans in October 2025. That growth is driven by a specific pattern: Indian developers have gravitated to Claude for coding tasks, which account for over half of all Indian Claude usage — roughly 50 per cent, compared to about a third globally.

## Enterprise Customers Are Signing On

The corporate adoption list reads like a roll call of India's most prominent companies. Air India is using Claude Code to accelerate custom software development. CRED — the fintech unicorn that has become a benchmark for product craft in India's startup ecosystem — reports faster feature delivery and improved test coverage with Claude. Most significantly, Cognizant is deploying Claude to 350,000 employees globally to modernise legacy systems and accelerate AI adoption.

That last data point deserves emphasis. Cognizant, led by CEO Ravi Kumar, employs roughly 250,000 people in India. When a company of that scale rolls out a single AI tool across its workforce, it is not an experiment. It is a signal about which platform the Indian IT services industry is standardising around.

## The Language and Education Play

Anthropic has invested in making Claude more useful in Indian languages. Six months ago, the company improved training data in 10 Indian languages including Hindi, Bengali, Marathi, Tamil and Telugu. It is now building evaluation benchmarks for locally relevant use cases in agriculture and law, working with Karya and the Collective Intelligence Project alongside nonprofits Digital Green and Adalat AI.

Educational use cases account for 12 per cent of Claude.ai usage in India. Nonprofit Pratham has partnered with Anthropic as a strategic AI lab collaborator, while Adalat AI is building a national WhatsApp helpline aimed at improving access to judicial services. These are not vanity partnerships — they are infrastructure bets on distribution channels that reach hundreds of millions.

## What This Means for Indian Tech Workers

For Indian-origin engineers in Silicon Valley, Anthropic's India push creates a dual opportunity. In the US, Anthropic's engineering team — led by global CTO Rahul Patil, who is of Indian origin — is hiring aggressively across research and applied AI roles. In India, the Bengaluru office is staffing up across enterprise sales, partnerships and engineering.

But the more consequential shift may be what Claude's enterprise adoption means for the Indian IT services workforce. If Cognizant's 350,000-person deployment proves that agentic AI tools can meaningfully accelerate legacy modernisation, the competitive pressure on TCS, Infosys, Wipro and HCL to adopt similar tools — or lose deals — becomes acute. The question is not whether Indian IT will adopt Claude and its competitors, but how fast the workforce retooling happens.

For NRI investors tracking AI companies, Anthropic's India traction adds a data point to the valuation debate. The company raised $65 billion at a staggering valuation. India being its second-largest market — and growing faster than the US on a percentage basis — suggests the valuation rests on more than American enterprise demand alone."""

# ──────────────────────────────────────────────────────────────────────
# Article 3: India's PLI 2.0 demands 55%+ domestic value addition
# ──────────────────────────────────────────────────────────────────────

pli_img = verify_image("https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")

pli_body = """India's government is rethinking how it subsidises smartphone manufacturing, and the revision carries a blunt message: assembly is no longer enough. The forthcoming PLI 2.0 scheme will require participating companies to achieve over 55 per cent domestic value addition in their devices — a sharp escalation from the original programme, which succeeded in making India the world's second-largest phone manufacturer by volume but left it importing more than half the value of every handset that rolled off its assembly lines.

The Finance Ministry's Expenditure Finance Committee has been sceptical. The original PLI scheme, launched in 2020 with a ₹40,995 crore ($5.7 billion) outlay, attracted 32 firms that collectively invested about ₹17,519 crore and generated production valued at ₹11.01 lakh crore ($134 billion). The export numbers were impressive — ₹6.27 lakh crore ($76 billion), far exceeding initial targets. But the ministry's scrutiny reveals a harder truth: a ₹41,000 crore subsidy programme that generated assembly operations while leaving the high-value component industry untouched did not fully deliver the manufacturing depth intended.

## The 55 Per Cent Problem

Understanding why 55 per cent domestic value addition is ambitious requires knowing where the money in a smartphone actually sits. In a typical mid-range Android device with a global average selling price of $250–300, the bill of materials accounts for roughly $150–200. Within that, display assemblies take the largest share — 20 to 30 per cent of total component cost. For OLED panels, production is controlled by Samsung Display and LG Display in South Korea, and BOE, CSOT and Tianma in China. India has no operational OLED panel facility of meaningful scale.

Then come application processors (designed in the US, fabricated in Taiwan, packaged in China or Malaysia), camera modules (China-dominated), NAND and DRAM memory (South Korea, Japan), and battery cells (China). The components India can currently source domestically — printed circuit board assembly, chargers, packaging materials, some passive components — account for perhaps 15 to 20 per cent of value.

PLI 2.0 will link directly with the ₹40,000 crore Electronic Component Manufacturing Scheme (ECMS), which aims to bring lithium-ion cell manufacturing, camera module assembly and display production onshore. Companies that demonstrate backward integration — sourcing high-value components from domestic suppliers — will receive higher incentive payouts.

## Who Wins, Who Sweats

Apple's contract manufacturers — Foxconn, Pegatron and Tata Electronics — now assemble a significant share of iPhones in India for global export. Under the new rules, they will face pressure to deepen their supplier base locally or see their incentive rates shrink. Samsung, which manufactures in Noida, faces similar calculations. The Chinese OEMs — Xiaomi, Oppo, Vivo — which dominate India's volume market, will need to decide whether deeper Indian manufacturing is worth the investment or whether they consolidate elsewhere.

For Indian EMS companies like Dixon Technologies, Kaynes Technology and Amber Enterprises, the revised scheme is a tailwind. They are already investing in component capabilities — Dixon in display assembly, Kaynes in semiconductor packaging — and higher value-addition requirements would route more work through domestic partners.

## The NRI Investment Angle

For diaspora investors who have watched India's electronics manufacturing story unfold, PLI 2.0 sharpens the thesis. The original scheme proved India could attract manufacturing volume. The revision tests whether it can attract manufacturing depth — the component fabs, display lines and battery plants that turn an assembly economy into a genuine industrial base.

The 75 facilities sanctioned under ECMS are in various stages of construction. Whether they come online fast enough to help OEMs hit 55 per cent targets will determine whether the next phase of Indian electronics manufacturing delivers the kind of high-value industrial jobs — and the investment returns — that the first phase only hinted at.

India exported smartphones worth $17 billion in FY2026. The government's bet is that demanding more value stay onshore will not drive that number down, but will instead force the supply chain to deepen. That bet is about to be tested."""

# ──────────────────────────────────────────────────────────────────────
# Assemble articles
# ──────────────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "C2i Semiconductors Just Taped Out India's First Homegrown AI Power Chip. The Country's Chip Ambitions Just Got Real.",
        "subheadline": "A Bengaluru startup backed by Peak XV and TDK Ventures has designed and taped out a smart power stage chip for AI data centres — entirely in India. It is one of the first original semiconductor products to emerge from the country's chip design ecosystem.",
        "slug": make_slug("c2i-semiconductors-india-ai-power-chip-tape-out"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of Indian-origin chip designers work at Intel, Qualcomm, Broadcom and AMD in the US. C2i's tape-out signals that India can originate competitive semiconductor products — not just staff design centres for foreign companies. The return-to-India calculus in semiconductors just shifted.",
        "tags": ["semiconductors", "india-chip-design", "ai-infrastructure", "c2i", "peak-xv", "india-semiconductor-mission"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/"},
            {"name": "Entrepreneur India", "url": "https://entrepreneurindia.com/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": c2i_img or "",
        "body": c2i_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Is Hiring Fast in Bengaluru. Claude's India Business Has Already Doubled.",
        "subheadline": "With a new Head of Partnerships, a former Microsoft India MD running operations, and Cognizant deploying Claude to 350,000 employees, Anthropic is making its most aggressive push yet into the world's second-largest Claude market.",
        "slug": make_slug("anthropic-india-bengaluru-claude-enterprise-expansion"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin engineers dominate AI research labs globally, and Anthropic's CTO Rahul Patil is of Indian origin. The Bengaluru expansion creates career paths on both sides of the Pacific. For H-1B holders at competing AI companies, Anthropic's India office offers a plan B that keeps them in the same industry.",
        "tags": ["anthropic", "claude", "bengaluru", "ai-enterprise", "indian-it", "cognizant", "ai-adoption"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/"},
            {"name": "MartechAI", "url": "https://martechai.com/"},
            {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/"},
            {"name": "OpenTools", "url": "https://opentools.ai/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": anthropic_img or "",
        "body": anthropic_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants 55% of Every Smartphone Made Locally. The Assembly Era Is Over.",
        "subheadline": "The government's PLI 2.0 scheme will demand that manufacturers source more than half their components domestically — a sharp escalation that could reshape how Apple, Samsung and Xiaomi operate in the country.",
        "slug": make_slug("india-pli-2-smartphone-55-domestic-value-addition"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors tracking India's electronics manufacturing boom face a sharpened thesis: PLI 2.0 tests whether the country can move from assembling iPhones to building the displays, batteries and chips inside them. For Indian-origin supply chain executives at Apple, Foxconn and Samsung, the deeper localisation mandate could create senior roles that did not exist a year ago.",
        "tags": ["pli-scheme", "india-manufacturing", "smartphones", "electronics", "make-in-india", "apple-india", "dixon-technologies"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/"},
            {"name": "Pulse", "url": "https://pulse.bot/"},
            {"name": "NewsPoint", "url": "https://www.newspointapp.com/"},
            {"name": "WhalesBook", "url": "https://whalesbook.com/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": pli_img or "",
        "body": pli_body
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
