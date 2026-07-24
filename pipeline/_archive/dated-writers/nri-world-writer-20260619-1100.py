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

article1_body = """When the Reserve Bank of India wants dollars, it knows exactly which doorbell to ring. On June 17th the central bank temporarily scrapped the interest-rate ceilings on two of the diaspora's favourite savings vehicles—fresh Foreign Currency Non-Resident Bank deposits of three-to-five-year tenors, and Non-Resident External rupee deposits of three years and above. Within forty-eight hours, banks were advertising returns that would have been unthinkable a month earlier.

Bandhan Bank moved first and loudest, lifting its FCNR(B) rate to 7.1% on dollar deposits of $1 million and above for three-to-five-year tenors, and 7% for smaller balances. That is roughly double the 3.35-4% on offer earlier in the year. Other lenders are following, with rates clustering between 6% and 7%. For an overseas Indian who has spent the past decade watching American and Gulf banks pay a pittance on savings, the arithmetic is suddenly hard to ignore.

## Why the rules changed

The relaxation is not generosity; it is strategy. The rupee has been under pressure from elevated crude prices and a jittery global market, and the RBI is reaching for a playbook it last used during the 2013 "taper tantrum," when FCNR(B) deposits hauled in tens of billions of dollars almost overnight. The mechanism is elegant. An NRE account holds foreign currency converted to rupees, with both principal and interest fully repatriable. An FCNR(B) deposit stays in the original foreign currency, sparing the depositor any exchange-rate risk if the rupee slides—a meaningful comfort given where the currency has been heading.

To sweeten the deal for banks, the RBI on June 5th introduced a concessional foreign-exchange swap window, effectively absorbing the cost of currency hedging that lenders would normally bear. That is what lets a bank offer 7% without bleeding on the hedge. Industry estimates cited in the Indian financial press suggest the combined measures could pull $60-70 billion into the system before the window closes on September 30th.

## The fine print NRIs should read twice

The headline rates are real, but the conditions matter. Crucially, transfers from an existing NRO (Non-Resident Ordinary) account into an NRE account do not qualify for the exemption—the RBI wants genuinely fresh foreign money, not domestic rupees relabelled. The relaxation also applies only to fresh deposits and those renewed on maturity during the window. Existing FCNR(B) deposits booked at the old 3-4% rates keep earning the old rates.

That last point has set off a quiet scramble. According to a report in The Economic Times, several banks have approached the RBI for permission to let existing NRI customers prematurely break and rebook their deposits at the new rates. Some large depositors are not waiting for clarity—they are already instructing banks to close old deposits and redeploy, or shifting balances between banks to chase the best number. For a community that prizes both safety and yield, a 300-basis-point jump is worth a phone call to the relationship manager.

## A familiar bargain

For the diaspora, the offer lands in a familiar emotional register. Parking money in India has always been about more than returns; it is a tether to home, a hedge against the day one might go back, a way of keeping a foot in two economies at once. The RBI is betting that sentiment, sharpened by genuinely competitive rates, will do the rest. With NRE outstanding deposits at $7.94 billion and FCNR(B) at $946 million on the books as of FY26, even a modest surge of fresh inflows would register.

There is a cooler-headed caveat for anyone tempted to act in haste. The window is short—just over three months—and rates this high are explicitly a crisis-era tool, not a permanent fixture. Locking in a five-year FCNR(B) deposit at 7% in dollars is attractive precisely because it is unusual; once the rupee stabilises and the swap subsidy lapses, the caps return. Tax treatment also varies by country of residence, and American depositors in particular must weigh FBAR and FATCA reporting before moving large sums. The deposits are repatriable, but the paperwork is not optional.

For now, the message from Mumbai is unambiguous. The diaspora's wallet is being courted, the terms are the best in years, and the clock is running until September 30th."""

