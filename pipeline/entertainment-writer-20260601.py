#!/usr/bin/env python3
"""Entertainment writer — 3 articles for 2026-06-01"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

# --- env ---
from pathlib import Path
env_file = Path.home() / "workspace" / ".env.supabase"
for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import requests, urllib.parse

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 201):
        print(f"INSERT ERROR {r.status_code}: {r.text[:500]}")
        return None
    result = r.json()
    return result[0] if isinstance(result, list) else result

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 204):
        print(f"PATCH ERROR {r.status_code}: {r.text[:500]}")

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
    """Fetch image from Pexels API using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket article-images."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}) for {image_url[:80]}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return None

        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.put(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase storage: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def validate_image_url(url):
    """Validate that a URL returns a real image."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if "image" in ct:
            return True
    except:
        pass
    return False

# ===== ARTICLES =====

articles = []

# --- Article 1: Ramayana SDCC + October 30 release ---
articles.append({
    "headline": "Ramayana Is Heading to San Diego Comic-Con. Here's Why That Matters for Every NRI Waiting for Diwali.",
    "subheadline": "Nitesh Tiwari's ₹1,000-crore epic will share SDCC's stage with Avengers and Dune before a possible October 30 theatrical release — a week ahead of Diwali.",
    "slug": "ramayana-san-diego-comic-con-sdcc-trailer-october-30-release-ranbir-kapoor-nri-20260601",
    "category": "entertainment",
    "sources": "Sacnilk, Mid-day, Bollywood Hungama, Mykhel",
    "image_person": "Ranbir Kapoor",
    "body": """Nitesh Tiwari's Ramayana is no longer just a Bollywood film. It's a global campaign — and the next stop is Hall H at San Diego Comic-Con.

## The Comic-Con Play

According to multiple industry reports, producer Namit Malhotra and his team at Prime Focus Studios are in advanced talks with SDCC organisers to present Ramayana: Part 1 at the July 23-26 event. If confirmed, this would make Ramayana the first Indian film ever to receive a dedicated presentation at Comic-Con's main stage — sharing the spotlight with Marvel's Avengers: Doomsday and Denis Villeneuve's Dune 3.

The move follows an encouraging reception at CinemaCon 2026 in Las Vegas, where Malhotra and actor Yash personally hosted private previews for international distributors. Trade insiders report that the response has emboldened the team to treat Ramayana as a genuine global tentpole rather than a domestic-first release with international spillover.

Reports suggest the SDCC presentation could include the first official trailer or even Yash's much-anticipated first look as Ravana, both featuring upgraded VFX from the Oscar-winning DNEG studio that represents a significant leap from the initial teaser.

## The Release Date Shift

Simultaneously, Bollywood Hungama reports that the makers are now eyeing October 30, 2026, for the theatrical release — a full week before Diwali. The original plan was a Diwali-day release, but the new strategy aims to build strong word-of-mouth before the extended holiday period kicks in.

The logic is straightforward: arriving a week early gives the film an uncontested opening in a window free of major competition, followed by a massive second-week surge driven by holiday crowds. Internal discussions are reportedly underway, with the final decision hinging on distribution negotiations reportedly worth ₹450 crore.

## Why NRIs Should Care

For diaspora audiences who grew up with the Ramayana in every form — from Ramanand Sagar's television serial to Amar Chitra Katha comics to bedtime stories — this is a watershed moment. The film features a once-in-a-generation cast: Ranbir Kapoor as Lord Ram (plus a dual role as Lord Parashurama, which he accidentally confirmed in a Hollywood media interview), Sai Pallavi as Goddess Sita, Yash as Ravana, Sunny Deol as Hanuman, and Arun Govil — the original television Ram — as King Dasharatha.

The music alone justifies the excitement. A.R. Rahman and Hans Zimmer are collaborating on the score, and the makers are reportedly planning a live orchestral event in October to showcase the soundtrack before release.

Both parts will span over six hours of storytelling, with Part 2 already 50 percent shot and scheduled for Diwali 2027. The production budget exceeds ₹1,000 crore, making it the most expensive Indian film ever produced.

If the SDCC gambit works, NRI audiences in North America, the UK, and beyond will have experienced Ramayana's world months before opening day — transforming them from ticket buyers into evangelists. For a film built to be "India's Avatar for the global audience," as Malhotra himself has described it, that's exactly the strategy you'd want.

The trailer may not be the film. But at Comic-Con, it becomes the invitation.""",
})

# --- Article 2: Michael Jackson biopic India box office ---
articles.append({
    "headline": "The Michael Jackson Biopic Is the Second-Biggest Hollywood Film in India This Year. The Reason Is a 40-Year-Old Love Affair.",
    "subheadline": "Antoine Fuqua's 'Michael' has grossed ₹76.50 crore in India and is marching toward ₹80 crore — driven by South India and Mumbai audiences who grew up on the King of Pop.",
    "slug": "michael-jackson-biopic-india-box-office-76-crore-second-biggest-hollywood-nri-20260601",
    "category": "entertainment",
    "sources": "Bollywood Life, Pinkvilla, Sacnilk, Screen Rant",
    "image_person": "Michael Jackson",
    "body": """Michael Jackson has been gone for 17 years. His music never left India.

Antoine Fuqua's biopic *Michael*, starring Jaafar Jackson — the King of Pop's nephew who bears an almost unsettling resemblance to his uncle — has quietly become the second-biggest Hollywood grosser in India in 2026. At ₹76.50 crore after five weeks, it trails only Ryan Gosling's *Project Hail Mary* (₹85+ crore) and is expected to cross ₹80 crore shortly.

## The Numbers Tell a Story

What's remarkable isn't just the total — it's the hold. *Michael* dropped only 43-45 percent from Week 4 to Week 5, a number that most Bollywood films would envy by their third week. Here's the week-by-week breakdown:

- **Week 1**: ₹31.25 crore
- **Week 2**: ₹20.50 crore
- **Week 3**: ₹13.00 crore
- **Week 4**: ₹7.50 crore
- **Week 5**: ₹4.25 crore (estimated)

This is not the trajectory of a film powered by opening-weekend hype. This is a film powered by word-of-mouth — people watching it, telling others, and returning for the recreated concert sequences that Fuqua stages with meticulous devotion.

## Why India Connects

The business is concentrated in two regions: South India and Mumbai. That's not random. Michael Jackson's music — and more importantly, his movement — became cultural currency in India during the 1980s and 1990s in ways that went far beyond what happened in most of the West.

In South Indian cities, Jackson wasn't just a pop star. He was a dance revolution. Local dance competitions, college festivals, and talent shows in Chennai, Hyderabad, and Bengaluru featured MJ impersonators long before YouTube made the practice global. Mumbai, with its deep film-music culture and proximity to Bollywood choreography, absorbed Jackson's influence through a different channel — through Prabhu Deva, through Hrithik Roshan, through every second dance number that borrowed a moonwalk or a crotch-grab.

## The Diaspora Angle

For NRIs in the US, UK, and Canada, Jackson's cultural position is even more layered. Many grew up in two musical worlds simultaneously — Bollywood playback and Western pop — and Jackson sat at the intersection. He was the one Western artist that transcended the divide, equally at home in a car stereo in Edison, New Jersey, and at a wedding in Hyderabad.

Jaafar Jackson's performance has drawn universal praise even from critics who gave the film itself a middling 27 percent on Rotten Tomatoes. The resemblance is physical, vocal, and kinetic — and it's proving enough to bring both longtime fans and a younger generation into theatres.

## What Happens Next

With no major Hollywood competition in Indian theatres right now, *Michael* has room to keep earning. The question is whether it can overtake *Project Hail Mary*'s lifetime total. At its current pace of decline, ₹85 crore is within reach but not guaranteed.

What's already guaranteed is this: a biopic about an American musician, produced in Hollywood, earned more in India than most Hindi films released this year. Somewhere in that fact is everything you need to know about how deeply Jackson's legacy is woven into the Indian cultural fabric — and how eager audiences are for films that honour that legacy with care rather than caricature.""",
})

# --- Article 3: Gullak Season 5 ---
articles.append({
    "headline": "Gullak's Annu Bhaiya Has a New Face. Anant Joshi Steps In, and the Mishras Return on June 5.",
    "subheadline": "TVF's beloved small-town family drama returns for Season 5 on SonyLIV with a major cast change — and it's already the most emotionally loaded recasting in Indian streaming.",
    "slug": "gullak-season-5-anant-joshi-replaces-vaibhav-raj-gupta-sonyliv-june-5-nri-20260601",
    "category": "entertainment",
    "sources": "Zoom TV, Hauterrfly, Bollywood Life, Wikipedia",
    "image_person": "Anant Joshi",
    "body": """There are shows you watch. And then there are shows that feel like visiting your parents' house. Gullak is the second kind.

TVF's gentle, melancholic, frequently hilarious family drama returns for its fifth season on SonyLIV on June 5, bringing back the Mishra family — Santosh Papa, Shanti Mummy, little Aman — and all the cramped-house, middle-class North Indian energy that has made it one of India's most quietly adored streaming series.

But this time, there's a change that will hit harder than any plot twist the show has ever attempted: Annu Bhaiya has a new face.

## The Swap

Vaibhav Raj Gupta, who played Anand "Annu" Mishra for four seasons, is out. In his place is Anant Joshi — best known for *12th Fail* and TVF's own *Maamla Legal Hai*. The reason for Gupta's departure hasn't been officially disclosed, but reports suggest he exited before filming began on Season 5.

In an interview with Zoom TV, Joshi described his reaction to getting the call from TVF: "Are you sure?" He'd been watching Gullak as a fan and had always thought he and Gupta looked similar enough to play brothers someday. He never imagined he'd be playing the same brother.

The two haven't spoken. "We were never friends," Joshi said. "So I couldn't talk to him about the role that I'm undertaking." It's an honest, slightly melancholy admission that captures exactly the kind of emotional complexity Gullak specialises in.

## Why Gullak Matters — Especially for NRIs

If you've left India, you know the specific ache that Gullak is designed to locate. The show doesn't trade in melodrama or spectacle. Its currency is recognition: the sound of pressure cooker whistles marking dinner time, the passive-aggressive family arguments about electricity bills, the father's quiet pride when a son achieves something small, the mother's impossible talent for making scarcity feel like abundance.

For diaspora audiences streaming from apartments in New Jersey, Hounslow, or Brampton, Gullak is a portal. It's the closest thing to sitting in your parents' drawing room during a visit that never lasts long enough. The Mishras aren't aspirational. They're familiar. And that familiarity is the show's superpower.

Jameel Khan (Santosh Mishra), Geetanjali Kulkarni (Shanti Mishra), and Harsh Mayar (Aman Mishra) all return for the new season, along with Sunita Rajwar as the scene-stealing neighbour Bittu Ki Mummy. A new addition is Gopal Datt as Pinky Mama, who, based on promos, seems poised to create domestic chaos of the highest order.

## The Recast Challenge

Recasting a lead in an ensemble show is always risky. When the show is built on intimacy and specificity — when audiences don't just like the characters but feel related to them — the stakes multiply. Every shared glance between Santosh and Annu, every sibling dynamic between Annu and Aman, every frustrated-but-loving exchange carries muscle memory from four seasons of buildup.

Joshi seems aware of the weight. "What made me very sure was the creative team of TVF for Gullak," he said. "They are very sure, they are very aware because we are doing the fifth season." He credits the writers for how they've shaped the character in Season 5, suggesting the show may acknowledge the transition within its narrative rather than pretending nothing changed.

Seven episodes. The Mishras' cramped house. A new face in a beloved chair. June 5 on SonyLIV.

For diaspora audiences who measure their homesickness in Gullak episodes, the countdown has already begun.""",
})

# ===== PUBLISH =====

published_count = 0
now_ts = datetime.now(timezone.utc).isoformat()

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:60]}...")

    # Source image
    img_url = None
    img_attribution = None

    # Try Wikipedia for the person
    person = art.get("image_person")
    if person:
        wiki_url = fetch_wikipedia_person_image(person)
        if wiki_url:
            # Upload to Supabase storage for permanence
            fname = f"{art['slug']}.jpg"
            uploaded = upload_to_supabase_storage(wiki_url, fname)
            if uploaded:
                img_url = uploaded
                img_attribution = "Wikimedia Commons"

    # Fallback to Pexels if no Wikipedia image
    if not img_url:
        if "Ramayana" in art["headline"]:
            pexels_url = fetch_pexels_image("Hindu epic mythology temple", "ancient Indian mythology")
        elif "Michael Jackson" in art["headline"]:
            pexels_url = fetch_pexels_image("concert stage performance lights", "music concert crowd")
        elif "Gullak" in art["headline"]:
            pexels_url = fetch_pexels_image("Indian family living room", "middle class Indian home")
        else:
            pexels_url = fetch_pexels_image("Bollywood cinema India")

        if pexels_url:
            fname = f"{art['slug']}.jpg"
            uploaded = upload_to_supabase_storage(pexels_url, fname)
            if uploaded:
                img_url = uploaded
                img_attribution = "Pexels"

    # Build insert payload
    article_id = str(uuid.uuid4())
    payload = {
        "id": article_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "sources": art["sources"],
        "status": "published",
        "published_at": now_ts,
        "is_editorial": False,
    }

    payload["vertical"] = "entertainment"

    if img_url:
        payload["image_url"] = img_url
    if img_attribution:
        payload["image_attribution"] = img_attribution

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        print(f"    Image: {img_url or 'none'}")
        published_count += 1
    else:
        print(f"  ✗ FAILED: {art['slug']}")

    time.sleep(1)  # Brief pause between inserts

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} entertainment articles.")
