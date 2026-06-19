#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (14:30 UTC run)
2 NEW articles for the "news" / "nri-world" categories:
  1. India's Hormuz oil lifeline reopens but the US-Iran peace wobbles (geopolitics)
  2. Indian diaspora pushes for a $14M India Heritage Center museum in Washington DC (nri-world)
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

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

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: Hormuz reopening / fragile US-Iran peace ─────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Hormuz oil lifeline reopens but peace wobbles")
    print("="*60)

    slug = "india-strait-of-hormuz-reopens-oil-lifeline-fragile-us-iran-peace-20260619"
    headline = "India's Oil Lifeline Through Hormuz Is Reopening. The Peace Holding It Open Just Wobbled."
    subheadline = "Tankers are moving through the Strait of Hormuz again after the US-Iran ceasefire, and an Indian-flagged ship is finally sailing home. But Friday's signing ceremony in Switzerland was scrapped, Iran is threatening transit fees, and roughly half of India's crude still rides on a 60-day truce."

    body = """For three months, the narrowest stretch of water that matters to India sat closed. The Strait of Hormuz — the chokepoint through which roughly half of India's crude imports and a vast share of its container trade pass — was effectively shut by the war between the United States and Iran, with ship crossings down more than 95 percent at the peak of the conflict. This week, it began to reopen. And almost as quickly, the peace that reopened it showed how fragile it still is.

The mechanics of the thaw are real and visible. After Washington and Tehran signed an interim agreement on Wednesday and the United States lifted its naval blockade on Thursday, traffic returned to the strait. At least four tankers carrying crude, oil products and liquefied petroleum gas entered Hormuz on Friday bound for Iraqi Gulf ports, according to ship-tracking data. There were 25 commercial crossings on June 18 — the highest single-day count in two months and more than five times the daily average of early June, though still far below the pre-war norm of about 120. Vessels that had spent weeks running dark, transponders switched off to hide their movements, began broadcasting their positions again.

## An Indian Ship Heads Home

For India, one detail captured the moment better than any statistic. The Indian-flagged tanker Desh Vaibhav, stranded by days of disruption, was preparing to sail for India as the strait reopened. It is the kind of small, concrete reversal that ripples outward: every cargo that moves again is freight cost that stops climbing, an insurance premium that stops bleeding, a refinery run that can be planned rather than improvised.

India's exporters were quick to cheer. The Federation of Indian Export Organisations said normalisation would "slash" the exorbitant freight fees and prohibitive war-risk insurance premiums that had crushed shippers, restoring "smoother, faster, and remarkably cheaper" transit to West Asia and Europe. Lower fuel prices, the body added, would soften input costs for crude-dependent sectors such as plastics, paints and chemicals. Indian refiners, who had scrambled to buy spot cargoes from as far away as Latin America during the closure, are now preparing to scale those purchases back and lift full committed volumes from Gulf suppliers once flows through the waterway steady.

The price signal has been dramatic. Brent crude, which spiked above $114 a barrel during the war, has fallen below $80 — down nearly 40 percent from its peak — easing the import bill of the world's third-largest oil consumer and taking pressure off the rupee, which had been battered toward record lows.

## Why the Calm Is Not Yet Secure

But the deal that delivered all this is a 60-day memorandum of understanding, not a settlement. On Friday, the planned signing ceremony in Switzerland — meant to bring US Vice President JD Vance and Iran's lead negotiator together to formalise the framework — was scrapped after fighting flared in Lebanon, where Israel and Hezbollah traded fire before agreeing to a ceasefire later in the day. Crude prices ticked up on the news, a reminder of how quickly the calculus can turn.

Two unresolved questions hang over the strait. The first is whether Iran will keep passage free. Iranian media has signalled that ships may transit without charge for only two months, after which Tehran could impose navigation fees to cover the cost of "managing" the waterway — a toll the United States, Europe and the Gulf states reject as illegitimate on what they consider international waters. The second is durability: President Trump has warned he could resume attacks if Iran does not honour its commitments, and the US Navy cautioned mariners that mines remain in the strait as clearance operations continue. Shipping and oil executives say it will take months, if not longer, for volumes to return to normal.

## Why It Matters for the Diaspora

For the diaspora, Hormuz is not an abstraction — it is the artery that connects two of its worlds. The Gulf is home to nearly half of India's overseas migrants and the source of a large share of the record remittances that flow back home. Many of those workers are seafarers, refinery hands and logistics staff whose livelihoods depend directly on the strait staying open and safe. A reopened waterway means steadier jobs, cheaper goods on Indian shelves and a calmer rupee for everyone wiring money home from Dubai, London or New Jersey.

It also means exposure. NRI investors hold the Indian energy and shipping stocks that move with every headline out of the Gulf, and the broader equity story the diaspora has been courted to buy into rises and falls with the oil import bill. The lesson Gulf producers are drawing from the war — that overreliance on a single chokepoint is no longer tenable — will reshape trade routes for years, and India, perched at the mouth of the Indian Ocean, sits squarely in that redrawing.

For now, the ships are moving and the price of oil is down. But the peace that made it possible is 60 days old, and on its fourth day it already flinched. India is breathing easier through Hormuz — with one eye fixed firmly on the next headline."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An oil tanker transits the Strait of Hormuz, the chokepoint through which roughly half of India's crude imports pass"
    img_attribution = "Wikimedia Commons"

    for q in ["Strait of Hormuz oil tanker", "oil tanker Persian Gulf", "crude oil tanker ship", "Strait of Hormuz"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "tanker" in t or "ship" in t:
                img_caption = "An oil tanker at sea; tankers resumed transiting the Strait of Hormuz this week after the US-Iran ceasefire"
            break

    if not img_url:
        px = fetch_pexels_image("oil tanker ship sea")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Oil shipments rise in Hormuz although questions grow over Iran's transit terms (June 19, 2026)",
            "The Hindu BusinessLine \u2014 US-Iran peace deal to ease disruptions for Indian exporters (FIEO reaction)",
            "Reuters \u2014 India's May oil supply from UAE tops pre-war levels as imports rise; refiners to scale back spot purchases once Hormuz reopens",
            "Reuters \u2014 Lebanon ceasefire agreed after US-Iran talks in Switzerland scrapped (June 19, 2026)"
        ]),
        "diaspora_angle": "Roughly half of India's crude and a huge share of its trade ride through the Strait of Hormuz, where nearly half its overseas migrants and seafarers work \u2014 so the strait reopening means steadier Gulf jobs, cheaper goods and a calmer rupee, while the 60-day truce's fragility keeps diaspora-held energy and shipping stocks on edge.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India Heritage Center museum in Washington DC ────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India Heritage Center museum push in DC")
    print("="*60)

    slug = "india-heritage-center-museum-washington-dc-diaspora-campaign-20260619"
    headline = "The Diaspora Wants to Build India's Story a Permanent Home in Washington. It Will Cost $14 Million."
    subheadline = "After eight years of quiet research, the team behind the India Heritage Center is launching an aggressive campaign for a 20,000-square-foot museum in the US capital \u2014 ten galleries tracing 11,000 years of civilisation, aimed as much at mainstream America as at the next generation of Indian-Americans."

    body = """For all the influence the Indian-American community now wields \u2014 in boardrooms, hospitals, universities and Congress \u2014 there is no permanent institution in the United States dedicated to telling India's civilisational story in full. A group of diaspora leaders wants to change that, and after nearly eight years of research and planning, they are finally going public with the ask.

