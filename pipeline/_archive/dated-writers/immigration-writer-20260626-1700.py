#!/usr/bin/env python3
"""Immigration article writer — 2026-06-26 17:00 PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ─────────────────────────────────────────────────────────────

article1_body = """USCIS approved 8.3 million immigration applications in 2025. The year before, the number was 11.4 million. That is a 27 per cent drop — the steepest single-year decline in the agency's modern history, and one that cuts across nearly every category that matters to Indian nationals waiting in America's immigration queue.

Employment-based petitions fell 26 per cent. Green-card-related approvals dropped 16 per cent. International student visas issued through September were down 31 per cent compared with the same window in 2024. Humanitarian admissions cratered by 69 per cent. Only family-based petition approvals rose, ticking up 8 per cent, and naturalisation-related approvals held roughly steady.

The data, compiled by USA Today from official USCIS records, lands at a moment when the administration's enforcement apparatus is operating at full throttle — and when the courts, as of this week's Supreme Court rulings, have largely stepped aside.

## The Pipeline Is Shrinking at Both Ends

The student-visa decline is not an abstract number. Indians are the second-largest international student cohort in the United States, and the F-1 pipeline is the primary feeder for H-1B employment. Fewer students arriving today means fewer H-1B petitions filed three or four years from now, which means fewer Indians entering the employment-based green-card queue at all.

"If you cut off that pathway, you could see the impact of that for years to come," said Julia Gelatt, associate director of the U.S. Immigration Policy Program at the Migration Policy Institute.

The 26 per cent drop in employment-based approvals compounds the problem on the other end. For Indians in the EB-2 and EB-3 queues — where wait times already stretch into decades — fewer annual approvals mean the line moves even more slowly. The July 2026 visa bulletin declared EB-2 India "unavailable" entirely. EB-3 India, the only category still technically open, has become a bottleneck as thousands of applicants attempt to downgrade.

## The Chilling Effect

Beyond the raw approval numbers, a subtler dynamic is taking hold. Economists call it the "chilling effect" — the behavioural pullback that legal immigrants exhibit when enforcement intensifies around them, even when they are not the target.

Research from the University of Colorado Boulder, published this month, found that employment among remaining immigrants declines 4 per cent on average after an ICE enforcement surge in a metro area. A separate study by Wharton's Exequiel Hernandez, tracking 5,388 ICE raids from January 2024 to February 2026, estimated that foot traffic fell 2.7 per cent and retail spending dropped 6.2 per cent in affected communities — amounting to roughly $14 billion in foregone spending in a single year.

"When the workforce starts to decline, that means less economic growth. That means less things are produced, which means higher costs for consumers," said David Bier, director of immigration studies at the Cato Institute.

For H-1B holders in particular, the chilling effect is not just psychological. The combination of the wage-weighted lottery, the now-appealed $100,000 fee, tighter RFE scrutiny, and the proposed four-year cap on student visas has created an environment where every step in the immigration journey carries more uncertainty and more cost than it did two years ago.

## What This Means for the Diaspora

Indian nationals file more H-1B petitions than any other nationality. They dominate the EB-2 and EB-3 queues. They are the fastest-growing international student population in the United States. A 27 per cent contraction in the overall approval pipeline does not hit every nationality equally — it hits Indians hardest, because Indians are most heavily represented in the categories that fell the most.

The Social Security trust fund, projected to be depleted by 2032, depends in part on payroll contributions from immigrant workers. The downstream economic argument for legal immigration has rarely been stronger — or less politically popular.

