#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 04:30 PDT batch:
1. Drishyam 3 crosses ₹160 crore worldwide in 6 days — Mohanlal's franchise
   finale becomes the 8th highest-grossing Malayalam film of all time. The
   overseas gross of ₹84+ crore tells the diaspora story: Georgekutty is the
   most discussed fictional character in every NRI WhatsApp family group.
2. Vashu Bhagnani vs. the Dhawans — The legal battle over 'Chunari Chunari'
   and 'Ishq Sona Hai' from Biwi No. 1 being used in Hai Jawani Toh Ishq
   Hona Hai. A ₹27 crore Coolie No. 1 loss, an IP lawsuit filed in Bihar,
   and a producer who says the industry has lost its ethics.
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
        try:
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
        except Exception as e:
            print(f"  Pexels error for '{q}': {e}")
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
# ARTICLE 1: Drishyam 3 Crosses ₹160 Crore Worldwide in 6 Days
# ══════════════════════════════════════════════════════════════
slug1 = "drishyam-3-160-crore-worldwide-6-days-mohanlal-8th-highest-grossing-malayalam-film-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Drishyam 3 Has Crossed ₹160 Crore Worldwide in Six Days. It Is Now the 8th Highest-Grossing Malayalam Film of All Time. The Overseas Gross Alone Is ₹84 Crore. Malayalam Cinema Is Not Competing With Bollywood Anymore. It Is Outperforming It.",
        "subheadline": "Jeethu Joseph's franchise finale collected ₹62 crore India net and over ₹160 crore worldwide by Day 6, driven by a ₹84 crore overseas gross that dwarfs what most Hindi-language films earn in international markets. Mohanlal's fifth ₹100-crore film, Drishyam 3 is now his third to cross ₹150 crore globally. A Hindi-language version with a separate narrative is reportedly in development. For the diaspora, Georgekutty is not a character. He is an argument — the argument that an ordinary man with no connections, no wealth, and no institutional power can protect his family against the state if he is smart enough. Every NRI WhatsApp group has debated this premise for a decade.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 80,
        "tags": ["Drishyam 3", "Mohanlal", "Jeethu Joseph", "Malayalam cinema", "Mollywood", "box office", "overseas collection", "Georgekutty", "thriller", "franchise", "Kerala", "diaspora", "NRI"],
        "diaspora_angle": "Georgekutty is the most debated fictional character in the Indian diaspora's collective consciousness. Every NRI family group chat has had the Drishyam argument at least once: could you do what he did? Would you? The ₹84 crore overseas gross — for a Malayalam-language film, in a market where Hindi films with ten times the marketing budget struggle to cross ₹50 crore abroad — is not just a box office number. It is a census. It counts exactly how many Malayalam-speaking families in the Gulf, in North America, in the UK, in Singapore and Malaysia, still go to the theater together for a film in their language. Drishyam 3 is proof that regional Indian cinema does not need Hindi dubbing to travel. It needs a story that matters to its audience. And Georgekutty's story — the story of a man who has nothing except his intelligence and his willingness to do anything for his family — matters to every immigrant who has ever felt outmatched by a system they did not build.",
        "sources": [
            {"url": "https://www.sacnilk.com/movies/Drishyam_3_(Malayalam)/collection", "name": "SacNilk"},
            {"url": "https://www.livemint.com/entertainment/drishyam-3-box-office-collection-day-5", "name": "Mint"},
            {"url": "https://www.bollywoodlife.com/box-office/drishyam-3-box-office-collection-day-6", "name": "Bollywood Life"},
            {"url": "https://thetimesofbengal.com/drishyam-3-box-office-collection-day-6-160-crore/", "name": "Times of Bengal"},
            {"url": "https://www.herzindagi.com/entertainment/drishyam-3-box-office-collection-day-6-mohanlal", "name": "HerZindagi"}
        ],
        "image_search_query": "Mohanlal actor",
        "image_entities": ["Mohanlal"],
        "image_must_show": "Mohanlal, Malayalam film superstar",
        "word_count": 790,
        "body": """By Day 6, the numbers are no longer a box office story. They are an industry thesis.

**Drishyam 3** — the final chapter of Jeethu Joseph's franchise about an ordinary cable operator who outwits the state to protect his family — has crossed **₹160 crore worldwide** in six days. The India net stands at approximately **₹62 crore**. The overseas gross is **₹84+ crore**. It is now the **8th highest-grossing Malayalam film of all time**, Mohanlal's **third film to cross ₹150 crore globally**, and his **fifth ₹100-crore film**.

For a Malayalam-language film. In six days.

## The Numbers That Rewrite the Conversation

To understand what ₹84 crore overseas means for a Malayalam film, consider what Hindi-language films earn in the same markets.

Most mid-budget Bollywood releases — the kind with recognizable names, national marketing campaigns, and Hindi as their built-in advantage — earn between ₹10-40 crore overseas in their entire theatrical run. Films like **Mardaani 3** (₹52.99 crore India total) or **Pati Patni Aur Woh Do** (₹38.59 crore India total) are considered solid performers domestically but rarely dominate overseas. Drishyam 3's overseas number — ₹84 crore in less than a week — exceeds what many of those films earn globally.

This is not an anomaly. This is the third time in 2026 that a Malayalam film has achieved this scale. **L2: Empuraan** and **Thudarum** preceded it. Mohanlal himself now has three films above ₹150 crore worldwide. Malayalam cinema — with a domestic market of roughly 3.5 crore people in Kerala — is producing blockbusters that travel further than Hindi films released in a market of 60 crore Hindi speakers.

The reason is the diaspora.

## The Diaspora Economics of Malayalam Cinema

The **Gulf states** account for the largest share of Drishyam 3's overseas gross. The UAE, Saudi Arabia, Qatar, Oman, Bahrain, and Kuwait together are home to an estimated 3-4 million Malayali workers and families. This is not a tourist audience. These are families who left Kerala for economic opportunity, maintained their language and cultural connections, and go to the cinema in Dubai or Muscat the way their parents went to the cinema in Kochi or Thiruvananthapuram.

**North America** is the second-largest overseas market. The Malayali population in the United States and Canada has grown significantly in the last decade, driven by tech-sector immigration and nursing-profession migration. Unlike the Gulf, where Malayalam cinema has always had a theater presence, the North American market is newer — and the fact that Drishyam 3 is filling screens in cities like Houston, Dallas, Chicago, and the Bay Area speaks to a demand that exhibitors are only now beginning to meet.

**Malaysia and Singapore** round out the top markets, driven by the Tamil-Malayalam cultural overlap and established South Indian cinema distribution networks.

## Why Georgekutty Travels

The Drishyam franchise is, at its core, a thought experiment. **Georgekutty** — played by Mohanlal with a stillness that is the opposite of the action-hero mode he is equally capable of — is a man with no formal education, no political connections, no institutional power. He runs a cable TV operation in a small Kerala town. When his family is threatened by the police, by the state, by the mother of a boy his daughter accidentally killed, he does not fight. He does not run. He schemes. He constructs an alibi so perfect that the entire machinery of investigation — forensics, interrogation, exhumation, political pressure — cannot break it.

This premise resonates with the diaspora in a way that no action film can.

Every immigrant has felt the asymmetry. Every H-1B holder who has navigated USCIS paperwork. Every Gulf worker who has dealt with the kafala system. Every student who has written the same essay fourteen times to satisfy a visa officer. The immigrant experience is, fundamentally, the experience of being outmatched by a system — and surviving it through preparation, attention to detail, and the willingness to endure discomfort that the system's operators never expect.

Georgekutty is the fantasy version of this. He is the immigrant who not only survives the system but defeats it. The fact that he does it for his family — not for wealth, not for revenge, not for ideology — makes it the most relatable motivation in diaspora cinema.

## The Franchise's Cultural Weight

The first **Drishyam** (2013) became a phenomenon that transcended language. It was remade in Hindi (2015, starring Ajay Devgn), Telugu (*Drushyam*, 2014), Kannada, and Chinese. The Hindi version itself became a franchise — **Drishyam 2** (Hindi, 2022) earned ₹240+ crore worldwide. Jeethu Joseph's Malayalam originals, however, have always been the definitive versions. The remakes are adaptations. The Malayalam films are the text.

**Drishyam 2** (Malayalam, 2021) was released on Amazon Prime Video during the pandemic and became one of the most-watched Indian films on the platform globally. It bypassed theaters entirely and still entered the cultural conversation at the same scale as a theatrical blockbuster.

**Drishyam 3** returns to theaters — and the result is a ₹160-crore validation of the franchise's theatrical viability. The second weekend held remarkably: Day 5 saw ₹7.35 crore, Day 6 maintained around ₹62 crore cumulative India net. Mixed reviews — some critics found the finale's resolution less elegant than the first two installments — have not slowed the audience.

## The Hindi Version

Reports indicate that a **Hindi-language Drishyam 3** is in development, but with a distinct narrative rather than a direct remake. This is significant — it suggests that the producers recognize the Malayalam original's standalone identity and are unwilling to simply transplant it. Whether Ajay Devgn returns as the Hindi Georgekutty remains unconfirmed.

For the Malayali diaspora, though, the Hindi version is secondary. The Malayalam Drishyam is theirs. It is the film they watch with their parents, debate with their siblings, and reference in group chats. Georgekutty's stillness is Mohanlal's stillness — the specific, irreplaceable quality of an actor who has been working for 46 years and knows that the most powerful thing a performer can do on screen is nothing.

₹160 crore in six days. ₹84 crore from overseas. For a film in a language spoken by 38 million people.

Malayalam cinema is not an alternative to Bollywood anymore. It is the standard.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Vashu Bhagnani vs. the Dhawans — Bollywood's Song-Rights War
# ══════════════════════════════════════════════════════════════
slug2 = "vashu-bhagnani-david-dhawan-varun-dhawan-chunari-chunari-hai-jawani-ip-lawsuit-bollywood-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Vashu Bhagnani Lost ₹27 Crore on Coolie No. 1. The Dhawans Never Called Him. Now They Have Used His Songs in a Film for Another Producer. He Is Suing. The Songs Are 'Chunari Chunari' and 'Ishq Sona Hai' — and If You Grew Up in the 1990s, You Know Exactly Why This Hurts.",
        "subheadline": "Producer Vashu Bhagnani has filed a lawsuit in Katihar, Bihar, against Tips Industries, Ramesh Taurani, and the makers of Hai Jawani Toh Ishq Hona Hai — starring Varun Dhawan, directed by his father David Dhawan — over the unauthorized recreation of songs from Biwi No. 1 (1999). Bhagnani alleges that David Dhawan, who directed the original film for him, recreated 'Chunari Chunari' and 'Ishq Sona Hai' for a competing production without permission. Tips Industries says it owns the music rights. Bhagnani says ownership is not the issue — ethics is. The court has issued a status quo order. The film releases June 5.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 76,
        "tags": ["Vashu Bhagnani", "David Dhawan", "Varun Dhawan", "Hai Jawani Toh Ishq Hona Hai", "Biwi No. 1", "Chunari Chunari", "song rights", "intellectual property", "Bollywood", "Tips Industries", "Ramesh Taurani", "lawsuit", "music rights", "remake"],
        "diaspora_angle": "If you grew up in an NRI household in the late 1990s and early 2000s, 'Chunari Chunari' was not just a song. It was the track that played at every community Diwali party from Edison to Wembley. It was the sangeet choreography your older cousin performed. It was the CD your parents brought back from India in a suitcase that smelled like mothballs. Biwi No. 1 was one of those films that NRI families owned on VHS or DVD before streaming made ownership irrelevant — the kind of film that was watched communally, on a Sunday afternoon, with the whole family in the living room. The fact that these songs — 'Chunari Chunari,' 'Ishq Sona Hai' — are now at the center of a legal battle between the producer who financed the original and the director who made it is the kind of news that lands differently in the diaspora. Because the diaspora does not see these as assets in a music-rights catalog. They see them as cultural markers. Songs that defined a generation's relationship with being Indian while being somewhere else. And the fight over who owns them is, in a way, a fight over who owns that memory.",
        "sources": [
            {"url": "https://www.tezzbuzz.com/david-dhawan-vashu-bhagnani-chunari-chunari/", "name": "Tezz Buzz"},
            {"url": "https://www.newspointapp.com/mouni-roy-varun-dhawan-mother/", "name": "NewsPoint"},
            {"url": "https://www.idiva.com/hai-jawani-toh-ishq-hona-hai-vashu-bhagnani/", "name": "iDiva"},
            {"url": "https://www.thetimesofbengal.com/vashu-bhagnani-david-dhawan-coolie-no-1/", "name": "Times of Bengal"},
            {"url": "https://www.mensxp.com/entertainment/varun-dhawan-taurani-copyright/", "name": "MensXP"}
        ],
        "image_search_query": "Vashu Bhagnani",
        "image_entities": ["Vashu Bhagnani"],
        "image_must_show": "Vashu Bhagnani, Bollywood producer",
        "word_count": 780,
        "body": """The timeline tells the story better than either party's statement.

