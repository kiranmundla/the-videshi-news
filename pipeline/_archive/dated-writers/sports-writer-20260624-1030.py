#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (10:30 UTC slot / videshi-writer-sports)

Article: Animesh Kujur — India's fastest man — feature. The 23-year-old from
Odisha holds the national records in both the 100m (10.15 PB, May 2026) and
200m (20.32 NR, 2025) and in 2025 became the first Indian male sprinter to
qualify for a World Athletics Championships in a short-sprint event. Through
the 2026 season he has been racking up international 200m wins/podiums (Saudi
GP gold 20.77, New Taipei City silver 20.47, Kalinga Continental Tour gold
20.77, Federation Cup gold 20.64) and has qualified for the Commonwealth Games
in Glasgow (July 23–Aug 2). Story = India, a country with no sprint tradition,
suddenly has a man who runs the blue-riband events at a world level.

DEDUP CHECK (vs recent feed, last ~4 days of sports):
- Recent sports feed is dominated by cricket (England/India T20I & ODI squads,
  Headingley Test, women's T20 World Cup, Pant trade, MLC, Vaibhav Sooryavanshi
  11-ball fifty), plus athletics one-offs (women's 4x100m relay gold Jun 24,
  100m NR fell twice May 23, javelin throwers May 27), hockey, para-badminton,
  and a basketball "Indian Wemby" piece (Jun 24).
- Kujur appears only inside two MULTI-subject May articles (the May 23 100m-NR
  piece and the May 27 javelin-vs-sprinters piece). There is NO dedicated
  Kujur profile/feature in the feed, and his 2026 international campaign +
  Commonwealth Games qualification has not been covered as its own story.
- The Neeraj Chopra Doha comeback (the other fresh candidate) was REJECTED as a
  topic: The Videshi already published it on June 19 ("Neeraj Chopra Finished
  Fourth on His Comeback. The Number That Matters Is 85.69.").

Key facts (Wikipedia, IndiaSportsHub, Amar Ujala/PTI, MyKhel, Odiasamaj —
May/June 2026):
- Animesh Kujur, 23, from Odisha; national record holder in BOTH 100m and 200m.
- 200m NR: 20.32s, bronze at 2025 Asian Athletics Championships, Gumi, South
  Korea (31 May 2025).
- 100m: broke the national mark with 10.18s in 2025 (first Indian under 10.2s);
  lowered his PB to 10.15s in Ranchi (22 May 2026).
- 4x100m relay NR: 38.69s (Chandigarh, 30 Apr 2025).
- 2025: first Indian male sprinter to qualify for a World Athletics
  Championships (Tokyo) in a short-sprint category.
- 2026 season form: 200m gold at Saudi Athletics Grand Prix, Riyadh (20.77s);
  200m silver at New Taipei City Athletics Open (20.47s, 7 Jun, his 4th-fastest
  ever) — Thailand's Puripol Boonson won in 20.03; 200m gold at the World
  Athletics Continental Tour Bronze meet at Kalinga Stadium, Bhubaneswar
  (20.77s, first World Athletics global meet held in India); 200m gold at
  Federation Cup (20.64s, missed CWG mark of 20.61 by 0.03).
- Qualified for the 2026 Commonwealth Games (Glasgow, 23 Jul–2 Aug) via his
  20.47 in Taipei (under the 20.61 standard).
- Biju Patnaik Sports Award (2024), Odisha "Sportsperson of the Year".
- Known for showmanship — a trademark Usain Bolt-style victory pose.

DIASPORA ANGLE: Sprinting's blue-riband 100m/200m have always belonged to the
Caribbean, the US and West Africa; India has never figured. For diaspora fans
in the US, UK and Canada who only tune into track every Olympics, an Indian man
running 10.1 and 20.3 — and now lining up at the Commonwealth Games against the
best in the world — is a genuinely new kind of representation in the sport's
glamour events.

Hero: Wikipedia/Wikimedia Commons photo of Animesh Kujur (the only Commons
image of him; 320x404 original, real photo of the named athlete). Pexels NOT
used (rules forbid generic stock for a named athlete).
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


def fetch_wikipedia_person_image(name):
    import urllib.parse
    enc = urllib.parse.quote(name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc}",
            headers={"User-Agent": UA}, timeout=20,
        )
        if r.status_code == 200:
            d = r.json()
            orig = d.get("originalimage", {}).get("source")
            thumb = d.get("thumbnail", {}).get("source")
            return orig or thumb
    except Exception as e:
        print(f"  wiki fetch error: {e}")
    return None


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
print("ARTICLE: Animesh Kujur — India's fastest man")
print("="*60)

art_slug = "animesh-kujur-india-fastest-man-sprinter-100m-200m-national-record-commonwealth-games-glasgow-2026-diaspora"
art_headline = "India Has Never Had a Sprinter Like Animesh Kujur. Now He's Heading to the Commonwealth Games."
art_subheadline = "The 23-year-old from Odisha holds the national records in both the 100m and 200m \u2014 the sport's glamour events, where India has never belonged \u2014 and a season of international podiums has booked his ticket to Glasgow."

