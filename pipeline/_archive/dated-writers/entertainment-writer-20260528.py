#!/usr/bin/env python3
"""
The Videshi – Entertainment Writer (2026-05-28 evening batch)
Publishes 3 fresh entertainment articles with proper image sourcing.
"""
import os, sys, json, uuid, re, time, urllib.parse
import requests
from datetime import datetime, timezone

# ── ENV ──────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = "TheVideshi/1.0 (thevideshi.com)"


# ── HELPERS ──────────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia REST API. Returns URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                "-H", f"Authorization: {PEXELS_KEY}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                src = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if src:
                    print(f"  ✓ Pexels image for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns HTTP 200 with image content-type and >5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ BANNED source: {url[:60]}")
        return False
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert row into Supabase table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None


def sb_patch(table, filters, payload):
    """Patch row in Supabase table."""
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
    return False


def publish_article(article):
    """Insert article and attach image."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article.get("sources", [])),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
    }

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
    return result


# ── ARTICLES ─────────────────────────────────────────────────────────────────

articles = []

# ────────────────────────────────────────────────────────────────────────────
# ARTICLE 1: Agar Tum Saath Ho hits 717M Spotify streams
# ────────────────────────────────────────────────────────────────────────────

art1 = {
    "headline": "A Song From 2015 Just Became the Most-Streamed Indian Track on Spotify. It Has 717 Million Plays.",
    "subheadline": "Arijit Singh and Alka Yagnik's 'Agar Tum Saath Ho' from Tamasha outlasted every Bollywood hit released since, including the entire Dhurandhar soundtrack.",
    "slug": "agar-tum-saath-ho-most-streamed-indian-song-spotify-717-million-tamasha-nri-20260528",
    "sources": ["Filmibeat", "Koimoi", "Spotify Charts"],
    "body": """In a music industry obsessed with first-week records and viral hooks, the most-streamed Indian song on Spotify is not from this year. It is not from last year. It is from a 2015 film that confused audiences when it first released, divided critics, and took years to find its true audience.

*Agar Tum Saath Ho* from Imtiaz Ali's *Tamasha* has crossed 717 million streams on Spotify, officially becoming the most-streamed Indian song on the platform. The track, composed by A.R. Rahman and sung by Arijit Singh and Alka Yagnik, has outlasted every Bollywood hit released in the decade since — including the recently chart-topping Dhurandhar soundtrack that put all 11 songs on Spotify's Global Top 200 simultaneously.

## Why This Matters for the Diaspora

For NRIs, *Agar Tum Saath Ho* is not just a song. It is a very specific emotional geography. It is the track that plays on headphones during long flights home, in shared playlists with friends who understand the particular ache of being far from the people you love, and at Indian weddings in New Jersey and Dallas and Scarborough where it has replaced older heartbreak anthems.

The song's streaming dominance tells a story that record labels have been slow to understand: Indian music's biggest global hits are not the ones that chart highest in week one. They are the ones that become emotional infrastructure — the songs people return to hundreds of times across years.

## The Numbers in Context

To put 717 million streams in perspective: the entire *Dhurandhar: The Revenge* album debuted at number two on Spotify's Global Top Albums chart and number five on the US Top Albums chart — a historic achievement for a Bollywood soundtrack. But the album got there through concentrated opening-week excitement across 11 tracks. *Agar Tum Saath Ho* got to 717 million as a single track, accumulating streams slowly and steadily over eleven years.

The song sits ahead of other Indian streaming giants like *Apna Bana Le* from *Bhediya* (695 million streams) and *Tujhe Kitna Chahne Lage* from *Kabir Singh* (680 million streams). In fifth place is *Shayad* from *Love Aaj Kal* with 555 million streams — another Imtiaz Ali film, another song that found its real audience long after the box office numbers were forgotten.

## The Tamasha Effect

When *Tamasha* released in November 2015, it earned roughly ₹138 crore worldwide — a solid but not spectacular number for a Ranbir Kapoor–Deepika Padukone film. Critics were split. The film's non-linear structure and its meditation on identity and performance felt indulgent to some, revelatory to others.

A decade later, *Tamasha* is among the most discussed and rewatched Hindi films of the 2010s, and its soundtrack — particularly *Agar Tum Saath Ho* and *Matargashti* — has achieved a cultural permanence that its box office run never predicted. Film schools reference it. Instagram reels use its dialogue as audio. First-generation Indian Americans cite it as the film that articulated something they could not.

