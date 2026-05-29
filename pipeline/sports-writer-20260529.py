#!/usr/bin/env python3
"""
The Videshi — Sports Writer (2026-05-29)
Publishes 3 sports articles with proper images.
"""

import json, os, sys, time, uuid, re, subprocess
import requests, urllib.parse
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ──────────────────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ POST {table} failed: {r.status_code} {r.text[:300]}")
        return None
    return r.json()

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ PATCH {table} failed: {r.status_code} {r.text[:300]}")
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
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: {r.status_code}")
            return image_url  # fall back to original URL if it's permanent
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping upload")
            return image_url
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {ur.status_code} {ur.text[:200]}")
            # If source is permanent (Wikipedia/Pexels), use it directly
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None

def validate_image(url):
    """Verify image URL returns valid image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if "image" in ct:
            return True
    except:
        pass
    return False

def publish_article(article):
    """Insert article into p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now,
        "sources": article["sources"],  # native JSON, NOT stringified
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "urgency": "medium",
        "score_total": 55,
        "is_featured": False,
        "is_editorial": False,
        "tags": [],
    }
    
    result = sb_post("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id[:8]})")
        return art_id
    return None


# ── Articles ─────────────────────────────────────────────────────────────

articles = []

# ── ARTICLE 1: FIFA World Cup Broadcast — Zee Deal ──────────────────────
print("\n═══ Article 1: FIFA World Cup India Broadcast Update ═══")

art1_body = """The largest democracy in the world nearly missed the world's largest football tournament. With the 2026 FIFA World Cup kicking off in Mexico on June 11 — thirteen days from now — India still does not have a confirmed broadcaster. But after weeks of fraught negotiations, a deal appears imminent.

## Zee Emerges as the Frontrunner

Zee Entertainment Enterprises Limited, once India's dominant sports broadcaster before ceding ground to Star and Sony in the 2010s, is in advanced talks with FIFA to secure the combined television and digital rights for both the 2026 and 2030 FIFA World Cups in the Indian subcontinent.

Multiple reports from industry publications including exchange4media and Storyboard18 indicate that Zee has gained significant momentum in negotiations over the past week. The broadcaster is preparing to launch four new sports channels under its **Unite8 Sports** brand, with the World Cup serving as the flagship property for the relaunch.

## How the Price Collapsed

FIFA originally sought approximately **$100 million** for the combined India rights package covering both tournaments. That number proved wildly unrealistic in a market where cricket commands premium rates and football remains a second-tier sport by broadcast revenue.

Reliance-Disney's JioHotstar — which broadcast the 2022 edition from Qatar — reportedly bid around **$20 million**, far below FIFA's expectations. Sony Pictures declined to submit an offer altogether. With limited buyer appetite, FIFA has reportedly revised its expectations down to roughly **$35 million** for both tournaments combined.

The collapse in price speaks to a fundamental asymmetry: India has 1.4 billion people and a rapidly growing football audience, but the broadcast economics still do not support Western-level rights fees. Cricket's IPL alone generates more domestic broadcast revenue than the entire FIFA World Cup cycle in India.

## What This Means for NRIs

For the estimated 4.5 million Indian Americans and millions more across the UK, Canada, Australia, and the Gulf states, the India broadcast situation has limited direct impact — you can watch on Fox Sports (US), ITV/BBC (UK), or TSN (Canada). But it matters enormously for three reasons:

**Family back home.** If you are planning to watch matches with relatives in India over video call, or if your parents and grandparents follow the tournament, the broadcast deal determines whether they can watch at all. Zee's deal would cover both linear television and its Zee5 OTT platform.

**Hindi and regional language commentary.** A Zee broadcast would likely offer commentary in Hindi, Tamil, Telugu, Bengali, and Marathi — languages that the US and UK English-only broadcasts will not provide. For diaspora fans who prefer watching in their mother tongue, this matters.

**The Indian team factor.** India is not in the 2026 World Cup. But the tournament is being held across the United States, Mexico, and Canada — in cities with massive Indian populations. MetLife Stadium in New Jersey, SoFi Stadium in Los Angeles, AT&T Stadium in Dallas, and NRG Stadium in Houston will all host matches. NRIs are buying tickets regardless of whether India is playing. The atmosphere in these stadiums will be shaped by the diaspora.

## The Unite8 Sports Gamble

Zee's play is a calculated bet. The company has been on the defensive since the collapse of its proposed merger with Sony in early 2024. Launching a new sports vertical with the World Cup as its opening act is a high-risk, high-reward move.

Industry analysts have raised legitimate questions about whether Zee can build the broadcast infrastructure — distribution deals, commentary teams, studio operations, and sales partnerships — in the roughly ten days between a deal closing and the first match. The opening game between Mexico and an opponent yet to be determined is on June 11 at Estadio Azteca in Mexico City.

But Zee has done this before. It built Ten Sports into a credible cricket broadcaster in the mid-2000s before selling it to Sony. The institutional knowledge exists.

## The Clock Is Ticking

As of this writing, no official announcement has been made. FIFA and Zee are still negotiating final terms. The All India Football Federation has urged FIFA to close the deal quickly, and former AIFF General Secretary Shaji Prabhakaran has publicly confirmed that negotiations are near finalization.

For the 200 million Indians who watched the 2022 World Cup final between Argentina and France — many of them staying up past midnight for the Doha kickoff — a deal cannot come soon enough. And for NRIs planning watch parties across Edison, Fremont, Brampton, and Southall, the question is no longer whether India gets the World Cup. It is whether Zee can pull off the broadcast equivalent of a last-minute equalizer.

*The 2026 FIFA World Cup runs from June 11 to July 19 across 16 cities in the United States, Mexico, and Canada. The final will be played at MetLife Stadium in East Rutherford, New Jersey.*"""

