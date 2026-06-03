#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-06-03 batch."""

import json, os, re, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── env ──
for envf in [os.path.expanduser("~/workspace/.env.supabase"), os.path.expanduser("~/workspace/.env.pexels")]:
    if os.path.exists(envf):
        with open(envf) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
UA = "TheVideshi/1.0 (thevideshi.com)"


# ── image helpers ──

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for p in pages.values():
                ii = p.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                w = ii.get("width", 0)
                if url and "image" in mime and w >= 300:
                    results.append(url)
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": per_page},
                         headers={"Authorization": PEXELS_KEY}, timeout=10)
        if r.status_code == 200:
            return [p["src"]["large2x"] for p in r.json().get("photos", [])]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []


def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Sometimes HEAD fails; try GET with stream
        r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct2 = r2.headers.get("Content-Type", "")
        chunk = r2.raw.read(6000)
        r2.close()
        if r2.status_code == 200 and "image" in ct2 and len(chunk) >= 5000:
            return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}...: {e}")
    return False


def best_image(wiki_person=None, commons_query=None, pexels_query=None):
    candidates = []
    if wiki_person:
        url = fetch_wikipedia_person_image(wiki_person)
        if url:
            candidates.append(("wikipedia", url))
    if commons_query:
        for u in fetch_wikimedia_commons(commons_query):
            candidates.append(("commons", u))
    if pexels_query:
        for u in fetch_pexels(pexels_query):
            candidates.append(("pexels", u))
    for source, url in candidates:
        if validate_image(url):
            print(f"  ✓ Using {source} image: {url[:80]}...")
            return url, source
    print("  ✗ No valid image found")
    return None, None


# ── article publishing ──

