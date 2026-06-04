#!/usr/bin/env python3
"""
Entertainment Writer — 2026-06-04 15:00 UTC run
Writes 3 articles:
1. Sambhavna Seth & Avinash Dwivedi welcome twins via surrogacy
2. Hai Jawani Toh Ishq Hona Hai preview + Vashu Bhagnani controversy 
3. Maa Behen Netflix reviews roundup
"""

import json, os, sys, uuid, subprocess, time, io, re
from datetime import datetime, timezone

# ---------- env ----------
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

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ---------- image helpers ----------
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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
    """Search Wikimedia Commons for CC-licensed images."""
    import urllib.parse
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(*queries):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    for q in queries:
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    result = buf.getvalue()
    print(f"  Compressed: {len(img_bytes)} -> {len(result)} bytes, {img.width}x{img.height}")
    return result


def upload_to_supabase_storage(img_bytes, filename, bucket="article-images"):
    """Upload image to Supabase storage bucket. Returns public URL."""
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or len(r.content) > 10000:
                print(f"  Downloaded {len(r.content)} bytes from {url[:60]}...")
                return r.content
        print(f"  ✗ Download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ✗ Download error: {e}")
    return None


def source_image(person_name=None, wiki_queries=None, pexels_queries=None, slug="article"):
    """Multi-source image pipeline. Returns (supabase_url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "priority": 1})
    
    # Source 2: Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons_images(q)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
            if results:
                break
    
    # Source 3: Pexels
    if pexels_queries:
        pexels_url = fetch_pexels_image(*pexels_queries)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "pexels", "priority": 3})
    
    # Pick best and upload
    candidates.sort(key=lambda x: x["priority"])
    
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:60]}...")
        img_bytes = download_image(c["url"])
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                sb_url = upload_to_supabase_storage(compressed, filename)
                if sb_url:
                    attribution = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return sb_url, attribution
    
    print("  ✗ No image found from any source")
    return None, None


# ---------- article insert ----------
def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id} — {article['headline'][:60]}")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ========== ARTICLE 1: Sambhavna Seth Twins ==========
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Sambhavna Seth & Avinash Dwivedi Welcome Twins")
    print("="*60)
    
    slug = "sambhavna-seth-avinash-dwivedi-twins-surrogacy-ivf-journey-nri-20260604"
    
    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr = source_image(
        person_name="Sambhavna Seth",
        wiki_queries=["Sambhavna Seth actress", "surrogacy India"],
        pexels_queries=["newborn twins hospital", "mother holding baby"]
    )
    
    headline = "Sambhavna Seth and Avinash Dwivedi Just Welcomed Twins Through Surrogacy. Their Ten-Year Journey to Get Here Is the Story."
    
    subheadline = "After seven failed IVF cycles and multiple miscarriages, the TV couple announced the arrival of a baby girl and a baby boy with a message that broke their followers: 'Lakshmi aur Ganesh dono ghar aa gaye.'"
    
    body = """After a decade of marriage, seven IVF cycles, and a pain that most people only discuss in whispers, television actress Sambhavna Seth and her husband Avinash Dwivedi are parents. On June 4, the couple announced the arrival of twins — a baby girl and a baby boy — via surrogacy.

The announcement came through a series of photographs posted on Instagram. In one image, Sambhavna is seen in tears, hands folded in prayer. In another, Avinash stands beside her, steadying her as the weight of the moment lands. The caption was simple and devastating in its restraint: "Maha Diwali came early this year. Lakshmi aur Ganesh dono ghar aa gaye. Our Hearts Are Full Of Gratitude. HAR HAR MAHADEV."

## A Journey Most People Don't Talk About

Sambhavna's fertility journey has been unusually public by Indian entertainment standards. She has spoken openly about the toll of repeated IVF failures — the hormone injections, the bloating, the hope that climbs with each cycle and crashes harder each time. She has described miscarriages on camera, not for sympathy, but because she believes silence around infertility causes more harm than the condition itself.