Rahman composed the song with a restraint that is unusual for Bollywood heartbreak tracks. There is no dramatic orchestral crescendo. The melody stays close to conversational register, as if the singer is not performing heartbreak but simply living inside it. Alka Yagnik's voice, usually deployed for brighter, more ornate compositions, operates here with a quiet devastation that becomes more powerful on the fiftieth listen than the first.

## What This Means for Indian Music Globally

The milestone arrives at a moment when Indian music is breaking into global charts with increasing frequency. Dhurandhar's album on the US Billboard chart, Arijit Singh's sold-out arena tours across North America and Europe, and the growing presence of Indian songs on global Spotify playlists all point toward a tipping point.

But *Agar Tum Saath Ho* reaching 717 million streams offers a quieter, more significant lesson: the global Indian audience — particularly the 32 million-strong NRI diaspora — does not consume music the way the industry assumes. They are not chasing the newest release. They are building lifelong relationships with songs that articulate something specific about their emotional lives. The hits that matter most are the ones that never stop playing.""",
}

# Image for Article 1: AR Rahman (person article about his composition)
img1 = fetch_wikipedia_person_image("A. R. Rahman")
if not img1 or not validate_image_url(img1):
    img1 = fetch_wikipedia_person_image("Arijit Singh")
    if not img1 or not validate_image_url(img1):
        img1 = fetch_pexels_image("music headphones emotional", "Bollywood concert")
        if img1 and not validate_image_url(img1):
            img1 = None

art1["image_url"] = img1
art1["image_caption"] = "A.R. Rahman composed 'Agar Tum Saath Ho' with an unusual restraint that helped it become the most-streamed Indian song on Spotify"
art1["image_attribution"] = "Wikimedia Commons" if img1 and "wikimedia" in (img1 or "").lower() else "Pexels"
articles.append(art1)


# ────────────────────────────────────────────────────────────────────────────
# ARTICLE 2: Ananya Panday Bharatanatyam controversy in Chand Mera Dil
# ────────────────────────────────────────────────────────────────────────────

art2 = {
    "headline": "Ananya Panday Danced Bharatanatyam in a Bollywood Film. Classical Dancers Called It a Catastrophe. Her Father Said They Missed the Point.",
    "subheadline": "The 'Chand Mera Dil' dance sequence has reignited a debate the diaspora knows well: who gets to interpret Indian classical art forms, and who decides when interpretation becomes disrespect?",
    "slug": "ananya-panday-bharatanatyam-chand-mera-dil-controversy-classical-dance-nri-debate-20260528",
    "sources": ["Zoom TV Entertainment", "Bollywood Hungama", "LatestLY", "Bollywood Bubble"],
    "body": """The sequence lasts about three minutes. Ananya Panday, playing a college student in Dharma Productions' *Chand Mera Dil*, performs what the film's choreography team describes as a Bharatanatyam fusion — a dance that borrows the postures and hand gestures of the classical South Indian form but sets them to a contemporary soundtrack, in a contemporary setting, with contemporary movement vocabulary.

Within hours of the song's release, the internet delivered its verdict. Classical dancers called the choreography "catastrophic." Bharatanatyam practitioners with decades of training posted side-by-side videos showing the precise mudras and aramandi positions that the sequence got wrong. The hashtag #NotBharatanatyam trended.

Then Chunky Panday — Ananya's father, a veteran Bollywood actor — pushed back. "People completely misunderstood it," he told Bollywood Hungama. "It was never supposed to be a traditional Bharatanatyam recital. It was a fusion performance, an experimental cinematic interpretation. The choreography deliberately blended contemporary and classical elements."

Choreographer Sandip Soparrkar went further, calling the outrage "rubbish" and accusing classical dance gatekeepers of hypocrisy. "When Madhuri Dixit or Aishwarya Rai incorporate classical elements into Bollywood choreography, everyone celebrates. When a younger actress does it, suddenly it is an offence against the art form."

## The Diaspora Dimension

For NRIs, this debate is not abstract. It is lived experience.

Across the United States, Canada, and the United Kingdom, hundreds of thousands of Indian-origin children learn Bharatanatyam, Kathak, Kuchipudi, and other classical forms at weekend schools and private academies. Their parents — many of whom never learned these dances themselves — invest significant time and money because classical dance is one of the few tangible connections to an Indian identity that risks being diluted across generations.

When Bollywood borrows the visual vocabulary of these art forms without the technical rigour, it produces a complicated emotional response. The parents who drive their children to Saturday morning Bharatanatyam class see the same postures performed carelessly on a screen watched by millions. The children, caught between cultures, sometimes wonder why the version they spend years perfecting looks so different from the version their favourite actress performs.

## A History of Bollywood's Classical Borrowing

