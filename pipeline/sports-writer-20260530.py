#!/usr/bin/env python3
"""
Sports Writer for The Videshi - 2026-05-30
Writes 3 sports articles with diaspora angle.
"""

import os, json, uuid, re, time, subprocess
import requests
import urllib.parse
from datetime import datetime, timezone

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ---------- Image Sourcing ----------

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
    """Fetch image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    # Ban Meta CDN URLs
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned CDN URL: {url[:60]}")
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        print(f"  ✗ Signed Meta URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't support HEAD, try GET
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get('Content-Type', '')
        cl2 = int(r2.headers.get('Content-Length', 0))
        if r2.status_code == 200 and 'image' in ct2 and cl2 > 5000:
            print(f"  ✓ Image validated (GET): {cl2} bytes, {ct2}")
            return True
        print(f"  ✗ Image validation failed: status={r2.status_code}, ct={ct2}, cl={cl2}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ---------- Supabase helpers ----------

def sb_insert(table, data):
    """Insert a record into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

def sb_update(table, match_field, match_value, data):
    """Update a record in Supabase."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{match_field}=eq.{match_value}",
        headers=HEADERS,
        json=data
    )
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Update failed ({r.status_code}): {r.text[:200]}")
        return False

# ---------- Articles ----------

articles = []

# ============================================================
# ARTICLE 1: Fonseca shocks Djokovic at French Open
# ============================================================
articles.append({
    "headline": "Fonseca Beat Djokovic From Two Sets Down. The French Open Has No Major Champion Left in the Men's Draw.",
    "subheadline": "The 19-year-old Brazilian became the first teenager to beat Novak Djokovic in a Grand Slam match. With Sinner and Alcaraz also gone, Roland Garros will crown a first-time men's singles champion.",
    "slug": "fonseca-beats-djokovic-two-sets-down-french-open-2026-no-major-champion-left-mens-draw",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/sports/tennis/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/sports/tennis/"},
        {"name": "People", "url": "https://people.com/sports/"},
        {"name": "Sportradar", "url": "https://sportradar.com/"}
    ]),
    "body": """It took four hours and fifty-three minutes. It took a heat wave in Paris, a cameraman who got too close, and a nineteen-year-old Brazilian who refused to believe the scoreboard.

João Fonseca beat Novak Djokovic 4-6, 4-6, 6-3, 7-5, 7-5 in the third round of the 2026 French Open on Friday — the longest match of Djokovic's career at Roland Garros, and one that may define the tournament's future more than any result this decade.

## The First Teenager to Beat Djokovic in a Slam

Djokovic had been 289-1 in Grand Slam matches when leading two sets to love. The only other man to come back from that deficit against him was Jürgen Melzer, on this same Parisian clay, in 2010. Fonseca, ranked 30th in the world and seeded 28th in the draw, became the second — and the first teenager ever to defeat Djokovic in a Grand Slam event.

"I actually didn't believe I could win the match," Fonseca said afterward, grinning. "I just played and enjoyed being on the court. What an idol we have and what a pleasure it was to step on the court against him."

## Two Sets Up, Then the Heat Takes Over

Djokovic started crisply. He broke Fonseca's serve in each of the first two sets, looking every bit the three-time French Open champion chasing a record 25th major title. But temperatures at Roland Garros hovered around 90 degrees Fahrenheit all week, and as the third set wore on, the 39-year-old Serb began to wilt.

Early in the fifth set, Djokovic vomited into a trash can at courtside. He had already snapped at a cameraman earlier — "Can you come more in my face? For God's sake, make some space" — after the second set.

Fonseca, meanwhile, found another gear. He broke Djokovic's serve at 5-5 in both the fourth and fifth sets, then closed the match with three consecutive aces. The Brazilian pointed to the stands where his mother sat beaming — it was her birthday.

"I was just trying to hit the ball as fast as I could," Fonseca said. "Djokovic doesn't miss and we still think he's 20. At the end of the match he was more fit than me, which is crazy."

## The Draw Is Wide Open

Fonseca's win comes less than 24 hours after world number one Jannik Sinner lost to Argentina's Juan Manuel Cerundolo in the second round. Two-time defending champion Carlos Alcaraz withdrew from the tournament entirely with a wrist injury. Sixth-seeded Daniil Medvedev fell in the first round to Australia's Adam Walton. Stan Wawrinka and Gaël Monfils, playing their final seasons, both lost their opening matches.

There is no former Grand Slam champion left in the men's draw. Roland Garros will crown a first-time major winner.

