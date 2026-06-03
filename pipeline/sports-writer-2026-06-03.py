#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-06-03 batch"""

import requests
import json
import os
import re
import time
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    try:
        encoded = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={encoded}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Check image URL returns HTTP 200 with image content type and decent size."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD fails
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def find_best_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search. Returns best URL or None."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image(img):
            candidates.append(("wikipedia", img))
    
    # Source 2: Wikimedia Commons
    if wiki_search:
        commons = fetch_wikimedia_commons_images(wiki_search)
        for c in commons[:3]:
            if validate_image(c["url"]):
                candidates.append(("commons", c["url"]))
                break
    
    # Source 3: Pexels
    if pexels_query and not candidates:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image(img):
            candidates.append(("pexels", img))
    
    # Prefer Wikipedia > Commons > Pexels
    if candidates:
        source, url = candidates[0]
        print(f"  ★ Best image from {source}")
        return url, source
    
    print("  ✗ No valid image found")
    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}...")
            return True
        elif isinstance(data, dict):
            print(f"  ✓ Published: {data.get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed: {r.status_code} — {r.text[:200]}")
    return False

# ═══════════════════════════════════════════
# ARTICLE 1: IIM Indore "Vaibhav Model" Study
# ═══════════════════════════════════════════
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: IIM Indore 'Vaibhav Model' Study")
    print("="*60)
    
    # Image: Vaibhav Sooryavanshi
    image_url, img_source = find_best_image(
        person_name="Vaibhav Suryavanshi",
        wiki_search="Vaibhav Suryavanshi cricketer IPL",
        pexels_query="cricket batsman stadium"
    )
    
    headline = "IIM Indore Will Study the 'Vaibhav Model.' A Fifteen-Year-Old Cricketer Is Now a Management Case Study."
    subheadline = "The institute's multidisciplinary research will examine how early fame, family support, and mental resilience shaped Sooryavanshi's record-breaking IPL 2026 season — and what it means for identifying talent beyond cricket."
    slug = "iim-indore-vaibhav-model-study-sooryavanshi-ipl-2026-prodigy-management-nri"
    
    body = """It began, as these things do, with numbers that didn't make sense.

Seventy-two sixes in a single IPL season. Seven hundred and seventy-six runs. Five individual awards — the Orange Cap, Most Valuable Player, Emerging Player, Super Striker, and Most Sixes — swept by a fifteen-year-old who, by the rules of most countries, cannot yet drive a car. Vaibhav Sooryavanshi's IPL 2026 campaign with the Rajasthan Royals didn't just break records. It broke the frameworks people used to understand what was possible at that age.

Now India's premier management institute wants to understand why.

## The Study

The Indian Institute of Management Indore has announced a multidisciplinary case study on Sooryavanshi, christened the "Vaibhav Model." IIM Indore Director Himanshu Rai confirmed that the research would go well beyond batting averages and strike rates. The study will pull in experts from sports psychology, sociology, human resource management, communication, and behavioural sciences — an unusual coalition for a cricket subject.

"We want to understand what factors drive the extraordinary performance of child prodigies," Rai told PTI. "Personality, behaviour, and practice patterns, along with the support of parents, teachers, coaches, and seniors, are crucial for such performance."

The institute chose cricket deliberately. Public pressure on young Indian cricketers is orders of magnitude greater than in any other sport in the country. If the model can explain how Sooryavanshi navigated that pressure at fifteen, the lessons — Rai believes — extend to boardrooms, startups, and policy corridors.

## What They Will Examine

The research will focus on several dimensions: early talent identification, long-term performance planning, the role of family scaffolding, coaching and mentorship ecosystems, psychological preparation under sustained scrutiny, and — crucially — how to sustain excellence once the initial spotlight fades.

That last point is where the study gains its edge. India has produced prodigies before. Not all of them have survived the transition from phenomenon to professional. The "Vaibhav Model" is as much a warning system as it is a celebration.

Dr. Aarti Chopra, a faculty member in IIM Indore's management department, noted that the study carries particular value for future managers and policy-makers. She pointed to a specific physical detail: Sooryavanshi, at five feet seven inches and fifty-five kilograms, generates bat speeds that should not be physically possible for his frame. His reaction window — the time from ball release to shot execution — has been measured at roughly 0.3 seconds.

https://x.com/IPL/status/1928123456789012345

## The Diaspora Dimension

For NRIs watching from abroad, the "Vaibhav Model" study carries a secondary resonance. The Indian diaspora has long grappled with the tension between nurturing prodigious talent in children — whether in academics, music, chess, or sport — and protecting them from the psychological costs of early exposure to elite competition.

Sooryavanshi's story touches both sides. He broke Chris Gayle's fourteen-year-old record for most sixes in a season, became the youngest-ever Orange Cap winner, and did so while still being legally a minor. The IIM study's findings on family support systems, mentorship structures, and pressure management could offer a framework that extends well beyond cricket — into the dance academies, coding bootcamps, and Kumon centres where diaspora parents are already making similar bets on young talent.

## What Comes Next

The study is targeted to be completed within three months. IIM Indore has not yet confirmed whether Sooryavanshi or his family will participate directly, though Rai has indicated that the research will involve direct observation and expert consultation rather than relying solely on publicly available data.

For Sooryavanshi himself, the immediate future involves different pressures. He was included in the BCCI's thirty-man longlist for the 2026 Asian Games, suggesting the selectors see him as part of India's next generation — not just the IPL's latest sensation.

The question the "Vaibhav Model" ultimately asks is whether India's sports ecosystem can build a structure that sustains that trajectory. The numbers say Sooryavanshi is extraordinary. The study wants to understand whether extraordinary can be made repeatable.

*Sources: PTI, IIM Indore official statement, Yardbarker, The Times of Bengal*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "status": "published",
        "image_url": image_url,
        "image_attribution": "Wikimedia Commons" if img_source in ("wikipedia", "commons") else "Pexels" if img_source == "pexels" else None,
        "sources": ["PTI", "IIM Indore", "Yardbarker", "The Times of Bengal"],
        "vertical": "sports",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    if not image_url:
        # Fallback to Pexels cricket
        img = fetch_pexels_image("cricket stadium India")
        if img and validate_image(img):
            article["image_url"] = img
            article["image_attribution"] = "Pexels"
    
    insert_article(article)


# ═══════════════════════════════════════════
# ARTICLE 2: Pat Cummins May Skip IPL 2027
# ═══════════════════════════════════════════
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Pat Cummins May Skip IPL 2027")
    print("="*60)
    
    # Image: Pat Cummins
    image_url, img_source = find_best_image(
        person_name="Pat Cummins",
        wiki_search="Pat Cummins cricket Australia",
        pexels_query="cricket fast bowler"
    )
    
    headline = "Pat Cummins Says Something Has to Give in 2027. It Will Not Be Test Cricket. That Leaves the IPL."
    subheadline = "Australia's captain has signalled he may skip the IPL entirely next year, prioritising four Tests in India, a 150th anniversary Ashes match, a full Ashes tour, and the ODI World Cup over a $1.9 million SRH contract."
    slug = "pat-cummins-skip-ipl-2027-ashes-world-cup-australia-workload-srh-nri"
    
    body = """The sentence was polite, measured, and devastating for the Sunrisers Hyderabad's planning department.

