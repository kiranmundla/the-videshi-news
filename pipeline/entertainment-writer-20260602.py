#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-02 batch."""

import json, os, re, sys, time, uuid, traceback
import requests, urllib.parse
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────────────
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
            v = v.strip().strip("'\"")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def sb_insert(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code >= 400:
        print(f"  ✗ Supabase error {r.status_code}: {r.text[:500]}")
    r.raise_for_status()
    return r.json()

def sb_patch(table, match, payload):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

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
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
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
    """Check that an image URL returns valid image content >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return CL on HEAD; try GET range
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            return len(chunk) > 5000
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def source_image_for_person(person_name, pexels_fallback_query=None, pexels_fallback2=None):
    """Try Wikipedia first, then Pexels for person articles."""
    img = fetch_wikipedia_person_image(person_name)
    if img and validate_image(img):
        return img, "Wikimedia Commons"
    # Try alternate names
    parts = person_name.split()
    if len(parts) > 1:
        # Try just first + last
        alt = f"{parts[0]} {parts[-1]}"
        if alt != person_name:
            img = fetch_wikipedia_person_image(alt)
            if img and validate_image(img):
                return img, "Wikimedia Commons"
    # Pexels fallback
    if pexels_fallback_query:
        img = fetch_pexels_image(pexels_fallback_query, pexels_fallback2)
        if img and validate_image(img):
            return img, "The Videshi"
    return None, None

def reading_time(body):
    words = len(body.split())
    return max(3, round(words / 238))

def check_banned_url(url):
    """Return True if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            return True
    return False

# ── Articles ──────────────────────────────────────────────────────────────────

ARTICLES = []

# ─── Article 1: Kangana's Bharat Bhhagya Viddhaata ───────────────────────────
ARTICLES.append({
    "headline": "Kangana Ranaut Plays a Nurse in a 26/11 Film That Ignores Commandos Entirely. It Releases June 12.",
    "subheadline": "Bharat Bhhagya Viddhaata tells the story of unarmed hospital staff who saved 400 lives during the Mumbai attacks — a story NRI audiences have never seen on screen.",
    "slug": "kangana-ranaut-bharat-bhhagya-viddhaata-26-11-cama-hospital-nurse-june-12-nri-20260602",
    "category": "entertainment",
    "person_name": "Kangana Ranaut",
    "pexels_fallback": "Mumbai hospital nurse",
    "sources_list": "Filmibeat, Bollywood Hungama, Sacnilk, Blaze Trends",
    "body": """Every 26/11 film made so far has centred the obvious heroes — NSG commandos rappelling from helicopters, armed officers storming the Taj. Kangana Ranaut's next film flips the frame entirely.

**Bharat Bhhagya Viddhaata**, written and directed by Manoj Tapadia and scheduled for a June 12 theatrical release, tells the story of the unarmed staff at Mumbai's Cama and Albless Hospital who kept nearly 400 patients alive while Ajmal Kasab and Abu Ismail moved through the building. Kangana plays a staff nurse. The cast around her — Girija Oak, Smita Tambe, Amrutha Namdev, Esha Dey, Priya Berde, Asha Shelar, Suhita Thatte, Rasika Aghase — is composed almost entirely of women.

## A Deliberate Absence of Gunfire

Tapadia has been clear about his tonal intent. This is not an action film. The director told press he wanted to capture the "silence of bravery" — how nurses, ward boys, cleaners, lift operators, and security guards made split-second decisions in corridors that had become a kill zone. No bulletproof vests. No weapons. Just the immediate calculation: keep the patients breathing, keep the doors shut, don't make a sound.

The production consciously avoided the spectacle of commando-style intervention. What it stages instead is claustrophobic, hospital-bound survival — a real-time dramatisation of ordinary people becoming human shields for the vulnerable.

## The NRI Connection No One Talks About

For the Indian diaspora, 26/11 occupies a particular emotional register. Many NRIs have personal ties to South Mumbai. Many watched the attacks unfold on live television from thousands of miles away, unable to reach family. The Taj and the Oberoi became symbols of the tragedy internationally, but Cama Hospital — a public women's and children's hospital — barely registered in the global news cycle.

The hospital's staff, drawn largely from lower-middle-class backgrounds, were never profiled on CNN or BBC. Their story became a footnote in a narrative dominated by luxury hotel sieges and counter-terror operations. Tapadia's film corrects that erasure.

## Kangana's Message Before Release

In a video shared on social media on June 1, Kangana decoded the film's title — drawn from the Indian national anthem — by naming the people society calls "aam aadmi": nurses, railway staff, school workers, sanitation crews. "Ek hi din mein sara system ruk jaayega," she said. "Wahi hai, asli Bharat Bhhagya Vidhaata."

The message lands differently for NRIs who left a country run by these invisible workers and built new lives in countries where similar workers remain similarly invisible. It is a specific kind of recognition that crosses borders.

## What to Watch For

Bharat Bhhagya Viddhaata is presented by Dr. Jayantilal Gada's Pen Studios and produced in collaboration with Manikarnika Films, Paramhans Creations, Eunoia Films LLP, and Floating Rocks Entertainment. Distribution is by Pen Marudhar.

Given Kangana's political profile and the film's inherently patriotic framing, expect the publicity cycle to get noisy. But the film itself appears to be doing something quieter and more interesting — telling a working-class story that the Indian film industry has repeatedly walked past for 18 years.

For NRI viewers who lived through 26/11 from afar, this may be the version of the story they've been waiting to see."""
})

# ─── Article 2: Masoom: The New Generation ────────────────────────────────────
ARTICLES.append({
    "headline": "Shekhar Kapur and A.R. Rahman Are Reuniting for a Masoom Sequel. The Original Stars Are Coming Back After 43 Years.",
    "subheadline": "Naseeruddin Shah and Shabana Azmi will reprise their roles alongside Manoj Bajpayee and Nithya Menen. The new film explores identity, migration, and the families that NRIs leave behind.",
    "slug": "masoom-new-generation-shekhar-kapur-ar-rahman-naseeruddin-shah-shabana-azmi-nri-20260602",
    "category": "entertainment",
    "person_name": "Shekhar Kapur",
    "person_name_alt": "A. R. Rahman",
    "pexels_fallback": "Indian family drama emotional",
    "sources_list": "Cinema Express, Bollywood Hungama, Devdiscourse, Zoom TV",
    "body": """In 1983, a 38-year-old Shekhar Kapur made his directorial debut with a film about a man whose past walks through the door in the form of a child he didn't know existed. **Masoom** starred Naseeruddin Shah and Shabana Azmi. It made grown adults cry in theatres. Forty-three years later, the same director, the same leads, and an Academy Award-winning composer are doing it again.

**Masoom: The New Generation** was officially announced on May 30. A.R. Rahman — who worked with Kapur on *Elizabeth: The Golden Age*, *Bombay Dreams*, and the musical *Why?* — is both composer and co-producer. The cast adds Manoj Bajpayee, Nithya Menen, and Kaveri Kapur (Shekhar's daughter) alongside Shah and Azmi in returning roles.

## Why Migration Matters

Kapur has been explicit that the new film will explore identity, family, love, and migration "through a contemporary lens." For a director who has spent decades moving between Mumbai, London, and Los Angeles, these are not abstract themes.

The original *Masoom* asked a brutally simple question: what happens when a family is confronted with a truth it never asked for? The answer — guilt, resentment, love, forgiveness — played out in an upper-middle-class Delhi household. The new film reportedly takes that emotional architecture and sets it against the displacement of modern diaspora life.

For NRI audiences, this reframing hits close. The families that immigration fractures are rarely shown with the kind of emotional precision Kapur brought to the 1983 film. Most Bollywood films about NRIs default to either patriotic nostalgia (*Swades*) or identity comedy (*Namaste London*). A drama that takes the quiet devastation of family separation seriously — and casts Naseeruddin Shah and Shabana Azmi to do it — occupies rare emotional territory.

## The Rahman Factor

Rahman described the opportunity in unusually personal terms. "Working with Shekhar has always been a deeply enriching experience — he has been a mentor and a creative force in many ways," he said. "When he shared the vision for this film, I felt compelled to be involved beyond the music."

That last phrase matters. Rahman isn't scoring someone else's project; he's co-producing a film whose themes — uprooting, cultural dislocation, the cost of leaving — mirror his own trajectory from Chennai to the global stage.

The original *Masoom* carried one of Hindi cinema's most devastating soundtracks, with R.D. Burman's "Lakdi Ki Kaathi" and "Tujhe Naraz Nahin Zindagi" becoming generational touchstones. Rahman stepping into those shoes is both an honour and a risk.

## Shekhar Kapur's Other Comment

In a lighter moment, Kapur tweeted about 15-year-old IPL sensation Vaibhav Sooryavanshi: "If Sooryavanshi wasn't such a sensational cricketer, I could have cast him in Masoom, the film." It was a joke, but it revealed something about the film's generational focus — the story clearly involves a child or young person whose presence disrupts the equilibrium of the adults around them.

## What NRI Audiences Should Know

Filming starts later this year. A worldwide theatrical release is anticipated in late 2026 or early 2027. Shabana Azmi and Naseeruddin Shah, both in their seventies now, are reprising roles they played as young married adults — an extraordinary span that will give the sequel a built-in emotional resonance no casting trick could replicate.

For a diaspora that grew up with the original *Masoom* and now raises its own children between two countries, this sequel isn't just a film announcement. It's a mirror being held up at precisely the right angle."""
})

# ─── Article 3: Ananya Panday / Chand Mera Dil Bharatanatyam Controversy ─────
ARTICLES.append({
    "headline": "Ananya Panday's Dance Went Viral for All the Wrong Reasons. Then She Blamed Social Media for Her Anxiety.",
    "subheadline": "Chand Mera Dil has collected ₹22 crore in 10 days. The Bharatanatyam fusion scene has become a larger conversation about Bollywood, privilege, and classical art.",
    "slug": "ananya-panday-chand-mera-dil-bharatanatyam-controversy-box-office-nri-20260602",
    "category": "entertainment",
    "person_name": "Ananya Panday",
    "pexels_fallback": "Bharatanatyam classical dance performance",
    "pexels_fallback2": "Indian classical dance stage",
    "sources_list": "Bollywood Hungama, Bollywood Life, Live Mint, India Forums, Tupaki",
    "body": """On May 22, Dharma Productions released **Chand Mera Dil**, a romantic drama starring Ananya Panday and Lakshya. Ten days later, the film has collected approximately ₹22 crore gross — a number that qualifies as a commercial disappointment for a Dharma release. But the conversation around the film has nothing to do with its box office and everything to do with a single dance scene.

## The Scene That Launched a Thousand Memes

In the film, Ananya plays Chandni, a college student from a family steeped in classical dance. During a campus cultural event, Chandni performs what the makers describe as a "fusion" routine — Bharatanatyam blended with hip-hop and locking. The scene was meant to introduce her character as bold and rule-breaking.

The internet saw it differently. Clips went viral within hours of release. The choreography was called stiff, the classical elements were called superficial, and the overall effect was called — in the most cutting coinage of the cycle — "Nepo Natyam." Established Bharatanatyam practitioners weighed in, questioning whether the sequence trivialized a 2,000-year-old art form. The backlash was loud, sustained, and brutal.

## Ananya's Response Made It Worse

Ananya addressed the controversy in a recent press interview, but not in the way classical dance communities were hoping. Rather than engaging with the artistic criticism, she spoke about muting Instagram pages that "give me the slightest amount of anxiety." She described social media as damaging to mental health — a valid personal stance, but one that read to many as deflection.

"Slamming social media for social health is nothing but slamming the audiences for the flop show of a film," entertainment portal Tupaki noted bluntly.

For NRI audiences who grew up learning Bharatanatyam, Kathak, or Kuchipudi at weekend classes — often as one of the few connections to their heritage — the controversy carries an additional charge. Classical Indian dance in diaspora communities is not just art; it is identity infrastructure. Seeing it reduced to a "breakout introduction" in a Bollywood film, performed without visible rigour, felt personal.

## The Defence

Charu Shankar, who plays Ananya's mother in the film, defended both the scene and her co-star. "The sequence was always conceived as a contemporary, edgy breakout introduction for Chandni's character," she told Hindustan Times. "Trolling is never in good taste. Conversations around art are valid. Mockery is not."

Ananya's father, veteran actor Chunky Panday, also weighed in, clarifying that the scene was never intended as a pure Bharatanatyam performance — it was meant to reflect the experimental fusion dances commonly seen at college cultural festivals.

Choreographer and dancer Sandip Soparrkar also came out in Ananya's defence, though the specifics of his argument didn't gain the same traction as the criticism.

## The Box Office Tells Its Own Story

Chand Mera Dil opened to lukewarm numbers and has struggled against competition. At ₹22 crore after 10 days, it trails significantly behind Pati Patni Aur Woh Do, which collected ₹40 crore gross — despite being considered a "run-of-the-mill" film.

The Bharatanatyam controversy has ensured the film stays in the news cycle, but attention hasn't translated into ticket sales. Whether the discourse helped or hurt is debatable; what's clear is that it overshadowed everything else about the film, including Lakshya's performance, which has received notably warmer reviews.

## The Larger Question

The incident sits at the intersection of several ongoing Bollywood debates: nepotism, cultural appropriation, the gap between mainstream Hindi cinema and the classical arts it occasionally borrows from, and the question of who gets to interpret traditional art forms on screen.

For the diaspora, these questions are not academic. They are lived. When your child performs Bharatanatyam at a community arangetram after years of training, and a Bollywood star performs a version of it that goes viral for being bad — that's not an abstract cultural critique. It's a visceral reaction to something you've invested in being treated as costume.

Whether Ananya deserved the scale of the backlash is a fair question. Whether the backlash itself reflected something real about Bollywood's relationship with Indian classical traditions is a better one."""
})

# ── Publish ───────────────────────────────────────────────────────────────────

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Image sourcing
    img_url, img_attr = None, None
    person = art.get("person_name")
    if person:
        img_url, img_attr = source_image_for_person(
            person,
            art.get("pexels_fallback"),
            art.get("pexels_fallback2")
        )
    # Try alt person name if first failed
    if not img_url and art.get("person_name_alt"):
        img_url, img_attr = source_image_for_person(
            art["person_name_alt"],
            art.get("pexels_fallback"),
            art.get("pexels_fallback2")
        )
    # Final Pexels fallback
    if not img_url and art.get("pexels_fallback"):
        img_url = fetch_pexels_image(art["pexels_fallback"], art.get("pexels_fallback2"))
        if img_url and validate_image(img_url):
            img_attr = "The Videshi"
        else:
            img_url = None

    if img_url and check_banned_url(img_url):
        print(f"  ✗ Banned URL detected, skipping: {img_url[:60]}")
        img_url = None
        img_attr = None

    body = art["body"].strip()
    rt = reading_time(body)

    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["category"],
        "body": body,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": art["sources_list"],
        "is_editorial": False,
    }
    if img_url:
        payload["image_url"] = img_url
    if img_attr:
        payload["image_attribution"] = img_attr

    try:
        result = sb_insert("p2_articles", payload)
        art_id = result[0]["id"] if isinstance(result, list) and result else None
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        print(f"    Image: {img_url[:80] if img_url else 'None'}")
        print(f"    Words: {len(body.split())}, Reading time: {rt} min")
        return art_id
    except Exception as e:
        print(f"  ✗ Failed to publish: {e}")
        traceback.print_exc()
        return None


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Entertainment Writer — {datetime.now(timezone.utc).isoformat()}")
    print(f"Articles to publish: {len(ARTICLES)}")

    results = []
    for art in ARTICLES:
        art_id = publish_article(art)
        results.append({"slug": art["slug"], "id": art_id, "ok": art_id is not None})
        time.sleep(1)

    print(f"\n{'='*60}")
    print("Summary:")
    for r in results:
        status = "✓" if r["ok"] else "✗"
        print(f"  {status} {r['slug']}")

    ok = sum(1 for r in results if r["ok"])
    print(f"\nDone: {ok}/{len(results)} articles published.")
    if ok < len(results):
        sys.exit(1)