In April 2026, the couple formally announced their surrogacy decision. They shared a photograph holding a newspaper cutout that read: "Sam Avi's baby coming soon, breaking news, we're pregnant." The post was met with an outpouring from fans, many of whom had followed her journey for years through her YouTube channel, which has over 3.8 million subscribers.

## The Emotional First Moments

According to their vlog documenting the birth, the daughter arrived first, just a minute before her brother. In a moment captured on camera, Sambhavna turned to her husband and said, "Hamari family complete ho gayi, Avinash." The newborns were introduced to extended family in Delhi via video call — a scene familiar to any NRI family that has welcomed a child far from home.

The comments section filled quickly. Gauahar Khan wrote, "God bless u both and the babies always!!!" Debinna Bonnerjee, who has been vocal about her own fertility challenges, responded: "Oh wow wow. So happy to hear this." Rohit Purohit, Kishwer Merchant, and Urfi Javed all extended congratulations.

## Why This Matters Beyond Bollywood

Infertility affects roughly 15 percent of Indian couples, according to a 2023 Indian Council of Medical Research study. For Indian diaspora families, the conversation is often even harder — layered with cultural expectations around timelines, in-law pressures, and the specific isolation of navigating treatment in a foreign healthcare system without the support network of extended family.

Sambhavna's decision to document her journey from failed IVFs to surrogacy has created a rare reference point in Indian popular culture. While Bollywood celebrities like Shah Rukh Khan, Karan Johar, and Priyanka Chopra have become parents through surrogacy, few have discussed the process with the candor Sambhavna has brought to her YouTube channel. Her videos on IVF side effects, the emotional aftermath of miscarriages, and the logistics of surrogacy in India have collectively garnered millions of views.

## India's Surrogacy Landscape

India's Surrogacy (Regulation) Act, 2021, significantly changed the legal framework by banning commercial surrogacy and permitting only altruistic surrogacy. The law requires the surrogate to be a close relative, and the intended parents must be a married Indian couple. For NRIs, this has added complexity — many overseas Indian couples who once traveled to India for surrogacy now face tighter eligibility requirements and must navigate the law's specific provisions.

The Seth-Dwivedi case falls within the domestic framework, but it highlights a broader conversation that the diaspora is actively engaged in — one about fertility, family planning, and the cultural baggage that surrounds both.

## What Comes Next

Sambhavna, known for her stint on Bigg Boss, Khatron Ke Khiladi 4, and various Bhojpuri films, has built a second career as a content creator alongside Avinash. Their YouTube channel, Sambhavna Seth Entertainment, regularly features lifestyle and family content. The arrival of twins will likely bring a new chapter to their public documentation of domestic life — one that millions of followers have been waiting for.

For now, though, the couple appears to be doing what new parents do: holding their children and trying to believe it is real.

*Sources: Sambhavna Seth and Avinash Dwivedi on Instagram; Pinkvilla; Telly Chakkar; IANS; Zoom TV Entertainment*"""
    
    image_caption = "Sambhavna Seth, known for Bigg Boss and her popular YouTube channel"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr
    }
    
    return insert_article(article)


# ========== ARTICLE 2: Hai Jawani Toh Ishq Hona Hai ==========
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Hai Jawani Toh Ishq Hona Hai Preview")
    print("="*60)
    
    slug = "hai-jawani-toh-ishq-hona-hai-varun-dhawan-david-dhawan-vashu-bhagnani-controversy-nri-20260604"
    
    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr = source_image(
        person_name="Varun Dhawan",
        wiki_queries=["Varun Dhawan actor", "David Dhawan filmmaker"],
        pexels_queries=["Bollywood comedy film", "Indian cinema poster"]
    )
    
    headline = "Hai Jawani Toh Ishq Hona Hai Arrives June 12 With a Song Rights Lawsuit, CBFC Cuts, and a 50% Ticket Discount. Welcome to Bollywood in 2026."
    
    subheadline = "Varun Dhawan and David Dhawan's fourth collaboration has been battling Vashu Bhagnani in court, dodging a clash with Yash's Toxic, and offering half-price tickets on opening day. The film hasn't released yet, and it already has three storylines."
    
    body = """Varun Dhawan's next film, Hai Jawani Toh Ishq Hona Hai, arrives in theaters on June 12. But before a single ticket has been sold, the film has already generated more off-screen drama than most Bollywood releases manage across their entire run.

