#!/usr/bin/env python3
"""Entertainment writer — 2026-06-02 batch"""

import os, json, requests, urllib.parse, time, uuid, re
from datetime import datetime, timezone

# ── env ──
env_file = os.path.expanduser("~/workspace/.env.supabase")
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── helpers ──

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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
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
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download an image and upload to Supabase storage bucket article-images."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed ({r.status_code}): {image_url[:80]}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image ({content_type}): {image_url[:80]}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes): {image_url[:80]}")
            return None

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            data=r.content,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article to Supabase p2_articles."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Article inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def patch_article(art_id, updates):
    """Patch an existing article."""
    r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art_id}",
        headers=HEADERS,
        json=updates,
        timeout=15
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched article {art_id}")
    else:
        print(f"  ⚠ Patch failed ({r.status_code}): {r.text[:200]}")


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: IMAX Returns to Hyderabad
# ═══════════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 1: IMAX Returns to Hyderabad ===")

art1 = {
    "headline": "Hyderabad Gets IMAX Back After a Decade. Mahesh Babu's AMB Cinemas Sealed the Deal.",
    "subheadline": "Three new IMAX with Laser screens are coming to Tollywood's home base — just in time for Rajamouli's Varanasi. NRIs who grew up watching Telugu blockbusters at Prasads should pay attention.",
    "slug": "imax-returns-hyderabad-amb-cinemas-mahesh-babu-decade-rajamouli-varanasi-nri-20260602",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "IMAX Corporation / Business Wire", "url": "https://www.businesswire.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Gulte", "url": "https://gulte.com"},
        {"name": "IndiaGlitz", "url": "https://www.indiaglitz.com"}
    ]),
    "body": """For more than a decade, Hyderabad — the beating heart of Telugu cinema, home to filmmakers who build ₹500-crore spectacles and audiences who fill 1,000-seat theatres on a Tuesday afternoon — has not had a single IMAX screen.

That drought ends this year.

On June 1, IMAX Corporation announced a partnership with Asian Cinemas to install three new IMAX with Laser screens through the AMB Cinemas brand. Two of the three will be in Hyderabad. The first, at AMB Classic on the historic grounds of the Sudarshan 70mm Theatre, is set to open before December 2026. The remaining two locations are planned for 2028.

## The Backstory: How Hyderabad Lost Its IMAX

The city's previous IMAX venue — the legendary Prasads IMAX, once among the first IMAX theatres in all of India — stopped operating in the proprietary format around 2015. For a city that produces some of the most visually ambitious films in the world, the absence was glaring.

S.S. Rajamouli said as much publicly. During a recent promotional event for his upcoming globe-trotting epic Varanasi, the RRR and Baahubali director expressed disbelief that Hyderabad — the city where Tollywood's biggest productions are born — lacked a premium large-format screen. The timing of the IMAX announcement, just ahead of Varanasi's release, feels almost poetic.

## Mahesh Babu's AMB Cinemas: The Vehicle

AMB Cinemas is a luxury multiplex chain co-owned by superstar Mahesh Babu along with the Asian Group's Sunil Narang and Bharat Narang. The brand has a track record of firsts: South India's first Dolby Cinema screen and one of Hyderabad's earliest HDR by Barco screens.

For the new IMAX installation, the group has also brought in Venkatesh Daggubati and Rana Daggubati as partners — effectively assembling Telugu cinema's most powerful exhibition consortium.

"Hyderabad's appetite and love for cinema is unparalleled," said the Narangs in a joint statement. "Bringing back the prestigious IMAX format is a matter of great honour and pride for AMB Cinemas."

Rich Gelfond, CEO of IMAX, noted that 2025 was the company's best year ever at the Indian box office. "India is home to a vibrant cinema culture of innovative filmmakers and passionate audiences, all of whom are clamoring for more of The IMAX Experience."

## What This Means for NRI Audiences

For the Telugu diaspora in the US, UK, and the Gulf, movie-watching trips to Hyderabad have long been part of the homecoming ritual. The absence of IMAX meant that Telugu blockbusters designed for the largest screens — from Pushpa to Salaar to the upcoming Varanasi — could only be experienced in their intended IMAX format in cities like Mumbai, Bengaluru, or overseas.

That changes now. When NRIs fly home for Sankranti or Dasara, the biggest Telugu films will finally be available on the screen format they were designed for, in the city where they were made.

## The Bigger Picture

The deal reflects a broader shift in Indian exhibition. Regional films now consistently outperform at the domestic box office, and premium formats like IMAX, Dolby Cinema, and ScreenX are no longer luxuries — they're how studios maximize returns on ₹200-crore productions.

With Rajamouli's Varanasi, the upcoming Kalki 2, and a pipeline of large-canvas Telugu productions, Hyderabad's three new IMAX screens arrive at exactly the moment the market demands them.

The Sudarshan 70mm Theatre location adds an emotional layer. For generations, the venue was where Telugu audiences experienced landmark film releases and wild fan celebrations. Now it becomes the site of Hyderabad's IMAX renaissance, a bridge between the old cinema and the new.

The first screen opens before the end of 2026. Telugu cinema's biggest filmmakers now have the biggest screen in their own backyard."""
}