def publish_article(article):
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
        "sources": json.dumps(article.get("sources", [])),
        "is_editorial": False,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    r = requests.post(f"{SB_URL}/rest/v1/p2_articles", headers=HEADERS,
                      json=payload, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        row = data[0] if isinstance(data, list) else data
        print(f"  ✅ Published: {row.get('slug', article['slug'])}")
        return True
    else:
        print(f"  ❌ Publish failed ({r.status_code}): {r.text[:200]}")
        return False


# ══════════════════════════════════════════════════
# ARTICLE 1: India's bumper 12-match NZ tour
# ══════════════════════════════════════════════════

def article_india_nz_tour():
    print("\n📰 Article 1: India's 12-match NZ tour")

    img_url, img_src = best_image(
        commons_query="India cricket New Zealand",
        pexels_query="cricket stadium New Zealand"
    )

    headline = "Twelve Matches. Five Cities. Two Tests. India's New Zealand Tour Will Be the Biggest in NZC History."
    subheadline = "New Zealand Cricket has unveiled a 42-day, all-format itinerary starting in October. For NRIs in Australasia, it is the home-summer event of a lifetime."

    body = """India will tour New Zealand later this year for the largest international cricket tour the country has ever hosted — twelve matches across all three formats, spread over 42 days and eight venues from Christchurch to Mount Maunganui.

New Zealand Cricket confirmed the schedule on June 3, calling it the centrepiece of their 2026-27 home summer. The tour opens with five T20Is beginning October 22 in Christchurch, rolls into five ODIs from November 4, and culminates in two Test matches — the first at Wellington's Basin Reserve starting November 19, and the second at Christchurch's Hagley Oval from November 27 to December 1.

## An Unprecedented Scale

No visiting team has ever played this many matches on a single New Zealand tour. The previous high was nine games — and even that figure feels modest against this itinerary's ambition. The series also marks India's return to Test cricket in New Zealand for the first time since 2019, and their first white-ball assignment there since 2022.

"When it comes to cricket, it simply doesn't get bigger than India and we're determined to deliver New Zealanders a tour like no other," said Glenn Critchley, NZC's Chief Marketing and Commercial Officer. "We're expecting all of these games to sell out."

The tour will coincide with celebrations marking 100 years of sporting ties between India and New Zealand — a relationship that has produced some of the most memorable contests in recent ICC tournament history, from the 2019 World Cup semi-final in Manchester to the 2021 World Test Championship final in Southampton.

## The Full Schedule

The T20I leg runs through four cities: Christchurch (October 22 and 24), Wellington (October 27), Auckland (October 30), and Hamilton (November 1). The ODIs move across Auckland (November 4), Wellington (November 7), Hamilton (November 10), and Mount Maunganui (November 13 and 15). The Tests round out the tour in Wellington and Christchurch.

## What It Means for the Diaspora

For the roughly 250,000 people of Indian origin living in New Zealand, and the hundreds of thousands more across Australia and the Pacific, this is as close as home-ground advantage gets. Kohli, Bumrah, Gill, and the full Indian contingent will be in their time zone for nearly six weeks.

NZC has signalled it expects enormous demand for tickets, particularly for the T20Is in Auckland and the Tests. Indian fans made their presence felt during the 2020 series, when Wellington's Basin Reserve saw stretches of the crowd draped in tricolour — and that was for a two-Test tour. A twelve-match marathon will amplify that by orders of magnitude.

https://x.com/BLACKCAPS/status/1929885263649284096

## Broader Context

India's packed calendar continues to accelerate. They face Afghanistan in a one-off Test starting June 6 in Mullanpur, followed by three ODIs. Then comes a full white-ball tour of England in July featuring five T20Is and three ODIs. The New Zealand leg arrives barely two months after that England assignment concludes.

For New Zealand, the home summer also includes hosting Sri Lanka for three ODIs, three T20Is, and two Tests in January and February 2027. The White Ferns women's team will host Bangladesh for three T20Is and three ODIs in December.

But the India tour is the commercial and cricketing headline. NZC knows it. The Indian diaspora in Australasia knows it. And with Kohli, Bumrah, and a World Cup on the 2027 horizon, the cricket world will be watching.

*Sources: Reuters, Cricket Addictor, New Zealand Cricket*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "india-new-zealand-tour-2026-27-twelve-matches-biggest-ever-nzc-nri",
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_src == "commons" else ("Pexels" if img_src == "pexels" else None),
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/sports/cricket/india-set-bumper-new-zealand-tour-later-this-year-2026-06-03/"},
            {"name": "Cricket Addictor", "url": "https://cricketaddictor.com/cricket-news/india-tour-of-new-zealand-2026-full-schedule-announced-nzc-set-to-host-biggest-tour-in-its-history-459967/"},
            {"name": "New Zealand Cricket", "url": "https://www.nzc.nz/"}
        ]
    }


# ══════════════════════════════════════════════════
# ARTICLE 2: Sairaj Bahutule — India spin bowling coach
# ══════════════════════════════════════════════════

def article_bahutule():
    print("\n📰 Article 2: Sairaj Bahutule spin bowling coach")

    img_url, img_src = best_image(
        wiki_person="Sairaj Bahutule",
        commons_query="Sairaj Bahutule cricket",
        pexels_query="cricket spin bowling India"
    )

    headline = "The BCCI Has Named Sairaj Bahutule as India's Spin Bowling Coach. He Replaces a Vacancy No One Wanted to Talk About."
    subheadline = "The 53-year-old domestic legend with 630 first-class wickets joins Gambhir's staff ahead of the Afghanistan series. His brief: rebuild India's spin identity after Ashwin's retirement and Jadeja's absence."

    body = """Sairaj Bahutule has been appointed India's spin bowling coach across all formats. The Board of Control for Cricket in India confirmed the appointment on June 2, placing the former leg-spinner in the coaching dugout alongside head coach Gautam Gambhir just days before the one-off Test against Afghanistan in Mullanpur on June 6.

The appointment fills a gap that has existed — awkwardly, quietly — since Ravichandran Ashwin retired from international cricket and Ravindra Jadeja was left out of both the Test and ODI squads for the Afghanistan series. India's spin cupboard is not bare, but it is younger and less experienced than at any point in the past decade.

## The Coaching Staff, Now Complete

Bahutule joins a setup that includes Gambhir (head coach), Sitanshu Kotak (batting coach), Morne Morkel (fast bowling coach), Ryan ten Doeschate (assistant coach), and T Dilip (fielding coach). The addition of a dedicated spin bowling coach is a first for this iteration of India's backroom staff, and it arrives at a pointed moment.

India were out-bowled in the spin department by both New Zealand and South Africa in their most recent Test series. The performances of Kuldeep Yadav, Washington Sundar, and younger names like Manav Suthar and Harsh Dubey are promising — but unproven at the international level where it counts. Bahutule's job is to bridge that gap.

"It is a tremendous honour to be appointed as the Spin Bowling Coach of the Indian Men's Cricket Team," Bahutule said in an official BCCI statement. "Representing India as a player was a matter of immense pride, and the opportunity to contribute to Indian cricket once again in a coaching capacity is deeply special."

## A Domestic Giant

Bahutule represented India in two Tests and eight ODIs between 1997 and 2003, taking just five international wickets — a record that does him no justice. In first-class cricket, where the sample size was not constrained by selectors' preferences for orthodox left-arm spin in his era, he was extraordinary: 630 wickets in 188 matches at an average of 26, with four ten-wicket hauls. He scored 6,176 runs with the bat, making him one of the most complete all-rounders Indian domestic cricket has produced.

His coaching résumé is equally deep. He served as head coach of Vidarbha, Kerala, Gujarat, and Bengal in domestic cricket. He was the bowling coach of India's ICC Under-19 World Cup-winning team in 2022 and was part of the coaching staff again in 2024. He worked extensively with India A and spent three years at the BCCI's National Cricket Academy (now Centre of Excellence) from 2021 to 2024.

Most recently, he was Punjab Kings' spin bowling coach during IPL 2026 — where he worked with the likes of Yuzvendra Chahal and local spinners from Punjab's domestic pipeline.

## Why It Matters for the Diaspora

For NRIs who follow Indian cricket with the intensity of a second religion, the spin bowling coach appointment might seem like bureaucratic shuffling. It is not. India's spin identity — the thing that made them lethal at home and competitive abroad for a generation — is in transition. Ashwin is gone. Jadeja is rested indefinitely. The next generation of spinners — Kuldeep, Sundar, Suthar, Dubey — need a mentor who understands the craft at the first-class level and the psychology at the international one.

Bahutule's first task begins this weekend: working with Kuldeep Yadav, Washington Sundar, debutant Manav Suthar, and Harsh Dubey ahead of the Afghanistan Test. Two of those four have never played a Test match. The coach who turns 630 first-class wickets into transferable knowledge will earn his place in this setup.

*Sources: ICC, CricTracker, Khel Now, BCCI*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "sairaj-bahutule-india-spin-bowling-coach-bcci-appointment-gambhir-afghanistan-nri",
        "image_url": img_url,
        "image_attribution": "Wikipedia" if img_src == "wikipedia" else ("Wikimedia Commons" if img_src == "commons" else ("Pexels" if img_src == "pexels" else None)),
        "sources": [
            {"name": "ICC", "url": "https://www.icc-cricket.com/news/india-appoint-new-spin-bowling-coach"},
            {"name": "CricTracker", "url": "https://www.crictracker.com/cricket-news/sairaj-bahutule-joins-indias-backroom-setup-as-spin-bowling-coach-ahead-of-one-off-test-against-afghanistan/"},
            {"name": "Khel Now", "url": "https://khelnow.com/cricket/bcci-appoints-sairaj-bahutule-spin-bowling-coach"}
        ]
    }


