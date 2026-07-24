#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 03:30 UTC batch:
1. David Dhawan retires after 46 films — Hai Jawani confirmed as final directorial
2. Cannes 2026 Palme d'Or winner Fjord — immigrant parents vs the state, NRI resonance
+ Score decay for older entertainment articles
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

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: David Dhawan retires — 46 films, final directorial
# ══════════════════════════════════════════════════════════════
slug1 = "david-dhawan-retires-46-films-hai-jawani-final-directorial-karan-johar-varun-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "David Dhawan Just Told Karan Johar That 'Hai Jawani Toh Ishq Hona Hai' Is His Last Film. After 46 Movies and Three Decades of Defining What Bollywood Comedy Means, the Man Who Made Coolie No. 1 Is Done.",
        "subheadline": "At a PVR celebration following the trailer launch of his 46th film, the 74-year-old director confirmed to Karan Johar that he is retiring from filmmaking. KJo's Instagram tribute — 'Here's a filmmaker who is responsible for creating an entire genre of films' — hit different because it's true. David Dhawan didn't just make comedies. He made the comedies that NRI families rented on VHS from the Indian grocery store every Friday night. His last film stars his son Varun, releases June 5, and carries the weight of a legacy that defined two generations of laughter.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "trending",
        "status": "published",
        "published_at": now_iso,
        "score_total": 80,
        "tags": ["David Dhawan", "retirement", "Hai Jawani Toh Ishq Hona Hai", "Varun Dhawan", "Karan Johar", "Coolie No 1", "Govinda", "Bollywood comedy", "90s Bollywood", "Hero No 1", "Judwaa"],
        "diaspora_angle": "For NRIs who grew up in the 90s, David Dhawan IS Bollywood comedy. Not Hera Pheri or 3 Idiots — those came later. David Dhawan comedies were the ones your parents picked up from the VHS rack at Patel Brothers or Raja Foods. Coolie No. 1 on a Saturday night. Hero No. 1 at a family gathering. Judwaa at a friend's birthday sleepover. Bade Miyan Chote Miyan when the uncles were visiting. These films weren't sophisticated. They weren't trying to be. They were pure, uncut, slapstick dopamine — and they were the connective tissue of diaspora entertainment before Netflix, before YouTube, before any of it. His retirement isn't just industry news. It's the closing of a chapter that every NRI household over 30 has lived through. And the fact that his last film is with his son, Varun — the kid who grew up watching his dad direct Govinda — makes it land even harder.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/features/karan-johar-pens-emotional-note-for-david-dhawan-after-the-latter-confirmed-to-him-that-hai-jawani-toh-ishq-hona-hai-is-his-final-directorial/", "name": "Bollywood Hungama"},
            {"url": "https://www.tezzbuzz.com/karan-johar-reacts-to-david-dhawan-retirement/", "name": "TezzBuzz"},
            {"url": "https://www.dailyprabhat.com/david-dhawan-retire-hai-jawani/", "name": "Daily Prabhat"},
            {"url": "https://www.bollywoodhungama.com/news/features/david-dhawan-admits-he-made-chashme-baddoor-in-anger/", "name": "Bollywood Hungama"}
        ],
        "image_search_query": "David Dhawan director Bollywood retirement Hai Jawani Varun Dhawan 2026",
        "image_entities": ["David Dhawan", "Varun Dhawan", "Karan Johar"],
        "image_must_show": "David Dhawan at event or with Varun Dhawan",
        "word_count": 820,
        "body": """At a PVR-hosted celebration following the trailer launch of Hai Jawani Toh Ishq Hona Hai on May 23, David Dhawan told the room — and specifically Karan Johar — that this would be his last film.

He is 74. He has directed 46 films. His first, Taaqatwar, released in 1989. His last will release on June 5, 2026. Between those two dates lies an entire genre.

## Karan Johar's Tribute

Karan Johar, who launched David Dhawan's son Varun in Student of the Year in 2012 and has since collaborated with him on five films, posted an Instagram Story that read like a eulogy for an era:

"Yesterday when I went to Davidji's celebration and he told me this was going to be his last film... I had a bittersweet reaction in my heart. Here's a filmmaker who is responsible for creating an entire genre of films. A DAVID DHAWAN film spells entertainment!"

He continued: "He is LOVED and RESPECTED and CELEBRATED by our fraternity. There's NO opposing that. Here's to your summer blockbuster with your son. DAVID DHAWAN... NO 1 man always."

The note was personal, not performative. Johar and the Dhawans have a relationship that predates any professional arrangement — and KJo's acknowledgment that David Dhawan "created an entire genre" is not hyperbole. It's the documented record.

## The Filmography That Defined Friday Nights

Between 1993 and 2007, David Dhawan directed 17 films with Govinda. Seventeen. That's not a collaboration — it's a marriage. Aankhen, Raja Babu, Coolie No. 1, Hero No. 1, Deewana Mastana, Bade Miyan Chote Miyan, Haseena Maan Jaayegi, Jodi No. 1 — the titles blur together in the memory because they occupied the same cultural space: pure, uncut, slapstick entertainment designed for maximum family consumption.

He also directed Judwaa (1997) and Mujhse Shaadi Karogi (2004) with Salman Khan, No Entry (2005) which remains the gold standard for ensemble Bollywood farce, and Partner (2007) with Govinda and Salman together.

His films weren't art. He'd be the first to tell you. At the Bollywood Hungama celebration, he recalled making Chashme Baddoor (2013) "out of anger" — because stars had started refusing to work with him. "I was not getting stars. They didn't reject the film but they were hesitating." So he cast younger actors and made it work.

That's the David Dhawan ethos: keep making comedies, no matter who says yes. The formula never changed. Double roles, mistaken identities, loud aunties, songs shot in Switzerland, and a climax where everyone ends up in the same room screaming. It worked because he committed to it completely.

## The Father-Son Chapter

Hai Jawani Toh Ishq Hona Hai is David Dhawan's fourth film with Varun. The previous three — Main Tera Hero (2014), Judwaa 2 (2017), and Coolie No 1 (2020) — were all remakes or spiritual successors of his earlier hits. This is the first original collaboration.

At the trailer launch, David broke down on stage. "Everybody should have a son like Varun," he said. Varun, for his part, has been publicly defending his father against the ongoing legal dispute with producer Vashu Bhagnani, who held a press conference the same week accusing David of being overpaid on Coolie No 1.

"Baap ko bolne se pehle, samaj lena ki beta khada hai," Varun told reporters — roughly translated: "Before you say anything about my father, understand that his son is standing right here."

The Supreme Court dismissed Bhagnani's case on the same day as his press conference. The timing was poetic.

## What He's Leaving Behind

David Dhawan's films collectively grossed over ₹2,000 crore at the box office across three decades. His partnership with Govinda is the most prolific actor-director collaboration in Hindi cinema history. His influence on a generation of comedy directors — from Rohit Shetty to Anees Bazmee — is widely acknowledged.

But the numbers don't capture what he actually did. He gave Indian families a shared language of humour. "Teja main hoon, mark idhar hai" from Andaz Apna Apna isn't his — but the ecosystem that made that line possible is. He industrialised Bollywood comedy. He proved that laughter was bankable, reliable, and infinitely renewable.

## The Diaspora Goodbye

For NRIs, this retirement lands differently than it would for someone in Mumbai.

David Dhawan comedies were the bridge. They were the films your parents could watch with you without anyone feeling awkward. They were the films you could quote at family gatherings and everyone would laugh — the Indian cousin in Delhi and the American cousin in Edison, New Jersey, equally.

They were not great cinema. They were better than that. They were shared experience.

His last film releases on June 5. It stars his son, features Anu Malik and Sameer's music, and has Jimmy Shergill, Chunky Panday, and the DNA of every David Dhawan film that came before it.

If you grew up on those VHS tapes, this one's worth seeing in a theatre. Not because it'll be good. Because it'll be the last one.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Cannes 2026 Palme d'Or — Fjord, immigrant parents
# ══════════════════════════════════════════════════════════════
slug2 = "cannes-2026-palme-dor-fjord-sebastian-stan-immigrant-parents-nri-child-services-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Film That Just Won Cinema's Highest Prize Is About Immigrant Parents Whose Children Were Taken by the State. Every NRI Parent Who Has Ever Worried About a Cultural Misunderstanding Knows Exactly Why It Won.",
        "subheadline": "Cristian Mungiu's Fjord — starring Marvel's Sebastian Stan and Renate Reinsve as Romanian evangelical parents in Norway — won the Palme d'Or at Cannes 2026. The film's premise: an immigrant couple's children are removed by child protective services after they are caught disciplining them. For the Indian diaspora, this isn't a European art film. It's the quiet fear that lives in the back of every NRI household where grandma still believes a light slap builds character and the neighbours live in a country that disagrees.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "trending",
        "status": "published",
        "published_at": now_iso,
        "score_total": 77,
        "tags": ["Cannes 2026", "Palme d'Or", "Fjord", "Cristian Mungiu", "Sebastian Stan", "Renate Reinsve", "Tilda Swinton", "immigrant parents", "child protective services", "NRI parenting", "cultural clash", "Park Chan-wook", "NEON", "film festival"],
        "diaspora_angle": "This is the most diaspora-relevant Palme d'Or winner in memory — and it's not even about Indians. Fjord is about Romanian immigrants in Norway whose children are taken by the state for spanking. For NRI families in America, Canada, the UK, and Australia, this premise isn't abstract. It's the anxiety that pulses beneath every cross-cultural parenting moment: the grandparent who disciplines differently, the neighbour who might call CPS, the school teacher who asks pointed questions about a bruise from cricket practice. Indian parenting norms — particularly around physical discipline, academic pressure, and family hierarchy — exist in genuine tension with Western child welfare frameworks. Most NRI families navigate this silently. The fact that cinema's highest prize just went to a film that dramatises this exact collision is validation of a fear that the diaspora has carried for decades without a cultural text to point to.",
        "sources": [
            {"url": "https://aihustlehq.com/cannes-film-festival-2026-full-list-of-winners-cristian-mungiu-wins-palme-dor-for-fjord-minotaur-gets-grand-prix/", "name": "AiHustleHQ"},
            {"url": "https://www.avclub.com/sebastian-stans-fjord-cannes-2026-winners/", "name": "AV Club"},
            {"url": "https://theplaylist.net/neon-cristian-mungiu-fjord-wins-palme-dor-cannes-2026/", "name": "The Playlist"},
            {"url": "https://www.thewrap.com/cannes-2026-winners-fjord-palme-dor/", "name": "The Wrap"},
            {"url": "https://www.lemonde.fr/en/culture/article/2026/05/24/cannes-film-festival-cristian-mungiu-wins-palme-d-or-for-fjord/", "name": "Le Monde"}
        ],
        "image_search_query": "Cannes 2026 Palme d'Or Fjord Cristian Mungiu Sebastian Stan Renate Reinsve Tilda Swinton ceremony",
        "image_entities": ["Cannes Film Festival", "Sebastian Stan", "Cristian Mungiu", "Renate Reinsve", "Tilda Swinton"],
        "image_must_show": "Palme d'Or ceremony or Fjord cast at Cannes",
        "word_count": 800,
        "body": """On Saturday evening in Cannes, Tilda Swinton announced the winner of the Palme d'Or — cinema's most prestigious prize — to a room that already knew. The whispers had been circulating since midweek. Cristian Mungiu's Fjord had landed.