## The Vashu Bhagnani Song Rights Fight

The first controversy is legal. Producer Vashu Bhagnani filed a court petition claiming that two songs used in the film — 'Chunari Chunari' and 'Ishq Sona Hai' — belong to his 1999 production Biwi No. 1. Bhagnani argues that the makers of Hai Jawani Toh Ishq Hona Hai do not have the right to use these tracks.

Tips Films, which is producing the Varun Dhawan-starrer, has pushed back firmly, stating it holds all necessary music rights. The dispute has kept the film in headlines for weeks — a dynamic that trade analysts have noted with some cynicism. "I don't think it helps the film commercially," veteran trade analyst Taran Adarsh told Bollywood Hungama. "People may read, react, write about it and express their opinion. But eventually you need to spend money on the product."

Atul Mohan, another trade expert, offered a more pragmatic take: "Had this controversy not taken place, what would have been the discussion point for the film? At least, thanks to this controversy, the film is getting some media space and attention."

## The CBFC Wanted Changes

The Central Board of Film Certification cleared the film with a UA certificate — but not before requesting several modifications. According to reports, the CBFC asked the makers to replace an inappropriate word in four places, blur the name of a condom brand visible in one scene, edit a reference to a flavour, remove a scene with a questionable hand gesture, and zoom in on shots where actors' undergarments were visible.

For a David Dhawan comedy — a genre built on innuendo, physical comedy, and the occasional double entendre — these cuts are both expected and telling. The CBFC also reportedly asked the makers to visually edit shots featuring the names of English cricketers Ben Stokes and Jos Buttler, presumably because the names were used in a comedic context that could be seen as defamatory.

## The Release Date Musical Chairs

The film's path to June 12 has been anything but straightforward. Originally scheduled for May 22, it moved to June 5 after Yash's Toxic vacated its June 4 slot. But when Toxic subsequently moved back to June 4, Hai Jawani found itself in a direct clash with a pan-India blockbuster. The solution: another postponement, this time to June 12, giving the David Dhawan film a solo weekend.

"The change is intended to support industry solidarity and avoid unnecessary box office competition," Tips Films said in a statement. In practice, the move was about survival. Toxic, backed by KVN Productions and Monster Mind Creations, carries a budget exceeding ₹500 crore and is being positioned as a global cinematic event. A David Dhawan rom-com, however charming, would have been collateral damage.

## The 50% Discount Question

Adding another layer of intrigue, reports suggest the film will offer 50% discounted tickets on its opening day. The move has divided the trade. "You are undermining a star's potential," one trade expert told Bollywood Hungama, arguing that discount pricing on day one signals a lack of confidence. Others see it as smart counter-programming — a way to pull families into theaters during a crowded June slate that includes the Diljit Dosanjh-Imtiaz Ali collaboration Main Vaapas Aaunga and Kangana Ranaut's Bharat Bhhagya Viddhaata, both arriving the same day.

## What Is the Film Actually About?

Beneath the controversies lies a fairly straightforward David Dhawan comedy. The film stars Varun Dhawan alongside Mrunal Thakur and Pooja Hegde, with a supporting cast that includes Maniesh Paul, Mouni Roy, Jimmy Sheirgill, Kubbra Sait, and Rakesh Bedi. The poster shows Varun in a characteristically chaotic pose atop twin baby strollers, flanked by his two leading ladies — a visual shorthand for the kind of comedy of errors that the elder Dhawan has been delivering since the 1990s.

