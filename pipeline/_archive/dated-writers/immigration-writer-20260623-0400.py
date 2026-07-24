#!/usr/bin/env python3
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

article1_body = """For the roughly one million Indians waiting in the employment-based green card queue, the July 2026 Visa Bulletin delivered a number that is not a number at all. It is a letter: **U**.

EB-2 India — the advanced-degree category that holds the largest single share of skilled Indian professionals stuck in the backlog — is listed as **Unavailable** for July. That means the State Department will issue zero green cards in that category for the rest of fiscal year 2026, which ends September 30. The category had a final action date of September 1, 2013, just a month earlier. Now there is no date to chase at all.

## What the bulletin actually says

The State Department released the July bulletin, its tenth of the fiscal year, on June 18. USCIS confirmed that employment-based applicants must keep using the more restrictive Final Action Dates chart — not the friendlier Dates for Filing chart — to decide whether they can file Form I-485 to adjust status.

The India numbers are bleak across the board:

- **EB-1 India** (priority workers) retrogressed two months, from December 15, 2022 to October 15, 2022.
- **EB-2 India** went **Unavailable** — the harshest possible designation.
- **EB-3 India** (skilled workers) crept forward roughly two weeks, from December 15, 2013 to January 1, 2014.

China, by contrast, advanced almost everywhere: EB-1 China moved forward two months and EB-3 China leapt four and a half months. The contrast is stark and not accidental. When a category nears its annual per-country limit, the State Department slams the door to avoid issuing more visas than the law allows. India hit that wall in EB-2.

## Why "Unavailable" is worse than a slow date

A retrogressed date is frustrating but survivable — you keep your place in line and wait. "Unavailable" is different. No visa numbers exist for the category, so no green cards can be approved and, in most cases, no new adjustment-of-status applications can be filed against it for the remainder of the fiscal year.

The practical effect: an Indian engineer with an approved EB-2 petition and a 2013 priority date, who was tantalizingly close under June's chart, cannot file in July. Anyone whose work permit and travel document (the I-485-linked EAD and advance parole) depend on a pending adjustment application now waits for the new fiscal year, when fresh visa numbers reset on October 1.

## The diaspora math

This is the structural trap that defines Indian skilled immigration. Indians make up roughly 71% of approved H-1B holders, and a vast share of them are funneling toward exactly two categories — EB-2 and EB-3 — that are capped at the same 7% per-country limit as every other nation, from Iceland to Indonesia. The result is a queue that researchers estimate could take decades to clear, with some applicants statistically unlikely to ever receive a green card in their lifetimes.

For an Indian family living this out, "Unavailable" is not abstract. It means another year tethered to an employer, another year where a layoff triggers a 60-day scramble, another year where children who arrived as toddlers inch closer to "aging out" at 21. The EB-3 half-month bump is the only crumb of forward movement, and some EB-2 applicants with older priority dates may file to "downgrade" to EB-3 to keep a live application — a defensive maneuver that has become standard backlog survival craft.

https://x.com/USCIS

## What's next

The bulletin warns that further retrogression in EB-1, EB-2 and EB-3 is "possible before the end of FY 2026." The reset on October 1 should restore some EB-2 India movement when the new fiscal year's numbers become available, but no one expects a dramatic jump — demand vastly outstrips the per-country allotment.

For Indians in the queue, the immediate to-do list is unglamorous but real: confirm your priority date, keep your I-140 approval current, talk to an attorney about an EB-3 downgrade if your dates line up, and make sure any EAD and advance parole tied to a pending I-485 are renewed well ahead of expiry. The line did not move in July. It went backward. Planning around that reality is the only available move.

**Sources:** U.S. Department of State July 2026 Visa Bulletin; USCIS Adjustment of Status Filing Charts; Capitol Immigration Law Group analysis."""