This is not new. Bollywood has been incorporating — and frequently misrepresenting — classical Indian dance forms since the industry's earliest decades. Vyjayanthimala brought authentic Bharatanatyam training to her performances. Waheeda Rehman's Kathak in *Guide* (1965) remains a benchmark. Hema Malini, Sridevi, and later Madhuri Dixit all brought varying degrees of classical training to their screen performances.

The difference, critics argue, is preparation. When Deepika Padukone performed a Ghoomar-inspired sequence in *Padmaavat*, she trained for months. When Hrithik Roshan incorporated Kathak elements into *Bajirao Mastani*, he worked with Kathak master Pandit Birju Maharaj. The standard being applied is not whether Bollywood can use classical dance, but whether it should use classical dance *carelessly*.

"The problem is not fusion," wrote one Bharatanatyam dancer in a viral Instagram post. "Fusion is beautiful when it comes from knowledge. The problem is appropriation disguised as fusion — borrowing the costume and the posture without understanding the grammar."

## The Box Office Does Not Care

Meanwhile, *Chand Mera Dil*'s box office tells its own story. After six days, the film has collected approximately ₹17-19 crore in India — making it one of the lowest career openings for Ananya Panday. The Bharatanatyam controversy, whether it helped or hurt the film's visibility, has not translated into ticket sales.

The film represents the broader struggle of Bollywood romance in 2026. In a year dominated by action spectacles and regional blockbusters, soft romantic dramas have struggled to find theatrical audiences. The genre's future may lie in streaming, where the target demographic — urban, English-educated, young — is more likely to discover it.

## Where This Leaves Us

The debate will continue because it has no clean resolution. Classical art forms are living traditions, not museum exhibits — they have always evolved through contact with contemporary culture. But that evolution historically happened through practitioners, not through film industries looking for visually striking sequences.

For the Indian diaspora, the stakes feel higher. Classical dance is not just art. It is identity maintenance. And when that maintenance collides with mainstream entertainment's casual treatment of the same forms, the resulting friction reveals something important about how Indian culture travels, who gets to interpret it, and what gets lost — or gained — in the translation.""",
}

# Image for Article 2: Ananya Panday
img2 = fetch_wikipedia_person_image("Ananya Panday")
if not img2 or not validate_image_url(img2):
    img2 = fetch_pexels_image("Bharatanatyam classical Indian dance", "Indian classical dancer")
    if img2 and not validate_image_url(img2):
        img2 = None

art2["image_url"] = img2
art2["image_caption"] = "Ananya Panday's Bharatanatyam-inspired sequence in 'Chand Mera Dil' has divided audiences and classical dance practitioners"
art2["image_attribution"] = "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "").lower() else "Pexels"
articles.append(art2)


# ────────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Bollywood romance is dying in 2026
# ────────────────────────────────────────────────────────────────────────────

