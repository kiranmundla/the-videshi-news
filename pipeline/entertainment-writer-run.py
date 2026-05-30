#!/usr/bin/env python3
"""Entertainment writer for The Videshi - Run 2026-05-30 evening batch."""

import json, os, re, sys, time, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# --- ENV ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- IMAGE FUNCTIONS ---
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
    """Fetch from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        cmd = [
            "curl", "-sS",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
            "-H", f"Authorization: {PEXELS_KEY}"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get("photos", [])
                if photos:
                    url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check that URL returns a real image > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def sb_insert(table, data):
    """Insert into Supabase."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        print(f"  ✓ Inserted into {table}")
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:200]}")
        return None

def sb_patch(table, match, data):
    """Update in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        print(f"  ✓ Patched {table}")
    else:
        print(f"  ✗ Patch failed: {r.status_code} {r.text[:200]}")

# --- ARTICLES ---
articles = []

# ---- ARTICLE 1: Bhooth Bangla Netflix OTT Release ----
articles.append({
    "headline": "Bhooth Bangla Hits Netflix on June 12. Akshay Kumar and Priyadarshan's ₹264 Crore Horror-Comedy Comes Home.",
    "subheadline": "After a 43-day theatrical run and a worldwide gross of ₹264 crore, the Hera Pheri duo's reunion is finally heading to your living room. Here's what the diaspora needs to know.",
    "slug": "bhooth-bangla-netflix-ott-release-june-12-akshay-kumar-priyadarshan-nri-20260530",
    "category": "entertainment",
    "body": """Bhooth Bangla, the horror-comedy that reunited Akshay Kumar and director Priyadarshan after 16 years, is officially heading to Netflix on June 12, 2026. For millions of Indian diaspora viewers who missed the film's theatrical run, this is the moment they've been waiting for.

## The Numbers Tell the Story

The film has been one of Bollywood's most commercially successful releases of 2026. After opening in theaters on April 17, Bhooth Bangla has grossed approximately ₹264 crore worldwide across its 43-day run, making it one of Akshay Kumar's strongest box office performances in recent years. It's a certified hit by every metric that matters.

What makes the financial story even more interesting is the risk management. Before a single ticket was sold, the producers had already recovered ₹105 crore of their estimated ₹120 crore budget through non-theatrical deals alone. Netflix paid ₹60 crore for digital rights, Zee Cinema secured satellite rights for ₹25 crore, and Zee Music Company acquired the music rights for ₹10 crore. By the time audiences showed up, the film was already in profit on paper.

## Why the Diaspora Should Care

This isn't just another Akshay Kumar comedy. This is a reunion of the partnership that gave Indian cinema Hera Pheri, Garam Masala, Bhool Bhulaiyaa, and Bhagam Bhag — films that remain comfort-watch staples in every NRI household from New Jersey to New South Wales. Priyadarshan's brand of comedy, rooted in South Indian storytelling traditions but executed with Bollywood's big-screen energy, has always traveled exceptionally well with diaspora audiences.

The film follows a vengeful spirit targeting newly married brides due to a tragic past, blending supernatural elements with the kind of physical comedy and ensemble chaos that Priyadarshan does better than anyone in the business. It's spooky enough to keep you engaged, funny enough to keep it light, and just chaotic enough to feel like a Priyadarshan film.

## The Reunion Factor

The last time Kumar and Priyadarshan collaborated was in 2010, and in the intervening 16 years, both have navigated very different career arcs. Kumar cycled through action dramas, social message films, and historical epics with varying success. Priyadarshan largely retreated to Malayalam cinema, where he continued making acclaimed work. Their coming back together felt like an event, and the box office responded accordingly.

## What to Expect on Netflix

The film runs at a tight 2 hours 15 minutes and features a supporting cast that includes Paresh Rawal, Rajpal Yadav, and Tabu — essentially a greatest-hits assembly of Bollywood's comedy talent. For NRI families looking for a movie night that the whole family can enjoy without anyone reaching for the remote, this is the safest bet on Netflix this month.

