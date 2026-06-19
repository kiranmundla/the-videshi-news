#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-19 00:30 UTC run.

Story: Anil Menon, the first Indian-American NASA astronaut assigned to a
long-duration ISS mission, is now four weeks from launch. Soyuz MS-29 is
targeted for Tuesday, July 14, 2026 from Baikonur, carrying Menon and
Roscosmos cosmonauts Pyotr Dubrov and Anna Kikina for an eight-month
Expedition 74/75 stay. Menon — born in Minneapolis to an Indian father and
Ukrainian mother, Harvard/Stanford-trained ER physician, SpaceX's first
flight surgeon, USSF colonel — is the third person of Indian descent to reach
orbit after Kalpana Chawla and (this month) Shubhanshu Shukla.

Distinct from prior coverage: the recent news feed is saturated with
visa/immigration, Iran-war oil/markets, India-EU/UK/Canada trade, Modi's
G7/Paris trip, and the FIFA World Cup diaspora angle (published 22:45). There
is NO space/science story in the feed. This is a fresh diaspora-pride +
science angle tied to a concrete, imminent date.

Diaspora angle: an Indian-American raised in the US Midwest is about to carry
the community's story to orbit, weeks after India's own Shubhanshu Shukla
flew — a back-to-back moment of Indian-origin presence in human spaceflight.

Sources: NASA (press releases + prelaunch advisory), Livemint, India-West,
Outlook Business, Wikipedia (Anil Menon).
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


