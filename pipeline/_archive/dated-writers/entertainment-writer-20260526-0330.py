#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 03:30 UTC batch (20:30 PDT May 25):
1. Alka Yagnik receives Padma Bhushan — India's most prolific playback voice
   honored today while battling sensorineural hearing loss she's had since 2024.
   She has put singing on hold and says "music today has lost its soul."
2. Suriya's Karuppu crosses ₹240 crore worldwide in 10 days —
   the temple guardian deity vs systemic corruption film becomes Suriya's
   highest-grossing film and 2026's biggest Tamil blockbuster so far.
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
# ARTICLE 1: Alka Yagnik's Padma Bhushan — Honored While She Cannot Hear
# ══════════════════════════════════════════════════════════════
slug1 = "alka-yagnik-padma-bhushan-hearing-loss-bollywood-playback-singer-ceremony-20260525"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Alka Yagnik Just Received the Padma Bhushan. She Has Not Been Able to Sing Since 2024. The Voice Behind 'Baazigar,' 'Taal,' and a Thousand NRI Weddings Was Honored for a Career She Can No Longer Continue.",
        "subheadline": "President Droupadi Murmu conferred the Padma Bhushan — India's third-highest civilian honor — on the 58-year-old playback singer at Rashtrapati Bhavan on May 25. Alka Yagnik was diagnosed with rare sensorineural hearing loss caused by a viral attack in June 2024. She has been unable to take new singing assignments since. In a recent interview, she said she is 'still suffering' from the condition and that 'music today has lost its soul.' For the Indian diaspora, her voice is not background music. It is the sound of home.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 82,
        "tags": ["Alka Yagnik", "Padma Bhushan", "Padma Awards 2026", "playback singer", "hearing loss", "sensorineural", "Bollywood music", "Hindi cinema", "Filmfare Awards", "President Murmu", "Rashtrapati Bhavan", "diaspora", "NRI"],
        "diaspora_angle": "For the Indian diaspora, Alka Yagnik's voice is not an artist's catalog. It is the sound system at your cousin's sangeet. It is the aux cord at every road trip your parents ever took you on. It is the song your mother hums while cooking on a Sunday in New Jersey or Scarborough or Wembley. 'Tip Tip Barsa Paani' at a summer barbecue in Houston. 'Kuch Kuch Hota Hai' at a Diwali party in Silicon Valley. 'Baazigar O Baazigar' in a car your father drove before you were old enough to know why he loved it. NRIs do not listen to Alka Yagnik the way they listen to other artists — as a choice, as a preference. They listen to her the way they breathe. She is simply present. The fact that this voice — the voice that defined what Bollywood sounds like for three decades — can no longer hear itself is the kind of loss that doesn't register as entertainment news. It registers as grief.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/amp/news/features/alka-yagnik-reveals-ongoing-hearing-condition-puts-singing-assignments-hold/", "name": "Bollywood Hungama"},
            {"url": "https://www.latestly.com/entertainment/bollywood/padma-awards-2026-hema-malini-accepts-posthumous-padma-vibhushan-for-dharmendra-padma-bhushan-conferred-on-mammootty-alka-yagnik-watch-video-6869253.html", "name": "LatestLY"},
            {"url": "https://www.glamsham.com/entertainment/padma-awards-2026-to-honour-dharmendra-mammootty-alka-yagnik-and-other-entertainment-icons", "name": "GlamSham"},
            {"url": "https://www.filmfare.com/news/bollywood/alka-yagnik-diagnosed-with-a-rare-sensorineural-nerve-hearing-loss", "name": "Filmfare"}
        ],
        "image_search_query": "Alka Yagnik",
        "image_entities": ["Alka Yagnik"],
        "image_must_show": "Alka Yagnik, Indian playback singer",
        "word_count": 780,
        "body": """On May 25, 2026, President Droupadi Murmu placed the **Padma Bhushan** — India's third-highest civilian honor — around the neck of a woman who cannot hear the sound of her own voice.

**Alka Yagnik** is 58 years old. She has recorded more songs than most people will hear in a lifetime. By some estimates, she has lent her voice to over **3,000 songs** across four decades, in Hindi, Bengali, Marathi, Gujarati, and several other languages. She has won **seven Filmfare Awards** for Best Female Playback Singer — a record she shares with no one in its current configuration. She is, by any metric that matters, the most prolific female playback singer in the history of Indian cinema.

And she has not been able to sing since 2024.

## The Diagnosis

In **June 2024**, Alka Yagnik shared an Instagram post that stopped her fans mid-scroll. She had been diagnosed with **rare sensorineural hearing loss**, caused by a viral attack. The condition affects the inner ear and auditory nerves, making it progressively difficult to process sound — the exact faculty on which her entire career, identity, and daily life depend.

"I woke up one day and felt that I was not hearing as well as I used to," she later told NDTV. "It was sudden. It was terrifying."

Sensorineural hearing loss is not the kind that can be fixed with a hearing aid turned to the right frequency. It is nerve damage. Medical experts note that when caused by a viral infection, the window for effective treatment is narrow — often the first few weeks — and even then, recovery is partial. For a singer whose instrument is not a guitar or a piano but her own auditory system, the condition is professionally terminal in a way that no other health diagnosis could replicate.

In **March 2026**, speaking to Bollywood Hungama, Yagnik confirmed that she is **"still suffering"** from the condition and has been unable to take up new singing assignments. Her last recorded song was **'Naram Kaalja'** from Imtiaz Ali's *Amar Singh Chamkila* (2024). That song — about vulnerability, about the softness hidden inside a performer — now reads like an accidental farewell.

## The Songs That Built a Diaspora's Soundtrack

To list Alka Yagnik's biggest songs is to list the emotional architecture of Indian popular culture from 1988 to 2024.

**Ek Do Teen** (*Tezaab*, 1988) — the song that introduced her to a generation.
**Baazigar O Baazigar** (*Baazigar*, 1993) — Shah Rukh Khan's breakout, her voice on the defining track.
**Choli Ke Peeche Kya Hai** (*Khalnayak*, 1993) — the most controversial, most hummed, most danced-to song of the decade.
**Tip Tip Barsa Paani** (*Mohra*, 1994) — still played at Indian weddings thirty-two years later.
**Didi Tera Devar Deewana** (*Hum Aapke Hain Koun..!*, 1994) — the wedding anthem that has never been retired.
**Taal Se Taal Mila** (*Taal*, 1999) — AR Rahman's composition, her delivery.
**Kuch Kuch Hota Hai** (*Kuch Kuch Hota Hai*, 1998) — with Udit Narayan, the song that taught a generation of NRIs what love sounded like.
**Kajra Re** (*Bunty Aur Babli*, 2005) — the playful seduction anthem she shared with Shankar Mahadevan and Javed Ali.
**Dilbar Dilbar** (*Sirf Tum*, 1999) — the club track that predated the remix era by a decade.

These are not just hits. They are calendar markers. NRIs know exactly where they were when they first heard these songs — at a cousin's wedding in New Delhi, in the back seat of a Honda Odyssey on the New Jersey Turnpike, at a Navratri garba in Leicester. Alka Yagnik did not just provide the vocals. She provided the emotional infrastructure.

## "Music Today Has Lost Its Soul"

In the same Bollywood Hungama interview where she confirmed her ongoing condition, Yagnik offered a critique of the contemporary music industry that would have been controversial from anyone with less standing.

**"Music today has lost its soul,"** she said.

The remark was not elaborated upon. It did not need to be. Coming from a woman who collaborated with **Anu Malik**, **Nadeem-Shravan**, **AR Rahman**, **Jatin-Lalit**, and **Vishal-Shekhar** across their defining periods, the statement carries the weight of comparative experience. She has been present for every phase of Bollywood music's evolution — from the analog orchestrations of the late 1980s to the digital productions of the 2020s. She has heard the industry from the inside of a recording booth for 38 years. Her assessment is not a hot take. It is a diagnosis — one she is uniquely qualified to make, and one she delivered while unable to hear the music she is critiquing.

## The Ceremony

At Rashtrapati Bhavan on May 25, the Padma Bhushan was conferred alongside 65 other Padma Awards in the first Civil Investiture Ceremony of 2026. Dharmendra received a posthumous **Padma Vibhushan**, accepted by his wife Hema Malini. **Mammootty** received a **Padma Bhushan** for his contributions to Malayalam cinema — though he was absent from the ceremony, having attended a third honorary doctorate conferral at Mahatma Gandhi University in Kerala instead. **R Madhavan** received a **Padma Shri**.

Alka Yagnik was present. She accepted the honor in person.

"If you stay honest to your work," she said afterward, "recognition finds its own way."

For the diaspora, the image of Alka Yagnik standing in Rashtrapati Bhavan — honored by the nation for a voice that she can no longer use as she once did — is not a feel-good story. It is the kind of moment that makes you pull up 'Baazigar O Baazigar' on Spotify and sit with it for the full four minutes, remembering what it felt like the first time you heard it. Which is, perhaps, exactly what Yagnik would want. The songs outlive the singer. The singer outlives the voice. And the voice — that particular voice, that warm, soaring, unmistakable instrument — outlives everything.

Including the ability to hear it.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Suriya's Karuppu — Temple Deity Film Crosses ₹240 Crore
# ══════════════════════════════════════════════════════════════
slug2 = "suriya-karuppu-240-crore-worldwide-temple-deity-corruption-court-rj-balaji-tamil-20260525"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Suriya's Karuppu Just Crossed ₹240 Crore Worldwide. It Is About a Temple Guardian Deity Who Wakes Up, Discovers That Systemic Corruption Has Eaten His Village, and Takes the Fight to Court. Not to the Battlefield. To Court.",
        "subheadline": "The Tamil fantasy action drama, directed by RJ Balaji and co-starring Trisha Krishnan, has earned ₹172 crore in India and ₹67 crore overseas in ten days, making it Suriya's highest-grossing film ever. It has crossed ₹130 crore in Tamil Nadu alone. The overseas number — driven almost entirely by the diaspora in the Gulf, Malaysia, Singapore, North America, and the UK — tells you everything about who this film is for: people who left their village deity behind and never stopped thinking about him.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 75,
        "tags": ["Suriya", "Karuppu", "Tamil cinema", "box office", "RJ Balaji", "Trisha Krishnan", "Kollywood", "temple deity", "guardian deity", "village god", "corruption", "fantasy action", "diaspora", "NRI", "overseas collection"],
        "diaspora_angle": "Every Tamil, Telugu, Kannada, and Malayalam household in the diaspora has a version of this relationship — the village deity, the kuladevata, the temple that your grandparents built and your parents funded from abroad and your generation knows only from annual visits that stopped when the pandemic hit. Karuppu is not just a film about a deity waking up to fight corruption. It is a film about the specific guilt that the diaspora carries: that the village they left behind is not the village their grandparents protected. That the temple still stands but the values it represented — community justice, collective responsibility, the idea that some things are sacred — have been hollowed out by the same systemic forces that made emigration necessary in the first place. The ₹67 crore overseas collection is not just money. It is a community watching a film that articulates something they feel every time they send a remittance to a temple renovation fund from their apartment in Edison or Scarborough or Wembley.",
        "sources": [
            {"url": "https://sacnilk.com/movies/Karuppu_(Tamil)/collection", "name": "SacNilk"},
            {"url": "https://www.cinemaexpress.com/tamil/karuppu-box-office-suriya-second-weekend/", "name": "Cinema Express"},
            {"url": "https://www.pinkvilla.com/entertainment/south/karuppu-box-office-collections-suriya-238-crore-worldwide/", "name": "Pinkvilla"},
            {"url": "https://www.filmibeat.com/tamil/karuppu-box-office-collection-day-10/", "name": "FilmiBeat"}
        ],
        "image_search_query": "Suriya actor",
        "image_entities": ["Suriya"],
        "image_must_show": "Suriya, Tamil film actor",
        "word_count": 760,
        "body": """The premise sounds like it should not work as a commercial blockbuster. A village guardian deity — the kind who sits in a small stone shrine at the edge of a field, garlanded with marigolds and fed with offerings of chicken blood and toddy — wakes up after a long dormancy. He surveys the village he was consecrated to protect and discovers that it has been consumed by systemic corruption: land grabs, institutional rot, the erosion of every collective value that once held the community together. And instead of picking up a celestial weapon and laying waste to the corrupt — which is what every other Indian mythological action film would have him do — he goes to court.

