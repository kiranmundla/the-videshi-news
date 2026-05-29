#!/usr/bin/env python3
"""Entertainment writer — 2026-05-29 batch"""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ["PEXELS_API_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}) for {image_url[:60]}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image ({content_type})")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return None

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=20,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:100]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def publish_article(article):
    """Insert article into p2_articles."""
    article["id"] = str(uuid.uuid4())
    article["status"] = "published"
    article["published_at"] = datetime.now(timezone.utc).isoformat()
    article["category"] = "entertainment"
    article.setdefault("vertical", "entertainment")
    article.setdefault("tags", [])
    article.setdefault("urgency", "medium")
    article.setdefault("is_featured", False)
    article.setdefault("score_total", 82)
    article.setdefault("is_editorial", False)

    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id", article["id"])
        print(f"✅ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"❌ Publish failed ({r.status_code}): {r.text[:200]}")
        return None


# ── ARTICLES ─────────────────────────────────────────────────────────

articles = []

# ── Article 1: Ranveer Singh's Pralay ────────────────────────────────
articles.append({
    "headline": "Ranveer Singh Is Making a ₹300 Crore Zombie Film. The Director Made Scam 1992. The Industry Banned Him Last Week.",
    "subheadline": "Pralay, a post-apocalyptic thriller directed by Jai Mehta, starts filming in August — even as FWICE's non-cooperation directive over the Don 3 fallout hangs over Ranveer's head.",
    "slug": "ranveer-singh-pralay-300-crore-zombie-film-jai-mehta-fwice-ban-nri-20260529",
    "body": """Ranveer Singh's next film is not a sequel. It is not a franchise extension. It is a ₹300 crore zombie thriller set in a post-apocalyptic Mumbai — and it is going ahead despite the most public industry standoff of the year.

## The Project

Pralay is directed by Jai Mehta, whose debut feature as co-director — Scam 1992: The Harshad Mehta Story — swept 11 awards at the 2021 Filmfare OTT Awards and rewired how India consumed long-form storytelling. The series' theme music crossed 7 million streams. Achint Thakkar's score became as recognizable as any Bollywood hit album that year.

Now Jai Mehta is moving from streaming to spectacle. Pralay is based on an original screenplay co-written by Mehta and Vishal Kapoor — not, as earlier rumored, an adaptation of José Saramago's 1995 novel Blindness. The film is produced by Hansal Mehta's True Story Films and Ranveer's own banner, Ma Kasam Films, with backing from Applause Entertainment.

Joining Ranveer in the lead is Kalyani Priyadarshan, making her Bollywood debut. The daughter of veteran director Priyadarshan, she has already established herself in Tamil and Telugu cinema.

## The Controversy

The timing is impossible to ignore. FWICE — the Federation of Western India Cine Employees — issued a non-cooperation directive against Ranveer Singh over the Don 3 fallout, demanding ₹45 crore in compensation after his exit from the franchise. Salman Khan briefly mediated between Ranveer and Farhan Akhtar, but the truce was fragile.

Sources close to the production say the directive does not apply to Pralay because the dispute is between Ranveer and Excel Entertainment, not with the broader industry. Filming is confirmed for August 2026. But the math is not simple — a ₹300 crore production requires hundreds of FWICE members on set, and the directive technically empowers them to refuse work.

## Why This Matters for the Diaspora

For NRIs who grew up on Bollywood's song-and-dance formula, Pralay represents the same tectonic shift that Dhurandhar did — except this time the genre is completely alien to Hindi cinema. India has never mounted a zombie film at this scale. The budget is larger than most Hollywood mid-range genre films. If it works, it opens a door that Indian cinema has been afraid to walk through.

The Don 3 controversy also matters abroad. Ranveer's Dhurandhar 2 just crossed ₹1,000 crore in Hindi net collections alone — the first Bollywood film to do so. His overseas draw is enormous. An industry ban, even a partial one, directly affects release strategies, promotions, and the diaspora screening ecosystem that has become a significant revenue stream.

## What's Next

Pre-production is underway. AI-assisted visual effects are reportedly being developed to depict Mumbai's post-apocalyptic decay. The August start date gives the production team roughly two months to resolve — or work around — the FWICE situation. Ranveer Singh is betting that the film's ambition will outweigh the industry's grievance.

*Sources: Bollywood Hungama, SacNilk, MensXP, Bollywood Bubble*""",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "SacNilk", "url": "https://www.sacnilk.com"},
        {"name": "MensXP", "url": "https://www.mensxp.com"},
        {"name": "Bollywood Bubble", "url": "https://www.bollywoodbubble.com"},
    ]),
    "person_name": "Ranveer Singh",
    "pexels_fallback": ("zombie apocalypse city ruins", "abandoned city dark"),
})


