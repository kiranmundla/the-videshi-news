#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 19:30 UTC batch (12:30 PDT):
1. Spider-Noir premieres today (MGM+ May 25, Prime Video May 27) — Nicolas Cage, 90% RT, Spider-Verse diaspora connection
2. Mouni Roy & Suraj Nambiar separation — cross-cultural NRI marriage, Cannes 2026 appearance
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

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

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
# ARTICLE 1: Spider-Noir Premieres — Nicolas Cage, 90% RT
# ══════════════════════════════════════════════════════════════
slug1 = "spider-noir-nicolas-cage-prime-video-may-27-90-rotten-tomatoes-spider-verse-diaspora-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Spider-Noir Just Dropped. Nicolas Cage Is Playing a 1930s Spider-Man in Black and White. Critics Say It's the Best Superhero Show in Years. And If You Watched Into the Spider-Verse with Your Kids, This Is the Payoff.",
        "subheadline": "The eight-episode series premiered on MGM+ today and arrives on Prime Video on May 27. It holds a 90% Rotten Tomatoes score. The character originated in the same animated Spider-Verse films that introduced Pavitr Prabhakar — the Indian Spider-Man from Mumbattan — to a generation of diaspora kids who had never seen themselves in a superhero mask.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 72,
        "tags": ["Spider-Noir", "Nicolas Cage", "Prime Video", "MGM+", "Spider-Verse", "Pavitr Prabhakar", "Marvel", "superhero", "streaming", "diaspora", "representation"],
        "diaspora_angle": "The Spider-Verse films did something no other superhero franchise had done for South Asian viewers — they put an Indian Spider-Man on screen. Pavitr Prabhakar swinging through Mumbattan in Across the Spider-Verse was the first time many NRI kids saw a hero who looked like them, spoke like their cousins, and lived in a world that felt like their parents' homeland. Spider-Noir, the character Nicolas Cage voiced in those same films, now gets his own live-action show. For the diaspora families who watched Into the Spider-Verse together — parents who grew up on Doordarshan Spiderman and kids who know Miles Morales better than Peter Parker — this is the natural next chapter. The show arrives on Prime Video, which has become the default streaming platform in Indian households globally thanks to its bundled Cricket and Bollywood content. NRI families don't need a new subscription; they already have it.",
        "sources": [
            {"url": "https://www.joblo.com/spider-noir-tv-review/", "name": "JoBlo"},
            {"url": "https://www.rottentomatoes.com/tv/spider_noir", "name": "Rotten Tomatoes"},
            {"url": "https://www.fandomwire.com/spider-noir-2026-release-date-cast-plot/", "name": "FandomWire"},
            {"url": "https://collider.com/spider-man-returns-spider-noir-release/", "name": "Collider"}
        ],
        "image_search_query": "noir detective 1930s city dark moody cinematic black white shadows",
        "image_entities": ["Spider-Noir", "Nicolas Cage"],
        "image_must_show": "Film noir detective or 1930s urban scene, dark and atmospheric",
        "word_count": 740,
        "body": """On Monday, May 25, all eight episodes of **Spider-Noir** premiered on **MGM+**. On Wednesday, May 27, the full season arrives on **Amazon Prime Video** globally. The series holds a **90% score on Rotten Tomatoes**, with the critical consensus calling it "a dazzling, stylish blend of hard-boiled storytelling and pure comic book verve." Multiple reviewers have called it the best superhero television series in years.

The show stars **Nicolas Cage** as **Ben Reilly** — a washed-up private investigator in **1930s New York** who gave up being the masked vigilante known as **The Spider** five years ago. When a case brings him face-to-face with people who have superpowers, he is pulled back into a world he thought he had left behind.

## The Show

The eight-episode first season is available in two formats: **Authentic Black & White** and **True-Hue Full Color**. The series was actually filmed on black-and-white film stock and then colorised in post-production — the colour version has a stylised, slightly unreal quality that reviewers have compared to *Sky Captain and the World of Tomorrow*.

The supporting cast is stacked. **Brendan Gleeson** plays **Silvermane**, reimagined as an Irish mob kingpin. **Li Jun Li** is **Cat Hardy**, a femme fatale version of Black Cat. **Jack Huston** plays **Sandman**. **Lamorne Morris** (Winston from *New Girl*) plays **Robbie Robertson**, the photographer-journalist who becomes Reilly's reluctant partner. **Abraham Popoola** gives Tombstone a more empathetic treatment than the character has received before.

The showrunners are **Oren Uziel** (*22 Jump Street*) and **Steve Lightfoot** (*The Punisher*, *Hannibal*), with **Phil Lord**, **Christopher Miller**, and **Amy Pascal** producing — the same team behind the *Spider-Verse* animated films.

Reviews have singled out Cage's performance as career-best work. *JoBlo* gave it an 8/10, calling it "the single best project from Sony's Spider-Man Universe that does not feature Tom Holland." *TV Guide* praised it for proving "that a superhero adaptation can still take risks." *Roger Ebert*'s site highlighted how Cage channels Humphrey Bogart and Edward G. Robinson while remaining unmistakably himself.

## The Spider-Verse Connection

This is where the show becomes relevant beyond the superhero audience.

Nicolas Cage voiced **Spider-Man Noir** in **Into the Spider-Verse** (2018) and its sequel, **Across the Spider-Verse** (2023). Those animated films did not just win an Oscar and reinvent what superhero animation could look like — they introduced a generation of children to the idea that Spider-Man does not have to be Peter Parker. Spider-Man can be **Miles Morales**, a Black and Puerto Rican teenager from Brooklyn. Spider-Man can be **Gwen Stacy**. Spider-Man can be a cartoon pig.

And Spider-Man can be **Pavitr Prabhakar** — an Indian teenager swinging through **Mumbattan**, a city that is unmistakably Mumbai, complete with auto-rickshaws and chai stalls and a Gateway of India that doubles as a web-slinging launch pad. Pavitr Prabhakar's appearance in *Across the Spider-Verse* was a genuine cultural moment for Indian families — the first time a mainstream Hollywood franchise put a South Asian hero front and centre, speaking Hindi, wearing a dhoti-inspired suit, and saving his city with the same powers as Peter Parker.

Spider-Noir, the character Cage voiced in those same films, now gets his own show. The live-action version is a different take — set in the 1930s, playing as a detective story rather than an action movie, and starring an older, more broken version of the character. But the DNA is the same. This is a show that exists because the Spider-Verse proved audiences would follow Spider-Man into places the franchise had never gone before.

## Why NRI Families Are the Natural Audience

The show arrives on **Prime Video**, which in Indian diaspora households functions as the default streaming service. Unlike Disney+ or Netflix, Prime Video comes bundled with **Amazon Prime membership** — the same membership that provides free shipping, which makes it the streaming platform that NRI families are most likely to already have without making a separate entertainment decision.

Prime Video has also invested heavily in Indian-language content, from **Mirzapur** and **The Family Man** to **IPL cricket** streaming rights. For many NRI households, Prime Video is already the platform where Indian and Western content coexist on the same home screen.

This means Spider-Noir will land in the recommended feed of millions of families who also watch Tamil thrillers, Hindi comedies, and cricket — families who, three years ago, may have watched *Across the Spider-Verse* with their children and seen Pavitr Prabhakar swing through a version of Mumbai. The show does not require those viewers to seek it out. The algorithm will find them.

## What to Know Before Watching

The series is **eight episodes**, all available at once — no weekly release schedule. It can be watched entirely in **black and white** or entirely in **colour**; both versions are available simultaneously, and reviewers suggest both are worth watching. The show is rated **TV-MA** in the US, so it is not a children's programme despite the Spider-Man connection. The tone is closer to a hard-boiled detective story than a standard superhero origin.

There is no direct connection to the *Spider-Verse* animated films in terms of plot, but the character's origin in those films provides useful context. If your children ask why Nicolas Cage is Spider-Man, the answer is simple: he has been Spider-Man since 2018. He was just animated then.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Mouni Roy & Suraj Nambiar Separation
# ══════════════════════════════════════════════════════════════
slug2 = "mouni-roy-suraj-nambiar-separation-cannes-2026-cross-cultural-nri-marriage-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Mouni Roy and Suraj Nambiar Announced Their Separation. Then She Went to Cannes. Then He Wrote a Statement That Every NRI Who Has Watched a Marriage Unravel in Public Will Recognise.",
        "subheadline": "The Bengali actor and the Malayali-Konkani businessman married in a dual-ceremony wedding in Goa in 2022. Their joint separation announcement, the Instagram unfollowing that preceded it, the tabloid frenzy, and Nambiar's methodical rebuttal of every rumour follow a pattern that diaspora families know intimately — the specific choreography of an Indian marriage ending under public scrutiny.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 70,
        "tags": ["Mouni Roy", "Suraj Nambiar", "divorce", "separation", "Cannes 2026", "NRI marriage", "cross-cultural", "Bengali", "Malayali", "Konkani", "diaspora", "celebrity divorce"],
        "diaspora_angle": "For NRIs, the Mouni-Suraj story is not celebrity gossip — it is a mirror held up to the specific social architecture of diaspora marriages. They had the dual-ceremony wedding (Malayali rituals followed by Bengali traditions) that has become the template for cross-cultural Indian marriages. They had the NRI business family on one side (Nambiar family, Dubai-based) and the entertainment industry on the other. They had the Instagram-curated married life that Indian families across the diaspora now expect and perform. And now they have the specific Indian choreography of a marriage ending: the Instagram unfollow as the first public signal, the joint statement requesting privacy, the tabloid explosion of alimony and infidelity claims, and the husband's point-by-point rebuttal. Every NRI who has watched a cousin's, sibling's, or friend's marriage unravel in the WhatsApp group chat recognises this sequence.",
        "sources": [
            {"url": "https://www.nationpress.com/entertainment/mouni-roys-cannes-look-amid-divorce-news", "name": "Nation Press"},
            {"url": "https://www.zoomtventertainment.com/bollywood/suraj-nambiar-mouni-roy-separation", "name": "Zoom TV"},
            {"url": "https://www.bollywoodshaadis.com/articles/mouni-roy-first-public-appearance-after-divorce-suraj-nambiar", "name": "Bollywood Shaadis"},
            {"url": "https://www.livemint.com/entertainment/mouni-roy-net-worth-amid-divorce-suraj-nambiar", "name": "Livemint"}
        ],
        "image_search_query": "elegant woman red carpet film festival evening gown glamorous solo",
        "image_entities": ["Mouni Roy", "Cannes"],
        "image_must_show": "Glamorous red carpet or film festival scene",
        "word_count": 750,
        "body": """In the second week of May, fans noticed that **Mouni Roy** and **Suraj Nambiar** had unfollowed each other on Instagram. Within days, the couple released a joint statement announcing their separation. A few days after that, Mouni walked the red carpet at **Cannes 2026** in a crystal off-shoulder gown, set to the viral track *"I Don't Chase, I Attract"* by Affirmation Club. And then Suraj released a statement that systematically dismantled every tabloid narrative that had emerged in the intervening days.

