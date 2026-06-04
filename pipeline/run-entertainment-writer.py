#!/usr/bin/env python3
"""
The Videshi Entertainment Writer — June 4, 2026
Writes 3 articles: Aamir Khan wedding, Varun Dhawan AI deepfakes ruling, FWICE withdraws Ranveer ban
"""
import json, os, sys, uuid, requests, subprocess, io, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, _, val = line.partition('=')
                    val = val.strip('"').strip("'")
                    os.environ[key.strip()] = val

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

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch a relevant image from Pexels using curl."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage bucket."""
    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}): {img_url[:60]}")
            return None
        content_type = r.headers.get('Content-Type', '')
        if 'image' not in content_type and len(r.content) < 5000:
            print(f"  ✗ Not a valid image or too small")
            return None
        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  📦 Compressed to {size_kb:.0f} KB")
        if size_kb < 10:
            print(f"  ✗ Too small after compression ({size_kb:.0f} KB)")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(upload_url, data=compressed, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=20)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({resp.status_code}): {resp.text[:100]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None

def source_image(person_name, topic_queries, slug):
    """Multi-source image comparison. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    for q in topic_queries:
        commons = fetch_wikimedia_commons_images(q, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
        if commons:
            break

    # Source 3: Pexels
    for q in topic_queries:
        pexels = fetch_pexels_image(q)
        if pexels:
            candidates.append({"url": pexels, "source": "pexels", "relevance": 1})
            break

    # Pick best and upload
    if not candidates:
        print("  ✗ No image found from any source")
        return None, None

    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    best = candidates[0]
    print(f"  → Best source: {best['source']} (relevance={best['relevance']})")

    filename = f"{slug}.jpg"
    uploaded_url = upload_to_supabase(best["url"], filename)
    if uploaded_url:
        attr = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
        return uploaded_url, attr

    # Try next candidate if first failed
    for fallback in candidates[1:]:
        print(f"  → Trying fallback: {fallback['source']}")
        uploaded_url = upload_to_supabase(fallback["url"], filename)
        if uploaded_url:
            attr = "Wikimedia Commons" if fallback["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return uploaded_url, attr

    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

# ──────────────────────────────────────────────
# ARTICLE 1: Aamir Khan & Gauri Spratt Wedding
# ──────────────────────────────────────────────
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Aamir Khan & Gauri Spratt Wedding")
    print("="*60)

    slug = "aamir-khan-gauri-spratt-wedding-july-5-third-marriage-nri-20260604"
    headline = "Aamir Khan Is Getting Married Again. The Story of the Woman He Chose Starts in 1920s Colonial India."
    subheadline = "Gauri Spratt's grandfather was a British Communist who came to India to fight for its freedom. Now his granddaughter is marrying Bollywood's most private superstar in a registered ceremony on July 5."

    body = """Aamir Khan, 60, is getting married for the third time. His partner, Gauri Spratt, 47, will formally become his wife on July 5, 2026, in a registered ceremony at his Mumbai residence. Only close family and a handful of friends will be present. There will be no Bollywood-scale reception. No spectacle. Just two families, a signing, and a new chapter that — by most accounts — has already been unfolding quietly for over a year.

The news, first reported by Filmfare and confirmed by multiple sources close to the couple, carries a kind of understatement that is distinctly Aamir. "They have built a happy, stable life together and simply decided to mark it formally with their families present," a family source told Filmfare. Aamir himself, in a recent interview with Screen, had already signaled this. "In my heart, I'm already married to her," he said. "Whether we formalize it or not is something I will decide as we go along."

He decided.

## A Friendship of Twenty-Five Years

What makes this story unusual, even by Bollywood standards, is its timeline. Aamir and Gauri have known each other for roughly 25 years. They were friends — just friends — for the vast majority of that time. Romantic feelings developed only in recent years, long after Aamir's second marriage to filmmaker Kiran Rao ended in 2021. He introduced Gauri publicly during his 60th birthday celebrations in March 2025, in a characteristically low-key moment during a media interaction. Since then, they have been seen together at family events, and Aamir has spoken about the relationship with a frankness that surprised many who know his famously guarded personality.

Gauri, who is originally from Bengaluru, runs a hair salon in Mumbai. She has a seven-year-old son, Quinn, from a previous marriage. She is, by design and temperament, not a public figure. But her family story is anything but ordinary.

## The Grandfather Who Crossed an Ocean

Gauri's grandfather, Philip Spratt, was born in England. In the 1920s, he traveled to India as a young Communist, sent by the Communist Party of Great Britain to support the Indian independence movement. He didn't come as a tourist or an academic. He came as an organizer, working alongside Indian trade unionists and political activists at a time when doing so carried real risk under British colonial law.

Spratt was arrested and tried in the famous Meerut Conspiracy Case of 1929, one of the landmark trials of the independence era, in which the British colonial government prosecuted labor leaders and Communists for attempting to overthrow the Crown. He spent years in Indian prisons. And then, after release, he stayed. He married an Indian woman, raised a family, and spent the rest of his life in the country he had chosen over the one he was born in.

There is something quietly fitting about his granddaughter now building her own life in India, on her own terms, with a man who has built one of the most singular careers in Indian cinema.

## A Pattern of Privacy

For the NRI community, which has followed Aamir's personal life across continents and decades, this wedding will carry a particular resonance. Aamir has always been the Bollywood star who does things differently. His first marriage to Reena Dutta, his teenage sweetheart, lasted from 1986 to 2002 and produced two children — Junaid and Ira. His second marriage to Kiran Rao, whom he met on the set of Lagaan, lasted 15 years. Both relationships ended with unusual grace and continued co-parenting.

This third chapter follows the same pattern: considered, unhurried, and stubbornly private. In an era where celebrity weddings are content events, Aamir's decision to sign papers in his living room feels like a statement in itself.

## What Comes Next

Professionally, Aamir is deep into pre-production on his next film — a biopic about Lala Amarnath, India's first Test centurion, directed by Ashutosh Gowariker. The film is set during Partition, and reunites the director-actor pair behind Lagaan. Whether the July 5 wedding will disrupt that schedule remains to be seen, though knowing Aamir, the disruption will be measured in hours, not weeks.

Both families have given their full support, and no public confirmation has been issued — because, in Aamir's world, the absence of a denial is confirmation enough."""

    # Source image
    print("Sourcing image...")
    img_url, attr = source_image(
        "Aamir Khan",
        ["Aamir Khan actor Bollywood", "Aamir Khan 2025 2026"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_attribution": attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Filmfare", "url": "https://www.filmfare.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
            {"name": "India Forums", "url": "https://www.indiaforums.com"}
        ])
    }

    art_id = insert_article(article)
    return art_id

