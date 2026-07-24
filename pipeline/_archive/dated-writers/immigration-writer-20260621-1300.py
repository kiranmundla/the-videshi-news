#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

art1_body = """Of all the people unsettled by President Trump's $100,000 H-1B fee, few had more to lose than the Indian doctor working a night shift in a rural American hospital. A federal court has, for now, taken that particular threat off the table — and the loudest cheers came from a group representing physicians of Indian origin.

The American Association of Physicians of Indian Origin (AAPI) this week welcomed a court ruling blocking the proposed $100,000 charge on H-1B physician visa applications. Its president, Dr. Amit Chakrabarty, framed the decision in deliberately apolitical terms. "This is not a political victory — it is a healthcare victory," he said. "It ensures that patients are not placed at risk due to policy barriers unrelated to clinical need."

## Why a Doctor's Visa Is Not Like a Coder's

The headline H-1B debate is usually about software engineers in Seattle and Bengaluru. But the visa quietly underpins something far less glamorous: staffing the hospitals that other doctors avoid.

International Medical Graduates — physicians trained outside the United States and Canada — make up roughly one in four practicing doctors in America. A large share of them are Indian. They cluster, disproportionately, in rural counties, safety-net hospitals, and the kind of underserved towns where a $100,000 levy is not a rounding error but a deal-breaker.

A rural hospital operating on thin margins cannot simply absorb a six-figure surcharge to hire one hospitalist. AAPI's argument was blunt: faced with that bill, hospitals would have withdrawn job offers, left vacancies unfilled, and deepened the physician shortages already strangling rural healthcare. The fee, in other words, would not have hit Google. It would have hit the emergency room two hours from the nearest city.

## The Legal Knot

The $100,000 charge traces back to Presidential Proclamation 10973, which the administration cast as a tool to "restore market discipline" to a program it considers abused. In a separate but related case, a Massachusetts federal judge, Leo Sorokin, struck down the broader fee, treating it as an unauthorized tax that the executive branch had no power to impose without Congress.

For physicians specifically, the blocked requirement removes — temporarily — an existential cost. But the operative word is temporarily. These are trial-court rulings, not settled law. The administration is widely expected to appeal, and the same legal machinery that produced the fee can produce another version of it.

## What It Means for the Indian Diaspora

For Indian-American families, this is more personal than an abstract policy fight. The pipeline of Indian doctors into the U.S. is one of the diaspora's oldest and most established routes — a generation of NRIs built their American lives on a J-1 or H-1B that led from an Indian medical college to a residency in Ohio or Pennsylvania to, eventually, a green card.

That pathway has always carried a peculiar cruelty. Because of per-country green card caps, an Indian physician can spend a decade or more on an H-1B, legally required to keep working as a doctor to maintain status. Lose the job — as happened to hospitalist Dr. Maheswara Reddy Koppula when his Pennsylvania hospital closed in 2025 — and the clock starts ticking on leaving the country entirely. A $100,000 entry toll would have made an already precarious path almost unwalkable for new arrivals.

For the Indian doctor weighing whether America is still worth it, this ruling is a reprieve, not a resolution. The smarter response is to treat it as breathing room: confirm with an immigration attorney how the decision affects a pending or planned petition, and watch the appeals docket closely. The fee was struck down in a courtroom. It can be revived in one too.

The deeper lesson for the diaspora is structural. As long as Indian physicians are funneled through the same backlogged, per-country-capped system as Indian engineers, their stability depends on court rulings that can flip with a single appeal. The cheering this week is real. So is the fine print."""

