#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-29 batch"""

import json, os, sys, time, uuid, re, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False

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
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}) for {image_url[:80]}")
            return None
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return None
        
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def validate_image_url(url):
    """Verify URL returns a valid image."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned source: {url[:60]}")
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        print(f"  ✗ Banned params in URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # HEAD might not return Content-Length, try GET
        if 'image' in ct:
            return True
        print(f"  ⚠ Validation failed: CT={ct}, CL={cl}")
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False

def source_image(person_name=None, pexels_query=None, pexels_fallback=None, slug=""):
    """Source image following the hierarchy: Wikipedia -> Pexels -> None"""
    img_url = None
    attribution = "The Videshi"
    
    # Try Wikipedia first for person articles
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"
            # Upload to Supabase for permanence
            filename = f"{slug}.jpg"
            uploaded = upload_to_supabase_storage(img_url, filename)
            if uploaded:
                return uploaded, attribution
            # If upload fails, use direct Wikipedia URL (permanent)
            if 'upload.wikimedia.org' in img_url:
                return img_url, attribution
    
    # Try Pexels
    if pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "The Videshi"
            # Pexels URLs are permanent, can use directly
            return img_url, attribution
    
    return None, None

# ============================================================
# ARTICLES
# ============================================================

articles = []

# ------------------------------------------------------------------
# Article 1: Vashu Bhagnani ₹400 Crore Lawsuit
# ------------------------------------------------------------------
articles.append({
    "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit to Stop Varun Dhawan's Next Film From Releasing",
    "subheadline": "Puja Entertainment claims Tips Industries used iconic 'Chunari Chunari' and 'Ishq Sona Hai' from Biwi No.1 without permission. The Bombay High Court hearing could decide if Hai Jawani Toh Ishq Hona Hai opens on June 5.",
    "slug": "vashu-bhagnani-400-crore-lawsuit-tips-hai-jawani-varun-dhawan-biwi-no-1-songs-nri-20260529",
    "category": "entertainment",
    "image_person": "Varun Dhawan",
    "pexels_query": "Bollywood movie courtroom",
    "sources": json.dumps(["Bollywood Hungama", "IANS", "ANI", "Zoom TV"]),
    "body": """The biggest copyright battle in recent Bollywood memory just landed on the Bombay High Court's docket.

Producer **Vashu Bhagnani's Puja Entertainment** has filed a staggering ₹400 crore lawsuit against **Tips Industries Limited**, producers **Ramesh Taurani** and **Kumar S Taurani**, and filmmaker **David Dhawan** — alleging that the iconic songs *Chunari Chunari* and *Ishq Sona Hai* from the 1999 blockbuster **Biwi No.1** were used without authorization in the upcoming Varun Dhawan-starrer **Hai Jawani Toh Ishq Hona Hai**.

The stakes could not be higher. The film, which also stars **Mrunal Thakur** and **Pooja Hegde**, is set for a worldwide theatrical release on **June 5, 2026** — barely a week away. Puja Entertainment is seeking an emergency injunction to halt the release entirely.

## What the Lawsuit Claims

According to the press statement filed through Counsels V K Dubey Associates, Puja Entertainment is demanding:

- An **immediate halt** on the release, distribution, exhibition, streaming, and commercial exploitation of the film
- A **ban on all promotional material** containing the disputed songs
- **₹400 crore in damages** from Tips Industries
- An **additional ₹100 crore** if the defendants continue using the disputed works
- A **title change** — Puja Entertainment is also demanding that the film's name be altered

The legal filing has been described as potentially "one of the most explosive copyright battles in recent Bollywood history."

## The Back Story: Audio Rights vs. Visual Rights

The dispute traces back decades. When *Biwi No.1* was made in 1999, the agreements between the producers and Tips covered only audio rights. According to Bhagnani's lawyer, the arrangement never extended to visual or synchronization rights — a distinction that matters enormously when songs are recreated for new films.

"In 2018, Tips emailed us requesting visual rights," advocate Dubey told ANI. "Vashu Bhagnani had replied to them, but their conversation did not settle." The lawyer further claimed that Puja Entertainment subsequently sent a notice to Tips **cancelling the audio rights** previously granted, which would mean Tips has no valid license to use the songs in any form.

"If they are the lawful owners of the music rights, they must show their documents," Dubey said. "Justice will prevail, and the truth will come out."

## Why NRIs Should Pay Attention

