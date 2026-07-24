#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 10:30 UTC run.

Story: On June 18, 2026, PM Modi landed in Paris for the final leg of his
Europe trip (after the G7 in Evian and a Slovakia visit). The Paris programme:
an address at VivaTech 2026 (Europe's largest tech/startup conference, India
has the largest national pavilion) alongside President Macron, plus a community
address to the Indian diaspora. Modi posted on X that he was "proud of the
Indian community's efforts in bringing India and France closer." India-France
marks 25 years of strategic partnership (since 1998), spanning defence, space,
nuclear, AI, semiconductors. Diaspora angle: ~119,000 Indians in mainland
France + 350,000+ PIO in French overseas territories; France's 5-year Schengen
short-stay visa for Indian graduates of French institutions (Masters+) and UPI
launch in France make this a mobility/skilled-migration story. The diaspora is
being positioned as the bridge of the relationship.
Sources: Nation Press, narendramodi.in, Livemint, ORF/NDTV, Embassy of India Paris.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1030.jpg"
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=60,
        )
        if r.stdout.strip().endswith("200") and os.path.exists(out):
            with open(out, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print("  curl_download err", e)
    return None


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env(os.path.expanduser("~/.env.supabase"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=40)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        print(f"  \u274c Upload failed ({r.status_code}): {r.text[:200]}")
        return None
    except Exception as e:
        print("  upload err", e)
        return None


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(8000)
        r.close()
        return r.status_code == 200 and "image" in ct and len(chunk) > 5000
    except Exception as e:
        print("  validate err", e)
        return False


def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB, json=article, timeout=25,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  \u2705 Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  \u2705 Inserted (raw): {r.text[:120]}")
        return data
    print(f"  \u274c Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def source_hero_image():
    # Wikimedia Commons: Modi and Macron waving to a crowd in France — the
    # exact diaspora-facing imagery this article is about.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/"
           "Prime_Minister_of_Bharat_Shri_Narendra_Damodardas_Modi_and_"
           "President_of_France_Mr._Emmanuel_Macron_wave_to_the_crowd.jpg/"
           "1280px-Prime_Minister_of_Bharat_Shri_Narendra_Damodardas_Modi_and_"
           "President_of_France_Mr._Emmanuel_Macron_wave_to_the_crowd.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "modi-macron-france-diaspora-paris-vivatech-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Modi in Paris, diaspora as the bridge ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "modi-paris-vivatech-2026-france-indian-diaspora-bridge-20260618"

    body = """When Narendra Modi's plane touched down in Paris on Thursday, the first people he thanked were not French ministers. They were Indians. "Reached Paris a short while ago to a warm welcome by the Indian diaspora," the prime minister wrote on X. "I am proud of their efforts in bringing India and France closer. The India-France partnership is vital for the progress of our planet."

It was a telling choice of words to open the final leg of a week-long European tour. After the G7 summit in Evian and a historic stop in Slovakia, Modi arrived in the French capital for two set-piece events: an address at VivaTech 2026, one of Europe's largest technology and startup conferences, and a community gathering with the Indian community in France. The diplomacy in Paris runs on two tracks at once — the boardroom and the banquet hall — and the diaspora sits squarely at the intersection.

## The pavilion and the podium

At VivaTech, India is not a guest. It is the headline act, fielding the largest national pavilion at this year's edition and using Modi's appearance alongside President Emmanuel Macron to pitch the country as a destination for European capital and a partner for European technology firms. Indian prime ministers have used this stage before to showcase the country's digital public infrastructure — the UPI payments rail, the Aadhaar identity system, the startup boom — and the 2026 outing is built to do the same, this time framed around artificial intelligence, semiconductors, and clean energy.

The timing is deliberate. France and India are marking 25 years of a strategic partnership that dates to 1998 and now spans defence co-development, space, civil nuclear energy, and a fast-growing technology agenda. Earlier this year, France hosted the AI Impact Summit with India as co-chair, and Paris has emerged as one of New Delhi's most reliable partners in a Europe that is itself recalibrating its ties to both Washington and Beijing.

## Why the diaspora is the headline, not the footnote

For the roughly 119,000 people of Indian origin in mainland France — and the more than 350,000 who live in France's overseas territories — Modi's visit is more than a photo opportunity. The French government has spent the past two years quietly building the scaffolding of a mobility relationship with India. It launched a five-year validity short-stay Schengen visa for Indians who hold a Master's degree or higher from French institutions, a meaningful concession at a time when European countries are competing with Australia and Canada for Indian students and skilled workers. India, in turn, launched its UPI payment system in France, letting Indian travellers and residents pay in euros the way they would in rupees.

These are not abstractions. They are the plumbing of a life lived across two countries — the student who can now return to France without re-applying for a visa each time, the professional weighing a posting in Paris over one in Toronto, the family sending money home. As India assembles a web of trade and mobility arrangements across the West, France has positioned itself as one of the more welcoming doors, and the diaspora is both the beneficiary and, in Modi's framing, the engine.

## A pattern, not a one-off

Modi's Paris stop fits a template India has refined since 2019: use multilateral summits to project New Delhi as a voice of the Global South, then convert that visibility into bilateral wins and direct diaspora outreach. At Evian, he pressed India's case on governance, AI rules, and development finance. In Paris, he turns to the people who carry the relationship between official visits — the engineers, founders, doctors, and students whose daily lives stitch the two countries together.

The substance to watch will be any technology or startup collaboration announced from the VivaTech stage, and whether the diaspora address yields fresh commitments on visas, recognition of qualifications, or community welfare. But the message was already clear the moment Modi landed and chose to thank the crowd first. In the modern Indian playbook, the diaspora is not the soft, sentimental edge of foreign policy. It is the bridge — and increasingly, the strategy."""

    return {
        "headline": "Modi Lands in Paris and Thanks the Diaspora First. That Choice Was the Whole Point.",
        "subheadline": "On the final leg of his Europe tour, the PM addresses VivaTech 2026 alongside Macron and the Indian community in France \u2014 where new visa and payment links are quietly rewiring how NRIs move between the two countries.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi and French President Emmanuel Macron wave to a crowd during a visit to France.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "France's five-year Schengen visa for Indian graduates of French institutions and the launch of UPI in France are reshaping how the ~119,000 Indians in mainland France and 350,000+ PIO in French territories live, study, and move between the two countries.",
        "sources": [
            "Nation Press \u2014 PM Modi in Paris: Proud of diaspora bridging India-France ties (June 18, 2026)",
            "narendramodi.in \u2014 PM's visit to France, Slovakia and the G7 Summit (June 2026)",
            "Livemint \u2014 PM Modi to attend G7 Summit in France; final leg in Paris for VivaTech 2026 (June 2026)",
            "ORF / NDTV \u2014 Modi In France: Celebrating The Past, Preparing For The Future (June 2026)",
            "Embassy of India, France & Principality of Monaco (eoiparis.gov.in) \u2014 Registration for PM's address to the Indian community, June 18, 2026",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    hl = len(art["headline"])
    print(f"  headline chars: {hl}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    elif len(art["headline"]) > 200:
        print("  \u274c headline too long, aborting")
    else:
        insert_article(art)