# Image: Try IMAX or Mahesh Babu from Wikipedia, fall back to Pexels
img1 = fetch_wikipedia_person_image("Mahesh Babu")
if not img1:
    img1 = fetch_pexels_image("IMAX theater cinema", "movie theater screen")
art1_id = insert_article(art1)
if art1_id and img1:
    fn1 = f"{art1_id}.jpg"
    final1 = upload_image_to_supabase(img1, fn1)
    if final1:
        patch_article(art1_id, {"image_url": final1, "image_attribution": "Wikimedia Commons"})

time.sleep(1)

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Varun Dhawan Delhi HC - AI Deepfakes
# ═══════════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 2: Varun Dhawan Delhi HC Personality Rights ===")

art2 = {
    "headline": "The Delhi High Court Just Told Google, Meta, and X to Hand Over Data on Varun Dhawan's Deepfake Creators.",
    "subheadline": "In a landmark ruling on celebrity personality rights in the AI age, Justice Jyoti Singh ordered a sweeping injunction against deepfakes, fake merchandise, and unauthorized use of Dhawan's persona. The precedent reaches far beyond one actor.",
    "slug": "varun-dhawan-delhi-hc-personality-rights-ai-deepfakes-google-meta-x-nri-20260602",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
        {"name": "ANI / LatestLY", "url": "https://www.latestly.com"},
        {"name": "IANS / Asia Post", "url": "https://asiapost.in"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"}
    ]),
    "body": """Varun Dhawan went to court over something that no amount of box-office success can fix: strangers were using artificial intelligence to put his face into pornographic videos, slapping his name on merchandise he never endorsed, and running fake booking websites that claimed they could hire him for events.

On May 29, Justice Jyoti Singh of the Delhi High Court granted one of the most sweeping personality-rights injunctions in Indian legal history.

## What the Court Ordered

The ruling restrains multiple categories of defendants — websites, e-commerce platforms, social media accounts, and unidentified "John Doe" entities — from exploiting Dhawan's name, image, voice, likeness, or any identifiable element of his persona without authorization. The restraint explicitly covers artificial intelligence, generative AI, machine learning, deepfakes, AI chatbots, and face-morphing technologies.

The specifics are striking. The court:

- **Banned AI-generated deepfakes** portraying Dhawan in inappropriate scenarios with female co-stars
- **Blocked unauthorized merchandise sales** using his name, image, and registered trademarks
- **Shut down fake booking agencies** falsely claiming to represent him for events and performances
- **Ordered Google, Meta Platforms, and X Corporation** to hand over Basic Subscriber Information (BSI) of the infringing social media users
- **Set a 36-hour takedown window**: social media platforms must remove any new infringing content within 36 hours of being notified by Dhawan's team

"Plaintiff is entitled to protection against dissemination of pornographic content as well as AI-generated images portraying him in an inappropriate scenario," Justice Singh wrote. "Such distasteful content is harming and damaging the reputation of the Plaintiff and may mislead the public into believing what is depicted may be true."

## Following Naga Chaitanya's Footsteps

Dhawan's suit lands weeks after Telugu actor Naga Chaitanya secured a similar order from the same court over AI deepfakes linked to allegations involving his ex-wife Samantha Ruth Prabhu. The two cases together signal that Indian courts are rapidly building a body of law around AI-generated celebrity exploitation — a legal framework that barely existed two years ago.

Senior Advocate Sandeep Sethi, representing Dhawan, argued that the actor's personality traits carry significant commercial value and that unauthorized exploitation causes both reputational harm and financial loss. The court agreed, noting that Dhawan is a "celebrated Hindi film actor with a career spanning over 14 years" whose distinctive characteristics — name, signature, voice, likeness — are uniquely associated with him and "constitute valuable personality and publicity rights deserving legal protection."

## Why the NRI Community Should Watch This

For the Indian diaspora, the implications go beyond Bollywood gossip. Deepfake technology is global. The tools used to create non-consensual AI content featuring Indian celebrities are the same tools being used against ordinary people — including NRIs — on platforms accessible from any country.

India's courts are now establishing that personality rights in the digital age extend to AI-generated content, that platforms have enforceable obligations to remove such content quickly, and that creators of deepfakes can be identified through court-ordered data disclosures.

As AI-generated content proliferates across social media, these rulings create a legal playbook that Indian citizens — including those living abroad — can point to when their own likenesses are weaponized.

## The Broader Legal Landscape

The Dhawan ruling joins a growing list of Indian court interventions on celebrity AI rights. Anil Kapoor secured a similar order in 2023 protecting his persona from AI misuse. Amitabh Bachchan has long held personality-rights protections through prior court orders. But the Dhawan and Naga Chaitanya cases are among the first to specifically address generative AI deepfakes and mandate platform-level data disclosure.

The case is listed for further hearing. The interim order remains in effect until then.

For Indian celebrities and ordinary citizens alike, the message from Justice Singh's courtroom is clear: your face is yours, even in the age of artificial intelligence."""
}

