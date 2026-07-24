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

body1 = """At a ceremony in London's Science Museum this month, Prince William handed out 20 Diana Legacy Awards, the highest honour given by the charity set up in memory of his mother. Two of the recipients were Indian: Uday Bhatia, 18, and Manasi Gupta, 24. For a diaspora that often measures its success in corner offices and campaign donations, the win is a reminder that the community's softest power travels through its youngest members.

The award is deliberately hard to get. Handed out only every two years, the Legacy Award is reserved for young people who already hold a Diana Award and have gone on to widen their impact. This year's cohort of 20 was selected by an independent panel chaired by Baroness Doreen Lawrence, drawn from those recognised in 2022 or 2023. The timing carries extra weight: the ceremony opened the charity's 25th anniversary year.

## Two very different problems

Bhatia and Gupta did not win for the same thing, and that is part of the story. Bhatia, who built his project as a schoolboy in northern India, designed a low-cost bulb he calls the Outage Guard — a lamp that keeps glowing for up to 10 hours during the power cuts that routinely interrupt study in much of small-town India. His company, Uday Electric, grew out of watching classmates lose evenings of homework to a dark grid. It is the kind of frugal engineering the diaspora likes to celebrate, because it solves a problem the older generation remembers in its bones.

Gupta's work is quieter and, in the Indian context, more quietly radical. Her nonprofit, Huesofthemind Foundation, takes on mental health — a subject that much of the community still files under shame. She says the foundation has reached more than 50,000 people, working with over 200 partner organisations and running more than 100 sessions herself. During the pandemic her services drew recognition from India's then health secretary at the IHW Digital Health Awards, and an illustrated fundraising book she produced has been seen by over a million people online.

## Why a London medal matters in Edison and Harrow

For the diaspora, the venue is the point. Both winners are Indian nationals rather than second-generation British Indians, yet they were honoured on a British stage, by a future British king, alongside young leaders from Bangladesh, Jamaica, the Cayman Islands and beyond. That is the diaspora's natural habitat: Indian by origin, global by platform, validated abroad in a way that ricochets back home.

It also flips a familiar script. The community abroad is used to writing cheques and lending its networks to causes in India. Here, two young Indians arrived in London to be recognised for fixing Indian problems — a dark classroom, an untended mind — on the world's terms. Diaspora parents who spend weekends ferrying children between coding camps and Bharatanatyam lessons will recognise the underlying anxiety the award soothes: that the next generation can be both rooted and recognised.

## The longer game

The Diana Award has handed its main honour to a string of young Indians over the years, including teenagers who shut down village liquor shops and others who built NGOs around childhood illness. The Legacy tier, far rarer, signals that the charity expects these names to keep compounding their impact for decades.

For Bhatia and Gupta, the medal is less a finish line than a credential. Bhatia now has a manufacturing story to scale and a royal photo-op to open doors with. Gupta has international cover for a conversation — mental health in South Asian households — that still needs all the cover it can get. Both will spend the next stretch being asked to speak, mentor and fundraise, the standard tax levied on young people the moment they are labelled inspiring.

The diaspora will happily pay it forward. In a year when the community's headlines have leaned toward tax statistics, election maps and remittance records, two young people getting a medal from Prince William for a cheap lamp and an honest conversation about feelings is the rarer kind of win — the kind that needs no caveat."""

