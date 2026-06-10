#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 21:00 UTC run"""
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Just Killed Trump's $100,000 H-1B Fee. The Indian IT Industry Exhaled.",
        "subheadline": "US District Judge Leo Sorokin ruled the fee was an unlawful tax Congress never authorised. TCS, Infosys, and Wipro dodged a bullet that could have reshaped their American delivery model.",
        "slug": make_slug("h1b-100k-fee-struck-down-indian-it-relief"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The $100,000 H-1B fee directly threatened the economic viability of hundreds of thousands of Indian tech workers in America and the companies that employ them. For individual H-1B holders, many of whom are Indian engineers at Google, Microsoft, and Amazon, the fee created existential anxiety about visa renewals. For the IT services firms that move talent between Bangalore and Boston, it would have forced a fundamental rethink of onsite delivery economics.",
        "tags": ["h-1b", "immigration", "indian-it", "trump", "court-ruling", "tcs", "infosys"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-2026"},
            {"name": "Bar and Bench", "url": "https://www.barandbench.com/news/here-is-why-us-court-struck-down-trump-100000-h1b-visa-fee"},
            {"name": "Upstox", "url": "https://upstox.com/news/market-news/stocks/tcs-infosys-hcl-tech-it-stocks-in-focus-as-a-us-court-strikes-down-trump-s-100-000-h-1-b-visa-fee-rule/article-195008/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/2023_H-1B_admissions_by_place_of_birth.svg/1280px-2023_H-1B_admissions_by_place_of_birth.svg.png",
        "image_caption": "H-1B visa admissions by country of birth — India dominates the programme",
        "image_attribution": "Wikimedia Commons",
        "body": """A federal judge in Boston has struck down the Trump administration's $100,000 fee on new H-1B visa petitions, ruling that the president overstepped his constitutional authority by imposing what the court called an unauthorised tax.

US District Judge Leo Sorokin's Monday ruling is the most consequential immigration decision for the Indian technology industry in years. It removes, at least for now, a financial threat that had kept HR departments at TCS, Infosys, Wipro, HCLTech, and Cognizant on edge since the fee was announced last September.

## What the court actually said

Sorokin, an Obama appointee, found that the $100,000 charge met every legal definition of a tax — and that Congress, not the president, holds the exclusive power to levy taxes. The Immigration and Nationality Act gives the executive broad authority to restrict entry of noncitizens, but "none of these terms, by their ordinary meaning, include the power to tax," the judge wrote.

He also cited the Supreme Court's February ruling that struck down Trump's sweeping tariffs under emergency powers. The logic, Sorokin argued, was identical: executive overreach into territory reserved for the legislature.

The ruling vacated the policy in its entirety. The Trump administration has vowed to appeal, with a White House spokeswoman insisting the president has "clear legal authority" over immigration entry conditions. Republican Rep. Mike Kennedy of Utah has already introduced the PROTECT Act, which would codify the $100,000 fee through legislation — the one route the court left open.

## Why the Indian IT industry was holding its breath

India accounts for roughly 72 percent of all H-1B visa holders. The top five Indian IT services companies — TCS, Infosys, Wipro, HCLTech, and Tech Mahindra — are among the programme's heaviest users, deploying thousands of engineers to client sites across the United States each year.

A $100,000-per-petition fee would have been devastating. At scale, the cost would have added hundreds of millions of dollars in annual operating expenses, compressed margins that are already under pressure from weak discretionary spending, and forced a structural shift toward offshore-heavy delivery. Several companies had already begun modelling scenarios where onsite work became economically unviable for mid-tier projects.

Indian IT stocks rallied on the news. The Nifty IT index, which had fallen 25 percent over six months, found a rare catalyst. TCS, Infosys, and HCLTech all saw buying interest on Tuesday.

## The bigger picture for Indian H-1B workers

For the estimated 600,000-plus Indian nationals on H-1B visas in the US, the ruling provides relief but not certainty. The fee specifically targeted new petitions, not renewals, but the policy had created a chilling effect on hiring pipelines. Some companies had paused new visa sponsorships while the legal challenge played out.

The court also found that the government violated the Administrative Procedure Act by implementing the policy without the required notice-and-comment rulemaking. It called the fee "arbitrary and capricious," noting the administration had not considered exemptions for universities, hospitals, or cap-exempt employers — sectors that employ significant numbers of Indian professionals beyond the tech industry.

Meanwhile, a separate legal challenge from the US Chamber of Commerce produced the opposite result in December, with a different judge upholding the fee as lawful. The contradiction makes an appeal almost certain, and the issue could eventually reach the Supreme Court.

## What NRIs should watch next

The PROTECT Act in Congress is the real long-term risk. If codified into law, a $100,000 H-1B fee would be immune to the constitutional objections Sorokin raised. Kennedy's bill also proposes requiring employers to pay foreign workers at least the "prevailing rate or $100,000 base" — a provision that could reshape compensation structures for Indian engineers.

For now, the status quo holds. But the political appetite for restricting skilled immigration has not diminished. Indian professionals in the US should track the appeals timeline closely, and Indian IT companies would be wise to keep their offshore contingency plans warm."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tech Minister Wants a New AI Law. The Current Rulebook Is from 2000.",
        "subheadline": "Ashwini Vaishnaw says the IT Act was written before AI existed and cannot govern it. India is now consulting industry on a dedicated framework, even as its Supreme Court drafts AI rules for courtrooms.",
        "slug": make_slug("india-ai-law-vaishnaw-new-framework-regulation"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's AI regulatory direction matters to NRIs on both sides: Indian-origin AI researchers at Anthropic, Google DeepMind, and OpenAI need to understand how their employer's products will be governed in the world's largest democracy, while Indian AI startups like Sarvam AI and Krutrim need clarity before NRI investors commit capital. A heavy-handed framework could slow India's AI ambitions; an absent one could leave Indian consumers unprotected.",
        "tags": ["ai-regulation", "india-policy", "ashwini-vaishnaw", "supreme-court", "deepfakes", "ai-governance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inc42", "url": "https://inc42.com/buzz/ai-world-very-different-from-it-act-era-new-law-required-ashwini-vaishnaw/"},
            {"name": "Exchange4Media", "url": "https://www.exchange4media.com/digital-news/ai-era-may-need-a-new-rulebook-says-vaishnaw-as-india-reassesses-digital-laws-143628.html"},
            {"name": "Livemint", "url": "https://www.livemint.com/technology/microsoft-says-regulatory-oversight-of-ai-essential-but-not-at-the-cost-of-innovation"},
            {"name": "Bar and Bench", "url": "https://www.barandbench.com/news/lawyers-can-use-ai-supreme-court-releases-draft-regulations-for-use-of-ai-in-courts"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
        "image_caption": "Union IT Minister Ashwini Vaishnaw at an official event",
        "image_attribution": "Wikimedia Commons",
        "body": """India's Union IT Minister Ashwini Vaishnaw has said the country needs an entirely new law to govern artificial intelligence, acknowledging that the 26-year-old Information Technology Act is not equipped to handle the challenges posed by modern AI systems.

"It's a very complex topic," Vaishnaw told PTI in an interview. "Certain things have been done under the IT Act framework, but I do think that there is a requirement for a new law because the world of AI is very different from the world when the IT Act was enacted in 2000."

The statement is the clearest signal yet that India's government is moving beyond piecemeal amendments toward a dedicated AI governance framework — a shift with significant implications for the country's booming AI startup ecosystem, its IT services giants, and the tens of thousands of Indian-origin researchers working at frontier AI labs globally.

## The gap between the law and the technology

India currently has no standalone AI legislation. The government has relied on tinkering with the IT Act through advisories and amendments — most recently in February, when it tightened rules requiring platforms like X and Instagram to remove deepfake content within three hours of a court or government directive.

The Digital Personal Data Protection Act, enacted in 2023, addresses privacy and consent but says nothing about model accountability, algorithmic bias, or AI-generated harms. That gap is growing wider by the month. Anthropic's Mythos model, which India gained access to under Project Glasswing, can identify software vulnerabilities faster than human security teams. India's own Sarvam AI and Krutrim are building large language models trained on Indian languages. None of this existed when the IT Act was drafted.

Vaishnaw said the government is consulting with industry stakeholders to determine the right regulatory approach. "Our objective and approach will be to balance innovation and regulation in a manner that innovation keeps happening, while our citizens remain safe," he added.

## The Supreme Court moves first

While the legislature deliberates, India's judiciary has already acted. On June 3, the Supreme Court's AI Committee released draft regulations governing the use of AI tools across Indian courts. The document is narrowly focused — it covers judges, lawyers, and court proceedings — but its principles have broader implications.

The draft permits AI-assisted legal research, drafting, translation, and case management. But it draws a firm line: judicial functions like bail decisions, sentencing, outcome prediction, and witness credibility assessment must remain entirely human-led. Lawyers who use AI to prepare pleadings must disclose it. Anyone who submits fabricated AI-generated material bears full personal responsibility and cannot blame the technology.

The rules were prompted by real embarrassments. In February 2025, an Income Tax Appellate Tribunal in Bengaluru withdrew an order after it cited AI-generated judicial precedents that did not exist. A Karnataka High Court order similarly referenced phantom Supreme Court judgments. By March 2026, fabricated citations surfaced in insolvency proceedings at the Supreme Court itself.

Comments on the draft are open until June 20, and the regulations would apply to the Supreme Court, High Courts, subordinate courts, tribunals, and statutory commissions nationwide.

## Microsoft weighs in

The timing is not coincidental. Microsoft, whose India operations generated revenue of ₹29,566 crore in FY25, has publicly backed India's regulatory approach. The company's stance — that oversight is essential but should not stifle innovation — aligns with the government's stated position.

In April, the Centre constituted an inter-ministerial AI governance and economy group (AIGEG) to examine AI's impact on education, employment, and underage users. Livemint reported that the government was shifting away from its earlier "light-touch, innovation-first" stance toward something more active.

## What this means for the diaspora

For Indian-origin AI professionals in the US and Europe, India's regulatory direction is no longer an abstract policy debate. It determines whether their employers — Google, Anthropic, OpenAI, Meta — can deploy frontier models in the Indian market without running afoul of compliance requirements that have not yet been written.

For NRI investors eyeing India's AI startup scene, the uncertainty cuts both ways. A well-designed framework could legitimise the sector and attract institutional capital. A poorly designed one — or one that takes years to materialise — could push Indian AI companies to incorporate and scale elsewhere, much as fintech startups once decamped to Singapore over regulatory ambiguity.

The challenge for Vaishnaw and his team is designing rules that address deepfakes, model bias, cybersecurity risks, and data governance without replicating the compliance burden that has slowed AI deployment in the European Union. India's instinct has historically been to move fast and regulate later. With AI, the minister is conceding, later has arrived."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's GCCs Just Out-Hired the Entire IT Services Industry. Again.",
        "subheadline": "Global capability centres added nearly 200,000 net employees in FY26, almost double the 110,000 added by TCS, Infosys, and their peers. The structural power shift in Indian tech talent is accelerating.",
        "slug": make_slug("gcc-outhire-it-services-india-talent-shift"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The GCC boom is reshaping career decisions for Indian tech professionals on both sides of the Pacific. NRIs considering a return to India now face a talent market where Google's Hyderabad centre, JPMorgan's Bangalore hub, and Goldman's engineering campus compete directly with TCS and Infosys for the same candidates — often at higher pay. For Indian engineers in the US on H-1B visas weighing a move home, GCCs offer multinational compensation structures that narrow the salary gap.",
        "tags": ["gcc", "global-capability-center", "indian-it", "hiring", "tcs", "ai-talent", "india-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/india-gccs-lead-ai-cloud-hiring/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-sees-rising-share-of-revenue-from-bfsi-in-fy26/article69653372.ece"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-launches-dedicated-business-to-build-ai-native-global-capability-centres/article69654781.ece"},
            {"name": "ET Edge Insights", "url": "https://etedge-insights.com/technology/gccs-in-the-ai-era-a-future-ready-operating-model/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35175238/pexels-photo-35175238.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Modern corporate towers in Hyderabad, a major hub for global capability centres in India",
        "image_attribution": "Pexels",
        "body": """For the third consecutive fiscal year, India's global capability centres have added more employees than the country's entire IT services industry. The gap is no longer marginal — it is becoming structural.

GCCs added nearly 200,000 net employees in FY26, almost twice the 110,000 added by IT services firms including TCS, Infosys, Wipro, HCLTech, and Tech Mahindra, according to TeamLease Digital data cited by The Economic Times. India now hosts over 1,700 GCCs employing more than 1.9 million people. The IT services sector still employs more in absolute terms, but the direction of the trend is unmistakable.

## What is driving the shift

Three forces are converging. First, multinational companies want direct control over their AI, cloud, and cybersecurity work. When JPMorgan builds fraud detection models or Goldman Sachs architects its trading platforms, it increasingly wants those engineers on its own payroll in Bangalore, not outsourced to Infosys. The sensitivity of AI workloads — training data governance, model accountability, intellectual property — makes in-house ownership more attractive than third-party delivery.

Second, GCCs are no longer support centres. The "back office" label that defined them a decade ago is obsolete. Google's Hyderabad campus runs core Search and Cloud engineering. Microsoft's India Development Centre contributes to Azure and Copilot. Walmart Labs in Bangalore builds the e-commerce stack that serves American consumers. These are product teams, not cost centres.

Third, the AI talent war favours GCCs. TeamLease data shows GCCs now account for 30 to 35 percent of all AI-related hiring in India. Mid-to-senior AI roles have surged from 60 percent of GCC hiring in 2023 to over 77 percent in FY26. A Quess Corp analysis estimated a 38 to 42 percent gap in AI and data skills across the GCC ecosystem — meaning demand is outstripping supply even at current hiring velocity.

## The IT services industry responds

TCS, reading the room, launched a new business unit last week dedicated to helping enterprises build and scale AI-native GCCs. Called the Global Value & Innovation Centres (GVIC) unit, it offers services across the full GCC lifecycle — from strategy and setup to AI-led transformation.

The move is shrewd and slightly desperate. If multinational companies are going to build their own technology centres in India regardless, TCS would rather be the architect than the casualty. CEO K. Krithivasan framed it as combining "TCS' deep experience across the GCC lifecycle with our strengths in AI, engineering, talent and operations."

It is also an implicit concession. The traditional model — where Indian IT firms hired hundreds of thousands of engineers, trained them, and deployed them to Western clients — is being challenged from two directions simultaneously. AI agents are automating the lower-skill tiers (TCS Chairman Chandrasekaran said last week that the company expects to eventually have as many AI agents as human employees). And GCCs are absorbing the higher-skill work that the industry would prefer to keep.

## Why NRIs should pay attention

For Indian professionals in the US weighing a return to India, the GCC boom has materially changed the calculus. A decade ago, moving back meant accepting a steep pay cut and a less interesting technology stack. Today, Google India, Amazon India, and JPMorgan India offer compensation that narrows the gap considerably — especially when adjusted for purchasing power — and the engineering challenges are often identical to what the same companies offer in Seattle or New York.

The competition for talent has also pushed GCC salaries upward across the board. Deloitte reported that demand for AI specialists in India has risen more than 300 percent since 2024, and much of that demand originates from GCCs willing to pay premiums that IT services firms cannot match.

For NRI investors, the implications are subtler. Indian IT services stocks have been hammered — the Nifty IT index is down 25 percent over six months, with Wipro hitting a 52-week low. The market is pricing in a structural decline in the outsourcing model. Whether firms like TCS and Infosys can reinvent themselves as GCC enablers, AI platform providers, and enterprise consultants — rather than body shops — will determine whether these stocks represent a value trap or a turnaround opportunity.

## The talent gap that could stall everything

The constraint is not demand — it is supply. India produces enormous numbers of engineering graduates, but the specific skills GCCs need (agentic AI architectures, cloud-native platform engineering, cybersecurity operations, and product management) remain scarce. The 38-to-42 percent skills gap identified by Quess Corp is a real bottleneck.

India's next phase of GCC growth depends less on whether multinationals want to build in India — they clearly do — and more on how quickly the country's education system and upskilling infrastructure can produce the professionals these centres need. For now, the GCCs are winning the hiring war. Winning the talent war is harder."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
