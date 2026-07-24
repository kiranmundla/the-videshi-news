#!/usr/bin/env python3
"""Entertainment writer - 2026-05-27 evening batch"""

import json, os, sys, uuid, re, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import urllib.parse, urllib.request

def sb_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

def sb_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=sb_headers(), method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗ Insert error: {e.code} {e.read().decode()[:300]}")
        return None
    except Exception as e:
        print(f"  ✗ Insert exception: {e}")
        return None

def sb_patch(table, filter_str, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}"
    body = json.dumps(data).encode()
    headers = sb_headers()
    req = urllib.request.Request(url, data=body, headers=headers, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ✗ Patch error: {e}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        req = urllib.request.Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            # Prefer originalimage for higher res, fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that URL returns an image with Content-Length > 5000."""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method='HEAD', headers={
            'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            ct = resp.headers.get('Content-Type', '')
            cl = int(resp.headers.get('Content-Length', '0') or '0')
            if 'image' in ct and cl > 5000:
                return True
            # Sometimes HEAD doesn't return Content-Length; try GET
            if 'image' in ct and cl == 0:
                return True  # Trust it if content-type is image
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
        # Try GET as fallback
        try:
            req2 = urllib.request.Request(url, headers={
                'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'
            })
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                data = resp2.read(10000)
                if len(data) > 5000:
                    return True
        except:
            pass
    return False

# Check for banned image sources
def is_banned_source(url):
    if not url:
        return True
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

# ─── ARTICLES ───

articles = []

# ── Article 1: FWICE vs Ranveer Singh ──
art1_id = str(uuid.uuid4())
art1 = {
    "id": art1_id,
    "headline": "Bollywood's Oldest Film Union Just Told Ranveer Singh No One Will Work With Him. He Succeeded Shah Rukh Khan as Don. Now He Can't Make a Film.",
    "subheadline": "FWICE issues a non-cooperation directive after Ranveer walked out of Don 3 three weeks before the shoot. Farhan Akhtar and Ritesh Sidhwani claim ₹45 crore in pre-production losses. The actor offered ₹35 crore. They said no.",
    "slug": "fwice-non-cooperation-ranveer-singh-don-3-farhan-akhtar-45-crore-bollywood-ban-20260527",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "https://www.livemint.com/entertainment/fwice-bans-ranveer-singh-amid-don-3-fallout-and-dispute-with-farhan-akhtar-11779722131684.html",
        "https://www.storyboard18.com/photos/trending/ranveer-singh-and-farhan-akhtar-fallout-explained-inside-the-don-3-controversy-99220.htm",
        "https://www.pinkvilla.com/entertainment/news/ranveer-singh-hit-with-fwice-ban-no-member-of-the-film-body-will-work-with-him-says-president"
    ]),
    "body": """The Federation of Western India Cine Employees — FWICE, the sixty-eight-year-old umbrella body of over thirty film worker unions — has issued a Non-Cooperation Directive against Ranveer Singh. The directive tells every camera technician, spot boy, costume designer, editor, and makeup artist registered under FWICE to refuse to work with one of Bollywood's biggest stars until further notice.

The trigger is Don 3. Ranveer was announced as the new face of the franchise in 2023, inheriting a role that had passed from Amitabh Bachchan to Shah Rukh Khan. Farhan Akhtar, who directed the 2006 and 2011 installments, was returning to direct. Excel Entertainment, co-founded by Akhtar and Ritesh Sidhwani, had been in pre-production for months.

## Three Weeks Before the Shoot

According to the complaint filed by Akhtar with the Indian Film & Television Directors' Association on April 11, 2026, Ranveer withdrew from the project "at the very last moment, just three weeks before our unit was scheduled to depart for a shoot." By that point, Excel Entertainment claims to have spent approximately ₹45 crore on pre-production — locations scouted, travel arranged, crew hired, schedules locked for hundreds of workers.

FWICE registered the complaint and sent three formal notices to Ranveer over the next month: April 22, April 30, and May 13. The actor did not respond to any of them. He replied only after FWICE announced plans to address the matter publicly.

## The Actor's Response

Through his legal team, Ranveer argued that FWICE "would not be the appropriate forum" for the dispute and that the issues were "contractual in nature" requiring adjudication in a proper legal forum.

His spokesperson later issued a softer statement: "Ranveer Singh holds the highest regard for the film fraternity and for everyone associated with the Don franchise. Throughout the recent developments surrounding Don 3, he has consciously chosen to maintain silence, believing that professional discussions and personal equations are best handled with dignity, maturity and mutual respect."

Reports suggest Ranveer offered to return his ₹10 crore signing amount. Separately, he reportedly proposed a ₹35 crore settlement. Excel Entertainment declined both, insisting on the full ₹45 crore.

## What Went Wrong

Industry reports point to creative disagreements. Ranveer reportedly pushed for a darker, more aggressive interpretation of the Don character — heavier language, more intensity. Farhan Akhtar wanted to preserve the suave, witty tone that defined his version of the franchise. Repeated requests for script revisions deepened the friction. The absence of a final locked script may have been the breaking point.

## Can FWICE Actually Enforce This?

Legally, no. FWICE's non-cooperation directives carry no statutory authority. They are registered under the Trade Unions Act of 1926 and can negotiate wages, mediate disputes, and organize collective action — but they cannot legally prevent a producer from hiring someone.

What they can do is make things very difficult. If crew members collectively refuse to work on a Ranveer Singh film, productions become logistically impossible. "Ranveer Singh is a superstar," FWICE president B.N. Tiwari told reporters. "But that doesn't mean anyone is above the rules."

FWICE has done this before. In 2019, they issued a directive against Punjabi singer Mika Singh for performing in Pakistan; it was revoked after he apologized. Last year, they banned all Pakistani artists following the Pahalgam attack.

## The Diaspora Angle

For NRI audiences, this matters because it directly impacts when — or whether — they will see a new Don film. The franchise has been one of Bollywood's most reliable draws overseas. Don 2 did exceptional business in international markets, and a Ranveer-led Don 3 was positioned as a global tentpole.

Instead, the franchise is in limbo. Excel Entertainment has not announced a replacement. The ₹45 crore dispute remains unresolved. And the question of whether a trade body can effectively blacklist a star worth hundreds of crores to the industry is now being tested in real time.

The directive remains in effect. FWICE says the door is open for Ranveer to appear before them and present his side. So far, he has not walked through it.""",
    "image_url": None,
    "image_attribution": None
}
articles.append(art1)