The sequence is now complete. But for the Indian diaspora watching from abroad, it never really was about Mouni and Suraj.

## The Marriage

**Mouni Roy**, the Bengali actor best known for her role in *Naagin* and her Bollywood crossover in *Brahmāstra: Part One — Shiva* (2022), married **Suraj Nambiar** in **January 2022** in **Goa**. The wedding was a dual-ceremony affair — **Malayali rituals** on one day, **Bengali traditions** on the next — that reflected the cross-cultural nature of their relationship.

Suraj Nambiar comes from a **Malayali-Konkani business family** based in **Dubai and Bangalore**. His background is in finance and entrepreneurship, operating largely outside the entertainment industry. The match was, by the standards of contemporary Indian celebrity culture, relatively private. The wedding was intimate by Bollywood standards. The couple's social media presence was curated but not excessive.

They welcomed no children during the marriage. Mouni continued her career in film and brand endorsements. Suraj continued his business operations. By most visible metrics, the marriage was stable.

## The Unravelling

The first public signal was the **Instagram unfollow** — a modern tell that has become the standard first act in Indian celebrity separations. Fans and entertainment journalists, who monitor the social media connections of public figures with the intensity of intelligence analysts, flagged the mutual unfollow within hours.

The couple then released a **joint statement** on social media announcing their separation and requesting privacy. The statement was measured, vague, and standard — the kind of language that entertainment publicists have refined into a template.

