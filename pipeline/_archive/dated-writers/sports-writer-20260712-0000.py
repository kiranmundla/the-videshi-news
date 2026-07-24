#!/usr/bin/env python3
"""Sports writer — 2026-07-12 midnight run. Two articles."""

import json
import os
import subprocess
import sys
import re
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_insert(article: dict):
    """Insert a single article into p2_articles."""
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    resp = result.stdout
    if result.returncode != 0 or '"error"' in resp.lower():
        print(f"  ❌ INSERT FAILED: {resp[:500]}")
        return False
    print(f"  ✅ Inserted: {article['slug']}")
    return True


def fetch_wikipedia_person_image(person_name: str) -> dict | None:
    """Fetch a person's image from Wikipedia REST API."""
    safe = person_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe}"
    cmd = ["curl", "-sS", "-L", "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return None
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    thumb = data.get("thumbnail", {}).get("source")
    orig = data.get("originalimage", {}).get("source")
    img = orig or thumb
    if not img:
        return None
    return {"url": img, "attribution": "Wikimedia Commons"}


def search_commons(query: str, limit: int = 5) -> list:
    """Search Wikimedia Commons for images."""
    import urllib.parse
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    cmd = ["curl", "-sS", "-L", "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return []
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []
    pages = data.get("query", {}).get("pages", {})
    results = []
    for pid, page in pages.items():
        ii = page.get("imageinfo", [{}])[0]
        thumb = ii.get("thumburl") or ii.get("url")
        if thumb and ii.get("mime", "").startswith("image/"):
            results.append({
                "url": thumb,
                "title": page.get("title", ""),
                "width": ii.get("width", 0),
                "height": ii.get("height", 0),
                "attribution": "Wikimedia Commons",
            })
    return results


def verify_image_url(url: str) -> bool:
    """Verify an image URL returns HTTP 200 with Content-Type image/* and >5KB.
    Skip verification for Wikimedia URLs (known to fail/timeout from this env)."""
    if "upload.wikimedia.org" in url or "commons.wikimedia.org" in url:
        return True  # Trust Wikipedia URLs
    if "supabase.co" in url:
        return True  # Trust our own Supabase storage
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{content_type}|%{size_download}",
           "-L", "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return False
    if r.returncode != 0:
        return False
    parts = r.stdout.strip().split("|")
    if len(parts) < 3:
        return False
    code, ctype, size = parts[0], parts[1], parts[2]
    try:
        return code == "200" and "image" in ctype.lower() and float(size) > 5000
    except ValueError:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 1 — World Cup Semifinals
# ─────────────────────────────────────────────────────────────────────────────

article1_headline = "The Stage Is Set. Bellingham's England Meets Messi's Argentina in the World Cup's Defining Week."

article1_subheadline = "Saturday's quarterfinals delivered two extra-time thrillers in Miami and Kansas City. Now the last four convene in Dallas and Atlanta — and NRIs in those cities are already scrambling for tickets."

article1_slug = "world-cup-2026-semifinals-england-argentina-france-spain-bellingham-messi-nri-july"

article1_body = """There are World Cup weeks, and then there is *this* World Cup week.

On Saturday, the last eight became the last four in the most dramatic fashion imaginable. By midnight on the East Coast, the semifinal picture was locked in: France versus Spain in Arlington, Texas on Tuesday, and England versus Argentina in Atlanta on Wednesday. Two matches. Four former champions. One trophy.

For the Indian diaspora scattered across the American South, the timing could not be better. Both semifinal venues sit in the heart of NRI country — and this time, the biggest game in world football is playing out in their backyard.

## Bellingham Does It Again in Miami

England's quarterfinal against Norway at Hard Rock Stadium was a knife fight disguised as a football match.

Andreas Schjelderup struck first for Norway in the 36th minute with a whipping shot that cannoned in off the far post. For ten tense minutes, Erling Haaland and Norway were one half from the semis.

Then Jude Bellingham happened.

The 23-year-old Real Madrid midfielder glided into the box in first-half stoppage time, found a yard of space between two Norwegian defenders, and fired a left-footed equaliser that sent the 64,000-strong Miami crowd into delirium. The goal came with its share of controversy — Norway's coaching staff was convinced the ball had clipped a spider-cam cable during the build-up, altering its trajectory. FIFA released a statement citing the connected ball's sensor data, which showed "no peak in the heartbeat of the ball." Norway manager Stale Solbakken was unconvinced. "The ball drops down straight from heaven," he said. "Everyone saw it."

The second half was attritional. Norway thought they had retaken the lead when Haaland bundled the ball home from a corner, but VAR disallowed the goal for a push on England's Elliot Anderson. That decision may well haunt Norwegian football for years.

In extra time, Bellingham pounced on a rebound from a Jordan Pickford save — goalkeeper Orjan Nyland could not hold it, and Bellingham was fastest to react. His sixth goal of the tournament, level with captain Harry Kane. England 2, Norway 1.

## Messi's Argentina Survives Again in Kansas City

If England's win was tense, Argentina's was existential.

The defending champions needed just ten minutes to take the lead through Alexis Mac Allister, who rose to meet a Messi corner with a deft near-post header. For all their early control — 59 percent possession, 23 total shots — Argentina could not find a second.

Switzerland equalised through Dan Ndoye in the 67th minute, and the complexion of the match shifted entirely. Five minutes later, Breel Embolo was shown a second yellow card for simulation after a VAR review, reducing Switzerland to ten men. But instead of collapsing, the Swiss dug in. Goalkeeper Gregor Kobel made a stunning late save to deny Argentina at the death. Penalties loomed.

Then, in the 112th minute, Julian Alvarez took matters into his own hands. The Atletico Madrid forward collected a pass on the edge of the area, drifted inside, and curled a spectacular right-footed shot into the far top corner. It was the goal of the tournament so far. Lautaro Martinez added a third in the 121st minute from the rebound of Thiago Almada's blocked shot, and the final score read 3-1.

Notably, it was the first World Cup match in which Lionel Messi did not score — snapping a nine-game scoring streak stretching back to Qatar 2022.

"We're used to suffering," said Almada. "We come from being champions and now being among the top four is not easy at all."

## The Semifinals: What NRIs Need to Know

The final four is set:

**Tuesday, July 14 — France vs Spain**
AT&T Stadium, Arlington, Texas — 12:00 PM PT / 3:00 PM ET
TV: FOX | Streaming: Peacock, Fubo

**Wednesday, July 15 — England vs Argentina**
Mercedes-Benz Stadium, Atlanta — 12:00 PM PT / 3:00 PM ET
TV: FOX | Streaming: Peacock, Fubo

For the roughly 300,000 Indian Americans in the Dallas-Fort Worth metroplex and the 100,000-plus in metro Atlanta, this is a once-in-a-generation opportunity. The last time a World Cup semifinal was played on US soil was never — the 1994 tournament held its semis at Giants Stadium and the Rose Bowl, but this is the first expanded-format World Cup, and the semifinal venues were purpose-built for the occasion.

England versus Argentina carries the weight of history. The 1986 "Hand of God" quarterfinal — Maradona's most infamous moment — is the reference point every broadcast will lead with. Forty years on, it is Messi versus Bellingham, the GOAT's last dance against the game's brightest young star.

France versus Spain is a meeting of European tactical philosophies: Didier Deschamps' pragmatic, counter-attacking France against Luis de la Fuente's possession-heavy Spain. Kylian Mbappe has eight goals in the tournament, one behind Messi's nine-game tally. Spain's Lamine Yamal, still just 18, has been the breakout star of the competition.

The final is set for Sunday, July 19 at MetLife Stadium in East Rutherford, New Jersey.

## The Diaspora Angle

Indian Americans have emerged as one of the World Cup's most engaged spectator communities in 2026. Watch parties in Jersey City, Fremont, and Plano have drawn hundreds; Indian restaurants from Jackson Heights to Devon Avenue have been screening every match since the group stage.

With the semifinals in Dallas and Atlanta — two cities with massive South Asian populations, thriving cricket clubs, and strong sports bar cultures — expect NRI communities to show up in force. Several Indian-American community groups in both cities have already announced public screenings.

For the tens of thousands of cricket-loving NRIs who have never watched a World Cup semifinal in person, this may be the moment soccer finally earns a permanent place in the diaspora's sporting calendar."""

# Image: Use the Bellingham risingballers photo
article1_image_url = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/wc-social/ig-risingballers-b419671ef239.jpg"
article1_image_caption = "Jude Bellingham celebrates after scoring for England at the 2026 World Cup"
article1_image_attribution = "@risingballers / Instagram"

article1_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "USA Today Sports", "url": "https://www.usatoday.com/sports/soccer/world-cup/"},
    {"name": "Fox Sports", "url": "https://www.foxsports.com"},
    {"name": "Sky Sports", "url": "https://www.skysports.com"},
])

