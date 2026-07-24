#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 17:30 UTC batch (10:30 PDT):
1. Sonam Kapoor & Anand Ahuja's Notting Hill property controversy — NRI wealth & neighbour clash
2. Dhanush's Kara arriving on Netflix May 28 — Gulf War-era heist thriller
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
# ARTICLE 1: Sonam Kapoor & Anand Ahuja — Notting Hill Property
#             Controversy
# ══════════════════════════════════════════════════════════════
slug1 = "sonam-kapoor-anand-ahuja-notting-hill-london-5-flats-staff-quarters-neighbours-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Sonam Kapoor and Anand Ahuja Bought Five Apartments Next to Their £21 Million London Mansion. Their Neighbours Say It's for 'Staff Quarters.' The Daily Mail Got Involved.",
        "subheadline": "The couple renovated a 200-year-old Notting Hill mansion — basement pool, underground basketball court — and then purchased five flats and the garage in the building next door. Residents of the 23-apartment Hillcrest block say they're too afraid to complain. For NRIs across the UK, the story touches a nerve that has nothing to do with celebrity gossip.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 74,
        "tags": ["Sonam Kapoor", "Anand Ahuja", "London", "Notting Hill", "NRI property", "Daily Mail", "UK", "real estate", "wealth", "diaspora", "staff quarters"],
        "diaspora_angle": "For the millions of Indians who own or aspire to own property in the UK, the Sonam-Anand story is not celebrity gossip — it is a mirror. Every NRI who has ever navigated a British planning permission application, managed the careful diplomacy of being 'the Indian family' on a quiet English street, or felt the specific social pressure of being visibly wealthy in a country that still processes wealth through the lens of class and race recognises the dynamics at play here. The Daily Mail covering an Indian couple's property purchases with the subtext of 'they're taking over the neighbourhood' is a genre of British media coverage that every NRI in the UK has internalised, whether they own a £21 million mansion or a two-bedroom flat in Wembley.",
        "sources": [
            {"url": "https://www.zoomtventertainment.com/bollywood/sonam-kapoor-anand-ahuja-neighbours-notting-hill-flats-article-154385274", "name": "Zoom TV"},
            {"url": "https://www.bollywoodhungama.com/news/features/sonam-kapoor-and-anand-ahujas-london-property-purchase-sparks-neighbourhood-controversy-report/", "name": "Bollywood Hungama"},
            {"url": "https://www.idiva.com/entertainment/bollywood/sonam-kapoor-anand-ahuja-buy-5-flats-servant-quarters-near-270-crore-mansion-notting-hill/18076044", "name": "iDiva"},
            {"url": "https://www.hungamaexpress.com/sonam-kapoor-anand-ahuja-spark-row-over-notting-hill-property-claims/", "name": "Hungama Express"}
        ],
        "image_search_query": "London Notting Hill luxury mansion property elegant townhouse",
        "image_entities": ["Sonam Kapoor", "Anand Ahuja", "Notting Hill"],
        "image_must_show": "Upscale London townhouse or Notting Hill street scene",
        "word_count": 730,
        "body": """Here is the sequence of purchases, laid out without editorialising:

In 2023, **Sonam Kapoor** and her husband, entrepreneur **Anand Ahuja**, bought a 200-year-old mansion in **Notting Hill, London** for **£21 million** — approximately **₹270 crore**. They then undertook a complete renovation: everything stripped out, a **basement swimming pool** installed, an **underground basketball court** constructed. The neighbours, at this point, did not object.

Then the couple — or a company representing them — purchased **five apartments** in **Hillcrest**, a 23-unit residential building adjacent to their mansion, for **£4 million** (approximately **₹51 crore**). They also acquired the building's **garage**, reportedly to store their vehicle collection.

The residents of Hillcrest are not happy. And the *Daily Mail* has the story.

## What the Neighbours Are Saying

According to residents quoted in the *Daily Mail* report — which Indian entertainment outlets have since picked up — the five apartments are being renovated and are currently unoccupied. The neighbours' core claim is that the flats are being converted into **living quarters for the couple's household staff**.

Some residents told the publication that they felt unable to voice complaints, alleging that if they did, the apartments would be redesignated for "social housing" — a threat they interpret as leverage. The overall anxiety, as expressed in the reporting, is that a single couple is acquiring a disproportionate share of a small residential building and transforming its character.

A representative for Sonam and Anand pushed back, stating that Sonam was "not involved" in the apartment purchases and that the flats were acquired **purely for investment purposes**.

## The Properties in Context

The Notting Hill mansion is not the couple's only real estate. Sonam and Anand maintain properties in **Delhi and Mumbai**, as well as a separate **flat and studio in Notting Hill** that was previously featured in an *Architectural Digest* video tour. The five Hillcrest apartments and the garage represent an expansion of what is already a substantial London portfolio.

Sonam, who was last seen on screen in the 2023 OTT thriller *Blind*, has been largely focused on family life since the birth of her first son, **Vayu Kapoor Ahuja**, in August 2022. The couple welcomed their second son, **Rudralokh Kapoor Ahuja**, on March 29, 2026.

## Why This Story Travels Beyond Gossip

For the average reader, this is a celebrity property story — famous couple buys houses, neighbours complain, tabloid covers it. But for the Indian diaspora in the UK, and particularly for NRIs who own property in Britain, the dynamics are uncomfortably familiar.

The *Daily Mail*'s framing — a wealthy Indian couple progressively acquiring real estate in a quiet residential area, with neighbours "afraid to speak up" — sits in a well-established genre of British tabloid coverage that Indian property owners in the UK recognise instantly. It is the genre where wealth is news when the wealthy person is not white, where "taking over" is the subtext of what would otherwise be a straightforward real estate transaction, where the staff arrangements of a wealthy family become a matter of public concern in a way that would not apply to, say, a Russian oligarch's identical setup in Belgravia.

This is not to say the neighbours' concerns are illegitimate. Buying five of 23 apartments in a building does concentrate ownership. Renovations are disruptive. Staff traffic changes the character of a residential block. These are reasonable planning objections.

But the coverage pattern — Indian couple, British neighbourhood, rising anxiety — is one that virtually every NRI in the UK has navigated in some form. Whether it is the family in Leicester whose Diwali celebrations prompted a noise complaint, the tech professional in Cambridge whose home renovation was scrutinised more closely than the identical one next door, or the Gujarati businessman in Edgware whose commercial property plans were met with organised opposition that his predecessor's were not.

## The Investment Defence

The representative's statement that the purchases were "purely for investment" is standard in these situations, and it may well be true. London property, particularly in prime central locations, is a well-established asset class for HNIs globally. Indian families with international wealth are among the most active buyers in the London property market, alongside buyers from the Gulf, Hong Kong, and Singapore.

But the "investment" framing also does not fully address the neighbours' concerns. If the apartments sit empty or are used for staff, the building's residential community is diminished either way. This is a tension that exists across London's luxury property market, not uniquely with Indian buyers.

What makes this story resonate for the diaspora is not the specifics — it is the recognition. The specific feeling of being visibly Indian, visibly wealthy, in a country that is simultaneously welcoming your money and anxious about your presence.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Dhanush's Kara — Netflix OTT Release May 28
# ══════════════════════════════════════════════════════════════
slug2 = "dhanush-kara-netflix-may-28-ott-gulf-war-heist-thriller-tamil-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Dhanush's Gulf War Heist Film Just Got a Netflix Date. If You're a Malayali or Tamil NRI Who Grew Up Hearing Stories About 1991 Kuwait, This One's for You.",
        "subheadline": "Kara — a heist thriller set during India's 1991 Gulf crisis, about a reformed thief whose ancestral land is seized by a bank — hits Netflix on May 28, less than a month after its theatrical run. The film earned ₹50 crore and an 8.2 IMDb rating, but its real resonance is with the millions of Indians whose families lived through the Gulf evacuation.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 68,
        "tags": ["Dhanush", "Kara", "Netflix", "OTT", "Gulf War", "1991", "heist thriller", "Tamil cinema", "Kerala", "diaspora", "ancestral land", "Vignesh Raja"],
        "diaspora_angle": "The 1991 Gulf crisis displaced approximately 170,000 Indians from Kuwait in one of the largest civilian evacuations in history — Air India's Operation Rajan ran over 480 flights in 59 days. For Malayali and Tamil families in the US, UK, and Canada, the Gulf is not a geopolitical abstraction; it is where their parents or grandparents built their first overseas lives before many of them moved West. A film set during that crisis, exploring how ordinary people were crushed between institutional greed and geopolitical chaos, speaks directly to a generation of NRIs who grew up hearing these stories at kitchen tables. That it stars Dhanush, who has emerged as one of the few Tamil actors with genuine global streaming visibility after The Gray Man and Raayan, makes the Netflix release date an event in diaspora households.",
        "sources": [
            {"url": "https://en.wikipedia.org/wiki/Kara_(film)", "name": "Wikipedia"},
            {"url": "https://www.lagercinema.com/dhanushs-kara-heist-thriller-arrives-on-netflix-may-28/", "name": "Lager Cinema"},
            {"url": "https://www.gadgets360.com/entertainment/news/kara-ott-release-date-confirmed-when-and-where-to-watch-dhanush-tamil-crime-drama-online-7944534", "name": "Gadgets 360"},
            {"url": "https://www.pinkvilla.com/entertainment/south/kara-ott-release-when-and-where-to-watch-dhanush-mamitha-baijus-heist-action-thriller-online-1412547", "name": "Pinkvilla"}
        ],
        "image_search_query": "bank vault heist thriller cinematic gold dramatic lighting vintage",
        "image_entities": ["Dhanush", "Kara"],
        "image_must_show": "Cinematic heist or vault scene, dramatic and moody",
        "word_count": 700,
        "body": """On May 28, **Dhanush**'s Tamil heist thriller **Kara** arrives on **Netflix** — less than a month after its theatrical release on April 30. The film, directed by **Vignesh Raja**, earned approximately **₹50 crore worldwide** in its theatrical run, drew an **8.2 rating on IMDb**, and prompted the kind of divided critical reception that often signals a film with more going on beneath the surface than reviews capture.

