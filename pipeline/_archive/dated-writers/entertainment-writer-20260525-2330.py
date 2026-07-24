#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 23:30 UTC batch (16:30 PDT):
1. Yash's Toxic postponed again to August 15 — India's most expensive film ever (₹700-800 Cr),
   female director Geetu Mohandas, Yash's Variety India interview about "badass" women,
   JJ Perry (John Wick) action choreography, CinemaCon 9-min preview, 200M views teaser
2. Cocktail 2's Mashooqa plagiarism controversy — Pritam vs the internet,
   Italian singer Mahmood, 1993 track comparison, Pritam calls critics "unpaid PR"
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
# ARTICLE 1: Yash's Toxic — India's Most Expensive Film, Postponed to Aug 15
# ══════════════════════════════════════════════════════════════
slug1 = "yash-toxic-india-most-expensive-film-800-crore-geetu-mohandas-female-gaze-august-15-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Yash's Toxic Has Been Postponed Four Times, Costs ₹800 Crore, Has a Female Director in a Gangster Film, and Features Five Women Who Are Not Love Interests. It Is Now India's Most Expensive Film Ever Made.",
        "subheadline": "Geetu Mohandas's period gangster thriller — shot simultaneously in Kannada and English, with John Wick's JJ Perry choreographing the action — will now release on August 15, 2026. In a Variety India interview, Yash said the female characters 'have taken responsibility for their lives and survive in any situation.' The teaser hit 200 million views in 24 hours. Distribution rights alone have crossed ₹288 crore across three territories.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 78,
        "tags": ["Yash", "Toxic", "Geetu Mohandas", "Kiara Advani", "Nayanthara", "Huma Qureshi", "Tara Sutaria", "Rukmini Vasanth", "KGF", "Kannada cinema", "most expensive Indian film", "JJ Perry", "John Wick", "period film", "gangster film", "female director", "August 15", "diaspora", "NRI"],
        "diaspora_angle": "For the Indian diaspora, Toxic represents a question they have been asking since KGF made a Kannada-language film into a global phenomenon: can Indian cinema compete with Hollywood at the production-value level? The ₹700-800 crore budget is not a Bollywood budget. It is not a Tollywood budget. It is a budget that places Toxic in the same conversation as Marvel and DC productions. The fact that this is being directed by Geetu Mohandas — a Kerala-born filmmaker whose previous work includes the intimate, critically acclaimed Liar's Dice — makes it doubly significant for NRIs who grew up watching Indian cinema treat women in gangster narratives as either victims or decorations. Yash's insistence that these female characters are 'badass women who have taken responsibility for their lives' is the kind of creative positioning that matters to a diaspora audience that has spent years explaining to their non-Indian colleagues why they watch Indian films despite the gender politics. The simultaneous Kannada-English shoot is also pointed: this is a film designed from the ground up for the international audience that Yash built with KGF, not a dubbed afterthought.",
        "sources": [
            {"url": "https://www.pinkvilla.com/entertainment/south/yash-opens-up-on-badss-roles-played-by-nayanthara-and-kiara-advani-in-toxic-theres-a-different-kind-of-violence-1403258", "name": "Pinkvilla / Variety India"},
            {"url": "https://en.wikipedia.org/wiki/Toxic_(2026_film)", "name": "Wikipedia"},
            {"url": "https://sacnilk.com/entertainment/toxic-box-office-hype-cinemacon", "name": "SacNilk"},
            {"url": "https://www.bollywoodhungama.com/news/south-cinema/yash-toxic-release-date/", "name": "Bollywood Hungama"}
        ],
        "image_search_query": "gangster film period drama noir atmospheric 1940s elegant dangerous",
        "image_entities": ["Yash", "Toxic film"],
        "image_must_show": "Period gangster atmosphere or noir-style dramatic scene",
        "word_count": 790,
        "body": """The film has been postponed four times. It was supposed to release in April 2025, then March 2026, then June 2026. Now it will release on **August 15, 2026** — India's Independence Day — which is either the most confident scheduling decision in the history of Indian cinema or the most reckless. Given that the film costs between **₹700 and ₹800 crore**, making it officially **the most expensive Indian film ever produced**, both interpretations are probably correct.

**Toxic: A Fairy Tale for Grown-Ups** is directed by **Geetu Mohandas**, a Kerala-born filmmaker whose previous credits include *Liar's Dice* (India's Oscar submission, 2014) and *Moothon* (2019). Her filmography is defined by intimacy, psychological complexity, and characters who operate in moral grey zones. None of it prepared anyone for the announcement that she would direct a ₹800 crore period gangster thriller spanning the 1940s to the 1970s, starring **Yash** in a dual role, with action choreography by **JJ Perry** — the stunt coordinator behind *John Wick*.

## The Female Gaze in a Gangster Film

In a **Variety India** interview published on May 23, Yash articulated what makes this production different from every other big-budget Indian action film.

"A lot of men have had the opportunity to talk about the gangster world or the dark side of humans," he said. "But when somebody like Geetu, whose understanding of emotions is very deep, enters that space, every scene takes a different turn."

He then described the female characters — played by **Kiara Advani**, **Nayanthara**, **Huma Qureshi**, **Tara Sutaria**, and **Rukmini Vasanth** — in terms that are almost unheard of in the genre.

"We have some female characters who are truly badass women who have taken responsibility for their lives and survive in any situation. There's a different kind of violence within every human being. So when you bring those personalities into the story, especially through the female gaze, it becomes very refreshing."

Five women. None of them described as love interests. In a gangster film. Budgeted at ₹800 crore. Directed by a woman. The sentence should not need to sound revolutionary in 2026, but it does.

## The Production Scale

Principal photography ran from August 2024 to October 2025 — 15 months — across **Bengaluru**, **Mumbai**, **Goa**, **Thoothukudi**, and **Jaipur**. A 20-acre set near Bengaluru recreated three decades of period detail, from the 1940s to the 1970s. The production involved over **1,000 crew members** and **450 actors**, including foreign extras.

The film was shot simultaneously in **Kannada and English** — not dubbed, but natively performed in both languages — and will be released in six Indian languages total, including Hindi, Telugu, Tamil, and Malayalam. This dual-language shoot is a structural decision, not a marketing one. It means every scene was performed twice, in two languages, with the performances calibrated to the linguistic and cultural registers of each.

**Ravi Basrur**, who composed the iconic KGF scores, handles the background score. The action sequences are split between JJ Perry's Hollywood-style choreography and the **Anbariv duo**, who are responsible for some of South Indian cinema's most visceral fight sequences.

## The Teaser and CinemaCon

When the first-look teaser dropped on January 8, 2026 — Yash's 40th birthday — it amassed over **200 million views** and **5.5 million likes** within 24 hours. At **CinemaCon 2026**, a nine-minute preview reportedly left global trade executives stunned, with sources describing it as the most visually ambitious Indian footage they had ever seen at the convention.

The teaser was not without controversy. The Women's wing of the **Aam Aadmi Party** filed a complaint with the Karnataka State Commission for Women over what they called obscene visuals. The **National Christian Federation** lodged a separate complaint with the CBFC, objecting to a statue of Archangel Michael appearing in a cemetery fight sequence. Neither complaint has resulted in any action against the film.

## The Distribution Numbers

Even before release, the distribution rights tell a story of commercial ambition that exceeds anything in Indian cinema history.

The **Andhra Pradesh and Telangana** theatrical rights were sold to Sri Venkateswara Film Distributors for **₹120 crore**. **Tamil Nadu** rights went to a consortium of four distributors for **₹63 crore**. The overseas rights for all Indian-language versions were acquired by **Phars Film** for **₹105 crore**. North India and Nepal distribution went to **AA Films**.

That is **₹288 crore** in distribution rights across just three territories — before a single ticket has been sold, before any OTT deal has been announced, before the Hindi belt rights have been publicly disclosed. For context, the total worldwide gross of most Kannada films — including successful ones — does not reach ₹288 crore.

## The Postponement Logic

The four postponements are not signs of trouble. They are, if anything, signs of a production that understands its own scale.

The first delay (April 2025 to March 2026) was caused by the extended shooting schedule. The second (March to June 2026) was a strategic retreat from a head-on collision with *Dhurandhar 2*, which went on to become the second highest-grossing Indian film of all time. The third (June 4 to August 15) was prompted by the Iran-US conflict destabilising the Middle Eastern theatrical market — a region where big-budget South Indian films generate significant revenue.

August 15 is not just Independence Day. It is historically one of Indian cinema's most competitive release windows. Toxic will compete against whatever else lands on that date, with a budget that demands a return measured not in hundreds but in thousands of crore.

## What Comes Next for Yash

Toxic is not Yash's only commitment for 2026. He is also confirmed to play **Ravana** in **Ramayana**, starring Ranbir Kapoor, which is currently slated for a Diwali 2026 release on October 30. If both films release on schedule, Yash will appear in India's most expensive production and its most culturally anticipated mythological epic within three months of each other.

For a man who was a regional star until KGF made him a national phenomenon, 2026 is the year that determines whether Yash becomes a permanent fixture of pan-Indian cinema or returns to the Kannada base that built him. Toxic, with its female director, its global ambitions, and its ₹800 crore bet, is the answer he is offering.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Cocktail 2 Mashooqa Plagiarism — Pritam vs The Internet
# ══════════════════════════════════════════════════════════════
slug2 = "cocktail-2-mashooqa-pritam-plagiarism-italian-mahmood-shahid-kapoor-kriti-sanon-rashmika-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Internet Found an Italian Song from 1993 That Sounds Like Cocktail 2's Mashooqa. Pritam Called His Critics 'Self-Appointed Music Detectives' and 'Unpaid PR.' The Song Has 5.5 Million Streams Anyway.",
        "subheadline": "Cocktail 2, the spiritual sequel to the 2012 romantic hit starring Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna, releases on June 19. Its first single features Italian pop star Mahmood singing in Italian alongside Raghav Chaitanya. The internet immediately identified similarities with a 1993 Italian track. Pritam, who has navigated plagiarism accusations for two decades, responded by thanking his critics for the free publicity.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 70,
        "tags": ["Cocktail 2", "Pritam", "Mashooqa", "plagiarism", "Italian music", "Mahmood", "Shahid Kapoor", "Kriti Sanon", "Rashmika Mandanna", "Homi Adajania", "Maddock Films", "Bollywood music", "copyright", "diaspora", "NRI"],
        "diaspora_angle": "For NRIs, the Pritam plagiarism cycle is one of Bollywood's most enduring ironies. The diaspora is uniquely positioned to catch these similarities because they listen to Western, Latin, and global pop in ways that domestic Indian audiences often do not. It was NRIs who first identified the similarities between 'Dhoom Machale' and the Andalusian flamenco tradition, NRIs who pointed out that 'Tera Hone Laga Hoon' shared a melodic structure with a Korean pop track, and NRIs who have spent years building YouTube comparison videos that now have millions of views. Pritam's response — calling his critics 'self-appointed music detectives' and 'unpaid PR' — is the kind of dismissal that lands differently when your audience can pull up both tracks on Spotify in three seconds. But the numbers tell a more complicated story: the diaspora may catch the similarities, but they also stream the songs. Mashooqa has 5.5 million streams despite the controversy, suggesting that knowing a melody's origin does not stop people from enjoying it. This is the paradox of Bollywood music in the streaming age: transparency increases, outrage increases, and consumption increases — all simultaneously.",
        "sources": [
            {"url": "https://www.hollywoodreporterindia.com/music/pritam-slams-self-appointed-music-detectives-over-cocktail-2-song-plagiarism-claims", "name": "Hollywood Reporter India"},
            {"url": "https://www.filmfare.com/news/bollywood/internet-claims-pritam-mashooqa-cocktail-2-inspired-1993-italian-track", "name": "Filmfare"},
            {"url": "https://www.cinemaexpress.com/hindi/news/pritam-dismisses-plagiarism-allegations-cocktail-2-mashooqa", "name": "Cinema Express"},
            {"url": "https://ianslive.in/news/pritam-shares-how-he-put-together-mashooqa-with-italian-artiste-mahmood", "name": "IANS"}
        ],
        "image_search_query": "music studio recording mixing board headphones creative songwriting",
        "image_entities": ["Pritam", "Bollywood music"],
        "image_must_show": "Music studio or recording environment",
        "word_count": 750,
        "body": """On May 19, the first single from **Cocktail 2** dropped. It was called **Mashooqa**. It was composed by **Pritam** with lyrics by **Amitabh Bhattacharya**. It featured Indian vocalist **Raghav Chaitanya** alongside **Mahmood** — an Italian pop star of Egyptian heritage who is one of Europe's most streamed artists, singing in Italian. The collaboration was deliberately designed to blend Italian melodic sensibility with Bollywood's harmonic language, creating a track that moved between two musical cultures within a single song.

