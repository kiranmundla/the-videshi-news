#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-01 batch."""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── Supabase config ─────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ───────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ───────────────────────────────────────────────
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
    """Fetch image from Pexels. Use curl internally since Python urllib gets 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                "-H", f"Authorization: {PEXELS_KEY}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
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
    """Verify image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Failed to download image: status={r.status_code}, size={len(r.content)}")
            return None

        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=20
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def sb_insert(table, data):
    """Insert row into Supabase and return the row."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=20
    )
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    else:
        print(f"  ✗ Insert into {table} failed: {r.status_code} {r.text[:300]}")
        return None


def sb_patch(table, filters, data):
    """Update a Supabase row."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=20
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ⚠ Patch {table} failed: {r.status_code} {r.text[:200]}")
    return False


# ── Articles ────────────────────────────────────────────────────
articles = []

# ─────────────────────────────────────────────────────────────────
# ARTICLE 1: Suman Kalyanpur Tribute
# ─────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Suman Kalyanpur, the Voice That Rivalled Lata Mangeshkar's, Has Died at 89. NRI Families Are Mourning a Soundtrack.",
    "subheadline": "The playback legend behind 'Aaj Kal Tere Mere Pyar Ke Charche' and 'Na Na Karte Pyar' shaped the sonic memory of an entire diaspora generation. She spent her final days listening to her own songs.",
    "slug": "suman-kalyanpur-death-89-playback-singer-golden-era-nri-tribute-20260601",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Bollywood Hungama", "Filmfare", "The Hindu Business Line",
        "Livemint", "PTI", "Radio City"
    ]),
    "image_person": "Suman Kalyanpur",
    "image_search_fallback": "vintage Indian music recording studio microphone",
    "image_attribution": "Wikimedia Commons",
    "body": """Suman Kalyanpur, one of the most distinctive and beloved voices in the history of Indian playback singing, passed away on Sunday evening at her Mumbai residence. She was 89. The singer, whose voice was so pure and crystalline that it was routinely mistaken for Lata Mangeshkar's, had been unwell for several weeks. According to her biographer Mangala Khadilkar, Kalyanpur spent her final days at home in Lokhandwala, listening to her own recordings.

"It happened around 8 pm. She passed away peacefully," Khadilkar told PTI. "I am going to remember what a gentle person Suman Tai was. Her voice — its sweetness was so different, soft and gentle, and touched your heart instantly."

## A Voice That Defined Bollywood's Golden Age

For three decades, from the mid-1950s through the 1980s, Kalyanpur was one of Hindi cinema's most prolific playback voices. Songs like *Na Na Karte Pyar Tumhin Se*, *Na Tum Humein Jaano*, *Ajhun Na Aaye Baalma*, and the iconic *Aaj Kal Tere Mere Pyar Ke Charche* became the emotional architecture of millions of Indian households — including those that would eventually scatter across the United States, the United Kingdom, and Canada.

Born Suman Hemmadi in 1937 in Bhawanipur, Bangladesh (then undivided India), she began her career at All India Radio in 1952, debuting in film with the Marathi movie *Shukrachi Chandni* a year later. Her Hindi cinema career took off with the 1954 film *Mangu*, and from there she became a fixture in the recording studios of Bollywood's greatest composers — Shankar Jaikishan, Naushad, Madan Mohan Kohli, S.D. Burman, Laxmikant-Pyarelal, and Kalyanji Anandji.

Her duets with Mohammed Rafi remain cornerstones of the Hindi film songbook. Songs like *Na Tum Humein Jaano* from *Baat Ek Raat Ki* (1962) and *Tumne Pukara Aur Hum Chale Aaye* continue to be played at Indian weddings and festivals worldwide.

## The Lata Comparison — and Why It Missed the Point

Throughout her career, Kalyanpur lived in the shadow of Lata Mangeshkar. Critics often compared the two, sometimes reducing Kalyanpur to a "backup" — a characterization that was both unfair and inaccurate. While their vocal registers overlapped, Kalyanpur possessed a softer, more intimate quality that composers specifically sought. She wasn't competing with Lata; she was offering something different.

Her versatility extended far beyond Hindi. She recorded in Marathi, Bengali, Kannada, Assamese, Gujarati, Odia, and Punjabi. Her Marathi songs — *Ketakichya Bani Tithe*, *Sang Kadhi Kalnar Tula* — remain beloved standards. She also had a significant body of work in devotional music, ghazals, and thumris.

## Why the Diaspora Is Mourning Differently

For NRI families, Suman Kalyanpur's songs occupy a particular emotional register. These are the songs their parents played on cassette tapes in apartments in New Jersey and houses in Leicester, the melodies that filled Diwali gatherings in Toronto and weekend picnics in the Bay Area. Her voice was rarely the loudest in the room, but it was always the one that made people stop talking and listen.

In an era before Spotify playlists and YouTube compilations, her music traveled through dubbed cassettes and Sunday morning requests on ethnic radio stations. For a generation of Indian Americans who grew up hearing these songs without fully understanding the lyrics, Kalyanpur's voice *was* the sound of heritage — gentle, persistent, and impossible to forget.

## A Quiet Departure

In recognition of her immense contribution to Indian music, the Government of India awarded her the Padma Bhushan in 2023. Maharashtra Chief Minister Devendra Fadnavis described her passing as the loss of "a divine voice that enriched India's musical heritage for more than six decades." NCP chief Sharad Pawar called it the end of "a golden era in Indian classical and light music."

Kalyanpur is survived by her daughter, Charu. Her last rites were performed at the Pawan Hans crematorium in Mumbai on Monday.

She was 89. Her songs will outlive everyone who mourns her today."""
})