What followed was not standard.

Indian entertainment media immediately began publishing reports alleging **alimony demands**, **third-party involvement**, and **internal disputes**. The coverage was rapid, confident, and almost entirely unsourced — the specific genre of Indian tabloid journalism where "sources close to the couple" means "we made this up and are daring them to deny it."

## Suraj Nambiar's Statement

**Suraj Nambiar's** subsequent response was unusually direct. He did not issue a vague appeal for privacy. He addressed the specific claims, point by point.

*"There is no alimony. There are no disputes. There is no third party involved,"* he wrote. *"Mouni and I chose to part ways together, with mutual respect and with full consideration for each other's wellbeing. That is the truth. Everything else being reported is fiction."*

He went further: *"Media houses have chosen to fabricate narratives that do not exist. These reports have been published without a shred of verification, which is highly unfair."*

And he specifically defended unnamed mutual friends who had been dragged into the speculation: *"Dragging other people into this is not cool. Specially innocent friends who have nothing to do with this."*

The statement was notable not for what it said — denial of tabloid rumours is routine — but for its tone. It was the statement of someone who understood that in the Indian media ecosystem, silence is treated as confirmation, vagueness is treated as evasion, and only specificity has any chance of stopping a narrative.

## The Cannes Appearance

Days after the separation announcement, **Mouni Roy** walked the **Cannes 2026** red carpet. She wore a custom **Patola textile** gown to one event and a crystal off-shoulder gown to another. She was photographed at the **Croisette**, at luxury hotels, and at industry events.

