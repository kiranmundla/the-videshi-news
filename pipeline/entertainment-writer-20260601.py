#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-01 batch"""

import json, os, re, sys, time, uuid, traceback
import requests, urllib.parse
from datetime import datetime, timezone

# === Load Supabase config ===
env_path = os.path.expanduser("~/workspace/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# === Load Pexels key ===
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                "-H", f"Authorization: {PEXELS_KEY}",
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


def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't support HEAD, try GET with range
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)", "Range": "bytes=0-10000"})
        ct2 = r2.headers.get("Content-Type", "")
        if r2.status_code in (200, 206) and "image" in ct2:
            chunk = r2.content
            if len(chunk) > 5000:
                print(f"  ✓ Image validated (GET fallback): {len(chunk)} bytes")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert article into Supabase."""
    sources_list = article.get("sources", [])
    sources_str = ", ".join(sources_list) if isinstance(sources_list, list) else str(sources_list)
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
        "sources": sources_str,
        "is_editorial": False,
    }
    # Remove None image
    if not payload["image_url"]:
        del payload["image_url"]
        del payload["image_attribution"]

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {aid})")
        return True
    else:
        print(f"  ✗ Publish failed ({r.status_code}): {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: Bhooth Bangla Netflix OTT + Record-Breaking Run
# ============================================================
print("\n=== Article 1: Bhooth Bangla Netflix OTT ===")

art1_headline = "Bhooth Bangla Lands on Netflix June 12 After Surpassing Bhool Bhulaiyaa 2's Worldwide Record"
art1_subheadline = "Akshay Kumar and Priyadarshan's horror-comedy crossed ₹265 crore globally in 45 days. Now it's coming to your living room — and for NRIs who missed the theatrical run, it's the most anticipated OTT drop of the month."
art1_slug = "bhooth-bangla-netflix-ott-june-12-265-crore-record-akshay-kumar-nri-20260601"

art1_body = """Akshay Kumar's comeback story just got its final punctuation mark. **Bhooth Bangla**, the horror-comedy that reunited him with director Priyadarshan after a 16-year gap, will premiere on Netflix on **June 12, 2026** — and it arrives not as a quiet OTT transition, but as a bonafide box office champion.

As of its seventh weekend in theatres, the film has crossed **₹265 crore worldwide**, overtaking Kartik Aaryan's Bhool Bhulaiyaa 2 (₹265.50 crore lifetime) to become the highest-grossing horror-comedy in Indian cinema history. The India net stands at **₹178 crore**, with overseas contributing a healthy share — driven in large part by diaspora audiences in North America, the UK, and the Gulf.

## The Reunion That Worked

The Kumar-Priyadarshan partnership has always been Bollywood's most reliable comedy engine. From **Hera Pheri** to **Garam Masala** to the original **Bhool Bhulaiyaa**, their films defined a generation of rewatchable Hindi cinema. Bhooth Bangla picks up that thread with a story about Arjun Acharya, a financially struggling man in London who inherits a supposedly haunted palace in small-town India.

The supporting cast reads like a who's-who of Priyadarshan's comic universe: **Paresh Rawal**, **Rajpal Yadav**, **Tabu**, **Wamiqa Gabbi**, **Jisshu Sengupta**, and the late **Asrani** — whose appearance in the film carries an unspoken emotional weight given his passing earlier this year. The film's London-to-India setup resonated particularly with NRI viewers, many of whom saw their own inheritance dramas refracted through the horror-comedy lens.

## Why NRIs Should Care About the Netflix Drop

For diaspora audiences who couldn't catch it theatrically — and there are plenty, given the limited Hindi-language screen counts outside India — the Netflix premiere is the real release date. The streaming rights reportedly went for **₹60 crore**, part of a ₹105 crore pre-release recovery that made the film profitable before it even opened.

Netflix will stream the film globally, which means NRIs in markets from the US to Australia to Germany can access it simultaneously. That's a meaningful shift from even five years ago, when OTT windows were staggered by region.

## The Bigger Picture

Bhooth Bangla's success cements several things. First, Akshay Kumar's post-pandemic career, which saw stumbles with **Selfiee**, **Mission Raniganj**, and **Bade Miyan Chote Miyan**, is no longer in question — this is his **20th ₹100-crore film** and his biggest global grosser in the post-pandemic era. Second, the horror-comedy genre in Hindi cinema has expanded dramatically: from Bhool Bhulaiyaa's ₹82 crore in 2007 to Bhooth Bangla's ₹265 crore in 2026, the audience appetite has tripled.

And third, for Priyadarshan, who returned to Hindi cinema after years focused on Malayalam projects, this is validation that his brand of slapstick-meets-supernatural storytelling still works — perhaps better than ever.