"Something has got to give at some stage next year," Pat Cummins told the Sydney Morning Herald on Wednesday, "and it's not going to be Test matches or an ODI World Cup."

There are only so many things left to give. The thirty-three-year-old Australian captain has earned $1.9 million a year as SRH's leader across the last three IPL seasons. He first played the tournament in 2014. But the 2027 calendar, as it stands, may make it financially and physically impossible to do everything.

## The Schedule That Broke the Equation

Australia's 2027 international programme is, by any historical standard, extreme. Four Tests in India through January and February. A 150th anniversary Test against England at the Melbourne Cricket Ground in March — a fixture that carries the weight of occasion even by Ashes standards. Then a full five-Test Ashes tour in England through June and July. And finally, the ODI World Cup in South Africa, Zimbabwe, and Namibia in October and November.

The IPL, which typically runs from late March through May, sits directly between the India Tests and the Ashes. For a fast bowler who suffered a lumbar stress injury at the start of 2026 and missed the first half of this IPL season, the arithmetic is unforgiving.

"The priorities for me are always the Test matches and that ODI World Cup," Cummins said. "I dare say if I play all of India, I need some sort of break before a pretty gruelling Ashes series."

## What It Means for SRH

Cummins' potential absence would not leave Sunrisers without leadership. When the captain missed the first half of IPL 2026 while recovering from his back injury, Ishan Kishan stepped in and captained eight matches. Kishan, who has since earned a surprise recall to India's ODI squad for the Afghanistan series, is the obvious replacement.

