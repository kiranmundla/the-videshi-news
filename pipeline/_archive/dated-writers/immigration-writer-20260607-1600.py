#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-07 16:00 UTC run"""
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


# ──────────────────────────────────────────────────────
# ARTICLE 1: Fake Degree Bust
# ──────────────────────────────────────────────────────

article1_body = """Indian law enforcement has seized more than 100,000 counterfeit university degree certificates across at least 28 institutions — certificates that investigators say were used to fabricate the educational credentials required for H-1B visa petitions filed in the United States.

The bust, first reported by Fox News and confirmed by multiple outlets this week, has drawn the attention of federal agencies including Immigration and Customs Enforcement. One institution alone, Manav Bharti University in Himachal Pradesh, is accused of issuing upwards of 36,000 fake degrees. The going rate: as little as $1,400 per certificate — a pittance compared to the six-figure salary an H-1B position commands.

## The legal architecture that makes it matter

The H-1B visa is, at its core, a credentialing programme. Under INA §214(i), a "specialty occupation" requires a U.S. bachelor's degree or its foreign equivalent. A counterfeit degree does not merely pad a résumé; it fabricates the legal basis of the visa petition itself, retroactively invalidating both the USCIS approval and the Labour Condition Application the employer certified.

What makes the revelation sting is a quiet admission from USCIS: the agency does not systematically track which institutions awarded the degrees backing approved petitions. There is no database cross-referencing Manav Bharti graduates against H-1B beneficiaries. The verification gap is structural, and it has apparently persisted for years. A 2008 compliance audit found that more than 13 per cent of approved H-1B visas were based on information that was, in some respect, fraudulent.

## Separating the signal from the noise

The bust has been amplified by a claim now circulating virally on social media: that nearly 90 per cent of Indian H-1B applications contain fraudulent information. That figure, however, traces to a former consular officer's account of adjudications in 2005–2007 — not to the current investigation. The Insider Wire, which published one of the most detailed breakdowns, was careful to note the distinction. The verified numbers from the Indian law enforcement action are damning enough without inflation.

A separate data point has also entered the discourse: that 83 per cent of H-1B hires during the Biden administration landed in junior or entry-level positions, complicating the programme's branding as a channel for "highly skilled" workers. Whether that reflects employer gaming, credential misrepresentation, or simply the economics of entry-level tech hiring is a question no single investigation can settle.

Texas Attorney General Ken Paxton has reportedly opened a state-level probe into H-1B-related fraud, building on civil investigative demands already issued to nearly 30 North Texas businesses.

## The collateral damage for legitimate professionals

Here is the part that should worry the roughly 600,000 Indian nationals currently in the employment-based green card queue: the fraud does not exist in a vacuum. It feeds a political narrative — already ascendant in Congress and the executive branch — that the H-1B programme is a "cheap labour pipeline" dressed up as a merit-based system. Congressman Chip Roy's American White-Collar Worker Jobs Act, introduced on 4 June, explicitly invokes fraud as a justification for eliminating the H-1B-to-green-card pathway and scrapping OPT.

For the IIT Bombay computer science graduate, the BITS Pilani engineer, the Delhi University commerce student who earned every credit legitimately — the bust changes the atmosphere. Expect more Requests for Evidence demanding degree authentication. Expect longer processing times as USCIS decides, perhaps for the first time, to verify institutional credentials systematically. Expect employers to think twice before sponsoring a petition when the political cost of being associated with the programme keeps climbing.

The programme's critics have a 100,000-certificate exhibit to point to. Its defenders have 75 per cent of H-1B holders who show up, do the work, and pay taxes in a country that recruited them. The question, as always, is whether Washington can distinguish between the two."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "One Hundred Thousand Fake Degrees — and a System That Never Checked",
    "subheadline": "Indian law enforcement seized over 100,000 counterfeit certificates linked to H-1B fraud. USCIS admits it has no database to track the institutions behind approved petitions.",
    "slug": make_slug("fake-degree-bust-h1b-fraud-100k-certificates-indian-uscis"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Legitimate Indian professionals with real degrees from IITs and top universities now face increased scrutiny, longer processing, and employer hesitancy — all because the system never built a way to tell them apart from the fraudsters.",
    "tags": ["h1b", "fraud", "uscis", "fake-degrees", "immigration-enforcement"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "InsiderWire", "url": "https://insiderwire.com/news/authorities-seize-over-100-000-fake-degrees-in-indian-h-1b-fraud-bust"},
        {"name": "AInvest / Fox News", "url": "https://ainvest.com/"},
        {"name": "NY Post / Bloomberg", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport displaying visa stamps at a border checkpoint",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────────────
# ARTICLE 2: July Visa Bulletin — All Doors Shut
# ──────────────────────────────────────────────────────

article2_body = """Immigration attorney Carl Shusterman, whose visa bulletin predictions have tracked State Department movements for decades, has released his projections for July 2026. For Indian nationals in the employment-based green card queue, the forecast reads like a weather report for a city without shelter: EB-2 remains "Unavailable." EB-1 faces retrogression. EB-3 shows little or no forward movement.

