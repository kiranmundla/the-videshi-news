#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (16:30 UTC slot / videshi-writer-sports)

Article: India holds its FIRST-EVER Indian Athletics Awards (inaugural AFI
ceremony, New Delhi, Sat June 20, 2026). Neeraj Chopra named Best Male Athlete
of the Year 2025, Parul Chaudhary Best Female Athlete. A milestone for a
federation trying to institutionalize recognition for a sport India is finally
winning at beyond cricket — set against Neeraj's emotional, just-flew-in-from-
Doha appearance as he rebuilds from a back injury toward Glasgow and the Asiad.

DEDUP CHECK (vs recent feed, last ~4 days of sports):
- Sports feed is cricket-heavy (England/India squads, Headingley Test, women's
  T20 World Cup, Pant trade, MLC, Vaibhav Sooryavanshi) plus athletics one-offs:
  Animesh Kujur sprinter profile (Jun 24), women's 4x100m relay gold (Jun 24),
  Jagmeet Singh basketball (Jun 24), Asian fencing + Bhavani Devi (Jun 24),
  para-badminton youth games (Jun 23), Manika Batra TT (Jun 22).
- The INAUGURAL INDIAN ATHLETICS AWARDS and NEERAJ CHOPRA's Best Male Athlete
  honour appear NOWHERE in the feed. Wholly uncovered. (The relay-gold article
  is a separate event; this is the AFI awards night.)

Key facts (ANI/PTI via Tribune, myKhel, Khel Ja, Daily Prabhat — June 20-21, 2026):
- Athletics Federation of India (AFI) hosted the INAUGURAL Indian Athletics
  Awards on Saturday, June 20, 2026, in New Delhi.
- Neeraj Chopra: Best Male Athlete of the Year 2025.
- Parul Chaudhary (3000m steeplechase national record holder, long-distance
  runner): Best Female Athlete of the Year 2025.
- Shahnavaz Khan and Pooja: Best Emerging Athletes (men's / women's).
- Lifetime Achievement Awards: P.T. Usha (IOA president, legendary sprinter),
  Anju Bobby George, Gurbachan Singh Randhawa, Bahadur Singh Chauhan.
- Awards presented by Union Minister for Youth Affairs and Sports Dr. Mansukh
  Mandaviya. Present: World Athletics VP Adille J. Sumariwalla, Sri Lanka
  Athletics President Korottage Bimal Prasanna, Maldives Sports Commissioner
  Mohamed Tholal. AFI President: Bahadur Singh Sagoo.
- Neeraj quote: "Yeh award dil ke nazdik hai" (this award is very close to my
  heart) — special because received in front of old and new generations of
  athletes. He flew in from Doha earlier that day.
- Neeraj context: flew in after the Doha Diamond League (Fri June 19), his
  2026 SEASON OPENER and first competition after ~8 months out with a back
  injury. Threw 85.69m (best, 3rd attempt) to finish FOURTH; one foul on the
  opening attempt. Comfortably cleared the AFI's 82.61m Commonwealth Games
  qualification mark.
- He had finished 8th at the World Championships in Tokyo (Sept 2025) carrying
  the injury; trained in Switzerland since May 25 after a rehab stint in Turkiye.
- 2025 season: breached the 90m barrier for the FIRST TIME (90.23m, Doha,
  2nd place); topped the Paris Diamond League standings; won the NC Classic in
  Bengaluru.
- Career: Tokyo 2020 Olympic GOLD, Paris 2024 Olympic SILVER, former World
  Champion. India's biggest medal hope at the Commonwealth Games (Glasgow,
  July-Aug 2026) and the Asian Games (Japan, Sept-Oct 2026), fitness permitting.

DIASPORA ANGLE: Neeraj Chopra is the rare Indian sporting icon who is NOT a
cricketer — the single most globally recognized face of India's Olympic
ambitions, a unifying figure across a diaspora that follows him from Tokyo to
Paris. An inaugural national awards night signals India finally building
institutions of recognition for athletics, the discipline the diaspora's
children actually compete in at schools and colleges abroad (track and field is
a mainstay of US/UK/Canada school sport). And Neeraj's message — that Indians
have the capability to match Europeans and Americans — speaks directly to
second-generation kids being told the same.

Hero: Wikipedia/Wikimedia Commons photo of Neeraj Chopra (real photo of the
named athlete). Pexels/generic stock NOT used (rules forbid generic stock for a
named athlete).
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
print("ARTICLE: Inaugural Indian Athletics Awards + Neeraj Chopra")
print("="*60)

art_slug = "inaugural-indian-athletics-awards-afi-neeraj-chopra-best-male-athlete-parul-chaudhary-pt-usha-lifetime-achievement-new-delhi-2026-diaspora-nri"
art_headline = "India Finally Gave Its Track Stars a Night of Their Own \u2014 and Neeraj Chopra Owned It"
art_subheadline = "At the inaugural Indian Athletics Awards in New Delhi, the Olympic javelin champion was named Best Male Athlete of 2025 \u2014 hours after flying in from his injury comeback in Doha \u2014 as India's federation set out to build a culture of recognition for the sport it now wins at beyond cricket."

