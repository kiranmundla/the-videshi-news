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

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

body1 = """When the University of Florida Research Foundation read out its 2026 list of honored professors this spring, thirty-four names made the cut — the university's most productive faculty, drawn from a process that begins with departmental nominations and ends with college leadership weighing publications, grants, patents, and influence. Four of those names traced the same long arc: from a classroom in Kolkata, Calcutta, or New Delhi to a laboratory in Gainesville.

Kshitij Khare, Desika Narayanan, Jasmeet Judge, and Paramita Chakrabarty are not a delegation. They did not arrive together or work in the same field. What links them is a biography the Indian diaspora knows by heart — the one that starts at a premier Indian institution and ends at an American research frontier — and the quiet fact that, this year, a tenth of one university's top honors went to scholars who began that way.

## Four Fields, One Pipeline

The range is the point. Khare, a professor of statistics, carries the rigor of the Indian Statistical Institute into the abstract territory of high-dimensional covariance estimation and Bayesian computation. He studied at ISI's Kolkata and Delhi campuses, took a PhD at Stanford, and landed at UF — a route that reads like a map of the global market for technical talent.

Paramita Chakrabarty's path was less linear. An associate professor in the College of Medicine, she began her scientific life studying intestinal parasites for a PhD in India, having trained at the University of Calcutta and Jawaharlal Nehru University. In the United States she switched to neuroscience, and her lab now sits at the front edge of Alzheimer's research, asking how the body's own immune system might be turned against neurodegenerative disease and whether a lifetime of inflammatory episodes leaves the aging brain more vulnerable.

Jasmeet Judge directs UF's Center for Remote Sensing, where agriculture meets satellite technology in the work of measuring soil moisture and crop health from orbit. She has kept a thread back to India through the Fulbright-Kalam Climate Fellowship, a program named for the late president and aerospace scientist A.P.J. Abdul Kalam. Desika Narayanan, an astrophysicist, works at the opposite end of the scale entirely, modeling how galaxies form and evolve across cosmic time.

Statistics, medicine, remote sensing, deep space. The four occupy corners of the research enterprise that rarely touch. They share a starting line, not a finish.

## What a Professorship Buys

The UFRF professorship is not a lottery prize. It runs three years, carries a $5,000 annual salary supplement and a one-time $3,000 research grant, and is funded — fittingly — from the university's own share of royalties and licensing revenue on UF-generated inventions. The reward for discovery, in other words, is paid for by discovery.

Since the program began in 1997, more than a thousand UF researchers have received the title. The honor is institutional rather than national, which is precisely what makes the diaspora pattern visible. These are not headline awards that draw lobbying or campaigns. They are the internal verdict of a research university on who among its faculty is shaping their field — and in 2026, four of those verdicts landed on scholars of Indian origin.

## The Quiet Infrastructure of Influence

The diaspora's most-told story is the visible one: the CEO, the surgeon general, the senator, the founder. The UFRF list points at the layer underneath — the tenured researchers who train the next generation of PhDs, win the federal grants, file the patents, and run the labs that keep American universities at the frontier.

It is a layer built on a specific transaction. Indian institutions — the ISIs, the IITs, the central universities — invest years of rigorous training in students who then carry that training abroad. The "brain drain" framing has always cast this as a loss for India. The more accurate reading, visible in lists like this one, is a transfer of intellectual capital that has quietly underwritten decades of American scientific output.

For the diaspora, the four UFRF professors are a reminder that influence is not only the thing announced from a podium. Sometimes it is the slow accumulation of papers, grants, and graduate students — the kind of achievement that gets read out once a year, in a list, and is no less consequential for the quiet."""

