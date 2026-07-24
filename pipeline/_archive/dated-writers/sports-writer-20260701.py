#!/usr/bin/env python3
"""Sports writer for The Videshi — July 1, 2026 batch.
Two articles:
1. India Women's Hockey Nations Cup 2026 Champions
2. IPL 2027 Mega Auction Retention Rules Debate
"""
import os, json, requests, urllib.parse, sys, re
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = "TheVideshi/1.0 (thevideshi.com)"
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── image helpers ────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
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

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []

def fetch_pexels(query, per_page=3):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            return [{"url": p["src"]["large2x"], "width": p["width"], "height": p["height"]} for p in photos]
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return []

def verify_image(url):
    """Return True if image URL is accessible and > 5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try reading some bytes if no content-length
        if r.status_code == 200 and "image" in ct:
            chunk = r.raw.read(6000)
            return len(chunk) > 5000
    except:
        pass
    return False

# ── insert helper ────────────────────────────────────────────────────────
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False

# ── dedup check ──────────────────────────────────────────────────────────
def check_existing(slug_fragment):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?select=slug&slug=like.*{slug_fragment}*&status=in.(published,review)&limit=5",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
    )
    if r.status_code == 200:
        return r.json()
    return []

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: India Women's Hockey Nations Cup 2026
# ═══════════════════════════════════════════════════════════════════════
def write_hockey_article():
    slug = "india-women-hockey-nations-cup-2026-champions-auckland-pro-league-deepika-lalremsiami-diaspora-nri"
    
    # Dedup
    existing = check_existing("india-women-hockey-nations-cup")
    if existing:
        print(f"  ⚠ Skipping hockey article — similar slug exists: {existing}")
        return False
    
    print("\n📝 Writing: India Women Hockey Nations Cup Champions")
    
    # Image: Try Commons for Indian women hockey
    hero_url = None
    hero_caption = ""
    hero_attribution = ""
    
    # Try Wikipedia for Indian women's national hockey team
    wiki_img = fetch_wikipedia_person_image("India women's national field hockey team")
    if wiki_img and verify_image(wiki_img):
        hero_url = wiki_img
        hero_caption = "The Indian women's national hockey team"
        hero_attribution = "Wikimedia Commons"
        print(f"  ✓ Using Wikipedia image")

    # Try Commons
    if not hero_url:
        commons = fetch_wikimedia_commons("India women hockey team 2024")
        for c in commons:
            if verify_image(c["url"]):
                hero_url = c["url"]
                hero_caption = f"Indian women's hockey team in action"
                hero_attribution = "Wikimedia Commons"
                print(f"  ✓ Using Commons image: {c['title'][:60]}")
                break
    
    # Try more specific Commons searches
    if not hero_url:
        for q in ["Indian women hockey", "field hockey women India", "FIH Nations Cup women"]:
            commons = fetch_wikimedia_commons(q)
            for c in commons:
                if verify_image(c["url"]):
                    hero_url = c["url"]
                    hero_caption = "Indian women's hockey in international competition"
                    hero_attribution = "Wikimedia Commons"
                    print(f"  ✓ Using Commons image: {c['title'][:60]}")
                    break
            if hero_url:
                break
    
    # Pexels fallback (generic hockey, not person)
    if not hero_url:
        pexels = fetch_pexels("field hockey women sport")
        for p in pexels:
            if verify_image(p["url"]):
                hero_url = p["url"]
                hero_caption = "Women's field hockey in action"
                hero_attribution = "Pexels"
                break

    if not hero_url:
        print("  ✗ No suitable image found for hockey article — skipping")
        return False

    body = """India's women went to Auckland as the lowest-ranked team in the draw. They left as champions.

The Indian women's hockey team won the FIH Nations Cup 2025-26 with a flawless campaign — five matches, five wins, zero defeats — and a composed 2-0 victory over hosts New Zealand in the final on June 21. It is India's second Nations Cup title after the inaugural edition in 2022, and it carries a prize far more valuable than the trophy: automatic promotion back to the FIH Pro League.

## Two Goals, Fifteen Minutes, Game Over

India set the tone inside four minutes. Navneet Kaur thundered a penalty corner past New Zealand goalkeeper Grace O'Hanlon, giving the visitors the kind of early cushion that changes the psychology of a final.

Eleven minutes later, Sunelita Toppo — the 22-year-old from Odisha who has quietly become one of the most reliable finishers in Indian hockey — deflected a sharp drag from Deepika Sehrawat to make it 2-0. The game was effectively over before the first quarter ended.

New Zealand, roared on by a partisan crowd at the North Harbour Hockey Stadium, pushed hard in the second and third quarters. But India's defensive structure — anchored by captain Salima Tete and goalkeeper Savita Punia, who produced a crucial save off a penalty corner in the fourth quarter — held firm.

