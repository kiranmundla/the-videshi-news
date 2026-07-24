#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

body1 = """The pitch was unusual for a fundraising dinner. Instead of the founder of a hospital network or a celebrity endorser, the man who held the room at the Sankara Eye Foundation's annual gala was a cricketer talking about sight — and a blind industrialist talking about being told he could not study science.

Sunil Gavaskar, the former India captain whose batting average is still recited from memory in living rooms across the diaspora, sat for a fireside chat alongside Srikanth Bolla, the CEO of Bollant Industries, who was born visually impaired. The pairing was the evening's emotional centre, and it did what these galas are designed to do: it loosened wallets.

**The mechanics of giving back**

Gavaskar's gimmick was simple and effective. Donors who gave more than $5,000 walked away with an autographed cricket bat; those who crossed $10,000 got a bat plus books he had written. For a diaspora audience that grew up watching him open the innings, an autographed bat is not a trinket — it is a relic. The donations followed.

"Just as a cricketer's vision is crucial on the field, sight is vital to living a full life," Gavaskar told the room. "Sankara Eye Foundation, USA is giving people a chance to regain that fundamental gift." The line is the kind of thing that reads as boilerplate on a page and lands very differently when delivered by a man the audience has watched for fifty years.

**Why this particular charity travels well**

The Sankara model is one of the more legible propositions in diaspora philanthropy. The money raised in banquet halls in New Jersey, California and Texas pays for free eye surgeries in India — cataract operations, mostly, the sort of procedure that is routine in American hospitals and life-altering when it is unavailable. For an NRI writing a cheque, the transaction is clean: a fixed sum buys a countable number of surgeries for people back home.

That legibility matters. Diaspora donors are, increasingly, sophisticated about where their money goes. Sankara Eye Foundation, USA has held a four-star rating from Charity Navigator for nine consecutive years, a credential the organisation mentions early and often. The single-event sponsor this year was Axtria, a data-analytics firm founded by Indian-Americans — itself a sign of how diaspora corporate money now underwrites diaspora causes.

**The Bolla factor**

If Gavaskar supplied the nostalgia, Bolla supplied the argument. He recounted his own journey: born blind, academically gifted, and then blocked from studying science in India because the system assumed a blind student could not. He fought a legal battle, won the right to study STEM, and went on to build a manufacturing company that employs people with disabilities.

His point was not subtle, and it was not meant to be. Vision, he argued, is not only a matter of the eyes. The foundation's mission to eliminate curable blindness in India was, in his telling, of a piece with the broader work of removing the barriers that keep capable people on the sidelines.

**The diaspora's evolving relationship with home**

There is a pattern worth noting here. The first generation of NRI philanthropy was often ad hoc — a temple donation here, a hometown school there, money sent in response to a flood or an earthquake. What galas like Sankara's represent is the institutionalisation of that impulse: recurring annual events, audited charities, named sponsorship tiers, celebrity draws.

For Indians abroad, this is partly about identity maintenance. Giving to a cause in India is a way of staying tethered to a country many left decades ago, a way of telling their American-raised children that the connection is real and has obligations attached. The autographed bat is a souvenir; the surgery in a clinic in India is the point.

The gala will be followed by others — the diaspora calendar is thick with them through the summer. But few will manage the particular alchemy of this one: a cricket legend and a blind entrepreneur, persuading a room full of immigrants that the gift of sight is worth their money.

**Sources**
"""

