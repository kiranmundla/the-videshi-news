#!/usr/bin/env python3
"""
Entertainment writer — June 6, 2026 batch (v2)
Uses permanent Wikimedia/Pexels URLs directly. Adds vertical field.
"""

import json, os, sys, time, subprocess, urllib.parse, requests
from datetime import datetime, timezone

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

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
            # Use thumbnail (330px) as-is per rules
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            if thumb:
                print(f"  ✓ Wiki thumb: {thumb[:80]}...")
                return thumb
            if orig:
                print(f"  ✓ Wiki original: {orig[:80]}...")
                return orig
    except Exception as e:
        print(f"  ⚠ Wiki error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml" or ii.get("width",0) < 300:
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url",""), "title": page.get("title","")})
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS_KEY: return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large"]
            print(f"  ✓ Pexels: {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image_url(url):
    """Verify URL returns image with Content-Length > 5000."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give Content-Length
        if "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ INSERTED: {article['slug']}")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLE 1 ──
def write_article_1():
    print("\n═══ Article 1: Made In India: A Titan Story ═══")
    slug = "made-in-india-titan-story-jim-sarbh-naseeruddin-shah-amazon-mx-player-nri-20260606"

    # Image: Jim Sarbh
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Jim Sarbh")
    img_caption = "Jim Sarbh, who plays Xerxes Desai in Made In India: A Titan Story"
    img_attr = "Wikimedia Commons"

    if not img_url:
        commons = fetch_wikimedia_commons("Jim Sarbh actor")
        if commons:
            img_url = commons[0]["url"]
    if not img_url:
        img_url = fetch_pexels("vintage Indian watch craftsmanship")
        img_attr = "Pexels"
        img_caption = "A precision timepiece being crafted"

    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, trying alternatives")
        img_url = fetch_pexels("watch mechanism luxury")
        img_attr = "Pexels"
        img_caption = "A precision watch mechanism"

    body = """Every Indian who grew up in the 1990s remembers their first Titan watch. For millions of diaspora families, a Titan Sonata or a Raga was the first gift at graduation, the first serious accessory at a first job abroad. The brand was India before India was cool.

Now, Amazon MX Player has turned that origin story into *Made In India: A Titan Story*, a six-episode docudrama directed by Robbie Grewal and adapted from Vinay Kamath's book *Titan: Inside India's Most Successful Consumer Brand*. It premiered on June 3, and it is streaming for free — no subscription required.

## A Story About Belief, Not Just Watches

The series traces the journey of Xerxes Desai, a Tata executive played by Jim Sarbh, who in 1978 was "loaned" to build the Vashi Bridge in New Bombay. When he returned to a desk job at Tata headquarters five years later, boredom set in fast. J.R.D. Tata — played by Naseeruddin Shah with the kind of quiet command that makes you sit up straighter — challenged him to turn around Tata Press, a loss-making division.

What followed was accidental genius. While reviving Tata Press, Desai stumbled on a startling fact: imported watches were the most smuggled consumer goods in India. The insight became an obsession. Could India build a watch that was not just affordable, but aspirational? Could "Made in India" mean something on a wrist?

JRD Tata said yes.

## Jim Sarbh and Naseeruddin Shah Are the Reason to Watch

Jim Sarbh delivers what multiple reviewers are calling his most layered performance to date. His Xerxes Desai is controlled yet deeply emotional — a man who radiates the kind of restless energy that builds institutions but also alienates colleagues. Sarbh captures the vulnerability beneath the confidence, the moments of doubt that never quite make it to the boardroom.

Naseeruddin Shah, meanwhile, does more with limited screen time as JRD Tata than most actors manage in a full season. His performance is understated brilliance — commanding, graceful, and quietly powerful. When Shah's JRD gives Desai a nod of approval, you feel the weight of an empire's trust shifting.

The ensemble — Vaibhav Tatwawadi, Kaveri Seth, Lakshvir Saran, Namita Dubey, Ashwath Bhatt — fills out a world that feels lived-in. Every character has a purpose. The production design recreates 1980s India with Ambassador cars, Lambretta scooters, and offices that smell of carbon paper. Real archival photographs are woven into the narrative so seamlessly that the line between fiction and history dissolves.

## Why This Matters for the Diaspora

For NRIs, *Made In India* is not just a corporate drama. It is a mirror.

The series is set in pre-liberalisation India, a country that many diaspora viewers remember but their children never knew. A country where importing a watch required navigating a maze of licensing, where "made in India" was often a euphemism for second-best, where ambition was routinely strangled by bureaucracy. Watching Xerxes Desai battle these forces — and win — is a reminder that the India that produced the engineers and doctors and entrepreneurs who emigrated was also producing something else: institutional ambition on a scale that the world had not yet learned to respect.

Titan went on to become the world's fifth-largest watch manufacturer. Today, it is part of a conglomerate that employs over 900,000 people. But in 1984, it was just an idea in a borrowed office with a borrowed team. The series captures that gap between origin and outcome with precision and emotional intelligence.

## The Verdict

*Made In India: A Titan Story* has received near-universal acclaim. India Forums gave it 4 out of 5 stars. IANS gave it a full 5 stars. Bollywood Hungama called it "brilliantly made." The consensus is clear: this is one of the best Indian series of 2026.

The fact that it is streaming for free on Amazon MX Player — no paywall, no subscription — makes it even more accessible. For diaspora families looking for a weekend binge that the whole family can watch together, this is it.

Six episodes. Six hours. The story of how India learned to tell time on its own terms.

*Made In India: A Titan Story is now streaming on Amazon MX Player.*"""

    article = {
        "headline": "Made In India: A Titan Story Is Now Streaming for Free. It May Be the Best Indian Series of 2026 So Far.",
        "subheadline": "Jim Sarbh and Naseeruddin Shah turn the origin of India's biggest watch brand into six hours of riveting television. The NRI nostalgia runs deep.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Amazon MX Player", "India Forums", "IANS", "Bollywood Hungama", "Vinay Kamath / Titan book"]),
        "image_url": img_url or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ── ARTICLE 2 ──
def write_article_2():
    print("\n═══ Article 2: Main Vaapas Aaunga ═══")
    slug = "main-vaapas-aaunga-imtiaz-ali-diljit-dosanjh-ar-rahman-partition-june-12-nri-20260606"

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Diljit Dosanjh")
    img_caption = "Diljit Dosanjh, who stars alongside Naseeruddin Shah in Main Vaapas Aaunga"
    img_attr = "Wikimedia Commons"

    if not img_url:
        commons = fetch_wikimedia_commons("Diljit Dosanjh")
        if commons:
            img_url = commons[0]["url"]
    if not img_url:
        img_url = fetch_pexels("India Pakistan border Wagah")
        img_attr = "Pexels"
        img_caption = "The Wagah border between India and Pakistan"

    body = """Imtiaz Ali has spent two decades making films about people who leave home and spend the rest of their lives trying to find their way back. *Jab We Met*, *Love Aaj Kal*, *Rockstar*, *Tamasha*, *Amar Singh Chamkila* — every one of them is, at its core, a story about departure and return.

Now he has made that theme literal. *Main Vaapas Aaunga* — *I Will Return* — is a Hindi romantic drama set across two timelines: the 1947 Partition and the present day. It arrives in cinemas on June 12, and it brings with it one of the most formidable creative collaborations in contemporary Hindi cinema.

## The Team

Diljit Dosanjh and Imtiaz Ali are reuniting after *Amar Singh Chamkila*, the 2024 Netflix film that earned some of the best reviews of either man's career. Joining them is Naseeruddin Shah, whose presence automatically raises the stakes of any ensemble. Vedang Raina — who broke out with *The Archies* and has been quietly building a reputation as one of his generation's most promising actors — and Sharvari, fresh from the buzz around YRF's spy universe, round out the principal cast. Banita Sandhu and Danish Pandor complete the ensemble.

The music is composed by A.R. Rahman, with lyrics by Irshad Kamil. This is the same trio — Ali, Rahman, Kamil — that created the soundtracks for *Rockstar*, *Highway*, and *Tamasha*, three of the most emotionally resonant Hindi film scores of the last fifteen years. Three singles have already been released: "Kya Kamaal Hai" (sung by Diljit), "Maskara" (by Nilanjana Ghosh Dastidar and Vedang Raina), and "Vo Nahin." Early listener response has been strong, with "Kya Kamaal Hai" in particular becoming a fan favourite.

## The Partition Angle

Partition films have a complicated history in Indian cinema. They tend to either sanitise the horror into melodrama or aestheticise the trauma into art-house contemplation. What makes *Main Vaapas Aaunga* intriguing is its dual-timeline structure, which promises to connect the events of 1947 to the emotional lives of people in 2026. This is not a period film. It is a film about what the period did to the people who lived through it — and what it continues to do to their descendants.

For the Indian diaspora, Partition is not history. It is family lore. It is the reason a grandmother never went back to Lahore. It is the reason a family recipe has no written record, only muscle memory. It is the reason someone's surname changed somewhere between Rawalpindi and Delhi. A Partition film that treats these echoes seriously — that makes the connection between 1947 and the way diaspora families carry inherited grief — has the potential to resonate far beyond the box office.

Diljit himself debuted the trailer at his AURA Tour 2026 concert in Toronto, where videos of the audience reaction went viral. The choice was deliberate: a film about Partition, previewed for a diaspora audience, in a city that is home to one of the largest Punjabi communities outside India.

## The June 12 Landscape

*Main Vaapas Aaunga* does not arrive in an empty theatre. June 12 is shaping up to be the most crowded release date of the year, with five new films and a Lagaan re-release competing for screens. The most talked-about clash is with Kangana Ranaut's *Bharat Bhhagya Viddhaata*, a 26/11 drama — which means the same weekend will feature two films dealing with national trauma from opposite ends of the political and aesthetic spectrum.

The Diljit-Kangana parallel is impossible to ignore. In 2020, the two clashed publicly on Twitter over the farmer protests. In 2019, their films *Arjun Patiala* and *Judgementall Hai Kya* released on the same day. Now, once again, their work will be measured against each other at the ticket counter.

For *Main Vaapas Aaunga*, the advantage is the creative pedigree. Imtiaz Ali has never made a film that audiences felt indifferent about. AR Rahman guarantees that at least the music will linger. And Diljit Dosanjh, after Chamkila and a global concert tour, is arguably at the peak of his cultural influence.

Whether the film delivers on that promise will be clear on June 12. But the ingredients — the team, the story, the timing — suggest something that could be genuinely important, not just commercially successful.

*Main Vaapas Aaunga releases in cinemas on June 12, 2026.*"""

    article = {
        "headline": "Main Vaapas Aaunga Arrives June 12. Imtiaz Ali, Diljit Dosanjh, and AR Rahman Have Made a Partition Film That Is Also a Love Story.",
        "subheadline": "The trio that gave us Amar Singh Chamkila reunites with Naseeruddin Shah, Vedang Raina, and Sharvari for a story that bridges 1947 and today.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Bollywood Hungama", "Wikipedia", "YouTube / Applause Entertainment", "Tips Music"]),
        "image_url": img_url or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


# ── ARTICLE 3 ──
def write_article_3():
    print("\n═══ Article 3: Yash's Toxic in Limbo ═══")
    slug = "yash-toxic-postponed-indefinitely-reshoot-rumors-buzz-crisis-nri-20260606"

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Yash (actor)")
    img_caption = "Yash, whose pan-India film Toxic has been postponed indefinitely"
    img_attr = "Wikimedia Commons"

    if not img_url:
        commons = fetch_wikimedia_commons("Yash KGF Kannada actor")
        if commons:
            img_url = commons[0]["url"]
    if not img_url:
        img_url = fetch_pexels("empty cinema theater dark")
        img_attr = "Pexels"
        img_caption = "An empty cinema hall"

    body = """In early 2026, *Toxic: A Fairy Tale for Grown-ups* was one of the most anticipated films in Indian cinema. Yash, the man who turned *KGF* into a franchise that rewrote the rules of South Indian box office, was returning with a film that promised to be darker, stranger, and more ambitious than anything he had done before. Directed by Geetu Mohandas, co-starring Kiara Advani, Nayanthara, Huma Qureshi, Tara Sutaria, and Rukmini Vasanth, the film had everything: star power, a visionary director, a budget reportedly exceeding ₹500 crore, and an initial release date of March 19, 2026.

Then the postponements began.

## From March to June to Nowhere

The first delay was attributed to geopolitical instability in the Middle East. The Gulf region, home to approximately 10 million Indians, has become a critical revenue market for pan-India blockbusters, particularly those from the South. *KGF: Chapter 2* had set extraordinary benchmarks in the Gulf, and the *Toxic* team determined that releasing during a period of regional conflict would risk a significant portion of their overseas recovery.

The release was pushed to June 4. That date, too, was abandoned. This time, the stated reason was more expansive: the team wanted to align international distribution and strategic partnerships for a synchronised global launch. In a statement, the producers cited the response they received after presenting the film at CinemaCon and said they wanted to give the film a wider, more impactful worldwide rollout.

No new date has been announced.

## The Reshoot Rumours

Into the silence rushed speculation. A rumour circulated on social media claiming that Yash was deeply unhappy with the current output and that a massive 100-day reshoot was being planned, pushing the release window all the way back to 2027.

The production team moved quickly to deny the reports, calling them "wrong and baseless." But as trade analysts and industry watchers have noted, the damage from such rumours is difficult to reverse. The absence of any fresh promotional material — no new teaser, no behind-the-scenes content, no social media campaign — has left a vacuum that speculation has been happy to fill.

## The Buzz Problem

This is *Toxic*'s real crisis. The film is complete. It was presented at CinemaCon. It stars some of the biggest names in Indian cinema. But it has lost the one thing that no amount of money can buy back: momentum.

Trade circles are openly discussing the erosion of buzz. When *KGF: Chapter 2* was building toward release, the promotional machinery was relentless — teasers, trailers, fan events, social media engagement at scale. For *Toxic*, the approach has been the opposite: near-total silence from the makers and the leading man.

The problem is compounded by what has happened around the film. In the time since *Toxic* was first announced, the Indian theatrical landscape has produced several massive hits — *Dhurandhar 2*, *Karuppu*, *Peddi* — each of which has consumed the attention and enthusiasm that *Toxic* once commanded. The longer the film stays in limbo, the harder it becomes to recapture that attention.

## What the Delay Means for Diaspora Audiences

For NRI audiences who follow South Indian cinema, *Toxic* was supposed to be a cultural event. Yash's fan base in North America, the Gulf, and Europe has grown significantly since KGF, and a global synchronised release was precisely what those audiences wanted. Instead, they are left with uncertainty — no release date, no trailer updates, and a growing sense that something may be wrong with the product.

The one bright spot is Yash's confirmed role as Ravana in *Ramayana*, alongside Ranbir Kapoor, slated for a Diwali 2026 release. That project ensures Yash remains in the conversation. But *Toxic* was supposed to be his statement film — the one that proved KGF was not a fluke but a floor.

## What Needs to Happen

The path forward is straightforward, even if it is not easy. Yash needs to break his silence. A teaser, a behind-the-scenes look, or at the very least a strong personal statement would go a long way toward quashing the negativity. The team needs to announce a concrete release date and commit to it. And the promotional campaign needs to begin in earnest, with the intensity and scale that a ₹500 crore production demands.

*Toxic* is not dead. It is not even in trouble, necessarily — the film is complete, the cast is extraordinary, and the director has a track record of delivering unconventional work. But it is in danger of becoming yesterday's news before it ever reaches a screen. And in an industry that moves as fast as Indian cinema does in 2026, that is a risk no one can afford.

*Toxic: A Fairy Tale for Grown-ups has no confirmed release date.*"""

    article = {
        "headline": "Yash's Toxic Has Been Postponed Indefinitely. The Reshoot Rumours Are Denied. The Silence Is Not Helping.",
        "subheadline": "The KGF star's pan-India biggie was supposed to redefine the summer. Instead, it has become a case study in how to lose momentum.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Gulte", "Sacnilk", "Pinkvilla", "Bollywood Hungama"]),
        "image_url": img_url or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False
    }
    return insert_article(article)


if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Entertainment Writer v2 (June 6, 2026)")
    print("=" * 60)

    results = []
    for fn in [write_article_1, write_article_2, write_article_3]:
        try:
            art_id = fn()
            results.append(("✓" if art_id else "✗", fn.__name__))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback; traceback.print_exc()
            results.append(("✗", fn.__name__))
        time.sleep(1)

    print("\n" + "=" * 60)
    for status, name in results:
        print(f"  {status} {name}")
    print("=" * 60)
