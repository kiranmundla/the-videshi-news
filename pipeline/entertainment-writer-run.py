#!/usr/bin/env python3
"""Entertainment writer — June 6, 2026 batch (fixed)"""

import json, os, sys, uuid, requests, io, subprocess, time, re, urllib.parse
from datetime import datetime, timezone
from PIL import Image

# ── ENV (load home AFTER workspace to get correct JWT) ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))  # Has correct JWT keys
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = 'TheVideshi/1.0 (thevideshi.com)'

def sb_headers():
    return {
        'apikey': SB_KEY,
        'Authorization': f'Bearer {SB_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

# ── IMAGE HELPERS ──

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

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail (330px, reliable) 
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = thumb or orig
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
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
                    "width": ii.get("width", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_image(url, retries=2):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 429:
                wait = 3 * (attempt + 1)
                print(f"  ⚠ Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code == 200 and len(r.content) > 5000:
                ct = r.headers.get('Content-Type', '')
                if 'image' in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    return r.content
                print(f"  ⚠ Not an image: {ct}")
            else:
                print(f"  ⚠ Download: status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        'apikey': SB_KEY,
        'Authorization': f'Bearer {SB_KEY}',
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true'
    }
    r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)} bytes)")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    """Multi-source image search. Returns (url, attribution)."""
    candidates = []
    
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "priority": 1})
    
    if topic_queries:
        for q in (topic_queries if isinstance(topic_queries, list) else [topic_queries]):
            time.sleep(1)  # Avoid rate limiting
            commons = fetch_wikimedia_commons(q, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
    
    if pexels_query:
        pex_url = fetch_pexels_image(pexels_query)
        if pex_url:
            candidates.append({"url": pex_url, "source": "pexels", "priority": 3})
    
    for cand in sorted(candidates, key=lambda x: x["priority"]):
        raw = download_image(cand["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) < 5000:
                continue
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(compressed, filename)
            if final_url:
                attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attr
            else:
                # Fallback: use original URL directly if it's from Wikimedia (permanent)
                if "wikimedia.org" in cand["url"] or "wikipedia.org" in cand["url"]:
                    attr = "Wikimedia Commons"
                    print(f"  → Using direct Wikimedia URL as fallback")
                    return cand["url"], attr
    
    # Last resort: use the first candidate URL directly
    for cand in sorted(candidates, key=lambda x: x["priority"]):
        if "wikimedia.org" in cand["url"] or "wikipedia.org" in cand["url"]:
            print(f"  → Last resort: direct Wikimedia URL")
            return cand["url"], "Wikimedia Commons"
        if "pexels.com" in cand["url"]:
            print(f"  → Last resort: direct Pexels URL")
            return cand["url"], "Pexels"
    
    return None, None

def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=sb_headers(),
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id', 'unknown')
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ═══════════════════════════════════════════════════════
# ARTICLE 1: Gullak Season 5
# ═══════════════════════════════════════════════════════
print("\n═══ Article 1: Gullak Season 5 ═══")

gullak_slug = "gullak-season-5-sonyliv-mishra-family-five-seasons-middle-class-india-nri-20260606"
gullak_body = """Gullak has returned for a fifth season, and with it comes a distinction no other Indian web series has earned. No show in the country's streaming history has sustained itself this long in the original format, with the same family at the centre and the same emotional DNA running through every episode.

The fifth season of TVF's beloved family drama premiered on SonyLIV on June 5, picking up where the Mishra household left off but carrying the quiet weight of everything that has changed since 2019. The paint on the walls is new. The problems, as always, are not.

## The Mishras, Upgraded but Unchanged

Santosh Mishra is still the anxious patriarch navigating a housing loan application. Shanti Mishra is still searching for an identity beyond her family's needs. Annu, now played by Anant V Joshi after Vaibhav Raj Gupta's departure, is chasing a promotion that will take nine months while his connection with Dr Priti deepens. And Aman, the younger son played by Harsh Mayar, returns home with a secret new direction in life — he wants to become a baba, having decided the spiritual economy has better odds than his academic one.

