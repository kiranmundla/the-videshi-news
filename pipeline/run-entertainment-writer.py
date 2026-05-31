#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 batch"""

import json, os, sys, time, re, uuid, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
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
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Insert error {r.status_code}: {r.text[:200]}")
        return None

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch error {r.status_code}: {r.text[:200]}")
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
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch from Pexels using curl (Python urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check that URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        # Use GET with stream to actually check content
        r = requests.get(url, timeout=15, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        if r.status_code == 200 and ('image' in ct or 'octet' in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp'))):
            chunk = r.raw.read(6000)
            r.close()
            if len(chunk) >= 5000:
                print(f"  ✓ Image validated: {len(chunk)}+ bytes, {ct}")
                return True
            else:
                print(f"  ⚠ Image too small: {len(chunk)} bytes")
        else:
            print(f"  ⚠ Image check: status={r.status_code}, ct={ct}")
            r.close()
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── ARTICLES ──

articles = []

# ─────────────────────────────────────────────
# ARTICLE 1: Bobby Deol's Bandar
# ─────────────────────────────────────────────
articles.append({
    "headline": "Bobby Deol's Bandar Premieres at TIFF, Hits Theatres June 5. Anurag Kashyap's Crime Thriller Is His Most Daring Role Yet.",
    "subheadline": "After Animal reinvented his career, Bobby Deol plays a faded TV star accused of rape in Anurag Kashyap's raw, TIFF-premiered crime thriller — and he's never been more compelling.",
    "slug": "bobby-deol-bandar-anurag-kashyap-tiff-premiere-june-5-release-nri-20260531",
    "category": "entertainment",
    "person": "Bobby Deol",
    "pexels_fallback": "prison cell dark thriller",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Bandar_(film)"},
        {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"}
    ]),
    "diaspora_angle": "Bobby Deol's career resurgence resonates with NRI audiences who grew up watching him in the 90s. His son Aryaman's NYU finance-to-acting pivot mirrors many diaspora career conversations. The TIFF premiere gives this indie crime thriller global cred.",
    "tags": ["Bobby Deol", "Bandar", "Anurag Kashyap", "TIFF", "crime thriller", "June releases", "Bollywood"],
    "body": """Bobby Deol's career arc over the past three years has been one of Bollywood's most unlikely second acts. From the villainous Abrar in Sandeep Reddy Vanga's *Animal* to the menacing patriarch in *The Ba***ds of Bollywood*, the actor who spent a decade in the wilderness has become one of Hindi cinema's most sought-after performers. Now, with *Bandar*, he takes on what may be his most demanding role yet — and he's doing it under the direction of Anurag Kashyap.

*Bandar* (English title: *Monkey in a Cage*) follows Samar Mehra, a once-celebrated television actor whose career and life unravel when his ex-girlfriend accuses him of rape after he cuts off contact. Proclaiming his innocence, Samar is thrust into a violent, deeply corrupt prison system where survival becomes a daily negotiation. The film is inspired by real events and was written by Sudip Sharma and Abhishek Banerjee — names that should make any Bollywood watcher sit up and pay attention.

## The TIFF Seal of Approval

The film premiered in the Special Presentations Program at the 2025 Toronto International Film Festival on September 6, earning strong critical attention for its unflinching treatment of false accusations, media trials, and the Indian prison system. For NRI audiences who watched the TIFF premiere coverage last fall, the theatrical release on June 5 has been a long time coming. The 140-minute crime thriller lands in cinemas worldwide, distributed by Zee Studios.

## A Cast Built for This Story

Kashyap has assembled an ensemble that reads like a festival director's dream. Alongside Bobby Deol, the cast includes Sanya Malhotra, Saba Azad, Sapna Pabbi, Raj B. Shetty (the Kannada powerhouse behind *Garuda Gamana Vrishabha Vahana*), Riddhi Sen, South Indian star Indrajith Sukumaran, and Jitendra Joshi. Music comes from a murderer's row of talent: Amit Trivedi, Vishal Mishra, and Payal Dev, with a debut Bollywood song from Salman Khan's nephew Ayaan Agnihotri.

## Bobby Deol's Personal Reckoning

In recent interviews, Bobby has been characteristically candid about the role. He spoke about growing up in a patriarchal society and how his protectiveness of his sisters shaped his understanding of the film's complex gender dynamics. "Stories are not merely created as fiction," he said. "Women experience more suffering than men do. It is still a reality. Yet, there are men who have faced certain injustices."

The actor also opened up about being replaced in *Jab We Met* by Shahid Kapoor — a wound that he says transformed his approach to acting. "The hurt and anger became my strength," he reflected.

## Why NRI Audiences Should Watch

*Bandar* sits at the intersection of several conversations that resonate across the Indian diaspora: the #MeToo movement's complexities, the presumption of guilt in the age of social media, and the nightmarish reality of India's undertrial prison system. Kashyap, whose *Gangs of Wasseypur* and *Dev.D* are staples of every NRI's Bollywood education, brings his signature raw visual style to a story that refuses to take easy sides.

Bobby Deol's sons Aryaman (a New York University finance graduate who chose acting over Wall Street) and Dharam have both expressed interest in following the family into Bollywood — a third generation of Deols that NRI families will be watching closely.

*Bandar* releases in theatres worldwide on June 5, 2026."""
})

# ─────────────────────────────────────────────
# ARTICLE 2: Manoj Bajpayee's Governor
# ─────────────────────────────────────────────
articles.append({
    "headline": "Manoj Bajpayee Is the Man Who Stopped India From Going Bankrupt. Governor Releases June 12.",
    "subheadline": "The film tells the untold story of RBI Governor S. Venkitaramanan and the secret 60-ton gold airlift that saved India's economy in 1991 — the crisis that shaped an entire generation of NRI migration.",
    "slug": "manoj-bajpayee-governor-rbi-1991-crisis-gold-airlift-june-12-nri-20260531",
    "category": "entertainment",
    "person": "Manoj Bajpayee",
    "pexels_fallback": "Reserve Bank of India building Mumbai",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Nation Press", "url": "https://nationpress.com"},
        {"name": "NewKerala", "url": "https://www.newkerala.com"}
    ]),
    "diaspora_angle": "The 1991 economic crisis is the origin story of an entire generation of Indian emigration. NRIs in finance, banking, and tech will find personal resonance in a story about the man whose decisions shaped why they left India. The gold airlift is a little-known chapter that diaspora audiences deserve to know.",
    "tags": ["Manoj Bajpayee", "Governor", "RBI", "1991 crisis", "economic history", "June releases", "Bollywood"],
    "body": """Every Indian who left for America, Britain, or the Gulf in the early 1990s carries a version of the same origin story: India was broke, opportunities were scarce, and leaving felt like the only rational choice. What most don't know is exactly how close India came to complete economic collapse — and who prevented it.

*Governor*, releasing June 12, tells that story. Manoj Bajpayee plays S. Venkitaramanan, the Reserve Bank of India Governor whose unconventional decisions — including a covert 60-ton gold airlift to secure emergency foreign exchange — pulled the country back from the brink of sovereign default in 1991.

## The Crisis That Made the Diaspora

For the Indian diaspora, 1991 isn't just economic history — it's personal. The Gulf War disrupted remittances from Kuwait and Iraq. Foreign exchange reserves dropped below $1 billion, barely enough to cover two weeks of imports. India's credit rating was slashed. The government quietly pledged 67 tons of gold to the Bank of England and the Union Bank of Switzerland to raise $600 million in emergency loans.

The New Economic Policy that followed — liberalization, privatization, globalization — reshaped India's economy and, in turn, the trajectory of millions of Indians who would emigrate to the West in the years that followed. If you're reading this from San Jose, New Jersey, or London, the 1991 crisis is part of why you're there.

## Why Bajpayee Was "Scared and Nervous"

At the trailer launch, Bajpayee was unusually candid about the demands of the role. "My maths was not good," he admitted. "I don't come from an economics background. The financial terminology, the Tamil diction — it was a very demanding role."

The actor, who has perfected accents from Bihar to UP across dozens of films, spent months studying Venkitaramanan's speech patterns and the mechanics of central banking. Director Chinmay Mandlekar — best known for the Marathi blockbuster *Dhurala* and the acclaimed *Pawankhind* — pushed Bajpayee to internalize the bureaucratic weight of decisions that carried the fate of 850 million people.

## A Story Hindi Cinema Has Never Told

"When we talk about heroes, we usually make films on army officers or politicians," Bajpayee said. "But I felt that for the first time, we are talking about a man who was working behind the curtain from a new sector — the financial machinery that drives the country."

The film also stars Adah Sharma (who was a revelation in *The Kerala Story*) as a journalist investigating the crisis. Music by Amit Trivedi and lyrics by Javed Akhtar add further pedigree to a production that appears to take its subject as seriously as the story demands.

## The Box Office Battle

*Governor* arrives on June 12 in a three-way clash with Imtiaz Ali's *Main Vaapas Aaunga* (starring Diljit Dosanjh) and Kangana Ranaut's *Bharat Bhhagya Viddhaata*. Producer Vipul Amrutlal Shah joked at the trailer launch that he's wearing "boxing gloves" for the release. The producer, who backed *The Kerala Story*, is betting that a story about economic governance can hold its own against a partition love story and a 26/11 drama.

For NRI audiences — particularly those in finance, banking, and tech who have a lived understanding of India's economic transformation — *Governor* may be the rare Bollywood film that speaks directly to their professional and personal histories. The 1991 crisis didn't just change India's economy. It changed who left, where they went, and what India became.

*Governor* releases in theatres on June 12, 2026."""
})

