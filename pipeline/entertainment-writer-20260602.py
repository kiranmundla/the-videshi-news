#!/usr/bin/env python3
"""Entertainment writer — 2026-06-02 batch"""

import json, os, sys, time, uuid, re, urllib.parse
import requests

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels ──
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image sourcing ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        time.sleep(2)  # Rate limit courtesy delay
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial use)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer originalimage (higher res), fall back to thumbnail
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        elif r.status_code == 429:
            print(f"  ⚠ Wikipedia rate limited for '{person_name}', trying thumbnail fallback...")
            time.sleep(5)
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial use)"},
                timeout=10
            )
            if r2.status_code == 200:
                data = r2.json()
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if img:
                    print(f"  ✓ Wikipedia image found (retry) for '{person_name}': {img[:80]}...")
                    return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check image URL returns HTTP 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't have content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        headers = {"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial use)"}
        r = requests.get(image_url, timeout=15, headers=headers)
        if r.status_code == 429:
            print(f"  ⚠ Rate limited downloading image, retrying after 5s...")
            time.sleep(5)
            r = requests.get(image_url, timeout=15, headers=headers)
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None

        content_type = r.headers.get("Content-Type", "image/jpeg")
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(person_name=None, pexels_query=None, pexels_fallback=None, slug="article"):
    """Source image following the hierarchy: Wikipedia → Pexels → None."""
    img_url = None
    attribution = None

    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"

    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "Pexels"

    if img_url:
        # Upload to Supabase for permanence (except Pexels which is permanent)
        if "upload.wikimedia.org" in img_url:
            uploaded = upload_to_supabase_storage(img_url, f"{slug}.jpg")
            if uploaded:
                return uploaded, attribution
            # If upload fails, use Wikipedia URL directly (it's permanent)
            if validate_image_url(img_url):
                return img_url, attribution
        elif "images.pexels.com" in img_url:
            if validate_image_url(img_url):
                return img_url, attribution
        else:
            uploaded = upload_to_supabase_storage(img_url, f"{slug}.jpg")
            if uploaded:
                return uploaded, attribution

    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
        "is_editorial": False,
        "is_featured": False,
        "tags": article.get("tags", []),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        print(f"✅ Published: {article['headline'][:70]}...")
        return art_id
    else:
        print(f"❌ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ═══════════════════════════════════════════════════════════════
# ARTICLES
# ═══════════════════════════════════════════════════════════════

articles = []

# ─── Article 1: Katrina Kaif May Photo Dump + Baby Vihaan ───
articles.append({
    "headline": "Katrina Kaif Just Shared Her May Photo Dump. Baby Vihaan's Tiny Hands Stole Every Frame.",
    "subheadline": "The actress introduced her seven-month-old son to paparazzi at the airport — then asked them not to photograph his face. Her Instagram post reveals a family quietly rewriting celebrity parenthood.",
    "slug": "katrina-kaif-may-photo-dump-baby-vihaan-vicky-kaushal-birthday-airport-nri-20260602",
    "person": "Katrina Kaif",
    "pexels_query": None,
    "pexels_fallback": None,
    "sources": [
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "India Forums", "url": "https://www.indiaforums.com"},
    ],
    "tags": ["Katrina Kaif", "Vicky Kaushal", "Baby Vihaan", "celebrity parenthood", "Bollywood"],
    "body": """Katrina Kaif does not post often. When she does, the internet stops scrolling and starts studying every pixel. Her May photo dump, dropped on June 1, is a masterclass in what a celebrity can share without actually revealing much — and why that restraint matters more than a perfectly curated grid.

## A Birthday, a Book, and a Pair of Tiny Hands

The carousel opens with warmth, not spectacle. There are images from Vicky Kaushal's 38th birthday celebration on May 16 — a cake reading "Happy Birthday Papa" with three little figures on top, a family picnic spread, and the kind of candid shots that feel more living room than red carpet. But it is one specific frame that has consumed comment sections across platforms: a photograph of baby Vihaan Kaushal's tiny hands, visible while Katrina appears to be reading *Gujapati Kulapati* to her seven-month-old son.

No face. No full reveal. Just hands and a children's book. And yet, it says everything about how Katrina and Vicky have chosen to navigate parenthood in the age of paparazzi culture.

## The Airport Moment That Rewrote the Rules

Days before the Instagram post, the couple was spotted at Mumbai airport with Vihaan. What happened next was unusual by Bollywood standards. Vicky smiled and posed at the entrance. Katrina held the baby. And then she made a request that a photographer later shared publicly: she asked that no pictures of the baby's face be taken or circulated.

She did not hide. She did not run. She introduced her son to the media — and then drew a line. The gesture echoed the privacy-first approach adopted by a handful of celebrity parents globally, from Ryan Reynolds and Blake Lively to Virat Kohli and Anushka Sharma. But in Mumbai's paparazzi ecosystem, where photographers routinely camp outside hospitals and schools, it carried a different weight.

For NRI families watching from Houston or London or Toronto, the moment resonated on a deeper frequency. Many diaspora parents navigate their own version of this — deciding how much of their children's lives to share on social media, balancing family WhatsApp groups that want every photo with the instinct to protect a child's digital footprint before they are old enough to consent.

## What Katrina's Caption Actually Tells You

The caption was vintage Katrina — warm, a little scattered, and oddly specific. She wrote about discovering the best hot chocolate and the best coffee in the same month, mentioned her legs hurting from watching someone named Reza, and claimed she discovered the song "Naa Pushde" entirely on her own. Each photo got its own micro-caption, including one that read: "Happy Family, but mummy has a strange hairstyle."

Fans, predictably, zeroed in on the hairstyle. Comments like "hair goals omg" and "mommy kat is everything" flooded the post. But the real story was in the tone — a woman who once guarded every public appearance with meticulous precision now sharing something genuinely unpolished. Motherhood has not made Katrina more public. It has made her more comfortable with imperfection.

## The Professional Pause

On the work front, Katrina has not announced any new project since Vihaan's birth on November 7, 2025. Reports continue to swirl about her potential return in Farhan Akhtar's *Jee Le Zaraa* alongside Priyanka Chopra Jonas and Alia Bhatt, but nothing has been confirmed. Meanwhile, Vicky Kaushal is deep into filming *Love & War* with Ranbir Kapoor and Alia Bhatt, directed by Sanjay Leela Bhansali, scheduled for January 21, 2027.

The career break is deliberate, not accidental. Katrina has been open about wanting to be present for Vihaan's first year, and the May photo dump — with its park walks, coffee dates, and picture books — suggests she is exactly where she wants to be.

## Why This Matters Beyond the Celebrity Bubble

The Kaif-Kaushal approach to parenting visibility is becoming a template. In an industry that has historically monetized every baby reveal, gender announcement, and first birthday, their decision to share on their own terms — one tiny hand at a time — feels like a quiet revolution. It is not about secrecy. It is about agency.

For the diaspora, whose relationship with Bollywood celebrity culture often runs through Instagram stories consumed at 2 AM in a different time zone, this photo dump offered something rarer than a baby face reveal: a reminder that some of the most meaningful moments do not need to be fully visible to be fully felt.

Vihaan Kaushal is seven months old. He has appeared in exactly one photograph, shown only his hands, and already become the most talked-about baby in Bollywood. His parents would not have it any other way.""",
})

