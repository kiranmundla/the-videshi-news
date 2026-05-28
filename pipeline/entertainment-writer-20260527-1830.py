#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-27 18:30 PDT batch."""

import json, os, sys, time, uuid, urllib.parse, subprocess, re
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──────────────────────────────────────────────────────────
import requests

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10,
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
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check URL returns HTTP 200 with image Content-Type and decent size."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Some servers don't return content-length on HEAD, try GET with range
        if r.status_code == 200 and "image" in ct:
            print(f"  ✓ Image validated (no Content-Length): {ct}")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert row into Supabase."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None


def make_slug(text):
    """Create a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].rstrip('-')


# ── ARTICLES ─────────────────────────────────────────────────────────
now_iso = datetime.now(timezone.utc).isoformat()

articles = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: Ram Charan's Peddi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

article1_headline = "Ram Charan Broke His Leg for RRR. For Peddi, He Can't Lift His Daughter. The Biggest Indian Film of June Opens in Seven Days."
article1_subheadline = "A.R. Rahman's soundtrack just debuted on the US charts. The runtime is 3 hours 9 minutes. Advance bookings in North America have already crossed $375,000. And the man at the centre of it says he might need an X-ray."
article1_slug = "ram-charan-peddi-june-4-release-ar-rahman-pan-india-sports-drama-nri-20260527"
article1_body = """Ram Charan is hurt. Not in the metaphorical, Bollywood-press-tour way — actually hurt.

During a recent promotional drive through Hyderabad with director Buchi Babu Sana, the actor revealed that the physical transformation demanded by **Peddi** has left him unable to lift his three-year-old daughter Klin Kaara without pain. "Even lifting my daughter hurts this hand," he said. "I need to get an X-ray. Constant grabbing during wrestling caused tremors. It did something to this hand."

The damage is the price of playing three different athletes in one film. Buchi Babu's script required Ram Charan to first build a cricketer's lean physique — think Tilak Varma, Hardik Pandya — then bulk up into a kabaddi player, then transform again into a wrestler. Each body type demanded a completely different training regime, diet, and movement vocabulary. "They are both extremely different," Ram Charan told the director. "You wanted that kind of body. Then, after a few days, he needed a bulkier body."

This is, by most measures, his most physically extreme role since breaking his leg during the filming of **RRR**.

## What Peddi Actually Is

Set in 1980s rural Andhra Pradesh, **Peddi** follows a spirited villager who unites his fractured community through sport — cricket, wrestling, and kabaddi — to defend their pride against a powerful political rival. It is part sports epic, part rural drama, part A.R. Rahman concert film.

And about that music: the Peddi soundtrack has already made history before the film has even opened. All of its tracks are charting simultaneously, with the title track, *Ishq Jalakar*, *Karvaan*, and *Hellallallo* (featuring a Shruti Haasan guest appearance alongside Janhvi Kapoor) driving massive streaming numbers. The album debuted at **#5 on the US Top Albums chart** — a staggering achievement for an Indian film soundtrack that tells you everything about where the diaspora audience has moved.

## The NRI Bet

The advance booking numbers from North America are already eye-catching. US premiere bookings have crossed **$375,000**, putting Peddi in rare company alongside RRR and Baahubali 2 for Telugu film openings in North America. The film is releasing day-and-date globally on **June 4** across Telugu, Hindi, Tamil, Kannada, and Malayalam — a true pan-India play with a deliberate weekday release to avoid competing with the IPL 2026 playoffs.

For NRI audiences, the June 4 date is strategic. The IPL final is done, the summer is starting, and there's a clear runway before the FIFA World Cup commandeers every screen on June 11.

## The Team

Director Buchi Babu Sana made his name with **Uppena** (2021), a rural drama that announced Vaishnav Tej and became a sleeper hit. Peddi is orders of magnitude more ambitious — a 3-hour-9-minute sports saga with A.R. Rahman composing the full soundtrack, R. Rathnavelu (Baahubali, RRR) behind the camera, and a cast that includes **Janhvi Kapoor**, **Shiva Rajkumar**, **Jagapathi Babu**, **Boman Irani**, **Ravi Kishan**, and **Divyenndu Sharma**.

The film cleared CBFC with a **U/A 16+** certificate. Priyanka Chopra publicly praised the trailer on X. Shiva Rajkumar predicted a National Award for Ram Charan.