Lalremsiami, the silky forward from Mizoram, was named Player of the Match in the final. Deepika Sehrawat finished as joint-top scorer in the tournament with six goals, sharing the honour with USA's Ashley Sessa.

## The Road to the Final

India's path through the tournament was relentless. They beat the United States 3-2 in the opener, edged Japan 2-1 in a tense second match, and overcame Uruguay 3-2 to top Pool A. The semi-final against Chile was a statement — a 6-0 demolition that announced India's intentions.

Head coach Sjoerd Marijne, who returned for a second stint with the Indian women's team, has rebuilt the squad around pace in transition and penalty corner efficiency. Both were on full display in Auckland.

## What Pro League Return Means

For the diaspora, the Nations Cup title is significant beyond the scoreboard. India's promotion back to the FIH Pro League means the women's team will play regular home-and-away fixtures against the world's best — the Netherlands, Argentina, Australia, Belgium — in a format that is broadcast globally.

The women's team had been relegated from the Pro League after a difficult 2024-25 season. Winning the Nations Cup was the only way back in. They didn't just win it — they dominated it.

Hockey India announced cash awards of ₹3 lakh per player and ₹1.5 lakh per support staff member to recognise the achievement. It is a welcome gesture, though the real reward is the platform: Pro League fixtures mean visibility, which means sponsors, which means investment in a programme that still operates on a fraction of the men's team's budget.

## The Bigger Picture

India's women are quietly building something. The Tokyo Olympics bronze medal run in 2021 was the breakthrough. The inaugural Nations Cup title in 2022 established consistency. This second title in 2026 — won away from home, against the defending champions, without dropping a match — is evidence of a programme maturing.

With the FIH Hockey World Cup in the Netherlands and Belgium later this year, and the 2028 LA Olympics now firmly in sight as cricket joins the programme, Indian women's hockey has never had more to play for. Auckland showed they are ready for it.

*Sources: FIH, Hockey India, Khel Now, Odisha Connect*"""

    article = {
        "headline": "Unbeaten in Auckland. India Women Lift the Nations Cup and Punch Their Ticket Back to the Pro League.",
        "subheadline": "Navneet Kaur and Sunelita Toppo scored inside fifteen minutes as India beat hosts New Zealand 2-0 in the final to win their second Nations Cup title and earn automatic promotion to the FIH Pro League.",
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "hockey",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": json.dumps(["FIH", "Hockey India", "Khel Now", "Odisha Connect"]),
        "diaspora_angle": "India's Pro League return means regular globally-broadcast fixtures against top nations — NRIs can watch the women's team compete at the highest level again.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return insert_article(article)

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: IPL 2027 Mega Auction Retention Rules
# ═══════════════════════════════════════════════════════════════════════
def write_ipl_article():
    slug = "ipl-2027-mega-auction-retention-rules-bcci-owners-split-salary-cap-rtm-impact-player-diaspora-nri"
    
    # Dedup
    existing = check_existing("ipl-2027-mega-auction")
    if existing:
        print(f"  ⚠ Skipping IPL article — similar slug exists: {existing}")
        return False
    
    print("\n📝 Writing: IPL 2027 Mega Auction Retention Debate")
    
    # Image: Try Commons for IPL/cricket auction
    hero_url = None
    hero_caption = ""
    hero_attribution = ""
    
    # Try Commons for IPL related images
    for q in ["IPL cricket auction", "Indian Premier League 2024", "IPL cricket", "BCCI cricket headquarters Mumbai"]:
        commons = fetch_wikimedia_commons(q)
        for c in commons:
            title_lower = c["title"].lower()
            # Skip logos, SVGs, tiny images
            if any(x in title_lower for x in ["logo", "flag", "icon", "symbol"]):
                continue
            if verify_image(c["url"]):
                hero_url = c["url"]
                hero_caption = "The IPL mega auction shapes franchises for the next three-year cycle"
                hero_attribution = "Wikimedia Commons"
                print(f"  ✓ Using Commons image: {c['title'][:60]}")
                break
        if hero_url:
            break
    
    # Try Pexels for generic cricket scene (not a person)
    if not hero_url:
        pexels = fetch_pexels("cricket stadium India")
        for p in pexels:
            if verify_image(p["url"]):
                hero_url = p["url"]
                hero_caption = "The IPL mega auction will reshape all ten franchises ahead of the 2027 season"
                hero_attribution = "Pexels"
                break
    
    if not hero_url:
        print("  ✗ No suitable image found for IPL article — skipping")
        return False
    
    body = """The most consequential meeting in Indian cricket this year won't happen on a pitch. It will happen in a boardroom.

