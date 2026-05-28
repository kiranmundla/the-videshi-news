#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-28 04:55 UTC run"""
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
        "headline": "Britain Just Told Sunil Mittal He Can't Buy More of BT. Here's Why It Matters.",
        "subheadline": "The UK government is blocking India's telecom titan from raising his BT stake beyond 25%, invoking national security over its fibre-optic backbone. For Indian capital eyeing Western infrastructure, the ceiling just got lower.",
        "slug": make_slug("uk-blocks-sunil-mittal-bt-stake-national-security"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian billionaire capital being blocked from Western telecom infrastructure raises questions about how Indian investment will be treated globally — relevant to NRI investors, Bharti Airtel shareholders, and anyone watching India's push to become a global business power.",
        "tags": ["sunil-mittal", "bharti-airtel", "bt-group", "telecom", "uk-india", "national-security"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/uk-would-block-indian-billionaire-mittal-raising-bt-stake-ft-reports-2026-05-28/"},
            {"name": "Financial Times", "url": "https://www.ft.com/content/sunil-mittal-bt-stake-uk-block"},
            {"name": "WhalesBook", "url": "https://www.whalesbook.com/news/English/telecom/UK-Signals-Block-on-Mittals-Expansion-in-BT-Group/6a17cc17c7466b1ac3b9024a"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/Sunil_Mittal.jpg",
        "image_caption": "Sunil Bharti Mittal, founder and chairman of Bharti Enterprises. Photo: Wikimedia Commons",
        "body": """Sunil Bharti Mittal built Bharti Airtel from a bicycle-parts business in Ludhiana into the world's third-largest mobile operator. He turned a £3.2 billion bet on BT Group — Britain's legacy telecom monopoly — into the single largest private shareholding in the company. And now the British government has told him, politely but firmly, that 24.5% is as far as he goes.

According to the Financial Times, the UK government would oppose any attempt by Bharti Enterprises to push its BT stake past the 25% threshold. That number isn't arbitrary. Under the National Security and Investment Act, crossing it triggers a mandatory formal review — one that Whitehall has already signalled it intends to block.

## The Openreach Problem

The issue isn't Mittal personally. It's Openreach, BT's fixed-line network subsidiary that runs the fibre-optic backbone serving 22 million British homes. Openreach is, in effect, critical national infrastructure — the digital equivalent of the water mains. The UK government treats it as such, and any foreign investor acquiring meaningful control triggers the same alarm bells that a defence contractor acquisition would.

Bharti acquired the bulk of its stake in 2024 from Patrick Drahi's debt-laden Altice, paying roughly £3.2 billion for what was then a struggling telco. Since then, Mittal and Bharti Global CEO Gopal Vittal have both joined BT's board as non-independent directors. The relationship has been broadly constructive — BT CEO Allison Kirkby has welcomed Bharti's support for the fibre rollout. But support and control are different things, and London has drawn the line.

## What It Signals for Indian Capital

For the Indian diaspora watching from the Bay Area, New Jersey, or London, this is more than a telecom story. It's a signal about the limits of Indian capital in Western markets.

Indian conglomerates have been on an acquisition spree. The Adani Group's ports, the Tata Group's Jaguar Land Rover and Corus Steel — Indian industrial capital has systematically expanded into Western infrastructure. Mittal's move on BT was the most ambitious play yet in telecom, a sector where national security sensitivities run high and regulatory barriers are thick.

The UK's block isn't a diplomatic affront. Officials have stressed that this isn't about India specifically — it's about sovereign prerogative over critical assets. But the practical effect is clear: there is a ceiling on how much Indian capital can influence Western infrastructure, and that ceiling is set by national security reviews rather than market forces.

For NRI investors holding Bharti Airtel stock — which has tripled in value over the past five years — the question is whether BT becomes a dead asset on Bharti's balance sheet or a steady-dividend cash cow that Mittal can influence but never fully control. At a P/E ratio well above the UK telecom industry median, BT's valuation already prices in some strategic premium from Bharti's involvement. The government's move caps that premium.

## The Bigger Picture

The pattern is visible across Western economies. Australia blocked a Chinese-linked bid for its largest power grid. Germany took a stake in a container terminal to prevent Chinese acquisition. And now Britain is capping an Indian billionaire's ownership of its telecom backbone. The message to global capital — including Indian capital — is consistent: invest, but don't expect control.

For Indian tech professionals in London working in BT's Shoreditch offices or Bharti's Mayfair headquarters, the stakes are personal. A more aggressive Bharti presence would likely have meant more Indian executives in senior roles, more cross-pollination between Airtel's mobile-first innovation culture and BT's legacy infrastructure mindset. That pathway is now narrower.

Mittal, characteristically, hasn't commented publicly. Bharti Enterprises has said it has "no current plans" to raise its stake beyond 25%. The phrasing is careful — it doesn't say it never will. But for now, the world's third-largest mobile operator has hit a wall that money alone cannot breach."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Standard Chartered Is Cutting 7,000 Jobs With AI. Its CEO Called Them 'Lower-Value Human Capital.'",
        "subheadline": "The bank plans to eliminate 15% of its back-office roles by 2030, with hubs in Bengaluru and Chennai bearing the heaviest burden. CEO Bill Winters apologised for the phrasing. The layoffs are proceeding anyway.",
        "slug": make_slug("standard-chartered-7000-ai-job-cuts-india-hubs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Standard Chartered employs tens of thousands in Bengaluru and Chennai back-office hubs — exactly the roles being targeted. For NRI finance professionals and their families in India, this is a direct threat to livelihoods. AI salary inflation of 40-50% in India tech roles means even the survivors face a transformed career landscape.",
        "tags": ["standard-chartered", "ai-layoffs", "india-banking", "bengaluru", "automation", "bill-winters"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ai-age-firms-chase-growth-fewer-workers-2026-05-28/"},
            {"name": "The Guardian", "url": "https://www.theguardian.com/business/standard-chartered-job-cuts-ai"},
            {"name": "Noah News", "url": "https://noah-news.com/standard-chartereds-job-cuts-signal-a-new-era-of-ai-driven-banking-reshuffle/"},
            {"name": "Tom's Hardware", "url": "https://www.tomshardware.com/tech-industry/standard-chartered-ai-job-cuts"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/ce/William_Thomas_Winters_%28born_1961%29_at_World_Economic_Forum_Davos_2021.png",
        "image_caption": "Standard Chartered CEO Bill Winters at the World Economic Forum, 2021. Photo: Wikimedia Commons",
        "body": """Bill Winters chose his words carefully, and then chose them very badly. The Standard Chartered CEO, explaining the bank's plan to cut more than 7,000 roles by 2030, described the affected workers as "lower-value human capital." He later apologised. The cuts are still happening.

The London-headquartered bank — which earns the bulk of its revenue in Asia, Africa, and the Middle East — is eliminating roughly 15% of its corporate and back-office workforce as it pushes deeper into AI and automation. The restructuring targets compliance, risk assessment, HR, and operational support functions, with the explicit goal of raising income per employee by 20% by 2028.

## Bengaluru and Chennai in the Crosshairs

For the Indian diaspora, the geography of these cuts matters enormously. Standard Chartered operates major technology and operations hubs in Bengaluru and Chennai — centres that employ tens of thousands of workers in precisely the back-office functions being targeted. These aren't call centres staffed by fresh graduates. They're compliance analysts, risk modellers, HR administrators, and operations specialists, many of whom have built decade-long careers at the bank.

The hubs also feed a broader ecosystem. A Standard Chartered job in Bengaluru's Manyata Tech Park anchors a household: school fees, car loans, apartment EMIs. When 15% of an operational workforce disappears, the ripple effects extend into local real estate, retail, and the broader services economy.

Winters' framing — that this is "replacing in some cases lower-value human capital," not cost-cutting — is technically interesting and humanly tone-deaf. The distinction he's drawing is between eliminating entire layers of routine work versus trimming headcount to hit quarterly targets. He may be right that AI-driven workflow redesign is structurally different from a traditional redundancy round. But the people losing their jobs experience both the same way.

## The Salary Inflation Paradox

The cuts come against a backdrop that makes the Indian tech labour market look almost paradoxical. At a Reuters summit in Bengaluru this week, Novo Nordisk executive John Dawber said salaries in some AI and machine-learning roles are rising 40% to 50% annually, threatening to erode India's cost advantage entirely.

"If costs go out of control, we start to lose one edge of the triangle of your value proposition," Dawber said.

So the same market is simultaneously shedding thousands of back-office workers and paying astronomical premiums for AI talent. The message for Indian tech professionals is stark: the median is hollowing out. If you're doing work that can be described in a process flowchart, AI is coming for your job. If you're building the AI that replaces those flowcharts, you can name your price.

This bifurcation will reshape career planning for an entire generation of Indian engineers and business graduates. The traditional path — solid degree, campus placement at a multinational, steady promotions in operations or compliance — is being compressed into a much shorter runway. The new path demands continuous upskilling in AI, data science, and automation tools. StanChart has promised retraining and redeployment for some affected employees, but "some" is doing a lot of work in that sentence.

## The Broader Pattern

Standard Chartered isn't alone. HSBC's CEO has told staff to "not fight AI." Meta cut 8,000 roles this month, with significant India exposure. Across global banking and technology, the pattern is consistent: AI is moving from pilot projects to workforce strategy, and the back offices of Bengaluru, Hyderabad, and Chennai are ground zero.

For NRI professionals in finance — whether in London's Canary Wharf, Singapore's Raffles Place, or Mumbai's BKC — the question isn't whether your bank will do this. It's when. The executives who frame it most honestly will be the ones who get criticised most publicly, as Winters discovered. But the underlying shift is indifferent to the language used to describe it.

The 7,000 roles being eliminated at Standard Chartered are not coming back. They're being replaced by systems that don't need lunch breaks, don't file HR complaints, and don't require visa sponsorship. For Indian workers who built their lives around the promise of multinational employment, the recalculation has already begun."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Synopsys Just Coined the Term 'Agent Engineer.' India's Chip Designers Should Pay Attention.",
        "subheadline": "The EDA giant raised its forecast on surging AI chip design demand and struck a deal with activist investor Elliott. Its new pitch: AI 'agent engineers' that work alongside human designers. India's 50,000-strong chip design workforce is directly in the path of this shift.",
        "slug": make_slug("synopsys-agent-engineer-ai-chip-design-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Synopsys employs thousands of engineers in India, its largest non-US engineering hub. India's semiconductor design workforce of ~50,000 engineers is directly affected by the 'agent engineer' concept — AI tools that augment or replace parts of the chip design process. For Indian chip designers in the Bay Area and Bengaluru, this reshapes career trajectories.",
        "tags": ["synopsys", "eda", "chip-design", "ai-agents", "india-semiconductor", "elliott-management"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/synopsys-raises-annual-forecast-demand-ai-chip-design-software-2026-05-27/"},
            {"name": "LSEG Data", "url": "https://www.lseg.com/"},
            {"name": "Investors.com", "url": "https://www.investors.com/news/technology/broadcom-stock-ready-to-buy-catch/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Microchips on a circuit board. AI is reshaping how these are designed. Photo: Pexels",
        "body": """Sassine Ghazi has a new term for what's coming to chip design, and it's worth sitting with for a moment: "agent engineer." Not a bot. Not an assistant. An agent — the implication being that it acts with some degree of autonomy, making design decisions that were previously the exclusive domain of human engineers with PhDs and decades of experience.

Ghazi, the CEO of Synopsys, used the phrase while explaining why the world's largest electronic design automation company just raised its annual revenue forecast to between $9.63 billion and $9.71 billion. Demand for AI chip design tools is surging as every major hyperscaler — Google, Amazon, Meta, Microsoft — races to build custom silicon. And Synopsys, which provides the software that makes those chips possible, is riding the wave.

## The Numbers Behind the Confidence

The forecast raise is modest in absolute terms — the midpoint moved up by roughly $50 million — but it comes with a structural shift in how Synopsys plans to charge customers. Ghazi told Reuters the company is working on new agreements where large customers pay more for AI-powered design tools and, separately, pay royalties for each chip manufactured using Synopsys intellectual property.

"AI changing both the balance between a human engineer and agent engineer is an inflection point to have a different conversation with our customers," Ghazi said.

The royalty model is particularly significant. If Synopsys successfully moves from pure software licensing to per-chip royalties, it transforms from a tools company into something closer to an intellectual property licensing business — think ARM Holdings, but for the design process rather than the architecture itself.

Synopsys also announced a board seat for Jesse Cohn, the managing partner of activist investor Elliott Investment Management. Elliott's involvement typically signals pressure for operational efficiency and shareholder returns, and Ghazi described the discussions as "constructive." Translation: Elliott sees room to extract more value, and Synopsys is willing to play ball.

## What This Means for India's Chip Design Army

India has roughly 50,000 semiconductor design engineers — one of the largest concentrations outside the United States. Synopsys itself operates major design centres in Bengaluru, Hyderabad, and Noida, employing thousands of engineers who work on everything from verification to physical design implementation.

The "agent engineer" concept is not about replacing these engineers tomorrow. It's about changing what they do. Today, a verification engineer might spend weeks running simulations to validate a chip design. An AI agent could compress that to hours, with the human engineer reviewing and refining the output rather than generating it from scratch.

For Indian chip designers — whether in Synopsys's Bengaluru office, at Intel's Hyderabad campus, or in the Bay Area offices of Qualcomm and Broadcom — this shifts the career value proposition. The premium moves from execution speed to design judgement. Engineers who can architect solutions and evaluate AI-generated designs will command higher compensation. Engineers whose primary skill is running established workflows will face the same compression that Standard Chartered's back-office workers are experiencing.

The timing intersects with India's broader semiconductor ambitions. The India Semiconductor Mission has approved over $18 billion in chip fabrication and assembly projects. But fabrication without design capability is incomplete, and India's design strength has historically been its ace card. If AI agents absorb the middle layers of chip design, India's competitive position shifts from "we have the most engineers" to "we have the best-trained engineers to work with AI."

## The Hyperscaler Gold Rush

The backdrop to Synopsys's forecast raise is an unprecedented chip design boom. Google's tensor processing units, Amazon's Trainium and Graviton chips, Meta's custom inference accelerators, and Microsoft's Maia AI chip are all designed using Synopsys tools. OpenAI's recently announced partnership with Broadcom for custom silicon will add another massive customer to the pipeline.

Each of these projects requires thousands of engineer-hours and millions of dollars in EDA tool licenses. Synopsys and its rival Cadence Design Systems are the duopoly that controls this market, and both are benefiting from the AI infrastructure build-out.

For NRI engineers and investors, the implications are layered. As an investment, Synopsys shares have risen roughly 30% over the past year, trading at elevated multiples that price in continued AI demand. As a career signal, the "agent engineer" concept should prompt serious reflection about how chip design work will be structured in three to five years. The engineers who adapt — learning to orchestrate AI agents rather than compete with them — will thrive. The rest face a narrowing runway that looks increasingly familiar across every knowledge-work profession."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
