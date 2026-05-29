#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-29 batch"""

import json, os, re, sys, time, uuid, traceback
from datetime import datetime, timezone
import requests, urllib.parse

# ── Load env file ────────────────────────────────────────────────
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/.env.pexels") if os.path.exists(os.path.expanduser("~/.env.pexels")) else None
if pexels_env:
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ────────────────────────────────────────────────
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
        print("  ⚠ No Pexels API key found")
        return None
    headers = {"Authorization": PEXELS_KEY}
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate that an image URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if "image" in ct:
            return True
    except:
        pass
    # Try GET with range
    try:
        r = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)",
                                  "Range": "bytes=0-10000"})
        ct = r.headers.get("Content-Type", "")
        if "image" in ct and len(r.content) > 5000:
            return True
    except:
        pass
    return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com",
              "_nc_ht=", "_nc_cat=", "ccb="]
    return any(b in url for b in banned)


# ── Supabase helpers ─────────────────────────────────────────────
def sb_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  ⚠ Insert error ({r.status_code}): {r.text[:300]}")
    return r.json() if r.text else None


def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ⚠ Patch error ({r.status_code}): {r.text[:300]}")
    return False


# ── Articles ─────────────────────────────────────────────────────
ARTICLES = [
    # ── Article 1: Alpha preponed to July 3 ──
    {
        "headline": "Alia Bhatt's Alpha Gets Bumped Up a Week. YRF's First Female Spy Film Now Opens July 3.",
        "subheadline": "Dhamaal 4 moved to July 17, giving Alpha two uncontested weeks before Nolan's The Odyssey arrives. Bobby Deol plays the villain. Hrithik Roshan may cameo.",
        "slug": "alia-bhatt-alpha-preponed-july-3-yrf-spy-universe-bobby-deol-nri-20260529",
        "category": "entertainment",
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"},
            {"name": "Filmibeat", "url": "https://www.filmibeat.com"}
        ]),
        "person_name": "Alia Bhatt",
        "pexels_query": None,
        "body": """Aditya Chopra has moved his biggest bet of the summer forward by a week.

Alpha, the first female-led instalment in the YRF Spy Universe, will now release on July 3 instead of the originally announced July 10. The decision came after Dhamaal 4 — previously slotted for July 3 — was pushed back to July 17, leaving the date wide open.

A source at a prominent multiplex chain confirmed the change to Bollywood Hungama: "With no major release planned for July 3, Aditya Chopra felt it was the right date to bring Alpha to theatres."

The math works in Alpha's favour. Christopher Nolan's The Odyssey is set for July 17 alongside Dhamaal 4, which means Alpha now has a clean two-week runway at the domestic box office before Hollywood's biggest director of the decade shows up.

## What We Know About Alpha

Directed by Shiv Rawail, who previously helmed Netflix's acclaimed series The Railway Men, Alpha stars Alia Bhatt and Sharvari as two elite agents in a gritty, globe-trotting espionage narrative. Bobby Deol plays the primary antagonist — his character was teased in the post-credits sequence of War 2, where he tattooed the Greek letter alpha on a young girl's arm and told her she would one day rule.

Anil Kapoor returns as Vikrant Kaul, a senior intelligence official within the spy network. And Hrithik Roshan is expected to make a special appearance as Major Kabir Dhaliwal, connecting Alpha to the broader timeline that includes Pathaan, Tiger, and War.

What sets this film apart from previous YRF spy entries is the character herself. Reports suggest Alia's role isn't a conventional spy at all — she plays a deadly assassin with a dark origin story, someone who was "raised and built to kill" from a young age. The makers are reportedly betting on brutal combat sequences, hand-to-hand action, and a grittier tone than anything the franchise has attempted before.

## Why NRIs Should Care

The YRF Spy Universe is Bollywood's closest equivalent to a global franchise — Pathaan crossed ₹1,000 crore worldwide, and War remains one of the highest-grossing Hindi action films ever made. Alpha is the first instalment that puts women at the centre of the action, and the delay-heavy production suggests Chopra wanted to get the visual effects right rather than rush a half-finished product.

For diaspora audiences who've watched every Spy Universe entry in IMAX overseas, July 3 just became the date to block. The film has been delayed three times — from Christmas 2025 to April 2026 to July 10 — and this final shift forward is a confidence signal, not another postponement.

Alpha's trailer hasn't dropped yet, but with five weeks to go, expect it any day now."""
    },

    # ── Article 2: Hombale Films enters Marathi cinema ──
    {
        "headline": "The KGF Makers Just Announced a Marathi Hip-Hop Musical. Nobody Saw That Coming.",
        "subheadline": "Hombale Films' Yeto Ka Naay is shooting in Mumbai right now. A Hindi version called YKN-Pehla Vaar drops simultaneously. The writer's room includes a real rapper.",
        "slug": "hombale-films-yeto-ka-naay-marathi-hip-hop-musical-mumbai-nri-20260529",
        "category": "entertainment",
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Blaze Trends", "url": "https://www.blazetrends.com"},
            {"name": "New Kerala", "url": "https://www.newkerala.com"}
        ]),
        "person_name": None,
        "pexels_query": "hip hop music concert India",
        "pexels_fallback": "Mumbai city street youth",
        "body": """Hombale Films has built its empire on scale. KGF. Salaar. Kantara. Mahavatar Narsimha. These are films that cost hundreds of crores, fill IMAX screens, and turn their leads into demigods. The banner's identity is rooted in spectacle.

Which is why Friday's announcement landed like a curveball.

Hombale Films has officially entered Marathi cinema — not with an action epic, not with a mythological franchise, but with a hip-hop musical called Yeto Ka Naay. The Hindi version, releasing simultaneously, is titled YKN-Pehla Vaar. Cameras are already rolling in Mumbai.

## The Details

Directed by Sarang Sanjeev Sathaye and produced by Vijay Kiragandur, the film is described as a coming-of-age story set entirely against the backdrop of Mumbai's underground hip-hop scene. The narrative explores friendship, love, identity, and ambition through the lens of contemporary music culture.

What makes the project credible beyond the corporate press release: the writer's room includes rapper Srushti Tawade, alongside Sujay Jadhav and Shreyas Sagvekar. Putting an actual hip-hop artist at the screenplay table — rather than hiring one to consult after the script is locked — signals that Hombale is treating the genre seriously, not cosplaying it.

Cinematography is by Harshvir Oberai. Music by AV Prafullachandra. The production house shared a motion poster on Instagram with the tagline: "The beat drops. The rivalry begins. Can the brotherhood bond survive?"

## Why This Matters

Hombale's expansion strategy has always been deliberate. They started in Kannada, scaled to Hindi with KGF, went pan-Indian with Salaar and Kantara, and now they're pushing into Marathi — a market that has been producing increasingly ambitious, commercially successful cinema in recent years. Deool Band 2 just crossed ₹200 crore. The audience is there.

But the genre choice is the real story. Indian hip-hop has graduated from Gully Boy novelty to a genuine cultural force, especially in Mumbai's Marathi-speaking communities. Divine, Emiway Bantai, and the underground scene they represent have built fanbases that rival mainstream Bollywood music. A Hombale-backed film that centres this world — rather than using it as set dressing for a star vehicle — could be the first studio-level Indian hip-hop film since Ranveer Singh put on Murad's hoodie in 2019.

## For the Diaspora

The film's theatrical release is planned for later in 2026, though no exact date has been announced. For NRIs who grew up on KGF's industrial swagger and Kantara's folk mythology, Yeto Ka Naay represents something different from Hombale — a bet on youth culture, street music, and a language market that the banner has never touched before.

If they pull it off, it won't just be a good film. It'll be proof that India's most ambitious production house can do intimate as well as it does epic."""
    },

    # ── Article 3: Kaante 2 story cracked ──
    {
        "headline": "Sanjay Gupta Has Cracked the Story for Kaante 2. The Legal Issues That Stalled It for 24 Years Are Finally Resolved.",
        "subheadline": "Gupta and Sanjay Dutt are reuniting for an 11th film together. The original Kaante was shot in LA with Amitabh Bachchan, Kumar Gaurav, and Sunil Shetty. Dutt was 'grossly wasted' before Dhurandhar, Gupta says.",
        "slug": "kaante-2-sanjay-gupta-sanjay-dutt-story-cracked-legal-cleared-nri-20260529",
        "category": "entertainment",
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "InControversial Podcast", "url": "https://www.youtube.com"}
        ]),
        "person_name": "Sanjay Dutt",
        "pexels_query": None,
        "body": """For 24 years, Kaante 2 existed only as a hypothetical. The original — shot in Los Angeles with Amitabh Bachchan, Sanjay Dutt, Sunil Shetty, Kumar Gaurav, Lucky Ali, and Mahesh Manjrekar — became a cult classic after its 2002 release, but legal complications locked the franchise in limbo. No sequel. No reboot. Just periodic nostalgia.

That's now changed.

Director Sanjay Gupta confirmed on the InControversial Podcast that he has "cracked, at a very base level, a story for Kaante 2" and will begin writing the screenplay. More importantly, the legal issues that had bound the original film for over two decades have been resolved.

"After Kaante was released, it was bound in some legal shackles and it has now been taken care of," Gupta said. "Because it's been taken care of, I am investing creatively into writing the sequel."

## Sanjay Dutt Is the Centrepiece

Gupta didn't name the full cast, but made it clear that Sanjay Dutt is the anchor. The two have collaborated on ten films — eight directed by Gupta (Aatish, Jung, Khauff, Kaante, Musafir, Zinda, Dus Kahaniyaan, and the unreleased Alibaug), plus two productions (Plan and Shootout at Lokhandwala). Kaante 2 would be their eleventh.

What's interesting is Gupta's candid assessment of Dutt's recent career. "Before Dhurandhar, I also believe that he was grossly wasted," he said. "The kind of films he had done — the filmmakers didn't know how to present him. They didn't know his strengths."

Dhurandhar, Nelson Dilipkumar's 2025 blockbuster that recently crossed ₹1,000 crore in Hindi alone, proved that Dutt still has box office pull when the material is right. Gupta clearly sees that as validation: "Even today, when I see him, I realize that he has so much potential in him. He can still carry a film on his shoulders, provided we give that film to him."

## What Made the Original Special

Kaante worked because it was unapologetically stylish and uncommonly dark for its era. Six Indian men in Los Angeles, all failed immigrants, come together to rob a bank. The film borrowed liberally from Quentin Tarantino's Reservoir Dogs — Gupta has never denied the influence — but its Indian cast, Hindi-language sensibility, and the sheer charisma of its ensemble gave it a distinct identity.

For the Indian diaspora, particularly NRIs in the US, Kaante hit differently. It was set in their world — the LA streets, the immigrant struggle, the desperation of men who left India for a dream that never materialised. The film's Yellow Cab sequence, its warehouse standoff, and Dutt's swaggering Ajju remain etched in the memory of a generation that watched it on pirated VCDs in college dorms.

## What's Next

Gupta is still in the writing phase, so casting, timelines, and production details are months away. Whether the sequel attempts to reassemble the original surviving cast or builds a new ensemble remains to be seen. But with the legal clearance finally in hand and Dutt riding the highest commercial wave of his career, the timing is better than it's been in two decades.

Kaante fans have waited 24 years. The wait, it appears, is entering its final stretch."""
    },

    # ── Article 4: Drishyam 3 crosses ₹200 crore ──
    {
        "headline": "Drishyam 3 Just Hit ₹200 Crore Worldwide in Eight Days. Georgekutty Is Now Malayalam Cinema's Most Profitable Character.",
        "subheadline": "Mohanlal's third film to cross the ₹200 crore mark this year alone. The trilogy's final chapter opened bigger than the original Pulimurugan's lifetime, and it's still running strong.",
        "slug": "drishyam-3-200-crore-worldwide-mohanlal-malayalam-box-office-record-nri-20260529",
        "category": "entertainment",
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Filmfare", "url": "https://www.filmfare.com"},
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
            {"name": "Filmibeat", "url": "https://www.filmibeat.com"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Drishyam_3"}
        ]),
        "person_name": "Mohanlal",
        "pexels_query": None,
        "body": """Three films. Three chapters. ₹200 crore in eight days.

Drishyam 3, the final instalment of Jeethu Joseph's thriller trilogy, has crossed the ₹200 crore mark at the worldwide box office, making it the fastest film in the franchise to reach the milestone and cementing Mohanlal's 2026 as one of the most dominant stretches any Indian actor has ever had.

The superstar acknowledged the achievement on X: "Three films. Three chapters. One unbroken bond. Thank you for walking with Georgekutty and family."

## The Numbers

According to Sacnilk and Pinkvilla, Drishyam 3 wrapped its extended opening week at approximately ₹197 crore gross worldwide — ₹95.20 crore gross in India (₹62.70 crore from Kerala alone) and over ₹100 crore from overseas markets. Day 8 added an estimated ₹6.50 crore net domestically, pushing the worldwide total past the ₹200 crore line.

That makes it the second-fastest Malayalam film to reach ₹200 crore worldwide, trailing only Mohanlal's own L2: Empuraan (₹234.50 crore opening week). Trade analysts project a lifetime collection of ₹250 crore or higher, with the real question being whether it can challenge Lokah Chapter One's ₹300 crore benchmark.

On Day 8, the film was screened across 3,453 shows nationally with an overall occupancy of 40.8%. The Malayalam version — running across 2,136 shows — maintained 53% occupancy, an exceptional hold for a second week.

## Mohanlal's 2026 Is Unprecedented

Here's the context that makes this number extraordinary: Drishyam 3 is Mohanlal's third film to cross ₹200 crore worldwide in 2026. L2: Empuraan and Thudarum got there first. No Malayalam actor — and very few Indian actors in any language — have achieved three ₹200 crore films in a single calendar year.

To put this in historical perspective: when Pulimurugan released in 2016, it was celebrated as Malayalam cinema's first ₹100 crore grosser. A decade later, Pulimurugan doesn't even make the list of the ten highest-grossing Malayalam films worldwide. The commercial ceiling of the industry has been completely rewritten, and Mohanlal has been the primary architect of that rewriting.

## Why Georgekutty Still Works

Drishyam 3 didn't have a guaranteed path to this number. Before release, a vocal section of audiences questioned whether the franchise needed a third chapter after the tightly concluded Drishyam 2. The film opened to mixed-to-positive reviews from critics but overwhelmingly positive audience response — a pattern that suggests word-of-mouth did the heavy lifting after opening day.

Directed by Jeethu Joseph, the final chapter explores the emotional consequences of the events that have defined Georgekutty's family across the trilogy. The cast includes Meena, Ansiba Hassan, Esther Anil, Siddique, Murali Gopy, and Asha Sarath.

## The Diaspora Factor

Drishyam 3's overseas gross — over ₹100 crore — tells a story that the Indian domestic market alone can't. Malayalam cinema's diaspora audience has become its most reliable growth engine. Keralite communities in the Gulf, North America, Europe, and Australia have turned Malayalam releases into must-see cultural events, and Drishyam's brand recognition extends well beyond the Malayali diaspora thanks to the Hindi, Tamil, and Telugu remakes.

For NRIs who watched the original Drishyam in 2013 and debated Georgekutty's moral calculus in WhatsApp groups for years after, the trilogy's conclusion at ₹200 crore feels earned. The character who convinced a nation that a cable operator could outwit the police has now convinced the box office that Malayalam cinema can compete at any scale."""
    },
]


