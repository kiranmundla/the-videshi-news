#!/usr/bin/env python3
"""
Entertainment writer for The Videshi — June 6, 2026
4 articles:
1. Governor — Manoj Bajpayee as RBI Governor during 1991 crisis (June 12 release)
2. June 2026: Bollywood's biggest month — 9 releases, ₹1,400 crore at stake
3. Bharat Bhagya Vidhata — Kangana Ranaut 26/11 nurse story (June 12 release)
4. What to Watch This Week streaming roundup (June 8–14)
"""

import os, json, time, uuid, requests, urllib.parse, subprocess
from datetime import datetime, timezone
from io import BytesIO

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def sb_headers():
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# ── image sourcing ──────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w,
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_and_compress(url, max_width=1200, quality=80):
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct and len(r.content) < 5000:
            print(f"  ⚠ Not a valid image (Content-Type: {ct}, size: {len(r.content)})")
            return None
        from PIL import Image
        img = Image.open(BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        data = buf.getvalue()
        size_kb = len(data) / 1024
        print(f"  ✓ Compressed: {img.width}x{img.height}, {size_kb:.0f} KB")
        if len(data) < 5000:
            print(f"  ⚠ Too small after compression ({len(data)} bytes), skipping")
            return None
        return data
    except Exception as e:
        print(f"  ⚠ Download/compress error: {e}")
        return None

def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    candidates = []
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})
    if topic_queries:
        for q in topic_queries[:3]:
            commons = fetch_wikimedia_commons_images(q)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
            time.sleep(0.5)
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "relevance": 1})

    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:70]}...")
        img_bytes = download_and_compress(c["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            sb_url = upload_to_supabase(img_bytes, filename)
            if sb_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return sb_url, attr
        time.sleep(1)

    print("  ✗ No image found from any source")
    return None, None

def insert_article(article):
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=sb_headers(), timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Governor — Manoj Bajpayee as RBI Governor
# ═══════════════════════════════════════════════════════════════════
def write_governor():
    print("\n═══ Article 1: Governor ═══")
    slug = "governor-manoj-bajpayee-rbi-1991-crisis-chinmay-mandlekar-nri-20260606"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Manoj Bajpayee",
        topic_queries=["Manoj Bajpayee actor", "Reserve Bank of India building Mumbai"],
        pexels_query="Indian central bank finance",
        slug=slug
    )

    headline = "Manoj Bajpayee Is Playing the Man Who Kept India from Going Bankrupt. Most Indians Don't Know His Name."
    subheadline = "Governor, releasing June 12, dramatises the 1991 balance-of-payments crisis through the eyes of RBI Governor S. Venkitaramanan — the bureaucrat who shipped India's gold reserves abroad to keep the country solvent."

    body = """In 1991, India had foreign reserves that could cover roughly two weeks of imports. The country was days away from defaulting on its international obligations. The man tasked with preventing that collapse was S. Venkitaramanan, the 18th Governor of the Reserve Bank of India — a career bureaucrat who was not anyone's first choice for the job, and who quietly made the most consequential financial decision in modern Indian history: airlifting 47 tonnes of gold to the Bank of England as collateral for an emergency loan.

That story is now a film. Governor, directed by Chinmay Mandlekar and produced by Vipul Amrutlal Shah, releases in theatres on June 12, 2026. Manoj Bajpayee plays the titular Governor, and everything about the project suggests this is the kind of serious, research-driven Hindi cinema that doesn't come around often enough.

## The Story Behind the Film

The 1991 crisis is one of those pivotal moments that every Indian over 40 remembers viscerally — the queues, the scarcity, the sudden disappearance of imported goods from shelves — but that most Indians under 30 have never been taught properly. India's balance of payments had deteriorated through the late 1980s. By the time Venkitaramanan took charge of the RBI in December 1990, the country was spending far more on imports than it was earning from exports, and foreign reserves had dwindled to dangerously low levels.

What followed was extraordinary. Under Venkitaramanan's watch, India pledged its gold reserves — physically shipping them to London — to raise approximately $405 million. The move was politically explosive. Pledging the nation's gold felt, to many, like mortgaging India's sovereignty. But the alternative was a sovereign default that would have locked the country out of international markets for years.

The gold pledge bought India time. That breathing room allowed Finance Minister Manmohan Singh and Prime Minister P.V. Narasimha Rao to launch the economic liberalisation that reshaped the country. Every software company in Bengaluru, every call centre in Gurgaon, every Indian student who went abroad on a merit scholarship in the years that followed — all of it traces back, in some measure, to the decisions made during those desperate weeks.

## Bajpayee's Preparation

Manoj Bajpayee has spoken candidly about the challenge of playing a character rooted in economics — a subject he freely admits was never his strong suit. "I've played the role of RBI Governor, so I had to study the basic terms and know the information needed," he told reporters during a podcast appearance. "For every scene and dialogue, I had to search the terms online because as an actor, everything I deliver has to be believable."

That commitment to authenticity extends to the film's production design. Chinmay Mandlekar, best known for his work in Marathi cinema including the blockbuster Pawankhind, has described the difficulty of recreating 1991 India on screen. "A lot of effort went to eliminate everything that looked like the modern world," the makers noted. That means no malls, no smartphones, no modern signage — a pre-liberalisation India that has essentially vanished from the physical landscape.

## Why This Matters to the Diaspora

For NRI audiences, Governor touches a nerve that most Bollywood films don't even attempt. The 1991 crisis wasn't just an economic event — it was the event that made the modern Indian diaspora possible. Liberalisation opened the floodgates for skilled migration, for IT exports, for the very infrastructure that allowed millions of Indians to build lives in the United States, the United Kingdom, and Canada.

Every NRI family has a "before and after" story anchored somewhere in the early 1990s. Before: your parents queued for a phone connection that took years to arrive. After: Infosys went public and your cousin got an H-1B visa. Governor dramatises the pivot point between those two Indias.

Bajpayee has framed the film as an urgent education for younger audiences. "They should know that there was a time when there were no soft drinks. There was no mall," he said. "In 1992, the first cricket match was telecast. So we are talking about that time."

## The Creative Team

The screenplay, written by Suvendu Bhattacharyjee, Saurabh Bharat, Ravi Asrani, and Vipul Amrutlal Shah, draws from publicly available historical accounts. The film features music composed by Amit Trivedi with lyrics by Javed Akhtar — a pairing that signals creative ambition. The cast also includes Adah Sharma and Noushad Mohamed Kunju.

## What to Expect

Governor releases on June 12, the same day as Kangana Ranaut's Bharat Bhagya Vidhata. It's a counter-intuitive release strategy in a month already packed with blockbusters, but the film's genre — a political financial thriller — gives it a distinct identity. There is no direct competition for the audience Governor is targeting: educated adults who want substance with their popcorn.

Venkitaramanan passed away on November 18, 2023, at 92. His contribution to India's survival remains largely unknown to the general public. If Governor does its job, that changes.

*Governor releases in theatres on June 12, 2026.*

Sources: Bollywood Hungama, Cinema Express, Filmibeat"""

    image_caption = "Manoj Bajpayee, who plays the RBI Governor in the upcoming political thriller"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.bollywoodhungama.com", "https://www.cinemaexpress.com", "https://www.filmibeat.com"]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: June 2026 — Bollywood's Biggest Month
# ═══════════════════════════════════════════════════════════════════
def write_june_battle():
    print("\n═══ Article 2: June 2026 Box Office Battle ═══")
    slug = "june-2026-bollywood-biggest-month-nine-releases-1400-crore-nri-20260606"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        topic_queries=["Bollywood cinema hall India", "Indian movie theatre audience"],
        pexels_query="movie theater cinema audience crowd",
        slug=slug
    )

    headline = "Nine Films. Four Fridays. ₹1,400 Crore at Stake. June 2026 Is Bollywood's Biggest Gamble Yet."
    subheadline = "From Ram Charan's Peddi to Toy Story 5, from Diljit Dosanjh's partition film to Akshay Kumar's comeback comedy — every major release is fighting for the same screens, and trade experts are worried."

    body = """June 2026 has quietly become the most consequential month in recent Bollywood history. Nine major releases are scheduled across just four Fridays, with a combined investment of over ₹1,400 crore. By any measure — number of releases, total budget, star power, genre diversity — this is unprecedented. And the industry isn't sure whether to celebrate or panic.

## The Lineup

The month opened with three simultaneous releases on June 5: David Dhawan's final directorial, Hai Jawani Toh Ishq Hona Hai; Bobby Deol and Anurag Kashyap's Bandar; and Ram Charan's Telugu blockbuster Peddi, which has already crossed ₹150 crore worldwide in its first two days. That triple-header set the tone for what's coming.

June 12 brings two more: Manoj Bajpayee's Governor, a political thriller about the 1991 RBI crisis, and Kangana Ranaut's Bharat Bhagya Vidhata, a 26/11 drama about hospital workers. The following week, June 13, sees Imtiaz Ali's Main Vaapas Aaunga with Diljit Dosanjh, Sharvari, and Vedang Raina — a partition-era story with A.R. Rahman's music. That same Friday also features Manoj Bajpayee's Governor (still in its second week), and two additional releases: Kangana's film and Vikram Bhatt's 3D horror Haunted: Echoes of the Past.

June 19 is the Cocktail 2 slot — Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna in Homi Adajania's romantic comedy, going head-to-head with Pixar's Toy Story 5. And June 26 closes the month with Welcome to the Jungle, Akshay Kumar's multi-starrer comedy featuring a cast so large it requires its own call sheet.

## The Math

According to Bollywood Hungama's calculations, the combined production and marketing budgets of this month's Hindi and pan-India releases exceed ₹1,400 crore. That's more than most entire years in the previous decade. The math is simple and brutal: every film needs screens, every film needs an opening weekend, and there aren't enough of either to go around.

Trade veteran Taran Adarsh has been blunt about the risks. "Now you can't stop anyone. Every producer is of the opinion that 'Main kyun aage jaau?'" he said. "However, there will be maara-maari for screens, as it's said in the trade."

The problem isn't that audiences won't come. Indian box office has been on a strong run — Dhurandhar 2 crossed ₹1,800 crore worldwide, Bhooth Bangla exceeded expectations, and regional cinema is consistently delivering hits. The problem is that nine films can't all have a healthy opening weekend in the same month. Screens will be carved up. Second-week holds will suffer. Some films that might have been hits in March will be casualties of the June traffic jam.

## What This Means for NRI Audiences

For diaspora audiences in the US, UK, and Canada, June 2026 is a different kind of problem — an embarrassment of riches. North American multiplexes that carry Indian films are already planning their schedules, and the screen allocation battles that play out in India are even more intense overseas, where Indian films compete for limited showtimes.

The upside: NRI audiences will have unprecedented choice. A Diljit Dosanjh partition film, a Ram Charan sports drama, a Shahid Kapoor romantic comedy, and a Kangana Ranaut historical drama — all in the same month. The diaspora has consistently been the difference between a film being a hit and a superhit, contributing 20-30 percent of lifetime grosses for major Hindi releases. This month will test whether that audience can split its spending across nine titles.

## The Peddi Effect

Ram Charan's Peddi has already set the early benchmark. With ₹96.40 crore net in India and ₹150.49 crore worldwide in just two days, it's one of the biggest Telugu openers of 2026. But its trajectory will also determine how the rest of the month plays out. If Peddi legs are strong through the weekend and into its second week, it will eat into screen availability for the June 12 releases. If it drops sharply — as the Day 2 decline of 47 percent from Day 1 suggests is possible — screens open up.

The same calculus applies at every stage. Main Vaapas Aaunga's first week will overlap with Cocktail 2's opening. Welcome to the Jungle's debut will compete with Cocktail 2's second week and Toy Story 5's third week. Every film is borrowing screens from the film that came before it and lending screens to the one that follows.

## The Hollywood Factor

Adding to the complexity, this isn't just a Bollywood month. Toy Story 5 opens on June 19 with massive advance buzz and a Taylor Swift original song. He-Man and the Masters of the Universe, Disclosure Day, and Supergirl are all scheduled for June releases in India. These films target the same multiplex audiences in metros and in NRI markets.

For the Indian film industry, which has spent the post-pandemic years arguing that Bollywood can compete with Hollywood for screens, June 2026 is the ultimate stress test. If all nine films perform, it proves the market is big enough. If half of them underperform, it proves the month was too crowded.

## The Bottom Line

What makes June 2026 genuinely historic is not just the quantity — it's the quality and diversity of the slate. There's a political thriller based on real events. A partition-era love story. A 26/11 tribute to unsung heroes. A Telugu sports drama. A Bollywood romantic comedy. A multi-starrer slapstick franchise. A Pixar sequel. The audience has never had this many reasons to go to the movies in a single month.

Whether that's a sign of Bollywood's confidence or its inability to coordinate release dates is the question no one will be able to answer until the numbers come in.

Sources: Bollywood Hungama, Sacnilk, Filmibeat, Pinkvilla"""

    image_caption = "A crowded Indian movie theatre — June 2026 will test just how many blockbusters audiences can absorb"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.bollywoodhungama.com", "https://www.sacnilk.com", "https://www.filmibeat.com", "https://www.pinkvilla.com"]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Bharat Bhagya Vidhata — Kangana Ranaut