## What's at Stake

June has been a graveyard for Bollywood this year — Chand Mera Dil and Pati Patni Aur Woh Do both flopped in May. But Peddi isn't a Bollywood film. It's a Telugu-origin pan-India release from the same ecosystem that produced RRR, Pushpa, and Baahubali. The bet is that Ram Charan can carry a sports drama the way he carried a freedom-fighter action film.

The last time A.R. Rahman scored a Telugu sports film with an RRR-level star, the result was an awards-season juggernaut. The last time Ram Charan put his body through this kind of punishment, the film won an Oscar.

Peddi premieres globally on June 3 and releases theatrically worldwide on June 4.

Sources: Pinkvilla (Ram Charan transformation interview, May 22, 2026), Bollywood Hungama (A.R. Rahman Bhopal concert, May 23, 2026), Sacnilk (CBFC certification, box office tracking), Filmibeat (US advance booking data)"""

article1_person = "Ram Charan"
articles.append({
    "headline": article1_headline,
    "subheadline": article1_subheadline,
    "slug": article1_slug,
    "body": article1_body,
    "person": article1_person,
    "pexels_query": "cricket stadium India",
    "pexels_fallback": "sports drama film",
    "sources": ["Pinkvilla", "Bollywood Hungama", "Sacnilk", "Filmibeat"],
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: Vicky Kaushal Mahavatar + Ranveer Pralay
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

article2_headline = "Vicky Kaushal Has Blocked 18 Months to Play a God. Ranveer Singh Is Killing Zombies. Bollywood's 2027 War Just Started."
article2_subheadline = "Mahavatar is a Parashurama epic directed by the man who made Stree. Pralay is India's first zombie action film. Both are insane bets on a genre Bollywood has never cracked."
article2_slug = "vicky-kaushal-mahavatar-ranveer-singh-pralay-bollywood-2027-blockbuster-war-nri-20260527"
article2_body = """The two biggest male stars in Hindi cinema just drew their lines in the sand for 2027 — and neither of them is making anything remotely safe.

**Vicky Kaushal** has blocked a full 18 months of his calendar for **Mahavatar**, an epic mythological film in which he plays **Parashurama** — the sixth avatar of Vishnu, the axe-wielding warrior-sage who wiped out the Kshatriya race twenty-one times. The film is directed by **Amar Kaushik**, the man behind the Stree franchise, and produced by Dinesh Vijan's Maddock Films. It was originally slated for Christmas 2026 but has been pushed to **December 24, 2027** — a delay that tells you everything about its scale.

Meanwhile, **Ranveer Singh** — currently banned by FWICE, currently the subject of a ₹45 crore Don 3 compensation dispute — is starting the shoot of **Pralay** in August 2026. It is a post-apocalyptic zombie thriller. The director is **Jai Mehta** (no relation to Hansal Mehta, though Hansal is producing). Ranveer is co-producing through his new banner **Maa Kasam Films**. The female lead is **Kalyani Priyadarshan**, whom Ranveer personally convinced to join after her breakout in the Malayalam hit Lokah.

Two films. Two genres Bollywood has historically fumbled. Two actors betting their careers on the proposition that Indian audiences are ready for something bigger than the rom-com-masala-sequel pipeline.

## The Parashurama Problem

Mythological cinema in India carries a peculiar burden. The most successful Indian film franchise — Baahubali — was mythology-adjacent but invented its own lore. Every actual mythology adaptation has struggled: Brahmastra needed three films to tell one story and hasn't finished. The Ramayana (starring Ranbir Kapoor) has been in production for years and just moved its release to October 30. Adipurush was a creative catastrophe.

Mahavatar is betting that Amar Kaushik — a director whose signature is smart, commercially calibrated horror-comedy — can crack what bigger budgets and more experienced directors couldn't. The fact that he's blocking 18 months suggests the VFX pipeline alone is unlike anything Maddock has attempted. Reports indicate **Shraddha Kapoor** is in talks for the female lead, which would reunite the Stree pair in a very different register.

For NRI audiences who grew up on Amar Chitra Katha Parashurama stories, this is either the film they've been waiting for or the one they're most afraid will disappoint.

## The Zombie Proposition

Pralay is a different kind of gamble. India has never had a successful zombie film. The genre doesn't have cultural roots in Indian storytelling the way it does in Korean or American cinema. Go Goa Gone (2013) tried zombie comedy and made ₹30 crore. Nothing else has even tried.

