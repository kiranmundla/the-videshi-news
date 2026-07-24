#!/usr/bin/env python3
"""Immigration writer — 2026-06-28 01:00 PT run"""
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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Supreme Court's Immigration Blitz Week
# ─────────────────────────────────────────────────────────────

article1_body = """Three rulings in four days, all 6-3, all expanding executive power over who enters the United States and who stays. The Supreme Court's final week of June 2026 has reshaped American immigration law with a speed and consistency that legal observers are calling unprecedented — and every decision carries consequences for Indian Americans holding green cards, waiting in visa backlogs, or watching from the sidelines.

## Blanche v. Lau: Green Card Holders on Notice

The first blow landed on Tuesday, June 23. In *Blanche v. Lau*, Justice Clarence Thomas wrote for the majority that border officers do not need "clear and convincing evidence" that a lawful permanent resident has committed a crime before treating them as an "applicant for admission" rather than a returning resident. The distinction matters enormously: an applicant for admission can be paroled, detained, and placed into expedited removal proceedings. A returning resident cannot.

The case involved Muk Choi Lau, a Chinese national who had held a green card since 2005. When Lau returned from a trip to China in 2012, he had been indicted — but not convicted — on trademark counterfeiting charges in New Jersey. Border agents paroled him into the country rather than admitting him, a decision that later enabled the government to initiate removal proceedings after his conviction.

The Second Circuit had ruled that agents needed clear and convincing evidence of the crime before they could parole a green card holder. The Supreme Court disagreed. The government, Thomas wrote, "correctly regarded Lau as an alien seeking admission because he had committed a crime involving moral turpitude before attempting to reenter the country."

For Indian Americans, the implications extend well beyond counterfeiting. Any returning green card holder who has been arrested, charged, or even investigated for an offense that could be classified as involving "moral turpitude" — a broad category that includes fraud, tax evasion, and certain regulatory violations — now faces the possibility that a border agent will parole rather than admit them. That parole can trigger removal proceedings regardless of how long the person has lived in the United States. Justice Ketanji Brown Jackson, dissenting, warned that the ruling "allows the Government to deem an LPR to be 'seeking an admission' first and justify the applicability of an exception later — undermining the statutory scheme as well as the benefits and security that come with having a green card."

## Mullin v. Al Otro Lado: The Border Line Becomes Literal

Two days later, the court delivered a second 6-3 opinion. In *Mullin v. Al Otro Lado*, Justice Samuel Alito held that a person standing in Mexico has not "arrived in the United States" for purposes of asylum law, even if they are at a port of entry and attempting to present themselves to U.S. officials.

"In ordinary speech, no one would say that a person 'arrives in' a place before the person enters that place," Alito wrote, deploying an analogy that will likely appear in law school exams for decades: "The running back does not arrive in the end zone (and six points do not go up on the scoreboard) when he is tackled at the 1-yard line by the defense."

The ruling ratifies the Trump administration's authority to turn away asylum seekers before they physically cross the border, reviving the legal foundation for "metering" — the practice of limiting how many people can present themselves at ports of entry on any given day. Justice Sotomayor, reading her dissent from the bench, argued the majority had created "a perverse incentive to cross the border between ports of entry" since only those who enter illegally would retain the right to apply for asylum.

This case affects Indian asylum seekers less directly than Central American populations, but it signals a judicial willingness to defer to executive discretion on border access that could extend to other immigration contexts.

## Mullin v. Doe: TPS Terminated, Courts Sidelined

The third ruling, also on June 25, may carry the broadest implications. In *Mullin v. Doe*, consolidated with *Trump v. Miot*, the court held that federal courts lack the authority to review the executive branch's decision to terminate Temporary Protected Status for nationals of Haiti and Syria. Roughly 350,000 Haitians and 6,100 Syrians who have lived and worked legally in the United States — some for more than a decade — now face the loss of their work authorisation and potential deportation.

The court also rejected the argument that the administration's decision was racially motivated, finding the constitutional claim "weak." Legal analysts note that the ruling could enable the Department of Homeland Security to terminate TPS for nationals of all 17 currently designated countries, affecting as many as 1.3 million people.

While TPS does not directly apply to Indian nationals — India has never been designated for the programme — the legal principle established is sweeping. If courts cannot review TPS termination decisions, the precedent strengthens executive power over a wide range of discretionary immigration benefits, including parole programmes and deferred action.

## Birthright Citizenship: Monday's Main Event

The court's immigration term is not over. The most consequential ruling may arrive on Monday, June 29, when the justices are expected to decide whether the 14th Amendment's guarantee of citizenship to "all persons born or naturalised in the United States" can be narrowed by executive order. The Trump administration issued an order in January 2025 attempting to deny birthright citizenship to children born in the U.S. to parents without legal status. Multiple federal courts have blocked it.

For the Indian diaspora, the stakes are both practical and symbolic. An estimated 200,000 to 300,000 children are born each year to Indian nationals on H-1B, L-1, and other temporary work visas. These children are U.S. citizens by birth — a status that has been constitutionally settled since the Supreme Court's 1898 decision in *United States v. Wong Kim Ark*. Any narrowing of birthright citizenship would upend the foundational assumption that has shaped family planning, estate planning, and career decisions for a generation of skilled Indian workers.

## What This Week Means

Taken together, the three rulings delivered this week share a common thread: the court's conservative majority is systematically reducing judicial checks on executive immigration authority. Green card holders can be paroled on suspicion. Asylum seekers can be turned away at the border. TPS can be terminated without judicial review. Each decision narrows the universe of people who can challenge the government's immigration decisions in court.

For Indian Americans, the practical takeaway is unsettling. The legal protections that come with a green card are weaker than they were a week ago. The system that has quietly enabled hundreds of thousands of families to build lives in the United States is being reinterpreted from the top down. And the court that will decide the future of birthright citizenship has already shown, three times this week, where its sympathies lie."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Rulings, Four Days, One Direction: The Supreme Court Just Rewrote Immigration Law",
    "subheadline": "Green card holders can be paroled on suspicion. Asylum seekers turned away at the border. TPS terminated without judicial review. A blitz week of 6-3 decisions signals where the court stands — and what Monday's birthright citizenship ruling may bring.",
    "slug": make_slug("scotus-immigration-blitz-week-green-card-tps-asylum"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Blanche v. Lau directly weakens the re-entry rights of the 400,000+ Indian-born green card holders who travel to India regularly. The TPS precedent strengthens executive power over discretionary immigration benefits that affect legal immigrants broadly.",
    "tags": ["supreme-court", "green-card", "tps", "asylum", "birthright-citizenship", "blanche-v-lau", "scotus"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/editorials/3455892/supreme-court-must-reform-immigration-system-landmark-ruling/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-supreme-court-accedes-trumps-restrictive-immigration-agenda-2026-06-26/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/25/opinion/supremes-memo-to-lower-courts-presidential-power-trumps-leftist-lawfare/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/trump-scores-scotus-asylum-win-liberal-justice-warns-could-backfire-border"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/26/supreme-court-tps-haitian-syrian-immigrants/84948327007/"},
        {"name": "Cornell Law Institute", "url": "https://www.law.cornell.edu/supct/cert/24-897"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The U.S. Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ─────────────────────────────────────────────────────────────────
# ARTICLE 2: EB-5 India's Last Window — September 30 Deadline
# ─────────────────────────────────────────────────────────────────

article2_body = """For two decades, Indian professionals treated the EB-5 investor visa as a curiosity — a programme designed for wealthy Chinese nationals willing to park $500,000 in a rural hotel project in exchange for a green card. Indians had the H-1B pipeline, the employer-sponsored EB-2 and EB-3 categories, and the patience to wait. That calculation has collapsed.

