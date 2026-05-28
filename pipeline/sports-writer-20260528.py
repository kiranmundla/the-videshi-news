#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-28 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── env ──
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──
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
    """Fetch a relevant image from Pexels via curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Verify it's a real image
                    head = requests.head(url, timeout=10)
                    clen = int(head.headers.get("Content-Length", "0"))
                    if head.status_code == 200 and clen > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    try:
        # Check for banned sources
        banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
        if any(b in url for b in banned):
            print(f"  ✗ BANNED source: {url[:80]}")
            return False
        ua = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        head = requests.head(url, timeout=10, allow_redirects=True, headers=ua)
        ctype = head.headers.get("Content-Type", "")
        clen = int(head.headers.get("Content-Length", "0"))
        if head.status_code == 200 and "image" in ctype and clen > 5000:
            return True
        # Retry with GET if HEAD fails (some servers don't support HEAD)
        if head.status_code != 200:
            resp = requests.get(url, timeout=10, headers=ua, stream=True)
            ctype = resp.headers.get("Content-Type", "")
            clen = int(resp.headers.get("Content-Length", "0"))
            resp.close()
            if resp.status_code == 200 and "image" in ctype and clen > 5000:
                return True
        print(f"  ✗ Image validation failed: status={head.status_code} type={ctype} len={clen}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert article into p2_articles."""
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Format sources as JSON array of objects with name key
    raw_sources = article.get("sources", [])
    formatted_sources = []
    for s in raw_sources:
        if isinstance(s, str):
            # Split on " — " to get name and description
            parts = s.split(" — ", 1)
            formatted_sources.append({"name": parts[0].strip(), "url": parts[1].strip() if len(parts) > 1 else ""})
        elif isinstance(s, dict):
            formatted_sources.append(s)

    payload = {
        "id": article_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now,
        "sources": json.dumps(formatted_sources),
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
    }

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if resp.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}... (id={article_id})")
        return article_id
    else:
        print(f"  ✗ Failed to publish: {resp.status_code} {resp.text[:200]}")
        return None


# ══════════════════════════════════════════════════════════════
# ARTICLES
# ══════════════════════════════════════════════════════════════

articles = []

# ── ARTICLE 1: FIFA World Cup Broadcast Crisis ──
print("\n═══ Article 1: FIFA World Cup Broadcast Crisis in India ═══")

art1_img = fetch_pexels_image("FIFA World Cup football stadium crowd", "world cup football fans")
if art1_img and not validate_image(art1_img):
    art1_img = None