article2_body = """Every community measures its own arrival in different ways. For the Association of Indians in America, the oldest national Indian-American organisation in the United States, the measuring stick this month was a stack of congratulatory letters. As the group swore in its National Executive Committee for the 2026-27 term at a ceremony in New York, the screen behind the stage filled with proclamations: from New York Attorney General Letitia James, from Senator Chuck Schumer, from India's Ambassador Vinay Kwatra, from the Consul General in New York, and from a roll-call of county comptrollers, congressmen and town supervisors.

Half a century ago, an Indian-American association would have struggled to get a single such letter. The fact that a community-group inauguration now draws written tribute from a sitting US senator and a state attorney general is itself the story—a quiet index of how far the diaspora has travelled from outsider to constituency worth courting.

## A new slate

Nilima Madan was sworn in as National President, leading a committee that included Vice Presidents Sunil Mehra and Dr Binod Verma and Treasurer Gobind Bathija. The evening, held despite poor weather, drew members in person and over Zoom from across several states—a logistical detail that doubles as a portrait of a community now too dispersed to fit in one ballroom.

The AIA occupies an unusual place in the diaspora's institutional landscape. Founded in 1967, it predates most of the alphabet soup of regional and professional associations that now blanket Indian-American life, and it has long styled itself as a pan-Indian body rather than a linguistic or sectarian one. That positioning has aged well. As newer organisations splinter along the lines of state, language or profession, a group that simply claims to speak for "Indians in America" retains a certain convening power.

## The choreography of belonging

The ceremony's programme was a study in dual identity rendered as ritual. A rendition of the American national anthem opened the proceedings, followed by a classical Kathak performance, and then the Indian national anthem—the two flags, in effect, standing side by side without apology. This is the choreography the diaspora has perfected over decades: not a choice between two countries but a practised fluency in both, performed at every gala, every Diwali function, every swearing-in.

Among those present was Padma Shri Sudhir Parikh, the physician-publisher whose presence at such events has become a kind of institutional blessing, alongside trustee Naveen Shah. The guest list, like the letters, functioned as a census of influence—who in the community could be summoned, and who in the wider political establishment thought it worth their while to send regards.

## Why the small ceremonies matter

It is easy to be cynical about community galas, with their interchangeable speeches and their proclamations printed on heavy stock. But the machinery they represent is real. Organisations like the AIA are the connective tissue between a scattered immigrant population and the levers of American civic life. They are where a first-generation engineer learns to lobby a county legislator, where a second-generation lawyer is introduced to a consul general, where the abstract idea of "the community" acquires officers, a treasury and a calendar.

The structural significance is in the relationships, not the rhetoric. A new National President takes office with a Rolodex that now reaches into the offices of senators and state officials, and a mandate to keep those channels open. For a diaspora that has graduated from seeking recognition to expecting it, that continuity is the point.

What the AIA's inauguration confirmed is less a single milestone than a steady state. The Indian-American community has reached the stage where its internal transitions—who runs which association, who is sworn in by whom—are accompanied by the formal good wishes of the American state. The novelty has worn off, which is precisely the achievement. Belonging, in the end, looks a lot like being taken for granted by the people whose letters used to be impossible to get."""