# ── Article 2: Kangana Defends Aishwarya at Cannes ──
art2_id = str(uuid.uuid4())
art2 = {
    "id": art2_id,
    "headline": "Kangana Ranaut Defended Aishwarya Rai at Cannes. These Two Women Have Spent a Decade Being Pitted Against Each Other. The Internet Had No Script for This.",
    "subheadline": "Aishwarya Rai walked the Cannes red carpet for the 24th time. Trolls mocked her appearance. Kangana Ranaut posted an Instagram Story calling her 'glorious' and told critics to get used to seeing older women. Bollywood's most unlikely alliance just happened.",
    "slug": "kangana-ranaut-defends-aishwarya-rai-cannes-2026-ageism-trolling-instagram-24th-appearance-20260527",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "https://www.filmibeat.com/bollywood/news/2026/cannes-2026-kangana-ranaut-slams-trolls-mocking-aishwarya-rai-bachchan-s-look-get-used-to-seeing-014-517897.html",
        "https://www.bollywoodhungama.com/news/kangana-ranaut-defends-aishwarya-rai-bachchan-amid-cannes-criticism",
        "https://www.filmfare.com/photos/aaradhya-bachchan-reaction-aishwarya-rai-cannes"
    ]),
    "body": """Aishwarya Rai Bachchan walked the Cannes Film Festival red carpet for the twenty-fourth time this year. She is fifty-two years old. She wore a sculpted blue mermaid-style gown designed by Amit Aggarwal. She looked like herself — which is to say, like a woman who has been attending Cannes since 2002, who has walked every iteration of the red carpet in every possible silhouette, and who long ago stopped needing anyone's permission to be there.

The internet, predictably, had opinions. Trolls posted body-shaming comments. Ageist remarks circulated on Instagram and X. The tone was familiar: an aging actress clinging to relevance, a woman who should know better, a former beauty queen who no longer looks twenty-five.

## The Unlikely Defender

Then Kangana Ranaut posted an Instagram Story.

If you follow Bollywood even casually, you know why this is remarkable. Kangana and Aishwarya have spent the better part of a decade being positioned — by the media, by publicists, by the architecture of celebrity feuds — as adversaries. Kangana has been Bollywood's most vocal critic of the industry's power structures, and Aishwarya, married into the Bachchan family, has been one of its most visible symbols.

But on May 24, Kangana shared a photo of Aishwarya's Cannes look and wrote: "Fashion and style is a self expression, it is one's own interpretation of life and their attitude, no woman owes anything to anyone, Ash looks great!! Those of you who want to see her any other way, why don't you show what you got?? She is not here to please you, she is glorious, if you are not used to seeing older women on red carpets, get used to them now."

## Twenty-Four Years at Cannes

Aishwarya's relationship with Cannes predates Instagram, X, smartphones, and the very concept of going viral. She first attended as a L'Oréal Paris ambassador in 2002, three years after winning Miss World, the same year she became the first Indian woman on the TIME 100 list. She has returned every year since, through pregnancies, personal tragedies, career pivots, and an industry that perpetually asks women to justify their presence.

This year, her daughter Aaradhya — now fourteen — accompanied her. A viral video showed Aaradhya beaming as her mother signed autographs for fans outside the Palais des Festivals. In a press interaction, Aishwarya offered advice to aspiring actresses: prioritize self-discovery, avoid overthinking external pressures, remain a lifelong learner.

Her stylist Mohit Rai told reporters he wanted "something timeless, beautiful and iconic" for this appearance. Across the week, she wore a pastel crystal gown with a feathered cape, a sculptural white ensemble with 3D floral designs by Rahul Mishra, and the sapphire Aggarwal gown that drew the loudest reactions — both admiring and cruel.

## The Cannes Pattern

Every year, Indian celebrities at Cannes face a cycle that is now almost ritualistic: the walk, the photos, the praise, the backlash, the discourse about whether Indian stars "belong" at a European film festival primarily because of a cosmetics sponsorship.

What makes this year different is not the cycle itself but who broke it. Kangana Ranaut — the politician, the provocateur, the woman who once called Bollywood's A-list "movie mafia" — stood up for the industry's most establishment figure. She did it not in defense of fashion or celebrity but against the specific cruelty of telling a fifty-two-year-old woman she has no business being on a red carpet.

## Why It Matters for NRIs

For the Indian diaspora, Aishwarya is not just an actress. She is a reference point — the face that launched a thousand "Do you know Aishwarya Rai?" conversations with non-Indian colleagues, the bridge between Bollywood and the world before Bollywood had a global audience. The fact that she is still walking Cannes at fifty-two, and that the harshest criticism comes from Indian social media rather than from the French press, says something about what the diaspora already knows: the standards applied to Indian women by Indian audiences are the most unforgiving ones in the room.

Kangana's defense, whatever its motivations, named that dynamic. And for one news cycle, two women who have never publicly agreed on anything agreed on the most basic thing: a woman at Cannes does not owe you youth.""",
    "image_url": None,
    "image_attribution": None
}
articles.append(art2)

