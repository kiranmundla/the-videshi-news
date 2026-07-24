#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 12:30 UTC run.

Story: India has quietly rewritten one of the oldest rules governing how
NRIs invest in Indian stocks. RBI Governor Sanjay Malhotra announced on
June 5 (MPC) that the per-company cap for NRIs/OCIs in a listed Indian
company is being doubled from 5% to 10%, and the aggregate NRI ceiling
raised from 10% to 24% — and the Finance Ministry's June 12 FEMA (Non-Debt
Instruments) Third Amendment opened the Portfolio Investment Scheme to ALL
"individual persons resident outside India," not just NRIs/OCIs. This is a
direct, practical NRI-money story: most diaspora investors barely use the
old limits (NRI ownership = 0.7% of Sensex cap), but experts say it removes
a friction point — provided KYC/tax/repatriation processes are simplified.
(Outlook Money, IANS, Hindu BusinessLine, Livemint, SCC Online — Jun 5-16, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1230.jpg"
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
    # Bombay Stock Exchange building — accurate, permanent Commons photo.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/"
           "BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "nri-equity-investment-limits-rbi-fema-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: India doubles NRI equity investment limits ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "india-doubles-nri-oci-equity-investment-limits-fema-portfolio-scheme-20260617"

    body = """For decades, the rules that governed how an overseas Indian could buy shares in an Indian company carried a quiet ceiling. Under the Portfolio Investment Scheme (PIS), a single non-resident Indian or Overseas Citizen of India could own no more than 5% of a listed company's paid-up capital, and all NRIs put together could not cross 10%. Cross that line and the regulator took notice. This month, New Delhi tore down half of that wall.

In a back-to-back set of moves, the Reserve Bank of India and the Finance Ministry have doubled the individual cap, raised the aggregate ceiling, and — most significantly — thrown the scheme open to every individual living outside India, not just those with an Indian passport or OCI card. For the global diaspora that has long treated Indian equities as a sentimental side-allocation rather than a serious one, the message is that the door has been widened.

## What actually changed

The shift came in two parts. On June 5, on the concluding day of the Monetary Policy Committee meeting, RBI Governor Sanjay Malhotra announced that the limits for NRI and OCI investment in stock-market equity instruments — held without separate SEBI registration — were being increased. A week later, on June 12, the Finance Ministry notified the Foreign Exchange Management (Non-Debt Instruments) Third Amendment Rules, putting the change into law.

The practical numbers: the individual per-company holding limit for an NRI or OCI doubles from 5% to 10%, while the aggregate ceiling for all overseas individual investors together rises from 10% to 24% of a listed company's paid-up capital. Breaches must be corrected within a prescribed window, failing which the holding is reclassified as foreign direct investment.

The amendment's most sweeping line is also its least noticed. The rulebook's old heading — "Investment by a Non-Resident Indian or an Overseas Citizen of India" — has been replaced with "Investment by an individual person resident outside India including a non-resident Indian or an overseas citizen of India." In plain terms, the Portfolio Investment Scheme is no longer reserved for the diaspora; any foreign individual can now use it on a repatriation basis, subject to conditions.

## Why now

The timing is not accidental. Foreign portfolio investors have been pulling money out of Indian equities at a punishing pace — more than ₹62,000 crore in June alone, against the backdrop of the Gulf conflict and a strong dollar. With the current account under strain, the government and central bank have rolled out a clutch of measures to court foreign capital: absorbing hedging costs on FCNR deposits, expanding the forex swap window, widening access to government securities, and now easing equity limits for overseas investors. Diaspora savings are being recruited as ballast.

## The catch experts keep flagging

Here is the sobering footnote. NRIs have barely used the limits they already had. NRI ownership stood at a negligible 0.7% of Sensex market capitalisation as of the quarter ending March 2026, and total diaspora holdings of roughly ₹5.2 lakh crore are a sliver of India's ₹461 lakh crore market. Raising a ceiling that almost no one was bumping against will not, on its own, unleash a flood.

"It is a step in the right direction, but needs to be complemented by simple and digital processes related to KYC, taxation, repatriation, etc., for significant inflows to materialise," said Nilesh Shah, managing director at Kotak Mahindra Asset Management. Others called it a "battle half won" — the limits are generous, but the paperwork, the tax friction, and the repatriation rules remain the real obstacles for a doctor in New Jersey or an engineer in Dubai who simply wants to buy a basket of Indian blue-chips.

## What it means for the diaspora

For NRI investors, the change is best read as an invitation rather than an instant opportunity. It removes a structural cap that occasionally tripped up larger family-office and high-net-worth holdings, and it signals that India wants diaspora money in its public markets, not just in real estate and fixed deposits. The RBI has said it will issue exact timelines for implementation, so the mechanics are still being finalised.

The deeper significance is symbolic. By folding NRIs into a broader category of "persons resident outside India," India is treating its diaspora less as a special-status group and more as one channel within a wider push to liberalise its capital account. For a community that sends record remittances home each year, the next test is whether the friction that has kept diaspora equity ownership at under 1% finally gets cleared away — or whether this remains, as the experts warn, a reform on paper waiting for the plumbing to catch up."""

    return {
        "headline": "India Just Doubled How Much NRIs Can Own in Its Stock Market — and Opened the Door to Everyone Else",
        "subheadline": "A new FEMA amendment raises the per-company cap for overseas Indians from 5% to 10% and the aggregate ceiling to 24%, but with NRI ownership at just 0.7% of the Sensex, experts say the paperwork still matters more than the limits.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The Bombay Stock Exchange building in Mumbai, home to India's benchmark Sensex index.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The reform directly affects how the global Indian diaspora can invest in Indian equities, doubling individual holding caps and opening the Portfolio Investment Scheme to all overseas individuals just as India courts foreign capital.",
        "sources": [
            "Outlook Money \u2014 RBI Proposes Higher Investment Limits in Equity Instruments for NRIs, OCIs, and Other Overseas Indians (June 5, 2026)",
            "IANS \u2014 RBI hikes equity investment limits for NRIs, OCIs (June 5, 2026)",
            "The Hindu BusinessLine \u2014 Finmin widens definition of overseas individual investors participating in capital markets (June 12, 2026)",
            "SCC Online \u2014 FEMA Third Amendment Rules 2026: Key Highlights (June 2026)",
            "Livemint \u2014 RBI move to raise foreign capital from NRIs a battle half won (June 2026)",
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
