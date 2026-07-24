#!/usr/bin/env python3
"""News writer for The Videshi — June 1, 2026 evening batch."""

import json, os, re, sys, time, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# ── env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip("'\"")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
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

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    if not url:
        return False
    try:
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        if "image" in ct:
            chunk = r.content[:10000]
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

def make_sources_json(source_list):
    """Convert list of source strings into the DB's JSON string format."""
    items = []
    for s in source_list:
        items.append({"name": s, "url": ""})
    return json.dumps(items)

def sb_insert(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['slug']}  (id={aid})")
        return aid
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLE 1 ────────────────────────────────────────────────────────────────
def article_zee_fifa():
    print("\n── Article 1: Zee secures FIFA World Cup 2026 broadcasting in India ──")

    slug = "zee-entertainment-fifa-world-cup-2026-india-broadcast-rights-zee5-unite8-20260601"
    headline = "Zee Just Secured the Rights to Broadcast the 2026 FIFA World Cup in India. The Tournament Starts in 10 Days."
    subheadline = "FIFA rejected JioStar's $20 million bid. Zee will carry 39 FIFA events through 2034, including the Women's World Cup 2027 and World Cup 2030."

    body = """India's 1.4 billion football fans finally know where they will watch the 2026 FIFA World Cup. Zee Entertainment announced on Monday that it has secured a long-term broadcasting deal with FIFA covering 39 competitions through 2034 — starting with the tournament that kicks off across the United States, Canada, and Mexico on June 11.

The deal ended months of uncertainty. As recently as last week, India — one of the world's largest television markets — still had no official broadcaster for football's biggest event. The agreement covers the 2026 World Cup, the 2027 Women's World Cup, the 2030 World Cup, and a full slate of youth, futsal, and intercontinental tournaments. Coverage will air on UNITE8 Sports and stream on Zee5 in multiple languages.

## How the Deal Almost Didn't Happen

FIFA originally sought around $100 million for the India media rights package covering the 2026 and 2030 World Cups. That figure dropped to roughly $60 million during negotiations, according to Reuters. Zee's final terms were not publicly disclosed.

The bigger story is who did not get the deal. JioStar — the Reliance-Disney joint venture that broadcast the 2022 World Cup through its predecessor Viacom18 — submitted a bid of approximately $20 million. FIFA rejected it. Sony, which held rights for the 2014 and 2018 editions, held discussions but never submitted a formal bid.

The standoff left Indian viewers in limbo until the last moment, a scenario that has become familiar in Indian sports broadcasting where rights negotiations regularly come down to the wire.

## What This Means for Indian Fans

The 2026 World Cup is the largest in FIFA history: 48 teams, 104 matches, and venues spread across 16 cities in three countries. For Indian fans, the time zone factor is significant — most matches will air between 7:30 PM and 5:30 AM IST, with prime evening slots landing perfectly for India's viewership window.

Zee5's streaming platform will be critical for the Indian diaspora. NRIs in the US, UK, Canada, and the Gulf will need to check whether Zee5's coverage is geo-restricted or available through international subscriptions. In previous tournaments, streaming platforms offered separate international packages that did not always mirror domestic availability.

## The Bigger Picture

Zee's aggressive push into sports comes at a time when the company is looking to differentiate itself from JioStar's dominance in cricket. While JioStar controls IPL and most ICC cricket rights, Zee is building a portfolio around football, positioning UNITE8 Sports as a challenger brand.

For FIFA, the India deal — however much it was discounted — locks in the world's most populous country and one of its fastest-growing streaming markets. India's football culture is surging, driven by the Indian Super League, growing Premier League viewership, and a generation of fans who discovered the sport through FIFA video games and social media.

The 2026 World Cup kicks off on June 11 when Mexico hosts their opener at the Estadio Azteca. The final is scheduled for July 19 at MetLife Stadium in New Jersey, where Shakira, Madonna, and BTS will perform at halftime."""

    sources = make_sources_json([
        "Reuters — Zee Entertainment to broadcast 2026 FIFA world cup in India (June 1, 2026)",
        "Athlon Sports — FIFA Lands Major India Broadcast Deal 10 Days Before 2026 World Cup (June 1, 2026)",
        "Mint — With 10 days to go, how will Indians watch FIFA World Cup 2026? (June 1, 2026)",
    ])

    img_url = fetch_pexels_image("FIFA World Cup trophy football", "football stadium fans celebration")
    if img_url and not validate_image(img_url):
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "media",
        "status": "published",
        "is_editorial": False,
        "is_featured": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": "Pexels" if img_url else None,
    }