# ══════════════════════════════════════════════════
# ARTICLE 3: Hardik Pandya fitness clearance at CoE
# ══════════════════════════════════════════════════

def article_pandya_fitness():
    print("\n📰 Article 3: Hardik Pandya fitness test at CoE")

    img_url, img_src = best_image(
        wiki_person="Hardik Pandya",
        commons_query="Hardik Pandya cricket",
        pexels_query="cricket fitness training India"
    )

    headline = "Pandya Is in Bengaluru. Rohit Is Not. India's Two Biggest ODI Stars Must Pass Fitness Tests Before They Can Play Afghanistan."
    subheadline = "Hardik Pandya has reported to the BCCI Centre of Excellence for a week of drills and match simulations. Rohit Sharma was told to do the same. There is no update on when he will arrive."

    body = """Hardik Pandya arrived at the BCCI Centre of Excellence in Bengaluru on June 2, beginning a week-long fitness assessment that will determine whether he plays the three-match ODI series against Afghanistan starting June 13 in Dharamsala.

The 32-year-old all-rounder was named in India's ODI squad with an asterisk — his participation subject to fitness clearance from the BCCI's medical team. He is expected to undergo fitness drills and match simulations over the next seven days, and will only be granted a return-to-play clearance if the results satisfy the selectors.

Pandya's last ODI appearance was in the 2025 Champions Trophy final against New Zealand in Dubai on March 9, where India won the silverware. Since then, his body has been the recurring subplot: he missed four matches during IPL 2026 for the Mumbai Indians — one due to viral fever, three due to back spasms — and managed only 206 runs in 10 innings with four wickets across the campaign.

## Rohit's Silence

The more concerning absence is Rohit Sharma. The former India captain was also named in the ODI squad with the same fitness caveat, having missed five consecutive IPL matches with a hamstring pull. The BCCI reportedly asked him to report to the CoE alongside Pandya.

As of June 3, there is no information on when — or whether — Rohit will arrive in Bengaluru. He was last seen publicly at the T20 Mumbai League 2026 opener on June 1, performing the coin toss at Wankhede Stadium. With the ODI squad expected to assemble by June 10 or 11, the window is narrowing.

https://x.com/BCCI/status/1929501934072586309

## The Stakes Are Higher Than One Series

The Afghanistan ODIs are not the endgame. They are the first step in India's preparation for the 2027 ODI World Cup — a tournament the selectors have explicitly flagged as their planning horizon. Chief selector Ajit Agarkar said as much when the squads were announced, noting that there are "still 15 to 16 months" before the World Cup and the team wants to "give opportunities to youngsters."

But opportunities for youngsters become urgent necessities if the seniors cannot pass a fitness test. Ishan Kishan has been recalled to the ODI squad after a three-year gap — the last time he played an ODI was also against Afghanistan, during the 2023 World Cup. Prince Yadav, the tall right-arm pacer from Lucknow Super Giants, has earned a maiden call-up on the strength of a standout IPL campaign.

If Pandya passes and Rohit does not, the team takes a fundamentally different shape. If neither passes, India's ODI middle order and leadership group looks younger than it has in years — Shubman Gill captaining, Shreyas Iyer as vice-captain, Kishan and KL Rahul behind the stumps, and Virat Kohli as the senior presence.

## What NRIs Should Watch

The ODI schedule has been tweaked: the first match, originally June 14, has been moved to June 13 at Dharamsala. The second is June 17 in Lucknow. The third is June 20 in Chennai.

For the diaspora, the Pandya-Rohit fitness story is really a succession story. India's white-ball core — the Champions Trophy winners, the T20 World Cup winners — is aging in public. Pandya is 32 with a back that has never fully cooperated. Rohit is 39 with a hamstring that sidelined him during what should have been a farewell IPL season. The question is not whether the next generation is ready. It is whether the current one can stay healthy long enough to make the transition orderly.

That question starts being answered this week in a Bengaluru training facility, one fitness drill at a time.

*Sources: CricTracker, Inside Sport, The Times of India, SportsTak*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "hardik-pandya-rohit-sharma-fitness-clearance-bcci-coe-afghanistan-odi-nri",
        "image_url": img_url,
        "image_attribution": "Wikipedia" if img_src == "wikipedia" else ("Wikimedia Commons" if img_src == "commons" else ("Pexels" if img_src == "pexels" else None)),
        "sources": [
            {"name": "CricTracker", "url": "https://www.crictracker.com/cricket-news/ind-vs-afg-2026-hardik-pandya-asked-to-obtain-fitness-clearance-from-coe-ahead-of-odi-series/"},
            {"name": "Inside Sport", "url": "https://www.insidesport.in/cricket/hardik-pandya-to-report-at-bcci-coe-on-june-2-no-update-on-rohit-sharma-before-ind-vs-afg-odis/"},
            {"name": "SportsTak", "url": "https://www.thesportstak.com/cricket/hardik-pandya-to-spend-over-a-week-at-coe-ahead-of-afghanistan-odis-to-prove-fitness-report/"}
        ]
    }


# ── main ──

if __name__ == "__main__":
    articles = [article_india_nz_tour(), article_bahutule(), article_pandya_fitness()]
    success = 0
    for a in articles:
        if publish_article(a):
            success += 1
        time.sleep(1)
    print(f"\n{'='*50}")
    print(f"Published {success}/{len(articles)} articles")
