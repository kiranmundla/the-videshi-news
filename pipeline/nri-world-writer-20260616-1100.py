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

berlin_body = """Twenty-one years is a long time to build anything. It is the span of a childhood, the gap between a first visa and a second passport, roughly the time it has taken Berlin's Tamil families to go from praying in living rooms to consecrating one of the largest Hindu temples in Europe.

On 7 June, after a five-day festival, water from the Ganges and from Berlin was poured by crane onto the spire of the Sri Ganesha Hindu Temple's seventeen-metre vimana. The temple, on the edge of Hasenheide park in the working-class district of Neukölln, opened its doors. Construction had begun, in effect, in 2005. It was funded entirely by donations and seva — voluntary labour — and is run today by ten unpaid board members and three priests.

## A community that arrived in pieces

The story of the temple is the story of how its congregation got to Germany. The first wave were Sri Lankan Tamils, refugees of the civil war that began in the 1980s, who landed in a divided city that had little idea what to do with them. They worshipped where they could: rented rooms, basements, the corners of other people's buildings. In 2013, Berlin got its first Hindu temple, the smaller Sri-Mayurapathy-Murugan-Tempel in Britz. The Ganesha temple was always meant to be the larger statement.

What changed the math, in the end, was a second wave — the students and IT workers who began arriving from India in the 2010s as Germany loosened its skilled-migration rules. "This is for the newcomers from India, the students, the IT workers," one devotee said at the opening, "together with the German population, not just alone." It is a revealing line. The temple was conceived by refugees and finished, in part, on the contributions of economic migrants who came two decades later for entirely different reasons. They now share a building.

## Granite from Tamil Nadu, in a Berlin park

The architecture insists on its origins. The first gopuram tower rose in 2015, built from black granite quarried in Tamil Nadu and hand-carved by stonemasons brought from India — the kind of craft that cannot be sourced locally and must be imported along with the people who practise it. Against the flat northern-European sky of Hasenheide, the carved tower is deliberately incongruous, a piece of Dravidian temple architecture transplanted whole.

The temple is now a registered non-profit, recognised by the Finanzamt für Körperschaften, Berlin's tax authority for corporations. That bureaucratic detail matters more than it sounds. It means the building is woven into the legal fabric of the German state — taxed, regulated, permanent — rather than tolerated as a curiosity. Doors open daily from 4pm to 6pm, with aarti morning and evening. The temple is open, the organisers stress, to every Hindu tradition — Vaishnava, Shaiva, Shakta, Smarta — and to anyone who walks in off the street.

## The diaspora's long game

For the Indian diaspora across Europe, the Berlin opening is a marker of a particular kind of maturity. Temples are the last thing a migrant community builds, not the first. A community first finds work, then housing, then schools, then — once it is confident it is staying — it builds in stone. A twenty-one-year construction project is itself a statement that nobody is going back.

Germany's Indian-origin population has grown sharply over the past decade, driven by the Blue Card scheme and the country's chronic shortage of engineers and IT professionals. Indians are now among the largest groups of skilled migrants entering Germany each year. They are younger and more dispersed than the Tamil refugees who preceded them, and the question of whether they will build the kind of dense community institutions that the diaspora has constructed in Britain, Canada and the United States is still open.

The Ganesha temple is one answer. It was built by a community that had every reason to assume it was temporary and decided, over two decades, to act as though it was not. That the project was completed largely on volunteer labour and small donations — rather than a single wealthy benefactor — is itself the point. It belongs to everyone who carried a stone.

For the families who first prayed in Berlin basements forty years ago, the crane lowering Ganges water onto the spire was the end of a very long wait. For the IT workers who arrived last year, it was a place to belong on their first weekend in a new country. Both, for once, were standing in the same room."""

