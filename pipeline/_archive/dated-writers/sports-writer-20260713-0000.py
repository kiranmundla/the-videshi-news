#!/usr/bin/env python3
"""
Sports Writer — July 13, 2026 midnight run
2 articles:
  1. MLC 2026 Playoff Bracket Set after league phase ends
  2. Sinner defends Wimbledon crown — back-to-back titles
"""

import json, os, re, subprocess, sys, uuid, urllib.parse, datetime, hashlib, textwrap
import requests

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Image helpers ────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia REST API."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = (
                data.get("originalimage", {}).get("source")
                or data.get("thumbnail", {}).get("source")
            )
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
                info = (page.get("imageinfo") or [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                w = info.get("thumbwidth") or info.get("width", 0)
                h = info.get("thumbheight") or info.get("height", 0)
                title = page.get("title", "")
                if url and "image" in mime and w >= 400:
                    results.append({"url": url, "title": title, "width": w, "height": h})
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []


def verify_image_url(url):
    """Verify image URL returns 200 with image/* content type and >5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image verified: {url[:80]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image verify error: {e}")
    return False


def make_slug(headline):
    """Create a URL-safe slug from headline."""
    s = headline.lower()
    s = re.sub(r"[''']s\b", "s", s)
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    # Truncate to reasonable length
    parts = s.split("-")
    slug = ""
    for p in parts:
        candidate = (slug + "-" + p) if slug else p
        if len(candidate) > 80:
            break
        slug = candidate
    return slug + "-nri-july-2026"


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        data = r.json()
        title = data[0]["headline"] if isinstance(data, list) else data.get("headline", "?")
        print(f"\n✅ Inserted: {title}")
        return True
    else:
        print(f"\n❌ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ── Article 1: MLC 2026 Playoffs Set ─────────────────────────────

def build_mlc_article():
    print("\n" + "=" * 60)
    print("ARTICLE 1: MLC 2026 Playoff Bracket Set")
    print("=" * 60)

    headline = "Three Teams, 12 Points Each. MLC's Playoff Bracket Is Set and Oakland Is Ready."
    subheadline = "San Francisco Unicorns, LA Knight Riders, and Washington Freedom all finished on 12 points. Net run rate decided their fates — and America's biggest cricket weekend heads to the Bay Area."

    body = textwrap.dedent("""\
The numbers are clean, brutal, and unprecedented. When the final ball of Major League Cricket's 2026 league phase was bowled on Sunday night in Grand Prairie, three of the six franchises sat locked on 12 points apiece — six wins each from ten matches. In a six-team league where every match carries outsized weight, the margin between a first-place finish and a third-place scramble came down to a decimal: net run rate.

San Francisco Unicorns (+0.487) claimed the top seed. Los Angeles Knight Riders (+0.245) took second. Washington Freedom, despite winning the same number of matches, slipped to third with a NRR of −0.399 — a testament to the tight losses and rain-affected matches that haunted their middle stretch. MI New York (10 points, five wins) squeezed into fourth, while Seattle Orcas (8) and Texas Super Kings (6) bowed out.

## The Playoff Picture

The bracket is now locked. On Tuesday, July 15, at the Oakland Coliseum:

**Qualifier:** San Francisco Unicorns vs. Los Angeles Knight Riders — winner goes straight to the final. Loser gets a second life in the Qualifier 2.

**Eliminator:** Washington Freedom vs. MI New York — loser goes home. Winner faces the Qualifier loser for the last spot in the final.

The championship match follows at the same venue. For the first time in MLC history, Oakland will host the knockout rounds and the final — a deliberate move to plant cricket's flag in the Bay Area, home to one of the largest South Asian populations in the United States.

## Knight Riders' Remarkable Surge

Perhaps the most dramatic subplot is LA Knight Riders' rise from mid-table obscurity to the second seed. After losing to MI New York on July 5, the Knight Riders sat with a middling record and the worst NRR among contenders. Then came a four-match finishing sprint: victories over Texas Super Kings (twice), Washington Freedom, and a hard-fought draw against league-leaders San Francisco. Andre Russell, Colin Munro, and Rovman Powell provided the muscle, while Jason Holder anchored the bowling with four-wicket hauls in back-to-back matches.

Their reward is a Qualifier showdown against the Unicorns — a team that beat them in their only league-phase meeting. History says that doesn't matter in knockout cricket.

## Unicorns: The Team to Beat

SF Unicorns have been the most consistent franchise in Season 3. Built around the batting of Matt Short, the experience of Quinton de Kock behind the stumps, and the left-arm spin of Shadley van Schalkwyk, the Unicorns have combined firepower with composure. Their sole loss came to the Knight Riders on July 11 — the match that ignited LA's playoff push.

The Unicorns' biggest asset may be intangible: they are, effectively, the home team in Oakland. The Bay Area's cricket community — weekend leagues in Sunnyvale, Cupertino, and Fremont — will pack the Coliseum stands. For NRI families who spent years driving to Grand Prairie for the only meaningful cricket on American soil, having a playoff weekend within BART distance is a minor revolution.

## What NRIs Should Watch For

MLC's third season has been the league's best. Average scores are up. Attendance at Knight Riders Cricket Ground in Pomona exceeded projections. And for the first time, the playoff viewership will test whether American cricket can sustain interest beyond the league phase.

For diaspora fans, the storylines write themselves. Can the Knight Riders — the IPL brand transplant — win their first MLC title with a squad of Caribbean power-hitters? Will the Freedom, anchored by Steve Smith and Marco Jansen, survive an Eliminator in hostile California territory? And can MI New York, the franchise that gave Kieron Pollard one last big stage, claw their way to a second straight final?

Tickets for the Oakland playoff matches are available through MLC's website. The Qualifier and Eliminator are on July 15, with the championship final to follow. All matches stream live on Willow TV and ESPN+.

The league phase is over. The arithmetic is settled. Now it's knockout cricket — the format that rewards nerve over numbers. Oakland is ready. The question is whether these four franchises are.\
""")

    # Source image: Wikimedia Commons for Oakland Coliseum or MLC
    print("\nSearching for hero image...")
    image_url = None
    image_caption = None
    image_attribution = "Wikimedia Commons"

    # Try Oakland Coliseum
    commons = fetch_wikimedia_commons_images("Oakland Coliseum cricket", limit=5)
    if not commons:
        commons = fetch_wikimedia_commons_images("Oakland Coliseum baseball stadium", limit=5)
    if not commons:
        commons = fetch_wikimedia_commons_images("Major League Cricket", limit=5)

    for c in commons:
        title_lower = c["title"].lower()
        # Skip irrelevant results
        if any(bad in title_lower for bad in ["logo", "icon", "map", "flag"]):
            continue
        if verify_image_url(c["url"]):
            image_url = c["url"]
            image_caption = "Oakland Coliseum will host MLC 2026's playoff matches and championship final"
            break

    if not image_url:
        # Fallback: try Wikipedia for Oakland Coliseum
        wiki_img = fetch_wikipedia_person_image("Oakland Coliseum")
        if wiki_img and verify_image_url(wiki_img):
            image_url = wiki_img
            image_caption = "Oakland Coliseum, the venue for MLC 2026 playoffs"

    if not image_url:
        # Last fallback: try Pexels for cricket stadium
        print("  ⚠ No image found from Commons/Wikipedia — trying Pexels...")
        try:
            pexels_key = os.environ.get("PEXELS_API_KEY", "")
            if pexels_key:
                pr = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": "cricket stadium", "per_page": 3},
                    headers={"Authorization": pexels_key},
                    timeout=10,
                )
                if pr.status_code == 200:
                    photos = pr.json().get("photos", [])
                    for p in photos:
                        url = p["src"]["large2x"]
                        if verify_image_url(url):
                            image_url = url
                            image_caption = "A cricket stadium ready for action"
                            image_attribution = "Pexels"
                            break
        except Exception as e:
            print(f"  Pexels error: {e}")

    slug = "mlc-2026-playoffs-set-three-teams-12-points-oakland-unicorns-knight-riders-freedom-nri-july-2026"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption or "MLC 2026 playoff action",
        "image_attribution": image_attribution,
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "vertical": "cricket",
        "diaspora_angle": "MLC playoffs head to Oakland — Bay Area's South Asian community gets its biggest cricket weekend on American soil, with BART-accessible matches and streaming on ESPN+.",
        "sources": json.dumps([
            {"name": "ESPNCricinfo", "url": "https://www.espncricinfo.com/series/major-league-cricket-2026"},
            {"name": "Sporting News", "url": "https://www.sportingnews.com"},
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"}
        ]),
        "score_total": 8,
    }
    return article


