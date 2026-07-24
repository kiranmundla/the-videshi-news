#!/usr/bin/env python3
"""Immigration writer — July 7, 2026 (0800 PT run)
Two articles on the SCOTUS birthright citizenship ruling and its fallout.
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: SCOTUS upholds birthright citizenship ──────────────────────

article1_body = """The United States Supreme Court has settled one of the most consequential immigration questions in a generation. In a 6-3 ruling on June 30, the Court struck down President Trump's executive order that sought to strip birthright citizenship from children born on American soil to parents without permanent status.

The decision in *Trump v. Barbara* means that children born in the United States remain citizens at birth, regardless of whether their parents hold green cards, temporary visas, or no papers at all.

For hundreds of thousands of Indian families on H-1B visas, the ruling removes a threat that had loomed since Trump signed the order on his first day back in office in January 2025.

## What the executive order would have done

The order sought to redefine "subject to the jurisdiction thereof" in the 14th Amendment to exclude children born to parents in the country illegally or on temporary visas. Under that reading, a baby born in Houston to two H-1B holders — both paying taxes, both lawfully present — would not have been an American citizen.

Lower courts blocked the order almost immediately, so it never took effect. But the legal uncertainty it created rippled through Indian families for eighteen months. Some delayed having children. Others rethought whether to stay in the United States at all.

## How the justices split

Five justices — Chief Justice Roberts, Sotomayor, Kagan, Barrett, and Jackson — held that the order violated the Constitution itself. Roberts, writing for the majority, grounded the ruling squarely in the 14th Amendment's text and history.

"The Framers of the Fourteenth Amendment extended that promise to every free-born person in this land," Roberts wrote. "We keep that promise today."

Justice Brett Kavanaugh supplied the critical sixth vote but on narrower grounds. He wrote that the executive order did not violate the 14th Amendment — but that it contravened a federal statute, 8 U.S.C. §1401(a), which independently guarantees birthright citizenship by act of Congress. An executive order, Kavanaugh reasoned, cannot override a statute.

Justices Thomas, Alito, and Gorsuch dissented.

## Why this matters for Indian Americans specifically

Indian nationals hold more H-1B visas than any other nationality — roughly three-quarters of all approvals. Most are in their late twenties or thirties, prime family-formation years. The average wait for an Indian-born EB-2 green card stretches decades, meaning many have US-born children long before they become permanent residents.

If the executive order had survived, those children would have been born into legal limbo — American by every measure of their daily lives, but not citizens. The ruling closes that door.

But it may not be closed for good. Kavanaugh's concurrence explicitly left a gap that Congress could exploit, and Capitol Hill is already moving to do exactly that.

## The Kavanaugh concurrence — the door that remains open

By ruling that the executive order violated statute rather than the Constitution, Kavanaugh implied that Congress could, in theory, amend §1401(a) to create exceptions to birthright citizenship. Five justices disagreed, holding that the 14th Amendment itself prohibits such carve-outs. But Kavanaugh's separate opinion has already become the rallying cry for Republican legislators who want another run at the issue.

Senator Eric Schmitt of Missouri filed legislation the same day as the ruling. "The majority tried to constitutionalize unlimited birthright citizenship," he posted. "But Justice Kavanaugh MAY have left Congress a door. I'm filing legislation to walk through it."

Any statute that attempts to narrow birthright citizenship would almost certainly face its own constitutional challenge — and five sitting justices have already said the 14th Amendment forbids exactly that. But for Indian families watching from visa limbo, the legal uncertainty is the point. Each new bill, each new court challenge, extends the anxiety.

## What Indian families should do now

For the moment, nothing changes. Children born in the United States are citizens. Period. No form to file, no status to prove. The 14th Amendment says so, five Supreme Court justices confirmed it, and a sixth agreed the statute alone would be enough.

But the congressional push has already begun. Indian Americans — especially those in the years-long green card queue with US-born children — should pay attention to three bills now circulating on Capitol Hill. Any one of them could become the next legal battleground.