body2 = """The slogan is a piece of wordplay that only works if you grew up bilingual: *HungerMitao* — "wipe out hunger" in Hindi, with the verb left untranslated so the English speaker has to lean in. That small linguistic move is the whole strategy. The movement it names has just crossed a threshold that most diaspora charities never reach.

At a gala in New York attended by India's Consul General Randhir Jaiswal, volunteer philanthropists Raj and Aradhana (Anna) Asava were honoured for pledging $1 million to Feeding America, the largest domestic hunger-relief organisation in the United States. The money is not going to India. That is the entire point.

**"Give where you live"**

Most Indian-American philanthropy flows in one direction: back to the old country. Eye surgeries in Andhra Pradesh, school buildings in Gujarat, flood relief in Kerala. HungerMitao, launched in 2017, was built on the opposite premise — that the diaspora has an obligation to the country it actually lives in.

"In the spirit of 'give where you live' we invite the 4 million strong Indian diaspora in the U.S. to join us in the mission of HungerMitao and ensure no one goes hungry," Raj Asava said at the gala. It is a deliberate reframing of who the diaspora is responsible for. The premise is that an Indian-American in Houston shares a city, and a moral claim, with a hungry neighbour in Houston — regardless of where either family came from.

**The numbers**

Since its founding, HungerMitao says it has enabled 30 million meals through the Feeding America network. The movement operates through member food banks in North Texas, Houston, New York City, Atlanta and Seattle, with planned chapters in Central Texas, Connecticut, Alameda, New Jersey and the Tarrant Area.

The model is unusual in that it does not build its own infrastructure. Rather than open Indian-American food banks, HungerMitao channels community money and volunteer hours into Feeding America's existing network. It is, in effect, a diaspora fundraising and mobilisation layer bolted onto mainstream American charity — which is both efficient and quietly assimilationist.

**Why the framing matters**

"HungerMitao is as much about eradicating hunger as it is about unifying the fragmented efforts of our community and focusing it on the humanitarian cause of hunger," Anna Asava said. The word "fragmented" is doing real work in that sentence. Indian-American philanthropy is famously balkanised — by region, by language, by caste, by hometown association. A Telugu organisation and a Gujarati one may share a metro area and never coordinate.

A cause like hunger, deliberately stripped of any regional Indian identity, is one of the few things broad enough to unite them. You do not have to be from a particular state to agree that no one in your city should go hungry. That universality is a feature, not a bug.

**The political subtext**

There is a quieter argument embedded in all this, and it is about belonging. A community that is still, in many quarters, treated as perpetually foreign — the "where are you really from" crowd — is making a visible, expensive case for its own rootedness. Writing a million-dollar cheque to feed Americans is, among other things, a statement that this is home.

MR Rangaswami, founder of the diaspora network Indiaspora and himself a Feeding America donor, put it in the language of community pride. "I am so proud of Indiaspora members Aradhana and Raj Asava and inspired by how much their HungerMitao movement has accomplished for communities across the country," he said. "When we come together with passion, we can accomplish anything."

**What it signals**

The Asavas' pledge is a single data point, but it fits a trend. As the Indian-American population ages into wealth and its second generation comes of age as fully American, the centre of gravity of its giving is shifting. The reflex to send money home does not disappear — remittances remain enormous — but it is increasingly joined by a parallel impulse to invest locally.

For a diaspora that has spent decades proving its economic value, the next frontier is proving its civic value. HungerMitao, with its bilingual pun and its million-dollar cheque, is one community's answer to a question it was rarely asked but has decided to answer anyway: what do you owe the place you actually live?

**Sources**
"""

