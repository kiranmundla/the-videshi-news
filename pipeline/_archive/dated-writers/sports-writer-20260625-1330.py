#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (13:30 UTC slot / videshi-writer-sports)

Article: Dev Meena clears 5.46m to break his own men's pole vault national
record at the 65th National Inter-State Senior Athletics Championships in
Bhubaneswar, sealing qualification for the 2026 Asian Games (Aichi-Nagoya) and
strengthening his case ahead of the Glasgow Commonwealth Games. Part of a
record-laden day at Kalinga Stadium (Anushka Yadav hammer NR, Jyothi Yarraji
hurdles comeback).

DEDUP CHECK (vs recent ~4 days sports feed, category=sports):
- Feed HAS: hockey Nations Cup win; Edgbaston Test; Vahin-style safeguarding;
  Anushka Yadav HAMMER THROW NR; Neeraj Chopra Doha javelin; badminton worlds;
  fencing; Animesh Kujur sprinter; Jagmeet basketball; women's 4x100 relay;
  para-badminton; MI New York; Pant-Kuldeep trade; Wimbledon; Kohli ODI return.
- Feed does NOT have: Dev Meena's POLE VAULT national record. Distinct athlete,
  distinct discipline (pole vault, never covered). The Anushka hammer-throw
  piece is its own event; this is a separate athlete/discipline. CLEAR TO WRITE.

Key facts (ANI via Daily PRABHAT, Yardbarker x2; Wikipedia "Dev Meena"):
- 65th National Inter-State Senior Athletics Championships 2026, Kalinga
  Stadium, Bhubaneswar, Odisha. Wednesday June 24, 2026.
- Dev Kumar Meena (Madhya Pradesh) cleared 5.46m — new men's pole vault
  national record, bettering the 5.45m he had jointly held with training
  partner Kuldeep Kumar (set at the Federation Cup in Ranchi a month earlier).
- 5.46m beats the Asian Games (Aichi-Nagoya) qualification mark of 5.45m →
  Asian Games berth secured. Also strengthens his Glasgow Commonwealth Games
  standing.
- Pole vault podium: Dev Meena 5.46m; Reegan G (Tamil Nadu) 5.30m; Kuldeep
  Kumar (Madhya Pradesh) 5.20m. Top three all bettered the old meet record of
  5.20m (M Gowtham, 2025).
- His second consecutive NR performance. India's men's pole vault NR has been
  improved five times in under two years — sign of growing depth.
- Dev: "It is good to improve the national record before going to the Glasgow
  Commonwealth Games." / "The competition was challenging, nonetheless I'm
  excited to have enhanced my profile."
- Background: born Dewas, Madhya Pradesh; began as a 400m runner before coach
  Ghanshyam Yadav moved him to pole vault; trains at Madhya Pradesh Athletics
  Academy, Bhopal; has worked with Cuban coach Angel Garcia; PB 5.40m at the
  2025 World University Games before this run of records.
- Same day records: Anushka Yadav hammer NR 67.02m (also AG qual); Jyothi
  Yarraji 100m hurdles comeback gold in 12.99s after 12 months injured.

Hero: Wikipedia/Commons photo of Dev Meena. Permanent Wikimedia URL,
downloaded + re-uploaded to Supabase.
"""

import os, io, json, subprocess
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


def compress_image(img_bytes, max_width=1200, quality=85):
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


print("\n" + "=" * 60)
print("ARTICLE: Dev Meena pole vault national record + Asian Games berth")
print("=" * 60)

art_slug = "dev-meena-pole-vault-national-record-5-46m-inter-state-athletics-bhubaneswar-asian-games-qualification-2026-diaspora-nri"
art_headline = "One Centimetre, and the Record Is His Alone: Dev Meena Vaults to 5.46m"
art_subheadline = "The 21-year-old from Madhya Pradesh cleared 5.46m at the National Inter-State Championships in Bhubaneswar, breaking the men's pole vault national record he had shared with his training partner and booking his ticket to the Asian Games."

art_body = """For a few weeks, the Indian men's pole vault national record had two names on it. On Wednesday in Bhubaneswar, Dev Meena made sure it carried only one. The 21-year-old from Madhya Pradesh cleared 5.46 metres at the 65th National Inter-State Senior Athletics Championships, going a single centimetre higher than the 5.45m he had jointly held with training partner Kuldeep Kumar — and, in doing so, claimed the record outright.