# ─────────────────────────────────────────────────────────────────
# ARTICLE 2: Jacqueline Fernandez Money Laundering Trial
# ─────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Jacqueline Fernandez Will Stand Trial in a ₹200 Crore Money Laundering Case. The Court Said She Wasn't a Victim.",
    "subheadline": "A Delhi court has ordered charges against the Sri Lankan-born Bollywood actress, alleged conman Sukesh Chandrashekhar, and 15 others. She must appear in person on June 3.",
    "slug": "jacqueline-fernandez-money-laundering-trial-sukesh-chandrashekhar-200-crore-nri-20260601",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Bollywood Hungama", "Cinema Express", "Hindustan Times",
        "PTI", "Movie Talkies", "News Ei Samay"
    ]),
    "image_person": "Jacqueline Fernandez",
    "image_search_fallback": "Delhi court building India law",
    "image_attribution": "Wikimedia Commons",
    "body": """A Delhi court has ordered the framing of criminal charges against Bollywood actress Jacqueline Fernandez, alleged conman Sukesh Chandrashekhar, and 15 other individuals in connection with a ₹200 crore money laundering investigation. The ruling, delivered on Saturday by Additional Sessions Judge Prashant Sharma, formally advances the case to trial — a significant escalation for the Sri Lankan-born actress who has maintained she was an unwitting victim.

The court rejected that defense squarely. "Prima facie, there is sufficient material on record based upon which a strong suspicion is raised against all the accused," Judge Sharma stated. All 17 individuals have been ordered to appear physically at Patiala House Court on June 3 at 2:00 PM for the formal signing and framing of charges.

## The Case: Spoofed Calls, Luxury Gifts, and Tihar Jail

The case originates from a Delhi Police extortion complaint filed by Aditi Singh, wife of former Ranbaxy promoter Shivinder Singh. Investigators allege that Chandrashekhar, operating from inside Tihar Jail, spoofed phone numbers to impersonate senior government officials, conning Singh into transferring enormous sums. The total alleged proceeds of crime amount to ₹215 crores.

The Enforcement Directorate named Fernandez in a supplementary chargesheet, alleging she maintained regular contact with Chandrashekhar and received high-value luxury gifts — purchased with the illicit funds — through an intermediary named Pinky Irani. The gifts reportedly included designer handbags, jewellery, and significant cash transfers.

## "Unwitting Victim" or "Conscious Association"?

Fernandez's legal strategy centered on portraying herself as a victim who was misled by Chandrashekhar's fabricated identity. Her team argued she should not face prosecution under the Prevention of Money Laundering Act because she was never named as an accused in the original extortion case.

The court dismissed this as "meritless," ruling that an individual can be independently prosecuted under anti-money laundering laws regardless of their role in the underlying crime.

The ED's response was even more pointed. The agency told the court that Fernandez "remained in regular and sustained contact with Sukesh Chandrashekhar even after having knowledge of his criminal antecedents." The consistent receipt of benefits, the ED argued, "negated any claim of being an unwitting victim" and instead demonstrated "conscious association with the main perpetrator."

Earlier this month, Fernandez had attempted to turn approver in the case — essentially seeking to cooperate with the prosecution in exchange for potential leniency. The court allowed her to withdraw that plea.

## The NRI Dimension

Jacqueline Fernandez's career arc is itself a diaspora story. Born in Bahrain to a Sri Lankan father of Sinhalese and Portuguese descent, she won Miss Universe Sri Lanka in 2006 before relocating to Mumbai to pursue Bollywood. Her success — from *Race 2* to *Kick* to the *Housefull* franchise — made her one of the few non-Indian-born actresses to achieve sustained stardom in Hindi cinema.

For NRI audiences who followed her career as a fellow outsider-who-made-it-in-Bollywood, the trial raises uncomfortable questions about the intersection of celebrity culture, wealth, and accountability. The court's finding that receiving luxury gifts with awareness of their dubious origin constitutes money laundering — regardless of direct involvement in the underlying crime — sets a legal precedent that extends well beyond Fernandez.

## What Happens Next

The formal framing of charges on June 3 will mark the beginning of what is expected to be a lengthy trial. Separately, Chandrashekhar and his direct associates face even harsher charges under the Maharashtra Control of Organised Crime Act, though Fernandez is not implicated in that specific track.

The case is being closely watched by legal observers as a test of whether Indian anti-money laundering laws will be applied as aggressively to celebrity beneficiaries as they are to the direct perpetrators of financial crimes. For Fernandez, who is simultaneously shooting for a forthcoming Bollywood project and preparing for her Cannes 2026 appearance, the dual reality of red carpets and courtrooms has become unavoidable."""
})