It is the first time in recent memory that all three major employment-based categories are simultaneously closed, frozen, or moving backwards for a single country. For the 574,765 Indian principal applicants — and the 862,363 individuals including dependents — in the backlog, there is, as of next month, no pathway moving forward.

## The numbers behind the lockout

The State Department exhausted its annual allocation of EB-2 visas for India before the fiscal year's end, a ceiling that will not reset until October when FY 2027 begins. Under the June 2026 bulletin, USCIS has already switched from the more permissive "Dates for Filing" chart to the restrictive "Final Action Dates" chart — a move that narrows who can even submit an adjustment-of-status application.

The EB-2 India Final Action Date currently sits at 15 July 2014. That is a 12-year wait from filing to potential approval, and even that figure understates the real timeline: 426,465 principal applicants are queued in EB-2 India alone, competing for roughly 2,800 visas per year under the seven per cent per-country cap. At current issuance rates, the mathematical wait exceeds 150 years — a number so absurd it functions less as an estimate and more as an indictment.

EB-3 India, often treated as a relief valve when EB-2 retrogresses, offers no escape. Its Final Action Date is stuck at 15 November 2013 — actually behind EB-2. The "downgrade to EB-3" strategy that immigration attorneys have recommended for years has been functionally dead for months.

EB-1, the category reserved for "priority workers" with extraordinary ability, multinational executives, and outstanding researchers, was supposed to be the fast lane. Its Final Action Date for India reached 1 April 2023 as of recent bulletins — years ahead of EB-2. But Shusterman's July prediction flags retrogression, meaning even the fast lane is about to reverse direction.

## Why July is different

Single-category freezes are not new. EB-2 India has hit "Unavailable" before, most recently in the final quarter of FY 2024. What distinguishes July 2026 is the convergence: EB-2 unavailable, EB-1 retrogressing, EB-3 frozen. The standard playbook for Indian green card applicants — file in EB-2, consider downgrading to EB-3 if it moves faster, or attempt an upgrade to EB-1 if qualifications allow — collapses when every option is simultaneously blocked.

USCIS's decision to use Final Action Dates rather than Dates for Filing compounds the problem. The Dates for Filing chart historically allowed applicants to submit I-485 adjustment-of-status packets earlier, even if visa numbers were not immediately available. That flexibility gave applicants access to employment authorisation documents and advance parole travel permits while they waited. Under Final Action Dates, even that intermediate relief is withdrawn.

## What it means in practice

For the Indian software engineer in Sunnyvale who filed her PERM labour certification in 2015, the July bulletin means another month of stasis — her eleventh year in the queue. For the data scientist in Chicago whose employer just completed an EB-1B petition, retrogression means the approval he expected by autumn may not come at all this fiscal year.

For employers, the calculus is shifting. Sponsoring an Indian national for a green card has always been expensive — the National Foundation for American Policy estimates the total cost at up to $50,000 including the $100,000 proclamation fee. Now it is expensive and indefinite, with no category offering forward momentum.

The Cato Institute and the National Foundation for American Policy have both called for eliminating the seven per cent per-country cap, the structural bottleneck that creates India's disproportionate backlog. Legislation to do so — the EAGLE Act and the Fairness for High-Skilled Immigrants Act — has been introduced in every Congress since 2011. None has passed.

Until it does, 862,363 people wait. And in July, they will wait in the dark."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Every Door Just Closed — July's Visa Bulletin Locks Out Indian Nationals Across All Categories",
    "subheadline": "EB-2 unavailable, EB-1 retrogressing, EB-3 frozen: for the first time, all three major employment-based green card pathways are simultaneously blocked for India.",
    "slug": make_slug("july-2026-visa-bulletin-eb1-eb2-eb3-india-all-closed"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With 862,363 Indians in the backlog and no employment-based category moving forward in July, the standard green card playbook — EB-2, downgrade to EB-3, or upgrade to EB-1 — collapses completely for Indian professionals.",
    "tags": ["green-card", "visa-bulletin", "eb2", "eb1", "eb3", "backlog", "retrogression"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Shusterman Immigration Law", "url": "https://www.shusterman.com/visa-bulletin-predictions/"},
        {"name": "Manifest Law", "url": "https://manifestlaw.com/"},
        {"name": "VisaHQ", "url": "https://visahq.com/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/13646957/pexels-photo-13646957.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "People waiting in a long queue along a city street",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────────────
# Publish
# ──────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