This marks the fourth father-son collaboration between David and Varun Dhawan, following Main Tera Hero (2014), Judwaa 2 (2017), and Coolie No. 1 (2020). Their track record is commercially reliable if critically mixed, and the brand of humor they traffic in — broad, family-friendly, and unapologetically slapstick — still finds an audience in India and across the diaspora.

## The NRI Box Office Factor

For NRI audiences, the June calendar presents an unusual concentration of options. Peddi (Ram Charan) opened today, Cocktail 2 (Shahid Kapoor, Kriti Sanon, Rashmika Mandanna) arrives June 19, and Welcome To The Jungle (Akshay Kumar) follows June 26. Hai Jawani Toh Ishq Hona Hai, with its Rs. 150 crore reported budget, needs strong overseas numbers to justify its investment. The 50% discount strategy may play differently in North American and UK multiplexes, where Indian film ticket prices are already premium.

Whether the controversies translate to curiosity or fatigue will become clear on June 12. Until then, the film continues to demonstrate a truth about modern Bollywood: the marketing begins long before the trailer drops, and sometimes the best publicity is a well-timed lawsuit.

*Sources: Bollywood Hungama; Sacnilk; Hauterrfly; Pinkvilla*"""
    
    image_caption = "Varun Dhawan at a promotional event in Mumbai"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr
    }
    
    return insert_article(article)


# ========== ARTICLE 3: Maa Behen Reviews ==========
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Maa Behen Netflix Reviews Roundup")
    print("="*60)
    
    slug = "maa-behen-netflix-reviews-madhuri-dixit-triptii-dimri-ratings-audience-reaction-nri-20260604"
    
    # Image sourcing
    print("\nSourcing image...")
    img_url, img_attr = source_image(
        person_name="Madhuri Dixit",
        wiki_queries=["Madhuri Dixit actress", "Triptii Dimri actress"],
        pexels_queries=["Indian women dark comedy", "Netflix India"]
    )
    
    headline = "The Reviews Are In for Maa Behen. Madhuri Dixit Is Spectacular. The Film Around Her Is Another Story."
    
    subheadline = "Netflix's Bihari dark comedy about a mother and two daughters hiding a body has split critics and audiences down the middle. The consensus: the performances are extraordinary, the screenplay loses its nerve in the second half."
    
    body = """Maa Behen dropped on Netflix today, and within hours, the internet had already fractured into two camps: those who think Suresh Triveni has delivered one of Netflix India's best Hindi films, and those who think it is a promising premise that collapses under the weight of its own second half. Both sides agree on one thing: Madhuri Dixit is phenomenal.

## What the Critics Say

The reviews are genuinely split. India Forums gave it 3.5 out of 5, calling it a film that "pulls you into its messy little world and refuses to let go" and praising it for using "chaos, humour and dysfunctional family dynamics to tell a story about women who have spent their lives being judged, labelled and underestimated." The review noted that it "never turns preachy" — high praise for a film with social commentary embedded in its DNA.

Pinkvilla was less generous at 2.5 out of 5, calling it a "slow-burning mystery" saved by its cast. Planet 9 Productions gave it 3.5 out of 5, describing it with the headline "Daayan nahi, devi hai" — a sharp summary of the film's central argument. MensXP landed at 3 out of 5, calling it "a decent entertainer with an outstanding Madhuri Dixit and Triptii Dimri leading the pack."

The pattern across reviews is consistent: strong first half, weaker second. "The first half comprises of the build up and some really good comic scenes which will make you laugh out loud," one X reviewer wrote. "But the second hour is where the screenplay and the film falters."

## The Performances

Every review, including the negative ones, singles out the three leading women.

