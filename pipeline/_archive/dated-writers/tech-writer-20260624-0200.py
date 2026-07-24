#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

# ============================================================
# ARTICLE 1 — Indian-origin tech leaders beat: Kunal Shah → WhatsApp
# ============================================================
body1 = """Mark Zuckerberg has run out of patience trying to crack payments on his own. So he is paying $900 million for a man who already did it.

On June 22nd Meta said it would invest about $900 million in CRED, the Bengaluru fintech, and install its founder, Kunal Shah, as the global head of WhatsApp. The deal values CRED at roughly $4.5 billion and hands Meta a minority stake of around 20%. Will Cathcart, who has led WhatsApp since 2019, moves to a new product role inside the company. Miten Sampat, CRED's strategy and finance chief since 2020, takes over as interim CEO.

The arithmetic is unusual, and so is the symbolism. Shah becomes the first Indian to run the world's largest messaging app — a service with more than half a billion users in India alone. For a country that already supplies the chief executives of Google, Microsoft, Adobe and IBM, the appointment extends the diaspora's reach from enterprise software and search into the most intimate corner of consumer tech: the app on nearly every Indian phone.

## A roundabout acquisition

Strip away the announcement language and the structure is telling. Meta is not buying CRED outright. It takes a minority position, caps its stake, will not get a board seat, and — crucially — gets no access to CRED's customer data. The Economic Times reported that part of the consideration comes as $100 million in Meta ad credits rather than cash.

That careful framing exists because Meta has tried, and failed, to win Indian payments before. WhatsApp Pay launched in India years ago and has barely dented a market dominated by PhonePe (owned by Walmart's Flipkart) and Google Pay. India's central bank has kept Big Tech's payment ambitions on a tight leash, and even a 30% market-share cap on any single UPI app hangs over the sector. By hiring the founder who built a profitable consumer-finance brand inside those constraints — rather than buying a payments licence — Meta is betting on talent and trust rather than control.

## Why an NRI should read past the headline

For the Indian-American reader, three things matter here.

First, leverage. Shah did not sell his company and disappear. He keeps a personal stake of under 20% in CRED, gives up his board seat, and walks into one of the most powerful product jobs in tech. It is the clearest recent example of an Indian founder converting a homegrown startup into a global operating role — the reverse of the usual "sell and retire" arc that diaspora entrepreneurs know well.

Second, the regulatory subtext. CRED is reportedly preparing for an eventual IPO, and Meta's investment is a primary-and-secondary mix that gives early backers liquidity. For NRIs who track Indian fintech as an asset class — through funds, ESOP secondaries, or angel positions — the deal sets a fresh private-market benchmark at $4.5 billion for a company that only just turned its first profitable quarter on roughly ₹3,200 crore ($325m) in annual revenue.

Third, the competition question. Reuters noted that WhatsApp is, in effect, buying up a payments competitor in a roundabout way, and there are already calls in India to review the deal. Any NRI sending money home, paying an Indian merchant, or building on UPI rails should watch whether regulators treat a Meta-Shah WhatsApp as a neutral pipe or a dominant player to be contained.

## The bigger pattern

Shah's move lands in a week thick with diaspora-leadership news, and it fits a now-familiar template: Indian operators who learned to scale under India's unforgiving regulatory and pricing conditions are increasingly the ones global firms trust to run their hardest consumer problems. Building a fintech that 17 million paying members tolerate — in a country where users expect everything free — is arguably harder training than running a Western unicorn.

Whether Shah can finally make WhatsApp Pay work where everyone before him stumbled is an open question. The Indian central bank has not changed its mind about Big Tech and money. But Zuckerberg has decided that if WhatsApp is going to become a commerce platform, the person to build it should be someone who already did it once, in the toughest market on earth — and happens to know that market better than anyone in Menlo Park."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Just Made an Indian Founder the Boss of WhatsApp. The $900 Million Price Tag Tells the Real Story.",
    "subheadline": "Kunal Shah becomes the first Indian to run the world's biggest messaging app, as Meta takes a 20% stake in his fintech CRED at a $4.5 billion valuation.",
    "slug": make_slug("kunal-shah-whatsapp-ceo-meta-cred-900-million-deal-nri-fintech"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "An Indian founder who scaled a profitable fintech under India's strict rules now runs the app on nearly every NRI's phone — a marker of diaspora leverage, a fresh $4.5bn benchmark for Indian fintech investors, and a regulatory fight worth watching for anyone who sends money home over UPI.",
    "tags": ["kunal-shah", "whatsapp", "meta", "cred", "indian-tech", "fintech", "upi"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Mark Zuckerberg tries to buy payments redemption", "url": "https://www.reuters.com/breakingviews/mark-zuckerberg-tries-buy-payments-redemption-2026-06-23/"},
        {"name": "PYMNTS — Meta Backs India's Cred and Hires Founder to Run WhatsApp", "url": "https://www.pymnts.com/news/investment-tracker/2026/meta-backs-indias-cred-and-hires-founder-to-run-whatsapp/"},
        {"name": "Exchange4media — Meta to invest $900 million in Cred", "url": "https://www.exchange4media.com/digital-news/meta-to-invest-900-million-in-cred-names-founder-kunal-shah-as-whatsapp-chief.html"},
    ]),
    "score_total": 86,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
    "image_caption": "CRED founder Kunal Shah, named the new global head of WhatsApp",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": body1,
}

# ============================================================
# ARTICLE 2 — Diaspora founders / AI infrastructure beat: Upscale AI
# ============================================================
body2 = """The headline number from AI is usually about chips. The bottleneck, increasingly, is the wiring between them — and a Palo Alto startup run by Indian-American veterans just raised half a billion dollars to own it.