# ── Article 2: Katrina and Vicky introduce baby Vihaan ──────────────
articles.append({
    "headline": "Katrina Kaif and Vicky Kaushal Brought Their Baby to the Airport. They Asked Photographers to Put Their Cameras Down.",
    "subheadline": "Seven months after welcoming son Vihaan, the couple introduced him to Mumbai's paparazzi — with one firm condition attached.",
    "slug": "katrina-kaif-vicky-kaushal-baby-vihaan-airport-paparazzi-privacy-nri-20260529",
    "body": """Katrina Kaif and Vicky Kaushal did something at Mumbai airport this week that most Bollywood couples avoid entirely: they walked their baby toward the press pack. And then they asked the press pack to stop shooting.

## The Moment

The couple was spotted leaving Mumbai together when photographers approached. Katrina was carrying their seven-month-old son, Vihaan Kaushal, born on November 7, 2025. Instead of the usual celebrity dodge — car window rolled up, security forming a wall — Katrina and Vicky stopped. They introduced the baby to the photographers present.

Then Katrina made a single request: no photographs of her holding the child.

"She asked not to be photographed with the baby and introduced the baby to the paparazzi," a photographer present at the airport told Pinkvilla. Vicky was photographed, but no images of Katrina with Vihaan were released.

## Why It Matters

This is the Bollywood equivalent of drawing a line in wet cement. The Mumbai paparazzi ecosystem — organized, persistent, commercially driven — operates on implicit agreements. Some celebrities cooperate for coverage; others retreat entirely. What Katrina and Vicky did was neither: they gave the media access to the moment while restricting the images.

It follows a pattern emerging among younger Bollywood parents. Anushka Sharma and Virat Kohli have kept their daughter Vamika almost entirely out of public view. Deepika Padukone and Ranveer Singh have shielded their daughter similarly. Priyanka Chopra and Nick Jonas took a different route, sharing Malti Marie's face on Instagram on their own terms.

Katrina's approach lands somewhere in the middle — acknowledging the public's curiosity while establishing that the terms belong to the parents.

## The Birthday Post

Earlier this month, Katrina shared an emotional birthday post for Vicky as he turned 38. She called him her "pillar of strength" and posted a series of family photographs, including one with Vihaan. In the caption, she joked about the "endless questions" she asks him about "mythology, AI, waterproofing, make up, health, business, all 'What if' situations in general and everything else in between."

The birthday cake in the photo read "happy birthday papa."

## The Diaspora Angle

For NRI fans who have followed Katrina's career from her early days as a British-Indian model through two decades of Hindi cinema, this chapter feels personal. Her marriage to Vicky — the Punjabi outsider who earned his way in — resonated across the diaspora. The baby's introduction, done on their terms, is a small but significant statement about how the next generation of Indian celebrity children might grow up in the public eye.

The couple tied the knot on December 9, 2021, in Rajasthan.

*Sources: Pinkvilla, Bombay Times, Bollywood Bubble, Medium*""",
    "sources": json.dumps([
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "Bombay Times", "url": "https://www.bombaytimes.com"},
        {"name": "Bollywood Bubble", "url": "https://www.bollywoodbubble.com"},
    ]),
    "person_name": "Katrina Kaif",
    "pexels_fallback": None,
})