art1 = {
    "headline": "Zee Is Close to Ending India's World Cup Broadcast Crisis. The First Match Is in Thirteen Days.",
    "subheadline": "FIFA wanted $100 million. The market offered $20 million. Now Zee Entertainment is preparing to launch four new sports channels with the World Cup as its flagship.",
    "body": art1_body,
    "slug": "zee-entertainment-fifa-world-cup-2026-india-broadcast-rights-unite8-sports-deal-nri-guide-20260529",
    "sources": [
        {"name": "exchange4media", "url": "https://www.exchange4media.com"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com"},
        {"name": "Business Today Malaysia", "url": "https://www.businesstoday.com.my"},
        {"name": "RevSportz", "url": "https://revsportz.in"}
    ],
}

# Image: Use Pexels for World Cup / stadium — no specific person
img1 = fetch_pexels_image("FIFA World Cup football stadium crowd", "football match stadium fans")
if img1:
    final_url1 = upload_image_to_supabase(img1, f"zee-world-cup-broadcast-20260529.jpg")
    if final_url1 and validate_image(final_url1):
        art1["image_url"] = final_url1
        art1["image_caption"] = "The 2026 FIFA World Cup kicks off on June 11 across 16 cities in North America. India is racing to secure a broadcast deal."
        art1["image_attribution"] = "Pexels"
    else:
        art1["image_url"] = None
else:
    art1["image_url"] = None

articles.append(art1)


# ── ARTICLE 2: Djokovic vs Fonseca at Roland Garros ─────────────────────
print("\n═══ Article 2: Djokovic vs Fonseca at Roland Garros ═══")

art2_body = """The third round of the 2026 French Open begins Friday with a match that distills everything compelling about elite tennis into a single contest on Court Philippe Chatrier. Novak Djokovic, thirty-nine years old and hunting a record twenty-fifth Grand Slam title, faces Joao Fonseca, the nineteen-year-old Brazilian who has called the Serb his idol and the greatest of all time.

## The Last Champion Standing

The draw at Roland Garros has been shredded by chaos. Carlos Alcaraz, the defending champion, withdrew before the tournament with a wrist injury. Jannik Sinner, the world number one and top seed, suffered one of the most extraordinary collapses in Grand Slam history on Day 5 — leading Juan Manuel Cerundolo 6-3, 6-2, 5-1, one game from victory, before losing eighteen consecutive points and ultimately the match in five sets. The Italian later cited dizziness and exhaustion in ninety-degree Paris heat.

That leaves Djokovic as the only former French Open champion remaining in the men's draw. At thirty-nine, he is the oldest man in the third round. He arrived in Paris with a 9-3 season record and questions about whether his body — battered by decades of elite competition — could sustain a two-week Grand Slam run on clay.

His second-round match against France's Valentin Royer suggested yes, with caveats. Djokovic won 6-3, 6-2, 6-7(9), 6-3, but needed to save a set point in the third-set tiebreak after the home crowd roared Royer back into the match. It was a reminder that Djokovic's margin for error is narrower than it once was.

## Fonseca: The Future Arrives on Schedule

Joao Fonseca entered 2026 as one of the most hyped teenagers in tennis. The twenty-eighth seed has justified the hype, reaching the third round at Roland Garros with composed, athletic play that belies his age.

Born in Rio de Janeiro, Fonseca carries a game built for the modern tour — explosive forehand, improving serve, and the kind of court coverage that exhausts older opponents. He won the Next Gen ATP Finals in 2024 and has risen steadily through the rankings.

Before the match, Fonseca addressed the Djokovic matchup with the reverence of a student and the confidence of a competitor: "He's my idol. He's the GOAT. But I'm here to win, not to take a selfie."

## What the Sinner Collapse Means for the Draw

Sinner's exit has blown the top half of the draw wide open. The potential semifinal on Djokovic's side now features names like Felix Auger-Aliassime (the fourth seed), Flavio Cobolli, Learner Tien, and the Cerundolo who just toppled the world number one.

For Djokovic, it is an opportunity that may not come again. The two players most capable of beating him on clay — Alcaraz and Sinner — are both gone. Alexander Zverev, the second seed and 2024 finalist, lurks in the other half.

The path to a fourth French Open title and a record-extending twenty-fifth Grand Slam is the clearest it has been in years. But Djokovic must first get past a teenager who has spent his entire life watching the Serb win these matches and believes he is ready to do the same.

## The NRI Tennis Connection

Tennis enjoys devoted following among the Indian diaspora, particularly in the US and UK. Djokovic's disciplined, vegetarian-leaning lifestyle and vocal advocacy for player rights have earned him a significant Indian fan base. His matches at the French Open air early morning in the US (the Fonseca match is scheduled for approximately 9:30 AM ET Friday) — a convenient time for NRI viewers tuning in before work.

The match will be broadcast on TNT, TruTV, and Tennis Channel in the US, with streaming available on Max and DIRECTV. In India, JioHotstar carries the French Open coverage.

## What to Watch For

Djokovic's serving numbers. He landed 73 percent of first serves in the Royer match but was broken twice. Against a returner as aggressive as Fonseca, he cannot afford service lapses.

Fonseca's forehand under pressure. The Brazilian generates enormous topspin but can become erratic when pinned behind the baseline. Djokovic will aim to extend rallies and force Fonseca into high-backhand positions — the same tactic that has neutralized young power hitters for two decades.

And the crowd. Philippe Chatrier has a habit of choosing underdogs, and a charismatic Brazilian teenager playing the greatest of all time is precisely the narrative the Parisian crowd will embrace.

*Djokovic vs Fonseca is scheduled as the featured night session match on Court Philippe Chatrier, Friday May 29. Coverage begins at 9:30 AM ET / 7:00 PM IST on TNT and JioHotstar.*"""

art2 = {
    "headline": "Djokovic at Thirty-Nine Is the Last Champion Standing at Roland Garros. Today He Faces a Nineteen-Year-Old Who Calls Him the GOAT.",
    "subheadline": "With Sinner and Alcaraz both gone, Novak Djokovic has the clearest path to a record 25th Grand Slam. But Joao Fonseca is not here for a history lesson.",
    "body": art2_body,
    "slug": "djokovic-fonseca-french-open-2026-round-3-sinner-collapse-roland-garros-25th-grand-slam-20260529",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Tennis365", "url": "https://www.tennis365.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"}
    ],
}

