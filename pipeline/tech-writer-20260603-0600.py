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
        "headline": "Apple Is About to Hand Siri's Brain to Sundar Pichai's Google. Indian Engineers Built Both Sides.",
        "subheadline": "WWDC 2026 will unveil a rebuilt Siri powered by a custom 1.2 trillion-parameter Gemini model. Apple is paying Google roughly $1 billion a year for the privilege — and Indian professionals sit at the centre of both companies making it work.",
        "slug": make_slug("apple-wwdc-siri-google-gemini-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers at Google built much of Gemini's foundation model architecture. Indian engineers at Apple are integrating it into iOS. Indian app developers in Bengaluru and Hyderabad will need to rearchitect their apps for App Intents. For the 500,000+ Indian professionals employed across both companies, this deal defines the next cycle of their work.",
        "tags": ["apple", "google", "gemini", "siri", "wwdc", "ios-27", "sundar-pichai", "ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/01/apples-wwdc-is-june-8-heres-the-1-announcement-tha/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/02/google-gemini-spark-apple-intelligence/"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/3254628/wwdc-what-can-developers-expect.html"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/apples-bid-to-turn-siri-into-a-persistent-ai-companion/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/30530426/pexels-photo-30530426.jpeg",
        "body": """When Apple CEO Tim Cook takes the stage at WWDC on June 8, the most consequential announcement will not be a new operating system or a hardware refresh. It will be a concession: Apple's rebuilt Siri will run on Google's Gemini, a 1.2 trillion-parameter model that dwarfs anything Cupertino has built on its own.

Bloomberg's Mark Gurman first reported the arrangement earlier this year. Apple is paying Google roughly $1 billion annually for access to a custom version of Gemini that handles the heavy reasoning — summarising, planning, multi-step task execution — while Apple routes data through its Private Cloud Compute servers to keep user information walled off from Google's systems. Tim Cook confirmed the partnership's progress during Apple's fiscal second-quarter earnings call: "The collaboration with Google is going well. We are happy with where things are."

## What Changes for Siri

The new Siri will be unrecognisable from the assistant that has frustrated iPhone users for over a decade. A standalone Siri app will offer a chat-style interface with message bubbles, conversation history, and options to auto-delete chats after 30 days, one year, or never. Users will be able to swipe down from the Dynamic Island to access a "Search or Ask" hub that pulls context from on-device data — emails, photos, calendars, notes — and routes complex queries to the cloud.

Citi analyst Atif Malik laid out what investors expect: "Siri will handle multi-step requests, understand personal data, analyse on-screen content, generate emails or messages using both web and device context, and surface rich card-based results." Perhaps most significantly, Apple will reportedly allow users to choose between Google Gemini, OpenAI's ChatGPT, and Anthropic's Claude through the new interface, turning Siri into an AI orchestration layer rather than a single locked-in model.

For developers, the shift is structural. Apple is overhauling its App Intents framework, which requires apps to wrap their features into semantic structures for Siri to invoke. New Foundation Models APIs will let developers run Apple Intelligence capabilities — summarisation, text generation, image analysis — directly on-device, offline, at no token cost.

## The Indian Talent at the Core

The partnership's execution depends heavily on Indian engineering talent on both sides. At Google, Indian-origin researchers and engineers have been central to building the Gemini model family since its inception. DeepMind and Google Brain, both now unified under Google DeepMind, employ hundreds of Indian-origin AI researchers working on the foundational architectures that Gemini uses. At Apple, Indian engineers across Cupertino, Austin, and Hyderabad are deeply embedded in the iOS, machine learning, and Siri teams integrating these capabilities.

The developer ecosystem matters just as much. India is home to the second-largest population of iOS developers in the world, behind only the United States. The App Intents redesign means every serious Indian app development shop — from Bengaluru startups building fintech apps to Hyderabad teams working on enterprise solutions — will need to rearchitect their applications to work with the new Siri. Those that move early get distribution advantages; those that lag risk irrelevance in a world where users interact with apps through an AI intermediary rather than tapping icons.

## Why NRIs Should Pay Attention

For the estimated 500,000-plus Indian professionals employed across Apple and Google in the United States, this partnership reshapes internal priorities. Teams are being rebalanced around AI integration, and the engineers who understand both mobile operating systems and large language model deployment are the ones being promoted and retained. In an era when Google has cut H-1B approvals from 5,100 to 2,200 and Amazon from 6,100 to 4,300, the AI-adjacent roles at both companies remain relatively insulated.

The Verge's Jay Peters recently tested Gemini Spark's agentic capabilities — asking it to draft an email compiling grocery spending from a spreadsheet it had to find on its own — and called the results "scarily good." If that performance carries over to Siri on iOS 27, Apple's 2.2 billion active devices become the largest deployment of agentic AI in consumer history.

For Indian investors, this is a $1 billion annual transfer from Apple's balance sheet to Alphabet's revenue line. For Indian engineers, it is the clearest signal yet that the AI stack is not a single-company affair — it is a web of dependencies, and the professionals who sit at its intersections hold the leverage."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sridhar Vembu Told India to Stop Consuming Everyone Else's AI. Then He Showed What Zoho Is Building Instead.",
        "subheadline": "At ImagiNxt 2026 in Mumbai, the Zoho founder argued that India cannot remain a customer of Western AI platforms. His company has filed 30 patents from rural R&D labs and is investing in semiconductors, quantum sensing, and advanced materials.",
        "slug": make_slug("sridhar-vembu-zoho-sovereign-ai-imaginxt-semiconductors"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Vembu's argument is directly relevant to NRI investors considering where to put capital in India's tech ecosystem. Zoho's 100 million+ users include a large diaspora base. His rural R&D model and semiconductor ambitions offer an alternative thesis to the Silicon Valley dependency that most Indian professionals live within.",
        "tags": ["zoho", "sridhar-vembu", "sovereign-ai", "india-tech", "semiconductors", "rural-innovation", "imaginxt"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Local Business News", "url": "https://newslocalbiz.com/imaginxt-2026-industry-leaders-advocate-indigenous-ai-deeptech-innovation/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/india-showcase-120-deep-tech-startups-bharat-innovates-2026"},
            {"name": "DQ India", "url": "https://www.dqindia.com/news/zoho-launches-vikra-and-zoho-iot-planning-semiconductor-initiatives-7092828"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8438994/pexels-photo-8438994.jpeg",
        "body": """When Sridhar Vembu walked onto the stage at ImagiNxt 2026 in Mumbai's Jio World Convention Centre on June 1, he did not begin with a product demo. He began with a warning.

"India cannot afford to remain only a consumer of global technology platforms," the Zoho founder and chief scientist told an audience of founders, policymakers, and investors. "The country has the talent and capability to build its own long-term technology and AI ecosystems, provided we invest patiently in research, engineering, and indigenous innovation."

It is a message Vembu has been refining for years, but the timing carries new weight. Global AI server costs have surged three to four times over the past six months, driven by relentless demand for GPU capacity. The companies building frontier models — OpenAI, Google, Anthropic, Meta — are headquartered in Silicon Valley, running on American chips, trained on data centres financed by American capital. India, for all its software talent, remains overwhelmingly a consumer of these platforms.

## What Zoho Is Actually Doing About It

Vembu's argument would be empty rhetoric without evidence. Zoho has filed more than 30 patents in recent years, many developed through its rural R&D teams in Tamil Nadu — an unusual setup for a company with more than 100 million users and operations in over 150 countries. The company runs significant research operations from Tenkasi, a small town in southern Tamil Nadu that most tech executives could not locate on a map.

Beyond software, Zoho is making bets that look eccentric for a SaaS company. The company is investing in semiconductors through its stake in Signalchip, a fabless semiconductor design firm. It is exploring quantum sensing and advanced materials. It is building computer vision systems and audio-video AI capabilities in-house. Vembu has described this as Zoho's attempt to build competencies across the entire technology stack — from chips to software to the interfaces that sit on top.

The rural dimension matters. Zoho's Tenkasi and other non-metro R&D centres are part of Vembu's thesis that deep technology innovation does not require Bengaluru rents or Silicon Valley salaries. The model has been quietly validated: Zoho remains profitable, privately held, debt-free, and growing faster in India than in any other market. It generates roughly $1 billion in annual revenue without ever having taken a dollar of venture capital.

## The Sovereign AI Question

Vembu's call for sovereign AI echoes a broader movement gaining momentum across India's technology establishment. The ImagiNxt conference itself was hosted by Maharashtra Tourism and featured conversations around indigenous R&D, private space innovation, drone technologies, and the evolution of India's deep-tech ecosystem. Days later, India's Ministry of Education will showcase 120 deep-tech startups at Bharat Innovates 2026 in Nice, France — described as the country's most ambitious attempt to position itself as a builder of frontier technology rather than a back-office for the world's software.

The sovereign AI argument has practical urgency. India's UPI now processes over 23 billion transactions monthly. Its digital public infrastructure — Aadhaar, DigiLocker, ONDC — runs on a scale that few Western systems match. But the AI models that will increasingly govern search, commerce, customer service, healthcare diagnostics, and financial decision-making are built elsewhere, trained on data that reflects Western contexts, and priced in dollars.

## Why NRIs Should Care

For the Indian diaspora, Vembu's stance challenges a comfortable assumption: that working at Google, Microsoft, or Meta is the highest-value deployment of Indian technical talent. His counter-argument is that India needs its own technology foundations, and that the professionals who help build them may ultimately create more durable value than those optimising advertising algorithms in Mountain View.

For NRI investors, Zoho represents something unusual in the Indian tech landscape — a large, profitable, privately held technology company with no near-term IPO plans and no interest in the growth-at-all-costs playbook that defined the Indian startup boom of the 2010s. Its semiconductor and deep-tech investments are long-cycle bets, unlikely to show returns for years. But if India's Semiconductor Mission succeeds, and if the country builds genuine capacity in AI model development, the companies that invested early in indigenous R&D will hold structural advantages.

Vembu ended with a point that sounded less like a tech executive and more like an industrialist. "We need to invest patiently," he said. In an industry that measures success in quarterly earnings and Series B valuations, patience may be the most radical position of all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS, Infosys, and Wipro Just Doubled Their Microsoft Copilot Licences. The Indian IT Workforce Is Being Rewired.",
        "subheadline": "India's three largest IT services firms have doubled their AI copilot deployments in six months, with daily active usage rates above 85 per cent. The shift signals a structural change in how 1.5 million Indian engineers do their jobs.",
        "slug": make_slug("tcs-infosys-wipro-copilot-ai-licences-doubled"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For the hundreds of thousands of NRIs who built careers at or alongside these companies, the Copilot rollout signals a fundamental shift in the Indian IT operating model. Engineers who trained juniors and managed large teams now work alongside AI tools that handle code generation, documentation, and analysis. The companies that employ the most H-1B holders in the United States are redefining what their workers actually do.",
        "tags": ["tcs", "infosys", "wipro", "microsoft-copilot", "ai-adoption", "indian-it", "enterprise-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/technology/tech-news/tcs-infosys-wipro-double-copilot-ai-licences-microsoft-employees-six-months-11748802037025.html"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/india-incs-fresher-hiring-sees-steep-drop-amid-ai-adoption"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/featured-stories/gccs-lead-the-hiring-story-as-ai-talent-and-emerging-cities-outpace-traditional-job-hubs-60983.htm"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg",
        "body": """India's three largest IT services companies have quietly doubled the number of employees using Microsoft's AI-powered Copilot tool within six months. The numbers, disclosed as part of a Microsoft release, reveal adoption rates that would make most enterprise software deployments look glacial.

At Infosys, 91 per cent of Copilot-licenced employees use the tool every month. At Wipro, the figure is 95 per cent. At TCS, 86 per cent of licenced associates use Copilot in their daily work — for HR functions, sales processes, software development, maintenance, and coding. These are not pilot programmes or innovation-lab experiments. These are production deployments touching hundreds of thousands of engineers across three companies that collectively employ more than 1.5 million people.

## What the CEOs Are Saying

The statements from all three CEOs carry a uniformity that suggests coordinated strategic positioning rather than casual endorsement. "This is an integral part of building an AI-first culture and shaping the Human + AI operating model of the future," said TCS CEO K. Krithivasan. "By embedding Agentic AI into the flow of work, our employees are redefining how work gets done."

Infosys CEO Salil Parekh kept it simpler: "The real opportunity with AI lies in how deeply it is embedded into everyday work." Wipro's Srini Pallia framed it as operational strategy: "At Wipro, we are embedding AI into everyday work to create real enterprise advantage — unlocking productivity, sharpening execution, accelerating innovation."

The language matters because it reveals something the companies have been reluctant to say directly: AI is not supplementing their workforce. It is restructuring it. When every developer has a Copilot generating code drafts, reviewing pull requests, and writing documentation, the value of a junior engineer who does those tasks manually drops to near zero.

## The Fresher Hiring Collapse

The Copilot rollout does not exist in isolation. It arrives alongside a sharp decline in fresher hiring across Indian IT. At Infosys, employees aged 30 and below now make up roughly 50.7 per cent of its 3.28 lakh workforce — the lowest proportion in 15 years, down from two-thirds as recently as FY18. At TCS, employees under 30 account for about 48 per cent of its workforce, and the company ended FY26 with 23,460 fewer employees than the previous year, partly due to a layoff exercise that affected around 12,000 workers.

Sushovon Nayak, lead IT analyst at Anand Rathi, put it directly: "Selective IT firms are looking to hire fewer young people, as automation tools are reducing the need for young graduates unless they have specialised skill sets." Companies are increasingly favouring employees between 30 and 40 who can be upskilled and bring deeper client-ecosystem familiarity.

Peter Bendor-Samuel of Everest Group added a dimension that Indian IT firms prefer not to discuss publicly: "With the new emerging AI talent, the tech services firms are having to hire employees with a higher calibre, which is harder to source, and in general, do not view the tech services firms as their first choice to work at."

## The Diaspora Impact

For the Indian diaspora, these shifts carry immediate professional implications. TCS, Infosys, and Wipro are among the largest sponsors of H-1B visas in the United States. When these companies restructure their operating models around AI tooling, the roles available to visa-holding employees change accordingly. The era of large teams of junior engineers deployed on maintenance contracts — the bread-and-butter business model of Indian IT services — is compressing.

The opportunity, for those who adapt, is significant. The same Naukri JobSpeak report that showed flat overall hiring in May 2026 revealed a 20 per cent surge in Global Capability Centre recruitment in Hyderabad. GCCs — the India-based technology arms of multinational corporations — are hiring aggressively for AI development, analytics, and machine learning roles. The hiring is shifting from Indian IT services firms to multinational centres that pay higher salaries and work on products rather than services contracts.

Phil Fersht of HFS Research argues the Copilot effect will be visible primarily in productivity acceleration. "Developers will generate code faster, consultants will produce deliverables more efficiently, analysts will summarise and synthesise information quicker," he said. Gartner's Anushree Verma offered a strategic frame: training engineers on Copilot is not about headcount reduction but about building the capability to sell AI-powered services to clients. "That is what's pushing adoption of Copilot and other such tools at IT firms."

The bottom line for Indian IT professionals in the US and India: the companies are not shrinking. They are redesigning themselves for a world where fewer people, equipped with better tools, can deliver more output. The question is which workers end up on which side of that equation."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