The June 12 premiere aligns with the standard 45-to-60-day theatrical-to-OTT window that Bollywood has settled into. For diaspora viewers in the US, UK, and Canada, the timing is convenient — a weeknight drop that sets up perfectly for weekend viewing.

Mark your calendars. The duo is back, and this time they're coming directly to your couch.""",
    "sources": ["Sacnilk", "Bollywood Hungama", "Netflix"],
    "image_person": "Akshay Kumar",
})

# ---- ARTICLE 2: Deool Band 2 Marathi Records ----
articles.append({
    "headline": "Deool Band 2 Just Surpassed Sairat's First-Week Record. Marathi Cinema Is Having the Year of Its Life.",
    "subheadline": "With ₹25.85 crore in its first week, the devotional drama is now the second-highest first-week Marathi grosser ever. Here's why this matters beyond Maharashtra.",
    "slug": "deool-band-2-marathi-box-office-sairat-record-golden-year-nri-20260530",
    "category": "entertainment",
    "body": """Something remarkable is happening in Marathi cinema, and the numbers for Deool Band 2 just confirmed it. The devotional drama has earned ₹25.85 crore net in its first seven days, surpassing Sairat's opening-week collection of ₹25.50 crore and becoming the second-highest first-week grosser in Marathi cinema history. Only Raja Shivaji, with ₹36.25 crore, sits above it.

## Three Blockbusters in One Month

What makes 2026 extraordinary for Marathi cinema isn't just Deool Band 2. It's the fact that this is the third major hit in the same month. First came Krantijyoti Vidyalay Marathi Madhyam, which connected with audiences on a cultural level. Then Raja Shivaji broke all existing records. Now Deool Band 2 has settled in right behind it, proving that the first two weren't flukes.

The May 2026 box office report tells a story that would have seemed improbable even two years ago: regional cinema is dominating Bollywood at the national box office. While Hindi films have struggled to find consistent audiences — with the exception of the Dhurandhar franchise and Bhooth Bangla — Marathi, Tamil, and Malayalam industries are delivering hit after hit.

## The Numbers in Detail

Deool Band 2 opened on a Thursday with ₹2.45 crore, making it the second-biggest opening day for a Marathi film. What happened next was textbook word-of-mouth growth. Friday stayed steady at ₹2.55 crore. Saturday jumped to ₹4.85 crore. Sunday surged to ₹5.90 crore — a 21.6 percent increase from Saturday. And here's the really impressive part: on its first Wednesday (Day 7), the film held completely flat at ₹3.35 crore, matching the previous day exactly.

Holding flat on a weekday isn't normal. Films drop. That's what they do. When a film holds or grows on a Tuesday or Wednesday, it signals that the audience isn't just showing up — they're telling other people to show up.

The national chains tell the same story. BookMyShow advance sales crossed 25,000 before release. By Sunday, PVR, INOX, and Cinepolis combined were selling over 38,000 tickets per day. MovieMax locations were selling out within four hours of opening.

## Why This Matters for the Diaspora

For the Marathi-speaking diaspora — and there are significant communities in the US (particularly New Jersey, the Bay Area, and the Chicago suburbs), the UK, and Australia — this is more than box office news. Marathi cinema has historically been overshadowed by Hindi and South Indian industries in the global conversation. The fact that three films in a single month have delivered these numbers suggests a structural shift, not a seasonal spike.

Deool Band 2 carries a devotional theme that resonates deeply with cultural identity. Pune continues to be the primary driver, recording 45.5 percent occupancy on its seventh day — extraordinary for any film in any language. Mumbai contributed 33.3 percent occupancy across 624 shows. These are blockbuster-level holds.

## The Bigger Picture

May 2026's top five Indian films by worldwide gross tell a story of regional dominance: Karuppu (Tamil, ₹253 crore), Drishyam 3 (Malayalam, ₹170 crore), Raja Shivaji (Marathi, ₹114 crore), Athiradi (Malayalam, ₹63 crore), and Pati Patni Aur Woh Do (Hindi, ₹54 crore). Only one Hindi film cracks the top five, and it's in last place.

For years, the narrative was that Bollywood was Indian cinema. That narrative is over. Regional industries are now the growth engine, and Marathi cinema — long considered a niche market — is proving it belongs in the conversation with Tamil, Telugu, and Malayalam as a genuine commercial force.

Deool Band 2 isn't just a hit. It's evidence of a transformation.""",
    "sources": ["Sacnilk", "BookMyShow"],
    "image_search": ["Marathi cinema theater Pune", "Indian movie theater audience"],
})

