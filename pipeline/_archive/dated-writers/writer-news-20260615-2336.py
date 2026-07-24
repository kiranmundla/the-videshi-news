#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-15 late run (Opendoor/AI offshoring)."""

import json, os, time
from datetime import datetime, timezone
import requests


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

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"


def validate_get(url):
    """GET-based validation (HEAD fails on upload.wikimedia.org)."""
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
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB, json=article, timeout=20,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✅ Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  ✅ Inserted (raw): {r.text[:120]}")
        return data
    print(f"  ❌ Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def article_opendoor():
    print("\n═══ Article: Opendoor India shutdown / AI offshoring ═══")

    # Sourced from Wikimedia Commons (Sasken HQ, Bengaluru), re-hosted on Supabase
    # storage for a permanent URL (Wikimedia 429s Python requests at insert time).
    img_url = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/opendoor-india-bengaluru-gcc-20260615.jpg"
    img_caption = "A technology company's headquarters in Bengaluru, India's GCC capital"
    img_attr = "Wikimedia Commons"
    if not validate_get(img_url):
        print("  ⚠ primary image failed validation")
        img_url = None

    slug = "opendoor-shuts-india-operations-ai-native-offshoring-gcc-bengaluru-chennai-20260615"

    body = """For twenty years, the deal was simple. American companies sent their back-office, engineering, and operational work to India, paid a fraction of US wages, and built entire careers and cities on the arbitrage. Opendoor just told 250 employees in Chennai and Bengaluru that the deal is off — and the reason it gave should make every Indian tech worker pay attention.

The US online real-estate firm announced last week that it is winding down its India operations entirely, less than two years after opening offices there. What made a routine 250-person restructuring travel across Silicon Valley was not the headcount. It was the rationale. CEO Kaz Nejatian did not frame it as cost-cutting. He framed it as an AI decision.

## What Opendoor actually said

"For years Opendoor built a large team in India to handle manual workflows across fragmented systems," Nejatian wrote in a note to staff that he later posted publicly. "As we've unified these systems and have hired small AI-native customer-facing teams throughout the US, we need all this operational work to be done in person and close to our customers."

"Our customers are in America," he added, "and that's where our operational work belongs."

The move is part of what the company calls "Opendoor 2.0" — a push to simplify operations, lean on AI, and shrink overall. This is not a story of jobs flooding back to American workers. Opendoor's global headcount fell from roughly 1,470 at the end of 2024 to about 1,042 at the end of 2025, according to SEC filings, with non-US staff cut from 342 to 184 over the same stretch. Affected India employees were offered severance, outplacement support, and short-term retention for knowledge transfer.

## Why this is different from a normal layoff

For decades, the logic of offshoring was durable: comparable talent at a fraction of the cost. That cost arbitrage — roughly $60,000 in American wages versus $8,000 in Indian wages for the same process work, as one widely-shared estimate put it — built India's $315 billion outsourcing industry and employed nearly six million people.

Opendoor's explanation broke that script. The offshore team was not replaced by a cheaper US team. A chunk of the work simply stopped needing humans at all. Once the company unified its internal systems and layered AI tooling on top, the gap those offshore teams had filled — absorbing manual, repetitive workflows across messy systems — shrank.

"The more important shift isn't jobs relocating from India to the US," Phil Fersht, CEO of HFS Research, told TechCrunch. "It's that AI is reducing the total amount of operational labor companies need in the first place." That lets firms run leaner regardless of where they are based.

## Is this a one-off or a pattern?

On its own, 250 jobs is a footnote. India hosts more than 2,100 Global Capability Centers employing roughly 2.36 million people and generating close to $100 billion in annual revenue. A single shutdown does not dent that.

But analysts are watching the pattern, not the number. Better Tomorrow Ventures co-founder Sheel Mohnot and Fersht both flagged the same thing: US companies are redesigning operations around AI and automation, and the most repeatable layer of that work — the entry-level, manual, process-heavy roles that have long been India's on-ramp into global tech — is exactly the layer AI eats first.

That is the quiet danger. The GCC boom is real, and high-skill AI and cybersecurity roles in Bengaluru are still growing fast. But the bottom rung of the ladder, the back-office and support work that gave millions of Indian graduates their first job, looks increasingly exposed.

## Why it matters for the diaspora

For the Indian diaspora, the Opendoor exit cuts two ways. Many NRIs in the US work at, or run, the very companies now rethinking their offshore footprint, and family members back home often staff the India centers being restructured. The shift also feeds a louder political narrative in Washington — "American companies should serve American customers and hire American workers first" — that intersects directly with H-1B scrutiny and immigration debates affecting Indian professionals on both sides of the ocean.

The reassuring read is that India's tech sector has absorbed disruption before, from the dot-com bust to automation waves, and moved up the value chain each time. The uncomfortable read is that this wave may not require a destination at all. When the work disappears instead of relocating, there is no city on the other side waiting to be built.

*Sources: Reuters, TechCrunch, HFS Research, SEC filings, Business Today*"""

    return {
        "headline": "Opendoor Just Closed Its Entire India Operation. The Reason Wasn't Cost — It Was AI.",
        "subheadline": "The US real-estate firm laid off 250 employees in Chennai and Bengaluru, saying AI-native US teams can now absorb the work. Analysts warn it's a preview of what's coming for India's back-office economy.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "India's $100 billion Global Capability Center economy gave millions their first job; when US firms cite AI rather than cost to pull work back onshore, the entry-level roles that anchor diaspora families and feed the H-1B pipeline are the first to vanish.",
        "sources": ["Reuters", "TechCrunch", "HFS Research", "SEC filings", "Business Today"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_opendoor()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if not art.get("image_url"):
        print(f"  ⚠ No valid image — aborting insert")
    else:
        insert_article(art)
