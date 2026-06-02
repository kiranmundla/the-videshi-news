#!/usr/bin/env python3
"""Entertainment writer — June 2, 2026 evening run"""

import json, os, re, time, urllib.parse, subprocess, uuid, sys
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

def sb_insert(table, data):
    """Insert a row into Supabase and return the response."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(url, json=data, headers=headers, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate that the image URL returns a proper image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if 'image' in content_type and content_length > 5000:
            return True
        # Try GET if HEAD doesn't give content-length
        if 'image' in content_type and content_length == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned_patterns = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com',
                       '_nc_ht=', '_nc_cat=', 'ccb=']
    return any(p in url for p in banned_patterns)


# ── Article definitions ──

articles = []

# ── ARTICLE 1: Zee FIFA World Cup Deal ──
articles.append({
    "headline": "Zee Just Grabbed the FIFA World Cup. Indian Fans Almost Watched the Biggest Tournament Ever on a Pirated Stream.",
    "subheadline": "Ten days before kickoff in the US, Canada, and Mexico, Zee locked an 8-year FIFA deal that JioStar walked away from. For NRIs hosting watch parties, the broadcast will finally have an Indian voice.",
    "slug": "zee-entertainment-fifa-world-cup-2026-unite8-sports-india-broadcast-nri-20260602",
    "category": "entertainment",
    "sources": json.dumps(["Reuters", "BestMediaInfo", "The Hindu BusinessLine", "Devdiscourse"]),
    "body": """The 2026 FIFA World Cup kicks off on June 11 across the United States, Canada, and Mexico. Until two days ago, India — a market of 1.4 billion people and a rapidly growing football fanbase — had no confirmed broadcaster. The most expensive sporting event on the planet was about to go dark in one of the world's last unsold major markets.

Then Zee Entertainment stepped in.

On Monday, Zee confirmed an eight-year partnership with FIFA covering 39 events, including the 2026 and 2030 Men's World Cups, the 2027 Women's World Cup, and a slate of youth, futsal, and intercontinental tournaments running through 2034. The deal also includes docu-series content exploring the cultural dimensions of participating nations.

## What Happened Behind the Scenes

The backstory is a masterclass in brinkmanship. FIFA initially sought approximately $100 million for the India package covering the 2026 and 2030 World Cups. JioStar — the Reliance-Disney joint venture that aired the 2022 World Cup through its predecessor Viacom18 — reportedly offered about $20 million and was rejected. Sony, which held rights for the 2014 and 2018 tournaments, held discussions but did not bid. FIFA then slashed its asking price to $60 million, and the final deal with Zee reportedly closed somewhere between $25 million and $80 million.

The timeline was extraordinary. The agreement was announced just ten days before the opening match. Had negotiations collapsed, India would have been the most populous nation on earth without a legal way to watch football's biggest event.

## Unite8 Sports: Zee's Big Bet

Zee is not just airing the World Cup. It is building an entire sports brand around it. The company has launched Unite8 Sports with four dedicated channels — Unite8 Sports 1 and Unite8 Sports 1 HD in Hindi, plus Unite8 Sports 2 and Unite8 Sports 2 HD in English. The tournament will also stream on ZEE5.

Beyond football, Unite8 Sports will carry kabaddi, cricket, badminton, wrestling, boxing, and combat sports. Airtel Digital TV has already lined up the four channels in its 300-303 band starting June 4. The brand went live on Instagram with its logo and tagline within hours of the deal's announcement.

Zee's stock surged roughly 7 percent on the news, signaling that investors view the FIFA acquisition as a genuine growth lever, not just a content expense.

## The NRI Angle

This is where it gets personal for the diaspora. The 2026 World Cup is being hosted in the US, Canada, and Mexico — the three countries with the largest concentrations of Indian immigrants in the Western Hemisphere. Matches will be played in cities like New York, Los Angeles, Dallas, Toronto, Miami, and Houston — all major NRI hubs.

For the first time, many NRIs will be able to attend World Cup matches in person while simultaneously having access to Indian-language commentary through Zee's Hindi broadcast. The combination of a home-country broadcaster covering a tournament literally in your backyard creates a unique cultural moment.

Watch parties at Indian restaurants, community centers, and cricket club halls across North America will have an Indian broadcast option — something that was genuinely uncertain until 48 hours ago.

## What It Means for Indian Football

