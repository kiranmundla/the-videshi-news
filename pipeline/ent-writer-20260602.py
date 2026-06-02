#!/usr/bin/env python3
"""Entertainment writer — 2026-06-02 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# ── env ──────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))
load_dotenv(os.path.expanduser("~/workspace/.env.pexels"))

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
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            r = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(r.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns a real image > 5KB."""
    if not url:
        return False
    # Block banned domains
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ BANNED domain in URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't give Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert into Supabase table, return response."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:300]}")
    return None


def sb_patch(table, match, payload):
    """Patch a Supabase row."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")
    return False


# ── articles ─────────────────────────────────────────────────────────────────

articles = [
    # ── Article 1: Made in India: A Titan Story ──
    {
        "headline": "Naseeruddin Shah Plays JRD Tata in a Show About India's First Watch. Every NRI's Wrist Has the Answer.",
        "subheadline": "Made in India: A Titan Story arrives on Amazon MX Player on June 3, tracing how a Parsi visionary and a watch-factory dream became a brand that 350 million Indians wore on their wrists.",
        "slug": "made-in-india-titan-story-naseeruddin-shah-jrd-tata-amazon-mx-june-3-nri-20260602",
        "category": "entertainment",
        "body": """Every Indian household has a Titan story. The first watch a father gifted before college. The Raga a mother wore to weddings. The Sonata that survived two countries, three time zones, and a decade of homesickness. That's the emotional bet behind *Made in India: A Titan Story*, the six-episode series premiering on Amazon MX Player on June 3.

## The Men Behind the Watch

Naseeruddin Shah steps into the role of JRD Tata, the Parsi industrialist who believed India could build a world-class watch before India believed it about itself. Jim Sarbh plays Xerxes Desai, the executive who turned that belief into a factory floor in Hosur, Tamil Nadu, in the 1980s. The cast also includes Vaibhav Tatwawadi, Namita Dubey, Lakshvir Saran, and Kaveri Seth, but the real star is the story itself — adapted from Vinay Kamath's acclaimed book *Titan: India's Most Successful Consumer Brand*.

Director Robbie Grewal and writer Karan Vyas set the series in pre-liberalisation India, a time when "Made in India" was an apology, not a boast. HMT dominated the watch market with its government-backed monopoly. Private players were told they couldn't compete. Tata and Desai competed anyway.

## Why the Diaspora Should Care

For NRIs, Titan isn't just a brand. It's a timestamp. The watch industry in India before Titan meant government-issue HMT timepieces that broke every monsoon and Soviet-style distribution. Titan introduced quartz, introduced fashion, introduced the idea that an Indian product could sit on a shelf next to Seiko and not apologise for being there.

Vaibhav Tatwawadi, who plays a key role, described the series' unusual pull during promotions: "Normally, when someone asks about your next project, you have to explain the details. For this one, I just said 'Titan' and people started telling me their own Titan stories." That emotional ownership — an audience that feels the brand belongs to them before a single frame is shot — is rare in Indian streaming.

## What It Means for the Business Story Genre

Indian OTT has been drowning in crime thrillers and family dramas. The business biopic is underserved territory, and *Made in India* arrives at a moment when Indian entrepreneurship narratives have global traction. The Tata Group's international footprint — from Jaguar Land Rover to Tata Consultancy Services — means NRI audiences in the US, UK, and Canada already have a relationship with the conglomerate. A story about its watchmaking arm, set in the decade before liberalisation cracked India open, fills a gap that no Bollywood thriller can.

The series is produced by Almighty Motion Pictures and will stream free on Amazon MX Player, making it accessible without a Prime subscription. For a diaspora that grew up setting their clocks to Titan's "Mozart" jingle, the timing couldn't be more deliberate.

**Where to watch:** Amazon MX Player, June 3, 2026
**Languages:** Hindi
**Episodes:** 6""",
        "sources": json.dumps([
            {"name": "Nation Press", "url": "https://nationpress.com"},
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
            {"name": "MensXP", "url": "https://www.mensxp.com"},
        ]),
        "image_person": "Naseeruddin Shah",
        "image_fallback_query": "Titan watch India vintage",
        "image_fallback_query2": "Indian watch factory",
        "image_attribution": "Wikimedia Commons",
    },

    # ── Article 2: Gullak Season 5 ──
    {
        "headline": "The Mishras Are Back. Gullak Season 5 Drops on SonyLIV Thursday, and the Diaspora's Comfort Show Just Got a New Annu.",
        "subheadline": "Anant Joshi replaces Vaibhav Raj Gupta as the elder Mishra son in a season that adds Gopal Datt as Shanti's brother Pinky — and asks whether a middle-class family can survive change without losing its soul.",
        "slug": "gullak-season-5-sonyliv-june-5-anant-joshi-mishra-family-nri-20260602",
        "category": "entertainment",
        "body": """There is no explosion in *Gullak*. No spy universe. No ₹600-crore budget. What there is: a piggy bank that narrates, a mother who solves problems with guilt, a father who solves problems with silence, and two sons who solve nothing but make you cry anyway. That formula has made TVF's *Gullak* one of the most quietly beloved Indian shows among NRI viewers — and Season 5 arrives on SonyLIV on June 5.