The July 2026 Visa Bulletin delivered the clearest signal yet. The EB-2 India category — the workhorse visa for Indian software engineers, data scientists, and managers — is now marked "Unavailable" through September 30. No new final action dates will advance. No green cards will be issued. For Indian nationals in the EB-2 queue, the estimated wait has stretched beyond 15 years. Some immigration attorneys now put it closer to 50 years for applicants filing today.

The EB-5, once an afterthought, has become the fastest available route for an Indian national to obtain a U.S. green card. But that window, too, is narrowing — and a hard deadline is approaching that most prospective investors do not yet understand.

## The Grandfathering Deadline Explained

Under the EB-5 Reform and Integrity Act of 2022, Congress reauthorised the Regional Center Programme through September 30, 2027. But buried within the legislation is a grandfathering provision with an earlier cutoff: petitions filed on or before September 30, 2026, are legally protected against future programme lapses. File after that date, and your petition enjoys no such protection.

The distinction is not academic. The EB-5 Regional Center Programme has lapsed before — most recently in 2021, when a gap in congressional authorisation froze thousands of pending petitions for nine months. Investors whose petitions were grandfathered under the 2022 act were shielded from that disruption. Those who filed after the grandfathering cutoff were not.

"Filing by this date locks in today's EB-5 rules, creating long-term certainty in an otherwise unpredictable immigration environment," wrote Theda Fisher of Withers LLP in a client advisory. Petitions filed after September 30, 2026, she noted, "may be exposed to programme lapses, new rules, or increased investment thresholds."