indiaspora_body = """The figure that ought to focus the mind is this: Indian Americans have given more than $3 billion to American universities since 2008. Not invested, not lent — donated. A community that numbers around 1% of the United States population has quietly become one of the more consequential forces in the financing of American higher education, and a new report from Indiaspora, the diaspora network, lays out the scale of it.

## The flywheel

The headline numbers are familiar but worth restating. Some 78% of Indian Americans hold a bachelor's degree or higher, against a national average closer to a third. Roughly 270,000 Indian students are currently enrolled at American universities, contributing nearly $10 billion a year to the economy and supporting an estimated 93,000 jobs. The community that arrived to study is now writing the cheques that fund the studying.

Indiaspora calls this a "flywheel effect" — educational achievement generates wealth, wealth flows back into the institutions that produced it, and those institutions educate the next cohort. It is a tidy formulation, and the giving data largely bears it out. The donations track the donors' own careers with almost mechanical precision.

## Where the money goes

Medicine dominates. Health sciences captured 46% of total giving, with eight separate gifts exceeding $10 million directed at medical schools, research centres and health infrastructure. In Florida, Dr. Kiran and Pallavi Patel have reshaped medical education through contributions large enough to put their names on institutions. The pattern reflects the disproportionate number of Indian Americans who became physicians after arriving in the 1970s and 1980s, and who are now at the age and wealth at which large philanthropy happens.

Engineering and technology took 31%, including a $100 million gift from Chandrika and Ranjan Tandon to New York University's engineering school. The benchmark was set back in 2002, when the entrepreneur Desh Deshpande gave $20 million to MIT to create a centre for technological innovation. Business education has drawn over $100 million, anchored by Indra Nooyi's landmark gift to the Yale School of Management. At Stanford, Ram Shriram's donations helped build a bioengineering centre.

The self-reinforcing logic is hard to miss. Doctors fund medicine; engineers fund engineering; the PepsiCo chief executive funds the business school. Successful professionals are, in effect, paying forward the disciplines that made them.

## Beyond the coasts

The geography is more interesting than the clichés suggest. Florida, not California or the north-east, received the highest concentration of gifts at 38% of the total. California followed at 13% — the University of California system alone has taken in over $80 million from Indian-American donors. The Ivy League accounts for a further 9%. But the report is at pains to point out that substantial giving is now emerging across the Midwest and South: Monte Ahuja in Ohio, Satish and Yasmin Gupta across Texas, and a long tail of contributions to community colleges and city universities that never make headlines.

That dispersal matters. It suggests the philanthropy is not merely a coastal-elite phenomenon but is tracking the diaspora's own spread into smaller cities and second-tier metros, where Indian-American doctors, hoteliers and engineers have put down roots.

## What the giving says

More than 12% of gifts — over $140 million — went to South Asian, Hindu or Indian studies programmes. This is the part of the portfolio that is not about workforce or career reinforcement at all. It is about ensuring that the culture the donors carried over is studied, taught and preserved in the institutions of their adopted country. It is the academic equivalent of building a temple: a bet that the community will still be here, and still care, in fifty years.

For the broader diaspora, the report is both a celebration and a quiet argument. The celebration is obvious — a community that arrived with little has become a pillar of American higher education in a single generation. The argument is subtler. Indiaspora notes that most small gifts to colleges go unrecorded and their donors unrecognised, and it is plainly trying to build a culture of named, visible, large-scale giving of the kind long established among older American philanthropic dynasties.

Whether that culture takes hold is the open question. The first generation gave to the institutions that educated them out of gratitude. Whether the second generation — born in America, with no memory of arriving — gives at the same rate, and to the same ends, will determine whether the flywheel keeps turning."""