The Romanian director, who first won the Palme in 2007 for 4 Months, 3 Weeks and 2 Days, became only the tenth filmmaker in history to win it twice. The jury, led by South Korean filmmaker Park Chan-wook, chose a film about immigrant parents in Norway whose children are taken away by the state.

For the Indian diaspora watching from afar, the premise hit with a precision that no European film critic would think to articulate.

## What Fjord Is About

Sebastian Stan — best known as Bucky Barnes in the Marvel Cinematic Universe — and Renate Reinsve star as a Romanian evangelical couple who relocate to a small Norwegian village with their children. When local child protective services discover that the parents physically discipline their children (specifically, spanking), the children are removed from the home.

What follows is not a courtroom thriller. It's something worse: a slow, bureaucratic dismantling of a family by a system that believes it is acting in the children's best interest. The parents believe they are raising their children according to their values. The state believes those values constitute abuse. Neither side is entirely wrong. The film refuses to resolve this tension.

Mungiu described it as "a message about tolerance, inclusion and empathy" — but added, with the weight of someone who has spent his career examining institutional power, that "we need to put them into practice more often."

## Why NRI Families Understand This Film Without Seeing It

In the United States, approximately 3.5 million calls are made to child protective services every year. The vast majority involve genuine welfare concerns. But for immigrant communities — Indian families included — the system operates in a cultural grey zone that can feel adversarial.