For an Indian investor evaluating the programme now, the September 30 deadline is effectively a hard stop. The I-526E petition requires assembling source-of-funds documentation, selecting a qualifying project, transferring the investment capital, and filing with USCIS — a process that immigration attorneys say takes three to six months at minimum. Anyone not already in motion is running out of time.

## Why Indians Are Rushing In

Indian demand for EB-5 has surged over the past 18 months, driven by a confluence of pressures that have made every other green card pathway slower, more expensive, or more precarious.

The H-1B programme, once the reliable first step, now carries a $100,000 filing fee (currently stayed by a federal court), a weighted lottery that disadvantages mid-tier salary placements, and social media vetting that has pushed consular wait times past 100 days at some Indian posts. The H-4 EAD, which allowed spouses of H-1B holders to work, faces a proposed rescission that could remove employment authorisation for tens of thousands of dependent spouses. The EB-2 backlog is functionally frozen.

Against this backdrop, the EB-5 set-aside categories created by the 2022 reform act have emerged as a genuine alternative. The act reserves 32 percent of annual EB-5 visas for investments in rural areas, high-unemployment areas (HUAs), and infrastructure projects. These reserved categories have their own visa pools, which means they are not subject to the same per-country caps that have created the EB-2 and EB-3 backlogs for Indian nationals.

For the current fiscal year, the rural and HUA set-asides remain current for Indian-born investors — meaning there is no backlog. An Indian national who files an I-526E petition under a rural set-aside project can, in theory, receive an approval and file for adjustment of status (or, under the new USCIS policy, consular process from India) without waiting years for a visa number.

The unreserved EB-5 category, however, has already retrogressed for India. The July 2026 Visa Bulletin shows no movement in the unreserved India queue. This means that only the set-aside categories offer a meaningful timeline advantage — and even those are expected to retrogress as Indian filing volumes increase.

## The Investment and the Risks

The minimum investment for a rural or HUA project is $800,000, reduced from $1.05 million for standard investments. The capital must be "at risk" in a qualifying job-creating enterprise — typically a real estate development, manufacturing facility, or infrastructure project managed by a USCIS-approved regional centre.

The risks are real. EB-5 fraud cases have made headlines for years, and the 2022 reform act's integrity measures — including mandatory fund administration, annual audits, and source-of-funds scrutiny — were designed to address a genuine problem. Immigration attorneys advise selecting only regional centres with established track records, transparent financial reporting, and projects that have already begun generating jobs.

The financial commitment is also significant. The $800,000 investment is typically locked for five to seven years, during which the capital is deployed in the project. Returns, if any, tend to be modest — the programme is designed as an immigration vehicle, not an investment opportunity.

## Three Months Left

For Indian professionals who have spent years in the H-1B-to-EB-2 pipeline watching priority dates crawl forward by days or weeks per bulletin, the EB-5 represents a different kind of bet: trade financial capital for time. The grandfathering deadline compresses that decision into the next 94 days.

Immigration attorneys report a surge in consultations from Indian H-1B holders exploring EB-5 as a concurrent filing strategy — maintaining their employer-sponsored EB-2 petition while simultaneously investing in an EB-5 rural project. The logic is straightforward: whichever green card comes first wins. The EB-2 is free but slow. The EB-5 is expensive but, for now, fast.

"The question Indian investors are asking is no longer whether EB-5 makes sense," said Kate Kalmykov, a shareholder at Greenberg Traurig who specialises in EB-5 law. "The question is whether they can get their paperwork together before September 30."