The recasting of Annu Bhaiya was the season's biggest question mark. Vaibhav Raj Gupta had made the character an emotional anchor over four seasons, and replacing him risked fracturing the show's most important dynamic. But Anant V Joshi does not attempt an imitation. He brings his own rhythm while preserving the character's defining trait — a quiet frustration that reveals itself in restrained bursts rather than outbursts. His chemistry with Harsh Mayar's Aman feels earned, not manufactured.

New addition Gopal Dutt as Pinky Mama, Shanti's brother, introduces a fresh layer of domestic chaos. And Sunita Rajwar's Bittu Ki Mummy has levelled up. She is now the head of a Mahila association and a content creator, poking her nose into every corner of Mishra family business with the authority of someone who believes she has a mandate.

## Five Seasons of Familiarity

The reviews have been divided in a way that reveals something interesting about the show's position. India Forums gave it three out of five stars, calling its familiarity both its greatest strength and its growing challenge. The Hollywood Reporter India was harsher, arguing the "sameness is now a deal-breaker." MensXP praised the emotional payoff, particularly the final episodes. Filmfare called it a warm return. IWMBuzz declared it a satisfying watch.

The disagreement is not really about quality. It is about whether a show that does the same thing beautifully can keep doing it without diminishing returns. Gullak has never chased spectacle. It has never tried to become something it is not. The drama lives in housing loans and neighbourhood gossip, in sons who cannot tell their parents what they really want to do with their lives, in mothers who absorb every family blow and call it duty.

For viewers who grew up in middle-class Indian homes, this is not nostalgia. It is recognition.

## Why the Diaspora Watches Differently

For the Indian diaspora, Gullak occupies a specific emotional space that no other Indian series does. It is not the aspirational India of tech startups or the heightened India of crime thrillers. It is the India of power cuts and pressure cookers, of neighbours who are simultaneously insufferable and indispensable, of parents who express love through criticism because they never learned any other way.

Watching Gullak from a distance — from New Jersey or Fremont or Brampton — hits differently than watching it from Bhopal. The specificity of Mishra family life becomes a mirror for everything the viewer left behind and everything they carry forward, sometimes without realising it.

That is why a show about a lower-middle-class family in a small Hindi-speaking town has resonated across an audience that lives in dollars and speaks in a mix of languages. The Mishras do not represent aspiration. They represent origin.

## The Verdict

Gullak Season 5 is seven episodes of exactly what you expect, and that is either a recommendation or a warning depending on what you came looking for. The writing by Vidit Tripathi remains the backbone. The ending wraps up a little too neatly. The new Annu works better than anyone expected.

For a show in its fifth year, the question is no longer whether it is good. It is whether familiarity is enough. For most of its audience, it is. The earthen piggy bank that gives the show its name has always been about accumulation — small coins dropped in over years, adding up to something larger than any individual deposit.

Five seasons in, Gullak is that piggy bank. It has never held a fortune. But what it holds is irreplaceable.

*Gullak Season 5 is now streaming on SonyLIV in Hindi, available worldwide.*

Sources: SonyLIV, India Forums, Hollywood Reporter India, Filmfare, MensXP, IWMBuzz"""

gullak_img_url, gullak_img_attr = source_image(
    person_name="Jameel Khan",
    topic_queries=["Gullak television series India", "Jameel Khan actor India"],
    pexels_query="Indian family home living room warm",
    slug=gullak_slug
)

# ═══════════════════════════════════════════════════════
# ARTICLE 2: Avantika Vandanapu
# ═══════════════════════════════════════════════════════
print("\n═══ Article 2: Avantika Vandanapu ═══")

avantika_slug = "avantika-vandanapu-harvard-south-asian-person-year-mean-girls-tangled-nri-20260606"
avantika_body = """Harvard University has named Avantika Vandanapu, the 19-year-old Indian-American actress best known for her role in the 2024 Mean Girls adaptation, as its South Asian Person of the Year. The honour arrives at a moment when Vandanapu is simultaneously being celebrated for her achievements and criticised for a role she has not yet even played.

