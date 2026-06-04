#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 4, 2026"""

import json, os, sys, time, uuid, io, re
import requests
from datetime import datetime, timezone

# Load env
def load_env(filepath):
    if os.path.exists(filepath):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Fetch an image from Pexels using requests."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        raw_bytes = r.content
        if len(raw_bytes) < 5000:
            print(f"  ⚠ Image too small: {len(raw_bytes)} bytes")
            return None

        compressed = compress_image(raw_bytes)
        print(f"  📦 Compressed: {len(raw_bytes)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded to Supabase: {public_url[:60]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get("id")
        return True
    else:
        print(f"  ❌ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ============================================================================
# ARTICLE 1: Lagaan 25th Anniversary Re-Release
# ============================================================================
def write_lagaan_article():
    print("\n📝 Article 1: Lagaan 25th Anniversary Re-Release")

    slug = "lagaan-25th-anniversary-re-release-june-12-aamir-khan-theaters-nri-20260604"
    headline = "Lagaan Returns to Theaters for Three Days. Twenty-Five Years Later, the Film That Almost Bankrupted Aamir Khan Is India's Most Beloved Underdog Story."
    subheadline = "The Oscar-nominated cricket drama re-releases on June 12-14 with a new trailer and a poster design contest. For NRIs who grew up on this film, the timing could not be better."

    body = """Aamir Khan Productions has announced that Lagaan: Once Upon a Time in India will return to Indian cinemas for a special three-day theatrical run on June 12, 13, and 14, marking the film's 25th anniversary. A new trailer was released on June 3, and a creative campaign called #LagaanPosterChallenge has been launched, inviting fans to reimagine the film's iconic poster in their own style. Winners will receive an invitation to a special screening with the original cast and crew.

## The Film That Changed Everything

When Lagaan released on June 15, 2001, it was the most expensive Indian film ever made. Its budget had ballooned from ₹12 crore to ₹24 crore during production, and the entire financial risk sat on Aamir Khan's shoulders. The film's producer, the late Jhamu Sughand, never once questioned the cost overruns — a detail Khan has spoken about with deep gratitude in recent years. The gamble paid off. Lagaan became a cultural phenomenon, won eight Filmfare Awards, multiple National Film Awards, and earned India its third-ever Academy Award nomination for Best Foreign Language Film.

Directed by Ashutosh Gowariker, Lagaan is set in 1893 during British colonial rule. The residents of drought-hit Champaner are crushed under heavy taxation. When a British officer challenges them to a cricket match — win and the taxes are waived for three years, lose and they triple — a young villager named Bhuvan rallies his community to learn a game they have never played. The cast included Gracy Singh, Rachel Shelley, Paul Blackthorne, Kulbhushan Kharbanda, Raghubir Yadav, and Rajesh Vivek. The soundtrack by A.R. Rahman, featuring "Ghanan Ghanan," "Mitwa," "Radha Kaise Na Jale," and "O Rey Chhori," remains one of Hindi cinema's most beloved albums.

## Why This Matters for the Diaspora

For millions of NRIs, Lagaan was the first Indian film they felt they could proudly show to non-Indian friends and colleagues. Its underdog narrative, rooted in anti-colonial resistance and village unity, carried a universality that transcended language and geography. The Oscar nomination in 2002 was a watershed moment — Indian cinema was being seen, judged, and respected on the world's biggest stage. The film's cricket match, with its motley crew of villagers taking on the Empire, became a metaphor that resonated far beyond sport.

The re-release arrives at an interesting moment for Bollywood. Re-releases have become a significant revenue stream over the past two years, with films like Tumbbad, Rockstar, and Laila Majnu finding new life in theaters. For Lagaan, the calculus is different. This is not a cult film being rediscovered. This is a film that an entire generation already knows by heart, being given a chance to experience on the big screen for the first time — or the first time in a quarter century.

## The Poster Challenge

The #LagaanPosterChallenge is a smart piece of engagement. Fans are invited to reinterpret the film's original poster in any artistic style — illustration, photography, collage, or digital art. The contest is being run through Aamir Khan Productions' social channels. The best entries will be showcased, and select winners will be invited to a special anniversary screening alongside the original cast and crew. It is the kind of campaign that plays perfectly to the diaspora's deep emotional connection with the film and the visual creativity of a generation raised on both Bollywood and internet culture.

## What to Expect

The three-day window — Thursday through Saturday — is designed for event-style screenings rather than a traditional box office run. Exhibitors in major metros are expected to program the film in premium formats. Whether the re-release extends to international markets has not been confirmed, but given the film's iconic status among the Indian diaspora, demand from NRI audiences in the US, UK, and Canada is virtually guaranteed.

Twenty-five years ago, Lagaan asked a simple question: what happens when ordinary people refuse to accept the rules imposed on them? The answer, told through cricket and set to one of the greatest soundtracks ever composed for an Indian film, has not aged a day.

Sources: Bollywood Hungama, Filmfare, Aamir Khan Productions"""

    # Image sourcing
    print("  🔍 Searching for images...")
    candidates = []

    # Wikipedia: Aamir Khan
    wiki_img = fetch_wikipedia_person_image("Aamir Khan")
    if wiki_img:
        candidates.append({"url": wiki_img, "source": "wikipedia", "caption": "Aamir Khan, producer and star of Lagaan", "attribution": "Wikimedia Commons"})

    # Wikimedia Commons: Lagaan
    commons = fetch_wikimedia_commons_images("Lagaan film Aamir Khan cricket")
    if not commons:
        commons = fetch_wikimedia_commons_images("Aamir Khan actor")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "caption": "Aamir Khan at a public event", "attribution": "Wikimedia Commons"})

    # Pexels fallback
    pexels = fetch_pexels_image("village cricket India")
    if pexels:
        candidates.append({"url": pexels, "source": "pexels", "caption": "Village cricket in India", "attribution": "Pexels"})

    # Pick best
    img_url = None
    img_caption = "Aamir Khan, producer and star of Lagaan"
    img_attribution = "Wikimedia Commons"
    if candidates:
        best = candidates[0]  # Wikipedia > Commons > Pexels
        filename = f"{slug}.jpg"
        uploaded = upload_to_supabase(best["url"], filename)
        if uploaded:
            img_url = uploaded
            img_caption = best["caption"]
            img_attribution = best["attribution"]

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Bollywood Hungama", "Filmfare", "Aamir Khan Productions"]),
    }

    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")

    result = insert_article(article)
    if result:
        print(f"  ✅ Published: {headline[:60]}...")
    return result