Upscale AI said on June 22nd it had added a $190 million extension to its Series A, lifting its valuation to $2 billion and its total funding to $500 million. The round was led by Premji Invest, the investment arm of Indian billionaire Azim Premji, with Nvidia, Salesforce Ventures, Singapore's Temasek and Seligman Ventures joining. Tiger Global, Mayfield, Prosperity7 and StepStone, all earlier backers, returned.

Upscale builds the unglamorous plumbing of artificial intelligence: hardware, systems and software that connect AI chips, memory and storage across one fast network so giant models can train and run without choking on data bottlenecks. As clusters swell to tens of thousands of accelerators, the network — not the chip — is often what decides how fast and how cheaply a model runs.

## A diaspora pedigree

The company is a study in Indian-American serial entrepreneurship. Executive chairman Rajiv Khemani founded Innovium, the networking-chip firm Marvell bought for about $1.1 billion, after senior stints at Intel, Cavium and Sun Microsystems. CEO Barun Kar spent 15 years as an engineering SVP at Palo Alto Networks, with earlier years at Juniper and Motorola. Upscale was spun out of Auradine, a blockchain-and-AI company the pair also built.

This is the part of Silicon Valley the diaspora has quietly dominated for two decades: deep infrastructure, where reputations are earned over multiple exits and investors back the people as much as the product. "We're excited to partner with repeat founders Rajiv and Barun," said Umesh Padval of Seligman Ventures — himself an Indian-American chip veteran — calling open-standard fabrics "critical" as AI clusters scale across messy, mixed environments.

## Why this matters to an NRI

For Indian-American engineers and investors, Upscale is a useful signal in a jittery week. The Nasdaq has been selling off on AI-bubble fears, the chip rout dragged down Qualcomm and the memory names, and "is this overbuilt?" is the question of the season. Yet the smart money — Nvidia, Premji Invest, Temasek — is still writing nine-figure checks for the infrastructure layer rather than another chatbot. The thesis: even if model hype cools, the data centres being built now will need better networking for years.

There is also a homegrown-capital angle. Azim Premji made his fortune at Wipro, the Bengaluru IT giant, and Premji Invest leading a $190m round into a diaspora-founded AI firm in Palo Alto is exactly the cross-border flow NRIs increasingly want exposure to — Indian wealth backing Indian-origin founders building frontier American tech. For the engineer at Google or Nvidia weighing whether to join an infrastructure startup, Upscale is the kind of credentialed, well-funded bet that de-risks the leap.

