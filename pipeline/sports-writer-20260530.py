#!/usr/bin/env python3
"""
Sports Writer — 2026-05-30
3 fresh articles:
1. Sinner's historic collapse at the French Open
2. India face Zimbabwe in Unity Cup third-place match today in London
3. SAFF Championship: India 11-0 Maldives, Bangladesh decider on Sunday
"""

import json, os, uuid, re, time
from datetime import datetime, timezone

import requests

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/.env.pexels") if os.path.exists(os.path.expanduser("~/.env.pexels")) else os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned_patterns = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    return any(p in url for p in banned_patterns)


# ── Supabase helpers ─────────────────────────────────────────────────────────

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert error ({r.status_code}): {r.text[:300]}")
        return None


def sb_patch(table, filters, data):
    """Patch rows in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")
    return False


# ── Articles ─────────────────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Sinner's French Open Collapse ───────────────────────────────
articles.append({
    "headline": "Sinner Was One Game From Victory at 6-3, 6-2, 5-1. He Lost the Last Three Sets and His Thirty-Match Win Streak.",
    "subheadline": "The world number one collapsed in the Paris heat against Juan Manuel Cerundolo. It is the earliest a top seed has exited the French Open since Andre Agassi in 2000.",
    "slug": "sinner-collapses-french-open-2026-cerundolo-two-sets-up-world-number-one-earliest-exit-agassi-2000",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "New York Post", "url": "https://nypost.com"},
        {"name": "People", "url": "https://people.com"},
        {"name": "BBC Sport", "url": "https://www.bbc.com/sport"}
    ]),
    "image_person": "Jannik Sinner",
    "image_query": "tennis Roland Garros clay court French Open",
    "body": """The numbers will age badly for Jannik Sinner. Up 6-3, 6-2, 5-1 against an unseeded Juan Manuel Cerundolo on Court Philippe Chatrier. Serving for the match. One game from a comfortable third-round berth. Then: nothing. Eighteen of the last twenty games went to the Argentine. The final score — 3-6, 2-6, 7-5, 6-1, 6-1 — reads like two different matches stitched together, because that is exactly what it was.

The world number one's second-round exit on Thursday was the earliest by a top seed at Roland Garros since Andre Agassi lost to Karol Kucera in the same round in 2000. It snapped a thirty-match winning streak that had carried Sinner through titles in Monte Carlo, Madrid, and Rome — the most dominant clay-court stretch by any player this decade.

## What Happened on Chatrier

Sinner was imperious through the first two sets, striking the ball with the clean, flat precision that has made him the best player in the world. Cerundolo, ranked 56th, could barely win three games in either set. At 5-1 in the third, the outcome seemed a formality.

Then Sinner called for medical attention. He was visibly struggling — bent over between points, fanning himself with bags of ice, moving as though his legs had stopped receiving instructions from his brain.

"I struggled, started to feel very dizzy," Sinner said afterward. "I was very low on energy. I tried to serve it out but didn't have a lot of energy."

The 24-year-old Italian, who hails from the Alpine town of Innichen in South Tyrol, has a well-documented history of struggling in heat. He retired in Shanghai last October and has had multiple incidents at the Australian Open. But Paris was not particularly extreme — around 33°C, warm but not brutal by Grand Slam standards.

"It was warm but not crazy warm," Sinner conceded. "It was just me today. But it happens."

What happened was startling in its totality. From 5-1 in the third set, Sinner won just two more games across three sets. Cerundolo, who had never previously reached the third round of a Grand Slam, suddenly found himself playing against a diminished opponent and seized every opportunity with increasingly confident shot-making.

## A Draw Blown Wide Open

Sinner's exit came one day before Novak Djokovic suffered an equally dramatic defeat — losing to 19-year-old João Fonseca from two sets down. With defending champion Carlos Alcaraz having withdrawn injured before the tournament, the French Open lost all three favourites before the fourth round. It is the first Grand Slam since 2004 where neither the top seed nor the defending champion made the second week.