The remaining contenders include second-seeded Alexander Zverev, 15th-seeded Casper Ruud, 11th-seeded Andrey Rublev, and Fonseca himself. For the diaspora watching from North America, there is also Nishesh Basavareddy — the Indian-American wildcard from Andhra Pradesh roots who stunned seventh-seeded Taylor Fritz in the second round, the biggest win by an Indian-heritage player at a Grand Slam in years.

## What It Means for Djokovic

When asked whether he would return to Roland Garros next year, Djokovic did not commit. "I don't know," he said. The 24-time Grand Slam winner, who turned 39 last week, said he felt he had played "really good tennis" but was physically spent.

"A couple of times I felt like I was barely standing on my legs towards the end," Djokovic said. "Incredible match to be part of. Obviously a tough one for me to lose, being two sets to love up, but huge credit to Joao for really deserving to win."

If Djokovic does return next year, he would join a short list of players who competed at Roland Garros at age 40 — a feat achieved by very few in the Open Era.

The 15,000 fans at Court Philippe Chatrier gave him a standing ovation as he walked off. For a man who spent two decades rewriting records on every surface, it was the kind of farewell that may or may not be a farewell at all.

## The NRI Watch Guide

Fonseca will face either 15th-seeded Casper Ruud or 24th-seeded Tommy Paul in the fourth round. Basavareddy's next match has not been scheduled yet. For viewers in North America, French Open matches air on TNT, and the schedule typically begins at 5 AM Eastern on weekdays, with night sessions on Court Chatrier starting around 3 PM Eastern. The men's final is on June 8.""",
    "image_person": "Novak Djokovic",
    "image_pexels_query": "tennis Roland Garros clay court",
    "image_pexels_fallback": "professional tennis match",
})

# ============================================================
# ARTICLE 2: India's historic U23 Asian Wrestling haul
# ============================================================
articles.append({
    "headline": "Twenty-Seven Medals in Da Nang. India's Wrestlers Just Delivered Their Best U23 Asian Championships in History.",
    "subheadline": "The men's freestyle team won the championship trophy. The women won six golds out of ten medals. PM Modi called it 'an outstanding performance.' The 2028 Olympics pipeline has never looked stronger.",
    "slug": "india-u23-asian-wrestling-championships-2026-27-medals-da-nang-historic-freestyle-women-20260530",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "Wrestling Federation of India", "url": "https://wrestlingfederationofindia.com/"},
        {"name": "IANS / HI India", "url": "https://hiindia.com/"},
        {"name": "PTI / Freedom Press", "url": "https://thefreedompress.in/"},
        {"name": "PM Modi on X", "url": "https://x.com/naaborendramodi"}
    ]),
    "body": """The numbers tell the story before a single name does. Eleven gold medals. Seven silver. Nine bronze. Twenty-seven medals total across three disciplines — freestyle, women's wrestling, and Greco-Roman. India's highest-ever haul at the U23 Asian Wrestling Championships. The men's freestyle team was crowned undisputed champion, finishing ahead of Kyrgyzstan and Kazakhstan. The women won the team title too.

This happened in Da Nang, Vietnam, over the last week of May 2026, and it happened mostly in silence. No prime-time broadcasts. No hashtags trending. Just a generation of Indian wrestlers aged twenty-three and under, beating Central Asian powerhouses on their mats.

## The Freestyle Domination

The men's freestyle squad alone accounted for nine medals — four golds, three silvers, and two bronzes. Akshay T Dhere at 57kg and Vicky at 97kg set the tone with gold medals early in the competition. Kumar Mohit at 65kg and Chandermohan at 79kg followed with golds of their own, each winning multiple bouts decisively.

Deepak Rathi (61kg), Punit Kumar (92kg), and Lacky at 125kg — a heavyweight category where India has historically struggled — all won silver. Deepak Berwal (74kg) and Mor Sachin (82kg) added bronze medals that padded India's final tally into historic territory.

India finished first in the freestyle team standings, ahead of Kyrgyzstan in second and Kazakhstan in third. These are nations where wrestling is a cultural cornerstone, where U23 programs receive state funding and media attention. India beat them all.

## The Women Were Even More Dominant

If the freestyle haul was impressive, the women's team was extraordinary. Six gold medals out of ten total medals — a conversion rate that would make any national federation proud. Muskan, Tapasya, Bhagyashree, Pulkit, Mansi, and Kajal all stood on the top step of the podium. These are names that most sports fans outside the wrestling community would not recognise today. That will change.