# ─────────────────────────────────────────────────────────────────
# ARTICLE 3: Star Kids Class of 2026
# ─────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Bollywood's Children Are Graduating from NYU, Columbia, and Emory. They're Coming Home to Act.",
    "subheadline": "The Class of 2026 includes Chunky Panday's daughter from Tisch, Juhi Chawla's son from Columbia, Farah Khan's triplets headed to Babson, NYU, and Emory — and a daughter of Rohit Roy preparing for her Bollywood debut.",
    "slug": "bollywood-star-kids-class-2026-nyu-columbia-emory-nri-diaspora-education-20260601",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": [],
    "is_featured": False,
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Zoom TV Entertainment", "Bollywood Hungama", "Times of India"
    ]),
    "image_person": None,
    "image_search_fallback": "university graduation ceremony cap gown celebration",
    "image_attribution": "Pexels",
    "body": """It is graduation season, and Bollywood's next generation is collecting degrees from some of the most prestigious American universities before doing what their parents expected — and perhaps feared — all along: returning to Mumbai to become actors.

The Class of 2026 is stacked. Rysa Panday, Ananya Panday's younger sister, has completed her Bachelor of Fine Arts in Film, Video and Photographic Arts at NYU's Tisch School of the Arts. Juhi Chawla's son Arjun Mehta just celebrated his graduation from Columbia University. And Farah Khan's triplets — Diva, Anya, and Czar Kunder — are splitting across three American campuses: Babson College (Entrepreneurship and Finance), NYU (Economics and Data Science), and Emory University (Artificial Intelligence in Business), respectively.

Then there's Kiara Bose Roy, daughter of actor Rohit Roy and Manasi Joshi Roy, who has not only graduated but is reportedly being groomed for a Bollywood debut.

## The American Degree Pipeline

The pattern is now unmistakable. Bollywood's elite have spent the last decade routing their children through elite American universities — not as a detour from entertainment, but as preparation for it. The choices tell a story: Rysa's BFA from Tisch is a technical film education at one of the world's top programs. Anya Kunder's Economics-meets-Data Science degree reflects the increasingly analytics-driven entertainment business. Czar's AI-in-Business major at Emory anticipates a Bollywood that will be radically transformed by generative AI within the next five years.

Even Bobby Deol's son Aryaman, who graduated from NYU with honors earlier this year, has already returned to Mumbai to begin his acting career. The American education isn't replacing Bollywood ambitions — it's refining them.

## What NRI Families Recognize

For Indian American families who have spent years navigating the same admissions cycle — the SAT prep, the extracurricular portfolios, the nail-biting decisions between UC Berkeley and a private East Coast school — watching Bollywood families make identical choices carries a particular resonance.

These aren't families sending their children abroad because India lacks options. Dhirubhai Ambani International School, where the Kunder triplets just graduated, is one of Mumbai's most elite institutions. The choice to send children to American universities is deliberate and strategic — access to global networks, exposure to diverse creative industries, and the credential that still carries disproportionate weight in India's entertainment and business establishment.

The tuition at these institutions ranges from $60,000 to $85,000 annually. For Bollywood's top families, this is easily absorbed. But the signaling matters: it tells the industry that the next generation is globally trained, not just locally connected.

## The Return Migration Pattern

What makes this wave different from previous generations is the near-universal plan to return. Unlike the 1990s brain drain, where Indian graduates stayed in the US for tech careers and green cards, Bollywood's children are treating American universities as finishing schools, not permanent relocations.

Rysa Panday is already back with her family in France on vacation. Bobby Deol publicly celebrated his son's decision to "come back to Mumbai to become an actor" — framing the return as the point, not the exception.

This mirrors a broader trend among affluent Indian diaspora families: education abroad, career at home. The global Indian identity now includes an American or British degree as a standard accessory, not a life-altering choice.

## What Comes Next

The real test will be whether American-educated star kids bring something genuinely new to Bollywood — different sensibilities, storytelling techniques learned at Tisch, analytical frameworks from Columbia — or whether the degrees simply serve as expensive Instagram captions before they land the same three-film deal their parents would have secured anyway.

For NRI audiences watching from the other side of the same university experience, the answer will reveal a lot about whether Bollywood's relationship with America is deepening or decorative."""
})