## The Big Change

This season's headline is a cast swap. Vaibhav Raj Gupta, who played the elder son Annu Mishra for four seasons, has been replaced by Anant Joshi. The show's creators haven't publicly detailed the reasons for the change, but Joshi — a theatre-trained actor from Nainital — has spoken about discovering that he shares roots with Jameel Khan, who plays his on-screen father Santosh Mishra. Both are from Nainital, Uttarakhand, and bonded over shared memories of the hill town before filming began.

The rest of the Mishra household returns intact. Jameel Khan and Geetanjali Kulkarni reprise their roles as the parents. Harsh Mayar returns as the younger son Aman. The new addition is Gopal Datt as Pinky, Shanti's brother, whose visit to Mishra Nivas promises the kind of extended-family chaos that anyone who's hosted a *mama* from India will recognise instantly.

## Why NRIs Keep Coming Back

For Indians abroad, *Gullak* functions as a time machine. The middle-class anxieties it depicts — the electricity bill that arrives at the worst time, the neighbour whose son got into IIT, the silent compromise of a father who wanted more from life — aren't period drama. They're Tuesday. The show captures a specific register of Indian family life that Bollywood's urban-elite narratives systematically ignore: the lower-middle-class household where love is expressed through sacrifice, not dialogue.

That register resonates differently when you're watching from a studio apartment in Jersey City or a shared flat in Hounslow. The Mishras aren't aspirational. They're memorial. They remind you of the home you left, the conversations your parents had when they thought you weren't listening, the piggy bank on the shelf that held coins for a future that looked exactly like this one.

## What to Expect

Season 5 spans seven episodes and, based on the pattern of previous seasons, will likely follow a semi-anthology structure — each episode centring on a different domestic micro-crisis while a season-long emotional arc connects them. The show's narration device — a piggy bank voiced with deadpan wisdom — remains one of the most distinctive storytelling choices in Indian streaming.

The cast change is a risk. Vaibhav Raj Gupta's Annu was gentle, anxious, and permanently caught between ambition and family obligation. Whether Anant Joshi can inherit that specific emotional frequency without disrupting the ensemble's chemistry will determine whether Season 5 extends the show's reputation or merely trades on it.

**Where to watch:** SonyLIV, June 5, 2026
**Episodes:** 7
**Languages:** Hindi""",
        "sources": json.dumps([
            {"name": "SonyLIV / TVF", "url": "https://www.sonyliv.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"},
            {"name": "Bharat Affairs", "url": "https://bharataffairs.com"},
        ]),
        "image_person": None,
        "image_fallback_query": "Indian middle class family home television",
        "image_fallback_query2": "Indian family living room evening",
        "image_attribution": "The Videshi",
    },

    # ── Article 3: Toxic — Yash's Big Bet ──
    {
        "headline": "Yash Spent ₹600 Crore on a Goa Gangster Fairy Tale. Toxic Opens Wednesday in IMAX. The Diaspora Pre-Sales Tell the Story.",
        "subheadline": "After KGF turned a Kannada star into a pan-India phenomenon, Toxic: A Fairy Tale for Grown-Ups arrives June 4 with Nayanthara, Kiara Advani, and a budget that dwarfs most Hollywood mid-range films.",
        "slug": "toxic-yash-june-4-imax-release-600-crore-goa-gangster-nri-diaspora-20260602",
        "category": "entertainment",
        "body": """The last time Yash walked into a theatre at this scale, he burned down every box office record south of the Vindhyas and most of the ones north of it. *KGF Chapter 2* grossed ₹859.7 crore in India net. The question Toxic answers isn't whether Yash can do it again. It's whether the Indian film industry can sustain a ₹600-crore bet on a single star's gravity.

## What Toxic Actually Is

Forget the marketing machinery for a moment. *Toxic: A Fairy Tale for Grown-Ups*, directed by Geetu Mohandas, is set in Goa between the 1940s and 1970s. It traces the rise of a criminal empire during the transition from colonial rule to local power structures. It's a period gangster film dressed in fairy-tale language — think *Gangs of Wasseypur* meets *Pan's Labyrinth*, if the labyrinth was a beach shack and the faun was running hashish routes.