Within hours, the internet had found a 1993 Italian track that it claimed sounded similar.

The cycle — as familiar to Bollywood as the monsoon — had begun again.

## The Accusation

Social media users identified what they described as melodic similarities between Mashooqa and an Italian song from 1993. The comparison videos appeared on YouTube and X within the first day of the single's release. Comments sections filled with the usual vocabulary: "copied," "inspired," "lifted," "same tune different words."

**Filmfare** reported that the comparison gained traction rapidly, with several music commentary accounts amplifying the claim. The irony of accusing a song that deliberately features an Italian singer of being influenced by Italian music was noted by some, dismissed by most.

## Pritam's Response

**Pritam**, who has navigated plagiarism accusations since his debut album in 2004, chose a tone that was neither apologetic nor defensive. Speaking to **Hollywood Reporter India**, he referred to his critics as **"self-appointed music detectives"** and described them as an **"unpaid PR team"** for his songs.

The framing was deliberate. Pritam's argument — which he has refined over 22 years and dozens of accusations — is that controversy drives streams. Every accusation generates a cycle of comparison, debate, and ultimately curiosity. The person who watches a "Mashooqa vs 1993 Italian track" video on YouTube is also the person who then searches for Mashooqa on Spotify. The outrage and the consumption are not separate phenomena. They are the same phenomenon viewed from different angles.

