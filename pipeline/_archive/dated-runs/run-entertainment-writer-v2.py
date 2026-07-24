#!/usr/bin/env python3
"""Entertainment writer - June 4, 2026 evening run (fixed)"""

import requests, json, os, io, uuid, urllib.parse, time, subprocess
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
            headers={"User-Agent": UA}, timeout=15
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
    """Download image via curl for maximum reliability"""
    try:
        tmp_path = f"/tmp/img_download_{uuid.uuid4().hex[:8]}.tmp"
        cmd = f'curl -sS -L -o "{tmp_path}" -H "User-Agent: {UA}" --max-time 20 -w "%{{http_code}} %{{size_download}}" "{url}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
        parts = result.stdout.strip().split()
        if len(parts) >= 2:
            status_code = parts[0]
            size = int(parts[1])
            if status_code == "200" and size > 5000:
                with open(tmp_path, "rb") as f:
                    data = f.read()
                os.remove(tmp_path)
                print(f"  Downloaded {len(data)} bytes")
                return data
            else:
                print(f"  ⚠ Download: status={status_code}, size={size}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
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
        print(f"  ✓ Uploaded: {filename}")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:100]}")
        return None

def source_image(person_name, topic_terms, slug):
    candidates = []
    
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})
    
    search_terms = f"{person_name} {topic_terms}" if person_name else topic_terms
    commons = fetch_wikimedia_commons_images(search_terms)
    if not commons and person_name:
        commons = fetch_wikimedia_commons_images(topic_terms)
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
    
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        raw = download_image(c["url"])
        if raw:
            filename = f"{slug}.jpg"
            public_url = upload_to_supabase(raw, filename)
            if public_url:
                attr = "Pexels" if c["source"] == "pexels" else "Wikimedia Commons"
                return public_url, attr
    
    print("  ⚠ No usable image found")
    return None, None

def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ PUBLISHED: {article['slug']}")
        return aid
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ================================================================
# ARTICLES
# ================================================================

now_iso = datetime.now(timezone.utc).isoformat()