# ── Publish all articles ────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"Articles to publish: {len(articles)}")
print(f"{'='*60}\n")

published = 0
for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:70]}... ---")

    # Image sourcing
    img_url = None
    img_attribution = article.pop("image_attribution", "The Videshi")
    person = article.pop("image_person", None)
    fallback_q = article.pop("image_search_fallback", None)

    if person:
        print(f"  Trying Wikipedia for '{person}'...")
        img_url = fetch_wikipedia_person_image(person)

    if not img_url and fallback_q:
        print(f"  Trying Pexels for '{fallback_q}'...")
        img_url = fetch_pexels_image(fallback_q)

    # Validate and upload
    final_image_url = None
    if img_url:
        if validate_image(img_url):
            art_id = str(uuid.uuid4())
            filename = f"{art_id}.jpg"
            final_image_url = upload_to_supabase_storage(img_url, filename)
            if not final_image_url:
                # Fall back to direct URL if from Wikipedia/Pexels
                if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                    final_image_url = img_url
                    print(f"  Using direct URL: {img_url[:80]}...")
        else:
            print(f"  ⚠ Image validation failed for {img_url[:80]}...")

    if final_image_url:
        article["image_url"] = final_image_url
        article["image_attribution"] = img_attribution
    else:
        print(f"  ⚠ No valid image found — publishing without image")

    # Insert
    row = sb_insert("p2_articles", article)
    if row:
        art_id = row.get("id", "unknown")
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {article['slug']}")

    time.sleep(1)  # Gentle delay between inserts

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")
