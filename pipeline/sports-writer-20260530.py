#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-30 batch."""

import json, os, sys, time, uuid, urllib.parse, re
from datetime import datetime, timezone

import requests

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Wikipedia image ──────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ── Pexels image ─────────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels as fallback. Uses curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


# ── Image upload to Supabase storage ─────────────────────────────────────
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        resp = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠ Image download failed ({resp.status_code}): {image_url[:80]}")
            return image_url  # fallback to original
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image ({content_type}): {image_url[:80]}")
            return image_url
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small ({len(resp.content)} bytes)")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=resp.content,
            timeout=30,
        )
        if upload_resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({upload_resp.status_code}): {upload_resp.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url


# ── Image validation ─────────────────────────────────────────────────────
def validate_image_url(url):
    """Ensure image URL is valid, permanent, and not from banned sources."""
    if not url:
        return None
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "scontent-"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source: {url[:80]}")
            return None
    for p in banned_params:
        if p in url:
            print(f"  ✗ BANNED param: {url[:80]}")
            return None
    try:
        resp = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            print(f"  ⚠ Image HEAD returned {resp.status_code}")
            return None
        ct = resp.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ⚠ Not image content-type: {ct}")
            return None
        cl = int(resp.headers.get("Content-Length", 0))
        if 0 < cl < 5000:
            print(f"  ⚠ Image too small: {cl} bytes")
            return None
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return url


# ── Supabase insert ──────────────────────────────────────────────────────
def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({resp.status_code}): {resp.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────────

articles = []

# ── Article 1: Satwik-Chirag beat World No. 1 to reach Singapore Open final ──
articles.append({
    "headline": "Satwik and Chirag Beat the World's Best Doubles Pair to Reach the Singapore Open Final.",
    "subheadline": "India's top men's doubles duo knocked out top seeds Kim Won-ho and Seo Seung-jae 21-19, 21-18 in a controlled semifinal display. They will play for the title on Sunday.",
    "slug": "satwik-chirag-beat-world-no-1-singapore-open-final-2026-kim-seo-semifinal",
    "category": "sports",
    "vertical": "sports",
    "body": """Satwiksairaj Rankireddy and Chirag Shetty are through to the Singapore Open final after beating top seeds Kim Won-ho and Seo Seung-jae 21-19, 21-18 in the men's doubles semifinals on Saturday.

The Indian fourth seeds took on the reigning World Champions and current World No. 1 pair from South Korea — a combination that has dominated the circuit for the past two years — and won in straight games, controlling the tempo from the opening rally to the final point.

## A Statement Win Against the Best

The scoreline reads straight games, but the match was anything but comfortable. Both games were tight deep into the stretch. At 18-18 in the first game, Satwik unleashed a steep crosscourt smash that left Kim stranded at the net, and Chirag followed with a clinical net kill to take a mini-break. The Indians closed out the game 21-19 with a sharp flat serve down the middle.

The second game followed a similar pattern. The Korean pair led 12-10 at the interval, but Satwik and Chirag shifted gears after the break, stringing together five consecutive points with a mix of deceptive pushes and powerful drives. At 19-18, Chirag produced the shot of the match — a backhand intercept at the net that clipped the tape and fell on the Korean side. A Satwik serve sealed it 21-18.

## The Route to the Final

Satwik and Chirag arrived at the semifinal through a series of increasingly difficult three-game battles. They dropped their opening game in both the second round and the quarterfinals before recovering composure. Against Malaysia's Kang Khai Xing and Aaron Tai in the quarterfinals, they fell behind 19-21 in the opener before surging back to win 21-17, 21-13 — the kind of resilience that has defined their partnership.

The semifinal against Kim and Seo, however, required no such comeback. The Indians were ahead or level throughout, a sign that they have developed the big-match poise necessary to beat the very best when it matters.

## What the NRI Audience Should Know

For the Indian diaspora, Satwik and Chirag are now the most consistent medal contenders India has in any racquet sport. Since their historic 2022 World Championship bronze, they have reached six semifinals in Super 750-level events this year alone. A title here would be their first at this level in 2026 and a major confidence boost heading into the second half of the Olympic qualifying cycle.

They will face either Indonesia's Fajar Alfian and Muhammad Shohibul Fikri or China's Liang Weikeng and Wang Chang in Sunday's final. Either matchup would test different dimensions of the Indian pair's game — Indonesia's flat drives or China's aerial power.

## India's Singles Challenge Ends

While Satwik and Chirag advanced, both of India's singles hopes ended in the quarterfinals on Friday. PV Sindhu lost to world No. 1 An Se Young 17-21, 14-21, extending her winless streak against the Korean to nine consecutive matches. Lakshya Sen also fell, beaten 19-21, 21-15, 15-21 by Japan's Koki Watanabe. The mixed doubles pair of Dhruv Kapila and Tanisha Crasto also reached the semifinals, giving India two shots at the title.

The Singapore Open final is scheduled for Sunday, May 31. For NRIs in the United States and Canada, the match will be available on BWF TV, with the men's doubles final expected in the late morning IST slot — which translates to the early morning hours in North American time zones.""",
    "sources": json.dumps([
        {"name": "BWF / Wikipedia Singapore Open 2026 bracket", "url": "https://en.wikipedia.org/wiki/2026_Singapore_Open_(badminton)"},
        {"name": "IndiaSportsHub", "url": "https://indiasportshub.com"},
        {"name": "Newzly", "url": "https://newzly.co.in"}
    ]),
    "image_person": "Satwiksairaj Rankireddy",
    "image_fallback_query": "badminton doubles match tournament",
    "image_fallback_query2": "badminton court competition",
})

# ── Article 2: Avni LLC Indian-American firm claims FIFA India broadcast rights ──
articles.append({
    "headline": "A Washington DC Investment Firm Run by an Indian American Says It Has the FIFA World Cup Broadcast Rights for India.",
    "subheadline": "Avni LLC claims a $300 million corporate guarantee and a winning bid through FIFA's closed tender. India still has no confirmed broadcaster twelve days before kickoff.",
    "slug": "avni-llc-indian-american-firm-fifa-world-cup-2026-india-broadcast-rights-nri",
    "category": "sports",
    "vertical": "sports",
    "body": """With the FIFA World Cup 2026 set to kick off on June 11, India remains without a confirmed broadcaster for the tournament — and the latest twist involves an Indian-American investment firm from Washington DC that claims it holds the winning bid.

Avni LLC, led by President and CEO Deelip Mhaske, says it submitted a corporate guarantee backed by financial commitments exceeding $300 million in February 2026 as part of FIFA's closed tender process for the Indian subcontinent. The firm claims an associated partner secured the winning bid after competing against several major Indian broadcasters.

## A Vision Beyond Traditional Television

What makes Avni's claim notable is its ambition. The firm is not pitching a conventional television deal. Instead, it envisions a distribution model built around OTT platforms, AI-powered multilingual broadcasting in multiple Indian languages, mobile micro-subscriptions for the price-sensitive Indian market, and esports integrations across Asia.

"The Indian subcontinent alone has the ability to exceed initial valuation expectations," Mhaske said in a statement.

The pitch reflects a broader bet — that India's football market, while dwarfed by cricket in traditional advertising terms, has untapped potential in digital consumption. With over 700 million smartphone users and growing football fandom among younger demographics, the logic is not unreasonable.

## The Broadcast Crisis in Context

The contrast with other markets is stark. China's state broadcaster CMG sealed a comprehensive deal with FIFA on May 15. Japan, South Korea, the UK, Brazil, and virtually every major football market has confirmed arrangements. India, one of the world's largest and fastest-growing football markets by population, stands as a conspicuous exception.

The reasons are well-documented. Cricket commands India's advertising rupees with a grip football cannot match. Worse, the tournament is hosted across the United States, Canada, and Mexico, meaning most matches will kick off late at night or in the early hours for Indian viewers — precisely the slots that make advertisers nervous and audiences thin.

JioStar and Sony, the two broadcasters who have historically written the biggest cheques for global sports events in India, have not bitten at FIFA's asking price. Reports suggest Reliance offered just $20 million — a fraction of what FIFA sought.

## The Public Interest Angle

Into this vacuum has stepped the Indian government. The Delhi High Court has issued notices to Prasar Bharati following a petition seeking mandatory free-to-air broadcast on DD Sports and Doordarshan. Justice Purushaindra Kumar Kaurav issued the notices after hearing a writ petition filed under Article 226 of the Constitution.

For NRIs, the question is both practical and emotional. Those in the United States and Canada will be able to watch the World Cup on Fox, Telemundo, and other local networks. But for family back home, and for the principle of access in the world's most populous country, the India broadcast situation has become an embarrassment.

## What Comes Next

FIFA has maintained only that discussions in India "are ongoing and must remain confidential at this stage." Whether Avni LLC's claim translates into actual broadcast delivery remains to be seen. The firm is not a household name in media, and a $300 million guarantee from a Washington DC LLC would need substantial verification.

But the very fact that an Indian-American entrepreneur from the diaspora is positioning himself at the center of India's World Cup broadcast crisis speaks to how unusual the situation has become. Twelve days remain before the first match. The clock is running.""",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "Reuters via FIFA broadcast crisis report", "url": "https://reuters.com"},
        {"name": "Indian Television Dot Com", "url": "https://indiantelevision.com"}
    ]),
    "image_person": None,
    "image_fallback_query": "FIFA World Cup 2026 stadium",
    "image_fallback_query2": "football soccer world cup stadium",
})

