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

# Verify images
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Will Spend $150 Billion a Year in Taiwan. The AI Industry's Centre of Gravity Just Shifted.",
        "subheadline": "As Computex 2026 opens, Jensen Huang's unprecedented commitment — alongside AMD's $10 billion pledge — cements Taiwan as AI's indispensable supply chain hub. Indian engineers staff every node of this trillion-dollar ecosystem.",
        "slug": make_slug("nvidia-150-billion-taiwan-computex-ai-triangle"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of Indian-origin engineers work at Nvidia, AMD, and TSMC ecosystem companies. India's own fab ambitions in Gujarat, Odisha, and Dholera are positioning it as a potential fourth node in the AI semiconductor supply chain. NRI investors hold significant positions in NVDA, AMD, and TSM.",
        "tags": ["nvidia", "computex", "taiwan", "semiconductor", "ai-infrastructure", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-taiwan-computex-ai-infrastructure-2026-05-30/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/first-windows-pc-nvidia-chips-debut-next-week-2026-05-30/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-jensen-huang-taiwan-computex-keynote-2026"},
            {"name": "WCCFTech", "url": "https://wccftech.com/computex-2026-nvidias-biggest-event/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg",
        "body": """Jensen Huang has never been one for understatement. But even by his standards, the number he dropped in Taipei this week landed hard: Nvidia will spend as much as $150 billion a year in Taiwan. Not over five years. Not cumulatively. Per year.

The declaration, made ahead of Computex 2026 — the annual hardware trade show that Nvidia has effectively turned into its own AI showcase — is more than a spending pledge. It is a statement about where the centre of gravity in artificial intelligence infrastructure actually sits. And for the tens of thousands of Indian-origin engineers who design, fabricate, package, and deploy these chips, that centre is increasingly a triangle: Nvidia in Santa Clara, TSMC in Hsinchu, and SK Hynix in Icheon.

## The Triangle Alliance

Nvidia's Computex keynote on Monday is expected to formalise what the industry has been calling the "AI semiconductor triangle alliance." The three companies — Nvidia designing the GPUs, TSMC manufacturing them, SK Hynix supplying the high-bandwidth memory — control the bottleneck layer of the entire AI infrastructure stack.

AMD CEO Lisa Su added her own stake last week, committing more than $10 billion to Taiwan's AI sector. "Taiwan's AI role is moving from a semiconductor story to an infrastructure story," said Ryan Fletcher, a partner at McKinsey.

Translation: it is no longer enough to make chips in Taiwan. The island now needs to house the packaging, testing, cooling, networking, and assembly that turns a wafer into a working AI server. Nvidia alone has grown from 10 Taiwanese partners to 150 in recent years.

## The Vera Rubin Rollout

Monday's keynote will likely detail Nvidia's Vera Rubin platform — its next-generation AI factory stack combining Rubin GPUs with Vera CPUs. While no new hardware launches are expected at Computex, deeper integration with Taiwan's supply chain is the headline. Foxconn Chairman Young Liu, TSMC CEO C.C. Wei, and Quanta Computer Chairman Barry Lam have all met privately with Huang over the past week.

Separately, Reuters reported on Saturday that the first Windows PCs powered by Nvidia's ARM-based chips will debut at Computex and Microsoft's Build conference, with models from Microsoft's Surface brand and Dell. The move puts Nvidia in direct competition with Qualcomm's Snapdragon X series and further fragments Intel's grip on the PC market.

## Why Indian Engineers Should Watch

Nvidia's engineering workforce includes thousands of Indian-origin employees across its Santa Clara headquarters, Bangalore R&D centre, and Hyderabad design teams. AMD's Hyderabad campus is one of its largest globally. TSMC's advanced packaging teams increasingly draw on talent from India's semiconductor training programmes.

This matters because Taiwan's ascent as AI's infrastructure hub creates demand for the exact skill set that Indian engineering graduates possess: chip design, verification, physical design, firmware, and systems integration. When Huang says he will spend $150 billion a year in Taiwan, the job requisitions flow downstream to Nvidia's India offices within weeks.

There is a symmetry to watch, too. India's own semiconductor ambitions — Micron's Gujarat fab, Tata Electronics' Dholera facility, Intel's Odisha substrate plant — are positioned as extensions of this same supply chain. The question for Indian semiconductor professionals is whether India can become a fourth node in the triangle, or whether it remains a talent feeder for the existing three.

## The Investment Signal

For NRI investors, the numbers frame a simple thesis. Nvidia's market capitalisation sits above $5 trillion. TSMC trades near all-time highs. Micron just crossed $1 trillion. AMD continues to climb. The AI infrastructure trade is no longer speculative — it is a documented capital allocation with three- to five-year supply contracts already signed.

Computex 2026 may not produce any single surprise. But the aggregate picture — $160 billion in annual Taiwan commitment from Nvidia and AMD alone, the first Nvidia-powered Windows PCs, deeper supply chain integration — describes an industry that has chosen its geography and is building there at industrial scale.

Indian engineers helped design these systems. Indian capital is invested in these stocks. And India's own fabs are being built to feed this machine.

The triangle is set. The question is whether India earns a seat at the table or remains the best supplier of talent sitting outside the room."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm's $300 Windows Laptop Chip Was Built by an Indian-Origin Engineer. It Could Reshape Budget Computing.",
        "subheadline": "The Snapdragon C platform, led by Senior Director Mandar Deshpande, targets students and families with ARM-powered Windows laptops that undercut Apple's MacBook Neo by half.",
        "slug": make_slug("qualcomm-snapdragon-c-300-laptop-mandar-deshpande"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm's Hyderabad campus is one of its largest R&D centres globally. Mandar Deshpande's leadership of the Snapdragon C project places an Indian-origin engineer at the helm of what could become one of the highest-volume ARM PC chips. For Indian American families stretching budgets, a $300 laptop that works is a practical proposition.",
        "tags": ["qualcomm", "snapdragon", "arm", "budget-laptop", "indian-tech-leaders", "computex"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Engadget", "url": "https://www.engadget.com/computing/laptops/qualcomm-announces-the-snapdragon-c-for-entry-level-windows-laptops/"},
            {"name": "Android Authority", "url": "https://www.androidauthority.com/snapdragon-c-windows-laptops/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/05/29/qualcomm_snapdragon_c/"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/qualcomms-new-compute-chip-macbook-neo/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/93405/pexels-photo-93405.jpeg",
        "body": """Apple disrupted the budget laptop market when it launched the $599 MacBook Neo earlier this year. Now Qualcomm wants to cut that price in half.

The San Diego chipmaker announced the Snapdragon C platform ahead of Computex 2026, targeting Windows laptops priced at $300 and above. The effort is led by Mandar Deshpande, Qualcomm's Senior Director of Product Management for PC products, who described the chip's mission in characteristically understated terms: "With Snapdragon C, we're now raising the bar of what budget-conscious laptop buyers should expect."

The first device is already confirmed. Acer's Aspire Go 15 pairs the Snapdragon C with up to 8GB of RAM, 512GB of storage, and a 1080p display on a 15.6-inch screen — larger than the MacBook Neo's 13 inches. HP and Lenovo have also signed on as launch partners. Devices are expected to ship later this year.

## What the Chip Is — and Is Not

Deshpande confirmed that the Snapdragon C does not use Qualcomm's custom Oryon CPU cores — the architecture that powers the premium Snapdragon X Elite and X2 in high-end Windows laptops. Instead, it relies on Kryo cores derived from Qualcomm's mobile designs, essentially bringing smartphone-class efficiency to the PC.

The chip includes an integrated neural processing unit for on-device AI workloads, but Deshpande acknowledged it falls below the performance threshold Microsoft sets for its Copilot+ PC branding. In practical terms: basic AI features will work, but not the full suite of Windows AI capabilities that ship on premium machines.

What Qualcomm is promising instead is the basics done well — responsive performance, all-day battery life, and fanless, cool-running designs. No whirring fans during video calls or web browsing. The emphasis is practical: smooth browsing, video streaming, productivity applications, and the everyday computing that most people actually do.

## The Memory Problem

The Register raised a sharp operational concern: Qualcomm is launching a budget platform during a global memory supply crunch. DRAM prices have surged 60 to 110 per cent quarter-on-quarter in 2026, driven by AI server demand consuming available supply. That $300 sticker price may be harder to hit than it sounds when 8GB of RAM costs significantly more than it did six months ago.

The Acer Aspire Go 15's specs — 8GB RAM, 512GB storage — suggest a machine that could easily drift toward $400 or $450 at current component prices. Whether the final devices actually hit $300 at retail will depend on how aggressively manufacturers and Qualcomm subsidise the launch to establish the platform.

## The Indian Engineering Pipeline

Qualcomm's Hyderabad campus is one of the company's largest R&D centres globally, employing thousands of engineers who contribute to everything from modem design to the Snapdragon platform itself. Deshpande's leadership of the Snapdragon C project places an Indian-origin engineer at the helm of what could become one of the highest-volume ARM PC chips in the market.

For Indian American families — particularly those stretching a single tech-sector income across mortgage payments, children's education, and ageing parents in India — a $300 laptop that actually works is not a luxury product story. It is a practical one. The Chromebook-dominated bottom of the market has long been the default for second and third household devices. A Windows machine with all-day battery life at the same price point changes that calculus.

The pitch also resonates in India itself, where Qualcomm is increasingly positioning ARM-based computing as the default for education and small business. If the Snapdragon C proves capable enough at $300, it creates a template that could eventually bring sub-$200 ARM laptops to India's domestic market — a move that would reach the 300 million students in India's education system who currently share one device per household, if they have one at all.

## The Bigger ARM Bet

The Snapdragon C arrives as Nvidia prepares to debut its own ARM-based Windows PC chips at Computex, and as Intel and AMD defend their x86 territory in a market that is visibly fragmenting. For the first time, Windows laptop buyers will have four architecture options: Intel x86, AMD x86, Qualcomm ARM, and Nvidia ARM.

Deshpande's chip is not the fastest or the smartest in that lineup. It is designed to be the most accessible. Whether that is enough to matter depends on a question the budget PC market has never convincingly answered: can cheap actually be good?

Qualcomm is betting an Indian-origin engineer's reputation on the answer being yes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Digital Rupee Is Going Cross-Border. The RBI Just Signed CBDC Pacts With Singapore and the UAE.",
        "subheadline": "The Reserve Bank of India's annual report reveals cross-border CBDC pilots, welfare payment experiments in three states, and a cloud platform for banks — India's digital public infrastructure is being exported.",
        "slug": make_slug("rbi-digital-rupee-cbdc-singapore-uae-cross-border"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India leads the world in inbound remittances at $137.7 billion annually. UPI is now live in 8 countries including UAE and Singapore — the two largest NRI hubs. Cross-border CBDC pilots target exactly where Indian professionals live and send money home from.",
        "tags": ["rbi", "digital-rupee", "cbdc", "upi", "fintech", "india-dpi", "remittances"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/finance/indias-rbi-plans-expansion-digital-rupee-welfare-cross-border-2026-05-30/"},
            {"name": "The Asset", "url": "https://www.theasset.com/article/interoperable-digital-payment-systems-bridge-more-markets"},
            {"name": "Policy Circle", "url": "https://www.policycircle.org/fintech/india-upi-global-expansion/"},
            {"name": "Angel One", "url": "https://www.angelone.in/news/government-expand-upi-international-presence"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg",
        "body": """The Reserve Bank of India buried a significant technology story in its 2025-26 annual report, released on Friday. India's central bank digital currency — the digital rupee — is going international.

The RBI has signed a digital assets pact with Singapore's Monetary Authority and is in discussions to pilot cross-border CBDC transactions with both Singapore and the United Arab Emirates. It is also participating in multilateral CBDC initiatives led by the Bank for International Settlements. For the estimated 32 million Indians living abroad, the implications are direct: the same digital infrastructure that makes paying for chai in Chennai instantaneous may soon make sending money home from Dubai or Singapore faster, cheaper, and free of correspondent banking fees.

## Welfare Pilots, Shrinking Retail Adoption

Domestically, the digital rupee is being tested in unexpected terrain. The RBI reported multiple welfare-linked CBDC pilots during the fiscal year in Gujarat, Puducherry, and Chandigarh, where beneficiaries received food subsidies through the digital rupee. The programmability feature — the ability to attach conditions to digital currency, ensuring funds are spent only on approved items — is what makes CBDC attractive to government agencies distributing benefits.

But there is a counterpoint the RBI did not bury: retail digital rupee circulation fell to ₹7.71 billion as of March 2026, down from ₹10.16 billion a year earlier. The e-rupee remains a niche product in a country where UPI processes over 21 billion transactions a month and handles roughly half of all payment activity. The digital rupee is not competing with cash. It is competing with UPI, and UPI is winning.

## The Cloud Move Nobody Noticed

Perhaps the report's most technically ambitious announcement received the least coverage. The RBI's cloud platform for financial firms went live in beta mode with nine users, making India's central bank among the first globally to offer regulated cloud infrastructure to its banking sector.

The platform represents a philosophical shift. Central banks have historically regulated technology choices. Building and operating the technology itself is a different mandate entirely, and one that puts the RBI in direct conversation with AWS, Azure, and Google Cloud — all of which have established India regions courting the same financial services customers.

For Indian-origin cloud architects working at the hyperscalers, this is a development worth watching. The RBI is not trying to replace AWS. It is building a sovereign alternative for the most regulation-sensitive workloads — the kind of infrastructure that could eventually host India's CBDC rails, payment switches, and bank-to-bank settlement systems.

## UPI's Quiet Global March

While the digital rupee experiments play out, UPI's international expansion continues to accumulate countries. The system is now live in eight nations: the UAE, Singapore, Bhutan, Nepal, Sri Lanka, France, Mauritius, and Qatar. India has signed 23 memorandums of understanding for India Stack sharing as of February 2026.

The NRI use case is already live. Indian tourists in the UAE can use Google Pay, BHIM, or PhonePe to scan QR codes at retail stores and duty-free shops, seeing the amount in dirhams while paying directly in rupees. Singapore's PayNow linkage with UPI enables the same flow for the hundreds of thousands of Indian professionals in the city-state.

India has also joined Project Nexus, a multilateral initiative alongside Malaysia, the Philippines, Singapore, and Thailand to connect domestic payment systems for instant cross-border retail payments.

## What NRIs Should Watch

Two threads matter for the Indian diaspora.

First, remittances. India leads the world in inbound remittances at $137.7 billion annually. Every percentage point reduction in transaction costs — currently averaging around five to six per cent on many corridors — translates to billions of dollars staying in families' pockets rather than feeding intermediary banks. UPI-linked cross-border rails, if scaled, could undercut Western Union and Wise on the India corridor specifically.

Second, the CBDC pilots with Singapore and the UAE target precisely the two largest hubs of Indian professional expatriates. If the pilots succeed, NRIs in these countries could eventually receive salary payments or make property investments in India through a central bank-backed digital channel, bypassing the SWIFT network entirely.

The technology is not science fiction. India has already built UPI, Aadhaar, and DigiLocker into functioning digital public infrastructure used by over a billion people. The cross-border CBDC work is an extension of that same engineering ambition.

Whether the digital rupee finds its audience or remains a solution searching for a problem beyond UPI's shadow is genuinely unclear. But the RBI is no longer running domesticised pilots alone. It is exporting the plumbing — and the two countries it chose to start with are exactly where Indian money and Indian talent already live."""
    }
]

# Verify images before publishing
for art in articles:
    img = art.get("image_url", "")
    if img:
        ok = verify_image(img)
        print(f"Image check for '{art['slug']}': {'✅ OK' if ok else '⚠️ FAILED'} — {img}")

print()

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