# ═══════════════════════════════════════════════════════════════════
def write_bharat_bhagya_vidhata():
    print("\n═══ Article 3: Bharat Bhagya Vidhata ═══")
    slug = "bharat-bhagya-vidhata-kangana-ranaut-2611-cama-hospital-nurses-nri-20260606"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Kangana Ranaut",
        topic_queries=["Kangana Ranaut actress", "2008 Mumbai attacks Cama Hospital"],
        pexels_query="hospital nurse India courage",
        slug=slug
    )

    headline = "Kangana Ranaut Is Playing a Nurse Who Saved 400 Lives During 26/11. The Film Was Originally Called Nurses of Cama."
    subheadline = "Bharat Bhagya Vidhata, releasing June 12, turns the spotlight away from commandos and towards the hospital staff who refused to abandon their posts during the Mumbai attacks."

    body = """The 26/11 Mumbai attacks have been told many times on screen — through the eyes of NSG commandos in Major, through hotel staff in Hotel Mumbai, through the broader siege in The Attacks of 26/11. But there is one story from that night that has never been told: what happened inside Cama Hospital, where a handful of nurses, ward boys, cleaners, and lift operators hid and protected over 400 patients while terrorists roamed the corridors outside.

That story is now Bharat Bhagya Vidhata. Directed by Manoj Tapadia and starring Kangana Ranaut as a nurse, the film releases in theatres on June 12, 2026.

## What the Trailer Reveals

The trailer, which launched on June 3, is remarkably restrained for a film about a terror attack. There are no action sequences, no heroic slow-motion shots. Instead, the two-and-a-half-minute preview is almost entirely set inside the hospital — a claustrophobic world of flickering lights, whispered instructions, and the constant awareness that violence is happening just outside the walls.

Kangana's character delivers a line early in the trailer that sets the film's thesis: "Hum log important nahi hain. Hum jo karte hain, wo important hai." We are not important. What we do is important. It's a statement that applies to the real hospital staff of that night and, by extension, to every essential worker who has ever been invisible until a crisis made them necessary.

The film co-stars Girija Oak and Smita Tambe, both accomplished Marathi actresses who have spoken about the emotional weight of the material. Oak revealed that after watching the first cut, she and Tambe were "holding hands, eyes filled with tears." Director Tapadia has described the film as a tribute to people "without whom the system would collapse in a single day."

## The Title Story

The film was originally called Nurses of Cama — a straightforward title that described exactly what it was. But Kangana felt the film's scope was broader than one hospital. "When I heard the script, it talked and showcased the spirit of India's shared compassion," she explained at the trailer launch. "That's when we decided we wanted the title Bharat Bhagya Vidhata."

There was a problem: the title was already registered to John Abraham. In Bollywood, registered titles are fiercely guarded assets. But when Kangana called Abraham, he released it within 24 hours, at no cost. "When you have such a title, people don't usually give it that easily," she acknowledged. "But I called John sir and he gave us the title within a day." It's a small industry anecdote that says something about the film's gravitational pull even before release.

## The 26/11 Story That Hasn't Been Told

Cama Hospital, a government women and children's hospital in south Mumbai, was one of the first locations attacked on November 26, 2008. Terrorists Ajmal Kasab and Abu Ismail entered the hospital grounds during their rampage through the city. What is less widely known is what happened inside.

The hospital staff — nurses, ward boys, security guards, cleaners, and administrators — made a collective decision to stay. They locked wards, moved patients away from windows, turned off lights, and maintained medical care in near-darkness while the attack unfolded outside. No patients died in the hospital that night. More than 400 people were protected by staff who had no training in crisis response, no weapons, and no guarantee they would survive.

These are the people the film honours. Not the armed responders — their story has been told. The unarmed ones. The ones who chose their patients over their own safety, not because they were brave in any cinematic sense, but because leaving wasn't something they considered.

## The Diaspora Dimension

For NRI audiences, 26/11 holds a particular weight. Many diaspora families were glued to their televisions during the 72-hour siege, watching their city — a city many still call home — under attack. The attacks also directly affected diaspora communities: foreign nationals were among the victims at the Taj and Oberoi hotels.

But 26/11 also reshaped how the world perceived Mumbai and, by extension, India. The city's resilience — the way it returned to normalcy with almost alarming speed — became a defining narrative. Bharat Bhagya Vidhata locates that resilience not in the city's skyline or its business district, but in a government hospital ward where a cleaner decided not to leave.

## Release Context

Bharat Bhagya Vidhata releases on June 12 alongside Manoj Bajpayee's Governor — two mid-budget films that are betting on substance over spectacle in a month dominated by blockbusters. For Kangana Ranaut, the film represents a return to the kind of performance-driven cinema that built her reputation, after a series of commercially underperforming big-budget projects.

The film is produced by Babita Ashiwal, Jayantilal Gada (of Pen Studios), Kangana Ranaut herself, and Shaailesh R. Singh, with music by an as-yet-unannounced composer. The supporting cast includes Aditya Mishra, Zahid Khan, and Rasika Agashe.

If the trailer is any indication, this is a film that trusts its audience to find meaning in restraint rather than spectacle. In a month of ₹1,400 crore blockbusters, that's either the bravest or the most foolish bet of June 2026.

*Bharat Bhagya Vidhata releases in theatres on June 12, 2026.*

Sources: Filmibeat, Zoom TV, Koimoi, Bollywood Hungama"""

    image_caption = "Kangana Ranaut, who plays a nurse during the 26/11 Mumbai attacks in Bharat Bhagya Vidhata"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.filmibeat.com", "https://www.zoomtventertainment.com", "https://www.koimoi.com", "https://www.bollywoodhungama.com"]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 4: What to Watch This Week (June 8–14)
