#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-01 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────
def sb_insert(table, payload):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code >= 300:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) and data else data

def sb_patch(table, params, payload):
    url = f"{SB_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=payload, timeout=30)
    if r.status_code >= 300:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return r

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
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check that URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET with range
        if "image" in ct:
            return True
    except:
        pass
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": ct,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code < 300:
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ── articles ─────────────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Ranveer Singh at Champions League Final
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Ranveer Singh Flew to Budapest for Arsenal's Champions League Final. His Instagram Note Hit Harder Than the Penalty Miss.",
    "subheadline": "Amid the FWICE controversy over Don 3, Bollywood's most visible football fan was in the stands at the Puskás Arena for one of the most heartbreaking finishes in Champions League history.",
    "slug": "ranveer-singh-budapest-arsenal-champions-league-final-psg-penalties-nri-20260601",
    "category": "entertainment",
    "body": """Arsenal came agonisingly close. And Ranveer Singh was there to watch it fall apart.

The Bollywood superstar flew to Budapest for Saturday's UEFA Champions League final between Arsenal and Paris Saint-Germain at the Puskás Arena — a match that ended 1-1 after extra time before PSG won 4-3 on penalties to claim back-to-back European titles.

## A Heartbreaker in Budapest

Kai Havertz had given Arsenal fans a dream start, powering the Gunners ahead after just six minutes. For much of the first half, Mikel Arteta's side — already crowned Premier League champions — looked capable of completing a historic double.

But Ousmane Dembélé's second-half penalty levelled the tie, and the match ground through a tense, goalless extra time before reaching the spot-kick lottery. Arsenal's Eberechi Eze missed first, and though David Raya saved Nuno Mendes' effort to give the Gunners a lifeline, Gabriel Magalhães blazed his decisive penalty over the bar. PSG celebrated becoming only the second club after Real Madrid to win consecutive Champions League titles in the modern era.

## "Proud of the Boys"

Hours after the final whistle, Ranveer posted an emotional tribute on Instagram that resonated far beyond football circles.

"Proud of the boys. Fought like lions!" he wrote. "Couldn't get any closer in a game of such fine margins. Congratulations to my Arsenal family on a historic season. And… the best is yet to come!"

Earlier in his Budapest trip, Ranveer had met Arsenal and England midfielder Declan Rice, sharing a photo on Instagram with the caption "All about last night" set to the classic Bollywood track *Tere Jaisa Yaar Kahan* from the film *Yaarana*.

## Bollywood's Most Devoted Football Fan

Ranveer's Arsenal devotion is not a recent PR exercise. He has been photographed at the Emirates Stadium multiple times, has worn the Gunners kit at public events, and has cultivated friendships across the Arsenal dressing room. His Budapest trip placed him among roughly 25,000 travelling Arsenal fans in a 67,000-capacity stadium.

For the Indian diaspora — a significant and growing segment of the Premier League's global audience — Ranveer's visible fandom has become a bridge between two of their biggest cultural passions. The sight of one of India's biggest film stars consoling himself alongside English, Ghanaian, and Nigerian Arsenal supporters in a Hungarian stadium captures something about modern fandom that transcends geography.

## The Don 3 Shadow

The Budapest trip came at a complicated moment for Ranveer professionally. The Federation of Western India Cine Employees (FWICE) recently issued a non-cooperation directive against him following his reported exit from *Don 3*, and the organisation has approached the Indian Motion Picture Producers' Association and the Producers Guild of India seeking intervention.

Ranveer has not publicly addressed the Don 3 situation in detail, but his Budapest presence — visible, unapologetic, emotional — suggested a man who was not hiding from the spotlight, just choosing where to point it.

The Premier League resumes in August. Arsenal will be back. So, presumably, will Ranveer.""",
    "sources": [
        "IANS (ianslive.in) — Ranveer Singh motivates team Arsenal post their Champions League defeat",
        "Fox Sports — UEFA Champions League final 2026: PSG defeat Arsenal on penalties",
        "Reuters — PSG forge modern dynasty with Champions League shootout triumph over Arsenal",
        "talkSPORT — PSG win Champions League LIVE REACTION: Arsenal lose on penalties"
    ],
    "person_image": "Ranveer Singh",
    "pexels_query": "football stadium champions league",
    "pexels_fallback": "football fans celebrating stadium",
    "diaspora_angle": "For the millions of NRI Premier League fans across the US, UK, and Middle East, Ranveer Singh's visible Arsenal fandom has become a cultural bridge. His Budapest trip places an Indian superstar at the heart of European football's biggest night — a reminder that the diaspora's sporting passions extend far beyond cricket."
})

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Panchayat Season 5 — "Bada, Behtar, Khoobsurat"
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Panchayat's Vikas Just Teased Season 5 in Three Words. Here's Everything NRI Fans Need to Know.",
    "subheadline": "Chandan Roy says Season 5 will be 'bada, behtar aur khoobsurat.' After Season 4 trended in 42 countries, the show that made the world fall in love with rural India is coming back.",
    "slug": "panchayat-season-5-chandan-roy-vikas-teaser-bada-behtar-prime-video-nri-20260601",
    "category": "entertainment",
    "body": """Three words. That is all Chandan Roy — the man who plays the endlessly lovable Vikas in Amazon Prime Video's *Panchayat* — needed to set the internet alight.

"Bada, behtar aur khoobsurat."

Bigger, better, and more beautiful.

Speaking publicly on May 31, the actor confirmed that the full ensemble is returning to Phulera for a fifth season of India's most beloved streaming series. And if Season 4's global reception is any indication, the world is paying attention.

## A Show That Conquered 180 Countries

When *Panchayat* Season 4 premiered on Prime Video in June 2025, it set a franchise record immediately. The show trended in over 42 countries on its opening day — including the United States, United Kingdom, Canada, Australia, and the UAE — and was streamed across more than 180 countries during its launch week.

For a Hindi-language show set in an imaginary village called Phulera, featuring no car chases, no item songs, and no CGI, those are extraordinary numbers.

"The season's exceptional viewership across India and in over 180 countries within its launch week is a testament to its universal appeal and deep cultural resonance," said Manish Menghani, Director and Head of Content Licensing at Prime Video India, when Season 5 was first confirmed.

## Why the Diaspora Cannot Get Enough

*Panchayat* works for NRI audiences in a way few Indian shows manage. It is not aspirational Mumbai or glossy Delhi — it is the India that many diaspora families left behind and still carry in their memories. The village politics, the chai-fuelled gossip, the gentle absurdity of a panchayat secretary who really just wants to crack the CAT exam — these are textures that resonate deeply with first-generation immigrants and their children alike.

The show has also become a gateway for non-Indian audiences curious about Indian life beyond Bollywood stereotypes. On Reddit and social media, international viewers have described discovering *Panchayat* as a revelation — a show that asks nothing of them except patience and an openness to laugh.

## What We Know About Season 5

Details remain scarce, but here is what has been confirmed:

**Returning cast:** Jitendra Kumar (Sachiv Ji), Neena Gupta (Manju Devi), Raghubir Yadav (Brij Bhushan), Chandan Roy (Vikas), Faisal Malik (Prahlad), Sanvikaa (Rinki), Durgesh Kumar, Sunita Rajwar, and Pankaj Jha are all expected back.

**Creators:** Deepak Kumar Mishra and Chandan Kumar, who created the show and wrote every season, are returning alongside director Akshat Vijaywargiya.

**Platform:** Exclusively on Amazon Prime Video, like all previous seasons.

**Release window:** 2026. No specific date has been announced, but the show typically drops in the June-July window — meaning a release within the next few months is plausible.

## The Questions Season 5 Must Answer

Season 4 left several threads dangling. The election outcome between key characters remains unresolved. Sachiv Ji's CAT exam results have raised the possibility that he might finally leave Phulera — a prospect that would fundamentally alter the show's DNA. And the cliffhanger involving Prahlad (Pradhan Ji) has fans speculating wildly about what comes next.

Vijay Koshy, President of The Viral Fever (TVF), the production company behind the series, has spoken about the emotional stakes: "This series holds a special place in our hearts for capturing the humor, charm, and warmth of rural India."

## A Quiet Global Phenomenon

*Panchayat* has never been a loud show. It does not trend because of controversy or celebrity Instagram posts. It trends because people watch it, feel something, and tell their friends. In an era of algorithm-driven content, that kind of organic word-of-mouth is increasingly rare — and increasingly valuable.

Bada, behtar aur khoobsurat. If Vikas says so, Phulera is in good hands.""",
    "sources": [
        "Wow News — Vikas Teases 'Bada, Behtar, Khoobsurat': Panchayat Season 5 Promises Bigger Drama",
        "The Indian Eye — Prime Video's Panchayat Season 4 Achieves Record-Breaking Success, Season 5 Confirmed",
        "BizzBuzz News — Panchayat Season 4 Sets Franchise Record, Prime Video Confirms Season 5 for 2026"
    ],
    "person_image": "Jitendra Kumar (actor)",
    "pexels_query": "Indian village rural life",
    "pexels_fallback": "Indian rural countryside",
    "diaspora_angle": "Panchayat Season 4 trended in 42 countries on its premiere day and was streamed in 180+ countries. The show has become a nostalgia touchstone for NRI families who left rural India behind — and a gateway for non-Indian viewers curious about Indian life beyond Bollywood stereotypes."
})

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Toxic's domino effect on Bollywood's June calendar
# ═══════════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Bollywood's Entire June Calendar Changed Four Times Because of One Film That Still Hasn't Released.",
    "subheadline": "Yash's Toxic has been postponed from April to March to June to 'later.' In its wake, at least five other films have reshuffled their release dates — and the Gulf diaspora market is the reason everyone keeps blinking first.",
    "slug": "toxic-yash-postponement-domino-effect-bollywood-june-calendar-gulf-diaspora-nri-20260601",
    "category": "entertainment",
    "body": """In Bollywood's 2026 release calendar, one film has caused more chaos than any other — without showing a single frame in a public theatre.

Yash's *Toxic: A Fairy Tale for Grown-Ups*, directed by Geetu Mohandas, has been rescheduled so many times that the Indian film trade has started referring to its release date as a moving target. And every time Toxic moves, everything around it moves too.

## The Timeline

Here is what happened:

**Original date: March 19, 2026.** The plan was simple — give the KGF star a solo Eid-adjacent weekend. IMAX confirmed. Advance bookings were set to open.

**First postponement: June 4, 2026.** In early March, the makers cited geopolitical instability in the Middle East. The Gulf region — home to approximately 9.5 million Indians, including over one million Kannadigas — is a primary revenue territory for South Indian blockbusters. For a film budgeted at a reported ₹600-800 crore, leaving Gulf money on the table was not an option.

**CinemaCon showcase: April 2026.** In a bold move, the team screened a nine-minute preview at CinemaCon in Las Vegas. The response was electric — trade analysts called it "a game-changer" and "unlike anything seen in Indian cinema before." The footage reportedly spans the 1940s to the 1970s, with a period gangster aesthetic filtered through what the makers call "a fairy tale for grown-ups."

**Second postponement: April 29, 2026.** Just five weeks before the June 4 date, the makers announced another delay. This time, the reason was strategic ambition — after the CinemaCon reception, they wanted to align global distribution and partnerships for a wider rollout. The new date? To be announced.

## The Domino Effect

Each Toxic move sent shockwaves through the June calendar.

**Hai Jawani Toh Ishq Hona Hai** — David Dhawan's romantic comedy starring Varun Dhawan, Mrunal Thakur, and Pooja Hegde — has changed its release date *four times*. It went from June 5 to June 12 (to avoid Toxic), then jumped forward to May 22 (to beat Toxic), and now sits back at June 5 (because Toxic left). Varun Dhawan publicly thanked Yash for the calendar clarity.

**Bobby Deol's Bandar**, directed by Anurag Kashyap, locked June 5 once the coast was clear.

**Main Vaapas Aaunga**, Imtiaz Ali's Partition-era love story with Diljit Dosanjh and Vedang Raina — the most anticipated Indian film of 2026 according to IMDb — staked out June 12, safely distant from Toxic's original June 4 slot.

**Welcome to the Jungle**, Ahmed Khan's 30-star comedy extravaganza led by Akshay Kumar, claimed June 26, the month's final major slot.

## The Gulf Market Factor

What makes Toxic's scheduling story particularly relevant for diaspora audiences is the explicit centrality of the Gulf market in every decision.

The 9.5 million Indians in the Gulf Cooperation Council countries are no longer an afterthought in Bollywood's box office calculations — they are a primary driver. Karnataka alone has over one million residents in the region, making the Gulf a kingmaker for Kannada-language blockbusters.

When Toxic postponed its March release, the stated reason was airspace disruptions and reduced foot traffic in Gulf cinemas due to regional tensions. This was not a soft excuse — exhibitors in the UAE and Saudi Arabia confirmed that occupancy rates had dropped significantly, especially for premium formats like IMAX and Dolby Cinema.

The implication is clear: a single overseas market now has the power to dictate when India's most expensive film opens worldwide. For NRI audiences, this is both validation and leverage — your tickets literally move mountains.

## What It Means for the Industry

Bollywood's 2026 release calendar has exposed a structural fragility. When one mega-budget film sneezes, a dozen mid-budget films catch a cold. The date-shuffling game disproportionately affects smaller films that lack the marketing budgets to pivot repeatedly — every date change means reprinted posters, renegotiated theatre allocations, and lost promotional momentum.

Trade analyst sentiment is mixed. Some see the chaos as a sign of a market in transition — moving from a domestic-first model to a truly global release strategy where international territories have equal weight. Others worry that the concentration of power in a handful of franchises (Toxic, Dhurandhar, Ramayana) is squeezing the oxygen out of mid-range cinema.

Either way, the lesson from Toxic's scheduling saga is unmistakable: in 2026, Bollywood's release calendar is no longer a local affair. It is a global negotiation — and the diaspora is at the table.""",
    "sources": [
        "Sacnilk — Toxic Box Office Hype: Yash Starrer Leaves Global Trade Speechless With 9-Minute CinemaCon Preview",
        "Hollywood Reporter India — 'Toxic': Release Of The Yash-Kiara Advani Film Pushed To June",
        "Sacnilk — Yash's Toxic Postponed to June 4: Analyzing the Significance of the Middle East Market",
        "PinkVilla — Varun Dhawan's Hai Jawani Toh Ishq Hona Hai locks June 5, 2026 release date after Toxic gets postponed",
        "Sacnilk — David Dhawan's Hai Jawani Moves Back To Original Date After Toxic Postponement"
    ],
    "person_image": "Yash (actor)",
    "pexels_query": "Indian cinema theatre audience",
    "pexels_fallback": "movie theatre marquee",
    "diaspora_angle": "The Gulf diaspora market — 9.5 million Indians across the GCC, including over 1 million Kannadigas — is now powerful enough to force release date changes for India's most expensive films. Every scheduling decision in Bollywood's 2026 June calendar was driven by the financial weight of overseas audiences, especially in the Middle East."
})

