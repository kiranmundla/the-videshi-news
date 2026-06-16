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

# ---------------------------------------------------------------------------
# ARTICLE 1 — DESIFEST Toronto turns 20
# ---------------------------------------------------------------------------
body1 = """Twenty years ago, a South Asian artist in Toronto who wanted a stage had two options: a community-hall talent show in front of relatives, or nothing. The mainstream festival circuit did not have a slot for a Punjabi rapper or a Carnatic-fusion act, and the diaspora's own institutions were built around temples, gurudwaras and the cricket league, not the music industry. So in 2006, a former tech entrepreneur named Sathish Bala built the slot himself. He called it DESIFEST.

On June 19 and 20, that grassroots experiment marks its twentieth anniversary at Sankofa Square — the downtown plaza most Torontonians still call Yonge-Dundas — and for the first time in its history it runs across a full weekend rather than a single afternoon. The expansion is the headline, but it is not the story. The story is what two decades of one free festival reveal about how a diaspora builds cultural infrastructure when no one else will.

### The economics of a stage

The numbers DESIFEST cites are the kind that make city cultural departments pay attention. Since 2006, the festival says it has put more than 1,000 artists on stage, drawn upward of 60,000 live attendees a year, and channelled over C$3 million into cultural development. In 2024 it claims a digital reach of 45 million. For a festival that charges nothing at the gate, those are not vanity metrics — they are the argument that persuades a bank to write a cheque.

That bank is TD, back again as Premier Sponsor. Corporate money in diaspora culture is often treated with suspicion, a logo bolted onto a Diwali mela. But the more revealing detail is what TD funds: not just the June weekend but a year-round pipeline — Open Mic Season 4, the intimate "Sofa Sessions," the development track that moves a performer from a coffee-shop microphone to the Sankofa main stage. The festival's pitch, in other words, is that it is not an event but a career ladder.

### Where culture meets the world

This year's theme — "Where South Asian Culture Meets the World" — reads like marketing copy until you look at the lineup logic behind it. Over twenty years DESIFEST has programmed Bollywood, Punjabi, Bangla, Carnatic fusion, hip hop and R&B on the same bill, a range that mirrors the actual demographic spread of the GTA's South Asian population rather than a single regional or linguistic bloc. That breadth is itself a diaspora statement. In the subcontinent, a Bangla act and a Punjabi act and a Tamil act belong to different industries, different languages, different markets. In a Toronto plaza on a Saturday afternoon, they share a stage and an audience that has stopped sorting itself by mother tongue.

For second-generation South Asian Canadians, that is the quiet inheritance DESIFEST offers — a version of "desi" identity that is pan-South-Asian by default, assembled in Scarborough and Brampton and Mississauga rather than imported intact from any one home town.

### Twenty years is not nothing

Cultural festivals in the diaspora tend to follow a predictable arc: a burst of founder energy, a few good years, then a slow fade as the volunteers age out and the second generation drifts. That DESIFEST has not just survived but doubled its footprint at twenty puts it in rare company. The festival now sits alongside Toronto's other ethnic-cultural anchors as proof that a South Asian event can hold prime downtown real estate on a summer weekend and fill it.

"For 20 years, DESIFEST has been the heartbeat of the South Asian diaspora in Canada," Bala said in announcing the anniversary. "This is about honouring our roots while aggressively spotlighting the global future of South Asian music."

The word that matters there is "aggressively." DESIFEST has always carried a chip on its shoulder — the conviction that South Asian talent deserves a real industry, not a charity slot. Two decades in, with a major bank's logo on the banner and a downtown square booked for two days, that chip looks less like grievance and more like a business plan that worked.

The festival is free, open to the public, and runs June 19 and 20 at Sankofa Square in downtown Toronto."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Twenty Years Ago, Toronto Had No Stage for South Asian Artists. So One Man Built DESIFEST.",
    "subheadline": "Canada's largest South Asian music festival turns 20 this weekend, expanding to two full days at Sankofa Square — and quietly proving a diaspora can build its own cultural industry.",
    "slug": make_slug("desifest-toronto-20-years-south-asian-music-festival-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "DESIFEST is a case study in how a diaspora builds cultural infrastructure from scratch — a pan-South-Asian identity assembled in the GTA's suburbs rather than imported from any one home region, and a career ladder for second-generation artists the mainstream circuit ignored.",
    "tags": ["nri", "diaspora", "canada", "toronto", "desifest", "south-asian", "culture", "music"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "EIN Presswire (DESIFEST announcement)", "url": "https://globalization.einnews.com/pr_news/913331610/desifest-marks-20-years-of-south-asian-culture-at-sankofa-square-june-19-20-2026"},
        {"name": "DESIFEST", "url": "https://desifest.ca"},
    ]),
    "score_total": 72,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Bhangra_dancers.jpg/1280px-Bhangra_dancers.jpg",
    "image_caption": "Bhangra dancers perform — the Punjabi folk form is a staple of South Asian diaspora festivals like Toronto's DESIFEST.",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": body1,
}

# ---------------------------------------------------------------------------
# ARTICLE 2 — Indian community in Brazil
# ---------------------------------------------------------------------------
body2 = """There are roughly 4,000 people of Indian origin in Brazil — a rounding error against the 32 million Indians scattered across the planet, and a fraction of the millions in the Gulf or the United States. Yet over the past month this tiny community has staged a street carnival on São Paulo's most famous avenue, lit lamps at a Diwali mela that drew Brazilians in the thousands, and choreographed a tribute performance that left the Prime Minister of India visibly moved. Smallness, it turns out, is not the same as invisibility.

