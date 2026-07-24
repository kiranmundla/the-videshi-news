#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Helped Build the AI Arms Race. Now He Says It's Time to Stop Fighting It.",
        "subheadline": "Microsoft's CEO is pushing the industry away from ever-bigger frontier models — and weighing whether to host China's DeepSeek. For Indian engineers inside Redmond, the pivot reshapes what they build next.",
        "slug": make_slug("satya-nadella-microsoft-ai-reset-deepseek-frontier-models-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tens of thousands of Indian engineers at Microsoft build on Azure and Copilot; Nadella's shift away from a frontier-model race toward cheaper, applied AI changes which projects get funded and which careers get protected.",
        "tags": ["satya-nadella", "microsoft", "ai", "indian-tech", "openai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/microsoft-satya-nadella-ai-reset"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/microsoft-stock-satya-nadella-ai"},
            {"name": "TipRanks", "url": "https://www.tipranks.com/news/microsoft-stock-msft-jumps-as-ceo-satya-nadella-says-xbox-needs-to-become-sustainable"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft chief executive Satya Nadella, who is urging the industry to rethink the race to build ever-larger AI models",
        "image_attribution": "Wikimedia Commons",
        "body": """Satya Nadella spent the better part of a decade turning Microsoft into one of the chief architects of the artificial-intelligence boom. He bet billions on OpenAI before most rivals took it seriously, wired its models into everything from Office to GitHub, and watched Microsoft's market value swell on the promise of Copilot. So it is striking that the man who helped start the race is now arguing the industry should slow it down.

In remarks reported this week, Nadella joined a growing camp of executives questioning whether the relentless pursuit of bigger, costlier frontier models is the right path. He suggested there is "room for every company to thrive," and that the future belongs as much to cheaper, applied AI as to ever-more-capable systems. A Microsoft spokesman framed it carefully — this is not a "zero-sum game," and the company will keep nurturing its partnerships with OpenAI and Anthropic. But the message landed as a quiet repudiation of the maximalist logic that has driven the sector.

## The DeepSeek question

The clearest sign of the shift is what Microsoft is reportedly weighing: hosting a version of DeepSeek, the ultralow-cost Chinese model-maker that both OpenAI and Anthropic have accused of "distilling" — effectively copying — their top systems. Offering DeepSeek on Azure would almost certainly send its usage soaring, and it would do so at the expense of the very partners Microsoft has spent billions building up.

That tension is the story. Microsoft is simultaneously OpenAI's oldest backer and, increasingly, a company hedging against the possibility that frontier models become a commodity. Nadella has long played elder statesman in the trillion-dollar AI contest. Hedging toward a low-cost Chinese challenger is not the move of a man who believes the biggest model always wins.

## Why this matters in San Jose and Hyderabad

For the Indian engineers who make up a large share of Microsoft's technical workforce — on Azure, on Copilot, in the India Development Center in Hyderabad and Bengaluru — this is not abstract strategy. It determines which roadmaps get funded. A company chasing frontier supremacy pours resources into a narrow set of research-heavy teams. A company optimizing for cheap, deployable AI spreads its bets across applied product work, cost engineering and inference efficiency — the kind of unglamorous but durable work where much of India's talent already sits.

It also reframes the anxiety hanging over the sector. Microsoft has been sued by shareholders alleging it masked slowing Azure growth while capital spending ballooned to $37.5 billion in a single quarter. Nadella himself has conceded that Xbox must become "sustainable," a word that has started creeping into how he talks about the whole business. When the chief executive starts emphasizing discipline over dominance, headcount math changes — and for visa-dependent engineers, the difference between a team that is "investing" and one that is "optimizing" can be the difference between a promotion and a layoff notice with a 60-day clock attached.

## A reset, not a retreat

None of this means Microsoft is pulling back from AI. Its sales grew 18% over the past year and earnings per share rose 30%, even as the stock lagged. ByteDance alone reportedly spends more than $1 billion a year on Azure AI services. The company is moving Copilot toward usage-based pricing and openly exploring cheaper models — both signs of a business trying to make AI pay rather than merely impress.

For the diaspora, the takeaway is that the era of blank-cheque AI ambition is giving way to something more familiar: a fight over margins, efficiency and which products actually earn their keep. That is a contest Indian engineers — trained in a services industry built on doing more with less — are unusually well placed to win. Nadella, born in Hyderabad and shaped by that same ethos, may simply be the first big-tech chief to say out loud what the next phase requires.

The question for the thousands who report up to him is whether their current project sits on the side of the bet he is now making — or the one he is quietly walking away from."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Is Building India Its First AI University. The Real Prize Is 10,000 Engineers a Year.",
        "subheadline": "Andhra Pradesh signed a memorandum with Nvidia to create the country's first dedicated AI university, with curriculum, training and startup access bundled in. It is a talent factory aimed squarely at the global market — including the diaspora's employers.",
        "slug": make_slug("nvidia-andhra-pradesh-ai-university-india-talent-naidu-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The university is designed to train AI engineers for a global market, meaning the next wave of talent flowing into Bay Area and New Jersey tech firms — and the GCCs that hire NRIs back home — may carry Nvidia-certified credentials from Amaravati.",
        "tags": ["nvidia", "india-ai", "andhra-pradesh", "ai-education", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indias-first-ai-university-to-be-built-in-andhra-pradesh"},
            {"name": "VentureBeat", "url": "https://venturebeat.com/ai/nvidia-ceo-touts-indias-progress-with-sovereign-ai"},
            {"name": "AI Magazine", "url": "https://aimagazine.com/articles/nvidia-backs-indiaai-mission"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia founder and CEO Jensen Huang, whose company is partnering with Andhra Pradesh on India's first AI university",
        "image_attribution": "Wikimedia Commons",
        "body": """India is getting its first university dedicated entirely to artificial intelligence, and the partner behind it is the most valuable company on earth. Andhra Pradesh has signed a memorandum with Nvidia to build the institution, the state's chief minister, N. Chandrababu Naidu, announced this week, with the project to be led by IT minister Nara Lokesh.

The headline is a building. The substance is a pipeline. Under the agreement, Nvidia will help shape the curriculum and train faculty, with a stated goal of giving AI skills to more than 10,000 engineering students across the state within two years. Roughly 500 AI startups would get access to Nvidia's Inception program, opening doors to its chips, software and global network. The state is selling it as a pillar of Naidu's "Swarna Andhra Pradesh" — golden Andhra — vision.

## A talent factory, not a campus

Strip away the political framing and what Nvidia is building is a credentialing machine. The company does not make money from a university; it makes money from an ecosystem of developers, startups and enterprises locked into its CUDA software and GPU hardware. Train 10,000 engineers a year on Nvidia tooling and you have created 10,000 people who will reach for Nvidia by instinct for the rest of their careers — wherever those careers take them.

And they will travel. India already trains a vast share of the world's AI engineers, and Nvidia has spent the past two years courting the country aggressively. Its executives note that of the world's 2,000 largest corporations, 1,800 run a global capability center in India, employing more than two million people and growing toward three million. Each of those centers, in Nvidia's telling, will eventually need its own "AI factory." A state university churning out GPU-fluent graduates feeds exactly that demand.

## Why the diaspora should pay attention

For Indian professionals abroad, this is the supply side of a story they live every day. The engineer in Sunnyvale wondering who will fill the next cohort of AI roles, the manager in a New Jersey bank staffing an offshore team, the founder hiring in Hyderabad — all of them are downstream of where India's talent gets trained and on whose tools. If that training increasingly runs through Nvidia and through state-backed institutions like this one, the credentials arriving on résumés will look different, and more standardized, within a few years.

There is also a return-migration angle. India's pitch to its diaspora has shifted from "come home for family" to "come home for the work." A flagship AI university, paired with the country's $1.2-billion AI Mission and a 20-year tax holiday for data-center investment announced in this year's budget, is part of a deliberate effort to make staying in India — or coming back — a credible career choice for ambitious engineers rather than a sacrifice.

## The caveats

Memorandums are not buildings, and India's record on translating ambitious education announcements into functioning institutions is mixed. Andhra Pradesh in particular has a history of grand tech promises — the state has separately touted an IBM Quantum and TCS partnership to build India's largest quantum computer in its Quantum Valley Tech Park — that move slower in practice than in press releases. A curriculum co-designed by a chip vendor also raises an obvious question about whether students are being educated or onboarded.

Still, the direction is unmistakable. Nvidia is no longer just selling India GPUs; it is helping shape who India trains and how. For a diaspora whose fortunes are tied to the flow of Indian engineering talent into the global economy, the factory being built in Amaravati is worth watching — because its graduates will, sooner or later, be sitting across the table.

Whether the university lives up to its billing will take years to judge. But the bet itself tells you where both India and Nvidia think the next decade of AI talent will be made."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "While Wall Street Panics About AI Killing IT Jobs, a US Firm Just Opened in Bengaluru to Hire More",
        "subheadline": "Cybersecurity company N-able is expanding its new India workforce by at least 50% this year, betting on AI and security talent even as Accenture's gloom drags down Indian IT stocks. The split says a lot about which tech jobs are safe.",
        "slug": make_slug("n-able-bengaluru-gcc-hiring-cybersecurity-india-talent-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "As layoffs and AI fears hammer the IT-services giants where many NRIs built careers, the GCC boom is quietly creating the opposite — high-skill AI and security roles in India that pull talent home and reshape where the diaspora's next jobs are.",
        "tags": ["gcc", "cybersecurity", "india-tech", "bengaluru", "indian-tech-jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/n-able-india-gcc-bengaluru-expansion"},
            {"name": "Reuters (Accenture / Indian IT)", "url": "https://www.reuters.com/markets/indian-it-stocks-tumble-accenture-weak-outlook"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/it-services-stocks-ai-sell-off"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software developers collaborating in a modern office, the kind of high-skill roles fueling India's global capability center boom",
        "image_attribution": "Pexels",
        "body": """It was a brutal week for Indian IT. The Nifty IT index slumped more than 5% on Friday after Accenture, the industry's bellwether, forecast weak quarterly sales and trimmed its annual outlook. Shares of Tata Consultancy Services, Infosys, HCLTech and Wipro fell between 3% and 8% as investors fretted that artificial intelligence is hollowing out the labour-intensive model that built India's $315-billion services empire.

Then, almost as a counterpoint, a US cybersecurity firm called N-able opened a new center in Bengaluru and announced it would grow its India workforce by at least 50% before the year is out. Two stories, same week, opposite directions. The gap between them is the most important thing happening in Indian tech right now.

## Talent, not cost

N-able, which provides IT-management, cybersecurity and data-protection software to more than 500,000 organizations, opened its Global Capability Center with over 100 employees and plans to expand fast. What is notable is the reasoning. "The reason we're in Bengaluru is capability," CEO John Pagliuca told Reuters. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play."

That sentence marks how far the GCC story has traveled. For two decades, the pitch for India was cost — cheaper engineers doing the same work. The new pitch is capability: AI engineering, applied machine learning, cloud security and threat research, which Pagliuca called among the hardest skills in the world to source. N-able is not in Bengaluru to save money. It is there because that is where the people are.

It is hardly alone. India's GCC workforce is projected to reach 2.36 million by the end of 2026, according to industry body Nasscom and consultancy Zinnov, with AI and cybersecurity driving much of the demand. While the headlines scream about layoffs at the services giants, multinationals are quietly building their own high-end engineering arms inside India and competing fiercely for the same talent.

## The two tiers of Indian tech

For the diaspora, this bifurcation is the crucial signal. The work that AI threatens — repetitive, ticket-based, low-margin services delivery — is exactly the work the IT giants are most exposed to, and it is why their stocks are being punished. The work that AI rewards — building the security systems, the models, the cloud architecture — is flowing into GCCs that pay well, demand elite skills and increasingly sit at the center of global products rather than the periphery.

That changes the calculus for an NRI engineer weighing a move home. A decade ago, returning to India often meant a step down into back-office delivery. Today it can mean a senior role at the India arm of a global firm, working on the same frontier problems as colleagues in Austin or Tel Aviv. As cybercriminals increasingly weaponize generative AI for automated attacks, Pagliuca said the Bengaluru team will lead defensive AI work — threat detection, monitoring, faster response. That is not commodity labour; it is the front line.

## Reading the sell-off

The market's pessimism is not baseless. As the Motley Fool noted, the fear that AI hollows out demand for consulting and engineering could weigh on services stocks for years. But it is worth separating the company from the country. Accenture's weak outlook says something about a particular business model under pressure. It does not say India's engineers are out of demand — N-able, and the broader GCC surge, suggest the opposite.

For the Indian American watching their portfolio and their LinkedIn feed at once, the lesson is to stop reading "Indian IT" as a single trade. One half of it is being disrupted. The other half is being courted harder than ever. Knowing which side your career — or your next hire — sits on has rarely mattered more."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
