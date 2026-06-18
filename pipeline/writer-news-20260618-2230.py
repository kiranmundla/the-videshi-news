#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 22:30 UTC run.

Story: India never qualified for the men's FIFA World Cup, but the 2026
tournament — under way right now across the US, Canada and Mexico — has the
biggest-ever Indian-origin presence on the field: four players of Indian
descent representing four different nations. Qatar's Tahsin Mohammed Jamshid,
a 19-year-old Malayali born in Doha, is poised to become the first holder of
an Indian passport to play in a World Cup match. Alongside him: Nishan
Velupillay (Australia, Tamil roots), Sarpreet Singh (New Zealand, Punjabi
roots) and Samuel Moutoussamy (DR Congo, Tamil-Guadeloupean roots). Qatar
played Canada at BC Place in Vancouver on June 18.

Distinct from prior coverage: the recent feed is saturated with visa/
immigration, Iran-war oil, India-EU/UK/Canada trade deals, Modi's Paris/G7
trip and the Fed. There is NO sports/diaspora-identity story in the last
several days. This is a fresh human-interest + heritage angle tied to a live,
major event being hosted in North America where most of the US/Canada
diaspora lives.

Diaspora angle: the World Cup is being co-hosted in the US and Canada, home
to the largest Indian diaspora outside India; for the first time NRI families
can watch players who share their heritage at a home-soil World Cup.

Sources: Mint (Livemint), Times of India / 7Globe, myKhel, Tabla (Singapore),
Jagran Josh, Wikipedia (FIFA World Cup 2026 squad list).
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