### A welcome built over Zoom

When Narendra Modi arrived in Rio de Janeiro, the women who greeted him had never rehearsed in the same room. They came from São Paulo, Campinas and Rio — three cities hundreds of kilometres apart — and they had coordinated a dance set to patriotic songs entirely over video calls and shared tutorials.

"These are women with jobs, small children, and daily responsibilities, but they came together because they believed in the cause," said Gyaneshree Karahe, one of the organisers. Her ten-year-old son, Jayesh, portrayed Modi in the final sequence. The Prime Minister, she recalled, "couldn't stop himself from clapping."

For a diaspora this dispersed, that logistical detail is the real headline. There is no Little India in Brazil, no dense neighbourhood where community happens by proximity. Connection has to be manufactured — over WhatsApp groups, weekend drives between cities, and the gravitational pull of an embassy event.

### The carnival that became "sambra"

Nowhere is the blending more literal than at Bloco Bollywood, the street carnival that has rolled down São Paulo's Rua Augusta every year since 2016. Created by the Indo-Brazilian couple Shobhan Saxena and Florencia Costa, it began as a way to coax the local Indian community into Brazil's signature cultural ritual — the street bloco — and to show off Indian culture to curious Brazilians.

It worked, and then it mutated. Brazilian drummers learned to play bhangra beats on samba instruments, a hybrid the organisers christened "sambra." The dancers performing Bollywood numbers are, increasingly, not Indian at all but Brazilians trained at the Swami Vivekananda Cultural Centre. Iara Ananda, a pioneer of Bollywood dance in Brazil, has been nicknamed the "Bollywood Queen" by the very community whose culture she has adopted.

"We started this bloco to encourage the Indian community to participate in the street carnival," Saxena has said. "But with the enthusiastic participation of Brazilians, the bloco has become a mixture of two cultures." That is an unusual outcome. In most of the diaspora, cultural transmission runs one way — Indians keeping their traditions alive in a foreign land. In São Paulo, the traffic is two-directional, and the host society has become a co-author.

### Lamps under an overcast sky

The same dynamic played out at the recent Diwali mela, inaugurated with a lamp-lighting ceremony by India's Consul General in São Paulo, Manisha Swami, alongside the president of the India-Brazil Chamber of Commerce. "It is really great to see such a big turnout despite inclement weather," Swami told the crowd, as community members joined a Lakshmi aarti and a garba troupe led by Seema Patel opened a two-hour cultural programme that ran until the fireworks.

For a community of a few thousand, fielding professional-grade tabla players, multiple dance troupes and a fireworks finale is not a casual undertaking. It requires nearly everyone to do something.

### Why a rounding error matters

The instinct is to file Brazil's Indians under curiosity — too few to register in remittance tables or diaspora-vote calculations. But the community is doing something the larger, more comfortable diasporas often stop doing: it is actively recruiting the host society into Indian culture, and being changed by it in return. The result is not a preserved museum-piece Indianness but a living, hyphenated one — Indo-Brazilian, sambra and all.

When the next Indian Prime Minister's plane touches down in Brazil, the welcome will again be assembled over Zoom calls between three cities. That it happens at all, in a country with no Little India and barely 4,000 of them, is the point."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "There Are Only 4,000 Indians in Brazil. They Just Threw a Street Carnival, a Diwali Mela, and a Welcome That Moved a Prime Minister.",
    "subheadline": "With no Little India to anchor them, Brazil's tiny Indian diaspora manufactures community over Zoom calls between cities — and has turned the host society into a co-author of its culture.",
    "slug": make_slug("indian-community-brazil-bloco-bollywood-diwali-sambra-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Brazil's Indian community shows what diaspora identity looks like at the smallest scale — connection manufactured across distance rather than inherited by proximity, and a rare two-way cultural exchange where Brazilians have become co-authors of Indian tradition (the 'sambra' hybrid), not just spectators.",
    "tags": ["nri", "diaspora", "brazil", "sao-paulo", "bloco-bollywood", "diwali", "culture"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE — How Indian diaspora welcomed PM Modi in Brazil", "url": "https://theindianeye.com/"},
        {"name": "The Indian EYE — Bloco Bollywood, São Paulo", "url": "https://theindianeye.com/2023/02/21/bloco-bollywood-dazzles-with-diversity-of-music-dance-and-honors-indian-women/"},
    ]),
    "score_total": 70,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8566097/pexels-photo-8566097.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A performer in Indian classical dress — Bollywood and folk dance anchor the Indian community's cultural events in Brazil.",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": body2,
}

