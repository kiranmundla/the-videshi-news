#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (16:30 UTC slot / videshi-writer-sports)

Article: India have SACKED Suryakumar Yadav as T20I captain — the man who led
them to their THIRD T20 World Cup title (home soil, 2026) — and left him out
of the squad ENTIRELY. Shreyas Iyer, recalled to T20Is for the first time
since December 2023, is the new full-time T20I captain for the Ireland +
England tours and the Asian Games 2026.

KEY FACTS (verified across CricTracker, Cricbuzz, Wisden, Sky Sports, The
Indian Eye):
- BCCI announced T20I squads for Ireland (2 T20Is from June 26, Belfast) and
  England (5 T20Is), plus the Asian Games 2026 (Japan, September).
- Shreyas Iyer named full-time T20I captain, replacing Suryakumar Yadav.
  Tilak Varma is vice-captain.
- Suryakumar has lost BOTH the captaincy AND his place in the side.
- Reason: form. SKY averaged just 28.65 across the 52 T20Is he captained;
  since the 2024 T20 WC win he managed only two fifties / 242 runs at avg 23;
  IPL 2026 was below par (270 runs, avg 20.76, SR 147.54 for 9th-placed MI).
- Iyer last played a T20I in December 2023 (vs Australia, Bengaluru). The
  recall AND the captaincy together make it a bold call.