The recognition from Harvard acknowledges what Vandanapu has accomplished in a remarkably short career. Born in Hyderabad to a Telugu family, she moved to the United States as a child and first gained visibility after winning second place on Dance India Dance L'il Masters. From there, she transitioned to acting — first in the Telugu film Brahmotsavam, then in Disney's Spin alongside Meera Syal and Abhay Deol, and ultimately in the Mean Girls musical adaptation that introduced her to a global audience.

## From Hyderabad to Harvard

"Being honored by such a prestigious institution as Harvard University is truly humbling and incredibly motivating," Vandanapu said in her acceptance remarks. "This award not only acknowledges my efforts but also underscores the significance of narratives transcending borders and the crucial role of Indian representation in global media."

At 19, Vandanapu sits at a specific intersection in the South Asian diaspora conversation. She is young enough to have grown up with representation that previous generations never had — Mindy Kaling on television, Priyanka Chopra in Hollywood — but she is also navigating the same debates about identity, casting, and belonging that those earlier trailblazers encountered.

Her trajectory from a Telugu-speaking household in Hyderabad to the Harvard stage mirrors a path that thousands of NRI families recognise. The dance competitions, the cultural performances, the careful negotiation between two identities — Vandanapu's story is specific to her, but the shape of it belongs to a generation.

## The Tangled Controversy

The honour comes amid a backlash that has followed Vandanapu since rumours surfaced that she is being considered for the role of Rapunzel in a live-action adaptation of Disney's Tangled. The reaction on social media was immediate and polarised. Some Disney fans objected to a South Asian actress portraying a character they associate with European fairy tales. Others argued that the casting would represent exactly the kind of boundary-crossing storytelling that Vandanapu described in her Harvard remarks.

Disney has not confirmed the casting. But the intensity of the response — both the criticism and the defence — reveals how much the conversation about representation has shifted without necessarily settling. A decade ago, the debate was about whether South Asians belonged in Hollywood at all. Now it is about which roles they are permitted to inhabit.

For the diaspora, the Tangled controversy carries a particular sting. Many NRI parents raised their children on Disney films while simultaneously ensuring they stayed connected to Indian culture. The idea that their children might now be told they do not fit into Disney's world feels like a rejection that cuts in a direction most did not anticipate.

## What the Honour Means

Harvard's recognition of Vandanapu is not just about one actress. It is about a generation of South Asian Americans who are no longer asking for permission to be visible. They are already there — on Broadway stages, in Marvel films, in the Mean Girls cafeteria — and the conversation has moved from whether they belong to what they are allowed to become.

Vandanapu herself seems aware of the weight. "My journey is just beginning," she said, "and this recognition ignites my determination to continue contributing positively through my work."

She has also appeared in the Indian OTT series Big Girls Don't Cry, maintaining a connection to Indian storytelling even as her Hollywood career grows. It is a choice that reflects the diaspora's broader negotiation — staying connected to both worlds rather than choosing one over the other.

The honour from Harvard arrives at a moment when South Asian representation in entertainment is simultaneously more visible and more contested than ever. Awards are being won. Roles are being debated. And a 19-year-old from Hyderabad is standing at the centre of it, carrying a conversation that is much larger than any single casting decision.

*Avantika Vandanapu was recognised at Harvard University's South Asian Person of the Year ceremony. She next appears in multiple upcoming Hollywood projects.*

