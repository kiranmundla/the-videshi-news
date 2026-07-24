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
        "headline": "Accenture Just Had Its Worst Week on Record. The Fear Driving It Lands Hardest on Indian IT.",
        "subheadline": "A cautious outlook and shrinking bookings wiped a quarter off Accenture's value. Wall Street is now treating the whole IT-services model — TCS, Infosys and Wipro included — as a thing AI might eat.",
        "slug": make_slug("accenture-worst-week-ai-fears-it-services-tcs-infosys-wipro-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the Indian engineer at a US IT-services firm and the NRI holding TCS or Infosys shares, Accenture's selloff is the clearest signal yet that AI is being priced as a threat to the entire outsourcing model, not a tailwind.",
        "tags": ["accenture", "indian-it", "ai", "tcs-infosys-wipro", "h1b", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/22/wall-street-sold-off-it-services-stocks-ai-fears/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/accenture-stock-downgrade-worst-week"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/accenture-stock-fiscal-q3-2026-earnings/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/no-near-term-recovery-it-sector-accenture-kotak/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg/1280px-Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg",
        "image_caption": "Accenture's office complex in Gachibowli, Hyderabad, one of its largest delivery hubs in India",
        "image_attribution": "Wikimedia Commons",
        "body": """Accenture shares fell about 18% on June 18, the consulting giant's worst single-day drop on record, and ended the week down nearly a quarter — its worst week ever. The striking part is what did *not* cause it. The fiscal third quarter, the period that ended May 31, was solid: revenue rose 6% to $18.7 billion and earnings per share climbed 9%.

What spooked investors was the outlook, and the fear underneath it.

## A quarter that was fine, a future that isn't

Management trimmed full-year revenue growth guidance to 3-4% in local currency, down from 3-5%, citing weakness in its US federal government business. More alarming was bookings — the measure of future work — which fell 3% to $19.3 billion against analyst hopes for 7% growth. Accenture also quietly said it will no longer break out its artificial-intelligence bookings, the metric it had spent two years showcasing.

Chief executive Julie Sweet blamed part of the softness on the conflict in the Middle East, which she said cost roughly $100 million in third-quarter revenue and $400 million in bookings as clients slowed decisions. She insisted AI "will be a tailwind for us and our industry as it scales."

The market is not convinced. At around $124, Accenture trades at roughly ten times earnings and less than half its 52-week high. TD Cowen's Bryan Bergin, long a bull, downgraded the stock to Hold and slashed his target from $258 to $150, writing that "our call for durability before potential recovery was wrong." The contagion was immediate: EPAM Systems slid about 9% the same day without reporting anything of its own.

## Why this is an Indian story

Accenture is, in headcount terms, substantially an Indian company. Hundreds of thousands of its people sit in Bengaluru, Hyderabad, Chennai and Pune, and its single largest concentration of employees is in India. When Wall Street reprices Accenture, it is repricing the labour-arbitrage model that built the careers of millions of Indian engineers — the model TCS, Infosys, Wipro, HCLTech, Tech Mahindra and Cognizant all run.

That is precisely why brokerage Kotak read Accenture's results as a warning for Indian IT. The firm flagged a "sharp year-on-year decline in managed services bookings" and noted Accenture's book-to-bill in that segment fell below 1x — meaning it is signing less new work than it is burning through. Kotak's verdict: continued demand uncertainty and "no immediate signs of a broad-based recovery in discretionary technology spending." For investors who treat Accenture as the leading indicator before Indian IT reports its own quarter, that is not a comforting tell.

The deeper anxiety is structural. The bear case is not that clients are spending less this year; it is that generative AI is starting to do the very work — code migration, testing, application maintenance, business-process drudgery — that armies of offshore engineers are paid to do. If a model can do in hours what a team did in weeks, the billable hour shrinks, and so does the headcount it supports.

## What it means in New Jersey and the Bay Area

For an Indian professional on an H-1B or L-1 at a US IT-services firm, the signal matters more than the stock price. Bookings are a leading indicator of staffing: when book-to-bill drops below 1x, hiring freezes and bench reductions tend to follow, and for a visa holder a layoff starts a 60-day clock to find a new sponsor or leave the country. The firms most exposed to commoditised application work are exactly the ones where Indian visa workers are most concentrated.

For NRI investors, the read is more nuanced. The bulls — including a Seeking Alpha "Strong Buy" and RBC's call for a fiscal-2027 recovery — argue the selloff is overdone, that a 15% free-cash-flow yield prices in disaster that may not arrive, and that AI-driven productivity could eventually *expand* services demand as enterprises rebuild their software estates. Accenture is leaning into that thesis with $4.2 billion of cybersecurity acquisitions (Dragos, runZero, NetRise) and partnerships with Palantir and Databricks.

The honest answer is that nobody yet knows whether AI shrinks the IT-services pie or reshapes it. What this week settled is the question investors are now asking. For a diaspora whose prosperity has been built, in large part, on selling technology services to Western companies, it is the only question that matters."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tesla Now Has Five Showrooms in India and Almost No Sales. The Real Test Starts This Summer.",
        "subheadline": "Hyderabad and Bengaluru just joined Mumbai and Delhi on Tesla's India map. But 100% import duties mean a Model Y costs nearly $70,000 — and only 350 have sold.",
        "slug": make_slug("tesla-india-expansion-hyderabad-bengaluru-model-y-import-duty-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who own Tesla stock or are eyeing a move back to India get a live case study in whether a premium American brand can crack a price-obsessed market choked by import tariffs.",
        "tags": ["tesla", "ev", "india", "model-y", "elon-musk", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NamasteCar", "url": "https://namastecar.com/tesla-hyderabad-experience-center-model-y/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/tesla-launches-six-seater-model-y-india/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/tesla-india-first-showroom-mumbai-bkc/"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/indias-first-tesla-cybertruck-imported-from-dubai/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Tesla_Model_Y_%282025%29_DSC_8297.jpg/1280px-Tesla_Model_Y_%282025%29_DSC_8297.jpg",
        "image_caption": "The 2026 Tesla Model Y, the company's lead model for the Indian market",
        "image_attribution": "Wikimedia Commons",
        "body": """Tesla has just opened an Experience Center in HITEC City, Hyderabad, adding the southern tech capital to a footprint that now spans Mumbai's Bandra Kurla Complex, Delhi's Aerocity, a Gurugram service center and a Bengaluru showroom in Whitefield. For a company that took nine years to put a single store on Indian soil, five locations in under a year looks like momentum.

The sales figures tell a humbler story.

## 350 cars, and counting slowly

Since deliveries began last September, Tesla has sold roughly 350 Model Ys in India — a rounding error in the world's third-largest car market, where nearly six million vehicles are produced annually. Rivals BYD, Mercedes-Benz and BMW have comfortably outsold it over the same stretch.

The reason is no mystery: price. India levies a 100% import duty on fully-built cars, a tariff Elon Musk has complained about for years. The result is that a Model Y rear-wheel-drive lists at about ₹59.9 lakh (roughly $68,000), and the long-range version closer to ₹67.9 lakh ($79,000), with a full self-driving add-on at another ₹6 lakh. In a market where most cars sell for under $22,000, Tesla is not competing for the mass buyer. It is competing for the same sliver of wealthy households that buy German luxury saloons.

Tesla's response is the Model Y L — a longer, three-row, six-seat variant with a claimed 681 km range, priced from ₹61.99 lakh, with deliveries from July. Senior director Isabel Fan said at the Mumbai launch that the company "continues to work on affordability." The pitch is shrewdly aimed at Indian family-buying habits, which increasingly favour three-row SUVs. Buyers who order before June 30 get a complimentary Wall Connector home charger — a nudge that doubles as an admission that charging anxiety, not just price, is the barrier.

## The build-out beneath the badges

What is more revealing than the showrooms is the plumbing. Tesla has committed to charging stations across Mumbai and Delhi, is offering home-charging support in every Indian state, and has spread service infrastructure to Hyderabad and Bengaluru. India's broader EV adoption remains thin — dominated by two- and three-wheelers — but the government wants 30% of new vehicle sales to be electric by 2030, and Tesla is positioning for that curve rather than today's demand.

The company has also hinted at a workaround for the tariff wall: importing cars from its Berlin gigafactory once an India-EU free-trade agreement is signed, which could lower landed costs versus China-sourced units. A genuinely affordable, locally relevant Tesla, however, still depends on local assembly — and Musk has so far refused to commit to an Indian factory without tariff relief, the same standoff that has defined the relationship for a decade. Meanwhile, India's first Cybertruck has already arrived in Gujarat, privately imported from Dubai by a businessman, underscoring that the appetite for the brand runs well ahead of the price points Tesla can offer.

## Why the diaspora is watching

For the NRI investor, India is the most-watched blank space on Tesla's growth map. The bull case has always assumed the company eventually unlocks the planet's largest untapped car market; the bear case is that 100% tariffs and a $22,000 median price make that math impossible without a local plant Tesla won't build. The next two quarters of Model Y L deliveries are the first real data point.

For the returning NRI — the engineer weighing a move from Sunnyvale to Bengaluru, or the executive relocating to Hyderabad — Tesla's expansion is a quality-of-life signal. The Experience Centers are clustered precisely in the cities where the diaspora congregates, and the charging build-out tracks the neighbourhoods they tend to settle in. Owning the car they drove in California is suddenly possible at home, if at a steep premium.

The honest verdict is that Tesla's India play is still a flag-planting exercise, not a business. Five showrooms and 350 cars is the definition of building ahead of demand. Whether that demand arrives depends less on Musk's showrooms than on a tariff negotiation in New Delhi — and on whether the world's most price-sensitive car market decides a Tesla is worth twice what an Indian would pay for almost anything else on four wheels."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Adobe's Indian-Born CEO Spent 18 Years Building a Subscription Empire. On His Way Out, He's Tearing Up the Playbook.",
        "subheadline": "Shantanu Narayen is leaving Adobe with a parting bet: give the AI tools away free, monetise later. Wall Street isn't sure his successor can pull it off.",
        "slug": make_slug("adobe-shantanu-narayen-freemium-ai-firefly-cfo-exit-succession-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Narayen is one of the original Indian-origin CEOs who made Silicon Valley's executive suite look like Hyderabad; how his AI-era succession plays out is a referendum on whether that generation's playbook survives the agentic shift.",
        "tags": ["adobe", "shantanu-narayen", "firefly", "ai", "indian-origin-ceo", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/22/this-software-stock-could-soar-74-percent-adobe/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/adobe-ceo-shantanu-narayen-step-down/"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/five-takeaways-shantanu-narayen-final-adobe-summit-keynote/"},
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/adobe-shantanu-narayen-transition-ceo"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Shantanu Narayen, the outgoing chief executive of Adobe Inc.",
        "image_attribution": "Wikimedia Commons",
        "body": """Shantanu Narayen built one of the great second acts in software. When he took over Adobe in 2007, it sold boxed copies of Photoshop. He turned it into a cloud-subscription machine that prints recurring revenue, created the "digital experience" category, and made Adobe one of the most reliable compounders in tech. He is also one of the founding members of a now-familiar club: the Indian-born executives — alongside Satya Nadella, Sundar Pichai, Arvind Krishna and Sanjay Mehrotra — who run America's largest technology companies.

Now, on his way out, he is dismantling the very model he is famous for.

## The freemium gamble

Narayen announced earlier this year that he will step down once the board names a successor, staying on as chair. The search, led by lead independent director Frank Calderoni, is expected to take months and weigh both internal and external candidates. The timing is awkward: alongside the company's second-quarter results, CFO Dan Durn announced his own departure, effective June 15, leaving Adobe with two of its top seats in flux at once.

Into that uncertainty Narayen has dropped a strategic grenade. On the Q2 earnings call he argued that "AI-first applications that will serve broader audiences need to provide free, intuitive onboarding that drives usage and monetization through paywalls." Translated: Adobe will give its AI tools away to win users at scale, then charge once they are hooked — a freemium land-grab, not the premium-from-day-one subscription model that built the company.

The market flinched. J.P. Morgan cut its price target from $420 to $340, warning the pivot creates "short-term annual-recurring-revenue headwinds" even if it positions Adobe for long-term upside. The stock has slid this year to around $195, less than half some bullish targets, as investors weigh a genuine question: is Adobe disrupting itself before someone else does, or admitting that free AI image and video tools have already commoditised the work Photoshop used to own?

## A real AI story, and a real threat

The case for Narayen's bet is that Adobe's AI traction is not hype. Annual recurring revenue from its AI-first offerings more than tripled year-over-year; consumption of generative-AI credits grew 45% quarter-over-quarter; video generation use rose eightfold and audio doubled. At his final Adobe Summit keynote, Narayen unveiled "Adobe CX Enterprise," pitching a shift from generative AI to *agentic* AI — software that doesn't just make content but executes multi-step marketing work, plugged into an Experience Platform that already processes 35 trillion segment evaluations a day.

The threat is equally real. Free or near-free image and video generators from OpenAI, Google and a swarm of startups have eroded the moat around Adobe's creative tools and dented its stock-image business. The next CEO inherits a company analysts call fundamentally strong but entering "a more complex phase of execution" — one where the challenge is no longer transformation but proving the AI strategy delivers durable growth.

## Why the diaspora has a stake

For Indian Americans, Narayen's exit is more than a corporate-governance story. He belongs to the generation of Hyderabad- and Manipal-trained engineers who quietly rewrote what an American tech CEO looks like — and whose presence at the top has been a source of both pride and aspiration for a community that ships tens of thousands of engineers to Silicon Valley each year. How cleanly Adobe hands off, and whether the board reaches again for that mold, will be read as a signal about the staying power of the playbook these leaders wrote.

There is a more concrete angle, too. Adobe employs thousands of engineers in Bengaluru and Noida, and its Firefly and Experience Platform work runs heavily through those India centers; a strategy reset of this scale reshapes roadmaps — and headcount — for the diaspora's counterparts back home. And for NRI investors holding ADBE, the stock now sits at a genuine fork: either the freemium pivot reaccelerates growth and the shares re-rate sharply, or the AI commoditisation thesis wins and a former compounder becomes a value trap.

Narayen spent eighteen years proving that selling software by subscription was the future. His last act is a bet that the future has already moved on — and he is handing the proof to someone else."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
