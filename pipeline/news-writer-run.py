#!/usr/bin/env python3
"""
News Writer for The Videshi — June 2, 2026
Generates 3 fresh news articles with proper image sourcing and publishes to Supabase.
"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import requests
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
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate that an image URL returns a valid image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            return True
        # Try GET if HEAD doesn't give Content-Length
        if r.status_code == 200 and 'image' in content_type:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=30,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Failed to download image: status={r.status_code}, size={len(r.content)}")
            return None

        content_type = r.headers.get('Content-Type', 'image/jpeg')
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        
        resp = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        
        if resp.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if resp.status_code in [200, 201]:
        data = resp.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else data.get('id')
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


def patch_article(art_id, updates):
    """Patch an article with updates."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}"
    resp = requests.patch(url, headers=HEADERS, json=updates, timeout=15)
    if resp.status_code in [200, 204]:
        print(f"  ✓ Patched article {art_id}")
    else:
        print(f"  ⚠ Patch failed: {resp.status_code} {resp.text[:200]}")


# ============================================================
# ARTICLE 1: India-UK Trade Deal in Trouble
# ============================================================
def write_article_1():
    print("\n📰 Article 1: India-UK Trade Deal — Scotch Whisky vs Steel")
    
    slug = "india-uk-trade-deal-scotch-whisky-steel-safeguards-piyush-goyal-peter-kyle-20260602"
    
    headline = "India Just Threatened to Pull the Scotch Whisky Tariff Cut. Britain's Steel Restrictions Are the Reason."
    
    subheadline = "A year-old trade deal that promised to reshape commerce between the world's fifth- and sixth-largest economies is unravelling before it has even taken effect. Britain's Trade Secretary is in New Delhi today to try to fix it."
    
    body = """India has warned Britain that it will reverse tariff concessions on Scotch whisky and other goods if London does not withdraw new steel safeguard measures that threaten Indian exports, a senior trade official said on Monday.

"So now the ball is in their court," the official told reporters. "If they do not leverage their free trade agreement, we can always reconsider the concessions we offered."

The warning lands as Britain's Trade Secretary Peter Kyle arrived in New Delhi on Tuesday for talks with Commerce Minister Piyush Goyal — a meeting that was supposed to finalize the implementation timeline for a deal both sides signed in July 2025 with considerable fanfare. Instead, it has become a damage-control exercise.

## The Steel Problem

The India-UK Comprehensive Economic and Trade Agreement, formally concluded last year but still not in force, hit a wall when Britain proposed slashing tariff-free steel import quotas from July 1, 2026, and nearly doubling the duty on shipments exceeding the reduced quota to 50 per cent.

India's steel exports to the UK totalled roughly $900 million in the financial year ending March 2026. Under the new safeguard measures, much of that trade could be hit, according to industry estimates.

New Delhi's objections extend beyond steel. Indian officials said they also plan to raise concerns about Britain's Carbon Border Adjustment Mechanism, which would impose levies on exports of steel, aluminium and fertilisers — measures India views as protectionist rather than environmental.

"Right now, India is more bothered about the steel import quotas as the new measures will be applicable from next month," a person tracking the discussions told reporters. "Carbon levies are still some months away, but those need to be discussed too."

## What India Is Threatening

Under the trade pact, India agreed to cut tariffs on Scotch whisky from 150 per cent to 75 per cent initially, with further reductions to 40 per cent over ten years. The deal also covers textiles, cars and a range of other goods, with both sides expecting it to boost bilateral trade by an additional £25.5 billion ($34 billion) by 2040.

If Britain does not respond to India's concerns, New Delhi could take "rebalancing" measures — a diplomatic term for withdrawing benefits as a tit-for-tat response.

India is not alone in its objections. Brazil, Turkey, Japan, South Korea, Switzerland and Australia have all raised concerns at the World Trade Organization over Britain's new steel import restrictions.

## The Diaspora Dimension

For the 1.8 million-strong Indian diaspora in the UK — and the growing number of Indian students and professionals in Britain — the trade deal promised more than tariff cuts. It was supposed to deliver enhanced mobility provisions, mutual recognition of qualifications and easier visa pathways for Indian professionals.

Those provisions are now hostage to a steel dispute that neither side anticipated when the deal was signed.

Britain's position is delicate. Kyle has described the deal as a "win-win" for both nations but has carefully avoided addressing the steel issue directly in public statements. His team has sought to separate the steel safeguard discussions from the broader FTA implementation — a distinction India has explicitly rejected.

## What Happens Next

The Goyal-Kyle meeting on Tuesday will determine whether the deal can be rescued before Britain's new steel measures take effect on July 1. If India follows through on its threat, British whisky producers — who have spent a year preparing for the Indian market at lower tariffs — would be the first casualties.

The UK whisky industry exports approximately £530 million worth of Scotch to India annually, making it one of the most commercially significant products in the deal. A reversal would be a significant blow to a sector that had banked on the agreement to finally crack a market where 150 per cent tariffs have long made Scotch a luxury few could afford.

The stakes extend well beyond whisky and steel. If the India-UK deal collapses before implementation, it would undermine both nations' credibility as reliable trade partners at a moment when both are simultaneously negotiating with the United States — and when the global trade architecture is under unprecedented strain from tariffs, wars and competing economic blocs."""
    
    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"}
    ])
    
    # Image sourcing — Pexels for trade/diplomatic concept
    img_url = fetch_pexels_image("British whisky scotch barrels trade", "steel factory industry trade")
    
    image_attribution = "Pexels"
    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")
        if not final_img:
            final_img = img_url  # Pexels URLs are permanent
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade",
        "tags": ["india-uk", "trade", "scotch-whisky", "steel", "tariffs", "piyush-goyal"],
        "urgency": "high",
        "diaspora_angle": "The India-UK trade deal includes enhanced mobility provisions, qualification recognition and visa pathways for Indian professionals in the UK — all now hostage to a steel dispute. The 1.8 million-strong Indian diaspora in Britain and Indian students face uncertainty.",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": final_img or "",
        "image_attribution": image_attribution if final_img else "",
        "is_editorial": False,
        "is_featured": False,
        "score_total": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 2: FII Record Outflow
