#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-02 batch."""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────────
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

# ── helpers ──────────────────────────────────────────────────────────────────

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
    """Fetch a relevant image from Pexels API using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify the URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert a row into Supabase."""
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:1000]}")
    return None


def sb_patch(table, filters, payload):
    """Patch rows in Supabase matching filters."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=payload)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False


def publish_article(article):
    """Insert article into p2_articles and attach image."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources"]),
        "is_editorial": False,
        "vertical": "entertainment",
    }

    result = sb_insert("p2_articles", payload)
    if not result:
        print(f"  ✗ Failed to publish: {article['headline']}")
        return None

    print(f"  ✓ Published: {article['headline']} (id={art_id})")

    # Image sourcing
    img_url = None
    if article.get("person_name"):
        img_url = fetch_wikipedia_person_image(article["person_name"])
        # Try alternate name if no result
        if not img_url and article.get("person_alt"):
            img_url = fetch_wikipedia_person_image(article["person_alt"])

    if not img_url and article.get("pexels_query"):
        img_url = fetch_pexels_image(article["pexels_query"], article.get("pexels_fallback"))

    if img_url:
        if validate_image(img_url):
            attribution = "Wikimedia Commons" if "wikimedia" in img_url or "wikipedia" in img_url else "The Videshi"
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": img_url,
                "image_attribution": attribution,
            })
            print(f"  ✓ Image attached: {img_url[:80]}...")
        else:
            print(f"  ⚠ Image validation failed, skipping: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found for: {article['headline']}")

    return art_id


# ── articles ─────────────────────────────────────────────────────────────────

articles = []

# ─── Article 1: Vicky Kaushal Mahavatar ───────────────────────────────────────
articles.append({
    "headline": "Vicky Kaushal Just Blocked 18 Months of His Life for One Role. It's Parashurama.",
    "subheadline": "The actor will undergo six months of physical transformation before filming even begins on Maddock Films' mythological epic Mahavatar, directed by Amar Kaushik.",
    "slug": "vicky-kaushal-mahavatar-parashurama-18-months-maddock-amar-kaushik-nri-20260602",
    "person_name": "Vicky Kaushal",
    "pexels_query": None,
    "pexels_fallback": None,
    "author_name": "Videshi Entertainment Desk",
    "author_slug": "videshi-entertainment-desk",
    "sources": [
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"}
    ],
    "body": """In an era when most A-listers juggle three to four projects a year, Vicky Kaushal has made a decision that breaks the template entirely. The actor has blocked a continuous eighteen-month window — from June 2026 through the end of 2027 — exclusively for **Mahavatar**, Maddock Films' mythological action epic about the immortal sage-warrior Parashurama.

No other film. No brand shoots squeezed in between schedules. No cameos. Just one role, one director, one story.

## The Prep Alone Takes Six Months

The timeline is staggering even by Bollywood's increasingly ambitious standards. Kaushal will begin an intensive six-month preparatory phase immediately after wrapping Sanjay Leela Bhansali's **Love and War**, which is targeting a January 2027 release with its final 50-day shooting schedule underway since May 2026.

Director **Amar Kaushik** — who turned Stree into a franchise and Stree 2 into a blockbuster — has designed a comprehensive training module for the role. It includes a rigorous physical transformation to bulk up Kaushal's physique to mythological proportions, alongside acting workshops focused on the psychological and spiritual depth of the character. Kaushik has been in pre-production for over seven months already, working on set design, weapon design, and character aesthetics.

"The prep is going on for 6-7 months. We have worked on the set design, weapon design, how every character would look. The scripting is done. Yet, we need more time," Kaushik told Bollywood Hungama in a recent interview.

## Why Parashurama Demands This Level of Commitment

Chiranjeevi Parashurama — the sixth avatar of Vishnu, an immortal warrior of dharma who bridges the Ramayana and Mahabharata — is among the most complex figures in Hindu mythology. He was the guru of Bheeshma, Dronacharya, and Karna. He received Mahakaal's Parashu (axe) and led the Devas to victory against the Asuras. His story spans ages, making him unlike any character Bollywood has attempted at this scale.

Filming is expected to begin in January 2027 and run through December, with heavy VFX post-production to follow. Maddock Films, produced by Dinesh Vijan, originally announced the film for a Christmas 2026 release before pushing it to 2027. An Independence Day 2027 weekend release is now being considered.

## Shraddha Kapoor in Talks for the Female Lead

According to Mid-Day, **Shraddha Kapoor** is the primary choice for the female lead. If confirmed, it would mark her first collaboration with Kaushal — a fresh pairing the producers believe will resonate with audiences. The Stree franchise connection through Kaushik makes the casting almost poetic.

## What This Means for the Industry — and the Diaspora

Kaushal's decision reflects a broader shift in Bollywood. Top-tier actors are increasingly choosing singular, high-impact performances over multiple concurrent projects. Ranveer Singh, notably, has moved away from the Don franchise to focus on **Pralay**, a survival drama shooting from August 2026. The industry is pivoting toward long-term investments in world-building — and the global audience, particularly the diaspora hungry for culturally rooted spectacle, stands to benefit.

For NRI audiences who grew up with Amar Chitra Katha depictions of Parashurama and debated his role in the Mahabharata over family dinners, Mahavatar represents something rare: a modern Indian film willing to take the time to get mythology right. Eighteen months for one character isn't excess. For Parashurama, it might just be enough.

*Mahavatar is produced by Maddock Films and directed by Amar Kaushik. A release date has not been officially confirmed.*"""
})

