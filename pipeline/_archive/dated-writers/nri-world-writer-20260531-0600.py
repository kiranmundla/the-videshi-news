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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Australia Just Halved Its Regional Migration Intake. Indian Professionals Are Wondering What Happened to the Welcome Mat.",
        "subheadline": "Regional skilled visas slashed from 33,000 to 14,110 for 2026-27, the 491 pathway trimmed by 23 per cent, and a new IDP report says a quarter of Indian students now call visa uncertainty their biggest barrier to studying abroad.",
        "slug": make_slug("australia-halves-regional-migration-indian-professionals-squeeze"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian professionals in healthcare, engineering, and hospitality — the backbone of regional Australia's migrant workforce — face the sharpest impact. The cuts rewrite the calculus for tens of thousands of Indians who planned their careers around the regional pathway.",
        "tags": ["nri", "diaspora", "australia", "migration", "skilled-workers", "students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/pravasi-daily-news-27-05-2026/"},
            {"name": "Australian Government Budget 2026-27", "url": "https://www.homeaffairs.gov.au/"},
            {"name": "IDP Education Report 2026", "url": "https://www.idp.com/"},
            {"name": "AIVES Australia Migration Analysis", "url": "https://www.linkedin.com/pulse/2026-migration-shake-up/"},
            {"name": "Australian Bureau of Statistics", "url": "https://abs.gov.au/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1766230/pexels-photo-1766230.jpeg",
        "body": """For the better part of a decade, regional Australia has been the quieter, steadier migration pathway — the one that didn't require a Big Four sponsor or a Sydney postcode. Indian nurses in Shepparton, engineers in Toowoomba, hospitality workers in Darwin. They filled the gaps that metropolitan migration programmes couldn't reach, and they built lives in towns that needed them.

That arrangement just got substantially harder.

## The numbers that matter

The Australian government's 2026-27 budget confirms what migration analysts had been whispering since March: permanent skilled regional migration visas have been slashed from 33,000 to 14,110 — a cut of more than 57 per cent. The Subclass 491 (Skilled Work Regional) visa, the main feeder into regional permanent residency, saw its allocation trimmed from 9,760 to 7,500 places, a 23 per cent reduction. The overall permanent migration cap stays at 185,000, but within that number, the government is channelling more places toward employer-sponsored visas and the independent 189/190 pathways.

In plain terms: Canberra still wants skilled migrants. It just wants fewer of them to come through the regional door.

## Who gets hurt

Indian professionals are disproportionately concentrated in exactly the sectors and pathways that these cuts target. Healthcare workers — nurses, aged-care staff, allied health professionals — account for a significant share of regional visa grants to Indian applicants. Engineering and hospitality follow close behind. Many of these workers arrived on student visas, converted to Subclass 485 temporary graduate visas, then moved into the 491 regional pathway with the expectation that permanent residency sat at the end of a defined timeline.

That timeline just got longer, and the queue just got narrower.

Migration experts quoted by Pravasi Samwad say Indian professionals working in healthcare, engineering, and hospitality "are expected to be among the most affected groups." The arithmetic is brutal: roughly the same number of applicants competing for less than half the available places.

## The student anxiety problem

The squeeze at the permanent residency end is compounding a separate problem at the intake end. A new IDP Education report released this week found that more than 25 per cent of Indian students now view visa uncertainty as a "major barrier" to pursuing overseas education. Students cited changing immigration rules, higher financial requirements, and shrinking post-study work opportunities — not just in Australia, but across the English-speaking destination countries that compete for Indian enrolments.

Australia's international student numbers tell the story in retrospect. In 2022-23, more than 103,000 student visas were granted to Indian nationals. By 2024, that number had dropped to roughly 50,000. Early 2025 data shows the slide continuing: approximately 5,000 visas issued between January and March alone.

The Indian student pipeline has been Australia's second-largest after China. If the flow slows further, regional universities and the towns that depend on them will feel it — not eventually, but within an academic cycle.

## What Canberra is signalling

The government's stated position is that migration should be "outcome-based" — fewer arrivals, but better matched to labour market needs. The budget emphasises onshore skilled migrants already present in Australia as the priority, a pragmatic shift toward workers who are "locally present, partially integrated, and closer to meeting workforce needs."

For Indian migrants already on Australian soil, this is cautiously good news. The "grow-your-own" model — student visa to temporary graduate to employer sponsorship to permanent residency — still functions. What has changed is the width of the pipeline. Fewer entry points mean more competition at every stage.

For those still in India weighing their options, the calculation has shifted. Canada recently reduced its own processing times for Indian visitor visas and study permits, a move some analysts read as a competitive response to Australia's tightening. The UK remains expensive and post-study work rights are limited. The United States has its own H-1B bottleneck.

## The diaspora effect

Australia's Indian community numbers roughly 1.2 million — the country's fastest-growing diaspora population. These cuts don't just affect prospective migrants; they reshape the community that receives them. Fewer arrivals mean smaller weekend cricket leagues, thinner temple congregations in regional towns, fewer customers for the Indian grocery stores that have become fixtures of places like Ballarat and Cairns.

The Australian government insists it is calibrating, not closing. Regional employers, who have lobbied hard against the cuts, are not convinced. Neither are the migration agents whose client lists are dominated by Indian applicants.

For the Indian professional weighing Melbourne against Toronto, or Toowoomba against Tauranga, the spreadsheet just changed. Australia's welcome mat hasn't been pulled inside. But it has been folded in half."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "June 15 Is Two Weeks Away. Most Indian Americans With Accounts Back Home Still Haven't Filed What the IRS Wants.",
        "subheadline": "The extended tax deadline for Americans abroad is approaching, and for the millions of Indian Americans holding dormant EPF, PPF, and NPS accounts in India, the FBAR and FATCA reporting obligations remain a minefield of overlapping forms, rising penalties, and genuinely unsettled law.",
        "slug": make_slug("june-15-tax-deadline-nri-fbar-fatca-epf-ppf-nps-compliance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Nearly every Indian American who worked in India before emigrating holds at least one dormant account — an EPF balance from a first job, a PPF account opened by a parent, an NPS contribution that stopped the day they flew out. These balances compound quietly in rupees while US reporting obligations compound loudly in dollars.",
        "tags": ["nri", "diaspora", "tax", "fbar", "fatca", "epf", "ppf", "nps", "irs", "compliance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IRS Publication 54 - Tax Guide for U.S. Citizens Abroad", "url": "https://www.irs.gov/publications/p54"},
            {"name": "RebaseNest - FBAR and FATCA on EPF, PPF and NPS", "url": "https://medium.com/@RebaseNest_Team/fbar-and-fatca-on-epf-ppf-and-nps-what-h-1b-holders-actually-need-to-file-rebasenest-a452bc403e49"},
            {"name": "NorthJersey.com - Tax Deadline for Americans Abroad", "url": "https://www.northjersey.com/story/money/2026/05/29/tax-deadline-americans-abroad/"},
            {"name": "IRS Publication 5286 - FBAR/FATCA Overlap", "url": "https://www.irs.gov/pub/irs-pdf/p5286.pdf"},
            {"name": "FinCEN BSA E-Filing", "url": "https://bsaefiling.fincen.treas.gov/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6863244/pexels-photo-6863244.jpeg",
        "body": """Somewhere in a filing cabinet in Bengaluru, or perhaps in the records of a post office branch in Pune, there is an account with your name on it. You opened it years ago — maybe your parents opened it for you — and you haven't contributed since you left India. The balance is modest: a few lakh in an Employees' Provident Fund, a Public Provident Fund that matured and rolled over, a National Pension System account you contributed to for three years before your H-1B came through.

You are now, for US tax purposes, a US person. And the US government would very much like to know about those accounts. The deadline is June 15.

## Two forms, two agencies, one headache

The core confusion, and the reason most Indian Americans either over-report or under-report, is that there are two separate US disclosure regimes for foreign accounts, and they are not the same thing.

**FBAR** (FinCEN Form 114) is a Bank Secrecy Act filing administered by the Treasury Department. If the aggregate maximum value of all your foreign financial accounts exceeds $10,000 at any point during the calendar year — even for a single day — you must file. The FBAR deadline is April 15, with an automatic extension to October 15. It goes to the BSA E-Filing system, not to the IRS.

**Form 8938** (FATCA) is an Internal Revenue Code requirement, filed with your tax return and administered by the IRS. For a single filer living in the US, the threshold is $50,000 at year-end or $75,000 at any point during the year. Thresholds are higher for joint filers and for Americans living abroad.

Filing one does not satisfy the other. They go to different agencies. You may need to file both. The Government Accountability Office has noted the "duplicative reporting regime" creates "additional costs to the government to process and store the same or similar information twice." The taxpayer, naturally, bears the duplication burden in full.

## The EPF, PPF, NPS puzzle

This is where it gets genuinely complicated, because the classification of Indian retirement and savings instruments under US reporting law ranges from "settled" to "nobody actually knows."

**EPF** is the most straightforward case. Your employer contributed, you contributed, the balance sits in a trust administered by the EPFO. The financial-interest test in federal regulation is clear enough: the balance is yours, it accrues interest, you can withdraw it. Most US tax preparers report EPF on both FBAR and Form 8938 without controversy.

**PPF** is murkier. It is a government-administered savings scheme held at a bank or post office. There is no IRS or FinCEN ruling addressing PPF directly. Conservative preparers report it; a minority view holds that PPF functions as a government welfare programme outside the reporting definition. The classification is not formally settled. If your PPF balance plus your other Indian accounts puts you above the $10,000 FBAR threshold, the conservative path is to include it.

**NPS** is the most contested. It is a defined-contribution pension scheme, and the Form 8938 instructions reference an exclusion for "certain foreign social-security or similar programs." Some preparers treat NPS Tier-I within that exclusion; others treat it as a reportable custodial arrangement. Both positions have practitioner support. Neither has been tested by enforcement action.

## The penalty arithmetic

The stakes for getting this wrong have increased. The non-willful FBAR penalty rose to $16,536 per report in 2026 — per report, not per account. Willful violations can reach 50 per cent of the account balance. Form 8938 carries a $10,000 initial penalty, with an additional $10,000 per 30 days of continued failure after notice, up to $50,000.

For a first-generation Indian American holding a dormant EPF worth ₹8 lakh (roughly $9,500) and a PPF worth ₹5 lakh (roughly $5,900), the combined balance likely crosses the FBAR threshold. The penalty for not reporting it could exceed the balance itself.

## The India-side trap

Here is the asymmetry that catches most returnees and dual-filers: India's tax treatment of these instruments has no bearing on US reporting obligations. PPF interest is exempt under Section 10(11) of India's Income-tax Act. The US does not care. If the interest is taxable under US rules — and for PPF, most preparers treat it as taxable annual income — then it must be reported, and India's exemption provides no shelter.

If India did withhold tax, US foreign tax credit relief is available under IRC sections 901 and 904 via Form 1116. But where India tax is zero — as with PPF interest — there is nothing to credit on the US side. Tax-free in India does not mean tax-free in America.

## What to actually do

The practical checklist for any Indian American with accounts in India: pull the account number, institution name, and address for each account. Determine the maximum balance during the calendar year and the year-end balance, both in INR. Convert to USD using the Treasury Reporting Rate of Exchange for December 31. If the aggregate exceeds $10,000 at any point, file the FBAR. If your total foreign financial assets exceed the Form 8938 thresholds, file that too.

Americans living abroad get until June 15 to file their 2025 income tax returns — an automatic two-month extension from the standard April 15 deadline. If you live in the US but have foreign accounts, the FBAR extension runs to October 15 regardless.

None of this is optional. The IRS is clear: any US citizen or permanent resident must report worldwide income, even if earned or held in another country. The dormant ₹3 lakh PPF your father opened for you in 2008 is not exempt from this requirement because you forgot about it.

The qualified cross-border chartered accountant you have been meaning to call? Call them before June 15."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