# Image: Wikipedia photo of Djokovic
img2 = fetch_wikipedia_person_image("Novak Djokovic")
if img2:
    final_url2 = upload_image_to_supabase(img2, f"djokovic-french-open-2026-20260529.jpg")
    if final_url2 and validate_image(final_url2):
        art2["image_url"] = final_url2
        art2["image_caption"] = "Novak Djokovic is the last former French Open champion remaining in the 2026 draw after Sinner's stunning second-round exit."
        art2["image_attribution"] = "Wikimedia Commons"
    else:
        art2["image_url"] = img2 if "upload.wikimedia.org" in (img2 or "") else None
        art2["image_attribution"] = "Wikimedia Commons"
else:
    # Fallback to Pexels
    img2_px = fetch_pexels_image("Roland Garros tennis clay court", "French Open tennis")
    if img2_px:
        final_url2 = upload_image_to_supabase(img2_px, f"djokovic-french-open-2026-20260529.jpg")
        art2["image_url"] = final_url2
        art2["image_caption"] = "The French Open third round begins Friday at Roland Garros with Djokovic facing Fonseca on Philippe Chatrier."
        art2["image_attribution"] = "Pexels"
    else:
        art2["image_url"] = None

articles.append(art2)


# ── ARTICLE 3: Knicks in the NBA Finals ─────────────────────────────────
print("\n═══ Article 3: Knicks in NBA Finals — NRI NYC Angle ═══")

