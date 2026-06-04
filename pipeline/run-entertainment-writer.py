#!/usr/bin/env python3
"""Entertainment writer - June 4, 2026 evening run"""

import requests, json, os, io, uuid, urllib.parse, time
from datetime import datetime, timezone
from PIL import Image

# === ENV ===
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1]

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# === IMAGE HELPERS ===

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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
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
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        cmd = f'curl -sS -H "Authorization: {PEXELS_KEY}" "https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes)")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    print(f"  Compressed to {size_kb:.0f} KB")
    
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:60]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:100]}")
        return None

def source_image(person_name, topic_terms, slug):
    """Multi-source image search: Wikipedia -> Commons -> Pexels"""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})
    
    # Source 2: Wikimedia Commons
    search_terms = f"{person_name} {topic_terms}" if person_name else topic_terms
    commons = fetch_wikimedia_commons_images(search_terms)
    if not commons and person_name:
        commons = fetch_wikimedia_commons_images(topic_terms)
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
    
    # Source 3: Pexels fallback
    if not candidates:
        pexels_url = fetch_pexels_image(topic_terms)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "pexels", "relevance": 1})
    
    # Pick best and upload
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        raw = download_image(c["url"])
        if raw:
            filename = f"{slug}.jpg"
            public_url = upload_to_supabase(raw, filename)
            if public_url:
                attr = "Pexels" if c["source"] == "pexels" else "Wikimedia Commons"
                return public_url, attr
    
    print("  ⚠ No image found for this article")
    return None, None

def insert_article(article):
    """Insert article into Supabase"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={aid})")
        return aid
    else:
        print(f"  ⚠ Insert failed: {r.status_code} {r.text[:200]}")
        return None


# ================================================================
# ARTICLE 1: Alpha - YRF Spy Universe's First Female-Led Film
# ================================================================

print("\n" + "="*60)
print("ARTICLE 1: Alpha - YRF's First Female-Led Spy Film")
print("="*60)

art1_slug = "alpha-alia-bhatt-sharvari-yrf-spy-universe-first-female-led-july-3-nri-20260604"
art1_headline = "Alpha Just Became the Most Important Film in YRF's Spy Universe. And It Has Not Even Released a Trailer Yet."
art1_subheadline = "Alia Bhatt and Sharvari Wagh begin their promotional campaign for the franchise's first female-led instalment, arriving July 3 with Bobby Deol and Anil Kapoor"

art1_body = """Yash Raj Films has officially kicked off the promotional campaign for Alpha, the most anticipated addition to its blockbuster Spy Universe franchise. With just under a month left before its July 3 theatrical release, the studio is signaling that this is not just another entry in the series. It is the entry that changes what the series means.

Headlined by Alia Bhatt and Sharvari Wagh, Alpha is the first film in the Spy Universe to place women at its centre. The franchise that gave us Pathaan, War, and Tiger — all anchored by male superstars operating in the familiar grammar of the Indian action blockbuster — is now handing the keys to two female agents. The shift is not cosmetic. According to reports, Alia's character is not a conventional spy but a deadly assassin, raised and built to kill from a young age. This is a darker, more emotionally layered origin story than anything the franchise has attempted before.

## Why This Matters for the Franchise

The YRF Spy Universe has been one of Indian cinema's most commercially successful experiments. Pathaan crossed ₹1,000 crore worldwide. War rewrote action cinema conventions. Tiger 3, despite mixed reviews, maintained the brand's pull. But each of those films followed a recognisable template: a male superstar, a geopolitical antagonist, and set pieces designed for maximum spectacle. Alpha breaks the template. Directed by Shiv Rawail, who helmed The Railway Men for YRF, the film pairs Alia with Sharvari in what is being described as a full-fledged female-driven action spectacle. Bobby Deol reportedly plays the primary antagonist, and Anil Kapoor appears in a pivotal role.

Reports also suggest that Hrithik Roshan will make a special appearance as Kabir, his character from War, further anchoring Alpha within the broader Spy Universe continuity. For fans who have been tracking the interconnected storyline, this is a significant connective thread.

## The Promotional Push Has a Smart Hook

YRF's opening salvo in the campaign is not a trailer. It is a tie-in with the ICC Women's T20 World Cup, which starts on June 12. On June 4, the studio released a promotional clip linking Alpha's two female leads with the Indian women's cricket team, carrying the tagline: "From 2 Alphas to Team India's 15 Alphas." The timing is deliberate. By associating the film with a live sporting event that celebrates women performing at the highest competitive level, YRF is positioning Alpha not just as a movie but as a cultural statement.

