#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (04:30 UTC slot / videshi-writer-sports)

Article: The ICC/ECB child-safeguarding rule that bars 15-year-old Vaibhav
Sooryavanshi from sharing India's dressing room during the T20I tours of
Ireland (Jun 26 & 28, Belfast) and England (five matches from Jul 1). He can
be in the room during play and in team talks, but must change in a separate
room/washroom; his parents are travelling with him and staying in the team
hotel — an exception agreed because of his age. If he debuts he becomes the
youngest man ever to play for India, breaking Sachin Tendulkar's record.

DEDUP CHECK (vs recent ~3 days sports feed, category=sports):
- Feed has a Sooryavanshi article but it is the FASTEST LIST-A FIFTY (11 balls,
  94 off 29 for India A vs Sri Lanka at Dambulla) — an on-field record story.
- It also has England's T20I squad, India's ODI/T20I squads, Suryakumar sacking,
  Nitish Reddy injury, Headingley Test, etc. NONE cover the SAFEGUARDING /
  separate-dressing-room story, which broke ~Jun 24 (Reuters/Guardian/ECB).
  This is a distinct off-field policy story with a strong UK/Ireland angle.

Key facts (Reuters; The Guardian via Khel Now/Inside Sport; ECB statement; ICC):
- Vaibhav Sooryavanshi, 15 (turns 16 in March 2027). Bihar / Rajasthan Royals.
  Top run-scorer of IPL 2026 (776 runs). On Sunday hit the fastest List-A fifty
  in history (11 balls) for India A vs Sri Lanka A at Dambulla.
- Named in India's T20I squad for the white-ball tours of Ireland and England.
- ICC + ECB safeguarding rules bar under-16 players from sharing a changing
  room with adult professionals. Enforced by ECB / Cricket Ireland; ICC has
  jurisdiction as these are ICC-sanctioned events. ECB "Safe Hands" policy.
- He WILL be allowed in the India dressing room during the match and in team
  talks/strategy meetings; the restriction applies only when changing before
  and after play. He gets a separate changing room/washroom at all venues.
- Cricket Ireland: "The Indian team have been given three separate rooms in the
  pavilion and safeguarding laws have been advised."
- ECB: parents travelling with him "at all times", staying in the SAME hotel —
  "outside of usual protocol, but agreed on this occasion due to his age."
- BCCI confirmed parents accompany him on tour.
- Precedent: Arsenal's Max Dowman (also Ethan Nwaneri earlier) used a separate
  changing room until turning 16 — football has done this; first time in cricket.
- If he debuts he'd be the youngest men's player for India, breaking Sachin
  Tendulkar's record (debuted Nov 1989 at 16y 205d).
- Schedule: IRE v IND 1st & 2nd T20I, June 26 & 28, Civil Service Cricket Club,
  Stormont, Belfast. ENG v IND five T20Is from July 1, Chester-le-Street.
  UK & Ireland broadcast: Sky Sports / TNT Sports.

Hero: Wikipedia/Commons photo of Sooryavanshi (Vaibhav_Suryavanshi_meets_PM_Modi.jpg),
the actual athlete. Permanent Wikimedia URL, downloaded + re-uploaded to Supabase.
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
print("ARTICLE: Sooryavanshi safeguarding / separate dressing room")
print("=" * 60)

art_slug = "vaibhav-sooryavanshi-15-separate-dressing-room-safeguarding-icc-ecb-rules-india-ireland-england-t20i-2026-youngest-debut-tendulkar-record-diaspora-nri"
art_headline = "India's 15-Year-Old Prodigy Will Change in a Room of His Own \u2014 the Safeguarding Rule Behind It"
art_subheadline = "Vaibhav Sooryavanshi can sit in India's dressing room during play and join every team talk, but ICC and English safeguarding rules bar an under-16 from changing alongside adults \u2014 so on the tours of Ireland and England, his parents come too."

