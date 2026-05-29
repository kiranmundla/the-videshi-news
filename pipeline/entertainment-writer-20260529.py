#!/usr/bin/env python3
"""Entertainment writer — 2026-05-29 run
3 articles:
1. May 2026 Box Office Report: Regional cinema dominated while Bollywood struggled
2. Ranveer Singh visits Chamundeshwari Temple after Karnataka HC court order
3. FWICE's Non-Cooperation Directive against Ranveer Singh is splitting Bollywood
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# ── Load env files ────────────────────────────────────────────────
def load_env_file(path):
    """Load KEY=VALUE env file into os.environ."""
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

load_env_file(os.path.expanduser("~/.env.supabase"))
load_env_file(os.path.expanduser("~/workspace/.env.pexels"))

# ── Supabase config ───────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ─────────────────────────────────────────────────
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

# ── Image helpers ─────────────────────────────────────────────────
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
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(r.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns 200 with image content-type and decent size."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Try GET if HEAD doesn't give Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}, {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=20,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ✗ Download failed: status={r.status_code}, size={len(r.content)}")
            return None

        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "scontent-"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False


def source_image(person_name=None, pexels_query=None, pexels_fallback=None, article_id=None):
    """Source an image following the hierarchy. Returns final URL or None."""
    img_url = None
    attribution = None

    # 1. Try Wikipedia for person articles
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url and not is_banned_url(img_url):
            attribution = "Wikimedia Commons"

    # 2. Fall back to Pexels
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "Pexels"

    # 3. Validate and upload
    if img_url and not is_banned_url(img_url):
        if validate_image_url(img_url):
            # Upload to Supabase for permanence
            if article_id:
                final_url = upload_to_supabase_storage(img_url, f"{article_id}.jpg")
                if final_url:
                    return final_url, attribution
            return img_url, attribution

    print("  ✗ No valid image found")
    return None, None


# ── Article publishing ────────────────────────────────────────────
def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Source image
    img_url, img_attr = source_image(
        person_name=article.get("image_person"),
        pexels_query=article.get("image_pexels_query"),
        pexels_fallback=article.get("image_pexels_fallback"),
        article_id=art_id,
    )

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "sources": json.dumps(article["sources"]),
        "image_url": img_url,
        "image_attribution": img_attr,
        "image_caption": article.get("image_caption"),
        "tags": [],
        "is_featured": False,
        "is_editorial": False,
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if resp.status_code in (200, 201):
        print(f"✅ Published: {article['headline'][:60]}... → {article['slug']}")
        return art_id
    else:
        print(f"❌ Failed to publish: {resp.status_code} {resp.text[:300]}")
        return None


# ── Articles ──────────────────────────────────────────────────────

articles = [
    # ─── Article 1: May 2026 Box Office Report ───
    {
        "headline": "May 2026 Belonged to Regional Cinema. Bollywood Barely Showed Up.",
        "subheadline": "Suriya, Mohanlal, and Riteish Deshmukh broke records in their languages. Hindi cinema's two big May releases combined for less than half of what Karuppu earned alone.",
        "slug": "may-2026-box-office-regional-cinema-dominates-bollywood-struggles-nri-20260529",
        "image_person": None,
        "image_pexels_query": "Indian cinema audience theater crowd",
        "image_pexels_fallback": "movie theater India",
        "image_caption": "May 2026 saw regional Indian cinema outpace Bollywood at the box office",
        "sources": [
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Koimoi", "url": "https://www.koimoi.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"}
        ],
        "body": """May 2026 just ended, and it settled an argument the Indian film industry has been having for years. Regional cinema isn't the underdog anymore. It's the main event.

## The Numbers Don't Lie

Three films from three different languages outperformed everything Bollywood put out this month — combined. Here's the May 2026 scorecard:

**Suriya's Karuppu** led the charge. The Tamil action drama, directed by RJ Balaji, crossed ₹253 crore worldwide in just 12 days after its May 15 release. In Tamil Nadu alone, it earned over ₹120 crore gross — shattering every career record Suriya has held, including more than doubling his previous biggest grosser, Singam 2. The film has performed strongly with overseas Tamil audiences too, continuing a pattern that NRIs in the US and UK have been driving for years.

**Mohanlal's Drishyam 3** proved the franchise is bulletproof. Despite mixed reviews — critics felt the third instalment couldn't match the first two — audiences showed up anyway. In just six days, the film crossed ₹170 crore worldwide. The overseas number is the real story: roughly ₹90 crore of that total came from international markets, making it the first South Indian film of 2026 to cross $10 million overseas. Kerala led domestically, but the Gulf, North America, UK, and Australia all contributed significantly.