# ---- ARTICLE 3: Jackie Shroff Great Grand Superhero ----
articles.append({
    "headline": "Jackie Shroff Just Made a Film Where His Grandson Tells Everyone He's a Superhero. It's the Most Heartfelt Hindi Film This Year.",
    "subheadline": "The Great Grand Superhero opened to ₹25 lakh and a 3.5-star Filmfare review. The box office doesn't care, but it should.",
    "slug": "jackie-shroff-great-grand-superhero-review-heartfelt-childrens-film-nri-20260530",
    "category": "entertainment",
    "body": """The Great Grand Superhero opened in Indian theaters on May 29 to near-empty halls and a day-one collection of ₹25 lakh — a number so small it barely registers on the same chart as the films it's competing against. By day two, the total was still under ₹1 crore. By every commercial metric, this film is invisible.

But here's the thing: it might also be the most genuinely good-hearted Hindi film released in 2026.

## What the Film Is Actually About

Directed by Manish Saini, the film stars Jackie Shroff as Jagdishchandra — known as Dadaji or Dadu — a creaky grandfather who grows plants and is terrified of lizards. His grandson Deepu, played by a pitch-perfect Mihir Godbole, is the new kid at school. Again. His father's job requires constant transfers, and every few months, Deepu finds himself in a new classroom full of strangers who don't know him and don't want to.

So Deepu does what kids do. He tells a lie. He tells his classmate Laddu that his grandfather is secretly a superhero.

The lie spreads. The kids want to meet Dadu. Deepu and his grandfather start playing along, creating an elaborate mythology. The first half, according to The Hollywood Reporter India, is "funny, poignant, satirical and very inventive" — drawing comparisons to Stanley Ka Dabba, the 2011 film that remains one of Indian cinema's best children's stories.

Then the actual aliens show up. Because of course they do.

## The Reviews Are Kind

Filmfare gave it 3.5 out of 5, calling it "not the most polished product, but this cute and warm film has all the right lessons." The Hollywood Reporter India praised its charming setup and child performances. Bollywood Hungama called it "a well-intentioned, rare children's film from Bollywood, driven by a novel plot and endearing performances." Audience reactions on social media have been emphatic — 4 out of 5 ratings, words like "comfort movie" and "a superhero story with heart."

The consensus is clear: this is a good film that the market decided not to show up for.

## Why This Matters

Bollywood doesn't make children's films. Not really. The industry makes superhero films for adults, family films that are actually comedies for parents, and animated imports from Hollywood. A genuine, original, live-action children's film — one that takes childhood imagination seriously and treats its young protagonist with respect — is vanishingly rare. The last widely praised example was Chillar Party in 2011. Before that, Taare Zameen Par in 2007.

The Great Grand Superhero sits in that tradition. It's a film about a kid who uses storytelling to survive loneliness, and a grandfather who loves him enough to play along. Jackie Shroff, at this point in his career, brings a worn-in warmth to the role that a younger actor couldn't replicate. He's not performing grandfatherhood — he's inhabiting it.

## The Diaspora Angle

For NRI families with children growing up between cultures, this film touches something specific. The experience of being the new kid — of showing up in a place where nobody knows your name and inventing a version of yourself to survive — isn't just a plot device. It's a lived reality for millions of diaspora kids who navigate different worlds every day.

The Great Grand Superhero might not make money. But if you have kids between 6 and 14, and you're looking for a Hindi film that doesn't rely on crude humor or manufactured emotion, this is the one.

Catch it in theaters before it's gone. Which, at this rate, might be next week.""",
    "sources": ["Filmfare", "The Hollywood Reporter India", "Bollywood Hungama", "Sacnilk"],
    "image_person": "Jackie Shroff",
})