# ─── Article 2: Dhurandhar 2 OTT ─────────────────────────────────────────────
articles.append({
    "headline": "Dhurandhar 2 Hits JioHotstar on June 4 With 20 Extra Minutes the Theatres Never Showed",
    "subheadline": "The ₹1,100 crore spy thriller gets a 'Raw and Undekha' extended cut for its digital premiere — and the franchise's economics are as jaw-dropping as its action.",
    "slug": "dhurandhar-2-revenge-jiohotstar-ott-june-4-extended-cut-raw-undekha-nri-20260602",
    "person_name": "Ranveer Singh",
    "pexels_query": None,
    "pexels_fallback": None,
    "author_name": "Videshi Entertainment Desk",
    "author_slug": "videshi-entertainment-desk",
    "sources": [
        {"name": "JioHotstar", "url": "https://www.jiohotstar.com"},
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"}
    ],
    "body": """After eleven weeks in theatres, ₹1,100 crore in domestic net collections, and ₹1,800 crore worldwide, **Dhurandhar 2: The Revenge** is finally coming to your living room. JioHotstar has confirmed the spy thriller will begin streaming on **June 4 at 7 PM IST**, with regular subscriber access from June 5 onwards.

But the platform isn't just putting the theatrical cut online. This is the **"Raw and Undekha"** edition — an extended version featuring twenty minutes of additional footage, longer action sequences, and unseen scenes that never made it to cinemas.

## The Numbers That Broke Bollywood's Brain

Let's talk about the economics, because the Dhurandhar franchise has rewritten every rule in the book.

The two films were produced on a combined budget of just **₹255 crore**. Across both chapters, the franchise has generated over **₹3,107 crore** in total worldwide gross. The return on investment isn't just impressive — it's in a league of its own.

The digital rights deal is equally remarkable. Part 1 remained with Netflix at a revised value of ₹85 crore. The sequel's massive hype allowed producers to negotiate a separate **₹150 crore deal** with JioHotstar — pushing total digital revenue to ₹235 crore. That's nearly the entire production cost of both films recovered through streaming rights alone, before a single OTT viewer hit play.

Overseas, the film grossed **₹426.67 crore**, with roughly 18 percent of international revenue coming from premium formats like IMAX and 4DX. For the diaspora, that's significant — NRI audiences drove a measurable chunk of the international haul.

## What's in the Extended Cut

The Raw and Undekha version promises additional character depth alongside the expected action extensions. Director **Aditya Dhar** has spoken about scenes that were trimmed for the theatrical runtime of 3 hours and 55 minutes — itself one of the longest mainstream Hindi films in recent memory.

JioHotstar is treating the premiere as an event. A 30-minute pre-show at 7 PM on June 4 will feature candid cast conversations, behind-the-scenes footage, and insights into the making of the film.

## The Spy Universe Keeps Expanding

Dhurandhar 2 picks up with **Ranveer Singh** reprising his role as undercover operative Jaskirat Singh Rangi, now operating as Hamza Ali Mazari in Karachi, navigating organized crime while targeting terror cells linked to the 26/11 attacks. The film also stars **R. Madhavan**, **Sanjay Dutt**, and **Arjun Rampal**.

The franchise's success has cemented the Spy Universe as Bollywood's most bankable cinematic universe. With the sequel's 8.5/10 IMDB rating and a box office trail that outpaced everything except Baahubali 2 adjusted for inflation, the conversation has shifted from "if" to "when" for the next installment.

## Why This Matters for NRI Audiences

For diaspora viewers who caught the film in packed North American theatres — where advance bookings crossed $1.07 million — the extended cut offers a reason to revisit. For those who couldn't make it to a theatre screening, this is the main event.

The film is available in Hindi, Telugu, Tamil, Kannada, and Malayalam on JioHotstar. If you've somehow avoided spoilers for eleven weeks, your patience has been rewarded — with twenty extra minutes to show for it.

*Dhurandhar 2: The Revenge Raw & Undekha premieres on JioHotstar June 4 at 7 PM IST. Regular streaming begins June 5.*"""
})

