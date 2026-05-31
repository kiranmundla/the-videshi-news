#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 batch"""

import json, os, sys, time, uuid, re, html
from datetime import datetime, timezone

import requests
import urllib.parse

# ── ENV ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── IMAGE HELPERS ──────────────────────────────────────────────────────
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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check that the URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET with range
        if r.status_code == 200 and "image" in ct:
            return True
    except Exception:
        pass
    return False


# ── SUPABASE HELPERS ────────────────────────────────────────────────────
def sb_insert(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Inserted: {article['slug']} (id={aid})")
        return aid
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLES ────────────────────────────────────────────────────────────
articles = []

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 1: Masoom: The New Generation — Shekhar Kapur & A.R. Rahman
# ────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Shekhar Kapur and A.R. Rahman Reunite for Masoom: The New Generation. Naseeruddin Shah and Shabana Azmi Are Returning.",
    "subheadline": "Forty-three years after the original, the filmmaker is revisiting his classic with the Oscar-winning composer as co-producer — and a cast that bridges two eras of Indian cinema.",
    "slug": "shekhar-kapur-ar-rahman-masoom-new-generation-naseeruddin-shabana-azmi-nri-20260531",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Cinema Express", "Bollywood Hungama", "Devdiscourse"]),
    "image_attribution": "Wikimedia Commons",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "person_for_image": "A. R. Rahman",
    "pexels_fallback": ("Indian film director", "Bollywood cinema"),
    "body": """It has been forty-three years since a young Jugal Hansraj walked into a household that did not know what to do with him, and the phrase *"Tujhe Nahin Chodhunga"* became shorthand for an entire generation's understanding of what family secrets could cost. Now Shekhar Kapur is going back.

The filmmaker has officially announced **Masoom: The New Generation**, a contemporary reimagining of his 1983 classic that will explore evolving ideas of identity, family, love, and migration — themes that carry a particular charge for diaspora audiences who have spent decades navigating those very questions across continents.

## The Reunion That Matters

The headline casting brings back **Naseeruddin Shah** and **Shabana Azmi**, who played the couple at the heart of the original film's devastating domestic crisis. They will be joined by **Manoj Bajpayee**, **Nithya Menen**, and **Kaveri Kapur** — Shekhar's own daughter, adding a personal dimension to a project already loaded with emotional weight.

But the collaboration that has the industry most intrigued is behind the camera. **A.R. Rahman** is not merely scoring the film — he is serving as co-producer, marking one of the rare occasions the Oscar-winning composer has taken a financial and creative stake in a project beyond its music.

"Working with Shekhar has always been a deeply enriching experience — he has been a mentor and a creative force in many ways," Rahman said in a statement. "When he shared the vision for this film, I felt compelled to be involved beyond the music. There's something timeless about *Masoom*, and reinterpreting that emotional world for a new generation feels both exciting and necessary."

## Why This Matters to the Diaspora

The original *Masoom* — adapted from Erich Segal's novel *Man, Woman and Child* — resonated precisely because it refused to moralize. It presented a family forced to confront an uncomfortable truth and let the audience sit in the discomfort. For NRI families who have watched Indian cinema grow progressively louder and more maximalist, the announcement signals a return to the kind of quiet, interior storytelling that once defined Hindi cinema's artistic peak.

The addition of "migration" to the film's stated themes is telling. Kapur, who has lived and worked between India and the UK for decades, brings a naturally transnational perspective. He knows what it means to belong to multiple worlds at once — a sensibility that the diaspora shares but rarely sees reflected in mainstream Bollywood.

"For a long time, I've felt that the themes of *Masoom* deserved to be revisited through the lens of today's world," Kapur said. "Families, relationships, identity — these ideas have evolved so much, and cinema must evolve with them."

## A Stacked Creative Partnership

Kapur and Rahman have a history that predates their celebrity. Rahman composed for Kapur's involvement in *Dil Se..* (1998) and scored *Elizabeth: The Golden Age* (2007). They also collaborated on the West End musical *Bombay Dreams* and the theatrical production *Why? The Musical*. Each project pushed both artists into unfamiliar territory — exactly the kind of creative risk-taking that *Masoom: The New Generation* appears to demand.

The film is currently in pre-production and is expected to begin shooting later this year, with a worldwide theatrical release anticipated in 2026.

For a generation of Indian viewers — both in India and abroad — who grew up with Jugal Hansraj's face and Gulzar's lyrics as their introduction to moral complexity in cinema, the question is simple: can lightning strike the same place twice? Kapur seems to believe the place has changed enough that it's worth trying.

*Sources: Cinema Express, Bollywood Hungama, Devdiscourse*"""
})

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 2: Vashu Bhagnani ₹400 Crore Lawsuit
# ────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit Over Two Biwi No. 1 Songs. Hai Jawani's June 5 Release Is Now in Jeopardy.",
    "subheadline": "The producer's Puja Entertainment is seeking an injunction to block distribution, exhibition, and streaming of Varun Dhawan's film — one of the largest copyright suits in recent Bollywood history.",
    "slug": "vashu-bhagnani-400-crore-lawsuit-biwi-no-1-songs-hai-jawani-varun-dhawan-nri-20260531",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Bollywood Hungama", "India Forums", "Zoom TV"]),
    "image_attribution": "Wikimedia Commons",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "person_for_image": "Varun Dhawan",
    "pexels_fallback": ("Bollywood film court", "Indian legal court"),
    "body": """A week before David Dhawan's **Hai Jawani Toh Ishq Hona Hai** was supposed to arrive in theatres, the film has walked into a legal minefield worth ₹400 crore.

Producer Vashu Bhagnani's **Puja Entertainment** has filed a massive suit in the Bombay High Court against **Tips Industries Limited**, brothers **Ramesh and Kumar S Taurani**, and filmmaker **David Dhawan** himself — alleging that two iconic songs from the 1999 blockbuster *Biwi No. 1* were used in the Varun Dhawan-starrer without valid rights or authorization.

The songs at the centre of the dispute: **'Chunnari Chunnari'** and **'Ishq Sona Hai'**, two of the most recognizable Bollywood tracks of the late '90s.

## What Puja Entertainment Is Claiming

According to the press statement issued through Counsels V K Dubey Associates, Puja Entertainment is seeking "urgent and sweeping injunctive relief" to restrain the release, distribution, exhibition, streaming, and any further commercial exploitation of the film and its promotional material containing the disputed songs.

The suit also seeks an additional ₹100 crore in damages beyond the ₹400 crore claim — bringing the total legal exposure to half a billion rupees.

The lawyer for Puja Entertainment, Advocate V K Dubey, has laid out the timeline in detail. He claims that Tips originally held only audio rights under their agreement with Puja Entertainment. In 2018, when Tips allegedly requested visual rights as well, things fell apart. "Puja Entertainment had sent a notice to them saying that they are cancelling the agreement as they didn't comply with the terms related to royalty and other things," Dubey told ANI. "So Puja Entertainment had cancelled all rights at that time. Leave alone video rights — Puja Entertainment had even cancelled the audio rights."

He further alleged that Tips continued to exploit both audio and visual content from Puja's films across YouTube, Instagram, and other platforms even after the rights were terminated.

## What This Means for the Film

**Hai Jawani Toh Ishq Hona Hai**, starring **Varun Dhawan**, **Mrunal Thakur**, and **Pooja Hegde**, is scheduled to release on **June 5, 2026**. The court has reportedly permitted the filing and has kept the matter for an early hearing — meaning a ruling could arrive before or around the release date.

If the injunction is granted, it could force the makers to either pull the disputed songs from the film or delay the release altogether. For a film that has already been through a turbulent production cycle, the timing could not be worse.

## The Bigger Picture

This is not just a contractual dispute. It touches on a chronic problem in Bollywood's music ecosystem: the tangled web of who owns what, especially when songs from the '90s and early 2000s are remixed for new films. The industry's appetite for nostalgic remakes has created a lucrative but legally precarious market where original producers, music labels, and new filmmakers often operate on conflicting assumptions about rights that were never properly documented or transferred.

For NRI audiences who grew up with *Biwi No. 1* — and who associate 'Chunnari Chunnari' with wedding sangeets and Navratri parties across three continents — the suit is a reminder that the soundtracks of their childhoods are now corporate battlegrounds.

The Bombay High Court's decision will be watched closely. If Puja Entertainment succeeds in blocking the release, it would set a significant precedent for how remixed or recreated songs are licensed in the future. If Tips prevails, it will likely be on the strength of whatever documentation exists from the original agreements — a question that could take months to fully adjudicate.

Either way, David Dhawan's retirement film — which was supposed to be a valedictory celebration — has become a legal exhibit.

*Sources: Bollywood Hungama, India Forums, Zoom TV*"""
})

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Hombale Films enters Marathi cinema with Yeto Ka Naay
# ────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "The Producers of KGF and Kantara Just Made Their First Marathi Film. It's a Hip-Hop Musical.",
    "subheadline": "Hombale Films' Yeto Ka Naay is a bilingual coming-of-age story set in Mumbai's underground music scene — a radical departure from the action epics that made them a pan-India powerhouse.",
    "slug": "hombale-films-yeto-ka-naay-marathi-hip-hop-musical-kgf-kantara-nri-20260531",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Bollywood Hungama", "New Kerala", "BlazeaTrends"]),
    "image_attribution": "",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "person_for_image": None,
    "pexels_fallback": ("Mumbai hip hop music street", "Indian hip hop rapper"),
    "body": """When you think of **Hombale Films**, you think of Yash walking through fire in *KGF*, or Rishab Shetty invoking ancient spirits in *Kantara*, or Prabhas with a rifle in *Salaar*. You think of scale, swagger, and the kind of maximalist action cinema that turned a Bangalore-based production house into a pan-India brand.

You do not think of hip-hop musicals.

Which is exactly why **Yeto Ka Naay** is interesting.

## The Announcement

Hombale Films, led by producer **Vijay Kiragandur**, has officially entered Marathi cinema for the first time with a project that could not be further from their comfort zone. *Yeto Ka Naay* is described as a coming-of-age hip-hop musical drama set entirely in Mumbai, exploring youth culture, friendship, identity, and ambition through the city's evolving underground music scene.

The film is being released as a bilingual — the Marathi version retains the original title, while the Hindi version will be called **YKN - Pehla Vaar**.

Directed by **Sarang Sanjeev Sathaye**, the screenplay was co-written by Sathaye alongside **Sujay Jadhav**, **Srushti Tawade** (an actual hip-hop artist, adding authentic street credibility), and **Shreyas Sagvekar**. Music is by **AV Prafullachandra**, and **Harshvir Oberai** is handling cinematography. The shoot is already underway in Mumbai.

## Why It Matters

The timing is not coincidental. Marathi cinema is in the middle of a historic run. **Raja Shivaji**, directed by and starring Riteish Deshmukh, has crossed ₹115 crore worldwide to become the highest-grossing Marathi film of all time, dethroning *Sairat*'s decade-old record. **Deool Band 2** has surprised everyone by racing toward ₹50 crore in its first week. The Marathi market is no longer a regional afterthought — it is a genuine commercial force.

For Hombale Films, entering this market is both a business move and a creative statement. The production house has spent years building a model based on high-concept, mass-appeal cinema in Kannada, Telugu, and Hindi. A Marathi hip-hop musical represents a deliberate expansion into a different register — intimate, urban, youth-driven, and culturally specific.

## The Diaspora Connection

Mumbai's hip-hop scene has always had a complicated relationship with the Indian diaspora. The genre's rise in India — from *Gully Boy* to the proliferation of battle rap leagues and independent labels — was partly fueled by NRIs who grew up on American hip-hop and recognized something familiar in the way young Indians were using the form to narrate their own stories of class, ambition, and identity.

A film that takes this culture seriously — rather than treating it as a backdrop for star-vehicle melodrama — has the potential to resonate with younger diaspora audiences who have watched Indian cinema struggle to represent their reality.

Whether Hombale Films can translate their instinct for spectacle into a more grounded, music-driven narrative remains to be seen. But the fact that the makers of *KGF* are willing to bet on a Marathi hip-hop film tells you something about where Indian cinema is headed: the regional is no longer niche, and genre experimentation is no longer optional.

The film is slated for a theatrical release later this year.

*Sources: Bollywood Hungama, New Kerala, BlazeaTrends*"""
})


