#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-29 batch."""

import json, os, re, sys, time, uuid, subprocess, urllib.parse, traceback
from datetime import datetime, timezone

import requests

# ── Supabase credentials ──
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels ──
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.strip().startswith("PEXELS_API_KEY"):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"')

# ── Image helpers ──

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
    """Search Pexels for a relevant image. Uses curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        if r.status_code != 200 or "image" not in ct:
            r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get("Content-Type", "")
            cl2 = int(r2.headers.get("Content-Length", 0))
            if r2.status_code == 200 and "image" in ct2:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def get_image(person_name=None, pexels_query=None, pexels_fallback=None):
    """Try Wikipedia first for person, then Pexels, validate result."""
    url = None
    attribution = None
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, "Wikimedia Commons"
        # Try disambiguation
        for suffix in ["(cricketer)", "(sportsperson)"]:
            url = fetch_wikipedia_person_image(f"{person_name} {suffix}")
            if url and validate_image(url):
                return url, "Wikimedia Commons"
    if pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url and validate_image(url):
            return url, "Pexels"
    return None, None


# ── Supabase insert ──

def publish_article(article):
    """Insert article into p2_articles."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✅ Published: {article['headline'][:60]}... (id={aid})")
        return True
    else:
        print(f"  ❌ Failed to publish: {r.status_code} - {r.text[:200]}")
        return False


# ── Articles ──

articles = []

# ────────────────────────────────────────────────────
# ARTICLE 1: Hardik Pandya Quits Mumbai Indians
# ────────────────────────────────────────────────────
print("\n📰 Article 1: Hardik Pandya Quits Mumbai Indians")

img1, attr1 = get_image(person_name="Hardik Pandya")

body1 = """Hardik Pandya has decided to leave the Mumbai Indians. The news broke on Friday through PTI, citing a top IPL source who described the 32-year-old all-rounder as "mentally stressed and completely exhausted" after three turbulent seasons at his old franchise.

Pandya informed the MI management of his decision mid-season, weeks before their 2026 campaign officially ended in ninth place. Once the playoff hopes were extinguished — with quite a few league matches still remaining — both sides reached a mutual understanding to part ways.

## The Weight of the Captaincy

The trouble began before the first ball was bowled. When MI brought Pandya back from the Gujarat Titans ahead of IPL 2024, he replaced Rohit Sharma as captain — a move that divided the fanbase in ways the franchise had not anticipated. Fans booed Pandya at the Wankhede, loudly and persistently, through the 2024 and 2026 seasons. MI finished last in 2024 and ninth in 2026, winning just four of fourteen matches this year.

"There is only so much a young man can take," the IPL source told PTI. "The last three years haven't been easy for him. The MI dressing room he left in 2021 wasn't the same when he returned in 2024. Not every senior player was on the same page."

The source painted a picture of a fractured dressing room — one where Pandya expected the kind of commitment from senior players that they had once demanded of him in India colours. When results failed to follow, his frustration compounded.

## A Back Injury, Then a Breaking Point

Pandya also battled a back spasm that forced him to miss matches during the season. His bowling economy offered nothing special, and his batting — once MI's most explosive weapon — lacked the sustained impact the five-time champions needed from their leader. The combination of physical strain, persistent fan hostility, and internal friction proved too much.

"If the results come despite differences of opinion, you still won't feel frustrated," the source explained. "But when everyone is pulling in different directions, after a certain point you don't have the mental bandwidth to continue."

## What It Means for MI — and for NRIs Watching From Abroad

Mumbai Indians now face the most significant leadership transition since the original handover from Rohit to Hardik. The franchise, which has won five IPL titles, must find not just a captain but a cultural reset. Names like Suryakumar Yadav and Jasprit Bumrah — who captained a match for the first time this season — will feature in the conversation.

For NRI fans who grew up watching MI as the IPL's most dominant franchise, this is unfamiliar territory. The blue jersey that once meant inevitability now represents a team in genuine flux.

Former England captain Michael Vaughan has already suggested a swap deal: Pandya to KKR, Cameron Green back to MI. Whether that specific move materialises or not, Pandya's IPL future is now an open question. He remains in India's ODI squad for the Afghanistan series starting June 14 in Dharamshala.

## The Numbers Tell the Story

Under Pandya's captaincy across three seasons, MI's combined record reads: bottom of the table in 2024, a Qualifier 2 exit in 2025, and ninth in 2026. His personal returns with the bat declined season on season, and his bowling workload was limited by recurring fitness concerns.

At 32, Pandya is far from finished as a cricketer. But his MI chapter — one that began with so much promise and ended with boos ringing in his ears — is now closed. The question is which franchise will take the gamble next, and whether a change of scenery can restore the player who once won India a T20 World Cup with a final-over spell in Barbados."""

