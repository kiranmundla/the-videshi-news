#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-19 02:30 UTC run.

Story: The Hindu American Foundation (HAF) submitted formal comments (dated
June 9, 2026; reported June 17) to California's Commission on the State of
Hate, urging it to formally recognize a documented surge in anti-Hindu bias
and to include Hindu Americans in statewide anti-hate initiatives. HAF cited
the state's own CA vs Hate hotline data showing anti-Hindu incidents were the
SECOND most frequent form of religiously motivated hate in California (23% of
reported religious bias cases), plus a pattern of temple desecrations
(Chino Hills, Sacramento/Rancho Cordova water-line sabotage, Newark + Hayward
Bay Area spree), targeted assaults in Santa Clara County, and a 115% reported
rise in anti-Indian slurs online between 2023-2025.

Distinct from prior coverage: the recent news feed is saturated with
visa/immigration, Iran-war oil/markets, India-EU/UK/Canada trade, Modi's
G7/Paris trip, the FIFA World Cup diaspora angle, and (00:45) the Anil Menon
space story. There IS a diaspora-safety lane in the feed (Frisco flag, Oman
seafarers) but no story on the California anti-Hindu hate data / HAF policy
push — and this one is heavily Bay Area-relevant (Newark, Hayward, Santa
Clara, Fremont), which matters for The Videshi's large NorCal readership.

Diaspora angle: California is home to one of the largest Indian-American
populations in the US; the state's own data now ranks anti-Hindu bias as its
second-most-common religious hate category, and the named incidents cluster
in the Bay Area where many NRI families live and worship.