# ---- ARTICLE 4: Kiara Advani on Toxic ----
articles.append({
    "headline": "Kiara Advani Learned Kannada Overnight to Shoot Toxic. She Wasn't Allowed to Say 'Hi' on Set.",
    "subheadline": "Yash's first film since KGF: Chapter 2 was shot entirely in English and Kannada. Kiara's character Nadia may redefine how Bollywood sees its female leads.",
    "slug": "kiara-advani-toxic-kannada-english-nadia-yash-geetu-mohandas-nri-20260530",
    "category": "entertainment",
    "body": """Kiara Advani has always been the warm one. She's the actor who walks on set saying "hi" to everyone, who greets the crew by name, who carries a sunny disposition that's become part of her professional identity. On the set of Toxic: A Fairy Tale for Grown-Ups, director Geetu Mohandas told her to stop.

"Geetu is like, okay, tomorrow when you come on set, I want you to be… I'm a person who walks on set always like, 'Hi, what's up, good morning.' And she's like, 'I don't want pleasantries, I want you to come in that zone, no hi hello, not your team, nobody, just be in a zone today,'" Kiara told Bombay Times in an interview published this week.

## A Film Shot in Two Languages Simultaneously

Toxic, directed by Geetu Mohandas and starring Yash in his first role since KGF: Chapter 2, was filmed in both English and Kannada — simultaneously. Every scene was shot twice: once in English, once in Kannada. For Kiara, who doesn't speak Kannada, this meant learning her lines by rote the night before each shoot day.

"I have been mugging up my dialogues literally. Sometimes, they would come with the lines the night before shoot," she said. "It is work; it is homework for sure." She compared it to her school days — she was, by her own admission, "that frontbencher in class" who memorized everything.

The dual-language approach is unusual in Indian cinema. Most multilingual releases are dubbed in post-production. Shooting natively in two languages raises the performance bar considerably — the emotional beats, the rhythm, the intonation all have to work independently in each language. It's a choice that signals Mohandas's ambition for the film to feel authentic in both its Kannada and English versions.

## Nadia: The Character That Changed Her Perspective

Kiara plays a character named Nadia, and she's clearly been affected by the role. "Toxic completely changes the way you see the dynamics between men and women," she said. "Even for me, when Geetu narrated the script, it took a while for me to understand that okay, this is also normal, even though it may be grey and not conventional. But there's a certain liberation in love."

She went further: "When Nadia was narrated to me, I was like 'wow,' I wish I was capable of being so detached and liberated in my own thoughts."

These are striking words from an actor whose filmography — Kabir Singh, Shershaah, Satyaprem Ki Katha — has largely placed her in conventional romantic roles. The suggestion that Nadia operates in morally gray territory, that she's "detached" and "liberated" in ways that challenge traditional relationship dynamics, hints at a very different kind of character than Kiara has played before.

## The Geetu Mohandas Factor

Mohandas is one of Indian cinema's most respected independent filmmakers, known for Liar's Dice (India's Oscar entry in 2015) and the critically acclaimed Moothon. She's also a founding member of the Women in Cinema Collective, which advocates for gender equality in the Malayalam film industry.

Her involvement in Toxic is what makes the film genuinely unpredictable. A KGF-scale action film directed by an art-house feminist filmmaker — it's a combination that shouldn't work on paper, but the early reactions from CinemaCon suggest it does. A nine-minute preview left international trade attendees "speechless," according to reports.

## What the Diaspora Should Watch For

Toxic features a stacked cast: Yash, Kiara Advani, Nayanthara, Huma Qureshi, Tara Sutaria, and Rukmini Vasanth. The film is set between the 1940s and 1970s, described as "a fairy tale for grown-ups" with a period-action aesthetic. Music by Ravi Basrur (KGF). Action choreography by JJ Perry and the Anbariv duo.

The release date remains in flux — it was originally set for June 4, then postponed as the makers recalibrated their global distribution strategy after the overwhelmingly positive CinemaCon response. An Independence Day (August 15) window is now being discussed.

For diaspora audiences who watched KGF: Chapter 2 turn into a cultural phenomenon in overseas markets, Toxic carries enormous expectations. The difference this time: the filmmaker behind it isn't making a mass entertainer. She's making something that, by Kiara's own admission, requires you to sit with its discomfort before you understand it.

That's either going to be a problem or a masterpiece. There's rarely an in-between.""",
    "sources": ["Bombay Times", "Bollywood Hungama", "Pinkvilla", "Cinema Express"],
    "image_person": "Kiara Advani",
})


