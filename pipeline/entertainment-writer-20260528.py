#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 batch"""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.replace('export ', '').strip()
            v = v.strip().strip('"').strip("'")
            os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Wikipedia image fetcher ──
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
    """Fetch an image from Pexels. Use curl since Python urllib gets 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3'
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that URL returns an actual image > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source detected: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={ct}, size={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert into Supabase and return the row."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def sb_patch(table, match, updates):
    """Patch rows in Supabase."""
    params = '&'.join(f'{k}={v}' for k, v in match.items())
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=updates,
        timeout=30
    )
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
        return False


# ── Articles ──
articles = [
    {
        "headline": "Aamir Khan Will Play Lala Amarnath. Rajkumar Hirani Will Direct the 3 Idiots Sequel. Both Films Start Within Months of Each Other.",
        "subheadline": "Twenty-five years after Lagaan, Aamir reunites with Ashutosh Gowariker for a cricket film rooted in Partition. Then he walks straight into the most anticipated Bollywood sequel in years.",
        "slug": "aamir-khan-lala-amarnath-biopic-ashutosh-gowariker-3-idiots-sequel-rajkumar-hirani-nri-20260528",
        "category": "entertainment",
        "person_name": "Aamir Khan",
        "pexels_query": None,
        "pexels_fallback": None,
        "sources": ["Variety India via Sacnilk", "Bollywood Hungama"],
        "body": """Twenty-five years after a village cricketer named Bhuvan changed the trajectory of Indian cinema at the Oscars, Aamir Khan is going back to the pitch. Only this time, the story is real.

According to a Variety India report confirmed by multiple trade sources, Khan will begin shooting in October 2026 for director Ashutosh Gowariker's untitled sports biopic about Lala Amarnath — arguably the most important cricketer in the history of Indian independence. The film centers on the 1952 India-Pakistan Test series, the first bilateral series between the two nations after Partition, and on Amarnath's relationship with Pakistan captain Abdul Hafeez Kardar — two men who played together before a border divided them.

## Why This Story Matters

For anyone who grew up in the subcontinent, Lala Amarnath is not just a cricketer. He scored India's first-ever Test century (against England at Bombay, 1933), captained the side, and became the unwitting symbol of a country trying to prove itself on the world stage. His friendship with Kardar — a man who literally switched national teams because of Partition — is the kind of story that only the subcontinent produces.

The project is being mounted at massive scale. Rajkumar Hirani and writer Abhijat Joshi are reportedly involved in the screenplay, which is significant: Hirani's involvement in a sports period drama is new territory for the filmmaker best known for comedies with a conscience.

## The 3 Idiots Factor

The Gowariker project also has a direct impact on the most anticipated sequel in Bollywood: 3 Idiots 2. According to reports, Hirani's follow-up — which is expected to reunite Aamir Khan, R. Madhavan, and Sharman Joshi — will now go on floors in mid-2027, pushed back from earlier schedules. The delay is attributed to script readiness rather than any creative disagreement.

The sequel is reported to feature a significant time jump and may include Vicky Kaushal in a prominent role. Kaushal, who is currently wrapping work on Sanjay Leela Bhansali's Love and War, has blocked an 18-month window starting June 2026 for his own epic, Mahavatar, in which he plays the immortal sage-warrior Parashurama.

## The Diaspora Angle

For the Indian diaspora, the Lala Amarnath story has particular resonance. The 1952 series was followed intensely by Indians abroad — many of them first-generation emigrants who had lived through Partition themselves. The narrative of two friends separated by a border, meeting again on a cricket field, is the kind of story that cuts across the "NRI nostalgia" genre and into something genuinely universal.

And then there's the sequel factor. 3 Idiots is arguably the single most-watched Indian film among NRIs under 40. The original grossed over ₹400 crore worldwide in 2009 — a number that was nearly unimaginable at the time — and became a cultural reference point for an entire generation of diaspora students navigating the expectations of Indian families.

## What Comes Next

Aamir Khan is now looking at three back-to-back films starting late 2026 — the most prolific stretch of his career since the early 2000s. After the commercial disappointment of Laal Singh Chaddha (2022) and the underwhelming reception of his son Junaid Khan's debut (which he produced), this feels like a deliberate reset. The message is clear: one of Bollywood's most methodical actors is not in retirement mode. He's loading up.

