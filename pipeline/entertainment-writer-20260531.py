#!/usr/bin/env python3
"""Entertainment writer for The Videshi - 2026-05-31 batch"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import requests
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Wikipedia image fetch ──
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
def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Image validation ──
def validate_image_url(url):
    """Check that URL returns an image > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: CT={ct}, CL={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

# ── Supabase insert ──
def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else 'unknown'
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:500]}")
        return None

# ── Articles ──

def write_anushka_sharma_one8_yoga():
    """Anushka Sharma invests in Agilitas, co-creating One8 Yoga with Virat Kohli"""
    print("\n📝 Writing: Anushka Sharma One8 Yoga...")

    headline = "Anushka Sharma Just Invested in Virat Kohli's Sportswear Company. Together, They're Launching a Yoga Line."
    subheadline = "One8 Yoga drops on International Yoga Day. The husband-wife bet on India's $22 billion athleisure market is a family affair now."
    slug = "anushka-sharma-virat-kohli-one8-yoga-agilitas-sports-athleisure-nri-20260531"

    body = """Anushka Sharma has picked up a minority stake in Agilitas Sports, the sportswear startup that already counts her husband Virat Kohli as an investor and co-creator. But this isn't a passive celebrity endorsement deal. Sharma will co-develop One8 Yoga, a new yoga-focused activewear line under the One8 brand, with a launch date of June 21 — International Day of Yoga.

The move makes the Kohli-Sharma household arguably the most commercially aligned power couple in Indian sport and entertainment. Kohli brought his One8 brand to Agilitas last year after ending an eight-year, ₹110 crore association with Puma. He invested roughly ₹40 crore in the startup as part of that deal. Now Sharma joins the cap table, though neither side has disclosed how much she's putting in.

## What Is Agilitas, and Why Does It Matter?

Agilitas Sports was founded in 2023 by Abhishek Ganguly, Atul Bajaj, and Amit Prabhu — all former Puma India executives. Ganguly was Puma India's managing director. The trio built the company as a vertically integrated sportswear platform: product design, manufacturing, distribution, and retail, all under one roof. It's backed by Convergent Finance and Nexus Venture Partners.

The company has moved fast. It acquired Mochiko Shoes in 2023, locked down long-term licensing rights for Lotto across India, South Asia, Australia, and South Africa, and recently launched Sportsyard, a large-format multi-brand sports retail chain. It claims over 12,500 employees across multiple manufacturing units.

When Kohli joined in 2025, the One8 brand came along — and with it, a clear signal that Agilitas was betting on athlete-driven lifestyle brands, not just performance gear.

## The Yoga Play

Sharma's involvement sharpens that bet. One8 Yoga will be a distinct category under the One8 umbrella, focused on yoga activewear that prioritizes comfort, movement, and functionality. Sharma described it as "building the category thoughtfully from the ground up," with products designed to "seamlessly integrate into daily routines."

Ganguly framed it as more than a brand extension. "Anushka joining goes much deeper than an investment," he said. "With One8 Yoga, we are extending that idea into a larger movement around wellness, mindfulness, and everyday fitness."

The timing is deliberate. India's athleisure market is projected to reach $22.4 billion by 2034, according to industry estimates. Yoga, once a niche wellness practice, has become a mainstream lifestyle category globally — and the Indian diaspora has been at the center of that shift. From Lululemon's dominance in North America to the proliferation of yoga studios in every NRI suburb, the market is there.

## What This Means for the Diaspora

For NRIs, the Kohli-Sharma entry into athleisure isn't just a business story — it's a cultural one. Indian-origin brands in the activewear space have been virtually nonexistent at the premium end. The closest parallel might be Sabyasachi's luxury fashion empire, but sportswear and yoga wear have been dominated by Western labels.

One8 Yoga, if executed well, could become the first Indian-founded yoga activewear brand with genuine global ambitions. Whether it ends up competing with Alo Yoga and Lululemon or carves out a distinctly Indian niche remains to be seen. But with two of India's most recognizable names behind it, it won't be starting from scratch.

The June 21 launch on International Day of Yoga is marketing that writes itself. Whether the product backs up the promise is the only question that matters."""

    sources = json.dumps([
        {"name": "Inc42", "url": "https://inc42.com"},
        {"name": "Franchise India", "url": "https://franchiseindia.com"},
        {"name": "Apparel Resources", "url": "https://apparelresources.com"}
    ])

    # Image: Try Wikipedia for Anushka Sharma
    img_url = fetch_wikipedia_person_image("Anushka Sharma")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_wikipedia_person_image("Virat Kohli")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("yoga activewear fashion", "yoga studio practice")
    if img_url and not validate_image_url(img_url):
        img_url = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikimedia" in img_url.lower() or "wikipedia" in img_url.lower()) else "The Videshi"
    }
    return insert_article(article)


