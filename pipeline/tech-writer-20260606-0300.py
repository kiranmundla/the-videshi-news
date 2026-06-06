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
        "headline": "Jensen Huang Called Marvell the 'Next Trillion-Dollar Company.' Its Biggest Lab Is in India.",
        "subheadline": "NVIDIA's CEO anointed the networking chipmaker at Computex, sending its stock up 30%. What Wall Street may not know: Marvell's largest R&D centre outside California sits across four Indian cities.",
        "slug": make_slug("marvell-trillion-dollar-jensen-huang-india-rd-hub"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Marvell employs over 1,000 engineers in Bangalore alone, with additional design centres in Pune, Hyderabad, and Chennai — making it a major employer of Indian semiconductor talent and a key beneficiary of India's chip design ecosystem.",
        "tags": ["marvell", "nvidia", "jensen-huang", "semiconductors", "india-rd", "computex"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
            {"name": "Zacks Investment Research", "url": "https://www.zacks.com"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com"},
            {"name": "Marvell Technology", "url": "https://www.marvell.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg",
        "image_caption": "Server racks in a modern data center, the kind of infrastructure Marvell's networking chips connect",
        "image_attribution": "Pexels",
        "body": """Jensen Huang does not waste endorsements. So when NVIDIA's CEO walked onto the Computex 2026 stage in Taipei, spotted Marvell CEO Matt Murphy wrapping up a keynote, and declared — "The next trillion-dollar company, ladies and gentlemen" — the semiconductor world paid attention.

Marvell's stock surged more than 30% in a single session. The market capitalisation leapt by $62 billion to roughly $254 billion. By the next morning, shares were up another 13%, and analysts were furiously revising their models. The question rippling through Wall Street: is Jensen Huang right?

## The Connectivity Thesis

The case is straightforward, once you understand the bottleneck. NVIDIA builds the processors that train and run AI models. But processors need to talk to each other — across racks, across data centres, across continents. That interconnect layer, the plumbing of the AI factory, is where Marvell lives.

Marvell makes custom application-specific integrated circuits (ASICs), high-speed networking switches, and silicon photonics technology that moves data at the speed AI demands. Its data centre segment now accounts for roughly 76% of total revenue. NVIDIA invested $2 billion in Marvell earlier this year to integrate its custom chips and networking gear into the NVLink Fusion ecosystem — the backbone of next-generation AI supercomputers.

"When you take a computing problem and disaggregate it into a lot of parts, and you distribute it across the entire data centre, what's necessary is connectivity," Huang said at Computex. "That's the reason why Marvell is so essential."

The implicit argument: as AI models grow, the networking layer scales faster than the compute layer. Marvell sits at that inflection point.

## India Designs the Chips

Here is the part that should matter to every Indian engineer scrolling LinkedIn jobs: Marvell's largest global R&D hub outside its Santa Clara headquarters is in India.

The India Design Centre spans four cities — Bangalore, Pune, Hyderabad, and Chennai. Bangalore alone employs over 1,000 engineers. A new 100,000-square-foot office in Pune houses labs and servers for end-to-end product development across Marvell's storage portfolio. The company plans to increase its Indian workforce by 15% annually over the next three years.

"Almost every product segment of Marvell has representation in India," Bharathi, a senior engineering leader at the company, told Digitimes. "Our objective is to position India as an equally important development site for all our data infrastructure products."

This is not outsourced grunt work. Indian teams at Marvell design custom ASICs, validate silicon, build switching platforms, and develop high-bandwidth memory compute architectures. Through acquisitions — Cavium, InPhi, Innovium — the India teams have absorbed capabilities in processor, network switch, and custom chip design. India now contributes to nearly every product line.

The broader context matters too. Nearly 25% of the world's fabless chip design engineers work in India. Marvell's competitors — Broadcom, Qualcomm, AMD — all run substantial Indian design centres. But Marvell's India operation is disproportionately central to its global output.

## The Trillion-Dollar Question

Getting from $254 billion to $1 trillion requires the stock to roughly quadruple. The optimists point to Micron Technology, which crossed the trillion-dollar threshold just days before Huang's Computex remarks, propelled by AI memory demand. Investors are scanning for the next semiconductor company to make that leap.

Marvell's bull case: AI data centres are being built at a rate that will sustain double-digit revenue growth for years. The custom ASIC market, where Marvell competes with Broadcom, is expanding as hyperscalers like Amazon, Google, and Microsoft design their own chips rather than buying off-the-shelf GPUs. Marvell holds an estimated 15-20% share of this market.

The bear case: the stock is trading at over 60 times forward earnings after a 40% rally in four trading sessions. Huang's endorsement, however sincere, is also strategic — NVIDIA owns $2 billion in Marvell stock. And the custom ASIC market, while growing, pits Marvell against Broadcom, a company with ten times its revenue.

## What NRIs Should Watch

For the Indian diaspora in tech, the Marvell story is worth tracking on two fronts. As an employer, the company is one of the most consequential semiconductor firms hiring Indian chip designers at scale. As a stock, it has become the latest AI-adjacency play that could either compound or correct sharply.

The jobs are real. The trillion-dollar framing is aspirational. Both are worth watching."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sanjay Mehrotra's Micron Joins the Trillion-Dollar Club. Three Visa Rejections Couldn't Stop Him.",
        "subheadline": "The Kanpur-born, BITS Pilani-educated CEO now leads one of America's ten most valuable companies. Three of the world's priciest tech firms are run by Indians who arrived with engineering degrees and middle-class resolve.",
        "slug": make_slug("sanjay-mehrotra-micron-trillion-dollar-visa-rejections"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Mehrotra completes an extraordinary Indian-origin trifecta atop trillion-dollar tech: alongside Satya Nadella at Microsoft and Sundar Pichai at Alphabet. Micron is also building a $2.75 billion ATMP facility in Gujarat — a direct bet on India's semiconductor future.",
        "tags": ["micron", "sanjay-mehrotra", "trillion-dollar", "indian-ceo", "semiconductors", "hbm", "ai-memory"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Times of India / CurrentIndia", "url": "https://www.currentindia.com"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Motley Fool", "url": "https://www.fool.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Sanjay Mehrotra, CEO of Micron Technology, now leads one of America's ten most valuable companies",
        "image_attribution": "Wikimedia Commons",
        "body": """In the summer of 1976, a teenage engineering student from BITS Pilani stood in the lobby of the US embassy in New Delhi. He had just been denied a student visa for the third time. His father, who had accompanied him, refused to leave. He spotted the consular officer's photo on the wall, worked out that the man was at lunch, and waited to confront him about why his son — with confirmed admissions to three American universities — kept being turned away.

The persistence worked. Half a century later, that student, Sanjay Mehrotra, is the CEO of Micron Technology, the memory-chip giant that crossed a $1 trillion market capitalisation in late May 2026 to break into the top ten US companies by valuation — overtaking Walmart, Berkshire Hathaway, and JPMorgan Chase.

## The Desi Tableau

Mehrotra's ascent completes an extraordinary Indian-origin trifecta atop corporate America. Three of the world's most valuable technology companies — Microsoft ($3.17 trillion, Satya Nadella), Alphabet ($4.31 trillion, Sundar Pichai), and Micron ($1.2 trillion, Sanjay Mehrotra) — are now run by Indian-born executives who arrived in the United States as middle-class strivers.

Nadella grew up in Hyderabad as the son of a civil servant. Pichai was raised in a modest Chennai apartment where the family shared a rotary telephone. Mehrotra came from a middle-class family in Kanpur that did not have a phone at all. Calls to his parents during his early American years went through "PP" — *padosi ka phone* — ringing a neighbour's landline who would summon his parents over.

The symbolism is hard to miss. At a time when H-1B visas dominate immigration debates and MAGA rhetoric questions the contributions of foreign-born workers, three Indians lead companies collectively worth over $8 trillion.

## The HBM Bet

Mehrotra's personal story is compelling. But what actually drove Micron to a trillion dollars is a product called high-bandwidth memory, or HBM.

HBM is the specialised RAM stacked directly beside AI processors — NVIDIA's GPUs, AMD's accelerators, Google's TPUs — to feed them data at speeds ordinary memory cannot match. As AI models grew from millions to trillions of parameters, the memory bottleneck became the constraint. Micron bet early on solving it.

The numbers are staggering. Micron's fiscal second quarter (ended February 2026) recorded $23.86 billion in revenue — nearly triple the $13.64 billion a year earlier. Non-GAAP gross margin hit 74.9%, a number that barely reads like a hardware business. Adjusted free cash flow was $6.9 billion for a single quarter.

The entire 2026 HBM supply is sold out under fixed-price contracts. Volume and pricing negotiations are locked in through calendar 2027. Analysts project full-year fiscal 2026 revenue of $108.7 billion, with earnings per share climbing to $58.05.

When NVIDIA CEO Jensen Huang met Mehrotra three years ago and outlined how the memory market would evolve, Mehrotra aligned Micron's roadmap accordingly. "I was really grateful that Micron and Nvidia really lined up all of our road map," Huang told Reuters.

## The Gujarat Connection

For the Indian diaspora, Micron's story has a second chapter that goes beyond CEO representation.

Micron is building a $2.75 billion assembly, testing, marking, and packaging (ATMP) facility in Sanand, Gujarat — one of the first major semiconductor investments under India's Semiconductor Mission. Prime Minister Modi inaugurated the facility in February 2026. The plant will process and package memory chips for global markets, creating thousands of skilled jobs in a state that is positioning itself as India's semiconductor corridor alongside the Tata Electronics fab in Dholera.

The Gujarat facility does not fabricate chips from scratch — Micron's wafer fabs remain in the US, Japan, and Singapore. But ATMP is the fastest-growing and most accessible segment of the semiconductor value chain for India, and Micron's commitment there signals that the company views India as more than a talent pool.

## Priced to Perfection?

At $864 per share, Micron trades at roughly 50 times trailing earnings. The bull case rests on the forward multiple of about 11 times, which only works if the current revenue trajectory holds. Samsung and SK Hynix are both ramping HBM capacity, and by late 2027, the supply crunch that has given Micron such extraordinary pricing power may begin to ease.

Morgan Stanley recently doubled its price target. Raymond James set a target of $1,100. But some analysts warn that the stock has priced in the best-case outcome.

For NRI investors, the risk-reward is a familiar tech dilemma: the fundamentals are real, the moat is narrowing, and the valuation assumes nothing goes wrong. Mehrotra has navigated Micron from a $20 billion company to a trillion-dollar one. Whether he can keep it there depends on whether AI's appetite for memory stays insatiable — or whether, like every semiconductor cycle before it, supply eventually catches demand."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Cut the Cybersecurity Team It Paid $5.4 Billion For. AI Got the Budget Instead.",
        "subheadline": "Sundar Pichai raised $85 billion last week for AI infrastructure. Days later, Google quietly laid off staff from Mandiant and its Threat Intelligence Group — the elite units that track state-sponsored hackers.",
        "slug": make_slug("google-mandiant-cybersecurity-layoffs-ai-budget"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Google Cloud employs thousands of Indian engineers, many on H-1B visas. Cybersecurity teams at Google, including Mandiant, have significant Indian representation — and these workers face the 60-day grace period clock if their roles are eliminated.",
        "tags": ["google", "mandiant", "cybersecurity", "layoffs", "ai-restructuring", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business Insider", "url": "https://www.businessinsider.com"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com"},
            {"name": "OpenTools", "url": "https://opentools.ai"},
            {"name": "Challenger, Gray & Christmas", "url": "https://www.challengergray.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/207580/pexels-photo-207580.jpeg",
        "image_caption": "Computer code on a dark screen, representing the cybersecurity work now being restructured at Google",
        "image_attribution": "Pexels",
        "body": """The timeline tells the story. On June 3, Sundar Pichai stood before investors and announced that Alphabet had raised approximately $85 billion in the largest technology equity offering in history — including a $10 billion anchor from Berkshire Hathaway. The purpose: building AI infrastructure at a scale that matches "strong demand for our AI solutions and services."

Two days later, Google quietly laid off employees across its Cloud division, including staff from the Threat Intelligence Group and Mandiant — the cybersecurity firm Google acquired in 2022 for $5.4 billion.

The cuts have not been quantified. A Google spokesperson offered the customary boilerplate: "We regularly evaluate our internal structures to ensure we are best positioned to meet the evolving demands of our customers and the industry." Internally, employees were told the reductions were linked to reallocating resources toward high-growth areas. The high-growth area, in case anyone missed it, is AI.

## What Google Is Cutting

Mandiant is not a marginal acquisition. Before Google bought it, Mandiant was the company governments called after state-sponsored hackers breached their networks. Its Threat Intelligence Group tracked advanced persistent threats — Chinese espionage campaigns, Russian disinformation operations, North Korean cryptocurrency theft. Its research shaped how the entire cybersecurity industry understood nation-state hacking.

Google integrated Mandiant into its Cloud division to differentiate Google Cloud Security as an enterprise offering. The logic was sound: enterprises choosing between AWS, Azure, and Google Cloud might tip toward the one that came with world-class threat intelligence built in.

Now, parts of that capability are being trimmed. The Threat Intelligence Group was hit on June 3. Broader Mandiant staff and other Cloud division employees followed over the next two weeks. Former employees have taken to LinkedIn with posts describing the experience as "bittersweet" — the particular Silicon Valley euphemism for being laid off from a team you believed in.

## The AI Reallocation Machine

Google is not alone. The pattern has become structural across big tech. Companies raise capital for AI, then reduce headcount in divisions that do not directly serve the AI roadmap. The arithmetic is blunt: AI infrastructure requires massive capital expenditure, and the easiest way to fund it without cratering margins is to cut teams whose work does not generate immediate revenue.

In May alone, US technology companies announced 38,242 job cuts — a nearly two-year high, according to outplacement firm Challenger, Gray & Christmas. For the third consecutive month, artificial intelligence was the primary reason employers cited for layoffs. Year-to-date, tech layoffs total 123,653, a 66% increase over the same period in 2025.

Meta cut 7,000 roles last month. Intuit eliminated 3,000. GitLab laid off 350 and exited 22 countries to pivot toward its "agentic era." Cloudflare announced over 1,100 position cuts. Oracle shed 30,000 globally, with 12,000 in India.

## The H-1B Dimension

For Indian engineers at Google, the cybersecurity layoffs carry an additional weight that their American colleagues do not face. Workers on H-1B visas who lose their positions have a 60-day grace period to find a new employer willing to sponsor them — or leave the country.

Google Cloud employs thousands of Indian-origin workers, many in precisely the kind of specialised cybersecurity, cloud engineering, and threat analysis roles that are being restructured. The Indian representation in these teams is not coincidental: India produces more cybersecurity and network engineering graduates than any country outside the United States, and Google has historically recruited aggressively from IITs and top Indian universities for its security divisions.

The grace period is not generous. Sixty days to interview, receive an offer, complete paperwork, and transfer an H-1B to a new employer — while processing the emotional and financial shock of a layoff — is a timeline that forces rushed decisions. Some will take roles below their skill level to maintain visa status. Others will return to India, where Google's Bangalore office may or may not have equivalent openings.

## The Paradox

There is an uncomfortable irony in Google cutting cybersecurity staff while pouring $85 billion into AI. Agentic AI systems — the kind Google is building with Gemini 3.5 and Antigravity — will create entirely new categories of security vulnerabilities. Autonomous agents that take actions on behalf of users, access enterprise data, and interact with third-party systems will need threat models that do not yet exist. The people best positioned to build those models are the ones Google is letting go.

The market does not appear troubled. Alphabet's stock dipped less than 1% on the news. Investors are focused on the $85 billion raise and the AI opportunity. The cybersecurity layoffs are a rounding error in a $4.5 trillion company.

For the engineers walking out of Google Cloud offices this week, the rounding error is their career."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