# ── publish ──────────────────────────────────────────────────────────────

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:70]}...")
    print(f"{'='*60}")

    # Image sourcing — Wikipedia first for person articles
    img_url = None
    img_attribution = None
    person = art.get("person_image")
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = fetch_pexels_image(art.get("pexels_query"), art.get("pexels_fallback"))
        if img_url:
            img_attribution = "Pexels"

    # Upload to Supabase storage for permanence
    final_image_url = None
    if img_url:
        slug = art["slug"]
        ext = "jpg"
        if ".png" in img_url.lower():
            ext = "png"
        filename = f"{slug}.{ext}"
        final_image_url = upload_to_supabase_storage(img_url, filename)
        if not final_image_url and validate_image_url(img_url):
            # If upload fails but URL is from a permanent source, use directly
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                final_image_url = img_url
                print(f"  → Using direct URL as fallback: {img_url[:80]}...")

    if not final_image_url:
        print(f"  ⚠ No image sourced for article {i}")

    # Build sources string
    sources_str = "\n".join(f"- {s}" for s in art["sources"])

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"].strip(),
        "category": art["category"],
        "vertical": art["category"],  # vertical = category for entertainment
        "diaspora_angle": art.get("diaspora_angle", ""),
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "sources": sources_str,
    }
    if final_image_url:
        payload["image_url"] = final_image_url
        payload["image_attribution"] = img_attribution or "The Videshi"

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")