The deal also arrives at a time when Indian football is experiencing quiet but real growth. The Indian Super League has stabilized as a domestic product, and the women's national team has been gaining visibility. FIFA's youth tournaments — the Men's U-17 and Women's U-17 World Cups — are included in the Zee package through 2034, providing consistent exposure to development-level international football.

The question now is whether Zee can convert the World Cup moment into a sustainable sports business or whether Unite8 Sports becomes another short-lived experiment in Indian sports broadcasting. The answer will likely depend on what happens in the three weeks between June 11 and July 19, when the world watches the most expanded World Cup in history — 48 teams for the first time — and India watches along, finally, with the broadcast secured.""",
    "image_person": None,
    "image_query": "FIFA World Cup stadium",
    "image_fallback_query": "football soccer stadium crowd"
})

# ── ARTICLE 2: Bhooth Bangla Netflix OTT ──
articles.append({
    "headline": "Bhooth Bangla Hits Netflix on June 12. Akshay Kumar's Biggest Hit in Years Is About to Find Its Real Audience.",
    "subheadline": "The Priyadarshan reunion grossed ₹264 crore worldwide in theatres. Netflix paid ₹60 crore for the digital rights alone. NRIs who missed the theatrical run get their shot in ten days.",
    "slug": "bhooth-bangla-netflix-ott-release-june-12-akshay-kumar-priyadarshan-nri-20260602",
    "category": "entertainment",
    "sources": json.dumps(["Sacnilk", "Filmfare", "Bollywood Hungama"]),
    "body": """Akshay Kumar and Priyadarshan made some of Bollywood's most beloved comedies together — Hera Pheri, Garam Masala, Bhagam Bhag, Bhool Bhulaiyaa. Then they stopped working together for the better part of two decades. When they finally reunited for Bhooth Bangla, the question was whether the old magic was still there.

The box office answered definitively. Bhooth Bangla, a horror-comedy that opened on April 10, has now grossed ₹264 crore worldwide, with ₹171 crore in India net collections — making it Akshay Kumar's biggest hit in years and a certified commercial success. The film ran for over six weeks in theatres, an increasingly rare feat in an era of two-week theatrical windows.

Now, on June 12, Bhooth Bangla arrives on Netflix. And for the Indian diaspora, this is arguably the more important release date.

## The Economics Tell the Story

The film was produced on a budget of approximately ₹120 crore, which sounds like a big bet until you look at what the producers recovered before a single ticket was sold. Netflix acquired the digital rights for ₹60 crore. Zee Cinema paid ₹25 crore for satellite rights. Zee Music Company picked up the music rights for ₹10 crore. That is ₹105 crore in non-theatrical revenue — nearly 88 percent of the production budget recovered through deals alone.

Every rupee from the box office was essentially profit from day one. It is a blueprint that more Bollywood producers are trying to replicate: build a film with enough star power and franchise potential to command premium pre-release deals, then let the theatrical run provide pure upside.

## Why It Worked

Bhooth Bangla is Priyadarshan's second Hindi-language horror comedy after the original Bhool Bhulaiyaa in 2007. The genre has since exploded — Stree, Bhediya, Munjya, and their various sequels have proven that Indian audiences will reliably turn out for well-executed horror comedies. Bhooth Bangla entered a proven market with the strongest possible brand combination.

The cast goes deep: Paresh Rawal, Tabu, Wamiqa Gabbi, Rajpal Yadav, Mithila Palkar, Jisshu Sengupta, and Manoj Joshi. For viewers who grew up on the Priyadarshan-Akshay comedies of the 2000s, the ensemble triggers a specific kind of nostalgia — the promise of genuine laughs without the heaviness that has dominated recent Hindi cinema.

The film follows a family that moves into a cursed ancestral property, with Akshay Kumar playing the wisecracking protagonist who must navigate both supernatural threats and family politics. Reviews praised the film's commitment to practical comedy — physical gags, situational humor, and character-driven laughs rather than CGI spectacle.

## The NRI Streaming Moment

For the diaspora, Bhooth Bangla's Netflix premiere fills a specific gap. Many NRIs follow Bollywood releases closely but cannot always make it to the limited theatrical windows in overseas markets. A horror comedy with 2000s-era Bollywood nostalgia, a cast that spans generations, and the Akshay-Priyadarshan brand is practically engineered for family streaming.

The film's Week 5 collections — ₹7.15 crore, with consistent daily numbers and steady occupancy — suggest that it was still drawing audiences to theatres well into its second month. On Netflix, where it will be available in multiple languages, the potential reach multiplies dramatically.