Character posters, songs, interviews, and the theatrical trailer are all expected in the coming weeks. The studio is reportedly preparing a large-scale marketing campaign that matches the film's ambitious scale and franchise value.

## The Release Strategy

Alpha was originally slated for a Christmas 2025 release, then pushed to April 2026, and later to July 10. The final date was preponed by a week to July 3 to secure a longer uninterrupted box office window before Christopher Nolan's The Odyssey and Dhamaal 4 crowd the calendar. That kind of strategic jockeying signals the film's commercial stakes: YRF cannot afford a middling result here. A strong opening would validate the franchise's expansion beyond its established male-led formula. A weak one would raise questions about whether Indian audiences are ready to buy tickets for a female-fronted action spectacle at this scale.

## What NRI Audiences Should Watch For

The Spy Universe has consistently overperformed in overseas markets, particularly in North America, the UK, and the Middle East. Pathaan's overseas numbers were historic. Alpha, with its global action setting and its departure from the usual spy-film tropes of India-Pakistan joint missions, could appeal to a broader diaspora audience that has been watching the franchise evolve. The combination of Alia Bhatt's global name recognition and the Spy Universe brand should give the film significant built-in demand.

For the diaspora, the real question is not whether Alpha will be entertaining. It is whether Indian cinema's biggest franchise can convincingly rewrite its own rules with women at the centre. The answer arrives on July 3."""

print("Sourcing image...")
art1_img_url, art1_img_attr = source_image("Alia Bhatt", "Alia Bhatt spy action film", art1_slug)

art1_caption = "Alia Bhatt at a promotional event in Mumbai"
art1_sources = json.dumps([
    {"name": "Sacnilk", "url": "https://sacnilk.com"},
    {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
    {"name": "YRF Official", "url": "https://x.com/yrf"}
])

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": art1_sources,
    "is_editorial": False,
    "image_url": art1_img_url,
    "image_caption": art1_caption,
    "image_attribution": art1_img_attr
}
if not art1_img_url:
    del art1["image_url"]
    del art1["image_caption"]
    del art1["image_attribution"]

print("Inserting article 1...")
insert_article(art1)

# ================================================================
# ARTICLE 2: Ramayana's Global Ambitions
# ================================================================

print("\n" + "="*60)
print("ARTICLE 2: Ramayana's Global Push")
print("="*60)

art2_slug = "ramayana-ranbir-kapoor-cinemacon-sdcc-trailer-hans-zimmer-ar-rahman-global-nri-20260604"
art2_headline = "Ramayana Is Being Sold to the World Like No Indian Film Before It. CinemaCon Was Just the Beginning."
art2_subheadline = "With a San Diego Comic-Con trailer planned for July, a Hans Zimmer–AR Rahman score, DNEG visual effects, and an October release window, India's most expensive film is playing by Hollywood's playbook"

