#!/usr/bin/env python3
"""NRI World writer – July 12 2026, 17:00 PT run."""

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


# ── Article 1: Indian Summer Festival 2026 ──────────────────────────────

art1_body = """\
When Am Johal chose the title *Ragas for a Ruptured World* for the sixteenth Indian Summer Festival, he was not reaching for metaphor. The Vancouver-based executive artistic director wanted a phrase that acknowledged what his audience already felt — the creeping unravelling of political consensus, ecological stability, and the social contracts that diaspora communities depend on — and then proposed art as a plausible response.

The festival, which opened on July 9 and runs through July 19 across venues in Vancouver, Burnaby, and Surrey, has become one of Canada's most distinctive cultural events: a gathering that treats South Asian arts not as heritage programming but as a live, evolving current in the country's cultural life. This year's edition brings together more than ninety Canadian and international artists for a lineup that spans comedy, live music, theatre, literature, and interdisciplinary installation work.

## Opening Night and Mainstage Performances

The opening celebration at the Vancouver Playhouse featured Sri Lankan-born, London-based comedian Vidura Bandara Rajapaksa, making his Vancouver debut as part of his *Paradise Gothic Tour*. His deadpan, postcolonial-themed humour — equal parts anthropological observation and punchline — set the tone for a festival that refuses to treat diasporic identity as either tragedy or triumph. Vancouver comedian Charlie Demers and interdisciplinary artist Priyanka "Piu" Chakrabarti, who blends raga-inspired vocals with experimental electronic sound, rounded out the evening.

Punjabi singer and composer Rashmeet Kaur made her own Vancouver debut on July 11 at *Sacred Sounds, New Worlds*, delivering a genre-blurring performance that fuses folk, Sufi, hip-hop, and R&B influences. Opening for her, Asad Khan's Sammah Project reinterpreted devotional and classical traditions with electronic flourishes — a pairing that would have been unthinkable at a South Asian festival a decade ago and now feels entirely natural.

## Comedy, Theatre, and the Diaspora Body

The second week brings two performances that wrestle with identity in visceral, embodied ways. On July 15, Indian American comedian Abby Govindan takes the stage at the Rio Theatre with *Pushing 30*, her internationally touring hour-long special exploring aging, dating, and breaking generational curses. It is the kind of material that resonates with second-generation South Asians who have spent their twenties navigating parental expectations and their thirties realising those expectations live inside them now.

From July 15 to 18, celebrated actor and playwright Anita Majumdar premieres *Why We Work Out* at The Fishbowl, a solo performance exploring how her embodied relationship with exercise has become entwined with major life events. It is a world premiere, and the kind of intensely personal, formally inventive work that Indian Summer has made its specialty.

## Sound, Gardens, and Free Programming

One of the festival's most distinctive offerings unfolded on July 13 at VanDusen Botanical Garden, where Vancouver musician Tarun Nayer's Modern Biology project transformed plant bioelectricity into live, improvised sound. The performance drew on raga and ecological systems, staging a conversation between technology and the natural world that felt less like a concert and more like an act of listening.

The festival's free programming includes the Gong Library at Ocean Artworks Pavilion — an immersive collection of gongs, chimes, and resonant instruments that visitors can play or simply sit among. Two video works by Farheen Haq are screening at Grunt Gallery's Community Art Screen. The Surrey Art Gallery hosts *Keerat Kaur: If Gardens Could Dream*, an interdisciplinary exhibition. And on July 18, Apna Mela transforms Strawberry Hill Park in Surrey into a joyful, intergenerational gathering of cultural pride and community connection.

## Closing in the Punjabi Market

The festival closes on July 19 with *Rishta*, curated by Ruby Singh, in the heart of Vancouver's Punjabi Market at the intersection of Main and 50th. The outdoor event weaves poetry, qawwali, memory, and community into an afternoon that doubles as a living archive of South Asian expression in the city.

"While the world seems to be unravelling at the seams, we are coming back to the question of what art can possibly open up in this time of necessity, storytelling, and defiance," Johal said in announcing the festival. "We will resist this time by gathering together in new ways."

For a diaspora community navigating the tensions of belonging — to a homeland increasingly distant, to a host country that oscillates between embrace and suspicion — that gathering is not decoration. It is infrastructure.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ninety Artists, Eleven Days, One Ruptured World: Inside Vancouver's Indian Summer Festival",
    "subheadline": "The sixteenth edition of Canada's premier South Asian arts festival is using comedy, raga, plant bioelectricity, and a closing ceremony in the Punjabi Market to argue that gathering is resistance.",
    "slug": make_slug("indian-summer-festival-vancouver-ragas-ruptured-world-2026"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The festival is one of North America's largest platforms for South Asian artistic expression in the diaspora — a space where second-generation identity, cross-cultural collaboration, and community building happen through art rather than politics.",
    "tags": ["nri", "diaspora", "canada", "vancouver", "arts", "culture", "festival", "south-asian"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Indian Summer Festival", "url": "https://indiansummerfest.ca"},
        {"name": "Stir Vancouver", "url": "https://createastir.ca"},
        {"name": "Drishti Magazine", "url": "https://drishtimagazine.com"},
        {"name": "Destination Vancouver", "url": "https://destinationvancouver.com"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Mamallapuram%2C_Indian_Dance_Festival%2C_Bharatanatyam_dancer_%289902464906%29.jpg/1280px-Mamallapuram%2C_Indian_Dance_Festival%2C_Bharatanatyam_dancer_%289902464906%29.jpg",
    "image_caption": "A Bharatanatyam dancer performs at an Indian dance festival",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ── Article 2: Vivek Ramaswamy Ohio Governor Race ──────────────────────

art2_body = """\
The race that was supposed to be a Republican formality has become the most closely watched governor's contest in the country — and the candidate at its centre is an Indian American biotech entrepreneur who, six months ago, was trying to remake the federal government.

