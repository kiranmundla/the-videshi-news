#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 batch."""

import json, os, time, re, uuid, sys
from datetime import datetime, timezone
import requests, urllib.parse

# ---------- ENV ----------
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ---------- IMAGE SOURCING ----------
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels with specific search terms."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p["src"]["large2x"]
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate image URL returns 200 with image content type and reasonable size."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            return True
        print(f"  ⚠ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert into Supabase, return response data."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    print(f"  ⚠ Insert error ({r.status_code}): {r.text[:200]}")
    return None


def sb_patch(table, match, payload):
    """Patch a Supabase row."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ⚠ Patch error ({r.status_code}): {r.text[:200]}")
    return False


# ---------- ARTICLES ----------
articles = [
    # Article 1: Kaala Hiran — Salman Khan's Blackbuck Case
    {
        "headline": "Salman Khan's 1998 Blackbuck Case Is Now a Film. It's Called Kaala Hiran, and It Covers Everything.",
        "subheadline": "Producer Amit Jani's crime drama revisits the Jodhpur hunt, the courtroom fallout, and the Salman-Lawrence Bishnoi feud that followed.",
        "slug": "kaala-hiran-salman-khan-blackbuck-case-lawrence-bishnoi-film-nri-20260531",
        "category": "entertainment",
        "image_person": "Salman Khan",
        "image_pexels_query": None,
        "sources_text": "IANS, Filmfare, India Forums",
        "body": """One of Bollywood's longest-running controversies is getting the cinematic treatment. Producer Amit Jani's Jani Firefox Media has officially announced *Kaala Hiran: The Battle for Legacy*, a crime drama inspired by Salman Khan's infamous 1998 blackbuck poaching case — and, crucially, the violent feud with gangster Lawrence Bishnoi that grew out of it.

The first-look poster dropped on X this week, with a teaser confirmed for June 20, 2026. Bharat S. Shrinate is directing.

## What the Film Covers

Jani confirmed to IANS that the film recreates the hunting of blackbucks in Kakani village near Jodhpur during the shooting of *Hum Saath-Saath Hain* in October 1998. It covers the arrest, the courtroom drama, the sentencing, and the broader rivalry between Khan and the Bishnoi community that has defined headlines for over two decades.

"Audiences have waited a long time for a cinematic story around Salman Khan, Lawrence Bishnoi, and the case of deer hunting," Jani said. The shoot has been completed across Sambhal, Moradabad, and other locations in Uttar Pradesh. Cast details remain under wraps — we still don't know who's playing Salman.

## Why the Bishnoi Community Cares

The Bishnoi community considers blackbucks sacred, viewing them as a reincarnation of their spiritual guru. What began as a poaching case escalated into a generational vendetta. Salman Khan was convicted by a Jodhpur court in 2018 and sentenced to five years in prison, though he was granted bail. Co-accused actors including Saif Ali Khan, Tabu, Sonali Bendre, and Neelam were acquitted.

The feud's most violent chapter came in October 2024, when politician Baba Siddique — a close associate of Khan — was shot dead outside his Mumbai residence. Lawrence Bishnoi's gang claimed responsibility, framing it as revenge for the blackbuck killing.

## The Diaspora Angle

For NRIs, the Salman-Bishnoi saga has been impossible to ignore. It surfaces every few months — in courtroom developments, in security bulletins, in the celebrity gossip cycle. A film that dramatizes the entire arc, from the hunt to the ongoing threats, taps directly into a story the diaspora has followed for nearly three decades.

Jani's previous production, *Udaipur Files*, stirred controversy but struggled at the box office. *Kaala Hiran* arrives with a built-in audience that has strong opinions about every character involved. The teaser on June 20 will be the first real test of whether this retelling has the gravity the subject demands.

**What to watch for:** The cast reveal — whoever plays Salman Khan will inherit one of the most scrutinized roles in recent Hindi cinema.""",
    },

    # Article 2: Manoj Bajpayee as RBI Governor
    {
        "headline": "Manoj Bajpayee Plays the RBI Governor Who Kept India From Going Bankrupt. Governor Opens June 12.",
        "subheadline": "The film is inspired by S. Venkitaramanan, the real RBI Governor during India's 1991 economic crisis. Bajpayee says he was 'scared and nervous' about the Tamil diction.",
        "slug": "manoj-bajpayee-governor-rbi-1991-economic-crisis-film-june-12-nri-20260531",
        "category": "entertainment",
        "image_person": "Manoj Bajpayee",
        "image_pexels_query": None,
        "sources_text": "IANS, Bollywood Hungama, The Freedom Press",
        "body": """Manoj Bajpayee's next film puts him in the kind of role he was born to play — understated, institutional, and loaded with the weight of national consequence. In *Governor*, releasing June 12, he plays the Reserve Bank of India chief who navigated the country through its worst economic crisis.

The character is inspired by S. Venkitaramanan, the real-life RBI Governor during India's 1991 balance-of-payments catastrophe — the year India nearly went bankrupt, pledged its gold reserves to the Bank of England, and was forced into the liberalization that transformed its economy.

## The Diction Challenge

At the trailer launch in Mumbai, Bajpayee was disarmingly honest about the difficulty of the role. His character comes from Tamil culture, and the actor — a native of Bihar — admitted he was "scared and nervous" about getting the linguistic texture right.

"I don't like to go wrong with language and diction," he told IANS. "I am from Bihar. So I know how much I get offended when language is wrongly spoken. It is better to go to the minimum. You need to play up the essence of that language, but you are not supposed to be completely indulgent about the accent because it will take away the attention from the matter."

He drew parallels to his earlier work in *Satya* and *Aligarh*, where he inhabited characters from the same cultural region but deployed completely different speech patterns based on their social standing and education. This kind of micro-calibration — playing a Tamil Brahmin bureaucrat in Hindi without veering into caricature — is the high-wire act that separates Bajpayee from most of his contemporaries.

## What Makes This Relevant for the Diaspora

The 1991 crisis is foundational mythology for every Indian who lived through it — and for the NRI generation that grew up hearing about it. The moment when India's foreign exchange reserves dropped to barely enough to cover two weeks of imports. The humiliating airlift of gold to London. The political crisis that brought P.V. Narasimha Rao to power and Manmohan Singh to the finance ministry.

For the diaspora, this isn't ancient history — it's the inflection point that created the India they left, or the India that made their careers possible. Economic liberalization opened the doors to the IT boom, the outsourcing revolution, and the middle-class migration wave that built Indian communities across the US, UK, and Canada.

*Governor* is directed by Chinmay Mandlekar, produced by Vipul Amrutlal Shah (who previously backed *The Kerala Story*), with music by Amit Trivedi and lyrics by Javed Akhtar. Adah Sharma co-stars.

The film enters a crowded June 12 slate — it'll compete with Kangana Ranaut's *Bharat Bhhagya Viddhaata* and at least two other releases. But a Bajpayee performance built around India's most consequential economic moment? That's an audience that books tickets regardless of what else is playing.

**Release date:** June 12, 2026, in theaters.""",
    },

    # Article 3: Jailer 2 Hrithik Roshan after SRK drops out
    {
        "headline": "Shah Rukh Khan Couldn't Do Jailer 2. Now Rajinikanth's Sequel Is Chasing Hrithik Roshan Instead.",
        "subheadline": "SRK reportedly dropped out due to King commitments. The Rajinikanth sequel, eyeing a September release, has already secured a record ₹160 crore OTT deal with Amazon.",
        "slug": "jailer-2-hrithik-roshan-cameo-shah-rukh-khan-rajinikanth-september-2026-nri-20260531",
        "category": "entertainment",
        "image_person": "Rajinikanth",
        "image_pexels_query": None,
        "sources_text": "Pinkvilla, MensXP, Sacnilk, Valai Pechu",
        "body": """The most anticipated cameo in Tamil cinema just got a plot twist. Shah Rukh Khan was supposed to appear in *Jailer 2* alongside Rajinikanth, but the Pathaan star has reportedly pulled out because of his commitments to *King*. The makers are now in active discussions with Hrithik Roshan to fill the slot.

The report, first surfaced by Tamil industry tracker Valai Pechu and confirmed by multiple outlets including Pinkvilla and MensXP, suggests that the swap is still being negotiated. There's no official confirmation from Sun Pictures or Hrithik's team.

## Why This Matters

*Jailer* was a monster. The 2023 original grossed over ₹604 crore worldwide, moved 9 million tickets, and registered ₹21 crore in advance bookings on BookMyShow alone. Its formula — Rajinikanth as a retired jailer who assembles an all-star crew of cameos — turned the film into a pan-Indian event. Mohanlal, Shiva Rajkumar, and Jackie Shroff all showed up, each getting their own mass moment.

The sequel, directed by Nelson Dilipkumar, was always going to double down on the cameo strategy. Mithun Chakraborty has already confirmed his involvement. Vidya Balan, S.J. Suryah, and Suraj Venjaramoodu are part of the ensemble. Mohanlal and Shiva Rajkumar are expected to return. Bigg Boss 18's Edin Rose has reportedly joined for a substantial role. Even Nora Fatehi is confirmed for a dance number.

Shah Rukh Khan's cameo was supposed to be the crown jewel — a Thalaivar-and-King-Khan frame that would have broken the internet. Fans are understandably processing the loss.

## The OTT Side of the Story

The business numbers tell their own tale. Amazon Prime Video has locked the post-theatrical digital rights for *Jailer 2* at a reported ₹160 crore — a 113% jump over the ₹75 crore Netflix paid for the first film. That makes it the most expensive Tamil OTT acquisition in history, surpassing even Vijay's *Leo* and Kamal Haasan's *Thug Life*, both valued around ₹120 crore.

The premium reflects the franchise's proven commercial viability, but it also prices in the expectation that *Jailer 2* will be a bigger spectacle than its predecessor. Losing SRK and potentially gaining Hrithik doesn't necessarily reduce the spectacle — Hrithik brings his own brand of screen command — but it changes the flavor entirely.

## Diaspora Audience Impact

For the NRI audience, the *Jailer* franchise occupies a unique space — it's a Tamil-language film that functions as a pan-Indian event, the kind of movie that fills screens from Dallas to Dubai on opening night. The cameo strategy turns each screening into a communal experience where the audience erupts at every reveal.

Hrithik Roshan, fresh off the *War* franchise and with strong pull among Hindi-belt NRIs, could deliver a different kind of electricity than SRK would have. But the question fans are asking is simpler: can any Bollywood star walk into Rajinikanth's world and match the energy?

The film is reportedly targeting a September 10-11 release, timed around Ganesh Chaturthi. Shooting has wrapped, and post-production is underway.

**Status:** Unconfirmed but widely reported. Watch for an official announcement from Sun Pictures.""",
    },
]


# ---------- PUBLISH ----------
def publish_article(art):
    """Publish a single article with image sourcing."""
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:60]}...")

    # Image sourcing
    img_url = None

    # Try Wikipedia for person articles
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Wikipedia image failed validation, trying fallback...")
            img_url = None

    # Try Pexels fallback
    if not img_url and art.get("image_pexels_query"):
        img_url = fetch_pexels_image(art["image_pexels_query"])
        if img_url and not validate_image_url(img_url):
            img_url = None

    attribution = "Wikimedia Commons" if img_url and "wikipedia" in (img_url or "").lower() or "wikimedia" in (img_url or "").lower() else "The Videshi"

    # Build payload
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": "entertainment",
        "body": art["body"],
        "status": "published",
        "published_at": now,
        "sources": art.get("sources_text", ""),
        "image_url": img_url,
        "image_attribution": attribution if img_url else None,
    }

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        print(f"  Image: {img_url[:80] if img_url else 'None'}")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
        return None


def main():
    published = []
    for art in articles:
        art_id = publish_article(art)
        if art_id:
            published.append(art_id)
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Published {len(published)}/{len(articles)} articles")
    return 0 if published else 1


if __name__ == "__main__":
    sys.exit(main())