*Sources used in this report: Associated Press, Reuters, NBC News, Washington Examiner, Daily Caller News Foundation, Tennessean.*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your American-Born Child Is Still American. Six Justices Made Sure of That",
    "subheadline": "The Supreme Court struck down Trump's birthright citizenship order 6-3 in Trump v. Barbara, but Kavanaugh's concurrence left a door that Congress is already rushing to open.",
    "slug": make_slug("scotus-birthright-citizenship-trump-barbara-indian-families"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders are the largest group of temporary visa holders with US-born children — the ruling directly protects their families, but the congressional push threatens to reopen the question.",
    "tags": ["birthright-citizenship", "supreme-court", "14th-amendment", "h1b", "trump-v-barbara", "kavanaugh"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Associated Press / NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2026/06/09/federal-judge-blocks-100000-fee-on-h1b-visa-applications"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/op-eds/4637306/supreme-court-protected-birthright-citizenship-not-industry/"},
        {"name": "Daily Caller News Foundation", "url": "https://dailycaller.com"},
        {"name": "USA Today / Courier-Journal", "url": "https://www.usatoday.com"},
        {"name": "Tennessean", "url": "https://www.tennessean.com"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The United States Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ── Article 2: Congressional response — three bills in seven days ─────────

article2_body = """The Supreme Court's 6-3 ruling in *Trump v. Barbara* barely had time to cool before Congress started drafting workarounds. Within a week of the June 30 decision, three separate pieces of legislation landed on Capitol Hill — each targeting birthright citizenship from a different angle, and each with a direct line to Indian American families.

## The bills

**The Ban Birth Tourism Act** — introduced by Senator Marsha Blackburn of Tennessee — takes the narrowest approach. It would amend the Immigration and Nationality Act to prohibit foreign nationals from obtaining nonimmigrant visas when the primary purpose is to give birth in the United States so their child acquires citizenship.

The bill includes an exception for legitimate medical care related to childbirth. What it does not include is any mechanism for how immigration officials would determine an applicant's "primary purpose" — a gap that immigration attorneys have already flagged as ripe for abuse and racial profiling at consular posts.

Blackburn's office cited an estimate of 33,000 children born annually to women on tourist visas, a figure driven primarily by organised operations catering to wealthy Russian and Chinese nationals. Indian families on H-1B or L-1 visas are not the target demographic — but broad language in immigration law has a long history of catching people it was never aimed at.

**The Anchors Away Act** — filed by Representative Andy Ogles of Tennessee on June 30 — goes further. It would redefine who is "subject to the jurisdiction of the United States" under the Immigration and Nationality Act, effectively narrowing the statutory basis for birthright citizenship itself.

**Senator Eric Schmitt's dual strategy** is the most aggressive. The Missouri Republican is pursuing both a constitutional amendment and standalone legislation, explicitly invoking Justice Kavanaugh's concurrence as his legal roadmap. "The majority tried to constitutionalize unlimited birthright citizenship," Schmitt wrote on the day of the ruling. "But Justice Kavanaugh MAY have left Congress a door. I'm filing legislation to walk through it."

## The DOJ crackdown

The executive branch moved the same day. Colin McDonald, the Justice Department's assistant attorney general for fraud enforcement and self-described "fraud czar," directed federal prosecutors to "zealously protect the sanctity of United States citizenship" by investigating and prosecuting birth tourism schemes.

McDonald's memo cited three recent prosecutions: a husband-and-wife team running "USA Happy Baby," a birth tourism operation serving Chinese nationals (sentenced to 41 months each in 2024); and a New York-based operator convicted in 2022 for a scheme targeting Turkish nationals.

The enforcement emphasis is on organised commercial fraud — not on families lawfully present on work visas. But the rhetorical escalation matters. When the government frames citizenship as something to be "zealously protected" from exploitation, the policy atmosphere shifts for everyone navigating the immigration system.

## The Kavanaugh question

Every one of these legislative efforts traces back to a single paragraph in Justice Kavanaugh's concurrence. By holding that the executive order violated federal statute rather than the Constitution, Kavanaugh implied that Congress could amend that statute — 8 U.S.C. §1401(a) — to create new exceptions to birthright citizenship.

Five other justices disagreed, holding that the 14th Amendment itself bars any such narrowing. Any bill that passes would face an immediate constitutional challenge, and the current Court has already shown its hand.

But constitutional litigation takes years. A bill that passes Congress would create legal uncertainty during that entire period — exactly the kind of uncertainty that chills decisions about whether to stay in the United States, buy a house, start a family, or accept a new job that requires visa sponsorship.

## What Indian Americans are watching for

The practical risk is not that Congress will strip citizenship from children already born. Even the most aggressive proposals apply only to future births, and the constitutional headwinds are severe.

The risk is cumulative ambiguity. Indian professionals on H-1B visas already contend with a green card backlog measured in decades, a $100,000 fee challenged in three federal circuits, social media vetting of consular appointments, the end of third-country visa stamping, and an H-4 EAD programme under review at OMB.

Each new bill adds another variable to a calculation that millions of people are already struggling to complete: Is staying in America still worth it?

For the moment, the answer from the Supreme Court is unambiguous. Born here means born American. But the answer from Congress is still being written.

*Sources used in this report: Tennessean, Daily Caller News Foundation, New York Post, Reuters, NBC News, Washington Examiner, USA Today.*"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Bills in Seven Days. Congress Is Coming for Birthright Citizenship Through the Back Door",
    "subheadline": "A week after the Supreme Court upheld the 14th Amendment, Republican legislators have introduced the Ban Birth Tourism Act, the Anchors Away Act, and a dual constitutional-and-statutory push — all targeting the citizenship of future American-born children.",
    "slug": make_slug("birthright-citizenship-bills-ban-birth-tourism-kavanaugh-loophole"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian families on temporary visas face years-long green card waits while raising US-born children — every new bill targeting birthright citizenship adds uncertainty to whether their children's status could be revisited.",
    "tags": ["birthright-citizenship", "congress", "ban-birth-tourism-act", "kavanaugh", "immigration-legislation", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Tennessean", "url": "https://www.tennessean.com"},
        {"name": "Daily Caller News Foundation", "url": "https://dailycaller.com"},
        {"name": "New York Post", "url": "https://nypost.com"},
        {"name": "NBC News / NBC Palm Springs", "url": "https://www.nbcpalmsprings.com"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Capitol_Building_Full_View.jpg/1280px-Capitol_Building_Full_View.jpg",
    "image_caption": "The United States Capitol in Washington, D.C., where three birthright citizenship bills were introduced within a week of the Supreme Court ruling.",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
