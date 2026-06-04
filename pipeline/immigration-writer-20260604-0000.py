#!/usr/bin/env python3
"""Immigration writer — 2026-06-04 00:00 UTC run"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 1: NIW Denial Rates Surpass EB-1A
# ─────────────────────────────────────────────────────────────────────────

art1_body = """For years, the EB-2 National Interest Waiver was the green card path of least resistance for Indian tech professionals. Skip the labour certification. Self-petition. Wait out the backlog with a priority date locked in. Compared with the EB-1A's demand for "extraordinary ability," NIW felt like the pragmatic choice — rigorous, sure, but accessible to anyone who could articulate a national-interest case around their engineering work or research.

That calculus has quietly inverted. USCIS data for the first quarter of fiscal year 2025 shows the EB-2 NIW denial rate at 37.2 per cent — nearly twelve points higher than the EB-1A's 25.1 per cent. It is the first time in the history of the two categories that NIW petitions are being rejected more frequently than those demanding proof of extraordinary ability.

https://x.com/USCIS/status/1870560922348957792

## The numbers behind the reversal

The shift did not happen overnight. In FY 2022, the NIW denial rate sat at 4.3 per cent while EB-1A hovered at 23.2 per cent — a gap of nearly twenty points in NIW's favour. By FY 2023 the NIW rate had surged to 20.3 per cent. In Q4 of FY 2024 it reached 29 per cent, drawing level with EB-1A's 27.7 per cent. And then it blew past.

| Fiscal Year | EB-1A Denial Rate | EB-2 NIW Denial Rate |
|---|---|---|
| FY 2022 | 23.2% | 4.3% |
| FY 2023 | 28.6% | 20.3% |
| FY 2024 Q4 | 27.7% | 29.0% |
| FY 2025 Q1 | 25.1% | 37.2% |

The volume tells part of the story. USCIS received 20,124 EB-2 petitions in Q1 alone but managed to approve only 4,722 and deny 2,799 — leaving more than 12,000 cases still pending. The backlog is feeding on itself: cases pile up, adjudicators tighten standards to manage throughput, and denial rates climb further.

## What changed at the adjudication window

Immigration attorneys point to three factors converging at once. First, USCIS is enforcing the *Matter of Dhanasar* framework with a rigour that would have surprised the lawyers who celebrated the 2016 decision as a liberalisation. The three-pronged test — that the endeavour has substantial merit and national importance, that the applicant is well-positioned to advance it, and that waiving the labour certification benefits the United States — is being read literally and sceptically, especially on the third prong. Generic claims about "contributing to the US technology ecosystem" no longer clear the bar.

Second, the pandemic-era surge in NIW filings created a volume that USCIS was never staffed or budgeted to handle. Between remote work expanding the pool of self-petitioners and the category's reputation as the safer bet, filings exploded. A policy recalibration was always coming; the question was whether it would arrive as a formal rule change or as a de facto tightening at the officer level. It arrived as the latter.

Third, there is the Requests for Evidence problem. RFE rates for NIW have climbed sharply, and when an RFE response fails to satisfy the officer — increasingly common as the goalposts shift — the case is denied rather than sent back again.

## What this means for Indians in the queue

India accounted for 813 EB-1A approvals in Q1 FY 2025, representing 17.2 per cent of all EB-1A approvals. Filings from India are increasing sharply, a trend driven partly by professionals who had been in the NIW lane and are now upgrading their petitions.

The strategic recalculation is straightforward. If you are an Indian tech professional with three or more qualifying criteria under the EB-1A's ten-factor test — peer-reviewed publications, a record of judging others' work, original contributions of major significance — the "harder" category now offers better odds of approval than the "easier" one. And EB-1A has a second advantage: its priority dates for India are far more current than EB-2's, meaning the green card itself arrives years sooner even after the petition is approved.

A January 2026 federal court ruling in *Mukherji v. Miller* may have shifted the ground further in EB-1A's favour. The judge found that USCIS's two-step adjudication process — meet three criteria, then pass a separate "final merits" review — violated the Administrative Procedure Act. If upheld, the ruling means that satisfying three criteria should be sufficient without the additional subjective gatekeeping that had driven up EB-1A denials in prior years.