For now, the numbers suggest that the system is not just harder to navigate. It is physically processing fewer people through it. The doors have not been shut. They have been narrowed — and the queue behind them has not gotten any shorter."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Numbers Are In. Legal Immigration Just Had Its Worst Year in a Decade",
    "subheadline": "USCIS approved 27 per cent fewer applications in 2025 than the year before. Employment-based petitions, student visas, and green-card approvals all fell — and Indians, who dominate every one of those categories, are absorbing the sharpest blow.",
    "slug": make_slug("uscis-27-percent-decline-legal-immigration-employment-students-indians"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians file more H-1B petitions and hold more EB-2/EB-3 spots than any other nationality. A 27% contraction in the overall approval pipeline disproportionately slows their path to permanent residency and tightens the student-to-work-visa pipeline they depend on.",
    "tags": ["uscis", "legal-immigration", "h1b", "green-card", "student-visa", "employment-based", "immigration-data"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/23/legal-immigration-drops-trump/89554398007/"},
        {"name": "Migration Policy Institute", "url": "https://www.migrationpolicy.org/"},
        {"name": "Cato Institute", "url": "https://www.cato.org/immigration-research-policy-brief"},
        {"name": "University of Colorado Boulder (Chloe East et al.)", "url": "https://www.colorado.edu/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/supreme-court-immigration-rulings-economy-labor-market-6a9fd4df"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ── Article 2 ─────────────────────────────────────────────────────────────

article2_body = """Immigration lawyers across the United States are telling green-card holders the same thing this week: think twice before booking that flight to Delhi.

The advice follows the Supreme Court's twin rulings on June 25, which handed the administration sweeping authority to end Temporary Protected Status and systematically turn back asylum seekers at the border. The decisions themselves do not directly target lawful permanent residents. But the legal architecture they affirm — broad executive discretion, minimal judicial review — has shifted the risk calculus for anyone crossing a U.S. port of entry, including the roughly 2.7 million Indian-born people who hold green cards.

## What Changed at the Border

The immediate concern is not a new law. It is a new posture. Legal analysts say that Customs and Border Protection officers are now operating under expanded enforcement guidance that treats re-entry screening as a chance to scrutinise a traveller's full record — not just their current immigration status.

"Even historical or minor offences may trigger scrutiny," warned an advisory published this week by Travel and Tour World, citing multiple immigration attorneys. "The threshold for triggering immigration attention has effectively been lowered."

That means a resolved misdemeanour from a decade ago, a traffic incident that was dismissed, or even a record that was expunged in state court could surface during a CBP secondary inspection. Officers have always had the authority to review criminal databases. What has changed, attorneys say, is the institutional appetite to act on what they find.

## Why India Makes It Worse

The practical risk is magnified for travellers returning from India specifically. A flight from Delhi or Mumbai to JFK or SFO is 16 to 18 hours in the air. If a green-card holder is flagged at secondary inspection and placed in removal proceedings — however wrongly — the disruption is not a matter of rebooking a two-hour domestic hop. It can mean weeks or months of legal proceedings, potential detention, and separation from family and employment.

Indian green-card holders travel to India frequently — for weddings, festivals, elder care, business — and many do so with aging parents or young children in tow. The immigration bar's advice to seek legal consultation before every international trip is not alarmist in this context. It is logistically prudent.

## The Chilling Effect on Legal Residents

The Supreme Court's rulings were primarily about TPS holders and asylum seekers. But the secondary effects ripple outward. Research published this month by the Upjohn Institute for Employment Research found that in metro areas where DHS enforcement surges occurred, hours worked fell 1.9 per cent and the number of businesses in operation declined 1.7 per cent — conservatively translating to $106.1 million in lost wages.

The University of Colorado Boulder's Chloe East found that employment among remaining immigrants — including legal residents — dropped 4 per cent on average after an ICE surge, a phenomenon she attributes to the chilling effect: people pulling back from economic participation out of fear, even when they have every right to be here.

For green-card holders, the chilling effect manifests differently. It is not about leaving the workforce. It is about leaving the country — or rather, not leaving it. An Indian-American family that might ordinarily fly to Hyderabad for Diwali or to attend a nephew's wedding may now decide to stay put, weighing the emotional cost of absence against the legal cost of re-entry.

## What Lawyers Recommend

The consensus guidance from immigration attorneys is straightforward:

- **Review your record.** Any criminal matter — active, resolved, dismissed, or expunged — may surface during a CBP inspection. Know what is in your file before an officer does.
- **Consult before you travel.** A 30-minute conversation with an immigration attorney before departure can identify risks that would be far more expensive to address at the border.
- **Carry documentation.** Bring proof of employment, tax returns, and property ownership — evidence of ties to the United States that can support your case during secondary inspection.
- **Avoid overstaying.** Even a few days beyond a planned return date can create complications in the current environment.

The legal community stresses that none of this means green-card holders cannot travel. It means the margin for error has shrunk, and the consequences of a bad interaction at the border have grown.

## A New Calculation

For three decades, the green card was the finish line — the document that meant the system had accepted you. What this week's rulings clarify is that the finish line is citizenship. Everything short of it is, in legal terms, a status that can be reviewed, questioned, and — under the right circumstances — revoked.

Indian Americans who have spent years waiting for that green card are now learning that the card itself does not end the uncertainty. It just changes its shape."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Green Card Won't Protect You at the Border. Lawyers Say Think Twice Before Flying to India",
    "subheadline": "After the Supreme Court's twin immigration rulings this week, attorneys are telling lawful permanent residents to get legal advice before every international trip. For the 2.7 million Indian-born green-card holders who travel home regularly, the stakes just got personal.",
    "slug": make_slug("green-card-holders-travel-risk-supreme-court-india-reentry-cbp"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian green-card holders travel to India frequently for family, festivals, and business. Long-haul reentry from Delhi or Mumbai makes border disruption especially costly, and expanded CBP scrutiny puts even routine trips at risk.",
    "tags": ["green-card", "travel-risk", "supreme-court", "cbp", "border-inspection", "nri", "india-travel", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/47fwqj6dv536/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/us-supreme-court/supreme-court-allows-trump-end-deportation-protections-hundreds-thousands-2026-06-25/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/supreme-court-immigration-rulings-economy-labor-market-6a9fd4df"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/25/politics/supreme-court-tps-asylum-immigration/index.html"},
        {"name": "University of Colorado Boulder / Upjohn Institute", "url": "https://www.colorado.edu/"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/U_S_Customs_and_Border_Protection%2C_JFK_Aircraft_Search_Team_%2850093902786%29.jpg/1280px-U_S_Customs_and_Border_Protection%2C_JFK_Aircraft_Search_Team_%2850093902786%29.jpg",
    "image_caption": "U.S. Customs and Border Protection officers at JFK International Airport",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