Indian parenting, particularly among first-generation immigrants and visiting grandparents, operates on principles that don't always align with Western child welfare norms. A light slap from a grandmother. A raised voice about homework grades. A child told to stand in the corner for hours. These are, in many Indian households, unremarkable. In a suburban American context, they can trigger a knock on the door.

Most NRI families never face this directly. But almost all of them have thought about it. The stories circulate in WhatsApp groups: someone's neighbour called CPS because a child was heard crying. A teacher asked a child if they were hit at home. A grandparent was questioned at a park.

Fjord takes this anxiety — one that immigrant families across the world share — and places it at the centre of cinema's highest stage. The fact that it won is not just a recognition of Mungiu's filmmaking. It is, inadvertently, a recognition that the immigrant parenting dilemma is one of the defining tensions of the globalised world.

## The Full Winners List

The 79th Cannes Film Festival awarded its prizes as follows:

**Palme d'Or**: Fjord (Cristian Mungiu) — starring Sebastian Stan, Renate Reinsve, Tilda Swinton

**Grand Prix**: Minotaur (Andrey Zvyagintsev) — a political thriller about a Russian businessman caught up in the Ukraine invasion. Zvyagintsev, who nearly died during COVID after spending a month in a coma, addressed Putin from the stage: "Put an end to the carnage. The whole world is waiting."