The BCCI has called IPL franchise owners to a meeting at the end of July — likely July 30 or 31 at the Cricket Centre inside the Wankhede Stadium complex in Mumbai — to finalize the retention rules for the IPL 2027 mega auction. The stakes are enormous. Every decision made in that room will determine which stars stay with their franchises and which become available in what promises to be the richest cricket auction in history.

## The Retention Divide

The franchise owners are split, and the fault lines are revealing.

On one side stands the continuity camp. Kavya Maran, CEO of Sunrisers Hyderabad, has argued for a minimum of seven retentions or Right to Match (RTM) options per franchise. Her reasoning is practical: it takes years to build a squad identity, and younger players need time to mature. "It has taken Abhishek Sharma three years to become consistent with his performances," she noted during discussions with BCCI officials. Kolkata Knight Riders have taken a similar position.

On the other side is Parth Jindal of Delhi Capitals, who has pushed for fewer retentions and a full mega auction. "I was surprised that there was debate on whether to hold the big auction," he said. "Some people said there should not be a mega auction at all. I feel that it evens the playing field. It makes the IPL what it is."

The BCCI is expected to settle somewhere in the middle — five or six retentions per franchise. The logic: retaining more than six players per team would remove the top 60-80 players from the auction, draining it of star power and reducing the event that has become cricket's Super Bowl Draft to a hunt for scraps.

## The ₹120 Crore Question

The salary cap is expected to rise to approximately ₹120 crore in the first year of the next three-year cycle — a significant jump from the ₹100 crore cap in the most recent mini-auction. The increase reflects the windfall from the BCCI's mammoth ₹48,390 crore broadcast deal signed two years ago, which has transformed the economics of every franchise.

With a higher cap comes a higher retention cost. Previously, the top retention slot cost roughly 16-17% of the salary cap. If that ratio holds, the first retention would cost around ₹19-20 crore — a number that will force franchises to think carefully about which players are truly indispensable.

## RTM With a Twist

The Right to Match option — which allows a franchise to re-acquire a player at auction by matching the highest bid — is back on the table, but with a significant modification under discussion.

In the proposed format, when a franchise exercises its RTM, the highest bidder gets one final chance to raise their offer. The franchise must then decide whether to match the new, higher price. It is a mechanism designed to prevent RTM from being an automatic safety net, adding genuine risk to the decision.

## The Impact Player Showdown

Beyond retentions, the meeting will address another divisive issue: the Impact Player rule, which allows teams to substitute a player mid-match.

Jindal has been vocal in his opposition. "Some people want it because it gives a chance to young players. I don't want it. I prefer the game as it is, XI vs XI. All-rounders are very important. You have different players who don't bowl in the IPL or don't bat because of this rule, which is not good for Indian cricket."

The rule has divided the IPL community since its introduction. Its fate may hinge on whether the BCCI views it as entertainment innovation or a structural problem for India's international pipeline.

## What This Means for Pandya, Kohli, and Every NRI's Fantasy Team

For the millions of NRIs who follow the IPL as closely as — or more closely than — any other sporting event, the mega auction is appointment viewing. The retention rules will determine whether Virat Kohli stays at RCB, whether Rohit Sharma remains a Mumbai Indian, whether MS Dhoni's legacy franchise at CSK keeps its core intact, and whether Hardik Pandya — already the subject of a seven-franchise trade war — enters the open market or stays put.

The auction itself, likely to be held in October or November, will be broadcast globally. But the real drama begins now, in the backrooms of the Wankhede, where ten franchise owners and the BCCI will try to agree on rules that could reshape Indian cricket's most lucrative property for the next three years.

*Sources: Cricbuzz, BCCI*"""

    article = {
        "headline": "The IPL's Biggest Boardroom Battle Is Here. Franchise Owners Are Split on How Many Players to Keep.",
        "subheadline": "The BCCI will meet IPL franchise owners at the end of July to finalize retention rules for the mega auction — with the salary cap set to rise to ₹120 crore and a fierce debate over whether the mega auction should even exist.",
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": json.dumps(["Cricbuzz", "BCCI"]),
        "diaspora_angle": "The mega auction is appointment viewing for NRIs worldwide — retention rules will determine whether Kohli stays at RCB, Rohit stays at MI, and whether Pandya enters the open market.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return insert_article(article)

# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    results = []
    results.append(("Hockey Nations Cup", write_hockey_article()))
    results.append(("IPL Mega Auction", write_ipl_article()))
    
    print("\n" + "="*60)
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    
    failed = sum(1 for _, ok in results if not ok)
    if failed:
        print(f"\n⚠ {failed} article(s) failed")
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully")