def write_salman_khan_maatrubhumi():
    """Salman Khan's Maatrubhumi gets first industry reactions"""
    print("\n📝 Writing: Salman Khan Maatrubhumi screening...")

    headline = "Salman Khan Screened Maatrubhumi for Bollywood's Inner Circle. Every Director Called It a Must-Watch."
    subheadline = "The Galwan Valley war drama got its first reactions from Subhash Ghai, Kabir Khan, Sooraj Barjatya, and David Dhawan. No release date yet."
    slug = "salman-khan-maatrubhumi-screening-subhash-ghai-kabir-khan-must-watch-nri-20260531"

    body = """Salman Khan doesn't do quiet previews. When he screened a rough cut of Maatrubhumi: May War Rest in Peace for a handpicked group of Bollywood directors this week, the guest list read like a who's who of Hindi cinema's establishment: Subhash Ghai, Sooraj Barjatya, Kabir Khan, David Dhawan, Riteish Deshmukh, Chitrangda Singh, and Siddharth Roy Kapur.

The verdict was unanimous — at least publicly. Subhash Ghai took to X to call it "a must watch film," describing it as "a warm story of Indo-China soldiers with their respective emotions for their nations and families." Writer-director Rumy Jafry, who also attended, echoed the sentiment: "The film is truly a must watch."

## What Is Maatrubhumi About?

Originally titled Battle of Galwan, the film is inspired by the June 2020 Galwan Valley clash between Indian and Chinese soldiers — the deadliest border confrontation between the two countries in decades. Twenty Indian soldiers and an unknown number of Chinese troops were killed in hand-to-hand combat at 14,000 feet in Ladakh's Aksai Chin region.

Director Apoorva Lakhia has framed the story not as a jingoistic war film but as an emotional drama about soldiers and their families on both sides of the border. The title change from Battle of Galwan to Maatrubhumi: May War Rest in Peace reflects that shift — reportedly driven by sensitivities around depicting an ongoing geopolitical flashpoint.

Salman Khan underwent intense physical training and filmed at high-altitude locations in Ladakh. Chitrangda Singh co-stars. Choreographer Mudassar Khan revealed that they shot a massive song sequence with 200 dancers over five days, calling Salman's performance "baap level."

## The Release Date Problem

Maatrubhumi was originally scheduled for April 17. It was postponed after the makers undertook roughly 40 days of reshoots to "revise certain portions and enhance narrative impact." No new date has been announced, though reports suggest a possible Independence Day weekend window — which would be August 2026.

That delay matters commercially. Salman's last few theatrical releases have underperformed relative to his star power, and a patriotic war drama timed to Independence Day is a proven formula in Bollywood (Uri: The Surgical Strike, Gadar 2, and even Lakshya all benefited from nationalist sentiment around release timing).

## Why NRIs Should Watch This Space

The Galwan Valley clash resonated deeply across the Indian diaspora. It was one of those rare geopolitical events that cut through the noise — WhatsApp groups lit up, vigils were held in Silicon Valley and London, and the fallen soldiers became household names in NRI communities within days.

A film that treats that event with nuance rather than chest-thumping nationalism could be significant. Ghai's description — "mutual peace and respect" — suggests the filmmakers are going for emotional depth over propaganda. Whether that translates to box office success in a market that rewards flag-waving spectacle is another question entirely.

The screening's guest list itself tells a story. Sooraj Barjatya directed Salman in Maine Pyar Kiya and Hum Aapke Hain Koun. Kabir Khan made Bajrangi Bhaijaan and Ek Tha Tiger with him. David Dhawan gave him Partner and Biwi No. 1. These aren't film critics — they're collaborators with decades of shared history. Their approval is meaningful, but it's also expected.

The real test comes when Maatrubhumi faces audiences. Until then, the early buzz is real — and the wait continues."""

    sources = json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Bollywood Life", "url": "https://bollywoodlife.com"},
        {"name": "Bollywood Bubble", "url": "https://bollywoodbubble.com"}
    ])

    img_url = fetch_wikipedia_person_image("Salman Khan")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("Indian army soldiers Ladakh", "Indian military")
    if img_url and not validate_image_url(img_url):
        img_url = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikimedia" in img_url.lower() or "wikipedia" in img_url.lower()) else "The Videshi"
    }
    return insert_article(article)


