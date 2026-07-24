#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 16:30 UTC run.

Story: Modi and Trump held their first bilateral in 16 months on the sidelines
of the G7 summit in Evian-les-Bains, France, on June 17, 2026. Trump called it
a "very good" conversation, described Modi as a "tough negotiator," said the two
countries are "working on trade deals," and made a striking off-the-cuff defense
remark: "If they were attacked, we would be there to help them... If anybody
attacks that man, we're going to be there." The meeting came amid fresh strain
after US strikes off Oman killed three Indian sailors, tariffs, and Operation
Sindoor fallout. USTR Greer travels to India June 23-24 to finalize an interim
trade deal that India's Goyal says could be sealed by mid-July.
(Reuters, Livemint, The Hindu BusinessLine, TBS — June 17, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1630.jpg"
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=40,
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
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
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
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15, stream=True, allow_redirects=True)
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
        headers=HEADERS_SB, json=article, timeout=20,
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
    # Wikimedia Commons photo of Trump and Modi together (official U.S. gov photo, public domain).
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/"
           "President_Donald_J._Trump_and_Indian_Prime_Minister_Narendra_Modi_%2802%29.jpg/"
           "1280px-President_Donald_J._Trump_and_Indian_Prime_Minister_Narendra_Modi_%2802%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "modi-trump-g7-bilateral-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Modi-Trump G7 bilateral outcome ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "modi-trump-g7-bilateral-france-trade-deal-defend-india-20260617"

    body = """It had been sixteen months since Narendra Modi and Donald Trump last sat across from each other. When they finally did, on the sidelines of the G7 summit in the French lakeside resort of Evian-les-Bains on Wednesday, the US President emerged with the kind of remark that travels faster than any communiqué.

"If they were attacked, we would be there to help them," Trump told reporters when asked about the US-India defence relationship. "If anybody attacks that man, we're going to be there" — gesturing to Modi — before adding, with characteristic unpredictability, "Now, if there's a new leader, I'm not sure about it."

It was an extraordinary, personalised pledge of protection, and it set the tone for a meeting both sides were watching anxiously after months of friction.

## A "very good" meeting after a rough patch

Trump described the conversation as "very good" and called Modi a "tough negotiator," confirming that the two countries are "working on trade deals." He also said he would travel to India "sometime in the future" — a trip New Delhi has been pressing for, potentially as part of a wider Quad-style gathering with Japan and Australia.

The warmth mattered because the relationship had cooled sharply. Ties came under fresh strain only last week after US military strikes on three merchant vessels off the coast of Oman killed three Indian sailors. New Delhi summoned the US charge d'affaires and called the strikes "lethal and deadly" and "unacceptable," while External Affairs Minister S Jaishankar raised the deaths directly with Secretary of State Marco Rubio. Layered on top were punitive US tariffs on Indian goods and Trump's repeated claim — which India denies — that he brokered the end of India's brief conflict with Pakistan during Operation Sindoor.

## Trade: close, but not closed

A trade deal was the centrepiece of the agenda, but as US officials had signalled all week, no agreement was finalised at Evian. The two leaders instead took stock of negotiations that have been running for the better part of a year, since they agreed on a framework for an interim deal in February.

The real work now moves to New Delhi. US Trade Representative Jamieson Greer is due to visit India on June 23 and 24 for follow-up talks aimed at giving the interim pact its "final touches." India's Commerce Minister Piyush Goyal has said the first tranche could be concluded by mid-July. New Delhi is seeking preferential tariff treatment, while also wanting clarity on proposed new tariffs under a US Section 301 probe touching textiles and steel.

The stakes are concrete. India's merchandise exports rose to $45.2 billion in May, and a deal that cuts US tariffs would directly affect the competitiveness of Indian goods — and the firms, many diaspora-linked, that move them across the Pacific.

## Defence, energy and the maritime question

Beyond trade, the leaders were expected to discuss defence cooperation, energy security and the crises in West Asia and Ukraine. Modi has been pressing a maritime theme with new urgency, calling for enhanced protection of global shipping routes and stressing that seafarers must be able to work "without fear" — a pointed reference to the Indian sailors killed in the Gulf strikes.

Trump's defence remark, however informal, lands against that backdrop. The US has described India as the "cornerstone" of its Indo-Pacific strategy, and Rubio last month conveyed a White House invitation for Modi to visit "in the near future."

## Why the diaspora is watching

For Indian Americans and NRIs worldwide, this bilateral is more than diplomatic theatre. The trade deal will shape tariffs on the goods and remittance-linked businesses that connect the diaspora to home. The defence pledge speaks to a strategic alignment that frames how Indian professionals and companies are received in the US. And the maritime safety push follows the deaths of Indian crew members — a reminder that the diaspora's footprint extends to the merchant sailors who keep global trade moving.

After sixteen months of distance, tariffs and a fatal flashpoint at sea, the message from Evian was that the world's largest democracy and its oldest are still, in Trump's telling, on the same side — even if the fine print of the deal that would prove it remains unwritten."""

    return {
        "headline": "Trump Says He'll 'Be There' to Defend India as He and Modi Reset Ties at the G7",
        "subheadline": "In their first face-to-face in 16 months, Trump called Modi a 'tough negotiator,' promised to visit India, and offered an unusually personal defence pledge — even as the trade deal both sides want stayed unfinished.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "US President Donald Trump and Indian Prime Minister Narendra Modi during an earlier meeting.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The trade terms, defence alignment and maritime-safety push from this Modi-Trump meeting directly shape tariffs, professional mobility and the safety of Indian workers that bind the diaspora to home.",
        "sources": [
            "Reuters \u2014 Trump says he had good meeting with India's Modi, working on trade deals (June 17, 2026)",
            "Livemint \u2014 Modi-Trump bilateral at G7 today amid fresh strain after sailors' deaths (June 17, 2026)",
            "The Hindu BusinessLine \u2014 First in 16 months: Modi and Trump exchange pleasantries amid strained ties (June 2026)",
            "TBS/Reuters \u2014 US, India to tackle trade at G7 but deal not imminent (June 14, 2026)",
            "Reuters \u2014 India's May trade gap narrows; USTR Greer to visit India June 23-24 (June 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
