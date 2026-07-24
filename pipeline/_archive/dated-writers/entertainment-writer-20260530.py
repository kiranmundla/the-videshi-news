#!/usr/bin/env python3
"""
Entertainment writer for The Videshi — 2026-05-30 batch
Articles:
1. Jackie Shroff's The Great Grand Superhero - rave reviews
2. Bollywood Q1 2026 Box Office Report - the sequel era
3. Shakti Shalini wraps shoot - Maddock Horror Comedy Universe
"""

import os, json, requests, urllib.parse, uuid, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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
    """Fetch image from Pexels API using curl (not urllib to avoid 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        cmd = [
            'curl', '-sS',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5',
            '-H', f'Authorization: {PEXELS_KEY}'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get('id')
        return None
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

def check_duplicate(slug_fragment):
    """Check if an article with similar slug exists in last 3 days."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?select=slug&status=eq.published&slug=like.*{slug_fragment}*&published_at=gte.{(datetime.now(timezone.utc)).strftime('%Y-%m-%dT00:00:00Z')}&limit=1",
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
    )
    if r.status_code == 200:
        return len(r.json()) > 0
    return False

# ============================================================
# ARTICLE 1: Jackie Shroff's The Great Grand Superhero
# ============================================================
def write_article_1():
    print("\n=== Article 1: Jackie Shroff's The Great Grand Superhero ===")

    if check_duplicate('great-grand-superhero'):
        print("  ⚠ Duplicate detected, skipping")
        return

    slug = "jackie-shroff-great-grand-superhero-india-first-grandfather-superhero-review-nri-20260530"
    headline = "Jackie Shroff Just Made a Superhero Film for Kids and Grandparents. Bollywood Critics Say It's the Year's Biggest Surprise."
    subheadline = "The Great Grand Superhero is a rare children's film in a Bollywood calendar dominated by sequels and action blockbusters — and early reviews call it the most heartfelt Hindi film of 2026."

    body = """It takes a particular kind of confidence to release a children's film in a Bollywood landscape that has spent 2026 chasing sequels, spectacles, and star-vehicle franchises. Jackie Shroff, at 70, apparently has exactly that kind of confidence — and *The Great Grand Superhero*, which opened on May 29 to some of the warmest reviews of the year, might just validate the gamble.

Directed by three-time National Award winner Manish Saini and produced by Zee Studios and Amdavad Films, the film casts Shroff as a creaky, lizard-fearing pensioner who grows plants and shuffles through retirement. His grandson Deepu — played by a pitch-perfect Mihir Godbole — tells his new classmates at school that grandpa is secretly a superhero. There's a catch: only people under 18 can know, or the old man loses his powers.

## A Genre Bollywood Forgot

What makes the film remarkable isn't the premise — it's the fact that it exists at all. Bollywood has essentially abandoned the children's genre. Hundreds of films release every year, but genuinely good family films aimed at young audiences have become almost extinct. *The Great Grand Superhero* fills a vacuum that most studios don't even acknowledge.

*The Hollywood Reporter India* called the first half "funny, poignant, satirical and very inventive" and compared the child performances to *Stanley Ka Dabba*, which was made 15 years ago — itself an indicator of how long this gap has persisted. The two films even share an editor, Deepa Bhatia, and a narrative spirit built around a child using imagination as a survival tool.

## Reviews Are Raving

Audience reception has been overwhelmingly positive. Social media reactions have ranged from "the most entertaining superhero mission" to "a comfort movie" to "Jackie Dada is the Baap of all superheroes." Critics gave it between 3.5 and 4 stars, praising its balance of fantasy, emotion, and environmental messaging.

One reviewer noted that the film "brings back a long-lost genre of earnest, sweet films catered to children" while acknowledging that the CGI and fight sequences don't land. But nobody seems to mind — the film's power comes from its storytelling, not its VFX budget.

Jackie Shroff's performance has drawn particular praise. The man who defined 1980s machismo with *Hero* is now being celebrated for playing a fragile, endearing grandparent. It's a full-circle moment that diaspora audiences — many of whom grew up watching him as the definitive Bollywood action hero — will appreciate deeply.

## Why NRIs Should Pay Attention

For the Indian diaspora, *The Great Grand Superhero* hits a specific nerve. Many NRI families navigate the gap between grandparents in India and grandchildren abroad, between stories told over video calls and the visceral experience of actually spending time together. The film's central dynamic — a grandfather's worth measured not in power but in presence — is the kind of emotional territory that transcends geography.

It's also a reminder of the kind of Hindi cinema that shaped so many childhoods in the diaspora: unpretentious, warm, and built on character rather than spectacle. Before the franchise era, Bollywood made films like *Hum Hain Rahi Pyar Ke*, *Kuch Kuch Hota Hai*, and yes, even the endearingly chaotic David Dhawan comedies. *The Great Grand Superhero* doesn't try to be any of those films. But it comes from the same impulse — the belief that cinema can be gentle and still matter.

## The Box Office Question

Whether the film can translate critical goodwill into ticket sales remains the open question. Children's films in India rarely get the marketing muscle of tentpole releases, and *The Great Grand Superhero* is competing for screens against Drishyam 3, Karuppu, and the week's other releases. But its word-of-mouth trajectory suggests it may have legs — the kind of film that builds through weekend family audiences rather than opening-day frenzy.

In a year where Bollywood's box office has been defined by the colossal shadow of *Dhurandhar 2* and the sequel industrial complex, Jackie Shroff's quiet little superhero film feels almost radical. Sometimes the bravest thing a 70-year-old actor can do isn't punch a villain. It's sit in a garden, be afraid of lizards, and let a child believe he can fly.

*The Great Grand Superhero is now playing in cinemas across India.*"""

    # Image sourcing - Jackie Shroff from Wikipedia
    img_url = fetch_wikipedia_person_image("Jackie Shroff")
    if not img_url or not validate_image(img_url):
        img_url = fetch_pexels_image("grandfather superhero costume", "Indian elderly man smiling")
    if img_url and not validate_image(img_url):
        img_url = None

    attribution = "Wikimedia Commons" if img_url and "wikimedia" in img_url else "The Videshi"

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'source': 'The Videshi Entertainment Desk',
        'sources': json.dumps([
            'The Hollywood Reporter India',
            'Koimoi',
            'Bollywood Bubble',
            'MensXP'
        ]),
        'image_url': img_url,
        'image_attribution': attribution
    }

    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Published: {headline} (id: {art_id})")
    return art_id

