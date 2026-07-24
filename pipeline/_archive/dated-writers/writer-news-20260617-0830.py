#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 08:30 UTC run.

Story: At the Evian G7, Washington refused to grant even close allies a
carve-out from its new export controls that block all foreign nationals
from Anthropic's most advanced models (Fable 5, Mythos 5), which Anthropic
disabled worldwide on June 12. UK PM Starmer's request for a British
carve-out was rejected as "completely illogical." The ban has reignited
India's sovereign-AI debate (Vembu, Pai, Nilekani, Chandrasekaran; IndiaAI
Mission's 12 foundation-model picks; Sarvam/HCLTech). Hits Indian engineers,
GCCs and startups that lean on US frontier models. (Reuters, NY Post,
Outlook Business/Moneycontrol — Jun 13-16, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    """Wikimedia rate-limits Python requests (429) but serves curl fine."""
    try:
        out = "/tmp/_videshi_hero.jpg"
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
    # On-topic Commons photo: PM Modi at a G7 summit (Prime Minister's
    # Office, India; GODL-India). Accurate context for a G7 / India-AI story.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/"
           "51st_G7_Summit.jpg/1280px-51st_G7_Summit.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "g7-summit-india-ai-export-controls-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: US AI export controls / India sovereign-AI debate ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "us-ai-export-controls-anthropic-g7-india-sovereign-ai-debate-20260617"

    body = """When the leaders of the world's seven richest democracies sat down to dinner in the French lakeside town of Evian this week, one of the first arguments was not about Iran or Ukraine. It was about who is allowed to use America's smartest computers. And the answer Washington gave its closest friends — for now — was no.

On June 12, the US Commerce Department ordered Anthropic, the maker of the frontier models Mythos 5 and Fable 5, to block all foreign nationals from using them, whether those people sit in Bengaluru, London or a cubicle inside Anthropic's own San Francisco offices. Unable to fence the models off to American users alone, Anthropic switched both off worldwide. By the time the G7 convened, its most advanced systems were dark for everyone.

## "Completely illogical"

The freeze landed hardest on allies who assumed friendship bought access. British Prime Minister Keir Starmer asked for a carve-out so UK nationals and companies could keep using the models, a request first reported by the Telegraph. A Trump administration official told the New York Post that granting even a G7 ally an exemption would be "completely illogical." Another put it more bluntly: "We can't have frontier models running amok." The stated worry is a "jailbreak" that could let the models hunt for software vulnerabilities — a national-security risk Washington says it will not export, not even to London.

At the summit, several delegations pressed US Commerce Secretary Howard Lutnick on a "trusted partners" framework that might restore access for select countries or firms, according to Reuters. White House officials say they are negotiating directly with Anthropic chief executive Dario Amodei. But as of this week, no carve-out exists, and Europe left Evian newly alarmed about how completely it depends on American AI.

## Why this is India's problem too

India was not in the room when the ban was written, but few countries are more exposed to it. The Indian AI market is dominated by American providers — Microsoft, Google, OpenAI and Anthropic among them — and the country's vast IT and global-capability-center workforce has built much of its recent AI ambition on top of US frontier models it does not own. When Washington flips a switch, Indian engineers, startups and enterprises lose tools overnight, with no domestic substitute of equal power to fall back on.

That dependence is the uncomfortable subtext of the past week. A foreign national on an H-1B visa inside an American AI lab was cut off from the very models their team builds. Indian startups that wired Mythos or Fable into their products had to scramble. And the episode arrived just as India is trying to prove it can stand on its own in AI.

## The sovereign-AI debate reignites

In New Delhi, the ban reopened an argument the technology industry has been having for two years. Zoho founder Sridhar Vembu was among the sharpest voices, writing on X that "technology is the ultimate weapon" and that "globalization is dead and Bharat must find her own way ahead," urging Indian firms toward smaller, open-source and homegrown models. Former Infosys finance chief Mohandas Pai, Lightspeed's Hemant Mohapatra and other investors echoed the warning about leaning on platforms a foreign government can switch off.

Not everyone agrees India should chase frontier models of its own. Infosys co-founder Nandan Nilekani and Tata Sons chairman N. Chandrasekaran have argued the bigger prize lies in building AI-powered applications and enterprise solutions rather than competing to train the world's largest model. Either way, the policy machinery is already moving: earlier this year the government picked 12 companies under the IndiaAI Mission to build indigenous foundation models, the country's biggest bet yet on sovereign large language models. Among the contenders, Sarvam AI is in advanced talks to raise fresh capital, with HCLTech reportedly set to put in $150 million as part of a $300 million round.

For the millions of Indians who work in technology at home and across the diaspora, the lesson of Evian is stark. The most valuable tools of this decade can be revoked by a directive they have no vote in. Whether India's answer is to build its own frontier models or to get very good at deploying everyone else's, the week made the stakes unmistakable: in the age of AI, access is sovereignty — and right now, India is renting."""

    return {
        "headline": "Washington Just Cut Off Its Closest Allies From Its Best AI. For India, the Lesson Is Brutal.",
        "subheadline": "After the US barred all foreign nationals from Anthropic's frontier models and refused even Britain a carve-out at the G7, India's reliance on American AI has reignited a fierce debate over building its own.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi at a G7 summit; India was among the countries left exposed by new US controls on frontier AI models.",
        "image_attribution": "Prime Minister's Office (India), GODL-India, via Wikimedia Commons",
        "diaspora_angle": "India's tech workforce at home and across the diaspora — including H-1B engineers inside American AI labs and the GCCs and startups built on US frontier models — lost access overnight, exposing how completely Indian AI ambition rents capability it does not own.",
        "sources": [
            "Reuters \u2014 G7 leaders discuss 'trusted partners' access to cutting-edge US AI models, sources say (June 16, 2026)",
            "New York Post \u2014 Trump officials won't allow G7 countries to access Anthropic's most advanced AI models: 'Completely illogical' (June 16, 2026)",
            "Outlook Business / Moneycontrol \u2014 US Blocks Foreign Access to Advanced AI Models, Putting India's AI Strategy Under Spotlight (June 14, 2026)",
            "Reuters \u2014 Europe frets about U.S. AI as tech world flocks to France for G7, VivaTech (June 16, 2026)",
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