body2 = """The award is new, the funding is real, and the name on it tells a familiar story. Vidya Chhabria, an assistant professor of electrical engineering at Arizona State University, has been named one of the inaugural recipients of Google's ML and Systems Junior Faculty Award — a recognition aimed at early-career researchers pushing the frontier where machine learning meets the systems that run it. With it comes $100,000 in unrestricted funding, the rarest and most useful kind of money in academic research.

Chhabria works in a corner of engineering most people never see but everyone depends on: the design of the chips inside every smartphone, laptop, and data center. Her field is electronic design automation — the specialized software that helps engineers lay out the billions of transistors on a modern processor — and her particular focus is on using artificial intelligence to do that work faster and at greater scale.

## The Problem She Is Solving

"Designing chips is complex, time-consuming and resource-intensive, and AI has shown enormous potential in addressing challenges of scale, automation and optimization in this area," Chhabria has said of her research. The claim is not abstract. The semiconductor industry's central bottleneck is no longer just manufacturing; it is design — the painstaking, expensive process of turning an architecture into a physical layout that can actually be fabricated.

Chhabria's group at ASU's Ira A. Fulton Schools of Engineering builds tools for exactly that, concentrating on what engineers call physical design: the optimization and analysis algorithms that decide where each component goes and how the whole thing holds together. It is the kind of work that rarely makes headlines but quietly determines whether the next generation of chips arrives on schedule or years late.

"Being recognized by Google via this junior faculty award is extremely rewarding, not just to me but to our entire group," she said, framing the honor as a vote of confidence in her lab's direction rather than a personal trophy.

## A Selective Inaugural Class

The award is competitive by design. Chhabria is one of more than fifty assistant professors across twenty-seven U.S. universities chosen for the inaugural class by a panel of Google engineers and researchers. The selection signals where one of the world's largest technology companies believes the next breakthroughs in computing will come from — and it is betting heavily on the intersection of AI and hardware design, the precise ground Chhabria has staked out.

The $100,000 in unrestricted funding matters more than its size suggests. Most research grants arrive with strings: a specific project, a defined deliverable, a reporting schedule. Unrestricted money lets a young researcher chase the riskier idea, hire the extra student, or pivot when the data points somewhere unexpected. For an early-career faculty member still building a lab, it is oxygen.

## The Diaspora's Engineering Spine

Chhabria's recognition lands at a moment when the Indian American presence in American technology is most often discussed through the lens of executives — the Sundar Pichais and Satya Nadellas who run the companies. Her award points at a less visible but arguably more foundational layer: the engineers and academics who design the physical machinery those companies run on.

Chip design is one of the diaspora's deepest grooves. Indian-origin engineers have long populated the electronic design automation industry, the semiconductor research labs, and the university departments that feed both. It is a lineage that runs from the IITs and India's electronics programs through the doctoral pipelines of American engineering schools and into the design teams at every major chipmaker.

The semiconductor has become the most strategically contested technology on earth, the object of national policies, export controls, and hundred-billion-dollar bets. The people who design those chips faster and better are, in a real sense, shaping the balance of technological power. That one of the inaugural Google awards in machine learning and systems went to an Indian American woman working on exactly that problem is a small data point in a much larger story — about where the diaspora's quiet engineering talent has concentrated, and why it matters more now than ever."""