The India Heritage Center, a registered 501(c)(3) non-profit, is preparing to launch an ambitious campaign to build what its organisers describe as the first museum in the United States devoted to India's cultural, historical and civilisational journey \u2014 a span the team traces back more than 11,000 years, to roughly 9,500 BC. The proposed home is deliberate: Washington, DC, in "the natural footfall" of the millions who visit the capital's museums each year.

## What They Are Building

The vision is concrete. Organisers envision a 20,000-square-foot complex with ten galleries, a 350-seat auditorium, a library, reception facilities and a gift centre. Rather than glass cases and placards, the plan leans heavily on immersive technology \u2014 virtual reality, augmented reality, interactive audio-video systems, murals and artefacts \u2014 to walk visitors through India's past, present and future.

The ten galleries would guide visitors from the Indus Valley civilisation and Vedic traditions through India's scientific and technological achievements, its spiritual heritage of yoga and Ayurveda, its cultural accomplishments, its periods of adversity, and its emergence as a modern democratic nation. The arc, organisers say, is meant to present the story whole rather than in the fragments by which it is usually told.

"Indian history and Indian civilization has never been portrayed in the strength that it deserves," said Dr Amitabh Sharma, the Atlanta-based educationist and community leader leading the project, in remarks to news agency IANS. "It is important in today's perspective, more importantly, to be able to tell the world that this is the rich civilization, rich heritage that we have."