art2_body = """For years, the deal felt manageable. Indian students applying for an F-1 visa grumbled about handing over their social media handles, set their Instagram to public for a few weeks, and got on with the business of getting to campus. From December 15, that same demand reaches a far larger and far more anxious population: H-1B workers and their H-4 spouses.

The State Department's requirement that visa applicants make all social media accounts "public" for vetting — first imposed on student and exchange categories (F, M and J) — is set to expand to H-1B and H-4 applicants on December 15, 2025, according to guidance circulated by university international offices. For the Indian diaspora, which dominates both categories, it converts a private digital life into part of the visa file.

## From a Handle to the Whole Profile

This is not the 2019 rule that asked applicants to list their social media usernames. That was disclosure. The new standard is access. Consular officers are instructed to ask applicants to switch every account to public, and they have been told that "limited access" to an applicant's online presence "could be construed as an effort to evade or hide certain activity."

The criteria officers are told to look for are expansive and, critics say, dangerously vague. Cables describe screening for "hostile attitudes" toward the United States, its citizens, culture, or founding principles, alongside more concrete grounds like support for terrorism or antisemitic harassment. There is no public definition of where ordinary political opinion ends and a "hostile attitude" begins — and that ambiguity is the point of contention.

## The 221(g) Trap

The mechanics matter as much as the rule. Enhanced vetting is run through Section 221(g) "administrative processing," which means an application can sit in limbo for weeks or months while an officer reviews an applicant's posts, tagged photos, and connections. Crucially, during that wait the official status reads "Refused" — even when nothing is actually wrong.

For an H-1B worker, that is not a paperwork curiosity. It is a frozen start date, a nervous employer, and a family's plans on hold. The State Department has explicitly barred consular officers from working to production quotas, instructing them to "take the time necessary." Thorough is reassuring in principle. In practice, for Indians already facing 10-to-12-month interview waits at jammed consulates, it means slower still.

## Why Indians Feel This First

Indians account for roughly 70% of approved H-1B petitions and form one of the largest H-4 dependent populations in the country. When a rule attaches to those categories, it attaches, overwhelmingly, to Indian applicants.

The H-4 angle is especially fraught. These are spouses — overwhelmingly women — who in many cases have built years of life in the United States, some with their own work authorization. Asking them to expose every personal account to consular review, on pain of delay or denial, lands differently than it does for a 22-year-old heading to a master's program.

## What the Diaspora Should Actually Do

The temptation, on hearing this, is to scrub everything — delete old posts, nuke accounts, go dark. Immigration lawyers warn that is exactly the wrong instinct. Deleting an account you previously disclosed, or that an officer can tell once existed, reads as evasion, the very thing the rule punishes. Listing every platform used in the past five years remains mandatory, and an undisclosed account discovered later is itself grounds for denial.

The practical playbook is less dramatic: list every account honestly, set them to public before the interview rather than after, and assume an officer will read what is there. For NRIs accustomed to treating their feeds as a personal space, the harder adjustment is conceptual — from December, for anyone on the H-1B track, the social media account is no longer just yours. It is part of your application."""

