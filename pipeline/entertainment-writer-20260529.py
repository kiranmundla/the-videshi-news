#!/usr/bin/env python3
"""Entertainment writer for The Videshi - May 29, 2026 batch"""
import os, json, requests, urllib.parse, uuid, time, re
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

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
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Verify size
                    head = requests.head(url, timeout=5)
                    cl = int(head.headers.get("Content-Length", 0))
                    if cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Verify URL returns valid image."""
    if not url:
        return False
    try:
        # Check for banned sources
        banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', 'scontent-']
        if any(b in url for b in banned):
            print(f"  ❌ Banned image source: {url[:60]}")
            return False
        if '_nc_ht=' in url or '_nc_cat=' in url or 'ccb=' in url:
            print(f"  ❌ Signed Meta URL detected: {url[:60]}")
            return False
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        else:
            print(f"  ❌ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
            return False
    except Exception as e:
        print(f"  ❌ Image validation error: {e}")
        return False

def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
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
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✅ Published: {article['headline'][:60]}... (id: {art_id})")
            return art_id
    print(f"  ❌ Publish failed: {r.status_code} — {r.text[:200]}")
    return None

# ============================================================
# ARTICLES
# ============================================================

articles = []

# --- ARTICLE 1: Anik Dutta ---
print("\n📰 Article 1: Anik Dutta tribute")
print("  Sourcing image...")
img1 = fetch_wikipedia_person_image("Anik Dutta")
if not img1 or not validate_image_url(img1):
    img1 = fetch_wikipedia_person_image("Anik Dutta (filmmaker)")
    if not img1 or not validate_image_url(img1):
        # Try Bimal Roy since Anik was his grandnephew, or try Satyajit Ray
        img1 = fetch_pexels_image("Kolkata cinema hall theatre", "Bengali film industry Kolkata")
        if not validate_image_url(img1):
            img1 = None

articles.append({
    "headline": "Bengali Filmmaker Anik Dutta Is Dead at 66. He Reinvented Political Satire in Indian Cinema.",
    "subheadline": "The director of Bhooter Bhabishyat and Aparajito was found after falling from a Kolkata rooftop. Police recovered a suicide note. The Bengali diaspora has lost one of its sharpest voices.",
    "slug": "anik-dutta-dead-66-bengali-filmmaker-bhooter-bhabishyat-aparajito-nri-20260529",
    "image_url": img1,
    "image_attribution": "Wikimedia Commons" if img1 and "wikipedia" in (img1 or "").lower() or "wikimedia" in (img1 or "").lower() else "The Videshi",
    "sources": [
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "LatestLY / ANI", "url": "https://www.latestly.com"},
        {"name": "BlazesTrends", "url": "https://blazetrends.com"},
        {"name": "Kolkata Police / DCP Southeast Division", "url": ""}
    ],
    "body": """Anik Dutta, the Bengali filmmaker who turned political satire into a commercially viable art form, died on May 27 in Kolkata after falling from the rooftop of a six-storey residential building in the city's Hindustan Park neighbourhood. He was 66.

Kolkata Police found a handwritten note on the terrace addressed to his daughter, who lives abroad, stating that no one was responsible for his death. A pair of sandals and a copy of *Cinematography Art* magazine were found alongside it. The Deputy Commissioner of Police (Southeast) confirmed the recovery and said an unnatural death case has been initiated. His body was taken to SSKM Hospital for post-mortem examination.

## A New Language for Bengali Cinema

Dutta came to filmmaking late, spending two decades in the advertising industry before picking up the director's chair. His debut feature, *Bhooter Bhabishyat* (2012), became an instant cultural phenomenon — a supernatural comedy-satire that mixed ghosts from different eras of Bengali history into a single crumbling mansion. The film earned over ₹10 crore at the box office on a modest budget and created a new template for commercially successful political commentary in Bengali cinema.

What made Dutta distinctive was his refusal to separate entertainment from critique. His ghosts debated colonial history, his comedies contained sharp observations about Bengali cultural anxieties, and his satires landed with the precision of someone who had spent decades studying how people respond to stories in 30-second commercial spots.

## Seven Films, One Uncompromising Voice

Over 14 years, Dutta directed seven feature films: *Bhooter Bhabishyat* (2012), *Aschorjo Prodip* (2013), *Meghnad Badh Rahasya* (2017), *Bhobishyoter Bhoot* (2019), *Borunbabur Bondhu* (2020), *Aparajito* (2022), and *Joto Kando Kolkatatei* (2025).