**1999:** Producer **Vashu Bhagnani** finances **Biwi No. 1**, directed by **David Dhawan**, starring Salman Khan and Karisma Kapoor. The film becomes the highest-grossing Hindi film of the year. Its soundtrack — composed by **Anu Malik** — produces two songs that enter the permanent NRI party playlist: **"Chunari Chunari"** and the title track. Bhagnani produces. David Dhawan directs. The relationship is professional, productive, and profitable.

**2020:** Bhagnani produces the **Coolie No. 1** remake, again directed by David Dhawan, this time starring David's son **Varun Dhawan** and Sara Ali Khan. It is released directly on Amazon Prime Video during the pandemic. Bhagnani says he suffered a loss of **₹27 crore**. He says Varun Dhawan never contacted him about the loss. "He never bothered to check," Bhagnani told media in May 2026.

**2025-2026:** David Dhawan directs **Hai Jawani Toh Ishq Hona Hai** — produced not by Bhagnani, but by **Ramesh Taurani's Tips Films** — starring Varun Dhawan, Mrunal Thakur, and Pooja Hegde. The film recreates **"Chunari Chunari"** and **"Ishq Sona Hai"** from Biwi No. 1. Bhagnani is not consulted.

**May 2026:** Bhagnani files a lawsuit in **Katihar, Bihar**, against Tips Industries and the film's makers for unauthorized use of intellectual property linked to Biwi No. 1. The court issues a **status quo order** covering the disputed songs.

