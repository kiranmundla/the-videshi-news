#!/usr/bin/env python3
"""
Sports Writer — June 26, 2026 (01:30 UTC slot / videshi-writer-sports)

Article: India's badminton stars have landed on US soil for the 2026 US Open
(BWF Super 300) at California State University, Fullerton, and the contingent
made a near-flawless start — veteran Kidambi Srikanth, teen prodigy Tanvi
Sharma, Devika Sihag and the Treesa Jolly / Gayatri Gopichand women's doubles
pair all advancing. Diaspora angle: a full-strength Indian badminton group is
playing a sanctioned BWF event in California, putting India's shuttlers within
driving distance of one of the largest South Asian communities in the US.

DEDUP CHECK (vs recent ~3 days sports feed, category=sports):
- Feed HAS: MLC Oakland Coliseum (Unicorns vs Texas, 22:45 today); India Women
  vs Bangladesh T20 WC; India-Ireland 1st T20I preview (Iyer era); Edgbaston
  Test preview; Dev Meena pole vault; women's hockey Nations Cup; Anushka Yadav
  hammer throw; Neeraj Chopra Doha; BWF WORLD CHAMPIONSHIPS 2026 New Delhi
  (hosting announcement, June 24 19:45); women's relay; Pant trade; para-
  badminton youth games; Headingley Test.
- The June 24 badminton piece is about INDIA HOSTING the BWF World
  Championships in New Delhi (a future event / hosting story). THIS piece is
  about the live 2026 US OPEN (BWF Super 300) being played NOW in Fullerton,
  California, and the Indian contingent's results there — different event,
  different venue (USA not India), different angle (diaspora-on-US-soil, live
  results). Distinct. CLEAR TO WRITE.

Key facts (BWF / Wikipedia 2026 U.S. Open badminton; thesportstak; yardbarker;
devdiscourse — all crawled within last 24h):
- 2026 U.S. Open = BWF Super 300, California State University Fullerton (Titan
  Gym), Fullerton, California, USA; 23–28 June 2026; total purse $250,000.
- Lakshya Sen was the No. 2 seed but WITHDREW. Chou Tien-chen (TPE) No. 1 seed.
  Srikanth Kidambi is the No. 5 seed.
- First-round Indian results (Wednesday):
  * Kidambi Srikanth (5) bt D. Saneeth (IND) 21-14, 21-12 (30 min) → 2nd round.
  * Rounak Chouhan (qualifier) bt S. Sankar Muthusamy (IND) 23-21, 21-16.
  * Tanvi Sharma (World Junior C'ships silver medallist) bt Yvonne Li (GER)
    23-21, 21-16 (women's singles R1).
  * Devika Sihag (Thailand Masters champion) bt Ines Lucia Castillo (PER)
    21-14, 21-14.
  * Rakshitha Sree bt Tereza Svabikova (CZE) 21-15, 21-8.
  * Mixed doubles: Dhruv Rawat / K. Maneesha (7th seed) bt Wirawan Ihsan Adam /
    Serena Kani (INA) 21-15, 21-16 (26 min).
  * Women's doubles: Treesa Jolly / Gayatri Gopichand (world No. 58,
    Commonwealth Games medallists) bt Paula López / Lucía Rodríguez (ESP)
    21-12, 14-21, 21-13 at the Titan Gym; next face Sumire Nakade / Miyu
    Takahashi (JPN). Treesa returned at the Indonesia Open this month after a
    ~3-month injury rehab. They are India's only women's doubles pair in the
    draw.

Hero: Wikipedia/Commons photo of Kidambi Srikanth (the marquee India seed in
the draw). Permanent Wikimedia URL (originalimage), downloaded + re-uploaded to
Supabase.
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
print("ARTICLE: India's shuttlers open strong at the US Open in California")
print("=" * 60)

art_slug = "india-badminton-us-open-2026-super-300-fullerton-california-srikanth-tanvi-sharma-treesa-gayatri-diaspora-nri"
art_headline = "India's Shuttlers Have Brought Their Season to California \u2014 and Opened the US Open With a Near-Clean Sweep"
art_subheadline = "From veteran Kidambi Srikanth to 17-year-old Tanvi Sharma, India's badminton contingent swept through the first round of the US Open in Fullerton, a Super 300 event staged on the doorstep of one of America's largest South Asian communities."

art_body = """Indian badminton does not often come to the United States, and almost never with this much of its depth on show. This week it has. The 2026 US Open, a BWF World Tour Super 300 event with a $250,000 purse, is being played from June 23 to 28 at the Titan Gym on the campus of California State University, Fullerton \u2014 and the Indian contingent could hardly have asked for a smoother opening day.

