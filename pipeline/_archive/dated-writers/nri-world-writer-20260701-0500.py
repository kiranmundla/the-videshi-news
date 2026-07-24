#!/usr/bin/env python3
"""NRI World writer — 2026-07-01 05:00 PDT batch."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────
# ARTICLE 1
# ──────────────────────────────────────────────

article1_body = """As firecrackers are loaded into barges along the Potomac and folding chairs staked out on lawns from Baltimore to Boston, a quieter preparation is under way in community halls and consulate ballrooms halfway around the world. America is turning 250, and the Indian diaspora — four million strong in the United States alone — is marking the moment in a way that only a community with two national anthems in its heart can.

## Two Curtain-Raisers, Two Continents

In Mineola, New York, more than 250 people packed the Theodore Roosevelt Executive & Legislative Building last week for the curtain raiser of the 15th India Day Parade USA 2026. The annual parade, which will roll through the streets later this summer, commemorates the 80th anniversary of India's independence — but this year, the planning committee made a point of weaving America's semiquincentennial into the programme.

"The India Day Parade has become one of the region's most significant celebrations of Indian heritage, bringing together people from all backgrounds to honour the values of freedom, unity, diversity, and community service," said Pradeep Tandon, the parade's general secretary. More attendees stood along the walls when the seats ran out.

Simultaneously, across the Atlantic and the Arabian Sea, the US Embassy hosted celebrations in Chennai and Hyderabad under the banner of "250 Years of American Freedom." US Ambassador Sergio Gor described the Chennai gathering as "a spectacular evening," praising the Indian guests drawn from government, industry, academia, sports, and culture across southern India. In Hyderabad, Gor underscored a bilateral relationship that now touches nearly every domain.

"If you pick any item around the world, India and the United States are already partnered or will be partnered on it. Whether it's space, whether it's ocean, whether it's defence, whether it's pharmaceuticals, whether it's trade — no matter the item," Gor said.

## The Tall Ship, the Ambassador, and the Lieutenant Governor

India's contribution to the semiquincentennial is also arriving by sea. INS Sudarshini, the Indian Navy's sail training ship, docked in Baltimore last week after a five-month, 13,000-nautical-mile transoceanic voyage from Kochi. The ship is taking part in Sail250 Maryland, a tall-ship gathering commemorating the 250th.

Aboard, the crew hosted India's Ambassador to the United States, Vinay Mohan Kwatra, and Maryland's Lieutenant Governor, Aruna Miller — herself of Indian descent. Miller's presence put a fine point on the diaspora's arc: from arrival to leadership, celebrated on both nations' decks.

## A Summer of Dual Calendars

For most Indian Americans, this summer is a double feature. The Fourth of July is three days away, and the India Day parades — in New York, Chicago, the Bay Area, and dozens of smaller metros — will begin rolling before August 15, India's own Independence Day. Between the two dates sit barbecues with samosas on the side table, Bollywood playlists at fireworks parties, and Sunday-school rehearsals for patriotic dance numbers in both Hindi and English.

The FIA-Chicago recently held its own independence day celebration, drawing over 550 people for a cultural showcase that concluded with a three-hour tribute to the legendary Bollywood lyricist Sahir Ludhianvi. Community awards were handed out, patriotic medleys were sung, and dinner was served — in that specifically diaspora order where the programme always runs longer than planned because no one wants to leave.

## What the 250th Means for a Community Still Writing Its Chapter

When America celebrated its bicentennial in 1976, the Indian-American population numbered in the low hundreds of thousands. Today it is the country's highest-earning and most educated ethnic group, with representation in Congress, corporate C-suites, space agencies, and state houses. Maryland's lieutenant governor standing aboard an Indian naval vessel in Baltimore Harbour is not just protocol — it is the visible product of five decades of migration, work, and belonging.

The semiquincentennial arrives at an interesting inflection. Indian Americans are simultaneously more established than ever — and more anxious about belonging than they have been in years, as anti-Asian sentiment, targeted online hate, and policy debates around immigration test the community's footing. Celebrations like the India Day Parade and the Embassy's Freedom 250 events serve a function beyond pageantry. They are public, joyful assertions that the diaspora's story is part of the American story.