art3_body = """Karl-Anthony Towns scored nineteen points and grabbed fourteen rebounds. OG Anunoby added seventeen. The New York Knicks demolished the Cleveland Cavaliers 130-93 on Monday night to complete a four-game sweep of the Eastern Conference Finals and reach the NBA Finals for the first time since 1999.

Twenty-seven years. That is how long New York has waited.

## The Sweep

The Knicks did not merely beat the Cavaliers. They embarrassed them. After blowing a twenty-two-point fourth-quarter lead in Game 1 — then winning anyway in overtime — the Knicks won the next three games by an average of twenty-two points. Game 4 in Cleveland was over by halftime, the Cavaliers' home crowd filing out long before the final buzzer.

Jalen Brunson was named Eastern Conference Finals MVP after averaging twenty-three points and eight assists across the four games. His steady, cerebral play — more surgeon than showman — has been the defining characteristic of this Knicks run, which now includes an eleven-game playoff winning streak with an average margin of victory exceeding twenty points.

The Cavaliers' star acquisitions — Donovan Mitchell and James Harden — combined for just thirty-seven points in the clinching game. Harden, who arrived in a midseason trade from the Lakers, told reporters afterward that he remains committed to Cleveland. Mitchell echoed the sentiment. Neither sounded convinced.

## The Western Conference: Game 7 on Saturday

The Knicks now wait for their Finals opponent. On Thursday night, Victor Wembanyama scored twenty-eight points and grabbed ten rebounds as the San Antonio Spurs destroyed the Oklahoma City Thunder 118-91 in Game 6 to force a decisive Game 7 on Saturday night in Oklahoma City.

The series has been spectacular. It opened with a double-overtime Spurs victory in OKC, followed by a Thunder win, then alternating blowouts that have made the series feel like two entirely different competitions depending on which team's building the game is in.

Game 7 tips off Saturday at 8:30 PM ET at Paycom Center. The winner faces the Knicks in the NBA Finals beginning Wednesday, June 3.

## Why This Matters to the Indian Diaspora

The New York metropolitan area is home to the largest Indian-American community in the United States. Jackson Heights, Jersey City, Edison, Hicksville — these neighborhoods contain some of the densest concentrations of NRI families anywhere in the world. And they are about to collide with the biggest sports summer New York has seen in a generation.

The Knicks are in the Finals. The FIFA World Cup arrives in New York on June 11, with MetLife Stadium in East Rutherford hosting multiple group-stage matches and a semifinal. The overlap of these two events in a single month — in a city already overwhelmed by cultural and sporting activity — will be unlike anything the tri-state area's Indian community has experienced.

Already, Knicks playoff tickets have become the hottest commodity in the city. Lower-level seats for a potential Game 1 at Madison Square Garden are listed at over $1,500. For NRIs who have adopted basketball as their American sport — and there are more of them every year, particularly among second-generation Indian Americans — this is a milestone.

The NBA has actively courted the Indian market for over a decade, launching NBA India games and signing Bollywood celebrities for promotional events. But nothing drives engagement like a New York team in the Finals. The Knicks' global brand, combined with the city's diaspora density, makes this a singular moment for Indian basketball fans.

## Wembanyama: The Future Is Already Here

Whether the Knicks face the Thunder or the Spurs, the Finals will feature a generational talent. If San Antonio wins Game 7, Victor Wembanyama — the seven-foot-four French phenom in only his second NBA season — will play on the sport's biggest stage. His Game 6 performance was a statement: twenty-eight points, ten rebounds, and defensive presence that made the Thunder's stars look ordinary.

If Oklahoma City wins, the Knicks face Shai Gilgeous-Alexander, the Thunder's elegant, relentless guard who is widely considered the league's best player this season. SGA averaged thirty-one points per game during the regular season and has been even better in the playoffs.

Either matchup promises appointment television. The NBA Finals begin June 3 and will air on NBC and stream on Peacock.

## The Numbers

The Knicks' playoff run by the numbers:

- **15-2** overall playoff record (sweeps of the Hawks, Pistons, and Cavaliers, plus a 3-2 first-round series)
- **23.7** average margin of victory during the eleven-game winning streak
- **130** points scored in the clinching Game 4 — the most in a closeout game in franchise history
- **1999** the last time the Knicks reached the Finals, when they lost to the Spurs in five games as an eighth seed

*The NBA Finals begin Wednesday, June 3. Game 7 of the Western Conference Finals between the Thunder and Spurs tips off Saturday at 8:30 PM ET on NBC and Peacock.*"""