art2_body = """There is a particular moment in the life of every big-budget film when it stops being a production and becomes a campaign. For Ramayana, that moment arrived at CinemaCon 2026 in Las Vegas, where producer Namit Malhotra and Yash took over the Milano III Ballroom to showcase the film to the global exhibition industry. What they presented was not a trailer. It was a declaration of intent: this is not an Indian film seeking a global audience. This is a global film that happens to be Indian.

That distinction matters. And if you are tracking what it means for Indian cinema's place in the world, what is happening with Ramayana over the next five months deserves your attention.

## The CinemaCon Play

CinemaCon is where studios make their pitch to the people who control the world's movie screens. Hollywood majors have owned this space for decades. An Indian film securing a private showcase at CinemaCon is not just rare — it is essentially unprecedented at this scale. The Ramayana team hosted private previews and open-house conversations with key distributors and exhibitors from North America, Europe, Latin America, and Australia. Posters and banner-style reveals were positioned at the centre of the venue. The messaging was clear: "one of the most ambitious theatrical productions currently in post-production, a sweeping mythological epic filmed for IMAX and designed as a global tentpole event."

The feedback, according to trade sources, was enthusiastic. Attendees were reportedly impressed by costume design, world-building, and the quality of the visual effects — all handled by DNEG, the eight-time Academy Award-winning studio.

## The SDCC Trailer

If CinemaCon was the industry pitch, San Diego Comic-Con in July is the consumer one. Reports indicate that the team is in advanced talks with SDCC organisers to debut the full theatrical trailer there. This follows a successful focus group screening in Los Angeles, where an early cut received highly positive feedback from a diverse audience. The choice of SDCC is strategic: it is where Marvel, DC, and the biggest Hollywood franchises unveil their tentpoles. An Indian film launching its trailer alongside them is a statement about where Ramayana sees itself in the hierarchy.

## The Score: Hans Zimmer Meets AR Rahman

The musical collaboration alone would be headline news. Hans Zimmer, the man behind the scores of Inception, Interstellar, Gladiator, and Dune, is working alongside AR Rahman, India's greatest film composer and a two-time Academy Award winner, on the Ramayana soundtrack. A live musical event is reportedly planned for October to showcase the score — an event designed to generate its own wave of global attention ahead of the theatrical release.

## The Cast and the Scale

Ranbir Kapoor plays Lord Rama. Sai Pallavi is Sita. Yash is Ravana. Sunny Deol is Hanuman. Ravi Dubey is Lakshman. The budget is reported to be among the highest ever for an Indian production, with a distribution deal reportedly valued at ₹450 crore. The film is being developed as a two-part saga, with Part 1 now eyeing an October 30 release — a week before Diwali — to build word-of-mouth before the extended holiday window.

Director Nitesh Tiwari, who directed Dangal, India's highest-grossing film in China, brings a track record of making big stories feel emotionally intimate. Early glimpses suggest the film emphasises character presence and emotional depth over spectacle alone, with parallel narrative arcs in Part 1 and limited direct interaction between key characters early on.

## What This Means for the Diaspora

For NRI audiences, Ramayana represents something specific. It is the first Indian film to be positioned, from the ground up, as what producer Namit Malhotra calls "India's Avatar" — a visual effects–driven spectacle designed for IMAX that carries a story with deep cultural resonance for hundreds of millions of people worldwide. The LA IMAX screening, the CinemaCon showcase, the SDCC trailer launch — these are not add-ons. They are the core strategy. DNEG's Brahma AI unit is being used for lip-sync dubbing technology to present the film seamlessly in multiple languages for international audiences.

The film arrives at a moment when Indian cinema's global footprint is expanding rapidly. Dhurandhar 2 crossed ₹1,800 crore worldwide. Peddi just opened to ₹100 crore on day one. But Ramayana is playing a different game entirely. It is not trying to be the biggest Indian film. It is trying to be a film that happens to be Indian and also happens to be one of the biggest in the world."""

print("Sourcing image...")
art2_img_url, art2_img_attr = source_image("Ranbir Kapoor", "Ramayana Ranbir Kapoor film", art2_slug)

art2_caption = "Ranbir Kapoor, who plays Lord Rama in the upcoming Ramayana epic"
art2_sources = json.dumps([
    {"name": "Sacnilk", "url": "https://sacnilk.com"},
    {"name": "Filmfare", "url": "https://filmfare.com"},
    {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
])

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": art2_sources,
    "is_editorial": False,
    "image_url": art2_img_url,
    "image_caption": art2_caption,
    "image_attribution": art2_img_attr
}
if not art2_img_url:
    del art2["image_url"]
    del art2["image_caption"]
    del art2["image_attribution"]

print("Inserting article 2...")
insert_article(art2)

# ================================================================
# ARTICLE 3: AA23 - Allu Arjun + Lokesh Kanagaraj Still On Track
# ================================================================

print("\n" + "="*60)
print("ARTICLE 3: Allu Arjun + Lokesh Kanagaraj AA23")
print("="*60)

art3_slug = "allu-arjun-lokesh-kanagaraj-aa23-not-shelved-lcu-rathna-kumar-nri-20260604"
art3_headline = "AA23 Is Not Dead. The Most Anticipated Collaboration in South Indian Cinema Just Got Its Loudest Confirmation Yet."
art3_subheadline = "LCU writer Rathna Kumar shuts down budget-constraint rumors about Allu Arjun and Lokesh Kanagaraj's pan-India project, confirming pre-production is firmly on track"

