#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 6, 2026 - Fixed"""

import json
import os
import subprocess
import sys
import urllib.parse
import requests
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v
                    break

UA = "TheVideshi/1.0 (thevideshi.com)"


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia: {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    return url
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return None


def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                return photos[0]["src"]["large"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Validate with retry and 2s delay for Wikimedia 429s."""
    for attempt in range(2):
        try:
            r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                ct = r.headers.get("Content-Type", "")
                cl = int(r.headers.get("Content-Length", 0))
                if "image" in ct and cl > 5000:
                    return True
                if "image" in ct and cl == 0:
                    r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
                    chunk = r2.raw.read(6000)
                    if len(chunk) > 5000:
                        return True
            elif r.status_code == 429 and attempt == 0:
                import time
                print(f"  ⏳ 429, retrying in 3s...")
                time.sleep(3)
                continue
            return False
        except:
            return False
    return False


def find_image(person_name=None, wiki_search=None, pexels_query=None):
    # Wikipedia person image first
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image(img):
            return img, "Wikimedia Commons"

    # Wikimedia Commons
    if wiki_search:
        import time
        time.sleep(2)  # Rate limit
        img = fetch_wikimedia_commons(wiki_search)
        if img and validate_image(img):
            return img, "Wikimedia Commons"

    # Pexels
    if pexels_query:
        img = fetch_pexels(pexels_query)
        if img and validate_image(img):
            return img, "Pexels"

    return None, None


def insert_article_curl(article):
    """Insert using curl to avoid potential Python requests encoding issues."""
    payload = json.dumps(article, ensure_ascii=False)
    tmp_file = "/tmp/article_payload.json"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(payload)

    result = subprocess.run(
        ["curl", "-sS", "-w", "\n%{http_code}",
         f"{SUPABASE_URL}/rest/v1/p2_articles",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", f"@{tmp_file}"],
        capture_output=True, text=True, timeout=30
    )
    lines = result.stdout.strip().split("\n")
    status_code = lines[-1] if lines else "0"
    body = "\n".join(lines[:-1])

    if status_code in ("200", "201"):
        try:
            data = json.loads(body)
            if isinstance(data, list) and data:
                print(f"  ✓ Published: {data[0].get('headline', '')[:60]}...")
        except:
            print(f"  ✓ Published (status {status_code})")
        return True
    else:
        print(f"  ✗ Insert failed ({status_code}): {body[:300]}")
        return False


# ============================================================
# ARTICLE 1: Peddi Director Apologizes
# ============================================================
print("\n=== Article 1: Peddi Director Buchi Babu Apology ===")

img1, attr1 = find_image(person_name="Ram Charan", pexels_query="cricket India sports")
if not img1:
    img1, attr1 = find_image(person_name="Janhvi Kapoor")

caption1 = "Ram Charan in a promotional appearance" if img1 and "Ram" in str(img1) else "Janhvi Kapoor at a media event"

body1 = """Buchi Babu Sana's *Peddi* crossed ₹150 crore worldwide in its first two days. By the end of day two, its director was apologising for how he made it.

In an interview with SCREEN published on June 6, Buchi Babu acknowledged the fierce backlash against the depiction of Janhvi Kapoor's character Achiyyamma in the Ram Charan-led sports drama. "I did not foresee that audiences would react so negatively to certain scenes," he said. He promised that the experience "will influence his future approach to female characters" and added that the team would "take more care to ensure better representation in our storytelling."

More significantly, the director indicated that changes would be made to "concerned portions" of the film — a rare mid-run editorial admission for a major Telugu release.

## What Audiences Objected To

The controversy centres on the first half of the film, which is set in the Vizianagaram district of Andhra Pradesh. Critics and social media users identified a pattern they called the objectification of the female lead. Kapoor's character is introduced in a scene where the camera lingers on her body without showing her face for an extended period. The courtship that follows includes the hero openly telling his friends he intends to touch Achiyyamma without consent, proceeding to do so, and later framing the physical aggression as an expression of love. The arc concludes with a kiss, with no narrative consequences for the behaviour.

The response was swift. Social media users, critics, and Kapoor herself appeared to weigh in — she reportedly liked a post calling the film "the most expensive disrespect" to its leading woman, then unliked it, drawing more attention to the debate. Reviewers at Firstpost called it a "muddled sports drama" that "suffers from too many subplots and an objectified Janhvi Kapoor." News18 noted the film "does not understand 'no means no.'"

## The Box Office Contradiction

None of this has dented the film's commercial performance. After ₹18.5 crore in paid previews and a ₹51 crore opening day, *Peddi* added ₹26.9 crore net on day two, bringing its India net total to ₹96.4 crore. The worldwide gross has crossed ₹150 crore. Advance bookings for Saturday already exceeded ₹13.87 crore gross with over five lakh tickets sold.

The Telugu market continues to drive the numbers — Andhra Pradesh and Telangana contributed ₹25 crore gross on day two alone. The Hindi version added ₹2.25 crore, while Tamil, Kannada, and Malayalam combined for under ₹0.5 crore.

## Why This Matters for the Diaspora

For NRI audiences, the debate has a particular charge. Many in the diaspora have watched Indian cinema evolve from the casual misogyny of the 1990s toward more progressive storytelling, and *Peddi* reads to some as a regression. The film is a multi-language release available in Telugu, Tamil, Hindi, Malayalam, and Kannada — meaning the portrayal is reaching the widest possible audience, including significant diaspora markets in the US, UK, and the Gulf.

The fact that a director is acknowledging the problem mid-run, rather than dismissing it as western sensibility or jealous trolling, is itself a development worth tracking. Whether the promised cuts actually materialise — and whether they arrive before the Netflix streaming window — will be the real test of whether the apology was contrition or crisis management.

## What Happens Next

*Peddi* still has the weekend to consolidate. With Saturday bookings pointing to a ₹30 crore-plus day, the film could cross ₹125 crore India net by Sunday. The creative conversation and the commercial trajectory are running on entirely separate tracks — which, depending on your perspective, is either the industry's oldest tension or its newest reckoning.

*Sources: SCREEN interview via News Dive, Bollywood Hungama, Sacnilk box office data, Filmibeat, Firstpost review, News18 review*"""

article1 = {
    "headline": "Peddi Director Buchi Babu Sana Has Apologised. He Has Also Promised to Cut Scenes.",
    "subheadline": "Two days after release, the filmmaker acknowledged the backlash over Janhvi Kapoor's portrayal and pledged changes while the film crossed ₹150 crore worldwide",
    "slug": "peddi-buchi-babu-apology-janhvi-kapoor-hypersexualisation-controversy-cuts-nri-20260606",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "vertical": "entertainment",
    "image_url": img1,
    "image_caption": caption1,
    "image_attribution": attr1,
    "body": body1,
    "sources": json.dumps([
        {"name": "SCREEN / News Dive", "url": "https://newsdive.net"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Firstpost", "url": "https://firstpost.com"}
    ])
}

if img1:
    insert_article_curl(article1)
else:
    print("  ✗ No image found, skipping")


# ============================================================
# ARTICLE 2: Drishyam 3 Hindi
# ============================================================
print("\n=== Article 2: Drishyam 3 Hindi Goes Its Own Way ===")

import time
time.sleep(2)
img2, attr2 = find_image(person_name="Ajay Devgn", pexels_query="Indian thriller mystery")

caption2 = "Ajay Devgn, who reprises his role as Vijay Salgaonkar in Drishyam 3"

body2 = """For the first time in its Hindi run, *Drishyam* is not a remake. It is a reimagining.

The first two Hindi instalments of the franchise — *Drishyam* (2015) and *Drishyam 2* (2022) — were faithful adaptations of Jeethu Joseph's Malayalam originals, down to their structural beats and emotional textures. The third will not be. Director Abhishek Pathak confirmed that the Hindi *Drishyam 3*, which wrapped shooting recently and is scheduled for release on October 2, 2026, has "drastically altered the plot and twists" from the Malayalam version that released on May 21.

"The Malayalam film is an emotional family drama, while ours is a family thriller," Pathak told Bollywood Hungama.

## New Additions, New Energy

The most significant change is in the cast. Jaideep Ahlawat and Prakash Raj join the returning ensemble of Ajay Devgn, Tabu, Shriya Saran, Akshaye Khanna, Ishita Dutta, Rajat Kapoor, and others. Both actors bring a specific kind of intensity that signals the film's tonal shift — Ahlawat's recent work in *Paatal Lok* and *An Action Hero* has made him one of Hindi cinema's most reliable antagonists, while Prakash Raj's career-long command of authority roles adds pan-Indian gravitas.

Trade sources say the additions are not cameos. "Jaideep Ahlawat and Prakash Raj have put up great acts," a source told Bollywood Hungama. "At the same time, Ajay Devgn, Tabu, Shriya Saran and others have once again delivered fine performances."

## The KGF Connection

In another departure, the franchise has brought in Ravi Basrur for the score. The composer behind *KGF*, *Salaar*, and *Marco* replaces Devi Sri Prasad, who scored *Drishyam 2* (Vishal Bhardwaj handled the first film). Basrur has worked with Devgn before, on *Bholaa* (2023) and *Singham Again* (2024), but his hiring here sends a clear signal: this *Drishyam* is louder, harder, and less interested in the quiet unease that defined the originals.

Each Hindi *Drishyam* has now had a different composer. The rotation has become an unintentional tradition — and a marker of how much the franchise reinvents itself with each chapter.

## The Stakes for October 2

The October 2 release date — Gandhi Jayanti, a national holiday — is prime real estate in the Bollywood calendar. *Drishyam 2* was one of the biggest Hindi hits of 2022, collecting over ₹342 crore worldwide and proving that Vijay Salgaonkar's cat-and-mouse game had become a genuinely beloved franchise. The third film carries the pressure of that success alongside the risk of diverging from the story that built it.

## Why the Diaspora Should Pay Attention

For NRI audiences who followed the Malayalam originals on OTT and then watched the Hindi versions theatrically, the break from source material introduces a new dynamic. You can watch both versions and get genuinely different stories — something no previous *Drishyam* cycle offered. The Malayalam *Drishyam 3*, which hit theatres on May 21, reportedly takes an emotional, family-centred route. The Hindi version, by contrast, appears to lean into the tension and paranoia that makes Vijay Salgaonkar a compelling protagonist in the first place.

Presented by Star Studios and produced under the Panorama Studios banner, *Drishyam 3* is written by Abhishek Pathak, Aamil Keeyan Khan, and Parveez Shaikh. The film arrives in cinemas on October 2, 2026.

*Sources: Bollywood Hungama exclusive, Sacnilk, BlazeeTrends, SAIndia Magazine*"""

article2 = {
    "headline": "Drishyam 3 Hindi Will Not Follow the Malayalam Film. Ajay Devgn's Version Is a Thriller Now.",
    "subheadline": "The franchise's first original Hindi script adds Jaideep Ahlawat and Prakash Raj, replaces the emotional drama with a family thriller, and brings KGF composer Ravi Basrur on board for October 2",
    "slug": "drishyam-3-hindi-different-from-malayalam-ajay-devgn-jaideep-ahlawat-ravi-basrur-nri-20260606",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "vertical": "entertainment",
    "image_url": img2,
    "image_caption": caption2,
    "image_attribution": attr2,
    "body": body2,
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "BlazeeTrends", "url": "https://blazetrends.com"},
        {"name": "SAIndia Magazine", "url": "https://saindiamagazine.com"}
    ])
}

if img2:
    insert_article_curl(article2)
else:
    print("  ✗ No image found, skipping")


# ============================================================
# ARTICLE 3: The Odyssey IMAX Ticket Frenzy
# ============================================================
print("\n=== Article 3: The Odyssey IMAX Frenzy ===")

time.sleep(2)
img3, attr3 = find_image(person_name="Christopher Nolan", pexels_query="movie theater cinema IMAX screen")

caption3 = "Christopher Nolan, director of The Odyssey" if img3 and "Nolan" in str(img3) else "An IMAX cinema auditorium"

body3 = """On June 4, AMC Theatres' ticketing system collapsed. Fandango queued users for hours. Regal went down. Kiosks at AMC Lincoln Square in New York — the legendary IMAX 70mm screen — were surrounded by lines that wrapped through the building. And on eBay, tickets for a single screening were being listed for $1,500.

The cause was not a concert or a sporting event. It was advance booking for a movie about a man trying to sail home from war — Christopher Nolan's *The Odyssey*.

## The Scale of the Frenzy

*The Odyssey*, based on Homer's ancient Greek epic, is the first feature film in cinema history shot entirely with IMAX cameras. That distinction alone has turned it into an event. But the combination of Nolan's track record — *Oppenheimer* earned $952 million worldwide — and a cast that includes Matt Damon, Tom Holland, Anne Hathaway, Zendaya, Robert Pattinson, Charlize Theron, and Lupita Nyong'o has created demand that outstrips any recent film release.

AMC's ticketing app had to be temporarily paused due to overwhelming traffic. Some fans reported hour-long waits before they could complete a purchase. On eBay, IMAX 70mm tickets for screenings in New York, Arizona, Florida, and Texas were being resold at $500 to $1,500 — prices more commonly associated with Taylor Swift concerts than cinema.

## India Enters the Race on June 8

Indian fans will get their shot starting June 8, when IMAX advance bookings open across participating theatres and ticketing platforms. Warner Bros. Discovery India confirmed the date, making Indian audiences among the first in the world to reserve seats alongside global Nolan fans.

"For the first time, Indian fans book their seats alongside the rest of the world, for the first film in history made entirely on IMAX cameras," said Denzil Dias, Vice President and Managing Director of Warner Bros. Discovery India.

The move reflects both IMAX's confidence in India's market and Nolan's outsized popularity in the country. *Oppenheimer* performed exceptionally well across Indian IMAX screens in 2023, and exhibitors expect *The Odyssey* to deliver an even larger event-level experience. The film opens in cinemas worldwide, including across India, on July 17, 2026.

## Why This Is an NRI Event

For the Indian diaspora, *The Odyssey* sits at the intersection of two cultural commitments — Hollywood spectacle and the communal theatre experience. NRI audiences in the US are already navigating the same crashed booking systems and inflated prices as everyone else. The India booking window opening on June 8 creates a parallel opportunity for family members back home to participate in the same opening-weekend event.

The film will be available in IMAX 70mm film, IMAX digital and laser, standard 70mm film, 35mm film, and digital large format. For viewers in cities with IMAX screens — Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, and several tier-two cities — the June 8 booking window is likely to see heavy traffic. *Oppenheimer* set the template; *The Odyssey* is testing whether that template has a ceiling.

## What Nolan Built

*The Odyssey* follows Odysseus (Matt Damon) on his perilous journey home to his wife Penelope (Anne Hathaway) after the fall of Troy. Tom Holland plays Telemachus. The film is produced by Emma Thomas and Christopher Nolan for Syncopy, distributed by Universal Pictures internationally and Warner Bros. Discovery in India.

The production used brand-new IMAX film technology developed specifically for this project. Nolan has pushed large-format filmmaking further with each release — from *The Dark Knight* to *Dunkirk* to *Oppenheimer* — but *The Odyssey* is the first to commit entirely to the format, with every frame captured on IMAX cameras.

Whether the film justifies $1,500 ticket prices remains to be seen. Whether the booking systems can handle June 8 in India is a more immediate question.

*Sources: Bollywood Hungama, Sacnilk, ZoomTV Entertainment, Gulte, Consequence, IndulgeExpress*"""

article3 = {
    "headline": "Nolan's The Odyssey Crashed AMC's Servers and Created a $1,500 Scalping Market. India Opens Bookings on June 8.",
    "subheadline": "The first film ever shot entirely on IMAX cameras has generated a global ticket frenzy, with Indian fans joining the race as advance sales launch this weekend",
    "slug": "christopher-nolan-the-odyssey-imax-india-booking-june-8-ticket-frenzy-nri-20260606",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "vertical": "entertainment",
    "image_url": img3,
    "image_caption": caption3,
    "image_attribution": attr3,
    "body": body3,
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "ZoomTV Entertainment", "url": "https://zoomtventertainment.com"},
        {"name": "Gulte", "url": "https://gulte.com"},
        {"name": "Consequence", "url": "https://consequence.net"},
        {"name": "IndulgeExpress", "url": "https://indulgexpress.com"}
    ])
}

if img3:
    insert_article_curl(article3)
else:
    print("  ✗ No image found, skipping")


print("\n=== Entertainment writer complete ===")
