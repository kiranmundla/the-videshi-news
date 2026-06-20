#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-20 06:30 UTC run.

Story: On Friday, June 19, 2026, Bangladesh's Hindu minority staged a large
torchlight procession through central Dhaka — from Shahbagh to the National
Press Club — chanting "Jai Shri Ram," after a mob allegedly desecrated a statue
of Lord Ram by placing a shoe on it and after threats from radical Islamist
groups halted construction of an 81-foot Ram statue at Palashbari in Gaibandha
district. Hindu student bodies (Bangladesh Hindu Buddhist Christian Unity
Council, Minority Rights Movement) issued a 72-hour ultimatum, are submitting a
memorandum to the Ministry of Religious Affairs, and the National Committee for
Puja Celebrations called a nationwide protest for Saturday. The unrest sits
inside a longer surge in anti-minority violence since the August 2024 fall of
Sheikh Hasina (2,000+ incidents, 61 killings documented by the Unity Council)
under the Muhammad Yunus interim government, ahead of a Feb. 12 national
election. India's MEA has repeatedly pressed Dhaka to protect minorities; US
lawmakers and the State Department have voiced concern.

Distinct from prior coverage: the feed has no article on the Bangladesh Hindu
minority, the Dhaka protest, the Gaibandha Ram statue, or the diaspora's
response — this is a fresh, ongoing story.

Diaspora angle: the Bangladeshi-Hindu and broader Indian diaspora in the US/UK/
Canada has driven much of the international pressure (congressional statements,
ISKCON advocacy, protests), and many NRIs have family ties across the
India–Bangladesh border whose safety is directly at stake.

Sources: ANI / Daily Prabhat (June 19, 2026 torchlight procession); Devdiscourse
/ The CSR Journal (student protest, 72-hour ultimatum, Gaibandha statue); AP via
Audacy (Hindu minority violence data, election context); ANI / India Tribune
(MEA statements); The Indian Eye (US congressional + State Dept concern).
"""

import os
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

# Hero: a Durga Puja procession by the Hindu minority of Bangladesh (Dhaka),
# Wikimedia Commons, CC BY 2.0, Stefan Krasowski. Downloaded and re-hosted on
# Supabase storage for permanence. Verified HTTP 200, image/jpeg, ~377KB.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-bangladesh-hindu-protest-lord-ram-20260620.jpg")


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
    print("\n=== Article: Dhaka Hindu protest over Lord Ram ===")

    slug = ("bangladesh-hindu-minority-dhaka-protest-lord-ram-statue-"
            "gaibandha-jai-shri-ram-20260620")

    body = """The slogans echoing off the buildings around Dhaka's Shahbagh intersection on Friday evening were not the ones Bangladesh's interim government wanted the world to hear. As torches lit the dusk, thousands of members of the country's Hindu minority marched from Shahbagh to the National Press Club chanting "Jai Shri Ram" \u2014 a public, defiant assertion of faith from a community that says it has rarely felt more unsafe.

The immediate trigger was an act of desecration. Protesters say a violent mob recently placed a shoe on a statue of Lord Ram \u2014 an unambiguous insult in Hindu practice \u2014 and that no one has been arrested despite a complaint being filed. The deeper grievance is a stalled monument: construction of what was meant to be Bangladesh's largest statue of Lord Ram, an 81-foot figure at the Sri Sri Radha Govinda Temple in Palashbari, Gaibandha district, was halted after organisers said they faced threats and pressure from radical Islamist groups.

## A 72-hour ultimatum, then the streets

The protest had been telegraphed days in advance. After an earlier torchlight procession at Dhaka University, Hindu student groups gave the government a 72-hour deadline to arrest those behind the desecration. When the deadline passed with no response, organisers moved to Shahbagh on Friday afternoon, with students and minority organisations gathering one after another.

"Our worshipped God, Lord Ram, has been insulted. It is a matter of deep pain," Novelty Roy Uday, a convener with the Bangladesh Student Unity Council's Dhaka Metropolitan South unit \u2014 part of the Bangladesh Hindu Buddhist Christian Unity Council \u2014 told news agency ANI. His warning was bleaker still: "Whatever happens in Bangladesh, if it continues over the next 10 years, I'm afraid the Hindu community will vanish."