Alexander Zverev, the second seed, is now the highest-ranked player remaining. The draw features a cluster of unseeded and lower-seeded players — Cerundolo, Fonseca, Casper Ruud, Karen Khachanov — who suddenly have a realistic path to the final.

## The Diaspora Connection

For NRI tennis fans, the chaos at Roland Garros had already produced a moment of pride before Sinner's collapse. Indian-American wildcard Nishesh Basavareddy — whose parents emigrated from Nellore, Andhra Pradesh — stunned seventh seed Taylor Fritz in the first round, winning in four sets. Basavareddy, 21, eventually lost to Alex Michelsen in the second round, but his victory over Fritz was the first by an American man over a top-ten opponent at Roland Garros since 2000.

## What Sinner Said

Sinner attributed his collapse to accumulated fatigue after three consecutive clay-court titles and a poor night's sleep. He will now rest before Wimbledon, where he is the defending champion.

"In general, many things came together," he said. "I played a lot and I didn't have a lot of time to recover. This morning I didn't sleep well. When I woke up, I was struggling a bit, but this can happen."

It can. But rarely does it happen to the best player in the world, from a position of such commanding dominance, on the sport's biggest stage. The French Open was supposed to be Sinner's coronation — the only Grand Slam he has not won, the final piece of the career Grand Slam. Instead, it became one of the most dramatic collapses in modern tennis history."""
})

# ─── ARTICLE 2: India vs Zimbabwe Unity Cup ─────────────────────────────────
articles.append({
    "headline": "India Play Zimbabwe in London Today. The Blue Tigers Are Back in England for the First Time in Twenty-Four Years.",
    "subheadline": "After losing the Unity Cup semi-final 0-2 to Jamaica, Khalid Jamil's depleted squad play for third place at The Valley. Two players made their senior debuts. The SAFF Championship resumes in Goa tomorrow.",
    "slug": "india-zimbabwe-unity-cup-third-place-london-blue-tigers-first-england-match-since-2002-khalid-jamil",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "AIFF", "url": "https://www.the-aiff.com"},
        {"name": "Khel Now", "url": "https://khelnow.com"},
        {"name": "LatestLY", "url": "https://www.latestly.com"}
    ]),
    "image_person": None,
    "image_query": "India national football team blue jersey",
    "body": """The Indian men's football team plays Zimbabwe in the third-place match of the Unity Cup at The Valley in London today — a fixture that matters less for the result than for what it represents. This is India's first visit to English soil since 2002, when a different generation of Blue Tigers played two friendlies in Watford and Wolverhampton against the same opponents they faced on Tuesday: Jamaica.

Twenty-four years later, the same fixture produced the same result. Jamaica's Courtney Clarke scored a spectacular eighth-minute goal — a breathtaking strike into the top corner after India failed to clear their lines — and Kaheim Dixon added a second in the 78th minute. The 0-2 semi-final defeat was not unexpected. Jamaica, ranked 71st in the world, are 65 places above India in the FIFA rankings and narrowly missed qualifying for next month's World Cup.

## A Squad Under Siege

What made India's London trip remarkable was less the result and more the circumstances surrounding it. Head coach Khalid Jamil — appointed to his first international assignment — saw his squad reduced to just 18 available players hours before departure. Seven Mohun Bagan Super Giant players withdrew despite having reported to camp, while defender Anwar Ali was ruled out through injury.

The withdrawals forced Jamil into emergency measures. FC Goa's Golden Glove winner Hritik Tiwari was called up but had to travel separately due to visa logistics. The squad that landed in London was depleted, undercooked, and facing opponents ranked significantly higher.

Against Jamaica, the Blue Tigers handed senior debuts to Noufal PN and Ricky Shabong, while Edmund Lalrindika received his first-ever start. For NRI football fans watching from across the UK — many of whom made the trip to The Valley in Charlton — these were names to file away for the future.

## The Match That Was