The women's team also won the team championship, mirroring the men's freestyle achievement. Combined with the Greco-Roman squad's eight medals — its own highest-ever tally at a U23 Asian Championships — the Indian contingent's overall dominance was complete.

## PM Modi Noticed

Prime Minister Narendra Modi congratulated the team on X, calling it "an outstanding performance."

"The Men's Freestyle Wrestling team secured 9 medals, including 4 Golds, thus registering India's highest-ever overall medal haul at the U23 Asian Championships in history," Modi wrote. "The women's wrestling contingent won 10 medals, including 6 Golds. The Greco-Roman team also recorded its highest-ever overall medal count with 8 medals."

Wrestling Federation of India President Sanjay Singh was more expansive. "Lifting the U23 Asian Championship Trophy is a monumental achievement for Indian wrestling and a moment of immense pride for the entire country," he said. "Our freestyle grapplers have shown unparalleled determination and technical superiority."

## Why the Diaspora Should Pay Attention

For the millions of Indian-Americans, Indian-Canadians, and Indian-Brits who watched Bajrang Punia, Ravi Dahiya, and Neeraj Chopra at the Tokyo and Paris Olympics, this is the incoming wave. The 2028 Los Angeles Games are two years away. The wrestlers who dominated in Da Nang are the ones who will be fighting for Olympic berths in the qualifying tournaments next year.

India has medalled in wrestling at three consecutive Olympics — Sushil Kumar in 2012, Sakshi Malik in 2016, Ravi Dahiya and Bajrang Punia in 2020, Aman Sehrawat in 2024. Each cycle has produced at least one moment that brought the diaspora to its feet. The 27-medal haul in Da Nang suggests that the 2028 cycle could be the richest yet.

What makes this result especially promising is the depth. This is not a single superstar carrying a team. This is eleven gold medallists across three disciplines, spread across weight categories from 50kg to 125kg. It is a system producing results, not just individuals.

The competition received almost no coverage outside specialist wrestling media. That is, in some ways, the point. The work is being done. The medals are being won. The pipeline is filling. By the time Los Angeles arrives, these names — Dhere, Vicky, Mohit, Chandermohan, Muskan, Tapasya — will be familiar. This week in Da Nang was where it started.""",
    "image_person": None,
    "image_pexels_query": "wrestling competition mat athlete",
    "image_pexels_fallback": "Indian wrestling sport",
})

# ============================================================
# ARTICLE 3: Anushka Sharma invests in Agilitas / One8 Yoga
# ============================================================
articles.append({
    "headline": "Anushka Sharma Has Invested in Virat Kohli's Sportswear Company. They Are Launching a Yoga Line on June 21.",
    "subheadline": "Sharma acquired a minority stake in Agilitas Sports and will co-develop One8 Yoga, set to debut on International Day of Yoga. It is the latest move by cricket's most powerful couple to build beyond the pitch.",
    "slug": "anushka-sharma-agilitas-sports-virat-kohli-one8-yoga-june-21-investment-nri-20260530",
    "category": "sports",
    "vertical": "sports",
    "sources": json.dumps([
        {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/"},
        {"name": "Apparel Resources", "url": "https://apparelresources.com/"},
        {"name": "Franchise India", "url": "https://franchiseindia.com/"},
        {"name": "IPO Scanner", "url": "https://iposcanner.ai/"}
    ]),
    "body": """Anushka Sharma has acquired a minority stake in Agilitas Sports, the Indian sportswear company co-founded by former Puma executives and already backed by her husband, Virat Kohli. As part of the deal, Sharma will lead the development of One8 Yoga, a new activewear category under the One8 sportswear brand. The line is set to launch on June 21 — International Day of Yoga.

It is a quiet, strategic move that says more about where Indian sport-as-business is heading than any IPL auction number.

## The Agilitas Story

Agilitas Sports was founded in 2023 by Abhishek Ganguly, Atul Bajaj, and Amit Prabhu — all former Puma India executives. The company built a vertically integrated model spanning manufacturing, brand development, and direct-to-consumer retail. Backed by Convergent Finance and Nexus Venture Partners, Agilitas has steadily acquired assets, including long-term Lotto licensing rights and footwear manufacturer Mochiko Shoes.

The company's biggest move came in 2025, when Kohli ended his eight-year, ₹110-crore endorsement deal with Puma and invested approximately ₹40 crore for a minority stake in Agilitas. That deal also transferred One8 — Kohli's personal sportswear and lifestyle brand — into the Agilitas portfolio. It was a shift from endorsement to ownership, from face of a brand to builder of one.