art3_body = """Buried in the noise of fee fights and visa-bulletin retrogressions is a bill that, if it ever passed, would do something almost unheard of for Indians stuck in the green card line: let some of them skip the per-country cap entirely. The catch is the "if."

The Healthcare Workforce Resilience Act (H.R. 5283 in the House, S. 2759 in the Senate) has been reintroduced in the 119th Congress with bipartisan, bicameral backing and the endorsement of the American Hospital Association. Its mechanism is narrow but, for the right applicant, transformative. It would "recapture" employment-based green cards that Congress authorized in past years but were never actually issued — up to 25,000 reserved for foreign nurses and 15,000 for physicians.

## The Part That Matters for Indians

Two features make this bill unusually consequential for the Indian diaspora.

First, the recaptured visas would be exempt from the per-country numerical limitation. That cap — which holds any single country to a small slice of the annual employment-based total regardless of how many of its nationals are waiting — is the single biggest reason Indians face green card waits measured in decades while applicants from smaller countries clear in a year or two. A visa pool that ignores the cap is, for an Indian doctor or nurse, a different universe.

Second, the visas would be issued in order of priority date. For someone who has been waiting since 2013 or 2014 — exactly where the EB-2 and EB-3 India final action dates currently sit — seniority in line finally becomes an asset rather than a cruel formality.

## Not New Visas, and Not for Everyone

The bill's sponsors, Senators Kevin Cramer and Dick Durbin, are careful to frame it as a realignment, not an expansion. "It does not authorize any new visas," the framing stresses; it merely puts unused, already-authorized green cards back into circulation. That design is deliberate — it lets the bill sidestep the politically toxic charge of "increasing immigration" at a moment when the administration is doing the opposite.

The limits are real, though. Only nurses and physicians qualify. Employers must attest the hires will not displace American workers. Applicants must meet licensing requirements, pay filing fees, and clear national-security and criminal background checks. And recaptured visas are available only when a visa is not otherwise immediately available — meaning this is explicitly a backlog-relief valve, not a queue-jump for everyone.

## A Familiar Graveyard

Indian-Americans who follow immigration policy will recognize the pattern, and the heartbreak in it. Bills to ease the green card backlog — the EAGLE Act, the RELIEF Act, various recapture proposals — are introduced session after session, draw warm bipartisan words, and then die in committee or get stripped out of larger packages. A version of this very healthcare bill passed the House in a previous Congress before stalling in the Senate.

So the honest read for the diaspora is twofold. The bill is genuinely well-aimed: it targets exactly the choke point — the per-country cap — that traps Indian medical professionals, and it does so through a fiscally and politically modest mechanism that has cleared at least one chamber before. That is more than most backlog bills can claim.

But "introduced" is not "passed," and a diaspora that has watched a decade of such bills evaporate should plan around the law as it is, not as it might be. For an Indian nurse or doctor in the EB-3 queue, the practical move is to keep the priority date pristine, maintain status, and treat H.R. 5283 as a reason to call your representative — not a reason to change your timeline. The bill points at the right problem. Whether Washington finally acts on it is the question that has gone unanswered for years."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Court Just Spared Indian Doctors a $100,000 Visa Bill. The Reprieve Comes With Fine Print",
        "subheadline": "A federal ruling blocked the proposed six-figure fee on H-1B physician visas. For the Indian doctors keeping rural American hospitals open, it's relief — but only until the appeal.",
        "slug": make_slug("h1b-physician-100k-fee-blocked-aapi-indian-doctors-img-rural"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-origin physicians make up a large share of the International Medical Graduates staffing rural and underserved US hospitals, and a $100,000 H-1B fee would have hit exactly the doctors and hospitals least able to pay it.",
        "tags": ["h1b", "physicians", "aapi", "img", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE — AAPI Applauds Court Ruling Blocking $100,000 H-1B Physician Visa Requirement", "url": "https://theindianeye.com/"},
            {"name": "South Asian Herald — AAPI Welcomes Court Ruling", "url": "https://southasianherald.com/"},
            {"name": "The Hospitalist — Essential, Yet Unsettled: H-1B Hospitalists", "url": "https://www.the-hospitalist.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4173244/pexels-photo-4173244.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hospital corridor; International Medical Graduates make up roughly one in four practicing US physicians.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "From December, the US Wants H-1B and H-4 Applicants to Open Up Their Social Media",
        "subheadline": "The 'make your accounts public' rule that hit student visas is set to expand to work-visa applicants and their spouses on December 15 — and Indians fill both lines.",
        "slug": make_slug("social-media-public-vetting-h1b-h4-december-15-indians-f1"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians account for about 70% of approved H-1B petitions and a huge share of H-4 dependents, so a vetting rule attached to those categories falls overwhelmingly on Indian applicants and their families.",
        "tags": ["h1b", "h4", "social-media-vetting", "state-department", "f1", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE — US Embassy in India warns visa holders screening continues", "url": "https://theindianeye.com/"},
            {"name": "Stanford Bechtel International Center — Social Media Vetting in U.S. Visa Applications", "url": "https://bechtel.stanford.edu/"},
            {"name": "NAFSA — Eleven Things to Know About the New Social Media Vetting Guidelines", "url": "https://www.nafsa.org/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5633334/pexels-photo-5633334.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smartphone showing social media apps; US consular vetting now reviews applicants' public online presence.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bill in Congress Would Let Indian Nurses and Doctors Skip the Green Card's Country Cap. If It Passes",
        "subheadline": "The Healthcare Workforce Resilience Act would recapture 40,000 unused green cards for medical workers — and exempt them from the per-country limit that traps Indians for decades.",
        "slug": make_slug("healthcare-workforce-resilience-act-recapture-green-cards-nurses-physicians-india-country-cap"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The per-country green card cap is the single biggest reason Indians face decades-long waits, and this bill would let recaptured visas for nurses and physicians bypass it — directly targeting the choke point that hurts Indian medical professionals most.",
        "tags": ["green-card", "per-country-cap", "nurses", "physicians", "legislation", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Congress.gov — H.R.5283 Healthcare Workforce Resilience Act (119th Congress)", "url": "https://www.congress.gov/bill/119th-congress/house-bill/5283"},
            {"name": "AHA News — Congress reintroduces bipartisan workforce bill supporting foreign nurses, physicians", "url": "https://www.aha.org/news"},
            {"name": "Sen. Kevin Cramer — Cramer, Durbin Introduce Merit-Based Immigration Policy", "url": "https://www.cramer.senate.gov/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7016960/pexels-photo-7016960.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The US Capitol in Washington, where the Healthcare Workforce Resilience Act has been reintroduced.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": art3_body
    }
]

def wc(t): return len(t.split())
for art in articles:
    print(f"   words={wc(art['body'])} headline_len={len(art['headline'])} sub_len={len(art['subheadline'])}")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