# ── Article 3: Suriya's Karuppu box office ───────────────────────────
articles.append({
    "headline": "Suriya's Karuppu Just Crossed ₹270 Crore Worldwide. He Waited 13 Years for a Hit This Big.",
    "subheadline": "The Tamil fantasy drama shattered Singam 2's lifetime in four days, became Suriya's biggest film in Kerala, and reunited him with Trisha after 21 years.",
    "slug": "suriya-karuppu-270-crore-worldwide-tamil-box-office-record-trisha-nri-20260529",
    "body": """Suriya has spent the better part of a decade watching younger actors claim the box office records that once belonged to him. Singam 2, released in 2013, held as his career-best for thirteen years. That record lasted four days against Karuppu.

## The Numbers

By Day 13, Karuppu had earned approximately ₹163 crore in India net and ₹258 crore worldwide. The film is now pushing past ₹270 crore globally and is closing in on ₹200 crore in Tamil Nadu alone — a milestone only a handful of Tamil films have ever reached. It beat the lifetime collections of Mersal, Petta, and Thunivu within its first eight days.

The opening weekend delivered ₹78.75 crore in India gross. The second week held at ₹28.35 crore, a strong hold for a Tamil film that received mixed critical reviews.

In Kerala, Karuppu became Suriya's highest-grossing film ever — an especially notable achievement given that his earlier films had a modest footprint in the Malayalam market. In the Telugu states, where the film released as Veerabhadrudu, it crossed ₹30 crore with a 211 percent recovery rate for distributors.

## The Film

Karuppu is directed by RJ Balaji, who also acts in the film. The premise is unconventional for a commercial Tamil movie: Suriya plays a guardian deity who assumes the form of a lawyer after a devotee in distress pleads for justice. The film blends mythology, fantasy, and courtroom drama in a way that critics found uneven but audiences embraced completely.

The cast reunites Suriya with Trisha Krishnan for the first time since 2005's Aaru — a 21-year gap. The supporting cast includes Indrans, Swasika, Sshivada, Natty, Supreeth Reddy, and Anagha Maya Ravi.

## What Changed

Suriya's career trajectory has been a study in resilience. After the Singam franchise made him one of Tamil cinema's biggest commercial draws, a series of underperforming films pushed him into a difficult stretch. Etharkkum Thunindhavan (2022) underperformed. Vaadivaasal and other announced projects stalled or changed shape. His collaboration with Vetrimaaran on Vaadivaasal became one of Tamil cinema's most anticipated — and most delayed — projects.

Karuppu was not the expected comeback vehicle. It was an RJ Balaji film, not an auteur project. But that is precisely why the box office response has been so significant: it proved that the audience's relationship with Suriya remains commercially potent, regardless of the director or genre.

## The NRI Market

Karuppu's overseas performance has been solid, contributing significantly to its worldwide total. For the Tamil diaspora — concentrated in Singapore, Malaysia, the Middle East, the US, and the UK — Suriya occupies a specific generational niche. He is not Rajinikanth-era or Vijay-era. He is the actor who bridged the two, and his return to this level of commercial success validates that bridge.

The film is now streaming in select territories, expanding its reach beyond theatrical windows.

*Sources: Cinema Express, Filmibeat, Pinkvilla, SacNilk, TrackTollywood*""",
    "sources": json.dumps([
        {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
        {"name": "Filmibeat", "url": "https://www.filmibeat.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "SacNilk", "url": "https://www.sacnilk.com"},
    ]),
    "person_name": "Suriya",
    "person_alt": "Suriya (actor)",
    "pexels_fallback": ("Tamil cinema movie theater India", "Indian cinema audience"),
})


# ── Article 4: Sitaare Zameen Par TV premiere ────────────────────────
articles.append({
    "headline": "Aamir Khan's Sitaare Zameen Par Premieres on TV This Saturday. It Made ₹268 Crore. Most NRIs Haven't Seen It.",
    "subheadline": "The basketball comedy-drama — a spiritual sequel to Taare Zameen Par — hits Sony MAX on May 31, bringing Aamir's quietest box office success to living rooms across India and the diaspora.",
    "slug": "aamir-khan-sitaare-zameen-par-sony-max-tv-premiere-may-31-nri-20260529",
    "body": """Aamir Khan's Sitaare Zameen Par made ₹268 crore worldwide during its theatrical run. It opened to a ₹93 crore opening weekend. The cast reacted with visible emotion when they learned it would premiere on Sony MAX this Saturday, May 31.

And yet, for a film that performed this well, it has an unusual problem: a large portion of its natural diaspora audience has barely heard of it.

## The Film

Sitaare Zameen Par is a spiritual sequel to the 2007 classic Taare Zameen Par, but it is not about dyslexia or childhood learning disabilities. This time, Aamir plays a character who coaches a basketball team made up of individuals with intellectual disabilities. It is an official remake of the 2018 Spanish film Campeones, which itself was a box office hit in Spain.

The film was directed by R.S. Prasanna (who directed Shubh Mangal Saavdhan) and produced by Aamir Khan Productions and Jio Studios. It features 10 debutant actors — many with actual disabilities — alongside Aamir, marking one of Bollywood's most significant casting decisions in terms of representation.

The Shankar-Ehsaan-Loy score, the trio's first collaboration with Aamir since Taare Zameen Par, was celebrated at a musical gathering at Aamir's home on June 6 before the theatrical release.

## The Diaspora Gap

Here is the paradox: Taare Zameen Par is one of the most beloved Indian films in the diaspora. NRI parents, teachers, and community leaders have screened it for years. It is a cultural reference point. But Sitaare Zameen Par, despite strong box office numbers in India, did not replicate that cultural penetration abroad.

Part of the reason is timing. The film released during a packed Hindi calendar. Part of it is marketing — the diaspora never received the same saturation campaign that Dhurandhar or King announcements generate. And part of it is the disability focus itself, which can make international distributors cautious about how they position the film.

The Sony MAX premiere changes the equation. Satellite TV premieres in India still reach millions of viewers, and in an era of cord-cutting, they often become the first time diaspora audiences catch a film through family WhatsApp groups, YouTube clips, and social media reactions.

## Why It Matters

Sitaare Zameen Par is not a typical Aamir Khan film in the way the public imagines his work. It is not a three-hour epic with a social message delivered through spectacle. It is warm, small-scale by his standards, and genuinely funny — a basketball comedy-drama where the comedy comes from real chemistry and the drama from real stakes.

The 10 debutant actors have been widely praised. Critics noted that Aamir's performance was less the "Aamir Khan playing a character" mode and more a supporting presence designed to let his co-stars shine. For an actor known for controlling every frame of his films, this was a meaningful creative choice.

## The Numbers in Context

At ₹268 crore worldwide, Sitaare Zameen Par is not in the same commercial stratosphere as Dhurandhar or Dhurandhar 2. But it was profitable, well-received, and represents a creative palette that Aamir had been promising since Dangal — a willingness to make mid-budget, character-driven films alongside the blockbusters.

The film is also available on Sony LIV for streaming. But for many in the diaspora, the TV premiere this Saturday will be their introduction.

*Sources: Bollywood Hungama, SacNilk, Pinkvilla, Zoom TV*""",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "SacNilk", "url": "https://www.sacnilk.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"},
    ]),
    "person_name": "Aamir Khan",
    "pexels_fallback": ("basketball game court indoor", "basketball team"),
})