## The open-standard wager

Upscale's actual product strategy is a contrarian one. The hyperscalers — Amazon, Meta, Google — are racing to build proprietary in-house networking, locking customers into their own fabrics. Upscale is betting on open standards instead: SONiC, Ultra Ethernet, Ultra Accelerator Link and the Switch Abstraction Interface, the same consortia-driven technologies that let buyers mix vendors instead of being captured by one.

That is a deliberate pitch to enterprises and second-tier clouds that fear being trapped in Nvidia's or AWS's walled gardens. It is also a crowded fight: every big-tech firm is pouring money into networking, and rival startups are raising aggressively. But Upscale's leadership has, as Kar likes to note, "been at the center of every major computing shift over the past 20 years."

For the diaspora reader, the lesson is less about one company than about where the value is migrating. The AI gold rush minted chip fortunes first. The next layer — the connective tissue that makes thousands of chips behave like one machine — is being built disproportionately by Indian-origin engineers, funded by Indian capital, in the heart of Silicon Valley. Upscale's $2 billion valuation is one more data point that the diaspora's edge has moved up the stack, from writing software to laying the rails AI runs on."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nvidia and Azim Premji Just Bet $190 Million on AI's Least Glamorous Problem. The Founders Are Indian-American.",
    "subheadline": "Upscale AI, run by serial diaspora entrepreneurs, hit a $2 billion valuation building the networking 'plumbing' that connects AI chips — funded by Indian money and Silicon Valley's biggest names.",
    "slug": make_slug("upscale-ai-190-million-premji-invest-nvidia-diaspora-founders-networking"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-origin serial founders, backed by Azim Premji's investment arm and Nvidia, are building the AI networking layer in Palo Alto — a signal for NRI engineers weighing infrastructure startups and investors tracking cross-border Indian capital into frontier American tech.",
    "tags": ["upscale-ai", "ai-infrastructure", "premji-invest", "nvidia", "indian-american-founders", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters — Upscale AI valued at $2 billion after funding extension", "url": "https://www.reuters.com/technology/upscale-ai-valued-2-billion-after-funding-extension-2026-06-23/"},
        {"name": "Business Wire — Upscale AI Adds $190 Million to Series A", "url": "https://www.businesswire.com/news/home/20260622/en/Upscale-AI-Series-A-Extension"},
        {"name": "Network World — Upscale emerges from stealth with $100 million seed", "url": "https://www.networkworld.com/article/upscale-ai-stealth-networking.html"},
    ]),
    "score_total": 74,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4682189/pexels-photo-4682189.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Fiber-optic cables connecting switches in a data center network rack",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": body2,
}