The Gowariker film does not yet have an official title or release date. The 3 Idiots sequel is expected in late 2028 at the earliest."""
    },
    {
        "headline": "Drishyam 3 Just Crossed ₹200 Crore Worldwide. Nobody Needed a Third Film. Everybody Watched Anyway.",
        "subheadline": "Mohanlal's franchise closer becomes the first South Indian film of 2026 to hit $10 million overseas. Kerala led the charge, but it was the Gulf and North America that turned it into history.",
        "slug": "drishyam-3-200-crore-worldwide-mohanlal-first-south-indian-10-million-overseas-nri-20260528",
        "category": "entertainment",
        "person_name": "Mohanlal",
        "pexels_query": None,
        "pexels_fallback": None,
        "sources": ["Cinema Express", "Sacnilk", "Pinkvilla"],
        "body": """When Jeethu Joseph first told the story of Georgekutty — a cable TV operator in Kerala who outwits the police to protect his family — nobody expected a franchise. Drishyam (2013) was a standalone thriller, a tight Malayalam film that happened to become the most remade Indian movie of the decade. Drishyam 2 arrived during the pandemic, went straight to OTT, and proved that the story still had legs. And now Drishyam 3, which many questioned the need for, has crossed ₹200 crore worldwide in just seven days.

Mohanlal is now the only Malayalam actor with three ₹200 crore films. Let that sink in.

## The Numbers Tell One Story

The film opened to ₹43.50 crore worldwide on its first day — the second-biggest opening for a Malayalam film ever, behind only L2: Empuraan. By Day 5, it had crossed ₹157 crore, setting a record as the first Malayalam film to gross ₹15 crore on a non-holiday Monday.

Here's the breakdown that matters:
- **India gross (Week 1):** ₹94.91 crore
- **Kerala alone:** ₹62.65 crore
- **Overseas:** ₹103+ crore (more than the domestic total)
- **First South Indian film of 2026 to cross $10 million overseas**

The overseas number is staggering. For a Malayalam-language thriller — not a pan-India blockbuster, not a Hindi-dubbed tentpole — to earn more abroad than at home is almost unprecedented. The Gulf, where the Malayali diaspora is enormous, drove the bulk of it. But North America, the UK, and Australia all delivered significantly above tracking.

## The Audience That Showed Up

The Drishyam franchise has always been an audience film, not a critic's film. The third installment received mixed reviews — some called it unnecessary, others felt the plotting strained under the weight of expectations. None of that mattered. The Mohanlal factor, combined with a franchise that has genuine emotional equity across at least four language markets, overrode the skepticism.

What's particularly notable is the cross-linguistic performance. The film released simultaneously in Malayalam, Tamil, Telugu, and Kannada. Karnataka delivered ₹11.59 crore in Week 1 — remarkable for a film that isn't a Kannada production. Tamil Nadu added ₹7.25 crore. These aren't massive numbers individually, but they reflect a franchise that has genuinely crossed regional boundaries through its story rather than its star.

## What It Means for NRIs

If you're in the diaspora and you haven't seen Drishyam 3 yet, you're running out of excuses. The film is playing in most North American and UK markets, and a digital premiere on Amazon Prime Video is expected in late June 2026.

But the bigger story isn't about one film. It's about what Malayalam cinema has become in the overseas market. In a month where Bollywood's Hindi releases (Pati Patni Aur Woh Do, Chand Mera Dil) collectively underperformed, a Malayalam thriller outearned all of them combined — and did it in half the screens.

## The Competition Ahead

Drishyam 3's theatrical momentum now faces a test: Kattalan, the Antony Varghese-starrer connected to the Marco universe, opened on the same day this story is published. Whether Drishyam 3 can hold screens in the second week against fresh competition will determine if it reaches ₹250 crore worldwide — a number that would make it one of the top five Malayalam grossers of all time.

The Hindi remake rights are reportedly in development, with a distinct narrative planned rather than a direct translation. If it happens, it would be the third Hindi Drishyam film — a franchise within a franchise, built on the back of a cable TV operator from Kerala who refused to tell the truth."""
    },
    {
        "headline": "Salman Khan Picked Up the Phone on Both Sides of the Don 3 War. Here's What He Said.",
        "subheadline": "As FWICE's non-cooperation directive against Ranveer Singh divides the industry, Bollywood's most powerful mediator steps in to broker a truce between Singh and Farhan Akhtar.",
        "slug": "salman-khan-mediates-ranveer-singh-farhan-akhtar-don-3-fwice-truce-nri-20260528",
        "category": "entertainment",
        "person_name": "Salman Khan",
        "pexels_query": None,
        "pexels_fallback": None,
        "sources": ["Bollywood Hungama", "The Daily Jagran"],
        "body": """The Don 3 saga just got its most interesting character. It's not Ranveer Singh. It's not Farhan Akhtar. It's Salman Khan — who, according to Bollywood Hungama, has personally called both sides and told them to sort it out before the industry does it for them.

## The Backstory

