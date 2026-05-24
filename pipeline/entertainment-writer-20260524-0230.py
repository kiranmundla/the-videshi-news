#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 02:30 PDT batch:
1. Maa Behen — Madhuri Dixit + Triptii Dimri Netflix dark comedy, June 4 premiere
2. Main Vaapas Aaunga — Imtiaz Ali's Partition-era love story with Naseeruddin Shah + Diljit Dosanjh, June 12 four-way clash
3. Score decay for old entertainment articles
"""

import json, os, uuid, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Maa Behen — Madhuri Dixit & Triptii Dimri's Netflix Dark Comedy
# ══════════════════════════════════════════════════════════════
slug1 = "madhuri-dixit-triptii-dimri-maa-behen-netflix-dark-comedy-june-4-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Madhuri Dixit Is Hiding a Dead Body on Netflix. Triptii Dimri Is Helping. 'Maa Behen' Might Be the Most Unhinged Indian Film of the Summer.",
        "subheadline": "The trailer for Suresh Triveni's dark comedy — streaming worldwide June 4 — shows a dysfunctional mother-daughter trio covering up a murder in their own living room. NRIs who grew up on Madhuri's grace are about to see something very different.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 76,
        "tags": ["Madhuri Dixit", "Triptii Dimri", "Maa Behen", "Netflix", "dark comedy", "Suresh Triveni", "Ravi Kishan"],
        "diaspora_angle": "Maa Behen streams on Netflix globally from June 4, making it instantly accessible to NRI audiences everywhere. For diaspora viewers who grew up watching Madhuri in Hum Aapke Hain Koun and Dil To Pagal Hai, seeing her in a pitch-black comedy about hiding a corpse is a genuine reinvention moment.",
        "sources": [
            {"url": "https://bollywoodhungama.com/news/bollywood/maa-behen-trailer-out-madhuri-dixit-triptii-dimri/", "name": "Bollywood Hungama"},
            {"url": "https://www.zoomtventertainment.com/bollywood/maa-behen-trailer-released-madhuri-dixit-triptii-dimri", "name": "Zoom TV"},
            {"url": "https://www.hollywoodreporterindia.com/film/maa-behen-netflix-madhuri-dixit-triptii-dimri-modern-single-mother", "name": "Hollywood Reporter India"},
            {"url": "https://en.wikipedia.org/wiki/Maa_Behen", "name": "Wikipedia"}
        ],
        "image_search_query": "Maa Behen Netflix Madhuri Dixit Triptii Dimri 2026 trailer",
        "image_entities": ["Madhuri Dixit", "Triptii Dimri", "Ravi Kishan", "Maa Behen"],
        "image_must_show": "Madhuri Dixit or Triptii Dimri from the Maa Behen trailer or poster",
        "word_count": 740,
        "body": """The trailer dropped on May 22, and within hours it was all over NRI WhatsApp groups. Not because Madhuri Dixit looked stunning — she always does — but because she was standing in a living room, staring at a dead body, and saying things that would make your aunty faint.

*Maa Behen* is a Netflix India original directed by Suresh Triveni — the man behind *Tumhari Sulu* and *Jalsa* — and it might be the most deliciously chaotic Indian film of the summer. It premieres globally on June 4.

## The Setup Is Simple. The Chaos Is Not.

The film follows Rekha (Madhuri Dixit), a mother living in the aggressively normal-sounding Adarsh Colony, and her two daughters Jaya (Triptii Dimri) and Sushma (Dharna Durgaa). These three women can barely stand each other on a good day.

Then Gupta Ji — played by Ravi Kishan at his most entertainingly ominous — dies in their living room. What follows, judging by the 2-minute-47-second trailer, is a cover-up that goes spectacularly wrong. Think lies spiralling into bigger lies, neighbourhood suspicion, police showing up, and a family whose dysfunction is both their biggest weakness and their only hope.

It's the kind of premise Suresh Triveni does better than almost anyone in Hindi cinema right now: take a seemingly ordinary domestic setup and inject it with pressure until everything cracks.

## Why Madhuri in This Role Matters

At the trailer launch in Mumbai on May 22, Madhuri Dixit said something that caught the attention of Indian film observers: "I have always worked in films where women play a powerful role. But Rekha is powerful in a completely different way."

That's an understatement. For NRI audiences who grew up watching Madhuri as the ideal Indian woman — graceful, musical, untouchable — seeing her in a role where she's actively hiding a corpse is a genuine cultural shift. This isn't a late-career prestige pivot. This is Madhuri choosing to be funny, dark, and morally questionable. It's delightful.

