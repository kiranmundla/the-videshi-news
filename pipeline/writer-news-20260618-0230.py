#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 02:30 UTC run.

Story: The $100,000 H-1B fee is BACK — for now. On June 8, 2026, U.S. District
Judge Leo Sorokin (D. Mass.) vacated the fee as an unlawful tax. But on June 12,
2026 the same court granted the Trump administration a *temporary administrative
stay* pending appeal to the First Circuit — reinstating the fee at least through
June 18, 2026 (today). The government must file its stay request with the First
Circuit by June 18 for the pause of the vacatur to remain in effect. Case: State
of California et al. v. Noem/Mullin et al. (1st Cir. No. 26-1699). Meanwhile a
separate D.C. case (U.S. Chamber of Commerce) went the government's way and a
San Francisco case is pending — a brewing circuit split that points toward the
Supreme Court. Indians are ~70%+ of H-1B beneficiaries, so this whiplash lands
squarely on the diaspora and the employers who sponsor them.
(Sources: WR Immigration/Wolfsdorf; CSG Law; Ogletree Deakins; SHRM; Burr & Forman
— all June 2026.)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news0230.jpg"
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
    # Wikimedia Commons: the John Joseph Moakley U.S. Courthouse in Boston —
    # home of the U.S. District Court for the District of Massachusetts, where
    # Judge Sorokin both struck down and then stayed his ruling on the fee.
    # CC-licensed, permanent upload.wikimedia.org URL.
    src = ("https://upload.wikimedia.org/wikipedia/commons/"
           "1/11/2017_Moakley_US_Courthouse_from_Boston_Harbor.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "moakley-courthouse-h1b-fee-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: $100,000 H-1B fee reinstated pending appeal ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "trump-100000-h1b-fee-reinstated-administrative-stay-first-circuit-appeal-june-18-20260618"

    body = """The $100,000 H-1B fee is back — at least for now. Just days after a federal judge struck it down as an unlawful tax, the same court hit pause on its own ruling, reinstating the eye-watering surcharge on new H-1B petitions while the Trump administration appeals. For the Indian professionals who make up the overwhelming majority of H-1B applicants, it is the latest lurch in a legal saga that keeps changing the price of a future in America.

The whiplash unfolded over four days in a Boston courthouse. On June 8, U.S. District Judge Leo Sorokin vacated the fee in its entirety, ruling that President Donald Trump had no authority to impose what amounted to a tax. By June 12, the government had appealed and won a temporary reprieve that put the fee back in force — and that reprieve runs at least through today, June 18.

## A fee struck down, then revived in four days

The story begins with Proclamation 10973, which Trump signed on September 19, 2025. It imposed a $100,000 "supplemental payment" on new H-1B petitions filed for workers located outside the United States, took effect two days later, and was set to last twelve months. The administration framed it as a crackdown on a program it accused employers of using to "replace, rather than supplement, American workers with lower-paid, lower-skilled labor."

Twenty Democratic state attorneys general sued in *State of California v. Noem*. On June 8, 2026, Judge Sorokin granted them summary judgment on every claim, finding the payment was a tax that only Congress can levy, and that the agency guidance implementing it violated the Administrative Procedure Act. "Here, the substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote, citing the Supreme Court's February ruling that struck down Trump's sweeping tariffs. Crucially, he vacated the policy universally — not just for the states that sued.

The relief lasted barely three days. On June 11 the administration filed a notice of appeal to the U.S. Court of Appeals for the First Circuit, and on June 12 it asked Sorokin to stay his own order. The court declined to stay the decision on the merits but granted a *temporary administrative stay* to give the First Circuit time to weigh in. The practical effect: USCIS may keep collecting the $100,000 fee on qualifying H-1B petitions that require consular notification, at least through June 18, 2026.

## Why today matters

That date is not arbitrary. For the district court's pause to remain in effect, the government must file its stay request with the First Circuit by June 18. If the appeals court grants a stay, USCIS will likely keep collecting the fee throughout the litigation. If it denies the stay, Sorokin's June 8 order vacating the fee could spring back to life. Immigration lawyers are telling employers to budget for the fee and brace for the rules to flip again with little warning.

The Boston case is not the only front. A separate challenge by the U.S. Chamber of Commerce in Washington, D.C. went the government's way, and another suit brought by religious and labor groups is pending in San Francisco. With federal courts in three circuits potentially reaching different conclusions, immigration attorneys widely expect the question to land at the Supreme Court.

## What it means for the diaspora

No community has more riding on the outcome than Indians. People born in India have accounted for more than 70 percent of approved H-1B petitions every year since 2015, which means the diaspora absorbs the lion's share of any new cost — and the bulk of the uncertainty.

The one piece of reassurance worth repeating: the fee, as implemented, applies to *new* petitions for beneficiaries outside the United States and subject to consular processing. The Department of Homeland Security has clarified it does not hit H-1B change-of-status, extension, or change-of-employer filings. F-1 students already in the country who change status to H-1B generally remain outside its reach. For the hundreds of thousands of Indians already working in the U.S. on H-1B status, in other words, the immediate exposure is narrower than the headline number suggests.

But for employers recruiting new talent from India, and for the workers waiting abroad for a petition to clear, the math is brutal and the ground keeps shifting. A $100,000 charge can quietly end a job offer before it begins, pushing companies toward candidates who are already stateside or toward building teams in Bengaluru instead of the Bay Area. Layered on top of a weighted lottery that now favors higher salaries and expanded social-media vetting at consulates, the fee fight is one more reason the classic path — study in America, work on an H-1B, settle down — feels narrower than it did a year ago.

For now, the diaspora is left watching a docket. Until the First Circuit rules, and likely until the Supreme Court has its say, the only safe assumption is that the $100,000 question has no settled answer."""

    return {
        "headline": "Struck Down, Then Revived in Three Days: The $100,000 H-1B Fee Is Back \u2014 and Today Is the Deadline",
        "subheadline": "A Boston judge struck down Trump's $100,000 H-1B surcharge as an unlawful tax on June 8, then stayed his own ruling on June 12 to let the appeals court weigh in. The fee is being collected again at least through June 18 \u2014 and Indians, who file most H-1B petitions, are caught in the whiplash.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The John Joseph Moakley U.S. Courthouse in Boston, home of the federal district court that struck down and then stayed its ruling on the $100,000 H-1B fee.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Indians account for more than 70% of approved H-1B petitions, so the on-again, off-again $100,000 fee and its looming First Circuit and Supreme Court fights land hardest on the diaspora and the U.S. employers who sponsor them.",
        "sources": [
            "WR Immigration (Wolfsdorf Rosenthal) \u2014 Court Temporarily Reinstates USCIS Authority to Collect $100,000 H-1B Consular Processing Fee Pending Appeal (June 2026)",
            "CSG Law Alert \u2014 Administrative Stay Issued on $100,000 H-1B Fee Ruling (June 2026)",
            "Ogletree Deakins \u2014 Trump Administration Appeals Ruling Striking Down $100,000 H-1B Fee Requirement (June 2026)",
            "SHRM \u2014 Federal Court Strikes Down $100K H-1B Fee (with stay editor's note, June 2026)",
            "Burr & Forman LLP \u2014 Federal Court Vacates $100,000 H-1B Fee (June 2026)",
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
    else:
        insert_article(art)