articles = [
    {
        "slug": "alpha-alia-bhatt-sharvari-yrf-spy-universe-first-female-led-july-3-nri-20260604",
        "headline": "Alpha Just Became the Most Important Film in YRF's Spy Universe. And It Has Not Even Released a Trailer Yet.",
        "subheadline": "Alia Bhatt and Sharvari Wagh begin their promotional campaign for the franchise's first female-led instalment, arriving July 3 with Bobby Deol and Anil Kapoor",
        "person": "Alia Bhatt",
        "topic": "Alia Bhatt spy action film",
        "caption": "Alia Bhatt at the 2026 Cannes Film Festival",
        "body": """Yash Raj Films has officially kicked off the promotional campaign for Alpha, the most anticipated addition to its blockbuster Spy Universe franchise. With just under a month left before its July 3 theatrical release, the studio is signaling that this is not just another entry in the series. It is the entry that changes what the series means.

Headlined by Alia Bhatt and Sharvari Wagh, Alpha is the first film in the Spy Universe to place women at its centre. The franchise that gave us Pathaan, War, and Tiger — all anchored by male superstars operating in the familiar grammar of the Indian action blockbuster — is now handing the keys to two female agents. The shift is not cosmetic. According to reports, Alia's character is not a conventional spy but a deadly assassin, raised and built to kill from a young age. This is a darker, more emotionally layered origin story than anything the franchise has attempted before.

## Why This Matters for the Franchise

The YRF Spy Universe has been one of Indian cinema's most commercially successful experiments. Pathaan crossed ₹1,000 crore worldwide. War rewrote action cinema conventions. Tiger 3, despite mixed reviews, maintained the brand's pull. But each of those films followed a recognisable template: a male superstar, a geopolitical antagonist, and set pieces designed for maximum spectacle.

Alpha breaks the template. Directed by Shiv Rawail, who helmed The Railway Men for YRF, the film pairs Alia with Sharvari in what is being described as a full-fledged female-driven action spectacle. Bobby Deol reportedly plays the primary antagonist, and Anil Kapoor appears in a pivotal role. Reports also suggest that Hrithik Roshan will make a special appearance as Kabir, his character from War, further anchoring Alpha within the broader Spy Universe continuity.

## The Promotional Push Has a Smart Hook

YRF's opening move in the campaign is not a trailer. It is a tie-in with the ICC Women's T20 World Cup, which starts on June 12. On June 4, the studio released a promotional clip linking Alpha's two female leads with the Indian women's cricket team, carrying the tagline: "From 2 Alphas to Team India's 15 Alphas." By associating the film with a live sporting event that celebrates women performing at the highest competitive level, YRF is positioning Alpha not just as a movie but as a cultural statement about what Indian women can do when they are given the lead.

Character posters, songs, interviews, and the theatrical trailer are all expected in the coming weeks. The studio is reportedly preparing a large-scale marketing campaign to match the film's ambitious scale and franchise value.

## The Release Strategy

Alpha was originally slated for a Christmas 2025 release, then pushed to April 2026, and later to July 10. The final date was preponed by a week to July 3 to secure a longer uninterrupted box office window before Christopher Nolan's The Odyssey and Dhamaal 4 crowd the calendar. That kind of strategic jockeying signals how seriously YRF is taking this release. A strong opening would validate the franchise's expansion beyond its established male-led formula. A weak one would raise questions about whether Indian audiences will buy tickets for a female-fronted action spectacle at this scale.

## What NRI Audiences Should Watch For

The Spy Universe has consistently overperformed in overseas markets, particularly in North America, the UK, and the Middle East. Pathaan's overseas numbers were historic. Alpha, with its global action setting and departure from the usual spy-film tropes of India-Pakistan joint missions, could appeal to a broader diaspora audience that has been watching the franchise evolve. The combination of Alia Bhatt's global name recognition and the Spy Universe brand should give the film significant built-in demand in markets where Indian films increasingly compete for premium screen time.

For the diaspora, the real question is not whether Alpha will be entertaining. It is whether Indian cinema's biggest franchise can convincingly rewrite its own rules with women at the centre. The answer arrives on July 3.""",
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "YRF Official", "url": "https://x.com/yrf"}
        ])
    },
    {
        "slug": "ramayana-ranbir-kapoor-cinemacon-sdcc-trailer-hans-zimmer-ar-rahman-global-nri-20260604",
        "headline": "Ramayana Is Being Sold to the World Like No Indian Film Before It. CinemaCon Was Just the Beginning.",
        "subheadline": "With a San Diego Comic-Con trailer debut planned for July, a Hans Zimmer-AR Rahman score, and an October release, India's most expensive film is playing by Hollywood's playbook",
        "person": "Ranbir Kapoor",
        "topic": "Ramayana Indian epic film 2026",
        "caption": "Ranbir Kapoor, who plays Lord Rama in the upcoming Ramayana epic",
        "body": """There is a particular moment in the life of every big-budget film when it stops being a production and becomes a campaign. For Ramayana, that moment arrived at CinemaCon 2026 in Las Vegas, where producer Namit Malhotra and Yash took over the Milano III Ballroom to showcase the film to the global exhibition industry. What they presented was not a trailer. It was a declaration of intent: this is not an Indian film seeking a global audience. This is a global film that happens to be Indian.

That distinction matters. And if you are tracking what it means for Indian cinema's place in the world, what is happening with Ramayana over the next five months deserves close attention.

## The CinemaCon Play

CinemaCon is where studios make their pitch to the people who control the world's movie screens. Hollywood majors have owned this space for decades. An Indian film securing a private showcase at CinemaCon is not just rare — it is essentially unprecedented at this scale. The Ramayana team hosted private previews and open-house conversations with key distributors and exhibitors from North America, Europe, Latin America, and Australia. Posters and banner-style reveals were positioned at the centre of the venue, describing the film as "a sweeping mythological epic filmed for IMAX and designed as a global tentpole event."

The feedback, according to trade sources, was enthusiastic. Attendees were reportedly impressed by costume design, world-building, and the quality of the visual effects — all handled by DNEG, the eight-time Academy Award-winning studio that has worked on Inception, Interstellar, and Dune.

## The SDCC Trailer

If CinemaCon was the industry pitch, San Diego Comic-Con in July is the consumer one. Reports from Mid-day indicate that the team is in advanced talks with SDCC organisers to debut the full theatrical trailer. This follows a successful focus group screening in Los Angeles, where an early cut received highly positive feedback from a diverse audience. The choice of SDCC is strategic and unprecedented for an Indian production: it is where Marvel, DC, and the biggest Hollywood franchises unveil their tentpoles. Launching an Indian film's trailer alongside them is a statement about where Ramayana sees itself in the global hierarchy.

## The Score: Hans Zimmer Meets AR Rahman

The musical collaboration alone would be headline news in any other year. Hans Zimmer — the man behind the scores of Inception, Interstellar, Gladiator, and Dune — is working alongside AR Rahman, India's greatest film composer and a two-time Academy Award winner, on the Ramayana soundtrack. A live musical event is reportedly planned for October to showcase the score, designed to generate its own wave of global attention ahead of the theatrical release.

## The Cast and the Scale

Ranbir Kapoor plays Lord Rama. Sai Pallavi is Sita. Yash is Ravana. Sunny Deol is Hanuman. Ravi Dubey is Lakshman. The budget is among the highest ever for an Indian production, with a distribution deal reportedly valued at ₹450 crore. The film is being developed as a two-part saga, with Part 1 now eyeing an October 30 release — a week before Diwali — to build strong word-of-mouth before the extended holiday window.

Director Nitesh Tiwari, who directed Dangal (India's highest-grossing film in China), brings a track record of making big stories feel emotionally intimate. Early glimpses suggest the film emphasises character presence and emotional depth over spectacle alone, with Yash revealing that Part 1 may explore parallel arcs with limited direct interaction between key characters early on.

## What This Means for the Diaspora

For NRI audiences, Ramayana represents something specific and personal. It is the first Indian film positioned, from the ground up, as what Namit Malhotra calls "India's Avatar" — a visual effects-driven spectacle designed for IMAX that carries a story with deep cultural resonance for hundreds of millions of people worldwide. The Ramayana is not just mythology for the diaspora; it is childhood, it is family, it is identity. Seeing it presented at the same scale and with the same technical ambition as Hollywood's biggest franchises is unprecedented.

DNEG's Brahma AI unit is developing lip-sync dubbing technology to present the film seamlessly in multiple languages for international audiences. The LA IMAX screening, the CinemaCon showcase, the planned SDCC trailer launch — these are not add-ons to the domestic release strategy. They are the core strategy.

The film arrives at a moment when Indian cinema's global footprint is expanding rapidly. Dhurandhar 2 crossed ₹1,800 crore worldwide. But Ramayana is playing a different game entirely. It is not trying to be the biggest Indian film. It is trying to be a film that happens to be Indian and also happens to be one of the biggest in the world.""",
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Filmfare", "url": "https://filmfare.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "Mid-day", "url": "https://mid-day.com"}
        ])
    },
    {
        "slug": "allu-arjun-lokesh-kanagaraj-aa23-not-shelved-lcu-rathna-kumar-nri-20260604",
        "headline": "AA23 Is Not Dead. The Most Anticipated Collaboration in South Indian Cinema Just Got Its Loudest Confirmation Yet.",
        "subheadline": "LCU writer Rathna Kumar shuts down budget-constraint rumors about Allu Arjun and Lokesh Kanagaraj's pan-India project, confirming pre-production is on track",
        "person": "Allu Arjun",
        "topic": "Allu Arjun Telugu actor Pushpa",
        "caption": "Allu Arjun, whose collaboration with Lokesh Kanagaraj remains on track despite shelving rumors",
        "body": """For forty-eight hours, a section of the internet convinced itself that the most exciting announcement in South Indian cinema this year had quietly collapsed. On Tuesday, an unverified post on X claimed that "a big-budget pan-India movie announced in a very celebrating manner is now stuck in a limbo over budget constraints." It did not name the film. It did not need to. Fans immediately connected it to AA23, the untitled collaboration between Allu Arjun and director Lokesh Kanagaraj.

The panic was swift, loud, and — as it turns out — entirely unnecessary.

## What Actually Happened

On June 3, Rathna Kumar, the screenwriter who has been part of every significant film in the Lokesh Cinematic Universe — Kaithi, Vikram, Leo, and Master — posted a tribute on X marking four years since Vikram's release. At the end of his message, he added five words that ended the speculation: "Can't wait for #AA23."

This was not a press release. It was not a studio clarification. It was better than both. Rathna Kumar is not a publicist managing damage control. He is a creative collaborator who knows exactly where the project stands because he is actively involved in building it. When he says he cannot wait for AA23, it means the project is alive, progressing, and generating the kind of creative excitement that makes a writer post about it voluntarily.

Industry tracker Ramesh Bala confirmed separately that all rumors about the project being shelved are "completely baseless." Pre-production, including script development, is continuing as planned.

## Why AA23 Matters

This is not just another film. This is the collision of two of Indian cinema's most powerful creative forces at the peak of their influence.

Allu Arjun spent five years building the Pushpa franchise into a national phenomenon. The sequel, Pushpa 2: The Rule, became the highest-grossing Telugu film of all time. His screen presence has evolved from regional superstar to pan-India icon, with a National Award underscoring the transition.

Lokesh Kanagaraj has built the most ambitious shared cinematic universe in Indian cinema history. The Lokesh Cinematic Universe — spanning Kaithi, Vikram, and Leo — has demonstrated that Indian audiences will follow interconnected narratives with the same enthusiasm they bring to Marvel films. His directorial grammar is distinctive: tight plotting, morally complex characters, and action choreography that serves the story rather than interrupting it.

AA23 was announced on January 14, 2026, by Mythri Movie Makers. The announcement teaser — featuring Allu Arjun's silhouette managing a horse, accompanied by an Anirudh Ravichander score — caught fire on Instagram Reels within hours. Reports suggest the film could be Lokesh's long-cherished sci-fi project, tentatively known as Irumbu Kai Mayavi, adapted for Allu Arjun's star persona.

## A Historic Cross-Industry Collaboration

This would be Lokesh Kanagaraj's first direct collaboration with a Telugu superstar in a primary lead role. While his dubbed films have performed exceptionally in the Telugu-speaking states, AA23 marks his official foray into directing a hero from outside the Tamil industry. The music is being composed by Anirudh Ravichander, whose scores for Vikram and Leo helped define the sonic identity of the LCU.

For the diaspora audience that follows South Indian cinema, this cross-pollination is significant. It represents the Tamil and Telugu industries not just coexisting but actively merging their biggest creative assets into projects designed for a national and global audience.

## The Budget Question

The shelving rumor specifically cited "budget constraints" as the reason for the alleged cancellation. For context: AA23 is being produced by Mythri Movie Makers, the same studio behind Pushpa 2, which was among the most expensive Telugu films ever made. Mythri has the financial infrastructure and track record to handle projects at this scale. The rumor appears to have originated from confusion about an entirely different project.

That said, the economics of pan-India filmmaking are genuinely challenging. Budgets above ₹300 crore require significant overseas revenue to break even, and the margin for error has shrunk considerably. Every major star vehicle now needs to perform in Hindi-speaking markets in addition to its home territory. AA23, with Allu Arjun's proven pan-India pull and Lokesh's growing national audience, is better positioned than most to clear that bar.

## What to Watch For

Shooting is expected to commence later in 2026 after pre-production wraps. There are unconfirmed reports that Shraddha Kapoor may be cast as the female lead. A formal shooting commencement announcement from Mythri would be the next milestone.

For the diaspora audience that has tracked the LCU's growth — from Kaithi's modest theatrical run to Vikram's blockbuster overseas numbers — AA23 represents the universe's most ambitious bet yet. As of today, it is very much alive.""",
        "sources": json.dumps([
            {"name": "Gulte", "url": "https://gulte.com"},
            {"name": "Hindustan Times", "url": "https://hindustantimes.com"},
            {"name": "LatestLY", "url": "https://latestly.com"},
            {"name": "Zoom TV", "url": "https://zoomtventertainment.com"}
        ])
    }
]

# Process each article
for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i}: {art['headline'][:60]}...")
    print(f"{'='*60}")
    
    # Source image
    print("Sourcing image...")
    img_url, img_attr = source_image(art["person"], art["topic"], art["slug"])
    
    # Build insert payload
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "slug": art["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "sources": art["sources"],
        "is_editorial": False,
        "is_featured": False
    }
    
    if img_url:
        payload["image_url"] = img_url
        payload["image_caption"] = art["caption"]
        payload["image_attribution"] = img_attr
    
    print("Inserting...")
    result = insert_article(payload)
    if not result:
        print("  Retrying without image...")
        for k in ["image_url", "image_caption", "image_attribution"]:
            payload.pop(k, None)
        insert_article(payload)

print(f"\n{'='*60}")
print("ENTERTAINMENT WRITER COMPLETE")
print(f"{'='*60}")