# ─────────────────────────────────────────────
# ARTICLE 3: Ishaan Khatter at Biarritz
# ─────────────────────────────────────────────
articles.append({
    "headline": "Ishaan Khatter Will Judge Films Alongside Kristen Stewart at Biarritz. He's the Only Indian on the Jury.",
    "subheadline": "From Majid Majidi's debut to the Oscar shortlist with Homebound, Ishaan Khatter's global trajectory just reached a new milestone — a jury seat at one of Europe's most important emerging cinema festivals.",
    "slug": "ishaan-khatter-biarritz-film-festival-jury-kristen-stewart-only-indian-nri-20260531",
    "category": "entertainment",
    "person": "Ishaan Khatter",
    "pexels_fallback": "film festival red carpet jury",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Indulge Express", "url": "https://www.indulgexpress.com"},
        {"name": "ANI News", "url": "https://www.aninews.in"}
    ]),
    "diaspora_angle": "Ishaan Khatter sitting on a jury alongside Kristen Stewart represents Indian cinema being invited to shape global taste, not just be exhibited. His Gold House recognition and Oscar shortlist further demonstrate diaspora cultural capital in the West.",
    "tags": ["Ishaan Khatter", "Biarritz Film Festival", "Kristen Stewart", "film jury", "Indian cinema global", "diaspora representation"],
    "body": """The list of Indian actors who have sat on a major international film festival jury is short. Sharmila Tagore at Cannes. Nandita Das at Venice. Deepika Padukone at the Oscars. Now add Ishaan Khatter to that list.

The 27-year-old has been invited to serve on the jury of the Biarritz Film Festival — Nouvelles Vagues 2026, alongside a panel chaired by Kristen Stewart. He is the only Indian actor on this year's jury.

## The Company He Keeps

The jury lineup reads like a who's who of global cinema's next wave: Whitney Peak (the Canadian actress known for *Gossip Girl* and *Hocus Pocus 2*), French actor-director Raphaël Quenard, French filmmaker Nathan Ambrosioni, actress Suzy Bemba, Italian director Carolina Cavalli, and British actress Esmé Creed-Miles. Stewart, who has evolved from *Twilight* to directing and producing, chairs the panel.

The Biarritz Film Festival — Nouvelles Vagues, now in its fourth edition, has positioned itself as Europe's premier platform for emerging voices and youth-centric cinema. Running June 23–28 in the coastal Basque city, the festival attracts filmmakers from across the world. Being invited to judge — rather than attend or screen — places Ishaan in the rare position of shaping which emerging filmmakers receive global attention.

## A Career Built for This Moment

Ishaan Khatter's path to a French jury table was not the conventional Bollywood trajectory. He debuted in 2018 with *Beyond the Clouds*, directed by the legendary Iranian filmmaker Majid Majidi — a choice that signaled his ambitions from the start. While most Bollywood newcomers chase commercial hits, Ishaan chose a filmmaker who speaks the language of global arthouse cinema.

What followed was a deliberate blend of commercial and international work. Mira Nair's *A Suitable Boy* for BBC introduced him to British and American audiences. A cameo in Adam McKay's *Don't Look Up* — alongside Leonardo DiCaprio and Jennifer Lawrence — put him on Hollywood's radar. And then came *Homebound*, which became India's official entry to the Oscars and reached the Academy shortlist, earning critical attention that most Indian actors never achieve.

## The Gold House Recognition

Earlier in 2026, Ishaan was featured on the Gold House Gold 100 list — an annual roster of the most influential Asian and Pacific Islander figures across industries. He was the only Indian male actor to make this year's lineup, alongside leaders in tech, business, and entertainment from across the Asian diaspora.

For NRI audiences who have followed Ishaan's career — from his mother Neelima Azeem's classical dance lineage to his half-brother Shahid Kapoor's commercial dominance — his jury invitation represents something larger than one actor's achievement. It represents Indian cinema being invited to the table where global taste is shaped, not merely displayed.

## What's Next

Ishaan isn't slowing down on the home front. He's currently filming *Jugaadu*, a comic caper directed by Palash Vaswani. Season 2 of *The Royals* — which saw a directorial change recently, with *Darlings* director Jasmeet K. Reen replacing Nupur Asthana — is also on the horizon.

But the Biarritz jury seat is the kind of milestone that changes an actor's international standing permanently. When the films are screened in that coastal French city from June 23 to 28, Ishaan Khatter won't just be watching. He'll be deciding.

The Biarritz Film Festival — Nouvelles Vagues runs June 23–28, 2026, in Biarritz, France."""
})