India's inability to create clear chances was the defining feature of the semi-final. After Clarke's early opener, Jamaica attacked with confidence through both wings, and Dixon nearly made it two in the 17th minute before Gurpreet Singh Sandhu made a brave stop.

India improved in the second half. Lallianzuala Chhangte and Ryan Williams showed flashes of incisive play, and the Blue Tigers held more possession. But the final ball was consistently missing. Jamaica's goalkeeper Coniah Boyce-Clarke was rarely troubled, and Dixon's individual goal in the 78th minute merely confirmed what the pattern of play had already suggested.

Nigeria awaits Jamaica in today's final — a repeat of last year's Unity Cup decider. India face Zimbabwe in the third-place match, with kickoff at 19:00 IST (14:30 BST).

## The Bigger Picture for NRI Football Fans

The Unity Cup is a small tournament, but it serves a purpose. For a squad ranked 136th, matches against Jamaica and Zimbabwe offer competitive minutes that the SAFF Championship — where India routinely dominates — cannot provide. The 11-0 demolition of Maldives in Margao on May 25, while emphatic, told Jamil nothing about how his squad would cope against organised, physically imposing opponents.

London told him plenty. The lack of creativity in the final third, the vulnerability to quick counters, and the squad's inability to recover after conceding early are problems that cannot be solved by beating Maldives by double digits. They require exactly the kind of competitive exposure the Unity Cup provides.

The tournament also offered something more personal. For the Indian diaspora in the UK — spread across London, Birmingham, Leicester, and beyond — seeing the Blue Tigers play in England was a rare intersection of two identities. Indian football rarely travels to Europe, and when it does, the matches carry an emotional weight that exceeds their competitive significance.

## What Comes Next

After today's third-place match, India's attention shifts back to Goa. The SAFF Championship resumes tomorrow with India facing Bangladesh in Margao — a group-stage match that will determine who finishes top of Pool A. India's 11-0 victory over Maldives gave them a massive goal-difference advantage, but Bangladesh, who beat Maldives 4-2, will provide a far sterner test.

Khalid Jamil's first month in charge has been a crash course in the realities of Indian football: a squad hollowed by withdrawals, a semi-final defeat in London, and a SAFF Championship where anything less than the title will be considered failure. Today's match in London is the appetiser. The real test begins tomorrow in Margao."""
})

# ─── ARTICLE 3: SAFF Championship India 11-0 + Bangladesh decider ───────────
articles.append({
    "headline": "India Scored Eleven Goals Against Maldives in Margao. On Sunday They Play Bangladesh With the Group on the Line.",
    "subheadline": "Dangmei Grace, Naorem Roshan Singh, and Aman Singh all scored in a record-equalling SAFF Championship rout. Bangladesh will be a very different proposition.",
    "slug": "india-saff-championship-2026-11-0-maldives-bangladesh-sunday-margao-group-decider-khalid-jamil",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "AIFF", "url": "https://www.the-aiff.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_in_Indian_football"},
        {"name": "Football Counter", "url": "https://footballcounter.com"}
    ]),
    "image_person": None,
    "image_query": "India football match SAFF championship stadium Goa",
    "body": """Eleven goals. Zero conceded. Twenty-five minutes into the second half, the stadium announcer in Margao had stopped trying to keep the crowd informed and simply let the electronic scoreboard do the work. India's opening SAFF Championship group match against Maldives on May 25 was not a contest. It was a statement.

Naorem Roshan Singh opened the scoring in the 10th minute and added a second seven minutes later. Ricky Shabong Xaxa made it three in the 29th minute. From there, the goals arrived with metronomic regularity: Aman Singh scored a hat-trick (34th, 66th, 70th, 86th minutes), Dangmei Grace added one (39th), Shirvoikar converted in the 52nd and 68th, and Basfore completed the rout in the 60th minute.

The 11-0 victory — played in front of a sparse 225-person crowd at the Jawaharlal Nehru Stadium in Margao, Goa — matched some of India's biggest-ever winning margins and gave Khalid Jamil the perfect start to his home campaign as head coach.

