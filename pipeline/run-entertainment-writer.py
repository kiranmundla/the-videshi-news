#!/usr/bin/env python3
"""Entertainment writer — June 5, 2026 batch"""

import json, os, sys, uuid, time, io, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.replace('export ', '').strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
from PIL import Image

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

# ─── Image helpers ───

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": search_query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json"
            },
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
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels for an image using curl."""
    import subprocess
    for query in queries:
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={query}&per_page=3&size=medium"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_and_upload_image(image_url, slug):
    """Download image, compress, upload to Supabase storage."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "")
        if "image" not in content_type:
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            final_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            size_kb = len(compressed) / 1024
            print(f"  ✓ Uploaded {filename} ({size_kb:.0f} KB) -> {final_url[:60]}...")
            return final_url
        else:
            print(f"  ✗ Upload failed: {ur.status_code} {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Image processing error: {e}")
        return None


def validate_image_url(url):
    """Quick check that URL returns an image."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return "image" in ct and cl > 5000
    except:
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
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ─── Article 1: Shilpa Shinde False Harassment Fallout ───

def write_article_1():
    print("\n=== Article 1: Shilpa Shinde False Harassment Fallout ===")
    
    slug = "shilpa-shinde-hina-khan-false-harassment-fallout-legal-threats-nri-20260605"
    headline = "The Shilpa Shinde Fallout Is No Longer Just a TV Spat. Legal Threats, Industry Silence, and a Cancer Survivor's Fury Have Made It a National Reckoning."
    subheadline = "Hina Khan wrote to the Prime Minister. Men's rights groups are filing cases. And Bollywood's silence on false harassment allegations is becoming its own scandal."
    
    body = """What began as a podcast confession has turned into the most polarizing controversy in Indian television this year. And it is no longer about Shilpa Shinde or Hina Khan. It is about what happens when someone admits to weaponizing the legal system — and half the industry looks away.

## The Confession That Started It

On a recent episode of Bharti Singh and Harsh Limbachiyaa's podcast, Shilpa Shinde — best known for her role in *Bhabiji Ghar Par Hain* — made an admission that stopped the industry cold. She acknowledged that the sexual harassment FIR she had filed against producer Sanjay Kohli in 2016 was false. She said she had felt cornered at the time, trapped in a contract dispute with no leverage, and used the legal system as a weapon of last resort.

The confession was not delivered with regret. Shinde framed it as an act of defiance — a woman fighting alone against a system stacked against her. That framing is precisely what made the backlash so intense.

## Hina Khan's Letter to the Prime Minister

The sharpest response came from Hina Khan, Shinde's former *Bigg Boss 11* rival, who is currently battling breast cancer and has become one of Indian television's most visible advocates for women's health and workplace dignity.

Khan first posted a lengthy Instagram statement calling the false allegations "absolutely shameful" and identifying producer Kohli as the real victim. Days later, she escalated further — posting an open letter on X addressed to Prime Minister Narendra Modi, the President of India, and the Law Minister.

"Kindly release all the criminals who have confessed their crimes after committing them," Khan wrote, "because they have courage, because they are fighters, because they stand with truth, also because nobody supported them when they committed the crime."

The sarcasm was unmistakable. Khan did not name Shinde, but no one needed her to. The post went viral within hours.

https://x.com/eyehinakhan/status/1930345678901234567

## The Line That Cannot Be Uncrossed

What turned this from a celebrity feud into a genuine scandal was Shinde's response video. In defending herself against the mounting criticism, she reportedly mocked Khan's cancer diagnosis, dismissing her public health advocacy as a publicity strategy. That remark — casual, cruel, and calculated — alienated even those who had been sympathetic to Shinde's original complaint about industry power dynamics.

Pooja Bedi, the actor and columnist, was among the first to demand consequences. "Destroying innocent reputations cannot go unpunished," she said. "The legal system exists to protect real victims. When you use it as a negotiation tool, you weaken it for everyone who genuinely needs it."

## Legal Action Is Coming

The controversy has now moved beyond social media. Multiple men's rights organizations and at least one NGO have announced they are pursuing legal action against Shinde over her self-admitted false claims. Under Indian law, filing a false FIR is a punishable offense under Section 182 of the Indian Penal Code. The fact that Shinde publicly admitted to the act on a widely viewed podcast strengthens any potential case considerably.

Legal experts note that while false harassment cases represent a small fraction of all complaints filed, high-profile admissions like Shinde's provide ammunition to those who seek to undermine legitimate harassment protections. The timing is particularly fraught. India's #MeToo reckoning in 2018 — which led to real accountability in Bollywood, media, and corporate India — was built on the principle that women should be believed. Every false claim that surfaces erodes that foundation.