articles.append({
    "headline": "Hardik Pandya Has Quit Mumbai Indians. He Was Mentally Stressed, Physically Hurt, and Done With the Boos.",
    "subheadline": "The all-rounder informed the franchise mid-season that he would not return. Both sides have reached a mutual understanding to part ways after three turbulent years.",
    "body": body1.strip(),
    "slug": "hardik-pandya-quits-mumbai-indians-mentally-stressed-three-seasons-mi-ipl-2026-20260529",
    "sources": [
        {"name": "PTI via Swadesi", "url": "https://swadesi.com"},
        {"name": "Livemint", "url": "https://livemint.com"},
        {"name": "CricTracker", "url": "https://crictracker.com"},
        {"name": "The Indian Express", "url": "https://indianexpress.com"}
    ],
    "image_url": img1,
    "image_attribution": attr1,
})


# ────────────────────────────────────────────────────
# ARTICLE 2: Rishabh Pant Steps Down as LSG Captain
# ────────────────────────────────────────────────────
print("\n📰 Article 2: Rishabh Pant Steps Down as LSG Captain")

img2, attr2 = get_image(person_name="Rishabh Pant")

body2 = """Rishabh Pant has stepped down as captain of the Lucknow Super Giants. The franchise confirmed on Friday that Pant approached the management to be relieved of his captaincy duties, and the request was accepted with immediate effect.

It ends a tenure that lasted twenty-eight matches, produced ten wins and eighteen defeats, and never once reached the IPL playoffs.

## The ₹27 Crore Experiment

When LSG signed Pant for a tournament-record ₹27 crore at the 2025 mega auction, owner Sanjiv Goenka said the wicketkeeper-batter's leadership would "be discussed in the same breath as MS Dhoni and Rohit Sharma." Two seasons later, that comparison looks cruel rather than aspirational.

LSG finished seventh in 2025 with six wins and last in 2026 with just four. Pant's individual numbers declined in parallel: 269 runs in his first LSG season — 118 of which came in a single dead-rubber match against RCB — and 312 runs in 2026 at a strike rate of 138.05 with just one half-century and a highest score of 68 not out.

For a player once considered India's most destructive white-ball batter, those are sobering numbers.

## The Wider Slide

The captaincy exit at LSG is not an isolated event. Pant recently lost India's Test vice-captaincy to KL Rahul ahead of the one-off Test against Afghanistan, scheduled for June 6 in New Chandigarh. His Test batting average has also dropped noticeably from its peak, and the aura of invincibility that surrounded him after his heroic Gabba hundred in 2021 and his recovery from the near-fatal car accident in 2022 has quietly dissipated.

Tom Moody, LSG's director of cricket, struck a diplomatic tone in the official statement: "Rishabh approached the franchise with this request and we have respectfully accepted it. These decisions are never easy. We are grateful for everything Rishabh has brought to this dressing room as captain. Our focus now is on the collective — rebuilding and restructuring to reach the best standards."

## Two Captains Gone in One Day

Pant's resignation came on the same day PTI reported that Hardik Pandya has decided to leave Mumbai Indians entirely. Both franchises finished in the bottom two of the IPL 2026 table. Both captains were mega-auction acquisitions expected to transform their teams. Both experiments failed comprehensively.

The parallel is difficult to ignore: the IPL's reliance on big-money captaincy appointments is being tested, and the evidence from 2026 suggests that leadership cannot be bought at auction.

## What Comes Next for LSG — and for NRI Fans

LSG has not named a successor. The franchise said a new captain "will be named in due course," suggesting internal evaluations are ongoing. Nicholas Pooran, who has captained West Indies in T20Is, and Quinton de Kock, who led South Africa and was previously at LSG, could feature in discussions if they remain on the roster.

For NRI fans who followed Pant's remarkable journey — from the car crash recovery to the Test heroics in Australia and England — watching him step down from a captaincy in these circumstances is a deflating moment. He remains contracted to LSG as a player, and at twenty-eight, there is time to rebuild. But the captain's armband is gone, and the burden of that ₹27 crore price tag has never felt heavier."""

articles.append({
    "headline": "Rishabh Pant Has Stepped Down as LSG Captain. Ten Wins and Eighteen Defeats in Twenty-Eight Matches.",
    "subheadline": "The ₹27 crore record signing asked to be relieved of his duties after Lucknow Super Giants finished last in IPL 2026. The franchise accepted immediately.",
    "body": body2.strip(),
    "slug": "rishabh-pant-steps-down-lsg-captain-27-crore-record-ipl-2026-last-place-20260529",
    "sources": [
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "Livemint", "url": "https://livemint.com"},
        {"name": "Yardbarker", "url": "https://yardbarker.com"},
        {"name": "ANI via LatestLY", "url": "https://latestly.com"}
    ],
    "image_url": img2,
    "image_attribution": attr2,
})


# ────────────────────────────────────────────────────
# ARTICLE 3: India Squads for Afghanistan Series
# ────────────────────────────────────────────────────
print("\n📰 Article 3: India vs Afghanistan Series Preview")

img3, attr3 = get_image(person_name="Shubman Gill", pexels_query="cricket stadium India", pexels_fallback="cricket match")