# ---------------------------------------------------------------------------
# ARTICLE 3 — Gulf diaspora as stabilizer
# ---------------------------------------------------------------------------
body3 = """The metric that has always defined the nine million Indians in the Gulf is the remittance — the money order home, the line item in India's balance of payments. It is a flattering number and a reductive one. It measures what the diaspora sends back, never what it holds together where it actually lives. The events of recent months in West Asia have made the second, harder-to-quantify role impossible to ignore.

### When formal systems lagged

As tension across the region disrupted travel routes, rattled energy markets and seeded waves of misinformation, the official machinery — consulates, evacuation protocols, government helplines — moved at the speed governments move. Into the gaps stepped something older and faster: the informal network.

According to a recent assessment, resident welfare associations, business groups and volunteer collectives across the Gulf mobilised within hours, not days. They arranged shelter for stranded workers, coordinated transport for those who needed to relocate within the region, and pushed real-time, verified information to communities drowning in rumour. The diaspora, in the report's framing, "evolved from economic contributor to community backbone."

The phrase is worth pausing on. Nearly 3.5 million Indians live in the UAE alone; across the wider Gulf the number exceeds nine million, one of the largest expatriate populations anywhere on earth. For decades that community has built the cities, staffed the hospitals and run the logistics. What the recent crisis exposed is how much of the region's day-to-day resilience quietly depends on it.

### The doctors who never stopped

Consider the continuity nobody noticed because nothing broke. Hospitals staffed heavily by Indian doctors and nurses kept functioning without interruption. Supply chains run by Indian managers stayed operational. In energy infrastructure and port operations — the literal arteries of the Gulf economy — Indian professionals kept critical systems running while global markets convulsed.

This is the inversion of the usual diaspora narrative. The story is normally about vulnerability: the migrant worker as the one who needs rescuing, the expatriate as a population to be evacuated. The recent picture is closer to the opposite. The Indian community was not only looked after; it was doing much of the looking-after, for itself and for the host society alike.

### Gratitude, both ways

The diplomacy has tracked the reality. India's Ambassador to the UAE, Deepak Mittal, has publicly thanked Emirati leadership for its support of the Indian community, describing the 4.5 million Indians in the country as "a vital bridge" between the two nations. Earlier, External Affairs Minister S. Jaishankar made the welfare of the diaspora the first item in his discussions with UAE counterparts, conveying the community's appreciation for "the manner in which they were looked after" — and, in the same breath, India's "major stakes" in the region's stability.

That two-way gratitude is the tell. New Delhi is no longer treating the Gulf diaspora purely as a vulnerable population to be protected, but as a strategic asset whose stability is bound up with India's own. The Emirati side, for its part, has every incentive to keep a community that anchors so much of its economy feeling secure.

### Beyond the remittance line

For the families back home, the abstraction of "Gulf stability" has a concrete face: a relative who texted to say the hospital was still running, that the welfare group had found a place to stay, that the rumours flying around social media were not true. None of that shows up in the remittance statistics that usually stand in for the Gulf diaspora's worth.

The nine million remain, in the cold language of economics, a source of foreign capital — India's single largest. But the recent months made the case that they are something more durable than a cash flow. They are infrastructure. And infrastructure, unlike a remittance, only gets noticed when it is tested."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nine Million Indians Are Usually Measured in Remittances. This Year, the Gulf Found Out What Else They Hold Together.",
    "subheadline": "When official systems lagged during West Asia's recent turbulence, the Gulf's Indian diaspora became the region's quiet backbone — staffing the hospitals, running the ports, and sheltering its own.",
    "slug": make_slug("nine-million-indians-gulf-diaspora-stabiliser-remittances-uae"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Gulf's nine million Indians are routinely reduced to a remittance figure, but the recent regional crisis revealed their deeper role as community infrastructure — and reframed how both New Delhi and Gulf governments now treat them: not a vulnerable population to evacuate, but a strategic asset whose stability is bound up with India's own.",
    "tags": ["nri", "diaspora", "gulf", "uae", "remittances", "migrant-workers", "west-asia"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IB Times — How 9 Million Indians Quietly Held The Gulf Together", "url": "https://www.ibtimes.sg/"},
        {"name": "IANS — Indian diaspora helps stabilise Gulf amid regional uncertainty", "url": "https://ianslive.in/"},
        {"name": "The Indian EYE — Ambassador Mittal on UAE support for Indian community", "url": "https://theindianeye.com/"},
    ]),
    "score_total": 74,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/BAPS_Shri_Swaminarayan_Hindu_Mandir_Night_View.jpg/1280px-BAPS_Shri_Swaminarayan_Hindu_Mandir_Night_View.jpg",
    "image_caption": "The BAPS Hindu Mandir in Abu Dhabi, a symbol of the deep ties between India and the Gulf's millions-strong Indian community.",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": body3,
}

articles = [art1, art2, art3]

ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"\u2705 {art['slug']}  ({wc} words)")
        ok += 1
    except Exception as e:
        print(f"\u274c {art['slug']}: {e}")

print(f"\n{ok}/{len(articles)} inserted")
