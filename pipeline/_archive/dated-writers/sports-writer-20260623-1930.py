#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (19:30 UTC slot / videshi-writer-sports)

Article: India's young para-badminton squad wins 27 medals (15 gold, 9 silver,
3 bronze) at the 2026 World Abilitysport Youth Games in Mersin, Türkiye.

Distinct from the recent feed:
- The recent sports feed = England Test (Headingley), MLC, India white-ball
  squad churn (Pant/Kuldeep trade, SKY sacked, Shedge call-up), women's T20 WC,
  hockey, Wimbledon, FIFA World Cup recaps. NONE cover para-sport or this youth
  para-badminton haul. New event, new discipline, strongly positive.

Key facts (RevSportz, June 22-23):
- India finished the 2026 World Abilitysport Youth Games (Mersin, Türkiye) with
  27 para-badminton medals: 15 gold, 9 silver, 3 bronze.
- Medals across WH1/WH2 (wheelchair), SL3/SL4 (standing lower-limb), SU5
  (upper-limb), SH6 (short stature) — depth across classifications.
- Haris Mythili Srikumar: 3 golds — men's singles WH2, men's doubles WH1-WH2
  (w/ Nitin Yadav), mixed doubles WH1-WH2.
- Akash Ranjan Mund: 2 golds — men's singles SL3, mixed doubles SL3-SU5
  (w/ Koshika Devda).
- Aryan Sharma: men's singles SL4 gold (+ men's doubles SL3-SU5 gold w/
  Bibhasindhu). Shivangi Pandey: women's singles SL4 gold.
- Tulika Jadhav: women's singles SL3 gold. Gopesh Jhalani: men's singles SU5.
- SH6: Prem Chand Potnuru men's singles gold (+ men's doubles w/ Harshit
  Rajput). Manisha Patel: women's singles SH6 + mixed doubles SH6 (w/ Prem) —
  2 golds. Samaira Kanwat: women's doubles SL3-SU5 gold.
- Silvers: Nitin Yadav (singles + mixed WH2), Bibhasindhu (singles SL3),
  Samaira Kanwat (singles SL3), Koshika Devda (singles SU5), plus doubles.
- Bronzes: Bibhasindhu/Nazliin (mixed SL3-SU5), Tulika Jadhav/Gopesh Jhalani
  (mixed SL3-SU5), Harshit Rajput (singles SH6).

DIASPORA ANGLE: India's para-badminton has become a global powerhouse (Pramod
Bhagat, Krishna Nagar, Sukant Kadam, Manisha Ramadass), and these youth results
signal the next generation. For NRI families — many raising children with
disabilities in inclusive Western school systems — India's rise in para-sport
is a source of pride and a reminder that the pathway now exists back home too.

Hero: Wikimedia Commons file photo of Indian para-badminton star Mansi Joshi —
honest "file photo / representative" caption (no specific youth-athlete portrait
exists on Commons; multi-athlete event). Person-led source rule respected:
Commons/Wikipedia first.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# -- ENV --
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
print("ARTICLE: India youth para-badminton 27 medals, Mersin")
print("="*60)

art_slug = "india-27-medals-para-badminton-2026-world-abilitysport-youth-games-mersin-turkiye-15-gold-haris-mythili-srikumar-akash-ranjan-mund-manisha-patel-diaspora-nri"
art_headline = "Fifteen Golds in Mersin: India's Young Para-Shuttlers Just Announced the Next Generation"
art_subheadline = "India finished the 2026 World Abilitysport Youth Games in Türkiye with 27 para-badminton medals \u2014 15 of them gold \u2014 spread across every classification, a haul that points to a pipeline far deeper than its Paralympic stars alone."