In the men's singles, fifth seed Kidambi Srikanth, the former world No. 1 and the marquee Indian name in the draw, needed just half an hour to dismiss compatriot D. Saneeth 21-14, 21-12 and move into the second round. In another all-Indian first-round tie, the emerging Rounak Chouhan, through from qualifying, upset former World Junior Championships silver medallist S. Sankar Muthusamy 23-21, 21-16.

## A new generation announces itself

The brightest result came from the women's draw. Tanvi Sharma, the teenaged World Junior Championships silver medallist who has been billed as the next big thing in Indian women's singles, edged Germany's Yvonne Li 23-21, 21-16 in a tight opener. Devika Sihag, the reigning Thailand Masters champion, was more comfortable, beating Peru's Ines Lucia Castillo 21-14, 21-14, while Rakshitha Sree raced past the Czech Republic's Tereza Svabikova 21-15, 21-8.

It added up to a near-flawless first day for the group. India's seventh-seeded mixed doubles pair of Dhruv Rawat and K. Maneesha needed only 26 minutes to see off Indonesia's Wirawan Ihsan Adam and Serena Kani 21-15, 21-16, rounding off a clean set of wins across singles, doubles and mixed.

## Treesa and Gayatri keep their comeback going

India's only women's doubles pair in the draw, Treesa Jolly and Gayatri Gopichand, also advanced, though they had to work for it. The Commonwealth Games medallists, ranked 58th in the world, took the opening game against Spain's Paula Lopez and Lucia Rodriguez before being pegged back in the second, then steadied themselves to close out a 21-12, 14-21, 21-13 win at the Titan Gym. The result keeps alive a comeback that began only this month, when Treesa returned at the Indonesia Open after roughly three months out with injury. The pair next face Japan's Sumire Nakade and Miyu Takahashi for a place in the quarter-finals.

There was one notable absentee. Lakshya Sen, the Olympic semi-finalist who had been seeded second, withdrew before the tournament, leaving Srikanth to carry the senior men's flag and opening the draw for the younger players behind him.

## Why the diaspora should care

For the millions of Indians who have made California home \u2014 in the Bay Area, in Los Angeles, in the Inland Empire around Fullerton itself \u2014 a full-strength Indian badminton contingent playing a sanctioned BWF event a short drive away is a rarity worth marking. The sport's American footprint is small, and tournaments of this level almost always sit in Asia or Europe. Having Srikanth, Sharma, Sihag and a doubles pair on the comeback trail competing on US soil turns an ordinary Super 300 into a homecoming of sorts for diaspora fans who grew up watching these names on screens half a world away.

It also lands at a moment of momentum for Indian badminton off the court. Just days earlier, the country confirmed it will host the BWF World Championships in New Delhi for the first time in 17 years, a sign of how central India now is to the global game. The US Open is a smaller stage, but for the community watching from the stands in Fullerton, it may feel like the bigger occasion. The early rounds run through the week, with the quarter-finals and the business end of the draw to follow \u2014 and, for once, the Indian contingent is doing its work in the same time zone as a large slice of its overseas support."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikimedia/Commons \u2014 Kidambi Srikanth)...")
img_caption = "Kidambi Srikanth in action; the former world No. 1 is the No. 5 seed in India's US Open contingent in Fullerton, California."
img_attribution = "Wikimedia Commons"

# Wikipedia originalimage (full-res, permanent) for Srikanth
wiki_img = "https://upload.wikimedia.org/wikipedia/commons/5/5d/Yonex_IFB_2013_-_Eightfinal_-_Boonsak_Ponsana_%E2%80%94_K._Srikanth_01.jpg"
img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 trying Treesa Jolly photo")
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/7/7b/The_six_medallists_in_the_women%27s_doubles_%28Treesa_Jolly%29.jpg",
        f"{art_slug}.jpg",
    )
    if img_final:
        img_caption = "Treesa Jolly, half of India's only women's doubles pair in the US Open draw, who advanced to the second round in Fullerton."

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "badminton",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2026 U.S. Open (badminton): venue, dates, seeds, draws", "url": "https://en.wikipedia.org/wiki/2026_U.S._Open_(badminton)"},
        {"name": "The Sports Tak \u2014 US Open 2026: Kidambi Srikanth, Tanvi Sharma march into second round", "url": "https://www.thesportstak.com/"},
        {"name": "Yardbarker \u2014 Treesa-Gayatri advance at US Open, Rounak Chouhan enters main draw", "url": "https://www.yardbarker.com/"},
        {"name": "Devdiscourse \u2014 Indian badminton stars shine at US Open", "url": "https://www.devdiscourse.com/"},
    ]),
    "diaspora_angle": "A full-strength Indian badminton contingent is competing in a sanctioned BWF event on US soil in Fullerton, California, putting the country's shuttlers within driving distance of one of America's largest South Asian communities.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