# ============================================================
def write_article_2():
    print("\n📰 Article 2: Foreign Investors Smash Annual Record in Just 5 Months")
    
    slug = "foreign-investors-26-billion-outflow-india-2026-annual-record-five-months-iran-war-20260602"
    
    headline = "Foreign Investors Have Now Pulled More Money Out of India in 2026 Than They Did in All of 2025."
    
    subheadline = "It took them just five months. The $26.4 billion exodus — driven by the Iran war, $94 oil and a weak monsoon forecast — has surpassed last year's full-year record of $18.91 billion and shows no sign of slowing."
    
    body = """Foreign portfolio investors have now pulled $26.4 billion out of Indian equities in 2026, smashing through the previous full-year record of $18.91 billion set in 2025 — and the year is not even half over.

The milestone, crossed on Monday as overseas funds sold another $411.8 million in a single session, marks the worst sustained exodus from India's $4.8 trillion stock market since records began. On Friday, MSCI's May rebalancing triggered a single-day fire sale of $2.22 billion — the largest one-day foreign sell-off in Indian market history.

Indian benchmarks fell for a fifth straight session on Tuesday. The Nifty 50 dropped 0.66 per cent to 23,229 and the Sensex shed 0.43 per cent to 73,945 in early trade, having already lost 2.9 per cent over the past four sessions. Fifteen of 16 major sectors logged losses.

## Why They Are Leaving

The scale of the retreat reflects a convergence of forces that have made India increasingly unattractive to global capital.

**The Iran war.** Since the US-Israeli strikes on Iran began in late February, foreign investors have pulled nearly $25 billion from Indian equities. Oil — India imports 85 per cent of its crude — has hovered near $94 per barrel, squeezing corporate margins and widening the current account deficit.

**Earnings stagnation.** Nifty 50 companies have now posted eight consecutive quarters of single-digit earnings growth. "If there is no resolution to the Iran war in the near term and crude prices sustain between $90 to $100 per barrel, FY27 earnings estimates could be downgraded as well," said Sunny Agrawal, head of fundamental equity research at SBICAPS Securities.

**Monsoon risk.** The India Meteorological Department has forecast the weakest monsoon in 11 years, rattling consumer goods and automobile stocks. FMCG shares fell 1.7 per cent on Monday and auto stocks shed 2.3 per cent.

**MSCI rebalancing.** The index provider's May reshuffle triggered a wave of passive selling, with $2.3 billion exiting India on a single day as global index-tracking funds mechanically adjusted their allocations.

## The Rupee Under Siege

The outflows have left the rupee teetering. It settled at 94.99 to the dollar on Monday — held up almost entirely by the Reserve Bank of India's aggressive interventions. The central bank has spent down its forex reserves to $681 billion, the lowest in over a year, and reduced its short forward dollar commitments from over $100 billion in March to $95.3 billion by end-April.

MUFG, the Japanese banking group, warned in a research note that the rupee could fall to 98 — and possibly even 100 — against the dollar if the conflict drags on or escalates.

"We continue to view the Indian rupee as vulnerable across a range of scenarios on the Strait of Hormuz, with USD/INR likely moving towards 98.00 levels and even 100.00 is in sight if the conflict prolongs or escalates," the analysts wrote.

## Can Domestic Investors Absorb the Blow?

India's domestic institutional investors — powered by a record 8 crore-plus SIP (Systematic Investment Plan) accounts — have poured $31 billion into the market this year, more than compensating for foreign exits in absolute terms. But cracks are appearing in the domestic cushion.

CLSA warned in April that mutual fund cash levels had dropped 24 per cent from their April 2025 peak, signalling "the first signs of depletion in the resources of DIIs after 18 months of fighting this battle of equity flows."

The IT sector has been a rare bright spot, rising 2.7 per cent on Monday after strong earnings from Snowflake lifted global software and cloud stocks. But the broader market tells a different story: small-caps and mid-caps, where retail investors are most exposed, fell 0.9 per cent and 1.5 per cent respectively.

## What NRIs Should Watch

The RBI's monetary policy decision on Friday is the week's defining event. Nearly 80 per cent of economists expect the central bank to hold rates at 5.25 per cent, but MUFG dissents, predicting a 25 basis-point hike to defend the rupee.

For NRIs with investments in Indian markets — or those considering repatriating funds — the key question is whether the RBI can hold the rupee near 95 without burning through its reserves. India's Q1 GDP data, also due Friday, will test whether the world's fastest-growing major economy can sustain that title through a war, an oil shock and a monsoon that may not arrive.

The foreign exit is no longer a correction. It is a structural repositioning — and it is happening faster than anyone predicted."""
    
    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "MUFG Research", "url": "https://www.mufg.jp"},
        {"name": "SBICAPS Securities", "url": "https://www.sbicaps.com"},
        {"name": "CLSA", "url": "https://www.clsa.com"}
    ])
    
    # Image — Pexels for stock market / financial trading
    img_url = fetch_pexels_image("stock market trading screen crash", "financial markets data charts")
    
    image_attribution = "Pexels"
    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")
        if not final_img:
            final_img = img_url
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "tags": ["fii-outflows", "indian-markets", "rupee", "iran-war", "rbi", "msci"],
        "urgency": "high",
        "diaspora_angle": "NRIs with investments in Indian equities or considering fund repatriation face a key decision point as the rupee weakens toward 95-100 and RBI burns forex reserves. The Q1 GDP data and RBI decision on Friday will shape NRI investment strategy.",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": final_img or "",
        "image_attribution": image_attribution if final_img else "",
        "is_editorial": False,
        "is_featured": False,
        "score_total": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 3: Trump Backs Down on Weaponization Fund