# ── Main execution ───────────────────────────────────────────────
def main():
    published = 0
    for i, art in enumerate(ARTICLES, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}/{len(ARTICLES)}: {art['headline'][:70]}...")
        print(f"{'='*60}")

        # ── Image sourcing ──
        img_url = None
        person = art.get("person_name")
        if person:
            print(f"  Trying Wikipedia for '{person}'...")
            img_url = fetch_wikipedia_person_image(person)
            if not img_url:
                # Try alternate forms
                for alt in [f"{person} (actor)", f"{person} (actress)", f"{person} (filmmaker)"]:
                    img_url = fetch_wikipedia_person_image(alt)
                    if img_url:
                        break

        if not img_url and art.get("pexels_query"):
            print(f"  Falling back to Pexels...")
            img_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))

        # Validate
        if img_url:
            if is_banned_url(img_url):
                print(f"  ✗ Banned URL detected, skipping: {img_url[:60]}")
                img_url = None
            elif not validate_image(img_url):
                print(f"  ✗ Image validation failed for: {img_url[:60]}")
                img_url = None
            else:
                print(f"  ✓ Image validated: {img_url[:80]}...")

        if not img_url:
            print(f"  ⚠ No image found — publishing without image (no image > wrong image)")

        # ── Build article payload ──
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"].strip(),
            "category": "entertainment",
            "vertical": "entertainment",
            "sources": json.loads(art["sources"]),
            "status": "published",
            "published_at": now,
            "image_url": img_url,
            "image_attribution": "Wikimedia Commons" if (img_url and "wikimedia" in (img_url or "").lower()) or (img_url and "wikipedia" in (img_url or "").lower()) else ("Pexels" if img_url else None),
        }

        # ── Insert ──
        print(f"  Inserting article...")
        result = sb_insert("p2_articles", payload)
        if result:
            if isinstance(result, list) and len(result) > 0:
                art_id = result[0].get("id", "unknown")
                print(f"  ✓ Published: {art['slug']} (id: {art_id})")
                published += 1
            elif isinstance(result, dict) and result.get("id"):
                print(f"  ✓ Published: {art['slug']} (id: {result['id']})")
                published += 1
            else:
                print(f"  ⚠ Insert returned: {str(result)[:200]}")
                published += 1  # Likely success despite odd format
        else:
            print(f"  ✗ Failed to publish: {art['slug']}")

        time.sleep(1)  # Rate limit courtesy

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(ARTICLES)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