art_body = """When India take the field in Belfast on Friday, the most talked-about name on the team sheet may be a boy who cannot get changed with his own teammates. Vaibhav Sooryavanshi, 15 years old and already the highest run-scorer of an entire IPL season, will use a separate dressing room throughout India's white-ball tours of Ireland and England \u2014 not as a punishment, but as a child-protection requirement.

Under safeguarding rules set by the International Cricket Council and the England and Wales Cricket Board, players under the age of 16 are not permitted to share a changing-room environment with adult professionals. Because both the Ireland series and the five-match England series fall under ICC and UK jurisdiction, the restriction applies the moment Sooryavanshi lands. "The Indian team have been given three separate rooms in the pavilion and safeguarding laws have been advised," a Cricket Ireland spokesperson confirmed, adding that the BCCI would manage the arrangements in line with UK law.

## What he can and cannot do

The rule is narrower than the headlines suggest. Sooryavanshi will be allowed inside India's main dressing room during matches, and he can attend every team talk, strategy session and huddle. The restriction bites only when the squad is changing \u2014 before and after play \u2014 when he must use a separate changing room and washroom provided at each of the venues.

"This is an ICC event, with their safeguarding procedures active as they have jurisdiction," the ECB said in a statement. "A safeguarding concern occurring during the event may be managed by the ICC. In addition to this, the ECB Safe Hands policy applies at all times." The board added that its Cricket Regulator was already in contact with India's team liaison officer, and that each county venue's safeguarding officer was working through risk assessments before the squad arrives.

## Parents in the team hotel

The most striking accommodation is off the field. Sooryavanshi's parents are travelling with him for the duration of the tour and, unusually, staying in the same team hotel \u2014 a measure the ECB called "outside of usual protocol, but agreed on this occasion due to his age." The BCCI has confirmed the arrangement. "This additional measure provides us with further confidence that he has family members that can provide the additional level of support and care," the ECB said.

Cricket is new to this, but sport is not. Arsenal's teenage forward Max Dowman \u2014 like Ethan Nwaneri before him \u2014 had to use a separate changing room until he turned 16, under Premier League rules built on the same principle. Such protections grew out of decades of abuse cases in academies and dressing rooms worldwide, prompting governing bodies to adopt strict locker-room and no-isolation policies for minors. What is notable here is that India itself has no equivalent rule: Sooryavanshi shared facilities with his adult teammates throughout IPL 2026 without issue.

## A record waiting on the other side

The off-field logistics are a footnote to what could happen on it. Sooryavanshi scored 776 runs in IPL 2026, the most of any batter, and only last Sunday struck the fastest fifty in the history of List A cricket \u2014 fifty from eleven balls, for India A against Sri Lanka A at Dambulla. Should he be handed a cap in Belfast or England, he would become the youngest man ever to play for India, erasing a record Sachin Tendulkar has held since his own debut at sixteen in 1989.

India open with two T20Is against Ireland at the Civil Service Cricket Club in Stormont, Belfast, on June 26 and 28, before five T20Is in England beginning July 1 at Chester-le-Street. Both series are available to UK and Ireland viewers on Sky Sports and TNT Sports.

## Why the diaspora should care

For the Indian community across Britain and Ireland, this is the rare summer when the country's most exciting young cricketer is playing on their doorstep \u2014 in Belfast, Manchester, Nottingham, Southampton. Many families will take children to watch a 15-year-old who is barely older than the kids in the stands, and the safeguarding measures around him are a reminder that the rules protecting minors in UK sport apply to touring stars too. If Sooryavanshi walks out to bat on these grounds, diaspora fans will have a front-row seat to a record-breaking debut \u2014 and to a glimpse of the player who may define India's next decade."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Vaibhav Sooryavanshi)...")
img_caption = "India's 15-year-old batting prodigy Vaibhav Sooryavanshi, named in the T20I squad for the tours of Ireland and England."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/6/68/Vaibhav_Suryavanshi_meets_PM_Modi.jpg"
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
        {"name": "Reuters \u2014 Safeguarding rules bar 15-year-old Sooryavanshi from Indian dressing room", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "The Guardian (via Khel Now) \u2014 Why Sooryavanshi will use a separate changing room on the England tour", "url": "https://khelnow.com/cricket"},
        {"name": "Inside Sport India \u2014 Vaibhav Sooryavanshi not allowed to use India's dressing room during IND vs ENG series", "url": "https://www.insidesport.in/"},
        {"name": "ICC \u2014 England name squad for India T20I series", "url": "https://www.icc-cricket.com/"},
    ]),
    "diaspora_angle": "Britain and Ireland's Indian community gets a rare home-soil look at India's 15-year-old prodigy this summer, and the UK safeguarding rules forcing a separate dressing room show how child-protection norms apply even to touring stars \u2014 with a potential record-breaking debut on local grounds.",
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
