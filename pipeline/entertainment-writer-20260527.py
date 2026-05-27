#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-27 run"""

import json, os, re, uuid, datetime, requests, urllib.parse, time

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image sourcing ─────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Fetch an image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that URL returns a real image > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if 'image' in ct:
            return True
        # Try GET for wikimedia
        if 'wikimedia' in url or 'wikipedia' in url:
            return True
    except:
        pass
    # Allow known good domains
    if any(d in url for d in ['upload.wikimedia.org', 'images.pexels.com']):
        return True
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = None
        for attempt in range(3):
            r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
            if r.status_code == 200:
                break
            if r.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  ⚠ Rate limited, retrying in {wait}s...")
                time.sleep(wait)
                continue
            break
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            if any(d in image_url for d in ['upload.wikimedia.org', 'images.pexels.com']):
                print(f"  → Using direct permanent URL instead")
                return image_url
            return None
        
        ct = r.headers.get('Content-Type', 'image/jpeg')
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': ct,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=15
        )
        if resp.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            # Fall back to original URL if from permanent source
            if any(d in image_url for d in ['upload.wikimedia.org', 'images.pexels.com']):
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if any(d in image_url for d in ['upload.wikimedia.org', 'images.pexels.com']):
            return image_url
        return None

def source_image(person_name, article_id, slug, fallback_pexels_query=None, fallback_pexels_alt=None):
    """Source image: Wikipedia first, then Pexels fallback."""
    attribution = None
    img_url = None
    
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"
    
    if not img_url and fallback_pexels_query:
        img_url = fetch_pexels_image(fallback_pexels_query, fallback_pexels_alt)
        if img_url:
            attribution = "Pexels"
    
    if not img_url:
        print(f"  ✗ No image found for article: {slug}")
        return None, None
    
    if not validate_image_url(img_url):
        print(f"  ✗ Image validation failed: {img_url[:80]}")
        return None, None
    
    # Upload to Supabase
    filename = f"{article_id}.jpg"
    final_url = upload_to_supabase_storage(img_url, filename)
    return final_url, attribution