# ─── Article 2: Karan Johar Instagram Unfollow ───
articles.append({
    "headline": "Karan Johar Unfollowed Shah Rukh Khan, Alia Bhatt, and Half of Bollywood on Instagram. Then He Explained Why.",
    "subheadline": "The filmmaker's mass Instagram unfollow triggered conspiracy theories across Reddit and Twitter. His response — 'It's a digital detox, not national news' — says more about celebrity social media culture than any of the theories did.",
    "slug": "karan-johar-instagram-unfollow-srk-alia-kareena-digital-detox-nri-20260602",
    "person": "Karan Johar",
    "pexels_query": None,
    "pexels_fallback": None,
    "sources": [
        {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
    ],
    "tags": ["Karan Johar", "Shah Rukh Khan", "Instagram", "social media", "digital detox", "Bollywood"],
    "body": """It started, as most modern Bollywood controversies do, on Reddit. Eagle-eyed users noticed something odd on Karan Johar's Instagram: his following count had plummeted. Shah Rukh Khan — gone. Alia Bhatt — gone. Kareena Kapoor Khan, Kajol, Varun Dhawan, Sidharth Malhotra, Ananya Panday, Kartik Aaryan, Manish Malhotra, even the entire Khan family including Gauri, Aryan, and Suhana — all unfollowed in what appeared to be a single, ruthless purge.

Within hours, the screenshots were everywhere. Theories multiplied like franchises at a YRF pitch meeting. Had Karan and SRK finally had a falling out? Was there trouble with Alia after years of mentorship? Had a professional disagreement turned personal? Was this a calculated PR move before a new project announcement?

## The Actual Explanation Was Anti-Climactic

Karan Johar, never one to let a narrative run without his input, responded through his Instagram Story with characteristic exasperation. "It's a DIGITAL DETOX!!!!" he wrote, the four exclamation marks doing a lot of heavy lifting. "Am unfollowing everyone to reduce my time and energy spent on the gram!!! This can't be national news for god's sake... please clickbait something else! This is irrelevant!"

The statement was simultaneously a denial, a clarification, and a critique of the media ecosystem that had turned a follower count into a Bollywood crisis. It was also, inadvertently, the most honest thing Karan Johar has said about social media in years.

## The Friendship That Made This News

The reason the unfollow became a story at all — rather than a footnote — is the Karan-SRK relationship. This is not a casual industry friendship. Karan Johar launched his directorial career with Shah Rukh Khan in *Kuch Kuch Hota Hai* in 1998. Over the next two decades, Khan starred in *Kabhi Khushi Kabhie Gham*, *Kabhi Alvida Naa Kehna*, and *My Name Is Khan*. Karan has publicly credited SRK with shaping not just his filmography but his identity as a filmmaker.

Unfollowing SRK on Instagram, in the public imagination, was the digital equivalent of removing a foundation stone. That it meant nothing — that it was just a man reducing his screen time — reveals how completely we have allowed social media metrics to stand in for human relationships.

## What NRIs Recognize in This Story

For the diaspora, this story hits a nerve that has nothing to do with Bollywood. Indian families — particularly those spread across multiple countries and time zones — have built their emotional infrastructure on WhatsApp groups, Instagram follows, and Facebook birthday wishes. An unfollow is not just a button click. It is a statement. A muted group chat is a cold war. A delayed response is a diplomatic incident.

Karan Johar's digital detox, whether genuine or performative, mirrors a conversation happening in living rooms from Fremont to Flushing: how much of our emotional life are we outsourcing to platforms designed to monetize our attention? When unfollowing your oldest friend becomes national news, the problem is not with the person who clicked unfollow. It is with a culture that made the follow count a measure of loyalty in the first place.

## The Broader Celebrity Detox Trend

Karan is not the first high-profile figure to publicly pull back from social media. Deepika Padukone has spoken about her complicated relationship with Instagram. Aamir Khan famously quit all platforms in 2022. Globally, celebrities from Selena Gomez to Tom Holland have documented cycles of deactivation and return.

But Karan Johar's version is distinctly Bollywood. He did not deactivate. He did not go silent. He unfollowed — the most visible, most trackable, most public form of digital withdrawal possible. And then he got annoyed when people noticed. It is the social media equivalent of slamming a door and then being surprised by the noise.

## What This Actually Means for Dharma

From a professional standpoint, absolutely nothing. Karan Johar's Dharma Productions has a slate that includes the highly anticipated *Love & War* and multiple projects in various stages of development. His professional relationships with the people he unfollowed remain unchanged — no one in the industry is evaluating partnerships based on Instagram follows, even if the public does.

The real takeaway is more mundane and more universal: a 54-year-old man decided he was spending too much time on Instagram and pressed a lot of buttons. The fact that this became the most discussed entertainment story of the week says less about Karan Johar and more about the rest of us.

He unfollowed everyone. The sky did not fall. Bollywood did not implode. *Kuch Kuch Hota Hai* is still a classic. Maybe that is the digital detox the rest of us need — the realization that an unfollow is just an unfollow, and the relationships that matter were never measured in follower counts to begin with.""",
})

# ─── Article 3: Divyanka Tripathi & Vivek Dahiya Twins ───
articles.append({
    "headline": "Divyanka Tripathi and Vivek Dahiya Waited Ten Years for This Moment. Then Twins Arrived.",
    "subheadline": "Television's most stable couple welcomed twin boys on May 26, announced them with a 'Karan Arjun' reference, and came home to a building guard's blessings. The response tells you everything about what Indian audiences want from their celebrities.",
    "slug": "divyanka-tripathi-vivek-dahiya-twin-boys-karan-arjun-nri-20260602",
    "person": "Divyanka Tripathi",
    "pexels_query": "newborn baby twins hospital",
    "pexels_fallback": "baby nursery celebration",
    "sources": [
        {"name": "Bollywood Shaadis", "url": "https://www.bollywoodshaadis.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"},
    ],
    "tags": ["Divyanka Tripathi", "Vivek Dahiya", "twins", "Indian television", "celebrity parenthood", "Bollywood"],
    "body": """There is a specific kind of love that the Indian diaspora reserves for celebrity couples who do not make headlines for drama. Divyanka Tripathi and Vivek Dahiya have built their public image on exactly this foundation — a decade of quiet stability in an industry that feeds on chaos. On May 26, 2026, that foundation expanded by two.

The couple welcomed twin baby boys, and their announcement carried the only pop culture reference that could possibly do the moment justice: "Mere Karan Arjun aa gaye!"

## The Announcement That Broke the Internet's Wholesome Meter

Divyanka and Vivek shared the news through a joint Instagram post that read: "We asked for happiness, God said take double. Blessed with twin baby boys." The caption added: "The wait is finally over... 'The Boys' are here, and life already feels more beautiful than we ever imagined."

The "Karan Arjun" reference — invoking the 1995 Salman Khan-Shah Rukh Khan reincarnation drama — was pitch-perfect. It acknowledged the ten-year wait since their 2016 wedding with humor rather than sentimentality. It positioned the twins as destined arrivals, not medical outcomes. And it gave every desi parent in the comment section the perfect reaction template. Within hours, the reference had become a shorthand, shared across WhatsApp groups and family chats with the universal understanding that only an Indian audience would fully appreciate.

## Ten Years, Zero Drama

Divyanka and Vivek met on the sets of *Yeh Hai Mohabbatein*, the long-running Star Plus drama that cemented Divyanka's position as one of Indian television's most beloved faces. They married in 2016 in a ceremony that was widely covered but notably free of the manufactured spectacle that often accompanies celebrity weddings.

For the next decade, they became something rare in Indian entertainment: a celebrity couple that the public rooted for without reservation. No breakup rumors. No public arguments. No cryptic Instagram stories. The absence of drama was itself remarkable, and their fan base — heavily concentrated among NRI women who grew up watching *Yeh Hai Mohabbatein* in syndication — treated their stability as aspirational rather than boring.

The pregnancy announcement came on Gudi Padwa in March 2026. Even then, the response was notably different from the typical Bollywood pregnancy discourse. There were no speculation cycles about due dates or gender reveals. The couple shared updates on their timeline, and the audience respected the boundaries.

## The Hospital Exit That Went Viral

On May 29, three days after the birth, Divyanka and Vivek made their first public appearance with the twins. The hospital exit video quickly became one of the most shared entertainment clips of the week. A decorated car with blue and white balloons pulled up. Vivek, beaming, announced to the gathered photographers: "Presenting the new mother and father in town." Divyanka emerged in white, radiant, and immediately requested that photographers not show the babies' faces.

But the moment that truly captured hearts came at their apartment building. As Divyanka walked in carrying one of her sons, she stopped at the gate. The building's security guard — an older man who had presumably watched the couple for years — was opening the gate. Instead of walking past, Divyanka paused, smiled, and showed her baby to the guard. He gently touched the infant and gave his blessings, an *aashirwad* caught on camera that felt more meaningful than any celebrity photo op.

The video went viral not because of what it showed but because of what it represented: a woman who, in the most significant moment of her personal life, remembered to include someone who is often invisible in celebrity narratives.

## Addressing the Questions She Never Owed Answers To

Throughout the decade-long wait, speculation about Divyanka's pregnancy was a recurring theme in tabloid coverage. Was there a medical issue? Had they chosen to delay? Was IVF involved? The questions were invasive, and Divyanka largely ignored them.

After the birth, she addressed it simply: it was a natural pregnancy, and she became a mother when she felt the time was right. She shared that she had a strong instinct from God and had been preparing herself. The matter-of-factness of the response was its own statement — a rejection of the idea that a woman's reproductive timeline requires public explanation.

## The NRI Connection

For diaspora families, particularly those who have watched Divyanka since her *Banoo Main Teri Dulhann* days, the twins represent a specific kind of emotional payoff. Many NRI women who were watching *Yeh Hai Mohabbatein* in their twenties are now in their thirties, navigating their own timelines around marriage, children, and career. Divyanka's decade-long journey — unmarked by public pressure or performative urgency — mirrors a choice that many diaspora women recognize.

The "Karan Arjun" reference, too, carries a different resonance abroad. For NRIs, the 1995 film is not just a movie. It is a cultural artifact — watched on rented VHS tapes in apartments in Edison and Brampton, quoted at family gatherings, and embedded in a generation's emotional vocabulary. Naming your twins after a Bollywood destiny narrative is not just a joke. It is a declaration of cultural continuity.

Divyanka Tripathi did not need twins to trend. She trended because, after ten years, the story wrote itself — and she let it.""",
})


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    published = 0
    for art in articles:
        print(f"\n{'='*60}")
        print(f"Processing: {art['headline'][:70]}...")

        # Source image
        img_url, img_attr = source_image(
            person_name=art.get("person"),
            pexels_query=art.get("pexels_query"),
            pexels_fallback=art.get("pexels_fallback"),
            slug=art["slug"],
        )

        art["image_url"] = img_url
        art["image_attribution"] = img_attr

        # Word count check
        word_count = len(art["body"].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ⚠ Article below 400-word floor! Skipping.")
            continue

        # Insert
        art_id = insert_article(art)
        if art_id:
            published += 1
            # If we got an image, update the article with it
            if img_url:
                print(f"  Image: {img_url[:70]}...")
            else:
                print(f"  ⚠ No image sourced — article published without image")

        time.sleep(1)  # Small delay between inserts

    print(f"\n{'='*60}")
    print(f"✅ Published {published}/{len(articles)} articles")


if __name__ == "__main__":
    main()