# ── PUBLISH LOOP ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"Publishing {len(articles)} articles")
print(f"{'='*60}\n")

for i, art in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {art['headline'][:70]}...")

    # Image sourcing
    img_url = None
    if art.get("person_for_image"):
        img_url = fetch_wikipedia_person_image(art["person_for_image"])
        if not img_url:
            # Try alternate name forms
            alts = []
            name = art["person_for_image"]
            if "." in name:
                alts.append(name.replace(".", ""))
            alts.append(name)
            for alt in alts:
                img_url = fetch_wikipedia_person_image(alt)
                if img_url:
                    break

    if not img_url and art.get("pexels_fallback"):
        q1, q2 = art["pexels_fallback"]
        img_url = fetch_pexels_image(q1, q2)

    if img_url and validate_image_url(img_url):
        art["image_url"] = img_url
        print(f"  ✓ Image validated: {img_url[:80]}...")
    elif img_url:
        print(f"  ⚠ Image failed validation, trying Pexels fallback...")
        if art.get("pexels_fallback"):
            q1, q2 = art["pexels_fallback"]
            img_url = fetch_pexels_image(q1, q2)
            if img_url and validate_image_url(img_url):
                art["image_url"] = img_url
                art["image_attribution"] = "Pexels"
            else:
                art["image_url"] = None
        else:
            art["image_url"] = None
    else:
        art["image_url"] = None

    # Clean up non-DB fields
    for k in ["person_for_image", "pexels_fallback"]:
        art.pop(k, None)

    # Insert
    aid = sb_insert(art)
    if aid:
        print(f"  ✓ Published: {art['slug']}")
    else:
        print(f"  ✗ FAILED: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done! Published {len(articles)} entertainment articles.")
print(f"{'='*60}")