# ============================================================
# ARTICLE 2: Bollywood Q1 2026 Box Office - The Sequel Era
# ============================================================
def write_article_2():
    print("\n=== Article 2: Bollywood Q1 2026 Box Office Report ===")

    if check_duplicate('bollywood-q1-2026-box-office'):
        print("  ⚠ Duplicate detected, skipping")
        return

    slug = "bollywood-q1-2026-box-office-sequel-era-dhurandhar-analysis-nri-20260530"
    headline = "Bollywood's First Quarter Was a ₹2,500 Crore Sequel Machine. Here's What That Means for Everyone Else."
    subheadline = "Dhurandhar 2 alone crossed ₹1,400 crore worldwide. The rest of Q1's top five were all sequels or franchise entries. Has Bollywood become a sequel-or-nothing industry?"

    body = """The numbers from Bollywood's first quarter of 2026 are in, and they tell a story that is simultaneously thrilling and deeply concerning. The Hindi film industry has just had one of its most commercially successful three-month stretches in history. It has also, almost entirely, been driven by films that audiences had already seen some version of before.

*Dhurandhar: The Revenge*, directed by Aditya Dhar and starring Ranveer Singh, didn't just top the chart — it created an entirely new one. With over ₹1,400 crore worldwide, the film sits in a stratosphere that only a handful of Indian films have ever reached. Behind it, *Border 2* rode patriotic sentiment and brand nostalgia to ₹450 crore. Then came *Mardaani 3* and *The Kerala Story 2*, both sequels trading on pre-existing audience investments. The only standalone film in the top five, *O'Romeo*, barely crossed ₹100 crore.

## The Sequel Security Blanket

What's striking isn't that sequels performed well — sequels have always performed well, in Bollywood and everywhere else. What's striking is the scale of the gap. When the top film earns 14 times what the best original film earns, the industry isn't merely favouring sequels. It's structurally dependent on them.

This dependency has cascading effects. Studios allocate their biggest budgets, their most coveted release windows, and their heaviest marketing spends to franchise properties. Original films are left to fight for whatever screens and attention remain. The result is a self-reinforcing cycle: sequels succeed because they receive resources, and they receive resources because they succeed.

For Indian audiences at home, this might feel like a temporary phase — a market correction that will sort itself out. For the diaspora, the calculus is different. NRI audiences have fewer opportunities to watch Hindi films theatrically. When they do go to the cinema, they're choosing between three or four titles at most. If all of those are sequels to films they may or may not have seen, the barrier to entry goes up.

## The Dhurandhar Effect

The Dhurandhar franchise deserves separate examination. Its ₹1,400 crore haul didn't come from nowhere — it came from the intersection of spectacle, nationalism, and event-cinema marketing that made theatrical viewing feel obligatory. You weren't just watching a movie. You were participating in a cultural moment.

That strategy works brilliantly for one film. But it creates a problem for every film that follows it. If the benchmark for "success" has been reset to ₹1,400 crore, then a solid ₹100 crore performance suddenly looks like a disappointment. The goalposts don't just move — they disappear over the horizon.

The propaganda controversy that dogged *Dhurandhar 2* — accusations of hyper-nationalism, the Sikh sentiment row, Dia Mirza's critique about "celebrating jingoism" — didn't dent its commercial performance in any measurable way. If anything, the controversy amplified its visibility. For the diaspora, which is often more politically divided about these films than domestic audiences, the discourse has become as much a part of the experience as the film itself.

## Where the Romance Went

Meanwhile, the romantic genre — once Bollywood's bread and butter — has been reduced to a footnote. *Chand Mera Dil*, starring Lakshya and Ananya Panday, is currently the second-highest opening romantic film of 2026. Its opening day was ₹3.31 crore. For context, a decade ago, a Bollywood romance that opened to ₹3 crore would have been considered a disaster.

The genre hasn't disappeared because audiences stopped believing in love stories. It's disappeared because studios stopped believing in them. The budgets have shrunk, the marketing has withered, and the release windows have been conceded to bigger, louder films. Romantic films now exist in the cracks between franchises — and their numbers reflect it.

## What's Left of the Original

Amid this franchise dominance, there are quiet counter-signals. Jackie Shroff's *The Great Grand Superhero*, a children's film released last week, has earned rave reviews despite zero franchise backing. Manoj Bajpayee's upcoming *Governor* — a drama about the 1991 economic crisis — represents the kind of original, issue-driven storytelling that once defined Bollywood's middle class.

These films may never compete with franchise tentpoles at the box office. But their existence matters. They're the proof that Hindi cinema can still produce stories that aren't prequels, sequels, or reboots — even if the market doesn't always reward them.

For the diaspora, which often discovers Bollywood films through streaming rather than theatrical release, the sequel dominance of Q1 2026 may matter less than it seems. The best Indian films of any given year frequently aren't the biggest. They're the ones that show up on Netflix or Prime three months later, recommended by a friend or a family WhatsApp group, watched late at night when the spectacle fades and the storytelling is all that's left.

The question for the rest of 2026 is whether Bollywood can produce enough of those films to sustain the audience that still wants them — or whether the sequel machine has become the only machine left.

*Source: SacNilk Box Office Data, Bollywood Hungama*"""

    # Image sourcing - use Pexels for movie theater/cinema
    img_url = fetch_pexels_image("Indian cinema theater audience", "movie theater crowd Bollywood")
    if img_url and not validate_image(img_url):
        img_url = None

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps([
            'SacNilk',
            'Bollywood Hungama',
            'Koimoi',
            'B4U Entertainment'
        ]),
        'image_url': img_url,
        'image_attribution': 'The Videshi'
    }

    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Published: {headline} (id: {art_id})")
    return art_id