Madhuri Dixit plays Rekha, a non-conforming widow in Bihar who works at a wine shop and wears sleeveless blouses — choices that make her neighbors' blood boil. MensXP noted that this is "a strong comeback after the atrocity that was her web series Mrs Deshpande" and added that "she proves why she was once the top star and deserves to be seen more on our screens." This is her first Bihari character, and multiple critics have remarked on how fully she commits to the dialect and mannerisms.

Triptii Dimri plays Jaya, one of Rekha's daughters. After a string of commercially successful but critically middling roles, this film appears to have given her the material she needed. India Forums called her work "a masterclass," and MensXP described her as "terrific."

But the breakout is Dharna Durga, a digital creator making her film debut as Sushma, the younger daughter. Multiple critics have called her "the heart of Maa Behen" and the one who "proves she is here to stay." Planet 9 described her as a "firebrand," and MensXP noted she "manages to stand her own against a stalwart like Madhuri Dixit and a veteran like Ravi Kishan."

Ravi Kishan, playing the dead neighbor Gupta ji, gets limited scope in the first hour but makes the most of his time in the second half.

## What the Film Is Actually About

On paper, the premise is simple: a dead body, three women, and the need to make it disappear before the neighbors find out. A man — Gupta ji, the neighborhood's self-appointed moral authority — dies in Rekha's house one night. Her daughters rush home, and the three begin an increasingly chaotic cover-up.

But the film uses this setup to do something more ambitious. It interrogates how a conservative society views a household of women without a male protector — the specific kind of suspicion, policing, and moral judgment that falls on women who live outside traditional structures. The title itself is a double-edged reference: 'maa-behen' is both a description of the family unit and a well-known Hindi expletive, often deployed as a threat. Director Suresh Triveni, who made Tumhari Sulu and Jalsa, has built his career on exactly this kind of social commentary wrapped in accessible packaging.

## The Audience Verdict

Social media reactions have been just as divided as the critics. "I just finished #maabehen it was really a great well-written movie I enjoyed every single scene," one viewer wrote. Another was less kind: "SNOOZEFEST. Good intentions. Good performances. Bad screenplay. The writing should get some MAA BEHEN gali."

A more thoughtful take emerged from viewers responding to the film's gender politics: "It's so refreshing to see a film openly address that specific kind of social policing. Women who choose their own path shouldn't have to fight a baseline of suspicion from society."

## Should NRIs Watch It?

For diaspora audiences, Maa Behen offers a few things that are genuinely rare in Hindi streaming content. First, it is set in Bihar and treats the setting with visual richness rather than the dull, poverty-coded palette that Hindi cinema typically reserves for the state. Second, its three female leads are given agency, complexity, and humor without being reduced to archetypes. Third, at roughly two hours, it respects your time — a virtue in an era of bloated three-hour streaming films.

The catch is the second half. If you can tolerate a screenplay that builds brilliantly and then loses some altitude, the performances alone justify the watch. If you need a tight, cohesive thriller from start to finish, you may find yourself reaching for your phone around the 75-minute mark.

Maa Behen is streaming now on Netflix worldwide.

*Sources: Pinkvilla; India Forums; MensXP; Planet 9 Productions; Livemint; TechnoSports*"""
    
    image_caption = "Madhuri Dixit at a film premiere in Mumbai"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr
    }
    
    return insert_article(article)


# ========== MAIN ==========
if __name__ == "__main__":
    print("Entertainment Writer — 2026-06-04 15:00 UTC")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")
    print(f"Pexels key: {'set' if PEXELS_KEY else 'MISSING'}")
    
    results = []
    
    art1_id = write_article_1()
    results.append(("Sambhavna Seth Twins", art1_id))
    
    art2_id = write_article_2()
    results.append(("Hai Jawani Preview", art2_id))
    
    art3_id = write_article_3()
    results.append(("Maa Behen Reviews", art3_id))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {name}: {aid}")
    
    success = sum(1 for _, aid in results if aid)
    print(f"\n{success}/3 articles published successfully")