This is **Karuppu**. Directed by **RJ Balaji**. Starring **Suriya** as the deity. Co-starring **Trisha Krishnan**. Released on May 15, 2026. And in ten days, it has crossed **₹240 crore worldwide**, making it the biggest Tamil film of 2026 so far and **Suriya's highest-grossing film** of his entire career.

## The Numbers

The breakdown tells its own story.

**India gross: ₹172.38 crore** in ten days, with ₹130+ crore from Tamil Nadu alone. That Tamil Nadu number is historically significant — it places Karuppu among the highest-grossing Tamil films ever in the state, surpassing several films that had wider release footprints and bigger marketing budgets.

**Overseas gross: ₹67 crore** and climbing. The Gulf states — UAE, Saudi Arabia, Qatar, Oman, Bahrain, Kuwait — account for the largest share, followed by Malaysia and Singapore, then North America and the UK. These are the geographies where Tamil and South Indian diaspora communities are densest, where the temple-going, remittance-sending, village-connected families that Karuppu speaks to are concentrated.

The second weekend held remarkably well. Day 9 brought ₹14.14 crore; Day 10 added ₹14.75 crore — an 18.5% increase from the previous day, which is almost unheard of for a film in its second week. Word of mouth is doing what marketing could not: converting skeptics into ticket-buyers.