def curl_download(url, out="/tmp/_videshi_hero_news0030.jpg"):
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
    # Anil Menon — official NASA portrait via Wikipedia/Wikimedia Commons.
    # Use originalimage.source for full-resolution (no non-standard thumb size).
    src = ("https://upload.wikimedia.org/wikipedia/commons/5/59/"
           "NASA_Astronaut_Anil_Menon_%28jsc2024e013690_alt%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "anil-menon-nasa-astronaut-soyuz-ms29-20260619.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Anil Menon — first Indian-American NASA astronaut to ISS ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "anil-menon-first-indian-american-nasa-astronaut-soyuz-ms29-iss-july-2026-diaspora-20260619"

    body = """Weeks after India watched one of its own pilot a spacecraft to the International Space Station, the Indian diaspora is preparing for a second milestone in orbit \u2014 this one carried by an American son of the community. **Anil Menon**, a NASA astronaut born and raised in Minneapolis to an Indian father and a Ukrainian mother, is now roughly four weeks from his first spaceflight. NASA has confirmed the **Soyuz MS-29** mission is targeted to launch on **Tuesday, July 14**, lifting Menon and two Roscosmos cosmonauts from the Baikonur Cosmodrome in Kazakhstan for an eight-month stay aboard the orbiting laboratory.

When he reaches the station, Menon will join a short and remarkable list: he will be among the few people of Indian descent ever to live and work in space, and the first Indian-American assigned by NASA to a long-duration station expedition.

## A doctor, an engineer, and a colonel

Menon's resume reads like three careers compressed into one. He earned a bachelor's degree in neurobiology from Harvard, then a master's in mechanical engineering and a medical degree from Stanford. He trained in both emergency and aerospace medicine, and to this day still treats patients in the emergency room at Memorial Hermann's Texas Medical Center in Houston while teaching residents at the University of Texas.

Before NASA selected him for its astronaut corps in 2021, Menon had already built a singular career at the intersection of medicine and spaceflight. He served as a NASA flight surgeon beginning in 2014, supporting multiple Soyuz crews, and then became **SpaceX's first flight surgeon** \u2014 helping launch the crewed Dragon spacecraft on NASA's Demo-2 mission in 2020 and standing up the company's entire medical operation for human spaceflight. He is also a colonel in the United States Space Force. He graduated with NASA's 23rd astronaut class in 2024.

## The mission

The Soyuz MS-29 flight will carry Menon alongside veteran Roscosmos cosmonauts **Pyotr Dubrov** and **Anna Kikina**. After launch from Baikonur, the trio will spend approximately eight months aboard the ISS as part of Expeditions 74 and 75, with Menon serving as a flight engineer.

During the expedition, Menon is set to conduct scientific investigations and technology demonstrations designed to prepare humans for longer journeys beyond low Earth orbit. That research feeds directly into NASA's Artemis program, which aims to return astronauts to the Moon and, eventually, send crews to Mars. NASA originally announced Menon's assignment last year, with the launch date refined to mid-July as the agency and its partners updated the 2026 station flight schedule.

## Back-to-back moments for the diaspora

The timing gives the story unusual resonance. Just this month, **Shubhanshu Shukla**, an Indian Air Force officer, became the first Indian to reach the ISS as pilot of the Axiom-4 mission \u2014 a flight India's space agency called a "defining chapter" in its program. Now, only weeks later, an Indian-American is preparing to follow.

Menon is the third person of Indian heritage to fly to orbit. He follows **Rakesh Sharma**, who flew aboard a Soviet mission in 1984, and **Kalpana Chawla**, the India-born NASA astronaut who flew two shuttle missions before her death aboard Columbia in 2003. For a community that has long pointed to Chawla's story with both pride and grief, Menon's flight lands as a hopeful new chapter.

## Why it matters to NRIs

For the millions of Indian-Americans who have built lives in cities like Houston, the Bay Area, New Jersey and Menon's own Minneapolis, the launch is more than a NASA headline. It is a reminder that the diaspora's children are now woven into the highest reaches of American science and exploration \u2014 not as outsiders, but as the people NASA trusts to fly its missions.

Menon has spoken about wanting his journey to inspire the next generation, much as Sharma and Chawla once inspired him. His path \u2014 from emergency rooms to SpaceX launchpads to the Space Force, and now to orbit \u2014 traces the kind of multidisciplinary, immigrant-rooted ambition that has come to define the Indian-American story in the United States.

## What's next

NASA and Roscosmos will continue prelaunch preparations through early July, with the agency expected to host launch coverage on its public channels ahead of the July 14 liftoff. If the schedule holds, Menon will be in orbit by mid-summer and aboard the station into early 2027 \u2014 carrying, like Shukla before him, the quiet weight of a community watching from the ground."""

    return {
        "headline": "An American Son of the Indian Diaspora Is Weeks From Orbit. Meet NASA's Anil Menon.",
        "subheadline": "Soyuz MS-29 is targeted for July 14, carrying the Minneapolis-born ER doctor, engineer and Space Force colonel to the ISS for eight months \u2014 the first Indian-American on a long-duration NASA station mission, just weeks after India's Shubhanshu Shukla made history.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "science",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "NASA astronaut Anil Menon, assigned as flight engineer for the Soyuz MS-29 / Expedition 74-75 mission to the International Space Station.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "An Indian-American raised in the US Midwest is about to carry the community's story to orbit just weeks after India's own Shubhanshu Shukla flew, marking a back-to-back moment of Indian-origin presence in human spaceflight that resonates across NRI communities in the US.",
        "sources": [
            "NASA \u2014 NASA Assigns Astronaut Anil Menon to First Space Station Mission (nasa.gov)",
            "NASA \u2014 NASA Astronaut Anil Menon to Discuss Upcoming Launch, Mission; Soyuz MS-29 targeted July 14 (nasa.gov)",
            "NASA \u2014 NASA, Partners Update International Space Station 2026 Flight Plan (nasa.gov)",
            "Livemint \u2014 Who is Anil Menon? The NASA astronaut set for his first ISS mission in 2026",
            "India-West \u2014 NASA Announces It Will Send Dr. Anil Menon On Debut Spaceflight In 2026",
            "Wikipedia \u2014 Anil Menon (astronaut)",
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
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    elif len(art["headline"]) > 200:
        print("  \u274c headline too long, aborting")
    else:
        insert_article(art)
