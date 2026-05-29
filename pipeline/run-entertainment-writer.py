#!/usr/bin/env python3
"""The Videshi Entertainment Writer — May 29, 2026 batch"""

import json, os, sys, time, uuid, subprocess, re, textwrap
import requests, urllib.parse
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── Wikipedia image fetcher ───────────────────────────────────────────
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

# ── Pexels fallback ──────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
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
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Image upload to Supabase ─────────────────────────────────────────
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return image_url  # fall back to direct URL for Wikipedia/Pexels
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            content_type = 'image/jpeg'
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping upload")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true',
            },
            data=r.content,
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            # Fall back to direct URL for Wikipedia/Pexels (permanent)
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

# ── Supabase insert ──────────────────────────────────────────────────
def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ── Articles ─────────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Spider-Noir
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Nicolas Cage Put On a Trench Coat and Became Spider-Man at 62. Prime Video's Spider-Noir Hit No. 1 Globally in 24 Hours.",
    "subheadline": "The noir-drenched Marvel series is streaming now on Prime Video — and NRI subscribers in India, Canada, and the UK are already bingeing it alongside the rest of the world.",
    "slug": "spider-noir-nicolas-cage-prime-video-number-one-global-nri-streaming-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["ScreenRant", "USA Today", "Collider", "Rotten Tomatoes"]),
    "image_person": "Nicolas Cage",
    "body": textwrap.dedent("""\
        Nicolas Cage has done it again — but this time, he did it slowly, deliberately, and in black and white.

        *Spider-Noir*, the live-action Marvel series starring Cage as a 62-year-old retired superhero turned private investigator, premiered on Prime Video on May 27 and climbed to the No. 1 spot globally within 24 hours. The show topped charts in Mexico, Thailand, Poland, and Brazil, reached No. 2 in Canada, Australia, the UK, France, and 15 other countries, and landed at No. 4 in India.

        For the Indian diaspora audience — most of whom already subscribe to Prime Video for its robust Indian content library — *Spider-Noir* is an easy add to the queue. It's the kind of prestige genre show that crosses cultural lines: a hardboiled detective mystery set in 1933 New York, dressed in the visual grammar of classic noir, with a superhero skeleton underneath.

        ## The Setup

        Cage plays Ben Reilly, a former costumed vigilante known as The Spider, who hung up his mask years ago and now works as a private eye in Depression-era Manhattan. A new case drags him back into the world he thought he'd left behind — one filled with superpowered crime bosses, old grudges, and the kind of moral ambiguity that noir does better than any other genre.

        Brendan Gleeson plays Silvermane, the show's primary antagonist, and Lamorne Morris rounds out the cast as Robbie Robertson. The series is showrun by Oren Uziel and Steve Lightfoot, with Phil Lord and Christopher Miller — the duo behind *Into the Spider-Verse* — serving as executive producers. That's the same team that cast Cage as Spider-Man Noir in the 2018 animated film, making this a long-awaited reunion.

        ## Critical Reception

        The reception has been emphatic. *Spider-Noir* holds a 91% score on Rotten Tomatoes, with critics singling out Cage's performance as the best thing he's done in years. ScreenRant's review called his turn as The Spider "fantastic," praising the show for being "an intriguing superhero series that offers plenty of excitement through its binge-worthy crime story with nuanced characters."

        USA Today described Cage as "a Spider-Man for aging adults," noting the actor's willingness to lean into the physicality of the role — wirework and all — at 62.

        The show offers two viewing modes: a classic black-and-white presentation that honours the noir genre, and a "True-Hue" colour version for viewers who prefer a more conventional look. Critics have been divided on which is superior, though the consensus is that the black-and-white version delivers the more immersive experience.

        ## The Diaspora Angle

        For NRI audiences, the appeal is twofold. First, Prime Video is already the most widely subscribed international streaming platform in Indian diaspora households across North America, the UK, and the Gulf — making *Spider-Noir* instantly accessible. Second, the show represents a shift in what superhero television can be: slower, more character-driven, more interested in atmosphere than action set pieces. It's closer to a Coen brothers film than a Marvel origin story.

        India's No. 4 ranking on launch day is notable. Indian Prime Video subscribers typically gravitate toward local-language content, so a live-action English-language Marvel show breaking into the top five within hours signals genuine cross-demographic pull.

        ## What's Next

        Season 2 has not yet been confirmed, though Cage and Uziel have both publicly discussed where the story could go. Uziel told ScreenRant that a second season would be "increasingly chaotic and conflict-heavy," suggesting a darker trajectory for Ben Reilly.

        In the meantime, Spider-Man returns to the big screen on July 31 with *Spider-Man: Brand New Day*, starring Tom Holland. The two properties aren't connected, but the proximity means Marvel's spider franchise will dominate both streaming and theatrical conversations through the summer.

        All eight episodes of *Spider-Noir* season 1 are streaming now on Prime Video worldwide.
    """).strip(),
})

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Shah Rukh Khan's King — Christmas 2026
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Shah Rukh Khan's King Opens Christmas Day. Standing in His Way: Avengers, Dune, and Jumanji.",
    "subheadline": "The ₹350-crore action thriller locks December 24, 2026 — one week after Marvel's Avengers: Doomsday, Dune 3, and the same day as Jumanji: Open World. For NRIs, it's the ultimate holiday dilemma.",
    "slug": "shah-rukh-khan-king-christmas-2026-avengers-dune-jumanji-clash-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Sacnilk", "Wikipedia", "The Hollywood Reporter India"]),
    "image_person": "Shah Rukh Khan",
    "body": textwrap.dedent("""\
        Shah Rukh Khan has never been afraid of a fight at the box office. But the one he's walking into this December might be the biggest of his career — and it's entirely by choice.

        *King*, the Siddharth Anand-directed action thriller starring Khan alongside his daughter Suhana Khan, Deepika Padukone, and Abhishek Bachchan, has officially locked December 24, 2026 as its worldwide release date. It's a Christmas Day opening — the kind of prime real estate that guarantees massive footfalls from holiday crowds and family audiences.

        The problem? The neighbourhood is crowded.

        ## The Collision Course

        Marvel's *Avengers: Doomsday* and Warner Bros.' *Dune 3* are both scheduled for December 18, exactly one week before *King* arrives. Dwayne Johnson's *Jumanji: Open World* opens on December 25. That's three Hollywood tentpoles — two of them franchise juggernauts — bookending SRK's biggest film in years.

        For Indian exhibitors, this creates a screen allocation nightmare. The Christmas corridor is traditionally the most lucrative window in Indian theatrical distribution, but it's also the period when Hollywood dominates multiplex screens, especially in metros and overseas markets. *King* will need to hold its own against films that will command IMAX, 3D, and premium large-format screens across North America, the UK, the Middle East, and Australia — the same markets where the Indian diaspora drives SRK's overseas numbers.

        ## The Stakes

        *King* is reportedly budgeted between ₹350 and ₹400 crore, making it one of the most expensive Indian productions ever. The film has already secured a distribution deal worth approximately ₹250 crore for the Indian market alone, signalling strong confidence from exhibitors and distributors who have seen early material.

        The cast is stacked. Suhana Khan makes her big-screen debut (she appeared in Netflix's *The Archies* in 2023). Deepika Padukone reunites with Shah Rukh after their triple-blockbuster run (*Pathaan*, *Jawan*, *Dunki* in 2023). Abhishek Bachchan plays the antagonist. The supporting cast includes Arshad Warsi, Anil Kapoor, Jackie Shroff, Rani Mukerji, and Abhay Varma.

        Siddharth Anand, who directed *Pathaan* and *War*, brings his signature large-scale action sensibility. Shooting has taken place across Mumbai, Warsaw, Gdansk, and Cape Town. The soundtrack is composed by Sachin–Jigar.

        ## The NRI Calculus

        For diaspora audiences, Christmas week is when families go to the movies together. In past years, SRK has owned this slot — *Dilwale* (2015), *Zero* (2018), and *Dunki* (2023) all opened during the Christmas-New Year corridor. But those films never had to share the week with both Marvel and Dune simultaneously.

        The calculus for NRI families is straightforward but brutal: *Avengers: Doomsday* on Thursday, *King* on Wednesday, *Jumanji* on Thursday. Three films in eight days, all competing for the same discretionary holiday spending.

        SRK's advantage is cultural loyalty. No Hollywood franchise can replicate the emotional pull that a Shah Rukh Khan film has on Indian households during the holidays. But cultural loyalty has limits when the alternative is the biggest Marvel event since *Endgame*.

        ## The Strategic Logic

        The 45-day gap between *Ramayana Part 1* (releasing November 6, 2026) and *King* is deliberate. The two films share no overlap in audience or genre, but their producers clearly coordinated to avoid cannibalising each other's runs. *Ramayana* gets the Diwali-to-Thanksgiving window; *King* gets Christmas.

        If *King* delivers — and the early confidence from distributors suggests it will — it could cap 2026 as the year Indian cinema proved it can go toe-to-toe with Hollywood's biggest franchises in the same release window, on the same screens, in the same markets.

        December 24, 2026. Mark it.
    """).strip(),
})

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Ishaan Khatter — Biarritz Film Festival
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Ishaan Khatter Is the Only Indian on the Biarritz Film Festival Jury. Kristen Stewart Is Chairing It.",
    "subheadline": "The Homebound actor joins an international panel in France next month — a quiet milestone in Indian cinema's growing presence at European festivals.",
    "slug": "ishaan-khatter-biarritz-film-festival-jury-kristen-stewart-indian-cinema-global-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["NewKerala", "Pinkvilla", "ANI", "Gold House"]),
    "image_person": "Ishaan Khatter",
    "body": textwrap.dedent("""\
        There's a particular kind of recognition that doesn't come with a box office number or a streaming chart. It comes with a phone call, a plane ticket, and a seat next to people who take cinema seriously.

        Ishaan Khatter has received that call. The 27-year-old Bollywood actor has been invited to serve on the jury of the Biarritz Film Festival — Nouvelles Vagues 2026, a prestigious European festival dedicated to emerging voices in global cinema. The festival runs from June 23 to 28 in the seaside city of Biarritz in southern France.

        He is the only Indian on the jury. The panel is chaired by Kristen Stewart.

        ## The Jury

        The full jury lineup includes Stewart (who won the César Award for Best Actress and has directed two short films), Canadian actress Whitney Peak (*Gossip Girl*), French actor-director Raphaël Quenard, French filmmaker Nathan Ambrosioni, French actress Suzy Bemba, Italian director Carolina Cavalli, and British actress Esme Creed-Miles (*Hanna*).

        It's a deliberately international panel assembled to evaluate films from emerging directors — the kind of work that doesn't yet have a marketing budget or a release date, but might reshape the medium in five years. The Biarritz Film Festival, now in its fourth edition, has quickly become one of Europe's most closely watched platforms for spotlighting the future of storytelling.

        For Ishaan, the invitation is a direct consequence of a year that has fundamentally repositioned him in the global film conversation.

        ## The Homebound Effect

        In 2025, Neeraj Ghaywan's *Homebound* — starring Ishaan alongside Janhvi Kapoor and Vishal Jethwa, executive-produced by Martin Scorsese — premiered at the Cannes Film Festival to a standing ovation. It was subsequently selected as India's official entry for the Best International Feature Film category at the 2026 Academy Awards, where it was shortlisted among 15 films from 86 countries.

        That trajectory — Cannes premiere, Oscar submission, Academy shortlist — is the kind of career sequence that opens doors at European festivals. Jury invitations at festivals like Biarritz don't come from audition tapes. They come from curators who have watched your work, tracked your choices, and decided you have the taste and perspective to evaluate other people's films.

        Ishaan was also recently named to the Gold House Gold 100 list, becoming the only Indian male actor on the 2026 roster — a recognition of his cultural impact across the Asian diaspora.

        ## What It Means for Indian Cinema

        India's presence at European film festivals has historically been sporadic and often confined to the competition or market sections. Having an Indian actor on the jury — not just attending, not just premiering a film, but actively judging the work of international filmmakers — represents a different kind of visibility.

        It's the kind of soft power that doesn't register on box office trackers but matters enormously for how Indian cinema is perceived by the global industry. When a festival like Biarritz invites an Indian artist to evaluate its competition, it signals that Indian cinema is no longer a curiosity or a niche category — it's part of the mainstream conversation.

        This is especially significant for the diaspora. NRI audiences have long had to explain the depth and range of Indian cinema to friends and colleagues who associate it only with song-and-dance spectacles. Every Indian artist who sits on a European jury, who walks a red carpet as a peer rather than a guest, makes that conversation a little easier.

        ## What's Next for Ishaan

        Beyond the festival circuit, Ishaan is gearing up for *Jugaadu*, a comic caper that also marks his first production venture. The film, which held its mahurat ceremony on April 30 in Mumbai, stars Abhishek Banerjee, Jameel Khan, and marks the Hindi debut of popular Punjabi actress Tania. The first schedule is being shot in Punjab.

        It's a deliberate contrast to the festival-circuit gravitas of *Homebound* — a commercial entertainer designed for theatrical audiences. The ability to toggle between both worlds is exactly what makes Ishaan's jury invitation feel earned rather than ceremonial.

        He'll be in Biarritz from June 23. Kristen Stewart will be sitting next to him. The films will be projected. The conversations will happen in French, English, and the universal language of people who care about what cinema can be.
    """).strip(),
})