# ── Supabase helpers ───────────────────────────────────────────
def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=15)
    if r.status_code in [200, 201]:
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    print(f"  ✗ Insert failed [{r.status_code}]: {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    params = '&'.join(f'{k}={v}' for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=15)
    if r.status_code in [200, 204]:
        return True
    print(f"  ✗ Patch failed [{r.status_code}]: {r.text[:300]}")
    return False

# ── Articles ───────────────────────────────────────────────────

articles = [
    {
        "headline": "Mammootty Skipped His Own Padma Bhushan Ceremony. He Was at a University in Kerala, Collecting His Third Doctorate.",
        "subheadline": "The Malayalam cinema legend was honoured by Mahatma Gandhi University in Kottayam on the same day President Murmu called his name at Rashtrapati Bhavan. He chose the university. Neither institution seemed surprised.",
        "slug": "mammootty-padma-bhushan-missed-ceremony-third-doctorate-mg-university-kerala-20260527",
        "category": "entertainment",
        "person_name": "Mammootty",
        "pexels_fallback": None,
        "pexels_alt": None,
        "sources": ["https://www.newspointapp.com/english/lifestyle/mammootty-receives-third-doctorate-honour", "https://www.latestly.com/entertainment/bollywood/padma-awards-2026-hema-accepts-dharmendras-award-mammootty-alka-honoured/", "https://en.wikipedia.org/wiki/Mammootty"],
        "diaspora_angle": "For the Kerala diaspora — one of the most globally dispersed Indian communities — Mammootty is a cultural cornerstone. He is proof that you can build a career entirely in Malayalam and still be recognised at the highest levels of Indian civilian honours.",
        "tags": ["entertainment", "bollywood", "mammootty", "padma-awards", "kerala", "malayalam-cinema", "diaspora"],
        "urgency": "medium",
        "score_total": 82,
        "body": """Mammootty did not attend his Padma Bhushan ceremony. This is not conjecture or gossip. On May 25, while President Droupadi Murmu conferred India's third-highest civilian honour at Rashtrapati Bhavan in New Delhi, the 74-year-old Malayalam superstar was in Kottayam, Kerala, receiving an honorary Doctor of Letters from Mahatma Gandhi University. He wore a simple traditional outfit. He received huge applause from students and faculty. He posted about it on social media. He did not mention the ceremony happening simultaneously in the capital.

## Two Honours, One Day, One Choice

The timing was not accidental. Mammootty — born Muhammad Kutty Panaparambil Ismail, known to every Malayali on the planet simply as Mammootty — had been announced as a Padma Bhushan recipient months ago, alongside playback singer Alka Yagnik and the late Dharmendra (posthumous Padma Vibhushan). The ceremony date was fixed. The university convocation date was also fixed. He chose the university.

This is the third honorary doctorate of his career. He had previously received similar honours from the University of Kerala and the University of Calicut. "Humbled to have received the Honorary D.Litt. from Mahatma Gandhi University today, presented by the Honourable Governor of Kerala," he wrote afterward. "My gratitude to each and every one of you who stood by my side throughout this memorable journey." The post went viral.

## The Career That Made Both Honours Inevitable

For anyone outside South India — or for any NRI who grew up in a household where Malayalam cinema was the weekend religion — the numbers are staggering. Over 400 films across Malayalam, Tamil, Telugu, Kannada, and Hindi. Three National Film Awards for Best Actor. Eleven Kerala State Film Awards. Sixteen Filmfare Awards South. A career that began in 1971 and, five decades later, shows no sign of fatigue.

His roles in films like *Mathilukal*, *Oru Vadakkan Veeragatha*, *Vidheyan*, and *Ponthan Mada* are considered pillars of Indian parallel cinema. His more commercial work — the CBI series, the Sethurama Iyer franchise — made him a household name beyond the art-house circuit. When you grow up Malayali in America, in the Gulf, in Singapore, in the UK, Mammootty is one of the constants. He is the actor your parents watched and your cousins still watch.

## The Padma Bhushan Isn't Going Anywhere

Mammootty hasn't commented on why he skipped the New Delhi ceremony. He hasn't needed to. The Padma Bhushan is not revoked for non-attendance. The award will be delivered. The recognition stands. What stands more, perhaps, is the image of a man who has been in the film industry for over fifty years choosing to stand in a university auditorium in his home state rather than in the grandest hall in the national capital.

The Padma Awards ceremony on May 25 honoured 131 recipients across arts, medicine, sports, and public service. Hema Malini accepted Dharmendra's posthumous Padma Vibhushan in a moment that made the entire country cry. Alka Yagnik — whose voice soundtracked every NRI wedding playlist for three decades — received her Padma Bhushan in person. R Madhavan and Prosenjit Chatterjee received their Padma Shri awards. Mammootty's chair was empty.

## What the Diaspora Sees

For the Kerala diaspora — one of the most globally dispersed communities in India — Mammootty is not just a film star. He is proof of concept. Proof that you can be rooted in Malayalam, make no serious attempt at Bollywood domination, speak your own language, tell your own stories, and still end up with three National Awards and a Padma Bhushan. The doctorate from Mahatma Gandhi University is, in some ways, a more intimate recognition — the state honouring its own, in its own soil, in its own language.

He is 74. He has three doctorates. He has a Padma Bhushan he hasn't picked up yet. He made over 400 films. And on the day India's President called his name in New Delhi, he was sitting in a university in Kottayam, listening to students clap."""
    },
    {
        "headline": "Shah Rukh Khan Was Missing From IPL 2026 Because He Was on a Beach in South Africa With Deepika Padukone. KKR Got Eliminated.",
        "subheadline": "The Bollywood superstar's absence from Kolkata Knight Riders matches this season wasn't mysterious. He was shooting King — a ₹350 crore action thriller releasing Christmas 2026. A leaked romance sequence went viral. Ranveer Singh was spotted holding baby Dua on set. And KKR finished with 13 points.",
        "slug": "shah-rukh-khan-missing-ipl-2026-kkr-king-south-africa-deepika-ranveer-leaked-video-20260527",
        "category": "entertainment",
        "person_name": "Shah Rukh Khan",
        "pexels_fallback": None,
        "pexels_alt": None,
        "sources": ["https://www.latestly.com/entertainment/bollywood/ipl-2026-why-was-shah-rukh-khan-missing-from-kkr-matches-actors-team-gets-knocked-out-of-playoffs-race-7447315.html", "https://en.wikipedia.org/wiki/King_(2026_film)", "https://sacnilk.com/entertainment/bollywood"],
        "diaspora_angle": "Shah Rukh Khan and KKR are how NRIs stay connected to the IPL from across time zones. His absence this season was felt disproportionately in diaspora WhatsApp groups — not because it changed the cricket, but because it changed the vibe.",
        "tags": ["entertainment", "bollywood", "shah-rukh-khan", "ipl", "kkr", "king-movie", "cricket", "diaspora"],
        "urgency": "medium",
        "score_total": 85,
        "body": """Throughout April and May 2026, Shah Rukh Khan was not in the stands at IPL matches. This is unusual. For two decades, SRK in the stands — jumping, screaming, hugging strangers, occasionally getting banned for confronting security guards — has been as much a part of IPL as the cricket itself. His children Aryan, Suhana, and AbRam have been fixtures. Eden Gardens roars louder when his box is occupied. This year, it was mostly empty. KKR finished with 13 points from 14 matches and didn't make the playoffs. The two facts are not unrelated in the imagination of the fanbase.

## The Reason Was Never a Secret

Shah Rukh Khan has been in South Africa shooting *King*, an action thriller directed by Siddharth Anand, the man who directed *Pathaan*. The film stars Deepika Padukone, Suhana Khan, and — according to sources close to the production — features a cameo by Ranveer Singh. The budget is reportedly ₹350 crore. The release date is locked for December 24, 2026, Christmas Day, the slot that has become SRK's personal property after the one-two punch of *Pathaan* and *Dunki*.

In early May, a video leaked from Cape Town showing Shah Rukh and Deepika shooting a romantic dance sequence on a beach. Director Siddharth Anand posted a request on X asking people to stop sharing it. By then, screenshots had been circulated across every WhatsApp group in existence. In a separate leaked clip, Ranveer Singh — Deepika's husband — was spotted on set holding their daughter Dua Padukone Singh while Deepika filmed with SRK. The internet did what the internet does.

## The One Appearance That Made It Worse

SRK was spotted once — at Eden Gardens in April for a KKR vs Punjab Kings match, accompanied by Suhana. He showed up with a new hair colour that dominated headlines for 48 hours. Then he disappeared again. For the remaining 10+ matches, including the ones where KKR's playoff hopes were mathematically alive, the owner's box was Shah Rukh-less. Sources close to the actor confirmed that the South Africa shoot schedule was non-negotiable.

## KKR's Season Without Their Talisman

The Kolkata Knight Riders were eliminated from IPL 2026 on May 24. They finished with 13 points from 14 matches — not terrible, not competitive. The team couldn't make it past the league stage. As ESPNcricinfo confirmed, they have no remaining matches and are out of the tournament. This is the same franchise that won IPL 2024 in dominant fashion. The drop-off was sharp.

Did SRK's absence cause KKR's elimination? Of course not. Cricket is not won by celebrity presence. But the optics — the richest film star in India choosing a film shoot over his cricket team during its worst season in years — became its own narrative. Fan forums oscillated between understanding ("the man has a ₹350 crore movie to finish") and resentment ("he built this team and now treats it like a side project").

## The NRI Angle Nobody Is Talking About

For the Indian diaspora, Shah Rukh Khan and the IPL exist on the same emotional axis. NRIs wake up at absurd hours to watch IPL matches. They track KKR because SRK owns it and SRK is — for a generation of Indians who grew up abroad — the closest thing to a cultural constant. *Dilwale Dulhania Le Jayenge* played at Maratha Mandir for over 1,200 weeks. *Pathaan* broke records in North American advance bookings. When SRK is in the stands at IPL, it is a visual confirmation that the things you care about from 8,000 miles away still exist, still matter.

His absence this season was felt disproportionately in diaspora WhatsApp groups. Not because it changed the cricket. Because it changed the vibe.

## What Comes Next

*King* releases December 24, 2026. It faces competition from Marvel's *Avengers: Doomsday* and *Dune 3* in the same holiday window. The teaser has already generated massive anticipation. SRK's global fanbase — bolstered by the diaspora — ensures the film will open strong in North America, the UK, the Gulf, and Australia. Whether it was worth missing an entire IPL season for is a question that will be answered at the box office.

The IPL 2026 finale is on May 31. SRK may show up. He may not. KKR won't be playing in it either way."""
    },
    {
        "headline": "R Madhavan Received His Padma Shri on Sunday. He Is Still the Guy From Rehnaa Hai Terre Dil Mein to an Entire Generation of NRIs.",
        "subheadline": "The actor who made Tamil and Hindi audiences claim him as their own stood at Rashtrapati Bhavan at 55, having done more in the last five years than most Bollywood stars manage in twenty.",
        "slug": "r-madhavan-padma-shri-2026-rocketry-ftii-president-rehnaa-hai-terre-dil-mein-nri-20260527",
        "category": "entertainment",
        "person_name": "R. Madhavan",
        "pexels_fallback": None,
        "pexels_alt": None,
        "sources": ["https://www.latestly.com/entertainment/bollywood/padma-awards-2026-hema-accepts-dharmendras-award-mammootty-alka-honoured/", "https://en.wikipedia.org/wiki/R._Madhavan", "https://ptcpunjabi.co.in/entertainment/bollywood/padma-awards-2026-cinema-icons"],
        "diaspora_angle": "Madhavan is the rare Indian actor who is genuinely bilingual (Tamil and Hindi) in a way that feels natural, not performative. For NRIs who switch between languages and identities daily, this resonance runs deep. RHTDM is the liturgical film of diaspora nostalgia.",
        "tags": ["entertainment", "bollywood", "r-madhavan", "padma-awards", "rocketry", "ftii", "tamil-cinema", "diaspora", "nri"],
        "urgency": "medium",
        "score_total": 80,
        "body": """On May 25, R Madhavan stood at Rashtrapati Bhavan in New Delhi and received the Padma Shri from President Droupadi Murmu. He was one of 131 recipients honoured at the 2026 Civil Investiture Ceremony. He was not the biggest name on the list — that distinction belonged to the late Dharmendra (posthumous Padma Vibhushan) and Mammootty (Padma Bhushan). He was not the most dramatic story — that was Hema Malini, accepting her husband's award in a pink saree while Ahana Deol wept. But for a specific generation of Indians — particularly those who grew up straddling two countries, two languages, two identities — Madhavan's Padma Shri carries a weight the others don't.

## The Trajectory That Made This Inevitable

Madhavan — R. Madhavan, or Maddy to his fans — has been in the industry for over 25 years. He debuted in Tamil cinema and Hindi cinema almost simultaneously, which is itself unusual. In Tamil, he became a romantic lead through Mani Ratnam's *Alaipayuthey* (2000). In Hindi, he became *that guy* through *Rehnaa Hai Terre Dil Mein* (2001), a film that flopped at the box office and then became the most rewatched romantic film on every NRI's laptop for the next two decades.

The man's career arc is genuinely strange. He did 3 Idiots with Aamir Khan and became an international name. He did *Tanu Weds Manu* and its sequel and became a comedy star. He did *Irudhi Suttru* (Tamil) / *Saala Khadoos* (Hindi) and became a gritty sports drama actor. Then he disappeared for a few years and came back as the director, producer, writer, and star of *Rocketry: The Nambi Effect* — a biographical film about ISRO scientist Nambi Narayanan that he took to the Cannes Film Festival in 2022.

## Rocketry Changed Everything

*Rocketry* was not a box office blockbuster. It didn't need to be. Madhavan spent years making it — learning rocket science, meeting Narayanan, shooting in multiple countries, doing it in three languages simultaneously (Hindi, Tamil, English). He directed it himself because no one else would. He acted in it because the subject demanded a performance that came from genuine obsession, not professional commitment. The film was selected for a special screening at Cannes. Shah Rukh Khan and Suriya made cameo appearances. Critics were astonished.

The film told the story of an Indian scientist who was falsely accused of espionage, imprisoned, and then exonerated — a man whose work was essential to India's space programme but who was destroyed by institutional paranoia. For the Indian diaspora, Narayanan's story resonated on multiple frequencies: the brilliance of Indian scientists, the cruelty of Indian bureaucracy, and the determination of one man to clear his name.

## FTII President: The Unexpected Turn

In 2024, Madhavan was appointed President of the Film and Television Institute of India (FTII) in Pune — the institution that produced Naseeruddin Shah, Shabana Azmi, Jaya Bachchan, and generations of India's finest filmmakers. The appointment was controversial in some quarters (Bollywood actor runs a venerated institution?) and welcomed in others (finally, someone who understands both commercial and artistic cinema).

He has held the position while continuing to act. He has navigated the politics of institutional leadership while maintaining a film career. He has done this quietly, without the drama that typically accompanies Bollywood figures in government-adjacent roles.

## The NRI Film Star

Here is what makes Madhavan different from almost every other Indian film star of his generation: he is genuinely bilingual in a way that doesn't feel performative. He didn't "cross over" from Tamil to Hindi or vice versa. He simply exists in both industries as if the border between them doesn't matter. For NRIs — who often exist in a similar state of cultural bilingualism, switching between languages and identities — this is deeply relatable.

*Rehnaa Hai Terre Dil Mein* is the patron saint of NRI nostalgia. It is the film that plays at every desi house party, every college cultural event, every "Indian Night" at every university in the Western world. The songs — "Zara Zara," "Sach Keh Raha Hai" — are liturgical. Madhavan's Maddy is the ideal NRI boyfriend: earnest, slightly messy, incapable of deception, and deeply romantic. That this same man went on to direct a film about rocket science and run FTII is the kind of career evolution that makes you reconsider what Indian film stars are capable of.

## The Ceremony

The Padma Awards ceremony on May 25 was emotional across the board. Dharmendra's posthumous Padma Vibhushan, accepted by Hema Malini, was the moment that broke the nation. Mammootty's Padma Bhushan was announced but the actor was notably absent — he was receiving a doctorate in Kerala. Alka Yagnik received her Padma Bhushan in person, a poignant recognition given her publicly disclosed hearing loss. Prosenjit Chatterjee, the giant of Bengali cinema, received his Padma Shri for four decades of work.

Madhavan stood among them. Not the loudest name. Not the most dramatic story. But perhaps the one that will mean the most to the kid in New Jersey who watches *Rehnaa Hai Terre Dil Mein* every year on the anniversary of the day they moved to America. The Padma Shri is the state recognising what the diaspora already knew: this man matters."""
    }
]

# ── Main execution ─────────────────────────────────────────────

def publish_article(article):
    art_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    print(f"\n{'='*60}")
    print(f"Publishing: {article['headline'][:80]}...")
    print(f"  Slug: {article['slug']}")
    print(f"  ID: {art_id}")
    
    # Source image
    print("  Sourcing image...")
    image_url, attribution = source_image(
        person_name=article.get('person_name'),
        article_id=art_id,
        slug=article['slug'],
        fallback_pexels_query=article.get('pexels_fallback'),
        fallback_pexels_alt=article.get('pexels_alt')
    )
    
    # Build sources JSON
    sources_json = json.dumps([{"url": s, "name": s.split('/')[2] if '/' in s else s} for s in article['sources']])
    
    # Validate article quality
    body = article['body']
    word_count = len(body.split())
    headline_len = len(article['headline'])
    sub_len = len(article['subheadline'])
    
    print(f"  Word count: {word_count}")
    print(f"  Headline length: {headline_len}")
    print(f"  Subheadline length: {sub_len}")
    
    if word_count < 400:
        print(f"  ✗ REJECTED: body too short ({word_count} words, minimum 400)")
        return None
    if headline_len < 20 or headline_len > 250:
        print(f"  ⚠ Headline length warning: {headline_len}")
    if sub_len < 15:
        print(f"  ✗ REJECTED: subheadline too short ({sub_len} chars)")
        return None
    
    payload = {
        "id": art_id,
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "body": body,
        "slug": article['slug'],
        "category": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": sources_json,
        "image_url": image_url,
        "image_attribution": attribution,
        "diaspora_angle": article.get('diaspora_angle', ''),
        "vertical": "entertainment",
        "tags": article.get('tags', ["entertainment", "bollywood", "diaspora"]),
        "urgency": article.get('urgency', 'medium'),
        "score_total": article.get('score_total', 75),
    }
    
    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published successfully!")
        return art_id
    else:
        print(f"  ✗ Failed to publish")
        return None

# Run
published = []
for art in articles:
    aid = publish_article(art)
    if aid:
        published.append(aid)
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {len(published)}/{len(articles)} articles.")
for pid in published:
    print(f"  - {pid}")
