#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 14:30 UTC run.

Story: A viral video from Frisco, Texas showed a man (Clayton Walker) tearing
the Indian tricolour outside Frisco City Hall during an anti-immigration
protest as the crowd cheered and shouted anti-India slogans. On June 16, six
Indian-American members of Congress — Raja Krishnamoorthi, Ami Bera, Pramila
Jayapal, Ro Khanna, Shri Thanedar and Suhas Subramanyam — issued a joint
statement condemning the act and the surrounding "anti-India rhetoric,"
while defending free-speech rights. The incident has reignited debate over
demographic change in North Texas suburbs where the Indian-American
population has surged on the back of tech and H-1B migration.
(IANS, Livemint, India-West, South Asian Herald, IndiaPost — Jun 6-16, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1430.jpg"
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
    # Frisco City Hall — the actual building outside which the protest occurred.
    # Permanent Wikimedia Commons photo.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/"
           "Frisco%2C_Texas_-_City_Hall.jpg/1280px-Frisco%2C_Texas_-_City_Hall.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "frisco-city-hall-indian-flag-protest-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Frisco flag-tearing & lawmakers' condemnation ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "frisco-texas-indian-flag-torn-protest-indian-american-lawmakers-condemn-xenophobia-20260617"

    body = """A cigarette in his mouth, a man steps forward outside Frisco City Hall, grabs an Indian tricolour and rips it apart. Around him, an anti-immigration crowd cheers — "yeah," "let's go" — while voices chant against India. The few seconds of footage, filmed in one of the fastest-growing suburbs of Dallas, have travelled far beyond Texas, and this week they reached the floor of the United States Congress.

On June 16, six Indian-American members of the US House of Representatives issued a rare joint statement condemning the act and the "anti-India rhetoric" that surrounded it. For a diaspora that has spent two decades building a quiet, prosperous foothold in North Texas, the episode has become a flashpoint — a test of how secure that foothold really is.

## What happened in Frisco

The video, which spread across social media in early June, shows a man identified as Clayton Walker tearing the Indian flag in front of Frisco City Hall during an immigration-related protest. As he rips the cloth, people in the crowd are heard shouting anti-India slogans and cheering him on. The clip was captioned with profanity directed at India and framed as anger against "the Indian immigration invasion in north Dallas."

Frisco is no random backdrop. Once a sleepy farming town, it has become a magnet for technology firms and the engineers who staff them. Its Asian population — overwhelmingly Indian — has climbed to roughly a third of residents, driven by corporate relocations and H-1B visa migration. That growth has brought prosperity, new temples and Indian grocery aisles, but also friction over housing costs, traffic, school crowding and what some longtime residents frame as rapid cultural change. In recent months, Frisco city council meetings have drawn speakers warning of an "Indian takeover," language local leaders have pushed back on as divisive and misleading.

## The Congressional response

The joint statement came from Representatives Raja Krishnamoorthi of Illinois, Ami Bera of California, Pramila Jayapal of Washington, Ro Khanna of California, Shri Thanedar of Michigan and Suhas Subramanyam of Virginia — the core of the Indian-American caucus on Capitol Hill.

"We strongly support the constitutional right to freedom of expression for all Americans," the lawmakers wrote. "At the same time, we condemn the tearing of an Indian flag outside Frisco City Hall alongside hateful anti-India rhetoric, which continues to fuel anti-Indian violence and xenophobia. Acts of hate and intimidation targeting any community are unacceptable and have no place in our country."

The members were careful to draw a line between protected political speech and intimidation. The incident, they said, "went beyond political expression" and had raised concerns among Indian Americans "about their safety and acceptance in the country." They closed by reaffirming solidarity: "Everyone deserves to live with dignity and safety, free from fear, harassment, and discrimination."

## A contested free-speech defence

Walker has defended his actions as protected speech. "All I did was exhibit my right to freedom of speech as an American. Now I'm getting death threats from Indians," he wrote online after the video went viral, saying he had received threatening messages.

That framing — provocative protest versus targeted hostility — is exactly the fault line the episode has exposed. Many Indian Americans who reacted online argued that disagreements over immigration policy should not be aimed at an entire community, and pointed to the economic contributions of Indian immigrants. Others insisted the debate should stay focused on policy rather than ethnicity. The result is a familiar, uneasy split: a constitutionally protected act that nonetheless lands as a threat for the people it targets.

## Why the diaspora is watching

For the Indian-American community, the Frisco video is not an isolated viral moment but the latest entry in a lengthening list. It arrives amid a broader climate of unease — surveys this year have documented widespread perceptions of discrimination and exposure to online and offline harassment among Indian Americans, even as the community remains one of the most economically successful in the country.

The discomfort is sharpest in the very suburbs that symbolise the diaspora's success. Places like Frisco, Plano and Irving were supposed to be the proof that Indian families could arrive, prosper and belong. The flag-tearing — and the cheering crowd behind it — has unsettled that assumption, and the swift, unified response from Indian-American lawmakers signals how seriously the community's elected representatives are treating the trend. For NRIs weighing where to raise children and put down roots, the question Frisco raises is not about one man with a lighter and a torn flag, but about whether the welcome they counted on still holds."""

    return {
        "headline": "A Man Tore the Indian Flag Outside a Texas City Hall. Six Indian-American Lawmakers Just Answered.",
        "subheadline": "After a viral video showed the tricolour ripped apart at an anti-immigration protest in Frisco, six members of Congress condemned the act and the 'anti-India rhetoric' around it — exposing the unease beneath one of the diaspora's biggest success stories.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Frisco City Hall in Texas, outside which a demonstrator tore an Indian flag during an anti-immigration protest.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The incident and the Congressional response speak directly to Indian-American families in fast-growing tech suburbs like Frisco, raising questions about safety, belonging and rising xenophobia just as the diaspora's numbers surge.",
        "sources": [
            "IANS \u2014 Indian American lawmakers condemn anti-India act in Texas (June 16, 2026)",
            "Livemint \u2014 Texas man tears Indian flag as anti-immigration crowd cheers; viral video sparks backlash (June 2026)",
            "India-West \u2014 Indian Flag Torn at Texas Protest Sparks Online Backlash (June 2026)",
            "South Asian Herald \u2014 Indian American Lawmakers Condemn Indian Flag Tearing at Texas Protest (June 16, 2026)",
            "IndiaPost \u2014 Indian American Lawmakers Condemn Anti-India Act In Texas (June 16, 2026)",
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