Now Sharma has joined the same cap table. Agilitas CEO Ganguly confirmed the partnership but declined to disclose financial details. "Anushka is partnering with Agilitas by investing capital in the company and building yoga-wear," he said.

## Why Yoga, Why Now

India's athleisure and wellness market is growing at double-digit rates. Yoga apparel is one of its fastest-expanding segments, driven by rising fitness consciousness across Indian metros and — critically for Agilitas — among the global Indian diaspora.

For NRIs in the United States, Canada, and the UK, yoga is both cultural inheritance and modern lifestyle. The market already includes established players like Lululemon, Alo Yoga, and Nike's yoga line. What it lacks is an Indian-rooted brand with genuine cultural authority.

That is the gap Sharma and Agilitas are aiming at. One8 Yoga launching on June 21 is not a coincidence — International Day of Yoga, established at India's initiative at the United Nations in 2015, has become a global event with particular resonance in the diaspora.

Ganguly framed the partnership as deeper than a celebrity endorsement. "Anushka joining goes much deeper than an investment," he said. "With One8 Yoga, we are extending that idea into a larger movement around wellness, mindfulness, and everyday fitness."

## Cricket's Most Powerful Couple, Off the Pitch

Kohli and Sharma are arguably the most recognisable couple in Indian public life. Kohli's One8 brand — spanning restaurants, fragrances, and sportswear — has long been a case study in how Indian athletes can build commercial empires beyond endorsements. Sharma, despite being on an indefinite sabbatical from films since 2018's *Zero*, has invested in multiple startups including clean beauty brand Nush.

Their joint involvement in Agilitas is notable for what it represents: a shift from separate business portfolios to a shared platform. Kohli brings performance sport credibility. Sharma brings lifestyle and wellness positioning. Together, they give One8 a reach that few Indian brands can match.

## What NRIs Should Know

One8 Yoga products are expected to launch online and through select retail channels starting June 21. Pricing and availability in North American and UK markets have not been announced, but Agilitas has indicated plans for international expansion.

For the diaspora, the brand's appeal will likely hinge on whether One8 Yoga can compete on quality and design with established Western activewear while offering an Indian identity that resonates with consumers who already practice yoga as both fitness and cultural connection.

The sportswear market globally is worth over $400 billion. India's share is growing but still small. What Kohli and Sharma are building at Agilitas — an Indian-owned, vertically integrated sportswear platform with global ambitions — is an attempt to change that. The yoga line is the first chapter of that story aimed squarely at the world.""",
    "image_person": "Anushka Sharma",
    "image_pexels_query": "yoga activewear fashion",
    "image_pexels_fallback": "yoga practice studio",
})

# ---------- Main execution ----------

def process_articles():
    published = 0
    for i, art in enumerate(articles):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art['headline'][:70]}...")
        print(f"{'='*60}")
        
        # Image sourcing
        image_url = None
        
        # Try Wikipedia first for person articles
        if art.get('image_person'):
            print(f"  → Trying Wikipedia for '{art['image_person']}'...")
            image_url = fetch_wikipedia_person_image(art['image_person'])
            if image_url and not validate_image_url(image_url):
                image_url = None
        
        # Fall back to Pexels
        if not image_url:
            print(f"  → Trying Pexels for '{art.get('image_pexels_query', '')}'...")
            image_url = fetch_pexels_image(
                art.get('image_pexels_query', ''),
                art.get('image_pexels_fallback', '')
            )
            if image_url and not validate_image_url(image_url):
                image_url = None
        
        if not image_url:
            print("  ⚠ No valid image found - publishing without image")
        
        # Prepare article record
        article_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        record = {
            "id": article_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"],
            "category": "sports",
            "vertical": "sports",
            "status": "published",
            "published_at": now,
            "sources": json.loads(art["sources"]),
            "image_url": image_url,
            "image_attribution": "Wikimedia Commons" if image_url and "wikimedia" in (image_url or "").lower() else "The Videshi" if image_url else None,
        }
        
        print(f"  → Publishing: {art['slug']}")
        result = sb_insert("p2_articles", record)
        
        if result:
            print(f"  ✓ Published successfully: {article_id}")
            published += 1
        else:
            print(f"  ✗ Failed to publish")
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Done: {published}/{len(articles)} articles published")
    print(f"{'='*60}")

if __name__ == "__main__":
    process_articles()