This case is bigger than one film. It cuts to the heart of how Bollywood handles music rights — a system built on handshake deals and loosely worded agreements from the 1990s that is now colliding with modern copyright law. The outcome could set a precedent for dozens of planned remakes and song recreations currently in development across the industry.

For diaspora audiences who grew up with the *Biwi No.1* soundtrack — and who now represent a significant chunk of Bollywood's overseas box office — the case raises uncomfortable questions about who actually owns the songs they love.

The Bombay High Court has permitted the filing and a hearing is expected soon. Whether *Hai Jawani Toh Ishq Hona Hai* makes its June 5 date may depend entirely on what happens in that courtroom."""
})

# ------------------------------------------------------------------
# Article 2: Patriot hitting OTT
# ------------------------------------------------------------------
articles.append({
    "headline": "Mammootty and Mohanlal's Patriot Hits ZEE5 on June 5. It Cost ₹140 Crore. The Theatres Couldn't Save It.",
    "subheadline": "Malayalam cinema's most anticipated reunion in two decades underperformed at the box office. Now NRIs who missed it get a second chance — in five languages.",
    "slug": "patriot-mammootty-mohanlal-zee5-ott-june-5-five-languages-nri-20260529",
    "category": "entertainment",
    "image_person": "Mammootty",
    "pexels_query": "Indian spy thriller cinema",
    "sources": json.dumps(["SacNilk", "ZEE5", "The Indian Express", "The Hindu", "India Today"]),
    "body": """The most hyped Malayalam film of 2026 is coming to your living room — and that is both good news and a quiet admission of defeat.

**Patriot**, the political-espionage thriller that brought **Mammootty** and **Mohanlal** together on screen for the first time in nearly two decades, will begin streaming on **ZEE5 on June 5, 2026** — in Malayalam, Tamil, Telugu, Kannada, and Hindi.

The film, directed by **Mahesh Narayanan** and featuring an ensemble that also includes **Fahadh Faasil**, **Kunchacko Boban**, **Nayanthara**, and **Revathy**, arrived in theatres with expectations that bordered on the unreasonable. It had a reported budget of **₹125 to ₹140 crore**, making it one of the most expensive Malayalam films ever produced.

## What Went Wrong at the Box Office

The numbers told an uncomfortable story. Despite a strong opening weekend fueled by the sheer novelty of seeing Malayalam cinema's two biggest stars share the screen, *Patriot* could not sustain momentum. The film went into free fall on weekdays, and the theatrical window closed far sooner than anyone expected.

For a film of this budget, breaking even required a worldwide gross that the ticket counters simply could not deliver. The quick pivot to OTT — barely six weeks after its theatrical release — confirms what the numbers already suggested.

## But the Film Itself Is Good

Here is what makes this story more complicated than a straightforward flop narrative: *Patriot* is actually well-made.

**The Indian Express** gave it 3 out of 5 stars, praising Narayanan for "not being intimidated by Mammootty and Mohanlal's superstardom" and the two legends for "simply trusting the director's vision." **India Today** went higher at 3.5 out of 5, calling it "spy cinema done right" with "unforgettable whistle-worthy moments."

**The Hollywood Reporter India** noted that the film "does a lot of things right" and "comes close to achieving the sky-high expectations." The consensus: a competent, ambitious thriller that stumbled commercially under the weight of its own hype.

## Why This Matters for the Diaspora

For NRIs, the June 5 ZEE5 premiere is arguably the best way to experience *Patriot*. Here is why:

**Language accessibility**: The film will be available in five languages simultaneously, meaning Tamil, Telugu, and Hindi-speaking diaspora audiences who might not have sought it out in Malayalam-only theatrical runs now have easy access.

**No spoilers yet**: Unlike many theatrical releases that get dissected on social media within hours, *Patriot's* relatively muted theatrical run means most international audiences are coming in fresh.

**The star power**: Watching Mammootty and Mohanlal share a frame is a once-in-a-generation experience. Their last meaningful collaboration was over 15 years ago. Regardless of what the box office said, this alone makes it essential viewing.

