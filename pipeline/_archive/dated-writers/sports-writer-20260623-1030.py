#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (10:30 UTC slot / videshi-writer-sports)

Article: Vaibhav Sooryavanshi, 15, smashes the FASTEST FIFTY in List A history —
11 balls — for India A vs Sri Lanka A in the tri-series final at Dambulla
(June 21), making 94 off 29, days before he is set to become India's youngest
ever men's international.

Why it's distinct from the recent feed:
- 2026-06-20 feed piece = his T20I CALL-UP for Ireland/England (selection story,
  "parents on tour"). This is the RECORD INNINGS in Dambulla on June 21 — a
  different event (the actual on-field 11-ball fifty / 94 off 29), not the squad
  announcement. New, marquee, diaspora-friendly.

Key facts (Reuters / Cricket World / IANS, June 21-22):
- India A beat Sri Lanka A by 66 runs in the tri-series final at Rangiri
  Dambulla International Stadium, June 21.
- Sooryavanshi reached fifty in 11 balls — fastest fifty in List A history,
  breaking Kaushalya Weeraratne's 21-year-old 12-ball record.
- He made 94 off 29 (10 fours, 8 sixes), opening; out in the 9th over to
  Sahan Arachchige; missed a record hundred. India A made 377-9; SL A 311 a.o.
- It was his maiden India A fifty.
- Coming off a record IPL: 776 runs in 16 games for Rajasthan Royals (Orange
  Cap), 65 sixes (passed Chris Gayle); first to win IPL MVP + Best Emerging.
- At 15y 71d he became youngest picked for India men's; named in T20I squads
  for Ireland + England tours and Asian Games 2026. If he features he passes
  Sachin Tendulkar (debut 16y 205d, 1989) as India's youngest men's debutant.
- His quote: "There was no pressure... today everything came together."

DIASPORA ANGLE: Sooryavanshi is the prodigy the entire cricket-following
diaspora is tracking — Ireland and England dates put him within reach of NRI
crowds, and a record fifty days before a likely record debut makes him the
must-watch name of the summer.

Hero: Wikipedia REST API portrait — Vaibhav Sooryavanshi. Person-led -> Wikipedia first.
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
print("ARTICLE: Sooryavanshi 11-ball fifty — fastest in List A history")
print("="*60)

art_slug = "vaibhav-sooryavanshi-15-fastest-fifty-list-a-history-11-balls-94-off-29-india-a-sri-lanka-dambulla-tri-series-youngest-india-debut-diaspora-nri"
art_headline = "Eleven Balls: A 15-Year-Old Just Broke the Fastest-Fifty Record in 50-Over Cricket"
art_subheadline = "Vaibhav Sooryavanshi reached his half-century in 11 deliveries for India A against Sri Lanka A in Dambulla, the quickest in the history of List A cricket \u2014 a record-breaking innings of 94 off 29 days before the teenager is set to become India's youngest ever men's international."

art_body = """It took Vaibhav Sooryavanshi eleven balls. Eleven deliveries to do something no one had done in more than half a century of recorded 50-over cricket: reach a half-century faster than any batter in the history of List A cricket. The 15-year-old left-hander did it on Sunday in Dambulla, opening the batting for India A in the tri-series final against Sri Lanka A, and by the time he was done he had turned a final into a personal showcase and a record book into a footnote.

The innings finished on 94 from just 29 balls \u2014 ten fours and eight sixes \u2014 and the only disappointment, if it can be called that, was that he fell six runs short of what would have been an absurd hundred, removed in the ninth over by the Sri Lanka A captain Sahan Arachchige. India A piled up 377 for 9 and then bowled Sri Lanka A out for 311 to win the final by 66 runs. But the scoreline was almost beside the point. The talking point was the fifty, and the eleven balls it took to get there.

## A Record That Stood for 21 Years

The previous mark for the fastest fifty in List A cricket belonged to Sri Lanka's Kaushalya Weeraratne, who reached the milestone in 12 balls back in 2005. It had stood, untouched, for 21 years. Sooryavanshi broke it with a ball to spare, and he did it on Weeraratne's home soil, in a final, against a Sri Lankan attack that had no answer. It was also his maiden fifty in India A colours \u2014 a first half-century that happened to rewrite history.

"I didn't think too much. I just wanted to make the most of the first 10 overs and execute my plans," he told reporters afterwards, with the unbothered calm that has become as much a part of his story as the sixes. "There was no pressure. I worked on areas that weren't going well, and today everything came together." He added, pointedly, that people underestimate his experience in the longer white-ball format: "I've played 50-over cricket quite a bit, even if people don't realise it."

## The Prodigy the World Is Watching

This is not a bolt from the blue. Sooryavanshi arrived at this final on the back of one of the most extraordinary debut seasons the Indian Premier League has seen. Playing for Rajasthan Royals, he topped the run charts with 776 runs in 16 matches to claim the Orange Cap, struck a century and five fifties, and smashed 65 sixes \u2014 a single-season record that pushed past Chris Gayle. He became the first cricketer in IPL history to be named both Most Valuable Player and Best Emerging Player in the same year. The Dambulla fifty was simply the next line in a CV that keeps outrunning his age.

What makes the timing remarkable is what comes next. Sooryavanshi has been named in India's T20I squads for the upcoming tours of Ireland and England, as well as the Asian Games 2026. At 15 years and 71 days he had already become the youngest player ever picked for India's men's team, breaking a record held by Sachin Tendulkar. Should he take the field on either tour, he will go one further and become the youngest man ever to play international cricket for India, surpassing Tendulkar's 1989 debut at 16 years and 205 days.

## Why the Diaspora Is Counting Down

For Indian cricket fans abroad, this is the rare prospect that arrives with a date attached. The tours of Ireland and England put Sooryavanshi within reach of British-Indian crowds at grounds many in the diaspora can actually get to, and the Asian Games add another stage. A teenager who has already broken Gayle's six-hitting record, won the IPL's top individual honours, and now holds the fastest List A fifty in history is the kind of generational talent that families across the United States, Canada, the Gulf and the UK will rearrange their summer viewing around.

There will be cautionary voices, and they are not wrong to urge patience; 15-year-olds have been hyped before, and the step up to international bowling is steep and unforgiving. But records like an 11-ball fifty are not built on hype. They are built on a kind of fearlessness that cannot be taught. India have unearthed something genuinely new, and the rest of the cricketing world \u2014 diaspora included \u2014 is now simply waiting to see how far it goes."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first \u2014 person-led article)...")
img_caption = "Vaibhav Sooryavanshi, the 15-year-old India A opener"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Vaibhav Suryavanshi", "Vaibhav Sooryavanshi, the 15-year-old who hit the fastest fifty in List A history"),
    ("Vaibhav Sooryavanshi", "Vaibhav Sooryavanshi, the 15-year-old who hit the fastest fifty in List A history"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        candidate = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
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
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Reuters \u2014 Sooryavanshi hits record fifty, says pressure not a factor", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Cricket World \u2014 India Celebrates as 15-Year-Old Vaibhav Sooryavanshi Sets New List A Record", "url": "https://www.cricketworld.com"},
        {"name": "IANS \u2014 Sooryavanshi smashes fastest ever List A fifty off 11 balls", "url": "https://www.ianslive.in"},
    ]),
    "diaspora_angle": "Vaibhav Sooryavanshi is the prodigy the entire cricket-following diaspora is tracking \u2014 his record 11-ball fifty comes just as he is named for India's tours of Ireland and England, putting a likely record-breaking debut within reach of NRI crowds and making him the must-watch name of the summer.",
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