**Raja Shivaji** rewrote Marathi cinema history. Riteish Deshmukh directed and starred in this historical epic, which crossed ₹114 crore worldwide in 26 days — dethroning Sairat's ₹110 crore record that had stood for nearly a decade. And it wasn't alone: Deool Band 2, a devotional drama, opened to ₹2.9 crore and then just kept climbing on word of mouth, reaching ₹26.5 crore in six days and marching toward ₹50 crore.

## Bollywood's Quiet Struggle

Meanwhile, Hindi cinema's May releases landed with a thud. Pati Patni Aur Woh Do — a sequel that the industry had positioned as a safe commercial bet — opened to weak occupancies and never recovered. It managed ₹53.85 crore worldwide, a number that looks even smaller next to what the regional films delivered.

Chand Mera Dil, a romantic drama banking on urban appeal and music-driven promotions, fared worse. It earned roughly ₹21 crore in five days — a number the trade calls "poor" for a film of its scale and marketing spend.

## What the Diaspora Should Know

For NRIs who grew up on Bollywood as India's cultural default, this shift is worth paying attention to. The films drawing the biggest audiences back home aren't Hindi anymore — they're Tamil, Malayalam, and Marathi. Streaming platforms have accelerated this. When Drishyam 3 drops on OTT in a few weeks, it'll be available dubbed and subtitled in multiple languages, reaching audiences who might never have watched a Malayalam film five years ago.

The theatrical ecosystem has also changed. South Indian films now command premium distribution deals in North America and the Gulf — territories that were once considered Hindi-film country. Suriya's Karuppu earned significantly from overseas, a market that Tamil films have been steadily claiming since the Vijay and Rajinikanth blockbusters showed the way.

## The Bigger Picture

May 2026 isn't an anomaly. It's a confirmation. The top-grossing Hindi film this year remains Dhurandhar 2, a sequel that succeeded partly because Ranveer Singh's star power transcends language barriers. Beyond that, Bollywood's 2026 has been inconsistent: Bhooth Bangla (₹193 crore) and Border 2 (₹362 crore) performed, but the mid-range — the ₹50-100 crore tier that used to be Bollywood's bread and butter — has been unreliable.

Regional cinema, by contrast, has been methodical. Tamil, Telugu, Malayalam, Kannada, and now Marathi industries are producing films that work locally and travel globally. They're spending less, earning more, and building franchises that audiences actually want to return to.

The second half of 2026 brings Ram Charan's Peddi, Shah Rukh Khan's King, and the Ramayana adaptation — all massive Hindi releases. But May's numbers suggest that the audience isn't waiting for Bollywood to show up anymore. They've already found what they're watching."""
    },

    # ─── Article 2: Ranveer Singh Chamundeshwari Temple ───
    {
        "headline": "Ranveer Singh Visited Chamundeshwari Temple This Week. A Karnataka Court Made Him Do It.",
        "subheadline": "The actor complied with a High Court directive after his Kantara mimicry controversy sparked an FIR, a public backlash, and an apology that wasn't enough.",
        "slug": "ranveer-singh-chamundeshwari-temple-karnataka-hc-kantara-mimicry-court-order-nri-20260529",
        "image_person": "Ranveer Singh",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "image_caption": "Ranveer Singh complied with a Karnataka High Court order to visit the Chamundeshwari Temple",
        "sources": [
            {"name": "Filmfare", "url": "https://www.filmfare.com/news/south/ranveer-singh-makes-vows-at-chamundeshwari-temple-after-kantara-controversy-and-court-directive-84135.html"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"}
        ],
        "body": """Ranveer Singh climbed the Chamundi Hills in Karnataka this week, walked into the Chamundeshwari Temple, and participated in religious ceremonies. He reportedly made personal vows. It wasn't a pilgrimage. It was a court order.

## How It Started

The controversy traces back to the closing ceremony of the International Film Festival of India in Goa last December. Ranveer was on stage when he launched into an imitation of a sacred Daiva sequence from Rishab Shetty's Kantara franchise — the films that turned Bhoota Kola rituals into a cinematic phenomenon. The crowd reacted. Then the internet reacted harder.

During the performance, Ranveer referred to the sacred Daivas as ghosts. In the coastal Karnataka tradition, Daivas — spirit worship deities central to Tulu culture — are not entertainment. They are living religious practice. A video of the moment went viral, and the backlash was immediate.