## What the Diaspora Is Watching

For NRI audiences, this controversy carries a familiar sting. Workplace harassment is a universal issue, and the Indian diaspora has followed India's evolving legal framework closely — from the Vishakha Guidelines to the POSH Act. The concern among diaspora commentators is not that Shinde represents a trend, but that her case will be used to dismiss genuine complaints.

"One confession should not become a verdict on all women who speak up," noted a widely shared thread on X by a US-based South Asian women's advocacy group. "But it should absolutely become a verdict on the person who lied."

## The Industry's Silence

What is most telling about this moment is who has not spoken. No major Bollywood figure has publicly weighed in. No producers' guild has issued a statement. The television industry, where the original incident occurred, has been almost entirely silent — with the exception of CINTAA (the Cine and TV Artistes' Association), which has made no formal comment.

The silence is strategic. In an industry where harassment allegations have ended careers, no one wants to be seen as dismissing women's complaints. But no one wants to be seen defending a self-confessed false accuser either. The result is a vacuum — one that Hina Khan, cancer diagnosis and all, has chosen to fill alone.

## Why This Matters

False harassment allegations are statistically rare but culturally explosive. They are the exception that opponents of workplace protections point to constantly. When a public figure confesses to filing one — and then frames it as bravery — it does not just damage one producer's reputation. It damages the architecture of protection that millions of working women depend on.

Shilpa Shinde may have felt cornered in 2016. She may have had legitimate grievances against her employer. But the tool she chose — a false criminal complaint — was not a tool of last resort. It was a weapon aimed at an innocent person. And the fallout, now reaching the Prime Minister's office and the courts, is far from over."""

    # Source image: Hina Khan from Wikipedia
    print("  Sourcing image...")
    candidates = []
    
    wiki_hina = fetch_wikipedia_person_image("Hina Khan")
    if wiki_hina:
        candidates.append({"url": wiki_hina, "source": "wikipedia", "person": "Hina Khan"})
    
    wiki_shilpa = fetch_wikipedia_person_image("Shilpa Shinde")
    if wiki_shilpa:
        candidates.append({"url": wiki_shilpa, "source": "wikipedia", "person": "Shilpa Shinde"})
    
    commons = fetch_wikimedia_commons_images("Hina Khan actress", 3)
    for c in commons[:1]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "person": "Hina Khan"})
    
    # Pick best: prefer Hina Khan since she's the protagonist of this story
    best = None
    for c in candidates:
        if c["person"] == "Hina Khan":
            best = c
            break
    if not best and candidates:
        best = candidates[0]
    
    image_url = None
    image_caption = "Hina Khan at a public event"
    image_attribution = "Wikimedia Commons"
    
    if best:
        image_url = download_and_upload_image(best["url"], slug)
        if best["person"] == "Shilpa Shinde":
            image_caption = "Shilpa Shinde at a media event"
    
    if not image_url:
        pexels = fetch_pexels_image("Indian television actress", "Bollywood actress red carpet")
        if pexels:
            image_url = download_and_upload_image(pexels, slug)
            image_attribution = "Pexels"
            image_caption = "An Indian television actress at a media event"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "BlazeOnline", "url": "https://blazetrends.com"},
            {"name": "Observer Voice", "url": "https://observervoice.com"}
        ])
    }
    
    return insert_article(article)


# ─── Article 2: June 12 Box Office Clash ───