# ── Article 3: Aamir Khan on Ek Din Failure ──
art3_id = str(uuid.uuid4())
art3 = {
    "id": art3_id,
    "headline": "Aamir Khan Says a Film Flopping Feels Like Losing a Child. His Son's Film Just Made ₹5.44 Crore. He Produced It.",
    "subheadline": "Ek Din opened advance bookings 39 days early — a Bollywood record. It starred Sai Pallavi in her Hindi debut. It earned ₹1 crore on day one. Aamir says he goes into depression for two to three months after every flop. This one had his son's name on it.",
    "slug": "aamir-khan-ek-din-flop-depression-losing-child-junaid-khan-sai-pallavi-box-office-20260527",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "https://www.newsbeep.com/ie/458632/",
        "https://www.filmfare.com/features/ek-din-opens-advance-bookings-39-days-early",
        "https://www.bollywoodhungama.com/news/ek-din-39-day-advance-booking"
    ]),
    "body": """Aamir Khan does not believe in pretending a failure did not happen. In a recent conversation with Zee Music Company, the actor — Bollywood's self-appointed perfectionist, the man who makes one film every three years and treats each one like an existential project — said this about what happens when it does not work:

"I go into depression for two to three months when a film doesn't work. A film is like your child. When it doesn't work or gets rejected, it is very painful. I feel it's important to mourn your losses. When your film doesn't work, it is like losing a child, so you should cry over it, give it time, so that it is out of your system and helps you move on."

He was speaking in general terms, but the timing made the subtext impossible to miss. Ek Din, produced by Aamir and starring his son Junaid Khan opposite Sai Pallavi, had just finished its theatrical run with a worldwide gross of ₹5.44 crore — a commercial disaster by any standard, and a particularly painful one for a film that had tried everything right.

## The 39-Day Experiment

Ek Din opened advance bookings thirty-nine days before its May 1 release — the earliest in Bollywood history. The strategy was deliberate. Rather than rely on a big opening weekend, the team tried to build anticipation slowly, letting word of mouth carry the film. Screenings were limited to twenty cities initially. The marketing leaned on the film's emotional core rather than spectacle.

It was, in theory, exactly the kind of release strategy that the industry has been calling for: patient, audience-first, designed for a film that did not have a ₹200 crore action set-piece to sell. But audiences did not show up. Day one collected ₹1 crore. Eleven days in, the India total sat at ₹4.25 crore.

## Sai Pallavi's Hindi Debut

Part of the anticipation was Sai Pallavi. The actress, already a star in Tamil and Telugu cinema — Premam, Fidaa, Jai Bhim — was making her Bollywood debut. The pairing with Junaid Khan, who had debuted the previous year in Maharaj to warmer reception, was positioned as a fresh combination with old-school appeal. Director Sunil Pandey adapted the 2016 Thai film One Day into a romantic drama about two people who share a single significant encounter.

Critics were kinder than audiences. Reviews noted emotional depth and genuine performances, particularly from Pallavi. But a film needs bodies in seats to survive its first week, and Ek Din did not have them. Competition from Raja Shivaji and the lingering pull of Dhurandhar 2 left no room in multiplexes.

## The Father's Reckoning

What makes this story unusual is not that a Bollywood film flopped — roughly eighty percent of them do — but that the producer who flopped is also the father of the lead actor, and he is talking about it with the candor of a man who has decided transparency is the only dignified option.

"When a film flops, it breaks my heart," Aamir continued. "At the end of the day, we make a film for our audience. When they buy a ticket and come to theaters to have a good time, and when they don't like a film, then there is a flaw in your work; the audience never decides intentionally to go and watch a bad film."

He then revealed that several of his most acclaimed films — Delhi Belly, Taare Zameen Par, Laapataa Ladies — had terrible first cuts that required extensive reworking. "You can always correct a film if you want to; it requires lots of endurance, stamina, patience, and passion."

Junaid himself acknowledged his father's struggle in an interview the previous week, saying Aamir was having difficulty processing Ek Din's performance. The younger Khan has not distanced himself from the result; if anything, the shared vulnerability has humanized a family name that Indian audiences have spent decades regarding with a mix of reverence and expectation.

## The NRI Audience Question

For diaspora audiences, Ek Din was exactly the kind of film they claim to want: small, sincere, romance-driven, anchored by two genuinely talented actors. It was not a franchise sequel. It was not a jingoistic spectacle. It was not a three-hour musical extravaganza. It was a film about two people, and it lasted eleven days in theaters.

The uncomfortable truth is that the Indian audience — at home and abroad — keeps saying it wants more of these films while buying tickets to Dhurandhar 2. Aamir Khan knows this. He has spent his career trying to bridge the gap between what audiences say and what they do. This time, the gap won.

"For me, real success is to manage to make what you set out to make," he said. By that measure, Ek Din might be a success. By every other measure, it is the thing Aamir compares to losing a child. And he is letting himself grieve it in public, which is more than most Bollywood stars would ever do.""",
    "image_url": None,
    "image_attribution": None
}
articles.append(art3)