# ============================================================================
# ARTICLE 2: Shilpa Shinde Admits False Harassment Case
# ============================================================================
def write_shilpa_shinde_article():
    print("\n📝 Article 2: Shilpa Shinde False Harassment Admission")

    slug = "shilpa-shinde-admits-false-sexual-harassment-case-bhabiji-ghar-par-hain-producer-nri-20260604"
    headline = "Shilpa Shinde Just Admitted Her Sexual Harassment Case Against a Producer Was False. The Fallout Has Been Immediate."
    subheadline = "The Bhabiji Ghar Par Hain actress confessed on a podcast that she filed a fabricated complaint against producer Sanjay Kohli a decade ago. Men's rights groups want her arrested. Others are asking harder questions."

    body = """Actress Shilpa Shinde, best known for her role in the long-running comedy Bhabiji Ghar Par Hain, has publicly admitted that the sexual harassment case she filed against the show's producer Sanjay Kohli in 2017 was false. The confession, made during a podcast appearance with Bharti Singh and Haarsh Limbachiyaa, has triggered immediate backlash — including demands from men's rights organizations for her arrest under laws governing false complaints.

## What She Said

Shinde's admission was remarkably candid. "Nobody knows this. I'm not afraid of telling the truth now," she said. "I filed a sexual harassment case against my producer because I had no other option. I eventually got out of that situation after reaching a settlement."

She explained the mechanics of how the complaint was constructed. "The police directly tell you that if you want an FIR registered, you have to write serious allegations. I come from a law background," she said. She also expressed regret over the damage done to Kohli's reputation: "Bechara woh usme badnaam hogaya" — the poor man ended up being defamed because of it.

The actress described the circumstances that led to her decision. She was in a contractual dispute with the show's producers, felt cornered professionally, and saw the harassment complaint as the only leverage available to her. "Mujhe tang kiya jaa raha tha," she told Zoom TV in a follow-up interview. "The entire industry was against me, while I stood alone."

## The Backlash

The response has been swift and polarizing. A men's rights NGO has publicly demanded Shinde's arrest, arguing that her confession constitutes an admission of filing a false FIR — a criminal offense under Indian law. "If false cases go unpunished, genuine victims suffer," the group stated, calling on producer Kohli to pursue legal action and seek compensation.

Television actress and columnist Pooja Bedi weighed in, saying the admission "validates what many people have always feared about the weaponization of harassment laws," while emphasizing that genuine victims suffer the most when such cases come to light.

## The Uncomfortable Middle Ground

Shinde's confession sits at the intersection of several uncomfortable realities. The first is that the legal system, as she describes it, incentivized escalation — she claims the police themselves guided her toward making the allegations more severe in order for an FIR to be registered. The second is that for a decade, an innocent producer carried the stigma of a sexual harassment accusation. The third is that every false case, by Shinde's own logic, makes it harder for women with legitimate complaints to be believed.

The timing is especially pointed. Her confession has arrived just days after Marathi actress Priya Bapat shared a detailed account of being harassed by a male co-star early in her career — a story that involves an actor repeatedly kissing her beyond what was agreed upon, messaging her relentlessly, and only backing off after her husband flew from Mumbai to the set in Bhopal to physically intervene. Bapat's account is the kind of experience that false cases actively undermine.

## What Happens Now

Shinde has said that her relationship with Kohli and the Bhabiji team has since been repaired, and she returned to the show after nearly a decade. "Our relationship is very good now," she said. Whether Kohli or the show's producers choose to pursue legal remedies remains to be seen.

For the Indian entertainment industry, the episode is a reminder that workplace protections and the abuse of those protections are not separate conversations — they are the same conversation. Strengthening one requires honestly confronting the other.

For NRIs watching from abroad, the story cuts particularly close. Many in the diaspora followed the original controversy in 2017 and formed opinions based on incomplete information. Shinde's confession does not undo the structural problems that make harassment common in the industry. But it does complicate the narrative — and in that complication, there may be an opportunity for more honest discourse about how India's entertainment workplace actually functions.

Sources: Bollywood Hungama, MensXP, India Forums, Zoom TV, Bollywood Bubble"""

    # Image sourcing
    print("  🔍 Searching for images...")
    candidates = []

    # Wikipedia: Shilpa Shinde
    wiki_img = fetch_wikipedia_person_image("Shilpa Shinde")
    if wiki_img:
        candidates.append({"url": wiki_img, "source": "wikipedia", "caption": "Shilpa Shinde, actress known for Bhabiji Ghar Par Hain", "attribution": "Wikimedia Commons"})

    # Wikimedia Commons
    commons = fetch_wikimedia_commons_images("Shilpa Shinde actress")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "caption": "Shilpa Shinde at a public event", "attribution": "Wikimedia Commons"})

    if not candidates:
        commons = fetch_wikimedia_commons_images("Bhabiji Ghar Par Hain")
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "caption": "Scene from Bhabiji Ghar Par Hain", "attribution": "Wikimedia Commons"})

    # Pexels fallback
    if not candidates:
        pexels = fetch_pexels_image("Indian television studio microphone")
        if pexels:
            candidates.append({"url": pexels, "source": "pexels", "caption": "A television studio setting", "attribution": "Pexels"})

    # Pick best
    img_url = None
    img_caption = "Shilpa Shinde, actress known for Bhabiji Ghar Par Hain"
    img_attribution = "Wikimedia Commons"
    if candidates:
        best = candidates[0]
        filename = f"{slug}.jpg"
        uploaded = upload_to_supabase(best["url"], filename)
        if uploaded:
            img_url = uploaded
            img_caption = best["caption"]
            img_attribution = best["attribution"]

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Bollywood Hungama", "MensXP", "India Forums", "Zoom TV", "Bollywood Bubble"]),
    }

    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")

    result = insert_article(article)
    if result:
        print(f"  ✅ Published: {headline[:60]}...")
    return result


