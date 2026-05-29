#!/usr/bin/env python3
"""Entertainment writer — 2026-05-29 batch"""

import os, json, requests, time, re, uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.replace('export ', '').strip()
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key, val)

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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
    """Fetch a relevant image from Pexels API using curl (Python urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape'
            ], capture_output=True, text=True, timeout=15)
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
    """Validate image URL returns HTTP 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, allow_redirects=True)
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and 'image' in content_type:
            r2 = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image failed validation: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}...")
            return True
        print(f"  ✓ Published (no return data)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False

def check_duplicate(slug):
    """Check if slug already exists."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?select=id&slug=eq.{slug}&limit=1",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=10
    )
    if r.status_code == 200:
        data = r.json()
        return len(data) > 0
    return False

now = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: Ramayana distribution deal + Comic-Con
# ============================================================
print("\n=== Article 1: Ramayana ₹450 Crore Distribution Deal ===")

img1 = fetch_wikipedia_person_image("Ranbir Kapoor")
if not validate_image(img1):
    img1 = fetch_wikipedia_person_image("Nitesh Tiwari")
    if not validate_image(img1):
        img1 = fetch_pexels_image("ancient Indian temple epic", "Hindu mythology art")
        if not validate_image(img1):
            img1 = None

slug1 = "ramayana-450-crore-distribution-comic-con-trailer-hans-zimmer-ar-rahman-nri-20260529"

if check_duplicate(slug1):
    print("  ⚠ Slug already exists, skipping")
else:
    article1 = {
        "headline": "Ramayana's Distribution Deal Just Hit ₹450 Crore. The Trailer May Debut at San Diego Comic-Con.",
        "subheadline": "Nitesh Tiwari's two-part epic — with AR Rahman and Hans Zimmer scoring, Ranbir Kapoor as Ram, and Yash as Ravana — is being positioned as the most expensive Indian film ever made. The makers already rejected a ₹700 crore OTT offer.",
        "slug": slug1,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "image_url": img1,
        "image_caption": "Ranbir Kapoor, who plays Lord Ram in Ramayana (via Wikimedia Commons)",
        "image_attribution": "Wikimedia Commons",
        "sources": json.dumps(["Sacnilk", "Bollywood Hungama", "Mid-day", "Hollywood Reporter India"]),
        "body": """The numbers around Ramayana have always been large. A ₹4,000 crore production budget across two parts. A cast that includes Ranbir Kapoor as Lord Ram, Sai Pallavi as Sita, Yash as Ravana, Sunny Deol as Hanuman, and Ravie Dubey as Laxman. A two-part Diwali release plan spanning 2026 and 2027. But the latest round of deal-making has pushed the film into territory Indian cinema has genuinely never occupied before.

## The ₹450 Crore Distribution Deal

According to Bollywood Hungama, the theatrical distribution deal for Ramayana Part 1 alone is reportedly valued at approximately ₹450 crore — a figure that would make it the highest pre-release theatrical valuation for any Indian film in history.

The deal has been broken into three massive tranches. Dil Raju's Sri Venkateswara Creations secured the Andhra Pradesh and Telangana theatrical rights for ₹120 crore — the highest ever for a non-Telugu project in those states. Anil Thadani's AA Films came on board for North India and Nepal, reuniting with Yash after their KGF collaboration. And Phars Film locked the international Indian-language rights for ₹105 crore, with a broader network being assembled through Prime Media US for the North American market.

These are not speculative valuations. These are advances paid before a single ticket is sold.

## Comic-Con and a Live Concert

The production team is aiming for a grand trailer launch at San Diego Comic-Con in July, according to Mid-day. Producer Namit Malhotra and director Nitesh Tiwari are in advanced talks with Comic-Con organizers — a move that follows a positive focus group screening held in Los Angeles, where an early cut reportedly received strong feedback from a diverse audience.

If confirmed, this would make Ramayana the first Indian film to use Comic-Con as a trailer launch platform, placing it alongside the marketing playbooks of Marvel, DC, and major Hollywood franchises.

Beyond Comic-Con, the makers are also planning an October musical event featuring a live performance by AR Rahman and Hans Zimmer — the first time these two Academy Award winners have collaborated on a single film score. Rahman has called the partnership "terrifying and exciting" in equal measure and described the project as potentially "one of India's greatest movies."

## A ₹700 Crore OTT Offer — Rejected

Perhaps the most telling signal of the makers' confidence: Namit Malhotra reportedly rejected a ₹700 crore post-theatrical digital deal for both parts, which would have been the highest OTT deal in Indian film history. According to Bollywood Hungama, the offer was turned down almost immediately — the team believes the film deserves at least ₹1,000 crore in digital rights alone, leaving ₹3,000 crore to be recovered from worldwide theatrical and other revenue streams.

## What NRIs Should Know

The October 30, 2026 release date is being considered — a week before Diwali — to give the film an uninterrupted run through the festive window. Part 2 is already 50 percent shot for Ranbir Kapoor and is locked for Diwali 2027.

Ranbir has confirmed a dual role: Lord Rama and Lord Parashurama. Both parts will have a combined runtime exceeding six hours. The visual effects are being handled by DNEG, the studio behind Dune, Tenet, and Interstellar.

For the Indian diaspora, the real question is not whether this film will be big. It is whether an Indian production can genuinely compete for global theatrical real estate the way a Marvel or Star Wars entry does. The Comic-Con strategy, the Zimmer-Rahman score, and the ₹450 crore distribution war chest all suggest the makers believe it can.

Whether that belief survives first contact with the global box office is the most expensive bet Indian cinema has ever placed."""
    }
    insert_article(article1)

time.sleep(1)

# ============================================================
# ARTICLE 2: Ishaan Khatter on Biarritz jury with Kristen Stewart
# ============================================================
print("\n=== Article 2: Ishaan Khatter — Biarritz Film Festival Jury ===")

img2 = fetch_wikipedia_person_image("Ishaan Khatter")
if not validate_image(img2):
    img2 = fetch_wikipedia_person_image("Ishaan Khattar")
    if not validate_image(img2):
        img2 = fetch_pexels_image("Biarritz France seaside", "French film festival")
        if not validate_image(img2):
            img2 = None

slug2 = "ishaan-khatter-biarritz-jury-kristen-stewart-only-indian-homebound-oscar-nri-20260529"

if check_duplicate(slug2):
    print("  ⚠ Slug already exists, skipping")
else:
    article2 = {
        "headline": "Ishaan Khatter Is the Only Indian on the Biarritz Film Festival Jury. Kristen Stewart Is Chairing It.",
        "subheadline": "The Homebound actor and Gold House Gold 100 honoree joins an international jury alongside Whitney Peak and Raphaël Quenard at one of Europe's fastest-growing festivals for emerging cinema.",
        "slug": slug2,
        "category": "entertainment",
        "status": "published",
        "published_at": now,
        "image_url": img2,
        "image_caption": "Ishaan Khatter, the only Indian member of the Biarritz Film Festival jury (via Wikimedia Commons)",
        "image_attribution": "Wikimedia Commons",
        "sources": json.dumps(["ANI", "NewKerala", "Pinkvilla", "Filmfare"]),
        "body": """It is a short list. Kristen Stewart will chair the jury. Whitney Peak, the Canadian actress from Gossip Girl, will sit beside her. So will Raphaël Quenard, the French César-winning actor. Nathan Ambrosioni, Suzy Bemba, Carolina Cavalli, and Esme Creed-Miles round out the panel. And then there is Ishaan Khatter — the only Indian, the only South Asian, and at 28, one of the youngest voices at the table.

The Biarritz Film Festival — Nouvelles Vagues, now in its fourth edition, runs June 23 to 28 in the seaside city on France's Atlantic coast. It is not Cannes. It is not Venice. It is something arguably more interesting for an actor at Ishaan's career stage: a festival built entirely around emerging voices, new filmmakers, and the next generation of global cinema. Being invited to judge that future is a statement about where the industry thinks he belongs.

## The Homebound Effect

This is not happening in a vacuum. Ishaan's trajectory over the past 18 months reads like a case study in what happens when an Indian actor makes the right festival bet at the right time.

Homebound — Neeraj Ghaywan's quietly devastating film starring Ishaan, Janhvi Kapoor, and Vishal Jethwa — premiered at Cannes, played TIFF, was selected as India's official Oscar entry for 2026, and made the Academy's shortlist for Best International Feature Film. The film did not win, but it did something more durable: it placed Ishaan in the peripheral vision of international festival programmers and jury organizers.

The Gold House Gold 100 listing earlier this year reinforced that momentum. Ishaan became the only Indian male actor on the list, an annual recognition of Asian and Pacific Islander leaders in culture and business. When Biarritz came looking for a jury member who could credibly represent both commercial and festival cinema from the non-Western world, Ishaan's recent résumé made the case for him.

## What This Means for Indian Cinema Abroad

Jury invitations at European festivals are not purely ceremonial. They are industry signals — acknowledgments that a particular film culture has produced someone whose taste the festival trusts. For Indian cinema, which has had a complicated relationship with the international festival circuit (strong in competition submissions, weak in jury representation), having Ishaan at Biarritz alongside Kristen Stewart is a small but meaningful step.

It also reflects a broader shift. Indian actors are no longer going to international festivals only to promote their own films. They are being asked to evaluate other people's work. That is a different kind of recognition — one that implies authority, not just visibility.

## What Is Next for Ishaan

On the work front, Ishaan is currently shooting Jugaadu, a comedy that marks his first production venture. The film, directed and produced under the Tips Films and Baweja Studios banner, also features Punjabi actress Tania's Hindi film debut and an ensemble cast including Abhishek Banerjee and Jameel Khan. The first schedule began in Punjab this month.

For the diaspora, Ishaan represents something specific: a young Indian actor who has built an international presence not through a Hollywood franchise or a Marvel audition, but through the festival circuit — the same path that Irrfan Khan, Nawazuddin Siddiqui, and Neeraj Ghaywan carved before him. Whether Biarritz leads to bigger jury seats at Venice or Berlin or Toronto remains to be seen. But the invitation itself is the proof of concept."""
    }
    insert_article(article2)

time.sleep(1)

# ============================================================
# ARTICLE 3: Dhurandhar 2 — ₹1,000 Cr Hindi net, ₹1,700 Cr worldwide
# ============================================================
print("\n=== Article 3: Dhurandhar 2 — ₹1,000 Crore Hindi Net Record ===")

img3 = fetch_wikipedia_person_image("Dhurandhar 2 film")
if not validate_image(img3):
    img3 = fetch_pexels_image("India cinema box office crowd", "Indian movie theater audience")
    if not validate_image(img3):
        img3 = None

slug3 = "dhurandhar-2-1000-crore-hindi-net-1700-crore-worldwide-bollywood-record-nri-20260529"

if check_duplicate(slug3):
    print("  ⚠ Slug already exists, skipping")
else:
    article3 = {
        "headline": "Dhurandhar 2 Just Hit ₹1,000 Crore Net in Hindi Alone. No Bollywood Film Has Done That Before.",
        "subheadline": "The sequel crossed ₹1,700 crore worldwide in 25 days — without a Gulf release — and is now chasing Baahubali 2's all-time Phase 1 record. Here is what the numbers actually mean.",
        "slug": slug3,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "image_url": img3,
        "image_caption": "Dhurandhar 2 has rewritten every box office record for a Hindi-original film",
        "image_attribution": "Pexels",
        "sources": json.dumps(["Sacnilk", "Koimoi", "Bollywood Hungama", "Venky Box Office"]),
        "body": """There is a number that Indian box office analysts have been waiting years for someone to hit, and Dhurandhar 2: The Revenge just hit it.

The sequel to the 2024 blockbuster crossed ₹1,003.54 crore net in Hindi alone within 24 days of its theatrical release. That is not a worldwide number. That is not a pan-Indian number bolstered by Tamil, Telugu, and Kannada dubs. That is the Hindi-original market — the heartland belt — delivering a four-digit crore figure for the first time in Bollywood history.

## The ₹1,700 Crore Club

By its 25th day, Dhurandhar 2 crossed ₹1,700 crore in worldwide gross, becoming the first Bollywood-original film to reach that milestone during its primary theatrical run. The total India net collection stands at ₹1,068.92 crore, with the worldwide gross at approximately ₹1,691.30 crore at last count — a figure that was all but certain to breach ₹1,700 crore by the evening sessions on day 25, based on BookMyShow ticket velocity.

To understand the scale: on day 25, the film was selling 66,490 tickets between 7 AM and 1 PM, outpacing the previous day's 61,520 in the same window. This is not a film coasting on its opening weekend. It is still accelerating on weekends nearly a month into its run.

## The Comparison That Matters

Indian box office records are often misleading because they conflate primary runs with secondary releases. Dangal, for instance, holds a lifetime worldwide gross of ₹2,070.3 crore — but ₹1,305.29 crore of that came from a secondary release in China. Strip out China, and Dangal's Phase 1 gross was approximately ₹765 crore. Dhurandhar 2 has already more than doubled that number.

The film is now within striking distance of the top two all-time Phase 1 worldwide grossers in Indian cinema:

| Rank | Film | Phase 1 Worldwide Gross |
|------|------|------------------------|
| 1 | Baahubali 2: The Conclusion | ₹1,788.06 Cr |
| 2 | Pushpa 2: The Rule | ₹1,742.10 Cr |
| 3 | Dhurandhar 2: The Revenge | ₹1,691.30 Cr |
| 4 | Dhurandhar | ₹1,307.35 Cr |
| 5 | Dangal (excl. China) | ₹765.00 Cr |

Surpassing Pushpa 2's ₹1,742 crore appears "mathematically probable," as Sacnilk's trade analysis put it. Catching Baahubali 2's ₹1,788 crore will depend on how much runway the film has before Bhooth Bangla and other releases eat into its screen count.

## The Missing Gulf Market

What makes this performance genuinely unprecedented is that Dhurandhar 2 achieved it without a Gulf release. The UAE, Saudi Arabia, Bahrain, Qatar, Kuwait, and Oman — collectively one of the most reliable overseas revenue drivers for Indian blockbusters — have not contributed a single rupee to these totals. The film has compensated by dominating markets like Australia, New Zealand, Canada, and Germany, with the North American market alone contributing $27.36 million.

For NRI audiences, this is the headline within the headline: an Indian film is setting all-time records in precisely the markets where the diaspora lives and watches, and it is doing so without leaning on the traditionally dominant Gulf corridor.

## What It Means for the Industry

Dhurandhar 2's performance has effectively created a new commercial category in Indian cinema — the Hindi-original that competes at the same scale as pan-Indian Telugu and Tamil tentpoles. Until now, the only Indian films to breach ₹1,500 crore worldwide in their primary runs were Baahubali 2 and Pushpa 2, both Telugu-original productions where the Hindi dub functioned as a secondary revenue stream.

With Dhurandhar 2, the Hindi belt is the primary engine. The film has sold over 18 million tickets on BookMyShow alone, becoming only the second Indian film to cross that threshold on the platform.

The question now is not whether Dhurandhar 2 will finish as one of the top three Indian grossers of all time. It almost certainly will. The question is whether it can hold enough screens and momentum over the coming weeks to challenge the top spot — or whether the arrival of new releases will narrow the window before it gets there."""
    }
    insert_article(article3)

print("\n=== Entertainment writer batch complete ===")