Sources: The Indian Eye, Harvard University, Disney, Dance India Dance"""

avantika_img_url, avantika_img_attr = source_image(
    person_name="Avantika Vandanapu",
    topic_queries=["Avantika Vandanapu actress Hollywood"],
    pexels_query=None,
    slug=avantika_slug
)

# ═══════════════════════════════════════════════════════
# ARTICLE 3: Peddi Day 2
# ═══════════════════════════════════════════════════════
print("\n═══ Article 3: Peddi Day 2 Box Office ═══")

peddi_slug = "peddi-ram-charan-day-2-box-office-150-crore-worldwide-steep-drop-nri-20260606"
peddi_body = """Ram Charan's Peddi crossed ₹150 crore worldwide by the end of its second day. That number, in isolation, sounds like a victory lap. In context, it is the beginning of a problem.

The sports action drama, directed by Buchi Babu Sana, collected ₹26.90 crore net in India on Day 2 — a 47 percent drop from its opening day haul of ₹51 crore. The overseas market added another ₹8 crore, bringing the total overseas gross to ₹36 crore and the worldwide gross to ₹150.49 crore across 23,372 shows. India net collections stand at ₹96.40 crore after two days.

The drop is steep, and it arrives at precisely the wrong moment.

## The Numbers Tell Two Stories

Day 1 told a story of triumph. Peddi became Ram Charan's first solo-led film to cross ₹100 crore worldwide on opening day, entering a club dominated by Prabhas (who holds six of the eleven entries on the list of Telugu ₹100-crore openers). It beat the opening day numbers of Dhurandhar, Pathaan, and The Raja Saab. For an actor still recovering from the theatrical disaster of Game Changer, it was vindication.

Day 2 tells a different story. A 47 percent drop on the first Friday — a working day — is not unusual for a Thursday release, but the regional breakdown reveals where the concern lies. Hyderabad occupancy fell to 52.3 percent overall. Bengaluru dropped to 32 percent. Mumbai managed just 22.3 percent. The National Capital Region recorded a dismal 14.5 percent.

The Telugu heartland is holding — Vizag reported 78.8 percent, Vijayawada 68 percent, Kakinada 76.8 percent — but those are small markets in absolute terms. The Hindi belt numbers suggest that Peddi's pan-India crossover, despite Janhvi Kapoor's presence, has not materialised the way the makers hoped. The Hindi version collected an estimated ₹3 crore on opening day, a figure that would barely register in a conversation about national blockbusters.

## The ₹500 Crore Question

The elephant in every trade conversation is the break-even target. Industry estimates place Peddi's worldwide gross requirement at approximately ₹500 crore for the film to be considered a financially successful venture. After two days, with ₹150.49 crore in hand and a declining trajectory, that target looks increasingly distant.

For comparison, Pushpa 2 collected ₹275 crore on its opening day alone. RRR, which also featured Ram Charan (alongside Jr NTR and the Rajamouli brand), opened at ₹223 crore. Peddi's Day 1 of ₹110 crore worldwide puts it in the top eleven Telugu openers ever — but the top eleven is no longer enough when the budget demands top-three performance.

The weekend will be the critical test. Telugu films typically see significant jumps on Saturday and Sunday, especially in their home states. If Peddi can recover to ₹40-45 crore net on Saturday, the weekend total could provide enough momentum for a respectable first-week number. But reaching ₹500 crore would require sustained collections over four to five weeks, and the mixed audience reception — particularly the criticism of Janhvi Kapoor's performance — makes that extended run uncertain.

## What the Diaspora Box Office Says

The overseas number deserves separate attention. ₹36 crore gross in two days is solid for a Telugu film but far from the kind of breakout that would signal genuine global demand. Telugu films in the diaspora tend to front-load heavily — most of the overseas collection comes from the first weekend as NRI audiences turn up for the event and then move on. If Peddi cannot push its overseas total past ₹60-70 crore by Sunday, the international window may already be closing.

The US market, which drives the bulk of Telugu overseas revenue, reflects a pattern familiar to the diaspora: opening night is a community event, Friday is a reality check. Telugu families in the US buy tickets for the Thursday premiere the way they buy tickets for Diwali shows — as a cultural obligation that doubles as entertainment. By Friday, word of mouth takes over, and word of mouth on Peddi has been decidedly mixed.