article2_body = """A fraud bust in India has handed Washington's H-1B critics exactly the ammunition they were looking for. Indian authorities say they have seized more than 100,000 counterfeit degree certificates tied to dozens of bogus "universities," in a sprawling racket that allegedly produced forged credentials — including foreign degrees — for as little as $1,400 apiece.

The scandal is a domestic Indian crime story. But because the H-1B visa runs on degree credentials, and because Indians hold roughly 71% of all H-1B approvals, it has instantly become an American immigration story — and a political weapon.

## What investigators found

The operation, traced through Tamil Nadu, Kerala, Karnataka and several other states, was allegedly run by a man who rebuilt his forgery network after a prior arrest. Police seized hundreds of printers, computers and counterfeit university seals, and recovered certificates bearing forged signatures, holograms and stamps. Preliminary estimates suggest the broader network may have supplied fraudulent documents to more than a million people over the years — though most were almost certainly used for domestic jobs in India, not US visas.

Separately, US commentary has fixated on a figure of roughly 36,000 fake degrees allegedly sold through one mill, and on institutions like Manav Bharti University long associated with degree fraud.

## How Washington pounced

The reaction in the United States was immediate. Senator Eric Schmitt of Missouri seized on the seizures, posting that "authorities busted a massive fake degree racket" and demanding federal prosecution of "those who broke the law" by using fraudulent credentials for immigration benefits.

The bust also revived older, more incendiary claims. A former US consular officer who served in Chennai has alleged on podcasts that a large majority of H-1B visas issued to Indians were tainted by fraud — fake degrees, forged employment letters, or applicants who lacked the claimed skills. Those figures (she has cited 80–90%) are contested and unsupported by USCIS's own data, but they travel fast in a political environment already primed to distrust the program.

## The uncomfortable data point

What gives the story legs is a genuine oversight gap. USCIS has acknowledged it does not systematically track which H-1B beneficiaries hold degrees from institutions known for fraud. A 2008 compliance audit famously found that more than 13% of a sample of approved H-1B petitions contained fraud or technical violations. Critics argue little has structurally changed since.

Layered on top: acting ICE leadership has pointed to more than 10,000 foreign students tied to "highly suspect employers" through the OPT program — some allegedly working at empty buildings or residential addresses. The OPT-to-H-1B pipeline is the dominant route Indian graduates take into the workforce, which makes any enforcement push here land squarely on the diaspora.

## Why this matters for Indian Americans

For the overwhelming majority of Indian H-1B holders — who earned legitimate degrees from IITs, NITs, state universities and US graduate schools — the danger is guilt by association. Fraud headlines fuel calls for blanket "merit" overhauls, document re-verification, and tougher Requests for Evidence (RFEs). That means more scrutiny, longer adjudications, and a heavier documentary burden for honest applicants, even those years into the green card queue.

It also strengthens the hand of lawmakers already pushing to gut the program. Bills to slash the H-1B cap, scrap the lottery for a wage-based system, eliminate OPT, and even pause the program for three years are circulating in Congress. Each fresh fraud story is cited as justification.

The practical advice for diaspora professionals is defensive: keep original degree documentation, transcripts and credential evaluations readily available; expect heightened verification on extensions and green card filings; and treat any credential gap or inconsistency as a serious liability. The fraud was committed in India. The scrutiny will be felt in cubicles across the United States.

**Sources:** Fox News / AInvest reporting on the H-1B fraud ring; PakistanTV/CIS commentary; EducationWorld and Careers360 coverage of the Kanpur and Kerala fake-degree busts; Senator Eric Schmitt public statements."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "For Indians, the July Visa Bulletin Has a New Worst-Case Word: 'Unavailable'",
        "subheadline": "EB-2 India just went dark for the rest of the fiscal year — no green cards, no new filings. EB-1 retrogressed too. Only EB-3 inched forward.",
        "slug": make_slug("july-2026-visa-bulletin-eb2-india-unavailable-eb1-retrogression"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "EB-2 India — the category holding the largest share of skilled Indian professionals in the green card backlog — is now Unavailable through September 30, freezing filings and approvals for the workers most affected.",
        "tags": ["green-card", "visa-bulletin", "eb2", "eb3", "backlog", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Department of State — July 2026 Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "USCIS — Adjustment of Status Filing Charts", "url": "https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/adjustment-of-status-filing-charts-from-the-visa-bulletin"},
            {"name": "Capitol Immigration Law Group — July 2026 Visa Bulletin Analysis", "url": "https://cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings-causing-further-retrogression-for-india/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An open passport with travel and visa stamps, representing the U.S. employment-based green card process",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Fake-Degree Bust in India Just Became Washington's Newest H-1B Weapon",
        "subheadline": "Indian police seized 100,000-plus counterfeit certificates. U.S. lawmakers are using it to argue the entire H-1B pipeline is rotten — and honest Indian applicants will feel the scrutiny.",
        "slug": make_slug("india-fake-degree-racket-h1b-scrutiny-schmitt-credential-fraud"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The fraud happened in India, but the fallout — tougher credential checks, more RFEs, and fresh ammunition for bills to slash H-1B and OPT — lands on the millions of legitimate Indian professionals who depend on the program.",
        "tags": ["h1b", "visa-fraud", "fake-degrees", "opt", "uscis", "congress"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fox News via AInvest — India H-1B visa fraud ring busted", "url": "https://www.ainvest.com/news/india-h-1b-visa-fraud-ring-busted-authorities-seize-100-000-fake-degree-certificates-fox-news"},
            {"name": "EducationWorld — Pan-India fake degree racket busted", "url": "https://www.educationworld.in/kanpur-police-busts-pan-india-fake-degree-racket-two-arrested/"},
            {"name": "PakistanTV Digital — India's H-1B system under scrutiny over fake degrees", "url": "https://www.pakistantv.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37012315/pexels-photo-37012315.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A stack of framed university diplomas, illustrating the academic credentials at the center of the H-1B fraud debate",
        "image_attribution": "Pexels",
        "body": article2_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