The film's trailer launches on May 23. David Dhawan cries on stage. Varun Dhawan cracks a joke about the controversy. The film is set to release on **June 5, 2026**.

## The Music Rights Question

The legal dispute hinges on a distinction that Bollywood has historically treated as irrelevant: the difference between **owning a song** and **having the right to use it in a new context**.

**Tips Industries** — Ramesh Taurani's company — claims it is the "lawful owner" of the music rights to the songs in question. If Tips holds the master recording rights and the publishing rights, then technically, it can license those songs for use in a new film. This is how the music industry works. Rights are assets. Assets are tradable.

Bhagnani's argument is different. He is not disputing the legal ownership chain. He is disputing the **ethics** of the transaction. "He should have come to me," Bhagnani said about David Dhawan. "At least he should have said, 'Vashu, I want to use this song, my son is in the film.' How can you shoot the same songs for another producer? There should be ethics in the industry."

This is a distinction that Indian entertainment law has historically struggled to adjudicate. Copyright law deals in rights. It does not deal in relationships. The fact that David Dhawan directed Biwi No. 1 for Bhagnani — that the creative association between the director and those songs exists because of Bhagnani's financing — has no standing in a copyright dispute if the music rights were properly transferred to Tips.

But Bhagnani is not making a copyright argument. He is making a **reputation argument**, a **loyalty argument**, a claim that the handshake economy that has governed Bollywood for decades — where personal relationships are supposed to override legal technicalities — has been violated.