*Bhobishyoter Bhoot* — a sharp political satire featuring ghosts who face censorship — was pulled from theatres within days of its 2019 release in a controversy that many saw as politically motivated. The incident became a landmark moment in debates about artistic freedom in West Bengal.

*Aparajito*, released in 2022, told the story of the making of Satyajit Ray's iconic *Pather Panchali*. It earned widespread critical acclaim and multiple awards, cementing Dutta's reputation as a filmmaker deeply invested in Bengali cinema's legacy while remaining fiercely contemporary.

## The Diaspora Connection

For the Bengali diaspora scattered across the United States, United Kingdom, Canada, and beyond, Dutta's films served as a particular kind of cultural mirror. *Bhooter Bhabishyat* became a staple at NRI film screenings and Bengali community events. His work captured the specific rhythms, humour, and social anxieties of contemporary Kolkata in a way that felt intimate to those who had left the city but never quite stopped belonging to it.

## "A Big Loss"

West Bengal Chief Minister Suvendu Adhikari called Dutta's contributions to Bengali cinema "priceless" and asked Kolkata Police to investigate the circumstances of his death. Actor and BJP leader Rudranil Ghosh said Dutta "still had so much more to give" and praised his films for being celebrated both domestically and internationally.

Director Aditya Sarpotdar, Dutta's colleagues across the Tollygunge industry, and figures from the advertising world where he spent his formative years all posted tributes through the evening.

Dutta was the grandson of Narendra Chandra Dutta, the founder of United Bank of India, and a grandnephew of legendary filmmaker Bimal Roy. He was deeply influenced by Satyajit Ray's filmmaking style and, like Ray, began his creative career in advertising before transitioning to cinema.

His last rites are pending the arrival of his daughter from abroad. He is survived by his daughter and estranged wife, Sandhi Dutta.

*If you or someone you know is struggling, reach out to a mental health professional. In the US, contact the 988 Suicide and Crisis Lifeline by calling or texting 988. In India, call iCall at 9152987821 or AASRA at 9820466726.*"""
})

# --- ARTICLE 2: Shakti Shalini wraps ---
print("\n📰 Article 2: Shakti Shalini wraps")
print("  Sourcing image...")
img2 = fetch_wikipedia_person_image("Nana Patekar")
if not img2 or not validate_image_url(img2):
    img2 = fetch_pexels_image("Rajasthan village India", "Indian film set production")
    if not validate_image_url(img2):
        img2 = None

articles.append({
    "headline": "Maddock's Next Horror Film Just Wrapped. It Has Nana Patekar, a Double Role, and a Rajasthani Village Built From Scratch.",
    "subheadline": "Shakti Shalini completed filming on May 27 after shoots across Chambal, Rajasthan, and a massive climax set in Mumbai. Aneet Padda plays both the hero and the ghost.",
    "slug": "shakti-shalini-maddock-horror-comedy-wraps-aneet-padda-nana-patekar-nri-20260529",
    "image_url": img2,
    "image_attribution": "Wikimedia Commons" if img2 and ("wikipedia" in (img2 or "").lower() or "wikimedia" in (img2 or "").lower()) else "The Videshi",
    "sources": [
        {"name": "Mid-Day", "url": "https://www.mid-day.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "CineTalkers", "url": "https://cinetalkers.com"},
        {"name": "Box Office Worldwide", "url": "https://boxofficeworldwide.com"}
    ],
    "body": """The Maddock Horror Comedy Universe — the franchise machine behind *Stree*, *Bhediya*, *Munjya*, and *Thamma* — has its next film locked and loaded. *Shakti Shalini* officially wrapped production on May 27 at Chitrarth Studio in Powai, Mumbai, after an intensive shooting schedule that stretched across Rajasthan, Madhya Pradesh, and multiple Mumbai sets.

Director Aditya Sarpotdar, who helmed both *Munjya* and the Ayushmann Khurrana-starrer *Thamma*, called wrap on the final schedule — a large-scale climax sequence featuring massive sets depicting a Rajasthani village, complete with detailed house interiors and a scene described as the village's women celebrating the defeat of evil.

## The Boldest Casting Bet in the Universe

At the centre of *Shakti Shalini* is a gamble: newcomer Aneet Padda in a demanding double role. She plays Shakti, an ordinary woman who becomes a protector, and Shalini, a vengeful spirit driven to target men after being betrayed and murdered. The film's central dramatic arc builds toward a confrontation between the two personas — effectively making Padda the hero and the villain of the same story.