Organisers say they will now submit a memorandum to the Ministry of Religious Affairs and seek a meeting with the prime minister, and the National Committee for Puja Celebrations has called a nationwide protest for Saturday. Some demonstrators went further, vowing to build a Ram temple in each of Bangladesh's 64 districts.

## A minority under pressure

Friday's march did not happen in a vacuum. Hindus make up roughly 8% of Bangladesh's 170 million people, and rights groups say attacks on the community have surged since the fall of Prime Minister Sheikh Hasina in the August 2024 uprising. The Bangladesh Hindu Buddhist Christian Unity Council says it has documented more than 2,000 incidents of communal violence since then, including at least 61 killings, 95 attacks on places of worship, and dozens of assaults on women.

The fear is sharpening as the country approaches a national election scheduled for February 12. "No one feels safe anymore," Dhaka-based Hindu rights activist Ranjan Karmaker told the Associated Press earlier this year. Critics accuse the interim administration led by Nobel laureate Muhammad Yunus of routinely dismissing or downplaying such violence as ordinary personal or political disputes \u2014 a characterisation minority leaders reject.

## India and Washington are watching

The unrest has long since spilled across borders. India's Ministry of External Affairs has repeatedly and publicly pressed Dhaka to protect its minorities, accusing Bangladesh of failing to acknowledge a "disturbing pattern of recurring attacks" on Hindus and warning that the violence "cannot be dismissed only as media exaggerations." Bangladesh has countered that India is stoking anti-Bangladesh sentiment. The dispute has already poisoned visa services, diplomatic missions and even cricket between the two neighbours.

The pressure is not only from New Delhi. US lawmakers have urged the interim government to act, and the State Department has called the situation "worrisome," saying it wants a Bangladesh where "the human rights of every person are protected." ISKCON, the global Hindu organisation with deep roots in Bengal, has been at the centre of the controversy since the arrest of monk Chinmoy Krishna Das in late 2024.

## Why it matters to NRIs

For the diaspora, this is not a distant story. Much of the international pressure on Dhaka has come from the diaspora itself \u2014 congressional statements driven by Indian-American and Bangladeshi-Hindu constituents, ISKCON's worldwide advocacy network, and protests outside Bangladeshi missions in Western capitals. Many NRIs trace their own families to the towns and villages of East Bengal, and have relatives still living as a vulnerable minority on the other side of the line drawn in 1947.

The community abroad has money, votes and a megaphone, and it is increasingly willing to use all three on behalf of co-religionists overseas. As Bangladesh heads into a fraught election and its Hindus take to the streets demanding basic protection, the diaspora's response \u2014 in Washington, London, Toronto and at the gates of Bangladesh's embassies \u2014 may shape how much the world is willing to look away."""

    return {
        "headline": "Dhaka's Hindus March by Torchlight, Chanting 'Jai Shri Ram,' After a Shoe Is Placed on Lord Ram",
        "subheadline": "A halted 81-foot Ram statue and a desecrated idol have pushed Bangladesh's anxious Hindu minority into the streets \u2014 and pulled India, Washington and the diaspora into the fight over their safety.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "A Durga Puja procession by members of Bangladesh's Hindu minority community in Dhaka.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Much of the international pressure on Dhaka over attacks on Hindus comes from the diaspora itself, and many NRIs have family roots and relatives across the India-Bangladesh border whose safety is directly at stake.",
        "sources": [
            "ANI / Daily Prabhat \u2014 'Hindus in Bangladesh hold torchlight protest against alleged disrespect to Lord Ram' (June 19, 2026)",
            "Devdiscourse / The CSR Journal \u2014 'Bangladeshi Hindu students to stage massive protest against alleged insult to Lord Ram' (72-hour ultimatum, Gaibandha statue, June 2026)",
            "Associated Press \u2014 'Bangladesh's Hindu minority in fear as attacks rise and a national election nears' (violence data, Yunus government, Feb 2026)",
            "ANI / India Tribune \u2014 'India concerned over surge in extremist rhetoric in Bangladesh, calls on Yunus govt to protect minorities' (MEA statement)",
            "The Indian Eye \u2014 'US officials raise concern about democracy in Bangladesh' (congressional and State Department concern, June 2026)",
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
