#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 06:30 run (Modi-Trump G7 bilateral)."""

import os
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


def article_modi_trump_g7():
    print("\n═══ Article: Modi-Trump G7 bilateral ═══")

    img_url = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/modi-trump-g7-bilateral-evian-20260616.jpg"
    img_caption = "US President Donald Trump and Indian Prime Minister Narendra Modi at an earlier bilateral meeting"
    img_attr = "Wikimedia Commons"
    if not validate_get(img_url):
        print("  ⚠ primary image failed validation")
        img_url = None

    slug = "modi-trump-g7-bilateral-evian-h1b-visa-trade-deal-first-meeting-16-months-20260616"

    body = """For sixteen months, Narendra Modi and Donald Trump have governed the world's two largest democracies while never once sitting in the same room. That ends this week. On Wednesday, on the sidelines of the G7 summit in the French spa town of Evian-les-Bains, the two leaders are scheduled to hold their first face-to-face bilateral since Modi's February 2025 state visit to Washington — and the agenda reads like a checklist of everything that keeps Indian-American households up at night.

Trade. Energy. And, most consequentially for the diaspora, H-1B visas.

## A meeting freighted with backlog

The Modi-Trump relationship has not stood still in those sixteen months, but it has frayed. Washington imposed tariffs on Indian goods. Trump repeatedly claimed — and New Delhi repeatedly denied — that he personally brokered the ceasefire in India's brief 2025 conflict with Pakistan. A proposed additional 12.5 percent US tariff on Indian imports, justified on forced-labour grounds India rejects outright, still hangs over the relationship.

Yet the temperature has been falling. Secretary of State Marco Rubio visited India last month. The two governments are now circling what Indian Trade Minister Piyush Goyal calls the "first tranche" of a bilateral trade agreement, with US Trade Representative Jamieson Greer due in New Delhi the week after the summit. A senior US official, briefing reporters before Evian, was blunt about expectations: "We think a very good deal is possible. I don't think we'll close that deal at the G7." The bilateral, in other words, is a stocktake, not a signing ceremony.

## Why the diaspora is watching the visa line, not the tariff line

For most Indian-Americans, tariffs on auto parts and shrimp are an abstraction. The H-1B is not. An Indian government source confirmed Modi "is expected to take up the issue of H-1B visas" directly with Trump — a striking signal that New Delhi now treats the immigration status of its diaspora professionals as a core bilateral interest rather than a domestic American matter.

The timing matters. Just last week, a US federal judge struck down the Trump administration's proposed $100,000 H-1B fee, a measure that would have hit Indian nationals hardest given they hold roughly 70 percent of the visas issued each year. Washington has also floated a December pilot allowing H-1B holders to renew their visas domestically — without the dreaded flight home and consular wait. Modi raising the issue at the leaders' level suggests India intends to lock in those gains, not leave them to the courts and the bureaucracy.

## Energy, defence, and the China subtext

Beyond visas and trade, the two delegations are expected to canvass defence procurement, artificial intelligence cooperation, and energy. On energy, the conversation has shifted fast. After February's framework deal — in which Trump said India agreed to buy more than $500 billion in US energy, technology and agricultural products and to wind down purchases of Russian oil — officials have floated the prospect of Indian buying of Venezuelan crude as Washington recalibrates its sanctions map.

The meeting also lands days after the US-Iran agreement to reopen the Strait of Hormuz, through which a fifth of the world's oil once flowed. For India, the world's third-largest oil importer, the de-escalation is an unambiguous relief, and energy security will be threaded through the Evian talks.

## What success looks like

No one expects a grand bargain on Wednesday. The realistic best case is momentum: a public reaffirmation that the trade deal is on track for mid-July, a warm photograph to bury sixteen months of friction, and — for the diaspora — language signalling that the H-1B framework will stabilise rather than lurch with each court ruling.

That modest bar is itself the story. Two leaders who pride themselves on personal chemistry let it lapse for over a year while the structural relationship absorbed real strain. Evian is the test of whether the chemistry still holds — and whether it can be converted, in the language of the cricket metaphors both capitals now favour, into runs on the board.

For the five-million-strong Indian-American community, the scoreboard that matters is narrower and more personal: whether the visa that anchors their careers, their mortgages and their children's futures gets a little more certain after Wednesday's handshake.

*Sources: Reuters, Livemint, The Hindu Businessline, New York Post, Outlook Business*"""

    return {
        "headline": "Modi and Trump Meet Wednesday for the First Time in 16 Months. H-1B Visas Are on the Table.",
        "subheadline": "The two leaders hold their first face-to-face bilateral since February 2025 on the sidelines of the G7 in Evian. Trade and energy lead the agenda — but for the diaspora, the visa conversation is the one that counts.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "Modi is expected to raise H-1B visas directly with Trump — the status that anchors the careers, mortgages and futures of millions of Indian professionals in the US, and which has lurched with every recent court ruling and policy pilot.",
        "sources": ["Reuters", "Livemint", "The Hindu Businessline", "New York Post", "Outlook Business"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_modi_trump_g7()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if not art.get("image_url"):
        print("  ⚠ No valid image — aborting insert")
    else:
        insert_article(art)