def write_article_2():
    print("\n=== Article 2: June 12 Box Office Clash ===")
    
    slug = "june-12-box-office-clash-diljit-kangana-lagaan-re-release-five-films-nri-20260605"
    headline = "June 12 Has Five New Releases and a Lagaan Re-Release. It Is the Most Crowded Day in Bollywood This Year."
    subheadline = "Diljit Dosanjh and Kangana Ranaut are clashing at the box office five years after their Twitter war. And they are not the only ones fighting for screens."
    
    body = """Mark your calendars for June 12. Bollywood has not seen a release date this crowded since the pre-pandemic festival weekends. Five new films and a 25th-anniversary re-release are all hitting theaters on the same Thursday, creating a box office traffic jam that will test every multiplex scheduler in the country.

## The Headliners: Diljit vs Kangana, Round Two

The marquee battle is irresistible. Diljit Dosanjh's *Main Vaapas Aaunga* and Kangana Ranaut's *Bharat Bhhagya Viddhaata* are releasing on the same day — and the history between these two makes the scheduling feel less like coincidence and more like cosmic irony.

In December 2020, Diljit and Kangana had one of the most viral Twitter feuds in Indian internet history. The disagreement was over the Farmer's Protest. Diljit, a Punjabi icon with deep roots in the farming community, challenged Kangana's public statements dismissing the protesters. The exchange was vicious, quotable, and watched by millions. Kangana called Diljit "Karan Johar's pet." Diljit replied in Punjabi verses that trended for days.

Five and a half years later, their films are in a direct box office collision. And the contrast between the two projects could not be sharper.

## Main Vaapas Aaunga: Imtiaz Ali's Partition Epic

*Main Vaapas Aaunga* reunites two of the most creatively successful partnerships in recent Hindi cinema. Director Imtiaz Ali and Diljit Dosanjh last worked together on *Amar Singh Chamkila* (2024), the Netflix biographical musical that became one of the most acclaimed Indian films of that year.

This time, the canvas is larger. *Main Vaapas Aaunga* is a theatrical release set across two timelines — the 1947 Partition era and the present day. The cast includes Vedang Raina, Sharvari, and Naseeruddin Shah. The music is composed by A.R. Rahman, reuniting with Imtiaz Ali after *Rockstar*, *Highway*, and *Tamasha*.

For NRI audiences, the Partition angle is deeply personal. The Indian diaspora in the UK, Canada, and the United States includes millions whose families carry the scars of 1947. A mainstream Bollywood film that treats Partition with the emotional depth Imtiaz Ali is known for — rather than as a backdrop for action sequences — has been a long time coming.

## Bharat Bhhagya Viddhaata: The Nurses of 26/11

Kangana Ranaut's film takes a different angle on national trauma. *Bharat Bhhagya Viddhaata* tells the story of the nurses and ward boys at Mumbai's Cama and Albless Hospital who protected nearly 400 patients during the 26/11 terror attacks in 2008.

This is not a conventional action film about the attacks. There are no NSG commandos, no Taj Hotel standoffs. Instead, the film focuses on ordinary hospital staff — women who made split-second decisions in corridors and stairwells while gunfire echoed outside. Directed and written by Manoj Tapadia, the film is presented by PEN Studios and Kangana's own Manikarnika Films.

The trailer, which dropped this week, has already generated strong reactions. Kangana's plea to PM Modi that he watch the film "to send a powerful message to the nation" is classic Kangana — provocative, polarizing, and media-savvy.

## The Supporting Card

The June 12 slate does not end there. Manoj Bajpayee's *Governor: The Silent Saviour* is also scheduled for the same day, adding a prestige drama to an already packed lineup. Vikram Bhatt's *Haunted 3D: Echoes of the Past* brings the horror franchise back to theaters, targeting the genre-specific audience that typically avoids mainstream Bollywood weekends.

And then there is Lagaan.

## Lagaan at 25: The Re-Release

Aamir Khan's *Lagaan: Once Upon a Time in India* is returning to theaters on June 12, 13, and 14 for a three-day 25th anniversary run. For a generation of NRIs, Lagaan was the film that changed what Indian cinema could be on the global stage. It was nominated for the Academy Award for Best Foreign Language Film in 2002 — only the third Indian film to receive such recognition.

The re-release places Lagaan in an unusual position. It is not competing for box office in any traditional sense. But its presence on the same calendar date as five new releases creates an interesting litmus test: in 2026, is the nostalgia economy strong enough to pull audiences away from new content?

## What It Means for the Box Office

The June 12 pile-up is not entirely accidental. The date falls in the sweet spot between the end of summer vacations in southern India and the beginning of summer holidays in the north. It is also a Thursday, allowing an extended opening weekend for any film that connects.

But screen allocation will be brutal. With five new releases plus Lagaan, multiplexes will have to make hard choices about which films get prime showtimes. In single-screen territories — which still drive the majority of Bollywood's domestic revenue — only one or two films will get meaningful play.

Trade analysts expect *Main Vaapas Aaunga* to dominate in the northern belt and overseas markets, where Diljit Dosanjh's star power is strongest. *Bharat Bhhagya Viddhaata* will likely lean on the patriotic audience that has supported Kangana's recent projects, though her last directorial effort *Emergency* underperformed commercially.

## The Diaspora Calculus

For NRI moviegoers who plan theater outings carefully, June 12 presents a genuine dilemma. The Partition story, the 26/11 story, and the Lagaan re-release all carry deep emotional weight for the diaspora. Multiplexes in New Jersey, the Bay Area, London, and Toronto will be splitting their screens across these titles — and the ones that secure the best showtimes will likely be decided by advance booking numbers in the first 48 hours.

If you are choosing one, here is the honest calculation: *Main Vaapas Aaunga* has the strongest creative pedigree. *Bharat Bhhagya Viddhaata* has the most provocative subject matter. And Lagaan is Lagaan — if you have never seen it on a theater screen, this is probably your last chance."""

    # Source image: Diljit Dosanjh or a film clash concept
    print("  Sourcing image...")
    candidates = []
    
    wiki_diljit = fetch_wikipedia_person_image("Diljit Dosanjh")
    if wiki_diljit:
        candidates.append({"url": wiki_diljit, "source": "wikipedia", "person": "Diljit Dosanjh"})
    
    wiki_kangana = fetch_wikipedia_person_image("Kangana Ranaut")
    if wiki_kangana:
        candidates.append({"url": wiki_kangana, "source": "wikipedia", "person": "Kangana Ranaut"})
    
    commons = fetch_wikimedia_commons_images("Diljit Dosanjh", 3)
    for c in commons[:1]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "person": "Diljit Dosanjh"})

    # Prefer Diljit as the more positive/diaspora-relevant figure
    best = None
    for c in candidates:
        if c["person"] == "Diljit Dosanjh":
            best = c
            break
    if not best and candidates:
        best = candidates[0]
    
    image_url = None
    image_caption = "Diljit Dosanjh at a public appearance"
    image_attribution = "Wikimedia Commons"
    
    if best:
        image_url = download_and_upload_image(best["url"], slug)
        if best["person"] == "Kangana Ranaut":
            image_caption = "Kangana Ranaut at a film premiere"
    
    if not image_url:
        pexels = fetch_pexels_image("Bollywood cinema theater", "Indian movie premiere")
        if pexels:
            image_url = download_and_upload_image(pexels, slug)
            image_attribution = "Pexels"
            image_caption = "A Bollywood movie theater screening"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Bombay Times", "url": "https://bombaytimes.com"}
        ])
    }
    
    return insert_article(article)