body3 = """The BCCI has announced India's squads for the upcoming home series against Afghanistan, and the selections tell you exactly where Indian cricket's priorities lie as the 2027 World Cup approaches. Players have been asked to assemble in New Chandigarh by June 2 — just two days after Sunday's IPL final in Ahmedabad.

The tour consists of one Test match from June 6 to 10 at the Maharaja Yadavindra Singh International Cricket Stadium in New Chandigarh, followed by three ODIs in Dharamshala (June 14), Lucknow (June 17), and Chennai (June 20).

## Shubman Gill Leads Both Squads

The 26-year-old captains India in both formats, cementing his position as the country's long-term leadership choice. KL Rahul serves as vice-captain for the Test and Shreyas Iyer takes the role for the ODI series — a split that reflects the BCCI's ongoing management of workloads and format specialisation.

The Test squad features several players fresh from IPL playoff action: Yashasvi Jaiswal, Dhruv Jurel, Sai Sudharsan, Prasidh Krishna, Mohammed Siraj, and Washington Sundar all feature in both the IPL's business end and the Test squad. For Jurel in particular — who has been RR's most reliable performer behind the stumps this IPL — the transition from T20 to five-day cricket will be nearly instantaneous.

Devdutt Padikkal, Nitish Kumar Reddy, Gurnoor Brar, Harsh Dubey, and Manav Suthar round out a Test squad that leans heavily on youth. Kuldeep Yadav provides the senior spin option.

## Kohli and Rohit Return for ODIs

The ODI squad is where the star power concentrates. Virat Kohli and Rohit Sharma — both now retired from Tests and T20Is — return to the India setup for the first time since the 2025 Champions Trophy. With the 2027 Cricket World Cup in South Africa less than eighteen months away, these three ODIs against Afghanistan represent the start of India's serious preparation.

Hardik Pandya's inclusion in the ODI squad carries particular irony given the morning's news of his departure from Mumbai Indians. He remains a central figure in India's white-ball plans regardless of his franchise situation, and his all-round ability in 50-over cricket is difficult to replace.

Ishan Kishan returns as the ODI wicketkeeper option alongside KL Rahul, while Arshdeep Singh and Prince Yadav provide pace depth.

## The Afghanistan Challenge

This is Afghanistan's first bilateral series against India since a three-game T20I series in January 2024. The Test will be just Afghanistan's second ever against India — their first, in 2018, ended in a loss by an innings and 262 runs in Bengaluru. The Test does not count towards the World Test Championship cycle.

Afghanistan arrive with a squad led by Hashmatullah Shahidi and featuring familiar IPL names: Rashid Khan, Rahmanullah Gurbaz, and Allah Ghazanfar (who was Mumbai Indians' leading wicket-taker this IPL). Azmatullah Omarzai, one of the most improved all-rounders in world cricket, will be the key threat with both bat and ball.

## A Diaspora Summer of Cricket

For NRIs in India this summer or planning trips, the series offers accessible live cricket across four venues. New Chandigarh's stadium hosted IPL matches this season and is well-served by Chandigarh airport. Dharamshala's HPCA Stadium is one of the most scenic grounds in world cricket. Lucknow and Chennai provide options for fans across north and south India.

The ODI series at 1:30 PM IST start times also means reasonable morning viewing hours for East Coast NRIs and late-night viewing for those on the West Coast — a consideration that matters as India begins its serious World Cup preparation cycle.

After this series, India heads to Ireland for two T20Is starting June 26, then to England for five T20Is and three ODIs beginning July 1. The summer of Indian cricket has begun, and it starts with Afghanistan in Chandigarh in eight days."""

articles.append({
    "headline": "Kohli and Rohit Return for the ODIs. Gill Captains Both Squads. India's Afghanistan Series Starts in Eight Days.",
    "subheadline": "The BCCI has named squads for one Test and three ODIs against Afghanistan across New Chandigarh, Dharamshala, Lucknow, and Chennai. Players assemble June 2.",
    "body": body3.strip(),
    "slug": "india-afghanistan-series-squads-kohli-rohit-gill-test-odi-june-2026-nri-guide-20260529",
    "sources": [
        {"name": "Wikipedia - Afghan cricket team in India in 2026", "url": "https://en.wikipedia.org/wiki/Afghan_cricket_team_in_India_in_2026"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "SportsTiger", "url": "https://sportstiger.com"},
        {"name": "Cricbuzz", "url": "https://cricbuzz.com"}
    ],
    "image_url": img3,
    "image_attribution": attr3,
})


# ── Publish all ──
print("\n" + "="*60)
print("Publishing articles...")
print("="*60)

success_count = 0
for i, article in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {article['headline'][:70]}...")
    # Word count check
    word_count = len(article["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ⚠ SKIPPED: Below 400 word minimum")
        continue
    if not article.get("image_url"):
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")
    if publish_article(article):
        success_count += 1
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {success_count}/{len(articles)} articles.")
print(f"{'='*60}")