body2 = """On a Sunday afternoon at the Bharatiya Vidya Bhavan in Manhattan, a few dozen Indian-American teenagers and their parents sat through something that looked less like a community event and more like a strategy session. The Global Organization of People of Indian Origin's Manhattan chapter had assembled a panel of professionals to answer a question the diaspora obsesses over but rarely discusses in the open: what actually happens after the acceptance letter?

The "College and Beyond" panel, held on June 7, was free, ran three hours, and drew a full room. That alone says something about where the community's anxieties now sit. The first-generation fight was to get the kids into good schools. The second-generation fight, increasingly, is about what they do with the degree — and whether the narrow track of medicine, engineering and finance is the only respectable map.

## A panel built to widen the map

The line-up was chosen, it seems, to quietly broaden the definition of success. There was Mihir Sanghavi, a senior engineering leader working in AI and large-scale software — the safe, aspirational anchor every desi parent recognises. But around him the organisers placed less obvious role models: Shashank Shamshabad, a public-affairs graduate of Columbia's school of international and public affairs now in public service; Vinisha Patel, a second-year osteopathic medical student; Brian Thomas, an undergraduate at NYU's Stern business school; and Dr. Sonia Sharma, a Hindi-language educator and author.

The mix is the message. Public service and language education are not the careers that get bragged about at weekend gatherings, yet they were given equal billing with the AI engineer. The session was moderated by Prof. Rajasekhar Vangapaty, who leads the chapter and teaches at the Fashion Institute of Technology — itself a gentle rebuttal to the idea that respectable Indian-American careers all run through Silicon Valley or a hospital.

## The quiet function of the community organisation

Events like this are easy to overlook in the larger diaspora story, which tends to be told through CEOs, congressional candidates and tax-contribution statistics. But the GOPIO chapter network — local, volunteer-run, unglamorous — is doing something those headlines miss: transmitting hard-won practical knowledge down the generational ladder, free of charge.

For a first-generation immigrant parent, the American higher-education system is a maze of internships, networking norms, leadership-resume signalling and unwritten rules that no amount of professional success back in India prepared them for. A panel of people who have already walked the path, speaking plainly to a room of nervous families, is a form of community infrastructure as real as any temple or grocery store. It just does not photograph as well.

## Mentorship as the new remittance

There is a tidy way to read the afternoon. The diaspora's older model of giving back ran in one direction — money wired home, scholarships funded in ancestral villages, hospitals built in home states. The community organisation's mentorship model runs sideways and forward: established professionals investing time in the diaspora's own next generation, on this soil.

It is a recognition that the community's most valuable export is no longer just dollars but know-how — and that the children of immigrants need a map for the American maze more than they need another reminder to study harder. Indian-Americans are now routinely cited as the country's highest-earning, best-educated ethnic group, contributing a wildly outsized share of federal income tax. Sustaining that requires more than good genes and tiger parenting; it requires the kind of unsexy, repeatable mentorship a Sunday-afternoon panel quietly provides.

The teenagers in the room may not remember the specific advice they got about internships or essays. But they saw something useful: a Hindi teacher and an AI engineer sharing a stage as equals, both held up as proof that the diaspora's definition of arriving is finally getting wider."""