# ============================================================
# ARTICLE 3 — India semiconductor mission beat: chip design talent
# ============================================================
body3 = """India keeps being told it cannot build leading-edge chips. Its government has decided to win a different race instead — the one for the people who design them.

Speaking at a Software Technology Parks of India event on June 20th, Ashwini Vaishnaw, the IT minister, framed a global shortage as an Indian opening. The semiconductor industry, worth about $800 billion today, is on track to pass $1 trillion within a year and will need roughly one million more workers by 2032, he said. "Filling this one million shortage is an opportunity for us." India, he added, is "ready to establish the world's best design facilities."

The pitch lands on a genuine strength. Indian engineers already make up around 20% of the world's semiconductor design workforce, and more than 100,000 VLSI design engineers work at global chip firms and domestic design houses. While the headlines chase fabs — Tata's plant at Dholera, Micron's packaging unit at Sanand — the quieter story is that India is positioning itself as the design brain of an industry it cannot yet manufacture at the cutting edge.

## Design over fabs

The government's own spending reflects the shift. Mint reported plans for ₹7,100 crore in fresh semiconductor incentives in FY27, layered on the ₹76,000 crore India Semiconductor Mission launched in 2021. HCL founder Ajai Chowdhry, a veteran of the sector, put it bluntly: the most promising move is the plan to support 30 chip-design companies. "India's strength lies in chip design. We have a large pool of VLSI talent, and if there is a strong focus on design, it could be a very effective strategy."

That is a realistic reading of where India can compete now. A leading-edge fab costs tens of billions and years to yield; Celesta's Arun Kumar Viswanathan, who sits on the mission's board, says even seasoned investors will not back full-scale fabs because of the capital required. Design, by contrast, plays to India's deep bench of engineers and its Design-Linked Incentive and Chips-to-Startup schemes — the programmes behind startups such as VerveSemi, AGNIT and Netrasemi, which represented India at a deep-tech showcase in France this month.

## What it means for the diaspora

For Indian-American semiconductor professionals — the engineers at Nvidia, Qualcomm, Intel, AMD, Micron and Texas Instruments who form one of the most concentrated diaspora cohorts in tech — this is more than national cheerleading.

First, it reshapes the career map. For years, the only way up in chip design ran through Silicon Valley, Austin or Portland. A credible Indian design ecosystem, backed by government money and global-standard facilities, creates a genuine return-to-India option for senior NRIs who want to lead rather than emigrate — or to run cross-border design teams without leaving the US.

Second, it is an investment thesis. Indian chip-design startups are still early, but the diaspora is uniquely placed to spot and back them: NRI angels and funds understand both the technology and the talent pool. The Bharat Innovates showcase and a string of design-startup fundraises signal a pipeline forming, even as India sensibly avoids the fab arms race.

Third, geopolitics. As Washington tightens chip-export controls and the US-China rivalry hardens, India is selling itself as the neutral, English-speaking, democratically aligned source of design talent. For Indian engineers caught between visa uncertainty in America and opportunity at home, that positioning matters — it could make Indian design centres a hedge rather than a consolation prize.

## The unglamorous bet

There is a temptation to dismiss "we'll do design, not manufacturing" as settling for the lower-margin slice. It is not. Fabless design is where companies like Nvidia and Qualcomm capture enormous value, and where India's comparative advantage — a million-strong, cost-competitive, English-fluent engineering base — is real and already proven inside foreign firms.

The risk is execution. India has announced grand chip ambitions before and watched fab deals collapse. Talent retention is hard when the same engineers can earn far more abroad; this month's run of founders relocating from Bengaluru to San Francisco is a reminder that capital alone does not keep people home. But for once the strategy fits the strength. India is not pretending it can out-fab Taiwan. It is betting it can out-design almost everyone — and that the diaspora, scattered across the world's chip companies, is its most underused asset in doing so."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Can't Out-Build Taiwan's Chip Fabs. So It's Betting It Can Out-Design Everyone.",
    "subheadline": "With Indians already 20% of the world's chip-design workforce, New Delhi is targeting a million-strong global talent shortage — and the diaspora is its most underused asset.",
    "slug": make_slug("india-semiconductor-chip-design-talent-vaishnaw-vlsi-diaspora-engineers"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India's pivot from fabs to chip design reshapes the career map for the huge cohort of NRI engineers at Nvidia, Qualcomm, Intel and Micron — creating return-to-India and investment options, and positioning India as a neutral design hub amid US-China chip tensions.",
    "tags": ["semiconductors", "india-semiconductor-mission", "chip-design", "vlsi", "ashwini-vaishnaw", "diaspora-engineers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Communications Today — India can fill semiconductor industry's one-million talent shortage", "url": "https://www.communicationstoday.co.in/india-can-fill-semiconductor-industrys-one-million-talent-shortage/"},
        {"name": "Mint — India plans semiconductor buildout with ₹7,100 crore incentives in FY27", "url": "https://www.livemint.com/industry/india-semiconductor-buildout-incentives-fy27.html"},
        {"name": "The Indian Eye — By 2032, India's semiconductor market to touch $100 billion", "url": "https://theindianeye.com/by-2032-indias-semiconductor-market-to-touch-100-billion/"},
    ]),
    "score_total": 72,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
    "image_caption": "Indian IT and Electronics Minister Ashwini Vaishnaw",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": body3,
}

articles = [art1, art2, art3]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
