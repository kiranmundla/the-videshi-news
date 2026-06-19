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

article1_body = """A small mountain town an hour north of Vancouver does not, on the face of it, look like a place to take the spiritual temperature of the Sikh diaspora. Squamish has roughly 25,000 residents, a famous granite monolith, and a reputation built on rock climbing and wind. On Saturday, June 20, it will also have a Nagar Kirtan — a religious procession the Squamish Sikh Society expects to draw more than 8,000 people, a number that would briefly make the parade larger than a third of the town's population.

The march returns after a year's absence. In 2024 the event was cancelled when the Dryden Creek wildfire forced the community to think about smoke and evacuation routes rather than processions. Its revival this weekend is, in the plainest sense, a story about a small congregation deciding that showing up in public still matters.

## A martyrdom remembered on a mountain

The procession marks the martyrdom of Guru Arjan Dev Ji, the fifth Sikh Guru, who was tortured and killed in 1606 — a foundational event in Sikh memory and one that the faith returns to each summer. The march will begin at the Gurdwara Sahib at around 10:30 a.m. and wind through 5th Avenue, Victoria Street, 3rd Avenue and Pemberton before finishing at the O'Siyam Pavilion. Along the way, performers will demonstrate Gatka, the Sikh martial art of swordsmanship that traces back to the same era of persecution the day commemorates.

For Paramjit Sidhu, the society's vice-president, the meaning is less about pageantry than pedagogy. "For me, this is basically teaching about spirituality, and it's about human rights," he said. "Our fifth Guru made us understand that everybody has the right to live on this planet, free."

## The langar as argument

At the pavilion, after political and religious leaders speak, roughly 26 food stalls will open, serving both traditional dishes and, in a concession to a Canadian June, ice cream. Sidhu is careful to frame the stalls as more than catering. They are, he said, "an opportunity for everyone to come together in one place" — a deliberate act of community-building rather than a side attraction.

This is the quiet genius of the Nagar Kirtan as the diaspora practises it. The free meal, or langar, is doctrine made edible: the Sikh principle that anyone, of any background, sits on the same floor and eats the same food. In a town where most onlookers will not be Sikh, the meal does the explaining that a sermon cannot.

## Small town, large signal

The guest list tells its own story about how embedded the community has become. Dignitaries expected to attend include the mayor, representatives of the Squamish Nation, the local MLA and MP, the RCMP and the fire department. A procession that exists to honour a 17th-century martyrdom has become, in 2026, a fixture on the civic calendar of a Canadian resort town — the kind of event where elected officials want to be photographed.

That ordinariness is the point. British Columbia is home to one of the largest Sikh populations outside India, and the province's marquee Vaisakhi parades in Surrey and Vancouver draw crowds in the hundreds of thousands. The Squamish march is a smaller, more intimate counterpoint: proof that diaspora religious life is not confined to the big metropolitan hubs but has rooted itself in places where Sikhs remain a visible minority.

For the families who will line the route on Saturday, the calculation is the one every immigrant community eventually faces. You can practise your faith privately, in the gurdwara, where no explanation is required. Or you can carry it out onto 3rd Avenue, where it becomes something your neighbours witness, ask about and — in the best version of the story — turn up for. Squamish, for one weekend, is betting on the second option.

"We will be waiting for you," Sidhu said. "Don't forget, Saturday, June 20.\""""