With **Sushin Shyam's** score and **Manush Nandan's** cinematography, *Patriot* is the kind of film that was perhaps always destined to find its real audience on streaming — where a ₹125 crore budget matters less than whether the story holds you for two and a half hours."""
})

# ------------------------------------------------------------------
# Article 3: Salman Khan's Maatrubhumi screening
# ------------------------------------------------------------------
articles.append({
    "headline": "Salman Khan Screened Maatrubhumi for Bollywood's Biggest Directors. Subhash Ghai Called It a 'Must-Watch.'",
    "subheadline": "Sooraj Barjatya, Kabir Khan, David Dhawan, and Riteish Deshmukh watched the rough cut of the Galwan Valley-inspired war drama. A release date still hasn't been announced.",
    "slug": "salman-khan-maatrubhumi-rough-cut-screening-subhash-ghai-must-watch-galwan-nri-20260529",
    "category": "entertainment",
    "image_person": "Salman Khan",
    "pexels_query": None,
    "sources": json.dumps(["Bollywood Hungama", "IANS", "Subhash Ghai (social media post)"]),
    "body": """Salman Khan's most politically sensitive film just passed its first industry test.

On the evening of May 28, **Salman Khan** hosted a private screening of the rough cut of **Maatrubhumi: May War Rest in Peace** — the Galwan Valley-inspired war drama that has been delayed, retitled, and caught in geopolitical crossfire for months. The guest list read like a who's who of Bollywood's directorial establishment.

**Subhash Ghai**, **Sooraj Barjatya**, **David Dhawan**, **Kabir Khan**, **Riteish Deshmukh**, and producer **Siddharth Roy Kapur** watched the early cut alongside Salman and co-star **Chitrangda Singh**. Director **Apoorva Lakhia** was also present.

## The Verdict from the Room

Ghai, never one to hold back, went straight to social media afterward. "It was so beautiful to see my favourite directors together at Food Square today to watch a rough cut of Apoorva Lakhia's film MAATRUBHUMI," he wrote, describing it as "a touching story of soldiers of India and China with their respective emotions for their nations and their families with a theme of mutual peace and respect."

He called it "truly a must-watch."

Coming from the man who directed *Taal*, *Pardes*, and *Karma*, that is not a casual endorsement.

## The Troubled Journey

The film's road to this point has been anything but smooth. Originally titled **Battle of Galwan**, the project was directly inspired by the **2020 Galwan Valley clash** between Indian and Chinese troops — a border confrontation that left 20 Indian soldiers dead and remains a deeply sensitive geopolitical flashpoint.