body3 = """For one Sunday each summer, a chariot the height of a building rolls down a North American street, pulled by ropes in the hands of strangers. There are drums, there is chanting, there is free vegetarian food at the end. And there is, increasingly, a crowd of non-Indians who have wandered over to see what the noise is about.

The Ratha Yatra — the chariot festival of Lord Jagannath — has quietly become one of the Indian diaspora's most visible public rituals, staged not in temple courtyards but on the main streets of cities from New York to Vancouver. This year's North American festival tour, organised under the Hare Krishna banner, runs from late spring into the autumn, hitting more than two dozen cities across the United States and Canada.

**A festival that goes outdoors**

The schedule reads like a map of where the diaspora has put down roots. New York on 13 June. Harrisburg on 20 June. Calgary on 21 June. Boston on 27 June. Montreal and Toronto in July. Vancouver and Los Angeles and San Francisco stretching into August and September. Each stop pairs the chariot procession with a "Festival of India" — stalls, food, music, and the kind of open-air spectacle designed to be watched by passers-by.

That outward orientation is the interesting part. Most diaspora gatherings are, by design, inward-looking — a temple anniversary, a regional association's gala, a language convention. They are spaces where the community talks to itself. The Ratha Yatra is the opposite. It is staged in public, it is free, and the whole architecture of the event assumes an audience that has never set foot in a temple.

**The Puri original, the diaspora copy**

The festival has a 12th-century home. In Puri, Odisha, the Ratha Yatra on 26 June this year will draw millions; three deities are placed on freshly built wooden chariots, 13 to 14 metres tall, and pulled along the Grand Road by tens of thousands of devotees. The Jagannath Temple itself is closed to non-Hindus, who may observe only from the street.

The diaspora version inverts that exclusivity. There is no temple to be barred from — the street *is* the venue, and the non-Hindu observer is not a tolerated outsider but the target audience. A festival that is, at home, hedged by centuries of ritual restriction becomes, abroad, a deliberate act of cultural outreach.

**Why the diaspora leans on it**

For immigrant parents, these festivals do a specific job. They give American- and Canadian-raised children a tangible, sensory experience of a tradition that might otherwise exist only as a story or a video call with grandparents. Pulling a chariot rope is not abstract. Neither is the food.

They also do diplomatic work the community rarely articulates out loud. A chariot festival on a closed-off downtown street, with curious locals snapping photos, is soft power of the cheapest and most effective kind. It costs the price of a permit and some volunteer hours, and it leaves a city with the impression that the Indian community is generous, colourful and unthreatening — an impression worth more than any embassy press release.

**The Canadian dimension**

The tour's Canadian legs — Calgary, Montreal, Toronto, Vancouver, Red Deer — track the country's fast-growing South Asian population, now among the most significant immigrant communities in cities like Brampton and Surrey. For these newer arrivals, many of them students and recent migrants navigating a tense immigration climate, the festivals offer something practical alongside the spiritual: a ready-made community, a free meal, and a Sunday that feels, briefly, like home.

The chariots will keep rolling through the summer, city by city, each one a small negotiation between a 900-year-old ritual and a 21st-century North American street. The deities ride; the diaspora pulls; and the neighbours, increasingly, watch.

**Sources**
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Cricket Legend and a Blind Industrialist Walked Into a Charity Gala. The Diaspora Opened Its Wallet.",
        "subheadline": "At the Sankara Eye Foundation's annual fundraiser, Sunil Gavaskar's autographed bats and Srikanth Bolla's life story turned nostalgia into surgeries for the blind back in India.",
        "slug": make_slug("sankara-eye-foundation-gala-gavaskar-srikanth-bolla-diaspora-philanthropy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Diaspora philanthropy that funds free eye surgeries in India shows how NRI giving has institutionalised — audited charities, celebrity draws, named sponsor tiers — as a way for immigrants to stay tethered to home and pass that obligation to American-raised children.",
        "tags": ["nri", "diaspora", "philanthropy", "sankara-eye-foundation", "sunil-gavaskar", "giving-back"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Sankara Eye Foundation Donor Gala", "url": "https://theindianeye.com/"},
            {"name": "Sankara Eye Foundation USA", "url": "https://www.giftofvision.org/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Anu_Ranjan%2C_Amruta_Fadnavis%2C_Sunil_Gavaskar%2C_Shashi_Ranjan_graces_the_Gr8_Beti_event_%2802%29_%28cropped_-_Gavaskar%29.jpg",
        "image_caption": "Former India captain Sunil Gavaskar, who headlined the Sankara Eye Foundation's diaspora fundraising gala",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Diaspora Famous for Sending Money Home Just Pledged $1 Million to Feed Americans Instead",
        "subheadline": "The HungerMitao movement, built on the slogan 'give where you live,' is quietly redirecting Indian-American philanthropy toward the country the community actually lives in.",
        "slug": make_slug("hungermitao-asava-feeding-america-million-diaspora-give-where-you-live"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "HungerMitao reframes who the diaspora is responsible for — arguing an Indian-American shares a moral claim with a hungry neighbour in their own US city, not only with causes back in India. It is both a unifying force across a fragmented community and a statement of belonging.",
        "tags": ["nri", "diaspora", "philanthropy", "hungermitao", "feeding-america", "indiaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Hunger Free America Gala", "url": "https://theindianeye.com/"},
            {"name": "Feeding America", "url": "https://www.feedingamerica.org/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9090903/pexels-photo-9090903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Volunteers sorting and packing food donations at a community food bank",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Each Summer, a Building-Sized Chariot Rolls Down a North American Street. That's the Whole Point.",
        "subheadline": "The Ratha Yatra has become the diaspora's most outward-facing ritual — staged on public streets from New York to Vancouver, designed for the neighbours who have never set foot in a temple.",
        "slug": make_slug("ratha-yatra-festival-tour-north-america-iskcon-diaspora-public-faith"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Unlike inward-looking diaspora gatherings, the Ratha Yatra is staged in public for a non-Indian audience — inverting the exclusivity of the Puri original, doing cheap and effective soft-power work, and giving American- and Canadian-raised children a sensory link to a tradition their parents left behind.",
        "tags": ["nri", "diaspora", "festival", "ratha-yatra", "iskcon", "culture", "canada"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Festival of India — 2026 Hare Krishna Festival Tour Schedule", "url": "https://www.festivalofindia.org/"},
            {"name": "StayVista Journal — Rath Yatra 2026", "url": "https://www.stayvista.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Swamibagh_ISKCON_Rathyatra.jpg/1280px-Swamibagh_ISKCON_Rathyatra.jpg",
        "image_caption": "Devotees pull a towering chariot during an ISKCON Ratha Yatra procession",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body3,
    },
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