art_body = """For a country whose sporting heart beats almost entirely to cricket, Saturday night in New Delhi was a small act of correction. The Athletics Federation of India (AFI) staged the inaugural Indian Athletics Awards \u2014 the first time the country has set aside an evening purely to honour the men and women who run, jump and throw for it \u2014 and the biggest name in the room was, fittingly, the man who has done more than anyone to make track and field matter in India.

Neeraj Chopra was named Best Male Athlete of the Year 2025. Long-distance runner Parul Chaudhary, the national record holder in the 3000m steeplechase, took the Best Female Athlete award. The honours were presented by Union Minister for Youth Affairs and Sports Dr. Mansukh Mandaviya, in the presence of World Athletics Vice President Adille J. Sumariwalla and a galaxy of Indian athletics royalty.

## A Champion Who Flew In to Be There

Chopra very nearly was not in the room. He had landed in Delhi only hours earlier, straight from the Doha Diamond League the night before, and the emotion of the occasion was plain. "Yeh award dil ke nazdik hai," he said \u2014 this award is very close to my heart \u2014 explaining that it meant more because he received it surrounded by athletes of both the old and new generations of Indian sport.

That his presence felt like a gift owed something to the year he has just endured. The 28-year-old missed roughly eight months with a back injury, an absence that included a deflating eighth-place finish at the World Championships in Tokyo last September. The Doha meet on Friday was his 2026 season opener and his first competition since. He fouled his opening attempt, then found his rhythm to throw 85.69m and finish fourth \u2014 a modest mark by his towering standards, but one that comfortably cleared the AFI's 82.61m qualification cut for next month's Commonwealth Games.

It was, in other words, the throw of a man rebuilding rather than dominating \u2014 and that made the timing of the award feel less like a coronation than a vote of confidence. The recognition was for 2025, a season in which Chopra finally breached the mythical 90-metre barrier for the first time, hurling 90.23m in Doha, topping the Paris Diamond League standings and winning the NC Classic in Bengaluru.

## The Federation Tries to Build a Culture

The awards themselves matter beyond who won them. India has long lacked the institutional scaffolding that turns isolated medals into a sustained sporting culture \u2014 the dinners, the honours, the public memory that tells a young athlete the country is watching. By instituting an annual awards night, the AFI is trying to manufacture exactly that.

The evening leaned hard into continuity. Lifetime Achievement Awards went to four giants of Indian athletics: P.T. Usha, the legendary sprinter who now serves as president of the Indian Olympic Association; long-jump pioneer Anju Bobby George; and the decathlete-era veterans Gurbachan Singh Randhawa and Bahadur Singh Chauhan. Shahnavaz Khan and Pooja were named the Best Emerging Athletes, a nod to the pipeline the federation hopes will eventually replace the stars on stage.

"Indian athletics has witnessed unprecedented growth over the last decade, with our athletes delivering world-class performances on the biggest stages," Mandaviya said. AFI President Bahadur Singh Sagoo framed the awards as deliberately inclusive: "From athletes and coaches to technical officials, every stakeholder plays a vital role in our journey."

## Why the Diaspora Should Watch

For Indians abroad, Chopra occupies a singular place. He is the rare Indian sporting icon who is not a cricketer \u2014 the face the diaspora follows from Tokyo to Paris, the proof that India can stand on an Olympic podium in a discipline the rest of the world treats as its own. And track and field is not abstract to diaspora families: in the United States, Britain and Canada, athletics is a mainstay of school and college sport, the very arena where second-generation Indian kids actually compete.

That is what gives Chopra's recurring message its weight. "We Indians think that Europeans or Americans are stronger," he said at the ceremony, "but I feel we have the capability within us to achieve anything." It is a sentiment aimed at the youth back home, but it lands just as squarely with a diaspora teenager lining up against the field at a county or state meet.

The road ahead is demanding. Chopra is India's biggest medal hope at the Commonwealth Games in Glasgow in July and August, and again at the Asian Games in Japan in September and October \u2014 provided his back holds. A first national awards night cannot guarantee any of that. But it is a statement of intent: that India intends to remember its athletes, not just its cricketers, and to build the kind of recognition that makes the next Neeraj Chopra believe the climb is possible."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia \u2014 Neeraj Chopra)...")
img_caption = "Olympic javelin champion Neeraj Chopra, named Best Male Athlete of the Year 2025 at the inaugural Indian Athletics Awards in New Delhi."
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Neeraj Chopra")
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
        {"name": "Tribune India / ANI \u2014 Neeraj Chopra, Parul Chaudhary honoured by AFI", "url": "https://www.tribuneindia.com/news/sports/"},
        {"name": "myKhel \u2014 Indian Athletics Awards full winners list", "url": "https://www.mykhel.com/"},
        {"name": "Wikipedia \u2014 Neeraj Chopra", "url": "https://en.wikipedia.org/wiki/Neeraj_Chopra"},
        {"name": "Athletics Federation of India", "url": "https://indianathletics.in/"},
    ]),
    "diaspora_angle": "Neeraj Chopra is the rare Indian sporting icon who is not a cricketer \u2014 the most globally recognized face of India's Olympic ambitions and a unifying figure the diaspora follows from Tokyo to Paris. India's first-ever athletics awards night signals the country building institutions of recognition for track and field, the discipline diaspora children actually compete in at schools and colleges across the US, UK and Canada \u2014 and Chopra's message that Indians can match the world's best speaks directly to those kids.",
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
