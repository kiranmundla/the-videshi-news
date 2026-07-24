#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (01:45 UTC slot / videshi-writer-sports retry)

Article: Manika Batra — India's most decorated active women's table tennis
player — was left OUT of India's main squad for the 2026 Asian Games
(Aichi-Nagoya, Sep 19 - Oct 4), named only as a reserve. The Table Tennis
Federation of India (TTFI) used a formula weighting national rankings 50%,
world rankings 40%, selection-committee discretion 10%. Batra, world No. 27
(India's No. 2) but with NO domestic ranking due to skipping national events,
fell below the cut. She publicly appealed to PM Modi, the Sports Minister and
the IOA on X for transparency. Sreeja Akula (world No. 45) leads the women's
team; squad also has Yashaswini Ghorpade, Diya Chitale, Sutirtha Mukherjee,
Syndrela Das; Swastika Ghosh + Batra are reserves. Men led by G Sathiyan.

DEDUP: Checked last 3 days of sports — covered: ETPL launch, Glasgow CWG
contingent, women's hockey, women's T20 WC v SA, post-Kohli ODIs/Test, MLC
run-fests, FIFA WC recaps, Neeraj Doha, Kohli England recall, US Open tennis.
Manika Batra / table tennis / Asian Games selection is FRESH and UNCOVERED.

ANGLE: A selection-criteria controversy involving one of India's biggest
Olympic-sport names, with a clean diaspora hook — Batra is a globally
recognized face of Indian table tennis, and the row over rankings vs. merit
resonates with NRIs who follow India's Olympic-sport rise.

Hero: Wikipedia REST API portrait of Manika Batra (verified, Arjuna Award
2018 photo, Wikimedia Commons CC). Person article → Wikipedia first.
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
            # Use thumbnail.source AS-IS (330px) per image rules; original as larger option
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = thumb or orig
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
print("ARTICLE: Manika Batra left out of Asian Games squad")
print("="*60)

art_slug = "manika-batra-left-out-india-asian-games-2026-squad-table-tennis-selection-row-ttfi-ranking-rule-pm-modi-appeal-diaspora"
art_headline = "India's Most Famous Paddler Was Just Left Off the Asian Games Team — Over a Ranking She Never Had"
art_subheadline = "Manika Batra, the world No. 27 and the face of Indian table tennis, has been named only a reserve for the Asian Games because she skipped domestic events. Her public appeal to the Prime Minister has reopened an old fight over how India picks its athletes."

art_body = """Manika Batra is, by some distance, the most recognisable name in Indian table tennis. She is a double Commonwealth Games gold medallist, an Asian Games bronze medallist, an Olympian, and — at world No. 27 — India's second-ranked woman on the international circuit. So when the Table Tennis Federation of India (TTFI) named its squad for the 2026 Asian Games in Aichi-Nagoya, Japan, the most striking name was the one missing from the main list. Batra was relegated to the reserves.

Her response was not quiet. Within a day she went to X to call the decision "deeply disheartening, with no specific reason communicated," and did something Indian athletes rarely do in public: she escalated it straight to the top, requesting that "the Hon'ble Prime Minister, Hon'ble Sports Minister and Indian Olympic Association look into the matter and ensure transparency and fair application of selection norms." For a sport that usually fights its battles behind closed doors, it was an extraordinary appeal.

## The Rule That Sank Her

The maths, on paper, is straightforward. The TTFI says it picked the squad using a fixed formula: 50 per cent weight to a player's national ranking, 40 per cent to world ranking, and 10 per cent to the selection committee's discretion. Batra's problem is the first and largest of those buckets. By skipping recent domestic tournaments, she no longer holds an official national ranking — and without it, half of the selection score effectively reads as zero. Her elite world ranking, worth 40 per cent, was not enough to drag her back above the cut line.

That is how a player ranked 27th in the world ends up behind teammates ranked lower internationally. Sreeja Akula, India's top-ranked woman at world No. 45, will captain the side. The squad also features Yashaswini Ghorpade, Diya Chitale, Sutirtha Mukherjee and Syndrela Das, with Swastika Ghosh and Batra named as reserves. The men's team will be led by G. Sathiyan, alongside Harmeet Desai, Manav Thakkar, Manush Shah and Payas Jain.

## Letter Versus Spirit

Batra's central charge is not that the rule was broken, but that it was applied inconsistently. "Questions arise on consistency, as different thresholds and considerations were applied in the previous selection cycle compared to my case," she wrote, arguing that the same standard was not used across cycles. The federation's defenders counter that a published, weighted formula is precisely what athletes have demanded for years — an objective system that does not bend for big names. Skip the domestic grind, the logic goes, and you forfeit the points it earns, however many medals you have on the shelf.

It is a genuinely hard case, and that is what makes it interesting. On one side is the principle that no athlete should be bigger than the criteria. On the other is the obvious risk in a system that can leave your best available player at home for a continental championship on a technicality. India goes to Aichi-Nagoya — the 20th Asian Games, running September 19 to October 4 — chasing medals in a discipline where it has only recently become competitive. Doing so without its most decorated active woman is a real cost, whatever the rulebook says.

## Why It Travels

For the diaspora, this is more than a domestic selection spat. Manika Batra is one of the handful of Indian Olympic-sport athletes who broke through to genuine global recognition — the player who beat world No. 4 Feng Tianwei at the 2018 Commonwealth Games and turned table tennis, briefly, into back-page news in a cricket-soaked country. NRIs who have watched India slowly build depth in Olympic sports tend to follow names like hers closely, because they represent the part of Indian sport that exists beyond the IPL economy.

The deeper resonance is about fairness and process — themes that travel well in diaspora communities built on the idea of merit. Indians abroad have spent decades navigating systems where rules and rankings decide outcomes, and the Batra row lands on a familiar nerve: when does a transparent rule become a blunt instrument, and who gets to override it? Her appeal to the Prime Minister has guaranteed that the question will not be settled quietly.

## What Happens Next

As a reserve, Batra is not fully out; an injury or withdrawal could still pull her into the squad before the September deadline. But the larger fight is now about the criteria themselves, and whether the TTFI or the sports ministry revisits how heavily a missing domestic ranking should count against proven international pedigree. For now, India's most famous paddler is on the outside of its biggest team of the year — and she has made sure everyone, all the way up to the Prime Minister, knows it."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person article)...")
img_caption = "Manika Batra receiving the Arjuna Award in 2018"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Manika Batra")
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
    "vertical": "table-tennis",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Mint \u2014 Asian Games 2026: Manika Batra urges PM Modi, Sports min to intervene after her exclusion", "url": "https://www.livemint.com/sports"},
        {"name": "Dainik Bhaskar (English) \u2014 Manika Batra Asian Games 2026 Snub: PM Modi Intervention Urged", "url": "https://www.bhaskarenglish.in/sports"},
        {"name": "SportsTak \u2014 Manika Batra shockingly left out of India's Asian Games 2026 squad", "url": "https://www.thesportstak.com/table-tennis"},
        {"name": "ANI \u2014 TTFI selection criteria for Aichi-Nagoya Asian Games squad", "url": "https://www.aninews.in/topic/table-tennis"},
    ]),
    "diaspora_angle": "Manika Batra is one of the few Indian Olympic-sport athletes with genuine global recognition, and the row over whether a transparent ranking rule should override proven international pedigree strikes a familiar chord with NRIs who follow India's Olympic-sport rise and value merit-based process.",
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