Rishab Shetty himself weighed in. "That makes me uncomfortable," the Kantara director said. "While much of the film is cinema and performance, the Daiva element is sensitive and sacred."

## The Legal Fallout

An FIR was filed. The case made its way to the Karnataka High Court. In April, Ranveer submitted a revised affidavit to the court, and the proceedings moved toward resolution. The court accepted what it termed an "unconditional apology" — but with conditions attached. Ranveer was ordered to visit the Chamundeshwari Temple within four weeks and offer prayers there.

This week, he complied.

## The Apology Before the Court

Before the legal proceedings escalated, Ranveer had tried to contain the damage through social media. "I have always deeply respected every culture, tradition, and belief in our country," he wrote on Instagram. "If I've hurt anyone's sentiments, I sincerely apologise."

For many in Karnataka and the Tulu-speaking community, the Instagram post wasn't enough. The complaint argued that a public figure with Ranveer's reach had a responsibility to understand what he was performing before performing it — particularly when it involved sacred rituals that communities still actively practice.

## Why This Matters for the Diaspora

The Kantara mimicry incident sits at the intersection of several tensions that the Indian diaspora knows well: the line between appreciation and appropriation, the distance between Bollywood's Mumbai bubble and the regional cultures it borrows from, and the question of who gets to represent whose traditions on a national stage.

Kantara became a pan-Indian hit precisely because it treated Bhoota Kola with reverence. Millions of Indians — including NRIs who packed North American theatres for the film — responded to that authenticity. When a Bollywood star appeared to reduce the same tradition to a party trick, the reaction wasn't just about hurt sentiments. It was about a pattern.

Bollywood has a long history of flattening regional cultures into content — turning classical dances into item numbers, sacred rituals into comedy bits, regional accents into punchlines. The backlash against Ranveer's IFFI performance was, in part, an assertion that the audience has changed. They know what they're watching. They know what's being mocked.

## What Happens Next

The Karnataka High Court has signalled that the matter is nearing resolution. With the temple visit completed and the apology on record, the legal case is expected to close in the coming weeks.

For Ranveer, the timing is complicated. He's simultaneously navigating the FWICE non-cooperation directive over the Don 3 dispute, preparing for his ₹300 crore zombie thriller Pralay (shooting begins in August), and managing a public image that has taken hits from multiple directions in 2026.

The temple visit was a quiet affair — no cameras, no social media posts from his team. Whether that restraint was strategic or sincere, only Ranveer knows. But the image of one of Bollywood's biggest stars walking into a Karnataka temple because a court told him to is, at minimum, a reminder that stardom doesn't insulate you from accountability."""
    },

    # ─── Article 3: FWICE Ban Splitting Bollywood ───
    {
        "headline": "FWICE Issued a Non-Cooperation Directive Against Ranveer Singh. Now the Rest of Bollywood Has to Pick a Side.",
        "subheadline": "Manoj Bajpayee wants clarity. CINTAA's president says nobody called her. A Gangs of Wasseypur editor wants to know why workers' issues don't get this energy. And Rakhi Sawant dared them to ban Salman Khan.",
        "slug": "fwice-ranveer-singh-non-cooperation-ban-bollywood-divided-manoj-bajpayee-cintaa-nri-20260529",
        "image_person": "Manoj Bajpayee",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "image_caption": "Manoj Bajpayee called for clarity amid the FWICE non-cooperation directive against Ranveer Singh",
        "sources": [
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com"},
            {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"}
        ],
        "body": """The Federation of Western India Cine Employees doesn't technically have the power to "ban" anyone. What it can do is issue a Non-Cooperation Declaration — an NCD — which instructs its 32 member craft associations, covering everyone from camera operators to carpenters, not to work with a named individual. In practical terms, it means no crew will show up on your set.

FWICE issued one against Ranveer Singh. And now everyone in Bollywood has an opinion about it.

## The Origin

The NCD stems from Ranveer's exit from Don 3. Excel Entertainment — the production company run by Farhan Akhtar and Ritesh Sidhwani — claims pre-production losses of ₹40-45 crore after Ranveer walked away from the project. The details of why he left remain disputed: creative differences, scheduling conflicts, and contract terms have all been cited. What isn't disputed is the money. Excel wants it back, and FWICE decided to enforce.

The directive effectively freezes Ranveer's ability to start new productions in India. His upcoming films — including the ₹300 crore zombie thriller Pralay — will need the NCD resolved before cameras roll.

## The Industry Reacts

