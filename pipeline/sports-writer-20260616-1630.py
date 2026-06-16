#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (16:30 UTC run)
Article: Sarpreet Singh became the first player of Indian origin to START a
FIFA World Cup match when New Zealand drew 2-2 with Iran in Los Angeles on
June 15. Distinct from the prior pre-match preview already in the section —
this is the result/milestone-realised story: he wore the No. 10, played the
full 90, the Kiwis led 2-1 through an Elijah Just brace before Iran's Mohebbi
levelled. Diaspora angle: Auckland-born to Jalandhar Punjabi parents, first
Indian-heritage starter ever (Dhorasoo only ever came off the bench).
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()

        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: Sarpreet Singh — first Indian-origin WC starter")
print("="*60)

art_slug = "sarpreet-singh-first-indian-origin-starter-world-cup-2026-new-zealand-iran-2-2-los-angeles-punjab-nri"
art_headline = "An Auckland Sikh in the No. 10 Shirt Played the Full 90. No Footballer of Indian Origin Had Ever Started a World Cup Match Before."
art_subheadline = "Sarpreet Singh, born in Auckland to a Jalandhar family, started New Zealand's 2-2 draw with Iran in Los Angeles \u2014 a milestone no Indian-heritage player had reached in 96 years of the tournament. Vikash Dhorasoo, the only one before him, had only ever come off the bench."

art_body = """For ninety minutes in Los Angeles on Sunday night, the most-watched footballer in millions of Indian households was a man who has never played for India, was born nearly nine thousand kilometres from Jalandhar, and wears the silver fern of New Zealand on his chest. Sarpreet Singh started in the No. 10 shirt as the All Whites drew 2-2 with Iran at the Los Angeles Stadium in Inglewood \u2014 and in doing so became the first player of Indian origin in history to start a FIFA World Cup match.

It is the kind of distinction that needs a careful asterisk, and the asterisk only makes it more remarkable. A footballer of Indian descent had appeared at a World Cup exactly once before: Vikash Dhorasoo, the France midfielder whose family roots trace to Andhra Pradesh, featured in 2006. But Dhorasoo came off the bench in both of his appearances, playing only a handful of minutes. Sarpreet Singh did what no one with Indian heritage had done since the tournament began in 1930 \u2014 he was named in the starting eleven and stayed on the pitch until the final whistle.

## A Point Snatched Away

The match itself was the sort of open, flawed, thoroughly entertaining contest that the lower-ranked nations have specialised in producing at this expanded 48-team World Cup. New Zealand, the lowest-ranked side in the entire tournament, twice led and twice were pegged back. Iran's full-back Ramin Rezaeian opened the scoring, but the Kiwis responded through Elijah Just, who struck twice to put his side 2-1 ahead and became the first man ever to score multiple goals in a single game for New Zealand at a men's World Cup. The lead held until the 64th minute, when Mohammad Mohebbi met a Rezaeian cross to level it at 2-2, a scoreline that flattered neither defence and delighted a noisy, mixed crowd.

Singh, deployed as the creative hub of New Zealand's 4-2-3-1, was at the centre of the Kiwis' best work. He registered three attempts on goal and came closest in the 61st minute as New Zealand pressed for a winner that never came. Head coach Darren Bazeley had travelled to Wellington in the build-up to tell his squad the news in person; for Singh, who had spent much of the past few months sidelined by injury, the start was, in his own word, a "reward."

## From a Jalandhar Family to the Bundesliga

The story behind the milestone is the diaspora story in miniature. Sarpreet Singh was born and raised in Auckland to Punjabi parents whose family originates from Jalandhar. His mother, Sarabjit, enrolled him at the Wynton Rufer Soccer Academy when he was seven, an unusual choice in a country where cricket and rugby dominate and where a Sikh boy taking up football was, by his own description, a rarity. The family ran a grocery store; he grew up alongside an elder brother and sister in what he calls "a very typical Punjabi family with a lot of uncles and aunties and cousins."

His talent took him far from that backyard. In 2019 Singh became the first player of Indian descent to sign for Bayern Munich, and the first of Indian heritage to feature in Germany's Bundesliga, winning a league title with the club during the 2019-20 season. Loan spells in Portugal and Serbia followed before he returned to Wellington Phoenix this year to rebuild his fitness ahead of the World Cup. An injury in February cost him nearly two months, but he recovered in time to make the 26-man squad \u2014 and then the starting eleven.

There is a neat thread connecting him to the country his family left. In 2018, at the Intercontinental Cup in Mumbai, a young Singh scored against Kenya and helped New Zealand's development side beat an India team led by Sunil Chhetri. "It's a little bit strange being a Singh and playing for New Zealand in India against India," he recalled.

## A Tournament of Firsts for the Diaspora

Singh is not alone. This World Cup has quietly become a showcase for footballers of Indian and broader South Asian descent. Australia's Melbourne-born winger Nishan Velupillay, whose mother is Anglo-Indian, came off the bench against Turkiye to become the first Indian-origin player at a World Cup since Dhorasoo. Qatar's squad includes Tahsin Mohammed Jamshid, whose parents hail from Kerala. For a region of 1.7 billion people whose national teams have never reached the men's World Cup \u2014 India last came close in 1950, when it withdrew \u2014 these players have become surrogate flags to wave.

That ache is the reason Singh's start resonates so far beyond New Zealand. India did not qualify; the Blue Tigers crashed out in the second round of Asian qualifying, extinguishing a brief flicker of hope that the 48-team field might finally open a door. So the diaspora has adopted the next best thing: a Punjabi-rooted, Virat Kohli-supporting attacking midfielder carrying their heritage onto the biggest stage in the sport.

"I just want to do my best to lift the names of Indian people, and there is no better stage to do it than the World Cup," Singh said before the tournament. "I see it as a responsibility to do my best and even inspire the next generation." On Sunday in Los Angeles, with the No. 10 on his back and ninety minutes in his legs, he did exactly that. New Zealand turn next to Egypt in Vancouver on June 21, both sides still chasing a first win \u2014 and a generation of Indian-origin kids, from Auckland to New Jersey, now has a name to put on the shirt."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Sarpreet Singh training with Bayern Munich in 2019; he became the first Indian-origin player to start a World Cup match"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Sarpreet Singh")
if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "football",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "myKhel \u2014 Sarpreet Singh Makes History as First Indian-Origin Starter in FIFA World Cup Match", "url": "https://www.mykhel.com/football/sarpreet-singh-first-indian-origin-starter-fifa-world-cup-match-011-440499.html"},
        {"name": "The Times \u2014 World Cup 2026 day 5 as it happened (Iran 2 New Zealand 2)", "url": "https://www.thetimes.com"},
        {"name": "Mint \u2014 Exclusive: New Zealand's Sarpreet Singh vows to make a mark at FIFA World Cup 2026", "url": "https://www.livemint.com"},
        {"name": "Sporting News \u2014 Who is Sarpreet Singh? New Zealand's Punjabi-origin footballer", "url": "https://www.sportingnews.com"},
        {"name": "FIFA \u2014 World Cup 2026 Matchday round-up", "url": "https://www.fifa.com"},
    ]),
    "diaspora_angle": "Sarpreet Singh, born in Auckland to a Jalandhar Punjabi family, became the first footballer of Indian origin ever to start a World Cup match \u2014 a surrogate source of pride for a diaspora whose own national team has never qualified.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