gujarati_body = """In Orlando over Memorial Day weekend, more than fifty children stood up, one after another, and spoke in Gujarati. Some recited poetry. Some delivered speeches. Some had written essays on family, food, tourism and Bharat. All of them were born and raised in the United States, and for many it was the first time they had performed in their mother tongue on a stage in front of strangers.

The first-ever FOGA USA National Gujarati Competition, held during the 2nd United Gujarati Convention from 22 to 25 May, was a small event with a large preoccupation behind it: the quiet, generational erosion of heritage languages in the diaspora, and whether anything can be done to slow it.

## The third-generation problem

Every immigrant community eventually confronts the same arithmetic. The first generation speaks the home language fluently. The second understands it but answers in English. The third often cannot follow a conversation with its own grandparents. For Gujaratis — one of the largest and most established Indian-American communities, dominant in everything from the motel industry to suburban medicine — the question of language loss is no longer hypothetical. The grandparents who arrived in the 1970s are now in their seventies and eighties. The grandchildren are in American schools where Gujarati has no place at all.

The competition was a deliberate intervention against that drift. Modelled on a programme run since 2023 by the Gujarati Mandal of Central Ohio, it was scaled up to a national platform by the Federation of Gujarati Associations of USA. Participants competed across three categories — essay writing, public speaking and poetry recitation — on topics chosen to make them reach for cultural vocabulary they might never use otherwise: family, Gujarati personalities, cuisine, tourism, the idea of Bharat itself.

## What the children said

The most telling testimony came from the participants. "This language helps me stay connected with my grandparents who don't speak English," said Kahani Patel, one competitor. "It also helps me stay connected with many of our religious scriptures that are only in Gujarati." It is a strikingly practical articulation of why a language matters: not abstract heritage, but the ability to talk to the people who raised your parents, and to read texts that exist in no other tongue.

Another participant, Kian Lakhani, described the simple act of speaking on stage as a kind of homecoming. "Speaking in Gujarati on the stage helped me feel more connected to our Gujarati language and culture." The organisers were careful to frame the achievement in the children's own terms — confidence, pride, connection — rather than as a chore imposed by anxious parents.

## The infrastructure of preservation

What makes the FOGA effort interesting is that it is institutional rather than familial. Language preservation in the diaspora has traditionally been left to individual households — a heroic, exhausting and frequently losing battle waged by one parent at a time. The competition represents an attempt to build community-level infrastructure around the problem: a calendar event, a national platform, a set of judged standards, a sense that proficiency will be recognised and rewarded rather than merely expected.

Much of this infrastructure already exists in fragments. Many children cited the temple — the mandir, and especially Bal Sabha, the children's assembly — as where they learned to read and write Gujarati in the first place. Weekend language classes, religious schools and cultural associations have been doing this work for decades, unevenly and without much coordination. The convention pulled those threads into something with national visibility.

## A model that travels

The structure is replicable, which is the point. A competition pioneered by one mandal in Ohio became a national event in two years; there is no obvious reason the same template could not serve Tamil, Telugu, Marathi, Punjabi or Bengali communities facing identical pressures. The mechanics — judged categories, age brackets, a convention to host it — are language-agnostic.

Whether such efforts actually move the needle on language retention is genuinely uncertain. A weekend competition cannot, by itself, reverse the structural forces pushing American-born children toward monolingual English. But it changes the social meaning of the language. A child who has competed in Gujarati poetry has been told, publicly, that the skill is valuable — and that recognition, repeated across enough children and enough years, is roughly how a heritage language survives a generation it might otherwise not have.

For the Gujarati diaspora, the inaugural competition was less a triumph than a marker laid down: the community has decided the language is worth organising to save, and has built the beginnings of the machinery to try."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-One Years, Hand-Carved Tamil Granite, and a Crane Pouring Ganges Water: Berlin Just Got One of Europe's Largest Hindu Temples",
        "subheadline": "Begun by Tamil refugees and finished partly on the donations of newly arrived IT workers, Berlin's Sri Ganesha Hindu Temple is the diaspora's long game in stone.",
        "slug": make_slug("berlin-sri-ganesha-hindu-temple-opens-europe-largest-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Temples are the last thing a migrant community builds, not the first — and a 21-year volunteer-funded project signals a German-Indian diaspora that has decided it is staying.",
        "tags": ["nri", "diaspora", "germany", "berlin", "hindu-temple", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/08/sri-ganesha-temple-in-berlin-opens-doors/"},
            {"name": "Wikimedia Commons", "url": "https://commons.wikimedia.org/wiki/File:(20260607_143234213)_Sri_Ganesha_Hindu_Temple_Berlin.jpg"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg/1280px-%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg",
        "image_caption": "The Sri Ganesha Hindu Temple in Berlin's Neukölln district, consecrated on 7 June 2026",
        "image_attribution": "Wikimedia Commons",
        "body": berlin_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Americans Have Given American Universities $3 Billion Since 2008. A New Report Maps Exactly Where It Went.",
        "subheadline": "Medicine took 46%, Florida outranked California, and a $140 million slice went to Indian studies. Indiaspora's data reveals a 'flywheel' the second generation must now decide whether to keep spinning.",
        "slug": make_slug("indiaspora-report-indian-american-university-philanthropy-3-billion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A community that arrived to study has become one of the largest private funders of US higher education in a single generation — and the giving tracks the donors' own careers with mechanical precision.",
        "tags": ["nri", "diaspora", "philanthropy", "education", "indiaspora", "usa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indiaspora", "url": "https://indiaspora.org/impact/from-migration-to-endowment-diaspora-support-for-education/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Graduates celebrate at a university commencement ceremony",
        "image_attribution": "Pexels",
        "body": indiaspora_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Fifty American-Born Children Stood Up in Orlando and Spoke Gujarati. It Was a Bet Against the Third-Generation Problem.",
        "subheadline": "FOGA USA's first national Gujarati competition is an attempt to move heritage-language preservation out of individual households and into community infrastructure.",
        "slug": make_slug("foga-usa-national-gujarati-competition-diaspora-language-preservation"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every immigrant community confronts the same arithmetic — the third generation can't talk to its grandparents. A judged national competition is the diaspora's organised attempt to slow the drift.",
        "tags": ["nri", "diaspora", "gujarati", "language", "community", "usa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/15/foga-usa-successfully-hosts-first-ever-national-gujarati-competition-at-the-2nd-united-gujarati-convention-2026/"},
            {"name": "FOGA USA", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5905929/pexels-photo-5905929.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Children writing at a classroom table",
        "image_attribution": "Pexels",
        "body": gujarati_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  {art['slug']} -> {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