On July 10, the Cook Political Report shifted the Ohio governor's race from "Lean Republican" to "Toss Up," a move that reflects both the structural oddities of Vivek Ramaswamy's candidacy and the surprising strength of his Democratic opponent, Amy Acton. A New York Times/Siena College poll released the same week found the race deadlocked at 47 per cent apiece. An AARP poll gave Acton a three-point edge; a Fox News survey had her up by a single point.

For a state that Donald Trump carried by eight points in 2024, those numbers are remarkable. For the Indian American community, they carry a different kind of weight entirely.

## The Self-Funder and the Health Director

Ramaswamy, 40, is a Cincinnati native who graduated valedictorian from St. Xavier High School before collecting degrees from Harvard and Yale Law. He founded Roivant Sciences, a biotech firm that made him a billionaire, and mounted a short-lived presidential campaign in 2024 that earned him national name recognition and a brief stint as co-head of the Department of Government Efficiency alongside Elon Musk. He left DOGE in January after his comments criticising American culture during the H-1B visa debate drew Republican ire — Musk, according to Politico, wanted him out.

His opponent is Amy Acton, 60, the Youngstown-born physician who became the public face of Ohio's COVID-19 response as state health director under Governor Mike DeWine. Her televised briefings during the pandemic made her one of the most recognised figures in the state, and her campaign has raised a record-breaking $18 million.

Ramaswamy has poured $25 million of his own money into the race and benefits from a $20 million contribution to a supporting super PAC. Cook's analysts noted, however, that "bottomless coffers like Ramaswamy enjoys have not guaranteed wins for other recent self-funders this cycle."

## Ethics Complaints and Likability Questions

The race took a procedural turn this week when Ohio Senate Democrats filed an ethics complaint alleging that Ramaswamy's campaign had failed to properly disclose roughly $500,000 in credit card payments to American Express — listing the entire sum as a single expenditure rather than itemising individual costs as state law requires. The Ohio Secretary of State's office noted the error was not uncommon, gave the campaign a one-month extension, and the filings were updated before the complaint was formally lodged.

"Vivek Ramaswamy and Rob McColley for Ohio is in full compliance with all applicable Ohio campaign finance laws," campaign spokesman Evan Machan said.

The Democratic Governors Association was less charitable: "Vivek Ramaswamy will take every chance he gets to pull a fast one on Ohioans."

Cook's more substantive concern is what it described as Ramaswamy's "clear likability problem — even some in his own party." Despite weeks of heavy advertising designed to boost his image and attack Acton's COVID-era record, polling has not shifted in his favour. Acton, meanwhile, has not yet begun airing her own ads, and her campaign war chest is growing.

## What It Means for Indian America

If elected, Ramaswamy would become one of the most prominent Indian American elected officials in the country's history, joining a roster that includes Vice President Kamala Harris, New York City Mayor Zohran Mamdani, and a growing cohort of congressional representatives including Ro Khanna, Pramila Jayapal, and Raja Krishnamoorthi.

The community's relationship with Ramaswamy is complicated. His H-1B comments — he suggested American culture "venerates mediocrity over excellence" and that tech companies hire foreign workers for that reason — alienated many Indian Americans who saw the remark as punching down at the very community he emerged from. A Carnegie survey released this week found that 71 per cent of Indian Americans disapprove of the current administration, and the community remains politically diverse in ways that do not map neatly onto Ramaswamy's brand of Republican populism.

Yet the simple fact of his candidacy — a first-generation Indian American running for governor of a major swing state, with a plausible chance of winning — represents a threshold moment. Two decades ago, Bobby Jindal's election as governor of Louisiana was treated as an anomaly. Today, Indian Americans govern, legislate, adjudicate, and now, in Ohio, they compete at parity in races that were supposed to be foregone conclusions.

The outcome in November will matter for policy — Ramaswamy has pledged to eliminate income taxes and slash property taxes, while Acton has proposed child tax credits and medical debt relief. But for a diaspora watching from both sides of the Pacific, the race already matters for what it says about where Indian Americans stand in the architecture of American power: no longer at the margins, and not yet at ease.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Billionaire, the Doctor, and the Toss-Up: Vivek Ramaswamy's Ohio Governor Race Just Got Real",
    "subheadline": "Cook Political Report shifts the Ohio race from 'Lean Republican' to a dead heat. Polls show Ramaswamy and Democrat Amy Acton locked at 47-47 in a state Trump won by eight points.",
    "slug": make_slug("vivek-ramaswamy-ohio-governor-toss-up-acton-cook"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Ramaswamy's candidacy represents a new threshold for Indian American political ambition — a first-generation Indian American competing at parity in a major swing-state governor race, while the community's relationship with his brand of politics remains deeply divided.",
    "tags": ["nri", "diaspora", "politics", "indian-american", "ohio", "elections", "vivek-ramaswamy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Cook Political Report", "url": "https://www.cookpolitical.com"},
        {"name": "The Columbus Dispatch", "url": "https://www.dispatch.com"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com"},
        {"name": "New York Times/Siena College Poll", "url": "https://www.nytimes.com"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/75/Vivek_Ramaswamy_%2855241367373%29_%28cropped%29.jpg",
    "image_caption": "Vivek Ramaswamy at a campaign event",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ── Insert ───────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