She's joined by Triptii Dimri, who has quietly become one of the most bankable names in Indian cinema after *Animal*, *Laila Majnu*, and *Bulbbul*. Their pairing — veteran grace meets millennial chaos — is exactly the kind of combination Netflix India has been chasing.

## Suresh Triveni's Netflix Bet

Triveni is an interesting case study in Indian filmmaking. His films (*Tumhari Sulu*, *Jalsa*) don't open to ₹100 crore weekends. They don't need to. They find their audience slowly, through word of mouth and streaming, and they last. *Jalsa*, which also starred Vidya Balan, premiered directly on Amazon Prime Video in 2022 and became one of the most-discussed Hindi films of that year.

With *Maa Behen*, Triveni is going straight to Netflix — skipping theatres entirely — and betting that a global audience is ready for a Hindi dark comedy that doesn't pander.

For the diaspora, this matters. NRI audiences are increasingly the core audience for mid-budget Indian content. They subscribe to Netflix, JioHotstar, and Prime Video. They don't always make it to the Indian cinema down the road. But they will absolutely queue up a Madhuri-Triptii dark comedy on a Wednesday night.

## The Cast Goes Deeper Than You Think

Beyond the three leads, the ensemble includes Ravi Kishan — whose death kicks off the entire plot — in what promises to be a memorably weird extended cameo. The supporting cast rounds out with neighbourhood characters who are all, to varying degrees, suspects, accomplices, or gossips.

Triveni has always been good at ensemble dynamics. His colonies and offices feel lived-in. If *Maa Behen* nails that neighbourhood texture — and the trailer suggests it will — it could become the kind of film that generates its own vocabulary. Every Indian family has an Adarsh Colony. Every NRI knows a Gupta Ji.

## Mark Your Calendar

*Maa Behen* premieres on Netflix on June 4, 2026. It will be available globally from day one — no waiting for international rights, no staggered rollout.

For Madhuri fans who've been waiting for her to do something genuinely surprising: this is it. For Triptii Dimri fans: another reason she's the most interesting actress under 30 in India. For everyone else: a dead body, three women who can't agree on anything, and Ravi Kishan being Ravi Kishan.

What more could you want from a Wednesday night?"""
    })
else:
    print(f"⏭️  Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Main Vaapas Aaunga — Imtiaz Ali's Partition Love Story
# ══════════════════════════════════════════════════════════════
slug2 = "imtiaz-ali-main-vaapas-aaunga-naseeruddin-shah-diljit-dosanjh-partition-june-12-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Imtiaz Ali Made a Film About an Old Man's Last Wish to Return to Pakistan. Naseeruddin Shah and Diljit Dosanjh Star. It Releases Into a Four-Way Box Office War.",
        "subheadline": "Main Vaapas Aaunga — a Partition-era love story about memory, borders, and generational trauma — hits theatres on June 12 alongside three other films. Imtiaz Ali says he announced first. The diaspora doesn't care who announced first. They care that it's a Partition story with Diljit.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 78,
        "tags": ["Imtiaz Ali", "Main Vaapas Aaunga", "Naseeruddin Shah", "Diljit Dosanjh", "Partition", "Kangana Ranaut", "box office clash"],
        "diaspora_angle": "A Partition-era love story about the desire to return to a homeland left behind in 1947 is, quite literally, a diaspora film. For NRIs whose grandparents lived through Partition — and whose families still carry those stories — Main Vaapas Aaunga lands differently than it does in a Mumbai multiplex. The June 12 worldwide release ensures diaspora audiences can see it opening weekend.",
        "sources": [
            {"url": "https://www.zoomtventertainment.com/bollywood/four-films-clash-box-office-imtiaz-ali-reacts-bollywood-release-date-culture-article-154384261", "name": "Zoom TV"},
            {"url": "https://globalindiabroadcastnews.com/2026/05/imtiaz-ali-main-vaapas-aaunga-kangana-bharat-bhhagya-viddhaata-clash", "name": "Global India Broadcast News"},
            {"url": "https://thepopularstory.com/imtiaz-ali-reacts-main-vaapas-aaunga-clash-kangana-bharat-bhhagya-viddhaata", "name": "The Popular Story"},
            {"url": "https://aihustlehq.com/imtiaz-ali-reacts-clash-kangana-ranaut", "name": "AI Hustle HQ"}
        ],
        "image_search_query": "Main Vaapas Aaunga Imtiaz Ali Naseeruddin Shah Diljit Dosanjh 2026",
        "image_entities": ["Imtiaz Ali", "Naseeruddin Shah", "Diljit Dosanjh", "Main Vaapas Aaunga"],
        "image_must_show": "Main Vaapas Aaunga poster or still, or Imtiaz Ali at a press event",
        "word_count": 730,
        "body": """There is a certain kind of story that only the Indian diaspora fully understands. It's the story of a place you can't go back to — a home that exists now only in memory, across a border that didn't exist when your grandparents were young. That's the story Imtiaz Ali is trying to tell.