# ── Article 3: Nousheen Naz 15-year-old scores both goals for India Women U18 Hockey ──
articles.append({
    "headline": "A Fifteen-Year-Old Scored Both Goals. India's Women Beat Malaysia 2-1 in Their Asia Cup Opener.",
    "subheadline": "Nousheen Naz converted a penalty corner and a field goal as India held off a late Malaysian fightback in Kakamigahara. South Korea, who thrashed Singapore 8-0, are next.",
    "slug": "nousheen-naz-india-women-u18-hockey-asia-cup-2026-malaysia-opener-kakamigahara",
    "category": "sports",
    "vertical": "sports",
    "body": """Nousheen Naz, a fifteen-year-old forward, scored both goals as India's Women's U18 hockey team opened their Asia Cup 2026 campaign with a hard-fought 2-1 victory over Malaysia in Kakamigahara, Japan, on Saturday.

Naz was named Player of the Match after converting a penalty corner in the 19th minute and adding a field goal in the 28th, giving India a 2-0 lead at halftime before Malaysia pulled one back through Nur Azli in the 41st minute.

## A Teenager Sets the Tone

The opening quarter was cagey, with both sides probing each other's defences without finding a breakthrough. India had the greater share of possession and created several half-chances, but the Malaysian defence held firm through the first fifteen minutes.

India's patience paid off early in the second quarter. A well-worked penalty corner routine found Naz positioned inside the circle, and the teenager made no mistake — slotting the ball past the Malaysian goalkeeper with a decisive strike to open the scoring.

Nine minutes later, Naz doubled the lead with a clinical field goal from inside the 'D'. The finish was sharp and demonstrated the kind of composure that belies her age. India went into halftime with a comfortable 2-0 cushion and complete control of the contest.

## Malaysia Fight Back

The third quarter brought a different energy from the Malaysian side. Sensing they had nothing to lose, Malaysia committed more players forward and began to trouble the Indian backline. The pressure told in the 41st minute when Nur Azli found space inside the circle and beat the Indian goalkeeper to make it 2-1.

The goal injected genuine tension into the final quarter. Malaysia pushed hard for the equaliser, creating several opportunities and forcing the Indian defence into sustained stretches of concentration. But the backline held firm, with organized defending and composure under pressure ensuring the lead was preserved.

## Both India Teams Win Their Openers

The women's win mirrors the men's U18 team's dominant 13-0 demolition of Kazakhstan on the previous day, when captain Ketan Kushwaha scored a hat-trick. Together, India's junior hockey teams have started the continental tournament with maximum points in both pools.

For the women, however, the path gets significantly harder. South Korea demolished Singapore 8-0 in the other Pool A match, with Kwon scoring four times from penalty corners. India face the Koreans on Sunday, May 31, in a match that will likely determine the pool winner and the semifinal seeding.

## Why It Matters for the Pipeline

The U18 Asia Cup is not just another age-group tournament. It feeds directly into the senior national team pipeline — a pipeline that has produced results at the Asian Games and the Olympic level. India's senior women's team, led by Savita Punia, has benefited from strong youth development in recent years, and tournaments like this one identify the next generation of international-level players.

Nousheen Naz, at fifteen, has announced herself as one to watch. Her composure under pressure, combined with clinical finishing from both open play and set pieces, suggests a player with the temperament for bigger stages.

The men's U18 team plays hosts Japan on Saturday, May 31, while the women face South Korea on the same day. Both matches will be available on FIH streaming platforms.""",
    "sources": json.dumps([
        {"name": "ANI via The Freedom Press", "url": "https://thefreedompress.in"},
        {"name": "FIH / Wikipedia U18 Asia Cup 2026", "url": "https://en.wikipedia.org/wiki/2026_Women%27s_Hockey_U18_Asia_Cup"},
        {"name": "India Sports Hub", "url": "https://indiasportshub.com"}
    ]),
    "image_person": None,
    "image_fallback_query": "field hockey women India match",
    "image_fallback_query2": "field hockey stick ball turf",
})


# ── Process and publish ──────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}\n")

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n── Article {i}/{len(articles)}: {art['headline'][:60]}...")

    # Image sourcing
    img_url = None
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        # Try disambiguation
        if not img_url:
            img_url = fetch_wikipedia_person_image(f"{art['image_person']} (badminton)")

    if not img_url:
        img_url = fetch_pexels_image(art.get("image_fallback_query"), art.get("image_fallback_query2"))

    img_url = validate_image_url(img_url)

    # Upload to Supabase if it's a Wikipedia/Pexels image
    if img_url and ("upload.wikimedia.org" in img_url or "images.pexels.com" in img_url):
        img_url = upload_image_to_supabase(img_url, f"{art['slug']}.jpg")

    # Build article record
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": "sports",
        "vertical": "sports",
        "body": art["body"].strip(),
        "sources": json.loads(art["sources"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and "wikimedia" in (img_url or "") else "The Videshi",
    }

    art_id = insert_article(record)
    if art_id:
        published += 1
        # If we uploaded to Supabase, update image with article ID
        if img_url and art_id and SUPABASE_URL in str(img_url):
            pass  # already using slug-based naming

    time.sleep(1)  # brief pause between inserts

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")