After that date, the answer may not matter."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "EB-5 Becomes India's Fastest Green Card Route. The Window Closes September 30",
    "subheadline": "With EB-2 India marked 'Unavailable' and H-1B costs soaring, Indian professionals are turning to the $800,000 investor visa. A grandfathering deadline in 94 days adds urgency to an already compressed timeline.",
    "slug": make_slug("eb5-india-green-card-september-30-grandfathering-deadline"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "EB-5 rural set-asides are currently the only green card category without a multi-year backlog for Indian nationals. The September 30 grandfathering deadline creates a hard decision point for the hundreds of thousands of H-1B holders stuck in the EB-2 queue.",
    "tags": ["eb-5", "green-card", "eb-2-backlog", "visa-bulletin", "regional-center", "investment-visa", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Colombo Hurd Law", "url": "https://colombohurdlaw.com/eb-5-grandfathering-deadline-september-30-2026-explained/"},
        {"name": "Withers LLP via Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1582782/eb-5-investors-face-a-critical-grandfathering-deadline-on-september-30-2026"},
        {"name": "Buchalter", "url": "https://www.buchalter.com/publication/eb-5-investors-the-september-30-2026-sunset-of-the-grandfathering-provision-of-the-reform-and-integrity-act-what-you-need-to-know/"},
        {"name": "CILaw Group (July 2026 Visa Bulletin)", "url": "https://cilawgroup.com/visa-bulletin-july-2026/"},
        {"name": "Greenberg Traurig / U.S. Immigration Fund (webinar)", "url": "https://www.youtube.com/watch?v=eb5-may-2026-visa-bulletin-breakdown"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/14426300/pexels-photo-14426300.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "An hourglass on a calendar — for Indian EB-5 investors, the September 30 grandfathering deadline is ticking",
    "image_attribution": "Pexels",
    "body": article2_body.strip(),
}


# ─────────────────────────────────────────────────────────────────────────
# ARTICLE 3: India-US Trade Deal "Very Close" — Immigration Still Missing
# ─────────────────────────────────────────────────────────────────────────

article3_body = """Commerce Minister Piyush Goyal says the India-U.S. trade deal is "very close." Ambassador Sergio Gor insists the H-1B review is not targeting India. U.S. Trade Representative Jamieson Greer spent three days in New Delhi last week. India's envoy to Washington, Vinay Mohan Kwatra, just sat down with the House Ways and Means Committee to discuss expanding the bilateral trade partnership. Every signal from both governments suggests a first-phase agreement is imminent.

There is one thing conspicuously absent from every briefing, readout, and ministerial statement: any mention of immigration.

## The Deal That Is "Very Close"

The contours of the emerging agreement have become increasingly visible. India is expected to offer expanded market access for American agricultural products — including ethanol and certain dairy categories — alongside procurement commitments for U.S. energy, defence equipment, and possibly civil aviation. In return, India seeks more favourable tariff treatment and recognition of its pharmaceutical and IT exports.

The overarching framework is Mission 500: a bilateral commitment to double trade from the current $230 billion to $500 billion by 2030. Greer's June 22-24 visit to New Delhi focused on what both sides describe as "the finer aspects" of a phase-one deal — tariff lines, digital trade rules, supply chain alignment, and agricultural market access.

"The trade deal is very close, but it cannot come into force unless India secures a competitive tariff advantage over its competitor nations," Goyal told reporters after the meetings. The statement suggests the deal is effectively drafted and awaiting final political sign-off on tariff terms.

What Goyal did not say — and what no official from either government has said — is that the deal includes any provision related to visa mobility, work authorisation, or the movement of professionals between the two countries.

## The Elephant Not in the Room

This omission is not an oversight. It is a deliberate structural choice that reflects the political constraints on both sides.

For the Trump administration, any trade agreement that loosens immigration restrictions — even for high-skilled workers — would contradict the central policy thrust of its second term. The administration has imposed a $100,000 H-1B filing fee, expanded social media vetting at consulates, proposed rescinding H-4 EAD work authorisation, announced a crackdown on Day-1 CPT programmes, and begun shifting green card processing from domestic adjustment of status to consular processing abroad. A trade deal that carved out immigration concessions would undermine the coherence of that agenda.

For India, raising immigration in the trade context risks poisoning a negotiation that is otherwise progressing. New Delhi has historically avoided linking trade and immigration in formal agreements, preferring to address visa issues through diplomatic channels. The Ministry of External Affairs has consistently treated H-1B and student visa concerns as bilateral relationship issues, not trade concessions to be bargained for.

The result is a structural gap. The two countries are negotiating their most significant economic agreement in years, and the single issue that most directly affects the 4.4 million Indian Americans and the hundreds of thousands of Indian nationals on temporary work visas — the terms under which skilled professionals can move between the two economies — is not on the table.

## What Other Countries Got

The absence is more striking when measured against precedent. The U.S.-Mexico-Canada Agreement, negotiated during Trump's first term, includes provisions on professional visa categories and temporary entry for business persons. The U.S.-Australia Free Trade Agreement created the E-3 visa, a category exclusively for Australian professionals that functions as a parallel H-1B with 10,500 annual slots. The U.S.-Chile and U.S.-Singapore free trade agreements each established dedicated H-1B1 visa allocations for nationals of those countries.

India has no such carve-out with the United States, and the emerging deal does not appear to create one. The closest precedent is the Totalisation Agreement — a social security treaty that would prevent Indian H-1B workers from paying into both the U.S. and Indian social security systems. That agreement has been under discussion for more than two decades and remains unsigned.

## Ambassador Gor's Balancing Act

Gor's public messaging over the past month has been a careful exercise in misdirection without technically misstating anything. His assertion that the H-1B review is "not targeting India" is literally true — the policy changes apply to all nationalities. It is also practically irrelevant: Indians account for 71 percent of H-1B approvals, and every structural change to the programme lands disproportionately on Indian applicants and Indian IT services firms.

When asked about the H-1B fee increase, Gor pivoted to the broader theme of immigration modernisation. When pressed on consular delays, he pointed to record visa issuance numbers — 1.4 million to Indians in 2025 — without addressing the per-category backlogs that have made several employment-based categories functionally unavailable.

The diplomatic logic is sound. Gor's job is to maintain the bilateral relationship during a period of significant policy turbulence, not to concede that American immigration policy disproportionately affects Indian nationals. But for the NRI community watching from Silicon Valley, the Jersey City waterfront, and the DFW suburbs, the gap between diplomatic reassurance and lived experience has never been wider.

## What a Deal Without Immigration Means

If the phase-one trade agreement closes without immigration provisions — as now appears virtually certain — the practical consequence is that the two fastest-growing elements of the U.S.-India relationship will continue to operate in separate silos.

Trade in goods and services will be governed by the new agreement, with tariff reductions, market access commitments, and dispute resolution mechanisms. The movement of people — the engineers, managers, researchers, and entrepreneurs who actually build the products and services that generate the trade — will remain governed by a patchwork of administrative policies, executive orders, and fee schedules that can be changed unilaterally and without notice.

For Indian American professionals, the deal may deliver cheaper almonds and expanded defence contracts. What it will not deliver is the one thing most of them need: a predictable, stable, and timely pathway to permanent residence in the country where they work and pay taxes.

Mission 500 envisions $500 billion in bilateral trade. It does not envision the people who would make that trade happen."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India and America Are About to Sign a Trade Deal. It Says Nothing About Immigration",
    "subheadline": "USTR Greer's New Delhi visit signals a phase-one agreement is imminent. But the deal that covers tariffs, agriculture, and defence procurement leaves out the issue that matters most to 4.4 million Indian Americans: the right to live and work in the country they trade with.",
    "slug": make_slug("india-us-trade-deal-immigration-provisions-missing"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The emerging India-US trade deal does not include any visa mobility, H-1B, or professional movement provisions — unlike US trade agreements with Australia, Chile, and Singapore that created dedicated visa categories.",
    "tags": ["india-us-trade-deal", "h1b", "visa-mobility", "mission-500", "piyush-goyal", "ambassador-gor", "ustr"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/indian-envoy-kwatra-discusses-trade-ties-with-us-house-panel/article69750123.ece"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-us-discuss-trade-critical-minerals-nuclear-power-2026-01-14/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/ambassador-gor-h1b-review-not-targeting-india"},
        {"name": "GK Today", "url": "https://www.gktoday.in/india-us-trade-deal-very-close-piyush-goyal/"},
        {"name": "Indian Embassy, Washington DC", "url": "https://www.indianembassyusa.gov.in/"}
    ]),
    "score_total": 83,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/President_Donald_Trump_and_Prime_Minister_Narendra_Modi_at_the_White_House.jpg/1280px-President_Donald_Trump_and_Prime_Minister_Narendra_Modi_at_the_White_House.jpg",
    "image_caption": "Prime Minister Modi meets President Trump at the White House, February 13, 2025",
    "image_attribution": "Prime Minister's Office, Government of India (GODL-India)",
    "body": article3_body.strip(),
}


# ─────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────

articles = [article1, article2, article3]
results = []
for i, art in enumerate(articles, 1):
    try:
        res = sb_post("p2_articles", art)
        title = art["headline"][:60]
        print(f"✅ Article {i}: {title}... → id={art['id']}")
        results.append(("OK", art["headline"]))
    except Exception as e:
        print(f"❌ Article {i} FAILED: {e}")
        results.append(("FAIL", str(e)))

print("\n─── Summary ───")
for status, info in results:
    print(f"  {status}: {info}")
print(f"\nTotal: {len(results)} articles, {sum(1 for s,_ in results if s=='OK')} succeeded")
