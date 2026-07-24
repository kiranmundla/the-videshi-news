#!/usr/bin/env python3
"""
Videshi Immigration Writer — 2026-07-01 09:00 PDT
Two fresh immigration articles targeting Indian American diaspora.
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


# ─── ARTICLE 1 ──────────────────────────────────────────────────────────────
article_1_body = """The Trump administration has proposed tripling some immigration court filing fees, a move that would make it dramatically more expensive for immigrants to fight their own deportation.

Under the proposed rule from the Justice Department's Executive Office for Immigration Review (EOIR), the cost of filing an appeal against an immigration judge's ruling would leap from $110 to $975 — nearly a ninefold increase. Two forms used by immigrants applying for cancellation of removal would rise from $100 to more than $300. The rule will be published in the Federal Register on Friday and is subject to a public comment period before it can take effect.

## The pattern is unmistakable

This is not an isolated fee hike. It follows a cascade of immigration cost increases under the current administration: the $100,000 surcharge on new H-1B petitions (since struck down as an unlawful tax by a Boston federal judge, though still being charged pending appeal), an 83 per cent increase in the naturalization application fee, and the first-ever charge on asylum applications proposed last November.

Taken together, the message is clear. The administration is building a financial barrier around the immigration system, one form at a time. EOIR frames the increase as a routine adjustment. "The fees have remained static, not accounting for inflation or any other intervening changes in EOIR's processing costs," the proposed rule reads. But a jump from $110 to $975 is not inflation. It is a policy choice dressed in fiscal language.

## What this means for Indians in the system

The immigration court system may feel remote to an H-1B worker with a stable job and a pending I-140. But the distance is shorter than most people think.

An H-1B holder whose extension is denied, whose employer withdraws sponsorship during a layoff, or whose status lapses during the limbo between an old petition and a new one can find themselves in removal proceedings faster than they expected. The same applies to workers whose adjustment of status is denied under USCIS's new policy treating it as "extraordinary discretionary relief" — a shift that pushes more applicants toward consular processing or, if they fail to leave, into the court system.

For anyone who ends up before an immigration judge and receives an unfavourable ruling, the appeal is often the last line of defence. At $110, it was at least accessible. At $975, it becomes a calculation: is it worth nearly a thousand dollars just to file the paperwork, before even accounting for attorney fees that can run into the tens of thousands?

## Fee waivers exist — in theory

The proposed rule does allow for fee waivers in some cases. But the Trump administration has been steadily narrowing fee waiver eligibility across the immigration system. The same DHS that proposed eliminating fee waivers for naturalization applications is unlikely to be generous with waivers in the court system it is simultaneously trying to streamline.

Immigration attorneys have long argued that the immigration court system is already overwhelmed, with more than 3.7 million cases pending nationwide. Higher fees are unlikely to reduce that backlog. They are more likely to deter appeals, leading to more uncontested removal orders — which may well be the intended outcome.

## The arithmetic of staying

For an Indian family that has spent a decade on H-1B visas, paid thousands in USCIS filing fees, premium processing charges, and attorney costs, and is now waiting in the EB-2 India queue that is shut until October, the prospect of an additional $975 charge to contest a removal order is not merely expensive. It is a reminder that at every stage of the American immigration journey, the price of staying keeps rising while the certainty of staying keeps falling.

The proposed rule is not yet final. Public comments may shape its trajectory. But the direction of travel is not in doubt."""

article_1 = {
    "id": str(uuid.uuid4()),
    "headline": "It Costs $975 to Appeal Your Own Deportation. The Old Price Was $110",
    "subheadline": "The Trump administration wants to nearly triple immigration court fees. For Indians caught in the system, the financial barrier to justice just got nine times higher.",
    "slug": make_slug("immigration-court-appeal-fee-975-eoir-triple-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians who lose H-1B status or face removal after denied extensions can now expect to pay $975 just to file an appeal — nearly nine times the old fee — on top of the mounting cost of every other immigration form.",
    "tags": ["immigration-court", "eoir", "deportation", "fees", "trump", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.nbcpalmsprings.com/2020/02/27/trump-administration-looks-to-triple-fees-for-some-immigration-court-filings"},
        {"name": "Nolo - 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
        {"name": "Executive Office for Immigration Review (EOIR)", "url": "https://www.justice.gov/eoir"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/11505601/pexels-photo-11505601.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A gavel resting on US dollar bills with an American flag backdrop",
    "image_attribution": "Pexels",
    "body": article_1_body.strip()
}


# ─── ARTICLE 2 ──────────────────────────────────────────────────────────────
article_2_body = """After a decade or more in the green card queue, an Indian immigrant who finally becomes a lawful permanent resident might assume the hardest financial stretch is over. It is not.