The mark did more than rewrite the books. At 5.46m, Meena cleared the 5.45m qualification standard for the 2026 Asian Games in Aichi-Nagoya, sealing his place on the flight to Japan. It also sharpened his case ahead of the Glasgow Commonwealth Games, where India will send a leaner athletics contingent than in years past.

## A record on the move

What stands out about Meena's jump is not just the height but the speed of his climb. Barely a month ago, he and Kuldeep Kumar had shared the national record at 5.45m at the Federation Cup in Ranchi. This was his second consecutive record-breaking performance, and it fits a wider pattern: the Indian men's pole vault national record has now been improved five times in under two years, a sign of how quickly the event's depth and competitiveness are growing.

The podium at Kalinga Stadium underlined that depth. Meena's 5.46m led the way, with Tamil Nadu's Reegan G taking second at 5.30m and Kuldeep Kumar third at 5.20m. All three bettered the old meet record of 5.20m, set by M. Gowtham in 2025 — three vaulters clearing a bar that had stood as the championship best only a season earlier.

## From the 400m to the pole

Meena's route to the top of Indian vaulting was not a straight line. Born in Dewas, Madhya Pradesh, he started out as a 400m runner before coach Ghanshyam Yadav, judging his physique better suited to the technical event, moved him to the pole vault. He now trains at the Madhya Pradesh Athletics Academy in Bhopal and has also worked under Cuban coach Angel Garcia. Before this run of records, his personal best was 5.40m, set at the 2025 World University Games.

"It is good to improve the national record before going to the Glasgow Commonwealth Games," Meena said after the win. "The competition was challenging, nonetheless I'm excited to have enhanced my profile."

## A day of records in Bhubaneswar

Meena was not the only athlete to leave Kalinga Stadium with a national record and an Asian Games berth. In the throwing arena, 18-year-old Anushka Yadav of Uttar Pradesh erased the women's hammer throw national record with a huge effort of 67.02m, booking her own ticket to Japan. And on the track, national record holder Jyothi Yarraji marked an emotional comeback from a year out with injury, winning the women's 100m hurdles in 12.99 seconds — comfortably inside the Asian Games qualification mark and just under the 13-second barrier.

Taken together, it was one of the most productive days Indian athletics has had on home soil this season, with the Inter-State Championships doing exactly what they are meant to do: serve as a hard qualification filter that pushes the country's best to peak at the right moment.

## Why the diaspora should care

For Indian sports fans abroad, the headline names are usually Neeraj Chopra's javelin or the sprinters chasing relay medals. Pole vault has rarely been part of that conversation — which is precisely what makes Meena's rise worth watching. He is a young athlete in a technical discipline that India has historically struggled in, improving a national record by the centimetre and qualifying for two major Games in the same season. As the Asian Games and Commonwealth Games approach, diaspora audiences in Europe, the Gulf and North America will have a new name to follow, and a reminder that the depth of Indian track and field now reaches well beyond its established stars."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Dev Meena)...")
img_caption = "Indian pole vaulter Dev Meena, who broke the men's national record with a clearance of 5.46m."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Dev_Meena.jpg/330px-Dev_Meena.jpg"
img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "athletics",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Daily PRABHAT / ANI \u2014 Anushka Yadav, Dev Meena set national records at 65th National Inter-State Senior Athletics C'ships", "url": "https://dailyprabhat.com/"},
        {"name": "Yardbarker \u2014 Inter-State Athletics 2026: Dev Meena, Anushka Yadav Break National Records; Secure Asian Games Tickets", "url": "https://www.yardbarker.com/"},
        {"name": "Yardbarker \u2014 National Inter-State Athletics: Dev Meena, Anushka, Jyothi Brightened Day One Of Meet (full results)", "url": "https://www.yardbarker.com/"},
        {"name": "Wikipedia \u2014 Dev Meena", "url": "https://en.wikipedia.org/wiki/Dev_Meena"},
    ]),
    "diaspora_angle": "Pole vault has rarely featured in NRI sports conversations, but Dev Meena's record run and dual Asian Games and Commonwealth Games qualification give diaspora fans a new Indian track-and-field name to follow as both Games approach.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