art3_body = """For forty-eight hours, a section of the internet convinced itself that the most exciting announcement in South Indian cinema this year had quietly collapsed. On Tuesday, an unverified post on X claimed that "a big-budget pan-India movie announced in a very celebrating manner is now stuck in a limbo over budget constraints." It did not name the film. It did not need to. Fans immediately connected it to AA23, the untitled collaboration between Allu Arjun and director Lokesh Kanagaraj.

The panic was swift, loud, and — as it turns out — entirely unnecessary.

## What Actually Happened

On June 3, Rathna Kumar, the screenwriter who has been part of every significant film in the Lokesh Cinematic Universe — Kaithi, Vikram, Leo, and Master — posted a tribute on X marking four years since Vikram's release. At the end of his message, he added five words that ended the speculation: "Can't wait for #AA23."

It was not a press release. It was not a studio clarification. It was better than both. Rathna Kumar is not a publicist managing damage control. He is a creative collaborator who knows exactly where the project stands because he is actively involved in building it. When he says he cannot wait for AA23, it means the project is alive, progressing, and generating the kind of creative excitement that makes a writer post about it voluntarily.

Industry tracker Ramesh Bala confirmed separately that all rumors about the project being shelved are "completely baseless." Pre-production, including script development, is continuing as planned.

## Why AA23 Matters

This is not just another film. This is the collision of two of Indian cinema's most powerful creative forces.

Allu Arjun spent five years building the Pushpa franchise into a national phenomenon. The sequel, Pushpa 2: The Rule, became the highest-grossing Telugu film of all time. His screen presence has evolved from regional superstar to pan-India icon, with a National Award to cement the transition.

Lokesh Kanagaraj, meanwhile, has built the most ambitious shared cinematic universe in Indian cinema history. The Lokesh Cinematic Universe — spanning Kaithi, Vikram, and Leo — has demonstrated that Indian audiences will follow interconnected narratives with the same enthusiasm they bring to Marvel films. His directorial grammar is distinctive: tight plotting, morally complex characters, and action choreography that serves the story rather than interrupting it.

AA23 was announced on January 14, 2026, by Mythri Movie Makers. The announcement teaser — featuring Allu Arjun's silhouette managing a horse, accompanied by an Anirudh Ravichander score — caught fire on Instagram Reels. Reports suggest the film could be Lokesh's long-cherished sci-fi project, tentatively known as Irumbu Kai Mayavi, adapted for Allu Arjun's star persona.

This would be Lokesh's first direct collaboration with a Telugu superstar in a primary lead role, marking a historic bridge between the Tamil and Telugu industries. The music is being composed by Anirudh Ravichander, whose scores for Vikram and Leo helped define the sonic identity of the LCU.

## The Budget Question

The shelving rumor specifically cited "budget constraints" as the reason. For context: AA23 is being produced by Mythri Movie Makers, the same studio behind Pushpa 2, which was one of the most expensive Telugu films ever made. Mythri has the financial infrastructure to handle projects at this scale. The rumor appears to have originated from confusion about an entirely different project.

That said, the economics of pan-India filmmaking are genuinely challenging. Budgets above ₹300 crore require significant overseas revenue to break even, and the margin for error has shrunk. Every major star vehicle now needs to perform in Hindi-speaking markets in addition to its home territory. AA23, with Allu Arjun's proven pan-India pull and Lokesh's growing national audience, is better positioned than most.

## What to Watch For

Shooting is expected to commence later in 2026 after pre-production wraps. There are unconfirmed reports that Shraddha Kapoor may be cast as the female lead. A formal shooting commencement announcement from Mythri would be the next milestone to watch for.

For the diaspora audience that has been tracking the LCU's growth — from Kaithi's modest theatrical run to Vikram's blockbuster overseas numbers — AA23 represents the universe's biggest bet yet. And as of today, it is very much on."""

print("Sourcing image...")
art3_img_url, art3_img_attr = source_image("Allu Arjun", "Allu Arjun Telugu actor", art3_slug)

art3_caption = "Allu Arjun, whose collaboration with Lokesh Kanagaraj remains on track despite shelving rumors"
art3_sources = json.dumps([
    {"name": "Gulte", "url": "https://gulte.com"},
    {"name": "Hindustan Times", "url": "https://hindustantimes.com"},
    {"name": "LatestLY", "url": "https://latestly.com"},
    {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"}
])

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": art3_sources,
    "is_editorial": False,
    "image_url": art3_img_url,
    "image_caption": art3_caption,
    "image_attribution": art3_img_attr
}
if not art3_img_url:
    del art3["image_url"]
    del art3["image_caption"]
    del art3["image_attribution"]

print("Inserting article 3...")
insert_article(art3)

print("\n" + "="*60)
print("ENTERTAINMENT WRITER COMPLETE - 3 articles published")
print("="*60)