## What Comes Next for Akshay

The Bhooth Bangla success has given Akshay Kumar significant momentum heading into his next release. Welcome to the Jungle, the third instalment of the Welcome franchise directed by Ahmed Khan, arrives on June 26 — just two weeks after Bhooth Bangla hits Netflix. If that film delivers even a fraction of Bhooth Bangla's performance, 2026 will mark the definitive Akshay Kumar comeback that his fans have been waiting for since the post-pandemic slump that saw films like Bachchhan Paandey, Raksha Bandhan, and Selfiee underperform.

For now, though, the Priyadarshan reunion stands on its own. Mark June 12. The ghosts are coming to your living room.""",
    "image_person": "Akshay Kumar",
    "image_query": None,
    "image_fallback_query": "Bollywood horror comedy movie"
})

# ── ARTICLE 3: Raaka Silence Speculation ──
articles.append({
    "headline": "Nobody Has Heard From the Raaka Set in Two Months. That Is Either Very Good or Very Bad for Allu Arjun.",
    "subheadline": "Atlee's ₹600-crore sci-fi epic with Deepika Padukone, Hollywood VFX studios, and a half-human Allu Arjun has gone completely quiet. The speculation is getting louder than the film.",
    "slug": "raaka-allu-arjun-atlee-silence-production-update-deepika-vfx-nri-20260602",
    "category": "entertainment",
    "sources": json.dumps(["Gulte", "Cinema Express", "Sacnilk", "Bollywood Hungama"]),
    "body": """The first-look poster dropped on April 8, Allu Arjun's birthday. It showed the Pushpa star in a rugged, primal avatar — heavy textures, wild beard, tusk-like elements emerging from his face. The title was one word: Raaka. The internet lost its collective mind. Two months later, nobody has heard anything.

No shooting updates. No behind-the-scenes footage. No official statements about the production timeline. The silence around what is reportedly the most expensive Indian film currently in production — budgeted at over ₹600 crore — has fueled a wave of speculation that the makers have so far chosen not to address.

## What We Know

Raaka is directed by Atlee, the filmmaker behind Bigil, Mersal, and Jawan. It is his first collaboration with Allu Arjun and his first film outside the commercial formula that made him a household name. The project is billed as a large-scale entertainer blending science fiction, fantasy, and superhero elements, set in a parallel universe.

The production pedigree is staggering. Five Hollywood VFX studios — Legacy Effects, Fractured FX, Spectral Motion, Lola VFX, and ILM Technoprops — are involved. Sun Pictures, owned by media mogul Kalanithi Maran, is producing. The cast includes Deepika Padukone in the lead opposite Allu Arjun, with Mrunal Thakur and Janhvi Kapoor in prominent roles. Reports have linked Vijay Sethupathi and Kajol to supporting parts, though the makers have not confirmed the full ensemble.

Principal photography began in Mumbai in mid-June 2025. Allu Arjun is reportedly playing a dual role. The film is expected to release in multiple languages.

## What We Do Not Know

This is where it gets complicated. Several industry trackers believe the production is moving slower than initially planned. Reports surfaced in late May that Deepika Padukone — who announced her second pregnancy on April 19 — may not be joining the shoot anytime soon. According to Bollywood Hungama, Atlee's team has drafted a strategic plan to use a body double for the majority of Deepika's remaining action sequences, as she reportedly has around 50 days of shooting left for the film.

Femina George, the Minnal Murali actor, confirmed in a recent interview that she has a role in Raaka. She described landing the part as an unexpected development, having been noticed by the makers through her breakout portrayal as Bruce Lee Biji. The confirmation was welcome, but it also highlighted a pattern: individual cast members are talking about the film, but the official production has said almost nothing since the first-look reveal.

## The Stakes

Raaka is not just another big-budget Indian film. At ₹600 crore, it sits alongside the most expensive productions in Indian cinema history. The VFX-heavy nature of the film means that delays in principal photography cascade into post-production timelines, which cascade into release windows, which cascade into recovery math.

For Allu Arjun, the film carries a specific weight. After Pushpa 2: The Rule became one of the highest-grossing Indian films of all time, the expectation is that his next project will match or exceed that scale. A VFX-driven sci-fi spectacle is inherently riskier than a sequel to a proven franchise. The commercial viability of the film depends heavily on the execution of its visual effects — the very department that requires the most time and the least schedule disruption.