## Built for Two Audiences

What distinguishes the pitch is who it is for. Sharma is explicit that the centre is aimed not only at the diaspora and its children \u2014 many of whom, he argues, are "totally oblivious" to the actual facts of their heritage \u2014 but at mainstream Americans and other ethnic communities with little exposure to India's long history.

He frames the institution around a particular message: India's traditions of inclusiveness and coexistence. "We want to tell the world, listen, we have embraced persecuted communities," Sharma said. "This is a community or a civilization that will always cherish peace and coexistence." It is a self-consciously soft-power argument, pitched at a moment when the community is increasingly focused on preserving cultural identity and educating younger generations.

Sharma is also careful about credibility. He said the team spent years collating and validating an enormous body of historical material precisely "so that tomorrow nobody can raise a finger or raise an objection" \u2014 an acknowledgement that any institution claiming to narrate 11,000 years of history will face scrutiny over what it includes and how.

## The Hard Part: Money

The estimated cost is $12 million to $14 million, and the fundraising plan is broad: high-net-worth individuals, corporate sponsorships, grants, crowdfunding and community support, with naming opportunities for galleries and facilities on offer. The organisation has begun an "aggressive, interactive campaign" to identify a suitable site in the capital.

Sharma is pitching it as a collective undertaking rather than a personal one. "This is not my project. It is not your project. It is the entire Indian community's project," he said, adding that the early response has been encouraging. "When I reach out to people, people say, yeah, why wasn't it done earlier? People are joining in."

## Why It Matters for the Diaspora

For a community that has spent a generation succeeding in America, the museum touches a quieter anxiety: that material success has outpaced cultural memory, and that the second and third generations are growing up with only a hazy, second-hand sense of where they come from. A permanent institution in Washington would be a statement that the Indian-American story has earned a fixed place in the national landscape \u2014 alongside the Smithsonian's museums of African American and American Indian history \u2014 rather than living only in temple basements and festival weekends.

It is also a test of the diaspora's capacity to fund its own cultural ambitions. The Indiaspora community has been described as the world's largest and one of its wealthiest, with an estimated annual income in the hundreds of billions of dollars; a $14 million museum is, in that context, eminently within reach if the will materialises. Whether the India Heritage Center rises on the National Mall's periphery or stalls in the long grind of capital fundraising will say something about how the diaspora chooses to invest in its own story \u2014 not just its bank accounts.

For now, the blueprint exists, the non-profit is registered, and the search for a Washington address has begun. The rest is up to a community being asked, in effect, to put its heritage where its home is."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "The National Mall in Washington, DC, where organisers hope to site the proposed India Heritage Center museum"
    img_attribution = "Wikimedia Commons"

    for q in ["Smithsonian museum Washington DC building", "National Mall Washington DC museums", "Indian civilization museum exhibit", "Washington DC museum"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "mall" in t:
                img_caption = "The National Mall in Washington, DC; organisers want the India Heritage Center in the capital's museum corridor"
            elif "smithsonian" in t or "museum" in t:
                img_caption = "A museum in Washington, DC; the proposed India Heritage Center would join the capital's cultural institutions"
            break

    if not img_url:
        px = fetch_pexels_image("museum gallery interior exhibit")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A museum gallery interior"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Andhra Headlines / IANS \u2014 Indian diaspora pushes for landmark museum in DC (Dr Amitabh Sharma interview)",
            "India Heritage Center \u2014 project documents and 501(c)(3) non-profit filing ($12\u201314 million cost estimate)",
            "Indiaspora \u2014 'India and its Diaspora: Partners in Progress' report on diaspora scale and philanthropy"
        ]),
        "diaspora_angle": "A proposed $14 million India Heritage Center in Washington would give the Indian-American story its first permanent civilisational museum in the US \u2014 a test of whether a community that has succeeded materially will fund its own cultural memory for the next generation.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