# ─── IMAGE SOURCING ───

print("\n=== Image Sourcing ===\n")

# Article 1: Ranveer Singh
print("Article 1: Ranveer Singh / Don 3")
img1 = fetch_wikipedia_person_image("Ranveer Singh")
if not img1:
    img1 = fetch_wikipedia_person_image("Ranveer Singh (actor)")
if img1 and not is_banned_source(img1):
    articles[0]["image_url"] = img1
    articles[0]["image_attribution"] = "Wikimedia Commons"
else:
    img1 = fetch_pexels_image("Bollywood film set production", "Indian cinema spotlight")
    if img1 and not is_banned_source(img1):
        articles[0]["image_url"] = img1
        articles[0]["image_attribution"] = "Pexels"

# Article 2: Aishwarya Rai
print("\nArticle 2: Aishwarya Rai / Cannes")
img2 = fetch_wikipedia_person_image("Aishwarya Rai")
if not img2:
    img2 = fetch_wikipedia_person_image("Aishwarya Rai Bachchan")
if img2 and not is_banned_source(img2):
    articles[1]["image_url"] = img2
    articles[1]["image_attribution"] = "Wikimedia Commons"
else:
    img2 = fetch_pexels_image("Cannes film festival red carpet", "film festival gala")
    if img2 and not is_banned_source(img2):
        articles[1]["image_url"] = img2
        articles[1]["image_attribution"] = "Pexels"

