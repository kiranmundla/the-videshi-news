#!/usr/bin/env python3
"""Immigration writer — 2026-06-10 04:00 UTC run"""
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

# ─────────────────────────────────────────────
# ARTICLE 1: EB-2 India Goes "Unavailable"
# ─────────────────────────────────────────────

article1_body = """The word sits in the middle of the State Department's June 2026 Visa Bulletin like a locked door: **Unavailable**. For every Indian-born professional waiting in the EB-2 employment-based green card queue, the message could not be clearer. No visas will be issued in this category until the new fiscal year begins on October 1.

It is the single most consequential entry in this month's bulletin, and it arrived without ceremony. The EB-2 India Final Action Date did not merely retrogress — it ceased to exist. Both the Final Action Dates chart and the Dates for Filing chart now read "Unavailable," meaning no new I-485 adjustment-of-status applications can be filed and no pending cases can be approved in this category until at least FY2027.

## The Numbers That Got Worse

The damage extends beyond EB-2. Here is what the June bulletin shows for India-born applicants across all major employment-based categories:

- **EB-1 (Priority Workers):** Retrogressed 3.5 months to December 15, 2022 — a reversal that stings professionals who had been counting on forward movement.
- **EB-2 (Advanced Degree / Exceptional Ability):** Unavailable until October 1, 2026. Previously the Final Action Date sat around late 2013; now it is simply gone.
- **EB-3 (Professionals & Skilled Workers):** Advanced one month to December 15, 2013. That is a 13-year backlog — meaning applications filed in December 2013 are only now becoming eligible.

For the roughly 400,000 Indian nationals in the EB-2 queue, the practical meaning is stark: no green card approvals for at least four months, and likely longer. July 2026 predictions from immigration analysts already indicate EB-2 India will remain Unavailable, with EB-1 India facing further retrogression.

## Why It Happened

The cause is arithmetic, not policy. Every fiscal year the United States allocates approximately 140,000 employment-based immigrant visas, with a 7 percent per-country cap. India-chargeable applicants — overwhelmingly concentrated in technology, healthcare, and engineering — far exceed that allocation every single year.

This fiscal year, heavy filings from Indian applicants early in the cycle consumed the available visa numbers faster than expected. The State Department was forced to slam the EB-2 India category shut to stay within the statutory annual limit, according to analysis from Fragomen and WR Immigration. The bulletin itself carried an unusual warning: further retrogression, or even additional "Unavailable" designations in other categories, could follow before September.

## What It Means If You Are on an H-1B

For the Indian tech worker on an H-1B in San Jose or Seattle, this is not an abstract policy update. It reshapes career planning in concrete ways.

If your EB-2 priority date is anything after late 2013, your green card is not coming this fiscal year. Your employer must continue sponsoring H-1B extensions — a process that costs several thousand dollars per cycle and requires proving the job still qualifies. Your spouse on an H-4 visa may have just lost work authorization if the H-4 EAD programme continues to face its own legal challenges.

Some immigration attorneys are advising clients to consider downgrading from EB-2 to EB-3, where India's Final Action Date has at least inched forward to December 2013. The trade-off: EB-3 priority dates move glacially, and the switch itself resets nothing — you keep your original priority date but file under a different preference category. It is a lateral move at best, useful mainly if your priority date happens to fall in the narrow window where EB-3 is current and EB-2 is not.

Others are eyeing EB-1A (extraordinary ability) or NIW (National Interest Waiver) petitions, both of which bypass the employment-based queue. But recent data shows NIW denial rates now outpacing the supposedly harder EB-1A category, closing off what many considered the last reliable escape hatch.

## The Bigger Picture

The June bulletin is a symptom of a system that has not been updated since 1990. The per-country cap treats India — which sends more H-1B workers than any other nation — the same as countries that send a handful. Bills to eliminate the per-country cap, such as the Eagle Act, have stalled repeatedly in Congress. Meanwhile, the American White-Collar Worker Jobs Act introduced by Representative Chip Roy in June proposes ending the H-1B-to-green-card pathway entirely.

For the hundreds of thousands of Indian professionals who moved to America, built careers, bought homes, and enrolled their children in American schools, the word "Unavailable" is not a bureaucratic technicality. It is a four-month sentence — at minimum — added to a wait that already stretches decades. And if the July bulletin confirms what analysts expect, October may not bring relief either."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Unavailable — The One Word That Just Froze Half a Million Indian Green Card Dreams",
    "subheadline": "The June 2026 Visa Bulletin shut the EB-2 India category entirely. No visas until October at the earliest — and the July forecast is no better.",
    "slug": make_slug("eb2-india-unavailable-june-visa-bulletin-green-card-frozen"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Directly affects the estimated 400,000+ Indian nationals in the EB-2 green card queue, most of them H-1B tech workers whose career plans, spousal work authorization, and long-term residency in America now hinge on whether FY2027 brings relief.",
    "tags": ["eb-2", "visa-bulletin", "green-card", "retrogression", "uscis", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Shusterman Law – June 2026 Visa Bulletin", "url": "https://www.shusterman.com/visa-bulletin-state-department/"},
        {"name": "Asanify – EB-2 India Retrogression Digest", "url": "https://asanify.com/blog/news/eb2-india-retrogression-june-6-2026/"},
        {"name": "Prister Law – June 2026 Visa Bulletin Updates", "url": "https://pristerlaw.com/june-2026-visa-bulletin/"},
        {"name": "India Tribune – Visa Bulletin Retrogression Analysis", "url": "https://www.indiatribune.com/visa-bulletin-retrogression/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "An opened passport with visa stamps — the document that defines immigration limbo for hundreds of thousands",
    "image_attribution": "Pexels",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: Secure America Act — $70B
# ─────────────────────────────────────────────

article2_body = """The U.S. Senate voted 52–47 on June 5 to pass the Secure America Act, a budget reconciliation package that funnels roughly $69.5 billion into immigration enforcement through the end of fiscal year 2029. It is the largest single immigration spending bill in American history, and its effects will be felt far beyond the southern border.