# ============================================================
def write_article_3():
    print("\n📰 Article 3: Trump Weaponization Fund Killed by Own Party")
    
    slug = "trump-weaponization-fund-killed-republicans-jan-6-slush-fund-ice-funding-20260602"
    
    headline = "Trump's Own Party Just Killed His $1.8 Billion 'Weaponization' Fund. It Was the Price of Getting His Border Bill Passed."
    
    subheadline = "Senate Republicans refused to move on $72 billion in immigration enforcement funding until the White House agreed to scrap a fund critics called a slush fund for January 6 defendants. Mitch McConnell called it 'utterly stupid, morally wrong.'"
    
    body = """President Donald Trump's $1.776 billion "anti-weaponization" fund — designed to compensate Americans who claimed they were unfairly targeted by the Biden and Obama administrations — is effectively dead, killed not by Democrats or federal judges but by members of Trump's own party.

The Justice Department announced on Monday that it would "abide by" a federal judge's ruling pausing the fund, after the White House faced what multiple sources described as an ultimatum from Senate Republican leaders: drop the fund, or the $72 billion bill to fund Immigration and Customs Enforcement and Border Patrol dies.

"They gave us an ultimatum," a White House source told Reuters.

## What Happened

The fund emerged from a legal settlement between Trump and the Justice Department to resolve an unprecedented $10 billion lawsuit against the IRS over the alleged mishandling of his tax records. The $1.776 billion was supposed to pay restitution to people who said they had been "weaponized" against by the federal government.

But the fund sparked immediate fury when critics — including Republican senators — realized it could direct taxpayer money to people who attacked the U.S. Capitol on January 6, 2021.

Senator Mitch McConnell of Kentucky, the former Republican leader, called it "utterly stupid, morally wrong." Senators reportedly yelled at acting Attorney General Todd Blanche during a closed-door meeting that Senator Ted Cruz of Texas described as "one of the roughest meetings I've seen in my entire time in the Senate."

The Republican rebellion was extraordinary given Trump's insistence on absolute loyalty and his track record of backing primary challengers against those who defy him.

## The Political Calculus

The timing was brutal for the White House. Senate Republicans returned from their Memorial Day recess facing an impasse: they could not pass the $72 billion immigration enforcement bill — Trump's top domestic priority — while the weaponization fund hung over the proceedings.

Trump had set a June 1 deadline for the funding package. The deadline was missed.

Senate Majority Leader John Thune made the stakes clear. "I do think the best way to handle it is if the administration decides to shut it down themselves," he told reporters on Monday.

House Speaker Mike Johnson discussed the fund with Trump during a nearly three-hour White House meeting on Monday. Shortly after, the Justice Department issued its statement.

## Not Quite Dead

The fund is paused, not officially terminated — and that distinction matters.

A federal judge in Virginia temporarily halted the fund on May 29 and scheduled a June 12 hearing. The Justice Department said it "disagrees strongly" with the ruling but would comply.

Separately, a Florida judge overseeing Trump's original lawsuit against the IRS has ordered his attorneys to respond to "grievous allegations" that the president abandoned his claims to avoid scrutiny of what critics called an illegal deal.

Democrats are not taking chances. Senate Minority Leader Chuck Schumer announced on Monday that his caucus would "launch a coordinated effort to kill the slush fund before one cent goes out the door."

"There will be no escape hatch," Schumer wrote in a letter to colleagues. "No fake guardrails or backroom promises to hide behind."

## Why This Matters Beyond Washington

The fund's collapse is significant not because of its dollar amount — $1.8 billion is a rounding error in federal spending — but because of what it reveals about the limits of presidential power in Trump's second term.

Republican senators, many facing midterm elections in November, calculated that the political cost of defending payments to January 6 defendants outweighed the cost of defying a president who has made loyalty his defining test. That calculation may not have been possible even six months ago.

For the Indian diaspora watching from the United States, the episode is a reminder that domestic political dysfunction has real downstream effects. The ICE and Border Patrol funding package — which includes provisions affecting visa processing times, asylum adjudication and workplace enforcement — remains stuck in limbo. Its passage now seems more likely with the fund removed, but the delay has already pushed back implementation timelines that affect millions of immigrants, including the estimated 4.4 million Indian Americans navigating the U.S. immigration system.

Acting Attorney General Todd Blanche, who had been seeking permanent appointment as attorney general, may be the biggest casualty. Two sources told CNN the fund was "Blanche's idea" — a characterization the Justice Department disputes — and the debacle has raised serious questions about whether he can win Senate confirmation."""
    
    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "Morningstar", "url": "https://www.morningstar.com"}
    ])
    
    # Image — Wikipedia for Trump
    img_url = fetch_wikipedia_person_image("Donald Trump")
    if not img_url:
        img_url = fetch_pexels_image("US Capitol building Washington", "American politics government building")
    
    image_attribution = "Wikimedia Commons"
    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")
        if not final_img and 'wikimedia' in (img_url or '') or 'pexels' in (img_url or ''):
            final_img = img_url
    
    if not final_img:
        image_attribution = ""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "politics",
        "tags": ["trump", "weaponization-fund", "republicans", "jan-6", "ice-funding", "congress"],
        "urgency": "medium",
        "diaspora_angle": "The ICE and Border Patrol funding package — stalled by this controversy — includes provisions affecting visa processing times, asylum adjudication and workplace enforcement for the estimated 4.4 million Indian Americans navigating the US immigration system.",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": final_img or "",
        "image_attribution": image_attribution,
        "is_editorial": False,
        "is_featured": False,
        "score_total": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer Run")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    results = []
    
    try:
        art1 = write_article_1()
        results.append(("India-UK Trade Deal", art1))
    except Exception as e:
        print(f"  ✗ Article 1 failed: {e}")
        results.append(("India-UK Trade Deal", None))
    
    try:
        art2 = write_article_2()
        results.append(("FII Record Outflow", art2))
    except Exception as e:
        print(f"  ✗ Article 2 failed: {e}")
        results.append(("FII Record Outflow", None))
    
    try:
        art3 = write_article_3()
        results.append(("Trump Weaponization Fund", art3))
    except Exception as e:
        print(f"  ✗ Article 3 failed: {e}")
        results.append(("Trump Weaponization Fund", None))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for title, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {title}: {status}")
    
    successes = sum(1 for _, aid in results if aid)
    print(f"\n  Published: {successes}/{len(results)} articles")
    print("=" * 60)