body3 = """For decades, the British Indian community has been described in the language of arrival: the wealthiest ethnic group in the country, nearly 3 percent of the population contributing roughly 6 percent of GDP, a model of integration that politicians liked to cite and then ignore. A new survey suggests the community has grown tired of being cited and ignored — and that its political loyalty, long taken for granted, is now genuinely up for grabs.

The British Indian Census 2025, presented this month at the Houses of Parliament, lands a blunt message for the country's major parties: the assumption that British Indians will reliably vote one way is no longer safe. "British Indian political loyalties can no longer be taken for granted," said Nishma Gosrani of Bain & Company, calling the community a now-volatile swing bloc nearly 1.8 million strong.

## The End of a Reliable Vote

The history is one of being claimed and then dropped. Lord Krish Raval, chair of Labour Indians, traced the arc at the parliamentary presentation: the community was once seen as firmly Labour, then later as predominantly Conservative, and that very swing taught both parties to assume it had nowhere else to go.

The survey suggests the assumption has finally cracked. Support is leaking toward smaller parties — Reform UK and the Greens among them — not out of ideological conversion but out of frustration with being treated as, in the researchers' phrase, a tick-box exercise. "Many within the community feel they are no longer willing to be treated as a guaranteed vote bank," the findings note.

The data complicates easy stories. Among British Indians drawn to Reform UK, the dominant concerns are crime and the cost of living — issues on which the party has been loud. Strikingly, education ranks lowest among that subgroup's priorities: only 20 percent of Reform-leaning British Indians call it important, against 51 percent of Green supporters and 61 percent of those backing none of the main parties. For a community whose self-image is built on educational achievement, the split is revealing.

## How They See India

On the relationship with India, the community's priorities are unsentimental. Trade and business top the list at 56 percent, followed by international institutions at 45 percent — a clear endorsement of economic ties in the wake of the UK-India Free Trade Agreement. Travel and visas (41 percent) and history and heritage (36 percent) register the emotional pull, while technology and AI (35 percent) point to an appetite for a forward-looking partnership.

Seema Malhotra, a government minister, read the numbers as proof of a community that is "very internationally connected and strongly focused on economic prosperity," noting how often Indian-led businesses and cultural connections drive the partnerships now taking shape between the two countries.

## Belonging, Still Contested

Underneath the polling sat something rawer: the question of whether the community is fully accepted at all. Warinder Juss, the MP for Wolverhampton West, described arriving from Tanzania as a child and building a life that should settle the matter. "I have lived here, studied here, worked here and contributed to this country. That is what makes someone British," he said — adding that some still question his belonging.

The comedian Ahir Shah was sharper. Thirty years into a career and an award for his contribution to drama, he said, he is still "constantly reminded" he is treated as a foreigner, and recent demonstrations had echoed the racism of his childhood: being told to go back, his mother spat at, his father beaten. "I told my children I was being reminded that I wasn't welcome here again."

The survey's authors frame the work as evidence-building — a credible base that policymakers can no longer wave away. "If we want a society that works for everyone, we have to start by seeing everyone clearly," said Jasvir Singh, co-founder of South Asian Heritage Month.

For a diaspora that measured its success in incomes and degrees, the 2025 census marks a shift in register. The community is done being a statistic others quote. It wants to be a constituency others answer to — and it is signaling, clearly, that its vote will go to whoever bothers to listen."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Four of the University of Florida's Top Professors This Year Took the Same Road From India. That's Not a Coincidence.",
        "subheadline": "Kshitij Khare, Desika Narayanan, Jasmeet Judge, and Paramita Chakrabarty span statistics, astrophysics, remote sensing, and Alzheimer's research — and a tenth of one university's highest research honors going to Indian-origin scholars reveals the quiet infrastructure of diaspora influence.",
        "slug": make_slug("four-indian-origin-scholars-2026-ufrf-professors-university-florida-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The four UFRF professors expose the diaspora's least-visible layer of influence — not the headline CEO or senator, but the tenured researchers who train PhDs, win federal grants, and run the labs that keep American universities at the frontier, built on intellectual capital that Indian institutions trained and exported.",
        "tags": ["nri", "diaspora", "indian-american", "academia", "university-of-florida", "research"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Bazaar Online", "url": "https://www.americanbazaaronline.com/"},
            {"name": "University of Florida News", "url": "https://news.ufl.edu/"},
            {"name": "UF College of Medicine (Doctor Gator)", "url": "https://news.drgator.ufl.edu/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8533136/pexels-photo-8533136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A researcher at work in a university science laboratory",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Picked Its First Class of Junior Faculty Stars. One of Them Is Teaching Computers to Design Computer Chips.",
        "subheadline": "Arizona State's Vidya Chhabria won an inaugural Google ML and Systems award and $100,000 in unrestricted funding — a spotlight on the diaspora's deepest and least-visible groove in American technology: the engineers who design the chips everyone else runs on.",
        "slug": make_slug("vidya-chhabria-google-ml-systems-award-asu-chip-design-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Chhabria's award redirects attention from the diaspora's celebrated tech executives to its foundational engineering layer — the Indian-origin researchers who have long populated electronic design automation and semiconductor labs, a lineage that now sits at the center of the world's most strategically contested technology.",
        "tags": ["nri", "diaspora", "indian-american", "technology", "semiconductors", "ai", "academia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Arizona State University (Fulton Schools of Engineering)", "url": "https://ecee.engineering.asu.edu/"}
        ]),
        "score_total": 73,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/51165/cpu-processor-electronics-computer-51165.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A computer processor chip on a circuit board",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Britain's Wealthiest Minority Just Told Its Politicians: We Are Done Being Taken for Granted",
        "subheadline": "The British Indian Census 2025, presented at Parliament this month, finds a 1.8-million-strong community whose political loyalty is now genuinely up for grabs — and whose patience with being a 'tick-box exercise' has run out.",
        "slug": make_slug("british-indian-census-2025-swing-vote-parliament-diaspora-politics"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For a community that measured success in incomes and degrees, the 2025 census marks a shift from being a statistic others quote to a constituency others must answer to — with loyalty leaking toward smaller parties and an unresolved question of belonging surfacing even at Parliament.",
        "tags": ["nri", "diaspora", "british-indian", "uk", "politics", "identity"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Asian Voice", "url": "https://www.asian-voice.com/News/UK/What-do-the-British-Indians-want"},
            {"name": "The 1928 Institute / British Indian Census 2025", "url": "https://www.1928institute.org/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/18729241/pexels-photo-18729241.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Houses of Parliament and Big Ben in London",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️  {art['slug']} only {wc} words — skipping")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
