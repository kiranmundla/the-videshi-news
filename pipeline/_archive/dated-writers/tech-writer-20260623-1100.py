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
        "headline": "India Just Approved Its First Silicon-Carbide Fab. The Map of Where Chips Get Made Is Quietly Shifting East.",
        "subheadline": "Four new projects in Odisha, Punjab and Andhra take India's chip mission to 10 plants and Rs 1.6 lakh crore. For diaspora engineers, the question is whether the jobs follow the press releases.",
        "slug": make_slug("india-silicon-carbide-fab-odisha-semiconductor-mission"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian-American chip engineers weighing a move home, the spread of fabs beyond Gujarat into Odisha, Punjab and Andhra is the first sign the semiconductor mission might create real careers, not just ribbon-cuttings.",
        "tags": ["semiconductor", "india-semiconductor-mission", "indian-tech", "chips", "odisha"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Prime Minister of India (PIB)", "url": "https://www.pmindia.gov.in/en/news_updates/cabinet-approves-semiconductor-manufacturing-units-in-odisha-punjab-and-andhra-pradesh/"},
            {"name": "Dataquest India", "url": "https://www.dqindia.com/news/cabinet-approves-semiconductor-manufacturing-units-in-odisha-punjab-and-andhra-pradesh/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indias-semiconductor-push-gains-momentum-as-odisha-signs-chip-technology-mou-with-intel-3dgs/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/200mm_Wafer_Fertigungslinie.JPG/1280px-200mm_Wafer_Fertigungslinie.JPG",
        "image_caption": "A 200mm semiconductor wafer fabrication line, the kind of facility India is now building across multiple states",
        "image_attribution": "Wikimedia Commons",
        "body": """The headlines out of Delhi this week carried a familiar rhythm: another Cabinet meeting, another round of semiconductor approvals, another round number for the cumulative investment. But buried in the boilerplate was something genuinely new. One of the four projects the Union Cabinet cleared will build India's first commercial compound-semiconductor fab — and it sits not in Gujarat, the state that has anchored the chip story so far, but in Odisha.

## What was actually approved

The Cabinet, chaired by Prime Minister Narendra Modi, signed off on four projects worth roughly Rs 4,600 crore, expected to create about 2,034 direct skilled jobs. That brings the India Semiconductor Mission to 10 approved projects across six states, with cumulative committed investment of around Rs 1.6 lakh crore.

The four are not identical. SiCSem, working with Britain's Clas-SiC Wafer Fab, will set up the country's first commercial silicon-carbide (SiC) compound fab in Bhubaneswar, with capacity for 60,000 wafers and 96 million packaged units a year. The second Odisha project, from America's 3D Glass Solutions, builds an advanced glass-substrate packaging plant aimed at high-performance computing and AI. Continental Device India will expand discrete power-chip output in Mohali, Punjab, and ASIP Technologies, partnering South Korea's APACT, will assemble chips in Andhra Pradesh.

## Why silicon carbide matters

Most of India's earlier wins — Micron's Sanand plant, the Tata-PSMC fab in Dholera — are about either packaging or mainstream silicon. Silicon carbide is a different animal. It is the material that makes electric-vehicle inverters, fast chargers, railway traction systems and solar power electronics efficient. China and the US are racing to lock up SiC supply because it underpins the energy transition. A domestic SiC fab, however modest, puts India on a map it has been absent from.

The geographic spread matters too. By pushing projects into Odisha, Punjab and Andhra, the mission is starting to look less like a single Gujarat showpiece and more like a national industrial base. Odisha's state government has been aggressive — it signed a separate substrate-technology MoU with Intel and 3DGS last month — and is openly courting the "semiconductor hub" label.

## The diaspora calculation

For the tens of thousands of Indian-origin engineers inside Intel, Micron, Nvidia, AMD and Applied Materials in the US, this is the question that actually matters: does any of this create work I would want?

The honest answer is "not yet, but the shape is forming." These are mostly assembly, packaging and mid-range device plants, not leading-edge logic fabs. The advanced nodes that define a chip-design career — sub-5nm logic — remain a TSMC and Samsung monopoly, and India is years from competing there. What is emerging instead is a packaging, power-electronics and compound-semiconductor ecosystem, exactly the kind of work that an experienced process or packaging engineer in Boise or Hillsboro could plausibly lead.

That is not nothing. Advanced packaging is where a growing share of chip value is migrating as Moore's Law slows, and a US-trained engineer who can stand up a glass-substrate or HBM-adjacent line is precisely who these plants will try to recruit. The 3DGS Odisha facility, which targets data-centre and AI packaging, is the one diaspora professionals should watch.

## What's next

Execution is the perennial Indian semiconductor caveat, and it applies here. Commercial production at the 3DGS plant is not expected before August 2028, and the SiC fab will take similar time to ramp. India's near-term output will remain concentrated in assembly and testing, not advanced fabrication.

But the through-line of the past year is consistent: more states, more materials, more of the supply chain. For an NRI engineer who has spent a decade being told the India chip story was all subsidy and no silicon, the map is finally starting to fill in — even if the jobs worth moving for are still a couple of years out."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Spent Three Years Being Called Late to AI. Google's Cloud Backlog Just Hit $460 Billion.",
        "subheadline": "A near-doubling of signed cloud commitments in a single quarter is the clearest sign yet that Pichai's full-stack AI bet is paying off — and it reshapes the job math for Indians inside Google.",
        "slug": make_slug("sundar-pichai-google-cloud-backlog-ai-gemini-momentum"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the thousands of Indian engineers at Google weighing AI-era job security, a $460 billion cloud backlog signals where the company is hiring and investing — and which teams are safest as the AI reorganisation grinds on.",
        "tags": ["google", "sundar-pichai", "ai", "gemini", "indian-tech-leaders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/google-ceo-says-ai-has-changed-revenue-picture-completely"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/alphabet-ai-sundar-pichai-gemini"},
            {"name": "Google Blog", "url": "https://blog.google/technology/developers/google-ai-studio-interactions-api/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai",
        "image_attribution": "Wikimedia Commons",
        "body": """When ChatGPT arrived in late 2022, the consensus on Sundar Pichai was unkind. Google had invented the transformer, the technology underneath modern AI, and then watched a San Francisco startup turn it into the fastest-growing product in history. Pichai, the story went, was the careful operator who had been caught flat-footed.

The numbers coming out of Mountain View now tell a different story.

## The backlog nobody expected

The figure that drew analysts' attention this quarter was not Google's AI revenue growth rate, though that was eye-catching. It was the cloud backlog — the value of signed, contracted commitments not yet recognised as revenue. It nearly doubled quarter over quarter to more than $460 billion, up from roughly $155 billion two quarters earlier. Management expects just over half of it to convert to revenue within 24 months.

A backlog of that size is not speculative interest. It is signed contracts. Pichai noted multiple billion-dollar-plus deals closed in the quarter, and said the number of deals in the $100 million-to-$1 billion range had doubled year over year. Gemini Enterprise's paid monthly active users grew 40% quarter over quarter, and existing customers expanded their spending 45% beyond their original commitments — the clearest signal that the product is being used, not shelved.

Alphabet's shares are up roughly 270% since ChatGPT's debut, triple the S&P 500's return over the same stretch. The man once mocked as slow has quietly turned a search-first company into what Barron's called a "full-stack AI powerhouse."

## How he did it

Pichai's playbook was unglamorous: consolidation. He merged Google Brain and DeepMind, pulled the AI work behind Chrome, Android, Pixel and Search into fewer teams, and pushed Gemini into products with, in his words, as little bureaucracy as possible. Layoffs and a stock offering funded enormous spending on custom TPUs, data centres and talent. This week the company moved its developer-facing Interactions API for Gemini to general availability, the kind of plumbing that locks enterprises in.

## What it means inside Google

Here is where the diaspora angle gets sharp. Google employs many thousands of Indian engineers, and the past 18 months have been anxious ones — buyouts, "efficiency" reorganisations, and a steady drumbeat of AI-will-replace-coders commentary. A $460 billion cloud backlog reframes that anxiety.

Money flows to backlog. The teams building and servicing Google Cloud, Gemini Enterprise and the AI infrastructure underneath them are where the contracted revenue lives, and they are the likeliest to keep hiring and the least likely to be cut. For an Indian engineer inside Google, the practical read is to gravitate toward Cloud, Gemini and infrastructure, and away from mature ad-tech maintenance roles that AI tooling is steadily automating.

There is a second, more personal angle. Pichai remains the most visible Indian-American in technology, and his rehabilitation from "too cautious" to "quietly won" is a useful counter-narrative for diaspora professionals who are themselves often typecast as reliable executors rather than bold leaders. The lesson he is modelling — that patient consolidation can beat first-mover noise — travels well.

## The cost side

None of this is free. Alphabet's capital expenditure has surged to build the chips and data centres these models require, and Pichai has acknowledged that managing the AI transition has consumed enormous leadership attention. The company is also experimenting with paid Gemini tiers through Google One, a sign it is still searching for the consumer business model to match the enterprise one.

But the core question that hung over Pichai for three years — could Google turn its research lead into a business — now has a number attached. It is $460 billion, and it is signed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ola Electric Built India's Biggest Scooter Factory. Its Quieter Rival Is Opening a Store a Day.",
        "subheadline": "As Ather expands toward 1,100 outlets and Ola shrinks from 4,000 to 700, India's electric-two-wheeler race has flipped from a land grab to a test of who can actually make money.",
        "slug": make_slug("ola-electric-ather-india-ev-scooter-profitability-race"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI investors who bought into the India EV story through Ola's or Ather's listings now face a clearer divide: the flashy market-share leader is retreating while the disciplined rival expands, and the gap explains which bet is holding up.",
        "tags": ["ev", "ola-electric", "ather-energy", "indian-tech", "mobility"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/indias-ola-electric-invest-2085-million-ev-cell-tech-units/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/ather-eyes-big-distribution-push-in-fy27-adding-400-stores-in-stark-contrast-with-ola-electrics-shrunk-footprint"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/ola-electric-ather-shift-focus-to-profitability-as-ev-industry-prioritises-margins-over-market-share"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Black_OLA_Electric_scooters.jpg/1280px-Black_OLA_Electric_scooters.jpg",
        "image_caption": "Ola Electric scooters, India's best-known electric two-wheeler brand",
        "image_attribution": "Wikimedia Commons",
        "body": """Two years ago, the story of India's electric-scooter market was a story about Ola Electric. The SoftBank-backed company commanded close to half of all e-scooter sales, ran an advertising blitz, and built the world's largest electric two-wheeler factory in Tamil Nadu. Founder Bhavish Aggarwal promised a vertically integrated empire — vehicles, battery cells, software, all in-house.

Today the most telling numbers in the sector belong to its quieter rival.

## A tale of two store counts

Ather Energy, the Bengaluru-based premium player, told analysts last week it plans to expand from about 700 retail stores in March 2026 to over 1,100 by March 2027 — opening, on average, more than a store a day. Executives suggested the real number could climb past 1,200 once its new EL platform launches.

Ola is moving in the opposite direction. After its December-quarter results, the company told investors it was shrinking its network from roughly 4,000 stores to around 700. Its deliveries fell to 1.73 lakh units in FY26 from 3.07 lakh the year before. Once the disruptor with 48.6% market share, Ola has ceded ground to legacy houses Bajaj and TVS, and to the steadier Ather.

## From land grab to margin discipline

The shift is not just about two companies. The entire industry has pivoted from chasing market share to chasing profitability. Ola is investing $208.5 million in its core vehicle and cell units, betting that in-house battery cells and heavy automation will finally cut its costs — it has projected operating costs falling as much as 50% in coming quarters. The logic is sound; the execution risk is real, because the same vertical-integration ambition is what stretched the company thin in the first place.

Ather is making the opposite wager: grow distribution methodically, keep the product premium, and let volume scale with reach rather than discounts. Across the sector, improving margins are coming from component localisation, stabilising supply chains and production efficiency — not from the subsidy-fuelled price wars of the early years.

## Why NRIs should care

For diaspora investors, this is more than industry trivia. Both Ola Electric and Ather are publicly listed, and the India EV growth story — a market projected to grow from roughly $5.3 billion in 2025 to nearly $18 billion by 2032 — has been a popular thesis for NRIs wanting exposure to domestic consumption without buying real estate.

The divergence now playing out is exactly the kind of signal that separates a narrative from a business. Ola's stock has rallied sharply on hopes of a turnaround, but its shrinking footprint and falling deliveries are warning lights. Ather's expansion is slower and less glamorous, but it is backed by volume growth and a clearer path to profit. An NRI deciding between the two is really deciding between betting on a dramatic recovery and betting on disciplined execution.

There is also a homeland-connection angle that is easy to miss from abroad. The scooters in question are the vehicles family members back in India are actually buying — the EV transition that diaspora relatives experience first-hand is happening on two wheels, not four. Tracking which brand survives is, in a small way, tracking how the everyday India that NRIs left behind is changing.

## What's next

Ather's EL platform launch in the middle of FY27 is the next real test; it is meant to widen the company's range from family scooters to performance models. Ola's profitability claims will be judged against its March-quarter results, still awaited. And looming over both is a government keen to accelerate the shift away from imported fuel — a tailwind that lifted EV stocks when the prime minister urged citizens to cut petrol consumption earlier this year.

The land grab is over. The endurance race has begun."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
