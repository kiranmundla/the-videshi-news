#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

body1 = """Noam Shazeer is leaving Google for OpenAI. If the name does not register, the resume should: he is one of eight authors of "Attention Is All You Need," the 2017 paper that introduced the transformer — the architecture under ChatGPT, Gemini, Claude, and every large language model an Indian engineer has shipped a feature on in the last three years.

His exit, announced on X on Wednesday, is not just another senior departure. It is the most expensive rehire in tech history walking back out the door. Google paid roughly $2.7 billion in 2024 to license technology from Character.AI, the startup Shazeer co-founded after leaving Google in 2021. Inside Google, that deal was widely understood as the price of getting him back to co-lead Gemini. Less than two years later, he is gone — to the company that turned his own paper into ChatGPT.

## The talent war just got more expensive

For the Indian diaspora that staffs the engine rooms of American AI, this is the story that matters more than any product launch. The fight among Google, OpenAI, Meta, Anthropic, and xAI is no longer about models. It is about people, and the people command sums that look like acquisitions.

Meta has reportedly dangled nine-figure packages to pull researchers from rivals. OpenAI, which confidentially filed for an IPO earlier this month, is now hiring the very people Google most wanted to keep. The going rate for a frontier researcher has detached from anything resembling a normal salary band.

A large share of the talent inside those labs is Indian-origin — research scientists, infrastructure leads, and applied-AI engineers who came through the IITs, did graduate work in the US, and now sit on H-1B or green-card tracks. When the labs bid against each other, these are often the people being bid on.

## Why an NRI engineer should read the fine print

The headline is glamorous. The mechanics are not. For an Indian engineer at Google DeepMind or Microsoft AI, a competing offer from OpenAI or Anthropic is not as simple as a bigger number. Visa status turns a job change into a legal event.

An H-1B holder who switches employers needs the new company to file a transfer petition; the worker can usually begin once the petition is receipted, but the clock and the paperwork are real. Anyone on an O-1 "extraordinary ability" visa — increasingly common for senior researchers — faces a fresh petition tied to the new role. And equity, the part of these packages that actually creates wealth, often vests over four years, which means leaving early forfeits the very upside that justified the move.

Shazeer can walk because he is already rich and already a citizen of the labor market's top tier. The Indian researcher two levels down, on a visa, weighing a 40% raise against an unvested grant and a pending green card, is playing a very different game with the same chessboard.

## The deeper signal

There is a structural lesson buried in the churn. Google invented the transformer and then watched OpenAI commercialize it. Now it is watching one of the inventors leave for the company that did. Institutional knowledge does not stay put; it follows the best offer and the most interesting problem.

For the diaspora, that mobility cuts both ways. It is why Indian engineers can build careers that ladder upward across companies that would have been lifetime employers a generation ago. It is also why no single employer — not even one willing to spend $2.7 billion — can count on keeping the talent it pays for.

The labs will keep bidding. The packages will keep climbing. And the engineers watching from the middle of the org chart, many of them Indian, will keep doing the quiet math that the headlines never show: what a move is worth once you subtract the visa risk and the equity left on the table.

What is next is an OpenAI IPO that will mint a new class of paper millionaires, many of them on visas, and a Google forced to prove it can build the next Gemini without the man it paid a fortune to bring home."""