Ranveer's bet is that 2027 India is ready — that the audience that embraced Korean zombie content (Train to Busan, Kingdom, All of Us Are Dead) on Netflix will show up for an Indian version with the right star. The film is described as an original story (not a Blindness adaptation, as was initially rumoured — Hansal Mehta himself clarified). Kalyani Priyadarshan brings a South Indian fanbase that could help the film travel beyond Hindi markets.

The timing is also strategic. If Ranveer's FWICE situation is resolved — and it likely will be, because no one stays banned forever when there's money on the table — Pralay positions him as a genre-breaking producer-star in the mould of what Aamir Khan used to be.

## What This Means for the Calendar

December 2027 is shaping up as the most stacked release window in Indian cinema history. Mahavatar is now targeting Christmas Day. The Ramayana sequel is likely nearby. If Pralay wraps on schedule, it could slot into the summer-monsoon window.

For the diaspora audience, the 2027 pipeline already looks far more interesting than 2026, which has been dominated by sequels and franchise fatigue. Mahavatar and Pralay are both original IP — risky, ambitious, and exactly the kind of swing that Indian cinema needs to make if it wants to compete globally.

Whether they connect is a question for 2027. That they exist at all is a 2026 story.

Sources: Sacnilk (Pralay details, Mahavatar schedule), Pinkvilla (Kalyani Priyadarshan casting), Plex (Mahavatar December 2027 release date), Filmfare (Vicky Kaushal first look)"""

article2_person = "Vicky Kaushal"
articles.append({
    "headline": article2_headline,
    "subheadline": article2_subheadline,
    "slug": article2_slug,
    "body": article2_body,
    "person": article2_person,
    "pexels_query": None,
    "pexels_fallback": None,
    "sources": ["Sacnilk", "Pinkvilla", "Plex", "Filmfare"],
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 3: South Indian exhibitors 8-week OTT window
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

article3_headline = "South Indian Theatres Just Told Netflix to Wait Eight Weeks. If You Live Abroad, This Is About You."
article3_subheadline = "A new exhibitor mandate across Telugu, Tamil, Kannada, and Malayalam cinema forces an 8-week theatrical window before any OTT release. For the diaspora, it means waiting two months for every South Indian film that doesn't get a global day-and-date release."
article3_slug = "south-indian-exhibitors-8-week-ott-window-nri-streaming-impact-20260527"
article3_body = """South Indian exhibitors have formally mandated an **8-week theatrical exclusivity window** for all new releases — and simultaneously shifted from fixed rental fees to a **revenue-sharing model** with producers. The decision, led by exhibitor associations across Telugu, Tamil, Kannada, and Malayalam cinema, is the most significant structural change to Indian film distribution in years.

And if you live in the US, UK, or Canada, it is almost entirely about you.

## What Changed

Until now, the theatrical-to-OTT window for South Indian films was chaotic. Some films hit streaming platforms within 2-3 weeks of their theatrical release. Dhanush's **Kara** made ₹50 crore at the box office on a ₹100 crore budget and landed on Netflix 36 days after release. Others waited longer. There was no standard.

The new mandate locks the window at **eight weeks** — 56 days of theatrical exclusivity before a film can appear on any streaming platform. This mirrors what Bollywood multiplexes adopted and what Universal Pictures enforces globally.

The revenue-sharing shift is the other half of the deal. Previously, many South Indian theatres operated on fixed rental agreements — producers paid a flat fee for screen access regardless of performance. The new model replaces this with **percentage-based splits**, meaning theatres now share both the upside and the downside of a film's box office run.

## Why Exhibitors Forced This

The math is simple. When a big Telugu film hits Netflix three weeks after release, the second and third week theatrical collections collapse. Audiences — especially younger audiences with Netflix/Prime subscriptions — simply wait. Every week of early OTT release cannibalises at least 20-30% of what a film would have earned in extended theatrical run.

For exhibitors, this is existential. Single-screen theatres in tier-2 and tier-3 cities rely on the long tail — the fourth, fifth, sixth week of a film's run. When that tail gets chopped by an OTT premiere, those screens go dark.

The 8-week window is designed to protect that tail. The revenue-sharing model is designed to align incentives — if a theatre shares box office risk with the producer, both parties are incentivised to keep the film running as long as it sells tickets.