articles.append({
    "headline": "The World Cup Starts in Two Weeks. India Still Does Not Have a Broadcaster.",
    "subheadline": "FIFA wanted a hundred million dollars. Reliance offered twenty. Zee entered talks this week. NRIs in America will watch every match. Their families in India might not see a single one.",
    "slug": "fifa-world-cup-2026-india-broadcast-crisis-zee-reliance-disney-nri-20260528",
    "image_url": art1_img or "",
    "image_caption": "The 2026 FIFA World Cup kicks off June 11 across the United States, Canada, and Mexico",
    "image_attribution": "Pexels" if art1_img else "",
    "sources": [
        "Reuters — Zee Entertainment in talks with FIFA on World Cup broadcast rights in India",
        "Exchange4Media — FIFA set to close India media rights deal for World Cup soon",
        "BestMediaInfo — The FIFA World Cup 2026 is coming to every screen in Asia except India"
    ],
    "body": """The 2026 FIFA World Cup begins on June 11. Forty-eight nations will play across sixteen cities in the United States, Canada, and Mexico. FIFA has sold broadcast rights in more than 180 countries. India is not one of them.

With barely two weeks remaining before the opening match, the world's most-watched sporting event has no confirmed broadcaster in the country of 1.4 billion people. For the Indian diaspora scattered across North America — living in the very cities hosting the tournament — the irony is extraordinary. They will watch matches at MetLife Stadium, SoFi, and AT&T Stadium. Their parents, siblings, and friends in Mumbai, Delhi, and Chennai may not be able to watch at all.

## The Money Problem

The deadlock is about price. FIFA initially sought $100 million for the combined broadcast rights to the 2026 and 2030 World Cups in India. That number has been revised downward — reports suggest FIFA is now looking for somewhere between $35 million and $60 million — but the gap between what FIFA wants and what Indian broadcasters are willing to pay remains vast.

JioHotstar, the Reliance-Disney joint venture that broadcast the 2022 World Cup, has reportedly maintained an offer of approximately $20 million. FIFA has rejected it. Sony, the other major sports broadcaster in India, declined to bid at all.

On Tuesday, Zee Entertainment entered the conversation. The company confirmed it is in talks with FIFA to stream and broadcast the tournament through its Unite8 Sports initiative, though no financial details were disclosed. Whether Zee can close a deal in the next fourteen days — when larger players with deeper pockets could not — remains an open question.

## A Cricket Country's Football Problem

The underlying issue is structural. India is a cricket-first market. The IPL alone commands billions in broadcast revenue. Football, despite a passionate and growing fanbase, does not generate the advertising returns that justify World Cup-level pricing.

In 2022, India accounted for roughly 2.9 percent of the World Cup's global linear TV reach — significant in absolute numbers given India's population, but a fraction of what cricket delivers to advertisers. The tournament's timing this year compounds the problem: the IPL final is May 31, and the World Cup begins eleven days later. Advertisers who just spent heavily on cricket may not have the budget for football.

A petition has been filed in Indian courts arguing that depriving millions of fans of the World Cup broadcast would be unjust. The petition invokes Article 226 of the Constitution, though its legal prospects are uncertain.

## What This Means for NRIs

For the estimated 4.4 million Indian-origin residents in the United States alone, the situation creates a surreal split screen. NRIs in the New York metro area can walk to MetLife Stadium to watch group-stage matches. NRIs in Los Angeles can attend games at SoFi Stadium, where the US opens against Paraguay on June 12. Houston, with its massive South Asian community, hosts multiple matches at NRG Stadium.

But when these fans call home to discuss the matches, their families may have nothing to watch. No legal stream, no TV broadcast, no highlights package.

India is not the only market where football struggles against cricket — Pakistan faces similar dynamics — but it is by far the largest. The 2022 World Cup final between Argentina and France drew an estimated 1.5 billion viewers globally. The idea that India could be blacked out entirely from the 2026 edition would have seemed absurd even six months ago.

## The Clock Is Ticking

FIFA and potential Indian broadcasters have approximately fourteen days to close a deal. If Zee's talks succeed, the tournament could land on Zee5 and its linear channels. If they fail, India joins a vanishingly small list of major nations without World Cup coverage.

For NRIs, the situation is a reminder of a familiar truth: the diaspora experience often means straddling two worlds that operate on entirely different logics. In one world, the World Cup is two weeks away and the excitement is building. In the other, no one is even sure they will be able to watch it."""
})


# ── ARTICLE 2: Dhruv-Tanisha Olympic Medalist Upset ──
print("\n═══ Article 2: Dhruv-Tanisha Upset at Singapore Open ═══")

art2_img = fetch_wikipedia_person_image("Tanisha Crasto")
if not art2_img:
    art2_img = fetch_wikipedia_person_image("Dhruv Kapila (badminton)")
if not art2_img:
    art2_img = fetch_wikipedia_person_image("Dhruv Kapila")
if not art2_img:
    art2_img = fetch_pexels_image("badminton mixed doubles match", "badminton court shuttlecock")
if art2_img and not validate_image(art2_img):
    art2_img = None

