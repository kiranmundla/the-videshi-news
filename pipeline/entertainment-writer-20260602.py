#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-02 batch."""

import json, os, re, sys, time, uuid, hashlib
from datetime import datetime, timezone
import requests, urllib.parse

# ── Supabase config ──
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ──

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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    headers = {"Authorization": PEXELS_KEY}
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length, try GET
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert a row into Supabase and return the result."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS, json=data, timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) else result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def sb_patch(table, match, data):
    """Update rows matching conditions."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS, json=data, timeout=30
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False


# ── Articles ──

articles = [
    # ── Article 1: Drishyam 3 ──
    {
        "headline": "Drishyam 3 Wraps Shooting. Akshaye Khanna Is Out. Jaideep Ahlawat Is In. October 2 Is Circled.",
        "subheadline": "Bollywood's most beloved franchise heads to post-production with a new cast member, a fee dispute, and a Gandhi Jayanti release that puts it on a collision course with the biggest day on India's calendar.",
        "slug": "drishyam-3-wraps-shoot-akshaye-khanna-exit-jaideep-ahlawat-october-2-nri-20260602",
        "category": "entertainment",
        "body": """If you grew up watching Vijay Salgaonkar outthink an entire police department with cable-TV plots and a fish pit, this one lands differently.

Drishyam 3 has wrapped its final shooting schedule. Director Abhishek Pathak confirmed the milestone with a note to his cast and crew that read less like a press release and more like a goodbye letter: "For the past many months, this film has been our world. We've spent countless days and nights together, chasing scenes, solving problems, sharing laughs, overcoming challenges."

The third and likely final instalment of the Hindi adaptation brings back Ajay Devgn as the 9th-fail cable operator who has now become Bollywood's most improbable criminal mastermind. Tabu returns as Meera Deshmukh, the IG whose obsession with justice has defined the franchise's moral tension. Shriya Saran, Ishita Dutta, and Mrunal Jadhav round out the Salgaonkar family.

## The Akshaye Khanna Exit

The headline-within-the-headline is who is **not** in the film. Akshaye Khanna, who electrified Drishyam 2 as IG Tarun Ahlawat, walked away from the project in late 2025. The fallout was spectacular and very public.

Producer Kumar Mangat Pathak told The Times of India that Khanna was initially enthusiastic — reportedly hugging the director and predicting a ₹500-crore haul. Then the terms changed. According to Bollywood Hungama, Khanna demanded ₹21 crore in fees, citing his post-Chhaava and post-Dhurandhar momentum. He also reportedly insisted on wearing a wig, which the makers rejected since his character went wigless in the second film.

Communication broke down. Panorama Studios initiated legal proceedings. By the time the dust settled, two new names had joined the cast.

## The Replacements

Jaideep Ahlawat — best known for Paatal Lok and the kind of screen presence that makes you forget he's acting — has stepped in, though director Pathak was careful to clarify: "Jaideep is not replacing Akshaye. I'm writing a new character." That distinction matters. This isn't a reshoot of existing scenes; it's a new antagonist thread.

Veteran Prakash Raj has also joined the ensemble, confirming that he too plays a fresh role rather than a stand-in. The casting upgrades have shifted the dynamic from a rematch to something potentially richer — a final chapter with new stakes.

## Shot Across Mumbai and Goa

The production spanned multiple locations, with an extended Goa schedule that reportedly provided some of the film's most crucial sequences. Given that the original Drishyam was set in Goa (Panaji, specifically), the return to that geography suggests the story circles back to where it all began.

## The October 2 Date

Drishyam 3 is locked for Gandhi Jayanti, October 2, 2026 — traditionally one of Indian cinema's most lucrative release windows. The date puts it in prime position for the festive corridor, though SRK's King has also been rumoured for the same slot. If both hold, it would be the biggest Bollywood clash of the year.

## The Diaspora Angle