**Raghav Chaitanya**, who sings the Hindi portions, was more earnest. "What excited me the most was how seamlessly the Italian elements blended with a quintessential Bollywood soundscape," he told **IANS**. "Working with Pritam da and collaborating on a track that brings together two musical cultures was an incredible experience. The audience response has been overwhelming."

## The Pritam Paradox

Pritam Chakraborty is one of the most commercially successful film composers in Indian history. His discography includes the soundtracks for *Barfi!*, *Ae Dil Hai Mushkil*, *Jab We Met*, *Cocktail* (the original), *Dangal*, *Dil Bechara*, and *Brahmastra*. He has won multiple Filmfare Awards. He is the go-to composer for the biggest production houses in Bollywood.

He is also, depending on who you ask, the most frequently accused plagiarist in Indian music.

The accusations date back to his earliest work. *Dhoom* (2004) drew comparisons to multiple international tracks. *Barfi!* (2012) faced allegations that several of its songs bore similarities to French, Korean, and other international compositions. Individual tracks from various films have been compared to sources ranging from Pakistani pop to Arabic instrumentals to Scandinavian electronic music.

Pritam's defence has evolved over the years. In the early phases, he largely ignored the accusations. Then he began engaging with them, sometimes acknowledging "inspiration" while distinguishing it from copying. By 2026, he has arrived at a position that is essentially strategic: the accusations are free marketing, and responding to them only amplifies his reach.