## The Coolie No. 1 Wound

The ₹27 crore loss on Coolie No. 1 is not incidental to this story. It is the foundation.

Bhagnani produced the remake as a goodwill project with the Dhawans. A father-son director-actor combination returning to a franchise that had worked before. When the pandemic forced the film to an OTT release — bypassing the theatrical revenue that would have recovered Bhagnani's investment — the financial loss was significant. But Bhagnani's complaint is not about the money. It is about the silence.

"Varun never even bothered to check," he said. In Bollywood's relational economy, this is a declaration of rupture. The producer financed the actor's film, lost money, and the actor — who went on to become one of the highest-paid stars in the industry — did not acknowledge the loss. Six years later, the actor and his director-father are using songs from the producer's biggest film for a different producer's project.

## The Diaspora Dimension

**"Chunari Chunari"** is one of those songs that exists outside of its film. Most people who know the song cannot describe the scene it appears in. They cannot name the film without thinking for a moment. But they can sing it. They can hear the opening bars and be transported to a specific place — a function hall in Fremont, a living room in Scarborough, a Garba night in Leicester.

The song's identity — that specific mix of Anu Malik's composition, the late-90s Bollywood energy, the communal wedding-party association — belongs to a generation of NRIs in a way that transcends the legal question of who holds the master recording. The fact that it is being recreated for a new film, by the same director who originally brought it to life, for a different producer, without the original producer's consent, is the kind of story that makes the diaspora feel the fragility of the things they assumed were permanent.

## What Happens Next

The court's **status quo order** covers the disputed songs and their use. Ramesh Taurani has publicly said "everything has been sorted," but Bhagnani has **denied any settlement**, calling Taurani's claims untrue. Varun Dhawan, at the trailer launch, made a joking reference to the controversy — the kind of deflection that works on a press tour but not in a courtroom.

The film releases on June 5. Whether the songs survive the legal challenge, or are edited out, or are settled through the kind of behind-the-scenes negotiation that Bollywood prefers to litigation, remains unresolved.

What is not unresolved is the fracture. Vashu Bhagnani was a producer who financed David Dhawan's biggest hit, lost ₹27 crore on the sequel, and watched the same director use his songs for someone else's film. There is no legal remedy for that.""",
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
    {"slug": slug1, "person": "Mohanlal", "pexels_fallback": "Kerala cinema theater audience crowd", "attribution": "Wikimedia Commons"},
    {"slug": slug2, "person": "Vashu Bhagnani", "pexels_fallback": "Bollywood film producer studio Mumbai", "pexels_fallback_2": None, "attribution": "Wikimedia Commons"},
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