article2_body = """Every two years, several hundred young Jains from across North America check into a hotel together, eat food cooked without onions, garlic, potatoes or any root vegetable, and spend four days arguing about what it means to inherit a 2,500-year-old religion in a country that has barely heard of it. From July 2 to 5, they will do it again. The 17th Young Jains of America convention, held this year in New Jersey, is one of the largest gatherings of its kind anywhere outside India — and a revealing case study in how a tiny diaspora keeps a faith from thinning out across generations.

## The arithmetic of a small faith

Jains number perhaps four to five million worldwide and a few hundred thousand in North America — a rounding error even within the Indian diaspora. That scarcity is precisely what makes the convention's scale notable. It draws over 800 Jain youth aged 14 to 29 and is organized entirely by a committee of 38 to 43 students and young professionals, who handle everything from booking the hotel to recruiting monks and nuns who travel from India to speak.

The math of belief in a diaspora is unforgiving. A religion with few temples, fewer clergy and no critical mass in any single American suburb cannot rely on ambient culture to transmit itself. It has to be organized, deliberately and repeatedly, by the young people who stand to lose it.

## Doctrine and Garba in the same building

The convention's design reflects that double task. Daytime programming runs sessions with scholars, monks and outside speakers on the philosophy of Jainism — non-violence, non-attachment, the ethics of how one eats and lives. Nighttime programming is a talent show, a Garba night and a formal dance. The organizers are unembarrassed about the combination. The faith is the reason to gather; the friendships are the reason to come back.

The food is its own statement of principle. Meals are strictly Jain and vegan — no meat, no animal byproducts, and none of the root vegetables whose harvesting harms small organisms in the soil. That a hotel kitchen in New Jersey is asked to feed 800 people Mexican, Italian and Indian cuisine under those constraints is, in miniature, the entire diaspora project: take an exacting tradition and make it work inside an American institution that was not built for it.

## The third-generation problem

What the YJA convention is really fighting is attrition. Across faith communities, the immigrant generation arrives devout, their children grow up bicultural, and the grandchildren often drift. For a group as small as the Jains, that drift is existential — there is no large home community in America to absorb the losses.

The convention's answer is to make the faith social before it becomes obligatory. A teenager who might never sit through a lecture on anekantavada — the Jain doctrine that truth is many-sided — will sit through it if their friends are in the room and a dance follows that evening. The biennial rhythm matters too: a 14-year-old at their first convention can plausibly attend their sixth before aging out at 29, building a decade and a half of friendships welded to the practice of the faith.

## A template worth watching

For the broader Indian diaspora, the Jains are a useful extreme. Larger communities — Hindu, Sikh, Muslim — can lean on temples, gurdwaras and mosques dense enough to sustain identity almost passively. The Jains cannot, and so they have had to be explicit about a problem everyone else faces more gradually: how do you hand down a tradition to children who are fully, comfortably American?

The convention is one answer, and a durable one — 17 editions and counting. Whether it is enough is the question every diaspora parent is quietly asking. In July, in a New Jersey ballroom, several hundred young people will offer their version of a reply."""

