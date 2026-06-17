#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 10:30 UTC run.

Story: The US naval blockade of Iran-linked shipping has now killed three
Indian seafarers (Aditya Sharma, Shivanand Chaurasiya, Patnala Suresh) aboard
the Palau-flagged MT Settebello off Oman on June 9-10, and struck at least
three Indian-crewed tankers in a single week. India has lodged two formal
protests, summoned the US charge d'affaires, and Jaishankar told Rubio the
lethal actions are "not justified." Opposition figures (Tharoor) decry the
lack of US condolence. With 300,000+ Indian seafarers crewing the world's
fleets — ~18,000 in the Middle East — this is a direct diaspora-safety story.
(Reuters, The Indian Eye, Madhyamam, Inshorts — Jun 12-16, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    """Wikimedia rate-limits Python requests (429) but serves curl fine."""
    try:
        out = "/tmp/_videshi_hero.jpg"
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=40,
        )
        if r.stdout.strip().endswith("200") and os.path.exists(out):
            with open(out, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print("  curl_download err", e)
    return None


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


def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
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
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15, stream=True, allow_redirects=True)
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
        headers=HEADERS_SB, json=article, timeout=20,
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
    # Clean, accurate Commons photo of a crude oil tanker at sea.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/"
           "Crude_oil_tanker_Eagle_San_Diego.jpg/1280px-Crude_oil_tanker_Eagle_San_Diego.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "indian-seafarers-oman-tanker-strikes-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: US strikes kill Indian seafarers off Oman ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "us-blockade-strikes-kill-three-indian-seafarers-oman-settebello-diaspora-safety-20260617"

    body = """They were not soldiers. Aditya Sharma was a deck cadet, barely starting his career at sea. Shivanand Chaurasiya was an engine fitter who had been at sea about nine months and had told his father earlier in the week that everything was fine. Patnala Suresh was a chief engineer. All three were Indian. All three are now dead, killed when an American aircraft fired precision munitions into the engine room of the oil tanker they crewed off the coast of Oman.

The strike on the Palau-flagged MT Settebello on the night of June 9 is the first deadly incident in a US naval blockade that has steadily tightened around the Strait of Hormuz since April 13. And it has thrust a community that rarely makes headlines — India's vast population of merchant seafarers — into the centre of a diplomatic rupture between New Delhi and Washington.

## A blockade that hit Indian crews three times in a week

US Central Command says it disabled the Settebello after the vessel "violated the ongoing blockade by attempting to transport oil from Iran," and that its forces fired only after the crew "repeatedly failed to comply." The Omani Navy responded to a distress call and rescued 21 of the 24 Indian crew members; three did not survive. US officials later told American media the military had issued nearly 60 verbal warnings and conducted eight aerial shows of force before firing.

The Settebello was not an isolated case. Within the same week US forces struck at least three tankers carrying Indian crews. On Thursday a US jet fired two Hellfire missiles into the engine room of the tanker Jalveer off Oman; its 20 crew members were reported safe. Days earlier the Marivex was disabled by precision munitions. By Washington's own count the blockade has now disabled nine non-compliant vessels, redirected more than 130 others, and allowed 42 humanitarian vessels to pass.

## India lodges rare back-to-back protests

The deaths triggered an unusually sharp Indian response. The Ministry of External Affairs summoned the US charge d'affaires in New Delhi to convey its "deepest concerns," then took the rare step of lodging a second protest days later over "the use of lethal and deadly force against civilian shipping." Spokesperson Randhir Jaiswal was blunt: "These attacks must cease and end."

External Affairs Minister S. Jaishankar raised the matter directly with US Secretary of State Marco Rubio, telling him that "such lethal actions against commercial shipping are not justified." Washington's reply offered little comfort: the State Department reiterated that violations of the blockade would "not be tolerated" and that all commercial vessels must comply immediately with US instructions — with no expression of regret for the Indian lives lost.

That silence drew fire at home. Congress MP Shashi Tharoor said he was "deeply shocked" that the American statement carried no condolence, asking, "How can a friend and strategic partner be so deeply insensitive?" He pressed a question many in the maritime community are asking: "Why couldn't a non-compliant commercial vessel have been stopped using other, non-lethal means? Is it not possible to disable a ship's propulsion or steering without firing missiles targeted to kill civilian crew members?" Opposition parties urged Prime Minister Narendra Modi to raise the deaths with President Trump on the sidelines of the G7 summit in Evian.

## Why this is a diaspora story

India supplies the world's ships with its people. More than 300,000 Indian seafarers crew vessels across the global merchant fleet, and roughly 18,000 of them work in Middle Eastern waters, according to the shipping ministry. They are the invisible diaspora — Indians who spend most of the year far from home, sending remittances back to villages in Himachal Pradesh, Uttar Pradesh and Andhra Pradesh, the home states of the three men killed.

The conflict in the Gulf has turned their workplaces into a war zone. The Directorate General of Shipping has ordered all Indian seafarers on Indian and foreign-flagged vessels transiting the region to "exercise the highest degree of caution and vigilance," and the government has told its agencies to stay ready for any contingency. The crisis has also exposed how exposed these workers can be: the body of a separate Indian sailor who died of medical complications aboard a tanker docked at Oman reportedly remained onboard for days without proper refrigeration, with crewmates resorting to cold water bottles to slow decomposition.

For NRI families, the message is sobering. A loved one need not be a combatant to be caught in a geopolitical crossfire — only employed on a ship in the wrong stretch of water at the wrong time. As India presses Washington for accountability and safe passage, the fate of its seafarers has become a test of just how much weight the "strategic partnership" carries when Indian lives are on the line."""

    return {
        "headline": "Three Indian Seafarers Are Dead Off Oman. India's Invisible Diaspora Just Became a Diplomatic Crisis.",
        "subheadline": "A US blockade of Iran-linked shipping has struck at least three Indian-crewed tankers in a week and killed three sailors, forcing New Delhi into rare back-to-back protests as 300,000 Indian seafarers face a war zone at work.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "A crude oil tanker at sea; US strikes enforcing a blockade off Oman have killed three Indian seafarers and hit several Indian-crewed vessels.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "More than 300,000 Indian seafarers crew the world's merchant fleet and about 18,000 work in Middle Eastern waters, making the US strikes off Oman a direct safety and accountability crisis for working-class Indian diaspora families.",
        "sources": [
            "Reuters \u2014 India demands end to US attacks on ships after three sailors killed (June 12, 2026)",
            "Reuters \u2014 US confirms third strike on Indian-crewed tankers this week (June 12, 2026)",
            "Reuters \u2014 Indian sailor dies from medical complications aboard tanker in Oman (June 14, 2026)",
            "The Indian Eye \u2014 Three Indians killed by US missile attack on oil tanker near Oman (June 16, 2026)",
            "Madhyamam \u2014 Shashi Tharoor criticises US response after death of three Indians off Oman coast (June 15, 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
