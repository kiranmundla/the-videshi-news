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
        "headline": "Qualcomm Wants to Buy Its Way Out of the Phone. The $10 Billion Target Is Jim Keller's Chip Startup.",
        "subheadline": "Qualcomm is in talks to acquire Tenstorrent for as much as $10 billion — a bet on RISC-V silicon and one of the industry's most coveted engineers, days before its make-or-break AI investor day.",
        "slug": make_slug("qualcomm-tenstorrent-jim-keller-10-billion-risc-v-ai-data-center"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Qualcomm employs thousands of Indian engineers across San Diego, Bengaluru and Hyderabad — a pivot from saturating smartphones to data-center AI silicon reshapes the career ladder and stock options for Indian chip professionals on both sides of the ocean.",
        "tags": ["semiconductors", "qualcomm", "ai-chips", "jim-keller", "indian-tech", "data-center"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-stock-price-ai-chip"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-talks-buy-tenstorrent-information-reports-2026-06-15/"},
            {"name": "The Information (via Finimize)", "url": "https://www.finimize.com/content/qualcomm-talks-to-buy-tenstorrent-for-up-to-10-billion"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Jim_Keller_%28engineer%29.jpg",
        "image_caption": "Tenstorrent CEO Jim Keller, the chip architect behind AMD's Zen and Apple's A-series, is the prize in Qualcomm's reported acquisition talks.",
        "image_attribution": "Wikimedia Commons",
        "body": """Qualcomm has spent four decades getting rich off the inside of your phone. Now it wants out — and it is willing to pay up to $10 billion to get there.

The chipmaker is in talks to acquire Tenstorrent, the AI-chip startup run by the celebrated engineer Jim Keller, for somewhere between $8 billion and $10 billion, *The Information* reported on Monday. Reuters confirmed the talks but cautioned that terms could shift or the deal could collapse. Qualcomm shares, which have run up 68% over the past three months, jumped another 3.3% in Tuesday premarket trading to about $228.

The timing is not an accident. Qualcomm holds its investor day on June 24, where it is expected to unveil the customer for a custom data-center chip and lay out targets that analysts at J.P. Morgan think could reach $3 billion in data-center revenue by fiscal 2027 and a striking $35 billion by 2031. A Tenstorrent deal would give that pitch a spine.

## Why Tenstorrent, and why now

Tenstorrent designs AI accelerators built on the open RISC-V architecture — chips that can both train models and run them in production. For Qualcomm, which has leaned on Arm-based designs, RISC-V offers a path to reduce its dependence on a licensor it has spent years fighting in court. But the bigger prize may simply be the man at the top.

Jim Keller is the closest thing the semiconductor industry has to a rock star. He helped create Apple's A4 and A5 processors, the Zen architecture that resurrected AMD, and Tesla's self-driving silicon. Acquirers do not pay $10 billion for a startup valued at $3.2 billion last November because of its order book. They pay for the architect and the team he assembled.

## The Indian engineer's stake in this

For the tens of thousands of Indian-origin engineers inside Qualcomm — in San Diego, in Bengaluru, in Hyderabad — this is more than M&A theater. Qualcomm's India operations are among its largest outside the United States, and the company's smartphone-modem business has been the bread and butter of those careers. A decisive shift toward AI data-center silicon redraws which teams get headcount, which get budget, and which get quietly wound down.

It also reshapes the calculus for the H-1B and L-1 engineers who joined Qualcomm betting on mobile. Data-center AI is where the hiring and the stock-price upside now live; mobile is the mature business funding the gamble. An engineer who spent a decade optimizing power on a Snapdragon modem may find the growth ladder has moved to a different building.

## A milestone-payment minefield

The structure matters as much as the headline number. Analysts flagged that the $8–10 billion could include performance-based milestone payments — money paid only if Tenstorrent's technology hits specific targets. That protects Qualcomm if RISC-V silicon takes longer to mature than promised, but it introduces years of messy accounting and headline risk. Qualcomm's brief 1% after-hours dip when the talks first surfaced looked like a classic deal-risk discount: the market wants to see the final structure before it cheers.

There is also competition lurking. Intel was reported in May to be circling Tenstorrent too, hunting for a credible AI story after its Gaudi chips disappointed. For Intel, whose own Indian-American CEO Lip-Bu Tan is mid-turnaround, losing Keller to Qualcomm would sting.

## What's next

Watch June 24. If Qualcomm walks onto its investor-day stage with Tenstorrent in the bag and a named hyperscale customer, the data-center pivot stops being a slide deck and becomes a strategy. If the talks slip, the company will have to convince Wall Street it can build that future organically — a far harder sell in a market where Nvidia already owns the AI compute conversation.

For Indian chip professionals tracking where the next decade of opportunity sits, the message from Qualcomm is blunt: the phone paid for the past. The data center is the future, and the company is shopping for it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forbes Counted America's Most Successful Immigrants. 26 of the Top 250 Are Indian.",
        "subheadline": "As the United States turns 250, Forbes' new ranking reads like a roll call of the diaspora — from four Big Tech CEOs to the venture capitalists quietly funding the next generation.",
        "slug": make_slug("forbes-2026-top-immigrants-26-indian-origin-leaders-diaspora"),
        "category": "technology",
        "vertical": "diaspora",
        "diaspora_angle": "For every Indian American watching their kids choose between an engineering degree and a startup, the Forbes list is proof of a ceiling that no longer exists — and a map of who in the community now controls capital, code, and corporate boards.",
        "tags": ["indian-diaspora", "forbes", "tech-leaders", "immigration", "nri", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India-West News", "url": "https://www.indiawest.com/news/forbes-2026-honors-26-indian-origin-leaders"},
            {"name": "Times Now World", "url": "https://www.timesnowworld.com/world/americas-top-immigrant-achievers-26-leaders-of-indian-descent"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai, one of 26 Indian-origin leaders named on Forbes' 2026 list of America's most successful immigrants.",
        "image_attribution": "Wikimedia Commons",
        "body": """Lists like this one usually invite a tired round of pride-posting on the diaspora WhatsApp groups. This one is worth reading more carefully.

Forbes has released its 2026 ranking of the 250 most successful living immigrants in the United States, timed to the country's approaching 250th anniversary. Twenty-six of them are of Indian origin — roughly one in ten — and the names span far more than the usual Big Tech quartet.

## The familiar faces, and the less familiar ones

Yes, the CEOs are all there: Satya Nadella at Microsoft, Sundar Pichai at Alphabet and Google, Arvind Krishna at IBM, Shantanu Narayen at Adobe. Nikesh Arora of Palo Alto Networks and Micron's Sanjay Mehrotra round out the operators running multibillion-dollar companies.

But the more telling entries are the ones that do not run a household-name firm. Vinod Khosla and Kavitark Ram Shriram, two of Silicon Valley's most consequential venture capitalists. Hemant Taneja, who runs General Catalyst. Naval Ravikant, the AngelList co-founder whose tweets have shaped a generation of founders. Jyoti Bansal, a serial software entrepreneur. Neha Narkhede, who co-created the data infrastructure that quietly powers much of the modern internet. Cybersecurity billionaire Jay Chaudhry of Zscaler. Nobel laureate economist Abhijit Banerjee. Toast co-founder Aman Narang. Clean-energy pioneer K.R. Sridhar of Bloom Energy.

In other words, the diaspora's influence has moved past the executive suite and into the layer that decides which companies get built at all — the capital, the boards, the infrastructure. The list also reaches well beyond software: investor Rajiv Jain, medical-technology executive David Paul, aviation entrepreneur Rakesh Gangwal, semiconductor leader Jitendra Mohan, and author and television personality Padma Lakshmi all feature, alongside former PepsiCo chief Indra Nooyi, who now sits on some of corporate America's most powerful boards.

## Why this matters beyond the bragging rights

For Indian American families, the practical signal is the one worth absorbing. A generation ago, the immigrant story in tech was about getting *in* — landing the H-1B, surviving the green-card queue, climbing to a director title. The Forbes roster says the ceiling that once defined that story has, for a meaningful cohort, simply dissolved.

That has knock-on effects most lists ignore. When Khosla, Shriram and Taneja control where venture dollars flow, founders from the community get a warmer first meeting. When Ravikant and Bansal mentor the next wave, the network compounds. The "diaspora network that pulls generations up" — the phrase critics use dismissively — is, in capital terms, real and quantifiable.

## The uncomfortable footnote

The timing lands awkwardly against the immigration backdrop. The same week the list circulated, a federal judge struck down the Trump administration's $100,000 H-1B application fee, ruling that only Congress can levy such a tax. The weighted-wage lottery and expanded consular vetting remain. The community celebrating 26 names at the top of American business is the same community whose newest arrivals face the steepest entry barriers in decades.

There is a tension there that the diaspora rarely says out loud: the leaders on this list mostly arrived in an era of comparatively open doors. The engineer landing at SFO this year on a freshly scrutinized visa is not walking the same path Nadella or Pichai did.

## What's next

Forbes notes the list "keeps growing" — Leena Nair at Chanel, Jayshree Ullal at Arista, P&G's incoming CEO Shailesh Jejurikar are all cited as the next tier. The HSBC Hurun count put 226 Indian-origin leaders across 200 companies, commanding $10 trillion in value.

For NRIs, the honest takeaway is two-sided. The success is undeniable and self-reinforcing. But a roll call of who made it is not a guarantee that the door stays open for who comes next — and that, more than the trophy list, is the conversation the community should be having."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest Nvidia GPU Operator Is Going Public. For NRI Investors, It's the First Pure AI-Infrastructure Bet at Home.",
        "subheadline": "Yotta Data Services is lining up a Mumbai IPO at a valuation of up to $6 billion, just as a $2.34 billion US partnership validates India's claim to be the next AI-compute hub.",
        "slug": make_slug("yotta-data-services-ipo-nvidia-gpu-india-ai-infrastructure-nri"),
        "category": "technology",
        "vertical": "economy",
        "diaspora_angle": "NRIs have long invested back home through Indian mutual funds and real estate; Yotta's listing offers the first liquid, public way to own a slice of India's AI-compute boom — the same buildout US hyperscalers are pouring $100 billion-plus into.",
        "tags": ["india-tech", "data-center", "ipo", "ai-infrastructure", "nri-investing", "nvidia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/yotta-data-said-to-hire-advisors-for-900-million-india-ipo/article.ece"},
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/tachyon9-yotta-nidar-nakota-ai-data-campus"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-supplier-jabil-adani-partner-build-ai-data-center-india-2026-06-15/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks inside a hyperscale data center — the kind of AI-compute infrastructure Yotta operates at scale across India.",
        "image_attribution": "Pexels",
        "body": """For years, the standard advice to an NRI who wanted to bet on India's tech story was frustratingly indirect: buy an Indian IT-services stock, or a mutual fund, and hope the rising tide lifted your boat. There was no clean way to own the actual machinery of the AI boom. That is about to change.

Yotta Data Services — the operator that runs India's largest cluster of Nvidia AI processors — is preparing an initial public offering in Mumbai that could raise as much as $900 million, with CEO Sunil Gupta targeting a valuation of up to $6 billion. The company has engaged ICICI Securities and SBI Capital Markets, with a draft prospectus expected within months and a listing pencilled in for the final quarter of the year. A pre-IPO round of up to $300 million is also on the table.

## The validation came this week

If anyone doubted the demand underneath that valuation, a US deal landed to settle the question. Tachyon9 Corporation signed a 15-year memorandum of understanding worth roughly $2.34 billion with Yotta's parent, Nidar Infrastructure, to anchor the Nakota AI Data Campus — a project designed to scale to one gigawatt of capacity. American capital is now writing multibillion-dollar checks against Indian AI infrastructure operators specifically.

That sits inside a much larger wave. The same week, Apple supplier Jabil and Adani announced a strategic alliance to build gigawatt-scale AI-rack manufacturing in India. Reliance is building a 168-MW data center in Jamnagar leased to Meta. CBRE expects Indian data-center investment to top $100 billion by 2027, helped by a government tax break of more than 20 years on local data-center use.

## Why an NRI should care

The diaspora's relationship with investing back home has always been emotional as much as financial — property in the hometown, a few lakh in a cousin's startup, an Indian equity fund tucked inside an NRE account. What has been missing is a way to own the infrastructure layer of India's most important industrial story: the compute that every Indian AI startup, bank and government service will rent.

Yotta's IPO would be the first reasonably liquid, public-market vehicle for exactly that. An NRI in New Jersey or the Bay Area who believes India becomes a genuine AI-compute hub no longer has to express that view through a diversified fund. They can — once it lists — own the picks-and-shovels operator directly.

## The cautions worth stating plainly

Enthusiasm should not outrun arithmetic. Data-center economics are capital-devouring: power, land, cooling, and Nvidia GPUs that cost a fortune and depreciate fast. A $6 billion valuation on an infrastructure operator prices in years of flawless execution and continued AI demand. The global chip selloff in early June — $1.3 trillion erased from semiconductor stocks in a single brutal week — was a reminder of how quickly sentiment on anything AI-adjacent can reverse.

There are also access frictions specific to NRIs: investing in an Indian IPO requires the right account structure, and tax treatment of Indian capital gains for non-residents is its own thicket. The fine print matters more here than in a routine fund purchase.

## What's next

Watch for Yotta's draft prospectus, which will be the first time outsiders see the real numbers — utilization rates, contract durations, and how much of that headline capacity is actually leased versus aspirational. The Tachyon9 MOU is a strong signal, but an MOU is not revenue.

For the diaspora, the broader point stands regardless of how Yotta's specific listing performs. India is being wired as an AI-compute economy, US money is co-signing the bet, and for the first time the public markets back home will let NRIs participate in the buildout directly rather than from the sidelines."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