article3_body = """The House of Lords is an unlikely launchpad for a poem. Yet a recent evening in the gilded committee rooms of Britain's upper chamber was given over almost entirely to verse — specifically, to English-language poetry written by the Indian diaspora, a body of work that has spent decades being published, praised in small circles and largely ignored by the literary establishment that surrounds it.

The gathering was hosted by Lord Bhikhu Parekh, the political theorist and crossbench peer, who is himself a distinguished diaspora writer and a patron of the Word Masala Foundation. The event was the brainchild of Yogesh Patel, the poet who founded the non-profit, and it drew some sixty people: established and emerging poets, publishers and journalists, packed into a programme of speeches, book launches, readings and awards.

## Between two languages, claiming one

The premise carries a quiet provocation. English-language poetry by the Indian diaspora occupies an awkward middle ground — too Indian for the mainstream British canon, too anglophone for some Indian gatekeepers. Patel's stated aim was to bring together and honour eminent diaspora poets from both Britain and the United States, alongside the British publishers who have backed the form when larger houses would not.

That double belonging is the diaspora condition rendered in literary terms. These are writers who think and dream in English yet carry a second country in their syntax — and who have, for years, struggled to find publishers willing to treat that hybridity as an asset rather than a marketing problem.

## The honour roll

The evening's awards, presented by Lord Parekh and Baroness Usha Prashar, read like a quiet census of the field. Recognized poets included Meena Alexander and Usha Akella, alongside Shanta Acharya, Siddhartha Bose, Kavita Jindal, Daljit Nagra, Usha Kishore, Reginald Massey and Debjani Chatterjee. Saleem Peeradina and Pramila Venkateswaran were honoured in absentia.

Some of these names are familiar to anyone who follows diaspora literature; Daljit Nagra, for one, has won major British poetry prizes. Others have built careers in the margins, publishing with small presses and reading to modest rooms. Gathering them under one ceiling, in a chamber of British state, was itself the message: this work belongs in the building.

A particular coup, Patel noted, was a publishing contract for the Isle of Man-based poet Usha Kishore, whose next collection will be brought out by Eyewear Publishing. And in a gesture toward the economics that govern small-press poetry, the foundation gave its first Crowd-Funding Award to Mona Dash, to support the publication of her next collection — an acknowledgment that for diaspora poets, money, not talent, is usually the binding constraint.

## Why a room of sixty matters

It would be easy to dismiss an evening of poetry readings for sixty people as a niche affair. That would miss what the diaspora has always understood about cultural survival: it happens in small rooms first. The Jewish, Irish and Caribbean literary traditions in Britain all began as gatherings of the unfashionable, championed by a handful of patrons before the wider culture caught up.

The Indian diaspora in Britain is now its wealthiest minority and an established political force. What it has not yet fully secured is a settled place in the country's cultural memory — the sense that its writers are simply British writers, read and taught as such. Evenings like this one are a bid to close that gap, one publishing contract and one award at a time.

The keynote, fittingly, was delivered by Zata Banks, founder of the Poetry Film research project, on the creative opportunities at the intersection of poetry and film — a reminder that the diaspora's next literary chapter may not arrive on a printed page at all. But it began, on this evening, where so much diaspora culture begins: in a borrowed room, among people who refused to wait for permission."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Town of 25,000 Is About to Host 8,000 Sikhs. Squamish's Nagar Kirtan Returns After the Fire.",
        "subheadline": "A mountain resort town north of Vancouver revives its Sikh procession on June 20, two years after a wildfire cancelled it — and turns a 17th-century martyrdom into a fixture of the civic calendar.",
        "slug": make_slug("squamish-sikh-nagar-kirtan-returns-diaspora-bc"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Sikhs in British Columbia, carrying the faith out of the gurdwara and onto a small town's main street is how a visible minority converts private devotion into public belonging — and the langar does the explaining a sermon cannot.",
        "tags": ["nri", "diaspora", "sikh", "canada", "nagar-kirtan", "british-columbia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Squamish Reporter", "url": "https://squamishreporter.com/2026/06/15/squamish-community-invited-to-annual-sikh-parade-on-june-20/"},
            {"name": "BC Gov News — Sikh Heritage Month", "url": "https://news.gov.bc.ca/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Vaisakhi_Nagar_Kirtan_Sikh_Parade_%2833965994714%29.jpg/1280px-Vaisakhi_Nagar_Kirtan_Sikh_Parade_%2833965994714%29.jpg",
        "image_caption": "A Nagar Kirtan procession winds through the streets, devotees following the float carrying the Guru Granth Sahib",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Million Jains, Eight Hundred Teenagers, One New Jersey Ballroom: How a Tiny Faith Refuses to Thin Out",
        "subheadline": "The 17th Young Jains of America convention, July 2-5, is one of the largest gatherings of Jain youth outside India — and a case study in how a small diaspora fights the third-generation problem.",
        "slug": make_slug("young-jains-america-2026-convention-diaspora-faith"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Too small to rely on ambient culture or dense temple networks, Jains in North America have to organize their faith's survival deliberately — making the YJA convention a sharp, instructive version of the transmission problem every diaspora family faces.",
        "tags": ["nri", "diaspora", "jain", "youth", "convention", "new-jersey"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Young Jains of America — 2026 Convention", "url": "https://yja.org/"},
            {"name": "JAINA (Federation of Jain Associations in North America)", "url": "https://jaina.org/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29449926/pexels-photo-29449926.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An ornately carved Jain temple, the kind of architectural tradition the diaspora works to keep meaningful for youth raised abroad",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "In the House of Lords, Sixty People Gathered to Argue That Diaspora Poetry Belongs in the Building",
        "subheadline": "An evening hosted by Lord Bhikhu Parekh honoured English-language poets of the Indian diaspora — a body of work long caught between two literary worlds and claimed by neither.",
        "slug": make_slug("indian-diaspora-poets-house-of-lords-word-masala-britain"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "British Indians are now the UK's wealthiest minority and an established political force, but their writers have yet to win a settled place in the nation's cultural memory — and this gathering was a bid to close that gap, one publishing contract at a time.",
        "tags": ["nri", "diaspora", "uk", "poetry", "literature", "british-indian"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Asian Voice", "url": "https://www.asian-voice.com/"},
            {"name": "Word Masala Foundation", "url": "https://www.wordmasala.com/"}
        ]),
        "score_total": 64,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Official_portrait_of_Lord_Parekh_%28crop_4%29.jpg",
        "image_caption": "Lord Bhikhu Parekh, the political theorist and crossbench peer who hosted the diaspora poetry evening at the House of Lords",
        "image_attribution": "Wikimedia Commons",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] ~{wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