For NRIs who discovered Drishyam through family WhatsApp groups and late-night binge sessions, this franchise carries weight beyond box office. It's the rare Hindi film that parents and children watch together, that sparks genuine debate at dinner tables — could Vijay really pull it off? Is Meera right to never let go?

The Malayalam Drishyam 3 with Mohanlal is also in production, and unlike previous instalments, the Hindi version will reportedly diverge from the original plot. For diaspora audiences who've watched both, that means two different final chapters to the same story.

The question Drishyam 3 needs to answer isn't whether Vijay Salgaonkar can outsmart the system one more time. It's whether anyone even wants him to. After two films of watching a man bury evidence and manipulate testimony to protect his family, the franchise has quietly become a referendum on complicity. The third film will either resolve that tension or live with it.

October 2 is circled. The cameras are down. Post-production has begun.""",
        "sources": [
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"},
            {"name": "The Times of India", "url": "https://www.timesofindia.com"}
        ],
        "image_person": "Ajay Devgn",
        "image_fallback_query": "Indian cinema thriller suspense",
    },
    # ── Article 2: Bandar ──
    {
        "headline": "Bobby Deol Spent 20 Days in a Fake Prison With 115 Theatre Actors. Someone's Foot Was on His Face. The Film Opens Thursday.",
        "subheadline": "Anurag Kashyap's Bandar premiered at TIFF to whispers of Bobby Deol's best work. Nine months later, it arrives in Indian theatres as a crime thriller about fame, false accusations, and the system that swallows you whole.",
        "slug": "bandar-bobby-deol-anurag-kashyap-tiff-prison-thriller-june-5-nri-20260602",
        "category": "entertainment",
        "body": """Here is something producer Nikhil Dwivedi wants you to know about the making of Bandar: Bobby Deol showed up at 7 AM every single morning for twenty consecutive days on a set designed to replicate an overcrowded Indian prison. The set held 115 actors — almost all trained theatre performers — packed into a single room, lying on top of each other. Bobby Deol was one of them. Someone's foot on his cheek. Someone else's on his stomach.

"In the beginning, the other actors were understandably hesitant," Dwivedi told Bollywood Hungama. "They would try to keep their distance and remain careful around him." Then Anurag Kashyap intervened: "It doesn't look like you're in jail at all. Why is everyone so stiff?" After that, Bobby Deol stopped being a star on set. He rarely returned to his vanity van. He ate where the others ate. He stayed.

## The Story

Bandar — released internationally as Monkey In A Cage — follows Sameer Mehra, a once-celebrated pop sensation and television star whose life collapses when his ex-girlfriend accuses him of rape. The film is inspired by real events, though the makers have not specified which. Written by Sudip Sharma and Abhishek Banerjee (the duo behind Paatal Lok and Kohrra), the screenplay navigates the space between allegation and guilt, between media spectacle and quiet devastation.

This is not a courtroom drama in the traditional sense. The courtroom exists, but the real arena is the prison — the brutal, corrupt, overcrowded world of India's undertrial system where innocence is theoretical and survival is the only immediate concern.

## The TIFF Reception

Bandar premiered at the 2025 Toronto International Film Festival in the Special Presentations program — the same section that has historically showcased films like Moonlight and The Whale before their commercial runs. Critics at TIFF described it as "hard-hitting, unflinching, and deeply impactful." The festival circuit positioned it as one of the year's most discussed Indian entries.

That was September 2025. The Indian theatrical release comes nine months later, on June 5, 2026 — a delay attributed to the competitive release calendar and strategic positioning by distributor Zee Studios.

## The Cast