def curl_download(url, out="/tmp/_videshi_hero_news2230.jpg"):
    try:
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=60,
        )
        if r.stdout.strip().endswith("200") and os.path.exists(out):
            with open(out, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print("  curl_download err", e)
    return None


def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=40)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        print(f"  \u274c Upload failed ({r.status_code}): {r.text[:200]}")
        return None
    except Exception as e:
        print("  upload err", e)
        return None


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, stream=True, allow_redirects=True)
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
            print(f"  \u2705 Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  \u2705 Inserted (raw): {r.text[:120]}")
        return data
    print(f"  \u274c Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def source_hero_image():
    # Nishan Velupillay (Australia, Tamil heritage) — one of the four
    # Indian-origin players at the 2026 World Cup. Tahsin Jamshid has no
    # Wikipedia photo, so we use Nishan, a verified Commons image of an
    # actual subject of the story (not generic stock).
    src = ("https://upload.wikimedia.org/wikipedia/commons/c/c9/"
           "Nishan_Velupillay_training_for_Melbourne_Victory_January_2023_%28cropped%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "nishan-velupillay-australia-world-cup-2026-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Indian-origin players at 2026 World Cup ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "four-indian-origin-players-fifa-world-cup-2026-tahsin-jamshid-nishan-velupillay-diaspora-20260618"

    body = """India has never played a single minute of men's football at a senior World Cup. And yet, as the 2026 tournament unfolds across stadiums in the United States, Canada and Mexico, the country's footballing diaspora is having its biggest moment on the sport's grandest stage. Four players of Indian origin \u2014 representing four different nations on three continents \u2014 are part of the expanded 48-team field. For a fan base that has spent decades watching from the outside, it is, as one columnist put it, a "massive cultural victory."

The most historic of the four is also the youngest. **Tahsin Mohammed Jamshid**, a 19-year-old winger born in Doha to Malayali parents from Kerala's Kannur district, has been named in Qatar's 26-man squad. If he steps onto the pitch, he will become the first holder of an **Indian passport** ever to appear in a World Cup match \u2014 a distinction that has electrified football circles in Kerala, a state that has long produced some of India's most passionate fans without ever having one of its own at the tournament.

## A Kerala dream, carried to Doha

Tahsin's father, Jamshid Thachankandy, played for the University of Calicut and later for a Kerala sub-junior side in 1985 before moving to Qatar in 1996 in search of better opportunities \u2014 the classic Gulf migration story of so many Malayali families. He carried his love for the game with him, and passed it to his son.

> "This is such a joyous moment for me personally. To see my son achieve the heights I dreamt of at his age is truly remarkable."

Tahsin came up through Qatar's celebrated Aspire Academy, broke into the national youth setup at Under-16 level, and now plays for Al Duhail, a powerhouse of the Qatar Stars League. He holds both an Indian passport and a Qatari "mission passport," a special document that allows foreign-born athletes to represent Qatar internationally. Senior Congress MP **Shashi Tharoor** publicly hailed his selection as a proud first for Indian-origin football.

## Three more carrying the flag

Tahsin is not alone. **Nishan Velupillay**, a 25-year-old winger with roots in Tamil Nadu, is part of Australia's squad after a breakout run with Melbourne Victory in the A-League. Known for his pace and directness, he is one of 17 first-time World Cup players in the Socceroos' camp and a source of pride for the Tamil community.

**Sarpreet Singh**, the New Zealand midfielder of Punjabi descent who once trained at Bayern Munich's academy, returns to a second World Cup with the All Whites. And **Samuel Moutoussamy**, a combative central midfielder for DR Congo, traces his Indian heritage through his father's South Indian Tamil family from the French Caribbean island of Guadeloupe \u2014 a reminder of just how far the Indian diaspora's threads run.

Together they span Qatar, Australia, New Zealand and DR Congo, and trace their roots to Kerala, Tamil Nadu and Punjab. It is the widest Indian-origin representation a single World Cup has ever seen.

## Why this World Cup, on this soil

The timing makes the story land differently for the diaspora. The 2026 tournament is being co-hosted by the United States and Canada, home to the largest population of overseas Indians anywhere in the world. For millions of NRI families across New Jersey, the Bay Area, Toronto and Houston, this is the first World Cup where they can buy tickets, drive to a stadium, and watch a player who shares their heritage compete against the planet's best \u2014 in their adopted home country.

India itself remains a long way from qualifying; the national team has never reached a senior men's World Cup, having famously withdrawn from the 1950 edition. But the success of these four players, all developed in elite systems abroad, has reopened a familiar conversation back home about why Indian talent so often has to leave to flourish \u2014 and what a more serious domestic pathway might one day produce.

## What's next

Qatar opened its campaign against Canada at BC Place in Vancouver, with the host nation taking an early lead through Cyle Larin. Whether or not Tahsin features in every match, his mere presence in the squad \u2014 and the simultaneous arrival of Velupillay, Singh and Moutoussamy on the world stage \u2014 marks a quiet milestone. For a country that has waited its entire footballing history for a World Cup moment, the diaspora has delivered one. And it is happening, fittingly, in the very cities where so much of that diaspora now lives."""

    return {
        "headline": "India Isn't at the World Cup. But Four Players of Indian Origin Are \u2014 on Home-Diaspora Soil.",
        "subheadline": "Qatar's 19-year-old Tahsin Jamshid is set to become the first Indian-passport holder to play a World Cup match, joined by Nishan Velupillay, Sarpreet Singh and Samuel Moutoussamy \u2014 the widest Indian-origin presence the tournament has ever seen, at a Cup co-hosted by the US and Canada.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Nishan Velupillay, the Tamil-heritage winger in Australia's 2026 World Cup squad, training for Melbourne Victory.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The 2026 World Cup is co-hosted by the US and Canada, home to the world's largest Indian diaspora, and for the first time those NRI families can watch four players who share their heritage \u2014 including the first-ever Indian-passport holder, Tahsin Jamshid \u2014 compete on home soil.",
        "sources": [
            "Mint (Livemint) \u2014 India may miss FIFA World Cup 2026, but these 4 Indian-origin players will be there",
            "The Times of India / 7Globe \u2014 Desi flex at FIFA World Cup: Kerala boy Tahsin Jamshid to play for Qatar",
            "myKhel \u2014 Who Is Tahsin Mohammed Jamshid? Indian-Malayali Set to Make FIFA World Cup History",
            "Tabla (Singapore) \u2014 Indian-Origin Footballers Nishan, Tahsin Set to Make History at World Cup",
            "Jagran Josh \u2014 Who Are The Four Indian-Origin Players Set To Feature At FIFA World Cup 2026?",
            "Wikipedia \u2014 FIFA World Cup 2026 Squad List (FIFA, 2 June 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    hl = len(art["headline"])
    print(f"  headline chars: {hl}")
    sub = len(art["subheadline"])
    print(f"  subheadline chars: {sub}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    elif len(art["headline"]) > 200:
        print("  \u274c headline too long, aborting")
    else:
        insert_article(art)