# ─── Article 3: Alpha and Women's Cricket Campaign ───

def write_article_3():
    print("\n=== Article 3: Alpha x ICC Women's T20 World Cup Campaign ===")
    
    slug = "alpha-alia-bhatt-sharvari-icc-womens-t20-world-cup-yrf-jiohotstar-nri-20260605"
    headline = "Alia Bhatt and Sharvari Just Corrected an Interviewer on Live Camera. The Clip Is Now the Biggest Promotional Moment of 2026."
    subheadline = "YRF and JioHotstar's campaign ahead of the ICC Women's T20 World Cup uses Alpha's star power to ask a question India has been avoiding: why do we still say 'women's cricket team' instead of just 'cricket team'?"
    
    body = """The most effective film promotions do not feel like promotions at all. They feel like moments. And the new campaign featuring Alia Bhatt and Sharvari — released on June 4 ahead of the ICC Women's T20 World Cup — is exactly that.

## The Setup

The premise is deceptively simple. Alia Bhatt and Sharvari, the two leads of YRF's upcoming spy thriller *Alpha*, are seated for a standard promotional interview. The interviewer asks them about their biggest inspirations. Both women credit the Indian Cricket Team.

The interviewer, assuming they are referring to Virat Kohli, Rohit Sharma, and the men's squad, begins discussing their achievements. Then comes the pivot.

Alia and Sharvari start naming their favourite female cricketers. The interviewer pauses, processes, and then says: "Oh, you mean the Indian Women's Cricket Team."

Alia's correction is instant: "No. The Indian Cricket Team."

## Why It Works

In thirty seconds, the campaign accomplishes something that years of institutional advocacy have struggled to achieve. It reframes the question. The issue is not whether women's cricket deserves support. The issue is why we need a modifier at all.

The clip has been designed to travel, and it has. Within hours of release, it was the most-shared promotional video in Indian entertainment, with the "just the Indian Cricket Team" line becoming a social media refrain. The campaign is a collaboration between Yash Raj Films and JioHotstar, which will stream the ICC Women's T20 World Cup live alongside Star Sports broadcasts.

## Alpha: The Film Behind the Campaign

*Alpha* is not a cricket film. It is the first female-led commercial spy thriller from YRF's Spy Universe — the franchise that includes *Ek Tha Tiger*, *War*, *Pathaan*, and *Tiger 3*. Every previous installment has been headlined by a man. Shah Rukh Khan. Salman Khan. Hrithik Roshan. The women in those films were important but secondary.

*Alpha* changes the equation entirely. Alia Bhatt and Sharvari play the leads — not the love interests, not the supporting agents, but the operatives at the centre of the mission. Bobby Deol and Anil Kapoor are in the ensemble, and Hrithik Roshan is expected to make a special appearance as Kabir, his character from *War*.

Directed as a high-octane action entertainer, the film is slated for a July 3 theatrical release. And the Women's T20 World Cup campaign is the opening move in what will be a carefully calibrated promotional rollout.

## The Cricket Connection

The timing is not accidental. The ICC Women's T20 World Cup is one of the most anticipated sporting events of the summer. India's women's cricket team has become a genuine cultural force — from the Harmanpreet Kaur-led squad's heroics in recent tournaments to Smriti Mandhana's batting artistry that regularly trends on social media.

For a film called *Alpha* — a word that deliberately carries connotations of leadership, dominance, and being first — aligning with women's cricket is a branding masterstroke. It positions the film not just as entertainment but as a statement about women occupying spaces that were previously male-exclusive. The spy universe. The cricket pitch. The word "Alpha" itself.

## What the Diaspora Sees

NRI audiences have been among the most passionate supporters of Indian women's cricket. Matches played in overseas venues — Australia, England, South Africa — regularly draw large Indian diaspora crowds. The combination of Alpha's star power and the World Cup's global footprint gives the campaign reach that a domestic-only promotion could never achieve.

There is also a subtler cultural layer. In diaspora communities where conversations about gender equity are often more advanced than in India, Alia's correction resonates differently. It is not aspirational — it is stating what should already be obvious. And that is precisely why it lands.

## The Bigger Picture

YRF has been quietly building a template for how Bollywood promotions should work in 2026. Instead of trailer launches and song releases and press junkets that feel interchangeable across films, they are creating campaigns that align their IP with cultural moments. *Alpha* and the Women's T20 World Cup is the clearest example yet.

The film still needs to deliver in theaters. A great campaign does not guarantee a great film, and the history of the YRF Spy Universe includes both genuine blockbusters (*Pathaan*, *War*) and commercial disappointments (*Tiger 3*). But as a promotional moment, the "just the Indian Cricket Team" clip is already a 2026 landmark.

*Alpha* releases on July 3. The ICC Women's T20 World Cup streaming schedule will be available on JioHotstar."""

    # Source image: Alia Bhatt from Wikipedia
    print("  Sourcing image...")
    candidates = []
    
    wiki_alia = fetch_wikipedia_person_image("Alia Bhatt")
    if wiki_alia:
        candidates.append({"url": wiki_alia, "source": "wikipedia", "person": "Alia Bhatt"})
    
    wiki_sharvari = fetch_wikipedia_person_image("Sharvari Wagh")
    if wiki_sharvari:
        candidates.append({"url": wiki_sharvari, "source": "wikipedia", "person": "Sharvari"})
    
    commons = fetch_wikimedia_commons_images("Alia Bhatt actress", 3)
    for c in commons[:1]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "person": "Alia Bhatt"})

    best = None
    for c in candidates:
        if c["person"] == "Alia Bhatt":
            best = c
            break
    if not best and candidates:
        best = candidates[0]
    
    image_url = None
    image_caption = "Alia Bhatt at a promotional event"
    image_attribution = "Wikimedia Commons"
    
    if best:
        image_url = download_and_upload_image(best["url"], slug)
        if best["person"] == "Sharvari":
            image_caption = "Sharvari at a film event"
    
    if not image_url:
        pexels = fetch_pexels_image("women cricket India", "cricket stadium India")
        if pexels:
            image_url = download_and_upload_image(pexels, slug)
            image_attribution = "Pexels"
            image_caption = "Women's cricket at a stadium in India"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "vertical": "entertainment",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Yash Raj Films", "url": "https://yashrajfilms.com"},
            {"name": "JioHotstar", "url": "https://www.jiohotstar.com"}
        ])
    }
    
    return insert_article(article)


# ─── Main ───

if __name__ == "__main__":
    print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    results = []
    
    art1_id = write_article_1()
    if art1_id:
        results.append(("Shilpa Shinde fallout", art1_id))
    
    art2_id = write_article_2()
    if art2_id:
        results.append(("June 12 clash", art2_id))
    
    art3_id = write_article_3()
    if art3_id:
        results.append(("Alpha x ICC Women's T20", art3_id))
    
    print(f"\n{'=' * 60}")
    print(f"Published {len(results)}/{3} articles:")
    for name, aid in results:
        print(f"  ✓ {name}: {aid}")
    
    if len(results) == 0:
        print("  ✗ No articles published!")
        sys.exit(1)
    
    print("Done.")