articles.append({
    "headline": "They Lost the First Game 8-21. Then Dhruv Kapila and Tanisha Crasto Destroyed an Olympic Medalist.",
    "subheadline": "The unseeded Indian mixed doubles pair staged one of the most dramatic comebacks of the badminton season to knock out Japan's Yuta Watanabe and Maya Taguchi at the Singapore Open.",
    "slug": "dhruv-kapila-tanisha-crasto-upset-olympic-medalist-watanabe-singapore-open-2026-20260528",
    "image_url": art2_img or "",
    "image_caption": "Dhruv Kapila and Tanisha Crasto have risen to a career-high world No. 17 in mixed doubles",
    "image_attribution": "Wikimedia Commons" if (art2_img and "wikimedia" in (art2_img or "").lower()) or (art2_img and "wikipedia" in (art2_img or "").lower()) else ("Pexels" if art2_img else ""),
    "sources": [
        "myKhel — Singapore Open 2026: Unseeded Indian Pair Dhruv-Tanisha Stun Olympic Medallist Watanabe & Taguchi",
        "IANS — Singapore Open: Sindhu, Lakshya, Satwik-Chirag, Tanisha-Dhruv march into QFs",
        "The Bridge — Badminton: Tanisha Crasto-Dhruv Kapila climb to career high world ranking"
    ],
    "body": """At 8-21 down after the first game, Dhruv Kapila and Tanisha Crasto looked finished. The scoreline was not merely lopsided — it was the kind of deficit that suggests a mismatch, a pairing that does not belong on the same court as its opponents.

Their opponents were Yuta Watanabe and Maya Taguchi of Japan. Watanabe is an Olympic bronze medalist from the Tokyo Games. Taguchi is one of the most experienced mixed doubles players on the World Tour. The match, a quarterfinal-round contest at the Singapore Open 2026 — a BWF Super 750 event with a million-dollar prize pool — was supposed to be a formality for the Japanese pair.

It was not.

## The Comeback

What followed the first-game demolition was one of the most remarkable turnarounds of the badminton season. Kapila and Crasto regrouped between games and came out with a fundamentally different approach. They attacked the net with more aggression, disrupted Watanabe's rhythm with sharper returns, and forced errors from a pair that had barely made any in the opening game.

The second game went 21-17 to the Indians. Not a blowout, but a clear and controlled reversal. By the third game, the momentum had shifted completely. Kapila and Crasto won it 21-16, and the Japanese pair that had seemed untouchable thirty minutes earlier walked off the court eliminated.

Final score: 8-21, 21-17, 21-16.

## Who Are They?

Dhruv Kapila, 27, is from Hyderabad. Tanisha Crasto, 21, is from Goa — born into a family with deep badminton roots (her sister Ashwini Ponnappa is one of India's most decorated doubles players). Together, they have been climbing the world rankings steadily over the past two years. After a quarterfinal run at the 2025 Badminton Asia Championships, they reached a career-high world ranking of No. 17.

But rankings only tell part of the story. Mixed doubles has historically been India's weakest discipline. The country has produced world-class singles players — Saina Nehwal, PV Sindhu, Kidambi Srikanth — and a genuinely elite men's doubles pair in Satwiksairaj Rankireddy and Chirag Shetty. But mixed doubles has been a persistent blind spot, a category where India rarely advances past the early rounds of major tournaments.

Kapila and Crasto are changing that narrative. Their partnership, which began in earnest in 2023, has evolved from a developmental project into a legitimate threat at the highest level. Beating an Olympic medalist at a Super 750 event is not a fluke — it is a statement.

## Part of Something Bigger

Their Singapore Open run is part of a broader Indian surge at the tournament. PV Sindhu, Lakshya Sen, Satwiksairaj Rankireddy and Chirag Shetty, and HS Prannoy have all advanced deep into the draw. India had five entries across disciplines in the quarterfinals — the kind of depth that would have been unthinkable a decade ago.

For the diaspora, this matters beyond the scoreboard. Badminton is a sport that many NRI families grew up playing — in backyards in Chennai, in community halls in Hyderabad, in school gymnasiums across India. The sport's presence in the Indian cultural memory is deep even if its professional infrastructure was, until recently, thin. Watching India compete credibly across multiple disciplines at the world's top tournaments is a validation of something families have believed for generations: that India can be a badminton power.

## What Comes Next

Kapila and Crasto now face Malaysia's Chen Tang Jie and Toh Ee Wei in the quarterfinals proper — another formidable pair. Whether they can sustain the magic of their Watanabe-Taguchi comeback remains to be seen.

But even if their run ends here, the result stands. An unseeded Indian pair lost the first game 8-21 against an Olympic medalist and came back to win the match. In a sport where India's mixed doubles program was an afterthought for decades, that is not a footnote. It is a beginning."""
})


# ── ARTICLE 3: Women's T20 World Cup NRI Guide ──
print("\n═══ Article 3: Women's T20 World Cup in England ═══")

art3_img = fetch_wikipedia_person_image("Smriti Mandhana")
if not art3_img:
    art3_img = fetch_wikipedia_person_image("Harmanpreet Kaur")
if not art3_img:
    art3_img = fetch_pexels_image("women cricket match India", "cricket stadium England")
if art3_img and not validate_image(art3_img):
    art3_img = None

