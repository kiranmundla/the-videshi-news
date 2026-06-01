#!/usr/bin/env python3
"""NRI World writer — 2026-06-01 06:00 UTC run."""

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


# ── Article 1 ────────────────────────────────────────────────────────────────
art1_body = """New York Assemblywoman Jenifer Rajkumar did something on May 27 that does not happen often in Albany. She invited a journalist — not a CEO, not a tech founder, not a donor — to stand on the floor of the State Assembly and receive a proclamation for his work covering a community that most of American media still treats as background noise.

T. Vishnudatta Jayaraman, the founder and editor-in-chief of the South Asian Herald, walked into the Assembly Chamber in Albany and heard himself described as "a man who represents the American dream, someone who seized every opportunity, pursued excellence across continents, and used the power of journalism to inform, connect, and uplift communities." Rajkumar, the first South Asian American woman elected to state office in New York, did not mince words about why the recognition mattered.

## A Publication Born in a Void

The South Asian Herald launched in October 2024 — less than two years ago — and has already built a growing national and international readership. In a media landscape where South Asian Americans number over five million but still struggle to find coverage that goes beyond curry-and-coding stereotypes, the publication carved out a space for policy analysis, community reporting, and diaspora-focused storytelling.

Speaker Pro Tempore Pamela Hunter, who presided over the session, underlined the stakes: "Now, more than ever, we need you to be a truth seeker and teller." Assemblyman David Weprin also joined in the honour, signalling bipartisan acknowledgment of the publication's role.

The Assembly proclamation itself stated that Jayaraman "has exemplified the highest standards of journalistic integrity, intellectual inquiry, and public service, serving as an inspiration to aspiring journalists and members of the South Asian Diaspora alike."

## The Congressional Backstory

The Albany honour was not a standalone event. Days earlier, during Asian American and Pacific Islander Heritage Month celebrations on Capitol Hill, US Congressmen Jonathan Jackson, Danny Davis, Shri Thanedar, and Suhas Subramanyam honoured Jayaraman with a Congressional Record entry and a commemorative medal through an event organised by Global Eye magazine. Earlier still, the Virginia State Senate had unanimously passed a resolution commending his "dedication to foreign policy and journalism," and the New York City Mayor's office had issued its own citation.

The pattern is worth noting: legislative bodies at the municipal, state, and federal level are all, independently, recognising that South Asian diaspora media is no longer a niche curiosity. It is becoming civic infrastructure.

## Why Diaspora Media Matters Now

For the 5.1 million Indian Americans in the United States — a community that pays an estimated five to six per cent of all US income taxes despite making up just 1.5 per cent of the population — mainstream media coverage remains sporadic and often reactive. Temple vandalism makes the news. Hate crime statistics get a paragraph. But the daily texture of diaspora life — community organisations, school board races, tax compliance headaches, property disputes back in India — rarely registers.

Publications like the South Asian Herald fill that gap. They are not competing with the New York Times for scoops; they are doing the patient, unglamorous work of documenting a community's evolution in real time. When Rajkumar called the Herald "a vital voice for a dynamic and influential community," she was not offering a courtesy compliment. She was describing a structural need.

Jayaraman's own trajectory mirrors that need. Originally from Chennai, he worked at the Hindustan Times, The Tribune, and The Sunday Observer in New Delhi before moving to the United States. He spent time at the United Nations Department of Public Information and served as Washington bureau chief for News India Times. The South Asian Herald is the culmination of a career spent navigating two media ecosystems — and recognising that neither one adequately serves the people living between them.

## The Quiet Test Ahead

Recognition from legislatures is gratifying, but the harder question for diaspora media is sustainability. Community publications have historically struggled with advertising revenue, reader retention, and the perennial tension between covering news and advocating for the community. The South Asian Herald's trajectory over the next two years will say more about the viability of diaspora journalism in America than any proclamation can.

For now, the fact that Albany's Assembly Chamber paused its business to acknowledge a journalist covering a community that most of American politics takes for granted — that, at least, is new."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "New York's State Assembly Just Honoured a Diaspora Journalist on Its Floor. It Was Not a Courtesy Visit.",
    "subheadline": "T. Vishnudatta Jayaraman, founder of the South Asian Herald, received a proclamation from the first South Asian American woman elected to state office in New York. The recognition points to something larger about who gets to tell the diaspora's story.",
    "slug": make_slug("ny-assembly-honours-south-asian-herald-jayaraman-diaspora-media"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The recognition of a South Asian diaspora journalist by the New York State Assembly signals that diaspora media is being acknowledged as civic infrastructure — not a niche curiosity — for five million Indian Americans whose daily lives remain largely invisible in mainstream coverage.",
    "tags": ["nri", "diaspora", "media", "journalism", "south-asian-herald", "new-york", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "South Asian Herald", "url": "https://southasianherald.com/new-york-state-assembly-honors-t-vishnudatta-jayaraman/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/politics/3393531-indian-american-journalist-recognized-by-new-york-state-assembly"},
        {"name": "New York News Beep", "url": "https://newsbeep.com/indian-american-journalist-vishnudatta-jayaraman-felicitated-at-new-york-state-assembly/"},
        {"name": "National Press Club", "url": "https://www.press.org/news/member-recognized-achievements"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Interborough_Express_Advancing_from_Planning_to_Active_Phase_%2854693464068%29_%28Jenifer_Rajkumar%29.jpg",
    "body": art1_body,
    "is_editorial": False,
}


# ── Article 2 ────────────────────────────────────────────────────────────────
art2_body = """On Easter Sunday in April, more than fifty Indian American residents of Frisco, Texas gathered at a local pizza place for coffee, samosas, and a conversation about storm drains.