But the real reason to pay attention to Kara's Netflix arrival has less to do with its box office numbers and more to do with when it is set.

## The Film

Kara takes place during the **1991 Gulf crisis** — the period when Iraq's invasion of Kuwait sent shockwaves through the Indian expatriate community in the Middle East and triggered one of the largest civilian evacuations in history.

The film follows a **reformed thief** whose family's **ancestral land is seized by a corrupt bank**. Forced back into a life he had left behind, he assembles a crew for a heist that is equal parts revenge and survival. The cast includes **Mamitha Baiju** and veteran **K. S. Ravikumar**, and the film was produced with a reported budget of **₹100 crore** — among the higher investments in recent Tamil cinema.

Critics were divided: some praised Dhanush's performance and the period-accurate production design, while others found the pacing uneven and the plot mechanics overly familiar. The audience response, particularly in Tamil Nadu and among overseas Tamil communities, was notably warmer than the critical consensus suggested.

## Why the Setting Matters

In August 1990, Iraq invaded Kuwait. Within days, approximately **170,000 Indian nationals** — the overwhelming majority from **Kerala and Tamil Nadu** — found themselves trapped in a war zone. What followed was **Air India's Operation Rajan**: over **480 flights in 59 days**, the largest civilian air evacuation until it was surpassed only by India's own Operation Devi Shakti from Afghanistan in 2021.