body2 = """The number that should worry every Indian software professional is not a layoff figure. It is a hiring figure. India's active technology job openings have fallen to 93,000 — a 28-month low, down 14% in a single month and 17% from a year ago, according to staffing firm Xpheno's June outlook.

Read alongside a second statistic, it becomes a warning. More than 56,000 professionals from 20 major tech firms — including Meta, Amazon, and Oracle — are now actively job-hunting, up from about 12,000 a month earlier and roughly 5,000 six months ago. Demand is collapsing at the exact moment supply is surging. That is not a soft patch. That is a market clearing out.

## The fresher's door is closing fastest

The most brutal part of the data sits at the entry level. Openings for talent with up to two years of experience fell 44% year-on-year, to just 10,000 in June from 13,000 in May. Senior-level openings, by one reading of the report, are down even more sharply.

For decades, the deal was simple: India's engineering colleges produced graduates, the big IT services firms — TCS, Infosys, Wipro, HCLTech, Cognizant — absorbed them by the tens of thousands, trained them, and put them on client projects, many of them in the US on H-1B or L-1 visas. That conveyor belt is jamming. The firms are no longer hiring by volume. They are hiring for productivity.

## Why this lands on a New Jersey kitchen table

The diaspora connection is direct and generational. The Indian American family in Edison or Fremont often has a younger sibling, a cousin, or a nephew finishing an engineering degree in Hyderabad or Pune, expecting the same path the elder generation took: campus placement, a few years at an IT major, then an onsite posting to the US.

That path is narrowing. The IT services cohort, historically the single largest consumer of Indian tech talent, is driving most of the decline. AI coding assistants now do a meaningful share of the routine work that justified armies of junior engineers. When the bottom rung of the ladder shrinks in India, the supply of future H-1B candidates shrinks with it — and so does the family reunification math that brought so many here in the first place.

## The one bright spot is not the obvious one

There is a hedge inside the gloom: Global Capability Centres. These are the in-house technology arms that multinationals — banks, retailers, chipmakers, and yes, the same American tech giants doing layoffs — run inside India. GCC hiring has been bucking the broader trend, growing even as IT services demand falls.

The shift is telling. Companies increasingly want to own their Indian engineering talent directly rather than rent it through a services contractor. For a young engineer in Bengaluru, a GCC job at an American multinational can be more stable, better paid, and more technically interesting than a traditional services role — and it sometimes comes with an internal path to a US transfer that does not run through the H-1B lottery.

## What the diaspora investor and worker should watch

Two things. First, the earnings of the IT majors, due over the coming weeks, will confirm whether the hiring freeze is cyclical or structural. If TCS and Infosys signal another year of muted net headcount additions, the 93,000 figure is a floor, not a trough.

Second, the AI-skills premium. India's AI talent pool is projected to nearly double by 2027, by one industry estimate, to around 16% of the global total. The engineers who pivot into AI, machine learning, and the GCC ecosystem will be fine. The ones waiting for the old conveyor belt to restart may be waiting a long time.

For the NRI watching from abroad, the uncomfortable truth is that the pipeline that built the Indian American tech community is being re-plumbed in real time. The next generation will still come — but fewer of them, later, and through different doors than their parents did."""

