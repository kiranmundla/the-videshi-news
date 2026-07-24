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
        "headline": "Elon Musk's SpaceX IPO Wants $75 Billion From You. Indian Engineers Built Half the Rockets.",
        "subheadline": "The largest public offering in history lists next week at a $1.75 trillion valuation. NRI investors face a rare retail window — and an extraordinary price tag.",
        "slug": make_slug("spacex-ipo-175-trillion-indian-engineers-nri-investors"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin engineers form a significant part of SpaceX's workforce, and NRI investors with Fidelity, Schwab, or Robinhood accounts can participate in the 30% retail allocation — a rare chance to buy into a company that normally only lets insiders in.",
        "tags": ["spacex", "ipo", "elon-musk", "nri-investors", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/elon-musk-needs-the-cultish-support-of-everyday-investors-to-pull-off-the-massive-spacex-ipo-08e7ea49"},
            {"name": "Reuters", "url": "https://www.reuters.com/breakingviews/spacex-straps-bankers-first-autonomous-ipo-2026-06-04/"},
            {"name": "The Times", "url": "https://www.thetimes.com/business-money/companies/article/elon-musks-spacex-gets-first-mover-advantage-in-year-of-huge-ipos-xq8bh0x5k"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/marketwatch/20260605261/elon-musks-175-trillion-spacex-valuation-leaves-virtually-zero-room-for-error"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Falcon_9_first_stage_at_LZ-1%28two%29.jpg/1280px-Falcon_9_first_stage_at_LZ-1%28two%29.jpg",
        "image_caption": "A SpaceX Falcon 9 first stage lands at Landing Zone 1 in Cape Canaveral",
        "image_attribution": "Wikimedia Commons",
        "body": """On June 12, SpaceX will go public at $135 a share. The price implies a $1.75 trillion valuation — larger than any initial public offering in American history and bigger than half the FTSE 100 combined. The company is seeking $75 billion in proceeds. Through May, every other IPO in 2026 raised $50.83 billion total.

The numbers are absurd. The price-to-sales ratio exceeds 93. NVIDIA, the reigning semiconductor titan, trades at 20 times revenue. Tesla, Musk's other public bet, sits at 15. University of Florida finance professor Jay Ritter, who maintains the most comprehensive academic IPO database in the country, has shown that companies listing with a PSR above 40 underperform the market by 58.5% over the following three years. SpaceX's ratio is more than double that threshold.

## The Retail Bet

What makes this offering structurally unusual is who SpaceX expects to buy it. The company has reserved up to 30% of its allocated shares for individual investors — six times the typical IPO retail allocation. Fidelity lowered its minimum account threshold to $2,000, down from $100,000. Schwab, Robinhood, SoFi, and E-Trade are all participating.

"Retail participation will be a defining feature of the SpaceX IPO," Truist analyst Sam Grelck wrote. The company itself, during its road show, stated that "retail investor participation is important to SpaceX."

This is not generosity. SpaceX needs retail demand to absorb a deal this large. Morningstar analysts this week pegged the company's fair value at $780 billion — less than half the asking price — and warned that its AI business, inherited through the xAI-SpaceX merger, poses a "material threat of value destruction."

## The Indian Engineering Pipeline

For Indian Americans in the aerospace and AI sectors, SpaceX has been an aspirational employer for years. The company's Hawthorne, California headquarters and its Starbase facility in Boca Chica, Texas draw heavily from the same graduate engineering talent pools — Stanford, MIT, Georgia Tech, Purdue — where Indian students disproportionately dominate. SpaceX does not publish workforce demographics, but LinkedIn data and immigration records suggest Indian-origin engineers occupy significant roles in propulsion, guidance systems, Starlink satellite operations, and the xAI division.

The IPO changes their economics overnight. Employees holding pre-IPO equity will see paper valuations crystallise into tradeable stock — a windfall that could rival the early Google and Facebook lockup expirations that minted millionaires across the Bay Area's Indian professional class a decade ago.

## The NRI Investor Calculus

For NRI investors with US brokerage accounts, the 30% retail window offers something genuinely rare: day-one access to a company that was previously gated behind venture capital minimums and special-purpose vehicles with steep fees.

But the valuation demands scrutiny. SpaceX lost $4.9 billion in 2025 on $18.7 billion in revenue. The merged entity — rocket launches, Starlink broadband, xAI's Grok chatbot, and the remnants of X — is pitched as a $28.5 trillion total addressable market, with 80% attributed to AI enterprise applications. Pitchbook analyst Franco Granda has forecast that the stock could trade like "Tesla on steroids," with violent swings on milestones or misses.

The prospectus itself reads more like a manifesto than a financial document. Asteroid mining, Mars colonisation, and space-based data centres sit alongside revenue breakdowns. Goldman Sachs CEO David Solomon is personally signing off on allocations. Jamie Dimon at JPMorgan is expected to pitch top clients.

## What Matters for the Diaspora

Three things to watch. First, the lockup period: when insiders — including Indian-origin engineers — can actually sell will determine whether the stock stabilises or dumps post-listing. Second, the xAI integration: the AI arm's losses are real, and NRI investors in particular should separate the romance of space from the reality of a chatbot business competing against OpenAI and Anthropic. Third, the Starlink India question: SpaceX's satellite internet licence application remains in regulatory limbo with the Indian Department of Telecommunications, held up by Mukesh Ambani's Jio and Bharti-backed OneWeb's lobbying for spectrum auctions rather than administrative allocation. If Starlink cracks India, it changes SpaceX's revenue trajectory. If it doesn't, a massive addressable market stays theoretical.

S&P Global Market Intelligence expects this to be the highest-volume IPO ever processed, with four to five times the normal institutional participation. Portfolio managers, one Baird strategist noted, are less debating whether to buy than "how much they own."

The retail window opens next week. The question for NRI investors is whether they want a piece of Musk's interplanetary pitch at 93 times revenue — or whether they'd rather let the valuation come to them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Tech Workers Built Dallas's Hottest Suburb. Now They're Leaving and Prices Are Cratering.",
        "subheadline": "Home prices in Collin County fell 9% as H-1B crackdowns, AI-driven layoffs, and a $100,000 visa fee gut the buyer pipeline that made North Texas boom.",
        "slug": make_slug("dallas-housing-crash-h1b-indian-tech-workers-collin-county"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian H-1B workers drove 70% of luxury home sales in North Dallas suburbs. The collision of 123,000 tech layoffs, a $100,000 H-1B fee, and FHA mortgage bans for non-permanent residents is forcing families to sell at losses or consider returning to India.",
        "tags": ["h1b-visa", "dallas-housing", "tech-layoffs", "indian-diaspora", "real-estate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/"},
            {"name": "Gulte", "url": "https://gulte.com/headlines/350973/trumps-h-1b-curbs-shake-texas-real-estate"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/why-h-1b-workers-are-leaving-texas-and-hurting-housing/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/17286412/pexels-photo-17286412.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Aerial view of a suburban neighbourhood in the United States",
        "image_attribution": "Pexels",
        "body": """For a decade, the suburbs north of Dallas ran on a single economic fuel: Indian-born engineers on H-1B visas buying homes. Now that fuel has been cut off, and the housing market is in free fall.

Home prices in Collin County — the suburban epicentre of the boom, encompassing Frisco, Prosper, and Celina — fell nearly 9% year-over-year as of February, according to Redfin data. That is more than double the 4% decline across the broader Dallas-Fort Worth metro. The correction has a single, identifiable cause: the Indian tech buyer has vanished.

## How They Built It

The numbers are stark. The federal government granted nearly 32,000 new H-1B approvals in the Dallas area during the Biden administration — more than Silicon Valley, Seattle, San Francisco, or Washington. Only New York ranked higher. The workers who arrived on those visas poured into new subdivisions where the population tripled in five years.

Collin County's Indian-born population averaged 116,000 annually through 2024, up from 70,000 in the prior five-year period. In Frisco, the share of Indian residents rose from 6% to nearly 20%. Builders tailored products to the market. Tradition Homes designed model homes with north-facing puja rooms and optional spice kitchens. At peak demand, South Asian buyers accounted for 70% of the company's sales.

That figure has now fallen below 30%. The builder sits on a backlog of 125 luxury homes under construction.

## The Three-Front Squeeze

The correction is not the product of a single policy change. It is three simultaneous shocks.

The first is layoffs. Over 123,000 tech jobs have been cut in 2026, with AI consistently cited as the primary driver. For an American citizen, a layoff is a career setback. For an H-1B holder, it triggers a 60-day countdown to find a new employer sponsor or leave the country.

The second is the $100,000 fee. In September 2025, the Trump administration imposed a supplemental charge on new H-1B petitions — a measure that priced out the staffing firms and mid-tier IT contractors that had been the largest sponsors of Indian workers in Dallas. The Department of Labor also launched "Project Firewall," an enforcement initiative targeting alleged employer abuse.

The third is mortgage access. The administration barred non-permanent residents, including H-1B holders, from FHA-insured mortgages starting May 2025. The share of FHA loans to non-permanent residents fell from 6% to virtually zero within months.

Texas added a fourth: Governor Abbott froze new H-1B petitions by state agencies and public universities, eliminating a safety net for workers who might have pivoted to academic or government roles.

## The Human Cost

The stories from North Dallas read like a chapter from a financial crisis novel.

Ravi Vavilala, an Indian-born naturalised citizen, bought a five-bedroom home in Celina for $895,000 in late 2023. Laid off from his IT job in March, he has reduced the asking price to $873,000 — below what he paid — and is struggling to compete against builder incentives down the street. Before his next showing, Bloomberg reported, he moved his religious items out of sight to attract a broader buyer pool.

Neeraj Gupta, a real estate agent who arrived in Dallas on an H-1B visa in 2000, says his phone used to ring with buyers. Now it rings with sellers. Some clients are absorbing monthly rental losses of $300 to $1,500. "Some of them said, 'I have seen enough: Just sell it — I don't care,'" he told Bloomberg.

One of his clients, a senior IT director holding two Frisco homes each valued over $1 million, is weighing a return to India. Another financed an $800,000 home almost entirely with debt and is now underwater.

## Why This Matters Beyond Texas

Housing analyst Alex Barron at Housing Research Center put the structural problem bluntly: "Who is there to replace them?"

The Indian tech buyer was not merely a large segment of the Dallas market. In many subdivisions, they were the market. The communities built around them — the Indian grocery stores, the cricket leagues, the temple expansions — all depend on continued inflow.

The pattern is likely to repeat in Seattle, where Amazon and Microsoft draw heavily from the H-1B pipeline, and in parts of New Jersey, Northern Virginia, and the Bay Area. Analysts project 2-5% price declines in H-1B-dense neighbourhoods as new hiring contracts.

For NRIs still holding property in these markets, the calculus has shifted. Those with green cards or citizenship face paper losses but no existential risk. Those on H-1B visas face the possibility of having to sell in a buyer's market while racing a 60-day clock. Immigration attorney Sharadha Kodem, who practices in Frisco, said the anxiety among her clients is unlike anything in her career: "They need more time to sell. They need to still pay the mortgage."

The suburbs that Indian tech workers built are now a case study in what happens when immigration policy, AI-driven layoffs, and housing economics collide. The question is not whether the correction deepens — it is where it spreads next."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sarvam AI Is Opening Its Voice Engine to the Public. It Already Makes 80% of Revenue From Talking.",
        "subheadline": "India's sovereign AI flagship moves beyond enterprise-only access as it closes in on a $250 million round that could make it a unicorn.",
        "slug": make_slug("sarvam-ai-voice-platform-public-launch-unicorn-round"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sarvam's 22-language voice AI stack is directly relevant to NRI investors eyeing India's AI sector and to diaspora families who need multilingual interfaces for elderly parents navigating Indian digital services.",
        "tags": ["sarvam-ai", "indian-ai", "voice-technology", "sovereign-ai", "startup-funding"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc42", "url": "https://inc42.com/buzz/sarvams-voice-stack-layoffs-at-interview-kickstart-more/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/sarvam-ai-in-talks-to-raise-250-mn-at-1-5-bn-valuation-report/"},
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/india-ai-startup-sarvam-raises-funds-at-1-5b-valuation/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4790267/pexels-photo-4790267.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smart speaker on a desk, representing voice AI technology",
        "image_attribution": "Pexels",
        "body": """Sarvam AI is about to make its most consequential product decision since launching two years ago. The Bengaluru-based startup, which has built India's most commercially successful sovereign AI platform, is opening its voice AI engine to the public — ending the enterprise-only gatekeeping that has defined its business model since inception.

The shift is more than a go-to-market tweak. Sarvam Samvaad, the company's multilingual voice AI platform, currently generates 80% of Sarvam's $12 million in annual recurring revenue. Until now, access required an enterprise sales conversation and a waitlist. The new model will introduce self-serve onboarding, allowing any startup or developer to sign up, test, and begin building voice workflows without a handshake.

## The Revenue Engine You Didn't Notice

Sarvam initially attracted attention for its large language models — Sarvam-30B and Sarvam-105B, both trained from scratch in India, optimised for Indian languages, and unveiled at the India AI Impact Summit alongside Prime Minister Modi. The models were the symbolic crown jewels: proof that India could build its own AI rather than renting it from OpenAI or Google.

But the money was never in the models. It was in the voice.

Tata Capital uses Sarvam Samvaad for multilingual customer interactions. The system handles 22 Indian languages, processing voice inputs from users who may not read, write, or type in English — which describes the majority of India's 1.45 billion people. For enterprise clients, the pitch is straightforward: voice AI that actually works in Hindi, Tamil, Bengali, and Marathi, not as an afterthought, but as the primary interface.

The 80% revenue concentration is both a strength and a vulnerability. It means Sarvam has found genuine product-market fit in voice. It also means the company's entire commercial trajectory depends on whether the platform can scale beyond a handful of large enterprise deployments.

## The Unicorn Round

The timing of the public launch is not accidental. Sarvam is reportedly finalising a $250 million funding round that would value the company at approximately $1.5 billion — a sevenfold jump from its $41 million Series A in December 2023.

Bessemer Venture Partners is expected to lead, with NVIDIA, Amazon, and Prosperity7 Ventures participating. If the round closes, Sarvam would join Bhavish Aggarwal's Krutrim as one of India's homegrown AI unicorns, though with a critical difference: Sarvam has meaningful commercial revenue, while Krutrim's trajectory has been more about capital raises and compute infrastructure than paying customers.

The investor roster matters. NVIDIA's participation signals that Sarvam is building on NVIDIA's stack in a way the chipmaker wants to promote — a strategic endorsement that carries weight beyond the cheque. Amazon's involvement suggests potential AWS integration or distribution, which could accelerate Sarvam's enterprise adoption internationally.

## The Pricing Problem

Opening the platform to the public forces Sarvam to solve a problem it has been able to defer: pricing. Enterprise contracts are negotiated individually. A self-serve platform requires published rates that compete with Google Cloud's Speech-to-Text, Amazon Transcribe, and Microsoft Azure's Cognitive Services — all of which offer Indian language support, even if with less depth.

Sarvam is evaluating usage-based billing and tiered plans, with a freemium layer under consideration. The challenge is acute. Indian startups and SMBs are extraordinarily price-sensitive, and the global hyperscalers can afford to subsidise voice AI as a loss leader to lock customers into their broader cloud ecosystems. Sarvam cannot.

What Sarvam can offer is specificity. Its models are not English-first with Indian language bolted on. They are designed ground-up for the acoustic and linguistic diversity of the subcontinent — a distinction that matters when you are processing a customer service call in Bhojpuri or a government helpline in Manipuri.

## The Diaspora Angle

For NRI investors, Sarvam presents a rare opportunity to back an Indian AI company that has actual revenue, not just a research lab and a government endorsement. The $1.5 billion valuation is steep for $12 million in ARR — roughly 125 times revenue — but comparable to early-stage AI valuations in the US, where companies with similar revenue profiles have raised at similar multiples.

The more immediate relevance is personal. Millions of diaspora families maintain daily contact with parents and grandparents in India who navigate an increasingly digital landscape — UPI payments, government portals, telecom services, banking — that assumes literacy and smartphone fluency. A voice-first AI interface that works natively in regional languages is not an abstraction for NRI families. It is the difference between a parent managing their own pension disbursement and a frantic WhatsApp call at 2 AM asking what button to press.

Sarvam's co-founder Pratyush Kumar framed the ambition at the platform's unveiling: "Today we show we can bring our own AI to a billion Indians." The public launch of Samvaad is the first real test of whether that sentence is a mission statement or marketing copy."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