Padda, who first gained attention for her performance in Mohit Suri's *Saiyaara* (2025), is stepping into a franchise that has turned relatively unknown actors into household names. Rajkummar Rao became a bigger star after *Stree*. Varun Dhawan found a new audience through *Bhediya*. Sharvari broke out with *Munjya*. The pattern is consistent: Maddock picks actors with range and gives them the kind of roles mainstream Bollywood rarely offers.

## Veterans on the Set

Veteran actor Nana Patekar and acclaimed actress Seema Biswas joined the cast in May, adding considerable weight to an ensemble that also includes Vishal Jethwa and Viineet Kumar Singh. Singh, who plays the film's antagonist, shot crucial scenes with Padda across the outdoor schedules.

According to production insiders, the antagonist's character is described as "dark and gritty" — a departure from the lighter comedic villains the franchise has occasionally deployed.

## A Shoot Across India's Heartland

Production began in March and moved at a rapid pace across some of India's most visually striking and historically layered landscapes. The principal cast filmed key sequences in Chambal, Datia, Antri, Panihar, Gwalior, and Morena in Madhya Pradesh, followed by shoots in Dholpur and Barkhandi in Rajasthan.

The choice of location is deliberate. Where previous Maddock horror films drew from Maharashtra's Konkan region (*Stree*, *Munjya*) or Arunachal Pradesh (*Bhediya*), *Shakti Shalini* is rooted in Rajasthan's folklore traditions — a region rich with stories of women warriors, supernatural protectors, and village-level myths that have been passed down for centuries.

## What It Means for the Franchise

The Maddock Horror Comedy Universe is now Bollywood's most commercially consistent franchise. *Stree 2* crossed ₹600 crore worldwide. *Thamma* was a clean hit for Ayushmann Khurrana. The shared universe model — where characters, supernatural entities, and locations interconnect across films — has given Maddock a Marvel-adjacent blueprint that no other Indian studio has replicated at this scale.

*Shakti Shalini* moves into post-production immediately. While no release date has been announced, industry sources expect a theatrical debut in the first half of 2027. With Maddock's track record of tight turnaround times between wrap and release, a late 2026 surprise isn't entirely off the table either.

For the Indian diaspora, the Maddock horror comedies have become a unique theatrical event — the kind of Hindi films that reliably draw audiences to NRI screenings because they're genuinely entertaining, culturally rooted, and don't require familiarity with the latest Bollywood gossip cycle to enjoy."""
})

# --- ARTICLE 3: Jee Le Zaraa ---
print("\n📰 Article 3: Jee Le Zaraa moving forward")
print("  Sourcing image...")
img3 = fetch_wikipedia_person_image("Farhan Akhtar")
if not img3 or not validate_image_url(img3):
    img3 = fetch_wikipedia_person_image("Priyanka Chopra")
    if not img3 or not validate_image_url(img3):
        img3 = fetch_pexels_image("Rajasthan desert road trip India", "women road trip India")
        if not validate_image_url(img3):
            img3 = None

articles.append({
    "headline": "Farhan Akhtar Has Shelved Don 3. He's Scouting Rajasthan for Jee Le Zaraa Instead.",
    "subheadline": "After Ranveer Singh walked out of Don 3 and got banned by FWICE, Farhan is pivoting to his dream project — a road trip film starring Priyanka Chopra, Alia Bhatt, and Katrina Kaif. The shoot could start in the second half of 2026.",
    "slug": "farhan-akhtar-jee-le-zaraa-priyanka-alia-katrina-don-3-shelved-nri-20260529",
    "image_url": img3,
    "image_attribution": "Wikimedia Commons" if img3 and ("wikipedia" in (img3 or "").lower() or "wikimedia" in (img3 or "").lower()) else "The Videshi",
    "sources": [
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"}
    ],
    "body": """The Don franchise is officially on hold. Filmmaker Farhan Akhtar has decided to step away from *Don 3* and redirect his energy toward *Jee Le Zaraa*, the long-delayed road trip film starring Priyanka Chopra, Alia Bhatt, and Katrina Kaif.

According to multiple reports, Akhtar shared a photograph on social media from the Rajasthan desert with the caption "Searching for gold" — a clear signal that location scouting for *Jee Le Zaraa* is underway. The script, written by Zoya Akhtar, Farhan Akhtar, and Reema Kagti, has been locked for some time. The only obstacle has been coordinating the schedules of three of Bollywood's biggest female stars.