**Manoj Bajpayee** was among the first senior actors to speak publicly. The Governor star didn't take a side, but he made it clear the situation was untenable. "We don't have clarity," he said, noting that the NCD affects 30 different film crafts and creates uncertainty across productions. He urged a resolution, saying the longer this drags, the more it hurts everyone — workers especially.

**Poonam Dhillon**, president of the Cine and TV Artistes Association (CINTAA), was more pointed. She expressed "disappointment" that neither Ranveer nor FWICE had involved her organization in the dispute. "He could have approached us," she said, adding that CINTAA exists precisely to mediate actor-producer conflicts. She described the situation as "very strange" and urged Ranveer to honour his professional commitments.

**Shweta Venkat**, the editor of Gangs of Wasseypur, went further. She publicly criticised FWICE for what she called selective enforcement. Film editors, she said, have been raising concerns about delayed payments and poor working conditions for three years with no response. "Maybe we weren't cool enough," she wrote — a cutting observation that the federation moves fast when a superstar's money is involved but goes quiet when below-the-line workers need help.

And then there was **Rakhi Sawant**, who did what Rakhi Sawant does: she challenged FWICE to apply the same standard to Salman Khan. "Ban Salman Khan and show me," she said, alleging double standards in how the federation treats different stars. It was tabloid bait, but it echoed a real question about power dynamics in the industry.

## What the NCD Actually Means

An NCD is not a legal instrument. It doesn't have the force of a court order. But it has enormous practical power because FWICE's member associations represent the vast majority of below-the-line film workers in western India. If they refuse to work with an actor, that actor's productions stall.

For producers, it creates a chilling effect. Signing Ranveer for a film now means risking a crew walkout. For Ranveer's team, it means either resolving the financial dispute with Excel Entertainment or finding a way to get the NCD lifted through negotiation.

Reports indicate that Salman Khan personally intervened to broker talks between Ranveer and Farhan Akhtar. Ranveer's team reportedly offered ₹10 crore upfront and a ₹25 crore discount on future projects — a total concession of ₹35 crore. Excel rejected the offer.

## The Bigger Question for the Industry

The Ranveer-FWICE situation has surfaced a question the Hindi film industry has avoided for decades: who actually has power in Bollywood disputes?

FWICE's critics argue that the federation oversteps when it punishes individual actors for contract disputes that should be settled in civil court. Its supporters counter that without the NCD mechanism, producers have no leverage against stars who walk away from commitments — and the workers who already spent months in pre-production absorb the losses.

Shweta Venkat's complaint cuts deepest. If FWICE can mobilise within days when a producer loses ₹45 crore, why can't it mobilise when editors, assistants, and crew members wait months for payment? The answer — that big-money disputes get big-money attention — is one the federation hasn't addressed.

## What the Diaspora Is Watching

For NRIs following Bollywood, the FWICE-Ranveer dispute is a window into how the industry actually functions behind the trailer launches and PR-managed Instagram stories. It reveals a system where a handshake deal can cost someone ₹45 crore, where a federation of workers can effectively sideline a top-three star, and where the resolution depends not on courts but on phone calls between powerful men.

Ranveer Singh remains one of Indian cinema's most bankable actors. Dhurandhar 2 just crossed ₹1,000 crore. His next film has a ₹300 crore budget. But until the NCD lifts, none of that matters on a film set.

The dispute continues."""
    },
]

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Publishing {len(articles)} articles")
    print("=" * 60)

    success = 0
    for i, art in enumerate(articles, 1):
        print(f"\n{'─' * 40}")
        print(f"Article {i}/{len(articles)}: {art['headline'][:60]}...")
        
        # Validate article quality
        body_words = len(art["body"].split())
        headline_len = len(art["headline"])
        subheadline_len = len(art["subheadline"])
        
        print(f"  Body: {body_words} words | Headline: {headline_len} chars | Subheadline: {subheadline_len} chars")
        
        if body_words < 400:
            print(f"  ⚠ Body too short ({body_words} words), skipping")
            continue
        if headline_len > 200:
            print(f"  ⚠ Headline too long ({headline_len} chars), skipping")
            continue
        if subheadline_len < 15:
            print(f"  ⚠ Subheadline too short ({subheadline_len} chars), skipping")
            continue
        if len(art["sources"]) < 2:
            print(f"  ⚠ Too few sources ({len(art['sources'])}), skipping")
            continue
        
        result = publish_article(art)
        if result:
            success += 1
        
        time.sleep(1)  # Be gentle with APIs

    print(f"\n{'=' * 60}")
    print(f"Done: {success}/{len(articles)} articles published")
    print("=" * 60)