The ensemble reads like a who's-who of India's finest character actors. Sanya Malhotra, who has steadily built one of the most interesting filmographies of her generation, plays a key role. Raj B. Shetty, the Kannada industry powerhouse behind Garuda Gamana Vrishabha Vahana, adds cross-industry gravity. Jitendra Joshi (Sacred Games), Sapna Pabbi, Saba Azad, Indrajith Sukumaran (one of Malayalam cinema's most respected actors), and Riddhi Sen round out a cast assembled for acting chops, not star power.

## Why the Diaspora Should Watch

For NRIs, Bandar arrives at a moment when India's criminal justice conversation has never been louder. The undertrial crisis — where hundreds of thousands of people languish in prison for years without conviction — is one of those issues that diaspora audiences know about but rarely see depicted with this level of specificity. Kashyap, whose work from Gangs of Wasseypur to Ugly has always drawn international festival audiences, has a built-in diaspora following.

Bobby Deol's career arc adds another layer. The Aap Ki Adalat interview last week — where he spoke about giving up on himself and the person who pulled him back — was not promotional machinery for this film. But it rhymes. Bandar is the work of an actor who has stopped performing and started inhabiting.

## The Box Office Reality

Bandar opens the same week as Peddi (Ram Charan's ₹250-crore sports drama), Hai Jawani Toh Ishq Hona Hai (David Dhawan's final directorial), and He-Man and the Masters of the Universe. It will not win the opening weekend numbers game. But Kashyap's films have never needed to. They find their audience — in theatres initially, on OTT platforms permanently, and in film school conversations for years after.

The foot on Bobby Deol's face? That's the film in miniature. Discomfort as craft. Specificity as style. A star who stopped asking for special treatment and got the best work of his career in return.""",
        "sources": [
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Bandar_(film)"},
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"}
        ],
        "image_person": "Bobby Deol",
        "image_fallback_query": "Indian cinema prison drama",
    },
    # ── Article 3: Ramayana at CinemaCon ──
    {
        "headline": "Ramayana Got a Private Screening Room at CinemaCon. The Audience Was Every Major Distributor on Earth.",
        "subheadline": "India's most expensive film just made its global pitch alongside Avengers and Avatar sequels. The diaspora might be the audience that unlocks the whole thing.",
        "slug": "ramayana-cinemacons-global-push-namit-malhotra-bollywood-nri-20260602",
        "category": "entertainment",
        "body": """CinemaCon is where Hollywood decides what gets screens. It is the annual convention where distributors, exhibitors, and studio executives from North America, Europe, Latin America, and Australia gather to see footage, hear pitches, and commit to the titles that will fill multiplexes for the next twelve months.

This year, Ramayana was in the room.

Not on a panel about "international cinema." Not in a sidebar about emerging markets. In the Milano III Ballroom, with its own private screening, its own presentation, and its own invitation — sent by exhibition industry veteran John Fithian — to "experience the world of Ramayana." The tone was unmistakable: this is not an Indian film seeking Hollywood's attention. This is a global blockbuster that happens to come from India.

## The Scale

Ramayana is widely reported as the most expensive Indian film ever produced. While exact figures remain unconfirmed, estimates place the budget between ₹600 crore and ₹1,000 crore — territory that puts it alongside mid-range Marvel productions. The visual effects pipeline, handled by producer Namit Malhotra's own Prime Focus (the same company that has done VFX work for Avatar, Gravity, and Interstellar), is being built to Hollywood technical standards.

Malhotra's pitch at CinemaCon was strategic: "Global audiences are now actively seeking fresh stories and new cultural perspectives." The implication was clear — in a market fatigued by superhero sequels, an ancient Indian epic rendered with cutting-edge technology offers something genuinely different.

## The Global Release Strategy

What happened at CinemaCon was not a screening. It was a sales operation. The production team organized private meetings with key distributors and exhibitors from every major territory. This level of focused international outreach is unprecedented for an Indian film.

Previous attempts at Indian films breaking through globally — from Baahubali to RRR to Pathaan — relied on diaspora audiences as the core international market, with crossover appeal as a bonus. Ramayana appears to be reversing that formula: the global pitch comes first, with the diaspora as the bridge audience that validates the investment for international exhibitors.

## Why the Diaspora Is the Linchpin

Every NRI who has tried to explain Diwali to a colleague or Dussehra to a neighbour has essentially been pitching the Ramayana. The story is the cultural operating system for a billion people. It is the reason Ram Navami exists, the reason Dussehra bonfires burn, the reason "Ram" is both a name and an invocation.

For diaspora audiences, a global Ramayana release isn't just a film — it's validation. It is seeing the story that shaped your childhood projected in an IMAX theatre in New Jersey or Leicester or Brampton, with the same technical polish as any Spielberg production. If the film delivers on its CinemaCon promise, NRI audiences will not just buy tickets. They will bring their non-Indian friends.

## The Competitive Landscape

Ramayana's CinemaCon presence positioned it alongside the biggest Hollywood titles of the year — films with marketing budgets that dwarf most Indian production costs entirely. That takes conviction, and it takes a certain amount of data. The success of RRR at the Oscars, Baahubali's $20M+ North American run, and the steady growth of Indian box office in the US and UK have created the market conditions for a film like this to be taken seriously by global exhibitors.

The risk is proportional to the ambition. If Ramayana delivers a visual spectacle that matches its source material's emotional weight, it could permanently redefine what "Indian cinema" means in international markets. If it feels like a VFX showreel with a mythology veneer, the setback won't just be commercial — it will close the door for the next Indian film that tries to walk into CinemaCon's ballroom.

## What Comes Next

The theatrical release date has not been confirmed, but the CinemaCon push suggests the makers are targeting a wide global day-and-date release — the same strategy used by Hollywood tentpoles. For diaspora audiences tracking the film, the CinemaCon moment was the signal that this is no longer an Indian industry event. It's a global entertainment bet with Indian storytelling at its centre.

The ballroom in Las Vegas is booked. The distributors have seen the footage. Now the film has to deliver what the pitch promised.""",
        "sources": [
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "CinemaCon Coverage", "url": "https://www.cinemacon.com"},
            {"name": "Variety (Indian cinema global push)", "url": "https://variety.com"}
        ],
        "image_person": None,
        "image_fallback_query": "Indian epic cinema ancient temple",
    },
]

# ── Publish loop ──
published = []

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Image sourcing
    img_url = None
    img_attribution = None

    if art.get("image_person"):
        print(f"  Trying Wikipedia for: {art['image_person']}")
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url:
            img_attribution = "Wikimedia Commons"

        if not img_url:
            # Try alternate name forms
            alt_names = {
                "Ajay Devgn": ["Ajay Devgan", "Ajay Devgn (actor)"],
                "Bobby Deol": ["Bobby Deol (actor)"],
            }
            for alt in alt_names.get(art["image_person"], []):
                img_url = fetch_wikipedia_person_image(alt)
                if img_url:
                    img_attribution = "Wikimedia Commons"
                    break

    if not img_url and art.get("image_fallback_query"):
        print(f"  Falling back to Pexels: {art['image_fallback_query']}")
        img_url = fetch_pexels_image(art["image_fallback_query"])
        if img_url:
            img_attribution = "The Videshi"

    # Validate image
    if img_url and not validate_image(img_url):
        print(f"  ✗ Image validation failed, dropping image")
        img_url = None
        img_attribution = None

    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")

    # Build sources JSON
    sources_json = json.dumps(art["sources"])

    # Build payload
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["category"],
        "body": art["body"].strip(),
        "sources": sources_json,
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "is_featured": False,
        "tags": [],
        "score_total": 0,
    }
    if img_url:
        payload["image_url"] = img_url
    if img_attribution:
        payload["image_attribution"] = img_attribution

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art_id}")
        published.append({
            "id": art_id,
            "slug": art["slug"],
            "headline": art["headline"],
            "has_image": bool(img_url),
        })
    else:
        print(f"  ✗ FAILED to publish")

# ── Summary ──
print(f"\n{'='*60}")
print(f"SUMMARY: {len(published)}/{len(articles)} articles published")
for p in published:
    img_status = "✓ with image" if p["has_image"] else "⚠ no image"
    print(f"  [{img_status}] {p['headline'][:60]}...")