# ═══════════════════════════════════════════════════════════════════
def write_streaming_roundup():
    print("\n═══ Article 4: What to Watch This Week ═══")
    slug = "what-to-watch-this-week-june-8-2026"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        topic_queries=["streaming television remote control", "family watching television"],
        pexels_query="streaming television cozy living room popcorn",
        slug=slug
    )

    headline = "What to Watch This Week: Your Streaming and Theatre Guide for June 8–14"
    subheadline = "From a still-fresh Dhurandhar 2 to Gullak Season 5's quiet brilliance to the theatrical arrival of Governor and Bharat Bhagya Vidhata — here's everything worth your time this week."

    body = """The first week of June was a firehose. Dhurandhar 2 dropped on JioHotstar. Gullak Season 5 returned on SonyLIV. Maa Behen brought Madhuri Dixit back in a dark comedy on Netflix. Made In India: A Titan Story launched on Amazon MX Player. And in theatres, Peddi crossed ₹150 crore worldwide in two days.

The second week of June is quieter on the OTT front, which makes it the perfect time to catch up — and to start planning for a stacked theatrical weekend. Here's what to watch between June 8 and 14.

## Still Streaming — Don't Miss These

**Dhurandhar 2: The Revenge** (JioHotstar)
If you haven't watched it yet, this is the week. Aditya Dhar's spy thriller starring Ranveer Singh crossed ₹1,800 crore worldwide during its theatrical run and is now streaming in Hindi, Telugu, Tamil, Kannada, and Malayalam. At nearly four hours, it demands commitment, but the consensus is clear: this is the real deal. Perfect for a long weekend binge.

**Gullak Season 5** (SonyLIV)
The Mishra family is back, and they're still the most relatable family on Indian television. TVF's slice-of-life series about a middle-class Lucknow household has quietly built one of the most loyal fanbases in Indian streaming. If you grew up in a joint family or a small town — or if your parents did — Gullak hits differently. Five seasons in, the writing is still sharp and the warmth is still genuine. The kind of show you watch with your parents on a video call.

**Maa Behen** (Netflix)
Madhuri Dixit and Triptii Dimri in a dark comedy that critics are calling Madhuri's best performance in years. It's not the Madhuri of Dil To Pagal Hai — this is a layered, occasionally unsettling turn that proves she has range her commercial filmography never fully explored. Worth watching for the performances alone.

**Made In India: A Titan Story** (Amazon MX Player)
Jim Sarbh and Naseeruddin Shah in a drama about the founding of Titan Industries. If you've ever worn a Titan watch — and if you're Indian, you probably have — this series contextualises the company's unlikely rise from a joint venture with Tamil Nadu Industrial Development Corporation to one of India's most trusted consumer brands. Available for free on MX Player.

## New This Week

**Every Year After** (Prime Video — June 10)
Amazon's new original series based on the bestselling novel. A romance that spans decades, told through annual reunions that reveal how two people grow together and apart over time. Early reviews suggest it's a strong adaptation that leans into emotional storytelling without becoming saccharine. Available globally.

**Patriot** (ZEE5 — already streaming)
The Mammootty-Mohanlal reunion spy thriller that underperformed in theatres gets its second life on streaming. If you missed it in cinemas, this is a low-risk way to see two legends sharing screen time. The reviews are mixed, but "Mammootty and Mohanlal in the same frame" remains its own genre.

**KD: The Devil** (ZEE5 — already streaming)
A Kannada period action drama that generated buzz at its theatrical release. Now available on ZEE5 for those who want South Indian cinema beyond the usual Telugu blockbusters.

## Coming to Theatres This Week

**Governor** (June 12)
Manoj Bajpayee as the RBI Governor who saved India from bankruptcy during the 1991 crisis. Directed by Chinmay Mandlekar. This is the most intellectually ambitious Hindi film of the month — a political thriller about economics, which shouldn't work but absolutely might.

**Bharat Bhagya Vidhata** (June 12)
Kangana Ranaut as a nurse during the 26/11 Mumbai attacks. The trailer was widely praised for its restraint. If you're in the US, UK, or Canada, check your local Indian film distributor for showtimes.

## On the Horizon

**Main Vaapas Aaunga** (theatres, June 13) — Imtiaz Ali's partition drama with Diljit Dosanjh, A.R. Rahman's music, and what promises to be one of the most emotionally charged theatrical experiences of the year.

**Toy Story 5** (theatres, June 19) — Pixar's PG-rated sequel, the first in the franchise's 31-year history. Features a Taylor Swift original song. Available in India on June 19.

**Cocktail 2** (theatres, June 19) — Shahid Kapoor, Kriti Sanon, Rashmika Mandanna. The spiritual sequel to the 2012 hit.

**House of the Dragon Season 3** (HBO/Max, June 21) — Eight episodes, a massive naval battle in the premiere, and the beginning of the end for the Dance of the Dragons. If you're a Game of Thrones fan, this is your summer show.

**The Bear Season 5** (Hulu, June 25) — The final season. Carmy, Sydney, Richie. If you know, you know.

## The Pick of the Week

If you can only watch one thing: **Gullak Season 5**. It's the kind of show that makes you miss home in the best way, and five episodes is a manageable commitment. Save Dhurandhar 2 for when you have four hours and zero interruptions.

Sources: Sacnilk, Gadgets 360, Decider, Brit + Co"""

    image_caption = "Your streaming and theatre guide for the second week of June 2026"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.sacnilk.com", "https://www.gadgets360.com", "https://decider.com", "https://www.brit.co"]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Entertainment Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []

    # Article 1
    art_id = write_governor()
    results.append(("Governor", art_id))
    time.sleep(2)

    # Article 2
    art_id = write_june_battle()
    results.append(("June Box Office Battle", art_id))
    time.sleep(2)

    # Article 3
    art_id = write_bharat_bhagya_vidhata()
    results.append(("Bharat Bhagya Vidhata", art_id))
    time.sleep(2)

    # Article 4
    art_id = write_streaming_roundup()
    results.append(("Streaming Roundup", art_id))

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {name}: {aid or 'FAILED'}")
    print("=" * 60)

    success = sum(1 for _, a in results if a)
    print(f"\n{success}/{len(results)} articles published successfully.")