Sources: IANS (June 17), Hindu American Foundation public comments (June 9),
California Civil Rights Department CA vs Hate data (as cited by HAF),
Rutgers-NCRI report (as cited).
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env(os.path.expanduser("~/.env.supabase"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Hero image already downloaded from Wikimedia Commons (BAPS Mandir Chino
# Hills — the largest Hindu temple in California and one of the named
# desecration sites), resized and uploaded to Supabase storage. Verified
# HTTP 200, image/jpeg, ~491KB.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-haf-california-hindu-hate-202606190230.jpg")


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20,
                         stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(8000)
        r.close()
        return r.status_code == 200 and "image" in ct and len(chunk) > 5000
    except Exception as e:
        print("  validate err", e)
        return False


def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB, json=article, timeout=25,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  Inserted (raw): {r.text[:120]}")
        return data
    print(f"  Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def article():
    print("\n=== Article: HAF urges California to recognize anti-Hindu hate ===")

    slug = ("haf-california-state-of-hate-commission-anti-hindu-bias-23-percent-"
            "bay-area-temple-vandalism-20260619")

    body = """California's own hate-tracking system now ranks bias against Hindus as the **second most common form of religiously motivated hate** in the state \u2014 and a national advocacy group is pressing the state to say so out loud. In formal comments submitted to California's Commission on the State of Hate, the **Hindu American Foundation (HAF)** has urged the panel to formally recognize what it calls a dangerous spike in anti-Hindu bias and to write Hindu Americans into the state's anti-hate strategy.

The submission, dated June 9 and reported this week, leans on the state's own numbers. According to data from the **CA vs Hate** hotline cited by HAF, anti-Hindu incidents accounted for a striking **23% of all reported religious bias cases** in California \u2014 trailing only one other category. For a community that often sees its experiences folded silently into broader "South Asian" or "Asian American" tallies, the figure is a rare, specific measure of the problem.

## A pattern, not isolated incidents

HAF's letter to Commission Chair Brian Levin frames the trend less as scattered vandalism and more as a systematic campaign against Hindu houses of worship. It points to a string of attacks, several of them clustered in regions with large Indian-American populations.

The **BAPS Shri Swaminarayan Mandir in Chino Hills** \u2014 the largest Hindu temple in California \u2014 was defaced with vulgarities and anti-Hindu, anti-Indian slogans across its marble signage and walkways, causing more than $15,000 in damage. In the Sacramento area, the BAPS Mandir in Rancho Cordova was hit in an overnight raid in which perpetrators not only defaced the marquee but **cut and damaged the property's primary water lines**, an escalation HAF describes as malicious infrastructure sabotage now investigated as a hate crime.

The Bay Area has seen its own spree. Temples across Northern California, including the **Newark Shri Swaminarayan Temple** and **Hayward's Vijay's Sherawali Temple**, have been repeatedly defaced with politically charged anti-Hindu graffiti meant to intimidate worshipers.

## When the target is a person

The intimidation has not stopped at buildings. HAF cites a series of **targeted assaults in Santa Clara County**, where an attacker sought out and physically assaulted elderly Hindu women wearing traditional sarees, ripping away their jewelry in what prosecutors are treating as bias-motivated violence. In another incident, a Hindu man was assaulted and subjected to anti-Hindu slurs at a Taco Bell in **Fremont**.

The foundation argues that the true scale is larger than any dataset shows. Many families, it says, hesitate to report incidents because of language barriers, unfamiliarity with the legal system, or fear of retaliation \u2014 meaning even California's elevated numbers capture only a fraction of the harassment the community faces day to day.

## From the timeline to the street

HAF also draws a line from online vitriol to physical danger. The group points to a reported **115% rise in anti-Indian slurs online between 2023 and 2025**, and to findings from Stop AAPI Hate that a large share of anti-Asian slurs recorded over a recent winter were aimed at South Asians, much of it tied to anti-Indian rhetoric around H-1B visas. A 2023 Rutgers\u2013Network Contagion Research Institute study it cites found anti-Hindu content "exploding across entire web communities," with coded slurs used to evade content moderation and, in some cases, state-linked troll networks amplifying the narratives.

The foundation's central warning is that this digital hostility functions as an early indicator of real-world targeting \u2014 the same pattern researchers have documented with other forms of bias.

## What HAF is asking for

The submission lays out five specific asks of the Commission and the Civil Rights Department: improve and translate reporting mechanisms so more Hindu Californians use the CA vs Hate system; disaggregate and publish anti-Hindu incident data so the scope is clear; expand state security grants for vulnerable temples and community centers; publicly condemn the systemic nature of anti-Hindu bias; and use the Commission's advisory role to steer state resources toward the problem.

"Hindu Americans are an integral, vibrant part of the California tapestry," HAF Managing Director **Samir Kalra** wrote. "Freedom of religion and the right to practice without fear of violence are foundational. We respectfully urge this Commission to formally recognize this dangerous spike in anti-Hindu bias."

## Why it matters to NRIs

California is home to one of the largest Indian-American communities in the United States, and the incidents HAF names are not abstract for diaspora families \u2014 Newark, Hayward, Fremont, and Santa Clara County are the very towns where many NRIs live, raise children, and gather at temples on weekends. The state's own data putting anti-Hindu bias second among religious hate categories turns a feeling many in the community have voiced into a documented trend.

For the diaspora, the policy fight is about whether that trend gets named and counted. Recognition by a state commission would unlock targeted security funding, better-tracked data, and outreach in community languages \u2014 the practical tools that decide whether a temple can afford cameras and whether a frightened grandmother feels safe walking into a police station to file a report."""

    return {
        "headline": "California's Own Data Ranks Anti-Hindu Hate Second. A Diaspora Group Wants the State to Say So.",
        "subheadline": "The Hindu American Foundation has urged California's Commission on the State of Hate to formally recognize a documented surge in anti-Hindu bias \u2014 23% of all reported religious hate cases \u2014 citing Bay Area temple vandalism, water-line sabotage in Sacramento, and assaults on elderly women in Santa Clara County.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "The BAPS Shri Swaminarayan Mandir in Chino Hills, the largest Hindu temple in California, named by HAF among recently desecrated sites.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "California holds one of the largest Indian-American populations in the US, and the temple vandalism and assaults HAF cites cluster in Bay Area towns like Newark, Hayward, Fremont and Santa Clara County where many NRI families live and worship.",
        "sources": [
            "IANS \u2014 Advocacy group urges California's commission to recognise rise in anti-Hindu hate (June 17, 2026)",
            "Hindu American Foundation \u2014 Public comments to the California Commission on the State of Hate (June 9, 2026)",
            "California Civil Rights Department \u2014 CA vs Hate hotline data (as cited by HAF)",
            "Rutgers\u2013Network Contagion Research Institute \u2014 'Anti-Hindu Disinformation' report (2023, as cited)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    print(f"  headline chars: {len(art['headline'])}")
    print(f"  subheadline chars: {len(art['subheadline'])}")
    if wc < 400:
        print("  word count below floor, aborting")
    elif len(art["headline"]) > 200:
        print("  headline too long, aborting")
    elif not validate_get(art["image_url"]):
        print("  hero image failed validation, aborting")
    else:
        insert_article(art)