As the fireworks go up this Friday, a fair number of Indian Americans will be watching them while fielding WhatsApp video calls from relatives in India who want to see the show. Dual calendars, dual time zones, dual belonging. At 250, America is big enough for both flags."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "America Turns 250. The Indian Diaspora Is Celebrating with Both Flags.",
    "subheadline": "From a packed curtain raiser in Mineola to a tall ship in Baltimore Harbour, Indian Americans are weaving their story into the semiquincentennial — while already rehearsing for India's 80th.",
    "slug": make_slug("america-250th-indian-diaspora-both-flags-celebrations"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Indian-American community is uniquely positioned this summer, celebrating America's 250th birthday while preparing for India's 80th Independence Day — a dual-calendar life that defines the diaspora experience.",
    "tags": ["nri", "diaspora", "july-4th", "india-day-parade", "semiquincentennial", "celebrations", "community"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com"},
        {"name": "Swadesi News", "url": "https://swadesi.com"},
        {"name": "Nation Press", "url": "https://nationpress.com"},
        {"name": "South Asian Herald", "url": "https://southasianherald.com"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/18004815/pexels-photo-18004815.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A colourful Indian-American parade with participants waving national flags and celebrating together",
    "image_attribution": "Pexels",
    "body": article1_body,
}

# ──────────────────────────────────────────────
# ARTICLE 2
# ──────────────────────────────────────────────

article2_body = """In the span of three weeks, three Hindu temples in the San Francisco Bay Area have been targeted — two defaced with pro-Khalistan graffiti, a third hit by theft. The incidents are not random. They are a pattern, and the community knows it.

## The Sequence

The first strike hit the Shri Swaminarayan Mandir in Newark, California. Black-ink graffiti bearing anti-India and anti-Hindu slogans appeared on an exterior wall. A devotee who lives nearby discovered the vandalism and alerted the temple administration. Newark police opened an investigation. The US State Department's Bureau of South and Central Asian Affairs publicly condemned the act.

"We condemn the vandalism of Shri Swaminarayan Mandir Hindu Temple in California. We welcome efforts by the Newark Police Department to ensure that those responsible are held accountable," the bureau wrote on X.

Two weeks later, the Vijay Sherawali Temple in Hayward — barely twenty miles south — was defaced in what the Hindu American Foundation described as a "copycat" attack. Pro-Khalistan graffiti, same medium, same message. Between the two, the Shiv Durga temple in the same corridor was burgled.

Three temples. Three weeks. One stretch of the East Bay.

## The Broader Map

The Bay Area cluster is not happening in a vacuum. A report by the Center for the Study of Organized Hate, a Washington, D.C.-based nonprofit, found that anti-Indian posts on X received more than 280 million views over a ten-week span last year. The rhetoric frames Indians as "invaders" and "job thieves" — language rooted in the great replacement theory that has fuelled anti-immigrant violence for years but has now found a specific Indian-origin target.

In Frisco, Texas — a Dallas suburb where the Indian-American population has surged — residents have described a campaign of coordinated intimidation. Activists with cameras showed up at Costco and the local Hindu temple, filming shoppers and demanding to know where they were born. An Indian Boy Scout troop was mocked online. City council candidates with Indian names were derided. "In the digital economy, these influencers know that bashing Indians and promoting bigotry gets you clicks and attention," said Raqib Naik, the centre's executive director.

## The Institutional Response

India's External Affairs Minister S. Jaishankar acknowledged the California incidents during a recent public exchange. "As you know, we are concerned about this. Extremists and separatist forces outside India should not get space," he said, noting that the Indian consulate had lodged complaints with both the US government and local police.

The Hindu American Foundation has urged temples across the country to install security cameras and alarm systems. The organisation said it is in contact with temple leaders in the Bay Area and coordinating with law enforcement. "Another Bay Area Hindu temple attacked with pro-Khalistan graffiti," HAF wrote on X. "HAF is in touch with temple leaders and in contact with the police."

## What the Diaspora Feels

For the four million Indian Americans who call the United States home, the temple is more than a place of worship. It is a community anchor — a weekend language school, a festival venue, a place where grandparents feel at home and children learn to pronounce Sanskrit shlokas they will carry unevenly into adulthood. An attack on a temple is an attack on that entire ecosystem.

The anxiety is compounded by a paradox that defines diaspora life in 2026. Indian Americans are, by most statistical measures, the most successful immigrant group in the country: highest median household income, highest educational attainment, disproportionate representation in technology, medicine, and finance. Yet success has not purchased safety. If anything, visibility has made the community a target.

The Bay Area, home to one of the densest concentrations of Indian Americans in the country, has long felt like a sanctuary. The Swaminarayan Mandir in Newark and the Sherawali Temple in Hayward are not fringe rural outposts. They sit in the heart of Silicon Valley's commuter belt, surrounded by tech campuses and good school districts — the exact geography the diaspora chose because it felt safe.

## What Comes Next

Temple administrators are quietly upgrading security. Community organisations are circulating best-practice guides. Parents in group chats are debating whether to tell their children or shield them. These are the calculations that follow every incident — not dramatic, not televised, but corrosive in the way dripping water is corrosive.

No arrests have been made in any of the three Bay Area cases. The investigations continue. The temples have cleaned the graffiti and reopened. The devotees have come back. They always do. But the question Sunayana Dumala asked after her husband Srinivas Kuchibhotla was shot dead in a Kansas bar in 2017 — "Do we belong?" — still has no comfortable answer. The spray paint on a Newark temple wall, seven years later, is a fresh coat of the same question."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Bay Area Temples Hit in Three Weeks. The Diaspora Is Running Out of Cheeks to Turn.",
    "subheadline": "Pro-Khalistan graffiti at a Swaminarayan mandir, a copycat attack in Hayward, and a burglary at a third temple have shaken Silicon Valley's Indian-American heartland — and renewed a question the community has never been able to put down.",
    "slug": make_slug("bay-area-hindu-temples-attacked-khalistan-graffiti-diaspora-safety"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Bay Area temple attacks strike at the heart of the Indian-American community's sense of belonging — raising the question of whether success and visibility have made the diaspora a target rather than a shield.",
    "tags": ["nri", "diaspora", "hate-crimes", "hindu-temple", "bay-area", "khalistan", "community-safety"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com"},
        {"name": "Hindu American Foundation", "url": "https://www.hinduamerican.org"},
        {"name": "US State Department", "url": "https://www.state.gov"},
        {"name": "Center for the Study of Organized Hate", "url": "https://csohate.org"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/BAPS_Mandir_Chino_Hills.jpg/1280px-BAPS_Mandir_Chino_Hills.jpg",
    "image_caption": "A BAPS Swaminarayan Mandir in California, similar to the temples targeted in the Bay Area attacks",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