For the diaspora audience that turned Pushpa 2 into a cultural event in overseas markets, Raaka represents the next evolution of Allu Arjun's global appeal. The science fiction genre has traditionally been underrepresented in Indian cinema at this scale. If Raaka delivers, it could redefine what is possible.

## The Silence Problem

The film industry runs on buzz. Controlled silence can build mystique — Rajamouli perfected this approach with RRR and Baahubali. But uncontrolled silence breeds speculation, and speculation rarely favors big-budget productions. When your film costs ₹600 crore and your lead actress's pregnancy has introduced legitimate scheduling questions, the absence of communication becomes the story.

Fans and industry watchers are not asking for a trailer. They are asking for an update — a shooting schedule, a casting confirmation, a behind-the-scenes photo. Even a small signal would redirect the conversation from anxiety to anticipation. The makers of Raaka have the material to generate that excitement. The question is why they have chosen not to.""",
    "image_person": "Allu Arjun",
    "image_query": None,
    "image_fallback_query": "Indian sci-fi movie visual effects"
})

# ── ARTICLE 4: Welcome to the Jungle ──
articles.append({
    "headline": "Welcome to the Jungle Has 15 Stars, One Director, and Bollywood's Last Great Comedy Franchise at Stake. It Opens June 26.",
    "subheadline": "After Bhooth Bangla's ₹264-crore run, Akshay Kumar returns with the Welcome threequel. JioStar has locked theatrical, satellite, and OTT rights. The ensemble includes everyone from Sanjay Dutt to Johnny Lever.",
    "slug": "welcome-to-the-jungle-akshay-kumar-ensemble-comedy-june-26-jiostar-nri-20260602",
    "category": "entertainment",
    "sources": json.dumps(["Sacnilk", "Bollywood Hungama", "Filmfare"]),
    "body": """In a year where Hindi cinema has been dominated by intense actioners, dark dramas, spy thrillers, and violent spectacles, Welcome to the Jungle is positioning itself as the antidote. A full-blown, unabashedly silly, family-friendly comedy with a cast list so long it looks like a wedding invitation.

The third instalment of the Welcome franchise opens on June 26. Director Ahmed Khan is at the helm, and the ensemble reads like a roll call of Bollywood's comedy establishment: Akshay Kumar, Suniel Shetty, Paresh Rawal, Sanjay Dutt, Arshad Warsi, Raveena Tandon, Lara Dutta, Jacqueline Fernandez, Disha Patani, Johnny Lever, Rajpal Yadav, Tusshar Kapoor, Shreyas Talpade, Krushna Abhishek, and Kiku Sharda. That is fifteen names, and there are reportedly more in smaller roles.

## The Franchise Math

The original Welcome (2007) was a Priyadarshan production that became a surprise blockbuster, eventually achieving cult status through television reruns and meme culture. Welcome Back (2015), directed by Anees Bazmee, underperformed relative to expectations but still earned enough to keep the franchise viable. The gap between the second and third films — eleven years — is unusually long for a Bollywood franchise.

During that gap, the comedy landscape shifted dramatically. Stree, Fukrey Returns, and the entire horror-comedy wave created a new template for commercial laughs. Multi-starrer comedies fell out of fashion as the economics of assembling large casts became increasingly prohibitive. Welcome to the Jungle is, in many ways, a throwback to an older model of Hindi comedy — the kind where the jokes come from character collisions and the star power comes from sheer volume.

## The Business Model

The film's distribution structure tells an interesting story. JioStar has acquired the domestic theatrical rights along with satellite and OTT rights, giving the Reliance-Disney joint venture complete control over the film's Indian lifecycle. It will release in theatres under JioStar's distribution, followed by a television premiere and digital streaming on JioHotstar.

On the international front, Pen Marudhar is reportedly in advanced talks for the overseas theatrical rights, with strong interest driven by the franchise's popularity in key diaspora markets — the Middle East, the UK, and North America. The deal structure mirrors a growing Bollywood trend: bulk domestic deals that ensure cost recovery before release, with overseas rights monetized separately for maximum value.

Produced by Firoz Nadiadwallah, Cape of Good Films, Seeta Films, and several co-producers, the film reportedly carries a controlled budget — a strategic decision given the uncertain box office climate for non-franchise comedies.

## The Akshay Kumar Factor

Welcome to the Jungle arrives exactly two weeks after Bhooth Bangla premieres on Netflix. If Akshay Kumar manages to deliver back-to-back successes — one in the horror-comedy space with Priyadarshan, another in the slapstick space with Ahmed Khan — 2026 will mark the most convincing stretch of his career since the pre-pandemic era.