# ── ARTICLE 2 ────────────────────────────────────────────────────────────────
def article_trump_hezbollah():
    print("\n── Article 2: Trump claims first direct US-Hezbollah communication ──")

    slug = "trump-hezbollah-direct-call-lebanon-ceasefire-netanyahu-beirut-oil-prices-20260601"
    headline = "Trump Says He Spoke Directly With Hezbollah. No US President Has Ever Done That Before."
    subheadline = "Netanyahu agreed to pull troops back from Beirut. Hezbollah agreed to stop shooting. Oil prices jumped 5 percent before the announcement. Israel-Lebanon talks are set for Tuesday."

    body = """In a post on Truth Social on Monday, US President Donald Trump said he had a "very good call with Hezbollah" through intermediaries and that the group agreed to stop all attacks on Israel. He also said he had a "very productive call" with Israeli Prime Minister Benjamin Netanyahu, who agreed to pull back troops from Beirut.

No US president has ever communicated directly with Hezbollah, with or without intermediaries. The group has been designated as a foreign terrorist organization by the United States since 1997.

## The Sequence of Events

The day began with a diplomatic crisis. Iran's semi-official Tasnim news agency reported that Tehran was halting all indirect negotiations with the US, citing Israel's intensifying military campaign in Lebanon. Oil prices immediately jumped 5 percent on the news, rattling global energy markets.

Israel had pushed its deepest into Lebanon in 25 years, with troops moving beyond the Litani River toward the Zaharani River — roughly 10 kilometers further north. Netanyahu had ordered fresh strikes on Hezbollah-controlled southern suburbs of Beirut.

Then came Trump's intervention. In rapid succession, he posted that Netanyahu had agreed to halt troop movements toward Beirut, that Hezbollah had agreed through representatives to stop shooting, and that talks with Iran were "continuing, at a rapid pace."

Lebanon's President Joseph Aoun confirmed Trump's claims regarding Beirut and said Israel-Lebanon negotiations were scheduled for June 2 and 3.

## Iran's Position Remains Unclear

The picture from Tehran is contradictory. Iranian state media initially announced a full suspension of indirect talks with Washington. Then Iran's foreign ministry said it held the US and Israel responsible for "any violation" of the ceasefire, including in Lebanon. Hours later, Trump posted that talks with Iran were back on.

Speaking to NBC News, Trump appeared unbothered by Iran's earlier walkout. "It's an appropriate thing to say, because they're better negotiators than they are fighters," he said. "But they haven't informed us of that."

The IRGC-affiliated Tasnim had also threatened a "complete closure of the Strait of Hormuz" and activation of the Bab el-Mandeb Strait — the two chokepoints that together control roughly 40 percent of the world's seaborne oil trade.

## What This Means for India

India is watching the Hormuz situation with particular urgency. Any disruption to the Strait directly threatens India's energy security — roughly 60 percent of India's crude oil imports transit through Hormuz. India has already begun diversifying its oil sourcing, pivoting to Venezuela, Brazil, and Angola, but these alternatives are more expensive and logistically complex.

The 5 percent spike in oil prices on Monday — even before any actual blockade — is a reminder of how fragile India's energy economics remain. With crude already trading between $90 and $100 per barrel due to the Iran-US conflict, any sustained disruption would push prices higher and further strain the Reserve Bank of India's inflation management ahead of its policy decision on Friday.

Indian equity markets fell for the fourth consecutive session on Monday, with the Nifty 50 dropping 0.7 percent to 23,382 and the Sensex losing 0.68 percent to 74,267. Foreign investors sold a record $2.22 billion of Indian shares on Friday during MSCI's May rebalancing.

## The Ceasefire's Fragile State

The US-Iran ceasefire, in effect since early April, was meant to create space for broader negotiations over Iran's nuclear program and the reopening of the Strait of Hormuz. But the ceasefire has been repeatedly tested — over the weekend, the US struck Iranian military sites and Iran's Revolutionary Guards targeted a US base in Kuwait.

Whether Monday's flurry of diplomatic activity represents a genuine de-escalation or merely a pause depends on what happens in the next 48 hours. The Israel-Lebanon talks scheduled for Tuesday and Wednesday will be the first real test."""

    sources = make_sources_json([
        "Reuters — Trump holds calls with Israel, Hezbollah amid hopes Lebanon ceasefire can hold (June 1, 2026)",
        "USA Today — Iran suspends US talks over Israel's attacks in Lebanon (June 1, 2026)",
        "New York Post — Iran calls off negotiations with US following Israeli strike on Beirut (June 1, 2026)",
        "Reuters — Indian shares drop again on outflows, weak monsoon woes (June 1, 2026)",
    ])

    img_url = fetch_wikipedia_person_image("Donald Trump")
    if img_url and not validate_image(img_url):
        img_url = None
    attr = "Wikimedia Commons" if img_url else None
    if not img_url:
        img_url = fetch_pexels_image("Middle East diplomacy oil tanker", "oil tanker strait ocean")
        attr = "Pexels" if img_url else None
        if img_url and not validate_image(img_url):
            img_url = None
            attr = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "published",
        "is_editorial": False,
        "is_featured": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": attr,
    }