## The Film's Argument

Karuppu is, at its core, a film about jurisdiction. The guardian deity's power is real — the film is unambiguous about this — but the film's central thesis is that supernatural power is not the appropriate tool for addressing systemic corruption. The deity chooses the legal system. He chooses arguments over miracles. He chooses the imperfect, corruptible, human institution of the court over the clean, unchallenged authority of divine intervention.

This is not a subtle choice. In a country where vigilante justice narratives dominate the box office — where the hero typically bypasses the system because the system is broken — Karuppu argues that the system, broken as it is, is the only mechanism that can produce lasting change. The deity does not fix the village by smiting the corrupt. He fixes it by establishing precedent.

**RJ Balaji**, who is better known as a comedian, radio host, and sharp political commentator, brings his media-literate sensibility to the direction. The film is not preachy despite its thesis. The courtroom sequences are intercut with the kind of high-energy fantasy action that Tamil cinema does better than any other industry — aerial deity sequences, mythological visual effects, the full-scale spectacle that audiences expect from a ₹100+ crore production.

## Suriya's Career Inflection

For **Suriya**, Karuppu represents something specific. He is 50 years old. His career has spanned three decades, from the romantic leads of the early 2000s (*Kaakha Kaakha*, *Ghajini*) through the action-star phase (*Singam* trilogy) to the more experimental recent work (*Jai Bhim*, the courtroom drama that became an Oscar conversation piece in 2021). Karuppu is his first film to cross ₹200 crore worldwide. The fact that it happened with a film about a deity who chooses law over violence is consistent with Suriya's trajectory — he has increasingly gravitated toward films that use commercial grammar to deliver systemic critiques.