## What the Scoreline Hides

The danger with a result like this is mistaking volume for quality. Maldives, ranked well below India, were outmatched from the first whistle. They offered minimal defensive structure, rarely won the ball in midfield, and were caught repeatedly by India's pressing and movement in the final third.

Against better opposition, the same patterns that produced 11 goals could produce zero. India's challenge in the SAFF Championship has never been winning — they have won the tournament eight times — but winning in a way that prepares them for sterner tests.

The Bangladesh match on Sunday will provide that test. Bangladesh beat Maldives 4-2 in the other group match, showing both attacking ambition and defensive vulnerability. They are ranked higher than Maldives, have a more organised defensive structure, and are capable of hurting India on the counter.

## NRI Eyes on Margao

For the Indian diaspora — particularly in cities like New York, London, Toronto, and the Bay Area, where Indian football has a passionate but often frustrated following — the SAFF Championship represents the national team's best chance at silverware each year. India are perpetual favourites in the regional tournament, and anything less than the title is considered failure.

The 11-0 against Maldives was broadcast on FanCode, which has global streaming rights for the tournament. Indian football fans in North America and Europe can watch Sunday's Bangladesh decider through the same platform, with kickoff at 19:30 IST (10:00 AM ET, 7:00 AM PT, 3:00 PM BST).

## Sunday's Stakes

A win against Bangladesh would seal top spot in Pool A and send India into the semi-finals with maximum points and a goal-difference cushion that borders on the absurd. A draw would still likely be enough, given India's +11 advantage. Only a loss would create complications — and even then, India would need Bangladesh to overhaul the goal-difference gap.

The real question is whether Khalid Jamil will use Sunday's match to experiment. Several players from the Unity Cup squad in London — including debutants Noufal PN and Ricky Shabong — could be integrated into the SAFF squad if they return in time. The dual-tournament schedule has stretched India's limited squad depth, but it has also given Jamil a broader view of his options.

## The Road to the Semi-Finals

India's semi-final is scheduled for June 3 in Margao. The likely opponent will be determined by results in Pool B, where Sri Lanka, Nepal, and Bhutan are competing. Sri Lanka and Nepal are the likely qualifiers, and either would offer India a competitive semi-final before a probable final against Bangladesh or another Pool B qualifier.

For Jamil, the SAFF is a chance to build confidence, establish combinations, and give competitive minutes to players who may feature in India's 2027 Asian Cup qualifying campaign. The 11-0 against Maldives was a foundation, not a finished product. Sunday's match against Bangladesh will show whether the foundation can hold."""
})


# ── Publish ──────────────────────────────────────────────────────────────────

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:80]}...")
    
    # ── Image sourcing ──────────────────────────────────────────────────────
    img_url = None
    
    if art.get("image_person"):
        print(f"  → Trying Wikipedia for '{art['image_person']}'...")
        img_url = fetch_wikipedia_person_image(art["image_person"])
    
    if not img_url and art.get("image_query"):
        print(f"  → Trying Pexels for '{art['image_query']}'...")
        img_url = fetch_pexels_image(art["image_query"])
    
    # Validate
    if img_url and is_banned_url(img_url):
        print(f"  ✗ Banned URL detected, skipping: {img_url[:80]}")
        img_url = None
    
    if img_url and not validate_image_url(img_url):
        print(f"  ✗ Image validation failed: {img_url[:80]}")
        img_url = None
    
    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print("  ⚠ No valid image found — publishing without image")
    
    # ── Insert article ──────────────────────────────────────────────────────
    art_id = str(uuid.uuid4())
    
    row = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now,
        "sources": json.loads(art["sources"]),
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and "wikimedia" in (img_url or "").lower() else "The Videshi" if img_url else None,
    }
    
    result = sb_insert("p2_articles", row)
    if result:
        print(f"  ✓ Published: {art['slug']}")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Sports writer complete. {len(articles)} articles processed.")