# ── PUBLISH ──

published_count = 0
for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Image sourcing — Wikipedia first for person articles
    person = art.pop("person", None)
    pexels_fb = art.pop("pexels_fallback", None)
    img_url = None

    if person:
        img_url = fetch_wikipedia_person_image(person)

    if not img_url and pexels_fb:
        img_url = fetch_pexels_image(pexels_fb)

    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, skipping image")
        img_url = None

    # Create topic first (required FK)
    topic_id = str(uuid.uuid4())
    topic = {
        "id": topic_id,
        "canonical_title": art["headline"][:200],
        "vertical": "entertainment",
        "urgency": "standard",
        "score_diaspora": 75,
        "score_significance": 70,
        "score_recency": 85,
        "score_source_avail": 80,
        "score_total": 78,
        "signal_count": 1,
        "status": "published",
        "category": "entertainment"
    }
    topic_result = sb_insert("p2_topics", topic)
    if not topic_result:
        print(f"  ✗ Failed to create topic for {art['slug']}")
        continue

    # Build article record
    now = datetime.now(timezone.utc).isoformat()
    
    # Fix image_attribution logic
    img_attr = "The Videshi"
    if img_url:
        if "wikimedia" in img_url.lower() or "wikipedia" in img_url.lower():
            img_attr = "Wikimedia Commons"
        elif "pexels" in img_url.lower():
            img_attr = "Pexels"

    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"],
        "sources": json.loads(art["sources"]),
        "status": "published",
        "published_at": now,
        "topic_id": topic_id,
        "image_url": img_url,
        "image_attribution": img_attr,
        "vertical": "entertainment",
        "diaspora_angle": art.get("diaspora_angle", "Relevant to Indian diaspora audiences in the US, UK, and Canada."),
        "tags": art.get("tags", []),
        "urgency": "daily",
        "word_count": len(art["body"].split())
    }

    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published_count += 1
    else:
        print(f"  ✗ FAILED: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done! Published {published_count}/{len(articles)} articles.")