def write_kd_devil_ott():
    """KD: The Devil hitting ZEE5 on June 5"""
    print("\n📝 Writing: KD The Devil OTT release...")

    headline = "KD: The Devil Hits ZEE5 on June 5. Sanjay Dutt and Dhruva Sarja's Gangster Saga Gets a Second Life."
    subheadline = "The Kannada period thriller underperformed in theatres but arrives on streaming in five languages — just in time for NRIs who missed it."
    slug = "kd-the-devil-zee5-ott-release-june-5-dhruva-sarja-sanjay-dutt-nri-20260531"

    body = """KD: The Devil had everything a pan-Indian blockbuster is supposed to have: a massive ensemble cast (Dhruva Sarja, Sanjay Dutt, Shilpa Shetty, Nora Fatehi, Sudeep in a cameo), a period gangster setting in 1970s Bengaluru, and a production scale that screamed event cinema. What it didn't have was an audience — at least not in theatres.

Now, five weeks after its April 30 theatrical release, the Kannada action thriller is heading to ZEE5 on June 5 for its digital debut. It'll stream in Kannada, Telugu, Tamil, Malayalam, and Hindi — and for the diaspora, this might actually be where the film finds its footing.

## What Went Wrong in Theatres

Director Prem's ambitious gangster saga drew near-universal negative reviews upon release. Critics called the narrative unfocused, the runtime excessive, and the visual effects inconsistent despite the big budget. The box office numbers reflected that disconnect: in a year where Tamil and Malayalam films have been setting records, KD: The Devil couldn't sustain first-week momentum.

The irony is that the film's building blocks were solid. The story follows Kalidasa — KD — a young man from humble beginnings who idolizes Dhak Deva (Sanjay Dutt), a feared underworld don. When a chain of betrayals drags KD's family into the don's crosshairs, the carefree youngster transforms into a reluctant warrior. It's a classic rise-of-the-underdog framework wrapped in period aesthetics, with the usual Kannada action cinema flair.

## The Cast Is the Draw

For NRI audiences who consume pan-Indian cinema primarily through OTT platforms, the cast alone makes this worth a look. Dhruva Sarja, fresh off the success of his prior Kannada hits, brings a raw, physical screen presence to the lead. Sanjay Dutt plays the menacing Dhak Deva — a role tailor-made for his late-career screen persona. Shilpa Shetty appears as Satyavati, Reeshma Nanaiah plays Macchu Lakshmi, and the supporting cast includes V. Ravichandran, Ramesh Aravind, and Jisshu Sengupta.

Sudeep's special appearance generated conversation even before the film's release. And Nora Fatehi's item number as "Senorita" was among the few elements that drew unqualified praise.

## June 5 Is a Crowded Day

ZEE5 isn't the only platform dropping heavy content on June 5. Mammootty's spy thriller Patriot also premieres on ZEE5 the same day in five languages. JioHotstar is releasing Dhurandhar 2 Revenge for Indian audiences. In theatres, Ram Charan's Peddi opens on June 4 and will dominate conversation.

For KD: The Devil, the OTT release is less about competing and more about redemption. Plenty of films that underperform theatrically — from Laal Singh Chaddha to Radhe — have found surprisingly engaged audiences on streaming platforms, especially among diaspora viewers who sample broadly and forgive theatrical flaws when they can watch at home.

The end credits already announced a sequel: KD 2: Evil's Kingdom. Whether it gets made will depend largely on whether ZEE5 can turn this into a streaming hit. Stranger things have happened.

## How to Watch

KD: The Devil premieres on ZEE5 on June 5, 2026. Available in Kannada, Telugu, Tamil, Malayalam, and Hindi. ZEE5 subscriptions are available in the US, UK, Canada, and most diaspora markets."""

    sources = json.dumps([
        {"name": "Koimoi", "url": "https://koimoi.com"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Cinema Express", "url": "https://cinemaexpress.com"},
        {"name": "The Cinema Post", "url": "https://thecinemapost.com"}
    ])

    img_url = fetch_wikipedia_person_image("Dhruva Sarja")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_wikipedia_person_image("Sanjay Dutt")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("gangster 1970s India vintage", "Indian cinema action")
    if img_url and not validate_image_url(img_url):
        img_url = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikimedia" in img_url.lower() or "wikipedia" in img_url.lower()) else "The Videshi"
    }
    return insert_article(article)