The film arrives on Netflix alongside another major Indian OTT premiere that week — **Maa Behen** (Madhuri Dixit's dark comedy, June 4) — making early June a stacked period for Indian content on the platform. For NRIs building their weekend watch list, the choice is clear: both."""

# Image: Try Akshay Kumar from Wikipedia
img1 = fetch_wikipedia_person_image("Akshay Kumar")
img1_attr = "Wikimedia Commons"
if not validate_image(img1):
    img1 = fetch_wikipedia_person_image("Priyadarshan")
    if not validate_image(img1):
        img1 = fetch_pexels_image("haunted mansion India", "horror comedy Bollywood")
        img1_attr = "Pexels"
        if not validate_image(img1):
            img1 = None
            img1_attr = ""

publish_article({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "image_url": img1,
    "image_attribution": img1_attr,
    "sources": ["Sacnilk Box Office", "Netflix India", "Esquire India", "Filmfare"],
})


# ============================================================
# ARTICLE 2: RCB Wins Back-to-Back IPL + Bollywood at the Final
# ============================================================
print("\n=== Article 2: RCB Back-to-Back IPL Dynasty ===")

art2_headline = "RCB Won Back-to-Back IPL Titles. Bollywood Made Sure It Looked Like a Film Premiere."
art2_subheadline = "Varun Dhawan, Pooja Hegde, Mrunal Thakur, AB de Villiers, and 130,000 fans packed Ahmedabad's Narendra Modi Stadium for the IPL 2026 final. Here's why the closing ceremony mattered as much as the match for diaspora audiences."
art2_slug = "rcb-ipl-2026-final-bollywood-celebrities-varun-dhawan-kailash-kher-nri-20260601"

art2_body = """The IPL 2026 final wasn't just a cricket match. It was a **130,000-person Bollywood event** that happened to have a cricket game in the middle of it.

Royal Challengers Bengaluru beat Gujarat Titans by five wickets at Ahmedabad's **Narendra Modi Stadium** on Sunday, chasing down 156 in 17.6 overs to clinch their **second consecutive IPL title**. With this win, RCB enters the same dynasty conversation as Chennai Super Kings and Mumbai Indians — the only other franchises to win back-to-back trophies.

But scroll through any NRI WhatsApp group or Instagram story from Sunday night, and you'll notice something: the cricket highlights are sharing screen time with red-carpet arrivals.

## The Celebrity Roll Call

**Varun Dhawan** was among the first Bollywood faces spotted at the stadium, arriving early and engaging with fans in the stands. He was there to promote his upcoming film **Hai Jawani Toh Ishq Hona**, but the crowd didn't care about the why — they cared about the selfies.

**Pooja Hegde** and **Mrunal Thakur** arrived together, adding glamour to the pre-match buzz. Both have significant fan bases in the South Indian film industry, making their presence at an RCB match feel appropriately cross-regional.

On the cricket side, the VIP box included **AB de Villiers** in the commentary booth — a man who has arguably done more for RCB's brand than any current player — alongside chief selector **Ajit Agarkar**, former head coach **Ravi Shastri**, IPL chairman **Arun Singh Dhumal**, and Rajasthan Royals sensation **Vaibhav Sooryavanshi**, who flew in as a spectator.

## Kailash Kher and the Closing Ceremony

The entertainment programming reflected the IPL's dual identity as sports league and cultural spectacle. **Kailash Kher** headlined the closing ceremony with his signature Sufi-rock energy, joined by Gujarati performers **Arvind Vegda** and **Devanshi Shah**, who brought regional flavour to the proceedings. A live violin performance during the innings break, a laser show, and a fireworks display rounded out the night.

For the **millions of NRIs watching on JioHotstar** — many of whom set alarms for a 6:30 AM start on the US East Coast or a 4:30 PM kick-off in the UK — the closing ceremony was part of the draw. The IPL has become the single biggest appointment-viewing event for the Indian diaspora, surpassing even Diwali specials and Republic Day parades.

## What RCB's Dynasty Means

**Virat Kohli** finally has the franchise legacy he spent 15 years building. **Rajat Patidar**, the breakout star of both finals, is now spoken of as RCB's most clutch player since AB de Villiers. And for diaspora fans who've worn the red-and-gold across five continents, this back-to-back run vindicates years of "ee sala cup namde" memes that once felt aspirational and now feel prophetic.

The IPL's ability to pull Bollywood A-listers into stadium seats isn't new — Shah Rukh Khan and KKR, Preity Zinta and Punjab Kings — but the 2026 final illustrated something bigger: cricket and entertainment are no longer adjacent industries in India. They're the same industry, and the diaspora consumes them as a single product.

RCB's IPL 2026 trophy is a cricket story. The way Sunday night looked and felt in Ahmedabad? That's a Bollywood story. And for NRIs, it was the best of both."""

# Image: Try Virat Kohli from Wikipedia
img2 = fetch_wikipedia_person_image("Virat Kohli")
img2_attr = "Wikimedia Commons"
if not validate_image(img2):
    img2 = fetch_pexels_image("cricket stadium India IPL", "cricket match celebration")
    img2_attr = "Pexels"
    if not validate_image(img2):
        img2 = None
        img2_attr = ""

publish_article({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "image_url": img2,
    "image_attribution": img2_attr,
    "sources": ["Mykhel", "SportsTiger", "InsideSport", "SportRadar IPL Data"],
})


# ============================================================
# ARTICLE 3: Trishala Dutt on Growing Up NRI Under Celebrity Pressure
# ============================================================
print("\n=== Article 3: Trishala Dutt NRI Celebrity Pressure ===")

art3_headline = "Trishala Dutt Says Growing Up as Sanjay Dutt's Daughter in America Was Lonelier Than Anyone Imagined"
art3_subheadline = "The 37-year-old psychotherapist opened up about bullying, body-shaming, and losing her mother as a child. Her story is a mirror for every NRI kid who grew up caught between two worlds."
art3_slug = "trishala-dutt-sanjay-dutt-nri-bullying-body-shaming-celebrity-pressure-20260601"

art3_body = """Trishala Dutt doesn't act. She doesn't sing. She didn't follow her father into Bollywood. And yet her recent public revelations about growing up as **Sanjay Dutt's daughter in the United States** have resonated more deeply with Indian diaspora audiences than most celebrity interviews this year.

In a series of candid social media posts and interviews, Trishala — now a **37-year-old psychotherapist based in New York** — opened up about the isolation, bullying, and body-shaming she experienced during her school years in America. The daughter of Sanjay Dutt and his first wife, the late actress **Richa Sharma**, Trishala lost her mother to brain cancer when she was just a toddler. She was raised by her maternal grandparents in the US while her father navigated his tumultuous career and personal life in Mumbai.

## The Weight of a Famous Last Name

"People expected me to look a certain way, behave a certain way, fit this 'perfect star kid' image," Trishala shared. "But I was a kid in New Jersey who was bullied for being Indian and simultaneously judged for not being Indian enough."

That tension — **too Indian for America, too American for India** — is the defining experience of a generation of NRI children. Trishala's version of it came with the added pressure of a surname that meant something in a country she didn't live in. In India, Dutt is royalty. In an American middle school, it's just another hard-to-pronounce name.

She spoke openly about battling weight issues from a young age, connecting her emotional struggles to the early loss of her mother and the complicated distance from her father. "Emotional eating was my coping mechanism for years," she said. "And then you get body-shamed for the very thing that's keeping you alive emotionally."

## Why This Matters Beyond Celebrity Gossip

Trishala's story has struck a nerve because it isn't really about being a celebrity's daughter. It's about the **specific loneliness of the Indian diaspora childhood** — the lunch-box shame, the accent mimicry, the constant code-switching between who you are at home and who you perform as at school.

What makes her revelations particularly powerful is what she did with that pain. Instead of entering Bollywood — a path that was always available — she pursued a career in **mental health and psychotherapy**. She now works with clients dealing with trauma, grief, and self-esteem issues, many of them South Asian Americans navigating the same cultural crosswinds she experienced.

"I chose this career because I lived it," she said. "Every client who sits across from me and says 'nobody in my family talks about mental health' — I know exactly what that silence sounds like."

## The Diaspora's Changing Conversation

Even five years ago, a public figure from an Indian entertainment family talking this openly about mental health, body image, and childhood trauma would have been unusual. The fact that Trishala's posts have been met with overwhelmingly positive responses — praise for her honesty, gratitude from NRI parents, solidarity from second-generation Indians — suggests the conversation has shifted.

For the Indian diaspora, celebrity has always been a one-way mirror: we watch them, they perform for us. Trishala Dutt's contribution is turning that mirror around and saying, "Here's what it actually looked like from this side." And for the thousands of NRI kids who grew up feeling caught between two countries, two cultures, and two versions of themselves, her words land like a diagnosis they've been waiting for.

She didn't need a film career to become the most relatable Dutt in the diaspora. She just needed to tell the truth."""

# Image: Try Trishala Dutt then Sanjay Dutt from Wikipedia
img3 = fetch_wikipedia_person_image("Trishala Dutt")
img3_attr = "Wikimedia Commons"
if not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Sanjay Dutt")
    img3_attr = "Wikimedia Commons"
    if not validate_image(img3):
        img3 = fetch_pexels_image("Indian American woman therapist", "South Asian mental health")
        img3_attr = "Pexels"
        if not validate_image(img3):
            img3 = None
            img3_attr = ""

publish_article({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "image_url": img3,
    "image_attribution": img3_attr,
    "sources": ["Asian News 18", "Hindustan Times", "Instagram (Trishala Dutt)"],
})

print("\n=== Entertainment writer complete ===")