img2 = fetch_wikipedia_person_image("Varun Dhawan")
art2_id = insert_article(art2)
if art2_id and img2:
    fn2 = f"{art2_id}.jpg"
    final2 = upload_image_to_supabase(img2, fn2)
    if final2:
        patch_article(art2_id, {"image_url": final2, "image_attribution": "Wikimedia Commons"})

time.sleep(1)

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Welcome to the Jungle
# ═══════════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 3: Welcome to the Jungle ===")

art3 = {
    "headline": "Welcome to the Jungle Has 30 Stars, a Late Actor's Final Role, and Bollywood's Most Unhinged Comedy Franchise. It Opens June 26.",
    "subheadline": "The third Welcome film reunites Akshay Kumar, Suniel Shetty, and Paresh Rawal in a jungle-set dark comedy that took three years to make. For NRIs who grew up quoting the original, this is the most nostalgic release of the summer.",
    "slug": "welcome-to-the-jungle-akshay-kumar-30-stars-june-26-franchise-nri-20260602",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com"}
    ]),
    "body": """If you grew up in an NRI household in the 2000s, there is a non-zero chance that someone in your family can recite entire scenes from Welcome (2007) by heart. The Nana Patekar-Anil Kapoor crime comedy became a cultural touchstone — the kind of film that plays on loop during Diwali parties and family gatherings, where "Uday bhai" and "Majnu bhai" are not characters but permanent inside jokes.

Nineteen years later, the franchise is back. Welcome to the Jungle releases worldwide on June 26, 2026, and it arrives with the largest ensemble cast assembled for a Hindi comedy in recent memory.

## The Cast: 30 Stars and Counting

Director Ahmed Khan has assembled what might be Bollywood's most ambitious comedy lineup. The headliners: Akshay Kumar, Suniel Shetty, Sanjay Dutt, Arshad Warsi, Paresh Rawal, and Jackie Shroff. The supporting ensemble reads like a who's-who of Hindi cinema: Raveena Tandon, Lara Dutta, Disha Patani, Jacqueline Fernandez, Johnny Lever, Tusshar Kapoor, Shreyas Talpade, Rajpal Yadav, Aftab Shivdasani, Krushna Abhishek, Kiku Sharda, Vindu Dara Singh, Mukesh Tiwari, Yashpal Sharma, and Daler Mehndi in a special role.

Suniel Shetty is reprising his iconic "Yeda Anna" character from Awara Paagal Deewana, creating an unexpected franchise crossover within the same film. Director Khan described his dynamic with Akshay Kumar and Arshad Warsi as "great banter that takes the fun and chaos a notch higher."

The film also carries emotional weight. The late actor Pankaj Dheer, who passed away earlier this year after decades in film and television, appears in Welcome to the Jungle in his final on-screen role.

## What Kind of Comedy Is This?

Not what you might expect. Ahmed Khan has been clear that Welcome to the Jungle diverges from the franchise's slapstick roots. "It's a black dark situational humour," he told Pinkvilla. "It's not a comedy. Firoz Nadiadwala believes in dark humour and situational humour. And of course, it's serious cinema: not a comedy or slapstick."

Set against a jungle backdrop, the film trades the original's urban gangster world for a wilder, more absurd premise. The teaser, dropped without announcement on May 15, was packed with over-the-top comedic situations that immediately went viral. JioStar has acquired the domestic theatrical, satellite, and OTT rights, meaning the film will stream on JioHotstar after its theatrical run.

## The Production Saga

Welcome to the Jungle had a turbulent path to the screen. Production began in 2024 but was halted midway, and the project was reportedly at risk of being shelved entirely. Shooting resumed in November 2025, with a final 15-day schedule in early 2026 wrapping up the remaining portions. Producer Firoz Nadiadwala stayed committed throughout, and the June 26 release date has held firm.

The budget is reported at a massive scale, befitting a franchise that grossed over ₹200 crore with its first two installments combined. With Akshay Kumar coming off the hit Bhooth Bangla and the franchise's built-in nostalgia factor, trade circles are projecting a major opening weekend.

## Why This Matters for the Diaspora

The original Welcome was not just a Bollywood hit — it was an NRI phenomenon. The film's outrageous humour, quotable dialogues, and ensemble energy made it a staple at Indian community events, university cultural nights, and family watch-alongs across the US, UK, Canada, and the Gulf. Welcome Back (2015) attempted to recapture that energy with a different cast and had a mixed reception.

Welcome to the Jungle brings back the franchise's original DNA — Akshay Kumar, Suniel Shetty, and Paresh Rawal — while adding enough new faces to keep it fresh. For a generation of NRIs now in their 30s and 40s, this is less a movie and more a reunion.

The film opens June 26 worldwide. Expect premiere shows across North America and the UK to fill up fast."""
}

img3 = fetch_wikipedia_person_image("Akshay Kumar")
art3_id = insert_article(art3)
if art3_id and img3:
    fn3 = f"{art3_id}.jpg"
    final3 = upload_image_to_supabase(img3, fn3)
    if final3:
        patch_article(art3_id, {"image_url": final3, "image_attribution": "Wikimedia Commons"})

print("\n=== All articles published ===")