# ============================================================================
# ARTICLE 3: Priya Bapat Harassment Revelation
# ============================================================================
def write_priya_bapat_article():
    print("\n📝 Article 3: Priya Bapat Workplace Harassment Revelation")

    slug = "priya-bapat-co-star-harassment-kissing-scene-husband-flew-set-bhopal-nri-20260604"
    headline = "Priya Bapat Said Her Co-Star Kept Kissing Her Beyond What the Script Required. Her Husband Flew to the Set to Make It Stop."
    subheadline = "The Marathi actress's detailed account of on-set harassment — improvised physical contact, persistent messaging, and the intervention that finally drew a line — is sparking a necessary conversation about boundaries in Indian film."

    body = """Marathi actress Priya Bapat has shared a detailed and deeply personal account of being harassed by a male co-star during the early days of her career. In a recent interview that has since gone viral, Bapat described an experience that began with unwanted physical contact during a scene and escalated into persistent off-set advances — one that was only resolved when her husband, actor Umesh Kamat, flew from Mumbai to the shoot location in Bhopal to intervene.

## What Happened on Set

Bapat explained that the film required a single kissing scene, which she had agreed to after discussion. The problems began during rehearsals and the shoot itself. "There were moments where the actor kept improvising in the song. And he kept kissing me," she recounted. "I didn't take a stand for myself at that point of time. Because I didn't know how to deal with this."

The situation did not remain confined to the set. The actor and Bapat were staying at the same hotel, and he began messaging her repeatedly. "He kept messaging me and asking me to come. 'Let me teach you how to swim.' 'Let's go out for dinner.' 'Can I meet you for breakfast?'" she recalled. "I said, I don't want any of this. This has never happened in my life before. And it shouldn't happen ever again."

## The Intervention

Bapat said she would call Kamat every night from Bhopal to describe what she was experiencing. Eventually, without being asked, he booked a flight and arrived on set. "He just came on the set. And he stayed with me for three days. Just so that the actor gets some understanding. And he kind of backs off. And he kind of understands the boundaries."

The approach worked. The co-star's behavior changed after Kamat's presence. Bapat noted that this remains the only such experience in her acting career. She did not name the actor involved.

## Why This Account Is Different

Most conversations about harassment in Indian entertainment have centered on Bollywood's biggest names and the most egregious cases — the kind that make national headlines and trigger industry-wide upheaval. Bapat's account describes something more insidious: the kind of boundary violation that happens quietly, in the gray zone between what was agreed upon and what was actually done, on sets where the power dynamics are not extreme enough to make someone walk away, but uncomfortable enough to leave a lasting mark.

Her description of not knowing how to respond in the moment is especially telling. Bapat is an accomplished actress with a strong body of work in both Marathi and Hindi industries. She appeared in Munna Bhai MBBS, Lage Raho Munna Bhai, and multiple acclaimed Marathi films. If someone of her stature felt paralyzed in the moment, the experience of younger, less established actresses can only be imagined.

## The Diaspora Connection

For NRIs, conversations about workplace culture in India often feel distant — abstractions filtered through headlines. Bapat's account is concrete, specific, and uncomfortably relatable to anyone who has navigated a professional environment where informal power structures override formal protections.

The timing of her revelation is notable. It arrives alongside Shilpa Shinde's admission that she filed a false harassment case against a producer, creating a juxtaposition that the Indian entertainment industry has long struggled to hold simultaneously — that harassment is real, pervasive, and destructive, and that the mechanisms meant to address it can also be misused. Both truths exist. Both demand attention.

## What It Means

Bapat's account is not a call for industry-wide reform or a legal complaint. It is a personal testimony shared with clarity and restraint. The fact that her resolution came not from an industry body or a legal process, but from her husband showing up on set to physically signal that boundaries existed, says something about the gap between the protections that should exist in Indian film production and the ones that actually do.

The response on social media has been largely supportive, with many pointing out the courage it takes to speak about these experiences even without naming the person involved. The conversation it has sparked — about consent, improvisation, and the line between creative collaboration and personal violation — is one that Indian cinema has needed to have for a long time.

Sources: Bollywood Hungama, Inshorts, Filmfare"""

    # Image sourcing
    print("  🔍 Searching for images...")
    candidates = []

    # Wikipedia: Priya Bapat
    wiki_img = fetch_wikipedia_person_image("Priya Bapat")
    if wiki_img:
        candidates.append({"url": wiki_img, "source": "wikipedia", "caption": "Priya Bapat, Marathi and Hindi film actress", "attribution": "Wikimedia Commons"})

    # Wikimedia Commons
    commons = fetch_wikimedia_commons_images("Priya Bapat actress Marathi")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "caption": "Priya Bapat at a public event", "attribution": "Wikimedia Commons"})

    if not candidates:
        commons = fetch_wikimedia_commons_images("Marathi film actress")
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "caption": "Indian film industry event", "attribution": "Wikimedia Commons"})

    # Pexels fallback
    if not candidates:
        pexels = fetch_pexels_image("film set clapperboard cinema India")
        if pexels:
            candidates.append({"url": pexels, "source": "pexels", "caption": "A film production set", "attribution": "Pexels"})

    # Pick best
    img_url = None
    img_caption = "Priya Bapat, Marathi and Hindi film actress"
    img_attribution = "Wikimedia Commons"
    if candidates:
        best = candidates[0]
        filename = f"{slug}.jpg"
        uploaded = upload_to_supabase(best["url"], filename)
        if uploaded:
            img_url = uploaded
            img_caption = best["caption"]
            img_attribution = best["attribution"]

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Bollywood Hungama", "Inshorts", "Filmfare"]),
    }

    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")

    result = insert_article(article)
    if result:
        print(f"  ✅ Published: {headline[:60]}...")
    return result


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("THE VIDESHI — Entertainment Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []
    results.append(("Lagaan 25th Anniversary", write_lagaan_article()))
    results.append(("Shilpa Shinde", write_shilpa_shinde_article()))
    results.append(("Priya Bapat", write_priya_bapat_article()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    for name, r in results:
        status = "✅" if r else "❌"
        print(f"  {status} {name}")
    print("=" * 60)