## The dual-filing hedge

Immigration attorneys are increasingly advising clients to file EB-1A and EB-2 NIW petitions simultaneously, or to file EB-1A first and fall back to NIW only if the extraordinary ability case is weak. The cost of a second filing — typically $2,965 for premium processing on each — is modest compared with the years of limbo that a denied petition can produce.

For Indian professionals already in the EB-2 queue with an approved NIW, the priority date still holds its value: it can be ported to an EB-1A petition, preserving years of wait time. But for anyone filing fresh, the data is unambiguous. The path once called "easier" is now the one more likely to end in a denial letter."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The 'Easy' Green Card Path Just Got Harder Than the Hard One — NIW Denials Surpass EB-1A for the First Time",
    "subheadline": "USCIS data shows EB-2 National Interest Waiver petitions are now rejected at 37 per cent — twelve points above EB-1A's denial rate, upending the strategy that a generation of Indian tech professionals relied on.",
    "slug": make_slug("niw-denial-rate-surpasses-eb1a-indian-green-card-strategy"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian tech professionals have long treated the EB-2 NIW as the pragmatic green card route — self-petition, skip PERM, lock in a priority date. With NIW denial rates now exceeding EB-1A, the strategic calculus for hundreds of thousands of Indians in the queue has fundamentally changed. Dual-filing EB-1A alongside NIW is no longer a luxury hedge; it may be a necessity.",
    "tags": ["niw", "eb-1a", "green-card", "uscis", "immigration", "i-140"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/immigration/news/eb-2-niw-denials-now-outpace-eb-1a/"},
        {"name": "USCIS I-140 RADP Summary Tables", "url": "https://www.uscis.gov/tools/reports-and-studies/semi-annual-report-on-the-application-adjudication-framework"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/research/uscis-eb-1a-filings-high-approval-rates-dip/"},
        {"name": "Beyond Border Global", "url": "https://beyondborderglobal.com/eb-2-niw-india-wait-time/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/6358840/pexels-photo-6358840.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "body": art1_body
}

# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 2: OBBBA IFR — Fee Machine Now Running
# ─────────────────────────────────────────────────────────────────────────

art2_body = """On May 29, a new interim final rule went into effect that most Indian H-1B holders probably did not notice. Published by the Department of Homeland Security on April 29 under authority granted by the One Big Beautiful Bill Act, the IFR codifies a set of fees, deadlines, and work-authorisation restrictions that had been floating as statutory text since the law's July 2025 signing. Now they are regulation — enforceable, specific, and already shaping how USCIS processes cases.

The rule does four things. It establishes a $24 fee for Form I-94 arrival and departure records. It codifies a $100 asylum application fee plus a $100 annual fee for every year a case remains pending, with application rejection and potential removal proceedings for non-payment. It retains the Form I-589 filing fee even when an application is improperly filed. And it limits the validity period of employment authorisation for Temporary Protected Status holders to one year or the remaining designation period, whichever is shorter.

## The I-94 fee: small charge, large signal

Twenty-four dollars is not going to bankrupt anyone. But the I-94 fee applies to every arrival record — meaning every time an H-1B worker re-enters the United States after a trip to India, another $24 is added to the pile. Stack it on top of the $250 Visa Integrity Fee that the OBBBA also introduced for non-immigrant visa applicants, the $100,000 H-1B proclamation fee that the Trump administration imposed in September 2025, and the regular USCIS filing fees that have risen steadily, and a pattern emerges. The immigration system is being funded, one new charge at a time, by the people using it.

For a typical Indian family on H-1B and H-4 visas making an annual trip home, the cumulative cost of entry now includes two I-94 fees, two Visa Integrity Fees already paid at the consulate, any applicable premium processing fees, and — if the H-1B worker's employer elected to pay the $100,000 proclamation fee — a cost that has almost certainly been factored into compensation decisions. None of these fees existed two years ago.

https://x.com/USCIS/status/1870560922348957792

## EAD validity: a precedent, not just a TPS rule

The IFR's restriction on TPS-based employment authorisation — limiting EAD validity to one year instead of the previous longer periods — directly affects nationals from designated countries such as Haiti, Venezuela, and Myanmar. Indians are not currently TPS beneficiaries. But the mechanism matters more than the immediate population it targets.

By writing shorter EAD validity periods into regulation, DHS is establishing a template. The February 2026 proposed rule on asylum-based EADs already suggested pausing acceptance of EAD applications when processing times exceed 180 days and extending the waiting period to 365 days. If the principle of shorter, more conditional work authorisation documents becomes embedded across categories, H-4 EAD holders — overwhelmingly Indian spouses — could eventually face the same squeeze. The current H-4 EAD crisis, with processing delays already forcing thousands out of work and into mandamus lawsuits, would only deepen.

## The comment window closes June 29

Because DHS published the IFR as an interim final rule rather than a proposed rule, it takes effect before the comment period ends — a procedural choice that limits meaningful public input. But the comment window is open until June 29, 2026, through the federal eRulemaking portal under Docket ID USCIS-2026-0133.

Immigration advocacy organisations are urging affected communities to submit comments, particularly on the EAD validity restrictions and the I-94 fee structure. Comments do not need to be written in legal language; they need to be specific about how the rule affects real people. An H-4 spouse in Sunnyvale who lost her job because USCIS took eleven months to renew a work permit has a story that matters more to rulemaking than a law firm's boilerplate objection.

## The compounding cost of staying legal

What the OBBBA's fee architecture reveals, taken as a whole, is a philosophy of immigration funding that has shifted entirely onto the backs of applicants. The $100,000 H-1B proclamation fee generates revenue that DHS Secretary Mullin told the Senate last week was processing 200,000 applications in 15 days — while standard applicants wait 7.5 months. The $250 Visa Integrity Fee adds a fresh charge at every consular visa issuance. The $24 I-94 fee adds a toll at the border. The $100 annual asylum fee makes seeking protection an ongoing subscription.

For Indian professionals navigating this system — already paying employer-sponsored attorneys, USCIS filing fees, biometrics appointments, and premium processing surcharges — each new line item is manageable on its own. But the total is not. A rough accounting for an Indian H-1B worker renewing status, stamping a visa in India, and re-entering the US now runs well above $2,000 in government fees alone, before any legal costs. For the family in the EB-2 queue with a priority date twelve years from becoming current, those fees will be paid again and again, every renewal cycle, every trip, every year — with no guarantee that the green card will materialise before the next fee increase arrives.

The comment period closes June 29. The fees are already being charged."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Fee Machine Is Running — OBBBA's New I-94 Charges and EAD Limits Are Already in Effect",
    "subheadline": "A DHS interim final rule that took effect May 29 adds a $24 I-94 fee, caps TPS work-permit validity, and sets a precedent that could eventually reach H-4 EAD holders. The public comment window closes June 29.",
    "slug": make_slug("obbba-ifr-i94-fee-ead-limits-tps-h4-comment-period"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The I-94 fee and Visa Integrity Fee stack onto the already-rising cost of every re-entry for Indian families on H-1B and H-4 visas. The EAD validity restrictions, while targeting TPS holders now, establish a template that could worsen the H-4 EAD renewal crisis affecting hundreds of thousands of Indian spouses. The comment period closing June 29 is a rare window for direct input.",
    "tags": ["obbba", "i-94", "ead", "fees", "uscis", "h-4", "tps", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Federal Register / DOJ EOIR", "url": "https://www.justice.gov/eoir/federal-register-notices-2026"},
        {"name": "SWACCA", "url": "https://swacca.org/uscis-rule-imposes-new-fees-tightens-work-authorization-for-asylum-applicants-and-tps-holders/"},
        {"name": "BAL Immigration News", "url": "https://www.bal.com/resources/client-alerts/interim-final-rule-codifies-new-uscis-immigration-fees/"},
        {"name": "University of Illinois Chicago OIS", "url": "https://ois.uic.edu/new-immigration-fees-included-in-the-one-big-beautiful-bill-act/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "body": art2_body
}

# ─────────────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