# ──────────────────────────────────────────────
# ARTICLE 2: Delhi HC Varun Dhawan AI Deepfakes
# ──────────────────────────────────────────────
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Delhi HC Protects Varun Dhawan's Personality Rights")
    print("="*60)

    slug = "delhi-hc-varun-dhawan-personality-rights-ai-deepfakes-takedown-nri-20260604"
    headline = "A Delhi Court Just Told the Internet to Stop Stealing Varun Dhawan's Face. The Ruling Matters Beyond Bollywood."
    subheadline = "The Delhi High Court ordered the takedown of AI-generated deepfakes, fake endorsements, and unauthorized merchandise using Dhawan's likeness — setting a precedent that could reshape how Indian celebrities fight back against synthetic media."

    body = """On May 29, Justice Jyoti Singh of the Delhi High Court issued an interim order that does something Indian law has struggled to do for years: protect a living person's face from being used without their consent in an age where artificial intelligence can replicate anyone.

The order was passed in a suit filed by actor Varun Dhawan, who alleged that multiple websites, e-commerce platforms, and social media accounts had been exploiting his name, image, voice, and likeness — including AI-generated deepfakes depicting him in pornographic scenarios. The court agreed he had a prima facie case and granted immediate relief.

## What the Court Actually Ordered

The ruling is specific and sweeping. Justice Singh restrained all named defendants from utilizing, exploiting, or misappropriating Dhawan's name, image, voice, likeness, or any other identifiable element of his persona, through technologies including artificial intelligence, generative AI, machine learning, deepfakes, AI chatbots, and face-morphing tools.

The order goes further. E-commerce platforms, social media intermediaries, and websites must take down offending content within 36 hours of being notified. The restraint covers fake endorsements, unauthorized merchandise — posters, mugs, phone cases, calendars, towels — and any commercial use of Dhawan's persona without explicit authorization.

"The plaintiff is entitled to protection against dissemination of pornographic content as well as AI-generated images portraying him in an inappropriate scenario," Justice Singh observed. "Such distasteful content is harming and damaging the reputation of the plaintiff and may mislead the public into believing what is depicted may be true."

## The Defendants Tell the Story

Dhawan's lawsuit named several categories of offenders: Artist Booking Company and Hire4Event, which were allegedly offering bookings for his appearances without authorization. E-commerce platforms including Iceposter, Amazon, Redbubble, and Desertcart, which were selling merchandise featuring his likeness. And digital platforms creating AI-generated content — including explicit material — using his face and name for commercial gain.

The lawsuit described Iceposter as a "habitual infringer," citing prior lawsuits by other celebrities. Dhawan also holds trademark registrations for his name and signature, which the court noted gave him additional legal standing.

## Why This Matters for the Diaspora

For NRIs working in tech, this ruling lands at an interesting intersection. India's current legal framework does not explicitly define "personality rights." The Information Technology Act, 2000, and the 2026 Intermediary Guidelines address synthetic media and deepfakes, but the protections are reactive rather than preventive. This case pushes the boundaries.

The ruling follows a similar recent case involving Telugu actor Naga Chaitanya, who also sought personality rights protection from the Delhi High Court. Together, these cases are building a body of precedent that Indian courts are willing to act decisively when AI technology is used to exploit celebrity identities — even before the legislature catches up with specific laws.

For the Indian tech community in Silicon Valley, Seattle, and beyond — where many work on the AI tools that enable this kind of content creation — the tension is real. The same generative models that power creative tools and enterprise products can, with minimal effort, produce synthetic celebrity content that Indian courts now consider harmful.

## The Bigger Pattern

Varun Dhawan is not the first Indian actor to fight this battle. Anil Kapoor secured a landmark personality rights order in 2023. Amitabh Bachchan has pursued similar protections. But the Dhawan case is notable for how explicitly it addresses AI-generated content, including deepfakes and face-morphing, as distinct categories of infringement.

The 36-hour takedown mandate is particularly significant. It imposes a timeline that platforms must meet, creating operational obligations that go beyond a simple cease-and-desist. For platforms operating globally but serving Indian users, this creates compliance complexity.

The next hearing in the case will determine whether these interim protections become permanent. But the signal is clear: Indian courts are treating AI-generated exploitation of celebrity identity as a serious, actionable harm — and they expect platforms to respond fast.

The question, as always, is enforcement. The internet moves faster than any court order. But for now, at least on paper, Varun Dhawan's face belongs to him."""

    # Source image
    print("Sourcing image...")
    img_url, attr = source_image(
        "Varun Dhawan",
        ["Varun Dhawan actor", "Delhi High Court"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_attribution": attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "MediaNama", "url": "https://www.medianama.com"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"}
        ])
    }

    art_id = insert_article(article)
    return art_id