def write_vicky_katrina_vihaan():
    """Vicky Kaushal and Katrina Kaif introduce baby Vihaan to paparazzi"""
    print("\n📝 Writing: Vicky-Katrina baby Vihaan...")

    headline = "Katrina Kaif and Vicky Kaushal Introduced Baby Vihaan to Mumbai's Paparazzi. Then They Set One Rule."
    subheadline = "No photographs. The couple let photographers meet their six-month-old son at the airport but drew a clear line on images — following the Virat-Anushka playbook."
    slug = "katrina-kaif-vicky-kaushal-baby-vihaan-paparazzi-airport-privacy-rule-nri-20260531"

    body = """Katrina Kaif carried her six-month-old son Vihaan through Mumbai airport this week while Vicky Kaushal posed for the cameras. The couple introduced their baby to the paparazzi for the first time — and then asked them not to take his picture.

It was vintage Katrina-Vicky: warm, deliberate, and completely controlled. A photographer at the scene described the interaction simply: "Katrina was with Vicky, but she asked not to be photographed with the baby and introduced the baby to the paparazzi."

## The Playbook

The Kohli-Sharma approach to celebrity children has become the template in Bollywood. Virat and Anushka have never publicly shared a photograph of their daughter Vamika's face (though one paparazzi image leaked and was swiftly condemned by fans and industry alike). Alia Bhatt and Ranbir Kapoor have been similarly protective of daughter Raha, though they've been more willing to share curated moments on their own terms.

Katrina and Vicky appear to be charting a middle path. They didn't avoid the paparazzi. They walked through the airport, let Vicky take photos, and introduced Vihaan by name. But the no-photo request was firm. The message is clear: you can know our son exists. You can know his name. You cannot own his image.

## Why This Matters Beyond Bollywood

For the Indian diaspora, the evolution of celebrity privacy norms in India is fascinating because it tracks a cultural shift that NRIs often feel more acutely. In the US, UK, and Canada, the expectation of children's privacy — even for public figures — is deeply embedded. Paparazzi laws in California, anti-harassment legislation in the UK, and the general cultural norm of keeping kids off social media until they're old enough to consent have all reshaped how celebrity parents navigate visibility.

In India, the paparazzi ecosystem operates differently. Airport arrivals and departures are a genre unto themselves — celebrity spotting at Mumbai's Chhatrapati Shivaji International Airport is content that feeds dozens of Instagram pages and YouTube channels daily. The unwritten rule has historically been: if you're at the airport, you're fair game.

What Katrina and Vicky did was renegotiate that contract in real time. They showed up, engaged, and drew a line. The paparazzi, to their credit, apparently respected it. No unauthorized images of Vihaan have surfaced.

## The Name That Started a Conversation

When the couple revealed their son's name in January, the choice sparked instant recognition among Bollywood fans. Vihaan was the name of Vicky Kaushal's character in Uri: The Surgical Strike — the 2019 war drama that made him a household name and gave India one of its most quoted film dialogues: "How's the josh?"

Whether the naming was intentional homage or coincidence, the connection is now permanently etched into the family's public narrative. For a couple that has managed to keep their relationship, wedding, pregnancy, and now their child largely on their own terms, it's a fitting detail — personal, meaningful, and shared only when they chose to share it.

## A Private Couple in a Public Industry

Katrina Kaif and Vicky Kaushal successfully kept their relationship hidden from the paparazzi throughout their courtship — no leaked dinner photos, no airport sightings together, nothing. Their December 2021 wedding at Six Senses Fort Barwara in Sawai Madhopur, Rajasthan, was an invitation-only affair with phones reportedly collected at the door.

They welcomed Vihaan in November 2025 and announced it with a simple Instagram post: "Our bundle of joy has arrived."

Katrina was last seen on screen in Merry Christmas opposite Vijay Sethupathi. Vicky delivered one of 2025's biggest Hindi films with Chhaava, which crossed ₹797 crore worldwide. Both careers are at a peak. Both have chosen to keep their son out of the content machine.

In an industry where baby reveals generate millions of views and brand deals, that restraint is its own statement."""

    sources = json.dumps([
        {"name": "Bollywood Bubble", "url": "https://bollywoodbubble.com"},
        {"name": "Bombay Times", "url": "https://bombaytimes.com"},
        {"name": "Radio City", "url": "https://radiocity.in"}
    ])

    img_url = fetch_wikipedia_person_image("Katrina Kaif")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_wikipedia_person_image("Vicky Kaushal")
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("Mumbai airport terminal", "airport departure India")
    if img_url and not validate_image_url(img_url):
        img_url = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikimedia" in img_url.lower() or "wikipedia" in img_url.lower()) else "The Videshi"
    }
    return insert_article(article)


# ── Main ──
if __name__ == "__main__":
    print("=" * 60)
    print(f"Entertainment Writer - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results = []
    results.append(("Anushka Sharma One8 Yoga", write_anushka_sharma_one8_yoga()))
    results.append(("Salman Khan Maatrubhumi", write_salman_khan_maatrubhumi()))
    results.append(("KD The Devil OTT", write_kd_devil_ott()))
    results.append(("Vicky-Katrina Baby Vihaan", write_vicky_katrina_vihaan()))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, art_id in results:
        status = "✓ Published" if art_id else "✗ Failed"
        print(f"  {status}: {name}")
    
    success = sum(1 for _, aid in results if aid)
    print(f"\n{success}/{len(results)} articles published successfully.")
    print("=" * 60)