art3 = {
    "headline": "Every Bollywood Romance Released in 2026 Has Underperformed. The Genre That Built the Industry Is Running Out of Theatres.",
    "subheadline": "From 'Chand Mera Dil' to 'Pati Patni Aur Woh Do', not a single romantic film has crossed ₹50 crore this year. For an industry built on love stories, the numbers are a crisis.",
    "slug": "bollywood-romance-genre-dying-2026-box-office-chand-mera-dil-streaming-shift-nri-20260528",
    "sources": ["Sacnilk", "Bollywood Hungama", "Pinkvilla", "Koimoi"],
    "body": """Here is a list of every Bollywood romantic film released in 2026, sorted by box office performance:

*Pati Patni Aur Woh Do* — ₹40 crore India net. *Tu Meri Main Tera Main Tera Tu Meri* — well under expectations. *Chand Mera Dil* — approximately ₹17 crore after six days, trending toward a lifetime total that will not recover its budget. *Ek Din* — a footnote.

Now here is the year's action-spectacle comparison: *Dhurandhar 2* alone has earned ₹1,150+ crore in India. *Bhooth Bangla* crossed ₹176 crore. Even regional action films like Tamil's *Karuppu* (₹163 crore) and Marathi's *Raja Shivaji* (₹93 crore) dwarf every romantic film Bollywood has produced this year.

The genre that defined Hindi cinema — the genre of *Dilwale Dulhania Le Jayenge*, *Jab We Met*, *Yeh Jawaani Hai Deewani* — cannot get audiences into theatres in 2026. The question is whether this is a temporary drought or a permanent structural shift.

## The Data Says Structural

The numbers are not ambiguous. In 2024, *Tu Jhoothi Main Makkaar* became the last Bollywood romance to genuinely overperform, earning ₹185 crore. But even that success obscured the trend: it worked because it had Ranbir Kapoor and Shraddha Kapoor, and because director Luv Ranjan built it as a comedy with romantic elements rather than a pure love story.

Since then, the pattern has been consistent. Romantic films open modestly, drop sharply on their first Monday, and lose screens to action blockbusters by their second weekend. *Chand Mera Dil*'s trajectory is textbook: a ₹4.3 crore opening day, a 47 percent drop by Monday, and weekday collections hovering around ₹2 crore — numbers that would have been considered a disaster for a Dharma-backed film five years ago.

For Ananya Panday, *Chand Mera Dil* represents the lowest career opening of any film she has headlined. Her previous films — *Liger* (₹15.95 crore opening), *Dream Girl 2* (₹10.69 crore), even *Kesari Chapter 2* (₹7.76 crore) — all opened significantly higher. The drop is not about her. It is about the genre.

## Where Did the Audience Go?

Three places, in roughly this order.

**First, streaming.** The audience for romantic dramas — urban, 18-35, educated, digitally native — is the exact demographic that streams most aggressively. They watch Korean dramas on Netflix. They binge Turkish romances on YouTube. They consume Indian romantic content on JioHotstar, where *Saiyaara* and *Jubilee* found massive audiences without ever needing a theatrical run. Paying ₹500 for a multiplex ticket to watch a romantic film you suspect will be on streaming in six weeks is a hard sell.

**Second, action spectacles.** The theatrical experience in 2026 has been redefined by films designed for big screens — the scale of *Dhurandhar 2*, the horror-comedy crowd experience of *Bhooth Bangla*, the visual spectacle of *Ramayana*'s trailer. Romantic films offer an intimate experience that streaming delivers equally well. Action films offer a collective, theatrical experience that streaming cannot replicate.

**Third, short-form content.** The NRI audience in particular consumes romantic content through Instagram Reels, YouTube Shorts, and TikTok. The emotional payload of a well-edited 60-second clip — the confession scene, the rain sequence, the airport goodbye — delivers the dopamine hit without the two-hour commitment. Bollywood love stories are being consumed in fragments, and those fragments do not require a movie ticket.

## The NRI Factor

For the Indian diaspora, the shift is pronounced. NRI audiences have historically been the most reliable theatrical audience for Bollywood romances — the *DDLJ* screenings at Maratha Mandir, the opening-weekend crowds at AMC and Cineplex theatres in North American suburbs.

But those audiences now have options. Korean romance on Netflix and Viki. Turkish dramas dubbed in Hindi. Anime romance with subtitles. The emotional need that Bollywood romance served — stories about love across distance, family expectations, and cultural identity — is now served by content from a dozen different industries.

## Can the Genre Survive?

The honest answer is that Bollywood romance will not die, but it will migrate. The future of the genre is streaming-first or streaming-only. Dharma Productions, which produced both *Chand Mera Dil* and the streaming success *Gehraiyaan*, likely already knows this.

The theatrical romantic hit is not impossible — it just requires a star combination and a marketing machine that makes the theatre experience feel like an event rather than a Wednesday evening option. Until Bollywood figures out that formula, every romantic film released in theatres will be competing not just against other films, but against the fundamental question of why this story requires a movie ticket at all.

The ₹17 crore six-day total for *Chand Mera Dil* is not just a box office number. It is an answer. And the industry has to decide what to do with it.""",
}

# Image for Article 3: Use Pexels for a thematic image
img3 = fetch_pexels_image("empty cinema theatre seats", "movie theater empty auditorium")
if img3 and not validate_image_url(img3):
    img3 = None

art3["image_url"] = img3
art3["image_caption"] = "Bollywood romantic films are struggling to fill seats in 2026, as audiences shift to streaming and action spectacles"
art3["image_attribution"] = "Pexels"
articles.append(art3)


# ── PUBLISH ──────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Publishing {len(articles)} entertainment articles...")
print(f"{'='*60}\n")

success_count = 0
for i, art in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {art['headline'][:70]}...")
    print(f"  Slug: {art['slug']}")
    print(f"  Image: {'YES' if art.get('image_url') else 'NO'}")
    word_count = len(art['body'].split())
    print(f"  Words: {word_count}")
    if word_count < 400:
        print(f"  ✗ SKIPPED: Body too short ({word_count} words, need 400+)")
        continue
    result = publish_article(art)
    if result:
        success_count += 1

print(f"\n{'='*60}")
print(f"Done. Published {success_count}/{len(articles)} articles.")
print(f"{'='*60}")