body3 = """The engineers Intel is letting go this year are not the kind that show up in a generic "tech layoff" recap. They are RTL designers, physical-design engineers, verification leads, and process integration specialists — the deep silicon talent the chip industry spent years failing to hire fast enough. Now tens of thousands of them are on the market at once, and where they land will reshape the global map of who builds chips, including India's place on it.

Intel's restructuring under CEO Lip-Bu Tan has cut its workforce from roughly 125,000 toward 75,000, concentrated in Hillsboro, Chandler, Folsom, and Santa Clara. That displaced pool is being absorbed by TSMC's Arizona fabs, the hyperscalers building custom silicon, and a wave of AI-chip startups. For the Indian diaspora that has quietly become a backbone of American semiconductor engineering, this is a once-in-a-cycle reshuffle.

## The diaspora is over-indexed in chips

Walk any chip design floor in the Bay Area, Austin, or Portland and the Indian-origin presence is hard to miss. Memory leader Micron is run by Sanjay Mehrotra. Hardware networking giant Arista is run by Jayshree Ullal. Below the C-suite, Indian engineers fill the physical-design and verification roles that the layoffs are now flooding into the open market.

That concentration makes the Intel unwind a deeply personal event for the community. An H-1B holder laid off from a chip role faces a 60-day grace period to find a new sponsor or leave the country — a brutal clock for a specialist whose skills, while rare, match only a handful of employers. The very specificity that makes a verification lead valuable also makes the job search narrow.

## India is the other side of the trade

Here is where the diaspora story bends back to the homeland. The same week the layoff data circulated, India's semiconductor push reached a milestone: Micron's $2.75 billion assembly and test facility in Sanand, Gujarat, is in commercial production, shipping its first made-in-India memory modules to Dell for locally built laptops. It is one of ten projects now moving under the India Semiconductor Mission, with Tata's fab in Dholera and compound-semiconductor plants following.

India is building the demand for exactly the talent America is shedding. For a displaced Indian-origin chip engineer weighing a shrinking US market against a 60-day visa clock, the return-to-India calculation has never looked more rational. Companies staffing the Gujarat plants want process and packaging expertise — and a generation of engineers who learned it at Intel and Micron in the US is suddenly available.

## Why an NRI should care beyond the job market

This is not only a careers story; it is an investment and identity one. The diaspora has long sent money home as remittances. The semiconductor build-out offers something different: a chance to send expertise home, or to back it as investors as India tries to climb from assembly and testing toward actual fabrication.

The gap is real. Sanand does assembly, test, and packaging — the back end of the chip supply chain — not the front-end wafer fabrication that defines true semiconductor sovereignty. Closing that gap requires precisely the front-end process talent now leaving Intel. Whether India can attract enough of it, fast enough, is the question that determines if the "China-plus-one" chip story is real or rhetorical.

## What to watch next

Three signals. First, how quickly TSMC Arizona and the AI-silicon startups absorb the Intel pool — a fast absorption keeps talent in the US, a slow one pushes it toward India and elsewhere. Second, whether the Indian fabs move beyond packaging toward fabrication, which would create roles senior enough to pull diaspora veterans back. Third, the H-1B environment, which remains the single biggest variable: every tightening of the visa regime makes the India option more attractive to the engineers America trained.

If oil regulated the last century, microchips will regulate this one — and the people who design them are, right now, deciding which country they will do it in. A surprising number of them carry Indian passports, or remember when they did."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Paid $2.7 Billion to Bring Noam Shazeer Home. He Just Left for OpenAI.",
        "subheadline": "The man who co-invented the transformer is changing sides again — and the AI talent war he embodies is quietly reshaping careers for thousands of Indian researchers on visas.",
        "slug": make_slug("noam-shazeer-google-openai-ai-talent-war-indian-researchers-visas"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The AI talent war minting nine-figure offers runs on Indian-origin researchers, but for those on H-1B and O-1 visas, switching labs is a legal and financial gamble that the headline numbers hide.",
        "tags": ["ai", "openai", "google", "indian-tech", "h1b", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/googles-gemini-co-lead-noam-shazeer-join-openai-2026-06-17/"},
            {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/17/google-gemini-co-lead-noam-shazeer-leaves-for-openai.html"},
            {"name": "Startup Fortune", "url": "https://startupfortune.com/noam-shazeer-openai/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Googleplex-SignIn.jpg",
        "image_caption": "The Google sign at the Googleplex headquarters in Mountain View, California",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tech Hiring Just Hit a 28-Month Low. The Conveyor Belt That Built the Diaspora Is Jamming.",
        "subheadline": "Active openings have fallen to 93,000 even as 56,000 professionals hunt for jobs — and the entry-level door, the one that fed a generation of H-1B careers, is closing fastest.",
        "slug": make_slug("india-tech-hiring-28-month-low-freshers-it-services-h1b-pipeline"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The campus-to-IT-major-to-US-onsite path that brought a generation of Indian Americans here is narrowing, reshaping the future H-1B pipeline and the family-reunification math behind it.",
        "tags": ["indian-tech", "it-services", "layoffs", "h1b", "hiring", "tcs-infosys"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Xpheno / People Matters", "url": "https://www.peoplematters.in/news/talent-acquisition/indias-tech-hiring-drops-to-28-month-low-as-active-openings-fall-to-93000"},
            {"name": "Inshorts / Economic Times", "url": "https://inshorts.com/en/news/over-56000-indian-techies-from-major-firms-looking-for-jobs-amid-mass-layoffs-report"},
            {"name": "BizzBuzz", "url": "https://www.bizzbuzz.news/technology/job-vacancies-in-indian-it-industry-continues-to-fall-hit-28-month-low-in-june"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg/1280px-Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg",
        "image_caption": "Aerial view of the glass pyramid at the Infosys campus in Bengaluru, India",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Is Shedding 25,000 Chip Engineers. For the Indian Diaspora, the Question Is Whether They Go Home.",
        "subheadline": "The deep silicon talent America is laying off is exactly what Gujarat's new fabs need — and a 60-day visa clock is making the return-to-India math look rational.",
        "slug": make_slug("intel-layoffs-chip-engineers-india-semiconductor-mission-diaspora-talent"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin engineers are over-represented in US chip design, so Intel's mass layoffs collide directly with India's semiconductor build-out — turning a 60-day H-1B grace period into a return-to-India decision.",
        "tags": ["semiconductors", "intel", "india-semiconductor-mission", "micron", "h1b", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "KORE1", "url": "https://www.kore1.com/intel-layoffs-2026-where-displaced-chip-talent-is-landing/"},
            {"name": "CRN Asia", "url": "https://www.crnasia.com/news/2026/micron-opens-indias-first-semiconductor-assembly-and-test-facility-in-gujarat"},
            {"name": "Windows Report", "url": "https://windowsreport.com/intel-confirms-major-job-cuts-targets-24500-layoffs-by-end-of-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/V11-wafer-dc328.jpg/1280px-V11-wafer-dc328.jpg",
        "image_caption": "A semiconductor wafer patterned with integrated circuit dies before packaging",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