That sentence sounds mundane. In the context of what has been happening in Frisco over the past year, it was an act of quiet defiance.

The Indian American Public Affairs Council (IAPAC) of North Texas hosted its inaugural "Conversation Over Coffee" forum, putting Frisco City Council and school board candidates across the table from the community they would govern. The moderators were a physician and a journalist. The topics were infrastructure, school funding, and diversity on decision-making boards. There were no chants, no counter-protests, no viral confrontations. Just questions.

## What They Were Answering

To understand why a coffee forum matters, you need to understand what has been happening in Frisco's city council chambers.

For months, a contingent of residents and outside agitators have swarmed council meetings to oppose the construction of Hindu temples and a mosque, framing demographic change in the city as a coordinated invasion. At a recent meeting, one speaker told the council that "the Hindus and the Muslims are teaming up to take over Texans" and that "your replacement is here, Americans." The language tracked closely with the "great replacement" conspiracy theory — a fringe idea that a 2022 AP-NORC poll found roughly one in three American adults now believe in some form.

Government data shows that Indians and other Asians now make up about 33 per cent of Frisco's population, up from 10 per cent in 2010. Critics have linked this growth to the H-1B visa programme, noting that about 75 per cent of H-1B visas go to Indian professionals. Texas Governor Greg Abbott's order freezing state hiring of H-1B workers gave the rhetoric additional political cover.

India West reported that one speaker at a council meeting described the situation as a "massive Indian takeover." Shanthan Toodi, a US Army veteran who served in Iraq and Afghanistan, pushed back: while visa fraud should be addressed, framing the issue as an Indian takeover was wrong. Frisco Mayor Jeff Cheney also defended the city's diversity: "Other than a handful of native Frisconians, every one of us is from somewhere else."

## The IAPAC Playbook

Against this backdrop, IAPAC's strategy was deliberate. Rather than organising counter-rallies or launching social media campaigns, the group chose the most unglamorous possible response: civic education.

Dr. Roopa Gir, IAPAC's president, opened the forum by outlining the organisation's mission — fostering civic engagement, promoting transparency in governance, and supporting community-rooted leadership. The group's North Texas leaders, Dr. Shehzad Batliwala, Ashish Patel, and Gitesh Desai, emphasised inclusive participation in "one of the fastest-growing cities in Texas."

The candidates who showed up engaged on substance. Gopal Ponangi noted that "45 per cent of Frisco ISD is Asian — yet we see very little representation on decision-making boards." Dr. Amit Kalra argued for culturally responsive education and mental health support: "Test scores don't always reflect intelligence. Equity includes emotional and cultural factors too."

When asked to define leadership, candidate Sangita Dutta offered a line that could have been aimed at the city council chambers: "Leadership is taking important decisions even if you stand alone — owning mistakes, learning, and growing from them."

## The Broader Pattern

Frisco is not an isolated case. Across the US, rapidly growing Indian American communities are navigating a tension between demographic momentum and political backlash. In Georgia, five South Asian candidates won primaries in a single week. In Howard County, Maryland, Indian Americans are the largest immigrant minority, and their cultural association recently sought $600,000 in state bond funding for a permanent community space. In New Jersey, Middlesex County's Indian population has reshaped entire school districts.

The common thread is that Indian Americans are learning — sometimes the hard way — that economic success does not automatically translate into political representation or social acceptance. The H-1B programme delivered professional mobility; it did not deliver belonging. That requires a different kind of work: showing up at school board meetings, running for local office, hosting coffee forums where candidates have to answer questions from the people whose taxes fund the roads.

## The Stakes in Frisco

IAPAC's forum was a first step, not a solution. The anti-Indian rhetoric in Frisco has not disappeared, and the city council still has no authority over federal visa policy — the issue that ostensibly drives the anger. What the forum did was establish a precedent: that Indian Americans in Frisco are not going to respond to exclusion by retreating into private enclaves. They are going to show up, ask questions, and — eventually — run for the seats themselves.

The event closed with Gitesh Desai thanking Pradeep Patel, who donated the venue and provided Iranian tea and refreshments. It was, by any measure, a small gathering. But in a city where Indians are being told they do not belong, fifty people drinking coffee and talking about storm drains is its own kind of statement."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "In Frisco, Texas, Indian Americans Are Answering 'Great Replacement' Rhetoric With Voter Guides and Coffee",
    "subheadline": "While anti-Indian agitators flood city council meetings with conspiracy theories, the Indian American Public Affairs Council is choosing the unglamorous path: civic engagement, one candidate forum at a time.",
    "slug": make_slug("frisco-texas-indian-americans-civic-engagement-iapac-backlash"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Frisco captures a tension playing out across the US: Indian Americans who arrived on professional visas now discovering that economic integration does not guarantee social acceptance, and that the fight for belonging happens in school board meetings and city council chambers, not just corporate boardrooms.",
    "tags": ["nri", "diaspora", "civic-engagement", "frisco", "texas", "iapac", "hate-crime", "indian-american", "politics"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/04/22/iapac-hosts-inaugural-conversation-over-coffee-in-frisco-texas/"},
        {"name": "India West", "url": "https://www.indiawest.com"},
        {"name": "Quorum Report / Dallas Observer", "url": "https://www.quorumreport.com"},
        {"name": "The Indian EYE (temple defacement)", "url": "https://theindianeye.com/2024/01/alarm-bells-as-hate-speech-and-crimes-against-hindus-on-the-rise-across-us-and-canada/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7103112/pexels-photo-7103112.jpeg",
    "body": art2_body,
    "is_editorial": False,
}


# ── Insert ────────────────────────────────────────────────────────────────────
articles = [art1, art2]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