After the teaser dropped in December 2025 (timed to Salman's birthday), Chinese state-backed media outlet **Global Times** published critical coverage. Reports then surfaced that the filmmakers were urged to soften the political tone and reduce direct references that could escalate diplomatic tensions.

What followed was a 40-day reshoot period, a title change from *Battle of Galwan* to the more diplomatic *Maatrubhumi: May War Rest in Peace*, and an indefinite postponement of the April 17 release date. The film continues to navigate defence-related clearances and CBFC certification.

## Why the Industry Screening Matters

Salman Khan does not show rough cuts to friends unless he is confident in the product — and unless he needs allies. By assembling Bollywood's most respected names and getting their public endorsement on record, he is doing two things: building advance word-of-mouth and creating an industry consensus that the film deserves a fair release.

The directors in that room — Sooraj Barjatya (*Maine Pyar Kiya*), Kabir Khan (*Bajrangi Bhaijaan*), David Dhawan (*Judwaa*) — represent decades of Salman Khan collaborations. Their presence is strategic.

## The Diaspora Angle

For NRIs, *Maatrubhumi* sits at the intersection of patriotism and pragmatism. The Galwan Valley clash resonated deeply with the Indian diaspora — vigils were held in multiple US and UK cities, and the story of the 20 fallen soldiers was widely shared across WhatsApp groups and community forums.

A release date has not been announced, but reports suggest an **Independence Day weekend** window could be in play. For a film about soldiers defending a border, the timing would be poetic — if the clearances come through."""
})

# ------------------------------------------------------------------
# Article 4: Anushka Sharma Yoga Wear
# ------------------------------------------------------------------
articles.append({
    "headline": "Anushka Sharma Invested in Virat Kohli's Sportswear Company. Now She's Building a Yoga Line Under His Brand.",
    "subheadline": "The actress picked up a minority stake in Agilitas Sports and will co-develop One8 Yoga — launching on International Yoga Day, June 21. Her last film was six years ago.",
    "slug": "anushka-sharma-agilitas-sports-one8-yoga-virat-kohli-investment-nri-20260529",
    "category": "entertainment",
    "image_person": "Anushka Sharma",
    "pexels_query": "yoga activewear fashion",
    "sources": json.dumps(["Economic Times", "Bollywood Hungama", "Franchise India", "Apparel Resources"]),
    "body": """Anushka Sharma has not made a film since 2018. She has, however, been quietly building something else.

The actress has acquired a **minority stake in Agilitas Sports**, the Indian sportswear company co-founded by former **Puma India** executives — and the same company where her husband **Virat Kohli** is already an investor and co-founder. As part of the deal, Sharma will co-develop a new **yoga wear range** under Kohli's **One8** sportswear brand, with a launch planned for **June 21 — International Yoga Day**.

"Anushka is partnering with Agilitas by investing capital in the company and building yoga-wear," confirmed **Abhishek Ganguly**, Agilitas Sports' co-founder and CEO, though he declined to share the deal's financial details.

## The Business Behind It

The numbers give context. In 2025, Kohli had acquired his own minority stake in Agilitas for approximately **₹40 crore** after ending his eight-year, **₹110 crore** association with German sportswear giant Puma. As part of that deal, Agilitas also acquired the **One8 brand** — Kohli's personal sportswear franchise that has become one of India's most recognized athleisure labels.

Agilitas itself is no scrappy startup. Founded by **Abhishek Ganguly**, **Atul Bajaj**, and **Amit Prabhu** — all former Puma India executives — the company runs a vertically integrated operation spanning manufacturing, branding, retail, and distribution. It is backed by **Convergent Finance** and **Nexus Venture Partners**, has acquired long-term Lotto licensing rights across multiple markets, and purchased footwear manufacturer **Mochiko Shoes**.

Adding Anushka Sharma to this mix is not just celebrity endorsement — it is a strategic expansion into the women's activewear category, specifically yoga and wellness apparel, one of the fastest-growing segments in Indian sportswear.

## The Bollywood Parallel

There is something quietly significant about this announcement coming from Anushka Sharma specifically.

Her last theatrical release was **Zero** in 2018 alongside Shah Rukh Khan and Katrina Kaif. In the seven years since, she has stayed almost entirely out of the public eye — no comeback announcements, no Netflix shows, no buzzy Instagram campaigns. While peers like Deepika Padukone, Alia Bhatt, and Priyanka Chopra have juggled acting careers with brand empires, Anushka has taken the opposite approach: step back from acting entirely, focus on family, and build businesses.

She previously founded the production house **Clean Slate Filmz** (which produced *Paatal Lok* and *Bulbbul* for Amazon Prime) and the clothing brand **Nush**. The Agilitas investment represents her most significant business move since.

## Why NRIs Should Watch This

For diaspora audiences, the Kohli-Sharma business play reflects a broader shift in how Indian celebrity power is being deployed.

The global yoga and wellness market is projected to be worth over **$87 billion by 2027**, and Indian diaspora communities in the US, UK, and Canada are among the most enthusiastic yoga practitioners worldwide. A premium Indian yoga wear brand with Anushka Sharma's name attached — launching on International Yoga Day — is positioned squarely at that intersection.

**One8 Yoga** could become the first Indian-origin activewear brand to meaningfully compete in yoga-specific apparel internationally. Whether it gets there depends on product quality more than star power — but the foundation is serious."""
})

# ============================================================
# PUBLISH
# ============================================================

now = datetime.now(timezone.utc).isoformat()

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")
    
    # Source image
    img_url, img_attr = source_image(
        person_name=art.get('image_person'),
        pexels_query=art.get('pexels_query'),
        slug=art['slug']
    )
    
    # Validate
    body = art['body'].strip()
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    
    if word_count < 400:
        print(f"  ✗ REJECTED — body too short ({word_count} words)")
        continue
    
    if len(art['headline']) > 200:
        print(f"  ⚠ Headline too long ({len(art['headline'])} chars), truncating")
        art['headline'] = art['headline'][:197] + "..."
    
    if len(art.get('subheadline', '')) < 15:
        print(f"  ✗ REJECTED — subheadline too short")
        continue
    
    # Build record
    record = {
        "headline": art['headline'],
        "subheadline": art['subheadline'],
        "slug": art['slug'],
        "body": body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": art.get('sources', '[]'),
        "image_url": img_url if img_url else None,
        "image_attribution": img_attr if img_attr else None,
        "urgency": "medium",
        "tags": [],
        "score_total": 60,
        "is_featured": False,
        "is_editorial": False,
    }
    
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print("\n✅ Entertainment writer batch complete.")