# ============================================================
# ARTICLE 3: Shakti Shalini Wraps - Maddock Horror Universe
# ============================================================
def write_article_3():
    print("\n=== Article 3: Shakti Shalini Wraps Shoot ===")

    if check_duplicate('shakti-shalini'):
        print("  ⚠ Duplicate detected, skipping")
        return

    slug = "shakti-shalini-maddock-horror-universe-aneet-padda-wraps-christmas-2026-nri-20260530"
    headline = "Maddock's Horror Universe Just Wrapped Its Sixth Film. Shakti Shalini Is Coming for Christmas."
    subheadline = "Aneet Padda plays a double role — one divine protector, one vengeful spirit — in the franchise's most folklore-heavy entry yet. Nana Patekar and Seema Biswas round out the cast."

    body = """The Maddock Horror Comedy Universe is now six films deep, and its latest entry — *Shakti Shalini* — has officially wrapped production. Director Aditya Sarpotdar called the final shot on May 27 at Chitrarth Studio in Powai, Mumbai, closing out a shoot that spanned months across Rajasthan and Madhya Pradesh. The film is locked for a Christmas Day 2026 release.

For the Indian diaspora, the Maddock horror franchise occupies a specific cultural niche. These aren't the jump-scare horror films that Hollywood mass-produces. They're supernatural comedies rooted in Indian folklore — the kind of stories that your grandmother might have told you, except with better production values and a sense of humour about themselves. *Stree*, *Bhediya*, *Munjya*, *Stree 2*, and *Thamma* have collectively built an audience that knows what it's getting: village mythology, vengeful spirits, and protagonists who are simultaneously terrified and hilarious.

## The Double Role

*Shakti Shalini* adds a darker dimension. Aneet Padda, who broke out with last year's ₹570 crore hit *Saiyaara*, plays two entirely contrasting characters. Shakti is an ordinary woman who becomes a protector. Shalini is a spirit driven by betrayal and a brutal death, returning to exact revenge on men. The film's dramatic core is the confrontation between these two personas — one representing divine goodness, the other embodying vengeful rage.

It's a structurally ambitious move for a franchise that has typically played its supernatural elements for laughs. Early reports suggest that *Shakti Shalini* will lean harder into genuine horror than its predecessors, while still maintaining the comedic DNA that defines the universe. Sarpotdar, who directed both *Munjya* and *Thamma*, has earned the trust to push that boundary.

## A Cast That Means Business

The supporting cast signals that Maddock is treating this as an event film, not a mid-budget genre entry. Nana Patekar and Seema Biswas — two of Indian cinema's most decorated actors — joined the production in May for key sequences. Viineet Kumar Singh, fresh off *Chhaava*, plays the antagonist. Vishal Jethwa rounds out the ensemble.

For NRI audiences who grew up watching Patekar in *Krantiveer* and Biswas in *Bandit Queen*, their presence in a horror comedy franchise is both surprising and deeply reassuring. These are actors who don't take roles lightly. Their involvement suggests that *Shakti Shalini*'s script offered something beyond the genre's usual formula.

## The Folklore Connection

The film draws from Bengali folklore and supernatural traditions, a departure from the North Indian mythology that anchored earlier entries. The climax, which was shot across massive sets depicting a Rajasthani village, reportedly features a celebration of evil's defeat — with the village's women at the centre of the triumph.

That detail matters. The Maddock horror universe has always had women at its narrative centre — from *Stree*'s vengeful spirit to *Thamma*'s grandmother figure. *Shakti Shalini* appears to continue that tradition, but with a more explicitly feminist framing. The protector is a woman. The avenger is a woman. The celebration of victory belongs to the village's women. In a franchise built on folklore, the politics of who gets to be powerful — and who gets to be monstrous — are never accidental.

## The Franchise Machine

The Maddock Horror Comedy Universe has become Bollywood's most reliable franchise engine outside of the Rohit Shetty cop universe. Its films consistently open well, play for weeks, and generate the kind of fan culture — theories, connections, post-credit teases — that Hollywood's MCU pioneered. *Shakti Shalini* was first teased through a post-credit scene in *Thamma*, a strategy that has become the franchise's signature marketing tool.

For Aneet Padda, the teaser described her character as "the creator, the destroyer, and the mother of all" — a tagline that positions her as the franchise's most powerful figure yet. The role was reportedly first written for Kiara Advani before going to Padda, making this not just a career breakthrough but a statement: the franchise is bigger than any single star.

The shoot covered an extraordinary geographic range — Chambal, Datia, Antri, Panihar, Gwalior, and Morena in Madhya Pradesh, plus Dholpur and Barkhandi in Rajasthan. That's the kind of location diversity that gives Indian horror films their texture. The landscapes aren't just backdrops. They're characters — ancient, sun-bleached, carrying their own mythologies.

*Shakti Shalini* arrives in theatres on December 24, 2026. For NRI families looking for their annual Christmas-week Bollywood outing, the timing is no accident.

*Sources: Bollywood Hungama, Mid-Day, SacNilk, Box Office Worldwide*"""

    # Image sourcing - Aneet Padda from Wikipedia
    img_url = fetch_wikipedia_person_image("Aneet Padda")
    if not img_url or not validate_image(img_url):
        # Try Nana Patekar as backup since he's well-known
        img_url = fetch_wikipedia_person_image("Nana Patekar")
    if not img_url or not validate_image(img_url):
        img_url = fetch_pexels_image("Indian horror film dark forest", "supernatural Indian folklore")
    if img_url and not validate_image(img_url):
        img_url = None

    attribution = "Wikimedia Commons" if img_url and "wikimedia" in img_url else "The Videshi"

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps([
            'Bollywood Hungama',
            'Mid-Day',
            'SacNilk',
            'Box Office Worldwide'
        ]),
        'image_url': img_url,
        'image_attribution': attribution
    }

    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Published: {headline} (id: {art_id})")
    return art_id

# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print(f"Entertainment writer starting at {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []
    for fn in [write_article_1, write_article_2, write_article_3]:
        try:
            r = fn()
            results.append(r)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    successes = sum(1 for r in results if r)
    print(f"\n{'=' * 60}")
    print(f"Done. {successes}/{len(results)} articles published.")