# ─── Article 3: Karisma Kapoor Brown ─────────────────────────────────────────
articles.append({
    "headline": "Karisma Kapoor Plays a Disgraced Kolkata Cop Hunting a Serial Killer. Brown Drops on ZEE5 Thursday.",
    "subheadline": "The neo-noir crime thriller marks one of the most dramatic role departures in Karisma's three-decade career — and it arrives with a 9-minute Cannes ovation still echoing.",
    "slug": "karisma-kapoor-brown-zee5-neo-noir-kolkata-cop-serial-killer-june-5-nri-20260602",
    "person_name": "Karisma Kapoor",
    "pexels_query": "Kolkata night city",
    "pexels_fallback": "Kolkata street noir",
    "author_name": "Videshi Entertainment Desk",
    "author_slug": "videshi-entertainment-desk",
    "sources": [
        {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "MensXP", "url": "https://www.mensxp.com"}
    ],
    "body": """There is a version of Karisma Kapoor that Bollywood remembers: the one who danced through Dil To Pagal Hai, who brought glamour to every frame she occupied through the nineties and early 2000s. **Brown** is not that Karisma. And that's precisely the point.

Premiering on **ZEE5 on June 5**, the neo-noir crime thriller casts the veteran actress as **DCDD Rita Brown** — a disgraced, alcoholic Kolkata police officer haunted by a past she can't outrun, pulled back into active investigation when a series of brutal murders shocks the city.

## A Character Built on Fragility, Not Glamour

"Rita Brown is unlike any character I've played before," Karisma said in a statement ahead of the trailer launch. "She is flawed, vulnerable, emotionally bruised, yet incredibly resilient in the way she keeps moving forward despite everything life throws at her."

The actress has been selective in recent years, appearing in the 2024 whodunit **Murder Mubarak** and the 2020 series **Mentalhood**. But Brown represents something fundamentally different — a de-glam, psychologically layered lead performance that leans into darkness rather than away from it.

"What drew me was the emotional honesty of the writing," she added. "There's no attempt to glamorise pain or simplify human relationships. Over the years, I've played many strong women, but Rita's strength lies in her fragility and silence as much as in her courage."

## Kolkata as a Character

Director **Abhinay Deo** — who gave Bollywood the irreverent classic **Delhi Belly** and the taut thriller **24** — has spoken at length about why Kolkata isn't just a backdrop in this series.

"What truly compelled me to direct it was the way the writers handled the story," Deo told Bollywood Hungama. "At its core, it felt like a case study of people — individuals from different walks of life, social strata, castes, and communities. There is a Bihari, a Marwadi, a bhadralok Bengali, along with Anglo-Indians and Chinese characters. All of them coexist within Kolkata."

The series is adapted from **City of Death**, a novel by Abheek Barua, and it uses the city's haunting beauty and moral chaos as a canvas for its central mystery: a serial killer targeting young women, beginning with the daughter of an influential businessman.

## The Cast and Creative Team

Beyond Karisma, the ensemble includes **Jisshu Sengupta** as a psychiatrist who may hold vital information about the murders, **Surya Sharma** as Rita's grieving junior officer Inspector Arjun Sinha, **Soni Razdan**, veteran actress **Helen Khan**, **Paresh Pahuja**, **Ajinkya Deo**, and **Aryann Bhowmik**. Singer **Shaan** makes his OTT acting debut in a role that has generated considerable curiosity.

The writing team comprises Diggi Sissodia, Sunayana Kumari, and Mayukh Gosh, with cinematography by Amogh Deshpande and editing by Huzefa Lokhandwala. Production designer Shiuli Thukral doubles as creative producer.

## Why NRI Audiences Should Care

For diaspora viewers, Brown offers something the Indian OTT landscape has been building toward for years: a female-led noir with genuine psychological complexity, anchored by a star who doesn't need the safety net of glamour to command attention.

The Kolkata setting adds a dimension that global audiences increasingly appreciate — a city that is simultaneously literary, decaying, and alive. If you've watched international crime series set in Scandinavian or British cities and wished for something with the same atmospheric density but rooted in India, Brown is making that argument.

The trailer, dropped on May 30, has already drawn comparisons to international noir series — the dark imagery, the unreliable protagonist, the sense that every character is hiding something. Fans have responded with "OG is back" trending online, signaling an appetite for Karisma in roles that match her range rather than her image.

*Brown premieres on ZEE5 on June 5, 2026. The series is produced by Zee Studios and directed by Abhinay Deo.*"""
})

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"Entertainment writer starting — {len(articles)} articles queued")
    published = []
    for i, art in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] Publishing: {art['headline']}")
        art_id = publish_article(art)
        if art_id:
            published.append(art_id)
        time.sleep(1)

    print(f"\n✅ Done — {len(published)}/{len(articles)} articles published")
    return 0 if len(published) == len(articles) else 1

if __name__ == "__main__":
    sys.exit(main())
