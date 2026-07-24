#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 08:30 run (US birth tourism crackdown)."""

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


def article_birth_tourism():
    print("\n═══ Article: US birth tourism crackdown ═══")

    img_url = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/"
               "article-images/birth-tourism-state-dept-20260616.jpg")
    img_caption = "The Harry S. Truman Building, headquarters of the US State Department in Washington, D.C."
    img_attr = "Wikimedia Commons"
    if not validate_get(img_url):
        print("  ⚠ primary image failed validation")
        img_url = None

    slug = "us-dismantles-birth-tourism-networks-revokes-visas-birthright-citizenship-indian-families-20260616"

    body = """The US State Department has gone public with one of the more aggressive uses of visa enforcement in recent memory, announcing that it has dismantled multiple overseas "birth tourism" networks and revoked the visas of hundreds of foreign nationals who travelled to the United States primarily to give birth and secure American citizenship for their children.

In a series of statements, the department said consular officers — working with law enforcement and data analytics — uncovered organised operations in Europe, West Africa and North Africa. One European embassy alone flagged more than 400 suspected cases since 2024, tracing them to at least six companies that coached applicants on what to say in visa interviews, arranged housing in America and set up delivery plans. A separate West African network involving more than 100 foreign nationals using fraudulent documents and "fixers" was shut down outright.

"We shut it down, revoked these foreign nationals' visas, and are coordinating with local authorities to systematically identify and cut off any similar operations," the department said. "A U.S. visa is a privilege, not a right."

## Why this lands differently for Indian families

For the Indian diaspora, the headline is not the West African fraud rings — it is the legal ground shifting beneath the children of perfectly lawful visa holders. The birth tourism crackdown is one prong of a much larger Trump administration push to narrow who is automatically American at birth, and that second prong reaches straight into the H-1B and L-1 households that form the backbone of the Indian community in the US.

On his first day back in office, President Trump signed an executive order declaring that a child born in the US is not automatically a citizen if the parents are in the country illegally or only temporarily — a category that explicitly includes people on student, work and visitor visas. Indians, who hold roughly 70 percent of H-1B visas issued each year, are among the most exposed of any nationality. A family that has waited a decade in the employment-based green card backlog could, under the order, have a US-born child who is not a citizen.

## The courts, not the consulates, will decide

The executive order has been frozen by multiple federal injunctions, and the Supreme Court heard oral arguments in the spring. A ruling is expected within weeks. Until the justices speak, birthright citizenship as Indian-American families have always understood it — born here, American, full stop — technically still holds, but its permanence is now a live question rather than a settled fact.

That uncertainty is the real story for the diaspora. The State Department's anti-birth-tourism drive is aimed at people who fly in for a delivery and fly home. But the rhetoric powering it — that citizenship is "not a souvenir," that a US passport should not be "a participation trophy" — is the same rhetoric being marshalled to argue that the children of long-term visa holders should not qualify either. Legally the two are distinct. Politically they are being fused.

## What it means on the ground

For now, the practical fallout is concentrated at the consular window. Officers overseas have long had authority to deny a B visa to any applicant they believe is travelling primarily to give birth on US soil, and that discretion is now being exercised far more assertively. Pregnant applicants — including Indian women planning to visit family during a pregnancy — may face sharper questioning, and a denial on suspicion of birth tourism can carry a permanent travel ban for those found to have used fraudulent documents.

For the millions of Indians already settled in the US on work visas, the more consequential moment is still ahead: the Supreme Court's decision on whether their American-born children remain American by right. The birth tourism announcement is a signal of how seriously the administration intends to police the edges of citizenship. The court will decide how far toward the centre that policing is allowed to reach.

For a community that has organised its entire American life — careers, mortgages, school districts — around the assumption that its US-born children are citizens, few rulings this decade will matter more.

*Sources: The Hindu Businessline, Fox News, Washington Examiner, USA Today, Wall Street Journal*"""

    return {
        "headline": "The US Just Dismantled Birth Tourism Networks. The Real Worry for Indian Families Is What Comes Next.",
        "subheadline": "Washington revoked hundreds of visas tied to overseas birth tourism rings. But the rhetoric driving the crackdown is the same one aimed at narrowing birthright citizenship for the children of H-1B holders — and the Supreme Court rules within weeks.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "The same campaign powering the birth tourism crackdown is being used to argue that US-born children of H-1B and student-visa holders — overwhelmingly Indian — should not be automatic citizens, with a Supreme Court ruling due within weeks.",
        "sources": ["The Hindu Businessline", "Fox News", "Washington Examiner", "USA Today", "Wall Street Journal"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_birth_tourism()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if not art.get("image_url"):
        print("  ⚠ No valid image — aborting insert")
    else:
        insert_article(art)