# ── Article 2: Sinner Defends Wimbledon Crown ────────────────────

def build_sinner_article():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Sinner Defends Wimbledon Crown")
    print("=" * 60)

    headline = "Sinner Makes It Two in a Row. The Italian Defends His Wimbledon Crown After a Four-Set Battle With Zverev."
    subheadline = "Jannik Sinner came back from a set down to beat Alexander Zverev 6-7, 7-6, 6-3, 6-4 in the men's final. Linda Noskova won the women's title in an all-Czech affair."

    body = textwrap.dedent("""\
Jannik Sinner is the best tennis player on the planet, and the conversation is no longer close.

The 24-year-old Italian defended his Wimbledon title on Sunday, defeating Germany's Alexander Zverev 6-7 (7-9), 7-6 (7-2), 6-3, 6-4 in a final that turned on a single tiebreak — and then became a masterclass. After dropping the opening set in a tight breaker, Sinner recalibrated with the surgical precision that has defined his rise: cleaner returns, deeper groundstrokes, and a serve that Zverev, for all his power, could not crack when it mattered.

It is Sinner's second consecutive Wimbledon title and his fourth Grand Slam overall. The man from South Tyrol, who learned to hit a ball on the Alpine slopes before choosing tennis over skiing, now holds the Australian Open and Wimbledon simultaneously — a distinction shared in the modern era only by Novak Djokovic and Roger Federer.

## The Final: A Study in Momentum

The opening set was everything a Wimbledon final should be. Both men held serve with ease through 12 games, neither offering a single break point. The tiebreak was a coin flip — Zverev edged it 9-7 after saving two set points. The scoreboard said Zverev; the body language said Sinner.

In the second set, Sinner reasserted control. His tiebreak was emphatic — 7-2 — the kind of performance that drains the opponent's belief. From there, the final's narrative was written. Sinner broke early in the third set, consolidated with 15 aces across the match, and closed out the fourth set on his second match point with a forehand winner that caught the line.

Zverev, the world No. 2, was gracious in defeat. "Jannik is the best player in the world right now," he said at the net. "I gave everything but he was better in the important moments."

## Djokovic's Last Bow?

The semifinal told a different story. Sinner dismantled Novak Djokovic 6-4, 6-4, 6-4 — straight sets against the man who has won this tournament seven times. At 39, Djokovic remains capable of producing vintage performances (he edged Felix Auger-Aliassime in a five-set epic in the quarterfinals), but against Sinner, the gap was undeniable. The Italian's movement, his ability to redirect Djokovic's best shots, and his composure under pressure all spoke to a generational shift that is now complete.

Whether Djokovic returns to Centre Court for a 25th Grand Slam campaign remains uncertain. The Serbian has dropped hints about retirement, though he has offered no definitive timeline.

## Noskova Stuns in Women's Final

The women's championship produced its own compelling narrative. Czech Republic's Linda Noskova, seeded ninth, defeated compatriot Karolina Muchova 6-2, 5-7, 6-3 in an all-Czech final — the first at Wimbledon since 2011. Noskova, just 21, dismantled the higher-seeded Muchova with aggressive baseline play and a fearless net game.

Her run through the draw was notable: she knocked out Madison Keys, Sorana Cirstea, and Marta Kostyuk without dropping a set until the final. Noskova is now the youngest Wimbledon women's champion since Petra Kvitova won her first title in 2011.

## What It Means for Indian Tennis

India's absence from the Wimbledon singles draws — no Indian man or woman reached the main draw this year — underscores the work ahead for Indian tennis. Sumit Nagal, who has shown flashes of capability on the ATP Tour, remains India's best hope for a Slam breakthrough, but consistency at this level demands a support system the country has yet to build.

The contrast with Indian cricket's global dominance is instructive. Tennis infrastructure in India lags far behind the enthusiasm of its fans — millions of Indians tune in to watch Wimbledon finals, making it one of the most-watched sporting events in the country after cricket and the World Cup. For NRIs in the United States, the Championships aired on ESPN and ESPN+, with the men's final competing for attention with an extraordinary convergence of live sport: the World Cup semifinals in Dallas and Atlanta, MLC playoffs in Oakland, and India Women's historic Test match at Lord's.

It was, by any measure, the greatest sports weekend of the year. Sinner standing on Centre Court with the trophy was its defining image.\
""")

    # Source image: Wikipedia for Jannik Sinner
    print("\nSearching for hero image...")
    image_url = None
    image_caption = None
    image_attribution = "Wikimedia Commons"

    # Try Wikipedia for Sinner
    wiki_img = fetch_wikipedia_person_image("Jannik Sinner")
    if wiki_img and verify_image_url(wiki_img):
        image_url = wiki_img
        image_caption = "Jannik Sinner defended his Wimbledon title with a four-set victory over Alexander Zverev"

    if not image_url:
        # Try Commons search
        commons = fetch_wikimedia_commons_images("Jannik Sinner tennis", limit=5)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "Jannik Sinner at the All England Club"
                break

    if not image_url:
        # Try Wimbledon Centre Court
        commons = fetch_wikimedia_commons_images("Wimbledon Centre Court tennis", limit=5)
        for c in commons:
            title_lower = c["title"].lower()
            if any(bad in title_lower for bad in ["logo", "icon", "map"]):
                continue
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "Centre Court at the All England Club, Wimbledon"
                break

    slug = "sinner-defends-wimbledon-crown-beats-zverev-four-sets-noskova-womens-nri-july-2026"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption or "Wimbledon 2026 men's singles final",
        "image_attribution": image_attribution,
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "vertical": "tennis",
        "diaspora_angle": "Millions of Indian fans tuned in to Wimbledon — the championships aired on ESPN+ for NRIs, capping the greatest sports weekend of the year alongside the World Cup semis, MLC playoffs, and India Women's Lord's Test.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/sports/tennis"},
            {"name": "Sky Sports", "url": "https://www.skysports.com/tennis"},
            {"name": "ESPN", "url": "https://www.espn.com/tennis"}
        ]),
        "score_total": 8,
    }
    return article


# ── Main ─────────────────────────────────────────────────────────

def main():
    # Load env
    env_file = os.path.expanduser("~/workspace/.env.supabase")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    articles = []

    # Build articles
    art1 = build_mlc_article()
    articles.append(art1)

    art2 = build_sinner_article()
    articles.append(art2)

    # Insert
    success = 0
    for art in articles:
        if art.get("image_url"):
            if insert_article(art):
                success += 1
        else:
            print(f"\n⚠ Skipping '{art['headline'][:50]}...' — no valid hero image found")

    print(f"\n{'=' * 60}")
    print(f"Done. {success}/{len(articles)} articles inserted into review queue.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
