#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (19:30 UTC slot / videshi-writer-sports)

Article: After a shock six-wicket loss to South Africa at Old Trafford,
India's women's T20 World Cup campaign has turned into a virtual knockout.
Harmanpreet Kaur's side, second in Group A on four points, must now navigate
Bangladesh (June 25) and the unbeaten six-time champions Australia (June 28,
Lord's) to be sure of a semi-final spot — and ideally win big to protect
their net run rate.

KEY FACTS (verified across Wisden, Female Cricket, Khel Now, Women's Cricket):
- India lost to South Africa by six wickets at Old Trafford (Manchester);
  Marizanne Kapp's unbeaten 81 off 45 chased it down, with India dropping
  Kapp twice (Radha Yadav).
- It was India's FIRST defeat of the tournament after big wins over Pakistan
  and the Netherlands.
- Group A standings after the SA game: Australia 6 pts (NRR +4.391, played 3,
  W3); India 4 pts (NRR +2.511); South Africa 4 pts (NRR -0.546);
  Bangladesh 2 pts (-0.641); Pakistan 0; Netherlands 0.
- Top two of each group advance to the semi-finals.
- India's remaining games: vs Bangladesh, June 25, Old Trafford; vs
  Australia, June 28, Lord's.
- Scenario 1 (win both): semis guaranteed, 8 points, NRR cushion.
- Scenario 2 (lose one, e.g. to Australia): max 6 points, fate out of their
  hands — they would need South Africa to drop points vs Netherlands/Bangladesh.
- India's destiny is in their own hands but the safety net is gone.
- Captain: Harmanpreet Kaur. (She also just played her 200th T20I — covered
  separately, not the focus here.)

DEDUP: Checked last 3 days of sports. Existing pieces cover (a) the SA-loss
match RECAP ("India's Unbeaten Run Ends at Old Trafford"), (b) Harmanpreet's
200th-cap MILESTONE, (c) the women's HOCKEY Nations Cup, plus men's ODI/T20I
squads, Headingley Test, MLC. NONE is the FORWARD-LOOKING qualification /
NRR / virtual-knockout scenario piece. This is distinct.

ANGLE: The maths of survival. A campaign that began with two thrashings has
become a tightrope — beat Bangladesh, then topple the team that has won this
trophy six times, or hand your fate to a calculator. For the diaspora it is
the most-followed women's side in the world cricket, and the Lord's date with
Australia is appointment viewing from London to New Jersey.

Hero: Wikipedia REST API portrait of Harmanpreet Kaur (the captain carrying
the side). Person-led → Wikipedia first.
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
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = orig or thumb
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=82):
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
            data=compressed, timeout=30,
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
print("ARTICLE: India women's T20 WC qualification — virtual knockout")
print("="*60)

art_slug = "india-women-t20-world-cup-2026-semifinal-qualification-scenarios-south-africa-loss-bangladesh-australia-lords-harmanpreet-net-run-rate-diaspora-nri"
art_headline = "One Defeat Turned India's World Cup Into a Tightrope: Beat Australia, or Trust a Calculator"
art_subheadline = "A shock loss to South Africa has stripped away India's safety net at the Women's T20 World Cup. Harmanpreet Kaur's side must now get past Bangladesh and the six-time champions to be sure of the semi-finals."

art_body = """For two matches, India's women looked like a side that had come to England to win the thing. Then, on a Sunday night in Manchester, the calculator came out.

A six-wicket defeat to South Africa at Old Trafford — India's first of the tournament, sealed by Marizanne Kapp's unbeaten 81 off 45 balls — has turned what began as a serene campaign into a tightrope walk. Harmanpreet Kaur's side still sits second in Group A, still controls its own destiny. But the comfortable cushion is gone, and the two games that remain have the unmistakable feel of knockouts.

## How the Group Stands

The top two from each group advance to the semi-finals, and Group A has tightened into a three-way scrap. Australia, the six-time champions, sit top with a perfect record from three matches and a net run rate of +4.391 that is almost untouchable. India are second on four points with a healthy +2.511. South Africa, level on four points, trail only because their run rate sits at -0.546 — the margin that for now keeps the Proteas in third.

The arithmetic is unforgiving but clear. India's last two group games are against Bangladesh on June 25 at Old Trafford, and then the big one: Australia at Lord's on June 28.

## The Two Roads

The clean road is simple to describe and hard to walk. Win both, and India reach eight points and a semi-final place with room to spare; even if South Africa win out and match them on points, India's superior run rate should carry them through. The only caveat is the small print of net run rate — squeak past Bangladesh and Australia by narrow margins while South Africa hammer their opponents, and the gap could close uncomfortably. The message from the dressing room is therefore not just to win, but to win big.

The other road is the one no one in blue wants to take. Lose even one of the two — an upset against Bangladesh, or the more probable stumble against an Australian juggernaut that has not lost a game — and India can finish with a maximum of six points. At that point their fate slips out of their hands entirely. They would need South Africa to drop points against the Netherlands or Bangladesh, and would spend the final days of the group stage as anxious spectators rather than masters of their own story.

## The South Africa Sting

What makes the margin so fine is how avoidable Sunday felt. India posted a competitive total and then watched it slip away, Kapp dropped twice — both chances off Radha Yadav — before she finished the job with the kind of clean, brutal hitting that decides World Cups. It was a reminder that this Indian side, for all its top-order firepower in Smriti Mandhana and the openers, still wrestles with the same old demon: closing out the games it should.

## Why It Travels

For the diaspora, the Indian women's team has become appointment viewing in its own right, no longer the afterthought to the men's calendar. The June 28 date with Australia at Lord's — the home of cricket, a ground steeped in NRI pilgrimage — is the sort of fixture that fills WhatsApp groups from London to New Jersey days in advance. A generation of young girls in the diaspora now grows up watching Harmanpreet and Mandhana the way an earlier one watched Tendulkar, and a deep run here matters far beyond the points table.

There is a harder truth beneath the romance. India have spent a decade being the nearly-team of women's cricket — semi-finalists, finalists, never quite champions. To take the next step, they first have to survive a group that, a week ago, looked like a formality.

## What's Next

Bangladesh first, at Old Trafford on June 25, where a big win would rebuild the run-rate buffer and ease the nerves. Then Lord's, and Australia, on June 28. Win that, and India march into the semi-finals on their own terms, having toppled the tournament's apex predator. Lose it, and Harmanpreet Kaur's team will be doing something no side ever wants to do at a World Cup — watching the other results, and waiting."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "India captain Harmanpreet Kaur, whose side must navigate a virtual knockout to reach the semi-finals"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Harmanpreet Kaur")
if wiki_img:
    img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wisden \u2014 Women's T20 World Cup 2026 Points Table: Updated Standings And Net Run Rate After South Africa Beat India", "url": "https://www.wisden.com"},
        {"name": "Female Cricket \u2014 What India Need to Do to Reach the ICC Women's T20 World Cup Semi-Final 2026 After South Africa Defeat?", "url": "https://femalecricket.com"},
        {"name": "Khel Now \u2014 How can India qualify for semi-final of Women's T20 World Cup 2026 after loss to South Africa?", "url": "https://khelnow.com"},
        {"name": "Women's Cricket \u2014 Here's how India can qualify for Women's T20 World Cup 2026 semi-final after a loss against South Africa", "url": "https://www.womencricket.com"},
    ]),
    "diaspora_angle": "The Indian women's team has become appointment viewing across the diaspora, and its June 28 virtual knockout against Australia at Lord's \u2014 a ground steeped in NRI pilgrimage \u2014 is the sort of fixture that fills WhatsApp groups from London to New Jersey, with a generation of diaspora girls now growing up on Harmanpreet and Mandhana.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