body3 = """The European Union has handed 75 Indian students prestigious Erasmus Mundus scholarships for the 2026-2028 cycle and launched a new network to bind India's brightest more tightly to European campuses. For a diaspora story usually dominated by the United States, it is a reminder that the map of where Indians study abroad — and put down roots — is quietly being redrawn toward Europe.

The numbers, announced on June 22 by the EU's delegation to India, keep India near the top of the Erasmus pile. The Erasmus Mundus programme funds fully-paid joint master's degrees taught across multiple European universities, and Indians have for years been among its largest national cohorts. Seventy-five new scholars will now spend two years moving between European institutions, the kind of multi-country education that tends to produce graduates who feel at home everywhere and nowhere — the classic diaspora condition, arrived at by design.

## A network, not just a cheque

Alongside the scholarships, the EU unveiled an EU-India Student Ambassadors' Network, connecting 40 student representatives across 20 Indian universities. The idea is to create a peer-led community that markets European study options from inside Indian campuses, aligned with the broader EU-India strategic agenda on youth, research and innovation.

It is a small initiative with an outsized logic. The United States and Britain have long relied on word of mouth and alumni networks to keep the Indian student pipeline flowing. Europe, a more fragmented and less English-default destination, is building that connective tissue deliberately. The ambassadors are, in effect, the seed corn of a future European-Indian diaspora — students who will pull the next cohort across, the way earlier generations did for America's universities.

## Why the diaspora map is shifting

The timing is not accidental. Indian families weighing where to send their children abroad are reading the same headlines everyone else is: tightening visa rules and a colder political climate around immigration in parts of the English-speaking world. Europe, with its push for skilled migration and post-study work pathways in several countries, is positioning itself as the pragmatic hedge.

For the diaspora, this matters beyond tuition. Where students go is where communities eventually form. The vast Indian populations of New Jersey, the Bay Area, Toronto and the English Midlands all began, in part, as student flows that turned into settlement. A sustained increase in Indians studying in Germany, France and the Netherlands is the early signature of diaspora clusters that do not yet fully exist — Little Indias being seeded one master's degree at a time.

## The two-worlds bargain, updated

There is something familiar in the bargain on offer. A young Indian takes a fully-funded degree that spans three or four European countries, builds a professional network across the continent, and faces the same choice every diaspora generation has faced: return home with a glittering credential, or stay and become the founding layer of a new community abroad.

What is different is the deliberateness. Europe is not passively receiving Indian talent; it is courting it, with scholarships, ambassador networks and a strategic agenda that treats Indian students as a relationship to be cultivated rather than a revenue line to be taxed. India, for its part, gains a wider set of destinations for its young — and, eventually, a wider diaspora to call on.

For NRI families, the practical takeaway is simple. The old default of America-or-Britain is loosening. A generation of Indians is being actively recruited into continental Europe, and the diaspora's next chapter may well be written in German lecture halls and Dutch research labs as much as in Edison or Hounslow. The community has always been good at growing in unexpected soil. Europe is now openly offering the seedbed."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Prince William Just Gave Two Young Indians the Diana Award's Top Honour. Neither Lives Abroad.",
        "subheadline": "An 18-year-old who built a power-cut-proof bulb and a 24-year-old mental-health campaigner were among 20 worldwide winners of the Diana Legacy Award, handed out in London.",
        "slug": make_slug("diana-legacy-awards-2026-uday-bhatia-manasi-gupta-prince-william-london-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For a community that prizes recognition abroad, two young Indians being honoured on a British stage by a future king — for solving Indian problems on the world's terms — is the diaspora's soft power at its purest.",
        "tags": ["nri", "diaspora", "diana-award", "uk", "youth", "philanthropy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/two-young-indians-are-recipients-of-diana-legacy-awards/"},
            {"name": "The Diana Award", "url": "https://diana-award.org.uk/"},
            {"name": "The Better India", "url": "https://thebetterindia.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Prince_of_Wales_at_State_Banquet_2025-09-17_%280.75_crop%29.jpg",
        "image_caption": "Prince William, the Prince of Wales, who presented the Diana Legacy Awards in London",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Sunday Panel in Manhattan Showed What the Indian-American Community Actually Worries About Now",
        "subheadline": "GOPIO's free 'College and Beyond' session put an AI engineer and a Hindi teacher on the same stage — a quiet bid to widen the diaspora's definition of a respectable career.",
        "slug": make_slug("gopio-manhattan-college-beyond-panel-indian-american-mentorship-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Volunteer-run community organisations are transmitting hard-won knowledge of the American higher-education maze to the diaspora's next generation — a sideways form of giving back that the CEO-and-Congress headlines miss.",
        "tags": ["nri", "diaspora", "gopio", "education", "usa", "mentorship"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/gopio-manhattan-organizes-college-and-beyond-panel-discussion-for-high-school-students/"},
            {"name": "GOPIO International", "url": "https://gopio.net/"}
        ]),
        "score_total": 64,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7234399/pexels-photo-7234399.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A speaker addresses an audience at a community panel discussion",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Is Quietly Courting Indian Students — and Seeding the Diaspora's Next Chapter",
        "subheadline": "The EU has awarded 75 Indians Erasmus Mundus scholarships and launched a student ambassadors' network, building the connective tissue that turns student flows into settled communities.",
        "slug": make_slug("eu-erasmus-mundus-scholarships-india-student-ambassadors-network-europe-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Where students go is where communities eventually form. Europe's deliberate recruitment of Indian talent is the early signature of diaspora clusters that do not yet fully exist — as old America-or-Britain defaults loosen.",
        "tags": ["nri", "diaspora", "education", "europe", "erasmus", "students"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/news/international/eu-awards-75-erasmus-scholarships-to-indian-students"},
            {"name": "Delegation of the European Union to India", "url": "https://www.eeas.europa.eu/delegations/india_en"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33885308/pexels-photo-33885308.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Students in graduation gowns celebrate at a university commencement",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