art_body = """India's para-badminton story has, for years, belonged to a handful of household names \u2014 Pramod Bhagat, Krishna Nagar, Sukant Kadam, Manisha Ramadass. This week in Mersin, on Türkiye's Mediterranean coast, a far younger group served notice that the next chapter is already being written. India closed the 2026 World Abilitysport Youth Games with 27 para-badminton medals: 15 gold, nine silver and three bronze, a return that ranked among the most dominant of any nation at the event.

What made the haul striking was not just its size but its spread. The medals came across the full sweep of para-badminton classifications \u2014 the wheelchair categories WH1 and WH2, the standing lower-limb classes SL3 and SL4, the upper-limb class SU5, and the short-stature category SH6. A country can win medals by being deep in one event. India won them everywhere, a sign of a system producing talent across the disability spectrum rather than around a single star.

## The Teenagers Who Led the Charge

Haris Mythili Srikumar was the standout, walking away with three gold medals. He took the men's singles WH2 title, then partnered Nitin Yadav to win the men's doubles WH1\u2013WH2, before completing his set in the mixed doubles WH1\u2013WH2. For a youth athlete to dominate a wheelchair category across singles and both doubles disciplines is the kind of week that marks a player as one to track all the way to senior international level.

Akash Ranjan Mund was not far behind, claiming the men's singles SL3 gold and adding the mixed doubles SL3\u2013SU5 title alongside Koshika Devda. Aryan Sharma won the men's singles SL4 crown and a second gold in the men's doubles SL3\u2013SU5 with Bibhasindhu, while Shivangi Pandey topped the women's singles SL4 podium. Tulika Jadhav took the women's singles SL3 gold, and Gopesh Jhalani won the men's singles SU5.

The short-stature SH6 category proved especially fruitful. Prem Chand Potnuru won the men's singles and then teamed with Harshit Rajput for the men's doubles title. Manisha Patel matched the multi-gold haul of her teammates, winning the women's singles SH6 and the mixed doubles SH6 alongside Prem. Samaira Kanwat rounded out the gold rush with victory in the women's doubles SL3\u2013SU5.

## Depth Behind the Gold

The silver and bronze medals told their own story of strength in numbers. Nitin Yadav added silvers in the men's singles and mixed doubles WH2; Bibhasindhu and Samaira Kanwat reached singles finals in SL3; Koshika Devda finished runner-up in the women's singles SU5; and several doubles pairings pushed deep into their draws. The three bronzes \u2014 Bibhasindhu and Nazliin and the pairing of Tulika Jadhav and Gopesh Jhalani in mixed doubles SL3\u2013SU5, plus Harshit Rajput in the men's singles SH6 \u2014 underlined just how many of India's young players were genuine podium contenders rather than passengers.

That breadth matters more than any single title. India's senior para-badminton program already ranks among the best in the world, but its long-term health depends on a steady supply of young athletes ready to graduate into it. A 27-medal week at a global youth event, spread across classifications, is exactly the evidence selectors and federations look for.

## Why the Diaspora Should Care

For Indians abroad, the rise of para-sport carries a meaning that goes beyond the medal table. Many NRI families are raising children in Western school systems built around inclusion and accessibility, where para-sport is visible and celebrated. Watching India \u2014 a country still building that infrastructure \u2014 produce world-class young para-athletes is both a point of pride and a sign that the pathway now exists back home, not only in Europe or North America.

It is also a reminder that India's sporting identity is broadening. The diaspora's attention is fixed, understandably, on cricket and increasingly on football's World Cup summer. But the athletes who often deliver India's most emotional global moments \u2014 the para-shuttlers, para-athletes and Paralympians \u2014 are quietly building a base that will define the country's medal hopes for the decade ahead. In Mersin this week, that base just got a great deal deeper."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikimedia Commons \u2014 Indian para-badminton, file/representative photo)...")
img_caption = "Indian para-badminton international Mansi Joshi in 2020 (file photo); India's youth squad won 27 para-badminton medals in Mersin"
img_attribution = "Wikimedia Commons"
img_final = None

# Commons file: Mansi Joshi in 2020.jpg (3183x2373, CC) — honest representative hero.
commons_candidates = [
    ("https://upload.wikimedia.org/wikipedia/commons/e/ec/Mansi_Joshi_in_2020.jpg",
     "Indian para-badminton international Mansi Joshi in 2020 (file photo); India's youth squad won 27 para-badminton medals in Mersin"),
]
for url, cap in commons_candidates:
    candidate = upload_to_supabase(url, f"{art_slug}.jpg")
    if candidate:
        img_final = candidate
        img_caption = cap
        break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "para-sport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "RevSportz \u2014 India Clinches 27 Medals in Para-Badminton at 2026 World Abilitysport Youth Games", "url": "https://revsportz.in/india-clinches-27-medals-in-para-badminton-at-2026-world-abilitysport-youth-games/"},
        {"name": "World Abilitysport \u2014 2026 Youth Games, Mersin (event)", "url": "https://www.worldabilitysport.org/"},
    ]),
    "diaspora_angle": "India's para-badminton has become a global powerhouse, and this youth haul signals the next generation \u2014 a point of pride for NRI families raising children in inclusion-focused Western systems and a sign that the pathway in para-sport now exists in India too.",
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