# --- MAIN EXECUTION ---
def main():
    published_count = 0
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"ARTICLE {i}: {art['headline'][:70]}...")
        print(f"{'='*60}")

        # Image sourcing
        img_url = None
        img_attribution = None

        if art.get("image_person"):
            print(f"  Sourcing Wikipedia image for: {art['image_person']}")
            img_url = fetch_wikipedia_person_image(art["image_person"])
            if img_url:
                img_attribution = "Wikimedia Commons"

        if not img_url and art.get("image_search"):
            for q in art["image_search"]:
                print(f"  Trying Pexels for: {q}")
                img_url = fetch_pexels_image(q)
                if img_url:
                    img_attribution = "Pexels"
                    break

        # Validate
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Image failed validation, skipping image")
            img_url = None
            img_attribution = None

        # Insert article
        now = datetime.now(timezone.utc).isoformat()
        article_id = str(uuid.uuid4())
        
        # Create topic first
        topic_id = str(uuid.uuid4())
        topic_data = {
            "id": topic_id,
            "canonical_title": art["headline"][:200],
            "vertical": "culture",
            "urgency": "daily",
            "score_diaspora": 70,
            "score_significance": 65,
            "score_recency": 80,
            "score_source_avail": 75,
            "score_total": 72,
            "signal_count": 1,
            "status": "published",
            "keywords": [],
            "category": art["category"],
            "created_at": now,
            "updated_at": now,
        }
        topic_result = sb_insert("p2_topics", topic_data)
        if not topic_result:
            print(f"  ✗ Failed to create topic, skipping article")
            continue

        # Calculate word count
        word_count = len(art["body"].split())

        insert_data = {
            "id": article_id,
            "topic_id": topic_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "body": art["body"],
            "diaspora_angle": "Diaspora-relevant coverage of Indian entertainment industry developments.",
            "vertical": "culture",
            "tags": [],
            "urgency": "daily",
            "sources": json.dumps(art["sources"]) if isinstance(art["sources"], list) else art["sources"],
            "word_count": word_count,
            "status": "published",
            "is_featured": False,
            "published_at": now,
            "created_at": now,
            "image_url": img_url,
            "image_attribution": img_attribution,
            "score_total": 0,
        }

        result = sb_insert("p2_articles", insert_data)
        if result:
            published_count += 1
            print(f"  ✓ Published: {art['slug']}")
        else:
            print(f"  ✗ FAILED to publish: {art['slug']}")

        time.sleep(1)  # Brief pause between inserts

    print(f"\n{'='*60}")
    print(f"DONE: Published {published_count}/{len(articles)} articles")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