## Where This Leaves Ram Charan

Two days into its theatrical run, Peddi is neither a disaster nor a triumph. It is something more uncomfortable — a film that opened like a blockbuster and is now behaving like a film that needs to prove itself to its audience all over again.

The comparison that matters most is not with Pushpa 2 or RRR. It is with Game Changer, Charan's last release, which collapsed after its opening weekend. If Peddi follows a similar trajectory, the narrative around Charan's solo box office power will become a talking point that overshadows the genuine achievement of a ₹100-crore-plus opening day.

The weekend will decide. The audience has shown up once. Whether they come back — and whether they bring their friends — is the only question that matters now.

Sources: Sacnilk, Bollywood Hungama, LiveMint, trade estimates"""

peddi_img_url, peddi_img_attr = source_image(
    person_name="Ram Charan",
    topic_queries=["Ram Charan actor Telugu"],
    pexels_query="Indian cinema movie theater",
    slug=peddi_slug
)

# ── BUILD AND INSERT ──
print("\n═══ Inserting Articles ═══")

all_articles = [
    {
        "headline": "Gullak Season 5 Is Here. No Other Indian Web Series Has Made It This Far.",
        "subheadline": "TVF's beloved Mishra family returns on SonyLIV with a new Annu Bhaiya, a housing loan crisis, and the same small-town warmth that has made it the diaspora's most personal comfort watch.",
        "slug": gullak_slug,
        "body": gullak_body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": gullak_img_url,
        "image_caption": "Jameel Khan as Santosh Mishra in Gullak, TVF's longest-running Indian web series",
        "image_attribution": gullak_img_attr or "Pexels",
        "is_editorial": False,
        "sources": json.dumps(["SonyLIV", "India Forums", "Hollywood Reporter India", "Filmfare", "MensXP", "IWMBuzz"])
    },
    {
        "headline": "Avantika Vandanapu Has Been Named Harvard's South Asian Person of the Year. She Is 19.",
        "subheadline": "The Telugu-American Mean Girls actress is being celebrated for breaking barriers in Hollywood — even as a rumoured Tangled casting sparks a debate about which roles South Asians are allowed to play.",
        "slug": avantika_slug,
        "body": avantika_body,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": avantika_img_url,
        "image_caption": "Avantika Vandanapu, Indian-American actress and Harvard's South Asian Person of the Year",
        "image_attribution": avantika_img_attr or "Wikimedia Commons",
        "is_editorial": False,
        "sources": json.dumps(["The Indian Eye", "Harvard University", "Disney", "Dance India Dance"])
    },
    {
        "headline": "Peddi Has Crossed ₹150 Crore Worldwide. The Numbers After Day 2 Tell a More Complicated Story.",
        "subheadline": "Ram Charan's sports drama dropped 47 percent on its second day. The Telugu heartland is holding, but the Hindi belt has barely shown up, and the ₹500 crore break-even target is looking increasingly steep.",
        "slug": peddi_slug,
        "body": peddi_body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": peddi_img_url,
        "image_caption": "Ram Charan, lead actor of Peddi, Telugu cinema's latest box office test",
        "image_attribution": peddi_img_attr or "Wikimedia Commons",
        "is_editorial": False,
        "sources": json.dumps(["Sacnilk", "Bollywood Hungama", "LiveMint"])
    }
]

inserted = 0
for art in all_articles:
    if not art.get('image_url'):
        print(f"  ⚠ No image for: {art['headline'][:50]}... — SKIPPING (image required)")
        continue
    
    word_count = len(art['body'].split())
    print(f"  📝 {art['headline'][:60]}... ({word_count} words)")
    
    art_id = insert_article(art)
    if art_id:
        inserted += 1

print(f"\n═══ Done: {inserted}/{len(all_articles)} articles inserted ═══")