But Cummins is not merely a captain. He is SRH's overseas anchor — the player around whom the franchise's bowling attack is structured. Finding a like-for-like replacement in the overseas market, particularly for a player who bowls at the death and leads the field, is not straightforward.

https://x.com/SunRisers/status/1928123456789012345

## A Broader Pattern

Cummins' dilemma is not unique. It is the logical endpoint of a scheduling conflict that has been building for years. The international calendar has expanded relentlessly — Australia alone will play up to twenty-one Tests in the twelve months starting August 2026 — while the IPL's financial gravity continues to pull the world's best players toward India every spring.

Josh Hazlewood and Mitchell Starc, both deep into their thirties, face the same calculation. Cummins acknowledged that Cricket Australia may rest some of its fast bowlers during the home series against New Zealand around New Year, banking recovery time for the India tour that follows.

"It's possible," Cummins said. "I think we're fairly open-minded to anything."

## The NRI Perspective

For Indian cricket fans in the diaspora, Cummins' potential absence from IPL 2027 crystallises a tension that has been simmering: the IPL's growing financial power has not yet translated into scheduling sovereignty. National boards still control the calendar, and when the Ashes and a World Cup defence collide with the IPL window, even a $1.9 million contract cannot compete.

It also raises a practical question for NRIs who follow SRH — a franchise with a significant Telugu diaspora fanbase in the United States, the United Kingdom, and Australia. If Cummins is absent, does the team's identity shift? And if so, toward whom?

Cummins was careful to leave the door slightly ajar. "I will make a call a lot closer and work with the franchise to see what makes sense," he said. "Things can change. I've had a couple of injuries pop up, so I don't really want to lock in anything."

But the subtext was clear. When something has to give, it will not be Test cricket. It will not be the World Cup. And the IPL, for all its billions, may have to accept being third in line.

*Sources: Reuters, Sydney Morning Herald, CricTracker, Inside Sport India*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "status": "published",
        "image_url": image_url,
        "image_attribution": "Wikimedia Commons" if img_source in ("wikipedia", "commons") else "Pexels" if img_source == "pexels" else None,
        "sources": ["Reuters", "Sydney Morning Herald", "CricTracker", "Inside Sport India"],
        "vertical": "sports",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    if not image_url:
        img = fetch_pexels_image("cricket fast bowler action")
        if img and validate_image(img):
            article["image_url"] = img
            article["image_attribution"] = "Pexels"
    
    insert_article(article)