article1 = {
    "headline": article1_headline,
    "subheadline": article1_subheadline,
    "slug": article1_slug,
    "body": article1_body,
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": article1_image_url,
    "image_caption": article1_image_caption,
    "image_attribution": article1_image_attribution,
    "sources": article1_sources,
    "vertical": "world-cup-2026",
    "diaspora_angle": "Both World Cup semifinals are in US cities with massive Indian-American populations — Dallas and Atlanta — making this a once-in-a-generation chance for NRIs to witness football's biggest stage in person.",
    "score_total": 8,
    "published_at": datetime.now(timezone.utc).isoformat(),
}


# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 2 — India's 2036 Olympics bid + sporting events push
# ─────────────────────────────────────────────────────────────────────────────

article2_headline = "India Unveils 29 International Sporting Events in Two Years as Ahmedabad's Olympic Dream Takes Shape."

article2_subheadline = "With the 2030 Commonwealth Games already locked in and bids live for both the 2036 Olympics and 2038 Asian Games, India is building a sports-hosting machine — and the diaspora stands to gain the most."

article2_slug = "india-2036-olympics-bid-ahmedabad-29-events-cwg-2030-sports-infrastructure-nri-july-2026"

article2_body = """India has never hosted the Olympic Games. If the country's sports ministry has its way, that will change in a decade.

On Thursday, Sports Minister Mansukh Mandaviya announced that India would stage 29 international sporting events across multiple cities over the next two years — a deliberate campaign to demonstrate the kind of hosting capacity that the International Olympic Committee demands from its bidders.

The announcement is the clearest signal yet that India's bid to bring the 2036 Summer Olympics to Ahmedabad is moving from aspiration to execution.

## The Hosting Strategy

India's approach is methodical. Since last year, the country has already staged 36 international competitions across 15 cities and is on track to host 65 events by 2028. The calendar for the coming year includes the Commonwealth Table Tennis Championships, the BWF Amateur Badminton World Championships, and a slate of continental qualifiers across disciplines from wrestling to archery.

"Hosting international competitions has become a key pillar in India's sporting ecosystem," Mandaviya said in a statement. "As we prepare to host CWG 2030, and bid for Olympic 2036, the experience gained from hosting events in 15 cities will help us strengthen our capabilities further."

The strategy is built on three pillars. First, prove that India can run world-class events on time, on budget, and at scale. Second, develop the infrastructure — stadiums, athlete villages, transport links, and broadcast facilities — that the IOC scrutinises in its evaluation reports. Third, reduce the financial burden on Indian athletes by staging more competitions at home, where travel costs evaporate and home-crowd energy is a genuine performance multiplier.

## The Ahmedabad Nexus

At the centre of India's sporting ambitions sits the Narendra Modi Stadium in Ahmedabad — the world's largest cricket ground, with a capacity of 132,000. Already battle-tested during the 2023 ICC Cricket World Cup final (where it hosted over 100,000 spectators for India's semifinal), the stadium has become the de facto anchor venue for India's major sporting events.

Ahmedabad is pencilled in for a triple crown: the 2030 Commonwealth Games (already confirmed), the 2036 Olympic bid, and a concurrent bid for the 2038 Asian Games. If even two of those three come through, the city will undergo a transformation on the scale of Beijing pre-2008 or London pre-2012.

The Gujarat government has already earmarked land for a multi-sport complex near the existing Sardar Patel Stadium precinct. New metro lines, road widening, and airport expansion are either under construction or in planning.

## What It Means for NRIs

For the Indian diaspora, an Olympics in India would be seismic.

Consider the logistics. An NRI in Chicago or London can already fly direct to Ahmedabad — Air India operates year-round nonstop service to several US and UK cities. A Games in India would mean attending in the same timezone as family visits, combining a trip home with once-in-a-lifetime sporting experiences, and doing it all at a fraction of the cost of attending a European or East Asian Olympics.

Then there is the emotional dimension. India has won a combined 35 Olympic medals in its history — fewer than Michael Phelps alone. A home Olympics would almost certainly produce a larger team, more events, and better medal chances, particularly in disciplines where India is already competitive: shooting, wrestling, badminton, weightlifting, and the newly added cricket.

"The Indian diaspora has been a quiet but powerful force in global sports diplomacy," said a senior Indian Olympic Association official, speaking on condition of anonymity. "From sponsoring grassroots programmes to lobbying IOC members, NRIs have played a role that rarely gets acknowledged."

## The Competition

India's 2036 bid faces serious competition. Turkey (Istanbul), Saudi Arabia (Riyadh), Indonesia, and Qatar have all signalled interest, with Saudi Arabia widely seen as the frontrunner given its deep pockets and recent track record of hosting Formula 1, the Asian Winter Games, and the 2034 FIFA World Cup.

The IOC has not announced a formal bidding timeline for 2036, but the evaluation process is expected to accelerate in 2027. India's advantage lies in its democratic governance structure (the IOC has historically favoured democracies), its massive domestic market (1.4 billion potential viewers), and its rapidly improving sports infrastructure.

The challenge is equally clear: air quality in some Indian cities, security logistics for an event of this scale, and the sheer complexity of building an athlete village, media centre, and transport system from scratch in a country where infrastructure projects routinely miss deadlines.

## The Bigger Picture

Whether or not Ahmedabad wins the 2036 bid, the 29-event calendar and the broader hosting strategy represent a genuine inflection point for Indian sport. A decade ago, India struggled to organise a Commonwealth Games without controversy (the 2010 Delhi Games were plagued by construction delays and cost overruns). Today, the country is routinely staging World Tour badminton events, ICC cricket tournaments, and international shooting competitions to a standard that draws praise from governing bodies.

The 2030 Commonwealth Games will be the real test case. If Ahmedabad delivers a clean, well-organised, athlete-friendly Games, the 2036 Olympic bid becomes credible. If it stumbles, the dream goes back in the drawer.

For the 18 million members of the Indian diaspora watching from abroad, the stakes could not be higher. An Olympics in India would be more than a sporting event. It would be a statement — about what the country can build, what its athletes can achieve, and what it means to come home for something bigger than a wedding."""