- Iyer's captaincy CV: led Delhi Capitals to IPL final 2020, won the IPL
  with KKR 2024, took Punjab Kings to the final 2025. T20 captaincy record:
  114 matches, 68 wins, 59.65% win rate (vs SKY's 73 matches, 71.23%).
- Ireland T20I squad: Shreyas Iyer (C), Abhishek Sharma, Sanju Samson (wk),
  Ishan Kishan (wk), Shivam Dube, Tilak Varma (VC), Nitish Kumar Reddy, Axar
  Patel, Washington Sundar, Varun Chakravarthy, Mohammed Siraj, Arshdeep
  Singh, Prince Yadav, Vaibhav Sooryavanshi, Harshit Rana, Ravi Bishnoi.
- 15-year-old Vaibhav Sooryavanshi included across all three white-ball
  assignments (covered separately — NOT this article's focus).
- Bumrah rested for white-ball Ireland/England (workload) but named for the
  Asian Games gold-medal push.

DEDUP: Checked last 3 days of sports. Existing pieces cover (a) the ODI squad
/ Gill all-format captaincy, (b) Kohli's white-ball return, (c) Vaibhav's
maiden call-up + parents on tour, (d) Headingley Test, (e) MLC, (f) women's
T20 WC, (g) women's hockey Nations Cup. NONE is about the T20I CAPTAINCY
CHANGE — Suryakumar sacked, Iyer in. This is a distinct, fresh story.

ANGLE: The brutal arithmetic of T20 leadership — a World Cup-winning captain
dropped barely months after the trophy lift, because the runs dried up. For
the diaspora it's a debate about loyalty vs ruthlessness, and a window on how
hard-nosed India have become about the 2026 (later) World Cup cycle and the
deep talent pool that lets them discard even a champion.

Hero: Wikipedia REST API portrait of Shreyas Iyer (the new captain, the
forward-looking face of the story). Person-led → Wikipedia first.
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
print("ARTICLE: India sack World Cup-winning T20I captain Suryakumar")
print("="*60)

art_slug = "india-sack-suryakumar-yadav-t20i-captain-dropped-squad-shreyas-iyer-new-captain-england-ireland-asian-games-2026-form-diaspora-nri"
art_headline = "India Sacked the Captain Who Won Them the T20 World Cup — and Left Him Out of the Team Altogether"
art_subheadline = "Months after Suryakumar Yadav lifted India's third T20 world title, the selectors have stripped him of the captaincy and his place in the side. Shreyas Iyer, back in the format after two and a half years, inherits the job."

art_body = """A World Cup-winning captain is supposed to be untouchable. India's selectors have just decided otherwise.

When the Board of Control for Cricket in India named its Twenty20 squads on Sunday for next month's tours of Ireland and England, the headline was not a name added but a name removed. Suryakumar Yadav — the man who, only months earlier, had lifted India's third T20 World Cup on home soil — was not the captain. He was not the vice-captain. He was not in the squad at all. In his place, as the new full-time T20I captain, stood Shreyas Iyer, a batter who had not played a single T20 international since December 2023.

It is the kind of call that, in a cricket-obsessed country, does not so much close a debate as detonate one.

## The Brutal Arithmetic

The case against Suryakumar was never about the trophy. It was about the runs. For all his reputation as the most inventive T20 batter of his generation, the numbers under his own captaincy had quietly curdled. Across the 52 matches in which he wore the armband, he averaged a modest 28.65. Since the 2024 World Cup triumph in Barbados, he had managed just two fifties and 242 runs at an average of 23. His IPL 2026 was the same story in miniature — 270 runs at 20.76, a strike rate of 147 that would once have embarrassed him, for a Mumbai Indians side that finished ninth.

A captain can carry a thin patch. A captain who is also the team's premier stroke-maker, and who is not scoring, becomes a harder argument to win. The selectors, planning toward the next World Cup cycle, chose ruthlessness over sentiment.

## The Bold Replacement

If dropping a world champion was brave, recalling Shreyas Iyer to lead was bolder still. Iyer last played a T20I in December 2023, against Australia in Bengaluru. He has spent the intervening period not in the national side but building one of the most decorated captaincy résumés in the modern game: a Delhi Capitals run to the IPL final in 2020, the title with Kolkata Knight Riders in 2024, and Punjab Kings to the final in 2025. Few Indian players have led as consistently, or as successfully, in the franchise arena.

The raw leadership ledger flatters Suryakumar — a 71% win rate from 73 matches in charge, against Iyer's 59.65% from 114. But win percentages in T20 cricket are slippery things, shaped by opposition and circumstance, and the selectors were plainly weighing something else: a man in form, trusted by dressing rooms, against one whose bat had gone quiet. Tilak Varma was named Iyer's deputy.

## A Squad Built for the Future

The wider squad underlined the generational tilt. Fifteen-year-old Vaibhav Sooryavanshi, the IPL's breakout sensation, was named across all three white-ball assignments. Jasprit Bumrah was rested from the white-ball legs to manage his workload but retained for the Asian Games in Japan, where India will chase gold. Abhishek Sharma, Sanju Samson, Shivam Dube, Washington Sundar, Varun Chakravarthy, Arshdeep Singh and Ravi Bishnoi fill out a group with one eye firmly on the world title to come.

India's two-match series against Ireland begins on June 26 in Belfast, with the five-match England series to follow.

## Why It Travels

For the diaspora, this is more than a selection note — it is a Rorschach test. To some it reads as cold-blooded modernity, the mark of a team so deep in talent it can afford to discard a champion the moment the output dips. To others it is a betrayal of a man who delivered the only thing that ultimately matters, a trophy, and was cast aside before the celebration had cooled. The debate will run hot in WhatsApp groups from New Jersey to Sydney, where the loyalty-versus-results argument is never quite settled.

There is also a harder truth beneath it. India have built a system in which even a World Cup-winning captaincy buys no immunity. That ruthlessness, uncomfortable as it looks here, is precisely what has kept them at the summit of the white-ball game.

## What's Next

Iyer's reign begins in Belfast, and the questions travel with him. Can a captain returning after two and a half years away rediscover his own international rhythm while running a young side? And has the door truly closed on Suryakumar Yadav, 35 and reportedly the subject of franchise interest elsewhere — or is this, as Indian cricket has taught its followers so often, merely an interval rather than an ending?"""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Shreyas Iyer, recalled after more than two years, is India's new full-time T20I captain"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Shreyas Iyer")
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
        {"name": "CricTracker \u2014 Vaibhav Sooryavanshi earns maiden call-up as India announce squad for England, Ireland T20Is and Asian Games 2026", "url": "https://www.crictracker.com"},
        {"name": "CricTracker \u2014 Shreyas Iyer vs Suryakumar Yadav: Who has the better T20 captaincy record?", "url": "https://www.crictracker.com"},
        {"name": "Cricketaddictor \u2014 Shreyas Iyer gets massive backing from PBKS pacer ahead of first series as India's full-time T20I captain", "url": "https://www.cricketaddictor.com"},
        {"name": "Sky Sports \u2014 England vs India: India name T20I and ODI squads", "url": "https://www.skysports.com"},
    ]),
    "diaspora_angle": "A World Cup-winning captain dropped months after the trophy lift is a Rorschach test for the diaspora \u2014 cold-blooded modernity to some, betrayal to others \u2014 and a window on how ruthless India have become about staying atop the white-ball game, the kind of loyalty-versus-results debate that runs hot in NRI WhatsApp groups across time zones.",
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