# ── ARTICLE 3 ────────────────────────────────────────────────────────────────
def article_sc_judges():
    print("\n── Article 3: President appoints 5 new Supreme Court judges ──")

    slug = "india-five-new-supreme-court-judges-appointed-collegium-may-2026-cji-surya-kant-20260601"
    headline = "India's President Just Appointed Five New Supreme Court Judges. The Court Is Racing to Clear a Backlog of Over 80,000 Cases."
    subheadline = "The appointments follow the Collegium's May 22 and May 27 recommendations and include four High Court chief justices and one senior advocate."

    body = """The President of India has appointed five new judges to the Supreme Court, giving effect to recommendations made by the Collegium headed by Chief Justice of India Surya Kant on May 22 and May 27. Union Law Minister Arjun Ram Meghwal announced the appointments on Monday.

The five appointees are:

**Justice Sheel Nagu**, Chief Justice of the Punjab and Haryana High Court, whose parent court is the Madhya Pradesh High Court.

**Justice Shree Chandrashekhar**, Chief Justice of the Bombay High Court, from the Jharkhand High Court.

**Justice Sanjeev Sachdeva**, Chief Justice of the Madhya Pradesh High Court, from the Delhi High Court.

**Justice Arun Palli**, Chief Justice of the High Court of Jammu and Kashmir and Ladakh, from the Punjab and Haryana High Court.

**Senior Advocate V. Mohana**, practicing at the Supreme Court of India — the only non-judge among the five.

## Why This Matters Now

India's Supreme Court has been grappling with a mounting case backlog. The latest data shows more than 80,000 cases pending before the court, a number that has grown steadily despite efforts to increase judicial strength. The President recently issued an ordinance to expand the court's capacity, and these five appointments are part of that broader push.

The selection of four sitting High Court chief justices signals the Collegium's emphasis on administrative experience. Each of the four has led a major High Court and managed complex docket pressures — experience directly applicable to the Supreme Court's own capacity challenges.

The inclusion of Senior Advocate V. Mohana marks a continuation of the tradition of elevating distinguished lawyers directly to the bench, bringing a practitioner's perspective to complement career judges.

## The Week That Was in India's Courts

The appointments cap an extraordinary week for India's judiciary. The Supreme Court issued a comprehensive victim protection plan for human trafficking survivors, directed all High Courts to deliver reserved judgments within three months, and issued pan-India directions on trauma care for road accident victims under Article 21's right to life.

The court also issued notice on a petition challenging CBSE's new three-language mandate for Class IX students — a policy requiring at least two of three languages to be native Indian languages, with foreign languages relegated to a secondary position. The challenge raises questions about educational autonomy and parental choice that resonate deeply with NRI families navigating language instruction for children straddling two cultures.

Meanwhile, the Centre moved to transfer petitions challenging the Transgender Persons (Protection of Rights) Amendment Act, 2026, from four High Courts to the Supreme Court — consolidating a constitutional challenge that will likely become one of the court's most closely watched cases this term.

## What This Means for the Indian Diaspora

For the Indian diaspora, the court's direction matters profoundly. Property disputes, inheritance claims, NRI-specific tax cases, and OCI rights issues all flow through India's judicial system. A stronger, better-staffed Supreme Court means faster resolution of the cases that directly affect Indians living abroad.

Over the past year, the government and Collegium have accelerated appointments to both the Supreme Court and High Courts, where vacancies had reached alarming levels. The five judges will take their oaths in the coming days, bringing the Supreme Court closer to its sanctioned strength — and closer to the capacity it needs to manage the world's largest democracy's heaviest docket."""

    sources = make_sources_json([
        "SCC Online — President Appoints 5 Judges to Supreme Court Following Collegium Recommendations (June 1, 2026)",
        "LawBeat — Supreme Court Weekly Round Up May 25-31 2026 (June 1, 2026)",
        "LawBeat — Law and Justice This Week May 25-31 2026 (June 1, 2026)",
    ])

    img_url = fetch_pexels_image("India Supreme Court building New Delhi", "Indian court justice")
    attr = "Pexels" if img_url else None
    if img_url and not validate_image(img_url):
        img_url = None
        attr = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "politics",
        "status": "published",
        "is_editorial": False,
        "is_featured": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_attribution": attr,
    }


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    articles = [article_zee_fifa(), article_trump_hezbollah(), article_sc_judges()]
    success = 0
    for art in articles:
        aid = sb_insert(art)
        if aid:
            success += 1
    print(f"\n✅ Published {success}/{len(articles)} articles.")

if __name__ == "__main__":
    main()