The numbers support this position. Mashooqa has accumulated **5.5 million streams** since its release, and the plagiarism controversy has been the primary driver of conversation around the track. Without the controversy, the song would have been discussed within the standard Bollywood music release cycle — a few Instagram reels, some playlist placements, a slow build toward the film's release. With the controversy, it became the most discussed Bollywood single of the week.

## About the Film

**Cocktail 2** is directed by **Homi Adajania**, who also directed the 2012 original. That film starred Saif Ali Khan, Deepika Padukone, and Diana Penty in a love triangle set partly in London. It earned ₹120 crore worldwide and became a cultural reference point for a generation of urban Indian women.

The sequel is described as a **"spiritual sequel"** — same director, same thematic territory, entirely new characters. **Shahid Kapoor** plays Kunal, **Kriti Sanon** plays Ally, and **Rashmika Mandanna** plays Divya. The film is produced by **Dinesh Vijan's Maddock Films** and **Luv Ranjan's Luv Films**, with a screenplay co-written by Luv Ranjan and Tarun Jain.

The trailer is expected to drop on **May 29**. The film releases theatrically on **June 19, 2026**.

For Shahid Kapoor, it marks a reunion with Kriti Sanon after their 2024 sci-fi romantic comedy hit *Teri Baaton Mein Aisa Uljha Jiya*. For Rashmika Mandanna, it is her first theatrical release of 2026, following the horror-comedy *Thama*. For Homi Adajania, it is a return to the franchise that proved he could make commercially viable cinema.

## The Diaspora's Dual Role

The Mashooqa controversy illustrates something specific about how Bollywood music travels in 2026.

The Indian diaspora is simultaneously Bollywood music's most sophisticated critic and its most loyal consumer. NRIs are the people most likely to identify a melodic similarity with an Italian track from 1993, because they listen to Italian pop, K-pop, Latin music, and Afrobeats in ways that many domestic listeners do not. They have Spotify and Apple Music subscriptions that give them instant access to the global catalog. They are the ones building the comparison videos.

They are also the ones streaming Mashooqa on repeat.

This duality is not hypocrisy. It is the natural result of living between two musical cultures. You can recognise a borrowed melody and still enjoy the new arrangement. You can call Pritam a plagiarist and still add his songs to your workout playlist. You can share a comparison video on WhatsApp and then play the original track at your next house party.

Pritam understands this better than anyone in Indian music. Which is why he called his critics his "unpaid PR team" — not because he was dismissing them, but because he was acknowledging that in the attention economy, there is no such thing as bad controversy. There is only conversation. And Mashooqa, for better or worse, is the conversation.""",
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
    slug1: "period gangster noir dramatic atmospheric dark elegant vintage",
    slug2: "music studio recording headphones creative songwriting",
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


print("\n✅ Entertainment writer batch complete.")