# ──────────────────────────────────────────────
# ARTICLE 3: FWICE Withdraws Ranveer Ban
# ──────────────────────────────────────────────
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: FWICE Withdraws Directive Against Ranveer Singh")
    print("="*60)

    slug = "fwice-withdraws-non-cooperation-directive-ranveer-singh-don-3-resolution-nri-20260604"
    headline = "FWICE Blinked First. The Non-Cooperation Directive Against Ranveer Singh Is Over. The Don 3 Fight Is Not."
    subheadline = "Nine days after issuing an industry-wide directive against Ranveer Singh for walking out of Don 3, FWICE withdrew it under pressure from producers' bodies and a legal notice. Nobody won. But the power balance in Bollywood just shifted."

    body = """The Federation of Western India Cine Employees announced on June 3 that it has withdrawn, with immediate effect, the non-cooperation directive it had issued against Ranveer Singh. The withdrawal comes nine days after FWICE ordered its members across all crafts to refuse work on any project involving the actor — and just days after Singh served the federation with a formal legal notice.

FWICE President BN Tiwari announced the decision at a press conference in Mumbai. "No one has emerged victorious or defeated in this situation," he said, a line that managed to be both diplomatic and revealing. "Our legal team will address his legal notice."

The backstory: On May 25, FWICE issued the directive following a complaint from filmmaker Farhan Akhtar and producer Ritesh Sidhwani. They alleged that Ranveer had withdrawn from Don 3 — the franchise reboot that Excel Entertainment had been developing with him since 2023 — at an advanced stage of pre-production, after approximately ₹45 crore had already been spent. FWICE described the walkout as a violation of "industry ethics and longstanding professional norms" and called on producers to take a collective stand.

## What Actually Happened

Ranveer Singh's response was not public contrition. It was a legal notice. While the actor himself maintained a deliberate silence — his team had earlier released a statement saying he believed "professional discussions and personal relationships should be managed with dignity, mutual respect, and maturity" — his lawyers challenged FWICE's jurisdiction head-on.

The legal footing was not new. In 2017, the Competition Commission of India had ruled in a case filed by producer Vipul Amrutlal Shah that FWICE's practice of mandating producers to work exclusively with its members violated the Competition Act, 2002. The CCI issued a cease-and-desist order, effectively limiting FWICE's enforcement powers. Singh's legal team reportedly invoked this precedent.

The intervention of the Indian Motion Picture Producers' Association (IMPPA) and the producers' guild was the final push. According to Tiwari, these bodies advised FWICE to resolve the matter through dialogue rather than directives that could set uncomfortable precedents for producers, directors, and actors alike.

## Why This Matters

The Don 3 episode exposed a structural tension that Bollywood has long preferred to manage quietly: who bears the risk when a star exits a project?

From Excel Entertainment's perspective, the numbers are straightforward. ₹45 crore in pre-production costs, committed schedules, location bookings, and crew allocations — all disrupted by one actor's decision. FWICE's directive, whatever its legal validity, was meant to signal that such walkouts carry consequences.

From Ranveer's perspective, the directive amounted to an industry body punishing an actor for what is ultimately a contractual dispute between two private parties. His refusal to appear before FWICE's committee — and his insistence that the federation lacked structural jurisdiction — challenged the body's authority in a way that few A-list actors have done publicly.

## The NRI Angle

For the diaspora, this story mirrors debates that play out in every industry where talent and capital negotiate power. In Hollywood, similar disputes are handled through binding contracts, arbitration clauses, and studio insurance. In Bollywood, where deal structures remain more informal, industry bodies like FWICE have historically filled the enforcement gap. The Don 3 episode suggests that gap is closing — or at least that the enforcement tools are inadequate.

The CCI's 2017 ruling already established that FWICE cannot function as a cartel. Singh's legal notice reinforced the point. And the federation's withdrawal, regardless of how it was framed, confirmed it. When a star has lawyers and precedent on his side, a press conference is not enough.

## What Happens Next

The directive is withdrawn, but the underlying dispute is not resolved. Farhan Akhtar and Ritesh Sidhwani's complaint about the ₹45 crore loss remains. Whether they pursue a civil claim, seek arbitration, or let the matter dissolve into Bollywood's long tradition of quiet settlements is an open question.

Ranveer, meanwhile, has Dhurandhar in theaters and Pralay reportedly beginning production in August. His calendar does not suggest a man in crisis. Farhan Akhtar's Don 3, however, remains in limbo — a franchise without its lead actor and a production without a clear path forward.

The federation blinked. The industry noticed."""

    # Source image
    print("Sourcing image...")
    img_url, attr = source_image(
        "Ranveer Singh",
        ["Ranveer Singh Bollywood actor", "FWICE Bollywood federation"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_attribution": attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"},
            {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "PTI", "url": "https://www.ptinews.com"}
        ])
    }

    art_id = insert_article(article)
    return art_id

# ── Main ──
if __name__ == "__main__":
    print("="*60)
    print("THE VIDESHI — Entertainment Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)

    results = []

    try:
        art1 = write_article_1()
        results.append(("Aamir Khan Wedding", art1))
    except Exception as e:
        print(f"✗ Article 1 failed: {e}")
        import traceback; traceback.print_exc()

    try:
        art2 = write_article_2()
        results.append(("Varun Dhawan AI Deepfakes", art2))
    except Exception as e:
        print(f"✗ Article 2 failed: {e}")
        import traceback; traceback.print_exc()

    try:
        art3 = write_article_3()
        results.append(("FWICE Ranveer Withdrawal", art3))
    except Exception as e:
        print(f"✗ Article 3 failed: {e}")
        import traceback; traceback.print_exc()

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    for title, art_id in results:
        status = "✓" if art_id else "✗"
        print(f"  {status} {title}: {art_id or 'FAILED'}")
    
    successes = sum(1 for _, aid in results if aid)
    print(f"\n  Published: {successes}/{len(results)} articles")
    
    if successes == 0:
        sys.exit(1)