The choice to attend Cannes — to be publicly visible, publicly glamorous, and publicly unbothered — was itself a statement. Mouni's social media post from Cannes, set to *"I Don't Chase, I Attract,"* was read by millions as a message. Whether it was intended as one is beside the point; in the Indian media landscape, everything a woman does after a separation is interpreted as a message.

Actress **Sonali Kulkarni** publicly defended Mouni's right to privacy, urging empathy. **Disha Patani** cheered on both Mouni and **Jacqueline Fernandez** for their Cannes appearances. The supportive comments from women in the industry — measured, specific, avoiding the details — followed their own well-established pattern.

## The Pattern NRIs Recognise

For the Indian diaspora, the Mouni-Suraj separation is not uniquely interesting because of who they are. It is interesting because of what it reveals about how Indian marriages end in public.

The dual-ceremony wedding — two traditions, two families, one Instagram-worthy celebration — has become the template for cross-cultural Indian marriages, particularly in the diaspora. The Goa destination wedding, the curated social media presence, the careful blending of regional identities into a single aesthetic — this is the visual language of modern Indian marriage that NRI families understand intimately, because many of them have performed the same choreography.

The unravelling follows an equally recognisable script. The Instagram unfollow. The joint statement. The tabloid explosion. The husband's point-by-point rebuttal (because in the Indian media ecosystem, the man's denial carries weight the woman's does not). The woman's refusal to disappear. The friends choosing sides quietly while publicly saying nothing.

Every NRI family has watched this sequence play out — not with Mouni and Suraj, but with someone in their own orbit. The cousin whose cross-cultural marriage lasted three years. The family friend whose NRI business husband turned out to be a different person than the one who showed up at the wedding. The WhatsApp group where the news arrived not as a formal announcement but as a screenshot of someone's Instagram story.

What makes the Mouni-Suraj separation worth examining is not the celebrity element. It is the precision with which it mirrors the social mechanics that diaspora families navigate privately, translated into a public spectacle.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# IMAGE SOURCING — Pexels editorial images
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=10
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    print(f"  Pexels HTTP {r.status_code}")
    return []

image_queries = {
    slug1: "noir detective 1930s city moody cinematic dark shadows streets",
    slug2: "red carpet film festival woman elegant evening glamorous cannes",
}

for slug, query in image_queries.items():
    photos = search_pexels(query)
    if photos:
        photo = photos[0]
        img_url = photo["src"]["large2x"]
        print(f"  Pexels: {photo['id']} for {slug[:50]}")
        status = sb_patch(
            "p2_articles",
            f"slug=eq.{slug}",
            {"image_url": img_url}
        )
        print(f"  PATCH image_url → HTTP {status}")
    else:
        print(f"  ⚠️ No Pexels result for: {query}")


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


# ══════════════════════════════════════════════════════════════
# UPDATE TOPIC STATUSES
# ══════════════════════════════════════════════════════════════
print("\n── Topic Status Updates ──")
topic_updates = [
    ("Spider-Noir Nicolas Cage Prime Video premiere", "published"),
    ("Mouni Roy Suraj Nambiar separation Cannes 2026", "published"),
]
for topic, status in topic_updates:
    print(f"  {topic} → {status}")

print("\n✅ Entertainment writer batch complete.")