For Indian professionals navigating the legal immigration system, the bill does not change visa categories or green card quotas directly. What it does is fund the infrastructure of enforcement at a scale that reshapes the terrain everyone — documented or not — must walk on.

## Where the Money Goes

The allocations are precise and revealing:

- **$38.5 billion for ICE** — covering hiring, detention expansion, and removal operations. ICE is the agency that conducts workplace audits, arrests people with expired status, and carries out deportation orders.
- **$22.6 billion for CBP** — funding Border Patrol agents, inspection personnel, and border operations.
- **$3.5 billion for border security technology** — surveillance systems, inspection equipment, and air and marine response platforms.
- **$5 billion in additional DHS funding** — a broad category covering the department's operational overhead.

The scale is deliberate. DHS plans to expand detention capacity to **100,000 beds** and has set an administration target of **1 million removals per year**. To reach those numbers, ICE will increase 287(g) agreements — which let local law enforcement act as immigration agents — by a staggering **1,075 percent**.

## The Reconciliation Manoeuvre

Senate Republicans moved the bill through budget reconciliation, a procedural tool that bypasses the 60-vote filibuster threshold. The vote fell along party lines. It is the second time the Trump administration has used reconciliation for immigration — the first was the 2025 "One Big Beautiful Bill Act."

The timing matters. The vote came after a **76-day partial DHS shutdown**, the longest on record, triggered when Democrats refused to fund ICE and CBP without new oversight guardrails after several fatal shootings by agents. By locking in multi-year funding through September 2029, the bill removes immigration enforcement from the annual appropriations cycle entirely, insulating it from future political negotiations.

DHS Secretary Markwayne Mullin was blunt about the strategy in his June 2 testimony: "The Secure America Act will ensure DHS funding is no longer held hostage by radical agendas."

## Why Legal Immigrants Should Pay Attention

The bill targets undocumented immigration and border crossings. But enforcement infrastructure does not check your visa status before it reshapes your daily environment.

**The 287(g) expansion** means local police departments across the country — in suburbs where Indian families have concentrated, in cities where tech campuses sit — will increasingly be trained and authorized to inquire about immigration status. For an H-1B worker who has never had a traffic stop turn into an immigration question, this changes the calculus. For an H-4 spouse whose EAD is caught in legal limbo, an encounter with local police now carries an extra layer of anxiety.

**The AOS memo compounds the effect.** A USCIS memorandum issued on May 22 declared that adjustment of status — the process by which someone already in the U.S. applies for a green card without leaving — is "a matter of administrative grace." The agency directed that most applicants pursue consular processing abroad instead. Combined with the Secure America Act's enforcement funding, the message to legal immigrants is consistent: America would rather you leave and apply from outside than adjust your status from within.

**Detention bed expansion to 100,000** affects anyone in removal proceedings, including Indians who overstay visas or whose status lapses between petition approvals. India is among the top ten nationalities for ICE encounters, and third-country deportation flights involving Indian nationals have already been documented this year.

## The Chilling Effect

Immigration attorneys describe what they call a "chilling effect" — a measurable reluctance among legal immigrants to assert their rights, change employers, or even travel domestically. The Secure America Act does not create that effect through new laws. It creates it through funding. When enforcement is well-resourced and widely distributed, the gap between policy and practice narrows. Discretion shrinks. The benefit of the doubt disappears.

For the Indian tech worker weighing whether to change jobs (and restart the green card clock), or the family considering a mortgage in a country where their permanent status remains decades away, the $70 billion is not an abstraction. It is a signal about what kind of immigration system America is building — and who it is building it for.

The bill now heads to the House, where passage is expected. Congressional Budget Office estimates project it will raise total deficits by $94.5 billion over the next decade after interest costs."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Seventy Billion Dollars and a Message — The Enforcement Machine America Just Funded Through 2029",
    "subheadline": "The Senate's Secure America Act is the largest immigration enforcement package in U.S. history. Indian legal immigrants are not the target — but they are in the blast radius.",
    "slug": make_slug("secure-america-act-70-billion-enforcement-indian-immigrants"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Although aimed at undocumented immigration, the $70 billion enforcement expansion — 100,000 detention beds, 1,075% increase in local immigration policing, and the AOS 'administrative grace' memo — directly affects the daily reality of Indian H-1B workers and their families across American suburbs and tech corridors.",
    "tags": ["secure-america-act", "ice", "enforcement", "287g", "h1b", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge – Senate Passes $70B Secure America Act", "url": "https://www.visaverge.com/news/senate-passes-70-billion-secure-america-act-backing-trump-deportation-plan/"},
        {"name": "Fox News – Federal Judge Strikes Down H-1B Fee", "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee-ruling-unconstitutional-tax"},
        {"name": "Reuters – Trump H-1B Fee Ruling", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "Congressional Budget Office – S.2 Cost Estimate", "url": "https://www.cbo.gov/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32177176/pexels-photo-32177176.jpeg",
    "image_caption": "The U.S. Capitol building in Washington, D.C., where the Senate passed the largest immigration enforcement bill in American history",
    "image_attribution": "Pexels",
    "body": article2_body
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