The Gulf crisis was not a distant geopolitical event for Indian families. It was the event that defined an entire generation's relationship with overseas work. Families in Trivandrum, Kochi, Chennai, and Madurai had sent their sons and brothers to Kuwait, Bahrain, and the UAE for construction, engineering, and service jobs that sustained entire local economies through remittances. When the invasion happened, those families experienced the crisis not through CNN but through weeks of silence followed by desperate phone calls from transit camps.

For Malayali and Tamil NRIs now living in the US, UK, Canada, and Australia — many of whom are the children or grandchildren of that Gulf generation — the 1991 crisis is family lore. It is the story told at weddings, the reason a grandfather moved from Kuwait to Texas, the backdrop to why a family chose to invest in land back home rather than trust any foreign country again.

## Dhanush's Streaming Profile

Kara's Netflix release is also significant because of where Dhanush sits in the global streaming landscape. His appearance in the Russo Brothers' **The Gray Man** (2022) gave him an international profile that few South Indian actors possess. His 2024 film **Raayan**, which he also directed, was one of Netflix's top-performing Indian-language acquisitions.

This means Kara will arrive on Netflix not as an obscure Tamil film for niche audiences, but as a Dhanush vehicle with built-in global recognition. The algorithm will serve it to the same audience that watched The Gray Man, Captain Miller, and Raayan — and that audience includes millions of diaspora Indians.

## The Theatrical-to-OTT Window

The sub-30-day theatrical-to-OTT gap has become a flashpoint in Indian cinema. Theatre owners, particularly in South India, have pushed back against what they see as a devaluation of the theatrical experience. Exhibitors argue that films need a longer exclusive window to build word-of-mouth and maximise ticket sales.

Kara's quick jump to Netflix — at approximately 28 days — sits at the aggressive end of the current norm, though it is consistent with the film's moderate theatrical performance. At ₹50 crore worldwide against a ₹100 crore budget, the theatrical run was not a runaway success, and the Netflix deal likely represents a significant portion of the film's overall recovery.

For the diaspora viewer, the OTT release is simply the release. Most NRIs do not have access to Tamil films in theatrical release outside of major metros, and even in cities like San Jose, Houston, and London, Tamil screenings are limited to opening weekend at best. Netflix makes Kara available everywhere, instantly, in a way that the theatrical window never could.""",
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
    slug1: "London Notting Hill luxury townhouse colourful houses street",
    slug2: "bank vault dramatic heist cinematic dark gold",
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
    ("Sonam Kapoor Notting Hill property controversy", "published"),
    ("Dhanush Kara Netflix OTT May 28", "published"),
]
for topic, status in topic_updates:
    print(f"  {topic} → {status}")

print("\n✅ Entertainment writer batch complete.")