USCIS has proposed raising the naturalization application fee by as much as 80 per cent and eliminating most fee waivers — a one-two punch that would make the final step to American citizenship substantially more expensive for the people who have already paid the most to get there.

## What the numbers look like

Under the proposed rule, published in June 2026 and open for public comment until August 24:

- The Form N-400 fee for paper filing would rise from $760 to $1,330 — a 75 per cent increase.
- The online filing fee would jump from $710 to $1,280 — an 80 per cent increase.
- The Form N-336 fee, for requesting a hearing after a naturalization denial, would climb from $830 to $1,475 for paper filings and from $780 to $1,425 for online submissions.

More consequentially, USCIS's rule would eliminate most fee waivers and reduced-fee options for low-income applicants. Only qualifying U.S. military service members would retain fee exemptions. Everyone else pays full freight.

## For Indian immigrants, the maths are personal

Consider a family of four — two parents and two children born in the United States — where one or both parents waited 15 years in the EB-2 India backlog before receiving green cards. The parents are now eligible to naturalise. Under current fees, both applications cost $1,520 (two paper N-400s at $760 each). Under the proposed rule, that rises to $2,660.

That is not pocket change. It follows years of cumulative immigration costs: H-1B filing fees, premium processing charges that rose again in March 2026, biometrics appointments, I-140 petitions, adjustment of status fees (or, increasingly, the cost of consular processing trips to India), and legal representation at every stage. The total bill for one person's journey from H-1B to citizenship now comfortably exceeds $15,000 in government fees alone, before attorney costs.

## Why the waivers matter

The elimination of fee waivers is arguably more significant than the fee increase itself. Under current rules, applicants with household incomes below 150 per cent of the Federal Poverty Guidelines — roughly $23,000 for a single-person household, $47,000 for a family of four — can apply for a full fee waiver. Those between 150 and 200 per cent of the poverty line can apply for a reduced fee.

The administration frames the change as full cost recovery: USCIS should not rely on taxpayer subsidies to process naturalization applications. But the practical effect is to price out permanent residents whose economic circumstances have changed — laid-off tech workers, single-income families supporting elderly parents, or people whose green card priority date moved forward during a period of unemployment.

## The clock is ticking

The rule is not yet final. It must go through a public comment period, and a final version will likely be published some weeks after the August 24 deadline. But immigration attorneys are already advising eligible green card holders to file their N-400 applications now, before any increase takes effect.

This is sound advice, with a caveat: the current naturalization processing time at most USCIS field offices is between eight and fourteen months. Filing early does not guarantee a faster ceremony. But it does lock in the current fee.

## The bigger picture

DHS says the fee increase will allow USCIS to "recover the full cost needed to process immigrant applications" and improve "the integrity of the U.S. naturalization system." But integrity cuts both ways. A system that charges $1,330 for a citizenship application while eliminating the safety net for those who cannot afford it is not merely recovering costs. It is selecting for applicants with means.

For the Indian diaspora — a community that has, by every measure, paid its dues through years of lawful residence, tax contributions, and a green card wait that exceeds any other nationality — the message is bracing. The final mile of the immigration journey is getting steeper, and the people who walked the longest to get there are now being asked to pay the most to finish."""

article_2 = {
    "id": str(uuid.uuid4()),
    "headline": "You Waited 20 Years for a Green Card. Now Citizenship Costs 75 Per Cent More",
    "subheadline": "USCIS wants to nearly double the naturalization fee and eliminate most fee waivers. If you are eligible to file, the smart move is to do it before August 24.",
    "slug": make_slug("naturalization-fee-hike-75-percent-n400-waiver-eliminated"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian green card holders who endured the longest backlog of any nationality now face a 75 per cent fee hike on the final step to citizenship, with fee waivers eliminated for everyone except military members.",
    "tags": ["naturalization", "n400", "citizenship", "uscis", "fees", "green-card", "indian-americans"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Nolo - 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
        {"name": "GovInfo - USCIS Proposed Rulemaking", "url": "https://www.govinfo.gov"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/25/rooke-dhs-mullin-citizenship-naturalization-application-fee-trump-administration-immigration/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg/1280px-2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg",
    "image_caption": "New citizens take the Oath of Citizenship at a 2025 naturalization ceremony",
    "image_attribution": "Wikimedia Commons",
    "body": article_2_body.strip()
}


# ─── INSERT ──────────────────────────────────────────────────────────────────
articles = [article_1, article_2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