art3 = {
    "headline": "The Knicks Are in the NBA Finals for the First Time Since 1999. New York's Biggest Sports Summer in a Generation Has Begun.",
    "subheadline": "A four-game sweep of Cleveland. An eleven-game winning streak. And for the millions of NRIs in the tri-state area, a summer with the Finals and the World Cup in the same city.",
    "body": art3_body,
    "slug": "knicks-nba-finals-2026-sweep-cavaliers-brunson-nyc-nri-sports-summer-world-cup-20260529",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "Sporting News", "url": "https://www.sportingnews.com"}
    ],
}

# Image: Pexels for NBA / Madison Square Garden — no specific person article
img3 = fetch_pexels_image("NBA basketball game arena crowd", "Madison Square Garden basketball")
if img3:
    final_url3 = upload_image_to_supabase(img3, f"knicks-nba-finals-2026-20260529.jpg")
    if final_url3 and validate_image(final_url3):
        art3["image_url"] = final_url3
        art3["image_caption"] = "The New York Knicks swept the Cavaliers to reach the NBA Finals for the first time in 27 years."
        art3["image_attribution"] = "Pexels"
    else:
        art3["image_url"] = None
else:
    art3["image_url"] = None

articles.append(art3)

# ── Publish All ──────────────────────────────────────────────────────────
print("\n═══ Publishing Articles ═══")
published = 0
for art in articles:
    art_id = publish_article(art)
    if art_id:
        published += 1
    time.sleep(1)

print(f"\n✅ Done. Published {published}/{len(articles)} articles.")