# ── Main execution ───────────────────────────────────────────────────
def main():
    published = 0
    for art in articles:
        print(f"\n{'='*60}")
        print(f"Processing: {art['headline'][:60]}...")

        # Extract custom fields not for DB
        person_name = art.pop("person_name", None)
        person_alt = art.pop("person_alt", None)
        pexels_fallback = art.pop("pexels_fallback", None)

        # Image sourcing — Wikipedia first for person articles
        img_url = None
        if person_name:
            img_url = fetch_wikipedia_person_image(person_name)
            if not img_url and person_alt:
                img_url = fetch_wikipedia_person_image(person_alt)

        if not img_url and pexels_fallback:
            if isinstance(pexels_fallback, tuple):
                img_url = fetch_pexels_image(pexels_fallback[0], pexels_fallback[1])
            else:
                img_url = fetch_pexels_image(pexels_fallback)

        # Upload to Supabase storage for permanence
        if img_url:
            filename = f"{art['slug']}.jpg"
            uploaded = upload_to_supabase_storage(img_url, filename)
            if uploaded:
                art["image_url"] = uploaded
                # Set attribution
                if "wikipedia" in img_url.lower() or "wikimedia" in img_url.lower():
                    art["image_attribution"] = "Wikimedia Commons"
                elif "pexels" in img_url.lower():
                    art["image_attribution"] = "Pexels"
                else:
                    art["image_attribution"] = "The Videshi"
            else:
                art["image_url"] = img_url
                art["image_attribution"] = "Wikimedia Commons"
        else:
            print("  ⚠ No image found — publishing without image")

        # Publish
        art_id = publish_article(art)
        if art_id:
            published += 1

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(articles)} articles.")

if __name__ == "__main__":
    main()