The teaser, dropped on May 15 without prior announcement, delivered exactly what the franchise's fanbase wanted: laugh-out-loud moments set against a jungle backdrop, trademark slapstick confusion, and the promise that the film stays true to the Welcome formula. The teaser's reception on social media was overwhelmingly positive, with fans expressing confidence in the film's box office prospects.

For Akshay Kumar specifically, the film represents a return to the comedy zone where his instincts are sharpest. Long before Pan-India spectacles and action universes became the industry's obsession, Akshay built a comic legacy through physical gags, deadpan reactions, and an ability to find genuine humor in absurd situations. Welcome to the Jungle is a bet that audiences still want that version of him.

## The NRI Factor

Comedy franchises have historically performed well in overseas markets because they travel on nostalgia. NRI audiences who grew up watching Welcome on television, quoting Majnu Bhai and Uday Bhai dialogue, represent a pre-sold audience for the threequel. The franchise's humor does not require cultural translation — it runs on universal slapstick and character archetypes that work across geographies.

The June 26 release date is strategically placed at the end of the month, giving the film a relatively clear window after the expected dominance of Peddi (June 4) and Bandar (June 5) in the first week. By late June, theatres will be looking for fresh content, and a big-screen comedy with this many recognizable faces is exactly what the release calendar needs.

Whether Welcome to the Jungle recaptures the original's lightning or joins the growing list of belated franchise sequels that could not quite find the old magic will come down to one thing: whether it is actually funny. The cast, the brand, and the timing are all in place. Ahmed Khan has the ingredients. The recipe is what matters now.""",
    "image_person": "Akshay Kumar",
    "image_query": None,
    "image_fallback_query": "Bollywood comedy movie ensemble cast"
})


# ── Main execution ──

print("=" * 60)
print(f"Entertainment Writer — {datetime.now(timezone.utc).isoformat()}")
print("=" * 60)

published_count = 0

for i, article in enumerate(articles):
    print(f"\n{'─' * 40}")
    print(f"Article {i+1}: {article['headline'][:80]}...")
    print(f"{'─' * 40}")

    # Image sourcing
    img_url = None
    img_attribution = None

    if article.get('image_person'):
        print(f"  → Trying Wikipedia for: {article['image_person']}")
        img_url = fetch_wikipedia_person_image(article['image_person'])
        if img_url:
            img_attribution = "Wikimedia Commons"

    if not img_url and article.get('image_query'):
        print(f"  → Trying Pexels for: {article['image_query']}")
        img_url = fetch_pexels_image(article['image_query'], article.get('image_fallback_query'))
        if img_url:
            img_attribution = "Pexels"

    if not img_url and article.get('image_fallback_query') and not article.get('image_query'):
        print(f"  → Trying Pexels fallback for: {article['image_fallback_query']}")
        img_url = fetch_pexels_image(article['image_fallback_query'])
        if img_url:
            img_attribution = "Pexels"

    # Validate image
    if img_url:
        if is_banned_url(img_url):
            print(f"  ✗ Banned URL detected, skipping: {img_url[:60]}")
            img_url = None
        elif not validate_image(img_url):
            print(f"  ✗ Image validation failed, skipping: {img_url[:60]}")
            img_url = None

    if not img_url:
        print("  ⚠ No valid image found — publishing without image")

    # Build payload
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "sources": article["sources"],
        "is_editorial": False,
    }

    if img_url:
        payload["image_url"] = img_url
        payload["image_attribution"] = img_attribution

    # Validation
    headline_len = len(article["headline"])
    subheadline_len = len(article["subheadline"])
    body_words = len(article["body"].split())

    print(f"  Headline: {headline_len} chars | Subheadline: {subheadline_len} chars | Body: {body_words} words")

    if headline_len < 20 or headline_len > 200:
        print(f"  ✗ Headline length out of range ({headline_len}), skipping")
        continue
    if subheadline_len < 15:
        print(f"  ✗ Subheadline too short ({subheadline_len}), skipping")
        continue
    if body_words < 400:
        print(f"  ✗ Body too short ({body_words} words), skipping")
        continue

    # Insert
    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result[0].get('id') if isinstance(result, list) else result.get('id')
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
        published_count += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

    time.sleep(1)

print(f"\n{'=' * 60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
print(f"{'=' * 60}")