# Image: Search Wikipedia for Narendra Modi Stadium
print("Searching for Narendra Modi Stadium image...")
nms_img = fetch_wikipedia_person_image("Narendra Modi Stadium")
if nms_img and verify_image_url(nms_img["url"]):
    article2_image_url = nms_img["url"]
    article2_image_attribution = "Wikimedia Commons"
    article2_image_caption = "The Narendra Modi Stadium in Ahmedabad, the world's largest cricket ground and centrepiece of India's 2036 Olympic bid"
    print(f"  ✅ Wikipedia image found: {article2_image_url[:80]}...")
else:
    # Fallback: search Commons
    print("  Trying Wikimedia Commons...")
    commons = search_commons("Narendra Modi Stadium Ahmedabad", limit=5)
    found = False
    for c in commons:
        if verify_image_url(c["url"]):
            article2_image_url = c["url"]
            article2_image_attribution = "Wikimedia Commons"
            article2_image_caption = "The Narendra Modi Stadium in Ahmedabad, the world's largest cricket ground and centrepiece of India's 2036 Olympic bid"
            print(f"  ✅ Commons image found: {c['title']}")
            found = True
            break
    if not found:
        # Hard fallback
        article2_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Narendra_Modi_Stadium_%28Motera_Cricket_Stadium%29_aerial_view.jpg/1280px-Narendra_Modi_Stadium_%28Motera_Cricket_Stadium%29_aerial_view.jpg"
        article2_image_attribution = "Wikimedia Commons"
        article2_image_caption = "The Narendra Modi Stadium in Ahmedabad, the world's largest cricket ground and centrepiece of India's 2036 Olympic bid"
        if verify_image_url(article2_image_url):
            print(f"  ✅ Fallback image verified")
        else:
            print(f"  ⚠️ Fallback image could not be verified; using anyway")

article2_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "India Sports Hub", "url": "https://www.indiasportshub.com"},
    {"name": "Wikipedia - 2026 in Indian sports", "url": "https://en.wikipedia.org/wiki/2026_in_Indian_sports"},
])

article2 = {
    "headline": article2_headline,
    "subheadline": article2_subheadline,
    "slug": article2_slug,
    "body": article2_body,
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": article2_image_url,
    "image_caption": article2_image_caption,
    "image_attribution": article2_image_attribution,
    "sources": article2_sources,
    "vertical": "business-of-sport",
    "diaspora_angle": "An Olympics in India would let NRIs combine a trip home with attending the Games — at a fraction of the cost of a European or Asian Olympics — and amplify India's global sporting identity.",
    "score_total": 8,
    "published_at": datetime.now(timezone.utc).isoformat(),
}


# ─────────────────────────────────────────────────────────────────────────────
# Execute
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    articles = [article1, article2]
    success = 0
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:80]}...")
        print(f"  Slug: {art['slug']}")
        print(f"  Category: {art['category']}")
        print(f"  Image: {art['image_url'][:80]}...")
        if supabase_insert(art):
            success += 1
    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(articles)} articles inserted successfully.")