articles.append({
    "headline": "India vs Pakistan on June 14 in Birmingham. The Women's T20 World Cup Is Two Weeks Away.",
    "subheadline": "The biggest tournament in women's cricket is being held in England — home to the largest NRI population outside India. Here is everything the diaspora needs to know.",
    "slug": "womens-t20-world-cup-2026-india-pakistan-june-birmingham-nri-guide-england-20260528",
    "image_url": art3_img or "",
    "image_caption": "Smriti Mandhana leads India's batting lineup into the Women's T20 World Cup in England",
    "image_attribution": "Wikimedia Commons" if (art3_img and ("wikimedia" in (art3_img or "").lower() or "wikipedia" in (art3_img or "").lower())) else ("Pexels" if art3_img else ""),
    "sources": [
        "Wikipedia — India women's cricket team in England in 2026",
        "Sportradar — ICC T20 World Cup Women 2026 schedule",
        "SportsCafe — ENG vs IND T20 Series England vs India Women Squads",
        "IANS — Focus on bowling unit as India begin key World Cup rehearsal against England"
    ],
    "body": """The ICC Women's T20 World Cup begins on June 12 in England and Wales. India's opening match is against Pakistan on June 14 at Edgbaston in Birmingham. For the estimated 1.8 million people of Indian origin living in the United Kingdom, this is not a tournament happening somewhere far away. It is happening in their backyard.

Birmingham alone has one of the highest concentrations of British Indians in the country. Edgbaston — a ground that has hosted multiple India-England men's Tests to packed stands of Indian fans — will be the venue for what is arguably the most emotionally charged fixture in women's cricket. India versus Pakistan, in a World Cup, in a city where the diaspora can walk to the ground.

## India's Path

India are the reigning champions. They won the ICC Women's T20 World Cup title in the most recent edition, and they enter this tournament as one of the favorites. The squad, led by Harmanpreet Kaur, features a formidable top order — Shafali Verma's explosive power, Smriti Mandhana's elegance, and Jemimah Rodrigues's inventiveness give India one of the most dangerous batting lineups in the tournament.

The bowling has been the question mark. India's three-match T20I series against England, which begins today at Chelmsford, is specifically designed to answer it. Deepti Sharma, Arundhati Reddy, Sneh Rana, and Renuka Singh are all in the touring party. How they perform against a strong England batting lineup in English conditions will determine India's bowling combinations for the World Cup.

India's group-stage schedule after the Pakistan opener includes the Netherlands on June 17 and Australia on June 28 — the last of those being a match that could decide group standings. The knockout rounds follow in late June and early July, with the final scheduled for July 5.

## Why This Tournament Matters for NRIs

Previous Women's T20 World Cups have been held in Australia, the Caribbean, South Africa, and the UAE. For most NRIs, attending in person was impractical. This time is different.

The tournament is spread across seven venues in England and Wales: Edgbaston (Birmingham), Lord's (London), The Oval (London), Old Trafford (Manchester), Headingley (Leeds), Sophia Gardens (Cardiff), and the County Ground (Bristol). Every one of these cities has a significant Indian-origin population. The logistics of attending a match — no intercontinental flights, no visa complications for UK residents — are trivial compared to previous editions.

This accessibility matters because women's cricket in India has undergone a transformation in the past five years. The Women's Premier League launched in 2023 and has grown into a genuine domestic competition. India's results have followed: consistent performances in bilateral series, competitive showings in ICC events, and now a World Cup defense.

For the diaspora, supporting the women's team in person is a way to participate in that transformation — to move beyond the familiar cycle of men's cricket fandom and invest in a team that is building something new.

## The India-Pakistan Factor

India versus Pakistan in any sport commands attention that transcends the game itself. In women's cricket, the rivalry has been less explored than its men's equivalent, partly because the teams have met less frequently and partly because the commercial infrastructure around women's cricket is still developing.

But June 14 at Edgbaston could be a watershed moment. If the stadium fills — and given Birmingham's demographics, it very likely will — it would be the largest live audience for a women's India-Pakistan cricket match in history. The atmosphere at Edgbaston during men's India matches has been compared to playing in India. For the women's team, experiencing that level of support in a World Cup opener would be unprecedented.

## What to Watch For

Beyond the headline fixture, India's World Cup campaign will be defined by a few key questions. Can Shafali Verma, who turns 22 during the tournament, deliver the consistency that her talent has always promised? Will Richa Ghosh's power-hitting at number five or six give India the finishing ability they have sometimes lacked? And can the bowling attack, which has historically relied heavily on spin, adapt to English conditions that may offer more for seam?

The bilateral series against England starting today is the first test. The World Cup — and that June 14 date at Edgbaston — is the real one.

For NRIs in the UK, the message is simple: this is the most accessible major cricket tournament in memory, featuring a team that has genuine title credentials, opening against Pakistan in a city that feels like home. The tickets are available. The ground is close. The moment is now."""
})


# ══════════════════════════════════════════════════════════════
# PUBLISH ALL
# ══════════════════════════════════════════════════════════════

print(f"\n═══ Publishing {len(articles)} articles ═══\n")

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n── Article {i}: {art['headline'][:60]}...")
    word_count = len(art["body"].split())
    print(f"   Words: {word_count}")
    if word_count < 400:
        print(f"   ✗ REJECTED: below 400 word minimum")
        continue
    if not art.get("subheadline") or len(art["subheadline"]) < 15:
        print(f"   ✗ REJECTED: subheadline missing or too short")
        continue
    if not art.get("slug") or art["slug"] != art["slug"].lower():
        print(f"   ✗ REJECTED: slug issue")
        continue

    result = publish_article(art)
    if result:
        published += 1
    time.sleep(1)

print(f"\n═══ Done. Published {published}/{len(articles)} articles. ═══")