## Why Don 3 Fell Apart

The *Don 3* implosion has been one of 2026's most dramatic Bollywood stories. Ranveer Singh was announced as the new face of the franchise — stepping into a role previously owned by Shah Rukh Khan — and production was set to begin in early 2026. Then Singh abruptly exited the project, reportedly because he didn't want to do back-to-back gangster films after the massive success of *Dhurandhar*.

The fallout was severe. Excel Entertainment, Farhan's production banner with Ritesh Sidhwani, had already invested heavily in pre-production. The Federation of Western India Cine Employees (FWICE) issued a non-cooperation directive against Singh. Salman Khan personally intervened to broker peace between the actor and filmmaker. Reports suggest producers are seeking damages of ₹40-45 crore.

Rather than rush the casting process to find a replacement for Singh, Akhtar has decided to put *Don 3* on ice entirely and pursue the project he's been trying to make for five years.

## Five Years of "It's Happening Soon"

*Jee Le Zaraa* was first announced in August 2021 with considerable fanfare. Priyanka Chopra, Alia Bhatt, and Katrina Kaif would star in a female-led road trip film — the spiritual successor to *Dil Chahta Hai* (2001) and *Zindagi Na Milegi Dobara* (2011), two of the most beloved Indian films among the global diaspora.

The project was supposed to start filming in 2022. It didn't. Schedule conflicts, life events (Katrina's marriage to Vicky Kaushal, Alia's pregnancy, Priyanka's Hollywood commitments), and shifting industry dynamics kept pushing the start date. Reports periodically surfaced suggesting the film was shelved, only to be contradicted by statements from one of the three leads or the Akhtar family.

Alia Bhatt told *The Lallantop* in late 2024 that aligning dates was "demanding" but that everyone involved was willing to make it happen. Priyanka Chopra, when pressed in a *Hindustan Times* interview, simply said: "You will need to speak to Excel about that." Farhan himself acknowledged the delay created "insecurities" and admitted he worried he was "squandering time."

## Why It Matters Now

The Don 3 disaster may have actually liberated *Jee Le Zaraa*. With the franchise parked indefinitely, Farhan's calendar is clear. More importantly, the film's emotional pitch — three women, one road trip, the freedom of unscripted adventure — has only become more resonant as the stars have aged into the roles.

In 2021, a Priyanka-Alia-Katrina road trip felt like a marketing dream. In 2026, after each has navigated motherhood, career pivots, Hollywood crossovers, and the relentless scrutiny of Indian tabloid culture, the same premise carries genuine emotional weight. These aren't ingenues anymore. They're women with complicated public lives who rarely get to be on screen together.

If dates align, filming could begin in the second half of 2026, with a theatrical release sometime in 2027. The film will be produced by Reema Kagti, Zoya Akhtar, Ritesh Sidhwani, and Farhan Akhtar under their Tiger Baby and Excel Entertainment banners.

## The NRI Factor

For the Indian diaspora, *Jee Le Zaraa* sits in a very specific emotional category. *Dil Chahta Hai* and *ZNMD* are among the most-watched Bollywood films at NRI gatherings, road trip playlists, and nostalgia events. A female-led addition to that lineage — from the same filmmaker — would almost certainly become one of the biggest diaspora theatrical events of whatever year it finally releases.

The key word, as it has been for half a decade, remains "finally.""""
})

# ============================================================
# PUBLISH ALL
# ============================================================
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i} ---")
    word_count = len(article["body"].split())
    print(f"  Title: {article['headline'][:70]}...")
    print(f"  Slug: {article['slug']}")
    print(f"  Words: {word_count}")
    print(f"  Image: {'✓' if article.get('image_url') else '✗ No image'}")
    
    if word_count < 400:
        print(f"  ❌ SKIPPED: Body too short ({word_count} words, need 400+)")
        continue
    
    if len(article["headline"]) > 200:
        print(f"  ⚠ Headline too long ({len(article['headline'])} chars), truncating")
        article["headline"] = article["headline"][:197] + "..."
    
    if len(article.get("subheadline", "")) < 15:
        print(f"  ❌ SKIPPED: Subheadline too short")
        continue
    
    art_id = publish_article(article)
    if art_id:
        print(f"  Published with ID: {art_id}")
    
    time.sleep(1)  # Brief pause between publishes

print("\n✅ Entertainment writer batch complete!")