**Jury Prize**: The Dreamed Adventure (Valeska Grisebach)

**Best Director** (tie): Javier Calvo & Javier Ambrossi for The Black Ball; Paweł Pawlikowski for Fatherland

**Best Actress** (tie): Virginie Efira and Tao Okamoto for All of a Sudden

**Best Actor** (tie): Emmanuel Macchia and Valentin Campagne for Coward

**Best Screenplay**: Emmanuel Marre for A Man of His Time

**Caméra d'Or** (best first film): Ben'Imana (Marie Clémentine Dusabejambo) — the first Rwandan film ever officially selected at Cannes

NEON, the US distributor behind Fjord, has now won seven consecutive Palme d'Or prizes — a streak that began with Parasite in 2019 and continued through Titane, Triangle of Sadness, Anatomy of a Fall, Anora, The Brutalist, and now Fjord.

## India's Absence, Again

India, the world's largest film industry by volume, had no films in competition at this year's festival. Payal Kapadia, whose All We Imagine as Light won the Grand Prix at Cannes 2024, was present but not competing. Aishwarya Rai Bachchan walked the red carpet for L'Oréal. That was the extent of India's official presence.

The diaspora irony is sharp: the film that won Cannes is about immigrant parents navigating a foreign state. India's film industry, which serves the world's largest immigrant diaspora, wasn't in the room when it happened.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

# 7+ days old → score 35
cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

# 3-7 days old → score 50
cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")

print("\n✅ Entertainment writer batch complete.")