# Article 3: Aamir Khan
print("\nArticle 3: Aamir Khan / Ek Din")
img3 = fetch_wikipedia_person_image("Aamir Khan")
if img3 and not is_banned_source(img3):
    articles[2]["image_url"] = img3
    articles[2]["image_attribution"] = "Wikimedia Commons"
else:
    img3 = fetch_pexels_image("Indian cinema theater empty seats", "Bollywood film screening")
    if img3 and not is_banned_source(img3):
        articles[2]["image_url"] = img3
        articles[2]["image_attribution"] = "Pexels"

# ─── VALIDATE IMAGES ───
print("\n=== Validating Images ===\n")
for i, art in enumerate(articles):
    url = art.get("image_url")
    if url:
        if validate_image_url(url):
            print(f"  ✓ Article {i+1}: Image OK")
        else:
            print(f"  ✗ Article {i+1}: Image validation failed, removing")
            art["image_url"] = None
            art["image_attribution"] = None
    else:
        print(f"  ⚠ Article {i+1}: No image found")

# ─── PUBLISH ───
print("\n=== Publishing ===\n")
for i, art in enumerate(articles):
    print(f"Publishing article {i+1}: {art['headline'][:60]}...")
    result = sb_insert("p2_articles", art)
    if result:
        print(f"  ✓ Published: {art['slug']}")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print("\n=== Done ===")