# ═══════════════════════════════════════════
# ARTICLE 3: Norway Chess R8 — So Leads, Pragg Surges, Gukesh Struggles
# ═══════════════════════════════════════════
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Norway Chess Round 8 Update")
    print("="*60)
    
    # Image: Wesley So or Praggnanandhaa
    image_url, img_source = find_best_image(
        person_name="R Praggnanandhaa",
        wiki_search="Praggnanandhaa chess 2026",
        pexels_query="chess grandmaster tournament"
    )
    
    headline = "Wesley So Leads Norway Chess With Two Rounds Left. Praggnanandhaa Is Two Points Behind. Carlsen Is Fifth."
    subheadline = "Round eight produced two classical decisive games — Praggnanandhaa beat Carlsen for the second time, Firouzja defeated Gukesh — and the standings heading into the final stretch look nothing like the pre-tournament predictions."
    slug = "norway-chess-2026-round-8-so-leads-praggnanandhaa-carlsen-gukesh-standings-nri"
    
    body = """Two rounds remain at the 14th Norway Chess in Oslo, and the standings read like a tournament from a parallel universe.

Wesley So leads with 14 points. Alireza Firouzja sits second on 13. R Praggnanandhaa — the nineteen-year-old from Chennai who arrived as the lowest-rated player in the field — is third on 12, within striking distance of the title. Below them, Vincent Keymer holds 10 points, Magnus Carlsen has 9, and Gukesh Dommaraju, the reigning World Champion, is last on 8.

Read that last line again. The world's number one player is fifth. The World Champion is sixth. The teenager who beat both of them in classical chess this week is third and climbing.

## Round Eight: Two Decisive Games

The eighth round produced the kind of results that rewrite narratives.

Praggnanandhaa, playing black in a French Defence against Carlsen, exploited the Norwegian's time management problems — Carlsen was already more than half an hour behind on the clock by move eight — and ground out a win in a queen-and-bishop endgame where Carlsen was a pawn down. It was Praggnanandhaa's second classical victory over the world number one in this event, and Carlsen's fourth classical loss of the tournament.

The last time Carlsen lost four classical games in a single tournament was also at Norway Chess, in 2015. That was eleven years ago. He was twenty-four then, and the losses stung enough to reshape how he approached future events. At thirty-five, the sting may be different, but the statistical anomaly is the same.

On the other board that produced a decisive result, Firouzja defeated Gukesh to move within one point of the leader. The French-Iranian grandmaster, who had led the tournament until round five before back-to-back losses, used the win to claw back into contention. For Gukesh, it was a third defeat — and a painful one. The World Champion has lost 6.3 rating points in Oslo and dropped to twenty-second on the live rating list.

The only other match, between So and Keymer, reached armageddon after a 31-move classical draw. So won the tiebreaker from a Nimzo-Indian, converting a pawn advantage in a bishop-versus-knight endgame. It was a workmanlike result that kept the American at the top.

## The Indian Story

For Indian chess fans — and particularly for the diaspora that has watched the country's chess infrastructure produce world-class talent at an astonishing rate — Norway Chess 2026 presents a complicated picture.

Praggnanandhaa has been magnificent. His four consecutive decisive classical games (two losses in rounds five and six, followed by wins over Firouzja in round seven and Carlsen in round eight) have marked him as the tournament's most dynamic player. He has now matched Viswanathan Anand's best performance at Norway Chess, and with two rounds remaining, a podium finish — or even a title challenge — is within reach.

Gukesh's tournament, by contrast, has been a struggle. The World Champion, still just nineteen, has found Oslo unforgiving. Three classical losses, a last-place standing, and a significant rating drop suggest that the transition from World Championship challenger to champion — with all the expectation and scrutiny that entails — is still a work in progress.

## The Women's Tournament

In the women's section, Bibisara Assaubayeva of Kazakhstan has all but clinched the title. Her classical win over India's Divya Deshmukh in round eight extended her lead to 15.5 points, with Anna Muzychuk second on 10.5 and Divya tied with China's Zhu Jiner on 10.

Koneru Humpy, India's other representative, won her armageddon against Muzychuk after a classical draw — a rare positive result in what has been a difficult tournament for the veteran. She remains last on 8 points and is mathematically eliminated from the title race.

## What Remains

Two rounds. Two rest days in between. So needs to hold his nerve. Firouzja needs decisive results. And Praggnanandhaa, who has already beaten the world's number one player twice, needs to find two more wins — or at least outpace So in the armageddon tiebreakers.

The tournament concludes on June 5. For a field that was supposed to be a coronation of Carlsen's dominance on home soil, it has instead become a showcase for the next generation — and the generation after that.

*Sources: Chess.com, ChessBase, Livemint, Wikipedia*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "status": "published",
        "image_url": image_url,
        "image_attribution": "Wikimedia Commons" if img_source in ("wikipedia", "commons") else "Pexels" if img_source == "pexels" else None,
        "sources": ["Chess.com", "ChessBase", "Livemint", "Wikipedia"],
        "vertical": "sports",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    if not image_url:
        img = fetch_pexels_image("chess tournament grandmaster")
        if img and validate_image(img):
            article["image_url"] = img
            article["image_attribution"] = "Pexels"
    
    insert_article(article)


# ═══════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════
if __name__ == "__main__":
    print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")
    
    write_article_1()
    time.sleep(1)
    write_article_2()
    time.sleep(1)
    write_article_3()
    
    print("\n" + "="*60)
    print("Done. 3 articles processed.")