The cast is deliberately pan-Indian. Nayanthara plays Ganga, reportedly Yash's sister in the film. Kiara Advani is the female lead Nadia. Tara Sutaria plays Rebecca. Huma Qureshi is the primary antagonist Elizabeth. Akshay Oberoi and Sudev Nair round out the ensemble. The music comes from Ravi Basrur (the man behind KGF's chest-thumping score), cinematography from Rajeev Ravi (*Annayum Rasoolum*, *Kammatipaadam*), and the action choreography from Hollywood's JJ Perry, who worked on the *John Wick* franchise.

## The Numbers Are Staggering

Toxic's pre-release business tells you where Indian cinema thinks it's going. The theatrical rights for Andhra Pradesh and Telangana alone were acquired by Dil Raju's Sri Venkateswara Creations for a reported ₹120 crore. Anil Thadani's AA Films handles North India and Nepal. Phars Film secured overseas rights for nearly ₹105 crore. The film is confirmed for IMAX, which positions it as an event-cinema experience rather than a standard multiplex release.

For NRI audiences, those overseas numbers matter. A ₹105-crore overseas rights deal means distributors in the US, UK, Canada, and the Gulf are betting heavily on diaspora turnout. KGF Chapter 2's overseas performance — it crossed ₹200 crore worldwide — proved that Kannada-origin films could sell tickets in markets that previously only opened for Hindi and Telugu blockbusters. Toxic is the test of whether that was a Yash-specific phenomenon or a permanent shift in the market.

## The Clash Factor

Toxic arrives on June 4, a Wednesday. The next day, June 5, brings two more major releases: Bobby Deol's *Bandar* (Anurag Kashyap's TIFF-premiered crime drama) and Varun Dhawan's *Hai Jawani Toh Ishq Hona Hai* (David Dhawan's rom-com). This three-way collision is unusual for a summer slate and suggests that studios believe the post-pandemic theatrical audience is large enough to split between an IMAX spectacle, an arthouse thriller, and a family entertainer in the same weekend.

For diaspora audiences who are deciding what to watch opening weekend at AMC or Cineplex, the choice may come down to appetite: Toxic offers scale and spectacle; Bandar offers Kashyap's trademark intensity; and HJTIHH offers nostalgia for the Dhawan-family comedy brand. The smart bet is that Toxic takes the IMAX and premium screens while the other two fight for standard auditoriums.

## What's at Stake

Yash co-produces Toxic through his banner. This isn't a hired-gun performance — it's a filmmaker's wager on his own star power. If Toxic works, it validates the model of a Kannada star building a global franchise outside the Hindi and Telugu ecosystems. If it doesn't, the ₹600-crore budget becomes a cautionary tale about overreach. For the diaspora, the answer arrives Wednesday.

**Where to watch:** Theatres nationwide and worldwide, June 4, 2026
**Languages:** Kannada, Hindi, Telugu, Tamil, Malayalam, English
**Format:** IMAX, 4DX, standard""",
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"},
            {"name": "KVN Productions (official)", "url": "https://twitter.com/KvnProductions"},
        ]),
        "image_person": "Yash (Kannada actor)",
        "image_person_alt": "Yash Gowda",
        "image_fallback_query": "Goa vintage 1960s India",
        "image_fallback_query2": "Indian cinema IMAX theatre",
        "image_attribution": "Wikimedia Commons",
    },
]

# ── publish loop ─────────────────────────────────────────────────────────────

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/{len(articles)}] {art['headline'][:70]}...")
    print(f"{'='*60}")

    # ── image sourcing ───────────────────────────────────────────────────
    img_url = None
    attribution = art.get("image_attribution", "The Videshi")

    # Try Wikipedia for person articles
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if not img_url and art.get("image_person_alt"):
            img_url = fetch_wikipedia_person_image(art["image_person_alt"])
        if img_url:
            attribution = "Wikimedia Commons"

    # Fall back to Pexels
    if not img_url:
        img_url = fetch_pexels_image(
            art.get("image_fallback_query", ""),
            art.get("image_fallback_query2"),
        )
        if img_url:
            attribution = "The Videshi"

    # Validate
    if img_url and not validate_image(img_url):
        print("  ⚠ Image failed validation, dropping")
        img_url = None

    # ── insert article ───────────────────────────────────────────────────
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"].strip(),
        "sources": art["sources"],
        "status": "published",
        "published_at": "now()",
        "is_editorial": False,
    }
    if img_url:
        payload["image_url"] = img_url
        payload["image_attribution"] = attribution

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")