**Trisha Krishnan**, who plays a key human role in the deity's legal battle, adds her own weight. She has been a leading actress in Tamil and Telugu cinema for over two decades. Her presence gives Karuppu a dual-star anchor that few Tamil films outside the Rajinikanth or Vijay vehicles can claim.

## What the Overseas Number Means

₹67 crore from overseas in ten days. For a Tamil-language film that was not marketed as a pan-India release, that was not dubbed into Hindi for a simultaneous north Indian release, that was not designed for the multiplexes of Mumbai and Delhi — this is a number that speaks exclusively to the diaspora.

Tamil NRIs bought these tickets. They drove to the one theater in their city that was showing a Tamil film on a weeknight. They took their children, who may or may not speak Tamil fluently, to watch a film about a concept — the kuladevata, the village guardian — that exists in their family's memory but not in their daily reality.

The kuladevata is one of the most emotionally charged concepts in South Indian diaspora life. Every family has one. Every family knows which village temple houses theirs. Many families send money annually for the temple's upkeep — a ritual that persists across generations and continents, often without the younger generation fully understanding why. Karuppu takes this relationship — this guilt, this devotion, this inherited obligation — and puts it on screen at scale.

The deity wakes up. The village is broken. The fix is not magic. The fix is showing up and arguing your case in a system that was built by humans and can only be repaired by humans — even if you happen to be a god.

₹240 crore suggests that a lot of people needed to hear that.""",
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
    {"slug": slug1, "person": "Alka Yagnik", "pexels_fallback": "Indian female singer recording studio microphone", "attribution": "Wikimedia Commons"},
    {"slug": slug2, "person": "Suriya (actor)", "pexels_fallback": "Indian temple deity village shrine guardian", "attribution": "Wikimedia Commons"},
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

    # Step 1: Wikipedia
    img_url = fetch_wikipedia_person_image(task["person"])
    attribution = task["attribution"]

    # Step 2: Pexels fallback
    if not img_url:
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