If you've been following the Don 3 implosion, here's where we are: Ranveer Singh walked away from the film three weeks before an international shoot, reportedly citing creative differences with the script. Excel Entertainment (Farhan Akhtar and Ritesh Sidhwani's production house) claims it spent ₹45 crore in pre-production. FWICE — the Federation of Western India Cine Employees, the industry's oldest film union — issued a non-cooperation directive against Ranveer, effectively telling the entire workforce not to work with him until the dispute is resolved.

The directive isn't technically a ban (FWICE was careful to clarify that), but the practical effect is the same. If crew members follow it, Ranveer can't shoot in Mumbai.

## What Salman Did

According to sources, Salman Khan — who is close to both Ranveer and the Akhtar family — initiated separate conversations with both camps. A source told Bollywood Hungama: "He explained to Farhan about creative differences being a common thing in the industry for decades, and he also had a long chat with Ranveer, understanding his stance. He is playing the cupid to ensure that no one feels sabotaged."

The key detail: Salman reportedly told both parties to think of themselves as "one industry" and to consider working together on a different project once the heat dissipates. He also specifically asked them not to involve third parties — including himself — in the formal resolution.

This is classic Salman Khan dispute resolution: step in, make your position known, then step back and let the parties do the actual work. It's the same approach he took during the Arijit Singh–Salman beef years ago, and during the Vivek Oberoi phase. The man doesn't arbitrate; he applies gravitational pressure.

## The Industry Response

The Don 3 conflict has split Bollywood in ways that feel genuinely uncomfortable. Rakhi Sawant (inevitably) weighed in publicly, defending Ranveer and telling FWICE to "try banning Salman Khan and see what happens." Chunky Panday shared his own experience of being banned decades ago. Manoj Bajpayee expressed hope that the matter would be resolved. Directors and editors have criticized FWICE's selective enforcement.

Meanwhile, Ranveer's team reportedly made a peace offer early on — ₹10 crore upfront plus a ₹25 crore discount on his next project with Excel. The offer was rejected. Farhan Akhtar's position, according to insiders, is that the losses to Excel exceed any compensation Ranveer has offered, and that the precedent of an A-lister walking out mid-production without consequences would be devastating for the industry.

## Why This Matters for NRIs

On the surface, this is Bollywood gossip. But it raises a question that the diaspora audience — the one paying $25 per ticket in New Jersey and Fremont — should care about: what happens when the biggest names in the industry can't resolve disputes without union intervention?

FWICE's directive lacks legal enforcement power. It's a moral pressure tool. If Ranveer simply moves his production to Hyderabad or starts a project with a South Indian studio (which he can), the directive becomes meaningless. The fact that Salman felt the need to intervene suggests that the people closest to both camps believe this could escalate further.

## What's Next

Both Farhan and Ranveer have reportedly taken Salman's words seriously. Ranveer's next confirmed project is Pralay, Jai Mehta's ₹300 crore post-apocalyptic thriller, which begins filming in August 2026 with Kalyani Priyadarshan making her Hindi debut. The film is proceeding regardless of the FWICE directive, suggesting the crew has not universally complied.

Don 3 itself remains in limbo. No new lead has been announced. The ₹45 crore in pre-production costs sits on Excel's books. And somewhere in Mumbai, Salman Khan has put down the phone and moved on to his next problem — which, knowing Salman, probably involves a farmhouse and a painting."""
    }
]

# ── Publish ──
published = 0
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:80]}...")
    
    # Image sourcing — Wikipedia first for person articles
    img_url = None
    if article.get('person_name'):
        print(f"  Trying Wikipedia for '{article['person_name']}'...")
        img_url = fetch_wikipedia_person_image(article['person_name'])
    
    if not img_url and article.get('pexels_query'):
        print(f"  Trying Pexels for '{article['pexels_query']}'...")
        img_url = fetch_pexels_image(article['pexels_query'], article.get('pexels_fallback'))
    
    # Validate
    if img_url:
        if not validate_image_url(img_url):
            print(f"  ✗ Image validation failed, proceeding without image")
            img_url = None
    
    # Build article record
    now = datetime.now(timezone.utc).isoformat()
    # Determine image attribution
    img_attr = None
    if img_url and ("wikimedia" in img_url.lower() or "wikipedia" in img_url.lower()):
        img_attr = "Wikimedia Commons"
    
    record = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": "entertainment",
        "body": article["body"].strip(),
        "sources": json.dumps(article["sources"]),
        "status": "published",
        "published_at": now,
        "image_url": img_url,
        "image_attribution": img_attr
    }
    
    # Word count check
    word_count = len(article["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ BELOW 400 WORD MINIMUM — skipping")
        continue
    
    # Headline length check
    hl_len = len(article["headline"])
    print(f"  Headline length: {hl_len}")
    
    # Insert
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