## The NRI Problem

Here's where it gets complicated for the diaspora.

The 8-week window works in India because Indian audiences have both options — theatres and streaming. But for NRIs in mid-sized American cities, secondary Canadian towns, or UK cities outside London, many South Indian films **never get a theatrical release at all**. The only way to watch them legally is OTT.

An 8-week window means that if a Tamil or Telugu film doesn't get a North American theatrical run — and most don't — the NRI audience waits two full months after Indian audiences have already seen it. Two months of spoilers on X, two months of YouTube thumbnail reveals, two months of being excluded from the cultural conversation.

The films that **do** get global day-and-date releases — your RRRs, your Pushpas, your Peddis — are unaffected. But the mid-budget films, the indie breakouts, the surprise hits that don't have international distribution deals? Those are the ones that the diaspora will now wait longest for.

## The OTT Platforms Aren't Happy

Netflix, Amazon Prime Video, and JioHotstar (Disney's new India joint venture with Reliance) all built their Indian content strategies around fast theatrical-to-digital windows. Shorter windows meant more subscribers, more first-week viewing spikes, more watercooler moments.

An 8-week mandate changes the calculus for digital rights valuations. If a film's streaming premiere comes two months after theatrical, the digital rights are worth less — because by then, the film's cultural moment has passed. This could compress the premiums that OTT platforms pay for South Indian content, which in turn could reduce production budgets for the mid-tier films that OTT currently subsidises.

The irony is that OTT platforms have been the single biggest enabler of South Indian cinema's national and global reach. Without Netflix, Drishyam and Kaithi don't become Hindi remakes. Without Prime Video, Pushpa doesn't become a cultural phenomenon. The exhibitors are protecting their business by constraining the very distribution channel that made their films valuable.

## What This Means Going Forward

The 8-week window will likely hold for big releases — no exhibitor is going to let a Ram Charan or Rajinikanth film jump to streaming early. But for smaller films that underperform at the box office, the pressure to break the window will be enormous. Producers who split revenue with theatres and see collections drop after week two will want out.

Expect a two-tier system to emerge: big films get the full 8-week theatrical run, mid-budget films negotiate early OTT exits with exhibitor consent, and the diaspora continues to be the last audience served.

For NRIs who've built their cultural lives around watching Tamil and Telugu films on opening weekends via Netflix — plan accordingly. The wait just got longer.

Sources: Sacnilk (exhibitor mandate details), Livemint (Indian film industry theatrical window debate), Pinkvilla (Bollywood multiplex 8-week precedent), Chitrajyothy (South Indian exhibitor announcement)"""

article3_person = None
articles.append({
    "headline": article3_headline,
    "subheadline": article3_subheadline,
    "slug": article3_slug,
    "body": article3_body,
    "person": article3_person,
    "pexels_query": "movie theatre India cinema",
    "pexels_fallback": "cinema hall audience",
    "sources": ["Sacnilk", "Livemint", "Pinkvilla", "Chitrajyothy"],
})

# ── PUBLISH ──────────────────────────────────────────────────────────
print("=" * 60)
print(f"Publishing {len(articles)} entertainment articles...")
print("=" * 60)

for i, art in enumerate(articles, 1):
    print(f"\n{'─' * 40}")
    print(f"Article {i}: {art['headline'][:60]}...")
    
    # Image sourcing
    img_url = None
    img_attribution = None
    
    # Try Wikipedia first for person articles
    if art["person"]:
        print(f"  → Trying Wikipedia for '{art['person']}'...")
        img_url = fetch_wikipedia_person_image(art["person"])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    # Fall back to Pexels
    if not img_url and art["pexels_query"]:
        print(f"  → Trying Pexels for '{art['pexels_query']}'...")
        img_url = fetch_pexels_image(art["pexels_query"], art["pexels_fallback"])
        if img_url:
            img_attribution = "Pexels"
    
    # Validate image
    if img_url:
        if not validate_image_url(img_url):
            print(f"  ✗ Image failed validation, skipping")
            img_url = None
            img_attribution = None
    
    if not img_url:
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")
    
    # Build article record
    art_id = str(uuid.uuid4())
    record = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "sources": json.dumps(art["sources"]),
    }
    
    if img_url:
        record["image_url"] = img_url
        record["image_attribution"] = img_attribution
    
    # Insert
    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        print(f"    ID: {art_id}")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)