article3_body = """France is about to acquire something it has never had: a traditional Hindu temple, carved from Indian stone, assembled on French soil. The BAPS Swaminarayan Mandir in Bussy-Saint-Georges, on the eastern edge of Paris, will be inaugurated in September with a 13-day "Festival of Culture" that organisers say will draw devotees and well-wishers from around the world. For the roughly several hundred thousand people of Indian origin in France, it is more than a building. It is a permanent address.

## Stone from home

What sets the Paris mandir apart from the prayer halls and converted spaces that have long served France's Hindu community is its method of construction. The temple has been built in the traditional shilpa-shastra style, using stone sourced and hand-carved in India, then shipped and assembled in France—a technique that turns the structure itself into an act of cultural transmission. It is the same painstaking approach BAPS used for its landmark mandirs in Abu Dhabi and London, and it produces something that reads unmistakably as a piece of India set down in a foreign landscape.

The symbolism is not subtle, and it is not meant to be. A temple carved in India and rebuilt in Europe is a literal rendering of what the diaspora does with its heritage: it carries the original across an ocean and reconstructs it, stone by stone, in a new home.

## A tour with a backdrop

The timing is conspicuous. The announcement of the September inauguration arrived in the same week that Prime Minister Narendra Modi was being welcomed by an emotional Indian diaspora in Paris, the closing leg of a European tour. In his address, Modi praised the community for "brilliantly mirroring India's core values on foreign soil" and credited it with bringing India and France closer—the standard grammar of diaspora diplomacy, but freshly resonant against the backdrop of a temple rising on the city's outskirts.

The convergence is no accident. India has learned to treat its diaspora's cultural institutions as instruments of soft power, and a traditional mandir in a G7 capital is a particularly photogenic one. The Abu Dhabi temple, gifted land by the UAE leadership and inaugurated by Modi himself, set the template; Paris extends it westward into Europe.

## What a temple does

For the community that will actually use it, the geopolitics are secondary. A traditional mandir performs a long list of quieter functions: a place to mark festivals that the French calendar ignores, a venue for weddings and naming ceremonies, a weekend school where children half-fluent in their grandparents' language can absorb a little more of it, a gathering point for a population that is otherwise dispersed across the Paris region and beyond.

These are the institutions through which a diaspora keeps from dissolving. Second- and third-generation children raised in France, fluent in French and at ease in European life, acquire through such spaces a working relationship with a heritage they might otherwise know only through their parents' nostalgia. The temple becomes a classroom, a calendar and an anchor at once.

## The wider map

The Paris mandir is one node in a rapidly expanding network. Berlin recently opened the Sri Ganesha temple in Neukölln, now among the largest Hindu temples in Europe, after fifteen years of construction financed entirely by community donations totalling €1.1 million. Abu Dhabi's BAPS mandir, built on 27 acres gifted by the Emirati government, drew contributions from more than 60,000 people across nationalities. London, New Jersey and Toronto have their own landmark temples. Together they trace the geography of where the Indian diaspora has settled in sufficient numbers, and with sufficient confidence, to build in permanent materials rather than rented rooms.

That confidence is the real subject. A community erects a stone temple when it has decided it is staying—when it stops thinking of itself as a population of guests and starts behaving like one of hosts. France, with its strict tradition of laïcité and its historical wariness of conspicuous religious expression, makes that statement a particularly pointed one. The September festival, with its boat procession down the Seine and its processions through the Paris suburbs, will be the diaspora announcing, in carved Indian stone, that it intends to stay."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Made Its NRI Savings Accounts the Best Deal in Years. The Window Closes September 30.",
        "subheadline": "The RBI scrapped interest-rate caps on NRE and FCNR(B) deposits, and banks are already offering 7%. The fine print is where the diaspora should look twice.",
        "slug": make_slug("rbi-removes-rate-caps-nre-fcnr-nri-deposits-7-percent"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For overseas Indians, parking money back home has always been about more than yield. A temporary RBI relaxation now pairs that sentiment with the most competitive deposit rates in years—and a short clock.",
        "tags": ["nri", "diaspora", "fcnr", "nre", "rbi", "banking", "remittances"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/attracting-nri-inflows-rbi-temporarily-withdraws-interest-rate-ceiling-on-fresh-fcnrb-deposits/article69706000.ece"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/"},
            {"name": "Capital Market", "url": "https://www.capitalmarket.com/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33813215/pexels-photo-33813215.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Hands holding ₹500 notes; the RBI's deposit-rate relaxation is aimed at pulling NRI dollars into Indian banks.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Oldest Indian Association Swore In a New President. The Congratulatory Letters Told the Real Story.",
        "subheadline": "When a community-group inauguration draws written tribute from a US senator and a state attorney general, the diaspora has stopped seeking recognition and started expecting it.",
        "slug": make_slug("aia-national-nec-2026-nilima-madan-sworn-in-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The small ceremonies of community organisations are where a scattered immigrant population connects to the levers of American civic life. The AIA's swearing-in is a quiet index of how far Indian-Americans have travelled.",
        "tags": ["nri", "diaspora", "indian-american", "aia", "community", "new-york"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://www.theindianeye.com/"},
            {"name": "Association of Indians in America", "url": "https://www.aiausa.org/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8818580/pexels-photo-8818580.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Members of the Indian-American community in traditional attire at a festive gathering.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "France Is Getting Its First Traditional Hindu Temple, Carved in India and Rebuilt Stone by Stone Near Paris",
        "subheadline": "A community builds in permanent stone when it has decided it is staying. In a country defined by laïcité, that is a particularly pointed statement.",
        "slug": make_slug("france-first-traditional-hindu-temple-baps-paris-indian-stone"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A temple carved in India and reassembled in Europe is a literal rendering of what the diaspora does with its heritage—carrying the original across an ocean and rebuilding it as an anchor for the next generation.",
        "tags": ["nri", "diaspora", "hindu-temple", "france", "baps", "culture", "paris"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Current Affairs Adda247", "url": "https://currentaffairs.adda247.com/"},
            {"name": "BAPS", "url": "https://www.baps.org/"},
            {"name": "Sarkaritel", "url": "https://www.sarkaritel.com/"},
            {"name": "The Indian EYE", "url": "https://www.theindianeye.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9e/20230307_164826_BAPS_Shri_Swaminarayan_Mandir_Auckland.jpg",
        "image_caption": "A BAPS Shri Swaminarayan Mandir, built in the traditional carved-stone style France's new temple will share.",
        "image_attribution": "Wikimedia Commons",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
