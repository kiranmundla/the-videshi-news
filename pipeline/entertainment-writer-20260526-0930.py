#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 09:30 UTC batch (02:30 PDT):
1. Ramakant Dayama, actor from Chak De India and Scam 1992, dies at 69.
   Father of Yashaswini Dayama. CINTAA mourns him.
2. Hema Malini in tears accepting Dharmendra's posthumous Padma Vibhushan
   at Rashtrapati Bhavan. Ahana Deol breaks down. The ceremony moment that
   said everything about what Dharmendra meant to a generation.
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests, urllib.parse
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

# ── Image sourcing: Wikipedia first (per IMAGE-SOURCING-RULES.md) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels fallback ──
PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": q, "per_page": 5, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
        print(f"  Pexels HTTP {r.status_code} for '{q}'")
    return None

# ── Supabase image upload ──
def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase article-images bucket. Returns public URL."""
    try:
        img_data = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"}).content
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url  # Fall back to original URL

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ramakant Dayama Dies at 69
# ══════════════════════════════════════════════════════════════
slug1 = "ramakant-dayama-dies-69-chak-de-india-scam-1992-actor-cintaa-tribute-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Ramakant Dayama, the Actor You Knew From Chak De! India and Scam 1992 but Could Never Name, Has Died at 69. He Was the Kind of Actor Who Made Every Scene He Was In Feel More Real Than the Scene Deserved.",
        "subheadline": "The veteran stage, film, and television actor — and father of actress Yashaswini Dayama — passed away on May 26, 2026, after months of illness. CINTAA remembered him as 'a respected former Executive Committee member and a cherished part of our fraternity.' His friend and colleague Shubhangi Latkar called him 'one of the strongest and most courageous people I have known.' They had planned a Hindi play together. He told her: 'Let me get well soon.' He did not get well soon.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 78,
        "tags": ["Ramakant Dayama", "Chak De India", "Scam 1992", "Dhanak", "character actor", "CINTAA", "Yashaswini Dayama", "Shubhangi Latkar", "Indian theatre", "Bollywood", "veteran actor", "obituary", "diaspora"],
        "diaspora_angle": "The Indian diaspora does not know Ramakant Dayama's name. They know his face. They know the feeling of seeing him in a scene and thinking: this scene is going to be good. He was in Chak De! India — the film that became the emotional center of every NRI's relationship with Indian sports, the film you watched at a community center in Edison or a theater in Southall and felt, for two hours, that you were home. He was in Scam 1992 — the show that became the streaming gateway drug for an entire generation of NRIs who had been too busy with American TV to notice that Indian content had gotten extraordinary. He was in Dhanak — a Rajasthani film about two children that played at international film festivals and made diaspora audiences cry in ways they couldn't explain. Ramakant Dayama was never the reason you watched these projects. He was the reason they worked.",
        "sources": [
            {"url": "https://www.latestly.com/entertainment/bollywood/chak-de-india-actor-ramakant-daayama-dies-at-69-shubhangi-latkar-remembers-him-as-a-beautiful-soul-7446985.html", "name": "LatestLY"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/", "name": "Bollywood Hungama"},
            {"url": "https://www.filmibeat.com/bollywood/news/ramakant-dayama-dies-69/", "name": "FilmiBeat"}
        ],
        "image_search_query": "Ramakant Dayama",
        "image_entities": ["Ramakant Dayama"],
        "image_must_show": "Ramakant Dayama, Indian actor",
        "word_count": 750,
        "body": """On May 26, 2026, actor **Ramakant Dayama** died. He was 69 years old. He had been unwell for months. His death was confirmed by **CINTAA** (Cine and TV Artistes' Association), of which he was a former Executive Committee member, and mourned publicly by his friend and colleague **Shubhangi Latkar**, who shared a video of him singing, dancing, and laughing at a gathering — the kind of footage that only becomes sacred after the person in it is gone.

You have seen Ramakant Dayama. You may not know that you have seen him. That is the precise nature of his accomplishment.

## The Face You Recognized

He was in **Chak De! India** (2007) — not as Shah Rukh Khan, not as one of the hockey players, but as one of the faces in the institutional machinery that the film's protagonist navigates. The kind of role that grounds a sports drama in bureaucratic reality.

He was in **Scam 1992: The Harshad Mehta Story** (2020) — the Sony LIV series that became the most culturally significant Indian show of its era, the show that NRIs in North America and the UK binged during lockdown and quoted in WhatsApp groups for months afterward. Dayama was part of the ensemble that gave the show its texture.

He was in **Dhanak** (2015) — Nagesh Kukunoor's National Award-winning film about two Rajasthani children on a road trip to meet Shah Rukh Khan, a film that traveled to international festivals and became a quiet touchstone for diaspora audiences who wanted Indian cinema that was neither Bollywood spectacle nor art-house penance.

He was in television. He was in theatre. He was in the kind of work that actors who love acting do — not for visibility, but because the work itself is the point.

## A Character Actor's Legacy

The phrase "character actor" is often used as a consolation prize — the thing you call someone who wasn't famous enough to be a lead. In Ramakant Dayama's case, it was a description of mastery. Character actors are the infrastructure of narrative cinema. They are the reason you believe the world the story is set in. They are the difference between a scene that feels written and a scene that feels lived.

Dayama brought something specific to every role: a physical presence that was small — Shubhangi Latkar described him as someone who "may have looked tiny in appearance" — but a quality that was enormous. He could make you believe that his character had a life before the scene started and would have one after it ended. This is not a skill that wins awards. It is a skill that makes award-winning films possible.

His career spanned decades of Hindi cinema and Marathi theatre. He worked across the full spectrum — commercial films, independent cinema, prestige television, stage productions. He was the kind of actor who said yes to good work regardless of the budget, because the work was the currency that mattered.

## "Let Me Get Well Soon"

Shubhangi Latkar's tribute, posted on Instagram alongside a video of Dayama at a party, contained the kind of detail that can break your heart if you sit with it.

"We had so many unfinished plans," she wrote. "After years, I had truly wished to work with him again. We had decided to do a beautiful Hindi play together. When I requested him, he smiled and said, **'Let me get well soon.'**"

They had also planned to present selected poems together on stage. "That dream, too, now remains unfinished."

She described him as "full of life, warmth, and energy," as "a spontaneous dancer, a soulful singer, a brilliant actor," and — in perhaps the most telling phrase — "a wise advisor whose words always carried meaning."

CINTAA's official statement called him "a respected former Executive Committee member and a cherished part of our fraternity" whose "dedication, wisdom, and contribution to the artist community will always be remembered with deep respect and gratitude."

## A Father's Legacy

Ramakant Dayama was also the father of **Yashaswini Dayama**, the actress and social media creator known for her roles in web series and independent films. The father-daughter relationship was visible on social media — they appeared together in photos and videos that showed the easy, affectionate dynamic of a creative family.

For the diaspora, Yashaswini Dayama is the more recognizable name — she belongs to the generation of Indian content creators who bridge the gap between traditional Bollywood and the digital-first entertainment that NRIs consume. But her craft was shaped by growing up in the home of a man who treated acting as a vocation, not a career.

## The Silence After

Shubhangi Latkar ended her tribute with a line that applies to every character actor who ever made a good film better: "Some losses leave behind a silence that words fail to express."

Ramakant Dayama was not the silence in the films he appeared in. He was the noise — the texture, the grain, the lived-in quality that made fictional worlds feel inhabited. Without actors like him, leads have no one to act against. Without actors like him, stories have settings but no atmosphere.

He was 69. He was unwell. He wanted to get well. He wanted to do a play. He wanted to read poems on stage. He did not get the chance.

The films remain. The performances remain. The face you recognized but could never name — that remains too, and it will keep doing what it always did: making every scene it appears in feel a little more real than you expected.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Hema Malini Accepts Dharmendra's Posthumous Padma Vibhushan
# ══════════════════════════════════════════════════════════════
slug2 = "hema-malini-dharmendra-posthumous-padma-vibhushan-tears-ahana-deol-ceremony-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Hema Malini Stood in Rashtrapati Bhavan in a Pink Saree and Accepted the Padma Vibhushan That Her Husband Would Never Hold. Ahana Deol Could Not Stop Crying. Neither Could Most of India.",
        "subheadline": "On May 25, 2026, President Droupadi Murmu conferred the Padma Vibhushan — India's second-highest civilian honor — posthumously on Dharmendra Deol, who died in November 2025 at the age of 89 after a prolonged illness. His wife, Hema Malini, accepted it on his behalf. Their daughter Ahana Deol stood beside her and broke down in tears. The ceremony was part of the first Civil Investiture of 2026, but for the millions watching, there was only one moment: the woman in pink receiving a medal for a man who spent six decades making India believe in its own heroes.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 80,
        "tags": ["Dharmendra", "Hema Malini", "Padma Vibhushan", "Padma Awards 2026", "Ahana Deol", "posthumous", "Rashtrapati Bhavan", "President Murmu", "Sholay", "Indian cinema", "Bollywood legend", "diaspora", "NRI"],
        "diaspora_angle": "For the Indian diaspora, Dharmendra is not a name that requires context. He is Veeru. He is the man on the water tank in Sholay, threatening to jump if the girl's father doesn't agree to the marriage, turning a suicide threat into a comedy scene that every Indian family quotes at weddings. He is the actor your parents watched before they became your parents, the face on the VHS tapes that came in the suitcases of relatives visiting from India, the voice that your father could imitate even if he couldn't imitate anything else. When NRIs of a certain generation say 'Bollywood,' they mean a very specific era — the era of Amitabh and Dharmendra, of Sholay and Chupke Chupke. Dharmendra was the warm half of that equation, the one who made you feel safe, the one who could be funny and dangerous in the same scene. Watching Hema Malini accept a medal on his behalf is not entertainment news. It is the kind of moment that makes you call your parents.",
        "sources": [
            {"url": "https://www.latestly.com/entertainment/bollywood/padma-awards-2026-hema-malini-accepts-posthumous-padma-vibhushan-for-dharmendra-padma-bhushan-conferred-on-mammootty-alka-yagnik-watch-video-6869253.html", "name": "LatestLY"},
            {"url": "https://www.filmibeat.com/bollywood/hema-malini-emotional-dharmendra-padma-vibhushan-2026/", "name": "FilmiBeat"},
            {"url": "https://www.zoomtventertainment.com/bollywood/hema-malini-becomes-overwhelmed-while-receiving-dharmendr-posthumous-padma-vibhushan-ahana-breaks-down-in-tears", "name": "Zoom TV"},
            {"url": "https://www.boldsky.com/entertainment/padma-awards-2026-hema-malini-dharmendra-padma-vibhushan/", "name": "Boldsky"}
        ],
        "image_search_query": "Dharmendra actor",
        "image_entities": ["Dharmendra"],
        "image_must_show": "Dharmendra, Indian actor",
        "word_count": 770,
        "body": """The ceremony was routine. The moment was not.

On **May 25, 2026**, at **Rashtrapati Bhavan** in New Delhi, President **Droupadi Murmu** conferred the first batch of **66 Padma Awards** for the year. There were five Padma Vibhushans, thirteen Padma Bhushans, and 113 Padma Shris. There were scientists, athletes, musicians, social workers, and doctors. The ceremony honored **131 recipients** in total.

But for most of India — and for the Indian diaspora around the world — there was only one image from the evening that mattered.

## The Woman in Pink

**Hema Malini** walked to the stage in a **pink saree**. She is 77 years old. She has been in Indian cinema for over fifty years. She was the Dream Girl before that phrase became a marketing cliché. She was one half of Indian cinema's most beloved real-life romance — the other half being **Dharmendra Deol**, who died in **November 2025** at the age of 89, after a prolonged illness.

The **Padma Vibhushan** — India's second-highest civilian honor — had been announced for Dharmendra in January 2026. He could not receive it. He was already gone.

So his wife walked to the stage. She accepted the medal from the President. She held it. And somewhere in the front rows, their daughter **Ahana Deol** — who had accompanied her mother to Delhi for the ceremony — broke down in tears.

The cameras captured everything. The controlled composure of a woman who has spent five decades in front of cameras and knows exactly how much emotion to show. The moment the composure cracked. The daughter who could not hold it together at all.

## What Dharmendra Was

To list Dharmendra's filmography is to list the evolution of Hindi cinema from the 1960s to the 2020s. Over **300 films**. More hit films than any other actor in Indian cinema history by some counts. A career that began with **Dil Bhi Tera Hum Bhi Tere** in 1960 and continued, in various forms, until he was well into his eighties.

But numbers do not capture what Dharmendra was to his audience.

He was **Veeru** in **Sholay** (1975) — the charming, reckless, loyal friend in what remains the most beloved Hindi film ever made. The water tank scene, in which Veeru threatens to jump unless Basanti's father agrees to the marriage, is not just a scene. It is a reference point. It is the scene that Indian families across the world quote, reenact, and build jokes around at every family gathering. It has survived three generations of audience turnover because it is fundamentally about joy — the specific, unearned, infectious joy of a man who refuses to take his own desperation seriously.

He was the lead in **Chupke Chupke** (1975) — the comedy that proved he could be as funny as he was tough. He was the action star of **Phool Aur Patthar** (1966). He was the romantic lead of **Haqeeqat** (1964). He was the patriarch of **Apne** (2007), sharing the screen with both his sons, Sunny and Bobby Deol, in a film that was barely a film but was entirely about the weight of being Dharmendra's family.

He was, in the simplest terms, the actor who made masculinity feel warm. In an industry that often defined its heroes through intensity — through Amitabh's anger, through Rajesh Khanna's brooding, through later generations' six-packs — Dharmendra was the one who could fight and then make you laugh. He could be the strongest man in the room and the funniest. He made it look easy. It was not easy.

## The Deol Dynasty

Dharmendra's legacy extends beyond his own filmography. His sons — **Sunny Deol** and **Bobby Deol** from his first wife Prakash Kaur, and **Esha Deol** and **Ahana Deol** from Hema Malini — represent one of Indian cinema's most enduring families. Sunny's career peak in **Gadar** (2001) and its sequel **Gadar 2** (2023), Bobby's reinvention in recent years, and the family's continued presence in public life all trace back to the foundation that Dharmendra built.

He was also a **Member of Parliament**, representing Bikaner in the Lok Sabha from 2004 to 2009 — a political career that was widely understood as secondary to his identity as an artist.

## The Padma Vibhushan

The Padma Vibhushan recognizes "exceptional and distinguished service" to the nation. Dharmendra had previously received the **Padma Bhushan** in 2012. The posthumous elevation to Vibhushan was widely expected and universally supported — the industry, the public, and the political establishment all agreed that this was overdue even before his death.

What the medal cannot capture is the emotional architecture of a nation's relationship with a man who spent six decades playing its heroes. Dharmendra did not just act in films. He provided the template for what an Indian man could be on screen — strong without cruelty, funny without weakness, romantic without artifice.

**Karan Johar**, who confirmed Dharmendra's death in November 2025, called him "a bona fide Legend of Indian Cinema." The phrase is accurate but insufficient. Legends are distant. Dharmendra was never distant. He was the actor who felt like family — the reason your mother smiled when his name came up, the reason your father could do exactly one impression.

On May 25, his wife held a medal and his daughter cried. Somewhere, a family in New Jersey or Brampton or Leicester saw the footage and did the same.

The strongest man in the room. The funniest. And now, the most missed.""",
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
# IMAGE SOURCING — Wikipedia first for person articles
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

# Check image skip list
skip_list = set()
skip_file = Path.home() / "workspace/the-videshi-news/pipeline/image-skip-list.json"
if skip_file.exists():
    try:
        skip_list = set(json.loads(skip_file.read_text()))
    except:
        pass

image_tasks = [
    {
        "slug": slug1,
        "person": "Ramakant Dayama",
        "alt_persons": ["Ramakant Daayama"],
        "pexels_fallback": None,  # No image > wrong image for a character actor
        "attribution": "Wikimedia Commons",
    },
    {
        "slug": slug2,
        "person": "Dharmendra",
        "alt_persons": ["Dharmendra (actor)"],
        "pexels_fallback": None,  # Wikipedia should have Dharmendra
        "attribution": "Wikimedia Commons",
    },
]

for task in image_tasks:
    slug = task["slug"]
    if slug in skip_list:
        print(f"  ⏭ Skipped (in skip list): {slug[:50]}")
        continue

    # Find the article ID
    art_match = [a for a in articles if a["slug"] == slug]
    if not art_match:
        print(f"  ⚠ No article found for {slug[:50]}")
        continue
    art_id = art_match[0]["id"]

    # Step 1: Wikipedia — try primary name, then alternates
    img_url = fetch_wikipedia_person_image(task["person"])
    attribution = task["attribution"]

    if not img_url and "alt_persons" in task:
        for alt in task["alt_persons"]:
            img_url = fetch_wikipedia_person_image(alt)
            if img_url:
                break

    # Step 2: Pexels fallback (only if specified)
    if not img_url and task.get("pexels_fallback"):
        print(f"  Wikipedia returned nothing for '{task['person']}', trying Pexels...")
        img_url = fetch_pexels_image(task["pexels_fallback"])
        attribution = "The Videshi"

    if img_url:
        # Upload to Supabase
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        status = sb_patch(
            "p2_articles",
            f"id=eq.{art_id}",
            {"image_url": final_url, "image_attribution": attribution}
        )
        print(f"  PATCH image → HTTP {status} for {slug[:50]}")
    else:
        print(f"  ⚠ No image found for: {slug[:50]} — leaving blank (no image > wrong image)")


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
