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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "She Left Kerala at Six. Now Nithya Raman Wants to Run America's Second-Largest City.",
        "subheadline": "The urban planner turned Los Angeles city councillor has secured a spot in the November mayoral runoff against incumbent Karen Bass, making her the first Indian-born candidate to seriously contend for the office.",
        "slug": make_slug("nithya-raman-kerala-los-angeles-mayor-runoff-indian-american"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Raman's journey from a Malayali immigrant family in Louisiana to the doorstep of LA's top job encapsulates the expanding arc of Indian American political ambition — no longer limited to state legislatures and Congress, but now reaching for executive power in the country's biggest cities.",
        "tags": ["nri", "diaspora", "indian-american", "politics", "los-angeles", "nithya-raman"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/06/09/incumbent-karen-bass-and-progressive-nithya-raman-advance-to-los-angeles-mayoral-runoff/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/news/world/who-is-nithya-raman-kerala-born-urban-planner-aims-to-become-los-angeles-mayor"},
            {"name": "The Wrap", "url": "https://www.thewrap.com/nithya-raman-defeats-spencer-pratt-la-mayor-runoff/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/07/02/us-news/los-angeles-mayoral-candidate-nithya-raman-dodges-question-about-capitalism/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Nithya_Raman"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Nithya_Raman%2C_2022.jpg/330px-Nithya_Raman%2C_2022.jpg",
        "image_caption": "Nithya Raman, Los Angeles city councillor for the 4th district, in her 2022 official portrait",
        "image_attribution": "Wikimedia Commons",
        "body": """When Los Angeles County election officials finished processing the last tranche of mail-in ballots from the June 2 primary, the result was clear: Nithya Raman, the 44-year-old Kerala-born city councillor, had overtaken reality television personality Spencer Pratt to claim the second spot in the November runoff. She will challenge incumbent Mayor Karen Bass for control of America's second-largest city.

The victory felt anything but certain on election night. Pratt, who rode grassroots anger over homelessness and the devastating Palisades fire, held a lead of roughly 41,000 votes after in-person ballots were tallied. But California's mail-in voting infrastructure — which permits postmarked ballots to arrive up to seven days after Election Day — shifted the calculus. With each registrar update, Raman gained. By June 8, she led by more than 22,000 votes, earning projections from NBC, CNN, and the Associated Press.

## From Thiruvananthapuram to City Hall

Raman was born in 1981 into a Tamil Iyer family in Kerala. Her family emigrated to Louisiana when she was six. She attended Harvard, studied political theory, and went on to earn a master's in urban planning from MIT.

What she did next surprised people in both countries. Instead of chasing a career in American consulting or policy, Raman returned to India and founded Transparent Chennai, a research initiative that mapped informal settlements the city government had written off its plans. For seven years she worked in the slums of Chennai and Delhi, advocating for sanitation access and challenging mass evictions along the Yamuna River that displaced more than 100,000 families. Her focus was granular — water lines, toilets, land rights — and her methods were rooted in data, not ideology.

In 2013, she followed her husband, television writer Vali Chandrasekaran, to Los Angeles. A report she wrote for the city administrative officer on homelessness spending became her entry point into local politics. She discovered that the city was funnelling over $100 million toward homelessness — and nearly 90 per cent of that was going to jailing people living on the streets, not housing them.

She co-founded SELAH, a neighbourhood homeless coalition in Silver Lake, and later served as the first executive director of Time's Up Entertainment, the women's rights organisation that emerged from the MeToo movement.

## A Pattern of Firsts

In 2020, Raman unseated 17-year council incumbent David Ryu, becoming the first Asian American woman and the first South Asian person elected to the Los Angeles City Council. She was re-elected in 2024 and currently represents District 4, which spans both sides of the Hollywood Hills — from the wealthy streets of Larchmont Village to the denser, lower-income blocks of Van Nuys.

Her mayoral campaign has centred on affordability, housing construction, and a pledge to reduce tent encampments by half before Los Angeles hosts the 2028 Summer Olympics. She has been blunt about what she sees as the city establishment's failure to deliver.

The runoff has already generated national attention, with comparisons drawn to New York City Mayor Zohran Mamdani, another Indian-origin progressive who won executive office this year. In a CNN interview last week, Raman was pressed on whether she considers herself a capitalist. Her answer was pragmatic rather than ideological: "We are in a capitalist system. The role is the mayor of Los Angeles. You operate within this context."

## What It Means for the Diaspora

Raman's candidacy sits at an inflection point in Indian American political life. The community has produced governors, senators, a vice president, and an FBI director. But the leap from legislative bodies to executive leadership of a major city remains rare.

If Raman wins in November, she would become the first Indian-born mayor of Los Angeles — a city whose Indian American population has grown by over 40 per cent since 2010 and now approaches 120,000, not counting the broader South Asian community. Her platform, shaped by years spent mapping informal settlements in Chennai and counting homeless encampments in Hollywood, would bring a distinctly diasporic lens to a quintessentially American crisis.

The November contest is expected to be competitive. Bass holds the advantages of incumbency, and several of Raman's fellow Democratic Socialists on the city council have endorsed the mayor rather than their ideological ally. But Raman's primary performance — built on mail-in ballots from progressive voters in the city centre — suggests her coalition is real, and growing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One Dollar a Day, Millions of Children: The Diaspora Gala Betting That Indian Education Is the Best Investment on Earth",
        "subheadline": "The Vidyabharati Foundation of America will gather tech leaders, philanthropists, and MIT's Ramesh Raskar in Boston this Sunday to fundraise for one of India's largest school networks — at a per-pupil cost that shames most Western aid budgets.",
        "slug": make_slug("vidyabharati-gala-boston-deshpande-raskar-indian-education-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The gala embodies a maturing pattern in NRI philanthropy — moving from writing cheques for hometown temples to funding scalable, institution-grade educational infrastructure in India, with the same venture-capital rigour that built careers in Silicon Valley and Route 128.",
        "tags": ["nri", "diaspora", "philanthropy", "education", "vidyabharati", "boston"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "EIN Presswire / WCIA", "url": "https://www.wcia.com/business/press-releases/ein-presswire/mit-visionary-ramesh-raskar-to-keynote-vidyabharati-annual-gala/"},
            {"name": "EIN Presswire", "url": "https://www.einpresswire.com/article/brandeis-professor-debarshi-k-nandy-to-deliver-keynote-at-vidyabharati-foundation-of-america-gala"},
            {"name": "LinkedIn (Satish Jha)", "url": "https://www.linkedin.com/posts/satishjha_one-child-one-dollar-one-future-activity-7205985384212672512"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Ramesh_Raskar_%2811539797465%29.jpg/330px-Ramesh_Raskar_%2811539797465%29.jpg",
        "image_caption": "MIT professor Ramesh Raskar, keynote speaker at the Vidyabharati Foundation of America's 2026 annual gala in Boston",
        "image_attribution": "Wikimedia Commons",
        "body": """On Sunday evening, a ballroom at the Boston Marriott Burlington will fill with an unlikely congregation: venture capitalists and Vedic educators, AI researchers and retired schoolteachers from small-town Rajasthan, MIT professors and first-generation donors who still wire money home every month. They are there for a single proposition — that educating a child in India for roughly a dollar a day may be the highest-return philanthropic investment available anywhere.

The Vidyabharati Foundation of America's 2026 annual gala, announced last week, has assembled a programme that signals the Indian diaspora's growing ambition in education philanthropy. MIT's Ramesh Raskar, one of the world's foremost minds in computational imaging and AI for social impact, will deliver the keynote. Desh Deshpande, the serial entrepreneur and philanthropist whose Deshpande Foundation has channelled hundreds of millions of dollars into Indian innovation and social enterprise, will attend as chief guest. Rajendra Khaitan, national vice chairman of Vidya Bharati in India, will represent the organisation's ground-level operations.

## The Scale Behind the Pitch

Vidya Bharati is not a startup. It is one of the world's largest non-governmental educational networks, operating thousands of schools across India and educating millions of students. Its alumni include military generals, senior civil servants, scientists, entrepreneurs, and national sports champions. The Foundation's American arm has positioned this heritage as its central fundraising argument: proven outcomes at a fraction of the cost.

The gala's tagline — "One Child. One Dollar. One Future" — is not merely aspirational. Vidya Bharati's operating model keeps per-pupil costs at approximately one dollar a day by relying on locally recruited teachers, donated land, community-maintained facilities, and curricula that blend modern subjects with cultural and values-based instruction. In a sector where American and European aid programmes routinely spend fifty to a hundred times more per student, the efficiency is startling.

Professor Debarshi Nandy, the Stephen J. Cloobeck Professor of Finance at Brandeis International Business School, will speak on why investment in human capital remains the single greatest driver of national prosperity. His presence alongside Raskar signals a deliberate framing: this is not charity, it is infrastructure.

## A New Generation of Giving

The gala also reflects a shift in how the Indian American diaspora thinks about philanthropy. An older generation's giving was often personal — a new wing on a family temple, a scholarship at the school where a donor's father once studied. The current wave is more institutional. Donors want scale, measurement, and leverage. They want their giving to look like a term sheet.

Deshpande epitomises this approach. His foundation, built on the fortune he made co-founding Sycamore Networks and Cascade Communications during the telecom boom, has invested in incubators, skill-building programmes, and social entrepreneurship across India. His presence at the Vidyabharati gala lends credibility to an organisation that some donors may know only by reputation.

Pooja Ika, founder of Nirvana Health, an AI-driven healthcare company, will also address the gathering, rounding out a programme that intentionally bridges technology, education, and social enterprise.

## The Broader Pattern

The gala arrives at a moment when NRI philanthropy for Indian education is accelerating on multiple fronts. Nandan Nilekani's $38 million gift to IIT Bombay, Indiaspora's cataloguing of 250 milestones of Indian American generosity, and the recent SBI Research report projecting record remittances of $137 to $140 billion in FY26 all point in the same direction: a diaspora that is financially mature, emotionally connected, and increasingly strategic about where its money goes.

For the organisers in Burlington on Sunday, the pitch is simple. India's classrooms will produce the engineers, doctors, and entrepreneurs who shape the next century. The question is whether the diaspora will fund the foundation — literally — before someone else does.

Sponsorship options range from funding a single student programme to underwriting an entire school. The gala's organisers have not disclosed a fundraising target, but the assembled guest list suggests they are not thinking small."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