*Main Vaapas Aaunga* follows Keenu, an elderly man played by Naseeruddin Shah, whose dying wish is to return to Sargodha — the city in present-day Pakistan that he was forced to leave during the 1947 Partition. His grandson, played by Diljit Dosanjh, sets out to understand why this place still haunts his grandfather, and in the process uncovers a love story that transcended borders and outlasted time.

The film releases in theatres worldwide on June 12, 2026. It's walking straight into a four-way box office collision.

## The June 12 Pileup

Imtiaz Ali's film isn't alone on its release date. It's sharing the weekend with Kangana Ranaut's *Bharat Bhhagya Viddhaata* (a thriller about hospital staff during the 2008 Mumbai attacks), Manoj Bajpayee's *Governor: The Silent Saviour*, and Vikram Bhatt's *Haunted 3D: Echoes of the Past*.

Four Bollywood releases on the same day. In an interview with *The Free Press Journal*, Ali addressed the collision with characteristic calm: "We announced first. Usually in the industry there's a camaraderie — you say, 'my film is coming, so hold off.' That usually works. This time, it didn't."

He also offered the most Imtiaz Ali response possible: "There are only 52 weeks in a year. More than 52 films release annually. Clashes are inevitable."

## Why This Film Hits Different for NRIs

Partition films have been made before. *Gadar* was a blockbuster. *Pinjar* was critically acclaimed. *Veer-Zaara* was Shah Rukh Khan at his most romantic. But *Main Vaapas Aaunga* appears to be doing something different: telling the story from the perspective of someone who is dying and can't let go.

For the Indian diaspora — particularly Punjabi families in the US, Canada, and the UK — this isn't historical fiction. It's family history. Almost every Punjabi NRI family has a version of Keenu's story: a grandfather who remembered a house in Lahore, a grandmother who kept a photograph of a street in Rawalpindi, a great-uncle who could still describe the taste of water from a well that no longer exists.

Naseeruddin Shah playing this role is casting that borders on cruelty. He's one of the finest actors in Indian cinema history, and at 75, bringing him face to face with mortality and partition loss is going to be devastating.

And then there's Diljit Dosanjh. The biggest Punjabi artist on the planet. A man who sells out arenas in North America. Having him play the grandson — the generation that inherited the trauma without the memories — is a stroke of genius.

## Imtiaz Ali's Track Record With Longing

If there's one filmmaker in India who understands longing, it's Imtiaz Ali. *Jab We Met* was about the longing for connection. *Rockstar* was about the longing for artistic truth. *Tamasha* was about the longing to be yourself. *Highway* was about the longing for freedom.

*Main Vaapas Aaunga* is about the most fundamental longing of all: the desire to go home when home no longer exists. It's the longing that defines the diaspora experience at its most elemental.

The trailer — which has already received strong audience reactions — moves between the chaos of Partition and the quiet desperation of an old man running out of time. If Ali can sustain that tonal balance over a full film, this could be his most emotionally ambitious work since *Rockstar*.

## The Box Office Math

Realistically, *Main Vaapas Aaunga* is unlikely to be a ₹100 crore opener. Imtiaz Ali's recent films (*Chamkila*, *Love Aaj Kal 2*) have been mid-range performers at best. But this cast — Shah and Dosanjh together — has the potential to draw audiences that an Imtiaz Ali film alone might not.

The diaspora market could be decisive. If Punjabi audiences in Canada, the UK, and the US show up on opening weekend — and they will, for a Partition film starring Diljit — the international numbers could carry the film past the domestic competition.

June 12. Four films. One story about going home. The math is complicated. The emotion isn't."""
    })
else:
    print(f"⏭️  Skipping duplicate: {slug2}")

# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
inserted = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['headline'][:80]}...")
        inserted += 1
    except Exception as e:
        print(f"❌ Failed to insert {art['slug']}: {e}")

print(f"\n📝 Inserted {inserted}/{len(articles)} articles")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — drop old entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n📉 Running score decay for entertainment articles...")
cutoff_3d = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

# Articles older than 7 days: drop score significantly
code = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.40",
    {"score_total": 35}
)
print(f"  7d+ decay: HTTP {code}")

# Articles older than 3 days: moderate decay
code = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.55",
    {"score_total": 50}
)
print(f"  3-7d decay: HTTP {code}")

print("\n✅ Entertainment writer batch complete!")