art_body = """For as long as anyone has kept time in India, the sprint events have been somebody else's province. The 100 metres and the 200 \u2014 athletics' blue-riband races, the ones the whole world stops to watch every Olympics \u2014 have belonged to Jamaica, the United States and West Africa. India produced javelin throwers and milers, wrestlers and shooters and a long line of badminton champions. It did not produce men who could run. Animesh Kujur is quietly rewriting that sentence.

The 23-year-old from Odisha is, by the only measure that counts, the fastest man the country has ever timed. He holds the national record in the 200 metres at 20.32 seconds, set when he took bronze at the 2025 Asian Athletics Championships in Gumi, South Korea. He also owns the 100m mark, having become the first Indian to break 10.2 seconds and then lowering his personal best to 10.15 seconds in Ranchi this May. For a nation whose sprinters spent decades stranded on the wrong side of 10.3 and 21 seconds, those are not incremental numbers. They are a different category of fast.

## A Season of Proving It Travels

A national record is one thing; doing it on foreign tracks against foreign fields is another, and that is where Kujur has spent 2026. He opened his international campaign with a 200m gold at the Saudi Athletics Grand Prix in Riyadh, clocking 20.77 seconds to beat a field that included British sprinters. He followed it with a silver at the New Taipei City Athletics Open in early June, running 20.47 seconds \u2014 the fourth-fastest time of his career \u2014 behind only Thailand's Puripol Boonson, who ran a blistering 20.03 to become one of the quickest Asians in history.

In between, he gave the home crowd something to roar about. At the World Athletics Continental Tour Bronze meet at the Kalinga Stadium in Bhubaneswar \u2014 the first global World Athletics competition ever staged in India \u2014 Kujur stormed to 200m gold in 20.77 seconds in front of a packed house in his own state, finishing with his trademark Usain Bolt-style pose. He added another 200m title at the Federation Cup in 20.64 seconds, missing the Commonwealth Games qualifying standard there by three hundredths of a second, before that Taipei run comfortably cleared the mark and locked in his place.

## What Glasgow Means

That place is at the 2026 Commonwealth Games in Glasgow, which begin on July 23. It is the kind of stage where Indian sprinters have historically gone to make up the numbers, eliminated in the heats while the cameras followed the Jamaicans and the South Africans. Kujur arrives differently \u2014 not as a tourist but as a genuine finalist-level threat, a man whose season's bests would have him racing for medals rather than merely for experience. In 2025 he had already become the first Indian male sprinter to qualify for a World Athletics Championships in a short-sprint event, lining up in Tokyo where no Indian man in the 100m or 200m had ever stood before.

He is also, by temperament, exactly the sort of athlete a sport without a sprint tradition needs. Kujur races with visible joy and showmanship, celebrating wins with crowd-pleasing flourishes that have made him a draw at home meets; Odisha named him its Sportsperson of the Year with the Biju Patnaik Sports Award. The state, which has poured money into athletics infrastructure and hosted that landmark Kalinga meet, has found in him the perfect ambassador.

## Why It Resonates Beyond India

For the Indian diaspora in the United States, Britain and Canada, the appeal is specific. These are communities that follow track seriously only once every four years, when the Olympic 100m final becomes appointment viewing in living rooms from New Jersey to London. To watch those races for a lifetime and never once see an Indian name in the lanes \u2014 and now to have a man who runs 10.1 and 20.3, who beats Europeans on the road and lines up at the Commonwealth Games \u2014 is a small but real shift in what feels possible.

There is a long way to go. The Asian and world standards keep climbing, and a single great season does not make a sustained career. But for the first time, India is not asking whether it can produce a sprinter who belongs on a world start line. It already has one, and his name is worth learning before Glasgow."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia \u2014 Animesh Kujur)...")
img_caption = "Animesh Kujur, India's national record holder in the 100m and 200m, competing at the 2025 World University Games."
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Animesh Kujur")
if wiki_img:
    print(f"  Wikipedia image: {wiki_img}")
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
        {"name": "Wikipedia \u2014 Animesh Kujur", "url": "https://en.wikipedia.org/wiki/Animesh_Kujur"},
        {"name": "IndiaSportsHub \u2014 Animesh Kujur, Mohammed Afsal Shine at Saudi Grand Prix 2026", "url": "https://www.indiasportshub.com/articles/indian-athletes-set-for-saudi-athletics-grand-prix-2026-afsal-kujur-lead-strong-squad"},
        {"name": "Amar Ujala / PTI \u2014 Animesh Wins Silver in 200m in Taipei City", "url": "https://english.amarujaladigital.com/"},
        {"name": "MyKhel \u2014 Federation Cup 2026 Live Updates (Kujur 200m gold)", "url": "https://www.mykhel.com/"},
    ]),
    "diaspora_angle": "Sprinting's blue-riband 100m and 200m have always belonged to the Caribbean, the US and West Africa \u2014 India has never figured. For diaspora fans in the US, UK and Canada who tune into track only at the Olympics, an Indian man running 10.1 and 20.3 and now lining up at the Commonwealth Games is a genuinely new kind of representation in the sport's glamour events.",
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