# ── Publish ──────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"The Videshi Entertainment Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}\n")

for i, article in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {article['headline'][:70]}...")
    
    # Image sourcing
    person = article.pop('image_person', None)
    img_url = None
    img_attribution = None
    
    if person:
        print(f"  → Sourcing image for: {person}")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    if not img_url:
        # Fallback to Pexels with specific query
        fallback_queries = {
            "Nicolas Cage": ("noir detective trench coat", "private detective noir"),
            "Shah Rukh Khan": ("Bollywood movie premiere", "Indian cinema"),
            "Ishaan Khatter": ("film festival France", "cinema jury panel"),
        }
        q1, q2 = fallback_queries.get(person, ("cinema", "film"))
        img_url = fetch_pexels_image(q1, q2)
        if img_url:
            img_attribution = "Pexels"
    
    # Upload to Supabase if we have an image
    if img_url:
        filename = f"{article['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            article['image_url'] = final_url
            article['image_attribution'] = img_attribution
            article['image_caption'] = f"{person}" if person else ""
    
    # Validate
    body = article.get('body', '')
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ⚠ BELOW 400 WORD MINIMUM — skipping")
        continue
    if not article.get('subheadline') or len(article['subheadline']) < 15:
        print(f"  ⚠ Missing/short subheadline — skipping")
        continue
    if article.get('category') != 'entertainment':
        print(f"  ⚠ Wrong category — skipping")
        continue

    # Insert
    art_id = insert_article(article)
    
    if art_id and article.get('image_url'):
        print(f"  ✓ Image: {article['image_url'][:60]}...")
    elif art_id:
        print(f"  ⚠ No image — article published without image")
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. {len(articles)} articles processed.")
print(f"{'='*60}")
